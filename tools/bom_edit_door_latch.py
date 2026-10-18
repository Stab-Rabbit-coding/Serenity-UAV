#!/usr/bin/env python3
"""Add the cargo-door positive-latch mechanism to the BOM (docs/CARGO_DOOR_LATCH_SPEC.md).

Same CSV/JSON mirror discipline as tools/bom_edit_door_gateway.py /
tools/bom_edit_tilt_controller.py:
  1. assert CSV/JSON parity before editing -- abort on mismatch, nothing written;
  2. edit rows in memory;
  3. write each file to a temp path, re-read it, assert parity, then os.replace().

Rows added (Rev A, 2026-09-21):
  * PRINT-DOOR-LATCH-BRACKET  -> door_latch_bracket_{port,stbd}.stl, CF-PETG, 2 off
  * PRINT-DOOR-HORN           -> door_horn.stl, CF-PETG, 2 off
  * PIN-3X10                  -> bell-crank pivot pin, steel, 2 off

No existing row's Qty changes -- the pushrod (existing "Steel pushrod 2mm,
Z-bend ends" procurement line) and M3 heat-set inserts/screws are already
qty-tracked generically elsewhere in the BOM and are noted, not duplicated.

Author: Claude Sonnet 5 (Anthropic) under the direction of Steve Griffing,
PE(CSE), CISSP-ISSEP, CPP, 2026-09-21. AI-generated. Run once; re-running is
a no-op once PRINT-DOOR-LATCH-BRACKET exists.
"""

from __future__ import annotations

import csv
import io
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = HERE.parent / "current-specification"
CSV_PATH = SPEC / "bom_revS.csv"
JSON_PATH = SPEC / "bom_revS.json"

SPEC_DOC = "docs/CARGO_DOOR_LATCH_SPEC.md"

BRACKET_ROW = {
    "Ref": "PRINT-DOOR-LATCH-BRACKET",
    "Description": (
        "door_latch_bracket_{port,stbd}.stl -- bell-crank + pivot bracket + mortise, "
        "cargo door positive latch, CF-PETG"
    ),
    "Category": "Printed Part",
    "Qty": "2",
    "Unit_Mass_g": "3.55",
    "Total_Mass_g": "7.10",
    "Supplier": "In-house 3D print",
    "Supplier_PN_or_Search": "CF-PETG (20% CF) -- see FIL-CF-PETG",
    "Est_Unit_Price_USD": "0.00",
    "Est_Total_Price_USD": "0.00",
    "Notes": (
        f"Rev A 2026-09-21 ({SPEC_DOC}): closes the DOOR-LATCH finding "
        "(docs/CARGO_DOOR_GATEWAY_SPEC.md) -- servo-driven bell-crank hook engages a "
        "mortise on this FIXED bracket; the hook/lip mechanical interference, not the "
        "SG90 gear train, carries the door-closed load (governing case: aero pressure at "
        "V_max=87kt, REF-FAA-002; SG90 stall torque 0.177 N.m < 0.202 N.m door-opening "
        "moment even at FOS=1). FOS_bearing=10.4, FOS_shear~3.0 (order-of-magnitude, FDM "
        "anisotropic -- bench pull-test required, DOOR-LATCH-1). One bracket per door, "
        "mounted at Y=39.33 (2nd hinge knuckle station). Print with a >=1.5mm hook-root "
        "fillet (not modelled in the CSG source -- DOOR-LATCH-4) and orient so the "
        "governing shear plane runs with the layer lines."
    ),
}

HORN_ROW = {
    "Ref": "PRINT-DOOR-HORN",
    "Description": "door_horn.stl -- door-panel control horn for the latch/drive pushrod, CF-PETG",
    "Category": "Printed Part",
    "Qty": "2",
    "Unit_Mass_g": "0.92",
    "Total_Mass_g": "1.84",
    "Supplier": "In-house 3D print",
    "Supplier_PN_or_Search": "CF-PETG (20% CF) -- see FIL-CF-PETG",
    "Est_Unit_Price_USD": "0.00",
    "Est_Total_Price_USD": "0.00",
    "Notes": (
        f"Rev A 2026-09-21 ({SPEC_DOC} section 2): bonded to each door panel's inner "
        "face at the bracket's Y station; the 2mm steel pushrod (existing Z-bend "
        "procurement row) runs from here to the bell-crank drive arm. One per door."
    ),
}

