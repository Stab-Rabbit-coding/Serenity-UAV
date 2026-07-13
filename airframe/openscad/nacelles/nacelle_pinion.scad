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
//   Two spur pinions (one SCAD, two PINION_VARIANT builds — no longer
//   dimensionally identical as of Rev S1) used at different positions in the
//   nacelle tilt-to-nozzle gear train:
//
//     Drive Pinion A (M1.0, 17T, R8.5) — mounted on the nacelle tilt shaft;
//       meshes with the fixed sector gear (nacelle_sector_gear.scad).  The
//       sector gear is centred ON the tilt pivot axis and does not rotate,
//       while Pinion A is carried by the nacelle and orbits the pivot axis
//       as the nacelle tilts -- this is an epicyclic (sun-fixed/planet-on-
//       carrier) mesh, NOT a simple two-gear mesh.  As the nacelle tilts
//       0-90 deg, Pinion A rotates 322.94 deg on its shaft (see "Gear ratio
//       context" below).  Shaft is transverse; Pinion A's output shaft
//       passes into Bevel Gear A (nacelle_bevel_pair.scad).
//
//     Nozzle Drive Pinion (M0.5, 14T, R3.5; called "Crown Pinion" through
//       Rev R1) — mounted on the longitudinal shaft (nacelle Z-axis) at the
//       nozzle end; meshes the INTERNAL nozzle ring gear (136T M0.5, pitch
//       R = 34, nacelle_nozzle_iris.scad) directly, at the 30.5 mm centre
//       distance set by shaft-conduit continuity through the bevel pair.
//       Drives ring rotation of ≈ 38.3° over the full -5°/140° tilt range
//       (23.75° over 0-90°; see "Gear ratio context" below).  The Rev R1
//       compound idler stage is DELETED (docs/NOZZLE_DRIVE_TRADE.md).
//
// Gear ratio context:
//   Stage 1 (Sector -> Pinion A) is EPICYCLIC, not a simple mesh: the
//   sector gear (sun) is fixed and centred on the tilt pivot axis; Pinion A
//   (planet) is carried by the nacelle (carrier) and orbits the pivot axis
//   as the nacelle tilts.  Rolling-without-slip contact-point velocity
//   matching at the mesh point (sector surface velocity = 0, since the
//   sector is fixed) gives the standard sun-fixed epicyclic relation:
//     omega_pinionA = omega_nacelle x (1 + R_sector / R_pinionA)
//                   = omega_nacelle x (1 + 22/8.5) = omega_nacelle x 3.5882
//   For a 90 deg nacelle tilt: theta_pinionA = 90 x 3.5882 = 322.94 deg.
//   (The naive simple-mesh ratio OMITS the "+1" orbital term and is WRONG
//   for this topology -- corrected 2026-06-22.)
//
//   Stage 2 (Bevel Gear A -> Bevel Gear B, nacelle_bevel_pair.scad) is a
//   10T:14T fixed-axis reducing bevel pair (Rev S1; was 1:1 through R1):
//     theta_shaft = theta_pinionA x (10/14) = 230.67 deg per 90 deg tilt.
//   The Nozzle Drive Pinion is rigidly keyed to the same shaft as Bevel B.
//
//   Stage 3 (Nozzle Drive Pinion -> INTERNAL nozzle ring, Rev S1) is a
//   single direct internal mesh (both carried by the nacelle):
//     theta_ring = theta_shaft x (R_drive / R_ring)
//                = theta_shaft x (3.5 / 34)  =  23.75 deg per 90 deg tilt.
//   The internal-mesh centre distance R_ring - R_drive = 34 - 3.5 = 30.5 mm
//   EQUALS the sector-mesh centre distance R_sector + R_pinionA = 22 + 8.5,
//   so both pinions, the bevel pair, and the longitudinal shaft all sit on
//   the single Y = 30.5 mm station (straight shaft-conduit path preserved).
//   The Rev R1 compound idler chain (420 deg / 17.6 = 23.86 deg via
//   nacelle_nozzle_idler.scad) is superseded: its Idler-In wheel's teeth
//   reached R≈51 mm — ~10 mm PAST the nacelle OD.  Trade study and
//   decision: docs/NOZZLE_DRIVE_TRADE.md (user selected the internal-ring
//   gear option, 2026-07-07).
//
// Mating interfaces:
//   Drive Pinion A ("A"):
//     • Sector gear (nacelle_sector_gear.scad):
//         Mesh at pitch circles: sector R = 22 mm, pinion R = 8.5 mm.
//         Centre distance = 30.5 mm nominal; 30.6 mm installed (0.10 mm backlash).
//     • Bevel Gear A shaft bore (nacelle_bevel_pair.scad): 3 mm CF shaft.
//     • MR63ZZ bearings (×2): 3 mm ID × 6 mm OD × 2.5 mm; press-fit in-gear.
//   Nozzle Drive Pinion ("DRIVE"):
//     • INTERNAL nozzle ring gear (nacelle_nozzle_iris.scad):
//         Mesh at pitch circles: drive pinion R = 3.5 mm, ring R = 34 mm.
//         Internal-mesh centre distance = 30.5 mm nominal.
//     • No in-gear bearings (hub too small for MR63ZZ) — shaft rides the
//       pod's crown_pinion_boss bearings (nacelle_pod_50mm_tandem.scad).
//     • Longitudinal shaft: 3 mm CF tube.
//
// COTS note (Rev S1): both variants are deliberately at COMMODITY sizes —
//   M1.0 17T and M0.5 14T spur pinions with 3 mm bores are stock hobby /
//   gearmotor items in steel, brass, and POM.  A purchased metal pinion
//   (grub-screw hub) is PREFERRED over the printed part for wear; record
//   verified part numbers in the BOM before flight builds (TODO §1.1.3.3).
//
// Gear standard: AGMA/ISO involute, Pressure angle 20°; Module per variant.
// Tooth profile: tooth-space subtraction method (annular-wedge polygons).
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

