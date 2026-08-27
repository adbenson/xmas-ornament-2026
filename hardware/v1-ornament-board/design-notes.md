# V1 Ornament Board — Design Notes

## Status

**Ordered from JLCPCB, 2026-08-17** (2× SMT-assembled boards + 1 spare bare board). R1/R2 hit
last-minute stock-outs; R1 swapped to RALEC `RTT022491FTH` (C102924, confirmed exact 0402/2.49k/±1%,
and a Basic part — better than the original), R2's proposed replacement had a real 0603-vs-0402
package mismatch (flagged, alternative found: Uniroyal `0402WGF1001TCE`/C11702). Invoice ($117.58
total: $58.70 merchandise + $34.81 shipping + $3.52 tax + $20.55/35.01% import tax) and the
assembly cost breakdown (Extended-component fee alone was ~$21.49, nearly matching base component
cost) are logged in this project's Claude memory for future order estimation, not duplicated here —
the invoice PDF itself (`invoice 2026-08-17.pdf`) has real PII, handle accordingly.

**Fully routed (2026-08-15)**, `kicad-cli pcb drc`: 0 violations, 0 unconnected items. 115 LEDs
(down from the original 121 — 6 removed to fit the joystick, see "LED grid"), 115 decoupling caps,
Xiao SAMD21 (U1), 74AHCT1G125 level shifter (U2) + its cap (C122), the ALPS joystick (SW1), and a
LiPo charge circuit (U3 MCP73832 + support components + JST-PH battery connector, see "Battery
charging" below) — all wired in the schematic and fully routed on the PCB. `kicad-cli sch erc`:
**0 errors**, only the same class of harmless pin-type warnings V0 saw.

**User-driven changes since 2026-08-16, done directly in the GUI** (verified against the live
files, not taken on faith):
- **Mounting holes removed** — the 4 holes from "Mounting holes" below are gone; the user will
  revisit hole placement later.
- **Back-side footprint count dropped from 6 to 3**: only **J1, U1, D123** remain on B.Cu now — U2
  (level shifter), U3 (charge IC), and F1 (PTC fuse) were moved to the front. This changes the
  JLCPCB front/back assembly split from "Fabrication package" below; that section's BOM/CPL split
  is now stale on top of already being stale from the mounting holes.
- **Trip indicator (D124, R3) removed from the PCB only** — **still present in the schematic**, a
  real desync, not just in-progress work. If "Update PCB from Schematic" is ever run again, both
  will silently reappear on the board. Left as-is per the user ("I might bring it back later") —
  flagged here so it doesn't cause a surprise down the line. F1 (the PTC fuse itself) is untouched;
  only the passive LED+resistor indicator branch across it is gone.
- **Decorative silkscreen additions** made directly in the GUI — not catalogued here in detail,
  user-owned per [[feedback_kicad_manual_layout]].

**Full re-review (2026-08-16)**: re-ran `sch erc`/`pcb drc` and manually verified every power/data
pin on the charge circuit, level shifter, and MCU against real datasheets/symbol pin definitions
(not just net names) — no new wiring bugs. Two minor, harmless things found:
- Two tiny (~0.5–0.7mm) dangling wire stubs in the schematic near U3's STAT pin, flagged by ERC as
  off-grid/unconnected — confirmed pre-existing (present in the very first git commit), and
  harmless (the real STAT connection is carried by proper junction-connected wires, these are just
  leftover stub cruft). Cosmetic only; clean up next time the schematic's open if it bugs you.
- One "isolated copper fill" DRC warning on the `+5V_LED` zone near (112, 98) — confirmed
  *not* caused by the R1 change below (reproduced identically with R1 reverted to 10k). Likely the
  same class of zone-fill/thermal-relief edge case as the dangling-GND-via finding from the original
  routing pass — not investigated further, flagging in case it's ever worth a closer look.

**Resolved (2026-08-16) — was never a via-placement bug at all.** The "GND via overlapping J1's
MP pad" finding above turned out to be a **lost net assignment, not a clearance problem**: the user
had deliberately set J1's two mechanical `MP` pads (confirmed electrically unconnected inside the
real JST connector) to the `GND` net on purpose, both for routing convenience and slightly better
board adhesion at that corner — a legitimate, intentional PCB-only net override (`MP` has no
matching schematic pin, so this can only be set directly on the pad, not through the netlist). That
override was silently lost at some point (most likely an "Update PCB from Schematic" sync, the same
category of wipe documented earlier for LED/cap placement — anything PCB-only with no schematic
counterpart doesn't survive a resync). Once the user reset both `MP` pads back to `GND` in the GUI,
`kicad-cli pcb drc` dropped from 4 violations/1 unconnected item to **1 warning, 0 errors, 0
unconnected items** — fixing this also silently resolved the "2 dangling GND vias" finding from the
original routing pass (one of those vias was this same MP-pad contact point; once real net data was
attached, the whole local copper island resolved as properly connected). **Only remaining item:**
the `isolated_copper` warning on the `+5V_LED` zone near (112, 98) — checked for nearby footprints
(none within 3mm), so it's a harmless disconnected copper sliver in the LED-grid fill pattern, not
tied to any component. **Watch for this recurring**: since `MP`'s `GND` assignment lives only on the
PCB with nothing in the schematic backing it up, any future "Update PCB from Schematic" will wipe it
again — worth remembering to re-check/reapply after that specific operation, not a one-time fix.

**R1 (charge current) bumped for the real cell (2026-08-16)**: now that the user has a 2Ah cell in
hand (400mA continuous / 2A peak per its datasheet), R1 changed from the placeholder 10kΩ (~100mA)
to **2.49kΩ (~401.6mA)** — see "Battery charging" below for the datasheet-sourced reasoning and a
thermal caveat worth knowing about. Schematic and PCB both updated; fab BOM's R1 line updated to
match but its LCSC part number needs resourcing at the next fab regen (marked TBD, not guessed).

**Battery polarity and PTC thermal open items closed out by the user, 2026-08-16**: J1's pinout was
checked against a charger from the same vendor as the actual battery pack (their verification, not
mine — noted here rather than re-derived). F1/U3's thermal dissipation is now tied into the ground
plane as well as the board's copper allowance allows, the user's own mitigation for the thermal
caveat flagged in "Battery charging" below.

**Fab package regenerated and ready (2026-08-16/17)** — Gerbers/BOM/CPL/hand-solder list all rebuilt
from the current live board (post mounting-hole-removal, post front/back-split change, post R1/D122
updates, post MP-pad fix, post silkscreen-artwork simplification — see "Fabrication package" below
for that last one). `pcb drc` on the exact board these were generated from: 1 warning (the
decorative isolated-copper item), 0 errors, 0 unconnected. Remaining open items: mounting hole
placement (deferred, the user's call) and the D124/R3 schematic/PCB desync (intentional, per the
user).

## Mounting holes (2026-08-16)

4× 3mm NPTH mounting holes (`MountingHole_3mm`, mechanical only, no net). **Final placement is the
user's own**, not algorithmically derived: two automated placement attempts (a squashed-X toward
vertical, then toward horizontal, both angle-optimized for component clearance — see git history /
prior design-notes revisions if the reasoning is ever needed again) didn't land where the user
wanted. They manually positioned one hole (**MH2_UL** at 92.5, 129.5) and deleted the other three
in the GUI; on request, the remaining three were added back as an exact mirror of MH2_UL across
both board axes (center 120, 150):

