#!/usr/bin/env python3
"""
add_eth_phy.py — Add one EM-hardened Ethernet port to Pilot and XO.

Components added:
  ADIN1300BCPZ  : ADI industrial 10/100/1000BASE-T PHY, IEC 61000-4 hardened,
                  RMII interface [REF-IEEE-001 Clause 22], -40/+85 C.
                  Ref: analog.com/media/en/technical-documentation/data-sheets/ADIN1300.pdf
  ISO7642FDWRR  : TI 6-channel 150 Mbps 5 kV digital isolator (SOIC-16W), x2.
                  Isolates RMII bus at same 5 kV reinforced-isolation level as
                  ISOW1044 on CAN [REF-IEC-001 §5.5.2] [REF-VDE-001 Cl.4.3].
                  Ref: ti.com/product/ISO7642
  749010012A    : Wurth SMD 10/100BASE-TX Ethernet transformer with integrated CMC.
                  Provides galvanic isolation on the MDI side, 1500 Vrms per
                  [REF-IEEE-001 Clause 38].  8-pin SMD.
                  Ref: Wurth Electronics 749010012A datasheet.
  JST GH 4P     : JST GH series 4-pin connector for Ethernet harness.
                  TX+/TX-/RX+/RX- on 1.25 mm pitch.  Lightweight, locking.

RMII0 signals are reconnected from the PB2-P2 connector (where no_connect markers
were placed by gen_cape_a2.py / gen_cape_b2.py) through two ISO7642FDWRR isolators
to the ADIN1300 PHY.  RMII1 signals and PHY2 control remain as no_connect (only
one PHY per cape).

For XO also removes orphaned PHY-side global_labels left by gen_cape_b2.py.

Usage:
    python3 add_eth_phy.py Pilot.kicad_sch
    python3 add_eth_phy.py XO.kicad_sch

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0  |  creativecommons.org/licenses/by/4.0
Date:    2026-06-03
References:
    TI ISO7642 datasheet SCDS349 (2022)
    ADI ADIN1300 datasheet (Rev. B, 2022)
    Wurth 749010012A datasheet (10/100BASE-TX SMD transformer)
    JST GH series datasheet
    KiCad S-expression schematic format v20240101
"""

import os
import re
import sys

# ---------------------------------------------------------------------------
# Y-positions on PB2-P2 connector (X=67.54) for RMII0 signals to restore.
# These were replaced with no_connect markers by gen_cape_a2/b2.py.
# ---------------------------------------------------------------------------
RMII0_RESTORE = {
    390.63: "RMII0_TXD0",
    393.17: "RMII0_TXD1",
    395.71: "RMII0_TX_EN",
    398.25: "RMII0_RXD0",
    400.79: "RMII0_RXD1",
    403.33: "RMII0_CRS_DV",
    405.87: "RMII0_RX_ER",
    408.41: "RMII0_REF_CLK",
    431.27: "MDC",
    433.81: "MDIO",
    436.35: "PHY1_INTRN",
    438.89: "PHY1_RSTN",
}

# Orphaned PHY-side labels in XO (left by gen_cape_b2.py).
# These are at X=197.30/222.70/347.30/372.70, Y=447-465.
CAPE_B2_ORPHAN_X = {197.30, 222.70, 347.30, 372.70}
CAPE_B2_ORPHAN_Y_RANGE = (440.0, 470.0)


# ---------------------------------------------------------------------------
# Lib-symbol definitions
# ---------------------------------------------------------------------------

