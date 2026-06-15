// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame: X = +port, Y = +aft, Z = +dorsal (up).
//   Landing gear parts are in hull frame; NOT primary-component STLs;
//   do NOT bake with bake_hull_frame.py.
// ===========================================================================
// ===========================================================================
// landing_leg_assy.scad
// Serenity UAV — Rev R1.3 — Landing Leg Assembly (Trapezoidal Brace Frame)
// ===========================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-06-15
// Revision: Rev R1.3
//
// Description
// -----------
// Parametric landing leg assembly for the Serenity UAV.  Four leg assemblies
// attach to the belly of the cargo section, one at each corner.
//
// Canonical geometry — trapezoidal brace frame per leg:
//
//   Each corner has ONE MAIN VERTICAL STRUT (the leg) hanging below the
//   cargo belly, braced by TWO ISOSCELES TRIANGULAR ARMS to the hull:
//
//   UPPER ARM: connects at the TOP of the strut (Z ≈ 0, hull belly level).
//     Its two hull boss points are on the CARGO SIDE WALL at height
//     UPPER_BOSS_Z above the belly — noticeably above the belly edge.
//     The arm is an isosceles triangle (V-shape): two equal arm struts
//     descend from the fore and aft hull bosses to the strut-top junction,
//     with a horizontal crossbeam (XBEAM) spanning the two hull bosses.
//
//   LOWER ARM: connects to the strut at depth LOWER_APEX_Z below the belly.
//     Its hull boss points are at LOWER_BOSS_Z (at or just above the
//     belly-to-side-wall transition).  Same isosceles V geometry.
//
//   Side-view profile (looking along hull-X, YZ plane):
//
//     ┌── hull side wall (Z = UPPER_BOSS_Z) ──── strut top (Z = UPPER_APEX_Z)
//     │                                                    │
//     │   trapezoidal frame                                │ (main strut)
//     │                                                    │
//     └── hull belly edge (Z = LOWER_BOSS_Z) ── strut node (Z = LOWER_APEX_Z)
//                                                          │
//                                                          │ (strut to foot)
//                                                          ▼
//                                                        foot
//
//   Front-view profile (looking along hull-Y, XZ plane):
//     Shows the isosceles triangle of each arm (V-shape opening upward
//     to the hull, apex downward at strut junction).
//
// Isosceles property:
//   Boss pairs are centred on the corner-centre Y.  The strut junction
//   lies on the Y perpendicular bisector of each boss pair.  Therefore
//   both arm struts from bosses to junction are equal length. ✓
//
// Rev R1.2 (prior): crossbeams added to 4-strut pyramid — SUPERSEDED.
// Rev R1.1 (prior): 4-strut pyramid — SUPERSEDED.
// Rev R1   (prior): flat-plate cantilever — SUPERSEDED.
//
// Structural design (see docs/LANDING_GEAR_ANALYSIS.md Rev R1.3):
//   - Design case: Phase 11 AUW 6.90 lbm (3,130 g), 6 ft (1,829 mm) drop.
//   - KE per leg = 124 in-lbf (14.0 J).
//   - Under vertical impact: load path = foot → main strut (compression)
//     → upper arm junction → upper arm struts + lower arm brace (shear +
//     compression) → 4 hull bosses.
//   - Main strut Euler buckling (OD=18, wall=2.5, L=143mm): P_crit ≫ design.
//   - Arm strut compression margin > 10×.
//   - PETG junction nodes (25 % gyroid) act as crush zones.
//   - 1× M3 PA6 nylon bolt per boss (4 total) for lateral retention.
//   - Safety cord: 2 mm Dyneema from strut top through hull to anchor post.
//
// Printable parts:
//   arm_upper : CF-PETG, 0.15 mm, 4 perimeters, 40 % gyroid.
//               Print lying flat (triangle in XY plane).
//               2 per aircraft (one upper arm per corner; but pairs at each
//               corner are different orientations, so print in sets).
//               Note: all 4 upper arms are the same shape (isosceles
//               triangle, base ARM_SPREAD_Y, sides UPPER_ARM_L each).
//   arm_lower : CF-PETG, same settings.  Print lying flat.
//               All 4 lower arms are the same shape (smaller triangle).
//   main_strut: CF-PETG, 0.15 mm, 4 perimeters, 40 % gyroid.  Print upright.
//               4 per aircraft.
//   node      : PETG (crush zone), 25 % gyroid.  Print upright.
//               8 per aircraft (upper + lower arm junction per corner × 4).
//   boss_side : CF-PETG, integral to cargo shell (side wall).  PART="boss_side".
//               8 per aircraft (fore + aft, per upper arm × 4 corners).
//   boss_belly: CF-PETG, integral to cargo shell (belly edge).  PART="boss_belly".
//               8 per aircraft (fore + aft, per lower arm × 4 corners).
//   foot      : TPU 95A, 0.20 mm, 25 % gyroid.  Print flat.  4 per aircraft.
//
// Assembly note:
//   Each isosceles arm is a 3-piece printed set: 2 arm struts + 1 crossbeam,
//   joined at the boss cylinders with thin CA + M3 retention bolt.  The strut
//   junction nodes (PETG) receive the two arm strut ends in socket bores.
//
// Attribution:
//   Geometry: canonical Serenity landing leg, Firefly/Serenity (TV/film,
//   Joss Whedon, creator).
//   Reference hull: misubisu, Thingiverse thing:4677565, CC BY 4.0.
//   <https://www.thingiverse.com/thing:4677565>
//
// Standards applied:
//   Fabrication per CLAUDE.md §Fabrication Standards.
//   Nylon bolt shear per ASTM D638 (Type I, PA6); verification before
//   first flight (TODO.md LG-01).
//   Lateral load ±15° per docs/LANDING_GEAR_ANALYSIS.md §5 Rev R1.3.
//
// Usage — set PART to render:
//   PART = "assy"       Full assembly, all 4 corners (hull frame)
//   PART = "arm_upper"  Upper arm frame, print orientation (flat)
//   PART = "arm_lower"  Lower arm frame, print orientation (flat)
//   PART = "main_strut" Main vertical strut, print orientation (upright)
//   PART = "node"       Arm-to-strut junction node, print orientation
//   PART = "boss_side"  Side-wall boss cylinder, reference only
//   PART = "boss_belly" Belly-edge boss cylinder, reference only
//   PART = "foot"       TPU foot pad, print orientation (flat)
//
// STL export commands (run from repo root):
//   openscad -o airframe/stls/fuselage/landing-gear/arm_upper_r1.stl \
//     -D 'PART="arm_upper"' airframe/openscad/fuselage/landing_leg_assy.scad
//   openscad -o airframe/stls/fuselage/landing-gear/arm_lower_r1.stl \
//     -D 'PART="arm_lower"' airframe/openscad/fuselage/landing_leg_assy.scad
//   openscad -o airframe/stls/fuselage/landing-gear/main_strut_r1.stl \
//     -D 'PART="main_strut"' airframe/openscad/fuselage/landing_leg_assy.scad
//   openscad -o airframe/stls/fuselage/landing-gear/junct_node_r1.stl \
//     -D 'PART="node"' airframe/openscad/fuselage/landing_leg_assy.scad
//   openscad -o airframe/stls/fuselage/landing-gear/boss_side_r1.stl \
//     -D 'PART="boss_side"' airframe/openscad/fuselage/landing_leg_assy.scad
//   openscad -o airframe/stls/fuselage/landing-gear/boss_belly_r1.stl \
//     -D 'PART="boss_belly"' airframe/openscad/fuselage/landing_leg_assy.scad
//   openscad -o airframe/stls/fuselage/landing-gear/foot_pad_r1.stl \
//     -D 'PART="foot"' airframe/openscad/fuselage/landing_leg_assy.scad
// ===========================================================================

