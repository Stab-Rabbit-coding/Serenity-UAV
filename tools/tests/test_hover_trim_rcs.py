# License: MIT — see LICENSES/MIT.txt (SPDX-License-Identifier: MIT)
"""Tests for tools/hover_trim_rcs.py (plan 002 U4, TEDF-04).

References are independent of the tool's formulas: a hand-worked moment balance by cross
products about the pivot and about the CG, and the plan's own table.  Agreement with the plan's
RCS and CG-window figures is a regression note in the tool, never asserted tightly here.
"""
import importlib.util
import json
import math
import sys
from dataclasses import replace
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


tf = _load("tail_edf_flow")
ht = _load("hover_trim_rcs")

PLAN = ht.plan_case()
PLAIN = ht.Setup(tf.Inputs(k_louvre=0.0))  # the plan's table is the plain screened ramp
DESIGN = ht.Setup(tf.Inputs())


def _cross_y_z(r, f):
    """Moment about +X of force f=(Fy, Fz) at r=(y, z), right-handed with Y aft, Z up."""
    return r[0] * f[1] - r[1] * f[0]


def test_untrimmed_moment_matches_a_hand_moment_balance_about_the_pivot_and_the_cg():
    f_t = 8.4
    c = PLAN
    # Forces: weight down at the CG, tail thrust forward (-Y) at the tail axis, and the nacelle
    # thrust that cancels both (vertical W, aft F_t) at the pivot.
    cg = (c.cg_y / 1e3, c.cg_z / 1e3)
    piv = (ht.PIVOT_Y / 1e3, ht.PIVOT_Z / 1e3)
    tail = (c.cg_y / 1e3 + 0.3, ht.TAIL_Z / 1e3)
    forces = [(cg, (0.0, -c.w)), (tail, (-f_t, 0.0)), (piv, (f_t, c.w))]
    assert math.isclose(sum(f[0] for _, f in forces), 0.0, abs_tol=1e-9)
    assert math.isclose(sum(f[1] for _, f in forces), 0.0, abs_tol=1e-9)
    # Moment of the weight and the tail thrust about the PIVOT, nose-up = -(rotation about +X):
    about_pivot = -sum(_cross_y_z((p[0] - piv[0], p[1] - piv[1]), f) for p, f in forces[:2])
    assert math.isclose(about_pivot, ht.untrimmed(c, f_t), rel_tol=1e-9)
    # The same moment taken about the CG: the weight drops out, the tail thrust acts at its
    # height above the CG and the nacelle force at the pivot's depth below it.
    about_cg = -(_cross_y_z((tail[0] - cg[0], tail[1] - cg[1]), forces[1][1])
                 + _cross_y_z((piv[0] - cg[0], piv[1] - cg[1]), forces[2][1]))
    assert math.isclose(about_cg, ht.untrimmed(c, f_t), rel_tol=1e-9)


def test_hover_trim_use_is_at_or_below_half_at_the_hover_throttle():
    """Covers AE7."""
    assert ht.trim_point(PLAN, PLAIN, ht.HOVER_THROTTLE)["use"] <= ht.R30_USE_MAX


def test_a_cg_outside_the_window_exits_nonzero(capsys):
    """Covers AE4. The ledger's CG sits forward of the pivot, outside the window."""
    assert ht.main([]) == 2
    out = capsys.readouterr().out
    assert "FAIL R23" in out
    assert ht.main(["--case", "plan", "--louvre-k", "0"]) == 0


def test_the_window_edges_are_on_the_r30_boundary():
    lo, hi = ht.cg_window(PLAN, PLAIN, 0.8, 1.0)
    assert lo < hi
    for d in (lo + 0.0005, hi - 0.0005):
        c = replace(PLAN, cg_y=ht.PIVOT_Y + d * 1e3)
        use = max(ht.trim_point(c, PLAIN, t)["use"] for t in (0.8, 0.9, 1.0))
        assert use <= ht.R30_USE_MAX + 1e-9
    c = replace(PLAN, cg_y=ht.PIVOT_Y + (hi + 0.002) * 1e3)
    assert max(ht.trim_point(c, PLAIN, t)["use"] for t in (0.8, 0.9, 1.0)) > ht.R30_USE_MAX
    c = replace(PLAN, cg_y=ht.PIVOT_Y + (lo - 0.002) * 1e3)
    assert max(ht.trim_point(c, PLAIN, t)["use"] for t in (0.8, 0.9, 1.0)) > ht.R30_USE_MAX


