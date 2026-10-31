#!/usr/bin/env python3
"""skid_failure_mode_study.py -- how does a rear skid fail, and in which material?

Question (owner, 2026-10-31): under the co-strike skid force, do the skid walls
collapse along their length, or does the skid bend where it joins the ring?

Method (closed-form, per station; no FEA):
  1. Geometry is MEASURED from rear_shell24_2mm_repaired.stl (+ middle shell): at
     every 2 mm station the port skid tube is its own outer/inner loop pair
     (docs/TAIL_STRIKE_AND_LG_SLS_MATERIALS.md section 1).  The annulus is rasterised
     at 0.05 mm to get area, centroid, I about the horizontal (X) axis, elastic
     section modulus Z = I / c_max, and plastic modulus Zp (equal-area axis).
     Where the tube merges into the hull/ring (forward), there is no separate pair:
     that station is the cantilever ROOT for the as-built (one-piece) case.
  2. Load: one vertical tip force F at the skid tip (Y ~689), the co-strike plateau
     per skid (CS-1: 625-750 N).  Bending moment M(y) = F (y_tip - y).
  3. Failure modes, each as the tip force that triggers it:
       a. Bending at station y: brittle -> F = sigma_u Z / L ; ductile -> F = sigma_y Zp / L
          (plastic hinge).  Minimum over y says WHERE it fails.
       b. Local wall crushing at the contact (ring under a diametral line load,
          contact length Lc): elastic-brittle first crack F = pi sigma_u t^2 Lc / (6 R);
          ductile 4-hinge collapse F = sigma_y t^2 Lc / R  [ring formulas, REF-STR-001,
          requires verification].
       c. Brazier ovalisation limit moment M_B = (2 sqrt2 / 9) pi E r t^2 / sqrt(1-nu^2)
          [Brazier 1927, REF-STR-002 requires verification] and SP-8007 local
          buckling in bending sigma_cr = 0.605 gamma E t / r [REF-NASA-002].
  4. Option B (ring + skids printed separately): the free length runs from the
     ring (Y ~485) instead of the as-built root, with the as-built tube section
     extended forward [ASSUMED -- no separate geometry exists yet].

Materials [REF-MAT-002, REF-MAT-011..013]: allowables at face value, no knockdowns;
PA12 Black is shown with its XY elongation (6.2 %) as well, because it is marginal
for a plastic hinge.

Run:  /usr/bin/python3 tools/skid_failure_mode_study.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude Opus 5.5 (Anthropic) under the author's direction, 2026-10-31.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import itertools
import math
import os

import numpy as np
import trimesh
from shapely.geometry import Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
STL = os.path.join(HERE, "..", "airframe", "stls", "fuselage")
LBF = 4.44822
F_CASES = (625.0, 750.0)        # N per skid, CS-1
LC = 10.0                       # mm contact length along the tube [ASSUMED]
NU = 0.35                       # nylon / PETG Poisson ratio [ASSUMED]
Y_RING = 485.0                  # Option B root at the horseshoe ring [ASSUMED station]
Y_MERGE = 515.0                 # first continuous separate-tube station aft of the ring merge [MESH]

# name, strength MPa, flexural E MPa, elongation %, ductile (plastic hinge)?
MATS = [
    ("CF-PETG FDM 20% (REF-MAT-002)", 77.0, 6670.0, 2.1, False),
    ("PA12-CF / DuraForm PA CF (REF-MAT-011)", 84.0, 7000.0, 3.8, False),
    ("PA12 Black (REF-MAT-013)", 45.0, 1500.0, 13.7, True),
    ("PA11 Black (REF-MAT-012)", 51.0, 1500.0, 52.6, True),
]


def section_props(outer, inner, res=0.05):
    """Area, centroid z, I_x, Z_el, Zp, wall t, mean radius for an annulus (X-Z plane)."""
    ann = Polygon(outer).difference(Polygon(inner))
    x0, z0, x1, z1 = ann.bounds
    xs = np.arange(x0 + res / 2, x1, res)
    zs = np.arange(z0 + res / 2, z1, res)
    gx, gz = np.meshgrid(xs, zs)
    import shapely
    inside = shapely.contains_xy(ann, gx.ravel(), gz.ravel()).reshape(gx.shape)
    da = res * res
    zc_cells = gz[inside]
    a = zc_cells.size * da
    zc = zc_cells.mean()
    ix = ((zc_cells - zc) ** 2).sum() * da
    c = max(z1 - zc, zc - z0)
    zmed = np.median(zc_cells)               # plastic neutral axis: equal area above/below
    zp = np.abs(zc_cells - zmed).sum() * da
    po = Polygon(outer)
    r_out = math.sqrt(po.area / math.pi)
    t = a / (2 * math.pi * (r_out - 0.5 * a / (2 * math.pi * r_out)))  # thin-wall estimate
    return {"A": a, "zc": zc, "I": ix, "Z": ix / c, "Zp": zp, "t": t,
            "r": r_out - t / 2, "w": x1 - x0, "h": z1 - z0}


def port_skid_pairs():
    """Station -> (outer, inner) loop for the port skid tube, where it is separate."""
    out = {}
    for f in ("middle_shell24_2mm_repaired.stl", "rear_shell24_2mm_repaired.stl"):
        mesh = trimesh.load(os.path.join(STL, f))
        for y in np.arange(math.ceil(mesh.bounds[0][1]) + 1.0, mesh.bounds[1][1] - 1.0, 2.0):
            sec = mesh.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
            if sec is None:
                continue
            loops = [d[:, [0, 2]] for d in sec.discrete if len(d) > 8]
            cand = [lp for lp in loops if lp[:, 0].mean() < -20 and np.ptp(lp[:, 0]) < 40
                    and lp[:, 1].min() < 125 and lp[:, 1].max() < 140]
            cand.sort(key=lambda lp: -Polygon(lp).area)
            if len(cand) >= 2 and Polygon(cand[0]).contains(Polygon(cand[1])):
                out[round(float(y), 1)] = (cand[0], cand[1])
    return out


def main():
    pairs = port_skid_pairs()
    ys = sorted(pairs)
    props = {y: section_props(*pairs[y]) for y in ys}
    y_tip = ys[-1] + 1.0
    # As-built root: the tube is continuous from where it merges into the middle
    # shell at the horseshoe ring (stations appear sporadically at Y 492-502 as it
    # emerges; continuous from Y ~519) to the tip.  Between Y ~613 and ~629 its outer
    # wall merges into the ventral CROSS MEMBER that ties the two skids together; the
    # cross member is its own loop below the hull, not attached to it, so it is not a
    # vertical support -- those stations are bridged, not a root.
    run = sorted((y for y in ys if y >= Y_MERGE), reverse=True)
    y_root = min(run)
    print(f"Port skid tube measured as a separate section from Y {y_root:.0f} to {ys[-1]:.0f} "
          f"(tip ~{y_tip:.0f}); free cantilever {y_tip - y_root:.0f} mm ({(y_tip - y_root) / 25.4:.1f} in)")
    print("  Y      w x h mm    wall t  r_mean   A mm2    I mm4    Z mm3   Zp mm3")
    for y in run[::-1][::8] + [run[0]]:
        p = props[y]
        print(f"  {y:5.0f}  {p['w']:4.1f} x {p['h']:4.1f}  {p['t']:5.2f}  {p['r']:6.2f}  {p['A']:6.1f} "
              f"{p['I']:8.0f} {p['Z']:7.0f} {p['Zp']:7.0f}")

    root = props[y_root]
    for case, y0, sec0 in (("AS-BUILT (tube merges into the middle shell at the ring)", y_root, None),
                           ("OPTION B (separate ring + skids; root at the ring, Y 485)", Y_RING, root)):
        L_root = y_tip - y0
        print(f"\n{case}: free length {L_root:.0f} mm ({L_root / 25.4:.1f} in)")
        print(f"  {'material':40s} {'root bend':>10s} {'weakest station':>17s} {'wall crush':>11s} "
              f"{'Brazier':>9s} {'buckle':>8s}  governs (F per skid at onset)")
        for name, s, e, el, duct in MATS:
            best = (math.inf, None)
            stations = [(y, props[y]) for y in run] + ([(y0, sec0)] if sec0 else [])
            for y, p in stations:
                lev = y_tip - y
                if lev <= 5:
                    continue
                f_b = s * (p["Zp"] if duct else p["Z"]) / lev
                if f_b < best[0]:
                    best = (f_b, y)
            p0 = sec0 if sec0 else root
            f_root = s * (p0["Zp"] if duct else p0["Z"]) / L_root
            tip = props.get(run[0], root)
            f_crush = (s * tip["t"] ** 2 * LC / tip["r"] if duct
                       else math.pi * s * tip["t"] ** 2 * LC / (6 * tip["r"]))
            m_b = 2 * math.sqrt(2) / 9 * math.pi * e * p0["r"] * p0["t"] ** 2 / math.sqrt(1 - NU ** 2)
            f_brz = m_b / L_root
            phi = math.sqrt(p0["r"] / p0["t"]) / 16
            gam = 1 - 0.731 * (1 - math.exp(-phi))
            s_cr = gam * 0.605 * e * p0["t"] / p0["r"]
            f_buck = s_cr * p0["Z"] / L_root
            modes = {f"bending at Y {best[1]:.0f}": best[0], "wall crush at contact": f_crush,
                     "Brazier ovalisation": f_brz, "local buckling": f_buck}
            gov = min(modes, key=modes.get)
            print(f"  {name:40s} {f_root:8.0f} N {best[0]:8.0f} N @Y{best[1]:3.0f} {f_crush:9.0f} N "
                  f"{f_brz:7.0f} N {f_buck:6.0f} N  {gov} ({modes[gov]:.0f} N, {modes[gov] / LBF:.0f} lbf)"
                  f"{'  ductile' if duct else '  BRITTLE: fracture, no stroke'}")
        need = F_CASES
        print(f"  CS-1 needs {need[0]:.0f}-{need[1]:.0f} N per skid "
              f"({need[0] / LBF:.0f}-{need[1] / LBF:.0f} lbf) sustained over the stroke")
        z_need = need[1] * L_root / 51.0
        print(f"  PA11 plastic modulus needed at the root for 750 N: Zp {z_need:.0f} mm3 "
              f"(have {(sec0 or root)['Zp']:.0f}); a round tube of the same wall would need "
              f"OD ~{(z_need / (sec0 or root)['t']) ** 0.5:.0f} mm (Zp ~ D^2 t)")


STROKE_MM = 7.3        # mm: >= 8.3 mm hull clearance (cross member counted as skid frame) - 1 mm margin
U_SKID_J = 3.3         # J per skid, co-strike (CS-4)
Y_TIE = 596.0          # rear CF ring frame station (add_structural_features.py rear_Y290 pocket)


def stiffness_check():
    """Can the skid develop the co-strike force inside the stroke? (tip stiffness)

    Tip compliance of a cantilever with measured I(y): c = integral (L - y)^2 / (E I) dy.
    Needed: U = 3.3 J inside STROKE_MM -> plateau F >= U/S, or elastic-only k >= 2U/S^2.
    """
    pairs = port_skid_pairs()
    props = {y: section_props(*pairs[y]) for y in sorted(pairs) if y >= Y_MERGE}
    ys = sorted(props)
    y_tip = ys[-1] + 1.0
    print(f"\nSTIFFNESS: need {U_SKID_J} J per skid within {STROKE_MM} mm -> plateau >= "
          f"{U_SKID_J * 1e3 / STROKE_MM:.0f} N, or elastic k >= {2 * U_SKID_J * 1e3 / STROKE_MM ** 2:.0f} N/mm")
    for name, s_, e, _el, _d in MATS:
        for lab, y0 in (("root at ring", Y_MERGE), ("tied at CF frame Y596", Y_TIE)):
            c = sum((y_tip - (a + b) / 2) ** 2 / (e * props[a]["I"]) * (b - a)
                    for a, b in itertools.pairwise(ys) if a >= y0)
            k = 1 / c
            f_s = k * STROKE_MM
            m_t = f_s * (y_tip - y0)
            z0 = props[min(y for y in ys if y >= y0)]["Z"]
            print(f"  {name:40s} {lab:22s} k {k:6.1f} N/mm ({k * 25.4 / LBF:4.0f} lbf/in)  "
                  f"F@stroke {f_s:5.0f} N  U {0.5 * k * STROKE_MM ** 2 / 1e3:4.2f} J  "
                  f"stress at support {m_t / z0:5.0f} MPa (strength {s_:.0f})")


if __name__ == "__main__":
    main()
    stiffness_check()
