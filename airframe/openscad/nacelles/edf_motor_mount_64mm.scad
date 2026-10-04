// =============================================================================
// edf_motor_mount_64mm.scad — 64 mm nacelle stator-as-mount cartridges
// =============================================================================
// WBS NAC-64-GEOM-01 (owner request 2026-10-03: "also build the motor mounts").
// REVISED 2026-10-03 (owner): "why isn't the forward motor mount/stator a
// single piece with the thrust tube?  I can install the rotor from the front
// and the motor from the rear.  The aft motor mount has to be removable from
// the rear."  So:
//
//   STAGE 1  INTEGRATED into the pod's thrust tube — nacelle_pod_64mm_tandem.scad
//            draws stator_stage(1) through its edf1_nacelle_spider() hook (Zone
//            C) and cuts lead_channel_stage(1).  Plate front at Z 42.2.  Rotor 1
//            on/off through the intake (exposes the plate screws); motor 1 in/out
//            AFT through the Ø64 bore once the stage-2 cartridge is out.  No
//            stage-1 cartridge, no double wall over Z 42..104 (-44.6 g).
//   STAGE 2  the one removable CARTRIDGE (this file's render, STAGE = 2):
//            Z 103.7 .. 187.86 in the pod's sleeve bore (SLEEVE_BORE_R 34.7,
//            keys 30/150/270, bore step at 103.7 = forward stop); rotor 2 runs
//            inside it (Z 104.2..114.9), motor-2 plate at Z 115.9; out AFT with
//            motor, rotor and leads (WBS NAC-64-SVC-01).
//
// The cartridge is the duct section itself (Ø64 bore, 2.5 mm wall, Ø69 OD); both
// stages carry:
//   * a FRONT MOTOR PLATE for the QX QF2822 (REF-EDF-003, 8-4.jpg: boss Ø20.00,
//     4 x M3 on Ø16.00, shaft Ø3.0, can Ø27.80; all VERIFY on a physical unit,
//     WBS NAC-64-FIT-02).  The motor hangs AFT of the plate; its boss face bears
//     on the plate's aft face; 4 x M3 countersunk screws (ISO 10642) enter from
//     the FRONT so a 2 mm hex key reaches them through the intake (stage 1) or
//     the cartridge's forward face (stage 2) after the rotor is off.  Flat heads
//     because the rotor hub runs only P64_GAP = 1.0 mm ahead of the plate.
//   * 11 cambered STATOR VANES (11 is coprime with the 12-blade rotor, the same
//     Tyler–Sofrin rule as edf_stator_sleeve.scad) that carry the plate from
//     the cartridge wall and straighten the rotor's swirl.
//   * one HOLLOW LEAD VANE replacing vane 0: the motor's three phase leads run
//     forward along the can (they CANNOT cross the duct behind motor 1 —
//     rotor 2 is 1.0 mm aft of its tail), enter the vane root, and leave
//     through the cartridge wall into the pod's axial lead-escape slot, along
//     which they slide when the cartridge is pulled.  Stage 1 exits at the ESC-1
//     bay azimuth, stage 2 at the ESC-2 bay azimuth.
//
// VANE AERODYNAMICS (first pass — CFD/bench to confirm, WBS):
//   Euler turbomachinery relation Q = mdot · r · V_theta for axial inflow, with
//   mdot = sqrt(T rho A) = 0.385 kg/s (tandem 37.6 N, the tilt tool's thrust
//   row), annulus axial velocity 120.4 m/s (hub r 13.9 .. tip 32.0), shaft
//   torque 0.227 N·m from 1265.4 W (REF-EDF-003 2400 KV row) x 0.85 motor
//   efficiency ASSUMED at 45 288 rpm (the tilt tool's 0.85 x KV x V rule,
//   ASSUMED): V_theta = 25.7 m/s at r_m = 22.95 mm -> 12.0 deg swirl at r_m.
//   Free vortex (V_theta ∝ 1/r): 18.2 deg at the hub, 8.7 deg at the tip.  The
//   vane surface is built point-by-point to that law (a linear_extrude twist —
//   as the 50 mm sleeve used — gives tan(alpha) ∝ r, the wrong radial trend),
//   with parabolic camber from the inlet angle at the LE to axial at the TE.
//
// RETENTION: the cartridge sits against the pod's bore step at Z 103.7 and is
// locked aft by the nozzle (nacelle_nozzle_iris_64mm.scad), whose throat bears
// on its aft face.  M3 heat-set inserts at r 34.9 in the key-rib aft faces are
// kept as the attachment for that aft lock (the 50 mm pod bosses, r 33.88, left
// 0.18 mm of wall to the bore and sat inside the throat; deleted at 64 mm).
// NOZZLE-TO-POD RETENTION IS AN OPEN JOINT ITEM (WBS): the pod skin ends at
// ~Z 187, so the housing has no pod material to screw into radially.
// Anti-rotation (EDF torque reaction) is the three keys.
//
// LEAD VANE CHANNEL is sized to draw a 4 mm bullet pin through, one lead at a
// time (motor 1 comes out aft, so its leads must withdraw through the vane).
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CEH (Stab-Rabbit-coding) —
// direction.  Model by Claude (Claude Opus 5.5, Anthropic), per AGENTS.md AI
// attribution.  Derivative of edf_stator_sleeve.scad / edf_aft_spider_sleeve.scad
// (key, insert and vane-count conventions).  License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0).
// =============================================================================

