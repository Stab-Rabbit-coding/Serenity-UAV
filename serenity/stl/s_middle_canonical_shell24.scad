// ============================================================
// s_middle_canonical_shell24.scad
// Mid-fuselage shell for Serenity Rev N 24" hull (s_middle.stl).
// Belly restored to standard Serenity geometry -- NO belly scoop.
// Replaces s_middle_intake_shell24.stl for the 4-radial-intake Rev N build.
//
// Mounts:
//   S3A  -- VL53L5CX port-side ToF,  Array A (FC3), sta 267 mm
//   S4A  -- VL53L5CX stbd-side ToF,  Array A (FC3), sta 267 mm
//   S3B  -- VL53L5CX port-side ToF,  Array B (FC2), sta 200 mm
//   S4B  -- VL53L5CX stbd-side ToF,  Array B (FC2), sta 200 mm
//   S5A  -- VL53L5CX zenith ToF,     Array A (FC3), sta 240 mm
//   S5B  -- VL53L5CX zenith ToF,     Array B (FC2), sta 347 mm
//   S6A  -- VL53L5CX nadir ToF,      Array A (FC3), sta 213 mm
//   S6B  -- VL53L5CX nadir ToF,      Array B (FC2), sta 293 mm
//   GPS  -- 25x25 mm GPS patch antenna, dorsal centreline, sta 209 mm
//   ANT  -- 49 MHz RCRS whip post boss (1.5 mm protrusion), dorsal, sta 234 mm
//   SiK  -- SMA bulkhead, 915 MHz SiK telemetry,  port side,  sta 224 mm
//   ZBE  -- SMA bulkhead, 2.4 GHz ZigBee,         stbd side,  sta 224 mm
//   WIFI -- SMA bulkhead, 5 GHz WiFi,              port side,  sta 264 mm
//
// Flush-mount design philosophy:
//   All VL53L5CX apertures are cut flush with no external protrusion.
//   PMMA window discs sit in a 0.5 mm x 14 mm OD registration ring recess
//   on the exterior face, retained by UV adhesive and 4x M1.6 countersunk
//   flathead screws (DIN 7991).  Carrier board pockets are on the interior.
//   SMA connectors sit flush; hex nut recess is on the interior only.
//   GPS patch is recessed 2 mm into the dorsal hull surface (flush with OML);
//   a separate printed PETG dome cover protects it from weather.
//   The 49 MHz post boss is the only external protrusion -- 1.5 mm minimum
//   to register the antenna base above the hull waterline.
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
//
// Scale factor 24" hull: SCALE_24 = 2.9294
// Centroid of s_middle.stl at 24" scale:
//   CX = 135.712 x (2.9294/2.1974) = 180.95 mm
//   CY = -50.459 x (2.9294/2.1974) = -67.28 mm
//   CZ =  27.348 x (2.9294/2.1974) =  36.47 mm
// Inner scale factors (from 18" scad -- same 2.5 mm absolute wall):
//   INNER_SX = 0.962373
//   INNER_SY = 0.959565
//   INNER_SZ = 0.908966
//
// Coordinate system (24"-scaled STL world space):
//   X -- longitudinal, positive toward nose
//   Y -- vertical,    positive toward dorsal (up)   NOTE: Y is up, not Z
//   Z -- lateral,     positive toward port  (left)
//
// Hull surface estimates (wall = 2.5 mm):
//   half_ext_Y = 2.5 / (1 - 0.959565) = 61.8 mm
//     Dorsal surface:  CY + 62 = approx -5 mm
//     Ventral surface: CY - 62 = approx -129 mm
//   half_ext_Z = 2.5 / (1 - 0.908966) = 27.5 mm
//     Port surface:    CZ + 28 = approx 64 mm
//     Stbd surface:    CZ - 28 = approx  9 mm
//
// All mount positions are estimates. VERIFY by measuring rendered mesh in slicer.
//
// Sensor wiring (dual-redundant failover):
//   Array A (FC3 SBC primary): S3A, S4A, S5A, S6A on I2C-3 bus, mux 0x70.
//   Array B (FC2 SBC primary): S3B, S4B, S5B, S6B on I2C-2 bus, mux 0x71.
//   Ref: ST UM2884 DocID032910 Rev 1, 2021.
//
// Antenna references:
//   SiK 915 MHz: FCC 47 CFR Part 97 / ISM.
//   ZigBee 2.4 GHz: IEEE 802.15.4; FCC Part 15.
//   WiFi 5 GHz: IEEE 802.11ac; FCC Part 15.
//   49 MHz RCRS: FCC 47 CFR Part 95 Subpart H.
// ============================================================

