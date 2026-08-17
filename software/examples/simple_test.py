"""
V1 ornament board bring-up test (CircuitPython, Seeed Xiao SAMD21).

Standalone learner-friendly version -- no imports from leds.py/buttons.py,
just plain NeoPixel/digitalio calls, so it's simple to read end to end.
For the "real" version built on the grid/button abstractions, see
software/code.py.

Simple test:
  1. Light up every LED, so you can see the whole strip is working.
  2. Then use five LEDs near the middle of the board -- arranged in a
     plus/cross shape -- to show which way the joystick is pointing.

Pin numbers match the V1 schematic (see hardware/v1-ornament-board/).

Requires the Adafruit CircuitPython NeoPixel library (neopixel.mpy) in
CIRCUITPY/lib/.
"""

import time

import board
import digitalio
import neopixel

NUM_LEDS = 115
PIXEL_PIN = board.D9  # -> level shifter -> LED chain

pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_LEDS, brightness=0.2, auto_write=False)

# These five LED numbers were picked (from the board's LED layout) to form
# a plus/cross shape near the middle of the board.
LED_CENTER = 54
LED_UP = 67
LED_DOWN = 41
LED_LEFT = 53
LED_RIGHT = 55

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
OFF = (0, 0, 0)


def make_button(pin):
    button = digitalio.DigitalInOut(pin)
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP
    return button


joy_up = make_button(board.D6)
joy_down = make_button(board.D2)
joy_left = make_button(board.D0)
joy_right = make_button(board.D1)
joy_select = make_button(board.D3)

# Step 1: light up every LED for a couple seconds, to check the whole chain.
pixels.fill(WHITE)
pixels.show()
time.sleep(2)
pixels.fill(OFF)
pixels.show()

# Step 2: show which way the joystick is pointing, using the cross of 5 LEDs.
while True:
    pixels.fill(OFF)

    if not joy_up.value:
        pixels[LED_UP] = RED
    elif not joy_down.value:
        pixels[LED_DOWN] = BLUE
    elif not joy_left.value:
        pixels[LED_LEFT] = GREEN
    elif not joy_right.value:
        pixels[LED_RIGHT] = YELLOW
    elif not joy_select.value:
        pixels[LED_CENTER] = WHITE
    else:
        pixels[LED_CENTER] = (20, 20, 20)  # dim = idle, nothing pressed

    pixels.show()
    time.sleep(0.05)
