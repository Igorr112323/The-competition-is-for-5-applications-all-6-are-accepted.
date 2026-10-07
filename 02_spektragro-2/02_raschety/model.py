import math

WAVELENGTHS_NM = list(range(900, 1701, 16))
N_POINTS = len(WAVELENGTHS_NM)
SPECTRAL_RESOLUTION_NM = 16
SNR_NIR_DB = 72
SNR_NIR_LINEAR = 10**(SNR_NIR_DB/20)

SAMPLE_PATH_LENGTH_CM = 2.5
MOLAR_ABSORPTIVITY = {
    "water":    {"peak_nm": 1450, "epsilon": 0.42, "baseline": 0.01},
    "protein":  {"peak_nm": 1520, "epsilon": 0.28, "baseline": 0.005},
    "lipid":    {"peak_nm": 1210, "epsilon": 0.35, "baseline": 0.008},
    "glucose":  {"peak_nm": 1590, "epsilon": 0.09, "baseline": 0.002},
}

def gaussian_absorbance(wavelength_nm, peak_nm, epsilon, sigma_nm=40):
    return epsilon * math.exp(-0.5 * ((wavelength_nm - peak_nm) / sigma_nm)**2)

def beer_lambert(epsilon, concentration_mol, path_cm):
    return epsilon * concentration_mol * path_cm

def compute_spectrum(concentrations):
    spectrum = []
    for wl in WAVELENGTHS_NM:
        absorbance = 0
        for analyte, conc in concentrations.items():
            params = MOLAR_ABSORPTIVITY[analyte]
            eps_at_wl = gaussian_absorbance(wl, params["peak_nm"], params["epsilon"])
            absorbance += beer_lambert(eps_at_wl, conc, SAMPLE_PATH_LENGTH_CM)
        transmission = 10**(-absorbance)
        spectrum.append(transmission)
    return spectrum

def snv_transform(spectrum):
    mean = sum(spectrum) / len(spectrum)
    std = math.sqrt(sum((x-mean)**2 for x in spectrum) / len(spectrum))
    return [(x-mean)/std if std > 1e-10 else 0 for x in spectrum]

def savitzky_golay_deriv(spectrum, window=5):
    deriv = []
    half = window // 2
    for i in range(len(spectrum)):
        if i < half or i >= len(spectrum) - half:
            deriv.append(0)
        else:
            deriv.append((spectrum[i+1] - spectrum[i-1]) / 2)
    return deriv

def mnk_calibrate(spectrum, reference):
    sum_xy = sum(x*y for x,y in zip(spectrum, reference))
    sum_xx = sum(x*x for x in spectrum)
    return sum_xy / sum_xx if sum_xx > 1e-10 else 0

def mnk_r_squared(spectrum, reference):
    n = len(spectrum)
    mean_s = sum(spectrum)/n
    mean_r = sum(reference)/n
    ss_res = sum((s-g*r)**2 for s,g in zip(spectrum, [mnk_calibrate(spectrum, reference)]*n))
    ss_tot = sum((s-mean_s)**2 for s in spectrum)
    return 1 - ss_res/ss_tot if ss_tot > 1e-10 else 0

NORMAL_CONCENTRATIONS = {"water": 0.55, "protein": 0.15, "lipid": 0.12, "glucose": 0.005}
TEST_CONCENTRATIONS = [
    {"water": 0.50, "protein": 0.18, "lipid": 0.10, "glucose": 0.004},
    {"water": 0.60, "protein": 0.12, "lipid": 0.14, "glucose": 0.006},
    {"water": 0.53, "protein": 0.16, "lipid": 0.11, "glucose": 0.005},
]

print("=== СпектрАгро-2: Расчёт NIR-спектроскопии ===")
print()
print("--- Оптическая система ---")
print(f"Диапазон: {WAVELENGTHS_NM[0]}-{WAVELENGTHS_NM[-1]} нм")
print(f"Точек спектра: {N_POINTS}")
print(f"Разрешение: {SPECTRAL_RESOLUTION_NM} нм")
print(f"SNR: {SNR_NIR_DB} дБ ({SNR_NIR_LINEAR:.0f}:1)")
print(f"Длина оптического пути: {SAMPLE_PATH_LENGTH_CM} см")
print()
print("--- Эталонный спектр (нормальные концентрации) ---")
ref_spectrum = compute_spectrum(NORMAL_CONCENTRATIONS)
ref_max = max(ref_spectrum)
ref_min = min(ref_spectrum)
print(f"Макс. пропускание: {ref_max:.4f}")
print(f"Мин. пропускание: {ref_min:.4f}")
print(f"Динамический диапазон: {ref_max/ref_min:.1f}×")
print()
print("--- Калибровка (МНК) ---")
ref_snv = snv_transform(ref_spectrum)
for i, test in enumerate(TEST_CONCENTRATIONS):
    test_spectrum = compute_spectrum(test)
    test_snv = snv_transform(test_spectrum)
    scale = mnk_calibrate(test_snv, ref_snv)
    r2 = sum(a*b for a,b in zip(test_snv, ref_snv))**2 / (sum(a*a for a in test_snv) * sum(b*b for b in ref_snv))
    print(f"  Образец {i+1}: R²={r2:.6f}, scale={scale:.4f}")
print()
print("--- Точность (расчётная оценка проекта) ---")
for analyte, params in MOLAR_ABSORPTIVITY.items():
    snr_at_peak = SNR_NIR_LINEAR * params["epsilon"] * 0.15 * SAMPLE_PATH_LENGTH_CM
    precision = 1.0 / snr_at_peak if snr_at_peak > 0 else 999
    print(f"  {analyte}: ε={params['epsilon']:.2f}, SNR@peak={snr_at_peak:.1f}, точность={precision*100:.2f}%")
print()
print("--- Параметры прибора ---")
MASS_G = 500
BATTERY_H = 24
MEAS_TIME_S = 15
COST_RUB = 250000
MARKET = 50000
print(f"Масса: {MASS_G} г, автономность: {BATTERY_H} ч")
print(f"Время измерения: {MEAS_TIME_S} сек")
print(f"Стоимость: {COST_RUB/1e3:.0f} тыс. ₽")
print(f"Рынок: {MARKET} × {COST_RUB/1e3:.0f} тыс. = {MARKET*COST_RUB/1e9:.1f} млрд ₽")