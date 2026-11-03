#!/usr/bin/env python3
"""DOOR-REWORK BOM edit: lapped cargo doors, ONE latch, crank split from bracket.

docs/CARGO_DOOR_LATCH_SPEC.md Rev B (owner 2026-10-19, built 2026-10-26):
  * PRINT-DOOR-LATCH-BRACKET -- now the FIXED pivot bracket only (port carries
    the mortise; starboard is drive-only).  Rev A unioned the moving bell-crank
    into it, so the printed part could never turn.  Masses re-measured from
    door_latch_bracket_{port,stbd}.stl (volume x 1.05 g/cm^3, the
    tools/auw_ledger.py RHO_PRINT): port 2.33 g, stbd 1.28 g.
  * PRINT-DOOR-LATCH-CRANK (new) -- the bell-crank, its own part on the
    PIN-3X10 pivot: port (latch + hook) 0.96 g, stbd (drive-only) 0.62 g.

Same CSV/JSON mirror discipline as tools/bom_edit_door_latch.py: parity
asserted before editing (abort, nothing written, on a mismatch), rows edited
in memory, each file written to a temp path, re-read, parity re-asserted,
then os.replace().  Re-running is a no-op once PRINT-DOOR-LATCH-CRANK exists.

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, 2026-10-26, per AGENTS.md section 3 AI attribution.
License: MIT (SPDX-License-Identifier: MIT) -- see tools/LICENSE.
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
CSV_PATH = SPEC / "bom_revT.csv"
JSON_PATH = SPEC / "bom_revT.json"
SPEC_DOC = "docs/CARGO_DOOR_LATCH_SPEC.md"

BRACKET_UPDATE = {
    "Description": (
        "door_latch_bracket_{port,stbd}.stl -- FIXED pivot bracket (pin seat); port "
        "carries the latch mortise, stbd is drive-only, CF-PETG"
    ),
    "Unit_Mass_g": "1.81",
    "Total_Mass_g": "3.61",
    "Notes": (
        f"Rev B 2026-10-26 ({SPEC_DOC} section 0a): ONE latch (port) holds both "
        "lapped doors; port 2.33 g (mortise), stbd 1.28 g (no mortise), measured "
        "from the STLs. The bell-crank is now its own part (PRINT-DOOR-LATCH-CRANK). "
        "Bonded to the flank at the 2nd hinge-knuckle station, pivot 2 mm inboard "
        "of the hinge line (clear of the payload keep-out)."
    ),
}

CRANK_ROW = {
    "Ref": "PRINT-DOOR-LATCH-CRANK",
    "Description": (
        "door_latch_crank_{port,stbd}.stl -- door bell-crank on the PIN-3X10 pivot; "
        "port has the latch hook (7 x 3.5 mm root), stbd is drive-only, CF-PETG"
    ),
    "Category": "Printed Part",
    "Qty": "2",
    "Unit_Mass_g": "0.79",
    "Total_Mass_g": "1.58",
    "Supplier": "In-house 3D print",
    "Supplier_PN_or_Search": "CF-PETG (20% CF) -- see FIL-CF-PETG",
    "Est_Unit_Price_USD": "0.00",
    "Est_Total_Price_USD": "0.00",
    "Notes": (
        f"Rev B 2026-10-26 ({SPEC_DOC} section 0a): port 0.96 g, stbd 0.62 g. Port hook "
        "carries both doors: FOS_shear 2.97, FOS_bearing 8.8 at FOS 3.0 on the 87 kt "
        "door moment (order-of-magnitude, FDM anisotropic -- bench pull test, "
        "DOOR-LATCH-1). Print with the >=1.5 mm hook-root fillet."
    ),
}


def parity(csv_rows: list[dict], json_rows: list[dict]) -> None:
    """Abort unless the CSV and JSON hold the same rows in the same order."""
    if len(csv_rows) != len(json_rows):
        sys.exit(f"parity: row count differs csv={len(csv_rows)} json={len(json_rows)}")
    if [r["Ref"] for r in csv_rows] != [r["Ref"] for r in json_rows]:
        sys.exit("parity: Ref order/set differs")


def edit(rows: list[dict]) -> list[dict]:
    """Update the bracket row and insert the crank row right after it."""
    out = []
    for r in rows:
        if r["Ref"] == "PRINT-DOOR-LATCH-BRACKET":
            r = {**r, **BRACKET_UPDATE}
            out.append(r)
            out.append({k: CRANK_ROW.get(k, "") for k in r})
            continue
        out.append(r)
    return out


def atomic_write(path: Path, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    with os.fdopen(fd, "w", newline="") as f:
        f.write(text)
    os.replace(tmp, path)


def main() -> int:
    with CSV_PATH.open(newline="") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        csv_rows = list(reader)
    doc = json.loads(JSON_PATH.read_text())
    parity(csv_rows, doc["items"])
    if any(r["Ref"] == "PRINT-DOOR-LATCH-CRANK" for r in csv_rows):
        print("PRINT-DOOR-LATCH-CRANK already present -- nothing to do")
        return 0
    new_csv = edit(csv_rows)
    doc["items"] = edit(doc["items"])
    parity(new_csv, doc["items"])
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\r\n")
    w.writeheader()
    w.writerows(new_csv)
    atomic_write(CSV_PATH, buf.getvalue())
    atomic_write(JSON_PATH, json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    with CSV_PATH.open(newline="") as f:
        parity(list(csv.DictReader(f)), json.loads(JSON_PATH.read_text())["items"])
    print(f"updated {CSV_PATH.name} / {JSON_PATH.name}: bracket row revised, crank row added")
    return 0


if __name__ == "__main__":
    sys.exit(main())
