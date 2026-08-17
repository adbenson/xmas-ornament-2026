import math
import pcbnew

MNT = "/tmp/.mount_kicadremp8173484700480565597"
PROJECT_DIR = "/home/welah/files-sync/projects/xmas ornaments/2026/hardware/v1-ornament-board/kicad"
LED_LIB = f"{PROJECT_DIR}/libs/footprints.pretty"
LED_NAME = "LED-SMD_4P-L2.2-W2.0-P1.00_WS2815C-2020-4P"
CAP_LIB = f"{MNT}/share/kicad/footprints/Capacitor_SMD.pretty"
CAP_NAME = "C_0402_1005Metric"
XIAO_NAME = "XIAO-SAMD21-SMD"
JOY_NAME = "SKRHABE010_ALPS"
SOT23_5_LIB = f"{MNT}/share/kicad/footprints/Package_TO_SOT_SMD.pretty"
SOT23_5_NAME = "SOT-23-5"
OUT_PCB = f"{PROJECT_DIR}/v1-ornament-board.kicad_pcb"

MM = pcbnew.FromMM

# --- Board geometry ---
CENTER_X, CENTER_Y = 120.0, 150.0   # arbitrary sheet placement, all-positive coords
R = 37.5                            # 75mm diameter circle
TAB_W = 16.0
TAB_H = 16.0
PITCH = 5.5                         # uniform square-lattice LED pitch (mm)

# LED counts per row, index 0 = bottom row (nearest MCU/joystick), index 12 = top row (nearest tab)
ROW_COUNTS = [3, 7, 9, 11, 11, 13, 13, 13, 11, 11, 9, 7, 3]
N_ROWS = len(ROW_COUNTS)
MID = (N_ROWS - 1) // 2  # =6, center row/col index

board = pcbnew.CreateEmptyBoard()

led_master = pcbnew.FootprintLoad(LED_LIB, LED_NAME)
led_master.SetFPID(pcbnew.LIB_ID("footprints", LED_NAME))
led_master.SetValue("WS2812B-2020-V6")

cap_master = pcbnew.FootprintLoad(CAP_LIB, CAP_NAME)
cap_master.SetFPID(pcbnew.LIB_ID("Capacitor_SMD", CAP_NAME))
cap_master.SetValue("100nF")

led_positions = []  # (ref, x, y, row, col) in chain order for notes/handoff

led_num = 0
for r, count in enumerate(ROW_COUNTS):
    half = (count - 1) // 2
    cols = list(range(MID - half, MID + half + 1))
    if r % 2 == 1:  # odd rows run R->L
        cols = list(reversed(cols))
    y = CENTER_Y - (r - MID) * PITCH
    for c in cols:
        led_num += 1
        x = CENTER_X + (c - MID) * PITCH

        led = pcbnew.Cast_to_FOOTPRINT(led_master.Duplicate(False))
        led_ref = f"D{led_num}"
        led.SetReference(led_ref)
        led.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        board.Add(led)

        cap = pcbnew.Cast_to_FOOTPRINT(cap_master.Duplicate(False))
        cap_ref = f"C{led_num}"
        cap.SetReference(cap_ref)
        # Placed above the LED (-Y, half pitch, toward the tab/top of the board) per Drew's call.
        # Still a placeholder side - orientation/final side TBD per Drew.
        cap.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y - PITCH / 2)))
        board.Add(cap)

        led_positions.append((led_num, led_ref, cap_ref, x, y, r, c))

# --- Board outline: circle + tangent-joined square tab (same technique as V0) ---
half_tab = TAB_W / 2
dy = math.sqrt(R ** 2 - half_tab ** 2)     # height above center where chord width == tab width
tab_bottom_y = CENTER_Y - dy
tab_top_y = tab_bottom_y - TAB_H
left_x = CENTER_X - half_tab
right_x = CENTER_X + half_tab


def add_line(p1, p2):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pcbnew.VECTOR2I(MM(p1[0]), MM(p1[1])))
    s.SetEnd(pcbnew.VECTOR2I(MM(p2[0]), MM(p2[1])))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(MM(0.1))
    board.Add(s)


add_line((left_x, tab_bottom_y), (left_x, tab_top_y))
add_line((left_x, tab_top_y), (right_x, tab_top_y))
add_line((right_x, tab_top_y), (right_x, tab_bottom_y))

arc = pcbnew.PCB_SHAPE(board)
arc.SetShape(pcbnew.SHAPE_T_ARC)
arc.SetLayer(pcbnew.Edge_Cuts)
arc.SetWidth(MM(0.1))
arc.SetArcGeometry(
    pcbnew.VECTOR2I(MM(right_x), MM(tab_bottom_y)),
    pcbnew.VECTOR2I(MM(CENTER_X), MM(CENTER_Y + R)),
    pcbnew.VECTOR2I(MM(left_x), MM(tab_bottom_y)),
)
board.Add(arc)

# --- MCU / level shifter / joystick: holding area, OFF the board outline. ---
# The 121-LED grid already tiles the full circle interior - there's no free space left inside
# the outline for these. Real placement means either carving space out of the LED grid (like V0
# did for the joystick) or extending the outline, both real design calls for Drew, not something
# to guess at from a script (same lesson V0 hit with its own U1/U2/SW1). Placed here purely so the
# PCB stays in sync with the schematic (nothing missing/unplaced) pending that decision.
HOLD_X = CENTER_X + R + 20.0  # clear of the circle, to the right


def place_simple(lib_path, name, nickname, ref, value, x, y):
    fp = pcbnew.FootprintLoad(lib_path, name)
    fp.SetFPID(pcbnew.LIB_ID(nickname, name))
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    board.Add(fp)


place_simple(f"{PROJECT_DIR}/libs/footprints.pretty", XIAO_NAME, "footprints", "U1", "XIAO-SAMD21-SMD",
             HOLD_X, CENTER_Y - 40)
place_simple(SOT23_5_LIB, SOT23_5_NAME, "Package_TO_SOT_SMD", "U2", "74AHCT1G125",
             HOLD_X, CENTER_Y)
place_simple(CAP_LIB, CAP_NAME, "Capacitor_SMD", "C122", "100nF",
             HOLD_X + 15, CENTER_Y)
place_simple(f"{PROJECT_DIR}/libs/footprints.pretty", JOY_NAME, "footprints", "SW1", "SKRHABE010_ALPS",
             HOLD_X, CENTER_Y + 40)

ok = pcbnew.SaveBoard(OUT_PCB, board)
print("SaveBoard ok:", ok)
print(f"Placed {led_num} LEDs + {led_num} caps")
print(f"Board bbox: x[{left_x:.3f},{right_x:.3f} tab / {CENTER_X-R:.3f},{CENTER_X+R:.3f} circle] "
      f"y[{tab_top_y:.3f} top .. {CENTER_Y+R:.3f} bottom]")

# Dump chain order for design notes / follow-up schematic wiring
with open(f"{PROJECT_DIR.rsplit('/',1)[0]}/led_chain_order.csv", "w") as f:
    f.write("chain_index,led_ref,cap_ref,x_mm,y_mm,row,col\n")
    for n, led_ref, cap_ref, x, y, r, c in led_positions:
        f.write(f"{n},{led_ref},{cap_ref},{x:.3f},{y:.3f},{r},{c}\n")
print("Wrote led_chain_order.csv")
