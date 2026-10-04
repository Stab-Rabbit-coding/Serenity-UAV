// =============================================================================
// nacelle_pod_64mm_tandem.scad — Serenity nacelle pod, QX-Motor 64 mm tandem
// =============================================================================
// Plan: docs/plans/2026-09-28-001-feat-nacelle-nozzle-servo-drive-plan.md, U9.
// WBS:  airframe/wings-nacelles/WBS.md §1.1.4 NAC-64-SERVO-01, NAC-64-*.
// Record: docs/NACELLE_64MM_VERIFICATION.md.
//
// HOW THIS FILE WORKS
// -------------------
// It includes the 50 mm pod and overrides parameters.  OpenSCAD 2021.01 uses
// the LAST assignment of a variable for the whole file scope, and the last
// definition of a module, so every derived expression and every module in the
// 50 mm pod sees the 64 mm values.  The 50 mm pod renders unchanged on its own
// (RADIAL_K = AXIAL_K = 1, POD_AUTORENDER = true there).  One source of
// geometry, two parameter sets — no forked copy of the pod to drift.
//
// ORDERING RULE: an overriding assignment is evaluated at the position of the
// variable's FIRST assignment in the 50 mm file.  So an override may only use
// literals and the P64_* constants, which are declared above the include and
// therefore exist before anything in the 50 mm file.
//
// OWNER DECISIONS APPLIED (Steve Griffing, GitHub Stab-Rabbit-coding)
// -------------------------------------------------------------------
//   2026-10-01  KTD9: 64 mm flow tube, QF2822 mounts on 4 x M3 / 16 mm bolt
//               circle.  Printed nacelle tube is the rotor flow boundary.
//   2026-10-03  STATOR FRONT PLATE IS THE MOTOR MOUNT (no separate spider).
//   2026-10-03  Wing interface held at the pylon face: wing tip, spar stub and
//               trunnion keep their positions relative to the INBOARD face;
//               the nacelle axis moves outboard by P64_AXIS_SHIFT.
//   2026-10-03  Pivot trunnion re-sited to the rotating-assembly CG.
//   2026-10-03  PROPORTIONS (supersedes the 1.28 radial / fixed-185.2 choice):
//               "minimum radial scale, lengthen to canon at that diameter,
//               optimised for aerodynamics, thrust, weight and canonical
//               shape."  tools/nacelle_64_proportion_trade.py pick: radial
//               1.21 (packaging minimum: pylon wall >= 41 mm, ESC-bay skin),
//               canonical axial stretch 1.13 -> L 209.3 mm.  Canon L/D
//               [REF-CAD-003 Sheets 3/4] 2.24 plan / 2.31 side; this pod
//               2.29 / 2.08 (was 1.92 / 1.74 at 1.28 x 185.2).
//   2026-10-03  INTAKE: a proper rounded lip (owner: "implement the rounded
//               intake bell as a proper aerodynamic design").  See below.
//   2026-10-03  80 A Open-Secure-ESC builds (WBS NAC-64-ESC-80A) — bay fit open until a part
//               is selected.
//   2026-10-03  Trunnion bearings 2 x 6704-ZZ -> 2 x 6804-ZZ: spar stub +7.0 mm
//               (20.5), joint collar +7.0 mm off the pylon face (WBS
//               NAC-64-TILT-01, nacelle_trunnion_64mm.scad).
//
// INTAKE LIP — two quarter-ellipses meeting at the highlight
// ----------------------------------------------------------
//   internal  2:1 ellipse, P64_LIP_A x P64_LIP_F = 16.0 x 8.0 mm, from the
//             highlight (Z 0, r 40.0) to the 64 mm throat at Z 16.0.
//             Contraction ratio (40/32)^2 = 1.56.  Nose radius F^2/a = 4.0 mm.
//   external  ellipse P64_FORE_A x P64_FORE_B = 1.56 x 2.5 mm with the SAME
//             4.0 mm nose radius, to the ring radius 42.5 mm, held to Z 22,
//             then faired down inside the canonical shell by Z 40.
//   Both branches have a RADIAL tangent and equal curvature at the highlight:
//   the leading edge is a true round nose (no corner, no cusp, no knife edge).
//   SELECTED BY CFD (tools/nacelle_intake_cfd.py, real external forebody,
//   static/hover): of eight lip variants, "lipE" (this one) is the only one
//   with no reversed flow on lip, bell or duct AND <= 4.2 % total-pressure
//   loss at r/R 0.95 on the rotor face.  The cosine bell (sharp lip) lost the
//   outer 10 % of radius; a knife-edged outside separated; contraction ratio
//   1.27-1.45 left tip separation.  A straight 64 mm duct runs from Z 16 to
//   the rotor at Z 30.5, so the rotor runs in a constant bore (no tip-gap
//   growth).  The lip ring is hollowed behind a 6 mm solid nose and vented
//   into the pod cavity (lip_ring_cavity()).

