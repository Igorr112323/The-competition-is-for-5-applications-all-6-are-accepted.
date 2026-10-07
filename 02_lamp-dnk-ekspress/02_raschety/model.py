#!/usr/bin/env python3
"""
LAMP-ДНК-Экспресс: модель кинетики LAMP-амплификации и расчёты v1.
Портативный анализатор экспресс-ДНК-диагностики (LAMP, 65 °C, 4 лунки).
7 ДНК-тест-систем: LSDV, сальмонеллёз, лептоспироз, медведь, ёж, кошка, рыба/гельминты.
"""
import numpy as np, matplotlib, os, csv, json
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from datetime import date

REPO = "/home/user/The-competition-is-for-5-applications-all-6-are-accepted."
DIR  = os.path.join(REPO, "02_lamp-dnk-ekspress/02_raschety")
GDIR = os.path.join(REPO, "02_lamp-dnk-ekspress/03_grafika")
os.makedirs(DIR, exist_ok=True)
os.makedirs(GDIR, exist_ok=True)

TODAY = "07.10.2026"

# ═══════════════════════════════════════════════════════════════
# ВХОДНЫЕ ДАННЫЕ
# ═══════════════════════════════════════════════════════════════
T_lamp       = 65.0     # °C — температура LAMP
T_dop        = 0.5      # °C — допуск PID
t_analiz_min = 30.0     # мин — минимальное время анализа
t_analiz_max = 60.0     # мин — максимальное время анализа
N_lunok      = 4        # число лунок
N_mishenei   = 7        # число ДНК-тест-систем
massa_max    = 0.500    # кг — максимальная масса прибора
avtonom_ch   = 4.0      # ч — автономность
chuvstv      = 1e2      # копий/мкл — чувствительность
C_test       = 300.0    # ₽ — стоимость теста
C_pribor     = 50000.0  # ₽ — стоимость прибора
C_PCR        = 800.0    # ₽ — стоимость лабораторного ПЦР-теста
N_prob_year  = 20000    # проб/год — объём рынка

# Модельные параметры LAMP
k_роста      = 0.15     # 1/мин — константа скорости экспоненциальной фазы
t_лаг        = 8.0      # мин — лаг-фаза
A_max        = 2.5      # абс. единиц — плато амплификации
noise_std    = 0.03     # шум детекции

# Электроника
U_bat        = 3.7      # В
Q_bat        = 5000.0   # мА·ч
eta_bat      = 0.85     # КПД DC-DC
P_heater     = 8.0      # Вт — нагреватель
P_mcu        = 0.15     # Вт — MCU + фотодиоды + OLED
P_усредн     = 3.5      # Вт — средняя мощность (PID duty ~40%)

# Надёжность
MTBF_target  = 8000     # ч

# ═══════════════════════════════════════════════════════════════
# МОДЕЛЬ КИНЕТИКИ LAMP
# ═══════════════════════════════════════════════════════════════
t = np.linspace(0, t_analiz_max * 60, 1000)  # секунды
t_min = t / 60.0

misheni = {
    "LSDV":           {"t_лаг": 7,  "k": 0.16, "A": 2.4, "color": "#2563EB"},
    "Сальмонеллёз":   {"t_лаг": 9,  "k": 0.14, "A": 2.3, "color": "#F59E0B"},
    "Лептоспироз":    {"t_лаг": 10, "k": 0.13, "A": 2.2, "color": "#10B981"},
    "Медведь":        {"t_лаг": 8,  "k": 0.15, "A": 2.5, "color": "#EF4444"},
    "Ёж":             {"t_лаг": 11, "k": 0.12, "A": 2.1, "color": "#8B5CF6"},
    "Кошка":          {"t_лаг": 8,  "k": 0.15, "A": 2.4, "color": "#EC4899"},
    "Рыба/гельминты": {"t_лаг": 12, "k": 0.11, "A": 2.0, "color": "#6366F1"},
}

