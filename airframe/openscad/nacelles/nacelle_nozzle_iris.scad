// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  Primary-component STLs published to airframe/stls/
//   are stored directly in hull frame, baked by tools/bake_hull_frame.py
//   (marker 'SerenityUAV HULL-FRAME R1' in the binary STL header).
//   NEVER re-bake a mesh derived from an already-baked file.
//   This file:
//     Part-local print frame, coaxial with the nacelle duct (duct axis =
//     local +Z, intake at Z = 0).  Hull placement derives from the nacelle
//     pose (cruise = 270 deg about +X + translation; hover rotates about the
//     tilt pivot at duct Z = 83 mm).  Assembly placement VERIFY pending
//     (serenity_assembly.py).
// ===========================================================================
// nacelle_nozzle_iris.scad
// Serenity UAV Rev R1 — Nacelle Iris Nozzle Assembly (50 mm EDF bore)
//
// Purpose:
//   Complete iris nozzle assembly for one nacelle, driven by the nacelle tilt
//   gear train through a Crown-Pinion-to-Ring idler gear
//   (nacelle_nozzle_idler.scad, added Rev R1 2026-06-22).  As the nacelle
//   tilts, the rotating inner ring (now a full-circle external spur gear,
//   not a partial rack) pulls/pushes eight pivot-hinged petals via a
//   piano-wire link ring, changing the nozzle exit radius.
//
//   Bore-percentage spec (Rev R1, 2026-06-22):
//     0°  tilt (cruise reference)  -> NOZZLE_CLOSED_R = 18.75 mm (75 % of the
//         25 mm EDF bore radius)
//     90° tilt (hover reference)   -> NOZZLE_OPEN_R   = 26.25 mm (105 % of
//         the 25 mm EDF bore radius)
//   Mechanical range is -5° to 140° (hard stops); the petal lever geometry
//   below is sized so this full range stays within the housing envelope
//   without binding — see "Ring rotation / petal swing" below.
//
//   Three separately-printable parts, each in its own module:
//     1. nozzle_inner_ring()    — rotating ring; full-circle M=1.0 spur gear
//        on its outer rim (meshes the idler, not the Crown Pinion directly)
//     2. nozzle_outer_housing() — fixed cylindrical housing with petal hinge
//        bores and an idler-access slot
//     3. nozzle_petal()         — one iris petal (print × 8)
//
// Gear/idler interface (Rev R1 — supersedes the direct Crown-Pinion-to-rack
// mesh that was the unresolved item in TODO.md §1.1.3.3):
//   The Crown Pinion (R = 6 mm, nacelle_pinion.scad) no longer meshes this
//   ring directly.  Its fixed 28 mm hull-frame offset from the nozzle axis
//   made a direct mesh force the ring pitch radius to ≈ 22 mm — too small to
//   carry the petal hinge circle this bore-percentage spec needs, and the
//   resulting ring rotation (driven by Stage 1's ×4.667 epicyclic
//   amplification) was far more than the petal lever could usefully absorb.
//   A compound idler gear (nacelle_nozzle_idler.scad) now sits between the
//   Crown Pinion and this ring:
//     Idler-In  (R = 22.0 mm) meshes Crown Pinion (R = 6 mm)
//     Idler-Out (R =  7.5 mm) meshes this ring's gear   (R = 36.0 mm)
//   giving omega_ring / omega_crownPinion = (6/22) x (7.5/36) = 0.056818,
//   so theta_ring = theta_nacelleTilt x 4.667 x 0.056818 = theta_nacelleTilt
//   x 0.26515.  See nacelle_nozzle_idler.scad for the full derivation and the
//   idler-position triangle-inequality check.
//
// Ring rotation / petal swing (law of cosines, hinge fixed, petal rigid):
//   tip_radius^2 = PETAL_HINGE_R^2 + PETAL_LENGTH^2
//                  - 2 x PETAL_HINGE_R x PETAL_LENGTH x cos(phi)
//   where phi is the petal swing angle from the fully-folded (phi = 0)
//   position.  With PETAL_HINGE_R = 38.75 mm and PETAL_LENGTH = 20.0 mm:
//     phi = 0°     -> tip_radius = 18.75 mm  (= NOZZLE_CLOSED_R, exact)
//     phi = 38.78° -> tip_radius = 26.33 mm  (≈ NOZZLE_OPEN_R, within 0.1 mm)
//   Ring-to-petal lever (piano-wire link ring, arc-length approximation):
//     Delta_phi = Delta_theta_ring x (DRIVE_POST_R / LINK_HOLE_R)
//               = Delta_theta_ring x (26.0 / 16.0)
//   Reference points (nacelle tilt -> theta_ring -> phi -> tip_radius):
//     0°    -> theta_ring   0.00° -> phi   0.00° -> tip 18.75 mm (closed)
//     90°   -> theta_ring  23.86° -> phi  38.78° -> tip 26.33 mm (open, spec)
//     -5°   -> theta_ring  -1.33° -> phi  -2.15° -> tip ≈ 18.76 mm (lower stop;
//             phi crosses the tip_radius(phi) cusp at phi=0, so this is the
//             true minimum, not a reversal — see nacelle_nozzle_idler.scad)
//     140°  -> theta_ring  38.45° -> phi  62.48° -> tip 34.42 mm (upper stop;
//             3.1 mm clear of HOUSING_INNER_R = 37.5 mm)
//   All four points are within the housing envelope with positive margin —
//   the full -5°/140° hard-stop range does not bind.
//
// Mating interfaces:
//   • Idler-Out gear (nacelle_nozzle_idler.scad): module M = 1.0, meshes this
//       ring's 72-tooth gear at pitch R = 36 mm, through IDLER_SLOT in the
//       outer housing wall.
//   • Nacelle exit face (hull): housing lip bonds to EDF exit duct face.
//   • Hinge pins: 3 mm × 18 mm stainless steel dowel pins (×8).
//   • Link ring: 0.8 mm 302 SS piano wire, formed into ring linking all petals.
//
// Print specification — Inner Ring:
//   Material:    CF-PETG (ring gear teeth carry mesh load)
//   Layers:      0.15 mm, 4 perimeters, 40 % gyroid infill
//   Orient:      Print flat (ring face down) for gear tooth quality
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
// Rev:     R (2026-06-11): Rev R baseline — no geometry changes (carried forward from Rev O initial release).
// Rev:     R1 (2026-06-22): Resolved TODO.md §1.1.3.3 Crown-Pinion-to-rack
//          radius inconsistency by adding an idler gear
//          (nacelle_nozzle_idler.scad) between the Crown Pinion and this
//          ring.  Replaced the partial inner-face rack (RACK_TEETH = 22,
//          RACK_PITCH_R = 26 mm) with a full-circle external spur gear on
//          the ring's outer rim (72 T, R = 36 mm) meshed by the idler —
//          removes the rack-arc-length/radius inconsistency entirely since
//          a full-circle gear has no arc-coverage limit.  Updated bore
//          targets from 36/42 mm dia (72 %/84 % of 50 mm bore) to the new
//          75 %/105 % spec (NOZZLE_CLOSED_R 18.0 -> 18.75 mm, NOZZLE_OPEN_R
//          21.0 -> 26.25 mm).  Grew PETAL_HINGE_R (33 -> 38.75 mm) and
//          PETAL_LENGTH (18.0 -> 20.0 mm) so the petal lever law of cosines
//          reaches both targets; fixed a pre-existing bug where
//          LINK_HOLE_R (28 mm) exceeded PETAL_LENGTH (18 mm) — now
//          LINK_HOLE_R = 16.0 mm, inside the 20 mm petal.  Moved the ring
//          drive posts from the ring's mid-annulus to its inner lip
//          (DRIVE_POST_R = RING_INNER_R = 26 mm) to get the lever ratio the
//          new ring-rotation figures need.  Housing grown proportionally
//          (HOUSING_INNER_R 31.5 -> 37.5 mm, HOUSING_OUTER_R 35 -> 41 mm,
//          same 3.5 mm wall).  Renamed the Crown-Pinion access slot to the
//          idler-access slot (CROWN_SLOT_* -> IDLER_SLOT_*).

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
//   Using polygon() for ring-gear tooth spaces avoids nested 2D CSG
//   (circle−circle−square²) which causes CGAL exponential blowup above
//   ~20 iterations (see nacelle_sector_gear.scad); the ring gear has 72.
//   n = arc-segment count per edge; inner/outer arcs wound for correct face normal.
//
function annular_wedge(r_in, r_out, a1, a2, n) =
    concat(arc_pts(r_in,  a1, a2, n),
            arc_pts(r_out, a2, a1, n));

