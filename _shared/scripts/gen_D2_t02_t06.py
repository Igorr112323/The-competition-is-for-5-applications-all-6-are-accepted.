#!/usr/bin/env python3
"""
Д+2: единый генератор для тем 02-06.
STL-модели (trimesh), DXF-чертежи (ezdxf), BOM (openpyxl), спецификации, графика.
"""
import os, math, numpy as np
import trimesh, ezdxf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

REPO = "/home/user/The-competition-is-for-5-applications-all-6-are-accepted."

# Общие стили
hf = Font(bold=True, size=11); hfi = PatternFill('solid', fgColor='D9E1F2')
thin = Side(style='thin'); bdr = Border(left=thin, right=thin, top=thin, bottom=thin)
def mk(): wb = Workbook(); wb.remove(wb.active); return wb
def asht(wb, t, h, d):
    ws = wb.create_sheet(t)
    for c, v in enumerate(h, 1):
        cell = ws.cell(1, c, v); cell.font = hf; cell.fill = hfi; cell.border = bdr
    for r, row in enumerate(d, 2):
        for c, v in enumerate(row, 1): ws.cell(r, c, v).border = bdr
    for c in range(1, len(h)+1): ws.column_dimensions[chr(64+c)].width = 20

def make_box(x, y, z, sx, sy, sz, color=None):
    v = np.array([[x,y,z],[x+sx,y,z],[x+sx,y+sy,z],[x,y+sy,z],
                  [x,y,z+sz],[x+sx,y,z+sz],[x+sx,y+sy,z+sz],[x,y+sy,z+sz]])
    f = np.array([[0,1,2],[0,2,3],[4,5,6],[4,6,7],[0,1,5],[0,5,4],
                  [2,3,7],[2,7,6],[0,3,7],[0,7,4],[1,2,6],[1,6,5]])
    m = trimesh.Trimesh(vertices=v, faces=f)
    if color: m.visual.face_colors = color
    return m

def add_gost_frame(msp, w=420, h=297, title="", subtitle="", scale="1:1"):
    msp.add_line((0,0),(w,0)); msp.add_line((w,0),(w,h))
    msp.add_line((w,h),(0,h)); msp.add_line((0,h),(0,0))
    bx, by, bw, bh = w-185, 0, 185, 55
    msp.add_line((bx,by),(bx+bw,by)); msp.add_line((bx+bw,by),(bx+bw,by+bh))
    msp.add_line((bx+bw,by+bh),(bx,by+bh)); msp.add_line((bx,by+bh),(bx,by))
    for dy in [8,16,24,32,40,48]: msp.add_line((bx,by+dy),(bx+bw,by+dy))
    for dx in [18,100,140,165]: msp.add_line((bx+dx,by),(bx+dx,by+bh))
    msp.add_text(title, dxfattribs={'height':5}).set_placement((bx+18,by+50))
    msp.add_text(subtitle, dxfattribs={'height':4}).set_placement((bx+18,by+42))
    msp.add_text(f"Масштаб {scale}", dxfattribs={'height':3}).set_placement((bx+100,by+26))

def draw_rect_dxf(msp, x, y, w, h, layer="0"):
    for (x1,y1,x2,y2) in [(x,y,x+w,y),(x+w,y,x+w,y+h),(x+w,y+h,x,y+h),(x,y+h,x,y)]:
        msp.add_line((x1,y1),(x2,y2), dxfattribs={'layer': layer})

def save_dxf_pdf(doc, dxf_path, pdf_path, title):
    doc.saveas(dxf_path)
    try:
        from ezdxf.addons.drawing import RenderContext, Frontend
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
        fig, ax = plt.subplots(figsize=(12, 8.5))
        ctx = RenderContext(doc)
        out = MatplotlibBackend(ax)
        Frontend(ctx, out).draw_layout(doc.modelspace(), finalize=True)
        ax.set_title(title, fontsize=11)
        plt.tight_layout(); plt.savefig(pdf_path, format='pdf', bbox_inches='tight'); plt.close()
        return True
    except Exception as ex:
        print(f"    PDF: {ex}")
        return False

