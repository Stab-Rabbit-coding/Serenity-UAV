"""Tests for tools/joint_register.py (plan 2026-11-02-001 U1).

Author: Claude Sonnet 5.5 (Anthropic) for S. Griffing, 2026-11-02.
License: MIT (SPDX-License-Identifier: MIT)
"""

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import joint_register as jr  # noqa: E402


class JointRegisterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.reg, self.bom = jr.load()

    def test_committed_register_is_clean(self) -> None:
        # Happy path: structure valid and every in-scope BOM row accounted for.
        self.assertEqual(jr.validate(self.reg, self.bom), [])

    def test_every_hardware_fastener_maps_to_a_joint(self) -> None:
        # Happy path: the M3 inserts, ESC-cover screws and studs are in joints.
        claimed = {r for j in self.reg["joints"] for r in j["bom_refs"]}
        for ref in ("INSERT-M3-WING", "SCREW-M3-BUTTON-8", "STUD-M3-BRASS", "HALL-SCR-M2-BRASS"):
            self.assertIn(ref, claimed)

    def test_joint_with_two_fastener_types_lists_both(self) -> None:
        # Edge case: the disconnect joint carries a stud and an insert.
        j = next(x for x in self.reg["joints"] if x["id"] == "J-NAC-ESC-DISCONNECT")
        self.assertEqual(len(j["fasteners"]), 2)

    def test_orphaned_bom_fastener_fails(self) -> None:
        # Error path / integration: a new BOM fastener with no joint is caught.
        bom = copy.deepcopy(self.bom)
        bom["SCREW-NEW-M4"] = {"Ref": "SCREW-NEW-M4", "Category": "Fastener", "Description": "x"}
        errs = jr.validate(self.reg, bom)
        self.assertTrue(any("SCREW-NEW-M4" in e for e in errs))

    def test_duplicate_id_and_bad_class_fail(self) -> None:
        # Error path.
        reg = copy.deepcopy(self.reg)
        reg["joints"].append(copy.deepcopy(reg["joints"][0]))
        reg["joints"][1]["joint_class"] = "glued"
        errs = jr.validate(reg, self.bom)
        self.assertTrue(any("duplicate" in e for e in errs))
        self.assertTrue(any("glued" in e for e in errs))

    def test_unknowns_block_threaded_joints(self) -> None:
        # R3: a threaded joint with an unknown field is reported as blocked.
        self.assertIn("J-WING-ROOT-INSERT", {j["id"] for j in jr.blocked(self.reg)})


if __name__ == "__main__":
    unittest.main()
