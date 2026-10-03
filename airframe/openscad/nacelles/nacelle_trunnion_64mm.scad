// =============================================================================
// nacelle_trunnion_64mm.scad — tilt trunnion for the 64 mm QX nacelle
// =============================================================================
// Includes nacelle_trunnion.scad and overrides its parameters (the same
// include-and-override pattern, and ORDERING RULE, as nacelle_pod_64mm_tandem:
// overrides may use literals and the T64_* constants declared above the
// include only).
//
// WHY (WBS NAC-64-TILT-01; tools/nacelle_tilt_dynamics.py)
// --------------------------------------------------------
// On the 64 mm nacelle, 2 x 6704-ZZ in the 8.0 mm stack reach fs = C0/P0 =
// 0.94 at ultimate (thrust x2, longer arm, gyroscopic and momentum-drag
// couples) — BELOW JTEKT's minimum of 1.0 for an oscillating bearing with
// impact load (CAT. B2001E Table 5-10, REF-BRG-003).  Owner decision
// 2026-10-03: lengthen the spar stub and thicken the pylon-side joint so the
// pair can be 2 x 6804-ZZ (20 x 32 x 7, C0 2.45 kN, REF-BRG-002).
//
// STACK (part-local z from the spar tip, toward the wing; mm)
//     0.0 – 14.0   2 x 6804-ZZ, Ø32 H7 seat (bearing centres 7.0 apart)
//    14.0 – 15.0   FLANGE BASE: one solid printed disc, Ø25 bore to Ø54.  It
//                  is at once the outer-race shoulder (the positive stop
//                  AGENTS.md requires), the magnet-seat floor, and the joint
//                  between the bearing barrel and the bolted flange.  This
//                  1 mm is why the extension is 7.0 mm, not 6.0.
//    15.0 – 17.0   ring magnet (unchanged part, ID26 / OD41.2 / 2.0 thick),
//                  seated in the flange, OUTSIDE the collar
//    17.0 – 18.2   pilot spigot (0.3 mm off the pad); air gap 1.5 unchanged
//   Flange face (seats on the collar rim) at z 14.0; flange plate 14.0-16.5.
//
// WHY NOT THE 50 mm LAYOUT (finding, 2026-10-03): in nacelle_trunnion.scad the
// magnet seat (z 8-10, r 12.9-20.7) starts 1 mm before the flange face and
// removes every printed path between the bearing barrel (r <= 17) and the
// flange (r >= 20.7); a mesh slice at z 8.5 shows only a 0.9 mm ring inside
// the magnet bore, not touching the barrel.  The barrel-to-flange load path
// there runs THROUGH THE BONDED MAGNET.  Its 2.5 mm flange plate also reaches
// the wing pad face (z 11.5) with no running clearance.  Recorded in WBS
// NAC-64-TILT-01; not repaired in the superseded 50 mm part.
//   Ring gear (50T m0.8, unchanged) moved +7.0 in part z so it sits at the
//   SAME distance from the wing tip pad as before: the wing's 14T pinion and
//   drive shaft do not move.  Register Ø38 / flange Ø54 / bolt circle Ø45.5
//   grow to clear the Ø32 seat with the repo's 2.5 mm minimum wall.
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CEH (Stab-Rabbit-coding) —
// owner decision above.  Design and file by Claude (Claude Opus 5.5,
// Anthropic) under the author's direction, per AGENTS.md AI attribution.
// Derivative of nacelle_trunnion.scad (Rev T4), which carries the upstream
// attribution chain.  References: [REF-BRG-002] JTEKT 6804-ZZ;
// [REF-BRG-003] JTEKT CAT. B2001E §5-5-3.
// License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
// =============================================================================

// ── 64 mm constants — declared BEFORE the include ───────────────────────────
T64_AXIS_SHIFT  = 34.0 * 1.21 - 34.0;   // = 7.14 mm, radial-scale axis shift
T64_STUB_EXTRA  = 7.0;    // [mm] spar stub / joint extension (owner 2026-10-03)

include <nacelle_trunnion.scad>

TRUNNION_AUTORENDER = false;

// Joint stations in the 64 mm nacelle frame.  The spar tip stays sleeve-
// bounded (0.84 mm to the Ø69 stator-sleeve OD); every WING feature moves
// outboard by the extension as well.
TRUNNION_X0     = 28.2 + T64_AXIS_SHIFT;                    // = 35.34
WING_TIP_FACE_X = 41.7 + T64_AXIS_SHIFT + T64_STUB_EXTRA;   // = 55.84

