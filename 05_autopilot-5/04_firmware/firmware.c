#include <stdint.h>
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
    int closed[MAP_SIZE][MAP_SIZE];
    for (int i = 0; i < MAP_SIZE; i++)
        for (int j = 0; j < MAP_SIZE; j++) {
            g_score[i][j] = 1e9f;
            f_score[i][j] = 0;
            closed[i][j] = 0;
        }
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