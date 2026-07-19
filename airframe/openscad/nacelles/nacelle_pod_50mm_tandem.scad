// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  Primary-component STLs published to airframe/stls/
//   are stored directly in hull frame, baked by tools/bake_hull_frame.py
//   (marker 'SerenityUAV HULL-FRAME R1' in the binary STL header).
//   NEVER re-bake a mesh derived from an already-baked file.
//   This file:
//     Nacelle duct axis along local +Z with the intake at Z = 0.  The
//     published nacelle STLs (nacelle_port/stbd_revs.stl) are baked to
//     hull frame in CRUISE attitude (270 deg about +X + translation;
//     COMPONENTS['Nacelle_Port'] / ['Nacelle_Stbd']).  Hover is a
//     downstream rotation about the tilt pivot (duct Z = PIVOT_Z = 104.5 mm), never a
//     stored orientation.  After regeneration, re-run:
//         python3 tools/bake_hull_frame.py Nacelle_Port Nacelle_Stbd
//   Nacelle label correction (Rev R1/nacelle-swap, 2026-06-11):
//     Port nacelle (hull +X):  SWIRL_DIR=-1, PYLON_SIDE=-1, NACELLE_SIDE=-1
//     Stbd nacelle (hull -X):  SWIRL_DIR=+1, PYLON_SIDE=+1, NACELLE_SIDE=+1
//     The harness conduit exits the inboard face; this geometry was confirmed
//     by physical layout inspection in FreeCAD.  Filenames corrected to match
//     physical mounting side; original SCAD defaults (SWIRL_DIR=+1 for port)
//     were inverted relative to the fitted geometry.
// ===========================================================================
// =============================================================================
// nacelle_pod_50mm_tandem.scad
// Serenity UAV — Rev R — Tandem-EDF Nacelle Pod (50 mm bore, canonical hull)
// =============================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-05-26
// Revision: Rev R (2026-06-11)   [carried forward from Rev T (2026-05-29); no geometry changes]
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
//   • Drive Pinion A boss (MR63ZZ, at Y=PINION_A_Y=30.5mm, meshes sector gear)
//   • Crown Pinion boss (MR63ZZ, near nozzle ring, drives idler gear which
//       in turn drives the nozzle ring gear — see nacelle_nozzle_idler.scad)
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
// Counter-rotation (Rev R1/nacelle-swap corrected):
//   port nacelle CCW from intake (SWIRL_DIR=-1),
//   starboard nacelle CW from intake (SWIRL_DIR=+1).
//   Determined by harness-conduit inboard mounting geometry confirmed in FreeCAD.
//
// Scale note
// ----------
// The source nacelle shells are uniformly scaled 1.25× from the 24″ reference
// model (REF_SHELL_LENGTH=148.3 mm) so the bore matches the physical 50mm EDF.
// All Z-axis parameters in this file are at 1.25× reference scale.
// Bore-radius (EDF_BORE_R=25mm) and all radial dimensions are physical sizes.
//
// Nacelle mass breakdown — FULL rotating assembly (at 1.25× scale)
// -------------------------------------------------------------------------
//   Every component that tilts WITH the nacelle is included (updated
//   2026-07-04).  Pylon/ground-fixed parts — the fixed sector gear and the
//   servo bracket — do NOT tilt about the pivot and are excluded.  The WS2812B
//   exhaust LED rings were REMOVED from the design (TODO §1.1.3.5) and no longer
//   appear.  Printed-part masses (gears, idler, ring, petals) are from STL
//   volume × effective printed CF-PETG density; the shell line already carries
//   the canonical aft cowl outer skin (so the iris "housing" is NOT counted
//   again).
//
//   Item               Mass (g / lbm)   CG_Z mm (in)   Moment (g·mm)
//   ─────────────────────────────────────────────────────────────────────
//   EDF1 (upstream)    70 g (0.154 lbm)    59.4 (2.34)     4158
//   EDF2 (downstream)  70 g (0.154 lbm)   150.6 (5.93)    10542
//   ESC1 (in hub bore) 25 g (0.055 lbm)    59.4 (2.34)     1485
//   ESC2 (in hub bore) 25 g (0.055 lbm)   150.6 (5.93)     3765
//   Shell+stator+cowl  130 g (0.287 lbm)   92.8 (3.65)    12064
//   Drive Pinion A     0.14 g               104.0            15
//   Bevel pair         0.03 g               104.0             3
//   Bevel housing      0.72 g               104.0            75
//   Crown Pinion       0.14 g               156.25           22
//   Nozzle idler gear  3.30 g               161.25          532
//   Idler bracket      0.90 g               161.25          145
//   Nozzle ring gear   7.00 g               169.25         1185
//   8× nozzle petals   10.2 g               176.0          1795
//   Total             342.4 g (0.755 lbm)  104.5 (4.11)    35786
//
//   CG_Z = 35786 / 342.4 ≈ 104.5 mm (4.11 in) → PIVOT_Z = 104.5 mm.  Only
//   +0.75 mm aft of the previous 103.75 mm pivot, so the pivot boss and gear
//   stations move negligibly.  First-article verification against printer-
//   sliced masses still applies (per the original acceptance note).
//
// Nacelle key dimensions — imperial primary, mm in parentheses
//   (OpenSCAD variable assignments remain in mm):
//   Total length    : 7.29 in (185.2 mm) at 1.25× scale
//   EDF bore ID     : 1.97 in (50.0 mm)
//   EDF casing OD   : 2.17 in (55.0 mm)
//   Nacelle OD (X)  : 2.97 in (75.4 mm)  spanwise bounding box
//   Nacelle OD (Y)  : 3.28 in (83.3 mm)  fore-aft bounding box
//   Wall minimum    : 0.098 in (2.5 mm)  CF-PETG
//   Pivot station   : 4.11 in (104.5 mm) from intake face (= full-assembly CG)
//   Stator zone     : 3.69–4.68 in (93.75–118.75 mm) from intake
//   Nozzle pocket   : starts at 6.55 in (166.25 mm) from intake
//   Per-nacelle thrust (static, 2× EDF × 90% stator eff):
//     2.73 lbf (1,240 gf) per EDF × 2 × 0.90 = 4.91 lbf (2,232 gf) per nacelle
//   Both nacelles total thrust: 9.84 lbf (4,464 gf)
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
//   Port nacelle (pylon inboard on -X face; RED nav light on the OUTBOARD +X
//     face per REF-FAA-003; CCW from intake):
//     openscad -o nacelle_port_revs.stl nacelle_pod_50mm_tandem.scad \
//              -D SWIRL_DIR=-1 -D PYLON_SIDE=-1 -D NACELLE_SIDE=-1
//
//   Starboard nacelle (pylon inboard on +X face; GREEN nav light on the
//     OUTBOARD -X face per REF-FAA-003; CW from intake):
//     openscad -o nacelle_stbd_revs.stl nacelle_pod_50mm_tandem.scad \
//              -D SWIRL_DIR=1 -D PYLON_SIDE=1 -D NACELLE_SIDE=1
//
// =============================================================================


