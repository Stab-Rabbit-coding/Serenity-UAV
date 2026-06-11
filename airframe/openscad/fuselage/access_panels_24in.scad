// access_panels_24in.scad
// Serenity UAV Rev R — Hull Access Panels and Ventral Hatch Covers (24" build)
//
// Purpose:
//   Parametric library producing all removable access panels for the 24"-scaled
//   Serenity hull.  Eight parts are defined across three categories:
//
//   (A) Avionics-bay Faraday covers  — four identical-footprint covers that cap
//       the 2.44 in × 1.65 in (62 × 42 mm) Faraday bay openings cut into the
//       port-side hull skin.  Each cover drops a 0.20 in (5 mm) shoulder lip
//       into the opening and fastens with 4× M3 screws into heat-set inserts
//       installed in boss posts moulded into the shell.
//
//       Shepherd cover  — head section,   starboard lateral face
//       Inara cover     — cargo section,  starboard lateral face, GPS recess
//       River cover     — cargo section,  starboard lateral face, GPS recess
//       Simon cover     — middle section, starboard lateral face
//
//   (B) Ventral hatch covers — two large hatches on the underside of the middle
//       section giving access to the battery bay and Kaylee (PDB) bay.  Each
//       cover is retained by self-tapping M2.5 screws into bonded PETG frames.
//
//       Battery cover   — 6.30 in × 2.36 in (160 × 60 mm) outer footprint
//       Kaylee cover    — 4.53 in × 3.94 in (115 × 100 mm) outer footprint
//
//   (C) Ventral hatch frames — bonded PETG frames epoxy-set into the hull
//       openings to provide positive M2.5 thread engagement and the required
//       2-wall contact annulus (CLAUDE.md §Fabrication Standards).
//
//       Battery frame   — matches battery-bay hull cut
//       Kaylee frame    — matches Kaylee-bay hull cut
//
// Coordinate convention (all modules):
//   Origin at cover face centroid.
//   +X = fore (toward nose), +Y = up (away from hull — exterior face faces +Y
//        for Faraday covers; –Y for ventral hatches), +Z = port.
//   Place in hull-frame coordinates when assembling.
//
// Faraday cover interface (head/cargo/middle shell SCADs):
//   Opening:    62.0 × 42.0 mm  (AV_OPEN_X × AV_OPEN_Z)
//   Boss BC:    ±25.0 mm (fore/aft) × ±15.0 mm (Z) from bay centre
//   Boss bore:  M3 heat-set RX-M3×5.7 (4.0 mm nom, 4.1 mm bore)
//   Screw:      M3 × 8 mm pan-head into boss insert; 3.3 mm clearance bore
//
// GPS retention-ring clearance (Inara + River covers only):
//   The GPS patch antenna retention rings protrude ≈ 0.24 in (6 mm) from the
//   hull surface at the boss cut-outs in cargo_sect_shell24.scad.
//   A 1.65 in (42 mm) OD × 0.24 in (6 mm) deep cylindrical recess is milled
//   into the underside of the shoulder lip to clear the ring without
//   penetrating the 0.079 in (2 mm) cover face.
//   Offset of GPS centre from bay centre:
//     Inara:  −0.524 in (−13.3 mm) in Z (toward starboard)
//     River:  +0.028 in (+0.7 mm)  in Z (slightly port of centre)
//
// Ventral frame bonding:
//   Frames are epoxied flush with the hull inner surface using West System
//   105/206 epoxy.  Frame OD matches the hull opening; frame ID provides
//   0.020 in (0.5 mm) insertion clearance per side for the cover shoulder.
//   Nominal wall = 0.24 in (6 mm); boss/pilot hole spacing = 0.31 in (8 mm)
//   from frame inner edge.
//
// Print specification:
//   All parts: CF-PETG, 0.15 mm layers, 4 perimeters, 40% gyroid infill.
//   Ventral frames: same spec; bond face sanded flat before installation.
//
// Gear standard / references:
//   CLAUDE.md §Fabrication: minimum 2-wall contact annulus, positive-stop
//   shoulder; friction fits alone unacceptable for flight-critical joints.
//   Ruthex RX-M3×5.7 heat-set insert: 4.0 mm bore, 5.7 mm OD, 5.7 mm length.
//   ISO 14589 — Ref for heat-set insert pullout in thermoplastics.
//
// Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date:    2026-06-11
// Rev:     R (2026-06-11): Initial release — derived from current shell SCADs.
//   Faraday-bay dimensions confirmed from:
//     head_shell24.scad       (Shepherd bay)
//     cargo_sect_shell24.scad (Inara + River bays, GPS positions)
//     middle_canonical_shell24.scad (Simon bay, battery hatch, Kaylee hatch)

