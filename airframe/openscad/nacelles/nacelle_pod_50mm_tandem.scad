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
//     downstream rotation about the tilt pivot (duct Z = PIVOT_Z = 111.5 mm), never a
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
//   • CG-aligned TRUNNION COLLAR at PIVOT_Z (Rev T4) — seats the printed
//       nacelle_trunnion.scad on the FIXED wing spar; nothing crosses the duct
//   • 4 × 10 AWG power-disconnect bay in the inboard flank (WA-R10)
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
// Both EDFs are Xfly Galaxy X5 **2627-3200KV** 50 mm 6S units.
// CORRECTED 2026-08-31 (owner-confirmed against the manufacturer's page): this
// line read 2700KV.  It was the only live 2700KV reference to this motor in the
// repo — AGENTS.md, LICENSE_AND_ATTRIBUTION.md and generate_placeholders.py all
// already said 3200KV.  (The 2700KV figures in docs/README.md and
// PHASED_BUILD_GUIDE.md belong to a different part, the 80 mm Changesun XRP
// 3660-2700KV of the archived Rev P / Phase 7 upgrade, and are untouched.)
// Derived operating point, for anything downstream that needs it:
//   6S nominal 22.2 V -> 71,040 rpm no-load;  6S full 25.2 V -> 80,640 rpm
//   tip speed at 71,040 rpm on Ø50 = 186 m/s (M 0.55 at ISA SL)
//   blade-passing frequency = 71,040/60 x 12 = 14.2 kHz
// The 11-vane stator count is UNAFFECTED — Tyler-Sofrin cut-off is a relationship
// between COUNTS (11 and 12 coprime), not frequencies.  What IS affected is the
// stator VANE ANGLE; see the flag on VANE_ANGLE_DEG in edf_stator_sleeve.scad.
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
// Nacelle mass breakdown — FULL rotating assembly (Rev T, at 1.25× scale)
// -------------------------------------------------------------------------
//   Re-derived 2026-07-19 for the Rev T pushrod / cam-only nozzle drive plus
//   the rotating Ø8 mm tilt-spar (supersedes the 2026-07-04 gear-train table of
//   342.4 g @ 104.5 mm).  Every component that tilts WITH the nacelle is
//   included; pylon/ground-fixed parts (wingtip sync gear, servo bracket) do
//   NOT tilt about the pivot and are excluded.  Changes from the gear-train
//   table: the ENTIRE tilt→nozzle gear train (Drive Pinion A, bevel pair +
//   housing, Crown/Nozzle Drive Pinion, idler + bracket, internal ring gear) is
//   DELETED (Option B, docs/NOZZLE_DRIVE_TRADE.md); the unison ring becomes a
//   cam-only disc; the flaps doubled 20→40 mm (Rev T2), moving their CG aft to
//   ~198 mm; a discrete Ø71 throat+housing now seats in the nozzle pocket; and
//   the rotating Ø8×1.5 mm 4130 spar (in-nacelle span), spar crank, and pushrod
//   are added on/near the pivot.  Printed-part masses = STL volume × effective
//   printed density (CF-PETG 1.05 g/cm³, calibrated from the documented
//   bevel-housing 0.72 g / 0.683 cm³; PETG flaps 1.00 g/cm³); steel 7.85 g/cm³.
//
//   Item                     Mass (g / lbm)   CG_Z mm (in)   Moment (g·mm)
//   ─────────────────────────────────────────────────────────────────────
//   EDF1 (upstream)          70 g (0.154 lbm)    59.4 (2.34)     4158
//   EDF2 (downstream)        70 g (0.154 lbm)   150.6 (5.93)    10542
//   ESC1 (in hub bore)       25 g (0.055 lbm)    59.4 (2.34)     1485
//   ESC2 (in hub bore)       25 g (0.055 lbm)   150.6 (5.93)     3765
//   Shell+stator+aft sleeve
//     +cowl skin            130 g (0.287 lbm)    92.8 (3.65)    12064
//   Nozzle throat+housing   21.4 g (0.047 lbm)  174.8 (6.88)     3741
//   Unison ring (cam-only)   6.7 g (0.015 lbm)  169.9 (6.69)     1138
//   8× nozzle flaps (40 mm) 21.1 g (0.047 lbm)  198.2 (7.80)     4182
//   Spar crank               1.4 g              111.5 (4.39)      156
//   Pushrod (COTS + links)   3.6 g              140.8 (5.54)      507
//   Rotating tilt-spar span 19.2 g (0.042 lbm)  111.5 (4.39)     2141
//   Total                   393.4 g (0.867 lbm) 111.5 (4.39)    43879
//
//   CG_Z = 43879 / 393.4 ≈ 111.5 mm (4.39 in) → PIVOT_Z = 111.5 mm, a +7.0 mm
//   aft move from the 104.5 mm gear-train pivot.  Drivers: the 40 mm flaps and
//   the discrete Ø71 housing at the far aft, only partly offset by the 19 g
//   steel spar sitting on the pivot; the deleted gear train and the ring-gear→
//   cam swap are ~a wash.  FIRST-PASS estimate (credible band ≈109–112 mm):
//   effective printed densities pending printer-sliced masses, and the discrete
//   housing vs. cowl-skin overlap pending the Ø72 nozzle-pocket shell re-bake
//   (see NOZZLE_RING_OD note + WBS §1.1.3).  First-article verification against
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
//   Pivot station   : 4.39 in (111.5 mm) from intake face (= full-assembly CG,
//                     Rev T; was 4.11 in / 104.5 mm under the gear-train drive)
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
// Measured from the centered-bore repaired STL near Z≈104.5 mm, Y<5mm (the old
// gear-train pivot).  Rev T moves the pivot to Z=111.5 mm — VERIFY the 34/38 mm
// face heights at the new station (they change little over +7 mm; WBS §1.1.3).
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

