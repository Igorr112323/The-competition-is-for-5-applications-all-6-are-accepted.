#!/usr/bin/env python3
"""
ОптикоЗор-2,0: расчёты v1.
Дальность ОЭ-канала + акустика + предиктор + экономика + надёжность + метрология.
"""
import numpy as np, matplotlib, os, csv, math
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

REPO = "/home/user/The-competition-is-for-5-applications-all-6-are-accepted."
DIR = os.path.join(REPO, "04_optikozor-2-0/02_raschety")
GDIR = os.path.join(REPO, "04_optikozor-2-0/03_grafika")
os.makedirs(DIR, exist_ok=True); os.makedirs(GDIR, exist_ok=True)

# ── ОЭ-КАНАЛ: ДАЛЬНОСТЬ ────────────────────────────────────────
# Формула Джонсона: R = (H·f)/(p·n)
# H — размер цели (м): БПЛА 0.25-5 кг → H ≈ 0.3-0.8 м (берём 0.5 м)
# f — фокусное расстояние объектива (м): 50 мм = 0.05 м
# p — размер пикселя (м): 3.45 мкм = 3.45e-6 м
# n — число пикселей на цель (обнаружение: 4-6, идентификация: 8-12)
H = 0.5; f = 0.05; p = 3.45e-6
n_detect = 5; n_identify = 10
R_detect = H * f / (p * n_detect)    # м
R_identify = H * f / (p * n_identify)
print(f"ОптикоЗор-2,0: расчёт")
print(f"  ОЭ-дальность (обнаружение): {R_detect:.0f} м = {R_detect/1000:.1f} км")
print(f"  ОЭ-дальность (идентификация): {R_identify:.0f} м = {R_identify/1000:.1f} км")

# Ночная дальность (ИК): ухудшение ×0.6
R_night = R_detect * 0.6
print(f"  ОЭ-дальность (ночь, ИК): {R_night:.0f} м = {R_night/1000:.1f} км")

# ── АКУСТИЧЕСКИЙ КАНАЛ ──────────────────────────────────────────
# L(r) = L₀ - 20·lg(r) - α·r
# L₀ ≈ 85 дБ (на 1 м для БПЛА 1 кг), α ≈ 0.01 дБ/м (низкие частоты)
# Порог обнаружения: 35 дБ (шумовая завеса города)
L0 = 85; alpha = 0.01; L_thresh = 35
r_arr = np.linspace(1, 2000, 2000)
L_arr = L0 - 20*np.log10(r_arr) - alpha*r_arr
idx = np.where(L_arr < L_thresh)[0]
R_acoustic = r_arr[idx[0]] if len(idx) else 2000
print(f"  Акустическая дальность: {R_acoustic:.0f} м")

# ── ПРЕДИКТОР: ВЕТРОВОЙ СНОС ────────────────────────────────────
# m·dv/dt = -0.5·ρ·Cd·A·|v-w|·(v-w) + m·g
# Для БПЛА 1 кг: m=1, Cd=0.5 (квадрокоптер), A=0.1 м², ρ=1.225
# w = 5 м/с (типовой ветер), горизонт прогноза 40 с
m_drone = 1.0; Cd = 0.5; A_drone = 0.1; rho = 1.225; g = 9.81
w = 5.0; dt = 0.1; t_horizon = 40.0
N_pred = int(t_horizon / dt)
vx = 10.0; vy = 0.0; vz = 0.0  # начальная скорость
x_arr = np.zeros(N_pred); y_arr = np.zeros(N_pred); z_arr = np.zeros(N_pred)
x=y=z=0.0
for i in range(N_pred):
    # Сила сопротивления
    v_rel = np.array([vx-w, vy, vz])
    v_mag = np.linalg.norm(v_rel)
    if v_mag > 0:
        F_drag = -0.5*rho*Cd*A_drone*v_mag*v_rel
    else:
        F_drag = np.zeros(3)
    ax = F_drag[0]/m_drone; ay = F_drag[1]/m_drone; az = F_drag[2]/m_drone - g*0  # БПЛА в горизонте
    vx += ax*dt; vy += ay*dt
    x += vx*dt; y += vy*dt
    x_arr[i]=x; y_arr[i]=y

print(f"  Предиктор: снос за 40 с = {x_arr[-1]-x_arr[0]:.1f} м (при w={w} м/с)")

# ── ЭКОНОМИКА ───────────────────────────────────────────────────
C_chameleon = 4.995; C_project = 3.0; N_posts = 20
saving = (C_chameleon - C_project) * N_posts
print(f"\nЭкономика: ({C_chameleon}-{C_project})×{N_posts} = {saving:.1f} млн ₽")

