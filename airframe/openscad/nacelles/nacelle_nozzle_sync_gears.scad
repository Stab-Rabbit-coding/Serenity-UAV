// ===========================================================================
// *** DO NOT PRINT THE SUN — ITS DATUM IS BLOCKED (2026-09-10) ***
//   The gear PAIR SIZING, the tooth-stress check, the backlash/chamfer work,
//   the print orientation and the integral pinion+crank are all sound and are
//   DATUM-INDEPENDENT: they carry over to whatever datum is finally chosen.
//   What is WRONG here is sun_*: its bore and wing-tip mounting were authored
//   to this document's SUPERSEDED 2026-07-19 datum (Ø8.4 bore for a ROTATING
//   Ø8 spar).  Under Rev T1 the spar is a FIXED Ø20 CF tube bonded into the
//   wing, and KTD3 (plan 004, 2026-08-29) re-datums the sync gear coaxial at
//   the trunnion — a position that DOES NOT PACKAGE in the as-built Rev T4
//   joint (+0.0 mm axial margin in hand; every lever at a floor).
//   Full numbers and the lever-by-lever analysis:
//     docs/NOZZLE_DRIVE_TRADE.md § "PACKAGING BLOCKER — the KTD3 datum does
//     not fit (2026-09-10)"     and     airframe/wings-nacelles/WBS.md §1.1.3
//   This file is committed for the reusable half ONLY.  The sun's bore, face
//   width and mounting must be re-authored once the datum decision is made.
// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  Primary-component STLs published to airframe/stls/ are
//   stored directly in hull frame, baked by tools/bake_hull_frame.py.
//   NEVER re-bake a mesh derived from an already-baked file.
//   This file:
//     PART-LOCAL PRINT FRAME.  Each of the two printed parts is authored in
//     its OWN print frame with the gear axis on local +Z and local z = 0 at
//     the BUILD-PLATE face (the chamfered face of the tooth band).  That is
//     the orientation the parts are printed in, and it is the orientation the
//     Makefile exports.  The "asm" preview additionally poses the pair (sun
//     flipped, pinion translated to the centre distance) in a shared MESH
//     frame whose +Z is INBOARD (away from the wing) — see RENDER_PART below.
//     Hull placement derives from the nacelle pivot pose; assembly placement
//     VERIFY pending (serenity_assembly.py).
// ===========================================================================
// =============================================================================
// nacelle_nozzle_sync_gears.scad
// Serenity UAV — Rev T — Nozzle sync gear pair (1:1 sun + pinion/crank)
// =============================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Analysis and drafting: Claude (Claude Opus 5, Anthropic) under the author's
//           direction, per AGENTS.md §3 "Attribution and Licensing"
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-09-09
// Revision: Rev T (2026-09-09) — NEW PART PAIR
//
// -----------------------------------------------------------------------------
// PURPOSE
// -----------------------------------------------------------------------------
// The two gear members of the ADOPTED hybrid A+B nozzle drive.  Governing
// decision: `docs/NOZZLE_DRIVE_TRADE.md`, "DECISION AMENDMENT -- hybrid A+B
// adopted (2026-07-19)".  Architecture, restated only so this file is readable
// on its own (the pushrod file's "ADOPTED ARCHITECTURE" block is the source of
// truth):
//
//   A gear FIXED to the non-tilting wing datum, coaxial with the tilt spar at
//   the wing tip (the "sun"), is meshed by a gear carried on the NACELLE (the
//   "pinion").  As the nacelle tilts through theta about the spar axis, the
//   fixed-sun / planet-pinion pair spins the pinion by theta * (Z_sun/Z_pinion)
//   RELATIVE TO THE NACELLE.  At the adopted 1:1 mesh the pinion tracks tilt
//   1:1 in the nacelle frame, so the crank -> pushrod -> unison-ring linkage is
//   entirely nacelle-body-fixed and the tilt rotation drops out of the linkage
//   math (nacelle_nozzle_pushrod.scad; tools/nozzle_linkage_check.py).
//
//   The nozzle therefore remains PASSIVELY driven by nacelle tilt, which is the
//   canonical requirement (airframe/AGENTS.md "Nacelle Nozzle Drive").
//
// This file provides:
//   sync_sun()          — the wing-fixed 33T sun (printed, CF-PETG)
//   sync_pinion_crank() — the nacelle 33T pinion CO-PRINTED WITH THE CRANK,
//                         one part, carrying the ball stud at CRANK_R (printed,
//                         CF-PETG)
//
// The COTS parts of the drive are NOT modelled here: the M3 ball studs, the
// ball-link pushrod (nacelle_nozzle_pushrod.scad pushrod()), and the Ø4 steel
// stub axle the pinion turns on.
//
// -----------------------------------------------------------------------------
// WHY THE PINION AND THE CRANK ARE ONE PART (decision, not an option)
// -----------------------------------------------------------------------------
// This is a PASSIVE POSITIONING drive: nothing closes a loop around the nozzle
// exit area, so every millidegree of lost motion between the tilt input and the
// unison ring shows up directly as error in the nozzle exit-area schedule (the
// 75 % -> 105 % of bore map that the iris file's cam implements).  A crank hub
// clamped or keyed to a pinion shaft is exactly such a lost-motion source — a
// printed clamp on a Ø4 shaft will slip or wind up under the 13 N pushrod load
// long before the teeth care.  Co-printing the crank into the pinion blank
// removes the shaft/key/retention problem entirely: there is no hub joint to
// slip, no key to shear, no set screw to back out, and one fewer printed part
// and two fewer fasteners per nacelle.
//
// -----------------------------------------------------------------------------
// TOOTH STRESS — VERIFIED RESULT (do not re-derive)
// -----------------------------------------------------------------------------
// Lewis bending check, worst case, transcribed from the verified analysis:
//   pushrod force            20 N   (deliberately generous — the measured
//                                    linkage worst case is well under this)
//   tangential load at pitch 12.88 N
//   Lewis form factor Y      0.368  (33T, 20 deg full depth)
//   bending stress sigma     10.94 MPa
//
// Against the MOST CONSERVATIVE allowable this repository actually cites —
// 48.41 MPa, the UNREINFORCED-PETG bulk tensile figure used elsewhere in this
// repo as a conservative bending proxy [REF-MAT-001] — the factor of safety is
// FOS 4.43, above the project's 4.0 target.  Against the 20 % CF-PETG figure of
// 77 MPa [REF-MAT-002, Table 4] it is FOS 7.04.  The teeth are NOT the
// governing concern in this drive; the ball-stud boss and the printed journal
// are (see their comments).
//
// HONESTY NOTE ON THE ALLOWABLE (required reading before anyone re-uses these
// numbers):
//   * This repository has NO print-orientation-specific and NO interlayer
//     (Z-axis) allowable for CF-PETG at all.  REF-MAT-002 states explicitly
//     that it publishes "no print-orientation-specific data ... no interlayer
//     (Z-axis) strength figure or orientation-dependent allowable", and the
//     related CF-PETG BEARING allowable is carried in REFERENCES.md as
//     "requires verification".  The check above is therefore deliberately
//     stated against the conservative unreinforced-PETG proxy, and the
//     conclusion (teeth are not governing) holds across EVERY candidate
//     allowable this repo can cite — 48.41, 54, or 77 MPa.
//   * Correction to how these two numbers are sometimes quoted: 48.41 MPa is
//     REF-MAT-001's bulk TENSILE figure for unreinforced PETG (a proxy, not a
//     bending test), and 77 MPa is REF-MAT-002's ASTM D790 three-point
//     FLEXURAL figure for 20 % CF-PETG — not a tensile figure.  Neither is an
//     interlayer allowable, and neither is orientation-qualified.  Do not
//     re-label either one.
//
// -----------------------------------------------------------------------------
// PRINT
// -----------------------------------------------------------------------------
//   Orientation : FLAT — gear axis VERTICAL, gear face in the XY build plane.
//                 Both parts are authored already in this orientation, so the
//                 exported STL needs no re-posing in the slicer.
//                 WHY: layer lines are like wood grain — strong along, splits
//                 between.  Printed flat, a tooth's bending load runs IN the
//                 layer plane (the strong direction) instead of across the
//                 layer interfaces, so a tooth cannot be peeled off at its
//                 root.  The COST of this orientation is that the crank arm
//                 and the ball-stud boss become vertical built-up features
//                 whose INTERLAYER direction takes the ball-stud load — which
//                 is precisely why the stud is a through-bolt / heat-set
//                 insert and never a plastic thread (see BALL_* below).
//   Material    : CF-PETG (20 % chopped CF, REF-MAT-002 fraction)
//   Layer       : 0.15 mm
//   Nozzle      : 0.4 mm
//   Perimeters  : 4
//   Infill      : 60 % minimum (gears; the tooth band prints effectively solid
//                 at 4 perimeters over a 4.0 mm face) — matches the existing
//                 gear-part spec in this repo (nacelle_trunnion.scad,
//                 nacelle_nozzle_pushrod.scad).
//   Quantity    : sync_sun() x 2 (one per nacelle), sync_pinion_crank() x 2.
//
//   MASS — solid volumes MEASURED off the rendered meshes (trimesh, 2026-09-09);
//   the density is the estimate, not the geometry:
//     sun    2.909 cm^3 -> 0.0083 lbm (3.78 g)
//     pinion 2.897 cm^3 -> 0.0083 lbm (3.77 g)
//     ship set (2 nacelles, 4 parts) 11.61 cm^3 -> 0.0333 lbm (15.1 g)
//   The 1.30 g/cm^3 printed density assumed here is a typical PETG-CF value
//   and is NOT a figure REFERENCES.md carries; treat the masses as estimates
//   until a coupon is weighed.  These parts REPLACE a deleted/archived gear
//   train (sector gear, Pinion A, bevel pair, bevel housing, internal ring),
//   so the net airframe change is a mass REDUCTION.
//
// -----------------------------------------------------------------------------
// OPEN VERIFY ITEMS (WBS §1.1.3) — read before printing
// -----------------------------------------------------------------------------
// V1. SPAR DIAMETER AND SPAR MOTION — UNRESOLVED CONFLICT IN THE REPO.
//     This file is authored to the directed interface: a Ø8 tilt spar that
//     ROTATES with the nacelle, so the sun needs a Ø8.4 clearance bore for the
//     spar to pass freely through it plus a separate bolted attachment to the
//     wing-tip structure (SUN_BORE_D / SUN_PAD_* below).  That matches
//     nacelle_nozzle_pushrod.scad (SPAR_OD = 8.0, "rotating tilt spar").
//     IT DOES NOT MATCH the Rev T1/T4 joint as built elsewhere:
//       * nacelle_trunnion.scad SPAR_OD = 20.0 — the spar is a FIXED
//         20 x 16.3 mm carbon tube BONDED INTO THE WING that stops outside the
//         duct (docs/WING_ATTACH_INTERFACE.md §4.3a); the nacelle rotates on it
//         through the trunnion's 2 x 6704 bearings.
//       * wings_s1223_revo.scad marks the relocated fixed R22 sector mount
//         SUPERSEDED and states "plan 004 KTD3 now re-datums the nozzle sync
//         gear onto the FIXED TRUNNION on the nacelle side, so no gear mounts
//         on the wing tip under Rev T1 either."
//       * docs/plans/2026-08-29-004-...-plan.md KTD3: "The tilt ring and the
//         nozzle sync gear are coaxial at the trunnion, one rotating and one
//         fixed"; its closeout records "KTD3 half-holds ... the nozzle sync
//         gear (U5) is not built".
//     If KTD3 governs, the ONLY changes needed here are (a) SUN_BORE_D 8.4 ->
//     20.4 and the pad/bolt circle grown to suit, and (b) the sun's datum
//     becomes the fixed spar / fixed trunnion race rather than a wing-tip rib.
//     The TOOTH GEOMETRY, the centre distance, the pinion and the crank are
//     unaffected either way.  Nothing here is printed until this is settled.
// V2. SUN WING-TIP ATTACHMENT DETAIL — the SOURCE follow-up the trade amendment
//     names ("reconcile the wing R22 sector to the chosen 1:1 sun").  The three
//     M3 pads below are a placeholder of the right shape, not a reconciled
//     interface: wings_s1223_revo.scad's FIX_GEAR_* bolt circle (R11, 3 x M2.5
//     heat-set inserts, 120 deg) is marked SUPERSEDED and NOT REFERENCED, and
//     the wing tip station is congested (plan 004 RISK-1: spar bore + register
//     pad + AK7455 pocket + drive-shaft bushing boss + nav-conduit exit, with
//     only 2.10 mm either side of the encoder pocket).  The sun's pads MUST be
//     placed against that as-built congestion before any wing insert is drilled.
// V3. CENTRE DISTANCE 26.4 vs 26.0 — this file uses SYNC_CD = 26.4 mm (= the
//     33T/module-0.8 pitch diameter, the only value a 1:1 standard-centre mesh
//     can have).  nacelle_nozzle_pushrod.scad still carries SYNC_CD = 26.0 and
//     SYNC_R = 13.0 from the pre-tooth-count solve, and derives the pinion axis
//     station as PIVOT_Z + SYNC_CD = 133.5.  With 26.4 that station becomes
//     107.5 + 26.4 = 133.9.  tools/nozzle_linkage_check.py must be re-run at
//     26.4 and the pushrod file's constant updated; a 0.4 mm centre-distance
//     shift is small but it is NOT zero, and this file must not silently own
//     that edit (scope: the pushrod file is not modified here).
// V4. BALL-CENTRE AXIAL OFFSET NOT IN THE LINKAGE MODEL — the solver places the
//     crank ball IN the mesh plane (x = SUN_XLOC = -38.0).  Physically it
//     cannot be: CRANK_R = 8.5 is INSIDE the 14.0 tip radius, so the arm and
//     boss must be stacked axially clear of the gear face.  As built the ball
//     centre sits BALL_CTR_Z = 10.5 mm off the build-plate face, i.e. ~8.5 mm
//     INBOARD of the tooth-band mid-plane.  Re-run
//     tools/nozzle_linkage_check.py with that offset before printing; the
//     pushrod becomes a slightly skewed RSSR link rather than the planar case.
// V5. PINION AXIAL RETENTION — the Ø4 stub axle needs a shoulder at the wall
//     and a washer/E-clip outboard of the journal to keep the pinion on it.
//     That hardware belongs to the nacelle wall boss, not to this part; it is
//     not in the BOM yet.
// =============================================================================


