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
// License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
// =============================================================================

// ── 64 mm constants — declared BEFORE the include ───────────────────────────
include <nacelle_64_scale.scad>
T64_AXIS_SHIFT  = P64_AXIS_SHIFT_S;     // = 34 x P64_K - 34 (9.61 mm at x1.06; was 7.14)
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

// Ring gear: option A (owner 2026-10-03) — m0.8, 50T/14T, face 5.0 -> 10.5 mm
// for Lewis FOS 4.1 under the CFD bounding crossflow (tools/
// nacelle_tilt_dynamics.py; nacelle_tip_gear_variants.scad VARIANT 1).  The
// band keeps its wing-side edge at part z 12.5 (same distance to the pad as
// before) and grows toward the spar tip.  The wing's 14T pinion widens to match.
GEAR_FACE       = 10.5;
GEAR_Z0         = 12.5 - GEAR_FACE;        // = 2.0

// ── Drive-shaft relief (option 1, owner 2026-10-03; WBS NAC-64-TILT-03) ─────
// The wing-fixed Ø4 drive shaft sits 25.6 mm off the tilt axis at azimuth
// 3.8 deg (part frame: x = aft, y = up), measured on the wing mesh.  Going to
// hover the nacelle turns -theta about the span axis, so in THIS frame the
// shaft moves +theta: over the -5..140 deg tilt range it sweeps -1.2..143.8
// deg, and it crosses the flange (r 23.1-28.1).  The flange therefore carries
// an arc slot over SLOT_A0..SLOT_A1 (6 deg margin each end), and the three
// M3 bolts move into the solid 205-deg remainder.
// Wing shaft relative to the spar at the tip, Rev T6 (2026-10-03): both
// bores are LEVEL on their fuselage datums (wings_s1223_revo.scad spar_bore /
// tilt_shaft_bore), so the shaft is 25.6 mm aft (station 53.6 - 28.0) and
// 2.2391 mm above (shaft_y 11.0797 - spar 8.8406) the tilt axis everywhere.
// Centre distance therefore 25.698 (was 25.6 at the old sloped-bore tip):
// +0.098 mm, ~0.07 mm extra backlash, closed out by the AK7455 loop.
SHAFT_DY        = 25.6;    // [mm] shaft aft of the spar
SHAFT_DZ        = 2.2391;  // [mm] shaft above the spar
SHAFT_R         = sqrt(SHAFT_DY * SHAFT_DY + SHAFT_DZ * SHAFT_DZ);  // 25.698
SHAFT_AZ        = atan2(SHAFT_DZ, SHAFT_DY);  // [deg] 5.00 at cruise
SLOT_A0         = SHAFT_AZ - 5.0 - 6.0;     // = -6.0 deg
SLOT_A1         = SHAFT_AZ + 140.0 + 6.0;   // = 151.0 deg
SLOT_HALF_W     = 2.0 + 0.8;                // shaft radius + 0.8 running gap
BOLT_ANGLES     = [175, 255, 335];          // [deg] outside the slot

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
    // 3 x M3 clearance through the flange plate, clear of the shaft slot
    for (a = BOLT_ANGLES)
        rotate([0, 0, a])
            translate([BOLT_CIRCLE_D / 2, 0, FLANGE_Z - 0.01])
                cylinder(d = BOLT_CLEAR_D, h = FLANGE_T + 0.02);
    // drive-shaft arc slot through flange + magnet carrier (see above)
    shaft_arc(FLANGE_Z - 0.01, FLANGE_T + 1.02, SLOT_HALF_W);
}

LIP_T = 1.0;   // [mm] flange-base layer between bearings and magnet

// Annular sector about the part z axis: radius SHAFT_R +/- half_w, azimuth
// SLOT_A0..SLOT_A1, from z0 for height h, with round ends (the shaft's own
// section at each end of its travel).
module shaft_arc(z0, h, half_w) {
    translate([0, 0, z0]) rotate([0, 0, SLOT_A0]) {
        rotate_extrude(angle = SLOT_A1 - SLOT_A0, $fn = 180)
            translate([SHAFT_R - half_w, 0]) square([2 * half_w, h]);
        for (a = [0, SLOT_A1 - SLOT_A0])
            rotate([0, 0, a]) translate([SHAFT_R, 0, 0])
                cylinder(r = half_w, h = h, $fn = 32);
    }
}

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
for (a = BOLT_ANGLES)
    assert(a > SLOT_A1 + 8 && a < SLOT_A0 + 360 - 8,
           "a flange bolt sits inside the drive-shaft slot");
assert(LIP_D / 2 < BRG_OD / 2 - 1.0,
       "flange base gives the outer race under 1 mm of shoulder");

if (is_undef(T64_NO_RENDER)) nacelle_trunnion();
