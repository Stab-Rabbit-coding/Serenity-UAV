// Shell of s_cargo_sect.stl
// wall=2.5mm  scale=2.1974  centroid=(-76.64,-246.47,56.02)
difference() {
    scale([2.197421959699318,2.197421959699318,2.197421959699318]) import("../files/s_cargo_sect.stl");
    translate([-76.6414,-246.4719,56.0153])
    scale([0.965771,0.967263,0.959167])
    translate([76.6414,246.4719,-56.0153])
    scale([2.197421959699318,2.197421959699318,2.197421959699318]) import("../files/s_cargo_sect.stl");
}
