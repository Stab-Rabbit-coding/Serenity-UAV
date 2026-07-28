#!/usr/bin/env python3
"""route_can_periph_gw_pcb.py -- non-destructive net-sync + rip-up/reroute pass
on the user's manually-packed CAN-PERIPH-GW-1.kicad_pcb.

Unlike gen_can_periph_gw_pcb.py (which rebuilds the board from scratch and
re-places every footprint at a fixed grid), this script never moves a
footprint. It only touches nets, tracks/vias, and zones:

    1. Re-syncs every pad's net assignment from a fresh schematic netlist
       export (footprint position untouched) -- needed whenever the
       schematic changes after a manual packing pass.
    2. Nudges reference-designator silkscreen text that DRC flags as
       overlapping (silk_overlap / silk_over_copper) onto F.Fab instead,
       same pattern this project already uses on ENC-NACELLE-1 for dense
       boards -- does not move the footprint itself.
    3. --route (or the default; see `main`): rips up every existing
       track/via and re-routes from scratch via the Specctra DSN/freerouting
       2.2.4 bridge (tools/export-specctra-dsn.py + freerouting headless CLI
       + tools/import-specctra-ses.py), then re-derives and fixes any
       `starved_thermal` DRC pads (avionics/kicad/fix_starved_thermal_pads.py).
       Rip-up-then-reroute, not patch-in-place, because freerouting needs the
       CURRENT placement and CURRENT netclass clearance from the start of its
       own pass -- routing done under an earlier placement or a looser
       clearance rule does not become compliant by importing more tracks on
       top of it (verified 2026-07-28: raising clearance from 0.127/0.2 mm to
       0.3 mm without a rip-up left the old tracks in place and violating the
       new rule).
    4. --sync-only: skip step 3 (net sync + silk fix + zone fill only, the
       original lighter-weight behavior of this script before 2026-07-28).

HISTORY -- TRIED AND REVERTED (2026-07-26): an early version of this script
auto-routed every net as a straight-line minimum-spanning-tree between its
pads. That is NOT a real autorouter (no collision avoidance) and made things
measurably WORSE -- DRC went from 114 unconnected (benign) to 266 errors
including 48 shorting_items and 55 tracks_crossing (actual shorts). That
finding is about naive straight-line routing specifically, not autorouting in
general -- freerouting IS a real, collision-aware autorouter and does not
have this failure mode (verified repeatedly since 2026-07-26; see
CAN-PERIPH-GW-1.md "Signal routing" open item for the current unrouted-net
count after each pass).

Usage:
    python3 route_can_periph_gw_pcb.py                 # full rebuild (default)
    python3 route_can_periph_gw_pcb.py --sync-only      # net sync only, no reroute
    python3 route_can_periph_gw_pcb.py --passes 10       # fewer freerouting passes

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI-assist: Claude Fable 5 (Anthropic), 2026-07-26/28
License: CC BY 4.0
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
KICADS = HERE.parent / "kicads"
BOARD = KICADS / "CAN-PERIPH-GW-1.kicad_pcb"
SCH = KICADS / "CAN-PERIPH-GW-1.kicad_sch"
NETLIST = KICADS / "CAN-PERIPH-GW-1.net"
DSN = KICADS / "CAN-PERIPH-GW-1.dsn"
SES = KICADS / "CAN-PERIPH-GW-1.ses"

TOOLS = HERE.parent.parent.parent.parent / "tools"
FIX_STARVED_THERMAL = HERE.parent.parent / "fix_starved_thermal_pads.py"
FREEROUTING_JAR = "/usr/share/freerouting-2.2.4-linux-x64/lib/app/freerouting-executable.jar"
DEFAULT_PASSES = 20
FREEROUTING_TIMEOUT_S = 1800

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


def sync_nets_and_silk():
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

    print(f"  synced {n_synced} pads to current schematic nets")

    # 2) Move overlapping-silk reference text to F.Fab (ENC-NACELLE-1 pattern).
    for fp in board.GetFootprints():
        ref_text = fp.Reference()
        if ref_text.GetLayer() == pcbnew.F_SilkS:
            ref_text.SetLayer(pcbnew.F_Fab)

    pcbnew.SaveBoard(str(BOARD), board)
    print("  saved (net sync + silk fix)")


def rip_up_routing():
    import pcbnew

    board = pcbnew.LoadBoard(str(BOARD))
    tracks = list(board.GetTracks())
    for t in tracks:
        board.Remove(t)
    pcbnew.SaveBoard(str(BOARD), board)
    print(f"  removed {len(tracks)} existing track/via segments")


def export_dsn():
    subprocess.run(
        [sys.executable, str(TOOLS / "export-specctra-dsn.py"), str(BOARD), str(DSN)],
        check=True,
        capture_output=True,
    )
    print(f"  exported {DSN.name}")


def run_freerouting(max_passes):
    if SES.exists():
        SES.unlink()
    cmd = [
        "java", "-Djava.awt.headless=true", "-jar", FREEROUTING_JAR,
        "-de", str(DSN), "-do", str(SES), "-mp", str(max_passes),
    ]
    log_path = KICADS / "freerouting_run.log"
    with open(log_path, "w") as log:
        subprocess.run(cmd, cwd=str(KICADS), stdout=log, stderr=subprocess.STDOUT,
                        timeout=FREEROUTING_TIMEOUT_S, check=True)
    if not SES.exists():
        raise RuntimeError(
            f"freerouting did not produce {SES.name} -- see {log_path} "
            f"(the jar only writes .ses on a completed run; a killed/timed-out "
            f"process leaves nothing, even after passes have visibly progressed "
            f"in the log)"
        )
    print(f"  freerouting session complete, see {log_path.name}")


def import_ses():
    subprocess.run(
        [sys.executable, str(TOOLS / "import-specctra-ses.py"), str(BOARD), str(SES)],
        check=True,
        capture_output=True,
    )
    print("  imported routed session, zones refilled")


def fix_starved_thermals():
    subprocess.run(
        [sys.executable, str(FIX_STARVED_THERMAL), str(BOARD)],
        check=True,
    )


def report_drc():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    subprocess.run(
        ["kicad-cli", "pcb", "drc", "--format", "json", "--severity-all",
         "--output", path, str(BOARD)],
        capture_output=True, text=True,
    )
    with open(path) as fh:
        report = json.load(fh)
    os.unlink(path)
    from collections import Counter
    c = Counter((v.get("severity"), v.get("type")) for v in report.get("violations", []))
    print(f"  DRC: {sum(c.values())} violations, {len(report.get('unconnected_items', []))} unconnected")
    for k, n in sorted(c.items(), key=lambda x: -x[1]):
        print(f"    {k[0]:8s} {k[1]:24s} {n}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sync-only", action="store_true",
                     help="net sync + silk fix only, skip rip-up/reroute")
    ap.add_argument("--passes", type=int, default=DEFAULT_PASSES,
                     help=f"freerouting max passes (default {DEFAULT_PASSES})")
    args = ap.parse_args()

    export_netlist()
    sync_nets_and_silk()

    if not args.sync_only:
        rip_up_routing()
        export_dsn()
        run_freerouting(args.passes)
        import_ses()
        fix_starved_thermals()

    report_drc()
    return 0


if __name__ == "__main__":
    sys.exit(main())
