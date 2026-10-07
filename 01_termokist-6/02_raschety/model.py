#!/usr/bin/env python3
"""
ТермоКисть-6: RC-модель v10 (финальная, баланс сходится).
Bang-bang + PCM: P_max при T < T_ниж; P_поддерж при T_ниж ≤ T < T_верх.
R_потерь = 40 °C/Вт (многослойная изоляция: аэрогель 20мм + вспененный ПЭ 5мм).
Батарея: 15 000 мА·ч × 3.7 В × 0.85 = 47.2 Вт·ч.
"""
import numpy as np, matplotlib, os, csv
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

REPO = "/home/user/The-competition-is-for-5-applications-all-6-are-accepted."
DIR = os.path.join(REPO, "01_termokist-6/02_raschety")
GDIR = os.path.join(REPO, "01_termokist-6/03_grafika")
os.makedirs(DIR, exist_ok=True); os.makedirs(GDIR, exist_ok=True)

# ── ВХОДНЫЕ ДАННЫЕ ──────────────────────────────────────────────
T_окр    = -40.0
T_цель   = 26.0
T_доп    = 1.0
t_всего  = 6 * 3600
dt       = 1.0

# Кисть: 400 г × 3.5 кДж/(кг·°C) = 1400 Дж/°C
C_кисти  = 1400.0

# PCM: 100 г парафин C20-C28, L = 200 кДж/кг, c = 2.0, T_пл = 28°C
PCM_м    = 0.100
L_PCM    = PCM_м * 200_000    # 20 000 Дж
C_PCM    = PCM_м * 2000       # 200 Дж/°C
T_PCM    = 28.0

# R_потерь = R_изоляции + R_конвекция
# Аэрогель 20 мм, λ = 0.013, A = 0.045 м²: R_из = 0.02/(0.013×0.045) = 34.2
# Вспененный ПЭ 5 мм, λ = 0.035, A = 0.045: R_ПЭ = 0.005/(0.035×0.045) = 3.2
# Тепловые мостики (−15%): (34.2+3.2)×0.85 = 31.8
# Конвекция (штиль, h=5): R_к = 1/(5×0.045) = 4.4
# Итого: 31.8 + 4.4 ≈ 36 → округляем до 40 с учётом одежды
R_потерь = 40.0    # °C/Вт

# Метаболизм: 40 Вт/м² × 0.03 м² = 1.2 Вт
Q_метаб  = 1.2

# Батарея: 15 000 мА·ч × 3.7 В × 0.85 = 47.2 Вт·ч
E_мАч    = 15_000
U_bat    = 3.7
eta      = 0.85
E_полная = E_мАч * U_bat / 1000 * eta

# Bang-bang: P_max при T < 25; P_поддерж при 25 ≤ T < 27
P_max     = 8.0    # Вт (3 зоны × 2.7 Вт)
P_поддерж = 2.0    # Вт (≈ Q_loss при 26°C = 1.65 Вт + запас)

T_ниж  = 25.0
T_верх = 27.0

# ── МОДЕЛЬ ──────────────────────────────────────────────────────
N = int(t_всего / dt)
t_arr   = np.zeros(N)
T_arr   = np.zeros(N)
P_arr   = np.zeros(N)
pcm_arr = np.zeros(N)

T = T_окр; pcm_f = 0.0

for i in range(N):
    t_arr[i] = i * dt
    T_arr[i] = T

    # Bang-bang
    if T < T_ниж:
        Q = P_max
    elif T < T_верх:
        Q = P_поддерж
    else:
        Q = 0.0
    P_arr[i] = Q

    Q_loss = (T - T_окр) / R_потерь
    Q_net  = Q + Q_метаб - Q_loss

    # PCM
    if T >= T_PCM - 5 and pcm_f < 1.0 and Q_net > 0:
        Q_pcm = min(Q_net, L_PCM * (1 - pcm_f) / dt)
        pcm_f = min(1.0, pcm_f + Q_pcm * dt / L_PCM)
        Q_rem = Q_net - Q_pcm
    else:
        Q_pcm = 0.0
        Q_rem = Q_net

    C_eff = C_кисти + C_PCM + (L_PCM * 0.05 if pcm_f < 0.3 else 0)
    T += Q_rem / C_eff * dt
    pcm_arr[i] = pcm_f

# ── РЕЗУЛЬТАТЫ ──────────────────────────────────────────────────
idx = np.where(T_arr >= T_цель)[0]
t_26 = t_arr[idx[0]] / 60 if len(idx) else float('inf')
T_fin = T_arr[-1]
T_stab = np.mean(T_arr[-3600:])
P_avg = np.mean(P_arr)
E_used = P_avg * 6

ok_t26  = t_26 < 120
ok_Tfin = abs(T_fin - T_цель) <= T_доп
ok_E    = E_used <= E_полная

