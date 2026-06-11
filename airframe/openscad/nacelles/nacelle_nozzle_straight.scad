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
// =============================================================================
// nacelle_nozzle_straight.scad
// Serenity UAV — Rev T2 — Push-On Straight Nozzle with Decorative Petals
// =============================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-06-07
// Revision: Rev T2 (push-on boss retention — no threads)
//
// Description
// -----------
// Rev T2 replacement for nacelle_nozzle_iris.scad (Rev O) and Rev T1.
// The variable-diameter iris, its gear-driven actuation, and the T1 epoxy-bonded
// housing are all removed.  This file produces a push-on straight-bore nozzle
// housing (50 mm exit diameter, constant) retained by 3× M3 set screws, plus
// eight decorative imitation petals that replicate the visual appearance of the
// iris nozzle without mechanical function.
//
// Two separately-printable parts:
//     1. nozzle_push_housing()  — push-on housing; retained by 3× M3 set screws
//     2. nozzle_petal_fixed()   — one decorative petal (print × 8)
//
// Changes from Rev T1 (epoxy-bonded housing):
//     REMOVED — bonding lip geometry       forward lip that epoxy-bonded to nacelle
//     REMOVED — HOUSING_LIP_H, LIP_R       bonding lip parameters
//     ADDED   — skirt section              bore over nacelle push-on boss (Ø 60 mm)
//     ADDED   — 3× M3 set-screw bores      radially through skirt at 0°/120°/240°
//     ADDED   — SET_SCREW_ANG, BOSS_R,     set-screw geometry parameters
//               M3_TAP_D, BOSS_CLEARANCE
//     RETAINED — housing body geometry     70 mm OD, 50 mm bore, hinge bores
//     RETAINED — petal geometry            no change from Rev T1
//
// Retention mechanism
// -------------------
//     Housing skirt bore (Ø 60.25 mm) slides over nacelle push-on boss
//     (Ø 60 mm, protruding 12 mm aft of nacelle exit face).  Shoulder stop
//     at bore step (60.25 mm → 50 mm) seats on nacelle boss aft face.
//     Three M3×6 flat-point SHCS through housing skirt engage shallow flats
//     (0.75 mm deep) on the nacelle boss OD at 0°/120°/240°.
//     Removal: loosen 3× set screws (2.5 mm hex key), pull housing off boss.
//
// Nozzle exit
// -----------
//     Exit diameter is fixed at 50 mm (EDF bore) regardless of nacelle tilt.
//
// Decorative petal function
// -------------------------
//     Petals installed on 3 mm × 18 mm stainless steel hinge pins pressed into
//     housing hinge bores.  Once positioned, pins are secured with medium-
//     strength threadlocker (Loctite 243 or equivalent).  Petals DO NOT ROTATE
//     after final assembly.  Cosmetic features matching REVT iris look.
//
//     Recommended fixed position: closed / cruise (petal tips roughly flush
//     with bore exit).  Adjust to taste before threadlocking.
//
// Mating interface
// ----------------
//     Mates to nacelle_pod_50mm_tandem_simple.scad Rev T2 push-on boss.
//     Boss OD = 60 mm; housing skirt bore = 60.25 mm (0.25 mm diametral).
//     Shoulder stop: housing bore step seats on nacelle boss aft face.
//     Set-screw flats on nacelle boss at 0°/120°/240° — align housing
//     set-screw holes before driving screws.
//
// Print specification — Housing:
//     Material    : CF-PETG (structural bore; hinge bore load; set-screw wall)
//     Layers      : 0.15 mm; 4 perimeters; 40% gyroid infill
//     Orientation : Exhaust face down (exhaust face on build plate)
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
//     [1] nacelle_pod_50mm_tandem_simple.scad Rev T2 — push-on boss geometry.
//     [2] nacelle_nozzle_iris.scad Rev O — iris petal geometry (geometric basis).
//     [3] nacelle_nozzle_straight.scad Rev T1 — epoxy-bonded predecessor.
//     [4] Serenity-UAV project CLAUDE.md — fabrication standards (2026).
//
// =============================================================================


// =============================================================================
// ── Resolution ────────────────────────────────────────────────────────────────
// =============================================================================

$fn = 72;   // standard circle resolution


// =============================================================================
// ── Parameter Block ───────────────────────────────────────────────────────────
// =============================================================================

// ── Bore and housing body dimensions ─────────────────────────────────────────

EDF_BORE_R       = 25.0;   // [mm] EDF bore inner radius → 50 mm ID (fixed exit)
HOUSING_OUTER_R  = 35.0;   // [mm] housing outer radius → OD = 70 mm
HOUSING_BODY_H   = 10.0;   // [mm] body section axial depth (exhaust side, 50 mm bore)

