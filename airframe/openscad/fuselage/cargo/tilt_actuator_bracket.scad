// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See AGENTS.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.
//   This file:
//     MODELLED DIRECTLY IN HULL FRAME (port side; SIDE = -1 mirrors about the
//     hull centreline X_CL for starboard).  Exported STLs import into
//     serenity_assembly.py at identity placement.  Print orientation is set
//     in the slicer (see PRINT ORIENTATION below), not here.
// ===========================================================================
// ============================================================
// tilt_actuator_bracket.scad -- Rev T5e (2026-09-16; Rev T5 2026-09-15 base)
// Nacelle-tilt actuator: worm-drive bracket, worm and worm wheel for the
// cargo-section fuselage stage.
//
// REV T5e (2026-09-16) -- what changed and why (docs/CARGO_SECTION_LAYOUT.md
// SS4, findings T5d-1..3):
//   * Gearmotor: Pololu 20D 25:1 CB 6 V (#3712, REF-ACT-001) replaces the
//     25D HP 9.7:1.  For a motor coaxial with the worm the motor-to-wheel-tip
//     gap is (WORM_PD/2 - MOTOR_D/2 - m) whatever C or the worm's angle on
//     the wheel is; with the worm's inboard reach capped by the battery
//     cradle (WORM_PD <= 26) a O25 body can never clear the O42 wheel
//     (T5d-1: -1.5 mm), a O20 body clears it by 2.0 mm.
//   * Worm: SIX-start m1 O26 (lead 13.0 deg) so the slower 20D still meets
//     TILT-CTL-07: 570 / 6.667 / 3.571 = 23.9 rpm = 144 deg/s at the nacelle.
//   * Controller board: moved from the web's INBOARD face (where the Rev T5b
//     rails ran straight through the worm -- T5d-2) to the web's OUTBOARD
//     face in the shoulder pocket, aft of the worm's reach (Y 55..97.9,
//     Z 85..121.5); the web is extended aft to Y 97.5 to carry it.
//   * Web slot for the worm + brake collar (T5d-3: the T5b web had no cut
//     where the O26 worm reaches 6.5 mm past the web plane).
//   * Feet: 0 / 1 in the top row forward of the board, 2 low at (Y 64, Z 77).
//   Stations are proved by tools/cargo_layout_fit.py (PASS 2026-09-16).
//
// WHAT THIS REPLACES.  Through Rev T4 the fuselage stage was a 38T/38T
// m0.8 spur pair driven by a DS3225 body carrying LibreServo_v4 with its
// rotation-limit pin removed, on a pair of 18 mm standoff pads
// (merge_cargo_interior.py NSVMT_*).  Two findings retired it:
//   1. WA-R16 (BLOCKS FLIGHT): the spur/spur train is not self-locking, so
//      an unpowered nacelle back-drives under an unquantified aero moment
//      (docs/TILT_DRIVE_CONTROL_SPEC.md SS5.2).
//   2. The DS3225 body reached to hull X -158.5 / -221.5, which is where the
//      flight battery has to go (docs/CARGO_SECTION_LAYOUT.md).
// A worm on a small gearmotor lying along the sidewall fixes the second:
// the motor body no longer reaches into the bay.  It does NOT fix the first
// by itself -- a single-start worm self-locks but is too slow to vector
// (24 deg/s), and any multi-start worm fast enough is back-drivable -- so
// the unpowered hold is a spring-applied pin brake on the worm shaft
// (tilt_brake.scad, BRK-1..3 in docs/TILT_DRIVE_CONTROL_SPEC.md SS5.2).
//
// KINEMATICS (docs/TILT_DRIVE_CONTROL_SPEC.md SS1.1):
//   gearmotor --[worm 6-start / wheel 40T, m1, C 33.0, 6.667:1]--> drive shaft
//   drive shaft --[tip pinion 14T -> ring 50T, m0.8, i 3.571]--> nacelle
//   Total 23.8:1.  145 deg of nacelle = 9.6 gearmotor-output revolutions
//   = 1.0 s at the 570 rpm no-load figure (Pololu 20D 25:1 CB 6 V,
//   REF-ACT-001); 144 deg/s at the nacelle, 111 deg/s at max efficiency.
//   Sense: a worm/wheel mesh reverses like an external spur pair, so the
//   double reversal of Rev T4 is preserved -- actuator-positive is nacelle-
//   positive on PORT; the starboard worm is the same right-hand part
//   translated, so starboard is REVERSED.  DECLARE IT IN FIRMWARE.
//
// LOADS.  Grounded tilt torque 0.177 N.m at the nacelle
//   (docs/TILT_SPAR_ANALYSIS.md SS2.1) -> 0.0496 N.m at the drive shaft
//   (wheel) -> tangential force on the wheel F_t = 0.0496 / 0.020 = 2.48 N
//   (0.56 lbf), which is also the axial thrust on the worm shaft.  Worm
//   torque at eta 0.51 (mu 0.20, lead 13 deg): 0.0496 / (6.667 x 0.51) =
//   0.0146 N.m = 0.149 kgf.cm against 1.6 kgf.cm stall -- 10.7x.  At motor
//   STALL the wheel sees 1.6 x 6.667 x 0.51 = 5.4 kgf.cm = 0.53 N.m, i.e.
//   the wheel-tooth Lewis limit (0.51 N.m, FOS 4) and the motor stall are
//   matched -- the train is limited by both together, the brake (BRK-1) is
//   sized to it.  Torque is not a driver anywhere in this bracket;
//   STIFFNESS of the centre distance is (a worm mesh tolerates +/-0.15 mm
//   of C at m1 before the backlash doubles), which is why the three feet sit
//   on a single flat plate and the feet slots allow a one-time shim at
//   assembly.  Worm thrust at motor stall: 0.53 / 0.020 = 27 N along Y into
//   the gearbox's own output bearing (REF-ACT-001 gives no axial rating --
//   VERIFY; a thrust washer between the worm hub and the face plate is the
//   fallback).
//
// PARTS (select with PART):
//   "bracket"  -- CF-PETG, one print, 3 feet to shell bosses (M3 heat-set)
//   "worm"     -- printed (PETG, 0.12 mm layers), six-start RH m1 O26 with
//                 the integral brake collar; no commercial equivalent is
//                 catalogued (BOM PRINT-TILT-WORM).
//                 ONE part, RIGHT-HAND, used on BOTH sides -- the starboard
//                 bracket is a mirror but the worm is NOT mirrored (a mirror
//                 would make it left-hand); the assembly TRANSLATES it.  The
//                 consequence is that the two sides turn opposite nacelle
//                 senses for the same motor direction: declare per side.
//   "wheel"    -- CF-PETG 40T m1, O4 bore, M3 grub, on the drive shaft; one
//                 part, 2 off, translated for starboard like the worm
//   "motor"    -- Pololu 20D #3712 placeholder (not printed) for assembly views
//   "assembly" -- everything, port side, for the FreeCAD assembly
//
// PRINT ORIENTATION:
//   bracket: foot plate DOWN on the bed (the YZ web is the bed plane, i.e.
//     print with hull X vertical, foot pads and board rails UP).  The motor
//     cradle then prints as a half pipe standing on its face plate -- no
//     supports.  4 perimeters, 40 % gyroid.
//   worm: axis vertical (hull Y vertical), 0.12 mm layers, 100 % infill.
//   wheel: face DOWN (hull X vertical), 0.16 mm layers, 5 perimeters.
//
// MASS (solid-volume upper bound x 1.05 g/cm^3 as-printed CF-PETG):
//   computed by tools/cargo_parts_mass.py at export -- see BOM rows
//   PRINT-TILT-BRACKET / PRINT-TILT-WHEEL / PRINT-TILT-WORM.
//
// Single-source numbers: cargo_layout_t5_params.scad (GENERATED by
//   tools/cargo_layout_fit.py --write-scad).  Do not restate them here.
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// AI note: Written by Claude (model: Claude Opus 5, Anthropic) under the
//   author's direction, 2026-09-15 / 2026-09-16, per AGENTS.md SS3 AI
//   attribution.
// License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
// References (REFERENCES.md): REF-ACT-001 (Pololu 20D gearmotor: 20Dx41L,
//   O4 D-shaft 18 mm, 6 x 2 mm rear shaft, M2.5 mounting threads; the hole
//   spacing (15 mm) and O7 boss are from the dimension diagram -- VERIFY),
//   REF-STD-GEAR-002 (worm self-locking condition), REF-SENSOR-008 (AK7455).
// ============================================================

