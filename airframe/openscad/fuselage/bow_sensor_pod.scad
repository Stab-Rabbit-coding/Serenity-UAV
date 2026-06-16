// ============================================================
// bow_sensor_pod.scad — Rev R1 (2026-06-15)
//
// Forward-facing bow sensor assembly for Serenity 24" hull.
// Replaces the two canonical convex domes at the head section
// bow flat face with functional sensor aperture sockets:
//
//   Dome A (dorsal)  → 19 mm Nano camera socket
//                      e.g. RunCam Nano 4 or equivalent nano-19
//                      format: 19×19×19 mm body, 12 mm lens bore.
//                      Forward-looking video — feeds Inara's stack.
//                      [REF-SENSOR-001]
//
//   Dome B (ventral) → Benewake TFmini-S long-range ToF sensor
//                      (12 m indoor / 7 m outdoor, 100 Hz, UART/I2C)
//                      [REF-SENSOR-002]
//                      + 12 mm OD crosshair-pattern laser module
//                      (≤ 5 mW, 650 nm, optionally energised via
//                      GPIO-switched N-channel MOSFET; bore-sighted
//                      at 30° below horizon on aircraft CL).
//                      [REF-IEC-002, REF-FDA-001]
//
// This file defines ONLY the CSG subtraction volumes (negative
// material).  Printed carrier bezels and hardware are separate files
// (bow_camera_bezel.scad, bow_tof_laser_bezel.scad — future work;
// see TODO.md §1.1.1.1a).
//
// ── Coordinate system ────────────────────────────────────────
//
// SCAD hull frame (identical to hull frame per CLAUDE.md Rev R1):
//   X  — lateral,      positive port  (left)
//   Y  — longitudinal, positive aft   (back)  — bow tip at Y ≈ -288 mm
//   Z  — vertical,     positive dorsal (up)
//   Origin coincides with SerenityAssembly.FCStd world origin
//   after bake (bake translation = [-332, -18, +61] mm, identity
//   rotation).  See tools/bake_hull_frame.py.
//
// Bow forward direction is -Y.
// Rotation convention used in this file:
//
//   BOW_ROT   = [90, 0, 0]
//     Rx(90°) maps default +Z cylinder axis to -Y (forward).
//     Derivation: Rx(90°)[0,0,1] = [0, -sin90, cos90] = [0,-1,0] ✓
//
//   LASER_ROT = [120, 0, 0]
//     Rx(120°) maps default +Z cylinder axis to 30° below the
//     forward horizontal: [0, -sin120, cos120] = [0,-0.866,-0.500] ✓
//     Bore vector: forward (-Y) rotated 30° toward ventral (-Z).
//
// Within each cutter module the inner translate([0, 0, -(WALL_T+1)])
// offsets the local origin so that local z = 0 is the INTERIOR face
// of the hull skin and local z = WALL_T + 1 is the EXTERIOR face.
// Positive local z → toward exterior (bow tip, -Y in hull frame).
// Negative local z → deeper into interior (+Y in hull frame).
//
// ── Dome positions ───────────────────────────────────────────
//
// All positions are ESTIMATED from the Thingiverse source mesh
// geometry (CLAUDE.md §Aircraft Geometry reference).  Verify every
// constant in a slicer cross-section at Y = BOW_FACE_Y before
// printing.  See TODO.md §1.1.1.1a for the complete slicer
// verification task list.
//
// ── Regulatory notes ─────────────────────────────────────────
//
// [REF-IEC-002 Table 3] The crosshair laser is Class 3R (≤ 5 mW,
//   650 nm visible-band).
// [REF-FDA-001 §1040.10] Laser product must bear required safety
//   labels; enable circuitry must include a key-switch or equivalent
//   controlled-access interlock.  GPIO enable counts as an
//   administrative control only; physical interlock required for
//   shipment.  Operator to consult local state laser-safety
//   regulations.
// [REF-FAA-002 §107.29] The laser does NOT substitute for required
//   anti-collision lighting during night operations.
// [REF-FAA-002 §107.51] Laser must not be operated in a manner that
//   creates a hazard to any airspace user.  Operator is responsible
//   for ensuring the beam cannot strike aircraft, persons, or
//   vehicles.
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
// ============================================================

