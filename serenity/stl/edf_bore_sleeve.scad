// =============================================================================
// edf_bore_sleeve.scad
// Serenity UAV — Rev A — Removable EDF Bore Sleeve (50 mm bore, 55 mm OD)
// =============================================================================
//
// *** DEPRECATED — DO NOT USE ***
// Superseded by the two-sleeve architecture in nacelle_pod_50mm_tandem.scad
// Rev T.  This single-sleeve design integrated both motor-mount spiders and
// the inter-stage stator into one part.  That prevents motor installation and
// removal without disassembling the spider mounts even with the sleeve removed
// from the nacelle.
//
// Replacement parts:
//   edf_stator_sleeve.scad    Rev A — inter-stage stator only (Z 90 … 122.5 mm)
//   edf_aft_spider_sleeve.scad Rev A — EDF2 spider mount    (Z 122.5 … 166.25 mm)
//   EDF1 spider is now integral to nacelle_pod_50mm_tandem.scad Rev T.
// =============================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-05-29
// Revision: Rev A (DEPRECATED)
//
// Description
// -----------
// Field-removable EDF bore sleeve for the Serenity-UAV tandem-EDF nacelle
// (nacelle_pod_50mm_tandem.scad Rev S).  The sleeve is a single printed part
// that slides into the nacelle from the nozzle end and carries all bore-interior
// features: motor-mount spiders for both EDFs and the inter-stage stator.
//
// Why a sleeve?
// -------------
// The 2627-class motor (Xfly Galaxy X5, bell OD = 26 mm, M3 bolt circle
// r ≈ 10 mm) must be bolted to a spider from the spider arm face.  A motor
// installed INSIDE a fixed nacelle bore cannot be bolted from an accessible
// direction because the bolt circle (r ≈ 10 mm) lies entirely inside the
// bore (r ≤ 25 mm), blocked by the stator hub.  Mounting the spider on a
// removable sleeve solves this: both motors are installed on the bench before
// the sleeve is inserted, giving full unrestricted access to every fastener.
//
// Sleeve geometry
// ---------------
//   Main tube  : OD = 55 mm (= EDF_CASING_R × 2), ID = 50 mm,
//                from Z_local = 0 to SLEEVE_MAIN_L = 138.75 mm.
//   Aft flange : OD = 62 mm, ID = 50 mm,
//                from Z_local = SLEEVE_MAIN_L to SLEEVE_L = 151.3 mm.
//   3× M3 clearance bores (Ø3.3 mm) through aft flange at r = 28 mm, 120°.
//
// Retention
// ---------
//   Forward stop (Z_nacelle = 27.5 mm): nacelle bore steps from
//   SLEEVE_BORE_R (27.7 mm) to EDF_BORE_R (25 mm) — sleeve OD 27.5 mm
//   cannot advance past this shoulder.
//
//   Aft stop: sleeve aft flange OD step (55 → 62 mm at Z_local = 138.75 mm)
//   catches on the nozzle ring pocket shoulder in the nacelle
//   (bore steps from SLEEVE_BORE_R to NOZZLE_RING_OD/2 at Z = 166.25 mm).
//
//   Positive aft retention: 3× M3 × 20 mm SHCS from nozzle bore end pass
//   through sleeve aft flange clearance bores and thread into M3 × 6 mm OLF
//   heat-set inserts in nacelle sleeve_retention_bosses() at r = 28 mm.
//   Accessible after iris assembly is removed (required for EDF2 service).
//
// Bore-interior features (sleeve-local Z coordinates)
// ----------------------------------------------------
//   EDF1 motor-mount spider : centre Z_local =  4.0 mm (inserts on intake face)
//   Inter-stage stator hub  :         Z_local = 66.25 … 91.25 mm
//   11 twisted stator fins  :         Z_local = 66.25 … 91.25 mm
//   EDF2 motor-mount spider : centre Z_local = 143.0 mm (inserts on nozzle face)
//
// Motor installation sequence (bench work, before sleeve insertion)
// -----------------------------------------------------------------
//   1. Press 3× M3 × 6 mm OLF inserts into EDF1 spider arm intake faces.
//   2. Press 3× M3 × 6 mm OLF inserts into EDF2 spider arm nozzle faces.
//   3. EDF1: seat motor back plate against sleeve intake face (Z_local = 0).
//      Thread 3× M3 × 10 mm SHCS through motor back plate holes into inserts.
//   4. Fit EDF1 impeller onto motor shaft from aft bore end.
//   5. EDF2: seat motor back plate against EDF2 spider nozzle face
//      (Z_local = 147 mm).  Thread 3× M3 × 10 mm SHCS through back plate.
//   6. Fit EDF2 impeller onto motor shaft from forward bore end.
//   7. Route ESC phase wires through hub bore alongside motor shaft.
//
// Nacelle insertion sequence
// --------------------------
//   1. Fill nacelle cavity (between sleeve bore and nacelle outer shell) with
//      2 lb/cf closed-cell foam BEFORE inserting sleeve (CLAUDE.md standard).
//   2. Slide sleeve aft-end first into nacelle nozzle bore until forward stop.
//   3. Thread 3× M3 × 20 mm SHCS from nozzle bore end through aft flange into
//      nacelle retention boss inserts.  Torque 0.5 N·m.
//   4. Install iris assembly.
//
// Field disassembly sequence
// --------------------------
//   1. Remove iris assembly.
//   2. Back out 3× M3 SHCS from nozzle bore end (2.5 mm hex key, reach ≈ 8 mm).
//   3. Pull sleeve aft out of nacelle.
//   4. To service a motor: back out its 3× M3 SHCS, remove impeller, remove motor.
//
// EDF motor reference
// -------------------
//   Xfly Galaxy X5 50 mm 6S EDF — bare motor + separate impeller
//   Motor OD (bell/can)  : 26 mm
//   Motor shaft diameter  :  3 mm
//   M3 bolt circle radius : ≈ 10 mm (MOTOR_BOLT_R) — VERIFY before printing
//   Fan OD               : ≈ 48–49 mm (fits 50 mm bore)
//
// References
// ----------
//   [1] nacelle_pod_50mm_tandem.scad Rev S — mating nacelle bore geometry.
//   [2] Xfly Galaxy X5 50 mm 6S EDF datasheet (Xfly Model, 2024).
//   [3] OpenSCAD language reference, v2021.01 <https://openscad.org>.
//   [4] Serenity-UAV project CLAUDE.md — fabrication standards (2026).
//
// =============================================================================


