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
// nacelle_bevel_pair.scad
// Serenity UAV Rev S1 — Nacelle Tilt Linkage, 10:14 Reducing Bevel Gear Pair
//
// Purpose:
//   A matched pair of M = 0.8 straight bevel gears providing BOTH the 90°
//   shaft-angle redirection AND a 10:14 speed reduction in the nacelle
//   tilt-to-nozzle gear train (Rev S1 internal-ring drive — see
//   docs/NOZZLE_DRIVE_TRADE.md).  Input on the transverse axis (from Drive
//   Pinion A, 322.94° per 90° tilt) is redirected to the longitudinal axis
//   and reduced ×10/14 (→ 230.67° per 90° tilt at the Nozzle Drive Pinion).
//
//   Gear A (Bevel A, 10T) — transverse axis; driven by the Pinion A shaft.
//   Gear B (Bevel B, 14T) — longitudinal axis; drives the longitudinal 3 mm
//     CF shaft to the Nozzle Drive Pinion (M0.5 14T, nacelle_pinion.scad
//     PINION_VARIANT="DRIVE") at the nozzle ring.
//
// COTS substitution note (Rev S1, 2026-07-07):
//   Commodity metal/POM bevel SETS are commonly sold in 1:1 and 2:1 ratios
//   (mod 0.5–1.0); the exact 10:14 ratio here is NOT a common catalog item.
//   If procurement sources a verified 2:1 set instead, the only design
//   change required is the ring-sweep constant THETA_RING_REF_OPEN in
//   nacelle_nozzle_iris.scad (23.74° → 16.61°; the spiral cam recuts
//   parametrically).  Record the substitution in the BOM and TODO.md
//   §1.1.3.3 before printing the unison ring.
//
// Bevel gear geometry basis:
//   90° shaft angle, ratio 10:14 → per-gear pitch cone half-angles:
//     GAMMA_A = atan(N_A / N_B) = atan(10/14) = 35.54°
//     GAMMA_B = 90° − GAMMA_A            = 54.46°
//   AGMA 2005: straight bevel, Module at large end M = 0.8 mm.
//   Pitch radii at large end: R_A = 4.0 mm, R_B = 5.6 mm.
//   Shared pitch-cone slant distance: L = R_A/sin(GAMMA_A)
//                                       = R_B/sin(GAMMA_B) = 6.882 mm.
//   Face width rule: F ≤ L/3 = 2.29 mm; F = 2.2 mm used.
//   Tooth proportions at large end (back-cone plane approximation):
//     Addendum  a = M = 0.8 mm;  Dedendum  b = 1.25 × M = 1.0 mm.
//     Addendum and dedendum taper toward the apex over the face width.
//
// Mating interfaces:
//   Bevel A (10T):
//     • Drive Pinion A shaft (nacelle_pinion.scad, PINION_VARIANT="A"):
//         3 mm CF shaft, D-key bore.
//     • Bevel housing transverse bore (nacelle_bevel_housing.scad).
//     • Mesh with Bevel B: pitch cones tangent; shaft axes intersect at the
//         shared virtual apex (5.6 mm above A's large-end face on A's axis;
//         4.0 mm above B's large-end face on B's axis).
//   Bevel B (14T):
//     • Longitudinal shaft: 3 mm CF shaft, D-key bore.
//     • Bevel housing longitudinal bore (nacelle_bevel_housing.scad).
//   Shaft support: MR63ZZ bearings live in the HOUSING bores
//     (nacelle_bevel_housing.scad), NOT in these gears — the Rev R gears
//     carried a 6.05 mm bearing seat inside a 6.0 mm hub (zero wall — a
//     latent defect); Rev S1 deletes the in-gear seats entirely.
//
// Gear standard: AGMA 2005 / ISO 10300 straight bevel, involute equivalent.
// Tooth profile: simplified trapezoidal approximation — tooth-space
//   subtraction on the conical face.  Adequate at M = 0.8 in SLA resin.
//
// Print specification:
//   Required:   SLA resin, ≤ 0.05 mm layer height (M0.8 teeth are too fine
//               for reliable 0.4 mm-nozzle FDM).
//   Orientation: Print with large-end face down (cone apex upward).
//
// Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date:    2026-05-24
// Rev:     R  (2026-06-11): Rev R baseline — 1:1 M1.0 14T:14T pair.
// Rev:     S1 (2026-07-07): Re-ratioed 1:1 → 10:14 (M1.0 → M0.8) for the
//          internal-ring nozzle drive (idler stage deleted — see
//          docs/NOZZLE_DRIVE_TRADE.md and nacelle_nozzle_iris.scad).
//          Per-gear cone geometry parametrized; in-gear MR63ZZ bearing
//          seats deleted (they had zero wall — bearings are in the housing).
//          AI contribution: Claude (Fable 5, Anthropic), 2026-07-07,
//          directed by Steve Griffing.

