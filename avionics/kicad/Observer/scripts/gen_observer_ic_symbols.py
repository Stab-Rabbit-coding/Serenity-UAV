#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_jayne_ic_symbols.py -- CLEAN-ROOM KiCad symbols for Observer carrier ICs, authored
from the manufacturers' PRIMARY datasheets (not SnapEDA renderings).
=============================================================================
Pin tables below are transcribed from the authoritative vendor datasheets held
in avionics/kicad/symbols/ (open, authoritative -- kept in-repo by project owner):

  * ISOW1044BDFMR  -- TI SLLSFF7A (Rev DEC 2021), Section 7 "Pin Configuration and
    Functions", Table 7-1.  Package: **20-pin DFM** (per Fig 7-1 and Section 8.4
    Thermal Information "DFM / 20 PINS").  NOTE: this corrects the project docs,
    which previously called it "SOIC-16W" -- it is a 20-pin part.
  * SLB9672XU2.0 (OPTIGA TPM) -- Infineon Datasheet Rev 1.3 (2024-11-18),
    Section 3.1.2 "Pin description", Tables 11/12/13.  Package: **PG-UQFN-32-1,-2**.
    Supersedes the earlier SLB9670VQ2.0 (Infineon DS Rev 1.4, 2018-12-07,
    PG-VQFN-32-13) -- same 5x5mm/0.5mm-pitch/32-pin QFN land pattern, but the
    GPIO/PP pin functions and which VDD/GND pins are mandatory vs optional
    differ; see the "pins" list below (transcribed from the 9672 datasheet,
    not carried over from the 9670 entry).

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
SYMDIR = HERE.parent.parent / "symbols"

# Each pin: (number, name, electrical_type, side)  side in {"L","R"}.
# Electrical types are conservative and ERC-oriented; NCI ("not connected
# internally, may be connected externally") -> no_connect unless the TCG spec
# recommends tying it (then passive so it may be wired without an ERC error).

ISOW1044 = {
    "name": "Observer_ISOW1044BDFMR",
    "value": "ISOW1044BDFMR",
    "footprint": "Observer:ISOW1044_DFM20_TBD",  # DFM-20: author from TI SLLSFF7A pkg
    # drawing -- isolation-critical (5kV clearance), do NOT substitute a generic land
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

SLB9672 = {
    "name": "SLB9672_TPM",
    "value": "SLB9672XU2.0",
    "footprint": "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm",
    # PG-UQFN-32-1,-2; same 5x5mm/0.5mm-pitch/32-pin QFN land pattern as the
    # superseded SLB9670VQ2.0 (Infineon datasheet Fig 3 recommended footprint,
    # both parts: 5x5mm body, 3.6x3.6mm exposed pad) -- footprint reused as-is.
    "desc": "Infineon OPTIGA TPM SLB9672 (SPI TPM 2.0), PG-UQFN-32-1,-2 "
    "(clean-room from Infineon DS Rev1.3 Tables 11/12/13)",
    "pins": [
        # SPI + control -- left
        (20, "CS#", "input", "L"),
        (19, "SCLK", "input", "L"),
        (21, "MOSI", "input", "L"),
        (24, "MISO", "output", "L"),
        (18, "PIRQ#", "output", "L"),
        (17, "RST#", "input", "L"),
        (6, "NC", "no_connect", "L"),
        (7, "GPIO_02", "bidirectional", "L"),
        # Power + TCG-compliance + NC -- right
        (8, "NCI/VDD", "passive", "R"),
        (22, "VDD", "power_in", "R"),
        (1, "VDD", "power_in", "R"),
        (14, "VDD", "power_in", "R"),
        (2, "GND", "power_in", "R"),
        (9, "GND", "power_in", "R"),
        (23, "GND", "power_in", "R"),
        (32, "GND", "power_in", "R"),
        (16, "NCI/GND", "passive", "R"),
        (29, "NC", "no_connect", "R"),
        (30, "NC", "no_connect", "R"),
        (3, "GPIO_00", "bidirectional", "R"),
        (4, "GPIO_01", "bidirectional", "R"),
        (5, "NCI", "no_connect", "R"),
        (10, "NCI/VDD", "passive", "R"),
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


# MSPM0G3507 -- TI SLASEX6C Figure 6-4 "48-Pin RGZ (VQFN) Top View".  Pin names
# are the physical port-pin identities (PAx/PBx); mux functions are firmware-set.
# Pin 49 = thermal pad (VSS).  Side: pins 1-24 left, 25-49 right (our arrangement).
_MSPM0_NAMES = [
    (1, "PA0"),
    (2, "PA1"),
    (3, "PA28"),
    (4, "NRST"),
    (5, "PA31"),
    (6, "VDD"),
    (7, "VSS"),
    (8, "PA2"),
    (9, "PA3"),
    (10, "PA4"),
    (11, "PA5"),
    (12, "PA6"),
    (13, "PA7"),
    (14, "PB2"),
    (15, "PB3"),
    (16, "PA8"),
    (17, "PA9"),
    (18, "PA10"),
    (19, "PA11"),
    (20, "PB6"),
    (21, "PB7"),
    (22, "PB8"),
    (23, "PB9"),
    (24, "PB14"),
    (25, "PB15"),
    (26, "PB16"),
    (27, "PA12"),
    (28, "PA13"),
    (29, "PA14"),
    (30, "PA15"),
    (31, "PA16"),
    (32, "PA17"),
    (33, "PA18"),
    (34, "PA19/SWDIO"),
    (35, "PA20/SWCLK"),
    (36, "PB17"),
    (37, "PB18"),
    (38, "PB19"),
    (39, "PA21"),
    (40, "PA22"),
    (41, "PB20"),
    (42, "PB24"),
    (43, "PA23"),
    (44, "PA24"),
    (45, "PA25"),
    (46, "PA26"),
    (47, "PA27"),
    (48, "VCORE"),
    (49, "VSS"),
]


def _mspm0_pins():
    pw = {"VDD": "power_in", "VSS": "power_in", "VCORE": "passive"}
    out = []
    for num, name in _MSPM0_NAMES:
        et = "input" if name == "NRST" else pw.get(name, "bidirectional")
        out.append((num, name, et, "L" if num <= 24 else "R"))
    return out


MSPM0 = {
    "name": "Observer_MSPM0G3507_RGZ",
    "value": "MSPM0G3507SRGZR",
    "footprint": "Package_DFN_QFN:QFN-48-1EP_7x7mm_P0.5mm_EP5.15x5.15mm",
    # RGZ 48-pin; confirm EP size vs TI pkg drawing before layout
    "desc": "TI MSPM0G3507 Arm Cortex-M0+ MCU (CAN-FD), 48-pin RGZ VQFN "
    "(clean-room from TI SLASEX6C Fig 6-4)",
    "pins": _mspm0_pins(),
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
        "serenity_jayne_cleanroom)\n" + build_symbol(part) + "\n)\n"
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
    for part in (ISOW1044, SLB9672, MSPM0):
        write_part(part)


if __name__ == "__main__":
    main()
