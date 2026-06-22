// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  Primary-component STLs published to airframe/stls/
//   are stored directly in hull frame, baked by tools/bake_hull_frame.py
//   (marker 'SerenityUAV HULL-FRAME R1' in the binary STL header).
//   NEVER re-bake a mesh derived from an already-baked file.
//   This file:
//     Part-local print frame, coaxial with its own shaft (shaft axis =
//     local Z).  Hull placement: the idler shaft position is fixed by two
//     simultaneous mesh constraints (Crown Pinion centre distance and Nozzle
//     Ring centre distance) — see "Idler position" below.  Assembly
//     placement PENDING (serenity_assembly.py) — see TODO.md §1.1.3.3.
// ===========================================================================
// nacelle_nozzle_idler.scad
// Serenity UAV Rev R1 — Nacelle Tilt Linkage, Crown-Pinion-to-Ring Idler Gear
//
// Purpose:
//   Compound reduction idler inserted between the Crown Pinion
//   (nacelle_pinion.scad) and the nozzle ring gear (nacelle_nozzle_iris.scad)
//   to resolve two problems with a direct Crown-Pinion-to-ring mesh that were
//   identified during the Rev R1 (2026-06-22) gear-train review:
//
//     1. RADIUS DECOUPLING — the Crown Pinion's hull-frame offset from the
//        nozzle axis is fixed at 28 mm (shaft-conduit continuity through the
//        bevel pair, shared with Drive Pinion A's 28 mm offset from the tilt
//        pivot — see nacelle_pinion.scad).  A direct mesh forces the nozzle
//        ring's pitch radius to ≈ 22 mm (28 − 6 mm Crown Pinion pitch R),
//        which is too small to carry the petal hinge circle needed for the
//        Rev R1 bore-percentage spec (see point 2).  The idler's two gears
//        independently satisfy the Crown-Pinion centre distance (28.1 mm)
//        and the ring centre distance, decoupling the ring's pitch radius
//        from the Crown Pinion's fixed position.
//
//     2. RATIO MISMATCH — Stage 1 (sector/Pinion A) is epicyclic and
//        amplifies nacelle tilt angle ×4.667 (see nacelle_pinion.scad); a
//        single direct mesh at any buildable ring radius produces far more
//        ring rotation than the petal lever can usefully convert into the
//        Rev R1 bore-percentage spec (75 % closed at 0° tilt -> 105 % open
//        at 90° tilt) without an oversized lever arm.  The idler supplies
//        the additional reduction needed.
//
//   The idler is a single compound gear (two tooth rings of different pitch
//   radius, rigidly keyed to one shaft) supported by its own two-bearing
//   bracket, mounted to the nozzle outer housing (nacelle_nozzle_iris.scad).
//
// Gear ratio derivation (Rev R1, 2026-06-22):
//   Idler-In  meshes Crown Pinion (R = 6 mm):  N = 44 T, R = 22.0 mm.
//     Centre distance = 22.0 + 6.0 + 0.1 mm backlash = 28.1 mm
//     (matches the Crown Pinion's fixed 28 mm hull-frame offset from the
//     nozzle axis, within the standard 0.1 mm backlash allowance).
//   Idler-Out meshes Nozzle Ring gear (R = 36 mm, nacelle_nozzle_iris.scad):
//     N = 15 T, R = 7.5 mm.
//     Centre distance = 36.0 + 7.5 + 0.1 mm backlash = 43.6 mm from nozzle axis.
//   Idler position check (triangle inequality, both centre distances measured
//   from the idler shaft axis): |28.1 - 43.6| = 15.5 mm <= 28 mm <=
//   28.1 + 43.6 = 71.7 mm -> a valid idler shaft position exists (two
//   mirror-image solutions; final angular placement is a packaging choice
//   resolved in the housing model / serenity_assembly.py, not a ratio
//   constraint).
//
//   Compound ratio:
//     omega_idler / omega_crownPinion = R_crownPinion / R_idlerIn = 6 / 22 = 0.27273
//     omega_ring   / omega_idler      = R_idlerOut / R_ring       = 7.5 / 36 = 0.20833
//     omega_ring   / omega_crownPinion = 0.27273 x 0.20833 = 0.056818  (= 1/17.6)
//
//   Full chain (theta_crownPinion = theta_nacelleTilt x 4.667, see
//   nacelle_pinion.scad Stage 1+2):
//     theta_ring = theta_nacelleTilt x 4.667 x 0.056818 = theta_nacelleTilt x 0.26515
//
//   Reference points (nacelle tilt measured from 0° = cruise):
//     0°   tilt -> theta_ring =   0.00°
//     90°  tilt -> theta_ring =  23.86°   (bore-percentage spec reference)
//     -5°  tilt -> theta_ring =  -1.33°   (lower hard stop)
//     140° tilt -> theta_ring =  38.45°   (upper hard stop)
//   See nacelle_nozzle_iris.scad for the petal-lever conversion of
//   theta_ring into petal swing angle and nozzle exit radius.
//
// Mating interfaces:
//   • Idler-In (R = 22 mm): meshes Crown Pinion (nacelle_pinion.scad),
//       0.1 mm backlash, centre distance 28.1 mm.
//   • Idler-Out (R = 7.5 mm): meshes Nozzle Ring gear (nacelle_nozzle_iris.scad),
//       0.1 mm backlash, centre distance 43.6 mm.
//   • Idler bracket: 2 x M2.5 mount bosses into nozzle outer housing wall.
//   • MR63ZZ bearings (x2): 3 mm ID x 6 mm OD x 2.5 mm, one at each shaft end.
//   • Shaft: 3 mm CF rod, D-key flat, shared shaft for both gear sections
//       (rigid compound gear — Idler-In and Idler-Out always co-rotate).
//
// Gear standard: AGMA/ISO involute, Module M = 1.0 mm, Pressure angle 20°.
// Tooth profile method: tooth-space subtraction via polygon() wedges
//   (arc_pts()/annular_wedge() helpers) — avoids the nested 2D CSG
//   (circle-circle-square-square) that causes CGAL exponential blowup at
//   tooth counts above ~20 (see nacelle_sector_gear.scad header).
//
// Print specification:
//   Preferred:  SLA resin, <= 0.05 mm layer height (captures M=1 tooth detail
//               on both the 44 T and 15 T sections).
//   Backup:     CF-PETG FDM, 0.10 mm layers, 4 perimeters, 40 % gyroid infill.
//   Nozzle:     Hardened steel (CF-PETG abrasive).
//   Orientation: Print with shaft vertical, larger (Idler-In) gear down.
//   Post-process: Ream 3 mm shaft bore; lightly sand bearing seats if MR63ZZ
//               does not seat by hand.
//
// Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date:    2026-06-22
// Rev:     R1 (2026-06-22): New file — idler gear added to resolve TODO.md
//          §1.1.3.3 "Resolve the unresolved Crown-Pinion-to-rack mesh radius"
//          by decoupling the nozzle ring's pitch radius from the Crown
//          Pinion's fixed 28 mm offset and supplying the additional
//          reduction the Rev R1 bore-percentage spec requires.

