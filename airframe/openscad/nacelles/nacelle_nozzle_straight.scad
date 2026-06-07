// =============================================================================
// nacelle_nozzle_straight.scad
// Serenity UAV — Rev T1 — Fixed Straight Nozzle with Decorative Petals
// =============================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-06-07
// Revision: Rev T1 (simplified variant — no gear train)
//
// Description
// -----------
// Simplified replacement for nacelle_nozzle_iris.scad (Rev O).  The variable-
// diameter iris and its passive gear-driven actuation are removed entirely.
// This file produces a fixed straight-bore nozzle housing (50 mm exit diameter,
// constant) plus eight decorative imitation petals that replicate the visual
// appearance of the iris nozzle without any mechanical function.
//
// Two separately-printable parts:
//     1. nozzle_fixed_housing()  — fixed outer housing; bonds to nacelle exit
//     2. nozzle_petal_fixed()    — one decorative petal (print × 8)
//
// Differences from nacelle_nozzle_iris.scad (Rev O):
//     REMOVED — nozzle_inner_ring()       rotating ring with M=1.0 rack
//     REMOVED — Crown Pinion access slot  radial wall slot for pinion mesh
//     REMOVED — piano-wire link ring      drive wire between ring and petals
//     REMOVED — link-ring slot on petals  1.2 mm wire slot through petal
//     REMOVED — drive posts on ring       link-ring attachment stubs
//     RETAINED — outer housing geometry   bonding lip, hinge bores, OD profile
//     RETAINED — petal geometry           curved trapezoidal slab, hinge knuckle
//
// Nozzle exit
// -----------
//     Exit diameter is fixed at 50 mm (EDF bore) regardless of nacelle tilt.
//     The exit area is constant; no thrust vectoring optimisation between
//     hover and cruise modes.
//
// Decorative petal function
// -------------------------
//     Petals are installed on 3 mm × 18 mm stainless steel hinge pins pressed
//     into the housing hinge bores.  Once positioned, pins are secured with a
//     drop of medium-strength threadlocker (Loctite 243 or equivalent) on the
//     pin ends.  Petals DO NOT ROTATE after final assembly.  They serve only
//     as aerodynamic fairings and cosmetic features matching the REVT iris look.
//
//     Recommended fixed position: closed / cruise (petals rotated so their tips
//     are roughly flush with the bore exit).  Adjust to taste before threadlocking.
//
// Mating interface
// ----------------
//     Bonds to nacelle exit face (nacelle_pod_50mm_tandem_simple.scad Rev T1).
//     Housing forward lip (OD = 70 mm, H = 3 mm) registers against the nacelle
//     exit face around the 50 mm bore opening.  Bond with structural epoxy
//     (JB Weld or equivalent, min shear 3 MPa cured).
//
//     The simplified nacelle pod does NOT have a nozzle ring pocket bore; the
//     housing lip sits on the exterior nacelle face.
//
// Print specification — Housing:
//     Material    : CF-PETG (structural bond surface; hinge bore load)
//     Layers      : 0.15 mm; 4 perimeters; 40% gyroid infill
//     Orientation : Bonding lip face down (lip face on build plate)
//     Quantity    : 1 per nacelle
//
// Print specification — Petal:
//     Material    : PETG (non-structural aerodynamic fairing; slight flex OK)
//     Layers      : 0.15 mm; 3 perimeters; 25% gyroid infill
//     Orientation : Flat, inner face down on build plate
//     Color note  : Inner face — translucent blue PETG (aesthetic reference)
//                   Outer face — match nacelle hull finish (titanium grey)
//     Quantity    : 8 per nacelle (one per hinge pin)
//
// References
// ----------
//     [1] nacelle_pod_50mm_tandem_simple.scad Rev T1 — mating nacelle bore
//         and exit face geometry.
//     [2] nacelle_nozzle_iris.scad Rev O — iris petal and housing geometry
//         used as the geometric basis for this file.  Actuation elements removed.
//     [3] Serenity-UAV project CLAUDE.md — fabrication standards (2026).
//
// =============================================================================


// =============================================================================
// ── Resolution ────────────────────────────────────────────────────────────────
// =============================================================================

$fn = 72;   // standard circle resolution


// =============================================================================
// ── Parameter Block ───────────────────────────────────────────────────────────
// =============================================================================

// ── Bore and housing dimensions ───────────────────────────────────────────────

EDF_BORE_R       = 25.0;   // [mm] EDF bore inner radius → 50 mm ID (fixed exit)
HOUSING_OUTER_R  = 35.0;   // [mm] housing outer radius → OD = 70 mm
HOUSING_H        = 10.0;   // [mm] housing body axial depth
HOUSING_LIP_H    =  3.0;   // [mm] forward bonding lip axial depth
HOUSING_LIP_R    = 26.0;   // [mm] bonding lip inner radius (1 mm clearance over bore)

