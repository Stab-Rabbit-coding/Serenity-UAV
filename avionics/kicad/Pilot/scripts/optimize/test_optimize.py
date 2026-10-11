#!/usr/bin/env python3
"""test_optimize.py — Regression tests for the Pilot placement-optimisation tooling.

Run:  python3 -m unittest -v test_optimize      (from this directory)

Covers the geometry helpers and text transforms that gate keep/revert decisions
(code-review finding #7, 2026-10-10):

* rot_offsets            — 0/90/180/270 deg in KiCad's y-down frame
* in_poly                — the concave notched ISO_BAND outline, inside/outside/notch
* rotate_children        — pad/text angles move with the footprint (finding #1)
* apply_moves vs pcbnew  — text rotation + side flip match FOOTPRINT::SetOrientation /
                           Flip on the committed board (skipped if pcbnew is absent)
* strip_routing          — removes segment/arc/via blocks and nothing else
* band_outline           — an outline that cannot be applied raises (finding #4)
* capfit                 — supply + loop metric on a synthetic two-part layout

pytest is not installed on this workstation, so plain unittest is used.

Author: Claude Opus 5.5, 2026-10-10.  Owner: sgriffing.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from eval_placement import BOARD, apply_moves, capfit, in_poly, rotate_children, strip_routing
from search_caps import rot_offsets

NOTCHED_BAND = [(128.3, 111.0), (137.6, 111.0), (137.6, 105.5),
                (155.9, 105.5), (155.9, 122.0), (128.3, 122.0)]


class GeometryHelpers(unittest.TestCase):
    """Pure-Python geometry used by the search and the harness."""

    def test_rot_offsets_quarter_turns(self) -> None:
        # KiCad y-down: +90 deg takes +x to -y
        self.assertEqual(rot_offsets([(1.0, 0.0)], 0), [(1.0, 0.0)])
        self.assertEqual(rot_offsets([(1.0, 0.0)], 90), [(0.0, -1.0)])
        self.assertEqual(rot_offsets([(1.0, 0.0)], 180), [(-1.0, 0.0)])
        self.assertEqual(rot_offsets([(1.0, 0.0)], 270), [(0.0, 1.0)])

    def test_in_poly_concave_band(self) -> None:
        self.assertTrue(in_poly(150.0, 110.0, NOTCHED_BAND))    # main band body
        self.assertTrue(in_poly(130.0, 115.0, NOTCHED_BAND))    # below the notch
        self.assertFalse(in_poly(130.0, 108.0, NOTCHED_BAND))   # inside the GPS notch
        self.assertFalse(in_poly(120.0, 115.0, NOTCHED_BAND))   # west of the band

    def test_rotate_children_adds_delta(self) -> None:
        blk = "\t\t\t(at 0.5 0)\n\t\t\t(at -0.5 0 90)\n\t\t(at 1 2)\n"
        out = rotate_children(blk, 90)
        self.assertIn("\t\t\t(at 0.5 0 90)\n", out)
        self.assertIn("\t\t\t(at -0.5 0 180)\n", out)
        self.assertIn("\t\t(at 1 2)\n", out)  # footprint-level line untouched
        self.assertIn("\t\t\t(at -0.5 0)\n", rotate_children(blk, -90).replace(" 0 90)", ""))


class TextTransforms(unittest.TestCase):
    """S-expression edits on the committed board."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = BOARD.read_text()

    def test_strip_routing_removes_only_routing(self) -> None:
        out = strip_routing(self.text)
        self.assertNotRegex(out, r"(?m)^\t\((segment|arc|via)\b")
        self.assertEqual(out.count("\n\t(footprint "), self.text.count("\n\t(footprint "))
        self.assertEqual(out.count("\n\t(zone"), self.text.count("\n\t(zone"))

    def test_band_outline_noop_raises(self) -> None:
        broken = self.text.replace('(name "ISO_BAND")', '(name "NOT_THE_BAND")')
        with self.assertRaises(SystemExit):
            apply_moves(broken, {"moves": {}, "band_outline": NOTCHED_BAND})

    def test_flip_refuses_multi_pad_parts(self) -> None:
        with self.assertRaises(SystemExit):
            apply_moves(self.text, {"moves": {"TPM": {"side": "B"}}})

    @unittest.skipUnless(subprocess.run([sys.executable, "-c", "import pcbnew"],
                                        capture_output=True).returncode == 0, "pcbnew absent")
    def test_apply_moves_matches_pcbnew(self) -> None:
        cases = {"C-SS": (0, False), "C-IN2": (0, False),
                 "C-485-1": (90, True), "BARO": (90, False)}
        moves = {r: {"rot": rot, **({"side": "F"} if flip else {})}
                 for r, (rot, flip) in cases.items()}
        work = Path(tempfile.mkdtemp(prefix="pilot-test-"))
        (work / "t.kicad_pcb").write_text(apply_moves(self.text, {"moves": moves}))
        code = f"""
import json, pcbnew
def pads(b, ref):
    return sorted([p.GetNumber(), round(p.GetPosition().x / 1e6, 3),
                   round(p.GetPosition().y / 1e6, 3), round(p.GetOrientationDegrees() % 360, 1)]
                  for p in b.GetPads()
                  if p.GetParentFootprint().GetReference() == ref and p.GetNumber())
t = pcbnew.LoadBoard({str(work / "t.kicad_pcb")!r}); o = pcbnew.LoadBoard({str(BOARD)!r})
res = {{}}
for ref, (rot, flip) in {cases!r}.items():
    f = o.FindFootprintByReference(ref)
    if flip:
        f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
    f.SetOrientationDegrees(rot)
    res[ref] = [pads(t, ref), pads(o, ref)]
print(json.dumps(res))
"""
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
        for ref, (text_pads, pcb_pads) in json.loads(r.stdout.strip().splitlines()[-1]).items():
            for a, b in zip(text_pads, pcb_pads):
                self.assertEqual(a[0], b[0], ref)
                self.assertAlmostEqual(a[1], b[1], delta=0.002, msg=ref)
                self.assertAlmostEqual(a[2], b[2], delta=0.002, msg=ref)
                self.assertAlmostEqual((a[3] - b[3] + 180) % 360 - 180, 0, delta=0.05, msg=ref)


class CapFit(unittest.TestCase):
    """Supply and loop metric on a synthetic layout."""

    def test_supply_and_loop(self) -> None:
        g = {"pads": [
            {"ref": "TPM", "num": "1", "net": "+3V3", "x": 0.0, "y": 0.0},
            {"ref": "TPM", "num": "2", "net": "GND", "x": 0.0, "y": 1.0},
            {"ref": "C-TPM1", "num": "1", "net": "+3V3", "x": 3.0, "y": 0.0},
            {"ref": "C-TPM1", "num": "2", "net": "GND", "x": 3.0, "y": 1.0},
            {"ref": "C-TPM2", "num": "1", "net": "UNRELATED", "x": 1.0, "y": 0.0},
            {"ref": "C-TPM2", "num": "2", "net": "GND", "x": 1.0, "y": 1.0},
        ]}
        loops: dict = {}
        d = capfit(g, loops)
        self.assertAlmostEqual(d["C-TPM1"], 3.0)
        self.assertAlmostEqual(loops["C-TPM1"], 6.0)   # supply 3 + ground return 3
        self.assertNotIn("C-TPM2", d)                  # no shared supply net -> not scored


if __name__ == "__main__":
    unittest.main()