// ── Resolution ────────────────────────────────────────────────────────────────

$fn = 72;   // standard circle resolution

// ── Gear Parameters ───────────────────────────────────────────────────────────

MODULE          =  1.0;    // [mm] AGMA Module — matches Crown Pinion and ring
PRESSURE_ANGLE  = 20.0;    // [deg] standard involute pressure angle

N_TEETH_IN   = 44;         // [count] Idler-In — meshes Crown Pinion
PITCH_R_IN   = N_TEETH_IN * MODULE / 2;          // [mm] = 22.0
TIP_R_IN     = PITCH_R_IN + MODULE;              // [mm] = 23.0
ROOT_R_IN    = PITCH_R_IN - 1.25 * MODULE;       // [mm] = 20.75

N_TEETH_OUT  = 15;         // [count] Idler-Out — meshes Nozzle Ring gear
PITCH_R_OUT  = N_TEETH_OUT * MODULE / 2;         // [mm] = 7.5
TIP_R_OUT    = PITCH_R_OUT + MODULE;             // [mm] = 8.5
ROOT_R_OUT   = PITCH_R_OUT - 1.25 * MODULE;      // [mm] = 6.25

ANGULAR_PITCH_IN  = 360.0 / N_TEETH_IN;          // [deg] = 8.182°
ANGULAR_PITCH_OUT = 360.0 / N_TEETH_OUT;         // [deg] = 24.0°

// ── Axial Layout ──────────────────────────────────────────────────────────────

GEAR_H_IN    =  8.0;    // [mm] Idler-In tooth face width (matches Crown Pinion
                         //   PINION_H = 8 mm, nacelle_pinion.scad)
