// ===========================================================================
// AIRCRAFT DATUM R2 (2026-10-19, plan 2026-10-19-001): origin centreline / nose / ground.
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
include <cargo_door_hinge_params.scad>

$fn = 48;
EPS = 0.01;

// ---------------------------------------------------------------------------
// Door / hinge geometry (CARGO-HINGE-SYNC single source, 2026-09-21)
// ---------------------------------------------------------------------------
// HINGE_X_PORT/HINGE_Z_PORT/HINGE_X_STBD/HINGE_Z_STBD come from the
// `include <cargo_door_hinge_params.scad>` above -- generated fresh by
// generate_cargo_doors.py every run, not restated here.  A prior revision
// hardcoded these (and, before that, a different stale pair) with no
// mechanism to catch drift when the cargo shell is re-merged; both
// generate_cargo_hinge_retention.py and this file now import/include the
// same single source instead.  Regenerate the door STLs (which writes this
// include) before regenerating this file's parts whenever the shell changes.
// 2nd hinge knuckle station (generate_cargo_doors.py: 12 mm knuckles, 4 evenly
// spaced over the bay) -- clear of the aperture rim (bay fwd edge) and the
// GW-CARGO-DOOR tray.  DERIVED from the hinge include (aircraft datum R2;
// R1 value 39.33), never retyped.
KNUCKLE_LEN  = 12.0;
BRACKET_Y    = HINGE_BAY_Y_FWD + KNUCKLE_LEN / 2
               + (HINGE_BAY_Y_AFT - HINGE_BAY_Y_FWD - KNUCKLE_LEN) / 3;

// Pivot bracket stands PIVOT_H above the hinge Z, inboard of the hinge line
// by PIVOT_IN so the crank clears the door panel's swept arc.
PIVOT_H  = 14.0;
// Rev B (2026-10-26): 10 -> 2.  At 10 mm the bracket reached X 32.5, inside
// the payload keep-out (X +/-38.1 + 2 mm gap): 584 / 544 mm^3 in
// tools/cargo_bulkhead_context.py (BHD-06, owned by DOOR-REWORK).  At 2 mm the
// inboard face is at hinge - 7 = 40.5, clear of the 40.1 gap line.
PIVOT_IN = 2.0;
// BHD-06 (2026-10-12): the standoff ran down to the HINGE Z, so its base sat
// inside the closed door panel (door x bracket 252 / 254 mm^3, Z 3..6.5 at
// this station -- tools/cargo_bulkhead_context.py).  Its base now starts
// BASE_LIFT above the hinge: 1 mm over the door's top here (Z 6.5 + 1.0).
// The bracket still bonds to the hull wall along its outboard face.
// Rev B: 4.5 -> 7.0 -- with the pivot moved outboard the base sits over the
// door's hinge knuckles, whose sweep reaches hinge Z + ~5.
BASE_LIFT = 7.0;

// Crank arms (mm), all about the same pivot pin
ARM_DRIVE = 5.0;    // rA: to the door-horn pushrod (D-LATCH-1)
ARM_LATCH = 10.0;   // rB: to the hook (r_lip in the statics package)

// Angular layout (deg) of the two arms about the crank pivot, phi=0 = door
// fully closed.  DRIVE arm points toward the door horn at phi=0; LATCH arm
// points into the mortise.
ANG_DRIVE = 200.0;
// Rev B (2026-10-26): 20 -> 60.  With the pivot 2 mm inboard of the hinge
// (PIVOT_IN) a 20 deg latch arm put the hook tip and its mortise against the
// flank (crank x shell 1.68 mm^3; mortise bridge 0.76 mm outside the skin,
// tools/placement_audit.py).  Swung 40 deg forward the arm stays inboard;
// r_lip = ARM_LATCH is unchanged, so the CARGO_DOOR_LATCH_SPEC statics hold,
// and mortise_boss() reads this angle, so hook and mortise stay registered.
ANG_LATCH = 60.0;

PIN_D = 3.0;  PIN_CL = 0.075;  PIN_BORE_R = PIN_D/2 + PIN_CL;

