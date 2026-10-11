#!/usr/bin/env python3
"""grid_route_pilot.py — Rule-aware grid router for Pilot's remaining unconnected items.

Usage:
    python3 grid_route_pilot.py <board.kicad_pcb> [--res 0.05] [--max N] [--only NET,NET]

Freerouting 2.2.4 hangs whenever the board already carries copper (see Pilot.md
"Routing status"), so the last connections are placed one at a time by this script,
the scripted equivalent of hand routing:

1. Read copper geometry read-only through pcbnew (pads by bounding box, tracks as
   capsules, vias as discs, drilled holes, board edge, ISO_BAND outlines).  No pcbnew
   geometry edits (the 9.0.2 SWIG binding is unreliable for them).
2. Read the unconnected pairs from ``kicad-cli pcb drc``.
3. For each pair run A* on a grid over the four routing layers (F.Cu, In2.Cu, In3.Cu,
   B.Cu) with through vias as layer changes.  Plane nets (GND, +3V3) only need a legal
   via site: In1 is the GND plane and In4 the +3V3 plane outside the band.
4. Append the tracks and vias to the board text, then let repair_pilot_routing.py strip
   anything DRC rejects.

Rules applied (Pilot.kicad_pro / Pilot.kicad_dru / zone keep-outs):
* 0.127 mm clearance; 0.5 mm between ISOLATION-class and other copper (X2Y exempt);
  copper-to-edge 0.3 mm; hole clearance 0.25 mm; hole-to-hole 0.5 mm; vias 0.6/0.3.
* ISOLATION nets: tracks only inside ISO_BAND, and since the In2-In4 band keep-outs
  forbid tracks AND vias, only on F.Cu, with no vias.
* Logic nets: no track or via inside ISO_BAND on F/In1-In4; B.Cu is free except the two
  small B.Cu band rectangles.  PGND is exempt from the band rule but not the keep-outs.
Track widths: 0.127 mm signals, 0.2 mm power/plane stubs, 0.2 mm isolation nets.

Author: Claude Opus 5.5, 2026-10-11.  Owner: sgriffing.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
from __future__ import annotations

import argparse
import heapq
import json
import math
import re
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

import numpy as np
from scipy.ndimage import distance_transform_edt

LAYERS = ["F.Cu", "In2.Cu", "In3.Cu", "B.Cu"]
CLR, ISO_CLR, EDGE_CLR, HOLE_CLR, HOLE_HOLE = 0.127, 0.5, 0.3, 0.25, 0.5
VIA_D, VIA_DRILL = 0.6, 0.3
CORNER_R = 3.0         # board corner radius, mm (Edge.Cuts gr_arc)
VIA_COST = 2.0          # mm-equivalent penalty per layer change
ISO_RE = re.compile(r"^(GND2_|VCC2_|CAN_|RS485_)")
PLANES = {"GND": "In1.Cu", "+3V3": "In4.Cu"}
POWER = {"GND", "+3V3", "+5V", "+5V_IN", "PGND"}
EXEMPT = ("X2Y-CAN", "X2Y-RS485")


def geometry(pcb: Path) -> dict:
    code = f"""
import json, pcbnew
b = pcbnew.LoadBoard({str(pcb)!r}); s = 1e6
L = {{pcbnew.F_Cu: "F.Cu", pcbnew.In2_Cu: "In2.Cu", pcbnew.In3_Cu: "In3.Cu", pcbnew.B_Cu: "B.Cu"}}
pads = []
for p in b.GetPads():
    bb = p.GetBoundingBox()
    pads.append(dict(net=p.GetNetname(), ref=p.GetParentFootprint().GetReference(),
        layers=[n for k, n in L.items() if p.IsOnLayer(k)], drill=p.GetDrillSize().x / s,
        x=p.GetPosition().x / s, y=p.GetPosition().y / s,
        box=[bb.GetX() / s, bb.GetY() / s,
             (bb.GetX() + bb.GetWidth()) / s, (bb.GetY() + bb.GetHeight()) / s]))
