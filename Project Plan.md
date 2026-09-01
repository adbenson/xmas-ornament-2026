# XMas Ornaments 2026 project plan

## Overview

### Context

It has become the tradition of the last five years to create customized Christmas ornaments for my immediate family and children of my extended family, approximately 20-25 people with a few spares.

### Concept

A programmable dot-matrix LED Christmas tree ornament. It will be a fun toy when given as a gift but also a learning opportunity \- the ornament can be easily connected to a computer to understand how it works and reprogram it if interested.

### Priorities

1. Safety. These will be for children of every age. Naturally they will not unsupervised toys for the smallest children but larger children should not be able to inadvertently hurt themselves.  
2. Entertainment. Though I'm motivated by the possibility of teaching programming through the ornaments, I accept that most never will and should find them delightful nevertheless.  
3. Education. I want the ornament to be as easy as possible to program and open enough to be somewhat comprehensible to a motivated child.  
4. Simplicity. I have finite time to work on this and limited experience in circuit design.  
5. Cost. I do not expect this to be a major factor but something that must be managed.

### Objectives

1. Safety. A child of 2 should be able to safely interact with the ornament under supervision. A child of 5 should be able to play with it on their own.  
2. Entertainment. The LED array should be dense enough to display basic images, animation, and games. The controls should be intuitive and discoverable. It should be pre-programmed with a variety of fun features, including at least one customizable message, one Christmas-y animation, and one simple game. The battery should last for at least 2 hours of active use and at least one month of standby.  
3. Education. The ornament should be programmable from any computer without specialized software. It should include: detailed instructions on how to learn to program it, helpful software, detailed plans for how it works and how it was built, and abundant resources for learning more.  
4. I should be able to design this in kiCad, iterate on the board design, then once finalized, have it partially assembled by the PCB fab and complete assembly and initial programming myself.  
5. Hard ceiling of $2000, aiming for under $1000. Willing to compromise on cost for simplicity and entertainment value.

## Hardware

### Overview

A custom circular circuit board covered on one side by a grid of addressable RGB LEDs and a small 5-way joystick. The obverse will have a USB-connectable microcontroller, power source, and any other support electronics. 

### Components

Much has been determined but much still remains unknown. Decisions should follow priorities but some may be delayed longer than others. 

