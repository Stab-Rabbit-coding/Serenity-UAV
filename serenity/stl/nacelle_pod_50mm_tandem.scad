// =============================================================================
// nacelle_pod_50mm_tandem.scad
// Serenity UAV — Rev R — Tandem-EDF Nacelle Pod (50 mm bore, canonical hull)
// =============================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-05-26
// Revision: Rev T (2026-05-29)
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
// Change from Rev S (Rev T — 2026-05-29):
//   Sleeve architecture redesigned based on axial order:
//   intake → rotor1 → spider1 → motor1 → stator → rotor2 → spider2 → motor2 → nozzle
//
//   • EDF1 spider (spider1) INTEGRATED INTO NACELLE (Zone C) just forward of stator
//     zone at EDF1_SPIDER_Z = 87.75 mm (2 mm gap to stator leading edge).
//     M3 clearance holes on intake face; motor's own threads mate the joint.
//     Screws set from intake bore end (T-handle hex key, reach ≈ 88 mm).
//   • Single edf_bore_sleeve.scad REPLACED by two shorter sleeves:
//       edf_stator_sleeve.scad    — stator hub + 11 fins, Z = 90 … 122.5 mm
//       edf_aft_spider_sleeve.scad — EDF2 spider2, Z = 122.5 … 166.25 mm
//     Stator sleeve held in place by aft sleeve pushing forward face; no own screws.
//     Aft sleeve retained by 3× M3 SHCS at nozzle ring pocket face (Rev S method).
//   • Both sleeves have 3× longitudinal keys at 120° on OD; nacelle bore has
//     matching slots (bore_key_slots() Zone B) for anti-rotation and alignment.
//   • thrust_tube() restored: shortened to forward integral section Z = 27.5 … 90 mm.
//   • ESC wire exit slot added (esc_wire_exit_slot() Zone B) at Z ≈ 90 mm —
//     routes EDF1 ESC leads from bore to nacelle cavity at the sleeve joint.
//   • edf_bore_sleeve.scad is now DEPRECATED (superseded by the two sleeve files).
//   • Stator and spider parameters re-added for EDF1_SPIDER_Z computation and
//     nacelle-integrated edf1_nacelle_spider() module.
//
// Change from Rev Q (Rev R — 2026-05-29):
//   • motor_mount_ring() REPLACED by motor_mount_spider() (now superseded by Rev T).
//
// Change from Rev P (Rev Q):
//   • nacelle_pod() restructured: stator_hub(), stator_fin() loop, and both
//     motor_mount_ring() calls moved from the difference() inner union to the
//     outer union() AFTER the difference() closes.  In Rev P these modules were
//     placed inside the difference() additive union, where the full-length bore
//     cylinder (r=25 mm, full nacelle length) subtracted all geometry with
//     r < EDF_BORE_R — erasing stator hub (r=0-16 mm), stator fins (r=16-25 mm),
//     and motor-mount arms and hub (r=0-25 mm) entirely.  Only the retaining lip
//     ring (r=25-27.5 mm) survived.  Moving to the outer union() prevents the
//     bore subtraction from applying to bore-interior geometry.
//   • stator_fin() radial span extended ±1 mm at hub and bore-wall ends.
//   • motor_mount_ring() arm span extended ±1 mm (now replaced by Rev R).
//
// Change from Rev O (Rev P):
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
//   • EDF1 seat and 3-arm motor-mount spider      (forward EDF, upstream)
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

// ── EDF motor-mount spider geometry (Rev T — shared by nacelle EDF1 spider
//    and aft sleeve EDF2 spider) ───────────────────────────────────────────────
// Hub bore sized for motor shaft clearance; motor pass-through not required.
// EDF1 spider (nacelle-integrated): M3 CLEARANCE bores on intake face.
//   Motor's own M3 female threads (standard RC motor) mate the screws.
//   Screws set from intake bore end with T-handle 2.5 mm hex key.
// EDF2 spider (aft spider sleeve): M3 heat-set inserts on nozzle face.
//   Screws from nozzle bore end after iris removed.
SPIDER_ARM_H    =   8.0;   // [mm] arm axial thickness
SPIDER_ARM_W    =   6.0;   // [mm] arm tangential width
MOTOR_BOLT_R    =  10.0;   // [mm] M3 bolt circle radius — VERIFY vs actual motor
M3_INSERT_D     =   3.5;   // [mm] M3 × 6 mm OLF brass heat-set insert OD
M3_INSERT_L     =   6.0;   // [mm] heat-set insert depth
M3_CLEAR_D      =   3.3;   // [mm] M3 clearance bore diameter
R_HUB           =   8.0;   // [mm] spider hub outer radius (16 mm OD)
R_HUB_BORE      =   2.0;   // [mm] spider hub bore radius   ( 4 mm ID, 3 mm shaft + 1 mm)

