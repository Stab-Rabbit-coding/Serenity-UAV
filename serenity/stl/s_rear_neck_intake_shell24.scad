// s_rear_neck_intake_shell24.scad
// Rear fuselage shell (Panel D/E/F) for Serenity Rev N 24" hull
// with 4 radial scoop windows cut through the hull wall at the neck station.
//
// Scoop locations: 90° spacing (dorsal, port, ventral, starboard).
// Neck station in s_rear STL space (24"-scaled coordinates):
//   The rear section spans from the cargo-bay aft bulkhead forward.
//   Longitudinal axis of the original STL = X-axis (positive toward nose).
//   Neck centre station ≈ −129mm in scaled STL X-space (station ~310mm from nose).
//
// Hull ellipse at neck (24"): half-width ≈ 63mm, half-height ≈ 50mm.
// Each scoop window: 65mm wide (circumferential) × 60mm tall (radial).
//
// Shell derivation follows same pattern as s_rear_shell18.scad (18" reference):
//   centroid at 18": (−131.8437, −81.8939, 51.4144)
//   centroid at 24": multiply by (2.9294/2.1974) = 1.33333
//     CX = −131.8437 × 1.33333 = −175.79 mm
//     CY =  −81.8939 × 1.33333 = −109.19 mm
//     CZ =   51.4144 × 1.33333 =   68.55 mm
//   Inner scale factors (from 18" scad — same absolute wall 2.5mm):
//     INNER_SX = 0.952708
//     INNER_SY = 0.957812
//     INNER_SZ = 0.963308
//
// IMPORTANT: After generating this shell, verify scoop window positions by
// measuring the exported mesh in a slicer at the neck cross-section.
// The NECK_X offset below is an estimate from hull profile data; adjust
// NECK_X if the windows do not centre on the correct hull station.

SCALE_24 = 2.9294;

// Centroid of s_rear.stl in 24"-scaled coordinate space
CX = -175.79;
CY = -109.19;
CZ =   68.55;

// Inner-shell scale factors (preserve 2.5mm absolute wall thickness)
INNER_SX = 0.952708;
INNER_SY = 0.957812;
INNER_SZ = 0.963308;

// ── Scoop window geometry ────────────────────────────────────────────────────
// X-position of neck station centre within s_rear STL 24"-scaled space.
// The rear STL's nose-end face is approximately at X = −44mm (unscaled).
// At 24" scale that face is at X ≈ −44 × SCALE_24 = −129mm.
// The neck centre station (310mm from nose) in the rear piece = the aft
// face of the cargo bay, which maps to approximately X = −129mm.
NECK_X   = -129;    // [mm] adjust after measuring mesh if needed

HULL_W2  =   63;    // port/stbd half-width at neck station [mm]
HULL_H2  =   50;    // dorsal/ventral half-height at neck   [mm]
SCOOP_W  =   65;    // circumferential width of each window [mm]
SCOOP_H  =   60;    // radial height of each window         [mm]
SCOOP_D  =   20;    // cutter depth (through hull + extra)  [mm]
SCOOP_AX =   38;    // axial extent of window               [mm]

$fn = 64;

// One scoop cutter at +Y (dorsal) before rotation
module scoop_cutter() {
    translate([NECK_X, HULL_H2 - 1, 0])
    rotate([90, 0, 0])
    linear_extrude(height = SCOOP_D + 1)
    square([SCOOP_W, SCOOP_AX], center = true);
}

difference() {
    // ── Canonical shell ───────────────────────────────────────────────────
    difference() {
        scale([SCALE_24, SCALE_24, SCALE_24])
            import("../../thingverse-serenity/files/s_rear.stl");

        translate([CX, CY, CZ])
        scale([INNER_SX, INNER_SY, INNER_SZ])
        translate([-CX, -CY, -CZ])
        scale([SCALE_24, SCALE_24, SCALE_24])
            import("../../thingverse-serenity/files/s_rear.stl");
    }

    // ── Four scoop windows at 90° spacing ────────────────────────────────
    // Rotation axis = X (longitudinal); 0° = dorsal (+Y), 90° = port (+Z rotated)
    // Note: in the STL's native orientation Z is up, Y is starboard.
    // Windows are cut around the Y/Z plane (cross-section normal to X axis).
    for (rot = [0, 90, 180, 270])
        rotate([rot, 0, 0])
        scoop_cutter();
}
