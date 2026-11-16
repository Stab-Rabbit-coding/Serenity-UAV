// twin_pack_tray.scad -- twin flat battery tray, sleds and aft gate for two
// Tattu R-Line 6S 2200 packs forward of the thrust line in the one-piece
// head+cargo hull (plan 003 R10; tools/twin_head_pack_fit.py proves the fit,
// tools/merge_head_cargo_shell.py builds the hull).  Replaces the single head
// cell rail / sled / catch (tools/gen_head_cell_rail.py) and the cargo
// battery cradle.
//
// Aircraft datum R2 (X port+, Y aft+, Z up), mm.  Parameters are GENERATED:
//     /usr/bin/python3 tools/twin_head_pack_fit.py
//
// Parts (select with PART):
//   "tray"  -- inverted box: ceiling, side walls (bonded to the skin, the
//              gate reports <= 52 mm^3 skin seat), FULL floor (the packs step
//              sideways into their lanes, so edge lips cannot carry them), and
//              the forward stop plate.  Open aft for loading.  A 1.5 mm
//              chamfered ramp at the aft floor edge takes the sled up from the
//              corridor (Zc 189.5) to the tray floor (Zc 191).
//   "sled"  -- one per pack: 1 mm pan + 2 mm nose / tail lips, a tail tab
//              that keys into the gate.
//   "gate"  -- hinged aft bar across both lanes with a pocket per sled tail
//              tab: holds both sleds forward against the stop AND laterally
//              in their lanes.  Hinge on the stbd wall, latch on the port
//              wall (latch hardware per docs/BATTERY_MOUNT.md §8 statics,
//              re-run for 2 x 321 g -- OPEN item).
//   "assy"  -- all of the above in place, packs shown as ghost boxes.
//
// Material: SLS DuraForm PA CF (docs/SLS_MATERIAL_SELECTION_3DSYSTEMS.md).
//
// Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the
// author's direction, 2026-10-31, per AGENTS.md §3 AI attribution.
// License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0
// (SPDX-License-Identifier: CERN-OHL-W-2.0)

include <twin_pack_tray_params.scad>

PART = "assy";
$fn = 32;

Z0 = TRAY_ZC - TRAY_H / 2;     // band floor
Z1 = TRAY_ZC + TRAY_H / 2;     // band ceiling
HW = TRAY_W / 2;
RAMP = TRAY_ZC - CORRIDOR_ZC;  // 1.5 mm step from the corridor
GATE_T = 4.0;
TAB_W = 10.0;
TAB_L = 3.0;
TAB_H = 6.0;
SLED_CLR = 0.5;                // sled to lane wall / neighbour, per side

module tray() {
    difference() {
        union() {
            // ceiling
            translate([-HW - RAIL_T, TRAY_Y0, Z1]) cube([TRAY_W + 2 * RAIL_T, TRAY_Y1 - TRAY_Y0, RAIL_T]);
            // side walls
            for (s = [-1, 1])
                translate([s > 0 ? HW : -HW - RAIL_T, TRAY_Y0, Z0 - RAIL_T])
                    cube([RAIL_T, TRAY_Y1 - TRAY_Y0, TRAY_H + RAIL_T]);
            // full floor
            translate([-HW, TRAY_Y0, Z0 - RAIL_T]) cube([TRAY_W, TRAY_Y1 - TRAY_Y0, RAIL_T]);
            // forward stop plate
            translate([-HW - RAIL_T, TRAY_Y0 - STOP_T, Z0 - RAIL_T])
                cube([TRAY_W + 2 * RAIL_T, STOP_T, TRAY_H + 2 * RAIL_T]);
        }
        // aft entry ramp: chamfer the floor's aft edge down to the corridor floor
        translate([-HW - 1, TRAY_Y1, Z0 - RAMP])
            rotate([0, 90, 0]) linear_extrude(TRAY_W + 2)
                polygon([[0, 0], [-RAMP - 0.01, 0], [0, -6]]);
    }
}

module sled() {
    // local: lane centred on X 0, Y from the stop face
    w = LANE_W - 2 * SLED_CLR;
    L = CELL_L + 2 * SLED_LIP;
    translate([-w / 2, 0, 0]) {
        cube([w, L, SLED_FLOOR_T]);                       // pan
        cube([w, SLED_LIP, 8]);                           // nose lip
        translate([0, L - SLED_LIP, 0]) cube([w, SLED_LIP, 8]);  // tail lip
        translate([w / 2 - TAB_W / 2, L, 0]) cube([TAB_W, TAB_L, TAB_H]);  // gate tab
    }
}

module gate() {
    difference() {
        translate([-HW, 0, 0]) cube([TRAY_W, GATE_T, TAB_H + 6]);
        for (s = [-1, 1])
            translate([s * LANE_X - TAB_W / 2 - 0.3, -0.01, -0.01])
                cube([TAB_W + 0.6, TAB_L - 0.5, TAB_H + 0.3]);
    }
}

module placed_sleds() {
    for (s = [-1, 1])
        translate([s * LANE_X, TRAY_Y0, Z0]) sled();
}

module placed_gate() {
    translate([0, TRAY_Y0 + CELL_L + 2 * SLED_LIP + TAB_L - (TAB_L - 0.5), Z0]) gate();
}

if (PART == "tray") tray();
else if (PART == "sled") sled();
else if (PART == "gate") gate();
else {
    tray();
    placed_sleds();
    placed_gate();
    for (s = [-1, 1])
        %translate([s * LANE_X - CELL_H / 2, TRAY_Y0 + SLED_LIP, Z0 + SLED_FLOOR_T])
            cube([CELL_H, CELL_L, CELL_W]);
}
