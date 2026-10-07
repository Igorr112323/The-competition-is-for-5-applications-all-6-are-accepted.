module sensor_body() {
    difference() {
        cube([140, 100, 30], center=true);
        translate([0, 0, 3])
            cube([130, 90, 25], center=true);
        translate([0, 0, -15])
            cube([20, 90, 10], center=true);
    }
}

module camera_window() {
    difference() {
        cube([30, 20, 5], center=true);
        cube([25, 15, 6], center=true);
    }
}

module laser_sensor() {
    difference() {
        cube([25, 15, 10], center=true);
        translate([0, 0, -5])
            cylinder(h=6, r=3, center=true);
    }
}

module display_mount() {
    difference() {
        cube([40, 25, 5], center=true);
        cube([35, 20, 6], center=true);
    }
}

module connector_flange() {
    difference() {
        cylinder(h=8, r=12, center=true);
        cylinder(h=10, r=6, center=true);
        for (i = [0:3]) {
            rotate([0, 0, i * 90])
                translate([8, 0, 0])
                    cylinder(h=10, r=1.5, center=true);
        }
    }
}

module tochnoves_full() {
    sensor_body();
    translate([0, 0, 20])
        camera_window();
    translate([-50, 0, 20])
        laser_sensor();
    translate([50, 0, 20])
        display_mount();
    translate([-60, -50, 0])
        connector_flange();
    translate([60, -50, 0])
        connector_flange();
    translate([-60, 50, 0])
        connector_flange();
    translate([60, 50, 0])
        connector_flange();
}

tochnoves_full();