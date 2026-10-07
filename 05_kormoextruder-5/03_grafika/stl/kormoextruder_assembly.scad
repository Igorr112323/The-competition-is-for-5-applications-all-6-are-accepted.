module barrel() {
    difference() {
        cylinder(h=500, r=60, center=true);
        cylinder(h=510, r=50, center=true);
    }
}

module screw() {
    for (i = [0:24]) {
        translate([0, 0, -240 + i * 20])
            rotate([0, 0, i * 30])
                linear_extrude(height=18, twist=30)
                    translate([15, 0, 0])
                        circle(r=30);
    }
    cylinder(h=500, r=15, center=true);
}

module hopper() {
    difference() {
        cube([80, 60, 100], center=true);
        translate([0, 0, 5])
            cube([70, 50, 95], center=true);
    }
}

module die_plate() {
    difference() {
        cylinder(h=10, r=60, center=true);
        for (i = [0:5]) {
            rotate([0, 0, i * 60])
                translate([25, 0, 0])
                    cylinder(h=12, r=4, center=true);
        }
        cylinder(h=12, r=15, center=true);
    }
}

module motor_mount() {
    difference() {
        cube([100, 80, 60], center=true);
        translate([0, 0, -5])
            cube([90, 70, 55], center=true);
        translate([0, 0, -30])
            cylinder(h=10, r=20, center=true);
    }
}

module frame() {
    for (x = [-100, 100]) {
        for (y = [-50, 50]) {
            translate([x, y, -300])
                cylinder(h=600, r=8, center=true);
        }
    }
    translate([0, 0, -300])
        cube([220, 120, 5], center=true);
    translate([0, 0, 300])
        cube([220, 120, 5], center=true);
}

module full_assembly() {
    barrel();
    screw();
    translate([0, 70, 200])
        hopper();
    translate([0, 0, 260])
        die_plate();
    translate([0, -80, -100])
        motor_mount();
    frame();
}

full_assembly();