// ── Sleeve key CLOCKING (Rev T4b, 2026-08-31) ────────────────────────────────
// Moved 0/120/240 -> 30/150/270, and the reason is an interference, not tidiness.
//
// A key stands proud to r = 30.5 and runs the sleeve's full length, so a key at
// 0 deg lies along +X and a key at 180 deg along -X — which is exactly where the
// trunnion sits, on the starboard and port pods respectively.  Measured mesh
// against mesh, the 0 deg key drove 37.7 mm3 of solid overlap into the starboard
// trunnion (tools/nacelle_trunnion_fit.py gate T8b).
//
// With three keys at 120 deg spacing the only clockings that miss BOTH +X and -X
// are theta = 30 and 90 (and equivalents).  30/150/270 is used: it holds 30 deg
// of angular clearance from each trunnion, and at r 30.5 the keys reach only
// |X| = 26.4, inboard of the trunnion's 28.2 face by 1.8 mm.
//
// The aft sleeve's M3 retention screws pass THROUGH the key ribs, and the pod's
// retention bosses receive them, so all three feature sets move together.
SLEEVE_KEY_ANGLES = [30, 150, 270];

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
// CG_Z re-derived 2026-07-19 for the Rev T pushrod / cam-only nozzle drive plus
// the rotating Ø8 mm tilt-spar (see the mass breakdown in the header).
// Superseding history: 103.75 mm (pre-gear-train) → 104.5 mm (2026-07-04 gear
// train) → 111.5 mm (Rev T).  The Rev T changes — 40 mm flaps at ~198 mm, the
// discrete Ø71 throat+housing at ~175 mm, the cam-only ring, the deleted gear
// train, and the ~19 g steel spar sitting on the pivot — move the rotating CG
// to Z = 111.5 mm (4.39 in), a +7.0 mm aft shift.  Pylon-fixed parts (wingtip
// sync gear, servo bracket) do NOT tilt and are excluded.  Y = 0 (bore axis) =
// Y_cg for the bore-symmetric assembly.  FIRST-PASS (credible band ≈109–112 mm);
// see the header for the density / nozzle-pocket caveats.
PIVOT_Z         = 113.8;   // [mm] pivot axial centre = full-assembly CG station
                           //      Rev T4b (2026-08-31): 111.5 -> 105.8 -> 113.8,
                           //      the first values in this part's history that
                           //      were COMPUTED FROM MEASURED MESHES rather than
                           //      from an estimated header table.
                           //        111.5  estimated table (pod guessed at 130 g
                           //               with the sleeves)
                           //        105.8  pod MEASURED solid at 285 g — the CG
                           //               moved FORWARD, and hover clearance
                           //               with it, to -10.5 mm on the 1.5 in gear
                           //        113.8  pod hollowed with a forward-biased
                           //               wall, plus the in-nacelle HARNESS,
                           //               which no previous roll-up counted at
                           //               all and which sits entirely aft of the
                           //               pivot (22.9 g)
                           //      tools/nacelle_mass_cg.py is the authority for
                           //      this number and checks the fixed point: the CG
                           //      it computes must land within 0.25 mm of the
                           //      value set here, or the pod needs re-rendering.

// ── Fixed-spar TRUNNION interface (Rev T4, 2026-08-30) ───────────────────────
// SUPERSEDES the Rev R2 rotating Ø8 mm "skewer" entirely.  That spar ran
// spanwise THROUGH the nacelle, breached BOTH duct walls at the pivot, needed
// reinforcing collars at each breach, a keyed hub and a plain hub on the two
// X-faces, a full-width through-bore, and a streamlined strut inside the stator
// sleeve to carry it across the airflow.  All of that is DELETED.
//
// Under Rev T1 the spar is a FIXED 20 × 16.3 mm carbon tube bonded into the
// wing, and it TERMINATES at nacelle-local |X| = 26.7 mm — outside the r = 25 mm
// duct, by owner requirement (docs/WING_ATTACH_INTERFACE.md §4.3a;
// wings_s1223_revo.scad SPAR_TIP_PROTRUSION = 15.0).  Nothing crosses the duct.
// The nacelle now hangs off that stub on a separate printed trunnion
// (nacelle_trunnion.scad), and this file supplies only the COLLAR that trunnion
// bolts into: a register bore, a flange seat with three M3 inserts, and the
// cavity its ring gear and bearing barrel occupy.
//
// What the change buys, beyond deleting a part:
//   • the duct is unobstructed at the pivot — the stator's 11 vanes get the
//     last word before EDF2, which is what the Rev T2 strut could not give;
//   • the two duct-wall breaches and their reinforcing collars are gone, so the
//     duct pressure boundary is continuous;
//   • ~19 g of steel spar and its crank come off the rotating assembly.
// Closes WA-R7 / WA-R8 / WA-R9 / WA-R11 / WA-R12 and OI-8 (the axial budget —
// see nacelle_trunnion.scad, which is where that arithmetic lives).
SPAR_OD          =  20.0;  // [mm] fixed CF spar OD (Rev T1) — reference only;
                           //      the spar is a WING part, not built here
TRUNNION_X0      =  28.2;  // [mm] |X| of the spar tip = trunnion outboard face.
                           //      HARD BOUND, corrected 2026-08-31: the binding
                           //      radius here is NOT the r = 25 duct.  PIVOT_Z
                           //      lies inside the sleeve zone, where the bore is
                           //      SLEEVE_BORE_R (27.7) and the stator sleeve's
                           //      own OD is r 27.5.  At the old 26.7 the trunnion
                           //      and the spar both cut into the sleeve — a
                           //      measured 23.3 mm³ of solid overlap.  Gate T8.
WING_TIP_FACE_X  =  41.7;  // [mm] |X| of the wing tip face = NACELLE_OD_X/2
                           //      (37.7) + the 4.0 mm joint gap
TRUNNION_REG_D   =  34.0;  // [mm] H7 register bore — mates nacelle_trunnion.scad
                           //      REG_D 33.9
COLLAR_X0        = TRUNNION_X0 + 5.5;   // = 32.2  register bore, outboard end
COLLAR_X1        = TRUNNION_X0 + 9.0;   // = 35.7  flange seat rim face
COLLAR_OD        =  50.0;  // [mm] collar OD = trunnion flange OD
COLLAR_BOLT_D    =  41.5;  // [mm] 3 × M3 bolt circle (matches the trunnion)
COLLAR_FAIR_D    =  66.0;  // [mm] junction-fairing footprint diameter
COLLAR_FAIR_X    =  22.0;  // [mm] |X| the fairing blends back to.  Everything
                           //      it puts inside the duct is removed again by
                           //      the Zone-B bore subtraction, so the fairing
                           //      survives only as fore/aft gussets into the
                           //      shell — which is where the shell HAS material
                           //      (measured 2026-08-30: at |X| = 31 the skin
                           //      reaches only r ≈ 9 about the spar axis on the
                           //      +Y side, but r ≈ 97 fore and aft).
