#pragma once
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

void rb_init(void);
int rb_write(const uint8_t *data, size_t len);
int rb_read(uint8_t *out, size_t len);
int rb_available(void);