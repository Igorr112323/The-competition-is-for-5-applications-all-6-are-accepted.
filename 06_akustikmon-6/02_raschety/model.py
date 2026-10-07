import math

def run_mic_model():
    sensitivity_dBV = -38
    sensitivity_VPa = 10**(sensitivity_dBV / 20)
    SNR_dBA = 65
    SNR_lin = 10**(SNR_dBA / 10)
    self_noise_dBSPL = 94 - SNR_dBA

    f_low = 20
    f_high = 20000
    n_octaves = math.log2(f_high / f_low)

    T = 293.15
    k_B = 1.381e-23
    R_mic = 2.2e3
    noise_thermal = math.sqrt(4 * k_B * T * R_mic)
    noise_thermal_dBuV = 20 * math.log10(noise_thermal * 1e6) if noise_thermal > 0 else 0

    P_ref = 20e-6
    voice_dBSPL = 60
    voice_Pa = P_ref * 10**(voice_dBSPL / 20)
    voice_V = voice_Pa * sensitivity_VPa

    breathing_dBSPL = 30
    breathing_Pa = P_ref * 10**(breathing_dBSPL / 20)
    breathing_V = breathing_Pa * sensitivity_VPa

    cough_dBSPL = 90
    cough_Pa = P_ref * 10**(cough_dBSPL / 20)
    cough_V = cough_Pa * sensitivity_VPa

    snr_voice = 20 * math.log10(voice_Pa / P_ref) - self_noise_dBSPL
    snr_breathing = 20 * math.log10(breathing_Pa / P_ref) - self_noise_dBSPL
    snr_cough = 20 * math.log10(cough_Pa / P_ref) - self_noise_dBSPL

    return {
        "sensitivity_dBV": sensitivity_dBV,
        "sensitivity_mV_Pa": round(sensitivity_VPa * 1000, 3),
        "SNR_dBA": SNR_dBA,
        "self_noise_dBSPL": round(self_noise_dBSPL, 1),
        "freq_range_Hz": f"{f_low}-{f_high}",
        "n_octaves": round(n_octaves, 1),
        "thermal_noise_nV": round(noise_thermal * 1e9, 2),
        "voice_60dBSPL_V": round(voice_V, 5),
        "breathing_30dBSPL_mV": round(breathing_V * 1000, 4),
        "cough_90dBSPL_V": round(cough_V, 4),
        "SNR_voice_dB": round(snr_voice, 1),
        "SNR_breathing_dB": round(snr_breathing, 1),
        "SNR_cough_dB": round(snr_cough, 1),
    }


def run_fft_model():
    fs = 44100
    N = 4096
    freq_res = fs / N
    duration = N / fs

    f0_voice = 120
    harmonics = 8
    f_harmonics = [f0_voice * (i + 1) for i in range(harmonics)]

    f0_breath = 0.2
    breath_cycles_per_min = f0_breath * 60

    formants = [500, 1500, 2500, 3500]

    f_cough_center = 500
    bw_cough = 800
    t_cough = 0.3
    n_fft_cough = int(t_cough * fs)
    freq_res_cough = fs / n_fft_cough

    mel_n = 40
    mel_low = 2595 * math.log10(1 + f_low_Hz / 700) if (f_low_Hz := 300) else 0
    mel_high = 2595 * math.log10(1 + 8000 / 700)
    mel_points = [mel_low + i * (mel_high - mel_low) / (mel_n + 1) for i in range(mel_n + 2)]
    hz_points = [700 * (10**(m / 2595) - 1) for m in mel_points]

    mfcc_n = 13
    mfcc_frames = 98

    return {
        "fs_Hz": fs,
        "N_FFT": N,
        "freq_res_Hz": round(freq_res, 3),
        "frame_duration_ms": round(duration * 1000, 2),
        "voice_f0_Hz": f0_voice,
        "harmonics_Hz": f_harmonics,
        "breath_rate_per_min": breath_cycles_per_min,
        "formants_Hz": formants,
        "cough_center_Hz": f_cough_center,
        "cough_bandwidth_Hz": bw_cough,
        "cough_duration_ms": t_cough * 1000,
        "mel_bands": mel_n,
        "mfcc_coeffs": mfcc_n,
        "mfcc_frames": mfcc_frames,
    }


