#!/usr/bin/env python3
"""bay_a_thermal_budget.py -- lumped thermal budget for the enclosed Bay A
forward nodes (plan 2026-11-01-001 U4, R5; KTD4, KTD5).

CN1 (TACCO + PB2-I) sits in the CN1 drawer under the nose Observer; FC1
(Pilot + PB2-I) sits on the FC1 shelf above it, under the bridge-roof hatch.
Each node is a Faraday pouch.  This tool estimates the board-air temperature
of each node at average and peak dissipation for each control tier and picks
the lowest tier that keeps every node under its limit.

Control tiers are CUMULATIVE (KTD5): tier N adds its control to tiers 1..N-1.
  0  none      pouch -> still bay air -> skin -> outside air
  1  pad       + gap pad from the PB2-I to the pouch wall, pouch on its mount
                 floor (conduction path in parallel with the bay air)
  2  mount     + mount bonded to the skin over its footprint (conduction
                 through the bond and skin to outside air)
  3  vents     + vent slots between the bay and the bow sensor bay, which is
                 open to outside air: through-flow raises the internal film
                 coefficient
  4  fan       + thermostatic 5 V fan on the vent path (forced convection)

Network per node (series/parallel thermal resistances, K/W):
  board -> [internal film on the pouch area]                -> bay air
  bay air -> [internal film on the bay skin] -> skin -> [external film] -> ambient
  tier >= 1: board -> pad -> pouch -> floor   (parallel to the internal film)
  tier >= 2: floor -> bond + skin -> [external film over the mount footprint]
The two nodes share one bay-air volume; each node's own heat must cross its
own film, and the bay air carries both nodes' heat to the skin.

EVERY material property and film coefficient below is ASSUMED (no cited
source in REFERENCES.md yet); a PASS that rests on an ASSUMED value is
PROVISIONAL.  Dissipation: docs/AVIONICS_PB2_REDESIGN.md §Power (CN node
~3 W average / 8.3 W peak, FC node ~1.25 W).  The 85 C limit is the PB2-I
MODULE rating, not an owner requirement; the design ambient (40 C) is ASSUMED
pending owner confirmation (open WBS item).

Run:
    /usr/bin/python3 tools/bay_a_thermal_budget.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the
author's direction, 2026-11-01, per `AGENTS.md` §3 AI attribution.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import sys
from dataclasses import dataclass, field

import numpy as np

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import cargo_layout_fit as _clf  # noqa: E402  pouch size (single source)
import gen_bay_a_fwd_mounts as _g  # noqa: E402  drawer geometry (single source)
import head_layout_fit as _h  # noqa: E402  stations (single source)

TIERS = ("none", "pad", "mount", "vents", "fan")


@dataclass
class Inputs:
    """Every field is ASSUMED unless `cited` names its source."""
    ambient_c: float = 40.0  # ASSUMED design ambient (104 F), owner to confirm
    limit_c: float = 85.0  # PB2-I module rating (module spec, not an owner requirement)
    # dissipation, W (docs/AVIONICS_PB2_REDESIGN.md §Power)
    cn1_avg_w: float = 3.0
    cn1_peak_w: float = 8.3
    fc1_w: float = 1.25
    # geometry, m (pouch 58 x 37 x 22 mm; bay skin wetted area from the head gate)
    pouch_area_m2: float = 2 * (0.058 * 0.037 + 0.058 * 0.022 + 0.037 * 0.022)
    footprint_m2: float = 0.058 * 0.037
    bay_skin_m2: float = 0.030  # ASSUMED: Y 60..170 head skin around Bay A, ~110 x 270 mm
    skin_t_m: float = 0.002
    # materials, W/m-K -- ASSUMED
    k_skin: float = 0.4  # SLS PA12-CF through-thickness
    k_pad: float = 3.0  # gap pad
    pad_t_m: float = 0.001
    k_pouch_contact: float = 0.2  # pouch fabric + contact, as an equivalent layer
    pouch_t_m: float = 0.0005
    k_floor: float = 0.4
    floor_t_m: float = 0.003
    # drawer wall under the FC1 shelf: geometry from tools/gen_bay_a_fwd_mounts.py
    wall_h_m: float = (_g.SHELF_Z0 - _h.CN1F_Z0) / 1000.0
    wall_a_m2: float = 2 * (_g.WALL_X1 - _g.WALL_X0) / 1000.0 * _clf.NODE_L / 1000.0
    # film coefficients, W/m^2-K -- ASSUMED
    h_still: float = 4.0  # enclosed natural convection
    h_vent: float = 10.0  # through-flow from the bow bay
    h_fan: float = 30.0  # small fan, forced
    h_ext: float = 10.0  # outside air, hover (worst case; forward flight is higher)
    cited: dict = field(default_factory=dict)  # field -> REF-ID once sourced


def _resistances(inp, tier):
    """(R_film, R_bay, R_cond_cn1, R_cond_fc1, cond_to_ambient) for a tier."""
    t = TIERS.index(tier)
    h_in = inp.h_fan if t >= 4 else inp.h_vent if t >= 3 else inp.h_still
    r_film = 1.0 / (h_in * inp.pouch_area_m2)
    r_bay = (1.0 / (h_in * inp.bay_skin_m2) + inp.skin_t_m / (inp.k_skin * inp.bay_skin_m2)
             + 1.0 / (inp.h_ext * inp.bay_skin_m2))
    a = inp.footprint_m2
    r_pad = inp.pad_t_m / (inp.k_pad * a) + inp.pouch_t_m / (inp.k_pouch_contact * a)
    r_floor = inp.floor_t_m / (inp.k_floor * a)
    if t == 0:
        return r_film, r_bay, None, None, False
    if t == 1:  # floor sheds into the bay air only
        r = r_pad + r_floor + 1.0 / (h_in * a)
        return r_film, r_bay, r, r, False
    r_skin_out = inp.skin_t_m / (inp.k_skin * a) + 1.0 / (inp.h_ext * a)
    r_cn1 = r_pad + r_floor + r_skin_out
    # FC1's shelf reaches the skin only through the drawer side walls
    r_fc1 = r_pad + inp.wall_h_m / (inp.k_floor * inp.wall_a_m2) + r_floor + r_skin_out
    return r_film, r_bay, r_cn1, r_fc1, True


def solve(inp, tier, p_cn1, p_fc1):
    """Rises over ambient (K): (board CN1, board FC1, bay air).  Linear network:
    node i:  P_i = (Tb_i - Ta)/R_film + (Tb_i - T_sink)/R_cond_i
    bay air: sum of heat into the bay air = Ta / R_bay
    T_sink is the bay air at tier 1 and ambient (0) at tier >= 2."""
    r_film, r_bay, r_c1, r_c2, to_amb = _resistances(inp, tier)
    g_f = 1.0 / r_film
    g = [0.0 if r is None else 1.0 / r for r in (r_c1, r_c2)]
    a = np.zeros((3, 3))
    b = np.array([p_cn1, p_fc1, 0.0])
    for i in range(2):
        a[i, i] = g_f + g[i]
        a[i, 2] = -g_f - (0.0 if to_amb else g[i])
        a[2, i] = g_f + (0.0 if to_amb else g[i])
        a[2, 2] -= g_f + (0.0 if to_amb else g[i])
    a[2, 2] -= 1.0 / r_bay
    return tuple(np.linalg.solve(a, b))


def budget(inp=None):
    """rows: (tier, case, node, temp C, margin K); and the adopted tier."""
    inp = inp or Inputs()
    rows, adopted = [], None
    for tier in TIERS:
        ok = True
        for case, p_cn1 in (("average", inp.cn1_avg_w), ("peak", inp.cn1_peak_w)):
            rise = solve(inp, tier, p_cn1, inp.fc1_w)
            for node, dt in (("CN1", rise[0]), ("FC1", rise[1])):
                temp = inp.ambient_c + dt
                rows.append((tier, case, node, temp, inp.limit_c - temp))
                ok &= temp <= inp.limit_c
        if ok and adopted is None:
            adopted = tier
    return rows, adopted


def max_sustained_cn1_w(inp, tier):
    """Highest steady CN1 dissipation (W) that keeps both nodes at the limit,
    FC1 at its own power.  The network is linear, so two solves suffice."""
    best = []
    for k in (0, 1):  # node index: CN1, FC1
        r0 = solve(inp, tier, 0.0, inp.fc1_w)[k]
        r1 = solve(inp, tier, 1.0, inp.fc1_w)[k]
        slope = r1 - r0
        head = inp.limit_c - inp.ambient_c - r0
        best.append(head / slope if slope > 0 else float("inf"))
    return max(0.0, min(best))


def provisional(inp):
    """True while any input field is uncited (KTD4).  `cited` must name real
    input fields; an unknown key is an error, not a citation."""
    fields = set(Inputs.__dataclass_fields__) - {"cited"}
    unknown = set(inp.cited) - fields
    if unknown:
        raise ValueError(f"cited names unknown input field(s): {sorted(unknown)}")
    return bool(fields - set(inp.cited))


def main():
    inp = Inputs()
    rows, adopted = budget(inp)
    print(f"Bay A forward thermal budget; ambient {inp.ambient_c:.0f} C (ASSUMED), "
          f"limit {inp.limit_c:.0f} C (PB2-I module rating)")
    print(f"{'tier':6s} {'case':8s} {'node':4s} {'temp C':>7s} {'margin K':>9s}")
    for tier, case, node, temp, margin in rows:
        print(f"{tier:6s} {case:8s} {node:4s} {temp:7.1f} {margin:9.1f}"
              f"{'  OVER' if margin < 0 else ''}")
    print("\nmax sustained CN1 dissipation per tier (both nodes at the limit):")
    for tier in TIERS:
        print(f"  {tier:6s} {max_sustained_cn1_w(inp, tier):5.2f} W "
              f"(average {inp.cn1_avg_w} W, all-radio peak {inp.cn1_peak_w} W)")
    status = "PROVISIONAL" if provisional(inp) else "PASS"
    if adopted is None:
        avg_tier = next((t for t in TIERS if all(m >= 0 for tt, c, _, _, m in rows
                                                 if tt == t and c == "average")), None)
        print(f"\naverage case first passes at tier: {avg_tier}")
        print("RESULT: FAIL -- no tier holds the sustained all-radio peak; it needs a TX "
              "duty/thermal-throttle limit (owner decision) or a better heat path")
        return 1
    print(f"\nadopted tier: {adopted} (cumulative tiers 1..{TIERS.index(adopted)})")
    print(f"RESULT: {status}{' (every input ASSUMED)' if status == 'PROVISIONAL' else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
