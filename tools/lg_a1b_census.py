#!/usr/bin/python3
"""LG Option A1b 3-D census: rendered members + CF backbone vs hull, keep-outs, leg.

Renders a1b_members(0), a1b_members(FLEX_DEG) and a1b_backbone() from
airframe/openscad/fuselage/canonical_leg_r6_3_0in.scad per corner, places
them with the bay generator's corner transform, and measures overlap with
the published merged cargo shell (wells cut), the keep-out solids and the
swept leg, and checks that the A1B constants restated in the sizing and
packaging tools equal the SCAD's.  This is the AUTHORITATIVE A1B packaging
gate (tools/lg_a1b_packaging.py is the exploratory sweep that chose the
azimuths).  Only the hull-wall test masks the hip (r 12 mm: the crank ends sit
in the open well by design); keep-outs and the swept leg are measured
unmasked.  Exit 2 on any overlap above CLASH_MM3 or any parity drift.
Plan 2026-10-27-001 U1/U3.

Run:  /usr/bin/python3 tools/lg_a1b_census.py   (from the repo root or tools/)

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, 2026-10-27, per AGENTS.md section 3 AI attribution.
License: MIT (SPDX-License-Identifier: MIT) -- see tools/LICENSE.
"""
import os
import re
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
CLASH_MM3 = 1.0       # mm^3, any overlap above this FAILS the gate
HIP_MASK_R = 12.0     # mm, hull-wall test only: the crank ends sit in the open well


def scad_param(name: str) -> str:
    """Raw right-hand side of a top-level `NAME = ...;` in the leg SCAD."""
    with open(lgbf.SCAD, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(rf"\s*{name}\s*=\s*([^;]+);", line)
            if m:
                return m.group(1).strip()
    raise KeyError(name)


def parity() -> list[str]:
    """A1B constants restated in the tools must equal the SCAD's."""
    import landing_gear_r6_sizing as sz
    import lg_a1b_packaging as pk
    bad = []
    checks = (("A1B_CRANK_R", float(scad_param("A1B_CRANK_R")), sz.A1B_CRANK_R),
              ("A1B_CRANK_R (packaging)", float(scad_param("A1B_CRANK_R")), pk.CRANK_R),
              ("A1B_ROW_Y (packaging)", float(scad_param("A1B_ROW_Y")), pk.ROW_Y),
              ("A1B_REACH (packaging)", float(scad_param("A1B_REACH")), pk.REACH),
              ("FLEX_DEG (sizing)", float(scad_param("FLEX_DEG")), sz.A1B_FLEX_DEG))
    for name, a, b in checks:
        if abs(a - b) > 1e-6:
            bad.append(f"{name}: SCAD {a} vs tool {b}")
    az = scad_param("A1B_STRUT_AZ")
    for st, val in pk.STRUT_AZ.items():
        if str(int(val)) not in az:
            bad.append(f"A1B_STRUT_AZ[{st}] {val} not in SCAD '{az}'")
    return bad


def main() -> int:
    """Print overlaps per corner/part; return 2 on any clash or parity drift."""
    fails = parity()
    for f in fails:
        print("PARITY FAIL", f)
    pub = trimesh.load(SHELL, process=False)
    pub.merge_vertices()
    hull = cbc.man(pub)
    solids = cbc.build()
    keep = Manifold.batch_boolean([solids[k]["m"] for k in g.KEEPOUTS], OpType.Add)
    corners = lgbf.parse_corners(lgbf.SCAD)
    mask = mci.to_man(trimesh.creation.icosphere(subdivisions=3, radius=HIP_MASK_R))
    for label, c in corners.items():
        st = "fore" if label.startswith("fore") else "aft"
        tf = lgbf.corner_tf(c)
        mk = mask.transform(np.asarray(tf)[:3, :4])
        leg_path = lgbf.render(lgbf.SCAD, st, "leg (thigh+shin+foot)",
                               lgbf.FEATURES["leg (thigh+shin+foot)"][0])
        leg = lgbf.swept_leg(leg_path, tf)
        for name, expr in PARTS:
            w = lgbf.posed(lgbf.render(lgbf.SCAD, st, name, expr), tf)
            v = {"hull": ((w - mk) ^ hull).volume(), "keep": (w ^ keep).volume()}
            if name == "a1b backbone":
                v["swept leg"] = (w ^ leg).volume()
            bad = {k: x for k, x in v.items() if x > CLASH_MM3}
            if bad:
                fails.append(f"{label} {name} {bad}")
            print(f"{'FAIL' if bad else 'OK  '} {label:9s} {name:17s} "
                  + "  ".join(f"{k} {x:7.1f}" for k, x in v.items()) + " mm3")
    print(f"\nRESULT: {'FAIL' if fails else 'PASS'}")
    return 2 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
