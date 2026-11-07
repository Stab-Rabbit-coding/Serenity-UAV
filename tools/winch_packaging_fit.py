#!/usr/bin/env python3
"""winch_packaging_fit.py -- does the Rev C1 cargo winch fit the one-piece forward hull?

docs/CARGO_WINCH_SPECIFICATION.md (Rev C1) defines a fixed-axle spool, a 24-tooth ratchet
ring, a pawl and catch solenoid on the starboard pedestal, and an SPT5425LV servo on the port
pedestal that drives the spool through a dog coupler.  Only two retired-design STLs exist, so
before any pedestal is drawn this tool answers the prior question: with the spec's own
dimensions, is there a place in the cargo bay where the whole stack fits inside the hull?

Method (no boolean on the 115 MB hull): slice the fused forward hull every SLICE_MM of Y, take the
wall cross-section as a polygon in the (X, Z) plane, and test each winch element's footprint at
that Y against it.  An element is a prism along X (spool, flanges, ratchet ring, coupler) or a box.
Elements are inflated by CLEARANCE_MM.  Hull frame: X +port (starboard = -X), Y +aft, Z up.

Stack along X, relative to the spool centre (starboard = -X; all from the spec):
  stbd pedestal   X -24.0 .. -14.5   (axle clamp, pawl pivot boss, spring seat)
  ratchet ring    X -14.0 .. -11.0   R 15.0 (24 teeth x 2 mm, face 3 mm)
  flange          X -11.0 ..  -9.0   R 13.0
  drum            X  -9.0 ..   9.0   R 10.0 (usable width 18 mm)
  flange          X   9.0 ..  11.0   R 13.0
  dog coupler     X  11.0 ..  19.0   R  8.0
  port pedestal   X  19.0 ..  25.0
  servo           X  25.0 ..  65.5   Y -12.0 .. 28.5   Z +/-10   (40.5 x 20 x 40.5 envelope,
                                       output spline along X, REF-SENSOR-013)
  catch solenoid  X -24.0 .. -12.0   Y  12.0 .. 36.0   Z +/-6    (O12 x 24, pull type)
The servo shaft offset along its length and the solenoid placement are ASSUMED (flagged below).

Usage:
    python3 tools/winch_packaging_fit.py            # report at the layout reservation, then search
    python3 tools/winch_packaging_fit.py --at X Y Z # test one placement (spool centre, mm)
Exit 0 = the spec stack fits at the placement tested / found; 1 = it does not.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic) under the author's direction, 2026-11-07.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import sys
import tarfile
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent.parent
HULL_TAR = ROOT / "airframe/stls/fuselage/head_cargo_shell24_2mm_merged.stl.tar.gz"
SLICE_MM = 2.0
CLEARANCE_MM = 1.0
#: The layout reservation: single line over the payload centre (tools/cargo_layout_fit.py).
HOIST_Y = 356.5
AXLE_Z = 221.4
PAYLOAD_TOP_Z = 167.2   # DOOR_CROWN_Z 91 + payload height 76.2

# (name, kind, x0, x1, y0, y1, z0, z1)  kind "cyl" = prism along X of radius R about (y,z)=(0,0)
# Boxes use y/z extents relative to the axle; cylinders use R in the y1 slot.
ELEMENTS = [
    ("stbd pedestal", "box", -24.0, -14.5, -14.0, 14.0, -10.0, 15.0),
    ("ratchet ring", "cyl", -14.0, -11.0, 15.0, 0, 0, 0),
    ("stbd flange", "cyl", -11.0, -9.0, 13.0, 0, 0, 0),
    ("drum", "cyl", -9.0, 9.0, 10.0, 0, 0, 0),
    ("port flange", "cyl", 9.0, 11.0, 13.0, 0, 0, 0),
    ("dog coupler", "cyl", 11.0, 19.0, 8.0, 0, 0, 0),
    ("port pedestal", "box", 19.0, 25.0, -12.0, 28.5, -10.0, 15.0),
    ("servo", "box", 25.0, 65.5, -12.0, 28.5, -10.0, 10.0),
    ("catch solenoid", "box", -24.0, -12.0, 12.0, 36.0, -6.0, 6.0),
]


def load_hull() -> trimesh.Trimesh:
    with tarfile.open(HULL_TAR) as tz:
        member = tz.extractfile("head_cargo_shell24_2mm_merged.stl")
        assert member is not None
        return trimesh.load_mesh(member, file_type="stl", force="mesh")


def wall_polygons(hull: trimesh.Trimesh, ys: np.ndarray) -> dict[float, object]:
    """Wall cross-section (union of polygons) in (X, Z) at each Y."""
    out = {}
    for y in ys:
        sec = hull.section(plane_origin=[0, float(y), 0], plane_normal=[0, 1, 0])
        if sec is None:
            continue
        p2, T = sec.to_planar()
        polys = []
        for p in p2.polygons_full:
            def xz(c):
                o = (T @ np.array([c[0], c[1], 0.0, 1.0]))[:3]
                return (o[0], o[2])
            polys.append(Polygon([xz(c) for c in p.exterior.coords],
                                 [[xz(c) for c in h.coords] for h in p.interiors]))
        out[round(float(y), 3)] = unary_union(polys)
    return out


def footprint(el, ox, oy, oz, y):
    """XZ footprint of an element at world slice `y`, or None if the slice misses it."""
    name, kind, x0, x1, a, b, c, d = el
    pad = CLEARANCE_MM
    if kind == "cyl":
        r = a + pad
        dy = y - oy
        if abs(dy) >= r:
            return None
        h = np.sqrt(r * r - dy * dy)
        return sbox(ox + x0 - pad, oz - h, ox + x1 + pad, oz + h)
    if not (oy + a - pad <= y <= oy + b + pad):
        return None
    return sbox(ox + x0 - pad, oz + c - pad, ox + x1 + pad, oz + d + pad)


def interference(walls, ox, oy, oz) -> dict[str, float]:
    """Max overlap area (mm^2) with the hull wall, per element, over all Y slices."""
    worst: dict[str, float] = {el[0]: 0.0 for el in ELEMENTS}
    for y, wp in walls.items():
        for el in ELEMENTS:
            fp = footprint(el, ox, oy, oz, y)
            if fp is not None:
                a = fp.intersection(wp).area
                if a > worst[el[0]]:
                    worst[el[0]] = a
    return worst


def others_overlap(ox: float, oy: float, oz: float) -> dict[str, float]:
    """Overlap volume (mm^3) of the winch stack with every OTHER cargo-bay item in the layout
    tool (tools/cargo_layout_fit.py), excluding the old winch/hoist reservation and the shell."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import cargo_layout_fit as clf  # noqa: PLC0415  heavy import, only for stage 2

    if not hasattr(others_overlap, "L"):
        others_overlap.L = clf.layout_t5()  # type: ignore[attr-defined]
    # The layout tool still models the retired battery cradle and the cargo battery (the pack
    # moved to the head twin tray at Rev U); counting them would charge the winch for a gap.
    skip = ("winch", "hoist", "ramp fairing", "battery", "cradle")
    hits: dict[str, float] = {}
    for name, x0, x1, y0, y1, z0, z1, kind in _solids(ox, oy, oz):
        mine = clf.to_man(clf.cyl("x", y0, z0, x0, x1, y1) if kind == "cyl"
                          else clf.box(x0, x1, y0, y1, z0, z1))
        for iname, item in others_overlap.L.items():  # type: ignore[attr-defined]
            if any(k in iname for k in skip) or item.get("skin_seat"):
                continue
            v = (mine ^ clf.to_man(item["solid"])).volume()
            if v > 1.0:
                hits[f"{name} x {iname}"] = round(float(v), 1)
    return hits