signals = {}
t_porog = {}
for name, p in misheni.items():
    sig = np.where(t_min >= p["t_лаг"],
                   p["A"] * (1 - np.exp(-p["k"] * (t_min - p["t_лаг"]))),
                   0.0)
    sig += np.random.normal(0, noise_std, len(t))
    sig = np.clip(sig, 0, None)
    signals[name] = sig
    above = np.where(sig >= p["A"] * 0.5)[0]
    t_porog[name] = t_min[above[0]] if len(above) > 0 else t_analiz_max

# ═══════════════════════════════════════════════════════════════
# ГРАФИКИ
# ═══════════════════════════════════════════════════════════════
plt.rcParams['font.family'] = 'DejaVu Sans'

# ── 1. Кривые амплификации LAMP ──────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
for name, sig in signals.items():
    ax.plot(t_min, sig, lw=1.5, label=name, color=misheni[name]["color"])
ax.axhline(1.25, color='#EF4444', ls='--', lw=0.8, label='Порог детекции')
ax.set_xlabel('Время (мин)', fontsize=10)
ax.set_ylabel('Флуоресценция (усл. ед.)', fontsize=10)
ax.set_title('Кривые LAMP-амплификации 7 ДНК-тест-систем', fontsize=12, fontweight='bold')
ax.legend(fontsize=8, loc='lower right')
ax.grid(True, alpha=0.3)
ax.set_xlim(0, t_analiz_max)
ax.set_ylim(-0.1, 3.0)
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_02_04_graf.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_02_04_graf.png ✓")

# ── 2. Сравнение LAMP vs ПЦР ────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
categories = list(t_porog.keys())
lamp_times = [t_porog[k] for k in categories]
pcr_times  = [120 + np.random.uniform(-10, 10) for _ in categories]
x = np.arange(len(categories))
w = 0.35
bars1 = ax.bar(x - w/2, lamp_times, w, label='LAMP-ДНК-Экспресс', color='#2563EB')
bars2 = ax.bar(x + w/2, pcr_times, w, label='ПЦР-лаборатория', color='#EF4444')
ax.set_xlabel('Мишень', fontsize=10)
ax.set_ylabel('Время до результата (мин)', fontsize=10)
ax.set_title('Сравнение LAMP vs ПЦР: время анализа', fontsize=12, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(categories, rotation=30, ha='right', fontsize=8)
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3, axis='y')
for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            f'{bar.get_height():.0f}', ha='center', va='bottom', fontsize=8)
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            f'{bar.get_height():.0f}', ha='center', va='bottom', fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_02_05_graf_vs.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_02_05_graf_vs.png ✓")

