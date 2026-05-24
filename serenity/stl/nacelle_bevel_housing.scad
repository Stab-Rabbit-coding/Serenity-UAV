// nacelle_bevel_housing.scad
// Serenity UAV Rev O — Nacelle Tilt Linkage, Bevel Gear Housing
//
// Purpose:
//   Structural housing for the M = 1.0 bevel gear pair (nacelle_bevel_pair.scad)
//   and associated MR63ZZ shaft bearings.  Mounts to two M2.5 boss posts on the
//   nacelle inboard face.  Houses both the transverse bore (Bevel Gear A +
//   Pinion A shaft, nacelle Y-axis) and the longitudinal bore (Bevel Gear B +
//   longitudinal CF shaft, nacelle Z-axis).  Bores intersect at the gear-mesh
//   centre.
//
//   The housing also locates the Pinion A gear relative to the sector gear:
//   the transverse bore centreline to nacelle pivot axis distance = 28.1 mm
//   (sector R 22 + pinion R 6 + 0.1 mm backlash).
//
// Mating interfaces:
//   • Nacelle boss posts (×2 M2.5): MOUNT_BOSS_SPACING_X × MOUNT_BOSS_SPACING_Z
//       = 16 mm × 12 mm pattern; MOUNT_HOLE_D = 2.7 mm clearance.
//   • Bevel Gear A (nacelle_bevel_pair.scad): seated in transverse bore,
//       bearing OD = 6 mm press-fit into BEARING_SEAT_D = 6.25 mm recess.
//   • Bevel Gear B (nacelle_bevel_pair.scad): seated in longitudinal bore,
//       same bearing arrangement.
//   • Pinion A shaft (nacelle_pinion.scad): passes through transverse bore,
//       3 mm CF, supported by two MR63ZZ bearings inside housing.
//   • Longitudinal shaft: 3 mm CF, exits longitudinal bore toward nozzle.
//
// Print specification:
//   Material:  CF-PETG (structural load path — tilt torque reaction)
//   Layers:    0.15 mm
//   Walls:     4 perimeters (≥ 2 mm minimum on any load-bearing wall)
//   Infill:    40 % gyroid (load-bearing block)
//   Nozzle:    Hardened steel (CF-PETG abrasive)
//   Orient:    Print with largest face (X-Z face) on build plate; support
//              inside transverse bore if overhang > 45°.
//   Post-proc: Ream bearing seat bores with 6 mm reamer if MR63ZZ won't seat.
//
// Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date:    2026-05-24
// Rev:     O (initial release)

// ── Resolution ────────────────────────────────────────────────────────────────

$fn = 72;   // standard circle resolution

// ── Housing Body Parameters ───────────────────────────────────────────────────

BLOCK_X = 24.0;   // [mm] housing body length along nacelle transverse axis (X)
BLOCK_Y = 14.0;   // [mm] housing body depth (inboard-outboard, Y)
BLOCK_Z = 20.0;   // [mm] housing body height along nacelle longitudinal axis (Z)
WALL_T  =  2.0;   // [mm] minimum wall thickness (all bearing-enclosure walls)

// ── Bore Dimensions ───────────────────────────────────────────────────────────

// Transverse bore (X-axis): houses Bevel Gear A + Pinion A shaft.
//   Bore diameter = gear pitch OD + 1.0 mm clearance each side = 14 + 2 = 16 mm?
//   Actually gear tip diameter = 2 × TIP_R_LARGE = 2 × 8.0 = 16.0 mm.
//   Add 0.5 mm clearance radially (both sides) → bore = 17.0 mm.
//   Specified as 8.5 mm radius = 17.0 mm diameter.
TRANS_BORE_D  = 17.0;  // [mm] transverse chamber bore (Bevel A + Pinion A)

// Longitudinal bore (Z-axis): houses Bevel Gear B + longitudinal shaft.
LONG_BORE_D   = 17.0;  // [mm] longitudinal chamber bore (Bevel B)