def _solids(ox, oy, oz):
    """The stack as hull-frame solids: (name, x0, x1, a, b, c, kind) for clf.cyl / clf.box."""
    out = []
    for name, kind, x0, x1, a, b, c, d in ELEMENTS:
        if kind == "cyl":
            out.append((name, ox + x0, ox + x1, oy, a, oz, 0, "cyl"))
        else:
            out.append((name, ox + x0, ox + x1, oy + a, oy + b, oz + c, oz + d, "box"))
    return out


def line_offset(ox: float) -> float:
    return abs(ox)


def report(walls, ox, oy, oz) -> bool:
    w = interference(walls, ox, oy, oz)
    bad = {k: v for k, v in w.items() if v > 0.5}
    print(f"spool centre X {ox:+.1f}  Y {oy:.1f}  Z {oz:.1f}   hoist line offset from the "
          f"payload centre: {line_offset(ox):.1f} mm")
    for k, v in w.items():
        verdict = f"CLASH {v:.0f} mm2" if v > 0.5 else f"clear (>= {CLEARANCE_MM:.1f} mm)"
        print(f"   {k:16s} {verdict}")
    return not bad


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--at", nargs=3, type=float, metavar=("X", "Y", "Z"))
    args = ap.parse_args(argv)
    hull = load_hull()
    ys = np.arange(300.0, 420.0, SLICE_MM)
    walls = wall_polygons(hull, ys)
    if args.at:
        return 0 if report(walls, *args.at) else 1
    print("1) Layout reservation: single line on the payload centre line")
    ok0 = report(walls, 0.0, HOIST_Y, AXLE_Z)
    print("\n2) Search for any placement where the whole spec stack is clear of the hull")
    best = []
    for oz in np.arange(190.0, 232.0, 2.0):
        for ox in np.arange(-60.0, 40.1, 2.5):
            for oy in np.arange(330.0, 391.0, 5.0):
                if sum(interference(walls, ox, oy, oz).values()) <= 0.5 * len(ELEMENTS):
                    best.append((abs(ox - 0.0), ox, oy, oz))
    best.sort()
    if not best:
        print("   NO placement in X -60..40, Y 330..390, Z 190..230 clears the hull.")
    else:
        print(f"   {len(best)} clear placements; nearest the payload centre line:")
        for d, ox, oy, oz in best[:6]:
            print(f"     X {ox:+6.1f}  Y {oy:6.1f}  Z {oz:6.1f}   line offset {d:.1f} mm")
        print("\n3) The nearest hull-clear placements against every other cargo-bay item")
        rank = sorted(best, key=lambda t: np.hypot(t[1], t[2] - HOIST_Y))[:30]
        scored = []
        for _, ox, oy, oz in rank:
            hits = others_overlap(ox, oy, oz)
            scored.append((sum(hits.values()), np.hypot(ox, oy - HOIST_Y), ox, oy, oz, hits))
        scored.sort(key=lambda t: (t[0] > 0, t[1]))
        free = [t for t in scored if t[0] == 0]
        print(f"   {len(free)} of {len(scored)} tested placements also clear all other equipment")
        for tot, off, ox, oy, oz, hits in scored[:6]:
            tag = "CLEAR" if tot == 0 else f"{tot:.0f} mm3 overlap"
            print(f"     X {ox:+6.1f}  Y {oy:6.1f}  Z {oz:6.1f}   {off:5.1f} mm from the payload "
                  f"centre   {tag}")
            for k, v in list(hits.items())[:3]:
                print(f"         {k}: {v} mm3")
    return 0 if (ok0 or best) else 1


if __name__ == "__main__":
    sys.exit(main())
