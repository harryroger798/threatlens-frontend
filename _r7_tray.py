import io

p = r"C:\Users\joxor\threatlens\pages-ui\src\app.js"
raw = io.open(p, "rb").read().decode("utf-8")

EDITS = [
    # 1) dismissal memory in state
    ("  Object.assign(state, { facetTypes: [], facetTags: [], facetSources: [], triageQuery: '', triageSeverity: 'open', auditAction: '', auditActor: '', incidentTab: 'timeline', liveHunts: [] });",
     "  Object.assign(state, { facetTypes: [], facetTags: [], facetSources: [], triageQuery: '', triageSeverity: 'open', auditAction: '', auditActor: '', incidentTab: 'timeline', liveHunts: [], trayDismissed: new Set() });"),
    # 2) badge counts what the tray would show: open alerts not dismissed
    ("""function updateBadge() {
  const count = state.mode === 'live' ? state.liveAlerts.filter(a => a.state === 'new').length : 3;
  const badge = qs('.notification-count');
  badge.textContent = count;
  badge.hidden = count === 0;
}""",
     """function updateBadge() {
  if (state.mode !== 'live') {
    const badge = qs('.notification-count');
    badge.textContent = 3;
    badge.hidden = false;
    return;
  }
  const count = state.liveAlerts.filter(a => ['new', 'acknowledged', 'in_progress'].includes(a.state) && !state.trayDismissed.has(a.id)).length;
  const badge = qs('.notification-count');
  badge.textContent = count;
  badge.hidden = count === 0;
}"""),
    # 3) tray renders open alerts not dismissed
    ("""function renderTrayLive() {
  const tray = qs('#notification-tray');
  const items = state.liveAlerts.slice(0, 5);
  if (!items.length) return;""",
     """function renderTrayLive() {
  const tray = qs('#notification-tray');
  const items = state.liveAlerts.filter(a => ['new', 'acknowledged', 'in_progress'].includes(a.state) && !state.trayDismissed.has(a.id)).slice(0, 5);
  if (!items.length) {
    clearTrayItems();
    const empty = document.createElement('div');
    empty.className = 'operator-empty';
    empty.style.minHeight = '6rem';
    empty.innerHTML = '<p>Tray clear — new alerts will land here live.</p>';
    tray.append(empty);
    return;
  }"""),
    # 4) Clear marks the visible items dismissed (real memory, not cosmetics)
    ("""function clearTray() {
  qsa('#notification-tray .notification-item').forEach(node => node.remove());
  showToast('Tray cleared.');
}""",
     """function clearTray() {
  qsa('#notification-tray .notification-item').forEach(node => {
    const id = node.dataset.alertId;
    if (id) state.trayDismissed.add(id);
  });
  clearTrayItems();
  updateBadge();
  showToast('Tray cleared — acknowledged alerts stay in the queue.');
}"""),
]

for old, new in EDITS:
    n = raw.count(old)
    print(("OK  " if n == 1 else f"MISS({n}) "), old[:70].replace("\n", "\\n"))
    if n == 1:
        raw = raw.replace(old, new)

# 5) tray items carry their alert id so dismissal can key on it
old = '    <div class="notification-item ${edge(a.severity)}" data-nav="triage" title="Open triage queue">'
new = '    <div class="notification-item ${edge(a.severity)}" data-alert-id="${escapeHtml(a.id)}" data-nav="triage" title="Open triage queue">'
n = raw.count(old)
print(("OK  tray item id" if n == 1 else f"MISS({n})  tray item id"))
if n == 1:
    raw = raw.replace(old, new)

io.open(p, "wb").write(raw.encode("utf-8"))
