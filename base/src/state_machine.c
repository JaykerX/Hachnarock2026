#include "state_machine.h"
#include "config.h"

static int detect_cnt = 0;
static int miss_cnt = 0;
static uint8_t DANGER = 0;

uint8_t get_danger(void)
{
    return DANGER;
}

void update_state(bool detected)
{
    if (detected) {

        detect_cnt++;
        miss_cnt = 0;

        if (detect_cnt >= DETECT_COUNT_MIN)
            DANGER = 1;

    } else {

        miss_cnt++;
        detect_cnt = 0;

        if (miss_cnt >= DETECT_COUNT_MIN)
            DANGER = 0;
    }
}