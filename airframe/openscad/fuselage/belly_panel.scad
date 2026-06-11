// ============================================================
// belly_panel.scad
// Battery bay belly access panel — Serenity UAV 24" hull.
//
// Rev R (2026-06-11): Rev R baseline — no geometry changes.
// Rev Q (2026-06-07): Initial release.
//   Fits head/bridge section belly opening:
//     6.30 × 2.56 in (160 × 65 mm) cutout.
//   Panel dimensions:
//     Length : 6.30 in (160.0 mm) fore-aft
//     Width  : 2.56 in ( 65.0 mm) lateral
//     Thickness: 0.079 in (2.0 mm) face + 0.059 in (1.5 mm) rebate lip
//   Panel sits in a 0.059 in (1.5 mm) rebate so it is flush with hull skin.
//   Two M3 coin-slot (flathead / button-head) screws — no tool
//   required; a coin or thumbnail turns the slot.
//   EPDM foam tape (0.079 in / 2 mm closed-cell) in rebate acts as dust seal.
//   Estimated panel mass: ~0.013 lbm (~6 g).
//
//   The port and starboard panels are identical; a single spare
//   covers both positions.
//
// Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
//
// Print spec:
//   Material: PETG (non-structural panel; no CF required)
//   Layer:    0.20 mm
//   Walls:    3 perimeters
//   Infill:   15% gyroid
//   Est. mass: ~6 g
//
// References:
//   [1] docs/BATTERY_MOUNT.md §3.3 — belly access panel spec.
//   [2] CLAUDE.md — fabrication standards.
// ============================================================

$fn = 64;

// ------------------------------------------------------------
// Panel dimensions
// Imperial primary: 6.30 × 2.56 in (160 × 65 mm)
// ------------------------------------------------------------
PANEL_L  = 160.0;   // mm — fore-aft length (fits 160 mm / 6.30 in hull opening)
PANEL_W  =  65.0;   // mm — lateral width   = 2.56 in
PANEL_T  =   2.0;   // mm — panel face thickness = 0.079 in

// ------------------------------------------------------------
// Rebate lip around perimeter (locates panel flush in hull)
// ------------------------------------------------------------
REBATE_D  = 1.5;    // mm — rebate depth into hull  = 0.059 in (panel lip stands proud by this)
REBATE_W  = 4.0;    // mm — rebate lip width on panel edge  = 0.157 in

// ------------------------------------------------------------
// Fastener bores (2× M3 coin-slot button-head screws)
// Clearance bore 3.4 mm; coin slot adds no thickness.
// Screws positioned 20 mm from each end, on centreline.
// ------------------------------------------------------------
SCREW_DIA  = 3.4;    // mm — M3 clearance bore
SCREW_CTR  = 20.0;   // mm — distance from each end to screw centre

// ============================================================
// Belly panel
// ============================================================
module belly_panel() {
    difference() {
        union() {
            // --- Main panel face ---
            cube([PANEL_L, PANEL_T, PANEL_W]);

            // --- Rebate lip (raised flange around all four edges) ---
            // This lip fits into the 1.5 mm rebate in the hull, locating
            // the panel flush with the outer mold line.
            translate([0, PANEL_T, 0])
                difference() {
                    cube([PANEL_L, REBATE_D, PANEL_W]);
                    translate([REBATE_W, -0.1, REBATE_W])
                        cube([
                            PANEL_L - 2.0 * REBATE_W,
                            REBATE_D + 0.2,
                            PANEL_W - 2.0 * REBATE_W
                        ]);
                }
        }

        // --- Fore screw bore ---
        translate([SCREW_CTR, -0.1, PANEL_W / 2.0])
            rotate([-90, 0, 0])
                cylinder(h = PANEL_T + REBATE_D + 0.2, d = SCREW_DIA);

        // --- Aft screw bore ---
        translate([PANEL_L - SCREW_CTR, -0.1, PANEL_W / 2.0])
            rotate([-90, 0, 0])
                cylinder(h = PANEL_T + REBATE_D + 0.2, d = SCREW_DIA);
    }
}

// ============================================================
// Render
// ============================================================
belly_panel();
