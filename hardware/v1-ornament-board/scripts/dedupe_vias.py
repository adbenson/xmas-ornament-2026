import pcbnew

PCB_PATH = "/home/welah/files-sync/projects/xmas ornaments/2026/hardware/v1-ornament-board/kicad/v1-ornament-board.kicad_pcb"
board = pcbnew.LoadBoard(PCB_PATH)

seen = set()
to_remove = []
for track in board.GetTracks():
    if track.Type() != pcbnew.PCB_VIA_T:
        continue
    pos = track.GetPosition()
    key = (pos.x, pos.y)
    if key in seen:
        to_remove.append(track)
    else:
        seen.add(key)

for v in to_remove:
    board.Remove(v)

print(f"Removed {len(to_remove)} duplicate vias, {len(seen)} unique vias remain")
ok = pcbnew.SaveBoard(PCB_PATH, board)
print("SaveBoard ok:", ok)