def render_3d_preview(meshes, labels_colors, title, out_path):
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    for mesh, color in meshes:
        pc = Poly3DCollection(mesh.vertices[mesh.faces], alpha=0.7, facecolor=color, edgecolor='#333', linewidth=0.3)
        ax.add_collection3d(pc)
    all_v = np.vstack([m.vertices for m,_ in meshes])
    mr = (all_v.max(0)-all_v.min(0)).max()/2; mid = all_v.mean(0)
    ax.set_xlim(mid[0]-mr, mid[0]+mr); ax.set_ylim(mid[1]-mr, mid[1]+mr); ax.set_zlim(mid[2]-mr, mid[2]+mr)
    ax.set_xlabel('X (мм)'); ax.set_ylabel('Y (мм)'); ax.set_zlabel('Z (мм)')
    ax.set_title(title, fontsize=12); ax.view_init(25, 135)
    plt.tight_layout(); plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='white'); plt.close()

def gannt_chart(tasks, title, out_path):
    fig, ax = plt.subplots(figsize=(12, 4))
    colors_g = ['#2563EB','#F59E0B','#10B981','#8B5CF6']
    for i, (name, s, e, phase) in enumerate(tasks):
        ax.barh(i, e-s+1, left=s-0.5, height=0.6, color=colors_g[phase%4], alpha=0.8)
        ax.text(s-0.3, i, name, va='center', fontsize=7)
    ax.set_xlabel('Месяц'); ax.set_yticks([]); ax.set_xticks(range(1,13))
    ax.set_title(title); ax.grid(True, alpha=0.3, axis='x')
    plt.tight_layout(); plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white'); plt.close()

def konkurent_chart(names, prices, title, out_path):
    fig, ax = plt.subplots(figsize=(10, 5))
    colors_k = ['#EF4444']*(len(names)-1) + ['#2563EB']
    ax.bar(names, prices, color=colors_k)
    ax.set_ylabel('Цена (₽)'); ax.set_title(title); ax.grid(True, alpha=0.3, axis='y')
    for i, v in enumerate(prices): ax.text(i, v+max(prices)*0.02, f'{v:,}₽', ha='center', fontsize=9)
    plt.tight_layout(); plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white'); plt.close()

