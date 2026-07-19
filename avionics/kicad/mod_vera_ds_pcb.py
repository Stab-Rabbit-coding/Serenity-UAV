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

Board frame (user-confirmed 2026-07-12): +X fore->aft, +Y starboard->port,
+Z ventral->dorsal.  The sensor connectors (and these lands) are at the HIGH-X end
(~62-67mm); the network connectors are at the low-X end -- correct as-built.  The
three apertures differ in the PORT-STARBOARD (Y) axis (camera=port/high-Y,
ToF=starboard/low-Y, laser=centreline), so the lands are spread along Y with the
aperture spacing from bow_sensor_pod.scad (ToF..laser 8.2mm, ToF..camera 16.5mm).
The Y positions here are a STARTING alignment; final XY/rotation to the sensor
mounting plate is a MANUAL mechanical fit (project rule: final placement is manual).

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

# Vera board frame (user, 2026-07-12): +X fore->aft, +Y starboard->port,
# +Z ventral->dorsal.  Sensors FORWARD, network AFT.  The three nose apertures
# differ in the PORT-STARBOARD (Y) axis: camera=PORT (high Y), ToF=STARBOARD
# (low Y), laser=centreline (mid Y); Y spacing is aperture-derived
# (bow_sensor_pod.scad: ToF..laser 8.2mm, ToF..camera 16.5mm).  The lands are
# co-located with their JST counterparts at the SENSOR end of the board (high-X,
# correct as-built).
#
# ref -> (footprint name, {pad_number: net_name}, (x_mm, y_mm))
SENSOR_X = 62.0  # co-located just inboard of the sensor JST cluster (X~65-67)
LANDS = {
    "J_TOF_DS": (
        "DS_ToF_4P",
        {1: "+5V", 2: "GND", 3: "UART_TOF_TX", 4: "UART_TOF_RX"},
        (SENSOR_X, 5.0),
    ),  # starboard (low Y)
    "J_LASER_DS": (
        "DS_Laser_2P",
        {1: "+5V", 2: "LASER_CATHODE"},
        (SENSOR_X, 13.2),
    ),  # centreline (mid Y) = +8.2 mm from ToF
    "J_CAM_DS": (
        "DS_Camera_9P",
        {
            1: "CSI_CLK_P",
            2: "CSI_CLK_N",
            3: "CSI_D0_P",
            4: "CSI_D0_N",
            5: "CAM_SDA",
            6: "CAM_SCL",
            7: "CAM_RESET_N",
            8: "+3V3",
            9: "GND",
        },
        (SENSOR_X, 21.5),
    ),  # port (high Y) = +16.5 mm from ToF
}


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
    existing = {f.GetReference(): f for f in board.GetFootprints()}
    for ref, (fpname, padnets, pos) in LANDS.items():
        if ref in existing:  # reposition an already-placed land (idempotent)
            fp = existing[ref]
            fp.SetPosition(mm(pos))
            print(f"  repositioned {ref} -> {pos}")
        else:
            fp = pcbnew.FootprintLoad(PRETTY, fpname)
            if fp is None:
                print(f"ERROR: could not load {fpname} from {PRETTY}")
                return 1
            fp.SetReference(ref)
            fp.SetPosition(mm(pos))
            board.Add(fp)
            print(f"  placed {ref} ({fpname}) at {pos}")
        for padnum, netname in padnets.items():  # pylint: disable=no-member
            pad = fp.FindPadByNumber(str(padnum))
            if pad is None:
                print(f"ERROR: {ref} has no pad {padnum}")
                return 1
            pad.SetNet(get_net(board, netname))
        print(f"    {ref}: {len(padnets)} pads netted")
    board.BuildListOfNets()
    pcbnew.SaveBoard(str(BOARD), board)
    print("saved", BOARD.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
