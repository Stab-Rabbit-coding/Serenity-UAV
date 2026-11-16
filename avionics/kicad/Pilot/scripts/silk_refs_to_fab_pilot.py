#!/usr/bin/env python3
"""silk_refs_to_fab_pilot.py — Move footprint reference designators from silkscreen to Fab.

Usage:
    python3 silk_refs_to_fab_pilot.py <board.kicad_pcb>

The 55 x 35 mm Pilot cape carries 136 parts on two sides; after the 2026-10-19
re-floorplan 252 of its 263 DRC silkscreen warnings were reference designators
overlapping each other, footprint outlines or pads.  Dense boards customarily carry
the designators on the Fab layers instead, and the assembler works from the
position (centroid) file plus a Fab-layer assembly drawing, which
export_pilot_gerbers.sh produces.  This script rewrites, in each footprint, the
``(property "Reference" ...)`` field's layer: F.SilkS -> F.Fab, B.SilkS -> B.Fab.
Polarity marks and outlines stay on silkscreen.

It edits the S-expression text only (the KiCad 9.0.2 pcbnew binding is unreliable for
edits, avionics/kicad/PCBNEW_SWIG_BUG.md) and reports how many fields it moved.

Author: Claude Opus 5.5, 2026-10-19.  Owner: sgriffing.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# a footprint's Reference property up to its layer token; KiCad 9 writes the property
# over several lines ((at ...) then (layer ...)), so the gap may span newlines but not
# another "(property" or "(effects" block
REF_LAYER = re.compile(r'(\(property "Reference" "[^"]*"(?:(?!\(property|\(effects).)*?'
                       r'\(layer ")([FB])\.SilkS(")', re.S)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    pcb = Path(sys.argv[1])
    text = pcb.read_text()
    new, n = REF_LAYER.subn(lambda m: f"{m.group(1)}{m.group(2)}.Fab{m.group(3)}", text)
    if n:
        pcb.write_text(new)
    print(f"reference fields moved to Fab: {n}")


if __name__ == "__main__":
    main()
