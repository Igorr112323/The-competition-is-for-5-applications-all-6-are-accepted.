// АкустикМон-6 — Носимый модуль
$fn = 64;
module main_body() {
    difference() {
        cylinder(d=40, h=12, center=true);
        cylinder(d=36, h=10, center=true);
    }
}
module mic_hole() {
    translate([0,0,5]) cylinder(d=3, h=4);
}
module assembly() {
    main_body();
    mic_hole();
}
assembly();
