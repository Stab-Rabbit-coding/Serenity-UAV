// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame: X = +port, Y = +aft, Z = +dorsal (up).
//   Landing gear parts are in hull frame; NOT primary-component STLs;
//   do NOT bake with bake_hull_frame.py.
// ===========================================================================
// ===========================================================================
// landing_leg_assy.scad
// Serenity UAV — Rev R1.4 — Landing Leg Assembly (Corner V-Brace Frame)
// ===========================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-06-15
// Revision: Rev R1.4
//
// Mounting geometry mates to the canonical hull derived from "Serenity
// Firefly with landing gear and swivel engines" by misubisu
// (thingiverse.com/thing:7330462, CC BY 4.0).
// Full attribution chain: current-specification/LICENSE_AND_ATTRIBUTION.md §2.
//
// Description
// -----------
// Parametric landing leg assembly for the Serenity UAV.  Four leg assemblies
// attach to the cargo section belly corners, one per corner.
//
// Canonical geometry — corner V-brace frame:
//
//   Each corner has ONE MAIN VERTICAL STRUT hanging below the belly, braced
//   by TWO ISOSCELES TRIANGULAR ARMS (upper + lower) to the hull corner.
//
//   Each arm (V-brace) has:
//     BOSS A — on the END-WALL of the cargo (fore face for fore corners,
//       aft face for aft corners).  Protrudes outward from that face.
//       Position: ARM_HALF_SPREAD in hull-Y (toward nearest hull end face)
//       from the strut centreline.
//     BOSS B — on the OUTBOARD SIDE-WALL of the cargo (port face for port
//       corners, stbd face for stbd corners).  Protrudes outward laterally.
//       Position: ARM_HALF_SPREAD in hull-X (outboard) from strut centreline.
//     CROSSBEAM — spans diagonally between Boss A and Boss B at the same Z,
//       bridging the chamfered corner of the hull.
//     TWO ARM STRUTS — equal-length diagonals from each boss down to the
//       arm apex (strut junction node).
//
//   Isosceles proof: Boss A is ARM_HALF_SPREAD from apex in hull-Y;
//   Boss B is ARM_HALF_SPREAD from apex in hull-X.  Because |ΔX| = |ΔY| and
//   ΔZ is the same for both, both arm struts have equal length. ✓
//
//   Bottom view (cargo belly corner, looking up):
//
//       hull end-wall    hull side-wall
//             \\                //
//               [A]===========[ B]   ← crossbeam (diagonal across chamfer)
//                  \         /
//                   \  arms /
//                    \     /
//                     [ ● ]          ← strut centreline (apex node)
//                       |
//                       |  main strut
//                       ▼
//                     [foot]
//
//   Side view (45° diagonal from centreline, looking toward corner):
//
//       \\  hull corner
//       /  \\
//     /      [====≈====]  ← crossbeam at side wall
//     ||   /
//     ||  /   ← arm strut (both arms overlap at 45° view, appear as one line)
//     ||
//     ||       ← main vertical strut
//
//   UPPER ARM: Boss A + Boss B at Z = UPPER_BOSS_Z (cargo side wall, above belly).
//     Apex (upper node) at Z = UPPER_APEX_Z (strut top, just below belly).
//   LOWER ARM: Boss A + Boss B at Z = LOWER_BOSS_Z (belly-edge transition).
//     Apex (lower node) at Z = LOWER_APEX_Z (strut, partway down).
//
//   Trapezoidal frame profile in side view (YZ plane at 45° cut):
//     Hull side (end + outboard): UPPER_BOSS_Z − LOWER_BOSS_Z = 65 mm
//     Strut side:                 UPPER_APEX_Z − LOWER_APEX_Z = 40 mm
//     (unequal → confirmed trapezoid, not parallelogram) ✓
//
// Prior revisions superseded:
//   Rev R1.3 (2026-06-15): trapezoidal brace with fore-aft arm spread — SUPERSEDED
//   Rev R1.2 / R1.1 / R1 — pyramid and flat-plate variants — SUPERSEDED
//
// Structural design (see docs/LANDING_GEAR_ANALYSIS.md Rev R1.4 — TODO LG-09):
//   - Design case: Phase 11 AUW 6.90 lbm (3,130 g), 6 ft (1,829 mm) drop.
//   - KE per leg = 124 in-lbf (14.0 J).
//   - Primary load path: foot → main strut → upper arm apex → two arm struts
//     (compression) → hull bosses on end-wall and side-wall.
//   - Arm strut compression margin > 10× (Euler buckling 5,300 N >> 78 N design).
//   - PETG junction nodes (25 % gyroid) crush at ≈ 2× design load.
//   - 1× M3 PA6 nylon bolt per boss (4 per leg) for lateral retention.
//   - Safety cord: 2 mm Dyneema, hub → column bore → boss → anchor post inside hull.
//
// Printable parts:
//   arm_upper : CF-PETG, 0.15 mm, 4 perimeters, 40 % gyroid.  Print flat.
//               4 per aircraft (1 per corner).  Same shape for all 4 corners
//               (isosceles triangle, base ARM_XBEAM_L, equal sides ≈ 77.6 mm).
//   arm_lower : CF-PETG, same.  4 per aircraft.
//               (equal sides ≈ 53.9 mm, same base ARM_XBEAM_L).
//   main_strut: CF-PETG, 4 perimeters, 40 % gyroid.  Print upright.  4/aircraft.
//   node      : PETG 25 % gyroid (crush zone).  2 per corner = 8 per aircraft.
//   boss_face : CF-PETG, integral to cargo shell.  4 orientations (see below).
//   foot      : TPU 95A, 25 % gyroid.  4 per aircraft.
//
// Attribution:
//   Canonical landing leg geometry: Firefly/Serenity (TV/film), Joss Whedon.
//   Reference hull model: misubisu, Thingiverse thing:4677565, CC BY 4.0.
//   <https://www.thingiverse.com/thing:4677565>
//
// Standards applied:
//   Fabrication per CLAUDE.md §Fabrication Standards.
//   Nylon bolt shear per ASTM D638 (Type I, PA6).  Verify before first
//   flight (TODO.md LG-01).
//   Lateral load ±15° per docs/LANDING_GEAR_ANALYSIS.md §5 Rev R1.4.
//
// Usage — set PART to render:
//   PART = "assy"       Full assembly, all 4 corners (hull frame view)
//   PART = "arm_upper"  Upper arm V-brace frame, print orientation (flat)
//   PART = "arm_lower"  Lower arm V-brace frame, print orientation (flat)
//   PART = "main_strut" Main vertical strut, print orientation (upright)
//   PART = "node"       Arm-to-strut junction node, print orientation
//   PART = "boss"       Hull boss cylinder (reference, one example)
//   PART = "foot"       TPU foot pad, print orientation (flat)
//
// STL export commands (from repo root):
//   openscad -o airframe/stls/fuselage/landing-gear/arm_upper_r1.stl \
//     -D 'PART="arm_upper"' airframe/openscad/fuselage/landing_leg_assy.scad
//   openscad -o airframe/stls/fuselage/landing-gear/arm_lower_r1.stl \
//     -D 'PART="arm_lower"' airframe/openscad/fuselage/landing_leg_assy.scad
//   openscad -o airframe/stls/fuselage/landing-gear/main_strut_r1.stl \
//     -D 'PART="main_strut"' airframe/openscad/fuselage/landing_leg_assy.scad
//   openscad -o airframe/stls/fuselage/landing-gear/junct_node_r1.stl \
//     -D 'PART="node"' airframe/openscad/fuselage/landing_leg_assy.scad
//   openscad -o airframe/stls/fuselage/landing-gear/hull_boss_r1.stl \
//     -D 'PART="boss"' airframe/openscad/fuselage/landing_leg_assy.scad
//   openscad -o airframe/stls/fuselage/landing-gear/foot_pad_r1.stl \
//     -D 'PART="foot"' airframe/openscad/fuselage/landing_leg_assy.scad
// ===========================================================================

