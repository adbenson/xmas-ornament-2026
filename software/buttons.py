"""
Basic debounced button handling, plus a Joystick that groups the
ornament's 5 buttons (up/down/left/right/select) together.
"""

import time

import digitalio


class Button:
    """A single momentary switch wired to a pin with an internal pull-up,
    so the pin reads HIGH when not pressed and LOW when pressed.

    Call .update() once per loop, then read isPressed()/wasPressed().
    """

    DEBOUNCE_SECONDS = 0.02

    def __init__(self, pin):
        self._io = digitalio.DigitalInOut(pin)
        self._io.direction = digitalio.Direction.INPUT
        self._io.pull = digitalio.Pull.UP

        self._pressed = False  # debounced current state
        self._pending_press = False  # set on a press, cleared by wasPressed()

        self._candidate = False
        self._candidate_since = time.monotonic()

    def update(self):
        raw_pressed = not self._io.value
        now = time.monotonic()

        if raw_pressed != self._candidate:
            # The reading changed -- start timing it, to make sure it's a
            # real press/release and not switch bounce.
            self._candidate = raw_pressed
            self._candidate_since = now
            return

        if raw_pressed == self._pressed:
            return  # nothing new to report

        if now - self._candidate_since < self.DEBOUNCE_SECONDS:
            return  # not held long enough yet

        self._pressed = raw_pressed
        if raw_pressed:
            self._pending_press = True

    def isPressed(self):
        """True for as long as the button is currently held down."""
        return self._pressed

    def wasPressed(self):
        """True the first time this is called after a press, then False
        again until the next press (clears on read)."""
        if self._pending_press:
            self._pending_press = False
            return True
        return False


class Joystick:
    """The 5-way joystick: up, down, left, right, select."""

    def __init__(self, up_pin, down_pin, left_pin, right_pin, select_pin):
        self.up = Button(up_pin)
        self.down = Button(down_pin)
        self.left = Button(left_pin)
        self.right = Button(right_pin)
        self.select = Button(select_pin)
        self._buttons = (self.up, self.down, self.left, self.right, self.select)

    def update(self):
        """Call once per loop to refresh every button's state."""
        for button in self._buttons:
            button.update()
