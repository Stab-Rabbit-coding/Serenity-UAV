#!/usr/bin/env python3
"""finish_tacco_pcb.py — Route TACCO with freerouting through KiCad's Specctra bridge,
then add the outer GND pours and the QFN thermal vias, refill every zone and save.

Usage:
    python3 finish_tacco_pcb.py export  <board.kicad_pcb> <out.dsn> [--band-keepout]
    python3 finish_tacco_pcb.py import  <board.kicad_pcb> <routed.ses>
    python3 finish_tacco_pcb.py finish  <board.kicad_pcb>

Phases (avionics/WBS.md §1.2a "TACCO area recovery", U5):

1. ``export --band-keepout`` writes a DSN in which the CAN-FD / RS-485 isolation band
   (the ``ISO_BAND`` rule area) is a hard track/via keepout on every copper layer.
   Freerouting knows nothing about this board's ``.kicad_dru`` isolation rules, so
   phase 1 routes every logic net with the band closed; the ISOLATION-class nets
   inside the band are left unrouted on purpose.
2. ``import`` brings the phase-1 session back.  ``export`` (no keepout) then writes a
   second DSN: the routed wires are carried into it, and freerouting finishes the
   ISOLATION nets, whose pads all sit inside the band.
3. ``finish`` adds a top and bottom GND pour (freerouting treats a filled zone as
   fixed copper, which is why the generator leaves F.Cu/B.Cu pour-free until now),
   drops a 3 x 3 grid of 0.3 mm thermal vias under the STM32WLE5JC exposed pad (the
   library ``_ThermalVias`` land uses 0.2 mm drills, below this board's 0.3 mm
   minimum), refills all zones and saves.  ``kicad-cli pcb drc --severity-all
   --schematic-parity`` is the gate that follows.

Same discipline as Pilot's ``finish_pilot_pcb.py``: an autorouted result is accepted
only if the DRC gate passes; shorts or isolation-rule violations are fixed or the
result is rejected.

Author: Claude Fable 5.1, 2026-09-29.  Owner: sgriffing.  License: CC BY 4.0.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pcbnew  # type: ignore


def mm(v: float) -> int:
    return int(round(v * 1e6))


def board_edge(board: pcbnew.BOARD):
    edge = board.GetBoardEdgesBoundingBox()
    x1, y1 = edge.GetX() / 1e6, edge.GetY() / 1e6
    return x1, y1, x1 + edge.GetWidth() / 1e6, y1 + edge.GetHeight() / 1e6


def add_band_keepouts(board: pcbnew.BOARD) -> int:
    """Copy the ISO_BAND rule area into a hard keepout per copper layer (phase 1)."""
    band = next((z for z in board.Zones() if z.GetIsRuleArea() and z.GetZoneName() == "ISO_BAND"), None)
    if band is None:
        raise SystemExit("ISO_BAND rule area not found")
    n = 0
    for layer in board.GetEnabledLayers().CuStack():
        z = pcbnew.ZONE(board)
        z.SetLayer(layer)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowTracks(True)
        z.SetDoNotAllowVias(True)
        z.SetDoNotAllowCopperPour(False)
        z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
        z.SetZoneName("TMP_BAND_KEEPOUT")
        ol = z.Outline()
        ol.NewOutline()
        src = band.Outline().Outline(0)
        for i in range(src.PointCount()):
            p = src.CPoint(i)
            ol.Append(p.x, p.y)
        board.Add(z)
        n += 1
    return n


def add_outer_gnd_pours(board: pcbnew.BOARD) -> None:
    gnd = board.FindNet("GND")
    if gnd is None:
        raise SystemExit("net GND not found on board")
    x1, y1, x2, y2 = board_edge(board)
    pts = [(x1 + 0.5, y1 + 0.5), (x2 - 0.5, y1 + 0.5), (x2 - 0.5, y2 - 0.5), (x1 + 0.5, y2 - 0.5)]
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


def add_qfn_thermal_vias(board: pcbnew.BOARD, ref: str = "MLRS-MCU", pitch: float = 1.4, n: int = 3) -> int:
    fp = board.FindFootprintByReference(ref)
    if fp is None:
        raise SystemExit(f"{ref} not found")
    gnd = board.FindNet("GND")
    c = fp.GetPosition()
    added = 0
    for i in range(n):
        for j in range(n):
            v = pcbnew.PCB_VIA(board)
            v.SetPosition(pcbnew.VECTOR2I(c.x + mm((i - (n - 1) / 2) * pitch), c.y + mm((j - (n - 1) / 2) * pitch)))
            v.SetViaType(pcbnew.VIATYPE_THROUGH)
            v.SetDrill(mm(0.3))
            v.SetWidth(mm(0.5))
            v.SetNet(gnd)
            board.Add(v)
            added += 1
    return added


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, pcb_path = sys.argv[1], sys.argv[2]
    board = pcbnew.LoadBoard(pcb_path)
    if cmd == "export":
        dsn = sys.argv[3]
        if "--band-keepout" in sys.argv:
            print("band keepouts added:", add_band_keepouts(board))
        ok = pcbnew.ExportSpecctraDSN(board, dsn)
        print("exported", dsn, ok)
        return
    if cmd == "import":
        ses = sys.argv[3]
        if not pcbnew.ImportSpecctraSES(board, ses):
            sys.exit("ImportSpecctraSES failed")
        for z in list(board.Zones()):
            if z.GetZoneName() == "TMP_BAND_KEEPOUT":
                board.Remove(z)
        pcbnew.SaveBoard(pcb_path, board)
        n_vias = sum(1 for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T)
        print(f"imported {ses}: {len(board.GetTracks()) - n_vias} segments, {n_vias} vias; saved {pcb_path}")
        return
    if cmd == "finish":
        add_outer_gnd_pours(board)
        print("thermal vias:", add_qfn_thermal_vias(board))
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(board.Zones())
        pcbnew.SaveBoard(pcb_path, board)
        print("pours added, zones filled, saved", pcb_path)
        return
    sys.exit(f"unknown command {cmd}")


if __name__ == "__main__":
    main()