// =============================================================================
// ── Parameter block ───────────────────────────────────────────────────────────
// =============================================================================

$fn = 96;                       // matches nacelle_trunnion.scad

// ── Shared gear geometry (BOTH members are identical — 1:1) ──────────────────
// The pair is a 1:1 mesh, so the sun and the pinion have the SAME tooth
// geometry and are generated from one profile function; only their hubs differ.
SYNC_M          =   0.8;   // [mm] module.  DELIBERATELY the repo-wide
                           //      tilt-drivetrain module — the wing 14T tilt
                           //      pinion, the trunnion 50T tilt ring (WA-R8)
                           //      and the fuselage 38T/38T stage are all
                           //      module 0.8.  One module across the airframe
                           //      means one hob/print-calibration answer and
                           //      one set of tooth-fit lessons; a second
                           //      module here would buy nothing and cost that.
SYNC_Z          =  33;     // [count] teeth, BOTH members
SYNC_PA         =  20.0;   // [deg] pressure angle, full depth
SYNC_FACE       =   4.0;   // [mm] face width.  b/m = 5.0, which is BELOW the
                           //      conventional 6-12 x module band, and that is
                           //      DELIBERATE: the face width is set by the
                           //      ~8 mm wing-tip <-> nacelle axial gap budget,
                           //      which must also house the tip bearing, the
                           //      Hall ring magnet and the AK7455 stack — NOT
                           //      by tooth stress.  Tooth stress is 10.94 MPa
                           //      against a >= 48.41 MPa allowable (FOS 4.43,
                           //      see the header), so widening the face would
                           //      spend gap millimetres to relieve a load that
                           //      is already a factor of four clear.  This is
                           //      the same argument nacelle_trunnion.scad
                           //      GEAR_FACE makes for the tilt ring.
