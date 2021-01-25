from adafruit_magtag.magtag import MagTag
import math
import time
import neopixel
import board
import terminalio

magtag = MagTag()

pixel_pin = board.D10
num_pixels = 30

RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)

pixel_brightness = 0.3

pixels = magtag.peripherals.neopixels
pixels.brightness = pixel_brightness
magtag.peripherals.neopixel_disable = False
pixels = neopixel.NeoPixel(pixel_pin, num_pixels,
                           brightness=pixel_brightness, auto_write=False)

settings = ["brightness", "speed", "mode"]
setting_num = 0

modes = ["rainbow", "off"]
mode_num = 0

wait_time = 0.2

button_pressed = False

rainbow_pos = 0


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)


def clamp(value, low, high):
    if (value <= low):
        return low
    elif (value >= high):
        return high
    return value


def color_chase(color, wait):
    for i in range(num_pixels):
        pixels[i] = color
        time.sleep(wait)
        pixels.show()


def scale(color1, color2, amount):
    amount = clamp(amount, 0, 1)
    pixel_amount = int(num_pixels * amount)
    for i in range(pixel_amount):
        pixels[i] = color1
    for i in range(pixel_amount, num_pixels):
        pixels[i] = color2
    pixels.show()


def rainbow(offset):
    for i in range(num_pixels):
        rc_index = (i * 256 // num_pixels) + offset
        pixels[i] = wheel(rc_index & 255)
    pixels.show()


def rainbow_cycle(wait):
    for j in range(255):
        rainbow(j)
        time.sleep(wait)


magtag.add_text(
    text_font=terminalio.FONT,
    text_position=(magtag.graphics.display.width / 2,
                   magtag.graphics.display.height / 2),
    text_anchor_point=(0.5, 0.5),
    text_color=0x000000,
    line_spacing=0.8
)
magtag.set_text(settings[setting_num])

while 1:

    if (not button_pressed) and magtag.peripherals.any_button_pressed:
        button_pressed = True
        if magtag.peripherals.button_a_pressed:
            setting_num += 1
            setting_num %= len(settings)
            magtag.set_text(settings[setting_num])
        elif magtag.peripherals.button_b_pressed:
            setting_num -= 1
            setting_num %= len(settings)
            magtag.set_text(settings[setting_num])
        elif magtag.peripherals.button_c_pressed:
            setting_mode = settings[setting_num]
            if setting_mode is "brightness":
                pixel_brightness += 0.1
                pixel_brightness = clamp(pixel_brightness, 0.01, 1)
                pixels.brightness = pixel_brightness
                scale(RED, BLUE, pixel_brightness)
            if setting_mode is "speed":
                wait_time -= 0.05
                wait_time = clamp(wait_time, 0, 0.5)
                scale(RED, BLUE, wait_time * 2)
            if setting_mode is "mode":
                mode_num -= 1
                mode_num %= len(modes)
        elif magtag.peripherals.button_d_pressed:
            setting_mode = settings[setting_num]
            if setting_mode is "brightness":
                pixel_brightness -= 0.1
                pixel_brightness = clamp(pixel_brightness, 0.01, 1)
                pixels.brightness = pixel_brightness
                scale(RED, BLUE, pixel_brightness)
            if setting_mode is "speed":
                wait_time += 0.05
                wait_time = clamp(wait_time, 0, 0.5)
                scale(RED, BLUE, wait_time * 2)
            if setting_mode is "mode":
                mode_num += 1
                mode_num %= len(modes)
    elif (not magtag.peripherals.any_button_pressed):
        button_pressed = False

        cur_mode = modes[mode_num]
        if cur_mode is "rainbow":
            rainbow(rainbow_pos)  # Increase the number to slow down the rainbow
            rainbow_pos += 1
            rainbow_pos %= 255
        elif cur_mode is "off":
            pixels.fill((0,0,0))
            pixels.show()

    time.sleep(wait_time)
