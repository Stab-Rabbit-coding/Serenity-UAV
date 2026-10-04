// =============================================================================
// nacelle_tilt_joint_context.scad — 64 mm nacelle tilt joint, in position
// =============================================================================
// Owner request 2026-10-03: "how do these options look in the context of the
// nacelle shell and wing? show them in position."
//
// Assembles, in the starboard nacelle frame (PYLON_SIDE = +1), re-oriented to
// a hull-like view (X span, Y aft, Z up):
//   * the rendered 64 mm pod (POD_STL, nacelle_pod_64mm_tandem.scad output);
//   * the real starboard wing mesh, placed by GEOMETRY rather than by the
//     (self-declared stale) bake: its Ø20.4 spar bore — measured on the mesh
//     at hull (y 21.00, z 64.63) — is put coaxial with the trunnion at
//     PIVOT_Z, and its tip-pad face (mesh min X, -345.18) at the 64 mm
//     station WING_TIP_FACE_X - TIP_PAD_PROUD = 53.84;
//   * the Ø20 CF spar stub to its sleeve-bounded tip (X0 = 35.34);
//   * the trunnion + ring of tip-gear VARIANT (nacelle_tip_gear_variants.scad)
//     and the wing's 14T pinion on the wing's own shaft axis — measured on the
//     mesh at hull (y 46.60, z 66.31), i.e. 25.6 mm aft and 1.7 mm above the
//     spar axis (wings_s1223_revo.scad SHAFT_BORE_STATION = spar + 25.6).
//     Variant B's 32.0 mm centre distance is drawn on the same azimuth: the
//     wing shaft would have to move there.
// CUT = 1 removes the pod and wing above the spar plane to show the mesh.
// CLASH_STL draws a pre-computed interference mesh in red (nacelle-local),
// e.g. from the manifold3d sweep recorded in WBS NAC-64-TILT-03.
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CEH (Stab-Rabbit-coding) —
// request.  Assembly by Claude (Claude Opus 5.5, Anthropic) under the
// author's direction, per AGENTS.md AI attribution.
// License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
// =============================================================================

CUT      = 0;
CLASH_STL = "";   // optional nacelle-local clash mesh, drawn red (see header)
POD_STL  = "nacelle_stbd_64mm.stl";        // pass -D POD_STL="..." to override
WING_STL = "../../stls/wings/wing_stbd_s1223_revo.stl";
include <nacelle_tip_gear_variants.scad>

// Overrides go AFTER the include: OpenSCAD keeps the last assignment.
VARIANT_RENDER = false;   // suppress the variant file's own free-standing copy
VARIANT  = 1;             // -D VARIANT=n on the command line still wins

// Wing mesh measurements (hull frame, mm) — see header.
W_XMIN = -345.18;  W_SPAR_Y = 21.00;  W_SPAR_Z = 64.63;
SHAFT_Y = 46.60;   SHAFT_Z = 66.31;
J_SHAFT_AZ = atan2(SHAFT_Z - W_SPAR_Z, SHAFT_Y - W_SPAR_Y);  // ≈ 3.8 deg up (own name: an
// override of the included SHAFT_AZ would evaluate before W_* exist)

// hull -> nacelle-local: x_l = x_h + dx, y_l = -(z_h - spar_z),
//                        z_l = (y_h - spar_y) + PIVOT_Z
module wing_local() {
    multmatrix([[1, 0,  0, (WING_TIP_FACE_X - PAD_PROUD) - W_XMIN],
                [0, 0, -1, W_SPAR_Z],
                [0, 1,  0, PIVOT_Z_64 - W_SPAR_Y],
                [0, 0,  0, 1]])
        import(WING_STL, convexity = 6);
}
PIVOT_Z_64 = 109.7;   // nacelle_pod_64mm_tandem.scad PIVOT_Z (converged)

// trunnion PART frame -> nacelle-local: part z -> +X, part x -> +Z (aft),
// part y -> -Y; origin at the spar tip on the tilt axis.
module part_to_local() {
    multmatrix([[0,  0, 1, TRUNNION_X0],
                [0, -1, 0, 0],
                [1,  0, 0, PIVOT_Z_64],
                [0,  0, 0, 1]]) children();
}

// nacelle-local -> view frame (X span, Y aft, Z up), centred on the joint.
module view() {
    multmatrix([[1, 0, 0, 0], [0, 0, 1, -PIVOT_Z_64], [0, -1, 0, 0],
                [0, 0, 0, 1]]) children();
}

module cut_box() {   // the half above the spar plane (local -Y = up)
    translate([-200, -200, -400]) cube([600, 200, 800]);
}

module maybe_cut() {
    if (CUT == 1) difference() { children(); cut_box(); } else children();
}

view() {
    if (CLASH_STL != "") color("Red") import(CLASH_STL, convexity = 4);
    color("LightGray", CUT == 1 ? 1.0 : 0.55) maybe_cut() import(POD_STL, convexity = 8);
    color("DarkSeaGreen", CUT == 1 ? 1.0 : 0.7) maybe_cut() wing_local();
    color("DimGray")                                   // CF spar stub + bay
        translate([TRUNNION_X0, 0, PIVOT_Z_64]) rotate([0, 90, 0])
            difference() { cylinder(d = 20, h = 120, $fn = 48);
                           translate([0, 0, -1]) cylinder(d = 16.3, h = 122, $fn = 48); }
    part_to_local() {
        color("SteelBlue") variant_trunnion();
        // shaft azimuth in the part frame: local (+Z aft, -Y up) = part (+x, +y)
        color("Goldenrod") variant_pinion(az = J_SHAFT_AZ);
        color("Goldenrod")                             // Ø4 drive shaft stub
            rotate([0, 0, J_SHAFT_AZ]) translate([CENTRE_D, 0, GEAR_Z0])
                cylinder(d = 4, h = 40, $fn = 16);
    }
}