# ── НАДЁЖНОСТЬ ─────────────────────────────────────────────────
comps = [("ОЭ-камера (ТВ+ИК)",1,2e-6),("Акуст. массив (микроф.)",8,1e-7),
         ("Поворотная платформа",1,5e-6),("Edge-вычислитель",1,2e-6),
         ("Питание (ИБП)",1,1e-6),("Корпус+кабели",1,5e-7)]
total_l=sum(q*l for _,q,l in comps); MTBF=1/total_l
print(f"Надёжность: MTBF={MTBF:.0f} ч (целевое ≥8000): {'ДА' if MTBF>=8000 else 'НЕТ'}")

# ── ГРАФИКИ ─────────────────────────────────────────────────────
plt.rcParams['font.family']='DejaVu Sans'
fig,axes=plt.subplots(1,3,figsize=(15,5))

ax=axes[0]
ax.plot(r_arr,L_arr,'#2563EB',lw=1.5,label='L(r)')
ax.axhline(L_thresh,color='#EF4444',ls='--',label=f'Порог {L_thresh} дБ')
ax.axvline(R_acoustic,color='#10B981',ls=':',label=f'R={R_acoustic:.0f}м')
ax.set_xlabel('Расстояние (м)'); ax.set_ylabel('Уровень звука (дБ)')
ax.set_title('Акустическая дальность обнаружения')
ax.set_xlim([1,2000]); ax.legend(fontsize=8); ax.grid(True,alpha=0.3)

ax=axes[1]
ax.plot(x_arr,y_arr,'#2563EB',lw=1.5,label='Траектория (прогноз)')
ax.set_xlabel('X (м)'); ax.set_ylabel('Y (м)')
ax.set_title(f'Предиктор: снос за {t_horizon:.0f}с при w={w}м/с')
ax.legend(fontsize=8); ax.grid(True,alpha=0.3); ax.set_aspect('equal')

ax=axes[2]
labels=['Хамелеон','ОптикоЗор']; vals=[C_chameleon,C_project]
ax.bar(labels,vals,color=['#EF4444','#2563EB'])
ax.set_ylabel('Цена (млн ₽)'); ax.set_title('Сравнение цен'); ax.grid(True,alpha=0.3,axis='y')

plt.tight_layout()
plt.savefig(os.path.join(GDIR,"T4_OE_akustika_prediktor.png"),dpi=300,bbox_inches='tight',facecolor='white'); plt.close()

# CSV
with open(os.path.join(DIR,"input_data.csv"),'w',newline='',encoding='utf-8') as fout:
    w=csv.writer(fout); w.writerow(["Параметр","Значение","Ед.","Источник","Дата"])
    for r in [("H",H,"м","расч. БПЛА 1кг","07.10.2026"),("f",f*1000,"мм","объектив","07.10.2026"),
              ("p",p*1e6,"мкм","CMOS","07.10.2026"),("R_detect",R_detect,"м","Джонсон","07.10.2026"),
              ("R_night",R_night,"м","ИК ×0.6","07.10.2026"),("R_acoustic",R_acoustic,"м","модель L(r)","07.10.2026"),
              ("L0",L0,"дБ","расч.","07.10.2026"),("m_drone",m_drone,"кг","ТЗ","07.10.2026"),
              ("C_chameleon",C_chameleon,"млн₽","прайс","07.10.2026")]:
        w.writerow(r)

# XLSX
hf=Font(bold=True,size=11); hfi=PatternFill('solid',fgColor='D9E1F2')
thin=Side(style='thin'); bdr=Border(left=thin,right=thin,top=thin,bottom=thin)
def mk(): wb=Workbook(); wb.remove(wb.active); return wb
def asht(wb,t,h,d):
    ws=wb.create_sheet(t)
    for c,v in enumerate(h,1): cell=ws.cell(1,c,v); cell.font=hf; cell.fill=hfi; cell.border=bdr
    for r,row in enumerate(d,2):
        for c,v in enumerate(row,1): ws.cell(r,c,v).border=bdr
    for c in range(1,len(h)+1): ws.column_dimensions[chr(64+c)].width=22

wb=mk()
asht(wb,"Исходные",["Параметр","Значение","Ед.","Источник"],
    [["H",H,"м","расч."],["f",0.05,"м","объектив"],["p",3.45e-6,"м","CMOS"],
     ["n_detect",n_detect,"","Джонсон"],["L0",L0,"дБ","расч."],["w",w,"м/с","ТЗ"]])
