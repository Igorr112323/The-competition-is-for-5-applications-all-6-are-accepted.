import os
import math
import ezdxf

BASE = "/home/user/The-competition-is-for-5-applications-all-6-are-accepted."

def draw_a3_border(ms, title):
    ms.add_line((0,0),(420,0))
    ms.add_line((420,0),(420,297))
    ms.add_line((420,297),(0,297))
    ms.add_line((0,297),(0,0))
    ms.add_line((5,5),(415,5))
    ms.add_line((415,5),(415,292))
    ms.add_line((415,292),(5,292))
    ms.add_line((5,292),(5,5))
    ms.add_text(title, dxfattribs={"height":4,"insert":(280,42)}).set_placement((280,42))
    ms.add_text("А3", dxfattribs={"height":3,"insert":(350,8)}).set_placement((350,8))

TOPICS_DXF = {
    "01_teplovid-4": {
        "sborochny_title": "ТеплоВид-4 — Тепловизионный модуль для БПЛА",
        "shema_title": "ТеплоВид-4 — Структурная схема",
        "blocks": [("FLIR Lepton",100,180,60,25),("Jetson Nano",200,180,50,25),("OV9282 камера",200,140,50,25),("BLE модуль",300,180,50,25),("LiPo батарея",300,140,50,25),("Germanium lens",100,140,60,25)],
        "components": [("FLIR Lepton 3.5","160×120","Germanium lens f/1.1"),("Jetson Nano","472 GFLOPS","CUDA"),("OV9282","1280×800","Stereo")],
    },
    "02_spektrobio-2": {
        "sborochny_title": "СпектрБио-2 — Портативный анализатор биомаркеров",
        "shema_title": "СпектрБио-2 — Структурная схема",
        "blocks": [("STM32H743",200,180,60,25),("QCL/LED ИК",100,180,50,25),("MCT детектор",100,140,50,25),("Газовая кювета",100,100,60,25),("TFT дисплей",300,180,50,25),("BLE модуль",300,140,50,25)],
        "components": [("QCL/LED","2.5-5.0 мкм","ИК-источник"),("MCT","20-20000 Гц","Детектор"),("Кювета","10 см","Оптический путь")],
    },
    "03_lamp-dnk-ekspress": {
        "sborochny_title": "LAMP-ДНК-Экспресс — Телемедицинский комплекс",
        "shema_title": "LAMP-ДНК-Экспресс — Структурная схема",
        "blocks": [("nRF52840",200,180,60,25),("Нагреватель",100,180,50,25),("NTC датчик",100,140,50,25),("Фотодиоды ×4",100,100,50,25),("HNB индикатор",200,140,50,25),("BLE модуль",300,180,50,25),("OLED дисплей",300,140,50,25)],
        "components": [("nRF52840","BLE 5.0","MCU"),("PID","65±0.5°C","Нагреватель"),("Фотодиоды","4 канала","HNB детекция")],
    },
    "04_zreniebpila-5": {
        "sborochny_title": "ЗрениеБПЛА-5 — Модуль технического зрения",
        "shema_title": "ЗрениеБПЛА-5 — Структурная схема",
        "blocks": [("Jetson Nano",200,180,60,25),("OV9282 L",100,180,50,25),("OV9282 R",100,140,50,25),("IMU MPU6050",100,100,50,25),("WiFi модуль",300,180,50,25),("CAN трансивер",300,140,50,25)],
        "components": [("OV9282×2","1280×800","Stereo global shutter"),("Jetson Nano","472 GFLOPS","CUDA YOLOv5"),("Baseline","60 мм","Глубинное зрение")],
    },
    "05_autopilot-5": {
        "sborochny_title": "АвтоПилот-5 — Бортовое ПО автопилота",
        "shema_title": "АвтоПилот-5 — Структурная схема",
        "blocks": [("STM32H743",200,200,60,25),("Jetson Nano",200,160,60,25),("LiDAR",100,200,50,25),("IMU",100,160,50,25),("Энкодеры",100,120,50,25),("CAN шина",300,200,50,25),("MAVLink",300,160,50,25),("Двигатели",300,120,50,25)],
        "components": [("STM32H7","480 МГц","MCU"),("Jetson Nano","CUDA","SLAM"),("LiDAR","360°","12 м")],
    },
    "06_akustikmon-6": {
        "sborochny_title": "АкустикМон-6 — Носимый акустический монитор",
        "shema_title": "АкустикМон-6 — Структурная схема",
        "blocks": [("nRF52840",200,180,60,25),("MEMS микрофон",100,180,50,25),("АЦП 24 бит",100,140,50,25),("DSP ядро",100,100,50,25),("BLE модуль",300,180,50,25),("CR2450×2",300,140,50,25)],
        "components": [("MEMS","20-20000 Гц","SNR 65 дБ"),("nRF52840","BLE 5.0","MCU+DSP"),("FFT","4096 точек","11.7 Гц")],
    },
}

