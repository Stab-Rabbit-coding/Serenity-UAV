#!/usr/bin/env python3
"""repair_pilot_routing.py — Rip up the DRC-violating copper of a partly routed Pilot
board so the next freerouting pass can finish it cleanly.

Usage:
    python3 repair_pilot_routing.py <board.kicad_pcb> [max_rounds, default 29]

Works on the S-expression text and on ``kicad-cli pcb drc`` JSON only.  The pcbnew
SWIG binding in KiCad 9.0.2 is not usable for this: after one geometry call it
starts returning unwrapped ``SwigPyObject``s even from ``BOARD.GetTracks()``
(see ``avionics/kicad/PCBNEW_SWIG_BUG.md``).  In order:

1. Clears the two courtyard overlaps left by the 2026-10-09 manual placement pass
   (owner S. Griffing): J-ETH-RMII2 aligns with J-ETH-USB1 at x = 172.7 mm (0.204 mm overlap with
   T-RMII2) and C-P2-A3 steps 0.15 mm east (0.100 mm overlap with 1553-XFM).
2. Removes every via that is not a 0.3 mm-drill through via.  The freerouting DSN
   offered 0.2/0.1 mm microvia/blind padstacks this board's rules forbid (min via
   0.5 mm, min drill 0.3 mm); ``route_pilot.sh`` now strips them from the DSN.
3. Loops: run DRC, delete every track/via named in an error-severity item of a
   copper rule (clearance, hole_to_hole, track_width, items_not_allowed — the
   ISO_BAND rules — ...), plus dangling-track/via warnings, until DRC names none.
   For a via pair (hole_to_hole) only one via is taken.

Author: Claude Opus 5.5, 2026-10-10.  Owner: sgriffing.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Placement fixes: reference -> (new x mm or None, new y mm or None).
MOVES = {"J-ETH-RMII2": (172.7, None), "C-P2-A3": (166.9, None)}
# DRC types whose track/via items are ripped up.
RIP_TYPES = {"hole_to_hole", "track_width", "connection_width", "clearance", "hole_clearance",
             "shorting_items", "tracks_crossing", "annular_width", "drill_out_of_range",
             "via_diameter", "copper_edge_clearance", "solder_mask_bridge", "items_not_allowed",
             "track_dangling", "via_dangling"}
ROUTED = ("Track ", "Via ", "Blind/Buried Via ", "Micro Via ")


def blocks(text: str):
    """Yield (start, end, kind, body) for each top-level segment/arc/via block."""
    for m in re.finditer(r"^\t\((segment|arc|via)(?: \w+)?\n.*?^\t\)\n", text, re.S | re.M):
        yield m.start(), m.end(), m.group(1), m.group(0)


def move_footprints(text: str) -> str:
    """Rewrite the footprint-level (at x y [rot]) of each MOVES reference."""
    for ref, (nx, ny) in MOVES.items():
        tag = f'(property "Reference" "{ref}"'
        i = text.index(tag)
        fp = text.rfind("\n\t(footprint ", 0, i)
        m = re.compile(r"\n\t\t\(at ([-\d.]+) ([-\d.]+)((?: [-\d.]+)?)\)").search(text, fp)
        assert m is not None, f"{ref}: footprint block has no (at x y) line"
        x, y = float(m.group(1)), float(m.group(2))
        x, y = nx if nx is not None else x, ny if ny is not None else y
        text = text[:m.start()] + f"\n\t\t(at {x:g} {y:g}{m.group(3)})" + text[m.end():]
        print(f"{ref}: moved to ({x:g}, {y:g})")
    return text


def drop(text: str, uuids: set) -> "tuple[str, int]":
    """Remove the routed blocks whose uuid is in ``uuids``."""
    out: list = []
    last, n = 0, 0
    for s, e, _kind, body in blocks(text):
        u_m = re.search(r'\(uuid "([^"]+)"\)', body)
        assert u_m is not None, f"routed block has no uuid: {body!r}"
        u = u_m.group(1)
        if u in uuids:
            out.append(text[last:s])
            last = e
            n += 1
    out.append(text[last:])
    return "".join(out), n


def odd_vias(text: str) -> set:
    """UUIDs of vias that are blind/buried/micro or have a drill under 0.3 mm."""
    bad = set()
    for _s, _e, kind, body in blocks(text):
        if kind != "via":
            continue
        drill_m = re.search(r"\(drill ([\d.]+)\)", body)
        assert drill_m is not None, f"via block has no drill: {body!r}"
        drill = float(drill_m.group(1))
        if re.search(r"^\t\t(blind|micro)\b", body, re.M) or "(type " in body or drill < 0.3:
            uuid_m = re.search(r'\(uuid "([^"]+)"\)', body)
            assert uuid_m is not None, f"via block has no uuid: {body!r}"
            bad.add(uuid_m.group(1))
    return bad


def drc(pcb: Path) -> dict:
    out = Path(tempfile.mkdtemp()) / "drc.json"
    subprocess.run(["kicad-cli", "pcb", "drc", "--severity-all", "--format", "json",
                    "--output", str(out), str(pcb)], check=True, capture_output=True)
    return json.loads(out.read_text())


def rip_set(report: dict) -> set:
    doomed: set = set()
    for v in report.get("violations", []):
        if v["type"] not in RIP_TYPES:
            continue
        items = [it for it in v.get("items", []) if it["description"].startswith(ROUTED)]
        if v["type"] == "hole_to_hole":
            items = items[:1]
        doomed.update(it["uuid"] for it in items)
    return doomed


def main() -> None:
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    pcb = Path(sys.argv[1])
    text = move_footprints(pcb.read_text())
    text, n = drop(text, odd_vias(text))
    print("non-through / undersized vias removed:", n)
    pcb.write_text(text)
    # dangling chains shrink one segment per DRC round, so long orphaned runs (the
    # 2026-10-17 keep-copper re-floorplan) need many rounds; a round costs ~2 s
    for rnd in range(1, int(sys.argv[2]) + 1 if len(sys.argv) > 2 else 30):
        doomed = rip_set(drc(pcb))
        text, n = drop(pcb.read_text(), doomed)
        print(f"round {rnd}: ripped {n} item(s)")
        if n == 0:
            break
        pcb.write_text(text)
    rep = drc(pcb)
    print("remaining violations:", len(rep["violations"]),
          "unconnected:", len(rep["unconnected_items"]))


if __name__ == "__main__":
    main()