// ---------------------------------------------------------------------------
// Render control
// ---------------------------------------------------------------------------
PART = "assy";  // see Usage above

// ---------------------------------------------------------------------------
// Arm strut + crossbeam tube parameters (same profile for both)
// ---------------------------------------------------------------------------

ARM_OD      = 12.0;   // mm — arm strut and crossbeam outer diameter
ARM_WALL    =  2.0;   // mm — wall thickness (CF-PETG hollow tube, ID = 8 mm)

// ---------------------------------------------------------------------------
// Main vertical strut parameters
// ---------------------------------------------------------------------------

MAIN_OD     = 18.0;   // mm — main strut outer diameter
MAIN_WALL   =  2.5;   // mm — wall thickness (CF-PETG, ID = 13 mm)

// ---------------------------------------------------------------------------
// Arm-to-strut junction node parameters (PETG crush zone)
// ---------------------------------------------------------------------------

NODE_R      =  9.0;   // mm — junction sphere radius
SOCK_DEPTH  = 11.0;   // mm — arm strut socket bore depth in node
SOCK_CLR    =  0.4;   // mm — total diametral clearance for socket bore
MAIN_SOCK_D = 18.4;   // mm — main strut socket bore diameter (MAIN_OD + CLR)
TETHER_D    =  4.5;   // mm — Dyneema cord axial hole through node

