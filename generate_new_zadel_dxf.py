import ezdxf
import math
import os

BASE = "/home/user/The-competition-is-for-5-applications-all-6-are-accepted."

def draw_a3_border(ms, title, scale_str="1:1"):
    ms.add_line((0, 0), (420, 0))
    ms.add_line((420, 0), (420, 297))
    ms.add_line((420, 297), (0, 297))
    ms.add_line((0, 297), (0, 0))
    ms.add_line((5, 5), (415, 5))
    ms.add_line((415, 5), (415, 292))
    ms.add_line((415, 292), (5, 292))
    ms.add_line((5, 292), (5, 5))
    ms.add_line((277, 5), (277, 50))
    ms.add_line((277, 50), (415, 50))
    ms.add_line((277, 17), (415, 17))
    ms.add_line((277, 28), (415, 28))
    ms.add_line((277, 39), (415, 39))
    ms.add_line((346, 5), (346, 17))
    ms.add_line((346, 28), (346, 39))
    ms.add_line((346, 50), (346, 50))
    ms.add_text(title, dxfattribs={"height": 5, "insert": (280, 42)}).set_placement((280, 42))
    ms.add_text(scale_str, dxfattribs={"height": 3, "insert": (350, 30)}).set_placement((350, 30))
    ms.add_text("А3", dxfattribs={"height": 4, "insert": (350, 8)}).set_placement((350, 8))

def add_dim(ms, x1, y1, x2, y2, offset=10, text=""):
    ms.add_line((x1, y1), (x2, y2))
    if x1 == x2:
        ms.add_line((x1 - 3, y1), (x1 + 3, y1))
        ms.add_line((x1 - 3, y2), (x1 + 3, y2))
        ms.add_line((x1, y1), (x1 - offset, y1))
        ms.add_line((x1, y2), (x1 - offset, y2))
        ms.add_line((x1 - offset, y1), (x1 - offset, y2))
        if text:
            ms.add_text(text, dxfattribs={"height": 2.5, "insert": (x1 - offset - 15, (y1 + y2) / 2)}).set_placement((x1 - offset - 15, (y1 + y2) / 2))
    else:
        ms.add_line((x1, y1 - 3), (x1, y1 + 3))
        ms.add_line((x2, y2 - 3), (x2, y2 + 3))
        ms.add_line((x1, y1), (x1, y1 - offset))
        ms.add_line((x2, y2), (x2, y2 - offset))
        ms.add_line((x1, y1 - offset), (x2, y2 - offset))
        if text:
            ms.add_text(text, dxfattribs={"height": 2.5, "insert": ((x1 + x2) / 2, y1 - offset - 8)}).set_placement(((x1 + x2) / 2, y1 - offset - 8))

def generate_spektragro_sborochny():
    path = os.path.join(BASE, "03_spektragro-p/03_grafika/dxf/03_spektragro-p_sborochny.dxf")
    doc = ezdxf.new("R2010")
    ms = doc.modelspace()
    draw_a3_border(ms, "СпектрАгро-П Сборочный чертёж", "1:1")
    cx, cy = 140, 160
    ms.add_lwpolyline([(cx-90, cy-60), (cx+90, cy-60), (cx+90, cy+60), (cx-90, cy+60)], close=True)
    ms.add_lwpolyline([(cx-86, cy-56), (cx+86, cy-56), (cx+86, cy+56), (cx-86, cy+56)], close=True)
    ms.add_circle((cx-30, cy+30), 10)
    ms.add_circle((cx+30, cy+30), 6)
    ms.add_lwpolyline([(cx-30, cy-20), (cx+30, cy-20), (cx+30, cy+20), (cx-30, cy+20)])
    ms.add_circle((cx-60, cy-30), 4)
    ms.add_circle((cx+60, cy-30), 4)
    add_dim(ms, cx-90, cy-60, cx+90, cy-60, 15, "180")
    add_dim(ms, cx-90, cy-60, cx-90, cy+60, -15, "120")
    ms.add_text("NIR модуль", dxfattribs={"height": 3, "insert": (cx-50, cy+35)}).set_placement((cx-50, cy+35))
    ms.add_text("УФ модуль", dxfattribs={"height": 3, "insert": (cx+15, cy+35)}).set_placement((cx+15, cy+35))
    ms.add_text("PCB", dxfattribs={"height": 3, "insert": (cx-15, cy+25)}).set_placement((cx-15, cy+25))
    ms.add_text("pH коннектор", dxfattribs={"height": 2.5, "insert": (cx-75, cy-25)}).set_placement((cx-75, cy-25))
    ms.add_text("BLE антенна", dxfattribs={"height": 2.5, "insert": (cx+45, cy-25)}).set_placement((cx+45, cy-25))
    doc.saveas(path)
    print(f"  Created: {path}")

