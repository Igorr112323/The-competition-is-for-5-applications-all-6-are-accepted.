#include <stdint.h>
#include <math.h>

#define FFT_SIZE 1024
#define SAMPLE_HZ 4000
#define VIB_FREQ_TARGET 50.0f
#define VIB_AMP_TARGET 1.5f
#define FRACTION_COUNT 3
#define CYCLE_MS 100

typedef struct {
    float freq_hz;
    float amp_mm;
    float accel_raw[FFT_SIZE];
    float spectrum[FFT_SIZE / 2];
    uint32_t seed_count[FRACTION_COUNT];
    float separation_eff;
    uint8_t vib_on;
    uint8_t mode;
} SeparatorState;

static SeparatorState sep;
static float fft_real[FFT_SIZE];
static float fft_imag[FFT_SIZE];

void fft_compute(float *input, int n) {
    for (int i = 0; i < n; i++) {
        fft_real[i] = input[i];
        fft_imag[i] = 0;
    }
    for (int s = 1; s <= 10; s++) {
        int m = 1 << s;
        int half = m / 2;
        float angle = -2.0f * 3.14159265f / m;
        float w_real = cosf(angle);
        float w_imag = sinf(angle);
        for (int k = 0; k < n; k += m) {
            float cur_real = 1.0f;
            float cur_imag = 0.0f;
            for (int j = 0; j < half; j++) {
                int even = k + j;
                int odd = k + j + half;
                float t_real = cur_real * fft_real[odd] - cur_imag * fft_imag[odd];
                float t_imag = cur_real * fft_imag[odd] + cur_imag * fft_real[odd];
                fft_real[odd] = fft_real[even] - t_real;
                fft_imag[odd] = fft_imag[even] - t_imag;
                fft_real[even] += t_real;
                fft_imag[even] += t_imag;
                float new_real = cur_real * w_real - cur_imag * w_imag;
                float new_imag = cur_real * w_imag + cur_imag * w_real;
                cur_real = new_real;
                cur_imag = new_imag;
            }
        }
    }
}

void find_peak_freq(int n, float sample_rate) {
    float max_mag = 0;
    int max_idx = 0;
    for (int i = 1; i < n / 2; i++) {
        float mag = sqrtf(fft_real[i] * fft_real[i] + fft_imag[i] * fft_imag[i]);
        if (mag > max_mag) {
            max_mag = mag;
            max_idx = i;
        }
    }
    sep.freq_hz = (float)max_idx * sample_rate / n;
    sep.amp_mm = max_mag / n * 1000.0f;
}

float calc_separation_eff(uint32_t *counts, int n) {
    uint32_t total = 0;
    for (int i = 0; i < n; i++) total += counts[i];
    if (total == 0) return 0;
    uint32_t target = counts[0];
    return (float)target / total * 100.0f;
}

void vibration_control(float target_freq, float target_amp) {
    float error_f = target_freq - sep.freq_hz;
    float error_a = target_amp - sep.amp_mm;
    if (fabsf(error_f) > 2.0f || fabsf(error_a) > 0.2f) {
        sep.vib_on = 1;
    } else {
        sep.vib_on = 0;
    }
}

void accel_callback(float *data, int n) {
    for (int i = 0; i < n && i < FFT_SIZE; i++) {
        sep.accel_raw[i] = data[i];
    }
}

void sieve_count_callback(int layer, uint32_t count) {
    if (layer < FRACTION_COUNT) {
        sep.seed_count[layer] = count;
    }
}

void ble_send(void) {
    uint8_t buf[20];
    buf[0] = (uint8_t)sep.freq_hz;
    buf[1] = (uint8_t)(sep.amp_mm * 100);
    buf[2] = (uint8_t)sep.separation_eff;
    buf[3] = sep.vib_on;
    buf[4] = sep.mode;
    for (int i = 0; i < FRACTION_COUNT; i++) {
        buf[5 + i * 3] = (sep.seed_count[i] >> 16) & 0xFF;
        buf[6 + i * 3] = (sep.seed_count[i] >> 8) & 0xFF;
        buf[7 + i * 3] = sep.seed_count[i] & 0xFF;
    }
}

void control_loop(void) {
    fft_compute(sep.accel_raw, FFT_SIZE);
    find_peak_freq(FFT_SIZE, SAMPLE_HZ);
    sep.separation_eff = calc_separation_eff(sep.seed_count, FRACTION_COUNT);
    vibration_control(VIB_FREQ_TARGET, VIB_AMP_TARGET);
    ble_send();
}

int main(void) {
    sep.vib_on = 0;
    sep.mode = 0;
    while (1) {
        control_loop();
        delay_ms(CYCLE_MS);
    }
    return 0;
}