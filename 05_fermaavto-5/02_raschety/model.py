import math
import random

HOUSE_LENGTH = 100
HOUSE_WIDTH = 15
HOUSE_AREA = HOUSE_LENGTH * HOUSE_WIDTH
GRID_RESOLUTION = 0.1
GRID_CELLS = int(HOUSE_LENGTH / GRID_RESOLUTION) * int(HOUSE_WIDTH / GRID_RESOLUTION)

CAMERA_FPS = 60
CAMERA_RESOLUTION = (1280, 800)
VISUAL_FEATURES = 1000
VO_FRAME_TIME = 1.0 / CAMERA_FPS
FEATURE_TRACKING_ERROR = 0.02
VO_ACCURACY_PER_M = FEATURE_TRACKING_ERROR * math.sqrt(VISUAL_FEATURES / 100)

UZ_COUNT = 6
UZ_RANGE_MAX = 4.0
UZ_RANGE_MIN = 0.03
UZ_ACCURACY = 0.002
UZ_ANGULAR_COVERAGE = 360

IMU_FREQ = 100
IMU_ACCEL_NOISE = 0.005
IMU_GYRO_NOISE = 0.01
IMU_DRIFT_PER_HOUR = 0.5

ODOMETRY_PPR = 400
WHEEL_DIAMETER = 0.15
WHEEL_CIRCUMFERENCE = math.pi * WHEEL_DIAMETER
ODOMETRY_ACCURACY = 1.0

KALMAN_UPDATE_FREQ = 30
POSITION_ACCURACY = math.sqrt(
    VO_ACCURACY_PER_M**2 +
    UZ_ACCURACY**2 +
    (ODOMETRY_ACCURACY / 100)**2 +
    (IMU_DRIFT_PER_HOUR / 3600)**2
) * 100

ROBOT_SPEED_MIN = 0.1
ROBOT_SPEED_MAX = 0.5
OBSTACLE_DETECTION_RANGE = 0.5
PATH_PLANNING_TIME = 0.05

CV_HOG_FEATURES = 3780
CV_SVM_CLASSES = 4
CV_TRAINING_IMAGES = 1000
CV_TEST_IMAGES = 200
CV_BASE_ACCURACY = 0.82
CV_WITH_MULTI_SENSOR = 0.87

POULTRY_HOUSE_POPULATION = 100000
FEED_PER_BIRD_KG = 0.12
FEED_PER_DAY_TON = POULTRY_HOUSE_POPULATION * FEED_PER_BIRD_KG / 1000
WORKERS_COUNT = 20
WORKER_SALARY_MONTH = 50000
LABOR_COST_YEAR = WORKERS_COUNT * WORKER_SALARY_MONTH * 12
AUTOMATION_SAVING_PCT = 60
SAVING_LABOR = LABOR_COST_YEAR * AUTOMATION_SAVING_PCT / 100

MORTALITY_WITHOUT_CV = 5.0
MORTALITY_WITH_CV = 3.0
BIRD_PRICE = 350
MORTALITY_SAVING = POULTRY_HOUSE_POPULATION * (MORTALITY_WITHOUT_CV - MORTALITY_WITH_CV) / 100 * BIRD_PRICE

TOTAL_SAVING = SAVING_LABOR + MORTALITY_SAVING
SYSTEM_COST = 3000000
PAYBACK_MONTHS = SYSTEM_COST / (TOTAL_SAVING / 12)

MARKET_POULTRY_FARMS = 3000
MARKET_CATTLE_FARMS = 100000
MARKET_PIG_FARMS = 5000
MARKET_VALUE_POULTRY = MARKET_POULTRY_FARMS * SYSTEM_COST

ASTAR_GRID_SIZE = 100
ASTAR_NODES = ASTAR_GRID_SIZE * ASTAR_GRID_SIZE
ASTAR_TIME_ESTIMATE = 0.01

