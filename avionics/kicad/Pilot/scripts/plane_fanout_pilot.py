#!/usr/bin/env python3
"""plane_fanout_pilot.py — Drop a plane via beside every unconnected plane-net pad.

Usage:
    python3 plane_fanout_pilot.py <board.kicad_pcb>

Pilot's inner layers carry the GND plane and the GND2_CAN / GND2_RS485 islands
(In1.Cu) and the +3V3 plane (In4.Cu).  A pad on one of those nets that DRC still
reports unconnected only needs a 0.6/0.3 mm through via next to it plus a short
0.25 mm stub on the pad's layer; the zone fill makes the rest of the connection.

Method (same intent as ``plane_fanout`` in ../../TACCO/scripts/finish_tacco_pcb.py,
reworked because the KiCad 9.0.2 SWIG binding returns unwrapped objects once
geometry calls are made — see avionics/kicad/PCBNEW_SWIG_BUG.md):

1. Read-only pcbnew pass: pad and track geometry only (positions, bounding boxes,
   widths, nets).  No polygon calls, nothing saved through pcbnew.
2. ``kicad-cli pcb drc`` lists the unconnected plane-net pads.
3. For each such pad, try 16 directions at (pad half-extent + via radius + 0.15 mm),
   stepping outward to +1.0 mm, with the stub also clearance-checked,
   and take the first site whose via keeps ≥ 0.25 mm to other-net copper and
   ≥ 0.8 mm centre spacing to other drills, inside the board edge less 0.9 mm.
   Logic-net (GND / +3V3) vias stay outside the ISO_BAND In1 outline and GND2_*
   vias inside it, both ≥ 0.85 mm from its boundary (0.5 mm cross-domain moat).
4. The vias and stubs are appended to the S-expression text; the zones are
   refilled by ``kicad-cli`` and ``repair_pilot_routing.py`` then rips anything
   the project DRC still rejects.

Author: Claude Opus 5.5, 2026-10-10.  Owner: sgriffing.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

import pcbnew  # type: ignore

PLANE_NETS = {"GND", "+3V3", "GND2_CAN", "GND2_RS485"}
ISO_NETS = {"GND2_CAN", "GND2_RS485"}
VIA_D, VIA_DRILL, STUB_W = 0.6, 0.3, 0.25
CLEAR = 0.25          # via edge to other-net copper, mm (board min 0.127; margin for stubs)
DRILL_PITCH = 0.8     # via centre to any other drill centre, mm (min_hole_to_hole 0.5 + 0.3)


def geometry(pcb: str) -> dict:
    """Read-only extraction of pads, tracks, vias, board edge and ISO_BAND box (mm)."""
    b = pcbnew.LoadBoard(pcb)
    s = 1e6
    pads = []
    for p in b.GetPads():
        bb = p.GetBoundingBox()
        pads.append(dict(net=p.GetNetname(), x=p.GetPosition().x / s, y=p.GetPosition().y / s,
                         x1=bb.GetX() / s, y1=bb.GetY() / s, x2=(bb.GetX() + bb.GetWidth()) / s,
                         y2=(bb.GetY() + bb.GetHeight()) / s,
                         back=p.IsOnLayer(pcbnew.B_Cu) and not p.IsOnLayer(pcbnew.F_Cu),
                         drill=p.GetDrillSize().x / s, ref=p.GetParentFootprint().GetReference(),
                         num=p.GetNumber()))
    segs, vias = [], []
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            vias.append(dict(net=t.GetNetname(), x=t.GetPosition().x / s, y=t.GetPosition().y / s,
                             r=t.GetWidth(pcbnew.F_Cu) / s / 2))
        else:
            segs.append(dict(net=t.GetNetname(), x1=t.GetStart().x / s, y1=t.GetStart().y / s,
                             x2=t.GetEnd().x / s, y2=t.GetEnd().y / s, w=t.GetWidth() / s))
    e = b.GetBoardEdgesBoundingBox()
    band = []
    for z in b.Zones():
        if z.GetIsRuleArea() and z.GetZoneName() == "ISO_BAND" and z.IsOnLayer(pcbnew.In1_Cu):
            ol = z.Outline().Outline(0)
            band.append([(ol.CPoint(i).x / s, ol.CPoint(i).y / s) for i in range(ol.PointCount())])
    netcodes = {n: b.FindNet(n).GetNetCode() for n in PLANE_NETS}
    return dict(pads=pads, segs=segs, vias=vias, netcodes=netcodes,
                edge=(e.GetX() / s, e.GetY() / s,
                      (e.GetX() + e.GetWidth()) / s, (e.GetY() + e.GetHeight()) / s),
                band=band)


def seg_dist(px, py, x1, y1, x2, y2) -> float:
    dx, dy = x2 - x1, y2 - y1
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def box_dist(px, py, x1, y1, x2, y2) -> float:
    return math.hypot(max(x1 - px, 0, px - x2), max(y1 - py, 0, py - y2))


def in_poly(x: float, y: float, poly: list) -> bool:
    """Even-odd ray test."""
    inside, n = False, len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def band_margin(x: float, y: float, g: dict) -> "tuple[bool, float]":
    """(inside the In1 ISO_BAND outline, distance to its boundary) in mm."""
    inside = any(in_poly(x, y, p) for p in g["band"])
    d = min(seg_dist(x, y, *p[i], *p[(i + 1) % len(p)]) for p in g["band"] for i in range(len(p)))
    return inside, d


def stub_ok(g: dict, net: str, x1: float, y1: float, x2: float, y2: float, back: bool) -> bool:
    """Stub keeps STUB_W/2 + 0.15 mm to other-net pads/tracks (sampled every 0.05 mm)."""
    n = max(2, int(math.hypot(x2 - x1, y2 - y1) / 0.05))
    need = STUB_W / 2 + 0.15
    for k in range(n + 1):
        px, py = x1 + (x2 - x1) * k / n, y1 + (y2 - y1) * k / n
        for p in g["pads"]:
            if p["net"] != net and box_dist(px, py, p["x1"], p["y1"], p["x2"], p["y2"]) < need:
                return False
        for t in g["segs"]:
            d = seg_dist(px, py, t["x1"], t["y1"], t["x2"], t["y2"])
            if t["net"] != net and d < need + t["w"] / 2:
                return False
    return True


def site_ok(g: dict, net: str, vx: float, vy: float, placed: list) -> bool:
    ex1, ey1, ex2, ey2 = g["edge"]
    if not (ex1 + 0.9 < vx < ex2 - 0.9 and ey1 + 0.9 < vy < ey2 - 0.9):
        return False
    inside, margin = band_margin(vx, vy, g)
    if (net in ISO_NETS) != inside or margin < VIA_D / 2 + 0.55:
        return False  # 0.5 mm cross-domain moat + rounding
    r = VIA_D / 2
    for p in g["pads"]:
        d = box_dist(vx, vy, p["x1"], p["y1"], p["x2"], p["y2"])
        if p["net"] != net and d < r + CLEAR:
            return False
        if p["drill"] > 0 and math.hypot(vx - p["x"], vy - p["y"]) < DRILL_PITCH + p["drill"] / 2:
            return False
    for t in g["segs"]:
        d = seg_dist(vx, vy, t["x1"], t["y1"], t["x2"], t["y2"])
        if t["net"] != net and d < r + t["w"] / 2 + CLEAR:
            return False
    for v in g["vias"] + placed:
        keep = r + v["r"] + CLEAR if v["net"] != net else 0
        if math.hypot(vx - v["x"], vy - v["y"]) < max(DRILL_PITCH, keep):
            return False
    return True


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    pcb = Path(sys.argv[1])
    g = geometry(str(pcb))
    out = Path(tempfile.mkdtemp()) / "drc.json"
    subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "--output", str(out), str(pcb)],
                   check=True, capture_output=True)
    want = set()
    for u in json.loads(out.read_text())["unconnected_items"]:
        for it in u["items"]:
            m = re.match(r"Pad (\S+) \[([^\]]+)\] of (\S+)", it["description"])
            if m and m.group(2) in PLANE_NETS:
                want.add((m.group(3), m.group(1), m.group(2)))
    placed: list = []
    blocks: list = []
    skipped: list = []
    for p in g["pads"]:
        if (p["ref"], p["num"], p["net"]) not in want or p["drill"] > 0:
            continue
        half = max(p["x2"] - p["x1"], p["y2"] - p["y1"]) / 2
        sites = [(half + VIA_D / 2 + 0.15 + step, k * math.pi / 8)
                 for step in (0.0, 0.25, 0.5, 0.75, 1.0) for k in range(16)]
        for reach, a in sites:
            vx, vy = round(p["x"] + reach * math.cos(a), 4), round(p["y"] + reach * math.sin(a), 4)
            if site_ok(g, p["net"], vx, vy, placed) and \
                    stub_ok(g, p["net"], p["x"], p["y"], vx, vy, p["back"]):
                placed.append(dict(net=p["net"], x=vx, y=vy, r=VIA_D / 2))
                code = g["netcodes"][p["net"]]
                layer = "B.Cu" if p["back"] else "F.Cu"
                blocks.append(f'\t(via\n\t\t(at {vx} {vy})\n\t\t(size {VIA_D})\n'
                              f'\t\t(drill {VIA_DRILL})\n\t\t(layers "F.Cu" "B.Cu")\n'
                              f'\t\t(net {code})\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n')
                blocks.append(f'\t(segment\n\t\t(start {p["x"]} {p["y"]})\n\t\t(end {vx} {vy})\n'
                              f'\t\t(width {STUB_W})\n\t\t(layer "{layer}")\n\t\t(net {code})\n'
                              f'\t\t(uuid "{uuid.uuid4()}")\n\t)\n')
                break
        else:
            skipped.append(f'{p["ref"]}.{p["num"]} [{p["net"]}]')
    text = pcb.read_text()
    i = text.index("\n\t(zone\n") + 1  # top-level zones only; KiCad writes routing before them
    pcb.write_text(text[:i] + "".join(blocks) + text[i:])
    print(f"plane vias placed: {len(placed)} of {len(want)} unconnected plane-net pads")
    if skipped:
        print("no free site:", ", ".join(skipped))


if __name__ == "__main__":
    main()