GEAR_GAP     =  2.0;    // [mm] axial clearance web between the two gear sections
GEAR_H_OUT   =  8.0;    // [mm] Idler-Out tooth face width (matches Nozzle Ring
                         //   RING_H = 8 mm, nacelle_nozzle_iris.scad)
HUB_EXTENSION =  2.0;   // [mm] hub extension beyond each outer gear face,
                         //   provides the bearing seat shoulder
TOTAL_H = HUB_EXTENSION + GEAR_H_IN + GEAR_GAP + GEAR_H_OUT + HUB_EXTENSION;
                         // [mm] = 22.0  total shaft span

// ── Shaft and Bearing Parameters ──────────────────────────────────────────────

SHAFT_BORE     =  3.2;   // [mm] MR63ZZ inner bore ID 3 mm + 0.2 mm clearance
SHAFT_KEY_W    =  1.0;   // [mm] flat key chord width (D-profile anti-rotation)
BEARING_OD     =  6.0;   // [mm] MR63ZZ outer diameter
BEARING_W      =  2.5;   // [mm] MR63ZZ axial width
BEARING_SEAT_D =  6.05;  // [mm] press-fit bore for MR63ZZ (6 mm OD + 0.05 mm
                         //   interference — resin/PETG elastic enough to seat)

// ── Idler Bracket Parameters ──────────────────────────────────────────────────

BRACKET_BOSS_OD     =  9.0;   // [mm] bearing-boss OD at each shaft end
BRACKET_MOUNT_HOLE_D =  2.7;  // [mm] M2.5 clearance (mounts into nozzle housing)
BRACKET_ARM_W        =  6.0;  // [mm] web width connecting the two bosses
BRACKET_ARM_T        =  3.0;  // [mm] web thickness

// ── Polygon Helpers ───────────────────────────────────────────────────────────
//
// arc_pts(r, a1, a2, n) / annular_wedge(...) — see nacelle_sector_gear.scad for
// the rationale (polygon-based tooth spaces avoid CGAL exponential blowup on
// nested 2D booleans at tooth counts above ~20; both gear sections here use
// this method since Idler-In has 44 teeth).
//
function arc_pts(r, a1, a2, n) =
    [for (i = [0 : n]) let(a = a1 + i * (a2 - a1) / n) [r * cos(a), r * sin(a)]];

function annular_wedge(r_in, r_out, a1, a2, n) =
    concat(arc_pts(r_in,  a1, a2, n),
           arc_pts(r_out, a2, a1, n));

// ── Module Definitions ────────────────────────────────────────────────────────

// tooth_space(i, pitch_r, tip_r, root_r, ang_pitch, h) — one full-depth
//   tooth-space wedge, full circle gear (general helper used by both sections).
module tooth_space(i, tip_r, root_r, ang_pitch, h) {
    space_centre = i * ang_pitch + ang_pitch / 2;   // [deg]
    half_ang     = ang_pitch / 4;                    // [deg] (equal tooth/space)
    linear_extrude(height = h + 0.2) {
        polygon(annular_wedge(
            root_r - 0.1, tip_r + 0.1,
            space_centre - half_ang, space_centre + half_ang,
            2
        ));
    }
}

// idler_in_ring() — 44-tooth gear section, meshes Crown Pinion.
module idler_in_ring() {
    difference() {
        cylinder(h = GEAR_H_IN, r = TIP_R_IN);
        translate([0, 0, -0.1])
            cylinder(h = GEAR_H_IN + 0.2, r = ROOT_R_IN - 1.0);
        for (i = [0 : N_TEETH_IN - 1]) {
            tooth_space(i, TIP_R_IN, ROOT_R_IN, ANGULAR_PITCH_IN, GEAR_H_IN);
        }
    }
}

// idler_out_ring() — 15-tooth gear section, meshes Nozzle Ring gear.
module idler_out_ring() {
    difference() {
        cylinder(h = GEAR_H_OUT, r = TIP_R_OUT);
        translate([0, 0, -0.1])
            cylinder(h = GEAR_H_OUT + 0.2, r = ROOT_R_OUT - 1.0);
        for (i = [0 : N_TEETH_OUT - 1]) {
            tooth_space(i, TIP_R_OUT, ROOT_R_OUT, ANGULAR_PITCH_OUT, GEAR_H_OUT);
        }
    }
}

// shaft_bore_with_key() — D-profile bore for 3 mm CF shaft + 1 mm flat key,
//   spanning the full idler length.
module shaft_bore_with_key() {
    union() {
        cylinder(h = TOTAL_H + 0.2, d = SHAFT_BORE, center = false);
        translate([0, SHAFT_BORE / 2 - SHAFT_KEY_W / 2, TOTAL_H / 2])
            cube([SHAFT_BORE + 0.2, SHAFT_KEY_W, TOTAL_H + 0.2], center = true);
    }
}

