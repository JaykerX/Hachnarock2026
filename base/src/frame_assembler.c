#include "frame_assembler.h"
#include "ring_buffer.h"
#include "config.h"
#include <string.h>

static uint8_t frame[IMG_SIZE];

static int filled = 0;

bool frame_get(uint8_t *out_frame)
{
    uint8_t tmp[64];

    while (rb_available() >= 64 && filled < IMG_SIZE) {

        rb_read(tmp, 64);

        for (int i = 0; i < 64 && filled < IMG_SIZE; i++) {
            frame[filled++] = tmp[i];
        }
    }

    if (filled >= IMG_SIZE) {
        memcpy(out_frame, frame, IMG_SIZE);
        filled = 0;
        return true;
    }

    return false;
}