// ── Resolution ────────────────────────────────────────────────────────────────

$fn = 72;   // standard circle resolution

// ── Gear Parameters ───────────────────────────────────────────────────────────

MODULE           =  0.8;   // [mm] AGMA Module at large end of bevel
N_TEETH_A        = 10;     // [count] Bevel A (input, transverse axis)
N_TEETH_B        = 14;     // [count] Bevel B (output, longitudinal axis)
PRESSURE_ANGLE   = 20.0;   // [deg] standard involute pressure angle

// Pitch cone half-angles (90° shaft angle):
GAMMA_A = atan(N_TEETH_A / N_TEETH_B);   // [deg] = 35.54° (Bevel A)
GAMMA_B = 90 - GAMMA_A;                  // [deg] = 54.46° (Bevel B)

// ── Derived Bevel Geometry (shared) ───────────────────────────────────────────

PITCH_R_A = N_TEETH_A * MODULE / 2;      // [mm] = 4.0  large-end pitch R, A
PITCH_R_B = N_TEETH_B * MODULE / 2;      // [mm] = 5.6  large-end pitch R, B

ADDENDUM  = MODULE;                       // [mm] = 0.8  at large end
DEDENDUM  = 1.25 * MODULE;               // [mm] = 1.0  at large end

// Shared pitch-cone slant distance (identical for both gears by construction):
CONE_DIST = PITCH_R_A / sin(GAMMA_A);    // [mm] ≈ 6.882

FACE_WIDTH = 2.2;   // [mm] face width along the slant (≤ CONE_DIST/3 = 2.29,
                     //   AGMA 2005 §8.4 maximum honoured — Rev S1 fix; the
                     //   Rev R value exceeded the rule by 20 %)

// Small-end taper factor (proportional taper toward the apex):
TAPER = (CONE_DIST - FACE_WIDTH) / CONE_DIST;   // ≈ 0.680

// ── Shaft and Hub Parameters ──────────────────────────────────────────────────

SHAFT_BORE   =  3.2;   // [mm] 3 mm CF shaft + 0.2 mm clearance
SHAFT_KEY_W  =  1.0;   // [mm] flat key chord width (D-profile bore)
BEVEL_H      =  6.0;   // [mm] total axial height incl. hub behind the cone
HUB_OD       =  6.0;   // [mm] hub outer diameter (registers in housing bore)

// ── Module Definitions ────────────────────────────────────────────────────────
//
// All geometry modules take the gear's tooth count and pitch-cone half-angle
// so one construction serves both gears (Rev S1 — the pair is no longer 1:1).

// bevel_cone_frustum(n, gamma) — solid conical blank, large end at Z = 0.
module bevel_cone_frustum(n, gamma) {
    pitch_r = n * MODULE / 2;
    tip_r   = pitch_r + ADDENDUM;           // back-cone plane approximation
    cone_h  = FACE_WIDTH * cos(gamma);      // axial projection of face width
    cylinder(h  = cone_h,
             r1 = tip_r,                    // large end at Z = 0
             r2 = tip_r * TAPER);           // small end toward apex
}

// bevel_hub(gamma) — cylindrical hub behind the large-end face
//   (Z = -(BEVEL_H - cone_h) .. 0).  Plain hub: NO bearing seat (Rev S1 —
//   the shaft's MR63ZZ bearings are housed in nacelle_bevel_housing.scad).
module bevel_hub(gamma) {
    cone_h = FACE_WIDTH * cos(gamma);
    hub_h  = BEVEL_H - cone_h;
    translate([0, 0, -hub_h])
        cylinder(h = hub_h, d = HUB_OD);
}

// bevel_tooth_space(i, n, gamma) — one tooth-space void on the conical face,
//   a hull between matching thin wedge slices at the large and small ends
//   (same trapezoidal approximation as Rev R, now per-gear parametric).
module bevel_tooth_space(i, n, gamma) {
    pitch_r  = n * MODULE / 2;
    tip_r    = pitch_r + ADDENDUM;
    root_r   = pitch_r - DEDENDUM;
    cone_h   = FACE_WIDTH * cos(gamma);
    ang_pitch = 360.0 / n;
    half_ang  = ang_pitch / 4;   // quarter pitch = half tooth-space width

