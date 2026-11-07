// =============================================================================
// nacelle_pod_64mm_tandem.scad — Serenity nacelle pod, QX-Motor 64 mm tandem
// =============================================================================
// Plan: docs/plans/2026-09-28-001-feat-nacelle-nozzle-servo-drive-plan.md, U9.
// WBS:  airframe/wings-nacelles/WBS.md §1.1.4 NAC-64-SERVO-01, NAC-64-*.
// Record: docs/NACELLE_64MM_VERIFICATION.md.
//
// HOW THIS FILE WORKS (Rev U)
// ---------------------------
// Self-contained.  Until Rev U it included the 50 mm pod and overrode its parameters
// (OpenSCAD keeps the LAST assignment of a variable for the file scope); that layering was
// flattened by tools/scad_flatten.py, so the 64 mm values below are the values in effect and
// nothing here depends on a 50 mm source.  Shared helpers still `include` the 64 mm scale
// table and the generated cowl table.
//
// VERIFIED 2026-11-07: rendered before and after the flatten (OpenSCAD 2021.01).  Volume is
// identical (367,236.67 mm3), as are the bounds and the face count (124,866).  124,862 triangles
// match exactly; the other 4 lie in one plane (z = 92.79, an 8.7 x 2.6 mm patch) where a flat
// face is triangulated differently, in a spot OpenSCAD already reports as non-manifold in the
// pre-flatten export as well.  The iris and trunnion flattens are exact (symmetric difference
// 0.0000 mm3).
//
// OWNER DECISIONS APPLIED (Steve Griffing, GitHub Stab-Rabbit-coding)
// -------------------------------------------------------------------
//   2026-10-01  KTD9: 64 mm flow tube, QF2822 mounts on 4 x M3 / 16 mm bolt
//               circle.  Printed nacelle tube is the rotor flow boundary.
//   2026-10-03  STATOR FRONT PLATE IS THE MOTOR MOUNT (no separate spider).
//   2026-10-03  Wing interface held at the pylon face: wing tip, spar stub and
//               trunnion keep their positions relative to the INBOARD face;
//               the nacelle axis moves outboard by P64_AXIS_SHIFT.
//   2026-10-03  Pivot trunnion re-sited to the rotating-assembly CG.
//   2026-10-03  PROPORTIONS (supersedes the 1.28 radial / fixed-185.2 choice):
//               "minimum radial scale, lengthen to canon at that diameter,
//               optimised for aerodynamics, thrust, weight and canonical
//               shape."  tools/nacelle_64_proportion_trade.py pick: radial
//               1.21 (packaging minimum: pylon wall >= 41 mm, ESC-bay skin),
//               canonical axial stretch 1.13 -> L 209.3 mm.  Canon L/D
//               [REF-CAD-003 Sheets 3/4] 2.24 plan / 2.31 side; this pod
//               2.29 / 2.08 (was 1.92 / 1.74 at 1.28 x 185.2).
//   2026-10-03  INTAKE: a proper rounded lip (owner: "implement the rounded
//               intake bell as a proper aerodynamic design").  See below.
//   2026-10-03  80 A Open-Secure-ESC builds (WBS NAC-64-ESC-80A) — bay fit open until a part
//               is selected.
//   2026-10-03  Trunnion bearings 2 x 6704-ZZ -> 2 x 6804-ZZ: spar stub +7.0 mm
//               (20.5), joint collar +7.0 mm off the pylon face (WBS
//               NAC-64-TILT-01, nacelle_trunnion_64mm.scad).
//
// INTAKE LIP — two quarter-ellipses meeting at the highlight
// ----------------------------------------------------------
//   internal  2:1 ellipse, P64_LIP_A x P64_LIP_F = 16.0 x 8.0 mm, from the
//             highlight (Z 0, r 40.0) to the 64 mm throat at Z 16.0.
//             Contraction ratio (40/32)^2 = 1.56.  Nose radius F^2/a = 4.0 mm.
//   external  ellipse P64_FORE_A x P64_FORE_B = 1.56 x 2.5 mm with the SAME
//             4.0 mm nose radius, to the shoulder radius 42.5 mm (1.67 in),
//             then (2026-11-01) faired per azimuth into the canonical skin
//             with G1 continuity, Z 28-45 (circular_intake_fairing()).
//   Both branches have a RADIAL tangent and equal curvature at the highlight:
//   the leading edge is a true round nose (no corner, no cusp, no knife edge).
//   SELECTED BY CFD (tools/nacelle_intake_cfd.py, real external forebody,
//   static/hover): of eight lip variants, "lipE" (this one) is the only one
//   with no reversed flow on lip, bell or duct AND <= 4.2 % total-pressure
//   loss at r/R 0.95 on the rotor face.  The cosine bell (sharp lip) lost the
//   outer 10 % of radius; a knife-edged outside separated; contraction ratio
//   1.27-1.45 left tip separation.  A straight 64 mm duct runs from Z 16 to
//   the rotor at Z 30.5, so the rotor runs in a constant bore (no tip-gap
//   growth).  The cowl is hollowed behind a 6 mm solid nose and vented
//   into the pod cavity (lip_ring_cavity()).

// AXIAL STACK (nacelle-local Z, mm; QF2822 drawing 8-4.jpg, VERIFY)
// -----------------------------------------------------------------
//     0.0 – 13.0   elliptical lip (internal contour)
//    13.0 – 30.5   straight inlet duct, 64 mm
//    30.5 – 41.2   rotor 1 hub (10.7 shaft protrusion)
//    42.2 – 45.2   stator-1 front plate = motor-1 mount  } stator sleeve
//    45.2 – 103.2  motor 1 body (58.0) inside stator-1 hub } 42.2 – 103.7
//   104.2 – 114.9  rotor 2 hub                            } aft sleeve
//   115.9 – 118.9  stator-2 front plate = motor-2 mount   } 103.7 – 187.86
//   118.9 – 176.9  motor 2 body        (11.0 mm margin to the nozzle pocket)
//   187.86 –       nozzle ring pocket (166.25 x 1.13, rides on the shell)
//
// NOT YET RE-DERIVED IN THIS FILE — each is an open WBS item, not an omission:
//   • edf_stator_sleeve.scad / edf_aft_spider_sleeve.scad (NAC-64-GEOM-01).
//   • nacelle_nozzle_iris.scad at 64 mm (plan U11) — NOZZLE_RING_OD is a
//     proportional placeholder for the pocket only.
//   • ESC cooling ports onto the sleeve wall (NAC-64-GEOM-02) and the 80 A
//     board fit (NAC-64-ESC-80A).
//   • nacelle_esc_cover.scad still builds from the unscaled skin grid.
//   • Hull-frame bake (tools/bake_hull_frame.py) for P64_AXIS_SHIFT.
//
// Render (stbd shown; port = all three -1):
//   openscad -o nacelle_stbd_64mm.stl nacelle_pod_64mm_tandem.scad \
//            -D SWIRL_DIR=1 -D PYLON_SIDE=1 -D NACELLE_SIDE=1
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CEH (Stab-Rabbit-coding) —
// owner decisions above.  Parameter derivation, lip design and file by Claude
// (Claude Opus 5.5, Anthropic) under the author's direction, per AGENTS.md AI
// attribution.  Derivative of nacelle_pod_50mm_tandem.scad, which carries the
// full upstream attribution chain (canonical shell: REF-CAD-001/REF-CAD-003).
// References: [REF-EDF-003] QX-Motor 64 mm EDF manual and QF2822 drawing;
// [REF-CAD-003] QMx blueprint pack (canonical proportions).
// License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
// =============================================================================

// ── 64 mm constants — declared BEFORE the include (see ORDERING RULE) ──────
// P64_K / P64_A (and P64_SCALE, the 2026-10-05 uniform x1.06 enlargement for
// the 70 A ESC bays) come from the single-source nacelle_64_scale.scad.
include <nacelle_64_scale.scad>
P64_BORE_R      = 32.0;   // [mm] 64 mm (2.52 in) nominal flow diameter.  The
                          //      rotor running clearance is NOT this number —
                          //      measure the bare rotor (NAC-64-FIT-02).
P64_WALL        =  2.5;   // [mm] duct wall = the 50 mm pod's WALL_T
P64_FACE_PYLON  = 34.0 * P64_K;          // = 41.14 mm pylon face |X|
P64_AXIS_SHIFT  = P64_FACE_PYLON - 34.0; // = 7.14 mm (0.28 in) per side
// Trunnion bearing upgrade (owner 2026-10-03, WBS NAC-64-TILT-01): the spar
// stub is 7.0 mm longer and the joint stands 7.0 mm further off the pylon
// face, so the trunnion carries 2 x 6804-ZZ in a 15 mm stack.  See
// nacelle_trunnion_64mm.scad and wings_s1223_revo.scad SPAR_TIP_PROTRUSION_64N.
P64_STUB_EXTRA  = 7.0;

// Intake lip (header).
P64_LIP_A       = 16.0;   // [mm] internal ellipse, axial semi-axis (2:1)
P64_LIP_F       =  8.0;   // [mm] internal ellipse, radial semi-axis (flare)
                          //      CFD lip sweep winner "lipE" (header)
P64_HL_R        = P64_BORE_R + P64_LIP_F;   // = 40.0 mm highlight radius
P64_FORE_R      = 42.5;   // [mm] lip SHOULDER radius = CFD lipE exactly
                          //      (tools/nacelle_intake_cfd.py).  2026-11-01:
                          //      no longer scaled x1.06 and no longer HELD as a
                          //      cylinder — aft of the shoulder the cowl is lofted
                          //      per azimuth into the measured canonical skin
                          //      (cowl_fair_loft(), nacelle_cowl_fair_table.scad).
P64_FORE_B      = P64_FORE_R - P64_HL_R;    // = 2.5 mm external semi-axis
// External semi-axis chosen so the external nose curvature radius B^2/A equals
// the internal one F^2/a (= 4.0 mm): a TRUE round nose.  A knife-edged
// outside (B^2/A = 0.18 mm, first cut) separated in the hover CFD.
P64_FORE_A      = P64_FORE_B * P64_FORE_B / (P64_LIP_F * P64_LIP_F / P64_LIP_A);
                          // = 1.5625 mm
P64_RING_HOLD   = 22.0 * P64_SCALE;   // [mm] aft limit of the lip-ring cavity
                                      //      (+ wall); the cowl is >= r 42.5 there
P64_COWL_SINK   = 0.3;    // [mm] cowl ends this far INSIDE the skin at its junction so
                          //      the skin, not the loft, is the surface aft of it
                          //      (no coincident faces)
P64_RING_WALL   =  2.5;   // [mm] lip-ring skin (AGENTS.md §7 2.0 min; 2.5 matches
                          //      the pod's measured skin)
P64_RING_CAV_Z0 =  6.0;   // [mm] solid nose ahead of the ring cavity

// Stack.
P64_ROTOR_Z     = 30.5;   // [mm] rotor-1 hub forward face (trade tool pick)
P64_BODY        = 58.0;   // [mm] QF2822 rear cap to mount face, 8-4.jpg — VERIFY
P64_SHAFT       = 10.7;   // [mm] 68.7 − 58.0 shaft protrusion — VERIFY
P64_GAP         =  1.0;   // [mm] running / interstage gap
P64_PLATE       =  3.0;   // [mm] stator front plate (motor mount) thickness
P64_STAGE       = P64_SHAFT + P64_GAP + P64_PLATE + P64_BODY;   // = 72.7 mm

// ---- begin include <nacelle_pod_50mm_tandem.scad> (inlined by scad_flatten.py) ----
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
// License : CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
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
// [flattened] NACELLE_L: value from its last assignment (override), kept at the first position
NACELLE_L       = 185.2 * P64_A;  // [mm] total nacelle length (intake face to nozzle exit)
                            //      = 7.29 in (185.2 mm)
// [flattened] EDF_BORE_R: value from its last assignment (override), kept at the first position
EDF_BORE_R      = P64_BORE_R;  // [mm] EDF bore inner radius → 50 mm (1.97 in) ID (Xfly Galaxy X5)
// [flattened] EDF_CASING_R: value from its last assignment (override), kept at the first position
EDF_CASING_R    = P64_BORE_R + P64_WALL;  // [mm] EDF casing outer radius → 55 mm (2.17 in) OD
WALL_T          =   2.5;  // [mm] minimum wall thickness — 0.098 in (2.5 mm) CF-PETG per CLAUDE.md

// ── Radial-scale and render hooks (2026-10-03, plan 2026-09-28-001 U9) ──────
// Identity here.  nacelle_pod_64mm_tandem.scad includes this file and sets
// RADIAL_K = 64/50 (owner decision: proportional radial scale about the thrust
// axis, axial stations fixed) and POD_AUTORENDER = false.  OpenSCAD's
// last-assignment-wins rule applies the override file-wide.  RADIAL_K scales
// the MEASURED shell, cavity and skin grids and the measured boss contour,
// never fasteners, boards or wall thicknesses.  Added by Claude (Claude Opus
// 5.5, Anthropic).
// [flattened] RADIAL_K: value from its last assignment (override), kept at the first position
RADIAL_K        = P64_K;   // [-] radial scale of the measured shell geometry
// [flattened] AXIAL_K: value from its last assignment (override), kept at the first position
AXIAL_K         = P64_A;   // [-] axial stretch of the measured shell geometry
                           //     (canonical silhouette kept; 64 mm wrapper)
// [flattened] POD_AUTORENDER: value from its last assignment (override), kept at the first position
POD_AUTORENDER = false;    // [bool] render nacelle_pod() at the end of this file
function radial_k_grid(g) = [ for (row = g) [ for (v = row) v * RADIAL_K ] ];
// Station list of the measured grids, stretched with the shell.
function hollow_zs() = [ for (z = HOLLOW_Z) z * AXIAL_K ];
// Cavity under a radially scaled skin: move the cavity surface out with the
// scaled skin so the WALL THICKNESS is unchanged (wall = structure, not
// silhouette).  cavity' = cavity + (K - 1) * skin.  Identity at K = 1.
function radial_k_cavity(cav, skin) =
    [ for (i = [0 : len(cav) - 1])
        [ for (j = [0 : len(cav[i]) - 1])
            cav[i][j] + (RADIAL_K - 1) * skin[i][j] ] ];

// ── Outer nacelle dimensions (canonical Serenity shape at 1.25× scale) ───────
// These are measured from the repaired STL bounding box.  They are provided for
// reference only; the actual shell geometry comes from the imported STL.
// [flattened] NACELLE_OD_X: value from its last assignment (override), kept at the first position
NACELLE_OD_X    = 75.4 * P64_K;  // [mm] nacelle bounding-box width, spanwise (X)  = 2.97 in
// [flattened] NACELLE_OD_Y: value from its last assignment (override), kept at the first position
NACELLE_OD_Y    = 83.3 * P64_K;  // [mm] nacelle bounding-box depth, fore-aft  (Y) = 3.28 in

// ── X-face positions at the pivot station (Z ≈ PIVOT_Z, Y ≈ 0) ───────────────
// Measured from the centered-bore repaired STL near Z≈104.5 mm, Y<5mm (the old
// gear-train pivot).  Rev T moves the pivot to Z=111.5 mm — VERIFY the 34/38 mm
// face heights at the new station (they change little over +7 mm; WBS §1.1.3).
// The Serenity nacelle is NOT a symmetric ellipse — pylon-attachment features
// make the pylon-side face narrower (+34mm) than the far side (-38mm).
// Used to guarantee the boss root is inside the nacelle wall.
// [flattened] NACELLE_FACE_X_PYLON: value from its last assignment (override), kept at the first position
NACELLE_FACE_X_PYLON = P64_FACE_PYLON;  // [mm] pylon-side X face from bore centre
// [flattened] NACELLE_FACE_X_FAR: value from its last assignment (override), kept at the first position
NACELLE_FACE_X_FAR   = 38.0 * P64_K;  // [mm] far-side   X face from bore centre

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
// [flattened] EDF1_Z_ENTRY: value from its last assignment (override), kept at the first position
EDF1_Z_ENTRY    = P64_ROTOR_Z;  // [mm] EDF1 forward face  (was 22.0 × 1.25)  = 1.08 in
// [flattened] EDF1_Z_EXIT: value from its last assignment (override), kept at the first position
EDF1_Z_EXIT     = P64_ROTOR_Z + P64_STAGE;  // [mm] EDF1 aft face      (was 72.0 × 1.25)  = 3.54 in
// [flattened] EDF2_Z_ENTRY: value from its last assignment (override), kept at the first position
EDF2_Z_ENTRY    = P64_ROTOR_Z + P64_STAGE + P64_GAP;  // [mm] EDF2 forward face  (was 98.0 × 1.25)  = 4.82 in
// [flattened] EDF2_Z_EXIT: value from its last assignment (override), kept at the first position
EDF2_Z_EXIT     = P64_ROTOR_Z + 2 * P64_STAGE + P64_GAP;  // [mm] EDF2 aft face      (was 143.0 × 1.25) = 7.04 in

// ── EDF motor-mount spider geometry (Rev T — shared by nacelle EDF1 spider
//    and aft sleeve EDF2 spider) ───────────────────────────────────────────────
// Hub bore sized for motor shaft clearance; motor pass-through not required.
// EDF1 spider (nacelle-integrated): M3 CLEARANCE bores on intake face.
//   Motor's own M3 female threads (standard RC motor) mate the screws.
//   Screws set from intake bore end with T-handle 2.5 mm hex key.
// EDF2 spider (aft spider sleeve): M3 heat-set inserts on nozzle face.
//   Screws from nozzle bore end after iris removed.
// ── Motor mount PATTERN — 4 screws at 90 deg (Rev T4c, 2026-09-01) ──────────
// CORRECTED on owner direction.  Both spiders mounted the motor on THREE arms at
// 120 deg with three M3 pockets.  The Xfly Galaxy X5 motor takes FOUR screws on
// a square pattern (REF-EDF-002, packing-list photo: four motor screws plus one
// longer spinner screw; hub is a disc with four round holes alternating with
// four slots).  Three holes at 120 deg cannot be made to coincide with four at
// 90 deg — this was a print-blocking defect, not a clearance one.
//
// CLOCKING 15/105/195/285 is not free choice.  A spider arm is the ONLY solid
// bridge from the annulus to the motor, so each ESC's phase bundle has to cross
// the bore wall AT an arm azimuth.  Measured on the canonical shell, azimuth 105
// and 285 are the pod's two deep lobes — the annulus survives aft to Z 163 at
// 6.2-6.4 mm depth there, against Z 135-147 elsewhere — and they are also where
// the two ESC bays land.  A 90 deg pattern can hold BOTH lobes at once, because
// 285 - 105 = 180 = 2 x 90; the old 120 deg pattern could not.  15 and 195 fall
// out of the spacing and land 15 deg clear of the sleeve key/retention angles
// (30/150/270), which sit at a different radius anyway.
//
// ** MOTOR_BOLT_R IS STILL UNVERIFIED and the owner direction does not settle
// it. ** The vendor listing publishes the screw COUNT but no bolt circle
// ("nc" on the manufacturer page).  10.0 mm is an assumption inherited from
// Rev R.  Measure the bolt circle off a physical motor before printing for
// flight — see the open item in airframe/wings-nacelles/WBS.md SS1.1.3.7.
N_SPIDER_ARMS   =   4;     // [count] motor mount arms — 4 screws at 90 deg
SPIDER_ARM_ANGLES = [15, 105, 195, 285];  // [deg] shared by BOTH spiders
SPIDER_ARM_H    =   8.0;   // [mm] arm axial thickness
SPIDER_ARM_W    =   6.0;   // [mm] arm tangential width
// [flattened] MOTOR_BOLT_R: value from its last assignment (override), kept at the first position
MOTOR_BOLT_R    =  8.0;   // [mm] M3 bolt circle radius — VERIFY vs actual motor
M3_INSERT_D     =   3.5;   // [mm] M3 × 6 mm OLF brass heat-set insert OD
M3_INSERT_L     =   6.0;   // [mm] heat-set insert depth
M3_CLEAR_D      =   3.3;   // [mm] M3 clearance bore diameter
// [flattened] R_HUB: value from its last assignment (override), kept at the first position
R_HUB           = 15.0;   // [mm] spider hub outer radius (16 mm OD)
R_HUB_BORE      =   2.0;   // [mm] spider hub bore radius   ( 4 mm ID, 3 mm shaft + 1 mm)

