#!/usr/bin/env bash
# refloorplan_keep_copper.sh — ISOW §13.1 re-floorplan of Pilot that keeps valid routing.
#
# Usage: bash refloorplan_keep_copper.sh <in.kicad_pcb> <workdir>
#
# Owner choice 2026-10-17 (S. Griffing): keep the manual routing the re-floorplan does
# not invalidate.  Pipeline (script by Claude Opus 5.5), all on copies in <workdir>:
#   1. refloorplan_pilot.py --keep-copper   netlist sync (GNSS off), §13.1 FIXED poses,
#                                           auto re-placement of displaced parts
#   2. iso_zones_pilot.py                   ISO_BAND / islands / planes / bubbles + DRC
#                                           rules, for the new isolated domains
#   3. cleanup_pilot_copper.py              copper on nets that left the netlist
#   4. repair_pilot_routing.py              rip DRC-violating and dangling copper
# The result is <workdir>/kicads/Pilot.kicad_pcb with its Pilot.kicad_dru beside it, ready
# for plane fan-out and grid routing.  The input board is never modified.
#
# SPDX-License-Identifier: CERN-OHL-W-2.0
set -euo pipefail

IN=$(realpath "$1")
WORK=$(realpath -m "$2")
HERE=$(cd "$(dirname "$0")" && pwd)
KICADS="$HERE/../kicads"
LIBS="$HERE/../.."
PY=/usr/bin/python3 # system Python: pcbnew + shapely (the repo .venv hides them)

mkdir -p "$WORK/kicads"
# the project fp-lib-table resolves ${KIPRJMOD}/../../Serenity-Custom.pretty
ln -sfn "$(realpath "$LIBS/Serenity-Custom.pretty")" "$WORK/Serenity-Custom.pretty"
ln -sfn "$(realpath "$LIBS/Serenity-Custom.3dshapes")" "$WORK/Serenity-Custom.3dshapes"
cp "$KICADS"/{Pilot.kicad_pro,Pilot.kicad_sch,Pilot.kicad_sym,sym-lib-table,fp-lib-table} "$WORK/kicads/"
cp "$KICADS/Pilot.kicad_dru" "$WORK/stage1.kicad_dru"

"$PY" "$HERE/refloorplan_pilot.py" --keep-copper --rmax 35 "$IN" "$WORK/stage1.kicad_pcb" \
    --png "$WORK/stage1.png" 2>&1 | grep -v "memory leak"
"$PY" "$HERE/iso_zones_pilot.py" "$WORK/stage1.kicad_pcb" "$WORK/kicads/Pilot.kicad_pcb" 2>&1 |
    grep -v "memory leak"
python3 "$HERE/cleanup_pilot_copper.py" "$WORK/kicads/Pilot.kicad_pcb"
python3 "$HERE/repair_pilot_routing.py" "$WORK/kicads/Pilot.kicad_pcb" 200