include <cargo_layout_t5_params.scad>

PART = "assembly";   // ["bracket", "worm", "wheel", "motor", "assembly"]
SIDE = 1;            // [1:port, -1:starboard]  mirror about X_CL

$fn = 64;
EPS = 0.01;

// ---------------------------------------------------------------------------
// Bracket parameters (hull frame, port side)
// ---------------------------------------------------------------------------
WALL_T        = 2.0;                     // CF-PETG structural wall
WEB_X1        = GEAR_X_OUT + 5.0;        // foot / web plane, outboard face (-117.75)
WEB_X0        = WEB_X1 - WALL_T;         // -119.75 -- 3.0 mm clear of the wheel face
WEB_Y0        = 4.0;
WEB_Y1        = 97.5;                    // Rev T5e: carries the board rails; 2 mm fwd of node N2 (Y 99.5)
WEB_Z0        = 70.0;                    // foot 2 pad bottom (71) sits on it; harness bores are Z <= 69 in the WALL
WEB_Z1        = 133.0;
FOOT_PAD      = 12.0;                    // square foot pad, matches shell boss
FOOT_T        = 3.0;                     // pad thickness (outboard of the web)
M3_CLR        = 3.4;                     // ISO 273 medium
M3_SLOT       = 0.6;                     // +/- shim travel in Z for centre-distance set-up
MOTOR_R       = MOTOR_D / 2;
CRADLE_R_IN   = MOTOR_R + 0.3;           // slip fit over the 20.0 body (0.3 radial)
CRADLE_R_OUT  = CRADLE_R_IN + WALL_T;
CRADLE_Y0     = MOTOR_FACE_Y - 37.0;     // forward end; leaves the rear cap + 6 mm rear shaft free
FACE_T        = 2.5;                     // face plate thickness (aft of the gearbox face) = WORM_HUB_L: the hub turns INSIDE the plate's bore
FACE_R        = MOTOR_D / 2 + 3.5;       // face plate radius
MOTOR_BOSS_D  = 7.0 + 0.4;               // O7.0 gearbox boss (REF-ACT-001) + clearance (the hub bore below supersedes it)
HUB_BORE_D    = 10.0 + 0.4;              // worm hub (O10) turns inside the face plate; the hub's forward face bears on the gearbox boss
M25_CLR       = 2.7;                     // M2.5 clearance (20D: 2 x M2.5 on MOTOR_HOLE_S, REF-ACT-001)
TIE_SLOT      = [1.6, 4.5];              // cable-tie slot (thickness x width)
// LibreServo_v4 board (36.5 x 42.9 mm outline, LibreServo-v4.0.0.kicad_pcb
// Edge.Cuts, read 2026-09-15; NO mounting holes in v4.0.0) -- card-edge
// rails on the web's OUTBOARD face (Rev T5e), board plane parallel to the
// web, component side toward the web (RAIL_H standoff), bare back to the
// skin.  BOARD_L / BOARD_W / BOARD_Y0 / BOARD_Z0 come from the params file
// (hull Y extent 42.9, hull Z extent 36.5, Y 55, Z 85).
BOARD_PCB_T   = 1.6;
RAIL_CLR      = 0.3;
RAIL_H        = 4.0;                     // rail standoff (component clearance under the board)
RAIL_CAP      = 1.2;                     // outboard lip of each rail (BOARD_T = RAIL_H + PCB + 2 CLR + CAP = 7.4)
// Worm / collar slot through the web: the O26 worm reaches 6.5 mm and the
// O14 collar 1.5 mm past the web plane
SLOT_Y0       = WORM_YC - WORM_LEN / 2 - 1.5;
SLOT_Y1       = BRAKE_Y + BRAKE_COLLAR_L / 2 + 1.0;
SLOT_R_WORM   = WORM_PD / 2 + GEAR_MODULE + GAP_MM;
SLOT_R_COLLAR = BRAKE_COLLAR_D / 2 + 2.0;

