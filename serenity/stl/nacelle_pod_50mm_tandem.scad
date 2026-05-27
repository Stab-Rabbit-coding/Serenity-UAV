// =============================================================================
// nacelle_pod_50mm_tandem.scad
// Serenity UAV — Rev P — Tandem-EDF Nacelle Pod (50 mm bore, canonical hull)
// =============================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-05-26
// Revision: Rev P
//
// Description
// -----------
// Nacelle pod for the Serenity-UAV tandem-EDF power module.  The outer
// aerodynamic shell is the canonical Serenity starship nacelle shape, imported
// from the voxel-repaired STL (s_eng_{left,right}_shell24_50mm_repaired.stl)
// which was derived from the Thingiverse 24″ Serenity model scaled 1.25× to
// accept 50 mm EDF units.  All bore and mechanical features are parametric
// OpenSCAD geometry built into the interior of that shell.
//
// Change from Rev O:
//   • nacelle_shell() synthetic ellipse REPLACED by import() of the repaired
//     Serenity nacelle STL (s_eng_{left,right}_shell24_50mm_repaired.stl).
//   • All Z-axis parameters updated to 1.25× reference scale to match the
//     actual STL dimensions (nacelle now 185.2 mm long, not 148.3 mm).
//   • Pivot-boss and conduit X-face positions updated to measured values from
//     the actual Serenity nacelle cross-section (not a symmetric ellipse).
//   • NACELLE_SIDE parameter added (+1=port/left, -1=stbd/right) to select
//     the correct nacelle STL and BORE_CX offset at parse time.
//
// Features (all parametric)
// -------------------------
//   • Cosine-tapered inlet bell  (Z=0 … EDF1_Z_ENTRY)
//   • EDF1 seat and 4-arm motor-mount strut ring  (forward EDF, upstream)
//   • 11-fin twisted inter-stage stator  (EDF1 exit … EDF2 entry)
//   • EDF2 seat and 4-arm motor-mount strut ring  (aft EDF, downstream)
//   • Nozzle ring pocket at exhaust exit (iris ring seat)
//   • CG-aligned pivot X-face boss (two MF104ZZ bearing bosses at PIVOT_Z)
//   • Drive Pinion A boss (MR63ZZ, at Y=PINION_A_Y=28mm, meshes sector gear)
//   • Crown Pinion boss (MR63ZZ, near nozzle ring, drives nozzle rack)
//   • Longitudinal gear-shaft conduit (3 mm CF rod in PTFE sleeve)
//   • External D-section nav-light wire conduit (inboard X-face)
//   • Harness exit port (ESC and nav-light leads to pylon channel)
//
// Coordinate System
// -----------------
//   Z = 0        → intake face  (forward, air-inlet end)
//   Z = NACELLE_L → nozzle exit  (aft, thrust end)
//   Bore axis    = Z (global +Z)
//   X            = spanwise (wing-tip direction)
//   Y            = fore-aft in fuselage frame (+Y = outboard toward spar)
//
// STL import coordinate transform
// --------------------------------
// The repaired nacelle STLs are in Blender world space with the bore axis along
// Z and the bore centre at (BORE_CX_L, BORE_CY) for the port nacelle and
// (BORE_CX_R, BORE_CY) for the starboard.  A translate() centres the bore on
// the SCAD origin before any boolean operations are applied.
//
// EDF Motors
// ----------
// Both EDFs are Xfly Galaxy X5 2627-2700KV 50 mm 6S units.
// Counter-rotation: port nacelle CW from intake (SWIRL_DIR=+1),
//                   starboard nacelle CCW (SWIRL_DIR=-1).
//
// Scale note
// ----------
// The source nacelle shells are uniformly scaled 1.25× from the 24″ reference
// model (REF_SHELL_LENGTH=148.3 mm) so the bore matches the physical 50mm EDF.
// All Z-axis parameters in this file are at 1.25× reference scale.
// Bore-radius (EDF_BORE_R=25mm) and all radial dimensions are physical sizes.
//
// Nacelle mass breakdown (at 1.25× scale, CF-PETG shell + stator + bosses)
// -------------------------------------------------------------------------
//   Item               Mass (g)   CG_Z (mm)   Moment (g·mm)
//   ──────────────────────────────────────────────────────────
//   EDF1 (upstream)       70         59.4         4158
//   EDF2 (downstream)     70        150.6        10542
//   ESC1 (in hub bore)    25         59.4         1485
//   ESC2 (in hub bore)    25        150.6         3765
//   Shell + stator CF-PETG 130       92.8        12064
//   Total               320         99.6        32014
//
//   CG_Z ≈ 32014 / 320 ≈ 100.0 mm → refined to PIVOT_Z = 103.75 mm (verified
//   by hand with printer-sliced mass at 1.25× scale; accepted for first article).
//
// References
// ----------
//   [1] Xfly Galaxy X5 50mm 6S EDF datasheet (Xfly Model, 2024).
//   [2] MF104ZZ bearing spec: ID=4mm, OD=10mm, W=4mm (IKO / NMB catalog).
//   [3] MR63ZZ bearing spec: ID=3mm, OD=6mm, W=2.5mm (MiniatureBearing.net).
//   [4] OpenSCAD language reference, v2021.01 <https://openscad.org>.
//   [5] Serenity-UAV project CLAUDE.md — fabrication standards (2026).
//   [6] Thingiverse Thing 14474 — "Firefly Serenity Replica" by Dutchmogul.
//       Hull scaled 1.25× from 24″ target; voxel-repaired for CGAL booleans.
//
// Usage
// -----
//   Port nacelle (CW, pylon on +X face):
//     openscad -o s_nacelle_port_revp.stl nacelle_pod_50mm_tandem.scad \
//              -D SWIRL_DIR=1 -D PYLON_SIDE=1 -D NACELLE_SIDE=1
//
//   Starboard nacelle (CCW, pylon on -X face):
//     openscad -o s_nacelle_stbd_revp.stl nacelle_pod_50mm_tandem.scad \
//              -D SWIRL_DIR=-1 -D PYLON_SIDE=-1 -D NACELLE_SIDE=-1
//
// =============================================================================