# ═══════════════════════════════════════════════════════════════
# ТЕМА 02: ВетПЦР-Чемодан
# ═══════════════════════════════════════════════════════════════
def gen_t02():
    P = os.path.join(REPO, "02_vetpcr-chemodan/01_zadel/prototype")
    G = os.path.join(REPO, "02_vetpcr-chemodan/03_grafika")
    os.makedirs(P, exist_ok=True); os.makedirs(G, exist_ok=True)

    # STL: чемодан 450×350×180
    chassis = make_box(0,0,0, 450,350,3, [60,60,60,255])
    walls = [make_box(0,0,0, 450,3,180, [70,70,70,255]),
             make_box(0,347,0, 450,3,180, [70,70,70,255]),
             make_box(0,0,0, 3,350,180, [70,70,70,255]),
             make_box(447,0,0, 3,350,180, [70,70,70,255])]
    # 32-луночный блок 8×4, шаг 9мм
    wells = []
    for r in range(8):
        for c in range(4):
            w = make_box(50+r*9, 50+c*9, 3, 7, 7, 15, [200,200,200,255])
            wells.append(w)
    # Оптический модуль
    optic = make_box(200, 150, 3, 40, 40, 30, [30,30,30,255])
    # Батарейный отсек
    battery = make_box(350, 50, 3, 80, 100, 40, [50,50,50,255])
    scene = trimesh.Scene([chassis]+walls+wells+[optic, battery])
    stl = os.path.join(P, "model3d.stl"); scene.export(stl)
    print(f"  T02 STL ✓ ({os.path.getsize(stl)} байт)")

    # Preview
    meshes = [(chassis,'#3C3C3C')]+[(w,'#464646') for w in walls]+[(w,'#C8C8C8') for w in wells]+[(optic,'#1E1E1E'),(battery,'#323232')]
    render_3d_preview(meshes, None, "ВетПЦР-Чемодан: 3D-модель", os.path.join(P, "model3d_preview.png"))
    print("  T02 Preview ✓")

    # DXF: сборочный чертёж
    doc = ezdxf.new('R2010'); msp = doc.modelspace()
    add_gost_frame(msp, title="ВетПЦР-Чемодан", subtitle="Сборочный чертёж")
    ox, oy = 50, 80
    draw_rect_dxf(msp, ox, oy, 450, 350)
    # Лунки
    for r in range(8):
        for c in range(4):
            msp.add_circle((ox+50+r*9+3.5, oy+50+c*9+3.5), 3.5)
    # Размеры
    msp.add_text("450", dxfattribs={'height':4}).set_placement((ox+200, oy-10))
    msp.add_text("350", dxfattribs={'height':4}).set_placement((ox-15, oy+175))
    msp.add_text("8×4 лунки, шаг 9мм", dxfattribs={'height':3}).set_placement((ox+50, oy+90))
    msp.add_text("Оптика", dxfattribs={'height':3}).set_placement((ox+200, oy+155))
    dxf_p = os.path.join(P, "02_vetpcr-chemodan_sborochny.dxf")
    save_dxf_pdf(doc, dxf_p, os.path.join(P, "02_vetpcr-chemodan_sborochny.pdf"), "ВетПЦР-Чемодан: Сборочный чертёж")
    print("  T02 DXF+PDF ✓")

    # BOM
    wb = mk()
    asht(wb,"Компоненты",["№","Категория","Наименование","Тип/марка","Кол-во","Цена (₽)","Сумма (₽)","Источник"],
        [["1","Корпус","Корпус-чемодан ABS","3D-печать","1","800","800","расч."],
         ["2","Термоциклер","Пельтье-элемент TEC1-12706","TEC1-12706","32","120","3840","расч."],
         ["3","Оптика","LED FAM/HEX/ROX/Cy5","Luxeon","4","250","1000","расч."],
         ["4","Оптика","Фотодиод Si","BPW34","4","80","320","расч."],
         ["5","MCU","STM32F407","STM32F407VGT6","1","450","450","расч."],
         ["6","Насос","Магнитный микронасос","TCS-25","1","600","600","расч."],
         ["7","Дисплей","TFT 3.5 дюйма","ILI9488","1","800","800","расч."],
         ["8","Батарея","Li-Ion 12В 20Ач","Sanyo NCR","1","4000","4000","расч."],
         ["9","BMS","BMS 3S","3S 20A","1","200","200","расч."],
         ["10","Картриджи","Лиофилизированный","собств. состав","100","50","5000","расч."]])
    wb.save(os.path.join(P, "bom.xlsx")); print("  T02 BOM ✓")

    # Спецификация
    with open(os.path.join(P, "specifikaciya.md"), 'w', encoding='utf-8') as f:
        f.write("# СПЕЦИФИКАЦИЯ: ВетПЦР-Чемодан\n\n## Назначение\nПереносной ПЦР-анализатор на лиофилизированных картриджах.\n\n## Состав\n1. Корпус-чемодан 450×350×180 мм.\n2. 32-луночный термоциклер (Пельтье).\n3. Оптический модуль 4 канала (FAM/HEX/ROX/Cy5).\n4. Экстракция на магнитных частицах в картридже.\n5. MCU + TFT-дисплей.\n6. Li-Ion 12В×20А·ч.\n\n## ТТХ\n- Анализ: 40 мин (ПЦР-РВ) / 15-20 мин (LAMP)\n- 4 патогена × 8 проб (32 лунки)\n- Масса ≤5 кг\n- Автономность 8 ч\n- Чувствительность до 10² копий/мкл\n- XML-выгрузка в ВетИС\n")
    print("  T02 Спецификация ✓")

    # Графики
    konkurent_chart(['ИнноКвик\n(5кг, 2 пробы)', 'Лаб. ПЦР\n(1-2 сут)', 'Импортные\n(ушли)', 'ВетПЦР\n(проект)'],
                    [150000, 5800, 200000, 80000], "ВетПЦР: Сравнение с конкурентами", os.path.join(G, "IMG_T02_06_konkurenty.png"))
    gannt_chart([('ТЗ',1,3,0),('Узлы термоциклера',1,3,0),('Лиофилизация',2,3,0),
                 ('Прототип',4,6,1),('Оптика',4,6,1),('ПО+ВетИС',5,6,1),
                 ('Сличения 100 проб',7,9,2),('Выезды',8,9,2),
                 ('Образец №2',10,12,3),('Опытная эксплуатация',10,12,3),('Отчёт',12,12,3)],
                "ВетПЦР-Чемодан: Гант", os.path.join(G, "IMG_T02_07_gant.png"))
    print("  T02 Графика ✓")
    print("  Т02 ✓")

