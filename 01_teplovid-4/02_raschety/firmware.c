#include <stdint.h>
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
