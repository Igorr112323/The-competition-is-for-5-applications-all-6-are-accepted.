import ezdxf
import math
import os

BASE = "/home/user/The-competition-is-for-5-applications-all-6-are-accepted."

def create_a3_dxf(filepath, title, scale_info, objects_func):
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    msp.add_line((0, 0), (420, 0), dxfattribs={'layer': 'frame'})
    msp.add_line((420, 0), (420, 297), dxfattribs={'layer': 'frame'})
    msp.add_line((420, 297), (0, 297), dxfattribs={'layer': 'frame'})
    msp.add_line((0, 297), (0, 0), dxfattribs={'layer': 'frame'})
    msp.add_line((5, 5), (415, 5), dxfattribs={'layer': 'frame'})
    msp.add_line((415, 5), (415, 292), dxfattribs={'layer': 'frame'})
    msp.add_line((415, 292), (5, 292), dxfattribs={'layer': 'frame'})
    msp.add_line((5, 292), (5, 5), dxfattribs={'layer': 'frame'})
    msp.add_line((272, 5), (272, 55), dxfattribs={'layer': 'frame'})
    msp.add_line((272, 55), (415, 55), dxfattribs={'layer': 'frame'})
    msp.add_line((272, 30), (415, 30), dxfattribs={'layer': 'frame'})
    msp.add_text(title, dxfattribs={'layer': 'text', 'height': 5, 'insert': (275, 40)})
    msp.add_text(scale_info, dxfattribs={'layer': 'text', 'height': 3.5, 'insert': (275, 15)})
    msp.add_text("А3", dxfattribs={'layer': 'text', 'height': 4, 'insert': (370, 15)})
    msp.add_text("КубГАУ | Старт-Пром-1", dxfattribs={'layer': 'text', 'height': 3, 'insert': (275, 22)})
    objects_func(msp)
    doc.saveas(filepath)

def draw_bolt(msp, x, y, d=6, l=30):
    msp.add_line((x, y), (x, y + l), dxfattribs={'layer': 'detail'})
    msp.add_circle((x, y), d / 2, dxfattribs={'layer': 'detail'})
    msp.add_circle((x, y + l), d / 2, dxfattribs={'layer': 'detail'})

def draw_flange(msp, cx, cy, od=60, id=20, bolts=4, bd=6):
    msp.add_circle((cx, cy), od / 2, dxfattribs={'layer': 'detail'})
    msp.add_circle((cx, cy), id / 2, dxfattribs={'layer': 'detail'})
    for i in range(bolts):
        a = 2 * math.pi * i / bolts
        bx = cx + (od / 2 - 8) * math.cos(a)
        by = cy + (od / 2 - 8) * math.sin(a)
        msp.add_circle((bx, by), bd / 2, dxfattribs={'layer': 'detail'})

def draw_dimensions(msp, x1, y1, x2, y2, offset=10):
    msp.add_line((x1, y1 - offset), (x2, y2 - offset), dxfattribs={'layer': 'dim'})
    msp.add_line((x1, y1 - offset - 2), (x1, y1 - offset + 2), dxfattribs={'layer': 'dim'})
    msp.add_line((x2, y2 - offset - 2), (x2, y2 - offset + 2), dxfattribs={'layer': 'dim'})

