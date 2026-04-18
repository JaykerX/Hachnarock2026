#include <zephyr/kernel.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/devicetree.h>

#define SW0_NODE DT_ALIAS(sw0)
#define SW1_NODE DT_ALIAS(sw1)
#define SW2_NODE DT_ALIAS(sw2)

static const struct gpio_dt_spec buttons[] = {
    GPIO_DT_SPEC_GET(SW0_NODE, gpios),
    GPIO_DT_SPEC_GET(SW1_NODE, gpios),
    GPIO_DT_SPEC_GET(SW2_NODE, gpios),
};

#define LED_PORT DEVICE_DT_GET(DT_NODELABEL(gpio0))

#define LED0_PIN 0
#define LED1_PIN 1
#define LED2_PIN 2
#define LED3_PIN 3

static const uint8_t led_pins[] = {
    LED0_PIN,
    LED1_PIN,
    LED2_PIN,
    LED3_PIN
};

int main(void)
{
    int ret;

    if (!device_is_ready(LED_PORT)) {
        return -1;
    }

    for (int i = 0; i < 4; i++) {
        gpio_pin_configure(LED_PORT, led_pins[i], GPIO_OUTPUT_HIGH);
    }

    for (int i = 0; i < 3; i++) {
        if (!gpio_is_ready_dt(&buttons[i])) {
            return -1;
        }

        ret = gpio_pin_configure_dt(&buttons[i], GPIO_INPUT | GPIO_PULL_UP);
        if (ret < 0) {
            return -1;
        }
    }

    while (1) {
        int value = 0;
        int b0 = (gpio_pin_get_dt(&buttons[0]) == 1);
        int b1 = (gpio_pin_get_dt(&buttons[1]) == 1);
        int b2 = (gpio_pin_get_dt(&buttons[2]) == 1);

        value = b0 * 1 + b1 * 2 + b2 * 4;

        if (value > 4) {
            value = 4;
        }

        for (int i = 0; i < 4; i++) {
            gpio_pin_set(LED_PORT, led_pins[i], (i < value) ? 1 : 0);
        }

        k_msleep(50);
    }

    return 0;
}