// ---------------------------------------------------------------------------
// Hull boss cylinder parameters (same for all 4 boss orientations)
// ---------------------------------------------------------------------------

BOSS_OD     = 22.0;   // mm — boss outer diameter
BOSS_H      = 30.0;   // mm — boss protrusion from hull face
// Boss bore: ARM_OD + SOCK_CLR = 12.4 mm; wall = (22−12.4)/2 = 4.8 mm
M3_CLR      =  3.4;   // mm — M3 nylon retention bolt clearance hole
ANCHOR_OD   =  5.0;   // mm — Dyneema anchor post OD (inside hull)
ANCHOR_H    =  8.0;   // mm — anchor post height (inside hull, away from face)

// ---------------------------------------------------------------------------
// Foot pad parameters (TPU 95A)
// ---------------------------------------------------------------------------

FOOT_W      = 55.0;   // mm — foot width  (hull X)
FOOT_L      = 55.0;   // mm — foot length (hull Y)
FOOT_H      = 12.0;   // mm — foot height
FOOT_R      =  5.0;   // mm — corner fillet radius
FOOT_SOCK_D = 14.0;   // mm — main strut spigot OD (column bottom inserts here)
FOOT_SOCK_H =  8.0;   // mm — foot socket depth
FOOT_M3_D   =  3.4;   // mm — M3 retention screw clearance
FOOT_M3_P   = 14.0;   // mm — M3 bolt spacing

// ---------------------------------------------------------------------------
// Arm geometry — spread and attachment heights
// ---------------------------------------------------------------------------

// Both bosses of each arm are ARM_HALF_SPREAD from the strut centreline:
//   Boss A: ARM_HALF_SPREAD toward the hull end-wall (fore or aft in hull-Y)
//   Boss B: ARM_HALF_SPREAD outboard (in hull-X × side)
// Because |ΔX| = |ΔY| = ARM_HALF_SPREAD and ΔZ is the same for both,
// both arm struts have equal length → isosceles triangle. ✓
ARM_HALF_SPREAD = 20.0;   // mm

// Z heights (hull frame; positive = above cargo belly):
UPPER_BOSS_Z    = 70.0;   // mm — upper arm boss pair on cargo side wall
LOWER_BOSS_Z    =  5.0;   // mm — lower arm boss pair at belly-edge transition
UPPER_APEX_Z    = -5.0;   // mm — upper arm strut junction (strut top, just below belly)
LOWER_APEX_Z    = -45.0;  // mm — lower arm strut junction (strut lower node)
STRUT_BOT_Z     = -148.0; // mm — foot top face (main strut bottom)

