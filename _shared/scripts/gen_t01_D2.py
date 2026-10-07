#!/usr/bin/env python3
"""
ТермоКисть-6: Д+2 — 3D-модель, чертежи, электрическая схема, BOM, спецификация.
"""
import os, sys, math, struct, numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import ezdxf
from ezdxf.addons.drawing import matplotlib as ezdxf_mpl
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

REPO = "/home/user/The-competition-is-for-5-applications-all-6-are-accepted."
PROTO = os.path.join(REPO, "01_termokist-6/01_zadel/prototype")
GRAF  = os.path.join(REPO, "01_termokist-6/03_grafika")
os.makedirs(PROTO, exist_ok=True); os.makedirs(GRAF, exist_ok=True)

# ── ПАРАМЕТРЫ ИЗДЕЛИЯ (из ТТХ) ──────────────────────────────────
L_main  = 220   # мм, длина накладки (кисть+предплечье)
W_main  = 110   # мм, ширина
H_main  = 30    # мм, высота (греющий+PCM+изоляция+корпус)
L_bat   = 70    # мм, батарейный отсек
W_bat   = 50
H_bat   = 20
t_wall  = 2.0   # мм, толщина стенки корпуса
t_heat  = 1.0   # мм, греющий слой
t_pcm   = 5.0   # мм, слой PCM (100 г парафина)
t_aero  = 3.0   # мм, аэрогелевая изоляция
t_insul = 2.0   # мм, вспененный ПЭ

# ── 3D-МОДЕЛЬ (trimesh) ─────────────────────────────────────────
def make_box(lox, loy, loz, size, color=None):
    """Создаёт параллелепипед с нижним углом в (lox, loy, loz)"""
    sx, sy, sz = size
    vertices = np.array([
        [lox, loy, loz], [lox+sx, loy, loz], [lox+sx, loy+sy, loz], [lox, loy+sy, loz],
        [lox, loy, loz+sz], [lox+sx, loy, loz+sz], [lox+sx, loy+sy, loz+sz], [lox, loy+sy, loz+sz]
    ])
    faces = np.array([
        [0,1,2],[0,2,3],[4,5,6],[4,6,7],[0,1,5],[0,5,4],
        [2,3,7],[2,7,6],[0,3,7],[0,7,4],[1,2,6],[1,6,5]
    ])
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    if color: mesh.visual.face_colors = color
    return mesh

# Корпус нижний
corpus = make_box(0, 0, 0, [L_main, W_main, t_wall], color=[80, 80, 80, 255])
# Изоляция ПЭ
insul_pe = make_box(t_wall, t_wall, t_wall, [L_main-2*t_wall, W_main-2*t_wall, t_insul], color=[200, 200, 200, 255])
# Аэрогель
aerogel = make_box(t_wall, t_wall, t_wall+t_insul, [L_main-2*t_wall, W_main-2*t_wall, t_aero], color=[180, 220, 255, 255])
# PCM слой
pcm_layer = make_box(t_wall, t_wall, t_wall+t_insul+t_aero, [L_main-2*t_wall, W_main-2*t_wall, t_pcm], color=[255, 200, 100, 255])
# Греющий слой (3 зоны)
z_h = t_wall + t_insul + t_aero + t_pcm
z_len = (L_main - 2*t_wall) / 3
for i in range(3):
    colors = [[255, 50, 50, 255], [255, 100, 50, 255], [255, 150, 50, 255]]
    heat = make_box(t_wall + i*z_len, t_wall, z_h, [z_len, W_main-2*t_wall, t_heat], color=colors[i])
    if i == 0: heats = heat
    else: heats = trimesh.util.concatenate(heats, heat)
# Корпус верхний
corpus_top = make_box(0, 0, z_h+t_heat, [L_main, W_main, t_wall], color=[80, 80, 80, 255])
# Батарейный отсек
bat_x = (L_main - L_bat) / 2
bat_off = make_box(bat_x, (W_main-W_bat)/2, -H_bat, [L_bat, W_bat, H_bat], color=[60, 60, 60, 255])

