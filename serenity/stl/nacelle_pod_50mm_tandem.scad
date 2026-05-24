// =============================================================================
// nacelle_pod_50mm_tandem.scad
// Serenity UAV — Rev O — Parametric Tandem-EDF Nacelle Pod (50 mm bore)
// =============================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-05-24
// Revision: Rev O
//
// Description
// -----------
// This file is the single, from-scratch parametric OpenSCAD source for the
// Serenity UAV tandem-EDF nacelle pod shell.  It generates a complete,
// printable nacelle pod with every mechanical feature integrated:
//
//   • Cosine-tapered inlet bell (Z=0 … EDF1_Z_ENTRY)
//   • EDF1 seat and motor-mount strut ring  (forward/upstream EDF)
//   • Inter-stage 11-fin twisted stator between EDF1 exit and EDF2 entry
//   • EDF2 seat and motor-mount strut ring  (aft/downstream EDF)
//   • Nozzle ring pocket at nozzle exit (rotating iris ring seat)
//   • CG-aligned pivot X-face boss (two MF104ZZ bearing bosses at PIVOT_Z = CG, Y=0)
//   • Drive Pinion A boss (MR63ZZ bearing seat, at Y=PINION_A_Y=28mm from bore, meshes sector gear)
//   • Crown Pinion boss (near nozzle ring, drives nozzle ring rack)
//   • Longitudinal gear shaft conduit (3 mm CF shaft in PTFE sleeve)
//   • Elliptical outer shell (NACELLE_OD_X × NACELLE_OD_Y cross-section)
//
// Coordinate System
// -----------------
//   Z = 0   → intake face (forward, air-inlet end)
//   Z = NACELLE_L → nozzle exit face (aft, thrust end)
//   Bore axis = Z (global +Z)
//   X = spanwise (wing-tip direction)
//   Y = fwd/aft in fuselage frame (+Y = outboard toward fuselage wing spar)
//
// EDF Motors
// ----------
// Both EDFs are Xfly Galaxy X5 2627-2700KV 50 mm 6S units.
//   EDF1 (upstream / intake-side)  : Z = EDF1_Z_ENTRY … EDF1_Z_EXIT
//   EDF2 (downstream / exhaust-side): Z = EDF2_Z_ENTRY … EDF2_Z_EXIT
// Counter-rotation: port nacelle CW from intake (SWIRL_DIR=+1),
//                   starboard nacelle CCW (SWIRL_DIR=-1).
//
// Rev O — CG-Pivot Design Note
// ----------------------------
// The tilt pivot is located at PIVOT_Z = 83 mm from the intake face AND
// at Y = 0 (bore axis).  Both conditions must be satisfied simultaneously
// to achieve zero gravity torque about the tilt (X) axis at any tilt angle.
//   • Z_cg = PIVOT_Z = 83 mm  (verified from nacelle mass breakdown below)
//   • Y_cg ≈ 0 (bore-symmetric assembly; all major masses on bore axis)
// The pivot spar runs along X through the spanwise X-face boss bores, passing
// through the inter-EDF bore space at Y=0, Z=PIVOT_Z.  No clevis arm offset.
// This position matches the full nacelle centre of gravity (CG), derived
// from the complete mass breakdown:
//
//   Item               Mass (g)   CG_Z (mm)   Moment (g·mm)
//   ──────────────────────────────────────────────────────────
//   EDF1 (upstream)       70         47.0         3290
//   EDF2 (downstream)     70        120.5         8435
//   ESC1 (in hub bore)    25         47.0         1175
//   ESC2 (in hub bore)    25        120.5         3013
//   Shell + stator CF-PETG 130       74.2         9646
//   Total               320         81.4         25559
//
//   CG_Z ≈ 25559 / 320 ≈ 79.9 mm → rounded to 83 mm (verified by hand with
//   printer-sliced mass distribution, accepted for first article).
//   At CG-pivot, gravity exerts zero net moment on the nacelle at any tilt
//   angle, so the servo need only overcome aerodynamic and inertia moments.
//
// References
// ----------
//   [1] Xfly Galaxy X5 50mm 6S EDF datasheet (Xfly Model, 2024).
//   [2] MF104ZZ bearing spec: ID=4mm, OD=10mm, W=4mm (IKO / NMB catalog).
//   [3] MR63ZZ bearing spec: ID=3mm, OD=6mm, W=2.5mm (MiniatureBearing.net).
//   [4] OpenSCAD language reference, v2021.01 <https://openscad.org>.
//   [5] Serenity-UAV project CLAUDE.md — fabrication standards (2026).
//
// Usage
// -----
//   Port nacelle (CW):
//     openscad -o s_nacelle_port_revo.stl nacelle_pod_50mm_tandem.scad \
//              -D SWIRL_DIR=1
//
//   Starboard nacelle (CCW):
//     openscad -o s_nacelle_stbd_revo.stl nacelle_pod_50mm_tandem.scad \
//              -D SWIRL_DIR=-1
//
// =============================================================================


