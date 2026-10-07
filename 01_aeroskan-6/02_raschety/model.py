import math

rho_water = 1000.0
Cd = 0.6
d_nozzle = 0.002
A_nozzle = math.pi * (d_nozzle / 2) ** 2
v_wind = 3.0
h_boom = 1.5
d_drop = 200e-6
LAI = 3.5
v_tractor = 8.0 / 3.6
P_pump = 3.0 * 1e5
n_nozzles = 6
k_drift = 0.005
n_exp = 1.2
m_exp = 0.3
p_exp = 0.5

Q_ideal = Cd * A_nozzle * math.sqrt(2 * P_pump / rho_water) * 1000
Q_total = Q_ideal * n_nozzles
LAI_factor = 1.0 - 0.15 * (LAI - 2.0) / 3.0
LAI_factor = max(0.5, min(1.0, LAI_factor))
Q_corrected = Q_total * LAI_factor

drift_pct = k_drift * (v_wind ** n_exp) * ((d_drop * 1e6) ** m_exp) * (h_boom ** p_exp) * 100
drift_pct = min(drift_pct, 40.0)

area_ha = 50.0
sprayings = 6
volume_base = 300.0
total_base = area_ha * sprayings * volume_base
drift_liters = total_base * drift_pct / 100

saving_pct = 25.0
saving_liters = total_base * saving_pct / 100
price_per_liter = 500.0
saving_rub = saving_liters * price_per_liter
module_cost = 80000.0
payback_sprayings = module_cost / (saving_rub / sprayings)

print(f"d_nozzle={d_nozzle*1000:.1f}mm  A_nozzle={A_nozzle*1e6:.3f}mm2")
print(f"Q_ideal_per_nozzle={Q_ideal*1000:.2f} l/s  Q_total={Q_total*1000:.2f} l/s")
print(f"LAI={LAI}  LAI_factor={LAI_factor:.3f}")
print(f"Q_corrected={Q_corrected*1000:.2f} l/s")
print(f"v_wind={v_wind}m/s  h_boom={h_boom}m  d_drop={d_drop*1e6:.0f}um")
print(f"drift_pct={drift_pct:.1f}%")
print(f"total_base={total_base:.0f} l/season")
print(f"drift_liters={drift_liters:.0f} l/season")
print(f"saving={saving_pct}% = {saving_liters:.0f} l/season = {saving_rub:.0f} rub/season")
print(f"module_cost={module_cost:.0f} rub")
print(f"payback={payback_sprayings:.1f} sprayings")