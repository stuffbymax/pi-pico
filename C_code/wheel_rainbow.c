// just small code for ws2812 wheel 


#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "ws2812.pio.h" // PIO program header from Pico SDK examples

#define PIN 0
#define NUM_LEDS 16

// Convert RGB to GRB 24-bit value
static inline uint32_t rgb_to_grb(uint8_t r, uint8_t g, uint8_t b) {
    return ((uint32_t)g << 16) | ((uint32_t)r << 8) | b;
}

// Generate a color from the wheel (0-255)
uint32_t wheel(uint8_t pos) {
    if(pos < 85) return rgb_to_grb(pos * 3, 255 - pos * 3, 0);
    else if(pos < 170) {
        pos -= 85;
        return rgb_to_grb(255 - pos * 3, 0, pos * 3);
    } else {
        pos -= 170;
        return rgb_to_grb(0, pos * 3, 255 - pos * 3);
    }
}

int main() {
    stdio_init_all();

    PIO pio = pio0;
    int sm = 0;
    uint offset = pio_add_program(pio, &ws2812_program);
    ws2812_program_init(pio, sm, offset, PIN, 800000, false);

    uint32_t pixels[NUM_LEDS];

    while(1) {
        for(int j = 0; j < 256; j++) {
            for(int i = 0; i < NUM_LEDS; i++) {
                pixels[i] = wheel((i + j) & 255);
            }
            // Send pixels to PIO state machine
            for(int i = 0; i < NUM_LEDS; i++) {
                pio_sm_put_blocking(pio, sm, pixels[i] << 8u); // WS2812 needs top 24 bits
            }
            sleep_ms(20);
        }
    }
}
