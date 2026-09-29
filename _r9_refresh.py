import io

p = r"C:\Users\joxor\threatlens\pages-ui\src\app.js"
raw = io.open(p, "rb").read().decode("utf-8")

# 1) refresh timer: schedule at 25 minutes after every successful login/refresh
old_connect = "    connectSocket();\n    await refreshLive();\n    showToast(`Signed in as ${session.user.name}.`);"
new_connect = """    connectSocket();
    await refreshLive();
    showToast(`Signed in as ${session.user.name}.`);
    scheduleTokenRefresh();"""
n = raw.count(old_connect)
print('login refresh anchor:', n)
if n == 1:
    raw = raw.replace(old_connect, new_connect)

# 2) also schedule after init (in case of stored token)
old_init = "    startPolling();\n  }"
new_init = "    startPolling();\n    scheduleTokenRefresh();\n  }"
n = raw.count(old_init)
print('init refresh anchor:', n)
if n == 1:
    raw = raw.replace(old_init, new_init)

# 3) the refresh function itself
BLOCK = """

// --- token refresh: silently renew before the 30-minute expiry ---------------

let tokenRefreshTimer = null;

function scheduleTokenRefresh() {
  clearTimeout(tokenRefreshTimer);
  // refresh at 25 minutes (access token expires at 30)
  tokenRefreshTimer = setTimeout(async () => {
    try {
      const resp = await fetch(`${API_ROOT}/auth/refresh`, { method: 'POST', credentials: 'include' });
      if (resp.ok) {
        const data = await resp.json();
        session.token = data.access_token;
        localStorage.setItem('tl.token', data.access_token);
        // reschedule for the next cycle
        scheduleTokenRefresh();
      } else if (resp.status === 401) {
        // refresh token expired — force re-login
        doLogout();
      }
    } catch {
      // network error — retry in 2 minutes
      tokenRefreshTimer = setTimeout(scheduleTokenRefresh, 120000);
    }
  }, 25 * 60 * 1000);
}
"""

if "scheduleTokenRefresh" in raw and "function scheduleTokenRefresh" not in raw:
    raw = raw.rstrip() + "\n" + BLOCK
    io.open(p, "wb").write(raw.encode("utf-8"))
    print("OK  app.js: token refresh block appended")
elif "function scheduleTokenRefresh" in raw:
    print("SKIP  app.js: already present")
