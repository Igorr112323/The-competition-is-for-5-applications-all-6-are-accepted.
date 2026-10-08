#include <stdint.h>
#include <math.h>

#define T_TARGET_C 65.0
#define T_AMB_C 25.0
#define NTC_R25 10000.0
#define NTC_B 3950.0
#define HEATER_MAX_W 5.0

static float pid_integral = 0;
static float pid_prev_error = 0;

float ntc_to_temp_c(float R_ohm) {
    float T_K = 1.0f / (1.0f / 298.15f + logf(R_ohm / NTC_R25) / NTC_B);
    return T_K - 273.15f;
}

float pid_control(float T_curr, float T_target, float dt) {
    float Kp = 50.0f, Ki = 0.5f, Kd = 10.0f;
    float error = T_target - T_curr;
    pid_integral += error * dt;
    if (pid_integral > 200.0f) pid_integral = 200.0f;
    if (pid_integral < -50.0f) pid_integral = -50.0f;
    float deriv = (error - pid_prev_error) / dt;
    pid_prev_error = error;
    float out = Kp * error + Ki * pid_integral + Kd * deriv;
    if (out > 100.0f) out = 100.0f;
    if (out < 0.0f) out = 0.0f;
    return out;
}

float lamp_kinetics(float copies_init, float time_min) {
    float rate = 1.15f;
    float result = copies_init;
    for (int i = 0; i < (int)time_min; i++) {
        result *= rate;
        if (result > 1e15f) break;
    }
    return result;
}

int hnb_detect(float abs_650, float abs_550) {
    float ratio = abs_650 / (abs_550 + 1e-6f);
    return ratio > 1.2f ? 1 : 0;
}

void ble_send_result(float temp_c, float copies, int positive) {
    uint8_t pkt[20];
    pkt[0] = 0xAA;
    pkt[1] = (uint8_t)(temp_c * 2);
    uint32_t c = (uint32_t)(copies * 1e-6f);
    pkt[2] = (c >> 24) & 0xFF;
    pkt[3] = (c >> 16) & 0xFF;
    pkt[4] = (c >> 8) & 0xFF;
    pkt[5] = c & 0xFF;
    pkt[6] = positive ? 1 : 0;
    pkt[7] = 0x55;
}

void heat_ramp_simulation(float *temp_curve, int n_steps, float dt) {
    float T = T_AMB_C;
    pid_integral = 0;
    pid_prev_error = 0;
    for (int i = 0; i < n_steps; i++) {
        float duty = pid_control(T, T_TARGET_C, dt);
        float Q_in = HEATER_MAX_W * duty * 0.01f;
        float Q_loss = 0.02f * (T - T_AMB_C);
        T += (Q_in - Q_loss) * dt / 2.0f;
        temp_curve[i] = T;
    }
}

int main(void) {
    float R_ntc = 2086.0f;
    float T = ntc_to_temp_c(R_ntc);
    float duty = pid_control(T, T_TARGET_C, 1.0f);
    float copies = lamp_kinetics(100.0f, 45.0f);
    int pos = hnb_detect(0.65f, 0.40f);
    ble_send_result(T, copies, pos);
    float curve[300];
    heat_ramp_simulation(curve, 300, 1.0f);
    return 0;
}