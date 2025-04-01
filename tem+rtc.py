from machine import Pin, I2C
import time
import ds3231  # RTC library
import bmp280
import ssd1306

# Initialize I2C for the RTC, BMP280, and OLED
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

# Initialize DS3231 RTC module
rtc = ds3231.DS3231(i2c)

# Initialize BMP280 sensor for temperature and pressure
sensor = bmp280.BMP280(i2c)

# Initialize SSD1306 OLED display
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Last time saved, in seconds
last_save_time = 0

# Function to get current time from RTC
def get_current_time():
    current_time = rtc.datetime()  # Get time as tuple
    year, month, day, _, hours, minutes, seconds, _ = current_time
    timestamp = f"{year}-{month:02}-{day:02} {hours:02}:{minutes:02}:{seconds:02}"
    return timestamp

# Function to save temperature and pressure data with timestamp
def save_temperature_data():
    global last_save_time
    
    # Get the current time from RTC
    timestamp = get_current_time()

    # Read temperature and pressure from BMP280 sensor
    temp = sensor.temperature
    pressure = sensor.pressure

    # Save data to a file (append mode)
    with open('sensor_data.txt', 'a') as file:
        file.write(f"{timestamp} - Temperature: {temp:.2f} C, Pressure: {pressure:.2f} Pa\n")
    
    # Update the last saved time (in seconds)
    last_save_time = time.time()

    print(f"Data saved at {timestamp} - Temp: {temp:.2f} C, Pressure: {pressure:.2f} Pa")

# Function to update the OLED display
def update_oled():
    # Read the latest temperature and pressure
    temp = sensor.temperature
    pressure = sensor.pressure

    # Clear the OLED display
    oled.fill(0)

    # Display the current temperature and pressure on the OLED
    oled.text(f"Temp: {temp:.2f} C", 0, 0)
    oled.text(f"Pressure: {pressure:.2f} Pa", 0, 20)
    
    # Show the updated display
    oled.show()

# Main loop
while True:
    # Check if it's time to save data (every hour)
    if time.time() - last_save_time >= 3600:  # 3600 seconds = 1 hour
        save_temperature_data()  # Save data to file
    
    # Update the OLED display every second
    update_oled()
    
    # Wait for 1 second
    time.sleep(1)