// ── Push-on boss interface (must match nacelle_pod_50mm_tandem_simple.scad T2) ─

NOZZLE_BOSS_OD   = 60.0;   // [mm] nacelle push-on boss OD (housing slides over this)
NOZZLE_BOSS_H    = 12.0;   // [mm] nacelle boss protrusion height = skirt section height
BOSS_CLEARANCE   =  0.25;  // [mm] diametral clearance on skirt bore (smooth push-on fit)

// ── Set-screw geometry ────────────────────────────────────────────────────────
// 3× M3 flat-point set screws radially through housing skirt at 0°/120°/240°.
// Set-screw holes are tapped M3 (2.5 mm tap drill).
// Bore direction: radial (inward from housing OD); engages nacelle boss flats.

SET_SCREW_ANGLES = [0, 120, 240];  // [deg] angular positions (match nacelle boss flats)
M3_TAP_D         =  2.5;           // [mm] M3 tap drill diameter

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
// ── Module: nozzle_push_housing ──────────────────────────────────────────────
// =============================================================================
// Push-on housing with set-screw retention.
//
// Geometry — two coaxial sections:
//
//   Body section (Z = 0 … HOUSING_BODY_H, exhaust side):
//     OD = 70 mm (HOUSING_OUTER_R = 35 mm).
//     Bore = 50 mm (EDF_BORE_R = 25 mm).
//     Contains 8× Z-axis hinge pin bores at PETAL_HINGE_R = 33 mm.
//
//   Skirt section (Z = HOUSING_BODY_H … HOUSING_BODY_H + NOZZLE_BOSS_H, nacelle side):
//     OD = 70 mm (same as body).
//     Bore = NOZZLE_BOSS_OD + BOSS_CLEARANCE = 60.25 mm.
//     Slides over nacelle push-on boss (Ø 60 mm).
//     Shoulder at bore step (Z = HOUSING_BODY_H) seats on nacelle boss aft face.
//     3× M3 tap-drill bores radially through skirt at SET_SCREW_ANGLES.
//
// Origin: Z = 0 at exhaust face (downstream); +Z toward nacelle.
//         Housing seated: nacelle boss aft face at Z = HOUSING_BODY_H.
//         Nacelle exit face at Z = HOUSING_BODY_H + NOZZLE_BOSS_H.
module nozzle_push_housing() {
    difference() {

        // ── Additive: body + skirt cylinder ──────────────────────────────────
        union() {
            // Body section — exhaust-side annular disk
            cylinder(h = HOUSING_BODY_H, r = HOUSING_OUTER_R);

            // Skirt section — nacelle-side skirt that surrounds boss
            translate([0, 0, HOUSING_BODY_H])
                cylinder(h = NOZZLE_BOSS_H, r = HOUSING_OUTER_R);
        }

        // ── Airflow bore (50 mm ID, full housing height) ──────────────────────
        // Constant 50 mm EDF bore from exhaust face through body section.
        // Shoulder stop at Z = HOUSING_BODY_H is the bore step to skirt bore.
        translate([0, 0, -0.1])
            cylinder(h = HOUSING_BODY_H + 0.2, r = EDF_BORE_R);

        // ── Skirt bore (60.25 mm ID, skirt section only) ──────────────────────
        // Smooth push-on fit over nacelle boss OD = 60 mm.
        // Shoulder at bore step Z = HOUSING_BODY_H stops on nacelle boss aft face.
        translate([0, 0, HOUSING_BODY_H - 0.1])
            cylinder(h = NOZZLE_BOSS_H + 0.2,
                     r = (NOZZLE_BOSS_OD + BOSS_CLEARANCE) / 2);

        // ── 3× M3 set-screw tap-drill bores (radial through skirt wall) ───────
        // Each bore runs from the skirt bore inner surface (r = boss_r) outward
        // to housing OD + 0.1 mm overrun to open the outer face.
        // Aligned at skirt mid-height = HOUSING_BODY_H + NOZZLE_BOSS_H / 2.
        for (angle = SET_SCREW_ANGLES) {
            rotate([0, 0, angle])
                translate([0, 0, HOUSING_BODY_H + NOZZLE_BOSS_H / 2])
                    rotate([0, 90, 0])
                        // Start at skirt bore inner radius; go outward to OD + margin
                        translate([0, 0, (NOZZLE_BOSS_OD + BOSS_CLEARANCE) / 2])
                            cylinder(r = M3_TAP_D / 2,
                                     h = HOUSING_OUTER_R
                                         - (NOZZLE_BOSS_OD + BOSS_CLEARANCE) / 2
                                         + 0.1,
                                     center = false);
        }

        // ── 8× hinge pin bores (Z-axis through body section only) ─────────────
        // Bores at PETAL_HINGE_R = 33 mm; span body section with 0.1 mm overrun.
        // Housing skirt section has no hinge bores.
        for (p = [0 : N_PETALS - 1]) {
            rotate([0, 0, p * 360 / N_PETALS])
                translate([PETAL_HINGE_R, 0, -0.1])
                    cylinder(h = HOUSING_BODY_H + 0.2, d = HINGE_BORE_D);
        }

    }
}


