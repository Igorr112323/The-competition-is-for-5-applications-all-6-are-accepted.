#include <stdint.h>
#include <math.h>
#include <string.h>

#define TARGET_TEMP 65.0f
#define TEMP_TOLERANCE 0.5f
#define NTC_BETA 3950
#define NTC_R0 10000
#define NTC_T0 298.15f
#define ADC_MAX 65535
#define ADC_VREF 3.3f
#define HEATER_PWM_MAX 255
#define PID_KP 50.0f
#define PID_KI 0.5f
#define PID_KD 10.0f
#define N_TARGETS 7
#define PHOTODIODE_CHANNELS 4
#define MEASUREMENT_INTERVAL_MS 1000

typedef struct {
    float temperature;
    float pid_output;
    uint32_t time_ms;
    uint8_t heater_on;
} heater_state_t;

typedef struct {
    uint16_t photodiode[PHOTODIODE_CHANNELS];
    float temperature;
    uint32_t time_ms;
} measurement_t;

typedef struct {
    char target_name[32];
    float ct_time_s;
    float t_threshold;
    uint8_t detected;
    float confidence;
} lamp_result_t;

static heater_state_t heater = {0};
static float integral = 0;
static float prev_error = 0;

float ntc_to_celsius(uint16_t adc_val) {
    float voltage = (float)adc_val / ADC_MAX * ADC_VREF;
    float resistance = 10000.0f * voltage / (ADC_VREF - voltage);
    float temp_k = 1.0f / (1.0f/NTC_T0 + 1.0f/NTC_BETA * logf(resistance/NTC_R0));
    return temp_k - 273.15f;
}

float pid_control(float current, float target, float dt) {
    float error = target - current;
    integral += error * dt;
    float derivative = (error - prev_error) / dt;
    prev_error = error;
    float output = PID_KP * error + PID_KI * integral + PID_KD * derivative;
    if (output > HEATER_PWM_MAX) output = HEATER_PWM_MAX;
    if (output < 0) output = 0;
    return output;
}

void set_heater_pwm(uint8_t pwm) {
    (void)pwm;
}

void lamp_detect(measurement_t* meas, int n_samples, lamp_result_t* results) {
    for (int t = 0; t < N_TARGETS; t++) {
        float baseline = 0;
        for (int i = 0; i < 10; i++) baseline += meas[i].photodiode[t % PHOTODIODE_CHANNELS];
        baseline /= 10;
        float last_val = meas[n_samples-1].photodiode[t % PHOTODIODE_CHANNELS];
        float ratio = last_val / baseline;
        results[t].detected = (ratio > 1.5f) ? 1 : 0;
        results[t].confidence = ratio;
        results[t].ct_time_s = n_samples * MEASUREMENT_INTERVAL_MS / 1000.0f;
    }
}

void send_ble(lamp_result_t* results) {
    uint8_t buf[244];
    memcpy(buf, results, sizeof(lamp_result_t) * N_TARGETS);
}

int main(void) {
    measurement_t samples[300];
    lamp_result_t results[N_TARGETS];
    int sample_idx = 0;
    while (1) {
        uint16_t ntc_adc = 0;
        float temp = ntc_to_celsius(ntc_adc);
        heater.pid_output = pid_control(temp, TARGET_TEMP, 0.1f);
        set_heater_pwm((uint8_t)heater.pid_output);
        if (fabsf(temp - TARGET_TEMP) < TEMP_TOLERANCE) {
            heater.heater_on = 1;
            if (sample_idx < 300) sample_idx++;
        }
        if (sample_idx >= 2700) {
            lamp_detect(samples, sample_idx, results);
            send_ble(results);
            sample_idx = 0;
        }
    }
    return 0;
}