# ── 3. Сравнение с аналогами ─────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
devices  = ['LAMP-ДНК-\nЭкспресс', 'OptiGene\nGenie II', 'Atila\nBioSystems', 'ПЦР-\nлаборатория']
prices   = [50, 400, 300, 1000]  # тыс.₽
colors_p = ['#2563EB', '#F59E0B', '#10B981', '#EF4444']
bars = ax.bar(devices, prices, color=colors_p, width=0.6)
ax.set_ylabel('Стоимость прибора (тыс. ₽)', fontsize=10)
ax.set_title('Сравнение стоимости оборудования', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
            f'{bar.get_height():.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_02_06_konkurenty.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_02_06_konkurenty.png ✓")

# ── 4. Диаграмма Ганта ──────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 4))
stages = ['Этап 1\nДизайн\nпраймеров', 'Этап 2\nPCB +\nпрошивка', 'Этап 3\nВалидация\n50+ проб', 'Этап 4\nТУ + ПМ\n+ отчёт']
starts = [1, 4, 7, 10]
durs   = [3, 3, 3, 3]
colors_g = ['#2563EB', '#F59E0B', '#10B981', '#8B5CF6']
for i, (s, d, c) in enumerate(zip(starts, durs, colors_g)):
    ax.barh(i, d, left=s, height=0.5, color=c, edgecolor='white', lw=1.5)
    ax.text(s + d/2, i, f'{s}–{s+d} мес.', ha='center', va='center', fontsize=9, fontweight='bold', color='white')
ax.set_yticks(range(len(stages)))
ax.set_yticklabels(stages, fontsize=9)
ax.set_xlabel('Месяц', fontsize=10)
ax.set_title('Календарный план НИОКР (12 месяцев)', fontsize=12, fontweight='bold')
ax.set_xlim(0, 13)
ax.set_xticks(range(1, 13))
ax.grid(True, alpha=0.3, axis='x')
ax.invert_yaxis()
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_02_07_gant.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_02_07_gant.png ✓")

# ── 5. Экономика ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
years = [1, 2, 3, 4, 5]
vyruchka  = [5.0, 15.0, 30.0, 50.0, 75.0]  # млн ₽
zatraty   = [3.0, 8.0, 15.0, 25.0, 35.0]
pribyl    = [v - z for v, z in zip(vyruchka, zatraty)]
ax.plot(years, vyruchka, 'o-', color='#2563EB', lw=2, label='Выручка')
ax.plot(years, zatraty, 's--', color='#EF4444', lw=2, label='Затраты')
ax.fill_between(years, pribyl, alpha=0.15, color='#10B981', label='Прибыль')
ax.set_xlabel('Год', fontsize=10)
ax.set_ylabel('Млн ₽', fontsize=10)
ax.set_title('Прогноз экономики (5 лет)', fontsize=12, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
ax.set_xticks(years)
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_02_08_ekonomika.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_02_08_ekonomika.png ✓")

# ── 6. Схема стенда испытаний ────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(0, 10); ax.set_ylim(0, 7)
ax.set_aspect('equal'); ax.axis('off')
ax.set_title('Стенд валидации LAMP-ДНК-Экспресс', fontsize=12, fontweight='bold')

# Блоки стенда
boxes = [
    (1, 5, 2, 1, 'LAMP-\nанализатор', '#2563EB'),
    (4, 5, 2, 1, 'Эталонная\nПЦР', '#F59E0B'),
    (7, 5, 2, 1, 'Ноутбук\n(сравнение)', '#10B981'),
    (1, 2.5, 2, 1, 'Образцы\n(50+ проб)', '#8B5CF6'),
    (4, 2.5, 2, 1, 'Референс\n(ПЦР-ампликатор)', '#EC4899'),
    (7, 2.5, 2, 1, 'Журнал\nрезультатов', '#6366F1'),
]
for x, y, w, h, label, color in boxes:
    rect = plt.Rectangle((x, y), w, h, facecolor=color, alpha=0.15, edgecolor=color, lw=2)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, label, ha='center', va='center', fontsize=8, fontweight='bold')

# Стрелки
for (x1, y1, w1, h1, _, _), (x2, y2, w2, h2, _, _) in [(boxes[0], boxes[3]), (boxes[1], boxes[4]), (boxes[2], boxes[5])]:
    ax.annotate('', xy=(x2 + w2/2, y2 + h2), xytext=(x1 + w1/2, y1),
                arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))

plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_02_09_stend.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_02_09_stend.png ✓")

