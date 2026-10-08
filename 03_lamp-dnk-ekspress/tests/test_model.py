import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_raschety'))
from model import *

def test_ntc_conversion():
    T = ntc_to_temp(10000.0)
    assert 24 < T < 26

def test_pid_output_range():
    out = pid_control(25.0, 65.0, 1.0)
    assert 0 <= out <= 100

def test_lamp_amplification():
    c = lamp_amplification(100, 45)
    assert c > 1e6

def test_hnb_positive():
    assert hnb_detect(0.65, 0.40, 1.2) == 1

def test_hnb_negative():
    assert hnb_detect(0.40, 0.65, 1.2) == 0

def test_pid_convergence():
    T = 25.0
    for _ in range(300):
        duty = pid_control(T, 65.0, 1.0)
        Q_in = 5.0 * duty * 0.01
        Q_loss = 0.02 * (T - 25.0)
        T += (Q_in - Q_loss) * 1.0 / 2.0
    assert abs(T - 65.0) < 2.0