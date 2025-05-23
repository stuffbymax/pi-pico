from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf
import time
import random

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

TH = bytearray(b'\xff\xff\xff\xf7\xff\xff\xff\xf0\xff\xff\xff\xef\xff\xff\xff\xf0\xff\xff\xff\xfb\xff\xff\xff\xf0\xff\xff\xff\xfb\xff\xff\xff\xf0\xff\xff\xff\xfb\xff\xff\xff\xf0\xff\xff\xff\xfd\xff\xff\xff\xf0\xff\xff\xff\xe1\xff\xff\xff\xf0\xff\xff\xff\xf1\xff\xff\xff\xf0\xff\xff\xff\xb1\xff\xff\xff\xf0\xff\xff\xff\xf0\xbf\xff\xff\xf0\xff\xff\xff\xf0\xbf\xff\xff\xf0\xff\xff\xff\xf9\xff\xff\xff\xf0\xff\xff\xff\xf9\xff\xff\xff\xf0\xff\xff\xff\xf9\xff\xff\xff\xf0\xff\xff\xff\xf9\xff\xff\xff\xf0\xff\xff\xff\xf9\xff\xff\xff\xf0\xff\xff\xff\xf9\xff\xff\xff\xf0\xff\xff\xff\xf8\xff\xff\xff\xf0\xff\xff\xff\xd8\xbf\xff\xff\xf0\xff\xff\xff\xf4\x7f\xff\xff\xf0\xff\xff\xff\xf5\x7f\xff\xff\xf0\xff\xff\xff\xe4\xff\xff\xff\xf0\xff\xff\xfd0\xff\xff\xff\xf0\xff\xfd\xfe\xf4\xfb\xff\xff\xf0\xff\xf7\xfc\xf0\x8f\xff\xff\xf0\xff\xff\xe0\xb8\x87\xff\xff\xf0\xff\xfc\x048a\xff\xff\xf0\xff\xfc\x04\x99e\xff\xff\xf0\xff\xf8\x04H\x82\x7f\xff\xf0\xff\xf9\x1c:\xe2\xff\xff\xf0\xff\xf8<H\xa1\x1f\xff\xf0\xff\xec<I\xa4\x1f\xff\xf0\xff\xf4|\xc8\xba\x1f\xff\xf0\xff\xf6|x\x90\x1f\xff\xf0\xff\xfe\xfc\t\xd1\x8f\xff\xf0\xff\xfex8\xf0O\xff\xf0\xff\xf6\xf8x \xd7\xff\xf0\xff\xfeq\xf0 C\xff\xf0\xff\xfe`!\x01a\xff\xf0\xff\xfeh\'fA\xff\xf0\xff\xfe"8\x11G\xff\xf0\xff\xfc\x10\x11\x00\x01\xff\xf0\xff\xfdPP\x02@\xff\xf0\xff\xfc\x10\x80\xa8\xc0\xff\xf0\xff\xfc\xdd0\xe6@\xff\xf0\xff\xf4\x9e\x98a\x81\xff\xf0\xff\xfe\x1ex\xc7G\xff\xf0\xff\xffN<\xde\x0f\xff\xf0\xff\xff\x86x\x86\xff\xff\xf0\xff\xfe\xc3(\x0c\x7f\xff\xf0\xff\xff\xe1\x13\x10\x7f\xff\xf0\xff\xff`P\x90\xff\xff\xf0\xff\xff\xb4\x04\x88\xff\xff\xf0\xff\xff\xf6p\x02\xff\xff\xf0\xff\xff\xf0F\x03\xff\xff\xf0\xff\xff\xff\x12O\xff\xff\xf0\xff\xff\xf7\xb0\x9f\xff\xff\xf0\xff\xff\xff\xffw\xff\xff\xf0\xff\xff\xff\xff\xff\xff\xff\xf0\xff\xff\xff\xf6\xff\xff\xff\xf0')
fb = framebuf.FrameBuffer(TH, 60, 60, framebuf.MONO_HLSB)

# Initial position & direction
x, y = random.randint(0, 68), random.randint(0, 4)  # Random start
dx, dy = 2, 2  

while True:
    # Change direction randomly
    if random.random() < 0.2:  # 20% chance to change direction
        dx, dy = random.choice([(2, 2), (-2, 2), (2, -2), (-2, -2)])

    # Update position
    x += dx
    y += dy

    # Check boundaries (bounce)
    if x <= 0 or x + 60 >= 128:
        dx = -dx  # Reverse X direction
    if y <= 0 or y + 60 >= 64:
        dy = -dy  # Reverse Y direction

    # Clear screen and redraw
    oled.fill(0)
    oled.blit(fb, x, y)
    oled.show()

    time.sleep(0.05)  # Delay for smooth animation5