// ── Resolution ────────────────────────────────────────────────────────────────

$fn = 64;

// ── Avionics-bay Faraday Cover Parameters ────────────────────────────────────
//
// All four Faraday bays share the same opening and boss geometry (Rev S4 baseline).
// Imperial primary; metric in parentheses per CLAUDE.md.

AV_OPEN_X   = 62.0;   // [mm] hull opening fore-aft (2.44 in)
AV_OPEN_Z   = 42.0;   // [mm] hull opening lateral  (1.65 in)
AV_SHOULDER =  5.0;   // [mm] shoulder lip width each side (0.20 in)
AV_COVER_X  = AV_OPEN_X + 2 * AV_SHOULDER;   // [mm] total cover fore-aft = 72 mm (2.83 in)
AV_COVER_Z  = AV_OPEN_Z + 2 * AV_SHOULDER;   // [mm] total cover lateral  = 52 mm (2.05 in)
AV_COVER_T  =  2.0;   // [mm] cover face plate thickness (0.079 in) — 2-wall min
AV_STEP_D   =  1.5;   // [mm] shoulder step depth (positive-stop per CLAUDE.md)
AV_STEP_H   =  3.0;   // [mm] shoulder insertion height into opening
AV_TOTAL_H  = AV_COVER_T + AV_STEP_H;   // [mm] total cover height = 5.0 mm

// M3 screw clearance bores — boss positions match shell SCAD boss DX/DZ constants
AV_SCREW_DX =  25.0;   // [mm] boss offset fore-aft from bay centre (1.0 in)
AV_SCREW_DZ =  15.0;   // [mm] boss offset lateral from bay centre (0.59 in)
AV_SCREW_D  =   3.3;   // [mm] M3 clearance bore diameter
AV_SCREW_CS =   6.0;   // [mm] M3 pan-head countersink diameter (shallow recess)
AV_SCREW_CS_D = 1.0;   // [mm] countersink recess depth (flush-mount aesthetic)

// ── GPS Clearance Recess Parameters ───────────────────────────────────────────
//
// Used only on Inara and River covers.  The GPS retention ring protrudes above
// the hull-face boss and must be cleared on the cover underside.
// 42 mm diameter keeps the recess within the cover face (62 × 42 mm minimum).

GPS_RECESS_OD  = 42.0;   // [mm] GPS retention ring clearance bore OD (1.65 in)
GPS_RECESS_DEP =  2.0;   // [mm] recess depth from shoulder underside (0.079 in)
                          //   6 mm hull recess – 4 mm flush cover = 2 mm remaining
                          //   clearance depth needed on cover underside

// GPS centre offset from bay centre in Z (lateral axis):
//   Derived from cargo_sect_shell24.scad:
//     Inara Z_CEN = 119.0 mm;  GPS_PORT Z = 104.7 mm  → offset = −14.3 mm
//     River Z_CEN =  44.0 mm;  GPS_STBD Z =  44.7 mm  → offset = +0.7 mm
//   TODO §1.1.1 Rev S3/S4 lists −13.3 / +0.7 — using −14.3 here to match
//   actual cargo_sect_shell24.scad GPS_PORT_POS derivation.
GPS_INARA_DZ = -14.3;   // [mm] Inara GPS offset in Z from bay centre
GPS_RIVER_DZ =  +0.7;   // [mm] River GPS offset in Z from bay centre

// ── Ventral Hatch Parameters (Battery + Kaylee) ────────────────────────────────
//
// Hatch openings from middle_canonical_shell24.scad:
//   BATT_HATCH_X = 150.0 mm, BATT_HATCH_Z = 50.0 mm
//   KAYLEE_HATCH_X = 105.0 mm, KAYLEE_HATCH_Z = 90.0 mm

