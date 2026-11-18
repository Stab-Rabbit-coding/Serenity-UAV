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

import numpy as np
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
def test_the_jet_set_is_symmetric_port_to_starboard():
    up = [j for j in rc.JETS if not j.ventral]
    ven = [j for j in rc.JETS if j.ventral]
    assert len(up) == 2 and up[0].az_deg + up[1].az_deg == 180.0
    assert len(ven) == 1 and ven[0].az_deg == 270.0  # owner option B: one jet on the centreline
    lo, hi = ven[0].panel
    assert math.isclose(270.0 - lo, hi - 270.0, abs_tol=1.0)  # the panel joints straddle 270


def test_a_centred_exhaust_is_its_area_over_its_length_about_its_azimuth(ev):
    """Review #5: checks exhaust_fit itself, against the closed form."""
    j = [t for t in rc.JETS if t.edges == "centred"][0]
    e = ev["exhaust"][j.name]
    w = j.area_mm2 / (j.y1 - j.y0)
    assert math.isclose(e["width_mm"], w)
    half = math.degrees(w / 2.0 / e["r_out"])
    assert math.isclose(e["edges"][0], j.az_deg - half)
    assert math.isclose(e["edges"][1], j.az_deg + half)
    for edge, joint, dd, mm in e["shifts"]:
        assert math.isclose(edge + dd, joint)
        assert math.isclose(mm, math.radians(abs(dd)) * e["r_out"])


def test_the_signed_angle_wraps_through_north():
    assert rc._ang(359.0 - 1.0) == -2.0 and rc._ang(1.0 - 359.0) == 2.0


def test_the_panel_exhaust_sits_on_the_centre_panel_joints_and_narrows_aft(ev):
    """Owner option B: the ventral exhaust's sides are the centre belly panel's joints."""
    j = [t for t in rc.JETS if t.edges == "panel"][0]
    e = ev["exhaust"][j.name]
    assert e["kind"] == "panel"
    for found, want in zip(e["edges"], j.panel):
        assert abs(found - want) <= 1.0
    assert e["width_fwd"] > e["width_aft"]  # the cone narrows aft
    assert abs(e["area_mm2"] / j.area_mm2 - 1.0) <= 0.03


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
    rules = dict(ev["design_rules"])
    assert rules["shroud ends at the joint, forward of the scoops"]


def test_the_motor_and_rotor_stay_inside_the_hull_and_forward_of_the_nozzle_exit(ev):
    L = ev["layout"]
    assert rc.STERN_STACK_Y1 < L["motor_y0"] < L["motor_face_y"] < L["rotor_y0"]
    assert L["rotor_y1"] < L["exit_y"]
    for start in ("motor clear of the stern stack", "rotor forward of the nozzle exit"):
        assert all(rc.passed(x) for x in _row(ev, start))


def test_the_pusher_stack_runs_motor_then_plate_then_rotor_aft_with_the_rotor_at_the_joint():
    """KD10 / KTD6: the motor is ahead of the rotor; the rotor is at the aft end of the shroud,
    just forward of the shroud joint and the Y 628 scoops."""
    st = rc.pusher_stack()
    assert st["motor_y0"] < st["motor_face_y"] == st["plate_y0"] < st["plate_y1"]
    assert st["plate_y1"] + rc.ROTOR_GAP == st["rotor_y0"] < st["rotor_y1"]
    assert st["rotor_y1"] == rc.SHROUD_JOINT_Y - rc.SHROUD_AFT_OF_ROTOR < rc.SCOOP_Y
    assert st["vanes_y1"] <= st["rotor_y0"]  # the plate's stator vanes are AHEAD of the rotor


def test_the_tube_stator_keeps_the_vane_row_wider_than_the_nozzle():
    """The vanes and hub fairing shall not become the throat in place of the R22 nozzle."""
    st = rc.tube_stator(650.0, 626.0)
    assert st is not None and st["ratio"] >= rc.THROAT_MARGIN
    assert st["le"] >= rc.SCOOP_Y + rc.SCOOP_LIP_L  # aft of the scoop lips
    lo, _ = rc.stator_min_ratio(650.0, st)
    assert math.isclose(lo, st["ratio"])
    # the same row moved 6 mm aft, into the narrower taper, falls below the margin
    aft = {**st, "le": st["le"] + 6.0, "te": st["te"] + 6.0, "hub_y1": st["hub_y1"] + 6.0}
    assert rc.stator_min_ratio(650.0, aft)[0] < rc.THROAT_MARGIN