// Bearings: 2 x 6804-ZZ [REF-BRG-002].
BRG_OD          = 32.0;
BRG_W           =  7.0;
BRG_SEAT_D      = 32.0;   // H7, printed; ream/scrape to fit
BRG_SHOULDER_D  = 28.0;   // outer-race abutment bore — VERIFY against the
                          // JTEKT 6804 abutment (Da) before printing

// Ring gear unchanged in size; shifted so it keeps its distance to the pad.
GEAR_Z0         = 0.5 + T64_STUB_EXTRA;    // = 7.5

// Register / flange scaled to the Ø32 seat (2.5 mm walls).
REG_D           = 38.0;   // collar register bore Ø38.1 in the pod wrapper
FLANGE_Z        = 14.0;   // flange face = top of the bearing stack
LIP_D           = 25.0;   // flange-base bore over the inner races — VERIFY
                          // against the JTEKT 6804 inner-ring shoulder (d1)
FLANGE_D        = 54.0;
BOLT_CIRCLE_D   = 45.5;   // Ø3.5 insert: 2.0 mm wall to the register, 2.5 to
                          // the flange rim

// ── Body and cuts (replace the 50 mm modules; see WHY NOT above) ────────────
module trunnion_body() {
    union() {
        cylinder(d = BRG_SEAT_D + 2 * WALL_T, h = FLANGE_Z);        // barrel
        translate([0, 0, GEAR_Z0]) linear_extrude(GEAR_FACE) ring_gear_2d();
        translate([0, 0, REG_Z0])                                   // register
            cylinder(d = REG_D, h = FLANGE_Z - REG_Z0);
        translate([0, 0, FLANGE_Z]) cylinder(d = FLANGE_D, h = FLANGE_T);
        translate([0, 0, FLANGE_Z])                                 // carrier
            cylinder(d = MAG_OD + 2 * WALL_T, h = MAGNET_FACE_Z - FLANGE_Z);
        translate([0, 0, FLANGE_Z])                                 // pilot
            cylinder(d = PILOT_OD, h = PILOT_Z - FLANGE_Z);
    }
}

module trunnion_cuts() {
    // bearing seat, 2 x 6804 (open at the spar-tip end for assembly)
    translate([0, 0, -0.01]) cylinder(d = BRG_SEAT_D, h = BRG_SEAT_L + 0.01);
    // flange-base bore over the inner races
    translate([0, 0, BRG_SEAT_L - 0.01])
        cylinder(d = LIP_D, h = LIP_T + 0.02);
    // spar clearance through the pilot
    translate([0, 0, BRG_SEAT_L + LIP_T - 0.01])
        cylinder(d = SPAR_CLEAR_D, h = PILOT_Z - BRG_SEAT_L - LIP_T + 0.02);
    // ring-magnet seat, floor = top of the flange base, open toward the pad
    translate([0, 0, MAGNET_FACE_Z - MAG_T])
        difference() {
            cylinder(d = MAG_OD + MAG_FIT, h = MAG_T + 0.01);
            translate([0, 0, -0.01])
                cylinder(d = MAG_ID - MAG_FIT, h = MAG_T + 0.03);
        }
    // 3 x M3 clearance through the flange plate
    for (i = [0 : N_BOLTS - 1])
        rotate([0, 0, i * 360 / N_BOLTS])
            translate([BOLT_CIRCLE_D / 2, 0, FLANGE_Z - 0.01])
                cylinder(d = BOLT_CLEAR_D, h = FLANGE_T + 0.02);
}

LIP_T = 1.0;   // [mm] flange-base layer between bearings and magnet

// ── Parse-time checks ────────────────────────────────────────────────────────
assert(abs(MAGNET_FACE_Z - MAG_T - (BRG_SEAT_L + LIP_T)) < 1e-9,
       "magnet floor is not the flange base directly behind the bearings");
assert(FLANGE_Z == BRG_SEAT_L, "flange face must sit on top of the bearing stack");
assert(FLANGE_Z + FLANGE_T < PAD_FACE_X - TRUNNION_X0 - PILOT_CLEAR,
       "flange plate reaches the wing pad face (no running clearance)");
assert(BOLT_CIRCLE_D / 2 - 3.5 / 2 > (MAG_OD + MAG_FIT) / 2,
       "flange bolt holes cut into the magnet seat");
assert(BOLT_CIRCLE_D / 2 - 3.5 / 2 - REG_D / 2 >= 2.0 - 1e-9,
       "collar insert wall to the register below 2.0 mm");
assert(GEAR_RF - BRG_OD / 2 >= 2.5,
       "ring-gear rim over the bearing seat below the 2.5 mm minimum wall");
assert(LIP_D / 2 < BRG_OD / 2 - 1.0,
       "flange base gives the outer race under 1 mm of shoulder");

nacelle_trunnion();
