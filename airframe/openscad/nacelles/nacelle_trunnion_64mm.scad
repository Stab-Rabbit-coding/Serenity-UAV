// =============================================================================
// nacelle_trunnion_64mm.scad — tilt trunnion for the 64 mm QX nacelle
// =============================================================================
// FLATTENED at Rev U (2026-11-07) by tools/scad_flatten.py.  This file used to `include` the
// 50 mm trunnion (nacelle_trunnion.scad) and override its parameters; the overrides are now applied and the 50 mm base
// is archived (archives/rev-T-frozen.tar.gz).  Geometry is unchanged: the render was compared
// with the pre-flatten render and the symmetric difference is 0.0000 mm3.  The 64 mm values
// below are the values in effect; "[flattened]" comments mark where an override replaced a
// base value.  Edit THIS file; there is no longer a base to keep in sync.
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

// ---- begin include <nacelle_trunnion.scad> (inlined by scad_flatten.py) ----
// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  Primary-component STLs published to airframe/stls/ are
//   stored directly in hull frame, baked by tools/bake_hull_frame.py.
//   NEVER re-bake a mesh derived from an already-baked file.
//   This file:
//     PART-LOCAL PRINT FRAME.  The trunnion's own axis (= the tilt axis =
//     the fixed spar axis) is local +Z, with local Z = 0 at the OUTBOARD
//     (spar-tip) end and +Z running INBOARD toward the wing.  In the nacelle
//     frame that axis is nacelle-local X, so the mapping is
//         nacelle_X = PYLON_SIDE * (TRUNNION_X0 + local_z)
//     with TRUNNION_X0 = 26.7 mm.  Printing in this frame puts the ring-gear
//     teeth in the XY build plane, which is the whole reason the trunnion is
//     a separate part (see PRINT ORIENTATION below).
// ===========================================================================
// =============================================================================
// nacelle_trunnion.scad
// Serenity UAV — Rev T4 — Nacelle tilt trunnion (fixed-spar pivot)
// =============================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Analysis and drafting: Claude (Claude Opus 5, Anthropic) under the author's
//           direction, per AGENTS.md §3 "Attribution and Licensing"
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
// Date    : 2026-08-30
// Revision: Rev T4 (2026-08-30) — NEW PART
//
// Description
// -----------
// The nacelle-side half of the Rev T1 wing/nacelle tilt joint.  It replaces the
// Rev R2 "skewer": a rotating Ø8 mm steel spar that ran spanwise THROUGH the
// nacelle, breached both duct walls, and had to be carried across the airflow on
// a strut inside the stator sleeve.  Under Rev T1 the spar is a FIXED
// 20 × 16.3 mm carbon tube bonded into the wing which STOPS outside the duct
// (docs/WING_ATTACH_INTERFACE.md §4.3a), and the nacelle hangs off its stub on
// this part.
//
// It carries, on one axis, everything the joint needs on the nacelle side:
//   • the trunnion bearing pair that rides the spar stub        (WA-R7, WA-R12)
//   • the 50T tilt ring gear the wing's 14T pinion drives       (WA-R8)
//   • the diametric ring magnet the wing-mounted AK7455 reads   (WA-R9)
//   • a pilot spigot that sets the encoder air gap off the wing tip pad
//
// THE AXIAL BUDGET — and why the specified 2 × 6804 does NOT fit
// --------------------------------------------------------------
// This is `docs/WING_ATTACH_INTERFACE.md` OI-8, closed here.
//
// The spar stub is 15.0 mm long, bounded by the duct, running nacelle-local
// |X| 41.7 (wing tip face) → 26.7 (spar tip, ≥ 26.0 duct bound, §4.3a).  The
// interface document budgeted all 15.0 mm to bearings and concluded
// "2 × 6804 (20 × 32 × 7) = 14.0 mm fits".  It does not, because three further
// items were never subtracted from the same 15 mm:
//
//   wing tip pad face (TIP_PAD_PROUD 2.0 below the tip face)   |X| = 39.7
//   − pilot running clearance                                        0.3
//   − HALL_AIR_GAP (magnet face → IC face, wings_s1223_revo)          1.5
//   = magnet inboard face                                      |X| = 38.2
//   − ring-magnet thickness                                          2.5
//   = magnet outboard face                                     |X| = 35.7
//   → space left for the bearing stack: 35.7 − 26.7            =    9.0 mm
//
// 9.0 mm cannot hold 14.0 mm of bearing.  The pair is therefore 2 × 6704ZZ
// (20 × 27 × 4 = 8.0 mm), which fits with 1.0 mm in hand.  6704 is still a
//
//   *** THE "1.0 mm IN HAND" ABOVE IS STALE — THE BUILT MARGIN IS ZERO. ***
//   The budget above was derived at spar tip |X| 26.7 and a 2.5 mm magnet.
//   The 2026-08-31 corrections moved the spar tip to 28.2 (SLEEVE-bounded, not
//   duct-bounded) and thinned the magnet 2.5 → 2.0.  Recomputed at the values
//   this file actually builds:
//       pad face 39.7 − air gap 1.5 = magnet inboard face   |X| 38.2
//       − magnet 2.0                = magnet outboard face  |X| 36.2
//       − spar tip                                          |X| 28.2
//       = space for the bearing stack                          8.0 mm
//       bearing stack (2 × 6704ZZ)                             8.0 mm
//       MARGIN IN HAND                                        +0.0 mm
//   Every term in this budget is at a hard-won floor: the wing tip face and pad
//   proud are built wing geometry; the air gap and magnet thickness are
//   flux-coupled and push in OPPOSITE directions (AK7455 window 10–70 mT, and
//   WING_ATTACH_INTERFACE.md already calls flux re-validation "load-bearing,
//   not a formality"); the spar tip is sleeve-bounded with 0.70 mm to the
//   stator sleeve; and OI-8's own analysis makes the bearing-centre SPAN the
//   governing number, so dropping to a single bearing is not available.
//   DO NOT plan new axial content into this joint on the strength of the
//   "1.0 mm" figure — there is none.  Recovering space means spending one of
//   those floors deliberately (see WBS §1.1.3, nozzle sync-gear packaging).
// deep-groove ball bearing, so BOTH races take axial and radial load together —
// which is what WA-R12's attitude-dependent duty actually requires (plan 004
// RISK-4) and what a plain bushing in the inboard position would NOT have given.
//
// WHAT THE SHORT STACK COSTS, stated rather than hidden.  Nacelle thrust
// (21.9 N static, 32.8 N at the repo's ×1.5 ultimate) acts along the duct axis
// at |X| = 0, i.e. ~31 mm off the trunnion, so the joint carries a 1.02 N·m
// ultimate moment.  Over the 4.0 mm bearing-centre span that is 254 N per
// bearing — 28 % of a 6704's ~0.9 kN static rating, and 2.4 MPa on the printed
// Ø27 seat.  Both pass, but the SPAN, not the rating, is the governing number
// and it is a direct consequence of the duct bound.  Angular play from bearing
// internal clearance is ≈ 0.25°; the AK7455 reads the nacelle, not the
// actuator, so that play appears as measured angle rather than as error.
//
// PRINT ORIENTATION — why this is a separate part at all
// ------------------------------------------------------
// The trunnion axis is nacelle-local X, i.e. HORIZONTAL when the pod prints on
// its duct axis.  Printed integrally with the pod, the ring-gear teeth would be
// built as stacked overhanging layers and the Ø27 bearing seat would be a
// bridged horizontal bore — neither is dimensionally usable.  As its own part,
// printed axis-vertical, the teeth lie in the build plane (best achievable FDM
// tooth form, plan 004 RISK-3) and the bearing seat is a true vertical bore.
//
// RETENTION — positive, not friction
// ----------------------------------
// A flange face at local z = FLANGE_Z lands on the nacelle collar rim and is
// held by 3 × M3 SHCS into heat-set inserts in the collar (AGENTS.md forbids
// friction-fit-only retention).  The flange face — not the 3.5 mm register — is
// what reacts the thrust moment: 1.02 N·m over the Ø41.5 bolt circle is 24.6 N
// at the fasteners.  The register is a pilot, and the joint is additionally
// bonded (West System 105/206), as the spar socket is.
//
// NON-FERROUS REQUIREMENT
// -----------------------
// The whole part lies inside HALL_KEEPOUT_R = 10 mm of the AK7455 IC.  It is
// CF-PETG, which is non-ferromagnetic; the 3 M3 fasteners MUST be brass, A2/A4
// stainless is NOT acceptable here (docs/TILT_ENCODER_WIRING_EMI_SPEC.md §6.2,
// avionics/emi-hardening/WBS.md §1.4.6).  The bearings themselves ARE steel and
// ARE inside the keep-out; that is why the in-situ zero/INL calibration is
// mandatory and must be run with bearings, shaft and pinion installed
// (docs/TILT_DRIVE_CONTROL_SPEC.md §7.5).
//
// References
// ----------
//   [1] docs/WING_ATTACH_INTERFACE.md §4.2/§4.3a/§4.5, OI-8 — the joint spec.
//   [2] airframe/openscad/wings/wings_s1223_revo.scad — SPAR_TIP_PROTRUSION,
//       TIP_PAD_PROUD, HALL_RING_OD/ID, HALL_SENS_R, HALL_AIR_GAP (built side).
//   [3] docs/plans/2026-08-29-004-…-trunnion-pivot-tilt-drive-plan.md U2/U4.
//   [4] REFERENCES.md REF-MAT-002 (20 % CF-PETG allowables).
// =============================================================================


