#include <stdint.h>
#include <math.h>

#define LIDAR_POINTS 360
#define NOZZLE_COUNT 6
#define PWM_MAX 255
#define CYCLE_MS 100
#define BLE_MTU 20

typedef struct {
    uint16_t distances[LIDAR_POINTS];
    float wind_speed;
    float flow_rate;
    float gps_speed;
    float lai;
    float drift_factor;
    float pwm_duty;
    uint8_t nozzle_pwm[NOZZLE_COUNT];
} AeroState;

static AeroState state;

float calc_lai(uint16_t *dist, float max_range) {
    int hits = 0;
    for (int i = 0; i < LIDAR_POINTS; i++) {
        if (dist[i] < (uint16_t)(max_range * 1000) && dist[i] > 50) {
            hits++;
        }
    }
    float gap_fraction = 1.0f - (float)hits / LIDAR_POINTS;
    if (gap_fraction < 0.01f) gap_fraction = 0.01f;
    return -logf(gap_fraction);
}

float calc_drift_factor(float lai, float v_wind, float h_boom) {
    float k = 0.05f;
    float n = 1.2f;
    float m = 0.8f;
    float p = 0.5f;
    float lai_f = 1.0f - 0.15f * (lai - 2.0f) / 3.0f;
    if (lai_f < 0.5f) lai_f = 0.5f;
    if (lai_f > 1.0f) lai_f = 1.0f;
    float drift = k * powf(v_wind, n) * powf(200.0f, m) * powf(h_boom, p);
    return drift * lai_f;
}

float calc_pwm(float target_lha, float v_speed, float boom_width) {
    if (v_speed < 0.1f) v_speed = 0.1f;
    float flow_lpm = target_lha * v_speed * boom_width / 60.0f;
    float pwm = flow_lpm / 10.0f * PWM_MAX;
    if (pwm > PWM_MAX) pwm = PWM_MAX;
    if (pwm < 20) pwm = 20;
    return pwm;
}

void update_nozzles(float base_pwm) {
    for (int i = 0; i < NOZZLE_COUNT; i++) {
        state.nozzle_pwm[i] = (uint8_t)base_pwm;
    }
}

void ble_send_state(void) {
    uint8_t buf[BLE_MTU];
    buf[0] = (uint8_t)(state.lai * 10);
    buf[1] = (uint8_t)(state.wind_speed * 10);
    buf[2] = (uint8_t)(state.drift_factor * 100);
    buf[3] = state.nozzle_pwm[0];
    buf[4] = (uint8_t)(state.flow_rate * 10);
    buf[5] = (uint8_t)(state.gps_speed * 10);
}

void control_loop(void) {
    state.lai = calc_lai(state.distances, 12.0f);
    state.drift_factor = calc_drift_factor(state.lai, state.wind_speed, 1.5f);
    float target_lha = 300.0f * (1.0f - state.drift_factor);
    state.pwm_duty = calc_pwm(target_lha, state.gps_speed, 3.0f);
    update_nozzles(state.pwm_duty);
    state.flow_rate = target_lha;
    ble_send_state();
}

void lidar_callback(uint16_t *dist) {
    for (int i = 0; i < LIDAR_POINTS; i++) {
        state.distances[i] = dist[i];
    }
}

void anemometer_callback(float speed) {
    state.wind_speed = speed;
}

void gps_callback(float speed) {
    state.gps_speed = speed;
}

void flow_callback(float rate) {
    state.flow_rate = rate;
}

int main(void) {
    while (1) {
        control_loop();
        delay_ms(CYCLE_MS);
    }
    return 0;
}