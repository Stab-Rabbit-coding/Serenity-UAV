// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  Primary-component STLs published to airframe/stls/
//   are stored directly in hull frame, baked by tools/bake_hull_frame.py
//   (marker 'SerenityUAV HULL-FRAME R1' in the binary STL header).
//   NEVER re-bake a mesh derived from an already-baked file.
//
//   Landing gear parts are modeled in hull frame directly.  They are NOT
//   primary-component STLs; they do not require bake_hull_frame.py.
//   They mount to hull boss cylinders that are integral to the cargo shell.
// ===========================================================================
// ===========================================================================
// landing_leg_assy.scad
// Serenity UAV — Rev R1.1 — Landing Leg Assembly (4-Strut Pyramid)
// ===========================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-06-15
// Revision: Rev R1.1
//
// Description
// -----------
// Parametric landing leg assembly for the Serenity UAV.  Four leg assemblies
// attach to the belly of the cargo section, one at each corner.
//
// Geometry — 4-strut pyramid:
//   Each assembly has four hull boss cylinders arranged in a 2 × 2 grid
//   (SPREAD_X laterally, SPREAD_Y fore-aft) at the cargo belly (Z = 0).
//   Four arm struts radiate inward and downward from the four boss tops to
//   a central JUNCTION HUB at depth JUNCT_Z below the belly.  A single
//   vertical COLUMN descends from the hub to a TPU FOOT PAD.
//
//   Viewed from the front (YZ plane): inverted-A frame (outboard and
//   inboard struts spreading at hull, converging at hub).
//   Viewed from the side (XZ plane): two arms diverging fore and aft.
//   This triangulates in both lateral axes — full 3-D stability.
//
//   Rev R1 (prior): flat-plate cantilever — SUPERSEDED by this file.
//
// Structural design summary (see docs/LANDING_GEAR_ANALYSIS.md Rev R1.1):
//   - Design case: Phase 11 AUW 6.90 lbm (3,130 g), 6 ft (1,829 mm)
//     drop onto hard level surface.
//   - Total KE = 497 in-lbf (56.1 J); 124 in-lbf (14.0 J) per leg assy.
//   - 4 struts carry load axially (compression) into 4 hull bosses; boss
//     bearing stress at design load ≪ CF-PETG bearing strength.
//   - Per-strut Euler buckling load ≈ 5,300 N >> 125 N per strut at design.
//   - Overload protection: junction hub printed in PETG (not CF-PETG) at
//     25 % gyroid infill acts as a crush zone above ~3× design load.
//   - Boss retention bolts: 1× M3 PA6 nylon per boss (4 per assy) in
//     single shear carry lateral loads from off-vertical landings; also
//     prevent strut backs from pulling out during handling/inverted flight.
//   - Safety cord: 2 mm Dyneema through TETHER_D hole in hub anchors the
//     assembly to the airframe so detached legs cannot reach the EDFs.
//   - Lateral landing (±15°): lateral component 129.7 N per assy resolved
//     by differential compression/tension in opposing strut pairs; well
//     within CF-PETG elastic range.
//
// Print specifications (see docs/LANDING_GEAR_ANALYSIS.md §9 Rev R1.1):
//   arm strut : CF-PETG, 0.15 mm layer, 4 perimeters, 40 % gyroid,
//               print lying flat (long axis on printer bed); one strut per
//               print job.  All 4 struts per assy are identical.
//   hub       : PETG, 0.15 mm layer, 25 % gyroid; print upright.
//               PETG (not CF-PETG) intentional — hub is the crush zone.
//   boss      : CF-PETG, same settings as strut; integral to cargo shell
//               (`cargo_sect_shell24.scad`).  Use PART="boss" as reference.
//   column    : CF-PETG, 0.15 mm layer, 4 perimeters, 40 % gyroid; print
//               upright.
//   foot      : TPU 95A, 0.20 mm layer, 25 % gyroid; print flat.
//
// Attribution:
//   Geometry concept: canonical Serenity landing leg silhouette,
//   Firefly/Serenity (TV/film), Joss Whedon (creator).
//   Reference hull: misubisu, Thingiverse thing:4677565, CC BY 4.0.
//   <https://www.thingiverse.com/thing:4677565>
//
// Standards applied:
//   Fabrication per CLAUDE.md §Fabrication Standards.
//   Nylon bolt shear values per ASTM D638 (Type I, PA6); verification
//   testing required before first flight (TODO.md LG-01).
//   Lateral load ±15° per docs/LANDING_GEAR_ANALYSIS.md §5 Rev R1.1.
//
// Usage — set PART to render:
//   PART = "assy"       Full assembly view in hull frame (all 4 corners)
//   PART = "strut"      One arm strut, print orientation (lying flat)
//   PART = "hub"        Junction hub, print orientation (upright)
//   PART = "column"     Vertical column, print orientation (upright)
//   PART = "boss"       Hull boss cylinder, reference only
//   PART = "foot"       TPU foot pad, print orientation (flat)
//
// STL export commands (run from repo root):
//   openscad -o airframe/stls/fuselage/landing-gear/arm_strut_r1.stl \
//     -D 'PART="strut"' airframe/openscad/fuselage/landing_leg_assy.scad
//   openscad -o airframe/stls/fuselage/landing-gear/junct_hub_r1.stl \
//     -D 'PART="hub"' airframe/openscad/fuselage/landing_leg_assy.scad
//   openscad -o airframe/stls/fuselage/landing-gear/leg_column_r1.stl \
//     -D 'PART="column"' airframe/openscad/fuselage/landing_leg_assy.scad
//   openscad -o airframe/stls/fuselage/landing-gear/hull_boss_cyl_r1.stl \
//     -D 'PART="boss"' airframe/openscad/fuselage/landing_leg_assy.scad
//   openscad -o airframe/stls/fuselage/landing-gear/foot_pad_r1.stl \
//     -D 'PART="foot"' airframe/openscad/fuselage/landing_leg_assy.scad
// ===========================================================================

