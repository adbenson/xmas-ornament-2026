import pcbnew
import os

PCB_PATH = "/home/welah/files-sync/projects/xmas ornaments/2026/hardware/v1-ornament-board/kicad/v1-ornament-board.kicad_pcb"
FP_LIB_DIR = os.environ.get("KICAD_FOOTPRINT_DIR", "/usr/share/kicad/footprints")
MM = pcbnew.FromMM
TOMM = pcbnew.ToMM

CX, CY = 120.0, 150.0

board = pcbnew.LoadBoard(PCB_PATH)

src = board.FindFootprintByReference("MH2_UL")
assert src is not None, "MH2_UL not found"
pos = src.GetPosition()
x, y = TOMM(pos.x), TOMM(pos.y)
print(f"Source MH2_UL at ({x}, {y})")

mirrors = {
    "MH1_UR": (2 * CX - x, y),       # mirror across vertical axis
    "MH4_LL": (x, 2 * CY - y),       # mirror across horizontal axis
    "MH3_LR": (2 * CX - x, 2 * CY - y),  # mirror across both
}

lib = f"{FP_LIB_DIR}/MountingHole.pretty"
for name, (nx, ny) in mirrors.items():
    fp = pcbnew.FootprintLoad(lib, "MountingHole_3mm")
    assert fp is not None
    fp.SetReference(name)
    fp.SetPosition(pcbnew.VECTOR2I(MM(nx), MM(ny)))
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    board.Add(fp)
    print(f"{name}: ({nx:.3f}, {ny:.3f})")

ok = pcbnew.SaveBoard(PCB_PATH, board)
print("SaveBoard ok:", ok)