tracks, vias = [], []
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T:
        vias.append(dict(net=t.GetNetname(), x=t.GetPosition().x / s, y=t.GetPosition().y / s,
                         r=t.GetWidth(pcbnew.F_Cu) / s / 2, drill=t.GetDrillValue() / s))
    else:
        tracks.append(dict(net=t.GetNetname(), layer=pcbnew.LayerName(t.GetLayer()),
                           x1=t.GetStart().x / s, y1=t.GetStart().y / s, x2=t.GetEnd().x / s,
                           y2=t.GetEnd().y / s, w=t.GetWidth() / s))
bands = []
for z in b.Zones():
    if z.GetIsRuleArea() and z.GetZoneName() == "ISO_BAND":
        ol = z.Outline().Outline(0)
        bands.append(dict(layers=[pcbnew.LayerName(l) for l in z.GetLayerSet().Seq()],
                          pts=[(ol.CPoint(i).x / s, ol.CPoint(i).y / s)
                               for i in range(ol.PointCount())]))
e = b.GetBoardEdgesBoundingBox()
nets = {{b.GetNetInfo().GetNetItem(i).GetNetname(): i for i in range(b.GetNetCount())}}
print(json.dumps(dict(pads=pads, tracks=tracks, vias=vias, bands=bands, nets=nets,
    edge=[e.GetX() / s, e.GetY() / s,
          (e.GetX() + e.GetWidth()) / s, (e.GetY() + e.GetHeight()) / s])))
