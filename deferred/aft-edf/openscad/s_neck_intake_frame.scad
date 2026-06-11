// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  Primary-component STLs published to airframe/stls/
//   are stored directly in hull frame, baked by tools/bake_hull_frame.py
//   (marker 'SerenityUAV HULL-FRAME R1' in the binary STL header).
//   NEVER re-bake a mesh derived from an already-baked file.
//   This file:
//     Part-local frame.  DEFERRED - Phase 11 (aft fuselage EDF).  On
//     integration, position in hull frame per the validated assembly and
//     bake or place explicitly; stations quoted from nose convert to hull
//     Y via nose tip at hull Y = -305.6 mm.
// ===========================================================================
// s_neck_intake_frame.scad
// CF-PETG structural intake frame ring for Serenity Rev N 24" hull.
// Bonds into the 4 radial scoop cutouts in s_middle_canonical_edf_intake.stl
// at the neck station (Z = 30 mm in the neck shell, Z-longitudinal coords).
// Print in CF-PETG; bond with structural epoxy.
//
// Rev C (2026-06-02): Z-longitudinal axis correction.
//   Coordinate system: Z = longitudinal (fore-aft), X = lateral, Y = vertical.
//   Both middle and rear shells sit on their flat Z=0 face for printing.
//   Hull dimensions re-measured via Z-slice at Z=30 mm.
//   See blender_middle_intake_cut.py Rev C for matching hull cut parameters.
//
// Coordinate origin: hull XY centreline at intake station.
// Frame axial direction = Z (same as hull longitudinal).

// ── Hull cross-section at intake station Z = 30 mm (measured, 24" scale) ────
// Source: Z-slice sweep of s_middle_canonical_shell24.stl,
//   Serenity UAV project log 2026-06-02 (Z-longitudinal Rev C).
// At Z=30: X span=177 mm (centre X=180.9), Y span=156.5 mm (centre Y=-77.8).
// Half-dimensions from XY centreline:
//   X half-width  = 88.5 mm → HULL_W2 = 89
//   Y half-height = 78.3 mm → HULL_H2 = 78
HULL_W2  = 89;     // X lateral half-width from centreline       [mm]
HULL_H2  = 78;     // Y vertical half-height from centreline     [mm]
HULL_WL  = 177;    // full width  (= 2 × HULL_W2 − 1)
HULL_HL  = 157;    // full height (= 2 × HULL_H2 + rounding)

// ── Scoop window dimensions ──────────────────────────────────────────────────
// Matched to blender_middle_intake_cut.py Rev C: SCOOP_W=75, SCOOP_H=38.
// X-scoops: 48 mm wall remaining.  Y-scoops: 37 mm wall remaining.
// Total capture area: 4 × 75 × 38 = 11 400 mm² (≈ 107 % of EDF fan annulus).
SCOOP_W  = 75;     // circumferential window width               [mm]
SCOOP_H  = 38;     // radial window height                       [mm]

// ── Frame geometry ───────────────────────────────────────────────────────────
FRAME_AX = 38;     // axial length of frame ring (matches SCOOP_AX) [mm]
FRAME_RD = 10;     // radial depth of frame collar               [mm]
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