H_SHOULDER  =  5.0;   // [mm] cover shoulder lip (0.20 in)
H_COVER_T   =  2.0;   // [mm] hatch face plate thickness (0.079 in)
H_STEP_D    =  1.5;   // [mm] shoulder step depth (positive-stop, same as av cover)
H_STEP_H    =  3.0;   // [mm] shoulder insertion height
H_TOTAL_H   = H_COVER_T + H_STEP_H;   // [mm] total hatch height = 5.0 mm

// Battery hatch
BATT_OPEN_X  = 150.0;   // [mm] battery bay hull opening fore-aft (5.91 in)
BATT_OPEN_Z  =  50.0;   // [mm] battery bay hull opening lateral  (1.97 in)
BATT_COVER_X = BATT_OPEN_X + 2 * H_SHOULDER;   // [mm] = 160 mm (6.30 in)
BATT_COVER_Z = BATT_OPEN_Z + 2 * H_SHOULDER;   // [mm] =  60 mm (2.36 in)

// Kaylee hatch
KLEE_OPEN_X  = 105.0;   // [mm] Kaylee bay hull opening fore-aft (4.13 in)
KLEE_OPEN_Z  =  90.0;   // [mm] Kaylee bay hull opening lateral  (3.54 in)
KLEE_COVER_X = KLEE_OPEN_X + 2 * H_SHOULDER;   // [mm] = 115 mm (4.53 in)
KLEE_COVER_Z = KLEE_OPEN_Z + 2 * H_SHOULDER;   // [mm] = 100 mm (3.94 in)

// ── Ventral Hatch Frame Parameters ────────────────────────────────────────────
//
// Bonded PETG frame epoxied into hull ventral opening.
// OD = hull opening; ID = opening + 2×clearance (0.5 mm per side insertion gap).
// Nominal wall = 6 mm gives M2.5 pilot thread depth ≥ 5 mm (adequate in PETG).
// Pilot holes spaced H_SCREW_INSET = 8 mm from frame inner edge (centre of wall).

H_FRAME_T       =  6.0;   // [mm] frame wall thickness (0.24 in)
H_FRAME_H       =  4.5;   // [mm] frame height = hull skin (2.5 mm max) + 2 mm insert margin
H_INSERT_CLEAR  =  0.5;   // [mm] cover shoulder insertion clearance per side
H_PILOT_D       =  2.1;   // [mm] M2.5 pilot bore (self-tapping in PETG)
H_SCREW_INSET   =  8.0;   // [mm] pilot hole centre from frame outer edge (midwall)
// Number of M2.5 screws per hatch edge: one per 50 mm of perimeter run
// Battery hatch: 2 screws per long edge (×2) + 1 per short edge (×2) = 6 total
// Kaylee hatch:  2 screws per long edge (×2) + 2 per short edge (×2) = 8 total
// Positions computed per-module below.

// ── Module: av_cover_body ─────────────────────────────────────────────────────
//
// Parametric base for all four Faraday-bay covers.
//
// Arguments:
//   open_x  — hull opening fore-aft dimension [mm]
//   open_z  — hull opening lateral dimension [mm]
//   flip    — set true for port-facing bays (default false = starboard-facing)
//
// Geometry:
//   Face plate (AV_COVER_T thick) at Y=0 → Y=AV_COVER_T.
//   Step shoulder (AV_STEP_D rebate) at perimeter, height AV_STEP_H below face.
//   4× M3 clearance bores + shallow CS recesses on face.
//   Origin at exterior face centroid (X=fore+, Z=port+).
//
module av_cover_body(open_x = AV_OPEN_X, open_z = AV_OPEN_Z, flip = false) {
    mirror_v = flip ? [0, 0, 1] : [0, 0, 0];   // optional Z-mirror for port-side bays

