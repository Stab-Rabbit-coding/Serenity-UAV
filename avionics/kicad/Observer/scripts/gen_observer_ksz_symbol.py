#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_jayne_ksz_symbol.py -- CLEAN-ROOM KiCad symbol for the Microchip KSZ9477S
7-port Gigabit Ethernet switch (128-TQFP-EP), banked by our own organization.
=============================================================================
The pin<->signal map below is transcribed DIRECTLY from the PRIMARY source:
Microchip KSZ9477S datasheet DS00002392C, TABLE 3-1 "Pin Assignments" (all 128
pins; pins 73/74/108 = NC).  Pad 129 is the exposed thermal pad (GND).  This is
our own original symbol drawing (banks/coordinates) built from those facts (facts
are not copyrightable); no vendor symbol geometry is used.  CC BY 4.0.

The gitignored SnapEDA KSZ9477 symbol is NOT used here -- it was found to omit
pins 73/74/108, so the primary datasheet is the authoritative source.

PRE-FAB GATE: spot-check against the DS00002392C Figure 3-1 package diagram
before layout.

Output: symbols/Observer_KSZ9477.kicad_sym + symbols/KSZ9477STXI_pinmap.csv (facts).

Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  (Griffing Technology LLC)
AI-assist: Claude Opus 4.8 (Anthropic) -- clean-room symbol authoring, 2026-07-12.
License: CC BY 4.0
"""

import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
SYMDIR = HERE.parent.parent / "symbols"
SYM = SYMDIR / "Observer_KSZ9477.kicad_sym"
CSVOUT = SYMDIR / "KSZ9477STXI_pinmap.csv"
SYMNAME = "Observer_KSZ9477"
FOOTPRINT = "Package_QFP:TQFP-128_14x14mm_P0.4mm"  # KiCad std land pattern

# Microchip DS00002392C TABLE 3-1 (all 128 pins), + pad 129 = exposed pad (GND).
KSZ_MAP = [
    (1, "TXRX1P_A"),
    (2, "TXRX1M_A"),
    (3, "AVDDL"),
    (4, "TXRX1P_B"),
    (5, "TXRX1M_B"),
    (6, "TXRX1P_C"),
    (7, "TXRX1M_C"),
    (8, "TXRX1P_D"),
    (9, "TXRX1M_D"),
    (10, "AVDDH"),
    (11, "DVDDL"),
    (12, "TXRX2P_A"),
    (13, "TXRX2M_A"),
    (14, "AVDDL"),
    (15, "TXRX2P_B"),
    (16, "TXRX2M_B"),
    (17, "TXRX2P_C"),
    (18, "TXRX2M_C"),
    (19, "AVDDL"),
    (20, "TXRX2P_D"),
    (21, "TXRX2M_D"),
    (22, "AVDDH"),
    (23, "DVDDL"),
    (24, "TXRX3P_A"),
    (25, "TXRX3M_A"),
    (26, "TXRX3P_B"),
    (27, "TXRX3M_B"),
    (28, "TXRX3P_C"),
    (29, "TXRX3M_C"),
    (30, "AVDDL"),
    (31, "TXRX3P_D"),
    (32, "TXRX3M_D"),
    (33, "AVDDH"),
    (34, "TXRX4P_A"),
    (35, "TXRX4M_A"),
    (36, "AVDDL"),
    (37, "TXRX4P_B"),
    (38, "TXRX4M_B"),
    (39, "TXRX4P_C"),
    (40, "TXRX4M_C"),
    (41, "AVDDL"),
    (42, "TXRX4P_D"),
    (43, "TXRX4M_D"),
    (44, "AVDDH"),
    (45, "DVDDL"),
    (46, "GND"),
    (47, "GND"),
    (48, "TX_CLK6/REFCLKI6"),
    (49, "TX_EN6/TX_CTL6"),
    (50, "TX_ER6"),
    (51, "COL6"),
    (52, "TXD6_3"),
    (53, "TXD6_2"),
    (54, "TXD6_1"),
    (55, "TXD6_0"),
    (56, "DVDDL"),
    (57, "RX_CLK6/REFCLKO6"),
    (58, "RX_DV6/CRS_DV6/RX_CTL6"),
    (59, "RX_ER6"),
    (60, "CRS6"),
    (61, "VDDIO"),
    (62, "RXD6_3"),
    (63, "RXD6_2"),
    (64, "RXD6_1"),
    (65, "RXD6_0"),
    (66, "DVDDL"),
    (67, "IBA"),
    (68, "VDDIO"),
    (69, "GND"),
    (70, "DVDDL"),
    (71, "VDDLS"),
    (72, "VDDHS"),
    (73, "NC"),
    (74, "NC"),
    (75, "GND"),
    (76, "S_REXT"),
    (77, "GND"),
    (78, "S_IN7M"),
    (79, "S_IN7P"),
    (80, "GND"),
    (81, "S_OUT7P"),
    (82, "S_OUT7M"),
    (83, "VDDHS"),
    (84, "VDDLS"),
    (85, "LED4_0"),
    (86, "LED4_1"),
    (87, "DVDDL"),
    (88, "LED3_0"),
    (89, "LED3_1"),
    (90, "GPIO_1"),
    (91, "LED2_0"),
    (92, "LED2_1"),
    (93, "PME_N"),
    (94, "INTRP_N"),
    (95, "SYNCLKO"),
    (96, "RESET_N"),
    (97, "SDO"),
    (98, "SDI/SDA/MDIO"),
    (99, "VDDIO"),
    (100, "SCS_N"),
    (101, "SCL/MDC"),
    (102, "LED5_0"),
    (103, "LED5_1"),
    (104, "DVDDL"),
    (105, "LED1_0"),
    (106, "LED1_1"),
    (107, "GND"),
    (108, "NC"),
    (109, "GND"),
    (110, "DVDDL"),
    (111, "AVDDH"),
    (112, "TXRX5P_A"),
    (113, "TXRX5M_A"),
    (114, "AVDDL"),
    (115, "TXRX5P_B"),
    (116, "TXRX5M_B"),
    (117, "TXRX5P_C"),
    (118, "TXRX5M_C"),
    (119, "AVDDL"),
    (120, "TXRX5P_D"),
    (121, "TXRX5M_D"),
    (122, "AVDDH"),
    (123, "GND"),
    (124, "AVDDL"),
    (125, "XO"),
    (126, "XI"),
    (127, "ISET"),
    (128, "AVDDH"),
    (129, "GND"),  # exposed thermal pad
]

BANK_ORDER = [
    "A_EthPorts",
    "B_Port6_MII",
    "C_Mgmt_SPI",
    "D_Ctrl_Clk",
    "E_Power",
    "F_Ground",
]
_PORT6 = {
    "TX_CLK6/REFCLKI6",
    "TX_EN6/TX_CTL6",
    "TX_ER6",
    "COL6",
    "TXD6_3",
    "TXD6_2",
    "TXD6_1",
    "TXD6_0",
    "RX_CLK6/REFCLKO6",
    "RX_DV6/CRS_DV6/RX_CTL6",
    "RX_ER6",
    "CRS6",
    "RXD6_3",
    "RXD6_2",
    "RXD6_1",
    "RXD6_0",
}
_MGMT = {"SDO", "SDI/SDA/MDIO", "SCS_N", "SCL/MDC", "RESET_N", "PME_N", "INTRP_N"}
_POWER = {"AVDDL", "AVDDH", "DVDDL", "VDDIO", "VDDLS", "VDDHS"}


def bank_of(name):
    if name.startswith("TXRX"):
        return "A_EthPorts"
    if name in _PORT6:
        return "B_Port6_MII"
    if name in _MGMT:
        return "C_Mgmt_SPI"
    if name == "GND":
        return "F_Ground"
    if name in _POWER:
        return "E_Power"
    return "D_Ctrl_Clk"


def elec_type(name):
    if name in ("GND",) or name in _POWER:
        return "power_in"
    if name == "NC":
        return "no_connect"
    if name in ("SDO", "PME_N", "INTRP_N", "XO", "S_OUT7P", "S_OUT7M"):
        return "output"
    if name in ("RESET_N", "SCS_N", "SCL/MDC", "XI", "S_IN7M", "S_IN7P"):
        return "input"
    if name in ("IBA", "ISET", "S_REXT"):
        return "passive"
    return "bidirectional"


def emit_pin(num, name, et, x, y, ang):
    return (
        f"      (pin {et} line (at {x:.2f} {y:.2f} {ang}) (length 3.81)\n"
        f'        (name "{name}" (effects (font (size 1.27 1.27))))\n'
        f'        (number "{num}" (effects (font (size 1.27 1.27))))\n'
        f"      )"
    )


def emit_unit(unit_no, bank, pins):
    if bank in ("E_Power", "F_Ground"):
        left, right = pins, []
    else:
        left = [p for p in pins if elec_type(p[1]) == "power_in"]
        right = [p for p in pins if elec_type(p[1]) != "power_in"]
    rows = max(len(left), len(right), 1)
    half_h = (rows * 2.54) / 2 + 2.54
    half_w = 30.48
    out = [
        f'    (symbol "{SYMNAME}_{unit_no}_1"',
        f'      (text "{bank}" (at {-half_w + 2.54:.2f} {half_h - 1.5:.2f} 0)'
        " (effects (font (size 1.27 1.27)) (justify left)))",
        f"      (rectangle (start {-half_w:.2f} {-half_h:.2f}) "
        f"(end {half_w:.2f} {half_h:.2f})\n"
        f"        (stroke (width 0.254)) (fill (type background)))",
    ]
    for i, (num, name) in enumerate(left):
        out.append(
            emit_pin(
                num, name, elec_type(name), -half_w - 3.81, half_h - 2.54 * (i + 1), 0
            )
        )
    for j, (num, name) in enumerate(right):
        out.append(
            emit_pin(
                num, name, elec_type(name), half_w + 3.81, half_h - 2.54 * (j + 1), 180
            )
        )
    out.append("    )")
    return "\n".join(out)


def main():
    banks = {b: [] for b in BANK_ORDER}
    for num, name in KSZ_MAP:
        banks[bank_of(name)].append((num, name))
    parts = [
        "(kicad_symbol_lib (version 20211014) (generator " "serenity_jayne_cleanroom)",
        f'  (symbol "{SYMNAME}" (pin_names (offset 1.016)) '
        "(in_bom yes) (on_board yes)",
        '    (property "Reference" "U" (id 0) (at -30.48 6.0 0)'
        " (effects (font (size 1.27 1.27)) (justify left)))",
        '    (property "Value" "KSZ9477STXI" (id 1) (at -30.48 3.0 0)'
        " (effects (font (size 1.27 1.27)) (justify left)))",
        f'    (property "Footprint" "{FOOTPRINT}" (id 2) (at 0 0 0)'
        " (effects (font (size 1.27 1.27)) hide))",
        '    (property "Datasheet" "" (id 3) (at 0 0 0)'
        " (effects (font (size 1.27 1.27)) hide))",
        '    (property "ki_description" "Microchip KSZ9477S 7-port GbE switch '
        '(HSR/PRP), 128-TQFP-EP -- clean-room from DS00002392C Table 3-1" '
        "(id 4) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))",
    ]
    for i, bank in enumerate(BANK_ORDER, start=1):
        parts.append(emit_unit(i, bank, banks[bank]))
    parts.append("  )")
    parts.append(")")
    SYM.write_text("\n".join(parts) + "\n", encoding="utf-8")
    with open(CSVOUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pad", "signal", "bank"])
        for num, name in KSZ_MAP:
            w.writerow([num, name, bank_of(name)])
    print(f"wrote {SYM.name} ({len(KSZ_MAP)} pads across {len(BANK_ORDER)} banks)")
    for b in BANK_ORDER:
        print(f"  unit {BANK_ORDER.index(b)+1}  {b:14} {len(banks[b])} pads")


if __name__ == "__main__":
    main()