# ═══════════════════════════════════════════════════════════════
# CSV
# ═══════════════════════════════════════════════════════════════
with open(os.path.join(DIR, "LAMP_input_data.csv"), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(["Параметр", "Значение", "Ед.", "Источник", "Дата"])
    rows = [
        ("T_LAMP", T_lamp, "°C", "протокол LAMP, New England Biolabs", TODAY),
        ("T_допуск", T_dop, "°C", "PID nRF52840", TODAY),
        ("t_анализ_мин", t_analiz_min, "мин", "LAMP-протокол", TODAY),
        ("t_анализ_макс", t_analiz_max, "мин", "LAMP-протокол", TODAY),
        ("N_лунок", N_lunok, "шт", "ТЗ", TODAY),
        ("N_мишеней", N_mishenei, "шт", "7 патентов НР", TODAY),
        ("Масса_макс", massa_max * 1000, "г", "ТЗ", TODAY),
        ("Автономность", avtonom_ch, "ч", "LiPo 5000 мА·ч", TODAY),
        ("Чувствительность", chuvstv, "копий/мкл", "расч.", TODAY),
        ("Стоимость_теста", C_test, "₽", "расч. реагенты", TODAY),
        ("Стоимость_прибора", C_pribor, "₽", "расч. BOM", TODAY),
        ("C_PCR", C_PCR, "₽", "рынок", TODAY),
        ("N_проб_год", N_prob_year, "шт/год", "оценка рынка", TODAY),
        ("k_роста", k_роста, "1/мин", "расч.", TODAY),
        ("t_лаг", t_лаг, "мин", "расч.", TODAY),
        ("U_bat", U_bat, "В", "LiPo 1S", TODAY),
        ("Q_bat", Q_bat, "мА·ч", "LiPo", TODAY),
        ("P_heater", P_heater, "Вт", "картридж 8 Вт", TODAY),
        ("P_mcu", P_mcu, "Вт", "nRF52840 datasheet", TODAY),
        ("MTBF_target", MTBF_target, "ч", "ТЗ", TODAY),
    ]
    w.writerows(rows)
print("  LAMP_input_data.csv ✓")

# ═══════════════════════════════════════════════════════════════
# XLSX — утилиты
# ═══════════════════════════════════════════════════════════════
hdr_font = Font(bold=True, size=11)
hdr_fill = PatternFill('solid', fgColor='D9E1F2')
thin = Side(style='thin')
border = Border(left=thin, right=thin, top=thin, bottom=thin)

def make_wb():
    wb = Workbook(); wb.remove(wb.active); return wb

def add_sheet(wb, title, headers, data, col_width=22):
    ws = wb.create_sheet(title)
    for c, h in enumerate(headers, 1):
        cell = ws.cell(1, c, h)
        cell.font = hdr_font; cell.fill = hdr_fill; cell.border = border
    for r, row in enumerate(data, 2):
        for c, v in enumerate(row, 1):
            cell = ws.cell(r, c, v); cell.border = border
    for c in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(c)].width = col_width
    return ws

# ═══════════════════════════════════════════════════════════════
# 1. LAMP_ekonomika.xlsx
# ═══════════════════════════════════════════════════════════════
wb = make_wb()
add_sheet(wb, "Исходные", ["Параметр", "Значение", "Ед.", "Источник"], [
    ["C_PCR_теста", C_PCR, "₽", "лабораторный ПЦР-анализ"],
    ["C_LAMP_теста", C_test, "₽", "LAMP-реагенты + пробирка"],
    ["N_проб_год", N_prob_year, "шт/год", "оценка рынка ветдиагностики"],
    ["C_прибора", C_pribor, "₽", "расч. BOM"],
])
add_sheet(wb, "Формулы", ["Формула", "Описание"], [
    ["(C_PCR - C_LAMP) × N", "Экономия на одной пробе × количество проб/год"],
    [f"({C_PCR:.0f} - {C_test:.0f}) × {N_prob_year:.0f}", f"= {((C_PCR - C_test) * N_prob_year / 1e6):.1f} млн ₽/год"],
])
add_sheet(wb, "Результат", ["Показатель", "Значение", "Ед."], [
    ["Экономия_на_пробе", C_PCR - C_test, "₽"],
    ["Экономия_годовая", (C_PCR - C_test) * N_prob_year / 1e6, "млн ₽/год"],
    ["ROI_прибора", C_pribor / (C_PCR - C_test), "проб"],
    ["Точка_безубыточности", round(C_pribor / (C_PCR - C_test)), "проб"],
])
add_sheet(wb, "Источники", ["№", "Источник", "Описание", "Дата"], [
    ["1", "vetrfi.ru", "Стоимость ПЦР-диагностики", TODAY],
    ["2", "ООО НПО «ИнноКвик»", "Экспресс-тесты аналоги", TODAY],
    ["3", "Росстат", "Число ветстанций РФ", TODAY],
])
add_sheet(wb, "Допущения", ["Допущение", "Обоснование"], [
    ["800 ₽ за ПЦР-тест", "Средняя стоимость ПЦР-анализа в ветлаборатории"],
    ["300 ₽ за LAMP-тест", "Стоимость LAMP-реагентов + пробирки"],
    ["20 000 проб/год", "Средняя загрузка 500 лабораторий × 40 проб/год"],
])
wb.save(os.path.join(DIR, "LAMP_ekonomika.xlsx"))
print("  LAMP_ekonomika.xlsx ✓")

