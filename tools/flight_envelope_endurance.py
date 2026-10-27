#!/usr/bin/python3
"""Flight-envelope and hover-endurance recompute for the split-battery aircraft.

Owner 2026-10-26: no endurance target was ever specified, and the README
Nominal Mission Profile gives no durations.  This tool:

  1. recomputes the docs/flight_envelope.md figures (T/W, theta_hover, V_min
     vs tilt, hover bank bound, density-altitude margin) at the current
     ledger mass and thrust, on the TWO main cells -- payload handling
     occupies the payload hooks, so the third cell is unavailable on a
     payload mission (plan 2026-10-26-001 R10);
  2. estimates hover electrical power and current from the one cited fan
     operating point;
  3. builds a duration budget for the mission profile from stated, labelled
     assumptions, and solves for the endurance target that budget implies;
  4. gives the maximum hover endurance with all three cells by adding the
     third cell's capacity (no payload carried).

Every input is either cited or labelled ASSUMED on each run.

Run:  /usr/bin/python3 tools/flight_envelope_endurance.py

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, 2026-10-26, per AGENTS.md section 3 AI attribution.
License: MIT (SPDX-License-Identifier: MIT) -- see tools/LICENSE.
"""

from __future__ import annotations

import math
import sys

G0 = 9.80665              # m/s^2, standard gravity
RHO0 = 1.225              # kg/m^3, ISA sea level
KT_PER_MS = 1.0 / 0.514444
LBM_PER_G = 1.0 / 453.59237

# ---- Mass (current-specification/auw_ledger.json, docs/BATTERY_SPLIT_OPTIONS.md S4)
AUW_S1_G = 6091.0         # 2 x Tattu 6S 2200 95C, no payload
PAYLOAD_G = 226.8         # 8.0 oz mission payload (README "Payload capacity")
CELL3_G = 240.0           # Tattu 6S 1600 160C (BATTERY_SPLIT_OPTIONS S3)
AUW_S1_CELL3_G = 6336.0   # S1 + third cell, no payload (BATTERY_SPLIT_OPTIONS S4)

# ---- Thrust (tools/auw_ledger.py THRUST_PER_FAN_GF, [REF-EDF-003])
FAN_T_GF = 2135.0         # QF2822-2400KV @ 22.2 V, manual sheet row
FAN_I_A = 57.0            # same row
FAN_P_W = 1265.4          # same row (= 57.0 A x 22.2 V: electrical input)
N_FANS = 4

# ---- Battery
V_NOM = 22.2              # 6S nominal (docs/POWER_DISTRIBUTION.md S2)
CAP_PAIR_AH = 4.4         # 2 x 2.2 Ah
CAP_CELL3_AH = 1.6
# ASSUMED: usable fraction to the 3.30 V/cell RTL trigger
# (docs/failsafe_thresholds.md); bench discharge to verify.
USABLE = 0.80

# ---- Non-propulsion load at VBAT (avionics/kicad/FlightEngineer/FlightEngineer.md
# "Power Budget": 2.4 A for 5 V + 1.5 A for 6 V, both at peak)
I_AVIONICS_A = 3.9

# ---- Wing (docs/flight_envelope.md design inputs, unchanged planform)
S_WING = 0.019025         # m^2
CL_MAX = 2.0              # UNVERIFIED for the built section (flight_envelope banner)


# ---- Planning sensitivities (doc-review 2026-10-26, feasibility reviewer).
# NOMINAL: the optimistic first pass.  PLANNING: the governing case until
# bench and thrust-stand data exist.  Every value ASSUMED.
CASES = {
    "NOMINAL": dict(usable=0.80, v_load=22.2, stack=1.00),
    # 0.70: a 3.30 V/cell LOADED trigger at ~34C reads ~0.2-0.3 V below rest;
    # 3.55 V/cell mean loaded voltage; 90 % tandem stacking (Rev S figure).
    "PLANNING": dict(usable=0.70, v_load=21.3, stack=0.90),
}
CELL_G_PER_AH = 321.0 / 2.2   # Tattu 6S 2200 95C, 321 g (BATTERY_SPLIT_OPTIONS S3)
TW_CONTROL_FLOOR = 1.2        # WA-R18 hover floor

# ---- Wing spar (README "Rev S1g": bonded 20 x 16.3 mm CF spar; read as a tube
# OD 20.0 mm, ID 16.3 mm -- ASSUMED tube reading).  sigma_u and FOS from
# docs/structural_analysis.md S3.
SPAR_OD, SPAR_ID = 20.0, 16.3
SIGMA_U, SPAR_FOS = 1500.0, 4.0
SEMI_SPAN_MM = 85.7


def hover_fan_power(thrust_per_fan_gf):
    """Electrical power per fan at a hover thrust, W.

    Momentum theory for a fixed disc gives P = T^1.5 / sqrt(2 rho A) / FM, so
    at constant figure of merit and constant motor/ESC efficiency
    P / P_ref = (T / T_ref)^1.5.  ASSUMED: FM and efficiency are the same at
    hover throttle as at the rated point; real part-throttle efficiency is
    usually lower, so this is optimistic.  Thrust-stand data replace it
    (Phase 9).
    """
    return FAN_P_W * (thrust_per_fan_gf / FAN_T_GF) ** 1.5