// ---------------------------------------------------------------------------
// Render control
// ---------------------------------------------------------------------------

PART = "assy";  // see Usage above; override with -D 'PART="..."'

// ---------------------------------------------------------------------------
// Arm strut + crossbeam parameters (same tube profile for both)
// ---------------------------------------------------------------------------

ARM_OD      = 12.0;  // mm — arm strut and crossbeam outer diameter
ARM_WALL    =  2.0;  // mm — wall thickness (CF-PETG hollow tube)
// Inner diameter: 12 − 2×2 = 8 mm

// ---------------------------------------------------------------------------
// Main vertical strut parameters
// ---------------------------------------------------------------------------

MAIN_OD     = 18.0;  // mm — main strut outer diameter
MAIN_WALL   =  2.5;  // mm — main strut wall thickness (CF-PETG)
// Inner diameter: 18 − 2×2.5 = 13 mm

// ---------------------------------------------------------------------------
// Arm-to-strut junction node parameters
// ---------------------------------------------------------------------------

NODE_R      =  9.0;  // mm — junction sphere radius (PETG crush zone)
SOCK_DEPTH  = 11.0;  // mm — arm strut socket depth in node
SOCK_CLR    =  0.4;  // mm — total diametral clearance for socket bore
MAIN_SOCK_D = 18.4;  // mm — main strut socket bore diameter (MAIN_OD + 0.4)

