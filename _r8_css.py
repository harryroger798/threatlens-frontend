import io

p = r"C:\Users\joxor\threatlens\pages-ui\src\styles.css"
raw = io.open(p, "rb").read().decode("utf-8")

# Check what's already there and append only what's missing
HAS_NODE_SEV = '.graph-node.high circle' in raw
HAS_ROOT_SUB = '.graph-pivot-sub' in raw
print('has node severity classes:', HAS_NODE_SEV)
print('has pivot sublabel class:', HAS_ROOT_SUB)

ADD = ""

if not HAS_NODE_SEV:
    ADD += """
/* severity fill/stroke for linked nodes — same tokens as chips */
.graph-node.high circle{fill:var(--high-wash);stroke:var(--high)}
.graph-node.medium circle{fill:var(--medium-wash);stroke:var(--medium)}
.graph-node.low circle{fill:var(--low-wash);stroke:var(--low)}
"""
if not HAS_ROOT_SUB:
    ADD += """
/* pivot sublabel sits with the root label block, not floating above */
.graph-pivot-sub{font:10px var(--font-ui);fill:var(--text-muted);paint-order:stroke;stroke:var(--surface-0);stroke-width:3px;stroke-linejoin:round;letter-spacing:.06em;text-transform:uppercase}
"""

if ADD:
    io.open(p, "ab").write(ADD.encode("utf-8"))
    print("OK  styles.css: appended graph node severity + pivot sublabel rules")
else:
    print("OK  styles.css: nothing to append")
