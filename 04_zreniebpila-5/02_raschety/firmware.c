#include <stdint.h>
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
