// s_middle_canonical_shell24.scad
// Canonical middle fuselage shell for Serenity Rev N 24" hull
// Belly restored to standard Serenity geometry — NO belly scoop opening.
// Replaces s_middle_intake_shell24.stl for the 4-radial-intake Rev N build.
//
// Shell generation pattern from thingverse-serenity/files-hollowed-18in/:
//   Shell = outer STL − (scale-inner × shifted-inner STL)
//   Inner scale factors derived from 2.5mm wall at 18" → same absolute wall at 24"
//   (wall thickness is absolute; inner factors unchanged from 18" version)
//
// Scale factor 24" hull: SCALE_24 = 2.9294 (24" / original model unit)
// Centroid of s_middle.stl at 24" scale:
//   CX = 135.712 × (2.9294/2.1974) = 180.95 mm
//   CY = −50.459 × (2.9294/2.1974) = −67.28 mm
//   CZ =  27.348 × (2.9294/2.1974) =  36.47 mm
// Inner scale factors (from 18" scad — wall is absolute not proportional):
//   INNER_SX = 0.962373
//   INNER_SY = 0.959565
//   INNER_SZ = 0.908966

SCALE_24 = 2.9294;

// Centroid of s_middle.stl in 24"-scaled coordinate space
CX =  180.95;
CY =  -67.28;
CZ =   36.47;

// Inner-shell scale factors (preserve 2.5mm absolute wall thickness)
INNER_SX = 0.962373;
INNER_SY = 0.959565;
INNER_SZ = 0.908966;

difference() {
    // Outer shell: s_middle.stl scaled to 24" hull
    scale([SCALE_24, SCALE_24, SCALE_24])
        import("../../thingverse-serenity/files/s_middle.stl");

    // Inner void: shifted inward by centroid, scaled to leave 2.5mm wall
    translate([CX, CY, CZ])
    scale([INNER_SX, INNER_SY, INNER_SZ])
    translate([-CX, -CY, -CZ])
    scale([SCALE_24, SCALE_24, SCALE_24])
        import("../../thingverse-serenity/files/s_middle.stl");
}