// ── Variant Selection (Rev S1, 2026-07-07) ────────────────────────────────────
// The two pinions are no longer dimensionally identical (Rev S1 internal-ring
// nozzle drive — see docs/NOZZLE_DRIVE_TRADE.md):
//   "A"     — Drive Pinion A: M1.0, 17T, R = 8.5 mm.  Meshes the fixed sector
//             gear (R = 22) at centre distance 30.5 mm (= PINION_A_Y).
//   "DRIVE" — Nozzle Drive Pinion (replaces the "Crown Pinion"): M0.5, 14T,
//             R = 3.5 mm.  Meshes the INTERNAL nozzle ring gear (136T M0.5,
//             pitch R = 34, nacelle_nozzle_iris.scad) at centre distance
//             34 − 3.5 = 30.5 mm — the SAME shaft station as Pinion A,
//             preserving the straight pinion-A → bevel → longitudinal-shaft
//             conduit through the nacelle.
// Override at CLI:  openscad -D 'PINION_VARIANT="DRIVE"' ...
PINION_VARIANT  = "A";    // "A" | "DRIVE"

// ── Gear Parameters ───────────────────────────────────────────────────────────

MODULE          = (PINION_VARIANT == "DRIVE") ? 0.5 : 1.0;
                          // [mm] AGMA Module.  M0.5 on the DRIVE pinion is
                          //   forced by packaging: the nozzle annulus between
                          //   throat OD (R27.5) and housing bore (R37.5) is
                          //   only ~9 mm wide, so an M1 pinion (OD ≥ 14 mm)
                          //   cannot fit.  SLA print (already the preferred
                          //   process for these gears) is REQUIRED for M0.5.
PRESSURE_ANGLE  = 20.0;   // [deg] standard involute pressure angle
N_TEETH         = (PINION_VARIANT == "DRIVE") ? 14 : 17;
                          // [count] A: 17T (R8.5, no undercut at 20° PA);
                          //   DRIVE: 14T (R3.5 — mild undercut at 20° PA is
                          //   tolerated by the trapezoidal tooth-space
                          //   approximation used here; drive torque is small)

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

PINION_H        = (PINION_VARIANT == "DRIVE") ? 4.0 : 8.0;
                        // [mm] tooth face width.  A: 8.0 (= 2 × MR63ZZ axial
                        //   width + 3 mm gap).  DRIVE: 4.0 — matches the
                        //   internal ring's gear-band height (RING_GEAR_BAND_H
                        //   = 4.5 in nacelle_nozzle_iris.scad, 0.5 axial clr).
