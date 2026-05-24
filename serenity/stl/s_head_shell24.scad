// ============================================================
// s_head_shell24.scad
// Nose / cockpit shell for Serenity Rev N 24" hull (s_head.stl).
//
// Mounts:
//   S1A  -- VL53L5CX forward ToF sensor, Array A (FC3 primary)
//   S1B  -- VL53L5CX forward ToF sensor, Array B (FC2 primary)
//   FPV  -- 28 mm standard FPV camera, bridge forward-facing viewport
//   GPS  -- 25x25 mm GPS patch antenna dome (dorsal, sta 100 mm)
//   ANT  -- 49 MHz RCRS vertical post boss (dorsal, sta 120 mm)
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
//   Station mapping: X_stl = 284 - station_mm  (nose approx. station 0)
//
//   This non-standard orientation (Y=up) was confirmed from the scoop-cutter
//   geometry in s_rear_neck_intake_shell24.scad where HULL_H2 (half-height)
//   is placed in the Y direction and the four radial cuts rotate around X.
//
// Position estimation method:
//   Hull half-extents from inner scale factors (wall = 2.5 mm):
//     half_ext_a = 2.5 / (1 - INNER_Sa)
//   Dorsal surface Y: CY + half_ext_Y = -148.57 + 88.2 = approx -60 mm
//   Hull Z-centrelineL CZ = 69.08 mm
//   All positions MUST be verified by measuring rendered mesh cross-sections.
//
// Sensor references:
//   VL53L5CX: ST UM2884 user manual, DocID032910 Rev 1, 2021.
//     FoV 65deg diagonal; 0.4-4.0 m; 8x8 zone; 6.4x3.4 mm package.
//   FPV camera: 28 mm industry-standard FPV mount pattern, 14 mm screw grid.
//   GPS patch: GNSS L1 25x25 mm ceramic patch, 3.3 V active amplified.
//   49 MHz RCRS: FCC 47 CFR Part 95 Subpart H; centre-loaded quarter-wave whip.
//
// IMPORTANT: All sensor / camera / antenna mount positions are estimated from
// hull profile data and the station mapping formula.  Verify every position
// by rendering in OpenSCAD and measuring the mesh cross-section before print.
// ============================================================

SCALE_24  = 2.9294;   // 24" hull scale factor

// Head shell centroid in 24"-scaled STL world coordinates
CX =  161.33;   // mm -- longitudinal
CY = -148.57;   // mm -- dorsal/ventral (positive = up)
CZ =   69.08;   // mm -- lateral (positive = port)

// Inner-shell scale factors (preserve 2.5 mm absolute wall thickness)
INNER_SX = 0.948480;
INNER_SY = 0.971650;
INNER_SZ = 0.952614;

// Nominal wall thickness for aperture depth calculations (2.5 mm nominal + tolerance)
WALL_T = 4.0;   // mm

// Estimated hull surface offsets from centroid (wall = 2.5 mm):
//   half_ext_Y = 2.5 / (1 - 0.971650) = 88.2 mm --> dorsal at CY + 88 = approx -60 mm
//   half_ext_Z = 2.5 / (1 - 0.952614) = 52.8 mm --> Z spans CZ +/- 53 mm

// VL53L5CX ToF sensor mount dimensions
//   Ref: ST UM2884 DocID032910 Rev 1, 2021 -- carrier board approx 13x13 mm
VBOSS_OD  = 16.0;   // mm -- boss outer diameter
VBOSS_H   =  3.0;   // mm -- boss protrusion above hull outer surface
VAPER_D   = 11.0;   // mm -- PMMA window bore (UV-adhesive flush mount)
VM16_D    =  1.7;   // mm -- M1.6 through-hole clearance diameter
VM16_R    =  8.0;   // mm -- M1.6 bolt circle radius (4 holes at 90 deg)
VRECESS_W = 14.0;   // mm -- carrier board pocket width (square)
VRECESS_D =  3.0;   // mm -- carrier board pocket depth (interior face)

