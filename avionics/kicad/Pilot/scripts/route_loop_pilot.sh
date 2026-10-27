#!/usr/bin/env bash
# route_loop_pilot.sh — iterate plane fan-out, grid routing and repair on a Pilot board.
#
# Usage: bash route_loop_pilot.sh <board.kicad_pcb> [rounds, default 3]
#
# The board must sit in a kicads/ directory beside its Pilot.kicad_dru / .kicad_pro (the
# layout refloorplan_keep_copper.sh writes).  Each round:
#   1. plane_fanout_pilot.py  a via beside each unconnected GND / +3V3 / GND2_* pad
#   2. grid_route_pilot.py    rule-aware A* routing of what is left, with rip-up
#   3. repair_pilot_routing.py rips whatever the project DRC rejects (it refills the
#                              zones first, so plane vias are not taken for dangling)
# and keeps a checkpoint copy of the board after the round.  freerouting is not used:
# 2.2.4 hangs on boards that already carry copper (Pilot.md "Routing status").
#
# Author: Claude Opus 5.5, 2026-10-19.  Owner: sgriffing.
# SPDX-License-Identifier: CERN-OHL-W-2.0
set -euo pipefail

PCB=$(realpath "$1")
ROUNDS=${2:-3}
HERE=$(cd "$(dirname "$0")" && pwd)
PY=/usr/bin/python3 # system Python: pcbnew + scipy (the repo .venv hides them)

unconnected() {
    # refill, then count the unconnected items kicad-cli reports
    "$PY" -c "import pcbnew, sys; b = pcbnew.LoadBoard(sys.argv[1]); \
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1], b)" "$PCB" \
        >/dev/null 2>&1
    kicad-cli pcb drc --format json -o "$PCB.drc.json" "$PCB" >/dev/null 2>&1 || true
    "$PY" -c "import json, sys; print(len(json.load(open(sys.argv[1]))['unconnected_items']))" \
        "$PCB.drc.json"
}

echo "start: $(unconnected) unconnected"
for ((r = 1; r <= ROUNDS; r++)); do
    echo "=== round $r"
    "$PY" "$HERE/plane_fanout_pilot.py" "$PCB" 2>&1 | grep -E '^plane vias placed' || true
    "$PY" "$HERE/grid_route_pilot.py" "$PCB" --ripup 2>&1 | grep -E '^routed' || true
    "$PY" "$HERE/repair_pilot_routing.py" "$PCB" 40 2>&1 | grep -E '^remaining' || true
    echo "after round $r: $(unconnected) unconnected"
    cp "$PCB" "${PCB%.kicad_pcb}.round$r.kicad_pcb"
done