// Worm and wheel
WORM_TIP_R    = WORM_PD / 2 + GEAR_MODULE;
WORM_ROOT_R   = WORM_PD / 2 - 1.25 * GEAR_MODULE;
WORM_HUB_D    = 10.0;
WORM_BORE_D   = 4.0 + 0.15;              // O4 D-shaft, slip
WORM_D_FLAT   = 3.5;                     // D flat width across (REF-ACT-001: 3.5 / 0.3 deep)
WHEEL_TIP_R   = WHEEL_PD / 2 + GEAR_MODULE;
WHEEL_ROOT_R  = WHEEL_PD / 2 - 1.25 * GEAR_MODULE;
WHEEL_HUB_D   = 10.0;
WHEEL_HUB_L   = 8.0;                     // hub extends INBOARD of the rim (away from the wall)
WHEEL_BORE_D  = 4.0 + 0.1;               // O4 AISI 4130 drive shaft
GRUB_D        = 2.5;                     // M3 tap drill

// ---------------------------------------------------------------------------
module mirror_side() {
    // Port geometry is authored; starboard is a mirror about the hull
    // centreline for the BRACKET and the motor envelope.  The worm and the
    // wheel are bodies of revolution (the worm carries a hand) and are
    // TRANSLATED, never mirrored -- see PARTS above.
    if (SIDE < 0) translate([2 * X_CL, 0, 0]) mirror([1, 0, 0]) children();
    else children();
}
module translate_side() {
    if (SIDE < 0) translate([2 * (X_CL - WORM_X), 0, 0]) children();
    else children();
}

