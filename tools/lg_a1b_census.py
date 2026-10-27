#!/usr/bin/python3
"""LG Option A1b 3-D census: rendered members + CF backbone vs hull, keep-outs, leg.

Renders a1b_members(0), a1b_members(FLEX_DEG) and a1b_backbone() from
airframe/openscad/fuselage/canonical_leg_r6_3_0in.scad per corner, places
them with the bay generator's corner transform, and measures overlap with
the published merged cargo shell (wells cut), the keep-out solids and the
swept leg.  The hip region (r 12 mm) is masked: the members' crank ends sit
in the open well by design.  Plan 2026-10-27-001 U1/U3.

Run:  /usr/bin/python3 tools/lg_a1b_census.py   (from the repo root or tools/)

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, 2026-10-27, per AGENTS.md section 3 AI attribution.
License: MIT (SPDX-License-Identifier: MIT) -- see tools/LICENSE.
"""
import os
import sys

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generate_lg_bays as g  # noqa: E402
from manifold3d import Manifold, OpType  # noqa: E402
mci, cbc, lgbf = g.mci, g.cbc, g.lgbf

SHELL = os.path.join(HERE, "..", "airframe", "stls", "fuselage", "cargo",
                     "cargo_sect_shell24_2mm_repaired.stl")
PARTS = (("a1b members rest", "a1b_members(0);"),
         ("a1b members flex", "a1b_members(FLEX_DEG);"),
         ("a1b backbone", "a1b_backbone();"))


def main() -> int:
    """Print overlap volumes per corner and part; return 0."""
    pub = trimesh.load(SHELL, process=False)
    pub.merge_vertices()
    hull = cbc.man(pub)
    solids = cbc.build()
    keep = Manifold.batch_boolean([solids[k]["m"] for k in g.KEEPOUTS], OpType.Add)
    corners = lgbf.parse_corners(lgbf.SCAD)
    mask = mci.to_man(trimesh.creation.icosphere(subdivisions=3, radius=12.0))
    for label, c in corners.items():
        st = "fore" if label.startswith("fore") else "aft"
        tf = lgbf.corner_tf(c)
        mk = mask.transform(np.asarray(tf)[:3, :4])
        leg_path = lgbf.render(lgbf.SCAD, st, "leg (thigh+shin+foot)",
                               lgbf.FEATURES["leg (thigh+shin+foot)"][0])
        leg = lgbf.swept_leg(leg_path, tf)
        for name, expr in PARTS:
            w = lgbf.posed(lgbf.render(lgbf.SCAD, st, name, expr), tf) - mk
            line = (f"{label:9s} {name:17s} hull {(w ^ hull).volume():7.1f}  "
                    f"keep {(w ^ keep).volume():7.1f}")
            if name == "a1b backbone":
                line += f"  swept leg {(w ^ leg).volume():7.1f}"
            print(line + " mm3")
    return 0


if __name__ == "__main__":
    sys.exit(main())