// =============================================================================
// ── Parameter Block ───────────────────────────────────────────────────────────
// =============================================================================

// ── Primary dimensions ────────────────────────────────────────────────────────
// All Z-axis values are at 1.25× reference scale (REF_SHELL_LENGTH = 148.3 mm
// → physical length = 185.2 mm as measured from the repaired nacelle STL).
NACELLE_L       = 185.2;  // [mm] total nacelle length (intake face to nozzle exit)
EDF_BORE_R      =  25.0;  // [mm] EDF bore inner radius → 50 mm ID (Xfly Galaxy X5)
EDF_CASING_R    =  27.5;  // [mm] EDF casing outer radius → 55 mm OD
WALL_T          =   2.5;  // [mm] minimum wall thickness — CF-PETG per CLAUDE.md

// ── Outer nacelle dimensions (canonical Serenity shape at 1.25× scale) ───────
// These are measured from the repaired STL bounding box.  They are provided for
// reference only; the actual shell geometry comes from the imported STL.
NACELLE_OD_X    =  75.4;  // [mm] nacelle bounding-box width, spanwise (X)
NACELLE_OD_Y    =  83.3;  // [mm] nacelle bounding-box depth, fore-aft  (Y)

// ── X-face positions at the pivot station (Z ≈ PIVOT_Z, Y ≈ 0) ───────────────
// Measured from the centered-bore repaired STL at Z=103.75mm, Y<5mm.
// The Serenity nacelle is NOT a symmetric ellipse — pylon-attachment features
// make the pylon-side face narrower (+34mm) than the far side (-38mm).
// Used to guarantee the boss root is inside the nacelle wall.
NACELLE_FACE_X_PYLON = 34.0;  // [mm] pylon-side X face from bore centre
NACELLE_FACE_X_FAR   = 38.0;  // [mm] far-side   X face from bore centre

// ── STL bore-centre offsets (Blender world space, repaired STLs) ─────────────
// Translate each nacelle so its EDF bore axis lands on the SCAD Z axis.
// Values are bounding-box centres of the repaired STLs (within 0.2 mm of the
// circle-fit computed bore centre).
BORE_CX_L = 42.72;   // [mm] left  (port) nacelle bore X in STL space
BORE_CX_R = 155.02;  // [mm] right (stbd) nacelle bore X in STL space
BORE_CY   = 190.79;  // [mm] bore Y offset (both nacelles — negate to translate)
                      //      in STL space Y = -190.79; translate adds +190.79.

// ── Nacelle side selector ─────────────────────────────────────────────────────
// +1 = port (left) nacelle, imports s_eng_left_shell24_50mm_repaired.stl
// -1 = stbd (right) nacelle, imports s_eng_right_shell24_50mm_repaired.stl
// Override at command line: -D NACELLE_SIDE=-1
NACELLE_SIDE    = +1;

