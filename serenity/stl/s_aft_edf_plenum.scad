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
module aft_edf_plenum() {
    difference() {
        union() {
            // EDF outlet bell: circular duct matching EDF OD
            _edf_outlet_bell();
            // Four tapered arms transitioning to rectangular inlets
            for (a = [0, 90, 180, 270])
                rotate([0, 0, a]) _inlet_arm();
            // Central merger hub connecting all four arms
            _merger_hub();
        }
        // Hollow out — keep WALL-thick walls everywhere
        union() {
            // Inner EDF bore (annular; hub centre can be solid for mounting)
            translate([0, 0, -1])
            cylinder(h = 20 + 1, d = EDF_D - 2*WALL);
            // Hollow each arm interior
            for (a = [0, 90, 180, 270])
                rotate([0, 0, a]) _inlet_arm_hollow();
            // Hollow merger hub
            _merger_hub_hollow();
        }
    }
    // EDF retaining lip ring (stands proud ~3mm on aft face for bonding)
    _edf_lip();
}

// Outlet bell: circular PETG sleeve bonding over EDF casing
module _edf_outlet_bell() {
    translate([0, 0, 0])
    cylinder(h = 18, d = EDF_D + 2*WALL);
}

module _edf_lip() {
    translate([0, 0, -3])
    difference() {
        cylinder(h = 3, d = EDF_D + 2*WALL + 6);
        cylinder(h = 3 + 1, d = EDF_D, center = false);
    }
}

// One tapered inlet arm pointing in +Y before rotation
module _inlet_arm() {
    // Rectangular inlet section (constant cross-section)
    translate([0, EDF_D/2 + WALL, TOTAL_L - ARM_LEN + WALL])
    rotate([90, 0, 0])
    linear_extrude(height = ARM_LEN)
    square([ARM_W, ARM_H], center = true);

    // Tapered transition: rectangular outlet → circular merger zone
    translate([0, EDF_D/2 + WALL, WALL])
    rotate([90, 0, 0])
    _taper_solid(ARM_W, ARM_H, CENTRE_R * 2, CENTRE_R * 2, TAPER_L);
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
