// LAMP-ДНК-Экспресс — Кейс
$fn = 64;
module case_body() {
    difference() {
        cube([300,200,100], center=true);
        translate([0,0,3]) cube([294,194,94], center=true);
    }
}
module heater_block() {
    color([0.8,0.2,0.2])
    cube([60,40,20], center=true);
}
module assembly() {
    case_body();
    translate([-80,0,-30]) heater_block();
}
assembly();
