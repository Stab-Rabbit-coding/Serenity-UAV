// ============================================================
// s_middle_canonical_shell24.scad
// Mid-fuselage shell for Serenity Rev N 24" hull (s_middle.stl).
// Belly restored to standard Serenity geometry -- NO belly scoop.
// Replaces s_middle_intake_shell24.stl for the 4-radial-intake Rev N build.
//
// Mounts:
//   S3A  -- VL53L5CX port-side ToF sensor,     Array A (FC3 primary), sta 267 mm
//   S4A  -- VL53L5CX stbd-side ToF sensor,     Array A (FC3 primary), sta 267 mm
//   S3B  -- VL53L5CX port-side ToF sensor,     Array B (FC2 primary), sta 200 mm
//   S4B  -- VL53L5CX stbd-side ToF sensor,     Array B (FC2 primary), sta 200 mm
//   S5A  -- VL53L5CX zenith ToF sensor,        Array A (FC3 primary), sta 240 mm
//   S5B  -- VL53L5CX zenith ToF sensor,        Array B (FC2 primary), sta 347 mm
//   S6A  -- VL53L5CX nadir ToF sensor,         Array A (FC3 primary), sta 213 mm
//   S6B  -- VL53L5CX nadir ToF sensor,         Array B (FC2 primary), sta 293 mm
//   SiK  -- SMA bulkhead, SiK 915 MHz telemetry (port side, sta 224 mm)
//   ZBE  -- SMA bulkhead, ZigBee 2.4 GHz (stbd side, sta 224 mm)
//   WIFI -- SMA bulkhead, WiFi 5 GHz (port side, sta 264 mm)
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
//
// Shell generation pattern from thingverse-serenity/files-hollowed-18in/:
//   Shell = outer STL - (scale-inner x shifted-inner STL)
//   Inner scale factors derived from 2.5 mm wall at 18" (same absolute wall at 24").
//
// Scale factor 24" hull: SCALE_24 = 2.9294 (24" / original model unit)
// Centroid of s_middle.stl at 24" scale:
//   CX = 135.712 x (2.9294/2.1974) = 180.95 mm
//   CY = -50.459 x (2.9294/2.1974) = -67.28 mm
//   CZ =  27.348 x (2.9294/2.1974) =  36.47 mm
// Inner scale factors (from 18" scad -- wall is absolute not proportional):
//   INNER_SX = 0.962373
//   INNER_SY = 0.959565
//   INNER_SZ = 0.908966
//
// Coordinate system (24"-scaled STL world space):
//   X -- longitudinal, positive toward nose
//   Y -- vertical,    positive toward dorsal (up)   NOTE: Y is up, not Z
//   Z -- lateral,     positive toward port  (left)
//
// Position estimation method (wall = 2.5 mm):
//   half_ext_a = 2.5 / (1 - INNER_Sa)
//   half_ext_Y = 2.5 / (1 - 0.959565) = 61.8 mm
//     Dorsal surface:  CY + 62 = -67.28 + 62 = approx -5 mm
//     Ventral surface: CY - 62 = -67.28 - 62 = approx -129 mm
//   half_ext_Z = 2.5 / (1 - 0.908966) = 27.5 mm
//     Port surface:    CZ + 28 = 36.47 + 28 = approx  64 mm
//     Stbd surface:    CZ - 28 = 36.47 - 28 = approx   9 mm
//
// All mount positions are estimates. VERIFY by measuring rendered mesh in slicer.
//
// Dual-redundant sensor array wiring:
//   Array A sensors: I2C bus 3, TCA9548A mux 0x70, addresses 0x54-0x56
//   Array B sensors: I2C bus 2, TCA9548A mux 0x71, addresses 0x54-0x56
//   Each array controlled by a separate FC SBC for hardware failover.
//   Ref: ST UM2884 DocID032910 Rev 1, 2021 (VL53L5CX user manual).
// ============================================================

SCALE_24  = 2.9294;   // 24" hull scale factor

// Mid-fuselage shell centroid in 24"-scaled STL world coordinates
CX =  180.95;   // mm -- longitudinal
CY =  -67.28;   // mm -- dorsal/ventral (positive = up)
CZ =   36.47;   // mm -- lateral (positive = port)

// Inner-shell scale factors (preserve 2.5 mm absolute wall thickness)
INNER_SX = 0.962373;
INNER_SY = 0.959565;
INNER_SZ = 0.908966;

// Nominal wall thickness for aperture depth calculations
WALL_T = 4.0;   // mm (2.5 mm nominal + tolerance)

