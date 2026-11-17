# License: MIT — see LICENSES/MIT.txt (SPDX-License-Identifier: MIT)
"""Tests for tools/tail_edf_flow.py (plan 002 U3, TEDF-03).

References are independent of the tool's solver: closed-form momentum theory for the
free-air and loss-free cases, and the maker's figures [REF-EDF-003].  Agreement with the
plan's planning figures is a regression note in the tool, never asserted here.
"""
import importlib.util
import math
import sys
from dataclasses import replace
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "tail_edf_flow", Path(__file__).resolve().parents[1] / "tail_edf_flow.py")
assert _spec is not None and _spec.loader is not None
tf = importlib.util.module_from_spec(_spec)
sys.modules["tail_edf_flow"] = tf  # dataclasses needs the module registered
_spec.loader.exec_module(tf)

BASE = tf.Inputs()
# A path with no loss anywhere: huge areas, K ~ 0 (1e-12 keeps the resistances nonzero; the
# nozzle's exit kinetic energy remains).
EPS = 1e-12
LOSSLESS = replace(
    BASE, k_ramp_entry=EPS, k_screen=EPS, k_louvre=EPS, k_bow_inlet=EPS, k_bay_a=EPS,
    k_cargo=EPS, k_cone=EPS, k_fan_face=EPS, a_ramp=10.0, a_bow=10.0, a_bay_a=10.0,
    a_cargo=10.0, a_cone=10.0)


def _momentum_thrust(p_flow: float, area: float, rho: float) -> float:
    """Ideal jet: P = rho A v^3 / 2, T = rho A v^2, solved in closed form."""
    v = (2.0 * p_flow / (rho * area)) ** (1.0 / 3.0)
    return rho * area * v * v


def test_free_air_calibration_reproduces_the_makers_thrust():
    """Covers AE3. Blowing out of the rotor annulus, the model returns 2370 gf."""
    inp = replace(LOSSLESS, a_nozzle=BASE.a_free)
    r = tf.operate(inp, 1.0)
    assert math.isclose(r.thrust_n, 2370.0 * 9.80665 / 1000.0, rel_tol=1e-6)


def test_no_upstream_loss_gives_the_momentum_theory_thrust_for_the_nozzle_area():
    r = tf.operate(LOSSLESS, 1.0)
    p = tf.flow_power_full(LOSSLESS)
    assert math.isclose(r.thrust_n, _momentum_thrust(p, LOSSLESS.a_nozzle, 1.225), rel_tol=1e-6)


def test_flow_power_is_below_the_makers_electrical_power():
    """The ideal flow power cannot exceed 1368 W electrical [REF-EDF-003]."""
    assert tf.flow_power_full(BASE) < BASE.p_elec_w


def test_each_throttle_reports_installed_beside_free_air_thrust():
    """Covers AE3."""
    for th in tf.THROTTLES:
        r = tf.operate(BASE, th)
        assert r.thrust_n < r.thrust_free_n
        assert math.isclose(r.thrust_free_n, BASE.t_free_n * th ** 2, rel_tol=1e-12)


def test_half_throttle_gives_one_eighth_of_the_flow_power():
    full = tf.operate(BASE, 1.0).power_w
    assert math.isclose(tf.operate(BASE, 0.5).power_w, full / 8.0, rel_tol=1e-12)


def test_more_louvre_loss_gives_less_thrust_and_less_flow():
    prev = None
    for k in (0.0, 0.5, 1.0, 2.3, 5.0):
        r = tf.operate(replace(BASE, k_louvre=k), 1.0)
        if prev is not None:
            assert r.thrust_n < prev.thrust_n and r.flow_m3s < prev.flow_m3s
        prev = r


def test_flow_in_at_ramp_and_bow_equals_flow_out_at_the_nozzle():
    for b in (0.0, 0.5, 0.9):
        r = tf.operate(replace(BASE, blocked=b), 0.8)
        assert math.isclose(r.flow_ramp_m3s + r.flow_bow_m3s, r.v_nozzle * BASE.a_nozzle,
                            rel_tol=1e-9)


def test_energy_balance_closes_at_the_operating_point():
    """P / Q + p_in = path loss + exit kinetic energy (checked outside the solver)."""
    inp = replace(BASE, p_in_pa=70.0)
    r = tf.operate(inp, 0.8)
    exit_ke = 0.5 * inp.rho * r.v_nozzle ** 2
    assert math.isclose(r.dp_fan_pa + inp.p_in_pa, r.path_loss_pa + exit_ke, rel_tol=1e-9)


def test_a_fully_blocked_ramp_leaves_only_the_bow_inlet_flow():
    r = tf.operate(replace(BASE, blocked=1.0), 0.8)
    assert r.flow_ramp_m3s == 0.0
    # Independent: with no ramp the whole path is the bow branch in series with the rest.
    r_tot = (tf.bow_resistance(BASE) + tf.interior_resistance(BASE) + 1.0 / BASE.a_nozzle ** 2)
    q = (tf.flow_power_full(BASE) * 0.8 ** 3 / (0.5 * BASE.rho * r_tot)) ** (1.0 / 3.0)
    assert math.isclose(r.flow_bow_m3s, q, rel_tol=1e-6)


def test_blocking_the_screen_lowers_thrust_and_the_margin_monotonically():
    prev = None
    for b in (0.0, 0.25, 0.5, 0.75, 1.0):
        r = tf.operate(replace(BASE, blocked=b), 1.0)
        if prev is not None:
            assert r.thrust_n < prev.thrust_n and r.margin_pa < prev.margin_pa
        prev = r


def test_raising_the_inlet_total_pressure_raises_the_flow_at_a_fixed_throttle():
    lo = tf.operate(replace(BASE, p_in_pa=0.0), 0.8)
    hi = tf.operate(replace(BASE, p_in_pa=100.0), 0.8)
    assert hi.flow_m3s > lo.flow_m3s


def test_the_largest_louvre_k_sits_on_the_margin_boundary():
    k = tf.max_louvre_k(BASE, 1.0)
    assert 0.0 < k < math.inf
    assert tf.operate(replace(BASE, k_louvre=k * 0.99), 1.0).margin_pa >= 0.0
    assert tf.operate(replace(BASE, k_louvre=k * 1.01), 1.0).margin_pa < 0.0


def test_a_margin_below_the_stated_minimum_fails_the_run(capsys):
    assert tf.main(["--min-margin-kpa", "50"]) == 2
    assert "FAIL" in capsys.readouterr().out


def test_the_default_design_case_passes(capsys):
    assert tf.main([]) == 0
    assert "stall pressure" in capsys.readouterr().out  # provenance printed with the margin


def test_an_exit_mach_above_the_validity_limit_fails_with_the_limit_named(capsys):
    small = tf.Inputs(a_nozzle=BASE.a_nozzle / 20.0)
    names = [n for n, _, _, ok, _ in tf.limits(small) if not ok]
    assert any(n.startswith("Mach") for n in names)
    assert tf.report(small) == 2
    assert "limit 0.3" in capsys.readouterr().out


def test_every_limit_in_the_list_is_printed_and_enforced(capsys):
    rows = tf.limits(BASE)
    tf.report(BASE)
    out = capsys.readouterr().out
    assert all(name in out for name, *_ in rows)
    broken = replace(BASE, min_margin_pa=1e9)
    assert not all(ok for *_, ok, _ in tf.limits(broken))
