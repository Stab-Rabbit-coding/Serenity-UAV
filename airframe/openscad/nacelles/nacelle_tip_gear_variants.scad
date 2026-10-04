// =============================================================================
// nacelle_tip_gear_variants.scad — tilt tip-stage gear options, 64 mm nacelle
// =============================================================================
// WBS NAC-64-TILT-01 / owner request 2026-10-03 ("model all these and show me
// the images").  The 50T m0.8 / 5 mm-face printed ring on the 64 mm trunnion
// reaches Lewis FOS 2.0 at the CFD bounding crossflow and 3.6 at the corridor
// (tools/nacelle_tilt_dynamics.py); FOS >= 4 is required.  Three options:
//
//   VARIANT = 0  baseline   m0.8, 50T/14T, face 5.0  (as built)
//   VARIANT = 1  A          m0.8, 50T/14T, face 10.5 (ratio, centre distance
//                           unchanged; band grows toward the spar tip)
//   VARIANT = 2  B          m1.0, 50T/14T, face 8.2  (centre distance
//                           25.6 -> 32.0: the wing drive shaft moves 6.4 mm)
//   VARIANT = 3  C          m0.8, 50T/14T, face 5.6  (corridor-only design)
//
// Each renders the trunnion (with the variant ring) and the wing's 14T pinion
// in mesh, pinion axis parallel to the tilt axis at the centre distance.  The
// gear band keeps its INBOARD edge at the baseline's part z 12.5, so the
// pinion's wing-side face stays where the wing places it.
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CEH (Stab-Rabbit-coding) —
// request.  Model by Claude (Claude Opus 5.5, Anthropic) under the author's
// direction, per AGENTS.md AI attribution.  Derivative of
// nacelle_trunnion_64mm.scad / nacelle_trunnion.scad.
// License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
// =============================================================================

VARIANT   = 1;
T64_NO_RENDER = true;
V_M    = [0.8, 0.8, 1.0, 0.8][VARIANT];
V_FACE = [5.0, 10.5, 8.2, 5.6][VARIANT];
PINION_Z = 14;
GEAR_INBOARD = 12.5;                   // part-z of the band's wing-side edge

include <nacelle_trunnion_64mm.scad>

// Ring-gear overrides (the trunnion's involute functions read these).
GEAR_M    = V_M;
GEAR_FACE = V_FACE;
GEAR_Z0   = GEAR_INBOARD - V_FACE;
CENTRE_D  = V_M * (GEAR_Z + PINION_Z) / 2;    // 25.6 / 25.6 / 32.0 / 25.6

// Pinion involute (same construction, 14 teeth).
function p_rb()  = V_M * PINION_Z / 2 * cos(GEAR_PA);
function p_ra()  = V_M * PINION_Z / 2 + V_M;
function p_rf()  = V_M * PINION_Z / 2 - 1.25 * V_M;
function p_flank(r) = 90 / PINION_Z
    + (inv_rad(GEAR_PA) - inv_rad(acos(p_rb() / r))) * 180 / PI;
function p_r(i) = max(p_rf(), p_rb()) + (p_ra() - max(p_rf(), p_rb())) * i / 9;
// Core at the ROOT circle with radial flanks rf -> rb (14T: rf < rb); a core
// filled to rb blocks the ring's tips (see wing_tilt_pinion.scad).
module pinion_2d() {
    a0 = p_flank(max(p_rf(), p_rb()));
    union() {
        circle(r = p_rf() + 0.01);
        for (k = [0 : PINION_Z - 1]) rotate(k * 360 / PINION_Z)
            polygon([[0, 0], [p_rf() * cos(-a0), p_rf() * sin(-a0)],
                     [p_rb() * cos(-a0), p_rb() * sin(-a0)],
                     [p_rb() * cos(a0), p_rb() * sin(a0)],
                     [p_rf() * cos(a0), p_rf() * sin(a0)]]);
        for (k = [0 : PINION_Z - 1]) rotate(k * 360 / PINION_Z)
            polygon(concat(
                [ for (i = [0 : 9]) let(r = p_r(i), a = -p_flank(r))
                      [r * cos(a), r * sin(a)] ],
                [ for (i = [9 : -1 : 0]) let(r = p_r(i), a = p_flank(r))
                      [r * cos(a), r * sin(a)] ]));
    }
}
module pinion() {
    difference() {
        translate([0, 0, GEAR_Z0]) linear_extrude(V_FACE) pinion_2d();
        translate([0, 0, GEAR_Z0 - 1]) cylinder(d = 4.0, h = V_FACE + 2, $fn = 24);
    }
}

// Reusable by nacelle_tilt_joint_context.scad (set VARIANT_RENDER = false).
module variant_trunnion() { nacelle_trunnion(); }
// Pinion in the TRUNNION PART frame, at centre distance along azimuth `az`
// (deg) about the part z axis; mesh phase puts a pinion gap on the line.
module variant_pinion(az = 0) {
    rotate([0, 0, az]) translate([CENTRE_D, 0, 0])
        rotate([0, 0, 180 + 180 / PINION_Z]) pinion();
}
VARIANT_RENDER = true;
if (VARIANT_RENDER) {
    color("SteelBlue") variant_trunnion();
    color("Goldenrod") variant_pinion();
}
echo(VARIANT = VARIANT, gear_module = V_M, face = V_FACE, centre_d = CENTRE_D,
     band = [GEAR_Z0, GEAR_INBOARD], ring_tip_d = 2 * GEAR_RA);
