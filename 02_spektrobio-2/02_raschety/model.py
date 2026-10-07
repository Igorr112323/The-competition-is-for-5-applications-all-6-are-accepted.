import math
import random

def run_spectrometer_model():
    lambda_min = 3.0e-6
    lambda_max = 12.0e-6
    n_points = 256
    delta_lambda = (lambda_max - lambda_min) / n_points
    SNR_dB = 72
    SNR_lin = 10**(SNR_dB / 10)
    NEP = 5e-12

    analytes = {
        "NH3": {"lambda_peak": 10.3e-6, "sigma": 2.1e-20, "ppb_healthy": 500, "ppb_disease": 2500},
        "NO": {"lambda_peak": 5.26e-6, "sigma": 6.8e-21, "ppb_healthy": 10, "ppb_disease": 80},
        "H2S": {"lambda_peak": 7.73e-6, "sigma": 3.5e-21, "ppb_healthy": 0.5, "ppb_disease": 10},
        "CH4": {"lambda_peak": 3.31e-6, "sigma": 8.6e-21, "ppb_healthy": 1800, "ppb_disease": 8000},
    }

    L = 0.10
    P0 = 1.0e-3
    T = 296.15
    k_B = 1.381e-23

    results = {}
    for name, a in analytes.items():
        C = a["ppb_healthy"] * 1e-9 * (101325 / (k_B * T))
        alpha = a["sigma"] * C
        tau_peak = math.exp(-alpha * L)
        absorbance = -math.log10(tau_peak)
        P_rx = P0 * tau_peak
        SNR_peak = P_rx / NEP
        C_mdl = NEP / (P0 * a["sigma"] * L)
        C_mdl_ppb = C_mdl * k_B * T / 101325 * 1e9

        X = []
        Y = []
        for i in range(50):
            c_ppb = a["ppb_healthy"] + i * (a["ppb_disease"] - a["ppb_healthy"]) / 49
            c_m = c_ppb * 1e-9 * (101325 / (k_B * T))
            alpha_i = a["sigma"] * c_m
            tau_i = math.exp(-alpha_i * L)
            A_i = -math.log10(tau_i) + random.gauss(0, 0.001)
            X.append(c_ppb)
            Y.append(A_i)

        n = len(X)
        sum_x = sum(X)
        sum_y = sum(Y)
        sum_xy = sum(x * y for x, y in zip(X, Y))
        sum_x2 = sum(x**2 for x in X)
        denom = n * sum_x2 - sum_x**2
        slope = (n * sum_xy - sum_x * sum_y) / denom
        intercept = (sum_y * sum_x2 - sum_x * sum_xy) / denom
        Y_pred = [slope * x + intercept for x in X]
        ss_res = sum((y - yp)**2 for y, yp in zip(Y, Y_pred))
        ss_tot = sum((y - sum_y / n)**2 for y in Y)
        R2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0

        results[name] = {
            "lambda_peak_um": a["lambda_peak"] * 1e6,
            "sigma_m2": a["sigma"],
            "absorbance_peak": round(absorbance, 6),
            "SNR_peak_dB": round(10 * math.log10(SNR_peak), 1) if SNR_peak > 0 else 0,
            "MDL_ppb": round(C_mdl_ppb, 2),
            "R2": round(R2, 4),
            "slope": slope,
        }

    return results


def run_modulator_model():
    T_chopper = 300.0
    T_ref = 296.0
    delta_T = T_chopper - T_ref
    emissivity = 0.95
    sigma_SB = 5.67e-8
    P_rad = emissivity * sigma_SB * T_chopper**4
    mod_freq = 10.0
    mod_depth = 0.85

    L_arms = 0.15
    T_base = 296.15
    k_al = 237.0
    A_cross = 1e-6
    Q_cond = k_al * A_cross * delta_T / L_arms
    t_settle = 4.0

    d_golay = 8e-3
    f_golay = 25e-3
    F_fo = f_golay / d_golay

    tau_window = 0.92
    n_windows = 2
    tau_total = tau_window ** n_windows

    return {
        "T_chopper_K": T_chopper,
        "T_ref_K": T_ref,
        "delta_T_K": delta_T,
        "emissivity": emissivity,
        "P_rad_W_m2": round(P_rad, 1),
        "mod_freq_Hz": mod_freq,
        "mod_depth": mod_depth,
        "L_arms_mm": L_arms * 1000,
        "Q_cond_W": round(Q_cond, 4),
        "t_settle_s": t_settle,
        "d_golay_mm": d_golay * 1000,
        "f_golay_mm": f_golay * 1000,
        "F_number": round(F_fo, 1),
        "tau_window": tau_window,
        "tau_total": round(tau_total, 4),
    }


if __name__ == "__main__":
    print("=" * 60)
    print("СПЕКТРОМЕТРИЧЕСКАЯ МОДЕЛЬ (FTIR/Beer-Lambert)")
    print("=" * 60)
    r1 = run_spectrometer_model()
    for name, data in r1.items():
        print(f"\n  {name}:")
        for k, v in data.items():
            print(f"    {k}: {v}")

    print()
    print("=" * 60)
    print("МОДЕЛЬ МОДУЛЯТОРА (Михельсона/Голея)")
    print("=" * 60)
    r2 = run_modulator_model()
    for k, v in r2.items():
        print(f"  {k}: {v}")