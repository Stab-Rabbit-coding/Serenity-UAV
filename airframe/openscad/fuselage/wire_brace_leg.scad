// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   This part is modeled in a PART-LOCAL frame (vertical axis = local Z,
//   foot at Z=0); NOT a primary-component STL; do NOT bake with
//   bake_hull_frame.py.
// ===========================================================================
// ===========================================================================
// wire_brace_leg.scad
// Serenity UAV -- Rev R5 -- Strong-Leg vertical post + 4-wire brace
// ===========================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-06-20
// Revision: Rev R5
//
// Description
// -----------
// IMPORTANT geometric correction (2026-06-20): the ORIGINAL canonical single-
// blade leg (pre-Strong-Leg) is itself a vertical part with TWO branch
// points -- one AT THE APEX (top) and one about 1/3 of the way down FROM
// THE APEX. The Strong-Leg's duplicate+rotate(30deg)+union therefore
// produces FOUR branch points total (2 at the apex, 2 at the 1/3-down
// point), not a single fork into 2 arms as earlier revisions (R2-R4)
// approximated from a coarser reading of the mesh. Rev R5 models this
// directly and braces the vertical post to the hull at both branch levels:
//
//   APEX socket (2 holes, Z ~= full leg length)        -- 2x SPRING wire
//     (elastic, recoverable; handles ordinary hard landings with zero
//     permanent set; sized for the 1.5 ft elastic-check energy, TODO.md LG-06).
//   1/3-DOWN socket (2 holes, Z ~= 2/3 of the leg length up from the foot)
//                                                        -- 2x DUCTILE wire
//     (plastic, sacrificial; each independently sized for the FULL 6 ft
//     full-AUW per-leg worst-case energy; fires by progressively deepening
//     its pre-formed bow, visibly bent afterward -- field-replaceable).
//
// Both wire types share the same simple "bowed strut" shape: a single
// shallow pre-bend in an otherwise straight wire/rod, NOT a closed loop --
// chosen specifically for manufacturability (forms with a simple bending
// jig or by hand, no precision winding) and field replacement (straight
// stock wire, cut to length, bent over a form block).
//
// All dimensions per docs/LANDING_GEAR_ANALYSIS.md Rev R5 SS4.
//
// Render commands
// ----------------
//   openscad -D 'PART="post"'                    -o post.stl                    wire_brace_leg.scad
//   openscad -D 'PART="spring_wire_nominal"'      -o spring_wire_nominal.stl     wire_brace_leg.scad
//   openscad -D 'PART="spring_wire_deformed"'     -o spring_wire_deformed.stl    wire_brace_leg.scad
//   openscad -D 'PART="ductile_wire_nominal"'     -o ductile_wire_nominal.stl    wire_brace_leg.scad
//   openscad -D 'PART="ductile_wire_deformed"'    -o ductile_wire_deformed.stl   wire_brace_leg.scad
// ===========================================================================

$fn = 48;

// ---------------------------------------------------------------------------
// Post parameters (mm) -- per docs/LANDING_GEAR_ANALYSIS.md Rev R5 SS4.7
// Branch heights match the ORIGINAL canonical single-blade leg's own two
// branch points (apex, and 1/3 of the way down from the apex) -- the
// Strong-Leg's duplicate+rotate+union doubles each into a pair.
// ---------------------------------------------------------------------------
LEG_LEN        = 79.8;             // mm, full leg length (matches the original canonical leg)
POST_FOOT_Z    = 0;
POST_MID_Z     = LEG_LEN * 2.0/3.0;  // ~=53.2mm -- "1/3 down from the apex" branch (ductile pair)
POST_TOP_Z     = LEG_LEN;            // ~=79.8mm -- apex branch (spring pair)

