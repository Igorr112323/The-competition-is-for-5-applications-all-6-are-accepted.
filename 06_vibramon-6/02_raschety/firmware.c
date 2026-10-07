#include <stdint.h>
#include <math.h>
#include <string.h>

#define FFT_SIZE 1024
#define SAMPLE_RATE 10000
#define FREQ_RESOLUTION ((float)SAMPLE_RATE / FFT_SIZE)
#define N_BEARINGS 3
#define N_FAULTS 4
#define N_CHANNELS 4
#define BLE_MESH_MAX_NODES 20
#define ALERT_THRESHOLD_VELOCITY 4.5f
#define ALERT_THRESHOLD_ACCEL 0.5f
#define TEMPERATURE_MAX 120.0f

typedef struct {
    float re[FFT_SIZE];
    float im[FFT_SIZE];
    float magnitude[FFT_SIZE / 2];
} fft_result_t;

typedef struct {
    float accel_x[FFT_SIZE];
    float accel_y[FFT_SIZE];
    float accel_z[FFT_SIZE];
    float temperature;
    float current;
    uint32_t timestamp;
} sensor_data_t;

typedef struct {
    float bpfo;
    float bpfi;
    float bsf;
    float ftf;
} bearing_params_t;

typedef struct {
    float vibration_velocity;
    float vibration_acceleration;
    float kurtosis;
    float spectral_kurtosis;
    float temperature;
    float current;
    uint8_t fault_type;
    uint8_t severity;
    float remaining_hours;
} diagnostic_result_t;

static const bearing_params_t bearings[N_BEARINGS] = {
    {3.16f, 4.84f, 2.06f, 0.40f},
    {3.58f, 5.42f, 2.32f, 0.40f},
    {3.05f, 4.95f, 2.02f, 0.40f}
};

static float twiddle_re[FFT_SIZE / 2];
static float twiddle_im[FFT_SIZE / 2];

void fft_init() {
    for (int i = 0; i < FFT_SIZE / 2; i++) {
        float angle = -2.0f * 3.14159265f * i / FFT_SIZE;
        twiddle_re[i] = cosf(angle);
        twiddle_im[i] = sinf(angle);
    }
}

void fft_radix2(float* input_re, float* input_im, float* output_re, float* output_im, int n) {
    if (n <= 1) {
        output_re[0] = input_re[0];
        output_im[0] = input_im[0];
        return;
    }
    int half = n / 2;
    float even_re[FFT_SIZE / 2];
    float even_im[FFT_SIZE / 2];
    float odd_re[FFT_SIZE / 2];
    float odd_im[FFT_SIZE / 2];
    for (int i = 0; i < half; i++) {
        even_re[i] = input_re[2 * i];
        even_im[i] = input_im[2 * i];
        odd_re[i] = input_re[2 * i + 1];
        odd_im[i] = input_im[2 * i + 1];
    }
    float even_fft_re[FFT_SIZE / 2];
    float even_fft_im[FFT_SIZE / 2];
    float odd_fft_re[FFT_SIZE / 2];
    float odd_fft_im[FFT_SIZE / 2];
    fft_radix2(even_re, even_im, even_fft_re, even_fft_im, half);
    fft_radix2(odd_re, odd_im, odd_fft_re, odd_fft_im, half);
    for (int k = 0; k < half; k++) {
        float t_re = twiddle_re[k] * odd_fft_re[k] - twiddle_im[k] * odd_fft_im[k];
        float t_im = twiddle_re[k] * odd_fft_im[k] + twiddle_im[k] * odd_fft_re[k];
        output_re[k] = even_fft_re[k] + t_re;
        output_im[k] = even_fft_im[k] + t_im;
        output_re[k + half] = even_fft_re[k] - t_re;
        output_im[k + half] = even_fft_im[k] - t_im;
    }
}

void compute_magnitude(float* re, float* im, float* mag, int n) {
    for (int i = 0; i < n / 2; i++) {
        mag[i] = sqrtf(re[i] * re[i] + im[i] * im[i]) / n;
    }
}

