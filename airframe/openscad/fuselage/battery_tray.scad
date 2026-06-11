// ============================================================
// battery_tray.scad
// Battery tray for Serenity UAV 24" hull — 6S 4000 mAh LiPo.
//
// Rev R (2026-06-11): Rev R baseline — no geometry changes.
// Rev Q (2026-06-07): Initial release.
//   CG analysis places battery centroid at ~3.31 in (~84 mm) from nose.
//   Tray spans stations 2.36–5.12 in (60–130 mm) inside head/bridge section.
//   Tray slides on 6×3 mm CF flat bar keel via two bottom rail
//   slots; ±0.79 in (±20 mm) fore-aft adjustment, locks at
//   0.39 in (10 mm) detents via M3 thumb screws.
//
//   Battery: Tattu / Gens Ace 4000 mAh 6S LiPo
//     Nominal dims (Tattu R-Line): 5.59 × 1.97 × 1.50 in (142 × 50 × 38 mm) L×W×H
//     Mass: 1.65 lbm (750 g)
//
//   Interior cavity (battery + 0.118 in / 3 mm foam each side):
//     5.83 × 2.20 × 1.61 in (148 × 56 × 41 mm) L×W×H
//
//   Outer tray dimensions:
//     6.06 × 2.44 × 1.77 in (154 × 62 × 45 mm) L×W×H
//
//   Wall thickness: 0.118 in (3.0 mm) CF-PETG side/front/rear
//   Floor thickness: 0.157 in (4.0 mm) CF-PETG load-bearing
//   Estimated printed mass: ~0.049 lbm (~22 g)
//
//   Retention — three independent mechanisms:
//     1. Forward positive-stop rib (0.157 in / 4 mm CF-PETG).
//     2. Two 0.63 in (16 mm) silicone cam-buckle straps (11.2 lbf / 50 N rated).
//     3. 0.118 in (3 mm) silicone anti-slip/vibration foam on floor and walls.
//   5G crash retention safety factor: 2.7× (see docs/BATTERY_MOUNT.md §3.2).
//   Under 5G load: 36.8 N (8.27 lbf) upward; two straps provide 100 N (22.5 lbf).
//
//   Belly access panel (separate part: belly_panel.scad):
//     6.30 × 2.56 in (160 × 65 mm) PETG panel, 2× M3 coin-slot screws,
//     0.059 in (1.5 mm) rebate.
//
// Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
//
// Print spec:
//   Material: CF-PETG (hardened-steel nozzle required)
//   Layer:    0.15 mm
//   Walls:    4 perimeters
//   Infill:   40% gyroid (load-bearing)
//   Est. mass: ~22 g
//
// Coordinate system (tray-local, origin = tray front-interior corner):
//   X — longitudinal: positive toward nose (forward)
//   Y — vertical:     positive upward
//   Z — lateral:      positive toward port
//
// References:
//   [1] docs/BATTERY_MOUNT.md — CG analysis + retention load case.
//   [2] Tattu R-Line 4000 mAh 6S datasheet, dimensions 142×50×38 mm.
//   [3] CLAUDE.md — fabrication standards (wall thickness, infill, boss spec).
// ============================================================

$fn = 64;    // Facet count for cylinders/spheres

// ------------------------------------------------------------
// Battery dimensions (Tattu R-Line 4000 mAh 6S LiPo)
// Imperial primary: 5.59 × 1.97 × 1.50 in (142 × 50 × 38 mm)
// ------------------------------------------------------------
BATT_L  = 142.0;   // mm — battery length  (fore-aft)   = 5.59 in
BATT_W  =  50.0;   // mm — battery width   (port-stbd)  = 1.97 in
BATT_H  =  38.0;   // mm — battery height  (top-bottom) = 1.50 in

// ------------------------------------------------------------
// Foam padding (3 mm / 0.118 in closed-cell silicone, Shore A 20-30)
// Applied to floor and all four side walls.
// ------------------------------------------------------------
FOAM    = 3.0;     // mm — foam thickness each face  = 0.118 in

