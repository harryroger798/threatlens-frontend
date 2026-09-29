import io

p = r"C:\Users\joxor\threatlens\pages-ui\src\widgets.js"
raw = io.open(p, "rb").read().decode("utf-8")

# dialog needs showModal/close, not classList
old_open = "if (open) { panel.classList.add('open'); return; }"
new_open = "if (open) { panel.showModal(); return; }"
n = raw.count(old_open)
print('open fix:', n)
if n == 1:
    raw = raw.replace(old_open, new_open)

old_render = "panel.classList.add('open');"
new_render = "panel.showModal();"
n = raw.count(old_render)
print('render fix:', n)
if n == 1:
    raw = raw.replace(old_render, new_render)

old_close = "panel.querySelector('[data-action=\"close-widget-panel\"]').addEventListener('click', () => panel.classList.remove('open'));"
new_close = "panel.querySelector('[data-action=\"close-widget-panel\"]').addEventListener('click', () => panel.close());"
n = raw.count(old_close)
print('close fix:', n)
if n == 1:
    raw = raw.replace(old_close, new_close)

old_save = "panel.classList.remove('open');"
new_save = "panel.close();"
n = raw.count(old_save)
print('save close fix:', n)
if n == 1:
    raw = raw.replace(old_save, new_save)

io.open(p, "wb").write(raw.encode("utf-8"))
