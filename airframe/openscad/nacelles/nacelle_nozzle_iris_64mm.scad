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
// author chain).  License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
// =============================================================================

include <nacelle_nozzle_iris.scad>
NSV_NO_RENDER = true;
use <nacelle_nozzle_servo_64mm.scad>   // rod clearance in the ring frame

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

// ── Servo drive interface (owner 2026-10-04, WBS NAC-64-SERVO-01) ─────────────
// Lever ear moved to the 292.5 deg flap gap (starboard; port = mirror, 247.5),
// 22.5 deg off top-centre under the canonical dorsal spine where the pod's
// bellcrank rod arrives (tools/nozzle_servo_linkage_64.py).  Stops, window and
// spring anchor all derive from RING_LEVER_AZ; the anchor stays opposite.
RING_LEVER_AZ    = 292.5;
SPRING_ANCHOR_AZ = 112.5;
// Forward lip deleted: the housing window then runs out through the front
// face, i.e. a FORWARD-OPEN NOTCH, so the nozzle slides aft off the pod's rod
// with no linkage part handled (field nozzle swap).  The lip also collided
// with the pod forward of the joint (joint census 2026-10-04).
HOUSING_LIP_H    = 0.0;
IRIS_NO_RENDER   = true;     // this file renders its own (modified) parts

// ── Field-swap retention (2026-10-04): 2 captive M3 screws at the top ─────────
// Two bosses on the housing OD under the pod's fixed spine extension, at
// az 302 / 316 (stbd), each with a radial M3 x 4 heat-set insert; the screws are
// captive in the spine.  A 3 mm throat spigot locates radially in the pod's
// sleeve bore (the stage-2 cartridge ends 3 mm short for it) and two key lugs
// in the pod's 30/150 key slots locate in rotation.
NZ64_BOSS_AZ  = [302, 316];   // both beside the notch (265..296), clear of the bellcrank path
NZ64_BOSS_R1  = 45.6;  NZ64_BOSS_W = 7.0;  NZ64_BOSS_Z = [1.0, 9.0];
NZ64_INSERT_D = 3.5;   NZ64_INSERT_L = 4.0;
NZ64_SPIGOT_L = 3.0;
NZ64_KEY_AZ   = [30, 150];  NZ64_KEY_W = 3.0;  NZ64_KEY_H = 3.0;
NZ_SIDE       = 1;        // +1 starboard, -1 port (mirror)
NZ_PART       = "asm";    // "throat" | "ring" | "flap" | "flap_seal" | "asm"

module nz64_throat() {
    difference() {
        union() {
            nozzle_throat_and_housing();
            // throat spigot into the pod sleeve bore
            translate([0, 0, -NZ64_SPIGOT_L]) difference() {
                cylinder(r = THROAT_OUTER_R, h = NZ64_SPIGOT_L + 0.01, $fn = 120);
                translate([0, 0, -0.1]) cylinder(r = BORE_R, h = NZ64_SPIGOT_L + 0.3, $fn = 120);
            }
            for (a = NZ64_KEY_AZ) rotate([0, 0, a])
                translate([THROAT_OUTER_R - 0.3, -NZ64_KEY_W / 2, -NZ64_SPIGOT_L])
                    cube([NZ64_KEY_H + 0.3, NZ64_KEY_W, NZ64_SPIGOT_L + 0.01]);
            for (a = NZ64_BOSS_AZ)
                nz_wedge(a - NZ64_BOSS_W / 2 / HOUSING_OUTER_R * 180 / PI,
                         a + NZ64_BOSS_W / 2 / HOUSING_OUTER_R * 180 / PI,
                         HOUSING_OUTER_R - 0.2, NZ64_BOSS_R1, NZ64_BOSS_Z[0], NZ64_BOSS_Z[1]);
        }
        // notch extension for the bellcrank output arm's tip (pod linkage),
        // forward-open like the window; starts at r 40.65 so the open-stop lug
        // (r 40.3..40.6) survives
        nz_wedge(243.0, 264.5, HOUSING_INNER_R + 0.05, HOUSING_OUTER_R + 1.2, -0.1, 10.0);
        for (a = NZ64_BOSS_AZ) rotate([0, 0, a])
            translate([NZ64_BOSS_R1 - NZ64_INSERT_L, 0, (NZ64_BOSS_Z[0] + NZ64_BOSS_Z[1]) / 2])
                rotate([0, 90, 0]) cylinder(d = NZ64_INSERT_D, h = NZ64_INSERT_L + 0.1, $fn = 20);
    }
}

// Unison ring: the 50 mm ring with the ball cup ALSO open axially forward, so
// the pod's rod ball leaves the cup when the nozzle slides aft and re-enters on
// refit (ring at its spring-open stop, servo at its open position).  The KTD3
// radial exit channel (fail-open) is kept unchanged.
module nz64_ring() {
    difference() {
        unison_ring();
        rotate([0, 0, RING_LEVER_AZ])
            translate([RING_LEVER_R - (RING_BALL_D + 0.4) / 2, -(RING_BALL_D + 0.4) / 2, -0.1])
                cube([RING_BALL_D + 0.4, RING_BALL_D + 0.4, RING_H / 2 + 0.1]);
        // rod-body clearance over the stroke (pod linkage, single-sourced)
        nsv_rod_clearance_ring_frame();
    }
}

module nz64_asm() {
    nz64_throat();
    nz64_ring();
    for (i = [0 : N_FLAPS - 1]) rotate([0, 0, i * 360 / N_FLAPS])
        translate([R_HINGE, 0, HINGE_Z]) rotate([0, -FLAP_PHI, 0])
            nozzle_flap(seal = (i % 2) == 1);
}

mirror([NZ_SIDE < 0 ? 1 : 0, 0, 0]) {
    if (NZ_PART == "throat") nz64_throat();
    else if (NZ_PART == "ring") nz64_ring();
    else if (NZ_PART == "flap") nozzle_flap(seal = false);
    else if (NZ_PART == "flap_seal") nozzle_flap(seal = true);
    else nz64_asm();
}

assert(HOUSING_OUTER_R < 87.12 / 2, "housing must fit the 64 mm pod pocket");
assert(abs(asin((R_HINGE - NOZZLE_CLOSED_R) / FLAP_LENGTH) - 16.96) < 0.05,
       "closed flap angle must match the validated 50 mm value");
echo(NZ64 = [R_HINGE, PHI_CLOSED, PHI_OPEN, RING_OUTER_R, HOUSING_OUTER_R, RING_LEVER_AZ]);