void hilbert_envelope(float* signal, float* envelope, int n) {
    float analytic_re[FFT_SIZE];
    float analytic_im[FFT_SIZE];
    float fft_re[FFT_SIZE];
    float fft_im[FFT_SIZE];
    memset(analytic_im, 0, n * sizeof(float));
    memcpy(analytic_re, signal, n * sizeof(float));
    fft_radix2(analytic_re, analytic_im, fft_re, fft_im, n);
    for (int i = 1; i < n / 2; i++) {
        fft_im[i] *= -1.0f;
    }
    for (int i = n / 2 + 1; i < n; i++) {
        fft_re[i] = 0.0f;
        fft_im[i] = 0.0f;
    }
    float inv_re[FFT_SIZE];
    float inv_im[FFT_SIZE];
    fft_radix2(fft_re, fft_im, inv_re, inv_im, n);
    for (int i = 0; i < n; i++) {
        envelope[i] = sqrtf(signal[i] * signal[i] + inv_im[i] * inv_im[i]);
    }
}

float compute_kurtosis(float* signal, int n) {
    float mean = 0.0f;
    for (int i = 0; i < n; i++) mean += signal[i];
    mean /= n;
    float m2 = 0.0f;
    float m4 = 0.0f;
    for (int i = 0; i < n; i++) {
        float d = signal[i] - mean;
        m2 += d * d;
        m4 += d * d * d * d;
    }
    m2 /= n;
    m4 /= n;
    if (m2 < 1e-10f) return 0.0f;
    return m4 / (m2 * m2) - 3.0f;
}

float compute_spectral_kurtosis(float* magnitude, int n) {
    int n_bands = 16;
    int band_size = n / n_bands;
    float sk_sum = 0.0f;
    for (int b = 0; b < n_bands; b++) {
        float band_mean = 0.0f;
        for (int i = 0; i < band_size; i++) {
            band_mean += magnitude[b * band_size + i];
        }
        band_mean /= band_size;
        float band_m2 = 0.0f;
        float band_m4 = 0.0f;
        for (int i = 0; i < band_size; i++) {
            float d = magnitude[b * band_size + i] - band_mean;
            band_m2 += d * d;
            band_m4 += d * d * d * d;
        }
        band_m2 /= band_size;
        band_m4 /= band_size;
        if (band_m2 > 1e-10f) {
            sk_sum += band_m4 / (band_m2 * band_m2) - 3.0f;
        }
    }
    return sk_sum / n_bands;
}

void order_tracking(float* signal, float* tacho, int n, int rpm, float* resampled) {
    float target_angle = 2.0f * 3.14159265f / n;
    int resample_idx = 0;
    float current_angle = 0.0f;
    for (int i = 0; i < n - 1; i++) {
        float angle_step = tacho[i] * 2.0f * 3.14159265f / 60.0f / SAMPLE_RATE;
        current_angle += angle_step;
        if (current_angle >= target_angle * resample_idx && resample_idx < n) {
            resampled[resample_idx] = signal[i];
            resample_idx++;
        }
    }
}

float compute_rms_velocity(float* signal, int n) {
    float sum = 0.0f;
    for (int i = 0; i < n; i++) sum += signal[i] * signal[i];
    return sqrtf(sum / n);
}

float compute_rms_acceleration(float* signal, int n) {
    float sum = 0.0f;
    for (int i = 0; i < n; i++) sum += signal[i] * signal[i];
    return sqrtf(sum / n) / 9.81f;
}

