"""Tests for tools/sync_operators_manual.py (WBS 0.10.3, OM-5).

Author: Claude Sonnet 5.5 (Anthropic) for S. Griffing, 2026-11-02.
License: MIT (SPDX-License-Identifier: MIT)
"""
import json
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import sync_operators_manual as som  # noqa: E402


class SyncOperatorsManualTest(unittest.TestCase):
    def setUp(self) -> None:
        self.lim = json.loads(som.LIMITS.read_text())
        self.vals = som.compute(self.lim, som._load_endurance())

    def test_owner_corrections_are_in_the_limits_file(self) -> None:
        # Happy path: the 2026-11-02 owner corrections.
        self.assertEqual(self.lim["tilt"]["min_deg"], -5.0)
        self.assertEqual(self.lim["tilt"]["max_deg"], 135.0)
        self.assertEqual(self.lim["fan"]["thrust_gf"], 2370.0)
        self.assertEqual(self.lim["fan"]["esc_a"], 80)
        self.assertAlmostEqual(self.lim["fan"]["thrust_ozf"], 83.60, places=2)

    def test_derived_values(self) -> None:
        # Happy path: T/W 9480/6318 and the critical angle asin(1/T/W).
        self.assertEqual(self.vals["tw_pl"], "1.50")
        self.assertEqual(self.vals["theta_pl"], "41.8")
        self.assertEqual(self.vals["tilt_span"], "140")

    def test_render_is_idempotent(self) -> None:
        # Edge: rendering already-current text changes nothing and reports no problems.
        text = som.MANUAL.read_text()
        once, problems = som.render(text, self.vals, som.blocks(self.vals))
        twice, _ = som.render(once, self.vals, som.blocks(self.vals))
        self.assertEqual(problems, [])
        self.assertEqual(once, twice)

    def test_unknown_marker_is_reported(self) -> None:
        # Error path: a typo'd inline key must not be silently dropped.
        _, problems = som.render("x <!--V:no_such_key-->1<!--/V-->", self.vals, som.blocks(self.vals))
        self.assertEqual(len(problems), 1)

    def test_sources_agree(self) -> None:
        # Integration: the drift gate passes on the committed tree.
        errs, _ = som.verify(self.lim)
        self.assertEqual(errs, [])


if __name__ == "__main__":
    unittest.main()