// ---------------------------------------------------------------------------
// Render control
// ---------------------------------------------------------------------------

// Which part to render.  Override from command line with -D 'PART="strut"'.
PART = "assy";   // "assy" | "strut" | "hub" | "column" | "boss" | "foot"

// ---------------------------------------------------------------------------
// Arm strut parameters
// ---------------------------------------------------------------------------

STRUT_OD    = 12.0;  // mm — arm strut outer diameter
STRUT_WALL  =  2.0;  // mm — arm strut wall thickness (CF-PETG, hollow tube)
// Inner diameter: 12 - 2*2 = 8 mm

// ---------------------------------------------------------------------------
// Hub (junction) parameters
// ---------------------------------------------------------------------------

HUB_R       = 11.0;  // mm — junction hub sphere radius
// Hub material: PETG at 25 % gyroid (intentional crush zone)
// Boss socket bore in hub: STRUT_OD + 0.4 clearance, to SOCKET_DEPTH depth
SOCKET_DEPTH = 12.0; // mm — depth of strut socket in hub
SOCKET_CLR  =  0.4;  // mm — total diametral clearance (0.2 mm per side)
COL_SOCKET_D = 18.4; // mm — column socket bore in hub (column OD + 0.4 mm)

// Tether anchor hole through hub centre (hull-Z axis)
TETHER_D    =  4.5;  // mm — Dyneema 2 mm cord, routed up through column bore

// ---------------------------------------------------------------------------
// Boss (hull attachment) parameters
// ---------------------------------------------------------------------------

BOSS_OD     = 22.0;  // mm — boss cylinder outer diameter
BOSS_H      = 30.0;  // mm — boss protrusion below hull belly (Z = 0 downward)
BOSS_WALL   =  3.8;  // mm — boss wall thickness (CF-PETG; computed: (22-12.4)/2)
// Boss bore: STRUT_OD + 0.4 = 12.4 mm (strut top end inserts into boss from below)

// Fuse / retention bolt: 1× M3 × 20 mm nylon PA6 bolt per boss, transverse.
// Single shear per bolt: 40 MPa × π×3²/4 = 282.8 N
// 4 bosses × 282.8 N = 1131 N total fuse / retention load per leg assembly
// (2.26× the 501 N design force; primary protection by hub crush zone, not fuse)
M3_CLR      =  3.4;  // mm — M3 clearance hole

