// s_edf_120_motor_mount.scad
// 120mm EDF motor-mount spider + forward fairing cone
// for Serenity Rev N rear fuselage EDF installation.
//
// Remixed from Thingiverse thing:2838324 (120mm fuselage EDF with motor mount).
// This file provides only the structural motor-mount ring, spider arms, and
// aerodynamic fairing cone. The EDF rotor and casing are commercial parts.
//
// Coordinate system: +Z = forward (toward nose / intake face of EDF).
// Z=0 = aft face of motor mount (where motor face sits).
// The outer ring clamps/bonds to the INNER bore of the EDF casing.
//
// Integration interfaces:
//   Forward (Z=RING_L): registration spigot drops into s_aft_edf_plenum
//                       outlet bell at station ~430mm from nose.
//   Aft (Z=0):          motor face at hub; M3 bolt pattern at BOLT_R.
//   Cone tip (Z=-CONE_L): aerodynamic fairing, no fastener.
//
// Print: CF-PETG, 0.15mm layers, 40% gyroid infill, 4 perimeter walls.
// Nozzle: hardened steel (CF-PETG abrasive).
// Post-process: lightly sand hub bolt-pattern face flat before motor install.

// ── Geometry parameters ────────────────────────────────────────────────────

EDF_BORE    = 120;   // [mm] EDF casing inner diameter (fan bore)
RING_OD     = 126;   // [mm] outer ring OD (friction/bond fit into EDF casing)
RING_ID     = 112;   // [mm] outer ring ID (clears airflow annulus)
RING_L      =  10;   // [mm] axial length of outer ring
RING_TAPER  =   1;   // [mm] chamfer at forward edge for easy insertion

SPIGOT_OD   = 120;   // [mm] forward registration spigot fits plenum bell ID
SPIGOT_L    =   8;   // [mm] length of spigot beyond ring face
SPIGOT_W    =   3;   // [mm] wall thickness of spigot tube

ARM_COUNT   =   3;   // number of spider arms
ARM_W       =   6;   // [mm] arm width (circumferential)
ARM_H       =   6;   // [mm] arm height (radial, tapers inward)
// arms span from RING_ID/2 down to HUB_OD/2

HUB_OD      =  38;   // [mm] central motor hub outer diameter
HUB_L       =  18;   // [mm] axial length of hub (aft face at Z=0)
HUB_BORE    =   8;   // [mm] central bore through hub (motor shaft / wiring)
BOLT_R      =  12;   // [mm] M3 bolt pattern radius (24mm bolt circle)
BOLT_D      =   3.2; // [mm] M3 clearance hole diameter
BOLT_COUNT  =   3;   // 3× M3 at 120° on bolt circle

CONE_L      =  35;   // [mm] fairing cone length behind motor face (aft, −Z)
CONE_BASE_R = HUB_OD / 2; // cone base radius matches hub OD
CONE_TIP_R  =   0;   // cone tip (sharp)

$fn = 72;

// ── Modules ────────────────────────────────────────────────────────────────

module outer_ring() {
    difference() {
        // main ring body
        cylinder(h = RING_L, r = RING_OD / 2);
        // bore out airflow annulus
        cylinder(h = RING_L + 1, r = RING_ID / 2);
        // forward insertion chamfer
        translate([0, 0, RING_L - RING_TAPER])
            cylinder(h = RING_TAPER + 1,
                     r1 = RING_OD / 2,
                     r2 = RING_OD / 2 + RING_TAPER + 0.5);
    }
}

module registration_spigot() {
    // thin-wall tube extending forward from ring face for plenum alignment
    translate([0, 0, RING_L])
    difference() {
        cylinder(h = SPIGOT_L, r = SPIGOT_OD / 2);
        cylinder(h = SPIGOT_L + 1, r = SPIGOT_OD / 2 - SPIGOT_W);
    }
}

module spider_arm(angle_deg) {
    rotate([0, 0, angle_deg])
    hull() {
        // outer end: rectangular cross-section at inner face of ring
        translate([RING_ID / 2, 0, RING_L / 2])
            cube([1, ARM_W, ARM_H], center = true);
        // inner end: narrower cross-section at hub OD
        translate([HUB_OD / 2, 0, RING_L / 2])
            cube([1, ARM_W * 0.6, ARM_H * 0.6], center = true);
    }
}

module hub() {
    difference() {
        cylinder(h = HUB_L, r = HUB_OD / 2);
        // central wiring bore
        cylinder(h = HUB_L + 1, r = HUB_BORE / 2);
        // M3 bolt holes
        for (i = [0 : BOLT_COUNT - 1])
            rotate([0, 0, i * 360 / BOLT_COUNT])
            translate([BOLT_R, 0, -0.5])
                cylinder(h = HUB_L + 1, r = BOLT_D / 2);
    }
}

module fairing_cone() {
    // aft-pointing aerodynamic spinner; Z=0 at hub aft face, tip at Z=−CONE_L
    translate([0, 0, -CONE_L])
        cylinder(h = CONE_L, r1 = CONE_TIP_R + 0.4, r2 = CONE_BASE_R);
}

// ── Assembly ───────────────────────────────────────────────────────────────

union() {
    outer_ring();
    registration_spigot();
    for (i = [0 : ARM_COUNT - 1])
        spider_arm(i * 360 / ARM_COUNT);
    hub();
    fairing_cone();
}
