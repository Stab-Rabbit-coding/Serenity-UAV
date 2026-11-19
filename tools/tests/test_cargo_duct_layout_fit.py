# License: CERN-OHL-W-2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""Tests for tools/cargo_duct_layout_fit.py (plan 002 U6, TEDF-06).

The mesh-based tests share one evaluation of the published head+cargo hull (about 2.5 min).
Closed-form checks (the line tangent, the reach rule, the CG and lead arithmetic) use hand
values, not the tool against itself.  Where the planned layout fails a gate (the Flight
Engineer box does not fit; the Observer is barely reachable), the test asserts that the gate
catches it and names why: the tool reports it for the G1 brief.
"""
import importlib.util
import math
import sys
from dataclasses import replace
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
_spec = importlib.util.spec_from_file_location("cargo_duct_layout_fit",
                                               TOOLS / "cargo_duct_layout_fit.py")
assert _spec is not None and _spec.loader is not None
cd = importlib.util.module_from_spec(_spec)
sys.modules["cargo_duct_layout_fit"] = cd
_spec.loader.exec_module(cd)


@pytest.fixture(scope="module")
def ev():
    return cd.evaluate()


def _rows(ev, start):
    rows = [x for x in ev["limits"] if x[0].startswith(start)]
    assert rows, start
    return rows


def _box(ev, name):
    return next(b for b in ev["placed"] if b.name == name)


# --- closed form (no mesh) ----------------------------------------------------------------------
def test_the_line_leaves_the_drum_on_a_tangent():
    """The line from the tangent point to the fairlead mouth is perpendicular to the radius."""
    g = cd.line_geometry(spool_z=119.0, drum_r=10.0, belly_z=89.0)
    ry, rz = g["tan_y"] - cd.WINCH_Y, g["tan_z"] - 119.0
    assert math.isclose(math.hypot(ry, rz), 10.0, rel_tol=1e-9)
    ly, lz = g["mouth_y"] - g["tan_y"], g["mouth_z"] - g["tan_z"]
    assert abs(ry * ly + rz * lz) < 1e-6
    assert g["mouth_y"] == cd.PIVOT_Y


def test_the_reach_rule_is_the_footprint_share_inside_the_inset_opening():
    opening = (-40.0, 40.0, 300.0, 420.0)
    inside = cd.Box("a", -10, 10, 330, 350, 90, 100)
    outside = cd.Box("b", 60, 80, 330, 350, 90, 100)
    half = cd.Box("c", 20, 40, 330, 350, 90, 100)  # 10 of 20 mm inside the 10 mm inset
    assert cd.reach_fraction(inside, opening) == 1.0
    assert cd.reach_fraction(outside, opening) == 0.0
    assert math.isclose(cd.reach_fraction(half, opening), 0.5)


def test_the_screen_covers_the_ramp_opening_and_a_shifted_screen_does_not():
    op = cd.ramp_opening()
    s = cd.screen_frame()
    assert cd.screen_coverage(s, op) == 1.0
    shifted = {**s, "x0": s["x0"] + 20.0, "x1": s["x1"] + 20.0}
    assert cd.screen_coverage(shifted, op) < 1.0


def test_the_ramp_opening_is_the_flow_models_ramp_area():
    import tail_edf_flow as tf
    x0, x1, z0, z1 = cd.ramp_opening()
    assert abs((x1 - x0) * (z1 - z0) - tf.Inputs().a_ramp * 1e6) < 5.0


def test_the_motor_lead_drop_is_current_times_two_leads():
    import tail_edf_flow as tf
    esc = cd.Box("tail speed controller", -10, 10, 400, 420, 100, 120)
    ld = cd.motor_lead([esc])
    i = tf.Inputs().p_elec_w * cd.HOVER_THROTTLE ** 3 / cd.V_BUS
    length = abs(cd.TAIL_MOTOR_Y - 410.0) + abs(cd.TAIL_MOTOR_Z - 110.0) + cd.LEAD_SLACK
    assert math.isclose(ld["drop_v"], i * cd.AWG14_OHM_PER_M * length / 1e3 * 2.0)


def test_the_orientations_are_the_six_axis_permutations():
    assert len(cd.orientations((1.0, 2.0, 3.0))) == 6


# --- the evaluated layout ---------------------------------------------------------------------
def test_every_bay_station_is_a_closed_duct(ev):
    assert all(cd.passed(x) for x in _rows(ev, "every bay station is a closed duct"))


def test_the_retired_envelopes_are_gone(ev):
    names = [b.name for b in ev["placed"]]
    for gone in ("payload", "door gateway", "hoist line", "winch drum 0", "battery", "cradle"):
        assert not any(gone in n for n in names), gone


def test_the_fairlead_is_under_the_pivot(ev):
    f = _box(ev, "fairlead boss (R14)")
    assert math.isclose(0.5 * (f.y0 + f.y1), cd.PIVOT_Y)
    assert all(cd.passed(x) for x in _rows(ev, "fairlead under the tilt pivot"))


def test_the_line_runs_inside_its_guard_at_any_payout_angle(ev):
    """Inside the hull the run is drum tangent to fairlead mouth whatever the outside payout
    angle; the guard encloses both ends, so a slack line cannot reach the stream."""
    g = _box(ev, "line guard (R26)")
    lg = ev["winch"]["line"]
    for y, z in ((lg["tan_y"], lg["tan_z"]), (lg["mouth_y"], lg["mouth_z"])):
        assert g.y0 <= y <= g.y1 and g.z0 <= z <= g.z1
    assert ev["line_inside"]


def test_the_moved_items_clear_the_hull_and_each_other(ev):
    assert ev["pairs"] == []
    placed = [b for b in ev["moved"] if b.kind != "unplaced"]
    assert len(placed) >= 4  # speed controller, gateway and the servos
    for b in placed:
        others = [p for p in ev["placed"] if p is not b]
        assert cd.clears(b, others), b.name


def test_the_stream_keeps_its_floor_where_it_had_it(ev):
    assert all(cd.passed(x) for x in _rows(ev, "stream free area kept at the floor"))
    assert all(cd.passed(x) for x in _rows(ev, "U6 adds no blockage where"))


def test_moving_an_envelope_into_the_stream_fails_the_gate(ev):
    esc = _box(ev, "tail speed controller")
    others = [p for p in ev["placed"] if p is not esc]
    pinch = min((y for y in ev["stations"] if ev["baseline"][y] < cd.A_STREAM_MIN),
                key=lambda y: ev["baseline"][y])
    moved = replace(esc, y0=pinch - 5.0, y1=pinch + 5.0)
    assert not cd.stream_ok(moved, others)
    wall = cd.Box("wall", -70, 70, 360, 364, 90, 200)  # a bulkhead across the bay
    assert not cd.stream_ok(wall, others)


def test_the_flight_engineer_fit_gate_catches_the_shortfall_and_names_why(ev):
    rows = _rows(ev, "placed clear of the hull, its neighbours and the stream: Flight Engineer")
    fe = next(b for b in ev["moved"] if b.name == "Flight Engineer box")
    assert (fe.kind == "unplaced") is (not cd.passed(rows[0]))
    if fe.kind == "unplaced":
        assert any(k.startswith("winch") or k == "hull height"
                   for k in ev["why"]["Flight Engineer box"])


def test_every_serviceable_item_has_a_reach_row_and_the_observer_shortfall_is_caught(ev):
    rows = _rows(ev, "reachable through the belly service panel")
    names = {x[0].split(": ", 1)[1] for x in rows}
    assert {"tail speed controller", "RCS gateway", "winch (stack)",
            "Cargo Observer tray"} <= names
    obs = [x for x in rows if x[0].endswith("Cargo Observer tray")][0]
    assert not cd.passed(obs)  # the tray sits aft of the panel field (G1 finding)


def test_the_panel_fastener_count_follows_the_pitch(ev):
    p = ev["panel"]
    perim = 2.0 * ((p["x1"] - p["x0"]) + (p["y1"] - p["y0"]))
    assert p["fasteners"] == max(4, math.ceil(perim / cd.FASTENER_PITCH))


def test_the_aft_allowance_is_the_hand_moment_balance(ev):
    a, cg = ev["aft"], ev["cg"]
    m = cg["m0"] + cg["dm"]
    want = cd.REAR_BALLAST_CAP * (cd.REAR_BALLAST_Y - cg["y0"]) / (m + cd.REAR_BALLAST_CAP)
    assert math.isclose(a["rear_travel"], want)
    assert math.isclose(a["total"], a["movable_travel"] + a["rear_travel"])


def test_the_cg_effect_is_the_hand_moment_sum(ev):
    cg = ev["cg"]
    moment = 0.0
    for name, m, frm, to in cg["rows"]:
        moment += m * (to - (frm if frm is not None else cg["y0"]))
    assert math.isclose(cg["dy"], moment / (cg["m0"] + cg["dm"]))


def test_every_limit_is_printed_and_a_failing_layout_exits_nonzero(ev, capsys):
    ok = cd.report(ev)
    out = capsys.readouterr().out
    assert all(x[0] in out for x in ev["limits"])
    assert ok is all(cd.passed(x) for x in ev["limits"])
    assert ok is False  # Flight Engineer fit and Observer reach: the G1 brief reports them


# --- owner rules, 2026-11-19 (AGENTS.md; airframe/AGENTS.md "Interior Air Path") ---------------
def test_the_stream_floor_is_the_owner_benchmark():
    """8,000 mm2 (12.4 in2) at every bay station; a change that lowers it must be an owner
    decision, not an edit to make a layout fit."""
    assert cd.A_STREAM_MIN == 8000.0
    assert math.isclose(cd.A_STREAM_MIN / 645.16, 12.4, abs_tol=0.05)


def test_a_pcb_is_never_offered_an_orientation_that_faces_the_stream():
    board = (40.0, 60.0, 18.0)
    for dx, dy, dz in cd.orientations(board, pcb=True):
        assert dy > min(board)
    assert any(o[1] == 18.0 for o in cd.orientations(board))  # a non-PCB may take any
    assert cd.in_line(cd.Box("b", 0, 18, 0, 60, 0, 40))
    assert not cd.in_line(cd.Box("dam", 0, 58, 0, 22, 0, 37))


def test_every_board_in_the_duct_is_checked_and_the_air_dams_are_caught(ev):
    rows = {x[0].split(": ", 1)[1]: x for x in _rows(ev, "PCB in line with the airflow")}
    for b in ev["moved"]:
        if cd.is_pcb(b.name) and b.kind != "unplaced":
            assert cd.passed(rows[b.name]), b.name
    # the kept aft nodes and the Observer tray stand across the flow today (re-lay, OQ6)
    for name in ("node N2 FC2 (aft port)", "node N4 FC3 (aft stbd)", "observer tray"):
        assert not cd.passed(rows[name]), name
    assert cd.passed(rows["tilt controller board"])