module cyl_y(r, y0, y1) {
    translate([0, y0, 0]) rotate([-90, 0, 0]) cylinder(r = r, h = y1 - y0);
}
module cyl_x(r, x0, x1) {
    translate([x0, 0, 0]) rotate([0, 90, 0]) cylinder(r = r, h = x1 - x0);
}

// ---------------------------------------------------------------------------
// BRACKET
// ---------------------------------------------------------------------------
module web_plate() {
    difference() {
        translate([WEB_X0, WEB_Y0, WEB_Z0])
            cube([WALL_T, WEB_Y1 - WEB_Y0, WEB_Z1 - WEB_Z0]);
        // motor clearance slot: the body runs forward of the face plate
        translate([WEB_X0 - 1, WEB_Y0 - 1, WORM_Z - MOTOR_R - GAP_MM])
            cube([WALL_T + 2, MOTOR_FACE_Y - WEB_Y0 + 1, MOTOR_D + 2 * GAP_MM]);
        // worm + brake-collar slot (Rev T5e, T5d-3): rounded ends
        translate([WEB_X0 - 1, 0, WORM_Z]) hull() {
            translate([0, SLOT_Y0 + SLOT_R_WORM, 0]) cyl_x(SLOT_R_WORM, 0, WALL_T + 2);
            translate([0, WORM_YC + WORM_LEN / 2, 0]) cyl_x(SLOT_R_WORM, 0, WALL_T + 2);
        }
        translate([WEB_X0 - 1, 0, WORM_Z]) hull() {
            translate([0, WORM_YC + WORM_LEN / 2, 0]) cyl_x(SLOT_R_COLLAR, 0, WALL_T + 2);
            translate([0, SLOT_Y1, 0]) cyl_x(SLOT_R_COLLAR, 0, WALL_T + 2);
        }
        // 2 x M2.5 through-holes for the brake guide block (tilt_brake.scad:
        // block Y = collar aft face + 1 .. + 5, screws at Z +/-11)
        for (dz = [-11, 11])
            translate([WEB_X0 - 1, BRAKE_Y + BRAKE_COLLAR_L / 2 + 1.0 + 2.5, WORM_Z + dz])
                cyl_x(2.7 / 2, 0, WALL_T + 2);
        // lightening windows (keep 6 mm bars) -- below the worm slot only
        for (y = [WEB_Y0 + 6, SLOT_Y1 + 4])
            translate([WEB_X0 - 1, y, WEB_Z0 + 4])
                cube([WALL_T + 2, 14, 8]);
    }
}

