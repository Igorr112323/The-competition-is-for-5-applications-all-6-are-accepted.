import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_raschety'))
from model import run_spectrometer_model, run_modulator_model

def test_nh3_detected():
    r = run_spectrometer_model()
    assert "NH3" in r

def test_r2_above_threshold():
    r = run_spectrometer_model()
    for name, data in r.items():
        assert data["R2"] > 0.9, f"{name} R2={data['R2']}"

def test_mdl_positive():
    r = run_spectrometer_model()
    for name, data in r.items():
        assert data["MDL_ppb"] > 0

def test_modulator_emissivity():
    r = run_modulator_model()
    assert 0 < r["emissivity"] <= 1.0

def test_modulator_tau():
    r = run_modulator_model()
    assert 0 < r["tau_total"] <= 1.0