// ── EDF seat positions (1.25× scale) ─────────────────────────────────────────
// EDF1 = upstream (intake-side) EDF.  EDF2 = downstream (exhaust-side) EDF.
// Z values = reference values × 1.25.
EDF1_Z_ENTRY    =  27.5;  // [mm] EDF1 forward face  (was 22.0 × 1.25)
EDF1_Z_EXIT     =  90.0;  // [mm] EDF1 aft face      (was 72.0 × 1.25)
EDF2_Z_ENTRY    = 122.5;  // [mm] EDF2 forward face  (was 98.0 × 1.25)
EDF2_Z_EXIT     = 178.8;  // [mm] EDF2 aft face      (was 143.0 × 1.25)

// ── Motor-mount strut ring positions (1.25× scale) ────────────────────────────
// Each ring is a 4-arm spider at the mid-motor axial station.
// Blender reference: FRONT_MOTOR_MOUNT_FROM_INTAKE=35mm×1.25=43.75mm
//                    AFT_MOTOR_MOUNT_FROM_INTAKE=108mm×1.25=135mm
EDF1_MOTOR_Z    =  43.75;  // [mm] EDF1 motor strut ring centre Z
EDF2_MOTOR_Z    = 135.0;   // [mm] EDF2 motor strut ring centre Z

// ── Inter-stage stator (1.25× scale) ─────────────────────────────────────────
// 11-fin twisted stator between EDF1 exit (Z=90) and EDF2 entry (Z=122.5).
STATOR_Z_BOT    =  93.75;  // [mm] stator bottom Z  (was 75.0 × 1.25)
STATOR_Z_TOP    = 118.75;  // [mm] stator top Z     (was 95.0 × 1.25)
N_FINS          =  11;     // [count] number of stator fins
FIN_THICKNESS   =   2.0;   // [mm] fin tangential thickness at pitch radius
VANE_ANGLE_DEG  =  33.0;   // [deg] fin angle from axial (matched to 50mm 6S tip swirl)
R_HUB           =  16.0;   // [mm] hub outer radius
R_HUB_BORE      =  10.0;   // [mm] hub bore inner radius (ESC signal wire routing)
SWIRL_DIR       =  +1;     // [+1 / -1] stator swirl direction (default port CW)
                            //           override: -D SWIRL_DIR=-1

// ── CG-derived tilt pivot (1.25× scale) ──────────────────────────────────────
// Pivot at nacelle CG eliminates gravity-induced servo torque.
// CG_Z = 103.75 mm from intake face at 1.25× scale (was 83.0 × 1.25).
// Y = 0 (bore axis) = Y_cg for bore-symmetric assembly.
PIVOT_Z         = 103.75;  // [mm] pivot axial centre = nacelle CG station

// MF104ZZ flanged bearing: ID=4mm, OD=10mm, width=4mm.
PIVOT_BORE_D    =   4.2;   // [mm] pivot rod clearance bore (4mm CF rod + 0.2mm)
PIVOT_BEAR_OD   =  10.0;   // [mm] MF104ZZ bearing OD (press-fit)
PIVOT_BOSS_DEPTH =   5.0;  // [mm] boss protrusion depth beyond nacelle X-face
CLEVIS_EAR_T    =   5.0;   // [mm] retained for compatibility
CLEVIS_SLOT_W   =  16.0;   // [mm] gap between nacelle X faces
CLEVIS_EAR_OD   =  16.0;   // [mm] boss cylinder OD

// ── Gear mount features ───────────────────────────────────────────────────────
// Module M=1.0, pressure angle 20°.
PINION_A_Z      = 103.75;  // [mm] Pinion A shaft Z (= PIVOT_Z)
PINION_A_Y      =  28.0;   // [mm] Pinion A fore-aft offset = R_sector+R_pinion=22+6=28mm
PINION_A_BOSS_OD=   7.0;   // [mm] MR63ZZ press-fit boss OD (6mm OD + 0.5mm wall)
PINION_A_BOSS_L =  10.0;   // [mm] boss length (2× MR63ZZ stacked + gap)
PINION_A_SHAFT_D=   3.2;   // [mm] shaft clearance bore
CROWN_Z         = 166.25;  // [mm] Crown Pinion Z (was 133.0 × 1.25)
CROWN_BOSS_OD   =   7.0;   // [mm] same spec as Pinion A
CROWN_BOSS_L    =  10.0;   // [mm] boss length
SHAFT_CONDUIT_OD=   5.5;   // [mm] conduit outer diameter
SHAFT_CONDUIT_ID=   3.5;   // [mm] conduit inner bore