// M3 anchor post inside boss top (Dyneema safety cord anchor point)
ANCHOR_POST_OD = 5.0; // mm — anchor post outer diameter
ANCHOR_POST_H  = 8.0; // mm — anchor post height above boss top (inside hull)

// ---------------------------------------------------------------------------
// Column parameters
// ---------------------------------------------------------------------------

COL_OD      = 18.0;  // mm — column outer diameter
COL_WALL    =  2.5;  // mm — column wall thickness (CF-PETG)
// Column inner diameter: 18 - 2*2.5 = 13 mm
// Tether cord (TETHER_D = 4.5 mm) routes through this bore to anchor in hub.
COL_H       = 60.0;  // mm — column length (hub bottom to foot top face)

// ---------------------------------------------------------------------------
// Foot pad parameters
// ---------------------------------------------------------------------------

FOOT_W      = 55.0;  // mm — foot pad width (hull X)
FOOT_L      = 55.0;  // mm — foot pad length (hull Y)
FOOT_H      = 12.0;  // mm — foot pad total height (TPU 95A)
FOOT_WALL   =  3.0;  // mm — foot perimeter wall thickness
FOOT_POST_D = 14.0;  // mm — central column plug outer diameter in foot top
FOOT_POST_H =  8.0;  // mm — depth of column plug socket in foot
FOOT_FILLET =  5.0;  // mm — corner fillet radius of foot pad

// 2× M3 SS SHCS through foot sole into column — foot retention
FOOT_BOLT_D =  3.4;  // mm — M3 clearance
FOOT_BOLT_PITCH = 14.0; // mm — bolt spacing

// ---------------------------------------------------------------------------
// Assembly geometry — boss spread and junction depth
// ---------------------------------------------------------------------------

// Fore-aft spread: bosses for the fore arm and aft arm are SPREAD_Y apart
// in the hull-Y direction, centred on the corner centre Y coordinate.
SPREAD_Y    = 60.0;  // mm — fore-aft boss pair separation

// Lateral spread: outboard and inboard bosses for each arm are SPREAD_X
// apart in the hull-X direction, centred on the corner centre X coordinate.
// "Outboard" means toward the ship flank; "inboard" toward centreline.
SPREAD_X    = 40.0;  // mm — lateral boss pair separation per arm

// Junction depth below cargo belly
JUNCT_Z     = 85.0;  // mm — hub centre below Z = 0 (cargo belly bottom)

// Resulting strut geometry:
//   Outboard-fore strut spans from boss at (+side*SPREAD_X/2, -SPREAD_Y/2, 0)
//   to junction at (0, 0, -JUNCT_Z) in local corner frame.
//   delta = (20, 30, 85) mm; length = sqrt(20²+30²+85²) = sqrt(8333) = 91.3 mm
//   Angle from vertical = atan(sqrt(20²+30²)/85) = atan(36.1/85) = 23.0°

// ---------------------------------------------------------------------------
// Hull frame corner positions
// ---------------------------------------------------------------------------

// Format: [X_centre, Y_centre, Z=0, side]
//   side = +1 port (hull +X outboard), -1 stbd (hull -X outboard)
//
// Approximate positions — verify against cargo_sect_shell24.scad belly
// geometry before cutting boss sockets (TODO.md LG-04).
//
// Cargo_Shell extents (hull frame, baked R1):
//   X: -267.0 .. -72.7   Y: -71.5 .. +132.0   Z: 0.0 .. 163.2
// Port belly corner ≈ X=-88, stbd belly corner ≈ X=-252.
// Fore belly edge ≈ Y=-50, aft belly edge ≈ Y=+105.
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
// MODULE: strut_tube(len, od, wall)
// Hollow cylindrical tube, lying along +Z from origin, length = len.
// Used for both arm struts (STRUT_OD) and column (COL_OD).
// ===========================================================================
module strut_tube(len, od, wall) {
    difference() {
        cylinder(h = len, d = od);
        translate([0, 0, -0.1])
            cylinder(h = len + 0.2, d = od - 2 * wall);
    }
}

