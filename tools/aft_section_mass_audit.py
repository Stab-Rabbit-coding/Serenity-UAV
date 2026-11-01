#!/usr/bin/env python3
"""aft_section_mass_audit.py -- measured geometry and mass baseline of the middle
and rear fuselage sections, and of the same two sections joined as one part.

Method: the one used for the cargo section in docs/MASS_AUDIT_CARGO_WING_ROOT.md.
Every figure comes from the published, watertight meshes:
  - mesh volume and area, mass at three densities (CF-PETG as-printed bulk,
    CF-PETG solid, SLS DuraForm PA CF solid);
  - mass per station band along Y, with a mean wall thickness for each band
    (t = 2V/A, valid for a thin closed shell);
  - envelope (filled) volume and enclosed cavity from the cross-section outer loops;
  - first moment and pitch inertia about the tilt pivot (Y 326.7, Z 146.9).
It does not design anything; it is the "before" picture.

Frame: aircraft datum R2 (Y aft-positive, Z up), hull frame as baked.

Run:  /usr/bin/python3 tools/aft_section_mass_audit.py
Needs: numpy, trimesh, shapely (system Python; see the venv note in AGENTS.md).

Sources:
  RHO_PRINT 1.05 and RHO_SOLID 1.28 g/cc -- tools/auw_ledger.py, REF-MAT-002
  DuraForm PA CF solid density 1.11 g/cc, ASTM D792 -- 3D Systems datasheet
    3DS-30108A (2023-10-31), supplied by the owner
  Pivot station -- tools/cg_relocation_study.py PIVOT_Y, auw_ledger pivot Z

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude Opus 5.5 (Anthropic) under the author's direction,
2026-10-31, per AGENTS.md AI attribution.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import itertools
import os
import sys

import numpy as np
import trimesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hull_datums as hd  # noqa: E402  (tilt pivot = SPAR_Y)
from shapely.geometry import MultiPolygon

HERE = os.path.dirname(os.path.abspath(__file__))
STL = os.path.join(HERE, "..", "airframe", "stls", "fuselage")

RHO = {"CF-PETG bulk 1.05": 1.05e-3, "CF-PETG solid 1.28": 1.28e-3,
       "PA CF SLS 1.11": 1.11e-3}          # g/mm^3
RHO_LEDGER = 1.05e-3
PIVOT_Y, PIVOT_Z = hd.SPAR_Y, 146.9  # 339.4 since the 2026-10-31 shift (was typed 326.7)
BAND = 10.0                                # mm, station band width

PARTS = {
    "middle": "middle_shell24_2mm_repaired.stl",
    "rear": "rear_shell24_2mm_repaired.stl",
    "collar Y509": "middle_rear_splice_collar.stl",
    "collar Y436": "cargo_middle_splice_collar.stl",
}


def load(name):
    """Load one STL and refuse a mesh whose volume is not trustworthy."""
    m = trimesh.load(os.path.join(STL, PARTS[name]))
    if not m.is_watertight:
        sys.exit(f"FAIL: {name} is not watertight; volume is meaningless")
    return m


def section(m, y):
    """Cross-section at station y: (outer-loop area, wall area, perimeter, x/z extent).
    Outer-loop area is the filled envelope; wall area is the material cut."""
    s = m.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    if s is None:
        return None
    p, _ = s.to_2D()
    polys = p.polygons_full
    if not polys:
        return None
    wall = sum(q.area for q in polys)
    # Envelope = convex hull of the whole cut.  The middle is open ventrally (horseshoe),
    # so its cuts are C-shaped and have no closed outer loop; the hull is an upper bound
    # for these near-convex ovals.
    outer = MultiPolygon(polys).convex_hull.area
    per = sum(q.exterior.length for q in polys)
    b = s.bounds
    return outer, wall, per, b[1][0] - b[0][0], b[1][2] - b[0][2], len(polys)


def bands(m, label):
    """Mass per Y band by slicing the mesh with two planes."""
    y0, y1 = m.bounds[0][1], m.bounds[1][1]
    edges = np.arange(np.floor(y0 / BAND) * BAND, y1 + BAND, BAND)
    print(f"\n{label}: mass per {BAND:.0f} mm band (CF-PETG bulk), mean wall t = 2V/A")
    print(f"  {'Y band':>15s} {'V mm3':>9s} {'mass g':>7s} {'t mm':>5s} {'env cm2':>8s} "
          f"{'wall mm2':>8s} {'W x H mm, loops':>15s}")
    rows = []
    for a, b in itertools.pairwise(edges):
        try:
            sl = m.slice_plane([0, a, 0], [0, 1, 0], cap=True)
            sl = sl.slice_plane([0, b, 0], [0, -1, 0], cap=True)
        except (ValueError, IndexError):
            continue
        if sl is None or sl.is_empty or sl.volume <= 0:
            continue
        v = sl.volume
        # wall area excludes the two cap faces: cap area is the cut material area
        sec = section(m, (a + b) / 2)
        caps = 2 * sec[1] if sec else 0.0
        t = 2 * v / max(sl.area - caps, 1e-9)
        env = sec[0] / 100 if sec else float("nan")
        wh = f"{sec[3]:.0f} x {sec[4]:.0f} n{sec[5]}" if sec else "-"
        rows.append((a, b, v))
        print(f"  {a:6.0f}..{b:6.0f} {v:9.0f} {v * RHO_LEDGER:7.1f} {t:5.2f} {env:8.1f} "
              f"{sec[1] if sec else 0:8.0f} {wh:>15s}")
    print(f"  sum of bands {sum(r[2] for r in rows):.0f} mm3 vs mesh {m.volume:.0f} mm3")
    return rows


def ventral_dorsal(m, label):
    """Split mass at the shell's own Z mid-line: skids and horseshoe legs sit ventral."""
    zc = (m.bounds[0][2] + m.bounds[1][2]) / 2
    lo = m.slice_plane([0, 0, zc], [0, 0, -1], cap=True)
    hi = m.slice_plane([0, 0, zc], [0, 0, 1], cap=True)
    print(f"  {label}: ventral (Z < {zc:.1f}) {lo.volume * RHO_LEDGER:.1f} g, "
          f"dorsal {hi.volume * RHO_LEDGER:.1f} g")