// =============================================================================
// ── Module: nozzle_petal_fixed ────────────────────────────────────────────────
// =============================================================================
// One decorative fixed petal — geometry unchanged from Rev T1.
// Link-ring slot is intentionally absent (no piano-wire connection).
//
// Shape:
//   Trapezoidal curved planform, wider at hinge root, narrower at tip.
//   2D footprint: pie sector spanning PETAL_SPAN_DEG about hinge pin axis.
//   Inner cutout clears hinge knuckle (r = 4.0 mm).
//   Tip arc radius from hinge = PETAL_LENGTH + 3 mm = 21 mm.
//   Extruded PETAL_THICKNESS = 2.5 mm in Z.
//
// Hinge bore:
//   3.2 mm Z-axis through-hole at [0, 0] — mates with hinge pin in housing.
//   Hinge knuckle lug (OD = 7.2 mm) provides bearing contact width.
//
// Origin: hinge pin centreline at [0, 0, 0]; petal extends in +X / ±Y plane.
//         Rotate [0,0,angle] and translate [PETAL_HINGE_R, 0, 0] to place in
//         housing.
module nozzle_petal_fixed() {
    difference() {

        // ── Petal slab body ───────────────────────────────────────────────────
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

        // ── Hinge bore (Z-axis through-hole at origin) ────────────────────────
        translate([0, 0, -0.1])
            cylinder(h = PETAL_THICKNESS + 0.2, d = HINGE_BORE_D);

        // NOTE: link-ring slot intentionally omitted — fixed petal variant.

    }

    // ── Hinge knuckle lug ─────────────────────────────────────────────────────
    // Cylindrical reinforcement around hinge bore; bearing contact between
    // petal and housing hinge bore face.  OD = 7.2 mm; bore = HINGE_BORE_D.
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
//   Skirt bore Ø 60.25 mm       Nacelle boss OD Ø 60 mm        0.25 mm diametral
//   (skirt section, H = 12 mm)  nozzle_push_boss() Rev T2      push-on clearance
//   Shoulder stop at bore step  Nacelle boss aft face           positive axial stop
//   (Z = HOUSING_BODY_H)        (Z = NACELLE_L in nacelle)
//   3× M3 tap bores in skirt    3× M3×6 flat-point SHCS        tapped M3
//   (r = 35 mm OD, 120° apart)  (field tool: 2.5 mm hex key)
//   Set-screw tip engagement    Nacelle boss OD flat            0.75 mm flat depth
//   HINGE_BORE_D 3.2 mm         3 mm × 18 mm SS hinge pin      0.2 mm clearance
//   (8 bores, r = 33 mm,        body section only              bond with threadlocker
//    Z = 0 … HOUSING_BODY_H)
//   Petal hinge bore 3.2 mm     3 mm × 18 mm SS hinge pin      0.2 mm clearance
//   Knuckle lug OD 7.2 mm       Housing bore face flat         abutment contact


// =============================================================================
// ── Render Instructions ───────────────────────────────────────────────────────
// =============================================================================
//
// Export housing (STL for print):
nozzle_push_housing();
//
// Export one petal (STL for print × 8):
// nozzle_petal_fixed();
//
// Assembly preview — housing + all 8 petals at closed / cruise position:
// nozzle_push_housing();
// for (i = [0 : N_PETALS - 1]) {
//     rotate([0, 0, i * 360 / N_PETALS])
//         translate([PETAL_HINGE_R, 0, 0])
//             rotate([0, 0, -PETAL_SPAN_DEG / 2])
//                 nozzle_petal_fixed();
// }
//
// Render commands:
//   openscad -o nacelle_nozzle_straight_housing_revt2.stl nacelle_nozzle_straight.scad
//   Uncomment nozzle_petal_fixed() and comment housing before exporting petal:
//   openscad -o nacelle_nozzle_straight_petal_revt2.stl nacelle_nozzle_straight.scad
