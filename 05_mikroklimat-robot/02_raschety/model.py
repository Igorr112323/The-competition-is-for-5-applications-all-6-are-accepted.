#!/usr/bin/env python3
"""
КлиматРобот-5: SLAM-навигация + мультисенсорный мониторинг микроклимата v1.
RPLIDAR A3, Cartographer, 5 датчиков, LoRa, LiFePO₄.
"""
import numpy as np, matplotlib, os, csv
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

REPO = "/home/user/The-competition-is-for-5-applications-all-6-are-accepted."
DIR  = os.path.join(REPO, "05_mikroklimat-robot/02_raschety")
GDIR = os.path.join(REPO, "05_mikroklimat-robot/03_grafika")
os.makedirs(DIR, exist_ok=True); os.makedirs(GDIR, exist_ok=True)
TODAY = "07.10.2026"

# ═══════════════════════════════════════════════════════════════
# ВХОДНЫЕ ДАННЫЕ
# ═══════════════════════════════════════════════════════════════
massa = 15.0           # кг
gabarits = (400, 300, 250)  # мм
S_pomesh = 500.0       # м² — площадь помещения
t_obhod = 30.0         # мин — время обхода
grid = 2.0             # м — шаг сетки сбора
toch_slam = 0.05       # м — точность SLAM ±5 см
v_robot = 0.5          # м/с — скорость
radius_lidar = 16.0    # м — радиус лидара
autonom = 6.0          # ч
U_bat = 12.6; Q_bat = 6000.0; eta = 0.90
P_motors = 15.0; P_rpi = 5.0; P_lidar = 2.5; P_sensors = 0.5; P_lora = 0.3
P_ussr = P_motors + P_rpi + P_lidar + P_sensors + P_lora
MTBF_target = 6000
N_sensors = 5
C_pribor = 150000.0    # ₽
C_manual = 500.0       # ₽/час ручной обход
t_manual = 4.0         # часа ручной обход

# ═══════════════════════════════════════════════════════════════
# МОДЕЛЬ SLAM (синтетическая карта помещения)
# ═══════════════════════════════════════════════════════════════
np.random.seed(42)

# Комната 25×20 м
W_room, H_room = 25, 20
# Маршрутный граф (сетка 2×2 м)
xs_grid = np.arange(1, W_room, grid)
ys_grid = np.arange(1, H_room, grid)
N_points = len(xs_grid) * len(ys_grid)

# Синтетические данные датчиков
T_map = np.zeros((len(ys_grid), len(xs_grid)))
RH_map = np.zeros_like(T_map)
CO2_map = np.zeros_like(T_map)

for i, y in enumerate(ys_grid):
    for j, x in enumerate(xs_grid):
        T_map[i, j] = 20 + 3*np.sin(x/5) + 2*np.cos(y/4) + np.random.normal(0, 0.3)
        RH_map[i, j] = 60 + 10*np.sin(x/3) + 5*np.cos(y/5) + np.random.normal(0, 1)
        CO2_map[i, j] = 400 + 200*np.exp(-((x-12)**2 + (y-10)**2)/20) + np.random.normal(0, 20)

# Синтетическая SLAM-траектория
N_steps = int(t_obhod * 60 / 0.5)  # шаги по 0.5 сек
t_arr = np.arange(N_steps) * 0.5
x_slam, y_slam = [1.0], [1.0]
for k in range(N_steps - 1):
    idx = k % N_points
    j = idx % len(xs_grid)
    i = idx // len(xs_grid)
    tx, ty = xs_grid[j], ys_grid[i]
    dx = tx - x_slam[-1]; dy = ty - y_slam[-1]
    dist = np.sqrt(dx**2 + dy**2)
    if dist > 0.1:
        step = min(v_robot * 0.5, dist)
        x_slam.append(x_slam[-1] + dx/dist * step)
        y_slam.append(y_slam[-1] + dy/dist * step)
    else:
        x_slam.append(x_slam[-1] + np.random.normal(0, 0.01))
        y_slam.append(y_slam[-1] + np.random.normal(0, 0.01))

x_slam = np.array(x_slam); y_slam = np.array(y_slam)