def test_a_slung_load_at_the_pivot_station_leaves_the_pitching_moment_unchanged():
    """Covers AE6."""
    new, swing = ht.sling(PLAN, 150.0, y=ht.PIVOT_Y, z=ht.FAIRLEAD_Z)
    f_t = 8.4
    assert math.isclose(ht.untrimmed(new, f_t), ht.untrimmed(PLAN, f_t), rel_tol=1e-6)
    assert math.isclose(new.w * new.d, PLAN.w * PLAN.d, rel_tol=1e-6)  # W d is unchanged
    assert abs(new.d) < abs(PLAN.d)  # the CG moves toward the pivot
    assert swing == 0.0


def test_a_swinging_slung_load_gives_force_times_the_fairlead_to_cg_height():
    new, swing = ht.sling(PLAN, 150.0, swing_deg=10.0)
    f_h = 0.150 * ht.G * math.tan(math.radians(10.0))
    assert math.isclose(swing, f_h * (new.cg_z - ht.FAIRLEAD_Z) / 1e3, rel_tol=1e-12)


def test_with_the_cg_at_the_couple_trim_point_the_untrimmed_moment_is_zero():
    f_t = ht.tail_thrust(PLAIN, 0.8)
    d_star = f_t * PLAN.arm / PLAN.w
    c = replace(PLAN, cg_y=ht.PIVOT_Y + d_star * 1e3)
    assert abs(ht.untrimmed(c, f_t)) < 1e-9


def test_jet_force_scales_with_the_square_of_throttle():
    f1 = ht.pair_capacity(PLAN, PLAIN, 1.0, ht.UPPER)["force"]
    f5 = ht.pair_capacity(PLAN, PLAIN, 0.5, ht.UPPER)["force"]
    assert math.isclose(f5, 0.25 * f1, rel_tol=1e-6)


def test_a_larger_jet_gives_more_reserve_and_less_tail_thrust():
    big = ht.Setup(PLAIN.flow, ht.JetModel(bore_m=0.77 * ht.IN_M))
    a = ht.pair_capacity(PLAN, PLAIN, 1.0, ht.UPPER)
    b = ht.pair_capacity(PLAN, big, 1.0, ht.UPPER)
    assert abs(b["pitch"]) > abs(a["pitch"]) and b["tail_thrust"] < a["tail_thrust"]


def test_the_trim_couple_arm_does_not_change_with_the_cg_height():
    arms = {round(replace(PLAN, cg_z=z).arm, 12) for z in (150.0, 157.2, 165.0)}
    assert arms == {round((ht.TAIL_Z - ht.PIVOT_Z) / 1e3, 12)}


def test_zero_tail_thrust_gives_zero_couple_and_tilt_alone_cannot_trim_a_level_aft_cg():
    assert ht.untrimmed(PLAN, 0.0) == PLAN.w * PLAN.d  # no couple term
    delta = ht.tilt_deg(PLAN, 0.0)
    assert delta > 0.0  # the moment balance wants aft tilt, the force balance wants none
    assert math.isclose(ht.degraded_attitude_deg(PLAN, 0.0), delta, rel_tol=1e-9)


def test_the_moment_balance_tilt_rises_as_tail_thrust_falls_and_matches_the_plan_schedule():
    plan = ((2.92, 4.1), (1.89, 7.2), (1.06, 9.7), (0.47, 11.5), (0.0, 12.9))
    prev = -1.0
    for lbf, deg in plan:
        f = lbf * ht.LBF_N
        assert abs(ht.tilt_deg_plan_form(PLAN, f) - deg) < 0.15
        assert abs(ht.tilt_deg(PLAN, f) - deg) < 0.4
        assert ht.tilt_deg(PLAN, f) > prev
        prev = ht.tilt_deg(PLAN, f)


def test_the_transient_pitch_before_compensation_matches_the_plan_at_two_detection_times():
    f = ht.tail_thrust(PLAIN, 0.8)
    assert ht.transient(PLAN, f, 0.1, 120.0)["phi_detect_deg"] < 0.5
    assert 25.0 < ht.transient(PLAN, f, 1.0, 120.0)["phi_detect_deg"] < 35.0


def test_the_latency_budget_matches_the_plan_move_time():
    f = 1.89 * ht.LBF_N
    move = ht.latency_budget_s(PLAN, f, 120.0) - 0.025
    assert abs(move - 0.048) < 0.004


