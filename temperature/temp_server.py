# this code is only for testing Pi pico and it was created by ai by using  my existing code 

from machine import Pin, I2C, PWM
import time
import bmp280
import ssd1306
import neopixel
import framebuf

# Initialize I2C for BMP280 and SSD1306
i2c_bmp280 = I2C(1, sda=Pin(2), scl=Pin(3), freq=400000)
i2c_oled = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

# Initialize BMP280 sensor and OLED display
sensor = bmp280.BMP280(i2c_bmp280)
oled = ssd1306.SSD1306_I2C(128, 64, i2c_oled)

# Initialize NeoPixel (using GPIO 28)
np = neopixel.NeoPixel(Pin(28), 15)  # 1 NeoPixel on GPIO 28

# Initialize Buzzer (PWM on GPIO 18)
buzzer = PWM(Pin(18))
buzzer.freq(1000)  # Set frequency to 1kHz
buzzer.duty_u16(0)  # Start with no sound

# Last time saved, in seconds
last_save_time = time.time()

# --- Image Data ---
TH = bytearray(b'\x00\x00\x00\x00\x0c\x00\x1e\x00\x3f\x00\x3f\x00\x3f\x00\x1e\x00\x0c\x00\x00\x00')
normal_temp_img = framebuf.FrameBuffer(TH, 10, 10, framebuf.MONO_HLSB)

cold_temp_data = bytearray(b'\x00\x00\x04\x20\x02\x40\x01\x80\x01\x80\x02\x40\x04\x20\x00\x00\x00\x00\x00\x00')
cold_temp_img = framebuf.FrameBuffer(cold_temp_data, 10, 10, framebuf.MONO_HLSB)

cool_temp_data = bytearray(b'\x00\x00\x08\x10\x0c\x30\x0e\x70\x0e\x70\x0c\x30\x08\x10\x00\x00\x00\x00\x00\x00')
cool_temp_img = framebuf.FrameBuffer(cool_temp_data, 10, 10, framebuf.MONO_HLSB)

warm_temp_data = bytearray(b'\x00\x00\x00\x00\x1e\x00\x1e\x00\x1e\x00\x1e\x00\x00\x00\x00\x00\x00\x00\x00\x00')
warm_temp_img = framebuf.FrameBuffer(warm_temp_data, 10, 10, framebuf.MONO_HLSB)

hot_temp_data = bytearray(b'\xfc\x00\xfc\x00\xfc\x00\xfc\x00\xfc\x00\xfc\x00\xfc\x00\xfc\x00\xfc\x00\x00\x00\x00\x00')
hot_temp_img = framebuf.FrameBuffer(hot_temp_data, 10, 10, framebuf.MONO_HLSB)
# --- End Image Data ---

# --- Animation Movement Variables ---
animation_x_pos = 128 - 10 - 2  # Initial X position (right side)
animation_y_pos = 64 - 10 - 2  # Y position (bottom side - remains fixed)
animation_direction = -1       # Direction: -1 for left, 1 for right
animation_speed = 1          # Pixels to move per frame
animation_right_boundary = 128 - 10 - 2 # Rightmost X position
animation_left_boundary = 2      # Leftmost X position
previous_temp = 0.0          # Store the previous temperature value
# --- End Animation Movement Variables ---


# Function to save temperature and pressure data with timestamp
def save_temperature_data():
    global last_save_time

    # Get the current system time
    current_time = time.localtime()
    year, month, day, _, hours, minutes, seconds, _ = current_time
    date_time_str = f"{year}-{month:02}-{day:02} {hours:02}:{minutes:02}:{seconds:02}"

    # Read data from BMP280
    temp = sensor.temperature
    pressure = sensor.pressure

    # Save data to a file with timestamp
    with open('sensor_data.txt', 'a') as file:
        file.write(f"{date_time_str} - Temperature: {temp:.2f} C, Pressure: {pressure:.2f} Pa\n")

    # Update the last saved time
    last_save_time = time.time()
    print(f"Data saved at {date_time_str} - Temp: {temp:.2f} C, Pressure: {pressure:.2f} Pa")