// Bridge FPV camera mount dimensions (28 mm standard FPV format)
FPV_BOSS_W  = 28.0;   // mm -- square boss footprint
FPV_BOSS_H  =  2.0;   // mm -- boss protrusion above hull surface
FPV_APER_D  = 16.0;   // mm -- lens aperture bore diameter
FPV_M2_D    =  2.2;   // mm -- M2 screw clearance diameter
FPV_M2_S    = 14.0;   // mm -- M2 hole spacing (14x14 mm standard grid)
FPV_BOARD_W = 20.0;   // mm -- camera PCB pocket width (square)
FPV_BOARD_D =  5.0;   // mm -- camera PCB pocket depth (interior face)

// GPS patch antenna dome mount (25x25 mm ceramic patch element)
GPS_BOSS_W  = 32.0;   // mm -- dome mount boss footprint (square)
GPS_BOSS_H  =  3.0;   // mm -- boss protrusion
GPS_PATCH_W = 26.0;   // mm -- patch antenna footprint + 0.5 mm clearance per side
GPS_COAX_D  =  5.0;   // mm -- coax feed-through bore
GPS_M2_D    =  2.2;   // mm -- M2 corner mount screw clearance
GPS_M2_S    = 24.0;   // mm -- M2 bolt spacing (corner to corner)

// 49 MHz RCRS vertical antenna post boss
//   M4 threaded insert pressed from interior; antenna base flange rests on boss top.
ANT49_BOSS_OD    = 14.0;   // mm -- post boss outer diameter
ANT49_BOSS_H     =  5.0;   // mm -- boss protrusion (captures antenna flange)
ANT49_BORE_D     =  4.3;   // mm -- M4 insert through-bore clearance
ANT49_FLANGE_D   = 12.0;   // mm -- antenna base flange recess diameter
ANT49_FLANGE_DEP =  2.0;   // mm -- antenna base flange recess depth (top of boss)

$fn = 64;

// Orientation rotation vectors
//   STL axes: X=forward (+nose), Y=dorsal (+up), Z=port (+left)
//   Rotation derivation uses right-hand Rx/Ry rotation matrices.
//   Default OpenSCAD cylinder axis is +Z; rotate() redirects it to the target.
//
//   FWD    (+X): Ry(+90deg) maps +Z to +X  --> rotate([  0,  90, 0 ])
//   ZENITH (+Y): Rx(-90deg) maps +Z to +Y  --> rotate([ -90,   0, 0 ])
FWD_ROT    = [   0,  90, 0 ];   // boss points in +X (toward nose)
ZENITH_ROT = [ -90,   0, 0 ];   // boss points in +Y (toward dorsal/up)

// Mount position constants -- 24"-scaled STL world coordinates
//   X_stl = 284 - station_mm; dorsal surface approx. CY + 88; Z centreline approx. CZ.
//   All positions are estimates; VERIFY by measuring rendered mesh in slicer.

// Array A forward sensor -- nose centreline, station 33 mm (FC3 primary)
S1A_POS = [ 251, CY, CZ ];            // VERIFY: approximates hull axis at sta 33 mm

// Array B forward sensor -- offset for distinct FoV, station 53 mm (FC2 primary)
S1B_POS = [ 231, CY + 8, CZ + 12 ];  // VERIFY: ~15 deg bearing offset from S1A

// Bridge FPV camera -- upper nose centre (Serenity bridge viewport), station 45 mm
FPV_POS = [ 239, CY + 12, CZ ];      // VERIFY: Y shifted upward toward windshield

// GPS patch antenna -- dorsal hull surface, station 100 mm from nose
GPS_POS = [ 184, CY + 88, CZ ];      // VERIFY: CY+88 approx dorsal surface