def run_beamforming_model():
    n_mics = 4
    d_mic = 0.04
    c = 343.0
    f_target = 1000
    wavelength = c / f_target
    d_ratio = d_mic / wavelength

    theta_target = 30
    theta_null = 90
    d_target = n_mics * d_mic * math.sin(math.radians(theta_target)) / wavelength
    d_null = n_mics * d_mic * math.sin(math.radians(theta_null)) / wavelength

    array_gain_dB = 10 * math.log10(n_mics)

    f_max_unaliased = c / (2 * d_mic)
    beam_width = math.degrees(2 * math.asin(0.886 * wavelength / (n_mics * d_mic))) if n_mics * d_mic > wavelength else 180

    d_source = 1.5
    t_propagation = d_source / c
    t_propagation_us = t_propagation * 1e6

    snr_enhancement_dB = 10 * math.log10(n_mics)

    return {
        "n_mics": n_mics,
        "d_mic_cm": d_mic * 100,
        "wavelength_m": round(wavelength, 3),
        "d_ratio": round(d_ratio, 3),
        "array_gain_dB": array_gain_dB,
        "f_max_unaliased_Hz": f_max_unaliased,
        "beam_width_deg": round(beam_width, 1),
        "propagation_delay_us": round(t_propagation_us, 1),
        "SNR_enhancement_dB": snr_enhancement_dB,
    }


def run_dsp_model():
    fs = 44100
    order_hpf = 4
    f_cutoff_hpf = 80
    gain_hpf_dB = -20 * math.log10(1 + (f_cutoff_hpf / 20)**(2 * order_hpf))

    f_notch = 50
    Q_notch = 30
    bw_notch = f_notch / Q_notch

    frame_ms = 25
    hop_ms = 10
    frame_samples = int(frame_ms * fs / 1000)
    hop_samples = int(hop_ms * fs / 1000)

    nfft = 512
    mel_n = 40
    mfcc_n = 13

    vad_energy_thresh_dB = -40
    vad_zcr_thresh = 0.1

    latency_ms = frame_ms + hop_ms

    return {
        "HPF_order": order_hpf,
        "HPF_cutoff_Hz": f_cutoff_hpf,
        "notch_freq_Hz": f_notch,
        "notch_Q": Q_notch,
        "notch_bw_Hz": round(bw_notch, 2),
        "frame_ms": frame_ms,
        "hop_ms": hop_ms,
        "frame_samples": frame_samples,
        "hop_samples": hop_samples,
        "nfft": nfft,
        "mel_bands": mel_n,
        "mfcc_coeffs": mfcc_n,
        "VAD_energy_thresh_dB": vad_energy_thresh_dB,
        "VAD_zcr_thresh": vad_zcr_thresh,
        "latency_ms": latency_ms,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("МОДЕЛЬ МИКРОФОНА (ЧУВСТВИТЕЛЬНОСТЬ/SNR)")
    print("=" * 60)
    r1 = run_mic_model()
    for k, v in r1.items():
        print(f"  {k}: {v}")

    print()
    print("=" * 60)
    print("МОДЕЛЬ FFT (СПЕКТР/ФОРМАНТЫ/MFCC)")
    print("=" * 60)
    r2 = run_fft_model()
    for k, v in r2.items():
        print(f"  {k}: {v}")

    print()
    print("=" * 60)
    print("МОДЕЛЬ БИМФОРМИНГА (МИКРОФОННАЯ РЕШЁТКА)")
    print("=" * 60)
    r3 = run_beamforming_model()
    for k, v in r3.items():
        print(f"  {k}: {v}")

    print()
    print("=" * 60)
    print("МОДЕЛЬ DSP (ФИЛЬТРЫ/VAD)")
    print("=" * 60)
    r4 = run_dsp_model()
    for k, v in r4.items():
        print(f"  {k}: {v}")