PIN_ROW = {
    "Ref": "PIN-3X10",
    "Description": "3mm x 10mm SS dowel pin -- door-latch bell-crank pivot",
    "Category": "Hardware",
    "Qty": "2",
    "Unit_Mass_g": "0.6",
    "Total_Mass_g": "1.2",
    "Supplier": "Amazon / McMaster",
    "Supplier_PN_or_Search": "3mm x 10mm stainless dowel pin",
    "Est_Unit_Price_USD": "0.50",
    "Est_Total_Price_USD": "1.00",
    "Notes": (
        f"Rev A 2026-09-21 ({SPEC_DOC} section 3): bell-crank pivot, one per door-latch "
        "bracket. Same class as the door-hinge PIN-3X18 stock, shorter length (no "
        "4-knuckle span to cross). Reaction ~135 N resultant, steel FOS large (not "
        "governing -- section 3)."
    ),
}


def parity(csv_rows: list[dict], json_rows: list[dict]) -> None:
    if len(csv_rows) != len(json_rows):
        sys.exit(f"parity: row count differs csv={len(csv_rows)} json={len(json_rows)}")
    cr = [r["Ref"] for r in csv_rows]
    jr = [r["Ref"] for r in json_rows]
    if cr != jr:
        sys.exit(f"parity: Ref order/set differs: {set(cr) ^ set(jr)}")
    for r in csv_rows:
        if None in r or "null" in r:
            sys.exit(f"parity: CSV overflow key on {r['Ref']}")
    for r in json_rows:
        if "null" in r or None in r:
            sys.exit(f"parity: JSON overflow key on {r['Ref']}")


def load() -> tuple[list[str], list[dict], dict]:
    with CSV_PATH.open(newline="") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        csv_rows = list(reader)
    doc = json.loads(JSON_PATH.read_text())
    return fields, csv_rows, doc


def atomic_write(path: Path, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    with os.fdopen(fd, "w", newline="") as f:
        f.write(text)
    os.replace(tmp, path)


def main() -> int:
    fields, csv_rows, doc = load()
    json_rows = doc["items"]
    parity(csv_rows, json_rows)
    if any(r["Ref"] == "PRINT-DOOR-LATCH-BRACKET" for r in csv_rows):
        print("PRINT-DOOR-LATCH-BRACKET already present -- nothing to do")
        return 0

    def edit(rows: list[dict]) -> list[dict]:
        out = []
        for r in rows:
            out.append(r)
            # insert right after the gateway tray row so the door-mechanism
            # parts cluster together in the file
            if r["Ref"] == "PRINT-GW-DOOR-TRAY":
                out.append(dict(BRACKET_ROW))
                out.append(dict(HORN_ROW))
                out.append(dict(PIN_ROW))
        return out

    new_csv = edit(csv_rows)
    new_json = edit(json_rows)

    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\r\n")
    w.writeheader()
    for r in new_csv:
        w.writerow(r)
    csv_text = buf.getvalue()
    doc["items"] = new_json
    json_text = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"

    check_csv = list(csv.DictReader(io.StringIO(csv_text)))
    check_json = json.loads(json_text)["items"]
    parity(check_csv, check_json)
    if len(check_csv) != len(csv_rows) + 3:
        sys.exit("post-edit: unexpected row count")

    atomic_write(CSV_PATH, csv_text)
    atomic_write(JSON_PATH, json_text)

    _, c2, d2 = load()
    parity(c2, d2["items"])
    print(
        f"ok: {len(c2)} rows in both mirrors; PRINT-DOOR-LATCH-BRACKET + "
        "PRINT-DOOR-HORN + PIN-3X10 added"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