// ── Inter-stage stator geometry (echoed from sleeve files for EDF1_SPIDER_Z) ──
// [flattened] STATOR_Z_BOT: value from its last assignment (override), kept at the first position
STATOR_Z_BOT    = P64_ROTOR_Z + P64_SHAFT + P64_GAP;  // [mm] stator bottom Z (was 75.0 × 1.25)
// [flattened] STATOR_Z_TOP: value from its last assignment (override), kept at the first position
STATOR_Z_TOP    = P64_ROTOR_Z + P64_STAGE;  // [mm] stator top Z    (was 95.0 × 1.25)

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
// [flattened] NOZZLE_RING_Z: value from its last assignment (override), kept at the first position
NOZZLE_RING_Z   = P64_Z_NOZ;  // [mm] start Z of nozzle ring pocket (= CROWN_Z)
// [flattened] NOZZLE_RING_OD: value from its last assignment (override), kept at the first position
NOZZLE_RING_OD  = 72.0 * 1.21;   // [mm] pocket bore OD — Rev T (2026-07-18, Option B):
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
// [flattened] STATOR_SLV_Z_START: value from its last assignment (override), kept at the first position
STATOR_SLV_Z_START = P64_ROTOR_Z + P64_STAGE + P64_GAP / 2;    // = 90.0  mm
// [flattened] STATOR_SLV_Z_END: value from its last assignment (override), kept at the first position
STATOR_SLV_Z_END   = P64_ROTOR_Z + P64_STAGE + P64_GAP / 2;   // = 122.5 mm
// [flattened] AFT_SLV_Z_START: value from its last assignment (override), kept at the first position
AFT_SLV_Z_START    = P64_ROTOR_Z + P64_STAGE + P64_GAP / 2;   // = 122.5 mm
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
// [flattened] SLEEVE_KEY_ANGLES: value from its last assignment (override), kept at the first position
SLEEVE_KEY_ANGLES = [30, 150];

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
// [flattened] SLEEVE_BOSS_R: value from its last assignment (override), kept at the first position
SLEEVE_BOSS_R   = 28.0 * 1.21;  // [mm] boss centre radius
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
// [flattened] PIVOT_Z: value from its last assignment (override), kept at the first position
PIVOT_Z         = 109.7;   // [mm] pivot axial centre = full-assembly CG station
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
// [flattened] TRUNNION_X0: value from its last assignment (override), kept at the first position
TRUNNION_X0     = 28.2 + P64_AXIS_SHIFT;  // [mm] |X| of the spar tip = trunnion outboard face.
                           //      HARD BOUND, corrected 2026-08-31: the binding
                           //      radius here is NOT the r = 25 duct.  PIVOT_Z
                           //      lies inside the sleeve zone, where the bore is
                           //      SLEEVE_BORE_R (27.7) and the stator sleeve's
                           //      own OD is r 27.5.  At the old 26.7 the trunnion
                           //      and the spar both cut into the sleeve — a
                           //      measured 23.3 mm³ of solid overlap.  Gate T8.
// [flattened] WING_TIP_FACE_X: value from its last assignment (override), kept at the first position
WING_TIP_FACE_X = 41.7 + P64_AXIS_SHIFT + P64_STUB_EXTRA;  // [mm] |X| of the wing tip face = NACELLE_OD_X/2
                           //      (37.7) + the 4.0 mm joint gap
// [flattened] TRUNNION_REG_D: value from its last assignment (override), kept at the first position
TRUNNION_REG_D  = 38.1;  // [mm] H7 register bore — mates nacelle_trunnion.scad
                           //      REG_D 33.9
// [flattened] COLLAR_X0: value from its last assignment (override), kept at the first position
COLLAR_X0       = 28.2 + P64_AXIS_SHIFT + 12.5;   // = 32.2  register bore, outboard end
// [flattened] COLLAR_X1: value from its last assignment (override), kept at the first position
COLLAR_X1       = 28.2 + P64_AXIS_SHIFT + 14.0;   // = 35.7  flange seat rim face
// [flattened] COLLAR_OD: value from its last assignment (override), kept at the first position
COLLAR_OD       = 54.0;  // [mm] collar OD = trunnion flange OD
// [flattened] COLLAR_BOLT_D: value from its last assignment (override), kept at the first position
COLLAR_BOLT_D   = 45.5;  // [mm] 3 × M3 bolt circle (matches the trunnion)
// [flattened] COLLAR_FAIR_D: value from its last assignment (override), kept at the first position
COLLAR_FAIR_D   = 70.0;  // [mm] junction-fairing footprint diameter
// [flattened] COLLAR_FAIR_X: value from its last assignment (override), kept at the first position
COLLAR_FAIR_X   = 22.0 + P64_AXIS_SHIFT;  // [mm] |X| the fairing blends back to.  Everything
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
// [flattened] ESC_DISC_Z: value from its last assignment (override), kept at the first position
ESC_DISC_Z      = 51.0 * P64_A;  // [mm] bay centre, in the measured 7.10 mm window
// [flattened] ESC_DISC_Z_LO: value from its last assignment (override), kept at the first position
ESC_DISC_Z_LO   = 40.0 * P64_A + 1.5;  // [mm] measured-depth window the bay must stay in —
// [flattened] ESC_DISC_Z_HI: value from its last assignment (override), kept at the first position
ESC_DISC_Z_HI   = 62.0 * P64_A - 1.5;  //      asserted below; the 64 mm wrapper re-sites it
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
// [flattened] INLET_BELL_L: value from its last assignment (override), kept at the first position
INLET_BELL_L    = P64_LIP_A;   // [mm] inlet bell axial length (was 22.0 × 1.25)
// [flattened] INLET_BELL_FLARE: value from its last assignment (override), kept at the first position
INLET_BELL_FLARE= P64_LIP_F;   // [mm] extra flare radius at intake lip

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
// [flattened] NAV_LIGHT_Z: value from its last assignment (override), kept at the first position
NAV_LIGHT_Z     = 70.0 * P64_A;    // [mm] emitter Z station (forward third, wide side arc;
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
// ---- begin include <nacelle_hollow_profile.scad> (inlined by scad_flatten.py) ----
// =============================================================================
// nacelle_hollow_profile.scad — GENERATED FILE, DO NOT EDIT BY HAND
// =============================================================================
//
// Regenerate with:  /usr/bin/python3 tools/nacelle_hollow_profile.py --emit
//
// The internal cavity surface of the nacelle pod, measured off the canonical
// shell by ray-casting and offset inward by a FORWARD-BIASED wall schedule:
//     wall = 2.5 mm for Z <= 100, ramping to 8.0 mm by Z 140
// Removing more from the forward end moves the rotating-assembly CG AFT, which
// is where the tilt pivot sits, which shortens the pivot-to-nozzle arm and
// lifts the nozzle in hover.  See the tool's header for the measured trade.
//
// This file supplies ONLY the outer cavity surface as a ring grid.  The duct
// wall, the structural ribs and the trunnion keep-out are subtracted in
// nacelle_pod_50mm_tandem.scad, so the pod's own bore parameters stay
// authoritative and none of them is restated here.
//
// Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Generated by Claude (Claude Opus 5, Anthropic) under the author's direction,
// per AGENTS.md S3 'Attribution and Licensing'.
// License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
// =============================================================================

