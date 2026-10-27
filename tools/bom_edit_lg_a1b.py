#!/usr/bin/env python3
"""LG-LOADPATH-A1B BOM edit: balanced-couple gear (owner 2026-10-27).

Plan docs/plans/2026-10-27-001-feat-lg-option-a-balanced-couple-plan.md;
sizing tools/landing_gear_r6_sizing.py a1b_sizing(); geometry
airframe/openscad/fuselage/canonical_leg_r6_3_0in.scad (LOADPATH "A1B").
  * LG-DUCTILE-WIRE -- retired (Qty 0): the R6 bowed ductile wire is replaced
    by the 6061-T6 axial tension fuse (owner decision 2026-10-26).
  * LG-SPRING-WIRE -- re-specified A228 O3.37 x 34 mm, 2 per leg (8).
  * New: LG-A1B-FUSE (8), LG-A1B-SLEEVE (4), LG-A1B-CAGE (4), LG-A1B-PIN (20),
    LG-A1B-CF-CHEEK (8).
Masses: CF cheeks from the rendered a1b_backbone() volume (10,089 mm^3 per leg
pair) x 1.52 g/cm^3 [REF-MAT-011]; 6061 parts x 2.70 g/cm^3 [REF-MAT-007];
A228 x 7.90 g/cm^3 proxy [REF-MAT-006] (as tools/lg_bellcrank_fbd.py).
Same CSV/JSON mirror discipline as tools/bom_edit_door_rework.py: parity
asserted before and after, temp-file writes, os.replace().  Re-running is a
no-op once LG-A1B-FUSE exists.

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, 2026-10-27, per AGENTS.md section 3 AI attribution.
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
PLAN = "docs/plans/2026-10-27-001-feat-lg-option-a-balanced-couple-plan.md"

UPDATES = {
    "LG-DUCTILE-WIRE": {
        "Qty": "0", "Total_Mass_g": "0", "Est_Total_Price_USD": "0.00",
        "Notes": (f"RETIRED 2026-10-27 (LG-LOADPATH-A1B, {PLAN}): the R6 same-side bowed "
                  "ductile wire put ~2P through the hip pin (docs/LG_BELLCRANK_LOAD_PATH_STUDY.md "
                  "SS1). Replaced by LG-A1B-FUSE. Row kept for traceability."),
    },
    "LG-SPRING-WIRE": {
        "Description": "Music-wire spring, ASTM A228, O3.37 x 34 mm -- A1B spring row, 2 per leg",
        "Qty": "8", "Unit_Mass_g": "2.40", "Total_Mass_g": "19.2",
        "Notes": ("A1B 2026-10-27 (tools/landing_gear_r6_sizing.py a1b_sizing): 1,934 N per wire, "
                  "span 20 mm, length 34 mm. O3.37 is not a stock music-wire size: buy the next "
                  "larger stock and re-run the sizing at that diameter before ordering. "
                  "[REF-MAT-008]"),
    },
}

NEW_ROWS = [
    {"Ref": "LG-A1B-FUSE",
     "Description": "6061-T6 axial tension fuse, O4.60 gauge x 33.9 mm, eye ends -- 2 per leg",
     "Category": "Structural Hardware", "Qty": "8", "Unit_Mass_g": "2.4", "Total_Mass_g": "19.4",
     "Supplier": "McMaster-Carr", "Supplier_PN_or_Search": "6061-T6 rod 3/16 in (4.76 mm), turn gauge to O4.60",
     "Est_Unit_Price_USD": "3.00", "Est_Total_Price_USD": "24.00",
     "Notes": ("Plateau 4,593 N per fuse (Sy 276 MPa) [REF-MAT-007]; gauge from 1.5 x stroke / "
               "17 % elongation (tools/lg_fuse_material.py). Plateau ends at necking -- LG-15 "
               "bench firing shall confirm before flight. Buy +4 spares.")},
    {"Ref": "LG-A1B-SLEEVE",
     "Description": "6061-T6 reversing sleeve, OD 8 x ID 5.6 x 43 mm, ductile push side -- 1 per leg",
     "Category": "Structural Hardware", "Qty": "4", "Unit_Mass_g": "3.0", "Total_Mass_g": "12.0",
     "Supplier": "McMaster-Carr", "Supplier_PN_or_Search": "6061-T6 tube 5/16 in OD, bore to ID 5.6",
     "Est_Unit_Price_USD": "4.00", "Est_Total_Price_USD": "16.00",
     "Notes": ("Compressive-yield margin 1.54 at the 4,593 N plateau (tools/lg_couple_options.py); "
               "buckling not checked -- the 6061 modulus is not in REF-MAT-007's applied section "
               "(requires verification).")},
    {"Ref": "LG-A1B-CAGE",
     "Description": "6061-T6 flat reversing cage, 1 mm side plates, 17.5 x 6 x 43 mm, spring pull side -- 1 per leg",
     "Category": "Structural Hardware", "Qty": "4", "Unit_Mass_g": "4.1", "Total_Mass_g": "16.4",
     "Supplier": "In-house / SendCutSend", "Supplier_PN_or_Search": "6061-T6 sheet 0.040 in, cut + fold",
     "Est_Unit_Price_USD": "5.00", "Est_Total_Price_USD": "20.00",
     "Notes": "Flat: the spring bow sweeps only in the swing plane (leg SCAD a1b_members)."},
    {"Ref": "LG-A1B-PIN",
     "Description": "6061-T6 pin O4 mm (hip 1 + crank 2 + anchor 2 per leg), with retaining clips",
     "Category": "Hardware", "Qty": "20", "Unit_Mass_g": "0.64", "Total_Mass_g": "12.8",
     "Supplier": "McMaster-Carr", "Supplier_PN_or_Search": "6061-T6 rod 4 mm, cut + groove for e-clips",
     "Est_Unit_Price_USD": "1.00", "Est_Total_Price_USD": "20.00",
     "Notes": "Hip pin carries the foot force only: double-shear margin 3.62, liner bearing 2.31 [REF-MAT-007]."},
    {"Ref": "LG-A1B-CF-CHEEK",
     "Description": "CF backbone cheek, 1/8 in quasi-iso plate, waterjet -- 2 per leg",
     "Category": "Structural Hardware", "Qty": "8", "Unit_Mass_g": "7.65", "Total_Mass_g": "61.2",
     "Supplier": "Rock West Composites", "Supplier_PN_or_Search": "204-xx Carbon Fiber Plate, Quasi-Iso, 1/8 in",
     "Est_Unit_Price_USD": "6.00", "Est_Total_Price_USD": "48.00",
     "Notes": ("[REF-MAT-011]: 5.58e4 psi compressive used as a bearing proxy (no published bearing; "
               "NCAMP analogs higher [REF-MAT-012/-013]). LG-11 bearing coupons from the same sheet "
               "shall precede flight. Fallback Toray TC1225/T700GC RTL [REF-MAT-013/-014]. Pin edge "
               "distance requires a cited minimum (open). Max operating 175-199 F.")},
]


def parity(csv_rows: list[dict], json_rows: list[dict]) -> None:
    """Abort unless the CSV and JSON hold the same rows in the same order."""
    if len(csv_rows) != len(json_rows):
        sys.exit(f"parity: row count differs csv={len(csv_rows)} json={len(json_rows)}")
    if [r["Ref"] for r in csv_rows] != [r["Ref"] for r in json_rows]:
        sys.exit("parity: Ref order/set differs")


def edit(rows: list[dict]) -> list[dict]:
    """Retire the R6 ductile wire, re-spec the spring wire, add the A1B rows."""
    out = []
    for r in rows:
        if r["Ref"] in UPDATES:
            r = {**r, **UPDATES[r["Ref"]]}
        out.append(r)
        if r["Ref"] == "LG-DUCTILE-WIRE":
            out.extend({k: row.get(k, "") for k in r} for row in NEW_ROWS)
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
    if any(r["Ref"] == "LG-A1B-FUSE" for r in csv_rows):
        print("LG-A1B-FUSE already present -- nothing to do")
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
    print("LG A1B BOM rows written; parity holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
