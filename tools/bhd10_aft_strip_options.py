#!/usr/bin/python3
"""BHD-10 option study: the Pilot FC2/FC3 aft-strip nodes vs the splice collar.

BHD-10 (docs/CARGO_BULKHEAD_FIT_CHECK.md): the two Pilot nodes (FC2 port,
FC3 starboard; Faraday-pouched PocketBeagle 2 + cape, 58 x 22 x 37 mm, from
tools/cargo_layout_fit.py) and their cable zones reach 0.5 mm into the
cargo/middle splice collar (22 / 24 / 19 / 19 mm^3).  The overlap is ONLY at
each node's upper-OUTBOARD corner -- the collar ring follows the skin -- not
across the face.  Moving the pair forward 2.5 mm was said to hit the tilt
controller boards.  The owner asked for pictures of the options; this tool
builds each one in context and reports every overlap, the same way the
bulkhead gate does (it reuses tools/cargo_bulkhead_context.py's solids):

O1  shift the aft pair forward by the 2 mm static gap + 0.5 mm (Y -2.5);
O2  relieve the collar's cargo-side ring locally behind each corner (pocket =
    node corner + 2 mm static gap), and report what bonded-ring volume the
    relief costs against the whole cargo-side bond band (Y 121..129);
O3  a thinner pouched stack (NODE_T 22 -> 19.5, i.e. 2.5 mm less), legal only
    if the first-article stack measures that (cargo_layout_fit.py marks the
    22 mm figure VERIFY).

Every option is checked against every context solid; "near" counts solids
within the 2 mm static gap the layout tool demands of fixed parts.

Run:  /usr/bin/python3 tools/bhd10_aft_strip_options.py [--export DIR] [--json OUT]

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, per AGENTS.md AI attribution.
License: MIT (SPDX-License-Identifier: MIT) -- see tools/LICENSE.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

import numpy as np
from manifold3d import Manifold

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cargo_bulkhead_context as cbc  # noqa: E402

GAP = 2.0                       # static gap, cargo_layout_fit.py node gap=2.0
SHIFT = GAP + 0.5               # O1: restore the gap from 0.5 mm interference
SIDE_PAD = 5.0                  # O2: lateral margin of the collar pocket
THIN = 2.5                      # O3: stack reduction that restores the gap
NODES = ("Pilot FC2 port", "Pilot FC3 stbd", "Pilot FC2 cable zone",
         "Pilot FC3 cable zone")
COLLAR = "collar cargo-middle"
BAND_Y = (121.0, 129.0)         # collar ring zone inside the cargo section


def bb(m: Manifold) -> np.ndarray:
    return np.array(m.bounding_box()).reshape(2, 3)


def box(lo, hi) -> Manifold:
    lo, hi = np.asarray(lo, float), np.asarray(hi, float)
    return Manifold.cube(list(hi - lo)).translate(list(lo))


def census(P: dict, moved: dict[str, Manifold], skip=()) -> list[dict]:
    """Every overlap and near-miss of the moved solids with the context."""
    rows = []
    for n, m in moved.items():
        for t, e in P.items():
            if t in moved or t in skip or t == n or t.startswith(("door", "Pilot")):
                continue
            tm = e["m"]
            if np.any(bb(tm)[0] > bb(m)[1] + GAP) or np.any(bb(m)[0] > bb(tm)[1] + GAP):
                continue
            v = (m ^ tm).volume()
            gap = 0.0 if v > 0.05 else m.min_gap(tm, GAP)
            if v > 0.05 or gap < GAP:
                rows.append(dict(part=n, target=t, mm3=round(v, 1),
                                 gap_mm=round(gap, 2),
                                 verdict="CLASH" if v > 0.05 else "near"))
    return rows


def option_rows(P: dict, export: str | None) -> dict:
    out: dict[str, Any] = {}
    base = {n: P[n]["m"] for n in NODES}
    out["baseline"] = census(P, base)
    o1 = {n: m.translate([0, -SHIFT, 0]) for n, m in base.items()}
    out["O1 shift fwd 2.5"] = census(P, o1)
    # O2 -- collar relief behind each node corner
    col = P[COLLAR]["m"]
    relief = None
    for n in NODES:
        c = base[n] ^ col
        if c.volume() <= 0.05:
            continue
        lo, hi = bb(c)
        # depth = 2 mm static gap behind the node face; the sides get more,
        # because the ring is curved and a 2 mm side pad left 0.42 mm (measured)
        r = box(lo - [SIDE_PAD, 0.0, SIDE_PAD], hi + [SIDE_PAD, GAP, SIDE_PAD])
        relief = r if relief is None else relief + r
    col2 = col - relief
    band = col ^ box([-400, BAND_Y[0], -100], [100, BAND_Y[1], 300])
    removed = (col ^ relief).volume()
    P2 = dict(P)
    P2[COLLAR] = dict(P[COLLAR], m=col2)
    out["O2 collar relief"] = census(P2, base)
    out["O2 collar relief cost"] = dict(
        removed_mm3=round(removed, 1), band_mm3=round(band.volume(), 1),
        band_loss_pct=round(100 * removed / band.volume(), 2),
        bodies_after=len(col2.decompose()))
    # O3 -- thinner stack (aft face moves forward, front face fixed)
    o3 = {}
    for n, m in base.items():
        lo, hi = bb(m)
        o3[n] = m ^ box(lo - 1, [hi[0] + 1, hi[1] - THIN, hi[2] + 1])
    out["O3 stack -2.5"] = census(P, o3)
    if export:
        os.makedirs(export, exist_ok=True)
        for tag, sol in (("base", base), ("O1", o1), ("O3", o3)):
            for n, m in sol.items():
                cbc.tri(m).export(os.path.join(export, f"{tag}_{n.replace(' ', '_')}.stl"))
        cbc.tri(col2).export(os.path.join(export, "O2_collar_relieved.stl"))
        cbc.tri(col ^ relief).export(os.path.join(export, "O2_collar_removed.stl"))
        cbc.tri(col).export(os.path.join(export, "collar.stl"))
        for t in ("tilt controller board port", "tilt controller board stbd",
                  "tilt bracket port", "tilt bracket stbd", "battery cradle"):
            cbc.tri(P[t]["m"]).export(os.path.join(export, f"ctx_{t.replace(' ', '_')}.stl"))
        for tag, sol in (("base", base), ("O1", o1)):
            for n, m in sol.items():
                for t in ("tilt controller board port", "tilt controller board stbd", COLLAR):
                    c = m ^ P[t]["m"]
                    if c.volume() > 0.05:
                        cbc.tri(c).export(os.path.join(
                            export, f"CLASH_{tag}_{n.replace(' ', '_')}_{t.replace(' ', '_')}.stl"))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--export", help="write option solids here (for the renders)")
    ap.add_argument("--json", help="write the study as JSON")
    a = ap.parse_args()
    R = option_rows(cbc.build(), a.export)
    for k, v in R.items():
        print(f"\n== {k}")
        if isinstance(v, dict):
            print("  ", v)
            continue
        for r in sorted(v, key=lambda r: (r["verdict"], -r["mm3"], r["gap_mm"])):
            print(f"  {r['verdict']:5s} {r['part']:22s} x {r['target']:32s} "
                  f"{r['mm3']:7.1f} mm3  gap {r['gap_mm']:.2f}")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(R, fh, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
