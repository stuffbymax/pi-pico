from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf
import time
import random

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

TH = bytearray(b'\xe1\xfc\x7f\x0f\xd3\xf8\xfe\x1f\xc7\xf1\xfc?\x80\x7f\xff\xff\xff\xef\xff\xff\xff\xff\xff\xff\xff\xf0\xfe?\x87\xf1\xf3\xf8\xf1\xfc?\x0f\xe3\xf8p\xff\xff\xff\xff\xcf\xff\xff\xff\xff\xff\xff\xff\xf0_\xff\xff\xff\xfe\xff\xff\xff\xff\xff\xff\xff\xf0\xbf\xaf\xdf\xfb\xb9\xe7\xff\xe3\xff\xfe\x1f\xff\xf0\xdf\xfd\xfd\xff\xc7\xff\xf7\xff\xff\xff\xff\xff\xf0\xdb\xff\x7f\xde\xd3\xdf\xfb\xff\xff\xeb\xff\xfd\xf0\xbf\xfb\xaf\xfd\xd97\xff\xff\xfe\xbf\xff\xff\xf0\xbf\xff\xdf\xff\x82\xef\xff\xf7\x97\xfe\xfb\xff\xf0\xd6\xbf\xf5\xfa@#\xbf\xfa\xef\xff\xff\x9fp\xffs\xff\xfd\x83\xec\xfb\xfe\x97\xdf\xfb\xb7\xf0\xff\xbf\xbf\xf1K{\xb6q\xdf\xd7\xff\xff\xf0\xff\xbf\xfb\xf5=\xdc\xd7\'\x1d\xff\xff\xff\xf0\xff\xff\xfb\xc5{\xf7\x80`\x97\x1f\xff\xcf\xe0\xff\xff\xff\xaa\xff\xff\xcb0?\xff\xef\xff\xf0\xff\xee\xff\x97\xff\xf6\x81\xdf\xbf\xf3\xfb\xf7\xf0\xed\xff\xff\x7f\xed\xff!S\xff~\x7f\xff\xe0\xfa\xff\xff\xbf\xfd\xea\x04o\xf7\xff\xff\xff\xf0\xfb\xff\xff\xaf\xbf\xff\x90\x1f\xdd\xdf\xb7\xff\xf0\xbf\xef\xfd\xdf\xff\xdf\xc1\xe3\xff\xef\xff\xff\xf0\xfe\xbf\xf1\x7f\xff\xde\xf9\xef\xdf\xcf\xff\xff\xf0\xff\xff\xffw\xff\xee1\xfb\xff\xff\xff\xfe\xf0\xbe\xff\x9dy\xfb?\x00?\xfd\xfa\xdf\xdc\xf0\xdf5\xeb\xe5\xff\x7f\xf0\xff\xbf\xef\xff\xff\xf0\xff\xf5\xfe\xd7\xd6\xefD=\xff\xff\xf7\xffp\xb5\xff\xac\x81t\x0f\xf0\xdf\xef\xff\xff\xfe\xf0\xff\x7f\xfcA\xf0\x07\xe0\xbf\x02\xf7\xfb\xbf\xf0\xff\xbf\xda\xac\xc7\x07\xa1|\x00\xfe\xff\x7f\xf0\xff\xff\xfa\x9e\xcf#\xb0\xff\xc0\xfe\xff\xfb\xd0\x7f\xf7\xfb\xf2\x8f\x06\xb0\xfa \xf4\x7f\xfd\xd0\xff\xff\xfb\xd1\x8f\x06\xa3\x7f\xe0\x9c\xfb\xff\xf0<\xff~\xf7\x8d\x07I\x7f\xc0\xfd\x7f\xff\xf0\xff\xff\xf4\xfb\xc0\x1f \xff\xe0\xf4\xe7\xff\xf0\xfd\xef\xea\xf9\x805\xed}\xc3~\xef\xff\xf0\xf7\xf7\xf2\xb5q\xf6\xe6?\xcf\xf6\xff~\xd0\xff\xef\xb7\x13{C\xa1\xbf\xff\xf5\xdf\xdd\xf0\xfd\xbf\xf7\xc1\xb4\xc8H\xfeyf\xef\xef\xf0\xfe\xff\xbb\x90\xbeE@\xbf/\xf7\xff\xff\xf0\xff\xfb\xf6Q\x10\x07\xe1~\x7f\x15\xff\xdfp\xdf\xef\xf7\x92\x80\x04\xab\xef\xd0\xf3\xeb\xef\xd0\xbb\xff\xfa\xa2\x00\x0f\xa9\xfe\xa7\xe5\xff\xff\xf0\xff\xe7\xfd\x88\x02\x07\xa7\x7fco\xff\xff\xe0\xff\xbf\xd5`\x04\x00\xd7\xff\x93\xdd\xff\xf5\xf0\xff\xf3\xf8\xf6\x00\r\xed\xef\xab\xdf\xff\xfd\xf0\xfb\xae\xfd@\x00\x0f\xff\xef\xb7\x97\xff\xff\xf0\xff\xfd\xe5\xf2\x00\x0f\xfd\xff\xd7\xdd\xff\xff\xe0\xff\xbe\xfc\xb2\x00\x07\x7f\xfa\x7f\xfe\xf9\xbf\xf0\xefq\x99\xfa\x00\x00\xff\xffJ\xff\xff\xfd\xb0\xbf\xf7\xfe\x18\x00\x08\x1b\xbf\x7f\x7f\xfe\xff\xf0\xef\xe7\xedd8\x00\x03g\\\xff\x9f;\xb0\x7ff\xf7p\x82\x00\x03}\xcd\xff\xef\xbf\xd0\x7fa\xe7\xda$\x00\x01\x8b\xf6\xff\xff\xfd\xf0\x7f;)\xd9\x81\x00b\xd5\xfeg\xdf\xdf\xf0\xff\xf8\xf8i\x81\x83\xff\x7f\xf1\xff\xff\xff\xf0\xff\xfe\x1d\xa5\xc3\xbd\xb5\x7f\xfb\xde\xff\xf7\xf0\xff\xf8\x9c>\x81\xcc\x00\x0f\xbd\xf1\xf7\xfc\xf0\xf3\xf8\xacm\x95\xfa\x00\x03\xec\xff\x7f\xdf\xe0\xff\xfe\xefo\x80\xfc\x00\t\xed\xff\xef\xff\xb0\x7f}\xdfHqVJ\x1b\xee\xff\xbf\xff\xe0~\xf7\xcf\xf6\xff\x82_\xff\xff\xef\xff\xffp?\xff\x7f.0\x00\x05?\xfe\xbf\x7f\xeb\xf0\xfb\xbf\xef\xed\xd6\x88"\xdb\xff\xef\xff\xfd\xf0\xffn\xff\xb7\xc5!\x1e\x7f\xdf\xdd\x7f\xfe\xf0\xfb\x7f\xff\x9e\xfeP&\xff\xfe\xef\xbf\xff\xf0\xff\xef\xff\xfb\xb8\x80I\xd7\xff\xfb\x7f\xff\xf0\xf6\xfd\x7f\xab\xf4\x00\x8f\x9f\xdc\xff\xbf\xdf\xd0?\xef\xff\xfd~ Ce\xdf\xfb\xff\xff\xf07\xff\xfea\xf2\x00\x07\xfb\xff\xf7\xff\xf3\xd0\xef\xff\xff\xe1y\x80\xc0A\xf7\xff\xff\xff\xf0\xff\xfe\xff\xe5\xbf\x00\x06S\xff\xff\xfb\xfa\xb0\xff\xfb\xff\xff\xf4\x00\x93\xbf\xfe\xff\xff\xbf\xf0\xff\xff\xff\xff\xf50\x12\x7f\xff\xff\xff\xff@\xdf\xff\xff\xfa\xf0\xa4\x15\x97\x7f~o\xff\xf0\x7f\xff\xff\xff\xbe@\x1b?\xf7\xbe\xff\xff\xd0\x7f\x7f\xef\xdd\xac\x85\x0b\xfe\xff\xde\xff\xff\xf0\xbf\xef\xfb\xff\xfc\xe0u\xff\xdd\xff\xff\xff\xe0\x9f\xff\xbf\xfb\xf8"\xff\xff\xff\xff\xfd\x7f\xf0\xf7\xff\xff\xf7\xfd^n\xf9\xff7\xdf\xe7\xe0\xff\xef\xdf\xff\xff\x97\xff\xff\xfe\xff\xff\xff\xf0\xff\xff\xef\xff\xff\xff\xfd\xb6\xff\xfd\xff\xff\xf0\xfd\xef\xff\xff\xff\xad\xeb\xff\xb7\xfaw\xff\xb0\xbf\xff\xff\xef\x7f\xff\xff\xff\xfb\x7f\xff\xfe\xf0\xff\xfe\xfd\x7f\x7f\xff\xdf\xdf\xff\xfd\xd7\xfd0\xff\xef\xbf\xff\xffw\xff\xff\xff\xff\xf5\xefp\xe9\x7f\xff\xcf\xff\xfd\xff\xff\xff\xfe\xa7\xfb\xf0\xff\xfe\xf7\xfb\xff\xf9\xfd\xff\xff\xff\xdfs\xf0\xff\x7f\xff\xfb\xfb\xff\xff\x7f\xbf\xfc\xb6\xff\xe0\xdf\xff\xef\xff\xfb\xff\xff\xff\xff\xbf\xfb\xdf\xf0\xf7\xf7\xfd\xff\xfd\x7f\xef\xff\xff\xfc\xf6\xef\xd0\xff\xff\xfe\xdf\xfd\xbf\xff\xff\xff\xff\xaf\xff\xf0\xfd\x9f\xff\xef\xbf\xfe\xfdu\xe7\xff\xdf\xff\xf0\xef\xfd\xff\xff\xf5\x97\xef\xff\xff\xfe\xff\xfd\xb0\x7f_\xfa\xfd\x7f}\xdf\xff\xff\xfe\xf7\xbf\xf0\x9f\xff\xff\xfd\xbf\xaf\xff\xff\xff\xff\xbf\xdf\xf0\xff\x7f\xff\xdf\xff\xbf\xf5\xff\xff\xff\xff\xff\xf0\xff\xff\xff\xff\xff\xff\xff\xff\xbb\xff\xf7\xfdp\xff\xff\xff\xff\xdd\xf6\xff\x7f\xff\xfe\xff\xbf\xe0\xfd\xff\xff\xff\xfc\xff\xff\xdf\xff\xff\xff\xff\xf0\xff\xf7\xff\xfe\xd6\xff\xff\xff\xff\xff\xfa\x8f\xf0')
fb = framebuf.FrameBuffer(TH, 100, 100, framebuf.MONO_HLSB)

# Initial position
x, y = 32, 16
dx, dy = 2, 2  # Step size for smooth movement

while True:
    # Randomly change direction sometimes
    if random.randint(0, 10) > 7:
        dx = random.choice([-2, 2])  # Change horizontal direction
        dy = random.choice([-2, 2])  # Change vertical direction

    # Update position
    x += dx
    y += dy

    # Keep within bounds (bounce effect)
    if x <= 0 or x + 64 >= 128:
        dx = -dx  # Reverse direction if hitting left/right edge
    if y <= 0 or y + 64 >= 64:
        dy = -dy  # Reverse direction if hitting top/bottom edge

    # Clear and redraw
    oled.fill(0)
    oled.blit(fb, x, y)
    oled.show()

    time.sleep(0.05)  # Smooth movement delay
