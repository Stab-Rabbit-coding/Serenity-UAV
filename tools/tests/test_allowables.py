"""Tests for tools/allowables.py (plan 2026-11-02-001 U3).

Author: Claude Sonnet 5.5 (Anthropic) for S. Griffing, 2026-11-02.
License: MIT (SPDX-License-Identifier: MIT)
"""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import allowables as al  # noqa: E402


class AllowablesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.db = al.load()
        self.sf = json.loads(al.SF.read_text())

    def test_committed_data_is_valid(self) -> None:
        self.assertEqual(al.validate(self.db, self.sf), [])

    def test_selector_prefers_printable_composite_with_a_cited_value(self) -> None:
        # Happy path: tensile exists for PETG-CF20 and aluminum -> composite wins.
        m, rec = al.select(self.db, ["AL-6061-T6", "PETG-CF20"], "tensile_strength")
        self.assertEqual(m, "PETG-CF20")
        self.assertEqual(rec["source"]["ref"], "REF-MAT-001")

    def test_selector_falls_through_when_the_preferred_has_no_cited_value(self) -> None:
        # Edge: no composite has a cited shear value -> aluminum is chosen.
        m, _ = al.select(self.db, ["PETG-CF20", "AL-6061-T6"], "shear_strength")
        self.assertEqual(m, "AL-6061-T6")

    def test_pa_cf_z_axis_is_not_defaulted(self) -> None:
        # Edge / R3: the open Z allowable raises and names what would establish it.
        with self.assertRaises(al.Unknown) as ctx:
            al.get(self.db, "SLS-PA-CF", "interlayer_tensile_z")
        self.assertIn("3D Systems", str(ctx.exception))

    def test_value_without_source_fails_validation(self) -> None:
        # Error path.
        db = copy.deepcopy(self.db)
        db["materials"]["PETG"]["props"]["tensile_strength"]["source"] = {}
        self.assertTrue(al.validate(db, self.sf))

    def test_fos_default_and_override_rule(self) -> None:
        # Happy path: 1.5 default. Integration: only a VERIFIED, larger override raises it.
        # The owner's 1.5 stands; the NASA fitting factor is not stacked on it.
        self.assertEqual(al.fastener_fos(self.sf), 1.5)
        sf = copy.deepcopy(self.sf)
        sf["overrides"] = [{"ref": "REF-X", "value": 2.0, "verified": False}]
        self.assertEqual(al.fastener_fos(sf), 1.5)
        sf["overrides"][0]["verified"] = True
        self.assertEqual(al.fastener_fos(sf), 2.0)


    def test_nasa_equivalent_is_independent_of_the_owner_factor(self) -> None:
        # Independent comparison: NASA total = its own program factor x 1.15, whatever 1.5 is.
        self.assertEqual(al.nasa_equivalent_fos(1.4, self.sf), 1.61)
        sf = copy.deepcopy(self.sf)
        sf["fastener_default"] = 2.0
        self.assertEqual(al.nasa_equivalent_fos(1.4, sf), 1.61)


if __name__ == "__main__":
    unittest.main()