    space_centre = i * ang_pitch + ang_pitch / 2;

    hull() {
        // Large-end wedge slice (thin disk at Z ≈ 0):
        linear_extrude(height = 0.1) {
            rotate([0, 0, space_centre - half_ang]) {
                difference() {
                    circle(r = tip_r + 0.1);
                    circle(r = root_r - 0.1);
                    rotate([0, 0, 2 * half_ang]) square([50, 50]);
                    rotate([0, 0, 180])           square([50, 50]);
                }
            }
        }

        // Small-end wedge slice (thin disk at Z = cone_h, tapered radii):
        translate([0, 0, cone_h - 0.1]) {
            linear_extrude(height = 0.1) {
                rotate([0, 0, space_centre - half_ang]) {
                    difference() {
                        circle(r = tip_r * TAPER + 0.1);
                        circle(r = max(root_r * TAPER - 0.1, 0.5));
                        rotate([0, 0, 2 * half_ang]) square([50, 50]);
                        rotate([0, 0, 180])           square([50, 50]);
                    }
                }
            }
        }
    }
}

// bevel_shaft_bore(gamma) — D-profile shaft bore through hub + cone.
module bevel_shaft_bore(gamma) {
    cone_h = FACE_WIDTH * cos(gamma);
    hub_h  = BEVEL_H - cone_h;
    total  = BEVEL_H + 0.2;
    translate([0, 0, -hub_h - 0.1]) {
        union() {
            cylinder(h = total, d = SHAFT_BORE);
            // D-key flat: thin box removing the chord segment of the bore
            translate([0, SHAFT_BORE / 2 - SHAFT_KEY_W / 2, total / 2 - 0.1])
                cube([SHAFT_BORE + 0.2, SHAFT_KEY_W, total], center = true);
        }
    }
}

// bevel_gear(n, gamma) — complete straight bevel gear, large end at Z = 0,
//   small end toward +Z (apex direction), hub behind (−Z).
module bevel_gear(n, gamma) {
    difference() {
        union() {
            bevel_cone_frustum(n, gamma);
            bevel_hub(gamma);
        }
        for (i = [0 : n - 1]) {
            bevel_tooth_space(i, n, gamma);
        }
        bevel_shaft_bore(gamma);
    }
}

// bevel_gear_a() — 10T input gear (transverse / Pinion-A shaft axis).
module bevel_gear_a() { bevel_gear(N_TEETH_A, GAMMA_A); }

// bevel_gear_b() — 14T output gear (longitudinal shaft axis).
module bevel_gear_b() { bevel_gear(N_TEETH_B, GAMMA_B); }

// ── Fit Confirmation ──────────────────────────────────────────────────────────
//
//   Interface                 Mating part                Clearance / fit
//   ────────────────────────  ─────────────────────────  ────────────────────
//   A large-end pitch R 4.0   B large-end pitch R 5.6    pitch cones tangent;
//   (10T, GAMMA 35.54°)       (14T, GAMMA 54.46°)         0.1 mm backlash via
//                                                          housing bore offset
//   SHAFT_BORE 3.2 mm         3 mm CF shaft              0.2 mm diametral clr
//   HUB_OD 6.0 mm             Housing bore (8.5 mm)      1.25 mm radial clr
//   Apex coincidence          both axes                  apex 5.6 mm above A
//                                                          face / 4.0 above B
//   Bearings                  MR63ZZ in HOUSING bores    none in-gear (Rev S1)

// ── Render ────────────────────────────────────────────────────────────────────
//
// RENDER_GEAR = "pair" (default) renders the meshed-pair assembly preview —
// the single STL serenity_assembly.py imports for spatial checks.  Export
// print-ready singles with -D 'RENDER_GEAR="a"' / -D 'RENDER_GEAR="b"'.
RENDER_GEAR = "pair";   // "a" | "b" | "pair"

if (RENDER_GEAR == "a") {
    bevel_gear_a();
} else if (RENDER_GEAR == "b") {
    bevel_gear_b();
} else {
    // Meshed pair preview: shared apex at (0, 0, 5.6).
    //   A: axis +Z, large face at Z=0, apex at Z = R_A/tan(GAMMA_A) = 5.6.
    //   B: axis +Y after rotate([-90,0,0]); its local apex (0,0,4.0) maps to
    //      origin+(0,4,0), so origin (0,-4,5.6) puts B's apex at (0,0,5.6).
    bevel_gear_a();
    translate([0, -PITCH_R_A, PITCH_R_B])
        rotate([-90, 0, 0])
            bevel_gear_b();
}
