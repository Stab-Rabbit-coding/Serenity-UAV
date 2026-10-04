// =============================================================================
// nacelle_nozzle_servo_options_context.scad — 64 mm nozzle-servo packaging
// options, in context (WBS NAC-64-SERVO-01; owner 2026-10-04 "all 4")
// =============================================================================
// Starboard nacelle, nacelle-local frame (z = duct axis from the intake).
// Real geometry: the 64 mm pod render (POD_STL), the stage-2 cartridge
// (CART_STL, at Z 103.7) and the assembled 64 mm iris (NOZ_STL, at the nozzle
// ring Z 187.86).  ENVELOPES (not final parts) for the servo — Hitec HS-40,
// 20 x 8.6 x 17 mm, the fully dimensioned KTD2 alternate, lying flat (8.6 mm
// radial) — its 9.3 mm crank, the rod to the ring's ball cup (r 39.0, mid
// ear sweep) and each option's fairing:
//
//   OPTION 1  servo on the NOZZLE housing, in a faired pod aft of Z 188
//   OPTION 2  faired BLISTER on the pod tail, servo inside, Z ~160..180
//   OPTION 3  servo FORWARD at az 210 (Z 150..170, existing skin room), narrow
//             rod fairing along the tail; ear moved to the 202.5 deg flap gap
//   OPTION 4  RE-SHAPED tail: boat-tail filled from Z 150 to the housing OD
//
// Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
// Stab-Rabbit-coding, per AGENTS.md AI attribution.  License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
// =============================================================================

OPTION   = 1;
POD_STL  = "nacelle_stbd_64mm_local.stl";
CART_STL = "cart2.stl";
NOZ_STL  = "nozzle_asm.stl";
CUT      = 0;     // 1 = remove the half-space y < 0 to show the inside

Z_NOZ  = 187.86;  BALL_R = 39.0;  BALL_Z = Z_NOZ + 4.0;
EAR_AZ = OPTION == 3 ? 202.5 : 145.6;      // mid-sweep of the ear window
SV_L = 20.0;  SV_W = 17.0;  SV_T = 8.6;  CRANK = 9.3;

// Place a child at azimuth az, radius r, axial z (x radial, y tangential).
module at(az, r, z) { rotate([0, 0, az]) translate([r, 0, z]) children(); }

module servo(az, r0, z0) {                        // r0 = inner (duct-side) face
    at(az, r0, z0) translate([0, -SV_W / 2, 0]) cube([SV_T, SV_W, SV_L]);
}
module rod(p, q) { hull() { translate(p) sphere(d = 2.5, $fn = 12);
                            translate(q) sphere(d = 2.5, $fn = 12); } }
function pt(az, r, z) = [r * cos(az), r * sin(az), z];

module fairing_pod(az, r0, r1, z0, z1, w) {        // streamlined envelope
    hull() for (z = [z0 + w / 2, z1 - w / 2]) at(az, (r0 + r1) / 2, z)
        scale([(r1 - r0) / w, 1, 1]) sphere(d = w, $fn = 32);
}

module option_geometry() {
    if (OPTION == 1) {
        color("Gold", 0.55) fairing_pod(EAR_AZ, 40.0, 53.0, 186.0, 216.0, 22);
        color("Red") servo(EAR_AZ, 43.2, 192.0);
        color("Black") rod(pt(EAR_AZ - 6, 44.5, 191.0), pt(EAR_AZ, BALL_R, BALL_Z));
    } else if (OPTION == 2) {
        color("Gold", 0.55) fairing_pod(EAR_AZ, 33.0, 48.5, 146.0, 194.0, 22);
        color("Red") servo(EAR_AZ, 37.6, 160.0);
        color("Black") rod(pt(EAR_AZ, 41.0, 181.0), pt(EAR_AZ, BALL_R, BALL_Z));
    } else if (OPTION == 3) {
        color("Red") servo(210, 37.6, 150.0);
        color("Gold", 0.55) fairing_pod(206, 34.0, 42.5, 166.0, 194.0, 8);
        color("Black") rod(pt(208, 40.0, 171.0), pt(EAR_AZ, BALL_R, BALL_Z));
        color("Magenta") at(EAR_AZ, BALL_R, BALL_Z) sphere(d = 3.0, $fn = 16);
    } else {
        color("Gold", 0.45) difference() {          // filled boat-tail
            rotate_extrude($fn = 120) polygon([[34.8, 150], [45.0, 150],
                                                [42.6, Z_NOZ], [34.8, Z_NOZ]]);
            translate([0, 0, 140]) cylinder(r = 34.8, h = 60);
        }
        color("Red") servo(EAR_AZ, 37.6, 162.0);
        color("Black") rod(pt(EAR_AZ, 41.0, 183.0), pt(EAR_AZ, BALL_R, BALL_Z));
    }
}

module maybe_cut() {
    if (CUT == 1) difference() { children(); translate([-200, -400, -10]) cube([400, 400, 400]); }
    else children();
}

maybe_cut() {
    color("LightGray", 0.6) import(POD_STL, convexity = 8);
    color("DimGray") translate([0, 0, 103.7]) import(CART_STL, convexity = 6);
    color("SteelBlue") translate([0, 0, Z_NOZ]) import(NOZ_STL, convexity = 8);
}
option_geometry();
