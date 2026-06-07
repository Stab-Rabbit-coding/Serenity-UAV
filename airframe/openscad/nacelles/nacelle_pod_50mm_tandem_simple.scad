// =============================================================================
// nacelle_pod_50mm_tandem_simple.scad
// Serenity UAV — Rev T2 — Tandem-EDF Nacelle Pod, Simplified (screw-on nozzle)
// =============================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-06-07
// Revision: Rev T2 (2026-06-07)
//
// Derivation
// ----------
// Derived from nacelle_pod_50mm_tandem.scad Rev T (2026-05-29).
// This variant removes the passive gear-driven variable-diameter iris nozzle
// and all supporting gear-train nacelle features.  The sleeve architecture and
// all EDF mounting features are unchanged.
//
// Changes from Rev T (Rev T1 — 2026-06-07):
//   REMOVED — pinion_a_boss()      MR63ZZ boss for Drive Pinion A at PIVOT_Z
//   REMOVED — crown_pinion_boss()  MR63ZZ boss for Crown Pinion at NOZZLE_RING_Z
//   REMOVED — shaft_conduit()      Longitudinal CF gear-shaft PTFE-sleeve conduit
//   REMOVED — nozzle_ring_pocket() Cylindrical bore pocket for iris inner ring seat
//   REMOVED — Gear mount parameter block (PINION_A_*, CROWN_*, SHAFT_CONDUIT_*)
//   RETAINED — NOZZLE_RING_Z (AFT_SLV_Z_END and sleeve_retention_bosses() ref)
//   RETAINED — All sleeve architecture (bore zones, key slots, retention bosses)
//   RETAINED — EDF1 nacelle-integrated spider and all other nacelle features
//
// Changes from Rev T1 (Rev T2 — 2026-06-07):
//   ADDED — nozzle_access_pocket() Bore Z = 166.25 … 186.25 mm at r = 32.5 mm;
//            exposes 3× sleeve retention screws (SLEEVE_BOSS_R = 28 mm) when
//            housing is removed for EDF/rotor bench maintenance.
//   ADDED — nozzle_push_boss()     Smooth push-on exit boss (OD = 60 mm,
//            ID = 50 mm, H = 12 mm) protruding aft from nacelle exit face;
//            base collar anchors boss to nacelle exit annular face.
//            3× M3 set-screw flats at 0°/120°/240° engage housing set screws.
//   ADDED — NOZZLE_ACCESS_*, NOZZLE_BOSS_*, NOZZLE_FLAT_* parameter blocks.
//
// Sleeve removability
// -------------------
// Maintenance sequence:
//   1. Loosen 3× M3 set screws in housing skirt (2.5 mm hex key).
//   2. Pull housing off push-on boss.
//   3. 3× M3×20 SHCS sleeve retention screws now accessible at SLEEVE_BOSS_R
//      = 28 mm radius through the access pocket bore.
//   4. Remove aft spider sleeve (edf_aft_spider_sleeve.scad).
//   5. Slide out stator sleeve (edf_stator_sleeve.scad).
//   6. Service EDF1/EDF2 motors and fan rotors.
//   7. Reinstall in reverse; push housing onto boss, drive set screws.
//
// Nozzle pairing
// --------------
// This nacelle mates with nacelle_nozzle_straight.scad (Rev T2):
//   • Push-on housing (skirt bore Ø 60.25 mm slides over Ø 60 mm boss)
//   • 50 mm airflow bore maintained through housing
//   • 8 decorative imitation petals — same shape as REVT iris, non-functional
//   • 3× M3 set screws in housing skirt engage boss OD flats at 0°/120°/240°
//
// Sleeves (unchanged from Rev T)
// --------------------------------
// The keyed sleeve architecture from Rev T is fully retained:
//   edf_stator_sleeve.scad    — inter-stage stator + 11 fins, Z = 90 … 122.5 mm
//   edf_aft_spider_sleeve.scad — EDF2 motor-mount spider, Z = 122.5 … 166.25 mm
// Both sleeves use 3× OD keys at 0°/120°/240° engaging bore_key_slots().
// Retention: 3× M3 SHCS at sleeve_retention_bosses() on nozzle pocket face.
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
// Features (all parametric)
// -------------------------
//   • Cosine-tapered inlet bell  (Z=0 … EDF1_Z_ENTRY)
//   • EDF1 seat and 3-arm motor-mount spider      (forward EDF, upstream)
//   • 11-fin twisted inter-stage stator  (EDF1 exit … EDF2 entry) — sleeve
//   • EDF2 seat and motor-mount spider             (aft EDF, downstream) — sleeve
//   • CG-aligned pivot X-face boss (two MF104ZZ bearing bosses at PIVOT_Z)
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
//
// References
// ----------
//   [1] Xfly Galaxy X5 50mm 6S EDF datasheet (Xfly Model, 2024).
//   [2] MF104ZZ bearing spec: ID=4mm, OD=10mm, W=4mm (IKO / NMB catalog).
//   [3] OpenSCAD language reference, v2021.01 <https://openscad.org>.
//   [4] Serenity-UAV project CLAUDE.md — fabrication standards (2026).
//   [5] Thingiverse Thing 14474 — "Firefly Serenity Replica" by Dutchmogul.
//       Hull scaled 1.25× from 24″ target; voxel-repaired for CGAL booleans.
//   [6] nacelle_pod_50mm_tandem.scad Rev T — parent design (gear train version).
//   [7] nacelle_nozzle_straight.scad Rev T1 — mating straight nozzle with
//       decorative fixed petals replacing the REVT iris nozzle assembly.
//
// Usage
// -----
//   Port nacelle (CW, pylon on +X face):
//     openscad -o s_nacelle_port_simple_revt1.stl \
//              nacelle_pod_50mm_tandem_simple.scad \
//              -D SWIRL_DIR=1 -D PYLON_SIDE=1 -D NACELLE_SIDE=1
//
//   Starboard nacelle (CCW, pylon on -X face):
//     openscad -o s_nacelle_stbd_simple_revt1.stl \
//              nacelle_pod_50mm_tandem_simple.scad \
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
// Measured from the repaired STL bounding box; provided for reference only.
NACELLE_OD_X    =  75.4;  // [mm] nacelle bounding-box width, spanwise (X)
NACELLE_OD_Y    =  83.3;  // [mm] nacelle bounding-box depth, fore-aft  (Y)

