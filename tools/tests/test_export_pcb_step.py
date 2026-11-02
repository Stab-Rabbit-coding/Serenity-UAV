"""Tests for tools/export_pcb_step.py (plan 2026-11-02-001 U12).

Author: Claude Sonnet 5.5 (Anthropic) for S. Griffing, 2026-11-02.
License: MIT (SPDX-License-Identifier: MIT)
"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import export_pcb_step as ex  # noqa: E402


class ExportPcbStepTest(unittest.TestCase):
    def test_parse_version(self) -> None:
        # Happy path and edge: patch level ignored.
        self.assertEqual(ex.parse_version("9.0.2"), (9, 0))
        self.assertEqual(ex.parse_version("9.0"), (9, 0))
        with self.assertRaises(ValueError):
            ex.parse_version("none")

    def test_newer_board_is_refused(self) -> None:
        # Error path: a board saved by a newer KiCad than kicad-cli is refused.
        d = Path(tempfile.mkdtemp())
        try:
            pcb = d / "x.kicad_pcb"
            pcb.write_text('(kicad_pcb (version 20250101) (generator "pcbnew") (generator_version "10.0")\n)')
            self.assertIn("10.0", ex.check_version(pcb, (9, 0)))
            self.assertIsNone(ex.check_version(pcb, (10, 0)))
        finally:
            shutil.rmtree(d)

    def test_every_board_is_discovered(self) -> None:
        # Integration: the first-flight boards are found.
        names = {p.parent.parent.name for p in ex.boards()}
        for n in ("Pilot", "TACCO", "FlightEngineer"):
            self.assertIn(n, names)


if __name__ == "__main__":
    unittest.main()