SYNC_BACKLASH   =   0.15;  // [mm] circumferential backlash, TOTAL, taken out
                           //      of the TOOTH THICKNESS — not by opening the
                           //      centre distance.  CD is fixed by the solved
                           //      linkage (SYNC_CD below is both the pitch
                           //      diameter and the pinion's station off the
                           //      spar axis), so it is not available as a fit
                           //      adjustment.  Thinning the tooth is also the
                           //      right answer for an FDM gear, where the real
                           //      error is extrusion width, not centre
                           //      location.  Implementation: the flank
                           //      half-angle is reduced by
                           //      SYNC_BACKLASH / (2 * pitch_radius) radians
                           //      -> SYNC_BL_ANG degrees; see flank_angle().
                           //      NOTE, honestly: applying that to BOTH
                           //      identical members removes SYNC_BACKLASH from
                           //      each tooth, so the assembled mesh sees
                           //      ~2 x 0.15 = 0.30 mm of circumferential play
                           //      at the pitch line.  That is the directed
                           //      implementation and it is the safe direction
                           //      for a first print (a tight mesh binds; a
                           //      loose one costs lost motion).  VERIFY on the
                           //      first printed pair: if the measured play is
                           //      unacceptable in the exit-area schedule, halve
                           //      this value rather than moving CD.

