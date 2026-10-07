#!/usr/bin/env python3
"""
ЦехГид-5: Модель SLAM-навигации + энергопотребления робота.
Расчётная оценка проекта.
"""
import numpy as np, csv, os, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DIR = os.path.dirname(os.path.abspath(__file__))

# ── Параметры робота ──
m = 12.0           # кг (шасси + электроника + батарея)
v_max = 0.3        # м/с (ограничение для снижения стресса птицы)
ceh_L = 100        # м
ceh_W = 18         # м
step = 2.0         # м (сетка обхода)

# ── Энергопотребление ──
P_rpi = 3.5        # Вт (Raspberry Pi 4B)
P_lidar = 2.5      # Вт (RPLIDAR A3)
P_sensors = 0.3    # Вт (SHT45+SGP41+SCD41+TSL2591+IMU)
P_lora = 0.1       # Вт (SX1276, среднее)
P_motors = 8.0     # Вт (2 мотора JGB37-520 при v=0.3 м/с)
P_total = P_rpi + P_lidar + P_sensors + P_lora + P_motors
print(f"Общее потребление: {P_total:.1f} Вт")

# ── Аккумулятор ──
V_batt = 12.0      # В
C_batt = 6.0       # А·ч (LiFePO₄)
E_batt = V_batt * C_batt * 3600  # Дж
t_batt = E_batt / (P_total * 3600 / V_batt)  # часы
print(f"Ёмкость батареи: {C_batt} А·ч = {E_batt/3600:.1f} Вт·ч")
print(f"Время автономной работы: {t_batt:.1f} ч")

# ── Маршрут обхода ──
n_rows = int(ceh_W / step)
n_cols = int(ceh_L / step)
n_points = n_rows * n_cols
print(f"Точек измерения: {n_points} ({n_rows} × {n_cols})")

# Зигзагообразный маршрут
path_length = 0
prev_x, prev_y = 0, 0
route = [(0, 0)]
for row in range(n_rows):
    y = row * step + step / 2
    cols_range = range(n_cols) if row % 2 == 0 else range(n_cols - 1, -1, -1)
    for col in cols_range:
        x = col * step + step / 2
        d = np.sqrt((x - prev_x)**2 + (y - prev_y)**2)
        path_length += d
        prev_x, prev_y = x, y
        route.append((x, y))

t_route = path_length / v_max / 60  # мин
print(f"Длина маршрута: {path_length:.0f} м")
print(f"Время обхода: {t_route:.1f} мин")

# ── SLAM точность ──
# RPLIDAR A3: точность угловая ±0.1°, дальность ±30 мм на 16 м
angular_res = 0.1   # градусы
range_res = 0.03    # м
at_16m = 16 * np.tan(np.radians(angular_res))
slam_error = np.sqrt(at_16m**2 + range_res**2)
print(f"SLAM точность (расчётная): ±{slam_error*1000:.0f} мм на 16 м")

# ── Качество SLAM (модель деградации) ──
distances = np.linspace(0.5, 16, 50)
slam_errors = np.sqrt((distances * np.tan(np.radians(angular_res)))**2 + range_res**2)

# ── Энергия по компонентам ──
components = ['Raspberry Pi\n4B', 'RPLIDAR\nA3', 'Сенсоры\n(4 шт.)', 'LoRa\nSX1276', 'Моторы\n(×2)']
powers = [P_rpi, P_lidar, P_sensors, P_lora, P_motors]

# ── Графики ──
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Маршрут
ax = axes[0, 0]
rx = [p[0] for p in route]
ry = [p[1] for p in route]
ax.plot(rx, ry, '#2563EB', lw=0.8, alpha=0.7)
ax.add_patch(plt.Rectangle((0, 0), ceh_L, ceh_W, fill=False, edgecolor='#333', lw=2))
ax.set_xlabel('Длина (м)'); ax.set_ylabel('Ширина (м)')
ax.set_title(f'Маршрут обхода: {n_points} точек, {path_length:.0f} м')
ax.set_aspect('equal'); ax.grid(True, alpha=0.3)

