module aeroskan_body() {
    difference() {
        cube([180, 120, 40], center=true);
        translate([0, 0, 3])
            cube([170, 110, 35], center=true);
        translate([0, 0, -20])
            cylinder(h=10, r=30, center=true);
    }
}

module flange_mount(x, y) {
    translate([x, y, 0]) {
        difference() {
            cylinder(h=8, r=15, center=true);
            cylinder(h=10, r=5, center=true);
            for (i = [0:3]) {
                rotate([0, 0, i * 90])
                    translate([10, 0, 0])
                        cylinder(h=10, r=2, center=true);
            }
        }
    }
}

module nozzle_mount() {
    difference() {
        cylinder(h=20, r=8, center=true);
        cylinder(h=22, r=4, center=true);
    }
}

module lidar_holder() {
    difference() {
        cylinder(h=15, r=20, center=true);
        cylinder(h=17, r=15, center=true);
        for (i = [0:3]) {
            rotate([0, 0, i * 90])
                translate([16, 0, 0])
                    cylinder(h=17, r=1.5, center=true);
        }
    }
}

module aeroskan_full() {
    aeroskan_body();
    flange_mount(-80, -50);
    flange_mount(80, -50);
    flange_mount(-80, 50);
    flange_mount(80, 50);
    translate([0, 0, 25])
        lidar_holder();
    translate([0, 60, 0])
        nozzle_mount();
    translate([0, -60, 0])
        nozzle_mount();
    translate([60, 60, 0])
        nozzle_mount();
    translate([60, -60, 0])
        nozzle_mount();
    translate([-60, 60, 0])
        nozzle_mount();
    translate([-60, -60, 0])
        nozzle_mount();
}

aeroskan_full();