STAGE      = 2;      // the cartridge (stage 1 is integrated in the pod)
SWIRL_DIR  = +1;     // as the pod / 50 mm stator: +1 stbd, -1 port
PYLON_SIDE = +1;     // mirrors the lead-vane azimuth with the pod

// ── Pod interface (nacelle_pod_64mm_tandem.scad) ─────────────────────────────
BORE_R     = 32.0;               // P64_BORE_R
WALL       = 2.5;                // P64_WALL
OD_R       = BORE_R + WALL;      // 34.5 = EDF_CASING_R
KEY_W      = 3.0;  KEY_H = 3.0;  KEY_ROOT = 0.5;
KEY_ANGLES = [30, 150];          // SLEEVE_KEY_ANGLES (64 mm: 270 freed for the servo)
Z_FWD      = 42.2;               // STATOR_SLV_Z_START (bore step)
Z_JOINT    = 103.7;              // STATOR_SLV_Z_END = AFT_SLV_Z_START
Z_AFT      = 187.86;             // AFT_SLV_Z_END = NOZZLE_RING_Z
Z0         = Z_JOINT;   // cartridge (stage 2)
Z1         = Z_AFT;
L          = Z1 - Z0;

// ── Motor plate (QF2822, REF-EDF-003 — VERIFY) ───────────────────────────────
PLATE_T    = 3.0;                // P64_PLATE
// Plate front, NACELLE Z: stage 1 at 42.2 (pod), stage 2 at 115.9 (cartridge)
function plate_z_abs(stage) = stage == 1 ? Z_FWD : 115.9;
PLATE_R    = 15.0;               // > can r 13.90 + 0.4 running gap + 0.7
BOLT_R     = 8.0;                // Ø16.00 bolt circle
BOLT_ANG0  = 45;                 // bolt clocking (VERIFY against the motor)
SHAFT_CLR_D = 6.0;               // Ø3 shaft + bearing-boss clearance
M3_CLR_D   = 3.4;
M3_CSK_D   = 6.3;                // ISO 10642 M3 head Ø (max 6.72; seat 6.3+chamfer)

// ── Stator vanes ──────────────────────────────────────────────────────────────
N_VANES    = 11;
VANE_T     = 2.0;                // [mm] thickness
VANE_C     = 18.0;               // [mm] axial chord, from the plate front face
HUB_R      = 14.3;               // vane root (can r 13.9 + 0.4)
ALPHA_M    = 12.0;               // [deg] inlet swirl at R_M (see header)
R_M        = 22.95;              // [mm] mean radius of the annulus
NR = 8;  NZ = 10;                // surface grid

