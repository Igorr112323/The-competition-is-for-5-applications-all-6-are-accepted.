import math
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