def hover_current(auw_g, v_load=V_NOM, stack=1.0):
    """Total VBAT current in hover, A (propulsion + avionics).

    stack < 1 is a tandem stacking efficiency: each fan must make 1/stack
    of its share of the weight.
    """
    p = N_FANS * hover_fan_power(auw_g / N_FANS / stack)
    return p / v_load + I_AVIONICS_A


def endurance_s(auw_g, cap_ah, k):
    """Hover time to the RTL trigger, s, for planning case k."""
    return cap_ah * k["usable"] / hover_current(auw_g, k["v_load"], k["stack"]) * 3600.0


def capacity_for(target_s, k):
    """Mass-coupled pair capacity that meets target_s, or None.

    Each added Ah adds CELL_G_PER_AH; stop when T/W falls below the control
    floor.  Returns (capacity Ah, AUW g, T/W) at the first capacity that
    meets the target, or None plus the best endurance found.
    """
    best = (0.0, 0.0)
    cap = CAP_PAIR_AH
    while True:
        m = AUW_S1_G + PAYLOAD_G + (cap - CAP_PAIR_AH) * CELL_G_PER_AH
        tw = N_FANS * FAN_T_GF * k["stack"] / m
        if tw < TW_CONTROL_FLOOR:
            return None, best
        t = endurance_s(m, cap, k)
        best = max(best, (t, cap))
        if t >= target_s:
            return (cap, m, tw), best
        cap += 0.1


def isa_sigma_alt_ft(sigma):
    """Density altitude, ft, for a density ratio (ISA troposphere)."""
    return (1.0 - sigma ** (1.0 / 4.2559)) / 6.8756e-6


# ---- Mission duration budget.  Every duration is ASSUMED, with its basis.
# (step, airborne seconds, ground seconds, basis)
MISSION = [
    ("1 VTOL take-off, climb to 20 ft (6.1 m)", 15, 0,
     "0.5 m/s climb + 3 s settle; 20 ft transition floor (flight_envelope S5)"),
    ("2 land, open bay, load + secure payload", 15, 60,
     "15 s descent/landing; 60 s on the ground, propulsion idle"),
    ("3 VTOL take-off with payload", 15, 0, "as step 1"),
    ("4 transit into the RF environment", 30, 0,
     "150 m at about 10 kt (5 m/s); distance ASSUMED, not in the profile"),
    ("5 lower + release payload onto platform", 30, 0,
     "1.5 m line (CARGO_WINCH_SPECIFICATION) at 0.1 m/s + 15 s release"),
    ("6 identify payload on moving platform", 20, 0, "Observer search, one pass"),
    ("7 synchronise with platform", 20, 0, "station-keeping convergence"),
    ("8 attach hoist + lift from platform", 30, 0, "lower 1.5 m, hook, take load"),
    ("9 reel in + close clamshells", 25, 0, "1.5 m at 0.1 m/s + 10 s doors"),
    ("10 exit + return to origin + land", 45, 0, "150 m back + 15 s landing"),
]
# ASSUMED: 30 % of airborne time held in reserve
# (no Part 107 reserve rule; design-team judgment).
RESERVE = 0.30


