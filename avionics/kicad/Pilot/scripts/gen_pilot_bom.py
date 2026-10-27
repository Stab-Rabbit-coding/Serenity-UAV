#!/usr/bin/env python3
"""gen_pilot_bom.py — Write the Pilot assembly BOM (CSV) from the schematic.

Usage:
    python3 gen_pilot_bom.py [--out docs/Pilot-BOM.csv]

Runs ``kicad-cli sch export bom`` on ``kicads/Pilot.kicad_sch`` (grouped by value,
footprint and MPN) and reformats the result into the column set that Cyber City Circuits,
PCBWay and most kitting houses accept: Line, Qty, Designator, MPN, Manufacturer, Description,
Package, Type, DNP.  Refuses to write the file if any line lacks an MPN or a manufacturer,
because a kitted or turnkey order cannot use such a line.

The MPNs themselves live in ``gen_pilot_sch.py`` (the symbol ``MPN`` field, ``PASSIVE_MPN``
and ``MFR_BY_MPN``), not here.

Author: Claude Sonnet 5.5, 2026-10-20.  Owner: sgriffing.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCH = HERE.parent / "kicads" / "Pilot.kicad_sch"
THT_FOOTPRINTS = ("PocketBeagle2", "Molex_NanoFit", "Samtec_TSM")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(HERE.parent / "docs" / "Pilot-BOM.csv"))
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        raw = Path(tmp) / "bom.csv"
        subprocess.run(
            ["kicad-cli", "sch", "export", "bom", "--fields",
             "Reference,Value,Footprint,MPN,Manufacturer,${QUANTITY},${DNP}",
             "--group-by", "Value,Footprint,MPN", "--ref-range-delimiter", "",
             "-o", str(raw), str(SCH)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        rows = list(csv.DictReader(raw.open()))
    bad = [r["Reference"] for r in rows if not r["MPN"].strip() or not r["Manufacturer"].strip()]
    if bad:
        sys.exit(f"BOM lines without MPN or manufacturer: {bad}")
    out_rows = []
    for i, r in enumerate(sorted(rows, key=lambda x: x["Reference"].split(",")[0]), start=1):
        fp = r["Footprint"].split(":")[-1]
        tht = fp.startswith(THT_FOOTPRINTS) or "THT" in fp
        out_rows.append({
            "Line": i, "Qty": r["QUANTITY"], "Designator": r["Reference"].replace("?", ""),
            "MPN": r["MPN"], "Manufacturer": r["Manufacturer"], "Description": r["Value"],
            "Package": fp, "Type": "THT" if tht else "SMD",
            "DNP": "DNP" if r["DNP"].strip() else "",
        })
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0]))
        w.writeheader()
        w.writerows(out_rows)
    print(f"wrote {a.out}: {len(out_rows)} lines")


if __name__ == "__main__":
    main()