// 49 MHz RCRS antenna post -- dorsal hull surface, station 120 mm from nose
ANT49_POS = [ 164, CY + 88, CZ ];    // VERIFY: same dorsal ridge, 20 mm aft of GPS

// ----------------------------------------------------------------------------
// Module: vlsensor_boss
//   Solid boss cylinder for VL53L5CX flush-mount; 4x M1.6 shoulder bosses.
//   Union this into the outer shell geometry.
// ----------------------------------------------------------------------------
module vlsensor_boss(pos, rot) {
    translate(pos)
    rotate(rot)
    union() {
        cylinder(h = VBOSS_H, d = VBOSS_OD);
        // 4x M1.6 shoulder bosses at 45 deg diagonal positions
        for (a = [45, 135, 225, 315])
            rotate([0, 0, a])
            translate([VM16_R, 0, 0])
            cylinder(h = VBOSS_H, d = VM16_D + 1.2);   // head-clearance flange
    }
}

// ----------------------------------------------------------------------------
// Module: vlsensor_cut
//   Aperture bore + M1.6 through-holes + carrier board recess.
//   Subtract from assembled union after all bosses are added.
// ----------------------------------------------------------------------------
module vlsensor_cut(pos, rot) {
    translate(pos)
    rotate(rot)
    translate([0, 0, -(WALL_T + 1)]) {
        // PMMA window aperture bore (interior through boss exterior + 1 mm)
        cylinder(h = WALL_T + VBOSS_H + 2, d = VAPER_D);
        // 4x M1.6 through-holes at 45 deg diagonal positions
        for (a = [45, 135, 225, 315])
            rotate([0, 0, a])
            translate([VM16_R, 0, 0])
            cylinder(h = WALL_T + VBOSS_H + 2, d = VM16_D);
        // Carrier board pocket on interior face
        translate([-VRECESS_W / 2, -VRECESS_W / 2, 0])
        cube([VRECESS_W, VRECESS_W, VRECESS_D + 1]);
    }
}

// ----------------------------------------------------------------------------
// Module: fpv_boss
//   Square raised boss for 28 mm standard FPV camera.
// ----------------------------------------------------------------------------
module fpv_boss(pos, rot) {
    translate(pos)
    rotate(rot)
    translate([-FPV_BOSS_W / 2, -FPV_BOSS_W / 2, 0])
    cube([FPV_BOSS_W, FPV_BOSS_W, FPV_BOSS_H]);
}

// ----------------------------------------------------------------------------
// Module: fpv_cut
//   Lens aperture bore + 4x M2 through-holes + camera PCB pocket.
// ----------------------------------------------------------------------------
module fpv_cut(pos, rot) {
    translate(pos)
    rotate(rot)
    translate([0, 0, -(WALL_T + 1)]) {
        // Lens aperture
        cylinder(h = WALL_T + FPV_BOSS_H + 2, d = FPV_APER_D);
        // 4x M2 mount holes (14x14 mm grid pattern)
        for (dx = [-FPV_M2_S / 2, FPV_M2_S / 2])
        for (dy = [-FPV_M2_S / 2, FPV_M2_S / 2])
            translate([dx, dy, 0])
            cylinder(h = WALL_T + FPV_BOSS_H + 2, d = FPV_M2_D);
        // Camera PCB pocket on interior face
        translate([-FPV_BOARD_W / 2, -FPV_BOARD_W / 2, 0])
        cube([FPV_BOARD_W, FPV_BOARD_W, FPV_BOARD_D + 1]);
    }
}

// ----------------------------------------------------------------------------
// Module: gps_boss
//   Square ring boss for GPS patch antenna cover plate (dome printed separately).
// ----------------------------------------------------------------------------
module gps_boss(pos, rot) {
    translate(pos)
    rotate(rot)
    difference() {
        // Outer ring
        translate([-GPS_BOSS_W / 2, -GPS_BOSS_W / 2, 0])
        cube([GPS_BOSS_W, GPS_BOSS_W, GPS_BOSS_H]);
        // Inner recess for patch antenna (leaves 3 mm wall around patch aperture)
        translate([-(GPS_PATCH_W - 4) / 2, -(GPS_PATCH_W - 4) / 2, 1.0])
        cube([GPS_PATCH_W - 4, GPS_PATCH_W - 4, GPS_BOSS_H]);
    }
}

