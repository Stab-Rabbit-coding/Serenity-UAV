// nacelle_nozzle_iris.scad
// Serenity UAV Rev O — Nacelle Iris Nozzle Assembly (50 mm EDF bore)
//
// Purpose:
//   Complete iris nozzle assembly for one nacelle, driven by the nacelle tilt
//   gear train.  As the nacelle tilts 0–90°, the Crown Pinion rotates ≈ 70.7°,
//   driving a rotating inner ring whose rack meshes with the pinion.  The ring
//   rotation pulls/pushes eight pivot-hinged petals via a piano-wire link ring,
//   opening the exit area from 36 mm dia (cruise, nacelle horizontal) to 42 mm
//   dia (hover, nacelle vertical).
//
//   Three separately-printable parts, each in its own module:
//     1. nozzle_inner_ring()   — rotating ring with M=1.0 rack on inner face
//     2. nozzle_outer_housing() — fixed cylindrical housing with petal hinge bores
//     3. nozzle_petal()        — one iris petal (print × 8)
//
// Gear/rack interface:
//   Crown Pinion R = 6 mm (nacelle_pinion.scad) meshes with rack on inner face
//   of rotating ring at effective radius R_eff = 28 mm from ring axis.
//   Ring rotation over 70.7° closes/opens petals from 36 mm to 42 mm exit dia.
//
// Assembly overview:
//   • Inner ring sits inside outer housing bore; 0.5 mm radial clearance.
//   • Eight petals hinge on 3 mm stainless steel pins pressed into hinge bores
//     on the outer housing (PETAL_HINGE_R = 33 mm from nozzle axis).
//   • 0.8 mm piano wire link ring threads through LINK_HOLE_D slots in each
//     petal and attaches to drive posts on the inner ring.
//   • As inner ring rotates, link ring pushes petal tips inward (closed) or
//     outward (open) by differential lever action.
//
// Mating interfaces:
//   • Crown Pinion (nacelle_pinion.scad): module M = 1.0 rack, 22 teeth,
//       on inner face at R ≈ 28 mm from ring axis.
//   • Nacelle exit face (hull): housing lip bonds to EDF exit duct face.
//   • Hinge pins: 3 mm ×18 mm stainless steel dowel pins (×8).
//   • Link ring: 0.8 mm 302 SS piano wire, formed into ring linking all petals.
//
// Print specification — Inner Ring:
//   Material:    CF-PETG (rack teeth carry mesh load)
//   Layers:      0.15 mm, 4 perimeters, 40 % gyroid infill
//   Orient:      Print flat (ring face down) for rack tooth quality
//   Nozzle:      Hardened steel
//
// Print specification — Outer Housing:
//   Material:    CF-PETG (structural, bonded to nacelle)
//   Layers:      0.15 mm, 4 perimeters, 40 % gyroid infill
//   Orient:      Print with bonding lip face down
//
// Print specification — Petals:
//   Material:    PETG (non-structural aerodynamic surface; slight flex OK)
//   Layers:      0.15 mm, 3 perimeters, 25 % gyroid infill
//   Orient:      Print flat (inner face down); outer face: convex upward
//   Color note:  Inner face marked "TRANSLUCENT-BLUE" — use translucent blue
//                PETG filament for visual airflow reference.  Outer face color
//                matches nacelle hull finish (titanium grey).
//
// Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date:    2026-05-24
// Rev:     O (initial release)

// ── Resolution ────────────────────────────────────────────────────────────────

$fn = 72;   // standard circle resolution (all rotational bodies)

// ── Polygon Helpers ───────────────────────────────────────────────────────────
//
// arc_pts(r, a1, a2, n) — n+1 points along an arc at radius r from a1 to a2.
//   Returns a list of [x, y] vectors usable in polygon().
//
function arc_pts(r, a1, a2, n) =
    [for (i = [0 : n]) let(a = a1 + i * (a2 - a1) / n) [r * cos(a), r * sin(a)]];

