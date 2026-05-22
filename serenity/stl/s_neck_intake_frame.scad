// s_neck_intake_frame.scad
// CF-PETG structural intake frame ring for Serenity Rev N 24" hull
// Bonds into the 4 scoop cutouts at the neck station (~310mm from nose)
// Print in CF-PETG; bond with structural epoxy.
//
// Coordinate origin: centre of the ring on the fuselage centreline axis.
// +X = forward (toward nose); fuselage axis = Z when printed upright.

// ── Hull cross-section at neck station (24" scale) ──────────────────────────
HULL_W2  = 63;     // port/stbd half-width at station 310mm  [mm]
HULL_H2  = 50;     // dorsal/ventral half-height (elliptical) [mm]
HULL_WL  = 126;    // full width
HULL_HL  = 100;    // full height

// ── Scoop window dimensions ──────────────────────────────────────────────────
SCOOP_W  = 65;     // circumferential width of each scoop cutout [mm]
SCOOP_H  = 60;     // radial height of each scoop cutout         [mm]

// ── Frame geometry ───────────────────────────────────────────────────────────
FRAME_AX = 38;     // axial length of frame ring                 [mm]
FRAME_RD = 14;     // radial depth of frame collar               [mm]
WALL     =  3;     // CF-PETG wall thickness                     [mm]
TONGUE_D =  5;     // tongue depth inserting into hull cutout    [mm]
SHOULDER =  5;     // bonding shoulder pressing on hull exterior  [mm]
LIP      =  6;     // forward aerodynamic lip projection          [mm]
DUCT_L   = 22;     // internal duct arm length inward (→ plenum) [mm]

// ── Derived ─────────────────────────────────────────────────────────────────
$fn = 64;
HALF_AX  = FRAME_AX / 2;

// ── Main module ─────────────────────────────────────────────────────────────
module neck_intake_frame() {
    difference() {
        union() {
            _elliptical_collar();
            for (a = [0, 90, 180, 270])
                rotate([0, 0, a]) _scoop_duct();
        }
        // Cut the 4 scoop windows through the collar
        for (a = [0, 90, 180, 270])
            rotate([0, 0, a]) _scoop_window();
        // Hollow the collar interior (leave WALL-thick walls)
        _collar_hollow();
    }
}

// Elliptical ring collar that matches hull outer profile + FRAME_RD
module _elliptical_collar() {
    linear_extrude(height = FRAME_AX, center = true)
    difference() {
        // Outer ellipse: hull outer surface + frame radial depth
        scale([(HULL_W2 + FRAME_RD) / HULL_W2,
               (HULL_H2 + FRAME_RD) / HULL_H2])
            ellipse(HULL_W2, HULL_H2);
        // Inner cut: hull outer surface (frame sits on hull exterior)
        ellipse(HULL_W2, HULL_H2);
    }
}

// Thin-wall hollow inside the collar (keep WALL thickness)
module _collar_hollow() {
    linear_extrude(height = FRAME_AX + 2, center = true)
    difference() {
        scale([(HULL_W2 + FRAME_RD - WALL) / HULL_W2,
               (HULL_H2 + FRAME_RD - WALL) / HULL_H2])
            ellipse(HULL_W2, HULL_H2);
        ellipse(HULL_W2 - WALL, HULL_H2 - WALL);
    }
}

// One scoop duct arm (placed pointing +Y before rotation)
// Extends radially inward from the collar opening toward the plenum
module _scoop_duct() {
    // Duct arm: rectangular tube from hull inner wall to plenum centre
    translate([0, HULL_H2, 0])
    rotate([90, 0, 0])
    linear_extrude(height = DUCT_L + FRAME_RD)
    difference() {
        square([SCOOP_W, SCOOP_H], center = true);
        square([SCOOP_W - 2*WALL, SCOOP_H - 2*WALL], center = true);
    }

    // Aerodynamic intake lip on forward edge
    translate([0, HULL_H2 + FRAME_RD, 0])
    rotate([90, 0, 0])
    linear_extrude(height = WALL)
    hull() {
        square([SCOOP_W, SCOOP_H], center = true);
        square([SCOOP_W + LIP*2, SCOOP_H + LIP], center = true);
    }

    // Registration tongue: projects into hull cutout (thin, snug fit)
    translate([0, HULL_H2 - TONGUE_D, 0])
    rotate([90, 0, 0])
    linear_extrude(height = TONGUE_D)
    square([SCOOP_W - 0.4, SCOOP_H - 0.4], center = true);  // 0.2mm clearance

    // Bonding shoulder: flange pressing on hull exterior
    translate([0, HULL_H2, 0])
    rotate([90, 0, 0])
    linear_extrude(height = WALL)
    difference() {
        square([SCOOP_W + SHOULDER*2, SCOOP_H + SHOULDER*2], center = true);
        square([SCOOP_W, SCOOP_H], center = true);
    }
}

// Window cut through collar at each scoop position
module _scoop_window() {
    translate([0, HULL_H2 - 1, 0])
    rotate([90, 0, 0])
    linear_extrude(height = FRAME_RD + 2)
    square([SCOOP_W, SCOOP_H], center = true);
}

// Helper: 2D ellipse
module ellipse(rx, ry) {
    scale([rx, ry]) circle(r = 1);
}

neck_intake_frame();
