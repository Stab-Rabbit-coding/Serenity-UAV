// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See AGENTS.md.
//   X = +port (left), Y = +aft (back), Z = +dorsal (up).  Modelled directly
//   in hull frame (port side; SIDE = -1 translates to starboard).
// ===========================================================================
// ============================================================
// tilt_brake.scad -- Rev T5e (2026-09-16; Rev T5b 2026-09-15 base)
// Spring-applied, solenoid-released PIN BRAKE for the nacelle-tilt worm
// shaft.  Satisfies BRK-1..3 (docs/TILT_DRIVE_CONTROL_SPEC.md SS5.2) for the
// selected Option 2 drive (4-start worm, back-drivable).
//
// WHY A PIN, NOT A FRICTION DISC.  The hold torque is sized to the TRAIN's
// own limit so the brake can never be the weakest link: 1.83 N.m at the
// nacelle (wheel tooth, Lewis, FOS 4) = 0.51 N.m at the drive shaft = 0.051
// N.m at the worm shaft (10:1).  A friction disc at that torque wants ~14 N
// of clamp at r 9 mm (mu 0.4) -- more than a small solenoid releases.  A
// positive pin in a castellated collar holds it in SHEAR: 0.051 N.m at r 5.5
// mm = 9.3 N on a O2 steel pin (tau = 9.3 / 3.14 = 3.0 MPa -- nothing), and
// the solenoid only has to lift the pin's spring plus the pin's friction
// under that side load (9.3 x 0.2 = 1.9 N).  Firmware un-loads the pin (a
// few degrees of motor motion) before commanding release, so even that is
// not the design case.
//
// WHERE.  Coaxial with the worm, AFT of it: the 12-slot face collar is an
// integral stub on the worm's aft end (tilt_actuator_bracket.scad PART=
// "worm" carries it; Rev T5e: the 20D's 18 mm shaft runs through it), the
// pin runs along -Y from a guide block bolted to the bracket WEB's inboard
// face into the collar's face slots, and the pull solenoid sits behind the
// guide, its axis 1.5 mm inboard of the worm's (BRAKE_SOL_X) so the O12
// coil clears the web by 1 mm (Y 62..86).  This is the only placement that
// clears the winch axle above (Z 139..143), the hoisted payload below (Z 85)
// and the battery inboard (tools/cargo_layout_fit.py, PASS 2026-09-16).
// Rev T5e: the guide block's outboard face IS the web face (X -119.75) and
// it is held by 2 x M2.5 THROUGH the web along X at Z +/-11 -- outside the
// web's collar slot (r 9); the T5b block straddled the web plane.
//
// RESOLUTION.  12 slots on the worm shaft = 30 deg at the worm = 3.0 deg at
// the drive shaft = 0.84 deg at the nacelle: after power loss the nacelle
// can drift at most +/-0.42 deg before the pin drops into a slot.
//
// SOLENOID.  Envelope O12 x 24 mm, pull, ~3 N at 3 mm stroke, 6 V, duty
// 100 % (continuous hold-off in flight) or PWM-held -- BOM SOL-TILT-BRAKE,
// part REQUIRES VERIFICATION (no candidate cited yet).  The spring is a
// compression spring over the pin, ~2 N at the engaged length.
//
// FAIL-SAFE LOGIC (BRK-3): coil de-energised = pin engaged.  Any loss of the
// tilt controller's own fused feed, its wiring or its board drops the pin.
//
// PARTS (PART): "guide" (printed, CF-PETG, bolts through the bracket web
//   with 2 x M2.5 along X), "pin" (O2 x 22 steel dowel + printed head -- the head is
//   printed, the dowel is BOM PIN-2X22), "assembly" (with the collar and the
//   solenoid envelope for the FreeCAD view)
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// AI note: Written by Claude (model: Claude Opus 5, Anthropic) under the
//   author's direction, 2026-09-15 / 2026-09-16, per AGENTS.md SS3 AI
//   attribution.
// License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
// ============================================================

include <cargo_layout_t5_params.scad>

PART = "assembly";   // ["guide", "pin", "assembly"]
SIDE = 1;            // [1:port, -1:starboard]

$fn = 48;
EPS = 0.01;

SLOTS       = 12;
PIN_D       = 2.0;
PIN_L       = 22.0;
PIN_CLR     = 0.15;
PIN_R       = 5.5;            // pin radius from the worm axis (slot pitch circle)
PIN_TRAVEL  = 3.0;
SLOT_DEPTH  = 2.5;
SLOT_W      = PIN_D + 0.4;
GUIDE_T     = 5.0;            // guide block thickness (Y): collar face + 1 .. solenoid face
GUIDE_X0    = WORM_X - 9.0;   // inboard face (X -134.25)
GUIDE_X1    = GEAR_X_OUT + 3.0;   // outboard face = bracket web inboard face (-119.75)
GUIDE_H     = 26.0;           // Z, screws at +/-11 clear the web's collar slot (r 9)
SCREW_DZ    = 11.0;
SPRING_OD   = 4.0;
HEAD_D      = 6.0;
HEAD_L      = 4.0;
M25_D       = 2.7;
WALL_T      = 2.0;

