// ЗрениеБПЛА-5 — Стереокамера
$fn = 64;
module camera_body() {
    difference() {
        cube([80,30,25], center=true);
        translate([0,0,2]) cube([76,26,21], center=true);
    }
}
module lens() {
    color([0.2,0.2,0.2])
    cylinder(d=15, h=10, center=true);
}
module assembly() {
    camera_body();
    translate([-20,15,0]) lens();
    translate([20,15,0]) lens();
}
assembly();