// =============================================================================
// ── Parameter Block ───────────────────────────────────────────────────────────
// =============================================================================

// ── EDF bore dimensions (must match nacelle_pod_50mm_tandem.scad) ─────────────
EDF_BORE_R      =  25.0;   // [mm] EDF bore inner radius (50 mm ID)
EDF1_Z_ENTRY    =  27.5;   // [mm] EDF1 forward face, nacelle-local Z
EDF2_Z_EXIT     = 178.8;   // [mm] EDF2 aft face, nacelle-local Z
NOZZLE_RING_Z   = 166.25;  // [mm] nozzle ring pocket start, nacelle-local Z

// ── Sleeve tube dimensions ─────────────────────────────────────────────────────
// SLEEVE_L     = total sleeve length in sleeve-local coordinates (Z=0 at intake end)
// SLEEVE_MAIN_L= main tube length before aft flange step
SLEEVE_OD       =  55.0;   // [mm] main tube OD (= EDF_CASING_R = EDF_BORE_R + 2.5 mm wall)
SLEEVE_WALL     =   2.5;   // [mm] tube wall thickness; (SLEEVE_OD − 50) / 2
SLEEVE_L        = EDF2_Z_EXIT - EDF1_Z_ENTRY;    // = 151.3 mm
SLEEVE_MAIN_L   = NOZZLE_RING_Z - EDF1_Z_ENTRY;  // = 138.75 mm
SLEEVE_FLANGE_OD=  62.0;   // [mm] aft flange OD; must fit in NOZZLE_RING_OD=65 mm
                            //      outer edge: r = 62/2 = 31 mm < 32.5 mm pocket → 1.5 mm gap