$fn = 64;

// ── Head shell centroid (replicated from head_shell24.scad) ──────────
//   Must match head_shell24.scad CX / CZ if used together.
BOW_CX = 161.33;   // mm — lateral centroid = aircraft CL
BOW_CZ =  69.08;   // mm — vertical centroid of head section

// ── Bow flat face — longitudinal station ─────────────────────────────
//   Head section STL Y_min = -288 mm (nose tip).  The canonical
//   Serenity bow has a subtly flat face ~4–6 mm aft of the very point.
//   VERIFY by slicer cross-section at Y = -285 to -280; adjust
//   BOW_FACE_Y until both dome pockets land within the hull skin.
BOW_FACE_Y = -283.0;   // mm — SCAD Y of bow exterior face; VERIFY slicer

// ── Dome A — dorsal (camera socket) ─────────────────────────────────
//   Estimated 14 mm dorsal of vertical centroid; on aircraft CL.
//   VERIFY Z in slicer cross-section at Y = BOW_FACE_Y.
DOME_A_X = BOW_CX;            // mm — laterally on aircraft CL
DOME_A_Y = BOW_FACE_Y;        // mm — bow exterior face
DOME_A_Z = BOW_CZ + 14.0;    // mm ≈ 83 mm dorsal; VERIFY slicer

// ── Dome B — ventral (ToF + laser socket) ───────────────────────────
//   Estimated 9 mm ventral of vertical centroid; on aircraft CL.
//   VERIFY Z in slicer cross-section at Y = BOW_FACE_Y.
//   ToF aperture offset 6 mm dorsal of dome-B centre to provide
//   clearance above the angled laser bore.
//   Laser bore centre 7 mm ventral of dome-B centre.
DOME_B_X = BOW_CX;            // mm — laterally on aircraft CL
DOME_B_Y = BOW_FACE_Y;        // mm — bow exterior face
DOME_B_Z = BOW_CZ - 9.0;     // mm ≈ 60 mm ventral; VERIFY slicer

TOF_Z_OFFSET   =  6.0;   // mm — ToF centre above DOME_B_Z
LASER_Z_OFFSET = -7.0;   // mm — laser bore centre below DOME_B_Z

// ── Wall / cutter parameters (match head_shell24.scad) ───────────────
WALL_MM = 2.0;    // mm — hull skin thickness
WALL_T  = 3.5;    // mm — cutter overlap (2.0 mm skin + 1.5 mm clearance)

// ── Rotation constants ───────────────────────────────────────────────
BOW_ROT   = [ 90, 0, 0];   // forward-facing: +Z cylinder → -Y (forward)
LASER_ROT = [120, 0, 0];   // 30° below horizon: +Z → [0,-0.866,-0.500]

// ============================================================
// A — 19 mm Nano camera socket
// ============================================================
//
// Camera format: 19 mm Nano (RunCam Nano 4 or equivalent).
// Body: 19×19×19 mm.  Lens: M7 thread, 12 mm clear bore.
// Mount: 4× M2 on 14×14 mm pitch (± 7 mm from lens centre).
// Exterior: 12 mm lens bore + 21×21×1 mm bezel recess +
//   4× M2 DIN 7991 90° countersunk holes.
// Interior: 20×20×21 mm camera body pocket (19 mm + 0.5 mm
//   clearance per side, 19 mm depth + 2 mm connector clearance).
//
// [REF-SENSOR-001] RunCam Nano 4 product specification.

CAM_APER_D    = 12.0;   // mm — lens aperture bore diameter
CAM_BEZ_W     = 21.0;   // mm — bezel recess width (19 mm + 1 mm/side)
CAM_BEZ_DEP   =  1.0;   // mm — bezel recess depth (camera face flush)
CAM_M2_D      =  2.2;   // mm — M2 clearance through-hole (ISO 286 H12)
CAM_M2_PITCH  = 14.0;   // mm — M2 hole pitch (± 7 mm from centre)
CAM_CSK2_OD   =  4.5;   // mm — M2 flathead countersink OD (DIN 7991 90°)
CAM_CSK2_D    =  1.2;   // mm — M2 countersink depth
CAM_BODY_W    = 20.0;   // mm — interior pocket width (19 + 1 mm clear)
CAM_BODY_H    = 20.0;   // mm — interior pocket height (19 + 1 mm clear)
CAM_BODY_D    = 21.0;   // mm — interior pocket depth (19 mm body + 2 mm connector clearance)