    mirror(mirror_v)
    difference() {
        union() {
            // ── Outer face plate ──────────────────────────────────────────
            // Full-footprint plate covers the opening shoulder and face.
            translate([-AV_COVER_X/2, 0, -AV_COVER_Z/2])
                cube([AV_COVER_X, AV_COVER_T, AV_COVER_Z]);

            // ── Shoulder insertion lip ─────────────────────────────────────
            // Narrowed block drops into hull opening; step-shoulder butts
            // against hull face (positive-stop per CLAUDE.md).
            translate([-open_x/2, -AV_STEP_H, -open_z/2])
                cube([open_x, AV_STEP_H, open_z]);
        }

        // ── Shoulder step rebate ───────────────────────────────────────────
        // Thin slot cut on the underside of the face plate at the opening
        // perimeter, creating the 1.5 mm recessed shoulder that locks against
        // the hull face.
        translate([-open_x/2 - AV_STEP_D, -AV_STEP_D, -open_z/2 - AV_STEP_D])
            cube([open_x + 2*AV_STEP_D, AV_STEP_D + 0.01,
                  open_z + 2*AV_STEP_D]);

        // ── M3 screw clearance bores (4×) ─────────────────────────────────
        // 3.3 mm through-bore + 6.0 mm × 1.0 mm pan-head recess on face.
        for (sx = [-AV_SCREW_DX/2, AV_SCREW_DX/2])
            for (sz = [-AV_SCREW_DZ/2, AV_SCREW_DZ/2]) {
                // Clearance bore
                translate([sx, -AV_STEP_H - 0.1, sz])
                    rotate([-90, 0, 0])
                        cylinder(h = AV_TOTAL_H + 0.2, d = AV_SCREW_D);
                // Countersink recess (flush mounting)
                translate([sx, AV_COVER_T - AV_SCREW_CS_D, sz])
                    rotate([-90, 0, 0])
                        cylinder(h = AV_SCREW_CS_D + 0.01, d = AV_SCREW_CS);
            }
    }
}

// ── Module: gps_recess_cut ────────────────────────────────────────────────────
//
// Cylindrical pocket milled into the underside of the shoulder insertion lip
// to clear the GPS retention ring that protrudes from the hull boss.
//
// Arguments:
//   dz  — offset of GPS centre from cover centroid in Z [mm]
//
// Geometry:
//   Centred at (0, −AV_STEP_H + GPS_RECESS_DEP, dz) so the flat base of the
//   pocket sits GPS_RECESS_DEP mm up from the bottom face of the shoulder.
//   The cylinder extends 0.1 mm proud of the bottom face to ensure clean cut.
//   If the GPS centre is near a cover edge, the difference() naturally trims
//   the bore to the cover boundary, forming a partial-arc notch.
//
module gps_recess_cut(dz) {
    translate([0, -AV_STEP_H - 0.1, dz])
        rotate([-90, 0, 0])
            cylinder(h = GPS_RECESS_DEP + 0.1, d = GPS_RECESS_OD);
}

// ── Module: shepherd_cover ────────────────────────────────────────────────────
//
// Faraday bay cover for Shepherd (head section starboard lateral face).
// Plain 72 × 52 mm cover — no GPS antennas adjacent.
// Refs: head_shell24.scad BOOK_PANEL_X/Z, BOOK_BOSS_DX/DZ.
//
module shepherd_cover() {
    av_cover_body();
}

// ── Module: simon_cover ───────────────────────────────────────────────────────
//
// Faraday bay cover for Simon (middle section starboard lateral face).
// Plain 72 × 52 mm cover — no GPS antennas adjacent.
// Refs: middle_canonical_shell24.scad SIMON_PANEL_X/Z, SIMON_BOSS_DX/DZ.
//
module simon_cover() {
    av_cover_body();
}

// ── Module: inara_cover ───────────────────────────────────────────────────────
//
// Faraday bay cover for Inara (cargo section starboard lateral face).
// GPS clearance recess at GPS_INARA_DZ offset from cover centroid in Z.
// Refs: cargo_sect_shell24.scad Z_CEN=119, GPS_PORT_POS Z=104.7.
//
module inara_cover() {
    difference() {
        av_cover_body();
        gps_recess_cut(GPS_INARA_DZ);
    }
}

// ── Module: river_cover ───────────────────────────────────────────────────────
//
// Faraday bay cover for River (cargo section starboard lateral face, aft bay).
// GPS clearance recess at GPS_RIVER_DZ offset from cover centroid in Z.
// Refs: cargo_sect_shell24.scad Z_CEN=44, GPS_STBD_POS Z=44.7.
//
module river_cover() {
    difference() {
        av_cover_body();
        gps_recess_cut(GPS_RIVER_DZ);
    }
}