// Trunnion internal cavity: the ring gear (Ø41.6) and the bearing barrel live
// inside the pod, outboard of the collar bore.
TRUNNION_CAV_D   =  42.6;  // [mm] cavity Ø — gear tip Ø41.6 + 0.5 mm/side
TRUNNION_CAV_X0  = TRUNNION_X0 - 1.0;   // = 25.7, opens the cavity outboard so
                           //      the gear is not blind-ended.  This is a VOID,
                           //      not a member, so the ≥ 26 bound does not apply.
// Legacy name retained where still referenced downstream (nav channel etc.):
PIVOT_BOSS_DEPTH = COLLAR_X1 - NACELLE_FACE_X_PYLON;  // nav_channel Z reference

// ── 4 × 10 AWG power disconnect bay (WA-R10, Rev T4) ─────────────────────────
// Plan 003 U3 put the four high-current bullet disconnects in a wingtip
// "maintenance garage"; the wing MEASURED itself out of that (aft of the spar
// the tip section is 6.78 mm deep by station 66) and reassigned them here, to
// "the annular space between the duct wall and the outer skin".
//
// THAT ANNULUS DOES NOT EXIST, and the reassignment repeated the error it was
// correcting — assumed volume, not measured volume.  The canonical shell import
// is SOLID; only the duct is bored out of it, so the space between duct and
// skin is solid CF-PETG.  Measured 2026-08-30 on the bore-centred shell, the
// depth actually available on the inboard face (skin radius − duct radius −
// 2.5 mm skin − 2.5 mm duct wall) is:
//
//     Z      55    60    65    70    75    80    85    90    95   100   110
//     depth 6.58 −0.76  5.58  3.47  7.10  7.10  7.10  4.40  4.10  2.63  1.05
//
// It peaks at 7.10 mm over Z 75–88 and collapses aft of Z 90 where the bore
// steps out to the Ø55.4 sleeve zone.  There is no station on this flank with
// room for a 10 AWG BULLET pair laid lengthwise (~20 mm of barrel + shrink).
//
// SO THE BAY IS BUILT FOR RING TERMINALS ON STUDS, not bullets — one of the
// three disconnect styles the wing itself listed, and the only one that fits a
// 6.0 mm pocket.  Four M3 brass studs on a 7.5 mm pitch across the 30 mm width;
// ring terminals stack under a brass nut.  Brass, not steel: this is 21 mm from
// the AK7455 keep-out and the whole joint is a non-ferrous zone
// (docs/TILT_ENCODER_WIRING_EMI_SPEC.md §6.2).
//
// **A bullet or lever-nut bay becomes available only when the pod is hollowed**
// to a 2.5 mm skin, which would open a genuine 5–17 mm annulus here.  That is
// tracked as W0 in docs/plans/2026-08-30-001-weight-reduction-targets-plan.md
// and it is the same finding from the other end: the pod is solid.
//
// SITING.  Z 82 centre, so the bay spans 75–89 and SWALLOWS the existing
// esc_wire_exit_slot() at Z 86 — the EDF1 ESC leads now surface directly into
// the disconnect bay instead of into blind material.  It is also ≥ 20 mm from
// the signal harness port, which is the separation between 40 A feeds and
// shielded signal pairs that the EMI spec §2.3 requires and that the previous
// shared-flank arrangement did not have.
ESC_DISC_AVAIL   = NACELLE_FACE_X_PYLON - EDF_BORE_R - WALL_T;  // = 6.50 mm
                           // [mm] the GEOMETRIC bound: how deep a pocket in the
                           // inboard face can go before it breaches the duct.
                           // Aft of Z 90 the bore steps out to SLEEVE_BORE_R and
                           // this collapses to 3.80 mm, which is why the bay must
                           // stay forward of the sleeve zone.  Independently
                           // cross-checked against the measured skin: 7.10 mm of
                           // material remains over Z 75–88 after reserving both
                           // 2.5 mm walls, so 6.0 mm of pocket is inside both
                           // bounds.
ESC_DISC_W       =  30.0;  // [mm] bay width  (Y) — 4 studs on a 7.5 mm pitch
ESC_DISC_H       =  14.0;  // [mm] bay length (Z)
ESC_DISC_D       =   6.0;  // [mm] bay depth  (X) — 1.10 mm inside the measured
                           //      envelope; 6.0 is the wing's own clear-height
                           //      figure for a disconnect
ESC_DISC_Z       =  82.0;  // [mm] bay centre, in the measured 7.10 mm window
ESC_DISC_FILLET  =   3.0;  // [mm] corner radius — a square internal corner in a
                           //      printed part is where the crack starts
ESC_STUD_N       =   4;    // [count] M3 brass studs (one per 10 AWG feed)
ESC_STUD_PITCH   =   7.5;  // [mm] stud spacing across the bay width
// NO TROUGH IS BUILT, and that is a finding rather than an omission.  The
// bundle leaves the SPAR BORE at the trunnion (Z = PIVOT_Z) and would have to
// reach this bay 29.5 mm forward.  There is no compliant route in a solid pod:
// a groove in the inboard face may be at most
//     skin_r(Z) − SLEEVE_BORE_R − WALL_T = 3.55 mm deep at Z 110, 3.8 at Z 111.5
// before it breaks into the Ø55.4 sleeve bore, against a 4 × 10 AWG bundle whose
// circumscribed diameter is 13.28 mm (WING_ATTACH_INTERFACE §2.3) and whose
// individual conductor OD is not even recorded yet (that document's OI-1).
// Routing it through the bore instead would put 40 A conductors in the airflow.
//
// **WA-R10 therefore stays OPEN, and it is blocked on W0 (hollowing the pod),
// not on this file.**  What is built here is the bay itself, which is
// independently useful: it sits directly over esc_wire_exit_slot() at Z 86, so
// it is already the junction for the EDF1 ESC leads.  When the pod is hollowed
// to a 2.5 mm skin the 5–17 mm annulus appears, the wing bundle reaches the bay,
// and the same pocket becomes the full four-feed disconnect WA-R10 asks for.

