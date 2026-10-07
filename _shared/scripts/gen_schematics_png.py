#!/usr/bin/env python3
"""
Д+3.5: Графические электрические схемы (PNG) для Т02-Т06 с помощью schemdraw.
"""
import os, sys
import matplotlib
matplotlib.use('Agg')

REPO = "/home/user/The-competition-is-for-5-applications-all-6-are-accepted."

try:
    import schemdraw
    import schemdraw.elements as elm
    HAS_SCHEMDRAW = True
except ImportError:
    HAS_SCHEMDRAW = False
    print("WARNING: schemdraw not installed, falling back to matplotlib block diagrams")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

THEMES = {
    "02_vetpcr-chemodan": {
        "title": "ВетПЦР-Чемодан: электрическая схема",
        "blocks": [
            {"name": "LiPo 18650\n3.7V 3000mAh", "pos": (0, 5), "color": "#F59E0B"},
            {"name": "TPS63020\nDC-DC 3.3V", "pos": (2.5, 5), "color": "#10B981"},
            {"name": "nRF52840\nMCU/BLE", "pos": (5, 3), "color": "#2563EB"},
            {"name": "DRV8837\nH-bridge", "pos": (2.5, 2), "color": "#8B5CF6"},
            {"name": "TEC1-12706\nPeltier", "pos": (0, 2), "color": "#EF4444"},
            {"name": "OPT101×4\nFAM/HEX/ROX/Cy5", "pos": (7.5, 5), "color": "#EC4899"},
            {"name": "NEO-6M\nGPS", "pos": (7.5, 1), "color": "#6366F1"},
            {"name": "MAX31855\nThermocouple", "pos": (5, 1), "color": "#14B8A6"},
        ],
        "connections": [
            (0, 1, "3.7V"), (1, 2, "3.3V"), (2, 3, "PWM/DIR"), (3, 4, "DC"),
            (5, 2, "ADC×4"), (6, 2, "UART"), (7, 2, "SPI"),
        ],
    },
    "03_parazit-kontrol": {
        "title": "Паразит-Контроль: электрическая схема",
        "blocks": [
            {"name": "USB-C\n5V 3A", "pos": (0, 4), "color": "#F59E0B"},
            {"name": "Raspberry Pi\n4B", "pos": (2.5, 4), "color": "#2563EB"},
            {"name": "IMX477\nHQ Camera", "pos": (5, 5), "color": "#EC4899"},
            {"name": "PCA9685\nPWM Driver", "pos": (5, 3), "color": "#8B5CF6"},
            {"name": "WS2812B×24\nLED Ring", "pos": (7.5, 3), "color": "#10B981"},
            {"name": "ST7789\n1.3\" IPS", "pos": (2.5, 1), "color": "#14B8A6"},
            {"name": "Button\nStart/Stop", "pos": (5, 1), "color": "#EF4444"},
        ],
        "connections": [
            (0, 1, "5V USB"), (1, 2, "CSI-2"), (1, 3, "I2C"),
            (3, 4, "PWM"), (1, 5, "SPI"), (6, 1, "GPIO"),
        ],
    },
    "04_optikozor-2-0": {
        "title": "ОптикоЗор-2,0: электрическая схема",
        "blocks": [
            {"name": "24V PSU\nIndustrial", "pos": (0, 4), "color": "#F59E0B"},
            {"name": "Zynq US+\nFPGA", "pos": (2.5, 4), "color": "#2563EB"},
            {"name": "4K CMOS\nLine Scan", "pos": (5, 5), "color": "#EC4899"},
            {"name": "ADS8860\n16-bit ADC", "pos": (5, 3), "color": "#8B5CF6"},
            {"name": "OSRAM\nHyper LED", "pos": (7.5, 5), "color": "#10B981"},
            {"name": "TMC2209\nStepper Dr.", "pos": (7.5, 3), "color": "#14B8A6"},
            {"name": "NEMA 17\nStepper", "pos": (7.5, 1), "color": "#EF4444"},
            {"name": "KSZ9031\nGbE PHY", "pos": (2.5, 1), "color": "#6366F1"},
        ],
        "connections": [
            (0, 1, "12V→DCDC"), (1, 2, "LVDS"), (1, 3, "SPI"),
            (1, 4, "SPI"), (1, 5, "UART"), (5, 6, "STEP/DIR"),
            (1, 7, "RGMII"),
        ],
    },
    "05_cehgid-5": {
        "title": "ЦехГид-5: электрическая схема",
        "blocks": [
            {"name": "LiFePO₄\n12V 6Ah", "pos": (0, 5), "color": "#F59E0B"},
            {"name": "12V BMS\nProtection", "pos": (2, 5), "color": "#10B981"},
            {"name": "Raspberry Pi\n4B", "pos": (4.5, 3.5), "color": "#2563EB"},
            {"name": "RPLIDAR A3\n360° 16m", "pos": (7, 5), "color": "#EC4899"},
            {"name": "BNO055\nIMU 9-DOF", "pos": (7, 3), "color": "#8B5CF6"},
            {"name": "SHT45+SGP41\n+SCD41+TSL2591", "pos": (7, 1), "color": "#14B8A6"},
            {"name": "SX1276\nLoRa 868MHz", "pos": (4.5, 1), "color": "#6366F1"},
            {"name": "L298N\nMotor Driver", "pos": (2, 2), "color": "#EF4444"},
            {"name": "JGB37×4\nDC Motors", "pos": (0, 2), "color": "#F97316"},
        ],
        "connections": [
            (0, 1, "12V"), (1, 2, "5V USB"), (2, 3, "USB"),
            (2, 4, "I2C"), (2, 5, "I2C×4"), (2, 6, "SPI"),
            (2, 7, "GPIO PWM"), (7, 8, "DC 12V"),
        ],
    },
    "06_smena-prognoz-40": {
        "title": "Смена-Прогноз-40: электрическая схема",
        "blocks": [
            {"name": "LiPo 3.7V\n250mAh", "pos": (0, 4), "color": "#F59E0B"},
            {"name": "TPS62740\nDC-DC 1.8/3.3V", "pos": (2, 4), "color": "#10B981"},
            {"name": "nRF52832\nMCU BLE 5.0", "pos": (4.5, 3), "color": "#2563EB"},
            {"name": "AFE4404\nPPG Frontend", "pos": (7, 4), "color": "#EC4899"},
            {"name": "Green+IR\nLEDs 525/940nm", "pos": (9, 4), "color": "#8B5CF6"},
            {"name": "MLX90614\nIR Temp", "pos": (7, 2), "color": "#14B8A6"},
            {"name": "AD5940\nEDA/BIOZ", "pos": (7, 0), "color": "#6366F1"},
            {"name": "LIS2DH12\nAccel 3-axis", "pos": (4.5, 0), "color": "#EF4444"},
            {"name": "ERM Motor\nVibration", "pos": (2, 1), "color": "#F97316"},
        ],
        "connections": [
            (0, 1, "3.7V"), (1, 2, "3.3V/1.8V"), (2, 3, "SPI"),
            (3, 4, "LED drive"), (2, 5, "I2C"), (2, 6, "SPI"),
            (2, 7, "I2C"), (2, 8, "GPIO+MOSFET"),
        ],
    },
}

