// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  Primary-component STLs published to airframe/stls/
//   are stored directly in hull frame, baked by tools/bake_hull_frame.py
//   (marker 'SerenityUAV HULL-FRAME R1' in the binary STL header).
//   NEVER re-bake a mesh derived from an already-baked file.
//   This file:
//     Part-local print frame, coaxial with the nacelle duct (duct axis =
//     local +Z, intake at Z = 0).  Hull placement derives from the nacelle
//     pose (cruise = 270 deg about +X + translation; hover rotates about the
//     tilt pivot at duct Z = 83 mm).  Assembly placement VERIFY pending
//     (serenity_assembly.py).
// ===========================================================================
// =============================================================================
// edf_aft_spider_sleeve.scad
// Serenity UAV — Rev R — EDF Aft Spider Sleeve
// =============================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
// Date    : 2026-05-29
// Revision: Rev R (2026-06-11)   [carried forward from Rev A (2026-05-29); no geometry changes]
//
// Description
// -----------
// Removable aft spider sleeve for the Serenity-UAV tandem-EDF nacelle
// (nacelle_pod_50mm_tandem.scad Rev T).
//
// This sleeve carries the EDF2 (aft) motor-mount spider and occupies
// nacelle Z = 122.5 … 166.25 mm (SLEEVE_L = 43.75 mm).
//
// Bore-interior axial order (nacelle coordinates):
//   intake → rotor1 → spider1 → motor1 → [stator sleeve] →
//            rotor2 → [spider2 ← this part] → motor2 → nozzle
//
// EDF2 bench pre-assembly (before nacelle installation)
// -----------------------------------------------------
//   1. No heat-set inserts required at this interface (CORRECTED 2026-09-28
//      — the motor supplies its own tapped flange; see "Motor mount" header
//      below). This sleeve only needs its 4× M2 clearance-and-countersink
//      through-holes at MOTOR_BOLT_R = 7.5 mm radius, cut in by this file.
//   2. Seat EDF2 motor forward face against spider arm aft face
//      (motor shaft extends forward through hub bore, R_HUB_BORE = 2 mm).
//   3. Drive 4× M2x12.5mm flat-head (countersunk) screws through this
//      sleeve's countersunk clearance holes (forward face) into the motor's
//      own tapped flange.  Access is via THIS PART'S OWN forward/intake
//      face with the rotor REMOVED — done at the bench, both before nacelle
//      installation and, for field service, only after extracting the whole
//      aft spider sleeve out the nacelle's AFT (nozzle) end per the removal
//      procedure below (this EDF2 assembly sits buried behind the stator
//      sleeve and EDF1; there is no in-situ path to it from the nacelle's
//      own front air intake once installed — owner-confirmed 2026-09-28:
//      that is WHY this sleeve has to come out the aft end to be serviced
//      at all). The rotor otherwise covers these screws and must come off
//      to reach them regardless.
//      Motor body protrudes aft past
//      sleeve aft face (Z_local > 43.75 mm) — this is by design; the
//      motor body occupies nacelle space between SLEEVE_Z_END and the iris
//      nozzle at NOZZLE_RING_Z.
//   4. Attach EDF2 fan rotor to motor shaft from the forward end.
//
// Nacelle installation sequence
// ------------------------------
//   1. Install EDF1 motor and stator sleeve (see edf_stator_sleeve.scad).
//   2. Slide aft spider sleeve — forward face leading — into nacelle from
//      nozzle end.  Keys at 0°/120°/240° on sleeve OD engage bore key
//      slots.  Forward face contacts stator sleeve aft face at Z = 122.5 mm.
//   3. Drive 3× M3×20 SHCS into retention bores at r = BOSS_R (28 mm)
//      in sleeve aft face (nozzle bore access with iris removed).  Screws
//      thread into M3 inserts in nacelle sleeve_retention_bosses() which
//      protrude from NOZZLE_RING_Z (Z = 166.25 mm) aft into nozzle ring.
//
//   SERVICE NOTE (owner-confirmed 2026-09-28): this retention scheme is what
//   makes field service possible at all. EDF2's motor-mount screws are only
//   reachable via THIS sleeve's own forward/intake face with the rotor off
//   (see "Motor mount" section below) — there is no path to them from the
//   nacelle's front intake once installed, because this sleeve sits buried
//   behind EDF1 and the stator sleeve. Removing these 3× M3×20 SHCS and
//   reversing step 2 (pull the sleeve out the nozzle end) is therefore the
//   ONLY service path to EDF2's motor screws or rotor.
//
// Retention summary
// -----------------
//   Forward stop : stator sleeve aft face at Z = 122.5 mm.
//   Anti-rotation: 3× longitudinal OD keys engage nacelle bore key slots.
//   Aft lock     : 3× M3×20 SHCS → nacelle boss inserts at Z ≈ 166.25 mm.
//
// Coordinate conventions
// -----------------------
//   SLEEVE-LOCAL Z: Z=0 = sleeve forward face (nacelle Z = 122.5 mm);
//                   Z=SLEEVE_L = sleeve aft face (nacelle Z = 166.25 mm).
//   Nacelle Z = SLEEVE_Z_START + Z_local.
//
// References
// ----------
//   [1] nacelle_pod_50mm_tandem.scad Rev T — mating nacelle bore geometry.
//   [2] edf_stator_sleeve.scad Rev A — forward sleeve retained by this part.
//   [3] Serenity-UAV project CLAUDE.md — fabrication standards (2026).
//
// =============================================================================