// ── SUPERSEDED Rev T (2026-07-18) — the tilt→nozzle GEAR TRAIN ──────────────
// Drive Pinion A, the Crown / Nozzle Drive Pinion, the bevel pair and housing,
// the sector gear and the internal ring gear were all DELETED and archived when
// the nozzle drive became a pushrod (Option B, docs/NOZZLE_DRIVE_TRADE.md;
// WBS §1.1.3.1 "Gear train archived (Stage 4)").
//
// Their MOUNTING FEATURES were left behind in this file for another six weeks:
// pinion_a_boss(), crown_pinion_boss() and shaft_conduit() were still being
// unioned into every rendered pod.  They are removed at Rev T4.  This was not
// only dead mass — the conduit's Ø3.5 bore, blind at both ends once the gears
// went, exported as a SECOND, INVERTED body inside the pod (measured 2026-08-30:
// −25.2 mm³ at Y ≈ 31.8, Z 118–142), i.e. a sealed internal void that no slicer
// can fill and no inspection can reach.  Removing them returns the pod to a
// single solid body.  Constants removed (recorded, not re-used): PINION_A_Z/_Y/
// _BOSS_OD/_BOSS_L/_SHAFT_D, CROWN_Z, CROWN_BOSS_OD/_L, SHAFT_CONDUIT_OD/_ID.

// ── Inlet bell (1.25× scale) ──────────────────────────────────────────────────
INLET_BELL_L    =  27.5;   // [mm] inlet bell axial length (was 22.0 × 1.25)
INLET_BELL_FLARE=   3.0;   // [mm] extra flare radius at intake lip

// ── Circular intake exterior blend ─────────────────────────────────────────
// The imported canonical shell is asymmetric at the nose.  Intersecting that
// shell with a circular bore therefore leaves an oblique, elliptical-looking
// intake rim even though the duct itself is round.  This fairing supplies a
// planar circular lip and blends it into the existing shell over the same
// 27.5 mm intake transition.  The bore and its area are unchanged.
INTAKE_LIP_R       = EDF_BORE_R + WALL_T;  // [mm] circular outer lip radius
INTAKE_BLEND_R_PEAK = 38.2;                // [mm] below measured shell maximum
INTAKE_BLEND_R_END = 27.0;                 // [mm] buried in the duct wall
INTAKE_BLEND_L     = 90.0;                 // [mm] reaches the thrust-tube station

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

// ── SUPERSEDED Rev T4 (2026-08-31) — the separate harness exit port ──────────
// Rev S1c sized and sited this slot (14 x 18 mm at Z 93.85) to line up with the
// wing's TWO Ø7 mm EDF power conduits where they broke out of the tip face.
// THOSE CONDUITS NO LONGER EXIST — under Rev T1 the four 10 AWG feeds run inside
// the spar bore, on the tilt axis.  A slot aligned to a deleted conduit pair is
// 252 mm² of hole in the pod's principal bending section serving nothing.
//
// It is DELETED rather than re-sited, because there is nowhere to re-site it to.
// A pocket in the inboard flank may be at most
//     NACELLE_FACE_X_PYLON − bore_r − WALL_T
// deep before it breaches the duct: 6.5 mm forward of Z 90, and only 3.8 mm aft
// of it where the bore steps out to the Ø55.4 sleeve zone.  The one window with
// usable depth is Z 75–89, and the disconnect bay is already in it.
//
// So the two merge: **esc_disconnect_bay() is the single wing-interface pocket**,
// carrying the power studs and the ESC/gateway signal pairs.  That gives up the
// ≥ 20 mm power-to-signal separation of TILT_ENCODER_WIRING_EMI_SPEC §2.3, and
// the deviation is taken on the same grounds the wing already took it for its
// shared Ø6.5 conduit (§2.3, "Rev T1 wing conduit only"): the actual mitigation
// is 100 % braid shielding plus the ferrite-lined conduit of §3.3, and the rule
// guards UNSHIELDED proximity.  Recorded here as a DOCUMENTED DEVIATION, and it
// reverts the moment the pod is hollowed (weight plan W0) and a real annulus
// exists to separate them in.
// ── Internal cavity — the pod is HOLLOWED at Rev T4b (2026-08-31) ────────────
// Until now this file imported the SOLID canonical shell and subtracted only
// the duct, so each pod weighed 285 g and the "annular space between the duct
// wall and the outer skin" that the wiring architecture routes through did not
// exist.  It exists now.
//
// THE WALL IS DELIBERATELY NOT UNIFORM — owner direction, 2026-08-31:
//   "take more from the forward end instead of the aft end to adjust CG and
//    nacelle ground clearance."
// The tilt pivot sits at the rotating assembly's CG, so mass removed FORWARD of
// it drags the pivot AFT, which shortens the pivot-to-nozzle-tip arm one for one
// and lifts the nozzle in hover.  Measured (tools/nacelle_mass_cg.py):
//
//   configuration                     pod g   PIVOT_Z   hover clr, 1.5 in gear
//   solid, as built                   285.0     105.9      -10.47  STRIKES
//   uniform 2.5 mm wall               105.0     113.7       -1.31  strikes
//   THIS: 2.5 fwd -> 8.0 aft          155.9     114.4       -1.92  strikes
//                        ... and with plan 005's 30 mm flaps    +8.08  clears
//
// Two things that table says plainly and should not be softened: the forward
// bias is worth ~8.6 mm of the 10.5 mm deficit but CANNOT close it alone, and it
// costs about 22 g per further millimetre, so it is not a lever to keep pulling.
// The residual needs the nozzle stack to shorten (plan 005 R1) or the 3.0 in
// gear.  Uniform hollowing would save 24 g more and land 0.6 mm lower.
//
// The ramp station is also structurally right, not only mass-right: thickening
// across Z 100-140 puts material exactly where the trunnion collar (Z 105.8)
// feeds the tilt-joint moment into the pod, and where the EDF2 mount, the aft
// sleeve zone and the nozzle housing loads live.
//
// The cavity surface itself is MEASURED, not modelled — see
// tools/nacelle_hollow_profile.py, which ray-casts the canonical shell and emits
// the ring grid below.  Ray-casting rather than section radii, because the
// canonical mesh carries an internal forward intake pocket that makes a
// section's minimum radius meaningless below Z ~58.
include <nacelle_hollow_profile.scad>