// ----------------------------------------------------------------------------
// Module: gps_cut
//   Square patch pocket + coax feed-through + 4x M2 corner holes.
// ----------------------------------------------------------------------------
module gps_cut(pos, rot) {
    translate(pos)
    rotate(rot)
    translate([0, 0, -(WALL_T + 1)]) {
        // Square patch antenna pocket through hull wall
        translate([-GPS_PATCH_W / 2, -GPS_PATCH_W / 2, 0])
        cube([GPS_PATCH_W, GPS_PATCH_W, WALL_T + GPS_BOSS_H + 2]);
        // Coax feed-through bore at patch centre
        cylinder(h = WALL_T + GPS_BOSS_H + 2, d = GPS_COAX_D);
        // 4x M2 corner mount holes
        for (dx = [-GPS_M2_S / 2, GPS_M2_S / 2])
        for (dy = [-GPS_M2_S / 2, GPS_M2_S / 2])
            translate([dx, dy, 0])
            cylinder(h = WALL_T + GPS_BOSS_H + 2, d = GPS_M2_D);
    }
}

// ----------------------------------------------------------------------------
// Module: ant49_boss
//   Cylinder post boss for 49 MHz RCRS whip antenna base.
// ----------------------------------------------------------------------------
module ant49_boss(pos, rot) {
    translate(pos)
    rotate(rot)
    cylinder(h = ANT49_BOSS_H, d = ANT49_BOSS_OD);
}

// ----------------------------------------------------------------------------
// Module: ant49_cut
//   M4 insert bore through hull + antenna base flange recess on boss top.
// ----------------------------------------------------------------------------
module ant49_cut(pos, rot) {
    translate(pos)
    rotate(rot) {
        // M4 insert bore (through hull wall and boss)
        translate([0, 0, -(WALL_T + 1)])
        cylinder(h = WALL_T + ANT49_BOSS_H + 2, d = ANT49_BORE_D);
        // Antenna base flange countersink on boss top exterior
        translate([0, 0, ANT49_BOSS_H - ANT49_FLANGE_DEP])
        cylinder(h = ANT49_FLANGE_DEP + 1, d = ANT49_FLANGE_D);
    }
}

// ============================================================
// Main geometry
// ============================================================
difference() {
    union() {
        // Canonical 24" head shell (outer minus inner void)
        difference() {
            scale([SCALE_24, SCALE_24, SCALE_24])
                import("../../thingverse-serenity/files/s_head.stl");

            translate([CX, CY, CZ])
            scale([INNER_SX, INNER_SY, INNER_SZ])
            translate([-CX, -CY, -CZ])
            scale([SCALE_24, SCALE_24, SCALE_24])
                import("../../thingverse-serenity/files/s_head.stl");
        }

        // Sensor / camera / antenna bosses (additive)
        vlsensor_boss(S1A_POS,  FWD_ROT);
        vlsensor_boss(S1B_POS,  FWD_ROT);
        fpv_boss(FPV_POS,       FWD_ROT);
        gps_boss(GPS_POS,       ZENITH_ROT);
        ant49_boss(ANT49_POS,   ZENITH_ROT);
    }

    // Apertures, through-holes, and interior recesses (subtractive)
    vlsensor_cut(S1A_POS,  FWD_ROT);
    vlsensor_cut(S1B_POS,  FWD_ROT);
    fpv_cut(FPV_POS,       FWD_ROT);
    gps_cut(GPS_POS,       ZENITH_ROT);
    ant49_cut(ANT49_POS,   ZENITH_ROT);
}
