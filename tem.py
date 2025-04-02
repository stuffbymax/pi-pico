from machine import Pin, I2C, PWM
import time
import bmp280
import ssd1306
import neopixel

# Initialize I2C for BMP280 and SSD1306
i2c_bmp280 = I2C(1, sda=Pin(2), scl=Pin(3), freq=400000)
i2c_oled = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

# Initialize BMP280 sensor and OLED display
sensor = bmp280.BMP280(i2c_bmp280)
oled = ssd1306.SSD1306_I2C(128, 64, i2c_oled)

# Initialize NeoPixel (using GPIO 28)
np = neopixel.NeoPixel(Pin(28), 1)  # 1 NeoPixel on GPIO 28

# Initialize Buzzer (PWM on GPIO 15)
buzzer = PWM(Pin(18))
buzzer.freq(1000)  # Set frequency to 1kHz
buzzer.duty_u16(0)  # Start with no sound

# Last time saved, in seconds
last_save_time = time.time()

# Function to save temperature and pressure data with timestamp
def save_temperature_data():
    global last_save_time
    
    # Get the current system time
    current_time = time.localtime()
    year, month, day, _, hours, minutes, seconds, _ = current_time
    date_time_str = f"{year}-{month:02}-{day:02} {hours:02}:{minutes:02}:{seconds:02}"
    
    # Read data from BMP280
    temp = sensor.temperature
    pressure = sensor.pressure
    
    # Save data to a file with timestamp
    with open('sensor_data.txt', 'a') as file:
        file.write(f"{date_time_str} - Temperature: {temp:.2f} C, Pressure: {pressure:.2f} Pa\n")
    
    # Update the last saved time
    last_save_time = time.time()
    print(f"Data saved at {date_time_str} - Temp: {temp:.2f} C, Pressure: {pressure:.2f} Pa")

# Function to update the OLED display
def update_oled():
    current_time = time.localtime()
    year, month, day, _, hours, minutes, seconds, _ = current_time
    date_time_str = f"{year}-{month:02}-{day:02} {hours:02}:{minutes:02}:{seconds:02}"

    temp = sensor.temperature
    pressure = sensor.pressure

    oled.fill(0)
    oled.text(date_time_str, 0, 0)
    oled.text(f'Temp: {temp:.2f} C', 0, 20)
    oled.text(f'Pressure: {pressure:.2f} Pa', 0, 30)
    oled.show()

    control_neopixel(temp)

# Function to control NeoPixel and trigger buzzer based on temperature
def control_neopixel(temp):
    if temp <= 10:
        np[0] = (0, 0, 255)  # Blue
    elif temp <= 20:
        np[0] = (0, 0, 128)  # Light Blue
    elif temp <= 30:
        np[0] = (128, 50, 0)  # Soft Orange
    elif temp <= 40:
        np[0] = (255, 255, 0)  # Yellow
    else:
        np[0] = (255, 0, 0)  # Red
        activate_buzzer()  # Activate buzzer if temp > 40°C
    np.write()

# Function to activate buzzer
def activate_buzzer():
    buzzer.duty_u16(30000)  # Set volume (duty cycle)
    time.sleep(0.51)  # Buzz for 0.5 seconds
    buzzer.duty_u16(0)  # Turn off buzzer

# Main loop
while True:
    update_oled()
    
    if time.time() - last_save_time >= 3600:  # Save data every hour
        save_temperature_data()
    
    time.sleep(1)