def test_a_jet_mach_above_the_validity_limit_fails_with_the_limit_named():
    tight = ht.Setup(replace(PLAIN.flow, mach_limit=0.05))
    rows = ht.limits(PLAN, tight)
    failed = [n for n, _, lim, ok, _ in rows if not ok and "Mach" in n]
    assert failed and all(lim == 0.05 for n, _, lim, ok, _ in rows if "Mach" in n)


def test_the_end_of_hover_voltage_case_fails_the_run_when_it_needs_more_than_full_throttle():
    rows = {n: (v, ok) for n, v, _, ok, _ in ht.limits(PLAN, DESIGN)}
    end = [k for k in rows if k.startswith("throttle for the couple trim, end of hover")][0]
    assert not rows[end][1]  # the low-loss louvre design case cannot hold the couple at 19.8 V
    plain = {n: ok for n, _, _, ok, _ in ht.limits(PLAN, PLAIN)}
    row = [k for k in plain if k.startswith("throttle for the couple trim, end of hover")][0]
    assert plain[row]  # the plain screened ramp holds the couple at 19.8 V
    assert ht.main(["--case", "plan", "--louvre-k", "1.0"]) == 2


def test_a_25_degree_aft_cant_gives_about_86_percent_of_the_radial_ventral_moment():
    radial = ht.Jet(245.0, 0.0)
    canted = ht.Jet(245.0, 25.0)
    ratio = ht.jet_wrench(PLAN, canted, 1.0)[0] / ht.jet_wrench(PLAN, radial, 1.0)[0]
    assert 0.84 < ratio < 0.88


def test_fifty_degree_ventral_spacing_gives_94_percent_of_the_30_degree_vertical_component():
    v50 = -ht.jet_wrench(PLAN, ht.Jet(245.0, 0.0), 1.0)[0]
    v30 = -ht.jet_wrench(PLAN, ht.Jet(255.0, 0.0), 1.0)[0]
    assert math.isclose(v50 / v30, math.cos(math.radians(25)) / math.cos(math.radians(15)),
                        rel_tol=0.02)
    assert 0.92 < v50 / v30 < 0.96


def test_the_ledger_case_reads_the_ledgers_mass_cg_and_single_pitch_inertia():
    led = json.loads((TOOLS.parent / "current-specification" / "auw_ledger.json").read_text())
    c = ht.ledger_case()
    assert c.mass_g == led["configs"]["hover_twin_2200"]["mass_g"]
    assert c.inertia == led["pitch_inertia"]["I_kg_m2"]


def test_every_limit_is_printed_and_enforced(capsys):
    rows = ht.limits(PLAN, PLAIN)
    assert ht.report(PLAN, PLAIN) == 0
    out = capsys.readouterr().out
    assert all(name in out for name, *_ in rows)
    assert ht.report(replace(PLAN, cg_y=ht.PIVOT_Y - 5.0), PLAIN) == 2


def test_the_plans_own_deltas_on_the_corrected_ledger_leave_the_cg_outside_the_window(capsys):
    """The plan's moves, applied to the ledger with its gaps closed, miss the R23 window."""
    c = ht.projected_case()
    lo, hi = ht.cg_window(c, DESIGN, ht.HOVER_THROTTLE, 1.0)
    assert c.d < lo
    assert ht.main(["--case", "projected"]) == 2
    out = capsys.readouterr().out
    assert "CG shortfall" in out and "Flight Engineer box move" in out
    # moving the FE box less (a smaller forward move) brings the CG back toward the window
    assert ht.projected_case(0.5).d > c.d


def test_a_radial_jet_force_is_minus_the_exhaust_direction_and_unit_length():
    for j in ht.DEFAULT_JETS + ht.PLAN_JETS:
        f = ht.unit_force(j)
        assert math.isclose(math.sqrt(sum(c * c for c in f)), 1.0, rel_tol=1e-12)
    down = ht.unit_force(ht.Jet(270.0, 0.0))  # exhaust straight down pushes the tail up
    assert math.isclose(down[2], 1.0) and abs(down[0]) < 1e-12 and abs(down[1]) < 1e-12