for topic, data in THEMES.items():
    out_dir = os.path.join(REPO, topic, "01_zadel/patent_PM/chertezhi")
    os.makedirs(out_dir, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(-1, 11); ax.set_ylim(-1, 7)
    ax.set_aspect('equal')
    ax.set_title(data["title"], fontsize=14, fontweight='bold')
    ax.axis('off')
    
    # Draw blocks
    block_rects = []
    for b in data["blocks"]:
        rect = mpatches.FancyBboxPatch(
            (b["pos"][0]-0.8, b["pos"][1]-0.5), 1.6, 1.0,
            boxstyle="round,pad=0.1", facecolor=b["color"], alpha=0.2,
            edgecolor=b["color"], linewidth=2
        )
        ax.add_patch(rect)
        ax.text(b["pos"][0], b["pos"][1], b["name"],
                ha='center', va='center', fontsize=7, fontweight='bold')
        block_rects.append(b)
    
    # Draw connections
    for src_idx, dst_idx, label in data["connections"]:
        src = block_rects[src_idx]
        dst = block_rects[dst_idx]
        ax.annotate("",
            xy=(dst["pos"][0], dst["pos"][1]),
            xytext=(src["pos"][0], src["pos"][1]),
            arrowprops=dict(arrowstyle="->", color="#374151", lw=1.5),
        )
        mx = (src["pos"][0] + dst["pos"][0]) / 2
        my = (src["pos"][1] + dst["pos"][1]) / 2
        ax.text(mx, my+0.15, label, fontsize=6, ha='center', color='#374151',
                bbox=dict(boxstyle='round,pad=0.1', facecolor='white', alpha=0.8))
    
    # Legend
    ax.text(0.5, -0.5, "Примечание: схема упрощена. Полная электрическая схема — в конструкторской документации.",
            fontsize=7, style='italic', color='#6B7280')
    
    plt.tight_layout()
    fname = f"schematic_{topic.split('_')[0]}.png"
    plt.savefig(os.path.join(out_dir, fname), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  {topic}: {fname} ✓")

print("\n✓ Все PNG-схемы Т02–Т06 созданы.")