"""
PicoOS - Fake OS for Raspberry Pi Pico (MicroPython)
Combines Clock, Temperature, Weather, and Snake game in a small "desktop" UI.
- Uses a tiny home/launcher screen with icons drawn from bytearray bitmaps (FrameBuffer).
- Adds boot animation, window frames and taskbar-like header.
- Keeps web server control from original script.

Adapted from original script provided by the user.
"""

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
import framebuf

# ---------- Configuration ----------
WIFI_SSID = ""
WIFI_PASSWORD = ""
OPENWEATHERMAP_API_KEY = ""
CITY = ""

# ---------- Network Setup ----------
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"Connecting to network '{ssid}'...")
        wlan.connect(ssid, password)
        max_wait = 20
        while not wlan.isconnected() and max_wait > 0:
            print('.', end='')
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

# ---------- Use bytearray for small icon bitmaps ----------
# We'll create small 16x16 icons and draw them using FrameBuffer + blit
# icon data are stored as bytearrays (1 bit per pixel, LSB vertical).

# Helper to create a blank icon buffer
def blank_icon():
    return bytearray(16 * 2)  # 16x16 pixels -> 16*16/8 = 32 bytes. Using 2 bytes per column (legacy placeholder)

# Small example icons (16x16) encoded manually. For clarity we'll create simple shapes.
# Note: framebuf for 16x16 requires 16*16//8 = 32 bytes per icon.
ICON_CLOCK = bytearray([
])
ICON_TMP = bytearray([
])
ICON_WEATHER = bytearray([
])
ICON_SNAKE = bytearray([
])

# Wrap icons in FrameBuffer objects (MONO_VLSB is common on SSD1306 drivers)
fb_clock = framebuf.FrameBuffer(ICON_CLOCK, 16, 16, framebuf.MONO_VLSB)
fb_tmp   = framebuf.FrameBuffer(ICON_TMP,   16, 16, framebuf.MONO_VLSB)
fb_wth   = framebuf.FrameBuffer(ICON_WEATHER,16,16, framebuf.MONO_VLSB)
fb_snake = framebuf.FrameBuffer(ICON_SNAKE, 16, 16, framebuf.MONO_VLSB)

# ---------- Global Variables & Mode Management ----------
MODES = ["HOME", "CLOCK", "TEMP", "WEATHER", "SNAKE"]
current_mode_index = 0
mode = MODES[current_mode_index]
button_last_state = button.value()

weather_data = {}
last_weather_fetch = 0
WEATHER_UPDATE_INTERVAL_MS = 60 * 1000  # 1 minute

# ---------- Weather Function ----------
def get_weather_data():
    global weather_data, last_weather_fetch
    if not wlan or not wlan.isconnected():
        weather_data = {"error": "No Wi-Fi"}
        return

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
        else:
            weather_data = {"error": f"API Err {response.status_code}"}
    except Exception as e:
        sys.print_exception(e)
        weather_data = {"error": "Fetch Failed"}
    finally:
        if response: response.close()
        last_weather_fetch = time.ticks_ms()
        gc.collect()

# ---------- Snake Game Logic ----------
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
    draw_window(mode)
    # shift drawing area down by 10 px to avoid title bar overlap
    for seg in snake:
        x, y = seg
        for dx in range(SEG_SIZE):
            for dy in range(SEG_SIZE): oled.pixel(x*SEG_SIZE+dx, y*SEG_SIZE+dy+10, 1)
    fx, fy = food
    for dx in range(SEG_SIZE):
        for dy in range(SEG_SIZE): oled.pixel(fx*SEG_SIZE+dx, fy*SEG_SIZE+dy+10, 1)
    oled.text(f"Score:{score}", 0, 54)
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
    else:
        snake.pop()

# ---------- Simple UI helpers: boot, window, home ----------

def boot_screen():
    oled.fill(0)
    oled.text("PicoOS v1.0", 16, 12)
    oled.text("Booting...", 24, 30)
    oled.show()
    for i in range(4):
        time.sleep(0.3)
        oled.invert(True); time.sleep(0.05); oled.invert(False)
    time.sleep(0.6)


def draw_window(title):
    # Title bar + border
    oled.rect(0, 0, 128, 64, 1)
    oled.fill_rect(0, 0, 128, 10, 1)
    oled.text(title, 2, 1, 0)


