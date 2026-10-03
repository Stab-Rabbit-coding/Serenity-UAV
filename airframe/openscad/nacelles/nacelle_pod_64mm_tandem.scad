// =============================================================================
// nacelle_pod_64mm_tandem.scad — Serenity nacelle pod, QX-Motor 64 mm tandem
// =============================================================================
// Plan: docs/plans/2026-09-28-001-feat-nacelle-nozzle-servo-drive-plan.md, U9.
// WBS:  airframe/wings-nacelles/WBS.md §1.1.4 NAC-64-SERVO-01, NAC-64-FIT-01/02.
//
// HOW THIS FILE WORKS
// -------------------
// It includes the 50 mm pod and overrides parameters.  OpenSCAD 2021.01 uses
// the LAST assignment of a variable for the whole file scope, and the last
// definition of a module, so every derived expression and every module in the
// 50 mm pod sees the 64 mm values.  The 50 mm pod renders unchanged on its own
// (RADIAL_K = 1, POD_AUTORENDER = true there).  One source of geometry, two
// parameter sets — no forked copy of the 1,700-line pod to drift.
//
// ORDERING RULE: an overriding assignment is evaluated at the position of the
// variable's FIRST assignment in the 50 mm file.  So an override may only use
// literals and the P64_* constants, which are declared above the include and
// therefore exist before anything in the 50 mm file.
//
// OWNER DECISIONS APPLIED (Steve Griffing, GitHub Stab-Rabbit-coding)
// -------------------------------------------------------------------
//   2026-10-01  KTD8: radial-only scale about the thrust axis; aircraft scale
//               and nacelle axial length unchanged.  KTD9: 64 mm flow tube,
//               QF2822 mounts on 4 x M3 / 16 mm bolt circle.  Printed nacelle
//               tube is the rotor flow boundary; the QX shroud is discarded.
//   2026-10-03  Axial-fit adjudication: STATOR FRONT PLATE IS THE MOTOR MOUNT
//               (no separate spider) and the intake bell is trimmed 8.0 mm.
//               tools/nacelle_axial_fit.py ADOPTED case, margin +0.3 mm on
//               drawing values — VERIFY by measurement (NAC-64-FIT-02).
//   2026-10-03  Radial scale = 64/50 = 1.28, proportional (silhouette held).
//   2026-10-03  Wing interface held: the wing tip face, spar stub, trunnion and
//               pylon-side wall stay where they are relative to the nacelle's
//               INBOARD face; the nacelle axis moves outboard by AXIS_SHIFT_X.
//
// ADOPTED AXIAL STACK (nacelle-local Z, mm; QF2822 drawing 8-4.jpg, VERIFY)
// -------------------------------------------------------------------------
//     0.0 – 19.5   intake bell (was 27.5; trimmed 8.0)
//    19.5 – 30.2   rotor 1 hub (10.7 shaft protrusion) — runs in the pod bore
//    31.2 – 34.2   stator-1 front plate = motor-1 mount  } stator sleeve
//    34.2 – 92.2   motor 1 body (58.0) inside stator-1 hub } 31.2 – 92.7
//    93.2 – 103.9  rotor 2 hub                            } aft sleeve
//   104.9 – 107.9  stator-2 front plate = motor-2 mount   } 92.7 – 166.25
//   107.9 – 165.9  motor 2 body                           }
//   166.25 –       nozzle ring pocket (unchanged station)
//
// NOT YET RE-DERIVED IN THIS FILE — each is an open WBS item, not an omission:
//   • edf_stator_sleeve.scad / edf_aft_spider_sleeve.scad — the stator-as-
//     mount sleeves themselves (this file only cuts the bores they slide into).
//   • nacelle_nozzle_iris.scad at 64 mm (plan U11) — NOZZLE_RING_OD below is a
//     proportional placeholder for the pocket only.
//   • PIVOT_Z — unchanged 107.5 pending tools/nacelle_mass_cg.py (plan U5).
//   • ESC cooling discharge ports (ESC_BLEED_Z) now open onto the stator
//     sleeve wall, not the duct; the sleeve needs matching ports (plan U9/U10).
//   • nacelle_esc_cover.scad still builds from the unscaled skin grid.
//   • Hull-frame bake (tools/bake_hull_frame.py) for AXIS_SHIFT_X.
//
// Render (stbd shown; port = all three -1):
//   openscad -o nacelle_stbd_64mm.stl nacelle_pod_64mm_tandem.scad \
//            -D SWIRL_DIR=1 -D PYLON_SIDE=1 -D NACELLE_SIDE=1
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CEH (Stab-Rabbit-coding) —
// owner decisions above.  Parameter derivation and file by Claude (Claude
// Opus 5.5, Anthropic) under the author's direction, per AGENTS.md AI
// attribution.  Derivative of nacelle_pod_50mm_tandem.scad, which carries the
// full upstream attribution chain (canonical shell: REF-CAD-001/REF-CAD-003).
// References: [REF-EDF-003] QX-Motor 64 mm EDF manual and QF2822 drawing, user-supplied
// images docs/references/qx-motor 64mm edf/ (requires verification, plan U7).
// License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
// =============================================================================