module foot_pads() {
    for (f = BRACKET_FEET) {
        fy = f[0]; fz = f[1];
        difference() {
            translate([WEB_X1 - EPS, fy - FOOT_PAD / 2, fz - FOOT_PAD / 2])
                cube([FOOT_T + EPS, FOOT_PAD, FOOT_PAD]);
            // M3 clearance, slotted +/- M3_SLOT in Z for the centre-distance shim
            hull() for (dz = [-M3_SLOT, M3_SLOT])
                translate([WEB_X0 - 1, fy, fz + dz]) cyl_x(M3_CLR / 2, 0, WALL_T + FOOT_T + 2);
        }
    }
    // bridge from the pads back into the web where a pad lies outside it
    for (f = BRACKET_FEET) {
        fy = f[0]; fz = f[1];
        translate([WEB_X0, max(WEB_Y0, fy - FOOT_PAD / 2), max(WEB_Z0, fz - FOOT_PAD / 2)])
            cube([WALL_T, FOOT_PAD, min(WEB_Z1, fz + FOOT_PAD / 2) - max(WEB_Z0, fz - FOOT_PAD / 2)]);
    }
}

module face_plate() {
    // Rev T5e: the plate is FLAT-BOTTOMED at the motor body's underside
    // (WORM_Z - MOTOR_R = 92.09): a round plate reached 1.5 mm into the O42
    // wheel's tip circle (Z 90.09) over Y 34..37.  The two M2.5 holes are on
    // a +/-45 deg diagonal so both stay inside the plate above the flat.
    difference() {
        translate([WORM_X, MOTOR_FACE_Y, WORM_Z]) hull() {
            cyl_y(FACE_R, 0, FACE_T);
            // tie the plate up/outboard into the web
            translate([WEB_X1 - WORM_X - WALL_T, 0, -MOTOR_R])
                cube([WALL_T, FACE_T, FACE_R + MOTOR_R]);
        }
        translate([WORM_X - FACE_R - 1, MOTOR_FACE_Y - 1, WORM_Z - FACE_R - 1])
            cube([2 * FACE_R + 2, FACE_T + 2, FACE_R - MOTOR_R + 1]);
        translate([WORM_X, MOTOR_FACE_Y - 1, WORM_Z]) cyl_y(HUB_BORE_D / 2, 0, FACE_T + 2);
        for (sgn = [-1, 1])
            translate([WORM_X + sgn * MOTOR_HOLE_S / 2 * cos(45), MOTOR_FACE_Y - 1,
                       WORM_Z + sgn * MOTOR_HOLE_S / 2 * sin(45)])
                cyl_y(M25_CLR / 2, 0, FACE_T + 2);
    }
}