// ── X-face positions at the pivot station (Z ≈ PIVOT_Z, Y ≈ 0) ───────────────
// Measured from the centered-bore repaired STL at Z=103.75mm, Y<5mm.
// The Serenity nacelle is NOT a symmetric ellipse — pylon-attachment features
// make the pylon-side face narrower (+34mm) than the far side (-38mm).
NACELLE_FACE_X_PYLON = 34.0;  // [mm] pylon-side X face from bore centre
NACELLE_FACE_X_FAR   = 38.0;  // [mm] far-side   X face from bore centre

// ── STL bore-centre offsets (Blender world space, repaired STLs) ─────────────
// Translate each nacelle so its EDF bore axis lands on the SCAD Z axis.
BORE_CX_L = 42.72;   // [mm] left  (port) nacelle bore X in STL space
BORE_CX_R = 155.02;  // [mm] right (stbd) nacelle bore X in STL space
BORE_CY   = 190.79;  // [mm] bore Y offset (both nacelles; translate adds +190.79)

// ── Nacelle side selector ─────────────────────────────────────────────────────
// +1 = port (left) nacelle, imports s_eng_left_shell24_50mm_repaired.stl
// -1 = stbd (right) nacelle, imports s_eng_right_shell24_50mm_repaired.stl
// Override at command line: -D NACELLE_SIDE=-1
NACELLE_SIDE    = +1;

// ── EDF seat positions (1.25× scale) ─────────────────────────────────────────
// EDF1 = upstream (intake-side) EDF.  EDF2 = downstream (exhaust-side) EDF.
EDF1_Z_ENTRY    =  27.5;  // [mm] EDF1 forward face
EDF1_Z_EXIT     =  90.0;  // [mm] EDF1 aft face
EDF2_Z_ENTRY    = 122.5;  // [mm] EDF2 forward face
EDF2_Z_EXIT     = 178.8;  // [mm] EDF2 aft face

// ── EDF motor-mount spider geometry ──────────────────────────────────────────
// Shared by nacelle-integrated EDF1 spider and aft sleeve EDF2 spider.
SPIDER_ARM_H    =   8.0;   // [mm] arm axial thickness
SPIDER_ARM_W    =   6.0;   // [mm] arm tangential width
MOTOR_BOLT_R    =  10.0;   // [mm] M3 bolt circle radius — VERIFY vs actual motor
M3_INSERT_D     =   3.5;   // [mm] M3 × 6 mm OLF brass heat-set insert OD
M3_INSERT_L     =   6.0;   // [mm] heat-set insert depth
M3_CLEAR_D      =   3.3;   // [mm] M3 clearance bore diameter
R_HUB           =   8.0;   // [mm] spider hub outer radius (16 mm OD)
R_HUB_BORE      =   2.0;   // [mm] spider hub bore radius  ( 4 mm ID)

// ── Inter-stage stator geometry (from sleeve files; used for EDF1_SPIDER_Z) ──
STATOR_Z_BOT    =  93.75;  // [mm] stator bottom Z
STATOR_Z_TOP    = 118.75;  // [mm] stator top Z

