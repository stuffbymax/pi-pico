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

# make wifi host
def start_access_point(ssid="PicoRobot", password="pico1234"):
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password)
    ap.active(True)

    # Optional: set static IP
    ap.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.1', '8.8.8.8'))

    print(f"Access Point '{ssid}' started.")
    print("IP address:", ap.ifconfig()[0])

    # Wait until active
    while not ap.active():
        time.sleep(1)
    print("AP is active!")
    return ap

# Start AP instead of connecting to Wi-Fi
ap = start_access_point()
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

