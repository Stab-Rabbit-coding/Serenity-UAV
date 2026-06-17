// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame: X = +port, Y = +aft, Z = +dorsal (up).
//   Landing gear parts are in hull frame; NOT primary-component STLs;
//   do NOT bake with bake_hull_frame.py.
// ===========================================================================
// ===========================================================================
// landing_leg_assy.scad
// Serenity UAV — Rev R1.5 — Landing Leg Assembly (Corner Single-Arm Bracket)
// ===========================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-06-16
// Revision: Rev R1.5
//
// Description
// -----------
// Parametric landing leg assembly for the Serenity UAV.  Four leg assemblies
// attach to the cargo section belly corners, one per corner.  Geometry
// matches the canonical reference part `airframe/freecad/assembly/strong-leg.stl`
// (author-modeled in `SerenityAssembly.FCStd`), reverse-derived to hull-frame
// dimensions and confirmed accurate for ground clearance (2026-06-16).
//
// Canonical geometry — corner single-arm bracket:
//
//   Each corner has ONE MAIN VERTICAL STRUT hanging a short distance below
//   the belly, rising through a small foot pad to ground.  The strut top
//   passes UP THROUGH the belly into the cargo bay interior to a single
//   JUNCTION NODE, from which ONE V-ARM (two struts + crossbeam) reaches
//   UP AND OUTWARD to two boss attachments on the cargo side wall, well
//   above the belly.  This is the Serenity canonical "low leg, tall
//   bracket" silhouette — the ship sits close to the ground; the structural
//   leverage comes from the high side-wall attachment, not strut length.
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
//   Side view (45° diagonal from centreline, looking toward corner):
//
//       hull side wall
//             ___
//            /   \   ← boss (protrudes from wall, Z = UPPER_BOSS_Z)
//           /
//          /        ← arm strut (both arms overlap at 45° view)
//         /
//        ●           ← junction node, Z = UPPER_APEX_Z (INSIDE cargo bay,
//        |              above belly — strut passes up through belly to here)
//        |
//   ─────┼─────       ← cargo belly, Z = 0
//        |
//       [foot]        ← Z = STRUT_BOT_Z (just below belly); foot cap below
//        ▼ ground      that.  Ground clearance = |STRUT_BOT_Z| + FOOT_H.
//
//   Bottom view (cargo belly corner, looking up):
//
//       hull end-wall    hull side-wall
//             \\                //
//               [A]===========[ B]   ← crossbeam (diagonal across chamfer)
//                  \         /
//                   \  arm  /
//                    \     /
//                     [ ● ]          ← junction node (inside cargo bay)
//                       |
//                       |  main strut (passes up through belly bore)
//                       ▼
//                     [foot]
//
// Ground clearance (Rev R1.5 — Serenity-accurate, confirmed 2026-06-16):
//   |STRUT_BOT_Z| + FOOT_H = 7 + 10 = 17 mm (0.67 in).
//   This is intentionally LOW — matches the canonical Serenity silhouette,
//   which sits close to the ground.  The leg's structural strength comes
//   from the tall side-wall attachment (UPPER_BOSS_Z = 60 mm above belly),
//   not from strut length.  Confirmed by author 2026-06-16; supersedes the
//   160 mm clearance figure carried in Rev R1–R1.4 (those revisions assumed
//   a tall hanging strut design that did not match the canonical hull).
//
// OPERATIONAL CONSTRAINT — cargo bay clamshell doors (2026-06-16):
//   With only 17 mm ground clearance, the cargo doors (Rev R1a,
//   ~12 mm panel thickness, hinged at hull centreline X ≈ -170 mm) can
//   strike the ground if opened to any angle other than fully CLOSED (0°)
//   or fully OPEN (180°, panel horizontal, clears ground by ≈ 5 mm).  At
//   intermediate angles the door tip swings below ground level before
//   reaching 180°.  FLIGHT RULE: cargo doors shall be commanded to 0° or
//   180° ONLY when the UAV is on the ground; partial-open ground operation
//   is prohibited.  See TODO.md LG-10.
//
// Prior revisions superseded:
//   Rev R1.4 (2026-06-15): two-arm (upper+lower) corner V-brace,
//     160 mm hanging-strut ground clearance — SUPERSEDED.  Did not match
//     the canonical Serenity leg silhouette in strong-leg.stl.
//   Rev R1.3 / R1.2 / R1.1 / R1 — trapezoidal, pyramid, flat-plate
//     variants — SUPERSEDED.
//
// Structural design (see docs/LANDING_GEAR_ANALYSIS.md Rev R1.5):
//   - Design case: Phase 11 AUW 6.90 lbm (3,130 g), 6 ft (1,829 mm) drop.
//   - KE per leg = 124 in-lbf (14.0 J).
//   - Primary load path: foot → main strut → junction node (inside cargo
//     bay) → two arm struts (compression) → hull bosses on end-wall and
//     side-wall.
//   - Single-arm (2 struts/leg) carries 2× the per-strut load of the
//     superseded two-arm (4 struts/leg) design; margins recomputed in
//     LANDING_GEAR_ANALYSIS.md Rev R1.5 and remain > 4× on all checks
//     (shorter arm struts improve buckling margin substantially).
//   - PETG junction node (25 % gyroid) crushes at ≈ 2× design load.
//   - 1× M3 PA6 nylon bolt per boss (2 per leg) for lateral retention.
//   - Safety cord: 2 mm Dyneema, hub → column bore → boss → anchor post inside hull.
//
// Printable parts:
//   arm       : CF-PETG, 0.15 mm, 4 perimeters, 40 % gyroid.  Print flat.
//               4 per aircraft (1 per corner).  Isosceles triangle, base
//               ARM_XBEAM_L ≈ 28.3 mm, equal sides ≈ 37.7 mm.
//   main_strut: CF-PETG, 4 perimeters, 40 % gyroid.  Print upright.  4/aircraft.
//   node      : PETG 25 % gyroid (crush zone).  1 per corner = 4 per aircraft.
//   boss_face : CF-PETG, integral to cargo shell.  2 per corner = 8 per aircraft.
//   foot      : TPU 95A, 25 % gyroid.  4 per aircraft.
//
// Attribution:
//   Canonical landing leg geometry: Firefly/Serenity (TV/film), Joss Whedon;
//   author-modeled reference part strong-leg.stl (S. Griffing, 2026-06-16).
//   Reference hull model: misubisu, Thingiverse thing:4677565, CC BY 4.0.
//   <https://www.thingiverse.com/thing:4677565>
//
// Standards applied:
//   Fabrication per CLAUDE.md §Fabrication Standards.
//   Nylon bolt shear per ASTM D638 (Type I, PA6).  Verify before first
//   flight (TODO.md LG-01).
//   Lateral load ±15° per docs/LANDING_GEAR_ANALYSIS.md §5 Rev R1.5.
//
// Usage — set PART to render:
//   PART = "assy"       Full assembly, all 4 corners (hull frame view)
//   PART = "hull_legs"  Same as "assy" but without reference belly slab —
//                        used for STL export / render-script import.
//   PART = "arm"        V-brace arm, print orientation (flat)
//   PART = "main_strut" Main vertical strut, print orientation (upright)
//   PART = "node"       Arm-to-strut junction node, print orientation
//   PART = "boss"       Hull boss cylinder (reference, one example)
//   PART = "foot"       TPU foot cap, print orientation (flat)
//
// STL export commands (from repo root):
//   openscad -o airframe/stls/fuselage/landing-gear/landing_legs_hull_r1.stl \
//     -D 'PART="hull_legs"' airframe/openscad/fuselage/landing_leg_assy.scad
//   openscad -o airframe/stls/fuselage/landing-gear/arm_r1.stl \
//     -D 'PART="arm"' airframe/openscad/fuselage/landing_leg_assy.scad
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
SOCK_DEPTH  = 10.0;   // mm — arm strut socket bore depth in node
SOCK_CLR    =  0.4;   // mm — total diametral clearance for socket bore
MAIN_SOCK_D = 18.4;   // mm — main strut socket bore diameter (MAIN_OD + CLR)
TETHER_D    =  4.5;   // mm — Dyneema cord axial hole through node