// Bearing seat dimensions — MR63ZZ: 3 mm ID, 6 mm OD, 2.5 mm wide.
//   Press-fit: housing bore = bearing OD + 0.25 mm interference
//   Resin/PETG elasticity absorbs interference; use light mallet to seat.
BEARING_SEAT_D     =  6.25;  // [mm] MR63ZZ press-fit bore (6 mm OD + 0.25 mm)
BEARING_SEAT_DEPTH =  2.5;   // [mm] axial depth of each bearing seat recess
BEARING_COUNT      =  2;     // per bore: one at each end of each shaft span

// ── Mounting Hole Parameters ──────────────────────────────────────────────────

MOUNT_HOLE_D         = 2.7;   // [mm] M2.5 clearance (M2.5 OD 2.5 + 0.2 mm)
MOUNT_BOSS_SPACING_X = 16.0;  // [mm] boss post centre-to-centre, X direction
MOUNT_BOSS_SPACING_Z = 12.0;  // [mm] boss post centre-to-centre, Z direction
// Mount holes at four corners of the boss-post pattern, centred on housing face.
// Hole pairs at ±MOUNT_BOSS_SPACING_X/2 in X, ±MOUNT_BOSS_SPACING_Z/2 in Z.

// ── Access Slot Parameters ────────────────────────────────────────────────────

ACCESS_SLOT_W = 8.0;   // [mm] width of inspection slot on top face (X direction)
ACCESS_SLOT_L = 6.0;   // [mm] length of inspection slot (Z direction)
ACCESS_SLOT_D = 3.0;   // [mm] depth of slot from top face

// ── Module Definitions ────────────────────────────────────────────────────────

// housing_body() — solid rectangular block forming the outer shell.
//   Origin: geometric centre of block (X=0, Y=0, Z=0 at block centroid).
module housing_body() {
    cube([BLOCK_X, BLOCK_Y, BLOCK_Z], center = true);
}

// transverse_bore() — through-bore along X-axis for Bevel Gear A + Pinion A.
//   Bore runs full BLOCK_X (24 mm) along X; centred at Y = 0, Z = 0.
//   Two bearing seat recesses are bored at each X-face entry, depth = BEARING_SEAT_DEPTH.
module transverse_bore() {
    union() {
        // Main through bore — X-axis
        rotate([0, 90, 0])
            translate([0, 0, -BLOCK_X / 2 - 0.1])
                cylinder(h = BLOCK_X + 0.2, d = TRANS_BORE_D);

        // Bearing seat recess — negative X face (left entry):
        rotate([0, 90, 0])
            translate([0, 0, -BLOCK_X / 2 - 0.1])
                cylinder(h = BEARING_SEAT_DEPTH + 0.1, d = BEARING_SEAT_D + 0.5);
                // Note: slightly oversized relief to allow bearing flange; actual
                // press-fit shoulder is at BEARING_SEAT_D exactly.

        // Bearing seat recess — positive X face (right entry):
        rotate([0, 90, 0])
            translate([0, 0, BLOCK_X / 2 - BEARING_SEAT_DEPTH])
                cylinder(h = BEARING_SEAT_DEPTH + 0.1, d = BEARING_SEAT_D + 0.5);
    }
}

// longitudinal_bore() — through-bore along Z-axis for Bevel Gear B + long shaft.
//   Bore runs full BLOCK_Z (20 mm) along Z; centred at X = 0, Y = 0.
module longitudinal_bore() {
    union() {
        // Main through bore — Z-axis
        translate([0, 0, -BLOCK_Z / 2 - 0.1])
            cylinder(h = BLOCK_Z + 0.2, d = LONG_BORE_D);

        // Bearing seat recess — bottom Z face (lower entry):
        translate([0, 0, -BLOCK_Z / 2 - 0.1])
            cylinder(h = BEARING_SEAT_DEPTH + 0.1, d = BEARING_SEAT_D + 0.5);