// ── Nozzle Bore and Ring Dimensions ───────────────────────────────────────────

BORE_R        = 25.0;   // [mm] 50 mm EDF bore radius (airflow passage centre) —
                        //   fixed by the 50 mm EDF spec (CLAUDE.md); unchanged.
RING_INNER_R  = 26.0;   // [mm] inner radius of rotating ring (1 mm clearance
                        //   over the bore so the ring lip never restricts flow)
RING_GEAR_PITCH_R = 36.0;   // [mm] pitch radius of the full-circle gear cut into
                        //   the ring's outer rim (meshes Idler-Out, R = 7.5 mm,
                        //   nacelle_nozzle_idler.scad)
RING_H        =  8.0;   // [mm] axial height (depth) of rotating ring — matches
                        //   GEAR_H_OUT in nacelle_nozzle_idler.scad

// ── Ring Gear Parameters (M=1.0, full-circle, on outer rim) ───────────────────
//
// Rev R1: replaces the Rev R partial inner-face rack (RACK_TEETH = 22 over a
// fixed arc) with a full-circle external spur gear.  A full circle has no
// arc-coverage limit, so it accommodates the entire -5°/140° mechanical
// range (38.45° of ring rotation, see header) without any rack-length sizing
// exercise — this was the structural source of the original inconsistency
// (a finite rack arc sized for one ratio, at a radius forced by a different
// constraint).  Standard AGMA tooth proportions, same method as
// nacelle_sector_gear.scad and nacelle_pinion.scad.

