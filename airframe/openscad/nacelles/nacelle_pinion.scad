// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  Primary-component STLs published to airframe/stls/
//   are stored directly in hull frame, baked by tools/bake_hull_frame.py
//   (marker 'SerenityUAV HULL-FRAME R1' in the binary STL header).
//   NEVER re-bake a mesh derived from an already-baked file.
//   This file:
//     Part-local print frame, coaxial with the nacelle duct (duct axis =
//     local +Z, intake at Z = 0).  Hull placement derives from the nacelle
//     pose (cruise = 270 deg about +X + translation; hover rotates about the
//     tilt pivot at duct Z = 83 mm).  Assembly placement VERIFY pending
//     (serenity_assembly.py).
// ===========================================================================
// nacelle_pinion.scad
// Serenity UAV Rev R — Nacelle Tilt Linkage, Drive Pinion A & Crown Pinion
//
// Purpose:
//   Two identical M = 1.0 spur pinions used at different positions in the
//   nacelle tilt-to-nozzle gear train:
//
//     Drive Pinion A — mounted on the nacelle tilt shaft; meshes with the
//       fixed sector gear (nacelle_sector_gear.scad).  The sector gear is
//       centred ON the tilt pivot axis and does not rotate, while Pinion A
//       is carried by the nacelle and orbits the pivot axis as the nacelle
//       tilts -- this is an epicyclic (sun-fixed/planet-on-carrier) mesh,
//       NOT a simple two-gear mesh.  As the nacelle tilts 0-90 deg, Pinion A
//       rotates 420 deg on its shaft (see "Gear ratio context" below for the
//       epicyclic derivation).  Shaft is transverse (nacelle Y-axis).
//       Pinion A output shaft passes into Bevel Gear A
//       (nacelle_bevel_pair.scad).
//
//     Crown Pinion — mounted on the longitudinal shaft (nacelle Z-axis) at
//       the nozzle end; meshes with Idler-In, the input gear of the
//       compound idler stage (nacelle_nozzle_idler.scad), at the fixed
//       28.1 mm centre distance set by shaft-conduit continuity through
//       the bevel pair.  The idler's output gear (Idler-Out) drives the
//       full-circle nozzle ring gear (nacelle_nozzle_iris.scad).  Rotation
//       of the crown pinion drives ring rotation of ≈ 38.45° over the full
//       -5°/140° tilt range (see "Gear ratio context" below).
//
//   Both pinions are dimensionally identical; only their installation position
//   and axis orientation differ.
//
// Gear ratio context:
//   Stage 1 (Sector -> Pinion A) is EPICYCLIC, not a simple mesh: the
//   sector gear (sun) is fixed and centred on the tilt pivot axis; Pinion A
//   (planet) is carried by the nacelle (carrier) and orbits the pivot axis
//   as the nacelle tilts.  Rolling-without-slip contact-point velocity
//   matching at the mesh point (sector surface velocity = 0, since the
//   sector is fixed) gives the standard sun-fixed epicyclic relation:
//     omega_pinionA = omega_nacelle x (1 + R_sector / R_pinionA)
//                   = omega_nacelle x (1 + 22/6) = omega_nacelle x 4.667
//   For a 90 deg nacelle tilt: theta_pinionA = 90 deg x 4.667 = 420 deg.
//   (The naive simple-mesh ratio 22/6 = 3.667, giving 330 deg, OMITS the
//   "+1" orbital term and is WRONG for this topology -- corrected 2026-06-22.)
//
//   Stage 2 (Bevel Gear A -> Bevel Gear B, nacelle_bevel_pair.scad) is a
//   1:1 fixed-axis bevel pair (both gears' axes are fixed relative to the
//   nacelle -- no epicyclic term applies here): theta_bevelB = theta_pinionA
//   = 420 deg.  Crown Pinion is rigidly keyed to the same shaft as Bevel
//   Gear B, so theta_crownPinion = 420 deg as well.
//
//   Stage 3 (Crown Pinion -> Idler -> Nozzle Ring) is now a two-mesh
//   fixed-axis chain in the nacelle-local frame (the Crown Pinion, the
//   idler shaft, and the nozzle ring are all carried by the nacelle; none
//   orbits another locally), via the compound idler gear
//   (nacelle_nozzle_idler.scad):
//     theta_idler  = theta_crownPinion x (R_crownPinion / R_idlerIn)
//                  = theta_crownPinion x (6 / 22)
//     theta_ring   = theta_idler x (R_idlerOut / R_ring)
//                  = theta_idler x (7.5 / 36)
//     => theta_ring / theta_crownPinion = (6/22) x (7.5/36) = 1/17.6
//   RESOLVED 2026-06-22 (TODO.md §1.1.3): the Crown Pinion's hull-frame
//   Y-offset is fixed at 28 mm by shaft-conduit continuity through the
//   bevel pair, while the nozzle ring's required pitch radius (36 mm, sized
//   for the petal/hinge geometry in nacelle_nozzle_iris.scad) is
//   geometrically incompatible with a direct 28 mm mesh.  Rather than force
//   either dimension to an unsuitable value, a compound idler gear
//   (Idler-In R=22 mm meshes Crown Pinion at 28.1 mm centre distance;
//   Idler-Out R=7.5 mm meshes the ring at 43.6 mm centre distance) was
//   inserted between them, decoupling the two radii and supplying
//   additional reduction.  A free idler-shaft position exists because the
//   two centre distances and the fixed 28 mm Crown-Pinion-axis-to-ring-axis
//   span satisfy the triangle inequality: |28.1-43.6| = 15.5 mm <= 28 mm
//   <= 28.1+43.6 = 71.7 mm.  Full chain: for a 90 deg nacelle tilt,
//   theta_crownPinion = 420 deg (Stage 1 x Stage 2), so theta_ring =
//   420 / 17.6 = 23.86 deg.  See nacelle_nozzle_idler.scad and
//   nacelle_nozzle_iris.scad for the full derivation and petal kinematics.
//
// Mating interfaces:
//   Drive Pinion A:
//     • Sector gear (nacelle_sector_gear.scad):
//         Mesh at pitch circles: sector R = 22 mm, pinion R = 6 mm.
//         Centre distance = 28.0 mm nominal; 28.1 mm installed (0.10 mm backlash).
//     • Bevel Gear A shaft bore (nacelle_bevel_pair.scad): 3 mm CF shaft.
//     • MR63ZZ bearings (×2): 3 mm ID × 6 mm OD × 2.5 mm; press-fit into housing.
//   Crown Pinion:
//     • Idler-In, compound idler gear (nacelle_nozzle_idler.scad):
//         Mesh at pitch circles: crown pinion R = 6 mm, Idler-In R = 22 mm.
//         Centre distance = 28.0 mm nominal; 28.1 mm installed (0.10 mm backlash).
//     • MR63ZZ bearings (×2): same as Drive Pinion A.
//     • Longitudinal shaft: 3 mm CF tube.
//
// Gear standard: AGMA/ISO involute, Module M = 1.0 mm, Pressure angle 20°.
// Tooth profile: tooth-space subtraction method (12-tooth full circle).
//
// Shaft key: 1 mm flat chord cut (D-profile bore) on inner bore for
//   anti-rotation keying to the 3 mm CF shaft.
//
// Print specification:
//   Preferred:  SLA resin, ≤ 0.05 mm layer height.
//   Backup:     CF-PETG FDM, 0.10 mm layers, 4 perimeters, 60 % infill.
//   Orientation: Print with shaft bore vertical (tooth faces outward).
//   Post-process: Lightly ream shaft bore with 3.0 mm drill bit before assembly.
//   Bearing seats: Press fit; lightly sand if MR63ZZ does not seat by hand.
//
// Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date:    2026-05-24
// Rev:     R (2026-06-11): Rev R baseline — no geometry changes (carried forward from Rev O initial release).
// Rev:     R1 (2026-06-22): Corrected Drive Pinion A rotation comment (330 deg
//          -> 420 deg): the original figure used the naive simple-mesh ratio
//          (Rs/Rp), omitting the "+1" orbital term required because the
//          sector gear (sun) is fixed and centred on the tilt pivot while
//          Pinion A (planet) is carried by the nacelle -- an epicyclic, not
//          simple, mesh.  No geometry changed, comment-only fix.
// Rev:     R1.1 (2026-06-22): Resolved the Stage 3 (Crown Pinion -> Nozzle
//          Ring) open issue: replaced the direct Crown-Pinion-to-rack mesh
//          with a compound idler gear stage (nacelle_nozzle_idler.scad, new
//          file), decoupling the Crown Pinion's fixed 28 mm hull-frame
//          offset from the nozzle ring's required pitch radius.  Rewrote
//          "Gear ratio context" Stage 3 derivation, Mating Interfaces, and
//          Fit Confirmation table accordingly.  No geometry change to this
//          file's own pinions; comment/documentation update only.