// ===========================================================================
// MODULE: strut_between(pt_a, pt_b, od, wall)
// Places a hollow strut_tube between two arbitrary 3-D points.
// Uses spherical decomposition to rotate local Z onto the connecting vector.
//   polar  = angle from hull +Z down toward hull XY plane
//   azimuth = angle in hull XY plane from hull +X axis
// ===========================================================================
module strut_between(pt_a, pt_b, od, wall) {
    v      = pt_b - pt_a;
    len    = norm(v);
    polar  = atan2(norm([v[0], v[1]]), v[2]);
    azimuth = atan2(v[1], v[0]);
    translate(pt_a)
        rotate([0, 0, azimuth])
        rotate([0, polar, 0])
            strut_tube(len, od, wall);
}

// ===========================================================================
// MODULE: junction_hub()
// Spherical junction hub where all 4 arm struts and the column meet.
// Origin: hub centre.  Printed in PETG (crush zone) — intentionally weaker
// than CF-PETG struts and bosses so the hub fails before the hull.
//
// The hub has:
//   4 socket bores for arm strut ends (angled to match strut directions)
//   1 socket bore downward for column top end
//   1 axial (Z) tether hole for Dyneema safety cord
//
// Socket angles are computed from SPREAD_X, SPREAD_Y, JUNCT_Z.
// The angles passed to boss_socket_at() must match the actual strut vectors.
// ===========================================================================
module junction_hub() {
    // Strut endpoint offsets from hub centre (in local corner frame,
    // hub centre = origin).  Struts go from hub upward to boss positions.
    //
    //   Boss relative to hub (local frame, side = +1 example):
    //     outboard-fore: (+SPREAD_X/2, -SPREAD_Y/2, +JUNCT_Z)
    //     inboard-fore:  (-SPREAD_X/2, -SPREAD_Y/2, +JUNCT_Z)
    //     outboard-aft:  (+SPREAD_X/2, +SPREAD_Y/2, +JUNCT_Z)
    //     inboard-aft:   (-SPREAD_X/2, +SPREAD_Y/2, +JUNCT_Z)
    //
    // Column goes downward from hub centre: (0, 0, -COL_H).
    //
    // The hub module is rendered in the "local corner frame" with side=+1.
    // When used for side=-1 (stbd), the leg_assembly() mirrors in X.

    half_x = SPREAD_X / 2;
    half_y = SPREAD_Y / 2;

    // Direction vectors from hub centre to each boss position (unit vectors
    // computed inline).  Length = strut length.
    boss_offsets = [
        [ half_x, -half_y, JUNCT_Z],   // outboard-fore
        [-half_x, -half_y, JUNCT_Z],   // inboard-fore
        [ half_x,  half_y, JUNCT_Z],   // outboard-aft
        [-half_x,  half_y, JUNCT_Z],   // inboard-aft
    ];

    difference() {
        // Sphere hub body
        sphere(r = HUB_R);

        // 4 arm-strut socket bores (from hub surface toward each boss)
        for (boff = boss_offsets) {
            len_v = norm(boff);
            pol   = atan2(norm([boff[0], boff[1]]), boff[2]);
            az    = atan2(boff[1], boff[0]);
            // Socket points from hub centre outward toward boss
            translate([0, 0, 0])
                rotate([0, 0, az])
                rotate([0, pol, 0])
                    // Socket bore: HUB_R depth ensures socket starts at surface
                    translate([0, 0, HUB_R - 0.1])
                        cylinder(h = SOCKET_DEPTH + 0.1,
                                 d = STRUT_OD + SOCKET_CLR);
        }

        // Column socket bore (downward, toward -Z from hub centre)
        translate([0, 0, -HUB_R - SOCKET_DEPTH + 0.1])
            cylinder(h = SOCKET_DEPTH + HUB_R, d = COL_SOCKET_D);

        // Tether cord hole (axial, +Z through hub; exits through column bore)
        translate([0, 0, -HUB_R - 0.1])
            cylinder(h = 2 * HUB_R + 0.2, d = TETHER_D);
    }
}

