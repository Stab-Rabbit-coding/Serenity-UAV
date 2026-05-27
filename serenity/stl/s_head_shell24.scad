// ============================================================
// s_head_shell24.scad
// Nose / cockpit shell for Serenity Rev N 24" hull (s_head.stl).
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
//   Inner scale factors from s_head_shell18.scad (same 2.5 mm absolute wall):
//     INNER_SX = 0.948480
//     INNER_SY = 0.971650
//     INNER_SZ = 0.952614
//
// Coordinate system (24"-scaled STL world space):
//   X -- longitudinal, positive toward nose
//   Y -- vertical,    positive toward dorsal (up)   NOTE: Y is up, not Z
//   Z -- lateral,     positive toward port  (left)
//   Station mapping: X_stl = 284 - station_mm
//
// Hull surface position estimates (wall = 2.5 mm):
//   half_ext_Y = 2.5 / (1 - 0.971650) = 88 mm
//   Hull Y-centreline (nose axis) approx CY = -149 mm
//   Hull Z-centreline approx CZ = 69 mm
//
// Sensor references:
//   VL53L5CX: ST UM2884 DocID032910 Rev 1, 2021.
//     FoV 65 deg diagonal; 0.4-4.0 m; 8x8 multizone; 6.4x3.4 mm package.
//     Carrier board approx 13x13 mm; PMMA window disc 11 mm dia.
//   FPV: 28 mm industry-standard mount; 14x14 mm M2 bolt grid; 16 mm aperture.
//
// IMPORTANT: All mount positions are estimated.  Verify by rendering in
// OpenSCAD and measuring mesh cross-sections in a slicer before printing.
// ============================================================

SCALE_24  = 2.9294;   // 24" hull scale factor

// Head shell centroid in 24"-scaled STL world coordinates
CX =  161.33;   // mm
CY = -148.57;   // mm -- dorsal/ventral axis (positive = up)
CZ =   69.08;   // mm -- lateral axis (positive = port)

// Inner-shell scale factors (2.5 mm absolute wall)
INNER_SX = 0.948480;
INNER_SY = 0.971650;
INNER_SZ = 0.952614;

// Conservative wall thickness for cutter overlap
WALL_T = 4.0;   // mm (nominal 2.5 mm + clearance)

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

// ============================================================
// Main geometry
// ============================================================
//
// Shell source note:
//   The 24" head shell was derived by Blender (blender_hollow_shells.py) from
//   the Thingiverse source s_head.stl via outer minus slightly-shrunk-inner
//   subtraction, then scaled to 24" (SCALE_24 = 2.9294).  The Thingiverse
//   source and all derived pre-computed shells carry open-edge non-manifold
//   geometry that CGAL cannot process in boolean operations.  The repaired
//   manifold version (s_head_shell24_repaired.stl) was created by
//   repair_shells_for_scad.py using Blender voxel remesh at 1.5 mm pitch.
//
difference() {
    // Canonical 24" head shell — manifold version for CGAL boolean operations
    import("../../thingverse-serenity/files-hollowed-18in/s_head_shell24_repaired.stl");

    // Flush aperture cuts -- sensors and camera
    vlsensor_cut(S1A_POS, FWD_ROT);
    vlsensor_cut(S1B_POS, FWD_ROT);
    fpv_cut(FPV_POS,      FWD_ROT);
}
