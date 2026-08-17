import csv
import re

PROJECT_DIR = "/home/welah/files-sync/projects/xmas ornaments/2026/hardware/v1-ornament-board"
PCB_PATH = f"{PROJECT_DIR}/kicad/v1-ornament-board.kicad_pcb"
CSV_PATH = f"{PROJECT_DIR}/led_chain_order.csv"
PITCH = 5.5

positions = {}  # ref -> (x, y)
with open(CSV_PATH) as f:
    for row in csv.DictReader(f):
        x, y = float(row["x_mm"]), float(row["y_mm"])
        positions[row["led_ref"]] = (x, y)
        positions[row["cap_ref"]] = (x, y - PITCH / 2)  # cap above its LED

print(f"Loaded {len(positions)} target positions from CSV")

text = open(PCB_PATH).read()

# Split into footprint blocks by balanced-paren scan, keep non-footprint text as-is.
out = []
i = 0
n = len(text)
key = "\t(footprint "
replaced = 0
seen_refs = set()
while True:
    idx = text.find(key, i)
    if idx == -1:
        out.append(text[i:])
        break
    out.append(text[i:idx])
    # balanced scan from idx
    depth = 0
    j = idx
    while True:
        c = text[j]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                j += 1
                break
        j += 1
    block = text[idx:j]

    m = re.search(r'\(property "Reference" "([^"]+)"', block)
    ref = m.group(1) if m else None

    if ref in positions:
        x, y = positions[ref]
        new_block, count = re.subn(r'\n\t\t\(at [^\n]*\)', f'\n\t\t(at {x:.3f} {y:.3f})', block, count=1)
        assert count == 1, f"failed to patch (at ...) for {ref}"
        block = new_block
        replaced += 1
        seen_refs.add(ref)

    out.append(block)
    i = j

open(PCB_PATH, "w").write("".join(out))
print(f"Repositioned {replaced} footprints")

missing = set(positions) - seen_refs
if missing:
    print(f"WARNING: {len(missing)} refs from CSV not found on PCB: {sorted(missing)[:10]}...")
else:
    print("All CSV refs found and repositioned.")
