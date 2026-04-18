#include <zephyr/device.h>
#include <zephyr/drivers/uart.h>
#include <zephyr/logging/log.h>

#include "ring_buffer.h"

LOG_MODULE_REGISTER(usb, 3);

static const struct device *cdc_dev;

static void cdc_acm_callback(const struct device *dev,
                             struct uart_event *evt,
                             void *user_data)
{
    switch (evt->type) {

    case UART_RX_RDY:
        rb_write(evt->data.rx.buf, evt->data.rx.len);
        break;

    case UART_RX_DISABLED:
        uart_rx_enable(dev, NULL, 0, SYS_FOREVER_MS);
        break;

    default:
        break;
    }
}

static const struct device *cdc_dev;

void usb_init(void)
{
    cdc_dev = device_get_binding("CDC_ACM_0");

    if (!cdc_dev) {
        LOG_ERR("CDC ACM not found");
        return;
    }

    int ret = uart_callback_set(cdc_dev, cdc_acm_callback, NULL);
    if (ret) {
        LOG_ERR("uart_callback_set failed (%d)", ret);
        return;
    }

    ret = uart_rx_enable(cdc_dev, NULL, 0, SYS_FOREVER_MS);
    if (ret) {
        LOG_ERR("uart_rx_enable failed (%d)", ret);
        return;
    }

    LOG_INF("USB CDC ACM initialized");
}