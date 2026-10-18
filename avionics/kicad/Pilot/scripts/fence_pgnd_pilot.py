#!/usr/bin/env python3
"""fence_pgnd_pilot.py — PGND perimeter fence (stitching vias + F/B ring) for Pilot.

Usage:
    python3 fence_pgnd_pilot.py <board.kicad_pcb> [--pitch 2.0] [--inset 0.9]

Owner request 2026-10-12 (S. Griffing, EMI): a PGND ring with stitching vias along the
board edge, gapped at the PB2 rail pads, the §13.1 bubbles and the isolated band.
Script by Claude Opus 5.5, 2026-10-17.

Method:
1. Candidate via sites every ``--pitch`` mm on a path ``--inset`` mm inside the board
   edge (the R3 corners are where the M2.5 PGND-ring holes H1-H4 sit, so the four
   straight runs end at those rings).
2. Each candidate via, and each F.Cu / B.Cu segment between neighbouring vias, is
   checked on the rasterised copper of ``grid_route_pilot.Board``: 0.127 mm to other
   copper, 0.5 mm to ISOLATION-class copper (PGND is a logic-side net; Pilot.kicad_dru
   iso_cross_domain_clearance), 0.3 mm to the edge, hole clearances, outside both §13.1
   bubbles.  Illegal items are dropped, which is what leaves the gaps.
3. Only runs that reach a corner hole's PGND ring are kept (a link segment from the
   nearest via to the hole pad): a floating fence piece would be an unconnected PGND
   island, i.e. an antenna rather than a shield.
4. The kept vias and segments are appended to the board text; ``repair_pilot_routing.py``
   then rips anything the project DRC still rejects.

Rationale: stitching vias tie the F/B edge copper to the chassis ring so edge-launched
noise sees a low-impedance PGND boundary; pitch 2.0 mm is < lambda/20 at 3 GHz in FR-4
(eps_r ~4.3: lambda ~ 48 mm), well above the board's fastest edges (50 MHz MCLK,
100BASE-TX).

License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
from __future__ import annotations

import argparse
import math
import re
import sys
import uuid
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import grid_route_pilot as G  # noqa: E402

NET = "PGND"
W = 0.3                                  # ring track width, mm
HOLES = ("H1", "H2", "H3", "H4")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pcb")
    ap.add_argument("--pitch", type=float, default=2.0)
    ap.add_argument("--inset", type=float, default=0.9)
    ap.add_argument("--res", type=float, default=0.05)
    a = ap.parse_args()
    pcb = Path(a.pcb)
    g = G.geometry(pcb)
    B = G.Board(g, a.res)
    x0, y0, x1, y1 = g["edge"]
    win = (0, B.ny, 0, B.nx)
    same, other = B.clearance_maps(NET, win)
    bub = B.bubble_clear(NET, win)
    slack = a.res + 0.01
    vr, hw = G.VIA_D / 2 + slack, W / 2 + slack
    via_ok = (np.all(same >= G.CLR + vr, axis=0) & np.all(other >= G.ISO_CLR + vr, axis=0)
              & (B.edge_dist >= G.EDGE_CLR + G.VIA_D / 2)
              & (B.hole_dist >= G.HOLE_HOLE + G.VIA_DRILL / 2 + slack) & (bub >= vr))
    trk_ok = ((same >= G.CLR + hw) & (other >= G.ISO_CLR + hw)
              & (B.edge_dist >= G.EDGE_CLR + W / 2)[None] & (B.hole_dist >= G.HOLE_CLR + W / 2)[None]
              & (bub >= hw)[None])
    own = np.stack([B.own[k] == B._ids(NET) for k in range(len(G.LAYERS))])
    trk_ok |= own

    def cell(x, y):
        return int(round((y - B.y0) / a.res)), int(round((x - B.x0) / a.res))

    def seg_ok(k, p, q):
        n = max(2, int(math.hypot(q[0] - p[0], q[1] - p[1]) / (a.res / 2)))
        for t in np.linspace(0, 1, n):
            iy, ix = cell(p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1]))
            if not (0 <= iy < B.ny and 0 <= ix < B.nx) or not trk_ok[k, iy, ix]:
                return False
        return True

    hole = {p["ref"]: (p["x"], p["y"]) for p in g["pads"] if p["ref"] in HOLES and p["net"] == NET}
    r = G.CORNER_R
    e = a.inset
    runs = [  # straight runs between the corner holes: (start, end)
        ((x0 + r, y0 + e), (x1 - r, y0 + e)), ((x0 + r, y1 - e), (x1 - r, y1 - e)),
        ((x0 + e, y0 + r), (x0 + e, y1 - r)), ((x1 - e, y0 + r), (x1 - e, y1 - r)),
    ]
    vias, segs = [], []
    kept_runs = 0
    for (sx, sy), (ex, ey) in runs:
        length = math.hypot(ex - sx, ey - sy)
        n = int(length / a.pitch) + 1
        pts = [(round(sx + (ex - sx) * i / (n - 1), 3), round(sy + (ey - sy) * i / (n - 1), 3))
               for i in range(n)]
        ok = [via_ok[cell(*p)] for p in pts]
        # components of legal vias joined by a legal F or B segment
        comps: list = []
        cur: list = []
        for i, p in enumerate(pts):
            if not ok[i]:
                if cur:
                    comps.append(cur)
                cur = []
                continue
            if cur:
                q = pts[cur[-1][0]]
                lays = [k for k in (0, 3) if seg_ok(k, q, p)]
                if not lays:
                    comps.append(cur)
                    cur = []
                cur.append((i, lays))
            else:
                cur.append((i, []))
        if cur:
            comps.append(cur)
        for comp in comps:
            ends = [pts[comp[0][0]], pts[comp[-1][0]]]
            link = None
            for hp in hole.values():
                for end in ends:
                    if math.hypot(hp[0] - end[0], hp[1] - end[1]) < 4.5:
                        lays = [k for k in (0, 3) if seg_ok(k, end, hp)]
                        if lays:
                            link = (lays, end, hp)
            if link is None:
                continue
            kept_runs += 1
            for j, (i, lays) in enumerate(comp):
                vias.append(pts[i])
                if j:
                    for k in lays:
                        segs.append((k, pts[comp[j - 1][0]], pts[i]))
            for k in link[0]:
                segs.append((k, link[1], link[2]))
    text = pcb.read_text()
    net_m = re.search(rf'^\t\(net (\d+) "{re.escape(NET)}"\)', text, re.M)
    assert net_m is not None, f"net block for {NET!r} not found in {pcb}"
    code = int(net_m.group(1))
    blocks = []
    for k, p, q in segs:
        blocks.append(f'\t(segment\n\t\t(start {p[0]} {p[1]})\n\t\t(end {q[0]} {q[1]})\n'
                      f'\t\t(width {W})\n\t\t(layer "{G.LAYERS[k]}")\n\t\t(net {code})\n'
                      f'\t\t(uuid "{uuid.uuid4()}")\n\t)\n')
    for x, y in vias:
        blocks.append(f'\t(via\n\t\t(at {x} {y})\n\t\t(size {G.VIA_D})\n\t\t(drill {G.VIA_DRILL})\n'
                      f'\t\t(layers "F.Cu" "B.Cu")\n\t\t(net {code})\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n')
    i = text.index("\n\t(zone\n") + 1
    pcb.write_text(text[:i] + "".join(blocks) + text[i:])
    perim = 2 * ((x1 - x0) + (y1 - y0))
    print(f"fence: {len(vias)} vias, {len(segs)} segments in {kept_runs} run(s); "
          f"about {len(vias) * a.pitch:.0f} of {perim:.0f} mm perimeter stitched")


if __name__ == "__main__":
    main()
