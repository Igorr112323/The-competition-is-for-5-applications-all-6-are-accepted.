#!/usr/bin/env python3
"""
Синтетическая кривая амплификации ПЦР.
Модель: F(n) = F_max / (1 + exp(-k*(n - Ct)))
"""
import numpy as np, os, csv, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

REPO = "/home/user/The-competition-is-for-5-applications-all-6-are-accepted."
DIR = os.path.join(REPO, "02_vetpcr-chemodan/02_raschety")

# Параметры кривых для 4 каналов
channels = {
    'FAM': {'Ct': 22, 'Fmax': 15000, 'k': 0.8, 'noise': 200},
    'HEX': {'Ct': 25, 'Fmax': 12000, 'k': 0.7, 'noise': 180},
    'ROX': {'Ct': 28, 'Fmax': 10000, 'k': 0.6, 'noise': 150},
    'Cy5': {'Ct': 31, 'Fmax': 8000, 'k': 0.5, 'noise': 120},
}

n_cycles = np.arange(1, 41)
np.random.seed(42)

rows = []
for ch, p in channels.items():
    baseline = 500 + np.random.normal(0, p['noise']*0.1, len(n_cycles))
    signal = p['Fmax'] / (1 + np.exp(-p['k'] * (n_cycles - p['Ct'])))
    fluo = baseline + signal + np.random.normal(0, p['noise'], len(n_cycles))
    fluo = np.maximum(fluo, 0)
    for i, (n, f) in enumerate(zip(n_cycles, fluo)):
        rows.append([ch, int(n), round(f, 1)])

with open(os.path.join(DIR, "synth_amplification.csv"), 'w', newline='', encoding='utf-8') as fout:
    w = csv.writer(fout)
    w.writerow(["Канал", "Цикл", "Флуоресценция (отн. ед.)"])
    for r in rows: w.writerow(r)

# График
plt.rcParams['font.family'] = 'DejaVu Sans'
fig, ax = plt.subplots(figsize=(10, 6))
colors = {'FAM': '#2563EB', 'HEX': '#10B981', 'ROX': '#F59E0B', 'Cy5': '#EF4444'}
for ch, p in channels.items():
    baseline = 500
    signal = p['Fmax'] / (1 + np.exp(-p['k'] * (n_cycles - p['Ct'])))
    fluo = baseline + signal
    ax.plot(n_cycles, fluo, color=colors[ch], lw=2, label=f"{ch} (Ct={p['Ct']})")
    ax.axvline(p['Ct'], color=colors[ch], ls=':', alpha=0.4)
ax.set_xlabel('Номер цикла'); ax.set_ylabel('Флуоресценция (отн. ед.)')
ax.set_title('ВетПЦР: синтетические кривые амплификации (4 канала)')
ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(REPO, "02_vetpcr-chemodan/03_grafika/T2_synth_amplification.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("✓ synth_amplification.csv + график")