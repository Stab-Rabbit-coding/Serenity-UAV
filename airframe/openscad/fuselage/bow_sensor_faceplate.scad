// ============================================================
// bow_sensor_faceplate.scad — Rev R1c (2026-06-30)
//
// Single combined retainer faceplate for the bow sensor pod.  Replaces
// the modeller's two convex bow camera bumps and the (superseded)
// separate bow_camera_bezel.scad / bow_tof_laser_bezel.scad parts.
// Seats on the 40°-tilted bow mounting flat (~26.4 x 15 mm) and carries
// all three apertures in one horizontal row:
//
//     camera (PORT) ── laser exit (CL) ── ToF (STARBOARD)
//
// The plate mates to the seat cut by bow_face_seat() in
// bow_sensor_pod.scad (bumps shaved flat + 4x M2 inserts).  Sensor
// bodies pocket into the nose behind the flat; the laser module is
// rear-mounted (only its 6 mm beam exits the plate).
//
// Aperture centres are given in the plate LOCAL frame (origin =
// aperture-row centroid hull(-169.85,-300.53,116.59) = SCAD
// FACEPLATE_CTR; +x = PORT, +y = up-along-flat, +z = outward/away from
// hull).  They were derived by projecting the skin-verified hull aperture
// points onto the flat:
//     camera (+8.65, -0.35)   laser (-0.82, +0.04)   ToF (-7.82, +0.30)
// In the head assembly the plate is placed at FACEPLATE_CTR with
// rotate(BOW_ROT) = rotate([130,0,0]).  [REF-SENSOR-001, REF-SENSOR-002,
// REF-IEC-002, REF-FDA-001]
//
// Windows:
//   ToF: 8 mm dia x 2 mm PMMA disc (rear counterbore; transmits 905 nm IR).
//   Laser: optional 5 mm dia x 2 mm PMMA exit window.
//   Camera: open 10 mm lens bore (no window; bezel flange shades the lens).
//
// Fastening: 4x M2 flathead from EXTERIOR, flush-countersunk in the plate
// corners, into the 4x M2 heat-set inserts set in the seat (bow_face_seat).
//
// Material: CF-PETG, 0.15 mm layer, 4 perimeters, >= 40% infill.  Print
// face (apertures) down.  Units: mm.
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
//        (geometry authored by Claude Opus 4.8)
// License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
// ============================================================

$fn = 72;

// ── Plate ────────────────────────────────────────────────────────────
FP_W   = 28.0;   // mm — plate width  (X, port-stbd); seat is 29 mm
FP_H   = 16.0;   // mm — plate height (in-plane vertical); seat is 17 mm
FP_T   =  2.5;   // mm — plate thickness (CF-PETG)
FP_R   =  2.0;   // mm — corner radius

// ── Aperture centres (plate local; see header) ───────────────────────
CAM_XY   = [ 8.65, -0.35];   CAM_D   = 10.0;   // camera lens bore
LASER_XY = [-0.82,  0.04];   LASER_D =  6.0;   // laser beam exit
TOF_XY   = [-7.82,  0.30];   TOF_D   =  8.0;   // ToF aperture
TOF_WIN_OD  = 8.4;   TOF_WIN_DEP = 2.0;          // rear PMMA disc counterbore

// ── Mount holes (align to bow_face_seat inserts FP_INS_X/Y) ──────────
FP_M2_X   = 11.0;   // mm — corner hole X offset
FP_M2_Y   =  6.0;   // mm — corner hole Y offset
M2_CLR_D  =  2.4;   // mm — M2 clearance
M2_CSK_OD =  4.2;   // mm — M2 flathead countersink OD (DIN 7991 90°)
M2_CSK_D  =  1.2;   // mm — countersink depth (front/exterior face)

// ----------------------------------------------------------------------------
// Module: rounded_plate(w, h, t, r)
// ----------------------------------------------------------------------------
module rounded_plate(w, h, t, r) {
    linear_extrude(height = t)
        hull()
            for (sx = [-1, 1], sy = [-1, 1])
                translate([sx * (w / 2 - r), sy * (h / 2 - r)])
                    circle(r = r);
}

// ----------------------------------------------------------------------------
// Module: bow_sensor_faceplate()
//   Local +z is the OUTWARD (exterior) direction; back face at z = 0
//   seats on the flat, front face at z = FP_T.
// ----------------------------------------------------------------------------
module bow_sensor_faceplate() {
    difference() {
        rounded_plate(FP_W, FP_H, FP_T, FP_R);

        // Camera lens bore (through)
        translate([CAM_XY[0], CAM_XY[1], -1])
            cylinder(h = FP_T + 2, d = CAM_D);

        // Laser beam exit (through)
        translate([LASER_XY[0], LASER_XY[1], -1])
            cylinder(h = FP_T + 2, d = LASER_D);

        // ToF aperture (through) + rear PMMA disc counterbore
        translate([TOF_XY[0], TOF_XY[1], -1])
            cylinder(h = FP_T + 2, d = TOF_D);
        translate([TOF_XY[0], TOF_XY[1], -0.01])
            cylinder(h = TOF_WIN_DEP, d = TOF_WIN_OD);   // rear (z=0 side) pocket

        // 4x M2 corner mount holes with exterior countersink
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx * FP_M2_X, sy * FP_M2_Y, 0]) {
                translate([0, 0, -1])
                    cylinder(h = FP_T + 2, d = M2_CLR_D);
                // Countersink opens on the front (exterior) face z = FP_T
                translate([0, 0, FP_T - M2_CSK_D])
                    cylinder(h = M2_CSK_D + 0.01, d1 = M2_CLR_D, d2 = M2_CSK_OD);
            }
    }
}

bow_sensor_faceplate();