# ============================================================
# T01: АэроСкан-6
# ============================================================
def t01_objects(msp):
    msp.add_circle((200, 180), 35, dxfattribs={'layer': 'detail'})
    msp.add_circle((200, 180), 15, dxfattribs={'layer': 'detail'})
    msp.add_line((165, 180), (140, 180), dxfattribs={'layer': 'detail'})
    msp.add_line((235, 180), (260, 180), dxfattribs={'layer': 'detail'})
    msp.add_line((200, 145), (200, 120), dxfattribs={'layer': 'detail'})
    msp.add_line((200, 215), (200, 240), dxfattribs={'layer': 'detail'})
    msp.add_circle((140, 180), 8, dxfattribs={'layer': 'detail'})
    msp.add_circle((260, 180), 8, dxfattribs={'layer': 'detail'})
    msp.add_circle((200, 120), 10, dxfattribs={'layer': 'detail'})
    msp.add_circle((200, 240), 6, dxfattribs={'layer': 'detail'})
    msp.add_text("LiDAR RPLIDAR A1", dxfattribs={'layer': 'text', 'height': 3, 'insert': (280, 178)})
    msp.add_text("PWM-насос Procon", dxfattribs={'layer': 'text', 'height': 3, 'insert': (280, 118)})
    msp.add_text("Анемометр Davis", dxfattribs={'layer': 'text', 'height': 3, 'insert': (280, 238)})
    msp.add_text("Форсунка TeeJet x6", dxfattribs={'layer': 'text', 'height': 3, 'insert': (115, 178)})
    msp.add_text("Форсунка TeeJet x6", dxfattribs={'layer': 'text', 'height': 3, 'insert': (265, 178)})
    msp.add_line((160, 160), (240, 160), dxfattribs={'layer': 'detail'})
    msp.add_line((160, 200), (240, 200), dxfattribs={'layer': 'detail'})
    msp.add_line((160, 160), (160, 200), dxfattribs={'layer': 'detail'})
    msp.add_line((240, 160), (240, 200), dxfattribs={'layer': 'detail'})
    msp.add_text("nRF52840", dxfattribs={'layer': 'text', 'height': 4, 'insert': (185, 177)})
    msp.add_text("OLED", dxfattribs={'layer': 'text', 'height': 3, 'insert': (185, 185)})
    msp.add_text("Расходомер HAF", dxfattribs={'layer': 'text', 'height': 3, 'insert': (170, 155)})
    msp.add_line((200, 145), (200, 90), dxfattribs={'layer': 'detail'})
    msp.add_line((180, 90), (220, 90), dxfattribs={'layer': 'detail'})
    msp.add_text("Бак рабочей жидкости", dxfattribs={'layer': 'text', 'height': 3, 'insert': (225, 88)})
    draw_dimensions(msp, 160, 155, 240, 155, -15)
    msp.add_text("80 мм", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (190, 138)})

create_a3_dxf(
    os.path.join(BASE, "01_aeroskan-6/03_grafika/dxf/01_aeroskan-6_shema.dxf"),
    "АэроСкан-6 — Схема модуля", "М 1:1", t01_objects
)

def t01_assembly(msp):
    msp.add_line((120, 100), (300, 100), dxfattribs={'layer': 'detail'})
    msp.add_line((120, 100), (120, 220), dxfattribs={'layer': 'detail'})
    msp.add_line((300, 100), (300, 220), dxfattribs={'layer': 'detail'})
    msp.add_line((120, 220), (300, 220), dxfattribs={'layer': 'detail'})
    msp.add_line((130, 110), (290, 110), dxfattribs={'layer': 'detail'})
    msp.add_line((130, 110), (130, 210), dxfattribs={'layer': 'detail'})
    msp.add_line((290, 110), (290, 210), dxfattribs={'layer': 'detail'})
    msp.add_line((130, 210), (290, 210), dxfattribs={'layer': 'detail'})
    draw_flange(msp, 140, 115, 30, 12, 4, 4)
    draw_flange(msp, 280, 115, 30, 12, 4, 4)
    draw_flange(msp, 140, 205, 30, 12, 4, 4)
    draw_flange(msp, 280, 205, 30, 12, 4, 4)
    msp.add_circle((210, 160), 25, dxfattribs={'layer': 'detail'})
    msp.add_circle((210, 160), 10, dxfattribs={'layer': 'detail'})
    msp.add_text("Корпус модуля (алюминий)", dxfattribs={'layer': 'text', 'height': 3, 'insert': (180, 225)})
    msp.add_text("Крышка (поликарбонат)", dxfattribs={'layer': 'text', 'height': 3, 'insert': (180, 230)})
    msp.add_text("LiDAR", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (200, 157)})
    draw_dimensions(msp, 120, 95, 300, 95, -8)
    msp.add_text("180 мм", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (195, 85)})
    draw_dimensions(msp, 115, 100, 115, 220, -8)
    msp.add_text("120 мм", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (85, 155)})

create_a3_dxf(
    os.path.join(BASE, "01_aeroskan-6/03_grafika/dxf/01_aeroskan-6_sborochny.dxf"),
    "АэроСкан-6 — Сборочный чертёж", "М 1:2", t01_assembly
)

