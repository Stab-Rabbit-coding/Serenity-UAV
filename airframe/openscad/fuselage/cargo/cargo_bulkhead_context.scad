// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See AGENTS.md.
//   X = +port, Y = +aft, Z = +dorsal; origin = SerenityAssembly.FCStd origin.
// ===========================================================================
// cargo_bulkhead_context.scad -- in-context view of the port and starboard
// cargo-bay bulkheads (side walls) and everything that lives on, crosses or
// moves past them.  Pattern: nacelle_tilt_joint_context.scad, per
// docs/solutions/design-patterns/build-every-joint-in-context-through-its-
// full-motion.md.
//
// This file DRAWS; it does not decide.  Every solid, swept volume, clash mesh
// and clipped wall slab is written by the checker, which is the gate:
//
//   /usr/bin/python3 tools/cargo_bulkhead_context.py --corridor --export DIR
//   openscad -D 'DIR="DIR"' -D VIEW=0 --camera=... -o v.png cargo_bulkhead_context.scad
//
// Clash meshes (CLASH_<side>_nn.stl) are solid red.  The checker does all the
// clipping, so this file only imports -- OpenCSG preview of intersections
// with these meshes draws false faces.
//
// VIEW: 0 = port bulkhead from inboard, 1 = starboard bulkhead from inboard,
//       2 = iso from above-aft (both sides), 3 = along the hinge axis from
//       aft (door 0..180 deg swing against the gear).
// Cameras used for docs/images/cargo_bulkhead_context_*.png (eye, centre):
//   0: -560,30,75,-110,30,75    1: 220,30,75,-230,30,75
//   2: 180,560,430,-170,40,60   3: -170,760,20,-170,50,20
//
// Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
// Stab-Rabbit-coding, per AGENTS.md AI attribution.
// License: CERN-OHL-W-2.0 -- see LICENSES/CERN-OHL-W 2.0
// (SPDX-License-Identifier: CERN-OHL-W-2.0)

DIR = ".";     // checker --export directory (absolute path)
VIEW = 0;      // 0 port, 1 stbd, 2 iso, 3 door swing
include_counts = true;
N_CLASH_PORT = 40;   // upper bounds; missing files are skipped with a warning
N_CLASH_STBD = 40;
N_CLASH_CL = 20;

function f(n) = str(DIR, "/", n, ".stl");
function nn(i) = str(i < 10 ? "0" : "", i);

SIDES = VIEW == 0 ? ["port"] : VIEW == 1 ? ["stbd"] : ["port", "stbd"];
INBOARD = VIEW <= 1;

module part(n, c) { color(c) import(f(n), convexity = 6); }

// --- structure ------------------------------------------------------------
for (s = SIDES) {
    if (INBOARD) part(str("shell_wall_", s), [0.82, 0.82, 0.84, 0.40]);
    if (VIEW != 3) {
        part(str("wing_", s), [0.55, 0.65, 0.80, 0.50]);
        part(str("root_flange_", s), [0.95, 0.75, 0.30, 0.60]);
        part(str("CF_spar_", s), [0.15, 0.15, 0.15, 0.90]);
        part(str("drive_shaft_", s), [0.40, 0.40, 0.45, 1.00]);
        part(str("tilt_bracket_", s), [0.30, 0.55, 0.85, 0.70]);
        part(str("wheel_swept_", s), [0.85, 0.85, 0.20, 0.55]);
        part(str("worm_swept_", s), [0.85, 0.65, 0.20, 0.60]);
        part(str("gearmotor_", s), [0.55, 0.55, 0.60, 0.80]);
        part(str("brake_guide_", s), [0.30, 0.70, 0.40, 0.80]);
        part(str("brake_solenoid_", s), [0.45, 0.45, 0.50, 0.80]);
        part(str("brake_collar_", s), [0.70, 0.70, 0.75, 0.80]);
        part(str("tilt_controller_board_", s), [0.10, 0.55, 0.20, 0.85]);
        // harnesses: power orange, encoder cyan, nav magenta; found route amber
        part(str("10AWG_bundle_exit_", s), [1.00, 0.45, 0.00, 0.95]);
        part(str("encoder_harness_exit_", s), [0.00, 0.80, 0.90, 0.95]);
        part(str("nav_harness_exit_", s), [0.90, 0.00, 0.80, 0.95]);
        part(str("ROUTE_10AWG_", s), [1.00, 0.70, 0.20, 0.45]);
    }
    part(str("latch_bracket_", s), [0.60, 0.30, 0.70, 0.85]);
    part(str("door_", s, "__closed_"), [0.70, 0.70, 0.70, 0.60]);
    if (VIEW >= 2) part(str("door_", s, "_swept_0-180"), [0.60, 0.80, 1.00, 0.25]);
    part(str("gear_legs_", s), [0.35, 0.35, 0.35, 0.55]);
}
if (VIEW == 0) {
    part("Pilot_FC2_port", [0.10, 0.60, 0.25, 0.55]);
    part("TACCO_CN2_port", [0.20, 0.70, 0.35, 0.55]);
}
if (VIEW == 1) {
    part("Pilot_FC3_stbd", [0.10, 0.60, 0.25, 0.55]);
    part("TACCO_CN3_stbd", [0.20, 0.70, 0.35, 0.55]);
}
if (VIEW == 2) {
    part("battery_cradle", [0.40, 0.40, 0.80, 0.45]);
    part("payload_keep-out", [0.90, 0.90, 0.20, 0.15]);
    part("collar_cargo-middle", [0.80, 0.55, 0.35, 0.40]);
    part("collar_head-cargo", [0.80, 0.55, 0.35, 0.40]);
    part("cargo_Observer", [0.10, 0.50, 0.50, 0.40]);
    part("Pilot_FC2_port", [0.10, 0.60, 0.25, 0.55]);
    part("Pilot_FC3_stbd", [0.10, 0.60, 0.25, 0.55]);
    part("TACCO_CN2_port", [0.20, 0.70, 0.35, 0.55]);
    part("TACCO_CN3_stbd", [0.20, 0.70, 0.35, 0.55]);
    part("chin_shelf", [0.50, 0.50, 0.55, 0.60]);
}

// --- clashes (solid red) -----------------------------------------------------
module clashes(tag, n) {
    for (i = [0 : n - 1]) color([1, 0, 0, 1]) import(f(str("CLASH_", tag, "_", nn(i))));
}
if (VIEW == 0 || VIEW >= 2) clashes("port", N_CLASH_PORT);
if (VIEW == 1 || VIEW >= 2) clashes("stbd", N_CLASH_STBD);
if (VIEW >= 2) clashes("cl", N_CLASH_CL);
