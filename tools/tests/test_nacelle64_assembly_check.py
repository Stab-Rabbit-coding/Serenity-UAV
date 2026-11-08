"""Unit tests for tools/nacelle64_assembly_check.py (geometry helpers; no meshes needed).

Author: Claude Opus 5.5 (Anthropic) for S. Griffing, 2026-11-07.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import sys
from pathlib import Path

import numpy as np
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import nacelle64_assembly_check as a  # noqa: E402


def test_tilt_fixes_pivot_and_points_exhaust_down_in_hover():
    r = a.tilt_matrix(90.0)
    pivot = np.array([0.0, 0.0, a.PIVOT_Z, 1.0])
    assert np.allclose(r @ pivot, pivot)
    # 0 deg: duct axis +Z points aft; +90 deg (hover): exhaust points down = hull -Z = local +Y
    tip = np.array([0.0, 0.0, a.PIVOT_Z + 10.0, 1.0])
    assert np.allclose((r @ tip)[:3], [0.0, 10.0, a.PIVOT_Z], atol=1e-9)


def test_stack_datums():
    assert abs(a.SEAT - 56.31) < 0.01        # 41.7 + 9.61 + 7.0 - 2.0
    assert abs(a.TRUNNION_X0 - 37.81) < 0.01


def test_fix_nonmanifold_splits_edge_touching_cubes():
    c1 = trimesh.creation.box(extents=(1, 1, 1))
    c1.apply_translation((0.5, 0.5, 0.5))
    c2 = c1.copy()
    c2.apply_translation((1.0, 1.0, 0.0))          # touches c1 along one edge only
    both = trimesh.util.concatenate([c1, c2])
    both.merge_vertices()
    fixed = a.fix_nonmanifold(both)
    mn = a.to_man(fixed)
    assert mn.status().name == "NoError"
    assert abs(mn.volume() - 2.0) < 1e-6


def test_bay_insert_walls_meet_minimum_and_old_insert_did_not():
    far = a.m.Manifold.cube([1, 1, 1]).translate([500, 500, 500])
    res = a.bay_check(far)
    assert res["min_wall_ok"]
    assert min(res["insert_wall_to_bore_mm"]) >= a.MIN_WALL
    assert res["floor_material_mm3"] == 0 and res["mouth_material_mm3"] == 0
    old = a.BAY_INSERT_L
    try:
        a.BAY_INSERT_L = 6.0          # the shared M3_INSERT_L used before 2026-11-08
        assert not a.bay_check(far)["min_wall_ok"]
    finally:
        a.BAY_INSERT_L = old