// Derived tooth circles.  Transcribed targets: pitch Ø26.4, tip Ø28.00, root
// Ø24.40, base Ø = 26.4 * cos(20 deg).
SYNC_PD         = SYNC_M * SYNC_Z;                 // = 26.40 mm pitch diameter
SYNC_PR         = SYNC_PD / 2;                     // = 13.20 mm pitch radius
SYNC_RA         = SYNC_PR + SYNC_M;                // = 14.00 mm tip radius
SYNC_RF         = SYNC_PR - 1.25 * SYNC_M;         // = 12.20 mm root radius
SYNC_RB         = SYNC_PR * cos(SYNC_PA);          // = 12.4045 mm base radius
SYNC_CD         = SYNC_PD;                         // = 26.40 mm centre distance
                                                   //   (1:1 standard centres)

// No profile shift.  Z = 33 is far above the 17-tooth undercut floor for a
// 20 deg full-depth rack-generated tooth, so there is nothing to correct and a
// shift would only break the 1:1 interchangeability of the two blanks.
SYNC_SHIFT      =   0.0;   // [mm] retained as an explicit zero, not an omission

// Backlash as an angle at the pitch circle (see SYNC_BACKLASH).
SYNC_BL_ANG     = SYNC_BACKLASH / (2 * SYNC_PR) * 180 / PI;   // = 0.32554 deg

// ── First-layer ("elephant foot") chamfer on the tooth band ─────────────────
SYNC_CHAM       =   0.4;   // [mm] 0.4 x 45 deg chamfer on the BOTTOM face of
                           //      the tooth band — the build-plate face.  First
                           //      layers squish outward; on a module-0.8 tooth
                           //      an unrelieved 0.1-0.2 mm of elephant foot is
                           //      a large fraction of the 0.15 mm design
                           //      backlash and will jam the mesh at the first
                           //      layer even though the rest of the face is
                           //      correct.  Chamfering the first 0.4 mm keeps
                           //      the squish inside the part outline.
                           //
                           //      HOW IT IS IMPLEMENTED, and why not as a
                           //      constant-normal offset: at m = 0.8 the tip
                           //      LAND is only 0.459 mm wide, so insetting the
                           //      profile 0.4 mm along its normal (OpenSCAD
                           //      offset(r = -0.4)) would consume the entire
                           //      land and truncate every tooth.  The chamfer
                           //      is therefore cut as a RADIAL taper (a uniform
                           //      2D scale about the gear axis) over the first
                           //      SYNC_CHAM of height: it delivers the full
                           //      0.4 mm of relief at the tip circle, ~0.35 mm
                           //      at the root circle, and thins the tooth
                           //      circumferentially by only ~0.03 mm at the
                           //      pitch line — in the loose (safe) direction,
                           //      on the one layer that is going to grow
                           //      anyway.  The 45 deg nominal is held at the
                           //      tip, where elephant foot actually interferes.
SYNC_CHAM_S     = (SYNC_RA - SYNC_CHAM) / SYNC_RA; // = 0.971429 radial scale

// ── Sun hub / wing attachment ───────────────────────────────────────────────
// See header V1 and V2 — this whole block is the unreconciled half of the part.
SPAR_OD         =   8.0;   // [mm] tilt spar OD as carried by
                           //      nacelle_nozzle_pushrod.scad.  SEE V1: the
                           //      Rev T1/T4 joint elsewhere in this repo uses a
                           //      FIXED Ø20 CF spar.  One line changes if KTD3
                           //      governs.
SUN_BORE_D      = SPAR_OD + 0.4;   // = 8.40 mm.  CLEARANCE, not a fit: under
                           //      the interface this file is authored to, the
                           //      spar ROTATES WITH THE NACELLE and the sun is
                           //      FIXED TO THE WING, so the spar must pass
                           //      freely through the sun.  0.2 mm per side is
                           //      the running clearance used elsewhere in the
                           //      nacelle stack (PILOT_CLEAR = 0.3 at the
                           //      trunnion pilot is the same order).  The sun
                           //      is NOT a bearing — it must never be the
                           //      spar's radial support; that is the tip
                           //      bearing's job.
SUN_PAD_OD      =  24.0;   // [mm] bolted mounting pad OD.  Sized to sit fully
                           //      INSIDE the root circle (Ø24.40) so the pad
                           //      does not overhang the tooth roots when the
                           //      part is printed teeth-down — a 0.2 mm ring
                           //      overhang would print as a drooping lip right
                           //      at the tooth root, the one place this part
                           //      cannot afford a defect.
SUN_PAD_T       =   3.0;   // [mm] pad thickness.  3.0 = 20 x the 0.15 mm layer
                           //      and enough seat depth for an M3 head bearing
                           //      on printed material without dishing.
SUN_BC_D        =  17.0;   // [mm] bolt circle, 3 x M3 at 120 deg.  At r = 8.5
                           //      each Ø3.3 bore leaves 2.65 mm of wall to the
                           //      Ø8.4 bore and 1.85 mm to the pad rim — both
                           //      above the 1.6 mm that 4 perimeters at 0.4 mm
                           //      needs.
SUN_BOLT_D      =   3.3;   // [mm] M3 clearance bore (repo M3_CLEAR_D)
SUN_N_BOLTS     =   3;     // [count] 120 deg spacing — three points fully
                           //      constrain a flat pad and cannot rock

// ── Pinion journal (plain bearing on a Ø4 steel stub axle) ──────────────────
PIN_AXLE_D      =   4.0;   // [mm] Ø4 steel stub axle, bonded into the nacelle
                           //      wall.  The pinion turns on it directly.
PIN_BORE_D      =   4.3;   // [mm] printed journal bore — ream/scrape to fit.
                           //      Same convention and the same words as
                           //      nacelle_trunnion.scad BRG_SEAT_D ("H7 seat
                           //      bore (printed; ream/scrape to fit)"): an FDM
                           //      hole comes out undersize and lobed, so it is
                           //      printed nominally loose and finished by hand
                           //      on assembly.
                           //
                           //      WHY A PLAIN JOURNAL AND NOT A BALL BEARING:
                           //      the worst-case journal load is ~13 N and the
                           //      duty is only a few hundred conversion cycles
                           //      over the airframe's life (each transition is
                           //      one stroke).  PV and total revolutions are
                           //      both trivial; a bearing here would add mass,
                           //      a seat bore, a retention feature and two more
                           //      BOM lines to solve a wear problem the duty
                           //      cycle does not create.