ADIN1300_SYM = """    (symbol "ADIN1300"
      (pin_names (offset 0.254))
      (pin_numbers (hide yes))
      (property "Reference" "U" (at 0 -19.05 0)
        (effects (font (size 1.27 1.27))))
      (property "Value" "ADIN1300" (at 0 19.05 0)
        (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_LGA:LGA-48_7x7mm_P0.5mm" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes)))
      (property "Datasheet"
        "https://www.analog.com/media/en/technical-documentation/data-sheets/ADIN1300.pdf"
        (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (symbol "ADIN1300_0_1"
        (rectangle (start -12.70 17.78) (end 12.70 -17.78)
          (stroke (width 0) (type default)) (fill (type background))))
      (symbol "ADIN1300_1_1"
        (pin input line (at -17.78 13.97 0) (length 2.54)
          (name "REF_CLK" (effects (font (size 1.016 1.016))))
          (number "1" (effects (font (size 1.016 1.016)))))
        (pin input line (at -17.78 11.43 0) (length 2.54)
          (name "TXD0" (effects (font (size 1.016 1.016))))
          (number "2" (effects (font (size 1.016 1.016)))))
        (pin input line (at -17.78 8.89 0) (length 2.54)
          (name "TXD1" (effects (font (size 1.016 1.016))))
          (number "3" (effects (font (size 1.016 1.016)))))
        (pin input line (at -17.78 6.35 0) (length 2.54)
          (name "TX_EN" (effects (font (size 1.016 1.016))))
          (number "4" (effects (font (size 1.016 1.016)))))
        (pin output line (at -17.78 3.81 0) (length 2.54)
          (name "RXD0" (effects (font (size 1.016 1.016))))
          (number "5" (effects (font (size 1.016 1.016)))))
        (pin output line (at -17.78 1.27 0) (length 2.54)
          (name "RXD1" (effects (font (size 1.016 1.016))))
          (number "6" (effects (font (size 1.016 1.016)))))
        (pin output line (at -17.78 -1.27 0) (length 2.54)
          (name "CRS_DV" (effects (font (size 1.016 1.016))))
          (number "7" (effects (font (size 1.016 1.016)))))
        (pin output line (at -17.78 -3.81 0) (length 2.54)
          (name "RX_ER" (effects (font (size 1.016 1.016))))
          (number "8" (effects (font (size 1.016 1.016)))))
        (pin input line (at -17.78 -6.35 0) (length 2.54)
          (name "MDC" (effects (font (size 1.016 1.016))))
          (number "9" (effects (font (size 1.016 1.016)))))
        (pin bidirectional line (at -17.78 -8.89 0) (length 2.54)
          (name "MDIO" (effects (font (size 1.016 1.016))))
          (number "10" (effects (font (size 1.016 1.016)))))
        (pin input line (at -17.78 -11.43 0) (length 2.54)
          (name "RESET_N" (effects (font (size 1.016 1.016))))
          (number "11" (effects (font (size 1.016 1.016)))))
        (pin output line (at -17.78 -13.97 0) (length 2.54)
          (name "INT_N" (effects (font (size 1.016 1.016))))
          (number "12" (effects (font (size 1.016 1.016)))))
        (pin output line (at 17.78 8.89 180) (length 2.54)
          (name "MDI_TXP" (effects (font (size 1.016 1.016))))
          (number "13" (effects (font (size 1.016 1.016)))))
        (pin output line (at 17.78 6.35 180) (length 2.54)
          (name "MDI_TXN" (effects (font (size 1.016 1.016))))
          (number "14" (effects (font (size 1.016 1.016)))))
        (pin input line (at 17.78 -6.35 180) (length 2.54)
          (name "MDI_RXP" (effects (font (size 1.016 1.016))))
          (number "15" (effects (font (size 1.016 1.016)))))
        (pin input line (at 17.78 -8.89 180) (length 2.54)
          (name "MDI_RXN" (effects (font (size 1.016 1.016))))
          (number "16" (effects (font (size 1.016 1.016)))))
        (pin power_in line (at 17.78 13.97 180) (length 2.54)
          (name "VDD" (effects (font (size 1.016 1.016))))
          (number "17" (effects (font (size 1.016 1.016)))))
        (pin power_in line (at 17.78 11.43 180) (length 2.54)
          (name "VDDIO" (effects (font (size 1.016 1.016))))
          (number "18" (effects (font (size 1.016 1.016)))))
        (pin power_in line (at 17.78 -13.97 180) (length 2.54)
          (name "GND" (effects (font (size 1.016 1.016))))
          (number "19" (effects (font (size 1.016 1.016)))))
      )
    )
"""

ISO7642_SYM = """    (symbol "ISO7642FDWRR"
      (pin_names (offset 0.254))
      (pin_numbers (hide yes))
      (property "Reference" "U" (at 0 -12.70 0)
        (effects (font (size 1.27 1.27))))
      (property "Value" "ISO7642FDWRR" (at 0 12.70 0)
        (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes)))
      (property "Datasheet" "https://www.ti.com/lit/ds/symlink/iso7642.pdf" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes)))
      (symbol "ISO7642FDWRR_0_1"
        (rectangle (start -7.62 10.16) (end 7.62 -10.16)
          (stroke (width 0) (type default)) (fill (type background)))
        (polyline
          (pts (xy 0 10.16) (xy 0 -10.16))
          (stroke (width 0.127) (type dash)) (fill (type none))))
      (symbol "ISO7642FDWRR_1_1"
        (pin power_in line (at -12.70 8.89 0) (length 2.54)
          (name "GND_A" (effects (font (size 1.016 1.016))))
          (number "1" (effects (font (size 1.016 1.016)))))
        (pin input line (at -12.70 6.35 0) (length 2.54)
          (name "INA1" (effects (font (size 1.016 1.016))))
          (number "2" (effects (font (size 1.016 1.016)))))
        (pin input line (at -12.70 3.81 0) (length 2.54)
          (name "INA2" (effects (font (size 1.016 1.016))))
          (number "3" (effects (font (size 1.016 1.016)))))
        (pin input line (at -12.70 1.27 0) (length 2.54)
          (name "INA3" (effects (font (size 1.016 1.016))))
          (number "4" (effects (font (size 1.016 1.016)))))
        (pin input line (at -12.70 -1.27 0) (length 2.54)
          (name "INA4" (effects (font (size 1.016 1.016))))
          (number "5" (effects (font (size 1.016 1.016)))))
        (pin input line (at -12.70 -3.81 0) (length 2.54)
          (name "INA5" (effects (font (size 1.016 1.016))))
          (number "6" (effects (font (size 1.016 1.016)))))
        (pin input line (at -12.70 -6.35 0) (length 2.54)
          (name "INA6" (effects (font (size 1.016 1.016))))
          (number "7" (effects (font (size 1.016 1.016)))))
        (pin power_in line (at -12.70 -8.89 0) (length 2.54)
          (name "VCC_A" (effects (font (size 1.016 1.016))))
          (number "8" (effects (font (size 1.016 1.016)))))
        (pin power_in line (at 12.70 8.89 180) (length 2.54)
          (name "VCC_B" (effects (font (size 1.016 1.016))))
          (number "9" (effects (font (size 1.016 1.016)))))
        (pin power_in line (at 12.70 6.35 180) (length 2.54)
          (name "GND_B" (effects (font (size 1.016 1.016))))
          (number "10" (effects (font (size 1.016 1.016)))))
        (pin output line (at 12.70 3.81 180) (length 2.54)
          (name "OUTB1" (effects (font (size 1.016 1.016))))
          (number "11" (effects (font (size 1.016 1.016)))))
        (pin output line (at 12.70 1.27 180) (length 2.54)
          (name "OUTB2" (effects (font (size 1.016 1.016))))
          (number "12" (effects (font (size 1.016 1.016)))))
        (pin output line (at 12.70 -1.27 180) (length 2.54)
          (name "OUTB3" (effects (font (size 1.016 1.016))))
          (number "13" (effects (font (size 1.016 1.016)))))
        (pin output line (at 12.70 -3.81 180) (length 2.54)
          (name "OUTB4" (effects (font (size 1.016 1.016))))
          (number "14" (effects (font (size 1.016 1.016)))))
        (pin output line (at 12.70 -6.35 180) (length 2.54)
          (name "OUTB5" (effects (font (size 1.016 1.016))))
          (number "15" (effects (font (size 1.016 1.016)))))
        (pin output line (at 12.70 -8.89 180) (length 2.54)
          (name "OUTB6" (effects (font (size 1.016 1.016))))
          (number "16" (effects (font (size 1.016 1.016)))))
      )
    )
"""

