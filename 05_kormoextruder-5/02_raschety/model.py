import math

SOY = {"protein_pct": 38.0, "fat_pct": 18.0, "moisture_pct": 12.0, "density": 750}

def extruder_throughput(d_mm, rpm, fill=0.45, rho=600):
    d_m = d_mm / 1000.0
    area = math.pi * (d_m / 2) ** 2
    pitch = d_m
    v = pitch * rpm / 60.0
    return area * v * fill * rho * 3600

def die_pressure(die_d_mm, die_count, throughput_kg_h, temp_c):
    viscosity = 500 * math.exp(-0.015 * (temp_c - 20))
    d_m = die_d_mm / 1000.0
    L = 0.02
    Q = throughput_kg_h / 3600.0 / 900.0
    A = math.pi * (d_m / 2) ** 2 * die_count
    v = Q / A if A > 0 else 0
    return 8 * viscosity * L * v / ((d_m / 2) ** 2) / 1e6

def protein_extraction(soak_h, grind_um):
    base = SOY["protein_pct"]
    return base * min(1.0, 0.3 + 0.7 * soak_h / 12.0) * min(1.0, 200.0 / grind_um)

throughput = extruder_throughput(100, 300)
pressure = die_pressure(8, 6, throughput, 130)
protein = protein_extraction(8, 150)
energy = 2.2 / throughput if throughput > 0 else 0

farm = 200
feed_kg = 8
days = 365
total_t = farm * feed_kg * days / 1000
buy_price = 25000
make_price = 12000
saving = total_t * (buy_price - make_price)
cost = 400000
payback = cost / (saving / 12)

print(f"throughput={throughput:.0f} kg/h")
print(f"die_pressure={pressure:.1f} MPa")
print(f"protein_extracted={protein:.1f}%")
print(f"energy={energy:.3f} kWh/kg")
print(f"total_feed={total_t:.0f} t/year")
print(f"saving={saving:.0f} rub/year")
print(f"cost={cost} rub  payback={payback:.1f} months")