PIN_JOURNAL_OD  =  10.0;   // [mm] journal boss OD -> 2.85 mm wall around the
                           //      Ø4.3 bore, comfortably over 4 perimeters
PIN_JOURNAL_TOP =  12.0;   // [mm] top of the journal boss in the part frame.
                           //      Bore length = 12.0 mm = 2.8 x bore diameter,
                           //      over the >= 2 x D (8.6 mm) needed to keep a
                           //      short plain journal from cocking on its shaft
                           //      (a 4 mm-long bore on a 4 mm shaft is a hinge,
                           //      not a journal).

// ── Crank (co-printed into the pinion) ──────────────────────────────────────
CRANK_R         =   8.5;   // [mm] ball-stud radius on the crank (the moment
                           //      arm).  SOLVED value, unchanged since the
                           //      2026-07-19 amendment — do not touch without
                           //      re-running tools/nozzle_linkage_check.py.
                           //      NOTE it is INSIDE the Ø28.00 tip circle
                           //      (14.0 tip radius), which is exactly why the
                           //      arm and boss are STACKED axially clear of the
                           //      gear face instead of lying in the gear plane.
CRANK_PHASE     = 206.4;   // [deg] crank clocking at ZERO TILT, measured about
                           //      the pinion axis.  This is an ASSEMBLY
                           //      clocking, not a moulded-in feature: the
                           //      pinion spins free on its stub axle, so its
                           //      tooth-to-arm relationship is established when
                           //      it is dropped into mesh with the sun at zero
                           //      tilt, and the part-local azimuth the arm is
                           //      drawn at below is only a datum for drawings
                           //      and for the "asm" preview.  The linkage
                           //      solver's convention (nacelle frame) is
                           //        y = CRANK_R * sin(theta + CRANK_PHASE)
                           //        z = pinion_axis_z
                           //            + CRANK_R * cos(theta + CRANK_PHASE)
                           //      and 206.4 deg is what makes psi(0) ~= 0 (no
                           //      re-clocking of the ring cam) while keeping
                           //      the 0->90 deg sweep monotonic.
CRANK_ARM_T     =   3.0;   // [mm] crank arm plate thickness (20 layers).  The
                           //      arm is a plate in bending about its own
                           //      plane, loaded 13 N at 8.5 mm; 3.0 mm printed
                           //      flat puts that bending IN the layer plane.
CRANK_ARM_Z0    = SYNC_FACE;        // arm sits directly on the gear band's
                                    // inboard face — INBOARD is away from the
                                    // wing, the only side with room.  Nothing
                                    // in this part except the tooth band itself
                                    // enters the ~8 mm wing-tip gap.
CRANK_ARM_Z1    = CRANK_ARM_Z0 + CRANK_ARM_T;   // = 7.0

// ── Ball-stud boss ──────────────────────────────────────────────────────────
BALL_STUD_D     =   3.0;   // [mm] COTS ball diameter (3 mm ball / M3 shank RC
                           //      ball stud, steel) — matches the ball cups on
                           //      the pushrod and the ring lever ear
BALL_HOLE_D     =   3.4;   // [mm] M3 CLEARANCE through-hole (standard M3
                           //      clearance).  NOT a tapped hole.
                           //      WHY: printed flat, this hole's axis runs
                           //      along the build Z, so a plastic thread here
                           //      would be loaded in the INTERLAYER direction —
                           //      pulling the stud would peel layers apart
                           //      rather than shear thread flanks, and
                           //      interlayer strength is the one allowable this
                           //      repository cannot cite at all (see the header
                           //      honesty note).  The load path is therefore
                           //      taken entirely in steel: the ball stud's M3
                           //      shank passes through the arm and the gear
                           //      band and is captured by a WASHER + NYLOC NUT
                           //      on the back (wing-side, z = 0) face, so the
                           //      plastic sees compression between two steel
                           //      faces instead of tension across layers.  A
                           //      heat-set brass insert is the acceptable
                           //      alternative if the back face turns out to be
                           //      inaccessible after assembly; the through-bolt
                           //      is preferred because it needs no interlayer
                           //      strength at all.
                           //      Stud length: grip is BALL_BOSS_TOP = 9.0 mm
                           //      of plastic plus washer plus nut, so specify
                           //      an M3 ball stud with a shank >= 12 mm.
BALL_BOSS_OD    =   8.0;   // [mm] boss OD -> 2.3 mm wall around the Ø3.4 hole
BALL_BOSS_TOP   =   9.0;   // [mm] boss top = the ball stud's seat face, 2.0 mm
                           //      proud of the arm so the ball clears the arm
                           //      and the pushrod cup can articulate
BALL_FILLET_R   =   1.5;   // [mm] generous fillet at the boss/arm junction.
                           //      This is the part's real stress concentration:
                           //      a 13 N side load at the top of a 9 mm-tall
                           //      built-up boss is a cantilever with its root
                           //      exactly at a printed corner.  A 1.5 mm radius
                           //      is 10 layers of transition, and it also gives
                           //      the slicer somewhere to put continuous
                           //      perimeters instead of a stack of 90 deg
                           //      corners.
BALL_WEB_T      =   2.4;   // [mm] gusset web thickness (6 x 0.4 nozzle)
BALL_CTR_Z      = BALL_BOSS_TOP + BALL_STUD_D / 2;   // = 10.5 mm, see V4
BORE_CHAM       =   0.3;   // [mm] first-layer relief chamfer at every bore
                           //      mouth on the build-plate face — same
                           //      elephant-foot argument as the tooth band,
                           //      and on the ball-stud hole it doubles as the
                           //      washer's seating relief


