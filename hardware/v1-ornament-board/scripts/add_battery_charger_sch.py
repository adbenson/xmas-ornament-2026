import re
import uuid as uuidlib

KICAD_DIR = "/home/welah/files-sync/projects/xmas ornaments/2026/hardware/v1-ornament-board/kicad"
MNT = "/tmp/.mount_kicadremp8173484700480565597"
SCH_PATH = f"{KICAD_DIR}/v1-ornament-board.kicad_sch"
PROJECT_NAME = "v1-ornament-board"
SHEET_UUID = "b6f2e8a1-3c4d-4e5f-9a1b-2c3d4e5f6a7b"


def u():
    return str(uuidlib.uuid4())


def extract_symbol_block(text, name):
    key = f'(symbol "{name}"'
    start = text.index(key)
    depth = 0
    i = start
    while True:
        c = text[i]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
        i += 1


def rename_symbol_header(block, new_name):
    m = re.match(r'\(symbol "([^"]+)"', block)
    return '(symbol "' + new_name + '"' + block[m.end():]


def load_lib_symbol(path, sym_name, nickname):
    text = open(path).read()
    block = extract_symbol_block(text, sym_name)
    return rename_symbol_header(block, f"{nickname}:{sym_name}")


def pin_abs(sym_x, sym_y, dx, dy):
    return sym_x + dx, sym_y - dy


symbol_instances = []
annotations = []


def prop(name, value, x, y, hide=False):
    hide_s = "\n\t\t\t(hide yes)" if hide else ""
    return (f'\t\t(property "{name}" "{value}"\n'
            f'\t\t\t(at {x:g} {y:g} 0){hide_s}\n'
            f'\t\t\t(show_name no)\n'
            f'\t\t\t(do_not_autoplace no)\n'
            f'\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n'
            f'\t\t)')


def place_symbol(lib_id, ref, value, footprint, x, y, pin_numbers):
    props = [
        prop("Reference", ref, x, y - 6),
        prop("Value", value, x, y + 6),
        prop("Footprint", footprint, x, y, hide=True),
        prop("Datasheet", "", x, y, hide=True),
        prop("Description", "", x, y, hide=True),
    ]
    pins = "\n".join(f'\t\t(pin "{n}"\n\t\t\t(uuid "{u()}")\n\t\t)' for n in pin_numbers)
    block = (
        f'\t(symbol\n'
        f'\t\t(lib_id "{lib_id}")\n'
        f'\t\t(at {x:g} {y:g} 0)\n'
        f'\t\t(unit 1)\n'
        f'\t\t(body_style 1)\n'
        f'\t\t(exclude_from_sim no)\n'
        f'\t\t(in_bom yes)\n'
        f'\t\t(on_board yes)\n'
        f'\t\t(in_pos_files yes)\n'
        f'\t\t(dnp no)\n'
        f'\t\t(uuid "{u()}")\n'
        + "\n".join(props) + "\n"
        + pins + "\n"
        f'\t\t(instances\n'
        f'\t\t\t(project "{PROJECT_NAME}"\n'
        f'\t\t\t\t(path "/{SHEET_UUID}"\n'
        f'\t\t\t\t\t(reference "{ref}")\n'
        f'\t\t\t\t\t(unit 1)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t)'
    )
    symbol_instances.append(block)


def label(net, x, y):
    annotations.append(
        f'\t(label "{net}"\n\t\t(at {x:g} {y:g} 0)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t)\n\t\t(uuid "{u()}")\n\t)'
    )


# --- Embedded lib_symbols for the new parts ---
lib_blocks = []
lib_blocks.append(load_lib_symbol(f"{MNT}/share/kicad/symbols/Battery_Management.kicad_symdir/MCP73832-2-OT.kicad_sym",
                                   "MCP73832-2-OT", "Battery_Management"))
lib_blocks.append(load_lib_symbol(f"{MNT}/share/kicad/symbols/Device.kicad_symdir/R.kicad_sym", "R", "Device"))
lib_blocks.append(load_lib_symbol(f"{MNT}/share/kicad/symbols/Device.kicad_symdir/LED.kicad_sym", "LED", "Device"))
lib_blocks.append(load_lib_symbol(f"{MNT}/share/kicad/symbols/Device.kicad_symdir/D_Schottky.kicad_sym", "D_Schottky", "Device"))
lib_blocks.append(load_lib_symbol(f"{MNT}/share/kicad/symbols/Connector.kicad_symdir/Conn_01x02_Pin.kicad_sym",
                                   "Conn_01x02_Pin", "Connector"))

# --- Pin local-offset maps (Y-flip already accounted for via pin_abs) ---
PIN_MCP73832 = {1: (10.16, -2.54), 2: (0, -7.62), 3: (10.16, 2.54), 4: (0, 7.62), 5: (-10.16, -2.54)}
PIN_R = {1: (0, 3.81), 2: (0, -3.81)}
PIN_LED = {1: (-3.81, 0), 2: (3.81, 0)}  # K, A
PIN_SCHOTTKY = {1: (-3.81, 0), 2: (3.81, 0)}  # K, A
PIN_CONN02 = {1: (5.08, 0), 2: (5.08, -2.54)}

# --- Placement: new "battery charger" cluster, clear of existing schematic content ---
UX, UY = 600.0, 152.4  # MCP73832 (multiples of 2.54 for grid alignment)

place_symbol("Battery_Management:MCP73832-2-OT", "U3", "MCP73832-2-OT",
             "Package_TO_SOT_SMD:SOT-23-5", UX, UY, [1, 2, 3, 4, 5])