- **MH2_UL** (92.5, 129.5) — user-placed
- **MH1_UR** (147.5, 129.5) — mirrored across the vertical axis
- **MH4_LL** (92.5, 170.5) — mirrored across the horizontal axis
- **MH3_LR** (147.5, 170.5) — mirrored across both axes

**No collision checking was done on this final placement** — the user explicitly said to ignore
component and trace conflicts this time. Whatever DRC reports against these holes reflects real
conflicts, not something to reflexively "fix" — the user is routing/placing around them by hand.

**Fab package needs regenerating** (see "Fabrication package" below) once the user is done — the
current Gerbers/drill files predate these holes entirely.

## Tooling holes (2026-08-24)

The two mystery drill holes spotted in the JLCPCB-side gerber preview (one near the upper-left rim,
one near the tab) turned out **not** to originate from this design at all — JLCPCB support confirmed
they're **assembly tooling holes**, auto-added by JLCPCB itself for their SMT pick-and-place jig when
none are supplied in the order. Spec, from
[their tooling-hole article](https://jlcpcb.com/help/article/how-to-add-tooling-holes-for-pcb-assembly-order):
**1.152mm round NPTH, 0.148mm solder mask expansion, 2–3 holes, opposite corners, as far apart as
practical**; empty space preferred, copper area acceptable if there's no room.

Added two placeholder footprints (`MountingHole_1.152mm` style, PCB-only/mechanical, no net,
`exclude_from_pos_files`/`exclude_from_bom` like the mounting-hole footprints) so the user can
position them by hand instead of leaving it to JLCPCB's default placement next order:

- **TH1** (125, 100) — in the tab, roughly where JLCPCB's own auto-placed hole landed
- **TH2** (95, 124) — upper-left rim; currently sitting inside the `+5V_LED`/`GND` copper fill (0.25mm
  hole-clearance DRC error against both zones) since that's the only "empty-ish" nearby space — user
  will reposition, per [[feedback_kicad_manual_layout]]. `kicad-cli pcb drc` otherwise unchanged (same
  1 pre-existing `isolated_copper` warning near (112, 98) as before).

**Fab package not regenerated for this** — these are placeholders pending the user's final placement.

## Fabrication package (regenerated 2026-08-16)

Complete JLCPCB fab + assembly package under `fab/`, regenerated from the current live board state
(mounting holes removed, U2/U3/F1 now front, MP-pad GND fix, R1=2.49k, D122=red — all reflected).
**Assembly split unchanged: JLCPCB assembles the front only; the user hand-solders 3 back-side
parts.**

- `GERBER-v1-ornament-board.zip` — RS-274X Gerbers (F.Cu, B.Cu, paste, silkscreen, mask ×2,
  Edge.Cuts) + Excellon drill + drill map, zipped per JLCPCB's upload convention.
  `kicad-cli pcb export gerbers --layers F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,
  F.Mask,B.Mask,Edge.Cuts` (explicit layer list — the tool's default exports every layer including
  Courtyard/Fab/User/Adhesive/Margin, which JLCPCB doesn't need).
  **Decorative-artwork silkscreen simplified, 2026-08-16/17**: the traced snowflake-ornament
  graphic on F.Silkscreen (320 `gr_poly` shapes, ~192,400 points total, several single polygons
  over 10,000–46,000 points) wasn't going to cause JLCPCB to reject the order — Gerber format and
  their CAM tooling have no meaningful vertex-count limit at this scale — but the fine vector
  detail was well past silkscreen printing's real physical resolution floor (~0.15mm line/gap), so
  most of it wouldn't have reproduced anyway. Ran Ramer–Douglas–Peucker simplification (0.08mm
  tolerance — conservative, well under the print floor, so nothing visible was traded away) on
  every polygon with ≥8 points (`gr_poly`s under that were already simple stroke-line segments, left
  untouched); the tiny <8-point polygons themselves weren't the size problem, so they were skipped.
  Result: 192,414 → 4,266 points (**97.8% reduction**), `F_Silkscreen.gto` 5.08MB → 231KB, full zip
  1.25MB → 219KB (below the original pre-decoration 167KB). **Verified, not just trusted the math**:
  rendered both the pre- and post-simplification F.Silkscreen layer via `kicad-cli pcb export svg` +
  headless Chrome screenshot and compared them side by side at the same crop/zoom — visually
  identical. `pcb drc` unchanged after (1 warning/0 errors/0 unconnected, same as before). Original
  `.kicad_pcb` state saved in the scratchpad before running, in case the user ever wants the
  full-detail original back — this changes the *rendered/manufactured* result, not something to
  redo blindly if the user re-imports a fresh version of the artwork later.
- `BOM-v1-ornament-board.csv` — `Comment,Designator,Footprint,LCSC Part #`, **front-side only**: 10
  lines / 240 parts (115 LEDs, 116 caps [115 LED decoupling + C122], R1, R2, SW1, D122, U2, U3, F1).
  Regenerated directly from the live board's footprint list via `pcbnew` (grouped by
  layer+value+designator), not hand-edited — verified the front/back split and part counts against
  the board before writing anything.
