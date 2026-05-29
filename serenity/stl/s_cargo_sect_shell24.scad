// ============================================================
// s_cargo_sect_shell24.scad
// Cargo gondola shell for Serenity Rev N 24" hull (s_cargo_sect.stl).
//
// Rev Q (2026-05-26): Updated to 2.0 mm foam-fill skin thickness.
//   - Shell source: s_cargo_sect_shell24_2mm_repaired.stl
//     (blender_shells_v3_2mm.py, voxel-remesh 1.2 mm pitch).
//   - WALL_T reduced 4.0 → 3.5 mm (nominal 2.0 mm + 1.5 mm cutter overlap).
//   - 6x M3 boss posts at fore joint face (X = -7 mm, cargo-to-mid junction).
//   - 6x M3 boss posts at aft joint face (X = -202 mm, cargo-to-rear junction).
//   - 2x interior belly stiffener ribs at X = -70 mm and X = -140 mm to limit
//     nadir skin panel deflection (Z span 163 mm and X span 195 mm both exceed
//     124 mm max-unbraced threshold at 2.0 mm wall without foam cure).
//   - Foam fill (2 lb/cf) carries distributed panel load; ribs handle seam-
//     zone stress concentrations and provide printing registration surfaces.
//   Ref: structural_analysis.py log, Serenity UAV project, 2026-05-26.
//
// Mounts (flush with outer mold line -- zero external protrusion):
//   CARGO_CAM -- 28 mm standard FPV camera, nadir-facing (downward),
//                belly of cargo gondola for payload hoist monitoring.
//
// Flush-mount design:
//   Camera face sits flush at the gondola belly skin.  A 29x29x1 mm bezel
//   recess on the exterior face seats the camera body; the lens protrudes
//   through a 16 mm bore.  4x M2 countersunk flathead screws (DIN 7991)
//   retain the camera from outside.  A 20x20x5 mm pocket on the interior
//   houses the camera body.
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
//
// Shell derivation:
//   18" centroid from s_cargo_sect_shell18.scad: (-76.64, -246.47, 56.02)
//   24" centroid = 18" centroid x (2.9294 / 2.1974) = x 1.33333:
//     CX =  -76.64 x 1.33333 = -102.19 mm
//     CY = -246.47 x 1.33333 = -328.63 mm
//     CZ =   56.02 x 1.33333 =   74.70 mm
//   Inner scale factors from blender_shells_v3_2mm.py (2.0 mm foam-fill wall):
//     INNER_SX = 0.979459  (dim = 194.7 mm, wall = 2.0 mm)
//     INNER_SY = 0.980354  (dim = 203.6 mm)
//     INNER_SZ = 0.975496  (dim = 163.2 mm)
//
// Coordinate system (24"-scaled STL world space):
//   X -- longitudinal, positive toward nose
//   Y -- vertical,    positive toward dorsal (up)   NOTE: Y is up, not Z
//   Z -- lateral,     positive toward port  (left)
//
// Note on cargo gondola geometry:
//   CY = -328.63 mm places the gondola well below the main fuselage keel.
//   STL bounds (voxel-remesh repair): X=-202..-7, Y=-415..-211, Z=0..163.
//   Nadir (downward, -Y) face approx Y = -415 mm (exterior).
//   Interior belly face at approx Y = -413 mm (2.0 mm wall).
//   All boss and rib positions VERIFY by measuring rendered mesh in slicer.
//
// M3 boss reference:
//   M3 heat-set insert (Ruthex RX-M3x5.7 or equiv): 4.0 mm bore, 5.7 mm OD.
//   Boss OD 8.0 mm gives 2-wall annulus per CLAUDE.md fabrication requirements.
//   Pullout capacity in CF-PETG: approx 400 N.
//   Ref: Ruthex data sheet, ISO 14589, CLAUDE.md fabrication standards.
//
// IMPORTANT: Verify all mount, boss, and rib positions by measuring mesh
// cross-sections in a slicer before printing.
// ============================================================

SCALE_24  = 2.9294;   // 24" hull scale factor

// Cargo gondola centroid in 24"-scaled STL world coordinates
CX = -102.19;   // mm
CY = -328.63;   // mm -- dorsal/ventral axis (positive = up)
CZ =   74.70;   // mm -- lateral axis (positive = port)

// Inner-shell scale factors (2.0 mm foam-fill wall)
// Source: blender_shells_v3_2mm.py console output 2026-05-26
INNER_SX = 0.979459;
INNER_SY = 0.980354;
INNER_SZ = 0.975496;

// Conservative wall thickness for cutter overlap (nominal 2.0 mm + 1.5 mm clearance)
WALL_T = 3.5;   // mm

