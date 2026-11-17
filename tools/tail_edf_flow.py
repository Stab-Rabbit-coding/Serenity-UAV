#!/usr/bin/env python3
"""tail_edf_flow.py -- installed thrust, flow, flow split and pressure margin of the
tail EDF (QX 64 mm, QF2822 2300 KV, pusher) drawing all its air through the
interior from a louvred, screened cargo ramp and the bow inlets (plan 002 U3,
TEDF-03; requirements R2, R10, R27, R39; KTD2, KTD7).

EVERY RESULT IS PROVISIONAL.  The fan is a planning model (constant flow power,
calibrated to the maker's free-air static thrust); every loss coefficient, the
bow-inlet and Bay A areas and the stall pressure are ASSUMED and are labelled on
every run.  The owner's pre-G1 bench run replaces the calibration (plan U3 step 8).

METHOD (steady, incompressible, one-dimensional control volume; momentum theory
as given in the aeronautical-engineering skill, propulsion.md section 1).
  1. Fan: flow power P = Q * dp_fan is constant at a given throttle and scales as
     the cube of throttle (fan laws).  Calibrated at 100 % throttle so that the
     fan blowing free air out of its own rotor annulus gives the maker's static
     thrust T0 [REF-EDF-003]: v0 = sqrt(T0 / (rho A0)), P100 = T0 v0 / 2.  Thrust is
     then proportional to throttle squared in free air.  P is FLOW power: it is
     the ideal momentum-theory power, so it sits below the maker's electrical
     power; the ratio is printed.
  2. System: each element loses dp = (rho/2) K (Q/A)^2.  Series elements add
     R = K / A^2; parallel branches add as 1/sqrt(R_eq) = sum 1/sqrt(R_i), because
     they share one pressure drop.  The ramp and bow branches are in parallel and
     feed the interior stations in series, then the nozzle (exit kinetic energy,
     K = 1, at the nozzle area).  Energy balance with inlet total pressure p_in:
         p_in + P / Q = (rho/2) (R_branches + R_interior + 1 / A_n^2) Q^2
     which is the cubic (rho/2) R Q^3 - p_in Q - P = 0 with one positive root.
  3. Installed thrust is the nozzle momentum flux, T = rho Q^2 / A_n (exit static
     pressure ambient).  In the cruise case the inlet momentum (ram) drag is not
     charged: that case reports flow and split only.
  4. Stall margin = p_stall(throttle) - P / Q, with p_stall = p_stall_100 * throttle^2.
     p_stall_100 is ASSUMED (no maker fan curve exists for this unit); the
     provenance is printed with every margin.

VALIDITY ENVELOPE: incompressible, every Mach number below 0.3 (the run fails
with the limit named otherwise); steady; sea-level ISA air (rho 1.225 kg/m^3).
Straight-run friction is neglected (short, wide path), as in the node tool.

One limits list (`limits()`) drives both the printout and the exit code
(docs/solutions/conventions/one-limits-list-drives-the-printout-and-the-exit-code.md).

Run:
    /usr/bin/python3 tools/tail_edf_flow.py [--louvre-k 1.0] [--min-margin-kpa 0]

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Sonnet 5.5, Anthropic) under the author's
direction, 2026-11-17, per `AGENTS.md` section 3 AI attribution.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass, replace

G = 9.80665
LBF_N, PSI_PA, CFM_M3S, KT_MS, IN2_M2 = 4.44822, 6894.757, 4.71947e-4, 0.514444, 6.4516e-4


@dataclass(frozen=True)
class Inputs:
    """Every ASSUMED field says so; the rest cite their source."""

    rho: float = 1.225  # kg/m^3, ISA sea level
    a_sound: float = 340.3  # m/s, ISA sea level
    mach_limit: float = 0.3  # incompressible validity limit
    # Maker's figures [REF-EDF-003, second sheet, 24 V, 100 %]: 2370 gf, 57.0 A, 1368 W.
    t_free_n: float = 2370.0 * G / 1000.0
    p_elec_w: float = 1368.0
    # Rotor annulus (64 mm rotor, ASSUMED 28 mm hub, plan "Ramp opening"): free-air exit.
    a_free: float = math.pi / 4 * (0.064 ** 2 - 0.028 ** 2)
    # Fixed elliptical nozzle 2.06 x 1.76 in (52.3 x 44.7 mm), R22.
    a_nozzle: float = math.pi / 4 * 0.0523 * 0.0447
    # Ramp branch: 2.0 x 1.4 in sealed fairing, 1,870 mm^2 (plan, cargo_layout_fit).
    a_ramp: float = 1.870e-3
    k_ramp_entry: float = 0.5  # ASSUMED sharp-edged entry
    k_screen: float = 1.0  # ASSUMED, on the gross ramp area
    sigma_louvre: float = 0.55  # open-area ratio (plan, ASSUMED)
    k_louvre: float = 1.0  # ASSUMED design case (KD15 low-loss); 0 = plain screened ramp
    blocked: float = 0.0  # fraction of the screen blocked, 0..1; 1 = bow inlets only
    # Bow branch: two 25 x 16 mm slots (node tool a_inlet_m2), then the Bay A duct.
    a_bow: float = 8.0e-4
    k_bow_inlet: float = 1.5  # ASSUMED (node tool: entry + expansion)
    a_bay_a: float = 1.2e-3  # ASSUMED, not measured (U7 and U13 set it)
    k_bay_a: float = 2.0  # ASSUMED
    # Interior, in series, from the closed-cavity figures of plan 001 "Measured Baseline".
    a_cargo: float = 1.275e-2  # m^2, midpoint of 11,800 to 13,700 mm^2
    k_cargo: float = 1.0
    a_cone: float = 9.48e-3  # m^2, rear cone at Y 600
    k_cone: float = 0.5  # ASSUMED
    k_fan_face: float = 0.4  # ASSUMED contraction to the rotor annulus
    p_stall_full_pa: float = 1.25 * PSI_PA  # ASSUMED (plan KTD7 text), not a maker curve
    min_margin_pa: float = 0.0  # R27 minimum: owner decision at G1, so 0 until then
    p_in_pa: float = 0.0  # inlet total pressure above ambient (still air)
    # Effective exit area of OPEN RCS jets, m^2 (sum of A_j / sqrt(1 + K_j)); 0 = jets closed.
    # They share the duct total pressure with the nozzle, so they add exit area and lower the
    # nozzle speed (plan "RCS jet model"); hover_trim_rcs.py sets it.
    a_jets_eff: float = 0.0


def flow_power_full(inp: Inputs) -> float:
    """Flow power at 100 % throttle, W, from the maker's free-air static thrust."""
    v0 = math.sqrt(inp.t_free_n / (inp.rho * inp.a_free))
    return 0.5 * inp.t_free_n * v0


