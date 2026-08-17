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
| PCB | Custom 2-sided in the shape of a Christmas ornament (circle with a tab) with both functional and decorative copper and silkscreen. Initial units will be hand-soldered. Front-side components (LEDs at least) will be assembled by fab for final run. The year should appear somewhere in the design. | What size? I usually aim for 75mm in diameter, but that may feel a little large for something like this.  |
| LED Array | WS2812/NeoPIxel compatible SMT LEDs in a roughly circular grid. Odd parity rows and columns for symmetry. Will need a gap at the bottom for the joystick. Transistor controlled to allow for complete power cutoff in standby. Consider hardware current limiting. | Form factor? Sizes go from 1515 to 5050\. Smaller allows for higher density but harder to solder. Density? Higher looks better but impacts performance and battery life. |
| Microcontroller | CircuitPython compatible. Atmel SAM D21 based. | Form factor (direct-soldered or Xiao/QT py? Individual components are cheaper and more learnable but add significant complexity to both design and assembly. |
| Human Interface | 5-way (UDLR, select) SMT joystick with 3D printed hat for grip | Size? Tradeoff between board space and durability. I strongly prefer a circular board so the joystick will have to take the place of some pixels. |
| Battery | Either li-po with 3D printed casing or 3-4 AAA in holster | Alkaline or li-po? The hardest decision at this time. LiPo offers rechargeability, compactness, higher current, and possibly higher capacity but requires extra circuitry and can be extremely dangerous if not well protected. Alkaline is cheap, safe, and simple but requires the owner to supply batteries and it's not clear how long they would last. |
|  |  |  |
|  |  |  |

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
| With Love (Message) | Scroll "With (heart shape) from Drew, Xmas 2026" | Down |
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