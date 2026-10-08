#include <stdint.h>
#include <math.h>

#define FS 44100
#define N_FFT 4096
#define N_MICS 4
#define FRAME_MS 25
#define HOP_MS 10
#define FRAME_SAMPLES (FS * FRAME_MS / 1000)
#define HOP_SAMPLES (FS * HOP_MS / 1000)
#define N_MEL 40
#define N_MFCC 13

static float audio[N_FFT];
static float fft_re[N_FFT];
static float fft_im[N_FFT];
static float mfcc_out[N_MFCC];

void hpf_4th(float *in, float *out, int n, float fc) {
    float rc = 1.0f / (6.28318f * fc);
    float dt = 1.0f / (float)FS;
    float alpha = rc / (rc + dt);
    float prev = 0;
    for (int i = 0; i < n; i++) {
        out[i] = alpha * (prev + in[i] - (i > 0 ? in[i-1] : 0));
        prev = out[i];
    }
}

void fft_radix2(float *re, float *im, int n) {
    for (int s = 1; s <= 12; s++) {
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

float hz_to_mel(float hz) { return 2595.0f * log10f(1.0f + hz / 700.0f); }
float mel_to_hz(float m) { return 700.0f * (powf(10.0f, m / 2595.0f) - 1.0f); }

void mfcc_compute(float *power_spectrum, int n_fft, float *out) {
    float mel_low = hz_to_mel(50.0f);
    float mel_high = hz_to_mel(4000.0f);
    float mel_points[42];
    for (int i = 0; i < 42; i++)
        mel_points[i] = mel_to_hz(mel_low + i * (mel_high - mel_low) / 41.0f);
    float mel_energy[40];
    for (int i = 0; i < 40; i++) mel_energy[i] = 0;
    for (int m = 0; m < N_MEL; m++) {
        int f_lo = (int)(mel_points[m] * n_fft / FS);
        int f_hi = (int)(mel_points[m+2] * n_fft / FS);
        if (f_lo < 0) f_lo = 0;
        if (f_hi > n_fft / 2) f_hi = n_fft / 2;
        for (int f = f_lo; f < f_hi; f++)
            mel_energy[m] += power_spectrum[f];
    }
    for (int c = 0; c < N_MFCC; c++) {
        out[c] = 0;
        for (int m = 0; m < N_MEL; m++)
            out[c] += logf(mel_energy[m] + 1e-10f) * cosf(3.14159f * c * (2*m+1) / (2.0f*N_MEL));
    }
}

float spectral_kurtosis(float *mag, int n) {
    float mean = 0, var = 0, kurt = 0;
    for (int i = 0; i < n; i++) mean += mag[i];
    mean /= n;
    for (int i = 0; i < n; i++) var += (mag[i] - mean) * (mag[i] - mean);
    var /= n;
    float std = sqrtf(var);
    for (int i = 0; i < n; i++) {
        float z = (mag[i] - mean) / (std + 1e-10f);
        kurt += z * z * z * z;
    }
    return kurt / n;
}

int vad_detect(float *frame, int n, float thresh_db) {
    float energy = 0;
    for (int i = 0; i < n; i++) energy += frame[i] * frame[i];
    float edb = 10.0f * log10f(energy / n + 1e-20f);
    return edb > thresh_db ? 1 : 0;
}

void beamform_4mic(float mic[N_MICS][N_FFT], float theta_deg, float d, float *out, int n) {
    float theta = theta_deg * 0.01745f;
    for (int i = 0; i < n; i++) {
        float sum = 0;
        for (int m = 0; m < N_MICS; m++) {
            float delay = m * d * sinf(theta) / 343.0f;
            int delay_samp = (int)(delay * FS);
            int idx = i - delay_samp;
            if (idx >= 0 && idx < n) sum += mic[m][idx];
        }
        out[i] = sum / N_MICS;
    }
}

int classify_acoustic(float kurt, float centroid_hz, float energy_db) {
    if (energy_db < -40) return 0;
    if (kurt > 10.0f && centroid_hz > 500) return 3;
    if (centroid_hz > 100 && centroid_hz < 400) return 1;
    if (centroid_hz > 200 && centroid_hz < 3000) return 2;
    return 4;
}

int main(void) {
    for (int i = 0; i < N_FFT; i++) {
        audio[i] = 0.001f * sinf(6.28318f * 1000.0f * i / FS);
        fft_re[i] = audio[i];
        fft_im[i] = 0;
    }
    fft_radix2(fft_re, fft_im, N_FFT);
    float power[2048];
    for (int i = 0; i < 2048; i++)
        power[i] = fft_re[i]*fft_re[i] + fft_im[i]*fft_im[i];
    mfcc_compute(power, N_FFT, mfcc_out);
    float kurt = spectral_kurtosis(power, 2048);
    int vad = vad_detect(audio, FRAME_SAMPLES, -40.0f);
    int cls = classify_acoustic(kurt, 1500.0f, -20.0f);
    return 0;
}