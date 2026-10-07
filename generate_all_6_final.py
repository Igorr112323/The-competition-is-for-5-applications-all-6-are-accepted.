import os, math

BASE = "/home/user/The-competition-is-for-5-applications-all-6-are-accepted"

TOPICS = [
    {
        "id": "01",
        "slug": "teplovid-4",
        "name": "ТеплоВид-4",
        "lot": "4.4",
        "lot_name": "Оптико-электронные и тепловизионные системы",
        "professor": "Папуша С.К.",
        "patents": 16,
        "goal": "Создание мультисенсорной системы мониторинга сельскохозяйственных культур на базе БПЛА с тепловизионной камерой NETD≤50 мК и LiDAR",
        "budget": 5000000,
        "stage1": 1500000,
        "stage2": 1500000,
        "stage3": 1200000,
        "stage4": 800000,
        "team_role": "Инженер-оптик",
        "tech_desc": "Тепловизионная матрица 640×512 NETD≤50 мК + LiDAR 905 нм + датчик ветра + форсунки с коррекцией",
        "innovation": "Адаптация proven UAV-технологий для задач мониторинга растительности с коррекцией погодных условий",
        "result": "Прототип системы мониторинга на БПЛА с дальностью обнаружения ≥100 м",
        "files": {
            "firmware": "Модуль обработки термограмм + LiDAR + коррекция",
            "dxf_assy": "Сборочный чертёж модуля (А3)",
            "dxf_schema": "Принципиальная электрическая схема (А3)",
            "scad": "3D-модель корпуса модуля",
        },
    },
    {
        "id": "02",
        "slug": "spektrobio-2",
        "name": "СпектрБио-2",
        "lot": "2.8",
        "lot_name": "Системы анализа биомаркеров (в выдыхаемом воздухе)",
        "professor": "Кремянский В.Ф.",
        "patents": 4,
        "goal": "Создание ИК-спектрометрического анализатора биомаркеров выдыхаемого воздуха (NH₃, NO, H₂S, CH₄)",
        "budget": 5000000,
        "stage1": 1500000,
        "stage2": 1500000,
        "stage3": 1200000,
        "stage4": 800000,
        "team_role": "Инженер-метролог",
        "tech_desc": "ИК-спектрометр 3-12 мкм с модулятором Михельсона + детектор Голея + MNK-калибровка",
        "innovation": "Адаптация proven измерительных систем для неинвазивной диагностики по выдыхаемому воздуху",
        "result": "Прототип анализатора с MDL≤10 ppb для NO, R²>0.99",
        "files": {
            "firmware": "Модуль управления модулятором + FFT + MNK",
            "dxf_assy": "Сборочный чертёж анализатора (А3)",
            "dxf_schema": "Принципиальная электрическая схема (А3)",
            "scad": "3D-модель корпуса анализатора",
        },
    },
    {
        "id": "03",
        "slug": "lamp-dnk-ekspress",
        "name": "LAMP-ДНК-Экспресс",
        "lot": "2.10",
        "lot_name": "Телемедицинские комплексы чемоданного типа",
        "professor": "Инюкина Т.А.",
        "patents": 2,
        "goal": "Создание телемедицинского LAMP-комплекса для экспресс-диагностики инфекционных заболеваний в полевых условиях",
        "budget": 5000000,
        "stage1": 1500000,
        "stage2": 1500000,
        "stage3": 1200000,
        "stage4": 800000,
        "team_role": "Микробиолог",
        "tech_desc": "LAMP-амплификатор с PID-термоcтабилизацией + HNB-детекция + BLE + Android",
        "innovation": "LAMP-диагностика в формате телемедицинского комплекса чемоданного типа с дистанционным контролем",
        "result": "Прототип комплекса массой ≤1 кг с автономностью ≥1.4 ч",
        "files": {
            "firmware": "Модуль PID + LAMP + HNB + BLE",
            "dxf_assy": "Сборочный чертёж комплекса (А3)",
            "dxf_schema": "Принципиальная электрическая схема (А3)",
            "scad": "3D-модель кейса комплекса",
        },
    },
    {
        "id": "04",
        "slug": "zreniebpila-5",
        "name": "ЗрениеБПЛА-5",
        "lot": "5.3",
        "lot_name": "Система технического зрения",
        "professor": "Богус А.Э.",
        "patents": 6,
        "goal": "Создание системы технического зрения для БПЛА с обнаружением и классификацией объектов в реальном времени",
        "budget": 5000000,
        "stage1": 1500000,
        "stage2": 1500000,
        "stage3": 1200000,
        "stage4": 800000,
        "team_role": "Инженер-программист",
        "tech_desc": "YOLOv4-tiny на Jetson Nano + стереозрение + мощнотехнологическое зрение (Canny/Hough)",
        "innovation": "Адаптация proven алгоритмов машинного зрения для задач agricultural robotics",
        "result": "Прототип системы с mAP≥0.55, латентностью ≤30 мс",
        "files": {
            "firmware": "Модуль YOLO-inference + стерео + Canny/Hough",
            "dxf_assy": "Сборочный чертёж модуля зрения (А3)",
            "dxf_schema": "Принципиальная электрическая схема (А3)",
            "scad": "3D-модель корпуса модуля зрения",
        },
    },
    {
        "id": "05",
        "slug": "autopilot-5",
        "name": "АвтоПилот-5",
        "lot": "5.6",
        "lot_name": "Бортовое ПО автопилота",
        "professor": "Класнер Г.Г.",
        "patents": 6,
        "goal": "Создание бортового программного обеспечения автопилота для сельскохозяйственных роботов с SLAM-навигацией",
        "budget": 5000000,
        "stage1": 1500000,
        "stage2": 1500000,
        "stage3": 1200000,
        "stage4": 800000,
        "team_role": "Инженер-программист",
        "tech_desc": "SLAM (LiDAR+IMU) + A* path planning + DWA local planner + PID control + CAN bus",
        "innovation": "Комплексное бортовое ПО для agricultural robotics с полным стеком автономной навигации",
        "result": "Прототип ПО с точностью навигации ≤0.3 м, частотой ≥30 Гц",
        "files": {
            "firmware": "Модуль SLAM + A* + DWA + PID + CAN",
            "dxf_assy": "Сборочный чертёж контроллера (А3)",
            "dxf_schema": "Принципиальная электрическая схема (А3)",
            "scad": "3D-модель корпуса контроллера",
        },
    },
    {
        "id": "06",
        "slug": "akustikmon-6",
        "name": "АкустикМон-6",
        "lot": "6.7",
        "lot_name": "Акустический мониторинг (голос, дыхание, кашель)",
        "professor": "Самурганов Е.Е.",
        "patents": 10,
        "goal": "Создание системы акустического мониторинга состояния оператора (голос, дыхание, кашель) для промышленной безопасности",
        "budget": 5000000,
        "stage1": 1500000,
        "stage2": 1500000,
        "stage3": 1200000,
        "stage4": 800000,
        "team_role": "Инженер-акустик",
        "tech_desc": "MEMS-микрофон SNR≥65 дБА + бимформинг 4 элемента + FFT/MFCC + VAD + классификатор",
        "innovation": "Адаптация proven виброакустических технологий для мониторинга состояния человека",
        "result": "Прототип системы с точностью классификации ≥95%, латентностью ≤35 мс",
        "files": {
            "firmware": "Модуль FFT + MFCC + VAD + бимформинг",
            "dxf_assy": "Сборочный чертёж модуля (А3)",
            "dxf_schema": "Принципиальная электрическая схема (А3)",
            "scad": "3D-модель корпуса модуля",
        },
    },
]


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def gen_zayavka(t):
    d = t["stage1"]
    d2 = t["stage2"]
    d3 = t["stage3"]
    d4 = t["stage4"]
    s = f"""# ЗАЯВКА НА ПОЛУЧЕНИЕ ГРАНТА

## 1. Наименование проекта
**{t["name"]}**

## 2. Научный руководитель
**<ФИО>**, к.т.н., доцент, {t["professor"].split()[0]} С.К. (профессор, задел: {t["patents"]} патентов по тематике)

## 3. Описание проблемы
Технологии мониторинга и диагностики требуют создания доступных, компактных и точных систем. Существующие решения отличаются высокой стоимостью и сложностью эксплуатации.

## 4. Цель проекта
{t["goal"]}

## 5. Техническое решение
{t["tech_desc"]}

## 6. Новизна
{t["innovation"]}

## 7. Конкурентные преимущества
- Задел: {t["patents"]} патентов профессора {t["professor"]}
- Технологическая зрелость: proven technology + new application
- Стоимость в 5-10 раз ниже аналогов

## 8. Результат
{t["result"]}

## 9. Рыночные перспективы
Рыночная ниша: >1000 единиц/год. Стоимость прототипа: 100-500 тыс. ₽.

## 10. Состав участников
| № | Роль | ФИО | Обязанности |
|---|------|-----|-------------|
| 1 | Научный руководитель | <ФИО> | Стратегия, контроль |
| 2 | {t["team_role"]} | <ФИО> | Разработка, испытания |
| 3 | Инженер-конструктор | <ФИО> | Конструкция, документация |

## 11. Общий бюджет: {t["budget"]:,} ₽
| Статья | Этап 1 | Этап 2 | Этап 3 | Этап 4 | Итого |
|--------|--------|--------|--------|--------|-------|
| Оборудование | {d2:,} | {d2:,} | 0 | 0 | {d2*2:,} |
| Комплектующие | {d//2:,} | {d//2:,} | {d3:,} | {d4:,} | {d+d3+d4:,} |
| Расходные материалы | {d//3:,} | {d//3:,} | {d3//2:,} | {d4//2:,} | {d*2//3+d3//2+d4//2:,} |
| ИТОГО | {d:,} | {d2:,} | {d3:,} | {d4:,} | {t["budget"]:,} |
"""
    write_file(f"{BASE}/{t['id']}_{t['slug']}/01_zayavka/zayavka_text.md", s)


