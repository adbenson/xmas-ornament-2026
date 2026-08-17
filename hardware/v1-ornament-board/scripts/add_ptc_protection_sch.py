import csv
import re
import uuid as uuidlib

KICAD_DIR = "/home/welah/files-sync/projects/xmas ornaments/2026/hardware/v1-ornament-board/kicad"
PROJECT_DIR = "/home/welah/files-sync/projects/xmas ornaments/2026/hardware/v1-ornament-board"
MNT = "/tmp/.mount_kicadremp8173484700480565597"
SCH_PATH = f"{KICAD_DIR}/v1-ornament-board.kicad_sch"
CSV_PATH = f"{PROJECT_DIR}/led_chain_order.csv"
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


PIN_2TERM_VERT = {1: (0, 3.81), 2: (0, -3.81)}  # Polyfuse, R, C - same vertical shape
PIN_LED = {1: (-3.81, 0), 2: (3.81, 0)}  # K, A

# --- New lib_symbols: Polyfuse ---
lib_blocks = [load_lib_symbol(f"{MNT}/share/kicad/symbols/Device.kicad_symdir/Polyfuse.kicad_sym", "Polyfuse", "Device")]

# --- F1: PTC resettable fuse on the LED rail only (not Xiao/level-shifter/charge IC) ---
FX, FY = 300.0, 200.0
place_symbol("Device:Polyfuse", "F1", "FSMD100-1206R", "Fuse:Fuse_1206_3216Metric", FX, FY, [1, 2])
dx, dy = PIN_2TERM_VERT[1]
label("+5V", *pin_abs(FX, FY, dx, dy))
dx, dy = PIN_2TERM_VERT[2]
label("+5V_LED", *pin_abs(FX, FY, dx, dy))

# --- R3 + D124: trip indicator, wired directly across F1's two terminals (+5V / +5V_LED) ---
R3X, R3Y = 320.0, 190.0
place_symbol("Device:R", "R3", "1k", "Resistor_SMD:R_0402_1005Metric", R3X, R3Y, [1, 2])
dx, dy = PIN_2TERM_VERT[1]
label("+5V", *pin_abs(R3X, R3Y, dx, dy))
dx, dy = PIN_2TERM_VERT[2]
label("TRIP_LED_A", *pin_abs(R3X, R3Y, dx, dy))

D124X, D124Y = 320.0, 210.0
place_symbol("Device:LED", "D124", "TRIP_LED", "LED_SMD:LED_0603_1608Metric", D124X, D124Y, [1, 2])
dx, dy = PIN_LED[2]  # A
label("TRIP_LED_A", *pin_abs(D124X, D124Y, dx, dy))
dx, dy = PIN_LED[1]  # K
label("+5V_LED", *pin_abs(D124X, D124Y, dx, dy))

# --- Splice new lib_symbols + new components into the live schematic ---
text = open(SCH_PATH).read()

open_paren_idx = text.index("(lib_symbols")
depth = 0
j = open_paren_idx
while True:
    c = text[j]
    if c == '(':
        depth += 1
    elif c == ')':
        depth -= 1
        if depth == 0:
            lib_close_idx = j
            break
    j += 1
insertion = "\n" + "\n".join(lib_blocks)
text = text[:lib_close_idx] + insertion + "\n\t" + text[lib_close_idx:]

sheet_key = "\t(sheet_instances\n"
sheet_idx = text.index(sheet_key)
new_content = "\n".join(symbol_instances) + "\n" + "\n".join(annotations) + "\n"
text = text[:sheet_idx] + new_content + text[sheet_idx:]

# --- Revert D123 to SS14/D_SMA ---
text = text.replace(
    '(property "Value" "SD103AW"\n\t\t\t(at 654.94 158.4 0)',
    '(property "Value" "SS14"\n\t\t\t(at 654.94 158.4 0)',
)
text = text.replace('(property "Footprint" "Diode_SMD:D_SOD-123"', '(property "Footprint" "Diode_SMD:D_SMA"')

# --- Retarget the 121 LED VDD labels + 121 LED-cap pin1 labels from +5V to +5V_LED ---
# NOTE: must use the SCHEMATIC's own 11x11 grid (from build_v1_schematic.py), not the PCB's
# physical circle-layout coordinates from led_chain_order.csv - those are a different coordinate
# system entirely (caught via 0 matches on first attempt, not assumed correct).
SCH_LED_X0, SCH_LED_Y0 = 20.32, 20.32
SCH_LED_DX, SCH_LED_DY = 30.48, 22.86
SCH_CAP_DY = 10.16

retarget_positions = set()
with open(CSV_PATH) as f:
    n_leds = sum(1 for _ in csv.DictReader(f))
for i in range(n_leds):
    col = i % 11
    row = i // 11
    x = SCH_LED_X0 + col * SCH_LED_DX
    y = SCH_LED_Y0 + row * SCH_LED_DY
    led_vdd = pin_abs(x, y, -8.89, -1.27)
    cap_pin1 = pin_abs(x, y + SCH_CAP_DY, 0, 3.81)
    retarget_positions.add((f"{led_vdd[0]:g}", f"{led_vdd[1]:g}"))
    retarget_positions.add((f"{cap_pin1[0]:g}", f"{cap_pin1[1]:g}"))

print(f"Computed {len(retarget_positions)} target label positions to retarget")

pattern = re.compile(r'\(label "\+5V"\n\t\t\(at (-?[\d.]+) (-?[\d.]+) 0\)')


def sub_fn(m):
    key = (m.group(1), m.group(2))
    if key in retarget_positions:
        sub_fn.count += 1
        return f'(label "+5V_LED"\n\t\t(at {m.group(1)} {m.group(2)} 0)'
    return m.group(0)


sub_fn.count = 0
text = pattern.sub(sub_fn, text)
print(f"Retargeted {sub_fn.count} labels from +5V to +5V_LED")
assert sub_fn.count == 242, f"expected 242 retargeted labels, got {sub_fn.count}"

open(SCH_PATH, "w").write(text)
print(f"Added {len(symbol_instances)} symbols, {len(annotations)} labels; reverted D123 to SS14")
