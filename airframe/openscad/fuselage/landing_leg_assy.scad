// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  Primary-component STLs published to airframe/stls/
//   are stored directly in hull frame, baked by tools/bake_hull_frame.py
//   (marker 'SerenityUAV HULL-FRAME R1' in the binary STL header).
//   NEVER re-bake a mesh derived from an already-baked file.
//
//   This file:
//     Parts are modeled in a local leg frame (Z = up along leg axis,
//     X = across leg width, Y = through leg depth).  The assembly()
//     module positions legs in hull frame at the HULL_ATTACH_POS[] array.
//     After regeneration, export each PART individually to STL (no baking
//     needed — landing gear parts are not primary-component STLs requiring
//     bake_hull_frame.py; they mount inside the hull-frame assembly via
//     the bosses defined in cargo_sect_shell24.scad).
// ===========================================================================
// ===========================================================================
// landing_leg_assy.scad
// Serenity UAV — Rev R1 — Landing Leg Assembly (Field-Replaceable, Fused)
// ===========================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-06-14
// Revision: Rev R1
//
// Description
// -----------
// Parametric landing leg assembly for the Serenity UAV.  The system
// comprises four field-replaceable main legs (CF-PETG flat-spring
// cantilevers) plus four TPU feet.  Two integral rear skids are built
// into the horseshoe ring of the middle/rear section and are NOT
// produced by this file.
//
// Structural design summary (see docs/LANDING_GEAR_ANALYSIS.md):
//   - Design case: Phase 11 AUW 6.90 lbm (3,130 g), 6 ft (1,829 mm)
//     vertical drop onto hard level surface.
//   - Each of the 4 main legs absorbs 124 in-lbf (14.0 J) of kinetic
//     energy through elastic/plastic cantilever bending.
//   - Peak force at 6 ft drop: ~527 N (118.5 lbf) per leg → ~68.7g
//     deceleration.  Avionics isolation mounts (Faraday enclosures) are
//     rated for 100g shock; no direct 60g hard limit on airframe structure.
//   - The flat-spring cantilever yields plastically above ~3 ft drop;
//     the hull boss is protected by 3x M3 nylon shear bolts (FUSE_N)
//     that sacrifice at ~850-950 N per leg (1.6–1.8× the 6 ft design
//     force), well below the ~2000 N estimated hull boss fracture load.
//   - After fuse activation: nylon bolt remnants are pushed out, leg
//     replaced, new bolts installed.  Safety cord (TETHER_D hole in leg
//     body) retains the detached leg so it does not fall into rotors or
//     away from the aircraft.
//   - Lateral loads at ±15° off-vertical: lateral force component is
//     119 N per leg; bending stress in 22 × 10 mm section = 24.2 MPa
//     (well within CF-PETG yield ≈ 55 MPa in the lateral bending plane).
//
// Print specifications:
//   leg_body   : CF-PETG, 0.15 mm layer, 4 perimeters, 40% gyroid infill
//                Print upright (long leg axis vertical) for optimal fiber
//                alignment along the primary stress direction.
//   hull_boss  : CF-PETG, same settings as leg_body, integral to cargo
//                shell (see cargo_sect_shell24.scad).  Export via
//                PART="boss" and use as a subtraction / addition reference
//                when updating cargo_sect_shell24.scad belly geometry.
//   TPU foot   : TPU 95A, 0.2 mm layer, 25% gyroid infill (existing
//                Thingiverse geometry or regenerated from this file).
//
// Thingiverse attribution:
//   Original landing leg geometry derived from Serenity model by misubisu
//   (Thingiverse thing:7330462, CC BY 4.0).  Cross-section dimensions,
//   length, and boss/fuse/foot features redesigned for structural
//   compliance.  Reference: <https://www.thingiverse.com/thing:7330462>
//
// Standards applied:
//   Fabrication materials per CLAUDE.md §Fabrication Standards.
//   Fastener shear fuse design uses M3 nylon (PA6) bolts — shear
//   strength ~40 MPa per ASTM D638 (Type I, PA6); verification testing
//   required before first flight.  See docs/LANDING_GEAR_ANALYSIS.md §7.
//   Lateral load case per ±15° off-vertical scenario;
//   see docs/LANDING_GEAR_ANALYSIS.md §4 for analysis details.
//
// Usage
// -----
// Set PART to render a specific component:
//   PART = "leg"   — leg body (CF-PETG), print orientation: upright
//   PART = "boss"  — hull boss profile (reference; integrate into cargo shell)
//   PART = "assy"  — full assembly view in hull frame (not for export)
//
// To render STLs (from repo root):
//   openscad -o airframe/stls/fuselage/landing-gear/leg_body_r1.stl \
//     -D 'PART="leg"' \
//     airframe/openscad/fuselage/landing_leg_assy.scad
//
//   openscad -o airframe/stls/fuselage/landing-gear/hull_boss_r1.stl \
//     -D 'PART="boss"' \
//     airframe/openscad/fuselage/landing_leg_assy.scad
// ===========================================================================

