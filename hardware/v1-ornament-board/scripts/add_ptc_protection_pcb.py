import pcbnew

MNT = "/tmp/.mount_kicadremp8173484700480565597"
PROJECT_DIR = "/home/welah/files-sync/projects/xmas ornaments/2026/hardware/v1-ornament-board/kicad"
PCB_PATH = f"{PROJECT_DIR}/v1-ornament-board.kicad_pcb"

MM = pcbnew.FromMM
board = pcbnew.LoadBoard(PCB_PATH)


def place(lib_path, name, nickname, ref, value, x, y):
    fp = pcbnew.FootprintLoad(lib_path, name)
    fp.SetFPID(pcbnew.LIB_ID(nickname, name))
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    board.Add(fp)


DIODE_LIB = f"{MNT}/share/kicad/footprints/Diode_SMD.pretty"
FUSE_LIB = f"{MNT}/share/kicad/footprints/Fuse.pretty"
RES_LIB = f"{MNT}/share/kicad/footprints/Resistor_SMD.pretty"
LED_LIB = f"{MNT}/share/kicad/footprints/LED_SMD.pretty"

# --- Revert D123 to SS14 / D_SMA (was swapped to SD103AW / D_SOD-123) ---
old = board.FindFootprintByReference("D123")
assert old is not None, "D123 not found"
pos = old.GetPosition()
layer = old.GetLayer()
board.Remove(old)
new = pcbnew.FootprintLoad(DIODE_LIB, "D_SMA")
new.SetFPID(pcbnew.LIB_ID("Diode_SMD", "D_SMA"))
new.SetReference("D123")
new.SetValue("SS14")
new.SetPosition(pos)
if layer != new.GetLayer():
    new.SetLayer(layer)
board.Add(new)
print("D123 reverted to SS14/D_SMA at", pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y))

# --- New parts: F1 (PTC), R3 + D124 (trip indicator). Holding area, clear of existing clusters. ---
place(FUSE_LIB, "Fuse_1206_3216Metric", "Fuse", "F1", "FSMD100-1206R", 300.0, 200.0)
place(RES_LIB, "R_0402_1005Metric", "Resistor_SMD", "R3", "1k", 315.0, 190.0)
place(LED_LIB, "LED_0603_1608Metric", "LED_SMD", "D124", "TRIP_LED", 315.0, 210.0)

ok = pcbnew.SaveBoard(PCB_PATH, board)
print("SaveBoard ok:", ok)