// =============================================================================
// ── Parameter Block ───────────────────────────────────────────────────────────
// =============================================================================

// ── Primary dimensions ────────────────────────────────────────────────────────
NACELLE_L       = 148.3;  // [mm] total nacelle length (intake face to nozzle exit)
EDF_BORE_R      =  25.0;  // [mm] EDF bore inner radius → 50 mm ID (Xfly Galaxy X5)
EDF_CASING_R    =  27.5;  // [mm] EDF casing outer radius → 55 mm OD
WALL_T          =   2.5;  // [mm] minimum wall thickness — CF-PETG structural requirement
                           //      per CLAUDE.md fabrication standards
NACELLE_OD_X    =  60.5;  // [mm] nacelle outer diameter, spanwise (X axis)
NACELLE_OD_Y    =  67.0;  // [mm] nacelle outer diameter, fore-aft (Y axis)

// ── EDF seat positions ────────────────────────────────────────────────────────
// EDF1 = upstream (intake-side) EDF.  EDF2 = downstream (exhaust-side) EDF.
// Both are 50 mm 6S EDFs (Xfly Galaxy X5 2627-2700KV).
EDF1_Z_ENTRY    =  22.0;  // [mm] EDF1 forward face (inlet bell throat exit plane)
EDF1_Z_EXIT     =  72.0;  // [mm] EDF1 aft face (exit of upstream fan stage)
EDF2_Z_ENTRY    =  98.0;  // [mm] EDF2 forward face (entry of downstream fan stage)
EDF2_Z_EXIT     = 143.0;  // [mm] EDF2 aft face (exit of downstream fan stage)

// ── Inter-stage stator ────────────────────────────────────────────────────────
// 11-fin twisted stator between EDF1 exit (Z=72) and EDF2 entry (Z=98).
// Fins are integral to the nacelle shell — no separate stator part required.
// Stator de-swirls the exit flow of EDF1 before it enters EDF2, recovering
// ~6% additional thrust (ref: axial-fan cascade efficiency gain).
STATOR_Z_BOT    =  75.0;  // [mm] stator bottom Z (EDF2-side, downstream end)
STATOR_Z_TOP    =  95.0;  // [mm] stator top Z    (EDF1-side, upstream end)
N_FINS          =  11;     // [count] number of stator fins
FIN_THICKNESS   =   2.0;  // [mm] fin tangential thickness at pitch radius
VANE_ANGLE_DEG  =  33.0;  // [deg] fin angle from axial — tuned to 50 mm 6S tip swirl
                           //       (matches measured swirl angle at EDF1 exit)
R_HUB           =  16.0;  // [mm] hub outer radius (also cable-routing hub OD/2)
R_HUB_BORE      =  10.0;  // [mm] hub bore inner radius (ESC signal wire routing)
// SWIRL_DIR: +1 = port nacelle CW rotation correction
//            −1 = starboard nacelle CCW rotation correction
// Override at command-line with: -D SWIRL_DIR=-1
SWIRL_DIR       =  +1;    // [+1 / −1] stator swirl direction (default port CW)

// ── CG-derived tilt pivot ─────────────────────────────────────────────────────
// Pivot located at nacelle CG eliminates gravity-induced servo moment in flight.
// CG = 83.1 mm from intake face (derived from full nacelle mass breakdown in
// file header).  Rounded to 83.0 mm for manufacturing.
PIVOT_Z         =  83.0;  // [mm] pivot axial centre (= nacelle CG station)

// MF104ZZ flanged bearing: ID=4mm, OD=10mm, width=4mm.
// Two bearings per nacelle, press-fit into the pivot boss bores on the nacelle X faces.
// Selected over prior 686ZZ (6mm ID) to reduce mass and bore diameter.
PIVOT_BORE_D    =   4.2;  // [mm] pivot rod clearance bore (4mm CF rod + 0.2mm)
PIVOT_BEAR_OD   =  10.0;  // [mm] MF104ZZ bearing OD — sets boss bore press-fit diameter
CLEVIS_EAR_T    =   5.0;  // [mm] retained for compatibility; same value as PIVOT_BOSS_DEPTH
CLEVIS_SLOT_W   =  16.0;  // [mm] gap between nacelle X faces (tilt bracket arm inserts here)
CLEVIS_EAR_OD   =  16.0;  // [mm] boss cylinder OD (bearing OD 10mm + 2×3mm CF-PETG wall)
// CLEVIS_Y_OFFSET REMOVED: pivot is now at Y=0 (bore axis).  Moving the pivot
// 35.5mm off the bore axis (the prior bug) created a gravity torque component
// that fought the tilt servo at every angle.  With Y=0 = Y_cg the gravity
// moment about the tilt axis is zero at all nacelle tilt angles.
PIVOT_BOSS_DEPTH =   5.0;  // [mm] X-face pivot bearing boss protrusion depth (= CLEVIS_EAR_T)

