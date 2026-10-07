#include <stdint.h>
#include <math.h>

#define ROWS 6
#define HISTORY_LEN 100
#define CV_TARGET 5.0
#define PRESSURE_MIN 100
#define PRESSURE_MAX 400
#define CYCLE_MS 200

typedef struct {
    uint32_t seed_count[ROWS];
    float cv;
    float pressure_mbar;
    float fan_rpm;
    float gps_speed;
    uint8_t corrected;
    uint32_t total_seeds;
} SowState;

static SowState sow;
static uint32_t history[HISTORY_LEN];
static uint8_t hist_idx;

float calc_cv(uint32_t *counts, int n) {
    float sum = 0;
    for (int i = 0; i < n; i++) sum += counts[i];
    float mean = sum / n;
    if (mean < 1) return 100.0f;
    float var = 0;
    for (int i = 0; i < n; i++) {
        float d = counts[i] - mean;
        var += d * d;
    }
    var /= n;
    return sqrtf(var) / mean * 100.0f;
}

float auto_correct_pressure(float cv, float current) {
    if (cv > CV_TARGET * 1.5f) return current * 0.9f;
    if (cv > CV_TARGET) return current * 0.95f;
    if (cv < CV_TARGET * 0.5f) return current * 1.05f;
    if (current < PRESSURE_MIN) return PRESSURE_MIN;
    if (current > PRESSURE_MAX) return PRESSURE_MAX;
    return current;
}

void laser_sensor_callback(int row, uint32_t count) {
    if (row < ROWS) {
        sow.seed_count[row] = count;
        sow.total_seeds += count;
    }
}

void gps_callback(float speed) {
    sow.gps_speed = speed;
}

void update_fan_rpm(float target_pressure) {
    sow.fan_rpm = target_pressure * 50.0f / 200.0f;
}

void ble_send(void) {
    uint8_t buf[20];
    buf[0] = (uint8_t)(sow.cv * 10);
    buf[1] = (uint8_t)(sow.pressure_mbar / 2);
    buf[2] = (uint8_t)(sow.gps_speed * 10);
    buf[3] = sow.corrected;
    buf[4] = (sow.total_seeds >> 24) & 0xFF;
    buf[5] = (sow.total_seeds >> 16) & 0xFF;
    buf[6] = (sow.total_seeds >> 8) & 0xFF;
    buf[7] = sow.total_seeds & 0xFF;
    for (int r = 0; r < ROWS && r < 6; r++) {
        buf[8 + r] = (uint8_t)(sow.seed_count[r] & 0xFF);
    }
}

void control_loop(void) {
    sow.cv = calc_cv(sow.seed_count, ROWS);
    float new_p = auto_correct_pressure(sow.cv, sow.pressure_mbar);
    if (fabsf(new_p - sow.pressure_mbar) > 1.0f) {
        sow.corrected = 1;
    } else {
        sow.corrected = 0;
    }
    sow.pressure_mbar = new_p;
    update_fan_rpm(sow.pressure_mbar);
    history[hist_idx % HISTORY_LEN] = (uint32_t)(sow.cv * 10);
    hist_idx++;
    ble_send();
}

int main(void) {
    sow.pressure_mbar = 200.0f;
    sow.fan_rpm = 50.0f;
    while (1) {
        control_loop();
        delay_ms(CYCLE_MS);
    }
    return 0;
}