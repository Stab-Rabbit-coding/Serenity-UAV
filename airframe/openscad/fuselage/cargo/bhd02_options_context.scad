// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See AGENTS.md.
//   X = +port, Y = +aft, Z = +dorsal; origin = SerenityAssembly.FCStd origin.
// ===========================================================================
// bhd02_options_context.scad -- pictures of the three BHD-02 owner decisions
// (landing-gear bays vs wing root), docs/CARGO_BULKHEAD_FIT_CHECK.md BHD-02.
//
// This file DRAWS; it does not decide.  Every solid is written by the study,
// which is where the numbers come from:
//
//   /usr/bin/python3 tools/landing_gear_bay_function.py --export BASE
//   /usr/bin/python3 tools/bhd02_option_study.py --export DIR ...
//   openscad -D 'DIR="DIR"' -D VIEW=n --camera=... -o v.png bhd02_options_context.scad
//
// Red = material removed (a cut) or an interference.  Import only -- OpenCSG
// preview of booleans on these meshes draws false faces, so the study does all
// the clipping (same rule as cargo_bulkhead_context.scad).
//
// VIEW and the cameras used for docs/images/bhd02/*.png (eye, centre):
//   0  A port root flange cut for the fore well, from inboard
//        -330,21,67,-90,21,67
//   1  B2 aft-port wing relief, from below-outboard-aft
//        -20,150,-30,-72,98,64
//   2  B2 fore-port wing relief, from below-outboard-fore
//        40,-150,-40,-80,0,60
//   3  B1 rejected: cluster rotated 30 deg, swept thigh strikes the bay
//        40,150,-60,-72,110,44
//   4  C fore bay, leg-local: handed (left) vs shared (right), from outboard
//        160,0,10,10,0,5
//
// Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
// Stab-Rabbit-coding, per AGENTS.md AI attribution.
// License: CERN-OHL-W-2.0 -- see LICENSES/CERN-OHL-W 2.0
// (SPDX-License-Identifier: CERN-OHL-W-2.0)

DIR = ".";     // tools/bhd02_option_study.py --export directory (absolute)
VIEW = 0;

STL = "../../../stls/";                 // repo airframe/stls from here
function d(n) = str(DIR, "/", n, ".stl");

// CF spar O20 along hull X at the wing spar datum (merge_cargo_interior.py
// WING_SPAR_Y / WING_SPAR_Z), drawn from the socket floor outboard.
module spar(x0, x1) {
    color("Black")
        translate([min(x0, x1), 21.00, 66.851])
            rotate([0, 90, 0]) cylinder(h = abs(x1 - x0), d = 20, $fn = 48);
}

if (VIEW == 0) {
    color("Tan") import(d("A_flange_cut_port"));
    color("Red", 0.85) import(d("A_flange_removed_port"));
    color("OliveDrab", 0.35) import(d("A_gear_through_flange_port"));
    spar(-100, -60);
} else if (VIEW == 1) {
    color("LightGrey", 0.45) import(str(STL, "wings/wing_port_s1223_revo.stl"));
    color("Red") import(d("B2_wing_relief_aft-port"));
    color("OliveDrab") import(d("base_bay_aft-port"));
} else if (VIEW == 2) {
    color("LightGrey", 0.45) import(str(STL, "wings/wing_port_s1223_revo.stl"));
    color("Red") import(d("B2_wing_relief_fore-port"));
    color("OliveDrab") import(d("base_bay_fore-port"));
    spar(-100, -40);
} else if (VIEW == 3) {
    // The swept leg is NOT drawn: OpenCSG sorts translucent meshes badly and
    // a translucent sweep hides the strike.  Red = sweep x bay, from the study.
    color("Red") import(d("B1_30_thigh_x_bay_aft-port"));
    color("OliveDrab", 0.35) import(d("B1_30_bay_aft-port"));
} else if (VIEW == 4) {
    translate([0, -40, 0]) {
        color("OliveDrab") import(d("C_bay_handed_port"));
        color("Red") import(d("C_removed_handed_port"));
    }
    translate([0, 40, 0]) {
        color("OliveDrab") import(d("C_bay_shared"));
        color("Red") import(d("C_removed_shared"));
    }
}
