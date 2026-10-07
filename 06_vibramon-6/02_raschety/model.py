import math

ADXL355_RANGE = 2
ADXL355_NOISE_UG = 25
ADXL355_BANDWIDTH = 1500
ADC_RESOLUTION = 20
FS_HZ = 10000
FFT_SIZE = 1024
FREQ_RESOLUTION = FS_HZ / FFT_SIZE
TIME_WINDOW = FFT_SIZE / FS_HZ

AE_FREQ_MIN = 20000
AE_FREQ_MAX = 100000
AE_SENSITIVITY_DB = -60

PT100_RANGE = (-40, 150)
PT100_ACCURACY = 0.5
CT_RANGE = (0, 500)
CT_ACCURACY_PCT = 2.0

BEARING_TYPES = {
    "6205": {"bpfo": 3.16, "bpfi": 4.84, "ftf": 0.40, "bsf": 2.06},
    "6308": {"bpfo": 3.58, "bpfi": 5.42, "ftf": 0.40, "bsf": 2.32},
    "6412": {"bpfo": 3.05, "bpfi": 4.95, "ftf": 0.40, "bsf": 2.02},
}

COMBINE_RPM = 1800
COMBINE_SHAFT_FREQ = COMBINE_RPM / 60
GEAR_TEETH = 32
GEAR_MESH_FREQ = COMBINE_SHAFT_FREQ * GEAR_TEETH
THRESHALD_VELOCITY_MM_S = 4.5
THRESHOLD_ACCELERATION_G = 0.5

def order_tracking_error(rpm_variability_pct):
    return rpm_variability_pct * 0.02

def spectral_kurtosis_sensitivity(snr_db, fft_size):
    return max(0, (snr_db - 10) * math.log2(fft_size) / 10)

def bearing_fault_frequency(rpm, bearing_type, fault_type):
    shaft_freq = rpm / 60
    bearing = BEARING_TYPES[bearing_type]
    if fault_type == "outer":
        return shaft_freq * bearing["bpfo"]
    elif fault_type == "inner":
        return shaft_freq * bearing["bpfi"]
    elif fault_type == "ball":
        return shaft_freq * bearing["bsf"]
    elif fault_type == "cage":
        return shaft_freq * bearing["ftf"]
    return 0

def envelope_analysis_improvement(snr_db, fault_freq, bandwidth):
    resonant_gain = 20 * math.log10(bandwidth / fault_freq) if fault_freq > 0 else 0
    return snr_db + resonant_gain

def detection_range_hours(defect_stage):
    stages = {1: 500, 2: 200, 3: 50, 4: 10}
    return stages.get(defect_stage, 0)

MACHINES = 200000
DOWNTIME_COST_RUB = 1500000
PREVENTION_RATE = 0.02
AVOIDED_EVENTS = MACHINES * PREVENTION_RATE
SAVING_PER_EVENT = DOWNTIME_COST_RUB
TOTAL_SAVING = AVOIDED_EVENTS * SAVING_PER_EVENT

SYSTEM_COST = 150000
PAYBACK_HA = SYSTEM_COST / DOWNTIME_COST_RUB

MAINTENANCE_SAVING_PCT = 35
ANNUAL_MAINTENANCE_COST = 500000
MAINTENANCE_SAVING = ANNUAL_MAINTENANCE_COST * MAINTENANCE_SAVING_PCT / 100

MARKET_COMBINES = 150000
MARKET_TRACTORS = 50000
MARKET_GRAIN_EQUIP = 30000
MARKET_VALUE = MARKET_COMBINES * SYSTEM_COST