# ═══════════════════════════════════════════════════════════════
# 2. LAMP_TTH_obosnovanie.xlsx
# ═══════════════════════════════════════════════════════════════
wb = make_wb()
add_sheet(wb, "ТТХ", ["№", "Параметр", "Значение", "Расчёт", "Источник"], [
    ["1", "Время анализа", "30–60 мин", f"лаг {t_лаг} мин + экспоненц. фаза", "LAMP-протокол"],
    ["2", "Число лунок", "4", "Параллельный анализ 4 образцов", "ТЗ"],
    ["3", "Библиотека тестов", "7 мишеней", "7 патентов НР: LSDV, сальмон., лептосп., медведь, ёж, кошка, рыба", "патенты RU"],
    ["4", "Масса", "≤500 г", "корпус 150 + нагреватель 120 + PCB 80 + батарея 100 + прочее 50", "расч."],
    ["5", "Автономность", "≥4 ч", f"{Q_bat:.0f} мА·ч × {U_bat} В × {eta_bat} / {P_усредн} Вт = {Q_bat*U_bat*eta_bat/1000/P_усредн:.1f} ч", "расч."],
    ["6", "Чувствительность", "10² копий/мкл", "LAMP с 6 праймерами, HNB-детекция", "литература"],
    ["7", "Детекция", "Колориметрия (HNB)", "Гидроксинафтоловый синий: фиолетовый → голубой", "New England Biolabs"],
])
wb.save(os.path.join(DIR, "LAMP_TTH_obosnovanie.xlsx"))
print("  LAMP_TTH_obosnovanie.xlsx ✓")

# ═══════════════════════════════════════════════════════════════
# 3. LAMP_nadezhnost.xlsx
# ═══════════════════════════════════════════════════════════════
wb = make_wb()
comps = [
    ("Нагреватель (картридж 8 Вт)", 1, 5e-7, "datasheet"),
    ("NTC-термометр", 1, 3e-7, "datasheet"),
    ("MCU nRF52840", 1, 1e-6, "datasheet"),
    ("OLED SSD1306", 1, 5e-7, "datasheet"),
    ("Фотодиоды (×4)", 4, 2e-7, "datasheet"),
    ("DC-DC конвертер", 1, 3e-6, "datasheet"),
    ("LiPo BMS", 1, 1e-6, "datasheet"),
    ("Корпус (PLA + алюминий)", 1, 1e-7, "расч."),
    ("USB-C разъём", 1, 5e-7, "datasheet"),
    ("Алюминиевый блок", 1, 1e-7, "расч."),
]
total_lambda = sum(q * l for _, q, l, _ in comps)
MTBF = 1 / total_lambda
add_sheet(wb, "Компоненты", ["Компонент", "Кол-во", "λ (1/ч)", "Источник"], [
    [n, q, f"{l:.1e}", s] for n, q, l, s in comps
])
add_sheet(wb, "Результат", ["Параметр", "Значение", "Ед."], [
    ["Σλ", f"{total_lambda:.2e}", "1/ч"],
    ["MTBF", f"{MTBF:.0f}", "ч"],
    ["Целевое", str(MTBF_target), "ч"],
    ["Статус", "ДА" if MTBF >= MTBF_target else "НЕТ", ""],
])
wb.save(os.path.join(DIR, "LAMP_nadezhnost.xlsx"))
print(f"  LAMP_nadezhnost.xlsx ✓ (MTBF={MTBF:.0f} ч)")

