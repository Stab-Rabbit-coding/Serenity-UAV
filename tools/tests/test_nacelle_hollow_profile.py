"""Regression tests for tools/nacelle_hollow_profile.py (WBS NAC-64-HOLLOW-SKIN).

The skin grid must be the NEAR-side outer skin.  The ray cast used to run each ray through the
duct axis and keep the largest hit, so skin(az) became max(skin(az), skin(az + 180)) and the
committed cavity was cut to the opposite, fatter side's skin -- it broke through the 64 mm pod's
belly.  SPDX-License-Identifier: MIT
"""

import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nacelle_hollow_profile as hp  # noqa: E402

trimesh = pytest.importorskip("trimesh")


def _near_skin(mesh, z, az_deg):
    a = math.radians(az_deg)
    o = np.array([[200.0 * math.cos(a), 200.0 * math.sin(a), z]])
    d = np.array([[-math.cos(a), -math.sin(a), 0.0]])
    loc, _, _ = mesh.ray.intersects_location(o, d, multiple_hits=True)
    s = loc[:, 0] * math.cos(a) + loc[:, 1] * math.sin(a)
    return float(np.hypot(loc[s > 0, 0], loc[s > 0, 1]).max())


@pytest.mark.slow
def test_skin_grid_reads_the_near_side():
    zs, az, outer = hp.skin_grid("STBD")
    name, cx = hp.SHELLS["STBD"]
    mesh = trimesh.load_mesh(hp.REPO / "airframe/stls/nacelles" / name, force="mesh")
    mesh.apply_translation([-cx, hp.BORE_CY, 0.0])
    k = int(np.argmin(abs(zs - 105.0)))
    worst = 0.0
    for j in range(0, len(az), 4):
        truth = _near_skin(mesh, float(zs[k]), float(az[j]))
        # the grid is the conservative MIN over a 3x3 sub-sample, so it may sit below the
        # centre-ray truth, but never above it by more than a sampling tolerance
        worst = max(worst, outer[k, j] - truth)
    assert worst < 0.5, f"skin grid exceeds the near-side skin by {worst:.2f} mm"


@pytest.mark.slow
def test_cavity_leaves_a_wall_under_the_true_skin():
    zs, az, outer = hp.skin_grid("STBD")
    rc = hp.cavity_radii(zs, outer)
    name, cx = hp.SHELLS["STBD"]
    mesh = trimesh.load_mesh(hp.REPO / "airframe/stls/nacelles" / name, force="mesh")
    mesh.apply_translation([-cx, hp.BORE_CY, 0.0])
    for k in range(0, len(zs), 6):
        for j in range(0, len(az), 6):
            inner = hp.bore_r(float(zs[k])) + hp.DUCT_WALL
            if rc[k, j] < inner:  # ring closed into the duct wall: no cavity here
                continue
            wall = _near_skin(mesh, float(zs[k]), float(az[j])) - rc[k, j]
            assert wall >= hp.wall(float(zs[k])) - 0.5, (zs[k], az[j], wall)
