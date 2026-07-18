// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame: X = +port (left), Y = +aft (back), Z = +dorsal (up); origin =
//   SerenityAssembly.FCStd world origin.  This file is authored DIRECTLY in
//   hull frame and is boolean-unioned into the baked cargo shell at merge time
//   (same pattern as generate_cargo_hinge_retention.py) — a new self-contained
//   generator, NOT an edit to the broken-legacy cargo_sect_shell24.scad.
// ===========================================================================
// =============================================================================
// cargo_spar_drive.scad
// Serenity UAV — Rev R2 — Cargo-bay tilt-spar drive + cableway ends
// =============================================================================
//
// Author  : Steve Griffing (drafted by Claude Opus 4.8)
// License : CC BY 4.0
// Date    : 2026-07-18
//
// Provides, inside the cargo section, for EACH wing (port + stbd), the cargo-bay
// end of the rotating 8 mm tilt-spar drive plus the wing-root cableway exits:
//   1. ROOT BEARING SEAT — F688ZZ (8×16×5) that supports the inboard end of the
//      rotating spar; the servo turns the spar, the nacelle tilts.
//   2. SERVO MOUNT — DS3218MG (≈40×20×40 mm) bracket below the spar; drives a
//      horn on the spar via a 2 mm pushrod + M2 clevis (repo hardware).  Output
//      axis parallel to the spar (X); arm sweeps the Y–Z plane.  Linkage throw
//      (arm/horn lengths for the −5°..140° range) is tuned at assembly.
//   3. CABLEWAY ENDS — two Ø7 guide tubes continuing the wing double-D EDF
//      power/signal conduits from the wing root into the cargo bay toward the
//      ESC/PDB bays (per user note 2026-07-18).
//
// Hull-frame positions (from tools/bake_hull_frame.py wing translations and
// wings_s1223_revo.scad: spar at chord-station 22, cableway at 0.48·chord,
// camber-midline height):
//   Port wing bake (−81, −7, +58): spar Y=+15, cableway Y≈+55, root at X≈−81.
//   Stbd wing bake (−262, −12, +58): spar Y=+10, cableway Y≈+50, root at X≈−250.
//   Spar/cableway height Z≈+66 (camber midline + 58).  Inboard is −X for port
//   (toward ship CL X≈−170) and +X for stbd.
//
// Render (visual/overlay): openscad -o cargo_spar_drive.stl cargo_spar_drive.scad
// Merge: union into cargo_sect_shell24_2mm_repaired.stl during interior merge.
// =============================================================================

$fn = 48;

// ── Spar / bearing ───────────────────────────────────────────────────────────
SPAR_BORE_D   =  8.15;   // [mm] rotating-spar clearance bore
BRG_OD        = 16.0;    // [mm] F688ZZ outer diameter (press-fit seat)
BRG_SEAT_D    = 15.95;   // [mm] seat bore (0.025 mm/side interference)
BRG_W         =  5.0;    // [mm] bearing width
BRG_BOSS_OD   = 22.0;    // [mm] bearing boss OD (≥ 3 mm wall around the seat)
BRG_BOSS_L    = 10.0;    // [mm] boss length (seat + backing)

// ── DS3218MG servo ────────────────────────────────────────────────────────────
SRV_L = 40.0; SRV_W = 20.0; SRV_H = 40.0;   // [mm] body
SRV_LUG_L = 54.0;                            // [mm] tab-to-tab length
SRV_WALL = 2.5;                              // [mm] pocket wall

// ── Cableway (double-D, matches wings_s1223_revo.scad) ───────────────────────
CABLE_BORE_D = 7.0;      // [mm]
CABLE_SEP    = 8.0;      // [mm] chord (Y) centre-to-centre
CABLE_TUBE_OD = 10.0;    // [mm] guide-tube OD
CABLE_TUBE_L  = 28.0;    // [mm] guide-tube length inward from the wall

OUTBOARD_WALL_X = -72.7; // [mm] cargo outboard (wing-side) wall