// Dyneema tether hole through node (cord routes along main strut bore)
TETHER_D    =  4.5;  // mm

// ---------------------------------------------------------------------------
// Hull boss cylinder parameters (used for both side-wall and belly bosses)
// ---------------------------------------------------------------------------

BOSS_OD     = 22.0;  // mm — boss outer diameter
BOSS_H      = 30.0;  // mm — boss protrusion from hull surface
// Boss bore: ARM_OD + SOCK_CLR = 12.4 mm (arm strut end inserts into boss)
// Boss wall: (22 − 12.4) / 2 = 4.8 mm (CF-PETG, adequate bearing wall)

M3_CLR      =  3.4;  // mm — M3 clearance hole (retention bolt)
ANCHOR_OD   =  5.0;  // mm — Dyneema anchor post OD (inside hull, above boss)
ANCHOR_H    =  8.0;  // mm — anchor post height

// ---------------------------------------------------------------------------
// Foot pad parameters (TPU 95A)
// ---------------------------------------------------------------------------

FOOT_W      = 55.0;  // mm — foot width (hull X)
FOOT_L      = 55.0;  // mm — foot length (hull Y)
FOOT_H      = 12.0;  // mm — foot height (TPU 95A)
FOOT_R      =  5.0;  // mm — corner fillet radius
SOCK_MAIN_D = 14.0;  // mm — main strut plug OD (strut bottom end inserts into foot)
SOCK_MAIN_H =  8.0;  // mm — socket depth in foot
FOOT_M3_D   =  3.4;  // mm — M3 foot-retention screw clearance
FOOT_M3_P   = 14.0;  // mm — bolt spacing

// ---------------------------------------------------------------------------
// Trapezoidal brace geometry — arm attachment heights and fore-aft spread
// ---------------------------------------------------------------------------

// Fore-aft spread of boss pairs (all bosses centred on corner-centre Y;
// each boss pair is ±ARM_SPREAD_Y/2 from this centre in hull-Y).
ARM_SPREAD_Y  = 50.0;   // mm — crossbeam length (same for both arms)

// Heights of arm hull attachments (in hull-Z, above cargo belly at Z = 0).
// UPPER_BOSS_Z: side-wall bosses, must clear the belly shell fillet.
// LOWER_BOSS_Z: belly-edge bosses, just above the belly-to-side transition.
UPPER_BOSS_Z  = 70.0;   // mm above cargo belly  (on cargo side wall)
LOWER_BOSS_Z  =  5.0;   // mm above cargo belly  (belly-edge transition)

// Heights of arm-to-strut junctions in hull-Z (both negative = below belly).
// UPPER_APEX_Z: where upper arm meets top of main strut.
// LOWER_APEX_Z: where lower arm meets the strut partway down.
UPPER_APEX_Z  = -5.0;   // mm below belly (upper arm strut-junction)
LOWER_APEX_Z  = -45.0;  // mm below belly (lower arm strut-junction)

// Bottom of main strut (top face of foot pad).
STRUT_BOT_Z   = -148.0; // mm below belly (foot top; = LOWER_APEX_Z − 103 mm)

