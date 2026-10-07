import math

FREQ = 50
AMP = 1.5
SLOPE = 5.0

FRACTIONS = {
    "large":  {"d": (4.0, 6.0), "hole": 5.0, "pct": 30},
    "medium": {"d": (2.5, 4.0), "hole": 3.5, "pct": 50},
    "small":  {"d": (1.0, 2.5), "hole": 2.0, "pct": 15},
    "reject": {"d": (0.0, 1.0), "hole": 0,   "pct": 5},
}

def vib_velocity(freq, amp_mm):
    return 2 * math.pi * freq * amp_mm / 1000

def sieving_prob(d_seed, d_hole, v):
    if d_seed >= d_hole:
        return 0.05
    ratio = d_seed / d_hole
    return max(0.0, min(1.0, (1.0 - ratio) * min(1.0, v / 0.2)))

def separation_eff(fractions, hole_mm, v):
    recovered = 0
    total = 0
    for f in fractions.values():
        if f["hole"] > 0 and f["d"][1] <= hole_mm:
            d_avg = (f["d"][0] + f["d"][1]) / 2
            p = sieving_prob(d_avg, f["hole"], v)
            recovered += f["pct"] * p
            total += f["pct"]
    return recovered / total * 100 if total > 0 else 0

def throughput(w_mm, l_mm, rho, v, depth_mm):
    return (w_mm/1000) * (l_mm/1000) * (depth_mm/1000) * rho * v * 3600 / (l_mm/1000/v if v > 0 else 1)

v = vib_velocity(FREQ, AMP)
print(f"vib_velocity={v:.3f} m/s")

for name, f in FRACTIONS.items():
    if f["hole"] > 0:
        d_avg = (f["d"][0] + f["d"][1]) / 2
        p = sieving_prob(d_avg, f["hole"], v)
        print(f"  {name}: d={f['d'][0]}-{f['d'][1]}mm hole={f['hole']}mm P={p:.2f}")

eff = separation_eff(FRACTIONS, 5.0, v)
print(f"separation_eff={eff:.1f}%")

tp = throughput(120, 200, 750, v, 5)
print(f"throughput={tp:.0f} kg/h")

farm = 500
rate = 250
cost_kg = 100
bad = 10.0
loss = farm * rate * bad / 100 * cost_kg
module = 80000
payback = module / loss * farm

print(f"farm={farm}ha  loss={loss:.0f} rub/year")
print(f"module={module} rub  payback={payback:.0f} ha")