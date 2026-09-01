import pcbnew

PCB_PATH = "/home/welah/files-sync/projects/xmas ornaments/2026/hardware/v1-ornament-board/kicad/v1-ornament-board.kicad_pcb"
NEW_FP = "Package_DFN_QFN:DFN-8-1EP_3x2mm_P0.5mm_EP1.7x1.4mm"

board = pcbnew.LoadBoard(PCB_PATH)

old_fp = board.FindFootprintByReference("U3")
assert old_fp is not None, "U3 not found on board"

pos = old_fp.GetPosition()
orient = old_fp.GetOrientationDegrees()
layer = old_fp.GetLayer()

# Old SOT-23-5 pad -> function (per MCP73832 SOT-23-5 datasheet pinout)
old_pad_function = {"1": "STAT", "2": "VSS", "3": "VBAT", "4": "VDD", "5": "PROG"}
net_by_function = {}
for pad in old_fp.Pads():
    fn = old_pad_function[pad.GetPadName()]
    net_by_function[fn] = pad.GetNet()
    print(f"Old pad {pad.GetPadName()} ({fn}) -> {pad.GetNet().GetNetname()}")

board.Remove(old_fp)

lib, name = NEW_FP.split(":")
new_fp = pcbnew.FootprintLoad(f"/tmp/.mount_kicadremp8173484700480565597/share/kicad/footprints/{lib}.pretty", name)
assert new_fp is not None, f"Could not load {NEW_FP}"

new_fp.SetReference("U3")
new_fp.SetValue("MCP73832-2-MC")
new_fp.SetPosition(pos)
new_fp.SetOrientationDegrees(orient)
new_fp.SetLayer(layer)

# New DFN-8-1EP pad -> function (per MCP73832 DFN-8 datasheet pinout; pad 9 = EP)
new_pad_function = {
    "1": "VDD", "2": "VDD", "3": "VBAT", "4": "VBAT",
    "5": "STAT", "6": "VSS", "7": "NC", "8": "PROG",
    "9": "VSS",  # exposed thermal pad, datasheet: must be tied to VSS
}

assigned = 0
for pad in new_fp.Pads():
    padnum = pad.GetPadName()
    if padnum == "":
        continue  # paste-only mechanical sub-pads under the EP, no net
    fn = new_pad_function[padnum]
    if fn == "NC":
        print(f"Pad {padnum} (NC): leaving unassigned")
        continue
    pad.SetNet(net_by_function[fn])
    assigned += 1
    tag = " (EP, PCB-only override)" if padnum == "9" else ""
    print(f"New pad {padnum} ({fn}){tag} -> {net_by_function[fn].GetNetname()}")

board.Add(new_fp)

ok = pcbnew.SaveBoard(PCB_PATH, board)
print(f"Assigned nets on {assigned} pads")
print("SaveBoard ok:", ok)