// ── Sleeve retention (must match nacelle_pod_50mm_tandem.scad SLEEVE_BOSS_R) ──
// Clearance bores in sleeve aft flange align with nacelle insert boss centres.
SLEEVE_BOSS_R   =  28.0;   // [mm] radial position of retention boss / clearance bore
M3_CLEAR_D      =   3.3;   // [mm] M3 clearance bore diameter (SHCS free fit)

// ── Stator geometry (1.25× nacelle scale; matches nacelle Rev P/Q stator) ──────
// Sleeve-local Z = nacelle Z − EDF1_Z_ENTRY (27.5 mm).
STATOR_Z_BOT_L  =  66.25;  // [mm] stator bottom  (nacelle 93.75 − 27.5)
STATOR_Z_TOP_L  =  91.25;  // [mm] stator top     (nacelle 118.75 − 27.5)
N_FINS          =  11;     // [count] inter-stage stator fins
FIN_THICKNESS   =   2.0;   // [mm] fin tangential thickness at pitch radius
VANE_ANGLE_DEG  =  33.0;   // [deg] fin angle from axial (tuned to 50 mm 6S tip swirl)

// ── Hub dimensions ────────────────────────────────────────────────────────────
// Hub OD and bore sized for shaft clearance + ESC wire routing.
// Motor pass-through is NOT required — motors are bench-mounted before insertion.
S_HUB_R         =   8.0;   // [mm] hub outer radius (16 mm OD)
S_HUB_BORE_R    =   2.0;   // [mm] hub bore inner radius (4 mm ID: 3 mm shaft + 1 mm)

// ── Motor-mount spider dimensions ─────────────────────────────────────────────
// 3-arm (120°) per EDF.  Arm span (S_HUB_R − 1) → (EDF_BORE_R + 1) with ±1 mm
// CGAL volumetric overrun at hub and bore-wall interfaces.
// One M3 × 6 mm OLF heat-set insert per arm (one per motor bolt hole).
//
// MOTOR_BOLT_R = 10.0 mm (20 mm bolt circle diameter) — estimated for Xfly
// Galaxy X5 2627-class with 26 mm bell OD and 3 mm shaft.
// VERIFY against actual motor back plate before printing the first article.
SPIDER_ARM_H    =   8.0;   // [mm] arm axial thickness (= M3_INSERT_L + 2 mm solid back)
SPIDER_ARM_W    =   6.0;   // [mm] arm tangential width
MOTOR_BOLT_R    =  10.0;   // [mm] M3 bolt-circle radius — VERIFY vs motor datasheet
M3_INSERT_D     =   3.5;   // [mm] M3 × 6 mm OLF brass heat-set insert bore OD
M3_INSERT_L     =   6.0;   // [mm] heat-set insert depth

// ── Spider centre positions (sleeve-local Z) ──────────────────────────────────
// EDF1 spider: intake face at Z_local = 0 (sleeve forward end).
//   Motor back plate seats on intake face.  Motor body and fan extend AFT (pusher).
//   M3 SHCS accessible from nacelle intake bore end; reach ≈ 32 mm.
EDF1_SPIDER_Z_L =   4.0;   // [mm]  centre = EDF1_Z_ENTRY + SPIDER_ARM_H/2 − EDF1_Z_ENTRY = 4 mm

// EDF2 spider: nozzle face at Z_local = 147 mm (aft flange zone, 4 mm from end).
//   Motor back plate seats on nozzle face.  Motor body and fan extend FORWARD (puller).
//   M3 SHCS accessible from nozzle bore end (iris removed for EDF2 service).
EDF2_SPIDER_Z_L = 143.0;   // [mm]  centre = EDF2_SPIDER_Z(170.5) − EDF1_Z_ENTRY(27.5) = 143 mm

