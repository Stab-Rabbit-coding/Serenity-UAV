#!/usr/bin/env python3
"""Wire the cargo-door servo gateway into the BOM (docs/CARGO_DOOR_GATEWAY_SPEC.md).

One-shot edit applying the mirror discipline from
docs/solutions/logic-errors/bom-csv-json-mirror-drift-and-in-place-rewrite-
truncation.md to BOTH current-specification/bom_revS.csv and bom_revS.json
(same procedure as tools/bom_edit_tilt_controller.py):

  1. assert CSV/JSON parity (row count, Ref set, no overflow key) BEFORE
     editing -- abort on mismatch, nothing written;
  2. edit rows in memory;
  3. write each file to a temp path next to the target, re-read it, assert
     parity, then os.replace().

Rows touched (Rev A, 2026-09-21):
  * CAN-PERIPH-GW-DOOR  -> new: one SKIPPER-CAN-PERIPH-GW-PCB at N_STACKS=1
  * PRINT-GW-DOOR-TRAY  -> new: gateway_door_tray.stl (CF-PETG, 5.0 g)
  * SERVO-CARGO         -> Qty 2 -> 3 (port door, stbd door, release; D-GW-2)
  * DRV8833-CARGO       -> Qty 0, RETIRED (servos are gateway-driven)
  * PRINT-DRV8833-TRAY  -> Qty 0, RETIRED with it

Author: Claude Opus 5 (Anthropic) under the direction of Steve Griffing,
PE(CSE), CISSP-ISSEP, CPP, 2026-09-21. AI-generated. Run once; re-running is
a no-op once CAN-PERIPH-GW-DOOR exists.
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

SPEC_DOC = "docs/CARGO_DOOR_GATEWAY_SPEC.md"

GW_ROW = {
    "Ref": "CAN-PERIPH-GW-DOOR",
    "Description": (
        "Cargo-door servo gateway GW-CARGO-DOOR -- SKIPPER-CAN-PERIPH-GW-PCB built at "
        "N_STACKS=1 (MSPM0G3518-Q1 + SLB9672 TPM + ISOW1044 CAN-FD + ISOW1412 RS-485), "
        "hosts the 3 SG90-class door/release servos on J_FLEX"
    ),
    "Category": "Avionics",
    "Qty": "1",
    "Unit_Mass_g": "6",
    "Total_Mass_g": "6",
    "Supplier": "JLCPCB (fab from avionics/kicad/CAN-PERIPH-GW-1) + hand assembly",
    "Supplier_PN_or_Search": "avionics/kicad/CAN-PERIPH-GW-1/ (N_STACKS=1 layout)",
    "Est_Unit_Price_USD": "28.00",
    "Est_Total_Price_USD": "28.00",
    "Notes": (
        f"Rev A 2026-09-21 ({SPEC_DOC}): the SG90 door/release servos are bus-networked "
        "trunk actuators (avionics/WBS.md 1.9.2, 2026-09-20) and this is the node that "
        "drives them -- their own N_STACKS=1 board, NOT a lane on the winch gateway "
        "(CARGO_WINCH_SPECIFICATION.md section 5.1 already uses every J_FLEX pin; D-GW-1). "
        "Primary: OpenServoCore osc-native chain on FLEX_UART_TX/RX; fallback: stock SG90 "
        "PWM on FLEX_PWM_IO (PA25 TIMA0_C3, port door) + FLEX_BSHOT_IO (PA26 TIMG8_C0, "
        "stbd door), release on FLEX_TTL_GPIO. Servo power is a fused 6 V rail branch, "
        "not J_FLEX +5V. Mounts in PRINT-GW-DOOR-TRAY on 4 slab bosses (Rev T5f shell) at "
        "hull X_CL / Y -17..-2 / Z 10..44, standing transverse, component side aft. "
        "Mass 6 g and price are ESTIMATES until a populated board is weighed/quoted. "
        "Outline 49.0 x 25.5 mm, no mounting holes (card-edge rails). No BOM rows exist "
        "yet for the two nacelle gateway boards (GW-PORT/GW-STBD) -- separate item."
    ),
}

TRAY_ROW = {
    "Ref": "PRINT-GW-DOOR-TRAY",
    "Description": (
        "gateway_door_tray.stl -- card-edge tray for the cargo-door servo gateway "
        "(CAN-PERIPH-GW-DOOR), CF-PETG, 4 x M3 to belly-slab bosses, keeper + pigtail tie slots"
    ),
    "Category": "Printed Part",
    "Qty": "1",
    "Unit_Mass_g": "5.0",
    "Total_Mass_g": "5.0",
    "Supplier": "In-house 3D print",
    "Supplier_PN_or_Search": "CF-PETG (20% CF) -- see FIL-CF-PETG",
    "Est_Unit_Price_USD": "0.00",
    "Est_Total_Price_USD": "0.00",
    "Notes": (
        f"Rev T5f 2026-09-21 ({SPEC_DOC} section 5; "
        "airframe/openscad/fuselage/cargo/gateway_door_tray.scad): 5.4 mm base slab "
        "52.2 x 15.25 mm on four 7 x 7 mm bosses (rear row counterbored under the board, "
        "front row exposed), side rails 1.6 mm + 2 mm lips, board drops in from above; "
        "exported volume 4 729 mm3 x 1.05 g/cm3. Print slab flat, rails up, 4 perimeters, "
        "30% gyroid. Hardware: 4 x RX-M3x5.7 inserts + 4 x M3x8 SHCS (add to those rows at "
        "order); 3 cable ties."
    ),
}

SERVO_NOTE = (
    " 2026-09-21 (" + SPEC_DOC + ", D-GW-2): Qty 2 -> 3 -- the doors are two INDEPENDENT "
    "piano-hinged halves (Rev R1b), one actuator each, plus the release; all three are "
    "driven by CAN-PERIPH-GW-DOOR (osc-native chain, or PWM fallback with stock SG90s), "
    "NOT by DRV8833-CARGO (retired) or TACCO GPIO. The old 'Ch-A/Ch-B' wording is "
    "historical. Owner to confirm the two-actuator reading (GW-DOOR-4)."
)

RETIRE_NOTE = (
    "RETIRED 2026-09-21 -- the door/release servos are driven by CAN-PERIPH-GW-DOOR "
    "(" + SPEC_DOC + " D-GW-1/D-GW-3); no local H-bridge. Qty 0, row kept for the record. "
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
    if any(r["Ref"] == "CAN-PERIPH-GW-DOOR" for r in csv_rows):
        print("CAN-PERIPH-GW-DOOR already present -- nothing to do")
        return 0

    def edit(rows: list[dict]) -> list[dict]:
        out = []
        for r in rows:
            r = dict(r)
            if r["Ref"] == "SERVO-CARGO":
                r["Qty"] = "3"
                r["Total_Mass_g"] = str(3 * int(r["Unit_Mass_g"]))
                r["Est_Total_Price_USD"] = f"{3 * float(r['Est_Unit_Price_USD']):.2f}"
                r["Description"] = (
                    "SG90 micro servo -- port door (1x) + stbd door (1x) + payload release "
                    "(1x), OpenServoCore control board, driven by CAN-PERIPH-GW-DOOR"
                )
                r["Notes"] = r["Notes"] + SERVO_NOTE
            elif r["Ref"] in ("DRV8833-CARGO", "PRINT-DRV8833-TRAY"):
                r["Qty"] = "0"
                r["Total_Mass_g"] = "0"
                r["Est_Total_Price_USD"] = "0.00"
                r["Notes"] = RETIRE_NOTE + r["Notes"]
            out.append(r)
            # the gateway row follows the servo row; the tray row follows the chin shelf
            if r["Ref"] == "SERVO-CARGO":
                out.append(dict(GW_ROW))
            if r["Ref"] == "PRINT-CHIN-SHELF":
                out.append(dict(TRAY_ROW))
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

    check_csv = list(csv.DictReader(io.StringIO(csv_text)))
    check_json = json.loads(json_text)["items"]
    parity(check_csv, check_json)
    if len(check_csv) != len(csv_rows) + 2:
        sys.exit("post-edit: unexpected row count")

    atomic_write(CSV_PATH, csv_text)
    atomic_write(JSON_PATH, json_text)

    _, c2, d2 = load()
    parity(c2, d2["items"])
    print(
        f"ok: {len(c2)} rows in both mirrors; CAN-PERIPH-GW-DOOR + PRINT-GW-DOOR-TRAY "
        "added, SERVO-CARGO qty 3, DRV8833-CARGO + PRINT-DRV8833-TRAY retired"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