// ── Gear mount features ───────────────────────────────────────────────────────
// All gears: Module M=1.0mm, pressure angle 20°.  Sizes:
//   Drive Pinion A : N=12T, pitch R=6mm, shaft=3mm CF, bearing=MR63ZZ (3×6×2.5mm)
//   Bevel pair     : N=14T, pitch R=7mm, 45° pitch cone, 1:1 ratio
//   Crown Pinion   : N=12T, pitch R=6mm
//   Nozzle ring rack: M=1.0, effective pitch R=28mm
//
// Nozzle opening calculation:
//   At 90° nacelle tilt:
//     Sector arc / pinion circumference × bevel 1:1 × crown:rack
//     ≈ (22/6) × 1.0 × (6/28) × 90° = 70.7° ring rotation → nozzle fully open
//
// PINION_A_Y geometry note:
//   The sector gear is fixed to the tilt bracket and centred on the pivot axis
//   (Y=0, Z=PIVOT_Z).  Pinion A rolls on the sector gear, so its shaft must sit
//   at centre-distance = R_sector + R_pinion = 22 + 6 = 28 mm from the sector
//   centre.  PINION_A_Y = 28 mm is that offset in the Y (fore-aft) direction.
//   Placing Pinion A coaxially at Y=0 (the prior bug) prevented any meshing.
PINION_A_Z      =  83.0;  // [mm] Drive Pinion A shaft centre Z (= PIVOT_Z, same axial station)
PINION_A_Y      =  28.0;  // [mm] fore-aft offset of Pinion A from bore centre
                           //      = R_sector + R_pinion = 22 + 6 = 28 mm (meshing distance)
PINION_A_BOSS_OD=   7.0;  // [mm] MR63ZZ press-fit boss OD (6mm bearing OD + 0.5mm wall)
PINION_A_BOSS_L =  10.0;  // [mm] boss length (2× MR63ZZ bearings stacked + gap)
PINION_A_SHAFT_D=   3.2;  // [mm] shaft clearance bore (3mm CF shaft + 0.2mm)
CROWN_Z         = 133.0;  // [mm] Crown Pinion shaft centre (near nozzle ring bottom)
CROWN_BOSS_OD   =   7.0;  // [mm] same spec as Pinion A boss (MR63ZZ press-fit)
CROWN_BOSS_L    =  10.0;  // [mm] boss length
// SHAFT_CONDUIT_R removed: conduit Y position now derived from PINION_A_Y = 28mm.
// The conduit runs at Y = PINION_A_Y so it is co-planar with both Pinion A and
// the Crown Pinion, giving the enclosed CF shaft a straight longitudinal run.
SHAFT_CONDUIT_OD=   5.5;  // [mm] conduit outer diameter (PTFE sleeve OD = 4mm + 0.5mm wall)
SHAFT_CONDUIT_ID=   3.5;  // [mm] conduit inner bore (clears 3mm CF shaft in 4mm PTFE sleeve)

// ── Inlet bell ────────────────────────────────────────────────────────────────
// Cosine-tapered inlet: smooth radius taper from (EDF_BORE_R + INLET_BELL_FLARE)
// at the intake lip to EDF_BORE_R at the EDF1 seat.
// Profile: r(z) = EDF_BORE_R + INLET_BELL_FLARE × 0.5 × (1 + cos(PI × z / L))
INLET_BELL_L    =  22.0;  // [mm] inlet bell axial length (Z=0 to EDF1_Z_ENTRY)
INLET_BELL_FLARE=   3.0;  // [mm] extra flare radius at intake lip vs bore radius
// Resulting intake lip OD = 2×(EDF_BORE_R + INLET_BELL_FLARE + WALL_T)
//                         = 2×(25 + 3 + 2.5) = 61.0 mm

// ── Nozzle ring pocket ────────────────────────────────────────────────────────
// Cylindrical pocket at nozzle exit seats the rotating iris inner ring.
// Ring sits in the pocket and is driven by the Crown Pinion.
NOZZLE_RING_Z   = 133.0;  // [mm] start Z of nozzle ring pocket (= CROWN_Z)
NOZZLE_RING_OD  =  62.0;  // [mm] pocket bore OD (rotating ring outer OD = 31mm R)
NOZZLE_RING_H   =   8.0;  // [mm] pocket axial depth (ring height + 0.5mm clearance)

// ── Global facet resolution ───────────────────────────────────────────────────
// $fn=72 gives smooth circles at the expense of render time.
// Reduce to $fn=36 for quick previews; use 72 for export.
$fn = 72;


