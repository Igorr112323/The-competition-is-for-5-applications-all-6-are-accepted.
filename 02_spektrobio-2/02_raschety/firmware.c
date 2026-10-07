#include <stdint.h>
#include <math.h>
#include <string.h>

#define NIR_POINTS 50
#define LAMBDA_MIN 2500
#define LAMBDA_MAX 5000
#define LIBRARY_SIZE 100
#define FFT_SIZE 128
#define GAS_CHANNELS 4

typedef struct {
    float spectrum[NIR_POINTS];
    float temperature;
    float pressure;
    float humidity;
} measurement_t;

typedef struct {
    char name[16];
    float threshold_ppm;
    float reference[NIR_POINTS];
} gas_entry_t;

typedef struct {
    float concentrations[GAS_CHANNELS];
    float confidence[GAS_CHANNELS];
    uint8_t alert[GAS_CHANNELS];
} result_t;

static gas_entry_t library[LIBRARY_SIZE] = {
    {"CO", 10.0, {0}},
    {"NO", 25.0, {0}},
    {"acetone", 0.5, {0}},
    {"ethanol", 0.5, {0}},
};

static float calibration[GAS_CHANNELS][NIR_POINTS];

void snv_normalize(float* spectrum, int n) {
    float mean = 0, std = 0;
    for (int i = 0; i < n; i++) mean += spectrum[i];
    mean /= n;
    for (int i = 0; i < n; i++) std += (spectrum[i]-mean)*(spectrum[i]-mean);
    std = sqrtf(std/n);
    for (int i = 0; i < n; i++) spectrum[i] = (std > 1e-10f) ? (spectrum[i]-mean)/std : 0;
}

float mnk_concentration(float* measured, float* reference, int n) {
    float sum_xy = 0, sum_xx = 0;
    for (int i = 0; i < n; i++) {
        sum_xy += measured[i] * reference[i];
        sum_xx += reference[i] * reference[i];
    }
    return (sum_xx > 1e-10f) ? sum_xy / sum_xx : 0;
}

float mnk_confidence(float* measured, float* reference, int n) {
    float sum_xy = 0, sum_xx = 0, sum_yy = 0;
    for (int i = 0; i < n; i++) {
        sum_xy += measured[i] * reference[i];
        sum_xx += measured[i] * measured[i];
        sum_yy += reference[i] * reference[i];
    }
    float denom = sqrtf(sum_xx * sum_yy);
    return (denom > 1e-10f) ? sum_xy / denom : 0;
}

void analyze_sample(measurement_t* meas, result_t* res) {
    float normalized[NIR_POINTS];
    memcpy(normalized, meas->spectrum, NIR_POINTS * sizeof(float));
    snv_normalize(normalized, NIR_POINTS);
    for (int g = 0; g < GAS_CHANNELS; g++) {
        res->concentrations[g] = mnk_concentration(normalized, library[g].reference, NIR_POINTS);
        res->confidence[g] = mnk_confidence(normalized, library[g].reference, NIR_POINTS);
        res->alert[g] = (res->concentrations[g] > library[g].threshold_ppm) ? 1 : 0;
    }
}

void compensate_temperature(measurement_t* meas) {
    float temp_coeff = 0.002f;
    float delta = meas->temperature - 25.0f;
    for (int i = 0; i < NIR_POINTS; i++) {
        meas->spectrum[i] *= (1.0f - temp_coeff * delta);
    }
}

void send_ble_result(result_t* res) {
    uint8_t buf[32];
    memcpy(buf, res, sizeof(result_t) < 32 ? sizeof(result_t) : 32);
}

int main(void) {
    measurement_t meas;
    result_t res;
    while (1) {
        compensate_temperature(&meas);
        analyze_sample(&meas, &res);
        send_ble_result(&res);
    }
    return 0;
}
