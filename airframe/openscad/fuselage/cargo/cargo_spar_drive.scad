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
// end of the rotating 8 mm tilt-spar drive plus the wing-root joint + cableway:
//   1. WING-ROOT RECEIVER + MORTISE — a reinforced socket that ties the tenon
//      mortise (aft, Y≈57) and the spar bearing boss (fwd, Y≈15) into one box.
//      The mortise pocket is sized to the wing root TENON (fuselage_root_tab
//      30 W × 20 H × 12 deep) + 0.3 mm slip + a positive-stop shoulder.
//   2. ROOT BEARING SEAT — F688ZZ (8×16×5) supporting the inboard spar end.
//   3. SERVO MOUNT — DS3218MG (≈40×20×40 mm) mounted FLAT against the outboard
//      side bulkhead (long faces in the Y–Z plane, only the 20 mm width into the
//      bay) so it does NOT intrude on the cargo volume.  Drives a horn on the
//      spar via a 2 mm pushrod + M2 clevis (repo hardware); linkage throw for the
//      −5°..140° range is tuned at assembly.
//   4. CABLEWAY ENDS — two Ø7 guide tubes continuing the wing double-D EDF
//      power/signal conduits from the wing root into the cargo bay.
//
// Wing-root joint load check (first principles, docs/TILT_SPAR_ANALYSIS.md):
//   - Nacelle cantilever → cargo root-bearing reaction ≈ 9.4 N (×2 dyn ≈ 19 N);
//     trivial for the 22 mm-OD CF-PETG bearing boss.
//   - Wing aero on the tenon: lift 3.8 N × ~43 mm + S1223 Cm ≈ 0.2–0.35 N·m;
//     negligible stress in the 30×20 tenon.
//   - Torsion reacted by the fwd spar-bearing (Y15) ↔ aft tenon (Y57) 42 mm
//     couple → ~5–8 N/point. All FOS large; the joint is fit/positive-stop-
//     limited, not strength-limited.  The receiver supplies both.
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
SRV_L = 40.0; SRV_W = 20.0; SRV_H = 40.0;   // [mm] body (L,H are the long faces)
SRV_LUG_L = 54.0;                            // [mm] tab-to-tab length
SRV_WALL = 2.5;                              // [mm] cradle wall

// ── Wing-root tenon / mortise (fuselage_root_tab: 30 W × 20 H × 12 deep) ──────
TENON_W    = 30.0;   // [mm] tenon width  (hull Y)
TENON_H    = 20.0;   // [mm] tenon height (hull Z)
TENON_D    = 12.0;   // [mm] tenon insertion depth (hull X)
MORTISE_FIT = 0.3;   // [mm] slip clearance per side
RECV_WALL  = 4.0;    // [mm] receiver wall around the mortise (2-wall min)
STOP_SHLDR = 3.0;    // [mm] positive-stop shoulder past the tenon tip

// ── Cableway (double-D, matches wings_s1223_revo.scad) ───────────────────────
CABLE_BORE_D = 7.0;      // [mm]
CABLE_SEP    = 8.0;      // [mm] chord (Y) centre-to-centre
CABLE_TUBE_OD = 10.0;    // [mm] guide-tube OD
CABLE_TUBE_L  = 28.0;    // [mm] guide-tube length inward from the wall

OUTBOARD_WALL_X = -72.7; // [mm] cargo outboard (wing-side) wall

