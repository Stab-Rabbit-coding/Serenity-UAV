#!/usr/bin/env python3
"""skid_open_items.py -- the five open items of the elastic PA12-CF skid design
(docs/SKID_FAILURE_MODE_STUDY.md section 9.3), on the CURRENT specification
(owner, 2026-10-31: no design changes; flag anything that breaks a spec).

  1. Stroke margin: how much softer can the as-built skid be before the 4 ft
     co-strike stroke exceeds the 0.217 in (5.5 mm) limit?  Sources of softness:
     SLS wall tolerance, modulus scatter, strut/rib compliance.
  2. Single-skid (rolled) strike: one skid with the aft gear pair, pitch dynamics
     only (no roll relief) -- a conservative bound.
  3. Rib to CF-frame joint: 2 x M3 in single shear through the rib flange and the
     2 mm CF plate; bearing in both; moment as a bolt couple.
  4. Interior clearance -- done by mesh in the session (no conflict); recorded in docs.
  5. Co-planarity of aft feet and skid tips (R1, +/-1 mm): tolerance stack, and the
     effect of a skid-height offset on hull clearance (which is the stroke limit).

US customary first.  Run:  /usr/bin/python3 tools/skid_open_items.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude Opus 5.5 (Anthropic) under the author's direction, 2026-10-31.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tail_strike_requirement as ts  # noqa: E402

LBF, IN = 4.44822, 25.4
K_SKID = 218.0          # N/mm per skid, size_elastic_design() (1,244 lbf/in)
S_LIMIT = 5.5           # mm stroke limit (6.5 mm clearance - 1 mm margin)
CLEAR = 6.5             # mm measured hull clearance at skid contact
F_STRUT = 2177.0        # N per side (size_elastic_design)
M_RIB = F_STRUT * 24.3  # N.mm at the frame end of the rib
SHEAR_M3 = 2113.0       # N, M3 A2-70 single-shear capacity (tools/landing_gear_r6_sizing.py)
FLAG = []


def case():
    th0, pt, _f = ts.tip_back()
    _n, m, cy, cz, k = ts.design_case()
    sched, smax = ts.gear_schedule_at(m)
    t = math.radians(th0)
    cg, sp = ts.rot((cy, cz), t), ts.rot(pt, t)
    return (m, k / 1000, (ts.Y_FOOT_AFT - cg[0]) / 1000, (sp[0] - cg[0]) / 1000,
            2 * sched["f_leg_n"], smax)


def item1(m, k, d1, d2, fg):
    print("ITEM 1 -- stroke margin vs as-built skid stiffness (4 ft co-strike)")
    k_lim = None
    for frac in (1.10, 1.05, 1.00, 0.97, 0.95, 0.90, 0.85, 0.80):
        r = ts.co_strike(m, k, d1, d2, fg, 0.0, skid_k=2 * K_SKID * frac, dt=2e-6)
        s = r["s_skid_max_mm"]
        if s <= S_LIMIT:
            k_lim = frac                                # lowest stiffness that still passes
        print(f"  k x{frac:.2f} ({K_SKID * frac * IN / LBF:5.0f} lbf/in): stroke {s / IN:.3f} in "
              f"({s:.2f} mm) {'OVER 0.217 in' if s > S_LIMIT else 'ok'}")
    # stroke ~ k^-1/2 near the design point -> a 3.8 % stiffness drop costs ~1.9 % stroke
    print("  Tolerance contributors to k (thin-wall I ~ t; k ~ E I):")
    t_nom = 2.3 * 2.4                                   # mm, grown wall at the critical zone
    dt_sls = 0.3                                        # mm SLS tolerance (3d-print-design skill)
    print(
        f"    SLS wall +/-{dt_sls} mm on ~{t_nom:.1f} mm wall -> I +/-{100 * dt_sls / t_nom:.0f} %")
    print(
        "    Flexural modulus lot / orientation scatter: no data in 3DS-30108A -> +/-10 % "
        "[ASSUMED]")
    worst = (1 - dt_sls / t_nom) * 0.90
    print(f"  worst-case k = x{worst:.2f} of nominal")
    r = ts.co_strike(m, k, d1, d2, fg, 0.0, skid_k=2 * K_SKID * worst, dt=2e-6)
    print(
        f"  -> stroke {r['s_skid_max_mm'] / IN:.3f} in ({r['s_skid_max_mm']:.2f} mm) vs limit "
        "0.217 in")
    if r["s_skid_max_mm"] > S_LIMIT:
        FLAG.append(f"ITEM 1 BREAKS R2/CS-7: at worst-case stiffness (x{worst:.2f}) the 4 ft "
                    "stroke is "
                    f"{r['s_skid_max_mm'] / IN:.3f} in > 0.217 in.  As-built acceptance must "
                    "require "
                    f"k >= {K_SKID * (k_lim or 1) * IN / LBF:.0f} lbf/in per skid (x{k_lim:.2f}; "
                    "bench test), or the "
                    f"design needs stiffness margin (not changed per owner).")
    return k_lim


def item2(m, k, d1, d2, fg, smax):
    print("\nITEM 2 -- single-skid strike (one skid + aft gear pair, pitch only, no roll relief)")
    r = ts.co_strike(m, k, d1, d2, fg, 0.0, skid_k=K_SKID, dt=2e-6)
    s, fpk = r["s_skid_max_mm"], r["f_skid_peak"]
    # strut/skid-force ratio from size_elastic_design
    strut = fpk * F_STRUT / 1181.0
    print(f"  skid stroke {s / IN:.3f} in ({s:.2f} mm); skid peak {fpk / LBF:.0f} lbf ({fpk:.0f} "
          "N); "
          f"strut on that side {strut / LBF:.0f} lbf; gear stroke {r['s_gear_mm'] / IN:.2f} in")
    stress_ratio = fpk / 1181.0 * 0.95                  # peak vs the 0.95 x ultimate design peak
    print(f"  skid stress ~{stress_ratio:.2f} x ultimate (design point 0.95 x at 1,181 N)")
    print(f"  cross member: pads at the skid junctions -> the loaded side reacts its own skid; "
          f"torsion into the U-frame ~{fpk * 45 / 1000 * 8.851:.0f} lbf.in [lever 45 mm, ASSUMED]")
    if s > S_LIMIT:
        FLAG.append("ITEM 2 BREAKS R2/CS-7 (conservative bound, no roll relief): a single-skid "
                    f"strike strokes {s / IN:.3f} in > 0.217 in "
                    f"(hull contact) under the conservative pitch-only bound.")
    if stress_ratio > 1.0:
        FLAG.append(f"ITEM 2 BREAKS TS-5 intent: single-skid peak {fpk / LBF:.0f} lbf puts the "
                    "skid at "
                    f"~{stress_ratio:.2f} x ultimate -> skid fracture before the hull is "
                    "protected.")
    if r["s_gear_mm"] > smax:
        FLAG.append("ITEM 2 BREAKS R3: gear stroke over the settle limit in the single-skid case.")


def item3():
    print("\nITEM 3 -- rib to CF ring frame joint (per side)")
    # (a) Concept as specified: rib cantilevered aft from the frame.  The rib end moment is
    #     OUT OF PLANE for the 2 mm CF plate frame (plate in the X-Z plane at Y 595.7).
    # mm frame band (BOM estimate), plate thickness
    band, t = 10.0, 2.0
    z_plate = band * t ** 2 / 6
    sig = M_RIB / z_plate
    print(f"  (a) cantilever from the frame: {M_RIB / 1e3 * 8.851:.0f} lbf.in out of plane on a "
          f"{t:.0f} mm x "
          f"{band:.0f} mm CF band -> {sig * 145.04:,.0f} psi ({sig:,.0f} MPa): the plate cannot "
          "react it")
    FLAG.append("ITEM 3 BREAKS the specified joint: a rib cantilevered from the 2 mm CF ring "
                "frame puts "
                f"{M_RIB / 1e3 * 8.851:.0f} lbf.in out of plane on the plate (~{sig:,.0f} MPa).  "
                "Resolution below "
                f"lengthens the rib (+~0.30 oz pair).")
    # (b) Resolution: rib passes OVER the frame as a lever, bonded/bolted to the 2 mm skin zone.
    # mm: pad->frame, frame->forward tie (Y ~572)
    a_aft, a_fwd = 24.3, 23.7
    # N, forward tie pulls the rib DOWN to the skin
    tie = F_STRUT * a_aft / a_fwd
    frame_v = F_STRUT + tie                             # N, frame reaction, in plane (vertical)
    t_bolt = tie / 2
    tens_m3 = 3521.0                                    # N M3 A2-70 tension (gear tool)
    tau_skin = 0.6 * 84.0                               # MPa, shear-out ~0.6 x ultimate [ASSUMED]
    pull = math.pi * 5.5 * 2.0 * tau_skin               # N, washer O5.5 punching a 2 mm skin
    print("  (b) lever over the frame (Y ~572-620, bonded to the 2 mm skin zone):")
    print(f"      forward tie {tie / LBF:.0f} lbf (2 x M3 in tension: {t_bolt / LBF:.0f} lbf each, "
          "FOS "
          f"{tens_m3 / t_bolt:.1f}); skin pull-through {pull / LBF:.0f} lbf per bolt -> FOS "
          f"{pull / t_bolt:.2f}")
    print(f"      frame reaction {frame_v / LBF:.0f} lbf IN PLANE (vertical) into the CF ring -- "
          "the direction "
          f"a plate frame carries; CF bearing on the rib saddle unsourced -> coupon (WBS 0.12)")
    rib_extra = 6.0 * 26.0 * a_fwd * 1.11e-3
    print(
        f"      rib grows forward by {a_fwd / IN:.2f} in: +{rib_extra / 28.35:.2f} oz "
        f"({rib_extra:.1f} g) per side")
    if pull / t_bolt < 1.5:
        FLAG.append(f"ITEM 3 (b): skin pull-through FOS {pull / t_bolt:.2f} < 1.5 at the forward "
                    "tie -> "
                    "add a backing washer plate.")


def item5(m, k, d1, d2, fg):
    print("\nITEM 5 -- co-planarity of aft feet and skid tips (R1: +/-1 mm)")
    # +/-0.3 % or +/-0.3 mm per SLS dimension (3d-print-design skill, SLS rules)
    contrib = {
        "U-frame: ring mount to skid tip (~200 mm)": 0.003 * 200,
        "middle shell ring seat to aft gear bay (~80 mm)": 0.3,
        "gear leg frame 3.0 in (121 mm)": 0.003 * 121,
        "bay plate + foot (two parts)": math.hypot(0.3, 0.3),
        "ductile/spring wire bow set (h0)": 0.2,
        "ring-to-hull bolted joint fit": 0.2,
    }
    rss = math.sqrt(sum(v * v for v in contrib.values()))
    for kk, v in contrib.items():
        print(f"    {kk:46s} +/-{v / IN:.3f} in ({v:.2f} mm)")
    print(
        f"  RSS stack +/-{rss / IN:.3f} in ({rss:.2f} mm); worst-case sum "
        f"+/-{sum(contrib.values()) / IN:.3f} in")
    # The hull clearance at skid contact is measured skid-tip to hull on the same U-frame /
    # rear shell pair; only the skid-to-hull part of the stack eats the 1 mm margin.
    skid_hull = math.hypot(0.003 * 200, 0.2)
    print(
        f"  skid-tip-to-hull part (eats the 1 mm stroke margin): +/-{skid_hull / IN:.3f} in "
        f"({skid_hull:.2f} mm)")
    stroke = 5.42
    left = CLEAR - skid_hull - stroke
    print(f"  stroke {stroke} mm + margin must fit in {CLEAR} - {skid_hull:.2f} (tolerance) = "
          f"{CLEAR - skid_hull:.2f} mm -> margin left {left / IN:.3f} in ({left:.2f} mm) vs 1 mm "
          "required")
    if left < 1.0:
        FLAG.append("ITEM 5 BREAKS CS-2/CS-7 margin: with the skid-to-hull tolerance "
                    f"(+/-{skid_hull:.2f} mm) "
                    f"the worst-case hull margin is {left:.2f} mm < 1 mm (the hull still clears; "
                    "the margin "
                    f"spec is not met).")
    if rss > 1.0:
        FLAG.append(f"ITEM 5 BREAKS R1: the feet/skid-tip co-planarity stack is +/-{rss / IN:.3f} "
                    "in "
                    f"({rss:.2f} mm) RSS > +/-1 mm.  Needs a shim / measure-and-set step at "
                    "assembly.")


def main():
    m, k, d1, d2, fg, smax = case()
    item1(m, k, d1, d2, fg)
    item2(m, k, d1, d2, fg, smax)
    item3()
    item5(m, k, d1, d2, fg)
    print("\nFLAGS (spec breaks):" if FLAG else "\nNo spec breaks.")
    for f in FLAG:
        print("  - " + f)


if __name__ == "__main__":
    main()
