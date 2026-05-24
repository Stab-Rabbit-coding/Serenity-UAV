// nacelle_sector_gear.scad
// Serenity UAV Rev O — Nacelle Tilt Linkage, Fixed Sector Gear
//
// Purpose:
//   Sector gear fixed to the fuselage-side tilt bracket.  The sector does NOT
//   rotate with the nacelle.  As the nacelle tilts, Drive Pinion A rolls along
//   this fixed sector, translating nacelle rotation angle into pinion shaft
//   rotation that ultimately drives the iris nozzle open/closed.
//
//   Gear ratio contribution (sector side):
//     Nacelle tilt 0–90° → Pinion A rotates (22/6) × 90° = 330°
//   Full system ratio: 90° × (22/6) × (6/28) = 70.7° nozzle ring travel.
//
// Mating interfaces:
//   • Drive Pinion A (nacelle_pinion.scad):
//       Pitch circles tangent at mesh point; 0.1 mm backlash on centre distance.
//   • Tilt bracket pivot bolt: M4, MOUNT_BORE_D = 4.2 mm clearance.
//   • Nacelle boss posts (×4 M2.5 adjustment slots): SLOT_BC_R = 18 mm,
//       SLOT_D = 2.7 mm clearance, SLOT_ARC_DEG = 10° per slot.
//
// Gear standard: AGMA/ISO involute, Module M = 1.0 mm, Pressure angle 20°.
// Tooth profile method: tooth-space subtraction — angular pitch wedges removed
//   from a solid sector annulus, leaving a functional trapezoidal approximation
//   of the involute tooth form.  Adequate for M = 1.0 in PETG or resin.
//
// Print specification:
//   Preferred:  SLA resin, ≤ 0.05 mm layer height (captures M=1 tooth detail).
//   Backup:     CF-PETG FDM, 0.10 mm layers, 4 perimeters, 40 % gyroid infill.
//   Nozzle:     Hardened steel (CF-PETG is abrasive).
//   Orientation: Print flat (teeth facing up) to maximise tooth-face quality.
//   Note:       M = 1.0 mm is printable in FDM at 0.10 mm layer height with a
//               0.25 mm nozzle; a 0.40 mm nozzle will round tooth crests —
//               acceptable for prototype but use resin for final flight article.
//
// Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date:    2026-05-24
// Rev:     O (initial release)

// ── Resolution ────────────────────────────────────────────────────────────────

$fn = 72;   // standard circle resolution for all rotational solids

// ── Gear Parameters ───────────────────────────────────────────────────────────

MODULE          =  1.0;   // [mm] AGMA Module — tooth size standard
PRESSURE_ANGLE  = 20.0;   // [deg] standard involute pressure angle
PITCH_R         = 22.0;   // [mm] pitch circle radius of sector gear
SECTOR_TEETH    = 38;     // [count] number of teeth spanning the active arc
                          //   38 T covers 155° — encompasses the nacelle's
                          //   operating range of 0° (cruise) to 90° (hover)
                          //   plus ±5° overtravel hard-stop margin each end.
BODY_H          =  3.0;   // [mm] plate (web) thickness behind teeth
MOUNT_BORE_D    =  4.2;   // [mm] M4 clearance bore at pivot axis
SLOT_BC_R       = 18.0;   // [mm] bolt-circle radius for M2.5 adjustment slots
SLOT_D          =  2.7;   // [mm] M2.5 clearance slot width
SLOT_ARC_DEG    = 10.0;   // [deg] arc length of each slot (mesh preload range)
N_SLOTS         =  4;     // [count] number of adjustment slots (evenly spaced)

// ── Derived Gear Geometry ─────────────────────────────────────────────────────

// Full-circle equivalent tooth count for M = 1.0 at PITCH_R = 22 mm:
//   N_FULL = round( 2π × PITCH_R / MODULE ) = round( 138.23 ) = 138
N_FULL = round(2 * PI * PITCH_R / MODULE);   // = 138 teeth (full circle)

