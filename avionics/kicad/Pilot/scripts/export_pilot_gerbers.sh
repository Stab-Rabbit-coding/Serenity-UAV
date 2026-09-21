#!/usr/bin/env bash
# export_pilot_gerbers.sh — Production Gerber/drill export for Pilot Rev T,
# JLCPCB 6-layer conventions (X2 format, protel extensions, mm drill, PTH/NPTH
# split, drill map).  Run only after finish_pilot_pcb.py has imported routing
# and re-filled zones.
#
# Author: Claude Sonnet 5, 2026-09-19.  Owner: sgriffing.  License: CC BY 4.0.
set -euo pipefail
cd "$(dirname "$0")/../kicads"
PCB=Pilot.kicad_pcb
OUT=../gerbers
rm -rf "$OUT"
mkdir -p "$OUT"

kicad-cli pcb export gerbers \
    --output "$OUT" \
    --layers "F.Cu,In1.Cu,In2.Cu,In3.Cu,In4.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts" \
    --subtract-soldermask \
    --precision 6 \
    "$PCB"

kicad-cli pcb export drill \
    --output "$OUT" \
    --format excellon \
    --excellon-units mm \
    --excellon-zeros-format decimal \
    --excellon-separate-th \
    --generate-map \
    --map-format gerberx2 \
    "$PCB"

echo "Gerbers + drill written to $OUT"
ls -la "$OUT"
