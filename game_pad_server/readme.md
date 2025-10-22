# Raspberry Pi Pico WebSocket Gamepad (MicroPython)

This project turns your Raspberry Pi Pico W into a simple web-based virtual gamepad using WebSockets and uasyncio.
It hosts both an HTML interface (a virtual D-pad and buttons) and a WebSocket server to receive real-time input messages directly from the browser.

> Note: This version feel unresponsive because of how MicroPython handles WebSockets and asynchronous loops — performance depends heavily on network stability and hardware limitations.