// AXIAL STACK (nacelle-local Z, mm; QF2822 drawing 8-4.jpg, VERIFY)
// -----------------------------------------------------------------
//     0.0 – 13.0   elliptical lip (internal contour)
//    13.0 – 30.5   straight inlet duct, 64 mm
//    30.5 – 41.2   rotor 1 hub (10.7 shaft protrusion)
//    42.2 – 45.2   stator-1 front plate = motor-1 mount  } stator sleeve
//    45.2 – 103.2  motor 1 body (58.0) inside stator-1 hub } 42.2 – 103.7
//   104.2 – 114.9  rotor 2 hub                            } aft sleeve
//   115.9 – 118.9  stator-2 front plate = motor-2 mount   } 103.7 – 187.86
//   118.9 – 176.9  motor 2 body        (11.0 mm margin to the nozzle pocket)
//   187.86 –       nozzle ring pocket (166.25 x 1.13, rides on the shell)
//
// NOT YET RE-DERIVED IN THIS FILE — each is an open WBS item, not an omission:
//   • edf_stator_sleeve.scad / edf_aft_spider_sleeve.scad (NAC-64-GEOM-01).
//   • nacelle_nozzle_iris.scad at 64 mm (plan U11) — NOZZLE_RING_OD is a
//     proportional placeholder for the pocket only.
//   • ESC cooling ports onto the sleeve wall (NAC-64-GEOM-02) and the 80 A
//     board fit (NAC-64-ESC-80A).
//   • nacelle_esc_cover.scad still builds from the unscaled skin grid.
//   • Hull-frame bake (tools/bake_hull_frame.py) for P64_AXIS_SHIFT.
//
// Render (stbd shown; port = all three -1):
//   openscad -o nacelle_stbd_64mm.stl nacelle_pod_64mm_tandem.scad \
//            -D SWIRL_DIR=1 -D PYLON_SIDE=1 -D NACELLE_SIDE=1
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CEH (Stab-Rabbit-coding) —
// owner decisions above.  Parameter derivation, lip design and file by Claude
// (Claude Opus 5.5, Anthropic) under the author's direction, per AGENTS.md AI
// attribution.  Derivative of nacelle_pod_50mm_tandem.scad, which carries the
// full upstream attribution chain (canonical shell: REF-CAD-001/REF-CAD-003).
// References: [REF-EDF-003] QX-Motor 64 mm EDF manual and QF2822 drawing;
// [REF-CAD-003] QMx blueprint pack (canonical proportions).
// License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
// =============================================================================

// ── 64 mm constants — declared BEFORE the include (see ORDERING RULE) ──────
P64_K           = 1.21;   // [-] radial scale — packaging minimum (trade tool)
P64_A           = 1.13;   // [-] canonical axial stretch (trade tool, re-
                          //     calibrated on the rendered pod; 1.15 gave
                          //     11.0 mm hover clearance < the 12.7 mm floor)
P64_BORE_R      = 32.0;   // [mm] 64 mm (2.52 in) nominal flow diameter.  The
                          //      rotor running clearance is NOT this number —
                          //      measure the bare rotor (NAC-64-FIT-02).
P64_WALL        =  2.5;   // [mm] duct wall = the 50 mm pod's WALL_T
P64_FACE_PYLON  = 34.0 * P64_K;          // = 41.14 mm pylon face |X|
P64_AXIS_SHIFT  = P64_FACE_PYLON - 34.0; // = 7.14 mm (0.28 in) per side
// Trunnion bearing upgrade (owner 2026-10-03, WBS NAC-64-TILT-01): the spar
// stub is 7.0 mm longer and the joint stands 7.0 mm further off the pylon
// face, so the trunnion carries 2 x 6804-ZZ in a 15 mm stack.  See
// nacelle_trunnion_64mm.scad and wings_s1223_revo.scad SPAR_TIP_PROTRUSION_64N.
P64_STUB_EXTRA  = 7.0;

