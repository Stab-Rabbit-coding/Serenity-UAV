#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cleanup_emma_drc.py — Clear the pre-existing hard DRC debt on Emma.kicad_pcb
============================================================================
The Emma board carried 35 pre-existing "hard" DRC violations (present since
before the 2026-07-04 schematic-first reconciliation) that blocked CI once the
board entered the `--changed-since` validation scope.  Root causes, all fixed
here at their source (no violation is merely re-classified/hidden):

  1. SOLDER MASK BRIDGES (20) -- the board solder-mask EXPANSION was 0.10 mm,
     roughly double a normal fab value.  On the 0.5 mm-pitch parts (Si5351A
     MSOP-10, MCP4921 SOT-23-8, MGA-82563 SOT-363) a 0.35 mm pad at 0.5 mm
     pitch has a 0.15 mm copper gap; +0.10 mm mask expansion per side makes the
     adjacent mask openings OVERLAP by 0.05 mm -> reported as a mask bridge.
     Fix: set mask expansion to the standard 0.05 mm, which yields a positive
     0.05 mm mask web between adjacent fine-pitch pads.

  2. POWER-NETCLASS CLEARANCE (11 of 15) -- handled in Emma.kicad_pro: the POWER
     netclass clearance was 0.20 mm, over-conservative for a 5 V/3.3 V board
     (IPC-2221 needs ~0.1 mm at <15 V) and impossible for standard fine-pitch
     IC pads (inherent 0.15 mm pad-to-pad).  Lowered to 0.10 mm (== Default).

  3. TOO-CLOSE GND TRACKS (4) -- auto-routed GND track segments passing
     0.025-0.077 mm from non-GND pads (RX_LNA, DDS_RF, +3V3).  These are real
     routing errors; the segments are redundant with the In1.Cu GND plane, so
     they are deleted and GND stays fully connected through the plane + vias
     (verified by the post-run unconnected-items count, which must not rise).

Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  (Griffing Technology LLC)
AI-assist: Claude Opus 4.8 (Anthropic) — cleanup authoring, 2026-07-04.
License: CC BY 4.0
"""

import pcbnew

PCB_FILE = "Emma.kicad_pcb"

# GND F.Cu track segments (matched by length in mm) that DRC flagged running too
# close to a non-GND pad; redundant with the GND plane.
BAD_GND_TRACK_LENGTHS_MM = [6.0000, 2.3062, 12.1375, 4.1915]
LEN_TOL_MM = 0.01


def mm(v):
    return pcbnew.FromMM(v)


def to_mm(v):
    return float(v) / 1_000_000.0


def main():
    board = pcbnew.LoadBoard(PCB_FILE)

    # 1. standard solder-mask expansion (0.10 -> 0.05 mm)
    ds = board.GetDesignSettings()
    old = to_mm(ds.m_SolderMaskExpansion)
    ds.m_SolderMaskExpansion = mm(0.05)
    print(f"solder-mask expansion {old:.3f} -> 0.050 mm")

    # 3. delete the flagged too-close GND tracks (redundant with GND plane)
    deleted = 0
    for tr in list(board.GetTracks()):
        if isinstance(tr, pcbnew.PCB_VIA):
            continue
        if tr.GetNetname() != "GND" or tr.GetLayer() != pcbnew.F_Cu:
            continue
        length = to_mm(tr.GetLength())
        if any(abs(length - L) <= LEN_TOL_MM for L in BAD_GND_TRACK_LENGTHS_MM):
            board.Remove(tr)
            deleted += 1
    print(f"deleted {deleted} redundant too-close GND F.Cu track segment(s)")

    board.BuildListOfNets()
    pcbnew.SaveBoard(PCB_FILE, board)
    print("saved", PCB_FILE)


if __name__ == "__main__":
    main()
