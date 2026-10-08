import os

BASE = "/home/user/The-competition-is-for-5-applications-all-6-are-accepted"

FIRMWARE = {
    "01_teplovid-4": """#include <stdint.h>
#include <math.h>

#define IMG_W 640
#define IMG_H 512
#define NETD_MK 50
#define T_BG_C 15.0
#define T_TAR_C 32.0

static uint16_t frame[IMG_H][IMG_W];
static float therm[IMG_H][IMG_W];
static float stabil_buf[8];

float adc_to_temp_c(uint16_t adc) {
    return (float)adc * 0.02f;
}

float calc_contrast(float t_obj, float t_bg) {
    float dt = fabsf(t_obj - t_bg);
    return dt / (NETD_MK * 0.001f);
}

void gyro_compensate(float gyro_x, float gyro_y, float *dx, float *dy) {
    static float prev_gx = 0, prev_gy = 0;
    float dgx = gyro_x - prev_gx;
    float dgy = gyro_y - prev_gy;
    prev_gx = gyro_x;
    prev_gy = gyro_y;
    for (int i = 0; i < 7; i++) {
        stabil_buf[i] = stabil_buf[i + 1];
    }
    stabil_buf[7] = dgx;
    float sum = 0;
    for (int i = 0; i < 8; i++) sum += stabil_buf[i];
    *dx = sum / 8.0f;
    *dy = dgy;
}

void detect_hotspots(float threshold_c) {
    for (int y = 2; y < IMG_H - 2; y++) {
        for (int x = 2; x < IMG_W - 2; x++) {
            float local_avg = 0;
            for (int dy = -2; dy <= 2; dy++) {
                for (int dx = -2; dx <= 2; dx++) {
                    local_avg += therm[y + dy][x + dx];
                }
            }
            local_avg /= 25.0f;
            float diff = therm[y][x] - local_avg;
            if (diff > threshold_c) {
                frame[y][x] = 0xFFFF;
            }
        }
    }
}

float lidar_calc_range(float P_tx, float rho, float d_rx, float NEP) {
    float A_rx = 3.14159f * (d_rx * 0.5f) * (d_rx * 0.5f);
    return sqrtf(P_tx * rho * A_rx / (3.14159f * NEP * 10.0f));
}

void spray_drift_correct(float wind_ms, float temp_c, float rh_pct, float *factor) {
    float evap = 0.01f * (temp_c - 20.0f) * (1.0f - rh_pct * 0.01f);
    float drift = 0.05f * wind_ms * wind_ms;
    *factor = 1.0f - drift - evap;
    if (*factor < 0.3f) *factor = 0.3f;
}

int main(void) {
    float contrast = calc_contrast(T_TAR_C, T_BG_C);
    float range = lidar_calc_range(75.0f, 0.3f, 0.025f, 1e-12f);
    float dx, dy;
    gyro_compensate(0.01f, 0.02f, &dx, &dy);
    float spray;
    spray_drift_correct(5.0f, 25.0f, 60.0f, &spray);
    detect_hotspots(2.0f);
    return 0;
}
""",
    "02_spektrobio-2": """#include <stdint.h>
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
""",
    "03_lamp-dnk-ekspress": """#include <stdint.h>
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
""",
    "04_zreniebpila-5": """#include <stdint.h>
#include <math.h>

#define IMG_W 1920
#define IMG_H 1080
#define GRID_SIZE 13
#define N_BOXES 5
#define N_CLASSES 80
#define CONF_THRESH 0.5f
#define IOU_THRESH 0.45f

typedef struct {
    float x, y, w, h, conf;
    int cls;
} Detection;

static Detection detections[GRID_SIZE * GRID_SIZE * N_BOXES];

float sigmoid_f(float x) {
    return 1.0f / (1.0f + expf(-x));
}

void yolo_decode(float *raw, Detection *out, int *count) {
    *count = 0;
    for (int j = 0; j < GRID_SIZE; j++) {
        for (int i = 0; i < GRID_SIZE; i++) {
            for (int b = 0; b < N_BOXES; b++) {
                int idx = ((j * GRID_SIZE + i) * N_BOXES + b) * (5 + N_CLASSES);
                float conf = sigmoid_f(raw[idx + 4]);
                if (conf > CONF_THRESH) {
                    out[*count].x = sigmoid_f(raw[idx]);
                    out[*count].y = sigmoid_f(raw[idx + 1]);
                    out[*count].w = raw[idx + 2];
                    out[*count].h = raw[idx + 3];
                    out[*count].conf = conf;
                    float max_p = -1;
                    int max_c = 0;
                    for (int c = 0; c < N_CLASSES; c++) {
                        float p = sigmoid_f(raw[idx + 5 + c]);
                        if (p > max_p) { max_p = p; max_c = c; }
                    }
                    out[*count].cls = max_c;
                    (*count)++;
                }
            }
        }
    }
}

float calc_iou(Detection *a, Detection *b) {
    float x1 = fmaxf(a->x - a->w * 0.5f, b->x - b->w * 0.5f);
    float y1 = fmaxf(a->y - a->h * 0.5f, b->y - b->h * 0.5f);
    float x2 = fminf(a->x + a->w * 0.5f, b->x + b->w * 0.5f);
    float y2 = fminf(a->y + a->h * 0.5f, b->y + b->h * 0.5f);
    float inter = fmaxf(0, x2 - x1) * fmaxf(0, y2 - y1);
    float area_a = a->w * a->h;
    float area_b = b->w * b->h;
    return inter / (area_a + area_b - inter + 1e-6f);
}

void nms(Detection *dets, int n, Detection *result, int *result_count) {
    int suppressed[200] = {0};
    *result_count = 0;
    for (int i = 0; i < n; i++) {
        if (suppressed[i]) continue;
        result[(*result_count)++] = dets[i];
        for (int j = i + 1; j < n; j++) {
            if (suppressed[j]) continue;
            if (dets[i].cls == dets[j].cls && calc_iou(&dets[i], &dets[j]) > IOU_THRESH) {
                suppressed[j] = 1;
            }
        }
    }
}

void ensemble_vote(Detection *det_a, int na, Detection *det_b, int nb, Detection *out, int *out_count) {
    *out_count = 0;
    for (int i = 0; i < na; i++) {
        for (int j = 0; j < nb; j++) {
            if (det_a[i].cls == det_b[j].cls && calc_iou(&det_a[i], &det_b[j]) > 0.3f) {
                out[*out_count] = det_a[i];
                out[*out_count].conf = (det_a[i].conf + det_b[j].conf) * 0.5f;
                (*out_count)++;
                break;
            }
        }
    }
}

void stereo_depth(float disparity_px, float baseline_m, float f_px, float *depth_m) {
    *depth_m = baseline_m * f_px / (disparity_px + 1e-6f);
}

void canny_sobel(uint8_t *in, float *out_mag, int w, int h) {
    for (int y = 1; y < h - 1; y++) {
        for (int x = 1; x < w - 1; x++) {
            int gx = -in[(y-1)*w+x-1] + in[(y-1)*w+x+1]
                   - 2*in[y*w+x-1] + 2*in[y*w+x+1]
                   - in[(y+1)*w+x-1] + in[(y+1)*w+x+1];
            int gy = -in[(y-1)*w+x-1] - 2*in[(y-1)*w+x] - in[(y-1)*w+x+1]
                   + in[(y+1)*w+x-1] + 2*in[(y+1)*w+x] + in[(y+1)*w+x+1];
            out_mag[y*w+x] = sqrtf((float)(gx*gx + gy*gy));
        }
    }
}

int main(void) {
    float raw[845] = {0};
    Detection det[100];
    int count;
    yolo_decode(raw, det, &count);
    Detection nms_out[100];
    int nms_count;
    nms(det, count, nms_out, &nms_count);
    float depth;
    stereo_depth(10.0f, 0.12f, 800.0f, &depth);
    return 0;
}
""",
    "05_autopilot-5": """#include <stdint.h>
#include <math.h>

#define MAP_SIZE 100
#define N_LIDAR 360
#define MAX_PATH 500
#define V_MAX 3.0f
#define A_MAX 2.0f
#define W_MAX 1.5f

static float map_grid[MAP_SIZE][MAP_SIZE];
static float pose_x = 0, pose_y = 0, pose_theta = 0;
static float imu_gyro_z = 0;
static float odom_v = 0;

typedef struct { float x; float y; } Point;

void slam_update(float *ranges, float *angles, int n) {
    for (int i = 0; i < n; i++) {
        if (ranges[i] <= 0 || ranges[i] > 30.0f) continue;
        float wx = pose_x + ranges[i] * cosf(pose_theta + angles[i]);
        float wy = pose_y + ranges[i] * sinf(pose_theta + angles[i]);
        int gx = (int)(wx * 10) + MAP_SIZE / 2;
        int gy = (int)(wy * 10) + MAP_SIZE / 2;
        if (gx >= 0 && gx < MAP_SIZE && gy >= 0 && gy < MAP_SIZE) {
            map_grid[gy][gx] += 0.1f;
            if (map_grid[gy][gx] > 1.0f) map_grid[gy][gx] = 1.0f;
        }
    }
}

void slam_odometry(float v, float omega, float dt) {
    pose_x += v * cosf(pose_theta) * dt;
    pose_y += v * sinf(pose_theta) * dt;
    pose_theta += omega * dt;
    while (pose_theta > 3.14159f) pose_theta -= 6.28318f;
    while (pose_theta < -3.14159f) pose_theta += 6.28318f;
}

float heuristic_euclid(int x1, int y1, int x2, int y2) {
    return sqrtf((float)((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1)));
}

int astar_plan(int sx, int sy, int gx, int gy, Point *path) {
    float g_score[MAP_SIZE][MAP_SIZE];
    float f_score[MAP_SIZE][MAP_SIZE];
    int closed[MAP_SIZE][MAP_SIZE] = {{0}};
    for (int i = 0; i < MAP_SIZE; i++)
        for (int j = 0; j < MAP_SIZE; j++)
            g_score[i][j] = 1e9f;
    g_score[sy][sx] = 0;
    f_score[sy][sx] = heuristic_euclid(sx, sy, gx, gy);
    int cx = sx, cy = sy;
    int steps = 0;
    int dx[] = {-1, 1, 0, 0, -1, 1, -1, 1};
    int dy[] = {0, 0, -1, 1, -1, -1, 1, 1};
    while ((cx != gx || cy != gy) && steps < 10000) {
        closed[cy][cx] = 1;
        float best_f = 1e9f;
        int best_x = cx, best_y = cy;
        for (int d = 0; d < 8; d++) {
            int nx = cx + dx[d], ny = cy + dy[d];
            if (nx < 0 || nx >= MAP_SIZE || ny < 0 || ny >= MAP_SIZE) continue;
            if (closed[ny][nx] || map_grid[ny][nx] > 0.8f) continue;
            float cost = (d < 4) ? 1.0f : 1.414f;
            float ng = g_score[cy][cx] + cost;
            if (ng < g_score[ny][nx]) {
                g_score[ny][nx] = ng;
                f_score[ny][nx] = ng + heuristic_euclid(nx, ny, gx, gy);
            }
            if (f_score[ny][nx] < best_f) {
                best_f = f_score[ny][nx];
                best_x = nx;
                best_y = ny;
            }
        }
        cx = best_x;
        cy = best_y;
        if (steps < MAX_PATH) {
            path[steps].x = (float)cx;
            path[steps].y = (float)cy;
        }
        steps++;
    }
    return steps;
}

float dwa_select_v(float v_curr, float v_desired, float dt) {
    float v_new = v_curr + A_MAX * dt;
    if (v_new > v_desired) v_new = v_desired;
    if (v_new > V_MAX) v_new = V_MAX;
    return v_new;
}

float dwa_select_w(float theta_err, float dt) {
    float w = theta_err * 2.0f;
    if (w > W_MAX) w = W_MAX;
    if (w < -W_MAX) w = -W_MAX;
    return w;
}

float pid_heading(float theta_target, float Kp, float Kd) {
    float err = theta_target - pose_theta;
    while (err > 3.14159f) err -= 6.28318f;
    while (err < -3.14159f) err += 6.28318f;
    static float prev_err = 0;
    float steer = Kp * err + Kd * (err - prev_err);
    prev_err = err;
    return steer;
}

void can_send(uint32_t id, uint8_t *data, uint8_t len) {
    (void)id;
    (void)data;
    (void)len;
}

int main(void) {
    float ranges[360];
    float angles[360];
    for (int i = 0; i < 360; i++) {
        ranges[i] = 10.0f;
        angles[i] = i * 0.01745f;
    }
    slam_update(ranges, angles, 360);
    slam_odometry(1.0f, 0.1f, 0.1f);
    Point path[MAX_PATH];
    int len = astar_plan(0, 0, 50, 50, path);
    float v = dwa_select_v(0, 2.0f, 0.1f);
    float w = dwa_select_w(0.5f, 0.1f);
    float steer = pid_heading(1.0f, 2.0f, 0.5f);
    return 0;
}
""",
    "06_akustikmon-6": """#include <stdint.h>
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
    float mel_energy[40] = {0};
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
""",
}

for slug, code in FIRMWARE.items():
    path = os.path.join(BASE, slug, "04_firmware", "firmware.c")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(code.lstrip())
    print(f"  {slug}/firmware.c: {len(code)} chars")

print("\nDone: 6 firmware.c")