#!/usr/bin/env python3
"""check_bom_mesh_sync.py -- the BOM printed-part mass IS the mesh mass.

The BOM is the procurement output, so every printed part's Unit_Mass_g must equal its
measured STL mass: mesh volume x the datasheet SLS density (tools/sls_materials.py),
as priced in current-specification/auw_ledger.json by tools/auw_ledger.py.

Check (default, stdlib only, no meshes needed -- it reads the committed ledger):
    python3 tools/check_bom_mesh_sync.py
Fix (rewrites bom_revU.csv and bom_revU.json from the ledger):
    python3 tools/check_bom_mesh_sync.py --write

Scope: BOM rows with Category "Printed Part" and Qty > 0 whose ref the ledger prices from
a mesh (PRINT rows).  Printed rows the ledger prices elsewhere (the nacelle roll-up) or
that have no mesh yet are listed as NOT COVERED, never silently passed.  The ledger itself
is kept current against the meshes by `tools/auw_ledger.py --check`.

Exit 0 = in sync, 1 = drift (or the CSV and JSON disagree).

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic) under the author's direction, 2026-11-07.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "current-specification"
BOM_CSV = SPEC / "bom_revU.csv"
BOM_JSON = SPEC / "bom_revU.json"
LEDGER = SPEC / "auw_ledger.json"
#: Unit masses are stored to 0.1 g, so half a unit of the last place is the tolerance.
TOL_G = 0.051
STAMP = "Mass synced to the STL mesh at the SLS datasheet density (Rev U, 2026-11-07)"
OLD_STAMP = re.compile(r"Rev U SLS density norm \(2026-11-07\):.*?basis \(converted by the "
                       r"density ratio only\)\. ")
SYNC_STAMP = re.compile(re.escape(STAMP) + r": was [0-9.]+ g\. Unit_Mass_g is authoritative"
                        r"; masses quoted earlier in this note are history\. ")


def fmt(v: float) -> str:
    v = round(v, 1)
    return str(int(v)) if v == int(v) else str(v)


def mesh_masses() -> dict[str, float]:
    """ref -> mesh mass in g.

    Hull-side PRINT rows are TOTALS over every STL of the ref (positive values; divide by the
    BOM Qty).  The 64 mm nacelle's printed parts are UNIT masses (stored negated) from the
    ledger's `nacelle_printed_unit_g`, because the nacelle roll-up prices one nacelle.
    """
    led = json.loads(LEDGER.read_text(encoding="utf-8"))
    tot: dict[str, float] = collections.defaultdict(float)
    for r in led["rows_hover"]:
        if r["kind"] == "PRINT":
            tot[r["ref"]] += r["mass_g"]
    out = dict(tot)
    for ref, unit in led.get("nacelle_printed_unit_g", {}).items():
        out[ref] = -unit
    return out


def target(row: dict, mesh: dict[str, float]) -> float | None:
    """Per-unit mesh mass for a covered BOM row, else None."""
    if row["Category"] != "Printed Part" or float(row["Qty"] or 0) <= 0:
        return None
    ref = row["Ref"]
    if ref not in mesh:
        return None
    return round(-mesh[ref], 1) if mesh[ref] < 0 else round(mesh[ref] / float(row["Qty"]), 1)


def drift(rows: list[dict], mesh: dict[str, float]) -> list[tuple[str, float, float]]:
    out = []
    for r in rows:
        t = target(r, mesh)
        if t is not None and abs(float(r["Unit_Mass_g"] or 0) - t) > TOL_G:
            out.append((r["Ref"], float(r["Unit_Mass_g"] or 0), t))
    return out


def not_covered(rows: list[dict], mesh: dict[str, float]) -> list[str]:
    return [r["Ref"] for r in rows if r["Category"] == "Printed Part"
            and float(r["Qty"] or 0) > 0 and r["Ref"] not in mesh]


def sync_row(r: dict, mesh: dict[str, float]) -> bool:
    t = target(r, mesh)
    if t is None or abs(float(r["Unit_Mass_g"] or 0) - t) <= TOL_G:
        return False
    old = fmt(float(r["Unit_Mass_g"] or 0))
    note = OLD_STAMP.sub("", r["Notes"])
    note = SYNC_STAMP.sub("", note)
    r["Notes"] = (note + ("" if note.endswith(" ") or not note else " ")
                  + f"{STAMP}: was {old} g. Unit_Mass_g is authoritative; masses quoted "
                  "earlier in this note are history. ")
    r["Unit_Mass_g"] = fmt(t)
    r["Total_Mass_g"] = fmt(t * float(r["Qty"]))
    return True


def load_csv() -> tuple[list[dict], list[str]]:
    with BOM_CSV.open(encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        return list(rd), list(rd.fieldnames or [])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--write", action="store_true",
                    help="rewrite bom_revU.csv/.json from the ledger meshes")
    args = ap.parse_args(argv)
    mesh = mesh_masses()
    rows, fields = load_csv()
    jdoc = json.loads(BOM_JSON.read_text(encoding="utf-8"))
    items = jdoc["items"]
    if args.write:
        n = sum(sync_row(r, mesh) for r in rows)
        m = sum(sync_row(r, mesh) for r in items)
        with BOM_CSV.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")  # repo BOM is LF
            w.writeheader()
            w.writerows(rows)
        BOM_JSON.write_text(json.dumps(jdoc, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
        print(f"check_bom_mesh_sync: synced {n} CSV rows and {m} JSON rows to the meshes")
    bad = drift(rows, mesh)
    for ref, have, want in bad:
        print(f"DRIFT  {ref:34s} BOM {have:8.1f} g   mesh {want:8.1f} g  ({have - want:+.1f})")
    jbad = drift(items, mesh)
    if sorted(bad) != sorted(jbad):
        print("DRIFT  bom_revU.csv and bom_revU.json disagree on printed-part masses")
        bad = bad or jbad or [("csv-vs-json", 0.0, 0.0)]
    nc = not_covered(rows, mesh)
    if nc:
        print(f"NOT COVERED by a mesh row in the ledger ({len(nc)}): " + ", ".join(nc))
    if bad:
        print("check_bom_mesh_sync: FAIL -- run tools/check_bom_mesh_sync.py --write")
        return 1
    print("check_bom_mesh_sync: PASS -- BOM printed-part masses match the meshes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
