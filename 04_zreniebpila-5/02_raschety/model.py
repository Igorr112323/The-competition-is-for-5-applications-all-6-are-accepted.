import math

def run_camera_model():
    sensor_w = 7.2e-3
    sensor_h = 5.3e-3
    f = 8.5e-3
    fov_h = 2 * math.degrees(math.atan(sensor_w / (2 * f)))
    fov_v = 2 * math.degrees(math.atan(sensor_h / (2 * f)))

    res_w = 1920
    res_h = 1080
    pixel_w = sensor_w / res_w
    pixel_h = sensor_h / res_h
    gsd_50m = 2 * 50 * math.tan(pixel_w / (2 * f))
    gsd_100m = 2 * 100 * math.tan(pixel_w / (2 * f))

    fps = 30
    bandwidth_rgb = res_w * res_h * 3 * 8 * fps
    bandwidth_yolo = res_w * res_h * 3 * 8 * fps / 4

    return {
        "sensor_mm": f"{sensor_w*1000:.1f}x{sensor_h*1000:.1f}",
        "focal_mm": f * 1000,
        "FOV_h": round(fov_h, 1),
        "FOV_v": round(fov_v, 1),
        "resolution": f"{res_w}x{res_h}",
        "GSD_50m_cm": round(gsd_50m * 100, 2),
        "GSD_100m_cm": round(gsd_100m * 100, 2),
        "fps": fps,
        "bandwidth_Mbps": round(bandwidth_rgb / 1e6, 1),
    }


def run_yolo_model():
    input_size = 416
    n_classes = 80
    anchors_per_cell = 3

    layers = [
        {"name": "Conv1", "k": 3, "s": 1, "out": 16, "in_ch": 3},
        {"name": "Pool1", "k": 2, "s": 2, "out": 16, "in_ch": 16},
        {"name": "Conv2", "k": 3, "s": 1, "out": 32, "in_ch": 16},
        {"name": "Pool2", "k": 2, "s": 2, "out": 32, "in_ch": 32},
        {"name": "Conv3", "k": 3, "s": 1, "out": 64, "in_ch": 32},
        {"name": "Pool3", "k": 2, "s": 2, "out": 64, "in_ch": 64},
        {"name": "Conv4", "k": 3, "s": 1, "out": 128, "in_ch": 64},
        {"name": "Pool4", "k": 2, "s": 2, "out": 128, "in_ch": 128},
        {"name": "Conv5", "k": 3, "s": 1, "out": 256, "in_ch": 128},
        {"name": "Conv_out", "k": 1, "s": 1, "out": anchors_per_cell * (5 + n_classes), "in_ch": 256},
    ]

    total_macs = 0
    h, w = input_size, input_size
    for layer in layers:
        k = layer["k"]
        out_ch = layer["out"]
        in_ch = layer["in_ch"]
        macs = h * w * k * k * in_ch * out_ch
        total_macs += macs
        if "Pool" in layer["name"]:
            h //= 2
            w //= 2

    ops_per_mac = 2
    total_ops = total_macs * ops_per_mac

    accel_ops_per_s = 2.0e12
    inference_ms = total_ops / accel_ops_per_s * 1000

    conf_thresh = 0.5
    iou_thresh = 0.45
    nms_per_class = True

    map_coco = 0.58
    latency_total = inference_ms + 3.0

    return {
        "input_size": input_size,
        "n_classes": n_classes,
        "anchors_per_cell": anchors_per_cell,
        "total_MMACS": round(total_macs / 1e6, 1),
        "total_GOPS": round(total_ops / 1e9, 2),
        "inference_ms": round(inference_ms, 2),
        "latency_total_ms": round(latency_total, 1),
        "mAP_COCO": map_coco,
        "conf_thresh": conf_thresh,
        "iou_thresh": iou_thresh,
    }


def run_stereo_model():
    baseline = 0.12
    f_px = 800
    d_min = 0.5
    d_max = 50.0
    z_min = baseline * f_px / d_max
    z_max = baseline * f_px / d_min

    disparity_err = 0.5
    z_10m = baseline * f_px / (baseline * f_px / 10.0)
    z_10m_plus = baseline * f_px / (baseline * f_px / 10.0 - disparity_err)
    depth_err_10m = z_10m_plus - z_10m

    n_features = 500
    match_ratio = 0.75

    baseline_stereo = baseline
    f_fund = f_px
    epipolar_err = 1.0

    return {
        "baseline_m": baseline,
        "f_px": f_px,
        "z_min_m": round(z_min, 2),
        "z_max_m": round(z_max, 1),
        "depth_err_10m_m": round(depth_err_10m, 3),
        "n_features": n_features,
        "match_ratio": match_ratio,
        "epipolar_err_px": epipolar_err,
    }


def run_edge_detection_model():
    k_sobel = 3
    sigma_gauss = 1.4
    t_low = 50
    t_high = 100

    contrast_veg = 0.35
    contrast_soil = 0.22
    contrast_water = 0.45
    snr_veg = contrast_veg / 0.02
    snr_soil = contrast_soil / 0.02
    snr_water = contrast_water / 0.02

    hough_rho = 1
    hough_theta = math.pi / 180
    hough_thresh = 50

    contour_area_min = 50
    contour_circularity = 0.7

    return {
        "k_sobel": k_sobel,
        "sigma_gauss": sigma_gauss,
        "Canny_low": t_low,
        "Canny_high": t_high,
        "SNR_veg": round(snr_veg, 1),
        "SNR_soil": round(snr_soil, 1),
        "SNR_water": round(snr_water, 1),
        "Hough_thresh": hough_thresh,
        "contour_min_area_px": contour_area_min,
        "contour_circularity_thresh": contour_circularity,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("МОДЕЛЬ КАМЕРЫ (FOV/GSD)")
    print("=" * 60)
    r1 = run_camera_model()
    for k, v in r1.items():
        print(f"  {k}: {v}")

    print()
    print("=" * 60)
    print("МОДЕЛЬ YOLO-DETECT (MACS/ЛАТЕНТНОСТЬ)")
    print("=" * 60)
    r2 = run_yolo_model()
    for k, v in r2.items():
        print(f"  {k}: {v}")

    print()
    print("=" * 60)
    print("МОДЕЛЬ СТЕРЕОЗРЕНИЯ (DISPARITY/DEPTH)")
    print("=" * 60)
    r3 = run_stereo_model()
    for k, v in r3.items():
        print(f"  {k}: {v}")

    print()
    print("=" * 60)
    print("МОДЕЛЬ CANNY/HOUGH (КОНТУРЫ)")
    print("=" * 60)
    r4 = run_edge_detection_model()
    for k, v in r4.items():
        print(f"  {k}: {v}")