HOLLOW_N_AZ = 48;
HOLLOW_Z_START = 21.00;
HOLLOW_Z_END   = 162.00;
HOLLOW_Z = [21.00, 24.00, 27.00, 30.00, 33.00, 36.00, 39.00, 42.00, 45.00, 48.00, 51.00, 54.00, 57.00, 60.00, 63.00, 66.00, 69.00, 72.00, 75.00, 78.00, 81.00, 84.00, 87.00, 90.00, 93.00, 96.00, 99.00, 102.00, 105.00, 108.00, 111.00, 114.00, 117.00, 120.00, 123.00, 126.00, 129.00, 132.00, 135.00, 138.00, 141.00, 144.00, 147.00, 150.00, 153.00, 156.00, 159.00, 162.00];
HOLLOW_R_PORT = [
  [31.26,31.44,31.87,32.54,32.25,32.21,32.36,32.42,32.78,32.74,32.40,32.36,32.22,32.25,32.57,31.84,31.43,31.25,31.02,31.00,31.28,31.32,30.99,30.99,31.26,31.44,31.87,32.54,32.25,32.21,32.36,32.42,32.78,32.74,32.40,32.36,32.22,32.25,32.57,31.84,31.43,31.25,31.02,31.00,31.28,31.32,30.99,30.99],
  [32.45,32.63,33.07,33.70,33.40,33.37,33.51,33.57,33.93,33.82,33.48,33.44,33.26,33.28,33.63,32.82,32.39,32.19,31.95,31.94,32.07,32.49,32.19,32.19,32.45,32.63,33.07,33.70,33.40,33.37,33.51,33.57,33.93,33.82,33.48,33.44,33.26,33.28,33.63,32.82,32.39,32.19,31.95,31.94,32.07,32.49,32.19,32.19],
  [33.36,33.53,33.97,34.56,34.28,34.24,34.38,34.43,34.77,34.64,34.28,34.24,34.05,34.07,34.41,33.57,33.15,32.93,32.69,32.68,32.96,33.37,33.09,33.09,33.36,33.53,33.97,34.56,34.28,34.24,34.38,34.43,34.77,34.64,34.28,34.24,34.05,34.07,34.41,33.57,33.15,32.93,32.69,32.68,32.96,33.37,33.09,33.09],
  [33.95,34.08,34.51,35.02,34.75,34.72,34.82,34.88,35.24,35.07,34.72,34.68,34.49,34.51,34.80,34.07,33.64,33.46,33.22,33.21,33.60,33.94,33.69,33.69,33.95,34.08,34.51,35.02,34.75,34.72,34.82,34.88,35.24,35.07,34.72,34.68,34.49,34.51,34.80,34.07,33.64,33.46,33.22,33.21,33.60,33.94,33.69,33.69],
  [34.29,34.34,34.65,34.77,34.83,34.83,34.91,34.93,34.85,34.86,34.80,34.79,34.60,34.51,34.17,34.17,33.92,33.80,33.53,33.46,33.61,34.08,33.96,33.99,34.29,34.34,34.65,34.77,34.83,34.83,34.91,34.93,34.85,34.86,34.80,34.79,34.60,34.51,34.17,34.17,33.92,33.80,33.53,33.46,33.61,34.08,33.96,33.99],
  [34.16,34.17,33.19,33.20,34.42,34.46,34.51,34.49,32.93,33.16,34.39,34.43,34.24,34.09,32.85,32.82,33.81,33.85,33.55,33.53,33.13,33.13,33.93,33.95,34.16,34.17,33.19,33.20,34.42,34.46,34.51,34.49,32.93,33.16,34.39,34.43,34.24,34.09,32.85,32.82,33.81,33.85,33.55,33.53,33.13,33.13,33.93,33.95],
  [33.91,33.88,33.19,33.21,34.03,34.08,34.13,34.01,32.94,33.09,34.03,34.11,33.94,33.76,32.91,32.92,33.68,33.74,33.50,33.46,33.14,33.14,33.70,33.75,33.91,33.88,33.19,33.21,34.03,34.08,34.13,34.01,32.94,33.09,34.03,34.11,33.94,33.76,32.91,32.92,33.68,33.74,33.50,33.46,33.14,33.14,33.70,33.75],
  [33.58,33.60,33.55,33.57,33.77,33.78,33.83,33.84,33.54,33.58,33.87,33.88,33.83,33.82,33.34,33.37,33.67,33.69,33.51,33.50,33.31,33.32,33.43,33.46,33.58,33.60,33.55,33.57,33.77,33.78,33.83,33.84,33.54,33.58,33.87,33.88,33.83,33.82,33.34,33.37,33.67,33.69,33.51,33.50,33.31,33.32,33.43,33.46],
  [33.46,32.16,32.13,32.07,32.14,32.24,32.36,32.36,32.33,32.39,32.47,32.55,32.60,32.57,32.50,32.52,32.59,32.60,32.55,32.47,32.43,32.38,32.42,33.25,33.46,32.16,32.13,32.07,32.14,32.24,32.36,32.36,32.33,32.39,32.47,32.55,32.60,32.57,32.50,32.52,32.59,32.60,32.55,32.47,32.43,32.38,32.42,33.25],
  [33.92,30.12,30.13,30.06,29.91,29.91,29.81,29.82,29.82,29.90,30.03,30.02,30.27,30.32,30.20,30.27,30.31,30.27,30.34,30.37,30.37,30.29,30.43,33.96,33.92,30.12,30.13,30.06,29.91,29.91,29.81,29.82,29.82,29.90,30.03,30.02,30.27,30.32,30.20,30.27,30.31,30.27,30.34,30.37,30.37,30.29,30.43,33.96],
  [34.62,30.25,30.20,30.18,30.04,29.99,29.89,29.89,29.97,29.99,30.09,30.10,30.29,30.36,30.28,30.35,30.38,30.35,30.42,30.45,30.41,30.40,30.44,34.67,34.62,30.25,30.20,30.18,30.04,29.99,29.89,29.89,29.97,29.99,30.09,30.10,30.29,30.36,30.28,30.35,30.38,30.35,30.42,30.45,30.41,30.40,30.44,34.67],
  [34.60,33.21,33.05,33.13,33.16,33.14,33.12,33.17,33.18,33.19,33.24,33.18,33.16,33.20,33.18,33.17,33.14,33.09,33.15,33.19,33.14,33.13,33.21,34.74,34.60,33.21,33.05,33.13,33.16,33.14,33.12,33.17,33.18,33.19,33.24,33.18,33.16,33.20,33.18,33.17,33.14,33.09,33.15,33.19,33.14,33.13,33.21,34.74],
  [32.97,33.09,33.00,32.97,33.01,32.99,33.09,33.15,33.23,33.39,33.47,33.54,33.56,33.56,33.45,33.28,33.17,33.12,33.12,33.16,33.11,33.12,33.19,33.36,32.97,33.09,33.00,32.97,33.01,32.99,33.09,33.15,33.23,33.39,33.47,33.54,33.56,33.56,33.45,33.28,33.17,33.12,33.12,33.16,33.11,33.12,33.19,33.36],
  [32.66,33.01,32.93,32.89,32.90,32.93,33.14,33.15,33.29,34.27,34.78,34.70,34.70,34.74,34.55,33.55,33.35,33.29,33.21,33.25,33.23,33.15,33.21,32.53,32.66,33.01,32.93,32.89,32.90,32.93,33.14,33.15,33.29,34.27,34.78,34.70,34.70,34.74,34.55,33.55,33.35,33.29,33.21,33.25,33.23,33.15,33.21,32.53],
  [32.43,32.94,32.89,32.79,32.77,32.89,33.16,33.14,33.47,35.10,36.07,35.87,35.85,35.90,35.71,34.07,33.59,33.55,33.45,33.42,33.41,33.30,33.33,32.30,32.43,32.94,32.89,32.79,32.77,32.89,33.16,33.14,33.47,35.10,36.07,35.87,35.85,35.90,35.71,34.07,33.59,33.55,33.45,33.42,33.41,33.30,33.33,32.30],
  [34.19,32.00,32.35,32.38,31.65,31.85,32.81,31.99,32.28,34.61,36.87,36.71,36.68,36.71,36.69,33.63,32.99,33.21,33.00,32.64,33.04,32.65,32.39,34.26,34.19,32.00,32.35,32.38,31.65,31.85,32.81,31.99,32.28,34.61,36.87,36.71,36.68,36.71,36.69,33.63,32.99,33.21,33.00,32.64,33.04,32.65,32.39,34.26],
  [34.60,30.58,31.05,31.05,30.13,30.32,31.29,30.66,30.79,33.84,36.44,36.44,36.39,36.24,36.79,32.31,31.54,31.75,31.58,31.25,31.68,31.16,30.92,34.74,34.60,30.58,31.05,31.05,30.13,30.32,31.29,30.66,30.79,33.84,36.44,36.44,36.39,36.24,36.79,32.31,31.54,31.75,31.58,31.25,31.68,31.16,30.92,34.74],
  [34.60,30.96,31.57,31.35,30.43,30.66,31.69,30.93,31.09,34.18,36.64,36.49,36.46,36.30,36.81,32.68,31.79,31.96,31.84,31.52,32.01,31.44,31.18,34.74,34.60,30.96,31.57,31.35,30.43,30.66,31.69,30.93,31.09,34.18,36.64,36.49,36.46,36.30,36.81,32.68,31.79,31.96,31.84,31.52,32.01,31.44,31.18,34.74],
  [34.60,34.90,35.09,35.56,35.86,35.72,35.79,36.09,35.92,37.71,38.76,38.55,38.45,38.49,38.48,36.33,35.54,35.50,35.39,35.40,35.26,35.14,34.85,34.74,34.60,34.90,35.09,35.56,35.86,35.72,35.79,36.09,35.92,37.71,38.76,38.55,38.45,38.49,38.48,36.33,35.54,35.50,35.39,35.40,35.26,35.14,34.85,34.74],
  [34.93,35.26,35.67,35.90,36.09,36.23,36.39,36.48,36.96,38.39,38.17,37.34,37.26,37.40,38.53,36.77,36.08,35.95,35.87,35.87,35.79,35.59,35.36,34.78,34.93,35.26,35.67,35.90,36.09,36.23,36.39,36.48,36.96,38.39,38.17,37.34,37.26,37.40,38.53,36.77,36.08,35.95,35.87,35.87,35.79,35.59,35.36,34.78],
  [34.90,35.23,35.65,35.87,36.09,36.22,36.39,36.50,37.03,38.49,36.24,35.16,35.10,35.39,37.19,36.81,36.00,35.91,35.86,35.86,35.79,35.56,35.35,34.76,34.90,35.23,35.65,35.87,36.09,36.22,36.39,36.50,37.03,38.49,36.24,35.16,35.10,35.39,37.19,36.81,36.00,35.91,35.86,35.86,35.79,35.56,35.35,34.76],
  [34.88,35.21,35.64,35.87,36.10,36.22,36.39,36.51,37.05,38.46,35.10,34.01,33.95,34.22,36.32,36.86,35.99,35.86,35.85,35.85,35.79,35.55,35.35,34.74,34.88,35.21,35.64,35.87,36.10,36.22,36.39,36.51,37.05,38.46,35.10,34.01,33.95,34.22,36.32,36.86,35.99,35.86,35.85,35.85,35.79,35.55,35.35,34.74],
  [34.85,35.19,35.62,35.87,36.11,36.23,36.39,36.53,37.01,38.41,34.69,33.41,33.36,33.61,35.71,36.92,36.02,35.86,35.85,35.86,35.81,35.55,35.33,34.74,34.85,35.19,35.62,35.87,36.11,36.23,36.39,36.53,37.01,38.41,34.69,33.41,33.36,33.61,35.71,36.92,36.02,35.86,35.85,35.86,35.81,35.55,35.33,34.74],
  [34.82,35.18,35.58,35.87,38.48,36.34,36.39,36.54,36.96,38.38,34.81,33.44,33.36,33.58,35.85,36.98,36.08,35.91,35.90,35.89,35.83,35.56,35.33,34.75,34.82,35.18,35.58,35.87,38.48,36.34,36.39,36.54,36.96,38.38,34.81,33.44,33.36,33.58,35.85,36.98,36.08,35.91,35.90,35.89,35.83,35.56,35.33,34.75],
  [34.79,35.18,35.55,35.85,36.14,36.69,36.39,36.48,36.89,38.29,35.68,33.98,33.84,34.01,36.63,37.04,36.14,35.99,35.99,35.95,35.87,35.58,35.32,34.76,34.79,35.18,35.55,35.85,36.14,36.69,36.39,36.48,36.89,38.29,35.68,33.98,33.84,34.01,36.63,37.04,36.14,35.99,35.99,35.95,35.87,35.58,35.32,34.76],
  [34.77,35.19,35.53,35.84,38.03,36.66,36.40,36.41,36.81,38.08,37.69,36.27,36.14,36.31,38.23,37.10,36.23,36.09,36.07,36.03,35.91,35.60,35.32,34.75,34.77,35.19,35.53,35.84,38.03,36.66,36.40,36.41,36.81,38.08,37.69,36.27,36.14,36.31,38.23,37.10,36.23,36.09,36.07,36.03,35.91,35.60,35.32,34.75],
  [34.77,35.21,35.53,35.85,38.88,36.44,36.43,36.40,36.79,37.77,39.38,38.35,38.26,38.48,39.52,37.18,36.37,36.23,36.26,36.17,36.04,35.68,35.32,34.74,34.77,35.21,35.53,35.85,38.88,36.44,36.43,36.40,36.79,37.77,39.38,38.35,38.26,38.48,39.52,37.18,36.37,36.23,36.26,36.17,36.04,35.68,35.32,34.74],
  [34.36,34.93,35.26,35.69,35.97,36.22,36.26,36.15,36.50,37.20,39.19,38.66,38.57,38.81,39.02,36.96,36.28,36.18,36.30,36.13,35.94,35.52,35.04,34.47,34.36,34.93,35.26,35.69,35.97,36.22,36.26,36.15,36.50,37.20,39.19,38.66,38.57,38.81,39.02,36.96,36.28,36.18,36.30,36.13,35.94,35.52,35.04,34.47],
  [33.91,34.04,34.83,35.42,35.77,35.92,36.02,35.84,36.04,36.51,38.36,38.34,38.26,38.54,38.37,36.57,36.08,36.02,36.18,35.98,35.73,35.22,34.63,34.05,33.91,34.04,34.83,35.42,35.77,35.92,36.02,35.84,36.04,36.51,38.36,38.34,38.26,38.54,38.37,36.57,36.08,36.02,36.18,35.98,35.73,35.22,34.63,34.05],
  [33.50,32.88,34.44,35.12,35.55,35.69,35.69,35.57,35.52,35.85,37.56,37.77,37.71,37.99,37.71,36.06,35.89,35.89,36.00,35.87,35.47,34.87,34.20,33.64,33.50,32.88,34.44,35.12,35.55,35.69,35.69,35.57,35.52,35.85,37.56,37.77,37.71,37.99,37.71,36.06,35.89,35.89,36.00,35.87,35.47,34.87,34.20,33.64],
  [33.09,26.20,33.61,34.89,35.29,35.41,35.29,35.13,34.99,35.21,36.79,37.09,37.03,37.30,37.06,35.53,35.46,35.58,35.69,35.77,35.20,34.50,33.68,33.23,33.09,26.20,33.61,34.89,35.29,35.41,35.29,35.13,34.99,35.21,36.79,37.09,37.03,37.30,37.06,35.53,35.46,35.58,35.69,35.77,35.20,34.50,33.68,33.23],
  [32.28,26.20,26.20,34.75,35.01,35.31,34.96,34.64,34.49,34.60,36.01,36.41,36.35,36.61,36.41,35.07,35.03,35.22,35.45,35.68,34.94,34.11,33.18,32.52,32.28,26.20,26.20,34.75,35.01,35.31,34.96,34.64,34.49,34.60,36.01,36.41,36.35,36.61,36.41,35.07,35.03,35.22,35.45,35.68,34.94,34.11,33.18,32.52],
  [26.20,26.20,26.20,34.49,34.88,35.10,34.65,34.26,33.98,34.04,35.24,35.73,35.67,35.92,35.75,35.17,34.62,34.76,35.32,35.41,34.45,33.56,32.71,26.20,26.20,26.20,26.20,34.49,34.88,35.10,34.65,34.26,33.98,34.04,35.24,35.73,35.67,35.92,35.75,35.17,34.62,34.76,35.32,35.41,34.45,33.56,32.71,26.20],
  [26.20,26.20,26.20,32.30,34.62,34.48,33.97,33.60,33.33,33.39,34.61,35.05,34.99,35.22,35.09,34.51,33.89,34.03,34.41,34.61,33.64,32.84,32.23,26.20,26.20,26.20,26.20,32.30,34.62,34.48,33.97,33.60,33.33,33.39,34.61,35.05,34.99,35.22,35.09,34.51,33.89,34.03,34.41,34.61,33.64,32.84,32.23,26.20],
  [26.20,26.20,26.20,26.20,34.11,33.81,33.29,32.93,32.66,32.74,34.01,34.37,34.30,34.53,34.42,33.35,33.10,33.25,33.56,33.81,32.94,32.12,31.50,26.20,26.20,26.20,26.20,26.20,34.11,33.81,33.29,32.93,32.66,32.74,34.01,34.37,34.30,34.53,34.42,33.35,33.10,33.25,33.56,33.81,32.94,32.12,31.50,26.20],
  [26.20,26.20,26.20,26.20,33.60,33.12,32.61,32.24,31.99,32.08,33.41,33.69,33.62,33.84,33.77,32.65,32.31,32.47,32.79,32.95,32.34,31.39,26.20,26.20,26.20,26.20,26.20,26.20,33.60,33.12,32.61,32.24,31.99,32.08,33.41,33.69,33.62,33.84,33.77,32.65,32.31,32.47,32.79,32.95,32.34,31.39,26.20,26.20],
  [26.20,26.20,26.20,26.20,33.09,32.44,31.94,31.55,31.33,31.41,32.82,33.00,32.92,33.15,33.12,31.96,31.53,31.68,32.03,32.09,31.75,26.20,26.20,26.20,26.20,26.20,26.20,26.20,33.09,32.44,31.94,31.55,31.33,31.41,32.82,33.00,32.92,33.15,33.12,31.96,31.53,31.68,32.03,32.09,31.75,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20],
];
HOLLOW_R_STBD = [
  [31.27,31.00,30.99,31.36,31.29,31.00,31.02,31.24,31.43,31.83,32.57,32.24,32.22,32.36,32.40,32.74,32.78,32.42,32.36,32.21,32.23,32.54,31.88,31.44,31.27,31.00,30.99,31.36,31.29,31.00,31.02,31.24,31.43,31.83,32.57,32.24,32.22,32.36,32.40,32.74,32.78,32.42,32.36,32.21,32.23,32.54,31.88,31.44],
  [32.45,32.19,32.19,32.52,32.09,31.94,31.95,32.19,32.39,32.82,33.62,33.28,33.26,33.44,33.48,33.82,33.94,33.57,33.52,33.38,33.41,33.73,33.07,32.63,32.45,32.19,32.19,32.52,32.09,31.94,31.95,32.19,32.39,32.82,33.62,33.28,33.26,33.44,33.48,33.82,33.94,33.57,33.52,33.38,33.41,33.73,33.07,32.63],
  [33.36,33.12,33.10,33.37,32.95,32.68,32.69,32.93,33.15,33.57,34.41,34.08,34.05,34.25,34.28,34.63,34.77,34.42,34.36,34.24,34.27,34.54,33.97,33.53,33.36,33.12,33.10,33.37,32.95,32.68,32.69,32.93,33.15,33.57,34.41,34.08,34.05,34.25,34.28,34.63,34.77,34.42,34.36,34.24,34.27,34.54,33.97,33.53],
  [33.95,33.69,33.69,33.95,33.59,33.21,33.23,33.45,33.64,34.07,34.79,34.52,34.49,34.68,34.72,35.06,35.22,34.88,34.82,34.72,34.75,35.04,34.52,34.09,33.95,33.69,33.69,33.95,33.59,33.21,33.23,33.45,33.64,34.07,34.79,34.52,34.49,34.68,34.72,35.06,35.22,34.88,34.82,34.72,34.75,35.04,34.52,34.09],
  [34.27,33.99,33.96,34.10,33.59,33.46,33.53,33.78,33.92,34.15,34.15,34.52,34.61,34.79,34.81,34.84,34.84,34.93,34.91,34.84,34.84,34.73,34.62,34.35,34.27,33.99,33.96,34.10,33.59,33.46,33.53,33.78,33.92,34.15,34.15,34.52,34.61,34.79,34.81,34.84,34.84,34.93,34.91,34.84,34.84,34.73,34.62,34.35],
  [34.15,33.95,33.94,33.11,33.14,33.53,33.54,33.84,33.81,32.84,32.85,34.07,34.25,34.43,34.39,33.09,32.82,34.50,34.51,34.47,34.43,33.13,33.26,34.16,34.15,33.95,33.94,33.11,33.14,33.53,33.54,33.84,33.81,32.84,32.85,34.07,34.25,34.43,34.39,33.09,32.82,34.50,34.51,34.47,34.43,33.13,33.26,34.16],
  [33.92,33.76,33.71,33.15,33.16,33.47,33.48,33.74,33.67,32.93,32.90,33.75,33.95,34.11,34.04,33.00,32.84,34.01,34.13,34.08,34.01,33.12,33.21,33.89,33.92,33.76,33.71,33.15,33.16,33.47,33.48,33.74,33.67,32.93,32.90,33.75,33.95,34.11,34.04,33.00,32.84,34.01,34.13,34.08,34.01,33.12,33.21,33.89],
  [33.59,33.47,33.44,33.33,33.32,33.50,33.50,33.69,33.66,33.37,33.33,33.82,33.82,33.88,33.87,33.59,33.55,33.85,33.84,33.79,33.78,33.58,33.56,33.60,33.59,33.47,33.44,33.33,33.32,33.50,33.50,33.69,33.66,33.37,33.33,33.82,33.82,33.88,33.87,33.59,33.55,33.85,33.84,33.79,33.78,33.58,33.56,33.60],
  [33.46,33.34,32.41,32.38,32.43,32.47,32.55,32.59,32.58,32.52,32.50,32.56,32.59,32.55,32.47,32.39,32.32,32.36,32.36,32.24,32.14,32.07,32.12,32.23,33.46,33.34,32.41,32.38,32.43,32.47,32.55,32.59,32.58,32.52,32.50,32.56,32.59,32.55,32.47,32.39,32.32,32.36,32.36,32.24,32.14,32.07,32.12,32.23],
  [33.93,33.95,30.48,30.29,30.33,30.38,30.37,30.28,30.37,30.27,30.20,30.31,30.26,30.11,30.05,29.90,29.77,29.86,29.75,29.88,29.98,29.98,30.12,30.17,33.93,33.95,30.48,30.29,30.33,30.38,30.37,30.28,30.37,30.27,30.20,30.31,30.26,30.11,30.05,29.90,29.77,29.86,29.75,29.88,29.98,29.98,30.12,30.17],
  [34.63,34.68,30.55,30.38,30.42,30.43,30.41,30.37,30.40,30.35,30.28,30.36,30.29,30.19,30.10,30.00,29.88,29.95,29.88,30.01,30.07,30.12,30.24,30.24,34.63,34.68,30.55,30.38,30.42,30.43,30.41,30.37,30.40,30.35,30.28,30.36,30.29,30.19,30.10,30.00,29.88,29.95,29.88,30.01,30.07,30.12,30.24,30.24],
  [34.60,34.74,33.23,33.14,33.14,33.18,33.14,33.09,33.14,33.18,33.21,33.21,33.16,33.17,33.26,33.17,33.14,33.17,33.13,33.06,33.10,33.07,33.03,33.25,34.60,34.74,33.23,33.14,33.14,33.18,33.14,33.09,33.14,33.18,33.21,33.21,33.16,33.17,33.26,33.17,33.14,33.17,33.13,33.06,33.10,33.07,33.03,33.25],
  [33.04,33.50,33.21,33.13,33.11,33.17,33.13,33.12,33.18,33.29,33.45,33.55,33.55,33.56,33.48,33.40,33.22,33.14,33.09,32.99,33.00,32.96,33.00,33.06,33.04,33.50,33.21,33.13,33.11,33.17,33.13,33.12,33.18,33.29,33.45,33.55,33.55,33.56,33.48,33.40,33.22,33.14,33.09,32.99,33.00,32.96,33.00,33.06],
  [32.66,32.53,33.22,33.16,33.23,33.25,33.22,33.29,33.36,33.55,34.59,34.74,34.70,34.70,34.78,34.26,33.28,33.15,33.14,32.93,32.90,32.88,32.94,32.98,32.66,32.53,33.22,33.16,33.23,33.25,33.22,33.29,33.36,33.55,34.59,34.74,34.70,34.70,34.78,34.26,33.28,33.15,33.14,32.93,32.90,32.88,32.94,32.98],
  [32.44,32.30,33.32,33.31,33.42,33.43,33.46,33.55,33.59,34.08,35.78,35.90,35.85,35.87,36.06,35.05,33.47,33.13,33.15,32.88,32.76,32.78,32.90,32.89,32.44,32.30,33.32,33.31,33.42,33.43,33.46,33.55,33.59,34.08,35.78,35.90,35.85,35.87,36.06,35.05,33.47,33.13,33.15,32.88,32.76,32.78,32.90,32.89],
  [33.91,34.14,32.30,32.57,33.07,32.65,32.98,33.21,32.99,33.64,36.65,36.71,36.68,36.71,36.87,34.64,32.35,32.08,32.85,31.89,31.66,32.37,32.48,32.13,33.91,34.14,32.30,32.57,33.07,32.65,32.98,33.21,32.99,33.64,36.65,36.71,36.68,36.71,36.87,34.64,32.35,32.08,32.85,31.89,31.66,32.37,32.48,32.13],
  [34.61,34.75,30.88,31.12,31.64,31.22,31.60,31.71,31.54,32.33,36.78,36.24,36.43,36.50,36.44,33.81,30.82,30.68,31.33,30.31,30.19,31.11,31.04,30.73,34.61,34.75,30.88,31.12,31.64,31.22,31.60,31.71,31.54,32.33,36.78,36.24,36.43,36.50,36.44,33.81,30.82,30.68,31.33,30.31,30.19,31.11,31.04,30.73],
  [34.61,34.75,31.15,31.39,31.97,31.48,31.95,31.98,31.83,32.67,36.80,36.31,36.51,36.53,36.64,34.29,31.20,30.93,31.70,30.64,30.41,31.41,31.45,31.06,34.61,34.75,31.15,31.39,31.97,31.48,31.95,31.98,31.83,32.67,36.80,36.31,36.51,36.53,36.64,34.29,31.20,30.93,31.70,30.64,30.41,31.41,31.45,31.06],
  [34.73,34.75,35.00,35.15,35.34,35.39,35.37,35.53,35.63,36.31,38.51,38.49,38.45,38.56,38.71,37.70,36.02,35.94,36.24,35.85,35.83,35.61,35.34,34.97,34.73,34.75,35.00,35.15,35.34,35.39,35.37,35.53,35.63,36.31,38.51,38.49,38.45,38.56,38.71,37.70,36.02,35.94,36.24,35.85,35.83,35.61,35.34,34.97],
  [34.92,34.78,35.37,35.60,35.80,35.88,35.88,35.95,36.08,36.77,38.52,37.39,37.26,37.33,38.18,38.38,36.96,36.48,36.38,36.23,36.08,35.89,35.67,35.25,34.92,34.78,35.37,35.60,35.80,35.88,35.88,35.95,36.08,36.77,38.52,37.39,37.26,37.33,38.18,38.38,36.96,36.48,36.38,36.23,36.08,35.89,35.67,35.25],
  [34.90,34.76,35.36,35.57,35.79,35.87,35.86,35.91,36.01,36.80,37.20,35.38,35.10,35.16,36.26,38.48,37.03,36.49,36.38,36.22,36.08,35.87,35.65,35.22,34.90,34.76,35.36,35.57,35.79,35.87,35.86,35.91,36.01,36.80,37.20,35.38,35.10,35.16,36.26,38.48,37.03,36.49,36.38,36.22,36.08,35.87,35.65,35.22],
  [34.87,34.75,35.35,35.55,35.80,35.85,35.85,35.86,35.99,36.85,36.29,34.22,33.95,34.01,35.09,38.45,37.04,36.51,36.39,36.22,36.10,35.86,35.64,35.20,34.87,34.75,35.35,35.55,35.80,35.85,35.85,35.86,35.99,36.85,36.29,34.22,33.95,34.01,35.09,38.45,37.04,36.51,36.39,36.22,36.10,35.86,35.64,35.20],
  [34.84,34.75,35.34,35.55,35.81,35.86,35.85,35.86,36.03,36.91,35.69,33.62,33.37,33.41,34.69,38.41,37.01,36.52,36.39,36.22,36.11,35.87,35.62,35.19,34.84,34.75,35.34,35.55,35.81,35.86,35.85,35.86,36.03,36.91,35.69,33.62,33.37,33.41,34.69,38.41,37.01,36.52,36.39,36.22,36.11,35.87,35.62,35.19],
  [34.81,34.76,35.33,35.57,35.84,35.89,35.90,35.91,36.09,36.96,35.81,33.59,33.37,33.42,34.80,38.36,36.96,36.54,36.39,36.34,38.37,35.86,35.59,35.17,34.81,34.76,35.33,35.57,35.84,35.89,35.90,35.91,36.09,36.96,35.81,33.59,33.37,33.42,34.80,38.36,36.96,36.54,36.39,36.34,38.37,35.86,35.59,35.17],
  [34.78,34.77,35.33,35.59,35.87,35.96,35.99,35.99,36.15,37.02,36.69,34.03,33.84,33.98,35.68,38.28,36.88,36.47,36.39,36.70,36.13,35.85,35.55,35.17,34.78,34.77,35.33,35.59,35.87,35.96,35.99,35.99,36.15,37.02,36.69,34.03,33.84,33.98,35.68,38.28,36.88,36.47,36.39,36.70,36.13,35.85,35.55,35.17],
  [34.77,34.75,35.33,35.61,35.92,36.03,36.08,36.09,36.24,37.08,38.28,36.32,36.14,36.27,37.69,38.08,36.81,36.40,36.39,36.67,37.33,35.83,35.53,35.19,34.77,34.75,35.33,35.61,35.92,36.03,36.08,36.09,36.24,37.08,38.28,36.32,36.14,36.27,37.69,38.08,36.81,36.40,36.39,36.67,37.33,35.83,35.53,35.19],
  [34.77,34.75,35.32,35.68,36.02,36.17,36.26,36.23,36.37,37.19,39.51,38.46,38.26,38.35,39.36,37.76,36.79,36.39,36.43,36.43,38.64,35.84,35.53,35.21,34.77,34.75,35.32,35.68,36.02,36.17,36.26,36.23,36.37,37.19,39.51,38.46,38.26,38.35,39.36,37.76,36.79,36.39,36.43,36.43,38.64,35.84,35.53,35.21],
  [34.39,34.47,35.05,35.52,35.94,36.13,36.30,36.18,36.29,36.97,39.02,38.81,38.57,38.66,39.19,37.19,36.50,36.15,36.26,36.19,35.97,35.68,35.25,34.96,34.39,34.47,35.05,35.52,35.94,36.13,36.30,36.18,36.29,36.97,39.02,38.81,38.57,38.66,39.19,37.19,36.50,36.15,36.26,36.19,35.97,35.68,35.25,34.96],
  [33.92,34.06,34.64,35.21,35.73,35.98,36.18,36.02,36.08,36.58,38.37,38.54,38.26,38.33,38.37,36.51,36.04,35.83,36.02,35.91,35.77,35.41,34.80,34.15,33.92,34.06,34.64,35.21,35.73,35.98,36.18,36.02,36.08,36.58,38.37,38.54,38.26,38.33,38.37,36.51,36.04,35.83,36.02,35.91,35.77,35.41,34.80,34.15],
  [33.51,33.65,34.21,34.87,35.48,35.87,36.00,35.89,35.88,36.07,37.71,37.99,37.71,37.77,37.57,35.86,35.52,35.57,35.68,35.68,35.54,35.12,34.41,32.97,33.51,33.65,34.21,34.87,35.48,35.87,36.00,35.89,35.88,36.07,37.71,37.99,37.71,37.77,37.57,35.86,35.52,35.57,35.68,35.68,35.54,35.12,34.41,32.97],
  [33.09,33.23,33.68,34.50,35.21,35.78,35.71,35.59,35.46,35.54,37.07,37.30,37.03,37.09,36.78,35.21,34.99,35.13,35.28,35.39,35.29,34.85,33.81,26.20,33.09,33.23,33.68,34.50,35.21,35.78,35.71,35.59,35.46,35.54,37.07,37.30,37.03,37.09,36.78,35.21,34.99,35.13,35.28,35.39,35.29,34.85,33.81,26.20],
  [32.36,32.62,33.12,34.12,34.94,35.68,35.46,35.22,35.03,35.08,36.43,36.61,36.35,36.41,35.99,34.59,34.48,34.64,34.96,35.30,35.00,34.73,26.20,26.20,32.36,32.62,33.12,34.12,34.94,35.68,35.46,35.22,35.03,35.08,36.43,36.61,36.35,36.41,35.99,34.59,34.48,34.64,34.96,35.30,35.00,34.73,26.20,26.20],
  [26.20,26.20,32.67,33.57,34.45,35.42,35.31,34.76,34.62,34.84,35.79,35.92,35.67,35.73,35.23,34.04,33.98,34.26,34.65,35.09,34.88,34.59,26.20,26.20,26.20,26.20,32.67,33.57,34.45,35.42,35.31,34.76,34.62,34.84,35.79,35.92,35.67,35.73,35.23,34.04,33.98,34.26,34.65,35.09,34.88,34.59,26.20,26.20],
  [26.20,26.20,32.26,32.85,33.63,34.61,34.41,34.03,33.90,34.51,35.12,35.22,34.99,35.05,34.60,33.40,33.33,33.60,33.98,34.45,34.62,32.37,26.20,26.20,26.20,26.20,32.26,32.85,33.63,34.61,34.41,34.03,33.90,34.51,35.12,35.22,34.99,35.05,34.60,33.40,33.33,33.60,33.98,34.45,34.62,32.37,26.20,26.20],
  [26.20,26.20,31.60,32.11,32.95,33.81,33.58,33.25,33.10,33.34,34.44,34.53,34.30,34.37,34.01,32.74,32.65,32.92,33.28,33.78,34.10,26.20,26.20,26.20,26.20,26.20,31.60,32.11,32.95,33.81,33.58,33.25,33.10,33.34,34.44,34.53,34.30,34.37,34.01,32.74,32.65,32.92,33.28,33.78,34.10,26.20,26.20,26.20],
  [26.20,26.20,26.20,31.36,32.34,32.95,32.79,32.47,32.32,32.64,33.77,33.84,33.62,33.69,33.41,32.08,31.99,32.24,32.61,33.11,33.59,26.20,26.20,26.20,26.20,26.20,26.20,31.36,32.34,32.95,32.79,32.47,32.32,32.64,33.77,33.84,33.62,33.69,33.41,32.08,31.99,32.24,32.61,33.11,33.59,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,31.72,32.09,32.04,31.67,31.54,31.95,33.14,33.15,32.92,33.00,32.82,31.42,31.33,31.54,31.92,32.43,33.08,26.20,26.20,26.20,26.20,26.20,26.20,26.20,31.72,32.09,32.04,31.67,31.54,31.95,33.14,33.15,32.92,33.00,32.82,31.42,31.33,31.54,31.92,32.43,33.08,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20],
  [26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20,26.20],
];