# ═══════════════════════════════════════════════════════════════
# ТЕМА 03-06: компактные генераторы
# ═══════════════════════════════════════════════════════════════
def gen_generic(num, name, dims, components_bom, konkurents, gantt_tasks, gantt_title, spec_text):
    P = os.path.join(REPO, f"{num:02d}_{name}/01_zadel/prototype")
    G = os.path.join(REPO, f"{num:02d}_{name}/03_grafika")
    os.makedirs(P, exist_ok=True); os.makedirs(G, exist_ok=True)
    prefix = f"{num:02d}_{name}"

    # STL: сборка из примитивов
    meshes = []
    for (x,y,z,sx,sy,sz,c) in dims:
        meshes.append(make_box(x,y,z,sx,sy,sz,c))
    scene = trimesh.Scene(meshes)
    stl = os.path.join(P, "model3d.stl"); scene.export(stl)

    # Preview
    def _mesh_color(m):
        try: c = m.visual.face_colors[0]; return '#{:02X}{:02X}{:02X}'.format(int(c[0]),int(c[1]),int(c[2]))
        except: return '#808080'
    render_3d_preview([(m, _mesh_color(m)) for m in meshes], None, f"{name}: 3D-модель", os.path.join(P, "model3d_preview.png"))

    # DXF
    doc = ezdxf.new('R2010'); msp = doc.modelspace()
    add_gost_frame(msp, title=name, subtitle="Сборочный чертёж")
    ox, oy = 60, 80
    max_x = max(d[0]+d[3] for d in dims); max_y = max(d[1]+d[4] for d in dims)
    scale = min(300/max_x, 150/max_y, 1.0)
    for (x,y,z,sx,sy,sz,c) in dims:
        draw_rect_dxf(msp, ox+x*scale, oy+y*scale, sx*scale, sy*scale)
    dxf_p = os.path.join(P, f"{prefix}_sborochny.dxf")
    save_dxf_pdf(doc, dxf_p, os.path.join(P, f"{prefix}_sborochny.pdf"), f"{name}: Сборочный чертёж")

    # Разрез
    doc2 = ezdxf.new('R2010'); msp2 = doc2.modelspace()
    add_gost_frame(msp2, title=name, subtitle="Разрез")
    for (x,y,z,sx,sy,sz,c) in dims[:3]:
        draw_rect_dxf(msp2, ox+x*scale, oy+z*scale, sx*scale, sz*scale)
    dxf2 = os.path.join(P, f"{prefix}_razrez.dxf")
    save_dxf_pdf(doc2, dxf2, os.path.join(P, f"{prefix}_razrez.pdf"), f"{name}: Разрез")

    # BOM
    wb = mk()
    asht(wb,"Компоненты",["№","Категория","Наименование","Тип/марка","Кол-во","Цена (₽)","Сумма (₽)","Источник"],
        components_bom)
    wb.save(os.path.join(P, "bom.xlsx"))

    # Спецификация
    with open(os.path.join(P, "specifikaciya.md"), 'w', encoding='utf-8') as f:
        f.write(spec_text)

    # Графики
    if konkurents:
        konkurent_chart(*konkurents, os.path.join(G, f"IMG_T{num:02d}_06_konkurenty.png"))
    if gantt_tasks:
        gannt_chart(gantt_tasks, gantt_title, os.path.join(G, f"IMG_T{num:02d}_07_gant.png"))

    print(f"  Т{num:02d} ✓")