// ---------------------------------------------------------------------------
// Hull boss cylinder parameters (same for all 4 boss orientations)
// ---------------------------------------------------------------------------

BOSS_OD     = 22.0;   // mm — boss outer diameter
BOSS_H      = 20.0;   // mm — boss protrusion from hull face (reduced from
                       //      R1.4's 30 mm to suit the shorter R1.5 arm struts)
// Boss bore: ARM_OD + SOCK_CLR = 12.4 mm; wall = (22−12.4)/2 = 4.8 mm
M3_CLR      =  3.4;   // mm — M3 nylon retention bolt clearance hole
ANCHOR_OD   =  5.0;   // mm — Dyneema anchor post OD (inside hull)
ANCHOR_H    =  8.0;   // mm — anchor post height (inside hull, away from face)

// ---------------------------------------------------------------------------
// Foot cap parameters (TPU 95A) — small rounded cap, not a wide pad.
// Matches the compact foot silhouette of strong-leg.stl.
// ---------------------------------------------------------------------------

FOOT_D      = 25.0;   // mm — foot cap outer diameter
FOOT_H      = 10.0;   // mm — foot cap height
FOOT_SOCK_D = 14.0;   // mm — main strut spigot OD (column bottom inserts here)
FOOT_SOCK_H =  6.0;   // mm — foot socket depth

