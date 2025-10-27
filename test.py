from machine import Pin, SoftI2C
import ssd1306
import time

# Software I2C (works on any pins)
i2c = SoftI2C(sda=Pin(0), scl=Pin(1), freq=400000)

oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

while True:
    # Clear the display
    oled.fill(0)
    
    # Get current time
    t = time.localtime()  # returns (year, month, day, hour, minute, second, weekday, yearday)
    hours = t[3]
    minutes = t[4]
    seconds = t[5]
    
    # Format time as HH:MM:SS
    current_time = "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
    date = "{:04d}-{:02d}-{:02d}".format(t[0], t[1], t[2])
    
    # Display time on OLED
    oled.text("Date and Time:", 0, 2)
    oled.text(current_time, 6, 30)
    oled.text(date, 5, 17)
    oled.show()
    
    time.sleep(1)