// ── 64 mm constants — declared BEFORE the include (see ORDERING RULE) ──────
P64_K           = 64.0 / 50.0;  // [-] = 1.28 proportional radial scale (owner)
P64_BORE_R      = 32.0;   // [mm] 64 mm (2.52 in) nominal flow diameter.  The
                          //      rotor running clearance is NOT this number —
                          //      measure the bare rotor (NAC-64-FIT-02).
P64_WALL        =  2.5;   // [mm] duct wall = the 50 mm pod's WALL_T
P64_FACE_PYLON  = 34.0 * P64_K;          // = 43.52 mm pylon face |X|
P64_AXIS_SHIFT  = P64_FACE_PYLON - 34.0; // = 9.52 mm (0.37 in) per side
P64_BELL_L      = 27.5 - 8.0;  // [mm] = 19.5, owner-approved 8.0 mm trim
P64_BODY        = 58.0;   // [mm] QF2822 rear cap to mount face, 8-4.jpg — VERIFY
P64_SHAFT       = 10.7;   // [mm] 68.7 − 58.0 shaft protrusion — VERIFY
P64_GAP         =  1.0;   // [mm] running / interstage gap
P64_PLATE       =  3.0;   // [mm] stator front plate (motor mount) thickness
P64_STAGE       = P64_SHAFT + P64_GAP + P64_PLATE + P64_BODY;   // = 72.7 mm

include <nacelle_pod_50mm_tandem.scad>

POD_AUTORENDER = false;    // render the 64 mm pod below, not the 50 mm one

// ── Radial scale (owner, 2026-10-03) ─────────────────────────────────────────
RADIAL_K        = P64_K;   // [-] applied to the measured shell grids

// ── Flow tube (KTD9) ────────────────────────────────────────────────────────
EDF_BORE_R      = P64_BORE_R;              // = 32.0 mm
EDF_CASING_R    = P64_BORE_R + P64_WALL;   // = 34.5 mm; printed tube is the duct

// ── Outer envelope (reference values, scaled with the shell) ─────────────────
NACELLE_OD_X    = 75.4 * P64_K;   // = 96.5 mm (3.80 in)
NACELLE_OD_Y    = 83.3 * P64_K;   // = 106.6 mm (4.20 in)
NACELLE_FACE_X_PYLON = P64_FACE_PYLON;    // = 43.52 mm
NACELLE_FACE_X_FAR   = 38.0 * P64_K;      // = 48.64 mm

// ── Wing interface hold (owner, 2026-10-03) ──────────────────────────────────
// Every |X| from the nacelle axis to a WING-side feature grows by the distance
// the pylon face moved outboard, so the wing tip, spar stub, trunnion and the
// pylon-side wall keep their positions relative to that face.
TRUNNION_X0     = 28.2 + P64_AXIS_SHIFT;   // = 37.72 mm
WING_TIP_FACE_X = 41.7 + P64_AXIS_SHIFT;   // = 51.22 mm
COLLAR_FAIR_X   = 22.0 + P64_AXIS_SHIFT;   // = 31.52 mm
CAVITY_TRUNNION_X0 = 20.0 + P64_AXIS_SHIFT;
CAVITY_TRUNNION_X1 = 40.0 + P64_AXIS_SHIFT;