def test_the_free_area_with_no_vanes_or_hub_is_the_bore_over_the_nozzle():
    st = {"n": 0, "le": 700.0, "te": 701.0, "hub_y0": 0.0, "hub_y1": 0.0}
    a, b = rc.tube_bore_ab(627.0, 650.0)
    want = (a * b) / (rc.NOZZLE_A * rc.NOZZLE_B / 4.0)
    assert math.isclose(rc.tube_free_ratio(627.0, 650.0, st), want)
    assert math.isclose(rc.tube_free_ratio(650.0, 650.0, st), 1.0)


def test_holding_the_bore_longer_allows_a_more_solid_stator():
    a = rc.tube_stator(650.0, 626.0)
    b = rc.tube_stator(650.0, 626.0, taper_y0=640.0)
    assert b["solidity"] > a["solidity"]


def test_the_nacelle_solidity_is_chord_over_pitch_at_the_mean_radius():
    pitch = 2.0 * math.pi * 0.5 * (rc.VANE_HUB_R + rc.ROTOR_TIP_R) / rc.N_VANES
    assert math.isclose(rc.NACELLE_SOLIDITY, rc.VANE_CHORD / pitch)


def test_the_scoop_faces_less_swirl_at_the_wall_than_the_rotor_mean_radius():
    """Free vortex: V_theta r is constant, so the wall sees less tangential speed."""
    d, sw = rc.scoop_deswirl(0.8), rc.rotor_swirl(0.8)
    r_m = 0.5 * (rc.VANE_HUB_R + rc.ROTOR_TIP_R)
    assert math.isclose(d["v_theta"] * rc.TUBE_R627, sw["v_theta"] * r_m)
    assert 0.0 < d["yaw_deg"] < 90.0


def test_the_tube_stator_and_its_checks_are_in_the_layout(ev):
    st = ev["layout"]["tube_stator"]
    assert any(p[0].startswith("tube stator") for p in ev["parts"])
    # the owner accepted the sparse stator (2026-11-18): reported, not a pass/fail limit
    assert st["solidity"] < rc.NACELLE_SOLIDITY
    assert not any(x[0].startswith("tube stator solidity") for x in ev["limits"])
    assert dict(ev["design_rules"])[
        "tube stator free area >= margin x nozzle (the search's own filter)"]
    cv = ev["contour"]
    assert cv["stator"]["solidity"] >= rc.NACELLE_SOLIDITY > st["solidity"]


def test_the_rotor_exit_swirl_is_reported_and_grows_with_pressure_rise():
    """Euler: V_theta = dp / (rho U); with no exit stator it reaches the scoops."""
    lo, hi = rc.rotor_swirl(0.8), rc.rotor_swirl(1.0)
    assert lo["swirl_deg"] > 30.0 and hi["v_theta"] > lo["v_theta"]
    import tail_edf_flow as tf
    assert math.isclose(lo["v_theta"], lo["dp_fan"] / (tf.Inputs().rho * lo["u_m"]))


def test_the_plate_stack_overhang_is_longer_than_the_stock_rotor_mounting():
    assert rc.default_overhang() - rc.stock_overhang() == rc.PLATE_T + rc.ROTOR_GAP
    assert (rc.critical_rpm(3.0, rc.BEARING_SPAN, rc.default_overhang(), rc.ROTOR_G)
            < rc.critical_rpm(3.0, rc.BEARING_SPAN, rc.stock_overhang(), rc.ROTOR_G))


