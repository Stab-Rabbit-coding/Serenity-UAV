#!/usr/bin/env python3
"""apply_nose_outline_r2.py -- reshape the Observer board outline and slot
keepouts to the measured nose envelope (owner decisions 2026-10-27).

* Edge.Cuts: steeper slot edges (half-width 13.25 -> 27.7 mm over 56 mm, a
  14.5 deg flare per side, was 12.0 deg), then an aft chamfer to a 46 mm aft
  edge at 66 mm (board shortened from 69.85 mm).  Every edge point sits
  >= 0.5 mm inside the head wall measured by tools/observer_board_envelope.py
  (port and starboard separately; the starboard leading corner is bounded by
  the owner-built pitot tube).
* Slot keepouts: the two existing keepout zones are re-shaped into 1.5 mm
  strips along both slot edges, u 0-56 (they sat at the KiCad origin,
  ~ (173.9, 138.6) mm off the board).

FOOTPRINTS ARE NOT MOVED: placement is the owner's (avionics/AGENTS.md).  The
aft row left outside the shortened board is reported by DRC and by
tools/observer_board_envelope.py for manual re-placement.

TEXT INJECTION, not pcbnew: the 9.0.2 binding stops wrapping objects after
Remove() and returns unwrapped SwigPyObjects from Zones()
(avionics/kicad/Observer/PCBNEW_SWIG_BUG.md); injection also leaves every
footprint byte-for-byte as the owner placed it.  (The 23 schematic-parity
items DRC reports are pre-existing soft findings -- HEAD in place shows the
same 23.)  Blocks are found by a
paren-matched walk, never by a greedy regex.

Board-local (u aft of the leading edge, lateral +port) -> KiCad:
X = X_LEAD - u, Y = Y_CL + lateral (Observer.md board frame).

Run:  /usr/bin/python3 avionics/kicad/Observer/scripts/apply_nose_outline_r2.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the
author's direction, 2026-10-27, per `AGENTS.md` §3 AI attribution.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import os
import re
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
PCB = os.path.abspath(os.path.join(HERE, "..", "kicads", "Observer.kicad_pcb"))
X_LEAD, Y_CL = 243.743246, 151.309093
HALF_U = ((0.0, 13.25), (56.0, 27.7), (66.0, 23.0))  # (u, half-width) along each side
SLOT_U1 = 56.0
SLOT_W = 1.5


def kxy(u, lat):
    return X_LEAD - u, Y_CL + lat


def blocks(s, tag):
    """(start, end) spans of board-level '(tag ...)' blocks, paren-matched."""
    out, i = [], 0
    while True:
        j = s.find("\n\t(" + tag, i)
        if j < 0:
            return out
        j += 1
        d, k = 0, j
        while True:
            if s[k] == "(":
                d += 1
            elif s[k] == ")":
                d -= 1
                if d == 0:
                    break
            k += 1
        out.append((j, k + 1))
        i = k + 1


def outline_pts():
    return [(u, h) for u, h in HALF_U] + [(u, -h) for u, h in reversed(HALF_U)]


def gr_line(a, b):
    (x0, y0), (x1, y1) = kxy(*a), kxy(*b)
    return (f'(gr_line\n\t\t(start {x0:.6f} {y0:.6f})\n\t\t(end {x1:.6f} {y1:.6f})\n'
            f'\t\t(stroke\n\t\t\t(width 0.1)\n\t\t\t(type default)\n\t\t)\n'
            f'\t\t(layer "Edge.Cuts")\n\t\t(uuid "{uuid.uuid4()}")\n\t)')


def main():
    s = open(PCB, encoding="utf-8").read()
    # 1. Edge.Cuts: drop every gr_line / gr_arc on Edge.Cuts, insert the new loop
    spans = [sp for t in ("gr_line", "gr_arc") for sp in blocks(s, t)
             if '(layer "Edge.Cuts")' in s[sp[0]:sp[1]]]
    if not spans:
        sys.exit("no Edge.Cuts items found")
    pts = outline_pts()
    new_edges = "\n\t".join(gr_line(a, b) for a, b in zip(pts, pts[1:] + pts[:1]))
    first = min(sp[0] for sp in spans)
    for a, b in sorted(spans, reverse=True):
        s = s[:a] + s[b:]
    s = s[:first] + new_edges + s[first:]
    s = re.sub(r"\n\t\n", "\n", s)
    # 2. slot keepouts: rewrite the pts of the two keepout zones
    (u0, h0), (u1, h1) = HALF_U[0], HALF_U[1]
    k = (h1 - h0) / (u1 - u0)
    zones = [sp for sp in blocks(s, "zone") if "(keepout" in s[sp[0]:sp[1]]]
    if len(zones) != 2:
        sys.exit(f"expected 2 keepout zones, found {len(zones)}")
    for (a, b), sgn in sorted(zip(zones, (1.0, -1.0)), key=lambda t: -t[0][0]):
        z = s[a:b]
        xy = []
        for u, inset in ((0.0, 0.0), (SLOT_U1, 0.0), (SLOT_U1, SLOT_W), (0.0, SLOT_W)):
            x, y = kxy(u, sgn * (h0 + k * u - inset))
            xy.append(f"(xy {x:.6f} {y:.6f})")
        z = re.sub(r"\(pts\s*(\(xy [^)]*\)\s*)+\)", "(pts\n\t\t\t\t" + " ".join(xy) + "\n\t\t\t)",
                   z, count=1)
        s = s[:a] + z + s[b:]
    open(PCB, "w", encoding="utf-8").write(s)
    print(f"wrote {PCB}: Edge.Cuts {len(spans)} -> {len(pts)} segments; 2 slot keepouts"
          " re-shaped; footprints untouched")


if __name__ == "__main__":
    main()