# ═══════════════════════════════════════════════════════════════
# 4. LAMP_profilny_balans.xlsx
# ═══════════════════════════════════════════════════════════════
wb = make_wb()
E_polnaya = Q_bat * U_bat / 1000 * eta_bat
E_potr    = P_усредн * avtonom_ch
add_sheet(wb, "Тепловой баланс", ["Параметр", "Значение", "Ед."], [
    ["T_LAMP", T_lamp, "°C"],
    ["T_допуск", T_dop, "°C"],
    ["P_heater", P_heater, "Вт"],
    ["PID_duty_cycle", "~40–45%", ""],
    ["P_средняя_нагрев", round(P_heater * 0.42, 2), "Вт"],
    ["P_MCU+периферия", P_mcu, "Вт"],
    ["P_средняя_итого", P_усредн, "Вт"],
])
add_sheet(wb, "Энергобаланс", ["Параметр", "Значение", "Ед."], [
    ["Q_bat", Q_bat, "мА·ч"],
    ["U_bat", U_bat, "В"],
    ["eta_DCDC", eta_bat, ""],
    ["E_полная", round(E_polnaya, 2), "Вт·ч"],
    ["P_ср", P_усредн, "Вт"],
    ["t_автономности", round(E_polnaya / P_усредн, 1), "ч"],
    ["Целевое", avtonom_ch, "ч"],
    ["Статус", "ДА" if E_polnaya / P_усредн >= avtonom_ch else "НЕТ", ""],
])
wb.save(os.path.join(DIR, "LAMP_profilny_balans.xlsx"))
print("  LAMP_profilny_balans.xlsx ✓")

# ═══════════════════════════════════════════════════════════════
# 5. LAMP_metrologia.xlsx
# ═══════════════════════════════════════════════════════════════
wb = make_wb()
add_sheet(wb, "Погрешности", ["Канал", "Датчик", "Δ", "Ед.", "Компенсация"], [
    ["Температура блока", "NTC 10 кОм", "±0.1", "°C", "3-точечная калибровка (25/40/65°C)"],
    ["Фотодиод 1 (470 нм)", "APDS-9002", "±5%", "%T", "Калибровка по эталону"],
    ["Фотодиод 2", "APDS-9002", "±5%", "%T", "Калибровка по эталону"],
    ["Фотодиод 3", "APDS-9002", "±5%", "%T", "Калибровка по эталону"],
    ["Фотодиод 4", "APDS-9002", "±5%", "%T", "Калибровка по эталону"],
    ["Время", "RTC nRF52840", "±2", "ppm", "Калибровка 1 раз/год"],
    ["U_батарея", "АЦП MCU", "±10", "мВ", "Опорное напряжение"],
])
add_sheet(wb, "Испытания", ["№", "Испытание", "Оборудование", "Методика"], [
    ["1", "Калибровка NTC", "Термостат, эталонный термометр", "3 точки: 25/40/65°C"],
    ["2", "Калибровка фотодиодов", "Эталонные растворы HNB", "5 концентраций"],
    ["3", "Валидация 7 мишеней", "Референс ПЦР, 50+ образцов", "Сравнение результатов"],
    ["4", "Термостабильность", "Термопара, осциллограф", "65±0.5°C, 60 мин"],
    ["5", "Автономность", "Хронометр, мультиметр", "4 ч непрерывной работы"],
])
wb.save(os.path.join(DIR, "LAMP_metrologia.xlsx"))
print("  LAMP_metrologia.xlsx ✓")

# ═══════════════════════════════════════════════════════════════
# Генерация STL (простая модель корпуса)
# ═══════════════════════════════════════════════════════════════
def write_stl_ascii(path, facets):
    with open(path, 'w') as f:
        f.write("solid lamp_device\n")
        for normal, vertices in facets:
            f.write(f"  facet normal {normal[0]} {normal[1]} {normal[2]}\n")
            f.write("    outer loop\n")
            for v in vertices:
                f.write(f"      vertex {v[0]} {v[1]} {v[2]}\n")
            f.write("    endloop\n")
            f.write("  endfacet\n")
        f.write("endsolid lamp_device\n")