def test_the_ventral_exhaust_rows_use_the_jets_own_station(ev, monkeypatch):
    """Review #2: the KD16 / crossbar rows read each ventral jet's own forward edge."""
    for start in ("ventral exhaust forward edge at or aft of Y 628",
                  "ventral exhaust forward edge clear of the crossbar"):
        assert all(rc.passed(x) for x in _row(ev, start))
    import dataclasses
    early = tuple(dataclasses.replace(j, y0=632.0) if j.ventral else j for j in rc.JETS)
    monkeypatch.setattr(rc, "JETS", early)
    rows = [x for x in rc.limits(ev) if x[0].startswith(
        "ventral exhaust forward edge clear of the crossbar")]
    assert rows and not any(rc.passed(x) for x in rows)


def test_the_passage_check_runs_at_both_stations_for_every_jet(ev):
    rows = _row(ev, "passage area >= exhaust area")
    assert len(rows) == 2 * len(rc.JETS)
    need = ev["sector_needed"]
    for j in rc.JETS:
        mine = [x for x in rows if x[0].endswith(j.name)]
        now = j.sector[1] - j.sector[0]
        # a passage passes at both stations exactly when its sector is at least the need
        assert all(rc.passed(x) for x in mine) is (now >= need[j.name])
    # the 45 deg upper sectors fall short until brief 4 widens them
    assert not any(rc.passed(x) for x in rows if "upper" in x[0])


def test_a_web_thinner_than_the_minimum_printed_wall_fails(ev, monkeypatch):
    import dataclasses
    up = [j for j in rc.JETS if not j.ventral]
    tight = (dataclasses.replace(up[0], sector=(22.5, 89.6)),
             dataclasses.replace(up[1], sector=(90.0, 157.5))) + tuple(
                 j for j in rc.JETS if j.ventral)
    webs = rc.passage_webs(ev["layout"], tight)
    assert webs[0][2] < rc.WALL_MIN_PRINT
    assert rc.passage_webs(ev["layout"])[0][2] >= rc.WALL_MIN_PRINT


def test_the_planned_ventral_pair_strikes_the_skid_pods_and_mirrors(ev):
    a, b = ev["plan_jets"]["ventral 245"], ev["plan_jets"]["ventral 295"]
    assert not a["clear"] and not b["clear"]
    assert rc.classify_hit(a["nearest"]) == rc.classify_hit(b["nearest"]) == "pod"
    assert a["blocked"] == b["blocked"]
    assert math.isclose(a["nearest"][1][0], -b["nearest"][1][0], abs_tol=0.5)


def test_the_flown_jets_are_clear_and_both_ventral_sides_are_probed(ev):
    assert all(j["clear"] for j in ev["jets"].values())
    band = ev["ventral_band"]
    for y in (635.0, 638.0, 641.0):
        assert band[(y, 270.0)] is None
        # the hull is probed on both sides, not mirrored: 255 and 285 agree here
        assert (band[(y, 255.0)] is None) == (band[(y, 285.0)] is None)


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


def test_the_plate_joints_are_mapped_and_each_centred_exhaust_reports_its_joint_shift(ev):
    joints = ev["joints"][630]
    assert len(joints) >= 10
    for e in ev["exhaust"].values():
        if e["kind"] == "centred":
            assert len(e["shifts"]) == 2 and all(sh[3] >= 0.0 for sh in e["shifts"])


def test_the_first_critical_speed_row_is_in_the_limits_list(ev):
    rows = _row(ev, "first critical speed over the top running speed")
    assert rows[0][1] == ev["crit_rpm"] / ev["top_rpm"]


def test_every_limit_is_printed_and_a_failing_layout_exits_nonzero(ev, capsys):
    ok = rc.report(ev)
    out = capsys.readouterr().out
    assert all(x[0] in out for x in ev["limits"])
    assert ok is all(rc.passed(x) for x in ev["limits"])
    assert ok is False  # critical speed and the 45 deg upper passages fail: the G1 brief


# --- review fixes and hand checks (2026-11-18) ---------------------------------------------
def test_the_hub_fairing_is_a_straight_cone():
    """Review #7: r falls linearly to a point; its half-angle is atan(R / length)."""
    y0, y1 = 600.0, 620.0
    assert rc.hub_r(590.0, y0, y1) == rc.VANE_HUB_R
    assert math.isclose(rc.hub_r(610.0, y0, y1), rc.VANE_HUB_R / 2.0)
    assert rc.hub_r(620.0, y0, y1) == 0.0
    st = rc.tube_stator(650.0, 626.0)
    assert math.isclose(st["boat_tail_deg"],
                        math.degrees(math.atan2(rc.VANE_HUB_R, st["hub_y1"] - st["hub_y0"])))