| Component | Known | Unknown |
| :---- | :---- | :---- |
| PCB | Custom 2-sided in the shape of a Christmas ornament (circle with a tab) with both functional and decorative copper and silkscreen. Initial units planned for assembly by fab, not hand-soldering (see V0 Findings — biggest unknown, worth validating before committing V1 to it). The year should appear somewhere in the design. Board diameter must be fixed *before* the LED grid is designed, not discovered from it — see V0 Findings. | Final diameter — V0 landed at ~60mm for 36 LEDs after 96mm and sub-50mm both turned out unworkable; final LED count isn't set yet so the real number is still open, but 75mm remains a reasonable ceiling. |
| LED Array | WS2812/NeoPIxel compatible SMT LEDs in a roughly circular grid. Odd parity rows and columns for symmetry. Will need a gap at the bottom for the joystick. Transistor controlled to allow for complete power cutoff in standby. Consider hardware current limiting. Physical layout approach validated in V0 — see V0 Findings for orientation, chain order, and decoupling cap placement. | Form factor/density still open — V0 used 3535, but that exact part went out of stock mid-project and WS2812-compatible LEDs are inconsistently named across vendors, making them hard to search for. Confirm real stock/alternates (or multi-source) before committing V1's package size — sourcing resilience matters more at 20-25 units than it did for one V0 prototype. |
| Microcontroller | CircuitPython compatible. Atmel SAM D21 based. Castellated-edge module (Xiao-style), hand-soldered post-assembly — validated as solderable and buildable in V0. | Xiao vs QT Py SAMD21 — pin/footprint compatible per Adafruit (same 20x17.5mm castellated form factor), so either sources the same design; QT Py uses a smaller-pin-count chip variant (ATSAMD21E18A vs Xiao's G18) but nothing in this project's pin needs exceeds it. Neither is an LCSC/JLCPCB catalog part — a fab-assembled module isn't possible either way, hand-soldering is required regardless of which board is used. |
| Human Interface | 5-way (UDLR, select) SMT joystick with 3D printed hat for grip. A/B/C/D-to-direction wiring is electrically arbitrary — firmware just needs to know which MCU pin is which direction, so hardware routing can pick whatever's most convenient to trace. | Size confirmed as a real tension, not just a theoretical one: the joystick's footprint (ALPS SKRHABE010, ~9x10.4mm) is bigger than a single LED grid slot at V0's tightened pitch, so it needs either multiple vacated LED positions around it or placement outside the LED disc entirely — budget real board space for it up front rather than assuming one pixel's worth of gap is enough. |
| Battery | LiPo. V1 schematic now includes a charge circuit (MCP73832 + support components) and a JST-PH 2.0mm connector — see `hardware/v1-ornament-board/design-notes.md`'s "Battery charging" section for the topology, safety caveats (protected-cell recommendation, JST polarity must be verified per-pack, a Seeed-documented USB+battery-simultaneous caution on the Xiao SAMD21) and open items. Gets its own **permanent, durable cover** (3D printed, not meant to be removed by a kid) separate from the main Case/Enclosure below — since the main case is meant to come off for tinkering/play, the battery still needs to stay physically inaccessible even with the main case off. | Actual cell (capacity/footprint/protected-cell part number) not chosen yet — the charge-current-setting resistor depends on it. Whether the USB+battery-simultaneous caution needs a hardware fix beyond the isolation diode already added, or just usage instructions, is still open. Fastening for the permanent battery cover (glue, ultrasonic weld, screws intended to not be removed, etc.) not chosen. |
| Case/Enclosure | 3D printed, 2-piece (front + back) covering the PCB — added for looks and for safety (priority 1: kids shouldn't be able to touch the board/solder joints directly). Front and back must stay separable/removable (not permanently bonded), so the board is still accessible for tinkering/reprogramming hardware — the user wants kids able to play with this cover off, which is why the battery (see Battery row) needs its own separate *permanent* cover instead of relying on this one. The PCB's existing hanging tab protrudes through the case and remains the actual hanging point — the case doesn't take over hanging duty. | CAD tool not yet chosen — Onshape (parametric, easier for the user to drive, but Claude can't assist directly inside it, so complex/repetitive features like the LED-grid-driven cutout pattern would need dimensions hand-transferred) vs OpenSCAD (Claude can write/iterate the model directly, but harder to get a polished/attractive result). Fastening method for the two removable halves (snap-fit, screws, friction, etc.) not chosen. Cutouts for the joystick, USB port, and JST battery connector not yet dimensioned — need real component/footprint positions from the routed board first. |
|  |  |  |

### V0 Findings (2026-08-14)

V0 was a 36-LED circular test board (`hardware/v0-test-board/`) built to validate the core
electronics before V1. It's being retired without ever being ordered — the LED sourcing problem
below made continuing not worth it — but the design work surfaced real, reusable lessons. Full
detail lives in `hardware/v0-test-board/design-notes.md` and the git history there; this is the
summary worth carrying into V1 planning. `Project Plan.md` as it stood before this update is
preserved as `Project Plan V0.md`.

**Board size must be a fixed input, not an output.** V0's outline started at a sensible size for
a 5x5 LED grid, then just grew to fit whatever the LED grid needed at each subsequent change —
more LEDs, then a circular rearrangement, then a bigger pitch — with nobody ever pulling it back
in. By the time anyone checked, it had drifted to 96x104mm. Fixing it required reworking the LED
pitch and cap placement from scratch. For V1: decide the diameter first, then derive LED
pitch/count to fit inside it.

**LED physical layout** (the part of V0 that's most directly reusable):
- *Orientation*: each LED rotated 90° per row, alternating direction (row 1 CW, row 2 CCW, row 3
  CW, ...). This doesn't affect the electrical pinout, but it aligns the footprint's narrower
  dimension with the tighter row-to-row spacing, which is what makes a tight pitch geometrically
  possible at all — the real footprint courtyard for a 3535 LED is 5.28x3.96mm, not the nominal
  3.5x3.5mm chip size, and that difference is what actually limits how small the board can go.
- *Chain order (zig-zag)*: serpentine/boustrophedon — row 1 left-to-right, row 2 right-to-left,
  row 3 left-to-right, etc. — keeps every consecutive pair of LEDs in the data chain physically
  adjacent, even across rows of different widths in a circular (non-rectangular) pattern.
- *Decoupling caps*: one per LED, placed *beside* it (not above/below) — offset toward whichever
  side its VDD pad rotated to. Beside works better than above/below because it uses the
  footprint's narrower courtyard dimension, the same trick that makes the tight pitch work at all.
- *Start point*: V0's chain starts (LED 1) at the top of the board, opposite where the MCU sits at
  the bottom — meaning the data line has to run all the way across the board before reaching the
  first LED. For V1, with the MCU intentionally placed at the bottom, the LED chain should *start*
  near the MCU instead, to avoid that long trace.
- *Joystick gap*: budget real board space for the joystick, not one LED's worth — see the Human
  Interface row above. In V0 this was one vacated slot at the bottom-center of the LED pattern.

**LED sourcing is the reason V0 is being retired, not the design.** The specific part used
(XINGLIGHT XL-3535RGBC-WS2812B) went out of stock mid-project, and WS2812-compatible LEDs turn out
to be inconsistently named/formatted across vendors, making "find an equivalent" surprisingly
hard. This matters more at V1's 20-25-unit scale than it did for one V0 prototype — worth
confirming real, current stock (and ideally a second compatible source) before locking in a
package size for V1, rather than discovering a shortage after the design is committed.

**MCU module**: Xiao SAMD21 and Adafruit's QT Py SAMD21 are pin/footprint compatible (same
20x17.5mm castellated form factor) — either works as a source for the same design. Neither is an
LCSC/JLCPCB catalog part (they're whole finished sub-boards, not discrete components), so a
fab-assembled MCU isn't possible with either — hand-soldering the module post-assembly is the plan
regardless, and V0 confirmed that's genuinely easy (castellated edges, no fine-pitch soldering).

**Assembly/ordering workflow** (JLCPCB specifically, likely relevant to any similar fab):
- BOM needs a real LCSC part number per line; CPL (placement) needs `kicad-cli`'s raw export
  reformatted to match JLCPCB's actual expected columns (`Designator,Mid X,Mid Y,Layer,Rotation`,
  coordinates with an `mm` suffix, rotation normalized to [0,360)) — their uploader rejects
  `kicad-cli`'s native format outright. See `hardware/v0-test-board/kicad/jlcpcb/convert_cpl.py`.
- Package size codes are a real trap: "0603" means two different physical sizes depending on
  imperial vs. metric convention (imperial 0603 = metric 1608 = 1.6x0.8mm; metric 0603 = imperial
  0201 = 0.6x0.3mm), and some distributor listings bury which one they mean in a parenthetical.
  Always confirm against the footprint's actual metric-equivalent name, not just the bare "0603."
- Double-sided assembly costs a flat ~$25 extra (setup fee doubles $25→$50) regardless of how many
  parts are on the back — not worth it for a small handful of parts on a small prototype run;
  cheaper to hand-solder those too.
- Fabrication (bare board) pricing depends only on board dimensions/layers/quantity; assembly
  pricing depends on part count/BOM complexity. Neither is affected by unrouted traces or
  component placement collisions — both are gettable for a real quote before a design is finished,
  though a real *order* submission will get rejected/flagged for those later.

##### 

## Software

### Overview

The ornament should be able to show a personalized Christmas greeting, a number of festive animations, and at least one game. It should balance power conservation with entertainment. Timing and control scheme are provisional. Any input can override the current mode, not including interactive modes.

### Mode Types

1. Standby. Lowest-power state. All LEDs dark, cut power to LED array, CPU in lowest power mode. Wake on any button press.  
2. Message. Scrolls text R-L with color effect. Returns to standby immediately on completion  
3. Animation. Displays a colorful "moving" image for 2 minutes at high brightness. Can be "locked in" by holding down select for 2 seconds. When locked in, continue to show at low brightness until the battery dies. Locked in can be interrupted by any other input.  
4. Interactive. Responds to joystick inputs until complete or Select is held for 2 seconds.

### Modes

| Mode | Description | Trigger |
| :---- | :---- | :---- |
| Greeting (Message) | Scroll "Merry Christmas, {recipient}\!" | Select |
| With Love (Message) | Scroll "With (heart shape) from the user, Xmas 2026" | Down |
| Snowflake (Animation) | Animation: 3D Spinning-effect snowflake animation. | Left |
| Tree (Animation) | Animation: Green tree with sparkling multi-color lights on the branches and white snowflakes falling | Right |
| Star (Animation) | Animation: Rotating 6-pointed yellow star with alternate long and short legs | Up |
| Snake (Interactive) | Classic snake game using joystick, lots of colorful effects. On "death", show score screen for 3 seconds then return to standby | UDLR |
| Easter Egg (interactive) | TBD | UDUDLRLRS |

## Extra Resources & Packaging

### Packaging

Folded cardboard box. Includes a very brief note on how to access the drive for programming

### Resources

Preferably delivered entirely on the CircuitPython drive. If space is insufficient, provide either flash drive or URL for more.

* code.py  
* README.txt \- very brief introduction to the contents of the drive  
* Getting Started.html  
  * More detailed instructions on programming  
  * Guide to drive contents  
  * Links:  
    * github source  
    * CircuitPython getting started  
    * Intro to Python  
    * Mu editor  
    * NeoPixel getting started  
    * KiCad  
* Software folder  
  * Mu installer for Windows and Mac  
  * read-only backup copy of [code.py](http://code.py)  
  * other example programs?  
* Hardware folder  
  * PDFs of PCB schematic and board layout  
  * kicad project files