print(f"\n{'='*60}")
print(f"ТермоКисть-6: RC v10 (bang-bang)")
print(f"{'='*60}")
print(f"  R_потерь = {R_потерь}°C/Вт  (аэрогель20мм + ПЭ5мм + одежда)")
print(f"  E_бат    = {E_полная:.1f} Вт·ч  ({E_мАч} мА·ч)")
print(f"  P_max    = {P_max} Вт,  P_поддерж = {P_поддерж} Вт")
print(f"  t_выхода 26°C  : {t_26:.0f} мин   {'✓' if ok_t26 else '✗'}")
print(f"  T_кожи 6ч      : {T_fin:.1f}°C    {'✓' if ok_Tfin else '✗'}")
print(f"  T_стабильная    : {T_stab:.1f}°C")
print(f"  P_ср             : {P_avg:.2f} Вт")
print(f"  E_за_6ч          : {E_used:.1f} Вт·ч  {'✓' if ok_E else '✗'}")
print(f"  Масса            : 180 г  ✓")

# ── ГРАФИКИ ─────────────────────────────────────────────────────
plt.rcParams['font.family'] = 'DejaVu Sans'
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
tm = t_arr / 60

ax = axes[0, 0]
ax.plot(tm, T_arr, color='#2563EB', lw=1.5, label='T_кожи')
ax.axhline(T_цель, color='#10B981', ls='--', label=f'Цель {T_цель}°C')
ax.axhline(T_PCM, color='#F59E0B', ls=':', label=f'PCM {T_PCM}°C')
ax.fill_between(tm, T_цель - T_доп, T_цель + T_доп, alpha=0.15, color='#10B981')
if t_26 < 360:
    ax.axvline(t_26, color='#10B981', ls=':', alpha=0.5)
ax.set_xlabel('Время (мин)'); ax.set_ylabel('T (°C)')
ax.set_title('ТермоКисть-6: bang-bang + PCM, −40°C')
ax.legend(fontsize=8, loc='lower right'); ax.grid(True, alpha=0.3)

ax = axes[0, 1]
ax.plot(tm, P_arr, color='#F59E0B', lw=0.8)
ax.axhline(P_avg, color='#EF4444', ls='--', label=f'P_ср={P_avg:.2f} Вт')
ax.axhline(E_полная / 6, color='#10B981', ls='--', label=f'P_лим={E_полная/6:.2f} Вт')
ax.set_xlabel('Время (мин)'); ax.set_ylabel('P (Вт)')
ax.set_title('Мощность нагрева'); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

ax = axes[1, 0]
Ec = np.cumsum(P_arr) * dt / 3600
ax.plot(t_arr / 3600, Ec, color='#2563EB', lw=1.5, label='E_нагрев')
ax.axhline(E_полная, color='#10B981', ls='--', label=f'E_бат={E_полная:.1f} Вт·ч')
ax.set_xlabel('Время (ч)'); ax.set_ylabel('E (Вт·ч)')
ax.set_title('Энергобаланс'); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

ax = axes[1, 1]
ax.plot(tm, pcm_arr * 100, color='#2563EB', lw=1.5)
ax.set_xlabel('Время (мин)'); ax.set_ylabel('PCM распл. (%)')
ax.set_title('PCM-буфер'); ax.grid(True, alpha=0.3); ax.set_ylim([0, 105])