def test_passage_area_is_the_annulus_sector_less_side_walls(monkeypatch):
    """Review #8: trapezoid rule; a uniform gap gives the closed-form sector exactly."""
    monkeypatch.setattr(rc, "section_solid", lambda mesh, y: None)
    monkeypatch.setattr(rc, "skin_radii", lambda s, z, az: (40.0, 41.0))
    monkeypatch.setattr(rc, "tube_outer_r", lambda y, az, e, t=None: 30.0)
    area, gmin, gmax = rc.passage_area(None, {"z_axis": 0.0, "exit_y": 650.0}, 10.0, 60.0)
    want = 0.5 * (40.0 ** 2 - 30.0 ** 2) * math.radians(50.0) - 2.0 * rc.SIDE_WALL * 10.0
    assert math.isclose(area, want, rel_tol=1e-12) and gmin == gmax == 10.0


def test_the_cg_shift_is_the_hand_moment_balance(tmp_path, monkeypatch):
    led = tmp_path / "led.json"
    led.write_text('{"configs": {"hover_twin_2200": {"mass_g": 6000.0, "cg": [0, 340.0, 0]}}}')
    monkeypatch.setattr(rc, "LEDGER", str(led))
    got = rc.cg_shift([("a", 100.0, 640.0, ""), ("b", 50.0, 600.0, "")])
    want = (100.0 * 300.0 + 50.0 * 260.0) / 6150.0
    assert math.isclose(got["dy"], want) and got["dm"] == 150.0


def test_the_dunkerley_critical_speed_matches_a_hand_value():
    d, span, a, m = 3.0e-3, 20.0e-3, rc.default_overhang() * 1e-3, rc.ROTOR_G * 1e-3
    i = math.pi * d ** 4 / 64.0
    w_r = math.sqrt(3.0 * rc.SHAFT_E * i / (a ** 2 * (span + a)) / m)
    w_s = (math.pi / span) ** 2 * math.sqrt(rc.SHAFT_E * i
                                            / (rc.SHAFT_RHO * math.pi * d ** 2 / 4.0))
    w = 1.0 / math.sqrt(1.0 / w_r ** 2 + 1.0 / w_s ** 2)
    got = rc.critical_rpm(3.0, 20.0, rc.default_overhang(), rc.ROTOR_G)
    assert math.isclose(got, w * 60.0 / (2.0 * math.pi), rel_tol=1e-9)


def test_the_jet_table_matches_the_hull(ev):
    """The shared table's measured radii are the hull's; a hull change fails here."""
    mesh = rc.load_aft_hull()
    for j in rc.JETS:
        r = rc.skin_radii(rc.section_solid(mesh, j.y), ev["layout"]["z_axis"], j.az_deg)[1]
        assert abs(r - j.r_mm) < 0.1, j.name


def test_json_output_is_written_and_loads(ev, tmp_path, monkeypatch, capsys):
    """Review #3: the ventral map's tuple keys are written as "Y/az" strings."""
    import json
    monkeypatch.setattr(rc, "evaluate", lambda: ev)
    out = tmp_path / "r.json"
    assert rc.main(["--json", str(out)]) == 1
    capsys.readouterr()
    d = json.loads(out.read_text())
    assert "635/270" in d["ventral_band"] and len(d["limits"]) == len(ev["limits"])


def test_an_open_mesh_is_refused(tmp_path, monkeypatch):
    import trimesh
    box = trimesh.creation.box()
    box.update_faces(np.arange(len(box.faces)) > 0)  # drop one face: no longer watertight
    path = tmp_path / "open.stl"
    box.export(str(path))
    monkeypatch.setattr(rc, "AFT_HULL", str(path))
    monkeypatch.setattr(rc, "_MESH", {})
    with pytest.raises(SystemExit):
        rc.load_aft_hull()