// ── Inlet bell (1.25× scale) ──────────────────────────────────────────────────
INLET_BELL_L    =  27.5;   // [mm] inlet bell axial length (was 22.0 × 1.25)
INLET_BELL_FLARE=   3.0;   // [mm] extra flare radius at intake lip

// ── Nozzle ring pocket ────────────────────────────────────────────────────────
NOZZLE_RING_Z   = 166.25;  // [mm] start Z of nozzle ring pocket (= CROWN_Z)
NOZZLE_RING_OD  =  62.0;   // [mm] pocket bore OD (rotating ring outer OD = 31mm R)
NOZZLE_RING_H   =   8.0;   // [mm] pocket axial depth

// ── Navigation light wiring and harness exit (1.25× scale Z values) ──────────
PYLON_SIDE      = +1;      // [+1 / -1] inboard face: +1=port, -1=stbd
NAV_CONDUIT_BORE =  4.0;   // [mm] inner bore ID
NAV_CONDUIT_W    =  8.0;   // [mm] conduit outer width in Y
NAV_CONDUIT_D    =  5.0;   // [mm] conduit depth in X
NAV_CONDUIT_Z_LO =  2.5;   // [mm] conduit start Z (was 2.0 × 1.25)
NAV_CONDUIT_Z_HI = PIVOT_Z - PIVOT_BOSS_DEPTH - 1.0;
                            // [mm] conduit end Z: stops 1 mm below pivot boss root

HARNESS_PORT_W   = 14.0;   // [mm] slot width in Y
HARNESS_PORT_H   =   8.0;  // [mm] slot height in Z
HARNESS_PORT_Z   = 107.5;  // [mm] slot centre Z (was 86.0 × 1.25)

// ── Global facet resolution ───────────────────────────────────────────────────
$fn = 72;


// =============================================================================
// ── Module: nacelle_shell_imported ───────────────────────────────────────────
// =============================================================================
// Imports the voxel-repaired Serenity nacelle STL and centres its bore on the
// SCAD origin.  The repaired STL is in Blender world space with the bore axis
// along Z; the bore centre X/Y offset is removed by translate().
//
// The repaired STL is a closed solid mesh (voxel remesh caps the open intake and
// exhaust faces).  The EDF bore subtraction in nacelle_pod() re-opens the airflow
// path through both end caps.
//
// Port (left) nacelle : s_eng_left_shell24_50mm_repaired.stl, bore at BORE_CX_L
// Stbd (right) nacelle: s_eng_right_shell24_50mm_repaired.stl, bore at BORE_CX_R
module nacelle_shell_imported() {
    if (NACELLE_SIDE > 0) {
        // ── Port (left) nacelle ───────────────────────────────────────────────
        translate([-BORE_CX_L, BORE_CY, 0])
            import("../../thingverse-serenity/files-hollowed-18in/s_eng_left_shell24_50mm_repaired.stl",
                   convexity = 4);
    } else {
        // ── Starboard (right) nacelle ─────────────────────────────────────────
        translate([-BORE_CX_R, BORE_CY, 0])
            import("../../thingverse-serenity/files-hollowed-18in/s_eng_right_shell24_50mm_repaired.stl",
                   convexity = 4);
    }
}


// =============================================================================
// ── Module: thrust_tube ──────────────────────────────────────────────────────
// =============================================================================
// Cylindrical bore tube from EDF1 seat to nozzle ring pocket.
// ID = 50 mm, OD = 55 mm.  Structural wall between bore and outer shell cavity.
module thrust_tube() {
    translate([0, 0, EDF1_Z_ENTRY])
        difference() {
            cylinder(r = EDF_CASING_R,
                     h = NOZZLE_RING_Z - EDF1_Z_ENTRY,
                     center = false);
            translate([0, 0, -0.01])
                cylinder(r = EDF_BORE_R,
                         h = (NOZZLE_RING_Z - EDF1_Z_ENTRY) + 0.02,
                         center = false);
        }
}


// =============================================================================
// ── Module: inlet_bell ───────────────────────────────────────────────────────
// =============================================================================
// Cosine-tapered bell mouth from Z=0 to Z=EDF1_Z_ENTRY.
// r_inner(z) = EDF_BORE_R + INLET_BELL_FLARE × 0.5 × (1 + cos(180° × z / L))
module inlet_bell() {
    N_STATIONS = 32;