scene = trimesh.Scene([corpus, insul_pe, aerogel, pcm_layer, heats, corpus_top, bat_off])
stl_path = os.path.join(PROTO, "model3d.stl")
scene.export(stl_path)
print(f"  STL: {stl_path} ({os.path.getsize(stl_path)} байт)")

# Preview PNG
try:
    # matplotlib 3D preview
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    for mesh, c in [(corpus, '#404040'), (insul_pe, '#C8C8C8'), (aerogel, '#B4DCFF'),
                    (pcm_layer, '#FFC864'), (corpus_top, '#404040'), (bat_off, '#303030')]:
        verts = mesh.vertices; faces = mesh.faces
        pc = Poly3DCollection(verts[faces], alpha=0.7, facecolor=c, edgecolor='#333333', linewidth=0.3)
        ax.add_collection3d(pc)
    # Зоны нагрева
    for mesh_i in [heats]:
        verts = mesh_i.vertices; faces = mesh_i.faces
        pc = Poly3DCollection(verts[faces], alpha=0.8, facecolor='#FF3232', edgecolor='#CC0000', linewidth=0.3)
        ax.add_collection3d(pc)
    
    ax.set_xlabel('X (мм)'); ax.set_ylabel('Y (мм)'); ax.set_zlabel('Z (мм)')
    ax.set_title('ТермоКисть-6: 3D-модель (изометрия)', fontsize=12)
    # Auto-scale
    all_verts = np.vstack([m.vertices for m in [corpus, insul_pe, aerogel, pcm_layer, heats, corpus_top, bat_off]])
    max_range = (all_verts.max(axis=0) - all_verts.min(axis=0)).max() / 2
    mid = all_verts.mean(axis=0)
    ax.set_xlim(mid[0]-max_range, mid[0]+max_range)
    ax.set_ylim(mid[1]-max_range, mid[1]+max_range)
    ax.set_zlim(mid[2]-max_range, mid[2]+max_range)
    ax.view_init(elev=25, azim=135)
    plt.tight_layout()
    plt.savefig(os.path.join(PROTO, "model3d_preview.png"), dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("  Preview PNG ✓")
except Exception as ex:
    print(f"  Preview PNG: ошибка ({ex})")

# ── ЧЕРТЁЖИ (ezdxf) ─────────────────────────────────────────────
def add_gost_frame(msp, w=420, h=297):
    """Рамка ГОСТ 2.104 формат А3"""
    msp.add_line((0,0),(w,0))  # внешняя рамка
    msp.add_line((w,0),(w,h))
    msp.add_line((w,h),(0,h))
    msp.add_line((0,h),(0,0))
    # основная надпись справа внизу
    bx, by, bw, bh = w-185, 0, 185, 55
    msp.add_line((bx,by),(bx+bw,by))
    msp.add_line((bx+bw,by),(bx+bw,by+bh))
    msp.add_line((bx+bw,by+bh),(bx,by+bh))
    msp.add_line((bx,by+bh),(bx,by))
    # горизонтальные линии основной надписи
    for dy in [8, 16, 24, 32, 40, 48]:
        msp.add_line((bx, by+dy), (bx+bw, by+dy))
    # вертикальные линии
    for dx in [18, 100, 140, 165]:
        msp.add_line((bx+dx, by), (bx+dx, by+bh))
    # текст
    msp.add_text("ТермоКисть-6", dxfattribs={'height': 5}).set_placement((bx+18, by+50))
    msp.add_text("Сборочный чертёж", dxfattribs={'height': 4}).set_placement((bx+18, by+42))
    msp.add_text("Масштаб 1:1", dxfattribs={'height': 3}).set_placement((bx+100, by+26))
    msp.add_text("Материал: ABS/PC", dxfattribs={'height': 3}).set_placement((bx+18, by+18))
    msp.add_text("Масса: 180 г", dxfattribs={'height': 3}).set_placement((bx+18, by+10))

def draw_rect(msp, x, y, w, h, layer="0"):
    msp.add_line((x,y),(x+w,y), dxfattribs={'layer': layer})
    msp.add_line((x+w,y),(x+w,y+h), dxfattribs={'layer': layer})
    msp.add_line((x+w,y+h),(x,y+h), dxfattribs={'layer': layer})
    msp.add_line((x,y+h),(x,y), dxfattribs={'layer': layer})

def add_dim(msp, x1, y1, x2, y2, offset=10, text="", above=True):
    """Простая размерная линия"""
    if abs(y1 - y2) < 1:  # горизонтальная
        yo = y1 + offset if above else y1 - offset
        msp.add_line((x1, y1), (x1, yo))
        msp.add_line((x2, y2), (x2, yo))
        msp.add_line((x1, yo), (x2, yo))
        if text:
            msp.add_text(text, dxfattribs={'height': 3}).set_placement(((x1+x2)/2, yo+2))
    else:  # вертикальная
        xo = x1 + offset if above else x1 - offset
        msp.add_line((x1, y1), (xo, y1))
        msp.add_line((x2, y2), (xo, y2))
        msp.add_line((xo, y1), (xo, y2))
        if text:
            t = msp.add_text(text, dxfattribs={'height': 3})
            t.set_placement((xo+2, (y1+y2)/2))
            t.dxf.rotation = 90

# Сборочный чертёж — вид сверху
doc = ezdxf.new('R2010')
msp = doc.modelspace()
add_gost_frame(msp)
# Корпус (вид сверху)
ox, oy = 80, 120
draw_rect(msp, ox, oy, L_main, W_main, "CORPUS")
# Зоны нагрева
for i in range(3):
    draw_rect(msp, ox + t_wall + i*z_len, oy + t_wall, z_len, W_main - 2*t_wall, f"ZONE{i+1}")
# Батарейный отсек
draw_rect(msp, ox + bat_x, oy + (W_main-W_bat)/2, L_bat, W_bat, "BAT")
# Размеры
add_dim(msp, ox, oy, ox+L_main, oy, offset=-15, text=f"{L_main}")
add_dim(msp, ox, oy, ox, oy+W_main, offset=-15, text=f"{W_main}")
add_dim(msp, ox+bat_x, oy+(W_main-W_bat)/2, ox+bat_x+L_bat, oy+(W_main-W_bat)/2, offset=5, text=f"{L_bat}")
# Текст
msp.add_text("Вид сверху", dxfattribs={'height': 5}).set_placement((ox, oy+W_main+10))
msp.add_text("Зона 1 (ладонная)", dxfattribs={'height': 3, 'color': 1}).set_placement((ox+5, oy+5))
msp.add_text("Зона 2 (тыльная)", dxfattribs={'height': 3, 'color': 3}).set_placement((ox+5+z_len, oy+5))
msp.add_text("Зона 3 (предплечье)", dxfattribs={'height': 3, 'color': 5}).set_placement((ox+5+2*z_len, oy+5))
dxf_path = os.path.join(PROTO, "01_termokist-6_sborochny.dxf")
doc.saveas(dxf_path)
print(f"  Сборочный DXF ✓")

# PDF из DXF
try:
    fig_dxf, ax_dxf = plt.subplots(figsize=(12, 8.5))
    ezdxf_mpl.draw(doc, ax=ax_dxf)
    ax_dxf.set_title("ТермоКисть-6: Сборочный чертёж (вид сверху)", fontsize=11)
    plt.tight_layout()
    pdf_path = os.path.join(PROTO, "01_termokist-6_sborochny.pdf")
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight'); plt.close()
    print("  Сборочный PDF ✓")
except Exception as ex:
    print(f"  Сборочный PDF: {ex}")

# Разрез А-А
doc2 = ezdxf.new('R2010')
msp2 = doc2.modelspace()
add_gost_frame(msp2)
ox2, oy2 = 80, 130
# Нижний корпус
draw_rect(msp2, ox2, oy2, L_main, t_wall, "0")
# Изоляция ПЭ
draw_rect(msp2, ox2+t_wall, oy2+t_wall, L_main-2*t_wall, t_insul, "0")
# Аэрогель
draw_rect(msp2, ox2+t_wall, oy2+t_wall+t_insul, L_main-2*t_wall, t_aero, "0")
# PCM
draw_rect(msp2, ox2+t_wall, oy2+t_wall+t_insul+t_aero, L_main-2*t_wall, t_pcm, "0")
# Греющий слой
draw_rect(msp2, ox2+t_wall, oy2+z_h, L_main-2*t_wall, t_heat, "0")
# Верхний корпус
draw_rect(msp2, ox2, oy2+z_h+t_heat, L_main, t_wall, "0")
# Размеры по высоте
add_dim(msp2, ox2-5, oy2, ox2-5, oy2+H_main, offset=-10, text=f"{H_main}")
# Подписи слоёв
msp2.add_text("Корпус ABS", dxfattribs={'height': 2.5}).set_placement((ox2+L_main+5, oy2+1))
msp2.add_text("ПЭ изоляция", dxfattribs={'height': 2.5}).set_placement((ox2+L_main+5, oy2+t_wall+t_insul/2))
msp2.add_text("Аэрогель", dxfattribs={'height': 2.5}).set_placement((ox2+L_main+5, oy2+t_wall+t_insul+t_aero/2))
msp2.add_text("PCM 100г", dxfattribs={'height': 2.5}).set_placement((ox2+L_main+5, oy2+t_wall+t_insul+t_aero+t_pcm/2))
msp2.add_text("Нагреватель", dxfattribs={'height': 2.5}).set_placement((ox2+L_main+5, oy2+z_h))
msp2.add_text("Разрез А-А", dxfattribs={'height': 5}).set_placement((ox2, oy2+H_main+10))
dxf2 = os.path.join(PROTO, "01_termokist-6_razrez.dxf")
doc2.saveas(dxf2)
print("  Разрез DXF ✓")

try:
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    ezdxf_mpl.draw(doc2, ax=ax2)
    ax2.set_title("ТермоКисть-6: Разрез А-А", fontsize=11)
    plt.tight_layout()
    pdf2 = os.path.join(PROTO, "01_termokist-6_razrez.pdf")
    plt.savefig(pdf2, format='pdf', bbox_inches='tight'); plt.close()
    print("  Разрез PDF ✓")
except Exception as ex:
    print(f"  Разрез PDF: {ex}")

# ── ЭЛЕКТРИЧЕСКАЯ СХЕМА (matplotlib) ────────────────────────────
fig_s, ax_s = plt.subplots(figsize=(14, 10))
ax_s.set_xlim(0, 100); ax_s.set_ylim(0, 80)
ax_s.set_aspect('equal'); ax_s.axis('off')
ax_s.set_title('ТермоКисть-6: Принципиальная электрическая схема', fontsize=13)

# Блоки
blocks = [
    (10, 40, 18, 12, 'Li-Po\n15000мА·ч\n3.7В', '#2563EB'),
    (35, 60, 18, 10, 'BMS\n(зарядка\n+ защита)', '#F59E0B'),
    (35, 40, 18, 12, 'DC-DC\n3.3В\n(η=85%)', '#10B981'),
    (60, 60, 22, 10, 'MCU\n(ARM Cortex\nnRF52832)', '#8B5CF6'),
    (60, 40, 10, 8, 'NTC\n×3', '#EF4444'),
    (75, 40, 12, 8, 'BLE\nмодуль', '#2563EB'),
    (60, 25, 10, 8, 'Аксел.\nLIS2DH', '#F59E0B'),
    (60, 10, 22, 10, 'ШИМ-драйвер\n(3 канала\n×2Вт)', '#EF4444'),
    (85, 10, 12, 10, 'Нагрев.\n×3 зоны\n(6Вт)', '#FF6B6B'),
    (35, 20, 18, 10, 'Подогрев\nотсека\nбатареи', '#FF8C00'),
    (60, 50, 22, 8, 'LED/\nЗвуковая\nиндикация', '#10B981'),
]

for (x, y, w, h, label, color) in blocks:
    rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5", 
                                    facecolor=color, edgecolor='#333', alpha=0.2, linewidth=1.5)
    ax_s.add_patch(rect)
    ax_s.text(x+w/2, y+h/2, label, ha='center', va='center', fontsize=7, fontweight='bold')