// =============================================================================
// ── Parameter Block ───────────────────────────────────────────────────────────
// =============================================================================

// ── Sleeve tube dimensions ─────────────────────────────────────────────────────
// Must match nacelle_pod_50mm_tandem.scad Rev T bore parameters.
EDF_BORE_R      =  25.0;    // [mm] EDF bore inner radius (50 mm ID)
SLEEVE_OD       =  55.0;    // [mm] sleeve outer diameter (= EDF_CASING_R × 2)
SLEEVE_WALL     =   2.5;    // [mm] wall thickness = (SLEEVE_OD − 50) / 2

// Nacelle-local Z boundaries (AFT_SLV_Z_START / END in nacelle file).
SLEEVE_Z_START  = 122.5;    // [mm] sleeve forward face (nacelle coord)
SLEEVE_Z_END    = 166.25;   // [mm] sleeve aft face     (nacelle coord)
SLEEVE_L        = SLEEVE_Z_END - SLEEVE_Z_START;  // = 43.75 mm

// ── Anti-rotation keys ─────────────────────────────────────────────────────────
// Must match nacelle SLEEVE_KEY_W / SLEEVE_KEY_H and bore_key_slots() angles.
// Angles must be identical to edf_stator_sleeve.scad for continuous slot engagement.
SLEEVE_KEY_W    =   3.0;    // [mm] key tangential width
SLEEVE_KEY_H    =   3.0;    // [mm] key radial height above sleeve OD
KEY_ROOT_OVERLAP =  0.5;    // [mm] key root sunk below the tube OD — CGAL
                            //      volumetric overlap, not a touching face

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