def ramp_resistance(inp: Inputs) -> float | None:
    """R = K / A^2 of the ramp branch, 1/m^4; None when the screen is fully blocked."""
    if inp.blocked >= 1.0:
        return None
    a = inp.a_ramp
    return (inp.k_ramp_entry / a ** 2 + inp.k_louvre / (inp.sigma_louvre * a) ** 2
            + inp.k_screen / ((1.0 - inp.blocked) * a) ** 2)


def bow_resistance(inp: Inputs) -> float:
    return inp.k_bow_inlet / inp.a_bow ** 2 + inp.k_bay_a / inp.a_bay_a ** 2


def interior_resistance(inp: Inputs) -> float:
    return (inp.k_cargo / inp.a_cargo ** 2 + inp.k_cone / inp.a_cone ** 2
            + inp.k_fan_face / inp.a_free ** 2)


def branch_resistance(inp: Inputs) -> tuple[float, float, float | None]:
    """(R_equivalent of the two branches, R_bow, R_ramp or None)."""
    rr, rb = ramp_resistance(inp), bow_resistance(inp)
    conductance = 1.0 / math.sqrt(rb) + (0.0 if rr is None else 1.0 / math.sqrt(rr))
    return 1.0 / conductance ** 2, rb, rr


@dataclass(frozen=True)
class Result:
    theta: float
    flow_m3s: float
    flow_ramp_m3s: float
    flow_bow_m3s: float
    v_nozzle: float
    thrust_n: float  # nozzle thrust (the tail EDF thrust)
    p_duct_pa: float  # duct total pressure behind the fan: nozzle and jets exhaust from it
    thrust_free_n: float
    path_loss_pa: float
    dp_fan_pa: float
    margin_pa: float
    mach_max: float
    power_w: float