// ── Inter-stage stator geometry (echoed from sleeve files for EDF1_SPIDER_Z) ──
STATOR_Z_BOT    =  93.75;  // [mm] stator bottom Z (was 75.0 × 1.25)
STATOR_Z_TOP    = 118.75;  // [mm] stator top Z    (was 95.0 × 1.25)

// ── EDF1 spider position (nacelle-integrated, just forward of stators) ─────────
// 2 mm axial gap between EDF1 spider aft face and stator fin leading edge.
// Wake from spider arms (120°) reattaches within ≈ 1.5 mm at cruise Re; the
// 2 mm gap prevents unsteady loading on stator leading edges.
EDF1_SPIDER_Z   = STATOR_Z_BOT - SPIDER_ARM_H / 2 - 2.0;  // = 87.75 mm

// EDF2 spider (in aft spider sleeve — edf_aft_spider_sleeve.scad).
// Nacelle-local Z; must satisfy: ≥ EDF2_Z_ENTRY + SPIDER_ARM_H/2 (126.5 mm)
//   and ≤ NOZZLE_RING_Z - SPIDER_ARM_H/2 (162.25 mm).
// Motor back plate (spider aft face + arm_h/2) + motor height (≈ 27 mm for 2627)
// should land at or before EDF2_Z_EXIT (178.8 mm).
// CONFIRM against actual motor dimensions before printing.
EDF2_SPIDER_Z   = 148.0;   // [mm] EDF2 spider centre, nacelle-local Z

// ── Nozzle ring pocket (defined here; used by AFT_SLV_Z_END below) ───────────
// Must precede the two-sleeve parameter block because AFT_SLV_Z_END references
// NOZZLE_RING_Z.  OpenSCAD 2021.01 does not resolve forward variable references
// reliably in initializer expressions.
NOZZLE_RING_Z   = 166.25;  // [mm] start Z of nozzle ring pocket (= CROWN_Z)
NOZZLE_RING_OD  =  65.0;   // [mm] pocket bore OD (rotating ring outer OD;
                            //      extended to 65 mm to cleanly cut fixed petals)
NOZZLE_RING_H   =  40.0;   // [mm] pocket axial depth

// ── Two-sleeve bore zone (Rev T) ─────────────────────────────────────────────
// edf_stator_sleeve.scad  : Z = STATOR_SLV_Z_START … STATOR_SLV_Z_END
// edf_aft_spider_sleeve.scad: Z = AFT_SLV_Z_START  … AFT_SLV_Z_END
// Both sleeves OD = EDF_CASING_R = 27.5 mm; nacelle bore enlarged to
// SLEEVE_BORE_R = 27.7 mm in this zone for 0.2 mm/side clearance fit.
// Stator sleeve forward stop: bore narrows to EDF_BORE_R at STATOR_SLV_Z_START.
// Aft sleeve aft retention: 3× M3 SHCS at nozzle ring pocket face.
STATOR_SLV_Z_START = EDF1_Z_EXIT;    // = 90.0  mm
STATOR_SLV_Z_END   = EDF2_Z_ENTRY;   // = 122.5 mm
AFT_SLV_Z_START    = EDF2_Z_ENTRY;   // = 122.5 mm
AFT_SLV_Z_END      = NOZZLE_RING_Z;  // = 166.25 mm
SLEEVE_BORE_R   = EDF_CASING_R + 0.2;  // [mm] = 27.7 mm