// ── Module: hatch_cover ───────────────────────────────────────────────────────
//
// Parametric ventral hatch cover.
//
// Arguments:
//   open_x   — hull opening fore-aft [mm]
//   open_z   — hull opening lateral (athwartships) [mm]
//
// Geometry identical to av_cover_body() but sized for ventral openings:
//   Face plate at Y=0 (exterior-face side, facing hull interior in situ).
//   Shoulder lip drops down (–Y) into hull opening.
//   No screw bores — ventral hatches use bonded frame pilots (see hatch_frame).
//
// Screw pilot bores pass through cover face into frame below:
//   Battery:  6 pilots  — 2 per long edge (fore/aft), 1 per short edge (port/stbd)
//   Kaylee:   8 pilots  — 2 per long edge, 2 per short edge
//   Pilot = H_PILOT_D = 2.1 mm (clearance through cover face; frame is tapped)
//
module hatch_cover(open_x, open_z) {
    cover_x = open_x + 2 * H_SHOULDER;
    cover_z = open_z + 2 * H_SHOULDER;

    // Pilot positions: pairs evenly spaced on long edges, singles on short edges
    long_pilots_x = (open_x > 120) ? [-open_x/3, open_x/3] : [-open_x/4, open_x/4];
    short_pilots   = (open_z > 80)  ? [-open_z/3, open_z/3] : [0];

    difference() {
        union() {
            // Face plate
            translate([-cover_x/2, 0, -cover_z/2])
                cube([cover_x, H_COVER_T, cover_z]);
            // Shoulder insertion lip
            translate([-open_x/2, -H_STEP_H, -open_z/2])
                cube([open_x, H_STEP_H, open_z]);
        }

        // Shoulder step rebate (positive-stop shoulder per CLAUDE.md)
        translate([-open_x/2 - H_STEP_D, -H_STEP_D, -open_z/2 - H_STEP_D])
            cube([open_x + 2*H_STEP_D, H_STEP_D + 0.01, open_z + 2*H_STEP_D]);

        // Screw pilot bores through cover face — long edges (in X, at ±Z_EDGE)
        for (px = long_pilots_x) {
            for (zs = [-1, 1]) {
                translate([px, -H_STEP_H - 0.1, zs * (open_z/2 + H_SHOULDER/2)])
                    rotate([-90, 0, 0])
                        cylinder(h = H_TOTAL_H + 0.2, d = H_PILOT_D);
            }
        }
        // Screw pilot bores — short edges (in Z, at ±X_EDGE)
        for (pz = short_pilots) {
            for (xs = [-1, 1]) {
                translate([xs * (open_x/2 + H_SHOULDER/2), -H_STEP_H - 0.1, pz])
                    rotate([-90, 0, 0])
                        cylinder(h = H_TOTAL_H + 0.2, d = H_PILOT_D);
            }
        }
    }
}

// ── Module: hatch_frame ───────────────────────────────────────────────────────
//
// Parametric bonded PETG ventral hatch frame.
//
// Arguments:
//   open_x   — hull opening fore-aft [mm]
//   open_z   — hull opening lateral [mm]
//
// The frame is a hollow rectangular ring:
//   OD = hull opening (press-fit during bonding with West System 105/206 epoxy)
//   ID = hull opening + 2 × H_INSERT_CLEAR  (cover shoulder clears with 0.5 mm per side)
//   Wall = H_FRAME_T = 6.0 mm
//   Height = H_FRAME_H = 4.5 mm
//
// Pilot bores match hatch_cover pilot positions; M2.5 self-tapping into PETG.
// Thread engagement: H_FRAME_H − H_COVER_T − H_STEP_H = 4.5 − 5.0 = −0.5 mm
//   → Frame slightly recessed; actual thread engagement ≈ 3.5 mm in frame body
//   (H_FRAME_H starts at hull inner face; cover shoulder seats at opening top).
//
// Bonding face: –Y (hull inner surface); +Y face is flush with hull opening bottom.
//
module hatch_frame(open_x, open_z) {
    frame_od_x = open_x;
    frame_od_z = open_z;
    frame_id_x = open_x + 2 * H_INSERT_CLEAR;
    frame_id_z = open_z + 2 * H_INSERT_CLEAR;

    long_pilots_x = (open_x > 120) ? [-open_x/3, open_x/3] : [-open_x/4, open_x/4];
    short_pilots   = (open_z > 80)  ? [-open_z/3, open_z/3] : [0];