def operate(inp: Inputs, theta: float) -> Result:
    """Operating point at a throttle fraction (0 < theta <= 1)."""
    p = flow_power_full(inp) * theta ** 3
    r_br, rb, rr = branch_resistance(inp)
    a_exit = inp.a_nozzle + inp.a_jets_eff
    r_tot = r_br + interior_resistance(inp) + 1.0 / a_exit ** 2
    c = 0.5 * inp.rho * r_tot
    lo, hi = 1e-9, 10.0
    for _ in range(200):  # bisection on c Q^3 - p_in Q - P (one positive root)
        mid = 0.5 * (lo + hi)
        if c * mid ** 3 - inp.p_in_pa * mid - p > 0.0:
            hi = mid
        else:
            lo = mid
    q = 0.5 * (lo + hi)
    cb = 1.0 / math.sqrt(rb)
    cr = 0.0 if rr is None else 1.0 / math.sqrt(rr)
    q_bow, q_ramp = q * cb / (cb + cr), q * cr / (cb + cr)
    v_n = q / a_exit  # nozzle exit speed; the duct total pressure is (rho/2) v_n^2
    dp_fan = p / q
    v_ramp = q_ramp / (min(inp.sigma_louvre, 1.0 - min(inp.blocked, 0.999999)) * inp.a_ramp)
    speeds = (v_n, v_ramp, q_bow / inp.a_bow, q / inp.a_free, q / inp.a_cone, q / inp.a_cargo)
    return Result(
        theta=theta, flow_m3s=q, flow_ramp_m3s=q_ramp, flow_bow_m3s=q_bow, v_nozzle=v_n,
        thrust_n=inp.rho * inp.a_nozzle * v_n * v_n,
        p_duct_pa=0.5 * inp.rho * v_n * v_n, thrust_free_n=inp.t_free_n * theta ** 2,
        path_loss_pa=0.5 * inp.rho * (r_br + interior_resistance(inp)) * q * q,
        dp_fan_pa=dp_fan, margin_pa=inp.p_stall_full_pa * theta ** 2 - dp_fan,
        mach_max=max(speeds) / inp.a_sound, power_w=p)


def max_louvre_k(inp: Inputs, theta: float) -> float:
    """Largest louvre K (on its open area) that still leaves the minimum margin at
    `theta`; 0.0 if even the plain screened ramp fails, inf if no K fails."""
    def ok(k: float) -> bool:
        return operate(replace(inp, k_louvre=k), theta).margin_pa >= inp.min_margin_pa
    if not ok(0.0):
        return 0.0
    if ok(1e4):
        return math.inf
    lo, hi = 0.0, 1e4
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if ok(mid) else (lo, mid)
    return lo


THROTTLES = (0.4, 0.6, 0.8, 1.0)
HOVER_THROTTLE = 0.8  # plan: the hover trim throttle
IDLE_THROTTLE = 0.10  # ASSUMED controller floor (plan U2 step 3b)
LOUVRE_CASES = (("plain screened ramp", 0.0), ("low-loss louvre", 1.0),
                ("ordinary louvre (plan K 2.3)", 2.3))
