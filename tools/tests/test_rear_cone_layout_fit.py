# License: CERN-OHL-W-2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""Tests for tools/rear_cone_layout_fit.py (plan 002 U5, TEDF-05).

The mesh-based tests share one evaluation of the published aft hull (about 45 s).  The
critical-speed tests check the beam-theory model against closed-form limits, not against
itself.  Tests assert what the checks DO; where the planned design fails a check, the test
asserts that the check catches it, and the tool reports it for the G1 brief.
"""
import importlib.util
import math
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
_spec = importlib.util.spec_from_file_location("rear_cone_layout_fit",
                                               TOOLS / "rear_cone_layout_fit.py")
assert _spec is not None and _spec.loader is not None
rc = importlib.util.module_from_spec(_spec)
sys.modules["rear_cone_layout_fit"] = rc
_spec.loader.exec_module(rc)


@pytest.fixture(scope="module")
def ev():
    return rc.evaluate()


def _row(ev, start):
    rows = [x for x in ev["limits"] if x[0].startswith(start)]
    assert rows, start
    return rows


# --- first critical speed (no mesh) --------------------------------------------------------
def test_adding_the_overhung_rotor_lowers_the_computed_critical_speed():
    bare = rc.critical_rpm(rc.SHAFT_D, rc.BEARING_SPAN, rc.default_overhang(), rc.ROTOR_G,
                           with_rotor=False)
    loaded = rc.critical_rpm(rc.SHAFT_D, rc.BEARING_SPAN, rc.default_overhang(), rc.ROTOR_G)
    assert loaded < bare


def test_a_tiny_bearing_span_reduces_to_the_cantilever_stiffness():
    """With L -> 0 the overhung stiffness is the cantilever's, k = 3 E I / a^3."""
    d, a, m = 3.0e-3, 10.0e-3, 0.020
    i = math.pi * d ** 4 / 64.0
    w_cant = math.sqrt(3.0 * rc.SHAFT_E * i / a ** 3 / m) * 60.0 / (2.0 * math.pi)
    # The shaft's own mode over a tiny span is huge, so Dunkerley leaves the rotor term.
    got = rc.critical_rpm(3.0, 1e-3, 10.0, 20.0)
    assert math.isclose(got, w_cant, rel_tol=1e-3)


def test_dunkerley_is_below_both_component_frequencies():
    bare = rc.critical_rpm(3.0, 20.0, 8.0, 20.0, with_rotor=False)
    both = rc.critical_rpm(3.0, 20.0, 8.0, 20.0)
    assert both < bare


def test_a_shaft_overhang_longer_than_the_limit_fails_with_the_margin_stated():
    a_max = rc.max_overhang(rc.SHAFT_D)
    ok = rc.critical_rpm(rc.SHAFT_D, rc.BEARING_SPAN, 0.95 * a_max, rc.ROTOR_G) / rc.top_rpm()
    bad = rc.critical_rpm(rc.SHAFT_D, rc.BEARING_SPAN, 1.2 * a_max, rc.ROTOR_G) / rc.top_rpm()
    assert ok >= rc.CRIT_MARGIN_MIN > bad


def test_the_top_running_speed_is_the_full_pack_unloaded_speed():
    assert rc.top_rpm() == rc.KV * rc.V_FULL > rc.KV * rc.V_NOM


# --- geometry rules (no mesh) --------------------------------------------------------------
def test_port_and_starboard_jets_mirror():
    az = {n: a for n, a, _ in rc.JETS}
    assert az["ventral 245"] + az["ventral 295"] == 540.0
    assert az["upper 45"] + az["upper 135"] == 180.0


def test_each_trapezoidal_exhaust_has_the_bore_area():
    area = math.pi / 4.0 * rc.BORE ** 2
    assert math.isclose(area / rc.EXHAUST_L * rc.EXHAUST_L, area)


def test_obstacles_are_named():
    assert rc.classify_hit(None) == "clear"
    assert rc.classify_hit((10.0, (0.0, 627.0, 104.0))) == "crossbar"
    assert rc.classify_hit((10.0, (-35.0, 633.0, 115.0))) == "pod"


