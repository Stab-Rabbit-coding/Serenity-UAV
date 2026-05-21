// Shell of s_wings_both.stl
// wall=2.5mm  scale=2.1974  centroid=(-181.66,-103.93,7.14)
difference() {
    scale([2.197421959699318,2.197421959699318,2.197421959699318]) import("../files/s_wings_both.stl");
    translate([-181.6554,-103.9338,7.1379])
    scale([0.951369,0.948243,0.656097])
    translate([181.6554,103.9338,-7.1379])
    scale([2.197421959699318,2.197421959699318,2.197421959699318]) import("../files/s_wings_both.stl");
}
