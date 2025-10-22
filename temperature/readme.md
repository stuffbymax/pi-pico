# Raspberry Pi Pico Multi-Project Collection

A collection of **three interactive MicroPython projects** for the **Raspberry Pi Pico**, each demonstrating different hardware capabilities — from displaying real-time data on an OLED, to visualizing temperature animations, and creating a temperature-controlled mini-game.  

These projects integrate **sensors**, **OLED graphics**, **NeoPixels**, and **buzzers** for practical and creative demonstrations.

---

## Hardware Components Used

| Component | Description | Typical Pins |
|------------|-------------|---------------|
| **Raspberry Pi Pico** | Microcontroller board (RP2040) | — |
| **SSD1306 OLED (128×64)** | I2C display for visuals | SDA=GP0, SCL=GP1 |
| **BMP280 Sensor** | Temperature and pressure sensor | SDA=GP2, SCL=GP3 |
| **NeoPixel (WS2812)** | RGB LED for visual feedback | GP28 |
| **Piezo Buzzer** | For sound output or alerts | GP18 |

---

## Project 1 — Real-Time Clock Display

### Description  
Displays the **current date and time** on an OLED display in real-time, refreshing every second.

### Features
- Real-time **date and time display**  
- Flexible **SoftI2C pin configuration**  
- Clean and readable **OLED layout**  

---

## Project 2 — Sensor Data Animation + NeoPixel + Buzzer

### Description  
Monitors temperature and pressure using the **BMP280 sensor**, animates icons across the OLED, and provides **visual and audio alerts** via NeoPixel and buzzer.

### Features
- Real-time **temperature & pressure display**  
- Animated **icon movement** on OLED  
- **NeoPixel LED** color changes based on temperature  
- **Buzzer alert** when temperature exceeds threshold  
- Periodic **data logging** to a text file  

### Temperature Ranges & LED Colors
| Temperature (°C) | LED Color | Description |
|------------------|------------|-------------|
| ≤ 10 | 🔵 Blue | Cold |
| 10–20 | 🟦 Light Blue | Cool |
| 20–30 | 🟠 Orange | Normal |
| 30–40 | 🟡 Yellow | Warm |
| > 40 | 🔴 Red + Buzzer | Overheat alert |

### 💡 Behavior Summary
- Animated icons move **left or right** depending on whether temperature is decreasing or increasing  
- NeoPixel changes color according to the temperature range  
- Temperature above **40°C** triggers **red blinking and buzzer sound**  
- Temperature and pressure data are logged every 30 minutes  

---

## Project 3 — Temperature-Controlled Mini Game

### Description  
A playful **mini-game** where the BMP280 sensor controls a character’s movement on the OLED screen.  
The player collects “food” squares to score points, with NeoPixel and buzzer feedback on collection.

###  Gameplay Overview
- 10×10 pixel **character** moves across the screen  
- **Food blocks** appear at random locations  
- **Temperature readings** determine character movement direction and speed  
- **Score tracking** displayed on OLED  
- Game ends if the character moves off-screen  

### Temperature-Based Movement Logic
| Temperature (°C) | Direction | Speed | Description |
|------------------|------------|--------|-------------|
| ≤ 22 | ⬇️ Down | Slow | Cold environment |
| 22–23 | ➡️ Right | Medium | Normal temperature |
| 23–24 | ⬅️ Left | Fast | Warm |
| > 24 | ⬆️ Up | Very Fast | Hot environment |

### Feedback System
| Event | NeoPixel | Buzzer | Effect |
|--------|-----------|---------|--------|
| Food collected | 🟩 Green | ✅ Beep | Positive feedback |
| Game over | ⚫ Off | ❌ Silent | OLED shows "Game Over" |

---

## Summary

| Project | Focus | Hardware Used | Key Feature |
|----------|--------|----------------|-------------|
| **1. OLED Clock** | Display & Timing | SSD1306 | Real-time date/time |
| **2. Sensor Animation** | Sensor I/O + Display | BMP280, OLED, NeoPixel, Buzzer | Animated icon + alerts |
| **3. Temperature Game** | Interactive Gameplay | BMP280, OLED, NeoPixel, Buzzer | Temperature-controlled character & score |

---

## Notes
- All projects are written in **MicroPython**  
- Designed for **Raspberry Pi Pico** hardware  
- NeoPixel and buzzer provide **instant visual and audio feedback**  
- Can be extended or combined for **multi-sensor interactive projects**