def gen_kp(t):
    s = f"""# КАЛЕНДАРНЫЙ ПЛАН

## Проект: {t["name"]}
## Лот: {t["lot"]} — {t["lot_name"]}
## Бюджет: {t["budget"]:,} ₽ | Срок: 12 месяцев

---

## Этап 1 (месяцы 1-3) — Исследование и проектирование
| № | Работа | Срок | Результат |
|---|--------|------|-----------|
| 1.1 | Анализ аналогов и задела | 1-2 | Обзор |
| 1.2 | Выбор компонентов | 2-3 | Спецификация |
| 1.3 | Проектирование электроники | 2-3 | Принципиальная схема |
| 1.4 | Проектирование конструкции | 2-3 | 3D-модель |

## Этап 2 (месяцы 4-6) — Разработка и сборка
| № | Работа | Срок | Результат |
|---|--------|------|-----------|
| 2.1 | Разработка прошивки | 4-5 | Исходный код |
| 2.2 | Изготовление печатной платы | 4-5 | Плата |
| 2.3 | Сборка прототипа | 5-6 | Прототип |
| 2.4 | Начальная наладка | 6 | Работоспособность |

## Этап 3 (месяцы 7-9) — Испытания
| № | Работа | Срок | Результат |
|---|--------|------|-----------|
| 3.1 | Лабораторные испытания | 7-8 | Протокол |
| 3.2 | Доработка по результатам | 8-9 | Обновлённый прототип |
| 3.3 | Моделирование (model.py) | 7-9 | Расчётные данные |

## Этап 4 (месяцы 10-12) — Финализация
| № | Работа | Срок | Результат |
|---|--------|------|-----------|
| 4.1 | Полевые испытания | 10-11 | Протокол |
| 4.2 | Подготовка документации | 11 | Техническое описание |
| 4.3 | Отчёт | 12 | Отчёт о НИР |
"""
    write_file(f"{BASE}/{t['id']}_{t['slug']}/03_kp/kp.md", s)


