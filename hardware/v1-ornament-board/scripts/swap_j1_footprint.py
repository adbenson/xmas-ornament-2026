import pcbnew

PCB_PATH = "/home/welah/files-sync/projects/xmas ornaments/2026/hardware/v1-ornament-board/kicad/v1-ornament-board.kicad_pcb"
NEW_FP = "Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal"

board = pcbnew.LoadBoard(PCB_PATH)

old_fp = board.FindFootprintByReference("J1")
assert old_fp is not None, "J1 not found on board"

pos = old_fp.GetPosition()
orient = old_fp.GetOrientationDegrees()
layer = old_fp.GetLayer()

# Net assignments by pad number, so the new footprint's pads land on the same nets.
net_by_padnum = {pad.GetPadName(): pad.GetNet() for pad in old_fp.Pads()}
print("Old pads/nets:", {k: v.GetNetname() for k, v in net_by_padnum.items()})

board.Remove(old_fp)

import os
FP_LIB_DIR = os.environ.get("KICAD_FOOTPRINT_DIR", "/usr/share/kicad/footprints")
lib, name = NEW_FP.split(":")
new_fp = pcbnew.FootprintLoad(f"{FP_LIB_DIR}/{lib}.pretty", name)
assert new_fp is not None, f"Could not load {NEW_FP}"

new_fp.SetReference("J1")
new_fp.SetValue("Battery_JST-PH-2.0")
new_fp.SetPosition(pos)
new_fp.SetOrientationDegrees(orient)
new_fp.SetLayer(layer)

assigned = 0
for pad in new_fp.Pads():
    padnum = pad.GetPadName()
    if padnum in net_by_padnum:
        pad.SetNet(net_by_padnum[padnum])
        assigned += 1
    else:
        # Mechanical "MP" anchor pads have no electrical net - leave unassigned.
        print(f"Pad {padnum}: no matching net (mechanical), leaving unassigned")

board.Add(new_fp)

ok = pcbnew.SaveBoard(PCB_PATH, board)
print(f"Assigned nets on {assigned} pads")
print("SaveBoard ok:", ok)
