// =============================================================================
// edf_aft_spider_sleeve.scad
// Serenity UAV — Rev A — EDF Aft Spider Sleeve
// =============================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-05-29
// Revision: Rev A
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
//   1. Press 3× M3 heat-set inserts (OLF M3×6) into spider arm aft-face
//      pockets at MOTOR_BOLT_R = 10 mm radius, accessible from nozzle end.
//   2. Seat EDF2 motor forward face against spider arm aft face
//      (motor shaft extends forward through hub bore, R_HUB_BORE = 2 mm).
//   3. Drive 3× M3×10 SHCS from nozzle end through motor mounting holes
//      into the three heat-set inserts.  Motor body protrudes aft past
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

// ── EDF2 spider geometry ────────────────────────────────────────────────────────
// Spider axial centre at nacelle Z = 148.0 mm.
// Sleeve-local Z = 148.0 − 122.5 = 25.5 mm.
SPIDER_Z_L      =  25.5;    // [mm] spider axial centre (sleeve-local)
SPIDER_ARM_H    =   8.0;    // [mm] spider arm axial height (thickness along Z)
SPIDER_ARM_W    =   6.0;    // [mm] spider arm tangential width
N_ARMS          =   3;      // [count] spider arms at 0°/120°/240°

// ── Motor mount — M3 heat-set inserts in spider arm aft faces ─────────────────
// EDF2 motor mounts on spider aft face using 3× M3×10 SHCS (nozzle-end access).
// MOTOR_BOLT_R: distance from sleeve axis to M3 screw centre.
// *** VERIFY against actual Xfly Galaxy X5 2627 motor bolt circle before print ***
MOTOR_BOLT_R    =  10.0;    // [mm] motor M3 bolt circle radius (UNVERIFIED — check motor)
M3_INSERT_D     =   3.5;    // [mm] M3 OLF heat-set insert outer diameter
M3_INSERT_L     =   6.0;    // [mm] M3 OLF heat-set insert length (pocket depth)

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
        for (angle = [0, 120, 240]) {
            rotate([0, 0, angle])
            translate([SLEEVE_OD / 2, -SLEEVE_KEY_W / 2, 0])
                cube([SLEEVE_KEY_H, SLEEVE_KEY_W, SLEEVE_L]);
        }

    }
}


// =============================================================================
// ── Module: edf2_spider ─────────────────────────────────────────────────────
// =============================================================================
// EDF2 motor-mount spider: 3-arm radial cross centred at SPIDER_Z_L.
//
// Arm radial span: (R_HUB − 1) → (EDF_BORE_R + 1) = 7 … 26 mm.
// ±1 mm CGAL volumetric overrun at both ends prevents touching-face
// non-manifold errors where arms meet the hub cylinder and the sleeve
// bore wall.
//
// Motor bolt M3 insert pockets are NOT in this module; they are subtracted
// from the unified geometry in edf_aft_spider_sleeve() to avoid nested
// difference() / union() CGAL conflicts.
module edf2_spider() {
    arm_h  = SPIDER_ARM_H;
    arm_w  = SPIDER_ARM_W;
    z_base = SPIDER_Z_L - arm_h / 2;   // = 21.5 mm

    // ── Spider arms (3× at 120°) ───────────────────────────────────────────
    // Arms are plain cuboids (no pockets).  Motor insert pockets are cut by
    // the parent module after the full union is assembled.
    for (angle = [0, 120, 240]) {
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
//   2. Difference: subtract 3× M3 motor insert pockets from spider arm aft
//      faces; subtract 3× M3 retention clearance bores through sleeve aft face.
//
// Motor insert pocket geometry (blind, from spider aft face):
//   Centre radius : MOTOR_BOLT_R = 10 mm (one bolt per arm, at arm angle).
//   Pocket        : Ø M3_INSERT_D = 3.5 mm × M3_INSERT_L = 6 mm deep.
//   Opens at      : Z_local = SPIDER_Z_L + SPIDER_ARM_H/2 = 29.5 mm (aft face).
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

        // ── Step 2a: M3 motor insert pockets (spider arm aft faces) ───────
        // Blind pocket opens at Z_local = 29.5 mm (spider aft face).
        // One pocket per arm, co-angular with that arm, at MOTOR_BOLT_R.
        for (angle = [0, 120, 240]) {
            rotate([0, 0, angle])
            translate([MOTOR_BOLT_R, 0,
                       SPIDER_Z_L + SPIDER_ARM_H / 2 - M3_INSERT_L])
                cylinder(r = M3_INSERT_D / 2,
                         h = M3_INSERT_L + 0.01,   // +0.01 opens aft face
                         center = false);
        }

        // ── Step 2b: M3 retention clearance bores (sleeve aft face) ───────
        // Axial bore through key rib at BOSS_R = 28 mm.
        // Bore passes through key body (27.5 … 30.5 mm) and sleeve wall
        // inner portion (25 … 27.5 mm), creating clearance for the M3 SHCS
        // retention screw to reach the nacelle boss insert at Z = 166.25 mm.
        for (angle = [0, 120, 240]) {
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
//   Motor mount  : 3× M3 OLF heat-set insert (3.5 mm OD × 6 mm)
//                  3× M3×10 SHCS (bench assembly — motor to spider)
//   Retention    : 3× M3×20 SHCS (nacelle installation — sleeve to nacelle)
//   Motor bolt c.: VERIFY MOTOR_BOLT_R = 10 mm against actual Xfly Galaxy X5
//                  2627 motor before printing (measure bolt circle on physical
//                  motor or obtain datasheet).
//
// Post-print checks
// -----------------
//   1. OD = 55.0 mm ± 0.2 mm at forward, mid, and aft stations.
//      Must slide freely into nacelle enlarged bore (≈ 55.4 mm) with keys engaged.
//   2. Bore ID = 50.0 mm ± 0.2 mm.
//   3. Key dimensions: 3.0 mm wide × 3.0 mm tall ± 0.1 mm; verify fit in
//      nacelle bore key slots (3.3 mm wide × 3.3 mm deep nominal).
//   4. Hub bore = 4.0 mm ± 0.1 mm (EDF2 motor shaft clearance).
//   5. M3 insert pockets at r ≈ 10 mm, Ø ≈ 3.5 mm: verify insert presses
//      flush to arm aft face.  Pocket must be ≥ 6 mm deep.
//   6. Retention bores at r ≈ 28 mm, Ø ≈ 3.3 mm: verify M3×20 SHCS passes
//      freely and aligns with nacelle boss insert (sleeve fully inserted).
//   7. Sleeve forward face must contact stator sleeve aft face with no gap
//      when both sleeves are fully seated in nacelle.
//
// Render command
// --------------
//   openscad -o edf_aft_spider_sleeve.stl edf_aft_spider_sleeve.scad