// ── EDF2 spider arm CLOCKING (Rev T4b, 2026-08-31) ───────────────────────────
// Moved 0/120/240 -> 105/225/345 so that ESC2's phase leads can actually reach
// the motor.  This is a routing constraint, and it was found by measurement.
//
// The motor sits at the duct centre; the ONLY solid bridge from the annulus to
// it is a spider arm.  So the phase bundle must cross the bore wall AT an arm
// azimuth and WITHIN the arm's axial band (Z 144-152 for EDF2_SPIDER_Z = 148).
// Measured on the canonical shell, the annulus (skin − 2.5 − duct wall) survives
// aft to:
//
//     azimuth    0   45  105  120  165  225  240  285  345
//     alive to  135  146  163  146  136  146  147  163  136   (mm, at >= 3.5 deep)
//
// At the old 0/120/240 the overlap with the arm band was 0 mm (az 0), 1.5 mm
// (az 120) and 2.5 mm (az 240) — against a 3 x Ø3 mm 16 AWG flat bundle needing
// ~3.5 mm.  The route was effectively closed.
//
// 105 and 285 are the pod's two deep lobes, alive to Z 163 at 6.2-6.4 mm, and
// they are also where the ESC bays land (bay centres measured at azimuth 90 and
// 270).  Clocking an arm to 105 puts the crossing directly beneath bay A with no
// circumferential run at all.  225/345 follow at 120 deg spacing.
//
// ── CORRECTED Rev T4c (2026-09-01) — FOUR arms at 90 deg, not three at 120 ──
// Owner direction.  The Xfly Galaxy X5 motor takes FOUR screws on a square
// pattern (REF-EDF-002: the packing-list photo shows four motor screws plus one
// longer spinner screw — CONFIRMED 2026-09-28 off the physical rotor: M1.5×11
// round-head screw, 1.5 mm Allen (hex) drive, threading axially into the
// motor shaft to retain the rotor — and the hub is a disc with four round
// holes alternating with four slots).  Note for any future rotor mass/CG or
// vibration work: the rotor is factory-balanced by drilling small holes in
// its face (visible in docs/img/20260923_065933.jpg), so its mass is not
// azimuthally uniform — treat it as an as-measured vendor part, not an
// idealized symmetric disc, if it is ever modeled for mass properties.
// Three arms at 120 deg cannot be made to coincide with four
// holes at 90 deg — using three of the four would need them at 90/90/180, which
// 120 deg spacing never provides.  This was PRINT-BLOCKING and is now fixed.
//
// The 90 deg pattern is strictly better for the routing constraint above, which
// is the happy part of the correction: 285 - 105 = 180 = 2 x 90, so a single
// 90 deg set can put an arm on BOTH deep lobes at once.  The old 120 deg set had
// to choose one and give the other a 50 deg circumferential run.  15 and 195
// fall out of the spacing.
//
// MOTOR_BOLT_R = 7.5 mm — MEASURED 2026-09-28 off the physical motor
// (15.0 mm caliper diameter / 2, true square confirmed). See the resolved
// block below for the full measurement note.
// 16 AWG silicone Ø3 mm per docs/TILT_SPAR_ANALYSIS.md.
SPIDER_ARM_ANGLES = [15, 105, 195, 285];

// ── EDF2 spider geometry ────────────────────────────────────────────────────────
// Spider axial centre at nacelle Z = 148.0 mm.
// Sleeve-local Z = 148.0 − 122.5 = 25.5 mm.
SPIDER_Z_L      =  25.5;    // [mm] spider axial centre (sleeve-local)
SPIDER_ARM_H    =   8.0;    // [mm] spider arm axial height (thickness along Z)
SPIDER_ARM_W    =   6.0;    // [mm] spider arm tangential width
N_ARMS          =   len(SPIDER_ARM_ANGLES);  // [count] = 4, at 90° (Rev T4c)

