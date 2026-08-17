import re
import uuid as uuidlib

PROJECT_DIR = "/home/welah/files-sync/projects/xmas ornaments/2026/hardware/v1-ornament-board"
KICAD_DIR = f"{PROJECT_DIR}/kicad"
LIBS = f"{KICAD_DIR}/libs"
MNT = "/tmp/.mount_kicadremp8173484700480565597"
PROJECT_NAME = "v1-ornament-board"
SHEET_UUID = "b6f2e8a1-3c4d-4e5f-9a1b-2c3d4e5f6a7b"
OUT_SCH = f"{KICAD_DIR}/v1-ornament-board.kicad_sch"


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


# --- Embedded lib_symbols ---
lib_blocks = []
lib_blocks.append(load_lib_symbol(f"{LIBS}/ws2812b_2020.kicad_sym", "WS2812B-2020-V6", "ws2812b_2020"))
lib_blocks.append(load_lib_symbol(f"{LIBS}/xiao_samd21.kicad_sym", "XIAO-SAMD21-SMD", "xiao_samd21"))
lib_blocks.append(load_lib_symbol(f"{LIBS}/skrhabe010_joystick.kicad_sym", "SKRHABE010", "joystick_alps"))
lib_blocks.append(load_lib_symbol(f"{MNT}/share/kicad/symbols/Device.kicad_symdir/C.kicad_sym", "C", "Device"))
lib_blocks.append(load_lib_symbol(f"{MNT}/share/kicad/symbols/74xGxx.kicad_symdir/74LVC1G125.kicad_sym", "74LVC1G125", "74xGxx"))
lib_blocks.append(load_lib_symbol(f"{MNT}/share/kicad/symbols/power.kicad_symdir/+5V.kicad_sym", "+5V", "power"))
lib_blocks.append(load_lib_symbol(f"{MNT}/share/kicad/symbols/power.kicad_symdir/GND.kicad_sym", "GND", "power"))
lib_blocks.append(load_lib_symbol(f"{MNT}/share/kicad/symbols/power.kicad_symdir/PWR_FLAG.kicad_sym", "PWR_FLAG", "power"))

lib_symbols_section = "\t(lib_symbols\n" + "\n".join(lib_blocks) + "\n\t)\n"

# --- Pin local-offset maps (dx,dy from symbol origin; instance rotation always 0) ---
PIN_LED = {1: (8.89, -1.27), 2: (8.89, 1.27), 3: (-8.89, 1.27), 4: (-8.89, -1.27)}
PIN_CAP = {1: (0, 3.81), 2: (0, -3.81)}
PIN_XIAO = {
    1: (-21.59, 1.27), 2: (-21.59, -2.54), 3: (-21.59, -6.35), 4: (-21.59, -10.16),
    5: (-21.59, -13.97), 6: (-21.59, -17.78), 7: (-21.59, -21.59), 8: (21.59, -21.59),
    9: (21.59, -17.78), 10: (21.59, -13.97), 11: (21.59, -10.16), 12: (21.59, -6.35),
    13: (21.59, -2.54), 14: (21.59, 1.27), 15: (-5.08, 13.97), 16: (-1.27, 13.97),
    17: (2.54, 13.97), 18: (6.35, 13.97), 19: (-2.54, -30.48), 20: (1.27, -30.48),
}
XIAO_NAMES = {1: "D0", 2: "D1", 3: "D2", 4: "D3", 5: "D4", 6: "D5", 7: "D6", 8: "D7",
              9: "D8", 10: "D9", 11: "D10", 12: "3V3_OUT", 13: "GND", 14: "VBUS",
              15: "SWDIO", 16: "SWCLK", 17: "EN", 18: "GND", 19: "VIN", 20: "GND"}
PIN_JOY = {1: (0, 0), 2: (0, -2.54), 3: (0, -5.08), 4: (40.64, -5.08), 5: (40.64, -2.54), 6: (40.64, 0)}
PIN_LVL = {1: (0, 10.16), 2: (-15.24, 0), 3: (-5.08, -10.16), 4: (12.7, 0), 5: (-5.08, 10.16)}
PIN_PWR = {1: (0, 0)}

symbol_instances = []  # text blocks
annotations = []       # (label|no_connect) text blocks


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


def no_connect(x, y):
    annotations.append(f'\t(no_connect\n\t\t(at {x:g} {y:g})\n\t\t(uuid "{u()}")\n\t)')


def pin_abs(sym_x, sym_y, dx, dy):
    # Symbol library Y-axis is inverted relative to the schematic sheet's Y-axis
    # (verified empirically via kicad-cli sch erc: unrotated instances need Y subtracted, not added).
    return sym_x + dx, sym_y - dy


# --- LED grid (schematic layout only - not meant to mirror physical PCB placement) ---
# Coordinates kept as multiples of 2.54mm so pin positions (offsets are multiples of 1.27mm) land on-grid.
LED_X0, LED_Y0 = 20.32, 20.32
LED_DX, LED_DY = 30.48, 22.86
CAP_DY = 10.16
N_LED = 121