// ── Adopted axial stack (see header table) ───────────────────────────────────
INLET_BELL_L    = P64_BELL_L;          // = 19.5 mm
INLET_BELL_FLARE= 3.0 * P64_K;
EDF1_Z_ENTRY    = P64_BELL_L;                               // = 19.5 rotor-1 hub
EDF1_Z_EXIT     = P64_BELL_L + P64_STAGE;                   // = 92.2 motor-1 tail
EDF2_Z_ENTRY    = P64_BELL_L + P64_STAGE + P64_GAP;         // = 93.2 rotor-2 hub
EDF2_Z_EXIT     = P64_BELL_L + 2 * P64_STAGE + P64_GAP;     // = 165.9 motor-2 tail
STATOR_Z_BOT    = P64_BELL_L + P64_SHAFT + P64_GAP;         // = 31.2 plate
STATOR_Z_TOP    = P64_BELL_L + P64_STAGE;                   // = 92.2

// Sleeve zones: the stator-1 sleeve starts at its front plate, so the pod's
// integral bore carries only rotor 1; rotor 2 runs inside the aft sleeve.
STATOR_SLV_Z_START = P64_BELL_L + P64_SHAFT + P64_GAP;          // = 31.2
STATOR_SLV_Z_END   = P64_BELL_L + P64_STAGE + P64_GAP / 2;      // = 92.7
AFT_SLV_Z_START    = P64_BELL_L + P64_STAGE + P64_GAP / 2;      // = 92.7
// AFT_SLV_Z_END stays NOZZLE_RING_Z (166.25), unchanged station.

// ── Motor mounts (KTD9 / R13) ────────────────────────────────────────────────
MOTOR_BOLT_R    =  8.0;   // [mm] QF2822 4 x M3 on ø16.00 (8-4.jpg) — VERIFY
R_HUB           = 15.0;   // [mm] stator hub outer radius over the ø27.8 can
                          //      (13.9 mm) + 1.1 mm — sleeve parts, VERIFY
SLEEVE_BOSS_R   = 28.0 * P64_K;   // = 35.84 mm, on the nozzle pocket face

// ── Nozzle pocket — PLACEHOLDER until plan U11 re-sizes the iris ─────────────
NOZZLE_RING_OD  = 72.0 * P64_K;   // = 92.16 mm

// ── Intake fairing, scaled with the shell it blends into ─────────────────────
INTAKE_BLEND_R_PEAK = 38.2 * P64_K;   // = 48.9 mm
INTAKE_BLEND_R_END  = 27.0 * P64_K;   // = 34.56 mm, buried in the duct wall

// ── Cavity, ESC seat ─────────────────────────────────────────────────────────
CAVITY_VENT_R   = 30.0 * P64_K;   // = 38.4 mm, inside the scaled annulus
ESC_MOUNT_R     = P64_BORE_R + P64_WALL + 0.2 + P64_WALL;   // = 37.2 mm
                  // = SLEEVE_BORE_R + CAVITY_DUCT_WALL (pod assert ties them)

// ── Module overrides ─────────────────────────────────────────────────────────

// No pod-integrated spider: the stator-1 front plate carries motor 1
// (owner adjudication 2026-10-03).
module edf1_nacelle_spider() {}

// The 50 mm keep-out ran from the bay's forward end to the Z 90 bore step and
// assumed the bay sat forward of the sleeve zone.  Here the whole bay is over
// the sleeve zone, so the keep-out spans the bay, and its inner bound tracks
// the larger duct (EDF_BORE_R + 1 instead of the literal 26.0).
module esc_bay_seat_keepout() {
    for (az_hinge = ESC_BAY_AZ)
        for (side = [0, 1])
            esc_panel_slab(
                (side == 0 ? ESC_W_POWER : ESC_W_SIGNAL) + 2 * (ESC_FIT + 2.0),
                az_hinge + (side == 0 ? esc_a_pow() : -esc_a_sig()),
                EDF_BORE_R + 1.0, ESC_MOUNT_R + 2.0,
                ESC_BAY_Z0 - 1.0, ESC_BAY_Z1 + 1.0);
}

// ── Parse-time checks specific to the 64 mm stack ────────────────────────────
assert(EDF2_Z_EXIT <= NOZZLE_RING_Z,
       "motor-2 tail enters the nozzle pocket — axial fit gate (R11) fails");
assert(MOTOR_BOLT_R + M3_CLEAR_D / 2 < R_HUB,
       "QF2822 bolt circle does not land on the stator hub");
assert(abs(NACELLE_FACE_X_PYLON - TRUNNION_X0 - (34.0 - 28.2)) < 1e-9,
       "pylon-face-to-trunnion distance changed — wing interface not held");

nacelle_pod(swirl_dir = SWIRL_DIR);
