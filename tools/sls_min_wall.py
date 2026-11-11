#!/usr/bin/env python3
"""sls_min_wall.py -- minimum wall (skin) thickness for SLS DuraForm PA CF printed parts.

Replaces the 0.079 in (2.0 mm) minimum that came from FDM CF-PETG.  Six cases:
load-bearing / non-load-bearing x foam-backed / free-standing / lattice-supported.
This is a MINIMUM-GAUGE rule (handling, oil-canning, process floor, stiffness parity with the
old FDM design basis).  It does not size a part for its own flight loads: a load-bearing part is
still sized by its own analysis, and this tool gives the floor that analysis starts from, plus the
in-plane allowables (panel buckling, face wrinkling) a part analysis needs.

Failure modes checked (each case reports the governing one):
  PROC   interim SLS minimum wall for carbon-filled PA, 1.5 mm (0.059 in); see T_PROC.  (Corrected
         2026-11-11: REF-MFG-001 p. 15 gives ">1mm" for pressure-tight tanks, not a minimum wall.)
  RUPT   flexural rupture of the skin under a handling point load, Roark-type thin-plate
         formula for a central load on a circular plate (simply supported for a free-standing
         panel, clamped for a lattice cell, a foundation-equivalent plate for a foam-backed skin).
  DEFL   oil-canning: deflection under the handling load above a declared limit.
  STIFF  (load-bearing only) bending-stiffness parity with the 2.0 mm FDM CF-PETG skin every
         existing analysis was written against: E t^3 equal.
  WRINK  (load-bearing foam-backed, informational) face-wrinkling stress, 0.5 (Ef Ec Gc)^(1/3)
         (Hoff and Mautner; Allen, Analysis and Design of Structural Sandwich Panels) - a limit
         on in-plane compressive skin stress, independent of skin thickness.
  BUCK   (load-bearing free-standing / lattice, informational) simply supported plate buckling,
         sigma_cr = k pi^2 E / (12 (1 - nu^2)) (t/b)^2, k = 4.

Inputs and their status (ASSUMED values are declared engineering judgment, not allowables):
  PA CF flexural modulus 7,000 MPa and strength 140 MPa, XY, TYPICAL (3DS-30108A, REF-MAT-015,
  via tools/sls_materials.py).  Typical values are not design allowables.
  Z knockdown 0.5 when the build orientation is not fixed
  (ASSUMED, sls_materials.Z_KNOCKDOWN_PA_CF).
  Poisson ratio 0.35 (ASSUMED, unfilled-polyamide order of magnitude; no PA CF value published).
  CF-PETG flexural modulus 6,670 MPa (repo MASS_AUDIT_CARGO_WING_ROOT.md section 1, REF-MAT-002).
  Handling load 10 lbf (44.5 N) on a 0.25 in (6.35 mm) radius contact (ASSUMED: a firm thumb press;
  no standard sets it).  Deflection limit 0.040 in (1.0 mm) under that load (ASSUMED).
  Factors: basic 1.5 on the handling load (ASSUMED) x special 1.5 for SLS process variability
  (ASSUMED, after the 14 CFR 23.2265 special-factor model) for load-bearing parts; 1.5 total for
  non-load-bearing parts.
  2 lb/ft3 PU core: Ec 1.0 MPa, Gc 0.4 MPa, depth 0.5 in (12.7 mm) (ASSUMED, low-end figures for
  rigid PU at that density; the FOAM-PU-2LB kit has no datasheet in the repo).

Usage:  python3 tools/sls_min_wall.py [--json OUT.json] [--orient xy|any]

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic, Claude Opus 5.5) under the author's direction, 2026-11-11.
         Plate formulas: Roark's Formulas for Stress and Strain (Young and Budynas), circular-plate
         central-load cases; Timoshenko and Woinowsky-Krieger, Theory of Plates and Shells, plates
         on an elastic foundation (characteristic length).  Neither is yet catalogued in
         REFERENCES.md: requires verification of edition and table numbers before citation.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sls_materials as sm  # noqa: E402

MM_IN = 25.4
# Interim floor for 33 % carbon-filled PA12 (2026-11-11 correction): REF-MFG-001 p. 15's ">1mm" is
# the wall for a pressure-tight SLS TANK, not a general minimum wall, and the guide (2019) predates
# PA CF.  No 3D Systems document read states a minimum wall for DuraForm PA CF.  General SLS
# guidance for fibre-filled powders is 1.5 mm minimum, 2.0-2.5 mm recommended (anthropic-skills
# 3d-print-design reference, uncited); 1.5 mm is used until the service bureau states its minimum.
T_PROC = 1.5                    # mm, INTERIM (see above)
NU = 0.35                       # ASSUMED
E_PETG = 6670.0                 # MPa, REF-MAT-002 via MASS_AUDIT section 1
T_PETG = 2.0                    # mm, the old FDM rule
P_HAND = 10.0 * 4.44822         # N, 10 lbf ASSUMED
R0 = 0.25 * MM_IN               # mm contact radius
DEFL_MAX = 1.0                  # mm, 0.040 in ASSUMED
FOS_NLB = 1.5                   # non-load-bearing
FOS_LB = 1.5 * 1.5              # load-bearing: basic x special (ASSUMED)
EC, GC, HC = 1.0, 0.4, 12.7     # foam core, ASSUMED
SPANS_IN = (0.5, 1.0, 2.0, 3.0, 4.0)        # free-standing panel span (in)
CELLS_IN = (0.25, 0.375, 0.5, 0.75, 1.0)    # lattice node pitch (in)


def inch(mm: float) -> str:
    return f"{mm / MM_IN:.3f} in ({mm:.2f} mm)"


def props(orient: str) -> tuple[float, float]:
    """(E_flex, sigma_flex) in MPa for the stated orientation control."""
    mat: dict[str, Any] = sm.PA_CF
    e, s = float(mat["flex_mod_mpa"]), float(mat["flex_strength_mpa"])
    if orient == "any":
        k = sm.Z_KNOCKDOWN_PA_CF
        e, s = e * k, s * k
    return e, s


def r_eq(t: float) -> float:
    """Roark's equivalent load radius for a concentrated load on a thin plate."""
    return math.sqrt(1.6 * R0 ** 2 + t ** 2) - 0.675 * t if R0 < 1.7 * t else R0