def draw_home(selected=0):
    oled.fill(0)
    oled.text("PicoOS Desktop", 8, 0)
    # Icons
    oled.fill_rect(6, 12, 44, 44, 0)
    oled.blit(fb_clock, 10, 16)
    oled.text("Clock", 12, 34)

    oled.blit(fb_tmp, 46, 16)
    oled.text("Temp", 48, 34)

    oled.blit(fb_wth, 82, 16)
    oled.text("Weather", 80, 34)

    oled.blit(fb_snake, 46, 36)
    oled.text("Snake", 48, 48)

    # small status bar
    oled.text(f"IP:{PICO_IP}", 0, 56)
    oled.show()

# ---------- Web Server (exposes remote control + data) ----------

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

            if "/mode=home" in request: mode = "HOME"; current_mode_index = 0
            elif "/mode=clock" in request: mode = "CLOCK"; current_mode_index = 1
            elif "/mode=temperature" in request: mode = "TEMP"; current_mode_index = 2
            elif "/mode=weather" in request: mode = "WEATHER"; current_mode_index = 3; get_weather_data()
            elif "/mode=snake" in request: mode = "SNAKE"; current_mode_index = 4

            if mode == "SNAKE" and not snake_initialized: init_snake()

            if "/action?dir=UP" in request and snake_dir != "DOWN": snake_dir_next = "UP"
            elif "/action?dir=DOWN" in request and snake_dir != "UP": snake_dir_next = "DOWN"
            elif "/action?dir=LEFT" in request and snake_dir != "RIGHT": snake_dir_next = "LEFT"
            elif "/action?dir=RIGHT" in request and snake_dir != "LEFT": snake_dir_next = "RIGHT"

            response = f"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n
            <html><head><title>PicoOS Control</title><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
            <body style="text-align:center;font-family:sans-serif;">
            <h1>Mode: {mode}</h1><p id="data" style="font-size:20px; line-height:1.5;"></p>
            <div style="display:grid; grid-template-columns: auto auto; justify-content:center;">
                <button onclick="window.location='/mode=clock'" style="width:140px;height:70px;margin:10px;">Clock</button>
                <button onclick="window.location='/mode=temperature'" style="width:140px;height:70px;margin:10px;">Temp</button>
                <button onclick="window.location='/mode=weather'" style="width:140px;height:70px;margin:10px;margin:10px;">Weather</button>
                <button onclick="window.location='/mode=snake'" style="width:140px;height:70px;margin:10px;">Snake</button>
                <button onclick="window.location='/mode=home'" style="width:140px;height:40px;margin:10px;">Home</button>
            </div>
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
boot_screen()

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

    if mode == "HOME":
        draw_home()
        time.sleep(0.3)
    elif mode == "SNAKE":
        move_snake(); draw_snake(); time.sleep(0.08)
    else:
        oled.fill(0)
        draw_window(mode)
        if mode == "TEMP":
            oled.text("T:", 8, 20)
            oled.text(f"{bmp.temperature:.1f}C", 28, 20)
            oled.text(f"P:{bmp.pressure:.1f}h", 8, 36)
        elif mode == "CLOCK":
            t = time.localtime()
            oled.text(f"{t[2]:02d}-{t[1]:02d}-{t[0]:04d}", 8, 22)
            oled.text(f"{t[3]:02d}:{t[4]:02d}:{t[5]:02d}", 8, 34)
        elif mode == "WEATHER":
            oled.text("Weather", 4, 1)  # title is already drawn in draw_window but small redundancy
            if "error" in weather_data:
                oled.text("Error:", 8, 20); oled.text(weather_data["error"], 8, 34)
            elif "city" in weather_data:
                oled.text(weather_data['city'][:12], 8, 20)
                oled.text(f"{weather_data['temp']:.1f}C", 8, 32)
                oled.text(weather_data['desc'][:14], 8, 44)
            else:
                oled.text("Loading...", 8, 28)
            if time.ticks_diff(time.ticks_ms(), last_weather_fetch) > WEATHER_UPDATE_INTERVAL_MS:
                get_weather_data()
        oled.show()
        time.sleep(0.15)

