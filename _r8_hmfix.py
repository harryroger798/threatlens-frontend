import io

p = r"C:\Users\joxor\threatlens\pages-ui\src\heatmap.js"
raw = io.open(p, "rb").read().decode("utf-8")

old_imp = "import { get } from './api.js';"
new_imp = "import { api } from './core.js';"
n = raw.count(old_imp)
print("import anchor:", n)
if n == 1:
    raw = raw.replace(old_imp, new_imp)

old_call = "const data = await get('/dashboard/threat');"
new_call = "const data = await api('/dashboard/threat');"
n = raw.count(old_call)
print("call anchor:", n)
if n == 1:
    raw = raw.replace(old_call, new_call)

io.open(p, "wb").write(raw.encode("utf-8"))