def simulate_navigation_error(steps, vo_accuracy, uz_accuracy, speed):
    total_error = 0
    for i in range(steps):
        vo_err = random.gauss(0, vo_accuracy)
        uz_err = random.gauss(0, uz_accuracy)
        step_error = math.sqrt(vo_err**2 + uz_err**2)
        total_error += step_error
    return total_error / steps * 100

random.seed(42)
nav_errors = [simulate_navigation_error(100, VO_ACCURACY_PER_M, UZ_ACCURACY, ROBOT_SPEED_MAX) for _ in range(10)]
avg_nav_error = sum(nav_errors) / len(nav_errors)

print("=== ФермаАвто-5: Расчёт навигационного модуля ===")
print(f"Птичник: {HOUSE_LENGTH}×{HOUSE_WIDTH} м = {HOUSE_AREA} м²")
print(f"Сетка: {GRID_CELLS} ячеек ({GRID_RESOLUTION} м)")
print()
print("=== Сенсоры ===")
print(f"Камера: {CAMERA_RESOLUTION[0]}×{CAMERA_RESOLUTION[1]}, {CAMERA_FPS} fps")
print(f"VO точность: {VO_ACCURACY_PER_M*100:.2f} см/м")
print(f"УЗ-дальномеры: {UZ_COUNT} шт, диапазон {UZ_RANGE_MIN}-{UZ_RANGE_MAX} м, точность {UZ_ACCURACY*100:.1f} см")
print(f"IMU: {IMU_FREQ} Гц, дрейф {IMU_DRIFT_PER_HOUR}°/ч")
print(f"Одометрия: {ODOMETRY_PPR} имп/об, точность {ODOMETRY_ACCURACY} см/м")
print()
print("=== Навигация ===")
print(f"Частота обновления Калмана: {KALMAN_UPDATE_FREQ} Гц")
print(f"Суммарная точность позиционирования: ±{POSITION_ACCURACY:.1f} см")
print(f"Смоделированная ошибка навигации: ±{avg_nav_error:.2f} см")
print(f"Рабочая скорость: {ROBOT_SPEED_MIN}-{ROBOT_SPEED_MAX} м/с")
print(f"Обнаружение препятствий: ≥{OBSTACLE_DETECTION_RANGE} м")
print(f"Планирование пути A*: ~{ASTAR_TIME_ESTIMATE*1000:.0f} мс")
print()
print("=== CV ===")
print(f"HOG-признаков: {CV_HOG_FEATURES}")
print(f"Классов: {CV_SVM_CLASSES}")
print(f"Обучающая выборка: {CV_TRAINING_IMAGES} изображений")
print(f"Точность (базовая): {CV_BASE_ACCURACY*100:.0f}%")
print(f"Точность (мультисенсор): {CV_WITH_MULTI_SENSOR*100:.0f}%")
print()
print("=== Экономика ===")
print(f"Птицефабрика: {POULTRY_HOUSE_POPULATION} голов")
print(f"Персонал: {WORKERS_COUNT} чел. × {WORKER_SALARY_MONTH/1e3:.0f} тыс. ₽/мес = {LABOR_COST_YEAR/1e6:.1f} млн ₽/год")
print(f"Автоматизация ({AUTOMATION_SAVING_PCT}%): {SAVING_LABOR/1e6:.1f} млн ₽/год")
print(f"Снижение падежа: {MORTALITY_WITHOUT_CV}% → {MORTALITY_WITH_CV}% = {MORTALITY_SAVING/1e6:.1f} млн ₽/год")
print(f"Общая экономия: {TOTAL_SAVING/1e6:.1f} млн ₽/год")
print(f"Стоимость системы: {SYSTEM_COST/1e6:.0f} млн ₽")
print(f"Окупаемость: {PAYBACK_MONTHS:.1f} мес.")
print()
print("=== Рынок ===")
print(f"Птицефабрики: {MARKET_POULTRY_FARMS} × {SYSTEM_COST/1e6:.0f} млн ₽ = {MARKET_VALUE_POULTRY/1e9:.0f} млрд ₽")
print(f"Фермы КРС: {MARKET_CATTLE_FARMS}")
print(f"Свинокомплексы: {MARKET_PIG_FARMS}")