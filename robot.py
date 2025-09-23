"""
Author:     MartinP
Date:       2025-09-23
Purpose:    a pi pico html server for controling robots
Version:    0.1
License:    MIT
"""

import network
import socket
import time
import neopixel
from PicoRobotics import KitronikPicoRobotics

# Initialize robot
board = KitronikPicoRobotics()

# Connect to Wi-Fi
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"Connecting to network '{ssid}'...")
        wlan.connect(ssid, password)

        max_wait = 15  # seconds
        while not wlan.isconnected() and max_wait > 0:
            print(".", end="")
            time.sleep(1)
            max_wait -= 1

        if wlan.isconnected():
            print("\nConnected! Network config:", wlan.ifconfig())
            return wlan
        else:
            print("\nConnection failed.")
            return None
    else:
        print("Already connected. Network config:", wlan.ifconfig())
        return wlan

# Replace with your credentials
ssid = 'test'
password = 'martin12345'

wlan = connect_wifi(ssid, password)

# Set up
num_leds = 12
pin = machine.Pin(0)  # GP0, change if using a different pin
np = neopixel.NeoPixel(pin, num_leds)

# Function to set all LEDs to a color
def set_color(r, g, b):
    for i in range(num_leds):
        np[i] = (r, g, b)
    np.write()

def web_page():
    html = """
<html>
<head>
<title>Pico Controller</title>
<style>
body { font-family: sans-serif; text-align: center; }
button {
  width: 100px; height: 100px; margin: 10px;
  font-size: 20px; border-radius: 20px;
}
.grid {
  display: grid; grid-template-columns: 120px 120px 120px;
  justify-content: center; align-items: center;
}
</style>
<script>
function send(dir) {
  fetch('/action?dir=' + dir);
}
</script>
</head>
<body>
<h2>Pico Control</h2>
<div class="grid">
  <div></div><button onclick="send('forward')">up</button><div></div>
  <button onclick="send('left')">left</button>
  <button onclick="send('stop')">stop</button>
  <button onclick="send('right')">right</button>
  <div></div><button onclick="send('backward')">back</button><div></div>
</div>
</body>
</html>
"""
    return html

# Start socket server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

print("Server started, waiting for connections...")

while True:
    conn, addr = s.accept()
    print('Got connection from', addr)
    request = conn.recv(1024).decode('utf-8')
    print('Request:', request)

    # Parse GET request line
    try:
        first_line = request.split('\n')[0]
        path = first_line.split(' ')[1]
    except IndexError:
        path = '/'

    # Basic parsing for /action?dir=forward style requests
    action = None
    if path.startswith('/action?dir='):
        action = path.split('=')[1].split('&')[0]

    # Control robot based on action
    if action == 'forward':
        board.motorOn(1, "f", 20)
        board.motorOn(2, "f", 20)
        set_color(0, 255, 0)
    elif action == 'backward':
        board.motorOn(1, "r", 20)
        board.motorOn(2, "r", 20)
    elif action == 'left':
        board.motorOn(1, "f", 20)
        board.motorOff(2)
    elif action == 'right':
        board.motorOff(1)
        board.motorOn(2, "f", 20)
    elif action == 'stop':
        board.motorOff(1)
        board.motorOff(2)

    response = web_page()
    conn.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n'.encode('utf-8'))
    conn.send(response.encode('utf-8'))
    conn.close()

