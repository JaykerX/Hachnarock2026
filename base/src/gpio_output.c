#include "gpio_output.h"
#include "state_machine.h"

#include <zephyr/drivers/gpio.h>
#include <zephyr/kernel.h>

#define LED DT_ALIAS(led0)

static const struct gpio_dt_spec led = GPIO_DT_SPEC_GET(LED, gpios);

void gpio_thread(void)
{
    gpio_pin_configure_dt(&led, GPIO_OUTPUT);

    while (1) {
        gpio_pin_set_dt(&led, get_danger());
        k_msleep(20);
    }
}

K_THREAD_DEFINE(gpio_t, 1024, gpio_thread, NULL, NULL, NULL, 2, 0, 0);