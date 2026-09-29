import io

p = r"C:\Users\joxor\threatlens\pages-ui\src\app.js"
raw = io.open(p, "rb").read().decode("utf-8")

old = """  if (routeName === 'hunt' && state.mode === 'live' && session.token) {
    loadMatrix().then(() => runLiveHunt());
  }"""
new = """  if (routeName === 'hunt' && state.mode === 'live' && session.token) {
    loadMatrix().then(() => runLiveHunt());
  }
  if (state.mode === 'live' && session.token) {
    if (routeName === 'admin-feeds') api('/feeds').then(d => { state.liveFeeds = d; renderFeeds('populated'); }).catch(() => {});
    if (routeName === 'admin-users') api('/users').then(d => { state.liveUsers = d; renderUsers('populated'); }).catch(() => {});
    if (routeName === 'admin-audit') api('/audit?page_size=60').then(d => { state.liveAudit = d; state.auditTotal = d.total || (d.items || []).length; state.auditPage = 1; renderAudit('populated'); }).catch(() => {});
  }"""
n = raw.count(old)
print("found:", n)
if n == 1:
    raw = raw.replace(old, new)
    io.open(p, "wb").write(raw.encode("utf-8"))
