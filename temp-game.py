import time
import bmp280
import ssd1306
from machine import Pin, I2C
import neopixel
import random

# Initialize I2C for BMP280 and SSD1306
i2c_bmp280 = I2C(1, sda=Pin(2), scl=Pin(3), freq=400000)
i2c_oled = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

# Initialize BMP280 sensor and OLED display
sensor = bmp280.BMP280(i2c_bmp280)
oled = ssd1306.SSD1306_I2C(128, 64, i2c_oled)

# Initialize NeoPixel (using GPIO 28)
np = neopixel.NeoPixel(Pin(28), 1)  # 1 NeoPixels on GPIO 28

# Initialize Buzzer (PWM on GPIO 18)
buzzer = Pin(18, Pin.OUT)

# --- Game Variables ---
animation_x_pos = 64  # Initial X position (middle)
animation_y_pos = 32  # Initial Y position (centered vertically)
animation_speed = 1   # Constant speed for all temperatures
animation_direction = 1  # Default direction (moving right initially)
score = 0  # Start with 0 points

food_x_pos = random.randint(0, 118)  # Random x position for food
food_y_pos = random.randint(0, 54)  # Random y position for food
food_size = 10  # Size of the food (same as the character size)

# Function to activate buzzer
def activate_buzzer():
    buzzer.value(1)  # Turn on the buzzer
    time.sleep(0.5)  # Buzz for 0.5 seconds
    buzzer.value(0)  # Turn off the buzzer

# Function to display feedback on NeoPixel
def food_collected_feedback():
    np[0] = (0, 255, 0)  # Change NeoPixel to green for food collection
    np.write()
    time.sleep(0.2)  # Short delay to show feedback
    np[0] = (0, 0, 0)  # Reset NeoPixel color
    np.write()

# Function to handle movement direction based on temperature
def get_direction_and_feedback(temp):
    global animation_speed, animation_direction
    
    # Adjust movement direction and speed based on temperature
    if temp <= 22:  # Cold (move down, slow speed)
        #np[0] = (0, 0, 255)  # Blue for cold
        animation_direction = 2  # Move down
        animation_speed = 1  # Slow
    elif temp <= 23:  # Normal (move right, medium speed)
        #np[0] = (128, 50, 0)  # Orange for normal temperature
        animation_direction = 1  # Move right
        animation_speed = 2  # Medium
    elif temp <= 24:  # Hot (move left, fast speed)
        #np[0] = (255, 255, 0)  # Yellow for hot temperature
        animation_direction = -1  # Move left
        animation_speed = 3  # Fast
    else:  # Very hot (move up, very fast)
        #np[0] = (255, 0, 0)  # Red for very hot
        animation_direction = 0  # Move up
        animation_speed = 4  # Very fast

# Function to update character position and check boundaries
def move_character():
    global animation_x_pos, animation_y_pos, animation_speed

    # Move the character based on direction
    if animation_direction == -1:  # Moving left
        animation_x_pos -= animation_speed
    elif animation_direction == 0:  # Moving up
        animation_y_pos -= animation_speed
    elif animation_direction == 2:  # Moving down
        animation_y_pos += animation_speed
    else:  # Moving right
        animation_x_pos += animation_speed

    # Ensure the character stays within the screen boundaries
    if animation_x_pos < 0:
        animation_x_pos = 0
    elif animation_x_pos > 118:  # 128 - 10 (character width)
        animation_x_pos = 118

    if animation_y_pos < 0:
        animation_y_pos = 0
    elif animation_y_pos > 54:  # 64 - 10 (character height)
        animation_y_pos = 54

# Function to check for food collision
def check_food_collision():
    global score, food_x_pos, food_y_pos

    if (animation_x_pos < food_x_pos + food_size and
        animation_x_pos + 10 > food_x_pos and
        animation_y_pos < food_y_pos + food_size and
        animation_y_pos + 10 > food_y_pos):
        score += 1  # Increase score if food is collected
        food_x_pos = random.randint(0, 118)  # Move food to a new random location
        food_y_pos = random.randint(0, 54)

        # Activate buzzer and feedback
        activate_buzzer()
        food_collected_feedback()

# Main game update function
def update_game():
    global animation_x_pos, animation_y_pos, score, food_x_pos, food_y_pos, animation_speed

    # Read temperature from BMP280 sensor
    temp = sensor.temperature

    # Get movement direction and feedback based on temperature
    get_direction_and_feedback(temp)

    # Move the character and check for boundaries
    move_character()

    # Check if character collides with food (overlaps)
    check_food_collision()

    # Clear the screen
    oled.fill(0)

    # Draw the character (as a simple rectangle for now)
    oled.fill_rect(animation_x_pos, animation_y_pos, 10, 10, 1)

    # Draw the food (as a small rectangle)
    oled.fill_rect(food_x_pos, food_y_pos, food_size, food_size, 1)

    # Display temperature, position, and score on OLED
    oled.text(f'Temp: {temp:.2f}C', 0, 0)  # Show the temperature
    oled.text(f'X: {animation_x_pos} Y: {animation_y_pos}', 0, 10)  # Show position
    oled.text(f'Score: {score}', 0, 20)  # Display score

    oled.show()

    # Simple Game Over condition: if the character goes off the screen
    if animation_x_pos < 0 or animation_x_pos > 118 or animation_y_pos < 0 or animation_y_pos > 54:
        oled.fill(0)
        oled.text('Game Over', 40, 30)
        oled.show()
        time.sleep(2)  # Display Game Over for 2 seconds
        return True  # Game Over
    return False

# Main loop
while True:
    if update_game():  # If game is over, exit the loop
        break
    np.write()  # Update the NeoPixel
    time.sleep(0.1)  # Adjust delay for smoother gameplay
