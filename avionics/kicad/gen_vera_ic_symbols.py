#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_vera_ic_symbols.py -- CLEAN-ROOM KiCad symbols for Vera carrier ICs, authored
from the manufacturers' PRIMARY datasheets (not SnapEDA renderings).
=============================================================================
Pin tables below are transcribed from the authoritative vendor datasheets held
in avionics/kicad/symbols/ (open, authoritative -- kept in-repo by project owner):

  * ISOW1044BDFMR  -- TI SLLSFF7A (Rev DEC 2021), Section 7 "Pin Configuration and
    Functions", Table 7-1.  Package: **20-pin DFM** (per Fig 7-1 and Section 8.4
    Thermal Information "DFM / 20 PINS").  NOTE: this corrects the project docs,
    which previously called it "SOIC-16W" -- it is a 20-pin part.
  * SLB9670VQ2.0 (OPTIGA TPM) -- Infineon Data Sheet Rev 1.4 (2018-12-07),
    Section 3 "Pin Description", Tables 3/4/5.  Package: **PG-VQFN-32-13**.

These are our own original symbol drawings (coordinates/arrangement); only the
factual pad<->signal mapping comes from the datasheets (facts, not copyrightable).
CC BY 4.0.  Also writes a factual CSV per part.

Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  (Griffing Technology LLC)
AI-assist: Claude Opus 4.8 (Anthropic) -- clean-room symbol authoring, 2026-07-12.
License: CC BY 4.0
"""

import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
SYMDIR = HERE / "symbols"

# Each pin: (number, name, electrical_type, side)  side in {"L","R"}.
# Electrical types are conservative and ERC-oriented; NCI ("not connected
# internally, may be connected externally") -> no_connect unless the TCG spec
# recommends tying it (then passive so it may be wired without an ERC error).

ISOW1044 = {
    "name": "Vera_ISOW1044BDFMR",
    "value": "ISOW1044BDFMR",
    "footprint": "Vera:SOP65P960X350-20N_DFM20",  # 20-pin DFM (see docstring)
    "desc": "TI ISOW1044BDFMR 5kVrms isolated CAN-FD + iso DC/DC, 20-pin DFM "
    "(clean-room from TI SLLSFF7A Table 7-1)",
    "pins": [
        # Side 1 (logic) -- left
        (1, "VIO", "power_in", "L"),
        (9, "VDD", "power_in", "L"),
        (2, "IN", "input", "L"),
        (3, "TXD", "input", "L"),
        (4, "STB", "input", "L"),
        (5, "RXD", "output", "L"),
        (8, "EN/FLT", "bidirectional", "L"),
        (7, "NC", "no_connect", "L"),
        (6, "GNDIO", "power_in", "L"),
        (10, "GND1", "power_in", "L"),
        # Side 2 (isolated + CAN bus) -- right
        (20, "VISOIN", "power_in", "R"),
        (12, "VISOOUT", "power_out", "R"),
        (13, "VSIN", "power_in", "R"),
        (19, "CANH", "bidirectional", "R"),
        (18, "CANL", "bidirectional", "R"),
        (14, "OUT", "output", "R"),
        (11, "GND2", "power_in", "R"),
        (15, "GISOIN", "power_in", "R"),
        (16, "GISOIN", "power_in", "R"),
        (17, "GISOIN", "power_in", "R"),
    ],
}

SLB9670 = {
    "name": "Vera_SLB9670_TPM",
    "value": "SLB9670VQ2.0",
    "footprint": "Vera:VQFN32_SLB9670",  # PG-VQFN-32-13
    "desc": "Infineon OPTIGA TPM SLB9670 (SPI TPM 2.0), PG-VQFN-32-13 "
    "(clean-room from Infineon DS Rev1.4 Tables 3/4/5)",
    "pins": [
        # SPI + control -- left
        (20, "CS#", "input", "L"),
        (19, "SCLK", "input", "L"),
        (21, "MOSI", "input", "L"),
        (24, "MISO", "output", "L"),
        (18, "PIRQ#", "output", "L"),
        (17, "RST#", "input", "L"),
        (6, "GPIO", "bidirectional", "L"),
        (7, "PP", "input", "L"),
        # Power + TCG-compliance + NC -- right
        (8, "VDD", "power_in", "R"),
        (22, "VDD", "power_in", "R"),
        (1, "NCI/VDD", "passive", "R"),
        (14, "NCI/VDD", "passive", "R"),
        (2, "GND", "power_in", "R"),
        (9, "GND", "power_in", "R"),
        (23, "GND", "power_in", "R"),
        (32, "GND", "power_in", "R"),
        (16, "NCI/GND", "passive", "R"),
        (29, "NC", "no_connect", "R"),
        (30, "NC", "no_connect", "R"),
        (3, "NCI", "no_connect", "R"),
        (4, "NCI", "no_connect", "R"),
        (5, "NCI", "no_connect", "R"),
        (10, "NCI", "no_connect", "R"),
        (11, "NCI", "no_connect", "R"),
        (12, "NCI", "no_connect", "R"),
        (13, "NCI", "no_connect", "R"),
        (15, "NCI", "no_connect", "R"),
        (25, "NCI", "no_connect", "R"),
        (26, "NCI", "no_connect", "R"),
        (27, "NCI", "no_connect", "R"),
        (28, "NCI", "no_connect", "R"),
        (31, "NCI", "no_connect", "R"),
    ],
}


def emit_pin(num, name, etype, x, y, ang, length=3.81):
    return (
        f"      (pin {etype} line (at {x:.2f} {y:.2f} {ang}) (length {length:.2f})\n"
        f'        (name "{name}" (effects (font (size 1.27 1.27))))\n'
        f'        (number "{num}" (effects (font (size 1.27 1.27))))\n'
        f"      )"
    )


def build_symbol(part):
    name = part["name"]
    left = [p for p in part["pins"] if p[3] == "L"]
    right = [p for p in part["pins"] if p[3] == "R"]
    rows = max(len(left), len(right), 1)
    half_h = (rows * 2.54) / 2 + 2.54
    half_w = 22.86  # 1800 mil
    out = [
        f'  (symbol "{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)',
        f'    (property "Reference" "U" (id 0) (at {-half_w:.2f} {half_h + 1.27:.2f} 0)'
        " (effects (font (size 1.27 1.27)) (justify left)))",
        f'    (property "Value" "{part["value"]}" (at {-half_w:.2f} '
        f"{-half_h - 2.54:.2f} 0)"
        " (effects (font (size 1.27 1.27)) (justify left)))",
        f'    (property "Footprint" "{part["footprint"]}" (id 2) (at 0 0 0)'
        " (effects (font (size 1.27 1.27)) hide))",
        '    (property "Datasheet" "" (id 3) (at 0 0 0)'
        " (effects (font (size 1.27 1.27)) hide))",
        f'    (property "ki_description" "{part["desc"]}" (id 4) (at 0 0 0)'
        " (effects (font (size 1.27 1.27)) hide))",
        f'    (symbol "{name}_1_1"',
        f"      (rectangle (start {-half_w:.2f} {-half_h:.2f}) "
        f"(end {half_w:.2f} {half_h:.2f})\n"
        f"        (stroke (width 0.254)) (fill (type background)))",
    ]
    for i, (num, pname, et, _) in enumerate(left):
        y = half_h - 2.54 * (i + 1)
        out.append(emit_pin(num, pname, et, -half_w - 3.81, y, 0))
    for j, (num, pname, et, _) in enumerate(right):
        y = half_h - 2.54 * (j + 1)
        out.append(emit_pin(num, pname, et, half_w + 3.81, y, 180))
    out.append("    )")
    out.append("  )")
    return "\n".join(out)


def write_part(part):
    sym = SYMDIR / f"{part['name']}.kicad_sym"
    body = (
        "(kicad_symbol_lib (version 20211014) (generator "
        "serenity_vera_cleanroom)\n" + build_symbol(part) + "\n)\n"
    )
    sym.write_text(body, encoding="utf-8")
    csv_path = (
        SYMDIR / f"{part['value'].replace('.', '_').replace('/', '_')}_pinmap.csv"
    )
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pad", "signal", "elec_type"])
        for num, pname, et, _ in sorted(part["pins"], key=lambda p: p[0]):
            w.writerow([num, pname, et])
    print(f"wrote {sym.name} ({len(part['pins'])} pins) + {csv_path.name}")


def main():
    for part in (ISOW1044, SLB9670):
        write_part(part)


if __name__ == "__main__":
    main()
