#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/device.h>
#include <zephyr/drivers/uart.h>
#include <zephyr/drivers/gpio.h>

LOG_MODULE_REGISTER(hello_ei);

#define IMG_W 96
#define IMG_H 96
#define IMG_C 3
#define IMG_SIZE (IMG_W * IMG_H * IMG_C)

#define UART_NODE DT_CHOSEN(zephyr_console)
static const struct device *uart_dev = DEVICE_DT_GET(UART_NODE);

#define LED0_NODE DT_ALIAS(led0)
#define LED1_NODE DT_ALIAS(led1)
#define LED2_NODE DT_ALIAS(led2)
#define LED3_NODE DT_ALIAS(led3)

static const struct gpio_dt_spec leds[] = {
	GPIO_DT_SPEC_GET(LED0_NODE, gpios),
	GPIO_DT_SPEC_GET(LED1_NODE, gpios),
	GPIO_DT_SPEC_GET(LED2_NODE, gpios),
	GPIO_DT_SPEC_GET(LED3_NODE, gpios),
};

static const float thresholds[4] = {0.5f, 0.6f, 0.7f, 0.8f};

static uint8_t image_buffer[IMG_SIZE];

static int get_image_data(size_t offset, size_t length, float *out_ptr)
{
	for (size_t i = 0; i < length; i++) {
		out_ptr[i] = (float)image_buffer[offset + i] / 255.0f;
	}
	return 0;
}

static int uart_read_frame(uint8_t *buf, size_t len)
{
	uint8_t byte;

	while (1) {
		if (uart_poll_in(uart_dev, &byte) == 0 && byte == 0xAA) {
			if (uart_poll_in(uart_dev, &byte) == 0 && byte == 0x55) {
				break;
			}
		}
	}

	size_t idx = 0;

	while (idx < len) {
		if (uart_poll_in(uart_dev, &byte) == 0) {
			buf[idx++] = byte;
		}
	}

	return 0;
}

static void update_leds(float score)
{
	for (size_t i = 0; i < ARRAY_SIZE(leds); i++) {
		gpio_pin_set_dt(&leds[i], score >= thresholds[i]);
	}
}

static void run_inference(void)
{
	ei_impulse_result_t result;

	signal_t signal;
	signal.total_length = IMG_SIZE;
	signal.get_data = get_image_data;

	uint32_t start = k_cycle_get_32();

	EI_IMPULSE_ERROR err = run_classifier(&signal, &result, false);

	uint32_t time_us = k_cyc_to_us_floor32(k_cycle_get_32() - start);

	if (err != EI_IMPULSE_OK) {
		LOG_ERR("Inference failed (%d)", err);
		return;
	}

	LOG_INF("Inference time: %u us", time_us);

	float max_score = 0.0f;
	const char *max_label = nullptr;

	for (size_t i = 0; i < EI_CLASSIFIER_LABEL_COUNT; i++) {
		float val = result.classification[i].value;

		LOG_INF("%s: %.3f", result.classification[i].label, (double)val);

		if (val > max_score) {
			max_score = val;
			max_label = result.classification[i].label;
		}
	}

	LOG_INF("Top result: %s (%.3f)",
		max_label ? max_label : "unknown",
		(double)max_score);

	update_leds(max_score);
}

static int init_peripherals(void)
{
	if (!device_is_ready(uart_dev)) {
		LOG_ERR("UART not ready");
		return -1;
	}

	for (size_t i = 0; i < ARRAY_SIZE(leds); i++) {
		if (!device_is_ready(leds[i].port)) {
			LOG_ERR("LED %d not ready", i);
			return -1;
		}

		gpio_pin_configure_dt(&leds[i], GPIO_OUTPUT_INACTIVE);
	}

	return 0;
}

int main(void)
{
	LOG_INF("Starting FOMO UART inference (FIXED)");

	if (init_peripherals() != 0) {
		return -1;
	}

	while (1) {
		LOG_INF("Waiting for image frame...");

		uart_read_frame(image_buffer, IMG_SIZE);

		run_inference();
	}

	return 0;
}