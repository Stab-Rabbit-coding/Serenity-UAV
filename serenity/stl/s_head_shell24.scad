// ============================================================
// s_head_shell24.scad
// Nose / cockpit shell for Serenity Rev N 24" hull (s_head.stl).
//
// Rev Q (2026-05-26): Updated to 2.0 mm foam-fill skin thickness.
//   - Shell source: s_head_shell24_2mm_repaired.stl (blender_shells_v3_2mm.py,
//     voxel-remesh at 1.2 mm pitch, repair_shells_for_scad.py).
//   - WALL_T reduced 4.0 → 3.5 mm (nominal 2.0 mm + 1.5 mm cutter overlap).
//   - 6x M3 heat-set boss posts added at aft joint face (X ≈ 99 mm) for
//     M3 bolts joining head to cargo section.
//   - Foam fill (2 lb/cf closed-cell) provides structural core; bosses provide
//     point-load capacity.  Structural analysis 2026-05-26 confirms 2.0 mm
//     CF-PETG + foam adequate for skin panels at 28 m/s cruise.
//   Ref: structural_analysis.py log, Serenity UAV project, 2026-05-26.
//
// Mounts (all flush with outer mold line -- zero external protrusion):
//   S1A  -- VL53L5CX forward ToF sensor, Array A (FC3 primary), sta 33 mm
//   S1B  -- VL53L5CX forward ToF sensor, Array B (FC2 primary), sta 53 mm
//   FPV  -- 28 mm standard FPV camera, bridge forward-facing viewport, sta 45 mm
//
// GPS patch antenna and 49 MHz RCRS post are on the broad, flat dorsal surface
// of the mid-fuselage section (s_middle_canonical_shell24.scad) where the
// ground plane is larger and the sky view is unobstructed.
//
// Flush-mount design philosophy:
//   Sensor apertures are cut flush through the hull wall.  No boss protrudes
//   above the outer mold line.  PMMA windows (VL53L5CX) and camera lenses
//   (FPV) are retained by M1.6 / M2 countersunk flathead screws from outside
//   and a carrier-board / camera-body recess on the interior.  A shallow
//   0.5 mm registration ring is cut around each aperture on the exterior
//   face to seat the window disc and preserve a clean hull surface.
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
//
// Shell derivation:
//   18" centroid from s_head_shell18.scad: (121.00, -111.43, 51.81)
//   24" centroid = 18" centroid x (2.9294 / 2.1974) = x 1.33333:
//     CX =  121.00 x 1.33333 =  161.33 mm
//     CY = -111.43 x 1.33333 = -148.57 mm
//     CZ =   51.81 x 1.33333 =   69.08 mm
//   Inner scale factors from blender_shells_v3_2mm.py (2.0 mm foam-fill wall):
//     INNER_SX = 0.969083  (dim = 129.4 mm, wall = 2.0 mm)
//     INNER_SY = 0.982987  (dim = 235.1 mm)
//     INNER_SZ = 0.971563  (dim = 140.7 mm)
//
// Coordinate system (24"-scaled STL world space):
//   X -- longitudinal, positive toward nose
//   Y -- vertical,    positive toward dorsal (up)   NOTE: Y is up, not Z
//   Z -- lateral,     positive toward port  (left)
//   Station mapping: X_stl = 284 - station_mm
//
// Hull surface position estimates (wall = 2.0 mm):
//   half_ext_Y = 2.0 / (1 - 0.982987) = 118 mm
//   Hull Y-centreline (nose axis) approx CY = -149 mm
//   Hull Z-centreline approx CZ = 69 mm
//   STL bounds (from voxel-remesh repair): X=99..228, Y=-288..-53, Z=0..141
//
// Sensor references:
//   VL53L5CX: ST UM2884 DocID032910 Rev 1, 2021.
//     FoV 65 deg diagonal; 0.4-4.0 m; 8x8 multizone; 6.4x3.4 mm package.
//     Carrier board approx 13x13 mm; PMMA window disc 11 mm dia.
//   FPV: 28 mm industry-standard mount; 14x14 mm M2 bolt grid; 16 mm aperture.
//
// M3 boss reference:
//   M3 heat-set insert (Ruthex RX-M3x5.7 or equiv): 4.0 mm bore, 5.7 mm OD,
//   5.7 mm installed length.  Boss OD 8.0 mm gives 2-wall annulus per CLAUDE.md.
//   Pullout capacity in CF-PETG: approx 400 N.
//   Ref: Ruthex data sheet, ISO 14589, CLAUDE.md fabrication standards.
//
// IMPORTANT: All mount and boss positions are estimated.  Verify by rendering in
// OpenSCAD and measuring mesh cross-sections in a slicer before printing.
// ============================================================

