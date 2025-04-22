from machine import Pin
import time

button1 = Pin(20, Pin.IN, Pin.PULL_UP)
button2 = Pin(21, Pin.IN, Pin.PULL_UP)
button3 = Pin(22, Pin.IN, Pin.PULL_UP)

while True:
    if not button1.value():
        print("Button 1 Pressed!")
    if not button2.value():
        print("Button 2 Pressed!")
    if not button3.value():
        print("Button 3 Pressed!")
    time.sleep(0.1)