# ═══════════════════════════════════════════════════════════════
# ЗАПУСК
# ═══════════════════════════════════════════════════════════════
print("Д+2: генерация для тем 02-06...")
gen_t02()

# Т03: Паразит-Контроль
gen_generic(3, "parazit-kontrol",
    [(0,0,0, 600,400,3, [80,80,80,255]),     # основание
     (0,0,0, 3,400,500, [70,70,70,255]),     # стенка
     (597,0,0, 3,400,500, [70,70,70,255]),
     (0,0,0, 600,3,500, [70,70,70,255]),
     (0,397,0, 600,3,500, [70,70,70,255]),
     (100,100,3, 30,30,40, [200,200,200,255]),  # пробоотборник
     (200,150,3, 80,80,60, [180,180,180,255]),   # микроскоп
     (350,100,3, 200,20,30, [150,150,150,255])], # конвейер
    [["1","Корпус","Станция 600×400×500","3D-печать+алюминий","1","2500","2500","расч."],
     ["2","Камера","CMOS 12MP","IMX477","1","1200","1200","расч."],
     ["3","Мотор","Шаговый NEMA17","NEMA17","2","350","700","расч."],
     ["4","MCU","NVIDIA Jetson Nano","Jetson","1","5000","5000","расч."],
     ["5","Освещение","LED кольцо","RGB LED","1","400","400","расч."],
     ["6","АКБ","Li-Ion 12В×10Ач","Sanyo","1","3000","3000","расч."]],
    (['Ручная\nмикроскопия', 'Лаборатория\n(1-2 сут)', 'Паразит-Контроль\n(проект)'],
     [0, 2500, 1500], "Паразит-Контроль: Сравнение стоимости"),
    [('ТЗ',1,3,0),('Датасет ≥3000 кадров',1,3,0),('Пробоподготовка',4,6,1),
     ('Макет',4,6,1),('Обучение НС',5,6,1),('Полевые 50+ проб',7,9,2),
     ('Сличения',8,9,2),('Сборка ПАК',10,12,3),('Опытная эксплуатация',10,12,3)],
    "Паразит-Контроль: Гант",
    "# СПЕЦИФИКАЦИЯ: Паразит-Контроль\n\n## Назначение\nПАК автоматической паразитологической оценки партий промысловой рыбы.\n\n## Состав\n1. Станция отбора/микроскопии 600×400×500 мм.\n2. Пробоотборник-дозатор.\n3. Модуль макро/микроскопии (CMOS 12MP).\n4. Конвейерная подача (шаговые моторы).\n5. Jetson Nano + НС-классификатор.\n6. ГИС-модуль (GPS).\n7. Li-Ion 12В×10А·ч.\n\n## ТТХ\n- 30 проб за 4 ч\n- Детекция от 1 личинки/100 г\n- Точность ≥90%\n- Масса ≤12 кг\n- Автономность 8 ч\n")