# Соединения
connections = [
    (28, 46, 35, 65, '+'), (28, 46, 35, 46, '+'),  # Li-Po → BMS, DC-DC
    (53, 65, 60, 65, 'I2C/SPI'), (53, 46, 60, 46, '3.3V'),  # BMS→MCU, DC-DC→датчики
    (70, 60, 70, 48, 'ADC'), (82, 60, 82, 48, 'BLE'),  # MCU→NTC, MCU→BLE
    (65, 60, 65, 48, 'I2C'),  # MCU→аксел.
    (71, 60, 71, 35, 'ШИМ'),  # MCU→драйвер
    (82, 15, 85, 15, ''),  # драйвер→нагреватели
    (44, 30, 44, 40, '3.3V'),  # DC-DC→подогрев
]
for (x1, y1, x2, y2, lbl) in connections:
    ax_s.annotate('', xy=(x2, y2), xytext=(x1, y1),
                  arrowprops=dict(arrowstyle='->', color='#333', lw=1.2))
    if lbl:
        ax_s.text((x1+x2)/2+1, (y1+y2)/2+1, lbl, fontsize=6, color='#666')

ax_s.text(5, 5, 'Источник: расчёт проекта. Дата: 08.10.2026', fontsize=7, color='#999')
plt.tight_layout()
shema_pdf = os.path.join(GRAF, "IMG_T01_01_shema.png")
plt.savefig(shema_pdf, dpi=300, bbox_inches='tight', facecolor='white'); plt.close()
print("  Электрическая схема ✓")

