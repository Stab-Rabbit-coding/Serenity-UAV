"""Characterization tests for tools/nacelle64_esc_housing.py (H1, WBS NAC-64-ESC-BLISTER).

Written after the generator (exception to test-first: the geometry was settled in a reviewed
concept, docs/figures/h1_esc_housing_canonical.png); they pin the owner-visible contract.
SPDX-License-Identifier: MIT
"""

import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
pytest.importorskip("manifold3d")
import nacelle64_esc_housing as g  # noqa: E402


@pytest.fixture(scope="module")
def built():
    return g.build()


@pytest.mark.slow
def test_covers_esc_b_and_stops_short_of_the_nozzle_housing(built):
    proud, rep = built
    assert rep["status_ok"]
    assert rep["esc_b_board_outside_mm3"] < 0.05
    assert rep["z_extent_mm"][1] <= g.Z_LOGIC_AFT + 0.01 < 160.25


@pytest.mark.slow
def test_louvres_equal_the_design_bleed_area(built):
    _, rep = built
    assert rep["louvre_open_area_mm2"] == pytest.approx(rep["design_bleed_area_mm2"], abs=0.5)


@pytest.mark.slow
def test_outer_faces_sit_one_wall_above_the_boards(built):
    proud, _ = built
    v = g.tmesh(proud).vertices
    r_max = float(np.hypot(v[:, 0], v[:, 1]).max())
    corner = max(
        math.hypot(g.MOUNT_R + env + g.SKIN_WALL, w / 2 + g.SKIN_WALL)
        for env in g.ENV.values()
        for w in (g.W_POWER, g.W_SIGNAL)
    )
    assert r_max == pytest.approx(corner, abs=0.1)


def test_wall_meets_the_sls_minimum():
    assert g.COVER_T >= 2.0  # AGENTS.md sec. 7 default SLS wall