module motor_cradle() {
    // half pipe on the OUTBOARD side of the motor (open toward the bay so the
    // motor drops in), from the face plate forward to CRADLE_Y0.  Rev T5e:
    // nothing below the motor body's underside (Z 92.09) -- the wheel tip is
    // 2 mm under it from Y 25.6 aft -- so the pipe is the top + outboard
    // quadrants; the face-plate screws and two cable ties hold the motor.
    difference() {
        translate([WORM_X, 0, WORM_Z]) cyl_y(CRADLE_R_OUT, CRADLE_Y0, MOTOR_FACE_Y + EPS);
        translate([WORM_X, 0, WORM_Z]) cyl_y(CRADLE_R_IN, CRADLE_Y0 - 1, MOTOR_FACE_Y + 1);
        // open the inboard half (keep 200 deg of arc for retention)
        translate([WORM_X - 2 * CRADLE_R_OUT, CRADLE_Y0 - 1, WORM_Z - CRADLE_R_OUT - 1])
            cube([2 * CRADLE_R_OUT - 3.0, MOTOR_FACE_Y - CRADLE_Y0 + 2, 2 * CRADLE_R_OUT + 2]);
        // two cable-tie slot pairs
        for (y = [CRADLE_Y0 + 6, MOTOR_FACE_Y - 8])
            translate([WORM_X - CRADLE_R_OUT - 1, y, WORM_Z - TIE_SLOT[1] / 2])
                cube([2 * CRADLE_R_OUT + 2, TIE_SLOT[0], TIE_SLOT[1]]);
        // trim below the motor underside
        translate([WORM_X - 2 * CRADLE_R_OUT, CRADLE_Y0 - 1, WORM_Z - 2 * CRADLE_R_OUT])
            cube([4 * CRADLE_R_OUT, MOTOR_FACE_Y - CRADLE_Y0 + 2, 2 * CRADLE_R_OUT - MOTOR_R]);
    }
    // filler blocks: bond the cradle's outboard wall to the web bars above
    // and below the motor slot; the lower one stops 3 mm forward of the wheel
    translate([WEB_X0, WEB_Y0, WORM_Z + MOTOR_R + GAP_MM - 5.0])
        cube([WEB_X1 - WEB_X0 + 3.0, MOTOR_FACE_Y - WEB_Y0, 6.0]);
    translate([WEB_X0, WEB_Y0, WORM_Z - MOTOR_R - GAP_MM - 1.0])
        cube([WEB_X1 - WEB_X0 + 3.0, SHAFT_Y - WHEEL_PD / 2 - GEAR_MODULE - GAP_MM - WEB_Y0, 6.0]);
}

module board_rails() {
    // two card-edge rails (top / bottom of the board) on the OUTBOARD face.
    // Each rail is a U: the slot is open toward the other rail so the board
    // slides in from aft (+Y, past the web's aft edge) and is retained by a
    // cable tie through the web; a stop closes the forward end.
    rail_w = RAIL_H + BOARD_PCB_T + 2 * RAIL_CLR + RAIL_CAP;   // 7.4 proud of the web = BOARD_T
    for (top = [0, 1]) {
        zz = top ? BOARD_Z0 + BOARD_W + RAIL_CLR - 1.0 : BOARD_Z0 - RAIL_CLR - 2.0;
        difference() {
            translate([WEB_X1 - EPS, BOARD_Y0 - 2, zz]) cube([rail_w, WEB_Y1 - BOARD_Y0 + 2, 3.0]);
            // slot: 1 mm cap left on the far side so the lip stays attached
            translate([WEB_X1 + RAIL_H, BOARD_Y0 - 1, top ? zz - 1 : zz + 1])
                cube([BOARD_PCB_T + 2 * RAIL_CLR, WEB_Y1 - BOARD_Y0 + 4, 3.0]);
        }
    }
    // forward stop
    translate([WEB_X1 - EPS, BOARD_Y0 - 2, BOARD_Z0 - RAIL_CLR - 2.0])
        cube([rail_w, 2.0, BOARD_W + 2 * RAIL_CLR + 4.0]);
}

