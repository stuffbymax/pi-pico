# Combined Clock, Temperature, Weather, and Snake Game for Raspberry Pi Pico
#
# Merges the local hardware functions of "clockwatch" with the
# internet connectivity of the "weather" script.
# - Connects to your Wi-Fi (Station Mode).
# - A physical button on GP15 cycles through modes.
# - Web interface is accessible on the Pico's IP address on your network.

import network
import time
from machine import Pin, SoftI2C
import ssd1306
from bmp280 import BMP280
import socket
import _thread
import urandom
import urequests
import gc
import sys

# ---------- Configuration ----------
# --- Wi-Fi Credentials ---
WIFI_SSID = "GRAIN_6334"
WIFI_PASSWORD = "B7P48B8Y7P"

# --- OpenWeatherMap API ---
OPENWEATHERMAP_API_KEY = "caa3c5a3121630838545026f24db4c34"
CITY = "Halifax,uk"

# ---------- Network Setup ----------
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"Connecting to network '{ssid}'...")
        wlan.connect(ssid, password)
        max_wait = 20
        while not wlan.isconnected() and max_wait > 0:
            print(".", end="")
            time.sleep(1)
            max_wait -= 1
    if wlan.isconnected():
        print(f"\nConnected! IP: {wlan.ifconfig()[0]}")
        return wlan
    else:
        print("\nConnection failed.")
        return None

wlan = connect_wifi(WIFI_SSID, WIFI_PASSWORD)
PICO_IP = wlan.ifconfig()[0] if wlan else "N/A"


# ---------- Hardware Setup ----------
i2c_bmp = SoftI2C(sda=Pin(26), scl=Pin(27))
bmp = BMP280(i2c_bmp, addr=0x76)
i2c_oled = SoftI2C(sda=Pin(0), scl=Pin(1))
oled = ssd1306.SSD1306_I2C(128, 64, i2c_oled, addr=0x3C)
button = Pin(15, Pin.IN, Pin.PULL_UP)


# ---------- Global Variables & Mode Management ----------
MODES = ["CLOCK", "TEMP", "WEATHER", "SNAKE"]
current_mode_index = 0
mode = MODES[current_mode_index]
button_last_state = button.value()

weather_data = {}
last_weather_fetch = 0
#WEATHER_UPDATE_INTERVAL_MS = 1 * 60 * 1000 # 1 minutes
WEATHER_UPDATE_INTERVAL_MS = 0


# ---------- Weather Function ----------
def get_weather_data():
    global weather_data, last_weather_fetch
    if not wlan or not wlan.isconnected():
        weather_data = {"error": "No Wi-Fi"}
        return

    print("Attempting to fetch weather data...")
    url = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OPENWEATHERMAP_API_KEY}&units=metric'
    response = None

    try:
        response = urequests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            raw_desc = data['weather'][0].get('description', 'N/A')
            weather_desc = raw_desc[0].upper() + raw_desc[1:].lower() if raw_desc else 'N/A'
            
            weather_data = {
                "desc": weather_desc, "temp": data['main'].get('temp'), "city": data.get('name', 'N/A'),
                "feels_like": data['main'].get('feels_like'), "humidity": data['main'].get('humidity'),
                "wind_speed": data['wind'].get('speed') }
            print(f"Weather successfully parsed for {weather_data['city']}.")
        else:
            weather_data = {"error": f"API Err {response.status_code}"}
            print(f"Error: Server returned status code {response.status_code}")

    except Exception as e:
        sys.print_exception(e)
        weather_data = {"error": "Fetch Failed"}
    
    finally:
        if response: response.close()
        last_weather_fetch = time.ticks_ms()
        gc.collect()

# ---------- Snake Game Logic (Original "clockwatch" version) ----------
snake_dir, snake_dir_next = "RIGHT", "RIGHT"
SEG_SIZE = 4
MAX_X, MAX_Y = 128 // SEG_SIZE, 64 // SEG_SIZE
snake, food, score, snake_initialized = [], [], 0, False

