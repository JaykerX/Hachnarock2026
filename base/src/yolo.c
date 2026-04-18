#include "yolo.h"
#include "state_machine.h"

//#include "tensorflow/lite/micro/micro_interpreter.h"
#include "model_data.cc"

static float run_model(uint8_t *img)
{

    int sum = 0;

    for (int i = 0; i < 1024; i++) {
        sum += img[i];
    }

    return (float)sum / 32768.0f;
}

bool yolo_detect(uint8_t *img)
{
    float score = run_model(img);

    return (score > 0.5f);
}