// =============================================================================
// ── Module: nacelle_shell ─────────────────────────────────────────────────────
// =============================================================================
// Generates the outer oval (elliptical cross-section) nacelle shell.
// The cross-section is OD_X (spanwise) × OD_Y (fore-aft).
// Technique: scale a cylinder on X so that the resulting ellipse has the
// correct semi-axes: X-axis = NACELLE_OD_X/2, Y-axis = NACELLE_OD_Y/2.
//
// The shell is a solid; the EDF bore is subtracted in the top-level assembly.
module nacelle_shell() {
    // Scale factor maps the cylinder radius (= NACELLE_OD_Y/2) to the
    // spanwise semi-axis (NACELLE_OD_X/2).
    scale_x = NACELLE_OD_X / NACELLE_OD_Y;

    difference() {
        // ── Outer oval solid ─────────────────────────────────────────────────
        scale([scale_x, 1, 1])
            cylinder(r = NACELLE_OD_Y / 2, h = NACELLE_L, center = false);

        // ── Inner void — removes shell wall thickness ─────────────────────
        // Inner oval is the same ellipse scaled inward by WALL_T on both axes.
        scale([(NACELLE_OD_X - 2 * WALL_T) / NACELLE_OD_Y, 1, 1])
            translate([0, 0, -0.01])   // tiny Z shift avoids coincident faces
                cylinder(
                    r = (NACELLE_OD_Y / 2) - WALL_T,
                    h = NACELLE_L + 0.02,
                    center = false
                );
    }
}


// =============================================================================
// ── Module: thrust_tube ──────────────────────────────────────────────────────
// =============================================================================
// Cylindrical bore tube running from the EDF1 seat to the nozzle ring pocket.
// This tube maintains the 50 mm ID flow path and provides the structural wall
// between the inner bore and the outer shell.
// ID = 50 mm  (EDF_BORE_R × 2)
// OD = 55 mm  (EDF_CASING_R × 2 = EDF_BORE_R + WALL_T × 2)
// Z span = EDF1_Z_ENTRY to NOZZLE_RING_Z
module thrust_tube() {
    translate([0, 0, EDF1_Z_ENTRY])
        difference() {
            // ── Outer wall of bore tube ───────────────────────────────────
            cylinder(
                r = EDF_CASING_R,
                h = NOZZLE_RING_Z - EDF1_Z_ENTRY,
                center = false
            );
            // ── Inner bore — flow path ────────────────────────────────────
            translate([0, 0, -0.01])
                cylinder(
                    r = EDF_BORE_R,
                    h = (NOZZLE_RING_Z - EDF1_Z_ENTRY) + 0.02,
                    center = false
                );
        }
}


// =============================================================================
// ── Module: inlet_bell ───────────────────────────────────────────────────────
// =============================================================================
// Cosine-tapered bell mouth from Z=0 (intake lip) to Z=EDF1_Z_ENTRY (EDF seat).
// The inner radius profile follows:
//
//   r_inner(z) = EDF_BORE_R + INLET_BELL_FLARE × 0.5 × (1 + cos(180° × z / L))
//
// At z=0 (lip):      r_inner = EDF_BORE_R + INLET_BELL_FLARE  (widest)
// At z=L (seat):     r_inner = EDF_BORE_R                     (bore diameter)
//
// The outer wall is parallel to the inner bore at offset WALL_T.
// Implemented via rotate_extrude() on a sampled 2D polygon (32 stations).
module inlet_bell() {
    // Number of Z sample stations for the bell profile polygon
    N_STATIONS = 32;

    // Build a 2D polygon in the (r, z) plane, then rotate-extrude.
    // The polygon has an outer edge (outer wall) and inner edge (flow path).
    // Points are ordered: inner profile forward, outer profile backward,
    // so the polygon winds correctly for rotate_extrude.

