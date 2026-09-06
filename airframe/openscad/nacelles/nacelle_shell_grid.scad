// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   This file defines no geometry of its own and no coordinate frame: it is a
//   helper library operating in whatever frame its caller supplies.  Every
//   consumer here works in the nacelle-local print frame (duct axis = local +Z,
//   intake at Z = 0).
// ===========================================================================
// =============================================================================
// nacelle_shell_grid.scad — turn a measured (Z, azimuth) radius grid into a solid
// =============================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Analysis and code by Claude (Claude Opus 5, Anthropic) under the author's
//           direction, per AGENTS.md §3 "Attribution and Licensing"
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-09-01  (Rev T4c)
//
// WHY THIS EXISTS
// ---------------
// The canonical Serenity nacelle is an imported mesh, so nothing downstream can
// ask it a question — you cannot offset it, cap it, or take a sector of it.
// `tools/nacelle_hollow_profile.py` solves that by RAY-CASTING the shell and
// emitting its outer skin as a radius grid (`nacelle_hollow_profile.scad`).
// This library turns any such grid back into a closed solid, and offsets one
// grid from another, so the pod's internal cavity, the ESC access-cover landing
// ledge and the covers themselves can all be built from the same measurement
// rather than from three separate approximations of the same surface.
//
// THE OFFSET IS RADIAL, NOT NORMAL — and that is a real approximation.
// `offset_grid(g, d)` subtracts d from every radius.  A true wall offset is
// along the surface NORMAL, so a radial offset under-thickens the wall by a
// factor of cos(θ), where θ is the angle between the surface normal and the
// radial direction.  On this shell that penalty is negligible where it is used:
// over Z 74–134, where the ESC bays live, the skin's meridional slope is under
// 12°, so a nominal 3.0 mm radial offset is a ≥ 2.93 mm true wall.  Do NOT reuse
// this near the intake dome or the tail cone, where the surface turns hard and
// the same call would leave a wall less than half its nominal thickness.
// =============================================================================


// ── Function: offset_grid ─────────────────────────────────────────────────────
// Radially offset every radius in the grid inward by d.  See the caveat above.
function offset_grid(g, d) = [ for (row = g) [ for (v = row) v - d ] ];


// ── Module: grid_solid ────────────────────────────────────────────────────────
// A closed polyhedron from one ring of `n_az` points per station in `zs`, with
// flat caps at both ends.  Faces are wound CLOCKWISE seen from outside, which is
// what polyhedron() wants; the result is a positive-volume, watertight solid.
module grid_solid(grid, zs, n_az) {
    nz = len(zs);
    pts = concat(
        [ for (k = [0 : nz - 1], i = [0 : n_az - 1])
              [ grid[k][i] * cos(i * 360 / n_az),
                grid[k][i] * sin(i * 360 / n_az),
                zs[k] ] ],
        [ [0, 0, zs[0]], [0, 0, zs[nz - 1]] ]);
    c0 = nz * n_az;
    c1 = nz * n_az + 1;
    fs = concat(
        [ for (k = [0 : nz - 2], i = [0 : n_az - 1])
              [ k * n_az + i, (k + 1) * n_az + i,
                (k + 1) * n_az + (i + 1) % n_az ] ],
        [ for (k = [0 : nz - 2], i = [0 : n_az - 1])
              [ k * n_az + i, (k + 1) * n_az + (i + 1) % n_az,
                k * n_az + (i + 1) % n_az ] ],
        [ for (i = [0 : n_az - 1]) [ c0, i, (i + 1) % n_az ] ],
        [ for (i = [0 : n_az - 1])
              [ c1, (nz - 1) * n_az + (i + 1) % n_az,
                (nz - 1) * n_az + i ] ]);
    polyhedron(points = pts, faces = fs, convexity = 12);
}


// ── Module: esc_panel_slab ────────────────────────────────────────────────────
// One flat ESC panel's swept envelope: a slab of width `w` whose INNER face is
// tangent to a cylinder of radius `r0`, centred on azimuth `az`, running from
// radius r0 out to r1 and from z0 to z1.
//
// Tangent, not chordal, is the whole point.  Every point of a slab tangent at r0
// is at radius >= r0, so the panel can never dip inside the duct wall it sits on
// — while its OUTER corners sit at sqrt(r1^2 + (w/2)^2), which is what has to
// clear the skin.  That asymmetry is why a hinged board fits where a flat one
// does not, and it is the same test tools/nacelle_esc_bay_fit.py applies.
module esc_panel_slab(w, az, r0, r1, z0, z1) {
    rotate([0, 0, az])
        translate([r0, -w / 2, z0])
            cube([r1 - r0, w, z1 - z0]);
}