// ---------------------------------------------------------------------------
// Arm geometry — spread and attachment heights
// ---------------------------------------------------------------------------

// Both bosses are ARM_HALF_SPREAD from the strut centreline:
//   Boss A: ARM_HALF_SPREAD toward the hull end-wall (fore or aft in hull-Y)
//   Boss B: ARM_HALF_SPREAD outboard (in hull-X × side)
// Because |ΔX| = |ΔY| = ARM_HALF_SPREAD and ΔZ is the same for both,
// both arm struts have equal length → isosceles triangle. ✓
ARM_HALF_SPREAD = 20.0;   // mm

// Z heights (hull frame; positive = above cargo belly).  Derived from
// measured placement of strong-leg.stl in SerenityAssembly.FCStd
// (Union003 instance, hull-frame back-transform, 2026-06-16):
//   measured boss Z ≈ +55..+63 mm  → UPPER_BOSS_Z = 60 mm (mid-range)
//   measured junction Z ≈ +28 mm   → UPPER_APEX_Z = 28 mm
//   measured foot-top Z ≈ -7.7 mm  → STRUT_BOT_Z = -7 mm
UPPER_BOSS_Z    =  60.0;  // mm — arm boss pair on cargo side wall
UPPER_APEX_Z    =  28.0;  // mm — arm strut junction; INSIDE cargo bay,
                           //      above the belly (strut passes up through
                           //      a belly bore to reach this node — see
                           //      TODO.md LG-02a)
STRUT_BOT_Z     =  -7.0;  // mm — foot-cap top face (main strut bottom)

// Derived geometry (documentation):
//   Arm strut length: sqrt(20² + 32²) ≈ 37.7 mm
//     (ΔX or ΔY = ARM_HALF_SPREAD = 20; ΔZ = UPPER_BOSS_Z − UPPER_APEX_Z = 32)
//   Crossbeam length: sqrt(20²+20²) = 20√2 ≈ 28.3 mm (diagonal across corner)
//   Main strut length: UPPER_APEX_Z − STRUT_BOT_Z = 35 mm
//   Ground clearance: |STRUT_BOT_Z| + FOOT_H = 7 + 10 = 17 mm (0.67 in)
//     — confirmed Serenity-accurate by author, 2026-06-16.

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

    // Rotate so boss protrudes in the face_az direction (hull XY plane).
    // rotate([0,90,0]) maps local +Z (cylinder axis) -> local +X; the
    // subsequent rotate([0,0,face_az]) then points +X at (cos,sin)(face_az).
    // Verified empirically 2026-06-16 against exported STL bounds.
    rotate([0, 0, face_az])       // azimuth in hull XY
    rotate([0, 90, 0])            // pivot so +Z (cylinder axis) → +X
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
// MODULE: foot_cap()
// TPU 95A foot cap.  Origin: sole bottom face at Z = 0.
// Printed flat.  Main strut spigot inserts from above into central socket.
// Small rounded cap (not a wide pad) — matches strong-leg.stl silhouette.
// ===========================================================================
module foot_cap() {
    difference() {
        cylinder(h = FOOT_H, d = FOOT_D);

        // Main strut spigot socket (from top face down)
        translate([0, 0, FOOT_H - FOOT_SOCK_H + 0.1])
            cylinder(h = FOOT_SOCK_H + 0.1, d = FOOT_SOCK_D);
    }
}