// ── Swirl direction ───────────────────────────────────────────────────────────
SWIRL_DIR       =  +1;     // [+1 / -1] stator swirl; port CW default
                            //           override at render: -D SWIRL_DIR=-1

// ── Global facet resolution ───────────────────────────────────────────────────
$fn = 72;


// =============================================================================
// ── Module: sleeve_body ──────────────────────────────────────────────────────
// =============================================================================
// Hollow tube with stepped OD:
//   Main section  OD = 55 mm  from Z_local = 0 … SLEEVE_MAIN_L (138.75 mm)
//   Aft flange    OD = 62 mm  from Z_local = SLEEVE_MAIN_L … SLEEVE_L (151.3 mm)
//   Bore          ID = 50 mm  full length (EDF_BORE_R = 25 mm)
//
// The OD step at Z_local = SLEEVE_MAIN_L engages the nacelle nozzle ring pocket
// shoulder, providing the sleeve aft positive stop without any fasteners.
// 3× M3 clearance bores through the aft flange retain the sleeve against
// the nacelle retention bosses.
module sleeve_body() {
    difference() {

        // ── Sleeve tube outer solid ──────────────────────────────────────
        union() {
            // Main tube section (OD = 55 mm)
            cylinder(r = SLEEVE_OD / 2,
                     h = SLEEVE_MAIN_L,
                     center = false);
            // Aft flange (OD = 62 mm, captures nozzle ring pocket shoulder)
            translate([0, 0, SLEEVE_MAIN_L])
                cylinder(r = SLEEVE_FLANGE_OD / 2,
                         h = SLEEVE_L - SLEEVE_MAIN_L,
                         center = false);
        }

        // ── EDF bore (50 mm ID, full length) ────────────────────────────
        translate([0, 0, -0.01])
            cylinder(r = EDF_BORE_R,
                     h = SLEEVE_L + 0.02,
                     center = false);

        // ── M3 clearance bores through aft flange ────────────────────────
        // 3× Ø3.3 mm bores at r = SLEEVE_BOSS_R = 28 mm, 120° spacing.
        // Aligns with nacelle sleeve_retention_bosses() insert centres.
        // M3 × 20 mm SHCS: 12.55 mm through flange + ≥ 6 mm into nacelle boss.
        for (angle = [0, 120, 240]) {
            rotate([0, 0, angle])
            translate([SLEEVE_BOSS_R, 0, SLEEVE_MAIN_L - 0.01])
                cylinder(r = M3_CLEAR_D / 2,
                         h = SLEEVE_L - SLEEVE_MAIN_L + 0.02,
                         center = false);
        }

    }
}


// =============================================================================
// ── Module: sleeve_spider ────────────────────────────────────────────────────
// =============================================================================
// 3-arm (120°) motor-mount spider in sleeve-local coordinates.
//
// Arms: rectangular cross-section, span (S_HUB_R − 1) → (EDF_BORE_R + 1).
// ±1 mm overrun at both ends prevents CGAL touching-face non-manifold errors
// at the hub cylinder and sleeve bore-wall interfaces.
//
// One M3 × 6 mm OLF heat-set insert per arm, bored from the face identified
// by insert_face_dir.  Motor back plate is bolted to this face; motor body and
// impeller extend in the opposite direction.
//
// Parameters
// ----------
// z_local        [mm] : axial spider centre in sleeve-local coordinates
// insert_face_dir      : −1 = intake (low-Z) face;  +1 = nozzle (high-Z) face
module sleeve_spider(z_local, insert_face_dir) {
    arm_h = SPIDER_ARM_H;
    arm_w = SPIDER_ARM_W;