// ── EDF1 spider position (nacelle-integrated, just forward of stators) ─────────
// 2 mm axial gap between EDF1 spider aft face and stator fin leading edge.
EDF1_SPIDER_Z   = STATOR_Z_BOT - SPIDER_ARM_H / 2 - 2.0;  // = 87.75 mm

// ── EDF2 spider position (in aft spider sleeve) ───────────────────────────────
EDF2_SPIDER_Z   = 148.0;   // [mm] EDF2 spider centre, nacelle-local Z

// ── Nozzle interface (push-on boss) ──────────────────────────────────────────
// NOZZLE_RING_Z is retained: AFT_SLV_Z_END and sleeve_retention_bosses() ref.
// nozzle_access_pocket() (Zone B) enlarges bore from NOZZLE_RING_Z aft to
// expose 3× sleeve retention screws at SLEEVE_BOSS_R = 28 mm when housing is
// removed.  nozzle_push_boss() (Zone C) adds the smooth push-on exit boss that
// the housing skirt registers over; 3× M3 set screws in housing skirt lock into
// shallow flats on boss OD.
NOZZLE_RING_Z      = 166.25;  // [mm] aft boundary of sleeve zone; sleeve boss Z ref
NOZZLE_ACCESS_OD   =  65.0;   // [mm] access pocket bore OD (clears boss OD + margin)
NOZZLE_ACCESS_H    =  20.0;   // [mm] pocket axial depth aft of NOZZLE_RING_Z
NOZZLE_BOSS_OD     =  60.0;   // [mm] push-on exit boss nominal OD (smooth, no thread)
NOZZLE_BOSS_H      =  12.0;   // [mm] boss protrusion aft of nacelle exit face
NOZZLE_COLLAR_OD   =  64.0;   // [mm] base collar OD (boss OD + 4 mm nacelle overlap)
NOZZLE_COLLAR_H    =   3.0;   // [mm] base collar axial height at nacelle exit face
NOZZLE_FLAT_DEPTH  =   0.75;  // [mm] M3 set-screw flat radial depth on boss OD
NOZZLE_FLAT_W      =   5.0;   // [mm] set-screw flat width (circumferential + axial)

// ── Two-sleeve bore zone ──────────────────────────────────────────────────────
// edf_stator_sleeve.scad    : Z = STATOR_SLV_Z_START … STATOR_SLV_Z_END
// edf_aft_spider_sleeve.scad: Z = AFT_SLV_Z_START    … AFT_SLV_Z_END
// Both sleeves OD = EDF_CASING_R = 27.5 mm; nacelle bore enlarged to
// SLEEVE_BORE_R = 27.7 mm for 0.2 mm/side clearance fit.
STATOR_SLV_Z_START = EDF1_Z_EXIT;    // = 90.0  mm
STATOR_SLV_Z_END   = EDF2_Z_ENTRY;   // = 122.5 mm
AFT_SLV_Z_START    = EDF2_Z_ENTRY;   // = 122.5 mm
AFT_SLV_Z_END      = NOZZLE_RING_Z;  // = 166.25 mm
SLEEVE_BORE_R   = EDF_CASING_R + 0.2;  // [mm] = 27.7 mm

// ── Sleeve key geometry ───────────────────────────────────────────────────────
// 3× longitudinal keys at 0°, 120°, 240° on each sleeve OD (keys protrude
// radially outward).  Matching slots in nacelle bore wall prevent rotation under
// EDF torque and ensure repeatable orientation for wire routing and assembly.
SLEEVE_KEY_W      =   3.0;  // [mm] key width  (tangential / circumferential)
SLEEVE_KEY_H      =   3.0;  // [mm] key height (radial protrusion above sleeve OD)
SLEEVE_KEY_SLOT_W = SLEEVE_KEY_W + 0.3;   // [mm] nacelle bore slot width (clearance)
SLEEVE_KEY_SLOT_H = SLEEVE_KEY_H + 0.3;   // [mm] nacelle bore slot depth (clearance)

// ── ESC wire exit slot ────────────────────────────────────────────────────────
// Rectangular slot through forward thrust tube bore wall at Z ≈ ESC_SLOT_Z.
// Routes EDF1 ESC motor leads and signal wire from bore to nacelle cavity.
ESC_SLOT_W  =  14.0;  // [mm] slot circumferential width
ESC_SLOT_H  =   8.0;  // [mm] slot axial height
ESC_SLOT_Z  = STATOR_SLV_Z_START - ESC_SLOT_H / 2;  // = 86.0 mm (slot bottom Z)