// =============================================================================
// ── Parameter Block ───────────────────────────────────────────────────────────
// =============================================================================

// ── Joint stations, expressed as nacelle-local |X| (see the budget above) ─────
// [flattened] TRUNNION_X0: value from its last assignment (override), kept at the first position
TRUNNION_X0     = 28.2 + T64_AXIS_SHIFT + P64_JOINT_SHIFT;   // [mm] outboard face = spar tip.  SLEEVE-BOUNDED,
                           //      not duct-bounded — corrected 2026-08-31.  The
                           //      pivot sits inside the Ø55.4 sleeve zone, where
                           //      the stator sleeve's OD is r 27.5, so the old
                           //      26.7 (taken against the Ø50 EDF bore) drove
                           //      23.3 mm³ of solid interference into
                           //      edf_stator_sleeve.stl.  28.2 leaves 0.70 mm.
// [flattened] WING_TIP_FACE_X: value from its last assignment (override), kept at the first position
WING_TIP_FACE_X = 41.7 + T64_AXIS_SHIFT + T64_STUB_EXTRA + P64_JOINT_SHIFT;   // [mm] wing tip face  (NACELLE_OD_X/2 + 4.0 joint gap)
PAD_PROUD       =   2.0;   // [mm] wing tip pad proud of that face (TIP_PAD_PROUD)
PILOT_CLEAR     =   0.3;   // [mm] running clearance, pilot spigot → pad face
AIR_GAP         =   1.5;   // [mm] magnet face → AK7455 IC face (HALL_AIR_GAP)

