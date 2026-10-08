import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_raschety'))
from model import run_thermal_model, run_lidar_model

def test_thermal_netd():
    r = run_thermal_model()
    assert r["NETD_mK"] == 50.0

def test_thermal_snr():
    r = run_thermal_model()
    assert r["SNR"] > 100

def test_thermal_range():
    r = run_thermal_model()
    assert r["detection_range_m"] > 50

def test_lidar_points():
    r = run_lidar_model()
    assert r["points_per_scan"] == 720

def test_lidar_accuracy():
    r = run_lidar_model()
    assert r["accuracy_m"] <= 0.05