// ── Motor mount — clearance holes into the motor's OWN tapped flange ──────────
// EDF2 motor mounts on spider aft face using 4× M2x12.5mm flat-head screws,
// driven at the bench with the rotor removed (rotor covers these screws).
// In the field this means pulling the whole sleeve out the nacelle's AFT
// end first — see the bench pre-assembly notes above for why this EDF2
// assembly has no in-situ access from the nacelle's own front intake.
// MOTOR_BOLT_R: distance from sleeve axis to M2 screw centre.
//
// HOLE COUNT / PATTERN — RESOLVED (Rev T4c, 2026-09-01, owner direction).
// The 3-arm/120° vs. 4-hole/90° mismatch that used to be documented here as
// PRINT-BLOCKING is fixed: SPIDER_ARM_ANGLES above is already the 4× 90°
// pattern (15/105/195/285) and the motor-insert loop below already cuts one
// pocket per arm. Do not re-open that question; see the Rev T4c note above
// (lines ~147-159) for the REF-EDF-002 evidence.
//
// BOLT-CIRCLE RADIUS — RESOLVED 2026-09-28. The vendor listing publishes
// screw count but not the bolt circle ("nc"); 10.0 mm was inherited from
// Rev R and was only an assumption.
//
// Measured directly off the physical Xfly Galaxy X5 motor with a Vernier
// caliper, owner re-measurement (superseding a first-pass 14.65 mm read):
// 15.0 mm spanning screw-centre to diagonally-opposite screw-centre through
// the shaft boss (bolt-circle DIAMETER, confirmed TRUE SQUARE 4-hole
// pattern — owner-verified, not just visual). MOTOR_BOLT_R = 15.0 / 2 =
// 7.5 mm.
//
// MOUNTING METHOD CORRECTED 2026-09-28 — no heat-set insert at this
// interface. Owner measured the motor's own hardware directly: the motor has
// its own 20 mm dia front flange, 3.5 mm thick, carrying the FOUR TAPPED M2
// holes (bolt circle above) — i.e. the motor supplies its own female thread.
// A second, non-tapped, 1.75 mm flange sits 6.5 mm further back (not a
// mounting feature). 15 mm from the back of the tapped flange to the motor
// body. So the fastener is 4× M2x12.5mm flat-head (countersunk), passing
// THROUGH this sleeve's spider arm (clearance hole, countersunk on the aft/
// nozzle-facing face to seat the flat head flush) and threading directly
// into the motor's own tapped flange — NOT into a heat-set insert in this
// part. The earlier "M2 heat-set insert, countersink in the motor's tab"
// note in this file had both halves backwards: the insert isn't needed at
// all, and the countersink belongs in THIS sleeve, not the motor.
// Stack check: 8 mm arm (clearance, unthreaded) + up to 3.5 mm thread
// engagement in the motor's tapped flange + ~1 mm head recess = 12.5 mm,
// matching the measured screw length — self-consistent.
// M2_CLEAR_D is a standard M2 close-fit clearance-hole diameter (fastener
// engineering convention, not a vendor spec); M2_CSK_D/M2_CSK_DEPTH are
// sized for a generic M2 flat/countersunk head — verify both against the
// actual screw's head diameter once a specific SKU is ordered.
// Square-pattern trueness — RESOLVED 2026-09-28 (owner caliper re-measurement
// confirms true square). Tracked in
// docs/plans/2026-08-26-001-nacelle-esc-intake-integration-plan.md.
MOTOR_BOLT_R    =   7.5;    // [mm] motor bolt circle radius — MEASURED
                            //      2026-09-28 (15.0 mm caliper diameter / 2,
                            //      confirmed true square).
M2_CLEAR_D      =   2.4;    // [mm] M2 close-fit clearance hole (shank passes
                            //      through; threads into motor's tapped
                            //      flange, not into this part).
M2_CSK_D        =   4.0;    // [mm] countersink diameter for M2 flat head —
                            //      generic fastener-catalog estimate, verify
                            //      against the actual screw SKU.
M2_CSK_DEPTH    =   1.2;    // [mm] countersink depth (head recess), same
                            //      caveat as M2_CSK_D.

// ── Hub dimensions ─────────────────────────────────────────────────────────────
// Hub bore provides 1 mm diametric clearance for 3 mm EDF2 motor shaft.
R_HUB           =   8.0;    // [mm] hub outer radius (16 mm OD hub ring)
R_HUB_BORE      =   2.0;    // [mm] hub bore radius  ( 4 mm ID → 1 mm shaft clearance)

// ── Aft retention bores ────────────────────────────────────────────────────────
// 3× axial M3 clearance bores through sleeve aft face (and through key body at
// that radius) at BOSS_R = 28 mm.  Bores align with nacelle
// sleeve_retention_bosses() M3 inserts which open toward Z = SLEEVE_Z_END.
// BOSS_R = 28 mm lies within the key rib (key spans 27.5 … 30.5 mm radially).
BOSS_R          =  28.0;    // [mm] retention bore radial centre (nacelle SLEEVE_BOSS_R)
M3_CLEAR_D      =   3.3;    // [mm] M3 clearance bore diameter
BOSS_BORE_DEPTH =  10.0;    // [mm] axial bore depth inward from aft face