    // Axial position of the fastener-access (insert-bearing) face.
    insert_face_z = (insert_face_dir < 0)
                    ? z_local - arm_h / 2   // intake (low-Z) face
                    : z_local + arm_h / 2;  // nozzle (high-Z) face

    // ── 3 arms at 120°, each with one M3 insert bore ─────────────────────
    for (angle = [0, 120, 240]) {
        rotate([0, 0, angle])
        difference() {
            // Arm solid block, ±1 mm overrun for CGAL volumetric overlap.
            translate([S_HUB_R - 1, -arm_w / 2, z_local - arm_h / 2])
                cube([EDF_BORE_R - S_HUB_R + 2, arm_w, arm_h]);

            // M3 heat-set insert bore — M3_INSERT_L deep from insert face.
            if (insert_face_dir < 0) {
                // Intake face: bore opens at insert_face_z, runs aft (+Z).
                translate([MOTOR_BOLT_R, 0, insert_face_z])
                    cylinder(r = M3_INSERT_D / 2,
                             h = M3_INSERT_L + 0.01,
                             center = false);
            } else {
                // Nozzle face: bore opens at insert_face_z, runs forward (−Z).
                translate([MOTOR_BOLT_R, 0, insert_face_z - M3_INSERT_L - 0.01])
                    cylinder(r = M3_INSERT_D / 2,
                             h = M3_INSERT_L + 0.01,
                             center = false);
            }
        }
    }

    // ── Central hub ring ─────────────────────────────────────────────────
    // OD = 2 × S_HUB_R (16 mm); bore = 2 × S_HUB_BORE_R (4 mm).
    // Motor shaft (3 mm dia) passes through bore; ESC phase wires share bore.
    translate([0, 0, z_local - arm_h / 2])
        difference() {
            cylinder(r = S_HUB_R,
                     h = arm_h,
                     center = false);
            translate([0, 0, -0.01])
                cylinder(r = S_HUB_BORE_R,
                         h = arm_h + 0.02,
                         center = false);
        }
}


// =============================================================================
// ── Module: sleeve_hub ───────────────────────────────────────────────────────
// =============================================================================
// Stator hub ring spanning the inter-stage stator zone.
// OD = 2 × S_HUB_R (16 mm); bore = 2 × S_HUB_BORE_R (4 mm).
// Routes ESC wires between EDF zones through the centre of the fin stack.
module sleeve_hub() {
    translate([0, 0, STATOR_Z_BOT_L])
        difference() {
            cylinder(r = S_HUB_R,
                     h = STATOR_Z_TOP_L - STATOR_Z_BOT_L,
                     center = false);
            translate([0, 0, -0.01])
                cylinder(r = S_HUB_BORE_R,
                         h = (STATOR_Z_TOP_L - STATOR_Z_BOT_L) + 0.02,
                         center = false);
        }
}


// =============================================================================
// ── Module: sleeve_fin ───────────────────────────────────────────────────────
// =============================================================================
// One twisted inter-stage stator fin.
// Radial span (S_HUB_R − 1) → (EDF_BORE_R + 1); ±1 mm CGAL overrun at hub
// and bore-wall interfaces (bore wall = inner surface of sleeve_body() tube).
module sleeve_fin(phi_center, swirl_dir) {
    fin_h     = STATOR_Z_TOP_L - STATOR_Z_BOT_L;
    twist_deg = swirl_dir * VANE_ANGLE_DEG * 2;

    rotate([0, 0, phi_center])
        translate([0, 0, STATOR_Z_BOT_L])
            linear_extrude(
                height = fin_h,
                twist  = twist_deg,
                slices = 16,
                center = false
            )
                translate([S_HUB_R - 1, -FIN_THICKNESS / 2, 0])
                    square([EDF_BORE_R - S_HUB_R + 2, FIN_THICKNESS]);
}


