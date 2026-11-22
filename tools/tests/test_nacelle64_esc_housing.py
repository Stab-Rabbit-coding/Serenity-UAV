"""Characterization tests for tools/nacelle64_esc_housing.py (H1, WBS NAC-64-ESC-BLISTER).

Written after the generator (exception to test-first: the geometry was settled in a reviewed
concept, docs/figures/h1_esc_housing_canonical.png); they pin the owner-visible contract.

License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
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
    assert rep["z_extent_mm"][1] <= g.Z_LOGIC_AFT + 0.01 <= g.Z_F1_HOUSING - 0.4


@pytest.mark.slow
def test_logic_housing_has_a_full_aft_wall():
    assert g.Z_LOGIC_AFT - g.G1_BAYS["B"][1]["z"][1] >= g.SKIN_WALL - 1e-9


@pytest.mark.slow
def test_every_louvre_opens_to_air(built):
    _, rep = built
    assert rep["louvres_blocked"] == []
    assert len(g.louvre_z(g.G1_BAYS["B"][0])) * g.LOUVRE[0] * g.LOUVRE[1] == pytest.approx(
        rep["design_bleed_area_mm2"], abs=0.5
    )


@pytest.mark.slow
def test_measured_wall_over_the_boards_is_clearance_plus_plate(built):
    """Ray-cast on the built solid, including under every panel-line groove."""
    _, rep = built
    assert rep["wall_over_boards_min_mm"] >= g.COVER_CLR + g.COVER_T - 0.05


def test_no_panel_line_crosses_a_louvre():
    b = g.G1_BAYS["B"][0]
    gz, lz = g.groove_z(b, "power"), g.louvre_z(b)
    assert gz, "power face lost all its panel lines"
    for z in gz:
        assert all(abs(z - zc) > g.LOUVRE[0] / 2 + g.GROOVE_W / 2 for zc in lz)


@pytest.mark.slow
def test_outer_faces_sit_one_wall_above_the_boards(built):
    proud, _ = built
    v = g.tmesh(proud).vertices
    r_max = float(np.hypot(v[:, 0], v[:, 1]).max())
    corner = max(
        math.hypot(g.MOUNT_R + env + g.TOP_WALL, w / 2 + g.SKIN_WALL)
        for env in g.ENV.values()
        for w in (g.W_POWER, g.W_SIGNAL)
    )
    assert r_max == pytest.approx(corner, abs=0.1)


def test_wall_meets_the_sls_minimum():
    assert g.COVER_T >= 2.0  # AGENTS.md sec. 7 default SLS wall
    assert g.TOP_WALL - g.GROOVE_D - g.COVER_CLR >= 2.0  # still 2.0 mm under a panel line