// Resulting geometry (for documentation / verification):
//   Upper arm strut length (boss to apex):
//     L_upper = sqrt((ARM_SPREAD_Y/2)² + (UPPER_BOSS_Z − UPPER_APEX_Z)²)
//             = sqrt(25² + 75²) = sqrt(6250) ≈ 79.1 mm
//   Lower arm strut length:
//     L_lower = sqrt((ARM_SPREAD_Y/2)² + (LOWER_APEX_Z − LOWER_BOSS_Z)²)
//             = sqrt(25² + 50²) = sqrt(3125) ≈ 55.9 mm
//   Main strut length (upper apex to foot top):
//     L_main = UPPER_APEX_Z − STRUT_BOT_Z = −5 − (−148) = 143 mm
//   Total ground clearance: 148 + FOOT_H = 148 + 12 = 160 mm (6.3 in)
//   Trapezoidal frame side lengths:
//     Hull side (left): UPPER_BOSS_Z − LOWER_BOSS_Z = 65 mm
//     Strut side (right): UPPER_APEX_Z − LOWER_APEX_Z = 40 mm (trapezoid ≠ parallelogram) ✓

// ---------------------------------------------------------------------------
// Hull frame corner positions
// ---------------------------------------------------------------------------

// Each corner = [X_centre, Y_centre, Z=0, side]
//   side = +1 port (hull +X is outboard); -1 stbd (hull -X is outboard)
//
// Cargo_Shell extents (hull frame, baked R1):
//   X: −267.0 .. −72.7   Y: −71.5 .. +132.0   Z: 0.0 .. 163.2
// Belly corners ≈ X = −88 (port) / −252 (stbd); Y = −50 (fore) / +105 (aft).
// Verify with TODO.md LG-04 before integrating bosses into cargo shell.
HULL_ATTACH_POS = [
    [  -88,  -50, 0,  1 ],  // Port-fore  (near Shepherd's room)
    [ -252,  -50, 0, -1 ],  // Stbd-fore  (near Inara's shuttle)
    [  -88, +105, 0,  1 ],  // Port-aft   (near River's room)
    [ -252, +105, 0, -1 ],  // Stbd-aft   (near Simon's medbay)
];

// ---------------------------------------------------------------------------
// Resolution
// ---------------------------------------------------------------------------
$fn = 48;

// ===========================================================================
// MODULE: tube(len, od, wall)
// Hollow cylindrical tube along +Z from origin.
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
// Hollow tube between two arbitrary 3-D points, using spherical decomposition
// to align local Z with the connecting vector.
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
// MODULE: arm_triangle(boss_fore, boss_aft, apex, od, wall)
// Isosceles triangular arm: crossbeam (base) + two equal arm struts (legs).
// All three tubes share the same OD and wall.
//   boss_fore, boss_aft — two hull boss positions at same Z (the base vertices)
//   apex               — strut junction position (the apex vertex)
// ===========================================================================
module arm_triangle(boss_fore, boss_aft, apex, od, wall) {
    // Crossbeam (base of triangle — horizontal, same Z for both bosses)
    strut_between(boss_fore, boss_aft, od, wall);
    // Two equal arm struts (legs of the isosceles triangle)
    strut_between(boss_fore, apex, od, wall);
    strut_between(boss_aft,  apex, od, wall);
}

// ===========================================================================
// MODULE: junction_node()
// Arm-to-strut junction node, printed in PETG (crush zone).
// Origin: node centre.
//
// The node has:
//   2 arm-strut socket bores (toward the two bosses of its arm, mirrored in Y)
//   1 main-strut socket bore (along +Z or -Z depending on which node)
//   1 tether cord hole (axial, +Z through node)
//
// The node module is rendered in a local frame where the two arm bores are
// symmetric about Y = 0.  The caller translates to hull-frame position and
// rotates to align the arm bore directions with the actual boss offsets.
//
// For simplicity the node is a sphere with two arm bores and a main bore.
// Both arm bores are in the +Z half-sphere (toward the bosses, which are
// above and to the fore/aft of the node).  The main bore exits at -Z (toward
// the foot / farther down the strut) and +Z (toward hull / top of strut).
// ===========================================================================
module junction_node(boss_fore_offset, boss_aft_offset) {
    // boss_*_offset: vector from node centre to respective boss position
    // Used to orient the socket bores.

    function az(v) = atan2(v[1], v[0]);
    function pol(v) = atan2(norm([v[0],v[1]]), v[2]);