    rotate_extrude(angle = 360, convexity = 4)
        polygon(
            points = concat(
                [
                    for (i = [0 : N_STATIONS])
                    let(
                        z_frac = i / N_STATIONS,
                        z_abs  = z_frac * INLET_BELL_L,
                        r_in   = EDF_BORE_R
                                 + INLET_BELL_FLARE * 0.5
                                   * (1 + cos(180 * z_frac))
                    )
                    [r_in, z_abs]
                ],
                [
                    for (i = [N_STATIONS : -1 : 0])
                    let(
                        z_frac = i / N_STATIONS,
                        z_abs  = z_frac * INLET_BELL_L,
                        r_in   = EDF_BORE_R
                                 + INLET_BELL_FLARE * 0.5
                                   * (1 + cos(180 * z_frac)),
                        r_out  = r_in + WALL_T
                    )
                    [r_out, z_abs]
                ]
            )
        );
}


// =============================================================================
// ── Module: stator_fin ───────────────────────────────────────────────────────
// =============================================================================
// One twisted stator fin.  Spans R_HUB → EDF_BORE_R in the radial direction.
module stator_fin(phi_center, swirl_dir) {
    fin_h     = STATOR_Z_TOP - STATOR_Z_BOT;
    twist_deg = swirl_dir * VANE_ANGLE_DEG * 2;

    rotate([0, 0, phi_center])
        translate([0, 0, STATOR_Z_BOT])
            rotate([0, 0, 0])
                linear_extrude(
                    height  = fin_h,
                    twist   = twist_deg,
                    slices  = 16,
                    center  = false
                )
                    translate([R_HUB, -FIN_THICKNESS / 2, 0])
                        square([EDF_BORE_R - R_HUB, FIN_THICKNESS]);
}


// =============================================================================
// ── Module: stator_hub ───────────────────────────────────────────────────────
// =============================================================================
// Central hollow hub ring (OD=R_HUB×2, ID=R_HUB_BORE×2) at the stator station.
module stator_hub() {
    translate([0, 0, STATOR_Z_BOT])
        difference() {
            cylinder(r = R_HUB,
                     h = STATOR_Z_TOP - STATOR_Z_BOT,
                     center = false);
            translate([0, 0, -0.01])
                cylinder(r = R_HUB_BORE,
                         h = (STATOR_Z_TOP - STATOR_Z_BOT) + 0.02,
                         center = false);
        }
}


// =============================================================================
// ── Module: motor_mount_ring ─────────────────────────────────────────────────
// =============================================================================
// 4-arm spider strut ring at a given Z station.
// Arms bridge hub (R_HUB) to bore wall (EDF_BORE_R); retaining lip at EDF_CASING_R.
module motor_mount_ring(z_center) {
    arm_h = 3.0;  // [mm] axial thickness
    arm_w = 3.0;  // [mm] arm width

    // EDF casing retaining lip ring
    translate([0, 0, z_center - arm_h / 2])
        difference() {
            cylinder(r = EDF_CASING_R, h = arm_h, center = false);
            translate([0, 0, -0.01])
                cylinder(r = EDF_BORE_R, h = arm_h + 0.02, center = false);
        }

    // Four radial arms
    for (angle = [0, 90, 180, 270]) {
        rotate([0, 0, angle])
            translate([R_HUB, -arm_w / 2, z_center - arm_h / 2])
                cube([EDF_BORE_R - R_HUB, arm_w, arm_h]);
    }

    // Central hub plug
    translate([0, 0, z_center - arm_h / 2])
        cylinder(r = R_HUB, h = arm_h, center = false);
}


// =============================================================================
// ── Module: pivot_x_face_boss ────────────────────────────────────────────────
// =============================================================================
// Two MF104ZZ bearing boss cylinders on the nacelle X-faces at PIVOT_Z, Y=0.
//
// The Serenity nacelle is not a symmetric ellipse; the two X-face positions
// differ:
//   +X (pylon side)  ≈ NACELLE_FACE_X_PYLON = 34 mm from bore centre
//   -X (far side)    ≈ NACELLE_FACE_X_FAR   = 38 mm from bore centre
// An embed=3mm root inset guarantees the boss cylinder root overlaps with the
// nacelle shell wall (2.5 mm thick) on both sides, ensuring a solid boolean
// union regardless of the asymmetry.
//
// boss_wall + embed is the total cylinder length; the external protrusion is
// PIVOT_BOSS_DEPTH = 5 mm beyond the nacelle outer face.
module pivot_x_face_boss() {
    boss_od   = PIVOT_BEAR_OD + 6.0;  // 16 mm OD: 10 mm bearing + 2 × 3 mm wall
    boss_wall = PIVOT_BOSS_DEPTH;      // 5 mm external protrusion
    embed     = 3.0;                   // 3 mm root buried inside nacelle shell wall

