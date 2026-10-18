#!/usr/bin/env python3
"""iso_via_windows.py — Open local via windows in Pilot's inner isolation keep-outs.

Usage:
    python3 iso_via_windows.py <board.kicad_pcb>

Owner decision 2026-10-11 (S. Griffing / Stab-Rabbit-coding): the four isolated-side
parts on B.Cu under the CAN / RS-485 band (CMC-CAN, C-CAN5, CMC-RS485, C-485-5) cannot
reach their F.Cu partners, because the "isolation keepout inner" rule areas on
In2/In3/In4 forbid every via inside the band and B.Cu carries no ISO_BAND area under
them.  gen_pilot_pcb.py documents the keep-outs' purpose as keeping the band
"copper-free on the inner signal layers ... and on the +3V3 plane" and expects an
isolated "island via" for the X2Y GND2 stubs, so the blanket via ban is not the
stated intent.  This script, by exact S-expression edits only:

1. Replaces each In2/In3/In4 keep-out (the notched band polygon) with rectangles that
   tile the band MINUS one window W, so isolated vias (and short isolated inner
   tracks) are possible only inside W.  Logic copper stays barred from the whole band
   by Pilot.kicad_dru iso_band_logic_copper; +3V3/GND planes already stop at the band.
2. Adds B.Cu ISO_BAND rule areas (no keep-out flags, name marker only) under the four
   parts, sized to stay clear of logic B.Cu copper (C-485-2, PB2-P2 pads, GPS pins), so
   iso_nets_stay_in_band admits their short B.Cu stubs.

Window and patch coordinates are board millimetres (KiCad y down).

Author: Claude Opus 5.5, 2026-10-11.  Owner: sgriffing.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
from __future__ import annotations

import re
import sys
import uuid
from pathlib import Path

# notched band (see notch_iso_band.py) as a union of two rectangles
BAND_RECTS = [(128.3, 111.0, 137.6, 122.0), (137.6, 105.5, 155.9, 122.0)]
# one via window over CMC-CAN, C-CAN5, CMC-RS485, C-485-5
WINDOW = (132.5, 107.9, 146.6, 113.4)
# B.Cu ISO_BAND patches (x1, y1, x2, y2)
B_PATCHES = [
    (132.5, 111.0, 141.9, 113.3),    # CMC-CAN + C-CAN5 (GPS pins end y 110.4)
    (140.2, 108.4, 144.0, 110.95),   # C-485-5 (C-485-2 starts x 144.05)
    (141.75, 110.65, 146.4, 113.25),  # CMC-RS485 (C-485-2 ends y 110.59; PB2 pads 113.385)
]


def minus(r, w):
    """Rectangle r minus rectangle w, as up to four rectangles."""
    x1, y1, x2, y2 = r
    a1, b1, a2, b2 = w
    if a1 >= x2 or a2 <= x1 or b1 >= y2 or b2 <= y1:
        return [r]
    out = []
    if b1 > y1:
        out.append((x1, y1, x2, b1))
    if b2 < y2:
        out.append((x1, b2, x2, y2))
    yy1, yy2 = max(y1, b1), min(y2, b2)
    if a1 > x1:
        out.append((x1, yy1, a1, yy2))
    if a2 < x2:
        out.append((a2, yy1, x2, yy2))
    return [q for q in out if q[2] - q[0] > 1e-6 and q[3] - q[1] > 1e-6]


def zone_block(layers: str, name: str, r, keepout: bool) -> str:
    x1, y1, x2, y2 = r
    flag = "not_allowed" if keepout else "allowed"
    pour = "not_allowed" if keepout else "allowed"
    return (f'\t(zone\n\t\t(net 0)\n\t\t(net_name "")\n\t\t(layers {layers})\n'
            f'\t\t(uuid "{uuid.uuid4()}")\n\t\t(name "{name}")\n\t\t(hatch edge 0.5)\n'
            f'\t\t(connect_pads\n\t\t\t(clearance 0)\n\t\t)\n\t\t(min_thickness 0.25)\n'
            f'\t\t(filled_areas_thickness no)\n\t\t(keepout\n\t\t\t(tracks {flag})\n'
            f'\t\t\t(vias {flag})\n\t\t\t(pads {flag})\n\t\t\t(copperpour {pour})\n'
            f'\t\t\t(footprints allowed)\n\t\t)\n\t\t(placement\n\t\t\t(enabled no)\n'
            f'\t\t\t(sheetname "")\n\t\t)\n\t\t(fill\n\t\t\t(thermal_gap 0.5)\n'
            f'\t\t\t(thermal_bridge_width 0.5)\n\t\t)\n\t\t(polygon\n\t\t\t(pts\n'
            f'\t\t\t\t(xy {x1:g} {y1:g}) (xy {x2:g} {y1:g}) (xy {x2:g} {y2:g}) (xy {x1:g} {y2:g})\n'
            f'\t\t\t)\n\t\t)\n\t)\n')


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    pcb = Path(sys.argv[1])
    text = pcb.read_text()
    if "ISO via window" in text:
        sys.exit("windows already present — board left unchanged")
    removed = 0
    out, last = [], 0
    for m in re.finditer(r"^\t\(zone\n", text, re.M):
        end = text.index("\n\t)\n", m.start()) + len("\n\t)\n")
        blk = text[m.start():end]
        if '(name "isolation keepout inner")' in blk:
            out.append(text[last:m.start()])
            last = end
            removed += 1
    out.append(text[last:])
    if removed != 3:
        sys.exit(f"expected 3 inner keep-outs, found {removed} — board left unchanged")
    text = "".join(out)
    pieces = [q for r in BAND_RECTS for q in minus(r, WINDOW)]
    blocks = []
    for layer in ("In2.Cu", "In3.Cu", "In4.Cu"):
        for q in pieces:
            blocks.append(zone_block(f'"{layer}"', "isolation keepout inner", q, True))
    for q in B_PATCHES:
        blocks.append(zone_block('"B.Cu"', "ISO_BAND", q, False))
    blocks.append(f"\t(gr_text \"ISO via window\"\n\t\t(at {WINDOW[0]:g} {WINDOW[1]:g} 0)\n"
                  f"\t\t(layer \"Cmts.User\")\n\t\t(uuid \"{uuid.uuid4()}\")\n"
                  f"\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 0.5 0.5)\n\t\t\t\t(thickness 0.08)\n"
                  f"\t\t\t)\n\t\t\t(justify left bottom)\n\t\t)\n\t)\n")
    i = text.index("\n\t(zone\n") + 1
    pcb.write_text(text[:i] + "".join(blocks) + text[i:])
    print(f"keep-outs: 3 replaced by {len(pieces)} rectangles per layer around window {WINDOW}; "
          f"{len(B_PATCHES)} B.Cu ISO_BAND patches added")


if __name__ == "__main__":
    main()