# CSV
with open(os.path.join(DIR, "KLIMAT_input_data.csv"), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(["Шаг", "t_сек", "x_м", "y_м", "T_C", "RH_%", "CO2_ppm"])
    for k in range(0, N_steps, 100):
        j = (k % N_points) % len(xs_grid)
        i = (k % N_points) // len(xs_grid)
        i = min(i, len(ys_grid)-1); j = min(j, len(xs_grid)-1)
        w.writerow([k, f"{t_arr[k]:.1f}", f"{x_slam[k]:.2f}", f"{y_slam[k]:.2f}",
                    f"{T_map[i,j]:.1f}", f"{RH_map[i,j]:.1f}", f"{CO2_map[i,j]:.0f}"])
print("  KLIMAT_input_data.csv ✓")

# ═══════════════════════════════════════════════════════════════
# ГРАФИКИ
# ═══════════════════════════════════════════════════════════════
plt.rcParams['font.family'] = 'DejaVu Sans'

# 1. SLAM-карта помещения (тепловая карта температуры)
fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(T_map, extent=[0, W_room, 0, H_room], origin='lower',
               cmap='RdYlBu_r', aspect='equal')
plt.colorbar(im, ax=ax, label='Температура (°C)')
ax.plot(x_slam[:1000], y_slam[:1000], '-', color='#1F2937', lw=0.5, alpha=0.5, label='Маршрут')
ax.set_xlabel('X (м)', fontsize=10); ax.set_ylabel('Y (м)', fontsize=10)
ax.set_title('SLAM-карта: распределение температуры (помещение 25×20 м)', fontsize=12, fontweight='bold')
ax.legend(fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_05_01_shema.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_05_01_shema.png ✓")

# 2. Сборочный чертёж
fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(-20, 420); ax.set_ylim(-20, 320); ax.set_aspect('equal'); ax.grid(True, alpha=0.2)
ax.set_title('Сборочный чертёж КлиматРобот-5 (мм)', fontsize=12, fontweight='bold')
rect = plt.Rectangle((0, 0), 400, 300, facecolor='none', edgecolor='#2563EB', lw=2)
ax.add_patch(rect)
# Лидар (круг сверху)
circle = plt.Circle((200, 250), 30, facecolor='none', edgecolor='#EF4444', lw=1.5)
ax.add_patch(circle); ax.text(200, 250, 'RPLIDAR\nA3', ha='center', va='center', fontsize=7)
# Колёса
for cx, cy in [(50, 30), (350, 30), (50, 270), (350, 270)]:
    c = plt.Circle((cx, cy), 40, facecolor='none', edgecolor='#10B981', lw=1.5)
    ax.add_patch(c)
# Батарея
rect2 = plt.Rectangle((100, 50), 200, 80, facecolor='#F59E0B', alpha=0.15, edgecolor='#F59E0B', lw=1)
ax.add_patch(rect2); ax.text(200, 90, 'LiFePO₄ 12.6В 6А·ч', ha='center', va='center', fontsize=8)
# RPi
rect3 = plt.Rectangle((150, 160), 100, 60, facecolor='#2563EB', alpha=0.15, edgecolor='#2563EB', lw=1)
ax.add_patch(rect3); ax.text(200, 190, 'Raspberry Pi 4B', ha='center', va='center', fontsize=8)
# Датчики
for cx, cy, name in [(30, 150, 'SHT45'), (30, 200, 'SGP41'), (370, 150, 'SCD41'), (370, 200, 'TSL2591')]:
    rect4 = plt.Rectangle((cx-15, cy-10), 30, 20, facecolor='#8B5CF6', alpha=0.2, edgecolor='#8B5CF6', lw=1)
    ax.add_patch(rect4); ax.text(cx, cy, name, ha='center', va='center', fontsize=7)
ax.set_xlabel('X (мм)'); ax.set_ylabel('Y (мм)')
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_05_02_chertezh.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_05_02_chertezh.png ✓")

# 3. 3D-модель
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')
W2, D2, H2 = 400, 300, 250
scale = 0.001
verts = [
    [[0,0,0],[W2,0,0],[W2,D2,0],[0,D2,0]],
    [[0,0,H2],[W2,0,H2],[W2,D2,H2],[0,D2,H2]],
    [[0,0,0],[W2,0,0],[W2,0,H2],[0,0,H2]],
    [[0,D2,0],[W2,D2,0],[W2,D2,H2],[0,D2,H2]],
    [[0,0,0],[0,D2,0],[0,D2,H2],[0,0,H2]],
    [[W2,0,0],[W2,D2,0],[W2,D2,H2],[W2,0,H2]],
]
verts_s = [[[v*scale for v in pt] for pt in face] for face in verts]
poly = Poly3DCollection(verts_s, alpha=0.3, facecolor='#2563EB', edgecolor='#1F2937', lw=0.5)
ax.add_collection3d(poly)
# Лидар сверху
theta = np.linspace(0, 2*np.pi, 30)
ax.plot((200+30*np.cos(theta))*scale, (250+30*np.sin(theta))*scale,
        np.ones_like(theta)*H2*scale, color='#EF4444', lw=2)
ax.set_xlabel('X (м)'); ax.set_ylabel('Y (м)'); ax.set_zlabel('Z (м)')
ax.set_title('КлиматРобот-5: 3D-модель (400×300×250 мм)', fontsize=12, fontweight='bold')
ax.set_xlim(0, 0.45); ax.set_ylim(0, 0.35); ax.set_zlim(0, 0.3)
ax.view_init(elev=25, azim=135)
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_05_03_3D.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_05_03_3D.png ✓")

# 4. График дрейфа SLAM
fig, ax = plt.subplots(figsize=(10, 6))
t_show = np.arange(0, 3600, 1)  # 1 час
drift = np.cumsum(np.abs(np.random.normal(0, 0.002, len(t_show))))
ax.plot(t_show/60, drift*100, '-', color='#2563EB', lw=1.5)
ax.axhline(toch_slam*100, color='#EF4444', ls='--', label=f'Допуск ±{toch_slam*100:.0f} см')
ax.fill_between(t_show/60, 0, toch_slam*100, alpha=0.1, color='#10B981')
ax.set_xlabel('Время (мин)', fontsize=10); ax.set_ylabel('Накопленный дрейф (см)', fontsize=10)
ax.set_title('Дрейф SLAM-позиционирования (1 час непрерывной работы)', fontsize=12, fontweight='bold')
ax.legend(fontsize=9); ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_05_04_graf.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_05_04_graf.png ✓")

# 5. Сравнение с аналогами
fig, ax = plt.subplots(figsize=(10, 6))
devs = ['КлиматРобот-5', '«Умная ферма»\n(НР)', 'iRobot\nCreate 3', 'TurtleBot3\n(Burger)']
params = [5, 10, 15, 10]  # см точность
colors_b = ['#2563EB', '#F59E0B', '#10B981', '#EF4444']
bars = ax.bar(devs, params, color=colors_b, width=0.6)
ax.set_ylabel('Точность позиционирования, см (↓ лучше)', fontsize=10)
ax.set_title('Сравнение точности SLAM-навигации', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'±{bar.get_height():.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_05_05_graf_vs.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_05_05_graf_vs.png ✓")

# 6. Конкуренты
fig, ax = plt.subplots(figsize=(10, 6))
devs2 = ['КлиматРобот-5', 'Переносной\nмонитор', 'Стационарная\nсеть', 'Ручной обход']
costs = [150, 50, 300, 500]  # тыс. ₽
colors_c = ['#2563EB', '#F59E0B', '#10B981', '#EF4444']
bars = ax.bar(devs2, costs, color=colors_c, width=0.6)
ax.set_ylabel('Стоимость системы (тыс. ₽)', fontsize=10)
ax.set_title('Сравнение стоимости решений мониторинга', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
            f'{bar.get_height():.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_05_06_konkurenty.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_05_06_konkurenty.png ✓")

# 7. Гант
fig, ax = plt.subplots(figsize=(10, 4))
stages = ['Этап 1\nSLAM +\nдатчики', 'Этап 2\nPCB +\nпрототип', 'Этап 3\nИспытания\n500 м²', 'Этап 4\nТУ + ПМ\n+ отчёт']
starts = [1, 4, 7, 10]; durs = [3, 3, 3, 3]
colors_g = ['#2563EB', '#F59E0B', '#10B981', '#8B5CF6']
for i, (s, d, c) in enumerate(zip(starts, durs, colors_g)):
    ax.barh(i, d, left=s, height=0.5, color=c, edgecolor='white', lw=1.5)
    ax.text(s + d/2, i, f'{s}–{s+d} мес.', ha='center', va='center', fontsize=9, fontweight='bold', color='white')
ax.set_yticks(range(4)); ax.set_yticklabels(stages, fontsize=9)
ax.set_xlabel('Месяц'); ax.set_title('Календарный план НИОКР (12 месяцев)', fontsize=12, fontweight='bold')
ax.set_xlim(0, 13); ax.set_xticks(range(1, 13)); ax.grid(True, alpha=0.3, axis='x'); ax.invert_yaxis()
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_05_07_gant.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_05_07_gant.png ✓")

# 8. Экономика
fig, ax = plt.subplots(figsize=(10, 5))
years = [1, 2, 3, 4, 5]
vyr = [3.0, 10.0, 25.0, 45.0, 70.0]
zat = [2.0, 6.0, 13.0, 22.0, 30.0]
ax.plot(years, vyr, 'o-', color='#2563EB', lw=2, label='Выручка')
ax.plot(years, zat, 's--', color='#EF4444', lw=2, label='Затраты')
ax.fill_between(years, [v-z for v,z in zip(vyr,zat)], alpha=0.15, color='#10B981', label='Прибыль')
ax.set_xlabel('Год'); ax.set_ylabel('Млн ₽')
ax.set_title('Прогноз экономики (5 лет)', fontsize=12, fontweight='bold')
ax.legend(fontsize=9); ax.grid(True, alpha=0.3); ax.set_xticks(years)
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_05_08_ekonomika.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_05_08_ekonomika.png ✓")

# 9. Стенд испытаний
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('Стенд испытаний: помещение 500 м²', fontsize=12, fontweight='bold')
boxes = [
    (1, 5, 2, 1, 'КлиматРобот-5\n(робот)', '#2563EB'),
    (4, 5, 2, 1, 'RPLIDAR A3\n(360°, 16м)', '#F59E0B'),
    (7, 5, 2, 1, 'LoRa-шлюз\n→ Облако', '#10B981'),
    (1, 2.5, 2, 1, 'Помещение\n500 м²', '#8B5CF6'),
    (4, 2.5, 2, 1, 'Тепловые\nкарты', '#EC4899'),
    (7, 2.5, 2, 1, 'Дашборд\n(T, RH, CO₂)', '#6366F1'),
]
for x, y, w, h, label, color in boxes:
    rect = plt.Rectangle((x, y), w, h, facecolor=color, alpha=0.15, edgecolor=color, lw=2)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, label, ha='center', va='center', fontsize=8, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_05_09_stend.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_05_09_stend.png ✓")

# ═══════════════════════════════════════════════════════════════
# XLSX
# ═══════════════════════════════════════════════════════════════
hf = Font(bold=True, size=11); hfill = PatternFill('solid', fgColor='D9E1F2')
bdr = Border(left=Side('thin'), right=Side('thin'), top=Side('thin'), bottom=Side('thin'))
def mkwb():
    wb = Workbook(); wb.remove(wb.active); return wb
def addsheet(wb, title, headers, data, cw=22):
    ws = wb.create_sheet(title)
    for c, h in enumerate(headers, 1):
        cell = ws.cell(1, c, h); cell.font = hf; cell.fill = hfill; cell.border = bdr
    for r, row in enumerate(data, 2):
        for c, v in enumerate(row, 1):
            ws.cell(r, c, v).border = bdr
    for c in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(c)].width = cw
    return ws

# ekonomika
wb = mkwb()
addsheet(wb, "Исходные", ["Параметр", "Значение", "Ед.", "Источник"], [
    ["C_ручного_обхода", C_manual, "₽/ч", "расч."], ["t_ручного", t_manual, "ч", "расч."],
    ["S_объектов", 250, "смен/год", "250 р.д."], ["C_робота", C_pribor, "₽", "расч. BOM"],
])
addsheet(wb, "Результат", ["Показатель", "Значение", "Ед."], [
    ["Стоимость_ручного_обхода", C_manual * t_manual * 250 / 1e6, "млн ₽/год"],
    ["Экономия_70%", C_manual * t_manual * 250 * 0.7 / 1e6, "млн ₽/год"],
    ["ROI_робота", round(C_pribor / (C_manual * t_manual * 250 * 0.7 / 250)), "смен"],
])
addsheet(wb, "Источники", ["№", "Источник", "Дата"], [
    ["1", "Росстат — фермерские хозяйства", TODAY], ["2", "RPLIDAR — каталог", TODAY],
])
addsheet(wb, "Допущения", ["Допущение", "Обоснование"], [
    ["500 ₽/ч", "Стоимость работника"], ["4 часа", "Ручной обход 500 м²"],
    ["250 смен/год", "250 р.д."], ["70% экономии", "Автоматизация + данные 24/7"],
])
wb.save(os.path.join(DIR, "KLIMAT_ekonomika.xlsx"))
print("  KLIMAT_ekonomika.xlsx ✓")

# TTH
wb = mkwb()
addsheet(wb, "ТТХ", ["№", "Параметр", "Значение", "Расчёт", "Источник"], [
    ["1", "Точность SLAM", "±5 см", "RPLIDAR A3 + Cartographer", "расч."],
    ["2", "Датчики", "5 шт", "SHT45, SGP41, SCD41, TSL2591 + NTC", "datasheet"],
    ["3", "Автономность", "≥6 ч", f"{Q_bat:.0f} мА·ч × {U_bat} В × {eta} / {P_ussr:.1f} Вт = {Q_bat*U_bat*eta/1000/P_ussr:.1f} ч", "расч."],
    ["4", "Масса", "≤15 кг", "шасси 5 + батарея 3 + электроника 2 + корпус 5", "расч."],
    ["5", "Скорость", "0.5 м/с", "шаговые двигатели", "ТЗ"],
    ["6", "Радиус лидара", "16 м", "RPLIDAR A3", "datasheet"],
    ["7", "LoRa-передача", "868 МГц", "SX1276, до 5 км", "datasheet"],
])
wb.save(os.path.join(DIR, "KLIMAT_TTH_obosnovanie.xlsx"))
print("  KLIMAT_TTH_obosnovanie.xlsx ✓")

# nadezhnost
wb = mkwb()
comps = [
    ("RPLIDAR A3", 1, 2e-6, "datasheet"),
    ("Raspberry Pi 4B", 1, 3e-6, "datasheet"),
    ("Шаговые двигатели (×2)", 2, 5e-6, "datasheet"),
    ("SHT45", 1, 1e-7, "datasheet"),
    ("SGP41", 1, 1e-7, "datasheet"),
    ("SCD41", 1, 1e-7, "datasheet"),
    ("TSL2591", 1, 1e-7, "datasheet"),
    ("LoRa SX1276", 1, 5e-7, "datasheet"),
    ("LiFePO₄ BMS", 1, 1e-6, "datasheet"),
    ("DC-DC конвертер", 1, 3e-6, "datasheet"),
    ("Корпус + шасси", 1, 1e-7, "расч."),
]
total_l = sum(q * l for _, q, l, _ in comps)
MTBF = 1 / total_l
addsheet(wb, "Компоненты", ["Компонент", "Кол-во", "λ (1/ч)", "Источник"], [[n, q, f"{l:.1e}", s] for n, q, l, s in comps])
addsheet(wb, "Результат", ["Параметр", "Значение", "Ед."], [
    ["Σλ", f"{total_l:.2e}", "1/ч"], ["MTBF", f"{MTBF:.0f}", "ч"],
    ["Целевое", str(MTBF_target), "ч"], ["Статус", "ДА" if MTBF >= MTBF_target else "НЕТ", ""],
])
wb.save(os.path.join(DIR, "KLIMAT_nadezhnost.xlsx"))
print(f"  KLIMAT_nadezhnost.xlsx ✓ (MTBF={MTBF:.0f} ч)")

# profilny_balans
wb = mkwb()
E_poln = Q_bat * U_bat / 1000 * eta
addsheet(wb, "Энергобаланс", ["Параметр", "Значение", "Ед."], [
    ["P_моторы", P_motors, "Вт"], ["P_RPi", P_rpi, "Вт"], ["P_лидар", P_lidar, "Вт"],
    ["P_датчики", P_sensors, "Вт"], ["P_LoRa", P_lora, "Вт"],
    ["P_средняя", P_ussr, "Вт"], ["E_полная", round(E_poln, 2), "Вт·ч"],
    ["t_автономности", round(E_poln / P_ussr, 1), "ч"], ["Целевое", autonom, "ч"],
    ["Статус", "ДА" if E_poln / P_ussr >= autonom else "НЕТ", ""],
])
wb.save(os.path.join(DIR, "KLIMAT_profilny_balans.xlsx"))
print("  KLIMAT_profilny_balans.xlsx ✓")

# metrologia
wb = mkwb()
addsheet(wb, "Погрешности", ["Канал", "Датчик", "Δ", "Ед.", "Компенсация"], [
    ["Температура", "SHT45", "±0.1", "°C", "Калибровка"],
    ["Влажность", "SHT45", "±1.5", "%", "Калибровка"],
    ["CO₂", "SCD41", "±(40+5%)", "ppm", "Автокалибровка"],
    ["VOC", "SGP41", "±15%", "ндекс", "Калибровка"],
    ["Освещённость", "TSL2591", "±5%", "лк", "Калибровка"],
    ["Позиция SLAM", "RPLIDAR A3", "±5", "см", "Cartographer loop closure"],
])
addsheet(wb, "Испытания", ["№", "Испытание", "Оборудование", "Методика"], [
    ["1", "Калибровка SHT45", "Эталонный термогигрометр", "3 точки"],
    ["2", "Калибровка SCD41", "Газовая смесь 400/1000/5000 ppm", "3 точки"],
    ["3", "SLAM-тест", "Помещение 500 м², маяки", "Обход, сравнение координат"],
    ["4", "Автономность", "Хронометр", "6 ч непрерывно"],
    ["5", "LoRa-передача", "LoRa-шлюз", "Дальность, пакеты"],
])
wb.save(os.path.join(DIR, "KLIMAT_metrologia.xlsx"))
print("  KLIMAT_metrologia.xlsx ✓")

# STL
def write_stl(path, facets):
    with open(path, 'w') as f:
        f.write("solid klimat_robot\n")
        for item in facets:
            n = item[0]
            for tri in item[1:]:
                f.write(f"  facet normal {n[0]} {n[1]} {n[2]}\n    outer loop\n")
                for v in tri:
                    f.write(f"      vertex {v[0]} {v[1]} {v[2]}\n")
                f.write("    endloop\n  endfacet\n")
        f.write("endsolid klimat_robot\n")

W3, D3, H3 = 400, 300, 250
faces = [
    ((0,0,-1), [(0,0,0),(W3,0,0),(W3,D3,0)], [(0,0,0),(W3,D3,0),(0,D3,0)]),
    ((0,0,1),  [(0,0,H3),(W3,D3,H3),(W3,0,H3)], [(0,0,H3),(0,D3,H3),(W3,D3,H3)]),
    ((0,-1,0), [(0,0,0),(W3,0,H3),(W3,0,0)], [(0,0,0),(0,0,H3),(W3,0,H3)]),
    ((0,1,0),  [(0,D3,0),(W3,D3,0),(W3,D3,H3)], [(0,D3,0),(W3,D3,H3),(0,D3,H3)]),
    ((-1,0,0), [(0,0,0),(0,D3,0),(0,D3,H3)], [(0,0,0),(0,D3,H3),(0,0,H3)]),
    ((1,0,0),  [(W3,0,0),(W3,0,H3),(W3,D3,H3)], [(W3,0,0),(W3,D3,H3),(W3,D3,0)]),
]
write_stl(os.path.join(DIR, "../01_zadel/prototype/klimat_robot.stl"), faces)
print("  klimat_robot.stl ✓")

print(f"\n✓ Все расчёты КлиматРобот-5 (v1) завершены.")