// ── Global facet resolution ─────────────────────────────────────────────────────
$fn = 72;


// =============================================================================
// ── Module: aft_sleeve_body ──────────────────────────────────────────────────
// =============================================================================
// Hollow cylinder: OD = 55 mm, ID = 50 mm, length = 43.75 mm.
// Three longitudinal key ribs protrude radially from OD at 0°/120°/240°.
// Key ribs span the full sleeve length; retention bore cutouts are applied in
// the parent edf_aft_spider_sleeve() module via a wrapping difference().
module aft_sleeve_body() {
    union() {

        // ── Main tube ──────────────────────────────────────────────────────
        difference() {
            cylinder(r = SLEEVE_OD / 2, h = SLEEVE_L, center = false);
            translate([0, 0, -0.01])
                cylinder(r = EDF_BORE_R, h = SLEEVE_L + 0.02, center = false);
        }

        // ── Anti-rotation keys (3× at 120°) ──────────────────────────────
        // Rectangular rib on OD surface, full sleeve length.
        // Angles match edf_stator_sleeve.scad for bore-key-slot continuity.
        // Retention bore cutouts at aft end are applied by parent module.
        for (angle = SLEEVE_KEY_ANGLES) {
            rotate([0, 0, angle])
            // Rev T4 (2026-08-30): the key root is sunk KEY_ROOT_OVERLAP mm
            // BELOW the tube OD so the two solids INTERPENETRATE rather than
            // meet on a coincident cylindrical face.  A touching face is what
            // left the exported STL locally non-manifold (WBS §1.1.3 "MESH FIX
            // 2026-08-25"), which had been patched downstream with a manifold3d
            // re-union of the split bodies; fixing it in the source removes the
            // need for that pass.  Outer edge is unchanged at OD/2 + KEY_H.
            translate([SLEEVE_OD / 2 - KEY_ROOT_OVERLAP, -SLEEVE_KEY_W / 2, 0])
                cube([SLEEVE_KEY_H + KEY_ROOT_OVERLAP, SLEEVE_KEY_W, SLEEVE_L]);
        }

    }
}


// =============================================================================
// ── Module: edf2_spider ─────────────────────────────────────────────────────
// =============================================================================
// EDF2 motor-mount spider: 4-arm radial cross centred at SPIDER_Z_L (Rev T4c).
//
// Arm radial span: (R_HUB − 1) → (EDF_BORE_R + 1) = 7 … 26 mm.
// ±1 mm CGAL volumetric overrun at both ends prevents touching-face
// non-manifold errors where arms meet the hub cylinder and the sleeve
// bore wall.
//
// Motor screw clearance/countersink holes are NOT in this module; they are
// subtracted from the unified geometry in edf_aft_spider_sleeve() to avoid
// nested difference() / union() CGAL conflicts.
module edf2_spider() {
    arm_h  = SPIDER_ARM_H;
    arm_w  = SPIDER_ARM_W;
    z_base = SPIDER_Z_L - arm_h / 2;   // = 21.5 mm

    // ── Spider arms (4× at 90°, Rev T4c) ───────────────────────────────────
    // Arms are plain cuboids (no holes).  Motor screw holes are cut by
    // the parent module after the full union is assembled.
    for (angle = SPIDER_ARM_ANGLES) {
        rotate([0, 0, angle])
            translate([R_HUB - 1, -arm_w / 2, z_base])
                cube([EDF_BORE_R - R_HUB + 2, arm_w, arm_h]);
    }

    // ── Hub ring ───────────────────────────────────────────────────────────
    // OD = 16 mm; bore = 4 mm (1 mm diametric clearance for 3 mm EDF2 shaft).
    translate([0, 0, z_base])
        difference() {
            cylinder(r = R_HUB, h = arm_h, center = false);
            translate([0, 0, -0.01])
                cylinder(r = R_HUB_BORE, h = arm_h + 0.02, center = false);
        }
}