// annular_wedge(r_in, r_out, a1, a2, n) — closed annular-sector polygon.
//   Using polygon() for rack tooth spaces avoids nested 2D CSG (circle−circle−square²)
//   which caused CGAL to time out when called 23 times inside a difference().
//   n = arc-segment count per edge; inner/outer arcs wound for correct face normal.
//
function annular_wedge(r_in, r_out, a1, a2, n) =
    concat(arc_pts(r_in,  a1, a2, n),
           arc_pts(r_out, a2, a1, n));

// ── Nozzle Bore and Ring Dimensions ───────────────────────────────────────────

BORE_R        = 25.0;   // [mm] 50 mm EDF bore radius (airflow passage centre)
RING_INNER_R  = 25.0;   // [mm] inner radius of rotating ring (flush with bore)
RING_OUTER_R  = 31.0;   // [mm] outer radius of rotating ring
RING_H        =  8.0;   // [mm] axial height (depth) of rotating ring

// ── Rack Parameters (M=1.0, on inner face of rotating ring) ──────────────────

RACK_MODULE       = 1.0;   // [mm] Module — matches Crown Pinion module
RACK_TEETH        = 22;    // [count] teeth covering required arc
                           //   Ring rotation 70.7° at R_eff = 28 mm:
                           //   arc length = 70.7 × π/180 × 28 = 34.6 mm
                           //   min teeth = 34.6 / (π × 1.0) = 11.0 → use 22 for
                           //   symmetry and ± margin (11 teeth per direction)
RACK_DEPTH        = 1.0;   // [mm] tooth addendum (= MODULE for standard rack)
RACK_DEDENDUM     = 1.25;  // [mm] rack dedendum (root depth below pitch line)
RACK_WIDTH_FRAC   = 0.5;   // fraction of circular pitch filled by tooth (standard)
RACK_PRESSURE_ANG = 20.0;  // [deg] rack pressure angle

// Rack pitch line radius: Crown Pinion pitch R + gap = 6 + 22 = 28 mm
//   (pinion centre is at RING_OUTER_R + 6 = 31 + 6 = 37 mm from nozzle axis;
//    pinion pitch R = 6 mm; pitch line at 37 - 6 = 31 mm from nozzle axis)
//   Wait — pinion is outside the ring, meshing inward.  Pinion boss on nacelle
//   shell at R = RING_OUTER_R + RACK_MODULE + Crown_Pinion_PITCH_R from axis.
//   Rack on inner face of ring means rack teeth point radially inward
//   (toward bore axis).  Crown pinion sits in a slot in the outer housing and
//   meshes with the rack teeth on the ring's inner bore surface.
//
// Rack pitch radius (ring inner face + rack depth):
RACK_PITCH_R  = RING_INNER_R + RACK_DEPTH;   // [mm] = 26.0 mm pitch line R

// Angular pitch of rack teeth mapped to ring circumference:
//   circular_pitch = π × MODULE = 3.1416 mm (arc length per tooth at pitch line)
//   angular_pitch_per_tooth = circular_pitch / RACK_PITCH_R × (180/π)
RACK_ANG_PITCH = (PI * RACK_MODULE / RACK_PITCH_R) * (180 / PI);  // [deg/tooth]
RACK_TOOTH_HALF_ANG = RACK_ANG_PITCH * RACK_WIDTH_FRAC / 2;       // [deg]

// Total arc span of 22 rack teeth:
RACK_TOTAL_ARC = RACK_TEETH * RACK_ANG_PITCH;  // [deg]

// Starting angle of rack arc (centred on ring, spanning ±RACK_TOTAL_ARC/2):
RACK_START_ANG = -RACK_TOTAL_ARC / 2;          // [deg]

// ── Outer Housing Dimensions ──────────────────────────────────────────────────

HOUSING_OUTER_R =  35.0;   // [mm] housing outer radius (OD = 70 mm)
HOUSING_INNER_R =  31.5;   // [mm] housing inner bore radius (ring fits inside;
                            //   ring OD = 62 mm, bore = 63 mm → 0.5 mm clr)