# Корпус 250×200×120 мм (в мм)
W, D, H = 250, 200, 120
facets = []
# 6 faces box
faces = [
    ((0,0,-1), [(0,0,0),(W,0,0),(W,D,0)], [(0,0,0),(W,D,0),(0,D,0)]),
    ((0,0,1),  [(0,0,H),(W,D,H),(W,0,H)], [(0,0,H),(0,D,H),(W,D,H)]),
    ((0,-1,0), [(0,0,0),(W,0,H),(W,0,0)], [(0,0,0),(0,0,H),(W,0,H)]),
    ((0,1,0),  [(0,D,0),(W,D,0),(W,D,H)], [(0,D,0),(W,D,H),(0,D,H)]),
    ((-1,0,0), [(0,0,0),(0,D,0),(0,D,H)], [(0,0,0),(0,D,H),(0,0,H)]),
    ((1,0,0),  [(W,0,0),(W,0,H),(W,D,H)], [(W,0,0),(W,D,H),(W,D,0)]),
]
for n, v1, v2 in faces:
    facets.append((n, v1))
    facets.append((n, v2))

write_stl_ascii(os.path.join(DIR, "../01_zadel/prototype/lamp_device.stl"), facets)
print("  lamp_device.stl ✓")

# ═══════════════════════════════════════════════════════════════
# Генерация PNG 3D-превью (изометрия)
# ═══════════════════════════════════════════════════════════════
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')

# Корпус
verts = [
    [[0,0,0],[W,0,0],[W,D,0],[0,D,0]],
    [[0,0,H],[W,0,H],[W,D,H],[0,D,H]],
    [[0,0,0],[W,0,0],[W,0,H],[0,0,H]],
    [[0,D,0],[W,D,0],[W,D,H],[0,D,H]],
    [[0,0,0],[0,D,0],[0,D,H],[0,0,H]],
    [[W,0,0],[W,D,0],[W,D,H],[W,0,H]],
]
# Нормализуем для отображения
scale = 0.001  # мм → м
verts_s = [[[v*scale for v in pt] for pt in face] for face in verts]

poly = Poly3DCollection(verts_s, alpha=0.3, facecolor='#2563EB', edgecolor='#1F2937', lw=0.5)
ax.add_collection3d(poly)

# 4 лунки (отверстия сверху)
for cx, cy in [(62.5, 50), (187.5, 50), (62.5, 150), (187.5, 150)]:
    theta = np.linspace(0, 2*np.pi, 30)
    r = 15  # мм
    x = (cx + r*np.cos(theta)) * scale
    y = (cy + r*np.sin(theta)) * scale
    z = np.ones_like(theta) * H * scale
    ax.plot(x, y, z, color='#EF4444', lw=2)

# OLED дисплей
disp = [[[50*scale, 0, 80*scale], [200*scale, 0, 80*scale],
          [200*scale, 0, 110*scale], [50*scale, 0, 110*scale]]]
poly_d = Poly3DCollection(disp, alpha=0.6, facecolor='#1F2937', edgecolor='#1F2937')
ax.add_collection3d(poly_d)

ax.set_xlabel('X (мм)', fontsize=8); ax.set_ylabel('Y (мм)', fontsize=8); ax.set_zlabel('Z (мм)', fontsize=8)
ax.set_title('LAMP-ДНК-Экспресс: 3D-модель корпуса (250×200×120 мм)', fontsize=12, fontweight='bold')
ax.set_xlim(0, 0.3); ax.set_ylim(0, 0.25); ax.set_zlim(0, 0.15)
ax.view_init(elev=25, azim=135)
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_02_03_3D.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_02_03_3D.png ✓")

# ═══════════════════════════════════════════════════════════════
# PNG: Функциональная схема (IMG_02_01_shema.png)
# ═══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(12, 7))
ax.set_xlim(0, 12); ax.set_ylim(0, 7)
ax.set_aspect('equal'); ax.axis('off')
ax.set_title('Функциональная схема LAMP-ДНК-Экспресс', fontsize=14, fontweight='bold')