// ── Petal hinge geometry ──────────────────────────────────────────────────────

N_PETALS         =  8;     // [count] decorative petal count (matches REVT iris)
PETAL_SPAN_DEG   = 50.0;   // [deg] angular span per petal (45° spacing + 5° overlap)
PETAL_HINGE_R    = 33.0;   // [mm] hinge pin circle radius (from nozzle axis)
HINGE_PIN_D      =  3.0;   // [mm] stainless steel hinge pin OD
HINGE_BORE_D     =  3.2;   // [mm] clearance bore for 3 mm hinge pin (0.2 mm clearance)

// ── Petal body dimensions ─────────────────────────────────────────────────────

PETAL_THICKNESS  =  2.5;   // [mm] petal slab thickness (uniform)
PETAL_LENGTH     = 18.0;   // [mm] radial length from hinge to tip
PETAL_CURVE_R    = HOUSING_OUTER_R;  // [mm] outer face convex radius = housing OD


// =============================================================================
// ── Module: nozzle_fixed_housing ─────────────────────────────────────────────
// =============================================================================
// Fixed outer housing bonded to the nacelle exit face.
//
// Geometry:
//   Main body  : Annular disk, OD = 70 mm, ID = 50 mm, H = 10 mm.
//   Bonding lip: Annular step at the forward (nacelle-side) face, H = 3 mm,
//                OD = 70 mm, ID = 52 mm; registers against nacelle exit face
//                and provides an epoxy bonding surface.
//   Hinge bores: 8× Z-axis through-holes at PETAL_HINGE_R = 33 mm, Ø 3.2 mm.
//                Holes span full housing + lip height for through-pin installation.
//
// NO pinion access slot (compared with iris nozzle_outer_housing).
// NO inner bore enlargement for a rotating ring.
// Bore is the full EDF_BORE_R = 25 mm throughout housing + lip thickness.
//
// Origin: Z = 0 at bonding lip inboard face (nacelle exit face contact plane).
//         Z = HOUSING_H at housing outboard face.
//         +Z = away from nacelle (downstream / exhaust direction).
module nozzle_fixed_housing() {
    difference() {

        // ── Main housing body + bonding lip (additive) ────────────────────
        union() {
            // Main annular disk body
            cylinder(h = HOUSING_H, r = HOUSING_OUTER_R);

            // Forward bonding lip (sits against nacelle exterior exit face)
            translate([0, 0, -HOUSING_LIP_H])
                difference() {
                    cylinder(h = HOUSING_LIP_H, r = HOUSING_OUTER_R);
                    // Inner clearance: 1 mm larger than EDF bore to clear edge
                    translate([0, 0, -0.1])
                        cylinder(h = HOUSING_LIP_H + 0.2, r = HOUSING_LIP_R);
                }
        }

        // ── EDF airflow bore (straight through — no rotating ring) ────────
        // 50 mm ID bore spans housing body and bonding lip with 0.1 mm overrun.
        translate([0, 0, -HOUSING_LIP_H - 0.1])
            cylinder(h = HOUSING_H + HOUSING_LIP_H + 0.2, r = EDF_BORE_R);

        // ── 8× hinge pin bores (Z-axis through-holes at PETAL_HINGE_R) ───
        // Hinge pins are 3 mm × 18 mm SS dowels pressed into these bores.
        // Petals pivot on the exposed pin (between housing faces).
        // Pins are bonded with threadlocker once petals are positioned.
        for (p = [0 : N_PETALS - 1]) {
            rotate([0, 0, p * 360 / N_PETALS])
                translate([PETAL_HINGE_R, 0, -HOUSING_LIP_H - 0.1])
                    cylinder(h = HOUSING_H + HOUSING_LIP_H + 0.2, d = HINGE_BORE_D);
        }

    }
}