def generate_spektragro_shema():
    path = os.path.join(BASE, "03_spektragro-p/03_grafika/dxf/03_spektragro-p_shema.dxf")
    doc = ezdxf.new("R2010")
    ms = doc.modelspace()
    draw_a3_border(ms, "СпектрАгро-П Структурная схема", "Не в масштабе")
    blocks = [
        ("STM32H743", 200, 200, 60, 30),
        ("NIR модуль", 80, 200, 50, 25),
        ("УФ модуль", 80, 160, 50, 25),
        ("pH электрод", 80, 120, 50, 25),
        ("Кондуктометр", 80, 80, 50, 25),
        ("TFT дисплей", 320, 200, 50, 25),
        ("BLE nRF52832", 320, 160, 50, 25),
        ("Аккумулятор", 320, 120, 50, 25),
    ]
    for name, x, y, w, h in blocks:
        ms.add_lwpolyline([(x, y), (x+w, y), (x+w, y+h), (x, y+h)], close=True)
        ms.add_text(name, dxfattribs={"height": 2.5, "insert": (x+3, y+h/2)}).set_placement((x+3, y+h/2))
    ms.add_line((130, 212), (200, 212))
    ms.add_line((130, 172), (200, 172))
    ms.add_line((130, 132), (200, 132))
    ms.add_line((130, 92), (200, 92))
    ms.add_line((260, 212), (320, 212))
    ms.add_line((260, 172), (320, 172))
    ms.add_line((260, 132), (320, 132))
    doc.saveas(path)
    print(f"  Created: {path}")

def generate_fermaavto_sborochny():
    path = os.path.join(BASE, "05_fermaavto-5/03_grafika/dxf/05_fermaavto-5_sborochny.dxf")
    doc = ezdxf.new("R2010")
    ms = doc.modelspace()
    draw_a3_border(ms, "ФермаАвто-5 Сборочный чертёж", "1:1")
    cx, cy = 140, 160
    ms.add_lwpolyline([(cx-60, cy-40), (cx+60, cy-40), (cx+60, cy+40), (cx-60, cy+40)], close=True)
    ms.add_lwpolyline([(cx-57, cy-37), (cx+57, cy-37), (cx+57, cy+37), (cx-57, cy+37)], close=True)
    for i in range(6):
        angle = i * 60
        x = cx + 35 * math.cos(math.radians(angle))
        y = cy + 35 * math.sin(math.radians(angle))
        ms.add_circle((x, y), 8)
        ms.add_circle((x, y), 5)
    ms.add_lwpolyline([(cx-22, cy-13), (cx+22, cy-13), (cx+22, cy+13), (cx-22, cy+13)])
    ms.add_lwpolyline([(cx-15, cy-25), (cx+15, cy-25), (cx+15, cy-15), (cx-15, cy-15)])
    ms.add_line((cx+55, cy), (cx+70, cy))
    ms.add_line((cx+70, cy-5), (cx+70, cy+5))
    add_dim(ms, cx-60, cy-40, cx+60, cy-40, 15, "120")
    add_dim(ms, cx-60, cy-40, cx-60, cy+40, -15, "80")
    ms.add_text("Jetson Nano", dxfattribs={"height": 3, "insert": (cx-18, cy)}).set_placement((cx-18, cy))
    ms.add_text("OV9282", dxfattribs={"height": 2.5, "insert": (cx-10, cy-22)}).set_placement((cx-10, cy-22))
    ms.add_text("УЗ×6", dxfattribs={"height": 2.5, "insert": (cx+25, cy+25)}).set_placement((cx+25, cy+25))
    doc.saveas(path)
    print(f"  Created: {path}")

def generate_fermaavto_shema():
    path = os.path.join(BASE, "05_fermaavto-5/03_grafika/dxf/05_fermaavto-5_shema.dxf")
    doc = ezdxf.new("R2010")
    ms = doc.modelspace()
    draw_a3_border(ms, "ФермаАвто-5 Структурная схема", "Не в масштабе")
    blocks = [
        ("Jetson Nano", 200, 200, 60, 30),
        ("OV9282 камера", 80, 220, 50, 20),
        ("УЗ HC-SR04×6", 80, 180, 50, 20),
        ("MPU6050 IMU", 80, 140, 50, 20),
        ("Энкодеры", 80, 100, 50, 20),
        ("nRF52840", 200, 140, 60, 25),
        ("CAN трансивер", 200, 100, 60, 25),
        ("WiFi модуль", 320, 220, 50, 20),
        ("LoRa модуль", 320, 180, 50, 20),
        ("Двигатели", 320, 100, 50, 20),
    ]
    for name, x, y, w, h in blocks:
        ms.add_lwpolyline([(x, y), (x+w, y), (x+w, y+h), (x, y+h)], close=True)
        ms.add_text(name, dxfattribs={"height": 2.5, "insert": (x+3, y+h/2)}).set_placement((x+3, y+h/2))
    ms.add_line((130, 230), (200, 230))
    ms.add_line((130, 190), (200, 190))
    ms.add_line((130, 150), (200, 150))
    ms.add_line((130, 110), (200, 110))
    ms.add_line((260, 230), (320, 230))
    ms.add_line((260, 190), (320, 190))
    ms.add_line((260, 110), (320, 110))
    doc.saveas(path)
    print(f"  Created: {path}")