def stress_ss(p: float, a: float, t: float) -> float:
    """Simply supported circular plate, radius a, central load p over r_eq: max radial stress."""
    return 3 * p / (2 * math.pi * t ** 2) * ((1 + NU) * math.log(max(a / r_eq(t), 1.0)) + 1)


def stress_cl(p: float, a: float, t: float) -> float:
    """Clamped circular plate, central load: max stress at the centre."""
    return 3 * p / (2 * math.pi * t ** 2) * ((1 + NU) * math.log(max(a / r_eq(t), 1.0)))


def defl_ss(p: float, a: float, t: float, e: float) -> float:
    d = e * t ** 3 / (12 * (1 - NU ** 2))
    return p * a ** 2 * (3 + NU) / (16 * math.pi * d * (1 + NU))


def defl_cl(p: float, a: float, t: float, e: float) -> float:
    d = e * t ** 3 / (12 * (1 - NU ** 2))
    return p * a ** 2 / (16 * math.pi * d)


def foam_length(t: float, e: float) -> float:
    """Characteristic length of a plate on a Winkler foundation k = Ec / hc."""
    d = e * t ** 3 / (12 * (1 - NU ** 2))
    return (d / (EC / HC)) ** 0.25


def solve(fn, lo: float = 0.2, hi: float = 12.0) -> float:
    """Smallest t in [lo, hi] (mm) for which fn(t) is True (monotone), bisection."""
    if not fn(hi):
        return float("inf")
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if fn(mid) else (mid, hi)
    return hi


def case_free(span_in: float, e: float, s: float, fos: float) -> dict:
    a = span_in * MM_IN / 2
    allow = s / fos
    t_r = solve(lambda t: stress_ss(P_HAND, a, t) <= allow)
    t_d = solve(lambda t: defl_ss(P_HAND, a, t, e) <= DEFL_MAX)
    return {"span_in": span_in, "t_rupture_mm": t_r, "t_defl_mm": t_d}