SCAD_FILES = {
    "01_teplovid-4": """// ТеплоВид-4 — Тепловизионный модуль
$fn = 64;
module main_body() {
    difference() {
        cube([60,40,25], center=true);
        translate([0,0,2]) cube([56,36,21], center=true);
    }
}
module lens_housing() {
    color([0.3,0.3,0.3])
    difference() {
        cylinder(d=22, h=15, center=true);
        cylinder(d=18, h=16, center=true);
    }
}
module assembly() {
    main_body();
    translate([0,20,0]) lens_housing();
}
assembly();
""",
    "02_spektrobio-2": """// СпектрБио-2 — Анализатор биомаркеров
$fn = 64;
module main_body() {
    difference() {
        cube([120,80,40], center=true);
        translate([0,0,2]) cube([116,76,36], center=true);
    }
}
module kuvette() {
    color([0.8,0.8,0.8])
    difference() {
        cube([40,20,15], center=true);
        translate([0,0,2]) cube([36,4,11], center=true);
    }
}
module assembly() {
    main_body();
    translate([20,0,-10]) kuvette();
}
assembly();
""",
    "03_lamp-dnk-ekspress": """// LAMP-ДНК-Экспресс — Кейс
$fn = 64;
module case_body() {
    difference() {
        cube([300,200,100], center=true);
        translate([0,0,3]) cube([294,194,94], center=true);
    }
}
module heater_block() {
    color([0.8,0.2,0.2])
    cube([60,40,20], center=true);
}
module assembly() {
    case_body();
    translate([-80,0,-30]) heater_block();
}
assembly();
""",
    "04_zreniebpila-5": """// ЗрениеБПЛА-5 — Стереокамера
$fn = 64;
module camera_body() {
    difference() {
        cube([80,30,25], center=true);
        translate([0,0,2]) cube([76,26,21], center=true);
    }
}
module lens() {
    color([0.2,0.2,0.2])
    cylinder(d=15, h=10, center=true);
}
module assembly() {
    camera_body();
    translate([-20,15,0]) lens();
    translate([20,15,0]) lens();
}
assembly();
""",
    "05_autopilot-5": """// АвтоПилот-5 — Контроллер
$fn = 64;
module pcb() {
    color([0.1,0.5,0.1])
    difference() {
        cube([80,50,1.6], center=true);
        translate([30,20,0]) cylinder(d=3, h=3, center=true);
        translate([-30,20,0]) cylinder(d=3, h=3, center=true);
        translate([30,-20,0]) cylinder(d=3, h=3, center=true);
        translate([-30,-20,0]) cylinder(d=3, h=3, center=true);
    }
}
module stm32() { color([0.2,0.2,0.2]) cube([14,14,1.5], center=true); }
module jetson() { color([0.1,0.5,0.1]) cube([45,27,1.6], center=true); }
module assembly() {
    pcb();
    translate([-15,0,2]) stm32();
    translate([15,0,2]) jetson();
}
assembly();
""",
    "06_akustikmon-6": """// АкустикМон-6 — Носимый модуль
$fn = 64;
module main_body() {
    difference() {
        cylinder(d=40, h=12, center=true);
        cylinder(d=36, h=10, center=true);
    }
}
module mic_hole() {
    translate([0,0,5]) cylinder(d=3, h=4);
}
module assembly() {
    main_body();
    mic_hole();
}
assembly();
""",
}

print("=== Generating DXF ===")
for key, t in TOPICS_DXF.items():
    doc = ezdxf.new("R2010")
    ms = doc.modelspace()
    draw_a3_border(ms, t["sborochny_title"])
    cx, cy = 140, 160
    ms.add_lwpolyline([(cx-60,cy-40),(cx+60,cy-40),(cx+60,cy+40),(cx-60,cy+40)], close=True)
    ms.add_lwpolyline([(cx-57,cy-37),(cx+57,cy-37),(cx+57,cy+37),(cx-57,cy+37)], close=True)
    for comp, name1, name2 in t["components"]:
        ms.add_text(comp, dxfattribs={"height":2.5,"insert":(cx-50,cy+25)}).set_placement((cx-50,cy+25))
        break
    path = os.path.join(BASE, key, "03_grafika/dxf", f"{key}_sborochny.dxf")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    doc.saveas(path)
    print(f"  ✓ {path}")

    doc2 = ezdxf.new("R2010")
    ms2 = doc2.modelspace()
    draw_a3_border(ms2, t["shema_title"])
    for name, x, y, w, h in t["blocks"]:
        ms2.add_lwpolyline([(x,y),(x+w,y),(x+w,y+h),(x,y+h)], close=True)
        ms2.add_text(name, dxfattribs={"height":2.5,"insert":(x+3,y+h/2)}).set_placement((x+3,y+h/2))
    path2 = os.path.join(BASE, key, "03_grafika/dxf", f"{key}_shema.dxf")
    doc2.saveas(path2)
    print(f"  ✓ {path2}")

print("\n=== Generating SCAD ===")
for key, code in SCAD_FILES.items():
    path = os.path.join(BASE, key, "03_grafika/stl", f"{key}_assembly.scad")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(code)
    print(f"  ✓ {path}")

print("\nDone!")