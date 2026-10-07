// ТеплоВид-4 — Тепловизионный модуль
$fn = 64;
module main_body() {
    difference() {
        cube([60,40,25], center=true);
        translate([0,0,2]) cube([56,36,21], center=true);
    }
}
module lens_housing() {
    color([0.3,0.3,0.3])
    difference() {
        cylinder(d=22, h=15, center=true);
        cylinder(d=18, h=16, center=true);
    }
}
module assembly() {
    main_body();
    translate([0,20,0]) lens_housing();
}
assembly();