def summary(label, m):
    """Mass at each density, centroid, first moment and pitch inertia about the pivot."""
    c = m.center_mass
    print(f"\n{label}: V {m.volume:,.0f} mm3, A {m.area:,.0f} mm2, mean t {2 * m.volume / m.area:.2f} mm")
    print(f"  bounds Y {m.bounds[0][1]:.1f}..{m.bounds[1][1]:.1f}, "
          f"X {m.bounds[0][0]:.1f}..{m.bounds[1][0]:.1f}, Z {m.bounds[0][2]:.1f}..{m.bounds[1][2]:.1f}")
    print(f"  centroid X {c[0]:.1f} Y {c[1]:.1f} Z {c[2]:.1f}")
    for k, r in RHO.items():
        g = m.volume * r
        inertia = m.moment_inertia * r  # g.mm2 about the centroid, mesh axes
        ip = inertia[0, 0] + g * ((c[1] - PIVOT_Y) ** 2 + (c[2] - PIVOT_Z) ** 2)
        print(f"  {k:18s}: {g:6.1f} g ({g / 453.592:.3f} lbm); moment about pivot "
              f"{g * (c[1] - PIVOT_Y):8.0f} g.mm; I_pitch about pivot {ip / 1e2:9.0f} g.cm2 "
              f"({ip / 453.592 / 645.16:.2f} lbm.in2)")
    return m.volume, c


def main():
    m = {k: load(k) for k in PARTS}
    for k in ("middle", "rear", "collar Y509", "collar Y436"):
        summary(k, m[k])
    for k in ("middle", "rear"):
        bands(m[k], k)
        ventral_dorsal(m[k], k)

    # Envelope and cavity: integrate the outer-loop area along Y (1 mm steps).
    print("\nEnvelope and cavity (integrated cross-section outer loops, 1 mm step)")
    for k in ("middle", "rear"):
        y = np.arange(np.ceil(m[k].bounds[0][1]) + 0.5, m[k].bounds[1][1], 1.0)
        env = sum((section(m[k], yy) or (0,))[0] for yy in y)
        print(f"  {k:6s}: envelope {env / 1e6:.3f} L, shell {m[k].volume / 1e6:.3f} L, "
              f"enclosed {(env - m[k].volume) / 1e6:.3f} L")

    # Joined baseline: middle + rear + a 2 mm bridge across the Y 508..510 gap, collar deleted.
    sa, sb = section(m["middle"], 507.5), section(m["rear"], 510.5)
    bridge = 0.5 * (sa[1] + sb[1]) * 2.0
    joined = trimesh.util.concatenate([m["middle"], m["rear"]])
    v = m["middle"].volume + m["rear"].volume + bridge
    cy = (m["middle"].volume * m["middle"].center_mass[1] + m["rear"].volume * m["rear"].center_mass[1]
          + bridge * 509.0) / v
    print("\nJOINED middle+rear (as-is walls, collar Y509 deleted, gap bridged)")
    print(f"  wall cut at Y 507.5 {sa[1]:.0f} mm2 (perimeter {sa[2]:.0f} mm), at Y 510.5 {sb[1]:.0f} mm2 "
          f"(perimeter {sb[2]:.0f} mm); bridge {bridge:.0f} mm3")
    print(f"  envelope mismatch at the joint: middle {sa[3]:.0f} x {sa[4]:.0f} mm, "
          f"rear {sb[3]:.0f} x {sb[4]:.0f} mm")
    old = m["middle"].volume + m["rear"].volume + m["collar Y509"].volume
    for k, r in RHO.items():
        print(f"  {k:18s}: joined {v * r:6.1f} g vs 4-section parts {old * r:6.1f} g "
              f"(delta {(v - old) * r:+.1f} g); centroid Y {cy:.1f}; moment {v * r * (cy - PIVOT_Y):.0f} g.mm")
    print(f"  overall length {joined.bounds[1][1] - joined.bounds[0][1]:.1f} mm "
          f"({(joined.bounds[1][1] - joined.bounds[0][1]) / 25.4:.2f} in); bbox "
          f"{np.ptp(joined.bounds, axis=0).round(1).tolist()} mm")


if __name__ == "__main__":
    main()
