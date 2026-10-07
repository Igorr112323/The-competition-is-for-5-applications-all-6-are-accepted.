// ВибраМон-6 — Беспроводной сенсорный узел
// Корпус 50×40×20 мм, IP67, магнитное крепление

$fn = 64;

module main_body() {
    difference() {
        hull() {
            translate([5, 5, 0])
                cylinder(r=3, h=20, center=true);
            translate([45, 5, 0])
                cylinder(r=3, h=20, center=true);
            translate([5, 35, 0])
                cylinder(r=3, h=20, center=true);
            translate([45, 35, 0])
                cylinder(r=3, h=20, center=true);
        }
        hull() {
            translate([7, 7, 0])
                cylinder(r=2, h=16, center=true);
            translate([43, 7, 0])
                cylinder(r=2, h=16, center=true);
            translate([7, 33, 0])
                cylinder(r=2, h=16, center=true);
            translate([43, 33, 0])
                cylinder(r=2, h=16, center=true);
        }
    }
}

module lid() {
    difference() {
        hull() {
            translate([5, 5, 0])
                cylinder(r=3, h=2, center=true);
            translate([45, 5, 0])
                cylinder(r=3, h=2, center=true);
            translate([5, 35, 0])
                cylinder(r=3, h=2, center=true);
            translate([45, 35, 0])
                cylinder(r=3, h=2, center=true);
        }
        for (x = [8, 42])
            for (y = [8, 32])
                translate([x, y, 0])
                    cylinder(d=2.5, h=3, center=true);
    }
}

module seal_groove() {
    translate([25, 20, 8])
    difference() {
        hull() {
            translate([15, 10, 0])
                cylinder(d=2, h=1.5, center=true);
            translate([-15, 10, 0])
                cylinder(d=2, h=1.5, center=true);
            translate([15, -10, 0])
                cylinder(d=2, h=1.5, center=true);
            translate([-15, -10, 0])
                cylinder(d=2, h=1.5, center=true);
        }
        hull() {
            translate([13, 8, 0])
                cylinder(d=1, h=2, center=true);
            translate([-13, 8, 0])
                cylinder(d=1, h=2, center=true);
            translate([13, -8, 0])
                cylinder(d=1, h=2, center=true);
            translate([-13, -8, 0])
                cylinder(d=1, h=2, center=true);
        }
    }
}

module magnet_housing() {
    color([0.5, 0.5, 0.5])
    difference() {
        cube([40, 30, 3], center=true);
        translate([12, 8, 0])
            cylinder(d=10, h=4, center=true);
        translate([-12, 8, 0])
            cylinder(d=10, h=4, center=true);
        translate([12, -8, 0])
            cylinder(d=10, h=4, center=true);
        translate([-12, -8, 0])
            cylinder(d=10, h=4, center=true);
    }
}

module magnet() {
    color([0.2, 0.2, 0.2])
    cylinder(d=9, h=2.5, center=true);
}

module adxl355_chip() {
    color([0.2, 0.2, 0.2])
    cube([6, 6, 1.5], center=true);
}

module mems_microphone() {
    color([0.3, 0.3, 0.3])
    cube([4, 3, 1], center=true);
}

module pt100_element() {
    color([0.8, 0.6, 0.2])
    cube([3, 2, 1], center=true);
}

module nrf52840_chip() {
    color([0.1, 0.3, 0.7])
    cube([7, 7, 1], center=true);
}

module pcb_node() {
    color([0.1, 0.5, 0.1])
    difference() {
        cube([42, 32, 1], center=true);
        translate([17, 12, 0])
            cylinder(d=2, h=2, center=true);
        translate([-17, 12, 0])
            cylinder(d=2, h=2, center=true);
        translate([17, -12, 0])
            cylinder(d=2, h=2, center=true);
        translate([-17, -12, 0])
            cylinder(d=2, h=2, center=true);
    }
}

module battery_cr2450() {
    color([0.7, 0.7, 0.7])
    cylinder(d=24.5, h=5, center=true);
}

module seal_ring() {
    color([0.2, 0.8, 0.2])
    difference() {
        hull() {
            translate([16, 11, 0])
                cylinder(d=2, h=1, center=true);
            translate([-16, 11, 0])
                cylinder(d=2, h=1, center=true);
            translate([16, -11, 0])
                cylinder(d=2, h=1, center=true);
            translate([-16, -11, 0])
                cylinder(d=2, h=1, center=true);
        }
        hull() {
            translate([14, 9, 0])
                cylinder(d=1, h=2, center=true);
            translate([-14, 9, 0])
                cylinder(d=1, h=2, center=true);
            translate([14, -9, 0])
                cylinder(d=1, h=2, center=true);
            translate([-14, -9, 0])
                cylinder(d=1, h=2, center=true);
        }
    }
}

module antenna_trace() {
    color([0.8, 0.8, 0.8])
    cube([20, 1, 0.2], center=true);
}

module assembly() {
    main_body();
    translate([0, 0, 11]) lid();
    translate([25, 20, -10]) magnet_housing();
    translate([13, 12, -11]) magnet();
    translate([-13, 12, -11]) magnet();
    translate([13, -12, -11]) magnet();
    translate([-13, -12, -11]) magnet();
    translate([0, 0, -5]) pcb_node();
    translate([15, 5, -4]) adxl355_chip();
    translate([-15, 5, -4]) mems_microphone();
    translate([-15, -5, -4]) pt100_element();
    translate([0, -8, -4]) nrf52840_chip();
    translate([0, 0, -8]) battery_cr2450();
    translate([25, 0, -4]) antenna_trace();
    translate([25, 20, -8]) seal_ring();
}

assembly();