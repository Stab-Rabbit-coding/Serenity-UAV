"""Tests for the co-strike and slap-down models in tools/tail_strike_requirement.py,
and the AUW parameter in tools/landing_gear_r6_sizing.py
(plan 2026-10-31-002 U1-U3).

Plain asserts so the file runs under pytest or as a script
(`/usr/bin/python3 tools/tests/test_tail_strike_requirement.py`): pytest is not
installed on the build host.

Tests by Claude (Claude Opus 5.5, Anthropic), per AGENTS.md AI attribution.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import landing_gear_r6_sizing as lg
import sls_auw_reconcile as rec
import tail_strike_requirement as ts

# Problem-frame case (plan 002): 14.68 lbm, k 102.1 mm, arms 14.4 / 290.5 mm.
M, K, D1, D2 = 6.657, 0.1021, 0.0144, 0.2905
FG = 2 * 1296.0


def _close(a, b, rel):
    return math.isclose(a, b, rel_tol=rel)


def test_energy_closure():
    """Absorbed energy + residual KE = m g (h + CG travel during the stroke)."""
    r = ts.co_strike(M, K, D1, D2, FG, 750.0)
    lhs = r["e_gear"] + r["e_skid"] + r["ke_res"]
    rhs = r["ke0"] + r["w_gravity"]
    assert _close(lhs, rhs, 0.01), (lhs, rhs)


def test_gear_only_limit_takes_almost_all_energy():
    """F_skid = 0: the gear pair, 14 mm from the CG, absorbs nearly the full KE."""
    r = ts.co_strike(M, K, D1, D2, FG, 0.0)
    assert r["e_skid"] == 0.0
    assert r["e_gear"] > 0.95 * r["ke0"]


def test_problem_frame_rows_reproduced():
    """750 N and 1000 N rows of the plan's problem-frame table, +/-5 %."""
    for fs, eg, sg, es, ss in ((750.0, 66.6, 25.7, 5.7, 7.7), (1000.0, 65.1, 25.1, 6.3, 6.3)):
        r = ts.co_strike(M, K, D1, D2, FG, fs)
        assert _close(r["e_gear"], eg, 0.05), (fs, r["e_gear"])
        assert _close(r["s_gear_mm"], sg, 0.05), (fs, r["s_gear_mm"])
        assert _close(r["e_skid"], es, 0.05), (fs, r["e_skid"])
        assert _close(r["s_skid_mm"], ss, 0.05), (fs, r["s_skid_mm"])


def test_stiff_skid_shortens_skid_stroke_and_unloads_gear():
    """A very large skid force drives its stroke toward zero and the gear share down."""
    lo = ts.co_strike(M, K, D1, D2, FG, 500.0)
    hi = ts.co_strike(M, K, D1, D2, FG, 5000.0)
    assert hi["s_skid_mm"] < lo["s_skid_mm"]
    assert hi["e_gear"] < lo["e_gear"]


def test_heavier_aircraft_strokes_gear_further():
    """AUW x1.1 at the same forces raises the gear stroke."""
    a = ts.co_strike(M, K, D1, D2, FG, 750.0)
    b = ts.co_strike(1.1 * M, K, D1, D2, FG, 750.0)
    assert b["s_gear_mm"] > a["s_gear_mm"]


def test_negative_arm_is_rejected():
    """A contact ahead of the CG is not a tail co-strike; refuse it."""
    try:
        ts.co_strike(M, K, -0.01, D2, FG, 750.0)
    except ValueError:
        return
    raise AssertionError("negative arm accepted")


def test_slap_down_zero_rotation_is_zero():
    assert ts.slap_down_per_leg(0.0, 0.0) == 0.0


def test_slap_down_hand_case_below_fore_capacity():
    """~10 J residual + gravity drop, shared by two fore legs, is under 35.3 J/leg."""
    per_leg = ts.slap_down_per_leg(9.8, ts.G * M * 0.024)
    assert 0 < per_leg < 35.3


def _with_auw(lbm):
    """wire_schedule at lbm, restoring the gear tool's design mass afterward."""
    prev = lg.DESIGN_AUW_LBM
    try:
        lg.set_design_auw(lbm)
        return lg.wire_schedule()
    finally:
        lg.set_design_auw(prev)