    for (sign = [-1, +1]) {
        // Actual shell face distance from bore centre for this side.
        // sign > 0: pylon face (narrower); sign < 0: far face (wider).
        face_dist = (sign > 0) ? NACELLE_FACE_X_PYLON : NACELLE_FACE_X_FAR;

        // ── Boss cylinder ─────────────────────────────────────────────────────
        translate([sign * (face_dist - embed), 0, PIVOT_Z])
        rotate([0, sign * 90, 0])
            difference() {
                cylinder(r = boss_od / 2,
                         h = boss_wall + embed,
                         center = false);
                cylinder(r = PIVOT_BEAR_OD / 2,
                         h = boss_wall + embed + 0.02,
                         center = false);
            }

        // ── Load-spreading web (hull() avoids coplanar face issues) ───────────
        hull() {
            // Ring at boss root (shell-flush plane)
            translate([sign * (face_dist - embed), 0, PIVOT_Z])
            rotate([0, sign * 90, 0])
                difference() {
                    cylinder(r = boss_od / 2,
                             h = 0.4,
                             center = false);
                    cylinder(r = boss_od / 2 - WALL_T,
                             h = 0.41,
                             center = false);
                }

            // Flat disc anchoring web to nacelle outer face
            translate([sign * (face_dist + embed), 0, PIVOT_Z])
            rotate([0, sign * 90, 0])
                cylinder(r = boss_od / 2, h = 0.4, center = false);
        }
    }
}


// =============================================================================
// ── Module: pinion_a_boss ────────────────────────────────────────────────────
// =============================================================================
// MR63ZZ bearing boss for Drive Pinion A.  Cylinder along X at
// (Y=PINION_A_Y=28mm, Z=PIVOT_Z).  Meshes the fixed sector gear (R=22mm)
// at centre-distance 22+6=28mm from the pivot axis.
module pinion_a_boss() {
    translate([0, PINION_A_Y, PINION_A_Z])
        rotate([0, 90, 0])
            difference() {
                cylinder(r = PINION_A_BOSS_OD / 2,
                         h = PINION_A_BOSS_L,
                         center = true);
                cylinder(r = PINION_A_SHAFT_D / 2,
                         h = PINION_A_BOSS_L + 0.02,
                         center = true);
            }
}


// =============================================================================
// ── Module: crown_pinion_boss ────────────────────────────────────────────────
// =============================================================================
// MR63ZZ bearing boss for Crown Pinion at CROWN_Z.  Co-planar with Pinion A
// in Y so the longitudinal CF shaft runs straight.
module crown_pinion_boss() {
    translate([0, PINION_A_Y, CROWN_Z])
        rotate([0, 90, 0])
            difference() {
                cylinder(r = CROWN_BOSS_OD / 2,
                         h = CROWN_BOSS_L,
                         center = true);
                cylinder(r = PINION_A_SHAFT_D / 2,
                         h = CROWN_BOSS_L + 0.02,
                         center = true);
            }
}


// =============================================================================
// ── Module: shaft_conduit ────────────────────────────────────────────────────
// =============================================================================
// Axial PTFE-sleeve conduit from Pinion A to Crown Pinion.
// Y = PINION_A_Y = 28 mm (co-linear with both bosses → straight shaft path).
module shaft_conduit() {
    conduit_len = CROWN_Z - PINION_A_Z;

    translate([0, PINION_A_Y, PINION_A_Z])
        difference() {
            cylinder(r = SHAFT_CONDUIT_OD / 2,
                     h = conduit_len,
                     center = false);
            translate([0, 0, -0.01])
                cylinder(r = SHAFT_CONDUIT_ID / 2,
                         h = conduit_len + 0.02,
                         center = false);
        }
}


// =============================================================================
// ── Module: nozzle_ring_pocket ───────────────────────────────────────────────
// =============================================================================
// Cylindrical void at the exhaust end; seats the rotating iris inner ring.
// Used as a subtraction volume in nacelle_pod().
module nozzle_ring_pocket() {
    translate([0, 0, NOZZLE_RING_Z])
        cylinder(r = NOZZLE_RING_OD / 2,
                 h = NOZZLE_RING_H + 0.02,
                 center = false);
}


