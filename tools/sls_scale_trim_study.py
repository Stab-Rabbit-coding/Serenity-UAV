#!/usr/bin/env python3
"""sls_scale_trim_study.py -- hover-CG effect of a pivot shift, a forward hull
plug (27 in) and uniform scaling, using the same mass items and rail-lever
arrangement as tools/cg_relocation_study.py (no relocation search is run).

Frame: aircraft datum R2, Y aft-positive, nose near Y 0, hover thrust line =
nacelle tilt pivot Y 326.7.  Positive offset = CG aft of the thrust line.

Run (needs numpy, shapely, manifold3d, trimesh):
    python3 tools/sls_scale_trim_study.py

Statics only: moment balance about the pivot, CG = sum(m*y)/sum(m).  Pitch
control authority is NOT in the repo; the trim range needed is therefore an
input, not a result.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic) under the author's direction,
2026-10-31, per `AGENTS.md` §3 AI attribution.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cg_relocation_study as c  # noqa: E402

PIVOT = c.PIVOT_Y
IN = 25.4


def entries():
    """Hover entries (label, group, m, y) for the rail-lever arrangement."""
    base, _payload = c.items()
    node_a = {i.name for i in base if "(node A)" in i.name}
    groups = {}
    moved = set(node_a)
    for name, pred, _dims, _split, _skip in c.CANDIDATES:
        g = [i for i in base if pred(i.name)]
        m = sum(i.m for i in g)
        groups[name] = (m, sum(i.m * i.cg[1] for i in g) / m)
        moved |= {i.name for i in g}
    lump = [i for i in base if i.ref in c.LUMP]
    moved |= {i.name for i in lump}
    out = [(i.name, i.kind, i.m, i.cg[1]) for i in base if i.name not in moved]
    m_a = sum(i.m for i in base if i.name in node_a)
    out += [("Bay A", "BOM", m_a, c.BAYA_Y), ("head cell", "BOM", c.CELL_G, c.HEAD_CELL_Y),
            ("nose Observer", "BOM", c.NOSE_OBS_G, c.NOSE_OBS_Y),
            ("cell 2", "BOM", c.CELL_G, c.CELL2_Y)]
    out += [(n, "BOM", m, y) for n, (m, y) in groups.items()]
    fe_y = groups["Flight Engineer (board + can + plate)"][1]
    spans = [(c.HEAD_CELL_Y0 + c.hlf.CELL_L, c.hlf.BAND_ZC), (c.CELL2_Y1, c.hlf.BAND_ZC)]
    w = c.harness(fe_y - (c.mlf.FE_CAN_Y + c.mlf.FE_PLATE_Y) / 2, c.mlf.FE_ZC, spans)
    out += [("harness", "BOM", m, y) for m, y in w]
    return out


def cg(es, dy=lambda e: 0.0):
    m = sum(e[2] for e in es)
    return m, sum(e[2] * (e[3] + dy(e)) for e in es) / m


def main():
    es = entries()
    w, y0 = cg(es)
    off0 = y0 - PIVOT
    print(f"baseline hover: AUW {w:.0f} g ({w / 453.592:.2f} lbm), CG Y {y0:.1f}, offset {off0:+.1f} mm")
    by = {}
    for _n, k, m, _y in es:
        by[k] = by.get(k, 0) + m
    print("mass by kind (g):", {k: round(v) for k, v in by.items()})
    nac = by.get("NACELLE", 0.0)
    f = nac / w
    print(f"nacelle mass fraction f = {f:.3f}")

    print("\n(A) pivot shift aft by d (nacelles ride the pivot; offset closes by d(1-f))")
    for d_in in (0.5, 0.75, 1.0):
        d = d_in * IN
        _m, y = cg(es, lambda e: d if e[1] == "NACELLE" else 0.0)
        print(f"  d = {d_in:.2f} in ({d:.1f} mm): offset {y - (PIVOT + d):+.1f} mm")
    print(f"  pivot shift to zero the offset: {off0 / (1 - f):.1f} mm ({off0 / (1 - f) / IN:.2f} in)")

    print("\n(B) uniform scale k about the pivot (every station scales; offset x k)")
    for k, label in ((1.125, "27 in"), (1.25, "30 in")):
        print(f"  {label}: offset {off0 * k:+.1f} mm; pivot move to zero "
              f"{off0 * k / (1 - f):.1f} mm")

    print("\n(C) forward plug P (27 in = 3 in) at split Y_s: items forward of Y_s move nose-ward")
    p = 3.0 * IN
    for ys in (235.0, 286.2):
        fwd = [e for e in es if e[3] < ys]
        mf = sum(e[2] for e in fwd)
        _m, y = cg(es, lambda e, ys=ys: -p if e[3] < ys else 0.0)
        print(f"  Y_s {ys:.0f}: forward mass {mf:.0f} g; offset {y - PIVOT:+.1f} mm "
              f"(shift {y - y0:+.1f} mm)")
    ys = 235.0
    d = 0.5 * IN
    _m, y = cg(es, lambda e: (d if e[1] == "NACELLE" else 0.0) + (-p if e[3] < ys else 0.0))
    print(f"  plug 3 in at Y 235 + pivot 0.5 in aft: offset {y - (PIVOT + d):+.1f} mm")

    print("\n(E) joint load at the remaining collar (Y 436) in the 2-section hull, crash case")
    yj = 436.0
    aft = [e for e in es if e[3] > yj]
    ma = sum(e[2] for e in aft)
    ya = sum(e[2] * e[3] for e in aft) / ma
    n = 79.4  # plan 001 R7 design load factor (landing-gear peak hull deceleration, 4 ft drop)
    v = ma / 1000 * n * 9.80665
    mom = v * (ya - yj) / 1000
    print(f"  aft mass {ma:.0f} g ({ma / 453.592:.2f} lbm), centroid Y {ya:.1f}, arm {ya - yj:.1f} mm")
    print(f"  at {n} g, load normal to the hull axis: shear V = {v:.0f} N ({v / 4.448:.0f} lbf), "
          f"bending M = {mom:.1f} N.m ({mom * 8.851:.0f} lbf.in)")
    print("  (assumes the aft mass is rigid and the whole load reacts at the joint; allowables not sourced)")

    print("\n(F) UNIFORM fuselage scale k about the nose (owner direction 2026-10-31)")
    print("    hull shells/collars mass x k^2 (2 mm wall kept); every fuselage item's station x k;")
    print("    nacelles/wings stay full size and ride the pivot P (free parameter)")
    hull = [e for e in es if "shell24" in e[0] or "splice_collar" in e[0]]
    m_hull = sum(e[2] for e in hull)
    for k in (25 / 24, 26 / 24, 27 / 24):
        sc = []
        for n, kind, m, y in es:
            if kind == "NACELLE":
                continue
            mm = m * k * k if (n, kind, m, y) in hull else m
            sc.append((mm, y * k))
        m_h = sum(a for a, _ in sc)
        y_h = sum(a * b for a, b in sc) / m_h
        m_n = nac
        p_zero = y_h  # nacelle (and wing) mass at the pivot; offset zero when P = CG_h
        p0 = PIVOT * k
        w2 = m_h + m_n
        off_k = (m_h * y_h + m_n * p0) / w2 - p0
        d_zero = p_zero - p0
        off_half = off_k - 0.5 * IN * (1 - m_n / w2)
        dm = (k * k - 1) * m_hull
        print(f"  k {k:.4f} ({24 * k:.0f} in): hull +{dm:.0f} g CF-PETG-ledger; AUW {w2:.0f} g; "
              f"offset at scaled pivot {off_k:+.1f} mm; pivot move to zero {d_zero:.1f} mm "
              f"({d_zero / IN:.2f} in); offset after a 0.5 in move {off_half:+.1f} mm; "
              f"cell-rail slack gained ~{(k - 1) * 246:.0f} mm [ASSUMED]")
        for lab, ratio in (("PA CF @1.28", 1.11 / 1.28), ("PA CF @1.05", 1.11 / 1.05)):
            dpa = m_hull * (k * k * ratio - 1)
            endu = ((6232 + dpa) / 6232) ** -1.5 - 1
            print(f"     {lab}: hull {dpa:+.0f} g vs today's CF-PETG hull; endurance {100 * endu:+.1f}%")
        am = [e for e in es if e[3] > 436.0]
        ma = sum(e[2] * (k * k if e in hull else 1) for e in am)
        ya = sum(e[2] * (k * k if e in hull else 1) * e[3] * k for e in am) / ma
        v = ma / 1000 * 79.4 * 9.80665
        print(f"     J2 at Y {436 * k:.0f}: aft mass {ma:.0f} g, arm {ya - 436 * k:.0f} mm, "
              f"V {v:.0f} N, M {v * (ya - 436 * k) / 1000:.1f} N.m (ultimate x3: {3 * v * (ya - 436 * k) / 1000:.0f} N.m)")

    print("\n(D) trim authority = m * travel / AUW  (mm of CG per item)")
    for name, m in (("one 321 g cell", c.CELL_G), ("both cells", 2 * c.CELL_G),
                    ("300 g ballast at nose arm", 300.0)):
        for t_in in (1.0, 2.0, 3.0):
            print(f"  {name:26s} travel {t_in:.0f} in: {m * t_in * IN / w:5.2f} mm")
    arm = PIVOT - 15.0
    print(f"  ballast sensitivity at nose (arm {arm:.0f} mm): {arm / w:.3f} mm per g; "
          f"at tail Y 640: {(640 - PIVOT) / w:.3f} mm per g (CG moves aft)")


if __name__ == "__main__":
    main()