RING_GEAR_MODULE = 1.0;    // [mm] Module — matches Idler-Out and Crown Pinion
RING_GEAR_ADDENDUM = RING_GEAR_MODULE;          // [mm] = 1.0
RING_GEAR_DEDENDUM = 1.25 * RING_GEAR_MODULE;   // [mm] = 1.25
RING_OUTER_R  = RING_GEAR_PITCH_R + RING_GEAR_ADDENDUM;  // [mm] = 37.0 (tip)
RING_GEAR_ROOT_R = RING_GEAR_PITCH_R - RING_GEAR_DEDENDUM; // [mm] = 34.75

N_RING_TEETH = round(2 * RING_GEAR_PITCH_R / RING_GEAR_MODULE);  // [count] = 72
RING_GEAR_ANGULAR_PITCH = 360.0 / N_RING_TEETH;   // [deg] = 5.0° per tooth

// ── Outer Housing Dimensions ──────────────────────────────────────────────────

HOUSING_OUTER_R =  41.0;   // [mm] housing outer radius (OD = 82 mm); same 3.5 mm
                            //   wall thickness as the Rev R baseline, scaled to
                            //   the larger ring
HOUSING_INNER_R =  37.5;   // [mm] housing inner bore radius (ring fits inside;
                            //   ring OD = 74 mm, bore = 75 mm → 0.5 mm clr)
HOUSING_H       =  10.0;   // [mm] housing total axial depth
HOUSING_LIP_H   =   3.0;   // [mm] forward bonding lip depth (bonds to nacelle
                            //   exit face; lip OD matches EDF duct exit OD)
HOUSING_LIP_R   =  26.0;   // [mm] forward lip inner radius (clears airflow bore;
                            //   matches RING_INNER_R)

// Idler-access slot in housing wall (Rev R1: renamed from CROWN_SLOT_* — the
// Crown Pinion no longer reaches this ring directly; the idler's Idler-Out
// gear section protrudes through this slot to mesh the ring gear):
IDLER_SLOT_W    =  10.0;   // [mm] slot width (circumferential; > Idler-Out tip
                            //   OD = 17 mm is NOT required — slot is sized for
                            //   shaft/tooth access during assembly, not gear
                            //   removal.  Idler installed before housing bonded.)
