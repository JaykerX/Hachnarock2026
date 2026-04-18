#include "ring_buffer.h"
#include "config.h"

static uint8_t buffer[RING_BUFFER_SIZE];

static volatile int head = 0;
static volatile int tail = 0;

void rb_init(void)
{
    head = tail = 0;
}

int rb_write(const uint8_t *data, size_t len)
{
    for (int i = 0; i < len; i++) {

        int next = (head + 1) % RING_BUFFER_SIZE;

        if (next == tail) return i;

        buffer[head] = data[i];
        head = next;
    }

    return len;
}

int rb_read(uint8_t *out, size_t len)
{
    int i = 0;

    while (i < len && tail != head) {
        out[i++] = buffer[tail];
        tail = (tail + 1) % RING_BUFFER_SIZE;
    }

    return i;
}

int rb_available(void)
{
    if (head >= tail) return head - tail;
    return RING_BUFFER_SIZE - tail + head;
}