// =============================================================================
// ── Module: edf_bore_sleeve (main assembly) ──────────────────────────────────
// =============================================================================
// Top-level assembly.  All bore-interior geometry is union'd into the sleeve
// after sleeve_body() closes its difference(), so the bore subtraction does not
// remove the spiders, hub, or fins.
//
// Both spiders and fin arms span to EDF_BORE_R + 1 = 26 mm, overlapping 1 mm
// into the sleeve tube wall (inner radius = EDF_BORE_R = 25 mm) for CGAL
// volumetric contact — no touching-face non-manifold issues.
module edf_bore_sleeve(swirl_dir = SWIRL_DIR) {
    union() {

        // ── Sleeve tube + aft flange + retention clearance bores ──────────
        sleeve_body();

        // ── EDF1 motor-mount spider (intake face at Z_local = 0) ─────────
        // Insert face (low-Z) is flush with sleeve forward end.
        // 3× M3 SHCS enter from nacelle intake bore; reach ≈ 32 mm.
        sleeve_spider(EDF1_SPIDER_Z_L, -1);

        // ── Inter-stage stator hub (ESC wire routing conduit) ─────────────
        sleeve_hub();

        // ── 11 twisted inter-stage stator fins ───────────────────────────
        for (i = [0 : N_FINS - 1]) {
            sleeve_fin(i * (360 / N_FINS), swirl_dir);
        }

        // ── EDF2 motor-mount spider (nozzle face at Z_local = 147 mm) ────
        // Insert face (high-Z) is 4 mm from sleeve aft end.
        // 3× M3 SHCS enter from nozzle bore end after iris is removed.
        sleeve_spider(EDF2_SPIDER_Z_L, +1);

    }
}


// =============================================================================
// ── Render call ───────────────────────────────────────────────────────────────
// =============================================================================
edf_bore_sleeve(swirl_dir = SWIRL_DIR);


// =============================================================================
// ── Print specifications ──────────────────────────────────────────────────────
// =============================================================================
// Material    : CF-PETG (CarbonX PETG+CF or equivalent)
// Layer height: 0.15 mm
// Walls       : 4 perimeter walls (minimum)
// Infill      : 40% gyroid (all regions — spider arms are load-bearing)
// Nozzle      : Hardened-steel required for CF-PETG
// Orientation : Intake face (EDF1_SPIDER_Z_L = 0) down; no supports required.
// Quantity    : 1 per nacelle (2 per UAV).  Port and starboard sleeves differ
//               only in SWIRL_DIR; re-render with -D SWIRL_DIR=-1 for stbd.
//
// Post-print checks
// -----------------
//   1. Sleeve OD = 55.0 mm ± 0.2 mm at main tube, measured 3 axial stations.
//      Must slide freely into nacelle enlarged bore (55.4 mm ID).
//   2. Bore ID  = 50.0 mm ± 0.2 mm; verify impeller tip clearance ≥ 0.5 mm
//      by temporarily fitting motor + impeller before sleeve installation.
//   3. Hub bore ID = 4.0 mm ± 0.1 mm (motor shaft 3 mm + 0.5 mm clearance).
//   4. M3 insert bores = 3.5 mm ± 0.05 mm — press-fit for OLF brass insert.
//      Use 2.0 mm drill if bore is under 3.5 mm; reprint if over 3.6 mm.
//   5. M3 clearance bores in aft flange = 3.3 mm ± 0.15 mm (M3 SHCS free fit).
//   6. Stator fin edges: lightly sand if layer bridging creates rough surface.
//   7. Aft flange step (55 → 62 mm OD) must seat flush against nacelle nozzle
//      ring pocket shoulder; verify no gap before installing retention screws.
//
// Render commands
// ---------------
//   Port nacelle sleeve (CW stator from intake, SWIRL_DIR = +1):
//     openscad -o edf_bore_sleeve_port.stl edf_bore_sleeve.scad -D SWIRL_DIR=1
//   Starboard nacelle sleeve (CCW stator, SWIRL_DIR = −1):
//     openscad -o edf_bore_sleeve_stbd.stl edf_bore_sleeve.scad -D SWIRL_DIR=-1