// =============================================================================
// ── Involute spur-gear profile (REUSED from nacelle_trunnion.scad) ───────────
// =============================================================================
// This is the same first-principles 20 deg full-depth involute generator that
// nacelle_trunnion.scad uses for the 50T tilt ring (WA-R8) at this same module
// 0.8 — reproduced here rather than re-invented, and rather than cross-included
// (the trunnion file is a self-contained part file with its own constants and
// its own top-level geometry; including it would drag in the trunnion body).
// Structure, naming and derivation are deliberately identical so the two files
// read the same way:
//   inv_rad(a)     involute function inv(a) = tan(a) - a, in RADIANS.
//                  OpenSCAD trigonometry is in DEGREES, so the "- a" term is
//                  converted explicitly.
//   flank_angle(r) half tooth angle at radius r, in degrees, measured from the
//                  tooth centreline.
//   tooth_pts()    one tooth as a closed polygon centred on angle 0.
//   sync_gear_2d() the full 2D gear: root cylinder + SYNC_Z teeth.
// The only functional addition over the trunnion version is the SYNC_BL_ANG
// backlash term and the sub-base-circle radial extension described below.
function inv_rad(a) = tan(a) - a * PI / 180;                    // radians

// Half tooth angle at radius r.
//   90/Z                      half the angular tooth thickness at the pitch
//                             circle for a standard (unshifted) tooth
//   (inv(PA) - inv(alpha_r))  the involute's own angular unwind between the
//                             pitch circle and radius r, alpha_r = acos(RB/r)
//   - SYNC_BL_ANG             BACKLASH: the whole flank is rotated toward the
//                             tooth centreline by a constant angle, thinning
//                             the tooth by SYNC_BACKLASH at the pitch line
//                             while leaving the involute's SHAPE — and hence
//                             the conjugate action and the pressure angle —
//                             untouched.  This is the standard way to cut
//                             backlash into a gear (thin the tooth, hold the
//                             centres); opening the centre distance instead
//                             would move the pinion off the station the linkage
//                             solve fixed.
//   max(r, SYNC_RB)           at 33T the ROOT circle (12.200) falls 0.205 mm
//                             INSIDE the base circle (12.4045) — the opposite
//                             of the trunnion's 50T case, where RF > RB and the
//                             flank was involute all the way down.  An involute
//                             does not exist below its base circle, so the
//                             clamp holds the flank angle constant there,
//                             producing a plain RADIAL extension from the base
//                             circle down to the root circle.  That is the
//                             conventional construction, it keeps the true root
//                             diameter at the specified Ø24.40, and it is below
//                             the active flank: in a 1:1 mesh at standard
//                             centres, contact never reaches either base
//                             circle.
function flank_angle(r) = 90 / SYNC_Z
                        + (inv_rad(SYNC_PA)
                           - inv_rad(acos(SYNC_RB / max(r, SYNC_RB))))
                          * 180 / PI
                        - SYNC_BL_ANG;

// Sample radii from the ROOT circle out to the tip circle.  12 stations puts
// ~0.16 mm between points on a 1.8 mm-tall tooth flank — finer than both the
// 0.15 mm layer height and the 0.4 mm extrusion width, so the faceting is
// below what the printer can resolve.
SYNC_STEPS   = 12;
function gear_r(i) = SYNC_RF + (SYNC_RA - SYNC_RF) * i / (SYNC_STEPS - 1);

// One tooth as a closed polygon, centred on angle 0: up the -flank, back down
// the +flank.
function tooth_pts() = concat(
        [ for (i = [0 : SYNC_STEPS - 1])
              let (r = gear_r(i), a = -flank_angle(r))
                  [r * cos(a), r * sin(a)] ],
        [ for (i = [SYNC_STEPS - 1 : -1 : 0])
              let (r = gear_r(i), a =  flank_angle(r))
                  [r * cos(a), r * sin(a)] ]);

// Sanity checks on the transcribed numbers — these are asserts, not
// derivations: they fail loudly if someone edits a constant into an
// inconsistent set.
assert(abs(SYNC_PD - 26.40) < 1e-9, "pitch diameter must be 26.40 mm");
assert(abs(2 * SYNC_RA - 28.00) < 1e-9, "tip diameter must be 28.00 mm");
assert(abs(2 * SYNC_RF - 24.40) < 1e-9, "root diameter must be 24.40 mm");
assert(abs(SYNC_CD - 26.40) < 1e-9, "centre distance must be 26.40 mm");
assert(SYNC_Z >= 17, "Z below the 17T undercut floor would need a profile shift");
// Adjacent teeth must not touch at the root: half tooth angle at the root
// circle must stay under the half angular pitch (180/Z = 5.4545 deg).
assert(flank_angle(SYNC_RF) < 180 / SYNC_Z,
       "tooth is too thick at the root circle - teeth would interfere");
// The tip land must survive the backlash cut.
assert(flank_angle(SYNC_RA) > 0, "backlash cut has consumed the tip land");

// The 2D gear: a root cylinder plus SYNC_Z teeth.  The root cylinder is drawn
// 0.01 mm proud of the root circle so the tooth polygons and the cylinder
// overlap rather than merely touch (a zero-width contact is the classic source
// of non-manifold output in this repo — see MEMORY "SCAD manifold fixes").
module sync_gear_2d() {
    union() {
        circle(r = SYNC_RF + 0.01);
        for (i = [0 : SYNC_Z - 1])
            rotate([0, 0, i * 360 / SYNC_Z]) polygon(tooth_pts());
    }
}

// The 3D tooth band, SHARED by both members: z = 0 at the build-plate face,
// with the first SYNC_CHAM of height radially tapered as the elephant-foot
// chamfer (see SYNC_CHAM for why this is a radial taper and not an offset).
module sync_gear_band() {
    union() {
        // Chamfered first 0.4 mm: bottom = SYNC_CHAM_S x profile, top = profile
        linear_extrude(height = SYNC_CHAM, scale = 1 / SYNC_CHAM_S)
            scale([SYNC_CHAM_S, SYNC_CHAM_S]) sync_gear_2d();
        // Full-section remainder of the face
        translate([0, 0, SYNC_CHAM])
            linear_extrude(height = SYNC_FACE - SYNC_CHAM) sync_gear_2d();
    }
}

