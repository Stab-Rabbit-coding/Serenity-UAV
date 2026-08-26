#!/usr/bin/env python3
"""Fail-closed check that the wing's tabulated airfoil is a valid closed section.

Why this exists
---------------
Owner, 2026-08-23: "verify that the airfoil doesn't create a zero thickness point
that would cause a gap partway toward the trailing edge, as some of the drawings
show."  It does.  The tabulated section in `wings_s1223_revo.scad` **crosses to
negative thickness at x/c ~= 0.742** -- `S1223_UPPER` falls below `S1223_LOWER`
over the aft quarter -- so the outline self-intersects and pinches to zero
thickness partway to the trailing edge.  That is exactly the artifact the
drawings show.

Why no existing check caught it
-------------------------------
Two reasons, and both matter:

1. `tools/wing_spar_station_fit.py` and `tools/wing_internal_clearance.py` both
   ask "does a BORE fit inside this section?".  Neither asks whether the section
   is a valid simple polygon in the first place.
2. `wing_solid()` lofts with OpenSCAD `hull()`, which takes the CONVEX HULL of
   each section.  A convex hull of a self-intersecting outline is still a clean
   convex region, so the exported STL is watertight and `tools/validate_stls.py`
   passes.  The defect is real in the source and invisible in the artifact.

The masking is not free.  The convex hull's area is **1.65x** the tabulated
outline's -- it fills the airfoil's concavity and swallows the bowtie -- so the
built wing is materially not the section the analysis assumes.  That propagates
into mass, aero, and every internal-clearance result computed against the table.

What this checks
----------------
  1. Thickness is strictly positive from just aft of the LE to just forward of
     the TE (both surfaces meeting at the endpoints is correct and expected).
  2. The section outline, built exactly as `s1223_scaled_pts()` builds it, is a
     valid simple polygon -- no self-intersection.
  3. The outline is not being materially reshaped by `hull()`: the convex hull's
     area must stay within a stated tolerance of the outline's.

Any failure exits non-zero.  This is a source-integrity gate, so it is
deliberately independent of the STL: a clean STL is not evidence here.

Run:
    /usr/bin/python3 tools/wing_airfoil_integrity.py
    /usr/bin/python3 tools/wing_airfoil_integrity.py --table   (dump the sweep)

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5, Anthropic) under the author's
         direction, per `AGENTS.md` SS3 "Attribution and Licensing".
License: CC BY-SA 4.0 - creativecommons.org/licenses/by-sa/4.0
"""

import os
import sys

from shapely.geometry import Polygon
from shapely.validation import explain_validity

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import wing_spar_station_fit as wsf  # noqa: E402

# Endpoint exclusion: upper and lower legitimately meet at the LE and the TE, so
# thickness is zero there by definition.  Everything between must be positive.
LE_EXCLUDE = 0.005
TE_EXCLUDE = 0.005
# How far the convex hull may exceed the outline before hull() is reshaping the
# section rather than merely closing it.  A true airfoil has some concavity, so
# this is not zero -- but 1.65x is not "some".
HULL_AREA_TOLERANCE = 1.10


def load_tables():
    with open(wsf.WING_SCAD, encoding="utf-8") as fh:
        src = fh.read()
    return (wsf.scad_points(src, "S1223_UPPER"),
            wsf.scad_points(src, "S1223_LOWER"),
            src)


def thickness_at(upper, lower, x):
    return wsf.surf_y(upper, x) - wsf.surf_y(lower, x)


def check_thickness(upper, lower, dump=False):
    """Thickness must be strictly positive between the endpoints."""
    bad, crossings, prev = [], [], None
    if dump:
        print(f"\n  {'x/c':>7s} {'t/c':>10s}")
    for i in range(0, 1001):
        x = i / 1000.0
        t = thickness_at(upper, lower, x)
        if prev is not None and (prev > 0) != (t > 0) and LE_EXCLUDE < x < 1.0:
            crossings.append(x)
        prev = t
        if LE_EXCLUDE < x < 1.0 - TE_EXCLUDE and t <= 0.0:
            bad.append((x, t))
        if dump and i % 25 == 0:
            print(f"  {x:7.3f} {t:10.5f}")
    return bad, crossings