// ===========================================================================
// MODULE: hull_boss_cyl()
// Hull boss cylinder — integral to cargo belly shell (CF-PETG).
// Origin: top face at Z = 0 (flush with cargo belly lower face in hull frame).
// Boss protrudes downward (hull -Z) by BOSS_H.
//
// The boss has:
//   A central bore (STRUT_OD + 0.4 mm) for the arm strut top end.
//   1× M3 clearance hole (transverse, in hull-Y) for the fuse/retention bolt.
//   A Dyneema tether pass-through slot into the hull interior (+Z direction).
//   An anchor post stub above Z=0 (inside hull) for the Dyneema cord.
// ===========================================================================
module hull_boss_cyl() {
    bore_d = STRUT_OD + SOCKET_CLR;  // 12.4 mm

    difference() {
        union() {
            // Boss cylinder (protrudes downward from hull belly)
            translate([0, 0, -BOSS_H])
                cylinder(h = BOSS_H, d = BOSS_OD);

            // Anchor post stub above hull belly (inside hull; Dyneema loop anchor)
            cylinder(h = ANCHOR_POST_H, d = ANCHOR_POST_OD);
        }

        // Strut socket bore — strut top end inserts from below (+Z into boss)
        translate([0, 0, -BOSS_H - 0.1])
            cylinder(h = BOSS_H - 2, d = bore_d);
        // Leave 2 mm solid floor above bore to bear the strut end in compression.

        // M3 fuse/retention bolt — transverse (hull-Y direction)
        // Bolt at mid-height of boss bore zone
        translate([0, -BOSS_OD / 2 - 1, -BOSS_H * 0.5])
            rotate([-90, 0, 0])
                cylinder(h = BOSS_OD + 2, d = M3_CLR);

        // Tether cord pass-through: from bore bottom up through anchor post
        // (cord runs: hub → column bore → boss bore → anchor post loop)
        translate([0, 0, -BOSS_H - 0.1])
            cylinder(h = BOSS_H + ANCHOR_POST_H + 0.2, d = TETHER_D);
    }
}

// ===========================================================================
// MODULE: foot_pad()
// TPU 95A foot pad.  Origin: bottom face centre at Z=0 (ground contact).
// Printed flat.  Column bottom end inserts into central socket from above.
// ===========================================================================
module foot_pad() {
    // Outer pad body with radiused corners in XY (rounded rectangle)
    // Approximated with hull() over 4 cylinders at corners
    difference() {
        union() {
            // Pad body (rounded rectangle)
            hull() {
                for (dx = [-(FOOT_W/2 - FOOT_FILLET), (FOOT_W/2 - FOOT_FILLET)])
                    for (dy = [-(FOOT_L/2 - FOOT_FILLET), (FOOT_L/2 - FOOT_FILLET)])
                        translate([dx, dy, 0])
                            cylinder(h = FOOT_H, r = FOOT_FILLET);
            }
        }

        // Column plug socket (from top face downward)
        translate([0, 0, FOOT_H - FOOT_POST_H + 0.1])
            cylinder(h = FOOT_POST_H + 0.1, d = FOOT_POST_D);

        // 2× M3 foot retention screw holes from sole through floor
        for (dx = [-FOOT_BOLT_PITCH/2, FOOT_BOLT_PITCH/2])
            translate([dx, 0, -0.1])
                cylinder(h = FOOT_WALL + 0.2, d = FOOT_BOLT_D);
    }
}

// ===========================================================================
// MODULE: one_leg_assembly(corner, side_sign)
// Full leg assembly for one cargo corner, placed in hull frame.
//   corner   = [X, Y, Z, side] from HULL_ATTACH_POS
//   side_sign = +1 port (outboard = +X), -1 stbd (outboard = -X)
//
// Placed in hull frame: bosses at Z=0 (cargo belly), hub at Z=-JUNCT_Z,
// foot sole at Z = -(JUNCT_Z + COL_H + FOOT_H).
// ===========================================================================
module one_leg_assembly(corner) {
    cx      = corner[0];  // hull X of corner centre
    cy      = corner[1];  // hull Y of corner centre
    side    = corner[3];  // +1 port, -1 stbd

    // Junction hub centre in hull frame
    jx = cx;
    jy = cy;
    jz = -JUNCT_Z;        // below hull belly (hull -Z direction)

    hub_pt  = [jx, jy, jz];

