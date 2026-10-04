"""Tests for tools/esc80_cooptimize.py (WBS NAC-64-ESC-80A).

Unit tests use small synthetic skin grids so they run without the shell mesh;
the golden tests run the real harness end to end (the first run ray-casts the
shell and caches it under ~/.cache/serenity-esc80).

Tests by Claude (Claude Opus 5.5, Anthropic), per AGENTS.md AI attribution.
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

import esc80_cooptimize as h  # noqa: E402


def _uniform_skin(n_rings, radius):
    """Skin grid with the same outer radius everywhere."""
    return np.full((n_rings, h.bay.N_AZ_SAMPLE), float(radius))


# ── area_after_reserve ───────────────────────────────────────────────────────

PROF = [(100.0, 20.0, 10.0), (102.0, 20.0, 10.0), (104.0, 10.0, 5.0)]


def test_reserve_zero_keeps_whole_run():
    a_p, a_s, span, zz = h.area_after_reserve(PROF, 0.0, 0.0)
    assert span == pytest.approx(6.0)
    assert a_p == pytest.approx(2 * 20 + 2 * 20 + 2 * 10)
    assert a_s == pytest.approx(2 * 10 + 2 * 10 + 2 * 5)
    assert zz == (100.0, 106.0)


def test_reserve_trims_partial_rings():
    a_p, _, span, _ = h.area_after_reserve(PROF, 1.0, 1.0)
    assert span == pytest.approx(4.0)
    assert a_p == pytest.approx(1 * 20 + 2 * 20 + 1 * 10)


def test_reserve_longer_than_run_gives_zero_not_negative():
    a_p, a_s, span, _ = h.area_after_reserve(PROF, 5.0, 5.0)
    assert (a_p, a_s, span) == (0.0, 0.0, 0.0)


# ── free_beyond ──────────────────────────────────────────────────────────────

def test_free_beyond_counts_rings_until_blocked():
    zs = np.arange(100.0, 120.0, h.DZ)
    skin = _uniform_skin(len(zs), 60.0)
    skin[1, :] = h.MOUNT_R          # ring at Z 102 leaves no room for a lead
    prof = [(z, 1.0, 1.0) for z in zs[4:6]]        # board run Z 108-112
    h.bay.SKIN_WALL = 1.9
    fwd = h.free_beyond(zs, skin, 0.0, prof, 3.0, -1)
    assert fwd == pytest.approx(2 * h.DZ)            # Z 106, 104 then blocked


def test_free_beyond_aft_respects_loop_z_max():
    zs = np.arange(h.LOOP_Z_MAX - 10.0, h.LOOP_Z_MAX + 10.0, h.DZ)
    skin = _uniform_skin(len(zs), 60.0)
    prof = [(zs[0], 1.0, 1.0)]
    h.bay.SKIN_WALL = 1.9
    aft = h.free_beyond(zs, skin, 0.0, prof, 3.0, +1)
    assert prof[0][0] + h.DZ + aft <= h.LOOP_Z_MAX + 1e-9


def test_free_beyond_empty_side_is_zero():
    zs = np.arange(100.0, 104.0, h.DZ)
    skin = _uniform_skin(len(zs), 60.0)
    prof = [(100.0, 1.0, 1.0)]
    assert h.free_beyond(zs, skin, 0.0, prof, 3.0, -1) == 0.0


# ── ring_width_fit ───────────────────────────────────────────────────────────

def test_ring_width_returns_nominal_when_it_fits():
    skin = _uniform_skin(1, 80.0)
    h.bay.SKIN_WALL = 1.9
    h.bay.duct_r = lambda z: h.DUCT_R_64
    h.bay.DUCT_WALL = h.MOUNT_R - h.DUCT_R_64
    assert h.ring_width_fit(skin, 0, 90.0, h.MOUNT_R, 5.0, 23.0, +1) == 23.0


def test_ring_width_is_zero_when_nothing_fits():
    skin = _uniform_skin(1, h.MOUNT_R + 1.0)
    h.bay.SKIN_WALL = 1.9
    assert h.ring_width_fit(skin, 0, 90.0, h.MOUNT_R, 5.0, 23.0, +1) == pytest.approx(0.0, abs=1e-3)


def test_ring_width_bisection_matches_corner_limit():
    """Corner radius sqrt(d_out^2 + (w/2)^2) must equal skin - wall at the result."""
    r_skin, wall, env = 46.0, 1.9, 5.0
    skin = _uniform_skin(1, r_skin)
    h.bay.SKIN_WALL = wall
    w = h.ring_width_fit(skin, 0, 90.0, h.MOUNT_R, env, 40.0, +1)
    expected = 2 * np.sqrt((r_skin - wall) ** 2 - (h.MOUNT_R + env) ** 2)
    assert w == pytest.approx(expected, abs=1e-3)


# ── golden end-to-end runs ───────────────────────────────────────────────────

def _run(design):
    proc = subprocess.run([sys.executable, str(TOOLS / "esc80_cooptimize.py"),
                           str(TOOLS / design)], capture_output=True, text=True,
                          timeout=1800)
    return proc.returncode, json.loads(proc.stdout)


@pytest.mark.slow
def test_model1_golden_unchanged():
    """Model 2 work must not move model 1 (ce-optimize phase-1 best point)."""
    _, out = _run("esc80_design.json")
    assert out["fit_margin_mm"] == pytest.approx(-6.51, abs=0.01)


@pytest.mark.slow
def test_model2_best_point_passes_and_reports_hotter_esc():
    code, out = _run("esc80_design_m2.json")
    assert code == 0
    assert out["fit_margin_mm"] >= 0
    hottest = max(e["tch_c"] for e in out["esc"].values())
    assert out["tch_c"] == pytest.approx(hottest)
    assert out["tch_c"] <= h.T_CH_DESIGN


@pytest.mark.slow
def test_failing_design_exits_nonzero(tmp_path):
    p = json.loads((TOOLS / "esc80_design_m2.json").read_text())
    p["bays_per_esc"] = 1                  # known not to fit (phase-2 log)
    f = tmp_path / "fail.json"
    f.write_text(json.dumps(p))
    proc = subprocess.run([sys.executable, str(TOOLS / "esc80_cooptimize.py"), str(f)],
                          capture_output=True, text=True, timeout=1800)
    assert proc.returncode != 0
