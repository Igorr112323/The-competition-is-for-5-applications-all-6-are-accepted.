module outer_case() {
    difference() {
        cube([160, 120, 200], center=true);
        translate([0, 0, 5])
            cube([150, 110, 195], center=true);
    }
}

module sieve_layer(thickness, hole_r, spacing) {
    difference() {
        cube([140, 100, thickness], center=true);
        for (x = [-60:spacing:60]) {
            for (y = [-40:spacing:40]) {
                translate([x, y, 0])
                    cylinder(h=thickness + 1, r=hole_r, center=true);
            }
        }
    }
}

module piezo_vibrator() {
    difference() {
        cylinder(h=8, r=15, center=true);
        cylinder(h=10, r=5, center=true);
    }
    translate([0, 0, 8])
        cylinder(h=3, r=12, center=true);
}

module accelerometer() {
    cube([8, 8, 3], center=true);
}

module controller_box() {
    difference() {
        cube([50, 35, 20], center=true);
        translate([0, 0, 2])
            cube([44, 29, 17], center=true);
    }
}

module battery_holder() {
    difference() {
        cylinder(h=70, r=18, center=true);
        cylinder(h=72, r=16, center=true);
    }
}

module display_mount() {
    difference() {
        cube([35, 20, 3], center=true);
        cube([30, 15, 4], center=true);
    }
}

module full_assembly() {
    outer_case();
    translate([0, 0, 60])
        sieve_layer(3, 3, 10);
    translate([0, 0, 20])
        sieve_layer(3, 2, 8);
    translate([0, 0, -20])
        sieve_layer(3, 1.5, 7);
    translate([0, 0, -60])
        cube([145, 105, 3], center=true);
    translate([0, -65, 0])
        piezo_vibrator();
    translate([0, -65, 15])
        accelerometer();
    translate([70, 0, -80])
        controller_box();
    translate([-70, 0, -80])
        battery_holder();
    translate([0, 65, 80])
        display_mount();
}

full_assembly();