// ----------------------------------------------------------------------------
// Module: bow_camera_cut(pos)
//   Subtracts the 19 mm Nano camera socket from the head shell.
//   pos = [x, y, z] of socket lens-centre on the hull EXTERIOR face.
//   Aperture faces -Y (forward, bow direction) via BOW_ROT.
//
//   Inner-scope z convention (after translate([0,0,-(WALL_T+1)])):
//     z = 0          interior face of hull skin
//     z = WALL_T+1   exterior face of hull skin (pos.Y)
//     z = WALL_T+2   1 mm past exterior (cutter clearance)
//     z < 0          deeper into interior
// ----------------------------------------------------------------------------
module bow_camera_cut(pos) {
    translate(pos)
    rotate(BOW_ROT)
    translate([0, 0, -(WALL_T + 1)]) {

        // Lens aperture bore — through full hull skin
        cylinder(h = WALL_T + 2, d = CAM_APER_D);

        // Bezel seating recess — 1 mm deep at exterior face, 21×21 mm
        //   Camera face sits flush at hull outer surface.
        translate([-CAM_BEZ_W / 2, -CAM_BEZ_W / 2, WALL_T + 1 - CAM_BEZ_DEP])
            cube([CAM_BEZ_W, CAM_BEZ_W, CAM_BEZ_DEP + 1]);

        // 4× M2 countersunk mount holes (± 7 mm from lens centre)
        //   DIN 7991 90° flathead countersink from exterior.
        //   [REF-IEC-001 Cl.5.5.2] clearance maintained from camera PCB.
        for (dx = [-CAM_M2_PITCH / 2, CAM_M2_PITCH / 2])
        for (dy = [-CAM_M2_PITCH / 2, CAM_M2_PITCH / 2])
            translate([dx, dy, 0]) {
                cylinder(h = WALL_T + 2, d = CAM_M2_D);
                translate([0, 0, WALL_T + 1 - CAM_CSK2_D])
                    cylinder(h = CAM_CSK2_D + 1, d1 = CAM_M2_D, d2 = CAM_CSK2_OD);
            }

        // Interior camera body pocket — 20×20×21 mm, opens to interior
        //   z < 0 goes deeper into interior (aft/+Y in hull frame).
        translate([-CAM_BODY_W / 2, -CAM_BODY_H / 2, -CAM_BODY_D])
            cube([CAM_BODY_W, CAM_BODY_H, CAM_BODY_D + 1]);
    }
}

// ============================================================
// B — Benewake TFmini-S long-range ToF sensor socket
// ============================================================
//
// Sensor: Benewake TFmini-S.
//   Range: 0.1–12 m (indoor, SNR > 3); 0.1–7 m (outdoor).
//   FoV: 2.3° (full-angle); update rate: 100 Hz.
//   Interface: UART 115200 baud or I2C 400 kHz.
//   Power: 5 V, 140 mA (0.7 W) average.
//   Weight: 5 g.
//   Body: 35×18.5×21 mm (L × W × H).
//   Optical aperture: single PMMA lens, 8 mm diameter, centred on
//     the 35×18.5 mm face.  [REF-SENSOR-002]
//
// Mount design:
//   Exterior: 8 mm PMMA aperture bore + 11 mm OD × 0.5 mm seat ring
//   + 4× M1.6 DIN 7991 90° countersunk holes on R = 7 mm bolt circle.
//   Interior: 36×20×22 mm body pocket (sensor + 0.5 mm each dim).
//   PMMA window: 8 mm dia × 2 mm thick; PMMA transmits 905 nm IR ✓.
//   Avionics interface: UART routed to Shepherd (Wash UART2, I2C fallback).
//   [REF-NIST-001 §2.1] all sensor telemetry authenticated per ZTA policy.