// M3 heat-set insert boss dimensions
//   Boss OD 8.0 mm gives minimum 2-wall annulus outside insert per CLAUDE.md.
//   Ref: Ruthex RX-M3x5.7 data sheet; ISO 14589.
BOSS_OD     = 8.0;   // mm -- boss outer diameter
BOSS_H      = 6.0;   // mm -- boss height from interior face (>= insert length 5.7 mm)
BOSS_BORE_D = 4.1;   // mm -- M3 heat-set insert bore (4.0 mm nominal + 0.1 mm clearance)

// Belly stiffener rib dimensions
//   Two X-aligned cross-ribs on interior belly face spanning Z.
//   Spaced at ~65 mm intervals across the 195 mm X extent to keep
//   unbraced belly panel X-spans under 80 mm.
//   Ref: max unbraced span per structural_analysis.py 2026-05-26.
BELLY_INT_Y  = -413;   // mm -- interior belly face (Y=-415 exterior + 2 mm wall)
BELLY_RIB_H  =    4;   // mm -- rib height (inward from interior face toward keel)
BELLY_RIB_T  =    2;   // mm -- rib wall thickness
BELLY_RIB_Z0 =    0;   // mm -- Z start of rib span
BELLY_RIB_Z1 =  163;   // mm -- Z end of rib span

// FPV camera flush recess dimensions (28 mm standard FPV format)
//   Exterior: 16 mm bore + 29x29x1 mm bezel recess + 4x M2 c/s holes.
//   Interior: 20x20x5 mm camera body pocket.
FPV_APER_D   = 16.0;   // mm -- lens aperture bore
FPV_BEZ_W    = 29.0;   // mm -- bezel recess width (28 mm camera + 0.5 mm per side)
FPV_BEZ_DEP  =  1.0;   // mm -- bezel recess depth (camera face sits flush with skin)
FPV_M2_D     =  2.2;   // mm -- M2 through-hole clearance
FPV_M2_S     = 14.0;   // mm -- M2 hole spacing (14x14 mm standard grid)
FPV_CSK2_OD  =  4.5;   // mm -- M2 flathead c/s OD (DIN 7991, 90 deg)
FPV_CSK2_D   =  1.2;   // mm -- M2 c/s depth
FPV_BOARD_W  = 20.0;   // mm -- camera body pocket width (square)
FPV_BOARD_D  =  5.0;   // mm -- camera body pocket depth (interior)

$fn = 64;

// Orientation rotation vectors
//   STL axes: X=forward, Y=dorsal (+up), Z=port (+left).
//   Rx(+90 deg) maps +Z -> -Y (nadir / downward): rotate([ 90, 0, 0 ])
NADIR_ROT = [ 90, 0, 0 ];   // aperture faces -Y (toward ground)

// Cargo nadir camera position
//   Interior belly face at Y=-413; camera centred on gondola X/Z centreline.
//   VERIFY gondola belly Y-coordinate in slicer before printing.
CARGO_CAM_POS = [ CX, CY - 76, CZ ];   // VERIFY: gondola belly, nadir face

// M3 boss positions at fore joint face (X = -7 mm, cargo fore end).
//   Bosses extend from fore face into interior (-X direction).
//   BOSS_FORE_ROT: rotate([0,-90,0]) aligns cylinder axis along -X (into interior).
//   Bounds at X=-7 joint: Y=-415..-211, Z=0..163; centroid CY=-329, CZ=75.
//   All positions VERIFY in slicer -- boss must sit fully inside hull skin.
BOSS_FORE_ROT = [ 0, -90, 0 ];

BOSS_FORE_1 = [ -7, CY + 82,  CZ       ];  // VERIFY: dorsal, near Y=-247
BOSS_FORE_2 = [ -7, CY + 41,  CZ + 55  ];  // VERIFY: dorsal-port
BOSS_FORE_3 = [ -7, CY - 41,  CZ + 55  ];  // VERIFY: ventral-port
BOSS_FORE_4 = [ -7, CY - 82,  CZ       ];  // VERIFY: ventral, near Y=-411
BOSS_FORE_5 = [ -7, CY - 41,  CZ - 55  ];  // VERIFY: ventral-stbd
BOSS_FORE_6 = [ -7, CY + 41,  CZ - 55  ];  // VERIFY: dorsal-stbd

// M3 boss positions at aft joint face (X = -202 mm, cargo aft end).
//   Bosses extend from aft face into interior (+X direction).
//   BOSS_AFT_ROT: rotate([0,90,0]) aligns cylinder axis along +X (into interior).
BOSS_AFT_ROT = [ 0, 90, 0 ];

BOSS_AFT_1 = [ -202, CY + 82,  CZ       ];  // VERIFY: dorsal
BOSS_AFT_2 = [ -202, CY + 41,  CZ + 55  ];  // VERIFY: dorsal-port
BOSS_AFT_3 = [ -202, CY - 41,  CZ + 55  ];  // VERIFY: ventral-port
BOSS_AFT_4 = [ -202, CY - 82,  CZ       ];  // VERIFY: ventral
BOSS_AFT_5 = [ -202, CY - 41,  CZ - 55  ];  // VERIFY: ventral-stbd
BOSS_AFT_6 = [ -202, CY + 41,  CZ - 55  ];  // VERIFY: dorsal-stbd