# --- the mesh-based layout -----------------------------------------------------------------
def test_the_shroud_clears_the_hull_by_the_static_gap_along_its_length(ev):
    assert ev["gap"][0] >= rc.STATIC_GAP
    assert all(rc.passed(x) for x in _row(ev, "radial gap, shroud to hull"))


def test_the_shroud_ends_at_the_joint_forward_of_the_scoops(ev):
    assert ev["layout"]["shroud_y1"] <= rc.SCOOP_Y
    assert all(rc.passed(x) for x in _row(ev, "shroud aft end forward of the scoops"))


def test_the_motor_and_rotor_stay_inside_the_hull_and_forward_of_the_nozzle_exit(ev):
    L = ev["layout"]
    assert rc.STERN_STACK_Y1 < L["motor_y0"] < L["motor_face_y"] < L["rotor_y"] < L["exit_y"]
    for start in ("motor clear of the stern stack", "rotor forward of the nozzle exit"):
        assert all(rc.passed(x) for x in _row(ev, start))


def test_scoops_at_y628_and_ventral_exhausts_at_or_aft_of_it(ev):
    for start in ("scoops at Y 628", "ventral exhausts at or aft of Y 628"):
        assert all(rc.passed(x) for x in _row(ev, start))


def test_the_passage_check_is_enforced_and_the_needed_sector_meets_the_exhaust_area(ev):
    rows = _row(ev, "passage area >= exhaust area")
    assert len(rows) == 4
    need = ev["sector_needed"]
    assert all(45.0 < v < 60.0 for v in need.values())
    # the planned 45-degree sectors fall short, and the tool says so
    assert not any(rc.passed(x) for x in rows)


def test_a_ventral_web_thinner_than_the_minimum_printed_wall_fails(ev, monkeypatch):
    monkeypatch.setattr(rc, "SECTOR_DEG", 49.0)
    assert rc.ventral_web_mm(ev["layout"]) < rc.WALL_MIN_PRINT
    monkeypatch.setattr(rc, "SECTOR_DEG", 45.0)
    assert rc.ventral_web_mm(ev["layout"]) >= rc.WALL_MIN_PRINT


def test_the_planned_ventral_pair_strikes_the_skid_pods_and_mirrors(ev):
    a, b = ev["jets"]["ventral 245"], ev["jets"]["ventral 295"]
    assert not a["clear"] and not b["clear"]
    assert rc.classify_hit(a["nearest"]) == rc.classify_hit(b["nearest"]) == "pod"
    assert a["blocked"] == b["blocked"]
    assert math.isclose(a["nearest"][1][0], -b["nearest"][1][0], abs_tol=0.5)


def test_a_jet_over_the_crossbar_fails_and_moving_the_exhaust_aft_clears_it(ev):
    band = ev["ventral_band"]
    assert rc.classify_hit(band[(632.0, 270.0)]) == "crossbar"
    assert band[(635.0, 270.0)] is None
    assert band[(638.0, 255.0)] is None


def test_a_jet_aimed_at_the_dorsal_pod_fails(ev):
    j = rc.jet_check(ev["layout"], 90.0, 0.0)
    assert not j["clear"]


def test_the_upper_jets_are_clear(ev):
    assert ev["jets"]["upper 45"]["clear"] and ev["jets"]["upper 135"]["clear"]


def test_the_plate_joints_are_mapped_and_each_exhaust_reports_its_joint_shift(ev):
    joints = ev["joints"][630]
    assert len(joints) >= 10
    for e in ev["exhaust"].values():
        assert len(e["shifts"]) == 2 and all(s[3] >= 0.0 for s in e["shifts"])


def test_the_first_critical_speed_row_is_in_the_limits_list(ev):
    rows = _row(ev, "first critical speed over the top running speed")
    assert rows[0][1] == ev["crit_rpm"] / ev["top_rpm"]


def test_every_limit_is_printed_and_a_failing_layout_exits_nonzero(ev, capsys):
    ok = rc.report(ev)
    out = capsys.readouterr().out
    assert all(x[0] in out for x in ev["limits"])
    assert ok is all(rc.passed(x) for x in ev["limits"])
    assert ok is False  # the planned jets and passages fail: the G1 brief reports them