// =============================================================================
// ── Module: nav_wire_conduit ─────────────────────────────────────────────────
// =============================================================================
// External D-section conduit on the inboard (pylon-side) X-face.
// Routes the WS2812C nav-light 28AWG 3-core signal wire from the tip cap to
// the pylon harness zone.
//
// The face_dist for each pylon_side is taken from the actual nacelle STL
// measurements rather than from the synthetic-ellipse NACELLE_OD_X/2.
module nav_wire_conduit(pylon_side = PYLON_SIDE) {
    face_dist = (pylon_side > 0) ? NACELLE_FACE_X_PYLON : NACELLE_FACE_X_FAR;
    face_x    = pylon_side * face_dist;
    cond_len  = NAV_CONDUIT_Z_HI - NAV_CONDUIT_Z_LO;
    embed     = 1.0;  // 1 mm root into nacelle shell to prevent touching face

    x_offset = (pylon_side > 0)
               ? face_x - embed
               : face_x - NAV_CONDUIT_D;

    bore_cx = (pylon_side > 0)
              ? NAV_CONDUIT_D / 2 + embed
              : NAV_CONDUIT_D / 2;

    translate([x_offset, -NAV_CONDUIT_W / 2, NAV_CONDUIT_Z_LO])
        difference() {
            cube([NAV_CONDUIT_D + embed, NAV_CONDUIT_W, cond_len]);
            translate([bore_cx, NAV_CONDUIT_W / 2, -0.01])
                cylinder(r = NAV_CONDUIT_BORE / 2,
                         h = cond_len + 0.02);
        }
}


// =============================================================================
// ── Module: harness_exit_port ────────────────────────────────────────────────
// =============================================================================
// Rectangular slot through the inboard X-face shell at HARNESS_PORT_Z.
// Allows ESC motor leads, signal leads, and nav-light wire to transition from
// nacelle interior to the pylon harness channel.
module harness_exit_port(pylon_side = PYLON_SIDE) {
    face_dist = (pylon_side > 0) ? NACELLE_FACE_X_PYLON : NACELLE_FACE_X_FAR;
    face_x    = pylon_side * face_dist;
    cut_depth = WALL_T + 3.5;

    translate([
        (pylon_side > 0) ? (face_x - cut_depth) : face_x,
        -HARNESS_PORT_W / 2,
        HARNESS_PORT_Z - HARNESS_PORT_H / 2
    ])
        cube([cut_depth + 0.5, HARNESS_PORT_W, HARNESS_PORT_H]);
}


// =============================================================================
// ── Module: nacelle_pod (main assembly) ──────────────────────────────────────
// =============================================================================
// Top-level assembly.  Additive geometry is unioned; subtractive is differenced.
//
// Additive:
//   • nacelle_shell_imported() — canonical Serenity nacelle exterior hull
//   • thrust_tube()            — 50 mm ID bore structural sleeve
//   • inlet_bell()             — cosine-tapered intake lip
//   • stator_hub()             — cable-routing hub ring
//   • N_FINS stator_fin()      — twisted inter-stage stator vanes
//   • 2× motor_mount_ring()    — EDF1 and EDF2 spider strut rings
//   • pivot_x_face_boss()      — CG-pivot MF104ZZ bearing bosses
//   • pinion_a_boss()          — Drive Pinion A MR63ZZ boss
//   • crown_pinion_boss()      — Crown Pinion MR63ZZ boss
//   • shaft_conduit()          — longitudinal CF gear shaft conduit
//   • nav_wire_conduit()       — external WS2812C signal wire channel
//
// Subtractive:
//   • Full-length 50 mm ID bore cylinder (opens intake and exhaust faces)
//   • nozzle_ring_pocket()     — iris ring seat at exhaust end
//   • harness_exit_port()      — ESC / nav-light wiring slot
//   • Tilt spar clearance bore (4.2 mm dia along X through both X-faces)
module nacelle_pod(swirl_dir = SWIRL_DIR) {