// Rev B (DOOR-REWORK, owner 2026-10-19): ONE latch, on the PORT door, now
// holds BOTH doors -- the port door's lap traps the starboard door's edge
// (generate_cargo_doors.py LAP_*), so the port latch reacts 2 x the Rev A
// door moment.  Hook root 5 x 2.4 (12 mm^2) -> 7 x 3.5 (24.5 mm^2) restores
// FOS_shear ~3.0; the lip pad widens with it (docs/CARGO_DOOR_LATCH_SPEC.md
// Rev B).
HOOK_L = 6.0;   HOOK_ROOT_W = 7.0;  HOOK_ROOT_T = 3.5;  // FOS_shear ~3.1 at 2 doors
HOOK_FOOT = 3.0;                                         // engagement depth under the lip
LIP_OVERHANG = 2.4;  LIP_PAD_W = 7.0;  LIP_PAD_T = 4.0;  // FOS_bearing ~9 at 2 doors
// Only these sides carry the hook + mortise.  The starboard bell-crank is a
// DRIVE-ONLY crank (no latch arm, no mortise): starboard is held shut by the
// port door's lap, never by its own latch.
LATCHED_SIDES = ["port"];
function is_latched(side) = len([for (s = LATCHED_SIDES) if (s == side) s]) > 0;
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

module bell_crank(latch = true) {
    union() {
        pivot_boss();
        crank_arm(ANG_DRIVE, ARM_DRIVE, 4.0, 5.0);
        if (latch)
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
// Rev B part split (2026-10-26): the bell-crank ROTATES on the pivot pin, so
// it is its own printed part.  Rev A unioned it into the fixed bracket (one
// STL that could never move; the hook-in-pocket coincidence also left a
// zero-volume sliver body).  The bracket now carries the pin in a blind bore
// in the standoff top; the crank sits on that face and turns on the pin.
module at_pivot(side) {
    sgn = (side == "port") ? 1 : -1;
    hx = (side == "port") ? HINGE_X_PORT : HINGE_X_STBD;
    hz = (side == "port") ? HINGE_Z_PORT : HINGE_Z_STBD;
    translate([hx - sgn * PIVOT_IN, BRACKET_Y, hz + PIVOT_H])
        mirror(side == "stbd" ? [1, 0, 0] : [0, 0, 0])
            children();
}

PIN_SEAT_D = PIN_D - 0.1;   // press seat for the steel pin in the standoff
PIN_SEAT_H = 6.0;           // blind seat depth below the crank face

module bracket(side) {
    at_pivot(side) difference() {
        union() {
            translate([-5, -6, -PIVOT_H + BASE_LIFT])
                cube([15, 12, PIVOT_H - BASE_LIFT]);               // standoff to the hull
            if (is_latched(side)) {
                mortise_boss();
                // the mortise is FIXED structure: tie it to the standoff
                // BELOW the crank plane (z < 0), where the crank never sweeps
                hull() {
                    translate([-5, -6, -PIVOT_H + BASE_LIFT]) cube([15, 12, PIVOT_H - BASE_LIFT - EPS]);
                    intersection() {
                        mortise_boss();
                        translate([-50, -50, -1]) cube([100, 100, 1 + EPS]);
                    }
                    translate([0, 0, -PIVOT_H + BASE_LIFT]) linear_extrude(EPS)
                        projection() mortise_boss();
                }
            }
        }
        translate([0, 0, -PIN_SEAT_H]) cylinder(h = PIN_SEAT_H + EPS, d = PIN_SEAT_D);
    }
}

module crank(side) {
    at_pivot(side) bell_crank(latch = is_latched(side));
}

// PART selector (matches the repo's -D 'PART="..."' export convention)
PART = "bracket_port";  // [bracket_port, bracket_stbd, crank_port, crank_stbd, horn, preview]

if (PART == "bracket_port") bracket("port");
else if (PART == "bracket_stbd") bracket("stbd");
else if (PART == "crank_port") crank("port");
else if (PART == "crank_stbd") crank("stbd");
else if (PART == "horn") door_horn();
else if (PART == "preview") {
    color("SteelBlue") bracket("port");
    color("SteelBlue") bracket("stbd");
    color("Orange") crank("port");
    color("Orange") crank("stbd");
    color("Gray") translate([HINGE_X_PORT - PIVOT_IN + ARM_DRIVE * cos(ANG_DRIVE),
                              BRACKET_Y + ARM_DRIVE * sin(ANG_DRIVE), HINGE_Z_PORT + PIVOT_H])
        translate([-HORN_L, 0, -PIVOT_H]) door_horn();
}
