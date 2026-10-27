#!/usr/bin/env python3
"""Apply the 2026-10-19 weight pass (13.0 lbm target) to the Rev T BOM.

Owner direction 2026-10-19: "go to 13.0 lbm; aggressively pursue ways to cut
weight without capability".  Owner-selected cuts applied here (the BOM half;
the geometry half is in the owning tools):

  * PRINT-PISTONS -> 0: decorative tilt-piston fairing, no source in tree.
  * FAR-CAGE-AV / -GASKET-AV / -FAN-40 / -EMI-VENT-40 / FAR-FT-PANEL -> 0: every
    node is now foil-pouched (cargo nodes D-T5-3, Simon nodes
    middle_layout_fit.py; Bay A joins them).  FAR-BOND-STRAP stays, one per
    node stack, to terminate each pouch to chassis; ferrites unchanged.
  * PRINT-CARGO-CRADLE -> 0: stowed payload is held by the winch ratchet
    (docs/CARGO_WINCH_SPECIFICATION.md state table, "Normal, stowed") over the
    latched doors; the auto-latch cradle duplicated that function and was
    unplaceable (CARGO-01).
  * SHAFT-TILT-4MM: solid -> 4 x 0.5 mm steel tube (24.7 -> 10.8 g each);
    torsional stiffness (D^4 - d^4)/D^4 = 0.68 of solid.
  * PRINT-BELLY-PANEL, SCREW-M3-8-BTN, SEAL-EPDM-2MM -> 0: superseded with the
    keel battery tray at Rev T5 (serenity_assembly.py LEGACY_BATTERY_TRAY).

Mirror discipline (as tools/bom_edit_door_latch.py): assert CSV/JSON row
parity first, edit in memory, write each to a temp file, re-read, assert
parity, os.replace().  Idempotent.

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, 2026-10-19, per AGENTS.md AI attribution.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import csv
import io
import json
import os
import sys
import tempfile
from pathlib import Path

SPEC = Path(__file__).resolve().parent.parent / "current-specification"
CSV_PATH = SPEC / "bom_revT.csv"
JSON_PATH = SPEC / "bom_revT.json"
TAG = "WEIGHT PASS 2026-10-19 (13.0 lbm)"

ZERO = {
    "PRINT-PISTONS": "decorative fairing with no source; dropped (no capability)",
    "FAR-CAGE-AV": "all nodes foil-pouched; cages retired",
    "FAR-GASKET-AV": "all nodes foil-pouched; cages retired",
    "FAR-FAN-40": "all nodes foil-pouched; cages retired",
    "FAR-EMI-VENT-40": "all nodes foil-pouched; cages retired",
    "FAR-FT-PANEL": "all nodes foil-pouched; cage feed-through retired",
    "PRINT-CARGO-CRADLE": "stowed payload held by the winch ratchet over latched doors",
    "PRINT-BELLY-PANEL": "superseded with the keel battery tray (Rev T5)",
    "SCREW-M3-8-BTN": "belly-panel fasteners, superseded (Rev T5)",
    "SEAL-EPDM-2MM": "belly-panel seal, superseded (Rev T5)",
}
SET = {
    "BATT-6S-4000": {
        "Description": ("6S 4000mAh 60C LiPo -- Motion RC Admiral Pro EPR40006PRO "
                        "(hover / high-endurance)"),
        "Unit_Mass_g": "624",
        "note": ("750 g pack -> Admiral Pro 4000 6S 60C, 624 g, 139 x 44 x 48 mm, "
                 "EC5 (US brand of record, no on-pack electronics); figures from a "
                 "search listing, VERIFY on a live page and WEIGH (WBS BATT-01). "
                 "Needs the cradle grown from 142x50x38 (no real 6S 4000 pack is "
                 "38 mm thick; WBS BATT-02) and an XT90/AS150-class battery path, "
                 "not XT60 (WBS PWR-CONN-01)"),
    },
    "SHAFT-TILT-4MM": {
        "Description": ("4mm OD x 0.5mm wall x ~250mm steel tube -- nacelle tilt drive, "
                        "fuselage to wingtip"),
        "Unit_Mass_g": "10.8",
        "note": ("solid 24.7 g -> tube 10.8 g; torsional stiffness 0.68 of solid; "
                 "gears/bushings on the unchanged 4 mm OD"),
    },
}
QTY_BOND = 4


def parity(csv_rows: list[dict], json_rows: list[dict]) -> None:
    a = [(r["Ref"], str(r["Qty"])) for r in csv_rows]
    b = [(r["Ref"], str(r["Qty"])) for r in json_rows]
    if a != b:
        sys.exit("[bom_edit] CSV/JSON parity FAILED -- nothing written")


def edit(rows: list[dict]) -> int:
    n = 0
    for r in rows:
        ref = r["Ref"]
        notes = str(r.get("Notes", ""))
        if TAG in notes and ref not in SET:
            continue
        if TAG in notes and ref in SET and r["Unit_Mass_g"] == SET[ref]["Unit_Mass_g"]:
            continue
        if ref in ZERO and float(r["Qty"] or 0) > 0:
            r["Qty"], r["Total_Mass_g"], r["Est_Total_Price_USD"] = "0", "0", "0.00"
            r["Notes"] = f"*** {TAG}: qty -> 0, {ZERO[ref]} *** " + notes
            n += 1
        elif ref in SET:
            s = SET[ref]
            r["Description"], r["Unit_Mass_g"] = s["Description"], s["Unit_Mass_g"]
            r["Total_Mass_g"] = f"{float(s['Unit_Mass_g']) * float(r['Qty']):.1f}"
            r["Notes"] = f"*** {TAG}: {s['note']} *** " + notes
            n += 1
        elif ref == "FAR-BOND-STRAP" and str(r["Qty"]) != str(QTY_BOND):
            r["Qty"] = str(QTY_BOND)
            r["Total_Mass_g"] = f"{float(r['Unit_Mass_g']) * QTY_BOND:.1f}"
            r["Notes"] = f"*** {TAG}: one per node-stack pouch to chassis *** " + notes
            n += 1
    return n


def main() -> int:
    with open(CSV_PATH, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fields = reader.fieldnames
        csv_rows = list(reader)
    doc = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    parity(csv_rows, doc["items"])
    n_c, n_j = edit(csv_rows), edit(doc["items"])
    if n_c != n_j:
        sys.exit("[bom_edit] CSV and JSON edits diverged -- nothing written")
    parity(csv_rows, doc["items"])
    if not n_c:
        print("[bom_edit] already applied -- no change")
        return 0
    if fields is None:
        sys.exit("[bom_edit] CSV has no header row -- nothing written")
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\r\n")  # file is CRLF
    w.writeheader()
    w.writerows(csv_rows)
    for path, text in ((CSV_PATH, buf.getvalue()),
                       (JSON_PATH, json.dumps(doc, indent=2, ensure_ascii=False) + "\n")):
        fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=path.suffix)
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        os.replace(tmp, path)
    with open(CSV_PATH, newline="", encoding="utf-8") as fh:
        parity(list(csv.DictReader(fh)), json.loads(JSON_PATH.read_text())["items"])
    print(f"[bom_edit] {n_c} rows edited in both {CSV_PATH.name} and {JSON_PATH.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
