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
pub = trimesh.load(os.path.join(HERE, "..", "airframe", "stls", "fuselage", "cargo", "cargo_sect_shell24_2mm_repaired.stl"), process=False); pub.merge_vertices()
hull = cbc.man(pub)
P = cbc.build(); keep = Manifold.batch_boolean([P[k]["m"] for k in g.KEEPOUTS], OpType.Add)
corners = lgbf.parse_corners(lgbf.SCAD)
mask = mci.to_man(trimesh.creation.icosphere(subdivisions=3, radius=12.0))
for label, c in corners.items():
    st = "fore" if label.startswith("fore") else "aft"
    Tf = lgbf.corner_tf(c); T = np.asarray(Tf)[:3, :4]; mk = mask.transform(T)
    parts = {n: lgbf.posed(lgbf.render(lgbf.SCAD, st, n, e), Tf) for n, e in
             (("a1b members rest", "a1b_members(0);"), ("a1b members flex", "a1b_members(FLEX_DEG);"),
              ("a1b backbone", "a1b_backbone();"))}
    leg = lgbf.swept_leg(lgbf.render(lgbf.SCAD, st, "leg (thigh+shin+foot)", lgbf.FEATURES["leg (thigh+shin+foot)"][0]), Tf)
    for n, m in parts.items():
        w = m - mk
        print(f"{label:9s} {n:17s} hull {(w ^ hull).volume():7.1f}  keep {(w ^ keep).volume():7.1f}"
              + (f"  swept leg {(w ^ leg).volume():7.1f}" if n == "a1b backbone" else "") + " mm3")
