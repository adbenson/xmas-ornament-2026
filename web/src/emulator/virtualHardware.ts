/**
 * The boundary between the emulated CircuitPython program and the browser.
 *
 * Mirrors the raw hardware surface the real board exposes -- an indexed
 * NeoPixel chain and five raw button states -- not the higher-level
 * row/col grid or debounced isPressed()/wasPressed() logic that
 * software/leds.py and software/buttons.py build on top of. Those modules
 * run unmodified against this, same as they would against real hardware.
 *
 * NUM_PIXELS matches NUM_LEDS in software/leds.py.
 */

export type RGB = readonly [number, number, number]

export const NUM_PIXELS = 115

const OFF: RGB = [0, 0, 0]

let pixels: RGB[] = Array.from({ length: NUM_PIXELS }, () => OFF)

export function setPixel(index: number, color: RGB): void {
  if (index < 0 || index >= NUM_PIXELS) return
  pixels[index] = color
}

export function fillPixels(color: RGB): void {
  pixels = pixels.map(() => color)
}

export function getPixels(): readonly RGB[] {
  return pixels
}

export type JoystickButton = 'up' | 'down' | 'left' | 'right' | 'select'

const JOYSTICK_BUTTONS: readonly JoystickButton[] = ['up', 'down', 'left', 'right', 'select']

const joystickState: Record<JoystickButton, boolean> = {
  up: false,
  down: false,
  left: false,
  right: false,
  select: false,
}

export function setJoystickButton(button: JoystickButton, pressed: boolean): void {
  joystickState[button] = pressed
}

export function isJoystickButtonPressed(button: JoystickButton): boolean {
  return joystickState[button]
}

export function getJoystickState(): Readonly<Record<JoystickButton, boolean>> {
  return joystickState
}

export { JOYSTICK_BUTTONS }
