#include <stdint.h>
#include <math.h>
#include <string.h>

#define UZ_COUNT 6
#define IMU_AXES 6
#define GRID_SIZE 200
#define LANDMARK_MAX 500
#define KALMAN_DIM 6
#define PATH_MAX 1000
#define BLE_MTU 244

typedef struct {
    float x;
    float y;
    float theta;
    float vx;
    float vy;
    float omega;
} pose_t;

typedef struct {
    float uz_distance[UZ_COUNT];
    float imu_accel[3];
    float imu_gyro[3];
    float encoder_left;
    float encoder_right;
    uint32_t timestamp;
} sensor_data_t;

typedef struct {
    float x;
    float y;
    float descriptor[64];
    uint8_t active;
} landmark_t;

typedef struct {
    float state[KALMAN_DIM];
    float P[KALMAN_DIM][KALMAN_DIM];
    float Q[KALMAN_DIM][KALMAN_DIM];
    float R[KALMAN_DIM][KALMAN_DIM];
} kalman_t;

static kalman_t kf;
static landmark_t landmarks[LANDMARK_MAX];
static int landmark_count = 0;
static uint8_t occupancy_grid[GRID_SIZE][GRID_SIZE];
static float grid_resolution = 0.1f;

static const float WHEEL_BASE = 0.35f;
static const float TICKS_PER_M = 400.0f / (3.14159f * 0.15f);
static const float UZ_ANGLES[UZ_COUNT] = {0, 60, 120, 180, 240, 300};

void kalman_init(kalman_t* k) {
    memset(k->state, 0, sizeof(k->state));
    for (int i = 0; i < KALMAN_DIM; i++) {
        for (int j = 0; j < KALMAN_DIM; j++) {
            k->P[i][j] = (i == j) ? 1.0f : 0.0f;
            k->Q[i][j] = (i == j) ? 0.01f : 0.0f;
            k->R[i][j] = (i == j) ? 0.1f : 0.0f;
        }
    }
}

void kalman_predict(kalman_t* k, float dt) {
    k->state[0] += k->state[3] * dt;
    k->state[1] += k->state[4] * dt;
    k->state[2] += k->state[5] * dt;
    for (int i = 0; i < KALMAN_DIM; i++) {
        k->P[i][i] += k->Q[i][i] * dt;
    }
}

void kalman_update_odometry(kalman_t* k, float dx, float dy, float dtheta) {
    float innovation_x = dx - k->state[3];
    float innovation_y = dy - k->state[4];
    float innovation_theta = dtheta - k->state[5];
    float S_x = k->P[3][3] + k->R[3][3];
    float S_y = k->P[4][4] + k->R[4][4];
    float S_theta = k->P[5][5] + k->R[5][5];
    float K_x = k->P[3][3] / S_x;
    float K_y = k->P[4][4] / S_y;
    float K_theta = k->P[5][5] / S_theta;
    k->state[3] += K_x * innovation_x;
    k->state[4] += K_y * innovation_y;
    k->state[5] += K_theta * innovation_theta;
    k->P[3][3] *= (1.0f - K_x);
    k->P[4][4] *= (1.0f - K_y);
    k->P[5][5] *= (1.0f - K_theta);
}

void kalman_update_uz(kalman_t* k, float* distances) {
    for (int i = 0; i < UZ_COUNT; i++) {
        float angle_rad = UZ_ANGLES[i] * 3.14159f / 180.0f;
        float expected_x = k->state[0] + distances[i] * cosf(k->state[2] + angle_rad);
        float expected_y = k->state[1] + distances[i] * sinf(k->state[2] + angle_rad);
        float predicted_x = k->state[0];
        float predicted_y = k->state[1];
        float innov_x = expected_x - predicted_x;
        float innov_y = expected_y - predicted_y;
        float S = k->P[0][0] + k->R[0][0];
        float K = k->P[0][0] / S;
        k->state[0] += K * innov_x;
        k->state[1] += K * innov_y;
        k->P[0][0] *= (1.0f - K);
    }
}

void update_occupancy_grid(int gx, int gy, uint8_t occupied) {
    if (gx >= 0 && gx < GRID_SIZE && gy >= 0 && gy < GRID_SIZE) {
        if (occupied) occupancy_grid[gx][gy] = 255;
        else if (occupancy_grid[gx][gy] < 200) occupancy_grid[gx][gy] += 5;
    }
}

int detect_obstacle(float* uz_distances, int* obstacle_gx, int* obstacle_gy) {
    for (int i = 0; i < UZ_COUNT; i++) {
        if (uz_distances[i] > 0.03f && uz_distances[i] < 0.5f) {
            float angle_rad = UZ_ANGLES[i] * 3.14159f / 180.0f;
            float ox = kf.state[0] + uz_distances[i] * cosf(kf.state[2] + angle_rad);
            float oy = kf.state[1] + uz_distances[i] * sinf(kf.state[2] + angle_rad);
            *obstacle_gx = (int)(ox / grid_resolution);
            *obstacle_gy = (int)(oy / grid_resolution);
            update_occupancy_grid(*obstacle_gx, *obstacle_gy, 1);
            return 1;
        }
    }
    return 0;
}

