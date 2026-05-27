// s_aft_edf_plenum.scad
// 4-to-1 cross-shaped internal air manifold for Serenity Rev N 24" hull
// Routes airflow from 4 radial neck scoops (station ~310mm) to the 120mm
// fuselage EDF (fan face at station ~430mm, inside Panel F engine bell).
// Print in PETG; bond to intake frame duct arms and EDF mount ring.
//
// Coordinate origin: centre of EDF fan face (output end).
// +Z = forward (toward nose, toward scoop inlets); −Z = aft (toward EDF fan).

// ── Dimensions ───────────────────────────────────────────────────────────────
EDF_D    = 120;    // 120mm EDF outer diameter
EDF_HUB  =  28;    // EDF hub/spinner diameter (annular fan)
ARM_W    =  65;    // duct arm width  (matches scoop window)
ARM_H    =  60;    // duct arm height (matches scoop window)
WALL     =   3;    // duct wall thickness [mm]
ARM_LEN  =  40;    // length of each rectangular inlet arm
TAPER_L  =  40;    // transition / merger zone length
TOTAL_L  =  80;    // ARM_LEN + TAPER_L
CENTRE_R =  20;    // radius of central merger zone (cross-bar where arms meet)

$fn = 64;

// ── Main module ───────────────────────────────────────────────────────────────
// Note: _edf_lip() is included inside the union so it shares the same boolean
// context as the outlet bell.  Placing it outside the difference() creates a
// touching face at Z=0 (lip top == bell bottom) which yields a non-manifold mesh.
module aft_edf_plenum() {
    difference() {
        union() {
            // EDF outlet bell: circular duct matching EDF OD
            _edf_outlet_bell();
            // EDF retaining lip ring (stands proud ~3mm on aft face for bonding).
            // Merged with the bell in this union to avoid touching faces at Z=0.
            _edf_lip();
            // Four tapered arms transitioning to rectangular inlets
            for (a = [0, 90, 180, 270])
                rotate([0, 0, a]) _inlet_arm();
            // Central merger hub connecting all four arms
            _merger_hub();
        }
        // Hollow out — keep WALL-thick walls everywhere
        union() {
            // Inner EDF bore: extend to cover lip region (Z=-3) so the lip is also
            // hollowed.  Height = 20+3+1 covers Z=-4..Z=20, clearing the full lip.
            translate([0, 0, -(3 + 1)])
            cylinder(h = 20 + 3 + 1, d = EDF_D - 2*WALL);
            // Hollow each arm interior
            for (a = [0, 90, 180, 270])
                rotate([0, 0, a]) _inlet_arm_hollow();
            // Hollow merger hub
            _merger_hub_hollow();
        }
    }
}

// Outlet bell: circular PETG sleeve bonding over EDF casing.
// Starts at Z=-0.01 (not Z=0) to avoid a coplanar face with the _edf_lip()
// top face at Z=0 — coincident faces at Z=0 produce non-manifold CGAL topology.
module _edf_outlet_bell() {
    translate([0, 0, -0.01])
    cylinder(h = 18 + 0.01, d = EDF_D + 2*WALL);
}

module _edf_lip() {
    translate([0, 0, -3])
    difference() {
        cylinder(h = 3, d = EDF_D + 2*WALL + 6);
        cylinder(h = 3 + 1, d = EDF_D, center = false);
    }
}

// One tapered inlet arm pointing in +Y before rotation.
// ARM_LEN+1 / TAPER_L+1: each arm solid penetrates 1 mm past the hub outer wall
// (CENTRE_R+WALL = 23 mm) so the union has no touching/coplanar face at that boundary.
// The hollow (_inlet_arm_hollow) already uses the same +1 offset from EDF_D/2 (not
// EDF_D/2+WALL), keeping 3 mm wall thickness throughout.
module _inlet_arm() {
    // Rectangular inlet section — extends 1 mm into hub outer wall
    translate([0, EDF_D/2 + WALL, TOTAL_L - ARM_LEN + WALL])
    rotate([90, 0, 0])
    linear_extrude(height = ARM_LEN + 1)
    square([ARM_W, ARM_H], center = true);

    // Tapered transition: rectangular inlet → square merger zone; 1 mm hub overlap
    translate([0, EDF_D/2 + WALL, WALL])
    rotate([90, 0, 0])
    _taper_solid(ARM_W, ARM_H, CENTRE_R * 2, CENTRE_R * 2, TAPER_L + 1);
}

module _inlet_arm_hollow() {
    IW = ARM_W - 2*WALL;
    IH = ARM_H - 2*WALL;
    translate([0, EDF_D/2, TOTAL_L - ARM_LEN + WALL])
    rotate([90, 0, 0])
    linear_extrude(height = ARM_LEN + 1)
    square([IW, IH], center = true);

    translate([0, EDF_D/2, WALL])
    rotate([90, 0, 0])
    _taper_solid(IW, IH, (CENTRE_R - WALL)*2, (CENTRE_R - WALL)*2, TAPER_L + 1);
}

// Central merger hub: hemisphere-like volume where 4 arms converge
module _merger_hub() {
    translate([0, 0, WALL])
    cylinder(h = TOTAL_L + 2, d = CENTRE_R * 2 + WALL * 2);
}

module _merger_hub_hollow() {
    translate([0, 0, 0])
    cylinder(h = TOTAL_L + 10, d = CENTRE_R * 2);
}

// Parametric linear taper between two rectangles (for use with rotate([90,0,0]))
// Z-axis is the taper axis here; actual orientation handled by caller's rotate
module _taper_solid(w1, h1, w2, h2, length) {
    hull() {
        linear_extrude(height = 0.01)
        square([w1, h1], center = true);
        translate([0, 0, length])
        linear_extrude(height = 0.01)
        square([w2, h2], center = true);
    }
}

aft_edf_plenum();