SCALE_24  = 2.9294;   // 24" hull scale factor

// Head shell centroid in 24"-scaled STL world coordinates
CX =  161.33;   // mm
CY = -148.57;   // mm -- dorsal/ventral axis (positive = up)
CZ =   69.08;   // mm -- lateral axis (positive = port)

// Hollow-shell parameters (Rev R: computed from solid STL bounding box)
// Bounding box of s_head_shell24_repaired.stl after voxel-remesh (1.5 mm pitch):
//   X =   99.2 .. 228.4  → DX = 129.2 mm
//   Y = -287.6 .. -52.7  → DY = 234.9 mm
//   Z =    0.2 .. 140.4  → DZ = 140.2 mm
// Inner scale factors: S = (D - 2 × WALL_MM) / D (centroid-inset approximation).
WALL_MM  = 2.0;
DX = 129.2;
DY = 234.9;
DZ = 140.2;
INNER_SX = (DX - 2 * WALL_MM) / DX;   // = 0.96904
INNER_SY = (DY - 2 * WALL_MM) / DY;   // = 0.98297
INNER_SZ = (DZ - 2 * WALL_MM) / DZ;   // = 0.97147

// Conservative wall thickness for cutter overlap (nominal 2.0 mm + 1.5 mm clearance)
WALL_T = 3.5;   // mm

// M3 heat-set insert boss dimensions
//   Boss added to interior face at joint surfaces; bore accepts M3 heat-set insert.
//   OD 8.0 mm gives minimum 2-wall annulus outside insert per CLAUDE.md requirement.
//   Ref: Ruthex RX-M3x5.7 data sheet; ISO 14589.
BOSS_OD     = 8.0;   // mm -- boss outer diameter
BOSS_H      = 6.0;   // mm -- boss height from interior face (>= insert length 5.7 mm)
BOSS_BORE_D = 4.1;   // mm -- M3 heat-set insert bore (4.0 mm nominal + 0.1 mm clearance)

// VL53L5CX flush mount dimensions
//   Exterior: 11 mm PMMA bore + 0.5 mm x 14 mm OD seat ring + 4x M1.6 c/s holes.
//   Interior: 14x14x3 mm carrier-board recess.
//   Ref: ST UM2884 DocID032910 Rev 1, 2021.
VAPER_D   = 11.0;   // mm -- PMMA window aperture bore
VRING_OD  = 14.0;   // mm -- seat ring outer diameter (0.5 mm recess, hull-flush)
VRING_DEP =  0.5;   // mm -- seat ring recess depth (PMMA rests here, UV-adhesive)
VM16_D    =  1.7;   // mm -- M1.6 through-hole clearance
VM16_R    =  7.0;   // mm -- M1.6 bolt circle radius (4 holes at 90 deg)
VCSK16_OD =  3.5;   // mm -- M1.6 flathead countersink OD  (DIN 7991, 90 deg)
VCSK16_D  =  1.0;   // mm -- M1.6 countersink depth
VRECESS_W = 14.0;   // mm -- carrier board pocket (square)
VRECESS_D =  3.0;   // mm -- carrier board pocket depth (interior face)

// FPV camera flush recess dimensions (28 mm standard FPV format)
//   Exterior: 16 mm lens bore + 29x29x1 mm bezel seating recess + 4x M2 c/s holes.
//   Interior: 20x20x5 mm camera body pocket.
FPV_APER_D   = 16.0;   // mm -- lens aperture bore
FPV_BEZ_W    = 29.0;   // mm -- bezel recess width (28 mm camera + 0.5 mm per side)
FPV_BEZ_DEP  =  1.0;   // mm -- bezel recess depth (camera face sits flush at hull)
FPV_M2_D     =  2.2;   // mm -- M2 through-hole clearance
FPV_M2_S     = 14.0;   // mm -- M2 hole spacing (14x14 mm grid)
FPV_CSK2_OD  =  4.5;   // mm -- M2 flathead countersink OD (DIN 7991, 90 deg)
FPV_CSK2_D   =  1.2;   // mm -- M2 countersink depth
FPV_BOARD_W  = 20.0;   // mm -- camera body pocket width (square)
FPV_BOARD_D  =  5.0;   // mm -- camera body pocket depth (interior)

$fn = 64;