// ── Derived part-local stations (local z = |X| − TRUNNION_X0) ────────────────
PAD_FACE_X      = WING_TIP_FACE_X - PAD_PROUD;          // = 39.7
// The trailing values below were corrected 2026-09-10: they were still quoting
// results computed at the pre-2026-08-31 TRUNNION_X0 = 26.7 and were each
// 1.5 mm optimistic.  The expressions were always right; only the comments
// were stale.
PILOT_Z         = PAD_FACE_X - PILOT_CLEAR - TRUNNION_X0;   // = 11.2 (was 12.7)
MAGNET_FACE_Z   = PAD_FACE_X - AIR_GAP - TRUNNION_X0;       // = 10.0 (was 11.5)
TRUNNION_L      = PILOT_Z;                               // = 11.2 total length

// ── Spar / bearing ───────────────────────────────────────────────────────────
SPAR_OD         =  20.0;   // [mm] fixed CF spar OD (Rev T1)
SPAR_CLEAR_D    =  20.6;   // [mm] spar clearance bore through hub + pilot
// [flattened] BRG_OD: value from its last assignment (override), kept at the first position
BRG_OD          = 32.0;   // [mm] 6704ZZ outer diameter
// [flattened] BRG_W: value from its last assignment (override), kept at the first position
BRG_W           =  7.0;   // [mm] 6704ZZ width
BRG_N           =   2;     // [count] bearings in the stack
// [flattened] BRG_SEAT_D: value from its last assignment (override), kept at the first position
BRG_SEAT_D      = 32.0;   // [mm] H7 seat bore (printed; ream/scrape to fit)
BRG_SEAT_Z0     =   0.0;   // [mm] stack starts at the outboard face
BRG_SEAT_L      = BRG_N * BRG_W;          // = 8.0 mm
// [flattened] BRG_SHOULDER_D: value from its last assignment (override), kept at the first position
BRG_SHOULDER_D  = 28.0;   // [mm] shoulder bore inboard of the stack — locates
                           //      the outer races; 1.5 mm of race face bearing

