"""
V1 ornament board bring-up test (CircuitPython, Seeed Xiao SAMD21).

On boot: sweeps every LED through red/green/blue/white to confirm the
chain and wiring are good. Then continuously shows which joystick
direction (if any) is currently pressed by lighting the corresponding
half of the board; idle shows a single dim LED at board center.

Pin mapping and LED chain order come from
hardware/v1-ornament-board/design-notes.md / led_chain_order.csv.

Requires the Adafruit CircuitPython NeoPixel library (neopixel.mpy) in
CIRCUITPY/lib/.
"""

import time

import board
import digitalio
import neopixel

from led_positions import LED_X, LED_Y

NUM_LEDS = len(LED_X)

LED_DATA_PIN = board.D9  # -> level shifter -> LED chain

# Software brightness cap. The board's real safety backstop is the
# hardware PTC (F1) on +5V_LED, not this -- but there's no reason to run
# anywhere near its trip point for a bring-up test.
BRIGHTNESS = 40 / 255

pixels = neopixel.NeoPixel(
    LED_DATA_PIN,
    NUM_LEDS,
    brightness=BRIGHTNESS,
    auto_write=False,
    pixel_order=neopixel.GRB,
)


def make_button(pin):
    b = digitalio.DigitalInOut(pin)
    b.direction = digitalio.Direction.INPUT
    b.pull = digitalio.Pull.UP
    return b


joy_up = make_button(board.D6)
joy_down = make_button(board.D2)
joy_left = make_button(board.D0)
joy_right = make_button(board.D1)
joy_select = make_button(board.D3)

CENTER_X = 120.0
CENTER_Y = 148.4  # centroid of LED_X/LED_Y, computed offline


def find_center_index():
    best_i = 0
    best_d = None
    for i in range(NUM_LEDS):
        dx = LED_X[i] - CENTER_X
        dy = LED_Y[i] - CENTER_Y
        d = dx * dx + dy * dy
        if best_d is None or d < best_d:
            best_d = d
            best_i = i
    return best_i


CENTER_INDEX = find_center_index()


def color_test():
    for color in ((255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)):
        pixels.fill(color)
        pixels.show()
        time.sleep(0.5)
    pixels.fill((0, 0, 0))
    pixels.show()
    time.sleep(0.3)


def show_joystick_position():
    up = not joy_up.value
    down = not joy_down.value
    left = not joy_left.value
    right = not joy_right.value
    select = not joy_select.value

    pixels.fill((0, 0, 0))

    if select:
        pixels.fill((0, 255, 255))
        pixels.show()
        return

    if up or down or left or right:
        if up:
            color = (255, 0, 0)
        elif down:
            color = (0, 0, 255)
        elif left:
            color = (0, 255, 0)
        else:
            color = (255, 255, 0)

        for i in range(NUM_LEDS):
            lit = (
                (up and LED_Y[i] < CENTER_Y)
                or (down and LED_Y[i] > CENTER_Y)
                or (left and LED_X[i] < CENTER_X)
                or (right and LED_X[i] > CENTER_X)
            )
            if lit:
                pixels[i] = color
    else:
        pixels[CENTER_INDEX] = (80, 80, 80)

    pixels.show()


color_test()

while True:
    show_joystick_position()
    time.sleep(0.02)
