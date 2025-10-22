import network
import urequests
import time

# --- Configuration---
WIFI_SSID = ""
WIFI_PASSWORD = "" 
API_KEY = ""
CITY = ""

# --- Connect to Wi-Fi ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print(f"Connecting to '{WIFI_SSID}'...")
wlan.connect(WIFI_SSID, WIFI_PASSWORD)

max_wait = 15
while not wlan.isconnected() and max_wait > 0:
    print(".", end="")
    time.sleep(1)
    max_wait -= 1

if wlan.isconnected():
    print(f"\nConnected! IP: {wlan.ifconfig()[0]}")
    
    # --- Attempt to fetch weather ---
    url = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric'
    print(f"Requesting URL: {url}")
    
    try:
        response = urequests.get(url)
        print("Request successful!")
        print(f"Status Code: {response.status_code}")
        print("Response Text:")
        print(response.text)
        response.close()
    except Exception as e:
        print("\n--- ERROR ---")
        print(f"An error occurred: {e}")
        print("---------------")
else:
    print("\nWi-Fi connection failed. Please check your credentials.")