// Intake lip (header).
P64_LIP_A       = 16.0;   // [mm] internal ellipse, axial semi-axis (2:1)
P64_LIP_F       =  8.0;   // [mm] internal ellipse, radial semi-axis (flare)
                          //      CFD lip sweep winner "lipE" (header)
P64_HL_R        = P64_BORE_R + P64_LIP_F;   // = 40.0 mm highlight radius
P64_FORE_R      = 42.5;   // [mm] lip ring outer radius = the scaled skin's
                          //      LARGEST radius at its first measured station
                          //      (Z 24.1: 40.5-42.7 mm); ahead of Z 24 the
                          //      canonical dome is narrower, so the ring is the
                          //      exterior there (recorded deviation).
P64_FORE_B      = P64_FORE_R - P64_HL_R;    // = 2.5 mm external semi-axis
// External semi-axis chosen so the external nose curvature radius B^2/A equals
// the internal one F^2/a (= 4.0 mm): a TRUE round nose.  A knife-edged
// outside (B^2/A = 0.18 mm, first cut) separated in the hover CFD.
P64_FORE_A      = P64_FORE_B * P64_FORE_B / (P64_LIP_F * P64_LIP_F / P64_LIP_A);
                          // = 1.5625 mm
P64_RING_HOLD   = 22.0;   // [mm] ring holds P64_FORE_R to here, then buries
P64_FAIR_END    = 40.0;   // [mm] Z by which the fairing is buried in the skin
P64_RING_WALL   =  2.5;   // [mm] lip-ring skin (AGENTS.md §7 2.0 min; 2.5 matches
                          //      the pod's measured skin)
P64_RING_CAV_Z0 =  6.0;   // [mm] solid nose ahead of the ring cavity

// Stack.
P64_ROTOR_Z     = 30.5;   // [mm] rotor-1 hub forward face (trade tool pick)
P64_BODY        = 58.0;   // [mm] QF2822 rear cap to mount face, 8-4.jpg — VERIFY
P64_SHAFT       = 10.7;   // [mm] 68.7 − 58.0 shaft protrusion — VERIFY
P64_GAP         =  1.0;   // [mm] running / interstage gap
P64_PLATE       =  3.0;   // [mm] stator front plate (motor mount) thickness
P64_STAGE       = P64_SHAFT + P64_GAP + P64_PLATE + P64_BODY;   // = 72.7 mm

include <nacelle_pod_50mm_tandem.scad>
use <edf_motor_mount_64mm.scad>   // stage-1 stator (integrated) + lead channel

POD_AUTORENDER = false;    // render the 64 mm pod below, not the 50 mm one

// ── Shell scale ──────────────────────────────────────────────────────────────
RADIAL_K        = P64_K;
AXIAL_K         = P64_A;
NACELLE_L       = 185.2 * P64_A;   // = 209.28 mm (8.24 in)

// ── Flow tube (KTD9) ────────────────────────────────────────────────────────
EDF_BORE_R      = P64_BORE_R;              // = 32.0 mm
EDF_CASING_R    = P64_BORE_R + P64_WALL;   // = 34.5 mm; printed tube is the duct

// ── Outer envelope (reference values, scaled with the shell) ─────────────────
NACELLE_OD_X    = 75.4 * P64_K;   // = 91.2 mm (3.59 in)
NACELLE_OD_Y    = 83.3 * P64_K;   // = 100.8 mm (3.97 in)
NACELLE_FACE_X_PYLON = P64_FACE_PYLON;    // = 41.14 mm
NACELLE_FACE_X_FAR   = 38.0 * P64_K;      // = 45.98 mm

// ── Wing interface hold (owner, 2026-10-03) ──────────────────────────────────
TRUNNION_X0     = 28.2 + P64_AXIS_SHIFT;   // = 35.34 mm
WING_TIP_FACE_X = 41.7 + P64_AXIS_SHIFT + P64_STUB_EXTRA;   // = 55.84 mm
COLLAR_FAIR_X   = 22.0 + P64_AXIS_SHIFT;   // = 29.14 mm
CAVITY_TRUNNION_X0 = 20.0 + P64_AXIS_SHIFT;
CAVITY_TRUNNION_X1 = 40.0 + P64_AXIS_SHIFT + P64_STUB_EXTRA;
// Collar for the 6804 trunnion (mirrors nacelle_trunnion_64mm.scad): register
// bore Ø38.1 H7 from the trunnion's REG_Z0 (12.5) to its flange face (14.0);
// collar OD = trunnion flange OD 54; 3 x M3 on Ø45.5.  The register is a
// 1.5 mm pilot; the bolted, bonded flange reacts the moment (as at 50 mm).
TRUNNION_REG_D  = 38.1;
COLLAR_X0       = 28.2 + P64_AXIS_SHIFT + 12.5;   // = 47.84
COLLAR_X1       = 28.2 + P64_AXIS_SHIFT + 14.0;   // = 49.34
COLLAR_OD       = 54.0;
COLLAR_BOLT_D   = 45.5;
COLLAR_FAIR_D   = 70.0;