# ── BOM ─────────────────────────────────────────────────────────
hf=Font(bold=True,size=11); hfi=PatternFill('solid',fgColor='D9E1F2')
thin=Side(style='thin'); bdr=Border(left=thin,right=thin,top=thin,bottom=thin)
def mk(): wb=Workbook(); wb.remove(wb.active); return wb
def asht(wb,t,h,d):
    ws=wb.create_sheet(t)
    for c,v in enumerate(h,1): cell=ws.cell(1,c,v); cell.font=hf; cell.fill=hfi; cell.border=bdr
    for r,row in enumerate(d,2):
        for c,v in enumerate(row,1): ws.cell(r,c,v).border=bdr
    for c in range(1,len(h)+1): ws.column_dimensions[chr(64+c)].width=20

wb=mk()
asht(wb,"Компоненты",["№","Категория","Наименование","Тип/марка","Кол-во","Ед.","Цена (₽)","Сумма (₽)","Источник","Прим."],
    [["1","Корпус","Корпус нижний ABS","3D-печать","1","шт","150","150","расч. оценка","ABS/PC"],
     ["2","Корпус","Корпус верхний ABS","3D-печать","1","шт","150","150","расч. оценка","ABS/PC"],
     ["3","Батарея","Li-Po 15000 мА·ч","LP-103450","1","шт","1200","1200","расч. оценка","3.7В"],
     ["4","BMS","BMS-модуль 1S","TP4056+DW01","1","шт","50","50","расч. оценка","зарядка+защита"],
     ["5","DC-DC","Преобразователь 3.3В","MP2307","1","шт","80","80","расч. оценка","η=85%"],
     ["6","MCU","nRF52832","nRF52832-QFAA","1","шт","350","350","расч. оценка","BLE 5.0"],
     ["7","Датчик","NTC 10kOm","NTC 10k B3950","3","шт","15","45","расч. оценка","±0.1°C"],
     ["8","Датчик","Акселерометр","LIS2DH12","1","шт","120","120","расч. оценка","MEMS"],
     ["9","Нагреватель","Греющий кабель","silicone heater","3","м","200","600","расч. оценка","2Вт/м"],
     ["10","PCM","Парафин C20-C28","RT28","100","г","500/кг","50","расч. оценка","L=200кДж/кг"],
     ["11","Изоляция","Аэрогель 3мм","Pyrogel XT","1","дм²","300","300","расч. оценка","λ=0.013"],
     ["12","Изоляция","Вспененный ПЭ 2мм","ППЭ-Э","1","дм²","30","30","расч. оценка","λ=0.035"],
     ["13","Крепеж","Липучка + ремешок","нейлон","1","компл","80","80","расч. оценка",""],
     ["14","Прочее","Паяльные работы","—","1","компл","200","200","расч. оценка",""]])