def test_jet_moments_match_a_hand_cross_product_about_the_cg():
    j = ht.Jet(255.0, 25.0, 638.0, 39.3)
    f = ht.unit_force(j)
    a = math.radians(j.az_deg)
    r = (j.r * math.cos(a) / 1e3, (j.y - PLAN.cg_y) / 1e3,
         (ht.TAIL_Z + j.r * math.sin(a) - PLAN.cg_z) / 1e3)
    m = ht.jet_moments(PLAN, j, 1.0)
    assert math.isclose(m["pitch"], r[2] * f[1] - r[1] * f[2], rel_tol=1e-9)
    assert math.isclose(m["yaw"], r[0] * f[1] - r[1] * f[0], rel_tol=1e-9)
    assert math.isclose(m["roll"], r[2] * f[0] - r[0] * f[2], rel_tol=1e-9)


def test_a_mirrored_pair_with_equal_scoops_leaves_no_yaw_or_roll():
    for pair in (ht.VENTRAL, ht.UPPER):
        c = ht.pair_capacity(PLAN, PLAIN, 1.0, pair)
        assert abs(c["pair_yaw"]) < 1e-12 and abs(c["pair_roll"]) < 1e-12


def test_unequal_scoop_recovery_leaves_a_yaw_and_cuts_the_pitch_capacity():
    lop = tuple(replace(j, scoop=0.8) if math.cos(math.radians(j.az_deg)) > 0 else j
                for j in ht.DEFAULT_JETS)
    su = ht.Setup(PLAIN.flow, ht.JetModel(), lop)
    a = ht.pair_capacity(PLAN, PLAIN, 1.0, ht.UPPER)
    b = ht.pair_capacity(PLAN, su, 1.0, ht.UPPER)
    assert abs(b["pair_yaw"]) > 0.0 and abs(b["pitch"]) < abs(a["pitch"])


def test_swirl_turns_the_force_tangentially_and_leaves_a_pair_yaw():
    sw = tuple(replace(j, swirl_deg=15.0) for j in ht.DEFAULT_JETS)
    su = ht.Setup(PLAIN.flow, ht.JetModel(), sw)
    assert abs(ht.pair_capacity(PLAN, su, 1.0, ht.VENTRAL)["pair_yaw"]) > 0.0


def test_one_jet_at_270_beats_the_245_295_pair_of_the_same_total_area():
    """Same open area and station, so the same jet force in total: the jet straight down puts
    cos(25) of it vertical, the 25-deg-off pair only cos(25) cos(25)."""
    pair = ht.PLAN_JETS
    one = (replace(pair[0], az_deg=270.0, area_ratio=2.0),) + pair[2:]
    a = ht.pair_capacity(PLAN, ht.Setup(PLAIN.flow, ht.JetModel(), pair), 1.0, ht.VENTRAL)
    b = ht.pair_capacity(PLAN, ht.Setup(PLAIN.flow, ht.JetModel(), one), 1.0, ht.VENTRAL)
    assert -b["pitch"] > -a["pitch"]


def test_the_flown_jets_come_from_the_shared_table():
    import rcs_jets as rj
    assert len(ht.DEFAULT_JETS) == len(rj.JETS)
    for j, t in zip(ht.DEFAULT_JETS, rj.JETS):
        assert (j.az_deg, j.cant_deg, j.y, j.r) == (t.az_deg, t.cant_deg, t.y, t.r_mm)
        assert math.isclose(j.area_ratio * rj.BORE_AREA_MM2, t.area_mm2)


def test_an_open_jet_adds_its_own_area_to_the_duct_exit():
    jm = ht.JetModel()
    assert math.isclose(jm.a_eff([1.0, 1.68]), 2.68 * jm.area / math.sqrt(1.0 + jm.k_total))


def test_the_vector_diagram_is_written(tmp_path):
    out = tmp_path / "jets.png"
    ht.plot_vectors(PLAN, str(out))
    assert out.stat().st_size > 10_000


def test_the_scoop_de_swirl_loss_adds_to_the_path_loss_and_lowers_the_jet_capacity():
    plain = ht.Setup(PLAIN.flow, ht.JetModel(k_deswirl=0.0))
    vaned = ht.Setup(PLAIN.flow, ht.JetModel(k_deswirl=0.3))
    assert ht.JetModel(k_deswirl=0.3).k_total == ht.JetModel().k_path + 0.3
    a = ht.pair_capacity(PLAN, plain, 1.0, ht.VENTRAL)["pitch"]
    b = ht.pair_capacity(PLAN, vaned, 1.0, ht.VENTRAL)["pitch"]
    assert abs(b) < abs(a)
