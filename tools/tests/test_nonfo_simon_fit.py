# License: MIT — see LICENSES/MIT.txt (SPDX-License-Identifier: MIT)
"""Mesh-free tests for tools/nonfo_simon_fit.py (the hull fit itself runs as a tool)."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "nonfo_simon_fit", Path(__file__).resolve().parents[1] / "nonfo_simon_fit.py")
assert _spec is not None and _spec.loader is not None
nf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(nf)
C = nf.load_contract()


def test_outline_is_the_beaglebone_black_cape():
    assert (C["outline"]["w"], C["outline"]["h"]) == (86.36, 54.61)
    assert len(C["holes"]["xy"]) == 4


def test_pb2_shadow_sits_inside_the_outline():
    s = C["pb2_shadow"]
    assert 0 <= s["x0"] < s["x1"] <= C["outline"]["w"]
    assert 0 <= s["y0"] < s["y1"] <= C["outline"]["h"]
    assert abs((s["x1"] - s["x0"]) - 55.0) < 1e-9 and abs((s["y1"] - s["y0"]) - 35.0) < 1e-9


def test_stack_height_sums_the_contract_and_meets_target():
    h = nf.stack_height(C)
    assert abs(h - 19.74) < 1e-6
    assert h <= C["limits"]["stack_height_target"]


def test_mass_meets_r2_and_thinner_board_is_lighter():
    assert nf.stack_mass(C, "t1.0") < nf.stack_mass(C, "t1.6") < C["limits"]["stack_mass_g_max"]


def test_mass_limit_trips_when_a_line_grows():
    heavy = dict(C, mass_g=dict(C["mass_g"], extra={"g": 20.0, "basis": "test"}))
    assert nf.stack_mass(heavy) >= C["limits"]["stack_mass_g_max"]


def test_power_is_volts_times_summed_current():
    amps = sum(v["a_peak"] for v in C["power_5v"].values())
    assert abs(nf.power_peak_w(C) - 5.0 * amps) < 1e-9