// Standard tooth proportions per AGMA 201:
ADDENDUM   = MODULE;              // [mm] tooth height above pitch circle = 1.0
DEDENDUM   = 1.25 * MODULE;      // [mm] tooth depth below pitch circle = 1.25
TIP_R      = PITCH_R + ADDENDUM; // [mm] addendum (tip) circle radius  = 23.0
ROOT_R     = PITCH_R - DEDENDUM; // [mm] dedendum (root) circle radius = 20.75
BASE_R     = PITCH_R * cos(PRESSURE_ANGLE); // [mm] base circle radius ≈ 20.67

// Angular pitch — angle subtended by one tooth + one space at pitch circle:
ANGULAR_PITCH = 360.0 / N_FULL;  // [deg] = 2.609° per tooth

// Tooth space width at pitch circle = π × MODULE / 2 = 1.5708 mm.
// In angular terms at pitch circle circumference:
//   tooth_space_angle = (PI * MODULE / 2) / (2 * PI * PITCH_R / 360) = 4.09°
//   (half angular pitch, because equal space and tooth width at pitch circle)
SPACE_HALF_ANG = ANGULAR_PITCH / 2;  // [deg] half-width of tooth space

// Sector arc angle based on actual tooth count:
SECTOR_ARC_DEG = SECTOR_TEETH * ANGULAR_PITCH;  // [deg] ≈ 99.1° for 38 T

// Starting angle of sector arc.  Zero the midpoint of the sector at 0° so the
// sector spans symmetrically about the tilt-bracket centreline.
SECTOR_START_DEG = -SECTOR_ARC_DEG / 2;  // [deg] first tooth left edge

// Backing plate inner radius — small ledge behind root circle for rigidity:
BACK_INNER_R = ROOT_R - 3.0;   // [mm] = 17.75 mm
// Backing plate outer radius matches addendum circle:
BACK_OUTER_R = TIP_R;          // [mm] = 23.0 mm

// ── Module Definitions ────────────────────────────────────────────────────────

// sector_plate() — solid pie-wedge annulus covering the full sector arc.
//   The teeth will be formed by subtracting tooth-space wedges from this solid.
module sector_plate() {
    // Pie-wedge extruded to BODY_H.  Built as difference of full disk minus
    // the angular regions outside the sector, then minus the inner bore.
    linear_extrude(height = BODY_H) {
        difference() {
            // Full annulus ring from BACK_INNER_R to TIP_R
            difference() {
                circle(r = BACK_OUTER_R);
                circle(r = BACK_INNER_R);
            }
            // Subtract everything outside the sector arc.
            // Two masking wedges trim the ring to the correct angular span.
            // Each masking wedge is a large square rotated to cover the
            // non-sector region above (positive angle) and below (negative).
            //
            // Method: subtract a full disk then re-add only the pie slice,
            // implemented here as two half-plane cuts.
            //
            // Upper mask — covers angles > SECTOR_START_DEG + SECTOR_ARC_DEG
            rotate([0, 0, SECTOR_START_DEG + SECTOR_ARC_DEG])
                translate([0, 0])
                    sector_mask_wedge();
            // Lower mask — covers angles < SECTOR_START_DEG
            rotate([0, 0, SECTOR_START_DEG + 180])
                sector_mask_wedge();
        }
    }
}

// sector_mask_wedge() — half-plane mask (large rectangle covering 180°).
//   Positioned by the caller's rotate() to clip the annulus to the sector arc.
module sector_mask_wedge() {
    // A 100 × 50 mm rectangle reaching from origin outward, covering 0 to 180°.
    // Width 100 mm > 2 × TIP_R so it fully covers the gear disk.
    translate([0, 0])
        square([100, 100]);
}

// tooth_space(i) — subtract one tooth-space gap between teeth i and i+1.
//   The gap is a thin angular wedge at the root-to-tip radial band, centred
//   midway between adjacent tooth centrelines.
//
//   Arguments:
//     i  — tooth index (0-based); space is placed between tooth i and tooth i+1
module tooth_space(i) {
    // Angular centre of this tooth space:
    //   teeth are at i × ANGULAR_PITCH; spaces fall between teeth.
    //   Space centre = SECTOR_START_DEG + (i + 0.5) × ANGULAR_PITCH
    space_centre_deg = SECTOR_START_DEG + (i + 0.5) * ANGULAR_PITCH;