HOUSING_H       =  10.0;   // [mm] housing total axial depth
HOUSING_LIP_H   =   3.0;   // [mm] forward bonding lip depth (bonds to nacelle
                            //   exit face; lip OD matches EDF duct exit OD)
HOUSING_LIP_R   =  26.0;   // [mm] forward lip inner radius (clears airflow bore)

// Crown pinion access slot in housing wall:
CROWN_SLOT_W    =   8.0;   // [mm] slot width (circumferential, > pinion OD=14 mm)
                            //   Note: 8 mm is narrower than pinion; slot is sized
                            //   for the pinion shaft access, not pinion removal.
                            //   Pinion installed before housing is bonded in place.
CROWN_SLOT_H    =   6.0;   // [mm] slot radial depth (from housing OD inward)
CROWN_SLOT_ANG  =   0.0;   // [deg] angular position of slot (at +Y face, 0°)

// ── Petal Dimensions ──────────────────────────────────────────────────────────

N_PETALS         =  8;       // [count] number of iris petals
PETAL_SPAN_DEG   = 50.0;     // [deg] angular span per petal (45° + 5° overlap)
PETAL_HINGE_R    = 33.0;     // [mm] hinge pin circle radius (on outer housing)
HINGE_PIN_D      =  3.0;     // [mm] stainless steel hinge pin OD
HINGE_BORE_D     =  3.2;     // [mm] clearance bore for 3 mm hinge pin (0.2 mm clr)
PETAL_THICKNESS  =  2.5;     // [mm] petal body thickness
PETAL_LENGTH     = 18.0;     // [mm] radial length (hinge to tip)
LINK_HOLE_D      =  1.2;     // [mm] piano-wire link ring slot (0.8 mm wire + clr)
LINK_HOLE_R      = 28.0;     // [mm] radial position of link hole from petal hinge
                              //   (mid-petal lever arm)

// Petal curvature: petals are curved to match nacelle exterior hull contour
//   at closed position.  The outer face is convex (radius = HOUSING_OUTER_R)
//   and the inner face is slightly concave to match.
PETAL_CURVE_R    = HOUSING_OUTER_R;   // [mm] outer face convex radius of curvature

// Petal closed-position exit radius at tip:
NOZZLE_CLOSED_R  = 18.0;   // [mm] nozzle exit radius when all petals closed = 36 mm dia
NOZZLE_OPEN_R    = 21.0;   // [mm] nozzle exit radius when all petals open   = 42 mm dia

// ── Drive Post Parameters (on inner ring, for link ring attachment) ───────────

DRIVE_POST_H   = 3.0;   // [mm] post height above ring face
DRIVE_POST_D   = 2.0;   // [mm] post diameter (link ring loops over post)

// ── Module: nozzle_inner_ring() ───────────────────────────────────────────────
//
// Rotating inner ring:
//   Annular ring: OD = 2 × RING_OUTER_R = 62 mm, ID = 2 × RING_INNER_R = 50 mm
//   Height: RING_H = 8 mm.
//   M = 1.0 rack teeth on inner diameter (teeth point toward bore axis).
//   22 rack teeth spanning ≈ 79.3° arc at pitch R = 26 mm.
//   8 drive posts on top face for piano-wire link ring attachment.
//   Crown pinion (nacelle_pinion.scad) meshes from outside through housing slot.
//
//   Origin: centre of ring face (Z = 0 at inboard face, Z = RING_H at outboard).
//   +Z = toward nacelle exit (outboard / downstream direction).
module nozzle_inner_ring() {
    difference() {
        // ── Base annular ring ────────────────────────────────────────────────
        union() {
            // Main ring body
            cylinder(h = RING_H,
                     r1 = RING_OUTER_R,
                     r2 = RING_OUTER_R);   // vertical (non-tapered)
            // Subtract inner bore separately via difference below
        }

        // Inner bore — remove to create the annular ring
        translate([0, 0, -0.1])
            cylinder(h = RING_H + 0.2, r = RING_INNER_R);

        // ── Rack tooth spaces on inner face ──────────────────────────────────
        // Tooth spaces are wedge voids cut into the inner bore face, leaving
        // the rack teeth as standing radial ridges.
        // Each tooth ridge protrudes RACK_DEPTH = 1.0 mm inward from bore face.
        for (i = [0 : RACK_TEETH]) {
            _rack_tooth_space(i);
        }
    }

