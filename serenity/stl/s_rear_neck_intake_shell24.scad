// ============================================================
// s_rear_neck_intake_shell24.scad
// Rear fuselage shell (Panel D/E/F) for Serenity Rev N 24" hull.
// Includes 4 radial scoop windows at the neck station AND
// dual aft-facing ToF collision-avoidance sensor mounts.
//
// Mounts:
//   S2A -- VL53L5CX aft ToF sensor, Array A (FC3 primary), sta ~504 mm
//   S2B -- VL53L5CX aft ToF sensor, Array B (FC2 primary), sta ~514 mm
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
//
// Scoop locations: 90 deg spacing (dorsal, port, ventral, starboard).
// Neck station in s_rear STL space (24"-scaled coordinates):
//   Longitudinal axis = X (positive toward nose).
//   Neck centre station approx -129 mm in scaled STL X-space (sta 413 mm from nose).
//
// Hull ellipse at neck (24"): half-width approx 63 mm, half-height approx 50 mm.
// Each scoop window: 65 mm wide (circumferential) x 60 mm tall (radial).
//
// Shell derivation (same pattern as s_rear_shell18.scad reference):
//   centroid at 18": (-131.8437, -81.8939, 51.4144)
//   centroid at 24": multiply by (2.9294/2.1974) = 1.33333
//     CX = -131.8437 x 1.33333 = -175.79 mm
//     CY =  -81.8939 x 1.33333 = -109.19 mm
//     CZ =   51.4144 x 1.33333 =   68.55 mm
//   Inner scale factors (from 18" scad -- same absolute wall 2.5 mm):
//     INNER_SX = 0.952708
//     INNER_SY = 0.957812
//     INNER_SZ = 0.963308
//
// Coordinate system (24"-scaled STL world space):
//   X -- longitudinal, positive toward nose
//   Y -- vertical,    positive toward dorsal (up)   NOTE: Y is up, not Z
//   Z -- lateral,     positive toward port  (left)
//
// Aft sensor position notes:
//   The rear section spans approximately from neck (X=-129) to stern (X approx -260 mm).
//   Stern position estimated from ship-length-to-wingspan ratio (approx 0.9);
//   with 24" wingspan (610 mm), ship length approx 550 mm, stern at X = 284-550 = -266 mm.
//   Aft sensors are positioned near the stern face with Y/Z offsets to avoid
//   the engine bell bore which is on the hull longitudinal centreline (Y=CY, Z=CZ).
//   VERIFY all positions by measuring rendered mesh cross-sections before printing.
//
// Sensor references:
//   VL53L5CX: ST UM2884 user manual, DocID032910 Rev 1, 2021.
//     FoV 65 deg diagonal; 0.4-4.0 m; 8x8 zone; 6.4x3.4 mm package.
//
// IMPORTANT: After generating this shell, verify all scoop and sensor positions
// by measuring the exported mesh in a slicer at the relevant cross-sections.
// ============================================================

SCALE_24  = 2.9294;   // 24" hull scale factor

// Rear shell centroid in 24"-scaled STL world coordinates
CX = -175.79;   // mm -- longitudinal
CY = -109.19;   // mm -- dorsal/ventral (positive = up)
CZ =   68.55;   // mm -- lateral (positive = port)

// Inner-shell scale factors (preserve 2.5 mm absolute wall thickness)
INNER_SX = 0.952708;
INNER_SY = 0.957812;
INNER_SZ = 0.963308;

// Nominal wall thickness for aperture depth calculations
WALL_T = 4.0;   // mm (2.5 mm nominal + tolerance)

// Scoop window geometry at neck station
NECK_X   = -129;    // [mm] VERIFY after measuring mesh; neck at sta 413 mm from nose
HULL_W2  =   63;    // port/stbd half-width at neck station [mm]
HULL_H2  =   50;    // dorsal/ventral half-height at neck   [mm]
SCOOP_W  =   65;    // circumferential width of each window [mm]
SCOOP_H  =   60;    // radial height of each window         [mm]
SCOOP_D  =   20;    // cutter depth (through hull + extra)  [mm]
SCOOP_AX =   38;    // axial extent of window               [mm]

