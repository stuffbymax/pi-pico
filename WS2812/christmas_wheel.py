from machine import Pin
import neopixel
import time

NUM_PIXELS = 13 # number of LED
pin = Pin(0, Pin.OUT)  # GP0 -> DIN
strip = neopixel.NeoPixel(pin, NUM_PIXELS)

# Define Christmas colors
colors = [(255, 0, 0), (0, 255, 0)]  # Red and Green

def christmas_wheel(strip, delay=0.1):
    while True:
        for j in range(NUM_PIXELS):
            for i in range(NUM_PIXELS):
                # Alternate red and green, spinning
                strip[i] = colors[(i + j) % len(colors)]
            strip.write()
            time.sleep(delay)

try:
    christmas_wheel(strip, 0.5)
except KeyboardInterrupt:
    # Turn off LEDs on exit
    for i in range(NUM_PIXELS):
        strip[i] = (0, 0, 0)
    strip.write()