print("=== ВибраМон-6: Расчёт системы мониторинга ===")
print()
print("=== Сенсорный узел ===")
print(f"ADXL355: ±{ADXL355_RANGE}g, шум {ADXL355_NOISE_UG} мкг/√Гц, полоса {ADXL355_BANDWIDTH} Гц")
print(f"АЦП: {ADC_RESOLUTION} бит, Fs = {FS_HZ} Гц")
print(f"FFT: {FFT_SIZE} точек, разрешение {FREQ_RESOLUTION:.1f} Гц, окно {TIME_WINDOW*1000:.1f} мс")
print(f"Температура: {PT100_RANGE[0]}…{PT100_RANGE[1]}°C, ±{PT100_ACCURACY}°C")
print(f"Ток: {CT_RANGE[0]}-{CT_RANGE[1]} А, ±{CT_ACCURACY_PCT}%")
print()
print(f"=== Частоты дефектов (комбайн, {COMBINE_RPM} об/мин) ===")
print(f"Частота вала: {COMBINE_SHAFT_FREQ:.1f} Гц")
print(f"Частота зацепления шестерни ({GEAR_TEETH} зуб): {GEAR_MESH_FREQ:.1f} Гц")
for btype, freqs in BEARING_TYPES.items():
    outer_f = bearing_fault_frequency(COMBINE_RPM, btype, "outer")
    inner_f = bearing_fault_frequency(COMBINE_RPM, btype, "inner")
    ball_f = bearing_fault_frequency(COMBINE_RPM, btype, "ball")
    cage_f = bearing_fault_frequency(COMBINE_RPM, btype, "cage")
    print(f"  Подшипник {btype}: BPFO={outer_f:.1f} Гц, BPFI={inner_f:.1f} Гц, BSF={ball_f:.1f} Гц, FTF={cage_f:.1f} Гц")
print()
print("=== Order tracking ===")
for var_pct in [5, 10, 20]:
    err = order_tracking_error(var_pct)
    print(f"  Вариация оборотов ±{var_pct}%: ошибка order tracking = {err*100:.2f}%")
print()
print("=== Спектральная куртозис ===")
for snr in [10, 20, 30]:
    sk = spectral_kurtosis_sensitivity(snr, FFT_SIZE)
    print(f"  SNR={snr} дБ: чувствительность куртозиса = {sk:.1f}")
print()
print("=== Огибающий анализ ===")
for snr in [10, 20]:
    for bw in [1000, 5000]:
        impr = envelope_analysis_improvement(snr, 100, bw)
        print(f"  SNR={snr} дБ, полоса={bw} Гц: улучшение SNR = {impr:.1f} дБ")
print()
print("=== Диагностика ===")
print(f"Порог вибрации (ISO 10816): {THRESHALD_VELOCITY_MM_S} мм/с")
print(f"Порог ускорения: {THRESHOLD_ACCELERATION_G}g")
for stage in [1, 2, 3, 4]:
    hours = detection_range_hours(stage)
    print(f"  Стадия {stage}: прогноз за {hours} ч до отказа")
print()
print("=== Экономика ===")
print(f"Парк техники: {MACHINES} машин")
print(f"Стоимость аварии: {DOWNTIME_COST_RUB/1e6:.1f} млн ₽")
print(f"Предотвращённых аварий/год: {AVOIDED_EVENTS:.0f}")
print(f"Экономия (аварии): {TOTAL_SAVING/1e9:.1f} млрд ₽/год (весь парк)")
print(f"Стоимость комплекта: {SYSTEM_COST/1e3:.0f} тыс. ₽")
print(f"Окупаемость: 1 авария = {DOWNTIME_COST_RUB/SYSTEM_COST:.0f} комплектов")
print(f"ТО экономия ({MAINTENANCE_SAVING_PCT}%): {MAINTENANCE_SAVING/1e3:.0f} тыс. ₽/год на машину")
print()
print("=== Рынок ===")
print(f"Комбайны: {MARKET_COMBINES} × {SYSTEM_COST/1e3:.0f} тыс. ₽ = {MARKET_VALUE/1e9:.0f} млрд ₽")
print(f"Тракторы: {MARKET_TRACTORS}")
print(f"Зерноочистительное: {MARKET_GRAIN_EQUIP}")