// A bore-mouth chamfer cone, to be subtracted at a bore on the z = 0 face.
// Cut as a cone from (d + 2*BORE_CHAM) at z = -eps up to d at z = BORE_CHAM.
module bore_mouth_chamfer(d) {
    translate([0, 0, -0.01])
        cylinder(h = BORE_CHAM + 0.01,
                 d1 = d + 2 * BORE_CHAM + 0.02, d2 = d);
}


// =============================================================================
// ── Module: sync_sun() — the WING-FIXED 33T sun ───────────────────────────────
// =============================================================================
// Print frame: gear axis = local +Z, z = 0 at the build plate = the chamfered
// tooth-band face.  Teeth DOWN, mounting pad UP, so the teeth get the flat
// first-layer treatment and the pad's bolt bores are printed as clean vertical
// holes.  In the installed pose the pad faces the WING and the tooth band faces
// INBOARD toward the nacelle (the "asm" preview flips the part accordingly).
//
// The sun is the drive's GROUND: it must not rotate, and it must not carry the
// spar.  Hence a clearance bore (SUN_BORE_D) for the rotating spar to pass
// through, and three M3 pads that take the reaction torque into wing-tip
// structure.  Reaction torque is small — 12.88 N at the 13.2 mm pitch radius is
// 0.170 N*m — but it REVERSES every transition, so the attachment must be
// bolted, not bonded-in-shear-only.
//
// VERIFY (header V1, V2): both the bore diameter and the pad interface are
// UNRECONCILED.  The wing-tip attachment detail must be reconciled against the
// wing's relocated/SUPERSEDED R22 sector stub in
// airframe/openscad/wings/wings_s1223_revo.scad (FIX_GEAR_BC_R = 11.0,
// 3 x M2.5 heat-set inserts at 120 deg, marked SUPERSEDED and NOT REFERENCED)
// and against plan 004's KTD3 re-datum onto the fixed trunnion.  The trade
// amendment names this as a SOURCE follow-up ("reconcile the wing R22 sector to
// the chosen 1:1 sun").  DO NOT drill wing inserts to the bolt circle below
// until that is closed.
module sync_sun() {
    difference() {
        union() {
            // Tooth band, z = 0 .. SYNC_FACE.  The band is a solid disc from
            // the bore out to the teeth: the rim below the root circle is
            // 12.20 - 4.20 = 8.00 mm, far above the 1.2 x m = 0.96 mm
            // conventional minimum rim under a gear root.
            sync_gear_band();

            // Bolted mounting pad, immediately above the band.  Kept inside the
            // root circle so it never overhangs a tooth root (see SUN_PAD_OD).
            translate([0, 0, SYNC_FACE])
                cylinder(h = SUN_PAD_T, d = SUN_PAD_OD);
        }

        // Spar clearance bore, through everything.
        translate([0, 0, -1])
            cylinder(h = SYNC_FACE + SUN_PAD_T + 2, d = SUN_BORE_D);
        bore_mouth_chamfer(SUN_BORE_D);

        // 3 x M3 clearance bores through the pad AND the band, so the bolt
        // clamps the full 7.0 mm stack against the wing-tip face rather than
        // just the 3.0 mm pad.
        for (i = [0 : SUN_N_BOLTS - 1])
            rotate([0, 0, i * 360 / SUN_N_BOLTS])
                translate([SUN_BC_D / 2, 0, 0]) {
                    translate([0, 0, -1])
                        cylinder(h = SYNC_FACE + SUN_PAD_T + 2,
                                 d = SUN_BOLT_D);
                    bore_mouth_chamfer(SUN_BOLT_D);
                }
    }
}


