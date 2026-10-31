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

LBF = 4.44822
Y_ROOT = 506.0          # skid roots leave the ring legs [MESH]
X_HALF = 45.0           # mm, skid centreline to aircraft centreline at the cross member [MESH]
STROKE = sf.STROKE_MM   # 7.3 mm
F_DESIGN = 750.0        # N per skid (CS-1 upper)
MATS = [("PA11 Black", 1500.0, 51.0), ("PA12-CF (DuraForm PA CF)", 7000.0, 84.0)]
K_STRUT = 5000.0        # N/mm: short PA strut in compression, E A / L ~ 1500*100/30 [ASSUMED]


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


if __name__ == "__main__":
    main()
