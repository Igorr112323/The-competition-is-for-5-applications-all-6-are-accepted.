// АвтоПилот-5 — Контроллер
$fn = 64;
module pcb() {
    color([0.1,0.5,0.1])
    difference() {
        cube([80,50,1.6], center=true);
        translate([30,20,0]) cylinder(d=3, h=3, center=true);
        translate([-30,20,0]) cylinder(d=3, h=3, center=true);
        translate([30,-20,0]) cylinder(d=3, h=3, center=true);
        translate([-30,-20,0]) cylinder(d=3, h=3, center=true);
    }
}
module stm32() { color([0.2,0.2,0.2]) cube([14,14,1.5], center=true); }
module jetson() { color([0.1,0.5,0.1]) cube([45,27,1.6], center=true); }
module assembly() {
    pcb();
    translate([-15,0,2]) stm32();
    translate([15,0,2]) jetson();
}
assembly();
