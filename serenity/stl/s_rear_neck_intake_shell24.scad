// ============================================================
// s_rear_neck_intake_shell24.scad
// Rear fuselage shell for Serenity Rev N 24" hull (s_rear.stl).
// Includes 4 radial neck scoop windows AND dual aft-facing ToF sensor mounts.
//
// Mounts (flush with outer mold line -- zero external protrusion):
//   S2A -- VL53L5CX aft ToF sensor, Array A (FC3 primary)
//   S2B -- VL53L5CX aft ToF sensor, Array B (FC2 primary)
//
// Flush-mount design:
//   Sensor apertures are cut flush through the hull wall.  PMMA window discs
//   sit in a 0.5 mm x 14 mm OD registration ring recess on the exterior face,
//   retained by UV adhesive and 4x M1.6 countersunk flathead screws (DIN 7991).
//   Carrier board pocket (14x14x3 mm) is on the interior face.
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
//
// Scoop locations: 90 deg spacing (dorsal, port, ventral, starboard).
// Neck station: approx X = -129 mm in 24"-scaled STL space (sta 413 mm from nose).
// Hull ellipse at neck (24"): half-width approx 63 mm, half-height approx 50 mm.
// Each scoop window: 65 mm wide x 38 mm axial x 21 mm deep.
//
// Shell derivation:
//   18" centroid: (-131.8437, -81.8939, 51.4144)
//   24" centroid = x 1.33333:
//     CX = -175.79 mm
//     CY = -109.19 mm
//     CZ =   68.55 mm
//   Inner scale factors (2.5 mm absolute wall):
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
//   Rear section estimated span: neck (X = -129) to stern (X approx -265 mm).
//   Stern estimated from ship-length/wingspan ratio approx 0.9 at 24" span (610 mm).
//   Sensors offset from engine bell centreline (approx Y = CY, Z = CZ) to give
//   unobstructed aft FoV and to serve as distinct Array A / Array B viewpoints.
//   VERIFY all positions by measuring rendered mesh in slicer.
//
// IMPORTANT: Verify scoop and sensor positions by measuring mesh cross-sections
// in a slicer after rendering before printing.
// ============================================================

SCALE_24  = 2.9294;   // 24" hull scale factor

// Rear shell centroid in 24"-scaled STL world coordinates
CX = -175.79;   // mm
CY = -109.19;   // mm -- dorsal/ventral axis (positive = up)
CZ =   68.55;   // mm -- lateral axis (positive = port)

// Inner-shell scale factors (2.5 mm absolute wall)
INNER_SX = 0.952708;
INNER_SY = 0.957812;
INNER_SZ = 0.963308;

// Conservative wall thickness for cutter overlap
WALL_T = 4.0;   // mm

// Neck scoop geometry
NECK_X   = -129;    // mm -- neck station; VERIFY after rendering
HULL_W2  =   63;    // mm -- port/stbd half-width at neck
HULL_H2  =   50;    // mm -- dorsal/ventral half-height at neck
SCOOP_W  =   65;    // mm -- circumferential width of each window
SCOOP_D  =   20;    // mm -- cutter depth (through hull + margin)
SCOOP_AX =   38;    // mm -- axial extent of window

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

$fn = 64;

// Orientation rotation vectors
//   STL axes: X=forward, Y=dorsal (+up), Z=port (+left).
//   Ry(-90 deg) maps +Z -> -X (aft): rotate([ 0, -90, 0 ])
AFT_ROT = [ 0, -90, 0 ];   // aperture faces -X (toward stern)

// Aft sensor positions -- near stern face, offset from engine bell centreline
//   Engine bell on hull axis at approx (CY, CZ); offset to give clear aft FoV.
//   VERIFY both positions by measuring stern face geometry in slicer.

// Array A aft sensor (FC3 primary) -- upper-port quadrant of stern face
S2A_POS = [ -222, CY + 25, CZ + 15 ];   // VERIFY

// Array B aft sensor (FC2 primary) -- lower-stbd quadrant, distinct bearing from S2A
S2B_POS = [ -215, CY - 20, CZ - 12 ];   // VERIFY

// ----------------------------------------------------------------------------
// Module: scoop_cutter
//   One rectangular neck scoop window before rotation.
//   Four instances at 0/90/180/270 deg around X give full radial coverage.
// ----------------------------------------------------------------------------
module scoop_cutter() {
    translate([NECK_X, HULL_H2 - 1, 0])
    rotate([90, 0, 0])
    linear_extrude(height = SCOOP_D + 1)
    square([SCOOP_W, SCOOP_AX], center = true);
}

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

        // PMMA disc seat ring (0.5 mm recess at exterior face, 14 mm OD)
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

// ============================================================
// Main geometry
// ============================================================
difference() {
    // Canonical 24" rear shell -- no additive bosses; all mounts are flush cuts
    difference() {
        scale([SCALE_24, SCALE_24, SCALE_24])
            import("../../thingverse-serenity/files/s_rear.stl");

        translate([CX, CY, CZ])
        scale([INNER_SX, INNER_SY, INNER_SZ])
        translate([-CX, -CY, -CZ])
        scale([SCALE_24, SCALE_24, SCALE_24])
            import("../../thingverse-serenity/files/s_rear.stl");
    }

    // Four radial neck scoop windows
    //   Rotation axis = X; 0 deg = dorsal (+Y), 90 deg = port (+Z).
    for (rot = [0, 90, 180, 270])
        rotate([rot, 0, 0])
        scoop_cutter();

    // Aft sensor flush apertures
    vlsensor_cut(S2A_POS, AFT_ROT);
    vlsensor_cut(S2B_POS, AFT_ROT);
}
