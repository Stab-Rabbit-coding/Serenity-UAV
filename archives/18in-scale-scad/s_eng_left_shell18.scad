// Shell of s_eng_left.stl
// wall=2.5mm  scale=2.1974  centroid=(26.19,-114.97,57.31)
difference() {
    scale([2.197421959699318,2.197421959699318,2.197421959699318]) import("../files/s_eng_left.stl");
    translate([26.1915,-114.9711,57.3082])
    scale([0.889859,0.900568,0.955048])
    translate([-26.1915,114.9711,-57.3082])
    scale([2.197421959699318,2.197421959699318,2.197421959699318]) import("../files/s_eng_left.stl");
}
