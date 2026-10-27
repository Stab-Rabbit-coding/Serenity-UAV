#!/usr/bin/env python3
"""cg_relocation_study.py -- move equipment forward until the hover CG sits on
the hover thrust line (nacelle tilt pivot, aircraft datum R2 Y 326.7), with
every move proved against the published shells and the existing layout
envelopes (no bounding-box placement, `airframe/AGENTS.md`).

Owner direction 2026-10-27: the CG target is the hover thrust line; try more
relocations before a pivot move or ballast.

Method
------
1. Mass items come from tools/auw_ledger.py (bom_rows, printed_items,
   nacelle_items, station_items, gap_items) -- the same roll-up the ledger
   reports, so this study and the ledger cannot drift.
2. Baseline A0 (owner decisions 2026-10-27): Bay A back in the nose
   (Observer edge-soldered on the bow flat), head cell on the rail at the
   Y 150 stop, second cell in the cargo roof band behind it.  Everything else
   at its ledger station.
3. Greedy relocation: for each candidate (largest aft moment first), remove
   it from the obstacle set, search the most-forward placement that clears
   the cargo shell (post-merge), the splice collars and every other envelope
   by STATIC_GAP, add it back at the new station, recompute CG.
4. Report CG for hover, heaviest-payload and third-cell configurations, and
   the spread against the MIL-F-83300 §3.4.4 50 % control-reserve framing.

Run:
    /usr/bin/python3 tools/cg_relocation_study.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the
author's direction, 2026-10-27, per `AGENTS.md` §3 AI attribution.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import os
import sys
import time

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import auw_ledger as al  # noqa: E402
import cargo_layout_fit as clf  # noqa: E402
import head_layout_fit as hlf  # noqa: E402
import hull_datums as hd  # noqa: E402
import middle_layout_fit as mlf  # noqa: E402
from cargo_layout_fit import box, to_man  # noqa: E402

PIVOT_Y = hd.SPAR_Y  # 326.7, hover thrust line = nacelle tilt axis
CELL_G = hlf.CELL_G  # 321 g, Tattu R-Line 6S 2200 (ORIGIN flag per plan 001 KTD4)
THIRD_CELL_G = 240.0  # Tattu R-Line v6.0 6S 1600 (plan 001 R9)
STATIC_GAP = 2.0  # static part to static part (cargo_layout_fit convention)
FSTL = os.path.join(REPO, "airframe", "stls", "fuselage")

# Stations, Rev H2 (head_layout_fit, 2026-10-27) -- imported, never retyped
H2_BAYA_Y = hlf.BAYA_Y0 + clf.NODE_L / 2  # 147
H2_HEAD_CELL_Y = 0.5 * (hlf.CELL_Y0 + hlf.CELL_Y1)  # 256
# Rail lever (this study, probed 2026-10-27): Bay A on edge ON the rail ceiling
# at Y 100-158, Z 208.65-245.65 (zero 1-2 mm-near vs the head skin and the
# pitched Observer board); the stop then moves to the band's forward limit.
LEVER_BAYA_Y0 = 100.0
LEVER_BAYA_Z0 = hlf.BAND_Z1 + hlf.RAIL_T + 1.0  # 208.65
LEVER_STOP_Y = 156.0  # band clear from Y 150 + stop plate 4 + leaf/tongue allowance
BAYA_Y = LEVER_BAYA_Y0 + clf.NODE_L / 2  # 129
HEAD_CELL_Y = LEVER_STOP_Y + hlf.SLED_LIP + hlf.CELL_L / 2  # 216
CELL2_Y1 = hlf.BAND_Y1  # 402.2, aft limit of the band (aft nodes)
CELL2_Y0 = CELL2_Y1 - hlf.CELL_L  # 286.2
CELL2_Y = 0.5 * (CELL2_Y0 + CELL2_Y1)  # 344.2
# Nose Observer (vision/ToF/laser) is NOT in the ledger: ASSUMED 60 g, the
# ledger's own figure for the cargo Observer node, at the pitched board's centroid.
NOSE_OBS_G = 60.0
NOSE_OBS_Y = float(hlf.observer_board().centroid[1])

# Candidates: name, ledger-name predicate, envelope (dx, dy, dz) incl. pouch /
# can, functional constraint note.  Envelopes from the owning layout tools.
NODE = (clf.NODE_L + clf.NODE_CABLE, clf.NODE_T, clf.NODE_H)  # standing transverse
CANDIDATES = [
    ("Flight Engineer (board + can + plate)",
     lambda n: n.startswith("Flight Engineer") or n.startswith("FE can"),
     (mlf.FE_CAN_X, mlf.FE_CAN_Y + mlf.FE_PLATE_Y, mlf.FE_CAN_Z),
     "power hub: battery leads in, ESC feeders out; ventral service access needed"),
    ("Simon CN4+FC4 (stack)", lambda n: "(node simon)" in n,
     (clf.NODE_L + clf.NODE_CABLE, clf.NODE_T, 2 * clf.NODE_H + 3.0),
     "bus-end termination + SMA whips on the middle crown"),
    ("aft nodes FC2/FC3", lambda n: "(node aft)" in n,
     (2 * (clf.NODE_L) + 3.0, clf.NODE_T, clf.NODE_H), "pair, transverse"),
    ("cargo Observer node", lambda n: n.startswith("Cargo Observer"),
     (clf.OBSERVER_L, clf.OBSERVER_T, clf.OBSERVER_W),
     "hoist monitor: must see the clamshell aperture (Y 307.7-413.7)"),
]


def items():
    bom = al.bom_rows()
    base = al.printed_items() + al.nacelle_items() + al.station_items(bom) + al.gap_items()
    payload = al.Item("payload", "PAYLOAD", al.PAYLOAD_G, al.PAYLOAD_ST[0], None, "", "PAYLOAD")
    return base, payload


def cg_y(entries):
    m = sum(e[0] for e in entries)
    return m, sum(e[0] * e[1] for e in entries) / m


def obstacles(exclude=()):
    """Union of fixed structure + placed envelopes in the cargo/middle zone."""
    cs = clf.shell_after_merge(trimesh.load(clf.SHELL))
    cs = to_man(cs) if isinstance(cs, trimesh.Trimesh) else cs
    m = cs
    for f in ("head_cargo_splice_collar.stl", "cargo_middle_splice_collar.stl",
              "middle_shell24_2mm_repaired.stl"):
        m = m + to_man(trimesh.load(os.path.join(FSTL, f)))
    L = clf.layout_t5()
    for k, e in list(L.items()):
        if e.get("mirror"):
            L[k + " (stbd)"] = dict(e, solid=clf.mirror_x(e["solid"]))
    for k, e in L.items():
        if k in ("battery", "battery cradle") or any(x in k for x in exclude):
            continue
        m = m + to_man(e["solid"])
    # the split cells' sliding band replaces the single pack
    m = m + to_man(box(-hlf.BAND_W / 2 - hlf.RAIL_T, hlf.BAND_W / 2 + hlf.RAIL_T, 150.0,
                       CELL2_Y1 + 2.0, hlf.BAND_Z0 - hlf.RAIL_T,
                       hlf.BAND_Z1 + hlf.RAIL_T))
    ML = mlf.layout_t6()
    for k, e in ML.items():
        if e.get("section", "middle") != "middle" or k.startswith("hatch"):
            continue
        if any(x in k for x in exclude):
            continue
        m = m + to_man(e["solid"])
    return m


def search(obst, dims, y_min, y_max, step=6.0):
    """Most-forward clear placement of an axis-aligned box (all 3 axis
    permutations), X on the centreline or +-30, Z swept."""
    perms = {tuple(dims), (dims[1], dims[0], dims[2]), (dims[0], dims[2], dims[1]),
             (dims[2], dims[1], dims[0])}
    for y0 in np.arange(y_min, y_max, step):
        for dx, dy, dz in perms:
            for xc in (0.0,):
                for z0 in np.arange(84.0, 250.0 - dz, 8.0):
                    b = box(xc - dx / 2, xc + dx / 2, y0, y0 + dy, z0, z0 + dz)
                    g = box(xc - dx / 2 - STATIC_GAP, xc + dx / 2 + STATIC_GAP,
                            y0 - STATIC_GAP, y0 + dy + STATIC_GAP,
                            z0 - STATIC_GAP, z0 + dz + STATIC_GAP)
                    if (to_man(g) ^ obst).volume() < 0.5:
                        return (xc, y0 + dy / 2, z0 + dz / 2), (dx, dy, dz), b
    return None


def main():
    t0 = time.time()
    base, payload = items()
    nodeA = [i for i in base if "(node A)" in i.name]
    moved_names = {i.name for i in nodeA}
    groups = {}
    for name, pred, dims, note in CANDIDATES:
        g = [i for i in base if pred(i.name)]
        groups[name] = (g, dims, note)
        moved_names |= {i.name for i in g}
    rest = [(i.m, i.cg[1]) for i in base if i.name not in moved_names]
    mA = sum(i.m for i in nodeA)
    station = {name: (sum(i.m for i in g), sum(i.m * i.cg[1] for i in g) / sum(i.m for i in g))
               for name, (g, _d, _n) in groups.items()}

    def entries(st, extra=()):
        e = list(rest) + [(mA, BAYA_Y), (CELL_G, HEAD_CELL_Y), (CELL_G, CELL2_Y),
                          (NOSE_OBS_G, NOSE_OBS_Y)]
        e += [(m, y) for (m, y) in st.values()]
        return e + list(extra)

    def report(label, st):
        out = []
        for cfg, extra in (("hover", ()), ("heaviest payload", ((payload.m, payload.cg[1]),)),
                           ("third cell", ((THIRD_CELL_G, payload.cg[1]),))):
            m, y = cg_y(entries(st, extra))
            out.append((cfg, m, y, y - PIVOT_Y))
        print(f"\n{label}")
        for cfg, m, y, d in out:
            print(f"  {cfg:17s} AUW {m:6.0f} g ({m / 453.592:5.2f} lbm)  CG Y {y:6.1f}  "
                  f"offset {d:+6.1f} mm ({d / 25.4:+.2f} in)")
        return out

    st = dict(station)
    m0, y0 = cg_y(list(rest) + [(mA, H2_BAYA_Y), (CELL_G, H2_HEAD_CELL_Y), (CELL_G, 541.7),
                                (NOSE_OBS_G, NOSE_OBS_Y)] + [v for v in station.values()])
    print(f"Rev H2 as handed over (Bay A Y {H2_BAYA_Y:.0f}, head cell Y {H2_HEAD_CELL_Y:.0f}, "
          f"cell 2 middle/aft Y 541.7): hover offset {y0 - PIVOT_Y:+.1f} mm")
    rows = [report("RAIL LEVER (Bay A on the rail ceiling, stop Y 156, cell 2 cargo band)", st)]
    log = []
    order = sorted(groups, key=lambda n: -station[n][0] * (station[n][1] - PIVOT_Y))
    for name in order:
        g, dims, note = groups[name]
        m, y_now = station[name]
        excl = {"Flight Engineer (board + can + plate)": ("Kaylee", "fan-out E5"),
                "Simon CN4+FC4 (stack)": ("Simon", "CN4", "FC4"),
                "aft nodes FC2/FC3": ("node N2", "node N4"),
                "cargo Observer node": ("Observer",)}[name]
        obst = obstacles(exclude=excl)
        for r in log:  # already-moved items at their new stations
            if r[0] != name and r[3] is not None:
                obst = obst + to_man(r[3])
        hit = search(obst, dims, 243.0, y_now - dims[1] / 2)
        if hit is None:
            log.append((name, m, None, None, note, 0.0))
            print(f"  {name}: no clear placement forward of Y {y_now:.1f}")
            continue
        (xc, yc, zc), d3, solid = hit
        gain = m * (y_now - yc)
        st[name] = (m, yc)
        log.append((name, m, (xc, yc, zc, d3), solid, note, gain))
        print(f"  {name}: {m:.0f} g  Y {y_now:.1f} -> {yc:.1f}  (X {xc:+.0f}, Z {zc:.0f}, "
              f"box {d3})  moment gained {gain:,.0f} g.mm")
        rows.append(report(f"after moving {name}", st))
    final = rows[-1]
    hover = final[0]
    spread = max(r[3] for r in final) - min(r[3] for r in final)
    resid = hover[3] * hover[1]
    print(f"\nresidual hover moment {resid:,.0f} g.mm; nose ballast at Y 15 to close "
          f"{resid / (PIVOT_Y - 15.0):.0f} g; CG spread across configs {spread:.1f} mm")
    print(f"pivot move to close without ballast: CG offset / (1 - f), f = nacelle+wing "
          f"mass fraction -- see docs/CG_RELOCATION_STUDY.md  ({time.time() - t0:.0f} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
