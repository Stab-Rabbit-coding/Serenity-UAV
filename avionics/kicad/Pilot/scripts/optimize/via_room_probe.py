#!/usr/bin/env python3
"""via_room_probe.py — How many GND/+3V3 plane pads can get a plane via, under two rule sets.

Usage:
    python3 via_room_probe.py <place.json> [--reach MM]

Answers ideation idea 9 ("put vias where the courtyards are") with a number instead of
an argument.  For every SMD pad on GND or +3V3 it searches for a 0.6/0.3 mm through-via
site within ``--reach`` mm (default 2.5) of the pad centre, under two rule sets:

* ``courtyard``  — the site must lie outside every footprint courtyard on BOTH sides
  (what plane_fanout_pilot.py effectively required);
* ``copper``     — the site only needs 0.127 mm (via edge) to other-net pad copper on
  either outer layer, 0.25 mm to any drilled hole, 0.5 mm hole-to-hole spacing to
  other sites, and must sit outside the In1 ISO_BAND outline.

Pad copper is approximated by a 0.35 mm-radius disc for 0201/0402 lands and by the pad
centre plus 0.6 mm for everything else (conservative for fine-pitch QFN pads).  Routed
tracks are ignored: the probe runs on the routing-stripped placement and measures room,
not a finished fanout.  Prints JSON.

Author: Claude Opus 5.5, 2026-10-10.  Owner: sgriffing.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
from __future__ import annotations

import json
import math
import sys

from eval_placement import in_poly

VIA_R = 0.3
EDGE = (120.975, 87.475, 176.025, 122.525)


def main() -> None:
    d = json.load(open(sys.argv[1]))
    reach = float(sys.argv[sys.argv.index("--reach") + 1]) if "--reach" in sys.argv else 2.5
    band = [(128.3, 111.0), (137.6, 111.0), (137.6, 105.5), (155.9, 105.5), (155.9, 122.0), (128.3, 122.0)]
    fp = {f["ref"]: f for f in d["fps"]}
    small = {r for r, f in fp.items() if "0201" in f["fp"] or "0402" in f["fp"]}
    copper = [(p["x"], p["y"], 0.35 if p["ref"] in small else 0.6, p["net"]) for p in d["pads"] if p["num"]]
    holes = [(p["x"], p["y"], p["drill"] / 2) for p in d["pads"] if p.get("drill", 0) > 0]
    boxes = [f["cy"] for f in d["fps"]]
    plane = [p for p in d["pads"] if p["net"] in ("GND", "+3V3") and p["num"] and not p.get("drill")
             and not p["ref"].startswith(("PB2-", "H"))]

    def ok(x, y, net, mode, placed):
        if not (EDGE[0] + 0.6 < x < EDGE[2] - 0.6 and EDGE[1] + 0.6 < y < EDGE[3] - 0.6):
            return False
        if in_poly(x, y, band):
            return False
        if any(math.hypot(x - a, y - b) < 0.8 for a, b in placed):
            return False
        if any(math.hypot(x - hx, y - hy) < hr + 0.25 + VIA_R for hx, hy, hr in holes):
            return False
        if mode == "courtyard":
            return not any(c[0] - VIA_R < x < c[2] + VIA_R and c[1] - VIA_R < y < c[3] + VIA_R for c in boxes)
        return all(n == net or math.hypot(x - cx, y - cy) >= r + VIA_R + 0.127 for cx, cy, r, n in copper)

    out = {"plane_pads": len(plane), "reach_mm": reach}
    for mode in ("courtyard", "copper"):
        placed, found = [], 0
        for p in plane:
            best = None
            for i in range(-25, 26):
                for j in range(-25, 26):
                    x, y = p["x"] + i * 0.1, p["y"] + j * 0.1
                    dd = math.hypot(x - p["x"], y - p["y"])
                    if dd > reach or (best and dd >= best[0]):
                        continue
                    if ok(x, y, p["net"], mode, placed):
                        best = (dd, x, y)
            if best:
                found += 1
                placed.append((best[1], best[2]))
        out[f"sites_{mode}"] = found
    print(json.dumps(out))


if __name__ == "__main__":
    main()
