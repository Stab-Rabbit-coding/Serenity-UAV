#!/usr/bin/env python3
"""finish_pilot_pcb.py — Import a freerouting session, fill outer-layer GND
pours, and leave the board ready for the DRC gate and gerber export.

Usage: python3 finish_pilot_pcb.py <board.kicad_pcb> <routed.ses>

Adds a top/bottom GND pour (net "GND", priority 0, matching the inner GND
plane) after routing — freerouting only produces tracks/vias, and treats any
pre-existing filled zone as fixed copper it must route around, which is why
gen_pilot_pcb.py deliberately left F.Cu/B.Cu pour-free for the router.  Then
re-fills every zone (including the isolated GND2 islands and the In2..In4
signal/plane layers) and saves in place.

Author: Claude Sonnet 5, 2026-09-19.  Owner: sgriffing.  License: CC BY 4.0.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pcbnew  # type: ignore


def mm(v: float) -> int:
    return int(round(v * 1e6))


def add_outer_gnd_pours(board: pcbnew.BOARD) -> None:
    gnd = board.FindNet("GND")
    if gnd is None:
        raise SystemExit("net GND not found on board")
    edge = board.GetBoardEdgesBoundingBox()
    x1, y1 = edge.GetX() / 1e6 + 0.5, edge.GetY() / 1e6 + 0.5
    x2 = (edge.GetX() + edge.GetWidth()) / 1e6 - 0.5
    y2 = (edge.GetY() + edge.GetHeight()) / 1e6 - 0.5
    pts = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
    for layer, name in ((pcbnew.F_Cu, "GND pour (top)"), (pcbnew.B_Cu, "GND pour (bottom)")):
        z = pcbnew.ZONE(board)
        z.SetLayer(layer)
        z.SetNet(gnd)
        z.SetZoneName(name)
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetLocalClearance(mm(0.25))
        z.SetMinThickness(mm(0.15))
        z.SetThermalReliefGap(mm(0.3))
        z.SetThermalReliefSpokeWidth(mm(0.3))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        ol = z.Outline()
        ol.NewOutline()
        for x, y in pts:
            ol.Append(mm(x), mm(y))
        board.Add(z)


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("Usage: finish_pilot_pcb.py <board.kicad_pcb> <routed.ses>")
    pcb_path, ses_path = sys.argv[1], sys.argv[2]

    board = pcbnew.LoadBoard(pcb_path)
    ok = pcbnew.ImportSpecctraSES(board, ses_path)
    if not ok:
        sys.exit("ImportSpecctraSES failed")

    add_outer_gnd_pours(board)

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    pcbnew.SaveBoard(pcb_path, board)
    n_vias = sum(1 for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T)
    n_tracks = sum(1 for t in board.GetTracks()) - n_vias
    print(f"imported {ses_path}: {n_tracks} track segments, {n_vias} vias; zones filled; saved {pcb_path}")


if __name__ == "__main__":
    main()