SCALE_24  = 2.9294;   // 24" hull scale factor

// Mid-fuselage centroid in 24"-scaled STL world coordinates
CX =  180.95;   // mm
CY =  -67.28;   // mm -- dorsal/ventral axis (positive = up)
CZ =   36.47;   // mm -- lateral axis (positive = port)

// Inner-shell scale factors (2.5 mm absolute wall)
INNER_SX = 0.962373;
INNER_SY = 0.959565;
INNER_SZ = 0.908966;

// Conservative wall thickness for cutter overlap
WALL_T = 4.0;   // mm

// Derived hull surface coordinates (VERIFY after rendering)
DORSAL_Y  = CY + 62;    // approx -5 mm
VENTRAL_Y = CY - 62;    // approx -129 mm
PORT_Z    = CZ + 28;    // approx 64 mm
STBD_Z    = CZ - 28;    // approx 9 mm
MID_Y     = CY;         // approx -67 mm (hull cross-section mid-height)
MID_Z     = CZ;         // approx 36 mm (hull Z centreline)

// VL53L5CX flush mount dimensions
//   Exterior: 11 mm PMMA bore + 0.5 mm x 14 mm OD seat ring + 4x M1.6 c/s.
//   Interior: 14x14x3 mm carrier-board recess.
//   Ref: ST UM2884 DocID032910 Rev 1, 2021.
VAPER_D   = 11.0;   // mm -- PMMA window aperture bore
VRING_OD  = 14.0;   // mm -- seat ring OD (hull-flush registration)
VRING_DEP =  0.5;   // mm -- seat ring recess depth
VM16_D    =  1.7;   // mm -- M1.6 clearance hole
VM16_R    =  7.0;   // mm -- M1.6 bolt circle radius
VCSK16_OD =  3.5;   // mm -- M1.6 flathead c/s OD (DIN 7991, 90 deg)
VCSK16_D  =  1.0;   // mm -- M1.6 c/s depth
VRECESS_W = 14.0;   // mm -- carrier board pocket (square)
VRECESS_D =  3.0;   // mm -- carrier board pocket depth

// SMA RF bulkhead dimensions (flush exterior, interior hex nut recess only)
//   SMA panel mount: 6.35 mm through-hole; 7/16" hex nut (11.1 mm AF).
SMA_BORE_D  =  6.5;    // mm -- SMA body clearance bore
SMA_HEX_AF  = 11.5;    // mm -- SMA hex nut across-flats (7/16" + clearance)
SMA_HEX_DEP =  4.0;    // mm -- interior hex nut recess depth

// GPS patch antenna flush recess dimensions (25x25 mm ceramic patch)
//   Patch sits 2 mm below hull surface; separate PETG dome cover snaps on.
//   Ref: u-blox UBX-15015498-R8 (NEO-M9N integration manual), Fig 3-3.
GPS_PATCH_W  = 26.0;   // mm -- patch pocket width (25 mm + 0.5 mm per side)
GPS_RECESS_D =  2.0;   // mm -- patch recess depth (patch element flush with OML)
GPS_COAX_D   =  5.0;   // mm -- coax feed-through bore (centre)
GPS_M2_D     =  2.2;   // mm -- M2 dome-cover mount hole clearance
GPS_M2_S     = 24.0;   // mm -- M2 bolt spacing (4 corners)
GPS_CSK2_OD  =  4.5;   // mm -- M2 flathead c/s OD (DIN 7991, 90 deg)
GPS_CSK2_D   =  1.2;   // mm -- M2 c/s depth

// 49 MHz RCRS antenna post boss
//   Minimum 1.5 mm protrusion to register antenna base above hull waterline.
//   M4 threaded insert (pressed from interior) retains antenna base flange.
ANT49_BOSS_OD    = 12.0;   // mm -- post boss OD (reduced to minimum functional)
ANT49_BOSS_H     =  1.5;   // mm -- boss protrusion above hull surface
ANT49_BORE_D     =  4.3;   // mm -- M4 insert bore clearance
ANT49_FLANGE_D   = 10.0;   // mm -- antenna base flange recess OD (on boss top)
ANT49_FLANGE_DEP =  1.0;   // mm -- flange recess depth

$fn = 64;