// The OUTER SKIN itself, on the same grid.  The cavity grid above is this
// surface offset inward by the wall schedule, so it cannot be used to
// rebuild the mould line — the ESC access covers need the skin, because a
// cover that does not sit flush is a step in the boundary layer.
HOLLOW_SKIN_PORT = [
  [33.76,33.94,34.37,35.04,34.75,34.71,34.86,34.92,35.28,35.24,34.90,34.86,34.72,34.75,35.07,34.34,33.93,33.75,33.52,33.50,33.78,33.82,33.49,33.49,33.76,33.94,34.37,35.04,34.75,34.71,34.86,34.92,35.28,35.24,34.90,34.86,34.72,34.75,35.07,34.34,33.93,33.75,33.52,33.50,33.78,33.82,33.49,33.49],
  [34.95,35.13,35.57,36.20,35.90,35.87,36.01,36.07,36.43,36.32,35.98,35.94,35.76,35.78,36.13,35.32,34.89,34.69,34.45,34.44,34.57,34.99,34.69,34.69,34.95,35.13,35.57,36.20,35.90,35.87,36.01,36.07,36.43,36.32,35.98,35.94,35.76,35.78,36.13,35.32,34.89,34.69,34.45,34.44,34.57,34.99,34.69,34.69],
  [35.86,36.03,36.47,37.06,36.78,36.74,36.88,36.93,37.27,37.14,36.78,36.74,36.55,36.57,36.91,36.07,35.65,35.43,35.19,35.18,35.46,35.87,35.59,35.59,35.86,36.03,36.47,37.06,36.78,36.74,36.88,36.93,37.27,37.14,36.78,36.74,36.55,36.57,36.91,36.07,35.65,35.43,35.19,35.18,35.46,35.87,35.59,35.59],
  [36.45,36.58,37.01,37.52,37.25,37.22,37.32,37.38,37.74,37.57,37.22,37.18,36.99,37.01,37.30,36.57,36.14,35.96,35.72,35.71,36.10,36.44,36.19,36.19,36.45,36.58,37.01,37.52,37.25,37.22,37.32,37.38,37.74,37.57,37.22,37.18,36.99,37.01,37.30,36.57,36.14,35.96,35.72,35.71,36.10,36.44,36.19,36.19],
  [36.79,36.84,37.15,37.27,37.33,37.33,37.41,37.43,37.35,37.36,37.30,37.29,37.10,37.01,36.67,36.67,36.42,36.30,36.03,35.96,36.11,36.58,36.46,36.49,36.79,36.84,37.15,37.27,37.33,37.33,37.41,37.43,37.35,37.36,37.30,37.29,37.10,37.01,36.67,36.67,36.42,36.30,36.03,35.96,36.11,36.58,36.46,36.49],
  [36.66,36.67,35.69,35.70,36.92,36.96,37.01,36.99,35.43,35.66,36.89,36.93,36.74,36.59,35.35,35.32,36.31,36.35,36.05,36.03,35.63,35.63,36.43,36.45,36.66,36.67,35.69,35.70,36.92,36.96,37.01,36.99,35.43,35.66,36.89,36.93,36.74,36.59,35.35,35.32,36.31,36.35,36.05,36.03,35.63,35.63,36.43,36.45],
  [36.41,36.38,35.69,35.71,36.53,36.58,36.63,36.51,35.44,35.59,36.53,36.61,36.44,36.26,35.41,35.42,36.18,36.24,36.00,35.96,35.64,35.64,36.20,36.25,36.41,36.38,35.69,35.71,36.53,36.58,36.63,36.51,35.44,35.59,36.53,36.61,36.44,36.26,35.41,35.42,36.18,36.24,36.00,35.96,35.64,35.64,36.20,36.25],
  [36.08,36.10,36.05,36.07,36.27,36.28,36.33,36.34,36.04,36.08,36.37,36.38,36.33,36.32,35.84,35.87,36.17,36.19,36.01,36.00,35.81,35.82,35.93,35.96,36.08,36.10,36.05,36.07,36.27,36.28,36.33,36.34,36.04,36.08,36.37,36.38,36.33,36.32,35.84,35.87,36.17,36.19,36.01,36.00,35.81,35.82,35.93,35.96],
  [35.96,34.66,34.63,34.57,34.64,34.74,34.86,34.86,34.83,34.89,34.97,35.05,35.10,35.07,35.00,35.02,35.09,35.10,35.05,34.97,34.93,34.88,34.92,35.75,35.96,34.66,34.63,34.57,34.64,34.74,34.86,34.86,34.83,34.89,34.97,35.05,35.10,35.07,35.00,35.02,35.09,35.10,35.05,34.97,34.93,34.88,34.92,35.75],
  [36.42,32.62,32.63,32.56,32.41,32.41,32.31,32.32,32.32,32.40,32.53,32.52,32.77,32.82,32.70,32.77,32.81,32.77,32.84,32.87,32.87,32.79,32.93,36.46,36.42,32.62,32.63,32.56,32.41,32.41,32.31,32.32,32.32,32.40,32.53,32.52,32.77,32.82,32.70,32.77,32.81,32.77,32.84,32.87,32.87,32.79,32.93,36.46],
  [37.12,32.75,32.70,32.68,32.54,32.49,32.39,32.39,32.47,32.49,32.59,32.60,32.79,32.86,32.78,32.85,32.88,32.85,32.92,32.95,32.91,32.90,32.94,37.17,37.12,32.75,32.70,32.68,32.54,32.49,32.39,32.39,32.47,32.49,32.59,32.60,32.79,32.86,32.78,32.85,32.88,32.85,32.92,32.95,32.91,32.90,32.94,37.17],
  [37.10,35.71,35.55,35.63,35.66,35.64,35.62,35.67,35.68,35.69,35.74,35.68,35.66,35.70,35.68,35.67,35.64,35.59,35.65,35.69,35.64,35.63,35.71,37.24,37.10,35.71,35.55,35.63,35.66,35.64,35.62,35.67,35.68,35.69,35.74,35.68,35.66,35.70,35.68,35.67,35.64,35.59,35.65,35.69,35.64,35.63,35.71,37.24],
  [35.47,35.59,35.50,35.47,35.51,35.49,35.59,35.65,35.73,35.89,35.97,36.04,36.06,36.06,35.95,35.78,35.67,35.62,35.62,35.66,35.61,35.62,35.69,35.86,35.47,35.59,35.50,35.47,35.51,35.49,35.59,35.65,35.73,35.89,35.97,36.04,36.06,36.06,35.95,35.78,35.67,35.62,35.62,35.66,35.61,35.62,35.69,35.86],
  [35.16,35.51,35.43,35.39,35.40,35.43,35.64,35.65,35.79,36.77,37.28,37.20,37.20,37.24,37.05,36.05,35.85,35.79,35.71,35.75,35.73,35.65,35.71,35.03,35.16,35.51,35.43,35.39,35.40,35.43,35.64,35.65,35.79,36.77,37.28,37.20,37.20,37.24,37.05,36.05,35.85,35.79,35.71,35.75,35.73,35.65,35.71,35.03],
  [34.93,35.44,35.39,35.29,35.27,35.39,35.66,35.64,35.97,37.60,38.57,38.37,38.35,38.40,38.21,36.57,36.09,36.05,35.95,35.92,35.91,35.80,35.83,34.80,34.93,35.44,35.39,35.29,35.27,35.39,35.66,35.64,35.97,37.60,38.57,38.37,38.35,38.40,38.21,36.57,36.09,36.05,35.95,35.92,35.91,35.80,35.83,34.80],
  [36.69,34.50,34.85,34.88,34.15,34.35,35.31,34.49,34.78,37.11,39.37,39.21,39.18,39.21,39.19,36.13,35.49,35.71,35.50,35.14,35.54,35.15,34.89,36.76,36.69,34.50,34.85,34.88,34.15,34.35,35.31,34.49,34.78,37.11,39.37,39.21,39.18,39.21,39.19,36.13,35.49,35.71,35.50,35.14,35.54,35.15,34.89,36.76],
  [37.10,33.08,33.55,33.55,32.63,32.82,33.79,33.16,33.29,36.34,38.94,38.94,38.89,38.74,39.29,34.81,34.04,34.25,34.08,33.75,34.18,33.66,33.42,37.24,37.10,33.08,33.55,33.55,32.63,32.82,33.79,33.16,33.29,36.34,38.94,38.94,38.89,38.74,39.29,34.81,34.04,34.25,34.08,33.75,34.18,33.66,33.42,37.24],
  [37.10,33.46,34.07,33.85,32.93,33.16,34.19,33.43,33.59,36.68,39.14,38.99,38.96,38.80,39.31,35.18,34.29,34.46,34.34,34.02,34.51,33.94,33.68,37.24,37.10,33.46,34.07,33.85,32.93,33.16,34.19,33.43,33.59,36.68,39.14,38.99,38.96,38.80,39.31,35.18,34.29,34.46,34.34,34.02,34.51,33.94,33.68,37.24],
  [37.10,37.40,37.59,38.06,38.36,38.22,38.29,38.59,38.42,40.21,41.26,41.05,40.95,40.99,40.98,38.83,38.04,38.00,37.89,37.90,37.76,37.64,37.35,37.24,37.10,37.40,37.59,38.06,38.36,38.22,38.29,38.59,38.42,40.21,41.26,41.05,40.95,40.99,40.98,38.83,38.04,38.00,37.89,37.90,37.76,37.64,37.35,37.24],
  [37.43,37.76,38.17,38.40,38.59,38.73,38.89,38.98,39.46,40.89,40.67,39.84,39.76,39.90,41.03,39.27,38.58,38.45,38.37,38.37,38.29,38.09,37.86,37.28,37.43,37.76,38.17,38.40,38.59,38.73,38.89,38.98,39.46,40.89,40.67,39.84,39.76,39.90,41.03,39.27,38.58,38.45,38.37,38.37,38.29,38.09,37.86,37.28],
  [37.40,37.73,38.15,38.37,38.59,38.72,38.89,39.00,39.53,40.99,38.74,37.66,37.60,37.89,39.69,39.31,38.50,38.41,38.36,38.36,38.29,38.06,37.85,37.26,37.40,37.73,38.15,38.37,38.59,38.72,38.89,39.00,39.53,40.99,38.74,37.66,37.60,37.89,39.69,39.31,38.50,38.41,38.36,38.36,38.29,38.06,37.85,37.26],
  [37.38,37.71,38.14,38.37,38.60,38.72,38.89,39.01,39.55,40.96,37.60,36.51,36.45,36.72,38.82,39.36,38.49,38.36,38.35,38.35,38.29,38.05,37.85,37.24,37.38,37.71,38.14,38.37,38.60,38.72,38.89,39.01,39.55,40.96,37.60,36.51,36.45,36.72,38.82,39.36,38.49,38.36,38.35,38.35,38.29,38.05,37.85,37.24],
  [37.35,37.69,38.12,38.37,38.61,38.73,38.89,39.03,39.51,40.91,37.19,35.91,35.86,36.11,38.21,39.42,38.52,38.36,38.35,38.36,38.31,38.05,37.83,37.24,37.35,37.69,38.12,38.37,38.61,38.73,38.89,39.03,39.51,40.91,37.19,35.91,35.86,36.11,38.21,39.42,38.52,38.36,38.35,38.36,38.31,38.05,37.83,37.24],
  [37.32,37.68,38.08,38.37,40.98,38.84,38.89,39.04,39.46,40.88,37.31,35.94,35.86,36.08,38.35,39.48,38.58,38.41,38.40,38.39,38.33,38.06,37.83,37.25,37.32,37.68,38.08,38.37,40.98,38.84,38.89,39.04,39.46,40.88,37.31,35.94,35.86,36.08,38.35,39.48,38.58,38.41,38.40,38.39,38.33,38.06,37.83,37.25],
  [37.29,37.68,38.05,38.35,38.64,39.19,38.89,38.98,39.39,40.79,38.18,36.48,36.34,36.51,39.13,39.54,38.64,38.49,38.49,38.45,38.37,38.08,37.82,37.26,37.29,37.68,38.05,38.35,38.64,39.19,38.89,38.98,39.39,40.79,38.18,36.48,36.34,36.51,39.13,39.54,38.64,38.49,38.49,38.45,38.37,38.08,37.82,37.26],
  [37.27,37.69,38.03,38.34,40.53,39.16,38.90,38.91,39.31,40.58,40.19,38.77,38.64,38.81,40.73,39.60,38.73,38.59,38.57,38.53,38.41,38.10,37.82,37.25,37.27,37.69,38.03,38.34,40.53,39.16,38.90,38.91,39.31,40.58,40.19,38.77,38.64,38.81,40.73,39.60,38.73,38.59,38.57,38.53,38.41,38.10,37.82,37.25],
  [37.27,37.71,38.03,38.35,41.38,38.94,38.93,38.90,39.29,40.27,41.88,40.85,40.76,40.98,42.02,39.68,38.87,38.73,38.76,38.67,38.54,38.18,37.82,37.24,37.27,37.71,38.03,38.35,41.38,38.94,38.93,38.90,39.29,40.27,41.88,40.85,40.76,40.98,42.02,39.68,38.87,38.73,38.76,38.67,38.54,38.18,37.82,37.24],
  [37.13,37.71,38.03,38.46,38.75,38.99,39.03,38.93,39.28,39.97,41.96,41.43,41.34,41.59,41.79,39.74,39.06,38.95,39.07,38.90,38.72,38.30,37.81,37.24,37.13,37.71,38.03,38.46,38.75,38.99,39.03,38.93,39.28,39.97,41.96,41.43,41.34,41.59,41.79,39.74,39.06,38.95,39.07,38.90,38.72,38.30,37.81,37.24],
  [37.10,37.23,38.02,38.61,38.96,39.11,39.21,39.02,39.23,39.70,41.55,41.52,41.45,41.72,41.56,39.76,39.27,39.21,39.37,39.16,38.92,38.40,37.81,37.24,37.10,37.23,38.02,38.61,38.96,39.11,39.21,39.02,39.23,39.70,41.55,41.52,41.45,41.72,41.56,39.76,39.27,39.21,39.37,39.16,38.92,38.40,37.81,37.24],
  [37.10,36.48,38.04,38.72,39.15,39.29,39.29,39.17,39.12,39.45,41.16,41.37,41.31,41.59,41.31,39.66,39.49,39.49,39.60,39.47,39.07,38.47,37.80,37.24,37.10,36.48,38.04,38.72,39.15,39.29,39.29,39.17,39.12,39.45,41.16,41.37,41.31,41.59,41.31,39.66,39.49,39.49,39.60,39.47,39.07,38.47,37.80,37.24],
  [37.10,34.79,37.62,38.90,39.30,39.42,39.30,39.14,39.00,39.23,40.80,41.10,41.04,41.31,41.07,39.55,39.47,39.59,39.70,39.79,39.22,38.51,37.69,37.24,37.10,34.79,37.62,38.90,39.30,39.42,39.30,39.14,39.00,39.23,40.80,41.10,41.04,41.31,41.07,39.55,39.47,39.59,39.70,39.79,39.22,38.51,37.69,37.24],
  [36.70,34.08,35.55,39.18,39.43,39.74,39.39,39.07,38.91,39.02,40.43,40.83,40.77,41.04,40.83,39.49,39.45,39.65,39.87,40.10,39.36,38.53,37.61,36.95,36.70,34.08,35.55,39.18,39.43,39.74,39.39,39.07,38.91,39.02,40.43,40.83,40.77,41.04,40.83,39.49,39.45,39.65,39.87,40.10,39.36,38.53,37.61,36.95],
  [32.33,33.68,34.74,39.33,39.72,39.94,39.48,39.09,38.82,38.88,40.07,40.57,40.50,40.76,40.59,40.01,39.46,39.59,40.15,40.25,39.29,38.40,37.55,32.07,32.33,33.68,34.74,39.33,39.72,39.94,39.48,39.09,38.82,38.88,40.07,40.57,40.50,40.76,40.59,40.01,39.46,39.59,40.15,40.25,39.29,38.40,37.55,32.07],
  [32.26,33.58,34.48,37.55,39.87,39.73,39.22,38.85,38.58,38.64,39.86,40.30,40.24,40.47,40.34,39.76,39.14,39.28,39.66,39.86,38.89,38.09,37.48,32.00,32.26,33.58,34.48,37.55,39.87,39.73,39.22,38.85,38.58,38.64,39.86,40.30,40.24,40.47,40.34,39.76,39.14,39.28,39.66,39.86,38.89,38.09,37.48,32.00],
  [33.77,33.94,34.46,36.71,39.77,39.47,38.95,38.59,38.32,38.40,39.67,40.03,39.97,40.19,40.08,39.01,38.76,38.91,39.22,39.47,38.61,37.79,37.17,34.81,33.77,33.94,34.46,36.71,39.77,39.47,38.95,38.59,38.32,38.40,39.67,40.03,39.97,40.19,40.08,39.01,38.76,38.91,39.22,39.47,38.61,37.79,37.17,34.81],
  [37.10,34.43,34.45,36.54,39.67,39.19,38.69,38.31,38.07,38.15,39.49,39.76,39.69,39.91,39.85,38.72,38.38,38.54,38.86,39.03,38.42,37.47,37.01,37.21,37.10,34.43,34.45,36.54,39.67,39.19,38.69,38.31,38.07,38.15,39.49,39.76,39.69,39.91,39.85,38.72,38.38,38.54,38.86,39.03,38.42,37.47,37.01,37.21],
  [37.10,35.28,35.11,36.40,39.58,38.93,38.43,38.03,37.82,37.90,39.30,39.49,39.41,39.63,39.61,38.44,38.02,38.16,38.51,38.57,38.24,37.16,36.84,37.24,37.10,35.28,35.11,36.40,39.58,38.93,38.43,38.03,37.82,37.90,39.30,39.49,39.41,39.63,39.61,38.44,38.02,38.16,38.51,38.57,38.24,37.16,36.84,37.24],
  [37.31,35.86,35.78,36.28,39.49,38.62,38.06,37.68,37.58,37.66,39.11,39.21,39.13,39.35,39.41,38.17,37.68,37.73,38.04,38.16,37.89,37.00,36.64,37.36,37.31,35.86,35.78,36.28,39.49,38.62,38.06,37.68,37.58,37.66,39.11,39.21,39.13,39.35,39.41,38.17,37.68,37.73,38.04,38.16,37.89,37.00,36.64,37.36],
  [36.07,36.31,36.32,36.52,39.40,38.29,37.64,37.28,37.33,37.46,38.94,38.98,38.86,39.07,39.27,37.90,37.32,37.20,37.44,37.69,37.50,36.84,36.13,35.84,36.07,36.31,36.32,36.52,39.40,38.29,37.64,37.28,37.33,37.46,38.94,38.98,38.86,39.07,39.27,37.90,37.32,37.20,37.44,37.69,37.50,36.84,36.13,35.84],
  [35.64,36.15,36.75,37.23,39.30,37.98,37.23,36.92,36.98,37.27,38.77,38.76,38.61,38.79,39.18,37.25,36.93,36.72,36.84,37.20,37.14,36.68,35.61,35.31,35.64,36.15,36.75,37.23,39.30,37.98,37.23,36.92,36.98,37.27,38.77,38.76,38.61,38.79,39.18,37.25,36.93,36.72,36.84,37.20,37.14,36.68,35.61,35.31],
  [35.47,36.27,37.08,37.81,39.16,37.77,36.85,36.61,36.67,37.11,38.58,38.55,38.40,38.54,39.08,36.96,36.53,36.30,36.36,36.69,36.79,36.52,35.57,35.26,35.47,36.27,37.08,37.81,39.16,37.77,36.85,36.61,36.67,37.11,38.58,38.55,38.40,38.54,39.08,36.96,36.53,36.30,36.36,36.69,36.79,36.52,35.57,35.26],
  [34.55,34.93,35.11,35.39,38.65,37.17,36.47,36.31,36.36,36.91,38.39,38.33,38.18,38.32,38.85,36.69,36.12,35.92,35.97,36.11,36.25,36.21,35.41,34.30,34.55,34.93,35.11,35.39,38.65,37.17,36.47,36.31,36.36,36.91,38.39,38.33,38.18,38.32,38.85,36.69,36.12,35.92,35.97,36.11,36.25,36.21,35.41,34.30],
  [31.27,31.39,32.15,31.77,36.21,35.78,35.67,35.79,35.92,36.50,38.18,38.12,37.97,38.12,38.67,36.43,35.72,35.57,35.60,35.37,31.26,30.71,30.67,31.42,31.27,31.39,32.15,31.77,36.21,35.78,35.67,35.79,35.92,36.50,38.18,38.12,37.97,38.12,38.67,36.43,35.72,35.57,35.60,35.37,31.26,30.71,30.67,31.42],
  [30.78,31.07,31.99,31.21,31.53,33.47,34.51,34.87,35.23,36.00,37.85,37.91,37.76,37.94,38.50,36.21,35.37,34.84,30.10,30.29,30.70,30.40,30.42,31.42,30.78,31.07,31.99,31.21,31.53,33.47,34.51,34.87,35.23,36.00,37.85,37.91,37.76,37.94,38.50,36.21,35.37,34.84,30.10,30.29,30.70,30.40,30.42,31.42],
  [30.70,31.12,32.21,31.11,31.50,32.21,31.37,33.04,34.48,35.50,37.40,37.70,37.58,37.75,38.30,36.05,31.19,30.81,30.05,30.48,31.14,30.41,30.53,31.81,30.70,31.12,32.21,31.11,31.50,32.21,31.37,33.04,34.48,35.50,37.40,37.70,37.58,37.75,38.30,36.05,31.19,30.81,30.05,30.48,31.14,30.41,30.53,31.81],
  [30.71,31.21,32.22,31.12,31.66,32.13,31.28,32.05,32.42,34.58,36.83,37.44,37.30,37.43,37.96,30.76,31.12,30.85,30.20,30.60,31.36,30.42,30.57,31.93,30.71,31.21,32.22,31.12,31.66,32.13,31.28,32.05,32.42,34.58,36.83,37.44,37.30,37.43,37.96,30.76,31.12,30.85,30.20,30.60,31.36,30.42,30.57,31.93],
  [30.83,31.32,32.17,31.18,31.80,32.06,31.28,32.04,31.68,30.94,35.86,36.94,36.80,36.95,37.18,30.18,31.06,30.97,30.25,30.60,31.48,30.45,30.75,31.94,30.83,31.32,32.17,31.18,31.80,32.06,31.28,32.04,31.68,30.94,35.86,36.94,36.80,36.95,37.18,30.18,31.06,30.97,30.25,30.60,31.48,30.45,30.75,31.94],
  [31.21,31.59,32.13,31.10,31.92,32.00,31.32,32.05,31.61,30.93,31.88,36.03,35.86,36.03,31.55,30.20,31.01,31.11,30.29,30.60,31.59,30.72,31.12,31.96,31.21,31.59,32.13,31.10,31.92,32.00,31.32,32.05,31.61,30.93,31.88,36.03,35.86,36.03,31.55,30.20,31.01,31.11,30.29,30.60,31.59,30.72,31.12,31.96],
];
HOLLOW_SKIN_STBD = [
  [33.77,33.50,33.49,33.86,33.79,33.50,33.52,33.74,33.93,34.33,35.07,34.74,34.72,34.86,34.90,35.24,35.28,34.92,34.86,34.71,34.73,35.04,34.38,33.94,33.77,33.50,33.49,33.86,33.79,33.50,33.52,33.74,33.93,34.33,35.07,34.74,34.72,34.86,34.90,35.24,35.28,34.92,34.86,34.71,34.73,35.04,34.38,33.94],
  [34.95,34.69,34.69,35.02,34.59,34.44,34.45,34.69,34.89,35.32,36.12,35.78,35.76,35.94,35.98,36.32,36.44,36.07,36.02,35.88,35.91,36.23,35.57,35.13,34.95,34.69,34.69,35.02,34.59,34.44,34.45,34.69,34.89,35.32,36.12,35.78,35.76,35.94,35.98,36.32,36.44,36.07,36.02,35.88,35.91,36.23,35.57,35.13],
  [35.86,35.62,35.60,35.87,35.45,35.18,35.19,35.43,35.65,36.07,36.91,36.58,36.55,36.75,36.78,37.13,37.27,36.92,36.86,36.74,36.77,37.04,36.47,36.03,35.86,35.62,35.60,35.87,35.45,35.18,35.19,35.43,35.65,36.07,36.91,36.58,36.55,36.75,36.78,37.13,37.27,36.92,36.86,36.74,36.77,37.04,36.47,36.03],
  [36.45,36.19,36.19,36.45,36.09,35.71,35.73,35.95,36.14,36.57,37.29,37.02,36.99,37.18,37.22,37.56,37.72,37.38,37.32,37.22,37.25,37.54,37.02,36.59,36.45,36.19,36.19,36.45,36.09,35.71,35.73,35.95,36.14,36.57,37.29,37.02,36.99,37.18,37.22,37.56,37.72,37.38,37.32,37.22,37.25,37.54,37.02,36.59],
  [36.77,36.49,36.46,36.60,36.09,35.96,36.03,36.28,36.42,36.65,36.65,37.02,37.11,37.29,37.31,37.34,37.34,37.43,37.41,37.34,37.34,37.23,37.12,36.85,36.77,36.49,36.46,36.60,36.09,35.96,36.03,36.28,36.42,36.65,36.65,37.02,37.11,37.29,37.31,37.34,37.34,37.43,37.41,37.34,37.34,37.23,37.12,36.85],
  [36.65,36.45,36.44,35.61,35.64,36.03,36.04,36.34,36.31,35.34,35.35,36.57,36.75,36.93,36.89,35.59,35.32,37.00,37.01,36.97,36.93,35.63,35.76,36.66,36.65,36.45,36.44,35.61,35.64,36.03,36.04,36.34,36.31,35.34,35.35,36.57,36.75,36.93,36.89,35.59,35.32,37.00,37.01,36.97,36.93,35.63,35.76,36.66],
  [36.42,36.26,36.21,35.65,35.66,35.97,35.98,36.24,36.17,35.43,35.40,36.25,36.45,36.61,36.54,35.50,35.34,36.51,36.63,36.58,36.51,35.62,35.71,36.39,36.42,36.26,36.21,35.65,35.66,35.97,35.98,36.24,36.17,35.43,35.40,36.25,36.45,36.61,36.54,35.50,35.34,36.51,36.63,36.58,36.51,35.62,35.71,36.39],
  [36.09,35.97,35.94,35.83,35.82,36.00,36.00,36.19,36.16,35.87,35.83,36.32,36.32,36.38,36.37,36.09,36.05,36.35,36.34,36.29,36.28,36.08,36.06,36.10,36.09,35.97,35.94,35.83,35.82,36.00,36.00,36.19,36.16,35.87,35.83,36.32,36.32,36.38,36.37,36.09,36.05,36.35,36.34,36.29,36.28,36.08,36.06,36.10],
  [35.96,35.84,34.91,34.88,34.93,34.97,35.05,35.09,35.08,35.02,35.00,35.06,35.09,35.05,34.97,34.89,34.82,34.86,34.86,34.74,34.64,34.57,34.62,34.73,35.96,35.84,34.91,34.88,34.93,34.97,35.05,35.09,35.08,35.02,35.00,35.06,35.09,35.05,34.97,34.89,34.82,34.86,34.86,34.74,34.64,34.57,34.62,34.73],
  [36.43,36.45,32.98,32.79,32.83,32.88,32.87,32.78,32.87,32.77,32.70,32.81,32.76,32.61,32.55,32.40,32.27,32.36,32.25,32.38,32.48,32.48,32.62,32.67,36.43,36.45,32.98,32.79,32.83,32.88,32.87,32.78,32.87,32.77,32.70,32.81,32.76,32.61,32.55,32.40,32.27,32.36,32.25,32.38,32.48,32.48,32.62,32.67],
  [37.13,37.18,33.05,32.88,32.92,32.93,32.91,32.87,32.90,32.85,32.78,32.86,32.79,32.69,32.60,32.50,32.38,32.45,32.38,32.51,32.57,32.62,32.74,32.74,37.13,37.18,33.05,32.88,32.92,32.93,32.91,32.87,32.90,32.85,32.78,32.86,32.79,32.69,32.60,32.50,32.38,32.45,32.38,32.51,32.57,32.62,32.74,32.74],
  [37.10,37.24,35.73,35.64,35.64,35.68,35.64,35.59,35.64,35.68,35.71,35.71,35.66,35.67,35.76,35.67,35.64,35.67,35.63,35.56,35.60,35.57,35.53,35.75,37.10,37.24,35.73,35.64,35.64,35.68,35.64,35.59,35.64,35.68,35.71,35.71,35.66,35.67,35.76,35.67,35.64,35.67,35.63,35.56,35.60,35.57,35.53,35.75],
  [35.54,36.00,35.71,35.63,35.61,35.67,35.63,35.62,35.68,35.79,35.95,36.05,36.05,36.06,35.98,35.90,35.72,35.64,35.59,35.49,35.50,35.46,35.50,35.56,35.54,36.00,35.71,35.63,35.61,35.67,35.63,35.62,35.68,35.79,35.95,36.05,36.05,36.06,35.98,35.90,35.72,35.64,35.59,35.49,35.50,35.46,35.50,35.56],
  [35.16,35.03,35.72,35.66,35.73,35.75,35.72,35.79,35.86,36.05,37.09,37.24,37.20,37.20,37.28,36.76,35.78,35.65,35.64,35.43,35.40,35.38,35.44,35.48,35.16,35.03,35.72,35.66,35.73,35.75,35.72,35.79,35.86,36.05,37.09,37.24,37.20,37.20,37.28,36.76,35.78,35.65,35.64,35.43,35.40,35.38,35.44,35.48],
  [34.94,34.80,35.82,35.81,35.92,35.93,35.96,36.05,36.09,36.58,38.28,38.40,38.35,38.37,38.56,37.55,35.97,35.63,35.65,35.38,35.26,35.28,35.40,35.39,34.94,34.80,35.82,35.81,35.92,35.93,35.96,36.05,36.09,36.58,38.28,38.40,38.35,38.37,38.56,37.55,35.97,35.63,35.65,35.38,35.26,35.28,35.40,35.39],
  [36.41,36.64,34.80,35.07,35.57,35.15,35.48,35.71,35.49,36.14,39.15,39.21,39.18,39.21,39.37,37.14,34.85,34.58,35.35,34.39,34.16,34.87,34.98,34.63,36.41,36.64,34.80,35.07,35.57,35.15,35.48,35.71,35.49,36.14,39.15,39.21,39.18,39.21,39.37,37.14,34.85,34.58,35.35,34.39,34.16,34.87,34.98,34.63],
  [37.11,37.25,33.38,33.62,34.14,33.72,34.10,34.21,34.04,34.83,39.28,38.74,38.93,39.00,38.94,36.31,33.32,33.18,33.83,32.81,32.69,33.61,33.54,33.23,37.11,37.25,33.38,33.62,34.14,33.72,34.10,34.21,34.04,34.83,39.28,38.74,38.93,39.00,38.94,36.31,33.32,33.18,33.83,32.81,32.69,33.61,33.54,33.23],
  [37.11,37.25,33.65,33.89,34.47,33.98,34.45,34.48,34.33,35.17,39.30,38.81,39.01,39.03,39.14,36.79,33.70,33.43,34.20,33.14,32.91,33.91,33.95,33.56,37.11,37.25,33.65,33.89,34.47,33.98,34.45,34.48,34.33,35.17,39.30,38.81,39.01,39.03,39.14,36.79,33.70,33.43,34.20,33.14,32.91,33.91,33.95,33.56],
  [37.23,37.25,37.50,37.65,37.84,37.89,37.87,38.03,38.13,38.81,41.01,40.99,40.95,41.06,41.21,40.20,38.52,38.44,38.74,38.35,38.33,38.11,37.84,37.47,37.23,37.25,37.50,37.65,37.84,37.89,37.87,38.03,38.13,38.81,41.01,40.99,40.95,41.06,41.21,40.20,38.52,38.44,38.74,38.35,38.33,38.11,37.84,37.47],
  [37.42,37.28,37.87,38.10,38.30,38.38,38.38,38.45,38.58,39.27,41.02,39.89,39.76,39.83,40.68,40.88,39.46,38.98,38.88,38.73,38.58,38.39,38.17,37.75,37.42,37.28,37.87,38.10,38.30,38.38,38.38,38.45,38.58,39.27,41.02,39.89,39.76,39.83,40.68,40.88,39.46,38.98,38.88,38.73,38.58,38.39,38.17,37.75],
  [37.40,37.26,37.86,38.07,38.29,38.37,38.36,38.41,38.51,39.30,39.70,37.88,37.60,37.66,38.76,40.98,39.53,38.99,38.88,38.72,38.58,38.37,38.15,37.72,37.40,37.26,37.86,38.07,38.29,38.37,38.36,38.41,38.51,39.30,39.70,37.88,37.60,37.66,38.76,40.98,39.53,38.99,38.88,38.72,38.58,38.37,38.15,37.72],
  [37.37,37.25,37.85,38.05,38.30,38.35,38.35,38.36,38.49,39.35,38.79,36.72,36.45,36.51,37.59,40.95,39.54,39.01,38.89,38.72,38.60,38.36,38.14,37.70,37.37,37.25,37.85,38.05,38.30,38.35,38.35,38.36,38.49,39.35,38.79,36.72,36.45,36.51,37.59,40.95,39.54,39.01,38.89,38.72,38.60,38.36,38.14,37.70],
  [37.34,37.25,37.84,38.05,38.31,38.36,38.35,38.36,38.53,39.41,38.19,36.12,35.87,35.91,37.19,40.91,39.51,39.02,38.89,38.72,38.61,38.37,38.12,37.69,37.34,37.25,37.84,38.05,38.31,38.36,38.35,38.36,38.53,39.41,38.19,36.12,35.87,35.91,37.19,40.91,39.51,39.02,38.89,38.72,38.61,38.37,38.12,37.69],
  [37.31,37.26,37.83,38.07,38.34,38.39,38.40,38.41,38.59,39.46,38.31,36.09,35.87,35.92,37.30,40.86,39.46,39.04,38.89,38.84,40.87,38.36,38.09,37.67,37.31,37.26,37.83,38.07,38.34,38.39,38.40,38.41,38.59,39.46,38.31,36.09,35.87,35.92,37.30,40.86,39.46,39.04,38.89,38.84,40.87,38.36,38.09,37.67],
  [37.28,37.27,37.83,38.09,38.37,38.46,38.49,38.49,38.65,39.52,39.19,36.53,36.34,36.48,38.18,40.78,39.38,38.97,38.89,39.20,38.63,38.35,38.05,37.67,37.28,37.27,37.83,38.09,38.37,38.46,38.49,38.49,38.65,39.52,39.19,36.53,36.34,36.48,38.18,40.78,39.38,38.97,38.89,39.20,38.63,38.35,38.05,37.67],
  [37.27,37.25,37.83,38.11,38.42,38.53,38.58,38.59,38.74,39.58,40.78,38.82,38.64,38.77,40.19,40.58,39.31,38.90,38.89,39.17,39.83,38.33,38.03,37.69,37.27,37.25,37.83,38.11,38.42,38.53,38.58,38.59,38.74,39.58,40.78,38.82,38.64,38.77,40.19,40.58,39.31,38.90,38.89,39.17,39.83,38.33,38.03,37.69],
  [37.27,37.25,37.82,38.18,38.52,38.67,38.76,38.73,38.87,39.69,42.01,40.96,40.76,40.85,41.86,40.26,39.29,38.89,38.93,38.93,41.14,38.34,38.03,37.71,37.27,37.25,37.82,38.18,38.52,38.67,38.76,38.73,38.87,39.69,42.01,40.96,40.76,40.85,41.86,40.26,39.29,38.89,38.93,38.93,41.14,38.34,38.03,37.71],
  [37.16,37.25,37.82,38.30,38.71,38.91,39.08,38.96,39.06,39.74,41.79,41.59,41.34,41.43,41.97,39.97,39.28,38.92,39.03,38.97,38.75,38.46,38.03,37.73,37.16,37.25,37.82,38.30,38.71,38.91,39.08,38.96,39.06,39.74,41.79,41.59,41.34,41.43,41.97,39.97,39.28,38.92,39.03,38.97,38.75,38.46,38.03,37.73],
  [37.11,37.25,37.82,38.40,38.91,39.17,39.37,39.21,39.27,39.76,41.55,41.72,41.45,41.52,41.56,39.70,39.22,39.02,39.21,39.10,38.95,38.60,37.99,37.34,37.11,37.25,37.82,38.40,38.91,39.17,39.37,39.21,39.27,39.76,41.55,41.72,41.45,41.52,41.56,39.70,39.22,39.02,39.21,39.10,38.95,38.60,37.99,37.34],
  [37.11,37.25,37.81,38.47,39.08,39.47,39.60,39.49,39.48,39.67,41.31,41.59,41.31,41.37,41.17,39.46,39.12,39.17,39.28,39.28,39.14,38.72,38.01,36.57,37.11,37.25,37.81,38.47,39.08,39.47,39.60,39.49,39.48,39.67,41.31,41.59,41.31,41.37,41.17,39.46,39.12,39.17,39.28,39.28,39.14,38.72,38.01,36.57],
  [37.11,37.25,37.69,38.51,39.22,39.79,39.72,39.60,39.47,39.55,41.08,41.31,41.04,41.10,40.80,39.22,39.00,39.14,39.30,39.41,39.30,38.86,37.82,34.74,37.11,37.25,37.69,38.51,39.22,39.79,39.72,39.60,39.47,39.55,41.08,41.31,41.04,41.10,40.80,39.22,39.00,39.14,39.30,39.41,39.30,38.86,37.82,34.74],
  [36.78,37.05,37.54,38.54,39.37,40.11,39.88,39.65,39.46,39.50,40.86,41.03,40.77,40.83,40.42,39.02,38.91,39.06,39.39,39.73,39.43,39.15,35.57,34.08,36.78,37.05,37.54,38.54,39.37,40.11,39.88,39.65,39.46,39.50,40.86,41.03,40.77,40.83,40.42,39.02,38.91,39.06,39.39,39.73,39.43,39.15,35.57,34.08],
  [32.34,32.06,37.51,38.40,39.29,40.26,40.15,39.60,39.46,39.67,40.63,40.75,40.50,40.57,40.07,38.87,38.81,39.10,39.49,39.93,39.72,39.43,34.73,33.67,32.34,32.06,37.51,38.40,39.29,40.26,40.15,39.60,39.46,39.67,40.63,40.75,40.50,40.57,40.07,38.87,38.81,39.10,39.49,39.93,39.72,39.43,34.73,33.67],
  [32.25,32.00,37.51,38.10,38.88,39.86,39.66,39.28,39.15,39.76,40.37,40.47,40.24,40.30,39.85,38.65,38.58,38.85,39.23,39.70,39.87,37.62,34.49,33.60,32.25,32.00,37.51,38.10,38.88,39.86,39.66,39.28,39.15,39.76,40.37,40.47,40.24,40.30,39.85,38.65,38.58,38.85,39.23,39.70,39.87,37.62,34.49,33.60],
  [34.34,34.77,37.26,37.77,38.61,39.47,39.24,38.92,38.76,39.01,40.10,40.19,39.97,40.03,39.67,38.40,38.32,38.58,38.95,39.45,39.76,36.76,34.45,33.94,34.34,34.77,37.26,37.77,38.61,39.47,39.24,38.92,38.76,39.01,40.10,40.19,39.97,40.03,39.67,38.40,38.32,38.58,38.95,39.45,39.76,36.76,34.45,33.94],
  [37.07,37.21,37.08,37.43,38.42,39.03,38.87,38.55,38.39,38.72,39.85,39.91,39.69,39.76,39.49,38.16,38.06,38.31,38.68,39.19,39.66,36.56,34.44,34.52,37.07,37.21,37.08,37.43,38.42,39.03,38.87,38.55,38.39,38.72,39.85,39.91,39.69,39.76,39.49,38.16,38.06,38.31,38.68,39.19,39.66,36.56,34.44,34.52],
  [37.10,37.25,36.84,37.16,38.21,38.58,38.53,38.16,38.03,38.44,39.62,39.63,39.41,39.49,39.31,37.90,37.81,38.03,38.41,38.92,39.57,36.40,35.11,35.24,37.10,37.25,36.84,37.16,38.21,38.58,38.53,38.16,38.03,38.44,39.62,39.63,39.41,39.49,39.31,37.90,37.81,38.03,38.41,38.92,39.57,36.40,35.11,35.24],
  [37.31,37.36,36.63,37.00,37.89,38.17,38.05,37.73,37.68,38.16,39.41,39.35,39.13,39.21,39.12,37.66,37.57,37.68,38.04,38.62,39.48,36.28,35.79,35.98,37.31,37.36,36.63,37.00,37.89,38.17,38.05,37.73,37.68,38.16,39.41,39.35,39.13,39.21,39.12,37.66,37.57,37.68,38.04,38.62,39.48,36.28,35.79,35.98],
  [36.07,35.84,36.14,36.85,37.51,37.69,37.44,37.20,37.33,37.91,39.27,39.07,38.86,38.97,38.95,37.45,37.33,37.28,37.63,38.29,39.39,36.53,36.32,36.31,36.07,35.84,36.14,36.85,37.51,37.69,37.44,37.20,37.33,37.91,39.27,39.07,38.86,38.97,38.95,37.45,37.33,37.28,37.63,38.29,39.39,36.53,36.32,36.31],
  [35.66,35.29,35.61,36.69,37.14,37.20,36.85,36.73,36.94,37.25,39.17,38.79,38.61,38.76,38.77,37.28,36.97,36.91,37.23,37.98,39.30,37.26,36.76,36.17,35.66,35.29,35.61,36.69,37.14,37.20,36.85,36.73,36.94,37.25,39.17,38.79,38.61,38.76,38.77,37.28,36.97,36.91,37.23,37.98,39.30,37.26,36.76,36.17],
  [35.46,35.24,35.58,36.53,36.79,36.69,36.36,36.31,36.53,36.98,39.05,38.54,38.40,38.55,38.58,37.09,36.66,36.61,36.84,37.77,39.17,37.82,37.09,36.27,35.46,35.24,35.58,36.53,36.79,36.69,36.36,36.31,36.53,36.98,39.05,38.54,38.40,38.55,38.58,37.09,36.66,36.61,36.84,37.77,39.17,37.82,37.09,36.27],
  [34.84,34.68,35.30,36.20,36.27,36.11,35.97,35.92,36.12,36.71,38.85,38.32,38.18,38.33,38.39,36.90,36.35,36.30,36.49,37.20,38.72,35.41,35.19,34.84,34.84,34.68,35.30,36.20,36.27,36.11,35.97,35.92,36.12,36.71,38.85,38.32,38.18,38.33,38.39,36.90,36.35,36.30,36.49,37.20,38.72,35.41,35.19,34.84],
  [31.31,31.49,30.77,30.68,31.26,35.45,35.57,35.57,35.72,36.45,38.67,38.12,37.97,38.12,38.18,36.50,35.91,35.78,35.65,35.75,36.19,31.80,32.20,31.47,31.31,31.49,30.77,30.68,31.26,35.45,35.57,35.57,35.72,36.45,38.67,38.12,37.97,38.12,38.18,36.50,35.91,35.78,35.65,35.75,36.19,31.80,32.20,31.47],
  [30.88,31.48,30.44,30.36,30.96,30.23,30.11,34.67,35.36,36.21,38.50,37.94,37.76,37.91,37.84,36.00,35.25,34.88,34.54,33.72,31.64,31.28,32.01,31.10,30.88,31.48,30.44,30.36,30.96,30.23,30.11,34.67,35.36,36.21,38.50,37.94,37.76,37.91,37.84,36.00,35.25,34.88,34.54,33.72,31.64,31.28,32.01,31.10],
  [30.68,31.80,30.54,30.38,31.14,30.48,30.07,30.82,34.96,36.02,38.31,37.75,37.58,37.70,37.42,35.50,34.49,32.96,31.29,32.18,31.64,31.19,32.23,31.08,30.68,31.80,30.54,30.38,31.14,30.48,30.07,30.82,34.96,36.02,38.31,37.75,37.58,37.70,37.42,35.50,34.49,32.96,31.29,32.18,31.64,31.19,32.23,31.08],
  [30.69,31.92,30.64,30.40,31.37,30.59,30.15,30.85,31.12,30.74,37.96,37.43,37.30,37.44,36.84,34.59,32.28,32.00,31.24,32.10,31.69,31.19,32.23,31.15,30.69,31.92,30.64,30.40,31.37,30.59,30.15,30.85,31.12,30.74,37.96,37.43,37.30,37.44,36.84,34.59,32.28,32.00,31.24,32.10,31.69,31.19,32.23,31.15],
  [30.97,31.93,30.77,30.48,31.49,30.58,30.22,30.95,31.05,30.30,37.18,36.95,36.80,36.94,35.92,30.68,31.77,31.99,31.23,32.03,31.80,31.06,32.19,31.33,30.97,31.93,30.77,30.48,31.49,30.58,30.22,30.95,31.05,30.30,37.18,36.95,36.80,36.94,35.92,30.68,31.77,31.99,31.23,32.03,31.80,31.06,32.19,31.33],
  [31.14,31.95,31.15,30.80,31.59,30.58,30.26,31.12,30.99,30.30,31.53,36.03,35.86,36.03,31.86,30.68,31.65,31.97,31.26,31.99,31.91,30.92,32.16,31.55,31.14,31.95,31.15,30.80,31.59,30.58,30.26,31.12,30.99,30.30,31.53,36.03,35.86,36.03,31.86,30.68,31.65,31.97,31.26,31.99,31.91,30.92,32.16,31.55],
];
// ---- end include <nacelle_hollow_profile.scad> ----