- `CPL-v1-ornament-board.csv` — `Designator,Mid X,Mid Y,Layer,Rotation`, front-side only, 240 rows,
  all `Layer=Top`. From `kicad-cli pcb export pos --side both`, filtered to `Side=top`.
- `HAND-SOLDER-v1-ornament-board.csv` — **new**, the user's own order list for the 3 back-side
  parts (J1, D123, U1) — see table below.

**Back-side parts — hand-solder order list (3 parts, matches the user's own count)**. DigiKey part
numbers added 2026-08-17, verified via WebSearch+WebFetch against real DigiKey product pages
(specs cross-checked, not assumed from the part number alone):

| Part | Designator | LCSC # | DigiKey # | Note |
|---|---|---|---|---|
| JST S2B-PH-SM4-TB | J1 | C295747 | `455-1749-1-ND` | [DigiKey product page](https://www.digikey.com/en/products/detail/jst-sales-america-inc/S2B-PH-SM4-TB/926655) — confirmed JST PH series, 2-position, 2.00mm pitch, SMD, exact match to the footprint in use |
| SS14 (SMA) | D123 | C112424 | `SS14CT-ND` (onsemi) | [DigiKey product page](https://www.digikey.com/en/products/detail/onsemi/SS14/965474) — confirmed 40V/1A Schottky, DO-214AC/SMA package. Check polarity by hand when soldering. |
| Xiao SAMD21 | U1 | **none** | **none** | Seeed SKU `102010328`, [product page](https://www.seeedstudio.com/Seeeduino-XIAO-Arduino-Microcontroller-SAMD21-Cortex-M0+-p-4426.html) — not LCSC/DigiKey-stocked, was never a JLCPCB-assemblable part regardless of front/back split |

U2 (level shifter), U3 (charge IC), and F1 (PTC) are **no longer on this list** — they moved to the
front on 2026-08-16 and are now in the JLCPCB order instead.

**Front-side (JLCPCB order) LCSC part sourcing** (verified via WebSearch/WebFetch against real
LCSC/JLCPCB listings, not guessed):

| Part | LCSC # | Note |
|---|---|---|
| WS2812B-2020-V6 | C52917434 | already known from LED sourcing |
| SKRHABE010 (SW1) | C139794 | exact match; **has 2 through-hole mechanical pads** alongside SMD electrical pads — may need JLCPCB's mixed-technology/THT assembly option |
| 0402 100nF | C309458 | Basic part |
| 0402 1µF | C52923 | Basic part |
| 0402 2.49k (R1) | ~~C20164962~~ **C102924** | Originally sourced as YAGEO `RT0402BRB072K49L` (±0.1%, Extended part). **Swapped 2026-08-17** — the user hit a stock-out on that part and proposed RALEC `RTT022491FTH` instead; confirmed via JLCPCB partdetail: 0402, 2.49kΩ, ±1%, and it's a **Basic** part (better than the original — no Extended-part fee). |
| 0402 1k (R2) | C2889341 | Basic part |
| KT-0603R (D122, red) | C2286 | Basic part, picked 2026-08-16 |
| 74AHCT1G125 (U2) | C7484 | SN74AHCT1G125DBVR — the *intended* real part (schematic uses the base `74LVC1G125` symbol with `Value` overridden, see "Schematic" above). Moved to front-side order 2026-08-16. |
| MCP73832-2-OT (U3) | C38066 | exact match. Moved to front-side order 2026-08-16. |
| FSMD100-1206R (F1) | C220149 | already known from PTC sourcing. Moved to front-side order 2026-08-16. |

**Known JLCPCB/KiCad gotcha, still worth checking in their checkout preview**: community reports
confirm KiCad's raw rotation/position export doesn't always match what JLCPCB's placement engine
expects for certain footprints. This mainly matters for SW1 (mixed SMD+THT) — check its orientation
in JLCPCB's interactive placement preview before finalizing.

**PCB is now netlist-linked to the schematic** (the user ran "Update PCB from Schematic" in the GUI).
That sync initially scattered the LED/cap placement, because the footprints my script had placed
were never associated with schematic symbols (no `path` UUID linking them) — expected once a real
schematic existed to sync against. Re-applied the grid positions from `led_chain_order.csv`
directly onto the live, now-linked PCB with `scripts/reposition_leds_caps.py` (targeted
`(at X Y)` rewrite by Reference designator, everything else untouched). `kicad-cli pcb drc` now
reports 499 "unconnected items" — expected and correct, not a regression: with real nets present,
DRC's ratsnest can finally see that nothing's routed yet.

## Schematic

Built programmatically (`scripts/build_v1_schematic.py`, kept in-tree like the PCB script) since
there's no eeschema-equivalent of `pcbnew`'s Python API — the file is hand-assembled KiCad 10
`.kicad_sch` S-expression text, using each library's actual `(symbol ...)` block (extracted from
the real `.kicad_sym`/`.kicad_symdir` files, not retyped) for the embedded `lib_symbols` section.

**Connectivity style**: every net is formed by placing a `(label ...)` exactly at a pin's computed
absolute position — no drawn wire segments. This is a deliberate simplification from V0's
hand-routed wire-stub-plus-label style: functionally identical (KiCad connects anything whose
coordinates coincide, wire or not) and far more tractable to generate correctly at 250-symbol
scale. Confirmed correct-by-construction via `kicad-cli sch erc`, not just visual inspection.

**Real gotcha hit and fixed**: a symbol library's local coordinate system has Y *increasing
upward*, but the schematic sheet has Y increasing *downward* — so an unrotated instance's absolute
pin position is `(symbol_x + pin_dx, symbol_y − pin_dy)`, not `+ pin_dy`. Found this empirically
(first draft had 659 ERC violations, nearly all `pin_not_connected`/`label_dangling` from labels
landing off their pins by exactly `2×pin_dy`) rather than assumed — same kind of sign-convention
trap V0 hit with footprint rotation, same fix (verify against real tool output, don't guess).

**Reused from V0 unchanged** (pin mapping, component choices — the user's ask was to check V0 rather
than re-derive):
- Xiao SAMD21 pins: `JOY_UP`=D6, `JOY_DOWN`=D2, `JOY_LEFT`=D0, `JOY_RIGHT`=D1, `JOY_SELECT`=D3,
  `LED_DATA_IN`=D9. Unused pins (D4,D5,D7,D8,D10,3V3_OUT,SWDIO,SWCLK,EN,VIN) marked no-connect.
- Level shifter: Xiao D9 → `LED_DATA_IN` → gate input (pin 2) → gate output (pin 4) →
  `LED_DATA_OUT` → D1's DIN. OE (pin 1) tied to GND (always enabled). VCC/GND to the shared rails.
  Used the base `74xGxx:74LVC1G125` symbol with `Value` overridden to `74AHCT1G125` (matches V0
  exactly) rather than the newer native `74AHCT1G125` symbol this KiCad ships — that one
  `(extends "74LVC1G125")`, and embedding an `extends`-based symbol into a schematic's
  `lib_symbols` was an unverified edge case not worth the risk when V0's approach is proven.
- Joystick pins 1–6 = UP/SELECT/DOWN/LEFT/COMMON(GND)/RIGHT, matching V0's SKRHABE010 pinout.
- One real `power:+5V`/`power:GND` symbol pair + `PWR_FLAG` each marks where power actually enters
  (off-schematic, from USB) — everything else just uses local labels `+5V`/`GND`, which merge into
  the same nets since this is a single-sheet schematic (same pattern V0 used, 0 ERC errors there).

**Reference numbering diverges from V0 on purpose**: V0 numbered LED caps `C2`-`C37` (C1 reserved
for the level shifter's cap). V1 already had `C1`-`C121` placed on the PCB for the LED caps before
this component set existed, so the level shifter's cap is `C122` instead — avoids renumbering 121
already-generated PCB parts for a cosmetic-only difference.

**Layout**: LEDs+caps in an 11×11 grid in schematic space (not meant to mirror physical PCB
placement, same as V0), MCU/level-shifter/joystick/power off to the right. Coordinates kept as
multiples of 2.54mm so every pin lands on the standard 1.27mm grid (no `endpoint_off_grid`
warnings). Dense/cramped at this component count — cosmetic only, same category of cleanup as the
PCB's silkscreen warnings below.

## LED part

**WS2812B-2020-V6** (Worldsemi), LCSC `C52917434`, footprint code
`LED-SMD_4P-L2.2-W2.0-P1.00_WS2815C-2020-4P` — a 2.0×2.0mm 4-pad package, real courtyard 2.0×2.0mm.
This resolves the V0 sourcing problem (XL-3535RGBC-WS2812B went out of stock, WS2812-compatible
parts are hard to search for): this is a current, stocked JLCPCB Extended Part, and much smaller
than V0's 3535 package, which is what makes 121 LEDs fit in the same 75mm diameter V0 was using
at 36 LEDs in ~57mm.

the user supplied the EasyEDA/JLCPCB raw export JSON for this part
(`hardware/part CAD/jclpcb 2812B 2020/`, both SCHLIB and PCBLIB). Rather than hand-parsing that
JSON's coordinate format, symbol + footprint were generated via `easyeda2kicad` fetching the same
part directly from LCSC by part number (`C52917434`) — an authoritative conversion, not a
hand-derived one (see [[feedback_hardware_footprints]] on why that distinction matters). Copied
into `kicad/libs/ws2812b_2020.kicad_sym` and `kicad/libs/footprints.pretty/`, registered in the
project's `sym-lib-table`/`fp-lib-table` under nicknames `ws2812b_2020` / `footprints`. KiCad can
also import the raw EasyEDA JSON directly if preferred — the converted files here just let the PCB
placement script proceed without waiting on a manual GUI import step.

Decoupling cap: **100nF, 0402 imperial** (= 1005 metric — see V0's package-naming-trap lesson,
avoided here since the user specified the imperial code explicitly). Stock KiCad footprint
`Capacitor_SMD:C_0402_1005Metric`.

## Board outline

Circle, 75mm diameter (R=37.5mm), tangent-joined 16×16mm square tab at top — same technique as V0
(see V0's design-notes for the derivation): tab bottom edge sits at the height where the circle's
chord width equals the tab width (`dy = sqrt(R² - (tab_w/2)²)`), so the tab's vertical sides meet
the circle with no step/notch. For 75mm/16mm that's `dy ≈ 36.637mm`, i.e. the tab starts ~0.86mm
above the circle's apex and extends 16mm further up. Overall board footprint: 75mm wide ×
~90.14mm tall.

## LED grid

Originally 121 LEDs in a square lattice, uniform **5.5mm pitch** (both row and column spacing), 13
rows × up to 13 columns, row counts `3,7,9,11,11,13,13,13,11,11,9,7,3` (row 0 = bottom, row 12 =
top; the 13-count rows are 5,6,7). Each row's LEDs are centered on the 13-column lattice (all
counts odd, so centering is exact with no half-pitch offset).

**Now 115 LEDs (2026-08-15)**: D1, D2, D3, D6, D7, D8 and their matching caps C1–C3, C6–C8 were
removed from both the schematic and PCB to physically fit **SW1 (the joystick)** inside the LED
grid — this is what finally resolved the long-open "MCU/joystick physical placement" item below.
**The MCU (U1) did not require this** — its placement doesn't affect the LED layout at all; only
the joystick's footprint needed grid space carved out for it. Data chain was correctly re-spliced
around the gap (`LED_DATA_OUT` feeds D4 directly, D5's DOUT feeds D9's DIN directly via a reused
net) — verified by direct inspection of pad net assignments on the PCB, not assumed from the
routed-segment count alone. Worst-case full-white current drops accordingly: 115 × 36mA ≈ 4.14A
(was 4.35A at 121) — doesn't change the PTC conclusion, just the number.

Pitch was derived, not guessed: for this specific count pattern the farthest lattice point from
center is always at `sqrt(6²+1²)·pitch = 6.083·pitch` (rows 0/5/7/12's outer corners), so pitch
was set so that distance stays inside `R` with margin: `6.083 × 5.5mm ≈ 33.46mm`, leaving ~4mm
to the 37.5mm board edge for component courtyard + copper clearance. `kicad-cli pcb drc` on the
result: **0 courtyard/copper-clearance violations** — the physical fit is confirmed, not just
eyeballed. (399 silkscreen-only warnings — overlapping/edge-clipped reference designator text at
this density — are expected and cosmetic; same category of cleanup V0 deferred to "once routing is
done.")

**Chain order**: serpentine starting at the bottom row (nearest where the MCU will sit, per V0's
"start the chain near the MCU" lesson), row 0 left→right, row 1 right→left, alternating up to row
12. Reference designators `D1`–`D121` and paired caps `C1`–`C121` follow this order; full
coordinates in `led_chain_order.csv` (chain_index, led_ref, cap_ref, x_mm, y_mm, row, col) for
whoever wires the schematic next.

**Cap placement**: each cap sits *above* its LED (−Y, half a pitch = 2.75mm, toward the tab/top of
the board — the user's call), same `X`. Still a placeholder side, not a final decision — the user hasn't
picked LED orientation yet (see [[feedback_kicad_manual_layout]] and V0's lesson that cap side
should follow whichever way the LED's VDD pad rotates to). This direction was chosen only because
it's collision-safe at every position in this grid (verified by DRC, same margin analysis as the
`+X` version it replaced — the lattice is square/uniform-pitch so the safety argument transfers
exactly); expect to change per-row/per-LED once rotation is chosen, same as V0 did.

## PCB: MCU / level shifter / joystick placement

**Resolved (2026-08-15)**. All four — U1 (Xiao), U2 (level shifter), C122 (its cap), and SW1
(joystick) — are now on-board (all within the 37.5mm board radius). Only **SW1** required carving
space out of the LED grid: 6 LEDs + their caps (D1–D3, D6–D8 / C1–C3, C6–C8, see "LED grid" above)
were removed to make physical room for the joystick's footprint. **U1's placement did not require
any LED removal** — the MCU fit without touching the grid, unlike the joystick.

## Battery charging

Added a LiPo/Li-Ion charge circuit + JST-PH 2.0mm battery connector, since this seems to resolve
the Project Plan's open "alkaline or LiPo?" battery question in LiPo's favor (Project Plan.md's
Battery row should get a matching update — flagging here in case that hasn't happened yet).

**U3 = MCP73832-2-OT** (SOT-23-5, single-cell Li-Ion/LiPo linear charge management controller,
4.20V regulation, open-drain STAT output) — used KiCad's own stock `Battery_Management:MCP73832-2-OT`
symbol (real part, real pinout, not hand-derived) rather than the base `MCP73832` some other
suffix variants extend from — same "avoid embedding an `extends`-based symbol" reasoning as the
level shifter. Standard Microchip reference-design support components, sized/valued per the
datasheet's typical application circuit:
- **R1 = 2.49kΩ** on PROG→GND: sets charge current via `I_reg[mA] = 1000 / R_PROG[kΩ]`
  (confirmed against the real MCP73831/2 datasheet, not assumed — DS20001984H, `Rprog` range is
  2kΩ–67kΩ, programmable current 15mA–500mA). 2.49kΩ (nearest standard E96 1% value) gives
  ≈401.6mA, matching the user's chosen 2Ah cell's 400mA continuous charge rating (was 10kΩ/100mA,
  a placeholder from before a real cell was picked). 2kΩ (the IC's ~500mA max) is explicitly
  footnoted in the datasheet as "not production tested, ensured by design" — 2.49kΩ sits safely
  inside the characterized range, not at that edge.
  **Thermal caveat — mitigated as well as the board allows (2026-08-16)**: during charge `VDD` is
  USB's ~5V (charging only happens with USB present) and early in a cycle `VBAT` can be as low as
  ~3.0–3.5V, so the pass transistor can dissipate up to ~0.7–0.8W (θJA ≈ 130–230°C/W depending on
  copper — DS20001984H). Enough to trip the IC's own automatic thermal regulation (a designed-in
  protection, not a fault) without help. The user tied U3's thermally-relevant pads into the ground
  plane as well as the board's copper allowance permits, which is the standard mitigation for this
  package (matches the datasheet's own note that θJA improves substantially with more copper around
  the part). Real-world charge current/time still may not hit the full 400mA/~5hr figure under
  thermal regulation — worth confirming with a meter once the board exists, but this is no longer an
  unaddressed gap.
- **C123 = 1µF** on VDD→GND (input bypass), **C124 = 1µF** on VBAT→GND (output stability) — both
  0402 imperial, matching the rest of the board's small-part convention.
- **R2 = 1kΩ + D122 (charge-status indicator, VDD→R2→LED anode→LED cathode→STAT)**. STAT sinks
  (open-drain, active while charging) so the LED lights during charging, off when done/no battery —
  standard reference-design pattern, not required but cheap and useful feedback for a device that'll
  be handed to kids. **Color picked 2026-08-16: red**, part = **KT-0603R** (Hubei Kento, LCSC
  `C2286`, JLCPCB Basic part, 0603, 615–630nm, Vf 1.8–2.4V @ 20mA test current). Checked R2 against
  the real part rather than assuming 1kΩ was still fine: during charging `VDD` is USB's ~5V, and at
  our much lower ~2–3mA drive current (vs. the LED's 20mA-rated test point) Vf will sit below the
  datasheet's 20mA figure — working out to roughly **2.0–3.3mA** through the LED across
  USB-tolerance/Vf-spread corners, comfortably inside both the LED's 25mA max and the MCP73832
  STAT pin's 25mA sink max. That's a modest-but-visible indicator current, not miswired or
  underdriven — **1kΩ kept as-is**. (680Ω would land closer to ~4mA/brighter if the user ever wants
  a more obviously-lit indicator; not changed since it wasn't asked for.)
- **D123 = SS14 Schottky** (SMA, anode→VBATT, cathode→+5V), **1A rated**. Briefly swapped to
  SD103AW (SOD-123, 350mA — the user had them in stock) but reverted back to SS14 once the user decided
  the LED rail should support up to ~1A (see "LED current protection" below) — his battery
  shortlist is rated to 1.5A, and a 350mA diode would've silently become the real ceiling on
  battery power regardless of anything downstream. See "Xiao power caveat" below for what this
  diode is for — lets the battery feed the system rail without a boost converter, while isolating
  it from USB's 5V when a cable is plugged in.
- **J1 = 2-pin JST-PH 2.0mm** (`Connector:Conn_01x02_Pin` +
  `Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal`), Pin 1→VBATT(+), Pin 2→GND(−).
  Originally placed with the PTH variant (`..._S2B-PH-K_1x02..._Horizontal`); switched to this SMD
  variant (same horizontal orientation/pinout) once the user confirmed the connector was still
  through-hole and asked to switch — matches the rest of the board's SMD-first assembly approach.
  Swapped via `scripts/swap_j1_footprint.py` (schematic `Footprint` property text edit + PCB
  `Remove()`+`FootprintLoad()`/`Add()` at the same position/orientation, same pattern as D123's
  package swap — a plain text edit doesn't work PCB-side because PTH/SMD pad geometry differs).
  The SMD footprint's two extra "MP" pads are mechanical-only (board-edge anchor tabs, confirmed
  by the user as not connected to the connector's real contacts inside the part) — initially left
  unassigned, then the user deliberately tied both to `GND` for routing convenience and slightly
  better board adhesion. That override is PCB-only (no matching schematic pin) and was lost once,
  presumably to an "Update PCB from Schematic" resync — see "Full re-review" in Status above for the
  DRC-error trail this caused and how it was diagnosed. `kicad-cli sch erc`/`pcb drc` after the
  original swap: no new J1-related violations (pre-existing LED-grid `pin_to_pin`/silkscreen counts
  unchanged).

**✅ Battery polarity verified (2026-08-16).** The user checked J1's pinout against a charger from
the same vendor as the actual battery pack — resolves what was flagged as a real, common
reversed-LiPo-connection risk (JST-PH 2-pin pinout isn't standardized across manufacturers). Their
verification, not independently re-derived here.

**Xiao power caveat (researched, not assumed)**: Seeed's own documentation is explicit that the
XIAO SAMD21's back-side `VIN`/`GND` pads are *not* designed for a direct battery connection
("especially not a rechargeable lithium battery"), and recommends powering it from an external
charge/protection module's output wired to the front **5V** pin instead — which is exactly what
D123 does here (VBATT → diode → the existing `+5V` net, which the Xiao's own 5V pin already sits
on). A follow-up search turned up the actual reasoning and the fix for the remaining risk: without
isolation, plugging in USB while a battery is present would let USB's 5V back-feed the battery
node; a series Schottky (SS14 here) between the battery and the 5V pin blocks that (reverse-biased
once USB drives the node to 5V), which is exactly D123's
job. **One unresolved caution from the same research, not yet mitigated in hardware**: Seeed's own
docs go further and say the plain XIAO SAMD21 "cannot connect to Type-C while a battery is
connected... it may pose a safety risk" and that the board "lacks the essential battery management
circuitry required for safe operation" — a stronger statement than just "add a diode." Whether the
diode here is sufficient or whether USB+battery-simultaneous should be avoided entirely (e.g. in
firmware/instructions, "unplug USB before/after swapping the battery") is the user's call — flagging
it clearly rather than silently assuming the diode fully resolves it.
[Seeed XIAO SAMD21 wiki](https://wiki.seeedstudio.com/Seeeduino-XIAO/),
[Designing a XIAO Expansion Board — Schottky backfeed protection](https://www.seeedstudio.com/blog/2025/11/24/designing-a-xiao-expansion-board-using-a-schottky-diode-to-prevent-power-backfeeding/).

**Not addressed here, worth flagging given Safety is priority #1**: MCP73832 has no thermal
monitoring (that's the MCP73833/73834 family, which adds a THERM pin) and provides *charge
regulation* only, not cell *protection* (over-discharge/over-current/over-voltage cutoff during
normal use). Recommend sourcing a **protected** LiPo cell (built-in PCM) rather than a bare cell —
common and cheap for small hobby cells, and the standard way this gap gets closed in designs like
this one, without adding a separate protection IC to the BOM.

## LED current protection

Since kids (including the user's target audience — older kids reprogramming the board) will be
writing firmware for this, **current limiting can't live in software only** — a one-line
`fill_solid(leds, 121, CRGB::White)` is an easy, non-malicious thing to type. Checked the real
numbers rather than assuming: WS2812B-2020's datasheet rates it at **12mA/channel**, so 36mA/LED
at full white → **121 × 36mA ≈ 4.35A** worst case. That's far beyond what any of D123, a small
LiPo, or most USB ports should be asked to sustain, so hardware limiting on the LED rail is
required, not optional. The user's call: **ungraceful degradation is fine** — an abrupt full shutoff
that needs a manual-instructions note ("if it goes dark, you asked for too much brightness") beats
relying on firmware to self-limit correctly.

**F1 = FSMD100-1206R** (Fuzetec, LCSC `C220149`), a **1.00A-hold PTC resettable fuse**, 1206
package. Placed in series between the shared `+5V` rail and a **new, separate `+5V_LED` net** that
feeds only the 121 LED VDD pins (and their decoupling caps) — *not* the Xiao, level shifter, or
charge IC, which stay directly on `+5V`. Deliberate: if F1 trips, the LEDs go dark but the Xiao
stays powered and immediately reprogrammable over USB, rather than the whole board looking dead
and needing a cooldown-and-reset cycle. This is also why D123 got reverted to SS14 (1A) rather
than staying SD103AW (350mA) — with a 1A-class PTC now setting the real limit, the diode needed
to not be the tighter bottleneck once the user confirmed their battery shortlist supports it.

All 121 `LED VDD` pin labels and all 121 LED-decoupling-cap pin-1 labels were retargeted from
`+5V` to `+5V_LED` (242 labels, matched by exact schematic coordinate, not a blanket text
replace — the same `+5V` text also appears on the Xiao/level-shifter/charge-IC side, which must
stay put). **Note for next PCB sync**: this net split happened in the schematic only; the PCB
hasn't been re-synced yet, so F1/R3/D124's copper connections and the `+5V`/`+5V_LED` split on
existing pads won't show up on the board until the user runs "Update PCB from Schematic" again — and
per the last time that happened, expect it to require another LED/cap repositioning pass
afterward (same fix as before, `scripts/reposition_leds_caps.py`).

**Trip indicator, added for near-zero extra complexity**: R3 (1kΩ) + D124 ("TRIP_LED", 0603)
wired in series directly *across F1's own two terminals* (+5V → R3 → D124 → +5V_LED) — not a
separate sensing circuit. This works because of how a PTC behaves: tripped, its resistance jumps
from a fraction of an ohm to tens of kΩ+, so nearly the full rail voltage suddenly appears across
it (and thus across the parallel R3+D124 branch), lighting the LED; untripped, the PTC's tiny
resistance means it barely drops any voltage, so the branch stays dark. Fully passive — no MCU,
no comparator, works even with the firmware not running, consistent with "can't count on
software" for the safety-relevant part of this circuit.

Not yet sized/verified against real firmware current draw — this is all based on the datasheet's
worst-case number, not a measurement. Worth reconfirming once the user has actual animations running
and can check real board current with a meter.

**System rail implication**: `+5V` (the level shifter and Xiao) and `+5V_LED` (all 121 LEDs, via
F1) are no longer *only* ~5V from USB — via D123 both are also fed by VBATT (nominal 3.0–4.2V,
minus the Schottky's ~0.3–0.5V drop) whenever USB isn't present. Functionally this means: on
battery, the LEDs run at a lower, more variable voltage than on USB, which affects WS2812
brightness/timing margin (a known, accepted tradeoff for small battery-powered NeoPixel projects,
not a defect) — worth keeping in mind when the user sets the firmware brightness cap.

## LED/cap orientation, silkscreen cleanup, GND stitching

Orientation (the "Open items" #1 above) is now decided and applied on the PCB:

**Labels hidden**: `Reference`/`Value` silkscreen fields are hidden (`SetVisible(False)`) on all
121 LEDs and 121 caps — at 5.5mm pitch there's no room to lay these out legibly, and with the
`led_chain_order.csv` reference already mapping every designator to a grid position, on-silkscreen
labels weren't adding information. Resolves the 399 `silk_overlap`/`silk_over_copper` DRC warnings
noted in "Open items" #5 above as a byproduct.

**Cap repositioned + rotated**: each decoupling cap moved from "above the LED" (the placeholder
from the LED grid section above) to the LED's **left side, GND-pad-proximate** — cap rotated 90°CW
in the LED's own canonical (unrotated) frame, then positioned so the cap's GND pad sits directly
left of the LED's GND pad at matching Y, ~0.27mm copper-to-copper clearance (derived from real pad
geometry probed via `pcbnew`, not eyeballed — see `scripts/rotate_leds_caps.py` header comments for
the exact pad coordinates used).

**LED+cap unit rotated per row** (135°CW on odd rows / 45°CCW on even rows, in the user's 1-based
row numbering where row 1 = bottom), so adjacent LEDs' in/out data pads aren't directly lined up —
the user's call, purely a routing/aesthetic choice. Implemented as a **rigid rotation around the
LED's own center** (`Footprint.Rotate(pivot, angle)` with the LED's position as pivot, not
the cap's own center) so the cap tracks the LED exactly, applied after the cap's local
offset+90°CW was set in the LED's unrotated frame — get this pivot wrong and the cap swings out to
the wrong spot instead of staying pinned to the LED.

**Real bug hit and fixed**: first version had row 1 (odd, should be 135°CW) and row 2 (even, should
be 45°CCW) swapped — an off-by-one on the 1-based/0-based row convention (project's
`led_chain_order.csv` and every other row-parity decision this session use 0-based rows; the
rotation script's first draft mapped 0-based-even → 135°CW instead of 0-based-odd → 135°CW). The
user caught it as "everything is 180 out of whack" while confirming "caps are perfect" — i.e. the
rotation *mechanism* (pivot, cap offset) was correct, only the per-row angle assignment was
backwards, and −135°/+45° are exactly 180° apart, confirming the diagnosis before touching code.
Fixed by swapping the parity branches; verified by the DRC violation count changing as predicted
(399→122) rather than re-eyeballing the board.

**GND vias**: after the user added copper fill/zone layers in the GUI, dropped a via on every GND
pad (`scripts/add_gnd_vias.py`) sized to match the Power net class (0.8mm/0.4mm drill, same as
"Net classes" below) — 252 unique vias, one per GND pad across the 121 LEDs + 121 caps + other GND
pins. **Real bug hit and fixed**: a user GUI save partially overwrote the first via-adding run
(254→242 vias survived), and rerunning the same script blindly added 252 *more* on top without
checking what already existed, landing at 494 (many exact-position duplicates) — caught via a
sanity-check `grep -c '(via'` count that was unexpectedly high, not trusted blindly. Fixed with
`scripts/dedupe_vias.py` (keep one via per unique `(x, y)`, remove the rest), landing back at the
correct 252. Lesson for any future via-adding pass: check for an existing via at each pad position
before adding a new one, rather than assuming a clean board.

## Net classes

`GND`, `+5V`, `+5V_LED`, and `VBATT` are assigned to a **Power** net class (project settings →
`net_settings`, same mechanism V0 used) with **0.6mm min track width / 0.8mm via / 0.4mm drill**,
vs. `Default`'s 0.2mm/0.6mm/0.3mm. Sized for the 1A LED-current budget (see "LED current
protection" above) — 0.6mm on 1oz copper carries roughly 1.6A at a conservative 10°C rise (IPC-2221
external-layer estimate), so there's real margin above the 1A target, not just-barely-enough. Since
this is project-settings-level (not per-track), it applies automatically once the user starts routing;
nothing to redo on the LED grid itself. No tracks exist yet, so this doesn't change anything
visible until routing starts — it just sets the rule DRC/the router will enforce then.

**Root cause of the repeated disappearance found (2026-08-15), not just assumed**: this was the
*third* time `Power` had to be re-added — twice it silently reverted to just `Default`. Confirmed
why: a `~v1-ornament-board.kicad_pro.lck` lock file shows KiCad has the project open live while
these edits were happening. KiCad loads project settings (including net classes) into memory once
at project-open time and does **not** hot-reload `.kicad_pro` from disk during a running session —
so a script editing the file on disk while KiCad is open changes nothing in the live GUI's state.
The next time KiCad itself writes the project file for *any* reason (schematic save, PCB save,
closing a settings dialog), it writes back its own stale in-memory net classes, silently
clobbering the disk-only edit. This isn't a random KiCad quirk, it's a live-file-open problem
specific to `.kicad_pro` (unlike `.kicad_sch`/`.kicad_pcb`, which KiCad *does* reliably pick up
correctly when reopened/synced during this project). **For this to actually stick**: either add
the `Power` class + patterns via Board Setup → Net Classes in the GUI directly (the only path
guaranteed not to get overwritten by KiCad's own next save), or close and fully reopen the project
so KiCad reloads `.kicad_pro` from disk before its next save.

## Routing complete (2026-08-15)

The user finished routing the whole board. Verified, not just eyeballed off a render (a full-board
PDF export at this component density is too small to make out individual 0.2mm data-chain traces
against the copper pour — confirmed programmatically instead):
- `kicad-cli pcb drc`: **0 violations, 0 unconnected items**.
- `+5V_LED` (F.Cu) and `GND` (B.Cu) are each a filled copper zone rather than discrete traces —
  expected, that's why they don't show as routed segments in a segment-count scan.
- All 114 `LED_CHn` chain-link nets that should exist have routed copper; the one "missing" one
  (`LED_CH121`) is correct and expected — D121 is the chain's last LED, so its data-out pad is
  properly `unconnected` (nothing follows it).
- A handful of GND/+5V segments near the U1/joystick corner are routed at 0.2mm (Default) rather
  than 0.6mm (Power class) — **confirmed not an issue**: these are short local data-line stubs, not
  power-distribution backbone, and carry negligible current. Left as-is.

## Open items / next steps

1. ~~**Orientation**~~ — resolved, see "LED/cap orientation, silkscreen cleanup, GND stitching"
   above (135°CW odd rows / 45°CCW even rows, caps left-of-LED).
2. ~~**MCU/joystick physical placement**~~ — resolved, see "PCB: MCU / level shifter / joystick
   placement" above. Only the joystick required carving LED-grid space (6 LEDs removed); the MCU's
   placement didn't touch the grid.
3. ~~**Battery polarity**~~ — resolved 2026-08-16, verified against a charger from the battery's own
   vendor. ~~Charge current~~ — resolved, R1=2.49kΩ (~400mA), see above.
4. **USB+battery-simultaneous caution**: decide whether D123 alone is sufficient mitigation or
   whether usage instructions should tell users not to have both connected at once (see Battery
   charging above) — Seeed's own docs are more cautious about this than a single diode implies.
5. ~~**Silkscreen cleanup**~~ — resolved by hiding Reference/Value labels on all LEDs/caps, see
   above.
6. Board center currently placed at KiCad sheet coords (120, 150) — arbitrary, not meaningful.
7. ~~**PCB netlist sync needed**~~ — resolved; board is fully routed, see "Routing complete" above.
8. **PTC/charger thermal sizing** — F1's 1A hold current and R1's 400mA charge target are both sized
   off datasheet worst-case numbers, not measurements; U3 is now tied into the ground plane for
   thermal margin (2026-08-16, the user's mitigation) but real current/temperature under load is
   still unmeasured. Reconfirm once firmware/animations exist and real board current can be checked
   with a meter.
9. ~~**Copper pour/GND vias**~~ — resolved; see #10, the same root cause covered both findings.
10. ~~**GND via overlapping J1's MP pad**~~ — resolved 2026-08-16, was a lost intentional net
    override (J1's `MP` pads → `GND`), not a placement bug. See "Full re-review" in Status above.
    Remember it can get wiped again by a future "Update PCB from Schematic."

## Tooling note

PCB generated with KiCad's own `pcbnew` Python module (via the installed KiCad 10 AppImage) rather
than hand-written `.kicad_pcb` text — footprint loading, duplication, and board-outline shapes all
went through the real API, then verified with `kicad-cli pcb drc`. Script:
`scripts/build_v1_board.py` (run with the AppImage's bundled `python3.11` + `pcbnew.py` on
`PYTHONPATH`).

Schematic has no equivalent Python API (eeschema doesn't expose one the way pcbnew does), so
`scripts/build_v1_schematic.py` generates `.kicad_sch` S-expression text directly — verified with
`kicad-cli sch erc` rather than assumed-correct. Both scripts are kept for re-running once
orientation/MCU-joystick placement is decided. Per [[feedback_kicad_manual_layout]]: this is fine
pre-routing, but once GUI routing/wiring starts on this board, switch to hand-editing the live
`.kicad_pcb`/`.kicad_sch` instead of regenerating from scripts.