// =============================================================================
// ── Parameter Block ───────────────────────────────────────────────────────────
// =============================================================================

// ── Primary dimensions ────────────────────────────────────────────────────────
// All Z-axis values are at 1.25× reference scale (REF_SHELL_LENGTH = 148.3 mm
// (5.84 in) → physical length = 185.2 mm (7.29 in) as measured from the
// repaired nacelle STL).
NACELLE_L       = 185.2;  // [mm] total nacelle length (intake face to nozzle exit)
                            //      = 7.29 in (185.2 mm)
EDF_BORE_R      =  25.0;  // [mm] EDF bore inner radius → 50 mm (1.97 in) ID (Xfly Galaxy X5)
EDF_CASING_R    =  27.5;  // [mm] EDF casing outer radius → 55 mm (2.17 in) OD
WALL_T          =   2.5;  // [mm] minimum wall thickness — 0.098 in (2.5 mm) CF-PETG per CLAUDE.md

// ── Outer nacelle dimensions (canonical Serenity shape at 1.25× scale) ───────
// These are measured from the repaired STL bounding box.  They are provided for
// reference only; the actual shell geometry comes from the imported STL.
NACELLE_OD_X    =  75.4;  // [mm] nacelle bounding-box width, spanwise (X)  = 2.97 in
NACELLE_OD_Y    =  83.3;  // [mm] nacelle bounding-box depth, fore-aft  (Y) = 3.28 in

