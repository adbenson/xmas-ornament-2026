import csv
import pcbnew

PROJECT_DIR = "/home/welah/files-sync/projects/xmas ornaments/2026/hardware/v1-ornament-board"
PCB_PATH = f"{PROJECT_DIR}/kicad/v1-ornament-board.kicad_pcb"
CSV_PATH = f"{PROJECT_DIR}/led_chain_order.csv"

MM = pcbnew.FromMM
DEG = lambda a: pcbnew.EDA_ANGLE(a, pcbnew.DEGREES_T)

# row -> LED rotation, in pcbnew's positive=CCW convention (empirically verified this session):
#   "135deg CW"  -> -135
#   "45deg CCW"  -> +45
# Odd/even uses the project's existing 0-based row index (row 0 = bottom, matches
# led_chain_order.csv and every other row-parity decision made this session, e.g. serpentine
# chain direction). Trivial to flip if the intent was 1-based rows.
def led_rotation_for_row(row):
    # User thinks in 1-based row numbers (row 1 = bottom = "odd"); our `row` here is 0-based
    # (row 0 = bottom) - so 0-based even = user's odd = 135deg CW, 0-based odd = user's even = 45CCW.
    return -135.0 if row % 2 == 0 else 45.0

# Cap's position/orientation in the LED's own *canonical* (0deg) local frame - i.e. before the
# LED's row-based rotation is applied. Derived from the actual footprint pad geometry (probed via
# pcbnew directly, not assumed):
#   - LED pad 2 (GND) sits at local (-0.87, 0.55) at 0deg - top-left of the LED.
#   - Cap pad 2 (GND) sits at local (0, +0.48) after the cap's own -90deg (90 CW) rotation.
#   - So placing the cap center at local (-1.8, 0.07) puts the cap's GND pad at (-1.8, 0.55),
#     directly left of the LED's GND pad at the same Y, with ~0.27mm clearance from the LED's
#     leftmost copper edge (pad half-width 0.4mm at x=-1.27) - checked against real pad half-widths,
#     not eyeballed, then confirmed with DRC after the fact.
CAP_LOCAL_OFFSET = (-1.8, 0.07)
CAP_OWN_ROTATION = -90.0  # 90deg CW, in the LED's canonical frame, before the LED's own rotation


def main():
    board = pcbnew.LoadBoard(PCB_PATH)

    row_by_ref = {}
    pos_by_ref = {}
    with open(CSV_PATH) as f:
        for r in csv.DictReader(f):
            row_by_ref[r["led_ref"]] = int(r["row"])

    led_fps = {}
    cap_fps = {}
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref in row_by_ref:
            led_fps[ref] = fp
        elif ref.startswith("C") and ref[1:].isdigit() and 1 <= int(ref[1:]) <= 121:
            cap_fps[ref] = fp

    print(f"Found {len(led_fps)} LED footprints, {len(cap_fps)} cap footprints")
    assert len(led_fps) == 121 and len(cap_fps) == 121

    def hide_labels(fp):
        for prop_name in ("Reference", "Value"):
            field = fp.GetField(prop_name) if hasattr(fp, "GetField") else None
            if field is None:
                # Fallback: iterate fields
                continue
            field.SetVisible(False)

    n_rotated_led = 0
    n_rotated_cap = 0
    n_hidden = 0

    for led_ref, led_fp in led_fps.items():
        n = int(led_ref[1:])
        cap_ref = f"C{n}"
        cap_fp = cap_fps[cap_ref]
        row = row_by_ref[led_ref]

        led_pos = led_fp.GetPosition()
        led_x_mm, led_y_mm = pcbnew.ToMM(led_pos.x), pcbnew.ToMM(led_pos.y)

        theta = led_rotation_for_row(row)

        # Rotate LED in place (pivot = its own position, unaffected).
        led_fp.SetOrientationDegrees(theta)
        n_rotated_led += 1

        # Cap: set up in the LED's canonical (0deg) frame, then rotate around the LED's center
        # by the same angle theta - NOT around the cap's own center - per the requirement that
        # the cap track the LED's rotation as a rigid attachment.
        dx, dy = CAP_LOCAL_OFFSET
        cap_fp.SetPosition(pcbnew.VECTOR2I(MM(led_x_mm + dx), MM(led_y_mm + dy)))
        cap_fp.SetOrientationDegrees(CAP_OWN_ROTATION)
        cap_fp.Rotate(pcbnew.VECTOR2I(MM(led_x_mm), MM(led_y_mm)), DEG(theta))
        n_rotated_cap += 1

        for fp in (led_fp, cap_fp):
            ref_field = fp.Reference()
            val_field = fp.Value()
            ref_field.SetVisible(False)
            val_field.SetVisible(False)
            n_hidden += 2

    ok = pcbnew.SaveBoard(PCB_PATH, board)
    print(f"Rotated {n_rotated_led} LEDs, {n_rotated_cap} caps; hid {n_hidden} label fields")
    print("SaveBoard ok:", ok)


if __name__ == "__main__":
    main()