def init_snake():
    global snake, food, score, snake_dir, snake_dir_next, snake_initialized
    snake = [[2,2],[1,2],[0,2]]
    food = [urandom.getrandbits(7)%MAX_X, urandom.getrandbits(6)%MAX_Y]
    score, snake_dir, snake_dir_next, snake_initialized = 0, "RIGHT", "RIGHT", True

def draw_snake():
    oled.fill(0)
    for seg in snake:
        x, y = seg
        for dx in range(SEG_SIZE):
            for dy in range(SEG_SIZE): oled.pixel(x*SEG_SIZE+dx, y*SEG_SIZE+dy, 1)
    fx, fy = food
    for dx in range(SEG_SIZE):
        for dy in range(SEG_SIZE): oled.pixel(fx*SEG_SIZE+dx, fy*SEG_SIZE+dy, 1)
    oled.text(f"Score:{score}", 0, 0)
    oled.show()

def move_snake():
    global snake, food, score, snake_dir
    head = snake[0][:]
    snake_dir = snake_dir_next

    if snake_dir == "UP": head[1] -= 1
    elif snake_dir == "DOWN": head[1] += 1
    elif snake_dir == "LEFT": head[0] -= 1
    elif snake_dir == "RIGHT": head[0] += 1

    head[0] %= MAX_X; head[1] %= MAX_Y
    if head in snake: init_snake(); return
    snake.insert(0, head)

    if head == food:
        score += 1
        food = [urandom.getrandbits(7)%MAX_X, urandom.getrandbits(6)%MAX_Y]
    else: snake.pop()