// Per-side data: [spar_Y, cable_Y, spar_Z, x_root, inboard_sign, tenon_Y, tenon_Z]
PORT = [15, 55, 66, -81,  -1, 57.5, 58];
STBD = [10, 50, 66, -250, +1, 52.5, 58];

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
// DS3218 cradle mounted FLAT against the outboard side bulkhead: the long faces
// (L×H = 40×40) lie in the Y–Z plane against the wall; only the 20 mm width (W)
// projects into the cargo bay, so the servo does not intrude on the payload
// volume.  The servo sits just inboard of the wing-root structure, its output
// end toward the spar; the arm→pushrod→spar-horn linkage is assembly hardware.
module servo_mount(spar_y, spar_z, x_root, inb) {
    wall_in = OUTBOARD_WALL_X - inb * 2.5;   // inner face of the outboard bulkhead
    // cradle occupies X: 20 mm (W) into the bay from the wall; Y: 40 (L) along
    // the wall; Z: 40 (H) vertical, centred a little below the spar.
    cx = wall_in - inb * (SRV_W/2 + 1);      // 1 mm off the wall
    cy = spar_y - 6;                         // nudge fwd of the spar horn plane
    cz = spar_z - 6;                         // roughly centred on the spar height
    translate([cx, cy, cz])
        difference() {
            cube([SRV_W + 2*SRV_WALL, SRV_L + 2*SRV_WALL, SRV_H + 2*SRV_WALL],
                 center = true);
            // servo pocket (open toward the bay, −inb·X)
            translate([-inb * SRV_WALL, 0, 0])
                cube([SRV_W + 0.4, SRV_L + 0.4, SRV_H + 0.4], center = true);
        }
    // gusset tying the cradle back to the bulkhead + down toward the floor
    hull() {
        translate([cx, cy, cz]) cube([1, SRV_L, SRV_H], center = true);
        translate([wall_in - inb * 0.5, cy - SRV_L/2, 20]) cube([1, SRV_L, 1]);
    }
}

// =============================================================================
// ── Module: wing_root_receiver ──────────────────────────────────────────────
// Reinforced socket that ties the aft tenon mortise and the fwd spar-bearing
// boss into one box, so wing-root bending and torsion are reacted across the
// fore-aft (Y15↔Y57 ≈ 42 mm) couple.  The MORTISE is a tenon-shaped pocket
// (tenon + MORTISE_FIT slip) with a STOP_SHLDR positive stop at its inboard end;
// it is cut from the receiver block.  The block is unioned into the cargo shell
// at merge; the pocket opens toward the wing (outboard face).
module wing_root_receiver(spar_y, spar_z, x_root, inb, tenon_y, tenon_z) {
    // receiver spans fore-aft from the spar bearing (spar_y) to past the tenon.
    y_lo = min(spar_y, tenon_y) - BRG_BOSS_OD/2;
    y_hi = max(spar_y, tenon_y) + TENON_W/2 + RECV_WALL;
    blk_x0 = x_root + inb * (TENON_D + STOP_SHLDR + RECV_WALL); // inboard back wall
    // solid block from the wing-root face inboard, enclosing tenon + bearing Y-span
    difference() {
        translate([min(x_root, blk_x0), y_lo,
                   min(spar_z, tenon_z) - TENON_H/2 - RECV_WALL])
            cube([abs(blk_x0 - x_root),
                  y_hi - y_lo,
                  max(spar_z, tenon_z) + TENON_H/2 + RECV_WALL
                    - (min(spar_z, tenon_z) - TENON_H/2 - RECV_WALL)]);
        // mortise pocket (tenon + slip), opening outboard toward the wing
        translate([x_root - inb * 0.1, tenon_y, tenon_z])
            rotate([0, inb * 90, 0])
                translate([0, 0, -(TENON_D + 0.2)])
                    linear_extrude(TENON_D + 0.2, center = false)
                        square([TENON_H + 2*MORTISE_FIT, TENON_W + 2*MORTISE_FIT],
                               center = true);
        // spar clearance bore through the block (bearing boss adds the seat)
        translate([blk_x0, spar_y, spar_z]) rotate([0, inb * 90, 0])
            cylinder(d = SPAR_BORE_D + 1, h = abs(blk_x0 - x_root) + 2,
                     center = false, $fn = 24);
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
module side(d) { // [spar_Y, cable_Y, spar_Z, x_root, inb, tenon_Y, tenon_Z]
    wing_root_receiver(d[0], d[2], d[3], d[4], d[5], d[6]);
    root_bearing_seat(d[0], d[2], d[3], d[4]);
    servo_mount(d[0], d[2], d[3], d[4]);
    cableway_ends(d[1], d[2], d[4]);
}

side(PORT);
side(STBD);
