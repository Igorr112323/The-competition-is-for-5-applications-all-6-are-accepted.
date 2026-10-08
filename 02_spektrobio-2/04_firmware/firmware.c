#include <stdint.h>
#include <math.h>

#define N_POINTS 256
#define L_PATH_M 0.10
#define LAMBDA_MIN_UM 3.0
#define LAMBDA_MAX_UM 12.0

static float spectrum[N_POINTS];
static float absorbance[N_POINTS];
static float reference[N_POINTS];

struct Analyte {
    float lambda_peak_um;
    float cross_section_m2;
    float threshold_ppb;
};

static struct Analyte analytes[4] = {
    {10.3f, 2.1e-20f, 500.0f},
    {5.26f, 6.8e-21f, 25.0f},
    {7.73f, 3.5e-21f, 10.0f},
    {3.31f, 8.6e-21f, 5000.0f}
};

float beer_lambert_tau(float sigma, float C_ppb, float L) {
    float C_mol = C_ppb * 1e-9f * 40.9f;
    return expf(-sigma * C_mol * L);
}

void calc_absorbance_array(void) {
    for (int i = 0; i < N_POINTS; i++) {
        if (reference[i] > 0 && spectrum[i] > 0) {
            absorbance[i] = -log10f(spectrum[i] / reference[i]);
        }
    }
}

void mnk_calibrate(float *x, float *y, int n, float *slope, float *intercept, float *R2) {
    float sx = 0, sy = 0, sxy = 0, sx2 = 0;
    for (int i = 0; i < n; i++) {
        sx += x[i];
        sy += y[i];
        sxy += x[i] * y[i];
        sx2 += x[i] * x[i];
    }
    float denom = n * sx2 - sx * sx;
    *slope = (n * sxy - sx * sy) / denom;
    *intercept = (sy * sx2 - sx * sxy) / denom;
    float y_mean = sy / n;
    float ss_tot = 0, ss_res = 0;
    for (int i = 0; i < n; i++) {
        float yp = (*slope) * x[i] + (*intercept);
        ss_res += (y[i] - yp) * (y[i] - yp);
        ss_tot += (y[i] - y_mean) * (y[i] - y_mean);
    }
    *R2 = (ss_tot > 0) ? (1.0f - ss_res / ss_tot) : 0;
}

void chopper_control(float freq_hz) {
    float period_us = 1000000.0f / freq_hz;
    float duty = period_us * 0.5f;
    (void)duty;
}

void fft_radix2(float *re, float *im, int n) {
    for (int s = 1; s <= 8; s++) {
        int m = 1 << s;
        float wm_r = cosf(6.28318f / m);
        float wm_i = -sinf(6.28318f / m);
        for (int k = 0; k < n; k += m) {
            float w_r = 1, w_i = 0;
            for (int j = 0; j < m / 2; j++) {
                int i1 = k + j;
                int i2 = k + j + m / 2;
                float t_r = w_r * re[i2] - w_i * im[i2];
                float t_i = w_r * im[i2] + w_i * re[i2];
                re[i2] = re[i1] - t_r;
                im[i2] = im[i1] - t_i;
                re[i1] += t_r;
                im[i1] += t_i;
                float nw_r = w_r * wm_r - w_i * wm_i;
                w_i = w_r * wm_i + w_i * wm_r;
                w_r = nw_r;
            }
        }
    }
}

int main(void) {
    chopper_control(10.0f);
    float tau = beer_lambert_tau(analytes[0].cross_section_m2, analytes[0].threshold_ppb, L_PATH_M);
    calc_absorbance_array();
    float slope, intercept, R2;
    float cal_x[5] = {100, 250, 500, 750, 1000};
    float cal_y[5] = {0.001f, 0.003f, 0.006f, 0.009f, 0.012f};
    mnk_calibrate(cal_x, cal_y, 5, &slope, &intercept, &R2);
    return 0;
}