asht(wb,"Материалы",["№","Наименование","Кол-во","Ед.","Цена","Сумма","Источник"],
    [["1","ABS-пластик (3D-печать)","100","г","500₽/кг","50","расч. оценка"],
     ["2","Парафин C20-C28","100","г","500₽/кг","50","расч. оценка"],
     ["3","Аэрогель 3мм","1","дм²","300₽/дм²","300","расч. оценка"],
     ["4","ППЭ 2мм","1","дм²","30₽/дм²","30","расч. оценка"]])
asht(wb,"Изготовление",["№","Операция","Время (ч)","Ставка (₽/ч)","Сумма (₽)"],
    [["1","3D-печать корпуса","4","200","800"],["2","Пайка электроники","2","300","600"],
     ["3","Сборка (греющие слои+PCM)","3","200","600"],["4","Тестирование","1","300","300"]])
asht(wb,"Итого",["Статья","Сумма (₽)"],
    [["Компоненты",3505],["Материалы",430],["Изготовление",2300],["ИТОГО себестоимость",6235]])
wb.save(os.path.join(PROTO, "bom.xlsx"))
print("  BOM ✓")

# ── СПЕЦИФИКАЦИЯ (txt/md) ────────────────────────────────────────
spec = """# СПЕЦИФИКАЦИЯ: ТермоКисть-6

## 1. Назначение
Автономная греющая накладка на кисть и предплечье с предиктивным дозированием тепловой мощности по трём зонам. Предназначена для защиты работников от переохлаждения при выполнении работ в условиях низких температур.

## 2. Состав
1. Корпус (нижняя + верхняя крышка) — ABS/PC, 3D-печать.
2. Три независимые зоны нагрева (греющий кабель в силиконовой матрице).
3. Слой PCM (100 г парафина C20-C28) — фазовый переход при 28°C.
4. Многослойная изоляция (ППЭ 2мм + аэрогель 3мм).
5. Батарейный отсек с подогревом (Li-Po 15000 мА·ч).
6. Электронный модуль: MCU nRF52832, ШИМ-драйвер, BMS, DC-DC.
7. Датчики: 3× NTC 10kOm, акселерометр LIS2DH12.
8. BLE-модуль для связи с приложением.
9. Ремешок (нейлоновая лента с липучкой).

## 3. Материалы и покрытия
- Корпус: ABS/PC (3D-печать FDM), толщина стенки 2 мм.
- Греющий слой: нихромовый кабель в силиконовой матрице.
- PCM: парафин C20-C28 (T_пл = 28°C, L = 200 кДж/кг).
- Изоляция: аэрогель Pyrogel XT (3 мм, λ = 0.013 Вт/(м·°C)) + ППЭ (2 мм).

## 4. Массогабаритные характеристики
- Длина: 220 мм
- Ширина: 110 мм
- Высота: 30 мм (основной блок) + 20 мм (батарейный отсек)
- Масса: ≤ 180 г

## 5. Условия эксплуатации
- Температура среды: от −40°C до +40°C
- Относительная влажность: до 95% (при +25°C)
- Защита: IP54
- Атмосферное давление: 84–107 кПа

## 6. Технические характеристики
1. Время обогрева: 6 ч при −40°C.
2. Температура кожи: 26 ± 1°C.
3. Зоны нагрева: 3 независимые (тыльная, ладонная, предплечье).
4. Аккумулятор: 15 000 мА·ч, Li-Po, 3.7 В.
5. Ресурс: ≥ 800 циклов заряда-разряда.
6. Защита: IP54.
7. Связь: BLE 5.0.

## 7. Комплектность
1. Накладка греющая — 1 шт.
2. Зарядное устройство USB-C — 1 шт.
3. Ремешок запасной — 1 шт.
4. Руководство пользователя — 1 шт.
"""
with open(os.path.join(PROTO, "specifikaciya.md"), 'w', encoding='utf-8') as f:
    f.write(spec)
