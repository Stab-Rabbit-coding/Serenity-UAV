// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  Primary-component STLs published to airframe/stls/
//   are stored directly in hull frame, baked by tools/bake_hull_frame.py
//   (marker 'SerenityUAV HULL-FRAME R1' in the binary STL header).
//   NEVER re-bake a mesh derived from an already-baked file.
//   This file:
//     Part-local print frame centred on its own origin.  Hull-frame
//     placement not yet validated - VERIFY pending (serenity_assembly.py).
// ===========================================================================
// ============================================================
// battery_tray.scad
// Battery tray for Serenity UAV 24" hull — 6S 4000 mAh LiPo.
//
// Rev R1 (2026-07-03): keel-rail slot geometry corrected to match the
//   Rev R1 keel first-principles re-evaluation (docs/structural_analysis.md
//   §4.3): CF-BAR-6X3 is oriented 3 mm lateral (hull X) x 6 mm vertical
//   (hull Z) -- the strong axis vertical, NOT the 6 mm-lateral x 3 mm-
//   vertical orientation this file previously assumed. RAIL_W/RAIL_D swapped
//   accordingly (was 6.5/3.5 mm, now 3.5/6.5 mm). Keel Z at this station is
//   cargo belly Z ≈ +1..+2 mm (§4.2); no change needed to the tray's own
//   floor/rail features for that (Z placement is set by the assembly
//   transform, not this part file).
//   **OPEN ITEM (flagged, not resolved here):** this header's "stations
//   60-130mm inside head/bridge section" text is stale -- the Rev R1 keel
//   spans cargo-to-rear only (hull Y -71..+384mm; head is keelless, see
//   structural_analysis.md §4.1), and other TODO.md entries (§1.1.1 "battery
//   tray in cargo section") now place this tray in the CARGO section, on the
//   cargo keel segment. A separate, older note (TODO.md ~line 2818-2830,
//   2026-06-08 Kaylee placement decision) instead describes a battery boss
//   pattern in the MIDDLE section keel face. These two placements conflict
//   and are NOT reconciled by this edit -- re-verify the tray's actual
//   hull-Y station and update this header before final placement in
//   serenity_assembly.py. See TODO.md §1.1.1.0b.
// Rev R (2026-06-11): Rev R baseline — no geometry changes.
// Rev Q (2026-06-07): Initial release.
//   CG analysis places battery centroid at ~3.31 in (~84 mm) from nose.
//   Tray spans stations 2.36–5.12 in (60–130 mm) inside head/bridge section.
//   [Rev R1: section placement under review -- see Rev R1 note above.]
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
//   Outer tray dimensions (Rev R1, 2026-07-03 -- floor thickened, see below):
//     6.06 × 2.03 × 2.44 in (154 × 51.5 × 62 mm) L×H×W
//     (H includes the forward stop rib, proud of the side walls by design;
//     wall top is 6.06 x 1.949 x 2.44 in / 154 x 49.5 x 62 mm)
//
//   Wall thickness: 0.118 in (3.0 mm) CF-PETG side/front/rear
//   Floor thickness: 0.335 in (8.5 mm) CF-PETG load-bearing -- increased from
//     4.0 mm (Rev R/Q) to clear the corrected 6.5 mm-deep keel-rail slot
//     (RAIL_D, see Rev R1 rail-system note above) with a 2.0 mm solid margin.
//   Estimated mass: solid-CAD-volume x 1.27 g/cm^3 (CF-PETG, per
//     docs/structural_analysis.md §2 convention) = 133 519 mm^3 x 1.27 g/cm^3
//     = ~169.5 g (0.374 lbm), verified 2026-07-03 by rendering this file with
//     `openscad` and computing mesh volume (trimesh). This is a **100%-solid
//     upper bound** -- it does not derate for the 40% gyroid infill specified
//     below, since no infill-vs-wall mass-splitting convention is established
//     elsewhere in this repo; confirm the actual printed mass in the slicer
//     before finalizing the AUW budget (docs/structural_analysis.md §2).
//     This supersedes the earlier ~22 g placeholder, which predates the
//     Rev R1 rail-slot correction and appears to have been a rough estimate,
//     not a computed figure (a first-principles hand check of the original
//     4 mm-floor geometry already gives on the order of 100 g solid).
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
//   Est. mass: ~169.5 g solid-CAD upper bound (Rev R1, 2026-07-03); confirm
//     infill-derated mass in slicer -- see Rev R1 note above.
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
// Rev R1 (2026-07-03): floor thickness increased 4.0 -> 8.5 mm. The rail
// slot depth (RAIL_D) grew from 3.5 to 6.5 mm to clear the keel bar's actual
// 6 mm vertical face (see Rev R1 rail-system note above); FLOOR must exceed
// RAIL_D with a positive margin so the slot does not breach the cavity
// floor. 8.5 mm leaves a 2.0 mm solid margin above the rail slot, matching
// the project's general 2 mm minimum-wall convention (CLAUDE.md).
FLOOR   = 8.5;     // mm — floor thickness (load-bearing)  = 0.335 in

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
// Rev R1 (2026-07-03): keel bar orientation per structural_analysis.md §4.3
// is 3 mm lateral (hull X) x 6 mm vertical (hull Z) -- strong axis vertical.
// In this file's tray-local frame (Z = lateral, Y = vertical), the rail slot
// WIDTH (Z direction) clears the bar's 3 mm lateral face and the rail slot
// DEPTH (Y direction) clears the bar's 6 mm vertical face -- reversed from
// the pre-Rev-R1 6.5/3.5 mm values.
// ------------------------------------------------------------
RAIL_W      = 3.5;    // mm — slot width  (3 mm bar + 0.25 mm clearance each side)  = 0.138 in
RAIL_D      = 6.5;    // mm — slot depth  (6 mm bar + 0.25 mm clearance each side)  = 0.256 in
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
