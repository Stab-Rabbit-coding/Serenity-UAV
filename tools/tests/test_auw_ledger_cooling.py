# License: MIT — see LICENSES/MIT.txt (SPDX-License-Identifier: MIT)
"""Tests for the PROVISIONAL cooling-airflow block of tools/auw_ledger.py."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "auw_ledger", Path(__file__).resolve().parents[1] / "auw_ledger.py")
assert _spec is not None and _spec.loader is not None
al = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(al)
CA = al.COOLING_AIRFLOW


def test_block_is_marked_provisional():
    assert CA["status"].startswith("PROVISIONAL")


def test_idle_is_the_controller_minimum_when_the_flow_need_is_lower():
    need, full = CA["need_lps"]["avg_chin_3000mm2"][0], CA["full_throttle_lps"][0]
    assert need / full < CA["esc_min_stable_throttle"]
    assert al.cooling_idle_throttle(need, full) == CA["esc_min_stable_throttle"]


def test_idle_follows_the_flow_need_when_it_is_higher():
    assert al.cooling_idle_throttle(50.0, 100.0, esc_min=0.10) == 0.5


def test_chin_flow_guides_cut_the_flow_needed():
    n = CA["need_lps"]
    for i in (0, 1):
        assert n["avg_chin_3000mm2"][i] < n["avg_no_guides"][i]


def test_louvres_need_more_flow_and_give_less():
    n = CA["need_lps"]
    assert n["avg_no_guides"][1] > n["avg_no_guides"][0]
    assert CA["full_throttle_lps"][1] < CA["full_throttle_lps"][0]