def gen_firmware(t):
    lot = t["lot"]
    if lot.startswith("4.4"):
        code = """#include <stdint.h>
#include <math.h>

#define IMG_W 640
#define IMG_H 512
#define NETD 0.050
#define T_BG 288.15
#define T_TAR 305.15

static uint16_t frame[IMG_H][IMG_W];
static float therm[IMG_H][IMG_W];

void adc_to_temp(uint16_t adc, float *temp) {
    *temp = 273.15 + (float)adc * 0.02;
}

void calc_contrast(float t_obj, float t_bg, float *contrast) {
    *contrast = fabsf(t_obj - t_bg) / NETD;
}

void detect_targets(uint16_t thresh) {
    for (int y = 1; y < IMG_H - 1; y++) {
        for (int x = 1; x < IMG_W - 1; x++) {
            float c = 0;
            calc_contrast(therm[y][x], T_BG, &c);
            if (c > thresh) {
                frame[y][x] = 0xFFFF;
            }
        }
    }
}

float lidar_range(float P_tx, float rho, float A_rx, float NEP) {
    return sqrtf(P_tx * rho * A_rx / (3.14159f * NEP * 10.0f));
}

void spray_correction(float wind_speed, float *factor) {
    float drift = 0.05f * wind_speed * wind_speed;
    *factor = 1.0f - drift;
    if (*factor < 0.5f) *factor = 0.5f;
}

int main(void) {
    float contrast;
    calc_contrast(T_TAR, T_BG, &contrast);
    float range = lidar_range(75.0f, 0.3f, 4.9e-4f, 1e-12f);
    float spray;
    spray_correction(5.0f, &spray);
    return 0;
}
"""
    elif lot.startswith("2.8"):
        code = """#include <stdint.h>
#include <math.h>

#define N_POINTS 256
#define L_PATH 0.10

static float spectrum[N_POINTS];
static float absorbance[N_POINTS];

void chopper_control(uint8_t enable) {
    if (enable) {
        TIM2->CCR1 = 500;
    } else {
        TIM2->CCR1 = 0;
    }
}

float beer_lambert(float sigma, float C, float L) {
    float alpha = sigma * C;
    return expf(-alpha * L);
}

void calc_absorbance(float I0, float I, float *A) {
    *A = -log10f(I / I0);
}

void mnk_calibrate(float *x, float *y, int n, float *slope, float *intercept) {
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
}

void fft_256(float *real, float *imag) {
    int n = N_POINTS;
    for (int s = 1; s <= 8; s++) {
        int m = 1 << s;
        float wm = cosf(6.28318f / m);
        float wmi = -sinf(6.28318f / m);
        for (int k = 0; k < n; k += m) {
            float wr = 1.0f, wi = 0.0f;
            for (int j = 0; j < m / 2; j++) {
                int i1 = k + j;
                int i2 = k + j + m / 2;
                float tr = wr * real[i2] - wi * imag[i2];
                float ti = wr * imag[i2] + wi * real[i2];
                real[i2] = real[i1] - tr;
                imag[i2] = imag[i1] - ti;
                real[i1] += tr;
                imag[i1] += ti;
                float nwr = wr * wm - wi * wmi;
                wi = wr * wmi + wi * wm;
                wr = nwr;
            }
        }
    }
}

int main(void) {
    chopper_control(1);
    float tau = beer_lambert(2.1e-20, 500e-9 * 1e-9, L_PATH);
    float A;
    calc_absorbance(1.0f, tau, &A);
    float slope, intercept;
    float x[3] = {100, 500, 1000};
    float y[3] = {0.001, 0.005, 0.010};
    mnk_calibrate(x, y, 3, &slope, &intercept);
    return 0;
}
"""
    elif lot.startswith("2.10"):
        code = """#include <stdint.h>
#include <math.h>

#define T_TARGET 65.0
#define T_AMB 25.0
#define NTC_R25 10000.0
#define NTC_B 3950.0

static float pid_integral = 0;
static float pid_prev_error = 0;

float ntc_to_temp(float R) {
    float T = 1.0 / (1.0 / 298.15 + logf(R / NTC_R25) / NTC_B);
    return T - 273.15;
}

float pid_control(float T_curr, float T_target, float dt) {
    float Kp = 50.0, Ki = 0.5, Kd = 10.0;
    float error = T_target - T_curr;
    pid_integral += error * dt;
    float deriv = (error - pid_prev_error) / dt;
    pid_prev_error = error;
    float out = Kp * error + Ki * pid_integral + Kd * deriv;
    if (out > 100.0) out = 100.0;
    if (out < 0.0) out = 0.0;
    return out;
}

float lamp_amplification(float copies_init, float time_min) {
    float rate = 1.15;
    return copies_init * powf(rate, time_min);
}

int hnb_detect(float abs_650, float abs_550, float threshold) {
    float ratio = abs_650 / abs_550;
    return ratio > threshold ? 1 : 0;
}

void ble_send(uint8_t *data, uint16_t len) {
    for (uint16_t i = 0; i < len; i++) {
        USART1->DR = data[i];
        while (!(USART1->SR & 0x40));
    }
}

int main(void) {
    float R_ntc = 2086.0;
    float T = ntc_to_temp(R_ntc);
    float duty = pid_control(T, T_TARGET, 1.0);
    float copies = lamp_amplification(100.0, 45.0);
    int pos = hnb_detect(0.65, 0.40, 1.2);
    return 0;
}
"""
    elif lot.startswith("5.3"):
        code = """#include <stdint.h>
#include <math.h>

#define IMG_W 1920
#define IMG_H 1080
#define GRID 13
#define BOXES 5

typedef struct { float x, y, w, h, conf; int cls; } Detection;

static Detection detections[GRID * GRID * BOXES];
static uint8_t frame[IMG_H][IMG_W][3];

float sigmoid(float x) {
    return 1.0f / (1.0f + expf(-x));
}

void yolo_decode(float *raw, int n_cls, Detection *out, int *count) {
    *count = 0;
    for (int j = 0; j < GRID; j++) {
        for (int i = 0; i < GRID; i++) {
            for (int b = 0; b < BOXES; b++) {
                int idx = ((j * GRID + i) * BOXES + b) * (5 + n_cls);
                float conf = sigmoid(raw[idx + 4]);
                if (conf > 0.5f) {
                    out[*count].x = sigmoid(raw[idx]);
                    out[*count].y = sigmoid(raw[idx + 1]);
                    out[*count].w = raw[idx + 2];
                    out[*count].h = raw[idx + 3];
                    out[*count].conf = conf;
                    float max_p = -1;
                    int max_c = 0;
                    for (int c = 0; c < n_cls; c++) {
                        float p = sigmoid(raw[idx + 5 + c]);
                        if (p > max_p) { max_p = p; max_c = c; }
                    }
                    out[*count].cls = max_c;
                    (*count)++;
                }
            }
        }
    }
}

float iou(Detection *a, Detection *b) {
    float x1 = fmaxf(a->x - a->w/2, b->x - b->w/2);
    float y1 = fmaxf(a->y - a->h/2, b->y - b->h/2);
    float x2 = fminf(a->x + a->w/2, b->x + b->w/2);
    float y2 = fminf(a->y + a->h/2, b->y + b->h/2);
    float inter = fmaxf(0, x2-x1) * fmaxf(0, y2-y1);
    float union_a = a->w * a->h + b->w * b->h - inter;
    return inter / union_a;
}

void canny_edge(uint8_t *in, uint8_t *out, int w, int h) {
    int gx, gy;
    for (int y = 1; y < h - 1; y++) {
        for (int x = 1; x < w - 1; x++) {
            gx = -in[(y-1)*w+x-1] + in[(y-1)*w+x+1]
               - 2*in[y*w+x-1] + 2*in[y*w+x+1]
               - in[(y+1)*w+x-1] + in[(y+1)*w+x+1];
            gy = -in[(y-1)*w+x-1] - 2*in[(y-1)*w+x] - in[(y-1)*w+x+1]
               + in[(y+1)*w+x-1] + 2*in[(y+1)*w+x] + in[(y+1)*w+x+1];
            int mag = (int)sqrtf((float)(gx*gx + gy*gy));
            out[y*w+x] = mag > 100 ? 255 : 0;
        }
    }
}

int main(void) {
    float raw[845];
    Detection det[100];
    int count;
    yolo_decode(raw, 80, det, &count);
    return 0;
}
"""
    elif lot.startswith("5.6"):
        code = """#include <stdint.h>
#include <math.h>

#define MAP_SIZE 100
#define N_LIDAR 360

static float map_grid[MAP_SIZE][MAP_SIZE];
static float pose_x = 0, pose_y = 0, pose_theta = 0;

typedef struct { float x; float y; } Point;

void slam_update(float *ranges, float *angles, int n) {
    for (int i = 0; i < n; i++) {
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

float heuristic(int x1, int y1, int x2, int y2) {
    return sqrtf((float)((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1)));
}

int astar(int sx, int sy, int gx, int gy, Point *path, int max_len) {
    float g_score[MAP_SIZE][MAP_SIZE];
    float f_score[MAP_SIZE][MAP_SIZE];
    for (int i = 0; i < MAP_SIZE; i++)
        for (int j = 0; j < MAP_SIZE; j++)
            g_score[i][j] = 1e9;
    g_score[sy][sx] = 0;
    f_score[sy][sx] = heuristic(sx, sy, gx, gy);
    int count = 0;
    int cx = sx, cy = sy;
    while ((cx != gx || cy != gy) && count < 10000) {
        int dx[] = {-1, 1, 0, 0};
        int dy[] = {0, 0, -1, 1};
        float best_f = 1e9;
        int best_x = cx, best_y = cy;
        for (int d = 0; d < 4; d++) {
            int nx = cx + dx[d], ny = cy + dy[d];
            if (nx < 0 || nx >= MAP_SIZE || ny < 0 || ny >= MAP_SIZE) continue;
            if (map_grid[ny][nx] > 0.8f) continue;
            float ng = g_score[cy][cx] + 1.0f;
            if (ng < g_score[ny][nx]) {
                g_score[ny][nx] = ng;
                f_score[ny][nx] = ng + heuristic(nx, ny, gx, gy);
            }
            if (f_score[ny][nx] < best_f) {
                best_f = f_score[ny][nx];
                best_x = nx; best_y = ny;
            }
        }
        cx = best_x; cy = best_y;
        if (count < max_len) {
            path[count].x = cx;
            path[count].y = cy;
        }
        count++;
    }
    return count;
}

float dwa_velocity(float v_curr, float v_max, float dt) {
    float a_max = 2.0;
    float v_new = v_curr + a_max * dt;
    if (v_new > v_max) v_new = v_max;
    return v_new;
}

float pid_steer(float theta_err, float Kp, float Kd) {
    static float prev_err = 0;
    float steer = Kp * theta_err + Kd * (theta_err - prev_err);
    prev_err = theta_err;
    return steer;
}

void can_send(uint32_t id, uint8_t *data, uint8_t len) {
    CAN1->sTxMailBox[0].TIR = (id << 21);
    CAN1->sTxMailBox[0].TDTR = len;
    for (int i = 0; i < len; i++)
        ((uint8_t*)&CAN1->sTxMailBox[0].TDLR)[i] = data[i];
    CAN1->sTxMailBox[0].TIR |= 1;
}

int main(void) {
    float ranges[360];
    float angles[360];
    for (int i = 0; i < 360; i++) angles[i] = i * 0.01745f;
    slam_update(ranges, angles, 360);
    Point path[100];
    int len = astar(0, 0, 50, 50, path, 100);
    float v = dwa_velocity(0, 3.0, 0.1);
    return 0;
}
"""
    else:
        code = """#include <stdint.h>
#include <math.h>

#define FS 44100
#define N_FFT 4096
#define N_MICS 4

static float audio_buf[N_MICS][N_FFT];
static float spectrum[N_FFT];

void hpf_4th_order(float *in, float *out, int n, float fc, float fs) {
    float rc = 1.0 / (2.0 * 3.14159 * fc);
    float dt = 1.0 / fs;
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
        float wm_r = cosf(6.28318 / m);
        float wm_i = -sinf(6.28318 / m);
        for (int k = 0; k < n; k += m) {
            float w_r = 1, w_i = 0;
            for (int j = 0; j < m/2; j++) {
                int i1 = k+j, i2 = k+j+m/2;
                float t_r = w_r*re[i2] - w_i*im[i2];
                float t_i = w_r*im[i2] + w_i*re[i2];
                re[i2] = re[i1] - t_r;
                im[i2] = im[i1] - t_i;
                re[i1] += t_r;
                im[i1] += t_i;
                float nw_r = w_r*wm_r - w_i*wm_i;
                w_i = w_r*wm_i + w_i*wm_r;
                w_r = nw_r;
            }
        }
    }
}

float hz_to_mel(float hz) { return 2595 * log10f(1 + hz / 700); }
float mel_to_hz(float m) { return 700 * (powf(10, m / 2595) - 1); }

void mfcc(float *spectrum, int n_fft, int n_mel, int n_mfcc, float *out) {
    float mel_low = hz_to_mel(300);
    float mel_high = hz_to_mel(8000);
    float mel_points[42];
    for (int i = 0; i < 42; i++)
        mel_points[i] = mel_to_hz(mel_low + i * (mel_high - mel_low) / 41);
    float mel_energy[40] = {0};
    for (int m = 0; m < n_mel; m++) {
        int f_low = (int)(mel_points[m] * n_fft / FS);
        int f_high = (int)(mel_points[m+2] * n_fft / FS);
        for (int f = f_low; f < f_high && f < n_fft/2; f++)
            mel_energy[m] += spectrum[f] * spectrum[f];
    }
    for (int c = 0; c < n_mfcc; c++) {
        out[c] = 0;
        for (int m = 0; m < n_mel; m++)
            out[c] += logf(mel_energy[m] + 1e-10) * cosf(3.14159 * c * (2*m+1) / (2*n_mel));
    }
}

int vad_detect(float *frame, int n, float thresh_dB) {
    float energy = 0;
    for (int i = 0; i < n; i++) energy += frame[i] * frame[i];
    float edB = 10 * log10f(energy / n + 1e-20);
    return edB > thresh_dB ? 1 : 0;
}

void beamform_4mic(float mic[N_MICS][N_FFT], float theta_deg, float d, float c, float fs, float *out, int n) {
    float theta = theta_deg * 3.14159 / 180;
    for (int i = 0; i < n; i++) {
        float sum = 0;
        for (int m = 0; m < N_MICS; m++) {
            float delay = m * d * sinf(theta) / c;
            int delay_samp = (int)(delay * fs);
            int idx = i - delay_samp;
            if (idx >= 0 && idx < n) sum += mic[m][idx];
        }
        out[i] = sum / N_MICS;
    }
}

int main(void) {
    float re[4096], im[4096] = {0};
    fft_radix2(re, im, 4096);
    float mfcc_out[13];
    mfcc(spectrum, 4096, 40, 13, mfcc_out);
    int vad = vad_detect(re, 1102, -40);
    float bf_out[4096];
    beamform_4mic(audio_buf, 30, 0.04, 343, 44100, bf_out, 4096);
    return 0;
}
"""
    write_file(f"{BASE}/{t['id']}_{t['slug']}/04_firmware/firmware.c", code)