// Per-side data: [spar_Y, cable_Y, spar_Z, x_root, inboard_sign]
PORT = [15, 55, 66, -81,  -1];
STBD = [10, 50, 66, -250, +1];

// =============================================================================
// ── Module: root_bearing_seat ──────────────────────────────────────────────
// Boss holding an F688ZZ at (spar_Y, spar_Z), 9 mm inboard of the wing root,
// with the spar bore through it.  A web ties it up from the surrounding shell.
module root_bearing_seat(spar_y, spar_z, x_root, inb) {
    bx = x_root + inb * 9;                  // 9 mm inboard of root
    translate([bx, spar_y, spar_z]) rotate([0, inb * 90, 0])
        difference() {
            cylinder(d = BRG_BOSS_OD, h = BRG_BOSS_L, center = true);
            // bearing seat (opens toward the wing/outboard face)
            translate([0, 0, BRG_BOSS_L/2 - BRG_W])
                cylinder(d = BRG_SEAT_D, h = BRG_W + 0.1);
            // spar clearance bore all the way through
            cylinder(d = SPAR_BORE_D, h = BRG_BOSS_L + 0.2, center = true);
        }
    // support web: boss down to the cargo floor plane (Z≈20) for a load path
    hull() {
        translate([bx, spar_y, spar_z]) rotate([0, inb * 90, 0])
            cylinder(d = BRG_BOSS_OD, h = 0.5, center = true);
        translate([bx - 6, spar_y - 4, 22]) cube([12, 8, 1]);
    }
}

// =============================================================================
// ── Module: servo_mount ─────────────────────────────────────────────────────
// DS3218 three-wall cradle below the spar, output axis along X (parallel to
// spar).  The open top receives the servo; two lug tabs screw down.  Linkage
// (arm→pushrod→spar horn) is assembly hardware.
module servo_mount(spar_y, spar_z, x_root, inb) {
    sx = x_root + inb * 30;                  // servo body centred 30 mm inboard
    sz = spar_z - 30;                        // 30 mm below the spar
    translate([sx, spar_y, sz])
        difference() {
            cube([SRV_L + 2*SRV_WALL, SRV_W + 2*SRV_WALL, SRV_H*0.6 + SRV_WALL],
                 center = true);
            translate([0, 0, SRV_WALL])
                cube([SRV_L + 0.4, SRV_W + 0.4, SRV_H*0.6 + 0.1], center = true);
        }
    // floor web under the cradle
    hull() {
        translate([sx, spar_y, sz - SRV_H*0.3]) cube([SRV_L, SRV_W, 1], center = true);
        translate([sx - SRV_L/2, spar_y - SRV_W/2, 20]) cube([SRV_L, SRV_W, 1]);
    }
}

// =============================================================================
// ── Module: cableway_ends ───────────────────────────────────────────────────
// Two Ø7 guide tubes continuing the wing double-D conduits from the outboard
// wall inward into the cargo bay (EDF power/signal to the ESC/PDB bays).
module cableway_ends(cable_y, spar_z, inb) {
    for (dy = [-CABLE_SEP/2, CABLE_SEP/2])
        translate([OUTBOARD_WALL_X, cable_y + dy, spar_z])
            rotate([0, inb * 90, 0])
                difference() {
                    cylinder(d = CABLE_TUBE_OD, h = CABLE_TUBE_L);
                    translate([0, 0, -0.1]) cylinder(d = CABLE_BORE_D, h = CABLE_TUBE_L + 0.2);
                }
}

// =============================================================================
// ── Assembly ─────────────────────────────────────────────────────────────────
module side(d) { // d = [spar_Y, cable_Y, spar_Z, x_root, inboard_sign]
    root_bearing_seat(d[0], d[2], d[3], d[4]);
    servo_mount(d[0], d[2], d[3], d[4]);
    cableway_ends(d[1], d[2], d[4]);
}

side(PORT);
side(STBD);
