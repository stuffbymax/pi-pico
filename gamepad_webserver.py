# this project is super unresponsive

import network
import uasyncio as asyncio
import usocket as socket

# --- Wi-Fi ---
ssid = 'YOUR NETWORK NAME HERE'
password = 'YOUR NETWORK PASSKEY HERE'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
while not wlan.isconnected():
    pass
print('Connected, IP:', wlan.ifconfig()[0])


# --- Simple WebSocket Handler ---
clients = []

async def websocket_handler(reader, writer):
    clients.append(writer)
    try:
        while True:
            data = await reader.read(100)
            if not data:
                break
            msg = data.decode().strip()
            print("Button:", msg)
    except Exception as e:
        print("WebSocket error:", e)
    finally:
        clients.remove(writer)
        await writer.aclose()


# --- HTTP Server to serve HTML page ---
html = """<!DOCTYPE html>
<html>
<head>
<title>Pi Pico WebSocket Gamepad</title>
<style>
button { width: 80px; height: 80px; font-size: 20px; margin: 5px; }
.grid { display: grid; grid-template-columns: 80px 80px 80px 80px;
       grid-template-rows: 80px 80px 80px; justify-content: center; align-items: center; }
</style>
</head>
<body>
<h1>Virtual Gamepad</h1>
<div class="grid">
  <div></div><button onmousedown="send('UP')" onmouseup="send('UP_RELEASE')">UP</button><div></div><button onmousedown="send('A')" onmouseup="send('A_RELEASE')">A</button>
  <button onmousedown="send('LEFT')" onmouseup="send('LEFT_RELEASE')">LEFT</button><div></div><button onmousedown="send('RIGHT')" onmouseup="send('RIGHT_RELEASE')">RIGHT</button><button onmousedown="send('B')" onmouseup="send('B_RELEASE')">B</button>
  <div></div><button onmousedown="send('DOWN')" onmouseup="send('DOWN_RELEASE')">DOWN</button><div></div><div></div>
</div>

<script>
var ws = new WebSocket('ws://' + location.hostname + ':8765/');
function send(action){ ws.send(action); }
</script>
</body>
</html>"""

async def http_server(reader, writer):
    request = await reader.read(1024)
    response = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + html
    await writer.awrite(response)
    await writer.aclose()


# --- Run servers ---
async def main():
    asyncio.create_task(asyncio.start_server(http_server, "0.0.0.0", 80))
    asyncio.create_task(asyncio.start_server(websocket_handler, "0.0.0.0", 8765))
    while True:
        await asyncio.sleep(1)

asyncio.run(main())
