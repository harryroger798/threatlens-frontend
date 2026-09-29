import io

p = r"C:\Users\joxor\threatlens\pages-ui\src\widgets.js"
raw = io.open(p, "rb").read().decode("utf-8")

old = """function saveLayout(layout) {
  const user = JSON.parse(localStorage.getItem('tl.user') || '{}');
  localStorage.setItem(STORAGE_KEY + '.' + (user.id || 'default'), JSON.stringify(layout));
}

function getLayout() {
  const user = JSON.parse(localStorage.getItem('tl.user') || '{}');
  return loadLayout()[user.id] || loadLayout();
}"""
new = """function saveLayout(layout) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(layout));
}

function getLayout() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); } catch { return {}; }
}"""
n = raw.count(old)
print('save/get anchor:', n)
if n == 1:
    raw = raw.replace(old, new)
    io.open(p, "wb").write(raw.encode("utf-8"))
