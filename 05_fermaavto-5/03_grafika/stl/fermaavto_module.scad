// ФермаАвто-5 — Навигационный модуль
// Корпус 120×80×40 мм

$fn = 64;

module main_body() {
    difference() {
        cube([120, 80, 40], center=true);
        translate([0, 0, 2])
            cube([114, 74, 36], center=true);
        translate([0, 40, 0])
            cube([40, 5, 30], center=true);
    }
}

module camera_housing() {
    color([0.2, 0.2, 0.2])
    difference() {
        union() {
            cube([30, 20, 15], center=true);
            translate([0, 10, 0])
                cylinder(d=22, h=15, center=true);
        }
        translate([0, 10, 0])
            cylinder(d=18, h=16, center=true);
    }
}

module uz_sensor() {
    color([0.8, 0.8, 0.2])
    difference() {
        cube([20, 10, 10], center=true);
        translate([5, 5, 0])
            cylinder(d=8, h=11, center=true);
        translate([-5, 5, 0])
            cylinder(d=8, h=11, center=true);
    }
}

module imu_chip() {
    color([0.2, 0.2, 0.2])
    cube([5, 5, 1.5], center=true);
}

module jetson_nano() {
    color([0.1, 0.5, 0.1])
    difference() {
        cube([45, 27, 1.6], center=true);
        translate([18, 10, 0])
            cylinder(d=3, h=3, center=true);
        translate([-18, 10, 0])
            cylinder(d=3, h=3, center=true);
        translate([18, -10, 0])
            cylinder(d=3, h=3, center=true);
        translate([-18, -10, 0])
            cylinder(d=3, h=3, center=true);
    }
}

module nrf52840() {
    color([0.1, 0.3, 0.7])
    cube([20, 15, 1.6], center=true);
}

module can_transceiver() {
    color([0.3, 0.3, 0.3])
    cube([8, 5, 1.5], center=true);
}

module encoder_connector() {
    color([0.6, 0.6, 0.6])
    cube([12, 8, 6], center=true);
}

module antenna() {
    color([0.8, 0.8, 0.8])
    union() {
        cylinder(d=2, h=30);
        translate([0, 0, 30])
            sphere(d=4);
    }
}

module mounting_bracket() {
    color([0.5, 0.5, 0.5])
    difference() {
        cube([30, 20, 3], center=true);
        translate([10, 5, 0])
            cylinder(d=4, h=4, center=true);
        translate([-10, 5, 0])
            cylinder(d=4, h=4, center=true);
        translate([10, -5, 0])
            cylinder(d=4, h=4, center=true);
        translate([-10, -5, 0])
            cylinder(d=4, h=4, center=true);
    }
}

module assembly() {
    main_body();
    translate([0, 35, 5]) camera_housing();
    translate([-50, 30, 0]) uz_sensor();
    translate([-50, -30, 0]) uz_sensor();
    translate([50, 30, 0]) uz_sensor();
    translate([50, -30, 0]) uz_sensor();
    translate([-30, 0, 10]) uz_sensor();
    translate([30, 0, 10]) uz_sensor();
    translate([0, 0, -15]) jetson_nano();
    translate([-30, -20, -15]) nrf52840();
    translate([30, -20, -15]) can_transceiver();
    translate([50, 0, -15]) encoder_connector();
    translate([55, 35, 20]) antenna();
    translate([0, -40, -5]) mounting_bracket();
    translate([0, 0, -5]) imu_chip();
}

assembly();