#!/usr/bin/python3
"""LG Option A1b packaging gate (plan 2026-10-27-001 U1).

A1b (tools/lg_couple_options.py): per row, two identical 6061-T6 tension
fuses either side of the hip pin at the crank radius; the push-side fuse sits
in a 6061 reversing sleeve.  Both members run up-inboard along the canonical
strut line (the extension of the thigh at rest) to anchor bosses inside the
hull, where QMx Sheet 5 [REF-CAD-003] and the Henning renders [REF-CAD-002]
show the strut entering its housing.

For every corner this places, in leg-local XZ (hip at the origin, +X
outboard, +Z up; thigh at rest along STRUT_AZ - 180):
  - 2 rows (ductile y = -ROW_Y, spring y = +ROW_Y) x 2 members (crank at
    +/- CRANK_R perpendicular to the strut line), each a cylinder of
    MEMBER_D from the crank point to REACH along the strut line;
  - an anchor boss of ANCHOR_D x ANCHOR_L at each member's far end.
It transforms the set to the hull frame with the bay generator's corner
transform and reports, per corner and per row:
  - volume inside the keep-outs (wing, tilt brackets, doors, nodes ...);
  - volume inside the hull shell wall (the printed skin);
  - volume outside the hull envelope (must be zero: canonical, protected).
A corner passes when all three are below CLASH_MM3.

Run:  /usr/bin/python3 tools/lg_a1b_packaging.py [--reach MM] [--az DEG]

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, 2026-10-27, per AGENTS.md section 3 AI attribution.
License: MIT (SPDX-License-Identifier: MIT) -- see tools/LICENSE.
"""

from __future__ import annotations

import argparse
import math
import sys

import numpy as np
import trimesh
from manifold3d import Manifold, OpType

import generate_lg_bays as g

cbc, mci, lgbf = g.cbc, g.mci, g.lgbf

CRANK_R = 10.0        # mm, Option A crank radius (study SS4.3)
ROW_Y = 7.0           # mm, ductile / spring rows either side of the leg plane
MEMBER_D = 10.0       # mm, OD 8 sleeve + 1 mm clearance each side
ANCHOR_D, ANCHOR_L = 16.0, 10.0   # mm, anchor boss (spreader O15 + wall)
STRUT_AZ = 154.0      # deg, up-inboard; aft sweep optimum 2026-10-27 (thigh at rest -48 reversed = 132)
REACH = 55.0          # mm, crank point -> anchor; aft sweep optimum 2026-10-27
CLASH_MM3 = 1.0


def az(t):
    return np.array([math.cos(math.radians(t)), 0.0, math.sin(math.radians(t))])


def cyl(p0, p1, d):
    m = trimesh.creation.cylinder(radius=d / 2, segment=[p0, p1], sections=32)
    return mci.to_man(m)


def members(reach, strut_az):
    """Leg-local member + anchor solids, per row."""
    u = az(strut_az)
    n = az(strut_az - 90.0)                       # perpendicular in the swing plane
    rows = {}
    for row, y in (("ductile", -ROW_Y), ("spring", ROW_Y)):
        parts = []
        for s in (+1, -1):
            p0 = s * CRANK_R * n + np.array([0, y, 0])
            p1 = p0 + reach * u
            parts.append(cyl(p0, p1, MEMBER_D))
            parts.append(cyl(p1, p1 + ANCHOR_L * u, ANCHOR_D))
        rows[row] = Manifold.batch_boolean(parts, OpType.Add)
    return rows


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--reach", type=float, default=REACH)
    ap.add_argument("--az", type=float, default=STRUT_AZ)
    a = ap.parse_args(argv)
    src = cbc.as_trimesh(trimesh.load(mci.BLENDER_SRC, process=False), mci.BLENDER_SRC)
    src.merge_vertices()
    env = mci.to_man(mci.extract_envelope(mci.bake(src)))
    hull = mci.to_man(mci.bake(src))
    P = cbc.build()
    keep = Manifold.batch_boolean([P[k]["m"] for k in g.KEEPOUTS], OpType.Add)
    corners = lgbf.parse_corners(lgbf.SCAD)
    local = members(a.reach, a.az)
    ok_all = True
    print(f"A1b packaging: crank r {CRANK_R}, reach {a.reach} mm along az {a.az} deg, "
          f"member O{MEMBER_D}, anchor O{ANCHOR_D}")
    for label, c in corners.items():
        tf = lgbf.corner_tf(c)
        for row, m in local.items():
            w = m.transform(np.asarray(tf)[:3, :4])
            k_v = (w ^ keep).volume()
            h_v = (w ^ hull).volume()
            o_v = (w - env).volume()
            ok = max(k_v, h_v, o_v) < CLASH_MM3
            ok_all &= ok
            print(f"  {'OK  ' if ok else 'FAIL'} {label:9s} {row:8s} keep-outs {k_v:7.1f}  "
                  f"hull wall {h_v:7.1f}  outside hull {o_v:7.1f} mm3")
    print(f"\nRESULT: {'PASS' if ok_all else 'FAIL'}")
    return 0 if ok_all else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