    // Four boss centres at hull belly (Z = 0)
    half_x = SPREAD_X / 2;
    half_y = SPREAD_Y / 2;

    boss_pts = [
        [cx + side * half_x, cy - half_y, 0],   // outboard-fore
        [cx - side * half_x, cy - half_y, 0],   // inboard-fore
        [cx + side * half_x, cy + half_y, 0],   // outboard-aft
        [cx - side * half_x, cy + half_y, 0],   // inboard-aft
    ];

    // Column base (foot top centre in hull frame)
    col_base = [jx, jy, jz - COL_H];

    // Foot bottom centre
    foot_sole = [jx, jy, jz - COL_H - FOOT_H];

    // --- Arm struts (CF-PETG) ---
    color("DimGray", 0.9) {
        for (bp = boss_pts)
            strut_between(hub_pt, bp, STRUT_OD, STRUT_WALL);
    }

    // --- Junction hub (PETG — crush zone) ---
    // Mirror stbd side in hull-X so socket bores face their own boss positions.
    color("LightSlateGray", 0.9)
        translate(hub_pt)
            scale([side, 1, 1])  // +1 for port (no flip), -1 for stbd (flip X)
                junction_hub();

    // --- Column (CF-PETG) ---
    color("DimGray", 0.9)
        strut_between(hub_pt, col_base, COL_OD, COL_WALL);

    // --- Hull boss cylinders (CF-PETG, integral to cargo shell) ---
    color("OliveDrab", 0.6)
        for (bp = boss_pts)
            translate(bp)
                hull_boss_cyl();

    // --- TPU foot pad ---
    color("Black", 0.85)
        translate(foot_sole)
            foot_pad();
}

// ===========================================================================
// MODULE: assembly()
// Full 4-corner assembly in hull frame — layout verification view.
// Not exported to STL.
// ===========================================================================
module assembly() {
    // Cargo belly reference plane (semi-transparent)
    color("SaddleBrown", 0.12)
        translate([-300, -100, -1])
            cube([270, 250, 1]);

    // All four leg assemblies
    for (corner = HULL_ATTACH_POS) {
        one_leg_assembly(corner);
    }
}

// ===========================================================================
// Entry point
// ===========================================================================

if (PART == "assy") {

    assembly();

} else if (PART == "strut") {

    // Print orientation: long axis horizontal on printer bed.
    // Compute strut length (outboard-fore case, conservative maximum).
    strut_len = norm([SPREAD_X/2, SPREAD_Y/2, JUNCT_Z]);  // 91.3 mm
    // Lay along X on printer bed (local Z → printer X)
    rotate([0, 90, 0])
        strut_tube(strut_len, STRUT_OD, STRUT_WALL);

} else if (PART == "hub") {

    // Print orientation: upright (hub socket for column faces down toward
    // print bed — overhangs kept to 45° or less for each socket bore).
    junction_hub();

} else if (PART == "column") {

    // Print orientation: upright, hub socket end down.
    // Column length = COL_H; hub socket (top end) inserts into hub.
    difference() {
        strut_tube(COL_H, COL_OD, COL_WALL);
        // Foot plug spigot at base (reduces to FOOT_POST_D OD over FOOT_POST_H)
        // — Integral reduced-diameter spigot on column bottom that fits into foot socket.
        // Machined as a separate reduction at the tip; modelled here as a subtraction
        // that leaves a ring flange and the spigot.
        // Spigot: OD = FOOT_POST_D, length = FOOT_POST_H at Z = 0 end.
        // Hollow bore is already open through COL_WALL subtraction above;
        // reduce the outer profile at the foot end by cutting away the excess.
        translate([0, 0, -0.1])
            difference() {
                cylinder(h = FOOT_POST_H + 0.1, d = COL_OD + 0.2);
                cylinder(h = FOOT_POST_H + 0.2, d = FOOT_POST_D);
            }
    }

} else if (PART == "boss") {

    // Reference / integration part — shows hull boss in its hull-frame
    // relationship to the cargo belly.  Top face at Z=0, boss below.
    hull_boss_cyl();

} else if (PART == "foot") {

    // Print orientation: flat on printer bed (pad bottom face down).
    foot_pad();

}