print("  Спецификация ✓")

# ── 9 ГРАФИК ДЛЯ ЗАЯВКИ ─────────────────────────────────────────
plt.rcParams['font.family'] = 'DejaVu Sans'

# 02: чертёж-эскиз
fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.set_xlim(0, 280); ax2.set_ylim(0, 180); ax2.set_aspect('equal'); ax2.axis('off')
rect_main = mpatches.FancyBboxPatch((30, 50), L_main, W_main, boxstyle="round,pad=2",
                                     facecolor='#E5E7EB', edgecolor='#333', linewidth=2)
ax2.add_patch(rect_main)
# Зоны
for i in range(3):
    c = ['#2563EB', '#F59E0B', '#10B981'][i]
    r = mpatches.Rectangle((30+t_wall+i*z_len, 50+t_wall), z_len, W_main-2*t_wall, 
                            facecolor=c, alpha=0.3, edgecolor=c, linewidth=1.5)
    ax2.add_patch(r)
    ax2.text(30+t_wall+i*z_len+z_len/2, 50+t_wall+(W_main-2*t_wall)/2, f'Зона {i+1}', ha='center', va='center', fontsize=8)
# Батарея
r_bat = mpatches.Rectangle((30+bat_x, 50+(W_main-W_bat)/2), L_bat, W_bat,
                            facecolor='#6B7280', alpha=0.3, edgecolor='#333', linewidth=1.5, linestyle='--')
