#!/usr/bin/env python3
"""
Синтетические датасеты для тем 03-06.
"""
import numpy as np, os, csv, json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

REPO = "/home/user/The-competition-is-for-5-applications-all-6-are-accepted."

def save_csv(path, headers, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(headers)
        for r in rows: w.writerow(r)

np.random.seed(42)

# ── Т03: Синтетический датасет личинок ──────────────────────────
print("Т03: датасет личинок...")
ds_dir = os.path.join(REPO, "03_parazit-kontrol/01_zadel/dataset_synthetic/images")
os.makedirs(ds_dir, exist_ok=True)

labels = []
for i in range(200):
    n_larvae = np.random.poisson(2)  # среднее 2 личинки на изображение
    w, h = 640, 480
    objs = []
    for j in range(min(n_larvae, 5)):
        cx = np.random.randint(50, w-50)
        cy = np.random.randint(50, h-50)
        a = np.random.randint(15, 40)  # полуось a
        b = np.random.randint(5, 15)   # полуось b
        angle = np.random.uniform(0, 180)
        objs.append({"cx": cx, "cy": cy, "a": a, "b": b, "angle": angle, "class": "Eustrongylides"})
    labels.append({"image": f"synth_{i:04d}.png", "width": w, "height": h, "objects": objs})
    
    # Создание простого изображения (эллипсы на тёмном фоне)
    img = np.ones((h, w), dtype=np.uint8) * 30
    for obj in objs:
        yy, xx = np.ogrid[:h, :w]
        cos_a = np.cos(np.radians(obj['angle']))
        sin_a = np.sin(np.radians(obj['angle']))
        dx = xx - obj['cx']; dy = yy - obj['cy']
        rx = dx * cos_a + dy * sin_a
        ry = -dx * sin_a + dy * cos_a
        mask = (rx/obj['a'])**2 + (ry/obj['b'])**2 <= 1
        img[mask] = np.random.randint(120, 200)
    
    plt.imsave(os.path.join(ds_dir, f"synth_{i:04d}.png"), img, cmap='gray')

with open(os.path.join(REPO, "03_parazit-kontrol/01_zadel/dataset_synthetic/labels.json"), 'w') as f:
    json.dump(labels, f, indent=2)
print(f"  Т03: {len(labels)} изображений + labels.json ✓")

# ── Т04: Синтетические траектории БПЛА ──────────────────────────
print("Т04: траектории...")
traj_rows = []
for flight in range(50):
    t = np.linspace(0, 60, 600)  # 60 с, 10 Гц
    v0 = np.random.uniform(5, 15)  # м/с
    w = np.random.uniform(0, 10)   # м/с ветер
    w_dir = np.random.uniform(0, 360)
    Cd = 0.5; A = 0.1; m = np.random.uniform(0.25, 5.0); rho = 1.225
    x = np.zeros_like(t); y = np.zeros_like(t); z = np.zeros_like(t)
    vx = v0; vy = 0; vz = 0
    wx = w * np.cos(np.radians(w_dir)); wy = w * np.sin(np.radians(w_dir))
    for i in range(1, len(t)):
        dt = t[i] - t[i-1]
        vrx, vry = vx - wx, vy - wy
        vr = np.sqrt(vrx**2 + vry**2)
        Fdx = -0.5*rho*Cd*A*vr*vrx; Fdy = -0.5*rho*Cd*A*vr*vry
        ax_d = Fdx/m; ay_d = Fdy/m
        vx += ax_d*dt; vy += ay_d*dt
        x[i] = x[i-1] + vx*dt; y[i] = y[i-1] + vy*dt
        z[i] = 50 + np.random.normal(0, 0.1)  # высота ~50 м
    for i in range(len(t)):
        traj_rows.append([flight, round(t[i],2), round(x[i],2), round(y[i],2), round(z[i],2)])

save_csv(os.path.join(REPO, "04_optikozor-2-0/02_raschety/synth_trajectories.csv"),
         ["Полёт", "Время (с)", "X (м)", "Y (м)", "Z (м)"], traj_rows)
print(f"  Т04: 50 траекторий ({len(traj_rows)} точек) ✓")

# ── Т05: Синтетическая карта цеха ───────────────────────────────
print("Т05: карта цеха...")
fig, ax = plt.subplots(figsize=(16, 4))
# Цех 100×18 м
ax.add_patch(plt.Rectangle((0, 0), 100, 18, fill=False, edgecolor='#333', lw=2))
# Линии поения (якоря)
for y_p in [4, 9, 14]:
    ax.plot([5, 95], [y_p, y_p], '#2563EB', lw=2, label='Линия поения' if y_p==4 else '')
# Линии кормления
for y_f in [2, 16]:
    ax.plot([10, 90], [y_f, y_f], '#F59E0B', lw=2, label='Линия кормления' if y_f==2 else '')
# Секции пола
for x_s in range(10, 100, 10):
    ax.axvline(x_s, color='#E5E7EB', lw=0.5)
# Проходы
ax.plot([50, 50], [0, 18], '#10B981', lw=3, label='Центральный проход')
# Робот-носитель
robot_x, robot_y = 25, 7
ax.plot(robot_x, robot_y, 'ro', ms=10, label='Робот')
# Зона обзора лидара
circle = plt.Circle((robot_x, robot_y), 12, fill=False, color='#EF4444', ls='--', label='Зона обзора лидара')
ax.add_patch(circle)
ax.set_xlabel('Длина цеха (м)'); ax.set_ylabel('Ширина (м)')
ax.set_title('ЦехГид-5: синтетическая карта цеха напольного содержания (100×18 м)')
ax.legend(fontsize=8, loc='upper right'); ax.grid(True, alpha=0.3); ax.set_aspect('equal')
plt.tight_layout()
plt.savefig(os.path.join(REPO, "05_cehgid-5/03_grafika/slam_map_synthetic.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

# CSV якорей
anchors = []
for y_p in [4, 9, 14]:
    for x in range(5, 96, 5):
        anchors.append(["линия_поения", x, y_p])
for y_f in [2, 16]:
    for x in range(10, 91, 10):
        anchors.append(["линия_кормления", x, y_f])
for x_s in range(10, 100, 10):
    for y in range(0, 19, 3):
        anchors.append(["секция_пола", x_s, y])
save_csv(os.path.join(REPO, "05_cehgid-5/02_raschety/slam_anchors.csv"),
         ["Тип якоря", "X (м)", "Y (м)"], anchors)
print(f"  Т05: карта + {len(anchors)} якорей ✓")

# ── Т06: Синтетические физиологические сигналы ──────────────────
print("Т06: физиология...")
physio_rows = []
t_total = 8 * 3600  # 8 часов
dt = 1.0
n = int(t_total / dt)
t_arr = np.arange(n) * dt

# Базовые сигналы
hr_base = 75; hr_noise = 3
temp_base = 36.6; temp_noise = 0.1
gsr_base = 2.0; gsr_noise = 0.3

# События: перегрев в 2-3м и 5-6м часу
events = [(7200, 9000, "heat_stress"), (18000, 21000, "heat_stress")]

for i in range(0, n, 10):  # каждые 10 с
    t_h = t_arr[i] / 3600
    hr = hr_base + np.random.normal(0, hr_noise)
    temp = temp_base + np.random.normal(0, temp_noise)
    gsr = gsr_base + np.random.normal(0, gsr_noise)
    accel = np.random.normal(0, 0.05)
    
    for (t_start, t_end, event) in events:
        if t_start <= t_arr[i] <= t_end:
            progress = (t_arr[i] - t_start) / (t_end - t_start)
            hr += 15 * progress + np.random.normal(0, 2)
            temp += 0.8 * progress + np.random.normal(0, 0.05)
            gsr += 1.5 * progress + np.random.normal(0, 0.2)
    
    physio_rows.append([round(t_arr[i], 0), round(hr, 1), round(temp, 2),
                        round(gsr, 2), round(accel, 3), 1 if any(s <= t_arr[i] <= e for s,e,_ in events) else 0])

save_csv(os.path.join(REPO, "06_smena-prognoz-40/02_raschety/synth_physio.csv"),
         ["Время (с)", "ЧСС (уд/мин)", "T_кожи (°C)", "КГР (мкСм)", "Акселерометр (g)", "Событие"],
         physio_rows)

# График
fig, axes = plt.subplots(3, 1, figsize=(14, 8), sharex=True)
t_h = t_arr[::10] / 3600
for (t_start, t_end, _) in events:
    for ax in axes:
        ax.axvspan(t_start/3600, t_end/3600, alpha=0.15, color='#EF4444')

axes[0].plot(t_h, [r[1] for r in physio_rows], '#2563EB', lw=0.5)
axes[0].set_ylabel('ЧСС (уд/мин)'); axes[0].set_title('Смена-Прогноз-40: синтетические физиологические сигналы (8 ч)')
axes[0].grid(True, alpha=0.3)

axes[1].plot(t_h, [r[2] for r in physio_rows], '#EF4444', lw=0.5)
axes[1].set_ylabel('T_кожи (°C)'); axes[1].grid(True, alpha=0.3)

axes[2].plot(t_h, [r[3] for r in physio_rows], '#10B981', lw=0.5)
axes[2].set_ylabel('КГР (мкСм)'); axes[2].set_xlabel('Время (ч)')
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(REPO, "06_smena-prognoz-40/03_grafika/T6_synth_physio.png"), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print(f"  Т06: {len(physio_rows)} точек + график ✓")

print("\n✓ Все синтетические датасеты созданы.")