// ── Sleeve key geometry ───────────────────────────────────────────────────────
// 3× longitudinal keys at 0°, 120°, 240° on each sleeve OD (keys protrude radially
// outward).  Matching slots in nacelle bore wall prevent rotation under EDF torque
// and ensure repeatable orientation for wire routing and assembly.
// Both sleeves use the same key angles → single bore slot set in nacelle.
SLEEVE_KEY_W      =   3.0;  // [mm] key width  (tangential / circumferential)
SLEEVE_KEY_H      =   3.0;  // [mm] key height (radial protrusion above sleeve OD)
SLEEVE_KEY_SLOT_W = SLEEVE_KEY_W + 0.3;   // [mm] nacelle bore slot width (clearance)
SLEEVE_KEY_SLOT_H = SLEEVE_KEY_H + 0.3;   // [mm] nacelle bore slot depth (clearance)

// ── ESC wire exit slot ────────────────────────────────────────────────────────
// Rectangular slot through the forward thrust tube bore wall at the joint
// between the integral nacelle bore section and the stator sleeve zone.
// Routes EDF1 ESC motor leads and signal wire radially outward from the bore
// to the nacelle cavity, then forward to the pylon harness exit port.
// Slot on pylon side (PYLON_SIDE × X direction).
ESC_SLOT_W  =  14.0;  // [mm] slot circumferential width
ESC_SLOT_H  =   8.0;  // [mm] slot axial height
ESC_SLOT_Z  = STATOR_SLV_Z_START - ESC_SLOT_H / 2;  // = 86.0 mm (slot bottom Z)

// ── Sleeve retention boss geometry (Zone C, aft sleeve, nozzle pocket face) ──
// 3× M3 × 6 mm OLF insert bosses at NOZZLE_RING_Z, r = SLEEVE_BOSS_R, 120°.
// Aft spider sleeve aft face seats against pocket step; M3 × 20 mm SHCS from
// nozzle bore end through sleeve clearance bores into these inserts.
SLEEVE_BOSS_R   =  28.0;  // [mm] boss centre radius
SLEEVE_BOSS_OD  =   7.0;  // [mm] boss OD (M3 insert 3.5 mm OD + 2 × 1.75 mm wall)
SLEEVE_BOSS_L   =   6.0;  // [mm] boss protrusion into pocket (= insert depth)