// Orientation rotation vectors
//   STL axes: X=forward, Y=dorsal (+up), Z=port (+left).
//   Ry(+90 deg) maps default +Z cylinder to +X:  rotate([ 0, 90, 0 ])
FWD_ROT = [ 0, 90, 0 ];   // aperture faces +X (toward nose)

// Mount position constants -- 24"-scaled STL world coordinates
//   X_stl = 284 - station_mm.  Y/Z at estimated hull centreline.
//   All positions VERIFY in slicer after rendering.

// Array A forward sensor -- nose centreline, station 33 mm (FC3 primary)
S1A_POS = [ 251, CY, CZ ];            // VERIFY: hull axis at station 33 mm

// Array B forward sensor -- offset for distinct FoV, station 53 mm (FC2 primary)
S1B_POS = [ 231, CY + 8, CZ + 12 ];  // VERIFY: ~15 deg bearing offset from S1A

// Bridge FPV camera -- upper nose, Serenity bridge viewport, station 45 mm
FPV_POS = [ 239, CY + 12, CZ ];      // VERIFY: Y offset toward windshield

// M3 boss positions at aft joint face (X = 99 mm, head-to-cargo mating face).
//   6 bosses distributed around the hull perimeter ellipse.
//   Positions estimated from STL bounds (Y=-288..-53, Z=0..141) and hull centroid.
//   BOSS_AFT_ROT: rotate([0,90,0]) aligns cylinder axis along +X (into interior).
//   All positions VERIFY in slicer -- boss must be fully inside the hull skin.
BOSS_AFT_ROT = [ 0, 90, 0 ];

BOSS_AFT_1 = [  99, CY + 75, CZ       ];  // VERIFY: dorsal face, top of section
BOSS_AFT_2 = [  99, CY + 38, CZ + 52  ];  // VERIFY: dorsal-port quadrant
BOSS_AFT_3 = [  99, CY - 38, CZ + 52  ];  // VERIFY: ventral-port quadrant
BOSS_AFT_4 = [  99, CY - 100, CZ      ];  // VERIFY: ventral face
BOSS_AFT_5 = [  99, CY - 38, CZ - 52  ];  // VERIFY: ventral-stbd quadrant
BOSS_AFT_6 = [  99, CY + 38, CZ - 52  ];  // VERIFY: dorsal-stbd quadrant

// ----------------------------------------------------------------------------
// Module: vlsensor_cut
//   Flush-mount cutter for VL53L5CX.  No protrusion above hull surface.
//   Cuts: aperture bore + 0.5 mm PMMA seat ring + 4x M1.6 c/s holes + board recess.
//   The translate([0,0,-(WALL_T+1)]) places z=0 one mm inside the hull interior;
//   z=WALL_T+1 is the outer hull surface.
// ----------------------------------------------------------------------------
module vlsensor_cut(pos, rot) {
    translate(pos)
    rotate(rot)
    translate([0, 0, -(WALL_T + 1)]) {
        // PMMA aperture bore through full wall
        cylinder(h = WALL_T + 2, d = VAPER_D);

        // PMMA disc seat ring: 0.5 mm recess at exterior face, 14 mm OD
        translate([0, 0, WALL_T + 1 - VRING_DEP])
        cylinder(h = VRING_DEP + 1, d = VRING_OD);

        // 4x M1.6 countersunk through-holes (45 deg diagonal from aperture axes)
        for (a = [45, 135, 225, 315])
            rotate([0, 0, a])
            translate([VM16_R, 0, 0]) {
                // Shaft through wall
                cylinder(h = WALL_T + 2, d = VM16_D);
                // Countersink at exterior face
                translate([0, 0, WALL_T + 1 - VCSK16_D])
                cylinder(h = VCSK16_D + 1, d1 = VM16_D, d2 = VCSK16_OD);
            }

        // Carrier board recess on interior face
        translate([-VRECESS_W / 2, -VRECESS_W / 2, 0])
        cube([VRECESS_W, VRECESS_W, VRECESS_D + 1]);
    }
}

