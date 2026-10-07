#include <stdint.h>
#include <math.h>
#include <string.h>

#define NIR_POINTS 80
#define LAMBDA_MIN 900
#define LAMBDA_MAX 1700
#define UV_CHANNELS 2
#define PH_CHANNELS 1
#define COND_CHANNELS 1
#define LIBRARY_SIZE 500
#define FFT_SIZE 256
#define BLE_MTU 244

typedef struct {
    float nir_spectrum[NIR_POINTS];
    float uv_fluorescence[UV_CHANNELS];
    float ph_value;
    float conductivity;
    float temperature;
} measurement_t;

typedef struct {
    char name[32];
    float protein;
    float fat;
    float moisture;
    float fiber;
    float nir_spectrum[NIR_POINTS];
    float uv_fluorescence[UV_CHANNELS];
} reference_entry_t;

typedef struct {
    float protein;
    float fat;
    float moisture;
    float fiber;
    float ph_value;
    float conductivity;
    uint8_t quality_class;
} result_t;

static reference_entry_t library[LIBRARY_SIZE];
static float snv_buffer[NIR_POINTS];
static float derivative_buffer[NIR_POINTS];
static float residual[NIR_POINTS];

void snv_transform(float* spectrum, int n) {
    float mean = 0.0f;
    float std = 0.0f;
    for (int i = 0; i < n; i++) mean += spectrum[i];
    mean /= n;
    for (int i = 0; i < n; i++) std += (spectrum[i] - mean) * (spectrum[i] - mean);
    std = sqrtf(std / n);
    for (int i = 0; i < n; i++) {
        if (std > 1e-10f) spectrum[i] = (spectrum[i] - mean) / std;
        else spectrum[i] = 0.0f;
    }
}

void savitzky_golay_derivative(float* input, float* output, int n) {
    float coeffs[] = {-0.0833f, -0.0833f, -0.0833f, -0.0833f, 0.0f,
                       0.0833f,  0.0833f,  0.0833f,  0.0833f};
    int half = 4;
    for (int i = half; i < n - half; i++) {
        output[i] = 0.0f;
        for (int j = -half; j <= half; j++) {
            output[i] += input[i + j] * coeffs[j + half];
        }
    }
    for (int i = 0; i < half; i++) output[i] = output[half];
    for (int i = n - half; i < n; i++) output[i] = output[n - half - 1];
}

void baseline_correction(float* spectrum, int n) {
    float min_val = spectrum[0];
    for (int i = 1; i < n; i++) {
        if (spectrum[i] < min_val) min_val = spectrum[i];
    }
    for (int i = 0; i < n; i++) spectrum[i] -= min_val;
}

float mnk_compare(float* measured, float* reference, int n) {
    float sum_xy = 0.0f;
    float sum_xx = 0.0f;
    float sum_yy = 0.0f;
    for (int i = 0; i < n; i++) {
        sum_xy += measured[i] * reference[i];
        sum_xx += measured[i] * measured[i];
        sum_yy += reference[i] * reference[i];
    }
    float denom = sqrtf(sum_xx * sum_yy);
    if (denom < 1e-10f) return 0.0f;
    return sum_xy / denom;
}

float mnk_predict(float* measured, float* reference, int n) {
    float sum_xy = 0.0f;
    float sum_xx = 0.0f;
    for (int i = 0; i < n; i++) {
        sum_xy += measured[i] * reference[i];
        sum_xx += measured[i] * measured[i];
    }
    if (sum_xx < 1e-10f) return 0.0f;
    return sum_xy / sum_xx;
}

int find_best_match(float* processed_spectrum, int n) {
    int best_idx = 0;
    float best_score = 0.0f;
    for (int i = 0; i < LIBRARY_SIZE; i++) {
        float score = mnk_compare(processed_spectrum, library[i].nir_spectrum, n);
        if (score > best_score) {
            best_score = score;
            best_idx = i;
        }
    }
    return best_idx;
}

void analyze_sample(measurement_t* meas, result_t* res) {
    memcpy(snv_buffer, meas->nir_spectrum, NIR_POINTS * sizeof(float));
    snv_transform(snv_buffer, NIR_POINTS);
    baseline_correction(snv_buffer, NIR_POINTS);
    savitzky_golay_derivative(snv_buffer, derivative_buffer, NIR_POINTS);

    int best = find_best_match(snv_buffer, NIR_POINTS);
    float scale = mnk_predict(snv_buffer, library[best].nir_spectrum, NIR_POINTS);

    res->protein = library[best].protein * scale;
    res->fat = library[best].fat * scale;
    res->moisture = library[best].moisture * scale;
    res->fiber = library[best].fiber * scale;
    res->ph_value = meas->ph_value;
    res->conductivity = meas->conductivity;

    uint8_t score = 0;
    if (res->protein > 10.0f && res->protein < 25.0f) score++;
    if (res->moisture > 8.0f && res->moisture < 18.0f) score++;
    if (res->ph_value > 5.5f && res->ph_value < 7.5f) score++;
    if (res->conductivity < 10.0f) score++;
    res->quality_class = score;
}

float read_nir_channel(int channel) {
    uint16_t raw = 0;
    float voltage = (float)raw / 65535.0f * 3.3f;
    return voltage;
}

float read_uv_channel(int channel) {
    uint16_t raw = 0;
    float voltage = (float)raw / 65535.0f * 3.3f;
    return voltage;
}

float read_ph() {
    uint16_t raw = 0;
    float voltage = (float)raw / 65535.0f * 3.3f;
    return 7.0f + (1.65f - voltage) / 0.059f;
}

float read_conductivity() {
    uint16_t raw = 0;
    float voltage = (float)raw / 65535.0f * 3.3f;
    return voltage * 6.06f;
}

void take_measurement(measurement_t* meas) {
    for (int i = 0; i < NIR_POINTS; i++) {
        meas->nir_spectrum[i] = read_nir_channel(i);
    }
    for (int i = 0; i < UV_CHANNELS; i++) {
        meas->uv_fluorescence[i] = read_uv_channel(i);
    }
    meas->ph_value = read_ph();
    meas->conductivity = read_conductivity();
}

void send_ble_result(result_t* res) {
    uint8_t buf[32];
    memcpy(buf, res, sizeof(result_t) < 32 ? sizeof(result_t) : 32);
}

int main(void) {
    measurement_t meas;
    result_t res;
    while (1) {
        take_measurement(&meas);
        analyze_sample(&meas, &res);
        send_ble_result(&res);
    }
    return 0;
}