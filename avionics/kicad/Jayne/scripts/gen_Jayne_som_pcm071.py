#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_jayne_som_pcm071.py -- CLEAN-ROOM KiCad symbol for the PHYTEC phyCORE-AM62x
CONNECTORIZED module (PCM-071), authored from the PHYTEC hardware manual.
=============================================================================
Jayne uses the CONNECTORIZED variant (user decision 2026-07-12): PCM-071, 32x43 mm,
240-pin via 2x Samtec BTH-060-01-L-D-A-K-TR board-to-board connectors (0.5 mm,
2x60), 5 mm stacking height. This SUPERSEDES the earlier direct-solder DSC work
(Jayne_SoM.kicad_sym 270-pin / jayne_som_pinmap.csv) which was the wrong variant.

Pin<->signal facts are transcribed from the PHYTEC manual
"L-1038e.A5_phyCORE-AM62x_HW Manual.pdf" (Tables 7-10, Connector X1 Columns A/B/C/D,
pins 1-60 each = 240). Facts are not copyrightable; the symbol drawing (our 4-column
banks / coordinates) is our own CC BY 4.0 work. Pin numbers use the manual's
A#/B#/C#/D# labels so they map 1:1 to the Samtec connector pads.

PRE-FAB GATE: cross-check the A/B/C/D pin labels against the mating Samtec BTH-060
pad numbering before layout (§4.3 Figure 6).

Input : avionics/kicad/symbols/phyCORE_AM62x_PCM071_pinmap.csv
Output: avionics/kicad/symbols/Jayne_SoM_PCM071.kicad_sym

Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  (Griffing Technology LLC)
AI-assist: Claude Opus 4.8 (Anthropic) -- clean-room symbol authoring, 2026-07-12.
License: CC BY 4.0
"""

import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
SYMDIR = HERE.parent.parent / "symbols"
CSVIN = SYMDIR / "phyCORE_AM62x_PCM071_pinmap.csv"
OUT = SYMDIR / "Jayne_SoM_PCM071.kicad_sym"
SYMNAME = "Jayne_SoM_PCM071"
# 2x Samtec BTH-060 board-to-board; footprint authored separately from Samtec dims.
FOOTPRINT = "Jayne:phyCORE-AM62x_PCM071_2xBTH-060"
BANKS = ["A", "B", "C", "D"]


def elec_type(sig, typ):
    s = sig.upper()
    if s.startswith("GND") or s in ("VIN", "VBAT"):
        return "power_in"
    if typ in ("PWR_I", "PWR_IO"):
        return "power_in"
    if typ == "PWR_O":
        return "power_out"
    if typ in ("O", "OD-O", "A/O"):
        return "output"
    if typ in ("I", "A/I"):
        return "input"
    if typ == "-":
        return "power_in"  # remaining bare-type rows are grounds
    return "bidirectional"  # I/O, OD-I/O, OD-I


def load():
    banks = {b: [] for b in BANKS}
    with open(CSVIN, newline="") as f:
        for r in csv.DictReader(f):
            banks[r["pin"][0]].append(
                (r["pin"], r["signal"], elec_type(r["signal"], r["type"]))
            )
    for b in banks:
        banks[b].sort(key=lambda t: int(t[0][1:]))
    return banks


def emit_pin(num, name, et, x, y, ang):
    return (
        f"      (pin {et} line (at {x:.2f} {y:.2f} {ang}) (length 3.81)\n"
        f'        (name "{name}" (effects (font (size 1.27 1.27))))\n'
        f'        (number "{num}" (effects (font (size 1.27 1.27))))\n'
        f"      )"
    )


def emit_unit(unit_no, bank, pins):
    left = [p for p in pins if p[2] in ("power_in", "power_out")]
    right = [p for p in pins if p[2] not in ("power_in", "power_out")]
    rows = max(len(left), len(right), 1)
    half_h = (rows * 2.54) / 2 + 2.54
    half_w = 33.02
    out = [
        f'    (symbol "{SYMNAME}_{unit_no}_1"',
        f'      (text "Connector X1 Col {bank}" (at {-half_w + 2.54:.2f} '
        f"{half_h - 1.5:.2f} 0)"
        " (effects (font (size 1.27 1.27)) (justify left)))",
        f"      (rectangle (start {-half_w:.2f} {-half_h:.2f}) "
        f"(end {half_w:.2f} {half_h:.2f})\n"
        f"        (stroke (width 0.254)) (fill (type background)))",
    ]
    for i, (num, name, et) in enumerate(left):
        out.append(emit_pin(num, name, et, -half_w - 3.81, half_h - 2.54 * (i + 1), 0))
    for j, (num, name, et) in enumerate(right):
        out.append(emit_pin(num, name, et, half_w + 3.81, half_h - 2.54 * (j + 1), 180))
    out.append("    )")
    return "\n".join(out)


def main():
    banks = load()
    total = sum(len(v) for v in banks.values())
    parts = [
        "(kicad_symbol_lib (version 20211014) (generator serenity_jayne_cleanroom)",
        f'  (symbol "{SYMNAME}" (pin_names (offset 1.016)) '
        "(in_bom yes) (on_board yes)",
        '    (property "Reference" "U" (id 0) (at -33.02 6.0 0)'
        " (effects (font (size 1.27 1.27)) (justify left)))",
        '    (property "Value" "phyCORE-AM62x (PCM-071)" (id 1) (at -33.02 3.0 0)'
        " (effects (font (size 1.27 1.27)) (justify left)))",
        f'    (property "Footprint" "{FOOTPRINT}" (id 2) (at 0 0 0)'
        " (effects (font (size 1.27 1.27)) hide))",
        '    (property "Datasheet" "" (id 3) (at 0 0 0)'
        " (effects (font (size 1.27 1.27)) hide))",
        '    (property "ki_description" "PHYTEC phyCORE-AM62x PCM-071 SoM, 240-pin '
        '2x Samtec BTH-060 -- clean-room from PHYTEC HW manual Tables 7-10" '
        "(id 4) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))",
    ]
    for i, b in enumerate(BANKS, start=1):
        parts.append(emit_unit(i, b, banks[b]))
    parts.append("  )")
    parts.append(")")
    OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"wrote {OUT.name} ({total} pins across {len(BANKS)} columns)")
    for b in BANKS:
        print(f"  unit {BANKS.index(b)+1}  Col {b}: {len(banks[b])} pins")


if __name__ == "__main__":
    main()
