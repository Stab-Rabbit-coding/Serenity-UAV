// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See AGENTS.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  MODELLED DIRECTLY IN HULL FRAME.
// ===========================================================================
// ============================================================
// door_latch_mechanism.scad -- Rev A (2026-09-21)
// Cargo clamshell door drive + POSITIVE mechanical latch, cross-linked port
// to starboard.  Closes the DOOR-LATCH finding in docs/CARGO_DOOR_GATEWAY_
// SPEC.md (Rev A S8): "the doors have no positive in-flight latch; retention
// is servo gear-train friction, forbidden for a flight-critical joint by
// AGENTS.md S7."  See docs/CARGO_DOOR_LATCH_SPEC.md for the full statics
// package (governing load, FOS, all margins) -- this file is geometry only.
//
// >>> ENGINEERING REVIEW REQUIRED. Reference material, not a certified
// >>> design. See docs/CARGO_DOOR_LATCH_SPEC.md S0 for the full notice.
//
// WHY A POSITIVE LATCH, QUANTIFIED (not just "friction is bad practice"):
// the SG90's own stall torque (0.177 N.m, REF-ACT-003) is LESS than the
// door-opening moment from 14 CFR SS107.51(a)'s 87 kt regulatory ceiling
// (0.202 N.m at Cp=1.0, worst door) -- the gear train cannot hold the door
// shut at V_max even with zero safety factor.  A mechanical latch is
// therefore a hard requirement, not a best-practice nicety.
//
// MECHANISM (one per door, port shown; stbd is a mirror about X_CL):
//   door horn (rH=8mm) --pushrod(2mm steel wire, Z-bend)--> bell-crank
//   (rA=5mm drive arm) on a fixed pivot bracket bolted to the airframe near
//   the door's 2nd hinge knuckle (Y=39.33).  The SAME crank carries a LATCH
//   ARM (rB=10mm) ending in a hook.  At phi_door=0 (closed) the hook has
//   swung fully into a MORTISE cut into a fixed frame boss: the hook's foot
//   sits UNDER a 2.4mm overhanging LIP on the mortise's outboard face.  Any
//   door-opening moment tries to rotate the crank the SAME sense that would
//   drive the hook FURTHER under the lip -- the lip is a hard mechanical
//   stop, not a friction detent or an over-centre linkage; it stops the
//   crank (and, via the now-rigid pushrod, the door) regardless of servo
//   power state.  To open, the servo actively rotates the crank the OTHER
//   way (increasing phi), which is the same rotation that lifts the hook
//   back out from under the lip -- normal, unassisted operation, no
//   separate release actuator.
//
// CROSS-LINK -- deliberately NOT a rigid crank-to-crank rod.  Two SG90s
// commanded open-loop by PWM do not reach a given angle at the same instant
// (independent slew, docs/CARGO_DOOR_LATCH_SPEC.md S4); a RIGID link between
// their cranks would fight itself every time the two servos are even
// briefly out of step, loading the pushrods/pins far beyond the S3 sizing
// and risking exactly the kind of joint AGENTS.md SS7 forbids.  The
// cross-link is instead TWO independent things that need no extra rod:
//   (a) SOFTWARE -- one signed DOOR_COMMAND frame drives both doors'
//       positions together (docs/CARGO_DOOR_GATEWAY_SPEC.md S4);
//   (b) STRUCTURAL -- door_seam_interlock.scad cuts a tongue-and-groove
//       joint the full length of the two doors' mating (free) edges at
//       X_CL, so the doors physically key to EACH OTHER when both are
//       closed: each door's own bell-crank latch (above) is still what
//       resists its own opening moment, but the interlocked seam shares
//       some of that moment with the other, independently-latched door
//       instead of leaving a single failed latch fully unrestrained.
// See docs/CARGO_DOOR_LATCH_SPEC.md S4 for both, including why a rigid
// mechanical rod between the two servos was rejected.
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// AI note: Written by Claude (model: Claude Sonnet 5, Anthropic) under the
//   author's direction, 2026-09-21, per AGENTS.md SS3 AI attribution.
// License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
// ============================================================

