import pcbnew

PCB_PATH = "/home/welah/files-sync/projects/xmas ornaments/2026/hardware/v1-ornament-board/kicad/v1-ornament-board.kicad_pcb"
MM = pcbnew.FromMM

board = pcbnew.LoadBoard(PCB_PATH)

gnd_net = board.FindNet("GND")
assert gnd_net is not None, "GND net not found on board"

added = 0
seen_positions = set()
for fp in board.GetFootprints():
    for pad in fp.Pads():
        if pad.GetNetname() != "GND":
            continue
        pos = pad.GetPosition()
        key = (pos.x, pos.y)
        if key in seen_positions:
            continue  # avoid stacking duplicate vias if two GND pads coincide exactly
        seen_positions.add(key)

        via = pcbnew.PCB_VIA(board)
        via.SetPosition(pos)
        via.SetWidth(pcbnew.PADSTACK.ALL_LAYERS, MM(0.8))  # match project's Power net class via size
        via.SetDrill(MM(0.4))
        via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        via.SetNetCode(gnd_net.GetNetCode())
        board.Add(via)
        added += 1

ok = pcbnew.SaveBoard(PCB_PATH, board)
print(f"Added {added} GND vias (0.8mm/0.4mm drill)")
print("SaveBoard ok:", ok)
