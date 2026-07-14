#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mod_vera_trapezoid.py -- redraw Vera.kicad_pcb Edge.Cuts as the nose-carrier
trapezoid derived in docs/VERA_NOSE_TRAPEZOID.md (Rev B).
=============================================================================
Board frame: +X fore->aft, +Y starboard->port.  The forward/sensor (narrow) end is
at high board-X; the aft (wide) end at low board-X.  From the airframe SCAD +
measured head-STL nose width:
  * narrow (fwd/sensor) end = 25.4 mm (set by the 26.4 mm bow flat + aperture span)
  * wide (aft) end          = 58.0 mm (fits the ~58 mm usable nose interior; holds
                                        the 40x40 SoM at the aft end -- see doc 4.1)
  * length                  = 69.85 mm (unchanged)
Symmetric about the board Y-centreline (~aircraft CL, where the CL laser land sits).

This is a CANDIDATE straight trapezoid; the doc notes a fast-widening / two-segment
edge (nose-following) is the refinement, and the exact inner-wall follow wants a
FreeCAD trace on the tilted board plane.  Modifies the board in place (GUI-owned).

Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  (Griffing Technology LLC)
AI-assist: Claude Opus 4.8 (Anthropic) -- pcbnew transform, 2026-07-12.
License: CC BY 4.0
"""

import sys
from pathlib import Path

import pcbnew

BOARD = Path(__file__).resolve().parent / "Vera.kicad_pcb"

NARROW_X = 69.85   # forward/sensor edge (high X)
WIDE_X = 0.0       # aft edge (low X)
Y_C = 12.7         # board Y centreline
NARROW_W = 25.4
WIDE_W = 58.0

# trapezoid corners (mm), CCW
CORNERS = [
    (NARROW_X, Y_C - NARROW_W / 2),   # fwd starboard
    (NARROW_X, Y_C + NARROW_W / 2),   # fwd port
    (WIDE_X, Y_C + WIDE_W / 2),       # aft port
    (WIDE_X, Y_C - WIDE_W / 2),       # aft starboard
]


def mm(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


def main():
    board = pcbnew.LoadBoard(str(BOARD))
    edge = board.GetLayerID("Edge.Cuts")
    # remove existing Edge.Cuts graphics
    removed = 0
    for d in list(board.GetDrawings()):
        if d.GetLayer() == edge:
            board.Remove(d)
            removed += 1
    print(f"  removed {removed} old Edge.Cuts shapes")
    # draw the trapezoid (4 segments)
    for i in range(4):
        x1, y1 = CORNERS[i]
        x2, y2 = CORNERS[(i + 1) % 4]
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(mm(x1, y1))
        seg.SetEnd(mm(x2, y2))
        seg.SetLayer(edge)
        seg.SetWidth(pcbnew.FromMM(0.1))
        board.Add(seg)
    print(f"  drew trapezoid narrow={NARROW_W}mm (X={NARROW_X}) -> "
          f"wide={WIDE_W}mm (X={WIDE_X}), len={NARROW_X - WIDE_X}mm")
    pcbnew.SaveBoard(str(BOARD), board)
    print("saved", BOARD.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
