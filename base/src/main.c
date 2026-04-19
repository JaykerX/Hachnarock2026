#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/uart.h>
#include <stdlib.h>

#define LED_PORT DEVICE_DT_GET(DT_NODELABEL(gpio0))

#define P0_00 0
#define P0_01 1
#define P0_02 2
#define P0_03 3
#define P0_04 4
#define P0_05 5

static const uint8_t out_pins[] = {
    P0_00, P0_01, P0_02, P0_03
};

#define T0 0.3f
#define T1 0.4f
#define T2 0.7f
#define T3 0.8f

#define MIN_TRESHOLD_FRAMES 8

const struct device *uart = DEVICE_DT_GET(DT_CHOSEN(zephyr_console));

#define BUF_SIZE 32
static char rx_buf[BUF_SIZE];
static int rx_pos = 0;

static int above_t1_count = 0;
static int below_t1_count = 0;
static int found = 0;
static int prev_found = 0;

static void uart_send(const char *s)
{
    while (*s) {
        uart_poll_out(uart, *s++);
    }
}

void process_value(float v)
{
    int out = 0;

    if (v > T0) out |= (1 << 0);
    if (v > T1) out |= (1 << 1);
    if (v > T2) out |= (1 << 2);
    if (v > T3) out |= (1 << 3);

    for (int i = 0; i < 4; i++) {
        gpio_pin_set(LED_PORT, out_pins[i], (out >> i) & 1);
    }

    if (v > T1) {
        above_t1_count++;
        below_t1_count = 0;

        if (above_t1_count >= MIN_TRESHOLD_FRAMES) {
            found = 1;
        }
    } else {
        above_t1_count = 0;
        below_t1_count++;

        if (below_t1_count >= MIN_TRESHOLD_FRAMES * 4) {
            found = 0;
        }
    }

    if (found && !prev_found) {
        uart_send("DANGER\n");
    }

    prev_found = found;

    gpio_pin_set(LED_PORT, P0_04, found);
    gpio_pin_set(LED_PORT, P0_05, found);
}

int main(void)
{
    if (!device_is_ready(LED_PORT) || !device_is_ready(uart)) {
        return -1;
    }

    for (int i = 0; i < 4; i++) {
        gpio_pin_configure(LED_PORT, out_pins[i], GPIO_OUTPUT_LOW);
    }

    gpio_pin_configure(LED_PORT, P0_04, GPIO_OUTPUT_LOW);
    gpio_pin_configure(LED_PORT, P0_05, GPIO_OUTPUT_LOW);

    while (1) {
        uint8_t c;

        if (uart_poll_in(uart, &c) == 0) {

            if (c == '\n' || c == '\r') {
                rx_buf[rx_pos] = '\0';

                float val = strtof(rx_buf, NULL);

                if (val < 0.0f) val = 0.0f;
                if (val > 1.0f) val = 1.0f;

                process_value(val);

                rx_pos = 0;
            }
            else if (rx_pos < BUF_SIZE - 1) {
                rx_buf[rx_pos++] = c;
            }
        }

        k_msleep(1);
    }
}