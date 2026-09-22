#!/usr/bin/env python3
"""route_can_periph_gw_pcb.py -- non-destructive net-sync pass on the user's
manually-packed CAN-PERIPH-GW-1.kicad_pcb.

Unlike gen_can_periph_gw_pcb.py (which rebuilds the board from scratch and
re-places every footprint at a fixed grid), this script:
    1. Re-syncs every pad's net assignment from a fresh schematic netlist
       export, WITHOUT moving any footprint (preserves the user's manual
       component packing/resizing) -- needed because the schematic changed
       (ADM2795E -> ISOW1412, MSPM0G3507 pinmux fixes) after the manual
       packing pass.
    2. Re-fills the GND zones.
    3. Nudges reference-designator silkscreen text that DRC flags as
       overlapping (silk_overlap / silk_over_copper) onto F.Fab instead,
       same pattern this project already uses on ENC-NACELLE-1 for dense
       boards -- does not move the footprint itself.

TRIED AND REVERTED: an earlier version of this script also auto-routed every
net as a straight-line minimum-spanning-tree between its pads. That is NOT
a real autorouter (no collision avoidance) and it made things measurably
WORSE, not better -- DRC went from 114 unconnected (annoying but benign) to
266 errors including 48 shorting_items and 55 tracks_crossing (actual
electrical shorts between different nets, which is worse than leaving a net
unrouted). No autorouter is available in this environment (no `freerouting`
binary; `kicad-cli pcb export` has no `dsn` target to hand off to one), so
real collision-aware routing for CAN_H/CAN_L, RS485_A/B, and the other ~40
nets is left as a manual KiCad routing pass -- see CAN-PERIPH-GW-1.md open
items. Net sync + silk fix are still safe, useful, non-destructive wins on
their own and are kept.

Usage: python3 route_can_periph_gw_pcb.py
Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI-assist: Claude Fable 5 (Anthropic), 2026-07-26
License: CC BY 4.0
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KICADS = HERE.parent / "kicads"
BOARD = KICADS / "CAN-PERIPH-GW-1.kicad_pcb"
SCH = KICADS / "CAN-PERIPH-GW-1.kicad_sch"
NETLIST = KICADS / "CAN-PERIPH-GW-1.net"

TRACK_WIDTH = 0.25
VIA_SIZE = 0.6
VIA_DRILL = 0.3


def export_netlist():
    subprocess.run(
        ["kicad-cli", "sch", "export", "netlist", "-o", str(NETLIST), str(SCH)],
        check=True,
        capture_output=True,
    )


def parse_padnet():
    src = NETLIST.read_text()
    padnet = {}
    for m in re.finditer(
        r'\(net \(code "[^"]*"\) \(name "([^"]*)"\)(.*?)(?=\(net \(code|\Z)', src, re.S
    ):
        name = m.group(1)
        for r, p in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"', m.group(2)):
            padnet[(r, p)] = name
    return padnet


def sync_nets_and_route():
    import pcbnew

    board = pcbnew.LoadBoard(str(BOARD))
    padnet = parse_padnet()

    # Ensure every net used by the netlist exists on the board.
    existing = {n.GetNetname() for n in board.GetNetInfo().NetsByNetcode().values()}
    for name in sorted(set(padnet.values())):
        if name and name not in existing:
            board.Add(pcbnew.NETINFO_ITEM(board, name))
    netinfo = board.GetNetInfo()
    by_name = {n.GetNetname(): n for n in netinfo.NetsByNetcode().values()}

    # 1) Re-sync every pad's net assignment (footprint position untouched).
    n_synced = 0
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        for pad in fp.Pads():
            padname = pad.GetPadName()
            net = padnet.get((ref, padname))
            if net and net in by_name:
                pad.SetNet(by_name[net])
                n_synced += 1
            else:
                pad.SetNet(board.FindNet(0))

    print(f"  synced {n_synced} pads to current schematic nets (no routing -- see module docstring)")

    # 2) Move overlapping-silk reference text to F.Fab (ENC-NACELLE-1 pattern).
    for fp in board.GetFootprints():
        ref_text = fp.Reference()
        if ref_text.GetLayer() == pcbnew.F_SilkS:
            ref_text.SetLayer(pcbnew.F_Fab)

    pcbnew.SaveBoard(str(BOARD), board)
    print("  saved (net sync + silk fix, no routing -- see module docstring)")


def fill_zones():
    import pcbnew

    board = pcbnew.LoadBoard(str(BOARD))
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(str(BOARD), board)
    print("  zones filled")


def main():
    export_netlist()
    sync_nets_and_route()
    fill_zones()
    return 0


if __name__ == "__main__":
    sys.exit(main())