ax2.add_patch(r_bat)
ax2.text(30+bat_x+L_bat/2, 50+(W_main-W_bat)/2+W_bat/2, 'Li-Po\n15А·ч', ha='center', va='center', fontsize=7)
# Размеры
ax2.annotate('', xy=(30+L_main, 40), xytext=(30, 40), arrowprops=dict(arrowstyle='<->', color='#333'))
ax2.text(30+L_main/2, 37, f'{L_main} мм', ha='center', fontsize=9)
ax2.annotate('', xy=(20, 50+W_main), xytext=(20, 50), arrowprops=dict(arrowstyle='<->', color='#333'))
ax2.text(17, 50+W_main/2, f'{W_main} мм', ha='right', va='center', fontsize=9, rotation=90)
ax2.set_title('ТермоКисть-6: Эскиз сборочного чертежа (вид сверху)', fontsize=11)
plt.tight_layout(); plt.savefig(os.path.join(GRAF, "IMG_T01_02_chertezh.png"), dpi=300, bbox_inches='tight', facecolor='white'); plt.close()

# 04: график из RC-модели (уже есть в 03_grafika, копируем ссылку)
# 06: конкуренты
fig6, ax6 = plt.subplots(figsize=(10, 5))
names = ['RL-2600', 'Alpenheat\nвставка', 'Alpenheat\nперчатка', 'ТермоКисть-6\n(проект)']
prices = [2795, 19500, 25000, 3500]  # расч. оценка
colors = ['#EF4444', '#EF4444', '#EF4444', '#2563EB']
ax6.bar(names, prices, color=colors)
ax6.set_ylabel('Цена (₽)'); ax6.set_title('ТермоКисть-6: Сравнение с конкурентами')
ax6.grid(True, alpha=0.3, axis='y')
for i, v in enumerate(prices):
    ax6.text(i, v+200, f'{v:,} ₽', ha='center', fontsize=9)
