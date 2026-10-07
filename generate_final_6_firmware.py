import os
BASE = "/home/user/The-competition-is-for-5-applications-all-6-are-accepted."

FIRMWARE = {
    "01_teplovid-4": """#include <stdint.h>
#include <math.h>
#include <string.h>

#define FRAME_W 160
#define FRAME_H 120
#define GRID_SIZE 32
#define DETECT_THRESHOLD 5
#define TRACK_MAX 20
#define YOLO_CLASSES 2

typedef struct {
    uint16_t thermal[FRAME_H][FRAME_W];
    float imu_accel[3];
    uint32_t timestamp;
} frame_t;

typedef struct {
    float x, y, w, h;
    float confidence;
    uint8_t class_id;
    uint8_t active;
    uint32_t last_seen;
} detection_t;

typedef struct {
    float x, y;
    float vx, vy;
    uint32_t id;
    uint32_t last_update;
} track_t;

static detection_t detections[TRACK_MAX];
static track_t tracks[TRACK_MAX];
static uint32_t track_counter = 0;
static uint16_t background[FRAME_H][FRAME_W];
static float grid_mean[GRID_SIZE][GRID_SIZE];
static float grid_var[GRID_SIZE][GRID_SIZE];

void background_subtract(frame_t* f) {
    for (int y = 0; y < FRAME_H; y++) {
        for (int x = 0; x < FRAME_W; x++) {
            float alpha = 0.01f;
            background[y][x] = (uint16_t)((1-alpha) * background[y][x] + alpha * f->thermal[y][x]);
        }
    }
}

float compute_grid_statistics(frame_t* f, int gx, int gy) {
    int cell_w = FRAME_W / GRID_SIZE;
    int cell_h = FRAME_H / GRID_SIZE;
    float sum = 0;
    int count = 0;
    for (int y = gy*cell_h; y < (gy+1)*cell_h; y++) {
        for (int x = gx*cell_w; x < (gx+1)*cell_w; x++) {
            float diff = (float)f->thermal[y][x] - (float)background[y][x];
            sum += diff * diff;
            count++;
        }
    }
    return sqrtf(sum / count);
}

int detect_hotspots(frame_t* f, detection_t* dets, int max_dets) {
    int n = 0;
    int cell_w = FRAME_W / GRID_SIZE;
    int cell_h = FRAME_H / GRID_SIZE;
    for (int gy = 0; gy < GRID_SIZE && n < max_dets; gy++) {
        for (int gx = 0; gx < GRID_SIZE && n < max_dets; gx++) {
            float energy = compute_grid_statistics(f, gx, gy);
            if (energy > DETECT_THRESHOLD) {
                dets[n].x = gx * cell_w + cell_w/2;
                dets[n].y = gy * cell_h + cell_h/2;
                dets[n].w = cell_w;
                dets[n].h = cell_h;
                dets[n].confidence = energy / 100.0f;
                dets[n].class_id = 0;
                dets[n].active = 1;
                n++;
            }
        }
    }
    return n;
}

void track_objects(detection_t* dets, int n_dets, track_t* trks, int* n_trks) {
    for (int i = 0; i < n_dets; i++) {
        float min_dist = 1e9f;
        int best = -1;
        for (int j = 0; j < *n_trks; j++) {
            float dx = dets[i].x - trks[j].x;
            float dy = dets[i].y - trks[j].y;
            float dist = sqrtf(dx*dx + dy*dy);
            if (dist < min_dist && dist < 50) {
                min_dist = dist;
                best = j;
            }
        }
        if (best >= 0) {
            trks[best].vx = dets[i].x - trks[best].x;
            trks[best].vy = dets[i].y - trks[best].y;
            trks[best].x = dets[i].x;
            trks[best].y = dets[i].y;
            trks[best].last_update = dets[i].last_seen;
        } else if (*n_trks < TRACK_MAX) {
            trks[*n_trks].x = dets[i].x;
            trks[*n_trks].y = dets[i].y;
            trks[*n_trks].vx = 0;
            trks[*n_trks].vy = 0;
            trks[*n_trks].id = track_counter++;
            trks[*n_trks].last_update = dets[i].last_seen;
            (*n_trks)++;
        }
    }
}

void compensate_vibration(frame_t* f, float gyro_x, float gyro_y, float dt) {
    int shift_x = (int)(gyro_x * dt * FRAME_W / 57.0f);
    int shift_y = (int)(gyro_y * dt * FRAME_H / 44.0f);
    if (abs(shift_x) > 0 || abs(shift_y) > 0) {
        for (int y = 0; y < FRAME_H; y++) {
            for (int x = 0; x < FRAME_W; x++) {
                int sx = x - shift_x;
                int sy = y - shift_y;
                if (sx >= 0 && sx < FRAME_W && sy >= 0 && sy < FRAME_H)
                    f->thermal[y][x] = f->thermal[sy][sx];
            }
        }
    }
}

void send_ble(track_t* trks, int n) {
    uint8_t buf[244];
    int len = 0;
    for (int i = 0; i < n && len < 240; i++) {
        memcpy(buf + len, &trks[i], sizeof(track_t));
        len += sizeof(track_t);
    }
}

int main(void) {
    frame_t frame;
    detection_t dets[TRACK_MAX];
    int n_trks = 0;
    memset(background, 0, sizeof(background));
    while (1) {
        background_subtract(&frame);
        int n_dets = detect_hotspots(&frame, dets, TRACK_MAX);
        track_objects(dets, n_dets, tracks, &n_trks);
        send_ble(tracks, n_trks);
    }
    return 0;
}
""",

    "02_spektrobio-2": """#include <stdint.h>
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
""",

    "03_lamp-dnk-ekspress": """#include <stdint.h>
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
""",

    "04_zreniebpila-5": """#include <stdint.h>
#include <math.h>
#include <string.h>

#define IMG_W 1280
#define IMG_H 800
#define BLOCK_SIZE 8
#define DISPARITY_RANGE 64
#define FOCAL_PX 800
#define BASELINE_MM 60
#define CONFIDENCE_THRESHOLD 20
#define YOLO_CLASSES 2
#define MAX_DETECTIONS 50

typedef struct {
    uint8_t left[IMG_H][IMG_W];
    uint8_t right[IMG_H][IMG_W];
    float imu_gyro[3];
    uint32_t timestamp;
} stereo_frame_t;

typedef struct {
    float x, y, w, h;
    float confidence;
    uint8_t class_id;
    float depth_m;
} detection_t;

typedef struct {
    float x, y, vx, vy;
    uint32_t id;
    uint32_t last_seen;
} track_t;

static float depth_map[IMG_H / BLOCK_SIZE][IMG_W / BLOCK_SIZE];
static track_t tracks[MAX_DETECTIONS];
static uint32_t track_id_counter = 0;

void stereo_match_block(stereo_frame_t* f, int bx, int by) {
    int best_d = 0;
    int best_sad = INT32_MAX;
    int x0 = bx * BLOCK_SIZE;
    int y0 = by * BLOCK_SIZE;
    for (int d = 0; d < DISPARITY_RANGE; d++) {
        int sad = 0;
        for (int dy = 0; dy < BLOCK_SIZE; dy++) {
            for (int dx = 0; dx < BLOCK_SIZE; dx++) {
                int lx = x0 + dx;
                int ly = y0 + dy;
                int rx = lx - d;
                if (rx >= 0 && rx < IMG_W)
                    sad += abs(f->left[ly][lx] - f->right[ly][rx]);
                else
                    sad += 255;
            }
        }
        if (sad < best_sad) {
            best_sad = sad;
            best_d = d;
        }
    }
    depth_map[by][bx] = (best_d > 2) ? (float)BASELINE_MM * FOCAL_PX / best_d / 1000.0f : 0;
}

void compute_depth(stereo_frame_t* f) {
    for (int by = 0; by < IMG_H/BLOCK_SIZE; by++)
        for (int bx = 0; bx < IMG_W/BLOCK_SIZE; bx++)
            stereo_match_block(f, bx, by);
}

float sobel_energy(stereo_frame_t* f, int cx, int cy, int radius) {
    float energy = 0;
    for (int y = cy-radius; y <= cy+radius; y++) {
        for (int x = cx-radius; x <= cx+radius; x++) {
            if (x > 0 && x < IMG_W-1 && y > 0 && y < IMG_H-1) {
                float gx = f->left[y][x+1] - f->left[y][x-1];
                float gy = f->left[y+1][x] - f->left[y-1][x];
                energy += gx*gx + gy*gy;
            }
        }
    }
    return energy;
}

int detect_objects(stereo_frame_t* f, detection_t* dets) {
    int n = 0;
    int cell = 40;
    for (int cy = cell; cy < IMG_H-cell && n < MAX_DETECTIONS; cy += cell) {
        for (int cx = cell; cx < IMG_W-cell && n < MAX_DETECTIONS; cx += cell) {
            float energy = sobel_energy(f, cx, cy, 20);
            if (energy > 100000) {
                int bx = cx / BLOCK_SIZE;
                int by = cy / BLOCK_SIZE;
                if (bx < IMG_W/BLOCK_SIZE && by < IMG_H/BLOCK_SIZE) {
                    dets[n].x = cx;
                    dets[n].y = cy;
                    dets[n].w = cell;
                    dets[n].h = cell;
                    dets[n].depth_m = depth_map[by][bx];
                    dets[n].confidence = energy / 1000000.0f;
                    dets[n].class_id = (energy > 500000) ? 1 : 0;
                    n++;
                }
            }
        }
    }
    return n;
}

void stabilize_frame(stereo_frame_t* f, float gyro_x, float gyro_y, float dt) {
    int shift_x = (int)(gyro_x * dt * IMG_W / 80.0f);
    int shift_y = (int)(gyro_y * dt * IMG_H / 60.0f);
    if (abs(shift_x) > 0 || abs(shift_y) > 0) {
        for (int y = 0; y < IMG_H; y++) {
            for (int x = 0; x < IMG_W; x++) {
                int sx = x - shift_x;
                int sy = y - shift_y;
                if (sx >= 0 && sx < IMG_W && sy >= 0 && sy < IMG_H)
                    f->left[y][x] = f->left[sy][sx];
            }
        }
    }
}

void send_detections(detection_t* dets, int n) {
    uint8_t buf[244];
    int len = n * sizeof(detection_t) < 244 ? n * sizeof(detection_t) : 244;
    memcpy(buf, dets, len);
}

int main(void) {
    stereo_frame_t frame;
    detection_t dets[MAX_DETECTIONS];
    while (1) {
        stabilize_frame(&frame, frame.imu_gyro[0], frame.imu_gyro[1], 0.033f);
        compute_depth(&frame);
        int n = detect_objects(&frame, dets);
        send_detections(dets, n);
    }
    return 0;
}
""",

    "05_autopilot-5": """#include <stdint.h>
#include <math.h>
#include <string.h>

#define GRID_SIZE 1000
#define GRID_RES 0.1f
#define LIDAR_RANGE 12.0f
#define LIDAR_POINTS 360
#define PATH_MAX 500
#define WP_MAX 50
#define PID_DIM 3

typedef struct {
    float x, y, theta;
    float vx, vy, omega;
} pose_t;

typedef struct {
    float distances[LIDAR_POINTS];
    uint32_t timestamp;
} lidar_scan_t;

typedef struct {
    float x, y;
} point_t;

typedef struct {
    float kp, ki, kd;
    float integral;
    float prev_error;
} pid_t;

static uint8_t grid[GRID_SIZE][GRID_SIZE];
static pose_t current_pose;
static point_t waypoints[WP_MAX];
static int n_waypoints = 0;
static pid_t pid[PID_DIM];

void pid_init(pid_t* p, float kp, float ki, float kd) {
    p->kp = kp; p->ki = ki; p->kd = kd;
    p->integral = 0; p->prev_error = 0;
}

float pid_update(pid_t* p, float error, float dt) {
    p->integral += error * dt;
    float derivative = (error - p->prev_error) / dt;
    p->prev_error = error;
    float output = p->kp * error + p->ki * p->integral + p->kd * derivative;
    return output;
}

void update_grid(lidar_scan_t* scan) {
    for (int i = 0; i < LIDAR_POINTS; i++) {
        float angle = current_pose.theta + i * 2.0f * M_PI / LIDAR_POINTS;
        float dist = scan->distances[i];
        if (dist > 0.1f && dist < LIDAR_RANGE) {
            float ox = current_pose.x + dist * cosf(angle);
            float oy = current_pose.y + dist * sinf(angle);
            int gx = (int)(ox / GRID_RES) + GRID_SIZE/2;
            int gy = (int)(oy / GRID_RES) + GRID_SIZE/2;
            if (gx >= 0 && gx < GRID_SIZE && gy >= 0 && gy < GRID_SIZE)
                grid[gx][gy] = 255;
        }
    }
}

int astar(int sx, int sy, int ex, int ey, point_t* path, int* path_len) {
    float g[GRID_SIZE][GRID_SIZE];
    float f[GRID_SIZE][GRID_SIZE];
    uint8_t closed[GRID_SIZE][GRID_SIZE];
    memset(closed, 0, sizeof(closed));
    for (int i = 0; i < GRID_SIZE; i++)
        for (int j = 0; j < GRID_SIZE; j++)
            g[i][j] = 1e9f;
    g[sx][sy] = 0;
    float h = sqrtf((ex-sx)*(ex-sx)+(ey-sy)*(ey-sy));
    f[sx][sy] = h;
    int cx = sx, cy = sy;
    int idx = 0;
    for (int iter = 0; iter < 50000; iter++) {
        if (cx == ex && cy == ey) { *path_len = idx; return 1; }
        closed[cx][cy] = 1;
        int dx[] = {-1,0,1,0,-1,1,1,-1};
        int dy[] = {0,1,0,-1,1,1,-1,-1};
        for (int d = 0; d < 8; d++) {
            int nx = cx+dx[d], ny = cy+dy[d];
            if (nx<0||nx>=GRID_SIZE||ny<0||ny>=GRID_SIZE||closed[nx][ny]) continue;
            if (grid[nx][ny]>200) continue;
            float cost = (d<4) ? 1.0f : 1.414f;
            float tent = g[cx][cy] + cost;
            if (tent < g[nx][ny]) {
                g[nx][ny] = tent;
                h = sqrtf((ex-nx)*(ex-nx)+(ey-ny)*(ey-ny));
                f[nx][ny] = tent + h;
                if (idx < PATH_MAX) { path[idx].x = nx*GRID_RES; path[idx].y = ny*GRID_RES; idx++; }
            }
        }
        float min_f = 1e9f;
        int nx = cx, ny = cy;
        for (int i = 0; i < GRID_SIZE; i++)
            for (int j = 0; j < GRID_SIZE; j++)
                if (!closed[i][j] && f[i][j] < min_f) { min_f = f[i][j]; nx = i; ny = j; }
        cx = nx; cy = ny;
    }
    *path_len = idx;
    return 0;
}

void dwa_avoid(lidar_scan_t* scan, float* linear, float* angular) {
    float min_dist = LIDAR_RANGE;
    int min_idx = 0;
    for (int i = 0; i < LIDAR_POINTS; i++) {
        if (scan->distances[i] < min_dist) { min_dist = scan->distances[i]; min_idx = i; }
    }
    if (min_dist < 1.0f) {
        float angle = min_idx * 2.0f * M_PI / LIDAR_POINTS;
        *angular = (angle < M_PI) ? -1.0f : 1.0f;
        *linear = 0.1f;
    }
}

void send_can(float linear, float angular) {
    int16_t lin = (int16_t)(linear * 1000);
    int16_t ang = (int16_t)(angular * 1000);
    (void)lin; (void)ang;
}

int main(void) {
    pid_init(&pid[0], 1.0f, 0.1f, 0.05f);
    pid_init(&pid[1], 1.0f, 0.1f, 0.05f);
    memset(grid, 0, sizeof(grid));
    lidar_scan_t scan;
    while (1) {
        update_grid(&scan);
        float linear = 0, angular = 0;
        dwa_avoid(&scan, &linear, &angular);
        send_can(linear, angular);
    }
    return 0;
}
""",

    "06_akustikmon-6": """#include <stdint.h>
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
""",
}

for key, code in FIRMWARE.items():
    path = os.path.join(BASE, key, "02_raschety/firmware.c")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(code)
    print(f"  ✓ {path}")

print("Done!")