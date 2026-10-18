#!/usr/bin/env python3
"""
nacelle_64_proportion_trade.py — multi-objective sweep of the 64 mm nacelle's
proportions: canonical shape, weight, drag and packaging, with thrust-side
inlet constraints.

WHY
---
Owner direction 2026-10-03: "use the minimum radial scale and lengthen to
canon at that diameter, but optimize for aerodynamics, thrust, weight, and
canonical shape."  The canonical engine [REF-CAD-003] measures L/D about 2.24
in plan (Sheet 4, 166 / 74 px) and 2.31 in side view (Sheet 3 VTOL, 164 / 71
px), and is nearly round in section.  The 50 mm shell is narrow spanwise
(75.4 x 83.3 mm), so the sweep scales X and Y separately.

VARIABLES
---------
  KX, KY   radial scale of the measured shell, spanwise / fore-aft (flight
           vertical).  KX >= 41.0/34.0 (pylon wall: bore 32 + duct wall 2.5 +
           6.0 disconnect pocket + 0.5 material, against the 34.0 face).
           KY >= 42.86/35.86: the ESC-bay skin (min r 35.86 at az 90, Z 87 on
           the measured grid) must keep the 50 mm pod's 5.66 mm over the
           board seat, which moves 30.2 -> 37.2 mm.
  A        uniform axial stretch of the canonical shell (silhouette kept);
           the nozzle pocket and its iris ride on the shell's aft end.
  BELL_L   intake bell length; the stack starts at the in-bell rotor
           station (tip-gap growth <= 0.1 mm) for that bell.
  F        lip flare.  F >= 6.5 mm is the only rounded lip VALIDATED attached
           by tools/nacelle_intake_cfd.py (both meshes); a longer bell at the
           same flare is gentler, which the CFD check of the pick confirms.

CONSTRAINTS: axial motor margin >= MIN_MARGIN; hover clearance on the 3.0 in
flight gear >= MIN_CLEAR.

OBJECTIVES (all minimised, equally weighted, each normalised to the K 1.28 /
A 1.0 baseline that tools/nacelle_mass_cg_64.py measured):
  canon   worst |L/D / canon - 1| over plan and side views;
  weight  rotating mass change, fraction of 954 g;
  drag    frontal-area change (cruise/hover body drag scales with it) plus
          half the wetted-area change (skin friction), fraction of baseline.
Thrust enters through the constraints: the lip must be the validated
attached design and the rotor tip may not see more than 0.1 mm extra gap, so
no candidate trades inlet quality away.  Mass feeds T/W directly.

MASS MODEL (est., stated):  pod = 283.4 g x P^1.55 x A, where P is the
perimeter ratio and 1.55 is calibrated between the two rendered pods (193.3 g
at K 1.0, 283.4 g at K 1.28).  Sleeves scale with mean K over fixed lengths;
nozzle parts with mean K; motors, rotors, ESCs, servo and on-axis items are
fixed (tools/nacelle_mass_cg_64.py rows).  Re-measure the chosen design by
rendering it — this sweep only ranks candidates.

Usage:
    /usr/bin/python3 tools/nacelle_64_proportion_trade.py [--top N] [--json]

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CEH (GitHub Stab-Rabbit-coding) —
optimisation goals and owner decisions.  Tool by Claude (Claude Opus 5.5,
Anthropic) under the author's direction, per AGENTS.md AI attribution.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys

# ── Canon [REF-CAD-003] ──────────────────────────────────────────────────────
CANON_LD_PLAN = 166.0 / 74.0    # Sheet 4 dorsal plan
CANON_LD_SIDE = 164.0 / 71.0    # Sheet 3 VTOL side

# ── 50 mm shell (measured) ───────────────────────────────────────────────────
L0, X0, Y0 = 185.2, 75.4, 83.3  # mm length, spanwise width, fore-aft depth
KX_MIN = 41.0 / 34.0            # pylon wall (module docstring)
KY_MIN = (37.2 + (35.86 - 30.2)) / 35.86   # ESC-bay skin over the seat

# ── Stack (QF2822, adopted stator-as-mount) [REF-EDF-003] ────────────────────
R_BORE = 32.0
STACK_L = 2 * 72.7 + 1.0        # two stages + interstage gap, mm
NOZ_Z0 = 166.25                 # nozzle pocket station at A = 1
NOZ_REACH = 221.3 - 166.25      # iris reach aft of the pocket (40 mm flaps)
TIP_GROWTH = 0.1                # mm, rotor-in-bell rule

# ── Baseline roll-up (tools/nacelle_mass_cg_64.py, K 1.28, A 1.0) ───────────
BASE_MASS = 954.2
BASE_K = 1.28
POD_EXP = math.log(283.4 / 193.3) / math.log(1.28)   # = 1.55
# Pod calibration point — the RENDERED pick (K 1.21, A 1.15, elliptical lip,
# forebody inside the skin): 270.6 g, CG 94.9 mm (tools/nacelle_mass_cg_64.py,
# 2026-10-03).  Re-calibrated after the first pick rendered 66 g heavier than
# this model predicted, because its forebody stood proud of the skin.
POD_CAL_G, POD_CAL_A, POD_CAL_CGF = 270.6, 1.15, 94.9 / (185.2 * 1.15)
POD_CAL_P = (1.21 * X0 + 1.21 * Y0) / (BASE_K * (X0 + Y0))
SPAR_HULL_Z = 66.851            # built spar height (nacelle_mass_cg.py)
GROUND_3IN = -80.0              # 3.0 in flight gear ground plane, hull Z

MIN_MARGIN = 3.0                # mm axial motor margin (drawing values)
MIN_CLEAR = 12.7                # mm hover clearance, 0.5 in


def rotor_entry(bell_l: float, flare: float) -> float:
    """In-bell rotor station for a quarter-elliptical lip (bisection)."""
    def r(z: float) -> float:
        u = 1.0 - z / bell_l
        return R_BORE + flare * (1.0 - math.sqrt(max(0.0, 1.0 - u * u)))
    lo, hi = 0.0, bell_l
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if r(mid) - R_BORE > TIP_GROWTH else (lo, mid)
    return hi


def evaluate(kx: float, ky: float, a: float, bell_l: float,
             flare: float) -> dict:
    """Metrics for one candidate."""
    length = L0 * a
    kbar = 0.5 * (kx + ky)
    perim = (kx * X0 + ky * Y0) / (BASE_K * (X0 + Y0))
    z_r = rotor_entry(bell_l, flare)
    z_noz = NOZ_Z0 * a
    margin = z_noz - (z_r + STACK_L)

    # Stations relative to the stack start (baseline z_r = 17.49).
    sh = z_r - 17.49
    rows = [
        (POD_CAL_G * (perim / POD_CAL_P) ** POD_EXP * a / POD_CAL_A,
         POD_CAL_CGF * length),                                    # pod
        (75.0 * kbar / BASE_K, 59.9 + sh),                         # stator sleeve
        (54.5 * kbar / BASE_K, 129.3 + sh),                        # aft sleeve
        (135.0, 61.2 + sh), (135.0, 134.9 + sh),                   # motors
        (20.0, 22.8 + sh), (20.0, 96.5 + sh),                      # rotors
        (84.0 + 17.9, 95.0 * a),                                   # ESCs + covers
        (27.4 * kbar / BASE_K, z_noz + 8.55),                      # throat+housing
        (8.6 * kbar / BASE_K, z_noz + 3.65),                       # ring
        (27.0 * kbar / BASE_K, z_noz + 31.95),                     # flaps
        (8.0, z_noz - 16.25),                                      # servo drive
        (21.8, 90.0 + sh),                                         # harness
    ]
    off_m = sum(m for m, _ in rows)
    cg = sum(m * z for m, z in rows) / off_m
    mass = off_m + 32.1                                            # on-axis items
    arm = z_noz + NOZ_REACH - cg
    clear = (SPAR_HULL_Z - arm) - GROUND_3IN

    ld_plan = length / (X0 * kx)
    ld_side = length / (Y0 * ky)
    canon = max(abs(ld_plan / CANON_LD_PLAN - 1), abs(ld_side / CANON_LD_SIDE - 1))
    frontal = (kx * ky) / BASE_K ** 2 - 1
    wetted = perim * a - 1
    weight = mass / BASE_MASS - 1
    drag = frontal + 0.5 * wetted
    return {"kx": kx, "ky": ky, "a": a, "length": length, "bell_l": bell_l,
            "flare": flare, "rotor_z": z_r, "margin": margin, "pivot": cg,
            "mass": mass, "clear": clear, "ld_plan": ld_plan,
            "ld_side": ld_side, "canon": canon, "weight": weight,
            "drag": drag, "score": canon + weight + drag,
            "feasible": (kx >= KX_MIN - 1e-9 and ky >= KY_MIN - 1e-9
                         and margin >= MIN_MARGIN and clear >= MIN_CLEAR
                         and flare >= 6.5)}


def frange(lo: float, hi: float, step: float) -> list[float]:
    """Inclusive grid that starts EXACTLY at lo (a rounded start can fall
    below a hard minimum and silently drop the bound itself)."""
    n = int((hi - lo) / step + 1e-9)
    return [lo + i * step for i in range(n + 1)]


def sweep() -> list[dict]:
    """Grid over KX, KY, A, bell length and flare."""
    return [evaluate(kx, ky, a, bl, f) for kx, ky, a, bl, f in itertools.product(
        frange(KX_MIN, 1.32, 0.01), frange(KY_MIN, 1.32, 0.01),
        frange(1.0, 1.25, 0.01), frange(19.5, 40.0, 2.5), (6.5, 7.5, 8.5))]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    res = sorted((r for r in sweep() if r["feasible"]), key=lambda r: r["score"])
    base = evaluate(1.28, 1.28, 1.0, 19.5, 6.5)
    if args.json:
        print(json.dumps({"baseline": base, "top": res[:args.top]}, indent=4))
        return 0 if res else 2
    hdr = (f"{'KX':>5}{'KY':>6}{'A':>6}{'L mm':>7}{'bell':>6}{'F':>5}"
           f"{'L/D pl':>8}{'L/D sd':>8}{'mass g':>8}{'pivot':>7}{'clr mm':>8}"
           f"{'marg':>6}{'canon':>7}{'wt':>7}{'drag':>7}{'score':>7}")
    print(f"canon L/D plan {CANON_LD_PLAN:.2f}, side {CANON_LD_SIDE:.2f}; "
          f"KX >= {KX_MIN:.3f}, KY >= {KY_MIN:.3f}")
    print(hdr)
    for r in [base] + res[:args.top]:
        print(f"{r['kx']:5.2f}{r['ky']:6.2f}{r['a']:6.2f}{r['length']:7.1f}"
              f"{r['bell_l']:6.1f}{r['flare']:5.1f}{r['ld_plan']:8.2f}"
              f"{r['ld_side']:8.2f}{r['mass']:8.1f}{r['pivot']:7.1f}"
              f"{r['clear']:8.1f}{r['margin']:6.1f}{r['canon']:7.3f}"
              f"{r['weight']:+7.3f}{r['drag']:+7.3f}{r['score']:7.3f}"
              + ("   <- baseline (K 1.28, A 1.0)" if r is base else ""))
    return 0 if res else 2


if __name__ == "__main__":
    sys.exit(main())