TOF_APER_D    =  8.0;   // mm — PMMA aperture bore (8 mm sensor lens)
TOF_RING_OD   = 11.0;   // mm — PMMA disc seat ring OD
TOF_RING_DEP  =  0.5;   // mm — PMMA disc seat ring recess depth
TOF_M16_D     =  1.7;   // mm — M1.6 clearance hole (ISO 286 H12)
TOF_M16_R     =  7.0;   // mm — M1.6 bolt circle radius (4 holes at 90°)
TOF_CSK16_OD  =  3.5;   // mm — M1.6 flathead countersink OD (DIN 7991 90°)
TOF_CSK16_D   =  1.0;   // mm — M1.6 countersink depth
TOF_BODY_X    = 36.0;   // mm — interior pocket X (35 mm + 0.5 mm clear)
TOF_BODY_Y    = 20.0;   // mm — interior pocket Y (18.5 mm + 0.75 mm/side)
TOF_BODY_D    = 22.0;   // mm — interior pocket depth (21 mm + 1 mm clear)

// ----------------------------------------------------------------------------
// Module: bow_tof_cut(pos)
//   Subtracts the TFmini-S forward-facing sensor socket from head shell.
//   pos = [x, y, z] of aperture centre on the hull EXTERIOR face.
//   Aperture faces -Y (forward) via BOW_ROT.
// ----------------------------------------------------------------------------
module bow_tof_cut(pos) {
    translate(pos)
    rotate(BOW_ROT)
    translate([0, 0, -(WALL_T + 1)]) {

        // PMMA aperture bore — through full hull skin
        cylinder(h = WALL_T + 2, d = TOF_APER_D);

        // PMMA disc seat ring — 0.5 mm recess at exterior face, 11 mm OD
        translate([0, 0, WALL_T + 1 - TOF_RING_DEP])
            cylinder(h = TOF_RING_DEP + 1, d = TOF_RING_OD);

        // 4× M1.6 countersunk mount holes (bolt circle R = 7 mm, 45° offset)
        for (a = [45, 135, 225, 315])
            rotate([0, 0, a])
            translate([TOF_M16_R, 0, 0]) {
                cylinder(h = WALL_T + 2, d = TOF_M16_D);
                translate([0, 0, WALL_T + 1 - TOF_CSK16_D])
                    cylinder(h = TOF_CSK16_D + 1, d1 = TOF_M16_D, d2 = TOF_CSK16_OD);
            }

        // Interior sensor body pocket — 36×20×22 mm, opens to interior
        translate([-TOF_BODY_X / 2, -TOF_BODY_Y / 2, -TOF_BODY_D])
            cube([TOF_BODY_X, TOF_BODY_Y, TOF_BODY_D + 1]);
    }
}

// ============================================================
// C — 12 mm crosshair laser bore, 30° below horizon
// ============================================================
//
// Bore for a standard 12 mm OD crosshair-pattern laser module.
//   Module spec: ≤ 5 mW, 650 nm visible; cross-line generating optic
//   (two 90°-crossed lines); any 12 mm OD module with cross-line lens.
//   Body: typically 12 mm OD × 30–35 mm long.
//
// Bore axis: 30° below the horizontal forward direction.
//   In hull frame: axis vector [0, -cos30°, -sin30°] = [0,-0.866,-0.500].
//   At 10 ft (3.05 m) AGL in level flight the crosshair illuminates
//   ground ≈ 5.3 m (17.4 ft) ahead of the bow.
//   At 50 ft (15.2 m) AGL the crosshair is ≈ 26.3 m (86.4 ft) ahead.
//   All ranges measured along ground track.
//
// Alignment: bore axis passes through aircraft lateral CL (DOME_B_X =
//   BOW_CX = 161.33 mm SCAD = aircraft CL).  Laser is aligned to
//   aircraft CL both laterally (X = CL) and vertically (bore in
//   the YZ symmetry plane of the aircraft).
//
// Enable circuit: laser anode → 10 Ω current-set resistor → drain of
//   2N7002 N-channel MOSFET → GND.  Gate driven by Shepherd Wash
//   GPIO with 10 kΩ pull-down; software must set GPIO HIGH to
//   energise.  Default state: disabled.
//
// Regulatory classification:
//   Class 3R per [REF-IEC-002 §4.3.3, Table 3] (P ≤ 5 mW, λ 630–680 nm).
//   Requires [REF-FDA-001 §1040.10(f)] safety interlock.
//   Operator must ensure beam cannot strike aircraft or persons
//   per [REF-FAA-002 §107.51].

