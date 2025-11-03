# SDOS port for pi pico
# crearor martinP


# ===============================
# Pico SDOS MicroPython Terminal
# ===============================
from machine import Pin, SoftI2C
import ssd1306
import utime
import urandom
import sys

# ---------- OLED Setup ----------
i2c = SoftI2C(sda=Pin(0), scl=Pin(1))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

oled_lines = []

def oled_clear():
    global oled_lines
    oled.fill(0)
    oled_lines = []
    oled.show()

def oled_print(line):
    global oled_lines
    # split long lines into 21-character chunks (fits 128px width)
    if len(line) > 21:
        parts = [line[i:i+21] for i in range(0, len(line), 21)]
    else:
        parts = [line]
    for part in parts:
        oled_lines.append(part)
    oled_lines = oled_lines[-8:]  # keep last 8 lines
    oled.fill(0)
    for i, l in enumerate(oled_lines):
        oled.text(l, 0, i*8)
    oled.show()
    
    

# ---------- Boot Sequence ----------
osBootSequence = [
    "CPU:"
    "RP2350",
    "Type:"
    "ARM",
    "PERSONAL COMPUTER SYSTEM",
    "ROM BIOS VERSION",
    "2.43.07",
    "COPYRIGHT (C)",
    "1987-1996",
    "CC INDUSTRIES",
    "----------------",
    "SYSTEM MEMORY",
    "TESTING ....................",
    "640K OK",
    "EXTENDED MEMORY",
    "CHECK ....................",
    "16384K OK",
    "CACHE MEMORY .............................",
    "ENABLED",
    "KEYBOARD CONTROLLER",
    "......................",
    "OK",
    "FLOPPY DRIVE A:",
    "3.5\" 1.44MB ..............",
    "OK",
    "FLOPPY DRIVE B:",
    "5.25\" 1.2MB",
    "..............",
    "NOT FOUND",
    "HARD DISK 0:",
    "CC 512MB IDE",
    "............ OK",
    "HARD DISK 1:",
    "NOT DETECTED",
    "CD-ROM DRIVE D: ..........................",
    "OK",
    "PARALLEL PORT",
    "LPT1 .......................",
    "OK",
    "SERIAL PORTS",
    "COM1 COM2 ...................",
    "OK",
    "VIDEO ADAPTER:",
    "CC VGA PLUS ...........",
    "OK",
    "VIDEO MEMORY:",
    "1024K DETECTED",
    "MOUSE DEVICE ............................. OK",
    "DMA CONTROLLERS ......................... OK",
    "CMOS BATTERY",
    "STATUS .....................",
    "GOOD",
    "SYSTEM CLOCK ............................",
    "W14.318 MHZ",
    "POST COMPLETE.",
    "NO ERRORS FOUND.",
    "",
    "CC BOOT MANAGER v1.22",
    "SCANNING FOR BOOTABLE DEVICES...",
    " - DRIVE A: NO SYSTEM DISK",
    " - DRIVE C: BOOTABLE PARTITION FOUND",
    "",
    "LOADING CC DOS 5.3 ............",
    "KERNEL INITIALIZATION ............. OK",
    "INSTALLING SYSTEM DRIVERS:",
    "  - HIMEM.SYS ..................... OK",
    "  - EMM386.EXE .................... ENABLED",
    "  - RICNET.SYS .................... LOADED",
    "  - RICSND.SYS .................... OK",
    "  - RICVGA.SYS .................... OK",
    "",
    "MOUNTING FILE SYSTEM ............. OK",
    "CONFIG.SYS PARSING ............... DONE",
    "EXECUTING AUTOEXEC.BAT ...........",
    "PATH=C:\\CC;C:\\CC\\BIN",
    "SET TEMP=C:\\TEMP",
    "",
    "LOADING KERNEL MODULES ........................... PASSED"
    "LOADING SYSTEM"
    "---------------------------"
    "1. Serve the public trust"
    "2. Protect the innocent"
    "3. Uphold the law"
    "4. Any attempt to arrest a senior officer of OCP results"
    "in shutdown (Listed as [Classified] in the initial activation)"
    "---------------------------"
    "CC NETWORK DRIVER INITIALIZED.",
    "CC VGA PLUS DRIVER ACTIVE.",
    "SYSTEM TIME: 07:42:36  TUE 10/14/25",
    "------------------------------------------------------------",
    "CC OPERATING SYSTEM v5.3.12",
    "COPYRIGHT (C) 1987-2025 CC INDUSTRIES",
    "ALL RIGHTS RESERVED.",
    "\n\n",
    "LOADING SDOS SHELL",
    "FOR MICRO PROCESSOR"
]

def oled_animate_dots(line, delay=0.05):
    """Animate dots on OLED if line has '...'"""
    if "..." in line or "...." in line or "................" in line:
        dot_index = line.find(".")
        left = line[:dot_index].rstrip()
        right = line[dot_index:].lstrip()

        dot_count = 0
        for c in right:
            if c == '.':
                dot_count += 1
            else:
                break
        trailing = right[dot_count:].strip()

        # print left part
        oled_print(left + " ")

        # animate dots
        for i in range(dot_count):
            oled_lines[-1] += "."
            oled.fill(0)
            for j, l in enumerate(oled_lines):
                oled.text(l, 0, j*8)
            oled.show()
            utime.sleep(delay)

        # add trailing text
        if trailing:
            oled_lines[-1] += " " + trailing
            oled.fill(0)
            for j, l in enumerate(oled_lines):
                oled.text(l, 0, j*8)
            oled.show()
            utime.sleep(delay)
    else:
        oled_print(line)

