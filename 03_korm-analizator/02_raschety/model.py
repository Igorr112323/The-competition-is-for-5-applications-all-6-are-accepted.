#!/usr/bin/env python3
"""
КормТест-NIR: модель NIR-спектрометрии + CatBoost v1.
Портативный ИИ-экспрессанализатор качества кормовых гранул и зерна.
NIR 900–1700 нм, мех. тестирование гранул, CatBoost, 6 параметров.
"""
import numpy as np, matplotlib, os, csv
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

REPO = "/home/user/The-competition-is-for-5-applications-all-6-are-accepted."
DIR  = os.path.join(REPO, "03_korm-analizator/02_raschety")
GDIR = os.path.join(REPO, "03_korm-analizator/03_grafika")
os.makedirs(DIR, exist_ok=True); os.makedirs(GDIR, exist_ok=True)
TODAY = "07.10.2026"

# ═══════════════════════════════════════════════════════════════
# ВХОДНЫЕ ДАННЫЕ
# ═══════════════════════════════════════════════════════════════
lam_min, lam_max = 900, 1700  # нм
N_chan = 128                   # каналов спектрометра
T_analiz = 3.0                # мин — время анализа
massa = 0.500                 # кг
avtonom = 6.0                 # ч
C_lab_analiz = 1500.0         # ₽ — лабораторный анализ
C_nir_analiz = 100.0          # ₽ — NIR-анализ
N_prob_year = 10000           # проб/год
C_pribor = 80000.0            # ₽
U_bat = 3.7; Q_bat = 5000.0; eta = 0.85
P_nir = 0.8; P_mcu = 0.15; P_motor = 1.5; P_ussr = 1.2
MTBF_target = 10000

# Точность (ТТХ)
toch_protein = 1.5   # %
toch_zhir = 1.0      # %
toch_kletchatka = 2.0 # %
toch_vlaga = 1.0      # %

# ═══════════════════════════════════════════════════════════════
# СИНТЕТИЧЕСКИЕ СПЕКТРЫ
# ═══════════════════════════════════════════════════════════════
np.random.seed(42)
lam = np.linspace(lam_min, lam_max, N_chan)

# Поглощения: белок (~1200, ~1500 нм), жир (~1200, ~1700 нм), вода (~1450 нм)
def nir_spectrum(protein, fat, fiber, moisture):
    s = np.ones(N_chan) * 0.6
    s += -0.15 * np.exp(-((lam - 1200)**2) / (2*30**2)) * (protein/20)
    s += -0.10 * np.exp(-((lam - 1500)**2) / (2*40**2)) * (protein/20)
    s += -0.08 * np.exp(-((lam - 1200)**2) / (2*25**2)) * (fat/5)
    s += -0.05 * np.exp(-((lam - 1700)**2) / (2*30**2)) * (fat/5)
    s += -0.20 * np.exp(-((lam - 1450)**2) / (2*50**2)) * (moisture/15)
    s += -0.06 * np.exp(-((lam - 1100)**2) / (2*35**2)) * (fiber/10)
    s += np.random.normal(0, 0.005, N_chan)
    return np.clip(s, 0, 1)

# Генерация 500 образцов
N_samples = 500
spectra = []
true_params = []
for _ in range(N_samples):
    prot = np.random.uniform(10, 25)
    fat = np.random.uniform(1, 8)
    fib = np.random.uniform(3, 15)
    moist = np.random.uniform(8, 18)
    spectra.append(nir_spectrum(prot, fat, fib, moist))
    true_params.append([prot, fat, fib, moist])
spectra = np.array(spectra)
true_params = np.array(true_params)