// ── Lead vane ─────────────────────────────────────────────────────────────────
LEAD_T      = 6.0;               // [mm] hollow vane thickness
LEAD_SLOT_T = 4.4;               // [mm] channel: passes a 4 mm bullet pin
// Lead-vane azimuth = its ESC bay hinge azimuth (pod ESC_BAY_AZ 68 / 248),
// mirrored with the pod.  $mm_side lets the pod pass its own PYLON_SIDE.
function mm_side()  = is_undef($mm_side) ? PYLON_SIDE : $mm_side;
function mm_swirl() = is_undef($mm_swirl) ? SWIRL_DIR : $mm_swirl;
function lead_az(stage) = mm_side() * (stage == 1 ? 68 : 248);
LEAD_EXIT_W = 8.6;               // [mm] wall exit, matches the pod slot

// ── Retention (stage 2 aft face) ──────────────────────────────────────────────
RET_R      = 34.9;               // [mm] screw / insert centre radius (1.15 mm to
                                 // the bore, 0.85 mm to the key face)
M3_INSERT_D = 3.5;  M3_INSERT_L = 6.0;

$fn = 96;

// θ(r, z) of the vane mean surface (radians, signed by SWIRL_DIR): free-vortex
// inlet angle tan(a) = tan(ALPHA_M)·R_M/r, parabolic camber to axial at the TE.
function k_tan()       = tan(ALPHA_M) * R_M;
function theta(r, z)   = mm_swirl() * (k_tan() / (r * r)) * (z - z * z / (2 * VANE_C));
function vr(j, r0, r1) = r0 + (r1 - r0) * j / NR;
function vz(i)         = VANE_C * i / NZ;

// One vane as a closed polyhedron between the camber surface ± t/2 (arc).
module vane_solid(t, r0, r1) {
    pts = [ for (s = [-1, 1]) for (i = [0 : NZ]) for (j = [0 : NR])
              let(r = vr(j, r0, r1), z = vz(i),
                  a = theta(r, z) * 180 / PI + s * (t / 2) / r * 180 / PI)
              [r * cos(a), r * sin(a), z] ];
    W = NR + 1;  S = (NZ + 1) * W;
    function id(s, i, j) = s * S + i * W + j;
    faces = concat(
        [ for (i = [0 : NZ - 1]) for (j = [0 : NR - 1])        // side -1
            [id(0, i, j), id(0, i, j + 1), id(0, i + 1, j + 1), id(0, i + 1, j)] ],
        [ for (i = [0 : NZ - 1]) for (j = [0 : NR - 1])        // side +1
            [id(1, i, j), id(1, i + 1, j), id(1, i + 1, j + 1), id(1, i, j + 1)] ],
        [ for (i = [0 : NZ - 1])                                // root r0
            [id(0, i, 0), id(0, i + 1, 0), id(1, i + 1, 0), id(1, i, 0)] ],
        [ for (i = [0 : NZ - 1])                                // tip r1
            [id(0, i, NR), id(1, i, NR), id(1, i + 1, NR), id(0, i + 1, NR)] ],
        [ for (j = [0 : NR - 1])                                // LE z = 0
            [id(0, 0, j), id(1, 0, j), id(1, 0, j + 1), id(0, 0, j + 1)] ],
        [ for (j = [0 : NR - 1])                                // TE z = c
            [id(0, NZ, j), id(0, NZ, j + 1), id(1, NZ, j + 1), id(1, NZ, j)] ]);
    polyhedron(points = pts, faces = faces, convexity = 4);
}