// Derived geometry (documentation):
//   Upper arm strut length: sqrt(20²+20²... no: sqrt(20² + 75²) ≈ 77.6 mm
//     (ΔX or ΔY = ARM_HALF_SPREAD = 20; ΔZ = UPPER_BOSS_Z − UPPER_APEX_Z = 75)
//   Lower arm strut length: sqrt(20² + 50²) ≈ 53.9 mm
//     (ΔZ = LOWER_BOSS_Z − LOWER_APEX_Z = 50)
//   Crossbeam length: sqrt(20²+20²) = 20√2 ≈ 28.3 mm (diagonal across corner)
//   Main strut length: UPPER_APEX_Z − STRUT_BOT_Z = 143 mm
//   Total ground clearance: 148 + FOOT_H = 160 mm (6.3 in)

// ---------------------------------------------------------------------------
// Hull frame corner positions
// ---------------------------------------------------------------------------

// Format: [X_strut, Y_strut, Z=0, side, fa_sign]
//   side    = +1 port (Boss B toward +X), -1 stbd (Boss B toward -X)
//   fa_sign = -1 fore corner (Boss A toward -Y / fore face)
//             +1 aft  corner (Boss A toward +Y / aft  face)
//
// Strut positions set so bosses land on the respective hull faces:
//   Boss A (end-wall): Y_strut + fa_sign * ARM_HALF_SPREAD
//   Boss B (side-wall): X_strut + side   * ARM_HALF_SPREAD
//
// Cargo_Shell extents (hull frame, baked R1):
//   X: -267.0 .. -72.7   Y: -71.5 .. +132.0
//   Port belly edge ≈ X = -72.7; stbd ≈ X = -267.0
//   Fore belly edge ≈ Y = -71.5; aft  ≈ Y = +132.0
//
// With ARM_HALF_SPREAD = 20:
//   Port-fore: Boss A at Y=-71 (≈fore edge), Boss B at X=-73 (≈port edge) ✓
//   Stbd-fore: Boss A at Y=-71 (≈fore edge), Boss B at X=-267 (≈stbd edge) ✓
//   Port-aft:  Boss A at Y=+132(≈aft  edge), Boss B at X=-73 (≈port edge) ✓
//   Stbd-aft:  Boss A at Y=+132(≈aft  edge), Boss B at X=-267 (≈stbd edge) ✓
// Verify exact positions in FreeCAD (TODO.md LG-04).
HULL_ATTACH_POS = [
    [  -93,  -51, 0,  1, -1 ],  // Port-fore (Shepherd's room area)
    [ -247,  -51, 0, -1, -1 ],  // Stbd-fore (Inara's shuttle area)
    [  -93, +112, 0,  1, +1 ],  // Port-aft  (River's room area)
    [ -247, +112, 0, -1, +1 ],  // Stbd-aft  (Simon's medbay area)
];

// ---------------------------------------------------------------------------
// Resolution
// ---------------------------------------------------------------------------
$fn = 48;

// ===========================================================================
// MODULE: tube(len, od, wall)
// Hollow cylindrical tube along +Z from origin, length = len.
// ===========================================================================
module tube(len, od, wall) {
    difference() {
        cylinder(h = len, d = od);
        translate([0, 0, -0.1])
            cylinder(h = len + 0.2, d = od - 2 * wall);
    }
}

// ===========================================================================
// MODULE: strut_between(pt_a, pt_b, od, wall)
// Hollow tube between two arbitrary 3-D points.
// Spherical decomposition aligns local +Z with the connecting vector.
// ===========================================================================
module strut_between(pt_a, pt_b, od, wall) {
    v       = pt_b - pt_a;
    len     = norm(v);
    polar   = atan2(norm([v[0], v[1]]), v[2]);
    azimuth = atan2(v[1], v[0]);
    translate(pt_a)
        rotate([0, 0, azimuth])
        rotate([0, polar, 0])
            tube(len, od, wall);
}

// ===========================================================================
// MODULE: arm_v_brace(boss_a, boss_b, apex)
// One isosceles triangular arm (V-brace):
//   crossbeam  — boss_a to boss_b (diagonal across hull corner)
//   arm strut A — boss_a to apex (equal length as arm strut B)
//   arm strut B — boss_b to apex
// All tubes use ARM_OD and ARM_WALL.
// ===========================================================================
module arm_v_brace(boss_a, boss_b, apex) {
    strut_between(boss_a, boss_b, ARM_OD, ARM_WALL);  // crossbeam
    strut_between(boss_a, apex,   ARM_OD, ARM_WALL);  // arm strut A
    strut_between(boss_b, apex,   ARM_OD, ARM_WALL);  // arm strut B
}

