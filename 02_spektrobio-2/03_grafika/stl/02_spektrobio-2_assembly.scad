// СпектрБио-2 — Анализатор биомаркеров
$fn = 64;
module main_body() {
    difference() {
        cube([120,80,40], center=true);
        translate([0,0,2]) cube([116,76,36], center=true);
    }
}
module kuvette() {
    color([0.8,0.8,0.8])
    difference() {
        cube([40,20,15], center=true);
        translate([0,0,2]) cube([36,4,11], center=true);
    }
}
module assembly() {
    main_body();
    translate([20,0,-10]) kuvette();
}
assembly();
