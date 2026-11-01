#!/usr/bin/env python3
"""skid_mount_loads.py -- forces and moments at the ring / skid / hull mount points,
with and without a ventral strut from the skid cross member to the hull.

As-built topology (measured, docs/SKID_FAILURE_MODE_STUDY.md section 5):
  * Both skids and the ventral cross member (Y 613-629) form ONE U-frame.
  * The U-frame is attached to the airframe only through the horseshoe ring's lower
    legs (skid roots emerge at Y ~506; ring merges with the hull at Y ~465-475).
  * The cross member hangs ~1 mm below the hull bottom and is not attached to it.
  * The nearest hard point aft is the rear CF ring frame at Y 595.7.

Model: each skid is an Euler-Bernoulli beam with the MEASURED I(y)
(tools/skid_failure_mode_study.py), fixed at the ring root, tip load F at the skid
tip.  Optional strut: a vertical pin support (axial stiffness k_s of a short strut)
at Y_s.  Solved with 2-node beam elements (direct stiffness), 1 mm mesh.

Outputs per case and material, per skid at the co-strike force F:
  root shear V and moment M at the ring (what the ring legs and ring-to-hull joint carry),
  strut force (what the hull frame carries), max skid moment and stress, tip stiffness,
  force and energy available inside the 7.3 mm stroke.  Cross member: symmetric case
  carries the strut reaction to a central strut over the skid half-spacing; single-skid
  case adds the same moment as torsion/bending into the cross member.

Run:  /usr/bin/python3 tools/skid_mount_loads.py
Sources: beam stiffness method (standard); materials REF-MAT-011/012; ring frame station
add_structural_features.py (rear_Y290 pocket, R2 Y 595.7).

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude Opus 5.5 (Anthropic) under the author's direction, 2026-10-31.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import skid_failure_mode_study as sf
import hull_datums as hd  # noqa: E402  (tilt pivot = SPAR_Y)

LBF = 4.44822
Y_ROOT = 506.0          # skid roots leave the ring legs [MESH]
X_HALF = 45.0           # mm, skid centreline to aircraft centreline at the cross member [MESH]
STROKE = sf.STROKE_MM   # 7.3 mm
F_DESIGN = 750.0        # N per skid (CS-1 upper)
MATS = [("PA11 Black", 1500.0, 51.0), ("PA12-CF (DuraForm PA CF)", 7000.0, 84.0)]
# Strut = canon-hidden pad + internal rib (see strut_design()).  The pad is ~1 mm thick
# (cross member top Z 117 vs hull bottom Z 116-118), so its compliance is negligible; the
# strut stiffness is the internal rib cantilevered 24.3 mm aft from the CF ring frame.
Y_FRAME = 595.7         # rear CF ring frame (add_structural_features.py rear_Y290 pocket, R2)
Y_PAD = 620.0           # pads at the skid / cross-member junction, X +/-40 (inboard of the rails)
RIB_B, RIB_H = 5.0, 30.0   # mm, PA12-CF rib section (thickness x depth above the hull skin)
E_RIB, S_RIB = 7000.0, 84.0
K_STRUT = 3 * E_RIB * (RIB_B * RIB_H ** 3 / 12) / (Y_PAD - Y_FRAME) ** 3   # N/mm


def i_of_y():
    """Measured I(y) for y >= the separate-tube start; root zone carries the first value."""
    pairs = sf.port_skid_pairs()
    props = {y: sf.section_props(*pairs[y]) for y in sorted(pairs) if y >= sf.Y_MERGE}
    ys = np.array(sorted(props))
    iz = np.array([props[y]["I"] for y in ys])
    zz = np.array([props[y]["Z"] for y in ys])
    return ys, iz, zz, ys[-1] + 1.0


def solve(e, ys, iz, y_tip, y_strut=None, f_tip=1.0):
    """Beam FE: returns node y, deflection w, moment M(y), root V/M, strut force."""
    yn = np.arange(Y_ROOT, y_tip + 0.5, 1.0)
    n = len(yn)
    k = np.zeros((2 * n, 2 * n))
    for i in range(n - 1):
        le = yn[i + 1] - yn[i]
        ii = np.interp(0.5 * (yn[i] + yn[i + 1]), ys, iz, left=iz[0], right=iz[-1])
        ke = e * ii / le ** 3 * np.array([[12, 6 * le, -12, 6 * le], [6 * le, 4 * le ** 2, -6 * le, 2 * le ** 2],
                                          [-12, -6 * le, 12, -6 * le], [6 * le, 2 * le ** 2, -6 * le, 4 * le ** 2]])
        idx = [2 * i, 2 * i + 1, 2 * i + 2, 2 * i + 3]
        k[np.ix_(idx, idx)] += ke
    js = None
    if y_strut is not None:
        js = round(y_strut - Y_ROOT)
        k[2 * js, 2 * js] += K_STRUT
    f = np.zeros(2 * n)
    f[2 * (n - 1)] = f_tip
    free = np.arange(2, 2 * n)                      # root fixed (w, theta)
    u = np.zeros(2 * n)
    u[free] = np.linalg.solve(k[np.ix_(free, free)], f[free])
    react = k @ u - f
    v_root, m_root = react[0], react[1]
    r_strut = K_STRUT * u[2 * js] if js is not None else 0.0
    # bending moment along the beam from statics (tip load and strut reaction)
    m = np.array([f_tip * (y_tip - y) - (r_strut * (y_strut - y) if (js is not None and y < y_strut) else 0.0)
                  for y in yn])
    return yn, u[0::2], m, v_root, m_root, r_strut


def main():
    ys, iz, zz, y_tip = i_of_y()
    print(f"Skid beam: fixed at the ring root Y {Y_ROOT:.0f}, tip Y {y_tip:.0f} "
          f"({y_tip - Y_ROOT:.0f} mm); tip load F per skid; strut k {K_STRUT:.0f} N/mm [ASSUMED]")
    for name, e, s in MATS:
        print(f"\n{name} (E {e:.0f} MPa, strength {s:.0f} MPa)")
        print(f"  {'case':34s} {'k_tip':>8s} {'F@7.3mm':>8s} {'U@7.3':>6s} | per unit tip force:  "
              f"{'V_root':>7s} {'M_root':>8s} {'strut':>6s} {'M_max @Y':>12s}")
        for lab, ysr in (("as built (ring only)", None), ("ventral strut to CF frame Y596", 596.0),
                         ("ventral strut at cross member Y620", 620.0)):
            yn, w, m, vr, mr, rs = solve(e, ys, iz, y_tip, ysr)
            kt = 1.0 / w[-1]
            fs = kt * STROKE
            imax = int(np.argmax(np.abs(m)))
            print(f"  {lab:34s} {kt:6.1f} N/mm {fs:6.0f} N {0.5 * kt * STROKE ** 2 / 1e3:5.2f} J | "
                  f"{vr:+7.2f} {mr:+8.1f} {rs:+6.2f} {m[imax]:+7.1f} @{yn[imax]:3.0f}")
            # loads at the co-strike design force (or what the stroke can develop, if lower)
            f_use = min(F_DESIGN, fs)
            z_at = np.interp(yn[imax], ys, zz, left=zz[0], right=zz[-1])
            print(f"  {'':34s}   at F = {f_use:4.0f} N ({f_use / LBF:3.0f} lbf) per skid: ring root V "
                  f"{abs(vr) * f_use:5.0f} N, M {abs(mr) * f_use / 1e3:5.1f} N.m ({abs(mr) * f_use / 1e3 * 8.851:4.0f} lbf.in); "
                  f"strut {abs(rs) * f_use:5.0f} N/skid -> hull {2 * abs(rs) * f_use:5.0f} N (pair); "
                  f"skid sigma_max {abs(m[imax]) * f_use / z_at:4.0f} MPa vs {s:.0f}")
            if ysr is not None:
                m_cm = abs(rs) * f_use * X_HALF / 1e3
                print(f"  {'':34s}   cross member (central strut): bending {m_cm:4.1f} N.m each side "
                      f"(symmetric); single-skid strike: {m_cm:4.1f} N.m one side + torsion into the U")


def strut_design(f_tip=F_DESIGN):
    """Item 2: pad + bolt + rib sizing at the co-strike force (PA12-CF frame)."""
    ys, iz, _zz, y_tip = i_of_y()
    _yn, w, _m, vr, mr, rs = solve(E_RIB, ys, iz, y_tip, Y_PAD)
    r = abs(rs) * f_tip                      # N per side into the hull
    lr = Y_PAD - Y_FRAME
    m_rib = r * lr                           # N.mm at the frame end of the rib
    z_rib = RIB_B * RIB_H ** 2 / 6
    pad_a = 10.0 * 16.0
    print(f"\nSTRUT (item 2): pads at Y {Y_PAD:.0f}, X +/-40 (inboard of the rails, hidden in profile), "
          f"rib to the CF frame at Y {Y_FRAME}")
    print(f"  skid tip k {1 / w[-1]:.1f} N/mm with k_strut {K_STRUT:.0f} N/mm; per skid at F = {f_tip:.0f} N "
          f"({f_tip / LBF:.0f} lbf):")
    print(f"  pad reaction {r:.0f} N ({r / LBF:.0f} lbf) per side, {2 * r:.0f} N ({2 * r / LBF:.0f} lbf) pair; "
          f"pad bearing {r / pad_a:.1f} MPa on 10 x 16 mm")
    print(f"  rib {RIB_B:.0f} x {RIB_H:.0f} mm PA12-CF, {lr:.1f} mm: M {m_rib / 1e3:.1f} N.m "
          f"({m_rib / 1e3 * 8.851:.0f} lbf.in), sigma {m_rib / z_rib:.0f} MPa -> FOS "
          f"{S_RIB / (m_rib / z_rib):.2f}; mass {RIB_B * RIB_H * lr * 1.11e-3:.1f} g per side")
    print(f"  CF frame: {r:.0f} N + {m_rib / 1e3:.1f} N.m per side, in-plane; ring-root V {abs(vr) * f_tip:.0f} N, "
          f"M {abs(mr) * f_tip / 1e3:.1f} N.m per skid")
    print("  M3 A2-70 (tension cap 3,521 N, gear tool) from BELOW through the cross-member pad into a heat-set "
          "insert in the rib: compression goes through the pad in bearing; the bolt carries only rebound and "
          "locates the frame")


def size_elastic_design(y_pad=Y_PAD, crash_frac=0.95, b=6.0):
    """Items 2 + 5 together (owner, 2026-10-31): size the PA12-CF skid wall (inside the
    tube, outer shape unchanged) and the internal rib for the elastic co-strike.

    Criteria (TS-5 practice, as for the gear): the 4 ft co-strike may use the skid up to
    crash_frac x ultimate (sacrificial allowed); the 1.5 ft ordinary landing (LG-06) must
    stay elastic at ultimate / 1.5.  Wall growth f(y) scales I and Z (thin wall, fixed
    outer).  Iterates stiffness <-> peak force <-> wall growth.  US customary output.
    """
    import math as _m

    import tail_strike_requirement as ts
    pairs = sf.port_skid_pairs()
    pp = {y: sf.section_props(*pairs[y]) for y in sorted(pairs) if y >= sf.Y_MERGE}
    ys = np.array(sorted(pp))
    i0 = np.array([pp[y]["I"] for y in ys])
    z0 = np.array([pp[y]["Z"] for y in ys])
    a0 = np.array([pp[y]["A"] for y in ys])
    y_tip = ys[-1] + 1.0
    th0, pt, _f = ts.tip_back()
    _n, m, cy, cz, k = ts.design_case()
    sched, _smax = ts.gear_schedule_at(m)
    t = _m.radians(th0)
    cg, sp = ts.rot((cy, cz), t), ts.rot(pt, t)
    d1, d2 = (ts.Y_FOOT_AFT - cg[0]) / 1000, (sp[0] - cg[0]) / 1000
    fg = 2 * sched["f_leg_n"]
    lr = y_pad - Y_FRAME
    f = np.ones_like(i0)
    h = 30.0
    allow = S_RIB * crash_frac
    global K_STRUT
    for _ in range(6):
        K_STRUT = 3 * E_RIB * (b * h ** 3 / 12) / lr ** 3
        yn, w, mm, _vr, mr, rs = solve(E_RIB, ys, i0 * f, y_tip, y_pad)
        kk = 1 / w[-1]
        r = ts.co_strike(m, k / 1000, d1, d2, fg, 0.0, skid_k=2 * kk, dt=2e-6)
        fpk = r["f_skid_peak"] / 2
        mi = np.abs(np.interp(ys, yn, mm)) * fpk
        f = np.maximum(1.0, mi / (allow * z0))
        fs = abs(rs) * fpk
        h = max(20.0, _m.sqrt(6 * fs * lr / (allow * b)))
    r15 = ts.co_strike(m, k / 1000, d1, d2, fg, 0.0, skid_k=2 * kk, dt=2e-6, h=1.5 * 0.3048)
    s15 = (mi / fpk * r15["f_skid_peak"] / 2 / (z0 * f)).max()
    dm = np.trapezoid(a0 * (f - 1), ys) * 1.11e-3
    rib = b * h * lr * 1.11e-3
    tot = 2 * (dm + rib) + 4.0
    mpa2psi, g2oz, mm2in = 145.038, 1 / 28.3495, 1 / 25.4
    print(f"\nELASTIC DESIGN (pad Y {y_pad:.0f}, 4 ft at {crash_frac:.2f} x ultimate, 1.5 ft at ultimate/1.5):")
    print(f"  skid k {kk * 25.4 / LBF:.0f} lbf/in; 4 ft stroke {r['s_skid_max_mm'] * mm2in:.3f} in "
          f"({r['s_skid_max_mm']:.2f} mm; limit 0.217 in); peak {fpk / LBF:.0f} lbf ({fpk:.0f} N) per skid")
    print(f"  strut {fs / LBF:.0f} lbf ({fs:.0f} N) per side; ring root {abs(mr) * fpk / 1e3 * 8.851:.0f} lbf.in; "
          f"gear stroke {r['s_gear_mm'] * mm2in:.2f} in")
    print(f"  skid wall growth up to x{f.max():.1f} over Y {ys[f > 1.01].min():.0f}-{ys[f > 1.01].max():.0f} "
          f"(inside the tube): +{dm * g2oz:.2f} oz ({dm:.1f} g) per skid")
    print(f"  rib {b * mm2in:.2f} x {h * mm2in:.2f} in, {lr * mm2in:.2f} in long: {rib * g2oz:.2f} oz ({rib:.1f} g) per side")
    print(f"  1.5 ft landing: peak {r15['f_skid_peak'] / 2 / LBF:.0f} lbf, max stress {s15 * mpa2psi:.0f} psi vs "
          f"{S_RIB / 1.5 * mpa2psi:.0f} psi allowable -> {'elastic, no damage' if s15 <= S_RIB / 1.5 else 'OVER'}")
    print(f"  pair total +{tot * g2oz:.2f} oz ({tot:.0f} g) at Y ~{y_pad:.0f} -> hover CG "
          f"+{tot * (y_pad - hd.SPAR_Y) / (m * 1000) * mm2in:.3f} in aft")


if __name__ == "__main__":
    main()
    strut_design()
    size_elastic_design()
