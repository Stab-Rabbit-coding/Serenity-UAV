#!/usr/bin/env bash
# export_tacco_gerbers.sh — Production Gerber/drill/position export for TACCO Rev S3,
# JLCPCB 6-layer conventions (X2 format, mm drill, PTH/NPTH split, drill map), the
# same recipe as Pilot's export_pilot_gerbers.sh.  Run only after finish_tacco_pcb.py
# has imported the routing and refilled the zones, and after
# `kicad-cli pcb drc --severity-all --schematic-parity` is clean.
#
# Author: Claude Fable 5.1, 2026-09-29.  Owner: sgriffing.  License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
set -euo pipefail
cd "$(dirname "$0")/../kicads"
KICAD_CLI="${KICAD_CLI:-kicad-cli}"
PCB=TACCO.kicad_pcb
OUT=../gerbers
rm -rf "$OUT"
mkdir -p "$OUT"

"$KICAD_CLI" pcb export gerbers \
    --output "$OUT" \
    --layers "F.Cu,In1.Cu,In2.Cu,In3.Cu,In4.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts" \
    --subtract-soldermask \
    --precision 6 \
    "$PCB"

"$KICAD_CLI" pcb export drill \
    --output "$OUT" \
    --format excellon \
    --excellon-units mm \
    --excellon-zeros-format decimal \
    --excellon-separate-th \
    --generate-map \
    --map-format gerberx2 \
    "$PCB"

"$KICAD_CLI" pcb export pos \
    --output "$OUT/TACCO-pos.csv" \
    --format csv --units mm --side both --exclude-dnp \
    "$PCB"

echo "Gerbers, drill and pick-and-place written to $OUT"
ls -la "$OUT"