module bracket() {
    union() {
        web_plate();
        foot_pads();
        face_plate();
        motor_cradle();
        board_rails();
    }
}

// ---------------------------------------------------------------------------
// WORM (WORM_STARTS starts, m1) -- thread by twisted extrusion of the
// TRANSVERSE tooth section.  Each start is a sector whose angular half-
// width at radius r follows the axial tooth thickness t(r) of a 20 deg
// trapezoidal thread: t = pi.m/2 at the pitch radius, +/- 2 (r - r_p) tan 20
// toward root / tip, mapped to angle by t / LEAD x 360.  (The Rev T5b
// profile used a fixed +/-0.79 mm TANGENTIAL half-width, which is a thread
// far too thin for any lead -- corrected in Rev T5e.)
// ---------------------------------------------------------------------------
WORM_LEAD     = PI * GEAR_MODULE * WORM_STARTS;   // 18.85 mm (6 starts)
function worm_t(r) = PI * GEAR_MODULE / 2 - 2 * (r - WORM_PD / 2) * tan(20);   // axial thickness at r
function worm_half_ang(r) = worm_t(r) / WORM_LEAD * 180;                         // deg
module worm_tooth_2d() {
    n = 6;   // radial steps root -> tip
    rs = [for (i = [0 : n]) WORM_ROOT_R - 0.2 + (WORM_TIP_R - WORM_ROOT_R + 0.2) * i / n];
    polygon(concat(
        [for (r = rs) [r * cos(-worm_half_ang(r)), r * sin(-worm_half_ang(r))]],
        [for (i = [n : -1 : 0]) let (r = rs[i]) [r * cos(worm_half_ang(r)), r * sin(worm_half_ang(r))]]));
}
module worm_profile() {
    union() {
        circle(r = WORM_ROOT_R);
        for (k = [0 : WORM_STARTS - 1]) rotate(k * 360 / WORM_STARTS) worm_tooth_2d();
    }
}

module worm() {
    translate([WORM_X, WORM_YC - WORM_LEN / 2, WORM_Z]) rotate([-90, 0, 0]) difference() {
        union() {
            linear_extrude(height = WORM_LEN, twist = -360 * WORM_LEN / WORM_LEAD,
                           slices = WORM_LEN * 6, convexity = 10)
                worm_profile();
            // hub toward the face plate (forward = -Y = local -Z here)
            translate([0, 0, -WORM_HUB_L + EPS]) cylinder(d = WORM_HUB_D, h = WORM_HUB_L);
            // Rev T5b: brake collar -- 12 face slots on an integral aft stub
            // (tilt_brake.scad; BRK-1..3).  Rev T5e: the 20D's 18 mm shaft
            // runs THROUGH the collar (2.5 hub + 10 worm + 0.5 + 4 collar =
            // 17.0), so the D bore continues to the collar's slot floor and
            // the magnet pocket sits in the last 1 mm beyond the shaft end.
            translate([0, 0, WORM_LEN - EPS]) cylinder(d = WORM_HUB_D, h = 0.5 + EPS);
            translate([0, 0, WORM_LEN + 0.5]) difference() {
                cylinder(d = BRAKE_COLLAR_D, h = BRAKE_COLLAR_L);
                for (i = [0 : 11]) rotate([0, 0, i * 30])
                    translate([5.5 - 1.2, -1.2, BRAKE_COLLAR_L - 2.5]) cube([4.0, 2.4, 3.0]);
                // Rev T5c: O6.2 x 2.5 diametric-magnet pocket on the axis --
                // the LibreServo AEAT-8800 in the brake guide reads it, so the
                // gearmotor carries no rear encoder (#1571, 25Dx48L)
                translate([0, 0, BRAKE_COLLAR_L - 1.0]) cylinder(d = 6.2, h = 3.0);
            }
        }
        // D bore, through hub + worm + 0.5 + the collar's first 3 mm
        // (shaft end at MOTOR_SHAFT_L from the face plate)
        translate([0, 0, -WORM_HUB_L - 1]) difference() {
            cylinder(d = WORM_BORE_D, h = MOTOR_SHAFT_L + 1);
            translate([-5, WORM_D_FLAT / 2 + (WORM_BORE_D / 2 - WORM_D_FLAT / 2) - 0.3, -1])
                cube([10, 10, MOTOR_SHAFT_L + 3]);
        }
        // M3 grub, radial, into the hub, onto the D flat
        translate([0, 0, -WORM_HUB_L / 2]) rotate([0, 90, 0]) cylinder(d = GRUB_D, h = 10);
    }
}

