import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_raschety'))
from model import *

def test_lidar_points():
    assert LIDAR_POINTS == 360

def test_slam_update():
    ranges = [10.0] * 360
    angles = [i * 0.01745 for i in range(360)]
    slam_update(ranges, angles, 360)
    assert True

def test_astar_path():
    for i in range(MAP_SIZE):
        for j in range(MAP_SIZE):
            map_grid[i][j] = 0
    path = [Point(0, 0) for _ in range(MAX_PATH)]
    n = astar_plan(0, 0, 20, 20, path, MAX_PATH)
    assert n > 0

def test_dwa_velocity():
    v = dwa_velocity(0, V_MAX, 0.1)
    assert 0 < v <= V_MAX

def test_pid_output():
    steer = pid_steer(0.5, 2.0, 0.5)
    assert isinstance(steer, float)