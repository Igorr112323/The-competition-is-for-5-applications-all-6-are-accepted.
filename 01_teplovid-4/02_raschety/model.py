import math

def run_thermal_model():
    NETD = 0.050
    d_aperture = 25e-3
    f = 50e-3
    fov_h = 2 * math.degrees(math.atan(12.8e-3 / (2 * f)))
    fov_v = 2 * math.degrees(math.atan(9.6e-3 / (2 * f)))
    IFOV = (fov_h / 640) * (math.pi / 180)
    pixels = 640 * 512

    T_bg = 288.15
    T_tar = 305.15
    T_air = 283.15
    delta_T = T_tar - T_bg
    d_target = 0.30
    tau_atm = math.exp(-0.02 * 0.5)
    SNR = delta_T * tau_atm / NETD
    R_max = math.sqrt(d_target**2 * SNR * IFOV**2 * tau_atm / (4 * NETD))

    T_cold = 253.15
    T_hot = 333.15
    steps = 20
    T_array = []
    T_curr = T_cold
    dt = 1.0
    for i in range(steps):
        Q_in = 0.02 * (T_hot - T_curr)
        Q_out = 0.005 * (T_curr - T_air)
        dT = (Q_in - Q_out) * dt / 500.0
        T_curr += dT
        T_array.append(T_curr - 273.15)

    fov_diag = math.sqrt(fov_h**2 + fov_v**2)
    ground_res_h = 2 * 100 * math.tan(math.radians(fov_h / 2)) / 640
    ground_res_v = 2 * 100 * math.tan(math.radians(fov_v / 2)) / 512

    payload_power = 2.5
    flight_speed = 8.0
    survey_width = 2 * 100 * math.tan(math.radians(fov_h / 2))
    area_rate = survey_width * flight_speed / 10000

    n_spectral = 64
    snr_spectral = delta_T * tau_atm / (NETD / math.sqrt(n_spectral))

    T_hum = 309.15
    T_veg = 285.15
    T_soil = 290.15
    T_water = 280.15
    c_hum = (T_hum - T_bg) * tau_atm / NETD
    c_veg = (T_veg - T_bg) * tau_atm / NETD
    c_soil = (T_soil - T_bg) * tau_atm / NETD
    c_water = (T_water - T_bg) * tau_atm / NETD

    return {
        "NETD_mK": round(NETD * 1000, 1),
        "aperture_mm": round(d_aperture * 1000, 1),
        "focal_length_mm": round(f * 1000, 1),
        "FOV_h_deg": round(fov_h, 2),
        "FOV_v_deg": round(fov_v, 2),
        "IFOV_mrad": round(IFOV * 1000, 3),
        "resolution": f"{640}x{512}",
        "pixels": pixels,
        "T_target_C": round(T_tar - 273.15, 1),
        "T_background_C": round(T_bg - 273.15, 1),
        "delta_T_K": round(delta_T, 1),
        "atmospheric_transmission": round(tau_atm, 4),
        "SNR": round(SNR, 1),
        "detection_range_m": round(R_max, 1),
        "thermal_curve": [round(t, 2) for t in T_array],
        "ground_resolution_100m_cm": round(ground_res_h * 100, 1),
        "survey_area_rate_ha_h": round(area_rate, 2),
        "SNR_spectral_64": round(snr_spectral, 1),
        "contrast_human": round(c_hum, 1),
        "contrast_vegetation": round(c_veg, 1),
        "contrast_soil": round(c_soil, 1),
        "contrast_water": round(c_water, 1),
    }


def run_lidar_model():
    wavelength = 905e-9
    P_tx = 75.0
    d_tx = 12e-3
    d_rx = 25e-3
    theta_beam = 2.44 * wavelength / d_tx
    A_rx = math.pi * (d_rx / 2)**2

    rho = 0.3
    R = 100.0
    tau_atm = math.exp(-0.1 * R / 1000)
    tau_opt = 0.85
    P_rx = (P_tx * rho * A_rx * tau_atm * tau_opt) / (math.pi * R**2)

    NEP = 1e-12
    snr = P_rx / NEP
    R_max = math.sqrt(P_tx * rho * A_rx * tau_opt / (math.pi * NEP * 10))

    scan_rate = 24000
    n_points = 720

    c = 3e8
    range_res = c / (2 * 1e9)
    accuracy = 0.02

    h_agb = 20.0
    n_returns = 3
    h_layers = [h_agb * (i + 1) / n_returns for i in range(n_returns)]

    power_system = 8.0
    weight = 0.35

    return {
        "wavelength_nm": round(wavelength * 1e9, 0),
        "beam_divergence_mrad": round(theta_beam * 1000, 2),
        "P_rx_100m_nW": round(P_rx * 1e9, 3),
        "SNR_100m_dB": round(10 * math.log10(snr), 1),
        "max_range_m": round(R_max, 0),
        "scan_rate_pps": scan_rate,
        "points_per_scan": n_points,
        "range_resolution_m": round(range_res, 3),
        "accuracy_m": accuracy,
        "agb_height_layers_m": h_layers,
        "power_W": power_system,
        "weight_kg": weight,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("ТЕПЛОВИЗИОННАЯ МОДЕЛЬ (NETD/SNR/КОНТРАСТ)")
    print("=" * 60)
    r1 = run_thermal_model()
    for k, v in r1.items():
        print(f"  {k}: {v}")

    print()
    print("=" * 60)
    print("LiDAR МОДЕЛЬ (ДАЛЬНОСТЬ/ТОЧНОСТЬ/СКАНИРОВАНИЕ)")
    print("=" * 60)
    r2 = run_lidar_model()
    for k, v in r2.items():
        print(f"  {k}: {v}")