CAVITY_DUCT_WALL  =  2.5;  // [mm] wall left on the duct side of the cavity
// Structural bulkheads.  A hollow shell with a duct tube inside it and no shear
// connection between them is a far weaker beam than the solid it replaces, and
// the pod is the beam that carries EDF thrust and nacelle inertia into the
// trunnion.  Three full annular webs forward of the trunnion restore the shear
// path; aft of it the 8 mm wall and the trunnion keep-out are already solid.
CAVITY_BULKHEAD_Z = [40.0, 62.0, 84.0];
CAVITY_BULKHEAD_T =  3.0;  // [mm] web thickness
// Each web must be VENTED or it seals a compartment.  The first render of the
// hollowed pod exported a −17,227 mm³ inverted body between Z 41.5 and 60.5 —
// the bay between the first two webs, closed at both ends and opening nowhere.
// A sealed void in a printed part cannot be drained, inspected, or dried, and
// CF-PETG is hygroscopic.  Six through-holes per web link every compartment to
// the openings at the disconnect bay, the nav-light bore, the ESC wire exit slot
// and the trunnion register.
CAVITY_VENT_N     =    6;  // [count] vent/drain holes per web
CAVITY_VENT_D     =  4.0;  // [mm] hole diameter
CAVITY_VENT_R     = 30.0;  // [mm] hole centre radius — inside the annulus at all
                           //      three web stations (measured: 27.5..33.1 at
                           //      Z 40, 27.5..34.5 at Z 84)
// Trunnion keep-out: solid material must survive around the collar, which is
// additive in Zone A and would otherwise be hollowed out from behind.
CAVITY_TRUNNION_R  = 30.0; // [mm] radius about the SPAR axis
CAVITY_TRUNNION_X0 = 20.0; // [mm] |X| the keep-out starts at
CAVITY_TRUNNION_X1 = 40.0; // [mm] |X| it ends at

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
// ── Module: circular_intake_fairing ─────────────────────────────────────────
// =============================================================================
// Additive rotationally symmetric exterior fairing.  Its front annulus is
// planar at Z=0, so the intake opening is circular in the side and front views.
// The outer profile first reaches the measured shell envelope, then tapers
// back into the duct wall before the thrust-tube station.  Its termination is
// therefore buried instead of exposing a circumferential cap at the shell.
module circular_intake_fairing() {
    N_STATIONS = 64;