// =============================================================================
// ── Module: nozzle_petal_fixed ────────────────────────────────────────────────
// =============================================================================
// One decorative fixed petal.  Geometry is identical to the iris petal
// (nacelle_nozzle_iris.scad nozzle_petal()) with the link-ring slot removed.
// No link-ring slot means no piano-wire connection; petals cannot be driven
// mechanically.
//
// Shape:
//   Trapezoidal curved planform, wider at hinge root, narrower at tip.
//   2D footprint: pie sector spanning PETAL_SPAN_DEG about hinge pin axis [0,0].
//   Inner cutout clears hinge knuckle (r = 4.0 mm).
//   Tip arc radius from hinge = PETAL_LENGTH + 3 mm = 21 mm.
//   Extruded PETAL_THICKNESS = 2.5 mm in Z.
//
// Hinge bore:
//   3.2 mm Z-axis through-hole at [0, 0] — mates with hinge pin in housing.
//   Hinge knuckle lug (OD = 7.2 mm) provides bearing contact width.
//
// NO link-ring slot (1.2 mm wire hole removed; compare iris version).
//
// Origin: hinge pin centreline at [0, 0, 0]; petal extends in +X / ±Y plane.
//         Rotate [0,0,angle] and translate [PETAL_HINGE_R, 0, 0] to place in
//         housing.
//
// Assembly note:
//   Set petal at desired fixed angle before threading hinge pin.  Apply
//   medium-strength threadlocker to both pin ends once position is confirmed.
//   Recommended position: tips approximately flush with bore exit (closed).
module nozzle_petal_fixed() {
    difference() {

        // ── Petal slab body ───────────────────────────────────────────────
        // 2D footprint: annular sector from r=4 mm (clear knuckle) to
        // PETAL_LENGTH+3 mm, spanning 0° to PETAL_SPAN_DEG.
        linear_extrude(height = PETAL_THICKNESS) {
            difference() {
                // Tip arc — outer edge of petal from hinge
                circle(r = PETAL_LENGTH + 3);
                // Inner cutout — clears hinge knuckle lug
                circle(r = 4.0);
                // Angular mask: upper boundary (clip at PETAL_SPAN_DEG)
                rotate([0, 0, PETAL_SPAN_DEG])
                    square([100, 100]);
                // Angular mask: lower boundary (clip at 0° below X-axis)
                rotate([0, 0, 180])
                    square([100, 100]);
            }
        }

        // ── Hinge bore (Z-axis through-hole at origin) ────────────────────
        // 3.2 mm clearance bore mates with 3 mm SS hinge pin in housing.
        translate([0, 0, -0.1])
            cylinder(h = PETAL_THICKNESS + 0.2, d = HINGE_BORE_D);

        // NOTE: link-ring slot is intentionally omitted in this fixed variant.

    }

    // ── Hinge knuckle lug ────────────────────────────────────────────────────
    // Cylindrical reinforcement around the hinge bore; provides bearing
    // contact width between petal and housing hinge bore face.
    // OD = HINGE_BORE_D + 4.0 mm = 7.2 mm; bore = HINGE_BORE_D = 3.2 mm.
    difference() {
        cylinder(h = PETAL_THICKNESS, d = HINGE_BORE_D + 4.0);
        translate([0, 0, -0.1])
            cylinder(h = PETAL_THICKNESS + 0.2, d = HINGE_BORE_D);
    }
}


// =============================================================================
// ── Fit Confirmation ──────────────────────────────────────────────────────────
// =============================================================================
//
//   Interface                   Mating part                    Clearance / fit
//   ──────────────────────────  ─────────────────────────────  ─────────────────
//   Housing lip OD 70 mm        Nacelle exit face exterior     epoxy bond,
//   (bonding lip, H = 3 mm)     nacelle_pod_50mm_tandem_simple shoulder stop
//   Housing bore Ø 50 mm        EDF bore Ø 50 mm (nacelle)    flush, coaxial
//   HINGE_BORE_D 3.2 mm         3 mm × 18 mm SS hinge pin     0.2 mm diametral
//   (8 bores, r = 33 mm)                                       clearance; bond
//   Petal hinge bore 3.2 mm     3 mm × 18 mm SS hinge pin     0.2 mm clearance
//   Knuckle lug OD 7.2 mm       Housing bore face flat         abutment contact


// =============================================================================
// ── Render Instructions ───────────────────────────────────────────────────────
// =============================================================================
//
// Export housing (STL for print):
nozzle_fixed_housing();
//
// Export one petal (STL for print × 8):
// nozzle_petal_fixed();
//
// Assembly preview — housing + all 8 petals at closed / cruise position:
// nozzle_fixed_housing();
// for (i = [0 : N_PETALS - 1]) {
//     rotate([0, 0, i * 360 / N_PETALS])
//         translate([PETAL_HINGE_R, 0, 0])
//             rotate([0, 0, -PETAL_SPAN_DEG / 2])
//                 nozzle_petal_fixed();
// }
//
// Render commands:
//   openscad -o nacelle_nozzle_straight_housing.stl nacelle_nozzle_straight.scad
//   Uncomment nozzle_petal_fixed() and comment housing before exporting petal:
//   openscad -o nacelle_nozzle_straight_petal.stl nacelle_nozzle_straight.scad