def check_polygon(upper, lower):
    """The outline, built the way s1223_scaled_pts() builds it."""
    pts = [(p[0], p[1]) for p in upper] + [(p[0], p[1]) for p in lower]
    poly = Polygon(pts)
    return poly


def wing_solid_uses_hull(src):
    """True if wing_solid() still lofts with hull() rather than a true loft.

    Rev S1d (KTD4, 2026-08-24) replaced the hull()-based loft with a manual
    polyhedron() built from s1223_scaled_pts() -- the SAME point list/order
    check 2 validates as a polygon() -- so root and tip cross-sections in the
    built solid are the tabulated outline exactly, not its convex hull.  This
    check reads wing_solid()'s own source rather than assuming either
    implementation, so it stays correct across a future revert either way.
    """
    start = src.find("module wing_solid()")
    if start == -1:
        return None  # can't locate the module; caller decides how to treat this
    end = src.find("\nmodule ", start + 1)
    body = src[start:end if end != -1 else len(src)]
    return "hull(" in body


def main():
    upper, lower, src = load_tables()
    dump = "--table" in sys.argv

    print("=== wing_airfoil_integrity.py ===")
    print(f"source: {os.path.relpath(wsf.WING_SCAD, REPO_ROOT)}")
    print(f"  S1223_UPPER {len(upper)} pts   S1223_LOWER {len(lower)} pts")

    failures = []

    bad, crossings = check_thickness(upper, lower, dump=dump)
    print("\n1. thickness strictly positive between the endpoints")
    if crossings:
        print(f"   surfaces CROSS at x/c {', '.join(f'{c:.3f}' for c in crossings)}")
    if bad:
        worst = min(bad, key=lambda t: t[1])
        print(f"   FAIL -- {len(bad)} sampled stations at or below zero thickness")
        print(f"   worst t/c {worst[1]:+.5f} at x/c {worst[0]:.3f}")
        print(f"   first offending station x/c {bad[0][0]:.3f}")
        failures.append("thickness crosses zero aft of the leading edge")
    else:
        print("   ok")

    poly = check_polygon(upper, lower)
    print("\n2. section outline is a valid simple polygon")
    if not poly.is_valid:
        print(f"   FAIL -- {explain_validity(poly)}")
        failures.append("section outline self-intersects")
    else:
        print("   ok")

    uses_hull = wing_solid_uses_hull(src)
    print("\n3. hull() is not reshaping the section")
    if uses_hull is None:
        print("   FAIL -- could not locate module wing_solid() to check")
        failures.append("wing_solid() not found in source")
    elif uses_hull:
        hull = poly.convex_hull
        ratio = hull.area / poly.area if poly.area else float("inf")
        print(f"   outline area {poly.area:.6f}   convex hull {hull.area:.6f}"
              f"   ratio {ratio:.3f}")
        if ratio > HULL_AREA_TOLERANCE:
            print(f"   FAIL -- hull() adds {(hull.area - poly.area) / hull.area * 100:.1f}% "
                  f"area (tolerance {HULL_AREA_TOLERANCE:.2f}x)")
            print("   wing_solid() lofts with hull(), so THIS is the shape that gets")
            print("   built -- not the tabulated section the analysis assumes.")
            failures.append("hull() materially reshapes the section")
        else:
            print("   ok")
    else:
        print("   n/a -- wing_solid() no longer calls hull() (Rev S1d, KTD4):")
        print("   it lofts a manual polyhedron() built directly from the same")
        print("   s1223_scaled_pts() list check 2 already validated, so the")
        print("   built cross-section IS the tabulated outline, not a convex")
        print("   approximation of it.  No area-ratio check applies.")

    print()
    if failures:
        print("  RESULT: FAIL")
        for f in failures:
            print(f"    - {f}")
        if uses_hull:
            print("\n  The exported STL is NOT evidence against this: hull() convexifies")
            print("  each section, so a self-intersecting outline still yields a")
            print("  watertight solid and validate_stls.py passes.")
        sys.exit(1)
    print("  RESULT: PASS -- the tabulated section is a valid closed airfoil")


if __name__ == "__main__":
    main()