    difference() {
        sphere(r = NODE_R);

        // Arm-strut socket bores (toward each boss)
        for (boff = [boss_fore_offset, boss_aft_offset]) {
            rotate([0, 0, az(boff)])
            rotate([0, pol(boff), 0])
                translate([0, 0, NODE_R - 0.1])
                    cylinder(h = SOCK_DEPTH + 0.1, d = ARM_OD + SOCK_CLR);
        }

        // Main strut bore — passes through node centre in ±Z (axial)
        translate([0, 0, -NODE_R - SOCK_DEPTH + 0.1])
            cylinder(h = 2 * NODE_R + SOCK_DEPTH, d = MAIN_SOCK_D);

        // Tether cord hole (runs along strut bore)
        translate([0, 0, -NODE_R - 0.1])
            cylinder(h = 2 * NODE_R + 0.2, d = TETHER_D);
    }
}

// ===========================================================================
// MODULE: hull_boss_side(side)
// Hull boss for upper arm — protrudes from the cargo SIDE WALL in hull ±X.
// Origin: boss top face (flush with hull outer side wall); boss protrudes
// OUTWARD (hull +X for port side, -X for stbd).
//   side = +1 → boss protrudes in hull +X direction (port)
//   side = -1 → boss protrudes in hull -X direction (stbd)
// Call is: translate([boss_x, boss_y, boss_z]) hull_boss_side(side)
// The hull outer wall at [boss_x, boss_y, boss_z] is the reference face.
// ===========================================================================
module hull_boss_side(side) {
    bore_d = ARM_OD + SOCK_CLR;  // 12.4 mm

    rotate([0, -side * 90, 0])   // rotate so boss extends in hull ±X
    difference() {
        union() {
            // Boss cylinder (protrudes outward)
            cylinder(h = BOSS_H, d = BOSS_OD);
            // Anchor post (inside hull, opposite face)
            translate([0, 0, -ANCHOR_H])
                cylinder(h = ANCHOR_H, d = ANCHOR_OD);
        }
        // Arm strut socket bore (strut end inserts from outside)
        translate([0, 0, 2])    // 2 mm solid bearing floor
            cylinder(h = BOSS_H, d = bore_d);
        // M3 retention bolt (transverse, in hull-Y direction)
        translate([0, -BOSS_OD/2 - 1, BOSS_H * 0.5])
            rotate([-90, 0, 0])
                cylinder(h = BOSS_OD + 2, d = M3_CLR);
        // Tether cord pass-through
        translate([0, 0, -ANCHOR_H - 0.1])
            cylinder(h = BOSS_H + ANCHOR_H + 0.2, d = TETHER_D);
    }
}

// ===========================================================================
// MODULE: hull_boss_belly()
// Hull boss for lower arm — protrudes from the cargo BELLY / side-transition.
// Origin: boss top face (flush with hull belly outer surface at Z = 0).
// Boss protrudes DOWNWARD (hull -Z direction) by BOSS_H.
// ===========================================================================
module hull_boss_belly() {
    bore_d = ARM_OD + SOCK_CLR;  // 12.4 mm

    difference() {
        union() {
            translate([0, 0, -BOSS_H])
                cylinder(h = BOSS_H, d = BOSS_OD);
            cylinder(h = ANCHOR_H, d = ANCHOR_OD);
        }
        // Arm strut socket bore (strut end inserts from below)
        translate([0, 0, -BOSS_H - 0.1])
            cylinder(h = BOSS_H - 2, d = bore_d);
        // M3 retention bolt (transverse, hull-Y)
        translate([0, -BOSS_OD/2 - 1, -BOSS_H * 0.5])
            rotate([-90, 0, 0])
                cylinder(h = BOSS_OD + 2, d = M3_CLR);
        // Tether cord
        translate([0, 0, -BOSS_H - 0.1])
            cylinder(h = BOSS_H + ANCHOR_H + 0.2, d = TETHER_D);
    }
}