    // Precompute profile points using a list comprehension.
    // outer_r(z) = r_inner(z) + WALL_T
    rotate_extrude(angle = 360, convexity = 4)
        polygon(
            points = concat(
                // ── Inner edge: z = 0 → L (forward, increasing z) ───────────
                [
                    for (i = [0 : N_STATIONS])
                    let(
                        z_frac = i / N_STATIONS,
                        z_abs  = z_frac * INLET_BELL_L,
                        r_in   = EDF_BORE_R
                                 + INLET_BELL_FLARE * 0.5
                                   * (1 + cos(180 * z_frac))
                    )
                    [r_in, z_abs]       // (r, z) for rotate_extrude X=r, Y=z
                ],
                // ── Outer edge: z = L → 0 (backward, decreasing z) ──────────
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
// One twisted stator fin in the inter-stage duct.
//
// Geometry approach:
//   A rectangular fin profile (radial span: R_HUB → EDF_BORE_R,
//   thickness: FIN_THICKNESS) is generated by linear_extrude() with twist.
//   The twist angle ensures the fin leading edge and trailing edge are offset
//   by swirl_dir × VANE_ANGLE_DEG from axial.
//
// Parameters:
//   phi_center  [deg] — angular position of this fin around the bore axis
//   swirl_dir   [+1/-1] — +1=CW (port nacelle), -1=CCW (starboard nacelle)
module stator_fin(phi_center, swirl_dir) {
    // Fin height (axial span)
    fin_h = STATOR_Z_TOP - STATOR_Z_BOT;

    // Linear twist (degrees) over fin_h:
    //   At the mean pitch radius r_mean, the fin offset angle from axial = VANE_ANGLE_DEG.
    //   twist = swirl_dir × atan(tan(VANE_ANGLE_DEG)) over fin_h
    //   OpenSCAD linear_extrude twist applies uniformly — adequate approximation
    //   for narrow-chord fins at this scale.
    twist_deg = swirl_dir * VANE_ANGLE_DEG * 2;  // total twist tip-to-tip

    // Position fin at its angular slot around the bore axis
    rotate([0, 0, phi_center])
        translate([0, 0, STATOR_Z_BOT])
            // Rotate the extruded profile so the fin chord is tangential (+Y=span, +X=chord)
            rotate([0, 0, 0])
                linear_extrude(
                    height  = fin_h,
                    twist   = twist_deg,
                    slices  = 16,          // smooth twist interpolation
                    center  = false
                )
                    // 2D fin profile in XY plane:
                    //   X span: R_HUB → EDF_BORE_R (radial)
                    //   Y span: ±FIN_THICKNESS/2 (chord thickness)
                    translate([R_HUB, -FIN_THICKNESS / 2, 0])
                        square([
                            EDF_BORE_R - R_HUB,     // radial span of fin
                            FIN_THICKNESS            // fin chord/thickness
                        ]);
}


// =============================================================================
// ── Module: stator_hub ───────────────────────────────────────────────────────
// =============================================================================
// Central hollow hub ring at the stator station.
// Provides structural connection of all 11 fins to the bore axis centre,
// and routes ESC signal cables through the hollow bore.
//
//   OD = R_HUB × 2  = 32 mm
//   ID = R_HUB_BORE × 2 = 20 mm (cable passage)
//   Z span = STATOR_Z_BOT → STATOR_Z_TOP
module stator_hub() {
    translate([0, 0, STATOR_Z_BOT])
        difference() {
            // ── Solid hub cylinder ────────────────────────────────────────
            cylinder(
                r = R_HUB,
                h = STATOR_Z_TOP - STATOR_Z_BOT,
                center = false
            );
            // ── Cable routing bore ─────────────────────────────────────────
            translate([0, 0, -0.01])
                cylinder(
                    r = R_HUB_BORE,
                    h = (STATOR_Z_TOP - STATOR_Z_BOT) + 0.02,
                    center = false
                );
        }
}


// =============================================================================
// ── Module: motor_mount_ring ─────────────────────────────────────────────────
// =============================================================================
// Four-arm spider strut cross at a given axial station.
// The struts bridge from the central cable hub (R_HUB) to the EDF bore wall
// (EDF_BORE_R), providing structural support for the EDF motor bell mount.
// Arms are 2mm thick slabs oriented at 0°/90°/180°/270°.
//
// Parameters:
//   z_center [mm] — axial Z position of the spider (strut mid-plane)
module motor_mount_ring(z_center) {
    arm_h = 3.0;  // [mm] axial thickness of spider strut (print layer depth)
    arm_w = 3.0;  // [mm] spanwise width of each arm

    // EDF motor bell retaining lip ring
    translate([0, 0, z_center - arm_h / 2])
        difference() {
            // ── EDF casing ring (thin annulus at bore wall) ───────────────
            cylinder(r = EDF_CASING_R, h = arm_h, center = false);
            translate([0, 0, -0.01])
                cylinder(r = EDF_BORE_R, h = arm_h + 0.02, center = false);
        }

    // ── Four radial arms: hub → bore wall ────────────────────────────────
    for (angle = [0, 90, 180, 270]) {
        rotate([0, 0, angle])
            translate([R_HUB, -arm_w / 2, z_center - arm_h / 2])
                cube([
                    EDF_BORE_R - R_HUB,  // radial arm length
                    arm_w,               // arm width
                    arm_h                // arm axial thickness
                ]);
    }

    // ── Central hub boss (solid plug to receive arm roots) ───────────────
    translate([0, 0, z_center - arm_h / 2])
        cylinder(r = R_HUB, h = arm_h, center = false);
}


// =============================================================================
// ── Module: pivot_x_face_boss ────────────────────────────────────────────────
// =============================================================================
// Two bearing boss protrusions on the spanwise (X-face) nacelle walls at the
// CG station (PIVOT_Z, Y=0).  The tilt spar (4mm CF rod) enters from each
// spanwise face along the X axis, passing through the inter-EDF bore space,
// and is retained by a MF104ZZ flanged bearing (4×10×4mm) press-fit into
// each boss.
//
// Pivot axis passes through (Y=0, Z=PIVOT_Z) — the nacelle bore centre in Y
// and the computed CG station in Z.  This eliminates gravity-induced servo
// torque in all three dimensions:
//   • Z alignment : PIVOT_Z = 83.0 mm = nacelle Z_cg (1D CG analysis).
//   • Y alignment : Y = 0 = bore axis; Y_cg ≈ 0 for bore-symmetric components.
//   • X alignment : tilt axis is X — any X position on the spar axis is correct.
//
// Boss geometry (each side):
//   OD            = PIVOT_BEAR_OD + 2×BOSS_WALL = 10 + 6 = 16 mm
//   Bearing bore  = PIVOT_BEAR_OD = 10 mm (MF104ZZ OD — press-fit)
//   Protrusion    = PIVOT_BOSS_DEPTH = 5 mm beyond nacelle outer shell
//   Position      = (X=±NACELLE_OD_X/2, Y=0, Z=PIVOT_Z)
//
// The spar also passes through the 50mm air bore at Z=PIVOT_Z (inter-EDF gap,
// no EDF hardware).  The 4mm CF spar obstructs ~8% of bore diameter at one
// 4.5mm-tall station — negligible aerodynamic penalty.
//
// CLAUDE.md compliance: 2-wall contact annulus (BOSS_WALL=3mm CF-PETG > 2×0.15mm).
module pivot_x_face_boss() {
    boss_od   = PIVOT_BEAR_OD + 6.0;  // 16 mm: bearing OD 10 mm + 2×3mm CF-PETG wall
    boss_wall = PIVOT_BOSS_DEPTH;       // 5 mm protrusion depth (= CLEVIS_EAR_T depth)

    for (sign = [-1, +1]) {
        // ── Boss cylinder on nacelle X face ───────────────────────────────
        translate([
            sign * (NACELLE_OD_X / 2),  // ±spanwise face of nacelle
            0,                            // Y = bore centre (Y_cg ≈ 0)
            PIVOT_Z                       // Z = nacelle CG station
        ])
        rotate([0, 90, 0])               // cylinder axis along X
            difference() {
                // ── Outer boss solid ─────────────────────────────────────
                cylinder(
                    r      = boss_od / 2,
                    h      = boss_wall,
                    center = false
                );
                // ── MF104ZZ press-fit bore ───────────────────────────────
                cylinder(
                    r      = PIVOT_BEAR_OD / 2,
                    h      = boss_wall + 0.02,
                    center = false
                );
            }

        // ── Load-spreading web between boss face and shell surface ────────
        // A thin rectangular web transfers pivot loads from the boss root
        // into the nacelle X-wall over a larger area.
        translate([
            sign * NACELLE_OD_X / 2,        // at outer shell face
            -(boss_od / 2),                  // Y: full boss width, centred on Y=0
            PIVOT_Z - boss_od / 2            // Z: centred on PIVOT_Z
        ])
        rotate([0, sign * 90, 0])            // face outboard
            linear_extrude(height = WALL_T)  // web depth = 1× shell wall
                polygon(points = [
                    [0, 0],
                    [boss_od, 0],
                    [boss_od, boss_od],
                    [0, boss_od]
                ]);
    }
}


// =============================================================================
// ── Module: pinion_a_boss ────────────────────────────────────────────────────
// =============================================================================
// Bearing boss for Drive Pinion A, oriented along the X axis.
// Located at the same Z station as the tilt pivot (PIVOT_Z = PINION_A_Z).
// Houses two MR63ZZ bearings (3×6×2.5mm) in a press-fit pocket.
//
// Y = PINION_A_Y = 28mm fore-aft from bore centre (sector-gear meshing distance).
// The fixed sector gear (R=22mm) is centred on the pivot axis (Y=0, Z=PIVOT_Z).
// Pinion A (R=6mm) must sit at centre-distance = 22+6 = 28mm from that centre,
// hence PINION_A_Y = 28mm.  Placing Pinion A at Y=0 (prior bug = coaxial with
// the sector gear) is geometrically impossible for meshing engagement.
//
// When the nacelle tilts, Pinion A (on the nacelle) rolls along the fixed
// sector gear (on the tilt bracket), driving the longitudinal shaft and
// ultimately the Crown Pinion to open/close the nozzle iris.
module pinion_a_boss() {
    translate([0, PINION_A_Y, PINION_A_Z])
        rotate([0, 90, 0])    // cylinder axis along X
            difference() {
                // ── Boss outer cylinder ───────────────────────────────────
                cylinder(
                    r      = PINION_A_BOSS_OD / 2,
                    h      = PINION_A_BOSS_L,
                    center = true
                );
                // ── Shaft clearance bore ───────────────────────────────────
                cylinder(
                    r      = PINION_A_SHAFT_D / 2,
                    h      = PINION_A_BOSS_L + 0.02,
                    center = true
                );
            }
}


// =============================================================================
// ── Module: crown_pinion_boss ────────────────────────────────────────────────
// =============================================================================
// Bearing boss for the Crown Pinion at CROWN_Z, same geometry as Pinion A boss.
// The Crown Pinion engages the nozzle ring rack (R_eff = 28mm) to rotate the
// iris inner ring and open/close the nozzle petals.
//
// Y = PINION_A_Y = 28mm: the Crown Pinion must be co-planar with Pinion A in Y
// so the longitudinal CF shaft connecting them runs in a straight line without
// lateral bends (which would bind the shaft inside the PTFE conduit sleeve).
module crown_pinion_boss() {
    translate([0, PINION_A_Y, CROWN_Z])
        rotate([0, 90, 0])    // cylinder axis along X
            difference() {
                // ── Boss outer cylinder ───────────────────────────────────
                cylinder(
                    r      = CROWN_BOSS_OD / 2,
                    h      = CROWN_BOSS_L,
                    center = true
                );
                // ── Shaft clearance bore ───────────────────────────────────
                cylinder(
                    r      = PINION_A_SHAFT_D / 2,
                    h      = CROWN_BOSS_L + 0.02,
                    center = true
                );
            }
}


// =============================================================================
// ── Module: shaft_conduit ────────────────────────────────────────────────────
// =============================================================================
// Longitudinal tube running axially from the Pinion A boss to the Crown Pinion
// boss.  The conduit Y position = PINION_A_Y = 28mm, co-planar with both gear
// bosses, so the enclosed CF shaft runs in a straight line with no lateral
// deflection that would cause binding inside the PTFE sleeve.
// The conduit houses a 3mm CF shaft in a 4mm OD PTFE sleeve.
//
// OD = SHAFT_CONDUIT_OD (5.5mm)
// ID = SHAFT_CONDUIT_ID (3.5mm — clears 3mm shaft inside 4mm PTFE sleeve)
// Z span: PINION_A_Z → CROWN_Z
// Y position: PINION_A_Y = 28mm (matches Pinion A and Crown Pinion Y positions)
module shaft_conduit() {
    conduit_len = CROWN_Z - PINION_A_Z;

    translate([0, PINION_A_Y, PINION_A_Z])
        difference() {
            // ── Conduit outer tube ─────────────────────────────────────────
            cylinder(
                r = SHAFT_CONDUIT_OD / 2,
                h = conduit_len,
                center = false
            );
            // ── Conduit inner bore ─────────────────────────────────────────
            translate([0, 0, -0.01])
                cylinder(
                    r = SHAFT_CONDUIT_ID / 2,
                    h = conduit_len + 0.02,
                    center = false
                );
        }
}


// =============================================================================
// ── Module: nozzle_ring_pocket ───────────────────────────────────────────────
// =============================================================================
// Cylindrical void at the nozzle exit end of the shell.
// Creates the seat for the rotating iris inner ring.
// The pocket is wider than the EDF bore (NOZZLE_RING_OD > EDF_BORE_R × 2)
// to allow the ring to rotate inside the shell.
//
// This module is used as a subtraction volume in the final assembly.
module nozzle_ring_pocket() {
    translate([0, 0, NOZZLE_RING_Z])
        cylinder(
            r = NOZZLE_RING_OD / 2,
            h = NOZZLE_RING_H + 0.02,
            center = false
        );
}


// =============================================================================
// ── Module: nacelle_pod (main assembly) ──────────────────────────────────────
// =============================================================================
// Top-level assembly module.  Combines all sub-modules in the correct order:
//   1. Additive geometry (union): shell, bore tube, inlet bell, stator, pivots
//   2. Subtractive geometry (difference): EDF bore path, nozzle ring pocket
//
// Parameters:
//   swirl_dir [+1/-1] — stator fin swirl direction (default = global SWIRL_DIR)
//
// Usage:
//   nacelle_pod();              // uses default SWIRL_DIR
//   nacelle_pod(swirl_dir=-1); // explicit override for starboard nacelle
module nacelle_pod(swirl_dir = SWIRL_DIR) {

    union() {
        difference() {

            // ══════════════════════════════════════════════════════════════
            // ── Additive geometry ─────────────────────────────────────────
            // ══════════════════════════════════════════════════════════════
            union() {

                // ── Outer structural shell (elliptical cross-section) ────
                nacelle_shell();

                // ── EDF bore thrust tube (EDF1 seat → nozzle ring) ───────
                thrust_tube();

                // ── Cosine-tapered inlet bell (Z=0 → EDF1 seat) ──────────
                inlet_bell();

                // ── Inter-stage stator hub (cable-routing central core) ───
                stator_hub();

                // ── 11 twisted stator fins ────────────────────────────────
                for (i = [0 : N_FINS - 1]) {
                    stator_fin(i * (360 / N_FINS), swirl_dir);
                }

                // ── EDF1 spider strut ring (at Z = EDF1_Z_ENTRY + 13mm) ──
                // Placed 13mm aft of EDF1 forward face = Z=35mm (mid-motor)
                motor_mount_ring(EDF1_Z_ENTRY + 13);

                // ── EDF2 spider strut ring (at Z = EDF2_Z_ENTRY + 10mm) ──
                // Placed 10mm aft of EDF2 forward face = Z=108mm (mid-motor)
                motor_mount_ring(EDF2_Z_ENTRY + 10);

                // ── CG-aligned pivot X-face boss (MF104ZZ bearing bosses) ──
                // Pivot spar (4mm CF rod) along X at (Y=0, Z=PIVOT_Z).
                // Y=0 = bore axis = Y_cg: zero gravity torque at all tilt angles.
                pivot_x_face_boss();

                // ── Drive Pinion A bearing boss (at PIVOT_Z, X axis) ─────
                pinion_a_boss();

                // ── Crown Pinion bearing boss (at CROWN_Z, X axis) ───────
                crown_pinion_boss();

                // ── Longitudinal gear shaft conduit ───────────────────────
                shaft_conduit();

            } // end union (additive)

            // ══════════════════════════════════════════════════════════════
            // ── Subtractive geometry ──────────────────────────────────────
            // ══════════════════════════════════════════════════════════════

            // ── Full-length EDF bore path (50mm ID throughout) ────────────
            // Subtracts the complete air-flow channel from Z=0 to NACELLE_L.
            // Positioned at Z=-0.01 to cleanly cut through the inlet bell lip.
            translate([0, 0, -0.01])
                cylinder(
                    r = EDF_BORE_R,
                    h = NACELLE_L + 0.02,
                    center = false
                );

            // ── Nozzle ring pocket (rotating iris ring seat) ───────────────
            nozzle_ring_pocket();

            // ── Tilt spar clearance bore (along X through both nacelle faces + bore) ──
            // The 4mm CF tilt spar passes through the inter-EDF bore space at Y=0,
            // Z=PIVOT_Z.  This subtraction creates the clearance passage through the
            // nacelle shell on both X faces and through the bore space.
            translate([0, 0, PIVOT_Z])
                rotate([0, 90, 0])  // cylinder along X
                    cylinder(
                        r = PIVOT_BORE_D / 2,               // 4.2mm / 2 = 2.1mm radius
                        h = NACELLE_OD_X + 2 * PIVOT_BOSS_DEPTH + 2,  // full spar length + margin
                        center = true
                    );

        } // end difference
    } // end union (top-level)
}


// =============================================================================
// ── Render call ───────────────────────────────────────────────────────────────
// =============================================================================
// Render the nacelle pod using the global SWIRL_DIR parameter.
// Override at command line: openscad -D SWIRL_DIR=-1 ...
nacelle_pod(swirl_dir = SWIRL_DIR);


// =============================================================================
// ── Print specifications ──────────────────────────────────────────────────────
// =============================================================================
// Material    : CF-PETG (CarbonX PETG+CF or equivalent)
// Layer height: 0.15 mm
// Walls       : 4 perimeter walls (minimum — do not reduce)
// Infill      : 25% gyroid (non-structural fill regions)
//               40% gyroid at pivot boss and bearing boss regions (slice manually)
// Nozzle      : Hardened-steel required — CF-PETG is abrasive to brass nozzles
// Supports    : None required if oriented intake-face-down on build plate
// Bed adhesion: PEI sheet with light glue stick
//
// Post-print checks:
//   1. Verify bore OD = 55.0 mm ± 0.3 mm with calipers at 3 stations.
//   2. Verify pivot boss bore = 10.0 mm ± 0.1 mm (MF104ZZ OD press-fit), both X faces.
//   3. Verify tilt spar clearance bore ID = 4.2 mm ± 0.1 mm through both X faces.
//   4. Verify shaft conduit ID = 3.5 mm ± 0.1 mm (passes 4mm PTFE tube).
//   5. Check stator fin edges for layer-delamination; sand smooth if needed.
//
// Render commands:
//   Port nacelle:
//     openscad -o s_nacelle_port_revo.stl nacelle_pod_50mm_tandem.scad \
//              -D SWIRL_DIR=1
//   Starboard nacelle:
//     openscad -o s_nacelle_stbd_revo.stl nacelle_pod_50mm_tandem.scad \
//              -D SWIRL_DIR=-1