// ----------------------------------------------------------------------------
// Module: fpv_cut
//   Flush recess cutter for 28 mm FPV camera.  Camera face sits flush at hull.
//   Exterior: lens bore + bezel seating recess + 4x M2 c/s holes.
//   Interior: camera body pocket.
// ----------------------------------------------------------------------------
module fpv_cut(pos, rot) {
    translate(pos)
    rotate(rot)
    translate([0, 0, -(WALL_T + 1)]) {
        // Lens aperture bore
        cylinder(h = WALL_T + 2, d = FPV_APER_D);

        // Bezel seating recess: 1 mm deep at exterior, 29x29 mm
        translate([-FPV_BEZ_W / 2, -FPV_BEZ_W / 2, WALL_T + 1 - FPV_BEZ_DEP])
        cube([FPV_BEZ_W, FPV_BEZ_W, FPV_BEZ_DEP + 1]);

        // 4x M2 countersunk mount holes (14x14 mm grid)
        for (dx = [-FPV_M2_S / 2, FPV_M2_S / 2])
        for (dy = [-FPV_M2_S / 2, FPV_M2_S / 2])
            translate([dx, dy, 0]) {
                cylinder(h = WALL_T + 2, d = FPV_M2_D);
                // Countersink at exterior face
                translate([0, 0, WALL_T + 1 - FPV_CSK2_D])
                cylinder(h = FPV_CSK2_D + 1, d1 = FPV_M2_D, d2 = FPV_CSK2_OD);
            }

        // Camera body pocket on interior face
        translate([-FPV_BOARD_W / 2, -FPV_BOARD_W / 2, 0])
        cube([FPV_BOARD_W, FPV_BOARD_W, FPV_BOARD_D + 1]);
    }
}

// ----------------------------------------------------------------------------
// Module: m3_boss
//   Interior M3 heat-set insert boss post.  Solid ring with bore for insert.
//   Added to union() so it is positive material inside the hull skin.
//   Boss cylinder axis along +X by default (BOSS_AFT_ROT = [0, 90, 0]).
//   Ref: Ruthex RX-M3x5.7; ISO 14589; CLAUDE.md min 2-wall annulus requirement.
// ----------------------------------------------------------------------------
module m3_boss(pos, rot) {
    translate(pos)
    rotate(rot)
    difference() {
        // Boss post: solid cylinder, 8 mm OD x 6 mm tall
        cylinder(h = BOSS_H, d = BOSS_OD);
        // Heat-set insert bore: 4.1 mm dia, full height + 0.1 mm clearance
        cylinder(h = BOSS_H + 0.1, d = BOSS_BORE_D);
    }
}

// ============================================================
// Main geometry
// ============================================================
//
// Shell source note (Rev Q):
//   2.0 mm foam-fill skin shell generated by blender_shells_v3_2mm.py
//   (WALL_MM=2.0, SCALE=2.9294x, centroid-inset hollowing) from Thingiverse
//   source s_head.stl.  Repaired to manifold (0 NM edges) by
//   repair_shells_for_scad.py using voxel remesh at 1.2 mm pitch.
//   STL bounds: X=99..228, Y=-288..-53, Z=0..141 mm.
//   Inner scale used: sx=0.969083, sy=0.982987, sz=0.971563.
//   Structural analysis (2026-05-26) confirms 2.0 mm CF-PETG + 2 lb/cf foam fill
//   adequate for skin panels: deflection 0.054 mm at 28 m/s cruise (vs 0.5 mm limit).
//
// ============================================================
// Module: hollow_shell (Rev R — same fix as s_rear_neck_intake_shell24.scad)
// ============================================================
module hollow_shell() {
    difference() {
        import("../../thingverse-serenity/files-hollowed-18in/s_head_shell24_repaired.stl");
        translate([CX, CY, CZ])
            scale([INNER_SX, INNER_SY, INNER_SZ])
            translate([-CX, -CY, -CZ])
                import("../../thingverse-serenity/files-hollowed-18in/s_head_shell24_repaired.stl");
    }
}

union() {
    difference() {
        // 2.0 mm foam-fill head shell — hollowed in SCAD (see hollow_shell above)
        hollow_shell();

        // Flush aperture cuts -- sensors and camera
        vlsensor_cut(S1A_POS, FWD_ROT);
        vlsensor_cut(S1B_POS, FWD_ROT);
        fpv_cut(FPV_POS,      FWD_ROT);
    }

    // 6x M3 boss posts at aft joint face (head → cargo section interface)
    //   Bosses extend into interior (+X) from joint face at X = 99 mm.
    //   VERIFY all boss positions are inside hull skin in slicer before printing.
    m3_boss(BOSS_AFT_1, BOSS_AFT_ROT);
    m3_boss(BOSS_AFT_2, BOSS_AFT_ROT);
    m3_boss(BOSS_AFT_3, BOSS_AFT_ROT);
    m3_boss(BOSS_AFT_4, BOSS_AFT_ROT);
    m3_boss(BOSS_AFT_5, BOSS_AFT_ROT);
    m3_boss(BOSS_AFT_6, BOSS_AFT_ROT);
}
