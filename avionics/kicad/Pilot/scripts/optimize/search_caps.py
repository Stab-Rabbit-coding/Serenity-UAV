#!/usr/bin/env python3
"""search_caps.py — Greedy legal-site search that pulls Pilot bypass caps toward their pins.

Usage:
    python3 search_caps.py <place.json> <out_moves.json> [--only REF,REF,...] [--base moves.json]

``place.json`` is a read-only dump of the board (footprints with side / rotation /
courtyard bbox, pads with net and absolute position).  For each bypass cap (worst
first, the four ISOW HF caps always first), every candidate site on a 0.1 mm grid
within 3 mm of a same-net pin of its IC is tried on both sides at 0° and 90°.  A site
is legal when the cap's courtyard bbox:

* stays ≥ 0.3 mm inside the board edge,
* overlaps no other courtyard on that side by more than 0.015 mm (THT parts and mounting
  holes block both), and keeps its pads clear of every drilled hole (NPTH clips included),
* puts its pads inside the In1 ISO_BAND outline only if the cap is an isolated-domain
  cap, and outside it otherwise.

Score = supply-pad-to-pin distance + 1.0 mm when the cap is on the opposite side from
its IC (two vias plus the board thickness in the loop).  A cap only moves when the
score improves by ≥ 0.2 mm.  The result is written as an eval_placement.py move list;
eval_placement.py's full DRC is the authority on whether it is kept.

Author: Claude Opus 5.5, 2026-10-10.  Owner: sgriffing.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
from __future__ import annotations

import argparse
import json
import math
from typing import Any

from eval_placement import GROUNDS, ISO_HF, TARGETS, in_poly

ISO_NETS = ("GND2_", "VCC2_", "CAN_", "RS485_")
BOTH_SIDES = ("PWR-IN", "H1", "H2", "H3", "H4")
OPPOSITE_PENALTY = 1.0
TOUCH = 0.015      # courtyard contact KiCad DRC accepts (measured: 0.01 mm overlap -> 0 errors)
HOLE_CLEAR = 0.25  # board min hole clearance, pad copper to any drilled hole


def rot_offsets(offs, drot):
    """Rotate pad offsets (KiCad y-down) by a multiple of 90 degrees."""
    out = []
    for dx, dy in offs:
        for _ in range(int(round(drot / 90)) % 4):
            dx, dy = dy, -dx
        out.append((dx, dy))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("place")
    ap.add_argument("out")
    ap.add_argument("--only", default=None)
    ap.add_argument("--base", default=None)
    a = ap.parse_args()
    only = set(a.only.split(",")) if a.only else None
    base = json.load(open(a.base)) if a.base else {"moves": {}}
    d = json.load(open(a.place))
    # band and edge come from the same geometry dump (review finding #6)
    band = [tuple(pt) for pt in base.get("band_outline", d["band"])]
    edge = tuple(d["edge"])
    F = {f["ref"]: f for f in d["fps"]}
    P: dict = {}
    for p in d["pads"]:
        if p["num"]:
            P.setdefault(p["ref"], []).append(p)
    holes = [(p["x"], p["y"], p.get("drill", 0) / 2) for p in d["pads"] if p.get("drill", 0) > 0]
    boxes = {}  # ref -> (side, x1, y1, x2, y2)
    for f in d["fps"]:
        boxes[f["ref"]] = (f["side"], *f["cy"])

    caps = []
    for ref in F:
        ic = next((t for pre, t in TARGETS if ref.startswith(pre)), None)
        if not ref.startswith("C-") or not ic or ic not in P:
            continue
        sig = [p for p in P[ref] if p["net"] not in GROUNDS]
        if not sig or not any(q["net"] == sig[0]["net"] for q in P[ic]):
            continue
        caps.append((ref, ic, sig[0]["net"]))

    def score(ref, ic, net, side, pads):
        sp = next(p for p in pads if p["net"] == net)
        d0 = min(math.hypot(q["x"] - sp["x"], q["y"] - sp["y"]) for q in P[ic] if q["net"] == net)
        return d0 + (OPPOSITE_PENALTY if side != F[ic]["side"] else 0.0)

    def legal(ref, side, box, pads, iso):
        x1, y1, x2, y2 = box
        if x1 < edge[0] + 0.3 or y1 < edge[1] + 0.3 or x2 > edge[2] - 0.3 or y2 > edge[3] - 0.3:
            return False
        for r, (s, a1, b1, a2, b2) in boxes.items():
            if r == ref or (s != side and r not in BOTH_SIDES):
                continue
            if x1 < a2 - TOUCH and a1 < x2 - TOUCH and y1 < b2 - TOUCH and b1 < y2 - TOUCH:
                return False
        for hx, hy, hr in holes:
            for p in pads:
                if math.hypot(p["x"] - hx, p["y"] - hy) < hr + HOLE_CLEAR + 0.35:
                    return False
        for p in pads:
            if in_poly(p["x"], p["y"], band) != iso:
                return False
        return True

    moves = dict(base.get("moves", {}))
    cur_score = {r: score(r, ic, n, F[r]["side"], P[r]) for r, ic, n in caps}
    order = sorted(caps, key=lambda c: (c[0] not in ISO_HF, -cur_score[c[0]]))
    for ref, ic, net in order:
        if only and ref not in only:
            continue
        f = F[ref]
        offs = [(p["x"] - f["x"], p["y"] - f["y"]) for p in P[ref]]
        hw, hh = (f["cy"][2] - f["cy"][0]) / 2, (f["cy"][3] - f["cy"][1]) / 2
        iso = net.startswith(ISO_NETS)
        best: "tuple[Any, Any]" = (cur_score[ref] - 0.2, None)
        targets = [q for q in P[ic] if q["net"] == net]
        for side in ("F", "B"):
            for drot in (0, 90):
                o = rot_offsets(offs, drot)
                w, h = (hw, hh) if drot == 0 else (hh, hw)
                for q in targets:
                    for i in range(-30, 31):
                        for j in range(-30, 31):
                            cx, cy = round(q["x"] + i * 0.1, 2), round(q["y"] + j * 0.1, 2)
                            pads = [dict(net=p["net"], x=cx + dx, y=cy + dy)
                                    for p, (dx, dy) in zip(P[ref], o)]
                            sc = score(ref, ic, net, side, pads)
                            if sc >= best[0]:
                                continue
                            if legal(ref, side, (cx - w, cy - h, cx + w, cy + h), pads, iso):
                                box = (cx - w, cy - h, cx + w, cy + h)
                                best = (sc, (side, drot, cx, cy, pads, box))
        if best[1] is None:
            continue
        side, drot, cx, cy, pads, box = best[1]
        moves[ref] = {"x": cx, "y": cy, "rot": (f["rot"] + drot) % 360, "side": side}
        boxes[ref] = (side, *box)
        P[ref] = [dict(p, x=n["x"], y=n["y"]) for p, n in zip(P[ref], pads)]
        F[ref] = dict(f, x=cx, y=cy, side=side, rot=(f["rot"] + drot) % 360, cy=list(box))
        print(f"{ref:10s} {cur_score[ref]:5.2f} -> {best[0]:5.2f}  {side} rot+{drot} ({cx}, {cy})")
    extra = {"band_outline": base["band_outline"]} if "band_outline" in base else {}
    json.dump({"moves": moves, **extra}, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
