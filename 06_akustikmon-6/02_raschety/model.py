import math
SAMPLE_RATE = 48000
FFT_SIZE = 4096
FREQ_RESOLUTION = SAMPLE_RATE / FFT_SIZE
TIME_WINDOW_MS = FFT_SIZE / SAMPLE_RATE * 1000
SNR_DB = 65
F0_MIN = 60
F0_MAX = 600
BREATHING_RATE_MIN = 8
BREATHING_RATE_MAX = 40
COUGH_FREQ_MIN = 100
COUGH_FREQ_MAX = 1000
MFCC_FEATURES = 13
ML_CLASSES = 5
ML_ACCURACY = 0.92
MASS_G = 30
BATTERY_H = 100
COST = 50000
MARKET = 100000
print("=== АкустикМон-6 ===")
print(f"Микрофон: {SAMPLE_RATE/1000:.0f} кГц, SNR={SNR_DB} дБ")
print(f"FFT: {FFT_SIZE} точек, разрешение={FREQ_RESOLUTION:.1f} Гц, окно={TIME_WINDOW_MS:.0f} мс")
print(f"F0 голоса: {F0_MIN}-{F0_MAX} Гц")
print(f"Дыхание: {BREATHING_RATE_MIN}-{BREATHING_RATE_MAX} в мин")
print(f"Кашель: {COUGH_FREQ_MIN}-{COUGH_FREQ_MAX} Гц")
print(f"MFCC: {MFCC_FEATURES} коэф., ML: {ML_CLASSES} классов, точность={ML_ACCURACY*100:.0f}%")
print(f"Масса: {MASS_G} г, автономность: {BATTERY_H} ч")
print(f"Стоимость: {COST/1e3:.0f} тыс. ₽")
print(f"Рынок: {MARKET} × {COST/1e3:.0f} тыс. = {MARKET*COST/1e9:.0f} млрд ₽")