// ---------------------------------------------------------------------------
// Render control
// ---------------------------------------------------------------------------

// Which part to render.  Set from command line with -D 'PART="leg"' etc.
PART = "assy";   // "leg" | "boss" | "assy"

// ---------------------------------------------------------------------------
// Primary dimensional parameters
// ---------------------------------------------------------------------------

// Leg cross-section (flat spring plate geometry)
LEG_W       = 22;      // mm — plate width (across, resists lateral bending)
LEG_D       = 10;      // mm — plate depth/thickness (bending spring direction)
LEG_WALL    = 2.5;     // mm — wall thickness, CF-PETG box section

// Leg length breakdown
FOOT_SOCKET_L   = 20;  // mm — depth of the foot socket at leg bottom
SPRING_L        = 145; // mm — free cantilever spring length (effective)
BOSS_INSERT_L   = 20;  // mm — stub that enters hull boss from below
LEG_TOTAL_L = FOOT_SOCKET_L + SPRING_L + BOSS_INSERT_L; // 185 mm total

// Splay geometry (applied in assembly(); leg_body() is modeled straight)
SPLAY_ANGLE = 30;  // deg — outboard angle from vertical (in ±X hull direction)
TOE_ANGLE   = 10;  // deg — forward lean (tip is hull-Y-forward of boss)

// Hull boss geometry
HULL_BOSS_W     = 30;  // mm — boss outer width (>= LEG_W + 2*BOSS_WALL)
HULL_BOSS_D     = 18;  // mm — boss outer depth (>= LEG_D + 2*BOSS_WALL)
HULL_BOSS_H     = 28;  // mm — boss height below cargo belly (>= BOSS_INSERT_L + clearance)
HULL_BOSS_WALL  = 4;   // mm — boss wall thickness (CF-PETG, 4 perimeters)
HULL_BOSS_FILLET = 3;  // mm — boss-to-belly blend fillet radius

// Safety tether
TETHER_D    = 4.0; // mm — Dyneema cord hole through leg body (2 mm Dyneema line)
TETHER_Z    = FOOT_SOCKET_L + SPRING_L - 20; // mm — from leg base (near top of spring)

// ---------------------------------------------------------------------------
// Fastener parameters
// ---------------------------------------------------------------------------

// M3 clearance (nylon shear bolts — fuse mechanism, through boss insert stub)
M3_CLR      = 3.4;  // mm — M3 clearance hole diameter
FUSE_N      = 3;    // count — M3 nylon shear bolts per leg (fuse)
// Bolt rows spaced evenly in the BOSS_INSERT_L zone
// Fuse load per bolt (40 MPa shear, PA6): 40 × π×3²/4 = 282.7 N
// Total fuse load: 3 × 282.7 = 848 N per leg (190.7 lbf) — see analysis doc

// M3 clearance (steel screws — foot retention, through foot socket bottom flange)
FOOT_BOLT_D = 3.4;  // mm — M3 clearance for foot screws
FOOT_BOLT_N = 2;    // count — M3 SS screws retaining TPU foot
FOOT_BOLT_PITCH = 12; // mm — spacing between foot bolt centres

// M4 heat-set insert in hull boss (main structural attachment, NOT fuse)
// OBSOLETED in Rev R1 — all attachment load is carried through the
// nylon fuse bolts only; hull boss slot walls bear the lateral load.
// Heat-set inserts are therefore NOT used in the hull boss in this revision.