// ── X-face positions at the pivot station (Z ≈ PIVOT_Z, Y ≈ 0) ───────────────
// Measured from the centered-bore repaired STL near the pivot (Z≈104.5mm, Y<5mm).
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
EDF1_Z_ENTRY    =  27.5;  // [mm] EDF1 forward face  (was 22.0 × 1.25)  = 1.08 in
EDF1_Z_EXIT     =  90.0;  // [mm] EDF1 aft face      (was 72.0 × 1.25)  = 3.54 in
EDF2_Z_ENTRY    = 122.5;  // [mm] EDF2 forward face  (was 98.0 × 1.25)  = 4.82 in
EDF2_Z_EXIT     = 178.8;  // [mm] EDF2 aft face      (was 143.0 × 1.25) = 7.04 in

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
NOZZLE_RING_OD  =  72.0;   // [mm] pocket bore OD — Rev T (2026-07-18, Option B):
                            //      grown 65 -> 72 to seat the pushrod-drive
                            //      nozzle housing (nacelle_nozzle_iris.scad Rev T
                            //      HOUSING_OUTER_R = 35.6, OD ≈ 71.2) inside the
                            //      canonical cowl (measured inner ≈ Ø72 at the
                            //      pocket start).  VERIFY: the baked pod shells
                            //      (nacelle_port_revs.stl / nacelle_stbd_revs.stl)
                            //      MUST be re-rendered/re-baked to cut this larger
                            //      pocket — tracked in WBS §1.1.3 (not re-baked in
                            //      this pass; the canonical-shell bake needs review).
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
// CG_Z re-derived 2026-07-04 for the FULL rotating assembly — the earlier
// 103.75 mm figure omitted the tilt gear train and the nozzle ring/petal/idler
// mechanism and still carried the (now-removed) WS2812B exhaust LED ring.  With
// every component that tilts with the nacelle included (see the mass breakdown
// in the header) and the exhaust LED rings deleted per TODO §1.1.3.5, the
// rotating CG lands at Z = 104.5 mm (4.11 in).  Pylon-fixed parts (sector gear,
// servo bracket) do NOT tilt and are excluded.  Y = 0 (bore axis) = Y_cg for the
// bore-symmetric assembly.
PIVOT_Z         = 104.5;   // [mm] pivot axial centre = full-assembly CG station

// ── Rotating 8 mm tilt-spar interface (Rev R2, 2026-07-18) ─────────────────────
// SUPERSEDES the MF104ZZ 4 mm fixed-rod pivot.  The 8 mm spar (AISI 4130,
// hollow 5 mm ID) is FIXED (keyed) to the nacelle at the CG and ROTATES with it,
// driven by the cargo-bay servo; the tilt bearings live at the wing root (cargo
// bay) and the wingtip, NOT in the nacelle.  So the nacelle needs a KEYED hub
// (inboard) + a plain support hub (outboard) + reinforcing collars where the
// bore breaches the two duct walls, and a full-width through-bore.  The nav
// 3-core routes through the hollow spar to the outboard nav light.
// See docs/TILT_SPAR_ANALYSIS.md.
SPAR_OD         =   8.0;   // [mm] rotating spar OD
SPAR_BORE_D     =   8.15;  // [mm] through-bore (clearance; spar fixed only at keyed hub)
SPAR_HUB_OD     =  16.0;   // [mm] keyed/support hub OD (matches old boss OD)
SPAR_HUB_PROUD  =   4.0;   // [mm] hub protrusion beyond the X-face skin
SPAR_HUB_EMBED  =   4.0;   // [mm] hub root buried inside shell wall (overlap margin)
SPAR_KEY_FLAT   =   0.8;   // [mm] D-flat depth at the inboard keyed hub (rotational lock)
SPAR_WALLBOSS_OD =  15.0;  // [mm] duct-wall reinforcing collar OD
SPAR_WALLBOSS_L  =   6.0;  // [mm] duct-wall collar length (straddles the bore breach)
// Legacy names retained where still referenced downstream (nav channel etc.):
PIVOT_BOSS_DEPTH =  SPAR_HUB_PROUD; // [mm] kept for nav_channel Z reference
CLEVIS_EAR_OD   =  16.0;   // [mm] retained for compatibility (nav rib sizing)

