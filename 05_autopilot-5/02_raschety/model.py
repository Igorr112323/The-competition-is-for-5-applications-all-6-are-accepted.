import math

LIDAR_RANGE_M = 12
LIDAR_ANGULAR_RES_DEG = 1.0
LIDAR_POINTS = int(360 / LIDAR_ANGULAR_RES_DEG)
LIDAR_SCAN_HZ = 10
LIDAR_RANGE_NOISE_MM = 30

IMU_ACCEL_NOISE_MG = 5
IMU_GYRO_NOISE_DPS = 0.01
IMU_DRIFT_DPS = 0.5
IMU_HZ = 100

ODOMETRY_PPR = 400
WHEEL_DIAMETER_M = 0.15
WHEEL_CIRCUMFERENCE = math.pi * WHEEL_DIAMETER_M
ODOMETRY_RES_M = WHEEL_CIRCUMFERENCE / ODOMETRY_PPR
WHEELBASE_M = 0.35

CAMERA_HZ = 30
CAMERA_FOV_DEG = 80
CAMERA_RES = 640

GRID_SIZE_M = 100
GRID_RES_M = 0.1
GRID_CELLS = int(GRID_SIZE_M / GRID_RES_M)

def slam_position_error(lidar_noise_m, imu_drift_dps, odometry_noise_m, dt, n_steps):
    lidar_accum = 0
    imu_accum = 0
    odo_accum = 0
    for _ in range(n_steps):
        lidar_accum += lidar_noise_m**2
        imu_accum += (imu_drift_dps * dt)**2
        odo_accum += odometry_noise_m**2
    return math.sqrt(lidar_accum + imu_accum + odo_accum)

lidar_noise_m = LIDAR_RANGE_NOISE_MM / 1000
imu_drift_per_step = IMU_DRIFT_DPS * (1/LIDAR_SCAN_HZ)
odo_noise_m = ODOMETRY_RES_M

n_steps_1min = LIDAR_SCAN_HZ * 60
n_steps_5min = LIDAR_SCAN_HZ * 300
n_steps_10min = LIDAR_SCAN_HZ * 600

error_1min = slam_position_error(lidar_noise_m, IMU_DRIFT_DPS, odo_noise_m, 1/LIDAR_SCAN_HZ, n_steps_1min)
error_5min = slam_position_error(lidar_noise_m, IMU_DRIFT_DPS, odo_noise_m, 1/LIDAR_SCAN_HZ, n_steps_5min)
error_10min = slam_position_error(lidar_noise_m, IMU_DRIFT_DPS, odo_noise_m, 1/LIDAR_SCAN_HZ, n_steps_10min)

ASTAR_GRID = 100
ASTAR_NODES = ASTAR_GRID * ASTAR_GRID
ASTAR_TIME_EST_S = 0.05
DWA_LOOKAHEAD_S = 2.0
DWA_MAX_SPEED_MS = 1.0
DWA_MAX_ACCEL_MS2 = 0.5
DWA_MIN_CLEARANCE_M = 0.3

PID_KP = 1.0
PID_KI = 0.1
PID_KD = 0.05

def pid_step(error, prev_error, integral, dt):
    integral += error * dt
    derivative = (error - prev_error) / dt
    output = PID_KP * error + PID_KI * integral + PID_KD * derivative
    return output, integral

CAN_BAUD = 500000
CAN_MSG_SIZE_BITS = 128
CAN_MSG_TIME_MS = CAN_MSG_SIZE_BITS / CAN_BAUD * 1000
MAVLINK_HZ = 50
MAVLINK_MSG_SIZE_BYTES = 17

ROS2_HZ = 100
COMPUTE_GFLOPS = 472
SLAM_COMPUTE_MS = 8

TOTAL_PIPELINE_MS = SLAM_COMPUTE_MS + CAN_MSG_TIME_MS + 1000/MAVLINK_HZ
EFFECTIVE_HZ = 1000 / TOTAL_PIPELINE_MS

MASS_G = 500
POWER_STM32_W = 0.5
POWER_JETSON_W = 5.0
POWER_LIDAR_W = 2.0
POWER_MOTORS_W = 20.0
POWER_TOTAL_W = POWER_STM32_W + POWER_JETSON_W + POWER_LIDAR_W + POWER_MOTORS_W
BATTERY_WH = 100
BATTERY_H = BATTERY_WH / POWER_TOTAL_W