ETH_XFMR_SYM = """    (symbol "ETH_XFMR"
      (pin_names (offset 0.254))
      (pin_numbers (hide yes))
      (property "Reference" "T" (at 0 -8.89 0)
        (effects (font (size 1.27 1.27))))
      (property "Value" "749010012A" (at 0 8.89 0)
        (effects (font (size 1.27 1.27))))
      (property "Footprint"
        "Transformer_SMD:Wurth_749010012A_10-100BASE-TX" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes)))
      (property "Datasheet"
        "https://www.we-online.com/catalog/datasheet/749010012A.pdf" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes)))
      (symbol "ETH_XFMR_0_1"
        (rectangle (start -5.08 7.62) (end 5.08 -7.62)
          (stroke (width 0) (type default)) (fill (type background)))
        (polyline
          (pts (xy 0 7.62) (xy 0 -7.62))
          (stroke (width 0.127) (type dash)) (fill (type none))))
      (symbol "ETH_XFMR_1_1"
        (pin input line (at -10.16 5.08 0) (length 2.54)
          (name "PHY_TX+" (effects (font (size 1.016 1.016))))
          (number "1" (effects (font (size 1.016 1.016)))))
        (pin input line (at -10.16 2.54 0) (length 2.54)
          (name "PHY_TX-" (effects (font (size 1.016 1.016))))
          (number "2" (effects (font (size 1.016 1.016)))))
        (pin output line (at -10.16 -2.54 0) (length 2.54)
          (name "PHY_RX+" (effects (font (size 1.016 1.016))))
          (number "3" (effects (font (size 1.016 1.016)))))
        (pin output line (at -10.16 -5.08 0) (length 2.54)
          (name "PHY_RX-" (effects (font (size 1.016 1.016))))
          (number "4" (effects (font (size 1.016 1.016)))))
        (pin output line (at 10.16 5.08 180) (length 2.54)
          (name "LINE_TX+" (effects (font (size 1.016 1.016))))
          (number "5" (effects (font (size 1.016 1.016)))))
        (pin output line (at 10.16 2.54 180) (length 2.54)
          (name "LINE_TX-" (effects (font (size 1.016 1.016))))
          (number "6" (effects (font (size 1.016 1.016)))))
        (pin input line (at 10.16 -2.54 180) (length 2.54)
          (name "LINE_RX+" (effects (font (size 1.016 1.016))))
          (number "7" (effects (font (size 1.016 1.016)))))
        (pin input line (at 10.16 -5.08 180) (length 2.54)
          (name "LINE_RX-" (effects (font (size 1.016 1.016))))
          (number "8" (effects (font (size 1.016 1.016)))))
      )
    )
"""

JST_GH4_SYM = """    (symbol "Conn_JST_GH_04P"
      (pin_names (offset 0.254))
      (pin_numbers (hide yes))
      (property "Reference" "J" (at 0 -7.62 0)
        (effects (font (size 1.27 1.27))))
      (property "Value" "JST_GH_04P" (at 0 7.62 0)
        (effects (font (size 1.27 1.27))))
      (property "Footprint"
        "Connector_JST:JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal"
        (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (property "Datasheet" "https://www.jst-mfg.com/product/pdf/eng/eGH.pdf"
        (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (symbol "Conn_JST_GH_04P_0_1"
        (rectangle (start -3.81 5.08) (end 3.81 -5.08)
          (stroke (width 0) (type default)) (fill (type background))))
      (symbol "Conn_JST_GH_04P_1_1"
        (pin passive line (at -8.89 3.81 0) (length 2.54)
          (name "TX+" (effects (font (size 1.016 1.016))))
          (number "1" (effects (font (size 1.016 1.016)))))
        (pin passive line (at -8.89 1.27 0) (length 2.54)
          (name "TX-" (effects (font (size 1.016 1.016))))
          (number "2" (effects (font (size 1.016 1.016)))))
        (pin passive line (at -8.89 -1.27 0) (length 2.54)
          (name "RX+" (effects (font (size 1.016 1.016))))
          (number "3" (effects (font (size 1.016 1.016)))))
        (pin passive line (at -8.89 -3.81 0) (length 2.54)
          (name "RX-" (effects (font (size 1.016 1.016))))
          (number "4" (effects (font (size 1.016 1.016)))))
      )
    )
"""


