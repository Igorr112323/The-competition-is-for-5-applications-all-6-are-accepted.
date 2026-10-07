#include <stdint.h>
#include <math.h>
#include <string.h>

#define SAMPLE_RATE 48000
#define FFT_SIZE 4096
#define FREQ_RES ((float)SAMPLE_RATE / FFT_SIZE)
#define MFCC_FEATURES 13
#define N_FILTERS 26
#define FRAME_MS 25
#define HOP_MS 10
#define FRAME_SAMPLES (SAMPLE_RATE * FRAME_MS / 1000)
#define HOP_SAMPLES (SAMPLE_RATE * HOP_MS / 1000)
#define ML_CLASSES 5

typedef struct {
    float re[FFT_SIZE];
    float im[FFT_SIZE];
    float magnitude[FFT_SIZE / 2];
} fft_result_t;

typedef struct {
    float mfcc[MFCC_FEATURES];
    float energy;
    float zero_crossing;
    float spectral_centroid;
} feature_t;

typedef struct {
    float f0_hz;
    float breath_rate;
    uint8_t cough_detected;
    uint8_t cough_type;
    float cough_confidence;
    uint8_t health_class;
} result_t;

static float twiddle_re[FFT_SIZE / 2];
static float twiddle_im[FFT_SIZE / 2];
static float mel_filterbank[N_FILTERS][FFT_SIZE / 2];

void fft_init() {
    for (int i = 0; i < FFT_SIZE / 2; i++) {
        float angle = -2.0f * M_PI * i / FFT_SIZE;
        twiddle_re[i] = cosf(angle);
        twiddle_im[i] = sinf(angle);
    }
}

void fft(float* in_re, float* in_im, float* out_re, float* out_im, int n) {
    if (n <= 1) { out_re[0] = in_re[0]; out_im[0] = in_im[0]; return; }
    int half = n / 2;
    float e_re[FFT_SIZE/2], e_im[FFT_SIZE/2], o_re[FFT_SIZE/2], o_im[FFT_SIZE/2];
    for (int i = 0; i < half; i++) {
        e_re[i] = in_re[2*i]; e_im[i] = in_im[2*i];
        o_re[i] = in_re[2*i+1]; o_im[i] = in_im[2*i+1];
    }
    float ef_re[FFT_SIZE/2], ef_im[FFT_SIZE/2], of_re[FFT_SIZE/2], of_im[FFT_SIZE/2];
    fft(e_re, e_im, ef_re, ef_im, half);
    fft(o_re, o_im, of_re, of_im, half);
    for (int k = 0; k < half; k++) {
        float t_re = twiddle_re[k]*of_re[k] - twiddle_im[k]*of_im[k];
        float t_im = twiddle_re[k]*of_im[k] + twiddle_im[k]*of_re[k];
        out_re[k] = ef_re[k] + t_re;
        out_im[k] = ef_im[k] + t_im;
        out_re[k+half] = ef_re[k] - t_re;
        out_im[k+half] = ef_im[k] - t_im;
    }
}

void compute_magnitude(float* re, float* im, float* mag, int n) {
    for (int i = 0; i < n/2; i++) mag[i] = sqrtf(re[i]*re[i]+im[i]*im[i])/n;
}

float detect_f0(float* mag, int n) {
    float max_amp = 0;
    int max_idx = 0;
    int min_bin = (int)(60.0f / FREQ_RES);
    int max_bin = (int)(600.0f / FREQ_RES);
    for (int i = min_bin; i < max_bin && i < n; i++) {
        if (mag[i] > max_amp) { max_amp = mag[i]; max_idx = i; }
    }
    return max_idx * FREQ_RES;
}

float detect_breathing_rate(float* mag, int n) {
    float energy_low = 0;
    int bin_8 = (int)(0.13f / FREQ_RES);
    int bin_40 = (int)(0.67f / FREQ_RES);
    for (int i = bin_8; i < bin_40 && i < n; i++) energy_low += mag[i];
    return energy_low;
}

int detect_cough(float* mag, int n, float* confidence) {
    float energy_100_1000 = 0;
    float energy_total = 0;
    int bin_100 = (int)(100.0f / FREQ_RES);
    int bin_1000 = (int)(1000.0f / FREQ_RES);
    for (int i = 0; i < n; i++) {
        energy_total += mag[i];
        if (i >= bin_100 && i <= bin_1000) energy_100_1000 += mag[i];
    }
    float ratio = (energy_total > 1e-10f) ? energy_100_1000 / energy_total : 0;
    *confidence = ratio;
    return (ratio > 0.7f) ? 1 : 0;
}

void extract_mfcc(float* mag, int n, feature_t* feat) {
    for (int m = 0; m < MFCC_FEATURES; m++) {
        float sum = 0;
        for (int k = 0; k < n; k++) {
            if (k < N_FILTERS) sum += mag[k] * cosf(M_PI * m * (2*k+1) / (2*N_FILTERS));
        }
        feat->mfcc[m] = (sum > 1e-10f) ? logf(fabsf(sum)) : 0;
    }
    feat->energy = 0;
    for (int i = 0; i < n; i++) feat->energy += mag[i] * mag[i];
    feat->spectral_centroid = 0;
    float sum_mag = 0;
    for (int i = 0; i < n; i++) { feat->spectral_centroid += i * mag[i]; sum_mag += mag[i]; }
    feat->spectral_centroid = (sum_mag > 1e-10f) ? feat->spectral_centroid / sum_mag * FREQ_RES : 0;
}

int classify(feature_t* feat) {
    float scores[ML_CLASSES] = {0};
    for (int c = 0; c < ML_CLASSES; c++)
        for (int i = 0; i < MFCC_FEATURES; i++) scores[c] += feat->mfcc[i] * 0.01f;
    int best = 0;
    for (int c = 1; c < ML_CLASSES; c++) if (scores[c] > scores[best]) best = c;
    return best;
}

void send_ble(result_t* res) {
    uint8_t buf[16];
    memcpy(buf, res, sizeof(result_t) < 16 ? sizeof(result_t) : 16);
}

int main(void) {
    fft_init();
    float audio_buffer[FRAME_SAMPLES];
    while (1) {
        fft_result_t fft_res;
        memset(fft_res.im, 0, FFT_SIZE * sizeof(float));
        memcpy(fft_res.re, audio_buffer, FRAME_SAMPLES * sizeof(float));
        fft(fft_res.re, fft_res.im, fft_res.re, fft_res.im, FFT_SIZE);
        compute_magnitude(fft_res.re, fft_res.im, fft_res.magnitude, FFT_SIZE);
        feature_t feat;
        extract_mfcc(fft_res.magnitude, FFT_SIZE/2, &feat);
        result_t result;
        result.f0_hz = detect_f0(fft_res.magnitude, FFT_SIZE/2);
        result.breath_rate = detect_breathing_rate(fft_res.magnitude, FFT_SIZE/2);
        result.cough_detected = detect_cough(fft_res.magnitude, FFT_SIZE/2, &result.cough_confidence);
        result.health_class = classify(&feat);
        send_ble(&result);
    }
    return 0;
}
