# ===============================
# Pico SDOS Terminal with OLED + Keyboard Input
# ===============================
from machine import Pin, SoftI2C
import ssd1306
import utime
import urandom
from machine import reset

# ---------- OLED Setup ----------
i2c = SoftI2C(sda=Pin(0), scl=Pin(1))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# OLED screen buffer
oled_lines = []

def oled_clear():
    global oled_lines
    oled.fill(0)
    oled_lines = []
    oled.show()

def oled_print(line):
    global oled_lines
    # Split long lines for OLED width (~21 chars)
    if len(line) > 21:
        parts = [line[i:i+21] for i in range(0, len(line), 21)]
    else:
        parts = [line]
    for part in parts:
        oled_lines.append(part)
    oled_lines = oled_lines[-8:]  # max 8 lines
    oled.fill(0)
    for i, l in enumerate(oled_lines):
        oled.text(l, 0, i*8)
    oled.show()

# ---------- Boot Sequence ----------
boot_lines = [
    "PICO SDOS TERMINAL",
    "ROM BIOS VERSION 0.2",
    "MEMORY CHECK ... 64KB OK",
    "VIDEO ADAPTER ... OK",
    "KEYBOARD ... OK",
    "STORAGE ... OK",
    "POST COMPLETE",
    "LOADING SDOS SHELL ..."
]

# Show boot sequence
for line in boot_lines:
    oled_print(line)
    utime.sleep(0.5)

# Clear OLED after boot and show initial DOS prompt
oled_clear()
oled_print("C:\\>")  # ready prompt

# ---------- Fake File System ----------
FILES = {
    "C:\\": [("AUTOEXEC.BAT", "2KB"), ("CONFIG.SYS", "1KB"), ("GAMES", "<DIR>")],
    "C:\\GAMES": [("SNAKE.EXE", "12KB"), ("ADVENTURE.EXE", "8KB")]
}
current_dir = ["C:\\"]

# ---------- DOS Commands ----------
def cmd_dir():
    oled_print(f"Directory of {current_dir[0]}")
    for name, size in FILES.get(current_dir[0], []):
        oled_print(f"{name:<15} {size:>6}")

def cmd_help():
    oled_print("Available commands: DIR CLS HELP VER TIME EXIT REBOOT GAMES")

def cmd_ver():
    oled_print("PICO SDOS v0.0.2")

def cmd_time():
    t = utime.localtime()
    oled_print(f"Time: {t[3]:02}:{t[4]:02}:{t[5]:02}")

# ---------- Snake Game ----------
def snake_game():
    width, height = 16, 8
    snake = [[height//2, width//2]]
    food = [urandom.getrandbits(3) % height, urandom.getrandbits(4) % width]
    direction = "RIGHT"
    score = 0

    oled_print("Starting Snake. W/A/S/D to move, Enter to exit.")

    while True:
        # Render screen
        for y in range(height):
            row = ""
            for x in range(width):
                if [y, x] == snake[0]:
                    row += "O"
                elif [y, x] in snake[1:]:
                    row += "o"
                elif [y, x] == food:
                    row += "*"
                else:
                    row += "."
            oled_print(row)
        oled_print(f"Score: {score}")

        try:
            key = input("Move (W/A/S/D Enter=exit): ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            break
        oled_print(f"C:\\>{key}")  # Show input on OLED

        if key == "":
            break
        elif key == "W": direction = "UP"
        elif key == "S": direction = "DOWN"
        elif key == "A": direction = "LEFT"
        elif key == "D": direction = "RIGHT"

        head = snake[0][:]
        if direction == "UP": head[0] -= 1
        if direction == "DOWN": head[0] += 1
        if direction == "LEFT": head[1] -= 1
        if direction == "RIGHT": head[1] += 1

        head[0] %= height
        head[1] %= width

        if head in snake:
            oled_print(f"GAME OVER! Score: {score}")
            break

        snake.insert(0, head)
        if head == food:
            score += 1
            food = [urandom.getrandbits(3) % height, urandom.getrandbits(4) % width]
        else:
            snake.pop()

# ---------- Text Adventure ----------
def text_adventure():
    oled_print("=== MINI TEXT ADVENTURE ===")
    oled_print("Room with door and window")
    try:
        choice = input("Go to (D)oor or (W)indow? ").lower().strip()
    except:
        choice = ""
    oled_print(f"C:\\>{choice}")  # Show input
    if choice == "d":
        oled_print("The door creaks open... freedom!")
    elif choice == "w":
        oled_print("Climb window, fall into bush. Ouch!")
    else:
        oled_print("You stand still. Time passes...")

# ---------- Games Menu ----------
def games_menu():
    while True:
        oled_print("=== GAMES MENU ===")
        oled_print("1. Snake")
        oled_print("2. Text Adventure")
        oled_print("3. Exit to DOS")
        try:
            choice = input("Select 1-3: ").strip()
        except:
            choice = "3"
        oled_print(f"C:\\>{choice}")
        if choice == "1":
            snake_game()
        elif choice == "2":
            text_adventure()
        elif choice == "3":
            oled_print("Returning to DOS...")
            break
        else:
            oled_print("Invalid choice")

# ---------- DOS Shell ----------
def run_sdos():
    while True:
        try:
            cmd = input("C:\\> ").strip().upper()
        except:
            cmd = "EXIT"
        oled_print(f"C:\\>{cmd}")  # mirror input on OLED
        if cmd == "EXIT":
            oled_print("SDOS halted.")
            break
        elif cmd == "REBOOT":
            oled_print("Soft reboot...")
            utime.sleep(1)
            reset()
        elif cmd == "DIR":
            cmd_dir()
        elif cmd == "HELP":
            cmd_help()
        elif cmd == "VER":
            cmd_ver()
        elif cmd == "TIME":
            cmd_time()
        elif cmd == "CLS":
            oled_clear()
            oled_print("C:\\>")  # show prompt after clearing
        elif cmd == "GAMES":
            games_menu()
        else:
            oled_print(f"'{cmd}' not recognized")

# ---------- Main ----------
run_sdos()