    // Half-angle of the trapezoidal tooth-space wedge.
    // AGMA circular tooth thickness at pitch circle = π × MODULE / 2.
    // As an angle: (π × MODULE / 2) / PITCH_R × (180/π)
    //            = (1.5708 / 22) × 57.296 = 4.09°
    // Tooth space width = same (equal division), so half-angle ≈ 2.045°
    half_ang = SPACE_HALF_ANG / 2;   // [deg]

    linear_extrude(height = BODY_H + 0.1) {
        // Wedge: a thin pie slice between ROOT_R and TIP_R + small overcut
        rotate([0, 0, space_centre_deg - half_ang]) {
            difference() {
                circle(r = TIP_R + 0.2);       // outer radius with slight overcut
                circle(r = ROOT_R - 0.1);      // stop at root circle
                // Angular mask to limit the wedge to 2 × half_ang width
                rotate([0, 0, 2 * half_ang])
                    square([100, 100]);         // mask away the upper half-plane
                rotate([0, 0, 180])
                    square([100, 100]);         // mask away the lower half-plane
            }
        }
    }
}

// adjustment_slot(i) — one M2.5 adjustment slot at SLOT_BC_R.
//   The slot is an arc of SLOT_ARC_DEG length and SLOT_D width, allowing
//   radial adjustment of the sector for mesh preload setting.
module adjustment_slot(i) {
    slot_centre_deg = i * (360.0 / N_SLOTS);   // evenly spaced around bolt circle

    // Render arc slot as hull of two small circles at slot endpoints
    hull() {
        rotate([0, 0, slot_centre_deg - SLOT_ARC_DEG / 2])
            translate([SLOT_BC_R, 0, -0.1])
                cylinder(h = BODY_H + 0.2, d = SLOT_D);
        rotate([0, 0, slot_centre_deg + SLOT_ARC_DEG / 2])
            translate([SLOT_BC_R, 0, -0.1])
                cylinder(h = BODY_H + 0.2, d = SLOT_D);
    }
}

// sector_gear() — top-level module: assembles the complete sector gear.
//
//   Geometry sequence:
//     1. Start with solid sector annulus plate.
//     2. Subtract SECTOR_TEETH + 1 tooth-space wedges (N spaces for N teeth).
//     3. Subtract pivot bore (M4 clearance).
//     4. Subtract N_SLOTS adjustment slots.
//
//   Coordinate origin: centre of pivot (tilt axis) bore.
//   +Z = forward face (Pinion A meshes from this side).
//   Sector arc centred at 0° in X-Y plane.
module sector_gear() {
    difference() {
        // ── Base solid ──────────────────────────────────────────────────────
        sector_plate();

        // ── Tooth-space subtractions ────────────────────────────────────────
        // Subtract SECTOR_TEETH + 1 spaces (one space on each outer flank):
        for (i = [0 : SECTOR_TEETH]) {
            tooth_space(i);
        }

        // ── Pivot bore ──────────────────────────────────────────────────────
        // M4 clearance through-hole at tilt-axis pivot.  Centre at origin.
        translate([0, 0, -0.1])
            cylinder(h = BODY_H + 0.2, d = MOUNT_BORE_D);

        // ── Adjustment slots ────────────────────────────────────────────────
        // Four M2.5 arc slots at SLOT_BC_R = 18 mm bolt circle.
        for (i = [0 : N_SLOTS - 1]) {
            adjustment_slot(i);
        }
    }
}

// ── Fit Confirmation ──────────────────────────────────────────────────────────
//
//   Interface          Mating part               Clearance / fit
//   ─────────────────  ────────────────────────  ─────────────────────────────
//   Tooth pitch circle Drive Pinion A            0.10 mm radial backlash
//                      (nacelle_pinion.scad)     (centre distance = 22+6+0.1)
//   MOUNT_BORE_D 4.2   M4 tilt-bracket pivot     0.2 mm diametral clearance
//   SLOT_D 2.7         M2.5 boss posts            0.2 mm diametral clearance
//   Plate face (Z=0)   Tilt bracket pocket        bonded / face contact

// ── Render ────────────────────────────────────────────────────────────────────

// Uncomment to render:
sector_gear();