int detect_fault_type(float* envelope_spectrum, int n, float shaft_freq, int bearing_idx) {
    float bpfo_freq = shaft_freq * bearings[bearing_idx].bpfo;
    float bpfi_freq = shaft_freq * bearings[bearing_idx].bpfi;
    float bsf_freq = shaft_freq * bearings[bearing_idx].bsf;
    int bpfo_bin = (int)(bpfo_freq / FREQ_RESOLUTION);
    int bpfi_bin = (int)(bpfi_freq / FREQ_RESOLUTION);
    int bsf_bin = (int)(bsf_freq / FREQ_RESOLUTION);
    float max_amp = 0.0f;
    int fault = 0;
    if (bpfo_bin < n / 2 && envelope_spectrum[bpfo_bin] > max_amp) {
        max_amp = envelope_spectrum[bpfo_bin];
        fault = 1;
    }
    if (bpfi_bin < n / 2 && envelope_spectrum[bpfi_bin] > max_amp) {
        max_amp = envelope_spectrum[bpfi_bin];
        fault = 2;
    }
    if (bsf_bin < n / 2 && envelope_spectrum[bsf_bin] > max_amp) {
        max_amp = envelope_spectrum[bsf_bin];
        fault = 3;
    }
    return fault;
}

uint8_t assess_severity(float rms_vel, float rms_acc, float kurtosis) {
    uint8_t severity = 0;
    if (rms_vel > ALERT_THRESHOLD_VELOCITY * 0.5f) severity = 1;
    if (rms_vel > ALERT_THRESHOLD_VELOCITY * 0.75f) severity = 2;
    if (rms_vel > ALERT_THRESHOLD_VELOCITY) severity = 3;
    if (rms_vel > ALERT_THRESHOLD_VELOCITY * 1.5f) severity = 4;
    if (kurtosis > 4.0f && severity < 3) severity++;
    return severity;
}

float estimate_remaining_hours(uint8_t severity, float degradation_rate) {
    float base_hours[] = {0, 500, 200, 50, 10};
    if (severity > 4) severity = 4;
    return base_hours[severity] / (degradation_rate > 0 ? degradation_rate : 1.0f);
}

void run_diagnostic(sensor_data_t* data, diagnostic_result_t* result) {
    fft_result_t fft_x;
    float envelope[FFT_SIZE];
    float envelope_spectrum[FFT_SIZE / 2];

    memset(fft_x.im, 0, FFT_SIZE * sizeof(float));
    memcpy(fft_x.re, data->accel_x, FFT_SIZE * sizeof(float));
    fft_radix2(fft_x.re, fft_x.im, fft_x.re, fft_x.im, FFT_SIZE);
    compute_magnitude(fft_x.re, fft_x.im, fft_x.magnitude, FFT_SIZE);

    hilbert_envelope(data->accel_x, envelope, FFT_SIZE);
    float env_im[FFT_SIZE];
    memset(env_im, 0, FFT_SIZE * sizeof(float));
    fft_radix2(envelope, env_im, envelope, env_im, FFT_SIZE);
    compute_magnitude(envelope, env_im, envelope_spectrum, FFT_SIZE);

    result->vibration_velocity = compute_rms_velocity(data->accel_x, FFT_SIZE);
    result->vibration_acceleration = compute_rms_acceleration(data->accel_x, FFT_SIZE);
    result->kurtosis = compute_kurtosis(data->accel_x, FFT_SIZE);
    result->spectral_kurtosis = compute_spectral_kurtosis(fft_x.magnitude, FFT_SIZE);
    result->temperature = data->temperature;
    result->current = data->current;

    float shaft_freq = data->current / 60.0f;
    result->fault_type = detect_fault_type(envelope_spectrum, FFT_SIZE, shaft_freq, 0);
    result->severity = assess_severity(result->vibration_velocity, result->vibration_acceleration, result->kurtosis);
    result->remaining_hours = estimate_remaining_hours(result->severity, 1.0f);
}

void send_ble_alert(diagnostic_result_t* result) {
    uint8_t buf[32];
    memcpy(buf, result, sizeof(diagnostic_result_t) < 32 ? sizeof(diagnostic_result_t) : 32);
}

int main(void) {
    fft_init();
    while (1) {
        sensor_data_t data;
        diagnostic_result_t result;
        run_diagnostic(&data, &result);
        if (result.severity >= 2) {
            send_ble_alert(&result);
        }
    }
    return 0;
}