// VL53L5CX ToF sensor mount dimensions
//   Ref: ST UM2884 DocID032910 Rev 1, 2021 -- carrier board approx 13x13 mm
VBOSS_OD  = 16.0;   // mm -- boss outer diameter
VBOSS_H   =  3.0;   // mm -- boss protrusion above hull outer surface
VAPER_D   = 11.0;   // mm -- PMMA window bore (UV-adhesive flush mount)
VM16_D    =  1.7;   // mm -- M1.6 through-hole clearance diameter
VM16_R    =  8.0;   // mm -- M1.6 bolt circle radius (4 holes at 90 deg)
VRECESS_W = 14.0;   // mm -- carrier board pocket width (square)
VRECESS_D =  3.0;   // mm -- carrier board pocket depth (interior face)

$fn = 64;

// Orientation rotation vectors
//   STL axes: X=forward (+nose), Y=dorsal (+up), Z=port (+left)
//   AFT (-X): Ry(-90deg) maps +Z -> -X --> rotate([ 0, -90, 0 ])
AFT_ROT = [ 0, -90, 0 ];   // boss points in -X (toward stern / aft)

// Aft sensor mount positions -- 24"-scaled STL world coordinates
//   Placed near stern face to maximise aft FoV, offset from engine bell centreline.
//   Engine bell on hull axis at approx (Y=CY, Z=CZ); sensors offset to avoid bore.
//   X_stl = 284 - station_mm_24in; stern estimated at X approx -260 mm.
//   VERIFY all positions by rendering and measuring mesh before printing.

// Array A aft sensor -- upper-port quadrant of stern face (FC3 primary)
S2A_POS = [ -222, CY + 25, CZ + 15 ];   // VERIFY: X, Y, Z relative to stern hull face

// Array B aft sensor -- lower-stbd quadrant of stern face (FC2 primary)
//   Offset from S2A to achieve distinct viewing angles for Array B failover.
S2B_POS = [ -215, CY - 20, CZ - 12 ];   // VERIFY: X, Y, Z relative to stern hull face

// ----------------------------------------------------------------------------
// Module: scoop_cutter
//   One rectangular scoop window cutter at +Y (dorsal) before rotation.
//   Four instances rotated around X at 90 deg spacing cover all four quadrants.
//   Cutter geometry: 65 mm wide x 38 mm axial x 21 mm deep (through 2.5 mm wall).
// ----------------------------------------------------------------------------
module scoop_cutter() {
    translate([NECK_X, HULL_H2 - 1, 0])
    rotate([90, 0, 0])
    linear_extrude(height = SCOOP_D + 1)
    square([SCOOP_W, SCOOP_AX], center = true);
}

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

// ============================================================
// Main geometry
// ============================================================
difference() {
    union() {
        // Canonical 24" rear shell (outer minus inner void)
        difference() {
            scale([SCALE_24, SCALE_24, SCALE_24])
                import("../../thingverse-serenity/files/s_rear.stl");

            translate([CX, CY, CZ])
            scale([INNER_SX, INNER_SY, INNER_SZ])
            translate([-CX, -CY, -CZ])
            scale([SCALE_24, SCALE_24, SCALE_24])
                import("../../thingverse-serenity/files/s_rear.stl");
        }

        // Aft sensor bosses (additive; boss protrudes in -X / aft direction)
        vlsensor_boss(S2A_POS, AFT_ROT);
        vlsensor_boss(S2B_POS, AFT_ROT);
    }

    // Four radial neck scoop windows at 90 deg spacing
    //   Rotation axis = X (longitudinal); 0 deg = dorsal (+Y).
    //   In the STL's native orientation Y is dorsal (up) and Z is port (left).
    for (rot = [0, 90, 180, 270])
        rotate([rot, 0, 0])
        scoop_cutter();

    // Aft sensor apertures and through-holes
    vlsensor_cut(S2A_POS, AFT_ROT);
    vlsensor_cut(S2B_POS, AFT_ROT);
}
