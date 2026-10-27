#!/usr/bin/env python3
"""Serenity UAV -- landing-gear thigh: grown printed section vs anchored CF-rod core.

LG-REMASS (2026-10-19).  Owner request: "I'm leaning toward the cf rod core,
but I want to see it in action, both normal and crash.  How would each fail
and how easy would each be to repair/replace?"  This tool is the numbers half;
the renders come from canonical_leg_r6_3_0in.scad THIGH_VARIANT.

Load cases come from tools/landing_gear_r6_sizing.py at the 13.0 lbm design
mass: hip moment M = F_leg x R_H, with F_leg the ductile plateau (crash, 4 ft)
or the spring elastic limit (ordinary, LG-06 1.5 ft inside the 13.7 mm nozzle
clearance).  Both are IMPACT loads, held to the sizing tool's conventions:

* CF-PETG bending allowable 27.5 MPa = yield / 2 (LANDING_GEAR_ANALYSIS SS4.6,
  sizing SIGMA_ALLOW_PETG); CF-PETG bearing 70 MPa (sizing LG-02).
* CF rod: 300 MPa conservative STAND-IN, NOT a qualified allowable
  (docs/TILT_SPAR_ANALYSIS.md SS3.6.3; WBS A7 CF certificate open).
* Steel pin double shear: 2 x 0.6 x 500 MPa x A, the sizing tool's hip-pin basis.
* Rod-to-PETG bond: ~5 MPa bond-limited figure the repo already uses
  (REFERENCES.md CARGO-03c row, wing-root two_rod path).

Section properties by the parallel-axis theorem [REF-NCEES-009]; the root
section is idealised as the twin cylinders plus web, as the sizing tool does.

Run: /usr/bin/python3 tools/lg_thigh_variants.py

Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CEH (GitHub Stab-Rabbit-coding)
AI note : Written by Claude (Claude Opus 5.5, Anthropic) under the author's
          direction, 2026-10-19, per AGENTS.md AI attribution.
License : MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import landing_gear_r6_sizing as lgs  # noqa: E402

R_H = lgs.R_H_BUILT
SIG_PETG = lgs.SIGMA_ALLOW_PETG       # 27.5 MPa
BEAR_PETG = 70.0                      # MPa
SIG_CF = 300.0                        # MPa, STAND-IN
TAU_PIN = 0.6 * 500.0                 # MPa, sizing hip-pin basis
TAU_BOND = 5.0                        # MPa
RHO_PRINT, RHO_CF = 1.05e-3, 1.6e-3   # g/mm^3 (CF laminate ESTIMATE)
LUG_W = 14.0
THIGH_LEN = 88.5                      # hip -> knee, SCAD KNEE comment


def cases() -> dict[str, float]:
    m = lgs.M_AUW_KG
    u_crash = m * lgs.G * 4.0 * lgs.FT * 0.5
    f_crash = u_crash * 1000.0 / (lgs.CLEARANCE_COMPACT - lgs.RESIDUAL_MIN)
    share = max((lgs.Y_CG - lgs.Y_FOOT_FORE), (lgs.Y_FOOT_AFT - lgs.Y_CG)) \
        / lgs.WHEELBASE / 2.0
    u_ord = share * m * lgs.G * 1.5 * lgs.FT
    f_ord = u_ord * 1000.0 / lgs.NOZZLE_TIP_CLEAR_3IN
    return {"ordinary (LG-06, 1.5 ft)": f_ord * R_H, "crash (LG-17, 4 ft)": f_crash * R_H}


def z_twin(d_cyl: float, c: float, bore: float) -> float:
    """Section modulus of twin cylinders (+ web) about the swing-plane axis."""
    r = d_cyl / 2.0
    a = math.pi * (r * r - (bore / 2.0) ** 2)
    i_c = math.pi * (d_cyl ** 4 - bore ** 4) / 64.0
    i = 2.0 * (i_c + a * (c / 2.0) ** 2) + d_cyl * c ** 3 / 12.0
    return i / (c / 2.0 + r)


def grown(m_nmm: float) -> list[tuple[str, float, float]]:
    """(mode, demand, capacity) for the 17 mm / 22 mm all-printed thigh."""
    s = m_nmm / z_twin(17.0, 22.0, 6.0)
    return [("root bending, CF-PETG (bored section, conservative)", s, SIG_PETG)]


def cf_core(m_nmm: float, pin_d: float = 3.0, rod_d: float = 6.0) -> list:
    """(mode, demand, capacity) for the anchored CF core, rods alone."""
    c = 18.0
    f_rod = m_nmm / c                                  # couple force per rod, N
    a_rod = math.pi * rod_d ** 2 / 4.0
    a_net = a_rod - pin_d * rod_d                      # cross-hole through the rod
    l_bond = THIGH_LEN - 6.0
    return [
        ("rod gross section, CF", f_rod / a_rod, SIG_CF),
        ("rod NET section at the cross-pin hole, CF", f_rod / a_net, SIG_CF),
        ("cross-pin double shear, steel (N)", f_rod, 2 * TAU_PIN * math.pi * pin_d ** 2 / 4),
        ("cross-pin bearing in the PETG lug (N)", f_rod, BEAR_PETG * pin_d * LUG_W),
        ("bond, KNEE side of the root section (N)", f_rod,
         TAU_BOND * math.pi * rod_d * l_bond),
        # The hip moment is greatest at the root lug.  The rod force there must be
        # anchored on the HUB side, where only CF_PIN_AT + ~3 - CF_ROD_START
        # ~ 8 mm of rod exists -- hence the cross-pin.  Bond alone over 8 mm:
        ("bond alone, HUB side, 8 mm (why the pin is needed) (N)", f_rod,
         TAU_BOND * math.pi * rod_d * 8.0),
    ]


def masses() -> dict[str, float]:
    """Delta mass per leg vs baseline (PETG cylinders over the thigh length)."""
    def cyl_vol(d, bore):
        return 2 * math.pi / 4 * (d * d - bore * bore) * (THIGH_LEN - 16)
    base = cyl_vol(14, 6) * RHO_PRINT
    g = cyl_vol(17, 6) * RHO_PRINT - base
    rods = 2 * math.pi / 4 * 36 * (THIGH_LEN - 4) * RHO_CF
    pins = 2 * math.pi / 4 * 9 * LUG_W * 7.85e-3
    removed_petg = 2 * math.pi / 4 * 6.2 ** 2 * 14 * RHO_PRINT   # bore extended thru lug
    return {"grown": g, "cf_core": rods + pins - removed_petg}


SIG_FLEX_ULT_PETG = 54.0     # MPa, CF-PETG ASTM D790 flexural strength [REF-MAT-002]
HIERARCHY_MIN = 1.25         # declared: mount capacity / leg breaking capacity
BOLT_PATTERN = 68.0          # mm, bay bolt pattern up the canted plane (sizing LG-02)
BOLT_T_CAP = 700.0 * 5.03    # N, M3 A2-70 tension (sizing LG-02)
BEAR_STACK_T = 10.0          # mm, wall + boss + backing plate (sizing LG-02)


def leg_breaking_moment(variant: str) -> tuple[float, str]:
    """Hip moment at which the LEG itself breaks (ultimate, not allowable)."""
    if variant == "grown":
        return SIG_FLEX_ULT_PETG * z_twin(17.0, 22.0, 6.0), "root bending at CF-PETG flex strength"
    # cf_core: the weakest anchor mode sets it (all of these are IN the leg)
    f = min(BEAR_PETG * 3.0 * LUG_W, 2 * TAU_PIN * math.pi * 9 / 4,
            SIG_CF * (math.pi * 9 - 3.0 * 6.0))
    return f * 18.0, "anchor (cross-pin bearing in the leg lug)"


def mount_capacities(m_leg: float) -> list[tuple[str, float, float]]:
    """(item, demand at the leg's breaking moment, capacity) for bay/bolts/pin."""
    f_leg = m_leg / R_H
    tension = m_leg / BOLT_PATTERN / 2.0
    shear = f_leg / 4.0
    res = math.hypot(tension, shear)
    return [
        ("bay M3 bolt tension (N)", tension, BOLT_T_CAP),
        ("bolt-hole bearing, bay + hull stack (N)", res, BEAR_PETG * 3.0 * BEAR_STACK_T),
        ("hip pin M3 double shear (N)", f_leg, 2 * TAU_PIN * math.pi * 9 / 4),
    ]


def hierarchy() -> bool:
    """Owner rule 2026-10-19: the leg must break before the bay or the hull."""
    ok_all = True
    print("\n== FAILURE HIERARCHY (owner rule: leg breaks before bay / hull) ==")
    print(f"   required: every mount capacity >= {HIERARCHY_MIN} x its demand at the "
          "leg's own breaking moment")
    for v in ("grown", "cf_core"):
        m_u, mode = leg_breaking_moment(v)
        print(f"  {v}: leg breaks at {m_u / 1000:.1f} N*m ({mode})")
        for item, dem, cap in mount_capacities(m_u):
            r = cap / dem
            ok = r >= HIERARCHY_MIN
            ok_all &= ok
            print(f"    {item:44s} {dem:7.0f} vs {cap:7.0f} N  ratio {r:5.2f} "
                  f"{'OK' if ok else 'MOUNT FAILS FIRST -- AUTOMATIC FAIL'}")
    # The bay wire bosses see the ductile wire PLATEAU force on every crash,
    # whatever the thigh is -- they must outlast the fuse, not just the design.
    m_crash = cases()["crash (LG-17, 4 ft)"]
    p_plateau = m_crash / (2.0 * lgs.R_WIRE)
    boss_cap = BEAR_PETG * (12 * 10 - 6 * 5)          # sizing tool's boss bearing area
    r = boss_cap / p_plateau
    ok_all &= r >= HIERARCHY_MIN
    verdict = ("OK" if r >= HIERARCHY_MIN
               else "MOUNT FAILS FIRST -- AUTOMATIC FAIL (grow the boss)")
    print(f"  both: bay wire-boss bearing vs ductile plateau {p_plateau:7.0f} vs "
          f"{boss_cap:7.0f} N  ratio {r:5.2f} {verdict}")
    need = HIERARCHY_MIN * p_plateau / BEAR_PETG
    print(f"        -> boss bearing area needed {need:.0f} mm^2 (sizing area 90 mm^2)")
    print("   NOTE: bay/hull bearing uses the 70 MPa CF-PETG bearing allowable against "
          "the leg's ULTIMATE moment -- conservative for the mount; the hull wall "
          "behind the seat collar is not modelled here (LG-14 drop test confirms).")
    return ok_all


def main() -> int:
    print("LG thigh variants at the 13.0 lbm design mass (impact allowables, see header)")
    worst: dict[str, float] = {}
    for name, m in cases().items():
        print(f"\n== {name}: hip moment {m / 1000:.1f} N*m ({m / 1000 * 8.851:.0f} lbf*in)")
        for label, fn in (("GROWN printed 17/22", grown), ("CF CORE 2x6 + 3 mm pins", cf_core),
                          ("CF CORE 2x6 + 4 mm pins", lambda x: cf_core(x, 4.0))):
            print(f"  {label}")
            for mode, dem, cap in fn(m):
                mar = cap / dem
                if "why" not in mode:          # explanatory row, not a load path
                    worst[label] = min(worst.get(label, 9e9), mar)
                unit = "N" if "(N)" in mode else "MPa"
                print(f"    {mode:55s} {dem:8.1f} vs {cap:7.1f} {unit:3}  margin "
                      f"{mar:5.2f}x {'OK' if mar >= 1 else 'FAILS'}")
    print("\nMass change per leg vs baseline:", {k: round(v, 1) for k, v in masses().items()},
          "g (x4 per aircraft)")
    print("Worst margin over both cases:", {k: round(v, 2) for k, v in worst.items()})
    return 0 if hierarchy() else 2


if __name__ == "__main__":
    sys.exit(main())
