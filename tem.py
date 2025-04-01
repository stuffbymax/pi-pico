from machine import Pin, I2C
import time
import bmp280
import ssd1306
import neopixel

# Initialize I2C for BMP280 and SSD1306
i2c_bmp280 = I2C(1, sda=Pin(2), scl=Pin(3), freq=400000)
i2c_oled = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

# Initialize BMP280 sensor and OLED d5isplay
sensor = bmp280.BMP280(i2c_bmp280)
oled = ssd1306.SSD1306_I2C(128, 64, i2c_oled)

# Initialize NeoPixel (using GPIO 28)
np = neopixel.NeoPixel(Pin(28), 1)  # 1 NeoPixel on GPIO 28

# Last time saved, in seconds
last_save_time = time.time()

# Function to save temperature and pressure data with timestamp
def save_temperature_data():
    global last_save_time
    
    # Get the current system time
    current_time = time.localtime()  # Returns a tuple (year, month, day, weekday, hours, minutes, seconds, subseconds)
    
    # Format the date and time in a single string
    year, month, day, _, hours, minutes, seconds, _ = current_time
    date_time_str = f"{year}-{month:02}-{day:02} {hours:02}:{minutes:02}:{seconds:02}"
    
    # Read data from BMP280
    temp = sensor.temperature
    pressure = sensor.pressure
    
    # Save data to a file with timestamp
    with open('sensor_data.txt', 'a') as file:
        file.write(f"{date_time_str} - Temperature: {temp:.2f} C, Pressure: {pressure:.2f} Pa\n")
    
    # Update the last saved time (in seconds)
    last_save_time = time.time()

    print(f"Data saved at {date_time_str} - Temp: {temp:.2f} C, Pressure: {pressure:.2f} Pa")

# Function to update the OLED display
def update_oled():
    # Get the current system time
    current_time = time.localtime()
    year, month, day, _, hours, minutes, seconds, _ = current_time
    date_time_str = f"{year}-{month:02}-{day:02} {hours:02}:{minutes:02}:{seconds:02}"

    # Read data from BMP280
    temp = sensor.temperature
    pressure = sensor.pressure

    # Clear the OLED display
    oled.fill(0)

    # Display the date and time on one line
    oled.text(date_time_str, 0, 0)  # Date and time on first line
    
    # Display the sensor data on the following lines
    oled.text(f'Temp: {temp:.2f} C', 0, 20)  # Temperature in one line
    oled.text(f'Pressure: {pressure:.2f} Pa', 0, 30)  # Pressure in one line
    
    # Update the OLED display
    oled.show()

    # Control the NeoPijumpxel based on temperature
    control_neopixel(temp)

# Function to control NeoPixel based on temperature
def control_neopixel(temp):
    if temp <= 10:  # Super Cold 
        np[0] = (0, 0, 255)  # Blue
    elif temp <= 20:  # Cold
        np[0] = (0, 0, 128)  # Light Blue
    elif temp <= 30:  # Normal
        np[0] = (128, 50, 0)  # Softer Orange
    elif temp <= 40:  # Hot
        np[0] = (255, 255, 0)  # Yellow
    else: # super hot
        np[0] = (255, 0, 0)  # Red

    # Update the NeoPixel
    np.write()

# Main loop
while True:
    # Update the OLED display every second
    update_oled()
    
    # Check if it's time to save data (every hour)
    if time.time() - last_save_time >= 3600:  # 3600 seconds = 1 hour
        save_temperature_data()  # Save data to file
    
    # Sleep for 1 second to update the display
    time.sleep(1)
