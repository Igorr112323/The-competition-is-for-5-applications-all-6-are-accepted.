import math
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