include <cargo_layout_t5_params.scad>

$fn = 48;
EPS = 0.01;

// ---------------------------------------------------------------------------
// Door / hinge geometry (generate_cargo_doors.py: KNUCKLE_Y, hinge X/Z)
// ---------------------------------------------------------------------------
HINGE_X_PORT = -117.6;   HINGE_Z_PORT = 5.11;
HINGE_X_STBD = -222.5;   HINGE_Z_STBD = 5.22;
BRACKET_Y    = 39.33;    // 2nd hinge knuckle station -- clear of the aperture
                         // rim (Y=2) and the GW-CARGO-DOOR tray (Y<=-2)

// Pivot bracket stands PIVOT_H above the hinge Z, inboard of the hinge line
// by PIVOT_IN so the crank clears the door panel's swept arc.
PIVOT_H  = 14.0;
PIVOT_IN = 10.0;

// Crank arms (mm), all about the same pivot pin
ARM_DRIVE = 5.0;    // rA: to the door-horn pushrod (D-LATCH-1)
ARM_LATCH = 10.0;   // rB: to the hook (r_lip in the statics package)

// Angular layout (deg) of the two arms about the crank pivot, phi=0 = door
// fully closed.  DRIVE arm points toward the door horn at phi=0; LATCH arm
// points into the mortise.
ANG_DRIVE = 200.0;
ANG_LATCH = 20.0;

PIN_D = 3.0;  PIN_CL = 0.075;  PIN_BORE_R = PIN_D/2 + PIN_CL;

HOOK_L = 6.0;   HOOK_ROOT_W = 5.0;  HOOK_ROOT_T = 2.4;  // sized to FOS_shear ~3.0
HOOK_FOOT = 3.0;                                         // engagement depth under the lip
LIP_OVERHANG = 2.4;  LIP_PAD_W = 4.0;  LIP_PAD_T = 4.0;  // sized to FOS_bearing ~10
FILLET_R = 1.5;       // hook-root fillet -- reduces Kt; VERIFY by section/render

HORN_L = 8.0;  HORN_T = 3.0;  HORN_W = 6.0;

module pivot_boss(h = 8.0) {
    difference() {
        cylinder(h = h, d = 10.0);
        translate([0, 0, -1]) cylinder(h = h + 2, r = PIN_BORE_R);
    }
}

// One arm: a flat blade from the pivot out to the tip, with a small pad at
// the tip for the pushrod/hook/cross-rod feature.
module crank_arm(ang, len, w = 4.0, t = 3.0) {
    rotate([0, 0, ang])
        translate([0, -w / 2, 0])
            cube([len, w, t]);
}

module bell_crank() {
    union() {
        pivot_boss();
        crank_arm(ANG_DRIVE, ARM_DRIVE, 4.0, 5.0);
        // latch arm ends in the hook: an L-foot turned toward the lip's
        // engaged side (ANG_LATCH - 90, i.e. trailing the arm as phi
        // increases -- so INCREASING phi from 0 is the direction that lifts
        // the foot back out from under the lip, matching "opening = normal
        // servo rotation" above)
        union() {
            crank_arm(ANG_LATCH, ARM_LATCH, HOOK_ROOT_W, HOOK_ROOT_T);
            translate([ARM_LATCH * cos(ANG_LATCH), ARM_LATCH * sin(ANG_LATCH), 0])
                rotate([0, 0, ANG_LATCH])
                    translate([0, -HOOK_ROOT_W / 2, 0])
                        cube([HOOK_L, HOOK_ROOT_W, HOOK_ROOT_T]);
            translate([ARM_LATCH * cos(ANG_LATCH), ARM_LATCH * sin(ANG_LATCH), 0])
                rotate([0, 0, ANG_LATCH - 90])
                    translate([0, -HOOK_FOOT, 0])
                        cube([HOOK_ROOT_W, HOOK_FOOT + EPS, HOOK_ROOT_T]);
        }
        // NOTE: the hook-root fillet (FILLET_R) assumed in the Kt estimate
        // (docs/CARGO_DOOR_LATCH_SPEC.md) is NOT modelled here -- OpenSCAD
        // has no native fillet; apply it in FreeCAD/slicer post-process or
        // as a print-in-place radius on the mould line before flight parts
        // are cut. A first attempt at cutting it in CSG (a corner cube)
        // produced a single coincident non-manifold edge; removed rather
        // than chased, since it is cosmetic here, not structural.
    }
}