// =============================================================================
// ── Module: edf_aft_spider_sleeve (main assembly) ────────────────────────────
// =============================================================================
// Assembly sequence:
//   1. Union: sleeve tube + keys + spider arms + spider hub.
//   2. Difference: subtract 4× M2 clearance-and-countersink through-holes
//      from the spider arms (Rev T4c — the Galaxy X5 takes four screws at
//      90°, M2 thread, CORRECTED 2026-09-28 to thread into the motor's OWN
//      tapped flange rather than a heat-set insert in this part — see the
//      "Motor mount" header comment above); subtract 3× M3 retention
//      clearance bores through sleeve aft face (still three — those are OUR
//      fasteners into the pod's bosses, not the motor's).
//
// Motor screw through-hole geometry (spans the full spider arm thickness):
//   Centre radius : MOTOR_BOLT_R = 7.5 mm (one bolt per arm, at arm angle).
//   Clearance     : Ø M2_CLEAR_D = 2.4 mm, full SPIDER_ARM_H = 8 mm span
//                   (Z_local 21.5 … 29.5 mm) — no threads cut in this part;
//                   the screw threads into the motor's own tapped flange
//                   beyond the aft face (Z_local = 29.5).
//   Countersink   : Ø M2_CSK_D = 4.0 mm × M2_CSK_DEPTH = 1.2 mm, cut into the
//                   FORWARD face (Z_local = 21.5 mm) so the flat head seats
//                   flush there — driver access is this part's own
//                   forward/intake face at the bench, rotor removed. Because
//                   this sleeve sits buried behind EDF1/the stator sleeve,
//                   there is no in-situ path to it from the nacelle's own
//                   front intake once installed: field service means
//                   extracting the whole sleeve out the nacelle's AFT
//                   (nozzle) end first (owner-confirmed 2026-09-28 — this is
//                   WHY this sleeve has to come out the aft end).
//
// Retention bore geometry (axial, from sleeve aft face through key body):
//   Centre radius : BOSS_R = 28 mm (within key rib, 27.5 … 30.5 mm).
//   Bore          : Ø M3_CLEAR_D = 3.3 mm × BOSS_BORE_DEPTH = 10 mm.
//   Opens at      : Z_local = SLEEVE_L = 43.75 mm (sleeve aft face).
module edf_aft_spider_sleeve() {
    difference() {

        // ── Step 1: full additive union ────────────────────────────────────
        union() {
            aft_sleeve_body();
            edf2_spider();
        }

        // ── Step 2a: M2 motor screw through-holes + countersinks ──────────
        // Clearance hole spans the full arm thickness (no threads here —
        // the screw threads into the motor's tapped flange beyond the aft
        // face). Countersink opens at the forward face (Z_local = 21.5) for
        // the flat head. One hole per arm, co-angular with that arm, at
        // MOTOR_BOLT_R.
        for (angle = SPIDER_ARM_ANGLES) {
            rotate([0, 0, angle]) {
                z_fwd = SPIDER_Z_L - SPIDER_ARM_H / 2;   // = 21.5 mm
                translate([MOTOR_BOLT_R, 0, z_fwd - 0.01])
                    cylinder(r = M2_CLEAR_D / 2,
                             h = SPIDER_ARM_H + 0.02,   // through-hole, both
                                                          // faces open
                             center = false);
                translate([MOTOR_BOLT_R, 0, z_fwd - 0.01])
                    cylinder(r1 = M2_CSK_D / 2,
                             r2 = M2_CLEAR_D / 2,
                             h  = M2_CSK_DEPTH + 0.01,
                             center = false);
            }
        }

        // ── Step 2b: M3 retention clearance bores (sleeve aft face) ───────
        // Axial bore through key rib at BOSS_R = 28 mm.
        // Bore passes through key body (27.5 … 30.5 mm) and sleeve wall
        // inner portion (25 … 27.5 mm), creating clearance for the M3 SHCS
        // retention screw to reach the nacelle boss insert at Z = 166.25 mm.
        for (angle = SLEEVE_KEY_ANGLES) {
            rotate([0, 0, angle])
            translate([BOSS_R, 0, SLEEVE_L - BOSS_BORE_DEPTH])
                cylinder(r = M3_CLEAR_D / 2,
                         h = BOSS_BORE_DEPTH + 0.01,   // +0.01 opens aft face
                         center = false);
        }

    }
}


