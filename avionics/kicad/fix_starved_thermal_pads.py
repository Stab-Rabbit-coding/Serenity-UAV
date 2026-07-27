#!/usr/bin/env python3
"""General, DRC-driven starved-thermal fixer: solid-connects any GND pad
that KiCad's zone fill can't give 2 thermal-relief spokes. Re-derives the
offending (ref, pad) list from a fresh kicad-cli DRC pass each iteration,
so it is not hardcoded to any specific footprint reference/instance count
-- works the same whether the board has 1 stack or N."""
import json
import subprocess
import sys
import tempfile
import re
import os

BOARD = sys.argv[1]


def run_drc():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    subprocess.run(
        ["kicad-cli", "pcb", "drc", "--format", "json", "--severity-all",
         "--output", path, BOARD],
        capture_output=True, text=True,
    )
    with open(path) as fh:
        report = json.load(fh)
    os.unlink(path)
    return report


def starved_targets(report):
    targets = set()
    for v in report.get("violations", []):
        if v.get("type") != "starved_thermal":
            continue
        for it in v.get("items", []):
            m = re.search(r"Pad (\S+) \[.*\] of (\S+) on", it.get("description", ""))
            if m:
                targets.add((m.group(2), m.group(1)))
    return targets


def main():
    import pcbnew

    for iteration in range(5):
        report = run_drc()
        targets = starved_targets(report)
        if not targets:
            print(f"iteration {iteration}: 0 starved_thermal remaining")
            return 0
        print(f"iteration {iteration}: fixing {len(targets)} pads:", sorted(targets))
        board = pcbnew.LoadBoard(BOARD)
        found = set()
        for fp in board.GetFootprints():
            ref = fp.GetReference()
            for pad in fp.Pads():
                key = (ref, pad.GetNumber())
                if key in targets:
                    pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
                    found.add(key)
        missing = targets - found
        if missing:
            print("  ! could not locate pads:", missing)
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(board.Zones())
        pcbnew.SaveBoard(BOARD, board)
    print("gave up after 5 iterations")
    return 1


if __name__ == "__main__":
    sys.exit(main())