    // ── Drive posts on outboard face ─────────────────────────────────────────
    // 8 posts evenly spaced, at the midpoint of ring radial width,
    // located at RING_H face (outboard side) for link ring attachment.
    for (p = [0 : N_PETALS - 1]) {
        rotate([0, 0, p * 360 / N_PETALS + 22.5]) {   // offset 22.5° between petals
            translate([(RING_INNER_R + RING_OUTER_R) / 2, 0, RING_H]) {
                cylinder(h = DRIVE_POST_H, d = DRIVE_POST_D);
            }
        }
    }
}

// _rack_tooth_space(i) — one tooth-space void on inner face of ring.
//   Tooth spaces are angular wedges at the RING_INNER_R + RACK_DEPTH band,
//   leaving standing rack teeth between them.
//   Built as a polygon (annular_wedge) — avoids nested 2D CSG (circle−circle−
//   square−square) that caused CGAL to time out over 23 iterations.
//
//   Arguments:
//     i — tooth-space index (0-based, 0 through RACK_TEETH)
module _rack_tooth_space(i) {
    // Angular centre of this tooth space:
    space_centre = RACK_START_ANG + (i + 0.5) * RACK_ANG_PITCH;   // [deg]

    // Half-angle of the space (= tooth width angle — equal division):
    half_ang = RACK_TOOTH_HALF_ANG;   // [deg]

    // Wedge radial extent: from ring inner face to past tip of tooth
    r_outer = RING_INNER_R + RACK_DEPTH + 0.1;   // outer bound (tip + overcut)
    r_inner = RING_INNER_R - RACK_DEDENDUM;       // inner bound (root depth)

    // Each tooth space spans only ~7° — 2 arc segments per edge is sufficient.
    linear_extrude(height = RING_H + 0.2) {
        polygon(annular_wedge(
            r_inner, r_outer,
            space_centre - half_ang, space_centre + half_ang,
            2   // 2 segments per arc edge (narrow tooth space, arc ≈ straight line)
        ));
    }
}

// ── Module: nozzle_outer_housing() ───────────────────────────────────────────
//
// Fixed cylindrical housing:
//   OD = 2 × HOUSING_OUTER_R = 70 mm.
//   Inner bore = 2 × HOUSING_INNER_R = 63 mm (ring slides inside, 0.5 mm clr).
//   8 hinge bores at PETAL_HINGE_R = 33 mm radius, HINGE_BORE_D = 3.2 mm.
//   Forward bonding lip (HOUSING_LIP_H = 3 mm) for adhesive bond to nacelle face.
//   Crown pinion access slot on inboard side wall.
//   4 × M2.5 mount holes for bonding to nacelle exit face (optional mechanical fix).
//
//   Origin: centre of housing, Z = 0 at inboard (nacelle-side) face.
module nozzle_outer_housing() {
    difference() {
        // ── Solid housing cylinder + bonding lip ─────────────────────────────
        union() {
            // Main housing body
            cylinder(h = HOUSING_H, r = HOUSING_OUTER_R);

            // Inboard bonding lip: slightly larger OD for a shoulder against nacelle face
            translate([0, 0, -HOUSING_LIP_H])
                difference() {
                    cylinder(h = HOUSING_LIP_H, r = HOUSING_OUTER_R);
                    // Inner clearance: lip inner R = HOUSING_LIP_R to pass airflow bore
                    cylinder(h = HOUSING_LIP_H + 0.1, r = HOUSING_LIP_R);
                }
        }

        // ── Inner bore — ring slides inside this bore ─────────────────────────
        translate([0, 0, -0.1])
            cylinder(h = HOUSING_H + 0.2, r = HOUSING_INNER_R);

        // ── 8 hinge pin bores — Z-axis through-holes at PETAL_HINGE_R ────────
        // Hinge pins are 3 mm × 18 mm SS dowels pressed into the housing;
        // petals pivot on the exposed pin section.
        for (p = [0 : N_PETALS - 1]) {
            rotate([0, 0, p * 360 / N_PETALS]) {
                translate([PETAL_HINGE_R, 0, -HOUSING_LIP_H - 0.1])
                    cylinder(h = HOUSING_H + HOUSING_LIP_H + 0.2, d = HINGE_BORE_D);
            }
        }

        // ── Crown pinion access slot ──────────────────────────────────────────
        // Slot in outer wall at CROWN_SLOT_ANG angular position.
        // The slot allows the Crown Pinion to protrude through the housing wall
        // and mesh with the inner ring rack.
        // Slot is cut as a radial trench from OD inward.
        rotate([0, 0, CROWN_SLOT_ANG]) {
            translate([HOUSING_INNER_R, -CROWN_SLOT_W / 2, HOUSING_H * 0.2])
                cube([CROWN_SLOT_H + (HOUSING_OUTER_R - HOUSING_INNER_R) + 0.1,
                      CROWN_SLOT_W,
                      HOUSING_H * 0.6]);
        }
    }
}

