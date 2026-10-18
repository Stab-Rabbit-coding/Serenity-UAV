#!/usr/bin/env python3
"""notch_iso_band.py — Cut the CAN isolation band back from under the GPS module.

Usage:
    python3 notch_iso_band.py <board.kicad_pcb>

Owner decision 2026-10-11 (S. Griffing / Stab-Rabbit-coding), option A of the GPS band
notch review (claude.ai artifact "Pilot GPS Band Notch"):
the band's top-left corner covered GPS (MAX-M10S, B.Cu) pins 1-9 at y 109.5 mm, so no pin
could via to a plane, and In1 under the module was the GND2_CAN island.  The band edge
moves from y 105.5 to y 111.0 mm over x 128.3-137.6 mm.  No part moves.

Six outlines change, all by exact point-list replacement on the S-expression text
(the pcbnew 9.0.2 SWIG binding is unreliable for geometry edits; see PCBNEW_SWIG_BUG.md):

* ISO_BAND rule area (F.Cu + In1-In4)          -> notched polygon
* "isolation keepout inner" on In2, In3, In4   -> notched polygon
* GND2_CAN island (In1)                         -> notched polygon
* GND plane (In1) and +3V3 plane (In4) cut-outs -> follow the notch

Zones are then refilled with pcbnew's ZONE_FILLER and saved.  The 0.5 mm cross-domain
rule (Pilot.kicad_dru iso_cross_domain_clearance) keeps the fills apart.

Tightest new gap: notch edge to CAN-TR isolated pins (F.Cu) 0.725 mm; the existing
B.Cu gap GPS pins -> CMC-CAN isolated pads is also 0.725 mm.  References: u-blox
MAX-M10S Integration Manual UBX-20053088 R05 sec. 4 (ground below the module);
TI ISOW1044 SLLSFF7A p. 7 note 1 [REF-SENSOR-009].

Author: Claude Opus 5.5, 2026-10-11.  Owner: sgriffing.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

RECT = "(xy 128.3 105.5) (xy 155.9 105.5) (xy 155.9 122) (xy 128.3 122)"
NOTCHED = ("(xy 128.3 111) (xy 137.6 111) (xy 137.6 105.5) (xy 155.9 105.5) "
           "(xy 155.9 122) (xy 128.3 122)")
CAN_RECT = "(xy 128.3 105.5) (xy 141.85 105.5) (xy 141.85 122) (xy 128.3 122)"
CAN_NOTCHED = ("(xy 128.3 111) (xy 137.6 111) (xy 137.6 105.5) (xy 141.85 105.5) "
               "(xy 141.85 122) (xy 128.3 122)")
# plane outlines walk the band cut-out counter-clockwise:
#   ... 155.9,105.5 -> 128.3,105.5 -> 128.3,122
PLANE_CUT = "(xy 155.9 105.5) (xy 128.3 105.5) (xy 128.3 122)"
PLANE_NOTCHED = "(xy 155.9 105.5) (xy 137.6 105.5) (xy 137.6 111) (xy 128.3 111) (xy 128.3 122)"

# zone name -> (expected count, old pts, new pts)
EDITS = {
    "ISO_BAND": (1, RECT, NOTCHED),
    "isolation keepout inner": (3, RECT, NOTCHED),
    "GND2_CAN island": (1, CAN_RECT, CAN_NOTCHED),
    "GND plane": (1, PLANE_CUT, PLANE_NOTCHED),
    "+3V3 plane": (1, PLANE_CUT, PLANE_NOTCHED),
}


def outline_span(blk: str) -> "tuple[int, int]":
    """Span of the zone's own outline point list (not its filled_polygon)."""
    m = re.search(r"\t\t\(polygon\n\t\t\t\(pts\n(.*?)\n\t\t\t\)", blk, re.S)
    if m is None:
        raise SystemExit("zone without an outline polygon")
    return m.start(1), m.end(1)


def norm(pts: str) -> str:
    return " ".join(pts.split())


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    pcb = Path(sys.argv[1])
    text = pcb.read_text()
    done = {k: 0 for k in EDITS}
    out, last = [], 0
    for m in re.finditer(r"^\t\(zone\n", text, re.M):
        end = text.index("\n\t)\n", m.start())
        blk = text[m.start():end]
        name = re.search(r'\(name "([^"]*)"\)', blk)
        if not name or name.group(1) not in EDITS:
            continue
        _, old, new = EDITS[name.group(1)]
        s, e = outline_span(blk)
        pts = norm(blk[s:e])
        if old not in pts:
            continue  # e.g. the two small B.Cu ISO_BAND rectangles
        new_pts = "\t\t\t\t" + pts.replace(old, new)
        out.append(text[last:m.start() + s])
        out.append(new_pts)
        last = m.start() + e
        done[name.group(1)] += 1
    out.append(text[last:])
    for k, (want, _, _) in EDITS.items():
        if done[k] != want:
            raise SystemExit(f"{k}: edited {done[k]} outline(s), expected {want} "
                             "— board left unchanged")
    pcb.write_text("".join(out))
    fill = (f"import pcbnew; b = pcbnew.LoadBoard({str(pcb)!r}); "
            f"pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard({str(pcb)!r}, b)")
    subprocess.run([sys.executable, "-c", fill], check=True, capture_output=True)
    print("notched:", ", ".join(f"{k} x{v}" for k, v in done.items()), "; zones refilled")


if __name__ == "__main__":
    main()