for n in range(1, N_LED + 1):
    col = (n - 1) % 11
    row = (n - 1) // 11
    x = LED_X0 + col * LED_DX
    y = LED_Y0 + row * LED_DY

    place_symbol("ws2812b_2020:WS2812B-2020-V6", f"D{n}", "WS2812B-2020-V6",
                 "footprints:LED-SMD_4P-L2.2-W2.0-P1.00_WS2815C-2020-4P", x, y, [1, 2, 3, 4])

    dx, dy = PIN_LED[1]  # DO
    if n < N_LED:
        label(f"LED_CH{n}", *pin_abs(x, y, dx, dy))
    else:
        no_connect(*pin_abs(x, y, dx, dy))

    dx, dy = PIN_LED[2]  # GND
    label("GND", *pin_abs(x, y, dx, dy))

    dx, dy = PIN_LED[3]  # DI
    net = "LED_DATA_OUT" if n == 1 else f"LED_CH{n - 1}"
    label(net, *pin_abs(x, y, dx, dy))

    dx, dy = PIN_LED[4]  # VDD
    label("+5V", *pin_abs(x, y, dx, dy))

    # Decoupling cap, placed below its LED in schematic space (schematic layout only)
    cx, cy = x, y + CAP_DY
    place_symbol("Device:C", f"C{n}", "100nF", "Capacitor_SMD:C_0402_1005Metric", cx, cy, [1, 2])
    dx, dy = PIN_CAP[1]
    label("+5V", *pin_abs(cx, cy, dx, dy))
    dx, dy = PIN_CAP[2]
    label("GND", *pin_abs(cx, cy, dx, dy))

# --- MCU (Xiao SAMD21) ---
UX, UY = 457.2, 101.6
place_symbol("xiao_samd21:XIAO-SAMD21-SMD", "U1", "XIAO-SAMD21-SMD", "footprints:XIAO-SAMD21-SMD",
             UX, UY, list(range(1, 21)))
XIAO_NET = {1: "JOY_LEFT", 2: "JOY_RIGHT", 3: "JOY_DOWN", 4: "JOY_SELECT", 5: None, 6: None,
            7: "JOY_UP", 8: None, 9: None, 10: "LED_DATA_IN", 11: None, 12: None,
            13: "GND", 14: "+5V", 15: None, 16: None, 17: None, 18: "GND", 19: None, 20: "GND"}
for pin, (dx, dy) in PIN_XIAO.items():
    net = XIAO_NET[pin]
    if net is None:
        no_connect(*pin_abs(UX, UY, dx, dy))
    else:
        label(net, *pin_abs(UX, UY, dx, dy))

# --- Level shifter (74AHCT1G125, using base 74LVC1G125 symbol w/ Value override - matches V0) ---
LX, LY = 457.2, 223.52
place_symbol("74xGxx:74LVC1G125", "U2", "74AHCT1G125", "Package_TO_SOT_SMD:SOT-23-5", LX, LY, [1, 2, 3, 4, 5])
LVL_NET = {1: "GND", 2: "LED_DATA_IN", 3: "GND", 4: "LED_DATA_OUT", 5: "+5V"}
for pin, (dx, dy) in PIN_LVL.items():
    label(LVL_NET[pin], *pin_abs(LX, LY, dx, dy))

# --- Level shifter decoupling cap ---
CX, CY = 495.3, 223.52
place_symbol("Device:C", "C122", "100nF", "Capacitor_SMD:C_0402_1005Metric", CX, CY, [1, 2])
dx, dy = PIN_CAP[1]
label("+5V", *pin_abs(CX, CY, dx, dy))
dx, dy = PIN_CAP[2]
label("GND", *pin_abs(CX, CY, dx, dy))

# --- Joystick ---
JX, JY = 457.2, 325.12
place_symbol("joystick_alps:SKRHABE010", "SW1", "SKRHABE010", "footprints:SKRHABE010_ALPS",
             JX, JY, [1, 2, 3, 4, 5, 6])
JOY_NET = {1: "JOY_UP", 2: "JOY_SELECT", 3: "JOY_DOWN", 4: "JOY_LEFT", 5: "GND", 6: "JOY_RIGHT"}
for pin, (dx, dy) in PIN_JOY.items():
    label(JOY_NET[pin], *pin_abs(JX, JY, dx, dy))

# --- Power entry point (off-schematic source = USB, matching V0's PWR_FLAG convention) ---
place_symbol("power:+5V", "#PWR001", "+5V", "", 406.4, 60.96, [1])
place_symbol("power:PWR_FLAG", "#FLG001", "PWR_FLAG", "", 406.4, 60.96, [1])
place_symbol("power:GND", "#PWR002", "GND", "", 406.4, 406.4, [1])
place_symbol("power:PWR_FLAG", "#FLG002", "PWR_FLAG", "", 406.4, 406.4, [1])

# --- Assemble file ---
header = (
    '(kicad_sch\n'
    '\t(version 20260306)\n'
    '\t(generator "eeschema")\n'
    '\t(generator_version "10.0")\n'
    f'\t(uuid "{SHEET_UUID}")\n'
    '\t(paper "A2")\n'
    '\t(title_block\n'
    '\t\t(title "XMas Ornament 2026 V1")\n'
    '\t\t(comment 1 "121-LED serpentine chain, joystick, Xiao SAMD21, 74AHCT1G125 level shifter")\n'
    '\t)\n'
)

body = "\n".join(symbol_instances) + "\n" + "\n".join(annotations) + "\n"

footer = (
    '\t(sheet_instances\n'
    '\t\t(path "/"\n'
    '\t\t\t(page "1")\n'
    '\t\t)\n'
    '\t)\n'
    '\t(embedded_fonts no)\n'
    ')\n'
)

with open(OUT_SCH, "w") as f:
    f.write(header + lib_symbols_section + body + footer)

print(f"Wrote {OUT_SCH}")
print(f"Symbols: {len(symbol_instances)}, annotations: {len(annotations)}")
