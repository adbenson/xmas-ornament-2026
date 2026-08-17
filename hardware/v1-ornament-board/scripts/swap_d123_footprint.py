import pcbnew

MNT = "/tmp/.mount_kicadremp8173484700480565597"
PROJECT_DIR = "/home/welah/files-sync/projects/xmas ornaments/2026/hardware/v1-ornament-board/kicad"
PCB_PATH = f"{PROJECT_DIR}/v1-ornament-board.kicad_pcb"
DIODE_LIB = f"{MNT}/share/kicad/footprints/Diode_SMD.pretty"

board = pcbnew.LoadBoard(PCB_PATH)

old = board.FindFootprintByReference("D123")
assert old is not None, "D123 not found"
pos = old.GetPosition()
layer = old.GetLayer()
print("Old D123 at", pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y))

board.Remove(old)

new = pcbnew.FootprintLoad(DIODE_LIB, "D_SOD-123")
new.SetFPID(pcbnew.LIB_ID("Diode_SMD", "D_SOD-123"))
new.SetReference("D123")
new.SetValue("SD103AW")
new.SetPosition(pos)
if layer != new.GetLayer():
    new.SetLayer(layer)
board.Add(new)

ok = pcbnew.SaveBoard(PCB_PATH, board)
print("SaveBoard ok:", ok)
