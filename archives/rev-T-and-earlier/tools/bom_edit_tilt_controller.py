#!/usr/bin/env python3
"""Swap the tilt-controller BOM row: retire LS-TILT-TC, add OSESC-TILT-TC.

One-shot edit for plan docs/plans/2026-09-17-001-feat-tilt-controller-open-
secure-esc-build-plan.md (U8, KTD14). It applies the mirror discipline from
docs/solutions/logic-errors/bom-csv-json-mirror-drift-and-in-place-rewrite-
truncation.md to BOTH current-specification/bom_revS.csv and bom_revS.json:

  1. assert CSV/JSON parity (row count, Ref set, no overflow key) BEFORE
     editing -- abort on mismatch, nothing written;
  2. edit rows in memory;
  3. write each file to a temp path next to the target, re-read it, assert
     parity and the absence of a None/"null" overflow key, then os.replace().

Rows touched:
  * LS-TILT-TC        -> Qty 0, totals 0, note RETIRED (row kept for the record)
  * OSESC-TILT-TC     -> new, qty 2, the Open-Secure-ESC build (REF-ESC-001)
  * GM-TILT-20D       -> note: controller pointer re-pointed
  * SOL-TILT-BRAKE    -> note: driver is on the controller; hold-in voltage item

Author: Claude Opus 5 (Anthropic) under the direction of Steve Griffing,
PE(CSE), CISSP-ISSEP, CPP, 2026-09-17. AI-generated. Run once; re-running is
a no-op once OSESC-TILT-TC exists.
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

NEW_ROW = {
    "Ref": "OSESC-TILT-TC",
    "Description": (
        "Nacelle tilt controller -- Open-Secure-ESC build 6S/10A "
        "BRUSHED_CAN_485_isolation (DRV8874-Q1 bridge, TPS54560B buck motor "
        "rail, TPL7407L brake driver, remote AEAT-8800 header, isolated "
        "CAN-FD + RS-485, OPTIGA Trust M)"
    ),
    "Category": "Avionics",
    "Qty": "2",
    "Unit_Mass_g": "12",
    "Total_Mass_g": "24",
    "Supplier": "JLCPCB (fab from the Open-Secure-ESC repo) + hand assembly",
    "Supplier_PN_or_Search": "Open-Secure-ESC/builds/6s/10A/BRUSHED_CAN_485_isolation/",
    "Est_Unit_Price_USD": "30.00",
    "Est_Total_Price_USD": "60.00",
    "Notes": (
        "2026-09-17 (docs/plans/2026-09-17-001-feat-tilt-controller-open-secure-esc-build-plan.md, "
        "REF-ESC-001): replaces LS-TILT-TC -- the controller is a build of the project's "
        "own Open-Secure-ESC platform, not a LibreServo variant. State: schematic ERC "
        "0/0, BOM walked from that repo's decision matrix, NO PCB yet (its TODO 18). "
        "Host constraints carried by the build: 42.9 x 36.5 mm outline, 4 mm parts on the "
        "web-facing side, bare back, connectors aft/inboard (PRINT-TILT-BRACKET card-edge "
        "rails, Rev T5e). Mass 12 g is an ESTIMATE carried from the retired row until a "
        "populated board is weighed; price carried likewise until quoted. Feeds: F_TILT_P/S "
        "3 A. The solenoid (SOL-TILT-BRAKE) and the AEAT-8800 sensor daughter (ENC-DAUGHTER, "
        "docs/TILT_ACTUATOR_SELECTION.md section 7) are separate rows/items."
    ),
}

RETIRE_NOTE = (
    "RETIRED 2026-09-17 -- replaced by OSESC-TILT-TC (Open-Secure-ESC build, REF-ESC-001); "
    "the LibreServo_v4.1-TC change request is SUPERSEDED. Qty 0, row kept for the record. "
    "Original note: "
)


def parity(csv_rows: list[dict], json_rows: list[dict]) -> None:
    """Abort unless the two mirrors agree row-for-row on Ref and carry no overflow."""
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
    if any(r["Ref"] == "OSESC-TILT-TC" for r in csv_rows):
        print("OSESC-TILT-TC already present -- nothing to do")
        return 0

    def edit(rows: list[dict]) -> list[dict]:
        out = []
        for r in rows:
            r = dict(r)
            if r["Ref"] == "LS-TILT-TC":
                r["Qty"] = "0"
                r["Total_Mass_g"] = "0"
                r["Est_Total_Price_USD"] = "0.00"
                r["Notes"] = RETIRE_NOTE + r["Notes"]
            elif r["Ref"] == "GM-TILT-20D":
                r["Notes"] = r["Notes"].replace(
                    "LibreServo_v4.1-TC",
                    "the Open-Secure-ESC tilt controller (OSESC-TILT-TC, REF-ESC-001)",
                )
            elif r["Ref"] == "SOL-TILT-BRAKE":
                r["Notes"] = r["Notes"] + (
                    " 2026-09-17: driven by the TPL7407L low-side driver on OSESC-TILT-TC "
                    "(coil between the 6.5 V motor rail and the sink; clamp to VBAT); BRK-4 "
                    "must also record the hold-in / dropout voltage so the controller's "
                    "rail-droop rule has a threshold."
                )
            out.append(r)
            if r["Ref"] == "LS-TILT-TC":
                out.append(dict(NEW_ROW))
        return out

    new_csv = edit(csv_rows)
    new_json = edit(json_rows)

    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\r\n")  # the file is CRLF
    w.writeheader()
    for r in new_csv:
        w.writerow(r)
    csv_text = buf.getvalue()
    doc["items"] = new_json
    json_text = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"

    # Re-read from the text before touching disk.
    check_csv = list(csv.DictReader(io.StringIO(csv_text)))
    check_json = json.loads(json_text)["items"]
    parity(check_csv, check_json)
    if len(check_csv) != len(csv_rows) + 1:
        sys.exit("post-edit: unexpected row count")

    atomic_write(CSV_PATH, csv_text)
    atomic_write(JSON_PATH, json_text)

    # Re-read from disk and prove parity once more.
    _, c2, d2 = load()
    parity(c2, d2["items"])
    print(f"ok: {len(c2)} rows in both mirrors; OSESC-TILT-TC added, LS-TILT-TC retired")
    return 0


if __name__ == "__main__":
    sys.exit(main())
