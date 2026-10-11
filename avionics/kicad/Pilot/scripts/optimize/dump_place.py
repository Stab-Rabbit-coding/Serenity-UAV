#!/usr/bin/env python3
"""dump_place.py — Write place.json (footprints + pads) for the committed Pilot board with a
move list applied, so search_caps.py starts from the current best placement.

Usage: python3 dump_place.py <moves.json> <out_place.json>

Author: Claude Opus 5.5, 2026-10-10.  Owner: sgriffing.
License: CERN-OHL-W-2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from eval_placement import BOARD, apply_moves, strip_routing

work = Path(tempfile.mkdtemp(prefix="pilot-dump-"))
pcb = work / "Pilot.kicad_pcb"
pcb.write_text(strip_routing(apply_moves(BOARD.read_text(), json.load(open(sys.argv[1])))))
code = f"""
import pcbnew, json
b = pcbnew.LoadBoard({str(pcb)!r}); s = 1e6
fps = []
for f in b.GetFootprints():
    f.BuildCourtyardCaches()
    c = f.GetCourtyard(pcbnew.B_CrtYd if f.IsFlipped() else pcbnew.F_CrtYd).BBox()
    fps.append(dict(ref=f.GetReference(), fp=f.GetFPIDAsString(), x=f.GetPosition().x/s, y=f.GetPosition().y/s,
                    rot=f.GetOrientationDegrees(), side='B' if f.IsFlipped() else 'F',
                    cy=[c.GetX()/s, c.GetY()/s, (c.GetX()+c.GetWidth())/s, (c.GetY()+c.GetHeight())/s]))
pads = [dict(ref=p.GetParentFootprint().GetReference(), num=p.GetNumber(), net=p.GetNetname(),
             x=p.GetPosition().x/s, y=p.GetPosition().y/s) for p in b.GetPads()]
json.dump(dict(fps=fps, pads=pads), open({sys.argv[2]!r}, 'w'))
"""
subprocess.run([sys.executable, "-c", code], check=True, capture_output=True)
print("wrote", sys.argv[2])