# ---------- Web Server ----------
def web_server():
    global mode, snake_dir_next, snake_initialized, score, current_mode_index
    if not wlan or not wlan.isconnected(): return

    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket(); s.bind(addr); s.listen(1)
    print(f"Web server running at http://{PICO_IP}")

    while True:
        try:
            cl, addr_client = s.accept()
            request = cl.recv(1024).decode('utf-8')

            if "/data" in request:
                response_data = ""
                if mode == "TEMP":
                    response_data = f"Temp: {bmp.temperature:.1f} C<br>Pres: {bmp.pressure:.1f} hPa"
                elif mode == "CLOCK":
                    t = time.localtime()
                    response_data = f"Time: {t[3]:02d}:{t[4]:02d}:{t[5]:02d}<br>Date: {t[0]:04d}-{t[1]:02d}-{t[2]:02d}"
                elif mode == "SNAKE":
                    response_data = f"Score: {score}"
                elif mode == "WEATHER":
                    if "error" in weather_data:
                        response_data = f"Error: {weather_data['error']}"
                    elif "city" in weather_data:
                        response_data = (f"{weather_data['city']}: {weather_data['desc']}<br>"
                                       f"Temp: {weather_data['temp']:.1f}C (Feels {weather_data['feels_like']:.1f}C)<br>"
                                       f"Humidity: {weather_data['humidity']}% | Wind: {weather_data['wind_speed']:.1f} m/s")
                cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n" + response_data); cl.close(); continue
            
            if "/mode=clock" in request: mode = "CLOCK"; current_mode_index = 0
            elif "/mode=temperature" in request: mode = "TEMP"; current_mode_index = 1
            elif "/mode=weather" in request: mode = "WEATHER"; current_mode_index = 2; get_weather_data()
            elif "/mode=snake" in request: mode = "SNAKE"; current_mode_index = 3
            
            if mode == "SNAKE" and not snake_initialized: init_snake()
            
            if "/action?dir=UP" in request and snake_dir != "DOWN": snake_dir_next = "UP"
            elif "/action?dir=DOWN" in request and snake_dir != "UP": snake_dir_next = "DOWN"
            elif "/action?dir=LEFT" in request and snake_dir != "RIGHT": snake_dir_next = "LEFT"
            elif "/action?dir=RIGHT" in request and snake_dir != "LEFT": snake_dir_next = "RIGHT"

            response = f"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n
            <html><head><title>Pico Control</title><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
            <body style="text-align:center;font-family:sans-serif;">
            <h1>Mode: {mode}</h1><p id="data" style="font-size:20px; line-height:1.5;"></p>
            <div style="display:grid; grid-template-columns: auto auto; justify-content:center;">
                <button onclick="window.location='/mode=clock'" style="width:140px;height:70px;margin:10px;">Clock</button>
                <button onclick="window.location='/mode=temperature'" style="width:140px;height:70px;margin:10px;">Temp</button>
                <button onclick="window.location='/mode=weather'" style="width:140px;height:70px;margin:10px;">Weather</button>
                <button onclick="window.location='/mode=snake'" style="width:140px;height:70px;margin:10px;">Snake</button>
            </div>
            <!-- D-PAD CONTROLS -->
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; grid-template-rows: 1fr 1fr 1fr; width: 270px; height: 210px; margin: 20px auto; gap: 5px;">
                <button onclick="fetch('/action?dir=UP')"    style="grid-column: 2; grid-row: 1; font-size: 1.2em;">UP</button>
                <button onclick="fetch('/action?dir=LEFT')"  style="grid-column: 1; grid-row: 2; font-size: 1.2em;">LEFT</button>
                <button onclick="fetch('/action?dir=RIGHT')" style="grid-column: 3; grid-row: 2; font-size: 1.2em;">RIGHT</button>
                <button onclick="fetch('/action?dir=DOWN')"  style="grid-column: 2; grid-row: 3; font-size: 1.2em;">DOWN</button>
            </div>
            <script>
            function updateData() {{ fetch('/data').then(r => r.text()).then(d => {{ document.getElementById('data').innerHTML = d; }}); }}
            setInterval(updateData, 1500); updateData();
            </script>
            </body></html>"""
            cl.send(response); cl.close()
        except Exception as e:
            if 'cl' in locals(): cl.close()

_thread.start_new_thread(web_server, ())

# ---------- Main Loop ----------
while True:
    button_current_state = button.value()
    if button_current_state == 0 and button_last_state == 1:
        current_mode_index = (current_mode_index + 1) % len(MODES)
        mode = MODES[current_mode_index]
        print(f"Mode switched to: {mode}")
        oled.fill(0); oled.text("Mode:", 0, 10); oled.text(mode, 0, 25); oled.show()
        time.sleep(0.5)

        if mode == "SNAKE" and not snake_initialized: init_snake()
        if mode == "WEATHER": get_weather_data()
            
    button_last_state = button_current_state

    if mode == "SNAKE":
        move_snake(); draw_snake()
        # --- SPEED CONTROL: Lower value = less latency & faster snake ---
       # time.sleep(0.04)
        time.sleep(0.1)
    else:
        oled.fill(0)
        if mode == "TEMP":
            oled.text("Temperature", 0, 0)
            oled.text(f"T: {bmp.temperature:.1f} C", 0, 20)
            oled.text(f"P: {bmp.pressure:.1f}hPa", 0, 40)
        elif mode == "CLOCK":
            t = time.localtime()
            oled.text("Clock", 0, 0)
            oled.text(f"{t[2]:02d}-{t[1]:02d}-{t[0]:04d}", 0, 35)  #date format: DD-MM-YYYY
            oled.text(f"{t[3]:02d}:{t[4]:02d}:{t[5]:02d}", 0, 25) # time
        elif mode == "WEATHER":
            oled.text("Weather", 0, 0)
            if "error" in weather_data:
                oled.text("Error:", 0, 25); oled.text(weather_data["error"], 0, 40)
            elif "city" in weather_data:
                oled.text(weather_data["city"], 0, 16)
                oled.text(f"{weather_data['temp']:.1f}C (feels {weather_data['feels_like']:.1f})", 0, 28)
                oled.text(weather_data['desc'], 0, 40)
                oled.text(f"H:{weather_data['humidity']}% W:{weather_data['wind_speed']:.1f}m/s", 0, 52)
            else:
                oled.text("Loading...", 0, 30)
            
            if time.ticks_diff(time.ticks_ms(), last_weather_fetch) > WEATHER_UPDATE_INTERVAL_MS:
                get_weather_data()
        
        oled.show()
        time.sleep(0.2)