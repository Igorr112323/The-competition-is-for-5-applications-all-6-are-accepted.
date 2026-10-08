import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_raschety'))
from model import run_camera_model, run_yolo_model, run_stereo_model, run_edge_detection_model

def test_camera_fov():
    r = run_camera_model()
    assert 40 < r["FOV_h"] < 60

def test_camera_gsd():
    r = run_camera_model()
    assert r["GSD_50m_cm"] > 0

def test_yolo_macs():
    r = run_yolo_model()
    assert r["total_MMACS"] > 0

def test_yolo_inference():
    r = run_yolo_model()
    assert r["inference_ms"] < 100

def test_stereo_depth():
    r = run_stereo_model()
    assert r["z_min_m"] < r["z_max_m"]

def test_edge_snr():
    r = run_edge_detection_model()
    assert r["SNR_veg"] > 5