// Orientation rotation vectors
//   STL axes: X=forward, Y=dorsal (+up), Z=port (+left).
//   Ry(+90):  +Z -> +X  (forward)   rotate([  0,  90, 0 ])
//   Rx(-90):  +Z -> +Y  (zenith)    rotate([ -90,  0, 0 ])
//   Rx(+90):  +Z -> -Y  (nadir)     rotate([  90,  0, 0 ])
//   no rot:   +Z -> +Z  (port)      rotate([   0,  0, 0 ])
//   Rx(180):  +Z -> -Z  (stbd)      rotate([ 180,  0, 0 ])
ZENITH_ROT = [ -90,   0, 0 ];
NADIR_ROT  = [  90,   0, 0 ];
PORT_ROT   = [   0,   0, 0 ];
STBD_ROT   = [ 180,   0, 0 ];

// Mount position constants -- 24"-scaled STL world coordinates
//   X_stl = 284 - station_mm.  All positions VERIFY in slicer.

// Array A lateral sensors (FC3 primary) -- station 267 mm (X_stl = 17)
S3A_POS = [  17, MID_Y, PORT_Z ];    // VERIFY: port hull, sta 267 mm
S4A_POS = [  17, MID_Y, STBD_Z ];    // VERIFY: stbd hull, sta 267 mm

// Array B lateral sensors (FC2 primary) -- station 200 mm (X_stl = 84)
S3B_POS = [  84, MID_Y, PORT_Z ];    // VERIFY: port hull, sta 200 mm
S4B_POS = [  84, MID_Y, STBD_Z ];    // VERIFY: stbd hull, sta 200 mm

// Array A zenith sensor (FC3) -- station 240 mm (X_stl = 44)
S5A_POS = [  44, DORSAL_Y, MID_Z ];  // VERIFY: dorsal hull, sta 240 mm

// Array B zenith sensor (FC2) -- station 347 mm (X_stl = -63)
S5B_POS = [ -63, DORSAL_Y, MID_Z ];  // VERIFY: dorsal hull, sta 347 mm

// Array A nadir sensor (FC3) -- station 213 mm (X_stl = 71)
S6A_POS = [  71, VENTRAL_Y, MID_Z ]; // VERIFY: ventral hull, sta 213 mm

// Array B nadir sensor (FC2) -- station 293 mm (X_stl = -9)
S6B_POS = [  -9, VENTRAL_Y, MID_Z ]; // VERIFY: ventral hull, sta 293 mm

// GPS patch -- dorsal centreline, station 209 mm (X_stl = 75)
//   Broad, flat dorsal surface provides optimal GPS ground plane and sky view.
GPS_POS  = [  75, DORSAL_Y, MID_Z ]; // VERIFY: dorsal centreline, sta 209 mm

// 49 MHz RCRS post -- dorsal centreline, station 234 mm (X_stl = 50), aft of GPS
ANT49_POS = [ 50, DORSAL_Y, MID_Z ]; // VERIFY: dorsal centreline, sta 234 mm

// SiK 915 MHz SMA -- port side, station 224 mm (X_stl = 60)
SIK_POS  = [  60, MID_Y + 20, PORT_Z ];  // VERIFY: port hull, 20 mm above mid

// ZigBee 2.4 GHz SMA -- stbd side, station 224 mm (X_stl = 60)
ZBE_POS  = [  60, MID_Y + 20, STBD_Z ];  // VERIFY: stbd hull, 20 mm above mid

// WiFi 5 GHz SMA -- port side, station 264 mm (X_stl = 20)
WIFI_POS = [  20, MID_Y + 20, PORT_Z ];  // VERIFY: port hull, 20 mm above mid

// ----------------------------------------------------------------------------
// Module: vlsensor_cut
//   Flush-mount cutter for VL53L5CX.  Zero protrusion above hull surface.
//   Aperture bore + 0.5 mm PMMA seat ring + 4x M1.6 c/s holes + board pocket.
// ----------------------------------------------------------------------------
module vlsensor_cut(pos, rot) {
    translate(pos)
    rotate(rot)
    translate([0, 0, -(WALL_T + 1)]) {
        // PMMA aperture bore
        cylinder(h = WALL_T + 2, d = VAPER_D);

        // PMMA disc seat ring (0.5 mm recess, 14 mm OD) at exterior face
        translate([0, 0, WALL_T + 1 - VRING_DEP])
        cylinder(h = VRING_DEP + 1, d = VRING_OD);

        // 4x M1.6 countersunk through-holes at 45 deg diagonal
        for (a = [45, 135, 225, 315])
            rotate([0, 0, a])
            translate([VM16_R, 0, 0]) {
                cylinder(h = WALL_T + 2, d = VM16_D);
                translate([0, 0, WALL_T + 1 - VCSK16_D])
                cylinder(h = VCSK16_D + 1, d1 = VM16_D, d2 = VCSK16_OD);
            }

        // Carrier board recess on interior face
        translate([-VRECESS_W / 2, -VRECESS_W / 2, 0])
        cube([VRECESS_W, VRECESS_W, VRECESS_D + 1]);
    }
}

