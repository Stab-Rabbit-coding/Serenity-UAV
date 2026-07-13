// ============================================================
// cargo_vera_faraday.scad  --  Rev S1 (2026-07-12)
//
// Faraday (EMI) enclosure for the CARGO-bay Vera vision/ToF/laser PCB.
// Standalone printed part (CF-PETG shell + conductive shielding: copper-tape or
// nickel-paint liner, or a 0.5 mm Al can dropped in), enclosing the trapezoidal
// Vera carrier on 4 M2.5 corner standoffs.  The camera/ToF/laser connect by JST
// jumpers (cargo variant), so the harness exits through an EMI cable slot; there
// is no sensor aperture in this enclosure (the nadir camera bezel is separate).
//
// Mates to the cargo belly on the 4 Vera bosses (cargo_sect_shell24.scad
// vera_board_bosses, VERA_HOLES) -- the tray corner bosses align to the same
// pattern.  Shield tied to PGND via a corner solder tab (SHIELD_TAB).
//
// EMI cooling: waveguide-below-cutoff honeycomb vents (6 mm cells; lambda/2 cutoff
// > 25 GHz) on two opposing side walls, matching the DUCT_CELL_D convention of the
// cape Faraday trays.  Lid is a shallow-lip EMI cover (finger-stock or gasket land).
//
// Dimensions: imperial-primary, mm in parentheses.
//   Board envelope: 2.75 x 2.28 in (69.85 x 58.0 mm), trapezoid; tray sized to bbox.
//   Wall: 0.059 in (1.5 mm).  Standoff: 0.315 in (8.0 mm).
//
// VERIFY in FreeCAD/slicer: tray fit inside the cargo bay vs door_bay_cut, GPS,
// ribs (per CLAUDE.md complex-geometry placement rule).  Run a watertight mesh
// check after any change.
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
//        (geometry authored by Claude Opus 4.8)
// License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
// ============================================================

$fn = 48;

// ---- Board envelope + clearances -------------------------------------------
BOARD_L   = 69.85;   // mm -- board long axis (fore-aft)
BOARD_W   = 58.0;    // mm -- board max width (aft/wide end)
CLR       =  2.0;    // mm -- board-to-wall clearance
STAND_H   =  8.0;    // mm -- standoff height (bottom-side component clearance)
TOP_CLR   =  8.0;    // mm -- above-board clearance (5 mm SoM stack + connectors)
BOARD_T   =  1.6;    // mm -- PCB thickness
WALL      =  1.5;    // mm -- tray wall

INT_L = BOARD_L + 2 * CLR;                 // internal length (~73.85)
INT_W = BOARD_W + 2 * CLR;                 // internal width  (~62.0)
INT_D = STAND_H + BOARD_T + TOP_CLR;       // internal depth  (~17.6)
EXT_L = INT_L + 2 * WALL;
EXT_W = INT_W + 2 * WALL;
EXT_D = INT_D + WALL;                      // closed floor, open top (lid separate)

// ---- Standoffs (M2.5) at the Vera corner-hole pattern ----------------------
// Board-local corner holes relative to board centre (mm): (+/-31.9, ...).
// Tray-local: board long -> Y, board width -> X.  [X, Y] offsets from tray centre.
STAND_OD   = 7.0;    // mm -- standoff OD (>= 2-wall around M2.5 insert)
STAND_BORE = 3.4;    // mm -- M2.5 heat-set insert bore
VERA_STAND = [ [-10.3,  31.9], [10.3,  31.9], [25.2, -31.9], [-25.2, -31.9] ];

// ---- EMI vents (waveguide below cutoff) ------------------------------------
VENT_CELL  = 6.0;    // mm -- honeycomb cell (lambda/2 cutoff > 25 GHz)
VENT_WALL  = 1.2;    // mm -- cell wall
VENT_ROWS  = 3;      // cells stacked vertically
VENT_COLS  = 6;      // cells along the wall

// ---- Lid EMI lip + cable slot ----------------------------------------------
LIP_H      = 3.0;    // mm -- lid lip that nests inside the tray for EMI seal
CABLE_W    = 12.0;   // mm -- harness exit slot width (JST-GH ribbon)
CABLE_H    =  5.0;   // mm -- harness exit slot height

// ----------------------------------------------------------------------------
module standoff(p) {
    translate([p[0], p[1], WALL])
    difference() {
        cylinder(h = STAND_H, d = STAND_OD);
        cylinder(h = STAND_H + 0.1, d = STAND_BORE);
    }
}

// Honeycomb vent cutter: a grid of hex cells across a wall panel.
module vent_panel() {
    dx = VENT_CELL + VENT_WALL;
    for (r = [0 : VENT_ROWS - 1])
    for (c = [0 : VENT_COLS - 1])
        translate([c * dx - (VENT_COLS - 1) * dx / 2,
                   r * dx - (VENT_ROWS - 1) * dx / 2,
                   0])
        rotate([90, 0, 0])
        cylinder(h = WALL * 4, d = VENT_CELL, center = true, $fn = 6);
}

// ----------------------------------------------------------------------------
// Module: vera_faraday_tray
//   Open-top tray: floor + 4 walls + 4 standoffs, with waveguide vents on the
//   two long side walls and a harness exit slot on one short wall.
// ----------------------------------------------------------------------------
module vera_faraday_tray() {
    difference() {
        union() {
            // 5-walled shell (closed floor, open top)
            difference() {
                translate([-EXT_L / 2, -EXT_W / 2, 0])
                    cube([EXT_L, EXT_W, EXT_D]);
                translate([-INT_L / 2, -INT_W / 2, WALL])
                    cube([INT_L, INT_W, INT_D + 1]);
            }
            for (p = VERA_STAND) standoff(p);
        }
        // waveguide vents on both long walls (at mid-height)
        translate([0, -EXT_W / 2, EXT_D / 2]) vent_panel();
        translate([0,  EXT_W / 2, EXT_D / 2]) vent_panel();
        // harness exit slot on the +Y short wall (aft), for the JST jumpers
        translate([-CABLE_W / 2, EXT_W / 2 - WALL - 0.1, EXT_D - CABLE_H])
            cube([CABLE_W, WALL + 0.2, CABLE_H + 1]);
    }
}

// ----------------------------------------------------------------------------
// Module: vera_faraday_lid
//   EMI cover with a nesting lip that seats inside the tray walls.
// ----------------------------------------------------------------------------
module vera_faraday_lid() {
    union() {
        translate([-EXT_L / 2, -EXT_W / 2, 0])
            cube([EXT_L, EXT_W, WALL]);
        // inner lip
        translate([-INT_L / 2 + 0.2, -INT_W / 2 + 0.2, -LIP_H])
        difference() {
            cube([INT_L - 0.4, INT_W - 0.4, LIP_H + 0.01]);
            translate([WALL, WALL, -0.1])
                cube([INT_L - 0.4 - 2 * WALL, INT_W - 0.4 - 2 * WALL, LIP_H + 0.2]);
        }
    }
}

// ---- Render: tray, and the lid offset for viewing --------------------------
vera_faraday_tray();
translate([0, 0, EXT_D + 12]) vera_faraday_lid();

// echo key dimensions for console verification
echo(str("Vera Faraday tray external: ", EXT_L, " x ", EXT_W, " x ", EXT_D, " mm"));
echo(str("internal: ", INT_L, " x ", INT_W, " x ", INT_D, " mm; standoffs ", STAND_H, " mm"));