void visual_odometry_update(float* frame_curr, float* frame_prev, int width, int height, float* dx, float* dy, float* dtheta) {
    float sum_dx = 0.0f;
    float sum_dy = 0.0f;
    int count = 0;
    for (int y = 1; y < height - 1; y++) {
        for (int x = 1; x < width - 1; x++) {
            float gx = frame_curr[y * width + x + 1] - frame_curr[y * width + x - 1];
            float gy = frame_curr[(y + 1) * width + x] - frame_curr[(y - 1) * width + x];
            if (gx * gx + gy * gy > 100.0f) {
                sum_dx += gx;
                sum_dy += gy;
                count++;
            }
        }
    }
    if (count > 0) {
        *dx = sum_dx / count * 0.001f;
        *dy = sum_dy / count * 0.001f;
    }
    *dtheta = 0.0f;
}

float hog_extract_feature(float* image, int x, int y, int cell_size) {
    float magnitude = 0.0f;
    float angle = 0.0f;
    for (int cy = 0; cy < cell_size; cy++) {
        for (int cx = 0; cx < cell_size; cx++) {
            int px = x * cell_size + cx;
            int py = y * cell_size + cy;
            float gx = image[py * 1280 + px + 1] - image[py * 1280 + px - 1];
            float gy = image[(py + 1) * 1280 + px] - image[(py - 1) * 1280 + px];
            magnitude += sqrtf(gx * gx + gy * gy);
        }
    }
    return magnitude / (cell_size * cell_size);
}

int svm_classify(float* features, int n_features) {
    float scores[4] = {0};
    for (int c = 0; c < 4; c++) {
        for (int i = 0; i < n_features; i++) {
            scores[c] += features[i] * 0.001f;
        }
    }
    int best = 0;
    for (int c = 1; c < 4; c++) {
        if (scores[c] > scores[best]) best = c;
    }
    return best;
}

void path_planner_astar(int start_gx, int start_gy, int goal_gx, int goal_gy, float* path_x, float* path_y, int* path_len) {
    float g_score[GRID_SIZE][GRID_SIZE];
    float f_score[GRID_SIZE][GRID_SIZE];
    uint8_t closed[GRID_SIZE][GRID_SIZE];
    memset(closed, 0, sizeof(closed));
    for (int i = 0; i < GRID_SIZE; i++)
        for (int j = 0; j < GRID_SIZE; j++)
            g_score[i][j] = 1e9f;
    g_score[start_gx][start_gy] = 0.0f;
    float h = sqrtf((goal_gx - start_gx) * (goal_gx - start_gx) + (goal_gy - start_gy) * (goal_gy - start_gy));
    f_score[start_gx][start_gy] = h;

    int current_gx = start_gx;
    int current_gy = start_gy;
    int path_idx = 0;

    for (int iter = 0; iter < 10000; iter++) {
        if (current_gx == goal_gx && current_gy == goal_gy) {
            *path_len = path_idx;
            return;
        }
        closed[current_gx][current_gy] = 1;
        int dx[] = {-1, 0, 1, 0};
        int dy[] = {0, 1, 0, -1};
        for (int d = 0; d < 4; d++) {
            int nx = current_gx + dx[d];
            int ny = current_gy + dy[d];
            if (nx < 0 || nx >= GRID_SIZE || ny < 0 || ny >= GRID_SIZE) continue;
            if (closed[nx][ny]) continue;
            if (occupancy_grid[nx][ny] > 200) continue;
            float tent_g = g_score[current_gx][current_gy] + 1.0f;
            if (tent_g < g_score[nx][ny]) {
                g_score[nx][ny] = tent_g;
                h = sqrtf((goal_gx - nx) * (goal_gx - nx) + (goal_gy - ny) * (goal_gy - ny));
                f_score[nx][ny] = tent_g + h;
                if (path_idx < PATH_MAX) {
                    path_x[path_idx] = nx * grid_resolution;
                    path_y[path_idx] = ny * grid_resolution;
                    path_idx++;
                }
            }
        }
        float min_f = 1e9f;
        int next_gx = current_gx;
        int next_gy = current_gy;
        for (int i = 0; i < GRID_SIZE; i++) {
            for (int j = 0; j < GRID_SIZE; j++) {
                if (!closed[i][j] && f_score[i][j] < min_f) {
                    min_f = f_score[i][j];
                    next_gx = i;
                    next_gy = j;
                }
            }
        }
        current_gx = next_gx;
        current_gy = next_gy;
    }
    *path_len = path_idx;
}

void send_motor_command(float linear_vel, float angular_vel) {
    float left_speed = linear_vel - angular_vel * WHEEL_BASE / 2.0f;
    float right_speed = linear_vel + angular_vel * WHEEL_BASE / 2.0f;
    uint16_t left_pwm = (uint16_t)(left_speed * 1000.0f);
    uint16_t right_pwm = (uint16_t)(right_speed * 1000.0f);
    (void)left_pwm;
    (void)right_pwm;
}

int main(void) {
    kalman_init(&kf);
    memset(occupancy_grid, 0, sizeof(occupancy_grid));
    while (1) {
        sensor_data_t sens;
        kalman_predict(&kf, 0.033f);
        float dx = (sens.encoder_left + sens.encoder_right) / 2.0f / TICKS_PER_M;
        float dtheta = (sens.encoder_right - sens.encoder_left) / TICKS_PER_M / WHEEL_BASE;
        kalman_update_odometry(&kf, dx, 0.0f, dtheta);
        kalman_update_uz(&kf, sens.uz_distance);
        int obs_gx, obs_gy;
        detect_obstacle(sens.uz_distance, &obs_gx, &obs_gy);
    }
    return 0;
}