# ============================================================
# T04: ТочноВес-6
# ============================================================
def t04_objects(msp):
    msp.add_line((150, 120), (270, 120), dxfattribs={'layer': 'detail'})
    msp.add_line((150, 120), (150, 200), dxfattribs={'layer': 'detail'})
    msp.add_line((270, 120), (270, 200), dxfattribs={'layer': 'detail'})
    msp.add_line((150, 200), (270, 200), dxfattribs={'layer': 'detail'})
    msp.add_line((155, 125), (265, 125), dxfattribs={'layer': 'detail'})
    msp.add_line((155, 195), (265, 195), dxfattribs={'layer': 'detail'})
    msp.add_circle((210, 160), 15, dxfattribs={'layer': 'detail'})
    msp.add_circle((210, 160), 6, dxfattribs={'layer': 'detail'})
    msp.add_line((165, 135), (165, 185), dxfattribs={'layer': 'detail'})
    msp.add_line((175, 135), (175, 185), dxfattribs={'layer': 'detail'})
    msp.add_line((165, 135), (175, 135), dxfattribs={'layer': 'detail'})
    msp.add_line((165, 185), (175, 185), dxfattribs={'layer': 'detail'})
    msp.add_line((245, 135), (255, 135), dxfattribs={'layer': 'detail'})
    msp.add_line((245, 185), (255, 185), dxfattribs={'layer': 'detail'})
    msp.add_line((245, 135), (245, 185), dxfattribs={'layer': 'detail'})
    msp.add_line((255, 135), (255, 185), dxfattribs={'layer': 'detail'})
    msp.add_text("Лазерный датчик расхода", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (145, 108)})
    msp.add_text("Камера потока семян", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (240, 108)})
    msp.add_text("STM32H7", dxfattribs={'layer': 'text', 'height': 3, 'insert': (195, 157)})
    msp.add_text("OLED дисплей", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (130, 195)})
    msp.add_text("Корпус IP54", dxfattribs={'layer': 'text', 'height': 3, 'insert': (130, 205)})
    draw_dimensions(msp, 150, 115, 270, 115, -8)
    msp.add_text("120 мм", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (195, 105)})

create_a3_dxf(
    os.path.join(BASE, "04_toshnoves-6/03_grafika/dxf/04_toshnoves-6_shema.dxf"),
    "ТочноВес-6 — Схема модуля", "М 1:1", t04_objects
)

def t04_assembly(msp):
    msp.add_line((140, 110), (280, 110), dxfattribs={'layer': 'detail'})
    msp.add_line((140, 110), (140, 210), dxfattribs={'layer': 'detail'})
    msp.add_line((280, 110), (280, 210), dxfattribs={'layer': 'detail'})
    msp.add_line((140, 210), (280, 210), dxfattribs={'layer': 'detail'})
    draw_flange(msp, 155, 125, 25, 10, 3, 3)
    draw_flange(msp, 265, 125, 25, 10, 3, 3)
    draw_flange(msp, 155, 195, 25, 10, 3, 3)
    draw_flange(msp, 265, 195, 25, 10, 3, 3)
    msp.add_circle((210, 160), 20, dxfattribs={'layer': 'detail'})
    msp.add_circle((210, 160), 8, dxfattribs={'layer': 'detail'})
    msp.add_line((210, 140), (210, 120), dxfattribs={'layer': 'detail'})
    msp.add_line((210, 180), (210, 200), dxfattribs={'layer': 'detail'})
    msp.add_text("Вход семян", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (215, 205)})
    msp.add_text("Выход семян", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (215, 108)})
    msp.add_text("Корпус (алюминий)", dxfattribs={'layer': 'text', 'height': 3, 'insert': (160, 220)})
    msp.add_text("Камера потока", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (195, 157)})
    draw_dimensions(msp, 140, 105, 280, 105, -8)
    msp.add_text("140 мм", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (195, 95)})

create_a3_dxf(
    os.path.join(BASE, "04_toshnoves-6/03_grafika/dxf/04_toshnoves-6_sborochny.dxf"),
    "ТочноВес-6 — Сборочный чертёж", "М 1:1", t04_assembly
)

