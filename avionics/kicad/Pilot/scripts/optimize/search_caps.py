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
* overlaps no other courtyard on that side (THT parts and mounting holes block both),
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

import json
import math
import sys

from eval_placement import GROUNDS, ISO_HF, TARGETS, in_poly

EDGE = (120.975, 87.475, 176.025, 122.525)
BAND = [(128.3, 105.5), (155.9, 105.5), (155.9, 122.0), (128.3, 122.0)]
ISO_NETS = ("GND2_", "VCC2_", "CAN_", "RS485_")
BOTH_SIDES = ("PWR-IN", "H1", "H2", "H3", "H4")
OPPOSITE_PENALTY = 1.0


def rot_offsets(offs, drot):
    """Rotate pad offsets (KiCad y-down) by a multiple of 90 degrees."""
    out = []
    for dx, dy in offs:
        for _ in range(int(round(drot / 90)) % 4):
            dx, dy = dy, -dx
        out.append((dx, dy))
    return out


def main() -> None:
    args = sys.argv[1:]
    only = None
    base = {"moves": {}}
    if "--only" in args:
        only = set(args[args.index("--only") + 1].split(","))
    if "--base" in args:
        base = json.load(open(args[args.index("--base") + 1]))
    band = [tuple(pt) for pt in base.get("band_outline", BAND)]
    d = json.load(open(args[0]))
    F = {f["ref"]: f for f in d["fps"]}
    P: dict = {}
    for p in d["pads"]:
        if p["num"]:
            P.setdefault(p["ref"], []).append(p)
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
        if x1 < EDGE[0] + 0.3 or y1 < EDGE[1] + 0.3 or x2 > EDGE[2] - 0.3 or y2 > EDGE[3] - 0.3:
            return False
        for r, (s, a1, b1, a2, b2) in boxes.items():
            if r == ref or (s != side and r not in BOTH_SIDES):
                continue
            if x1 < a2 and a1 < x2 and y1 < b2 and b1 < y2:
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
        best = (cur_score[ref] - 0.2, None)
        targets = [q for q in P[ic] if q["net"] == net]
        for side in ("F", "B"):
            for drot in (0, 90):
                o = rot_offsets(offs, drot)
                w, h = (hw, hh) if drot == 0 else (hh, hw)
                for q in targets:
                    for i in range(-30, 31):
                        for j in range(-30, 31):
                            cx, cy = round(q["x"] + i * 0.1, 2), round(q["y"] + j * 0.1, 2)
                            pads = [dict(net=p["net"], x=cx + dx, y=cy + dy) for p, (dx, dy) in zip(P[ref], o)]
                            sc = score(ref, ic, net, side, pads)
                            if sc >= best[0]:
                                continue
                            if legal(ref, side, (cx - w, cy - h, cx + w, cy + h), pads, iso):
                                best = (sc, (side, drot, cx, cy, pads, (cx - w, cy - h, cx + w, cy + h)))
        if best[1] is None:
            continue
        side, drot, cx, cy, pads, box = best[1]
        moves[ref] = {"x": cx, "y": cy, "rot": (f["rot"] + drot) % 360, "side": side}
        boxes[ref] = (side, *box)
        P[ref] = [dict(p, x=n["x"], y=n["y"]) for p, n in zip(P[ref], pads)]
        F[ref] = dict(f, x=cx, y=cy, side=side, rot=(f["rot"] + drot) % 360, cy=list(box))
        print(f"{ref:10s} {cur_score[ref]:5.2f} -> {best[0]:5.2f}  {side} rot+{drot} ({cx}, {cy})")
    json.dump({"moves": moves, **({"band_outline": base["band_outline"]} if "band_outline" in base else {})},
              open(args[1], "w"), indent=1)


if __name__ == "__main__":
    main()