MCP_NET = {1: "STAT", 2: "GND", 3: "VBATT", 4: "+5V", 5: "PROG"}
for pin, (dx, dy) in PIN_MCP73832.items():
    label(MCP_NET[pin], *pin_abs(UX, UY, dx, dy))

# R1: PROG-setting resistor, PROG -> GND. 10k = ~100mA charge current (conservative default,
# see design notes - depends on actual battery capacity, which isn't chosen yet).
R1X, R1Y = 561.98, 152.4
place_symbol("Device:R", "R1", "10k", "Resistor_SMD:R_0402_1005Metric", R1X, R1Y, [1, 2])
dx, dy = PIN_R[1]
label("PROG", *pin_abs(R1X, R1Y, dx, dy))
dx, dy = PIN_R[2]
label("GND", *pin_abs(R1X, R1Y, dx, dy))

# R2: STAT-LED series resistor, +5V -> R2 -> D122 anode.
R2X, R2Y = 561.98, 76.2
place_symbol("Device:R", "R2", "1k", "Resistor_SMD:R_0402_1005Metric", R2X, R2Y, [1, 2])
dx, dy = PIN_R[1]
label("+5V", *pin_abs(R2X, R2Y, dx, dy))
dx, dy = PIN_R[2]
label("STAT_LED_A", *pin_abs(R2X, R2Y, dx, dy))

# D122: charge-status indicator LED (lights while charging - STAT sinks current when active).
D122X, D122Y = 561.98, 40.64
place_symbol("Device:LED", "D122", "STAT_LED", "LED_SMD:LED_0603_1608Metric", D122X, D122Y, [1, 2])
dx, dy = PIN_LED[1]  # K
label("STAT", *pin_abs(D122X, D122Y, dx, dy))
dx, dy = PIN_LED[2]  # A
label("STAT_LED_A", *pin_abs(D122X, D122Y, dx, dy))

# D123: Schottky isolation diode, VBATT -> +5V (anode->VBATT, cathode->+5V). Lets the battery
# feed the system rail when USB is absent; reverse-biased (blocking) when USB drives +5V, per
# Seeed's own guidance against directly tying external battery power into the Xiao without this.
D123X, D123Y = 654.94, 152.4
place_symbol("Device:D_Schottky", "D123", "SS14", "Diode_SMD:D_SMA", D123X, D123Y, [1, 2])
dx, dy = PIN_SCHOTTKY[1]  # K
label("+5V", *pin_abs(D123X, D123Y, dx, dy))
dx, dy = PIN_SCHOTTKY[2]  # A
label("VBATT", *pin_abs(D123X, D123Y, dx, dy))

# J1: 2-pin JST-PH 2.0mm battery connector. Pin1=VBATT(+), Pin2=GND(-) - VERIFY against the
# actual battery pack before ordering, JST-PH battery-pack polarity isn't universally standardized
# across manufacturers (see design notes).
J1X, J1Y = 708.66, 152.4
place_symbol("Connector:Conn_01x02_Pin", "J1", "Battery_JST-PH-2.0", "Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal",
             J1X, J1Y, [1, 2])
dx, dy = PIN_CONN02[1]
label("VBATT", *pin_abs(J1X, J1Y, dx, dy))
dx, dy = PIN_CONN02[2]
label("GND", *pin_abs(J1X, J1Y, dx, dy))

# C123: VDD input bypass cap, +5V -> GND, near U3.
C123X, C123Y = 632.46, 88.9
place_symbol("Device:C", "C123", "1uF", "Capacitor_SMD:C_0402_1005Metric", C123X, C123Y, [1, 2])
PIN_CAP = {1: (0, 3.81), 2: (0, -3.81)}
dx, dy = PIN_CAP[1]
label("+5V", *pin_abs(C123X, C123Y, dx, dy))
dx, dy = PIN_CAP[2]
label("GND", *pin_abs(C123X, C123Y, dx, dy))

# C124: VBAT stability cap, VBATT -> GND, near U3.
C124X, C124Y = 632.46, 213.36
place_symbol("Device:C", "C124", "1uF", "Capacitor_SMD:C_0402_1005Metric", C124X, C124Y, [1, 2])
dx, dy = PIN_CAP[1]
label("VBATT", *pin_abs(C124X, C124Y, dx, dy))
dx, dy = PIN_CAP[2]
label("GND", *pin_abs(C124X, C124Y, dx, dy))

# --- Splice into the live schematic file ---
text = open(SCH_PATH).read()

# 1) Insert new lib_symbols blocks just before the closing of the existing (lib_symbols ...) section.
lib_key = "\t(lib_symbols\n"
lib_start = text.index(lib_key)
depth = 0
i = lib_start + 1  # start just after the opening paren of "(lib_symbols"
# find the '(' that opens lib_symbols itself (it's the char right before "lib_symbols" text... use the tab)
open_paren_idx = text.index("(lib_symbols", lib_start)
depth = 0
j = open_paren_idx
while True:
    c = text[j]
    if c == '(':
        depth += 1
    elif c == ')':
        depth -= 1
        if depth == 0:
            lib_close_idx = j  # index of the matching ')'
            break
    j += 1

insertion = "\n" + "\n".join(lib_blocks)
text = text[:lib_close_idx] + insertion + "\n\t" + text[lib_close_idx:]

# 2) Insert new symbol instances + annotations just before (sheet_instances ...).
sheet_key = "\t(sheet_instances\n"
sheet_idx = text.index(sheet_key)
new_content = "\n".join(symbol_instances) + "\n" + "\n".join(annotations) + "\n"
text = text[:sheet_idx] + new_content + text[sheet_idx:]

open(SCH_PATH, "w").write(text)
print(f"Added {len(symbol_instances)} symbols, {len(annotations)} labels to {SCH_PATH}")