COST_LICENSE_RUB = 500000
MARKET_PLATFORMS = 50000
MARKET_VALUE = MARKET_PLATFORMS * COST_LICENSE_RUB

print("=== АвтоПилот-5: Расчёт SLAM + навигация ===")
print()
print("--- LiDAR ---")
print(f"Дальность: {LIDAR_RANGE_M} м")
print(f"Разрешение: {LIDAR_ANGULAR_RES_DEG}°, {LIDAR_POINTS} точек/скан")
print(f"Частота сканирования: {LIDAR_SCAN_HZ} Гц")
print(f"Шум: ±{LIDAR_RANGE_NOISE_MM} мм")
print()
print("--- IMU ---")
print(f"Шум акселерометра: {IMU_ACCEL_NOISE_MG} мg")
print(f"Шум гироскопа: {IMU_GYRO_NOISE_DPS} °/с")
print(f"Дрейф: {IMU_DRIFT_DPS} °/с")
print(f"Частота: {IMU_HZ} Гц")
print()
print("--- Одометрия ---")
print(f"Энкодер: {ODOMETRY_PPR} имп/об")
print(f"Колесо: ⌀{WHEEL_DIAMETER_M*1000:.0f} мм, L={WHEEL_CIRCUMFERENCE*1000:.1f} мм")
print(f"Разрешение: {ODOMETRY_RES_M*1000:.2f} мм/импульс")
print(f"Колея: {WHEELBASE_M*1000:.0f} мм")
print()
print("--- SLAM: накопление ошибки позиционирования ---")
print(f"  1 мин: ±{error_1min*100:.1f} см")
print(f"  5 мин: ±{error_5min*100:.1f} см")
print(f"  10 мин: ±{error_10min*100:.1f} см")
print()
print("--- Планирование пути (A* + DWA) ---")
print(f"Сетка: {ASTAR_GRID}×{ASTAR_GRID} = {ASTAR_NODES} узлов")
print(f"Время планирования: ~{ASTAR_TIME_EST_S*1000:.0f} мс")
print(f"DWA: горизонт={DWA_LOOKAHEAD_S} с, Vmax={DWA_MAX_SPEED_MS} м/с")
print(f"Зазор безопасности: {DWA_MIN_CLEARANCE_M} м")
print()
print("--- PID-регулятор ---")
print(f"Kp={PID_KP}, Ki={PID_KI}, Kd={PID_KD}")
integral = 0
prev_err = 0
errors = []
for step in range(100):
    err = max(0, 1.0 - step * 0.015)
    output, integral = pid_step(err, prev_err, integral, 0.1)
    errors.append(err)
    prev_err = err
print(f"Ошибка на шаге 0: {errors[0]:.3f}, на шаге 100: {errors[-1]:.3f}")
print()
print("--- Интерфейсы ---")
print(f"CAN: {CAN_BAUD/1000:.0f} кбит/с, сообщение: {CAN_MSG_TIME_MS:.2f} мс")
print(f"MAVLink: {MAVLINK_HZ} Гц, {MAVLINK_MSG_SIZE_BYTES} байт/сообщение")
print(f"ROS2: {ROS2_HZ} Гц")
print(f"Jetson: {COMPUTE_GFLOPS} GFLOPS, SLAM: {SLAM_COMPUTE_MS} мс")
print(f"Общий pipeline: {TOTAL_PIPELINE_MS:.1f} мс ({EFFECTIVE_HZ:.0f} Гц)")
print()
print("--- Питание ---")
print(f"Потребление: {POWER_TOTAL_W:.1f} Вт")
print(f"Автономность: {BATTERY_H:.1f} ч")
print(f"Масса: {MASS_G} г")
print()
print("--- Рынок ---")
print(f"Стоимость лицензии: {COST_LICENSE_RUB/1e3:.0f} тыс. ₽ (open source + поддержка)")
print(f"Платформы: {MARKET_PLATFORMS}")
print(f"Рынок: {MARKET_PLATFORMS} × {COST_LICENSE_RUB/1e3:.0f} тыс. = {MARKET_VALUE/1e9:.0f} млрд ₽")