// ── Axial stack (header table) ───────────────────────────────────────────────
// INLET_BELL_L / _FLARE now describe the lip, for cavity_duct_wall().
INLET_BELL_L    = P64_LIP_A;
INLET_BELL_FLARE= P64_LIP_F;
EDF1_Z_ENTRY    = P64_ROTOR_Z;                               // = 30.5
EDF1_Z_EXIT     = P64_ROTOR_Z + P64_STAGE;                   // = 103.2
EDF2_Z_ENTRY    = P64_ROTOR_Z + P64_STAGE + P64_GAP;         // = 104.2
EDF2_Z_EXIT     = P64_ROTOR_Z + 2 * P64_STAGE + P64_GAP;     // = 176.9
STATOR_Z_BOT    = P64_ROTOR_Z + P64_SHAFT + P64_GAP;         // = 42.2
STATOR_Z_TOP    = P64_ROTOR_Z + P64_STAGE;                   // = 103.2
// Owner 2026-10-03: the forward motor mount/stator is ONE PIECE with the
// thrust tube, so the removable sleeve zone (and its bore step, key slots and
// cavity wall offset) starts at the stage-2 cartridge's forward face.
STATOR_SLV_Z_START = P64_ROTOR_Z + P64_STAGE + P64_GAP / 2;  // = 103.7
STATOR_SLV_Z_END   = P64_ROTOR_Z + P64_STAGE + P64_GAP / 2;  // = 103.7
AFT_SLV_Z_START    = P64_ROTOR_Z + P64_STAGE + P64_GAP / 2;  // = 103.7
NOZZLE_RING_Z   = 166.25 * P64_A;  // = 187.86, rides on the shell's aft end

// ── Shell-tied stations stretched with the shell ─────────────────────────────
// The two forward webs ride with the shell.  The two that bracket the ESC
// bays are tied to the BAYS, which keep a fixed board length: in the 50 mm
// pod they sat "just forward / just aft of the bays" (plan Rev T4c).  At
// 70 x 1.13 = 79.1 the third web landed on the bay doubler's forward edge
// (Z 78.35) and left open slivers in the render; it now sits 4 mm clear of
// the doubler band (ESC_BAY_Z0 - ESC_LEDGE_W - 4), the fourth 3.5 mm aft of it.
CAVITY_BULKHEAD_Z = [40.0 * P64_A, 62.0 * P64_A,
                     95.0 * P64_A - 21.0 - 8.0 - 4.0,     // = 74.35
                     95.0 * P64_A + 21.0 + 8.0 + 3.5];    // = 139.85
NAV_LIGHT_Z     = 70.0 * P64_A;    // = 79.1
BOSS_Z_LO       = 83.0 * P64_A;    // vestigial-boss cleanup, a shell feature
BOSS_Z_H        = 24.0 * P64_A;
// ESC bays keep their 42 mm board length, centred where the stretched shell
// puts the 50 mm bays' centre (95 x 1.13 = 107.35).  Cooling ports move with
// the bay by the same offset.
ESC_BAY_Z0      = 95.0 * P64_A - 21.0;   // = 86.35
ESC_BAY_Z1      = 95.0 * P64_A + 21.0;   // = 128.35
ESC_BLEED_Z     = [ for (z = [76.0, 80.0, 84.0, 88.0]) z + 95.0 * (P64_A - 1) ];

// ── Motor mounts (KTD9 / R13) ────────────────────────────────────────────────
MOTOR_BOLT_R    =  8.0;   // [mm] QF2822 4 x M3 on ø16.00 (8-4.jpg) — VERIFY
R_HUB           = 15.0;   // [mm] stator hub outer radius over the ø27.8 can
SLEEVE_BOSS_R   = 28.0 * P64_K;   // = 33.88 mm, on the nozzle pocket face

// ── Nozzle pocket — PLACEHOLDER until plan U11 re-sizes the iris ─────────────
NOZZLE_RING_OD  = 72.0 * P64_K;   // = 87.12 mm

