// gear_box_cf_backbone_placed.scad -- the A1B CF backbone cheeks
// (canonical_leg_r6_3_0in.scad a1b_backbone()) placed at ONE corner in the
// hull frame, for the canonical gear-box fit renders.
//
// Run per corner, with that corner's station (the strut azimuth depends on it):
//   openscad -D 'BAY_STATION="fore"' -D CORNER=0 -o fore_port.stl <this>
//   openscad -D 'BAY_STATION="aft"'  -D CORNER=2 -o aft_port.stl  <this>
// CORNER indexes canonical_leg_r6_3_0in.scad CORNERS (0 fore-port,
// 1 fore-stbd, 2 aft-port, 3 aft-stbd).  Placement repeats hull_legs().
//
// Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
// Stab-Rabbit-coding, per AGENTS.md AI attribution.
// License: CERN-OHL-P-2.0 (hardware source) -- see repo LICENSE files.

CORNER = 0;
include <canonical_leg_r6_3_0in.scad>
PART = "none";      // library mode: the included file emits nothing

c = CORNERS[CORNER];
translate([c[0], c[1], c[2]]) rotate([0, 0, c[3]])
    mirror([0, c[4] < 0 ? 1 : 0, 0]) a1b_backbone();