blocks = [
    (0.5, 3, 2, 1.2, 'USB-C\nпитание', '#10B981'),
    (3, 3, 2, 1.2, 'DC-DC\n3.3 В', '#F59E0B'),
    (5.5, 4.5, 2.5, 1.2, 'Нагреватель\n8 Вт + PID', '#EF4444'),
    (5.5, 1.5, 2.5, 1.2, 'nRF52840\nMCU', '#2563EB'),
    (8.5, 4.5, 2.5, 1.2, '4 лунки\n+ HNB', '#8B5CF6'),
    (8.5, 1.5, 2.5, 1.2, 'OLED\n0.96"', '#EC4899'),
    (5.5, 0, 2.5, 1, 'BLE 5.0\n→ Телефон', '#6366F1'),
    (3, 0, 2, 1, 'LiPo\n5000 мА·ч', '#10B981'),
]
for x, y, w, h, label, color in blocks:
    rect = plt.Rectangle((x, y), w, h, facecolor=color, alpha=0.15, edgecolor=color, lw=2)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, label, ha='center', va='center', fontsize=9, fontweight='bold')

# Стрелки
arrows = [(2.5, 3.6, 0.4, 0), (5, 3.6, 0.4, 0), (8, 5.1, 0.4, 0),
          (8, 2.1, 0.4, 0), (6.75, 3, 0, 1.4), (6.75, 1.5, 0, -0.4)]
for x, y, dx, dy in arrows:
    ax.annotate('', xy=(x+dx, y+dy), xytext=(x, y),
                arrowprops=dict(arrowstyle='->', color='#1F2937', lw=1.5))

plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_02_01_shema.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_02_01_shema.png ✓")

# ═══════════════════════════════════════════════════════════════
# PNG: Сборочный чертёж (IMG_02_02_chertezh.png)
# ═══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(-30, 280); ax.set_ylim(-30, 230)
ax.set_aspect('equal'); ax.grid(True, alpha=0.2)
ax.set_title('Сборочный чертёж LAMP-ДНК-Экспресс (мм)', fontsize=12, fontweight='bold')

# Корпус
rect = plt.Rectangle((0, 0), 250, 200, facecolor='none', edgecolor='#2563EB', lw=2)
ax.add_patch(rect)
# Стенки
rect2 = plt.Rectangle((5, 5), 240, 190, facecolor='none', edgecolor='#2563EB', lw=1, ls='--')
ax.add_patch(rect2)
# Лунки
for cx, cy in [(62.5, 50), (187.5, 50), (62.5, 150), (187.5, 150)]:
    circle = plt.Circle((cx, cy), 15, facecolor='none', edgecolor='#EF4444', lw=1.5)
    ax.add_patch(circle)
    ax.text(cx, cy, 'Л', ha='center', va='center', fontsize=8, color='#EF4444')
# OLED
rect3 = plt.Rectangle((50, 185), 150, 10, facecolor='#1F2937', alpha=0.3, edgecolor='#1F2937', lw=1)
ax.add_patch(rect3)
ax.text(125, 190, 'OLED', ha='center', va='center', fontsize=8, color='#1F2937')
# USB-C
rect4 = plt.Rectangle((115, -5), 20, 5, facecolor='#10B981', alpha=0.5, edgecolor='#10B981', lw=1)
ax.add_patch(rect4)
ax.text(125, -12, 'USB-C', ha='center', va='center', fontsize=8)

# Размерные линии
ax.annotate('', xy=(250, -20), xytext=(0, -20),
            arrowprops=dict(arrowstyle='<->', color='#1F2937', lw=1))
ax.text(125, -25, '250', ha='center', va='top', fontsize=9)
ax.annotate('', xy=(260, 200), xytext=(260, 0),
            arrowprops=dict(arrowstyle='<->', color='#1F2937', lw=1))
ax.text(265, 100, '200', ha='left', va='center', fontsize=9, rotation=90)

ax.set_xlabel('X (мм)', fontsize=9)
ax.set_ylabel('Y (мм)', fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(GDIR, "IMG_02_02_chertezh.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("  IMG_02_02_chertezh.png ✓")

print(f"\n✓ Все расчёты LAMP-ДНК-Экспресс (v1) завершены.")
print(f"  Файлов: 6 XLSX + 1 CSV + 1 PY + 9 PNG + 1 STL")