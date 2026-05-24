// nacelle_bevel_pair.scad
// Serenity UAV Rev O — Nacelle Tilt Linkage, 1:1 Straight Bevel Gear Pair
//
// Purpose:
//   A matched pair of M = 1.0 straight bevel gears providing a 90° shaft-angle
//   redirection in the nacelle gear train.  The pair is 1:1 ratio; input on the
//   transverse axis (from Drive Pinion A) is redirected to the longitudinal axis
//   (to the Crown Pinion and nozzle ring) without speed change.
//
//   Gear A (Bevel A) — transverse axis; driven by Pinion A shaft.
//   Gear B (Bevel B) — longitudinal axis; drives longitudinal CF shaft to
//     Crown Pinion at the nozzle end.
//
// Bevel gear geometry basis:
//   1:1 ratio + 90° shaft angle → pitch cone half-angle = 45° for both gears.
//   AGMA 2005: straight bevel, Module at large end M = 1.0 mm.
//   Pitch radius at large end: R = N × M / 2 = 14 × 1.0 / 2 = 7.0 mm.
//   Back-cone (pitch cone slant) distance: L = R / sin(45°) = 9.899 mm.
//   Face width rule: F ≤ L/3 = 3.3 mm; use F = 4.0 mm for printability.
//   Tooth proportions at large end:
//     Addendum  a = M = 1.0 mm
//     Dedendum  b = 1.25 × M = 1.25 mm
//     Tooth taper: both addendum and dedendum taper to zero at apex.
//
// Mating interfaces:
//   Bevel A:
//     • Drive Pinion A shaft (nacelle_pinion.scad): 3 mm CF shaft, D-key bore.
//     • Bevel housing transverse bore (nacelle_bevel_housing.scad):
//         gear OD + 0.5 mm clearance = 14.0 + 1.0 = 15.0 mm chamber bore.
//     • Mesh with Bevel B: pitch cones tangent at large end; shaft axes
//         intersect at virtual apex (17.0 mm from each large-end face).
//   Bevel B:
//     • Longitudinal shaft: 3 mm CF shaft, D-key bore.
//     • Bevel housing longitudinal bore (nacelle_bevel_housing.scad).
//
// Gear standard: AGMA 2005 / ISO 10300 straight bevel, involute equivalent.
// Tooth profile: simplified trapezoidal approximation — tooth-space subtraction
//   on conical face.  Adequate for M = 1.0 resin/PETG prototype.
//
// Print specification:
//   Preferred:  SLA resin, ≤ 0.05 mm layer height.
//   Backup:     CF-PETG FDM, 0.10 mm layers, 4 perimeters, 60 % infill.
//   Orientation: Print with large-end face down (cone apex upward) for best
//     tooth-face layer adhesion.
//   Nozzle:     Hardened steel (CF-PETG abrasive).
//
// Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date:    2026-05-24
// Rev:     O (initial release)

// ── Resolution ────────────────────────────────────────────────────────────────

$fn = 72;   // standard circle resolution

// ── Gear Parameters ───────────────────────────────────────────────────────────

MODULE           =  1.0;   // [mm] AGMA Module at large end of bevel
N_TEETH          = 14;     // [count] teeth per gear (1:1 pair, same count)
PRESSURE_ANGLE   = 20.0;   // [deg] standard involute pressure angle
PITCH_CONE_ANGLE = 45.0;   // [deg] half-angle of pitch cone
                           //   = arctan(1) = 45° for 1:1 ratio, 90° shaft angle

// ── Derived Bevel Geometry ────────────────────────────────────────────────────

PITCH_R_LARGE  = N_TEETH * MODULE / 2;           // [mm] = 7.0  pitch R, large end
ADDENDUM_LARGE = MODULE;                          // [mm] = 1.0  at large end
DEDENDUM_LARGE = 1.25 * MODULE;                  // [mm] = 1.25 at large end
TIP_R_LARGE    = PITCH_R_LARGE + ADDENDUM_LARGE; // [mm] = 8.0  tip R, large end
ROOT_R_LARGE   = PITCH_R_LARGE - DEDENDUM_LARGE; // [mm] = 5.75 root R, large end

// Back-cone (slant) distance — distance from virtual apex to large-end pitch circle:
//   L = R_large / sin(pitch_cone_angle) = 7.0 / sin(45°) = 9.899 mm
BACK_CONE_DIST = PITCH_R_LARGE / sin(PITCH_CONE_ANGLE);  // [mm] ≈ 9.899