# 2. SLAM ошибка
ax = axes[0, 1]
ax.plot(distances, slam_errors * 1000, '#EF4444', lw=2)
ax.set_xlabel('Дальность до объекта (м)'); ax.set_ylabel('Ошибка позиционирования (мм)')
ax.set_title('SLAM точность (RPLIDAR A3)')
ax.grid(True, alpha=0.3)

# 3. Энергопотребление
ax = axes[1, 0]
colors = ['#2563EB', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6']
bars = ax.bar(components, powers, color=colors, alpha=0.8)
ax.set_ylabel('Потребление (Вт)'); ax.set_title(f'Энергобаланс: итого {P_total:.1f} Вт')
ax.grid(True, alpha=0.3, axis='y')

# 4. Время работы vs ёмкость
ax = axes[1, 1]
capacities = np.linspace(1, 20, 50)
times = capacities * V_batt / P_total
ax.plot(capacities, times, '#10B981', lw=2)
ax.axvline(C_batt, color='#EF4444', ls='--', label=f'LiFePO₄ {C_batt} А·ч = {t_batt:.1f} ч')
ax.axhline(t_route/60, color='#2563EB', ls=':', label=f'Время обхода: {t_route:.1f} мин')
ax.set_xlabel('Ёмкость батареи (А·ч)'); ax.set_ylabel('Время работы (ч)')
ax.set_title('Время автономной работы')
ax.legend(); ax.grid(True, alpha=0.3)

plt.suptitle('ЦехГид-5: модель SLAM-навигации и энергопотребления', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(DIR, '..', '03_grafika', 'T5_model_cehgid.png'), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print(f"✓ График: T5_model_cehgid.png")

# ── CSV ──
with open(os.path.join(DIR, 'T5_slam_model.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Параметр', 'Значение', 'Единица'])
    w.writerows([
        ['Масса робота', m, 'кг'],
        ['Макс. скорость', v_max, 'м/с'],
        ['Размер цеха', f'{ceh_L}×{ceh_W}', 'м'],
        ['Шаг сетки', step, 'м'],
        ['Точек измерения', n_points, 'шт.'],
        ['Длина маршрута', round(path_length, 0), 'м'],
        ['Время обхода', round(t_route, 1), 'мин'],
        ['Общее потребление', P_total, 'Вт'],
        ['Ёмкость батареи', C_batt, 'А·ч'],
        ['Время работы', round(t_batt, 1), 'ч'],
        ['SLAM точность (16 м)', round(slam_error * 1000, 0), 'мм'],
    ])
print(f"✓ CSV: T5_slam_model.csv")

# ── XLSX (создаётся через openpyxl) ──
try:
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = 'SLAM+Энергия'
    ws.append(['Параметр', 'Значение', 'Единица'])
    ws.append(['Масса робота', m, 'кг'])
    ws.append(['Макс. скорость', v_max, 'м/с'])
    ws.append(['Размер цеха', f'{ceh_L}×{ceh_W}', 'м'])
    ws.append(['Шаг сетки', step, 'м'])
    ws.append(['Точек измерения', n_points, 'шт.'])
    ws.append(['Длина маршрута', round(path_length, 0), 'м'])
    ws.append(['Время обхода', round(t_route, 1), 'мин'])
    ws.append(['Общее потребление', P_total, 'Вт'])
    ws.append(['Ёмкость батареи', C_batt, 'А·ч'])
    ws.append(['Время работы', round(t_batt, 1), 'ч'])
    ws.append(['SLAM точность (16 м)', round(slam_error * 1000, 0), 'мм'])
    wb.save(os.path.join(DIR, 'T5_slam_model.xlsx'))
    print(f"✓ XLSX: T5_slam_model.xlsx")
except Exception as e:
    print(f"XLSX skip: {e}")

print("\n✓ ЦехГид-5: модель завершена.")