#include <stdint.h>
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