LASER_BORE_D      = 12.5;   // mm — bore ID (12 mm module + 0.25 mm/side clearance)
LASER_BORE_L      = 38.0;   // mm — bore length along axis (35 mm module + 3 mm clear)
LASER_SETSCR_D    =  3.2;   // mm — M3 set-screw hole diameter (locks module in bore)
LASER_SETSCR_OFST = 20.0;   // mm — set-screw centre from bore entrance (along axis)

// ----------------------------------------------------------------------------
// Module: bow_laser_cut(pos)
//   Subtracts the 12 mm crosshair laser bore from the head shell.
//   pos = [x, y, z] of bore entrance centre on the hull EXTERIOR face.
//   Bore axis: 30° below horizon, forward direction (LASER_ROT).
//   Set-screw hole: lateral (X direction), 20 mm from bore entrance.
// ----------------------------------------------------------------------------
module bow_laser_cut(pos) {
    translate(pos)
    rotate(LASER_ROT)
    translate([0, 0, -(WALL_T + 1)]) {

        // Main laser module bore — 12.5 mm ID through hull skin and into interior
        cylinder(h = WALL_T + 1 + LASER_BORE_L, d = LASER_BORE_D);

        // M3 lateral set-screw hole — perpendicular to bore axis (in local XY plane)
        //   Locks the laser module against axial and rotational movement.
        //   Local X → lateral (port/stbd in hull frame).
        translate([0, 0, WALL_T + 1 + LASER_SETSCR_OFST])
            rotate([0, 90, 0])
            cylinder(h = LASER_BORE_D + 4, d = LASER_SETSCR_D, center = true);
    }
}

// ============================================================
// Combined bow sensor pod — all cuts
// ============================================================

// ----------------------------------------------------------------------------
// Module: bow_pod_cuts()
//   Combined subtraction for the full bow sensor pod assembly.
//   Intended to be used inside a difference() in head_shell24.scad.
//
//   Dome A (dorsal, Z ≈ 83 mm):
//     19 mm Nano camera socket, forward-facing, on aircraft CL.
//
//   Dome B (ventral, Z ≈ 60 mm):
//     TFmini-S ToF socket, 6 mm dorsal of dome-B centre, fwd-facing.
//     12 mm crosshair laser bore, 7 mm ventral of dome-B centre,
//       30° below horizon, on aircraft CL.
//
//   All positions VERIFY in slicer at Y = BOW_FACE_Y before printing.
//   See TODO.md §1.1.1.1a for the complete verification task list.
// ----------------------------------------------------------------------------
module bow_pod_cuts() {
    // Dome A — 19 mm Nano camera socket (dorsal dome)
    bow_camera_cut([DOME_A_X, DOME_A_Y, DOME_A_Z]);

    // Dome B — TFmini-S ToF socket (6 mm dorsal of dome-B centre)
    bow_tof_cut([DOME_B_X, DOME_B_Y, DOME_B_Z + TOF_Z_OFFSET]);

    // Dome B — crosshair laser bore (7 mm ventral of dome-B centre, 30° down)
    bow_laser_cut([DOME_B_X, DOME_B_Y, DOME_B_Z + LASER_Z_OFFSET]);
}

// Standalone preview — render only the cut volumes for position verification.
// This call executes only when this file is opened directly in OpenSCAD;
// when loaded via `use <bow_sensor_pod.scad>` in head_shell24.scad the
// module definitions are imported but the call below is NOT executed.
bow_pod_cuts();