// ===========================================================================
// MODULE: junction_node(boss_a_offset, boss_b_offset)
// Arm-to-strut junction node (PETG crush zone).  Origin = node centre.
//
// The node has:
//   2 arm-strut socket bores (pointing toward Boss A and Boss B)
//   1 main-strut bore (axial, through node in ±Z)
//   1 Dyneema tether hole (axial, same bore as main strut channel)
//
// boss_a_offset and boss_b_offset: vectors from node centre toward each boss.
// Used to orient the two arm socket bores.
// ===========================================================================
module junction_node(boss_a_offset, boss_b_offset) {
    difference() {
        sphere(r = NODE_R);

        // Two arm-strut socket bores
        for (boff = [boss_a_offset, boss_b_offset]) {
            pol = atan2(norm([boff[0], boff[1]]), boff[2]);
            az  = atan2(boff[1], boff[0]);
            rotate([0, 0, az])
            rotate([0, pol, 0])
                translate([0, 0, NODE_R - 0.1])
                    cylinder(h = SOCK_DEPTH + 0.1, d = ARM_OD + SOCK_CLR);
        }

        // Main strut bore (passes through node; strut slides through)
        translate([0, 0, -NODE_R - SOCK_DEPTH + 0.1])
            cylinder(h = 2 * NODE_R + SOCK_DEPTH, d = MAIN_SOCK_D);

        // Tether cord channel (concentric with main bore)
        translate([0, 0, -NODE_R - 0.1])
            cylinder(h = 2 * NODE_R + 0.2, d = TETHER_D);
    }
}

// ===========================================================================
// MODULE: hull_boss_face(face_az)
// Generic hull boss cylinder protrudes from a hull face in the direction
// given by face_az (azimuth angle in hull XY plane, degrees):
//   face_az =   0°  → protrudes in hull +X (out port face, for port Boss B)
//   face_az =  90°  → protrudes in hull +Y (out aft  face, for aft  Boss A)
//   face_az = 180°  → protrudes in hull -X (out stbd face, for stbd Boss B)
//   face_az = 270° (=-90°) → protrudes in hull -Y (out fore face, for fore Boss A)
//
// Origin: centre of the boss top face (flush with hull outer surface).
// Boss cylinder protrudes OUTWARD by BOSS_H from the hull surface.
// Anchor post protrudes INWARD by ANCHOR_H (inside hull for Dyneema).
// ===========================================================================
module hull_boss_face(face_az) {
    bore_d = ARM_OD + SOCK_CLR;  // 12.4 mm — arm strut end inserts from outside

    // Rotate so boss protrudes in the face_az direction (hull XY plane)
    rotate([0, 0, face_az])       // azimuth in hull XY
    rotate([0, -90, 0])           // pivot so +Z (cylinder axis) → +X then rotate to face_az
    difference() {
        union() {
            // Boss body (protrudes outward from hull face, along +Z in local frame)
            cylinder(h = BOSS_H, d = BOSS_OD);
            // Anchor post inside hull (along -Z in local frame)
            translate([0, 0, -ANCHOR_H])
                cylinder(h = ANCHOR_H, d = ANCHOR_OD);
        }

        // Arm strut socket bore (arm inserts from outside; 2 mm solid bearing floor)
        translate([0, 0, 2])
            cylinder(h = BOSS_H, d = bore_d);

        // M3 retention / fuse bolt (transverse — in local Y direction through boss)
        translate([0, -BOSS_OD / 2 - 1, BOSS_H * 0.55])
            rotate([-90, 0, 0])
                cylinder(h = BOSS_OD + 2, d = M3_CLR);

        // Tether cord pass-through (axial, from outside through anchor post)
        translate([0, 0, -ANCHOR_H - 0.1])
            cylinder(h = BOSS_H + ANCHOR_H + 0.2, d = TETHER_D);
    }
}