// ----------------------------------------------------------------------------
// Module: sma_cut
//   Flush SMA bulkhead bore + interior hex-nut recess.  No exterior protrusion.
// ----------------------------------------------------------------------------
module sma_cut(pos, rot) {
    translate(pos)
    rotate(rot)
    translate([0, 0, -(WALL_T + 1)]) {
        // SMA body clearance bore (full wall)
        cylinder(h = WALL_T + 2, d = SMA_BORE_D);
        // Interior hex-nut recess (6-sided, first SMA_HEX_DEP mm from inside)
        cylinder(h = SMA_HEX_DEP + 1, d = SMA_HEX_AF, $fn = 6);
    }
}

// ----------------------------------------------------------------------------
// Module: gps_cut
//   Flush GPS patch recess + coax bore + 4x M2 dome-cover c/s holes.
//   Patch sits 2 mm below hull OML; dome cover (separate part) clips on.
// ----------------------------------------------------------------------------
module gps_cut(pos, rot) {
    translate(pos)
    rotate(rot)
    translate([0, 0, -(WALL_T + 1)]) {
        // Patch element pocket (square recess, 2 mm deep at exterior face)
        translate([-GPS_PATCH_W / 2, -GPS_PATCH_W / 2, WALL_T + 1 - GPS_RECESS_D])
        cube([GPS_PATCH_W, GPS_PATCH_W, GPS_RECESS_D + 1]);

        // Coax feed-through bore at patch centre (full wall depth)
        cylinder(h = WALL_T + 2, d = GPS_COAX_D);

        // 4x M2 dome-cover retention holes (countersunk, 4 corners)
        for (dx = [-GPS_M2_S / 2, GPS_M2_S / 2])
        for (dy = [-GPS_M2_S / 2, GPS_M2_S / 2])
            translate([dx, dy, 0]) {
                cylinder(h = WALL_T + 2, d = GPS_M2_D);
                translate([0, 0, WALL_T + 1 - GPS_CSK2_D])
                cylinder(h = GPS_CSK2_D + 1, d1 = GPS_M2_D, d2 = GPS_CSK2_OD);
            }
    }
}

// ----------------------------------------------------------------------------
// Module: ant49_boss
//   Minimal 1.5 mm post boss for 49 MHz RCRS antenna base registration.
//   This is the only external protrusion; required to keep the antenna base
//   above the hull waterline.
// ----------------------------------------------------------------------------
module ant49_boss(pos, rot) {
    translate(pos)
    rotate(rot)
    cylinder(h = ANT49_BOSS_H, d = ANT49_BOSS_OD);
}

// ----------------------------------------------------------------------------
// Module: ant49_cut
//   M4 insert bore through hull + boss + flange recess on boss top.
// ----------------------------------------------------------------------------
module ant49_cut(pos, rot) {
    translate(pos)
    rotate(rot) {
        // M4 bore through hull and boss
        translate([0, 0, -(WALL_T + 1)])
        cylinder(h = WALL_T + ANT49_BOSS_H + 2, d = ANT49_BORE_D);
        // Antenna base flange recess on top of boss
        translate([0, 0, ANT49_BOSS_H - ANT49_FLANGE_DEP])
        cylinder(h = ANT49_FLANGE_DEP + 1, d = ANT49_FLANGE_D);
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

        // 49 MHz antenna post boss -- only external protrusion on this section
        ant49_boss(ANT49_POS, ZENITH_ROT);
    }

    // VL53L5CX flush apertures (8 sensors, 6 directions)
    vlsensor_cut(S3A_POS,  PORT_ROT);
    vlsensor_cut(S4A_POS,  STBD_ROT);
    vlsensor_cut(S3B_POS,  PORT_ROT);
    vlsensor_cut(S4B_POS,  STBD_ROT);
    vlsensor_cut(S5A_POS,  ZENITH_ROT);
    vlsensor_cut(S5B_POS,  ZENITH_ROT);
    vlsensor_cut(S6A_POS,  NADIR_ROT);
    vlsensor_cut(S6B_POS,  NADIR_ROT);

    // GPS patch recess and dome-cover holes
    gps_cut(GPS_POS, ZENITH_ROT);

    // 49 MHz post bore and flange recess
    ant49_cut(ANT49_POS, ZENITH_ROT);

    // SMA RF bulkhead bores (flush exterior, interior hex recess)
    sma_cut(SIK_POS,  PORT_ROT);
    sma_cut(ZBE_POS,  STBD_ROT);
    sma_cut(WIFI_POS, PORT_ROT);
}