use <nacelle_shell_grid.scad>

CAVITY_DUCT_WALL  =  2.5;  // [mm] wall left on the duct side of the cavity
// Structural bulkheads.  A hollow shell with a duct tube inside it and no shear
// connection between them is a far weaker beam than the solid it replaces, and
// the pod is the beam that carries EDF thrust and nacelle inertia into the
// trunnion.  Three full annular webs forward of the trunnion restore the shear
// path; aft of it the 8 mm wall and the trunnion keep-out are already solid.
// Rev T4c (2026-09-01): 84.0 -> 70.0 and a fourth web added at 138.0.  The ESC
// bays run Z 74-134, so a web at 84 would be cut away over 2 x 60 deg of its
// circumference by the two bay pockets plus another 50 deg by the disconnect
// bay — barely half a web, in the middle of the span it exists to stiffen.
// Moved just FORWARD of the bays instead, with a fourth picked up just AFT of
// them.  The 138 web costs almost nothing: the wall is already at 8 mm there so
// the cavity, and therefore the web, is nearly closed.
// [flattened] CAVITY_BULKHEAD_Z: value from its last assignment (override), kept at the first position
CAVITY_BULKHEAD_Z = [40.0 * P64_A, 62.0 * P64_A,
                     95.0 * P64_A - 21.0 - 8.0 - 4.0,     // = 74.35
                     95.0 * P64_A + 21.0 + 8.0 + 3.5];
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
// [flattened] CAVITY_VENT_R: value from its last assignment (override), kept at the first position
CAVITY_VENT_R   = 30.0 * P64_K;  // [mm] hole centre radius — inside the annulus at all
                           //      three web stations (measured: 27.5..33.1 at
                           //      Z 40, 27.5..34.5 at Z 84)