// Cylindrical post, area-equivalent to the Rev R5 square sizing in
// docs/LANDING_GEAR_ANALYSIS.md SS4.6 (20.3x20.3mm / 10.6x10.6mm), per
// user feedback that a round post is preferred over a rectangular one.
POST_LOWER_R = 11.45;      // mm, lower segment radius (foot -> taper start)
POST_UPPER_R = 5.98;       // mm, upper segment radius (taper end -> cap)
POST_TAPER_LEN = 8.0;      // mm, smooth conical taper length (no hard step/ledge)
SOCK_REACH_MARGIN = 6.0;   // mm, clearance kept between a socket's Z reach and the
                            // taper, so bores stay in uniform-diameter material
POST_CAP_CLEARANCE = 6.0;  // mm, extra post material above the apex socket height
                            // so that socket has material on both sides of its bore

TAPER_START_Z = POST_MID_Z + SOCK_REACH_MARGIN;          // ~=59.2mm
TAPER_END_Z   = TAPER_START_Z + POST_TAPER_LEN;          // ~=67.2mm
POST_CAP_Z    = POST_TOP_Z + POST_CAP_CLEARANCE;         // ~=85.8mm, actual printed top

SOCK_D   = 5.0;     // socket bore diameter (wire end + clearance)
SOCK_DEPTH = 10.0;  // socket depth
LEAN_ANG = 24.0;    // deg from vertical, both wire pairs
AZ_SPLIT = 15.0;    // deg, +/- azimuth split within each pair (30 deg apart)

// ---------------------------------------------------------------------------
// Wire parameters -- bowed strut, single shallow pre-bend.
// Apex (spring) wires are LONGER and 1/3-down (ductile) wires SHORTER,
// proportioned similarly to the retired Rev R1.4 V-brace's upper:lower
// strut ratio (77.6:53.9mm) -- the apex branch reaches further out to a
// higher hull attachment, the 1/3-down branch to a closer one.
// ---------------------------------------------------------------------------
SPRING_L       = 45.0;     // mm, apex (spring) wire chord length
DUCTILE_L      = 30.0;     // mm, 1/3-down (ductile) wire chord length

SPRING_D       = 3.17;     // mm, spring wire diameter
SPRING_H_NOM   = 3.5;      // mm, nominal (undeformed) sag
SPRING_H_DEF   = 10.5;     // mm, deformed (post-overload) sag -- NOTE: spring wire is
                            // elastic and should NOT take a permanent set in normal
                            // service; this deformed variant exists only to illustrate
                            // the bow-deepening mechanism for review, see TODO LG-06.

DUCTILE_D      = 4.35;     // mm, ductile wire diameter
DUCTILE_H_NOM  = 3.5;      // mm, nominal (undeformed) sag
DUCTILE_H_DEF  = 10.5;     // mm, deformed (fired) sag -- the field-inspection
                            // "this fuse has activated, replace it" shape.

PART = "post";   // override with -D on the CLI

// ---------------------------------------------------------------------------
// Bowed wire strut: a round-wire rod of length L (chord) with a shallow
// circular-arc pre-bend of rise h at its midpoint, lying in the local XZ
// plane (chord along local Z). Built as a single polyhedron tube swept
// along the bow path (fast -- avoids chaining many hull() operations,
// which is extremely slow in OpenSCAD's CGAL backend).
// ---------------------------------------------------------------------------
module bowed_wire(d, L, h) {
    n = 16;          // path segments -- coarse is fine, the bow is shallow
    sides = 8;        // sides per tube cross-section
    r = d / 2;

    path = [for (i = [0 : n]) let (
        t = i / n,
        z = (t - 0.5) * L,
        x = h * (1 - pow(2*t - 1, 2))
    ) [x, 0, z]];

    // local tangent direction at each path point (for a perpendicular ring)
    tangents = [for (i = [0 : n]) let (
        i0 = max(i - 1, 0),
        i1 = min(i + 1, n),
        dv = path[i1] - path[i0]
    ) dv / norm(dv)];