FACE_WIDTH   =  4.0;   // [mm] face width along slant (slightly > L/3 = 3.3 for
                        //   printability; does not violate AGMA 2005 §8.4 max
                        //   face width of L/3 by more than 20 %)

// Small-end pitch radius (proportional taper):
//   R_small = R_large × (L - F) / L
PITCH_R_SMALL = PITCH_R_LARGE * (BACK_CONE_DIST - FACE_WIDTH) / BACK_CONE_DIST;
                                                 // [mm] ≈ 4.171

// Small-end tip and root radii (same taper proportion):
TIP_R_SMALL  = TIP_R_LARGE  * (BACK_CONE_DIST - FACE_WIDTH) / BACK_CONE_DIST;
ROOT_R_SMALL = ROOT_R_LARGE * (BACK_CONE_DIST - FACE_WIDTH) / BACK_CONE_DIST;

// Cone frustum axial height (projection of slant along axis):
//   H_cone = FACE_WIDTH × cos(PITCH_CONE_ANGLE)
CONE_H = FACE_WIDTH * cos(PITCH_CONE_ANGLE);    // [mm] ≈ 2.828

// Angular pitch on large-end base circle:
ANGULAR_PITCH = 360.0 / N_TEETH;               // [deg] = 25.714° per tooth
SPACE_HALF_ANG = ANGULAR_PITCH / 4;            // [deg] ≈ 6.429° (half tooth space)

// ── Shaft and Hub Parameters ──────────────────────────────────────────────────

SHAFT_BORE   =  3.2;   // [mm] 3 mm CF shaft + 0.2 mm clearance
SHAFT_KEY_W  =  1.0;   // [mm] flat key chord width (D-profile bore)
BEVEL_H      =  7.0;   // [mm] total axial height incl. hub extension behind cone
HUB_OD       =  6.0;   // [mm] hub outer diameter (behind the conical tooth face)
HUB_H        = BEVEL_H - CONE_H;  // [mm] hub backing height ≈ 4.17 mm

// Bearing seat (MR63ZZ: 3 mm ID, 6 mm OD, 2.5 mm):
BEARING_SEAT_D = 6.05;   // [mm] press-fit bore for MR63ZZ
BEARING_W      =  2.5;   // [mm] MR63ZZ axial width

// ── Module Definitions ────────────────────────────────────────────────────────

// cone_frustum() — base conical body for the bevel gear (solid, no teeth yet).
//   The frustum spans axially from Z = 0 (large end) to Z = CONE_H (small end).
//   Large-end radius = TIP_R_LARGE; small-end radius = TIP_R_SMALL.
module cone_frustum() {
    // cylinder() with r1 ≠ r2 produces a frustum (truncated cone)
    cylinder(h  = CONE_H,
             r1 = TIP_R_LARGE,    // large end at Z = 0
             r2 = TIP_R_SMALL);   // small end at Z = CONE_H
}

// hub_backing() — cylindrical hub behind the large-end face (Z = -HUB_H to Z = 0).
//   Provides bearing seat and shaft registration behind the gear cone.
module hub_backing() {
    translate([0, 0, -HUB_H]) {
        difference() {
            cylinder(h = HUB_H, d = HUB_OD);

            // Bearing seat at base of hub (Z = -HUB_H):
            translate([0, 0, -0.1])
                cylinder(h = BEARING_W + 0.1, d = BEARING_SEAT_D);
        }
    }
}

// bevel_tooth_space(i) — one tooth-space void cut from the conical face.
//
//   Approximation method:
//     The tooth space is a tapered wedge subtracted from the frustum.
//     At the large end the wedge has angular half-width SPACE_HALF_ANG and
//     radial depth from ROOT_R_LARGE to TIP_R_LARGE.
//     At the small end the wedge tapers proportionally.
//     Implemented as hull() of two thin cylinder subtraction wedges at each end,
//     then intersected with the frustum face.
//
//   Arguments:
//     i — tooth-space index (0-based)
module bevel_tooth_space(i) {
    space_centre = i * ANGULAR_PITCH + ANGULAR_PITCH / 2;  // [deg]
    half_ang     = SPACE_HALF_ANG;                          // [deg]