    rotate_extrude(angle = 360, convexity = 4)
        polygon(
            points = concat(
                [[0, 0], [INTAKE_LIP_R, 0]],
                [
                    for (i = [0 : N_STATIONS])
                    let(
                        z_frac = i / N_STATIONS,
                        rise_frac = min(z_frac / (60 / INTAKE_BLEND_L), 1),
                        fall_frac = max((z_frac - (60 / INTAKE_BLEND_L))
                                / (1 - (60 / INTAKE_BLEND_L)), 0),
                        rise_smooth = rise_frac * rise_frac
                            * (3 - 2 * rise_frac),
                        fall_smooth = fall_frac * fall_frac
                            * (3 - 2 * fall_frac),
                        r_at_shell = INTAKE_LIP_R
                            + (INTAKE_BLEND_R_PEAK - INTAKE_LIP_R)
                            * rise_smooth,
                        r_outer = r_at_shell
                            + (INTAKE_BLEND_R_END - r_at_shell)
                            * fall_smooth,
                        z_abs = z_frac * INTAKE_BLEND_L
                    )
                        [r_outer, z_abs]
                ],
                    [[0, INTAKE_BLEND_L], [0, INTAKE_BLEND_L + 0.5]]
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
    for (angle = SLEEVE_KEY_ANGLES) {
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
    for (angle = SLEEVE_KEY_ANGLES) {
        rotate([0, 0, angle])
        translate([SLEEVE_BORE_R - 0.01, -SLEEVE_KEY_SLOT_W / 2, STATOR_SLV_Z_START])
            cube([SLEEVE_KEY_SLOT_H + 1.0, SLEEVE_KEY_SLOT_W, slot_len]);
    }
}


// =============================================================================
// ── Module: trunnion_collar  (Rev T4 — fixed-spar pivot) ─────────────────────
// =============================================================================
// ADDITIVE.  The seat nacelle_trunnion.scad bolts into, on the INBOARD (pylon)
// X-face at the pivot station, concentric with the fixed spar.
//
// Two pieces, and the second one is the interesting one:
//
//   1. The COLLAR proper — a Ø50 tube from COLLAR_X0 to COLLAR_X1 carrying the
//      Ø34 H7 register bore and the flange seat rim.
//   2. A JUNCTION FAIRING hulled from that rim back to a Ø66 footprint at
//      |X| = COLLAR_FAIR_X.  It is not decoration: the canonical shell falls
//      away hard on one side here.  Measured on the bore-centred shell at the
//      pivot, the skin's reach about the SPAR axis is
//          |X| = 31 →  r ≈ 9 at azimuth 0/345 (+Y),  r ≈ 97 fore and aft
//      so a collar standing to |X| = 35.7 has no shell under it on the +Y side
//      and a great deal of shell fore and aft.  The hull turns that into two
//      gussets running along the duct axis into the thick part of the shell,
//      which is the load path the joint actually needs, and fairs the ~15 mm
//      the collar stands proud on the tight side.
//
// The fairing is deliberately built oversize and then TRIMMED BY THE DUCT: it
// is placed in Zone A, so the Zone-B bore subtraction removes everything it put
// inside r = 25 (and inside the r = 27.7 sleeve bore).  Nothing here may finish
// closer than 26 mm to the duct axis — asserted in nacelle_pod().
//
// DOCUMENTED MOULD-LINE EXCEPTION (plan 2026-08-29-005 R7): the collar stands
// proud of the canonical shell at this station.  It cannot not: the encoder air
// gap is set from the wing tip pad at |X| = 39.7, which is 5.7 mm outboard of
// the shell face, and the wing side is already built to it.  The protrusion is
// wholly inside the 4.0 mm wing/nacelle joint gap region and is bounded by the
// wing tip face at |X| = 41.7 — it is a junction fillet, not drift.  Measured
// magnitude is reported by tools/nacelle_trunnion_fit.py.
module trunnion_collar() {
    sgn = PYLON_SIDE;
    union() {
        // ── Collar tube ────────────────────────────────────────────────────
        translate([sgn * COLLAR_X0, 0, PIVOT_Z])
            rotate([0, sgn * 90, 0])
                cylinder(d = COLLAR_OD, h = COLLAR_X1 - COLLAR_X0);

        // ── Junction fairing / gussets ─────────────────────────────────────
        hull() {
            translate([sgn * (COLLAR_X1 - 0.4), 0, PIVOT_Z])
                rotate([0, sgn * 90, 0])
                    cylinder(d = COLLAR_OD, h = 0.4);
            translate([sgn * COLLAR_FAIR_X, 0, PIVOT_Z])
                rotate([0, sgn * 90, 0])
                    cylinder(d = COLLAR_FAIR_D, h = 0.4);
        }
    }
}


// =============================================================================
// ── Module: trunnion_collar_cut  (Rev T4) ────────────────────────────────────
// =============================================================================
// SUBTRACTIVE counterpart to trunnion_collar().
//   • Ø34.0 H7 register bore, COLLAR_X0 … out through the inboard face
//   • Ø42.6 cavity for the trunnion's ring gear and bearing barrel
//   • 3 × M3 heat-set insert bores in the flange seat rim
//   • nav 3-core crossing port (WA-R11), radially separated from the power
//     bundle: the 40 A feeds come out of the SPAR BORE on the axis, the nav
//     3-core crosses through this port at r = 21 mm, 90° away from the
//     disconnect bay.  That is the radial + angular separation the EMI spec
//     asks for (§2.3) without a second conduit.
module trunnion_collar_cut() {
    sgn = PYLON_SIDE;

    // ── Register bore, open to the inboard face ────────────────────────────
    translate([sgn * COLLAR_X0, 0, PIVOT_Z])
        rotate([0, sgn * 90, 0])
            cylinder(d = TRUNNION_REG_D, h = (WING_TIP_FACE_X - COLLAR_X0) + 1);

    // ── Ring-gear / bearing-barrel cavity, outboard of the register ────────
    translate([sgn * TRUNNION_CAV_X0, 0, PIVOT_Z])
        rotate([0, sgn * 90, 0])
            cylinder(d = TRUNNION_CAV_D, h = COLLAR_X0 - TRUNNION_CAV_X0 + 0.01);

    // ── 3 × M3 heat-set inserts in the flange rim (bores run OUTBOARD) ─────
    for (i = [0 : 2])
        rotate([0, 0, i * 120])
            translate([0, COLLAR_BOLT_D / 2, 0])
                translate([sgn * (COLLAR_X1 + 0.01), 0, PIVOT_Z])
                    rotate([0, sgn * 90, 0])
                        cylinder(d = M3_INSERT_D, h = M3_INSERT_L + 0.01);

    // ── Nav 3-core crossing port (WA-R11) ──────────────────────────────────
    translate([sgn * (COLLAR_X1 + 0.01), 0, PIVOT_Z + COLLAR_BOLT_D / 2])
        rotate([0, sgn * 90, 0])
            cylinder(d = NAV_WIRE_BORE + 1.6, h = COLLAR_X1 - COLLAR_FAIR_X + 1);
}


// =============================================================================
// ── Module: esc_disconnect_bay  (Rev T4 — WA-R10) ────────────────────────────
// =============================================================================
// SUBTRACTIVE.  Carved pocket in the inboard flank for the four 10 AWG power
// disconnects, plus the trough that feeds it from the spar bore, plus the four
// stud insert bores.  See the parameter block for why it is stud-and-ring
// rather than bullet, and why it sits at Z 82.
//
// Filleted in both in-plane axes (hull of four cylinders) because this pocket
// is in the pod's principal bending section.
//
// SERVICE MODEL — reached by sliding the nacelle off the spar; there is no
// hatch, because the wing tip face is the cover (WING_ATTACH_INTERFACE §4.4).
// Open to the inboard face, so it also prints without support: the only
// overhang is the pocket roof, bridging 6 mm.
module esc_disconnect_bay(pylon_side = PYLON_SIDE) {
    face_x = pylon_side * NACELLE_FACE_X_PYLON;
    r      = ESC_DISC_FILLET;

    // ── Filleted pocket ────────────────────────────────────────────────────
    translate([(pylon_side > 0) ? (face_x - ESC_DISC_D) : face_x, 0, ESC_DISC_Z])
        hull()
            for (dy = [-1, 1], dz = [-1, 1])
                translate([0,
                           dy * (ESC_DISC_W / 2 - r),
                           dz * (ESC_DISC_H / 2 - r)])
                    rotate([0, 90, 0])
                        cylinder(r = r, h = ESC_DISC_D + 0.5);

    // ── 4 × M3 brass stud inserts in the pocket floor ──────────────────────
    // Bores run OUTBOARD from the floor into the 2.5 mm skin plus the material
    // behind it; ESC_DISC_AVAIL − ESC_DISC_D = 1.10 mm remains beyond the
    // insert, so the insert length is capped at that plus the duct wall.
    for (i = [0 : ESC_STUD_N - 1])
        translate([(pylon_side > 0) ? (face_x - ESC_DISC_D)
                                    : (face_x + ESC_DISC_D),
                   (i - (ESC_STUD_N - 1) / 2) * ESC_STUD_PITCH,
                   ESC_DISC_Z])
            rotate([0, pylon_side > 0 ? -90 : 90, 0])
                cylinder(d = M3_INSERT_D, h = M3_INSERT_L);

}


// =============================================================================
// ── Inboard-face boss cleanup (Rev R2, 2026-07-18) ────────────────────────────
// =============================================================================
// The canonical (Thingiverse-derived) shell carries a vestigial rectangular
// boss + socket on the PYLON (inboard) X-face just below the pivot — an artifact
// of no functional use.  Smooth it into the surrounding nacelle OML: the FILL
// closes the socket up to the natural face contour, the SHAVE removes the proud
// boss beyond it.  Boss measured at X-sign = PYLON_SIDE, Y +6..+30, Z +87..+101,
// ~7 mm proud (docs/TILT_SPAR_ANALYSIS boss note; verified on the pivot slab).
// BOSS_CONTOUR = measured natural |X|-face height vs Y, from clean Z rows.
BOSS_CONTOUR = [[37, 6], [36.5, 8], [36, 10], [35, 13], [33.4, 15], [32, 18],
                [30.2, 20], [28, 23], [26.2, 25], [24, 27], [22, 29], [20.5, 30]];
BOSS_Z_LO = 83.0;   // [mm] cutter lower Z
BOSS_Z_H  = 24.0;   // [mm] cutter Z span (covers Z 83..107)

module smooth_boss_fill() {   // union: solid 25..contour (Y6..25) — closes the socket
    fc = [[25, 6], [37, 6], [36.5, 8], [36, 10], [35, 13], [33.4, 15], [32, 18],
          [30.2, 20], [28, 23], [26.2, 25], [25, 25]];
    scale([PYLON_SIDE, 1, 1])
        translate([0, 0, BOSS_Z_LO]) linear_extrude(BOSS_Z_H) polygon(fc);
}

module smooth_boss_shave() {  // difference: remove material beyond the contour
    scale([PYLON_SIDE, 1, 1])
        translate([0, 0, BOSS_Z_LO]) linear_extrude(BOSS_Z_H)
            polygon(concat(BOSS_CONTOUR, [[50, 30], [50, 6]]));
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
// joins the wing-interface pocket esc_disconnect_bay() (Rev T4: this used to say
// harness_exit_port(), which is deleted — see its SUPERSEDED block above).  The wire groove is OPEN toward the interior (a snap-in
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
// ── Module: cavity_outer_solid ───────────────────────────────────────────────
// =============================================================================
// The measured cavity boundary as a closed polyhedron: one ring of HOLLOW_N_AZ
// points per station in HOLLOW_Z, with flat caps at each end.  Faces are wound
// CLOCKWISE seen from outside, which is what polyhedron() wants.
module cavity_outer_solid(grid) {
    nz = len(HOLLOW_Z);
    na = HOLLOW_N_AZ;
    pts = concat(
        [ for (k = [0 : nz - 1], i = [0 : na - 1])
              [ grid[k][i] * cos(i * 360 / na),
                grid[k][i] * sin(i * 360 / na),
                HOLLOW_Z[k] ] ],
        [ [0, 0, HOLLOW_Z[0]], [0, 0, HOLLOW_Z[nz - 1]] ]);
    c0 = nz * na;
    c1 = nz * na + 1;
    fs = concat(
        [ for (k = [0 : nz - 2], i = [0 : na - 1])
              [ k * na + i, (k + 1) * na + i, (k + 1) * na + (i + 1) % na ] ],
        [ for (k = [0 : nz - 2], i = [0 : na - 1])
              [ k * na + i, (k + 1) * na + (i + 1) % na, k * na + (i + 1) % na ] ],
        [ for (i = [0 : na - 1]) [ c0, i, (i + 1) % na ] ],
        [ for (i = [0 : na - 1])
              [ c1, (nz - 1) * na + (i + 1) % na, (nz - 1) * na + i ] ]);
    polyhedron(points = pts, faces = fs, convexity = 12);
}


// =============================================================================
// ── Module: cavity_duct_wall ─────────────────────────────────────────────────
// =============================================================================
// The solid the cavity may NOT eat into on the bore side: the duct plus one
// minimum wall, following the pod's own bore schedule (bell-mouth flare, the
// Ø50 EDF1 section, then the Ø55.4 sleeve zone).  Restated nowhere else — this
// reads the same constants the bore subtraction uses.
module cavity_duct_wall() {
    w = CAVITY_DUCT_WALL;
    union() {
        translate([0, 0, -1])
            cylinder(r1 = EDF_BORE_R + INLET_BELL_FLARE + w + 1,
                     r2 = EDF_BORE_R + w,
                     h  = INLET_BELL_L + 1);
        translate([0, 0, INLET_BELL_L])
            cylinder(r = EDF_BORE_R + w, h = STATOR_SLV_Z_START - INLET_BELL_L);
        translate([0, 0, STATOR_SLV_Z_START])
            cylinder(r = SLEEVE_BORE_R + w, h = NACELLE_L - STATOR_SLV_Z_START);
    }
}


// =============================================================================
// ── Module: hollow_cavity ────────────────────────────────────────────────────
// =============================================================================
// SUBTRACTIVE.  The measured cavity, less everything that must stay solid:
// the duct wall, three structural bulkheads, and a plug around the trunnion.
//
// NOT A TRAPPED VOID.  The cavity is deliberately open at four places — the
// disconnect bay pocket, the nav-light through-bore, the EDF1 ESC wire exit
// slot, and the trunnion register bore.  Printed intake-face-down the aft
// openings are uppermost, so air escapes and the cavity can be inspected and
// drained.  It is also, finally, the volume the wiring architecture has been
// drawn against since plan 003.
module hollow_cavity() {
    grid = (NACELLE_SIDE > 0) ? HOLLOW_R_PORT : HOLLOW_R_STBD;
    difference() {
        cavity_outer_solid(grid);
        cavity_duct_wall();
        // Structural webs, each with its vent holes drilled back through
        difference() {
            for (z = CAVITY_BULKHEAD_Z)
                translate([0, 0, z - CAVITY_BULKHEAD_T / 2])
                    cylinder(r = 60, h = CAVITY_BULKHEAD_T);
            for (z = CAVITY_BULKHEAD_Z, i = [0 : CAVITY_VENT_N - 1])
                rotate([0, 0, i * 360 / CAVITY_VENT_N + 30])
                    translate([CAVITY_VENT_R, 0,
                               z - CAVITY_BULKHEAD_T / 2 - 0.1])
                        cylinder(d = CAVITY_VENT_D,
                                 h = CAVITY_BULKHEAD_T + 0.2);
        }
        translate([PYLON_SIDE * CAVITY_TRUNNION_X0, 0, PIVOT_Z])
            rotate([0, PYLON_SIDE * 90, 0])
                cylinder(r = CAVITY_TRUNNION_R,
                         h = CAVITY_TRUNNION_X1 - CAVITY_TRUNNION_X0);
    }
}


// =============================================================================
// ── Module: nacelle_pod (main assembly) ──────────────────────────────────────
// =============================================================================
// Top-level assembly.  Geometry is organised into three zones:
//
// Zone A — inside difference() additive union (survive bore subtraction, r > 25):
//   • nacelle_shell_imported() — canonical Serenity nacelle exterior hull
//   • thrust_tube()            — forward bore wall, Z = 27.5 … 90 mm (Rev T restored)
//   • trunnion_collar()        — Rev T4 fixed-spar pivot seat + junction fairing
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
//   • nav_light_pocket()       — outboard flush WS2812C recess + wire bore
//   • trunnion_collar_cut()    — Ø34 H7 register, gear cavity, 3× M3, nav port
//   • esc_disconnect_bay()     — 4 × 10 AWG bullet-disconnect pocket (WA-R10)
//   • hollow_cavity()          — Rev T4b forward-biased internal cavity
//
// Zone C — outer union() AFTER difference():
//   • edf1_nacelle_spider()     — EDF1 spider at Z = 87.75 mm (nacelle-integrated)
//   • nav_wire_channel()        — cableway rib, now standing in the real cavity
//   • sleeve_retention_bosses() — 3× M3 insert bosses on nozzle pocket face
module nacelle_pod(swirl_dir = SWIRL_DIR) {

    // ── Hard geometric bounds, checked at parse time ─────────────────────────
    // The one requirement this whole revision exists to satisfy: no member of
    // the tilt joint may enter the thrust duct (docs/WING_ATTACH_INTERFACE.md
    // §4.3a).  TRUNNION_CAV_X0 is deliberately NOT checked — it is a void.
    assert(TRUNNION_X0 >= EDF_BORE_R + 1.0,
           "trunnion outboard face is inside the duct + 1 mm margin");
    assert(COLLAR_X1 < WING_TIP_FACE_X,
           "trunnion collar reaches past the wing tip face");
    assert(COLLAR_OD / 2 + 0.1 < COLLAR_FAIR_D / 2,
           "junction fairing is not larger than the collar it fairs");
    assert(ESC_DISC_D < ESC_DISC_AVAIL,
           "disconnect bay is deeper than the MEASURED inboard-face envelope");
    assert(ESC_DISC_Z - ESC_DISC_H / 2 >= 75.0
           && ESC_DISC_Z + ESC_DISC_H / 2 <= 89.0,
           "disconnect bay has left the Z 75-89 window where that depth exists");

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

                // ── Circular intake exterior fairing ─────────────────────
                // Establishes a round planar lip before the circular bore and
                // blends into the canonical shell over the existing intake
                // transition; it does not change the internal duct diameter.
                circular_intake_fairing();

                // ── Trunnion collar + junction fairing (Rev T4) ──────────
                // The fixed-spar pivot seat.  Placed in Zone A ON PURPOSE so
                // the bore subtraction below trims whatever the fairing hull
                // put inside the duct.
                trunnion_collar();

                // ── Fill the vestigial inboard-face socket (Rev R2) ──────
                smooth_boss_fill();

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


            // ── Nav-light emitter recess + through-wall wire bore (outboard)
            nav_light_pocket(pylon_side = PYLON_SIDE);

            // ── Shave the vestigial inboard-face boss (Rev R2) ───────────
            smooth_boss_shave();

            // ── Trunnion register bore, gear cavity, inserts, nav port ───
            trunnion_collar_cut();

            // ── 4 × 10 AWG disconnect bay (WA-R10) ────────────────────────
            esc_disconnect_bay(pylon_side = PYLON_SIDE);

            // ── Internal cavity (Rev T4b) — forward-biased hollowing ──────
            hollow_cavity();

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

        // ── Internal nav-light wire channel (inside the outboard skin) ────
        // Rev T4b: MOVED from Zone A to Zone C.  It is a rib standing INTO the
        // cavity, so while the pod was solid it was a no-op and while the
        // cavity is subtracted in Zone B it would simply be deleted.  Added
        // after the difference() closes, it is finally a real cableway in a
        // real void — which is what it was drawn to be.
        nav_wire_channel(pylon_side = PYLON_SIDE);

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
// MEASURED MASS (Rev T4, 2026-08-31): port 285.0 g, stbd 285.7 g at
// RHO_PRINT 1.05e-3 g/mm^3.  Not 132 g — that BOM figure named a file that does
// not exist and was never measured.  **The pod is SOLID**: this file imports the
// solid canonical shell and subtracts only the duct and a few pockets, so the
// "cavity" the foam note below refers to is not a cavity.  Hollowing it to a
// 2.5 mm skin recovers 96.4 g per pod and is tracked as W0 in
// docs/plans/2026-08-30-001-weight-reduction-targets-plan.md — the largest
// structural weight target on the aircraft.  The foam line below is therefore
// NOT ACTIONABLE as written and is retained only until W0 lands.
//
// Post-print checks (Rev T4):
//   1. Sleeve bore ID = 55.4 mm ± 0.3 mm at 3 axial stations in the EDF zone
//      (Z = 90 … 166.25 mm).  Sleeve OD 55.0 mm must slide freely, and the three
//      key slots must accept the sleeve keys without forcing.
//   2. Trunnion collar register bore = 34.0 mm H7 (+0.03/−0.00) over its full
//      3.5 mm depth; nacelle_trunnion.scad's Ø33.9 register must slip in.
//   3. Collar flange rim flat within 0.1 mm — it is the moment path from the
//      nacelle into the trunnion, and the three M3 inserts are not.
//   4. 3 × M3 insert bores = 3.5 mm ± 0.05 mm on the Ø41.5 bolt circle.
//      **Fit BRASS screws only** — this is inside the AK7455 non-ferrous zone.
//   5. Disconnect-bay pocket 30 × 14 × 6.0 mm at Z 82, with ≥ 2.5 mm of material
//      remaining between its floor and the Ø50 duct.
//   6. Sleeve retention boss bores = 3.5 mm ± 0.05 mm (M3 × 6 mm heat-set).
//   7. There must be NO through-bore on the X axis at the pivot.  If one is
//      present the render came from a pre-Rev-T4 source: the spar does not pass
//      through this part any more.
//
// ASSEMBLY ORDER AT THE TILT JOINT (Rev T4)
//   1. Press 2 × 6704ZZ into the trunnion's Ø27.0 seat, outboard bearing first.
//   2. Bond the ring magnet into the trunnion's inboard counterbore, flush.
//   3. Enter the trunnion into the collar FROM INSIDE the nacelle, register
//      first; the ring gear stays outboard of the collar and never passes it.
//   4. Seat the flange on the collar rim; 3 × M3 brass into the inserts; bond.
//   5. Slide the nacelle onto the wing's spar stub.  The trunnion's pilot spigot
//      lands 0.3 mm off the wing tip pad, which sets HALL_AIR_GAP = 1.5 mm.
//   6. Removal is the reverse and disturbs neither the wing, the spar, the
//      encoder calibration nor the drive shaft — the nacelle is the cover.
//
// Render commands (Rev R1 nacelle-swap corrected):
//   Port nacelle (pylon inboard -X; RED nav light OUTBOARD +X; CCW from intake):
//     openscad -o nacelle_port_revs.stl nacelle_pod_50mm_tandem.scad \
//              -D SWIRL_DIR=-1 -D PYLON_SIDE=-1 -D NACELLE_SIDE=-1
//   Starboard nacelle (pylon inboard +X; GREEN nav light OUTBOARD -X; CW from intake):
//     openscad -o nacelle_stbd_revs.stl nacelle_pod_50mm_tandem.scad \
//              -D SWIRL_DIR=1 -D PYLON_SIDE=1 -D NACELLE_SIDE=1
