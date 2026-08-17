"""
Maps the ornament's LEDs to a simple grid, so the rest of the code can say
"light up row 3, column 5" instead of knowing anything about how the LEDs
are wired together in one long chain.

Grid convention: origin (row 0, col 0) is the upper-left. Not every
(row, col) has an LED -- the board is round, not a rectangle, and a few
LEDs near the bottom were removed to make room for the joystick -- so
GRID has holes (None) at the positions with no LED.

This does NOT try to match real-world measurements yet. Row/column
spacing isn't uniform in millimeters; it's just "which LED comes after
which" in a sensible top-to-bottom, left-to-right layout.
"""

import neopixel

NUM_LEDS = 115
ROWS = 13
COLS = 13

# GRID[row][col] = index of that LED in the chain, or None if there's no
# LED there. Generated from hardware/v1-ornament-board/led_chain_order.csv
# (see the project's design notes for how the physical layout came to be).
GRID = (
    (None, None, None, None, None,  112,  113,  114, None, None, None, None, None),
    (None, None, None,  111,  110,  109,  108,  107,  106,  105, None, None, None),
    (None, None,   96,   97,   98,   99,  100,  101,  102,  103,  104, None, None),
    (None,   95,   94,   93,   92,   91,   90,   89,   88,   87,   86,   85, None),
    (None,   74,   75,   76,   77,   78,   79,   80,   81,   82,   83,   84, None),
    (  73,   72,   71,   70,   69,   68,   67,   66,   65,   64,   63,   62,   61),
    (  48,   49,   50,   51,   52,   53,   54,   55,   56,   57,   58,   59,   60),
    (  47,   46,   45,   44,   43,   42,   41,   40,   39,   38,   37,   36,   35),
    (None,   24,   25,   26,   27,   28,   29,   30,   31,   32,   33,   34, None),
    (None,   23,   22,   21,   20,   19,   18,   17,   16,   15,   14,   13, None),
    (None, None,    4,    5,    6,    7,    8,    9,   10,   11,   12, None, None),
    (None, None, None,    3,    2, None, None, None,    1,    0, None, None, None),
    (None, None, None, None, None, None, None, None, None, None, None, None, None),
)


class Leds:
    """Grid-addressable wrapper around the LED chain."""

    def __init__(self, pin, brightness=0.2):
        self._pixels = neopixel.NeoPixel(
            pin, NUM_LEDS, brightness=brightness, auto_write=False
        )

    def set(self, row, col, color):
        """Set the LED at (row, col) to color=(r, g, b). Does nothing if
        there's no LED at that position."""
        index = GRID[row][col]
        if index is not None:
            self._pixels[index] = color

    def fill(self, color):
        """Set every LED to the same color."""
        self._pixels.fill(color)

    def clear(self):
        self.fill((0, 0, 0))

    def show(self):
        """Push the colors set with .set()/.fill() out to the LEDs."""
        self._pixels.show()