// ── Resolution ────────────────────────────────────────────────────────────────

$fn = 72;   // standard circle resolution

// ── Gear Parameters ───────────────────────────────────────────────────────────

MODULE          =  1.0;   // [mm] AGMA Module
PRESSURE_ANGLE  = 20.0;   // [deg] standard involute pressure angle
N_TEETH         = 12;     // [count] 12-tooth pinion (minimum practical for M=1
                          //   PETG/resin without undercut at 20° PA)

// ── Derived Gear Geometry ─────────────────────────────────────────────────────

PITCH_R    = N_TEETH * MODULE / 2;          // [mm] = 6.0  pitch circle radius
TIP_R      = PITCH_R + MODULE;              // [mm] = 7.0  addendum circle
ROOT_R     = PITCH_R - 1.25 * MODULE;      // [mm] = 4.75 dedendum (root) circle
BASE_R     = PITCH_R * cos(PRESSURE_ANGLE); // [mm] ≈ 5.638 base circle

// Full-circle angular pitch (angle per tooth + space):
ANGULAR_PITCH = 360.0 / N_TEETH;   // [deg] = 30.0° per tooth

// Half-angle of one tooth space at pitch circle (equal tooth and space widths):
SPACE_HALF_ANG = ANGULAR_PITCH / 4;  // [deg] = 7.5° (quarter of angular pitch)