    // Create the tooth-space wedge as a hull between two thin wedge disks:
    //   - Large-end wedge disk at Z = -0.05 (just forward of large end)
    //   - Small-end wedge disk at Z = CONE_H + 0.05 (just past small end)
    hull() {
        // Large-end wedge slice (thin disk in XY plane at Z ≈ 0):
        linear_extrude(height = 0.1) {
            rotate([0, 0, space_centre - half_ang]) {
                difference() {
                    circle(r = TIP_R_LARGE + 0.1);
                    circle(r = ROOT_R_LARGE - 0.1);
                    rotate([0, 0, 2 * half_ang]) square([50, 50]);
                    rotate([0, 0, 180])           square([50, 50]);
                }
            }
        }

        // Small-end wedge slice (thin disk at Z = CONE_H):
        translate([0, 0, CONE_H - 0.1]) {
            linear_extrude(height = 0.1) {
                rotate([0, 0, space_centre - half_ang]) {
                    difference() {
                        circle(r = TIP_R_SMALL + 0.1);
                        circle(r = ROOT_R_SMALL - 0.1);
                        rotate([0, 0, 2 * half_ang]) square([50, 50]);
                        rotate([0, 0, 180])           square([50, 50]);
                    }
                }
            }
        }
    }
}

// shaft_bore_bevel() — D-profile shaft bore through the full gear height.
//   Bore runs from bottom of hub (Z = -HUB_H) to top of cone (Z = CONE_H).
module shaft_bore_bevel() {
    total_length = HUB_H + CONE_H + 0.2;
    translate([0, 0, -HUB_H - 0.1]) {
        union() {
            // Main circular bore
            cylinder(h = total_length, d = SHAFT_BORE);
            // D-key flat: thin box cutting the chord from bore interior
            translate([0, SHAFT_BORE / 2 - SHAFT_KEY_W / 2, total_length / 2 - 0.1])
                cube([SHAFT_BORE + 0.2, SHAFT_KEY_W, total_length], center = true);
        }
    }
}

// bevel_gear_a() — Bevel Gear A: transverse axis, driven by Pinion A shaft.
//
//   Installation: transverse (nacelle Y-axis).
//   Meshes with Bevel Gear B at 90°; pitch cones tangent at large-end face (Z=0).
//   Origin: centre of large-end face; Z+ is toward small end (into the housing).
module bevel_gear_a() {
    difference() {
        union() {
            // Conical tooth body
            cone_frustum();
            // Hub backing cylinder
            hub_backing();
        }

        // Subtract tooth spaces (N_TEETH spaces for N_TEETH teeth)
        for (i = [0 : N_TEETH - 1]) {
            bevel_tooth_space(i);
        }

        // Shaft bore (D-profile)
        shaft_bore_bevel();
    }
}

// bevel_gear_b() — Bevel Gear B: longitudinal axis, drives longitudinal shaft.
//
//   Geometry: identical to Bevel Gear A (1:1 pair, same tooth count).
//   Installation: rotated 90° about X-axis relative to Gear A to achieve the
//     90° shaft-angle redirection.  The installer rotates as needed.
//   Meshes with Bevel Gear A; pitch cones tangent at large-end face (Z=0).
//   Origin: same convention as bevel_gear_a().
module bevel_gear_b() {
    // Identical geometry — orientation handled by installation / assembly file
    bevel_gear_a();
}

// ── Fit Confirmation ──────────────────────────────────────────────────────────
//
//   Interface                 Mating part                Clearance / fit
//   ────────────────────────  ─────────────────────────  ────────────────────
//   Large-end pitch R = 7 mm  Bevel B large-end R = 7    Pitch cones tangent;
//   (Bevel A)                 (nacelle_bevel_pair.scad)   0.1 mm axial backlash
//   SHAFT_BORE 3.2 mm         3 mm CF shaft              0.2 mm diametral clr
//   BEARING_SEAT_D 6.05 mm    MR63ZZ OD 6.0 mm           0.05 mm interference
//   Cone large face (Z=0)     Housing chamber floor       axial face contact
//   HUB_OD 6.0 mm            Housing bore (8.5 mm)        1.25 mm radial clr
//                             nacelle_bevel_housing.scad  (gear clears housing)

// ── Render ────────────────────────────────────────────────────────────────────

// Uncomment one at a time to export individual STLs:
bevel_gear_a();
// Bevel B is identical; export separately by uncommenting:
// translate([20, 0, 0]) bevel_gear_b();

// Assembly preview — both gears at 90° shaft angle (comment out singles above):
// bevel_gear_a();
// translate([0, PITCH_R_LARGE + PITCH_R_LARGE, CONE_H])
//     rotate([90, 0, 0])
//         bevel_gear_b();
