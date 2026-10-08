import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_raschety'))
from model import run_mic_model, run_fft_model, run_beamforming_model, run_dsp_model

def test_mic_sensitivity():
    r = run_mic_model()
    assert r["SNR_dBA"] == 65

def test_mic_voice_snr():
    r = run_mic_model()
    assert r["SNR_voice_dB"] > 0

def test_fft_resolution():
    r = run_fft_model()
    assert r["freq_res_Hz"] < 20

def test_fft_formants():
    r = run_fft_model()
    assert 400 < r["formants_Hz"][0] < 600

def test_beam_gain():
    r = run_beamforming_model()
    assert r["array_gain_dB"] > 0

def test_dsp_latency():
    r = run_dsp_model()
    assert r["latency_ms"] < 100