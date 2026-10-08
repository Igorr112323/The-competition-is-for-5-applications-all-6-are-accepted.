#include <stdint.h>
#include <math.h>

#define IMG_W 640
#define IMG_H 512
#define NETD_MK 50
#define T_BG_C 15.0
#define T_TAR_C 32.0

static uint16_t frame[IMG_H][IMG_W];
static float therm[IMG_H][IMG_W];
static float stabil_buf[8];

float adc_to_temp_c(uint16_t adc) {
    return (float)adc * 0.02f;
}

float calc_contrast(float t_obj, float t_bg) {
    float dt = fabsf(t_obj - t_bg);
    return dt / (NETD_MK * 0.001f);
}

void gyro_compensate(float gyro_x, float gyro_y, float *dx, float *dy) {
    static float prev_gx = 0, prev_gy = 0;
    float dgx = gyro_x - prev_gx;
    float dgy = gyro_y - prev_gy;
    prev_gx = gyro_x;
    prev_gy = gyro_y;
    for (int i = 0; i < 7; i++) {
        stabil_buf[i] = stabil_buf[i + 1];
    }
    stabil_buf[7] = dgx;
    float sum = 0;
    for (int i = 0; i < 8; i++) sum += stabil_buf[i];
    *dx = sum / 8.0f;
    *dy = dgy;
}

void detect_hotspots(float threshold_c) {
    for (int y = 2; y < IMG_H - 2; y++) {
        for (int x = 2; x < IMG_W - 2; x++) {
            float local_avg = 0;
            for (int dy = -2; dy <= 2; dy++) {
                for (int dx = -2; dx <= 2; dx++) {
                    local_avg += therm[y + dy][x + dx];
                }
            }
            local_avg /= 25.0f;
            float diff = therm[y][x] - local_avg;
            if (diff > threshold_c) {
                frame[y][x] = 0xFFFF;
            }
        }
    }
}

float lidar_calc_range(float P_tx, float rho, float d_rx, float NEP) {
    float A_rx = 3.14159f * (d_rx * 0.5f) * (d_rx * 0.5f);
    return sqrtf(P_tx * rho * A_rx / (3.14159f * NEP * 10.0f));
}

void spray_drift_correct(float wind_ms, float temp_c, float rh_pct, float *factor) {
    float evap = 0.01f * (temp_c - 20.0f) * (1.0f - rh_pct * 0.01f);
    float drift = 0.05f * wind_ms * wind_ms;
    *factor = 1.0f - drift - evap;
    if (*factor < 0.3f) *factor = 0.3f;
}

int main(void) {
    float contrast = calc_contrast(T_TAR_C, T_BG_C);
    float range = lidar_calc_range(75.0f, 0.3f, 0.025f, 1e-12f);
    float dx, dy;
    gyro_compensate(0.01f, 0.02f, &dx, &dy);
    float spray;
    spray_drift_correct(5.0f, 25.0f, 60.0f, &spray);
    detect_hotspots(2.0f);
    return 0;
}