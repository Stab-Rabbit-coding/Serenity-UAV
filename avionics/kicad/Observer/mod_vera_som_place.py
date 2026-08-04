#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mod_vera_som_place.py -- place the phyCORE-AM62x PCM-071 SoM (placement footprint)
on Vera.kicad_pcb for the initial two-sided fit against the nose trapezoid.
=============================================================================
Adds U_SOM (Vera:phyCORE-AM62x_PCM071_placement, 32x43mm) at the AFT/WIDE end of
the trapezoid, rotated 90 deg so the module's 43 mm length runs along the board
fore-aft (X) axis and its 32 mm width along port-starboard (Y).  Verified fit: at
the SoM forward edge (board X~45.5) the trapezoid is ~36.8 mm wide vs the 32 mm the
module needs; the aft end is ~57 mm.  Board loads; invalid_outline = 0.

The old raw-SoC placeholders (U1 AM62A7, U_PMIC, ...) are NOT removed here -- their
overlap DRC is expected and clears in the full connector-variant re-layout (drop the
raw-SoC parts, add the real BTH-060 land + carrier ICs, wire per the net map).
Idempotent: repositions U_SOM if already present.

Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  (Griffing Technology LLC)
AI-assist: Claude Opus 4.8 (Anthropic) -- pcbnew transform, 2026-07-12.
License: CC BY 4.0
"""

import sys
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
BOARD = HERE / "Vera.kicad_pcb"
PRETTY = str(HERE / "Vera.pretty")
POS = (24.0, 12.7)  # aft/wide end, board centreline
ROT = 90


def main():
    board = pcbnew.LoadBoard(str(BOARD))
    existing = {f.GetReference(): f for f in board.GetFootprints()}
    if "U_SOM" in existing:
        fp = existing["U_SOM"]
        print("repositioned U_SOM")
    else:
        fp = pcbnew.FootprintLoad(PRETTY, "phyCORE-AM62x_PCM071_placement")
        if fp is None:
            print("ERROR: could not load placement footprint")
            return 1
        fp.SetReference("U_SOM")
        board.Add(fp)
        print("placed U_SOM (phyCORE-AM62x PCM-071, 32x43)")
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(POS[0]), pcbnew.FromMM(POS[1])))
    fp.SetOrientationDegrees(ROT)
    pcbnew.SaveBoard(str(BOARD), board)
    print(f"saved {BOARD.name} (U_SOM at {POS} rot{ROT})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