# Т04: ОптикоЗор-2,0
gen_generic(4, "optikozor-2-0",
    [(0,0,0, 300,300,5, [80,80,80,255]),       # платформа
     (140,140,5, 60,40,50, [50,50,50,255]),    # ОЭ-модуль (ТВ+ИК)
     (0,0,5, 300,5,1500, [70,70,70,255]),      # стойка
     # Микрофоны по кругу
     ] + [(150+125*math.cos(2*math.pi*i/8), 150+125*math.sin(2*math.pi*i/8), 5, 15,15,20, [100,100,100,255]) for i in range(8)],
    [["1","Платформа","Поворотная Ø300","алюминий","1","3000","3000","расч."],
     ["2","Камера ТВ","CMOS 12MP","IMX477","1","1200","1200","расч."],
     ["3","Камера ИК","LWIR 640×480","FLIR Lepton","1","8000","8000","расч."],
     ["4","Акустика","Микрофон MEMS","ICS-43434","8","50","400","расч."],
     ["5","Edge-вычислитель","NVIDIA Jetson Orin","Orin Nano","1","15000","15000","расч."],
     ["6","Привод","Серводвигатель","Dynamixel","1","2000","2000","расч."],
     ["7","ИБП","LiFePO4 12В×10Ач","EVE","1","6000","6000","расч."]],
    (['Хамелеон\n(1км)', 'Малик\n(500-1000м)', 'Купол\n(300-500м)', 'ОптикоЗор\n(проект)'],
     [4995000, 1500000, 800000, 3000000], "ОптикоЗор: Сравнение цен"),
    [('ТЗ',1,3,0),('Датасет БПЛА',1,3,0),('FTO+ПМ',2,3,0),
     ('Стендовый пост',4,6,1),('Обучение детектора',4,6,1),('Предиктор',5,6,1),
     ('Полигон 60+ заданий',7,9,2),('Замеры дальности',8,9,2),
     ('Образец',10,12,3),('Опытная эксплуатация',10,12,3)],
    "ОптикоЗор-2,0: Гант",
    "# СПЕЦИФИКАЦИЯ: ОптикоЗор-2,0\n\n## Назначение\nМультимодальный пассивный пост обнаружения БПЛА.\n\n## Состав\n1. Поворотная платформа Ø300 мм.\n2. ОЭ-модуль (ТВ + ИК).\n3. Акустическая решётка 8 микрофонов по кругу Ø250 мм.\n4. Edge-вычислитель (Jetson Orin).\n5. Защитный кожух.\n6. ИБП LiFePO4.\n\n## ТТХ\n- ОЭ: 2 км день / 1.2 км ночь\n- Акустика: до 1 км\n- Ложные тревоги: ≤1 на 100 ч\n- Прогноз: 40 с\n- Время выдачи: ≤0.5 с\n- Сектор 360°, до 24 целей\n- Энергопотребление ≤150 Вт\n")

# Т05: ЦехГид-5
gen_generic(5, "cehgid-5",
    [(0,0,0, 150,100,3, [80,80,80,255]),     # основание
     (0,0,3, 3,100,80, [60,60,60,255]),      # стенка
     (147,0,3, 3,100,80, [60,60,60,255]),
     (0,0,3, 150,3,80, [60,60,60,255]),
     (0,97,3, 150,3,80, [60,60,60,255]),
     (30,30,83, 70,70,20, [50,50,50,255]),    # крепление лидара
     (110,30,83, 30,30,15, [40,40,40,255])],  # крепление камеры
    [["1","Корпус","Корпус IP65","алюминий+резина","1","800","800","расч."],
     ["2","Лидар","RPLIDAR A3","Slamtec","1","8000","8000","расч."],
     ["3","Камера","VIO-камера","OAK-D Lite","1","5000","5000","расч."],
     ["4","IMU","Блок IMU","BNO055","1","500","500","расч."],
     ["5","MCU","NVIDIA Jetson Nano","Jetson","1","5000","5000","расч."],
     ["6","Питание","DC-DC 24В→5В","MP1584","1","100","100","расч."],
     ["7","Виброразвязка","Силиконовые втулки","—","4","50","200","расч."],
     ["8","Разъёмы","M12 IP67","—","4","150","600","расч."]],
    (['Модули для\nчистых помещ.', 'Роботы\n(без SLAM)', 'ЦехГид-5\n(проект)'],
     [50000, 200000, 40000], "ЦехГид-5: Сравнение"),
    [('ТЗ',1,3,0),('Модель карта-якорь',1,3,0),('Пилотные тесты',2,3,0),
     ('Образец №1',4,6,1),('SLAM с якорями',5,6,1),('Метрика',5,6,1),
     ('200 ч в цехе',7,9,2),('Калибровка',8,9,2),
     ('Опытная эксплуатация',10,12,3),('Заявка ПМ+ПО',11,12,3)],
    "ЦехГид-5: Гант",
    "# СПЕЦИФИКАЦИЯ: ЦехГид-5\n\n## Назначение\nМодуль технического зрения для автономных роботов птичников.\n\n## Состав\n1. Корпус IP65 150×100×80 мм.\n2. VIO-камера (OAK-D Lite).\n3. 2D-лидар RPLIDAR A3.\n4. IMU BNO055.\n5. Jetson Nano.\n6. Виброразвязка (силиконовые втулки).\n7. Разъёмы M12 IP67.\n\n## ТТХ\n- Точность: ±5 см без ГНСС\n- Запылённость: до 10 мг/м³\n- Наработка: 200 ч в цехе\n- Режим: 24/7\n- Питание: 24 В, ≤15 Вт\n- IP65\n")

