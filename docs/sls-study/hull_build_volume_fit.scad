// SPDX-License-Identifier: CERN-OHL-W-2.0
// Hull envelope vs. SLS/MJF build volumes (mm). Envelope = bounding box only,
// NOT the hull geometry. 24 in dims from measured shell STL extents (approx.).
scale_k   = 1.25;          // 30 in / 24 in
hull24    = [610, 200, 210];
hull30    = hull24 * scale_k;
vol_p770  = [700, 380, 580];   // EOS P 770 (PA 2200)
vol_ht1001= [1000, 500, 450];  // Farsoon HT1001P
vol_pl    = [482, 482, 431];   // Protolabs SLS (listed)
module ghost(v, c) color(c, 0.18) cube(v);
translate([0,0,0])    ghost(vol_ht1001, "green");
translate([0,600,0])  ghost(vol_p770,   "orange");
translate([0,1100,0]) ghost(vol_pl,     "red");
for (y=[0,600,1100]) translate([10,y+10,0]) { color("blue") cube(hull30); }
translate([10,1700,0]) color("gray") cube(hull24);
