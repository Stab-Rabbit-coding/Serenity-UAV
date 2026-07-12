#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_vera_som_symbol.py -- author a CLEAN-ROOM KiCad symbol for the PHYTEC
phyCORE-AM62A SoM from the factual pad<->signal map only.
=============================================================================
Why clean-room: SnapEDA's rendering of this part (symbols/PHYCORE-AM62AX-DSC.*)
carries restrictive usage terms and is gitignored -- it must NOT be committed or
embedded in Vera.kicad_sch.  The pad<->signal PINOUT, however, is PHYTEC-published
fact (facts are not copyrightable).  This script reads only the factual CSV
(avionics/kicad/vera_som_pinmap.csv) and emits an ORIGINAL symbol with our own
functional-bank arrangement -- no SnapEDA geometry, grouping, or coordinates.

Output: avionics/kicad/symbols/Vera_SoM.kicad_sym  (CC BY 4.0, committable).

Pre-fab gate: the factual map should be cross-verified against the PHYTEC
phyCORE-AM62Ax Hardware Manual (primary source) before fabrication -- the CSV was
derived from a secondary rendering.

Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  (Griffing Technology LLC)
AI-assist: Claude Opus 4.8 (Anthropic) -- clean-room symbol authoring, 2026-07-12.
License: CC BY 4.0
"""

import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV = HERE / "vera_som_pinmap.csv"
OUT = HERE / "symbols" / "Vera_SoM.kicad_sym"

SYMNAME = "Vera_SoM_phyCORE_AM62A"
FOOTPRINT = "Vera:phyCORE-AM62A-DSC-270"  # clean-room footprint authored separately

# --- our OWN functional banks (deliberately NOT SnapEDA's unit layout) --------
# Map each CSV functional_group into one of our banks; the ordering and grouping
# here is our original organization of the published pinout.
BANK_OF = {
    "Power": "A_Power",
    "MIPI CSI-2": "B_Camera_Display",
    "Video Out": "B_Camera_Display",
    "RGMII 2": "C_Ethernet",
    "Ethernet": "C_Ethernet",
    "WKUP IO": "D_Serial_Ctrl",
    "MCU IO": "D_Serial_Ctrl",
    "General IO": "D_Serial_Ctrl",
    "Audio / MCASP": "E_System",
    "MMC1": "E_System",
    "MMC2": "E_System",
    "USB": "E_System",
    "JTAG": "F_Debug_Boot",
    "Reset / Error": "F_Debug_Boot",
    "GPMC": "F_Debug_Boot",
    "unit6": "G_NoConnect",
}
# Bank draw order (unit numbers assigned in this order).
BANK_ORDER = [
    "A_Power",
    "B_Camera_Display",
    "C_Ethernet",
    "D_Serial_Ctrl",
    "E_System",
    "F_Debug_Boot",
    "G_NoConnect",
]


def elec_type(sig: str) -> str:
    """Assign a conservative, ERC-friendly electrical type from the signal name."""
    s = sig.upper()
    if s.startswith("NC_"):
        return "no_connect"
    if s.startswith("GND"):
        return "power_in"
    if s.startswith("VDD_3V3_OUT"):
        return "power_out"  # module SOURCES 3V3 to the carrier
    if s.startswith(("VIN", "VBAT", "VDD", "VDDA", "VDDS", "SOC_VDD")):
        return "power_in"
    return "bidirectional"


def load_pins():
    banks = {b: [] for b in BANK_ORDER}
    with open(CSV, newline="") as f:
        for row in csv.DictReader(f):
            pad = int(row["pad"])
            sig = row["signal"]
            grp = row["functional_group"]
            bank = BANK_OF.get(grp, "F_Debug_Boot")
            banks[bank].append((pad, sig, elec_type(sig)))
    for b in banks:
        banks[b].sort(key=lambda t: t[0])  # by pad number within our bank
    return banks


def emit_pin(pad, sig, etype, x, y, ang, length=3.81):
    return (
        f"      (pin {etype} line (at {x:.2f} {y:.2f} {ang}) (length {length:.2f})\n"
        f'        (name "{sig}" (effects (font (size 1.27 1.27))))\n'
        f'        (number "{pad}" (effects (font (size 1.27 1.27))))\n'
        f"      )"
    )


def emit_unit(unit_no, bankname, pins):
    """One KiCad sub-symbol (unit). Power/ground pins on the left, signals on the
    right; our own tidy two-column arrangement."""
    left = [p for p in pins if p[2] in ("power_in", "power_out")]
    right = [p for p in pins if p[2] not in ("power_in", "power_out")]
    rows = max(len(left), len(right), 1)
    half_h = (rows * 2.54) / 2 + 2.54
    half_w = 33.02  # 2600 mil -- room for long TI signal names
    body = []
    body.append(f'    (symbol "{SYMNAME}_{unit_no}_1"')
    # bank label inside the body, top-left
    body.append(
        f'      (text "{bankname}" (at {-half_w + 2.54:.2f} {half_h - 1.5:.2f} 0)'
        f" (effects (font (size 1.27 1.27)) (justify left)))"
    )
    body.append(
        f"      (rectangle (start {-half_w:.2f} {-half_h:.2f}) "
        f"(end {half_w:.2f} {half_h:.2f})\n"
        f"        (stroke (width 0.254)) (fill (type background)))"
    )
    for i, (pad, sig, et) in enumerate(left):
        y = half_h - 2.54 * (i + 1)
        body.append(emit_pin(pad, sig, et, -half_w - 3.81, y, 0))
    for j, (pad, sig, et) in enumerate(right):
        y = half_h - 2.54 * (j + 1)
        body.append(emit_pin(pad, sig, et, half_w + 3.81, y, 180))
    body.append("    )")
    return "\n".join(body)


def main():
    banks = load_pins()
    total = sum(len(v) for v in banks.values())
    parts = [
        "(kicad_symbol_lib (version 20211014) (generator "
        "serenity_vera_som_cleanroom)",
        f'  (symbol "{SYMNAME}" (pin_names (offset 1.016)) '
        "(in_bom yes) (on_board yes)",
        '    (property "Reference" "U" (id 0) (at -33.02 6.0 0)'
        " (effects (font (size 1.27 1.27)) (justify left)))",
        '    (property "Value" "phyCORE-AM62A" (id 1) (at -33.02 3.0 0)'
        " (effects (font (size 1.27 1.27)) (justify left)))",
        f'    (property "Footprint" "{FOOTPRINT}" (id 2) (at 0 0 0)'
        " (effects (font (size 1.27 1.27)) hide))",
        '    (property "Datasheet" "" (id 3) (at 0 0 0)'
        " (effects (font (size 1.27 1.27)) hide))",
        '    (property "ki_description" "PHYTEC phyCORE-AM62A SoM (270-pad DSC) '
        '-- clean-room symbol from published pinout facts" (id 4) (at 0 0 0)'
        " (effects (font (size 1.27 1.27)) hide))",
    ]
    for i, bank in enumerate(BANK_ORDER, start=1):
        parts.append(emit_unit(i, bank, banks[bank]))
    parts.append("  )")
    parts.append(")")
    OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"wrote {OUT}  ({total} pins across {len(BANK_ORDER)} clean-room banks)")
    for b in BANK_ORDER:
        print(f"  unit {BANK_ORDER.index(b)+1}  {b:18} {len(banks[b])} pins")


if __name__ == "__main__":
    main()