IDLER_SLOT_H    =   6.0;   // [mm] slot radial depth, added to wall thickness
                            //   (matches Rev R CROWN_SLOT_H convention)
IDLER_SLOT_ANG  =  50.9;   // [deg] angular position of slot, measured from this
                            //   part's local +X axis (TODO.md §1.1.3.3, resolved
                            //   2026-06-22).  Solved from the two simultaneous
                            //   centre-distance constraints in
                            //   nacelle_nozzle_idler.scad — Crown Pinion sits at
                            //   local (X=0, Y=28) (PINION_A_Y, nacelle_pod_50mm_
                            //   tandem.scad), and the idler shaft must be 28.1 mm
                            //   from that point AND 43.6 mm from this ring's axis
                            //   (0,0).  Solving the two circle equations gives
                            //   shaft position (X=+27.485, Y=33.846), i.e. 50.92°
                            //   from +X (rounded to 50.9°).  This is one of the
                            //   two valid mirror-image solutions (the other is
                            //   129.08° at X=-27.485); +X was chosen arbitrarily
                            //   — no other component occupies this angular sector
                            //   at this Z station.  NOTE: the idler's AXIAL (Z)
                            //   placement is a separate, still-open question — see
                            //   TODO.md §1.1.3.3 "idler axial mesh-band mismatch".

// ── Petal Dimensions ──────────────────────────────────────────────────────────

N_PETALS         =  8;       // [count] number of iris petals
PETAL_SPAN_DEG   = 50.0;     // [deg] angular span per petal (45° + 5° overlap)
PETAL_HINGE_R    = 38.75;    // [mm] hinge pin circle radius (on outer housing) —
                                //   chosen so PETAL_HINGE_R - PETAL_LENGTH =
                                //   NOZZLE_CLOSED_R exactly at phi = 0 (see header)
HINGE_PIN_D      =  3.0;     // [mm] stainless steel hinge pin OD
HINGE_BORE_D     =  3.2;     // [mm] clearance bore for 3 mm hinge pin (0.2 mm clr)
PETAL_THICKNESS  =  2.5;     // [mm] petal body thickness
PETAL_LENGTH     = 20.0;     // [mm] radial length (hinge to tip)
LINK_HOLE_D      =  1.2;     // [mm] piano-wire link ring slot (0.8 mm wire + clr)
LINK_HOLE_R      = 16.0;     // [mm] radial position of link hole from petal hinge
                                //   (Rev R1: corrected from 28 mm, which exceeded
                                //   PETAL_LENGTH = 18 mm and put the hole off the
                                //   physical petal — see TODO.md §1.1.3. 16 mm is
                                //   80 % of the new 20 mm PETAL_LENGTH, leaving a
                                //   4 mm solid tip past the hole.)

// Petal curvature: petals are curved to match nacelle exterior hull contour
// at closed position.  The outer face is convex (radius = HOUSING_OUTER_R)
// and the inner face is slightly concave to match.
PETAL_CURVE_R    = HOUSING_OUTER_R;   // [mm] outer face convex radius of curvature

// Petal closed/open exit radius at tip (Rev R1 bore-percentage spec, 75 %/105 %
// of the 25 mm EDF bore radius — replaces the Rev R 36/42 mm diameter targets):
NOZZLE_CLOSED_R  = 18.75;   // [mm] nozzle exit radius at 0° tilt  = 75 % of BORE_R
NOZZLE_OPEN_R    = 26.25;   // [mm] nozzle exit radius at 90° tilt = 105 % of BORE_R

// ── Drive Post Parameters (on inner ring, for link ring attachment) ───────────

