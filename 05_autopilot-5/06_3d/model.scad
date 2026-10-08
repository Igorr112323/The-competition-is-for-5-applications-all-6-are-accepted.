// AvtoPilot-5 Lot 5.6
module body() { difference() { cube([100,60,25],center=true); translate([0,0,2]) cube([94,54,22],center=true); } }
module mounts() { for(x=[-40,-20,0,20,40]) { translate([x,-25,-10]) cylinder(h=5,r=2,$fn=16); translate([x,25,-10]) cylinder(h=5,r=2,$fn=16); } }
module lid() { translate([0,0,30]) difference() { cube([100,60,3],center=true); for(x=[-40,40]) for(y=[-25,25]) translate([x,y,0]) cylinder(h=5,r=1.5,center=true,$fn=16); } }
color("SteelBlue") body(); color("Gold") mounts(); color("LightBlue",0.7) lid();