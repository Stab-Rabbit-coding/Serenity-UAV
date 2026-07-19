// =============================================================================
// gear_option_compare.scad — DECISION AID (2026-07-18)
// Serenity UAV — nacelle-tilt fixed-gear size comparison
// =============================================================================
//
// Author  : Steve Griffing (drafted by Claude Opus 4.8)
// License : CC BY 4.0
//
// Purpose
// -------
// 2-D comparison, IN THE TILT ROTATION PLANE (nacelle fore-aft Y vs duct Z),
// of the two fixed-gear options for the rotating-spar nacelle tilt drive:
//
//   MODE = "R22"       fixed sector R22 / Pinion A R8.5, centre distance 30.5
//                      (preserves the one-shaft nozzle drive, NO idler)
//   MODE = "R14_IDLER" fixed sector R14 / Pinion A R5.5, centre distance 19.5
//                      + idler bridging back to the Y=30.5 nozzle shaft
//
// The pivot (spar axis) is at the origin.  The fixed sector is COAXIAL with the
// spar (centred on the pivot).  Pinion A is mounted on the NACELLE at radius =
// centre distance, on the fore-aft (+Y) side.  The heavy circle is the nacelle
// fore-aft OD boundary (OD_Y = 67 mm → r = 33.5 mm) at the pivot station: any
// gear geometry OUTSIDE it protrudes past the canonical nacelle skin.
//
// KEY QUESTION the picture answers: does the mesh stay INSIDE the nacelle OD?
//   • R22:       Pinion A outer edge at 30.5 + 9.5 = 40.0 mm  → 6.5 mm PROUD  ✗
//   • R14_IDLER: Pinion A outer edge at 19.5 + 6.5 = 26.0 mm  → 7.5 mm inside ✓
//
// Render both:
//   openscad -o /tmp/gear_R22.png       gear_option_compare.scad -D 'MODE="R22"'
//   openscad -o /tmp/gear_R14.png       gear_option_compare.scad -D 'MODE="R14_IDLER"'
// =============================================================================

MODE = "R22";          // "R22" or "R14_IDLER" — override at CLI with -D
$fn  = 96;

// ── Fixed geometry ───────────────────────────────────────────────────────────
NAC_OD_Y_R   = 33.5;   // [mm] nacelle fore-aft OD half-width at pivot (OD_Y 67 / 2)
DUCT_R       = 25.0;   // [mm] EDF bore radius (reference; duct axis = +Z here)
NOZZLE_SHAFT_Y = 30.5; // [mm] longitudinal nozzle-drive shaft offset (fixed by
                       //      internal-ring mesh R_ring 34 − R_drive 3.5)
SWEEP_DEG    = 95;     // [deg] tilt sweep (−5°..90°) the sector arc must cover
LINE         = 0.5;    // [mm] outline thickness

// ── Per-mode gear parameters (Module 1.0) ────────────────────────────────────
SECTOR_PR = (MODE == "R22") ? 22.0 : 14.0;   // sector pitch radius
SECTOR_TR = SECTOR_PR + 1.0;                  // sector tip radius
PINION_PR = (MODE == "R22") ? 8.5  : 5.5;     // Pinion A pitch radius
PINION_TR = PINION_PR + 1.0;                  // Pinion A tip radius
CDIST     = SECTOR_PR + PINION_PR;            // centre distance (30.5 or 19.5)

// ── Helpers ──────────────────────────────────────────────────────────────────
module ring(r, w = LINE) { difference() { circle(r); circle(r - w); } }

module pitch_circle(cx, cy, pr) {
    translate([cx, cy]) difference() { circle(pr); circle(pr - 0.3); }
}

module gear_blank(cx, cy, tr) { translate([cx, cy]) circle(tr); }

// Sector arc: coaxial wedge of the fixed gear, spanning SWEEP_DEG + margin,
// centred about +Y (the side Pinion A sits on).
module sector(tr) {
    span = SWEEP_DEG + 20;                    // teeth margin each end
    a0 = 90 - span / 2;  a1 = 90 + span / 2;  // centred on +Y (90°)
    intersection() {
        circle(tr);
        polygon(concat([[0, 0]],
            [ for (a = [a0 : 2 : a1]) [1.2 * tr * cos(a), 1.2 * tr * sin(a)] ]));
    }
}

// =============================================================================
// ── Drawing ──────────────────────────────────────────────────────────────────
// =============================================================================

// Nacelle fore-aft OD boundary (the "do not cross" line for canonical skin).
color("black") ring(NAC_OD_Y_R, 0.8);

// Duct bore reference strip edges (|Y| = 25 lines, duct flows along Z).
color("gray")
    for (s = [-1, 1])
        translate([s * DUCT_R - LINE / 2, -NAC_OD_Y_R]) square([LINE, 2 * NAC_OD_Y_R]);

// Fixed sector gear (coaxial with the spar / pivot at origin).
color("steelblue") sector(SECTOR_TR);
color("navy")      pitch_circle(0, 0, SECTOR_PR);

// Pinion A on the nacelle at (+Y = CDIST).
color([1, 0.6, 0, 0.85]) gear_blank(0, CDIST, PINION_TR);
color("darkorange")      pitch_circle(0, CDIST, PINION_PR);

// Nozzle-drive shaft station (must be reached by the train).
color("red")
    translate([0, NOZZLE_SHAFT_Y]) difference() { circle(2.0); circle(1.4); }

// Mode-specific: the R14 option needs an idler to bridge CDIST(19.5) → 30.5.
if (MODE == "R14_IDLER") {
    // Idler sits between the Pinion-A shaft (Y=19.5) and nozzle shaft (Y=30.5),
    // meshing both.  Offset 11 mm → idler pitch R ≈ 5.5 meshing two R5.5 gears.
    idler_y = (CDIST + NOZZLE_SHAFT_Y) / 2;   // 25.0
    color([0, 0.7, 0, 0.85]) gear_blank(0, idler_y, 6.5);
    color("darkgreen")       pitch_circle(0, idler_y, 5.5);
}

// Pivot marker.
color("black") difference() { circle(1.6); circle(1.0); }

// Outer-edge radius call-out ring (shows where Pinion A's tip reaches).
color([1, 0, 0, 0.5]) ring(CDIST + PINION_TR, 0.4);