def generate_vibramon_sborochny():
    path = os.path.join(BASE, "06_vibramon-6/03_grafika/dxf/06_vibramon-6_sborochny.dxf")
    doc = ezdxf.new("R2010")
    ms = doc.modelspace()
    draw_a3_border(ms, "ВибраМон-6 Сенсорный узел", "2:1")
    cx, cy = 140, 160
    ms.add_lwpolyline([(cx-25, cy-20), (cx+25, cy-20), (cx+25, cy+20), (cx-25, cy+20)], close=True)
    ms.add_lwpolyline([(cx-23, cy-18), (cx+23, cy-18), (cx+23, cy+18), (cx-23, cy+18)], close=True)
    ms.add_lwpolyline([(cx-20, cy-20), (cx+20, cy-20), (cx+20, cy-23), (cx-20, cy-23)], close=True)
    for x in [-12, 12]:
        for y in [-8, 8]:
            ms.add_circle((cx+x, cy+y), 5)
    ms.add_circle((cx, cy), 12)
    ms.add_line((cx-10, cy+18), (cx-10, cy+30))
    ms.add_line((cx+10, cy+18), (cx+10, cy+30))
    ms.add_arc((cx, cy+30), 10, 0, 180)
    add_dim(ms, cx-25, cy-20, cx+25, cy-20, 10, "50")
    add_dim(ms, cx-25, cy-20, cx-25, cy+20, -10, "40")
    ms.add_text("ADXL355", dxfattribs={"height": 2, "insert": (cx+5, cy+2)}).set_placement((cx+5, cy+2))
    ms.add_text("MEMS", dxfattribs={"height": 2, "insert": (cx-20, cy+2)}).set_placement((cx-20, cy+2))
    ms.add_text("Магниты", dxfattribs={"height": 2, "insert": (cx-8, cy-18)}).set_placement((cx-8, cy-18))
    ms.add_text("Антенна", dxfattribs={"height": 2, "insert": (cx+5, cy+32)}).set_placement((cx+5, cy+32))
    doc.saveas(path)
    print(f"  Created: {path}")

def generate_vibramon_shema():
    path = os.path.join(BASE, "06_vibramon-6/03_grafika/dxf/06_vibramon-6_shema.dxf")
    doc = ezdxf.new("R2010")
    ms = doc.modelspace()
    draw_a3_border(ms, "ВибраМон-6 Структурная схема", "Не в масштабе")
    blocks = [
        ("nRF52840", 200, 200, 60, 30),
        ("ADXL355", 80, 220, 50, 20),
        ("MEMS микрофон", 80, 180, 50, 20),
        ("PT100", 80, 140, 50, 20),
        ("CT датчик", 80, 100, 50, 20),
        ("BLE Mesh", 320, 220, 50, 20),
        ("Raspberry Pi", 320, 160, 60, 30),
        ("WiFi", 320, 100, 50, 20),
    ]
    for name, x, y, w, h in blocks:
        ms.add_lwpolyline([(x, y), (x+w, y), (x+w, y+h), (x, y+h)], close=True)
        ms.add_text(name, dxfattribs={"height": 2.5, "insert": (x+3, y+h/2)}).set_placement((x+3, y+h/2))
    ms.add_line((130, 230), (200, 230))
    ms.add_line((130, 190), (200, 190))
    ms.add_line((130, 150), (200, 150))
    ms.add_line((130, 110), (200, 110))
    ms.add_line((260, 230), (320, 230))
    ms.add_line((260, 175), (320, 175))
    ms.add_line((260, 110), (320, 110))
    doc.saveas(path)
    print(f"  Created: {path}")

print("Generating DXF files...")
generate_spektragro_sborochny()
generate_spektragro_shema()
generate_fermaavto_sborochny()
generate_fermaavto_shema()
generate_vibramon_sborochny()
generate_vibramon_shema()
print("Done!")