// ── Gear mount features ───────────────────────────────────────────────────────
// Module M=1.0, pressure angle 20°.
PINION_A_Z      = PIVOT_Z;  // [mm] Pinion A shaft Z (tracks PIVOT_Z = 104.5)
PINION_A_Y      =  30.5;   // [mm] Pinion A fore-aft offset = R_sector + R_pinionA
                           //   = 22 + 8.5 = 30.5 mm (Rev S1: Pinion A regeared
                           //   12T R6 -> 17T R8.5 for the internal-ring nozzle
                           //   drive — docs/NOZZLE_DRIVE_TRADE.md.  30.5 mm is
                           //   ALSO the internal-mesh centre distance to the
                           //   nozzle ring, R_ring - R_drive = 34 - 3.5, so the
                           //   whole shaft run stays on one Y station.)
PINION_A_BOSS_OD=   7.0;   // [mm] MR63ZZ press-fit boss OD (6mm OD + 0.5mm wall)
PINION_A_BOSS_L =  10.0;   // [mm] boss length (2× MR63ZZ stacked + gap)
PINION_A_SHAFT_D=   3.2;   // [mm] shaft clearance bore
// Rev S1 (2026-07-07): the compound idler is DELETED — the Nozzle Drive
// Pinion (14T M0.5, nacelle_pinion.scad PINION_VARIANT="DRIVE") meshes the
// INTERNAL nozzle ring gear directly at the ring plane, its 4 mm gear band
// seated in the ring's gear band (iris local Z 0..4.5 = nacelle Z
// 166.25..170.75).  This boss is the shaft's MR63ZZ bearing, placed just
// FORWARD of the nozzle housing so the pinion cantilevers into the ring.
CROWN_Z         = NOZZLE_RING_Z - 6.0;   // [mm] = 160.25; drive-pinion shaft
                                         //   bearing boss centre (Rev S1)
CROWN_BOSS_OD   =   7.0;   // [mm] same spec as Pinion A
CROWN_BOSS_L    =  10.0;   // [mm] boss length
SHAFT_CONDUIT_OD=   5.5;   // [mm] conduit outer diameter
SHAFT_CONDUIT_ID=   3.5;   // [mm] conduit inner bore

// ── Inlet bell (1.25× scale) ──────────────────────────────────────────────────
INLET_BELL_L    =  27.5;   // [mm] inlet bell axial length (was 22.0 × 1.25)
INLET_BELL_FLARE=   3.0;   // [mm] extra flare radius at intake lip

// ── Navigation light + harness exit (1.25× scale Z values) ───────────────────
// Rev S1 (2026-07-04, TODO §1.1.3.5): the WS2812C position light was moved from
// the INBOARD (pylon) face to the OUTBOARD (far) face, and its signal wire was
// re-routed from an EXTERNAL protruding D-section conduit to an INTERNAL cableway
// buried in the skin.
//   • Item 6 — a red (port) / green (starboard) position light must radiate to
//     its own side of the aircraft [REF-FAA-003 §91.209(a)]; on the inboard face
//     the pylon/fuselage occludes the required outboard arc.  It now sits in a
//     flush recess on the outboard face so nothing protrudes past the mould line.
//   • Item 7 — the wire runs in an internal covered channel bonded to the inside
//     of the outboard skin (never breaks the exterior surface) down to the
//     existing harness exit, reusing the EDF harness path to the pylon.
PYLON_SIDE      = +1;      // [+1 / -1] inboard (pylon) face: +1=port, -1=stbd;
                            //   outboard (light) face is the opposite sign
NAV_WIRE_BORE   =  2.4;    // [mm] WS2812C 3-core 28AWG signal-wire bore ID
// Outboard-face emitter recess (flush WS2812C-2020 seat; does NOT protrude):
NAV_LIGHT_Z     = 70.0;    // [mm] emitter Z station (forward third, wide side arc;
                            //   VERIFY/fine-tune against the canonical skin in FreeCAD)