# Function to draw temperature animation on OLED using images
def draw_temperature_animation(oled, temp, x_pos, y_pos): # Added x_pos and y_pos parameters
    # Select image based on temperature
    if temp <= 10:
        image = cold_temp_img
    elif temp <= 20:
        image = cool_temp_img
    elif temp <= 30:
        image = normal_temp_img
    elif temp <= 40:
        image = warm_temp_img
    else:
        image = hot_temp_img

    # Clear the animation area (optional, for cleaner animation)
    oled.fill_rect(x_pos, y_pos, 10, 10, 0) # Clear at the current position

    # Draw the selected image at the specified position
    oled.blit(image, x_pos, y_pos)


# Function to update the OLED display
def update_oled():
    global animation_x_pos, animation_direction, previous_temp # Declare globals to modify them

    current_time = time.localtime()
    year, month, day, hours, minutes, seconds, _, _ = time.localtime()

    date_time_str = f"{year}-{month:02}-{day:02} {hours:02}:{minutes:02}:{seconds:02}"
    #print(f"Current time: {date_time_str}")
    temp = sensor.temperature
    pressure = sensor.pressure

    oled.fill(0)
    oled.text(date_time_str, 0, 0)
    oled.text(f'Temp: {temp:.2f} C', 0, 20)
    oled.text(f'Pressure: {pressure:.2f} Pa', 0, 30)

    draw_temperature_animation(oled, temp, animation_x_pos, animation_y_pos) # Pass x and y positions

    oled.show()

    control_neopixel(temp)

    # --- Update Animation Position ---
    # Compare the current temperature with the previous temperature
    if temp > previous_temp:
        animation_direction = 1  # Move right
    elif temp < previous_temp:
        animation_direction = -1  # Move left

    animation_x_pos += animation_direction * animation_speed

    # Check boundaries and reverse direction
    if animation_x_pos <= animation_left_boundary:
        animation_x_pos = animation_left_boundary
        animation_direction = 1 # Move right
    elif animation_x_pos >= animation_right_boundary:
        animation_x_pos = animation_right_boundary
        animation_direction = -1 # Move left

    # Update previous temperature
    previous_temp = temp
    # --- End Update Animation Position ---


# Function to control NeoPixel and trigger buzzer based on temperature
def control_neopixel(temp):
    if temp <= 10:
        np[0] = (0, 0, 255)  # Blue
    elif temp <= 20:
        np[0] = (0, 0, 128)  # Light Blue
    elif temp <= 30:
        np[0] = (128, 50, 0)  # Soft Orange
    elif temp <= 40:
        np[0] = (255, 255, 0)  # Yellow
    else:
        # Blink Red if temp > 40
        for _ in range(5):  # Blink 5 times
            np[0] = (255, 0, 0)  # Red ON
            np.write()  # Update the NeoPixel with the red color
            time.sleep(0.005)  # Stay ON for 0.5s
            np[0] = (0, 0, 0)  # OFF
            np.write()  # Update the NeoPixel to OFF state
            time.sleep(0.0005)  # Stay OFF for 0.5s
        activate_buzzer()  # Activate buzzer if temp > 40°C
        return  # Exit the function once blinking is done to avoid overwriting the color

# Function to activate buzzer
def activate_buzzer():
    buzzer.duty_u16(30000)  # Set volume (duty cycle)
    time.sleep(0.51)  # Buzz for 0.5 seconds
    buzzer.duty_u16(0)  # Turn off buzzer

# Main loop
while True:
    np.write() 
    update_oled()
    if time.time() - last_save_time >= 1800:  # Save data every 30 minutes
        save_temperature_data()

    time.sleep(0.05) # Reduced sleep time for smoother animation (adjust as needed)