// =============================================================================
// ── Module: sync_pinion_crank() — the NACELLE 33T pinion + integral crank ────
// =============================================================================
// ONE PART (see "WHY THE PINION AND THE CRANK ARE ONE PART" in the header).
//
// Print frame: gear axis = local +Z, z = 0 at the build plate = the chamfered
// tooth-band face.  In the installed pose that face looks OUTBOARD into the
// wing-tip joint gap (it is the mesh plane), and everything else — arm, ball
// boss, journal barrel — stacks INBOARD on +Z where the nacelle has room.  The
// only thing this part puts into the ~8 mm wing-tip gap is the 4.0 mm tooth
// band itself, plus the M3 washer and nut on the back of the ball-stud hole
// (~2.9 mm proud at r = 8.5 mm from the pinion axis, well clear of the on-axis
// bearing/Hall/AK7455 stack, which sits 26.4 mm away at the spar axis — VERIFY
// against the as-built tip congestion, plan 004 RISK-1).
//
// The additive stack, build plate upward:
//   0.0 .. 4.0   tooth band (solid disc, Ø4.3 journal bore through it)
//   4.0 .. 7.0   crank arm plate — a hull from the journal boss out to a
//                circular pad under the ball boss (a teardrop web, so the boss
//                fillet lands on supported material rather than in mid-air)
//   4.0 .. 9.0   ball-stud boss, Ø8.0, at CRANK_R, axis PARALLEL to the pinion
//                axis (so the ball stud, the pushrod cup and the ring-lever
//                ball all share the nacelle's spar-parallel direction)
//   7.0 .. 9.0   gusset web tying the boss back into the journal barrel
//   4.0 .. 12.0  journal barrel, Ø10.0 over the Ø4.3 bore
module sync_pinion_crank() {
    difference() {
        union() {
            // ── Tooth band ──────────────────────────────────────────────────
            sync_gear_band();

            // ── Journal barrel ──────────────────────────────────────────────
            // Rises from the band's inboard face to PIN_JOURNAL_TOP, giving a
            // 12.0 mm long bore on a 4 mm shaft (see PIN_JOURNAL_TOP).
            translate([0, 0, SYNC_FACE])
                cylinder(h = PIN_JOURNAL_TOP - SYNC_FACE, d = PIN_JOURNAL_OD);

            // ── Crank arm plate ─────────────────────────────────────────────
            // hull() from the journal barrel to a circular pad of radius
            // (BALL_BOSS_OD/2 + BALL_FILLET_R) centred under the ball boss.
            // The pad radius is what makes the boss fillet land on material:
            // 4.0 + 1.5 = 5.5 mm, exactly the fillet's outer reach.  The pad's
            // far edge sits at 8.5 + 5.5 = 14.0 mm = the tip radius, so the arm
            // never oversails the tooth tips.
            translate([0, 0, CRANK_ARM_Z0])
                linear_extrude(height = CRANK_ARM_T)
                    hull() {
                        circle(d = PIN_JOURNAL_OD);
                        translate([CRANK_R, 0])
                            circle(r = BALL_BOSS_OD / 2 + BALL_FILLET_R);
                    }

            // ── Ball-stud boss ──────────────────────────────────────────────
            translate([CRANK_R, 0, CRANK_ARM_Z0])
                cylinder(h = BALL_BOSS_TOP - CRANK_ARM_Z0, d = BALL_BOSS_OD);

            // ── Fillet at the boss / arm junction ───────────────────────────
            // A concave ring of revolution seated on the arm's top face.  This
            // is the part's governing stress concentration (see BALL_FILLET_R).
            translate([CRANK_R, 0, 0])
                rotate_extrude(angle = 360)
                    translate([BALL_BOSS_OD / 2, CRANK_ARM_Z1])
                        difference() {
                            square([BALL_FILLET_R, BALL_FILLET_R]);
                            translate([BALL_FILLET_R, BALL_FILLET_R])
                                circle(r = BALL_FILLET_R);
                        }

            // ── Gusset web, boss -> journal barrel ──────────────────────────
            // A triangular web in the arm's radial plane, full height at the
            // boss and tapering to nothing at the journal barrel.  It carries
            // the boss's overturning moment back into the barrel instead of
            // letting the 3.0 mm arm plate take it all as plate bending, and it
            // does so along a printed direction that is IN the layer plane.
            rotate([90, 0, 0])
                linear_extrude(height = BALL_WEB_T, center = true)
                    polygon([[PIN_JOURNAL_OD / 2, CRANK_ARM_Z1],
                             [CRANK_R,            CRANK_ARM_Z1],
                             [CRANK_R,            BALL_BOSS_TOP]]);
        }

        // ── Journal bore, through the whole part ────────────────────────────
        translate([0, 0, -1])
            cylinder(h = PIN_JOURNAL_TOP + 2, d = PIN_BORE_D);
        bore_mouth_chamfer(PIN_BORE_D);

        // ── Ball-stud through-hole, through boss + arm + tooth band ─────────
        // Steel-to-steel load path: stud shank through the plastic, washer and
        // nyloc nut on the z = 0 face.  NOT tapped — see BALL_HOLE_D.
        translate([CRANK_R, 0, 0]) {
            translate([0, 0, -1])
                cylinder(h = BALL_BOSS_TOP + 2, d = BALL_HOLE_D);
            bore_mouth_chamfer(BALL_HOLE_D);
        }
    }
}


// =============================================================================
// ── Render selection ─────────────────────────────────────────────────────────
// =============================================================================
// Part selection is via the RENDER_PART -D string parameter, matching the
// pattern used by nacelle_nozzle_iris.scad and nacelle_nozzle_pushrod.scad:
//   RENDER_PART = "sun"     -> sync_sun()            (printed x 2)
//   RENDER_PART = "pinion"  -> sync_pinion_crank()   (printed x 2)
//   RENDER_PART = "asm"     -> the meshed pair       (DEFAULT; preview only,
//                              NOT a printable body)
//
// Build (see airframe/FreeCAD-scripts/Makefile):
//   openscad -D 'RENDER_PART="sun"'    -o <out> nacelle_nozzle_sync_gears.scad
//   openscad -D 'RENDER_PART="pinion"' -o <out> nacelle_nozzle_sync_gears.scad
RENDER_PART = "asm";   // "sun" | "pinion" | "asm"

// ── Assembly preview ────────────────────────────────────────────────────────
// Shared MESH frame: the tooth bands of both members occupy z = 0 .. SYNC_FACE,
// +Z is INBOARD (away from the wing) and -Z is toward the wing.  The sun is
// shown FLIPPED (rotate 180 deg about X, then lifted by SYNC_FACE) so its
// mounting pad faces the wing at -Z while the pinion's crank stack rises
// inboard at +Z; that flip is why the two printed parts' chamfered faces end up
// on OPPOSITE sides of the mesh plane, which is harmless (the chamfer is
// first-layer relief, not a functional face).  Flipping about X maps azimuth
// a -> -a and the tooth is symmetric about its centreline, so the flip does not
// disturb the tooth clocking.
//
// TOOTH CLOCKING: SYNC_Z = 33 is ODD, so the direction from the pinion back
// toward the sun (azimuth 180 deg in the pinion's frame) falls exactly half a
// pitch from a tooth centre — a SPACE centre.  Drawing both members identically,
// with a tooth centred on azimuth 0, therefore meshes them correctly at
// SYNC_CD with no additional index rotation.  (This is only true for odd Z; a
// future even-Z variant would need a half-pitch index on one member.)
//
// The crank is drawn at part-local azimuth CRANK_PHASE = 206.4 deg, the zero-
// tilt pose.  As noted at CRANK_PHASE, that clocking is established at ASSEMBLY
// when the pinion is set into mesh, not by the printed geometry.
if (RENDER_PART == "sun") {
    sync_sun();
} else if (RENDER_PART == "pinion") {
    sync_pinion_crank();
} else {
    // Wing-fixed sun at the origin, flipped pad-to-wing.
    translate([0, 0, SYNC_FACE]) rotate([180, 0, 0]) sync_sun();
    // Nacelle pinion at the centre distance, crank clocked to zero tilt.
    translate([SYNC_CD, 0, 0]) rotate([0, 0, CRANK_PHASE]) sync_pinion_crank();
}