DRIVE_POST_H   = 3.0;    // [mm] post height above ring face
DRIVE_POST_D   = 2.0;    // [mm] post diameter (link ring loops over post)
DRIVE_POST_R   = RING_INNER_R;   // [mm] = 26.0  radial position of drive posts.
                        //   Rev R1: moved from the ring's mid-annulus
                        //   ((RING_INNER_R+RING_OUTER_R)/2) to the inner lip
                        //   so the post/link-hole lever ratio (26/16 = 1.625)
                        //   matches the ring-rotation figures in the header
                        //   without exceeding LINK_HOLE_R ≤ PETAL_LENGTH.

// ── Module: nozzle_inner_ring() ───────────────────────────────────────────────
//
// Rotating inner ring:
//   Annular ring: OD = 2 × RING_OUTER_R = 74 mm, ID = 2 × RING_INNER_R = 52 mm
//   Height: RING_H = 8 mm.
//   M = 1.0 full-circle gear on outer rim (72 teeth at pitch R = 36 mm) —
//   meshed by Idler-Out (nacelle_nozzle_idler.scad) through the housing's
//   IDLER_SLOT, not by the Crown Pinion directly (Rev R1 change).
//   8 drive posts on top face for piano-wire link ring attachment, at
//   DRIVE_POST_R = RING_INNER_R (ring's inner lip).
//
//   Origin: centre of ring face (Z = 0 at inboard face, Z = RING_H at outboard).
//   +Z = toward nacelle exit (outboard / downstream direction).
module nozzle_inner_ring() {
    difference() {
        // ── Base ring body (gear blank, tip radius OD) ──────────────────────
        cylinder(h = RING_H, r = RING_OUTER_R);

        // Inner bore — remove to create the annular ring
        translate([0, 0, -0.1])
            cylinder(h = RING_H + 0.2, r = RING_INNER_R);

        // ── Ring gear tooth spaces, full circle ──────────────────────────────
        for (i = [0 : N_RING_TEETH - 1]) {
            _ring_gear_tooth_space(i);
        }
    }

    // ── Drive posts on outboard face ─────────────────────────────────────────
    // 8 posts evenly spaced, at DRIVE_POST_R (ring's inner lip),
    // located at RING_H face (outboard side) for link ring attachment.
    for (p = [0 : N_PETALS - 1]) {
        rotate([0, 0, p * 360 / N_PETALS + 22.5]) {   // offset 22.5° between petals
            translate([DRIVE_POST_R, 0, RING_H]) {
                cylinder(h = DRIVE_POST_H, d = DRIVE_POST_D);
            }
        }
    }
}

// _ring_gear_tooth_space(i) — one tooth-space void on the ring's outer rim.
//   Standard external spur gear tooth-space subtraction, full circle.
//   Built as a polygon (annular_wedge) — avoids nested 2D CSG that caused
//   CGAL to time out at high tooth counts (see header).
//
//   Arguments:
//     i — tooth-space index (0-based, 0 through N_RING_TEETH - 1)
module _ring_gear_tooth_space(i) {
    space_centre = i * RING_GEAR_ANGULAR_PITCH + RING_GEAR_ANGULAR_PITCH / 2;
    half_ang     = RING_GEAR_ANGULAR_PITCH / 4;   // quarter pitch = half tooth space

    linear_extrude(height = RING_H + 0.2) {
        polygon(annular_wedge(
            RING_GEAR_ROOT_R - 0.1, RING_OUTER_R + 0.1,
            space_centre - half_ang, space_centre + half_ang,
            2   // 2 segments per arc edge (5° pitch — arc ≈ straight line)
        ));
    }
}