// =============================================================================
// ── Render call ───────────────────────────────────────────────────────────────
// =============================================================================
edf_aft_spider_sleeve();


// =============================================================================
// ── Print specifications ──────────────────────────────────────────────────────
// =============================================================================
// Material    : CF-PETG (CarbonX PETG+CF or equivalent)
// Layer height: 0.15 mm
// Walls       : 4 perimeter walls (minimum)
// Infill      : 40% gyroid
// Nozzle      : Hardened-steel required for CF-PETG
// Orientation : Forward face (Z=0 end) down; no supports required.
// Quantity    : 2 (one per nacelle — identical for port and starboard).
//
// Hardware required per sleeve
// ----------------------------
//   Motor mount  : 4× M2×12.5 mm flat-head (countersunk) screw — CONFIRMED
//                  2026-09-28 off the physical motor's packed hardware
//                  (bench assembly — motor to spider). NO insert required:
//                  screws thread directly into the motor's OWN tapped
//                  20 mm dia × 3.5 mm flange (owner-measured 2026-09-28).
//                  Countersink for the flat head is cut into THIS sleeve's
//                  forward face (M2_CSK_D/M2_CSK_DEPTH), not the motor.
//   Retention    : 3× M3×20 SHCS (nacelle installation — sleeve to nacelle)
//   Motor bolt c.: MOTOR_BOLT_R = 7.5 mm — MEASURED 2026-09-28 off the
//                  physical Xfly Galaxy X5 motor (15.0 mm caliper diameter
//                  reading / 2, true square confirmed). Screw thread
//                  confirmed M2 by owner off the same physical motor.
//
// Post-print checks
// -----------------
//   1. OD = 55.0 mm ± 0.2 mm at forward, mid, and aft stations.
//      Must slide freely into nacelle enlarged bore (≈ 55.4 mm) with keys engaged.
//   2. Bore ID = 50.0 mm ± 0.2 mm.
//   3. Key dimensions: 3.0 mm wide × 3.0 mm tall ± 0.1 mm; verify fit in
//      nacelle bore key slots (3.3 mm wide × 3.3 mm deep nominal).
//   4. Hub bore = 4.0 mm ± 0.1 mm (EDF2 motor shaft clearance — the motor's
//      shaft is Ø3 mm, published, so this is 1 mm diametric clearance).
//   5. ** BORE ID = 50.0 mm +0.4 / −0.0 AT THE EDF2 ROTOR STATION. **  The build
//      discards the EDF's own shroud and uses this sleeve's bore as the duct, so
//      the rotor now runs against PRINTED plastic.  The vendor keeps 0.4 mm
//      between blade tip and shell (REF-EDF-002), and the shroud ID is 50 mm, so
//      the rotor is ~Ø49.2.  A bore that prints UNDERSIZE rubs the rotor.  Check
//      it at three stations before fitting the fan.
//   6. M2 clearance/countersink holes at r ≈ 7.5 mm: clearance Ø ≈ 2.4 mm
//      full arm thickness, countersink Ø ≈ 4.0 mm × 1.2 mm deep on the
//      forward face. Verify a M2×12.5 flat-head screw seats flush at the
//      countersink and reaches full thread engagement in the motor's tapped
//      flange with the sleeve and motor fully mated.
//   7. Retention bores at r ≈ 28 mm, Ø ≈ 3.3 mm: verify M3×20 SHCS passes
//      freely and aligns with nacelle boss insert (sleeve fully inserted).
//   8. Sleeve forward face must contact stator sleeve aft face with no gap
//      when both sleeves are fully seated in nacelle.
//
// Render command
// --------------
//   openscad -o edf_aft_spider_sleeve.stl edf_aft_spider_sleeve.scad
