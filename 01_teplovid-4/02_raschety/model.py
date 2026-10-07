import math
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