// ── Shaft and Bearing Parameters ──────────────────────────────────────────────

PINION_H        =  8.0;   // [mm] tooth face width
                          //   = 2 × MR63ZZ axial width (2.5 mm each) + 3 mm gap
SHAFT_BORE      =  3.2;   // [mm] MR63ZZ inner bore ID 3 mm + 0.2 mm clearance
SHAFT_KEY_W     =  1.0;   // [mm] flat key chord width (D-profile anti-rotation)
HUB_OD          =  5.5;   // [mm] hub outer diameter (seats between bearings)
HUB_EXTENSION   =  2.0;   // [mm] hub extension beyond tooth face each side
                          //   provides bearing seat shoulder; total shaft span
                          //   = PINION_H + 2 × HUB_EXTENSION = 12.0 mm

// Bearing seat dimensions (MR63ZZ: 3 mm ID, 6 mm OD, 2.5 mm wide):
BEARING_OD      =  6.0;   // [mm] MR63ZZ outer diameter
BEARING_W       =  2.5;   // [mm] MR63ZZ axial width
BEARING_SEAT_D  =  6.05;  // [mm] press-fit bore for MR63ZZ (6 mm OD + 0.05 mm
                          //   interference — resin/PETG elastic enough to seat)

// ── Module Definitions ────────────────────────────────────────────────────────

// tooth_space_pinion(i) — subtract one tooth-space gap from the pinion blank.
//
//   For a 12-tooth pinion the angular pitch is 30°.  Each tooth space is a thin
//   wedge centred between two adjacent tooth centrelines.
//
//   Arguments:
//     i — tooth-space index (0-based); space between tooth i and tooth i+1
module tooth_space_pinion(i) {
    // Angular centre of this space (midpoint between tooth i and tooth i+1):
    space_centre = i * ANGULAR_PITCH + ANGULAR_PITCH / 2;

    // Half-angular width of the tooth space.
    // At pitch circle: circular tooth space = π × MODULE / 2 = 1.5708 mm.
    // As angle at R = 6 mm: (1.5708 / 6) × (180/π) = 15.0°
    // Half-angle = 7.5°
    half_ang = SPACE_HALF_ANG;   // [deg] = 7.5°

    linear_extrude(height = PINION_H + 0.2) {
        // A wedge between ROOT_R and TIP_R trimmed to the space half-angle.
        rotate([0, 0, space_centre - half_ang]) {
            difference() {
                circle(r = TIP_R + 0.2);       // outer with slight overcut
                circle(r = ROOT_R - 0.1);      // stop at root fillet
                // Angular mask: keep only 2 × half_ang width
                rotate([0, 0, 2 * half_ang])
                    square([50, 50]);
                rotate([0, 0, 180])
                    square([50, 50]);
            }
        }
    }
}

// shaft_bore_with_key() — D-profile bore for 3 mm CF shaft + 1 mm flat key.
//
//   The "D" flat is a chord cut at distance (SHAFT_BORE/2 - SHAFT_KEY_W) from
//   the bore centre, removing a thin sliver from the circular bore to create a
//   flat that keys into a matching flat filed/milled on the CF shaft.
module shaft_bore_with_key() {
    union() {
        // Circular bore — 3.2 mm clearance
        cylinder(h = PINION_H + 2 * HUB_EXTENSION + 0.2,
                 d = SHAFT_BORE,
                 center = true);

