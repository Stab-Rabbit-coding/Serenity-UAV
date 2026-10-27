// ============================================================
// bow_sensor_pod.scad -- Rev H2 (2026-10-27), AIRCRAFT DATUM R2
//
// Nose sensor bay for the Serenity 24 in hull: a recessed TWIN-POD bay under
// the nose brow, matching the canon arrangement (owner-approved 2026-10-27):
//   * REF-CAD-002 Nick Henning, close-bridge render: two identical rectangular
//     pods side by side in a recessed, vented bay under the brow;
//   * REF-CAD-003 QMx Official Serenity Blueprints, Sheet 3 Bow Elevation: two
//     bow fixtures either side of the centreline below the bridge window.
// Layout: camera pod PORT (+X), ToF pod STARBOARD (-X), laser exit on the CL
// in the web between them.  All three are SOLDERED TO THE LEADING EDGE of the
// Observer board (owner 2026-10-27), so the board is pitched along the bay
// axis BAY_N (the 40 deg bow-flat normal) and its outline is the traced
// inner-wall outline OBS_OUTLINE.
//
// SUPERSEDES Rev R1c (the three overlapping pockets cut on the bow flat in the
// legacy part-local frame) and bow_sensor_faceplate.scad (the bay insert's
// window face replaces the faceplate).  The old pockets lie inside BAY cut.
//
// Coordinates: aircraft datum R2 (X = +port, Y = +aft, Z = +dorsal, origin
// centreline / nose tip / ground on the 3.0 in gear) -- tools/hull_datums.py.
// Every number comes from the GENERATED include head_layout_params.scad,
// written by tools/head_layout_fit.py (single source; the same file gates the
// layout against the published shell).  Nothing below is typed twice.
//
// ToF: Broadcom AFBR-S50LX85D (12.4 x 7.6 x 7.9 mm, optics on the top face)
//   on a right-angle carrier -- recommended, pending REFERENCES.md entry
//   (official datasheet docs.broadcom.com/doc/AFBR-S50LX85D-DS).  TFmini-S
//   [REF-SENSOR-002] REJECTED: maker PRC-domiciled (AGENTS.md §5).
// Camera: NOT selected -- requirement: full-cone FoV <= CAM_FOV_DEG (54 deg is
//   the widest the bay passes unobstructed) and body within POD_W x POD_T.
// Laser: 520 nm source per docs/OBSERVER_LASER_ANALYSIS.md, Class 2 at both
//   sites [REF-IEC-002, REF-FDA-001]; module within LASER_D x LASER_L.
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
//         (Rev H2 geometry authored by Claude Opus 5.5, Anthropic, 2026-10-27)
// License: CERN-OHL-W-2.0 -- see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
// ============================================================

include <../hull_datums.scad>
include <head_layout_params.scad>

$fn = 48;

// Frame placing local (x lateral, y board-normal, z outward axis) at point c.
module bay_frame(c) {
    multmatrix([[1, BAY_BN[0], BAY_N[0], c[0]],
                [0, BAY_BN[1], BAY_N[1], c[1]],
                [0, BAY_BN[2], BAY_N[2], c[2]],
                [0, 0, 0, 1]]) children();
}

function edge_w() = 2 * (POD_XC + POD_W / 2);

// ----------------------------------------------------------------------------
// bay_cutter(): material removed from the published head (forward of the
// window face, out through the nose).  Applied by
// airframe/blender-scripts/merge_head_sensor_bay.py.
// ----------------------------------------------------------------------------
module bay_cutter() {
    bay_frame(BAY_FACE + BAY_N * 15)
        cube([edge_w() + 2 * BAY_WALL, POD_T + 2 * BAY_WALL, 30], center = true);
}

// ----------------------------------------------------------------------------
// bay_insert(): printed CF-PETG liner bonded into the cut -- side walls,
// ceiling, floor and the window face (back wall) with the three apertures.
// UNTRIMMED here: the fabrication STL (head/bow_sensor_bay_insert.stl) is
// trimmed to the head's outer envelope by merge_head_sensor_bay.py so no lip
// stands proud of the outer mould line.
// ----------------------------------------------------------------------------
module bay_insert() {
    difference() {
        bay_frame(BAY_FACE + BAY_N * (BAY_INSERT_L / 2 - BAY_WALL / 2))
            cube([edge_w() + 2 * BAY_WALL, POD_T + 2 * BAY_WALL, BAY_INSERT_L + BAY_WALL],
                 center = true);
        bay_frame(BAY_FACE + BAY_N * (BAY_INSERT_L / 2 + 0.01))
            cube([edge_w(), POD_T, BAY_INSERT_L], center = true);
        for (a = [[POD_XC, POD_W - 2], [-POD_XC, POD_W - 2], [0, LASER_D]])
            bay_frame(BAY_FACE + [a[0], 0, 0])
                cylinder(h = 6, d = a[1], center = true);
    }
}

// ----------------------------------------------------------------------------
// Sensor and board envelopes (reference solids for the assembly view).
// ----------------------------------------------------------------------------
module sensor_pods() {
    for (xc = [POD_XC, -POD_XC])   // camera port, ToF stbd
        bay_frame(BAY_FACE + [xc, 0, 0] - BAY_N * (POD_D / 2))
            cube([POD_W, POD_T, POD_D], center = true);
    bay_frame(BAY_FACE - BAY_N * (LASER_L / 2))
        cylinder(h = LASER_L, d = LASER_D, center = true);
}

// Observer board on the traced outline: local x lateral, y = u aft along the
// board (-BAY_N), z = roof-side face normal (-BAY_BN).
module observer_board(thk = 1.6) {
    multmatrix([[1, -BAY_N[0], -BAY_BN[0], OBS_LEAD[0]],
                [0, -BAY_N[1], -BAY_BN[1], OBS_LEAD[1]],
                [0, -BAY_N[2], -BAY_BN[2], OBS_LEAD[2]],
                [0, 0, 0, 1]])
        linear_extrude(height = thk) polygon(OBS_OUTLINE);
}

// Standalone preview: the bay insert, pods and board in R2.
bay_insert();
%sensor_pods();
%observer_board();
