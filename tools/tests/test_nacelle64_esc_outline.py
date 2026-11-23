"""Tests for tools/nacelle64_esc_outline.py (WBS NAC-64-ESC-OUTLINE).

A cover far outside the board must leave the full rectangle; a cover cut into the board stack
must remove width from the far edge first, never from the hinge.

License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
trimesh = pytest.importorskip("trimesh")
import nacelle64_esc_housing as hg  # noqa: E402
import nacelle64_esc_outline as eo  # noqa: E402


def _tube(r_in, r_out, z0=0.0, z1=220.0):
    outer = trimesh.creation.cylinder(radius=r_out, height=z1 - z0, sections=360)
    inner = trimesh.creation.cylinder(radius=r_in, height=z1 - z0 + 2, sections=360)
    t = outer.difference(inner)
    t.apply_translation([0, 0, (z0 + z1) / 2])
    return t


def test_far_cover_leaves_the_full_rectangle():
    b, role, _ = eo.bay_of(2)
    r = eo.panel_outline(_tube(60.0, 62.0), b, hg.ENV[role])
    assert r["area_per_face_mm2"] == pytest.approx(r["full_area_per_face_mm2"], rel=1e-6)


def test_cover_low_at_the_far_edge_trims_from_the_far_edge():
    """A cover higher over the hinge than over the far edge (centre shifted toward az - 60 deg):
    the far edge loses width, the hinge keeps it."""
    import math

    b, role, _ = eo.bay_of(2)
    env = hg.ENV[role]
    corner = math.hypot(hg.MOUNT_R + env, hg.W_POWER / 2) + hg.COVER_CLR
    tube = _tube(corner - 0.2, corner + 2.0)
    a = math.radians(b["az"] - 60.0)
    tube.apply_translation([2.0 * math.cos(a), 2.0 * math.sin(a), 0.0])
    r = eo.panel_outline(tube, b, env)
    assert all(0.0 < w < hg.W_POWER for w in r["power"])  # trimmed, but the hinge holds


def test_flat_panel_edges_sit_at_one_radius():
    """Behaviour note: a flat panel tangent at its centre has both edges at the same radius, so a
    round cover centred on the axis that fails one edge fails the hinge too (zero width)."""
    b, role, _ = eo.bay_of(2)
    env = hg.ENV[role]
    r_cov = hg.MOUNT_R + env + hg.COVER_CLR + 0.3
    r = eo.panel_outline(_tube(r_cov, r_cov + 2.0), b, env)
    assert all(w == 0.0 for w in r["power"])
