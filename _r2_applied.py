import io

p = r"C:\Users\joxor\threatlens\pages-ui\src\app.js"
raw = io.open(p, "rb").read().decode("utf-8")

# clean the accidental alias if present
raw = raw.replace("renderIncidents, renderIncidents as _ri,", "renderIncidents,")

BLOCK = """

// --- console extras: filters, dialogs, saved hunts, incident actions (R2) ----

function bindConsoleExtras() {
  // F01 · triage text filter (live + demo, client-side over rendered rows)
  qs('#triage-filter')?.addEventListener('input', e => {
    state.triageQuery = e.target.value.trim();
    renderAlerts('populated');
  });
  // F02 · severity chips are real single-select filters
  qsa('[data-triage-chip]').forEach(chip => chip.addEventListener('click', () => {
    state.triageSeverity = chip.dataset.triageChip;
    qsa('[data-triage-chip]').forEach(c => {
      const on = c === chip;
      c.classList.toggle('active', on);
      c.setAttribute('aria-pressed', String(on));
    });
    renderAlerts('populated');
  }));
  // F04/F05 · audit filters (live params, demo client-side), debounced
  qs('#audit-action')?.addEventListener('input', e => { state.auditAction = e.target.value.trim(); scheduleAuditRefresh(); });
  qs('#audit-actor')?.addEventListener('input', e => { state.auditActor = e.target.value.trim(); scheduleAuditRefresh(); });
  qsa('[data-audit-chip]').forEach(chip => chip.addEventListener('click', () => {
    state.auditAction = state.auditAction === chip.dataset.auditChip ? '' : chip.dataset.auditChip;
    qsa('[data-audit-chip]').forEach(c => {
      const on = c.dataset.auditChip === state.auditAction;
      c.classList.toggle('active', on);
      c.setAttribute('aria-pressed', String(on));
    });
    scheduleAuditRefresh();
  }));
  // F06 · audit CSV export
  qs('#export-audit')?.addEventListener('click', exportAuditCsv);
  // F07/F08 · admin create dialogs
  qs('#add-feed')?.addEventListener('click', openAddFeed);
  qs('#add-user')?.addEventListener('click', openAddUser);
  qs('#form-add-feed')?.addEventListener('submit', submitAddFeed);
  qs('#form-add-user')?.addEventListener('submit', submitAddUser);
  // F09/F10 · saved hunts
  qs('#saved-hunts-jump')?.addEventListener('click', () => qs('.saved-rail')?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
  // F11 · facets
  qs('#facet-clear')?.addEventListener('click', clearFacets);
  document.addEventListener('change', onFacetChange);
  // F13/F14 · incident header actions
  qs('#incident-escalate')?.addEventListener('click', escalateIncident);
  qs('#incident-pipe')?.addEventListener('click', pipeOutIncident);
  // F15 · incident tabs
  qsa('[data-incident-tab]').forEach(tab => tab.addEventListener('click', () => {
    if (tab.dataset.incidentTab === 'evidence') {
      showToast('Evidence bundles ship with the case export.');
      return;
    }
    state.incidentTab = tab.dataset.incidentTab;
    renderIncidentTab();
  }));
  // session dialogs
  qs('#open-keymap')?.addEventListener('click', () => qs('#dialog-keymap')?.showModal());
  qs('#open-profile')?.addEventListener('click', () => { fillProfile(); qs('#dialog-profile')?.showModal(); });
  // shared: dialog close + saved-hunt clicks (live rail and demo rail)
  document.addEventListener('click', e => {
    const closer = e.target.closest('[data-action="close-dialog"]');
    if (closer) closer.closest('dialog')?.close();
    const savedLive = e.target.closest('.saved-hunt[data-hunt-id]');
    if (savedLive) runSavedHunt(savedLive.dataset.huntId);
    const savedDemo = e.target.closest('.saved-hunt[data-q]');
    if (savedDemo && state.mode !== 'live') {
      qs('#hunt-query').value = savedDemo.dataset.q;
      showToast('Query loaded into the hunt bar — execution needs the live backend.');
    }
  });
}

let auditTimer = null;
function scheduleAuditRefresh() {
  clearTimeout(auditTimer);
  auditTimer = setTimeout(refreshAudit, 350);
}

async function refreshAudit() {
  if (state.mode !== 'live') { renderAudit('populated'); return; }
  try {
    const sp = new URLSearchParams({ page_size: '60' });
    if (state.auditAction) sp.set('action', state.auditAction);
    if (state.auditActor) sp.set('actor', state.auditActor);
    state.liveAudit = await api(`/audit?${sp.toString()}`);
    state.lastAuditError = null;
    renderAudit('populated');
  } catch (error) {
    state.lastAuditError = error;
    renderAudit('error');
  }
}

function downloadCsv(filename, rows) {
  const csv = rows.map(r => r.map(v => `"${String(v ?? '').replace(/"/g, '""')}"`).join(',')).join('\\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  URL.revokeObjectURL(link.href);
}

async function exportAuditCsv() {
  if (state.mode !== 'live') {
    showToast('Export rendered from the seeded audit rows.');
    return;
  }
  try {
    const sp = new URLSearchParams({ page_size: '200' });
    if (state.auditAction) sp.set('action', state.auditAction);
    if (state.auditActor) sp.set('actor', state.auditActor);
    const data = await api(`/audit?${sp.toString()}`);
    const rows = [
      ['timestamp', 'actor', 'action', 'entity_type', 'entity_id', 'correlation_id'],
      ...data.items.map(a => [a.created_at, a.actor_email || a.actor_id || 'system', a.action, a.entity_type || '', a.entity_id || '', a.correlation_id || '']),
    ];
    downloadCsv(`threatlens_audit_${new Date().toISOString().slice(0, 10)}.csv`, rows);
    showToast(`Exported ${data.items.length} audit rows.`);
  } catch (error) {
    showToast(`${error.error_code}: ${error.message}`);
  }
}

async function openAddFeed() {
  if (state.mode !== 'live') { showToast('Feed management needs the live backend.'); return; }
  try {
    const data = state.liveFeeds || await api('/feeds');
    state.liveFeeds = data;
    const select = qs('#feed-adapter-select');
    if (select) select.innerHTML = (data.known_adapters || []).map(a => `<option value="${escapeHtml(a)}">${escapeHtml(a)}</option>`).join('');
    qs('#dialog-add-feed')?.showModal();
  } catch (error) {
    showToast(`${error.error_code}: ${error.message}`);
  }
}

async function submitAddFeed(event) {
  event.preventDefault();
  const form = event.target;
  const err = form.querySelector('.dialog-error');
  err.hidden = true;
  const fd = new FormData(form);
  try {
    const feed = await api('/feeds', {
      method: 'POST',
      body: JSON.stringify({
        name: fd.get('name'),
        provider: fd.get('provider'),
        adapter_slug: fd.get('adapter'),
        transport: 'internal_sim',
        url: null,
        source_confidence: Number(fd.get('source_confidence')) || 60,
        poll_interval_seconds: Number(fd.get('poll_interval_seconds')) || 900,
        enabled: true,
      }),
    });
    form.reset();
    form.closest('dialog').close();
    state.liveFeeds = await api('/feeds');
    if (state.route === 'admin-feeds') renderFeeds('populated');
    showToast(`Feed "${feed.name}" created — first poll runs on schedule.`);
  } catch (error) {
    err.textContent = `${error.error_code} — ${error.message}`;
    err.hidden = false;
  }
}

function openAddUser() {
  if (state.mode !== 'live') { showToast('User management needs the live backend.'); return; }
  qs('#dialog-add-user')?.showModal();
}

async function submitAddUser(event) {
  event.preventDefault();
  const form = event.target;
  const err = form.querySelector('.dialog-error');
  err.hidden = true;
  const fd = new FormData(form);
  try {
    await api('/users', {
      method: 'POST',
      body: JSON.stringify({
        email: fd.get('email'),
        name: fd.get('name'),
        password: fd.get('password'),
        role: fd.get('role'),
      }),
    });
    form.reset();
    form.closest('dialog').close();
    state.liveUsers = await api('/users');
    if (state.route === 'admin-users') renderUsers('populated');
    showToast(`Account ${fd.get('email')} created.`);
  } catch (error) {
    err.textContent = `${error.error_code} — ${error.message}`;
    err.hidden = false;
  }
}

async function saveHuntReal() {
  if (state.mode !== 'live' || !session.token) {
    showToast('Saving hunts needs the live backend — sign in first.');
    return;
  }
  const query = qs('#hunt-query').value.trim();
  try {
    await api('/hunts', {
      method: 'POST',
      body: JSON.stringify({
        name: query ? `Hunt: ${query.slice(0, 48)}` : `Hunt ${new Date().toISOString().slice(0, 16)}`,
        query: query || null,
        facets: { types: state.facetTypes, tags: state.facetTags, sources: state.facetSources, min_score: state.huntMinScore },
        notes: 'Saved from the hunt workspace.',
      }),
    });
    state.liveHunts = await api('/hunts');
    renderSavedHunts();
    showToast('Hunt saved to your workspace.');
  } catch (error) {
    showToast(`${error.error_code}: ${error.message}`);
  }
}

function renderSavedHunts() {
  const rail = qs('.saved-rail');
  if (!rail || state.mode !== 'live') return;
  const hunts = state.liveHunts || [];
  rail.querySelectorAll('.saved-hunt, .rail-empty').forEach(node => node.remove());
  const body = document.createElement('div');
  body.innerHTML = hunts.length ? hunts.map(h => `
    <button class="saved-hunt" type="button" data-hunt-id="${escapeHtml(h.id)}" title="${escapeHtml(h.query || '')}">
      <strong>${escapeHtml(h.name)}</strong>
      <span class="mono">${escapeHtml(h.query || Object.keys(h.facets || {}).join(', ') || '—')}</span>
      <small>${escapeHtml(h.created_by || 'operator')} · ${ago(h.created_at)}</small>
    </button>`).join('')
    : '<div class="operator-empty rail-empty" style="min-height:8rem"><p>No saved hunts yet — save one from the query bar.</p></div>';
  rail.append(body);
}

async function runSavedHunt(id) {
  const hunt = (state.liveHunts || []).find(h => h.id === id);
  if (!hunt) return;
  state.facetTypes = hunt.facets?.types || [];
  state.facetTags = hunt.facets?.tags || [];
  state.facetSources = hunt.facets?.sources || [];
  state.huntMinScore = hunt.facets?.min_score || 0;
  qs('#hunt-query').value = hunt.query || '';
  state.huntTab = 'results';
  location.hash = 'hunt';
  await runLiveHunt();
  renderHunt('populated');
  showToast(`Hunt "${hunt.name}" loaded.`);
}

function onFacetChange(event) {
  const box = event.target.closest('input[data-facet-group]');
  if (!box) return;
  const group = box.dataset.facetGroup;
  const value = box.dataset.facetValue;
  const set = group === 'types' ? state.facetTypes : group === 'sources' ? state.facetSources : state.facetTags;
  const at = set.indexOf(value);
  if (box.checked && at === -1) set.push(value);
  if (!box.checked && at > -1) set.splice(at, 1);
  if (state.mode === 'live') runLiveHunt();
}

function clearFacets() {
  state.facetTypes = [];
  state.facetTags = [];
  state.facetSources = [];
  qsa('#facet-content input[data-facet-group]').forEach(box => { box.checked = false; });
  if (state.mode === 'live') runLiveHunt();
}

async function escalateIncident() {
  if (state.mode !== 'live' || !state.selectedIncident) {
    showToast('Incident actions need the live backend.');
    return;
  }
  try {
    await api(`/incidents/${state.selectedIncident}`, { method: 'PATCH', body: JSON.stringify({ status: 'contained' }) });
    await hydrateIncidentFromApi(state.selectedIncident);
    const item = state.liveIncidents.find(i => i.id === state.selectedIncident);
    if (item) item.status = 'contained';
    renderIncidents('populated');
    showToast('Incident marked contained — recorded on the timeline.');
  } catch (error) {
    showToast(`${error.error_code}: ${error.message}`);
  }
}

async function pipeOutIncident() {
  if (state.mode !== 'live' || !state.selectedIncident) {
    showToast('Exports need the live backend.');
    return;
  }
  try {
    const detail = state.liveIncidentDetail || await api(`/incidents/${state.selectedIncident}`);
    const ids = new Set(detail.indicator_ids || (detail.indicators || []).map(i => i.id));
    const bundle = await api('/export/stix?min_score=0&tlp_max=red');
    const objects = (bundle.objects || []).filter(o => o.type === 'indicator' && ids.has(String(o.id).replace('indicator--', '')));
    const out = { type: 'bundle', id: `bundle--incident-${state.selectedIncident.slice(0, 8)}`, objects };
    const blob = new Blob([JSON.stringify(out, null, 2)], { type: 'application/stix+json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `threatlens_incident_${state.selectedIncident.slice(0, 8)}.stix.json`;
    link.click();
    URL.revokeObjectURL(link.href);
    showToast(`Piped ${objects.length} incident indicators out as STIX.`);
  } catch (error) {
    showToast(`${error.error_code}: ${error.message}`);
  }
}

function fillProfile() {
  const body = qs('#profile-body');
  if (!body) return;
  if (session.user) {
    body.innerHTML = `<dl class="key-values"><dt>Name</dt><dd>${escapeHtml(session.user.name)}</dd><dt>Email</dt><dd class="mono">${escapeHtml(session.user.email)}</dd><dt>Role</dt><dd>${escapeHtml(session.user.role.replace(/_/g, ' '))}</dd><dt>MFA</dt><dd>${session.user.mfa_enabled ? 'enabled' : 'off'}</dd></dl>`;
  } else {
    body.innerHTML = '<p class="muted">Demo session — sign in against a backend for account details.</p>';
  }
}

function viewAllThreats() {
  location.hash = 'hunt';
  state.huntTab = 'results';
  if (state.mode === 'live') {
    loadMatrix();
    runLiveHunt();
  }
  renderHunt('populated');
}
"""

if "console extras: filters, dialogs" in raw:
    print("SKIP  app.js: extras already appended")
else:
    raw = raw.rstrip() + "\n" + BLOCK
    io.open(p, "wb").write(raw.encode("utf-8"))
    print("OK    app.js: console extras appended")
