"""test_bay_a_thermal_budget.py -- lumped thermal network for the Bay A
forward nodes (plan 2026-11-01-001 U4, R5; KTD4, KTD5).

Plain asserts so the file runs under pytest or as a script:
    /usr/bin/python3 tools/tests/test_bay_a_thermal_budget.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the
author's direction, 2026-11-01, per `AGENTS.md` §3 AI attribution.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import math
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import bay_a_thermal_budget as tb  # noqa: E402


def test_zero_power_gives_zero_rise():
    for tier in tb.TIERS:
        assert all(abs(r) < 1e-9 for r in tb.solve(tb.Inputs(), tier, 0.0, 0.0)), tier


def test_tier0_matches_hand_calculation():
    """No controls: each node = own film + shared bay path, by hand."""
    inp = tb.Inputs()
    r_film = 1.0 / (inp.h_still * inp.pouch_area_m2)
    a = inp.bay_skin_m2
    r_bay = 1 / (inp.h_still * a) + inp.skin_t_m / (inp.k_skin * a) + 1 / (inp.h_ext * a)
    cn1, fc1, bay = tb.solve(inp, "none", 3.0, 1.25)
    assert math.isclose(bay, 4.25 * r_bay, rel_tol=1e-9)
    assert math.isclose(cn1, bay + 3.0 * r_film, rel_tol=1e-9)
    assert math.isclose(fc1, bay + 1.25 * r_film, rel_tol=1e-9)


def test_energy_balance_at_every_tier():
    """Heat into the bay air (film + tier-1 floor) leaves through the bay skin."""
    inp = tb.Inputs()
    for tier in tb.TIERS:
        r_film, r_bay, r1, r2, to_amb = tb._resistances(inp, tier)
        cn1, fc1, bay = tb.solve(inp, tier, 3.0, 1.25)
        into_bay = (cn1 - bay) / r_film + (fc1 - bay) / r_film
        if r1 is not None and not to_amb:
            into_bay += (cn1 - bay) / r1 + (fc1 - bay) / r2
        assert math.isclose(into_bay, bay / r_bay, rel_tol=1e-9), tier


def test_tiers_are_cumulative_and_monotone():
    """Adding a control never makes a node hotter (KTD5)."""
    inp = tb.Inputs()
    prev = None
    for tier in tb.TIERS:
        cur = tb.solve(inp, tier, 3.0, 1.25)[:2]
        if prev is not None:
            assert all(c <= p + 1e-9 for c, p in zip(cur, prev)), tier
        prev = cur


def test_over_limit_at_every_tier_fails():
    rows, adopted = tb.budget(replace(tb.Inputs(), cn1_peak_w=50.0))
    assert adopted is None


def test_easy_case_adopts_lowest_tier():
    rows, adopted = tb.budget(replace(tb.Inputs(), cn1_avg_w=0.01, cn1_peak_w=0.01,
                                      fc1_w=0.01))
    assert adopted == "none"


def test_assumed_inputs_are_provisional():
    assert tb.provisional(tb.Inputs())


def test_max_sustained_power_puts_cn1_at_the_limit():
    inp = tb.Inputs()
    p = tb.max_sustained_cn1_w(inp, "fan")
    hot = max(tb.solve(inp, "fan", p, inp.fc1_w)[:2])
    assert math.isclose(inp.ambient_c + hot, inp.limit_c, abs_tol=1e-6)


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception as exc:  # noqa: BLE001 -- script runner reports every failure
                fails += 1
                print(f"FAIL {name}: {type(exc).__name__}: {exc}")
    sys.exit(1 if fails else 0)