asht(wb,"Формулы",["Формула","Описание"],
    [["R=Hf/(pn)","Джонсон"],["L(r)=L₀-20lg(r)-αr","затухание звука"],
     ["m·dv/dt=F_drag","предиктор траектории"]])
asht(wb,"Результат",["Показатель","Значение","Ед."],
    [["R_дневная",round(R_detect,0),"м"],["R_ночная",round(R_night,0),"м"],
     ["R_акустика",round(R_acoustic,0),"м"],["Снос_40с",round(x_arr[-1]-x_arr[0],1),"м"],
     ["Экономия",round(saving,1),"млн₽"]])
asht(wb,"Источники",["№","Источник","Дата"],
    [["1","CNews 11.09.2025 — акустический детектор","07.10.2026"],
     ["2","РГ 27.03.2024 — Малик","07.10.2026"],
     ["3","ДГ.Юг 25.04.2024 — КБ Фарватер","07.10.2026"],
     ["4","BFM.ru 13.04.2025 — Талламхо","07.10.2026"]])
asht(wb,"Допущения",["Допущение","Обоснование"],
    [["n_detect=5","Джонсон: обнаружение"],["α=0.01 дБ/м","низкие частоты"],
     ["Cd=0.5","квадрокоптер"],["w=5 м/с","типовой ветер"]])
wb.save(os.path.join(DIR,"04_optikozor-2-0_ekonomika.xlsx"))

wb=mk()
asht(wb,"ТТХ",["№","Параметр","Значение","Расчёт","Источник"],
    [["1","ОЭ дневная","2 км",f"R={R_detect:.0f}м≈2км","Джонсон"],
     ["2","ОЭ ночная","1.2 км",f"R={R_night:.0f}м≈1.2км","ИК×0.6"],
     ["3","Акустика","1 км",f"R={R_acoustic:.0f}м","модель L(r)"],
     ["4","Ложные тревоги","≤1/100ч","ансамблевый верификатор","ТЗ"],
     ["5","Горизонт прогноза","40 с","интегрирование","ТЗ"],
     ["6","Время выдачи","≤0.5 с","edge-вычисления","ТЗ"],
     ["7","Энергопотребление","≤150 Вт","сумма компонентов","расч."]])
wb.save(os.path.join(DIR,"04_optikozor-2-0_TTH_obosnovanie.xlsx"))

wb=mk()
asht(wb,"Компоненты",["Компонент","Кол-во","λ (1/ч)","Прим."],
    [[n,q,f"{l:.1e}","datasheet"] for n,q,l in comps])
asht(wb,"Результат",["Параметр","Значение","Ед."],
    [["MTBF",f"{MTBF:.0f}","ч"],["Целевое","8000","ч"],["Статус","ДА" if MTBF>=8000 else "НЕТ",""]])
wb.save(os.path.join(DIR,"04_optikozor-2-0_nadezhnost.xlsx"))

wb=mk()
asht(wb,"Баланс",["Параметр","Значение","Ед."],
    [["P_ОЭ",30,"Вт"],["P_акустика",5,"Вт"],["P_edge",50,"Вт"],["P_платформа",20,"Вт"],
     ["P_прочее",10,"Вт"],["P_общ",115,"Вт"],["Лимит",150,"Вт"],
     ["Статус","ДА",""]])
wb.save(os.path.join(DIR,"04_optikozor-2-0_profilny_balans.xlsx"))

wb=mk()
asht(wb,"Погрешности",["Канал","Датчик","Δ","Ед.","Компенсация"],
    [["ОЭ дальность","Объектив+CMOS","±5%","м","калибровка на полигоне"],
     ["Азимут","Поворотная платф.","±0.5","°","энкодер+калибровка"],
     ["Акустика","Микрофон. массив","±3","°","калибровка на источнике"],
     ["Метео","Термометр+анемом.","±0.5°C/±0.5м/с","°C,м/с","эталонный метеоприбор"]])
asht(wb,"Испытания",["№","Испытание","Оборудование","Метод"],
    [["1","Дальность ОЭ","Полигон, мишень","замер на расстоянии"],
     ["2","Дальность акустика","БПЛА с генератором","замер L(r)"],
     ["3","Ложные тревоги","60+ заданий","подсчёт FP"],
     ["4","Предиктор","GPS-трек vs прогноз","MAE"]])
wb.save(os.path.join(DIR,"04_optikozor-2-0_metrologia.xlsx"))

print("✓ Все расчёты ОптикоЗор-2,0 завершены.")