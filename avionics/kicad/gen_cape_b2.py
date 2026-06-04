#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_cape_b2.py  —  Generate CAPE-B-2.kicad_sch from CAPE-B-1.kicad_sch
=======================================================================
Transforms the CAPE-B-1 Comms/Logging/Payload Cape schematic into the
EMI-hardened CAPE-B-2 variant by:

  A. Updating the title block (title, rev, date).
  B. Replacing ATA6561 (non-isolated CAN) with ISOW1044BDFMR
     (isolated CAN transceiver, SOIC-16W, TI).
  C. Replacing MAX3485E (non-isolated RS-485) with ADM2795EBRWZ
     (isolated RS-485, SOIC-20W, ADI).
  D. Removing both DP83825I Ethernet PHY instances and all associated
     nets (RMII, MDC, MDIO, PHYx_*), replacing former connector pins
     with no_connect markers at PB2-P2.
  E. Keeping all other CAPE-B-1 components unchanged.
  F. Adding EMI-hardening passives:
       CMC_CAN   — SRF2012-100Y common-mode choke on CAN_H/CAN_L
       D_CAN     — PRTR5V0U2X TVS array on CAN_H_CMC/CAN_L_CMC
       CMC_RS485 — SRF2012-100Y common-mode choke on RS485_A/B
       D_RS485   — PRTR5V0U2X TVS array on RS485_A_CMC/RS485_B_CMC
       D_1553    — SMAJ33CA TVS on 1553 bus lines
       FB_PWR    — Würth 742792512 ferrite bead on +5V power entry
       X2Y_CAN   — 4.7 nF X2Y cap bridging GND ↔ CAN isolated GND
       X2Y_RS485 — 4.7 nF X2Y cap bridging GND ↔ RS-485 isolated GND
  G. Updating the sheet UUID to b2000000-0000-0000-0000-000000000001.
  H. Remapping all UUID prefixes to "b2000000-0000-0000-0000-".
  I. (v2 EMI) Adding PRTR5V0U2X TVS on the XCVR_RX_RAW input net
     (D_XCVR_TVS at 138, 561.27) — the PRTR5V0U2X lib_symbol is already
     present from step F; only a new instance is added.

Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
         Griffing Technology LLC
Date   : 2026-06-04
License: CC BY 4.0  |  creativecommons.org/licenses/by/4.0

References
----------
  ISOW1044B datasheet  : https://www.ti.com/lit/ds/symlink/isow1044.pdf
  ADM2795E datasheet   : https://www.analog.com/media/en/technical-documentation/data-sheets/ADM2795E.pdf
  SRF2012 datasheet    : https://product.tdk.com/en/search/emc/emc/cmb/info?part_no=SRF2012-100Y
  PRTR5V0U2X datasheet : https://www.nxp.com/docs/en/data-sheet/PRTR5V0U2X.pdf
  SMAJ33CA datasheet   : https://www.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diodes_smaj_datasheet.pdf.pdf
  Würth 742792512      : https://www.we-online.com/en/components/products/EMC/742792512
  Nexperia PRTR5V0U2X  : https://assets.nexperia.com/documents/data-sheet/PRTR5V0U2X.pdf