module cartridge_tube() {
    difference() {
        union() {
            cylinder(r = OD_R, h = L);
            for (a = KEY_ANGLES) rotate([0, 0, a])
                translate([OD_R - KEY_ROOT, -KEY_W / 2, 0])
                    cube([KEY_H + KEY_ROOT, KEY_W, L]);
        }
        translate([0, 0, -1]) cylinder(r = BORE_R, h = L + 2);
    }
}

// Plate + vanes of a stage, in NACELLE Z (front face at plate_z_abs).
module motor_plate(stage) {
    translate([0, 0, plate_z_abs(stage)]) difference() {
        cylinder(r = PLATE_R, h = PLATE_T);
        translate([0, 0, -1]) cylinder(d = SHAFT_CLR_D, h = PLATE_T + 2, $fn = 32);
        for (k = [0 : 3]) rotate([0, 0, BOLT_ANG0 + 90 * k]) translate([BOLT_R, 0, 0]) {
            translate([0, 0, -1]) cylinder(d = M3_CLR_D, h = PLATE_T + 2, $fn = 20);
            // 90 deg countersink from the FRONT face (rotor side)
            translate([0, 0, -0.01])
                cylinder(d1 = M3_CSK_D, d2 = M3_CLR_D, h = (M3_CSK_D - M3_CLR_D) / 2, $fn = 24);
        }
    }
}

module vanes(stage) {
    translate([0, 0, plate_z_abs(stage)]) {
        for (k = [1 : N_VANES - 1])
            rotate([0, 0, lead_az(stage) + k * 360 / N_VANES])
                vane_solid(VANE_T, HUB_R, BORE_R + 0.6);
        rotate([0, 0, lead_az(stage)]) vane_solid(LEAD_T, HUB_R, BORE_R + 0.6);
    }
}

// Lead channel: the hollow vane's core, open at the root, out through the wall
// (to r_out).  Nacelle Z.
module lead_channel_stage(stage, r_out = OD_R + 1) {
    translate([0, 0, plate_z_abs(stage)]) rotate([0, 0, lead_az(stage)]) {
        intersection() {
            vane_solid(LEAD_SLOT_T, HUB_R - 1, r_out);
            translate([0, 0, PLATE_T + 1.0]) cylinder(r = r_out + 2, h = VANE_C - PLATE_T - 2.5);
        }
        translate([BORE_R - 0.5, -LEAD_EXIT_W / 2, PLATE_T + 1.0])
            cube([r_out - BORE_R + 0.5, LEAD_EXIT_W, VANE_C - PLATE_T - 2.5]);
    }
}

// Stator of a stage (plate + vanes, lead channel cut), nacelle Z.  Used by
// the pod for stage 1 and by the cartridge for stage 2.
module stator_stage(stage) {
    difference() {
        union() { motor_plate(stage); vanes(stage); }
        lead_channel_stage(stage);
    }
}

module retention_inserts() {
    if (STAGE == 2) for (a = KEY_ANGLES) rotate([0, 0, a])
        translate([RET_R, 0, L - M3_INSERT_L]) cylinder(d = M3_INSERT_D, h = M3_INSERT_L + 0.1, $fn = 20);
}

// The stage-2 cartridge, cartridge-local z (0 = its forward face, nacelle Z 103.7).
module edf_motor_mount_64mm() {
    difference() {
        union() {
            cartridge_tube();
            translate([0, 0, -Z0]) union() { motor_plate(2); vanes(2); }
        }
        translate([0, 0, -Z0]) lead_channel_stage(2);
        retention_inserts();
    }
}

assert(PLATE_R > 13.9 + 0.4, "plate must cover the can");
assert(BOLT_R + M3_CSK_D / 2 < PLATE_R, "countersinks must stay on the plate");
assert(RET_R - M3_INSERT_D / 2 > BORE_R + 1.0 && RET_R + M3_INSERT_D / 2 < OD_R + KEY_H - 0.8,
       "retention insert must sit inside the key rib");

if (is_undef(MM64_NO_RENDER)) edf_motor_mount_64mm();