"""
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    return json.loads(r.stdout.strip().splitlines()[-1])


def unconnected(pcb: Path) -> list:
    out = Path(tempfile.mkdtemp()) / "u.json"
    subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "-o", str(out), str(pcb)],
                   capture_output=True, check=True)
    return json.loads(out.read_text())["unconnected_items"]


def in_poly_grid(X: np.ndarray, Y: np.ndarray, poly: list) -> np.ndarray:
    inside = np.zeros(X.shape, bool)
    n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if y1 == y2:
            continue
        cond = (y1 > Y) != (y2 > Y)
        xint = x1 + (Y - y1) * (x2 - x1) / (y2 - y1)
        inside ^= cond & (X < xint)
    return inside


class Board:
    """Rasterised copper on the four routing layers."""

    def __init__(self, g: dict, res: float) -> None:
        self.g, self.res = g, res
        self.x0, self.y0, self.x1, self.y1 = g["edge"]
        self.nx = int(math.ceil((self.x1 - self.x0) / res)) + 1
        self.ny = int(math.ceil((self.y1 - self.y0) / res)) + 1
        xs = self.x0 + np.arange(self.nx) * res
        ys = self.y0 + np.arange(self.ny) * res
        self.X, self.Y = np.meshgrid(xs, ys)          # [iy, ix]
        self.netid = {n: i for i, n in enumerate(sorted(g["nets"]))}
        self.iso_ids = {i for n, i in self.netid.items() if ISO_RE.match(n)}
        self.exempt_ids: set = set()
        # owner grids: 0 = free, -1 = edge/blocked, else netid+1 (last writer; conflicts rare)
        self.own = np.zeros((len(LAYERS), self.ny, self.nx), np.int32)
        self.exempt = np.zeros((len(LAYERS), self.ny, self.nx), bool)  # X2Y pad copper
        self.holes = [(p["x"], p["y"], p["drill"] / 2) for p in g["pads"] if p["drill"] > 0]
        self.holes += [(v["x"], v["y"], v["drill"] / 2) for v in g["vias"]]
        for p in g["pads"]:
            for lay in p["layers"]:
                self._box(LAYERS.index(lay), p["box"], p["net"], p["ref"] in EXEMPT)
        for t in g["tracks"]:
            if t["layer"] in LAYERS:
                self._capsule(LAYERS.index(t["layer"]), t["x1"], t["y1"], t["x2"], t["y2"],
                              t["w"] / 2, t["net"])
        for v in g["vias"]:
            for k in range(len(LAYERS)):
                self._capsule(k, v["x"], v["y"], v["x"], v["y"], v["r"], v["net"])
        band_f = next(b["pts"] for b in g["bands"] if "In1.Cu" in b["layers"])
        self.band = in_poly_grid(self.X, self.Y, band_f)
        self.band_b = np.zeros_like(self.band)
        for b in g["bands"]:
            if b["layers"] == ["B.Cu"]:
                self.band_b |= in_poly_grid(self.X, self.Y, b["pts"])
        # distance from a cell to the band (outside cells) and to its boundary (inside cells),
        # so a whole via disc / track width, not just its centre, is checked against the band
        self.to_band = distance_transform_edt(~self.band) * res
        self.in_band = distance_transform_edt(self.band) * res
        self.to_band_b = distance_transform_edt(~self.band_b) * res
        # Edge.Cuts is a rectangle with CORNER_R arcs; the bbox includes half the 0.05 mm
        # outline stroke, so the true edge sits 0.025 mm inside it.
        ex0, ey0, ex1, ey1 = self.x0 + 0.025, self.y0 + 0.025, self.x1 - 0.025, self.y1 - 0.025
        ex = np.minimum.reduce([self.X - ex0, ex1 - self.X, self.Y - ey0, ey1 - self.Y])
        r = CORNER_R
        centres = ((ex0 + r, ey0 + r), (ex1 - r, ey0 + r), (ex0 + r, ey1 - r), (ex1 - r, ey1 - r))
        for cx, cy in centres:
            corner = (np.abs(self.X - cx) <= r) & (np.abs(self.Y - cy) <= r) & \
                ((self.X - cx) * np.sign(cx - (ex0 + ex1) / 2) > 0) & \
                ((self.Y - cy) * np.sign(cy - (ey0 + ey1) / 2) > 0)
            ex = np.where(corner, r - np.hypot(self.X - cx, self.Y - cy), ex)
        self.edge_dist = ex
        hole_mask = np.zeros((self.ny, self.nx), bool)
        for hx, hy, hr in self.holes:
            hole_mask |= np.hypot(self.X - hx, self.Y - hy) <= hr
        self.hole_dist = distance_transform_edt(~hole_mask) * res

    def _ids(self, net: str) -> int:
        return self.netid.get(net, -2) + 1 if net else -1

    def _box(self, k, box, net, exempt=False) -> None:
        x1, y1, x2, y2 = box
        ix1, iy1 = int((x1 - self.x0) / self.res), int((y1 - self.y0) / self.res)
        ix2 = int(math.ceil((x2 - self.x0) / self.res))
        iy2 = int(math.ceil((y2 - self.y0) / self.res))
        sl = (k, slice(max(iy1, 0), iy2 + 1), slice(max(ix1, 0), ix2 + 1))
        self.own[sl] = self._ids(net)
        if exempt:
            self.exempt[sl] = True

    def _capsule(self, k, x1, y1, x2, y2, r, net, keep_foreign=False) -> None:
        pad = r + self.res
        bx1, bx2 = min(x1, x2) - pad, max(x1, x2) + pad
        by1, by2 = min(y1, y2) - pad, max(y1, y2) + pad
        ix1 = max(int((bx1 - self.x0) / self.res), 0)
        ix2 = min(int((bx2 - self.x0) / self.res) + 1, self.nx)
        iy1 = max(int((by1 - self.y0) / self.res), 0)
        iy2 = min(int((by2 - self.y0) / self.res) + 1, self.ny)
        X, Y = self.X[iy1:iy2, ix1:ix2], self.Y[iy1:iy2, ix1:ix2]
        dx, dy = x2 - x1, y2 - y1
        L2 = dx * dx + dy * dy
        t = np.clip(((X - x1) * dx + (Y - y1) * dy) / L2, 0, 1) if L2 else 0
        d = np.hypot(X - (x1 + t * dx), Y - (y1 + t * dy))
        sub = self.own[k, iy1:iy2, ix1:ix2]
        hit = d <= r
        if keep_foreign:  # router copper never relabels another net's copper
            hit &= (sub == 0) | (sub == self._ids(net))
        sub[hit] = self._ids(net)

    def add_route(self, net, segs, vias, w) -> None:
        for k, a, b in segs:
            self._capsule(k, a[0], a[1], b[0], b[1], w / 2, net, keep_foreign=True)
        for x, y in vias:
            for k in range(len(LAYERS)):
                self._capsule(k, x, y, x, y, VIA_D / 2, net, keep_foreign=True)
            self.holes.append((x, y, VIA_DRILL / 2))
            # distance to the new hole edge
            new = np.hypot(self.X - x, self.Y - y) - VIA_DRILL / 2
            self.hole_dist = np.minimum(self.hole_dist, new)

    def clearance_maps(self, net: str, win) -> "tuple[np.ndarray, np.ndarray]":
        """Per layer: distance to other-net copper of the same domain / of the other domain."""
        iy1, iy2, ix1, ix2 = win
        nid = self._ids(net)
        iso = (nid - 1) in self.iso_ids
        same, other = [], []
        iso_lookup = np.zeros(len(self.netid) + 2, bool)
        for i in self.iso_ids:
            iso_lookup[i + 1] = True
        for k in range(len(LAYERS)):
            o = self.own[k, iy1:iy2, ix1:ix2]
            foreign = (o != 0) & (o != nid)
            o_iso = iso_lookup[np.clip(o, 0, None)] & (o > 0)
            dom_diff = foreign & (o_iso != iso) & ~self.exempt[k, iy1:iy2, ix1:ix2]
            dom_same = foreign & ~dom_diff
            same.append(distance_transform_edt(~dom_same) * self.res if dom_same.any()
                        else np.full(o.shape, 99.0))
            other.append(distance_transform_edt(~dom_diff) * self.res if dom_diff.any()
                         else np.full(o.shape, 99.0))
        return np.array(same), np.array(other)


def route_pair(B: Board, net: str, a: dict, b: "dict | None", margin=6.0, plane=False,
               cap=400000):
    """A* from item a to item b (or, for a plane net, to the nearest legal via site)."""
    res = B.res
    iso = bool(ISO_RE.match(net))
    w = 0.2 if (net in POWER or iso) else 0.127
    pts = [a["pos"]] + ([b["pos"]] if b else [])
    xs, ys = [p["x"] for p in pts], [p["y"] for p in pts]
    m = 3.0 if plane else margin
    ix1 = max(int((min(xs) - m - B.x0) / res), 0)
    ix2 = min(int((max(xs) + m - B.x0) / res) + 1, B.nx)
    iy1 = max(int((min(ys) - m - B.y0) / res), 0)
    iy2 = min(int((max(ys) + m - B.y0) / res) + 1, B.ny)
    same, other = B.clearance_maps(net, (iy1, iy2, ix1, ix2))
    edge = B.edge_dist[iy1:iy2, ix1:ix2]
    holed = B.hole_dist[iy1:iy2, ix1:ix2]
    band = B.band[iy1:iy2, ix1:ix2]
    band_b = B.band_b[iy1:iy2, ix1:ix2]
    to_band, in_band = B.to_band[iy1:iy2, ix1:ix2], B.in_band[iy1:iy2, ix1:ix2]
    to_band_b = B.to_band_b[iy1:iy2, ix1:ix2]
    slack = res + 0.01   # grid cells measure to centres: allow one full cell of error
    track_ok = (same >= CLR + w / 2 + slack) & (other >= ISO_CLR + w / 2 + slack)
    track_ok &= (edge >= EDGE_CLR + w / 2)[None] & (holed >= HOLE_CLR + w / 2)[None]
    allowed = np.ones_like(track_ok)
    hw, vr = w / 2 + slack, VIA_D / 2 + slack       # copper extent past the cell centre
    out_band, out_band_b = to_band >= hw, to_band_b >= hw
    if iso:
        allowed[0] &= in_band >= hw
        allowed[1:3] = False
        allowed[3] = band_b & (to_band_b == 0)
    elif net == "PGND":
        allowed[1:3] &= out_band[None]
    else:
        allowed[0:3] &= out_band[None]
        allowed[3] &= out_band_b
    nid = B._ids(net)
    own_net = np.stack([B.own[k, iy1:iy2, ix1:ix2] == nid for k in range(len(LAYERS))])
    walk = (track_ok & allowed) | (own_net & allowed)
    via_ok = np.all(same >= CLR + VIA_D / 2 + slack, axis=0) & np.all(
        other >= ISO_CLR + VIA_D / 2 + slack, axis=0)
    via_ok &= (edge >= EDGE_CLR + VIA_D / 2) & (holed >= HOLE_HOLE + VIA_DRILL / 2 + slack)
    if iso:
        via_ok[:] = False      # In2-In4 band keep-outs forbid vias; outside the band is barred
    else:
        via_ok &= (to_band >= vr) & (to_band_b >= vr)

    def cell(p):
        return (int(round((p["y"] - B.y0) / res)) - iy1, int(round((p["x"] - B.x0) / res)) - ix1)

    def lay(item):
        mm = re.search(r" on ([A-Za-z0-9.]+)", item["description"])
        return [LAYERS.index(mm.group(1))] if mm and mm.group(1) in LAYERS else list(range(4))

    H, W = band.shape
    sy, sx = cell(a["pos"])
    if not (0 <= sy < H and 0 <= sx < W):
        return None
    starts = [(k, sy, sx) for k in lay(a)]
    if b:
        gy, gx = cell(b["pos"])
        goals = {(k, gy, gx) for k in lay(b)}
    dirs = [(-1, 0, 1), (1, 0, 1), (0, -1, 1), (0, 1, 1), (-1, -1, 1.4142), (-1, 1, 1.4142),
            (1, -1, 1.4142), (1, 1, 1.4142)]
    dist, prev, pq = {}, {}, []
    for s in starts:
        dist[s] = 0.0
        heapq.heappush(pq, (0.0, 0.0, s))
    found = None
    while pq:
        f, g0, s = heapq.heappop(pq)
        if g0 > dist.get(s, 1e18):
            continue
        k, y, x = s
        if plane:
            if via_ok[y, x] and (g0 > 0 or True):
                found = s
                break
        elif s in goals:
            found = s
            break
        for dy, dx, c in dirs:
            ny_, nx_ = y + dy, x + dx
            if 0 <= ny_ < H and 0 <= nx_ < W and walk[k, ny_, nx_]:
                n = (k, ny_, nx_)
                ng = g0 + c * res
                if ng < dist.get(n, 1e18):
                    dist[n], prev[n] = ng, s
                    h = 0.0 if plane else math.hypot(ny_ - gy, nx_ - gx) * res
                    heapq.heappush(pq, (ng + h, ng, n))
        if via_ok[y, x] and not plane:
            for k2 in range(4):
                if k2 != k and walk[k2, y, x]:
                    n = (k2, y, x)
                    ng = g0 + VIA_COST
                    if ng < dist.get(n, 1e18):
                        dist[n], prev[n] = ng, s
                        heapq.heappush(pq, (ng + math.hypot(y - gy, x - gx) * res, ng, n))
        if len(dist) > cap:
            break
    if not found:
        return None
    path = [found]
    while path[-1] in prev:
        path.append(prev[path[-1]])
    path.reverse()

    def xy(s):
        return (round(B.x0 + (s[2] + ix1) * res, 4), round(B.y0 + (s[1] + iy1) * res, 4))

    segs, vias = [], []
    if plane:
        vias.append(xy(found))
    run = [path[0]]
    for s in path[1:]:
        if s[0] != run[-1][0]:
            vias.append(xy(s))
            segs += _segments(run, xy)
            run = [s]
        else:
            run.append(s)
    segs += _segments(run, xy)
    return segs, vias, w


def _segments(run, xy):
    """Collapse a same-layer cell run into straight segments at direction changes."""
    if len(run) < 2:
        return []
    out, start = [], run[0]
    d0 = (run[1][1] - run[0][1], run[1][2] - run[0][2])
    for i in range(1, len(run) - 1):
        d = (run[i + 1][1] - run[i][1], run[i + 1][2] - run[i][2])
        if d != d0:
            out.append((run[i][0], xy(start), xy(run[i])))
            start, d0 = run[i], d
    out.append((run[-1][0], xy(start), xy(run[-1])))
    return [s for s in out if s[1] != s[2]]


def emit(net_code: int, segs, vias, w) -> str:
    blocks = []
    for k, a, b in segs:
        blocks.append(f'\t(segment\n\t\t(start {a[0]} {a[1]})\n\t\t(end {b[0]} {b[1]})\n'
                      f'\t\t(width {w})\n\t\t(layer "{LAYERS[k]}")\n\t\t(net {net_code})\n'
                      f'\t\t(uuid "{uuid.uuid4()}")\n\t)\n')
    for x, y in vias:
        blocks.append(f'\t(via\n\t\t(at {x} {y})\n\t\t(size {VIA_D})\n\t\t(drill {VIA_DRILL})\n'
                      f'\t\t(layers "F.Cu" "B.Cu")\n\t\t(net {net_code})\n'
                      f'\t\t(uuid "{uuid.uuid4()}")\n\t)\n')
    return "".join(blocks)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pcb")
    ap.add_argument("--res", type=float, default=0.05)
    ap.add_argument("--max", type=int, default=10000)
    ap.add_argument("--only", default=None)
    ap.add_argument("--margin", type=float, default=6.0)
    ap.add_argument("--cap", type=int, default=400000)
    a = ap.parse_args()
    pcb = Path(a.pcb)
    g = geometry(pcb)
    B = Board(g, a.res)
    items = unconnected(pcb)
    only = set(a.only.split(",")) if a.only else None
    text = pcb.read_text()
    codes = {m.group(2): int(m.group(1))
             for m in re.finditer(r'^\t\(net (\d+) "([^"]*)"\)', text, re.M)}
    added, ok, fail = [], 0, []
    placed: dict = {}   # net -> via sites already emitted (two pads may pick one site)

    def fresh(net, r):
        segs, vias, w = r
        keep = [v for v in vias if all(math.hypot(v[0] - q[0], v[1] - q[1]) > 0.06
                                       for q in placed.get(net, []))]
        placed.setdefault(net, []).extend(keep)
        return segs, keep, w

    # route plane drops first, then short connections before long ones
    def span(u):
        p, q = u["items"][0]["pos"], u["items"][-1]["pos"]
        net = re.search(r"\[([^\]]+)\]", u["items"][0]["description"]).group(1)
        return (net not in PLANES, math.hypot(p["x"] - q["x"], p["y"] - q["y"]))
    items.sort(key=span)
    for u in items[:a.max]:
        ia, ib = u["items"][0], u["items"][-1]
        net = re.search(r"\[([^\]]+)\]", ia["description"]).group(1)
        if only and net not in only:
            continue
        plane = net in PLANES
        if plane:
            # a plane pad: drop a via from whichever item is a pad (both, if both are)
            r = None
            for it in (ia, ib):
                if it["description"].startswith("Pad"):
                    r1 = route_pair(B, net, it, None, plane=True)
                    if r1:
                        r1 = fresh(net, r1)
                        B.add_route(net, *r1)
                        added.append(emit(codes[net], *r1))
                        r = r1
            ok += 1 if r else 0
            if not r:
                fail.append(net)
            continue
        r = route_pair(B, net, ia, ib, margin=a.margin, cap=a.cap)
        if r:
            r = fresh(net, r)
            B.add_route(net, *r)
            added.append(emit(codes[net], *r))
            ok += 1
        else:
            fail.append(net)
    i = text.index("\n\t(zone\n") + 1
    pcb.write_text(text[:i] + "".join(added) + text[i:])
    print(f"routed {ok} of {ok + len(fail)}; failed: {sorted(set(fail))}")


if __name__ == "__main__":
    main()