    // build an orthonormal frame (tangent, u, v) at each point, then a ring
    // of `sides` points around it, radius r
    rings = [for (i = [0 : n]) let (
        t = tangents[i],
        arbitrary = (abs(t[1]) < 0.9) ? [0, 1, 0] : [1, 0, 0],
        u = cross(t, arbitrary) / norm(cross(t, arbitrary)),
        v = cross(t, u)
    ) [for (j = [0 : sides - 1]) let (
        ang = 2 * PI * j / sides
    ) path[i] + r * (u * cos(ang * 180 / PI) + v * sin(ang * 180 / PI))]];

    points = [for (i = [0 : n]) for (j = [0 : sides - 1]) rings[i][j]];

    side_faces = [for (i = [0 : n - 1]) for (j = [0 : sides - 1]) let (
        a = i * sides + j,
        b = i * sides + (j + 1) % sides,
        c = (i + 1) * sides + (j + 1) % sides,
        d2 = (i + 1) * sides + j
    ) each [[a, b, c], [a, c, d2]]];

    cap_start = [for (j = [sides - 1 : -1 : 0]) j];
    cap_end_base = n * sides;
    cap_end = [for (j = [0 : sides - 1]) cap_end_base + j];

    faces = concat(side_faces, [cap_start], [cap_end]);

    polyhedron(points = points, faces = faces, convexity = 4);
}

// ---------------------------------------------------------------------------
// Simplified vertical post: round (cylindrical) column, foot at Z=0, with a
// smooth conical taper between the wider lower segment and the narrower
// upper segment (no hard ledge/step), and 4 angled socket bores (2 near
// POST_TOP_Z for the spring pair, 2 near POST_MID_Z for the ductile pair),
// each bored at LEAN_ANG from vertical, split +/-AZ_SPLIT in azimuth within
// its pair. Both socket heights are kept clear of the taper zone (see
// TAPER_START_Z/TAPER_END_Z) so each bore lands in uniform-diameter material.
// ---------------------------------------------------------------------------
module post_solid() {
    union() {
        cylinder(h = TAPER_START_Z - POST_FOOT_Z, r = POST_LOWER_R);
        translate([0, 0, TAPER_START_Z])
            cylinder(h = POST_TAPER_LEN, r1 = POST_LOWER_R, r2 = POST_UPPER_R);
        translate([0, 0, TAPER_END_Z])
            cylinder(h = POST_CAP_Z - TAPER_END_Z, r = POST_UPPER_R);
    }
}

// Short blind-ish hole anchored on the post's centreline axis at height z:
// extends just past the post's surface outward (so the wire has somewhere
// to plug in) without reaching all the way through to the far surface --
// deliberately SHORT (well under the post half-width) to avoid carving a
// disconnected sliver out of the thin post, per the schematic nature of
// this demonstration model.
module socket_bore(z, az_deg) {
    translate([0, 0, z])
        rotate([0, LEAN_ANG, az_deg])
            translate([0, 0, -SOCK_DEPTH/2])
                cylinder(h = SOCK_DEPTH, d = SOCK_D, center = true);
}

module post() {
    difference() {
        post_solid();
        socket_bore(POST_TOP_Z, 90 - AZ_SPLIT);
        socket_bore(POST_TOP_Z, 90 + AZ_SPLIT);
        socket_bore(POST_MID_Z, 90 - AZ_SPLIT);
        socket_bore(POST_MID_Z, 90 + AZ_SPLIT);
    }
}

// ---------------------------------------------------------------------------
// PART selector
// ---------------------------------------------------------------------------
if (PART == "post") {
    post();
} else if (PART == "spring_wire_nominal") {
    bowed_wire(SPRING_D, SPRING_L, SPRING_H_NOM);
} else if (PART == "spring_wire_deformed") {
    bowed_wire(SPRING_D, SPRING_L, SPRING_H_DEF);
} else if (PART == "ductile_wire_nominal") {
    bowed_wire(DUCTILE_D, DUCTILE_L, DUCTILE_H_NOM);
} else if (PART == "ductile_wire_deformed") {
    bowed_wire(DUCTILE_D, DUCTILE_L, DUCTILE_H_DEF);
} else {
    assert(false, str("Unknown PART: ", PART));
}