# ============================================================
# T05: КормоЭкструдер-5
# ============================================================
def t05_objects(msp):
    msp.add_circle((210, 170), 40, dxfattribs={'layer': 'detail'})
    msp.add_circle((210, 170), 25, dxfattribs={'layer': 'detail'})
    msp.add_circle((210, 170), 15, dxfattribs={'layer': 'detail'})
    msp.add_line((170, 170), (130, 170), dxfattribs={'layer': 'detail'})
    msp.add_line((250, 170), (290, 170), dxfattribs={'layer': 'detail'})
    msp.add_line((130, 160), (130, 180), dxfattribs={'layer': 'detail'})
    msp.add_line((290, 165), (290, 175), dxfattribs={'layer': 'detail'})
    msp.add_text("Загрузка зерна", dxfattribs={'layer': 'text', 'height': 3, 'insert': (100, 185)})
    msp.add_text("Выход гранул", dxfattribs={'layer': 'text', 'height': 3, 'insert': (295, 185)})
    msp.add_text("Шнек", dxfattribs={'layer': 'text', 'height': 3, 'insert': (195, 167)})
    msp.add_text("Матрица", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (270, 167)})
    msp.add_text("Корпус (сталь)", dxfattribs={'layer': 'text', 'height': 3, 'insert': (215, 215)})
    msp.add_text("Электромотор 2.2 кВт", dxfattribs={'layer': 'text', 'height': 3, 'insert': (175, 125)})
    msp.add_line((210, 130), (210, 100), dxfattribs={'layer': 'detail'})
    msp.add_line((200, 100), (220, 100), dxfattribs={'layer': 'detail'})
    msp.add_text("Привод", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (225, 98)})
    draw_dimensions(msp, 130, 155, 290, 155, -8)
    msp.add_text("160 мм", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (195, 145)})

create_a3_dxf(
    os.path.join(BASE, "05_kormoextruder-5/03_grafika/dxf/05_kormoextruder-5_shema.dxf"),
    "КормоЭкструдер-5 — Схема установки", "М 1:2", t05_objects
)

def t05_assembly(msp):
    msp.add_line((120, 100), (300, 100), dxfattribs={'layer': 'detail'})
    msp.add_line((120, 100), (120, 230), dxfattribs={'layer': 'detail'})
    msp.add_line((300, 100), (300, 230), dxfattribs={'layer': 'detail'})
    msp.add_line((120, 230), (300, 230), dxfattribs={'layer': 'detail'})
    msp.add_line((130, 110), (290, 110), dxfattribs={'layer': 'detail'})
    msp.add_line((130, 220), (290, 220), dxfattribs={'layer': 'detail'})
    msp.add_line((130, 110), (130, 220), dxfattribs={'layer': 'detail'})
    msp.add_line((290, 110), (290, 220), dxfattribs={'layer': 'detail'})
    msp.add_line((135, 115), (175, 115), dxfattribs={'layer': 'detail'})
    msp.add_line((135, 145), (175, 145), dxfattribs={'layer': 'detail'})
    msp.add_line((135, 115), (135, 145), dxfattribs={'layer': 'detail'})
    msp.add_line((175, 115), (175, 145), dxfattribs={'layer': 'detail'})
    msp.add_text("Бункер", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (140, 127)})
    msp.add_line((180, 130), (280, 130), dxfattribs={'layer': 'detail'})
    msp.add_line((180, 170), (280, 170), dxfattribs={'layer': 'detail'})
    msp.add_line((180, 130), (180, 170), dxfattribs={'layer': 'detail'})
    msp.add_line((280, 130), (280, 170), dxfattribs={'layer': 'detail'})
    msp.add_text("Корпус экструдера", dxfattribs={'layer': 'text', 'height': 3, 'insert': (200, 147)})
    msp.add_line((180, 180), (280, 180), dxfattribs={'layer': 'detail'})
    msp.add_line((180, 210), (280, 210), dxfattribs={'layer': 'detail'})
    msp.add_line((180, 180), (180, 210), dxfattribs={'layer': 'detail'})
    msp.add_line((280, 180), (280, 210), dxfattribs={'layer': 'detail'})
    msp.add_text("Матрица гранулятора", dxfattribs={'layer': 'text', 'height': 3, 'insert': (195, 192)})
    msp.add_text("Привод 2.2 кВт", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (285, 147)})
    draw_dimensions(msp, 120, 95, 300, 95, -8)
    msp.add_text("180 мм", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (195, 85)})

create_a3_dxf(
    os.path.join(BASE, "05_kormoextruder-5/03_grafika/dxf/05_kormoextruder-5_sborochny.dxf"),
    "КормоЭкструдер-5 — Сборочный чертёж", "М 1:2", t05_assembly
)

