import math

LAMBDA_MIN = 900e-9
LAMBDA_MAX = 1700e-9
N_POINTS = 80
DELTA_LAMBDA = (LAMBDA_MAX - LAMBDA_MIN) / N_POINTS
SLIT_WIDTH = DELTA_LAMBDA
GRATING_LINES = 300
GRATING_ANGLE = math.degrees(math.asin(GRATING_LINES * (LAMBDA_MIN + LAMBDA_MAX) / 2))
FOCAL_LENGTH = 50e-3
SPOT_SIZE = 2.44 * (LAMBDA_MIN + LAMBDA_MAX) / 2 * FOCAL_LENGTH / (5e-3)
PIXEL_SIZE = 25e-6
PIXELS_PER_POINT = int(SLIT_WIDTH / PIXEL_SIZE * 10)

LED_POWER_MW = 50
DETECTOR_RESPONSIVITY = 0.9
SIGNAL_V = LED_POWER_MW * 1e-3 * DETECTOR_RESPONSIVITY
NOISE_UV = 5
SNR_DB = 20 * math.log10(SIGNAL_V * 1e6 / NOISE_UV) if NOISE_UV > 0 else 0

UV_254_POWER_MW = 10
UV_365_POWER_MW = 15
FLUORESCENCE_QY = 0.05
FLUORESCENCE_SIGNAL = UV_365_POWER_MW * 1e-3 * FLUORESCENCE_QY * 0.3

PH_RANGE = (0, 14)
PH_ACCURACY = 0.1
CONDUCTIVITY_RANGE = (0, 20)
CONDUCTIVITY_ACCURACY = 0.5

CALIBRATION_SPECTRA = 500
MATERIALS = 10
SPECTRA_PER_MATERIAL = CALIBRATION_SPECTRA // MATERIALS

def mnk_error(n_spectra, snr_db, n_params=4):
    base_error = 100 / (snr_db * math.sqrt(n_spectra))
    return max(0.1, base_error * math.sqrt(n_params))

protein_error = mnk_error(SPECTRA_PER_MATERIAL, SNR_DB, 4)
fat_error = protein_error * 0.5
moisture_error = protein_error * 1.0
fiber_error = protein_error * 2.0

FARM_COWS = 200
FEED_KG_PER_COW_DAY = 10
DAYS_PER_YEAR = 365
FEED_TONNES = FARM_COWS * FEED_KG_PER_COW_DAY * DAYS_PER_YEAR / 1000
FEED_PRICE_RUB_TON = 15000
FEED_COST_RUB = FEED_TONNES * FEED_PRICE_RUB_TON
OPTIMIZATION_SAVING_PCT = 7.5
SAVING_RUB = FEED_COST_RUB * OPTIMIZATION_SAVING_PCT / 100
DEVICE_COST = 200000
PAYBACK_MONTHS = DEVICE_COST / (SAVING_RUB / 12)

FARM_HA = 500
GRAIN_PRICE_PREMIUM_PCT = 12
GRAIN_YIELD_TON_HA = 4.5
GRAIN_PRICE_RUB_TON = 25000
PREMIUM_RUB = FARM_HA * GRAIN_YIELD_TON_HA * GRAIN_PRICE_RUB_TON * GRAIN_PRICE_PREMIUM_PCT / 100

LAB_ANALYSIS_COST = 10000
SAMPLES_PER_YEAR = 200
LAB_SAVING = SAMPLES_PER_YEAR * LAB_ANALYSIS_COST
TOTAL_SAVING = SAVING_RUB + PREMIUM_RUB + LAB_SAVING

MARKET_FARMS = 50000
MARKET_MILITARY = 1000000
MARKET_MCHS = 85 * 2
MARKET_VALUE_FARMS = MARKET_FARMS * DEVICE_COST

print("=== СпектрАгро-П: Расчёт оптической системы ===")
print(f"NIR диапазон: {LAMBDA_MIN*1e9:.0f}-{LAMBDA_MAX*1e9:.0f} нм")
print(f"Точек спектра: {N_POINTS}")
print(f"Шаг: {DELTA_LAMBDA*1e9:.1f} нм")
print(f"Угол дифракции: {GRATING_ANGLE:.1f}°")
print(f"Размер пятна: {SPOT_SIZE*1e6:.0f} мкм")
print(f"SNR: {SNR_DB:.1f} дБ")
print(f"УФ-флуоресценция (365 нм): {FLUORESCENCE_SIGNAL*1e6:.1f} мкВ")
print()
print("=== Точность (расчётная оценка проекта) ===")
print(f"Протеин: ±{protein_error:.2f}%")
print(f"Жир: ±{fat_error:.2f}%")
print(f"Влага: ±{moisture_error:.2f}%")
print(f"Клетчатка: ±{fiber_error:.2f}%")
print(f"pH: ±{PH_ACCURACY}")
print(f"Электропроводность: ±{CONDUCTIVITY_ACCURACY} мСм/см")
print()
print("=== Экономика ===")
print(f"Ферма: {FARM_COWS} голов КРС")
print(f"Корм: {FEED_TONNES:.0f} т/год = {FEED_COST_RUB/1e6:.1f} млн ₽/год")
print(f"Оптимизация рациона: {OPTIMIZATION_SAVING_PCT}% = {SAVING_RUB/1e6:.2f} млн ₽/год")
print(f"Премия за сертифицированное зерно: {PREMIUM_RUB/1e6:.1f} млн ₽/год ({FARM_HA} га)")
print(f"Экономия на лаборатории: {LAB_SAVING/1e6:.2f} млн ₽/год ({SAMPLES_PER_YEAR} образцов)")
print(f"Общая экономия: {TOTAL_SAVING/1e6:.2f} млн ₽/год")
print(f"Стоимость прибора: {DEVICE_COST/1e3:.0f} тыс. ₽")
print(f"Окупаемость: {PAYBACK_MONTHS:.1f} мес.")
print()
print("=== Рынок ===")
print(f"Фермерские хозяйства: {MARKET_FARMS} × {DEVICE_COST/1e3:.0f} тыс. ₽ = {MARKET_VALUE_FARMS/1e9:.0f} млрд ₽")
print(f"ВС РФ: ~{MARKET_MILITARY} военнослужащих (контроль питания)")
print(f"МЧС: {MARKET_MCHS} аварийных лабораторий")