// ── Tilt ring gear (WA-R8: 50T module 0.8, PD 40.0, meshes the wing 14T) ─────
GEAR_M          =   0.8;   // [mm] module — matches the wing pinion and the
                           //      fuselage 38T/38T stage (merge_cargo_interior)
GEAR_Z          =  50;     // [count] teeth
GEAR_PA         =  20.0;   // [deg] pressure angle
// [flattened] GEAR_FACE: value from its last assignment (override), kept at the first position
GEAR_FACE       = 10.5;   // [mm] face width = 6.25 × module (conventional
                           //      band 6–12 × m); tangential load is only
                           //      1.02/0.020 = 51 N ultimate, so face width is
                           //      set by the axial budget, not by tooth stress
// [flattened] GEAR_Z0: value from its last assignment (override), kept at the first position
GEAR_Z0         = 12.5 - GEAR_FACE;   // [mm] gear band start, part-local z
GEAR_PD         = GEAR_M * GEAR_Z;             // = 40.0 mm
GEAR_RA         = GEAR_PD / 2 + GEAR_M;        // = 20.8 mm tip radius
GEAR_RF         = GEAR_PD / 2 - 1.25 * GEAR_M; // = 19.0 mm root radius
GEAR_RB         = GEAR_PD / 2 * cos(GEAR_PA);  // = 18.794 mm base radius

// ── Register into the nacelle collar + bolted flange ─────────────────────────
// [flattened] REG_D: value from its last assignment (override), kept at the first position
REG_D           = 38.0;   // [mm] register OD (nacelle collar bore Ø34.0 H7)
REG_Z0          = GEAR_Z0 + GEAR_FACE;   // = 5.5, immediately inboard of the gear
// [flattened] FLANGE_Z: value from its last assignment (override), kept at the first position
FLANGE_Z        = 14.0;   // [mm] flange face, part-local z (= |X| 35.7)
// [flattened] FLANGE_D: value from its last assignment (override), kept at the first position
FLANGE_D        = 54.0;   // [mm] flange OD — also the nacelle collar OD
FLANGE_T        =   2.5;   // [mm] flange plate thickness (4 perimeters @ 0.6)
// [flattened] BOLT_CIRCLE_D: value from its last assignment (override), kept at the first position
BOLT_CIRCLE_D   = 45.5;   // [mm] 3 × M3, 120°: 2.0 mm of wall each side of a
                           //      Ø3.5 insert between the Ø33.9 register and
                           //      the Ø50 rim
BOLT_CLEAR_D    =   3.3;   // [mm] M3 clearance bore (M3_CLEAR_D)
N_BOLTS         =   3;

