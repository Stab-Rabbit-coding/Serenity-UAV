// Shell of s_eng_right.stl
// wall=2.5mm  scale=2.1974  centroid=(92.47,-114.97,57.31)
difference() {
    scale([2.197421959699318,2.197421959699318,2.197421959699318]) import("../files/s_eng_right.stl");
    translate([92.4693,-114.9711,57.3082])
    scale([0.889859,0.900568,0.955048])
    translate([-92.4693,114.9711,-57.3082])
    scale([2.197421959699318,2.197421959699318,2.197421959699318]) import("../files/s_eng_right.stl");
}