def boot_sequence():
    oled_clear()
    for line in osBootSequence:
        oled_animate_dots(line)
        utime.sleep(0.3)
    utime.sleep(0.5)
    oled_clear()  # Clear OLED after boot
    oled_print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    oled_print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    oled_print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    oled_print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    oled_print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    oled_print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    oled_print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    oled_print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    oled_print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    oled_print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    oled_print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    utime.sleep(0.5)
    oled_clear()
    oled_print("wellcome to SDOS")
    oled_print("Pi pico")
    utime.sleep(0.3)
    oled_print("'_'")
    utime.sleep(0.1)
    
    oled_clear()
# ---------- Fake File System ----------
FILES = {
    "C:\\": [
        ("AUTOEXEC.BAT", "2KB"),
        ("CONFIG.SYS", "1KB"),
        ("COMMAND.COM", "38KB"),
        ("GAMES", "<DIR>"),
        ("BIN", "<DIR>")
    ],
    "C:\\GAMES": [
        ("SNAKE.EXE", "12KB"),
        ("ADVENTURE.EXE", "8KB")
    ],
    "C:\\BIN": [
        ("UTIL.EXE", "15KB"),
        ("NETSTAT.EXE", "10KB")
    ],
}
current_dir = ["C:\\"]

# ---------- Commands ----------
def cmd_help():
    oled_print("Available commands:")
    oled_print("DIR")
    oled_print("CLS")
    oled_print("HELP")
    oled_print("VER")
    oled_print("TIME")
    oled_print("EXIT")
    oled_print("CD")
    oled_print("ECHO")
    oled_print("PI")
    oled_print("GAMES")

def cmd_dir():
    oled_print(f"Directory of {current_dir[0]}")
    for name, size in FILES.get(current_dir[0], []):
        oled_print(f"{name:<15} {size:>6}")

def cmd_echo(args):
    oled_print(" ".join(args))

def cmd_ver():
    oled_print("PICO SDOS v0.0.1")

def cmd_time():
    t = utime.localtime()
    oled_print(f"Time {t[3]:02}:{t[4]:02}:{t[5]:02}")

def cmd_pi():
    pi_digits = "3.14159265358979323846264338327950288419716939937510"
    oled_print("Pi:")
    oled_print(pi_digits)

# ---------- Games ----------
def snake_game():
    oled_clear()
    oled_print("Snake Game")
    oled_print("Use UP/DOWN/LEFT/RIGHT keys")
    oled_print("Press 'X' to exit")
    # simplified random snake score simulation
    score = urandom.getrandbits(5) + 1
    utime.sleep(2)
    oled_print(f"Game over! Score: {score}")

def text_adventure():
    oled_clear()
    oled_print("Mini Text Adventure")
    oled_print("Door or Window? (D/W)")
    choice = input("Choice (D/W): ").strip().upper()
    if choice == "D":
        oled_print("You escape through the door!")
    elif choice == "W":
        oled_print("You fall out the window! Ouch!")
    else:
        oled_print("You stand still...")

def cmd_games():
    while True:
        oled_clear()
        oled_print("Games Menu")
        oled_print("1. Snake")
        oled_print("2. Adventure")
        oled_print("3. Exit")
        choice = input("Select (1-3): ").strip()
        if choice == "1":
            snake_game()
        elif choice == "2":
            text_adventure()
        elif choice == "3":
            oled_print("Returning to DOS...")
            utime.sleep(1)
            oled_clear()
            oled_print(f"{current_dir[0]}>")
            break
        else:
            oled_print("Invalid choice")
            utime.sleep(1)

# ---------- DOS Shell ----------
def dos_loop():
    oled_print(f"{current_dir[0]}>")
    while True:
        try:
            cmd_line = input(f"{current_dir[0]}> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        oled_print(f"{current_dir[0]}>{cmd_line}")  # mirror input

        if not cmd_line:
            continue

        parts = cmd_line.split()
        cmd = parts[0].upper()
        args = parts[1:]

        if cmd == "HELP":
            cmd_help()
        elif cmd == "DIR":
            cmd_dir()
        elif cmd == "CLS":
            oled_clear()
            oled_print(f"{current_dir[0]}>")
        elif cmd == "ECHO":
            cmd_echo(args)
        elif cmd == "VER":
            cmd_ver()
        elif cmd == "TIME":
            cmd_time()
        elif cmd == "PI":
            cmd_pi()
        elif cmd == "GAMES":
            cmd_games()
        elif cmd == "CD":
            if not args:
                oled_print(f"Current directory: {current_dir[0]}")
                oled_print("Usage: CD [directory]")
            else:
                target = args[0].upper()
                if len(target) == 2 and target[1] == ":":
                    drive_path = target + "\\"
                    if drive_path in FILES:
                        current_dir[0] = drive_path
                    else:
                        oled_print(f"Drive {target} not found")
                elif target == "\\":
                    current_dir[0] = current_dir[0][0] + ":\\"
                elif target == "..":
                    parts = current_dir[0].rstrip("\\").split("\\")
                    if len(parts) > 1:
                        current_dir[0] = "\\".join(parts[:-1]) + "\\"
                    else:
                        oled_print("Already at root")
                else:
                    new_path = current_dir[0].rstrip("\\") + "\\" + target
                    if new_path in FILES:
                        current_dir[0] = new_path
                    else:
                        oled_print("Path not found")
        elif cmd == "EXIT":
            oled_print("shell halted.")
            break
        elif cmd == "poweroff":
            oled_print("system is turning of")
            utime.sleep(0.2)
            break
        else:
            oled_print(f"'{cmd}' not recognized")

# ---------- Run ----------
if __name__ == "__main__":
    boot_sequence()
    dos_loop()