// ── Ring magnet seat (WA-R9; the wing side is BUILT to these) ────────────────
MAG_OD          =  41.2;   // [mm] HALL_RING_OD
MAG_ID          =  26.0;   // [mm] HALL_RING_ID (clears Ø20 spar + 3 mm collar)
MAG_T           =   2.0;   // [mm] magnet thickness.  2.5 -> 2.0 on 2026-08-31:
                           //      the stub lost 1.5 mm when the bound moved to
                           //      the sleeve, and the 0.5 mm has to come from
                           //      somewhere the wing has not already fixed.  The
                           //      air gap (1.5) and the pad proud (2.0) are built
                           //      wing geometry; the magnet is a stock part and
                           //      2.0 is a stock thickness.  FLUX CONSEQUENCE IS
                           //      REAL AND UNVERIFIED: a 20 % thinner magnet
                           //      weakens the field the AK7455 reads, and the
                           //      off-axis window is 10-70 mT.  The bench
                           //      validation the BOM row already demands is now
                           //      load-bearing, not a formality.
MAG_FIT         =   0.2;   // [mm] diametric bond-line clearance in the seat

// ── Pilot spigot (sets the air gap off the wing tip pad) ─────────────────────
PILOT_OD        =  25.6;   // [mm] must clear MAG_ID (26.0) and sit inside the
                           //      wing pad disc (TIP_PAD_R 14.0 → Ø28)
WALL_T          =   2.5;   // [mm] minimum wall — 4 perimeters at 0.6 mm

$fn = 96;


// =============================================================================
// ── Involute spur-gear profile ────────────────────────────────────────────────
// =============================================================================
// Standard 20° full-depth involute, generated from first principles rather than
// approximated by a trapezoid: the wing pinion is only 14T (the no-undercut
// floor), so a profile error here shows up directly as transmission error in
// the tilt loop.  inv(a) = tan a − a; OpenSCAD trigonometry is in DEGREES, so
// the "− a" term is converted explicitly.
function inv_rad(a)      = tan(a) - a * PI / 180;               // radians
function flank_angle(r)  = 90 / GEAR_Z
                         + (inv_rad(GEAR_PA) - inv_rad(acos(GEAR_RB / r)))
                           * 180 / PI;                          // degrees

// Sample radii from the root (or base, whichever is larger) out to the tip.
// GEAR_RF (19.000) > GEAR_RB (18.794) at 50T, so the flank is fully involute
// and no radial root extension is needed — asserted below.
GEAR_R_START = max(GEAR_RF, GEAR_RB);
GEAR_STEPS   = 10;
function gear_r(i) = GEAR_R_START
                   + (GEAR_RA - GEAR_R_START) * i / (GEAR_STEPS - 1);

// One tooth as a closed polygon, centred on angle 0.
function tooth_pts() = concat(
        [ for (i = [0 : GEAR_STEPS - 1])
              let (r = gear_r(i), a = -flank_angle(r))
                  [r * cos(a), r * sin(a)] ],
        [ for (i = [GEAR_STEPS - 1 : -1 : 0])
              let (r = gear_r(i), a =  flank_angle(r))
                  [r * cos(a), r * sin(a)] ]);

module ring_gear_2d() {
    union() {
        circle(r = GEAR_R_START + 0.01);       // root cylinder
        for (i = [0 : GEAR_Z - 1])
            rotate([0, 0, i * 360 / GEAR_Z]) polygon(tooth_pts());
    }
}


// =============================================================================
// ── Module: trunnion_body ─────────────────────────────────────────────────────
// =============================================================================
// The additive stack, outboard (z = 0) to inboard (z = TRUNNION_L).



// =============================================================================
// ── Module: trunnion_cuts ─────────────────────────────────────────────────────
// =============================================================================



// =============================================================================
// ── Module: nacelle_trunnion (main) ──────────────────────────────────────────
// =============================================================================
module nacelle_trunnion() {
    // Fail loudly rather than silently building an undercut gear.
    assert(GEAR_RF >= GEAR_RB,
           "ring gear: root radius below base radius — flank would be undercut");
    assert(TRUNNION_L <= WING_TIP_FACE_X - TRUNNION_X0,
           "trunnion overruns the duct-bounded spar stub");
    difference() {
        trunnion_body();
        trunnion_cuts();
    }
}

