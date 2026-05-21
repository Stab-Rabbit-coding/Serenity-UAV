// Shell of s_middle.stl
// wall=2.5mm  scale=2.1974  centroid=(135.71,-50.46,27.35)
difference() {
    scale([2.197421959699318,2.197421959699318,2.197421959699318]) import("../files/s_middle.stl");
    translate([135.7120,-50.4591,27.3477])
    scale([0.962373,0.959565,0.908966])
    translate([-135.7120,50.4591,-27.3477])
    scale([2.197421959699318,2.197421959699318,2.197421959699318]) import("../files/s_middle.stl");
}
