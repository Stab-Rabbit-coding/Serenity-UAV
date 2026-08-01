// ============================================================
// bow_sensor_pod.scad — Rev R1c (2026-06-30)
//
// Forward-facing bow sensor assembly for Serenity 24" hull.
// Replaces the modeller's two convex camera bumps on the 40° bow
// mounting flat with functional sensor aperture sockets:
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
// material) cut into the head shell.  The printed exterior retainer is
// the single combined faceplate bow_sensor_faceplate.scad (Rev R1c,
// supersedes the earlier separate camera/ToF/laser bezels).
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
// printing for final design validation.
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

// ── Nose-tip flat-face layout (Rev R1c, 2026-06-30) ──────────────────
//   SUPERSEDES the Rev R1 vertical "Dome A/Dome B" stack and the
//   interim Rev R1b straight-forward (-Y) tip layout.  Geometric
//   verification of the baked canonical head shell (tools/verify_bow_pod.py
//   against airframe/stls/fuselage/head_shell24_2mm_repaired.stl) located
//   the canonical bow MOUNTING FLAT: a ~26.4 x 15 mm planar face whose
//   outward normal is tilted 39.8 deg about the +X (port/stbd) axis from
//   forward, i.e. n = (0, -0.766, -0.643) — it faces forward-and-down and
//   runs down-and-aft from the nose tip.  Flat centre hull (-167, -301,
//   120).  The modeller placed TWO convex camera bumps on this flat (the
//   ship's two bow cameras), at hull X -161 (port) and X -175 (stbd),
//   ~2.2 mm proud; per design direction (2026-06-30) those bumps are
//   REPLACED by the functional camera (port) and ToF (stbd) apertures,
//   and a crosshair laser is added on the centreline between them.  All
//   three apertures lie on the one flat and are carried by a single
//   combined faceplate (bow_sensor_faceplate.scad).
//
//   Distribution (HORIZONTAL, on the flat):
//       camera -> PORT bump (+X)   ToF -> STBD bump (-X)   laser -> CL
//
//   Bores are NORMAL to the 40 deg flat (BOW_ROT below).  Aperture face
//   points were measured as the skin intersection along the flat normal;
//   they fit the 26.4 mm width in one row (span ~25.5 mm).  Positions are
//   PART-LOCAL SCAD coords (hull = local + [-332,-18,+61]; bake_hull_frame
//   Head_Shell).  This is a verified ROUGH fit — final fractional-mm
//   alignment (and the ~1.5 mm stbd over-run of the ToF onto the flat
//   roll-off) is to be confirmed in FreeCAD per CLAUDE.md complex-geometry
//   policy.  Re-run tools/verify_bow_pod.py after any change.
//
//   Hull-frame X convention: +X = PORT (left), -X = STARBOARD (right).

// Camera — 19 mm Nano socket, on the PORT camera bump.
//   hull (-161.20, -300.68, 116.01) -> SCAD below.  Face lens bore 10 mm.
CAM_POS   = [170.80, -282.68, 55.01];   // SCAD [x,y,z]; on flat, skin-verified

// ToF — TFmini-S socket, on the STARBOARD camera bump.
//   Body rolled vertical (TOF_BODY_ROLL) so its 36 mm long axis runs in
//   the flat's in-plane vertical, narrowing its lateral footprint.
//   hull (-177.67, -300.98, 116.61) -> SCAD below.
TOF_POS   = [154.33, -282.98, 55.61];   // SCAD [x,y,z]; on flat, skin-verified
TOF_BODY_ROLL = 90;                     // deg — roll body about bore axis

// Laser — crosshair bore, on aircraft CL, between the two bumps.
//   Rear-mounted: only a 6 mm beam exit pierces the flat (12.5 mm module
//   bore is behind the skin); bore NORMAL to the flat (40 deg below
//   horizon, was 30 deg in Rev R1 — re-aim in FreeCAD if 30 deg desired).
//   hull (-170.67, -299.94, 117.14) -> SCAD below.
LASER_POS = [161.33, -281.94, 56.14];   // SCAD [x,y,z]; on CL, skin-verified

// Combined faceplate footprint on the flat (for the bump-removal seat
// cutter).  Centre = mean of the three aperture face points (balances the
// asymmetric camera/ToF row); sized to clear all three apertures.
//   hull (-169.85, -300.53, 116.59) -> SCAD below.
FACEPLATE_CTR = [162.15, -282.53, 55.59];  // SCAD aperture-row centroid
FACEPLATE_W   = 29.0;   // mm — seat width  (X, port-stbd)
FACEPLATE_H   = 17.0;   // mm — seat height (flat in-plane vertical)

// ── Wall / cutter parameters (match head_shell24.scad) ───────────────
WALL_MM = 2.0;    // mm — hull skin thickness
WALL_T  = 3.5;    // mm — cutter overlap (2.0 mm skin + 1.5 mm clearance)