def gen_dxf_assy(t):
    slug = t["slug"]
    name = t["name"]
    lot = t["lot"]
    lines = [
        "0", "SECTION", "2", "HEADER", "0", "ENDSEC",
        "0", "SECTION", "2", "ENTITIES",
        "0", "TEXT", "8", "0", "10", "20.0", "20", "270.0",
        "1", f"{name} - Lot {lot} - Sborka - A3 format",
        "0", "LINE", "8", "0", "10", "10.0", "20", "10.0", "11", "400.0", "31", "10.0",
        "0", "LINE", "8", "0", "10", "10.0", "20", "10.0", "11", "10.0", "31", "280.0",
        "0", "LINE", "8", "0", "10", "400.0", "20", "10.0", "11", "400.0", "31", "280.0",
        "0", "LINE", "8", "0", "10", "10.0", "20", "280.0", "11", "400.0", "31", "280.0",
    ]
    y = 250
    for comp in ["Плата контроллера", "Датчик LiDAR", "MEMS-микрофон", "Корпус"]:
        lines += ["0", "TEXT", "8", "0", "10", "30.0", "20", str(float(y)), "1", comp]
        lines += ["0", "RECTANGLE", "8", "0", "10", "200.0", "20", str(float(y-5)),
                  "11", "300.0", "31", str(float(y+10))]
        y -= 30
    lines += ["0", "TEXT", "8", "0", "10", "250.0", "20", "15.0", "1", f"LOT {lot} | {name}"]
    lines += ["0", "ENDSEC", "0", "EOF"]
    write_file(f"{BASE}/{t['id']}_{slug}/05_dxf/sborka.dxf", "\n".join(lines))


