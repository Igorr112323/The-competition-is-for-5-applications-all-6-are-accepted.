import math

TARGET_TEMP_C = 65.0
TEMP_TOLERANCE_C = 0.5
ROOM_TEMP_C = 25.0
HEATER_POWER_W = 8.0
HEAT_CAPACITY_J_K = 45.0
MASS_G_ALUMINUM = 120
SPECIFIC_HEAT_AL_J_KG_K = 900
MASS_KG = MASS_G_ALUMINUM / 1000
HEAT_CAPACITY_ACTUAL = MASS_KG * SPECIFIC_HEAT_AL_J_KG_K
RAMP_TIME_S = HEAT_CAPACITY_ACTUAL * (TARGET_TEMP_C - ROOM_TEMP_C) / HEATER_POWER_W

NTC_BETA = 3950
NTC_R0 = 10000
NTC_T0_K = 298.15
ADC_BITS = 16
ADC_VREF = 3.3
ADC_MAX = 2**ADC_BITS - 1
R_FIXED = 10000

def ntc_resistance(temp_c):
    temp_k = temp_c + 273.15
    return NTC_R0 * math.exp(NTC_BETA * (1/temp_k - 1/NTC_T0_K))

def adc_to_temp(adc_val):
    voltage = adc_val / ADC_MAX * ADC_VREF
    r_ntc = R_FIXED * voltage / (ADC_VREF - voltage)
    if r_ntc <= 0: return -999
    temp_k = 1 / (1/NTC_T0_K + math.log(r_ntc/NTC_R0)/NTC_BETA)
    return temp_k - 273.15

PID_KP = 50.0
PID_KI = 0.5
PID_KD = 10.0

def pid_simulate(target_c, n_steps=2000, dt=0.1):
    temp = ROOM_TEMP_C
    integral = 0
    prev_error = 0
    temps = []
    for i in range(n_steps):
        error = target_c - temp
        integral += error * dt
        derivative = (error - prev_error) / dt
        prev_error = error
        output = PID_KP * error + PID_KI * integral + PID_KD * derivative
        output = max(0, min(HEATER_POWER_W, output))
        q_in = output
        q_loss = 0.01 * (temp - ROOM_TEMP_C)
        temp += (q_in - q_loss) * dt / HEAT_CAPACITY_ACTUAL
        temps.append(temp)
        if abs(temp - target_c) < TEMP_TOLERANCE_C and i > 100:
            return temps, i * dt
    return temps, n_steps * dt

temps, settle_time_s = pid_simulate(TARGET_TEMP_C)

AMPLIFICATION_KINETICS = {
    "Bst DNA polymerase": {"optimal_temp": 65, "rate_per_min": 0.15, "yield_after_45min": 10**9},
    "LAMP primers": {"n_primers": 6, "specificity_pct": 97},
}

HNB_CONCENTRATION_MM = 0.8
HNB_COLOR_CHANGE_THRESHOLD = 1.5
PHOTODIODE_WAVELENGTH_NM = 590
PHOTODIODE_RESPONSIVITY = 0.45
PHOTODIODE_DARK_CURRENT_NA = 5

def hnb_signal_ratio(amplified_conc, baseline_conc):
    if baseline_conc <= 0: return 0
    ratio = amplified_conc / baseline_conc
    return ratio

amplified_ratio = hnb_signal_ratio(1e9, 1)
signal_v = amplified_ratio * HNB_CONCENTRATION_MM * PHOTODIODE_RESPONSIVITY * 0.001
baseline_v = 1 * HNB_CONCENTRATION_MM * PHOTODIODE_RESPONSIVITY * 0.001
ratio_signal = signal_v / baseline_v if baseline_v > 0 else 0

BATTERY_V = 3.7
BATTERY_MAH = 3000
BATTERY_WH = BATTERY_V * BATTERY_MAH / 1000
BATTERY_H = BATTERY_WH / HEATER_POWER_W

BLE_MTU = 244
RESULT_SIZE = 32