// Hull surface coordinates estimated from centroid + half-extents:
DORSAL_Y  = CY + 62;    // approx -5 mm
VENTRAL_Y = CY - 62;    // approx -129 mm
PORT_Z    = CZ + 28;    // approx 64 mm
STBD_Z    = CZ - 28;    // approx 9 mm
MID_Y     = CY;         // approx -67 mm (hull cross-section mid-height)
MID_Z     = CZ;         // approx 36 mm (hull Z centreline)

// VL53L5CX ToF sensor mount dimensions
//   Ref: ST UM2884 DocID032910 Rev 1, 2021 -- carrier board approx 13x13 mm
VBOSS_OD  = 16.0;   // mm -- boss outer diameter
VBOSS_H   =  3.0;   // mm -- boss protrusion above hull outer surface
VAPER_D   = 11.0;   // mm -- PMMA window bore (UV-adhesive flush mount)
VM16_D    =  1.7;   // mm -- M1.6 through-hole clearance diameter
VM16_R    =  8.0;   // mm -- M1.6 bolt circle radius (4 holes at 90 deg)
VRECESS_W = 14.0;   // mm -- carrier board pocket width (square)
VRECESS_D =  3.0;   // mm -- carrier board pocket depth (interior face)

// SMA RF bulkhead mount dimensions
//   SMA panel connector: 6.35 mm (1/4") through-hole; 7/16" hex nut (11.1 mm AF).
SMA_BOSS_OD  = 15.0;   // mm -- boss outer diameter
SMA_BOSS_H   =  2.0;   // mm -- boss protrusion above hull surface
SMA_BORE_D   =  6.5;   // mm -- SMA body through-bore clearance
SMA_HEX_AF   = 11.5;   // mm -- SMA hex nut across-flats (7/16" = 11.1 mm + clearance)
SMA_HEX_DEP  =  4.0;   // mm -- hex nut recess depth on interior face

$fn = 64;

// Orientation rotation vectors
//   STL axes: X=forward (+nose), Y=dorsal (+up), Z=port (+left)
//   Rotation derivation uses right-hand Rx/Ry rotation matrices:
//     FWD    (+X): Ry(+90deg)  maps +Z -> +X  --> rotate([  0,  90, 0 ])
//     ZENITH (+Y): Rx(-90deg)  maps +Z -> +Y  --> rotate([ -90,   0, 0 ])
//     NADIR  (-Y): Rx(+90deg)  maps +Z -> -Y  --> rotate([  90,   0, 0 ])
//     PORT   (+Z): no rotation (default cylinder points +Z)
//     STBD   (-Z): Rx(180deg)  maps +Z -> -Z  --> rotate([ 180,   0, 0 ])
FWD_ROT    = [   0,  90, 0 ];   // boss points in +X (toward nose)
ZENITH_ROT = [ -90,   0, 0 ];   // boss points in +Y (dorsal, toward sky)
NADIR_ROT  = [  90,   0, 0 ];   // boss points in -Y (ventral, toward ground)
PORT_ROT   = [   0,   0, 0 ];   // boss points in +Z (toward port/left)
STBD_ROT   = [ 180,   0, 0 ];   // boss points in -Z (toward starboard/right)

// Mount position constants -- 24"-scaled STL world coordinates
//   X_stl = 284 - station_mm; all Y/Z from surface estimates above.
//   All positions VERIFY by measuring rendered mesh cross-sections in slicer.

// Array A lateral sensors -- station 267 mm (X_stl = 17)
S3A_POS = [  17, MID_Y, PORT_Z ];    // VERIFY: port side, sta 267 mm
S4A_POS = [  17, MID_Y, STBD_Z ];    // VERIFY: stbd side, sta 267 mm

// Array B lateral sensors -- station 200 mm (X_stl = 84)
S3B_POS = [  84, MID_Y, PORT_Z ];    // VERIFY: port side, sta 200 mm
S4B_POS = [  84, MID_Y, STBD_Z ];    // VERIFY: stbd side, sta 200 mm

// Array A zenith sensor -- station 240 mm (X_stl = 44)
S5A_POS = [  44, DORSAL_Y, MID_Z ];  // VERIFY: dorsal hull, sta 240 mm

// Array B zenith sensor -- station 347 mm (X_stl = -63)
S5B_POS = [ -63, DORSAL_Y, MID_Z ];  // VERIFY: dorsal hull, sta 347 mm

// Array A nadir sensor -- station 213 mm (X_stl = 71)
S6A_POS = [  71, VENTRAL_Y, MID_Z ]; // VERIFY: ventral hull, sta 213 mm

// Array B nadir sensor -- station 293 mm (X_stl = -9)
S6B_POS = [  -9, VENTRAL_Y, MID_Z ]; // VERIFY: ventral hull, sta 293 mm

// SiK 915 MHz SMA bulkhead -- port side, station 224 mm (X_stl = 60)
//   Antenna: SiK-radio-v2 dipole, 915 MHz; FCC 47 CFR Part 97 / ISM exempt.
SIK_POS  = [  60, MID_Y + 20, PORT_Z ];  // VERIFY: port hull, 20 mm above mid-height

