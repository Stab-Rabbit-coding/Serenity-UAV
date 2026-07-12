#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mod_vera_ds_pcb.py -- add the direct-solder sensor lands (camera/ToF/laser) to the
existing Vera.kicad_pcb via the pcbnew API (the board is hand-maintained in the GUI,
so it must be MODIFIED in place, never regenerated from gen_vera_pcb.py).
=============================================================================
Adds J_CAM_DS (DS_Camera_9P), J_TOF_DS (DS_ToF_4P), J_LASER_DS (DS_Laser_2P) from
the Vera.pretty library, assigning each pad the SAME net as its JST counterpart so
the lands are true populate-one-or-the-other alternates (no net change).

PLACEMENT: the three lands are seeded in a row at the aperture-relative X spacing
from bow_sensor_pod.scad (camera CAM_POS X=170.80, ToF TOF_POS X=154.33, laser CL
~162.5 -> ToF..laser 8.2mm, ToF..camera 16.5mm) near one board edge.  This is a
STARTING position only: the final XY/rotation and which board edge faces the pod
(and the port/stbd sense) are a MANUAL mechanical fit to the nose sensor mounting
plate -- refer to user (project rule: final footprint placement is manual).

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

# ref -> (footprint name, {pad_number: net_name}, seed X mm)
# X seeds keep the ToF..laser..camera relative spacing (aperture-derived).
LANDS = {
    "J_TOF_DS": ("DS_ToF_4P",
                 {1: "+5V", 2: "GND", 3: "UART_TOF_TX", 4: "UART_TOF_RX"}, 4.5),
    "J_LASER_DS": ("DS_Laser_2P", {1: "+5V", 2: "LASER_CATHODE"}, 12.7),
    "J_CAM_DS": ("DS_Camera_9P",
                 {1: "CSI_CLK_P", 2: "CSI_CLK_N", 3: "CSI_D0_P", 4: "CSI_D0_N",
                  5: "CAM_SDA", 6: "CAM_SCL", 7: "CAM_RESET_N", 8: "+3V3",
                  9: "GND"}, 21.0),
}
SEED_Y = 6.0  # mm from the (current rectangular) board's top edge


def mm(v):
    return pcbnew.VECTOR2I(pcbnew.FromMM(v[0]), pcbnew.FromMM(v[1]))


def get_net(board, name):
    net = board.FindNet(name)
    if net is None:
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net)
        print(f"  (created missing net {name})")
    return net


def main():
    board = pcbnew.LoadBoard(str(BOARD))
    existing = {f.GetReference() for f in board.GetFootprints()}
    for ref, (fpname, padnets, seedx) in LANDS.items():
        if ref in existing:
            print(f"  {ref} already present -- skipping")
            continue
        fp = pcbnew.FootprintLoad(PRETTY, fpname)
        if fp is None:
            print(f"ERROR: could not load {fpname} from {PRETTY}")
            return 1
        fp.SetReference(ref)
        fp.SetPosition(mm((seedx, SEED_Y)))
        board.Add(fp)
        for padnum, netname in padnets.items():
            pad = fp.FindPadByNumber(str(padnum))
            if pad is None:
                print(f"ERROR: {ref} has no pad {padnum}")
                return 1
            pad.SetNet(get_net(board, netname))
        print(f"  placed {ref} ({fpname}) at x={seedx} y={SEED_Y}, "
              f"{len(padnets)} pads netted")
    board.BuildListOfNets()
    pcbnew.SaveBoard(str(BOARD), board)
    print("saved", BOARD.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