# Planning figures of plan 002 "Installed thrust" and "Hover trim": regression notes only.
PLAN_N = {("plain screened ramp", 1.0): 13.0, ("plain screened ramp", 0.8): 8.4,
          ("ordinary louvre (plan K 2.3)", 1.0): 9.0}


def limits(inp: Inputs) -> list[tuple[str, float, float, bool, str]]:
    """THE limits list: (name, value, limit, ok, unit).  Printout and exit code use it."""
    full = operate(inp, 1.0)
    hover = operate(inp, HOVER_THROTTLE)
    out: list[tuple[str, float, float, bool, str]] = []
    for name, r in (("full", full), ("hover", hover)):
        out.append((f"Mach, highest station, {name} throttle", r.mach_max, inp.mach_limit,
                    r.mach_max <= inp.mach_limit, ""))
    out.append(("R27 stall margin at full throttle", full.margin_pa / 1e3,
                inp.min_margin_pa / 1e3, full.margin_pa >= inp.min_margin_pa, "kPa"))
    a_exit = inp.a_nozzle + inp.a_jets_eff
    imbalance = (abs(full.flow_ramp_m3s + full.flow_bow_m3s - full.v_nozzle * a_exit)
                 / full.flow_m3s)
    out.append(("flow in (ramp + bow) minus flow out (nozzle), relative", imbalance, 1e-9,
                imbalance <= 1e-9, ""))
    out.append(("flow power at 100 % throttle below the maker's electrical power",
                flow_power_full(inp), inp.p_elec_w, flow_power_full(inp) <= inp.p_elec_w, "W"))
    return out


def lbf(n: float) -> str:
    return f"{n / LBF_N:5.2f} lbf ({n:5.1f} N)"


