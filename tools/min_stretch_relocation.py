#!/usr/bin/env python3
"""min_stretch_relocation.py -- smallest uniform fuselage scale k (24 in -> at
most 27 in) at which relocating the Flight Engineer and the aft stack forward,
plus a forward battery cell used as live ballast, puts the hover CG forward of
the thrust line with trim room.

Plan: docs/plans/2026-10-31-003-feat-forward-trim-room-relocation-plan.md
(R1 relocation first, R2 minimum uniform scale <= 27 in, R3/R4 stacks, R5 nose
Observer fixed, R6 hoist on the thrust line, R7 single pivot 0.5 in aft).
Owner 2026-10-31: "use battery cells instead of dead ballast".

Method (reuses tools/cg_relocation_study.py, no retyped geometry)
------
1. Uniform scale S_k about the datum (X 0, Y 0 at the nose, Z ZC): every shell
   and collar mesh is scaled by k.  Layout ENVELOPES are NOT scaled (procured
   equipment keeps its size); each is TRANSLATED so its centroid lands at
   S_k(centroid), i.e. the layout keeps its proportional station.
2. Free-space map and greedy most-forward search exactly as
   cg_relocation_study.Map, over three candidates: the Flight Engineer (board,
   can, plate), the aft stack (Pilot+TACCO, split into its two pouches so a
   port/starboard pair is admissible), and a third 6S 1600 cell (240 g) whose
   only allowed station is forward of the thrust line.
3. Fixed by owner direction and NOT moved: nose Observer (R5), node A (fore
   stack), Simon (aft stack, made NoNFO-Pilot: -58 g, R3), cargo Observer and
   winch (R6).
4. Mass: printed hull items x k^2 at k*y; equipment at k*y; nacelles ride the
   pivot (y + (k-1)*326.7 + 12.7 for the 0.5 in shift); PA12-CF skid U-frame
   +17 g at Y 620k (docs/SKID_FAILURE_MODE_STUDY.md §8).  Skin thinning is NOT
   credited (handling governs, docs/AFT_SKIN_THINNING_STUDY.md) -- conservative.
   The routed harness is left as the ledger lump (scaled) -- ASSUMED.

Limits: S_k is a geometric stand-in for re-building the hull from the owner's
OpenSCAD/Blender sources (feedback: rebuild from source builds); it is a
screening fit, not a release geometry.  Port/starboard mirroring of the split
stack is reported, not enforced.

Run:
    /usr/bin/python3 tools/min_stretch_relocation.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the
author's direction, 2026-10-31, per `AGENTS.md` §3 AI attribution.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import os
import sys
import time

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import auw_ledger as al  # noqa: E402
import cg_relocation_study as c  # noqa: E402
import hull_datums as hd  # noqa: E402  (PENDING_PIVOT_SHIFT)

ZC = 160.0  # ASSUMED scale centre in Z (fuselage centreline height, datum R2)
# 0.5 in shift: 12.7 when planned, 0.0 now it is in the geometry (2026-10-31)
PIVOT_SHIFT = hd.PENDING_PIVOT_SHIFT
SIMON_NONFO_G = 58.0  # one TACCO 40 g + one PB2-I 13 g + half the pouches 5 g
SKID_G, SKID_Y = 17.0, 620.0
KS = (1.0, 25.0 / 24, 26.0 / 24, 27.0 / 24)
CANDS = [  # name, ledger predicate, envelope dims, split, envelope skip names
    c.CANDIDATES[0],  # Flight Engineer
    c.CANDIDATES[2],  # aft nodes (split -> port/stbd pair admissible)
]
CELL3 = ("third cell (live ballast)", (c.hlf.CELL_L, 38.5, 34.0))


def S(k):
    return np.array([[k, 0, 0, 0], [0, k, 0, 0], [0, 0, k, ZC * (1 - k)], [0, 0, 0, 1]])


def translate_to_scaled(tm, k):
    """Move an envelope (unscaled) so its centroid sits at S_k(centroid)."""
    cx, cy, cz = tm.bounds.mean(axis=0)
    t = np.array([(k - 1) * cx, (k - 1) * cy, (k - 1) * (cz - ZC)])
    out = tm.copy()
    out.apply_translation(t)
    return out


def patch(k):
    """Monkeypatch the layout sources so cg_relocation_study builds a k-scaled
    map.  Originals are kept on the module for restore."""
    orig = c.__dict__.setdefault("_orig", dict(
        load=c.trimesh.load, t5=c.clf.layout_t5, t6=c.mlf.layout_t6, hl=c.hlf.layout,
        box=c.box, shell=c.clf.shell_after_merge))

    def load(p, *a, **kw):
        m = orig["load"](p, *a, **kw)
        if isinstance(m, trimesh.Trimesh):
            m = m.copy()
            m.apply_transform(S(k))
        return m

    def wrap(fn):
        def f(*a, **kw):
            r = fn(*a, **kw)
            L = r[0] if isinstance(r, tuple) else r
            for e in L.values():
                if "solid" in e:
                    e["solid"] = translate_to_scaled(e["solid"], k)
            return r
        return f

    c.trimesh.load = load
    c.clf.layout_t5 = wrap(orig["t5"])
    c.mlf.layout_t6 = wrap(orig["t6"])
    c.hlf.layout = wrap(orig["hl"])
    c.box = lambda *a: translate_to_scaled(orig["box"](*a), k)


def mass_items(k):
    base, payload = c.items()
    nac = {i.name for i in al.nacelle_items()}
    out = []
    for i in base:
        if i.name in nac:
            out.append([i.name, i.m, i.cg[1] + (k - 1) * c.PIVOT_Y + PIVOT_SHIFT])
        elif i.kind == "PRINT":
            out.append([i.name, i.m * k * k, i.cg[1] * k])
        else:
            out.append([i.name, i.m, i.cg[1] * k])
    out.append(["Simon NoNFO-Pilot delta", -SIMON_NONFO_G, 494.7 * k])
    out.append(["skid U-frame PA12-CF + strut", SKID_G, SKID_Y * k])
    return out, (payload.m, payload.cg[1] * k)


def cg(rows):
    m = sum(r[1] for r in rows)
    return m, sum(r[1] * r[2] for r in rows) / m


def run(k):
    t0 = time.time()
    patch(k)
    pivot = k * c.PIVOT_Y + PIVOT_SHIFT
    rows, payload = mass_items(k)
    skip = tuple(s for _, _, _, _, sk in CANDS for s in sk)
    xs, ys, zs, free = c.free_map(c.shells(), c.envelopes(skip))
    fmap = c.Map(xs, ys, zs, free)
    log = []
    for name, pred, dims, split, _sk in sorted(
            CANDS, key=lambda cd: -sum(r[1] * (r[2] - pivot) for r in rows if cd[1](r[0]))):
        grp = [r for r in rows if pred(r[0])]
        m = sum(r[1] for r in grp)
        y0 = sum(r[1] * r[2] for r in grp) / m
        for r in grp:
            rows.remove(r)
        for j in range(split):
            best = fmap.most_forward(dims, y0)
            if best is None:
                rows.append([f"{name} #{j + 1} (stays)", m / split, y0])
                log.append((name, j, m / split, y0, y0, None))
                continue
            xc, yc, zc, d = best
            fmap.occupy(xc - d[0] / 2, xc + d[0] / 2, yc - d[1] / 2, yc + d[1] / 2,
                        zc - d[2] / 2, zc + d[2] / 2)
            rows.append([f"{name} #{j + 1}", m / split, yc])
            log.append((name, j, m / split, y0, yc, (xc, zc, d)))
    m0, y_h = cg(rows)
    best = fmap.most_forward(CELL3[1], pivot)
    cell = None if best is None else (c.THIRD_CELL_G, best[1], best)
    print(f"\n=== k = {k:.4f}  ({24 * k:.1f} in)  pivot Y {pivot:.1f}  "
          f"map {time.time() - t0:.0f} s")
    for name, j, m, y0, y1, w in log:
        if w is None:
            print(f"  {name[:34]:34s} #{j + 1} {m:6.1f} g stays at Y {y0:.1f}")
        else:
            print(f"  {name[:34]:34s} #{j + 1} {m:6.1f} g Y {y0:.1f} -> {y1:.1f} "
                  f"at X {w[0]:+.1f} Z {w[1]:.1f} box {tuple(round(v, 1) for v in w[2])}")
    print(f"  hover (no 3rd cell)      AUW {m0:6.0f} g  offset {y_h - pivot:+6.1f} mm")
    mp, yp = cg(rows + [["payload", *payload]])
    print(f"  heaviest payload         AUW {mp:6.0f} g  offset {yp - pivot:+6.1f} mm")
    if cell is None:
        print("  third cell: NO forward placement found")
        return k, y_h - pivot, None
    m3, y3 = cg(rows + [["cell 3", cell[0], cell[1]]])
    b = cell[2]
    print(f"  third cell 240 g at Y {cell[1]:.1f} X {b[0]:+.1f} Z {b[2]:.1f} "
          f"box {tuple(round(v, 1) for v in b[3])}: AUW {m3:6.0f} g  "
          f"offset {y3 - pivot:+6.1f} mm")
    return k, y_h - pivot, y3 - pivot


def main():
    res = [run(k) for k in KS]
    print("\nSUMMARY  (negative = CG forward of the thrust line = trim room)")
    for k, a, b in res:
        bs = "n/a" if b is None else f"{b:+.1f} mm"
        print(f"  {24 * k:4.1f} in: relocation only {a:+.1f} mm; plus forward cell {bs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