// Trunnion keep-out: solid material must survive around the collar, which is
// additive in Zone A and would otherwise be hollowed out from behind.
CAVITY_TRUNNION_R  = 30.0; // [mm] radius about the SPAR axis
// [flattened] CAVITY_TRUNNION_X0: value from its last assignment (override), kept at the first position
CAVITY_TRUNNION_X0 = 20.0 + P64_AXIS_SHIFT; // [mm] |X| the keep-out starts at
// [flattened] CAVITY_TRUNNION_X1: value from its last assignment (override), kept at the first position
CAVITY_TRUNNION_X1 = 40.0 + P64_AXIS_SHIFT + P64_STUB_EXTRA; // [mm] |X| it ends at

// ── Hinged ESC bays (Rev T4c, 2026-09-01) ───────────────────────────────────
// Every dimension the pod and the access covers must agree on lives in ONE file,
// because they are two parts that have to match a third thing — the hole between
// them.  The cover was briefly built from the wrong shell and dropped 442 mm3 of
// itself inside the pod; that was a selector error, but duplicated parameters
// are how the same class of mistake becomes permanent.
// ---- begin include <nacelle_esc_bay.scad> (inlined by scad_flatten.py) ----
// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Nacelle-local print frame: duct axis = local +Z, intake at Z = 0, azimuth
//   measured from local +X.  Consumed by nacelle_pod_50mm_tandem.scad and by
//   nacelle_esc_cover.scad, which must agree on every number in this file or
//   the cover will not fit the hole it covers.
// ===========================================================================
// =============================================================================
// nacelle_esc_bay.scad — the hinged-ESC bay interface, defined once
// =============================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Analysis and code by Claude (Claude Opus 5, Anthropic) under the author's
//           direction, per AGENTS.md §3 "Attribution and Licensing"
// License : CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
// Date    : 2026-09-01  (Rev T4c)
//
// THE BOARD — owner direction, 2026-09-01
// ---------------------------------------
// Each of the two ESCs in a nacelle is TWO PCBs joined by a hinge:
//     power panel   23.0 mm
//     signal panel  10.0 mm
//     total         33.0 mm across the fold
//
// The hinge exists because the board cannot narrow.  32 mm is the floor set by
// Open-Secure-ESC's own `isolation_envelope.py` — 12.90 mm widest non-isolated
// part + 2 × (7.5 mm creepage + 1.43 mm inset) + 2 × 0.55 mm = 31.86 mm, off the
// ADM2582E/ADM2587E Table 6 clearance — and this pod's annulus is about 7 mm
// deep.  Folding does not make the board smaller; it makes its DEVIATION FROM
// THE ARC smaller, and that is the dimension the pod is short of.  Sagitta of a
// chord of width w on a circle of radius R is R − sqrt(R² − (w/2)²); at R 33:
//
//     one flat 33.0 mm board   4.42 mm   — 63 % of the annulus, gone
//     23.0 mm power panel      2.07 mm
//     10.0 mm signal panel     0.38 mm
//
// MEASURED FIT — tools/nacelle_esc_bay_fit.py.  That tool tests the OUTER
// CORNERS of each panel against the ray-cast skin, at radius
// sqrt(d_out² + (w/2)²) and azimuth φ ± atan((w/2)/d_out).  The corners are
// always the binding points, never the panel centre, which is why an earlier
// model that sized the bay as an annular SECTOR concluded the board should be
// wide and short — the exact opposite of the truth.
//
//     stack   length   Z span     area    vs as-built 32.0 × 66.1 = 2115 mm²
//     3.0 mm   74 mm   74–146   2442 mm²   115 %
//     3.5 mm   68 mm   74–140   2244 mm²   106 %
//     4.0 mm   62 mm   74–134   2046 mm²    97 %   <- BUILT
//     4.5 mm   58 mm   74–130   1914 mm²    91 %
//     5.0 mm   50 mm   74–122   1650 mm²    78 %
//     6.0 mm   16 mm   74– 88    528 mm²    25 %
//
// 4.0 mm is the stack: 1.6 mm of PCB leaves 2.4 mm for components across both
// faces plus mounting.
//
// THE RADIAL BUDGET — corrected 2026-09-06, and the correction costs 18 mm
// ------------------------------------------------------------------------
// The 62 mm figure was wrong, and it was wrong because the fit search tested the
// board against a 2.5 mm skin wall while the COVER is a separate part occupying
// its own thickness in the same space.  Everything between the seat and the
// canonical skin comes out of one budget, and the board's outer CORNERS bind:
//
//     seat R 30.2
//       + component stack        4.0
//       + cooling flow lane      1.0     <- did not exist in the first sizing
//       + cover                  2.5
//       + running clearance      0.4
//     = 7.9 mm to the skin
//
// Every millimetre of that comes straight off the board's LENGTH, because the
// bay runs out of depth before it runs out of length:
//
//     stack  lane  cover      length    area   vs COTS 2115 mm²
//      3.0   0.0    2.5        70 mm   2310     109 %
//      3.5   0.0    2.5        62 mm   2046      97 %   <- what was claimed
//      4.0   0.0    2.5        56 mm   1848      87 %
//      3.5   1.0    2.5        52 mm   1716      81 %
//      4.0   1.0    2.5        44 mm   1452      69 %   <- BUILT
//      4.0   1.0    3.0        16 mm    528      25 %
//
// **The 3.0 mm cover was costing 28 mm of board on its own** — hence the drop to
// the 2.5 mm minimum and a proud screw head.
//
// TWO WAYS TO GET THE LENGTH BACK, and both belong to the board rather than the
// airframe:
//   * `ESC_FLOW_LANE = 0` if the ESC layout guarantees a 1 mm clear lane along
//     its own length between components — the airframe then need not reserve it,
//     and the board returns to 56 mm.
//   * a 3.5 mm stack instead of 4.0 returns it to 52 mm.
// Neither is the airframe's to decide; both are recorded so the choice is
// visible.
// =============================================================================

ESC_BAY_AZ      = [68, 248];  // [deg] hinge azimuth of each bay.  NOT free: 105
                              //   and 285 are the pod's two DEEP LOBES (annulus
                              //   alive aft to Z 163 at 6.2–6.4 mm, against
                              //   Z 135–147 elsewhere) and are where the EDF
                              //   spider arms are clocked, so each bay sits
                              //   directly over its own phase-lead crossing with
                              //   no circumferential run.  Also clear of the nav
                              //   cableway (az 0) and of the trunnion and
                              //   disconnect bay (az 180).
ESC_W_POWER     =  23.0;  // [mm] power panel width   (owner direction)
ESC_W_SIGNAL    =  10.0;  // [mm] signal panel width  (owner direction)
ESC_PCB_T       =   1.6;  // [mm] PCB thickness
ESC_STACK       =   4.0;  // [mm] radial envelope: PCB + parts both faces + mount
// [flattened] ESC_MOUNT_R: value from its last assignment (override), kept at the first position
ESC_MOUNT_R     = P64_BORE_R + P64_WALL + 0.2 + P64_WALL;  // [mm] board inner face — equals the pod's
                          //   SLEEVE_BORE_R + CAVITY_DUCT_WALL, asserted there
// [flattened] ESC_BAY_Z0: value from its last assignment (override), kept at the first position
ESC_BAY_Z0      = 95.0 * P64_A - 21.0;  // [mm] bay forward end
// [flattened] ESC_BAY_Z1: value from its last assignment (override), kept at the first position
ESC_BAY_Z1      = 95.0 * P64_A + 21.0;  // [mm] bay aft end — 44 mm of board.  This was 134
                          //   (62 mm) until 2026-09-06, and the 18 mm came off
                          //   for two reasons that had both been missed; see
                          //   THE RADIAL BUDGET below.
ESC_FLOW_LANE   =   1.0;  // [mm] clear lane above the component stack, for the
                          //   cooling air.  Set this to 0 and the board grows
                          //   back to 56 mm — see the trade below.
ESC_FIT         =   0.6;  // [mm] clearance per side around the board

// ── Access ───────────────────────────────────────────────────────────────────
// A board 33 mm across the fold cannot be threaded into a sealed annulus, so
// each bay is cut RADIALLY THROUGH THE SKIN and closed by a printed cover that
// drops into a rebate and finishes flush with the mould line.  The window is the
// union of the two panel footprints, so it is chevron-shaped and follows the
// fold — a rectangular window would either foul the fold or waste skin.
ESC_COVER_T     =   2.5;  // [mm] cover thickness — the repo minimum wall, and
                          //   every 0.5 mm above it costs ~10 mm of board
                          //   LENGTH (see the radial budget).  The M3 button
                          //   head therefore sits 0.65 mm proud rather than
                          //   flush; see ESC_CBORE_DEPTH.
ESC_LEDGE_W     =   8.0;  // [mm] cover landing band around the window
ESC_LEDGE_T     =   2.5;  // [mm] material under the cover, radially
ESC_COVER_FIT   =   0.25; // [mm] clearance per side, cover into its rebate
ESC_BOSS_OD     =   7.0;  // [mm] insert boss OD
ESC_BOSS_INSET  =   4.0;  // [mm] boss centre inset from the window edge
ESC_SCREW_D     =   3.4;  // [mm] M3 clearance through the cover
ESC_CBORE_D     =   6.2;  // [mm] counterbore for an M3 BUTTON head (Ø5.7×1.65)
ESC_CBORE_DEPTH =   1.0;  // [mm] counterbore depth.  An M3 button head is
                          //   1.65 mm tall, so it stands 0.65 mm PROUD — a
                          //   deliberate, quantified deviation.  Sinking it
                          //   flush would need a 3.0 mm cover, and that costs
                          //   ~10 mm of board length; 0.65 mm of screw head is
                          //   the cheaper of the two, on a nacelle that already
                          //   carries a 15 mm trunnion fairing proud of the
                          //   mould line.
ESC_INSERT_D    =   3.5;  // [mm] M3 × 6 heat-set insert bore (pod M3_INSERT_D)
ESC_INSERT_L    =   6.0;  // [mm] insert depth              (pod M3_INSERT_L)
ESC_BOSS_DEPTH  = ESC_INSERT_L + 1.0;  // [mm] 6.0 of insert plus 1.0 of material
                          //   behind it, so a slightly over-driven insert does
                          //   not burst through into the cavity

// ── Cooling ──────────────────────────────────────────────────────────────────
// A 50 A ESC in a sealed CF-PETG annulus has no heat path at all, and CF-PETG
// conducts at ~0.25 W/mK — 2.5 mm of it over a 460 mm² footprint is 21.7 K/W,
// so conduction through the duct wall into the fan stream is not a path either.
// The cover therefore carries louvres at both ends, venting the bay to ambient.
//
// ** SIZED 2026-09-06, THEN CORRECTED 2026-09-06 — THE FLOW RUNS THE OTHER WAY. **
//
// The first sizing had this circuit taking air FROM the duct and venting it to
// the skin, driven by what it called a "~3.1 kPa inter-stage static rise".
// **There is no static rise.  The inter-stage is 2.78 kPa BELOW ambient**, and
// that circuit would have flowed backwards.
//
// The error was using thrust/area as a static pressure.  In a constant-area duct
// discharging as a free jet, the exit is AT ambient and the inlet is a full
// dynamic head BELOW it, so the fans' pressure rise exactly restores the inlet
// depression and **every station inside the duct is at or below ambient**:
//
//     station 1  duct inlet, pre-forward-fan        -5562 Pa gauge
//     station 2  INTER-STAGE = aft-fan inlet        -2781 Pa gauge
//     station 3  nozzle exit (free jet)                 +0 Pa gauge
//
// Thrust/area also conflates the fan's share with the inlet-lip suction, which
// on this duct is a 50/50 split (10.9 N each of 21.8 N) — so it overstates the
// fan's pressure rise by about 2x on top of getting the sign wrong.
//
// **The hardware is unchanged; only the direction and the labels were wrong.**
// Owner's proposal, and it is strictly better than what it replaces.
// This block used to say a duct bleed "would cost thrust, and stealing it
// without analysis is not a trade this file is entitled to make."  The analysis
// has now been done (`tools/nacelle_esc_thermal.py`) and the cost is small while
// every alternative fails:
//
//   path                                          R (K/W)   Tch at 28 A / 50 A
//   sealed bay, conduct through CF-PETG to stator   19.63     215 C / 632 C
//   same path in 6061 aluminium with a thermal pad   1.86      94 C / 246 C
//   ASPIRATED: skin inlet -> bay -> duct suction     2.84      64 C / 150 C
//
// The stator sleeve is an EXCELLENT sink — 188 cm² of wetted area at 71 m/s
// gives 0.27 K/W — but it cannot be reached.  The 0.2 mm running fit between
// the sleeve OD and the pod bore is 5.33 K/W of still air ON ITS OWN, more than
// the pod wall, the sleeve wall and the stator sink combined even at a generous
// k = 1.2 W/m·K.  Filling it is not available: the sleeve slides in and out on
// its keys, and a thermal pad across a sliding joint shears on every service.
//
// So the heat leaves in the air, not through the walls — and the fan aspirates
// it rather than the duct feeding it.  Ambient air enters through the cover
// louvres, washes both faces of the board, and is drawn out through the
// discharge ports into the aft fan's inlet:
//
//     ambient (0 Pa) -> louvres -> BAY -> discharge ports -> station 2 (-2781 Pa)
//
// At the built port area that is 4.53 g/s and 28.0 m/s over the board — 1.98 %
// of the duct's mass flow.
//
// **THRUST COST 0.99 %, against 3.95 % for the discard circuit.**  The cooling
// air is INGESTED and then pumped by the aft fan, so it leaves with the jet and
// carries its own momentum out; all it misses is the forward fan's work.  The
// discarded air, by contrast, had already been worked on and was then thrown
// away — twice the cost, for a circuit that could not flow.
//
// It also scales the right way.  The driving depression goes as Ve^2, i.e. with
// thrust, so cooling arrives with the power that needs it: 2781 Pa and 28.0 m/s
// at full throttle, 1390 Pa and 19.8 m/s at half.
//
// ** NEW REQUIREMENT THIS CREATES: ** the bay is now an unfiltered path from
// outside air INTO the aft fan.  The louvres are the screen, and that is why
// ESC_LOUVRE_W is 1.2 mm — it is a FOD criterion now, not only a printability
// one.  Anything that passes a 1.2 mm slot reaches the EDF2 rotor.
//
// STILL OPEN, and it is the flow and not the geometry: the circuit loss
// coefficient is ASSUMED K = 3 (one velocity head each for inlet, bay and
// discharge).  Whether the bay delivers 28 m/s needs CFD or a bench flow test.
// See airframe/wings-nacelles/WBS.md §1.1.3.8.
// The louvres are the circuit's INLET and they are AFT-ONLY.  Slots at both ends
// short-circuit: the forward field sat directly over the discharge ports at
// Z 76-88, so air would have entered and left again without ever crossing the
// board.  One field at the aft end forces the full-length traverse.
ESC_LOUVRE_N    =   8;    // [count] slots, aft field only
ESC_LOUVRE_W    =   1.2;  // [mm] slot width (Z).  TWO CRITERIA MEET HERE: two
                          //   extrusions at a 0.6 mm nozzle, AND the coarse FOD
                          //   limit — see the screen note below.
ESC_LOUVRE_L    =  24.0;  // [mm] slot length (circumferential)
ESC_LOUVRE_P    =   3.0;  // [mm] slot pitch (1.8 mm rib)

// ── FOD screen (owner direction, 2026-09-06) ─────────────────────────────────
// Aspirating rather than bleeding made the bay an unfiltered path from outside
// air INTO the aft fan.  A woven screen closes it, bonded into a rebate in the
// cover's inner face over the louvre field.
//
// WHAT THE SCREEN BUYS IS NOT WHAT IT LOOKS LIKE.  The louvres are already
// 1.2 mm wide and standard insect mesh has a ~1.2 mm aperture — no better in
// that dimension.  The gain is the OTHER dimension: a 1.2 x 24 mm slot passes a
// 1.2 x 24 mm sliver; a square aperture passes only 1.2 x 1.2.  The screen bounds
// the second dimension, which a slot cannot.
//
// AND THE LOUVRES HAD TO GROW TO CARRY IT.  A screen's free area is beta =
// (aperture/(aperture+strand))^2, so it throws away a third to a half of the
// geometric opening.  At the old 144 mm2 an insect mesh left 95 mm2 free —
// exactly the discharge-port throat, so the inlet would have BECOME the
// restriction.  At 230 mm2:
//
//     screen                         beta    free area   vs throat   flow
//     none                          1.000     230 mm2      2.42x     100 %
//     insect mesh, 1.2 mm aperture  0.657     151 mm2      1.59x      98 %
//     no-see-um,   0.6 mm aperture  0.498     115 mm2      1.21x      96 %
//     fine,        0.4 mm aperture  0.379      87 mm2      0.92x      91 %  <- inlet becomes the throat
//
// **No-see-um (0.6 mm) is the selection**: it bounds FOD at 0.6 mm in BOTH
// dimensions for 4 % of the flow, where the coarse mesh only matches the slot.
// The fine 0.4 mm mesh is where the trade breaks down.
ESC_MESH_REBATE   = 0.6;  // [mm] rebate depth in the cover's inner face
ESC_MESH_MARGIN   = 3.0;  // [mm] rebate oversize around the louvre field