def test_gear_tool_regression_at_13_lbm():
    """13.0 lbm reproduces today's ductile 5.27 mm / spring 4.00 mm wires."""
    s = _with_auw(13.0)
    assert _close(s["ductile_d_mm"], 5.27, 0.005), s
    assert _close(s["spring_d_mm"], 4.00, 0.005), s


def test_gear_tool_wires_grow_with_auw():
    """A heavier design mass needs larger wires (roughly AUW^(1/3))."""
    a, b = _with_auw(13.0), _with_auw(14.19)
    assert b["ductile_d_mm"] > a["ductile_d_mm"]
    assert _close(b["ductile_d_mm"] / a["ductile_d_mm"], (14.19 / 13.0) ** (1 / 3), 0.01)


def test_gear_schedule_at_restores_state_even_on_error():
    """ts.gear_schedule_at must not leak its mass into the gear tool."""
    prev = lg.DESIGN_AUW_LBM
    ts.gear_schedule_at(6.4)
    assert lg.DESIGN_AUW_LBM == prev
    try:
        ts.gear_schedule_at(-1.0)
    except ValueError:
        pass
    assert lg.DESIGN_AUW_LBM == prev


def test_gear_arm_further_aft_takes_less_energy():
    """Direction check: moving the gear contact further from the CG lowers its
    effective mass, so it absorbs less (catches a sign flip in the arm)."""
    near = ts.co_strike(M, K, 0.0144, D2, FG, 1250.0)
    far = ts.co_strike(M, K, 0.0600, D2, FG, 1250.0)
    assert far["e_gear"] < near["e_gear"]


def test_reconcile_includes_nacelle_printed_parts():
    """Guards the 14.09 -> 14.19 lbm fix: nacelle printed parts are re-priced too."""
    nac = 2 * sum(m for _n, m in rec.nacelle_printed_g())
    assert nac > 800.0, nac                       # ~852 g at 1.05 g/cc today
    names = " ".join(n.lower() for n, _m in rec.nacelle_printed_g())
    assert "bearing" not in names and "motor" not in names
    _solid, d_sls = rec.deltas()
    d_hull_only = sum(r["mass_g"] / rec.RHO_LEDGER * rec.RHO[rec.SLS_MATERIAL.get(r["name"], "PA CF")]
                      - r["mass_g"] for r in rec.ledger()["rows_hover"] if r["kind"] == "PRINT")
    assert _close(d_sls - d_hull_only, nac * (1.11 / 1.05 - 1), 1e-6)


def test_mesh_check_on_todays_rear_shell():
    """U4: today the skid tips lead and the ventral cross member clears by ~6.5 mm.
    With the 1 mm CS-2 margin, the 1,250 N stroke (5.2 mm) passes and the
    1,000 N stroke (6.1 mm) fails.  (Earlier versions passed 6.1 mm because the
    margin was not enforced -- review finding P0, 2026-10-31.)"""
    ok = ts.co_strike_mesh_check(stroke_mm=5.2)
    short = ts.co_strike_mesh_check(stroke_mm=6.1)
    assert ok["skid_deg"] < ok["tail_deg"]
    assert 6.2 <= ok["tail_clear_mm"] <= 6.8, ok["tail_clear_mm"]
    assert ok["pass"] is True
    assert short["pass"] is False and "needs 7.1" in short["reason"]

def test_elastic_skid_returns_its_energy():
    """Elastic skid (spring, owner decision PA12-CF): it stores energy and gives it back,
    so its net absorbed energy at release is ~0 and more energy is left for the slap-down
    than with a plateau skid of similar peak force."""
    el = ts.co_strike(M, K, D1, D2, FG, 0.0, skid_k=2 * 135.6)
    pl = ts.co_strike(M, K, D1, D2, FG, 900.0)
    assert el["s_skid_max_mm"] > 0
    assert abs(el["e_skid"]) < 0.05 * el["e_skid_peak"]
    assert el["ke_res"] > pl["ke_res"]
    assert _close(el["f_skid_peak"], 2 * 135.6 * el["s_skid_max_mm"], 0.01)


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