// ── Cavity, ESC seat ─────────────────────────────────────────────────────────
CAVITY_VENT_R   = 30.0 * P64_K;   // = 36.3 mm
ESC_MOUNT_R     = P64_BORE_R + P64_WALL + 0.2 + P64_WALL;   // = 37.2 mm
                  // = SLEEVE_BORE_R + CAVITY_DUCT_WALL (pod assert ties them)

// ── Tilt pivot = rotating-assembly CG (plan 003 KTD7; owner 2026-10-03) ─────
// tools/nacelle_mass_cg_64.py is the authority; iterate to <= 0.25 mm.
PIVOT_Z         = 109.7;  // iteration 2 (iteration 1: 109.1 -> measured 109.72)

// ── 10 AWG disconnect bay — between the stretched Z 40 and Z 62 bulkheads,
// clear of the trunnion ring-gear cavity (ø42.6 about PIVOT_Z).
ESC_DISC_Z      = 51.0 * P64_A;         // = 57.63
ESC_DISC_Z_LO   = 40.0 * P64_A + 1.5;   // = 46.7
ESC_DISC_Z_HI   = 62.0 * P64_A - 1.5;   // = 68.56

// ── Module overrides ─────────────────────────────────────────────────────────

// No pod-integrated spider: the stator-1 front plate carries motor 1.
// Stage-1 motor mount + stator, INTEGRAL with the thrust tube (owner
// 2026-10-03; edf_motor_mount_64mm.scad stator_stage(1): QF2822 plate at
// Z 42.2, 11 free-vortex cambered vanes, hollow lead vane at the ESC-1 bay
// azimuth).  Zone C, so no cavity cut removes it.
module edf1_nacelle_spider() {
    $mm_side = PYLON_SIDE;  $mm_swirl = SWIRL_DIR;
    stator_stage(1);
}
// The 50 mm motor-lead exit slot sat at STATOR_SLV_Z_START; at 103.7 it would
// open the duct at the rotor-2 tips.  The lead vanes replace it.
module esc_wire_exit_slot(pylon_side = PYLON_SIDE) {}
// The 50 mm sleeve-retention bosses reached r 30.4 at 64 mm — inside the bore
// and the nozzle throat (joint census 2026-10-03).  The nozzle is the aft lock.
module sleeve_retention_bosses() {}

// ESC seat keep-out spans the bay (the whole bay is over the sleeve zone) and
// tracks the larger duct (EDF_BORE_R + 1 instead of the 50 mm literal 26.0).
module esc_bay_seat_keepout() {
    for (az_hinge = ESC_BAY_AZ)
        for (side = [0, 1])
            esc_panel_slab(
                (side == 0 ? ESC_W_POWER : ESC_W_SIGNAL) + 2 * (ESC_FIT + 2.0),
                az_hinge + (side == 0 ? esc_a_pow() : -esc_a_sig()),
                EDF_BORE_R + 1.0, ESC_MOUNT_R + 2.0,
                ESC_BAY_Z0 - 1.0, ESC_BAY_Z1 + 1.0);
}

// ── Intake lip profile functions (header) ────────────────────────────────────
// Internal: r = R + F (1 - sqrt(1 - (1 - z/a)^2)),  0 <= z <= a.
function lip_r_in(z) =
    let(u = 1 - z / P64_LIP_A)
    P64_BORE_R + P64_LIP_F * (1 - sqrt(max(0, 1 - u * u)));
// External: r = R_hl + B sqrt(1 - (1 - z/A)^2),  0 <= z <= A.
function lip_r_out(z) =
    let(u = 1 - z / P64_FORE_A)
    P64_HL_R + P64_FORE_B * sqrt(max(0, 1 - u * u));

LIP_N = 48;   // profile stations per branch

// SUBTRACTIVE — the internal lip contour (replaces the cosine bell cut).
// Overshoots 0.5 mm forward of Z 0 at the highlight radius so the front of the
// canonical shell's dome is cleanly removed inside the highlight.
module inlet_bellmouth() {
    rotate_extrude(angle = 360, convexity = 4)
        polygon(concat(
            [[0, -0.5], [P64_HL_R, -0.5]],
            [ for (i = [0 : LIP_N]) let(z = P64_LIP_A * i / LIP_N)
                  [lip_r_in(z), z] ],
            [[0, P64_LIP_A]]));
}

