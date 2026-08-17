"""
V1 ornament board test, using the leds/buttons abstractions.

  1. Light up every LED, so you can see the whole strip is working.
  2. Move a single lit LED around the grid with the joystick. Each
     press moves it one cell; select changes its color.

Pin numbers match the V1 schematic (see hardware/v1-ornament-board/).

Requires the Adafruit CircuitPython NeoPixel library (neopixel.mpy) in
CIRCUITPY/lib/.
"""

import time

import board

from buttons import Joystick
from leds import Leds, ROWS, COLS

leds = Leds(board.D9)  # -> level shifter -> LED chain

joystick = Joystick(
    up_pin=board.D6,
    down_pin=board.D2,
    left_pin=board.D0,
    right_pin=board.D1,
    select_pin=board.D3,
)

COLORS = ((255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0))

# Step 1: light up every LED for a couple seconds, to check the whole chain.
leds.fill((255, 255, 255))
leds.show()
time.sleep(2)
leds.clear()
leds.show()

# Step 2: move a cursor around the grid with the joystick.
row = ROWS // 2
col = COLS // 2
color_index = 0

while True:
    joystick.update()

    if joystick.up.just_pressed and row > 0:
        row -= 1
    if joystick.down.just_pressed and row < ROWS - 1:
        row += 1
    if joystick.left.just_pressed and col > 0:
        col -= 1
    if joystick.right.just_pressed and col < COLS - 1:
        col += 1
    if joystick.select.just_pressed:
        color_index = (color_index + 1) % len(COLORS)

    leds.clear()
    leds.set(row, col, COLORS[color_index])
    leds.show()

    time.sleep(0.02)