// ----------------------------------------------------------------------------
// Module: fpv_cut
//   Flush recess cutter for 28 mm FPV camera.  Zero protrusion above skin.
//   Lens bore + bezel seating recess + 4x M2 c/s holes + camera body pocket.
// ----------------------------------------------------------------------------
module fpv_cut(pos, rot) {
    translate(pos)
    rotate(rot)
    translate([0, 0, -(WALL_T + 1)]) {
        // Lens aperture bore
        cylinder(h = WALL_T + 2, d = FPV_APER_D);

        // Bezel seating recess: 1 mm deep at exterior face, 29x29 mm
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
//   Added to union() as positive material inside hull skin.
//   Rotate to align cylinder axis with desired inward direction before call.
//   Ref: Ruthex RX-M3x5.7; ISO 14589; CLAUDE.md min 2-wall annulus.
// ----------------------------------------------------------------------------
module m3_boss(pos, rot) {
    translate(pos)
    rotate(rot)
    difference() {
        // Boss post: 8 mm OD x 6 mm tall
        cylinder(h = BOSS_H, d = BOSS_OD);
        // Heat-set insert bore: 4.1 mm dia, through height + 0.1 mm clearance
        cylinder(h = BOSS_H + 0.1, d = BOSS_BORE_D);
    }
}

// ----------------------------------------------------------------------------
// Module: belly_rib
//   Interior stiffener rib on cargo gondola nadir (belly) face.
//   Thin cross-wall (X-parallel) anchored at interior belly face, spanning Z.
//   Added to union() as positive material fused to interior skin face.
//   Position VERIFY: rib must be fully inside hull skin in slicer.
// ----------------------------------------------------------------------------
module belly_rib(x_pos) {
    translate([x_pos - BELLY_RIB_T / 2, BELLY_INT_Y, BELLY_RIB_Z0])
    cube([BELLY_RIB_T, BELLY_RIB_H, BELLY_RIB_Z1 - BELLY_RIB_Z0]);
}

// ============================================================
// Main geometry
// ============================================================
//
// Shell source note (Rev Q):
//   2.0 mm foam-fill skin shell generated by blender_shells_v3_2mm.py
//   (WALL_MM=2.0, SCALE=2.9294x, centroid-inset hollowing) from Thingiverse
//   source s_cargo_sect.stl.  Repaired to manifold (0 NM edges) by
//   repair_shells_for_scad.py using voxel remesh at 1.2 mm pitch.
//   STL bounds: X=-202..-7, Y=-415..-211, Z=0..163 mm.
//   Inner scale used: sx=0.979459, sy=0.980354, sz=0.975496.
//
union() {
    difference() {
        // 2.0 mm foam-fill cargo gondola shell -- manifold for CGAL boolean ops
        import("../../thingverse-serenity/files-hollowed-18in/s_cargo_sect_shell24_2mm_repaired.stl");

        // Nadir camera flush aperture
        fpv_cut(CARGO_CAM_POS, NADIR_ROT);
    }

    // 6x M3 boss posts at fore joint face (X = -7 mm, cargo → mid junction)
    //   Bosses extend into interior (-X) from fore joint face.
    //   VERIFY all boss positions inside hull skin before printing.
    m3_boss(BOSS_FORE_1, BOSS_FORE_ROT);
    m3_boss(BOSS_FORE_2, BOSS_FORE_ROT);
    m3_boss(BOSS_FORE_3, BOSS_FORE_ROT);
    m3_boss(BOSS_FORE_4, BOSS_FORE_ROT);
    m3_boss(BOSS_FORE_5, BOSS_FORE_ROT);
    m3_boss(BOSS_FORE_6, BOSS_FORE_ROT);

    // 6x M3 boss posts at aft joint face (X = -202 mm, cargo → rear junction)
    //   Bosses extend into interior (+X) from aft joint face.
    m3_boss(BOSS_AFT_1, BOSS_AFT_ROT);
    m3_boss(BOSS_AFT_2, BOSS_AFT_ROT);
    m3_boss(BOSS_AFT_3, BOSS_AFT_ROT);
    m3_boss(BOSS_AFT_4, BOSS_AFT_ROT);
    m3_boss(BOSS_AFT_5, BOSS_AFT_ROT);
    m3_boss(BOSS_AFT_6, BOSS_AFT_ROT);

    // 2x belly stiffener ribs on interior nadir face, spanning Z.
    //   Rib at X=-70: splits fore zone (X=-7..-133, ~126 mm) into 63 mm halves.
    //   Rib at X=-140: splits aft zone (X=-68..-202, ~134 mm) into 67 mm halves.
    //   VERIFY rib positions are inside hull skin in slicer before printing.
    belly_rib(-70);
    belly_rib(-140);
}
