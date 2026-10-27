#!/usr/bin/env python3
"""observer_board_envelope.py -- the nose Observer board's real envelope on its
pitched plane, measured against the bay-cut head shell, and the current KiCad
board checked against it.

Measures (aircraft datum R2, board plane = the Rev H2 bay geometry from
tools/head_layout_fit.py):
  1. WALL half-widths, port and starboard separately, per station u (mm aft of
     the leading edge), at the board's own thickness -- where the slot rails
     printed on the head walls must hold the board's slanted edges;
  2. a CLEARANCE map per (x, u) cell: free height above the roof-side face and
     below the floor-side face before the skin;
  3. the KiCad board (avionics/kicad/Observer/kicads/Observer.kicad_pcb):
     its Edge.Cuts outline against the walls, and every footprint's assumed
     body height against the clearance map on the face it is mounted on.

KiCad -> board-local mapping (Observer.md "Board coordinate frame"): the
narrow (sensor) end is at KiCad X_LEAD, u = X_LEAD - X; lateral x (hull +X =
port) = Y - Y_CL (KiCad +Y = starboard -> port per Observer.md).  F.Cu faces
the roof (ROOF_FACE), B.Cu the floor -- the SoM side faces the floor.

Component heights are ASSUMED (listed in BODY_H with their basis); verify each
against its datasheet before relying on a margin.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the
author's direction, 2026-10-27, per `AGENTS.md` §3 AI attribution.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import json
import os
import re
import sys

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import head_layout_fit as h  # noqa: E402
from cargo_layout_fit import to_man  # noqa: E402

PCB = os.path.join(REPO, "avionics", "kicad", "Observer", "kicads", "Observer.kicad_pcb")
OUT_JSON = os.path.join(REPO, "avionics", "kicad", "Observer", "observer_nose_envelope.json")
X_LEAD, Y_CL = 243.743246, 151.309093  # KiCad narrow-end X and centre-line Y
BOARD_T = 1.6
GRID = 1.0
ROOF_FACE = "F.Cu"

# ASSUMED body heights above the board, mm (basis in the comment).
BODY_H = {
    # 5 mm BTH-060 stack + module (VERA_NOSE_TRAPEZOID Rev C) + margin
    "phyCORE-AM62x_PCM071": 11.0,
    "Wurth_749010012A": 6.0,  # ASSUMED, verify REF-SENSOR-028 drawing
    "JST_GH_BM": 4.3,  # ASSUMED vertical GH header, verify JST GH drawing
    "JST_GH_SM": 3.0,  # ASSUMED horizontal GH header
    "JST_SH_BM": 3.0,  # ASSUMED vertical SH header
    "SOIC-20W": 2.65,  # ASSUMED JEDEC MS-013 class max
    "TQFP-128": 1.2,  # ASSUMED TQFP max body
    "VQFN": 1.0, "QFN": 1.0, "WSON": 0.8, "SOT-563": 0.6,
    "SOT-23": 1.2, "SOT-143": 1.2, "L_Taiyo-Yuden_NR-20xx": 1.0,
    "L_CommonModeChoke": 1.3, "Crystal_SMD_2012": 0.6, "0402": 0.6, "SolderJumper": 0.1,
    "DS_": 0.1,  # direct-solder lands (sensor bodies are on the leading edge)
}


def body_h(name):
    for k, v in BODY_H.items():
        if k in name:
            return v
    return None


def frame():
    lead = h.bay_face() - h.FLAT_N * (h.POD_D + h.JOINT)
    return lead, np.array([1.0, 0, 0]), -h.FLAT_N, -h.BAY_BN  # origin, X, U (aft), V (roof)


def cut_head():
    m = to_man(trimesh.load(h.HEAD)) - to_man(h.bay_cutter())
    mm = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts))


def first_hit(head, P, d):
    loc, ri, _ = head.ray.intersects_location(P, np.repeat(d[None], len(P), 0),
                                              multiple_hits=False)
    dist = np.full(len(P), np.inf)
    dist[ri] = np.linalg.norm(loc - P[ri], axis=1)
    return dist


def measure(head):
    lead, X, U, V = frame()
    us = np.arange(0.0, 72.0 + GRID / 2, GRID)
    xs = np.arange(-34.0, 34.0 + GRID / 2, GRID)
    walls = []
    for u in us:
        row = {}
        for side, sx in (("port", 1.0), ("stbd", -1.0)):
            hw = np.inf
            for v in (0.0, BOARD_T):
                P = (lead + U * u + V * v)[None]
                hw = min(hw, float(first_hit(head, P, X * sx)[0]))
            row[side] = hw
        walls.append((float(u), row["port"], row["stbd"]))
    P = np.array([lead + X * x + U * u for u in us for x in xs])
    up = first_hit(head, P + V * BOARD_T, V).reshape(len(us), len(xs))
    dn = first_hit(head, P, -V).reshape(len(us), len(xs))
    return us, xs, walls, up, dn


def pcb_items():
    s = open(PCB, encoding="utf-8").read()
    edge = re.findall(r'\(gr_(?:line|arc)\s+\(start ([-\d.]+) ([-\d.]+)\)(?:\s+\(mid ([-\d.]+) '
                      r'([-\d.]+)\))?\s+\(end ([-\d.]+) ([-\d.]+)\)(?:(?!\(layer).)*\(layer '
                      r'"Edge.Cuts"\)', s, re.S)
    pts = []
    for e in edge:
        vals = [float(v) for v in e if v != ""]
        pts += [vals[i:i + 2] for i in range(0, len(vals), 2)]
    fps = []
    for m in re.finditer(r'\n\t\(footprint "([^"]*)"\s+\(layer "([^"]+)"\).*?\n\t\t\(at ([-\d.]+) '
                         r'([-\d.]+)(?: ([-\d.]+))?\)', s, re.S):
        blk_end = s.find("\n\t(footprint", m.end())
        blk = s[m.start():blk_end if blk_end > 0 else len(s)]
        ref = re.search(r'\(property "Reference" "([^"]*)"', blk)
        cx, cy = [], []
        for c in re.finditer(r'\((?:fp_line|fp_rect)\s+\(start ([-\d.]+) ([-\d.]+)\)\s+\(end '
                             r'([-\d.]+) ([-\d.]+)\)(?:(?!\(fp_).)*?\(layer "[FB]\.CrtYd"\)',
                             blk, re.S):
            cx += [float(c.group(1)), float(c.group(3))]
            cy += [float(c.group(2)), float(c.group(4))]
        fps.append(dict(ref=ref.group(1) if ref else "?", name=m.group(1).split(":")[-1],
                        layer=m.group(2), x=float(m.group(3)), y=float(m.group(4)),
                        rot=float(m.group(5) or 0),
                        crt=(min(cx), max(cx), min(cy), max(cy)) if cx else None))
    return np.array(pts), fps


def main():
    head = cut_head()
    us, xs, walls, up, dn = measure(head)
    print("wall half-width at the board plane (port / stbd), mm:")
    print("  " + "  ".join(f"u{int(u)}:{p:.1f}/{s:.1f}" for u, p, s in walls[::4]))
    pts, fps = pcb_items()
    U_b = X_LEAD - pts[:, 0]
    X_b = pts[:, 1] - Y_CL
    over = []
    for u, xb in zip(U_b, X_b):
        i = int(round(u / GRID))
        if 0 <= i < len(walls):
            wall = walls[i][1] if xb > 0 else walls[i][2]
            if abs(xb) > wall:
                over.append((round(float(u), 1), round(float(xb), 1), round(wall, 1)))
    print(f"\nEdge.Cuts points beyond the wall: {len(over)}"
          + (f" e.g. {over[:6]}" if over else ""))
    print(f"\nfootprint height check (roof face {ROOF_FACE}; heights ASSUMED, see BODY_H):")
    bad = []
    for f in fps:
        hgt = body_h(f["name"])
        if hgt is None or f["crt"] is None:
            continue
        roof = f["layer"] == ROOF_FACE
        clear = up if roof else dn
        c = f["crt"]
        a = np.radians(f["rot"])
        corners = [(f["x"] + px * np.cos(a) + py * np.sin(a), f["y"] - px * np.sin(a)
                    + py * np.cos(a)) for px in (c[0], c[1]) for py in (c[2], c[3])]
        uu = [X_LEAD - cx for cx, _ in corners]
        xx = [cy - Y_CL for _, cy in corners]
        iu = [i for i, u in enumerate(us) if min(uu) - 0.5 <= u <= max(uu) + 0.5]
        ix = [j for j, x in enumerate(xs) if min(xx) - 0.5 <= x <= max(xx) + 0.5]
        avail = float(np.min(clear[np.ix_(iu, ix)])) if iu and ix else -1.0
        margin = avail - hgt
        if margin < 1.0:
            bad.append((f["ref"], f["layer"], round(hgt, 2), round(avail, 2), round(margin, 2)))
    for b in sorted(bad, key=lambda t: t[4]):
        print(f"  {b[0]:12s} {b[1]:5s} body {b[2]:5.2f}  free {b[3]:6.2f}  margin {b[4]:+6.2f}")
    print(f"  {len(bad)} footprint(s) with < 1.0 mm margin to the skin")
    json.dump({"grid_mm": GRID, "u": us.tolist(), "x": xs.tolist(), "walls": walls,
               "clear_roof": np.where(np.isfinite(up), up, 99).round(2).tolist(),
               "clear_floor": np.where(np.isfinite(dn), dn, 99).round(2).tolist()},
              open(OUT_JSON, "w"))
    print(f"\nwrote {os.path.relpath(OUT_JSON, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