// ── Discharge ports (Rev T4d, 2026-09-06; direction corrected same day) ─────
// Where the cooling air GOES — into the duct, not out of it.  They have to be at
// Z 74–90: that is the only part of the bay where the POD's own bore is the flow
// boundary.  Aft of Z 90 the stator and aft-spider sleeves line the duct, so a
// hole in the pod wall there would open into the sleeve clearance rather than
// the airflow, and drilling both would put the circuit across a sliding joint.
//
// Z 74–90 is downstream of the forward rotor and upstream of the aft fan, so it
// sits at the same −2781 Pa station-2 depression as the inter-stage proper.
//
// These are the circuit's THROAT — 95 mm² against 144 mm² of louvre — so the
// flow is set here and the louvres cannot choke it.
//
// Teardrop profile, not round: the hole axis is radial, so it is a HORIZONTAL
// hole in the print, and the top of a horizontal circle is an unsupported arc.
// A 45° apex removes it (3d-print-design FDM rules, "Horizontal holes").  It
// also adds a little area, which is free.
ESC_BLEED_N     =    4;   // [count] discharge ports per bay
ESC_BLEED_D     =  5.5;   // [mm] port diameter — 4 x Ø5.5 = 95 mm2, giving
                          //   4.53 g/s at K = 3 against the 2781 Pa depression
// [flattened] ESC_BLEED_Z: value from its last assignment (override), kept at the first position
ESC_BLEED_Z     = [ for (z = [76.0, 80.0, 84.0, 88.0]) z + 95.0 * (P64_A - 1) ];  // [mm] stations, all inside 74–90


// ── Derived fold geometry ────────────────────────────────────────────────────
// Each panel is tangent to the same inner cylinder, so its half-angle is
// atan((w/2) / ESC_MOUNT_R) and the fold angle is the sum of the two.  At
// R 30.2 that is 20.85° + 9.40° = 30.25°, so the panels sit at 149.75° to each
// other — a shallow fold, well inside what a flex hinge will take.
function esc_a_pow() = atan((ESC_W_POWER  / 2) / ESC_MOUNT_R);
function esc_a_sig() = atan((ESC_W_SIGNAL / 2) / ESC_MOUNT_R);


// ── Module: esc_bay_footprint ────────────────────────────────────────────────
// The two panel envelopes, optionally grown by `pad` on every side.  `r_out`
// lets one footprint serve as the board pocket, the access window, and the
// cover's own outline — which is the point: three features that must match
// cannot be drawn three times.
module esc_bay_footprint(az_hinge, r_out, pad = 0) {
    union() {
        esc_panel_slab(ESC_W_POWER + 2 * (ESC_FIT + pad),
                       az_hinge + esc_a_pow(),
                       ESC_MOUNT_R - pad, r_out,
                       ESC_BAY_Z0 - pad, ESC_BAY_Z1 + pad);
        esc_panel_slab(ESC_W_SIGNAL + 2 * (ESC_FIT + pad),
                       az_hinge - esc_a_sig(),
                       ESC_MOUNT_R - pad, r_out,
                       ESC_BAY_Z0 - pad, ESC_BAY_Z1 + pad);
    }
}