// ── Rotation constants ───────────────────────────────────────────────
//   BOW_ROT maps a +Z-axis cutter onto the flat's outward normal:
//   Rx(130 deg)[0,0,1] = [0,-sin130,cos130] = [0,-0.766,-0.643] = n.  The
//   130 = 90 (forward) + 40 (flat tilt about X).  All three apertures and
//   the faceplate seat share this orientation.
BOW_ROT   = [130, 0, 0];   // normal to the 40 deg bow flat
LASER_ROT = [130, 0, 0];   // laser normal to flat (see LASER_POS note)
LASER_EXIT_D = 6.0;        // mm — beam exit aperture through the skin

// ============================================================
// A — 19 mm Nano camera socket
// ============================================================
//
// Camera format: 19 mm Nano (RunCam Nano 4 or equivalent).
// Body: 19×19×19 mm.  Lens: M7 thread.
// Rev R1c: the shell carries ONLY a 10 mm lens aperture + a 20×20×21 mm
//   interior body pocket; the exterior seat, bezel and all mount
//   fasteners moved to the combined faceplate (bow_sensor_faceplate.scad)
//   and the shared seat cut bow_face_seat().  Legacy CAM_BEZ_*/CAM_M2_*
//   constants below are retained for reference only (unused by the cut).
//
// [REF-SENSOR-001] RunCam Nano 4 product specification.

CAM_APER_D    = 10.0;   // mm — lens aperture bore (Rev R1c: trimmed 12->10
                        //      so camera+laser+ToF apertures fit the 26.4 mm
                        //      flat width; a Nano lens needs only ~8 mm)
CAM_BEZ_W     = 21.0;   // mm — (legacy) standalone-bezel recess width;
                        //      unused now the combined faceplate seats on
                        //      the flat — see bow_sensor_faceplate.scad
CAM_BEZ_DEP   =  1.0;   // mm — (legacy) bezel recess depth
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

        // Lens aperture bore — through full hull skin (10 mm, Rev R1c).
        //   Bezel recess and the 4x M2 face countersinks are deleted in
        //   Rev R1c: the combined faceplate (bow_sensor_faceplate.scad)
        //   provides the exterior seat and all mount fasteners.
        cylinder(h = WALL_T + 2, d = CAM_APER_D);

        // Interior camera body pocket — 20×20×21 mm, opens to interior
        //   z < 0 goes deeper into interior (behind the flat, into nose).
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
// Mount design (Rev R1c):
//   Shell cut: 8 mm aperture bore + 36×20×22 mm interior body pocket,
//     rolled vertical (TOF_BODY_ROLL) to pack to starboard on the flat.
//   Exterior PMMA disc seat + 8.4 mm counterbore and mount fasteners are
//     on the combined faceplate (bow_sensor_faceplate.scad); legacy
//     TOF_RING_*/TOF_M16_* constants below are reference only (unused).
//   PMMA window: 8 mm dia × 2 mm thick; PMMA transmits 905 nm IR ✓.
//   Avionics interface: UART routed to Shepherd (Pilot UART2, I2C fallback).
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
// Module: bow_tof_cut(pos, roll)
//   Subtracts the TFmini-S forward-facing sensor socket from head shell.
//   pos  = [x, y, z] of aperture centre on the hull EXTERIOR face.
//   roll = body rotation (deg) about the bore axis.  The aperture, seat
//          ring and bolt circle are all rotationally symmetric, so roll
//          only reorients the rectangular interior body pocket.  roll =
//          90 turns the 36 mm long pocket axis from lateral (X) to
//          vertical (Z), narrowing the lateral footprint to 20 mm so the
//          starboard ToF clears the centreline laser bore.
//   Aperture faces -Y (forward) via BOW_ROT.
// ----------------------------------------------------------------------------
module bow_tof_cut(pos, roll = 0) {
    translate(pos)
    rotate(BOW_ROT)
    rotate([0, 0, roll])
    translate([0, 0, -(WALL_T + 1)]) {

        // PMMA aperture bore — through full hull skin (8 mm).
        //   PMMA disc seat ring and the 4x M1.6 face countersinks are
        //   deleted in Rev R1c; the combined faceplate carries the PMMA
        //   window and the mount fasteners.
        cylinder(h = WALL_T + 2, d = TOF_APER_D);

        // Interior sensor body pocket — 36×20×22 mm, opens to interior.
        //   Rolled 90° (TOF_BODY_ROLL) so the 36 mm axis runs in the
        //   flat's in-plane vertical, behind the flat into the nose.
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
// Alignment (Rev R1c): bore axis passes through aircraft lateral CL
//   (LASER_POS X = BOW_CX = 161.33 mm SCAD = aircraft CL) and is normal
//   to the 40° bow flat (40° below horizon).  Rev R1c rear-mounts the
//   module: only LASER_EXIT_D (6 mm) pierces the flat; the 12.5 mm
//   module bore is behind the skin.  See bow_laser_cut().
//
// Enable circuit: laser anode → 10 Ω current-set resistor → drain of
//   2N7002 N-channel MOSFET → GND.  Gate driven by Shepherd Pilot
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

        // Beam exit aperture — 6 mm through the hull skin (Rev R1c
        //   rear-mount: only the beam exits on the flat, so the laser's
        //   face footprint is 6 mm, not the 12.5 mm module bore).
        cylinder(h = WALL_T + 2, d = LASER_EXIT_D);

        // Module bore — 12.5 mm, BEHIND the skin into the interior.
        //   z = 0 is the interior face of the skin; the module is loaded
        //   from inside the nose and butts up under the 6 mm exit.
        translate([0, 0, -LASER_BORE_L])
            cylinder(h = LASER_BORE_L + 0.1, d = LASER_BORE_D);

        // M3 lateral set-screw hole — perpendicular to bore axis.
        //   Locks the laser module against axial and rotational movement.
        translate([0, 0, -LASER_SETSCR_OFST])
            rotate([0, 90, 0])
            cylinder(h = LASER_BORE_D + 4, d = LASER_SETSCR_D, center = true);
    }
}

