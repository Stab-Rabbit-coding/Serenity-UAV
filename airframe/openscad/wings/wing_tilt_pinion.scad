// =============================================================================
// wing_tilt_pinion.scad — nacelle tilt drive, wing-side 14T pinion (64 mm, A)
// =============================================================================
// The pinion on the outboard end of the Ø4 tilt drive shaft (wings_s1223_revo
// .scad tilt_shaft_bore(), station 53.6).  It drives the trunnion's 50T ring
// (nacelle_trunnion_64mm.scad) — module 0.8, 20° PA, i = 3.571, C = 25.6 mm.
// Until 2026-10-03 the pinion existed only as a number; it is now a part.
//
// FACE 10.5 mm — owner option A (WBS NAC-64-TILT-01/-03): matches the widened
// ring face so the full ring face is in contact.
//
// MATERIAL: METAL (steel or brass), NOT PRINTED.  Same tangential load as the
// ring (43.9 N limit, bounding aero), but the Lewis form factor of a 14T gear
// is 0.277 against 0.409 for 50T (Shigley 10th ed. Table 14-2 [REF-STD-GEAR-002],
// table number requires verification).  Root stress 18.9 MPa, so CF-PETG
// (54 MPa [REF-MAT-002]) gives FOS 2.86 < 4.  The material's bending allowable
// must be >= 76 MPa (tools/nacelle_tilt_dynamics.py prints the live figure).
// Wider face cannot fix a printed pinion: contact is limited by the ring face.
//
// RETENTION: one ISO 8752 Ø1.5 x 8 slotted spring pin, cross-drilled through
// pinion and shaft at mid-face.  It carries both torque and axial location;
// pin length 8 < root Ø 9.2, so it stays inside the tooth roots.  Torque at the
// pinion 0.246 N·m limit -> pin double-shear 17 MPa (spring steel, ample).
// No hub: the inboard face sits at the trunnion collar plane (COLLAR_X0 47.84)
// and the outboard face 10.5 mm further into the pod relief; a hub on either
// side would enter the collar slot (Ø5.6) or the spar-tip gap.
//
// PLACEMENT (nacelle-local, PYLON_SIDE = +1): faces at X 37.34 .. 47.84;
// shaft therefore protrudes >= 16.5 mm past the wing tip pad (X 53.84) plus
// 1 mm chamfer run-out = 17.5 mm minimum stick-out.
//
// Mass: 0.852 cm³ (rendered) -> 6.7 g steel / 7.2 g brass (densities 7.85 / 8.5 g/cm³
// ASSUMED nominal); +7 g on the wing tip vs the unmodelled baseline.
//
// IN-CONTEXT CHECK (2026-10-03): this mesh rolled against the 64 mm trunnion
// ring over tilt -5..140 deg (spin = PH + orbit x (1 + 50/14)): tooth overlap
// 0.03-0.06 mm³ throughout (zero-backlash tangency), pod 0 mm³.
//
// Standards: ISO 8752 (spring-type straight pins, slotted, heavy duty) — see
// REFERENCES.md REF-STD-PIN-001.  Involute construction identical to
// nacelle_tip_gear_variants.scad / nacelle_trunnion.scad.
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CEH (Stab-Rabbit-coding) —
// direction.  Part by Claude (Claude Opus 5.5, Anthropic), per AGENTS.md AI
// attribution.  License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
// =============================================================================

TP_M      = 0.8;     // [mm] module
TP_Z      = 14;      // teeth (no-undercut floor at 20° PA)
TP_PA     = 20;      // [deg] pressure angle
TP_FACE   = 10.5;    // [mm] face width (option A)
TP_BORE   = 4.0;     // [mm] Ø4 shaft, H7 bore (ream on the machined part)
TP_PIN_D  = 1.5;     // [mm] ISO 8752 spring pin nominal Ø
TP_PIN_L  = 8.0;     // [mm] pin length
TP_FN     = 48;

function tp_inv(a) = tan(a) - a * PI / 180;
function tp_rb()   = TP_M * TP_Z / 2 * cos(TP_PA);
function tp_ra()   = TP_M * TP_Z / 2 + TP_M;
function tp_rf()   = TP_M * TP_Z / 2 - 1.25 * TP_M;
function tp_r0()   = max(tp_rf(), tp_rb());
function tp_flank(r) = 90 / TP_Z + (tp_inv(TP_PA) - tp_inv(acos(tp_rb() / r))) * 180 / PI;
function tp_r(i)   = tp_r0() + (tp_ra() - tp_r0()) * i / 9;

// 2-D involute profile.  At 14T the root circle (rf 4.60) lies INSIDE the
// base circle (rb 5.26), so the core is the ROOT circle and each flank runs
// radially from rf to rb before the involute starts.  (A core filled out to
// rb — as the variant stand-in does — leaves no room for the ring's tips,
// which reach r 4.80 from the pinion centre: found by the in-context sweep.)
module tilt_pinion_2d() {
    a0 = tp_flank(tp_r0());
    union() {
        circle(r = tp_rf() + 0.01, $fn = TP_FN);
        for (k = [0 : TP_Z - 1]) rotate(k * 360 / TP_Z)
            polygon(concat(
                [[tp_rf() * cos(-a0), tp_rf() * sin(-a0)]],
                [for (i = [0 : 9]) let(r = tp_r(i), a = -tp_flank(r)) [r * cos(a), r * sin(a)]],
                [for (i = [9 : -1 : 0]) let(r = tp_r(i), a = tp_flank(r)) [r * cos(a), r * sin(a)]],
                [[tp_rf() * cos(a0), tp_rf() * sin(a0)]]));
    }
}

// The part: z = 0 is the OUTBOARD face (nacelle side), z = TP_FACE inboard.
module tilt_pinion() {
    difference() {
        linear_extrude(TP_FACE) tilt_pinion_2d();
        translate([0, 0, -1]) cylinder(d = TP_BORE, h = TP_FACE + 2, $fn = 24);
        // spring-pin cross hole at mid-face
        translate([0, 0, TP_FACE / 2]) rotate([0, 90, 0])
            cylinder(d = TP_PIN_D, h = TP_PIN_L + 4, center = true, $fn = 16);
    }
}

assert(TP_PIN_L < 2 * tp_rf(), "spring pin must stay inside the root circle");

if (is_undef(TP_NO_RENDER)) tilt_pinion();