// ZigBee 2.4 GHz SMA bulkhead -- stbd side, station 224 mm (X_stl = 60)
//   Antenna: 2.4 GHz 1/4-wave stub; 802.15.4 ZigBee.
ZBE_POS  = [  60, MID_Y + 20, STBD_Z ];  // VERIFY: stbd hull, 20 mm above mid-height

// WiFi 5 GHz SMA bulkhead -- port side, station 264 mm (X_stl = 20)
//   Antenna: 5 GHz dual-band stub; 802.11ac AP module.
WIFI_POS = [  20, MID_Y + 20, PORT_Z ];  // VERIFY: port hull, 20 mm above mid-height

// ----------------------------------------------------------------------------
// Module: vlsensor_boss
//   Solid boss cylinder for VL53L5CX flush-mount; 4x M1.6 shoulder bosses.
//   Union into outer shell geometry.
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
//   Subtract from union after all bosses added.
// ----------------------------------------------------------------------------
module vlsensor_cut(pos, rot) {
    translate(pos)
    rotate(rot)
    translate([0, 0, -(WALL_T + 1)]) {
        // PMMA window aperture bore
        cylinder(h = WALL_T + VBOSS_H + 2, d = VAPER_D);
        // 4x M1.6 through-holes
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
// Module: sma_boss
//   Cylinder boss for SMA panel-mount bulkhead connector.
// ----------------------------------------------------------------------------
module sma_boss(pos, rot) {
    translate(pos)
    rotate(rot)
    cylinder(h = SMA_BOSS_H, d = SMA_BOSS_OD);
}

// ----------------------------------------------------------------------------
// Module: sma_cut
//   SMA through-bore + hex nut recess on interior face.
//   The hex recess receives the SMA locking nut from inside the hull.
// ----------------------------------------------------------------------------
module sma_cut(pos, rot) {
    translate(pos)
    rotate(rot) {
        // Through-bore from interior through boss
        translate([0, 0, -(WALL_T + 1)])
        cylinder(h = WALL_T + SMA_BOSS_H + 2, d = SMA_BORE_D);
        // Hex nut recess on interior face (first SMA_HEX_DEP mm from inside)
        translate([0, 0, -(WALL_T + 1)])
        cylinder(h = SMA_HEX_DEP + 1, d = SMA_HEX_AF, $fn = 6);
    }
}

// ============================================================
// Main geometry
// ============================================================
difference() {
    union() {
        // Canonical 24" mid-fuselage shell (outer minus inner void)
        difference() {
            scale([SCALE_24, SCALE_24, SCALE_24])
                import("../../thingverse-serenity/files/s_middle.stl");

            translate([CX, CY, CZ])
            scale([INNER_SX, INNER_SY, INNER_SZ])
            translate([-CX, -CY, -CZ])
            scale([SCALE_24, SCALE_24, SCALE_24])
                import("../../thingverse-serenity/files/s_middle.stl");
        }

        // Sensor bosses (additive)
        vlsensor_boss(S3A_POS,  PORT_ROT);
        vlsensor_boss(S4A_POS,  STBD_ROT);
        vlsensor_boss(S3B_POS,  PORT_ROT);
        vlsensor_boss(S4B_POS,  STBD_ROT);
        vlsensor_boss(S5A_POS,  ZENITH_ROT);
        vlsensor_boss(S5B_POS,  ZENITH_ROT);
        vlsensor_boss(S6A_POS,  NADIR_ROT);
        vlsensor_boss(S6B_POS,  NADIR_ROT);

        // RF antenna SMA bosses (additive)
        sma_boss(SIK_POS,  PORT_ROT);
        sma_boss(ZBE_POS,  STBD_ROT);
        sma_boss(WIFI_POS, PORT_ROT);
    }

    // Sensor apertures and through-holes (subtractive)
    vlsensor_cut(S3A_POS,  PORT_ROT);
    vlsensor_cut(S4A_POS,  STBD_ROT);
    vlsensor_cut(S3B_POS,  PORT_ROT);
    vlsensor_cut(S4B_POS,  STBD_ROT);
    vlsensor_cut(S5A_POS,  ZENITH_ROT);
    vlsensor_cut(S5B_POS,  ZENITH_ROT);
    vlsensor_cut(S6A_POS,  NADIR_ROT);
    vlsensor_cut(S6B_POS,  NADIR_ROT);

    // RF antenna bore and nut recesses (subtractive)
    sma_cut(SIK_POS,  PORT_ROT);
    sma_cut(ZBE_POS,  STBD_ROT);
    sma_cut(WIFI_POS, PORT_ROT);
}