// idler_gear() — top-level module: complete compound idler gear.
//
//   Axial stack (Z = 0 at bottom bearing seat face):
//     0                       -> HUB_EXTENSION            : bottom hub
//     HUB_EXTENSION           -> + GEAR_H_IN              : Idler-In teeth
//     ...                     -> + GEAR_GAP               : spacer web
//     ...                     -> + GEAR_H_OUT             : Idler-Out teeth
//     ...                     -> + HUB_EXTENSION          : top hub
//
//   Origin: centre of bottom bearing seat face, shaft axis = local Z.
module idler_gear() {
    z_in  = HUB_EXTENSION;
    z_gap = z_in + GEAR_H_IN;
    z_out = z_gap + GEAR_GAP;
    z_top = z_out + GEAR_H_OUT;

    difference() {
        union() {
            // Bottom hub (bearing seat boss)
            cylinder(h = HUB_EXTENSION, d = BRACKET_BOSS_OD);

            // Idler-In gear section
            translate([0, 0, z_in])
                idler_in_ring();

            // Spacer web between gear sections (plain shaft, hub diameter)
            translate([0, 0, z_gap])
                cylinder(h = GEAR_GAP, d = BRACKET_BOSS_OD);

            // Idler-Out gear section
            translate([0, 0, z_out])
                idler_out_ring();

            // Top hub (bearing seat boss)
            translate([0, 0, z_top])
                cylinder(h = HUB_EXTENSION, d = BRACKET_BOSS_OD);
        }

        // Bottom bearing seat recess
        translate([0, 0, -0.1])
            cylinder(h = BEARING_W + 0.1, d = BEARING_SEAT_D);

        // Top bearing seat recess
        translate([0, 0, TOTAL_H - BEARING_W])
            cylinder(h = BEARING_W + 0.1, d = BEARING_SEAT_D);

        // Shaft bore with D-key, full length
        shaft_bore_with_key();
    }
}

// idler_bracket() — two-boss bracket supporting the idler shaft bearings.
//   Mounted to the nozzle outer housing wall (nacelle_nozzle_iris.scad) via
//   M2.5 bosses; final angular position about the nozzle axis is a packaging
//   choice (two valid mirror-image solutions per the centre-distance triangle
//   inequality in the file header) resolved in serenity_assembly.py.
//
//   Origin: same shaft axis convention as idler_gear() (Z = 0 at bottom
//   bearing seat face); bracket is a standoff frame around the shaft, not a
//   full housing — the nozzle outer housing wall provides the enclosing shell.
module idler_bracket() {
    union() {
        // Bottom boss (bearing land) + mount foot
        cylinder(h = HUB_EXTENSION + 1.0, d = BRACKET_BOSS_OD + 2.0);

        // Top boss (bearing land) + mount foot
        translate([0, 0, TOTAL_H - HUB_EXTENSION - 1.0])
            cylinder(h = HUB_EXTENSION + 1.0, d = BRACKET_BOSS_OD + 2.0);

        // Connecting web (carries bearing reaction load between the two bosses)
        translate([-BRACKET_ARM_W / 2, -BRACKET_ARM_T / 2, 0])
            cube([BRACKET_ARM_W, BRACKET_ARM_T, TOTAL_H]);
    }
}

// ── Fit Confirmation ──────────────────────────────────────────────────────────
//
//   Interface              Mating part                    Clearance / fit
//   ──────────────────────  ─────────────────────────────  ─────────────────────
//   Idler-In R = 22.0 mm    Crown Pinion R = 6 mm          0.1 mm backlash
//                           (nacelle_pinion.scad)           (centre dist 28.1 mm)
//   Idler-Out R = 7.5 mm    Nozzle Ring gear R = 36 mm     0.1 mm backlash
//                           (nacelle_nozzle_iris.scad)      (centre dist 43.6 mm)
//   SHAFT_BORE 3.2 mm       3 mm CF shaft                  0.2 mm diametral clr
//   BEARING_SEAT_D 6.05 mm  MR63ZZ OD 6.0 mm               0.05 mm interference
//   Bracket bosses          Nozzle outer housing wall      M2.5 bonded/bolted

// ── Render ────────────────────────────────────────────────────────────────────

idler_gear();
// idler_bracket();