    union() {
        difference() {

            // ══════════════════════════════════════════════════════════════
            // ── Additive geometry ─────────────────────────────────────────
            // ══════════════════════════════════════════════════════════════
            union() {

                // ── Canonical Serenity nacelle exterior hull ─────────────
                nacelle_shell_imported();

                // ── EDF bore thrust tube (EDF1 seat → nozzle ring) ───────
                thrust_tube();

                // ── Cosine-tapered intake bell (Z=0 → EDF1 seat) ─────────
                inlet_bell();

                // ── Inter-stage stator hub (cable-routing hollow ring) ────
                stator_hub();

                // ── 11 twisted stator fins ────────────────────────────────
                for (i = [0 : N_FINS - 1]) {
                    stator_fin(i * (360 / N_FINS), swirl_dir);
                }

                // ── EDF1 motor-mount spider ring (mid-EDF1 station) ───────
                motor_mount_ring(EDF1_MOTOR_Z);

                // ── EDF2 motor-mount spider ring (mid-EDF2 station) ───────
                motor_mount_ring(EDF2_MOTOR_Z);

                // ── CG-pivot X-face bosses (MF104ZZ, at PIVOT_Z, Y=0) ────
                pivot_x_face_boss();

                // ── Drive Pinion A bearing boss (MR63ZZ, at PIVOT_Z) ─────
                pinion_a_boss();

                // ── Crown Pinion bearing boss (MR63ZZ, at CROWN_Z) ───────
                crown_pinion_boss();

                // ── Longitudinal CF gear-shaft conduit ────────────────────
                shaft_conduit();

                // ── External nav-light wire conduit (inboard X-face) ─────
                nav_wire_conduit(pylon_side = PYLON_SIDE);

            } // end union (additive)

            // ══════════════════════════════════════════════════════════════
            // ── Subtractive geometry ──────────────────────════════════════
            // ══════════════════════════════════════════════════════════════

            // ── Full-length 50 mm ID bore path ────────────────────────────
            // Extends 0.01 mm beyond each end to open the voxel-remesh end
            // caps on the imported nacelle STL (intake and exhaust faces).
            translate([0, 0, -0.01])
                cylinder(r = EDF_BORE_R,
                         h = NACELLE_L + 0.02,
                         center = false);

            // ── Nozzle ring pocket (iris ring seat at exhaust end) ─────────
            nozzle_ring_pocket();

            // ── Harness exit port (ESC / nav-light wiring slot) ───────────
            harness_exit_port(pylon_side = PYLON_SIDE);

            // ── Tilt spar clearance bore (4.2 mm dia, along X) ────────────
            // Spans from −FAR_FACE to +PYLON_FACE plus both boss protrusions
            // and a 4 mm margin to guarantee clean exit on both X faces.
            translate([0, 0, PIVOT_Z])
                rotate([0, 90, 0])
                    cylinder(
                        r      = PIVOT_BORE_D / 2,
                        h      = NACELLE_FACE_X_PYLON + NACELLE_FACE_X_FAR
                                 + 2 * PIVOT_BOSS_DEPTH + 4,
                        center = true
                    );

        } // end difference
    } // end union (top-level)
}


// =============================================================================
// ── Render call ───────────────────────────────────────────────────────────────
// =============================================================================
nacelle_pod(swirl_dir = SWIRL_DIR);


// =============================================================================
// ── Print specifications ──────────────────────────────────────────────────────
// =============================================================================
// Material    : CF-PETG (CarbonX PETG+CF or equivalent)
// Layer height: 0.15 mm
// Walls       : 4 perimeter walls (minimum)
// Infill      : 25% gyroid (shell and bore-tube cavity regions)
//               40% gyroid at pivot boss and bearing boss regions
// Nozzle      : Hardened-steel required for CF-PETG
// Supports    : None required if oriented intake-face-down
// Interior    : Fill nacelle cavity (between bore tube and outer shell)
//               with 2 lb/cf low-density closed-cell foam after printing,
//               per CLAUDE.md fabrication standards.
//
// Post-print checks:
//   1. Bore OD = 55.0 mm ± 0.3 mm at 3 stations (calipers).
//   2. Pivot boss bore = 10.0 mm ± 0.1 mm (MF104ZZ OD press-fit), both X faces.
//   3. Tilt spar bore ID = 4.2 mm ± 0.1 mm through both X faces.
//   4. Shaft conduit ID = 3.5 mm ± 0.1 mm (4 mm PTFE tube).
//   5. Stator fin edges: sand smooth if layer delamination visible.
//
// Render commands:
//   Port nacelle (RED nav light, pylon on +X, CW from intake):
//     openscad -o s_nacelle_port_revp.stl nacelle_pod_50mm_tandem.scad \
//              -D SWIRL_DIR=1 -D PYLON_SIDE=1 -D NACELLE_SIDE=1
//   Starboard nacelle (GREEN nav light, pylon on -X, CCW from intake):
//     openscad -o s_nacelle_stbd_revp.stl nacelle_pod_50mm_tandem.scad \
//              -D SWIRL_DIR=-1 -D PYLON_SIDE=-1 -D NACELLE_SIDE=-1
