// Cloudflare Pages Function — same-origin reverse proxy for the ThreatLens API.
// Routes /api/v1/* to the FastAPI backend named by the API_ORIGIN environment
// variable. Keeps the browser on one origin (no CORS) and transparently passes
// WebSocket upgrades through to the backend.

const json = (data, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
  });

async function proxy(request, env, routePath) {
  const origin = (env.API_ORIGIN || '').replace(/\/+$/, '');
  if (!origin) {
    return json(
      { error_code: 'backend_not_configured', message: 'Set the API_ORIGIN variable in Pages settings to your ThreatLens backend URL.', correlation_id: 'pages-proxy' },
      503,
    );
  }
  const incoming = new URL(request.url);
  const target = new URL(`${origin}/api/v1/${routePath}`);
  target.search = incoming.search;

  if (request.headers.get('upgrade') === 'websocket') {
    const upgrade = await fetch(target, { method: 'GET', headers: request.headers });
    return upgrade;
  }

  const headers = new Headers(request.headers);
  headers.delete('host');
  headers.delete('cf-connecting-ip');
  headers.delete('cf-ipcountry');
  headers.delete('cf-ray');
  headers.delete('x-forwarded-for');
  headers.delete('x-forwarded-proto');

  const init = { method: request.method, headers, redirect: 'follow' };
  if (!['GET', 'HEAD'].includes(request.method)) {
    init.body = await request.arrayBuffer();
  }
  return fetch(target, init);
}

export async function onRequest({ request, env, params }) {
  const raw = params.route || '';
  const routePath = (Array.isArray(raw) ? raw.join('/') : String(raw)).replace(/\/+$/, '');
  try {
    return await proxy(request, env, routePath);
  } catch (error) {
    return json(
      { error_code: 'backend_unreachable', message: `ThreatLens backend did not answer: ${error.message}`, correlation_id: 'pages-proxy' },
      502,
    );
  }
}
