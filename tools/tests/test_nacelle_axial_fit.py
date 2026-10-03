"""Tests for tools/nacelle_axial_fit.py (plan 2026-09-28-001 U9).

Tests by Claude (Claude Opus 5.5, Anthropic), per AGENTS.md AI attribution.
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import nacelle_axial_fit as fit


def test_stations_read_from_scad():
    """Stations come from the pod SCAD, not from constants in the tool."""
    st = fit.stations()
    assert st["NACELLE_L"] == pytest.approx(185.2)
    assert st["EDF1_Z_ENTRY"] < st["NOZZLE_RING_Z"] < st["NACELLE_L"]


def test_shaft_protrusion_from_drawing():
    """68.7 mm overall less 58.0 mm body leaves a 10.7 mm shaft."""
    assert fit.SHAFT_PROTRUSION == pytest.approx(10.7)


def test_best_case_is_more_favourable_than_current():
    """BEST must never need more length than CURRENT."""
    st = fit.stations()
    res = {c.name: fit.evaluate(c, st) for c in fit.CASES}
    assert res["BEST"]["required"] < res["CURRENT"]["required"]


def test_fit_passes_when_envelope_is_long_enough():
    """A synthetic long envelope must pass; proves the comparison direction."""
    st = {"NACELLE_L": 300.0, "EDF1_Z_ENTRY": 27.5, "NOZZLE_RING_Z": 250.0}
    assert fit.evaluate(fit.CASES[1], st)["verdict"] == "PASS"


def test_gate_exit_code_matches_best_case():
    """Exit 2 exactly when the BEST case fails (R11 stop)."""
    best = fit.evaluate(fit.CASES[1], fit.stations())
    assert fit.main([]) == (0 if best["verdict"] == "PASS" else 2)


def test_missing_parameter_fails_loudly():
    """An expression or missing station raises instead of being misread."""
    with pytest.raises(ValueError):
        fit.scad_param("NACELLE_L = A + B;", "NACELLE_L")