// Door horn: bonded to the door panel's inner face at the bracket's Y
// station, projecting HORN_L toward the crank's drive-arm pin at phi=0.
module door_horn() {
    difference() {
        translate([-HORN_T, -HORN_W / 2, 0]) cube([HORN_T + HORN_L, HORN_W, PIVOT_H]);
        translate([HORN_L - 2, 0, PIVOT_H - 4]) rotate([90, 0, 0])
            cylinder(h = HORN_W + 2, r = PIN_BORE_R, center = true);
    }
}

// Fixed mortise boss: the hook's engaged position (crank at phi=0, i.e. arm
// rotated to ANG_LATCH) defines the lip's location -- read directly off the
// crank at that pose so hook and mortise are always in registration.
module mortise_boss() {
    hx = ARM_LATCH * cos(ANG_LATCH) + HOOK_L * cos(ANG_LATCH);
    hy = ARM_LATCH * sin(ANG_LATCH) + HOOK_L * sin(ANG_LATCH);
    translate([hx, hy, 0])
        rotate([0, 0, ANG_LATCH])
            difference() {
                translate([-LIP_PAD_T / 2, -LIP_PAD_W / 2 - HOOK_FOOT, 0])
                    cube([LIP_PAD_T, LIP_PAD_W + HOOK_FOOT + LIP_OVERHANG, HOOK_ROOT_T + LIP_OVERHANG]);
                // pocket the hook drops into
                translate([-LIP_PAD_T / 2 - EPS, -LIP_PAD_W / 2 - HOOK_FOOT - EPS, -EPS])
                    cube([LIP_PAD_T + 2 * EPS, LIP_PAD_W + HOOK_FOOT + 2 * EPS, HOOK_ROOT_T + EPS]);
            }
}

// Pivot bracket: bonds to the airframe interior at BRACKET_Y, carries the
// crank pin boss and (unioned) the mortise so hook/lip registration is
// baked into one printed part per side -- no separate-part tolerance stack.
module bracket(side) {
    sgn = (side == "port") ? 1 : -1;
    hx = (side == "port") ? HINGE_X_PORT : HINGE_X_STBD;
    hz = (side == "port") ? HINGE_Z_PORT : HINGE_Z_STBD;
    translate([hx - sgn * PIVOT_IN, BRACKET_Y, hz + PIVOT_H])
        mirror(side == "stbd" ? [1, 0, 0] : [0, 0, 0])
            union() {
                translate([-5, -6, -PIVOT_H]) cube([15, 12, PIVOT_H]);  // standoff to the hull
                bell_crank();
                mortise_boss();
            }
}

// PART selector (matches the repo's -D 'PART="..."' export convention)
PART = "bracket_port";  // [bracket_port, bracket_stbd, horn, preview]

if (PART == "bracket_port") bracket("port");
else if (PART == "bracket_stbd") bracket("stbd");
else if (PART == "horn") door_horn();
else if (PART == "preview") {
    color("SteelBlue") bracket("port");
    color("SteelBlue") bracket("stbd");
    color("Gray") translate([HINGE_X_PORT - PIVOT_IN + ARM_DRIVE * cos(ANG_DRIVE),
                              BRACKET_Y + ARM_DRIVE * sin(ANG_DRIVE), HINGE_Z_PORT + PIVOT_H])
        translate([-HORN_L, 0, -PIVOT_H]) door_horn();
}