// ===========================================================================
// MODULE: one_leg_assembly(corner)
// Full corner single-arm leg assembly for one cargo corner in hull frame.
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

    // --- Boss positions (at hull faces) ---
    // Boss A: on hull end-wall (fore or aft face)
    ba_xy = [cx,          cy + fa * sp];
    // Boss B: on hull side-wall (port or stbd face)
    bb_xy = [cx + side * sp, cy        ];

    // Boss A faces outward from the end wall:
    //   fore corner (fa=-1): outward normal = -Y → face_az = 270° (= -90°)
    //   aft  corner (fa=+1): outward normal = +Y → face_az =  90°
    ba_az = (fa == -1) ? 270 : 90;

    // Boss B faces outward from the side wall:
    //   port (side=+1): outward normal = +X → face_az = 0°
    //   stbd (side=-1): outward normal = -X → face_az = 180°
    bb_az = (side == 1) ? 0 : 180;

    // --- Apex (junction node) position — inside cargo bay, above belly ---
    apex = [cx, cy, UPPER_APEX_Z];

    // --- Boss 3-D positions ---
    boss_a = [ba_xy[0], ba_xy[1], UPPER_BOSS_Z];
    boss_b = [bb_xy[0], bb_xy[1], UPPER_BOSS_Z];

    // --- V-brace arm (CF-PETG), entirely inside the cargo bay ---
    color("DimGray", 0.9)
        arm_v_brace(boss_a, boss_b, apex);

    // --- Main vertical strut (CF-PETG) ---
    // Passes up through a belly bore from the foot-cap top to the apex.
    color("DimGray", 0.85)
        strut_between(apex, [cx, cy, STRUT_BOT_Z], MAIN_OD, MAIN_WALL);

    // --- Junction node (PETG crush zone) ---
    color("LightSlateGray", 0.9)
        translate(apex)
            junction_node(boss_a - apex, boss_b - apex);

    // --- Hull boss cylinders ---
    color("OliveDrab", 0.65) {
        translate(boss_a) hull_boss_face(ba_az);
        translate(boss_b) hull_boss_face(bb_az);
    }

    // --- TPU foot cap ---
    color("Black", 0.85)
        translate([cx, cy, STRUT_BOT_Z - FOOT_H])
            foot_cap();
}

// ===========================================================================
// MODULE: assembly()
// All 4 leg assemblies in hull frame — layout verification (with reference
// belly slab for visual context).
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
// MODULE: hull_legs_only()
// Four landing legs positioned in hull frame with no reference geometry.
// Exported as a single STL for assembly visualisation and render scripts.
// The result is in hull-frame coordinates (X=+port, Y=+aft, Z=+dorsal).
// ===========================================================================
module hull_legs_only() {
    for (corner = HULL_ATTACH_POS)
        one_leg_assembly(corner);
}

// ===========================================================================
// Entry point
// ===========================================================================

if (PART == "assy") {

    assembly();

} else if (PART == "hull_legs") {

    // All 4 legs in hull-frame coordinates — use for assembly STL export and renders.
    hull_legs_only();

} else if (PART == "arm") {

    // V-brace arm, print orientation flat (triangle in printer XY plane).
    // Triangle: base (crossbeam) = 28.3 mm (diagonal); equal sides ≈ 37.7 mm.
    half_x   = ARM_HALF_SPREAD;   // 20 mm
    half_y   = ARM_HALF_SPREAD;   // 20 mm (equal for isosceles, different face offsets)
    dz_boss  = UPPER_BOSS_Z - UPPER_APEX_Z;   // 32 mm height to bosses
    // Boss A offset from apex (in local arm print frame):
    b_a = [  half_x,  0,       dz_boss];  // A = fore/aft offset (mapped to print-X)
    b_b = [0,         half_y,  dz_boss];  // B = lateral offset (mapped to print-Y)
    arm_v_brace(b_a, b_b, [0, 0, 0]);

} else if (PART == "main_strut") {

    // Main vertical strut, print upright (Z is print direction).
    // Length = 35 mm; bottom end has reduced-OD spigot for foot socket.
    strut_len = UPPER_APEX_Z - STRUT_BOT_Z;   // 35 mm

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

    // Representative junction node (uses arm angles).
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