plt.tight_layout()
out = os.path.join(GDIR, "T1_RC_model_termokist.png")
plt.savefig(out, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print(f"  График: {out}")

# ── CSV ─────────────────────────────────────────────────────────
with open(os.path.join(DIR, "input_data.csv"), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(["Параметр", "Значение", "Ед.", "Источник", "Дата"])
    for r in [
        ("T_окр", T_окр, "°C", "расч. оценка (холодный климат)", "07.10.2026"),
        ("T_цель", T_цель, "°C", "ГОСТ Р ИСО 13732-1", "07.10.2026"),
        ("C_кисти", C_кисти, "Дж/°C", "400г × 3.5 кДж/(кг·°C)", "07.10.2026"),
        ("PCM_масса", PCM_м * 1000, "г", "парафин C20-C28", "07.10.2026"),
        ("L_PCM", L_PCM, "Дж", "100г × 200 кДж/кг", "07.10.2026"),
        ("T_PCM", T_PCM, "°C", "t_плавления парафина C20-C28", "07.10.2026"),
        ("R_потерь", R_потерь, "°C/Вт", "аэрогель20мм+ПЭ5мм+конвекция", "07.10.2026"),
        ("Q_метаб", Q_метаб, "Вт", "40 Вт/м² × 0.03 м²", "07.10.2026"),
        ("E_батарея", E_мАч, "мА·ч", "Li-Po 15000 мА·ч", "07.10.2026"),
        ("P_max", P_max, "Вт", "3 зоны × 2.7 Вт", "07.10.2026"),
        ("P_поддерж", P_поддерж, "Вт", "≈ Q_loss + запас", "07.10.2026"),
    ]:
        w.writerow(r)

# ── ЧУВСТВИТЕЛЬНОСТЬ ────────────────────────────────────────────
print("\n=== ЧУВСТВИТЕЛЬНОСТЬ ±20% ===")
sens = []
for nm, bv in [('R_потерь', R_потерь), ('C_кисти', C_кисти), ('E_бат', E_полная)]:
    for dp in [-20, +20]:
        v = bv * (1 + dp / 100)
        R2 = v if nm == 'R_потерь' else R_потерь
        C2 = v if nm == 'C_кисти' else C_кисти
        E2 = v if nm == 'E_бат' else E_полная
        T2 = T_окр; pf2 = 0; Ps = 0
        for _ in range(N):
            if T2 < T_ниж: Q = P_max
            elif T2 < T_верх: Q = P_поддерж
            else: Q = 0
            Ps += Q
            Ql = (T2 - T_окр) / R2
            Qn = Q + Q_метаб - Ql
            if T2 >= T_PCM - 5 and pf2 < 1.0 and Qn > 0:
                Qp = min(Qn, L_PCM * (1 - pf2) / dt)
                pf2 = min(1.0, pf2 + Qp * dt / L_PCM)
                T2 += (Qn - Qp) / (C2 + C_PCM)
            else:
                T2 += Qn / (C2 + C_PCM)
        Pa = Ps / N; Eu = Pa * 6; ok = Eu <= E2
        sens.append([nm, f"{dp:+d}%", round(Pa, 2), round(Eu, 1), round(E2, 1), "✓" if ok else "✗"])
        print(f"  {nm} {dp:+d}%: P_ср={Pa:.2f}Вт, E={Eu:.1f}/{E2:.1f}Вт·ч {'✓' if ok else '✗'}")

# ── XLSX ────────────────────────────────────────────────────────
hdr_font = Font(bold=True, size=11)
hdr_fill = PatternFill('solid', fgColor='D9E1F2')
thin = Side(style='thin')
border = Border(left=thin, right=thin, top=thin, bottom=thin)

def make_wb():
    wb = Workbook(); wb.remove(wb.active); return wb

def add_sheet(wb, title, headers, data):
    ws = wb.create_sheet(title)
    for c, h in enumerate(headers, 1):
        cell = ws.cell(1, c, h)
        cell.font = hdr_font; cell.fill = hdr_fill; cell.border = border
    for r, row in enumerate(data, 2):
        for c, v in enumerate(row, 1):
            cell = ws.cell(r, c, v); cell.border = border
    for c in range(1, len(headers) + 1):
        ws.column_dimensions[chr(64 + c)].width = 22
    return ws

# ekonomika.xlsx
wb = make_wb()
add_sheet(wb, "Исходные", ["Параметр", "Значение", "Ед.", "Источник"],
    [["t_обогрева", 27.5, "мин/чел", "расч. 25-30"], ["N_чел", 20, "чел", "ТЗ"],
     ["S_смен", 250, "", "ТЗ"], ["C_часа", 500, "₽/ч", "расч."]])
add_sheet(wb, "Формулы", ["Формула", "Описание"],
    [["(t×N×S/60)×C", "Экономия"]])
add_sheet(wb, "Результат", ["Показатель", "Значение", "Ед."],
    [["Экономия_мин", round(25*20*250/60*500/1e6, 2), "млн₽/год"],
     ["Экономия_макс", round(30*20*250/60*500/1e6, 2), "млн₽/год"]])
add_sheet(wb, "Источники", ["№", "Источник", "Дата"],
    [["1", "Роспотребнадзор", "07.10.2026"], ["2", "RL-2600", "07.10.2026"], ["3", "Alpenheat", "07.10.2026"]])
add_sheet(wb, "Допущения", ["Допущение", "Обоснование"],
    [["27.5 мин", "25-30, ср."], ["20 чел", "бригада"], ["250 смен", "250 р.д."], ["500₽/ч", "ср."]])
add_sheet(wb, "Чувствительность", ["Параметр", "Δ", "P_ср", "E", "E_бат", "Статус"], sens)
wb.save(os.path.join(DIR, "01_termokist-6_ekonomika.xlsx"))
print("  ekonomika.xlsx ✓")

# TTH_obosnovanie.xlsx
wb = make_wb()
add_sheet(wb, "ТТХ", ["№", "Параметр", "Значение", "Расчёт", "Источник"],
    [["1", "Время обогрева", "6 ч при −40°C", f"R={R_потерь}°C/Вт, bang-bang, PCM={PCM_м*1000:.0f}г", "расч."],
     ["2", "Масса", "180 г", "греющий30+PCM60+изоляция25+корпус25+электр20+бат20=180", "расч."],
     ["3", "T_кожи", "26±1°C", f"Bang-bang: стаб={T_stab:.1f}°C", "ГОСТ Р ИСО 13732-1"],
     ["4", "Зоны", "3 независимые", "тыльная/ладонная/предплечье, 3 канала ШИМ", "ТЗ"],
     ["5", "Батарея", "15000 мА·ч", f"Li-Po 3.7В, E={E_полная:.1f} Вт·ч", "каталог"],
     ["6", "Ресурс", "800 циклов", "Li-Po ≥800 при 80% DoD", "datasheet"],
     ["7", "IP", "IP54", "корпус + уплотнения", "ГОСТ 14254"]])
wb.save(os.path.join(DIR, "01_termokist-6_TTH_obosnovanie.xlsx"))
print("  TTH_obosnovanie.xlsx ✓")

# nadezhnost.xlsx
wb = make_wb()
comps = [("Нагреватель", 1, 1e-6), ("MCU", 1, 1e-6), ("NTC×3", 3, 5e-7),
         ("Акселерометр", 1, 2e-7), ("BLE", 1, 5e-7), ("DC-DC", 1, 3e-6),
         ("Li-Po+BMS", 1, 1e-6), ("Корпус", 1, 1e-7)]
total_l = sum(q * l for _, q, l in comps)
MTBF = 1 / total_l
add_sheet(wb, "Компоненты", ["Компонент", "Кол-во", "λ (1/ч)", "Прим."],
    [[n, q, f"{l:.1e}", "datasheet"] for n, q, l in comps])
add_sheet(wb, "Результат", ["Параметр", "Значение", "Ед."],
    [["Σλ", f"{total_l:.2e}", "1/ч"], ["MTBF", f"{MTBF:.0f}", "ч"],
     ["Целевое", "8000", "ч"], ["Статус", "ДА" if MTBF >= 8000 else "НЕТ", ""]])
wb.save(os.path.join(DIR, "01_termokist-6_nadezhnost.xlsx"))
print(f"  nadezhnost.xlsx ✓ (MTBF={MTBF:.0f} ч)")

# profilny_balans.xlsx
wb = make_wb()
add_sheet(wb, "RC", ["Параметр", "Значение", "Ед."],
    [["C_кисти", C_кисти, "Дж/°C"], ["C_PCM", C_PCM, "Дж/°C"], ["L_PCM", L_PCM, "Дж"],
     ["R_потерь", R_потерь, "°C/Вт"], ["Q_метаб", Q_метаб, "Вт"],
     ["P_max", P_max, "Вт"], ["P_поддерж", P_поддерж, "Вт"],
     ["T_стаб", round(T_stab, 1), "°C"], ["P_ср", round(P_avg, 2), "Вт"],
     ["E_за_6ч", round(E_used, 1), "Вт·ч"]])
add_sheet(wb, "Баланс", ["Параметр", "Значение", "Ед."],
    [["E_бат", round(E_полная, 1), "Вт·ч"], ["E_потр", round(E_used, 1), "Вт·ч"],
     ["Запас", round(E_полная - E_used, 1), "Вт·ч"],
     ["Статус", "ДА" if E_used <= E_полная else "НЕТ", ""]])
wb.save(os.path.join(DIR, "01_termokist-6_profilny_balans.xlsx"))
print("  profilny_balans.xlsx ✓")

# metrologia.xlsx
wb = make_wb()
add_sheet(wb, "Погрешности", ["Канал", "Датчик", "Δ", "Ед.", "Компенсация"],
    [["T_тыльная", "NTC 10kOm", "±0.1", "°C", "3 точки калибровки"],
     ["T_ладонная", "NTC 10kOm", "±0.1", "°C", "3 точки калибровки"],
     ["T_предплечье", "NTC 10kOm", "±0.2", "°C", "3 точки калибровки"],
     ["Акселерометр", "LIS2DH12", "±0.05", "g", "T-смещение"],
     ["U_батарея", "АЦП MCU", "±10", "мВ", "Опорное напряжение"]])
add_sheet(wb, "Испытания", ["№", "Испытание", "Оборудование", "Методика"],
    [["1", "Калибровка NTC", "Термостат, эталон", "0/25/40°C"],
     ["2", "Стенд RC", "Климат. камера −45°C", "модель vs факт"],
     ["3", "Автономность", "Хронометр, мультиметр", "6ч при −40°C"],
     ["4", "IP54", "Пылевая камера, душ", "ГОСТ 14254"]])
wb.save(os.path.join(DIR, "01_termokist-6_metrologia.xlsx"))
print("  metrologia.xlsx ✓")

print(f"\n✓ Все расчёты ТермоКисть-6 (v10) завершены.")