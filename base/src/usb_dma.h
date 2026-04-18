#pragma once
#include <stdint.h>
#include <stddef.h>

void usb_init(void);
void usb_rx_callback(const uint8_t *data, size_t len);