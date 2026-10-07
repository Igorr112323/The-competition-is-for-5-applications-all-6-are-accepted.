#include <stdint.h>
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