plt.tight_layout(); plt.savefig(os.path.join(GRAF, "IMG_T01_06_konkurenty.png"), dpi=300, bbox_inches='tight', facecolor='white'); plt.close()

# 07: Гант
fig7, ax7 = plt.subplots(figsize=(12, 4))
tasks = [
    ('ТЗ и ТЭО', 1, 3), ('Патентный поиск FTO', 1, 2), ('Тепловой расчёт', 1, 3),
    ('Подача заявки ПМ', 2, 3), ('Образец №1', 4, 6), ('Стенд камера −45°C', 4, 6),
    ('Отладка ПИД', 5, 6), ('ПО журнал', 4, 6), ('Протокол предв.', 6, 6),
    ('Натурные испытания', 7, 9), ('Доработка', 8, 9), ('Проект ТУ', 9, 9),
    ('Партия 10 шт.', 10, 12), ('Опытная эксплуатация', 10, 12), ('Итоговый отчёт', 12, 12),
]
colors_g = ['#2563EB', '#2563EB', '#2563EB', '#2563EB', '#F59E0B', '#F59E0B', '#F59E0B', '#F59E0B', '#F59E0B',
            '#10B981', '#10B981', '#10B981', '#8B5CF6', '#8B5CF6', '#8B5CF6']
for i, ((name, s, e), c) in enumerate(zip(tasks, colors_g)):
    ax7.barh(i, e-s+1, left=s-0.5, height=0.6, color=c, alpha=0.8)
    ax7.text(s-0.3, i, name, va='center', fontsize=7)
ax7.set_xlabel('Месяц'); ax7.set_yticks([])
ax7.set_xticks(range(1, 13)); ax7.set_xticklabels([f'{m}' for m in range(1, 13)])
ax7.set_title('ТермоКисть-6: Календарный план (Гант)', fontsize=11)
ax7.grid(True, alpha=0.3, axis='x')
plt.tight_layout(); plt.savefig(os.path.join(GRAF, "IMG_T01_07_gant.png"), dpi=300, bbox_inches='tight', facecolor='white'); plt.close()

# 08: экономика-инфографика
fig8, ax8 = plt.subplots(figsize=(10, 5))
labels = ['Потери на\nобогрев', 'Стоимость\nслучая', 'Экономия\nна бригаду']
vals = [1.15, 2.1, 1.15]
units = ['млн ₽/год', 'млн ₽', 'млн ₽/год']
colors8 = ['#EF4444', '#EF4444', '#10B981']
bars = ax8.bar(labels, vals, color=colors8, width=0.5)
for bar, v, u in zip(bars, vals, units):
    ax8.text(bar.get_x() + bar.get_width()/2, bar.get_height()+0.03, f'{v} {u}', ha='center', fontsize=10)
ax8.set_ylabel('млн ₽'); ax8.set_title('ТермоКисть-6: Экономическое обоснование')
ax8.grid(True, alpha=0.3, axis='y')
plt.tight_layout(); plt.savefig(os.path.join(GRAF, "IMG_T01_08_ekonomika.png"), dpi=300, bbox_inches='tight', facecolor='white'); plt.close()

print("\n✓ ТермоКисть-6: Д+2 завершён.")