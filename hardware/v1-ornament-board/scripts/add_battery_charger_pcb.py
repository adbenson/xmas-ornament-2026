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


CAP_LIB = f"{MNT}/share/kicad/footprints/Capacitor_SMD.pretty"
RES_LIB = f"{MNT}/share/kicad/footprints/Resistor_SMD.pretty"
LED_LIB = f"{MNT}/share/kicad/footprints/LED_SMD.pretty"
DIODE_LIB = f"{MNT}/share/kicad/footprints/Diode_SMD.pretty"
SOT23_5_LIB = f"{MNT}/share/kicad/footprints/Package_TO_SOT_SMD.pretty"
JST_LIB = f"{MNT}/share/kicad/footprints/Connector_JST.pretty"

# Holding area, clear of the board outline and the existing U1/U2/C122/SW1 cluster
# (which sits around x=177.5, y=110-190).
place(SOT23_5_LIB, "SOT-23-5", "Package_TO_SOT_SMD", "U3", "MCP73832-2-OT", 220.0, 130.0)
place(RES_LIB, "R_0402_1005Metric", "Resistor_SMD", "R1", "10k", 220.0, 150.0)
place(RES_LIB, "R_0402_1005Metric", "Resistor_SMD", "R2", "1k", 220.0, 160.0)
place(LED_LIB, "LED_0603_1608Metric", "LED_SMD", "D122", "STAT_LED", 220.0, 170.0)
place(DIODE_LIB, "D_SMA", "Diode_SMD", "D123", "SS14", 235.0, 130.0)
place(CAP_LIB, "C_0402_1005Metric", "Capacitor_SMD", "C123", "1uF", 235.0, 150.0)
place(CAP_LIB, "C_0402_1005Metric", "Capacitor_SMD", "C124", "1uF", 235.0, 160.0)
place(JST_LIB, "JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal", "Connector_JST", "J1", "Battery_JST-PH-2.0", 250.0, 130.0)

ok = pcbnew.SaveBoard(PCB_PATH, board)
print("SaveBoard ok:", ok)