// ------------------------------------------------------------
// Wall and floor thicknesses (CF-PETG structural)
// ------------------------------------------------------------
WALL    = 3.0;     // mm — side/front/rear wall thickness  = 0.118 in
FLOOR   = 4.0;     // mm — floor thickness (load-bearing)  = 0.157 in

// ------------------------------------------------------------
// Interior cavity (battery + foam each side)
// Imperial: 5.83 × 2.20 × 1.61 in (148 × 56 × 41 mm)
// ------------------------------------------------------------
CAV_L   = BATT_L + 2 * FOAM;    // 148 mm (5.83 in) fore-aft
CAV_W   = BATT_W + 2 * FOAM;    //  56 mm (2.20 in) port-stbd
CAV_H   = BATT_H + FOAM;        //  41 mm (1.61 in) (foam on floor only; top is open)

// ------------------------------------------------------------
// Outer tray dimensions
// Imperial: 6.06 × 2.44 × 1.77 in (154 × 62 × 45 mm)
// ------------------------------------------------------------
TRAY_L  = CAV_L + 2 * WALL;     // 154 mm (6.06 in)
TRAY_W  = CAV_W + 2 * WALL;     //  62 mm (2.44 in)
TRAY_H  = CAV_H + FLOOR;        //  45 mm (1.77 in)

// ------------------------------------------------------------
// Rail system (CF-BAR-6×3 keel bar interface)
// Two bottom slots run full tray length; rail travel ±0.79 in (±20 mm).
// ------------------------------------------------------------
RAIL_W      = 6.5;    // mm — slot width  (6 mm bar + 0.25 mm clearance each side)  = 0.256 in
RAIL_D      = 3.5;    // mm — slot depth  (3 mm bar + 0.25 mm clearance)             = 0.138 in
RAIL_INSET  = 8.0;    // mm — inset from outer tray edge Z-wise
DETENT_DIA  = 3.2;    // mm — M3 detent screw bore diameter
DETENT_STEP = 10.0;   // mm — detent spacing (10 mm increments along X)
DETENT_N    = 5;      // number of detent positions (covers ±20 mm from centre)

// ------------------------------------------------------------
// Strap anchor slots (two per strap × 2 straps = 4 slots)
// Slots are 4 mm wide × 20 mm long through the tray walls,
// positioned at 1/3 and 2/3 of battery length.
// ------------------------------------------------------------
STRAP_SLOT_W  = 4.0;    // mm — strap slot width
STRAP_SLOT_L  = 20.0;   // mm — strap slot length (through tray wall, Y direction)
STRAP_POS_1   = CAV_L * (1.0 / 3.0) + WALL;   // slot 1 X-centre from tray front
STRAP_POS_2   = CAV_L * (2.0 / 3.0) + WALL;   // slot 2 X-centre from tray front

// ------------------------------------------------------------
// Connector exit slot in rear wall (XT60 + JST-XH-7P balance)
// ------------------------------------------------------------
EXIT_W  = 14.0;   // mm — slot width
EXIT_H  = 10.0;   // mm — slot height

// ------------------------------------------------------------
// Ventilation slots in floor (4× 8×2 mm; covered by stainless mesh)
// ------------------------------------------------------------
VENT_L  = 8.0;    // mm — vent slot length (fore-aft)
VENT_W  = 2.0;    // mm — vent slot width  (port-stbd)
VENT_N  = 4;      // number of vent slots
VENT_MARGIN = 15.0;   // mm — margin from front and rear interior face

// ------------------------------------------------------------
// Forward stop rib (prevents battery sliding forward under braking)
// ------------------------------------------------------------
STOP_T  = 4.0;    // mm — rib thickness (CF-PETG, flush with cavity front wall)
STOP_H  = BATT_H + FOAM + 2.0;  // mm — rib height (full cavity height + clearance)