def case_lattice(cell_in: float, e: float, s: float, fos: float) -> dict:
    a = cell_in * MM_IN / 2
    allow = s / fos
    t_r = solve(lambda t: stress_cl(P_HAND, a, t) <= allow)
    t_d = solve(lambda t: defl_cl(P_HAND, a, t, e) <= DEFL_MAX)
    return {"cell_in": cell_in, "t_rupture_mm": t_r, "t_defl_mm": t_d}


def case_foam(e: float, s: float, fos: float) -> dict:
    """Foam-backed skin: conservative bound = simply supported plate of radius 2 x the foundation
    characteristic length (the skin's bending is confined to about that radius)."""
    allow = s / fos
    t_r = solve(lambda t: stress_ss(P_HAND, 2 * foam_length(t, e), t) <= allow)
    t_d = solve(lambda t: P_HAND / (8 * math.sqrt((EC / HC) * e * t ** 3
                                                  / (12 * (1 - NU ** 2)))) <= DEFL_MAX)
    return {"t_rupture_mm": t_r, "t_defl_mm": t_d,
            "foam_length_at_1mm_mm": foam_length(1.0, e)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path)
    ap.add_argument("--orient", choices=("xy", "any"), default="any",
                    help="'xy': skin bends in the build plane (orientation fixed on the drawing); "
                         "'any': orientation not fixed, Z knockdown applied (default)")
    args = ap.parse_args(argv)
    e, s = props(args.orient)
    t_stiff = T_PETG * (E_PETG / e) ** (1 / 3)
    wrink = 0.5 * (e * EC * GC) ** (1 / 3)
    out: dict = {"orient": args.orient, "E_flex_mpa": e, "sigma_flex_mpa": s,
                 "t_process_mm": T_PROC, "t_stiffness_parity_mm": t_stiff,
                 "wrinkling_stress_mpa": wrink, "cases": {}}
    print(f"PA CF, orientation '{args.orient}': E_flex {e:.0f} MPa, sigma_flex {s:.0f} MPa "
          f"(typical, REF-MAT-015{'; Z knockdown 0.5 ASSUMED' if args.orient == 'any' else ''})")
    print(f"process floor {inch(T_PROC)}; stiffness parity with 2.0 mm CF-PETG {inch(t_stiff)}")
    for lb, fos in (("non-load-bearing", FOS_NLB), ("load-bearing", FOS_LB)):
        res: dict = {}
        fr = case_foam(e, s, fos)
        free = [case_free(sp, e, s, fos) for sp in SPANS_IN]
        lat = [case_lattice(c, e, s, fos) for c in CELLS_IN]
        floor = T_PROC if lb == "non-load-bearing" else max(T_PROC, t_stiff)
        res["foam_backed"] = {**fr, "t_min_mm": max(floor if lb == "non-load-bearing" else T_PROC,
                                                    fr["t_rupture_mm"], fr["t_defl_mm"])}
        res["free_standing"] = [{**c, "t_min_mm": max(floor, c["t_rupture_mm"], c["t_defl_mm"])}
                                for c in free]
        res["lattice"] = [{**c, "t_min_mm": max(T_PROC, c["t_rupture_mm"], c["t_defl_mm"])}
                          for c in lat]
        out["cases"][lb] = res
        print(f"\n{lb.upper()} (factor {fos:.2f} on the {P_HAND / 4.44822:.0f} lbf handling load)")
        f = res["foam_backed"]
        print(f"  foam-backed: rupture {inch(f['t_rupture_mm'])}, deflection {inch(f['t_defl_mm'])}"
              f" -> min {inch(f['t_min_mm'])}")
        for c in res["free_standing"]:
            print(f"  free-standing, span {c['span_in']:.2f} in: rupture {inch(c['t_rupture_mm'])},"
                  f" deflection {inch(c['t_defl_mm'])} -> min {inch(c['t_min_mm'])}")
        for c in res["lattice"]:
            print(f"  lattice, node pitch {c['cell_in']:.3f} in: rupture {inch(c['t_rupture_mm'])},"
                  f" deflection {inch(c['t_defl_mm'])} -> min {inch(c['t_min_mm'])}")
    print(f"\nface-wrinkling limit on a foam-backed skin (in-plane compression): {wrink:.1f} MPa "
          f"({wrink * 145.04:.0f} psi), independent of skin thickness")
    if args.json:
        args.json.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