// ── Module: esc_boss_cylinders ───────────────────────────────────────────────
// Six fastener positions per bay as long radial cylinders, to be clipped against
// the skin by the caller.  Three down each long side of the WIDE panel's window
// — the narrow panel's sides sit too close to the fold to carry a Ø7 boss.
module esc_boss_cylinders(az_hinge, dia) {
    off = ESC_W_POWER / 2 + ESC_FIT + ESC_BOSS_INSET;
    for (dy = [-off, off],
         z  = [ESC_BAY_Z0 + 6, (ESC_BAY_Z0 + ESC_BAY_Z1) / 2, ESC_BAY_Z1 - 6])
        rotate([0, 0, az_hinge + esc_a_pow()])
            translate([0, dy, z])
                rotate([0, 90, 0])
                    cylinder(d = dia, h = 60, center = false);
}
// ---- end include <nacelle_esc_bay.scad> ----


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
        scale([RADIAL_K, RADIAL_K, AXIAL_K])
        translate([-BORE_CX_L, BORE_CY, 0])
            import("../../stls/nacelles/eng_left_shell24_50mm_repaired.stl",
                    convexity = 4);
    } else {
        // ── Starboard (right) nacelle ─────────────────────────────────────────
        scale([RADIAL_K, RADIAL_K, AXIAL_K])
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



// =============================================================================
// ── Module: circular_intake_fairing ─────────────────────────────────────────
// =============================================================================
// Additive rotationally symmetric exterior fairing.  Its front annulus is
// planar at Z=0, so the intake opening is circular in the side and front views.
// The outer profile first reaches the measured shell envelope, then tapers
// back into the duct wall before the thrust-tube station.  Its termination is
// therefore buried instead of exposing a circumferential cap at the shell.



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
//   • 4× M3 SHCS from INTAKE bore end pass through M3 CLEARANCE bores in spider
//     arms and thread into the motor's own female back-plate holes (Rev T4c —
//     the Galaxy X5 takes four screws on a 90 deg pattern, REF-EDF-002).
//   • T-handle 2.5 mm hex key required; reach ≈ EDF1_SPIDER_Z ≈ 88 mm.
//
// Arms span (R_HUB − 1) → (EDF_BORE_R + 1) with ±1 mm CGAL overrun.
// M3 clearance bores run THROUGH the arm (intake face → nozzle face).



// =============================================================================
// ── Module: esc_wire_exit_slot ────────────────────────────────────────────────
// =============================================================================
// Rectangular slot through the forward thrust tube bore wall at Z ≈ ESC_SLOT_Z.
// Routes EDF1 ESC motor leads and signal wire radially from bore interior to the
// nacelle cavity (between bore tube and outer shell), then to the pylon harness.
// Placed on the pylon-side X face for direct routing to the pylon channel.
// Used as a Zone B subtraction.



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
// [flattened] BOSS_Z_LO: value from its last assignment (override), kept at the first position
BOSS_Z_LO       = 83.0 * P64_A;   // [mm] cutter lower Z
// [flattened] BOSS_Z_H: value from its last assignment (override), kept at the first position
BOSS_Z_H        = 24.0 * P64_A;   // [mm] cutter Z span (covers Z 83..107)

module smooth_boss_fill() {   // union: solid 25..contour (Y6..25) — closes the socket
    fc = [[25, 6], [37, 6], [36.5, 8], [36, 10], [35, 13], [33.4, 15], [32, 18],
          [30.2, 20], [28, 23], [26.2, 25], [25, 25]];
    scale([PYLON_SIDE * RADIAL_K, RADIAL_K, 1])
        translate([0, 0, BOSS_Z_LO]) linear_extrude(BOSS_Z_H) polygon(fc);
}

module smooth_boss_shave() {  // difference: remove material beyond the contour
    scale([PYLON_SIDE * RADIAL_K, RADIAL_K, 1])
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
    grid = (NACELLE_SIDE > 0)
        ? radial_k_cavity(HOLLOW_R_PORT, HOLLOW_SKIN_PORT)
        : radial_k_cavity(HOLLOW_R_STBD, HOLLOW_SKIN_STBD);
    difference() {
        grid_solid(grid, hollow_zs(), HOLLOW_N_AZ);
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
        // The ESC cover doubler and its bosses are Zone-A material INSIDE the
        // skin, which is exactly where the cavity wants to be.  Keep them, or
        // the covers have nothing to land on and nothing to screw into.
        esc_cover_doubler();

        // Keep the ESC board seat solid forward of the bore step — see
        // esc_bay_seat_keepout() for why this is a keep-out and not a plinth.
        esc_bay_seat_keepout();

        // Keep the vestigial-boss cleanup region solid.  smooth_boss_shave()
        // trims the canonical shell back to a MEASURED contour at this station,
        // and the cavity's own 48-facet surface crosses that contour at a
        // shallow angle — which left a 0.08 mm3 lens of material detached from
        // the pod (a floating speck the slicer would try to print in mid-air).
        // Two measured surfaces grazing each other is not something to resolve
        // with more facets; the region is small, it is where the trunnion
        // collar's loads enter the shell, and keeping it solid settles both.
        scale([PYLON_SIDE * RADIAL_K, RADIAL_K, 1])
            translate([20, 4, BOSS_Z_LO - 1])
                cube([40, 28, BOSS_Z_H + 2]);
    }
}


// =============================================================================
// ── ESC bay geometry (Rev T4c) ───────────────────────────────────────────────
// =============================================================================
// Offsets of the MEASURED skin, hoisted so every consumer builds from the same
// surface.  See nacelle_shell_grid.scad for why a radial offset is legitimate
// over this Z range and would not be near the nose.
ESC_SKIN = radial_k_grid((NACELLE_SIDE > 0) ? HOLLOW_SKIN_PORT : HOLLOW_SKIN_STBD);

// Both bays' fastener positions at once, from the shared bay definition — the
// same module the covers drill their clearance holes with, so a boss and its
// hole cannot end up on different centres.
module esc_boss_cylinders_local(dia) {
    for (az_hinge = ESC_BAY_AZ) esc_boss_cylinders(az_hinge, dia);
}

// The shell of material between two radial offsets of the measured skin.
module _esc_skin_shell(d_out, d_in) {
    difference() {
        grid_solid(offset_grid(ESC_SKIN, d_out), hollow_zs(), HOLLOW_N_AZ);
        grid_solid(offset_grid(ESC_SKIN, d_in), hollow_zs(), HOLLOW_N_AZ);
    }
}


// ── ADDITIVE (Zone A) — the cover doubler and its insert bosses ──────────────
// The cover has to land on something, and forward of Z 100 the skin is at the
// 2.5 mm minimum — thinner than the cover itself.  So the bay carries a DOUBLER:
// a band of material added inside the skin around the window, thick enough that
// a rebate can be cut into it without breaking through.
//
// Placed in Zone A, not Zone C, and that ordering is the whole trick.  In Zone A
// the Zone-B rebate can cut into it; in Zone C nothing could.  It is protected
// from the cavity subtraction by being named in hollow_cavity()'s keep-out list,
// the same way the trunnion collar is.
module esc_cover_doubler() {
    intersection() {
        _esc_skin_shell(0.0, ESC_COVER_T + ESC_LEDGE_T);
        union() for (az = ESC_BAY_AZ) esc_bay_footprint(az, 60.0, ESC_LEDGE_W);
    }
    intersection() {
        _esc_skin_shell(0.0, ESC_COVER_T + ESC_BOSS_DEPTH);
        esc_boss_cylinders_local(ESC_BOSS_OD);
    }
}

// ── SUBTRACTIVE (Zone B) — window, rebate, insert bores ─────────────────────
// Three cuts that must be made together, because each is defined against the
// others:
//   window  the board footprint, cut clean through from the seat radius out —
//           a 33 mm folded board cannot be threaded into a sealed annulus, so
//           the bay opens radially and the cover closes it;
//   rebate  everything outside (skin − ESC_COVER_T) across window PLUS the
//           doubler band, so the cover drops in and its outer face is flush with
//           the mould line.  A cover standing proud is a step in the boundary
//           layer at the widest part of the nacelle;
//   bores   M3 heat-set pockets opening on the rebate floor.
module esc_bay_cut() {
    // window — full depth over the board footprint.  The pocket is cut from the
    // SEAT outward, so it automatically carries ESC_STACK + ESC_FLOW_LANE: the
    // lane is the gap between the top of the component stack and the cover's
    // inner face, and it is what the cooling air actually flows through.
    for (az = ESC_BAY_AZ) esc_bay_footprint(az, 60.0);

    // rebate — a cover's thickness deep, over window + landing band
    intersection() {
        difference() {
            translate([0, 0, ESC_BAY_Z0 - ESC_LEDGE_W - 1])
                cylinder(r = 60, h = (ESC_BAY_Z1 - ESC_BAY_Z0)
                                     + 2 * ESC_LEDGE_W + 2, $fn = 96);
            grid_solid(offset_grid(ESC_SKIN, ESC_COVER_T),
                       hollow_zs(), HOLLOW_N_AZ);
        }
        union() for (az = ESC_BAY_AZ) esc_bay_footprint(az, 60.0, ESC_LEDGE_W);
    }

    // insert bores — opening on the rebate floor
    intersection() {
        _esc_skin_shell(ESC_COVER_T - 0.01, ESC_COVER_T + M3_INSERT_L);
        esc_boss_cylinders_local(M3_INSERT_D);
    }
}

// ── SUBTRACTIVE (Zone B) — ESC bay DISCHARGE ports (Rev T4d) ────────────────
// The cooling circuit's OUTLET into the duct — the fan aspirates the bay through
// these.  Named "bleed" in the first pass, when the flow was believed to run the
// other way; it does not.  See nacelle_esc_bay.scad for the station pressures
// that settle the direction, and for why these must sit forward of Z 90.
//
// The teardrop apex points toward +Z, which is UP when the pod prints
// intake-face-down — so the unsupported top arc of each horizontal hole becomes
// a self-supporting 45° roof.
module esc_discharge_ports() {
    for (az_hinge = ESC_BAY_AZ, z = ESC_BLEED_Z)
        rotate([0, 0, az_hinge + esc_a_pow()])
            translate([EDF_BORE_R - 1.0, 0, z])
                rotate([0, 90, 0])
                    linear_extrude(ESC_MOUNT_R - EDF_BORE_R + 3.0)
                        hull() {
                            circle(d = ESC_BLEED_D);
                            // local -x maps to global +Z under rotate([0,90,0])
                            translate([-ESC_BLEED_D * 0.5, 0])
                                rotate(45)
                                    square(ESC_BLEED_D * 0.707, center = true);
                        }
}


// ── The board seat is a KEEP-OUT, not an addition (Rev T4c) ─────────────────
// Forward of Z 90 the bore is Ø50, so the duct wall's outer face sits at 27.5
// and the board needs 2.7 mm of packing under it to reach ESC_MOUNT_R.
//
// The first attempt ADDED that packing as a Zone-C plinth whose top face was at
// exactly ESC_MOUNT_R — the same plane the Zone-B pocket floor lies in.  Two
// coplanar faces meeting is the touching-face problem this repo has hit before,
// and it duly produced six non-2-manifold edges in the starboard pod at
// local r 30.4, Z 86.9–88.8 — precisely on that plane, in both bays.
//
// The fix is to stop adding material and start KEEPING it.  The canonical shell
// is solid; the cavity is what would have hollowed this region out.  Excluding
// the seat footprint from the cavity leaves the shell's own material there, and
// the bay pocket then CUTS the seat face at ESC_MOUNT_R as a real boolean
// result rather than as two surfaces that happen to coincide.  Same geometry,
// one fewer coincidence, and one fewer part to print.
//
// The inner bound deliberately runs BELOW the duct wall (26.0 against 27.5) so
// the keep-out crosses the cavity's inner cylinder instead of grazing it.



// Extra Zone-B cuts hook — overridden by derived pods; nothing here.


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
//   • esc_discharge_ports()    — Rev T4d aspirated-cooling outlet into the duct
//   • esc_bay_cut()            — Rev T4c ESC window + cover rebate + bores
//     (the board seat is cut by the same pocket; see esc_bay_seat_keepout)
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
    // The bay must not reach inside the duct wall, and its board must be the
    // one the fit tool measured — a silent widening here is a silent foul.
    // The shared bay file states ESC_MOUNT_R as a literal so the cover can use
    // it without importing the pod.  This is where the two are tied together.
    assert(abs(ESC_MOUNT_R - (SLEEVE_BORE_R + CAVITY_DUCT_WALL)) < 1e-9,
           "ESC seat radius has drifted from the sleeve-zone duct wall");
    assert(ESC_INSERT_D == M3_INSERT_D && ESC_INSERT_L == M3_INSERT_L,
           "ESC insert size has drifted from the pod's M3 insert");
    assert(ESC_W_POWER + ESC_W_SIGNAL >= 32.0,
           "folded ESC width is under the 32 mm isolation floor");
    // The bay length is an OUTPUT of the radial budget, not a target, so this
    // asserts the budget instead of the length.  Pinning it to a length is what
    // it did before, and that assertion then fired on a correct change: the
    // board went 62 -> 44 mm when the cover's own thickness and the cooling lane
    // were finally charged to the same budget.
    assert(ESC_STACK + ESC_FLOW_LANE + ESC_COVER_T + 0.4 <= 8.0,
           "ESC radial budget over 8.0 mm - the bay then runs out of depth before length; see nacelle_esc_bay.scad");
    assert(ESC_BAY_Z1 - ESC_BAY_Z0 >= 40.0,
           "ESC bay is under 40 mm — below the shortest board considered viable");
    assert(ESC_DISC_D < ESC_DISC_AVAIL,
           "disconnect bay is deeper than the MEASURED inboard-face envelope");
    assert(ESC_DISC_Z - ESC_DISC_H / 2 >= ESC_DISC_Z_LO
           && ESC_DISC_Z + ESC_DISC_H / 2 <= ESC_DISC_Z_HI,
           "disconnect bay has left the measured-depth Z window");

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

                // ── ESC cover doubler + insert bosses (Rev T4c) ──────────
                esc_cover_doubler();

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

            // ── ESC bay discharge ports into the duct (Rev T4d) ───────────
            esc_discharge_ports();

            // ── Hinged-ESC bays: board pocket + access window (Rev T4c) ───
            // Cut AFTER the cavity so the two merge into one volume — that is
            // deliberate: it is what gives the power feed a route from the
            // disconnect bay and the phase leads a route to the spider arms.
            esc_bay_cut();

            // ── Variant hook (empty here) — extra Zone-B cuts a derived pod
            // (nacelle_pod_64mm_tandem.scad) needs, e.g. its intake-lip
            // ring cavity.  Identity for the 50 mm pod.
            extra_zone_b_cuts();

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

        // ── ESC bay seat plinth, cover ledge and insert bosses (Rev T4c) ──
        // Zone C, all three: the cavity subtraction would otherwise delete the
        // plinth and the ledge, and the bay cut would delete the bosses.  They
        // sit outside every Zone-B cut by construction, so adding them after the
        // difference() closes is correct rather than a workaround.
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
if (POD_AUTORENDER) nacelle_pod(swirl_dir = SWIRL_DIR);


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
//   1b. ** THRUST-TUBE BORE = 50.0 mm +0.4 / −0.0 OVER THE EDF1 ROTOR STATION **
//      (Z ≈ 27.5 … 40).  The build keeps only the rotor and motor and uses this
//      bore as the duct, so the EDF1 rotor runs against PRINTED plastic.  The
//      vendor holds 0.4 mm blade-tip-to-shell in a 50 mm shroud (REF-EDF-002),
//      i.e. the rotor is ~Ø49.2.  An undersize bore rubs the rotor; check it
//      before fitting the fan, and scrape rather than force.
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
// ---- end include <nacelle_pod_50mm_tandem.scad> ----

use <edf_motor_mount_64mm.scad>   // stage-1 stator (integrated) + lead channel
use <nacelle_nozzle_servo_64mm.scad>   // nozzle servo drive in the resized dorsal shroud

    // render the 64 mm pod below, not the 50 mm one

// ── Shell scale ──────────────────────────────────────────────────────────────
   // = 209.28 mm (8.24 in)

// ── Flow tube (KTD9) ────────────────────────────────────────────────────────
              // = 32.0 mm
   // = 34.5 mm; printed tube is the duct

// ── Outer envelope (reference values, scaled with the shell) ─────────────────
   // = 91.2 mm (3.59 in)
   // = 100.8 mm (3.97 in)
    // = 41.14 mm
      // = 45.98 mm

// ── Wing interface hold (owner, 2026-10-03) ──────────────────────────────────
   // = 35.34 mm
   // = 55.84 mm
   // = 29.14 mm

// Collar for the 6804 trunnion (mirrors nacelle_trunnion_64mm.scad): register
// bore Ø38.1 H7 from the trunnion's REG_Z0 (12.5) to its flange face (14.0);
// collar OD = trunnion flange OD 54; 3 x M3 on Ø45.5.  The register is a
// 1.5 mm pilot; the bolted, bonded flange reacts the moment (as at 50 mm).
   // = 47.84
   // = 49.34


// ── Axial stack (header table) ───────────────────────────────────────────────
// INLET_BELL_L / _FLARE now describe the lip, for cavity_duct_wall().
                               // = 30.5
                   // = 103.2
         // = 104.2
     // = 176.9
         // = 42.2
                   // = 103.2
// Owner 2026-10-03: the forward motor mount/stator is ONE PIECE with the
// thrust tube, so the removable sleeve zone (and its bore step, key slots and
// cavity wall offset) starts at the stage-2 cartridge's forward face.
  // = 103.7
  // = 103.7
  // = 103.7
       // = 199.13 at x1.06; rides on the shell's aft end

// ── Shell-tied stations stretched with the shell ─────────────────────────────
// The two forward webs ride with the shell.  The two that bracket the ESC
// bays are tied to the BAYS, which keep a fixed board length: in the 50 mm
// pod they sat "just forward / just aft of the bays" (plan Rev T4c).  At
// 70 x 1.13 = 79.1 the third web landed on the bay doubler's forward edge
// (Z 78.35) and left open slivers in the render; it now sits 4 mm clear of
// the doubler band (ESC_BAY_Z0 - ESC_LEDGE_W - 4), the fourth 3.5 mm aft of it.
    // = 139.85
    // = 79.1
    // vestigial-boss cleanup, a shell feature

// ESC bays keep their 42 mm board length, centred where the stretched shell
// puts the 50 mm bays' centre (95 x 1.13 = 107.35).  Cooling ports move with
// the bay by the same offset.
   // = 86.35
   // = 128.35


// ── Motor mounts (KTD9 / R13) ────────────────────────────────────────────────
   // [mm] QF2822 4 x M3 on ø16.00 (8-4.jpg) — VERIFY
   // [mm] stator hub outer radius over the ø27.8 can
    // = 33.88 mm, on the nozzle pocket face. FAN-TIED (aft sleeve screws): NOT scaled by the 2026-10-05 x1.06

// ── Nozzle pocket — PLACEHOLDER until plan U11 re-sizes the iris ─────────────
    // = 87.12 mm. FAN-TIED: the iris housing (r 42.6) is not scaled; 0.96 mm running fit. Scaling it with the shell cut the tail off at Z 209 (2026-10-05)

// ── Cavity, ESC seat ─────────────────────────────────────────────────────────
   // = 36.3 mm
   // = 37.2 mm
                  // = SLEEVE_BORE_R + CAVITY_DUCT_WALL (pod assert ties them)

// ── Tilt pivot = rotating-assembly CG (plan 003 KTD7; owner 2026-10-03) ─────
// tools/nacelle_mass_cg_64.py is the authority; iterate to <= 0.25 mm.
  // iteration 2 (iteration 1: 109.1 -> measured 109.72)

// ── 10 AWG disconnect bay — between the stretched Z 40 and Z 62 bulkheads,
// clear of the trunnion ring-gear cavity (ø42.6 about PIVOT_Z).
         // = 57.63
   // = 46.7
   // = 68.56

// ── Module overrides ─────────────────────────────────────────────────────────

// No pod-integrated spider: the stator-1 front plate carries motor 1.
// Stage-1 motor mount + stator, INTEGRAL with the thrust tube (owner
// 2026-10-03; edf_motor_mount_64mm.scad stator_stage(1): QF2822 plate at
// Z 42.2, 11 free-vortex cambered vanes, hollow lead vane at the ESC-1 bay
// azimuth).  Zone C, so no cavity cut removes it.
module edf1_nacelle_spider() {
    $mm_side = PYLON_SIDE;  $mm_swirl = SWIRL_DIR;
    stator_stage(1);
    // Zone C is also where the RESIZED canonical dorsal shroud joins the pod
    // (nacelle_nozzle_servo_64mm.scad nsv_pod_adds; owner rule 2026-10-04).
    $nsv_side = PYLON_SIDE;
    nsv_pod_adds();
}
// The 50 mm motor-lead exit slot sat at STATOR_SLV_Z_START; at 103.7 it would
// open the duct at the rotor-2 tips.  The lead vanes replace it.
module esc_wire_exit_slot(pylon_side = PYLON_SIDE) {}
// The 50 mm sleeve-retention bosses reached r 30.4 at 64 mm — inside the bore
// and the nozzle throat (joint census 2026-10-03).  The nozzle is the aft lock.
module sleeve_retention_bosses() {}
// Two anti-rotation keys at 64 mm (owner-approved nozzle-servo packaging,
// 2026-10-04): the 270 deg key slot lies under the canonical dorsal spine where
// the nozzle servo pocket goes.  Two 3 x 3 mm keys carry the 0.227 N·m EDF
// reaction torque with large margin; 30/150 mirror onto each other port/stbd.


// ESC seat keep-out spans the bay (the whole bay is over the sleeve zone) and
// tracks the larger duct (EDF_BORE_R + 1 instead of the 50 mm literal 26.0).
module esc_bay_seat_keepout() {
    for (az_hinge = ESC_BAY_AZ)
        for (side = [0, 1])
            esc_panel_slab(
                (side == 0 ? ESC_W_POWER : ESC_W_SIGNAL) + 2 * (ESC_FIT + 2.0),
                az_hinge + (side == 0 ? esc_a_pow() : -esc_a_sig()),
                EDF_BORE_R + 1.0, ESC_MOUNT_R + 2.0,
                ESC_BAY_Z0 - 1.0, ESC_BAY_Z1 + 1.0);
}

// ── Intake lip profile functions (header) ────────────────────────────────────
// Internal: r = R + F (1 - sqrt(1 - (1 - z/a)^2)),  0 <= z <= a.
function lip_r_in(z) =
    let(u = 1 - z / P64_LIP_A)
    P64_BORE_R + P64_LIP_F * (1 - sqrt(max(0, 1 - u * u)));
// External: r = R_hl + B sqrt(1 - (1 - z/A)^2),  0 <= z <= A.
function lip_r_out(z) =
    let(u = 1 - z / P64_FORE_A)
    P64_HL_R + P64_FORE_B * sqrt(max(0, 1 - u * u));

LIP_N = 48;   // profile stations per branch

// SUBTRACTIVE — the internal lip contour (replaces the cosine bell cut).
// Overshoots 0.5 mm forward of Z 0 at the highlight radius so the front of the
// canonical shell's dome is cleanly removed inside the highlight.
module inlet_bellmouth() {
    rotate_extrude(angle = 360, convexity = 4)
        polygon(concat(
            [[0, -0.5], [P64_HL_R, -0.5]],
            [ for (i = [0 : LIP_N]) let(z = P64_LIP_A * i / LIP_N)
                  [lip_r_in(z), z] ],
            [[0, P64_LIP_A]]));
}

// ADDITIVE — the intake cowl (replaces the circular intake fairing).
// CANON RULE (airframe/AGENTS.md "Geometry Integrity", 2026-11-01): the
// 2026-10-03..05 ring HELD a cylinder r 45.05 to Z 23.3 and then dropped inside
// the skin — a plain can proud of the canonical dome with a groove behind it,
// which the canonical engine never shows [REF-CAD-002 Henning engine model;
// REF-CAD-003 Sheets 3/4]: there the cowl rolls continuously from the intake
// lip into the bulbous forward shell.  Now, on every 5 deg azimuth:
//   Z 0 .. P64_FORE_A   the CFD lipE external ellipse (unchanged nose, r 40->42.5)
//   .. Z junction       a monotone cubic Hermite from the shoulder (r 42.5,
//                       slope 0) to the MEASURED skin radius and slope at that
//                       azimuth's junction = the earliest G1-feasible station
//                       on Z 28..50 (or the skin's crest)
//                       (tools/nacelle_cowl_fair.py), sunk P64_COWL_SINK
// so the cowl takes the canonical dome's own asymmetry and meets it with
// G1 continuity.  Inner side: 0.05 mm inside the lip contour (the subtractive
// cut defines the flow surface), then buried in the duct wall at r 31.5.
include <nacelle_cowl_fair_table.scad>
COWL_TABLE = NACELLE_SIDE > 0 ? COWL_SKIN_PORT : COWL_SKIN_STBD;
COWL_NH = 24;    // Hermite stations
// Mirrored in tools/nacelle_intake_cfd.py r_ext() — change both together.
function cowl_herm(z, zj, r1, m1) =
    let(L = zj - P64_FORE_A, rise = r1 - P64_FORE_R,
        m = min(m1, 3 * rise / L) * L,          // Fritsch-Carlson monotone clamp
        t = (z - P64_FORE_A) / L)
    P64_FORE_R * (2*t*t*t - 3*t*t + 1) + r1 * (-2*t*t*t + 3*t*t)
        + m * (t*t*t - t*t);
function cowl_profile(row) =
    let(zj = row[1], r1 = row[2] - P64_COWL_SINK, m1 = max(0, row[3]))
    concat(
        [ for (i = [LIP_N : -1 : 0]) let(z = P64_LIP_A * i / LIP_N)
              [lip_r_in(z) - 0.05, z] ],                       // throat -> HL
        [ for (i = [1 : LIP_N]) let(z = P64_FORE_A * i / LIP_N)
              [lip_r_out(z), z] ],                             // lipE nose
        [ for (i = [1 : COWL_NH]) let(
              z = P64_FORE_A + (zj - P64_FORE_A) * i / COWL_NH)
              [cowl_herm(z, zj, r1, m1), z] ],                 // fair to skin
        [[P64_BORE_R + P64_WALL - 0.5, zj],                    // bury in duct wall
         [P64_BORE_R - 0.5, zj], [P64_BORE_R - 0.5, P64_LIP_A]]);
module circular_intake_fairing() {
    n_az = len(COWL_TABLE);
    np = len(cowl_profile(COWL_TABLE[0]));
    pts = [ for (k = [0 : n_az - 1]) let(a = COWL_TABLE[k][0])
                for (q = cowl_profile(COWL_TABLE[k]))
                    [q[0] * cos(a), q[0] * sin(a), q[1]] ];
    // Triangles, not quads: adjacent azimuths have different junction
    // stations, so a quad would be non-planar.
    faces = [ for (k = [0 : n_az - 1]) for (j = [0 : np - 1])
                let(k1 = (k + 1) % n_az, j1 = (j + 1) % np)
                for (t = [[k * np + j, k * np + j1, k1 * np + j1],
                          [k * np + j, k1 * np + j1, k1 * np + j]]) t ];
    polyhedron(points = pts, faces = faces, convexity = 6);
}

// SUBTRACTIVE (Zone B, via the 50 mm pod's extra_zone_b_cuts() hook) — the
// lip ring cavity.  Without it the ring is solid from the nose to the pod's
// measured cavity (which starts at Z 24.15), ~60 g of material forward of the
// pivot.  Walls: P64_RING_WALL to the lip flow surface and to the ring's outer
// surface; a solid nose ahead of P64_RING_CAV_Z0.  NOT a sealed void: four
// axial vent bores carry it aft into the pod cavity (the same rule as the
// pod's vented bulkheads — CF-PETG is hygroscopic and a sealed void cannot
// be drained or inspected).
module lip_ring_cavity() {
    z1 = P64_RING_HOLD - P64_RING_WALL;          // stay inside the held ring
    r_out = P64_FORE_R - P64_RING_WALL;          // = 40.0
    rotate_extrude(angle = 360, convexity = 4)
        polygon(concat(
            [ for (i = [0 : 16]) let(
                  z = P64_RING_CAV_Z0 + (z1 - P64_RING_CAV_Z0) * i / 16)
                  [(z < P64_LIP_A ? lip_r_in(z) : P64_BORE_R) + P64_RING_WALL, z] ],
            [[r_out, z1], [r_out, P64_RING_CAV_Z0]]));
    // vents into the pod cavity (which starts at Z 24.15, r 34.5-38+)
    for (i = [0 : 3])
        rotate([0, 0, 45 + 90 * i])
            translate([(P64_BORE_R + P64_RING_WALL + r_out) / 2, 0, z1 - 0.5])
                cylinder(d = 3.0, h = 30.0 * P64_A - z1, $fn = 24);
}

// ── Tilt drive: pinion + shaft relief, and the collar fasteners (option 1,
// owner 2026-10-03; WBS NAC-64-TILT-03) ──────────────────────────────────────
// Must stay in step with nacelle_trunnion_64mm.scad (SHAFT_R, SHAFT_AZ, slot
// angles, BOLT_ANGLES, gear band).  Geometry is built in the TRUNNION PART
// frame (z = tilt axis toward the wing from the spar tip, x = aft, y = up)
// and mapped to the pod by part_frame(): part z -> +X, part x -> +Z,
// part y -> -Y, origin (TRUNNION_X0, 0, PIVOT_Z).  Starboard / PYLON_SIDE +1.
// Wing shaft relative to the spar at the tip, Rev T6 (2026-10-03): both
// bores are LEVEL on their fuselage datums (wings_s1223_revo.scad spar_bore /
// tilt_shaft_bore), so the shaft is 25.6 mm aft (station 53.6 - 28.0) and
// 2.2391 mm above (shaft_y 11.0797 - spar 8.8406) the tilt axis everywhere.
// Centre distance therefore 25.698 (was 25.6 at the old sloped-bore tip):
// +0.098 mm, ~0.07 mm extra backlash, closed out by the AK7455 loop.
T_SHAFT_DY = 25.6;  T_SHAFT_DZ = 2.2391;
T_SHAFT_R = sqrt(T_SHAFT_DY * T_SHAFT_DY + T_SHAFT_DZ * T_SHAFT_DZ);  // 25.698
T_SHAFT_AZ = atan2(T_SHAFT_DZ, T_SHAFT_DY);                          // 5.00 deg
T_A0 = T_SHAFT_AZ - 5.0 - 6.0;  T_A1 = T_SHAFT_AZ + 140.0 + 6.0;  // -6.0..151.0
T_PIN_RA = 0.8 * 14 / 2 + 0.8;   // = 6.4 mm, 14T m0.8 tip radius
T_GEAR_Z = [2.0, 12.5];          // ring/pinion band, part z (option A face 10.5)
T_BOLTS = [175, 255, 335];

module part_frame() {
    multmatrix([[0, 0, PYLON_SIDE, PYLON_SIDE * TRUNNION_X0],
                [0, -1, 0, 0], [1, 0, 0, PIVOT_Z], [0, 0, 0, 1]]) children();
}
module t_sector(z0, h, half_w) {     // swept annular sector, round ends
    translate([0, 0, z0]) rotate([0, 0, T_A0]) {
        rotate_extrude(angle = T_A1 - T_A0, $fn = 180)
            translate([T_SHAFT_R - half_w, 0]) square([2 * half_w, h]);
        for (a = [0, T_A1 - T_A0]) rotate([0, 0, a])
            translate([T_SHAFT_R, 0, 0]) cylinder(r = half_w, h = h, $fn = 32);
    }
}
// SUBTRACTIVE — the swept volume of the wing-fixed pinion (tip radius + 0.8)
// over the gear band +/- 0.5, and of the Ø4 shaft (+0.8) from the band out
// past the wing tip face.  Opens into the joint gap; it is the pod-side half
// of the clearance the trunnion flange slot provides.
module tilt_drive_relief() {
    part_frame() {
        t_sector(T_GEAR_Z[0] - 0.5, T_GEAR_Z[1] - T_GEAR_Z[0] + 1.0,
                 T_PIN_RA + 0.8);
        t_sector(T_GEAR_Z[1] + 0.5 - 0.01,
                 WING_TIP_FACE_X - TRUNNION_X0 - T_GEAR_Z[1] + 1.0, 2.0 + 0.8);
    }
}

module extra_zone_b_cuts() {
    lip_ring_cavity(); tilt_drive_relief(); motor_lead_routes();
    $nsv_side = PYLON_SIDE;
    nsv_pod_cuts();     // nozzle servo pocket, drive sweeps, service wells, cover opening
}

// Motor phase-lead routes (WBS NAC-64-SVC-01), PYLON_SIDE-mirrored with the
// lead vanes (edf_motor_mount_64mm.scad lead_az: 68 / 248 = ESC_BAY_AZ):
//  * stage 1: the integrated lead vane's channel, out through the duct wall,
//    then a Ø5 conduit at r 37.5 through the cavity bulkheads aft to the
//    ESC-1 bay (ESC_BAY_Z0 86.35).  Motor 1 comes out aft, so its leads are
//    drawn back through this path one bullet at a time.  The pour-foam core
//    (plan 2026-10-03-001) must keep this conduit open.
//  * stage 2: an axial lead-escape slot in the sleeve bore from the lead vane
//    (Z ~119) to the aft end, so the leads slide out with the cartridge; it
//    opens into the ESC-2 bay over the bay's Z range.
LEAD_CONDUIT_R = 37.5;  LEAD_CONDUIT_D = 5.0;
LEAD_SLOT_W2   = 5.0;   LEAD_SLOT_D2   = 4.8;
module motor_lead_routes() {
    $mm_side = PYLON_SIDE;  $mm_swirl = SWIRL_DIR;
    az1 = PYLON_SIDE * 68;  az2 = PYLON_SIDE * 248;
    lead_channel_stage(1, LEAD_CONDUIT_R + 1.0);
    rotate([0, 0, az1]) translate([LEAD_CONDUIT_R, 0, 46.0])
        cylinder(d = LEAD_CONDUIT_D, h = ESC_BAY_Z0 + 4.0 - 46.0, $fn = 24);
    rotate([0, 0, az2]) translate([SLEEVE_BORE_R - 0.01, -LEAD_SLOT_W2 / 2, 119.0])
        cube([LEAD_SLOT_D2, LEAD_SLOT_W2, NOZZLE_RING_Z - 119.0 + 1.0]);
}

// Override of the 50 mm trunnion_collar_cut(): identical register bore, gear
// cavity and nav port, but the 3 x M3 collar inserts are placed about the
// SPAR axis at the trunnion's BOLT_ANGLES.  The 50 mm module rotates them
// about the DUCT axis (rotate([0,0,i*120]) applied after translation), which
// puts two of the three on the wrong side of the pod — found 2026-10-03 by the
// in-context check (WBS NAC-64-TILT-03).
module trunnion_collar_cut() {
    sgn = PYLON_SIDE;
    translate([sgn * COLLAR_X0, 0, PIVOT_Z]) rotate([0, sgn * 90, 0])
        cylinder(d = TRUNNION_REG_D, h = (WING_TIP_FACE_X - COLLAR_X0) + 1);
    translate([sgn * TRUNNION_CAV_X0, 0, PIVOT_Z]) rotate([0, sgn * 90, 0])
        cylinder(d = TRUNNION_CAV_D, h = COLLAR_X0 - TRUNNION_CAV_X0 + 0.01);
    part_frame() for (a = T_BOLTS) rotate([0, 0, a])
        translate([COLLAR_BOLT_D / 2, 0,
                   COLLAR_X1 - TRUNNION_X0 - M3_INSERT_L - 0.01])
            cylinder(d = M3_INSERT_D, h = M3_INSERT_L + 0.02, $fn = 24);
    // Nav 3-core crossing port: the 50 mm module drills it at azimuth 0, which
    // is INSIDE the drive shaft's sweep — the shaft would cut the nav wire.
    // Moved to T_NAV_AZ, beside the wing's own nav conduit (measured on the
    // wing mesh: hull y 1.0, z 61.5 -> 189 deg, r 20.2 about the spar axis),
    // in the solid sector between the 175 and 255 deg bolts.
    part_frame() rotate([0, 0, T_NAV_AZ])
        translate([COLLAR_BOLT_D / 2, 0, COLLAR_FAIR_X - TRUNNION_X0 - 1])
            cylinder(d = NAV_WIRE_BORE + 1.6,
                     h = COLLAR_X1 - COLLAR_FAIR_X + 2.01, $fn = 16);
}
T_NAV_AZ = 210;   // [deg] part frame; 35 deg from the 175 bolt, 45 from 255

// ── Parse-time checks specific to the 64 mm pod ──────────────────────────────
assert(EDF2_Z_EXIT <= NOZZLE_RING_Z,
       "motor-2 tail enters the nozzle pocket — axial fit gate (R11) fails");
assert(EDF1_Z_ENTRY >= P64_LIP_A,
       "rotor 1 is inside the lip — it must run in the constant 64 mm bore");
assert(MOTOR_BOLT_R + M3_CLEAR_D / 2 < R_HUB,
       "QF2822 bolt circle does not land on the stator hub");
assert(abs(NACELLE_FACE_X_PYLON - TRUNNION_X0 - (34.0 - 28.2)) < 1e-9,
       "pylon-face-to-spar-tip distance changed — sleeve bound not held");
assert(abs(WING_TIP_FACE_X - TRUNNION_X0 - 20.5) < 1e-9,
       "spar stub != wings_s1223_revo.scad SPAR_TIP_PROTRUSION_64N (20.5 mm)");
assert(NACELLE_FACE_X_PYLON - EDF_BORE_R - WALL_T >= 6.5,
       "pylon wall too thin for the 6.0 mm disconnect pocket + 0.5 material");
assert(abs(PIVOT_Z - ESC_DISC_Z) > TRUNNION_CAV_D / 2 + ESC_DISC_H / 2,
       "10 AWG disconnect bay overlaps the trunnion ring-gear cavity");
assert(abs(lip_r_out(P64_FORE_A) - P64_FORE_R) < 1e-6
       && min([ for (row = COWL_TABLE) row[2] ]) >= P64_FORE_R + 1.0,
       "cowl junction skin is under the lip shoulder + 1 mm — regenerate with a larger COWL_ZJ (tools/nacelle_cowl_fair.py)");
assert(COWL_GEN_SHOULDER_R == P64_FORE_R && abs(COWL_GEN_SHOULDER_Z - P64_FORE_A) < 1e-9
       && COWL_GEN_SINK == P64_COWL_SINK,
       "nacelle_cowl_fair_table.scad is stale vs the lip — rerun tools/nacelle_cowl_fair.py");
assert(abs(P64_FORE_B * P64_FORE_B / P64_FORE_A
           - P64_LIP_F * P64_LIP_F / P64_LIP_A) < 1e-9,
       "external and internal nose radii differ — the nose is not a true round");
assert(lip_r_in(P64_RING_CAV_Z0) + 2 * P64_RING_WALL < P64_FORE_R,
       "lip ring too thin for its cavity at the nose end");

if (is_undef(P64_NO_RENDER)) nacelle_pod(swirl_dir = SWIRL_DIR);