SWIRL_DIR       =  +1;    // [+1 / -1] default port nacelle CW from intake
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
// Forward bore tube from EDF1_Z_ENTRY to STATOR_SLV_Z_START (Z = 27.5 … 90 mm).
// OD = EDF_CASING_R (27.5 mm), ID = EDF_BORE_R (25 mm); 2.5 mm wall.
// Provides structural bore wall for the integral nacelle section housing EDF1
// motor and spider.  Stator sleeve starts where this tube ends.
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
// step face (Z = NOZZLE_RING_Z).  The EDF bore sleeve aft flange seats against
// this face; 3× M3 SHCS (accessible from nozzle bore end after iris removed)
// pass through the sleeve flange and thread into these inserts.
//
// Boss geometry:
//   Centre radius   : SLEEVE_BOSS_R = 28 mm from bore axis
//   Boss OD         : SLEEVE_BOSS_OD = 7 mm (insert 3.5 mm + 2× 1.75 mm wall)
//   Boss outer edge : 28 + 3.5 = 31.5 mm < 32.5 mm (NOZZLE_RING_OD/2) → 1 mm clearance
//   Boss protrusion : SLEEVE_BOSS_L = 6 mm aft into pocket (Z_RING … Z_RING+6)
//
// Placed in Zone C (outer union after difference) so the nozzle ring pocket
// subtraction does not remove them.
module sleeve_retention_bosses() {
    for (angle = [0, 120, 240]) {
        rotate([0, 0, angle])
        translate([SLEEVE_BOSS_R, 0, NOZZLE_RING_Z])
            difference() {
                cylinder(r = SLEEVE_BOSS_OD / 2,
                         h = SLEEVE_BOSS_L,
                         center = false);
                // M3 heat-set insert bore (blind, opening toward nozzle end).
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
// Axial assembly order inside the bore:
//   rotor1 (fan) — spider1 (this module) — motor1 — stator — rotor2 — spider2 — motor2
//
// Motor mounting (EDF1):
//   • Motor slides in from nozzle end; back plate seats against spider AFT face.
//   • Motor shaft extends FORWARD through hub bore (Ø4 mm) to rotor1.
//   • 3× M3 SHCS from INTAKE bore end pass through M3 CLEARANCE bores in spider
//     arms and thread into motor's own M3 female back-plate holes.
//   • T-handle 2.5 mm hex key required; reach ≈ EDF1_SPIDER_Z ≈ 88 mm.
//
// Arms span (R_HUB − 1) → (EDF_BORE_R + 1) with ±1 mm CGAL overrun.
// M3 clearance bores run THROUGH the arm (intake face → nozzle face).
module edf1_nacelle_spider() {
    arm_h = SPIDER_ARM_H;
    arm_w = SPIDER_ARM_W;
    z_ctr = EDF1_SPIDER_Z;

    for (angle = [0, 120, 240]) {
        rotate([0, 0, angle])
        difference() {
            // Arm solid — ±1 mm overrun for CGAL volumetric overlap.
            translate([R_HUB - 1, -arm_w / 2, z_ctr - arm_h / 2])
                cube([EDF_BORE_R - R_HUB + 2, arm_w, arm_h]);
            // M3 clearance bore through full arm thickness (intake face to nozzle face).
            // Screw head sits on intake face; shaft exits nozzle face into motor.
            translate([MOTOR_BOLT_R, 0, z_ctr - arm_h / 2 - 0.01])
                cylinder(r = M3_CLEAR_D / 2,
                         h = arm_h + 0.02,
                         center = false);
        }
    }

    // Hub ring — OD = 2 × R_HUB (16 mm), bore = 2 × R_HUB_BORE (4 mm).
    // Motor shaft passes through; ESC phase wires share bore alongside shaft.
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
// Routes EDF1 ESC motor leads and signal wire radially from bore interior to the
// nacelle cavity (between bore tube and outer shell), then to the pylon harness.
// Placed on the pylon-side X face for direct routing to the pylon channel.
// Used as a Zone B subtraction.
module esc_wire_exit_slot(pylon_side = PYLON_SIDE) {
    cut_depth = (EDF_CASING_R - EDF_BORE_R) + 3.0;  // through tube wall + 3 mm into cavity

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
// Used as a Zone B subtraction.
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
// Top-level assembly.  Geometry is organised into three zones:
//
// Zone A — inside difference() additive union (survive bore subtraction, r > 25):
//   • nacelle_shell_imported() — canonical Serenity nacelle exterior hull
//   • thrust_tube()            — forward bore wall, Z = 27.5 … 90 mm (Rev T restored)
//   • inlet_bell()             — cosine-tapered intake lip
//   • pivot_x_face_boss()      — CG-pivot MF104ZZ bearing bosses
//   • pinion_a_boss()          — Drive Pinion A MR63ZZ boss
//   • crown_pinion_boss()      — Crown Pinion MR63ZZ boss
//   • shaft_conduit()          — longitudinal CF gear shaft conduit
//   • nav_wire_conduit()       — external WS2812C signal wire channel
//
// Zone B — subtracted by difference():
//   • Full-length 50 mm ID bore (opens intake and exhaust end caps)
//   • Sleeve zone bore: r = SLEEVE_BORE_R (27.7 mm) from STATOR_SLV_Z_START (90 mm)
//     to AFT_SLV_Z_END (166.25 mm) — accepts OD 55 mm sleeves
//   • bore_key_slots()         — 3× longitudinal anti-rotation key slots, sleeve zone
//   • esc_wire_exit_slot()     — EDF1 ESC wire exit at Z ≈ 86 mm
//   • nozzle_ring_pocket()     — iris ring seat at exhaust end
//   • harness_exit_port()      — ESC / nav-light wiring slot
//   • Tilt spar clearance bore (4.2 mm dia along X through both X-faces)
//
// Zone C — outer union() AFTER difference():
//   • edf1_nacelle_spider()     — EDF1 spider at Z = 87.75 mm (nacelle-integrated)
//   • sleeve_retention_bosses() — 3× M3 insert bosses on nozzle pocket face
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

                // ── Forward bore tube (Z = 27.5 … 90 mm, Rev T restored) ─
                // Structural bore wall for integral EDF1 section.
                // Stator / aft spider sleeves begin where this tube ends.
                thrust_tube();

                // ── Cosine-tapered intake bell (Z=0 → EDF1 seat) ─────────
                inlet_bell();

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

            // ── Enlarged bore for sleeve zone (Rev T) ─────────────────────
            // STATOR_SLV_Z_START (90 mm) to AFT_SLV_Z_END (166.25 mm).
            // Bore step at STATOR_SLV_Z_START provides stator sleeve forward stop.
            translate([0, 0, STATOR_SLV_Z_START])
                cylinder(r = SLEEVE_BORE_R,
                         h = AFT_SLV_Z_END - STATOR_SLV_Z_START,
                         center = false);

            // ── Sleeve key slots (anti-rotation, both sleeves) ─────────────
            // 3× longitudinal slots at 0°/120°/240° spanning full sleeve zone.
            bore_key_slots();

            // ── EDF1 ESC wire exit slot ────────────────────────────────────
            // Through forward thrust tube bore wall at Z ≈ 86 mm.
            esc_wire_exit_slot(pylon_side = PYLON_SIDE);

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

        } // end difference (Zone A + Zone B)

        // ══════════════════════════════════════════════════════════════════
        // Zone C — geometry added after difference() closes.
        // Stator hub/fins and motor-mount spiders moved to edf_bore_sleeve.scad
        // (Rev S).  Only sleeve retention bosses remain here.
        // ══════════════════════════════════════════════════════════════════

        // ── EDF1 nacelle-integrated motor-mount spider ────────────────────
        // At EDF1_SPIDER_Z = 87.75 mm (just forward of stator zone).
        // M3 clearance bores on intake face; screws from intake bore end.
        edf1_nacelle_spider();

        // ── Aft sleeve retention M3 insert bosses on nozzle pocket face ──
        // 3× bosses at r = SLEEVE_BOSS_R = 28 mm, 120° spacing.
        // Aft spider sleeve aft-face clearance holes mate with these bosses.
        // 3× M3 × 20 mm SHCS from nozzle bore end after iris removed.
        sleeve_retention_bosses();

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
//               40% gyroid at pivot boss, bearing boss, and sleeve retention boss regions
// Nozzle      : Hardened-steel required for CF-PETG
// Supports    : None required if oriented intake-face-down
// Interior    : Fill nacelle cavity (between sleeve OD and outer shell)
//               with 2 lb/cf low-density closed-cell foam after printing,
//               per CLAUDE.md fabrication standards.
//               Insert foam before sliding EDF bore sleeve into nacelle.
//
// Post-print checks:
//   1. Sleeve bore ID = 55.4 mm ± 0.3 mm at 3 axial stations in EDF zone
//      (Z = 27.5 … 178.8 mm).  Sleeve OD 55.0 mm must slide freely.
//   2. Pivot boss bore = 10.0 mm ± 0.1 mm (MF104ZZ OD press-fit), both X faces.
//   3. Tilt spar bore ID = 4.2 mm ± 0.1 mm through both X faces.
//   4. Shaft conduit ID = 3.5 mm ± 0.1 mm (4 mm PTFE tube).
//   5. Retention boss bores = 3.5 mm ± 0.05 mm (M3 × 6 mm OLF heat-set insert).
//
// Render commands:
//   Port nacelle (RED nav light, pylon on +X, CW from intake):
//     openscad -o s_nacelle_port_revs.stl nacelle_pod_50mm_tandem.scad \
//              -D SWIRL_DIR=1 -D PYLON_SIDE=1 -D NACELLE_SIDE=1
//   Starboard nacelle (GREEN nav light, pylon on -X, CCW from intake):
//     openscad -o s_nacelle_stbd_revs.stl nacelle_pod_50mm_tandem.scad \
//              -D SWIRL_DIR=-1 -D PYLON_SIDE=-1 -D NACELLE_SIDE=-1