// ------------------------------------------------------------
// M3 heat-set boss for detent thumb screws (side wall)
// ------------------------------------------------------------
BOSS_OD  = 8.0;   // mm — boss outer diameter (2-wall annulus, per CLAUDE.md)
BOSS_H   = WALL;  // mm — boss flush with outer wall face

// ============================================================
// Main tray body
// ============================================================
module battery_tray() {
    difference() {
        // --- Outer solid block ---
        cube([TRAY_L, TRAY_H, TRAY_W]);

        // --- Interior cavity (open top) ---
        translate([WALL, FLOOR, WALL])
            cube([CAV_L, CAV_H + 1.0, CAV_W]);   // +1 mm so top is fully open

        // --- Connector exit slot in rear wall ---
        // Centred on rear wall (X = TRAY_L - WALL .. TRAY_L), floor-level exit
        translate([
            TRAY_L - WALL - 0.1,
            FLOOR + FOAM,
            (TRAY_W - EXIT_W) / 2.0
        ])
            cube([WALL + 0.2, EXIT_H, EXIT_W]);

        // --- Rail slots on tray underside (two slots, fore-aft) ---
        // Port rail
        translate([-0.1, -0.1, RAIL_INSET - RAIL_W / 2.0])
            cube([TRAY_L + 0.2, RAIL_D + 0.1, RAIL_W]);

        // Stbd rail
        translate([-0.1, -0.1, TRAY_W - RAIL_INSET - RAIL_W / 2.0])
            cube([TRAY_L + 0.2, RAIL_D + 0.1, RAIL_W]);

        // --- Detent screw bores through stbd side wall ---
        // Bores are perpendicular to keel bar (Z-axis), through stbd outer wall
        for (i = [0 : DETENT_N - 1]) {
            detent_x = WALL + VENT_MARGIN + i * DETENT_STEP;
            translate([detent_x, FLOOR / 2.0, TRAY_W + 0.1])
                rotate([0, 0, -90])
                    cylinder(h = WALL + 0.2, d = DETENT_DIA);
        }

        // --- Strap anchor slots through port side wall ---
        // Slot 1 at 1/3 battery length
        translate([
            STRAP_POS_1 - STRAP_SLOT_W / 2.0,
            FLOOR + FOAM,
            -0.1
        ])
            cube([STRAP_SLOT_W, STRAP_SLOT_L, WALL + 0.2]);

        // Slot 2 at 2/3 battery length
        translate([
            STRAP_POS_2 - STRAP_SLOT_W / 2.0,
            FLOOR + FOAM,
            -0.1
        ])
            cube([STRAP_SLOT_W, STRAP_SLOT_L, WALL + 0.2]);

        // --- Strap anchor slots through stbd side wall ---
        translate([
            STRAP_POS_1 - STRAP_SLOT_W / 2.0,
            FLOOR + FOAM,
            TRAY_W - WALL - 0.1
        ])
            cube([STRAP_SLOT_W, STRAP_SLOT_L, WALL + 0.2]);

        translate([
            STRAP_POS_2 - STRAP_SLOT_W / 2.0,
            FLOOR + FOAM,
            TRAY_W - WALL - 0.1
        ])
            cube([STRAP_SLOT_W, STRAP_SLOT_L, WALL + 0.2]);

        // --- Ventilation slots through tray floor ---
        // Evenly spaced along cavity length, avoiding strap zone ±15 mm
        for (i = [0 : VENT_N - 1]) {
            vent_x = WALL + VENT_MARGIN + i * ((CAV_L - 2.0 * VENT_MARGIN) / (VENT_N - 1));
            vent_z = (TRAY_W - VENT_L) / 2.0;  // centred laterally
            translate([vent_x - VENT_L / 2.0, -0.1, vent_z])
                cube([VENT_L, FLOOR + 0.2, VENT_W]);
        }
    }

    // --- Forward stop rib (added, sits at interior front wall) ---
    translate([WALL, FLOOR, WALL])
        cube([STOP_T, STOP_H, CAV_W]);
}

// ============================================================
// Render
// ============================================================
battery_tray();
