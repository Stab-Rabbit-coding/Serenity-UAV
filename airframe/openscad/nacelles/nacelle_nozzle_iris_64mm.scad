// =============================================================================
// nacelle_nozzle_iris_64mm.scad — spring-open servo iris nozzle, 64 mm (U11)
// =============================================================================
// Plan 2026-09-28-001 U11 / owner request 2026-10-03 ("build the 64mm nozzle
// with its servo activation").  Includes the 50 mm iris (nacelle_nozzle_iris
// .scad, Rev T3 shingled flaps, KTD3 open ball cup + spring cord + stops) and
// re-derives its RADIAL literals around the Ø64 bore.  OpenSCAD evaluates an
// override at the variable's FIRST assignment, so only LITERALS are set here;
// every derived quantity in the included file (THROAT_*, R_HINGE, PHI_*, TAB_*,
// spiral slot, ear / window azimuths) follows automatically.
//
// Re-derivation rules (each 50 mm offset preserved RELATIVE TO THE HINGE
// CIRCLE R_HINGE = BORE_R + THROAT_WALL, 27.5 -> 34.5 mm, so every proven
// clearance in the ring/flap/housing stack carries over unchanged):
//   exit radii      75 % / 105 % of BORE_R = 24.0 / 33.6 mm (plan U2/U11)
//   FLAP_LENGTH     30.0 -> 36.0: keeps the validated CLOSED flap angle,
//                   asin((34.5 - 24.0)/36.0) = 16.96 deg (50 mm: 16.96 deg);
//                   open angle asin(0.9/36) = 1.43 deg
//   pin radii       hinge + 1.5 / + 3.5 (29/31 -> 36/38): same 2.0 mm cam
//                   travel, so THETA_RING_REF_OPEN 23.75 deg stays valid
//   ring / lever /  hinge + 5.6 / + 4.5 / + 5.8 / + 4.6 / + 6.1 / + 8.1 / + 6.0
//   lug / groove /  (rim 40.1, ball cup 39.0, stop lug 40.3, groove 39.1,
//   housing         housing bore 40.6, OD 42.6, aft 40.5)
// Housing OD 85.2 sits in the 64 mm pod's NOZZLE_RING_OD 87.12 pocket with
// 0.96 mm radial clearance.  Ear tip 42.0 mm stays inside the pocket.
//
// RETENTION / SERVICE (WBS NAC-64-SVC-01, joint census 2026-10-03): the nozzle
// is the AFT LOCK of the motor-mount cartridge stack — the throat's forward
// face bears on edf_motor_mount_64mm.scad STAGE 2's aft face — and the housing
// is held in the pocket by 3 radial M3 screws through the pod skin into heat-
// set inserts in the housing lip (pod-side holes: nacelle_pod_64mm_tandem.scad
// nozzle_retention_holes()).  It is NOT bonded (the 50 mm lip was), so the
// nozzle comes off for cartridge service.  The 50 mm pod's sleeve-retention
// bosses are deleted at 64 mm: they reached r 30.4, inside the Ø64 bore and
// the throat liner.
//
// Forces, spring rate and servo margin are NOT scaled from 50 mm here — they
// come from tools/nozzle_servo_linkage.py with the bench load (plan U2/U8).
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CEH (Stab-Rabbit-coding) —
// direction.  Re-derivation by Claude (Claude Opus 5.5, Anthropic), per
// AGENTS.md AI attribution.  Derivative of nacelle_nozzle_iris.scad (same
// author chain).  License: CC BY 4.0.
// =============================================================================

include <nacelle_nozzle_iris.scad>

// ── Radial re-derivation (literals only — see header) ─────────────────────────
BORE_R             = 32.0;
NOZZLE_CLOSED_R    = 24.0;
NOZZLE_OPEN_R      = 33.6;
FLAP_LENGTH        = 36.0;
PIN_R_REF_CLOSED   = 36.0;
PIN_R_REF_OPEN     = 38.0;
RING_OUTER_R       = 40.1;
CAM_FLANGE_INNER_R = 35.5;
RING_LEVER_R       = 39.0;
STOP_LUG_R         = 40.3;
SPRING_GROOVE_R    = 39.1;
SPRING_ANCHOR_R0   = 40.3;
HOUSING_INNER_R    = 40.6;
HOUSING_OUTER_R    = 42.6;
HOUSING_AFT_R      = 40.5;

// ── 64 mm retention: radial screws into the housing lip ───────────────────────
NZ64_SCREW_AZ  = [60, 180, 300];   // clear of the ear window (129.5..161.8)
                                   // and the spring anchor (337.5)
NZ64_INSERT_D  = 3.5;  NZ64_INSERT_L = 4.0;   // M3 x 4 heat-set (lip is 2 mm
                                              // proud of the ring + 0.5 clr)
NZ64_SCREW_Z   = 1.5;              // [mm] axial station in the lip

assert(HOUSING_OUTER_R < 87.12 / 2, "housing must fit the 64 mm pod pocket");
assert(abs(asin((R_HINGE - NOZZLE_CLOSED_R) / FLAP_LENGTH) - 16.96) < 0.05,
       "closed flap angle must match the validated 50 mm value");
echo(NZ64 = [R_HINGE, PHI_CLOSED, PHI_OPEN, RING_OUTER_R, HOUSING_OUTER_R]);
