// СпектрАгро-П — Портативный мультиспектральный анализатор
// Корпус 180×120×60 мм

$fn = 64;

module nir_window() {
    translate([0, 0, -1])
        cylinder(d=20, h=3);
}

module uv_window() {
    translate([0, 0, -1])
        cylinder(d=12, h=3);
}

module ph_connector() {
    translate([0, 0, -1])
        cylinder(d=8, h=5);
}

module display_cutout() {
    translate([-30, -20, -1])
        cube([60, 40, 3]);
}

module button_hole() {
    cylinder(d=6, h=5);
}

module main_body() {
    difference() {
        cube([180, 120, 60], center=true);
        translate([0, 0, 2])
            cube([172, 112, 56], center=true);
    }
}

module lid() {
    difference() {
        union() {
            cube([180, 120, 4], center=true);
            translate([0, 0, 2])
                cube([172, 112, 4], center=true);
        }
        display_cutout();
    }
}

module nir_module() {
    color([0.2, 0.2, 0.8])
    union() {
        cube([50, 30, 20], center=true);
        translate([0, 15, 0])
            nir_window();
    }
}

module uv_module() {
    color([0.8, 0.2, 0.2])
    union() {
        cube([30, 20, 15], center=true);
        translate([0, 10, 0])
            uv_window();
    }
}

module ph_module() {
    color([0.2, 0.8, 0.2])
    union() {
        cube([25, 15, 10], center=true);
        translate([0, 8, 0])
            ph_connector();
    }
}

module cond_module() {
    color([0.8, 0.8, 0.2])
    cube([25, 15, 10], center=true);
}

module pcb() {
    color([0.1, 0.5, 0.1])
    difference() {
        cube([120, 80, 1.6], center=true);
        for (x = [-50, 50])
            for (y = [-30, 30])
                translate([x, y, 0])
                    cylinder(d=3, h=3, center=true);
    }
}

module stm32_chip() {
    color([0.2, 0.2, 0.2])
    cube([14, 14, 1.5], center=true);
}

module battery() {
    color([0.3, 0.3, 0.8])
    cube([70, 40, 12], center=true);
}

module ble_module() {
    color([0.5, 0.5, 0.5])
    cube([15, 10, 2], center=true);
}

module assembly() {
    main_body();
    translate([0, 0, 32]) lid();
    translate([30, 0, -15]) nir_module();
    translate([-30, 20, -15]) uv_module();
    translate([-30, -20, -15]) ph_module();
    translate([50, -20, -15]) cond_module();
    translate([0, 0, -20]) pcb();
    translate([30, 0, -22]) stm32_chip();
    translate([0, -30, -25]) battery();
    translate([-50, 0, -22]) ble_module();
}

assembly();