# ---------------------------------------------------------------------------
# S-expression helper
# ---------------------------------------------------------------------------


def find_balanced(text: str, start: int) -> int:
    """Return index past closing ')' of balanced S-expr beginning at start."""
    depth = 0
    i = start
    while i < len(text):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return len(text)


# ---------------------------------------------------------------------------
# UUID factory
# ---------------------------------------------------------------------------


class UUIDFactory:
    """Sequential UUID generator with a fixed prefix."""

    def __init__(self, prefix: str, start: int = 950_000_000_001):
        self._prefix = prefix
        self._counter = start

    def next(self) -> str:
        uid = f"{self._prefix}{self._counter:012d}"
        self._counter += 1
        return uid


# ---------------------------------------------------------------------------
# Transformation helpers
# ---------------------------------------------------------------------------


def insert_lib_symbols(content: str, new_syms: str) -> str:
    """Insert lib_symbol definitions just before the closing ) of lib_symbols."""
    # Find the end of (lib_symbols ...) block.
    idx = content.find("  (lib_symbols")
    if idx == -1:
        idx = content.find("(lib_symbols")
    end = find_balanced(content, idx)
    # Insert before the final closing paren of lib_symbols.
    return content[:end - 1] + new_syms + content[end - 1:]


def insert_before_sheet_instances(content: str, new_text: str) -> str:
    """Insert new_text immediately before the (sheet_instances ...) block."""
    marker = "  (sheet_instances"
    idx = content.rfind(marker)
    if idx == -1:
        marker = "(sheet_instances"
        idx = content.rfind(marker)
    if idx == -1:
        return content + new_text
    return content[:idx] + new_text + "\n" + content[idx:]


def remove_noconnects_at_y(content: str, y_values: set) -> str:
    """Remove no_connect markers at X=67.54 for specified Y values."""
    for y in y_values:
        # Flexible match: allow slight float formatting variation.
        pattern = (
            r"\n?\s*\(no_connect \(at 67\.54 "
            + re.escape(f"{y:.2f}")
            + r'\) \(uuid "[^"]+"\)\)'
        )
        content = re.sub(pattern, "", content)
    return content


def remove_orphan_labels_cape_b2(content: str) -> str:
    """
    Remove orphaned global_labels at X in CAPE_B2_ORPHAN_X and
    Y in CAPE_B2_ORPHAN_Y_RANGE — left by gen_cape_b2.py when
    DP83825I instances were removed but their attached labels were not.
    """
    x_pattern = "|".join(re.escape(f"{x:.2f}") for x in CAPE_B2_ORPHAN_X)
    pattern = (
        r'\n?\s*\(global_label "[^"]*" \(shape [^)]+\) \(at '
        r"(?:" + x_pattern + r") "
        r"(?:44[0-9]\.[0-9]+|4[56][0-9]\.[0-9]+|470\.[0-9]+) "
        r'[0-9]+\)[\s\S]*?\(property "Intersheet References"[\s\S]*?\)\)'
    )
    # Use non-greedy match per label block.
    content = re.sub(
        r'\n?\s*\(global_label "[^"]*" \(shape bidirectional\) \(at '
        r"(?:197\.30|222\.70|347\.30|372\.70) "
        r"4[4-6][0-9]\.[0-9]+ [0-9]+\)"
        r"[\s\S]*?"
        r'\(property "Intersheet References" "\$\{INTERSHEET_REFS\}"'
        r"[\s\S]*?\)\)",
        "",
        content,
    )
    return content


# ---------------------------------------------------------------------------
# KiCad element generators
# ---------------------------------------------------------------------------


def make_global_label(
    name: str, x: float, y: float, angle: int, uid: str, ref_uid: str
) -> str:
    """Return a KiCad global_label S-expression string."""
    return (
        f'  (global_label "{name}" (shape bidirectional) (at {x:.2f} {y:.2f} {angle})\n'
        f"    (effects (font (size 1.016 1.016)))\n"
        f'    (uuid "{uid}")\n'
        f'    (property "Intersheet References" "${{INTERSHEET_REFS}}" '
        f"(at {x:.2f} {y:.2f} 0)\n"
        f"      (effects (font (size 1.016 1.016)) (hide yes))))\n"
    )