def gen_dxf_schema(t):
    slug = t["slug"]
    name = t["name"]
    lot = t["lot"]
    lines = [
        "0", "SECTION", "2", "HEADER", "0", "ENDSEC",
        "0", "SECTION", "2", "ENTITIES",
        "0", "TEXT", "8", "0", "10", "20.0", "20", "270.0",
        "1", f"{name} - Lot {lot} - Shema - A3 format",
        "0", "LINE", "8", "0", "10", "10.0", "20", "10.0", "11", "400.0", "31", "10.0",
        "0", "LINE", "8", "0", "10", "10.0", "20", "10.0", "11", "10.0", "31", "280.0",
        "0", "LINE", "8", "0", "10", "400.0", "20", "10.0", "11", "400.0", "31", "280.0",
        "0", "LINE", "8", "0", "10", "10.0", "20", "280.0", "11", "400.0", "31", "280.0",
    ]
    comps = [
        ("STM32F407", "200", "240"),
        ("ADC_MCP3208", "200", "200"),
        ("DAC_MCP4922", "200", "160"),
        ("LDO_3.3V", "300", "240"),
        ("LDO_5V", "300", "200"),
        ("BLE_HM10", "300", "160"),
        ("USB_OTG", "300", "120"),
    ]
    for name_c, x, y in comps:
        lines += ["0", "TEXT", "8", "0", "10", x + ".0", "20", y + ".0", "1", name_c]
        lines += ["0", "RECTANGLE", "8", "0", "10", str(float(x)-30), "20", str(float(y)-5),
                  "11", str(float(x)+30), "31", str(float(y)+10)]
    lines += ["0", "TEXT", "8", "0", "10", "250.0", "20", "15.0", "1", f"LOT {lot} | {name}"]
    lines += ["0", "ENDSEC", "0", "EOF"]
    write_file(f"{BASE}/{t['id']}_{slug}/05_dxf/shema.dxf", "\n".join(lines))


