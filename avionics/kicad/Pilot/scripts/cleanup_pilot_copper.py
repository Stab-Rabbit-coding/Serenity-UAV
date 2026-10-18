#!/usr/bin/env python3
"""cleanup_pilot_copper.py — Drop routed copper whose net left the Pilot netlist.

Usage:
    python3 cleanup_pilot_copper.py <board.kicad_pcb>

Part of the keep-copper re-floorplan (owner choice 2026-10-17: keep the manual routing
the ISOW §13.1 re-floorplan does not invalidate; script by Claude Opus 5.5).  After
``refloorplan_pilot.py --keep-copper`` the board still carries tracks and vias on nets
that ``kicads/Pilot.net`` no longer has (the GNSS chain left the cape, schematic
3f55d588).  Those items are removed here, by exact S-expression edits; everything the
moves made illegal or dangling is left for ``repair_pilot_routing.py``, which rips
DRC-named copper in a loop.

License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

NETLIST = Path(__file__).resolve().parent.parent / "kicads" / "Pilot.net"


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    pcb = Path(sys.argv[1])
    text = pcb.read_text()
    keep = set(re.findall(r'\(net \(code "?\d+"?\) \(name "((?:[^"\\]|\\.)*)"\)', NETLIST.read_text()))
    if not keep:
        sys.exit("no nets read from the netlist (format changed?)")
    # board net table: (net <code> "<name>") at indent 1
    code_name = {int(c): n for c, n in re.findall(r'^\t\(net (\d+) "((?:[^"\\]|\\.)*)"\)', text, re.M)}
    gone = {c for c, n in code_name.items() if c and n not in keep}
    out, last, n = [], 0, 0
    for m in re.finditer(r"^\t\((segment|arc|via)(?: \w+)?\n.*?^\t\)\n", text, re.S | re.M):
        net = re.search(r"^\t\t\(net (\d+)\)", m.group(0), re.M)
        if net and int(net.group(1)) in gone:
            out.append(text[last:m.start()])
            last = m.end()
            n += 1
    out.append(text[last:])
    pcb.write_text("".join(out))
    print(f"nets gone from the netlist: {sorted(code_name[c] for c in gone)}")
    print(f"removed {n} track/via item(s) on them")


if __name__ == "__main__":
    main()
