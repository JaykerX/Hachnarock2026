#pragma once
#include <stdbool.h>
#include <stdint.h>

void state_machine_init(void);
void update_state(bool detected);
uint8_t get_danger(void);