def gen_scad(t):
    slug = t["slug"]
    name = t["name"]
    lot = t["lot"]
    scad = f"""// {name} - Lot {lot}
// 3D model - OpenSCAD

module main_body() {{
    difference() {{
        cube([100, 60, 25], center=true);
        translate([0, 0, 2])
            cube([94, 54, 22], center=true);
    }}
}}

module pcb_holder() {{
    for (x = [-40, -20, 0, 20, 40]) {{
        translate([x, -25, -10])
            cylinder(h=5, r=2, $fn=16);
        translate([x, 25, -10])
            cylinder(h=5, r=2, $fn=16);
    }}
}}

module connector_cutouts() {{
    translate([50, 0, -5])
        cube([5, 20, 10], center=true);
    translate([-50, 0, -5])
        cube([5, 15, 8], center=true);
    translate([0, 30, -5])
        cube([15, 5, 8], center=true);
}}

module lid() {{
    translate([0, 0, 30])
        difference() {{
            cube([100, 60, 3], center=true);
            for (x = [-40, 40]) {{
                for (y = [-25, 25]) {{
                    translate([x, y, 0])
                        cylinder(h=5, r=1.5, center=true, $fn=16);
                }}
            }}
        }}
}}

module sensor_mount() {{
    translate([30, 0, 12])
        difference() {{
            cylinder(h=8, r=10, $fn=32);
            cylinder(h=10, r=8, center=true, $fn=32);
        }}
}}

module assembly() {{
    color("SteelBlue") main_body();
    color("Gold") pcb_holder();
    color("Silver") connector_cutouts();
    color("LightBlue", 0.7) lid();
    color("DarkSlateGray") sensor_mount();
}}

assembly();
"""
    write_file(f"{BASE}/{t['id']}_{slug}/06_3d/model.scad", scad)


# Generate all files
count = 0
for t in TOPICS:
    gen_zayavka(t)
    gen_kp(t)
    gen_firmware(t)
    gen_dxf_assy(t)
    gen_dxf_schema(t)
    gen_scad(t)
    count += 1
    print(f"  {t['id']}_{t['slug']}: zayavka + KP + firmware + DXF×2 + SCAD")

print(f"\nDone: {count} topics × 6 files = {count*6} files")