#!/usr/bin/env python3
"""gen_pilot_routing_worklist.py — List the Pilot board's open connections for hand routing.

Usage:
    python3 gen_pilot_routing_worklist.py [--out docs/Pilot-Routing-Worklist.md]

Runs ``kicad-cli pcb drc`` on ``kicads/Pilot.kicad_pcb`` and groups every "Missing connection"
item by net, ordered by the work each net needs: signal nets first (most open items first),
then the plane nets (GND, +3V3, GND2_*), which only need a via beside the pad.  Each row gives
the two items KiCad wants joined, with their board coordinates (mm, KiCad y down), so a
designer can jump to them (Edit > Find or the coordinate in the status bar).

Author: Claude Sonnet 5.5, 2026-10-20.  Owner: sgriffing.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "kicads" / "Pilot.kicad_pcb"
PLANE_NETS = ("GND", "+3V3", "GND2_CAN", "GND2_RS485", "PGND")


def net_of(desc: str) -> str:
    m = re.search(r"\[([^\]]+)\]", desc)
    return m.group(1) if m else "?"


def short(desc: str) -> str:
    desc = re.sub(r" on [A-Za-z0-9.]+( - [A-Za-z0-9.]+)?$", "", desc)
    return desc.replace("Pad ", "").replace("Track ", "track ").replace("Via ", "via ")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(HERE.parent / "docs" / "Pilot-Routing-Worklist.md"))
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        rpt = Path(tmp) / "drc.json"
        subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "-o", str(rpt), str(PCB)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        items = json.loads(rpt.read_text())["unconnected_items"]
    by_net = collections.defaultdict(list)
    for it in items:
        x, y = it["items"]
        by_net[net_of(x["description"])].append((x, y))
    sig = sorted((n for n in by_net if n not in PLANE_NETS), key=lambda n: -len(by_net[n]))
    pln = sorted((n for n in by_net if n in PLANE_NETS), key=lambda n: -len(by_net[n]))
    o = ["# Pilot hand-routing worklist", "",
         f"Generated from `kicads/Pilot.kicad_pcb`: **{len(items)} open connections on "
         f"{len(by_net)} nets**. Coordinates are board mm (KiCad y down).", "",
         "Method: open the board in KiCad's PCB Editor, enable the ratsnest, route with the",
         "interactive router (X) in push-and-shove mode, then run DRC with schematic parity.",
         "The project rules in `Pilot.kicad_dru` are active in the editor: they forbid logic",
         "copper in `ISO_BAND` and any foreign metal inside the two TI 13.1 bubbles. Plane nets",
         "need only a 0.024 / 0.012 in (0.6 / 0.3 mm) via beside the pad (In1 is GND, In4 is +3V3).",
         "",
         "## Signal nets", ""]
    for kind, nets in (("", sig), ("## Plane nets", pln)):
        if kind:
            o += ["", kind, ""]
        for n in nets:
            o += [f"### `{n}` ({len(by_net[n])})", "", "| From | At (x, y) | To | At (x, y) |",
                  "| --- | --- | --- | --- |"]
            for x, y in by_net[n]:
                xp, yp = x["pos"], y["pos"]
                o.append(f"| {short(x['description'])} | {xp['x']:.2f}, {xp['y']:.2f} | "
                         f"{short(y['description'])} | {yp['x']:.2f}, {yp['y']:.2f} |")
            o.append("")
    Path(a.out).write_text("\n".join(o))
    print(f"wrote {a.out}: {len(items)} open connections, {len(by_net)} nets")


if __name__ == "__main__":
    main()