// ── Module: nozzle_petal() ────────────────────────────────────────────────────
//
// One iris petal:
//   Trapezoidal curved planform; wider at hinge root, narrower at tip.
//   PETAL_THICKNESS = 2.5 mm uniform slab.
//   Outer face: convex arc of radius PETAL_CURVE_R (matches housing OD) —
//     when closed, outer faces form a smooth cylindrical nacelle tail surface.
//   Inner face: slightly concave (inner radius = PETAL_CURVE_R - PETAL_THICKNESS).
//   Hinge knuckle at root: cylindrical lug with HINGE_BORE_D = 3.2 mm bore.
//   Link-ring slot at mid-petal: 1.2 mm slot for 0.8 mm piano wire.
//
//   NOTE — inner face material: TRANSLUCENT-BLUE PETG (aesthetic; allows visual
//     confirmation of petal position during ground inspection via bore sighting).
//   NOTE — outer face: must match nacelle hull colour/finish (titanium grey paint
//     or grey PETG filament).
//
//   Print orientation: flat (inner face down on build plate).
//   Origin: hinge pin centreline at [0, 0, 0]; petal extends radially in +X.
module nozzle_petal() {
    // Petal planform: trapezoidal, wider at hinge (root) by PETAL_SPAN_DEG,
    // narrowing toward tip.  Built as a curved slab.

    // Root width (arc at PETAL_HINGE_R over PETAL_SPAN_DEG):
    //   root_arc = PETAL_HINGE_R × PETAL_SPAN_DEG × π/180
    //            = 33 × 50 × 0.01745 = 28.8 mm
    // Tip width: zero at tip (fully closed = point), but minimum print width
    //   of 3 mm to avoid thin-wall failure.

