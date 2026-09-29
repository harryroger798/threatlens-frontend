import io

BASE = r"C:\Users\joxor\threatlens\pages-ui"

# ---- 1) hunt.js: rewrite liveGraphMarkup + graphMarkup label placement ----
p = BASE + r"\src\hunt.js"
raw = io.open(p, "rb").read().decode("utf-8")

OLD_START = "function graphMarkup() {"
OLD_END = "function attackMarkup() {"
i_start = raw.index(OLD_START)
i_end = raw.index(OLD_END)
old_block = raw[i_start:i_end]

NEW_BLOCK = """function graphMarkup() {
  if (state.mode === 'live') {
    if (state.liveGraph) return graphSvg(state.liveGraph);
    if (state.graphBusy) return pivotLoading();
    const first = state.liveSearch?.results?.[0];
    if (!first) {
      return '<div class="graph-canvas"><div class="state-message"><strong>NO PIVOT LOADED</strong><span>Run a hunt with matches, then open a result row to grow its graph.</span></div></div>';
    }
    state.graphBusy = true;
    openIndicatorGraph(first.id).finally(() => { state.graphBusy = false; });
    return pivotLoading();
  }
  return graphSvg({
    root: { id: 'demo-root', value: '203.0.113.187', type: 'IP', severity_score: 98 },
    neighbors: [
      { id: 'd1', value: 'cdn-update-check.net', type: 'DOMAIN', severity_score: 91, relation: 'communicates-with' },
      { id: 'd2', value: '6f30cfa90c8a89f7e9abc2630e3955853ff18569', type: 'SHA-256', severity_score: 96, relation: 'drops' },
      { id: 'd3', value: 'auth-sync-service.org', type: 'DOMAIN', severity_score: 84, relation: 'resolves-to' },
      { id: 'd4', value: 'invoice-review-cloud.com', type: 'DOMAIN', severity_score: 68, relation: 'resolves-to' },
      { id: 'd5', value: '198.51.100.91', type: 'IPV4', severity_score: 72, relation: 'communicates-with' },
    ],
  });
}

function pivotLoading() {
  return '<div class="graph-canvas"><div class="state-message"><strong>PIVOTING</strong><span>Resolving typed relationships for the selected indicator…</span></div></div>';
}

function graphSvg(g) {
  const W = 1040, H = 680, cx = W / 2, cy = H / 2;
  const cols = 14;
  const wrap = v => {
    const s = String(v ?? '');
    const out = [];
    for (let i = 0; i < s.length && out.length < 4; i += cols) out.push(s.slice(i, i + cols));
    if (!out.length) out.push('—');
    return out;
  };
  const sevClass = s => s >= 85 ? 'critical' : s >= 70 ? 'high' : s >= 45 ? 'medium' : 'low';
  const shown = g.neighbors.slice(0, 10);
  const extra = g.neighbors.length - shown.length;
  const ringR = shown.length <= 4 ? 200 : shown.length <= 7 ? 250 : 295;
  const positions = shown.map((nb, i) => {
    const angle = (2 * Math.PI * i) / shown.length - Math.PI / 2;
    return { ...nb, x: Math.round(cx + ringR * Math.cos(angle)), y: Math.round(cy + ringR * Math.sin(angle)) };
  });
  const grid = '<g class="graph-grid">'
    + Array.from({ length: Math.ceil(W / 40) }, (_, i) => `<line x1="${i * 40}" y1="0" x2="${i * 40}" y2="${H}"/>`).join('')
    + Array.from({ length: Math.ceil(H / 40) }, (_, i) => `<line x1="0" y1="${i * 40}" x2="${W}" y2="${i * 40}"/>`).join('')
    + '</g>';
  // label block: multi-line value + sub, placed above or below the node anchor
  const labelBlock = (x, nodeY, r, value, sub, place) => {
    const lines = wrap(value);
    const block = lines.length * 13 + 14;
    let firstY;
    if (place === 'above') firstY = nodeY - r - 6 - block + 13;
    else firstY = nodeY + r + 13;
    const spans = lines.map((ln, i) => `<tspan x="${x}" dy="${i === 0 ? 0 : 13}">${escapeHtml(ln)}</tspan>`).join('');
    const subY = firstY + (lines.length - 1) * 13 + 12;
    return `<text class="graph-label" x="${x}" y="${Math.round(firstY)}" text-anchor="middle">${spans}</text>`
      + `<text class="graph-sublabel" x="${x}" y="${Math.round(subY)}" text-anchor="middle">${escapeHtml(sub)}</text>`;
  };
  const edges = positions.map(n => `<path class="graph-edge ${sevClass(n.severity_score)}" d="M${cx} ${cy} L${n.x} ${n.y}"/>`).join('');
  // root: value label + sublabel BELOW the circle (clear of edges and neighbors)
  const rootLabel = labelBlock(cx, cy, 36, g.root.value, `PIVOT · ${g.root.type} · SCORE ${g.root.severity_score} · ${g.neighbors.length} linked`, 'below');
  const rootMark = `<g class="graph-node root" title="${escapeHtml(g.root.value)}"><circle cx="${cx}" cy="${cy}" r="36"/></g>${rootLabel}`;
  // neighbors: label above if in the top half, below if in the bottom half
  const nodeMarks = positions.map(n => {
    const place = n.y < cy ? 'above' : 'below';
    return `<g class="graph-node ${n.severity_score >= 70 ? 'malicious' : ''}" title="${escapeHtml(n.value)}"><circle cx="${n.x}" cy="${n.y}" r="24"/></g>`
      + labelBlock(n.x, n.y, 24, n.value, `${n.type} · ${n.relation}`, place);
  }).join('');
  const legend = `<g class="graph-legend"><span>${shown.length} linked object${shown.length === 1 ? '' : 's'}${extra ? ` · ${extra} more not drawn` : ''}</span><span>edges colored by severity</span></g>`;
  return `<div class="graph-canvas"><svg class="graph-svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="Indicator relationship graph">${grid}<g>${edges}</g>${rootMark}<g>${nodeMarks}</g>${legend}</svg></div>`;
}

"""

new_raw = raw[:i_start] + NEW_BLOCK + "\n" + raw[i_end:]
io.open(p, "wb").write(new_raw.encode("utf-8"))
print("OK  hunt.js: graph renderer rewritten (labels below/above nodes, no overlap, no duplication)")