// ===========================================================================
// MODULE: foot_pad()
// TPU 95A foot pad.  Origin: sole (bottom face) centre at Z = 0.
// Printed flat.  Main strut bottom end inserts into central socket from above.
// ===========================================================================
module foot_pad() {
    difference() {
        // Rounded rectangular pad
        hull() {
            for (dx = [-(FOOT_W/2 - FOOT_R), (FOOT_W/2 - FOOT_R)])
                for (dy = [-(FOOT_L/2 - FOOT_R), (FOOT_L/2 - FOOT_R)])
                    translate([dx, dy, 0])
                        cylinder(h = FOOT_H, r = FOOT_R);
        }
        // Main strut socket (from top face down)
        translate([0, 0, FOOT_H - SOCK_MAIN_H + 0.1])
            cylinder(h = SOCK_MAIN_H + 0.1, d = SOCK_MAIN_D);
        // 2× M3 retention screws from sole
        for (dx = [-FOOT_M3_P/2, FOOT_M3_P/2])
            translate([dx, 0, -0.1])
                cylinder(h = 3.0 + 0.2, d = FOOT_M3_D);
    }
}

// ===========================================================================
// MODULE: one_leg_assembly(corner)
// Full trapezoidal brace-frame leg assembly for one cargo corner in hull frame.
//   corner = [X_centre, Y_centre, Z=0, side] from HULL_ATTACH_POS
//
// Placed in hull frame:
//   Upper arm hull bosses: Z = UPPER_BOSS_Z (on side wall)
//   Upper arm apex:        Z = UPPER_APEX_Z (strut top node)
//   Lower arm hull bosses: Z = LOWER_BOSS_Z (belly edge)
//   Lower arm apex:        Z = LOWER_APEX_Z (strut lower node)
//   Main strut:            from UPPER_APEX_Z to STRUT_BOT_Z
//   Foot:                  at STRUT_BOT_Z (top face), STRUT_BOT_Z − FOOT_H (sole)
// ===========================================================================
module one_leg_assembly(corner) {
    cx   = corner[0];   // hull X of corner centre
    cy   = corner[1];   // hull Y of corner centre
    side = corner[3];   // +1 port, -1 stbd

    half_y = ARM_SPREAD_Y / 2;

    // --- Hull boss positions ---

    // Upper arm (side wall): bosses spread ±half_y in hull-Y at UPPER_BOSS_Z
    upper_fore_boss = [cx, cy - half_y, UPPER_BOSS_Z];
    upper_aft_boss  = [cx, cy + half_y, UPPER_BOSS_Z];

    // Lower arm (belly edge): bosses at LOWER_BOSS_Z
    lower_fore_boss = [cx, cy - half_y, LOWER_BOSS_Z];
    lower_aft_boss  = [cx, cy + half_y, LOWER_BOSS_Z];

    // --- Strut junction node positions ---
    upper_apex = [cx, cy, UPPER_APEX_Z];  // top of main strut
    lower_apex = [cx, cy, LOWER_APEX_Z];  // lower node on main strut

    // Foot top centre
    foot_top  = [cx, cy, STRUT_BOT_Z];
    foot_sole = [cx, cy, STRUT_BOT_Z - FOOT_H];

    // --- Upper triangular arm (CF-PETG) ---
    color("DimGray", 0.9)
        arm_triangle(upper_fore_boss, upper_aft_boss, upper_apex,
                     ARM_OD, ARM_WALL);

    // --- Lower triangular arm (CF-PETG) ---
    color("DimGray", 0.9)
        arm_triangle(lower_fore_boss, lower_aft_boss, lower_apex,
                     ARM_OD, ARM_WALL);

    // --- Main vertical strut (CF-PETG) ---
    // Runs from upper apex node down through lower apex node to foot.
    // The two nodes act as sleeves/rings on the strut; strut is continuous.
    color("DimGray", 0.85)
        strut_between(upper_apex, foot_top, MAIN_OD, MAIN_WALL);

    // --- Arm-to-strut junction nodes (PETG crush zone) ---
    // Upper node: boss offsets in local node frame (Y spread, +Z upward)
    color("LightSlateGray", 0.9) {
        translate(upper_apex)
            junction_node(
                [0, -half_y, UPPER_BOSS_Z - UPPER_APEX_Z],   // toward fore boss
                [0,  half_y, UPPER_BOSS_Z - UPPER_APEX_Z]    // toward aft boss
            );
        translate(lower_apex)
            junction_node(
                [0, -half_y, LOWER_BOSS_Z - LOWER_APEX_Z],   // toward fore boss
                [0,  half_y, LOWER_BOSS_Z - LOWER_APEX_Z]    // toward aft boss
            );
    }