"""

import re
import sys

# ---------------------------------------------------------------------------
# 1. UTILITY S-EXPRESSION HELPERS
# ---------------------------------------------------------------------------

def find_balanced_sexp(text: str, start: int) -> int:
    """Return the index one past the closing ')' of the s-expression that
    opens at *start*.  The character at *start* must be '('.

    Parameters
    ----------
    text  : The full schematic text.
    start : Index of the opening '(' of the target expression.

    Returns
    -------
    int  — Index of the character immediately after the closing ')'.
           Returns len(text) if no matching ')' is found.
    """
    depth = 0
    i = start
    while i < len(text):
        if text[i] == '(':
            depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return len(text)


def replace_sexp_block(text: str, pattern: str, replacement: str) -> str:
    """Find the first occurrence of *pattern* and replace the complete
    s-expression that begins at that position with *replacement*.

    The function locates the '(' at *pattern* and uses
    find_balanced_sexp() to determine the end of the block.

    Parameters
    ----------
    text        : The full schematic text.
    pattern     : Leading text that identifies the start of the block.
    replacement : Text to substitute in place of the matched block.

    Returns
    -------
    str  — Modified text, or the original text if *pattern* is not found.
    """
    idx = text.find(pattern)
    if idx == -1:
        return text
    end = find_balanced_sexp(text, idx)
    return text[:idx] + replacement + text[end:]


def remove_sexp_block(text: str, pattern: str) -> str:
    """Remove the first s-expression block whose opening matches *pattern*,
    including any immediately trailing whitespace and newline.

    Parameters
    ----------
    text    : The full schematic text.
    pattern : Leading text of the block to remove.

    Returns
    -------
    str  — Text with the matched block removed, or original if not found.
    """
    idx = text.find(pattern)
    if idx == -1:
        return text
    end = find_balanced_sexp(text, idx)
    # Consume only the trailing newline so we don't leave a blank line.
    # Do NOT consume leading spaces of the next block — doing so strips its
    # indentation and breaks subsequent pattern-based removals.
    while end < len(text) and text[end] in '\r\n':
        end += 1
    return text[:idx] + text[end:]


def remove_all_sexp_blocks(text: str, pattern: str) -> str:
    """Repeatedly remove every s-expression block whose opening contains
    *pattern* until none remain.

    Parameters
    ----------
    text    : The full schematic text.
    pattern : Leading text of blocks to remove.

    Returns
    -------
    str  — Text with all matching blocks removed.
    """
    while pattern in text:
        text = remove_sexp_block(text, pattern)
    return text


# ---------------------------------------------------------------------------
# 2. NEW LIB_SYMBOL DEFINITIONS
# ---------------------------------------------------------------------------

# ISOW1044BDFMR — Fully isolated CAN FD transceiver, 5 kV isolation,
# SOIC-16W package (Texas Instruments).
# Pin y-positions are relative to component origin (0,0).
# Placed at schematic (210, 170): schematic_y = origin_y + lib_y_offset.
LIB_ISOW1044BDFMR = """\
  (symbol "ISOW1044BDFMR" (in_bom yes) (on_board yes)
    (pin_names (offset 0.254))
    (pin_numbers (hide yes))
    (property "Reference" "U" (at 0 -12.70 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "ISOW1044BDFMR" (at 0 12.70 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.ti.com/lit/ds/symlink/isow1044.pdf" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "ISOW1044BDFMR_0_1"
      (rectangle (start -10.16 -8.89) (end 10.16 8.89)
        (stroke (width 0.254) (type default)) (fill (type background)))
      (polyline
        (pts (xy 0 8.89) (xy 0 -8.89))
        (stroke (width 0.127) (type dash))
        (fill (type none)))
    )
    (symbol "ISOW1044BDFMR_1_1"
      (pin power_in line (at -12.70 -5.08 0) (length 2.54)
        (name "VCC1" (effects (font (size 1.016 1.016))))
        (number "6" (effects (font (size 1.016 1.016)))))
      (pin input line (at -12.70 -1.27 0) (length 2.54)
        (name "TXD" (effects (font (size 1.016 1.016))))
        (number "2" (effects (font (size 1.016 1.016)))))
      (pin input line (at -12.70 1.27 0) (length 2.54)
        (name "STB_N" (effects (font (size 1.016 1.016))))
        (number "3" (effects (font (size 1.016 1.016)))))
      (pin output line (at -12.70 3.81 0) (length 2.54)
        (name "RXD" (effects (font (size 1.016 1.016))))
        (number "4" (effects (font (size 1.016 1.016)))))
      (pin power_in line (at -12.70 6.35 0) (length 2.54)
        (name "GND1" (effects (font (size 1.016 1.016))))
        (number "1" (effects (font (size 1.016 1.016)))))
      (pin power_out line (at 12.70 -5.08 180) (length 2.54)
        (name "VCC2" (effects (font (size 1.016 1.016))))
        (number "11" (effects (font (size 1.016 1.016)))))
      (pin output line (at 12.70 -2.54 180) (length 2.54)
        (name "CANH" (effects (font (size 1.016 1.016))))
        (number "15" (effects (font (size 1.016 1.016)))))
      (pin output line (at 12.70 0.00 180) (length 2.54)
        (name "CANL" (effects (font (size 1.016 1.016))))
        (number "14" (effects (font (size 1.016 1.016)))))
      (pin power_out line (at 12.70 2.54 180) (length 2.54)
        (name "ISOGND" (effects (font (size 1.016 1.016))))
        (number "10" (effects (font (size 1.016 1.016)))))
    )
  )
"""

# ADM2795EBRWZ — Fully isolated RS-485/RS-422 transceiver, 5 kV isolation,
# SOIC-20W package (Analog Devices).
# Pin y-positions relative to component origin (0,0).
# Placed at schematic (340, 170): schematic_y = origin_y + lib_y_offset.
LIB_ADM2795EBRWZ = """\
  (symbol "ADM2795EBRWZ" (in_bom yes) (on_board yes)
    (pin_names (offset 0.254))
    (pin_numbers (hide yes))
    (property "Reference" "U" (at 0 -12.70 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "ADM2795EBRWZ" (at 0 12.70 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.analog.com/media/en/technical-documentation/data-sheets/ADM2795E.pdf" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "ADM2795EBRWZ_0_1"
      (rectangle (start -10.16 -9.652) (end 10.16 9.652)
        (stroke (width 0.254) (type default)) (fill (type background)))
      (polyline
        (pts (xy 0 9.652) (xy 0 -9.652))
        (stroke (width 0.127) (type dash))
        (fill (type none)))
    )
    (symbol "ADM2795EBRWZ_1_1"
      (pin power_in line (at -12.70 -5.08 0) (length 2.54)
        (name "VCC1" (effects (font (size 1.016 1.016))))
        (number "8" (effects (font (size 1.016 1.016)))))
      (pin input line (at -12.70 -2.54 0) (length 2.54)
        (name "DI" (effects (font (size 1.016 1.016))))
        (number "4" (effects (font (size 1.016 1.016)))))
      (pin input line (at -12.70 0.00 0) (length 2.54)
        (name "DE" (effects (font (size 1.016 1.016))))
        (number "2" (effects (font (size 1.016 1.016)))))
      (pin input line (at -12.70 2.54 0) (length 2.54)
        (name "RE_N" (effects (font (size 1.016 1.016))))
        (number "3" (effects (font (size 1.016 1.016)))))
      (pin output line (at -12.70 5.08 0) (length 2.54)
        (name "RO" (effects (font (size 1.016 1.016))))
        (number "1" (effects (font (size 1.016 1.016)))))
      (pin power_in line (at -12.70 7.62 0) (length 2.54)
        (name "GND1" (effects (font (size 1.016 1.016))))
        (number "5" (effects (font (size 1.016 1.016)))))
      (pin power_in line (at 12.70 -5.08 180) (length 2.54)
        (name "VCC2" (effects (font (size 1.016 1.016))))
        (number "16" (effects (font (size 1.016 1.016)))))
      (pin bidirectional line (at 12.70 -2.54 180) (length 2.54)
        (name "A" (effects (font (size 1.016 1.016))))
        (number "19" (effects (font (size 1.016 1.016)))))
      (pin bidirectional line (at 12.70 0.00 180) (length 2.54)
        (name "B" (effects (font (size 1.016 1.016))))
        (number "18" (effects (font (size 1.016 1.016)))))
      (pin power_in line (at 12.70 2.54 180) (length 2.54)
        (name "GND2" (effects (font (size 1.016 1.016))))
        (number "12" (effects (font (size 1.016 1.016)))))
    )
  )
"""

# SRF2012-100Y — TDK 100 Ω common-mode choke, 0805 (2012 metric) package.
# 4-pin (two windings): L1A-L1B on one differential line,
# L2A-L2B on the other.
# Reference: https://product.tdk.com/en/search/emc/emc/cmb/info?part_no=SRF2012-100Y
LIB_SRF2012 = """\
  (symbol "SRF2012" (in_bom yes) (on_board yes)
    (pin_names (offset 0.254))
    (pin_numbers (hide yes))
    (property "Reference" "L" (at 0 -5.08 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "SRF2012-100Y" (at 0 5.08 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "Inductor_SMD:L_0805_2012Metric" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://product.tdk.com/en/search/emc/emc/cmb/info?part_no=SRF2012-100Y" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "SRF2012_0_1"
      (rectangle (start -2.54 2.54) (end 2.54 -2.54)
        (stroke (width 0.254) (type default)) (fill (type background)))
      (polyline
        (pts (xy -1.27 2.54) (xy -1.27 -2.54))
        (stroke (width 0.127) (type default)) (fill (type none)))
    )
    (symbol "SRF2012_1_1"
      (pin passive line (at -5.08 1.27 0) (length 2.54)
        (name "L1A" (effects (font (size 1.016 1.016))))
        (number "1" (effects (font (size 1.016 1.016)))))
      (pin passive line (at -5.08 -1.27 0) (length 2.54)
        (name "L2A" (effects (font (size 1.016 1.016))))
        (number "2" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 5.08 1.27 180) (length 2.54)
        (name "L1B" (effects (font (size 1.016 1.016))))
        (number "3" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 5.08 -1.27 180) (length 2.54)
        (name "L2B" (effects (font (size 1.016 1.016))))
        (number "4" (effects (font (size 1.016 1.016)))))
    )
  )
"""

# PRTR5V0U2X — NXP 5 V dual-rail TVS ESD protection array, SOT-363.
# Simplified 4-pin schematic symbol: A1, A2 (anodes), K (common cathode), GND.
# Reference: https://www.nxp.com/docs/en/data-sheet/PRTR5V0U2X.pdf
LIB_PRTR5V0U2X = """\
  (symbol "PRTR5V0U2X" (in_bom yes) (on_board yes)
    (pin_names (offset 0.254))
    (pin_numbers (hide yes))
    (property "Reference" "D" (at 0 -6.35 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "PRTR5V0U2X" (at 0 6.35 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_TO_SOT_SMD:SOT-363_SC-70-6" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.nxp.com/docs/en/data-sheet/PRTR5V0U2X.pdf" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "PRTR5V0U2X_0_1"
      (rectangle (start -2.54 3.81) (end 2.54 -3.81)
        (stroke (width 0.254) (type default)) (fill (type background)))
    )
    (symbol "PRTR5V0U2X_1_1"
      (pin passive line (at -5.08 1.27 0) (length 2.54)
        (name "A1" (effects (font (size 1.016 1.016))))
        (number "1" (effects (font (size 1.016 1.016)))))
      (pin passive line (at -5.08 -1.27 0) (length 2.54)
        (name "A2" (effects (font (size 1.016 1.016))))
        (number "2" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 5.08 0.00 180) (length 2.54)
        (name "K" (effects (font (size 1.016 1.016))))
        (number "3" (effects (font (size 1.016 1.016)))))
      (pin power_in line (at 0 5.08 270) (length 2.54)
        (name "GND" (effects (font (size 1.016 1.016))))
        (number "6" (effects (font (size 1.016 1.016)))))
    )
  )
"""

# SMAJ33CA — Littelfuse 33 V bidirectional TVS, DO-214AC (SMA) package.
# Simple 2-pin passive symbol (A, K).
# Reference: Littelfuse SMAJ series datasheet.
LIB_SMAJ33CA = """\
  (symbol "SMAJ33CA" (in_bom yes) (on_board yes)
    (pin_names (offset 0.254))
    (pin_numbers (hide yes))
    (property "Reference" "D" (at 0 -3.81 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "SMAJ33CA" (at 0 3.81 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "Diode_SMD:D_SMA" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diodes_smaj_datasheet.pdf.pdf" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "SMAJ33CA_0_1"
      (rectangle (start -2.54 2.54) (end 2.54 -2.54)
        (stroke (width 0.254) (type default)) (fill (type background)))
    )
    (symbol "SMAJ33CA_1_1"
      (pin passive line (at -5.08 0.00 0) (length 2.54)
        (name "A" (effects (font (size 1.016 1.016))))
        (number "1" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 5.08 0.00 180) (length 2.54)
        (name "K" (effects (font (size 1.016 1.016))))
        (number "2" (effects (font (size 1.016 1.016)))))
    )
  )
"""

# Ferrite_Bead — Würth Elektronik 742792512 ferrite bead, 0805 package,
# 600 Ω @ 100 MHz, 2 A.
# Simple 2-pin passive symbol.
# Reference: https://www.we-online.com/en/components/products/EMC/742792512
LIB_FERRITE_BEAD = """\
  (symbol "Ferrite_Bead" (in_bom yes) (on_board yes)
    (pin_names (offset 0.254))
    (pin_numbers (hide yes))
    (property "Reference" "FB" (at 0 -3.81 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "742792512" (at 0 3.81 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "Inductor_SMD:L_0805_2012Metric" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.we-online.com/en/components/products/EMC/742792512" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "Ferrite_Bead_0_1"
      (rectangle (start -2.54 1.27) (end 2.54 -1.27)
        (stroke (width 0.254) (type default)) (fill (type background)))
    )
    (symbol "Ferrite_Bead_1_1"
      (pin passive line (at -5.08 0.00 0) (length 2.54)
        (name "1" (effects (font (size 1.016 1.016))))
        (number "1" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 5.08 0.00 180) (length 2.54)
        (name "2" (effects (font (size 1.016 1.016))))
        (number "2" (effects (font (size 1.016 1.016)))))
    )
  )
"""

# X2Y_4N7 — 4.7 nF X2Y capacitor for isolated-domain bypass.
# Generic 2-pin passive capacitor symbol.
LIB_X2Y_4N7 = """\
  (symbol "X2Y_4N7" (in_bom yes) (on_board yes)
    (pin_names (offset 0.254))
    (pin_numbers (hide yes))
    (property "Reference" "C" (at 0 -3.81 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "4.7nF_X2Y" (at 0 3.81 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "Capacitor_SMD:C_0402_1005Metric" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "X2Y_4N7_0_1"
      (polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762))
        (stroke (width 0.508) (type default)) (fill (type none)))
      (polyline (pts (xy -2.032 0.762) (xy 2.032 0.762))
        (stroke (width 0.508) (type default)) (fill (type none)))
    )
    (symbol "X2Y_4N7_1_1"
      (pin passive line (at 0 3.81 270) (length 2.54)
        (name "+" (effects (font (size 1.016 1.016))))
        (number "1" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 0 -3.81 90) (length 2.54)
        (name "-" (effects (font (size 1.016 1.016))))
        (number "2" (effects (font (size 1.016 1.016)))))
    )
  )
"""


# ---------------------------------------------------------------------------
# 3. NEW SYMBOL INSTANCE STRINGS
# ---------------------------------------------------------------------------

# ISOW1044BDFMR at (210, 170) — replaces ATA6561.
# Pin endpoint schematic coordinates when placed at (210, 170) with rot=0:
#   TXD  (pin 2) : x=197.30, y=170+(-1.27)=168.73   ← MCAN1_TX
#   STB_N(pin 3) : x=197.30, y=170+(+1.27)=171.27   ← CAN_STB
#   RXD  (pin 4) : x=197.30, y=170+(+3.81)=173.81   ← MCAN1_RX
#   VCC1 (pin 6) : x=197.30, y=170+(-5.08)=164.92
#   GND1 (pin 1) : x=197.30, y=170+(+6.35)=176.35
#   CANH (pin15) : x=222.70, y=170+(-2.54)=167.46   ← CAN_H
#   CANL (pin14) : x=222.70, y=170+(  0  )=170.00   ← CAN_L
#   VCC2 (pin11) : x=222.70, y=170+(-5.08)=164.92
#   ISOGND(pin10): x=222.70, y=170+(+2.54)=172.54
INST_ISOW1044 = """\
  (symbol (lib_id "ISOW1044BDFMR") (at 210.00 170.00 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-000000000199")
    (property "Reference" "CAN-TR" (at 210.00 155.00 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "ISOW1044BDFMR" (at 210.00 185.00 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.ti.com/lit/ds/symlink/isow1044.pdf" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "b2000000-0000-0000-0000-0000000001a1"))
    (pin "2" (uuid "b2000000-0000-0000-0000-0000000001a2"))
    (pin "3" (uuid "b2000000-0000-0000-0000-0000000001a3"))
    (pin "4" (uuid "b2000000-0000-0000-0000-0000000001a4"))
    (pin "6" (uuid "b2000000-0000-0000-0000-0000000001a5"))
    (pin "10" (uuid "b2000000-0000-0000-0000-0000000001a6"))
    (pin "11" (uuid "b2000000-0000-0000-0000-0000000001a7"))
    (pin "14" (uuid "b2000000-0000-0000-0000-0000000001a8"))
    (pin "15" (uuid "b2000000-0000-0000-0000-0000000001a9"))
  )
"""

# Power symbols for ISOW1044 isolated side.
# VCC1 at (197.30, 164.92) — driven from +3V3.
INST_CAN_VCC1 = """\
  (symbol (lib_id "+3V3") (at 197.30 164.92 0)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-0000000001b1")
    (property "Reference" "#PWR0B1" (at 197.30 164.92 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "+3V3" (at 197.30 162.38 0)
      (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "b2000000-0000-0000-0000-0000000001b2"))
  )
"""

# GND1 at (197.30, 176.35) — primary-side ground.
INST_CAN_GND1 = """\
  (symbol (lib_id "GND") (at 197.30 176.35 0)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-0000000001b3")
    (property "Reference" "#PWR0B2" (at 197.30 176.35 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at 197.30 178.89 0)
      (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "b2000000-0000-0000-0000-0000000001b4"))
  )
"""

# VCC2 at (222.70, 164.92) — isolated-side supply (internal regulator output).
INST_CAN_VCC2 = """\
  (symbol (lib_id "+3V3") (at 222.70 164.92 0)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-0000000001b5")
    (property "Reference" "#PWR0B3" (at 222.70 164.92 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "+3V3" (at 222.70 162.38 0)
      (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "b2000000-0000-0000-0000-0000000001b6"))
  )
"""

# ISOGND at (222.70, 172.54) — isolated-side ground.
INST_CAN_ISOGND = """\
  (symbol (lib_id "GND") (at 222.70 172.54 0)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-0000000001b7")
    (property "Reference" "#PWR0B4" (at 222.70 172.54 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at 222.70 175.08 0)
      (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "b2000000-0000-0000-0000-0000000001b8"))
  )
"""

# ADM2795EBRWZ at (340, 170) — replaces MAX3485E.
# Pin endpoint schematic coordinates when placed at (340, 170) with rot=0:
#   DI   (pin 4) : x=327.30, y=170+(-2.54)=167.46   ← RS485_TX
#   DE   (pin 2) : x=327.30, y=170+(  0  )=170.00   ← RS485_DE
#   RE_N (pin 3) : x=327.30, y=170+(+2.54)=172.54   ← RS485_DE (tied)
#   RO   (pin 1) : x=327.30, y=170+(+5.08)=175.08   ← RS485_RX
#   VCC1 (pin 8) : x=327.30, y=170+(-5.08)=164.92
#   GND1 (pin 5) : x=327.30, y=170+(+7.62)=177.62
#   A    (pin19) : x=352.70, y=170+(-2.54)=167.46   ← RS485_A
#   B    (pin18) : x=352.70, y=170+(  0  )=170.00   ← RS485_B
#   VCC2 (pin16) : x=352.70, y=170+(-5.08)=164.92
#   GND2 (pin12) : x=352.70, y=170+(+2.54)=172.54
INST_ADM2795 = """\
  (symbol (lib_id "ADM2795EBRWZ") (at 340.00 170.00 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-000000000212")
    (property "Reference" "RS485" (at 340.00 155.00 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "ADM2795EBRWZ" (at 340.00 185.00 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.analog.com/media/en/technical-documentation/data-sheets/ADM2795E.pdf" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "b2000000-0000-0000-0000-0000000002a1"))
    (pin "2" (uuid "b2000000-0000-0000-0000-0000000002a2"))
    (pin "3" (uuid "b2000000-0000-0000-0000-0000000002a3"))
    (pin "4" (uuid "b2000000-0000-0000-0000-0000000002a4"))
    (pin "5" (uuid "b2000000-0000-0000-0000-0000000002a5"))
    (pin "8" (uuid "b2000000-0000-0000-0000-0000000002a6"))
    (pin "12" (uuid "b2000000-0000-0000-0000-0000000002a7"))
    (pin "16" (uuid "b2000000-0000-0000-0000-0000000002a8"))
    (pin "18" (uuid "b2000000-0000-0000-0000-0000000002a9"))
    (pin "19" (uuid "b2000000-0000-0000-0000-0000000002aa"))
  )
"""

# Power symbols for ADM2795 primary side.
INST_RS485_VCC1 = """\
  (symbol (lib_id "+3V3") (at 327.30 164.92 0)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-0000000002b1")
    (property "Reference" "#PWR0B5" (at 327.30 164.92 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "+3V3" (at 327.30 162.38 0)
      (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "b2000000-0000-0000-0000-0000000002b2"))
  )
"""

INST_RS485_GND1 = """\
  (symbol (lib_id "GND") (at 327.30 177.62 0)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-0000000002b3")
    (property "Reference" "#PWR0B6" (at 327.30 177.62 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at 327.30 180.16 0)
      (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "b2000000-0000-0000-0000-0000000002b4"))
  )
"""

INST_RS485_VCC2 = """\
  (symbol (lib_id "+3V3") (at 352.70 164.92 0)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-0000000002b5")
    (property "Reference" "#PWR0B7" (at 352.70 164.92 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "+3V3" (at 352.70 162.38 0)
      (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "b2000000-0000-0000-0000-0000000002b6"))
  )
"""

INST_RS485_GND2 = """\
  (symbol (lib_id "GND") (at 352.70 172.54 0)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-0000000002b7")
    (property "Reference" "#PWR0B8" (at 352.70 172.54 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at 352.70 175.08 0)
      (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "b2000000-0000-0000-0000-0000000002b8"))
  )
"""

# RE_N tie wire — connects RE_N at (327.30, 172.54) to DE at (327.30, 170.00)
# via a short vertical wire segment.
WIRE_ADM_RE_DE = """\
  (wire (pts (xy 327.30 172.54) (xy 327.30 170.00))
    (uuid "b2000000-0000-0000-0000-0000000002c1"))
"""

# ---------------------------------------------------------------------------
# 4. EMI COMPONENT INSTANCES (Change F)
# ---------------------------------------------------------------------------

# F-1. CMC_CAN at (225, 170) — SRF2012-100Y on CAN_H/CAN_L lines.
# Connects CANH→L1A and CANL→L2A; L1B and L2B drive downstream labels.
# Pin 1 (L1A) at x=225-5.08=219.92, y=170+1.27=171.27
# Pin 2 (L2A) at x=225-5.08=219.92, y=170-1.27=168.73
# Pin 3 (L1B) at x=225+5.08=230.08, y=170+1.27=171.27
# Pin 4 (L2B) at x=225+5.08=230.08, y=170-1.27=168.73
INST_CMC_CAN = """\
  (symbol (lib_id "SRF2012") (at 225.00 170.00 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-000000000f01")
    (property "Reference" "CMC_CAN" (at 225.00 163.65 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "SRF2012-100Y" (at 225.00 176.35 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "Inductor_SMD:L_0805_2012Metric" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://product.tdk.com/en/search/emc/emc/cmb/info?part_no=SRF2012-100Y" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "b2000000-0000-0000-0000-000000000f02"))
    (pin "2" (uuid "b2000000-0000-0000-0000-000000000f03"))
    (pin "3" (uuid "b2000000-0000-0000-0000-000000000f04"))
    (pin "4" (uuid "b2000000-0000-0000-0000-000000000f05"))
  )
"""

# Wires connecting ISOW1044 CANH/CANL outputs to CMC_CAN inputs.
# CANH at (222.70, 167.46) → CMC L1A at (219.92, 171.27):
#   The y-coordinates differ, so route via a junction node.
#   Use a horizontal wire from CANH at y=167.46 to x=219.92,
#   then a vertical stub down to CMC L1A at y=171.27.
# Actually the SRF2012 lib_y: L1A at lib_y=+1.27, placed at center (225,170)
#   → schematic pin at x=225-5.08=219.92, y=170+1.27=171.27
#   CANH connects to CAN_H at y=167.46 — those are different y values;
#   insert short routing wires.
WIRE_CANH_TO_CMC = """\
  (wire (pts (xy 222.70 167.46) (xy 219.92 167.46))
    (uuid "b2000000-0000-0000-0000-000000000f10"))
  (wire (pts (xy 219.92 167.46) (xy 219.92 171.27))
    (uuid "b2000000-0000-0000-0000-000000000f11"))
"""

WIRE_CANL_TO_CMC = """\
  (wire (pts (xy 222.70 170.00) (xy 219.92 170.00))
    (uuid "b2000000-0000-0000-0000-000000000f12"))
  (wire (pts (xy 219.92 170.00) (xy 219.92 168.73))
    (uuid "b2000000-0000-0000-0000-000000000f13"))
"""

# Global labels on CMC_CAN outputs (L1B → CAN_H_CMC, L2B → CAN_L_CMC).
LABEL_CAN_H_CMC = """\
  (global_label "CAN_H_CMC" (shape bidirectional) (at 230.08 171.27 0)
    (effects (font (size 1.016 1.016)))
    (uuid "b2000000-0000-0000-0000-000000000f20")
    (property "Intersheet References" "${INTERSHEET_REFS}" (at 230.08 171.27 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
"""

LABEL_CAN_L_CMC = """\
  (global_label "CAN_L_CMC" (shape bidirectional) (at 230.08 168.73 0)
    (effects (font (size 1.016 1.016)))
    (uuid "b2000000-0000-0000-0000-000000000f21")
    (property "Intersheet References" "${INTERSHEET_REFS}" (at 230.08 168.73 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
"""

# F-2. D_CAN at (245, 175) — PRTR5V0U2X TVS on CAN_H_CMC / CAN_L_CMC.
# Pin 1 (A1) at x=245-5.08=239.92, y=175+1.27=176.27
# Pin 2 (A2) at x=245-5.08=239.92, y=175-1.27=173.73
# Pin 3 (K)  at x=245+5.08=250.08, y=175+0=175.00
# Pin 6 (GND) at x=245, y=175+5.08=180.08 (pin direction=270)
INST_D_CAN = """\
  (symbol (lib_id "PRTR5V0U2X") (at 245.00 175.00 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-000000000f30")
    (property "Reference" "D_CAN" (at 245.00 168.65 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "PRTR5V0U2X" (at 245.00 181.35 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_TO_SOT_SMD:SOT-363_SC-70-6" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.nxp.com/docs/en/data-sheet/PRTR5V0U2X.pdf" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "b2000000-0000-0000-0000-000000000f31"))
    (pin "2" (uuid "b2000000-0000-0000-0000-000000000f32"))
    (pin "3" (uuid "b2000000-0000-0000-0000-000000000f33"))
    (pin "6" (uuid "b2000000-0000-0000-0000-000000000f34"))
  )
"""

# GND symbol for D_CAN pin 6.
INST_D_CAN_GND = """\
  (symbol (lib_id "GND") (at 245.00 180.08 0)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-000000000f35")
    (property "Reference" "#PWR0F1" (at 245.00 180.08 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at 245.00 182.62 0)
      (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "b2000000-0000-0000-0000-000000000f36"))
  )
"""

# Global labels driving D_CAN A1/A2 from CMC outputs.
LABEL_D_CAN_A1 = """\
  (global_label "CAN_H_CMC" (shape bidirectional) (at 239.92 176.27 180)
    (effects (font (size 1.016 1.016)))
    (uuid "b2000000-0000-0000-0000-000000000f37")
    (property "Intersheet References" "${INTERSHEET_REFS}" (at 239.92 176.27 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
"""

LABEL_D_CAN_A2 = """\
  (global_label "CAN_L_CMC" (shape bidirectional) (at 239.92 173.73 180)
    (effects (font (size 1.016 1.016)))
    (uuid "b2000000-0000-0000-0000-000000000f38")
    (property "Intersheet References" "${INTERSHEET_REFS}" (at 239.92 173.73 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
"""

# No-connect on D_CAN K pin (cathode returned to VCC2 internally in SOT-363).
NC_D_CAN_K = """\
  (no_connect (at 250.08 175.00)
    (uuid "b2000000-0000-0000-0000-000000000f39"))
"""

# F-3. CMC_RS485 at (355, 170) — SRF2012-100Y on RS485_A/B lines.
INST_CMC_RS485 = """\
  (symbol (lib_id "SRF2012") (at 355.00 170.00 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-000000000f40")
    (property "Reference" "CMC_RS485" (at 355.00 163.65 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "SRF2012-100Y" (at 355.00 176.35 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "Inductor_SMD:L_0805_2012Metric" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://product.tdk.com/en/search/emc/emc/cmb/info?part_no=SRF2012-100Y" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "b2000000-0000-0000-0000-000000000f41"))
    (pin "2" (uuid "b2000000-0000-0000-0000-000000000f42"))
    (pin "3" (uuid "b2000000-0000-0000-0000-000000000f43"))
    (pin "4" (uuid "b2000000-0000-0000-0000-000000000f44"))
  )
"""

# Wires: ADM2795 A/B → CMC_RS485 inputs.
# A at (352.70, 167.46) → CMC L1A at x=355-5.08=349.92, y=170+1.27=171.27
# B at (352.70, 170.00) → CMC L2A at x=349.92, y=170-1.27=168.73
WIRE_A_TO_CMC_RS485 = """\
  (wire (pts (xy 352.70 167.46) (xy 349.92 167.46))
    (uuid "b2000000-0000-0000-0000-000000000f50"))
  (wire (pts (xy 349.92 167.46) (xy 349.92 171.27))
    (uuid "b2000000-0000-0000-0000-000000000f51"))
"""

WIRE_B_TO_CMC_RS485 = """\
  (wire (pts (xy 352.70 170.00) (xy 349.92 170.00))
    (uuid "b2000000-0000-0000-0000-000000000f52"))
  (wire (pts (xy 349.92 170.00) (xy 349.92 168.73))
    (uuid "b2000000-0000-0000-0000-000000000f53"))
"""

# Global labels for CMC_RS485 outputs.
LABEL_RS485_A_CMC = """\
  (global_label "RS485_A_CMC" (shape bidirectional) (at 360.08 171.27 0)
    (effects (font (size 1.016 1.016)))
    (uuid "b2000000-0000-0000-0000-000000000f60")
    (property "Intersheet References" "${INTERSHEET_REFS}" (at 360.08 171.27 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
"""

LABEL_RS485_B_CMC = """\
  (global_label "RS485_B_CMC" (shape bidirectional) (at 360.08 168.73 0)
    (effects (font (size 1.016 1.016)))
    (uuid "b2000000-0000-0000-0000-000000000f61")
    (property "Intersheet References" "${INTERSHEET_REFS}" (at 360.08 168.73 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
"""

# F-4. D_RS485 at (375, 175) — PRTR5V0U2X TVS.
INST_D_RS485 = """\
  (symbol (lib_id "PRTR5V0U2X") (at 375.00 175.00 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-000000000f70")
    (property "Reference" "D_RS485" (at 375.00 168.65 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "PRTR5V0U2X" (at 375.00 181.35 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_TO_SOT_SMD:SOT-363_SC-70-6" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.nxp.com/docs/en/data-sheet/PRTR5V0U2X.pdf" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "b2000000-0000-0000-0000-000000000f71"))
    (pin "2" (uuid "b2000000-0000-0000-0000-000000000f72"))
    (pin "3" (uuid "b2000000-0000-0000-0000-000000000f73"))
    (pin "6" (uuid "b2000000-0000-0000-0000-000000000f74"))
  )
"""

INST_D_RS485_GND = """\
  (symbol (lib_id "GND") (at 375.00 180.08 0)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-000000000f75")
    (property "Reference" "#PWR0F2" (at 375.00 180.08 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at 375.00 182.62 0)
      (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "b2000000-0000-0000-0000-000000000f76"))
  )
"""

LABEL_D_RS485_A1 = """\
  (global_label "RS485_A_CMC" (shape bidirectional) (at 369.92 176.27 180)
    (effects (font (size 1.016 1.016)))
    (uuid "b2000000-0000-0000-0000-000000000f77")
    (property "Intersheet References" "${INTERSHEET_REFS}" (at 369.92 176.27 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
"""

LABEL_D_RS485_A2 = """\
  (global_label "RS485_B_CMC" (shape bidirectional) (at 369.92 173.73 180)
    (effects (font (size 1.016 1.016)))
    (uuid "b2000000-0000-0000-0000-000000000f78")
    (property "Intersheet References" "${INTERSHEET_REFS}" (at 369.92 173.73 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
"""

NC_D_RS485_K = """\
  (no_connect (at 380.08 175.00)
    (uuid "b2000000-0000-0000-0000-000000000f79"))
"""

# F-5. D_1553 at (295, 365) — SMAJ33CA TVS on 1553 bus lines.
# Placed between BUS_1553_A_P/N global labels and the bus connector.
INST_D_1553 = """\
  (symbol (lib_id "SMAJ33CA") (at 295.00 365.00 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-000000000f80")
    (property "Reference" "D_1553" (at 295.00 358.65 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "SMAJ33CA" (at 295.00 371.35 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "Diode_SMD:D_SMA" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diodes_smaj_datasheet.pdf.pdf" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "b2000000-0000-0000-0000-000000000f81"))
    (pin "2" (uuid "b2000000-0000-0000-0000-000000000f82"))
  )
"""

# GND symbol for D_1553 cathode.
INST_D_1553_GND = """\
  (symbol (lib_id "GND") (at 300.08 365.00 0)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-000000000f83")
    (property "Reference" "#PWR0F3" (at 300.08 365.00 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at 300.08 367.54 0)
      (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "b2000000-0000-0000-0000-000000000f84"))
  )
"""

# Label at D_1553 anode referencing the 1553 A-bus positive signal.
LABEL_D_1553_A = """\
  (global_label "BUS_1553_A_P" (shape bidirectional) (at 289.92 365.00 180)
    (effects (font (size 1.016 1.016)))
    (uuid "b2000000-0000-0000-0000-000000000f85")
    (property "Intersheet References" "${INTERSHEET_REFS}" (at 289.92 365.00 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
"""

# F-6. FB_PWR at (80, 123.09) — ferrite bead on +5V power entry.
# Inserted between the PB2-P1 +5V output and the +5V power rail.
# Original +5V symbol was at (72.62, 123.09); move it to (88.17, 123.09)
# and insert the ferrite bead between x=72.62 and x=88.17.
INST_FB_PWR = """\
  (symbol (lib_id "Ferrite_Bead") (at 80.39 123.09 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-000000000f90")
    (property "Reference" "FB_PWR" (at 80.39 119.28 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "742792512" (at 80.39 126.90 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "Inductor_SMD:L_0805_2012Metric" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.we-online.com/en/components/products/EMC/742792512" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "b2000000-0000-0000-0000-000000000f91"))
    (pin "2" (uuid "b2000000-0000-0000-0000-000000000f92"))
  )
"""

# +5V symbol moved to right of ferrite bead.
INST_5V_FILTERED = """\
  (symbol (lib_id "+5V") (at 88.17 123.09 0)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-000000000f93")
    (property "Reference" "#PWR0F4" (at 88.17 123.09 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "+5V" (at 88.17 125.63 0)
      (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "b2000000-0000-0000-0000-000000000f94"))
  )
"""

# Wire connecting FB_PWR pin 2 output to the +5V symbol.
WIRE_FB_5V = """\
  (wire (pts (xy 85.47 123.09) (xy 88.17 123.09))
    (uuid "b2000000-0000-0000-0000-000000000f95"))
"""

# Wire from the connector side through FB_PWR pin 1.
WIRE_CONN_FB = """\
  (wire (pts (xy 72.62 123.09) (xy 75.31 123.09))
    (uuid "b2000000-0000-0000-0000-000000000f96"))
"""

# F-7. X2Y_CAN at (230, 182) — 4.7 nF X2Y cap bridging GND to CAN isolated GND.
INST_X2Y_CAN = """\
  (symbol (lib_id "X2Y_4N7") (at 230.00 182.00 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-000000000fa0")
    (property "Reference" "X2Y_CAN" (at 230.00 176.92 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "4.7nF_X2Y" (at 230.00 187.08 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "Capacitor_SMD:C_0402_1005Metric" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "b2000000-0000-0000-0000-000000000fa1"))
    (pin "2" (uuid "b2000000-0000-0000-0000-000000000fa2"))
  )
"""

INST_X2Y_CAN_GND_TOP = """\
  (symbol (lib_id "GND") (at 230.00 178.19 0)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-000000000fa3")
    (property "Reference" "#PWR0FA1" (at 230.00 178.19 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at 230.00 175.65 0)
      (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "b2000000-0000-0000-0000-000000000fa4"))
  )
"""

INST_X2Y_CAN_GND_BOT = """\
  (symbol (lib_id "GND") (at 230.00 185.81 0)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-000000000fa5")
    (property "Reference" "#PWR0FA2" (at 230.00 185.81 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at 230.00 188.35 0)
      (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "b2000000-0000-0000-0000-000000000fa6"))
  )
"""

# F-8. X2Y_RS485 at (360, 182) — 4.7 nF X2Y cap bridging GND to RS-485 isolated GND.
INST_X2Y_RS485 = """\
  (symbol (lib_id "X2Y_4N7") (at 360.00 182.00 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-000000000fb0")
    (property "Reference" "X2Y_RS485" (at 360.00 176.92 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "4.7nF_X2Y" (at 360.00 187.08 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "Capacitor_SMD:C_0402_1005Metric" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "b2000000-0000-0000-0000-000000000fb1"))
    (pin "2" (uuid "b2000000-0000-0000-0000-000000000fb2"))
  )
"""

INST_X2Y_RS485_GND_TOP = """\
  (symbol (lib_id "GND") (at 360.00 178.19 0)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-000000000fb3")
    (property "Reference" "#PWR0FB1" (at 360.00 178.19 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at 360.00 175.65 0)
      (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "b2000000-0000-0000-0000-000000000fb4"))
  )
"""

INST_X2Y_RS485_GND_BOT = """\
  (symbol (lib_id "GND") (at 360.00 185.81 0)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "b2000000-0000-0000-0000-000000000fb5")
    (property "Reference" "#PWR0FB2" (at 360.00 185.81 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at 360.00 188.35 0)
      (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "b2000000-0000-0000-0000-000000000fb6"))
  )
"""

# ---------------------------------------------------------------------------
# 4b. XCVR_RX_RAW TVS protection — Change I (v2 EMI addition)
# ---------------------------------------------------------------------------

def inst_xcvr_rx_tvs(cx: float, cy: float) -> str:
    """Return the PRTR5V0U2X TVS instance on the XCVR_RX_RAW input line.

    D_XCVR_TVS is placed at (*cx*, *cy*) = (138, 561.27) on the
    XCVR_RX_RAW net.  The TVS clamps transients from the external 49 MHz
    XCVR module before they reach U_SBUS_B and SW1.

    The PRTR5V0U2X lib_symbol is already present in CAPE-B-2 (inserted by
    the existing gen_cape_b2.py for CAN and RS-485 protection in step F).
    This function adds a new instance only — no new lib_symbol is needed.

    Pin tips derived from lib_sym_prtr5v0u2x() geometry (pins at ±5.08 x,
    ±1.27 y for A1/A2, 0 y for K):
      A1 tip at (cx − 5.08, cy + 1.27)  →  global XCVR_RX_RAW (angle=180)
      A2 tip at (cx − 5.08, cy − 1.27)  →  no_connect (unused TVS channel)
      K  tip at (cx + 5.08, cy + 0.00)  →  GND power (0°)
      GND pin is internal (angle=270 at cy + 5.08) → GND power

    Note: The gen_cape_b2.py PRTR5V0U2X lib_symbol has 4 pins (A1, A2, K,
    GND at pin 6 pointing down).  We add a GND power symbol for the GND pin.

    Args:
        cx: Component centre X coordinate in mm  (138).
        cy: Component centre Y coordinate in mm  (561.27).

    Returns:
        A multi-line string with the D_XCVR_TVS symbol instance plus
        its connections.
    """
    # The PRTR5V0U2X lib in gen_cape_b2.py has:
    #   A1 at (-5.08, +1.27, 0)  tip = (cx-5.08, cy+1.27)
    #   A2 at (-5.08, -1.27, 0)  tip = (cx-5.08, cy-1.27)
    #   K  at (+5.08, 0.00, 180) tip = (cx+5.08, cy)
    #   GND at (0, +5.08, 270)   tip = (cx, cy+5.08)  [power_in pin pointing down]
    left_x = cx - 5.08          # 132.92
    right_x = cx + 5.08         # 143.08
    y_a1 = cy + 1.27            # 562.54
    y_a2 = cy - 1.27            # 560.00
    y_k = cy                    # 561.27
    y_gnd_pin = cy + 5.08       # 566.35

    # UUIDs use the b2000000 prefix directly since this string is inserted
    # before UUID remapping (step H).
    inst_uuid = "b2000000-0000-0000-0000-000000000fc0"
    p1_uuid = "b2000000-0000-0000-0000-000000000fc1"
    p2_uuid = "b2000000-0000-0000-0000-000000000fc2"
    p3_uuid = "b2000000-0000-0000-0000-000000000fc3"
    p6_uuid = "b2000000-0000-0000-0000-000000000fc4"
    lbl_uuid = "b2000000-0000-0000-0000-000000000fc5"
    nc_uuid = "b2000000-0000-0000-0000-000000000fc6"
    gnd_inst_uuid = "b2000000-0000-0000-0000-000000000fc7"
    gnd_pwr_uuid = "b2000000-0000-0000-0000-000000000fc8"

    return f'''\
  (symbol (lib_id "PRTR5V0U2X") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{inst_uuid}")
    (property "Reference" "D_XCVR_TVS" (at {cx:.2f} {cy - 6.35:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "PRTR5V0U2X" (at {cx:.2f} {cy + 6.35:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_TO_SOT_SMD:SOT-363_SC-70-6" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://assets.nexperia.com/documents/data-sheet/PRTR5V0U2X.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{p1_uuid}"))
    (pin "2" (uuid "{p2_uuid}"))
    (pin "3" (uuid "{p3_uuid}"))
    (pin "6" (uuid "{p6_uuid}"))
  )
  (global_label "XCVR_RX_RAW" (shape bidirectional) (at {left_x:.2f} {y_a1:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{lbl_uuid}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_x:.2f} {y_a1:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (no_connect (at {left_x:.2f} {y_a2:.2f}) (uuid "{nc_uuid}"))
  (symbol (lib_id "GND") (at {right_x:.2f} {y_k:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{gnd_inst_uuid}")
    (property "Reference" "#PWR0FC1" (at {right_x:.2f} {y_k:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at {right_x + 2.54:.2f} {y_k:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{gnd_pwr_uuid}"))
  )'''


# ---------------------------------------------------------------------------
# 5. NO-CONNECT MARKERS for former PHY connector pins on PB2-P2
# ---------------------------------------------------------------------------
# PB2-P2 is at (65, 430).  Connector pin endpoints at x=67.54.
# RMII / MDC / MDIO / PHYx_* labels formerly connected at these y-values
# (from CAPE-B-1 line 1089–1198):
#   390.63, 393.17, 395.71, 398.25, 400.79, 403.33, 405.87, 408.41  (RMII0)
#   410.95, 413.49, 416.03, 418.57, 421.11, 423.65, 426.19, 428.73  (RMII1)
#   431.27 (MDC), 433.81 (MDIO),
#   436.35 (PHY1_INTRN), 438.89 (PHY1_RSTN),
#   441.43 (PHY2_INTRN), 443.97 (PHY2_RSTN)

PHY_NC_Y = [
    390.63, 393.17, 395.71, 398.25, 400.79, 403.33, 405.87, 408.41,
    410.95, 413.49, 416.03, 418.57, 421.11, 423.65, 426.19, 428.73,
    431.27, 433.81,
    436.35, 438.89,
    441.43, 443.97,
]

def build_phy_no_connects() -> str:
    """Build no_connect marker strings for all former PHY connector pins."""
    parts = []
    for i, y in enumerate(PHY_NC_Y):
        uid = f"b2000000-0000-0000-0000-00000000nc{i:02d}"
        parts.append(
            f"  (no_connect (at 67.54 {y:.2f})\n"
            f"    (uuid \"{uid}\"))\n"
        )
    return "".join(parts)


# ---------------------------------------------------------------------------
# 6. UUID REMAPPING (Change H)
# ---------------------------------------------------------------------------

def remap_uuids(text: str) -> str:
    """Replace all UUID prefix '00000000-0000-0000-0000-' with
    'b2000000-0000-0000-0000-' throughout the schematic.

    This canonically distinguishes CAPE-B-2 objects from CAPE-B-1 objects
    and satisfies change H in the specification.

    Parameters
    ----------
    text : The full schematic text (after all other transformations).

    Returns
    -------
    str  — Text with remapped UUIDs.
    """
    return text.replace(
        "00000000-0000-0000-0000-",
        "b2000000-0000-0000-0000-"
    )


# ---------------------------------------------------------------------------
# 7. MAIN TRANSFORMATION PIPELINE
# ---------------------------------------------------------------------------

def transform(src: str) -> str:
    """Apply all CAPE-B-2 transformations to the CAPE-B-1 source text.

    Parameters
    ----------
    src : The raw content of CAPE-B-1.kicad_sch.

    Returns
    -------
    str  — The transformed CAPE-B-2 schematic text.
    """
    text = src

    # ------------------------------------------------------------------
    # A. Title block update
    # ------------------------------------------------------------------
    text = text.replace(
        '(title "CAPE-B-1")',
        '(title "CAPE-B-2 EMI-Hardened Comms, Logging & Payload Cape")'
    )
    text = text.replace(
        '(date "2026-05-21")',
        '(date "2026-06-03")'
    )
    text = text.replace(
        '(rev "M")',
        '(rev "2")'
    )

    # ------------------------------------------------------------------
    # B. Replace ATA6561 lib_symbol with ISOW1044BDFMR
    # ------------------------------------------------------------------
    text = replace_sexp_block(
        text,
        '  (symbol "ATA6561"',
        LIB_ISOW1044BDFMR
    )

    # ------------------------------------------------------------------
    # C. Replace MAX3485E lib_symbol with ADM2795EBRWZ
    # ------------------------------------------------------------------
    text = replace_sexp_block(
        text,
        '  (symbol "MAX3485E"',
        LIB_ADM2795EBRWZ
    )

    # ------------------------------------------------------------------
    # F (lib_symbols). Insert new EMI lib_symbols before closing ')' of
    # lib_symbols block.  The closing tag in CAPE-B-1 is '  )\n' on its
    # own line immediately before the first symbol instance.
    # ------------------------------------------------------------------
    new_libs = (
        LIB_SRF2012 +
        LIB_PRTR5V0U2X +
        LIB_SMAJ33CA +
        LIB_FERRITE_BEAD +
        LIB_X2Y_4N7
    )
    # The lib_symbols block ends with exactly '  )\n' on its own line.
    text = text.replace('  )\n  (symbol (lib_id "Conn_36")',
                        new_libs + '  )\n  (symbol (lib_id "Conn_36")',
                        1)

    # ------------------------------------------------------------------
    # B (instances). Replace ATA6561 symbol instance with ISOW1044BDFMR.
    # ------------------------------------------------------------------
    text = replace_sexp_block(
        text,
        '  (symbol (lib_id "ATA6561")',
        INST_ISOW1044 +
        INST_CAN_VCC1 +
        INST_CAN_GND1 +
        INST_CAN_VCC2 +
        INST_CAN_ISOGND
    )

    # ------------------------------------------------------------------
    # C (instances). Replace MAX3485E symbol instance with ADM2795EBRWZ.
    # ------------------------------------------------------------------
    text = replace_sexp_block(
        text,
        '  (symbol (lib_id "MAX3485E")',
        INST_ADM2795 +
        INST_RS485_VCC1 +
        INST_RS485_GND1 +
        INST_RS485_VCC2 +
        INST_RS485_GND2 +
        WIRE_ADM_RE_DE
    )

    # ------------------------------------------------------------------
    # D. Remove both DP83825I lib_symbol and all instances.
    # ------------------------------------------------------------------
    # Remove lib_symbol definition.
    text = remove_sexp_block(text, '  (symbol "DP83825I"')

    # Remove ETH1-PHY instance block (at 210, 455).
    text = remove_sexp_block(text, '  (symbol (lib_id "DP83825I") (at 210.00 455.00')

    # Remove ETH2-PHY instance block (at 360, 455).
    text = remove_sexp_block(text, '  (symbol (lib_id "DP83825I") (at 360.00 455.00')

    # Remove global labels containing RMII, MDC, MDIO, PHY in their name.
    # These appear in two groups:
    #   (a) on PB2-P2 connector side (near y=390..444)
    #   (b) on PHY component side (near y=440..465 and 447..465)
    phy_label_patterns = [
        '  (global_label "RMII0_TXD0"',
        '  (global_label "RMII0_TXD1"',
        '  (global_label "RMII0_TX_EN"',
        '  (global_label "RMII0_RXD0"',
        '  (global_label "RMII0_RXD1"',
        '  (global_label "RMII0_CRS_DV"',
        '  (global_label "RMII0_RX_ER"',
        '  (global_label "RMII0_REF_CLK"',
        '  (global_label "RMII1_TXD0"',
        '  (global_label "RMII1_TXD1"',
        '  (global_label "RMII1_TX_EN"',
        '  (global_label "RMII1_RXD0"',
        '  (global_label "RMII1_RXD1"',
        '  (global_label "RMII1_CRS_DV"',
        '  (global_label "RMII1_RX_ER"',
        '  (global_label "RMII1_REF_CLK"',
        '  (global_label "MDC"',
        '  (global_label "MDIO"',
        '  (global_label "PHY1_INTRN"',
        '  (global_label "PHY1_RSTN"',
        '  (global_label "PHY2_INTRN"',
        '  (global_label "PHY2_RSTN"',
        '  (global_label "ETH1_TX_P"',
        '  (global_label "ETH1_TX_N"',
        '  (global_label "ETH1_RX_P"',
        '  (global_label "ETH1_RX_N"',
        '  (global_label "ETH2_TX_P"',
        '  (global_label "ETH2_TX_N"',
        '  (global_label "ETH2_RX_P"',
        '  (global_label "ETH2_RX_N"',
    ]
    for pat in phy_label_patterns:
        text = remove_all_sexp_blocks(text, pat)

    # Remove the two blank wires that connected GND/+5V to PB2-P2 first
    # two pins (lines 1085-1088 in original, now at (67.54, 385.55) and
    # (67.54, 388.09)).
    # NOTE: Those wires are kept — they connect the GND and +5V symbols
    # that remain.  Only the PHY-related content is removed.

    # Remove PHY-side power symbols (GND at 72.62,385.55 and +5V at 72.62,388.09)
    # are KEPT because they supply the PB2-P2 power header pins (non-PHY use).

    # Add no_connect markers for the freed connector pins.
    nc_block = build_phy_no_connects()

    # ------------------------------------------------------------------
    # F (instances). Insert all EMI components.
    # Replace the original CAN_H global label (output of ISOW1044 CANH)
    # with the wires + CMC + TVS chain, then re-insert the terminal labels.
    # ------------------------------------------------------------------

    # The original CAPE-B-1 had:
    #   (global_label "CAN_H" ... (at 222.70 167.46 0) ...)
    #   (global_label "CAN_L" ... (at 222.70 170.00 0) ...)
    # Replace them with wires routing to CMC_CAN.
    text = replace_sexp_block(
        text,
        '  (global_label "CAN_H" (shape bidirectional) (at 222.70 167.46 0)',
        WIRE_CANH_TO_CMC
    )
    text = replace_sexp_block(
        text,
        '  (global_label "CAN_L" (shape bidirectional) (at 222.70 170.00 0)',
        WIRE_CANL_TO_CMC
    )

    # Replace original RS485_A / RS485_B labels with routing wires.
    text = replace_sexp_block(
        text,
        '  (global_label "RS485_A" (shape bidirectional) (at 352.70 167.46 0)',
        WIRE_A_TO_CMC_RS485
    )
    text = replace_sexp_block(
        text,
        '  (global_label "RS485_B" (shape bidirectional) (at 352.70 170.00 0)',
        WIRE_B_TO_CMC_RS485
    )

    # Replace original +5V power symbol at (72.62, 123.09) with FB_PWR chain.
    text = replace_sexp_block(
        text,
        '  (symbol (lib_id "+5V") (at 72.62 123.09 0)',
        INST_FB_PWR + INST_5V_FILTERED + WIRE_FB_5V + WIRE_CONN_FB
    )

    # Append all new EMI instances before the closing ')' of the schematic.
    emi_block = (
        INST_CMC_CAN +
        LABEL_CAN_H_CMC +
        LABEL_CAN_L_CMC +
        INST_D_CAN +
        INST_D_CAN_GND +
        LABEL_D_CAN_A1 +
        LABEL_D_CAN_A2 +
        NC_D_CAN_K +
        INST_CMC_RS485 +
        LABEL_RS485_A_CMC +
        LABEL_RS485_B_CMC +
        INST_D_RS485 +
        INST_D_RS485_GND +
        LABEL_D_RS485_A1 +
        LABEL_D_RS485_A2 +
        NC_D_RS485_K +
        INST_D_1553 +
        INST_D_1553_GND +
        LABEL_D_1553_A +
        INST_X2Y_CAN +
        INST_X2Y_CAN_GND_TOP +
        INST_X2Y_CAN_GND_BOT +
        INST_X2Y_RS485 +
        INST_X2Y_RS485_GND_TOP +
        INST_X2Y_RS485_GND_BOT +
        nc_block
    )

    # Insert EMI block before the final closing paren of the schematic.
    assert text.rstrip().endswith(')'), "Unexpected schematic ending"
    text = text.rstrip()[:-1] + emi_block + ")\n"

    # ------------------------------------------------------------------
    # I. Add PRTR5V0U2X TVS on the XCVR_RX_RAW net (D_XCVR_TVS).
    #    The PRTR5V0U2X lib_symbol is already present from step F above.
    #    We append a new instance before the final closing ')'.
    # ------------------------------------------------------------------
    xcvr_tvs_block = inst_xcvr_rx_tvs(138.0, 561.27)
    assert text.rstrip().endswith(')'), "Unexpected schematic ending after EMI block"
    text = text.rstrip()[:-1] + xcvr_tvs_block + "\n)\n"

    # ------------------------------------------------------------------
    # G. Update sheet UUID.
    # ------------------------------------------------------------------
    # The sheet-level uuid is embedded in the kicad_sch outer s-expression
    # as a (uuid ...) token at the top level.  CAPE-B-1 doesn't have an
    # explicit (uuid ...) at the top level (it is per-symbol), so we add
    # a sheet description block if absent, or simply let the UUID remap
    # in step H cover any existing sheet uuid tag.

    # Ensure the schematic carries the canonical CAPE-B-2 sheet uuid by
    # inserting it just after the (paper "A1") line.
    SHEET_UUID_LINE = '  (uuid "b2000000-0000-0000-0000-000000000001")\n'
    if '(uuid "b2000000-0000-0000-0000-000000000001")' not in text:
        text = text.replace(
            '  (paper "A1")\n',
            '  (paper "A1")\n' + SHEET_UUID_LINE,
            1
        )

    # ------------------------------------------------------------------
    # H. Remap all UUID prefixes.
    # ------------------------------------------------------------------
    text = remap_uuids(text)

    return text


# ---------------------------------------------------------------------------
# 8. ENTRY POINT
# ---------------------------------------------------------------------------

def main() -> int:
    """Read CAPE-B-1.kicad_sch, apply all transforms, write CAPE-B-2.kicad_sch.

    Returns
    -------
    int  — 0 on success, 1 on error.
    """
    import pathlib

    script_dir = pathlib.Path(__file__).parent.resolve()
    src_path = script_dir / "CAPE-B-1.kicad_sch"
    dst_path = script_dir / "CAPE-B-2.kicad_sch"

    print(f"Reading  : {src_path}")
    try:
        src_text = src_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"ERROR: source file not found: {src_path}", file=sys.stderr)
        return 1

    print("Transforming ...")
    dst_text = transform(src_text)

    print(f"Writing  : {dst_path}")
    dst_path.write_text(dst_text, encoding="utf-8")

    # ---- Quick sanity checks ----------------------------------------
    line_count = dst_text.count('\n')
    print(f"Lines    : {line_count}")

    ok = True

    # Must contain new EMI parts.
    for token in ["ISOW1044BDFMR", "ADM2795EBRWZ", "SRF2012", "PRTR5V0U2X",
                  "SMAJ33CA", "Ferrite_Bead", "X2Y_4N7"]:
        n = dst_text.count(token)
        if n == 0:
            print(f"FAIL: '{token}' not found in output", file=sys.stderr)
            ok = False
        else:
            print(f"OK   : '{token}' appears {n} time(s)")

    # Must NOT contain removed parts.
    for token in ["DP83825I", "ATA6561", "MAX3485E"]:
        n = dst_text.count(token)
        if n != 0:
            print(f"FAIL: '{token}' still present ({n} occurrences)",
                  file=sys.stderr)
            ok = False
        else:
            print(f"OK   : '{token}' absent (correctly removed/replaced)")

    # RMII/MDC/MDIO labels should be gone.
    for token in ["RMII", "\"MDC\"", "\"MDIO\""]:
        n = dst_text.count(token)
        if n != 0:
            print(f"FAIL: PHY signal '{token}' still present ({n}x)",
                  file=sys.stderr)
            ok = False
        else:
            print(f"OK   : '{token}' absent")

    # Rev and title updated.
    if '(rev "2")' in dst_text:
        print("OK   : rev=\"2\" present")
    else:
        print("FAIL: rev not updated", file=sys.stderr)
        ok = False

    if "CAPE-B-2" in dst_text:
        print("OK   : title contains CAPE-B-2")
    else:
        print("FAIL: title not updated", file=sys.stderr)
        ok = False

    # Sheet UUID present.
    if "b2000000-0000-0000-0000-000000000001" in dst_text:
        print("OK   : sheet UUID b2000000-…-0001 present")
    else:
        print("FAIL: sheet UUID missing", file=sys.stderr)
        ok = False

    # Old UUID prefix should be gone.
    if "00000000-0000-0000-0000-" in dst_text:
        print("FAIL: old UUID prefix still present", file=sys.stderr)
        ok = False
    else:
        print("OK   : old UUID prefix replaced")

    if ok:
        print("\nAll checks passed.")
    else:
        print("\nOne or more checks FAILED — review output.", file=sys.stderr)

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