def make_power_symbol(
    lib_id: str, x: float, y: float, ref: str, uid: str, pin_uid: str
) -> str:
    """Return a KiCad power symbol instance S-expression."""
    val_dy = -2.54 if lib_id == "GND" else 2.54
    return (
        f'  (symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} 0)\n'
        f"    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)\n"
        f'    (uuid "{uid}")\n'
        f'    (property "Reference" "{ref}" (at {x:.2f} {y:.2f} 0)\n'
        f"      (effects (font (size 1.27 1.27)) (hide yes)))\n"
        f'    (property "Value" "{lib_id}" (at {x:.2f} {y + val_dy:.2f} 0)\n'
        f"      (effects (font (size 1.27 1.27))))\n"
        f'    (pin "1" (uuid "{pin_uid}")))\n'
    )


def make_iso7642_instance(
    ref: str, x: float, y: float, uids: list, pin_uids: list
) -> str:
    """Build a ISO7642FDWRR symbol instance."""
    return (
        f'  (symbol (lib_id "ISO7642FDWRR") (at {x:.2f} {y:.2f} 0)\n'
        f"    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)\n"
        f'    (uuid "{uids[0]}")\n'
        f'    (property "Reference" "{ref}" (at {x:.2f} {y - 13.97:.2f} 0)\n'
        f"      (effects (font (size 1.27 1.27))))\n"
        f'    (property "Value" "ISO7642FDWRR" (at {x:.2f} {y + 13.97:.2f} 0)\n'
        f"      (effects (font (size 1.27 1.27))))\n"
        f'    (property "Footprint" "Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm"'
        f" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n"
        + "".join(
            f'    (pin "{n}" (uuid "{pu}"))\n'
            for n, pu in zip(
                [
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    "10",
                    "11",
                    "12",
                    "13",
                    "14",
                    "15",
                    "16",
                ],
                pin_uids,
            )
        )
        + "  )\n"
    )


def make_adin1300_instance(
    ref: str, x: float, y: float, uids: list, pin_uids: list
) -> str:
    """Build an ADIN1300 symbol instance."""
    pin_nums = [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
    ]
    return (
        f'  (symbol (lib_id "ADIN1300") (at {x:.2f} {y:.2f} 0)\n'
        f"    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)\n"
        f'    (uuid "{uids[0]}")\n'
        f'    (property "Reference" "{ref}" (at {x:.2f} {y - 21.59:.2f} 0)\n'
        f"      (effects (font (size 1.27 1.27))))\n"
        f'    (property "Value" "ADIN1300" (at {x:.2f} {y + 21.59:.2f} 0)\n'
        f"      (effects (font (size 1.27 1.27))))\n"
        f'    (property "Footprint" "Package_LGA:LGA-48_7x7mm_P0.5mm"'
        f" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n"
        + "".join(
            f'    (pin "{n}" (uuid "{pu}"))\n' for n, pu in zip(pin_nums, pin_uids)
        )
        + "  )\n"
    )


def make_xfmr_instance(ref: str, x: float, y: float, uids: list, pin_uids: list) -> str:
    """Build a Wurth 749010012A ETH_XFMR symbol instance."""
    return (
        f'  (symbol (lib_id "ETH_XFMR") (at {x:.2f} {y:.2f} 0)\n'
        f"    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)\n"
        f'    (uuid "{uids[0]}")\n'
        f'    (property "Reference" "{ref}" (at {x:.2f} {y - 10.16:.2f} 0)\n'
        f"      (effects (font (size 1.27 1.27))))\n"
        f'    (property "Value" "749010012A" (at {x:.2f} {y + 10.16:.2f} 0)\n'
        f"      (effects (font (size 1.27 1.27))))\n"
        f'    (property "Footprint"'
        f' "Transformer_SMD:Wurth_749010012A_10-100BASE-TX"'
        f" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n"
        + "".join(
            f'    (pin "{n}" (uuid "{pu}"))\n'
            for n, pu in zip(["1", "2", "3", "4", "5", "6", "7", "8"], pin_uids)
        )
        + "  )\n"
    )


def make_jst_instance(ref: str, x: float, y: float, uids: list, pin_uids: list) -> str:
    """Build a JST GH 4-pin Ethernet connector symbol instance."""
    return (
        f'  (symbol (lib_id "Conn_JST_GH_04P") (at {x:.2f} {y:.2f} 0)\n'
        f"    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)\n"
        f'    (uuid "{uids[0]}")\n'
        f'    (property "Reference" "{ref}" (at {x:.2f} {y - 7.62:.2f} 0)\n'
        f"      (effects (font (size 1.27 1.27))))\n"
        f'    (property "Value" "JST_GH_04P" (at {x:.2f} {y + 7.62:.2f} 0)\n'
        f"      (effects (font (size 1.27 1.27))))\n"
        f'    (property "Footprint"'
        f' "Connector_JST:JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal"'
        f" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n"
        + "".join(
            f'    (pin "{n}" (uuid "{pu}"))\n'
            for n, pu in zip(["1", "2", "3", "4"], pin_uids)
        )
        + "  )\n"
    )


# ---------------------------------------------------------------------------
# Main transformation
# ---------------------------------------------------------------------------