// ADDITIVE — the lip ring (replaces the circular intake fairing).
// Bounded in front by ONE smooth curve: the internal branch runs up to the
// highlight and the external branch continues from it with the same radial
// tangent and curvature.  Its inner side sits 0.05 mm inside the lip contour
// so the subtractive cut, not this solid, defines the flow surface (no
// coincident faces).  The ring holds P64_FORE_R to P64_RING_HOLD, then
// smooth-steps down inside the skin by P64_FAIR_END and buries in the duct wall.
module circular_intake_fairing() {
    r_end  = P64_BORE_R + 0.5;    // = 32.5, inside the 34.5 duct wall
    n_fall = 24;
    rotate_extrude(angle = 360, convexity = 4)
        polygon(concat(
            // internal branch, throat -> highlight (0.05 mm proud of the cut)
            [ for (i = [LIP_N : -1 : 0]) let(z = P64_LIP_A * i / LIP_N)
                  [lip_r_in(z) - 0.05, z] ],
            // external branch, highlight -> ring radius
            [ for (i = [1 : LIP_N]) let(z = P64_FORE_A * i / LIP_N)
                  [lip_r_out(z), z] ],
            // hold the ring radius, then smooth-step into the duct wall
            [[P64_FORE_R, P64_RING_HOLD]],
            [ for (i = [1 : n_fall]) let(
                  f = i / n_fall, s = f * f * (3 - 2 * f),
                  z = P64_RING_HOLD + (P64_FAIR_END - P64_RING_HOLD) * f)
                  [P64_FORE_R + (r_end - P64_FORE_R) * s, z] ],
            // back along the duct side to the throat
            [[P64_BORE_R - 0.5, P64_FAIR_END], [P64_BORE_R - 0.5, P64_LIP_A]]));
}

// SUBTRACTIVE (Zone B, via the 50 mm pod's extra_zone_b_cuts() hook) — the
// lip ring cavity.  Without it the ring is solid from the nose to the pod's
// measured cavity (which starts at Z 24.15), ~60 g of material forward of the
// pivot.  Walls: P64_RING_WALL to the lip flow surface and to the ring's outer
// surface; a solid nose ahead of P64_RING_CAV_Z0.  NOT a sealed void: four
// axial vent bores carry it aft into the pod cavity (the same rule as the
// pod's vented bulkheads — CF-PETG is hygroscopic and a sealed void cannot
// be drained or inspected).
module lip_ring_cavity() {
    z1 = P64_RING_HOLD - P64_RING_WALL;          // stay inside the held ring
    r_out = P64_FORE_R - P64_RING_WALL;          // = 40.0
    rotate_extrude(angle = 360, convexity = 4)
        polygon(concat(
            [ for (i = [0 : 16]) let(
                  z = P64_RING_CAV_Z0 + (z1 - P64_RING_CAV_Z0) * i / 16)
                  [(z < P64_LIP_A ? lip_r_in(z) : P64_BORE_R) + P64_RING_WALL, z] ],
            [[r_out, z1], [r_out, P64_RING_CAV_Z0]]));
    // vents into the pod cavity (which starts at Z 24.15, r 34.5-38+)
    for (i = [0 : 3])
        rotate([0, 0, 45 + 90 * i])
            translate([(P64_BORE_R + P64_RING_WALL + r_out) / 2, 0, z1 - 0.5])
                cylinder(d = 3.0, h = 30.0 * P64_A - z1, $fn = 24);
}

// ── Tilt drive: pinion + shaft relief, and the collar fasteners (option 1,
// owner 2026-10-03; WBS NAC-64-TILT-03) ──────────────────────────────────────
// Must stay in step with nacelle_trunnion_64mm.scad (SHAFT_R, SHAFT_AZ, slot
// angles, BOLT_ANGLES, gear band).  Geometry is built in the TRUNNION PART
// frame (z = tilt axis toward the wing from the spar tip, x = aft, y = up)
// and mapped to the pod by part_frame(): part z -> +X, part x -> +Z,
// part y -> -Y, origin (TRUNNION_X0, 0, PIVOT_Z).  Starboard / PYLON_SIDE +1.
// Wing shaft relative to the spar at the tip, Rev T6 (2026-10-03): both
// bores are LEVEL on their fuselage datums (wings_s1223_revo.scad spar_bore /
// tilt_shaft_bore), so the shaft is 25.6 mm aft (station 53.6 - 28.0) and
// 2.2391 mm above (shaft_y 11.0797 - spar 8.8406) the tilt axis everywhere.
// Centre distance therefore 25.698 (was 25.6 at the old sloped-bore tip):
// +0.098 mm, ~0.07 mm extra backlash, closed out by the AK7455 loop.
T_SHAFT_DY = 25.6;  T_SHAFT_DZ = 2.2391;
T_SHAFT_R = sqrt(T_SHAFT_DY * T_SHAFT_DY + T_SHAFT_DZ * T_SHAFT_DZ);  // 25.698
T_SHAFT_AZ = atan2(T_SHAFT_DZ, T_SHAFT_DY);                          // 5.00 deg
T_A0 = T_SHAFT_AZ - 5.0 - 6.0;  T_A1 = T_SHAFT_AZ + 140.0 + 6.0;  // -6.0..151.0
T_PIN_RA = 0.8 * 14 / 2 + 0.8;   // = 6.4 mm, 14T m0.8 tip radius
T_GEAR_Z = [2.0, 12.5];          // ring/pinion band, part z (option A face 10.5)
T_BOLTS = [175, 255, 335];