// ============================================================
// D — Faceplate seat (bump removal) + mount inserts
// ============================================================
//
// The modeller placed two convex camera bumps (~2.2 mm proud) on the
// bow flat.  bow_face_seat() shaves everything proud of the flat plane
// over the faceplate footprint, leaving a clean planar seat for the
// combined faceplate (bow_sensor_faceplate.scad), and drills 4 blind
// M2 heat-set-insert holes near the corners to anchor it.

SEAT_CLEAR   = 6.0;   // mm — material removed proud of flat (clears 2.2 mm bumps)
FP_INS_D     = 3.0;   // mm — M2 heat-set insert pilot hole
FP_INS_DEP   = 6.0;   // mm — insert depth into the skin/interior
FP_INS_X     = 11.0;  // mm — insert X offset (matches faceplate FP_M2_X)
FP_INS_Y     = 6.0;   // mm — insert Y offset (matches faceplate FP_M2_Y)

// ----------------------------------------------------------------------------
// Module: bow_face_seat(ctr, w, h)
//   ctr = faceplate centre on the flat (SCAD).  w,h = seat extents on the
//   flat (X width, in-plane height).  Oriented normal to the 40° flat.
// ----------------------------------------------------------------------------
module bow_face_seat(ctr, w, h) {
    translate(ctr)
    rotate(BOW_ROT)
    translate([0, 0, -(WALL_T + 1)]) {
        // Shave bump material proud of the flat plane (z = WALL_T+1)
        translate([-w / 2, -h / 2, WALL_T + 1 - 0.01])
            cube([w, h, SEAT_CLEAR]);
        // 4× M2 insert pilot holes, blind into the interior
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx * FP_INS_X, sy * FP_INS_Y, -FP_INS_DEP])
                cylinder(h = FP_INS_DEP + 0.5, d = FP_INS_D);
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
//   Nose-tip flat-face layout (Rev R1c) — all on the 40° bow flat,
//   covered by one combined faceplate (bow_sensor_faceplate.scad):
//     Faceplate seat: bumps shaved flat + 4× M2 inserts.
//     Camera (PORT bump, +X):  10 mm lens aperture + body pocket.
//     ToF (STARBOARD bump, -X): 8 mm aperture + body pocket (rolled).
//     Laser (CL):               6 mm beam exit + 12.5 mm bore behind.
//
//   Verified against the baked canonical mesh by tools/verify_bow_pod.py;
//   fine-tune fractional-mm in FreeCAD as needed.
// ----------------------------------------------------------------------------
module bow_pod_cuts() {
    // Faceplate seat — remove the two camera bumps, prep mount inserts
    bow_face_seat(FACEPLATE_CTR, FACEPLATE_W, FACEPLATE_H);

    // Camera — 19 mm Nano socket, on the PORT bump
    bow_camera_cut(CAM_POS);

    // ToF — TFmini-S socket, on the STARBOARD bump, body rolled vertical
    bow_tof_cut(TOF_POS, TOF_BODY_ROLL);

    // Laser — beam exit on CL, module bore behind, normal to flat
    bow_laser_cut(LASER_POS);
}

// Standalone preview — render only the cut volumes for position verification.
// This call executes only when this file is opened directly in OpenSCAD;
// when loaded via `use <bow_sensor_pod.scad>` in head_shell24.scad the
// module definitions are imported but the call below is NOT executed.
bow_pod_cuts();