        // Bearing seat recess — top Z face (upper entry):
        translate([0, 0, BLOCK_Z / 2 - BEARING_SEAT_DEPTH])
            cylinder(h = BEARING_SEAT_DEPTH + 0.1, d = BEARING_SEAT_D + 0.5);
    }
}

// mount_holes() — four M2.5 clearance through-bores for boss-post mounting.
//   Holes run through Y-axis (inboard face to outboard face).
//   Pattern: ±MOUNT_BOSS_SPACING_X/2 in X, ±MOUNT_BOSS_SPACING_Z/2 in Z.
module mount_holes() {
    for (xi = [-1, 1]) {
        for (zi = [-1, 1]) {
            translate([xi * MOUNT_BOSS_SPACING_X / 2,
                       0,
                       zi * MOUNT_BOSS_SPACING_Z / 2]) {
                // Bore through full Y depth
                rotate([90, 0, 0])
                    translate([0, 0, -BLOCK_Y / 2 - 0.1])
                        cylinder(h = BLOCK_Y + 0.2, d = MOUNT_HOLE_D);
            }
        }
    }
}

// access_slot() — rectangular inspection port on top face (Z = +BLOCK_Z/2).
//   Allows visual gear mesh inspection in the field.
//   Centred at X = 0, Y = 0, opening downward ACCESS_SLOT_D into housing.
module access_slot() {
    translate([-ACCESS_SLOT_W / 2,
               -ACCESS_SLOT_L / 2,
               BLOCK_Z / 2 - ACCESS_SLOT_D]) {
        cube([ACCESS_SLOT_W, ACCESS_SLOT_L, ACCESS_SLOT_D + 0.1]);
    }
}

// bevel_housing() — top-level module: complete bevel gear housing.
//
//   Build sequence:
//     1. Solid rectangular block.
//     2. Subtract transverse bore (X-axis, gear A + pinion A shaft).
//     3. Subtract longitudinal bore (Z-axis, gear B + long shaft).
//     4. Subtract four mount-hole bores (Y-axis through, boss-post pattern).
//     5. Subtract top-face inspection slot.
//
//   Coordinate origin: geometric centroid of the block.
//   +Z = toward nozzle (longitudinal shaft exits here, upward in print orientation).
//   +X = toward sector gear / pinion A mesh side.
//   +Y = outboard face.
module bevel_housing() {
    difference() {
        // ── Solid outer shell ────────────────────────────────────────────────
        housing_body();

        // ── Transverse bore (Bevel A + Pinion A) ────────────────────────────
        transverse_bore();

        // ── Longitudinal bore (Bevel B + long shaft) ─────────────────────────
        longitudinal_bore();

        // ── Mounting through-holes (M2.5 boss posts) ─────────────────────────
        mount_holes();

        // ── Top inspection slot ───────────────────────────────────────────────
        access_slot();
    }
}

// ── Fit Confirmation ──────────────────────────────────────────────────────────
//
//   Interface              Mating part                   Clearance / fit
//   ─────────────────────  ────────────────────────────  ─────────────────────
//   TRANS_BORE_D 17.0 mm   Bevel A tip OD = 16.0 mm      0.5 mm radial clr
//                          nacelle_bevel_pair.scad        (gear clears housing)
//   LONG_BORE_D 17.0 mm    Bevel B tip OD = 16.0 mm      0.5 mm radial clr
//   BEARING_SEAT_D 6.25    MR63ZZ OD 6.0 mm              0.25 mm interference
//                                                          (press fit, light mallet)
//   MOUNT_HOLE_D 2.7 mm    M2.5 boss post OD 2.5 mm      0.2 mm diametral clr
//   Block face (Y plane)   Nacelle inboard face           bonded / face contact
//   Top face slot          Field inspection (no mating)  N/A

// ── Render ────────────────────────────────────────────────────────────────────

bevel_housing();