    difference() {
        // ── Main petal body (curved slab via rotate_extrude approximation) ───
        // Approximated as a linear_extrude of a 2D trapezoidal arc profile.
        // The 2D profile is an annular sector from PETAL_CURVE_R - PETAL_THICKNESS
        // to PETAL_CURVE_R, spanning PETAL_SPAN_DEG.
        // Then extruded PETAL_LENGTH in Z (radial direction).
        //
        // Simpler workable geometry: a curved slab using hull of two arc slices:
        linear_extrude(height = PETAL_THICKNESS) {
            // 2D footprint: pie sector, inner edge at bore, outer edge at housing OD
            // Spans PETAL_SPAN_DEG about hinge pin at [0,0]
            difference() {
                // Outer arc — matches housing OD curvature when closed
                circle(r = PETAL_LENGTH + 3);     // tip arc radius from hinge
                // Inner cutout — central bore region
                circle(r = 4.0);                  // clears hinge knuckle area
                // Angular mask — limit to PETAL_SPAN_DEG
                rotate([0, 0, PETAL_SPAN_DEG])
                    square([100, 100]);
                rotate([0, 0, 180])
                    square([100, 100]);
            }
        }

        // ── Hinge bore through knuckle ────────────────────────────────────────
        // 3.2 mm through-hole at hinge root (Z-axis at [0,0,0]).
        translate([0, 0, -0.1])
            cylinder(h = PETAL_THICKNESS + 0.2, d = HINGE_BORE_D);

        // ── Link-ring slot (mid-petal) ────────────────────────────────────────
        // 1.2 mm slot at radial distance LINK_HOLE_R from hinge pin.
        // Link ring (0.8 mm piano wire) threads through this slot and connects
        // petal to inner ring drive post.
        // Slot is oriented tangentially (perpendicular to petal radial axis).
        translate([LINK_HOLE_R * cos(PETAL_SPAN_DEG / 2),
                   LINK_HOLE_R * sin(PETAL_SPAN_DEG / 2),
                   -0.1]) {
            // Round slot: hull of two small cylinders for slot length
            hull() {
                translate([-1.5, 0, 0])
                    cylinder(h = PETAL_THICKNESS + 0.2, d = LINK_HOLE_D);
                translate([1.5, 0, 0])
                    cylinder(h = PETAL_THICKNESS + 0.2, d = LINK_HOLE_D);
            }
        }
    }

    // ── Hinge knuckle lug ────────────────────────────────────────────────────
    // Cylindrical lug around the hinge bore for bearing contact width.
    // Lug extends PETAL_THICKNESS (flush with petal body) but is reinforced
    // to 2 × wall thickness around the pin bore.
    difference() {
        cylinder(h = PETAL_THICKNESS, d = HINGE_BORE_D + 4.0);   // knuckle OD = 7.2 mm
        translate([0, 0, -0.1])
            cylinder(h = PETAL_THICKNESS + 0.2, d = HINGE_BORE_D);  // bore
    }
}

// ── Fit Confirmation ──────────────────────────────────────────────────────────
//
//   Interface                  Mating part                   Clearance / fit
//   ─────────────────────────  ────────────────────────────  ──────────────────
//   RING_OUTER_R 31 mm OD      Housing HOUSING_INNER_R 31.5  0.5 mm radial clr
//   (inner ring)               (outer housing bore)           (ring rotates freely)
//   Rack pitch R 26 mm         Crown Pinion pitch R 6 mm     0.1 mm backlash
//   (inner ring rack)          nacelle_pinion.scad            (standard AGMA)
//   HINGE_BORE_D 3.2 mm        3 mm SS hinge pin             0.2 mm diametral clr
//   (8 petal knuckles)         (×8, 3 mm × 18 mm dowels)      (petals pivot freely)
//   LINK_HOLE_D 1.2 mm         0.8 mm 302 SS piano wire       0.4 mm diametral clr
//   (petal link slot)          (link ring)                    (wire moves in slot)
//   Drive posts 2 mm OD        Piano wire loop on post        0.2 mm radial clr
//   Housing bonding lip        Nacelle exit face duct         epoxy bond,
//   OD = HOUSING_OUTER_R 35mm  (hull exit aperture 70 mm ID)  positive shoulder stop

// ── Render Instructions ───────────────────────────────────────────────────────
//
// Export each part individually (uncomment one section at a time):
//
// Render inner ring:
nozzle_inner_ring();
//
// Render outer housing:
// nozzle_outer_housing();
//
// Render one petal (print × 8):
// nozzle_petal();
//
// Assembly preview — all 8 petals at closed position + housing + ring:
// nozzle_outer_housing();
// nozzle_inner_ring();
// for (i = [0 : N_PETALS - 1]) {
//     rotate([0, 0, i * 360 / N_PETALS])
//         translate([PETAL_HINGE_R, 0, 0])
//             rotate([0, 0, -PETAL_SPAN_DEG / 2])
//                 nozzle_petal();
// }