// ===========================================================================
// MODULE: foot_pad()
// TPU 95A foot pad.  Origin: sole bottom face at Z = 0.
// Printed flat.  Main strut spigot inserts from above into central socket.
// ===========================================================================
module foot_pad() {
    difference() {
        // Rounded rectangular pad body
        hull() {
            for (dx = [-(FOOT_W/2 - FOOT_R), (FOOT_W/2 - FOOT_R)])
                for (dy = [-(FOOT_L/2 - FOOT_R), (FOOT_L/2 - FOOT_R)])
                    translate([dx, dy, 0])
                        cylinder(h = FOOT_H, r = FOOT_R);
        }

        // Main strut spigot socket (from top face down)
        translate([0, 0, FOOT_H - FOOT_SOCK_H + 0.1])
            cylinder(h = FOOT_SOCK_H + 0.1, d = FOOT_SOCK_D);

        // 2× M3 retention screws from sole upward
        for (dx = [-FOOT_M3_P / 2, FOOT_M3_P / 2])
            translate([dx, 0, -0.1])
                cylinder(h = 3.0 + 0.2, d = FOOT_M3_D);
    }
}

// ===========================================================================
// MODULE: one_leg_assembly(corner)
// Full corner V-brace leg assembly for one cargo corner in hull frame.
//
//   corner = [X_strut, Y_strut, 0, side, fa_sign] from HULL_ATTACH_POS
//     side    = +1 port, -1 stbd
//     fa_sign = -1 fore corner, +1 aft corner
//
// Boss positions in hull frame:
//   Boss A (end-wall):  [X_c,                    Y_c + fa*SPREAD, Z_boss]
//   Boss B (side-wall): [X_c + side*SPREAD,       Y_c,            Z_boss]
// ===========================================================================
module one_leg_assembly(corner) {
    cx      = corner[0];
    cy      = corner[1];
    side    = corner[3];
    fa      = corner[4];   // fore/aft sign: -1 = fore, +1 = aft

    sp = ARM_HALF_SPREAD;

    // --- Boss positions (at hull faces, same XY for upper and lower) ---
    // Boss A: on hull end-wall (fore or aft face)
    ba_pos = [cx,          cy + fa * sp, 0];  // XY position; Z added per arm below
    // Boss B: on hull side-wall (port or stbd face)
    bb_pos = [cx + side * sp, cy,        0];  // XY position

    // Boss A faces outward from the end wall:
    //   fore corner (fa=-1): outward normal = -Y → face_az = 270° (= -90°)
    //   aft  corner (fa=+1): outward normal = +Y → face_az =  90°
    ba_az = (fa == -1) ? 270 : 90;

    // Boss B faces outward from the side wall:
    //   port (side=+1): outward normal = +X → face_az = 0°
    //   stbd (side=-1): outward normal = -X → face_az = 180°
    bb_az = (side == 1) ? 0 : 180;

    // --- Apex (junction node) positions ---
    upper_apex = [cx, cy, UPPER_APEX_Z];
    lower_apex = [cx, cy, LOWER_APEX_Z];

    // --- Boss positions for each arm (inject the arm Z) ---
    upper_ba = [ba_pos[0], ba_pos[1], UPPER_BOSS_Z];
    upper_bb = [bb_pos[0], bb_pos[1], UPPER_BOSS_Z];
    lower_ba = [ba_pos[0], ba_pos[1], LOWER_BOSS_Z];
    lower_bb = [bb_pos[0], bb_pos[1], LOWER_BOSS_Z];

    // --- Upper V-brace arm (CF-PETG) ---
    color("DimGray", 0.9)
        arm_v_brace(upper_ba, upper_bb, upper_apex);

    // --- Lower V-brace arm (CF-PETG) ---
    color("DimGray", 0.9)
        arm_v_brace(lower_ba, lower_bb, lower_apex);

    // --- Main vertical strut (CF-PETG) ---
    // Continuous from upper apex to foot top; nodes ring around it.
    color("DimGray", 0.85)
        strut_between(upper_apex, [cx, cy, STRUT_BOT_Z], MAIN_OD, MAIN_WALL);

