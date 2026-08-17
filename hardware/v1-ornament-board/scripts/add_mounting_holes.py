import pcbnew
import math
import os

PCB_PATH = "/home/welah/files-sync/projects/xmas ornaments/2026/hardware/v1-ornament-board/kicad/v1-ornament-board.kicad_pcb"
FP_LIB_DIR = os.environ.get("KICAD_FOOTPRINT_DIR", "/usr/share/kicad/footprints")
MM = pcbnew.FromMM

CX, CY = 120.0, 150.0
R_HOLE = 34.5  # 3mm inset from the 37.5mm board radius
A_DEG = 71.6   # angle from vertical (top) - "squashed X" closer to horizontal per the user's
               # correction: wide top-gap/bottom-gap (2a=143deg), narrow side gap (180-2a=37deg),
               # symmetric about both board axes. Chosen for max clearance from components
               # (pads only - traces/vias ignored per the user's "just avoid components" call).

board = pcbnew.LoadBoard(PCB_PATH)

rad = math.radians(A_DEG)
dx, dy = R_HOLE * math.sin(rad), R_HOLE * math.cos(rad)
positions = {
    "MH1_UR": (CX + dx, CY - dy),
    "MH2_UL": (CX - dx, CY - dy),
    "MH3_LR": (CX + dx, CY + dy),
    "MH4_LL": (CX - dx, CY + dy),
}

lib = f"{FP_LIB_DIR}/MountingHole.pretty"
added = 0
for name, (x, y) in positions.items():
    fp = pcbnew.FootprintLoad(lib, "MountingHole_3mm")
    assert fp is not None, "Could not load MountingHole_3mm"
    fp.SetReference(name)
    fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    board.Add(fp)
    added += 1
    print(f"{name}: ({x:.3f}, {y:.3f})")

ok = pcbnew.SaveBoard(PCB_PATH, board)
print(f"Added {added} mounting holes (3mm NPTH)")
print("SaveBoard ok:", ok)