// ---------------------------------------------------------------------------
// Hull boss attachment positions (hull frame, Z = cargo belly bottom ≈ +5 mm)
// ---------------------------------------------------------------------------
// Approximate positions — verify against cargo_sect_shell24.scad belly geometry
// before machining boss sockets into the cargo shell STL.
//
// In hull frame: X = +port, Y = +aft, Z = +dorsal.
// Cargo belly Z ≈ +5 mm (2 mm shell + 3 mm boss floor above belly).
// Port side = hull +X; stbd side = hull -X.
// Legs splay outboard: port legs splay in +X, stbd legs splay in -X.
//
// Format: [X, Y, Z, side]  side = +1 port, -1 stbd
HULL_ATTACH_POS = [
    [ -100,  25,  5,  1 ],  // Port-fore (Shepherd's room area)
    [ -240,  25,  5, -1 ],  // Stbd-fore (Inara's shuttle area)
    [ -100, 100,  5,  1 ],  // Port-aft  (River's room area)
    [ -240, 100,  5, -1 ],  // Stbd-aft  (Simon's medbay area)
];

// ---------------------------------------------------------------------------
// $fn for curved surfaces
// ---------------------------------------------------------------------------
$fn = 32;

// ---------------------------------------------------------------------------
// Module: leg_body()
// CF-PETG flat-spring cantilever leg.  Print upright (leg axis = Z).
// Origin: foot bottom face at Z=0; hull boss insert stub extends from
// Z = FOOT_SOCKET_L + SPRING_L to Z = LEG_TOTAL_L.
// ---------------------------------------------------------------------------
module leg_body() {
    difference() {
        union() {
            // Boss insert stub (solid for shear bolt clamping — no hollow)
            translate([0, 0, FOOT_SOCKET_L + SPRING_L])
                cube([LEG_W, LEG_D, BOSS_INSERT_L]);

            // Spring body — hollow box tube for weight saving
            translate([0, 0, FOOT_SOCKET_L])
                cube([LEG_W, LEG_D, SPRING_L]);

            // Foot socket outer walls (foot TPU presses in from below)
            cube([LEG_W, LEG_D, FOOT_SOCKET_L]);
        }

        // --- Hollow the spring body (box tube) ---
        // Leave LEG_WALL on all four sides; stop WALL above foot socket
        translate([LEG_WALL, LEG_WALL, FOOT_SOCKET_L + LEG_WALL])
            cube([
                LEG_W - 2*LEG_WALL,
                LEG_D - 2*LEG_WALL,
                SPRING_L - 2*LEG_WALL
            ]);

        // --- Foot socket cavity (open bottom, receives TPU foot) ---
        translate([LEG_WALL, LEG_WALL, 0])
            cube([
                LEG_W - 2*LEG_WALL,
                LEG_D - 2*LEG_WALL,
                FOOT_SOCKET_L + 0.1   // small overcut to ensure clean opening
            ]);

        // --- 3× M3 nylon shear bolt holes through boss insert stub ---
        // Bolts pass through the stub in the Y direction (through 10 mm depth)
        // Rows are evenly distributed along the BOSS_INSERT_L zone
        for (i = [0:FUSE_N-1]) {
            z_bolt = FOOT_SOCKET_L + SPRING_L + (i + 0.5) * (BOSS_INSERT_L / FUSE_N);
            translate([LEG_W/2, -1, z_bolt])
                rotate([-90, 0, 0])
                    cylinder(h = LEG_D + 2, d = M3_CLR);
        }

        // --- 2× M3 foot retention screws (from sole/bottom, into foot) ---
        // These are clearance holes in the bottom flange of the foot socket
        translate([LEG_W/2 - FOOT_BOLT_PITCH/2, LEG_D/2, -1])
            cylinder(h = LEG_WALL + 2, d = FOOT_BOLT_D);
        translate([LEG_W/2 + FOOT_BOLT_PITCH/2, LEG_D/2, -1])
            cylinder(h = LEG_WALL + 2, d = FOOT_BOLT_D);

        // --- Safety tether hole (through leg width, near top of spring zone) ---
        // 2 mm Dyneema safety cord; hole through the X dimension of the leg
        translate([-1, LEG_D/2, TETHER_Z])
            rotate([0, 90, 0])
                cylinder(h = LEG_W + 2, d = TETHER_D);
    }
}