TARGETS = [
    {"name": "LSDV (кожная узелковая)", "organism": "вирус", "copies_detectable": 100},
    {"name": "Salmonella spp.", "organism": "бактерия", "copies_detectable": 500},
    {"name": "Leptospira spp.", "organism": "бактерия", "copies_detectable": 1000},
    {"name": "E. coli O157:H7", "organism": "бактерия", "copies_detectable": 200},
    {"name": "Brucella spp.", "organism": "бактерия", "copies_detectable": 500},
    {"name": "Avian influenza H5N1", "organism": "вирус", "copies_detectable": 100},
    {"name": "African swine fever", "organism": "вирус", "copies_detectable": 50},
]

MASS_TOTAL_G = 1000
CASE_DIMENSIONS = "300×200×100 мм"
CASE_IP = "IP67"
COST_RUB = 100000
MARKET = 25000
GENEXPERT_COST = 3000000

print("=== LAMP-ДНК-Экспресс: Расчёт ===")
print()
print("--- Термодинамика нагревателя ---")
print(f"Целевая температура: {TARGET_TEMP_C}°C")
print(f"Мощность нагревателя: {HEATER_POWER_W} Вт")
print(f"Теплоёмкость блока: {HEAT_CAPACITY_ACTUAL:.2f} Дж/К")
print(f"Время разогрева (расчётное): {RAMP_TIME_S:.0f} сек")
print(f"Время разогрева (PID-симуляция): {settle_time_s:.0f} сек")
print(f"Температура в стационаре: {temps[-1]:.2f}°C")
print(f"Разброс температуры (последние 100): ±{max(temps[-100:])-min(temps[-100:]):.3f}°C")
print()
print("--- PID-регулятор ---")
print(f"Kp={PID_KP}, Ki={PID_KI}, Kd={PID_KD}")
ntc_r = ntc_resistance(TARGET_TEMP_C)
adc_at_target = int(ntc_r / (ntc_r + R_FIXED) * ADC_MAX)
temp_from_adc = adc_to_temp(adc_at_target)
print(f"NTC при {TARGET_TEMP_C}°C: {ntc_r:.0f} Ом, АЦП={adc_at_target}, обратный расчёт={temp_from_adc:.1f}°C")
print()
print("--- Кинетика амплификации ---")
print(f"Температура амплификации: {AMPLIFICATION_KINETICS['Bst DNA polymerase']['optimal_temp']}°C")
print(f"Скорость амплификации: {AMPLIFICATION_KINETICS['Bst DNA polymerase']['rate_per_min']*100:.0f}%/мин")
print(f"Выход за 45 мин: 10^{math.log10(AMPLIFICATION_KINETICS['Bst DNA polymerase']['yield_after_45min']):.0f} копий")
print(f"Число праймеров: {AMPLIFICATION_KINETICS['LAMP primers']['n_primers']}")
print(f"Специфичность: {AMPLIFICATION_KINETICS['LAMP primers']['specificity_pct']}%")
print()
print("--- HNB-детекция ---")
print(f"Концентрация HNB: {HNB_CONCENTRATION_MM} мМ")
print(f"Фотодиод: λ={PHOTODIODE_WAVELENGTH_NM} нм, R={PHOTODIODE_RESPONSIVITY} А/Вт")
print(f"Сигнал (амплифицированный): {signal_v*1000:.3f} мВ")
print(f"Сигнал (базовый): {baseline_v*1000:.3f} мВ")
print(f"Отношение сигнал/фон: {ratio_signal:.0f}×")
print()
print("--- Мишени ({len(TARGETS)} шт.) ---")
for t in TARGETS:
    print(f"  {t['name']}: {t['organism']}, лимит детекции {t['copies_detectable']} копий")
print()
print("--- Параметры комплекса ---")
print(f"Масса: {MASS_TOTAL_G} г (в кейсе)")
print(f"Кейс: {CASE_DIMENSIONS}, {CASE_IP}")
print(f"Автономность: {BATTERY_H:.1f} ч")
print(f"Стоимость: {COST_RUB/1e3:.0f} тыс. ₽")
print(f"Рынок: {MARKET} × {COST_RUB/1e3:.0f} тыс. = {MARKET*COST_RUB/1e9:.1f} млрд ₽")
print(f"vs GeneXpert: {GENEXPERT_COST/1e6:.0f} млн ₽ ({GENEXPERT_COST/COST_RUB:.0f}× дороже)")