// ── Sleeve retention boss geometry ────────────────────────────────────────────
// 3× M3 × 6 mm OLF insert bosses at NOZZLE_RING_Z, r = SLEEVE_BOSS_R, 120°.
SLEEVE_BOSS_R   =  28.0;  // [mm] boss centre radius
SLEEVE_BOSS_OD  =   7.0;  // [mm] boss OD (M3 insert 3.5 mm OD + 2 × 1.75 mm wall)
SLEEVE_BOSS_L   =   6.0;  // [mm] boss protrusion into pocket (= insert depth)

SWIRL_DIR       =  +1;    // [+1 / -1] default port nacelle CW from intake

// ── CG-derived tilt pivot (1.25× scale) ──────────────────────────────────────
// Pivot at nacelle CG eliminates gravity-induced servo torque.
PIVOT_Z         = 103.75;  // [mm] pivot axial centre = nacelle CG station

// MF104ZZ flanged bearing: ID=4mm, OD=10mm, width=4mm.
PIVOT_BORE_D    =   4.2;   // [mm] pivot rod clearance bore (4mm CF rod + 0.2mm)
PIVOT_BEAR_OD   =  10.0;   // [mm] MF104ZZ bearing OD (press-fit)
PIVOT_BOSS_DEPTH =   5.0;  // [mm] boss protrusion depth beyond nacelle X-face
CLEVIS_EAR_T    =   5.0;   // [mm] retained for compatibility
CLEVIS_SLOT_W   =  16.0;   // [mm] gap between nacelle X faces
CLEVIS_EAR_OD   =  16.0;   // [mm] boss cylinder OD

// NOTE: Gear mount parameter block (PINION_A_*, CROWN_*, SHAFT_CONDUIT_*)
// is removed in this simplified variant.  Those parameters drove features
// that only exist on the REVT gear-train nacelle (nacelle_pod_50mm_tandem.scad).

// ── Inlet bell (1.25× scale) ──────────────────────────────────────────────────
INLET_BELL_L    =  27.5;   // [mm] inlet bell axial length
INLET_BELL_FLARE=   3.0;   // [mm] extra flare radius at intake lip

// ── Navigation light wiring and harness exit (1.25× scale Z values) ──────────
PYLON_SIDE      = +1;      // [+1 / -1] inboard face: +1=port, -1=stbd
NAV_CONDUIT_BORE =  4.0;   // [mm] inner bore ID
NAV_CONDUIT_W    =  8.0;   // [mm] conduit outer width in Y
NAV_CONDUIT_D    =  5.0;   // [mm] conduit depth in X
NAV_CONDUIT_Z_LO =  2.5;   // [mm] conduit start Z
NAV_CONDUIT_Z_HI = PIVOT_Z - PIVOT_BOSS_DEPTH - 1.0;
                            // [mm] conduit end Z: stops 1 mm below pivot boss root

HARNESS_PORT_W   = 14.0;   // [mm] slot width in Y
HARNESS_PORT_H   =   8.0;  // [mm] slot height in Z
HARNESS_PORT_Z   = 107.5;  // [mm] slot centre Z

// ── Global facet resolution ───────────────────────────────────────────────────
$fn = 72;


// =============================================================================
// ── Module: nacelle_shell_imported ───────────────────────────────────────────
// =============================================================================
// Imports the voxel-repaired Serenity nacelle STL and centres its bore on the
// SCAD origin.
//
// Port (left) nacelle : s_eng_left_shell24_50mm_repaired.stl, bore at BORE_CX_L
// Stbd (right) nacelle: s_eng_right_shell24_50mm_repaired.stl, bore at BORE_CX_R
module nacelle_shell_imported() {
    if (NACELLE_SIDE > 0) {
        // ── Port (left) nacelle ───────────────────────────────────────────────
        translate([-BORE_CX_L, BORE_CY, 0])
            import("../../stls/nacelles/s_eng_left_shell24_50mm_repaired.stl",
                   convexity = 4);
    } else {
        // ── Starboard (right) nacelle ─────────────────────────────────────────
        translate([-BORE_CX_R, BORE_CY, 0])
            import("../../stls/nacelles/s_eng_right_shell24_50mm_repaired.stl",
                   convexity = 4);
    }
}