# Т06: Смена-Прогноз-40
gen_generic(6, "smena-prognoz-40",
    [(0,0,0, 42,36,3, [80,80,80,255]),       # браслет основание
     (0,0,3, 42,36,9, [60,60,60,255]),       # крышка
     (15,2,3, 12,8,1, [200,200,200,255]),    # окно PPG
     (30,2,3, 8,8,1, [150,150,150,255]),     # окно NTC
     (5,25,3, 32,8,1, [180,180,180,255]),    # электроды КГР
     (50,0,0, 120,90,3, [80,80,80,255]),     # шлюз основание
     (50,0,3, 120,90,32, [60,60,60,255]),    # шлюз крышка
     (160,30,20, 15,15,30, [50,50,50,255])], # антенна LoRa
    [["1","Корпус","Корпус браслета","PC/ABS","1","200","200","расч."],
     ["2","MCU","nRF52840","Nordic","1","400","400","расч."],
     ["3","PPG","Si1153","Silicon Labs","1","150","150","расч."],
     ["4","NTC","NTC 10kOm","Murata","1","10","10","расч."],
     ["5","Акселерометр","LIS2DW12","ST","1","80","80","расч."],
     ["6","LoRa","SX1276","Semtech","1","200","200","расч."],
     ["7","АКБ","Li-Po 300мАч","LP503035","1","150","150","расч."],
     ["8","Шлюз","LoRa-шлюз ESP32+ SX1276","—","1","2000","2000","расч."],
     ["9","Ремешок","Силиконовый","—","1","50","50","расч."]],
    (['Фитнес-\nтрекеры', 'Мед. носимые\n(нужна рег.)', 'HSE-платформы\n(нет прогноа)', 'Смена-Прогноз\n(проект)'],
     [3000, 50000, 100000, 50000], "Смена-Прогноз: Сравнение"),
    [('ТЗ+этико-правовая рамка',1,3,0),('Выбор сенсоров',1,2,0),('Прототип v1',2,3,0),('Заявка ПМ',3,3,0),
     ('Шлюз+ПО',4,6,1),('Пороги+ансамбль',5,6,1),('Лаб. валидация',6,6,1),
     ('Опытная эксплуатация ≥200 смен',7,9,2),('Второй объект',8,9,2),
     ('ПАК v3 (20 браслетов)',10,12,3),('Методика охраны труда',11,12,3),('Отчёт',12,12,3)],
    "Смена-Прогноз-40: Гант",
    "# СПЕЦИФИКАЦИЯ: Смена-Прогноз-40\n\n## Назначение\nНосимая мультисенсорная платформа прогноза состояния работника.\n\n## Состав\n1. Браслет 42×36×12 мм (≤50 г): PPG, NTC, КГР, акселерометр.\n2. LoRa-шлюз 120×90×35 мм.\n3. MCU nRF52840 + SX1276.\n4. Li-Po 300 мА·ч.\n\n## ТТХ\n- Датчиков: ≥6\n- Прогноз: ≥40 мин\n- Точность: ≥90%\n- Автономность: 7 суток, масса ≤50 г\n- Ложные тревоги: ≤1 на смену\n- Шлюз: LoRa, до 500 устройств, 5 км\n- Отчётность: CSV/API\n")

print("\n✓ Д+2: все темы (02-06) завершены.")