module part_frame() {
    multmatrix([[0, 0, PYLON_SIDE, PYLON_SIDE * TRUNNION_X0],
                [0, -1, 0, 0], [1, 0, 0, PIVOT_Z], [0, 0, 0, 1]]) children();
}
module t_sector(z0, h, half_w) {     // swept annular sector, round ends
    translate([0, 0, z0]) rotate([0, 0, T_A0]) {
        rotate_extrude(angle = T_A1 - T_A0, $fn = 180)
            translate([T_SHAFT_R - half_w, 0]) square([2 * half_w, h]);
        for (a = [0, T_A1 - T_A0]) rotate([0, 0, a])
            translate([T_SHAFT_R, 0, 0]) cylinder(r = half_w, h = h, $fn = 32);
    }
}
// SUBTRACTIVE — the swept volume of the wing-fixed pinion (tip radius + 0.8)
// over the gear band +/- 0.5, and of the Ø4 shaft (+0.8) from the band out
// past the wing tip face.  Opens into the joint gap; it is the pod-side half
// of the clearance the trunnion flange slot provides.
module tilt_drive_relief() {
    part_frame() {
        t_sector(T_GEAR_Z[0] - 0.5, T_GEAR_Z[1] - T_GEAR_Z[0] + 1.0,
                 T_PIN_RA + 0.8);
        t_sector(T_GEAR_Z[1] + 0.5 - 0.01,
                 WING_TIP_FACE_X - TRUNNION_X0 - T_GEAR_Z[1] + 1.0, 2.0 + 0.8);
    }
}

module extra_zone_b_cuts() {
    lip_ring_cavity(); tilt_drive_relief(); motor_lead_routes();
}

// Motor phase-lead routes (WBS NAC-64-SVC-01), PYLON_SIDE-mirrored with the
// lead vanes (edf_motor_mount_64mm.scad lead_az: 68 / 248 = ESC_BAY_AZ):
//  * stage 1: the integrated lead vane's channel, out through the duct wall,
//    then a Ø5 conduit at r 37.5 through the cavity bulkheads aft to the
//    ESC-1 bay (ESC_BAY_Z0 86.35).  Motor 1 comes out aft, so its leads are
//    drawn back through this path one bullet at a time.  The pour-foam core
//    (plan 2026-10-03-001) must keep this conduit open.
//  * stage 2: an axial lead-escape slot in the sleeve bore from the lead vane
//    (Z ~119) to the aft end, so the leads slide out with the cartridge; it
//    opens into the ESC-2 bay over the bay's Z range.
LEAD_CONDUIT_R = 37.5;  LEAD_CONDUIT_D = 5.0;
LEAD_SLOT_W2   = 5.0;   LEAD_SLOT_D2   = 4.8;
module motor_lead_routes() {
    $mm_side = PYLON_SIDE;  $mm_swirl = SWIRL_DIR;
    az1 = PYLON_SIDE * 68;  az2 = PYLON_SIDE * 248;
    lead_channel_stage(1, LEAD_CONDUIT_R + 1.0);
    rotate([0, 0, az1]) translate([LEAD_CONDUIT_R, 0, 46.0])
        cylinder(d = LEAD_CONDUIT_D, h = ESC_BAY_Z0 + 4.0 - 46.0, $fn = 24);
    rotate([0, 0, az2]) translate([SLEEVE_BORE_R - 0.01, -LEAD_SLOT_W2 / 2, 119.0])
        cube([LEAD_SLOT_D2, LEAD_SLOT_W2, NOZZLE_RING_Z - 119.0 + 1.0]);
}