CY = BRAKE_Y + BRAKE_COLLAR_L / 2;        // collar aft face
GUIDE_Y0 = CY + 1.0;                     // 1 mm running clearance to the collar face
// Rev T5c: the LibreServo AEAT-8800 (on-axis magnetic encoder) reads a
// O6 x 2.5 diametric magnet in the collar's centre; its carrier PCB
// (SENSOR_PCB_T) is captured in a pocket on the guide block's forward face,
// on the worm axis, inside the pin's slot circle.  The motor therefore needs
// no rear encoder (#1571 25Dx48L), which is what frees the chin flank.
MAGNET_D = 6.0 + 0.2;
MAGNET_L = 2.5;

module translate_side() { if (SIDE < 0) translate([2 * (X_CL - WORM_X), 0, 0]) children(); else children(); }

// Face-castellated collar (integral with the worm's aft stub; drawn here for
// the view -- the printable copy lives in tilt_actuator_bracket.scad worm())
module collar() {
    translate([WORM_X, BRAKE_Y - BRAKE_COLLAR_L / 2, WORM_Z]) rotate([-90, 0, 0]) difference() {
        cylinder(d = BRAKE_COLLAR_D, h = BRAKE_COLLAR_L);
        for (i = [0 : SLOTS - 1]) rotate([0, 0, i * 360 / SLOTS])
            translate([PIN_R - SLOT_W / 2, -SLOT_W / 2, BRAKE_COLLAR_L - SLOT_DEPTH])
                cube([SLOT_W + 2, SLOT_W, SLOT_DEPTH + 1]);
    }
}

// Pin guide: block on the bracket's aft plate with the pin bore, spring
// pocket, solenoid saddle and 2 x M2.5 flange holes
module guide() {
    difference() {
        union() {
            translate([GUIDE_X0, GUIDE_Y0, WORM_Z - GUIDE_H / 2]) cube([GUIDE_X1 - GUIDE_X0, GUIDE_T, GUIDE_H]);
            // solenoid saddle (half pipe wrapping the INBOARD half, open
            // toward the web) aft of the block, on the solenoid's own axis
            translate([BRAKE_SOL_X, GUIDE_Y0 + GUIDE_T - EPS, WORM_Z]) rotate([-90, 0, 0]) difference() {
                cylinder(d = BRAKE_SOL_D + 2 * WALL_T + 0.6, h = 12.0);
                translate([0, 0, -1]) cylinder(d = BRAKE_SOL_D + 0.6, h = 14.0);
                translate([0, -BRAKE_SOL_D - 2, -1]) cube([BRAKE_SOL_D, 2 * BRAKE_SOL_D + 4, 14.0]);
            }
        }
        // 2 x M2.5 through the block AND the bracket web, along X
        for (dz = [-SCREW_DZ, SCREW_DZ])
            translate([GUIDE_X0 - 1, GUIDE_Y0 + GUIDE_T / 2, WORM_Z + dz]) rotate([0, 90, 0])
                cylinder(d = M25_D, h = GUIDE_X1 - GUIDE_X0 + 6);
        // AEAT-8800 carrier pocket on the worm axis (8 x 8 x SENSOR_PCB_T),
        // open toward the collar; the chip sits 1.5 mm from the magnet face
        translate([WORM_X - 4.0, GUIDE_Y0 - 1, WORM_Z - 4.0]) cube([8.0, SENSOR_PCB_T + 1, 8.0]);
        // pin bore at the slot pitch circle, top dead centre
        translate([WORM_X, GUIDE_Y0 - 1, WORM_Z + PIN_R]) rotate([-90, 0, 0]) cylinder(d = PIN_D + 2 * PIN_CLR, h = GUIDE_T + 2);
        // spring pocket behind the bore
        translate([WORM_X, GUIDE_Y0 + 2.0, WORM_Z + PIN_R]) rotate([-90, 0, 0]) cylinder(d = SPRING_OD + 0.4, h = GUIDE_T);
    }
}

module pin() {
    // steel dowel (BOM PIN-2X22) with a printed head the solenoid plunger pulls
    translate([WORM_X, GUIDE_Y0 - SLOT_DEPTH, WORM_Z + PIN_R]) rotate([-90, 0, 0]) {
        color("silver") cylinder(d = PIN_D, h = PIN_L);
        color("gray") translate([0, 0, PIN_L - HEAD_L]) cylinder(d = HEAD_D, h = HEAD_L);
    }
}

module solenoid_env() {
    color("firebrick", 0.6) translate([BRAKE_SOL_X, BRAKE_SOL_Y0, WORM_Z]) rotate([-90, 0, 0]) cylinder(d = BRAKE_SOL_D, h = BRAKE_SOL_L);
}

translate_side() {
    if (PART == "guide") guide();
    else if (PART == "pin") pin();
    else { color("goldenrod") collar(); color("gray") guide(); pin(); solenoid_env(); }
}