    // --- Hull boss cylinders ---
    // Upper arm bosses: on side wall, protrude outward in hull ±X
    color("OliveDrab", 0.65)
        for (bp = [upper_fore_boss, upper_aft_boss])
            translate(bp)
                hull_boss_side(side);

    // Lower arm bosses: at belly edge, protrude downward in hull -Z
    color("OliveDrab", 0.65)
        for (bp = [lower_fore_boss, lower_aft_boss])
            translate(bp)
                hull_boss_belly();

    // --- TPU foot pad ---
    color("Black", 0.85)
        translate(foot_sole)
            foot_pad();
}

// ===========================================================================
// MODULE: assembly()
// All 4 leg assemblies in hull frame — layout verification only.
// ===========================================================================
module assembly() {
    // Cargo belly reference plane (semi-transparent grey slab)
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

    // Upper isosceles triangular arm, print orientation (flat in XY plane).
    // Triangle: base = ARM_SPREAD_Y (crossbeam), equal sides ≈ 79.1 mm.
    // Altitude from base midpoint to apex ≈ 75.0 mm.
    half_y  = ARM_SPREAD_Y / 2;
    // Boss offsets from apex (apex at origin in print coordinates)
    dz_up   = UPPER_BOSS_Z - UPPER_APEX_Z;  // 75 mm height
    b_left  = [-half_y, dz_up, 0];   // print X = hull Y (fore), print Y = hull Z
    b_right = [ half_y, dz_up, 0];
    apex    = [0, 0, 0];
    arm_triangle(b_left, b_right, apex, ARM_OD, ARM_WALL);

} else if (PART == "arm_lower") {

    // Lower isosceles triangular arm, print orientation (flat in XY plane).
    // Triangle: base = ARM_SPREAD_Y (crossbeam), equal sides ≈ 55.9 mm.
    // Altitude from base midpoint to apex ≈ 50.0 mm.
    half_y  = ARM_SPREAD_Y / 2;
    dz_lo   = LOWER_BOSS_Z - LOWER_APEX_Z;  // 50 mm height
    b_left  = [-half_y, dz_lo, 0];
    b_right = [ half_y, dz_lo, 0];
    apex    = [0, 0, 0];
    arm_triangle(b_left, b_right, apex, ARM_OD, ARM_WALL);

} else if (PART == "main_strut") {

    // Main vertical strut, print orientation upright.
    // Total length = UPPER_APEX_Z - STRUT_BOT_Z = 143 mm.
    // Bottom end has a spigot (SOCK_MAIN_D OD) for the foot socket.
    strut_len = UPPER_APEX_Z - STRUT_BOT_Z;  // 143 mm

    difference() {
        tube(strut_len, MAIN_OD, MAIN_WALL);
        // Foot spigot: reduce OD to SOCK_MAIN_D at the bottom (Z=0) end
        translate([0, 0, -0.1])
            difference() {
                cylinder(h = SOCK_MAIN_H + 0.1, d = MAIN_OD + 0.2);
                cylinder(h = SOCK_MAIN_H + 0.2, d = SOCK_MAIN_D);
            }
    }

} else if (PART == "node") {

    // Junction node, print upright.
    // Render using the upper-node boss offsets as a representative example.
    half_y = ARM_SPREAD_Y / 2;
    dz_up  = UPPER_BOSS_Z - UPPER_APEX_Z;
    junction_node(
        [0, -half_y, dz_up],
        [0,  half_y, dz_up]
    );

} else if (PART == "boss_side") {

    // Side-wall boss (upper arm), reference view.
    // Boss protrudes in +X (port). Hull outer surface at Z=0 of this module.
    hull_boss_side(1);

} else if (PART == "boss_belly") {

    // Belly-edge boss (lower arm), reference view.
    hull_boss_belly();

} else if (PART == "foot") {

    // TPU foot pad, print orientation flat (sole down).
    foot_pad();

}