    difference() {
        // Outer frame block
        translate([-frame_od_x/2, 0, -frame_od_z/2])
            cube([frame_od_x, H_FRAME_H, frame_od_z]);

        // Inner cavity (cover-shoulder channel + 0.5 mm clearance per side)
        translate([-frame_id_x/2, -0.1, -frame_id_z/2])
            cube([frame_id_x, H_FRAME_H + 0.2, frame_id_z]);

        // Pilot bores — long edges
        for (px = long_pilots_x) {
            for (zs = [-1, 1]) {
                translate([px, -0.1, zs * (frame_id_z/2 + H_FRAME_T/2)])
                    rotate([-90, 0, 0])
                        cylinder(h = H_FRAME_H + 0.2, d = H_PILOT_D);
            }
        }
        // Pilot bores — short edges
        for (pz = short_pilots) {
            for (xs = [-1, 1]) {
                translate([xs * (frame_id_x/2 + H_FRAME_T/2), -0.1, pz])
                    rotate([-90, 0, 0])
                        cylinder(h = H_FRAME_H + 0.2, d = H_PILOT_D);
            }
        }
    }
}

// ── Named Instances ───────────────────────────────────────────────────────────

// Avionics bay covers — call directly for single-part render:
module battery_cover() { hatch_cover(BATT_OPEN_X, BATT_OPEN_Z); }
module battery_frame()  { hatch_frame(BATT_OPEN_X, BATT_OPEN_Z); }
module kaylee_cover()   { hatch_cover(KLEE_OPEN_X, KLEE_OPEN_Z); }
module kaylee_frame()   { hatch_frame(KLEE_OPEN_X, KLEE_OPEN_Z); }

// ── Render Selector ───────────────────────────────────────────────────────────
//
// Set RENDER to select a single part for STL export, or set RENDER = "layout"
// to show all 8 parts spread on the build plate for visual review.
//
// Part names (use as RENDER value):
//   "shepherd"  — Shepherd Faraday cover  (head section)
//   "inara"     — Inara Faraday cover     (cargo section, GPS recess)
//   "river"     — River Faraday cover     (cargo section, GPS recess)
//   "simon"     — Simon Faraday cover     (middle section)
//   "battery"   — battery ventral cover   (middle section)
//   "battery_f" — battery ventral frame
//   "kaylee"    — Kaylee ventral cover    (middle section)
//   "kaylee_f"  — Kaylee ventral frame
//   "layout"    — all 8 parts on plate

RENDER = "layout";   // ← change to part name for STL export

if (RENDER == "shepherd")  shepherd_cover();
if (RENDER == "inara")     inara_cover();
if (RENDER == "river")     river_cover();
if (RENDER == "simon")     simon_cover();
if (RENDER == "battery")   battery_cover();
if (RENDER == "battery_f") battery_frame();
if (RENDER == "kaylee")    kaylee_cover();
if (RENDER == "kaylee_f")  kaylee_frame();

if (RENDER == "layout") {
    // ── Layout: all 8 parts arrayed on build plate ────────────────────────
    // Row 1: four identical-footprint Faraday covers (72 × 52 mm), 10 mm gap
    translate([-(AV_COVER_X + 10) * 1.5, 0, 0]) shepherd_cover();
    translate([-(AV_COVER_X + 10) * 0.5, 0, 0]) inara_cover();
    translate([ (AV_COVER_X + 10) * 0.5, 0, 0]) river_cover();
    translate([ (AV_COVER_X + 10) * 1.5, 0, 0]) simon_cover();

    // Row 2: battery cover + frame, then Kaylee cover + frame
    translate([-(BATT_COVER_X + 10)/2 - (KLEE_COVER_X + 10)/2 - 5,
               AV_COVER_Z + 30, 0])
        battery_cover();
    translate([-(BATT_COVER_X + 10)/2 - (KLEE_COVER_X + 10)/2 - 5,
               AV_COVER_Z + 30 + BATT_COVER_X + 15, 0])
        battery_frame();

    translate([ (KLEE_COVER_X + 10)/2 + 5,
               AV_COVER_Z + 30, 0])
        kaylee_cover();
    translate([ (KLEE_COVER_X + 10)/2 + 5,
               AV_COVER_Z + 30 + KLEE_COVER_X + 15, 0])
        kaylee_frame();
}
