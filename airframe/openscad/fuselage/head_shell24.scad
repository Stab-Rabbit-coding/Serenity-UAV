// ============================================================
// head_shell24.scad -- Rev H2 (2026-10-27), AIRCRAFT DATUM R2
//
// Head section assembly view in the aircraft datum R2 (X = +port, Y = +aft,
// Z = +dorsal; origin centreline / nose tip / ground on the 3.0 in gear;
// tools/hull_datums.py).  Plan 2026-10-26-001 U1 (head R2 migration).
//
// What this file is
// -----------------
// The PUBLISHED head (airframe/stls/fuselage/head_shell24_2mm_repaired.stl,
// stamped "SerenityUAV AIRCRAFT-FRAME R2") is the fabrication mesh.  It cannot
// be regenerated end to end from its own pipeline (R2 handoff 2026-10-20: the
// pipeline output lacks 3,517 mm^3 in the nose), so the head is never rebuilt
// from this SCAD.  Head features are applied to the published mesh as
// deterministic, idempotent SUBTRACTIVE merges, and head contents are separate
// parts at their installed R2 positions (owner rule: one STL per instance):
//   * nose sensor bay cut + insert ...... bow_sensor_pod.scad,
//       merge_head_sensor_bay.py
//   * head-cell rail / stop / sled / catch ... tools/gen_head_cell_rail.py
// Every station is read from the GENERATED include head_layout_params.scad,
// written by tools/head_layout_fit.py -- the head context gate.
//
// Retired by Rev H2 (not in the published mesh; kept out deliberately):
//   * S1A/S1B VL53L5CX and the 28 mm FPV nose cuts (Rev S2) -- superseded
//     by the twin-pod sensor bay;
//   * Shepherd Book dorsal Faraday tray + panel (Rev S1) -- legacy
//     Y-as-dorsal axis bug, and the nodes now live in pouches (cargo T5c, and
//     Bay A in the head per head_layout_fit);
//   * six X-face aft joint bosses (Rev Q) -- the head/cargo splice collar
//     carries the joint (airframe/WBS.md §1.1.0, 2026-07-06);
//   * jayne_board_bosses() (Rev R2 proposal) -- the Observer board is now
//     pitched on the traced outline, held by the bay insert and a standoff
//     carrier (pending, see the Observer TODO).
// The Rev R1a..S2 history is in git (`git log -- this file`).
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
//         (Rev H2 rewrite authored by Claude Opus 5.5, Anthropic, 2026-10-27)
// License: CERN-OHL-W-2.0 -- see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
// ============================================================

include <../hull_datums.scad>
include <head_layout_params.scad>
use <bow_sensor_pod.scad>

SHOW_SHELL = true;
SHOW_CONTENTS = true;

module head_shell_published() {
    import("../../stls/fuselage/head_shell24_2mm_repaired.stl");
}

module head_contents() {
    // nose sensor bay
    bay_insert();
    sensor_pods();
    observer_board();
    // Bay A pouches (CN1 port, FC1 stbd), on edge
    for (s = [1, -1])
        translate([s > 0 ? 1 : -23, BAYA_Y0, BAYA_Z0]) cube([22, 58, 37]);
    // head cell on its sled + generated rail parts
    translate([-CELL_W / 2, CELL_Y0, BAND_ZC - CELL_H / 2]) cube([CELL_W, CELL_L, CELL_H]);
    import("../../stls/fuselage/head/head_cell_rail.stl");
    import("../../stls/fuselage/head/head_cell_sled.stl");
    import("../../stls/fuselage/head/head_cell_catch.stl");
}

if (SHOW_SHELL) %head_shell_published();
if (SHOW_CONTENTS) head_contents();