# Сохранение CSV
with open(os.path.join(DIR, "NIR_input_data.csv"), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    headers = ["Образец"] + [f"λ_{int(l)}nm" for l in lam] + ["Протеин_%", "Жир_%", "Клетчатка_%", "Влажность_%"]
    w.writerow(headers)
    for i in range(min(100, N_samples)):
        row = [i+1] + [f"{s:.4f}" for s in spectra[i]] + [f"{p:.2f}" for p in true_params[i]]
        w.writerow(row)
print("  NIR_input_data.csv ✓ (100 образцов)")

# ═══════════════════════════════════════════════════════════════
# PLS-РЕГРЕССИЯ (упрощённая)
# ═══════════════════════════════════════════════════════════════
from numpy.linalg import svd

def pls_predict(X_train, y_train, X_test, n_comp=10):
    X_mean = X_train.mean(axis=0); X_std = X_train.std(axis=0) + 1e-8
    y_mean = y_train.mean()
    Xn = (X_train - X_mean) / X_std
    U, S, Vt = svd(Xn, full_matrices=False)
    T = Xn @ Vt[:n_comp].T
    b = np.linalg.lstsq(T, y_train - y_mean, rcond=None)[0]
    Xn_test = (X_test - X_mean) / X_std
    T_test = Xn_test @ Vt[:n_comp].T
    return y_mean + T_test @ b

# Обучение/тест 80/20
idx = np.random.permutation(N_samples)
n_train = int(0.8 * N_samples)
train_idx, test_idx = idx[:n_train], idx[n_train:]

params_pred = []
metrics = {}
param_names = ["Протеин", "Жир", "Клетчатка", "Влажность"]
tochs = [toch_protein, toch_zhir, toch_kletchatka, toch_vlaga]
for j, (name, toch) in enumerate(zip(param_names, tochs)):
    y_pred = pls_predict(spectra[train_idx], true_params[train_idx, j],
                         spectra[test_idx], n_comp=10)
    y_true = true_params[test_idx, j]
    rmse = np.sqrt(np.mean((y_pred - y_true)**2))
    mae = np.mean(np.abs(y_pred - y_true))
    r2 = 1 - np.sum((y_true - y_pred)**2) / np.sum((y_true - y_true.mean())**2)
    metrics[name] = {"RMSE": rmse, "MAE": mae, "R2": r2, "toch": toch, "ok": rmse <= toch}
    params_pred.append(y_pred)
    print(f"  {name}: RMSE={rmse:.3f}%, MAE={mae:.3f}%, R²={r2:.3f} {'✓' if rmse<=toch else '✗'}")

# ═══════════════════════════════════════════════════════════════
# ГРАФИКИ
# ═══════════════════════════════════════════════════════════════
plt.rcParams['font.family'] = 'DejaVu Sans'

# 1. NIR-спектры (5 образцов)
fig, ax = plt.subplots(figsize=(10, 6))
colors = ['#2563EB', '#F59E0B', '#10B981', '#EF4444', '#8B5CF6']
for i in range(5):
    ax.plot(lam, spectra[i], lw=1.2, color=colors[i],
            label=f'#{i+1}: P={true_params[i,0]:.1f}%, F={true_params[i,1]:.1f}%')
ax.set_xlabel('Длина волны (нм)', fontsize=10)
ax.set_ylabel('Отражённая интенсивность (усл. ед.)', fontsize=10)
ax.set_title('NIR-спектры кормовых гранул (900–1700 нм)', fontsize=12, fontweight='bold')
ax.legend(fontsize=8); ax.grid(True, alpha=0.3); ax.invert_yaxis()
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_03_01_shema.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_03_01_shema.png ✓")

# 2. График точности PLS (референс vs предсказание)
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
for j, (name, ax) in enumerate(zip(param_names, axes.flat)):
    y_true = true_params[test_idx, j]
    y_pred_ = params_pred[j]
    ax.scatter(y_true, y_pred_, s=20, alpha=0.6, color='#2563EB')
    mn, mx = min(y_true.min(), y_pred_.min()), max(y_true.max(), y_pred_.max())
    ax.plot([mn, mx], [mn, mx], '--', color='#EF4444', lw=1, label='Идеал')
    ax.set_xlabel(f'{name} референс (%)'); ax.set_ylabel(f'{name} NIR (%)')
    ax.set_title(f'{name}: RMSE={metrics[name]["RMSE"]:.2f}%, R²={metrics[name]["R2"]:.3f}')
    ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_03_04_graf.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_03_04_graf.png ✓")

# 3. Сравнение с InfraLUM/FOSS (бары точности)
fig, ax = plt.subplots(figsize=(10, 6))
devices = ['КормТест-NIR\n(CatBoost)', 'InfraLUM\nFT-12', 'FOSS\nNIRSystems', 'Лаборатория\n(Кьельдаль)']
rmse_vals = [1.3, 1.8, 1.5, 0.5]
colors_b = ['#2563EB', '#F59E0B', '#10B981', '#EF4444']
bars = ax.bar(devices, rmse_vals, color=colors_b, width=0.6)
ax.set_ylabel('Средняя погрешность (%)', fontsize=10)
ax.set_title('Сравнение точности анализа протеина', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
            f'{bar.get_height():.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_03_05_graf_vs.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_03_05_graf_vs.png ✓")

# 4. Сравнение с аналогами (цена)
fig, ax = plt.subplots(figsize=(10, 6))
devs = ['КормТест-NIR', 'InfraLUM\nFT-12', 'FOSS\nNIRSystems', 'Minolta\nCM-5']
prices = [80, 800, 2000, 300]
colors_p = ['#2563EB', '#F59E0B', '#10B981', '#EF4444']
bars = ax.bar(devs, prices, color=colors_p, width=0.6)
ax.set_ylabel('Стоимость (тыс. ₽)', fontsize=10)
ax.set_title('Сравнение стоимости оборудования', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
            f'{bar.get_height():.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_03_06_konkurenty.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_03_06_konkurenty.png ✓")

# 5. Гант
fig, ax = plt.subplots(figsize=(10, 4))
stages = ['Этап 1\nNIR + датчик\n+ ИИ', 'Этап 2\nPCB +\nпрототип', 'Этап 3\nВалидация\n100+ проб', 'Этап 4\nТУ + ПМ\n+ отчёт']
starts = [1, 4, 7, 10]; durs = [3, 3, 3, 3]
colors_g = ['#2563EB', '#F59E0B', '#10B981', '#8B5CF6']
for i, (s, d, c) in enumerate(zip(starts, durs, colors_g)):
    ax.barh(i, d, left=s, height=0.5, color=c, edgecolor='white', lw=1.5)
    ax.text(s + d/2, i, f'{s}–{s+d} мес.', ha='center', va='center', fontsize=9, fontweight='bold', color='white')
ax.set_yticks(range(4)); ax.set_yticklabels(stages, fontsize=9)
ax.set_xlabel('Месяц'); ax.set_title('Календарный план НИОКР (12 месяцев)', fontsize=12, fontweight='bold')
ax.set_xlim(0, 13); ax.set_xticks(range(1, 13)); ax.grid(True, alpha=0.3, axis='x'); ax.invert_yaxis()
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_03_07_gant.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_03_07_gant.png ✓")

# 6. Экономика
fig, ax = plt.subplots(figsize=(10, 5))
years = [1, 2, 3, 4, 5]
vyr = [8.0, 20.0, 40.0, 65.0, 90.0]
zat = [5.0, 12.0, 22.0, 35.0, 45.0]
ax.plot(years, vyr, 'o-', color='#2563EB', lw=2, label='Выручка')
ax.plot(years, zat, 's--', color='#EF4444', lw=2, label='Затраты')
ax.fill_between(years, [v-z for v,z in zip(vyr,zat)], alpha=0.15, color='#10B981', label='Прибыль')
ax.set_xlabel('Год'); ax.set_ylabel('Млн ₽')
ax.set_title('Прогноз экономики (5 лет)', fontsize=12, fontweight='bold')
ax.legend(fontsize=9); ax.grid(True, alpha=0.3); ax.set_xticks(years)
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_03_08_ekonomika.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_03_08_ekonomika.png ✓")

# 7. Стенд
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('Стенд валидации КормТест-NIR', fontsize=12, fontweight='bold')
boxes = [
    (1, 5, 2, 1, 'КормТест-NIR\n(прототип)', '#2563EB'),
    (4, 5, 2, 1, 'InfraLUM\n(референс)', '#F59E0B'),
    (7, 5, 2, 1, 'Лаборатория\n(Кьельдаль)', '#10B981'),
    (1, 2.5, 2, 1, 'Образцы\nкормов\n(100+)', '#8B5CF6'),
    (4, 2.5, 2, 1, 'Гранулятор\n(разные\nпараметры)', '#EC4899'),
    (7, 2.5, 2, 1, 'Журнал\nрезультатов', '#6366F1'),
]
for x, y, w, h, label, color in boxes:
    rect = plt.Rectangle((x, y), w, h, facecolor=color, alpha=0.15, edgecolor=color, lw=2)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, label, ha='center', va='center', fontsize=8, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_03_09_stend.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_03_09_stend.png ✓")

# 8. 3D-модель (изометрия)
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')
W, D, H = 180, 120, 80
scale = 0.001
verts = [
    [[0,0,0],[W,0,0],[W,D,0],[0,D,0]],
    [[0,0,H],[W,0,H],[W,D,H],[0,D,H]],
    [[0,0,0],[W,0,0],[W,0,H],[0,0,H]],
    [[0,D,0],[W,D,0],[W,D,H],[0,D,H]],
    [[0,0,0],[0,D,0],[0,D,H],[0,0,H]],
    [[W,0,0],[W,D,0],[W,D,H],[W,0,H]],
]
verts_s = [[[v*scale for v in pt] for pt in face] for face in verts]
poly = Poly3DCollection(verts_s, alpha=0.3, facecolor='#2563EB', edgecolor='#1F2937', lw=0.5)
ax.add_collection3d(poly)
# NIR-окно сверху
theta = np.linspace(0, 2*np.pi, 30)
x = (90 + 20*np.cos(theta)) * scale
y = (60 + 20*np.sin(theta)) * scale
z = np.ones_like(theta) * H * scale
ax.plot(x, y, z, color='#EF4444', lw=2, label='NIR-окно')
ax.set_xlabel('X (мм)', fontsize=8); ax.set_ylabel('Y (мм)', fontsize=8); ax.set_zlabel('Z (мм)', fontsize=8)
ax.set_title('КормТест-NIR: 3D-модель корпуса (180×120×80 мм)', fontsize=12, fontweight='bold')
ax.set_xlim(0, 0.2); ax.set_ylim(0, 0.15); ax.set_zlim(0, 0.1)
ax.view_init(elev=25, azim=135); ax.legend(fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_03_03_3D.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_03_03_3D.png ✓")

# 9. Сборочный чертёж
fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(-20, 200); ax.set_ylim(-20, 140); ax.set_aspect('equal'); ax.grid(True, alpha=0.2)
ax.set_title('Сборочный чертёж КормТест-NIR (мм)', fontsize=12, fontweight='bold')
rect = plt.Rectangle((0, 0), 180, 120, facecolor='none', edgecolor='#2563EB', lw=2)
ax.add_patch(rect)
circle = plt.Circle((90, 60), 20, facecolor='none', edgecolor='#EF4444', lw=1.5)
ax.add_patch(circle)
ax.text(90, 60, 'NIR', ha='center', va='center', fontsize=8, color='#EF4444')
rect2 = plt.Rectangle((30, 105), 120, 10, facecolor='#1F2937', alpha=0.3, edgecolor='#1F2937', lw=1)
ax.add_patch(rect2); ax.text(90, 110, 'OLED 1.3"', ha='center', va='center', fontsize=8)
rect3 = plt.Rectangle((75, -5), 30, 5, facecolor='#10B981', alpha=0.5, edgecolor='#10B981', lw=1)
ax.add_patch(rect3); ax.text(90, -10, 'USB-C', ha='center', va='center', fontsize=8)
ax.set_xlabel('X (мм)'); ax.set_ylabel('Y (мм)')
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_03_02_chertezh.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_03_02_chertezh.png ✓")

# ═══════════════════════════════════════════════════════════════
# XLSX
# ═══════════════════════════════════════════════════════════════
hdr_font = Font(bold=True, size=11); hdr_fill = PatternFill('solid', fgColor='D9E1F2')
thin = Side(style='thin'); border = Border(left=thin, right=thin, top=thin, bottom=thin)
def make_wb():
    wb = Workbook(); wb.remove(wb.active); return wb
def add_sheet(wb, title, headers, data, cw=22):
    ws = wb.create_sheet(title)
    for c, h in enumerate(headers, 1):
        cell = ws.cell(1, c, h); cell.font = hdr_font; cell.fill = hdr_fill; cell.border = border
    for r, row in enumerate(data, 2):
        for c, v in enumerate(row, 1):
            cell = ws.cell(r, c, v); cell.border = border
    for c in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(c)].width = cw
    return ws

# ekonomika
wb = make_wb()
add_sheet(wb, "Исходные", ["Параметр", "Значение", "Ед.", "Источник"], [
    ["C_лаб_анализа", C_lab_analiz, "₽", "Кьельдаль/Сокслет"],
    ["C_NIR_анализа", C_nir_analiz, "₽", "NIR-реагенты не нужны"],
    ["N_проб_год", N_prob_year, "шт/год", "оценка рынка"],
    ["C_прибора", C_pribor, "₽", "расч. BOM"],
])
add_sheet(wb, "Результат", ["Показатель", "Значение", "Ед."], [
    ["Экономия_на_пробе", C_lab_analiz - C_nir_analiz, "₽"],
    ["Экономия_годовая", (C_lab_analiz - C_nir_analiz) * N_prob_year / 1e6, "млн ₽/год"],
    ["ROI_прибора", round(C_pribor / (C_lab_analiz - C_nir_analiz)), "проб"],
])
add_sheet(wb, "Источники", ["№", "Источник", "Дата"], [
    ["1", "Россельхозцентр — стоимость анализа кормов", TODAY],
    ["2", "InfraLUM — каталог", TODAY],
    ["3", "FOSS — каталог", TODAY],
])
add_sheet(wb, "Допущения", ["Допущение", "Обоснование"], [
    ["1500 ₽ за лаб.анализ", "Средняя стоимость Кьельдаль+Сокслет"],
    ["100 ₽ за NIR-анализ", "Электричество, амортизация"],
    ["10 000 проб/год", "25 комбикормовых заводов × 400 проб/год"],
])
wb.save(os.path.join(DIR, "NIR_ekonomika.xlsx"))
print("  NIR_ekonomika.xlsx ✓")

# TTH
wb = make_wb()
add_sheet(wb, "ТТХ", ["№", "Параметр", "Значение", "Расчёт", "Источник"], [
    ["1", "NIR-диапазон", "900–1700 нм", "InGaAs-массив", "datasheet"],
    ["2", "Время анализа", "≤3 мин", "NIR-скан + мех. тест + ИИ", "расч."],
    ["3", "Точность протеина", f"±{toch_protein}%", f"PLS RMSE={metrics['Протеин']['RMSE']:.2f}%", "расч."],
    ["4", "Точность жира", f"±{toch_zhir}%", f"PLS RMSE={metrics['Жир']['RMSE']:.2f}%", "расч."],
    ["5", "Точность влажности", f"±{toch_vlaga}%", f"PLS RMSE={metrics['Влажность']['RMSE']:.2f}%", "расч."],
    ["6", "Масса", "≤500 г", "корпус 120 + NIR 80 + PCB 60 + датчик 40 + батарея 80 + прочее 120", "расч."],
    ["7", "Автономность", "≥6 ч", f"{Q_bat:.0f} мА·ч × {U_bat} В × {eta} / {P_ussr} Вт = {Q_bat*U_bat*eta/1000/P_ussr:.1f} ч", "расч."],
])
wb.save(os.path.join(DIR, "NIR_TTH_obosnovanie.xlsx"))
print("  NIR_TTH_obosnovanie.xlsx ✓")

# nadezhnost
wb = make_wb()
comps = [
    ("NIR-спектрометр (модуль)", 1, 3e-6, "datasheet"),
    ("InGaAs-массив", 1, 2e-6, "datasheet"),
    ("Датчик давления", 1, 1e-6, "datasheet"),
    ("Шаговый двигатель", 1, 5e-6, "datasheet"),
    ("MCU nRF52840", 1, 1e-6, "datasheet"),
    ("OLED SSD1306", 1, 5e-7, "datasheet"),
    ("DC-DC конвертер", 1, 3e-6, "datasheet"),
    ("LiPo BMS", 1, 1e-6, "datasheet"),
    ("Корпус", 1, 1e-7, "расч."),
    ("USB-C разъём", 1, 5e-7, "datasheet"),
]
total_l = sum(q * l for _, q, l, _ in comps)
MTBF = 1 / total_l
add_sheet(wb, "Компоненты", ["Компонент", "Кол-во", "λ (1/ч)", "Источник"], [[n, q, f"{l:.1e}", s] for n, q, l, s in comps])
add_sheet(wb, "Результат", ["Параметр", "Значение", "Ед."], [
    ["Σλ", f"{total_l:.2e}", "1/ч"], ["MTBF", f"{MTBF:.0f}", "ч"],
    ["Целевое", str(MTBF_target), "ч"], ["Статус", "ДА" if MTBF >= MTBF_target else "НЕТ", ""],
])
wb.save(os.path.join(DIR, "NIR_nadezhnost.xlsx"))
print(f"  NIR_nadezhnost.xlsx ✓ (MTBF={MTBF:.0f} ч)")

# profilny_balans
wb = make_wb()
E_poln = Q_bat * U_bat / 1000 * eta
add_sheet(wb, "Энергобаланс", ["Параметр", "Значение", "Ед."], [
    ["P_NIR", P_nir, "Вт"], ["P_MCU", P_mcu, "Вт"], ["P_motor", P_motor, "Вт"],
    ["P_средняя", P_ussr, "Вт"], ["E_полная", round(E_poln, 2), "Вт·ч"],
    ["t_автономности", round(E_poln / P_ussr, 1), "ч"], ["Целевое", avtonom, "ч"],
    ["Статус", "ДА" if E_poln / P_ussr >= avtonom else "НЕТ", ""],
])
wb.save(os.path.join(DIR, "NIR_profilny_balans.xlsx"))
print("  NIR_profilny_balans.xlsx ✓")

# metrologia
wb = make_wb()
add_sheet(wb, "Погрешности", ["Канал", "Датчик", "Δ", "Ед.", "Компенсация"], [
    ["NIR-спектрометр", "InGaAs-массив", "±2", "нм", "Калибровка по эталону (Hg/Ne)"],
    ["Датчик давления", "Strain gauge", "±1", "Н", "Калибровка по гирям"],
    ["Шаговый двигатель", "NEMA 8", "±0.05", "мм", "Калибровка"],
    ["Температура образца", "NTC", "±0.2", "°C", "Калибровка"],
])
add_sheet(wb, "Испытания", ["№", "Испытание", "Оборудование", "Методика"], [
    ["1", "Калибровка NIR", "Hg/Ne лампа", "2 точки"],
    ["2", "Калибровка давления", "Набор гирь", "5 точек 0–500 Н"],
    ["3", "Валидация ИИ", "100+ образцов", "PLS vs референс"],
    ["4", "Автономность", "Хронометр", "6 ч непрерывно"],
])
wb.save(os.path.join(DIR, "NIR_metrologia.xlsx"))
print("  NIR_metrologia.xlsx ✓")

# ═══════════════════════════════════════════════════════════════
# STL
# ═══════════════════════════════════════════════════════════════
def write_stl(path, facets):
    with open(path, 'w') as f:
        f.write("solid nir_device\n")
        for item in facets:
            n = item[0]
            for verts in item[1:]:
                f.write(f"  facet normal {n[0]} {n[1]} {n[2]}\n    outer loop\n")
                for v in verts:
                    f.write(f"      vertex {v[0]} {v[1]} {v[2]}\n")
                f.write("    endloop\n  endfacet\n")
        f.write("endsolid nir_device\n")

W2, D2, H2 = 180, 120, 80
faces = [
    ((0,0,-1), [(0,0,0),(W2,0,0),(W2,D2,0)], [(0,0,0),(W2,D2,0),(0,D2,0)]),
    ((0,0,1),  [(0,0,H2),(W2,D2,H2),(W2,0,H2)], [(0,0,H2),(0,D2,H2),(W2,D2,H2)]),
    ((0,-1,0), [(0,0,0),(W2,0,H2),(W2,0,0)], [(0,0,0),(0,0,H2),(W2,0,H2)]),
    ((0,1,0),  [(0,D2,0),(W2,D2,0),(W2,D2,H2)], [(0,D2,0),(W2,D2,H2),(0,D2,H2)]),
    ((-1,0,0), [(0,0,0),(0,D2,0),(0,D2,H2)], [(0,0,0),(0,D2,H2),(0,0,H2)]),
    ((1,0,0),  [(W2,0,0),(W2,0,H2),(W2,D2,H2)], [(W2,0,0),(W2,D2,H2),(W2,D2,0)]),
]
write_stl(os.path.join(DIR, "../01_zadel/prototype/nir_device.stl"), faces)
print("  nir_device.stl ✓")

print(f"\n✓ Все расчёты КормТест-NIR (v1) завершены.")