// Override of the 50 mm trunnion_collar_cut(): identical register bore, gear
// cavity and nav port, but the 3 x M3 collar inserts are placed about the
// SPAR axis at the trunnion's BOLT_ANGLES.  The 50 mm module rotates them
// about the DUCT axis (rotate([0,0,i*120]) applied after translation), which
// puts two of the three on the wrong side of the pod — found 2026-10-03 by the
// in-context check (WBS NAC-64-TILT-03).
module trunnion_collar_cut() {
    sgn = PYLON_SIDE;
    translate([sgn * COLLAR_X0, 0, PIVOT_Z]) rotate([0, sgn * 90, 0])
        cylinder(d = TRUNNION_REG_D, h = (WING_TIP_FACE_X - COLLAR_X0) + 1);
    translate([sgn * TRUNNION_CAV_X0, 0, PIVOT_Z]) rotate([0, sgn * 90, 0])
        cylinder(d = TRUNNION_CAV_D, h = COLLAR_X0 - TRUNNION_CAV_X0 + 0.01);
    part_frame() for (a = T_BOLTS) rotate([0, 0, a])
        translate([COLLAR_BOLT_D / 2, 0,
                   COLLAR_X1 - TRUNNION_X0 - M3_INSERT_L - 0.01])
            cylinder(d = M3_INSERT_D, h = M3_INSERT_L + 0.02, $fn = 24);
    // Nav 3-core crossing port: the 50 mm module drills it at azimuth 0, which
    // is INSIDE the drive shaft's sweep — the shaft would cut the nav wire.
    // Moved to T_NAV_AZ, beside the wing's own nav conduit (measured on the
    // wing mesh: hull y 1.0, z 61.5 -> 189 deg, r 20.2 about the spar axis),
    // in the solid sector between the 175 and 255 deg bolts.
    part_frame() rotate([0, 0, T_NAV_AZ])
        translate([COLLAR_BOLT_D / 2, 0, COLLAR_FAIR_X - TRUNNION_X0 - 1])
            cylinder(d = NAV_WIRE_BORE + 1.6,
                     h = COLLAR_X1 - COLLAR_FAIR_X + 2.01, $fn = 16);
}
T_NAV_AZ = 210;   // [deg] part frame; 35 deg from the 175 bolt, 45 from 255

// ── Parse-time checks specific to the 64 mm pod ──────────────────────────────
assert(EDF2_Z_EXIT <= NOZZLE_RING_Z,
       "motor-2 tail enters the nozzle pocket — axial fit gate (R11) fails");
assert(EDF1_Z_ENTRY >= P64_LIP_A,
       "rotor 1 is inside the lip — it must run in the constant 64 mm bore");
assert(MOTOR_BOLT_R + M3_CLEAR_D / 2 < R_HUB,
       "QF2822 bolt circle does not land on the stator hub");
assert(abs(NACELLE_FACE_X_PYLON - TRUNNION_X0 - (34.0 - 28.2)) < 1e-9,
       "pylon-face-to-spar-tip distance changed — sleeve bound not held");
assert(abs(WING_TIP_FACE_X - TRUNNION_X0 - 20.5) < 1e-9,
       "spar stub != wings_s1223_revo.scad SPAR_TIP_PROTRUSION_64N (20.5 mm)");
assert(NACELLE_FACE_X_PYLON - EDF_BORE_R - WALL_T >= 6.5,
       "pylon wall too thin for the 6.0 mm disconnect pocket + 0.5 material");
assert(abs(PIVOT_Z - ESC_DISC_Z) > TRUNNION_CAV_D / 2 + ESC_DISC_H / 2,
       "10 AWG disconnect bay overlaps the trunnion ring-gear cavity");
assert(abs(lip_r_out(P64_FORE_A) - P64_FORE_R) < 1e-6
       && P64_FORE_R <= 42.7 && P64_RING_HOLD < P64_FAIR_END,
       "lip ring must not exceed the skin's largest first-station radius");
assert(abs(P64_FORE_B * P64_FORE_B / P64_FORE_A
           - P64_LIP_F * P64_LIP_F / P64_LIP_A) < 1e-9,
       "external and internal nose radii differ — the nose is not a true round");
assert(lip_r_in(P64_RING_CAV_Z0) + 2 * P64_RING_WALL < P64_FORE_R,
       "lip ring too thin for its cavity at the nose end");

if (is_undef(P64_NO_RENDER)) nacelle_pod(swirl_dir = SWIRL_DIR);
