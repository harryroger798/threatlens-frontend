# ThreatLens Console — Frontend

Vanilla JS operations console for the ThreatLens CTI platform.
Deployed on Cloudflare Pages with a Pages Function proxying the FastAPI backend.

**Live:** https://threatlens-5f1.pages.dev/threatlens

## Design system

Dark-first SOC palette (mineral teal actions, severity-only warm colors) with a
high-contrast light mode. IBM Plex Sans + Mono. 2/4/6/10/14/20/28/40 spacing ladder.
4px control radius, 8px panel radius. One shadow level for detached overlays only.

See `design/tokens.css` for the full token sheet and `design/DECISIONS.md` for the
argued design decisions.

## Structure

```
threatlens.html      single-page console
src/
  app.js            boot, routing, WebSocket, session glue
  core.js           config, transport, demo fixtures
  views.js          overview, triage, drawer, incidents
  hunt.js           hunt workspace: facets, graph, ATT&CK
  admin.js          feeds, users, audit, health
  heatmap.js        geographic threat density map (FR-20)
  widgets.js        dashboard widget library (FR-22)
  styles.css        all styles (tokens + components + craft revisions)
design/
  tokens.css        design token sheet
  DECISIONS.md      reference dossier + argued decisions
  AUDIT.md          craft audit + revision log (R1–R9)
functions/
  api/v1/[[route]].js   Pages Function: same-origin proxy to Render backend
```

## Key implementation details

- No framework: vanilla ES modules, flat component structure
- Two render paths: live (real API data) and demo (offline fallback), selected by
  backend health probe at boot
- WebSocket channels: alerts.stream, indicators.high_severity, incidents.{id},
  system.health — with auto-reconnect, backoff, and polling fallback
- Enrichment calls: AbuseIPDB, VirusTotal, ip-api.com, CISA KEV — with DB-backed
  60-minute cache and graceful fallback
- Widget system: show/hide Executive overview sections, persisted per user (FR-22)
- Geographic heatmap: dot-density SVG on equirectangular projection with country
  centroids (FR-20)
- Incident tabs: timeline (append-only), linked indicators, containment checklist
- All API errors surfaced with the uniform envelope: error_code, message, correlation_id

## Running locally

```bash
python -m http.server 4173
# open http://localhost:4173/threatlens.html (demo mode without backend)
```

## Deployment

```bash
npx wrangler pages deploy . --project-name threatlens --branch main --commit-dirty=true
```

The Pages Function at `functions/api/v1/[[route]].js` proxies `/api/v1/*` to the
FastAPI backend (set via `API_ORIGIN` in `wrangler.toml`), including WebSocket
upgrades. No CORS involved — same-origin proxy.
