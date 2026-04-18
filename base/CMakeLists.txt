cmake_minimum_required(VERSION 3.20.0)
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})

project(untitled)

target_sources(app PRIVATE
    src/main.c

    src/usb_dma.c
    src/ring_buffer.c
    src/frame_assembler.c

    src/yolo.c
    src/postprocess.c

    src/state_machine.c
    src/gpio_output.c
)