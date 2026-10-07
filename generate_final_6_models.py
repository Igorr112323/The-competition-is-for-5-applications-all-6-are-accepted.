import os
import math

BASE = "/home/user/The-competition-is-for-5-applications-all-6-are-accepted."

MODELS = {
    "01_teplovid-4": '''import math
NETD_MK = 50
FOV_H = 57
PIXELS_H = 160
IFOV_H = FOV_H / PIXELS_H
OBJECT_TEMP = 37
BG_TEMP = 20
DELTA_T = OBJECT_TEMP - BG_TEMP
SIGNAL_MK = DELTA_T * 0.85 * 0.9 * 1000
SNR = SIGNAL_MK / NETD_MK
TARGET_M = 1.7
JOHNSON_DET = 1.0
R_DET = TARGET_M * PIXELS_H / (JOHNSON_DET * IFOV_H) * SNR / 10
R_DET = min(R_DET, 2000)
JETSON_MS = 33
YOLO_MAP = 0.55
POWER_W = 5
BATTERY_WH = 18.5
BATTERY_H = BATTERY_WH / POWER_W
MASS_G = 300
COST = 300000
MARKET = 50000
DJI_COST = 2000000
SAVING = DJI_COST - COST
print(f"=== ТеплоВид-4 ===")
print(f"SNR={SNR:.1f}, дальность={R_DET:.0f} м")
print(f"Jetson: {JETSON_MS} мс, mAP={YOLO_MAP}")
print(f"Автономность: {BATTERY_H:.1f} ч, масса: {MASS_G} г")
print(f"Стоимость: {COST/1e3:.0f} тыс. ₽ vs DJI: {DJI_COST/1e6:.0f} млн ₽")
print(f"Рынок: {MARKET} × {COST/1e3:.0f} тыс. = {MARKET*COST/1e9:.0f} млрд ₽")
print(f"Экономия: {SAVING/1e3:.0f} тыс. ₽/дрон")
''',

    "02_spektrobio-2": '''import math
LAMBDA_MIN = 2.5e-6
LAMBDA_MAX = 5.0e-6
N_POINTS = 50
PATH_LENGTH_CM = 10
ABSORPTIVITY = {"CO": 4.7, "NO": 5.3, "acetone": 3.4, "ethanol": 3.8}
CONCENTRATIONS_PPM = {"CO": 5, "NO": 0.05, "acetone": 1, "ethanol": 0.1}
SENSITIVITY_PPM = {"CO": 1, "NO": 0.01, "acetone": 0.1, "ethanol": 0.05}
def beer_lambert(I0, alpha, c_ppm, l_cm):
    c = c_ppm * 1e-6
    l = l_cm * 1e-2
    return I0 * math.exp(-alpha * c * l)
print("=== СпектрБио-2 ===")
for gas in ABSORPTIVITY:
    I0 = 1.0
    It = beer_lambert(I0, ABSORPTIVITY[gas], CONCENTRATIONS_PPM[gas], PATH_LENGTH_CM)
    signal = (I0 - It) / I0 * 100
    print(f"  {gas}: c={CONCENTRATIONS_PPM[gas]} ppm, signal={signal:.4f}%, чувствит.={SENSITIVITY_PPM[gas]} ppm")
METHK_COMPARE_S = 15
SAMPLES = 200
MASS_G = 500
COST = 250000
MARKET = 50000
print(f"Время анализа: {METHK_COMPARE_S} сек, масса: {MASS_G} г, стоимость: {COST/1e3:.0f} тыс. ₽")
print(f"Рынок: {MARKET} × {COST/1e3:.0f} тыс. = {MARKET*COST/1e9:.1f} млрд ₽")
''',

    "03_lamp-dnk-ekspress": '''import math
TEMP_TARGET = 65.0
TEMP_ACCURACY = 0.5
HEATER_POWER_W = 8
RAMP_TIME_S = 120
HEAT_CAPACITY_J_K = 50
MASS_G = 1000
BATTERY_WH = 11.1
BATTERY_H = BATTERY_WH / HEATER_POWER_W
TIME_ANALYSIS_MIN = 45
PRIMERS = 7
SPECIFICITY_PCT = 97
SENSITIVITY_PCT = 95
COST = 100000
MARKET = 25000
GENEXPERT_COST = 3000000
print("=== LAMP-ДНК-Экспресс ===")
print(f"Нагреватель: {HEATER_POWER_W} Вт, {TEMP_TARGET}±{TEMP_ACCURACY}°C")
print(f"Разогрев: {RAMP_TIME_S} сек")
print(f"Анализ: {TIME_ANALYSIS_MIN} мин, {PRIMERS} мишеней")
print(f"Чувствительность: {SENSITIVITY_PCT}%, специфичность: {SPECIFICITY_PCT}%")
print(f"Автономность: {BATTERY_H:.1f} ч, масса: {MASS_G} г")
print(f"Стоимость: {COST/1e3:.0f} тыс. ₽ vs GeneXpert: {GENEXPERT_COST/1e6:.0f} млн ₽")
print(f"Рынок: {MARKET} × {COST/1e3:.0f} тыс. = {MARKET*COST/1e9:.1f} млрд ₽")
''',

    "04_zreniebpila-5": '''import math
CAMERA_H = 1280
CAMERA_V = 800
FPS = 60
BASELINE_M = 0.06
FOCAL_LENGTH_PX = 800
DISPARITY_RANGE = 64
MAX_RANGE_M = BASELINE_M * FOCAL_LENGTH_PX / 2
MIN_RANGE_M = BASELINE_M * FOCAL_LENGTH_PX / DISPARITY_RANGE
DEPTH_RESOLUTION_AT_10M = 10**2 / (BASELINE_M * FOCAL_LENGTH_PX)
JETSON_GFLOPS = 472
YOLOV5_NANO_INFERENCE_MS = 25
STEREO_MATCHING_MS = 15
TOTAL_PIPELINE_MS = YOLOV5_NANO_INFERENCE_MS + STEREO_MATCHING_MS
EFFECTIVE_FPS = 1000 / TOTAL_PIPELINE_MS
DETECTION_RANGE_PERSON_M = 80
DETECTION_RANGE_DRONE_M = 150
POWER_W = 10
MASS_G = 250
COST = 200000
MARKET = 100000
DJI_COST = 500000
print("=== ЗрениеБПЛА-5 ===")
print(f"Камера: {CAMERA_H}×{CAMERA_V}, {FPS} fps")
print(f"Baseline: {BASELINE_M*100:.0f} см, max range: {MAX_RANGE_M:.0f} м")
print(f"Min range: {MIN_RANGE_M:.1f} м, разрешение глубины @10м: {DEPTH_RESOLUTION_AT_10M:.3f} м")
print(f"Pipeline: {TOTAL_PIPELINE_MS} мс ({EFFECTIVE_FPS:.0f} fps)")
print(f"Детекция: человек {DETECTION_RANGE_PERSON_M} м, БПЛА {DETECTION_RANGE_DRONE_M} м")
print(f"Масса: {MASS_G} г, стоимость: {COST/1e3:.0f} тыс. ₽")
print(f"Рынок: {MARKET} × {COST/1e3:.0f} тыс. = {MARKET*COST/1e9:.0f} млрд ₽")
''',

    "05_autopilot-5": '''import math
GRID_SIZE_M = 100
GRID_RESOLUTION_M = 0.1
GRID_CELLS = int(GRID_SIZE_M / GRID_RESOLUTION_M) ** 2
LIDAR_RANGE_M = 12
LIDAR_RPM = 10
LIDAR_POINTS_PER_SCAN = int(LIDAR_RANGE_M * 2 * math.pi / GRID_RESOLUTION_M)
SLAM_UPDATE_HZ = 10
POSE_ACCURACY_CM = 5
PATH_PLANNING_TIME_MS = 50
DWA_LOOKAHEAD_S = 2.0
PID_KP = 1.0
PID_KI = 0.1
PID_KD = 0.05
MAX_SPEED_MS = 1.0
MAX_ACCELERATION = 0.5
CAN_BAUD = 500000
MAVLINK_HZ = 50
POWER_W = 15
MASS_G = 500
COST_SW = 0
COST_LICENSE = 500000
MARKET = 50000
print("=== АвтоПилот-5 ===")
print(f"Сетка: {GRID_SIZE_M}×{GRID_SIZE_M} м, {GRID_CELLS} ячеек")
print(f"LiDAR: {LIDAR_RANGE_M} м, {LIDAR_RPM} об/с")
print(f"SLAM: {POSE_ACCURACY_CM} см, {SLAM_UPDATE_HZ} Гц")
print(f"Планирование: {PATH_PLANNING_TIME_MS} мс")
print(f"PID: Kp={PID_KP}, Ki={PID_KI}, Kd={PID_KD}")
print(f"CAN: {CAN_BAUD/1e3:.0f} кбит/с, MAVLink: {MAVLINK_HZ} Гц")
print(f"Масса: {MASS_G} г")
print(f"Рынок: {MARKET} × {COST_LICENSE/1e3:.0f} тыс. = {MARKET*COST_LICENSE/1e9:.0f} млрд ₽")
''',

    "06_akustikmon-6": '''import math
SAMPLE_RATE = 48000
FFT_SIZE = 4096
FREQ_RESOLUTION = SAMPLE_RATE / FFT_SIZE
TIME_WINDOW_MS = FFT_SIZE / SAMPLE_RATE * 1000
SNR_DB = 65
F0_MIN = 60
F0_MAX = 600
BREATHING_RATE_MIN = 8
BREATHING_RATE_MAX = 40
COUGH_FREQ_MIN = 100
COUGH_FREQ_MAX = 1000
MFCC_FEATURES = 13
ML_CLASSES = 5
ML_ACCURACY = 0.92
MASS_G = 30
BATTERY_H = 100
COST = 50000
MARKET = 100000
print("=== АкустикМон-6 ===")
print(f"Микрофон: {SAMPLE_RATE/1000:.0f} кГц, SNR={SNR_DB} дБ")
print(f"FFT: {FFT_SIZE} точек, разрешение={FREQ_RESOLUTION:.1f} Гц, окно={TIME_WINDOW_MS:.0f} мс")
print(f"F0 голоса: {F0_MIN}-{F0_MAX} Гц")
print(f"Дыхание: {BREATHING_RATE_MIN}-{BREATHING_RATE_MAX} в мин")
print(f"Кашель: {COUGH_FREQ_MIN}-{COUGH_FREQ_MAX} Гц")
print(f"MFCC: {MFCC_FEATURES} коэф., ML: {ML_CLASSES} классов, точность={ML_ACCURACY*100:.0f}%")
print(f"Масса: {MASS_G} г, автономность: {BATTERY_H} ч")
print(f"Стоимость: {COST/1e3:.0f} тыс. ₽")
print(f"Рынок: {MARKET} × {COST/1e3:.0f} тыс. = {MARKET*COST/1e9:.0f} млрд ₽")
''',
}

for key, code in MODELS.items():
    path = os.path.join(BASE, key, "02_raschety/model.py")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(code)
    print(f"  ✓ {path}")

print("\nRunning all models...")
for key in MODELS:
    path = os.path.join(BASE, key, "02_raschety/model.py")
    print(f"\n--- {key} ---")
    exec(open(path).read())