// ---------------------------------------------------------------------------
// Module: hull_boss()
// Hull boss receiver — integral to cargo belly shell (CF-PETG).
// Use as a reference / subtraction block when updating cargo_sect_shell24.scad.
// Origin: top face at Z=0 (flush with cargo belly inner face); boss extends
// downward (−Z direction in hull frame) by HULL_BOSS_H.
// ---------------------------------------------------------------------------
module hull_boss() {
    difference() {
        // Boss outer body (solid block)
        translate([-HULL_BOSS_W/2, -HULL_BOSS_D/2, -HULL_BOSS_H])
            cube([HULL_BOSS_W, HULL_BOSS_D, HULL_BOSS_H]);

        // Leg insert slot — accepts boss insert stub from below
        // Clearance 0.2 mm all around for easy assembly
        translate([-(LEG_W/2 + 0.2), -(LEG_D/2 + 0.2), -HULL_BOSS_H - 1])
            cube([LEG_W + 0.4, LEG_D + 0.4, BOSS_INSERT_L + 1]);

        // 3× M3 nylon shear bolt holes — align with leg_body() holes
        for (i = [0:FUSE_N-1]) {
            z_bolt = -HULL_BOSS_H + (i + 0.5) * (BOSS_INSERT_L / FUSE_N);
            translate([0, -HULL_BOSS_D/2 - 1, z_bolt])
                rotate([-90, 0, 0])
                    cylinder(h = HULL_BOSS_D + 2, d = M3_CLR);
        }

        // Safety tether cord pass-through to airframe interior
        // (allows Dyneema cord to route from leg tether hole up into the airframe)
        translate([0, 0, -HULL_BOSS_H/2])
            rotate([0, 90, 0])
                cylinder(h = HULL_BOSS_W, d = TETHER_D + 1, center = true);
    }
}

// ---------------------------------------------------------------------------
// Module: single_leg_in_hull_frame(pos, side)
// Places a leg body in the hull frame coordinate system at the given
// attachment position, applying splay and toe angles.
// pos = [X, Y, Z, side] from HULL_ATTACH_POS
// side = +1 for port (splay in +X), -1 for stbd (splay in -X)
// ---------------------------------------------------------------------------
module single_leg_in_hull_frame(pos) {
    x     = pos[0];
    y     = pos[1];
    z     = pos[2];
    side  = pos[3];

    translate([x, y, z]) {
        // Apply splay (outboard in ±X) and toe (forward = -Y in hull frame)
        // Hull +X = port; leg splay is outboard so:
        //   port leg splays in +X → rotate about hull -Y axis by +SPLAY_ANGLE
        //   stbd leg splays in -X → rotate about hull -Y axis by -SPLAY_ANGLE
        // Toe: forward lean tilts the top of the leg aft (+Y) and the foot fwd (-Y)
        //   → rotate about hull -X axis by +TOE_ANGLE for both port and stbd
        rotate([-TOE_ANGLE, side * (-SPLAY_ANGLE), 0]) {
            // Leg in local frame: Z=up, origin at boss top.
            // In hull frame Z=dorsal(up). Leg hangs downward, so flip:
            // leg local Z → hull -Z direction when hanging.
            translate([0, 0, -LEG_TOTAL_L])
                rotate([0, 180, 0])
                    translate([-LEG_W/2, -LEG_D/2, 0])
                        leg_body();
        }
    }
}

// ---------------------------------------------------------------------------
// Module: assembly()
// Full assembly view in hull frame — all 4 legs + boss outlines.
// Use for layout verification only; not exported to STL.
// ---------------------------------------------------------------------------
module assembly() {
    // Hull reference plane (cargo belly, shown as transparent slab)
    color("SaddleBrown", 0.15)
        translate([-300, -100, 0])
            cube([300, 250, 3]);

    // All 4 legs
    for (pos = HULL_ATTACH_POS) {
        color("DimGray", 0.9)
            single_leg_in_hull_frame(pos);
    }

    // Hull boss outlines at each attachment point
    for (pos = HULL_ATTACH_POS) {
        color("Olive", 0.4)
            translate([pos[0], pos[1], pos[2]])
                hull_boss();
    }
}

// ---------------------------------------------------------------------------
// Entry point
// ---------------------------------------------------------------------------
if (PART == "leg") {
    // Print-orientation: stand upright on foot end (Z=0 at foot, Z=LEG_TOTAL_L at top)
    translate([-LEG_W/2, -LEG_D/2, 0])
        leg_body();

} else if (PART == "boss") {
    // Hull boss: origin at cargo belly inner face, boss extends in -Z
    hull_boss();

} else if (PART == "assy") {
    assembly();
}