NAV_LIGHT_POCKET_D     = 7.0;  // [mm] recess diameter (2×2 mm LED + lens + potting)
NAV_LIGHT_POCKET_DEPTH = 2.5;  // [mm] recess depth into the outboard face (≤ wall + lens)
// Internal wire channel (covered rib on the inside of the outboard skin):
NAV_CHAN_W      =  5.0;    // [mm] channel outer width (Y)
NAV_CHAN_D      =  4.5;    // [mm] channel outer depth (radially inward from skin)
NAV_CHAN_Z_LO   = NAV_LIGHT_Z;                    // [mm] channel start (at emitter)
NAV_CHAN_Z_HI   = PIVOT_Z - PIVOT_BOSS_DEPTH - 1.0;  // [mm] end below pivot boss root
NAV_CHAN_INSET  =  3.0;    // [mm] channel wall sits this far inboard of the outer face

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
            import("../../stls/nacelles/eng_left_shell24_50mm_repaired.stl",
                    convexity = 4);
    } else {
        // ── Starboard (right) nacelle ─────────────────────────────────────────
        translate([-BORE_CX_R, BORE_CY, 0])
            import("../../stls/nacelles/eng_right_shell24_50mm_repaired.stl",
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
// ── Module: inlet_bellmouth ──────────────────────────────────────────────────
// =============================================================================
// SUBTRACTIVE cosine bell-mouth intake, carved into the SOLID canonical nacelle
// dome (TODO §1.1.3.4).  Rev S1 (2026-07-04): the previous inlet_bell() was an
// ADDITIVE flared tube whose lip (r ≈ 30.5 mm at Z = 0) protruded well past the
// canonical leading dome, whose ogive nose is only r ≈ 21 mm at the tip growing
// to ≈ 38.7 mm by Z = 27.5 mm.  Because the imported nacelle shell is a SOLID
// body (the airflow path is carved by subtraction), the correct intake is a
// subtractive cosine bell-mouth: a filled plug of revolution whose outer wall
// follows r_cut(z) = EDF_BORE_R + INLET_BELL_FLARE·0.5·(1+cos(180°·z/L)),
// flaring from r = EDF_BORE_R (aft, Z = L) to EDF_BORE_R+FLARE (front).  Since
// r_cut(z) is monotonically DECREASING in z and the dome radius is monotonically
// INCREASING, the two surfaces cross exactly once: everything forward of that
// crossover (the thin nose tip, thinner than the 50 mm EDF anyway) is removed and
// the LEADING EDGE of the nacelle becomes precisely that dome∩cosine crossover
// rim — exactly the §1.1.3.4 requirement — while the dome aft of it is untouched
// (r_cut < dome there).  A 0.5 mm forward overshoot guarantees a clean cut of the
// voxel-capped front face.  VERIFY the exact crossover station in FreeCAD against
// the canonical mould line.
module inlet_bellmouth() {
    N_STATIONS = 32;

    translate([0, 0, -0.5])   // overshoot the front cap for a clean cut
        rotate_extrude(angle = 360, convexity = 4)
            polygon(
                points = concat(
                    [[0, 0]],   // axis point at the (overshot) front face
                    [
                        for (i = [0 : N_STATIONS])
                        let(
                            z_frac = i / N_STATIONS,
                            z_abs  = z_frac * INLET_BELL_L,
                            r_cut  = EDF_BORE_R
                                    + INLET_BELL_FLARE * 0.5
                                        * (1 + cos(180 * z_frac))
                        )
                        [r_cut, z_abs]
                    ],
                    [[0, INLET_BELL_L]]   // back to axis at the aft end
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
// ── Module: pivot_x_face_boss  (Rev R2 — keyed 8 mm spar hubs) ────────────────
// =============================================================================
// SOLID (bored separately) keyed hubs on the nacelle X-faces at PIVOT_Z, Y=0,
// for the rotating 8 mm spar that is FIXED to the nacelle (replaces the two
// MF104ZZ bearing bosses).  Inboard (+X, pylon side) is the KEYED hub (the spar
// D-flat locks rotation here); outboard (−X, far side) is a plain support hub
// the spar/nav-wire exits through.  The 8 mm through-bore and the inboard D-flat
// are SUBTRACTED in the main assembly (Zone B), so these are additive solids.
//
// Face asymmetry (measured from the true shell slab, 2026-07-18):
//   +X pylon face ≈ 37.1 mm, −X far face ≈ 37.7 mm.  SPAR_HUB_EMBED (4 mm) buries
// the hub root well inside the wall on both sides, so the union is solid despite
// the pod's approximate NACELLE_FACE_X_* constants (34/38).
module pivot_x_face_boss() {
    for (sign = [-1, +1]) {
        face_dist = (sign > 0) ? NACELLE_FACE_X_PYLON : NACELLE_FACE_X_FAR;

        // ── Solid keyed/support hub cylinder (bored later in Zone B) ─────────
        translate([sign * (face_dist - SPAR_HUB_EMBED), 0, PIVOT_Z])
        rotate([0, sign * 90, 0])
            cylinder(r = SPAR_HUB_OD / 2,
                    h = SPAR_HUB_EMBED + SPAR_HUB_PROUD,
                    center = false);

        // ── Load-spreading web onto the shell (hull avoids coplanar faces) ──
        hull() {
            translate([sign * (face_dist - SPAR_HUB_EMBED), 0, PIVOT_Z])
            rotate([0, sign * 90, 0])
                difference() {
                    cylinder(r = SPAR_HUB_OD / 2, h = 0.4, center = false);
                    cylinder(r = SPAR_HUB_OD / 2 - WALL_T, h = 0.41, center = false);
                }
            translate([sign * (face_dist + SPAR_HUB_PROUD), 0, PIVOT_Z])
            rotate([0, sign * 90, 0])
                cylinder(r = SPAR_HUB_OD / 2, h = 0.4, center = false);
        }
    }
}


// =============================================================================
// ── Module: spar_duct_wall_bosses  (Rev R2) ──────────────────────────────────
// =============================================================================
// Reinforcing collars where the 8 mm spar bore breaches the two duct walls
// (bore inner radius EDF_BORE_R = 25 mm) at Y=0, PIVOT_Z.  Straddle the wall so
// the airflow-duct penetration stays sealed and stiff.  Additive; bored in Zone B.
module spar_duct_wall_bosses() {
    for (sign = [-1, +1])
        translate([sign * (EDF_BORE_R - SPAR_WALLBOSS_L / 2), 0, PIVOT_Z])
        rotate([0, sign * 90, 0])
            cylinder(r = SPAR_WALLBOSS_OD / 2, h = SPAR_WALLBOSS_L, center = false);
}


// =============================================================================
// ── Module: pinion_a_boss ────────────────────────────────────────────────────
// =============================================================================
// MR63ZZ bearing boss for Drive Pinion A.  Cylinder along X at
// (Y=PINION_A_Y=30.5mm, Z=PIVOT_Z).  Meshes the fixed sector gear (R=22mm)
// at centre-distance 22+8.5=30.5mm from the pivot axis (Rev S1).
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
// MR63ZZ bearing boss for the Nozzle Drive Pinion shaft at CROWN_Z (Rev S1;
// the part this supports was called the "Crown Pinion" through Rev R1).
// Co-planar with Pinion A in Y so the longitudinal CF shaft runs straight.
//
// The drive pinion is documented (nacelle_pinion.scad, nacelle_bevel_housing.scad)
// as mounted on the longitudinal shaft (nacelle Z-axis) — unlike Pinion A,
// which is transverse (X-axis, meshes the fixed sector gear on the tilt
// pivot) and needs rotate([0, 90, 0]) to lay its bore along X.  This boss
// must NOT carry that rotation: cylinder() already extrudes along Z by
// default, the correct bore axis here.  Fixed 2026-06-22 — see TODO.md
// §1.1.3.3 ("crown_pinion_boss() copies pinion_a_boss()'s rotate([0,90,0])
// X-axis-bore pattern verbatim").
module crown_pinion_boss() {
    translate([0, PINION_A_Y, CROWN_Z])
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
// Axial PTFE-sleeve conduit from Pinion A to the Nozzle Drive Pinion.
// Y = PINION_A_Y = 30.5 mm (co-linear with both bosses → straight shaft path).
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
// ── Module: nav_light_pocket ─────────────────────────────────────────────────
// =============================================================================
// SUBTRACTIVE.  Flush WS2812C-2020 position-light recess in the OUTBOARD (far)
// X-face + a short through-wall wire bore reaching the internal wire channel.
// Port = RED, Stbd = GREEN [REF-FAA-003 §91.209(a)].  The recess is cut INTO the
// canonical mould line (interior modification per CLAUDE.md) — the LED + lens sit
// flush, nothing protrudes.  Built on the +X (stbd-outboard / port-inboard) side
// then mirrored: the OUTBOARD face is opposite the pylon side.
module nav_light_pocket(pylon_side = PYLON_SIDE) {
    // out_sign = -pylon_side: outboard is opposite the pylon.  Build on +X,
    // mirror to -X when the outboard face is on -X.
    if (-pylon_side > 0) _nav_light_pocket_posX();
    else mirror([1, 0, 0]) _nav_light_pocket_posX();
}
module _nav_light_pocket_posX() {
    // Emitter recess: short cylinder bored inward (−X) from the +X outer face.
    translate([NACELLE_FACE_X_FAR + 0.01, 0, NAV_LIGHT_Z])
        rotate([0, -90, 0])
            cylinder(r = NAV_LIGHT_POCKET_D / 2,
                    h = NAV_LIGHT_POCKET_DEPTH + 0.01,
                    center = false);
    // Through-wall wire bore: from the outer face inward just far enough to reach
    // the internal channel groove (INSET + channel depth + margin), NOT all the
    // way to the bore axis.
    translate([NACELLE_FACE_X_FAR + 0.01, 0, NAV_LIGHT_Z])
        rotate([0, -90, 0])
            cylinder(r = NAV_WIRE_BORE / 2,
                    h = NAV_CHAN_INSET + NAV_CHAN_D + 1.0,
                    center = false);
}


// =============================================================================
// ── Module: nav_wire_channel ─────────────────────────────────────────────────
// =============================================================================
// ADDITIVE.  An INTERNAL cableway rib bonded to the inside of the OUTBOARD skin,
// running longitudinally from the emitter (NAV_CHAN_Z_LO) to just below the pivot
// boss (NAV_CHAN_Z_HI), where the wire joins the existing ESC/harness bundle and
// exits via harness_exit_port() to the pylon (reuses the EDF cableway — TODO
// §1.1.3.5 item 7).  The wire groove is OPEN toward the interior (a snap-in
// U-channel, not a sealed tunnel — so it prints without a trapped void and the
// wire is field-serviceable), and open at both Z ends (wire enters from the
// pocket bore at the top, drops into the interior at the bottom).  The rib sits
// NAV_CHAN_INSET inboard of the outer face, never breaking the exterior mould
// line, and at |X| ≈ FAR − INSET it is well outside the 50 mm airflow bore
// (r = 25 mm), so the Zone-B bore subtraction never reaches it.  Built on +X
// then mirrored to the outboard side.
module nav_wire_channel(pylon_side = PYLON_SIDE) {
    if (-pylon_side > 0) _nav_wire_channel_posX();
    else mirror([1, 0, 0]) _nav_wire_channel_posX();
}
module _nav_wire_channel_posX() {
    chan_out = NACELLE_FACE_X_FAR - NAV_CHAN_INSET;   // outer edge of rib (≈35)
    chan_in  = chan_out - NAV_CHAN_D;                 // inboard edge (≈30.5)
    chan_len = NAV_CHAN_Z_HI - NAV_CHAN_Z_LO;

    difference() {
        translate([chan_in, -NAV_CHAN_W / 2, NAV_CHAN_Z_LO])
            cube([NAV_CHAN_D, NAV_CHAN_W, chan_len]);
        // Groove open on the INBOARD face (bore centred at chan_in): half the
        // cylinder lies outside the rib → open U-channel, no enclosed void.
        // Overruns both Z ends so the wire path is open top and bottom.
        translate([chan_in, 0, NAV_CHAN_Z_LO - 0.1])
            cylinder(r = NAV_WIRE_BORE / 2, h = chan_len + 0.2);
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
//   • pivot_x_face_boss()      — CG-pivot MF104ZZ bearing bosses
//   • pinion_a_boss()          — Drive Pinion A MR63ZZ boss
//   • crown_pinion_boss()      — Crown Pinion MR63ZZ boss
//   • shaft_conduit()          — longitudinal CF gear shaft conduit
//   • nav_wire_channel()       — internal WS2812C wire cableway (outboard skin)
//
// Zone B — subtracted by difference():
//   • Full-length 50 mm ID bore (opens intake and exhaust end caps)
//   • inlet_bellmouth()        — cosine intake flare; trims dome tip so the
//                                 leading edge = canonical dome ∩ cosine intake
//   • Sleeve zone bore: r = SLEEVE_BORE_R (27.7 mm) from STATOR_SLV_Z_START (90 mm)
//     to AFT_SLV_Z_END (166.25 mm) — accepts OD 55 mm sleeves
//   • bore_key_slots()         — 3× longitudinal anti-rotation key slots, sleeve zone
//   • esc_wire_exit_slot()     — EDF1 ESC wire exit at Z ≈ 86 mm
//   • nozzle_ring_pocket()     — iris ring seat at exhaust end
//   • harness_exit_port()      — ESC / nav-light wiring slot
//   • nav_light_pocket()       — outboard flush WS2812C recess + wire bore
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

                // (Intake bell-mouth is now SUBTRACTIVE — see Zone B,
                //  inlet_bellmouth(); TODO §1.1.3.4.)

                // ── CG-pivot keyed 8 mm spar hubs (at PIVOT_Z, Y=0) ──────
                pivot_x_face_boss();

                // ── Duct-wall reinforcing collars at the spar breach ─────
                spar_duct_wall_bosses();

                // ── Drive Pinion A bearing boss (MR63ZZ, at PIVOT_Z) ─────
                pinion_a_boss();

                // ── Crown Pinion bearing boss (MR63ZZ, at CROWN_Z) ───────
                crown_pinion_boss();

                // ── Longitudinal CF gear-shaft conduit ────────────────────
                shaft_conduit();

                // ── Internal nav-light wire channel (inside outboard skin) ─
                nav_wire_channel(pylon_side = PYLON_SIDE);

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

            // ── Cosine intake bell-mouth (front flare, trims dome tip) ────
            // Leading edge = canonical dome ∩ cosine intake (TODO §1.1.3.4).
            inlet_bellmouth();

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

            // ── Nav-light emitter recess + through-wall wire bore (outboard)
            nav_light_pocket(pylon_side = PYLON_SIDE);

            // ── Rotating 8 mm spar through-bore (along X, Rev R2) ─────────
            // Spans both X faces + hub protrusions + margin for clean exits.
            translate([0, 0, PIVOT_Z])
                rotate([0, 90, 0])
                    cylinder(
                        r      = SPAR_BORE_D / 2,
                        h      = NACELLE_FACE_X_PYLON + NACELLE_FACE_X_FAR
                                + 2 * SPAR_HUB_PROUD + 8,
                        center = true
                    );

            // ── Inboard keyed D-flat (locks the fixed spar rotationally) ──
            // Axis-aligned chord slab across the top of the bore, only over the
            // inboard (+X pylon) keyed hub, so the spar's matching D-flat seats
            // and the nacelle cannot rotate on the spar (they turn as one).
            //   X: over the keyed-hub length; Y: full bore width; Z: top KEY_FLAT.
            translate([NACELLE_FACE_X_PYLON - SPAR_HUB_EMBED,
                       -6,
                       PIVOT_Z + SPAR_BORE_D / 2 - SPAR_KEY_FLAT])
                cube([SPAR_HUB_EMBED + SPAR_HUB_PROUD + 0.1, 12, SPAR_KEY_FLAT + 3]);

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
// Render commands (Rev R1 nacelle-swap corrected):
//   Port nacelle (pylon inboard -X; RED nav light OUTBOARD +X; CCW from intake):
//     openscad -o nacelle_port_revs.stl nacelle_pod_50mm_tandem.scad \
//              -D SWIRL_DIR=-1 -D PYLON_SIDE=-1 -D NACELLE_SIDE=-1
//   Starboard nacelle (pylon inboard +X; GREEN nav light OUTBOARD -X; CW from intake):
//     openscad -o nacelle_stbd_revs.stl nacelle_pod_50mm_tandem.scad \
//              -D SWIRL_DIR=1 -D PYLON_SIDE=1 -D NACELLE_SIDE=1
