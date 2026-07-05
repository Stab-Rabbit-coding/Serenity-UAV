#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route_emma_rssi.py — Route the RSSI carrier-detect sub-circuit on Emma.kicad_pcb.
================================================================================
The 4 RSSI parts (RSSI_CMP + RSSI_RH/RL/CBY divider/bypass) were placed by the
user on B.Cu in the RF section (2026-07-05). This routes their nets:

  GND     : via at each RSSI GND pad down to the F.Cu GND pour (the plane ties them)
  RSSI_REF: B.Cu trace among RH.2 / RL.1 / RSSI_CMP.3 (routed down the mid-column
            between the divider's L/R pads to clear the GND/+3V3 pads)
  +3V3    : B.Cu trace among RH.1 / CBY.1 / RSSI_CMP.2, jogging around RL.1(REF)
  RSSI_ANA: B.Cu east from RSSI_CMP.1, via to F.Cu, to the RSSI Hi/Lo divider
  RSSI_DCD: RSSI_CMP.5 toward PB2-P2 pad 2 (attempted; long cross-board run)

Every segment is added then the caller runs `kicad-cli pcb drc`; routes were tuned
against DRC (paths pruned/weaved until 0 hard). Traces 0.15 mm; vias 0.30 mm drill
/ 0.55 mm. Zones are refilled on save. Uses pcbnew layer CONSTANTS (F_Cu/B_Cu) so
it is immune to the file's internal layer numbering. `all` routes everything that
lands DRC-clean (GND/REF/+3V3/+3V3-link/RSSI_ANA); RSSI_DCD is left for the GUI.

Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  (Griffing Technology LLC)
AI-assist: Claude Opus 4.8 (Anthropic) — routing authoring, 2026-07-05.
License: CC BY 4.0
"""

import sys

import pcbnew

PCB = "Emma.kicad_pcb"


def mm(v):
    return pcbnew.FromMM(v)


def net(board, name):
    n = board.FindNet(name)
    if n is None:
        raise RuntimeError("missing net " + name)
    return n


def track(board, netname, layer, pts, w=0.20):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(board)
        t.SetLayer(layer)
        t.SetNet(net(board, netname))
        t.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        t.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
        t.SetWidth(mm(w))
        board.Add(t)


def via(board, netname, x, y, drill=0.30, size=0.55):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    v.SetDrill(mm(drill))
    for lyr in (pcbnew.F_Cu, pcbnew.B_Cu):
        v.SetWidth(lyr, mm(size))
    v.SetNet(net(board, netname))
    board.Add(v)


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    board = pcbnew.LoadBoard(PCB)
    B = pcbnew.B_Cu
    F = pcbnew.F_Cu

    if which in ("gnd", "all"):
        # Tie the 3 RSSI GND pads on B.Cu (0.15 mm), one small via to the F.Cu
        # GND pour at the clear spot (RL.2). A via at CMP.4 would clip L1's F.Cu
        # RF_TX pad, so the pour is reached only at RL.2.
        track(
            board,
            "GND",
            B,
            [(131.50, 114.00), (131.53, 116.00), (131.55, 118.91)],
            w=0.15,
        )
        via(board, "GND", 131.50, 114.00)

    if which in ("ref", "all"):
        # REF threads the 0.5 mm mid-channel (x=132.0) between the GND left
        # column (131.5) and the +3V3 right column (132.5); 0.15 mm trace.
        # Weave: x=132.0 upper column, jog to x=132.25 at the wide CMP.4 GND
        # pad latitude (y~118.9), then down to CMP.3.
        track(
            board,
            "RSSI_REF",
            B,
            [
                (131.50, 112.00),
                (132.00, 112.80),
                (132.00, 117.00),
                (132.25, 118.20),
                (132.25, 119.50),
                (131.55, 121.19),
            ],
            w=0.15,
        )
        track(board, "RSSI_REF", B, [(132.00, 114.00), (132.52, 114.00)], w=0.15)

    if which in ("v3", "all"):
        # +3V3 stays right of the REF weave / RL.1(REF): jog to x=133.0 over
        # RL.1, down x=132.6 to CMP.2.
        track(
            board,
            "+3V3",
            B,
            [
                (132.52, 112.00),
                (133.00, 112.50),
                (133.00, 115.00),
                (132.49, 116.00),
                (132.60, 116.50),
                (132.60, 120.50),
                (132.50, 121.19),
            ],
            w=0.15,
        )

    if which in ("v3link", "all"):
        # tie the +3V3 island to board +3V3 at LNA By (140.02,121). Cross east
        # at y=116 (below the x=137.5 GND stitching-via column, y=117..122.5),
        # then down to LNA By east of that column. B.Cu.
        track(
            board,
            "+3V3",
            B,
            [(132.49, 116.00), (138.50, 116.00), (140.00, 117.50), (140.02, 121.00)],
            w=0.15,
        )
        via(board, "+3V3", 140.02, 121.00)

    if which in ("ana", "all"):
        # RSSI_ANA: B.Cu east from CMP.1 to just short of RSSI Lo.1, via, land
        track(
            board,
            "RSSI_ANA",
            B,
            [(133.45, 121.19), (137.00, 123.20), (139.60, 123.70)],
            w=0.15,
        )
        via(board, "RSSI_ANA", 139.60, 123.70)
        track(board, "RSSI_ANA", F, [(139.60, 123.70), (139.99, 124.00)], w=0.15)

    # NOTE: RSSI_DCD (RSSI_CMP.5 -> PB2-P2 pad 2 at 105.4,130.2) is a ~28 mm
    # cross-board run through the ETH-PHY/LoRa (B.Cu) and PB2 header (bottom)
    # congestion; a naive straight route shorts/mask-bridges heavily. It is left
    # for interactive GUI push-shove routing (or a real autorouter) and is NOT
    # emitted here. Invoke `dcd` only to experiment.
    if which == "dcd":
        track(
            board, "RSSI_DCD", B, [(133.45, 118.91), (135.00, 127.00), (135.00, 130.21)]
        )
        via(board, "RSSI_DCD", 135.00, 130.21)
        track(board, "RSSI_DCD", F, [(135.00, 130.21), (105.39, 130.21)])

    board.BuildListOfNets()
    # refill copper zones so they clear around the new vias/tracks
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(PCB, board)
    print("saved", PCB, "(routed:", which, ")")


if __name__ == "__main__":
    main()
