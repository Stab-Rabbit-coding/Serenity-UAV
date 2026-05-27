// ============================================================
// s_cargo_sect_shell24.scad
// Cargo gondola shell for Serenity Rev N 24" hull (s_cargo_sect.stl).
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
//   Inner scale factors from s_cargo_sect_shell18.scad (2.5 mm absolute wall):
//     INNER_SX = 0.965771
//     INNER_SY = 0.967263
//     INNER_SZ = 0.959167
//
// Coordinate system (24"-scaled STL world space):
//   X -- longitudinal, positive toward nose
//   Y -- vertical,    positive toward dorsal (up)   NOTE: Y is up, not Z
//   Z -- lateral,     positive toward port  (left)
//
// Note on cargo gondola geometry:
//   CY = -328.63 mm places the gondola well below the main fuselage keel in
//   the Thingiverse model's coordinate frame.  The nadir (downward, -Y) face
//   of the gondola is at approximately CY - half_ext_Y.
//   half_ext_Y = 2.5 / (1 - 0.967263) = 76.3 mm
//   Gondola belly (nadir face): CY - 76 = approx -405 mm
//   All positions VERIFY by measuring rendered mesh in slicer.
//
// IMPORTANT: Verify gondola belly Y-coordinate in slicer before printing.
// ============================================================

SCALE_24  = 2.9294;   // 24" hull scale factor

// Cargo gondola centroid in 24"-scaled STL world coordinates
CX = -102.19;   // mm
CY = -328.63;   // mm -- dorsal/ventral axis (positive = up)
CZ =   74.70;   // mm -- lateral axis (positive = port)

// Inner-shell scale factors (2.5 mm absolute wall)
INNER_SX = 0.965771;
INNER_SY = 0.967263;
INNER_SZ = 0.959167;

// Conservative wall thickness for cutter overlap
WALL_T = 4.0;   // mm

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
//   Gondola belly (nadir face) estimated at CY - 76 = approx -405 mm.
//   Camera centred on gondola X/Z centreline.
//   VERIFY gondola belly Y-coordinate in slicer before printing.
CARGO_CAM_POS = [ CX, CY - 76, CZ ];   // VERIFY: gondola belly, nadir face

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

// ============================================================
// Main geometry
// ============================================================
//
// Shell source note:
//   The 24" cargo gondola shell was derived by Blender (blender_hollow_shells.py)
//   from the Thingiverse source s_cargo_sect.stl.  The Thingiverse source and all
//   derived pre-computed shells carry open-edge non-manifold geometry that CGAL
//   cannot process in boolean operations.  The repaired manifold version
//   (s_cargo_sect_shell24_repaired.stl) was created by repair_shells_for_scad.py
//   using Blender voxel remesh at 1.5 mm pitch.
//
difference() {
    // Canonical 24" cargo gondola shell — manifold version for CGAL boolean ops
    import("../../thingverse-serenity/files-hollowed-18in/s_cargo_sect_shell24_repaired.stl");

    // Nadir camera flush aperture
    fpv_cut(CARGO_CAM_POS, NADIR_ROT);
}