def main():
    t_total = N_FANS * FAN_T_GF
    print("=" * 78)
    print("Inputs: thrust", f"{t_total:.0f} gf ({t_total * LBM_PER_G:.2f} lbf, "
          f"{t_total / 1000 * G0:.1f} N) = 4 x {FAN_T_GF:.0f} gf [REF-EDF-003]; "
          "NO tandem stacking loss applied (ledger basis) -- ASSUMED")
    print(f"usable capacity fraction {USABLE:.2f} ASSUMED; hover power by "
          "(T/T_ref)^1.5 scaling ASSUMED (constant FM and efficiency)")
    print("=" * 78)

    cases = [
        ("Two cells, payload aboard", AUW_S1_G + PAYLOAD_G, CAP_PAIR_AH),
        ("Two cells, no payload", AUW_S1_G, CAP_PAIR_AH),
        ("Three cells, no payload", AUW_S1_CELL3_G, CAP_PAIR_AH + CAP_CELL3_AH),
    ]
    res = {}
    for name, m, cap in cases:
        w_n = m / 1000 * G0
        tw = t_total / m
        th = math.degrees(math.asin(1.0 / tw))
        i_h = hover_current(m)
        t_s = cap * USABLE / i_h * 3600.0
        res[name] = (m, tw, th, i_h, t_s, cap)
        print(f"\n{name}: AUW {m * LBM_PER_G:.2f} lbm ({m:.0f} g), W {w_n:.1f} N")
        print(f"  T/W {tw:.3f}   theta_hover {th:.1f} deg   hover bank bound "
              f"{math.degrees(math.acos(1 / tw)):.1f} deg   density alt at T/W=1 "
              f"{isa_sigma_alt_ft(1 / tw):,.0f} ft")
        print(f"  hover per fan {m / N_FANS:.0f} gf -> {hover_fan_power(m / N_FANS):.0f} W; "
              f"total VBAT {i_h:.0f} A ({i_h / cap:.1f}C on {cap:.1f} Ah)")
        print(f"  hover endurance {t_s:.0f} s ({t_s / 60:.2f} min) on "
              f"{cap * USABLE:.2f} Ah usable")
        for deg in (-5, 0, 10, 20, 30, 40):
            lreq = w_n - t_total / 1000 * G0 * math.sin(math.radians(deg))
            v = math.sqrt(2 * lreq / (RHO0 * S_WING * CL_MAX)) if lreq > 0 else 0.0
            print(f"    V_min @ {deg:>4d} deg: {v * KT_PER_MS:6.1f} kt ({v:5.1f} m/s)")
        for deg in (120, 140, 145):
            print(f"    vertical thrust / W @ {deg} deg: "
                  f"{tw * math.sin(math.radians(deg)):.3f}")

    # Three-cell, third cell first and jettisoned (plan 002 R12/R13)
    m3 = AUW_S1_CELL3_G
    t1 = CAP_CELL3_AH * USABLE / hover_current(m3) * 3600
    t2 = CAP_PAIR_AH * USABLE / hover_current(m3 - CELL3_G) * 3600
    print(f"\nThree cells, third drained first then jettisoned: {t1:.0f} s + {t2:.0f} s "
          f"= {t1 + t2:.0f} s ({(t1 + t2) / 60:.2f} min); retained: "
          f"{res['Three cells, no payload'][4]:.0f} s")

    air = sum(a for _, a, _, _ in MISSION)
    gnd = sum(g for _, _, g, _ in MISSION)
    print("\nMission duration budget (README profile; every duration ASSUMED):")
    for step, a, g, basis in MISSION:
        print(f"  {step:44s} air {a:3d} s  ground {g:3d} s  -- {basis}")
    target = air * (1 + RESERVE)
    print(f"  airborne {air} s, ground {gnd} s; with {RESERVE:.0%} reserve -> "
          f"ENDURANCE TARGET {target:.0f} s ({target / 60:.1f} min) airborne")
    have = res["Two cells, payload aboard"][4]
    i_need = CAP_PAIR_AH * USABLE * 3600 / target
    print(f"  available on two cells with payload: {have:.0f} s -> "
          f"{'PASS' if have >= target else 'FAIL'} ({have / target:.2f} of target)")
    print(f"  capacity needed at {res['Two cells, payload aboard'][3]:.0f} A: "
          f"{res['Two cells, payload aboard'][3] * target / 3600 / USABLE:.1f} Ah "
          f"(have {CAP_PAIR_AH} Ah); or hover current <= {i_need:.0f} A on 4.4 Ah")
    print("\nPlanning sensitivities (two cells + payload unless stated):")
    for name, k in CASES.items():
        m = AUW_S1_G + PAYLOAD_G
        print(f"  {name:8s} usable {k['usable']:.2f}, V {k['v_load']} V, stacking "
              f"{k['stack']:.2f}: I {hover_current(m, k['v_load'], k['stack']):.0f} A, "
              f"hover {endurance_s(m, CAP_PAIR_AH, k):.0f} s; three cells retained "
              f"{endurance_s(AUW_S1_CELL3_G, CAP_PAIR_AH + CAP_CELL3_AH, k):.0f} s")
        i3 = hover_current(AUW_S1_CELL3_G, k["v_load"], k["stack"])
        print(f"           third-cell-first leg {i3:.0f} A = {i3 / CAP_CELL3_AH:.0f}C on "
              f"the 1.6 Ah cell (usable fraction at that C unverified)")
        hit, best = capacity_for(target, k)
        if hit:
            print(f"           capacity to meet {target:.0f} s (mass-coupled): "
                  f"{hit[0]:.1f} Ah, AUW {hit[1]:.0f} g, T/W {hit[2]:.2f}")
        else:
            print(f"           NO capacity meets {target:.0f} s before T/W < "
                  f"{TW_CONTROL_FLOOR}; best {best[0]:.0f} s at {best[1]:.1f} Ah")

    z = math.pi * (SPAR_OD ** 4 - SPAR_ID ** 4) / (32.0 * SPAR_OD)
    m_allow = z * SIGMA_U / SPAR_FOS / 1000.0
    l_tot = m_allow / (0.5 * 0.5 * SEMI_SPAN_MM / 1000.0)
    v_s = math.sqrt(2 * l_tot / (RHO0 * S_WING * 1.0))
    print(f"\nSpar check (OD {SPAR_OD} / ID {SPAR_ID} mm): Z {z:.1f} mm^3, M_allow "
          f"{m_allow:.1f} N.m, L_total {l_tot:,.0f} N, V_struct {v_s * KT_PER_MS:,.0f} kt "
          f"({v_s:.0f} m/s) at CL 1.0")
    print(f"Density altitude at T/W {TW_CONTROL_FLOOR}: "
          f"{isa_sigma_alt_ft(TW_CONTROL_FLOOR / res['Two cells, payload aboard'][1]):,.0f} ft")
    return 0


if __name__ == "__main__":
    sys.exit(main())
