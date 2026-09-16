// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See AGENTS.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  MODELLED DIRECTLY IN HULL FRAME; the exported STL imports
//   into serenity_assembly.py at identity placement.
// ===========================================================================
// ============================================================
// chin_node_shelf.scad -- Rev T5e (2026-09-16)
// Shelf for the two remaining cargo-section avionics nodes (N1 CN2 Inara,
// N3 CN3 River: PB2I + cape in a Faraday pouch, 58 x 37 x 22 each) lying
// FLAT on the chin floor under the battery nose, Y -58..0, Z 66..88, side by
// side with a shared 10 mm cable channel on the centreline (connector edges
// inboard).  Every station is from cargo_layout_t5_params.scad (GENERATED
// by tools/cargo_layout_fit.py --write-scad; PASS 2026-09-16).
//
// WHY HERE.  The chin FLANKS beside the battery nose were measured 0.2-0.5
// mm short on 2026-09-15 and again on 2026-09-16 (the hull is 2.7 mm
// asymmetric there); the shoulder pockets outboard of the tilt brackets take
// no 35 mm board.  The chin FLOOR under the battery nose (forward of the
// hoisted payload box, Y < 4.7) is 113 mm wide at Z 66..88 and was clear
// first try, both sides, at the 2 mm static budget.
//
// WHAT IT IS.  A 2.4 mm CF-PETG plate, 84 x 53.6 mm (Y -52..+1.6), with a 4 mm lip around
// each pouch pocket and a centre rib that forms the cable channel.  Its
// forward 7 mm (Y -52..-45) is a SILL that lies on the chin floor (Z 60-62,
// rising forward) and takes the two forward M3 screws into floor bosses; the
// aft pair of bosses rise ~20 mm from the ramp fairing's inner face to the
// same plate underside (merge_cargo_interior.py t5_chin_shelf_bosses).  The
// pouches are held by two 16 mm silicone cam straps each, through slots in
// the plate (BATT-STRAP-CAM, same part as the battery).
//
// LOADS.  2 x ~90 g (node + pouch, VERIFY at first article) = 1.77 N at 1 g,
//   4.4 N at the 2.5 g hard-landing case: plate as a 58 mm simply supported
//   beam 84 wide -> M = 4.4 x 0.058 / 8 = 0.032 N.m; Z = 84 x 2.4^2 / 6 =
//   81 mm^3 -> 0.4 MPa.  Nothing.  The legs (2 x 6 x 6 mm, 20 mm) see 2.2 N
//   each.  First plate mode (simply supported, 0.18 kg on 84 x 58 x 2.4 mm
//   CF-PETG, E ~ 4 GPa): k ~ 48 E I / L^3 = 48 x 4000 x 97 / 195112 ~ 95
//   N/mm -> f_n ~ 115 Hz, well above the airframe modes and below the 470 Hz
//   EDF shaft rate (transmissibility ~ 0.06).
//
// PRINT ORIENTATION: plate flat, pockets up.  3 perimeters, 30 % gyroid,
//   CF-PETG.
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// AI note: Written by Claude (model: Claude Opus 5, Anthropic) under the
//   author's direction, 2026-09-16, per AGENTS.md SS3 AI attribution.
// License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
// ============================================================

include <cargo_layout_t5_params.scad>

$fn = 48;
EPS = 0.01;

LIP_H      = 4.0;                  // pocket lip above the plate
LIP_T      = 1.6;
M3_CLR     = 3.4;
STRAP_SLOT = [4.0, 20.0];          // Y x X through-slots for the 16 mm cam straps
STRAP_Y    = [SHELF_Y0 + 8.0, N_CHIN_Y1 - 12.0];

X1 = N_CHIN_X_IN + NODE_H;         // port outboard face (-127.85)
X0 = 2 * X_CL - X1;                // stbd (-211.85)
Y0 = SHELF_Y0;   Y1 = SHELF_Y1;   // -52..+1.6: clear of the head/cargo collar ring (Y < -53.5) and the payload (Y > 4.7)
Z0 = SHELF_Z0;                     // plate underside (63.6)

module plate() {
    difference() {
        translate([X0, Y0, Z0]) cube([X1 - X0, Y1 - Y0, SHELF_T]);
        // 4 x M3 to the floor bosses
        for (b = SHELF_BOSS) translate([b[0], b[1], Z0 - 1]) cylinder(d = M3_CLR, h = SHELF_T + 2);
        // strap slots: 2 straps per node, at the pouch's outboard and inboard thirds
        for (y = STRAP_Y, sx = [-1, 1], k = [1, 2])
            translate([X_CL + sx * (NODE_CABLE / 2 + k * NODE_H / 3) - STRAP_SLOT[1] / 2, y - STRAP_SLOT[0] / 2, Z0 - 1])
                cube([STRAP_SLOT[1], STRAP_SLOT[0], SHELF_T + 2]);
        // lightening windows under each pouch centre
        for (sx = [-1, 1])
            translate([X_CL + sx * (NODE_CABLE / 2 + NODE_H / 2) - 10, Y0 + 20, Z0 - 1]) cube([20, 18, SHELF_T + 2]);
    }
}

module lips() {
    // an aft lip behind each pocket (Y 0..1.6) and an inboard lip standing
    // in the cable channel (1.6 mm x 4 mm at the channel floor -- the
    // connectors sit mid-height on the 22 mm stack, above it).  No outboard
    // or forward lip: the plate ends at the pouch's outboard face, the pouch
    // overhangs the plate's forward edge by 6 mm over the collar ring, and
    // the two cam straps take the lateral and forward load.
    for (sx = [-1, 1]) {
        xi = X_CL + sx * NODE_CABLE / 2;                 // pocket inboard face
        xo = X_CL + sx * (NODE_CABLE / 2 + NODE_H);      // pocket outboard face
        xa = min(xi, xo); xb = max(xi, xo);
        translate([xa, N_CHIN_Y1, Z0 + SHELF_T - EPS]) cube([xb - xa, LIP_T, LIP_H]);   // aft lip, behind the pouch
        translate([sx > 0 ? xi - LIP_T : xi, Y0, Z0 + SHELF_T - EPS]) cube([LIP_T, Y1 - Y0, LIP_H]);
    }
}

union() { plate(); lips(); }
