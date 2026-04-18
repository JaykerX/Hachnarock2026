#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>

#include "usb_dma.h"
#include "frame_assembler.h"
#include "yolo.h"
#include "state_machine.h"
#include "config.h"

LOG_MODULE_REGISTER(main, 3);

static uint8_t frame[IMG_SIZE];

void inference_thread(void)
{
    while (1) {

        if (frame_get(frame)) {

            bool detected = yolo_detect(frame);

            update_state(detected);
        }

        k_msleep(5);
    }
}

K_THREAD_DEFINE(inf, 4096,
                inference_thread,
                NULL, NULL, NULL,
                1, 0, 0);

void main(void)
{
    LOG_INF("System init");

    usb_init();

    while (1) {
        k_msleep(1000);
    }
}