// =============================================================================
// ── Module: thrust_tube ──────────────────────────────────────────────────────
// =============================================================================
// Forward bore tube from EDF1_Z_ENTRY to STATOR_SLV_Z_START (Z = 27.5 … 90 mm).
// OD = EDF_CASING_R (27.5 mm), ID = EDF_BORE_R (25 mm); 2.5 mm wall.
// Provides structural bore wall for the integral nacelle section housing EDF1.
module thrust_tube() {
    tube_len = STATOR_SLV_Z_START - EDF1_Z_ENTRY;  // = 62.5 mm
    translate([0, 0, EDF1_Z_ENTRY])
        difference() {
            cylinder(r = EDF_CASING_R,
                     h = tube_len,
                     center = false);
            translate([0, 0, -0.01])
                cylinder(r = EDF_BORE_R,
                         h = tube_len + 0.02,
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
// ── Module: sleeve_retention_bosses ─────────────────────────────────────────
// =============================================================================
// 3× M3 × 6 mm OLF heat-set insert boss cylinders on the nozzle ring pocket
// step face (Z = NOZZLE_RING_Z).  The EDF aft spider sleeve aft flange seats
// against this Z face; 3× M3 SHCS from nozzle bore end thread into these bosses.
//
// Boss geometry:
//   Centre radius   : SLEEVE_BOSS_R = 28 mm from bore axis
//   Boss OD         : SLEEVE_BOSS_OD = 7 mm
//   Boss protrusion : SLEEVE_BOSS_L = 6 mm aft (Z_RING … Z_RING+6)
module sleeve_retention_bosses() {
    for (angle = [0, 120, 240]) {
        rotate([0, 0, angle])
        translate([SLEEVE_BOSS_R, 0, NOZZLE_RING_Z])
            difference() {
                cylinder(r = SLEEVE_BOSS_OD / 2,
                         h = SLEEVE_BOSS_L,
                         center = false);
                // M3 heat-set insert bore (blind, opening toward nozzle end)
                translate([0, 0, -0.01])
                    cylinder(r = M3_INSERT_D / 2,
                             h = M3_INSERT_L + 0.01,
                             center = false);
            }
    }
}


// =============================================================================
// ── Module: edf1_nacelle_spider ──────────────────────────────────────────────
// =============================================================================
// EDF1 motor-mount spider integrated into the nacelle (Zone C).
// Axial position: EDF1_SPIDER_Z = 87.75 mm (just forward of stator zone).
//
// Motor mounting (EDF1):
//   • Motor slides in from nozzle end; back plate seats against spider aft face.
//   • Motor shaft extends FORWARD through hub bore (Ø4 mm) to rotor1.
//   • 3× M3 SHCS from INTAKE bore end pass through clearance bores in spider
//     arms and thread into motor's own M3 female back-plate holes.
//   • T-handle 2.5 mm hex key required; reach ≈ EDF1_SPIDER_Z ≈ 88 mm.
module edf1_nacelle_spider() {
    arm_h = SPIDER_ARM_H;
    arm_w = SPIDER_ARM_W;
    z_ctr = EDF1_SPIDER_Z;

    for (angle = [0, 120, 240]) {
        rotate([0, 0, angle])
        difference() {
            // Arm solid — ±1 mm overrun for CGAL volumetric overlap
            translate([R_HUB - 1, -arm_w / 2, z_ctr - arm_h / 2])
                cube([EDF_BORE_R - R_HUB + 2, arm_w, arm_h]);
            // M3 clearance bore: screw head on intake face; exits into motor
            translate([MOTOR_BOLT_R, 0, z_ctr - arm_h / 2 - 0.01])
                cylinder(r = M3_CLEAR_D / 2,
                         h = arm_h + 0.02,
                         center = false);
        }
    }

    // Hub ring — OD = 2 × R_HUB (16 mm), bore = 2 × R_HUB_BORE (4 mm)
    translate([0, 0, z_ctr - arm_h / 2])
        difference() {
            cylinder(r = R_HUB,      h = arm_h, center = false);
            translate([0, 0, -0.01])
                cylinder(r = R_HUB_BORE, h = arm_h + 0.02, center = false);
        }
}


// =============================================================================
// ── Module: esc_wire_exit_slot ────────────────────────────────────────────────
// =============================================================================
// Rectangular slot through the forward thrust tube bore wall at Z ≈ ESC_SLOT_Z.
// Routes EDF1 ESC motor leads radially outward from bore to nacelle cavity,
// then forward to the pylon harness exit port.
module esc_wire_exit_slot(pylon_side = PYLON_SIDE) {
    cut_depth = (EDF_CASING_R - EDF_BORE_R) + 3.0;  // through wall + 3 mm into cavity

    translate([
        pylon_side > 0 ? EDF_BORE_R - 0.01 : -(EDF_BORE_R + cut_depth),
        -ESC_SLOT_W / 2,
        ESC_SLOT_Z
    ])
        cube([cut_depth + 0.01, ESC_SLOT_W, ESC_SLOT_H]);
}


// =============================================================================
// ── Module: bore_key_slots ────────────────────────────────────────────────────
// =============================================================================
// 3× longitudinal rectangular slots in the nacelle enlarged bore wall spanning
// the full sleeve zone (STATOR_SLV_Z_START → AFT_SLV_Z_END).
// Match the 3× keys on both stator sleeve and aft spider sleeve OD.
// Used as Zone B subtractions.
module bore_key_slots() {
    slot_len = AFT_SLV_Z_END - STATOR_SLV_Z_START;
    for (angle = [0, 120, 240]) {
        rotate([0, 0, angle])
        translate([SLEEVE_BORE_R - 0.01, -SLEEVE_KEY_SLOT_W / 2, STATOR_SLV_Z_START])
            cube([SLEEVE_KEY_SLOT_H + 1.0, SLEEVE_KEY_SLOT_W, slot_len]);
    }
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
// embed=3mm root guarantees boss cylinder root overlaps nacelle shell wall.
module pivot_x_face_boss() {
    boss_od   = PIVOT_BEAR_OD + 6.0;  // 16 mm OD: 10 mm bearing + 2 × 3 mm wall
    boss_wall = PIVOT_BOSS_DEPTH;      // 5 mm external protrusion
    embed     = 3.0;                   // 3 mm root buried inside nacelle shell wall

    for (sign = [-1, +1]) {
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

        // ── Load-spreading web ────────────────────────────────────────────────
        hull() {
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

            translate([sign * (face_dist + embed), 0, PIVOT_Z])
            rotate([0, sign * 90, 0])
                cylinder(r = boss_od / 2, h = 0.4, center = false);
        }
    }
}


// =============================================================================
// ── Module: nav_wire_conduit ─────────────────────────────────────────────────
// =============================================================================
// External D-section conduit on the inboard (pylon-side) X-face.
// Routes the WS2812C nav-light 28AWG 3-core signal wire.
module nav_wire_conduit(pylon_side = PYLON_SIDE) {
    face_dist = (pylon_side > 0) ? NACELLE_FACE_X_PYLON : NACELLE_FACE_X_FAR;
    face_x    = pylon_side * face_dist;
    cond_len  = NAV_CONDUIT_Z_HI - NAV_CONDUIT_Z_LO;
    embed     = 1.0;  // 1 mm root into nacelle shell

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
// ── Module: nozzle_access_pocket ─────────────────────────────────────────────
// =============================================================================
// Zone B subtraction: bore from NOZZLE_RING_Z aftward at r = NOZZLE_ACCESS_OD/2.
// Exposes the 3× sleeve retention screws (at SLEEVE_BOSS_R = 28 mm) after the
// nozzle housing is removed.  Boss collar (Zone C) registers in this pocket lip.
module nozzle_access_pocket() {
    translate([0, 0, NOZZLE_RING_Z])
        cylinder(r = NOZZLE_ACCESS_OD / 2,
                 h = NOZZLE_ACCESS_H,
                 center = false);
}


// =============================================================================
// ── Module: nozzle_push_boss ──────────────────────────────────────────────────
// =============================================================================
// Zone C addition: smooth push-on exit boss ring protrudes aft from nacelle
// exit face.  Housing skirt bore (60.25 mm) slides over boss to shoulder stop
// at boss aft face; 3× M3 set screws in housing skirt lock into the three
// flats machined into boss OD.
//
// Geometry:
//   Base collar: OD = NOZZLE_COLLAR_OD (64 mm), anchors boss to nacelle face.
//                Height = NOZZLE_COLLAR_H (3 mm); sits inside nacelle exit annulus.
//   Boss ring  : OD = NOZZLE_BOSS_OD (60 mm), ID = EDF bore (50 mm),
//                protrudes NOZZLE_BOSS_H (12 mm) aft of nacelle exit face.
//   Set-screw flats: 3× shallow flats on boss OD at 0°/120°/240°.
//                    Depth = NOZZLE_FLAT_DEPTH (0.75 mm), W × H = 5 × 5 mm.
//                    Centred at boss mid-height (NACELLE_L + NOZZLE_BOSS_H/2).
//
// Thread: NONE — push-on smooth bore.  Housing is retained by 3× M3 set screws
// through housing skirt into these flats.
module nozzle_push_boss() {
    union() {

        // ── Base collar (spans exit annulus, anchors boss to nacelle face) ──
        translate([0, 0, NACELLE_L - NOZZLE_COLLAR_H])
            difference() {
                cylinder(r = NOZZLE_COLLAR_OD / 2,
                         h = NOZZLE_COLLAR_H,
                         center = false);
                translate([0, 0, -0.01])
                    cylinder(r = EDF_BORE_R,
                             h = NOZZLE_COLLAR_H + 0.02,
                             center = false);
            }

        // ── Boss ring (protrudes aft; housing skirt registers over this) ────
        translate([0, 0, NACELLE_L])
            difference() {
                cylinder(r = NOZZLE_BOSS_OD / 2,
                         h = NOZZLE_BOSS_H,
                         center = false);
                // EDF airflow bore
                translate([0, 0, -0.01])
                    cylinder(r = EDF_BORE_R,
                             h = NOZZLE_BOSS_H + 0.02,
                             center = false);
                // 3× M3 set-screw engagement flats at 0°/120°/240°
                for (angle = [0, 120, 240]) {
                    rotate([0, 0, angle])
                        translate([NOZZLE_BOSS_OD / 2 - NOZZLE_FLAT_DEPTH,
                                   -NOZZLE_FLAT_W / 2,
                                   NOZZLE_BOSS_H / 2 - NOZZLE_FLAT_W / 2])
                            cube([NOZZLE_FLAT_DEPTH + 0.1,
                                  NOZZLE_FLAT_W,
                                  NOZZLE_FLAT_W + 0.1]);
                }
            }

    }
}


// =============================================================================
// ── Module: nacelle_pod (main assembly) ──────────────────────────────────────
// =============================================================================
// Top-level assembly.  Geometry is organised into three zones:
//
// Zone A — inside difference() additive union (survive bore subtraction, r > 25):
//   • nacelle_shell_imported() — canonical Serenity nacelle exterior hull
//   • thrust_tube()            — forward bore wall, Z = 27.5 … 90 mm
//   • inlet_bell()             — cosine-tapered intake lip
//   • pivot_x_face_boss()      — CG-pivot MF104ZZ bearing bosses
//   • nav_wire_conduit()       — external WS2812C signal wire channel
//   NOTE: pinion_a_boss(), crown_pinion_boss(), and shaft_conduit() removed
//         (gear train not present in this simplified variant).
//
// Zone B — subtracted by difference():
//   • Full-length 50 mm ID bore (opens intake and exhaust end caps)
//   • Sleeve zone bore: r = SLEEVE_BORE_R (27.7 mm), Z = 90 mm … 166.25 mm
//   • bore_key_slots()         — 3× longitudinal anti-rotation key slots
//   • esc_wire_exit_slot()     — EDF1 ESC wire exit at Z ≈ 86 mm
//   • harness_exit_port()      — ESC / nav-light wiring slot
//   • Tilt spar clearance bore (4.2 mm dia along X through both X-faces)
//   • nozzle_access_pocket()   — r = 32.5 mm pocket from NOZZLE_RING_Z aft;
//                                exposes sleeve retention screws when housing off
//
// Zone C — outer union() AFTER difference():
//   • edf1_nacelle_spider()     — EDF1 spider at Z = 87.75 mm
//   • sleeve_retention_bosses() — 3× M3 insert bosses on nozzle pocket face
//   • nozzle_push_boss()        — smooth push-on exit boss, OD = 60 mm, H = 12 mm
module nacelle_pod(swirl_dir = SWIRL_DIR) {

    union() {

        // ── Zone A + Zone B ──────────────────────────────────────────────────
        difference() {

            // ══════════════════════════════════════════════════════════════
            // Zone A — additive geometry (r > EDF_BORE_R or exterior shell)
            // ══════════════════════════════════════════════════════════════
            union() {

                // ── Canonical Serenity nacelle exterior hull ─────────────
                nacelle_shell_imported();

                // ── Forward bore tube (Z = 27.5 … 90 mm) ─────────────────
                // Structural bore wall for integral EDF1 section.
                thrust_tube();

                // ── Cosine-tapered intake bell (Z=0 → EDF1 seat) ─────────
                inlet_bell();

                // ── CG-pivot X-face bosses (MF104ZZ, at PIVOT_Z, Y=0) ────
                pivot_x_face_boss();

                // ── External nav-light wire conduit (inboard X-face) ─────
                nav_wire_conduit(pylon_side = PYLON_SIDE);

                // NOTE: pinion_a_boss() removed — no Drive Pinion A
                // NOTE: crown_pinion_boss() removed — no Crown Pinion
                // NOTE: shaft_conduit() removed — no longitudinal gear shaft

            } // end union (Zone A additive)

            // ══════════════════════════════════════════════════════════════
            // Zone B — subtractive geometry
            // ══════════════════════════════════════════════════════════════

            // ── Full-length 50 mm ID bore path ────────────────────────────
            // Extends 0.01 mm past each end to open voxel-remesh end caps.
            translate([0, 0, -0.01])
                cylinder(r = EDF_BORE_R,
                         h = NACELLE_L + 0.02,
                         center = false);

            // ── Enlarged bore for sleeve zone ─────────────────────────────
            // STATOR_SLV_Z_START (90 mm) to AFT_SLV_Z_END (166.25 mm).
            // Bore step at STATOR_SLV_Z_START is the stator sleeve forward stop.
            translate([0, 0, STATOR_SLV_Z_START])
                cylinder(r = SLEEVE_BORE_R,
                         h = AFT_SLV_Z_END - STATOR_SLV_Z_START,
                         center = false);

            // ── Sleeve key slots (anti-rotation, both sleeves) ─────────────
            // 3× longitudinal slots at 0°/120°/240° spanning full sleeve zone.
            bore_key_slots();

            // ── EDF1 ESC wire exit slot ────────────────────────────────────
            esc_wire_exit_slot(pylon_side = PYLON_SIDE);

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

            // ── Nozzle access pocket (exposes sleeve retention screws) ────────
            // r = NOZZLE_ACCESS_OD/2 = 32.5 mm from NOZZLE_RING_Z aft.
            // Sleeve retention screws (BOSS_R = 28 mm) accessible when housing removed.
            nozzle_access_pocket();

        } // end difference (Zone A + Zone B)

        // ══════════════════════════════════════════════════════════════════
        // Zone C — geometry added after difference() closes.
        // ══════════════════════════════════════════════════════════════════

        // ── EDF1 nacelle-integrated motor-mount spider ────────────────────
        // At EDF1_SPIDER_Z = 87.75 mm (just forward of stator zone).
        edf1_nacelle_spider();

        // ── Aft sleeve retention M3 insert bosses on nozzle pocket face ──
        // 3× bosses at r = SLEEVE_BOSS_R = 28 mm, 120° spacing.
        sleeve_retention_bosses();

        // ── Push-on nozzle exit boss (housing skirt registers over this) ──
        // Smooth OD = 60 mm; 3× M3 set-screw flats at 0°/120°/240°.
        nozzle_push_boss();

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
// Infill      : 25% gyroid (nacelle cavity regions)
//               40% gyroid at pivot boss, bearing boss, and sleeve retention boss
// Nozzle      : Hardened-steel required for CF-PETG
// Supports    : None required if oriented intake-face-down
// Interior    : Fill nacelle cavity (between sleeve OD and outer shell) with
//               2 lb/cf low-density closed-cell foam after printing.
//               Insert foam before sliding EDF bore sleeves into nacelle.
//
// Post-print checks:
//   1. Sleeve bore ID = 55.4 mm ± 0.3 mm at 3 axial stations in sleeve zone
//      (Z = 90 … 166.25 mm).  Sleeve OD 55.0 mm must slide freely.
//   2. Key slots: 3.3 mm wide × 3.3 mm deep at 0°/120°/240°, full sleeve zone.
//   3. Pivot boss bore = 10.0 mm ± 0.1 mm (MF104ZZ OD press-fit), both X faces.
//   4. Tilt spar bore ID = 4.2 mm ± 0.1 mm through both X faces.
//   5. Retention boss bores = 3.5 mm ± 0.05 mm (M3 × 6 mm OLF heat-set insert).
//
// Post-print checks (additional, Rev T2):
//   6. Nozzle boss OD = 60.0 mm ± 0.2 mm — housing skirt bore 60.25 mm must
//      slide on without binding.
//   7. Boss flats at 0°/120°/240°: depth = 0.75 mm ± 0.1 mm.  M3 set screw
//      tip must seat fully in flat without protrusion past boss OD.
//   8. Access pocket OD = 65.0 mm ± 0.3 mm in Z = 166.25 … 186.25 mm band.
//      Sleeve boss heads (r = 28 mm) must be fully visible with housing removed.
//
// Nozzle installation (Rev T2 — push-on with M3 set screws):
//   1. Slide nacelle_nozzle_straight.scad housing over nozzle boss until
//      housing shoulder seats on boss aft face (positive stop).
//   2. Align housing set-screw holes with boss OD flats (3× at 120°).
//   3. Drive 3× M3×6 flat-point SHCS (2.5 mm hex key) through housing skirt
//      into boss flats.  Torque to 0.5 N·m; Loctite 243 on threads optional.
//   4. Install petals on 3 mm × 18 mm SS hinge pins; set desired fixed
//      orientation; threadlock pin ends in place.
//
// Render commands:
//   Port nacelle (RED nav light, pylon on +X, CW from intake):
//     openscad -o s_nacelle_port_simple_revt2.stl \
//              nacelle_pod_50mm_tandem_simple.scad \
//              -D SWIRL_DIR=1 -D PYLON_SIDE=1 -D NACELLE_SIDE=1
//   Starboard nacelle (GREEN nav light, pylon on -X, CCW from intake):
//     openscad -o s_nacelle_stbd_simple_revt2.stl \
//              nacelle_pod_50mm_tandem_simple.scad \
//              -D SWIRL_DIR=-1 -D PYLON_SIDE=-1 -D NACELLE_SIDE=-1