    // --- Junction nodes (PETG crush zone) ---
    // Each node knows the offsets from itself to its two bosses.
    color("LightSlateGray", 0.9) {
        // Upper node
        translate(upper_apex)
            junction_node(
                upper_ba - upper_apex,
                upper_bb - upper_apex
            );
        // Lower node
        translate(lower_apex)
            junction_node(
                lower_ba - lower_apex,
                lower_bb - lower_apex
            );
    }

    // --- Hull boss cylinders ---
    // Upper arm bosses (on side wall above belly)
    color("OliveDrab", 0.65) {
        translate(upper_ba) hull_boss_face(ba_az);
        translate(upper_bb) hull_boss_face(bb_az);
        // Lower arm bosses (at belly-edge transition)
        translate(lower_ba) hull_boss_face(ba_az);
        translate(lower_bb) hull_boss_face(bb_az);
    }

    // --- TPU foot pad ---
    color("Black", 0.85)
        translate([cx, cy, STRUT_BOT_Z - FOOT_H])
            foot_pad();
}

// ===========================================================================
// MODULE: assembly()
// All 4 leg assemblies in hull frame — layout verification.
// ===========================================================================
module assembly() {
    // Cargo belly reference slab (semi-transparent)
    color("SaddleBrown", 0.10)
        translate([-300, -100, -1])
            cube([270, 250, 1]);

    for (corner = HULL_ATTACH_POS)
        one_leg_assembly(corner);
}

// ===========================================================================
// Entry point
// ===========================================================================

if (PART == "assy") {

    assembly();

} else if (PART == "arm_upper") {

    // Upper V-brace arm, print orientation flat (triangle in printer XY plane).
    // Triangle: base (crossbeam) = 28.3 mm (diagonal); equal sides ≈ 77.6 mm.
    // Place crossbeam ends at ±half-base in printer-X; apex in printer-Y.
    half_x   = ARM_HALF_SPREAD;   // 20 mm
    half_y   = ARM_HALF_SPREAD;   // 20 mm (equal for isosceles, different face offsets)
    dz_boss  = UPPER_BOSS_Z - UPPER_APEX_Z;   // 75 mm height to bosses
    // Boss A offset from apex (in local arm print frame):
    b_a = [  half_x,  0,       dz_boss];  // A = fore/aft offset (mapped to print-X)
    b_b = [0,         half_y,  dz_boss];  // B = lateral offset (mapped to print-Y)
    arm_v_brace(b_a, b_b, [0, 0, 0]);

} else if (PART == "arm_lower") {

    // Lower V-brace arm, print orientation flat.
    // Triangle: base ≈ 28.3 mm; equal sides ≈ 53.9 mm.
    half_x   = ARM_HALF_SPREAD;
    half_y   = ARM_HALF_SPREAD;
    dz_boss  = LOWER_BOSS_Z - LOWER_APEX_Z;   // 50 mm
    b_a = [ half_x, 0,      dz_boss];
    b_b = [0,       half_y, dz_boss];
    arm_v_brace(b_a, b_b, [0, 0, 0]);

} else if (PART == "main_strut") {

    // Main vertical strut, print upright (Z is print direction).
    // Length = 143 mm; bottom end has reduced-OD spigot for foot socket.
    strut_len = UPPER_APEX_Z - STRUT_BOT_Z;   // 143 mm

    difference() {
        tube(strut_len, MAIN_OD, MAIN_WALL);
        // Foot spigot: cut outer profile to FOOT_SOCK_D at bottom end
        translate([0, 0, -0.1])
            difference() {
                cylinder(h = FOOT_SOCK_H + 0.1, d = MAIN_OD + 0.2);
                cylinder(h = FOOT_SOCK_H + 0.2, d = FOOT_SOCK_D);
            }
    }

} else if (PART == "node") {

    // Representative junction node (uses upper arm angles).
    sp = ARM_HALF_SPREAD;
    dz = UPPER_BOSS_Z - UPPER_APEX_Z;
    junction_node([sp, 0, dz], [0, sp, dz]);

} else if (PART == "boss") {

    // One hull boss, protruding in +X direction (port face example).
    hull_boss_face(0);

} else if (PART == "foot") {

    // TPU foot pad, print flat (sole on printer bed).
    foot_pad();

}