def report(inp: Inputs) -> int:
    p100 = flow_power_full(inp)
    print("tail_edf_flow -- tail EDF installed thrust, flow and pressure margin")
    print("PROVISIONAL: constant-flow-power planning model; every loss coefficient, the bow and "
          "Bay A areas\nand the stall pressure are ASSUMED; no maker fan curve exists (plan KTD7).")
    print(f"Regime: steady, incompressible, Mach < {inp.mach_limit}; ISA sea level air "
          f"{inp.rho} kg/m3.")
    print(f"Calibration [REF-EDF-003]: free-air {lbf(inp.t_free_n)}, flow power at 100 % "
          f"{p100:.0f} W of {inp.p_elec_w:.0f} W electrical ({p100 / inp.p_elec_w:.0%}).")
    print(f"Areas: nozzle {inp.a_nozzle / IN2_M2:.2f} in2 ({inp.a_nozzle * 1e6:.0f} mm2); "
          f"ramp {inp.a_ramp / IN2_M2:.2f} in2 ({inp.a_ramp * 1e6:.0f} mm2) = "
          f"{inp.a_ramp / inp.a_free:.0%} of the rotor annulus "
          f"{inp.a_free / IN2_M2:.2f} in2 ({inp.a_free * 1e6:.0f} mm2).")
    prov = (f"stall pressure {inp.p_stall_full_pa / PSI_PA:.2f} psi "
            f"({inp.p_stall_full_pa / 1e3:.1f} kPa) at 100 %, ASSUMED, not a maker fan curve")
    for cname, k in LOUVRE_CASES:
        c = replace(inp, k_louvre=k)
        print(f"\nCase: {cname} (louvre K {k} on {inp.sigma_louvre:.0%} open area)")
        print("  throttle  installed thrust     free-air thrust    flow cfm (L/s)   ramp share"
              "  path loss psi (kPa)  margin psi (kPa)")
        for th in THROTTLES:
            r = operate(c, th)
            print(f"  {th:6.0%}   {lbf(r.thrust_n)}  {lbf(r.thrust_free_n)}  "
                  f"{r.flow_m3s / CFM_M3S:6.1f} ({r.flow_m3s * 1e3:5.1f})  "
                  f"{r.flow_ramp_m3s / r.flow_m3s:8.0%}  "
                  f"{r.path_loss_pa / PSI_PA:6.3f} ({r.path_loss_pa / 1e3:5.2f})  "
                  f"{r.margin_pa / PSI_PA:+6.3f} ({r.margin_pa / 1e3:+5.2f})")
        print(f"  margin provenance: {prov}")
    print("\nLargest louvre K (on open area) that keeps the stall margin of "
          f"{inp.min_margin_pa / 1e3:.1f} kPa (R27; owner sets the minimum at G1):")
    for label, th in (("hover throttle", HOVER_THROTTLE), ("full throttle", 1.0)):
        k = max_louvre_k(inp, th)
        print(f"  at {label} ({th:.0%}): K {'no limit' if math.isinf(k) else f'{k:.2f}'}"
              f"   (R30 trim bound is added by hover_trim_rcs.py)")
    print("\nBlocked ramp screen (design louvre case), hover and full throttle:")
    for b in (0.0, 0.25, 0.5, 0.75, 0.9, 1.0):
        row = []
        for th in (HOVER_THROTTLE, 1.0):
            r = operate(replace(inp, blocked=b), th)
            row.append(f"{th:.0%}: {lbf(r.thrust_n)}, {r.flow_m3s / CFM_M3S:5.1f} cfm, "
                       f"margin {r.margin_pa / 1e3:+5.2f} kPa")
        print(f"  blocked {b:4.0%}  " + "  |  ".join(row))
    print("\nCruise inlets (ASSUMED 25 kt, ASSUMED 70 % total-pressure recovery; flow and split "
          "only, no ram drag charged):")
    pin = 0.7 * 0.5 * inp.rho * (25 * KT_MS) ** 2
    for label, th in (("minimum cooling floor", IDLE_THROTTLE), ("hover", HOVER_THROTTLE)):
        r = operate(replace(inp, p_in_pa=pin), th)
        print(f"  {label} ({th:.0%}): {r.flow_m3s / CFM_M3S:6.1f} cfm "
              f"({r.flow_m3s * 1e3:5.1f} L/s), ramp {r.flow_ramp_m3s / r.flow_m3s:.0%}, "
              f"inlet total pressure {pin:.0f} Pa")
    print("\nRegression notes against the planning figures (NOT pass criteria):")
    for (cname, th), plan_n in PLAN_N.items():
        k = dict(LOUVRE_CASES)[cname]
        r = operate(replace(inp, k_louvre=k), th)
        print(f"  {cname}, {th:.0%}: plan {lbf(plan_n)}, this tool {lbf(r.thrust_n)} "
              f"({(r.thrust_n - plan_n) / plan_n:+.0%})")
    print("\nLimits (one list; the exit code uses it):")
    ok_all = True
    for name, val, lim, ok, unit in limits(inp):
        ok_all &= ok
        print(f"  {'OK  ' if ok else 'FAIL'} {name}: {val:.4g} vs limit {lim:.4g} {unit}")
    print("RESULT: " + ("PASS (provisional)" if ok_all else "FAIL"))
    return 0 if ok_all else 2


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--louvre-k", type=float, default=Inputs.k_louvre,
                    help="design louvre K on its open area (ASSUMED 1.0)")
    ap.add_argument("--min-margin-kpa", type=float, default=0.0,
                    help="R27 minimum stall margin, kPa (owner decision at G1)")
    ap.add_argument("--blocked", type=float, default=0.0, help="screen blockage fraction")
    a = ap.parse_args(argv)
    return report(Inputs(k_louvre=a.louvre_k, min_margin_pa=a.min_margin_kpa * 1e3,
                         blocked=a.blocked))


if __name__ == "__main__":
    sys.exit(main())