def transform(path: str) -> None:
    """Apply the full EMI Ethernet PHY transformation to a CAPE schematic."""
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read()

    is_cape_b = "XO" in path or "cape_b2" in path.lower()

    # Determine UUID prefix from existing content.
    if "a2000000" in content:
        uuid_prefix = "a2000000-0000-0000-0000-"
    elif "b2000000" in content:
        uuid_prefix = "b2000000-0000-0000-0000-"
    else:
        uuid_prefix = "a2000000-0000-0000-0000-"  # fallback

    uf = UUIDFactory(uuid_prefix)

    # -----------------------------------------------------------------------
    # Step 1: Insert new lib_symbols.
    # -----------------------------------------------------------------------
    content = insert_lib_symbols(
        content, ADIN1300_SYM + ISO7642_SYM + ETH_XFMR_SYM + JST_GH4_SYM
    )

    # -----------------------------------------------------------------------
    # Step 2: Remove no_connect markers for RMII0 signals.
    # -----------------------------------------------------------------------
    content = remove_noconnects_at_y(content, set(RMII0_RESTORE.keys()))

    # -----------------------------------------------------------------------
    # Step 3: For XO, remove orphaned PHY-side labels.
    # -----------------------------------------------------------------------
    if is_cape_b:
        content = remove_orphan_labels_cape_b2(content)

    # -----------------------------------------------------------------------
    # Step 4: Build all new schematic elements.
    # -----------------------------------------------------------------------
    new_elements = []

    # 4a. Restore connector-side global_labels for RMII0 / management signals.
    for y_pos, sig_name in RMII0_RESTORE.items():
        new_elements.append(
            make_global_label(sig_name, 67.54, y_pos, 0, uf.next(), uf.next())
        )

    # Component placement geometry (all Y=490 row).
    # ISO7642_TX (U_ISO_TX): MCU side = left, PHY side = right.
    # Pin reach: lib X=-12.70 => schematic offset -12.70-2.54=-15.24 from centre.
    TX_CX, TX_CY = 175.00, 490.00
    TX_A_X = TX_CX - 12.70 - 2.54  # 159.76
    TX_B_X = TX_CX + 12.70 + 2.54  # 190.24

    # ADIN1300 (U_ETH): lib pin reach 17.78 + 2.54 = 20.32.
    ETH_CX, ETH_CY = 280.00, 490.00
    ETH_L_X = ETH_CX - 17.78 - 2.54  # 259.68
    ETH_R_X = ETH_CX + 17.78 + 2.54  # 300.32

    # ISO7642_RX (U_ISO_RX): PHY side = left, MCU side = right.
    RX_CX, RX_CY = 365.00, 490.00
    RX_A_X = RX_CX - 12.70 - 2.54  # 349.76  (PHY-side inputs)
    RX_B_X = RX_CX + 12.70 + 2.54  # 380.24  (MCU-side outputs)

    # ETH_XFMR (T_ETH) — SMD 10/100BASE-TX transformer.  lib pin reach 10.16+2.54=12.70.
    TF_CX, TF_CY = 430.00, 490.00
    TF_L_X = TF_CX - 10.16 - 2.54  # 417.30  (PHY side, from ADIN1300)
    TF_R_X = TF_CX + 10.16 + 2.54  # 442.70  (line side, to JST)

    # JST GH 4P (J_ETH) — lightweight Ethernet harness connector.  lib reach 8.89+2.54=11.43.
    RJ_CX, RJ_CY = 490.00, 490.00
    RJ_L_X = RJ_CX - 8.89 - 2.54  # 478.57  (MDI line signals from transformer)

    # 4b. ISO7642_TX component instance.
    iso_tx_uids = [uf.next()]
    iso_tx_pin_uids = [uf.next() for _ in range(16)]
    new_elements.append(
        make_iso7642_instance("U_ISO_TX", TX_CX, TX_CY, iso_tx_uids, iso_tx_pin_uids)
    )

    # 4c. ADIN1300 component instance.
    adin_uids = [uf.next()]
    adin_pin_uids = [uf.next() for _ in range(19)]
    new_elements.append(
        make_adin1300_instance("U_ETH", ETH_CX, ETH_CY, adin_uids, adin_pin_uids)
    )

    # 4d. ISO7642_RX component instance.
    iso_rx_uids = [uf.next()]
    iso_rx_pin_uids = [uf.next() for _ in range(16)]
    new_elements.append(
        make_iso7642_instance("U_ISO_RX", RX_CX, RX_CY, iso_rx_uids, iso_rx_pin_uids)
    )

    # 4e. SMD Ethernet transformer (T_ETH) and JST connector (J_ETH).
    tf_uids = [uf.next()]
    tf_pin_uids = [uf.next() for _ in range(8)]
    new_elements.append(make_xfmr_instance("T_ETH", TF_CX, TF_CY, tf_uids, tf_pin_uids))
    rj_uids = [uf.next()]
    rj_pin_uids = [uf.next() for _ in range(4)]
    new_elements.append(make_jst_instance("J_ETH", RJ_CX, RJ_CY, rj_uids, rj_pin_uids))

    # 4f. Global labels on ISO7642_TX A-side (MCU side, same names as connector).
    # lib_y: GND_A=+8.89,INA1=+6.35,INA2=+3.81,INA3=+1.27,INA4=-1.27,
    #        INA5=-3.81,INA6=-6.35,VCC_A=-8.89
    tx_a_signals = [
        (TX_CY + 6.35, "RMII0_REF_CLK"),
        (TX_CY + 3.81, "RMII0_TXD0"),
        (TX_CY + 1.27, "RMII0_TXD1"),
        (TX_CY - 1.27, "RMII0_TX_EN"),
        (TX_CY - 3.81, "MDC"),
        (TX_CY - 6.35, "PHY1_RSTN"),
    ]
    for y_pos, sig in tx_a_signals:
        # angle 180 = label arrow points LEFT (away from body toward connector)
        new_elements.append(
            make_global_label(sig, TX_A_X, y_pos, 180, uf.next(), uf.next())
        )

    # 4g. Global labels on ISO7642_TX B-side (isolated PHY-side internal nets).
    tx_b_signals = [
        (TX_CY + 3.81, "ETH_REFCLK_I"),
        (TX_CY + 1.27, "ETH_TXD0_I"),
        (TX_CY - 1.27, "ETH_TXD1_I"),
        (TX_CY - 3.81, "ETH_TXEN_I"),
        (TX_CY - 6.35, "ETH_MDC_I"),
        (TX_CY - 8.89, "ETH_RSTN_I"),
    ]
    for y_pos, sig in tx_b_signals:
        new_elements.append(
            make_global_label(sig, TX_B_X, y_pos, 0, uf.next(), uf.next())
        )

    # 4h. Power symbols on ISO7642_TX.
    new_elements.append(
        make_power_symbol(
            "+3V3", TX_A_X, TX_CY - 8.89, "#PWR_ETH01", uf.next(), uf.next()
        )
    )
    new_elements.append(
        make_power_symbol(
            "GND", TX_A_X, TX_CY + 8.89, "#PWR_ETH02", uf.next(), uf.next()
        )
    )
    new_elements.append(
        make_power_symbol(
            "+3V3", TX_B_X, TX_CY + 8.89, "#PWR_ETH03", uf.next(), uf.next()
        )
    )
    new_elements.append(
        make_power_symbol(
            "GND", TX_B_X, TX_CY + 6.35, "#PWR_ETH04", uf.next(), uf.next()
        )
    )

    # 4i. Global labels on ADIN1300 left side (RMII interface, PHY side).
    # lib_y: REF_CLK=13.97, TXD0=11.43, TXD1=8.89, TX_EN=6.35,
    #        RXD0=3.81, RXD1=1.27, CRS_DV=-1.27, RX_ER=-3.81,
    #        MDC=-6.35, MDIO=-8.89, RESET_N=-11.43, INT_N=-13.97
    eth_l_signals = [
        (ETH_CY + 13.97, "ETH_REFCLK_I"),
        (ETH_CY + 11.43, "ETH_TXD0_I"),
        (ETH_CY + 8.89, "ETH_TXD1_I"),
        (ETH_CY + 6.35, "ETH_TXEN_I"),
        (ETH_CY + 3.81, "ETH_RXD0_I"),
        (ETH_CY + 1.27, "ETH_RXD1_I"),
        (ETH_CY - 1.27, "ETH_CRSDV_I"),
        (ETH_CY - 3.81, "ETH_RXER_I"),
        (ETH_CY - 6.35, "ETH_MDC_I"),
        (ETH_CY - 8.89, "ETH_MDIO_I"),
        (ETH_CY - 11.43, "ETH_RSTN_I"),
        (ETH_CY - 13.97, "ETH_INTRN_I"),
    ]
    for y_pos, sig in eth_l_signals:
        new_elements.append(
            make_global_label(sig, ETH_L_X, y_pos, 180, uf.next(), uf.next())
        )

    # 4j. Global labels on ADIN1300 right side (MDI to RJ45).
    eth_r_signals = [
        (ETH_CY + 8.89, "ETH_TXP"),
        (ETH_CY + 6.35, "ETH_TXN"),
        (ETH_CY - 6.35, "ETH_RXP"),
        (ETH_CY - 8.89, "ETH_RXN"),
    ]
    for y_pos, sig in eth_r_signals:
        new_elements.append(
            make_global_label(sig, ETH_R_X, y_pos, 0, uf.next(), uf.next())
        )

    # 4k. Power symbols on ADIN1300.
    new_elements.append(
        make_power_symbol(
            "+3V3", ETH_R_X, ETH_CY + 13.97, "#PWR_ETH05", uf.next(), uf.next()
        )
    )
    new_elements.append(
        make_power_symbol(
            "+3V3", ETH_R_X, ETH_CY + 11.43, "#PWR_ETH06", uf.next(), uf.next()
        )
    )
    new_elements.append(
        make_power_symbol(
            "GND", ETH_R_X, ETH_CY - 13.97, "#PWR_ETH07", uf.next(), uf.next()
        )
    )

    # 4l. Global labels on ISO7642_RX A-side (PHY-side inputs).
    rx_a_signals = [
        (RX_CY + 6.35, "ETH_RXD0_I"),
        (RX_CY + 3.81, "ETH_RXD1_I"),
        (RX_CY + 1.27, "ETH_CRSDV_I"),
        (RX_CY - 1.27, "ETH_RXER_I"),
        (RX_CY - 3.81, "ETH_INTRN_I"),
        (RX_CY - 6.35, "ETH_MDIO_I"),
    ]
    for y_pos, sig in rx_a_signals:
        new_elements.append(
            make_global_label(sig, RX_A_X, y_pos, 180, uf.next(), uf.next())
        )

    # 4m. Power symbols on ISO7642_RX A-side.
    new_elements.append(
        make_power_symbol(
            "+3V3", RX_A_X, RX_CY - 8.89, "#PWR_ETH08", uf.next(), uf.next()
        )
    )
    new_elements.append(
        make_power_symbol(
            "GND", RX_A_X, RX_CY + 8.89, "#PWR_ETH09", uf.next(), uf.next()
        )
    )

    # 4n. Global labels on ISO7642_RX B-side (MCU-side outputs = RMII0 signals).
    rx_b_signals = [
        (RX_CY + 3.81, "RMII0_RXD0"),
        (RX_CY + 1.27, "RMII0_RXD1"),
        (RX_CY - 1.27, "RMII0_CRS_DV"),
        (RX_CY - 3.81, "RMII0_RX_ER"),
        (RX_CY - 6.35, "PHY1_INTRN"),
        (RX_CY - 8.89, "MDIO"),
    ]
    for y_pos, sig in rx_b_signals:
        new_elements.append(
            make_global_label(sig, RX_B_X, y_pos, 0, uf.next(), uf.next())
        )

    # 4o. Power symbols on ISO7642_RX B-side.
    new_elements.append(
        make_power_symbol(
            "+3V3", RX_B_X, RX_CY + 8.89, "#PWR_ETH10", uf.next(), uf.next()
        )
    )
    new_elements.append(
        make_power_symbol(
            "GND", RX_B_X, RX_CY + 6.35, "#PWR_ETH11", uf.next(), uf.next()
        )
    )

    # 4p. Global labels on ETH_XFMR left side (PHY-side, from ADIN1300 MDI).
    #   lib_y: PHY_TX+=+5.08, PHY_TX-=+2.54, PHY_RX+=-2.54, PHY_RX-=-5.08
    tf_l_signals = [
        (TF_CY + 5.08, "ETH_TXP"),
        (TF_CY + 2.54, "ETH_TXN"),
        (TF_CY - 2.54, "ETH_RXP"),
        (TF_CY - 5.08, "ETH_RXN"),
    ]
    for y_pos, sig in tf_l_signals:
        new_elements.append(
            make_global_label(sig, TF_L_X, y_pos, 180, uf.next(), uf.next())
        )

    # 4q. Global labels on ETH_XFMR right side (line-side, to JST connector).
    #   lib_y: LINE_TX+=+5.08, LINE_TX-=+2.54, LINE_RX+=-2.54, LINE_RX-=-5.08
    tf_r_signals = [
        (TF_CY + 5.08, "ETH_LINE_TXP"),
        (TF_CY + 2.54, "ETH_LINE_TXN"),
        (TF_CY - 2.54, "ETH_LINE_RXP"),
        (TF_CY - 5.08, "ETH_LINE_RXN"),
    ]
    for y_pos, sig in tf_r_signals:
        new_elements.append(
            make_global_label(sig, TF_R_X, y_pos, 0, uf.next(), uf.next())
        )

    # 4r. Global labels on JST connector left side.
    #   lib_y: TX+=+3.81, TX-=+1.27, RX+=-1.27, RX-=-3.81
    jst_signals = [
        (RJ_CY + 3.81, "ETH_LINE_TXP"),
        (RJ_CY + 1.27, "ETH_LINE_TXN"),
        (RJ_CY - 1.27, "ETH_LINE_RXP"),
        (RJ_CY - 3.81, "ETH_LINE_RXN"),
    ]
    for y_pos, sig in jst_signals:
        new_elements.append(
            make_global_label(sig, RJ_L_X, y_pos, 180, uf.next(), uf.next())
        )

    # -----------------------------------------------------------------------
    # Step 5: Insert all new elements.
    # -----------------------------------------------------------------------
    content = insert_before_sheet_instances(content, "".join(new_elements))

    # -----------------------------------------------------------------------
    # Step 6: Write output.
    # -----------------------------------------------------------------------
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)

    print(f"Written : {path}")
    print(f"Lines   : {content.count(chr(10))}")
    # Quick sanity checks.
    for token in (
        "ADIN1300",
        "ISO7642FDWRR",
        "ETH_XFMR",
        "Conn_JST_GH_04P",
        "ETH_TXP",
        "RMII0_TXD0",
        "ETH_REFCLK_I",
        "ETH_LINE_TXP",
    ):
        n = content.count(token)
        status = "OK  " if n > 0 else "FAIL"
        print(f'{status}: "{token}" appears {n}x')
    phy_orphans = sum(
        1
        for line in content.splitlines()
        if "DP83825I" in line
        or (
            "RMII" in line
            and any(f"{x:.2f}" in line for x in [197.30, 222.70, 347.30, 372.70])
        )
    )
    status = "OK  " if phy_orphans == 0 else "WARN"
    print(f"{status}: PHY orphan lines remaining: {phy_orphans}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path/to/CAPE-X-2.kicad_sch>")
        sys.exit(1)
    target = sys.argv[1]
    if not os.path.isfile(target):
        print(f"ERROR: file not found: {target}")
        sys.exit(1)
    transform(target)
