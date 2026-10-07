import math
import random

SEED_TYPES = {
    "wheat": {"density": 780, "diameter_mm": 3.5, "target_lha": 250, "price_rub_ton": 25000},
    "barley": {"density": 650, "diameter_mm": 3.0, "target_lha": 200, "price_rub_ton": 22000},
    "corn": {"density": 720, "diameter_mm": 8.0, "target_lha": 15, "price_rub_ton": 18000},
    "sunflower": {"density": 400, "diameter_mm": 7.0, "target_lha": 5, "price_rub_ton": 30000},
}

def flow_sensor_accuracy(laser_hz=1000, pixel_size_um=50, seed_d_mm=3.5):
    pixels_per_seed = seed_d_mm * 1000 / pixel_size_um
    min_detectable = pixel_size_um / 1000.0
    accuracy_pct = min_detectable / seed_d_mm * 100
    return accuracy_pct

def uniformity_cv(counts):
    n = len(counts)
    if n == 0:
        return 100.0
    mean = sum(counts) / n
    if mean == 0:
        return 100.0
    variance = sum((x - mean) ** 2 for x in counts) / n
    cv = math.sqrt(variance) / mean * 100
    return cv

def simulate_sowing(seed_type, speed_kmh, pressure_mbar, rows=6, duration_s=60):
    params = SEED_TYPES[seed_type]
    v_ms = speed_kmh / 3.6
    row_spacing_m = 0.125
    seeds_per_m2_ideal = params["target_lha"] / (math.pi * (params["diameter_mm"] / 2000) ** 2 * params["density"]) * 10
    noise_factor = 0.05 + 0.02 * (speed_kmh / 8.0)
    counts = []
    for t in range(int(duration_s)):
        for r in range(rows):
            ideal = seeds_per_m2_ideal * v_ms * row_spacing_m
            actual = ideal * (1.0 + random.gauss(0, noise_factor))
            counts.append(max(0, int(actual)))
    cv = uniformity_cv(counts)
    return cv, counts

def auto_correct(cv, current_pressure, target_cv=5.0):
    if cv > target_cv * 1.5:
        return current_pressure * 0.9
    elif cv > target_cv:
        return current_pressure * 0.95
    elif cv < target_cv * 0.5:
        return current_pressure * 1.05
    return current_pressure

accuracy = flow_sensor_accuracy()
print(f"sensor_accuracy={accuracy:.2f}%")

for seed in SEED_TYPES:
    cv_raw, _ = simulate_sowing(seed, 8.0, 200)
    print(f"{seed}: CV_raw={cv_raw:.1f}%")

economy_ha = 200
seed_price = 25000
seed_rate_tha = 0.25
overlap_pct_old = 15.0
overlap_pct_new = 5.0
seed_saving_t = economy_ha * seed_rate_tha * (overlap_pct_old - overlap_pct_new) / 100
seed_saving_rub = seed_saving_t * seed_price
module_cost = 50000
payback_ha = module_cost / (seed_saving_rub / economy_ha)

print(f"seed_saving={seed_saving_t:.1f}t/season = {seed_saving_rub:.0f}rub/season")
print(f"module_cost={module_cost}rub  payback={payback_ha:.0f}ha")