// ── Module: nozzle_outer_housing() ───────────────────────────────────────────
//
// Fixed cylindrical housing:
//   OD = 2 × HOUSING_OUTER_R = 82 mm.
//   Inner bore = 2 × HOUSING_INNER_R = 75 mm (ring slides inside, 0.5 mm clr).
//   8 hinge bores at PETAL_HINGE_R = 38.75 mm radius, HINGE_BORE_D = 3.2 mm.
//   Forward bonding lip (HOUSING_LIP_H = 3 mm) for adhesive bond to nacelle face.
//   Idler-access slot on inboard side wall (Rev R1: was Crown Pinion slot).
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

        // ── Idler-access slot ──────────────────────────────────────────────────
        // Slot in outer wall at IDLER_SLOT_ANG angular position.
        // The slot allows the Idler-Out gear section (nacelle_nozzle_idler.scad)
        // to protrude through the housing wall and mesh with the ring gear.
        // Slot is cut as a radial trench from OD inward.
        rotate([0, 0, IDLER_SLOT_ANG]) {
            translate([HOUSING_INNER_R, -IDLER_SLOT_W / 2, HOUSING_H * 0.2])
                cube([IDLER_SLOT_H + (HOUSING_OUTER_R - HOUSING_INNER_R) + 0.1,
                        IDLER_SLOT_W,
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
//   Link-ring slot at mid-petal: 1.2 mm slot for 0.8 mm piano wire, at
//     LINK_HOLE_R = 16 mm from the hinge (inside the 20 mm petal length).
//
//   NOTE — inner face material: TRANSLUCENT-BLUE PETG (aesthetic; allows visual
//     confirmation of petal position during ground inspection via bore sighting).
//   NOTE — outer face: must match nacelle hull colour/finish (titanium grey
//     paint or grey PETG filament).
//
//   Print orientation: flat (inner face down on build plate).
//   Origin: hinge pin centreline at [0, 0, 0]; petal extends radially in +X.
module nozzle_petal() {
    // Petal planform: trapezoidal, wider at hinge (root) by PETAL_SPAN_DEG,
    // narrowing toward tip.  Built as a curved slab.

    // Root width (arc at PETAL_HINGE_R over PETAL_SPAN_DEG):
    //   root_arc = PETAL_HINGE_R × PETAL_SPAN_DEG × π/180
    //            = 38.75 × 50 × 0.01745 = 33.8 mm
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
//   RING_OUTER_R 37 mm OD      Housing HOUSING_INNER_R 37.5  0.5 mm radial clr
//   (inner ring)               (outer housing bore)           (ring rotates freely)
//   Ring gear pitch R 36 mm    Idler-Out pitch R 7.5 mm      0.1 mm backlash
//   (full-circle, 72 T)        nacelle_nozzle_idler.scad      (centre dist 43.6 mm)
//   HINGE_BORE_D 3.2 mm        3 mm SS hinge pin             0.2 mm diametral clr
//   (8 petal knuckles)         (×8, 3 mm × 18 mm dowels)      (petals pivot freely)
//   LINK_HOLE_D 1.2 mm         0.8 mm 302 SS piano wire       0.4 mm diametral clr
//   (petal link slot)          (link ring)                    (wire moves in slot,
//                                                                LINK_HOLE_R 16 mm
//                                                                ≤ PETAL_LENGTH 20 mm)
//   Drive posts 2 mm OD        Piano wire loop on post        0.2 mm radial clr
//   (DRIVE_POST_R 26 mm)
//   Housing bonding lip        Nacelle exit face duct         epoxy bond,
//   OD = HOUSING_OUTER_R 41mm  (hull exit aperture 82 mm ID)  positive shoulder stop

// ── Render Instructions ───────────────────────────────────────────────────────
//
// Export each part individually (uncomment one section at a time):
//
// Render inner ring:
// nozzle_inner_ring();
//
// Render outer housing:
// nozzle_outer_housing();
//
// Render one petal (print × 8):
// nozzle_petal();
//
// Assembly preview — all 8 petals at closed position + housing + ring.
// This is the DEFAULT render: serenity_assembly.py imports
// nacelle_nozzle_iris.stl as the combined assembly (see its comment at the
// nozzle placement block) for spatial/clearance purposes, not as a
// print-ready single part — the ring/housing/petals are still printed as
// three separate parts pulled from this same file (uncomment one block at
// a time above) or, for the petal, from blender_nozzle_gen.py's
// nacelle_nozzle_petal.stl.
nozzle_outer_housing();
nozzle_inner_ring();
for (i = [0 : N_PETALS - 1]) {
    rotate([0, 0, i * 360 / N_PETALS])
        translate([PETAL_HINGE_R, 0, 0])
            rotate([0, 0, -PETAL_SPAN_DEG / 2])
                nozzle_petal();
}
