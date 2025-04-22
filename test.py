import urequests
import ssd1306
from machine import Pin, I2C
import network
import time

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('your_SSID', 'your_password')

# Wait for the connection
while not wlan.isconnected():
    time.sleep(1)

# OLED setup
i2c = I2C(0, scl=Pin(15), sda=Pin(14))  # Adjust pins for your setup
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Fetch weather data
API_KEY = "your_api_key"
CITY = "your_city"
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}"

response = urequests.get(URL)
weather_data = response.json()
temp_kelvin = weather_data['main']['temp']
temp_celsius = temp_kelvin - 273.15  # Convert from Kelvin to Celsius

# Display on OLED
oled.fill(0)  # Clear display
oled.text(f"Temp: {temp_celsius:.1f}C", 0, 0)
oled.show()