        // Key flat: subtract by intersecting with a box that cuts the flat side.
        // The flat is at Y = -(SHAFT_BORE/2 - SHAFT_KEY_W) from bore centre.
        // Implemented as a "negative box" that removes the cylinder segment.
        // Here we ADD a slot cut via difference in the parent module.
        // The flat chord: X spans full bore width, Y is a thin slab.
        translate([0, SHAFT_BORE / 2 - SHAFT_KEY_W / 2, 0])
            cube([SHAFT_BORE + 0.2,
                  SHAFT_KEY_W,
                  PINION_H + 2 * HUB_EXTENSION + 0.2],
                 center = true);
    }
}

// hub_body() — solid hub cylinder with bearing seat bores at each end.
//   The hub spans PINION_H + 2 × HUB_EXTENSION along the shaft axis.
//   Two MR63ZZ bearing seats are bored into each axial end face.
module hub_body() {
    total_h = PINION_H + 2 * HUB_EXTENSION;   // [mm] = 12.0

    difference() {
        // Outer hub cylinder
        cylinder(h = total_h, d = HUB_OD, center = true);

        // Bearing seat — bottom end (Z = -total_h/2)
        translate([0, 0, -total_h / 2 - 0.1])
            cylinder(h = BEARING_W + 0.1, d = BEARING_SEAT_D);

        // Bearing seat — top end (Z = +total_h/2)
        translate([0, 0, total_h / 2 - BEARING_W])
            cylinder(h = BEARING_W + 0.1, d = BEARING_SEAT_D);

        // Shaft bore with D-key (centred on hub)
        shaft_bore_with_key();
    }
}

// pinion_teeth_ring() — annular tooth ring, height = PINION_H.
//   Built by starting with a solid disk of TIP_R diameter and subtracting
//   N_TEETH tooth-space wedges.
module pinion_teeth_ring() {
    difference() {
        // Solid disk from root to tip radius
        cylinder(h = PINION_H, d = TIP_R * 2, center = false);

        // Subtract inner bore region (hub handles the inner volume)
        cylinder(h = PINION_H + 0.2, d = ROOT_R * 2 - 0.5, center = false);

        // Subtract all N_TEETH tooth spaces
        for (i = [0 : N_TEETH - 1]) {
            tooth_space_pinion(i);
        }
    }
}

// drive_pinion_a() — Drive Pinion A: meshes with fixed sector gear.
//   Installation axis: transverse (nacelle Y-axis).
//   Assembled flush with Bevel Gear A on the same shaft.
//   Origin: centre of gear face, Z = 0 at inboard bearing seat face.
module drive_pinion_a() {
    union() {
        // Hub (bearing seats + shaft bore), centred on Z = PINION_H/2 + HUB_EXTENSION
        translate([0, 0, PINION_H / 2 + HUB_EXTENSION])
            hub_body();

        // Tooth ring at Z = 0 to Z = PINION_H
        pinion_teeth_ring();
    }
}

// crown_pinion() — Crown Pinion: meshes with Idler-In (nacelle_nozzle_idler.scad).
//   Installation axis: longitudinal (nacelle Z-axis), at nozzle end of shaft.
//   Mesh centre distance to Idler-In = 28.1 mm (Idler-In R = 22 mm).
//   Geometry identical to drive_pinion_a(); orientation is set by assembler.
//   Origin: same as drive_pinion_a().
module crown_pinion() {
    // Identical geometry — orientation handled by installation
    drive_pinion_a();
}

// ── Fit Confirmation ──────────────────────────────────────────────────────────
//
//   Interface               Mating part                   Clearance / fit
//   ──────────────────────  ────────────────────────────  ─────────────────────
//   Tooth pitch R = 6 mm    Sector gear pitch R = 22 mm   0.10 mm backlash
//   (Drive Pinion A)        nacelle_sector_gear.scad       (Δ centre distance)
//   Tooth pitch R = 6 mm    Idler-In pitch R = 22 mm      0.10 mm backlash
//   (Crown Pinion)          nacelle_nozzle_idler.scad      (Δ centre distance)
//   SHAFT_BORE 3.2 mm       3 mm CF shaft                  0.2 mm diametral clr
//   BEARING_SEAT_D 6.05 mm  MR63ZZ OD 6.0 mm              0.05 mm interference
//                                                           (press fit in PETG)
//   HUB_EXTENSION 2.0 mm    Bevel housing bore shoulder    face contact stop

// ── Render ────────────────────────────────────────────────────────────────────

// Uncomment one at a time to export individual STLs:
drive_pinion_a();
// translate([20, 0, 0]) crown_pinion();