// ---------------------------------------------------------------------------
// WHEEL (40T m1, plain spur profile -- adequate at 2.5 N tooth load)
// ---------------------------------------------------------------------------
module wheel_2d() {
    union() {
        circle(r = WHEEL_ROOT_R, $fn = 120);
        for (i = [0 : WHEEL_N - 1]) rotate(i * 360 / WHEEL_N)
            polygon([[WHEEL_ROOT_R - 0.3, -PI * GEAR_MODULE / 4 - 0.5],
                     [WHEEL_TIP_R, -PI * GEAR_MODULE / 4 + 0.9 * tan(20) + 0.25],
                     [WHEEL_TIP_R,  PI * GEAR_MODULE / 4 - 0.9 * tan(20) - 0.25],
                     [WHEEL_ROOT_R - 0.3,  PI * GEAR_MODULE / 4 + 0.5]]);
    }
}

module wheel() {
    translate([GEAR_X_OUT - WHEEL_FACE, SHAFT_Y, SHAFT_Z]) rotate([0, 90, 0]) difference() {
        union() {
            linear_extrude(height = WHEEL_FACE, convexity = 10) wheel_2d();
            // hub INBOARD of the rim (local -Z = hull -X)
            translate([0, 0, -WHEEL_HUB_L + EPS]) cylinder(d = WHEEL_HUB_D, h = WHEEL_HUB_L);
        }
        translate([0, 0, -WHEEL_HUB_L - 1]) cylinder(d = WHEEL_BORE_D, h = WHEEL_FACE + WHEEL_HUB_L + 2);
        translate([0, 0, -WHEEL_HUB_L / 2]) rotate([0, 90, 0]) cylinder(d = GRUB_D, h = 10);
    }
}

// ---------------------------------------------------------------------------
// MOTOR placeholder (REF-ACT-001 envelope) -- for assembly views only
// ---------------------------------------------------------------------------
module motor() {
    translate([WORM_X, 0, WORM_Z]) {
        cyl_y(MOTOR_R, MOTOR_FACE_Y - MOTOR_BODY_L, MOTOR_FACE_Y);          // body
        cyl_y(7.0 / 2, MOTOR_FACE_Y, MOTOR_FACE_Y + 0.9);                    // boss
        cyl_y(2.0, MOTOR_FACE_Y, MOTOR_FACE_Y + MOTOR_SHAFT_L);              // O4 shaft
        cyl_y(1.0, MOTOR_FACE_Y - MOTOR_BODY_L - MOTOR_ENC_L,
              MOTOR_FACE_Y - MOTOR_BODY_L);                                  // 6 x 2 mm rear shaft
    }
}

// ---------------------------------------------------------------------------
if (PART == "worm") translate_side() worm();
else if (PART == "wheel") translate_side() wheel();
else mirror_side() {
    if (PART == "bracket") bracket();
    else if (PART == "motor") motor();
    else {
        color("gray") bracket();
        color("dimgray") motor();
    }
}
if (PART == "assembly") translate_side() {
    color("goldenrod") worm();
    color("steelblue") wheel();
}