# ============================================================
# T06: СортоСепаратор-6
# ============================================================
def t06_objects(msp):
    msp.add_line((150, 120), (270, 120), dxfattribs={'layer': 'detail'})
    msp.add_line((150, 120), (150, 220), dxfattribs={'layer': 'detail'})
    msp.add_line((270, 120), (270, 220), dxfattribs={'layer': 'detail'})
    msp.add_line((150, 220), (270, 220), dxfattribs={'layer': 'detail'})
    for i in range(5):
        y = 130 + i * 18
        msp.add_line((155, y), (265, y), dxfattribs={'layer': 'detail'})
        for j in range(8):
            x = 162 + j * 13
            msp.add_circle((x, y + 5), 2.5, dxfattribs={'layer': 'detail'})
    msp.add_text("Виброрешето (3 фракции)", dxfattribs={'layer': 'text', 'height': 3, 'insert': (155, 225)})
    msp.add_text("Пьезо-вибратор", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (275, 160)})
    msp.add_text("ADXL355", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (275, 140)})
    msp.add_text("STM32F4", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (275, 120)})
    msp.add_line((270, 155), (290, 155), dxfattribs={'layer': 'detail'})
    msp.add_line((270, 135), (290, 135), dxfattribs={'layer': 'detail'})
    msp.add_line((270, 115), (290, 115), dxfattribs={'layer': 'detail'})
    msp.add_text("Корпус (алюминий)", dxfattribs={'layer': 'text', 'height': 3, 'insert': (155, 230)})
    msp.add_text("Аккумулятор 3.7V 2000mAh", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (155, 112)})
    draw_dimensions(msp, 150, 115, 270, 115, -8)
    msp.add_text("120 мм", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (195, 105)})

create_a3_dxf(
    os.path.join(BASE, "06_sortoseparator-6/03_grafika/dxf/06_sortoseparator-6_shema.dxf"),
    "СортоСепаратор-6 — Схема модуля", "М 1:1", t06_objects
)

def t06_assembly(msp):
    msp.add_line((130, 100), (290, 100), dxfattribs={'layer': 'detail'})
    msp.add_line((130, 100), (130, 230), dxfattribs={'layer': 'detail'})
    msp.add_line((290, 100), (290, 230), dxfattribs={'layer': 'detail'})
    msp.add_line((130, 230), (290, 230), dxfattribs={'layer': 'detail'})
    msp.add_line((140, 110), (280, 110), dxfattribs={'layer': 'detail'})
    msp.add_line((140, 220), (280, 220), dxfattribs={'layer': 'detail'})
    msp.add_line((140, 110), (140, 220), dxfattribs={'layer': 'detail'})
    msp.add_line((280, 110), (280, 220), dxfattribs={'layer': 'detail'})
    draw_flange(msp, 155, 125, 20, 8, 3, 3)
    draw_flange(msp, 265, 125, 20, 8, 3, 3)
    draw_flange(msp, 155, 205, 20, 8, 3, 3)
    draw_flange(msp, 265, 205, 20, 8, 3, 3)
    msp.add_line((145, 130), (275, 130), dxfattribs={'layer': 'detail'})
    msp.add_line((145, 150), (275, 150), dxfattribs={'layer': 'detail'})
    msp.add_line((145, 170), (275, 170), dxfattribs={'layer': 'detail'})
    msp.add_line((145, 190), (275, 190), dxfattribs={'layer': 'detail'})
    msp.add_text("Решето 1 (крупная фракция)", dxfattribs={'layer': 'text', 'height': 2, 'insert': (150, 137)})
    msp.add_text("Решето 2 (средняя фракция)", dxfattribs={'layer': 'text', 'height': 2, 'insert': (150, 157)})
    msp.add_text("Решето 3 (мелкая фракция)", dxfattribs={'layer': 'text', 'height': 2, 'insert': (150, 177)})
    msp.add_text("Поддон", dxfattribs={'layer': 'text', 'height': 2, 'insert': (150, 197)})
    msp.add_text("Корпус (алюминий)", dxfattribs={'layer': 'text', 'height': 3, 'insert': (150, 235)})
    draw_dimensions(msp, 130, 95, 290, 95, -8)
    msp.add_text("160 мм", dxfattribs={'layer': 'text', 'height': 2.5, 'insert': (195, 85)})

create_a3_dxf(
    os.path.join(BASE, "06_sortoseparator-6/03_grafika/dxf/06_sortoseparator-6_sborochny.dxf"),
    "СортоСепаратор-6 — Сборочный чертёж", "М 1:1", t06_assembly
)

print("ALL DXF GENERATED OK")