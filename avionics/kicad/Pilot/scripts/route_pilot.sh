#!/usr/bin/env bash
# route_pilot.sh — two-phase freerouting pass over a (partly) routed Pilot board.
#
# Usage: bash route_pilot.sh <board.kicad_pcb> [max_passes]
#
# Phase 1 (band closed): the ISO_BAND rule area is exported as a hard keepout on
#   every layer it covers, so freerouting routes only logic nets around the band.
# Phase 2 (band open): the ISO_BAND marker is left out of the DSN and freerouting
#   finishes the ISOLATION-class nets, whose pads all sit inside the band.
# After each import, repair_pilot_routing.py rips up anything the project DRC
#   rejects (freerouting cannot read Pilot.kicad_dru), so the board stays DRC-clean.
#
# Both DSNs are restricted to the netclass 0.6/0.3 mm through via: KiCad's Specctra
# exporter also offers 0.2/0.1 mm microvia/blind padstacks (from the netclass
# microvia fields), which this board's rules forbid and freerouting will use.
#
# Export/import/clean helpers: ../../TACCO/scripts/finish_tacco_pcb.py (shared flow).
# Freerouting: https://github.com/freerouting/freerouting (v2.2.4, GPL-3.0).
#
# Author: Claude Opus 5.5, 2026-10-10.  Owner: sgriffing.
# SPDX-License-Identifier: CERN-OHL-W-2.0
set -euo pipefail

PCB=$(realpath "$1")
PASSES=${2:-25}
HERE=$(cd "$(dirname "$0")" && pwd)
FLOW="$HERE/../../TACCO/scripts/finish_tacco_pcb.py"
JAR=/usr/share/freerouting-2.2.4-linux-x64/lib/app/freerouting-executable.jar
WORK=$(mktemp -d)

only_through_vias() {
    # Keep only the first (through) padstack in the structure's (via ...) rule.
    sed -i -E 's/^(\s*\(via "Via\[0-5\]_600:300_um")( "[^"]+")+\)\s*$/\1)/' "$1"
    grep -m1 -E '^\s*\(via "Via' "$1"
}

route() {
    local dsn=$1 ses=$2
    only_through_vias "$dsn"
    # hard wall-clock cap: freerouting 2.2.4 can hang in PolylineTrace.combine and only
    # writes the session at exit, so a hung run would otherwise block forever
    timeout "${ROUTE_TIMEOUT:-150m}" java -Xss256m -jar "$JAR" --gui.enabled=false \
        -de "$dsn" -do "$ses" -mp "$PASSES" > "${ses%.ses}.log" 2>&1 || true
    test -s "$ses" || echo "freerouting wrote no session: ${ses%.ses}.log"
}

echo "== phase 1: logic nets, band closed"
python3 "$FLOW" export "$PCB" "$WORK/p1.dsn" --band-keepout
route "$WORK/p1.dsn" "$WORK/p1.ses"
test -s "$WORK/p1.ses" || { echo "phase 1 produced no session; board unchanged"; exit 1; }
python3 "$FLOW" import "$PCB" "$WORK/p1.ses"
python3 "$HERE/repair_pilot_routing.py" "$PCB"

unconnected() {
    kicad-cli pcb drc --format json -o "$WORK/u.json" "$PCB" > /dev/null 2>&1
    python3 -c "import json; print(len(json.load(open('$WORK/u.json'))['unconnected_items']))"
}
cp "$PCB" "$WORK/after_p1.kicad_pcb"
U1=$(unconnected)
echo "after phase 1: $U1 unconnected"

echo "== phase 2: ISOLATION nets, band open"
python3 "$FLOW" export "$PCB" "$WORK/p2.dsn"
route "$WORK/p2.dsn" "$WORK/p2.ses"
if [ -s "$WORK/p2.ses" ] && python3 "$FLOW" import "$PCB" "$WORK/p2.ses"; then
    python3 "$HERE/repair_pilot_routing.py" "$PCB"
fi
U2=$(unconnected)
echo "after phase 2: $U2 unconnected"
# an import REPLACES all routing; a crashed/truncated phase-2 session must not win
if [ "$U2" -gt "$U1" ]; then
    echo "phase 2 worse ($U2 > $U1): keeping the phase-1 board"
    cp "$WORK/after_p1.kicad_pcb" "$PCB"
fi

echo "sessions and logs kept in $WORK"
