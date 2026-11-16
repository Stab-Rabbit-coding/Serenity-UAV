// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See AGENTS.md.
//   X = +port, Y = +aft, Z = +dorsal; origin = SerenityAssembly.FCStd origin.
// ===========================================================================
// bhd10_aft_strip_context.scad -- pictures of the BHD-10 options: the Pilot
// FC2 / FC3 aft-strip nodes against the cargo/middle splice collar and the
// tilt controller boards (docs/CARGO_BULKHEAD_FIT_CHECK.md BHD-10).
//
// Draws only; the numbers come from
//   /usr/bin/python3 tools/bhd10_aft_strip_options.py --export DIR
//   openscad -D 'DIR="DIR"' -D VIEW=n --camera=... -o v.png bhd10_aft_strip_context.scad
// Red = interference or material removed.  Import only (see
// cargo_bulkhead_context.scad for why).
//
// VIEW (camera eye,centre for docs/images/bhd02/BHD10_*.png):
//   0 baseline: nodes 0.5 mm into the collar at the upper-outboard corners
//   1 O1 pair moved forward 2.5 mm: into the tilt controller boards
//   2 O2 collar ring relieved behind each corner (removed ring in red)
//   3 O3 pouched stack 2.5 mm thinner (needs first-article measurement)
//   all, with --viewall --autocenter: -60,0,260,-170,110,105
//
// Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
// Stab-Rabbit-coding, per AGENTS.md AI attribution.
// License: CERN-OHL-W-2.0 -- see LICENSES/CERN-OHL-W 2.0
// (SPDX-License-Identifier: CERN-OHL-W-2.0)

DIR = ".";
VIEW = 0;
function d(n) = str(DIR, "/", n, ".stl");

TAG = (VIEW == 1) ? "O1" : (VIEW == 3) ? "O3" : "base";
NODES = ["Pilot_FC2_port", "Pilot_FC3_stbd"];
ZONES = ["Pilot_FC2_cable_zone", "Pilot_FC3_cable_zone"];

module context() {
    color("SteelBlue") {
        import(d("ctx_tilt_controller_board_port"));
        import(d("ctx_tilt_controller_board_stbd"));
    }
    color("Gray", 0.8) {
        import(d("ctx_tilt_bracket_port"));
        import(d("ctx_tilt_bracket_stbd"));
    }
}

context();
if (VIEW == 2) {
    color("Tan") import(d("O2_collar_relieved"));
    color("Red") import(d("O2_collar_removed"));
} else {
    color("Tan", 0.6) import(d("collar"));
}
for (n = NODES) color("DarkGreen", 0.85) import(d(str(TAG, "_", n)));
for (z = ZONES) color("LightGreen", 0.5) import(d(str(TAG, "_", z)));
// clash meshes for the shown option (missing files are skipped with a warning)
if (VIEW <= 1)
    for (n = concat(NODES, ZONES))
        for (t = ["collar_cargo-middle", "tilt_controller_board_port",
                  "tilt_controller_board_stbd"])
            color("Red") import(d(str("CLASH_", TAG, "_", n, "_", t)));