HAS_BEARING_SEATS = (PINION_VARIANT != "DRIVE");
                        // The DRIVE pinion's root circle (Ø 5.75) is smaller
                        //   than the MR63ZZ seat bore (Ø 6.05), so it cannot
                        //   host bearings — it is keyed directly to the 3 mm
                        //   shaft, whose bearings live in the pod's
                        //   crown_pinion_boss (nacelle_pod_50mm_tandem.scad).
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
// Rev S1 BUG FIX (2026-07-07): the original construction masked the annulus
// with two rotated first-quadrant squares — that removes only the arcs
// (2·half_ang..90°+2·half_ang) and (180°..270°), leaving ~155° of EXTRA arc
// in every "tooth space" cut.  Overlapping cuts consumed ALL teeth: every
// previously published pinion STL was a toothless blank at the root circle
// (verified: archived nacelle_pinion.stl max radius = ROOT_R − 0.1 exactly).
// Replaced with the closed annular-wedge polygon method already used (and
// proven) by nacelle_sector_gear.scad and the nozzle ring.

// arc_pts(r, a1, a2, n) — n+1 points along an arc at radius r from a1 to a2.
function arc_pts(r, a1, a2, n) =
    [for (i = [0 : n]) let(a = a1 + i * (a2 - a1) / n) [r * cos(a), r * sin(a)]];

// annular_wedge(r_in, r_out, a1, a2, n) — closed annular-sector polygon.
function annular_wedge(r_in, r_out, a1, a2, n) =
    concat(arc_pts(r_in,  a1, a2, n),
            arc_pts(r_out, a2, a1, n));

module tooth_space_pinion(i) {
    // Angular centre of this space (midpoint between tooth i and tooth i+1):
    space_centre = i * ANGULAR_PITCH + ANGULAR_PITCH / 2;

    // Half-angular width of the tooth space (quarter of the angular pitch —
    // equal tooth and space widths at the pitch circle):
    half_ang = SPACE_HALF_ANG;

    linear_extrude(height = PINION_H + 0.2) {
        polygon(annular_wedge(
            ROOT_R - 0.1, TIP_R + 0.2,
            space_centre - half_ang, space_centre + half_ang,
            2   // 2 segments per arc edge (spaces are only a few deg wide)
        ));
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

        // Bearing seats (variant "A" only — the DRIVE pinion's hub is too
        // small for MR63ZZ seats; see HAS_BEARING_SEATS above):
        if (HAS_BEARING_SEATS) {
            // Bearing seat — bottom end (Z = -total_h/2)
            translate([0, 0, -total_h / 2 - 0.1])
                cylinder(h = BEARING_W + 0.1, d = BEARING_SEAT_D);

            // Bearing seat — top end (Z = +total_h/2)
            translate([0, 0, total_h / 2 - BEARING_W])
                cylinder(h = BEARING_W + 0.1, d = BEARING_SEAT_D);
        }

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

// nozzle_drive_pinion() — Nozzle Drive Pinion (Rev S1; replaces "Crown
//   Pinion").  Renders correctly only with PINION_VARIANT = "DRIVE".
//   Installation axis: longitudinal (nacelle Z-axis), at nozzle end of shaft.
//   Meshes the INTERNAL nozzle ring gear (136T M0.5 pitch R=34,
//   nacelle_nozzle_iris.scad) at 30.5 mm centre distance, gear band seated
//   in the ring's gear band (iris local Z 0..4.5).
//   Origin: same as drive_pinion_a().
module nozzle_drive_pinion() {
    // Same construction; dimensions switch on PINION_VARIANT
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
//
// Export each variant via the CLI define (Rev S1):
//   Pinion A (M1 17T):
//     openscad -o airframe/stls/nacelles/nacelle_pinion_a.stl \
//              nacelle_pinion.scad -D 'PINION_VARIANT="A"'
//   Nozzle Drive Pinion (M0.5 14T):
//     openscad -o airframe/stls/nacelles/nacelle_drive_pinion.stl \
//              nacelle_pinion.scad -D 'PINION_VARIANT="DRIVE"'
drive_pinion_a();