// Render hook (2026-10-03): nacelle_trunnion_64mm.scad includes this file and
// sets TRUNNION_AUTORENDER = false.  Identity for this part.
// [flattened] TRUNNION_AUTORENDER: value from its last assignment (override), kept at the first position
TRUNNION_AUTORENDER = false;
if (TRUNNION_AUTORENDER) nacelle_trunnion();


// =============================================================================
// ── Print specifications ──────────────────────────────────────────────────────
// =============================================================================
// Material    : CF-PETG (20 % CF) — non-ferromagnetic, REF-MAT-002
// Layer height: 0.12 mm (finer than the 0.15 mm airframe default: this part
//               carries a gear tooth form and two bearing seats)
// Walls       : 4 perimeters (2.5 mm at a 0.6 mm nozzle)
// Infill      : 60 % gyroid — higher than the 40 % airframe default; the part
//               is small and is the entire load path from nacelle to wing
// Nozzle      : hardened steel (CF-PETG)
// Orientation : OUTBOARD face (local Z = 0) DOWN on the plate.  Gear teeth then
//               lie in the build plane.  No supports: every overhang is either
//               a bore (bridged < 3 mm) or the flange underside, which is
//               supported by the register step.
// Quantity    : 2 (one per nacelle) — the part is HANDED ONLY by which nacelle
//               it bolts into; the geometry is identical, so print two.
//
// Post-print checks
// -----------------
//   1. Ø27.0 +0.00/−0.03 bearing seat over the full 8.0 mm; 6704 outer race
//      must press without cocking.  Ream/scrape — do NOT heat-fit.
//   2. Ø33.9 register: must slip into the nacelle collar Ø34.0 bore.
//   3. Flange face flat within 0.1 mm; it is the moment path.
//   4. Ring-gear span over 3 teeth vs. the wing pinion — roll the pair by hand
//      through the full 140° before bonding; no tight spot.
//   5. Ring-magnet seat Ø41.4 × 2.5 deep; magnet must sit FLUSH or 0–0.1 mm
//      proud of nothing — a recessed magnet grows HALL_AIR_GAP and the AK7455
//      off-axis flux window (10–70 mT) is gap-sensitive.
//   6. Verify with a magnet/steel probe that no ferrous fastener was fitted.
//
// Render command
// --------------
//   openscad -o nacelle_trunnion.stl nacelle_trunnion.scad
// ---- end include <nacelle_trunnion.scad> ----


// Joint stations in the 64 mm nacelle frame.  The spar tip stays sleeve-
// bounded (0.84 mm to the Ø69 stator-sleeve OD); every WING feature moves
// outboard by the extension as well.
                    // = 35.34
   // = 55.84

// Bearings: 2 x 6804-ZZ [REF-BRG-002].
   // H7, printed; ream/scrape to fit
   // outer-race abutment bore — VERIFY against the
                          // JTEKT 6804 abutment (Da) before printing

// Ring gear: option A (owner 2026-10-03) — m0.8, 50T/14T, face 5.0 -> 10.5 mm
// for Lewis FOS 4.1 under the CFD bounding crossflow (tools/
// nacelle_tilt_dynamics.py; nacelle_tip_gear_variants.scad VARIANT 1).  The
// band keeps its wing-side edge at part z 12.5 (same distance to the pad as
// before) and grows toward the spar tip.  The wing's 14T pinion widens to match.
        // = 2.0

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
   // collar register bore Ø38.1 in the pod wrapper
   // flange face = top of the bearing stack
LIP_D           = 25.0;   // flange-base bore over the inner races — VERIFY
                          // against the JTEKT 6804 inner-ring shoulder (d1)
   // Ø3.5 insert: 2.0 mm wall to the register, 2.5 to
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
