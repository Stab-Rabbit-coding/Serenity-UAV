#!/usr/bin/env python3
"""
gen_cape_a2.py — Transform CAPE-A-1.kicad_sch into CAPE-A-2.kicad_sch.

CAPE-A-2 is the EMI-hardened variant of the Flight Control & Sensor Cape for
the Serenity UAV project.  This script performs the following transformations:

  A. Updates the title block (title, rev, date).
  B. Replaces the ATA6561 CAN transceiver lib_symbol with ISOW1044BDFMR
     (isolated CAN, SOIC-16W) and updates the corresponding symbol instance
     and associated global_labels.
  C. Replaces the MAX3485E RS-485 transceiver lib_symbol with ADM2795EBRWZ
     (isolated RS-485, SOIC-20W) and updates the corresponding symbol instance.
  D. Removes both DP83825I Ethernet PHY instances, their lib_symbol definition,
     all associated global_labels (RMII*, MDC, MDIO, PHY*_INTRN/RSTN, ETH*),
     associated power symbols and wires, and adds no_connect markers on the
     PB2-P2 connector pins that previously drove those signals.
  E. Adds new EMI protection components: SRF2012-100Y common-mode chokes,
     PRTR5V0U2X TVS diodes, SMAJ33CA 1553 TVS, and a Würth 742792512 ferrite bead.
  F. Adds X2Y capacitors bridging isolation ground planes.
  G. Updates the sheet UUID to the CAPE-A-2 canonical value.
  H. Remaps all UUIDs to use the "a2000000-0000-0000-0000-" prefix so that
     CAPE-A-2 is unambiguously distinct from CAPE-A-1.
  I. (v2 sensor upgrades) Replaces QMC5883L magnetometer lib_symbol and instance
     with MMC5983MA (MEMSIC, 18-bit, AEC-Q100) — same 5-pin I²C interface.
  J. (v2 sensor upgrades) Replaces INA219AIDR lib_symbol and instance with
     INA226AIDGSR (TI, VSSOP-8, 16-bit, 36 V) — compatible net connections.
  K. (v2 EMI) Adds PRTR5V0U2X TVS on the SBUS_RAW input line (D_SBUS_TVS).

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
         Griffing Technology LLC
License: CC BY 4.0  |  creativecommons.org/licenses/by/4.0
Date:    2026-06-04
Project: Serenity UAV — EDF Tilt-Rotor UAV

References:
  - Texas Instruments ISOW1044BDFMR datasheet (SLLSEO9, 2023)
  - Analog Devices ADM2795EBRWZ datasheet (Rev. C, 2022)
  - Würth Elektronik 742792512 ferrite bead datasheet
  - Nexperia PRTR5V0U2X datasheet (Rev. 5, 2021)
  - Coilcraft SRF2012-100Y datasheet (2020)
  - MEMSIC MMC5983MA datasheet (Rev. C, 2022)
  - Texas Instruments INA226AIDGSR datasheet (SBOS547, 2011)
  - KiCad S-expression schematic format, version 20240101
"""

import re
import sys
import os

# ---------------------------------------------------------------------------
# File paths (absolute, per project convention)
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(SCRIPT_DIR, "CAPE-A-1.kicad_sch")
DST_PATH = os.path.join(SCRIPT_DIR, "CAPE-A-2.kicad_sch")

# ---------------------------------------------------------------------------
# UUID remapping constants
# ---------------------------------------------------------------------------
# All original CAPE-A-1 UUIDs use "00000000-0000-0000-0000-" as prefix.
# CAPE-A-2 uses "a2000000-0000-0000-0000-" so the two schematics are
# unambiguously distinct in any KiCad project database.
OLD_UUID_PREFIX = "00000000-0000-0000-0000-"
NEW_UUID_PREFIX = "a2000000-0000-0000-0000-"

# New sequential UUID counter for newly-inserted elements.
# We start at 900000000001 to avoid collisions with remapped originals.
_uuid_counter = 900000000001


def next_uuid() -> str:
    """Return the next sequential UUID with the CAPE-A-2 prefix.

    Sequential UUIDs keep the schematic deterministic and reproducible.
    The counter starts at 900000000001 so new UUIDs sort after all
    remapped originals (which end at most at 000000000370 in A-1).
    """
    global _uuid_counter
    uid = f"{NEW_UUID_PREFIX}{_uuid_counter:012d}"
    _uuid_counter += 1
    return uid


# ---------------------------------------------------------------------------
# Helper: find matching closing paren for an S-expression block
# ---------------------------------------------------------------------------

def find_balanced_sexp(text: str, start: int) -> int:
    """Return the index ONE PAST the closing ')' that balances the '(' at *start*.

    Scans *text* forward from *start*.  Raises ValueError when the text is
    exhausted before the expression is closed.

    Args:
        text:  Full schematic text.
        start: Index of the opening '(' whose matching ')' is sought.

    Returns:
        Index immediately after the closing ')'.
    """
    depth = 0
    i = start
    in_string = False
    escape_next = False
    while i < len(text):
        ch = text[i]
        if escape_next:
            # Previous character was a backslash inside a quoted string.
            escape_next = False
        elif in_string:
            if ch == '\\':
                escape_next = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    return i + 1
        i += 1
    raise ValueError(f"Unbalanced S-expression starting at index {start}")


def find_sexp_block(text: str, tag: str) -> tuple[int, int]:
    """Locate the first S-expression block whose opening token matches *tag*.

    Searches for '(' followed immediately (possibly with whitespace) by *tag*,
    then returns (start_index, end_index) of the complete block including
    the opening '('.

    Args:
        text: Schematic text to search.
        tag:  The leading token name to find, e.g. 'symbol "ATA6561"'.

    Returns:
        (start, end) tuple where text[start:end] is the block.

    Raises:
        ValueError: if the tag is not found.
    """
    # Build a pattern that matches '(' then optional whitespace then the tag.
    pattern = r'\(' + re.escape(tag)
    match = re.search(pattern, text)
    if match is None:
        raise ValueError(f"Tag not found: ({tag}")
    start = match.start()
    end = find_balanced_sexp(text, start)
    return start, end


def find_all_sexp_blocks(text: str, tag: str) -> list[tuple[int, int]]:
    """Return a list of (start, end) spans for all S-expression blocks matching *tag*.

    Args:
        text: Schematic text to search.
        tag:  The leading token name to find.

    Returns:
        List of (start, end) tuples; may be empty.
    """
    pattern = r'\(' + re.escape(tag)
    results = []
    for match in re.finditer(pattern, text):
        start = match.start()
        end = find_balanced_sexp(text, start)
        results.append((start, end))
    return results


# ===========================================================================
# Replacement lib_symbol definitions
# ===========================================================================

def lib_sym_isow1044() -> str:
    """Return the KiCad lib_symbol S-expression for ISOW1044BDFMR.

    ISOW1044BDFMR: Isolated CAN-FD transceiver, SOIC-16W.
    Galvanic isolation between CAN controller side (VCC1/GND1) and
    CAN bus side (VCC2/ISOGND).  The isolation boundary is depicted
    as a vertical dashed line at x=0 in the symbol body.

    Pin mapping relative to component centre at (310, 170):
      Left-side (controller) pins at x_offset = -12.70:
        VCC1  pin 6   y_offset = -5.08
        TXD   pin 2   y_offset = -1.27
        STB_N pin 3   y_offset = +1.27
        RXD   pin 4   y_offset = +3.81
        GND1  pin 1   y_offset = +6.35
      Right-side (bus) pins at x_offset = +12.70:
        VCC2   pin 11  y_offset = -5.08
        CANH   pin 15  y_offset = -2.54
        CANL   pin 14  y_offset =  0.00
        ISOGND pin 10  y_offset = +2.54

    Reference: TI ISOW1044BDFMR datasheet, SLLSEO9 (2023).
    """
    return '''\
  (symbol "ISOW1044BDFMR" (in_bom yes) (on_board yes)
    (property "Reference" "U" (at 0 -10.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "ISOW1044BDFMR" (at 0 10.16 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.ti.com/lit/ds/sllseo9/sllseo9.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "ISOW1044BDFMR_0_1"
      (rectangle (start -10.16 -8.89) (end 10.16 8.89)
        (stroke (width 0.254) (type default)) (fill (type background)))
      (polyline (pts (xy 0 -8.89) (xy 0 -3.81))
        (stroke (width 0.127) (type dash)) (fill (type none)))
      (polyline (pts (xy 0 3.81) (xy 0 8.89))
        (stroke (width 0.127) (type dash)) (fill (type none)))
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
      (pin power_in line (at 12.70 -5.08 180) (length 2.54)
        (name "VCC2" (effects (font (size 1.016 1.016))))
        (number "11" (effects (font (size 1.016 1.016)))))
      (pin bidirectional line (at 12.70 -2.54 180) (length 2.54)
        (name "CANH" (effects (font (size 1.016 1.016))))
        (number "15" (effects (font (size 1.016 1.016)))))
      (pin bidirectional line (at 12.70 0.00 180) (length 2.54)
        (name "CANL" (effects (font (size 1.016 1.016))))
        (number "14" (effects (font (size 1.016 1.016)))))
      (pin power_in line (at 12.70 2.54 180) (length 2.54)
        (name "ISOGND" (effects (font (size 1.016 1.016))))
        (number "10" (effects (font (size 1.016 1.016)))))
    )
  )'''


def lib_sym_adm2795() -> str:
    """Return the KiCad lib_symbol S-expression for ADM2795EBRWZ.

    ADM2795EBRWZ: Isolated RS-485 transceiver, SOIC-20W.
    Full galvanic isolation between the logic side (VCC1/GND1) and the
    bus side (VCC2/GND2).  Logic-side RE_N is tied to DE to eliminate
    the need for a separate enable signal, which simplifies routing.

    Pin mapping relative to component centre at (210, 260):
      Left-side (logic) pins at x_offset = -12.70:
        VCC1  y_offset = -5.08
        DI    y_offset = -2.54
        DE    y_offset =  0.00
        RE_N  y_offset = +2.54
        RO    y_offset = +5.08
        GND1  y_offset = +7.62
      Right-side (bus) pins at x_offset = +12.70:
        VCC2  y_offset = -5.08
        A     y_offset = -2.54
        B     y_offset =  0.00
        GND2  y_offset = +2.54

    Reference: Analog Devices ADM2795EBRWZ datasheet, Rev. C (2022).
    """
    return '''\
  (symbol "ADM2795EBRWZ" (in_bom yes) (on_board yes)
    (property "Reference" "U" (at 0 -11.43 0) (effects (font (size 1.27 1.27))))
    (property "Value" "ADM2795EBRWZ" (at 0 11.43 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.analog.com/media/en/technical-documentation/data-sheets/ADM2795E.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "ADM2795EBRWZ_0_1"
      (rectangle (start -10.16 -10.16) (end 10.16 10.16)
        (stroke (width 0.254) (type default)) (fill (type background)))
      (polyline (pts (xy 0 -10.16) (xy 0 -3.81))
        (stroke (width 0.127) (type dash)) (fill (type none)))
      (polyline (pts (xy 0 3.81) (xy 0 10.16))
        (stroke (width 0.127) (type dash)) (fill (type none)))
    )
    (symbol "ADM2795EBRWZ_1_1"
      (pin power_in line (at -12.70 -5.08 0) (length 2.54)
        (name "VCC1" (effects (font (size 1.016 1.016))))
        (number "20" (effects (font (size 1.016 1.016)))))
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
        (number "10" (effects (font (size 1.016 1.016)))))
      (pin power_in line (at 12.70 -5.08 180) (length 2.54)
        (name "VCC2" (effects (font (size 1.016 1.016))))
        (number "11" (effects (font (size 1.016 1.016)))))
      (pin bidirectional line (at 12.70 -2.54 180) (length 2.54)
        (name "A" (effects (font (size 1.016 1.016))))
        (number "16" (effects (font (size 1.016 1.016)))))
      (pin bidirectional line (at 12.70 0.00 180) (length 2.54)
        (name "B" (effects (font (size 1.016 1.016))))
        (number "17" (effects (font (size 1.016 1.016)))))
      (pin power_in line (at 12.70 2.54 180) (length 2.54)
        (name "GND2" (effects (font (size 1.016 1.016))))
        (number "20" (effects (font (size 1.016 1.016)))))
    )
  )'''


def lib_sym_srf2012() -> str:
    """Return the KiCad lib_symbol S-expression for SRF2012-100Y.

    SRF2012-100Y: 100 µH common-mode choke, 2-winding, for CAN and RS-485
    EMI suppression.  Wound as a 4-terminal device; this symbol shows two
    mutually-coupled inductors sharing a common ferrite core.

    Reference: Coilcraft SRF2012-100Y datasheet (2020).
    """
    return '''\
  (symbol "SRF2012-100Y" (in_bom yes) (on_board yes)
    (property "Reference" "CMC" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
    (property "Value" "SRF2012-100Y" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Inductor_SMD:L_Taiyo-Yuden_NR-20xx" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.coilcraft.com/getmedia/3a436de1-46ad-49b9-b3a8-9a3faa3ecf61/srf2012.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "SRF2012-100Y_0_1"
      (rectangle (start -5.08 -3.81) (end 5.08 3.81)
        (stroke (width 0.254) (type default)) (fill (type background)))
      (polyline (pts (xy -1.27 -3.81) (xy -1.27 3.81))
        (stroke (width 0.127) (type dash)) (fill (type none)))
      (polyline (pts (xy 1.27 -3.81) (xy 1.27 3.81))
        (stroke (width 0.127) (type dash)) (fill (type none)))
    )
    (symbol "SRF2012-100Y_1_1"
      (pin passive line (at -7.62 -2.54 0) (length 2.54)
        (name "L1A" (effects (font (size 1.016 1.016))))
        (number "1" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 7.62 -2.54 180) (length 2.54)
        (name "L1B" (effects (font (size 1.016 1.016))))
        (number "2" (effects (font (size 1.016 1.016)))))
      (pin passive line (at -7.62 2.54 0) (length 2.54)
        (name "L2A" (effects (font (size 1.016 1.016))))
        (number "3" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 7.62 2.54 180) (length 2.54)
        (name "L2B" (effects (font (size 1.016 1.016))))
        (number "4" (effects (font (size 1.016 1.016)))))
    )
  )'''


def lib_sym_prtr5v0u2x() -> str:
    """Return the KiCad lib_symbol S-expression for PRTR5V0U2X.

    PRTR5V0U2X: Dual TVS / ESD protection diode in SOT-363, rated 5 V.
    Used to clamp both CAN bus lines (CANH/CANL) and RS-485 lines (A/B)
    against transient overvoltages.  Anode 1 and Anode 2 connect to the
    two bus lines; the common cathode (K) connects to isolated ground.

    Reference: Nexperia PRTR5V0U2X datasheet, Rev. 5 (2021).
    """
    return '''\
  (symbol "PRTR5V0U2X" (in_bom yes) (on_board yes)
    (property "Reference" "D" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
    (property "Value" "PRTR5V0U2X" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_TO_SOT_SMD:SOT-363_SC-70-6" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://assets.nexperia.com/documents/data-sheet/PRTR5V0U2X.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "PRTR5V0U2X_0_1"
      (rectangle (start -5.08 -3.81) (end 5.08 3.81)
        (stroke (width 0.254) (type default)) (fill (type background))))
    (symbol "PRTR5V0U2X_1_1"
      (pin passive line (at -7.62 -2.54 0) (length 2.54)
        (name "A1" (effects (font (size 1.016 1.016))))
        (number "1" (effects (font (size 1.016 1.016)))))
      (pin passive line (at -7.62 2.54 0) (length 2.54)
        (name "A2" (effects (font (size 1.016 1.016))))
        (number "2" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 7.62 0.00 180) (length 2.54)
        (name "K" (effects (font (size 1.016 1.016))))
        (number "3" (effects (font (size 1.016 1.016)))))
    )
  )'''


def lib_sym_smaj33ca() -> str:
    """Return the KiCad lib_symbol S-expression for SMAJ33CA.

    SMAJ33CA: Bidirectional TVS diode, 33 V standoff, SMB package.
    One instance is placed on each MIL-STD-1553 bus line (A and B).
    Each diode clamps the bus wire to chassis ground on overvoltage
    events (e.g., lighting-induced transients).

    Reference: Littelfuse SMAJ33CA datasheet, Rev. 2019.
    """
    return '''\
  (symbol "SMAJ33CA" (in_bom yes) (on_board yes)
    (property "Reference" "D" (at 0 -4.45 0) (effects (font (size 1.27 1.27))))
    (property "Value" "SMAJ33CA" (at 0 4.45 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Diode_SMD:D_SMB" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diode_smaj_datasheet.pdf.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "SMAJ33CA_0_1"
      (rectangle (start -3.81 -2.54) (end 3.81 2.54)
        (stroke (width 0.254) (type default)) (fill (type background))))
    (symbol "SMAJ33CA_1_1"
      (pin passive line (at -6.35 0.00 0) (length 2.54)
        (name "A" (effects (font (size 1.016 1.016))))
        (number "1" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 6.35 0.00 180) (length 2.54)
        (name "K" (effects (font (size 1.016 1.016))))
        (number "2" (effects (font (size 1.016 1.016)))))
    )
  )'''


def lib_sym_ferrite_742792512() -> str:
    """Return the KiCad lib_symbol S-expression for Würth 742792512 ferrite bead.

    742792512: 600 Ω @ 100 MHz, 2 A rated ferrite bead, 0805 package.
    Placed at the +5 V power entry point to suppress conducted emissions
    from the motor drive circuitry before power reaches the logic supply.

    Reference: Würth Elektronik 742792512 datasheet (2021).
    """
    return '''\
  (symbol "742792512" (in_bom yes) (on_board yes)
    (property "Reference" "FB" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
    (property "Value" "742792512" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Inductor_SMD:L_0805_2012Metric" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.we-online.com/catalog/datasheet/742792512.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "742792512_0_1"
      (rectangle (start -3.81 -1.27) (end 3.81 1.27)
        (stroke (width 0.254) (type default)) (fill (type background))))
    (symbol "742792512_1_1"
      (pin passive line (at -6.35 0.00 0) (length 2.54)
        (name "P1" (effects (font (size 1.016 1.016))))
        (number "1" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 6.35 0.00 180) (length 2.54)
        (name "P2" (effects (font (size 1.016 1.016))))
        (number "2" (effects (font (size 1.016 1.016)))))
    )
  )'''


def lib_sym_x2y_cap() -> str:
    """Return the KiCad lib_symbol S-expression for an X2Y capacitor.

    The X2Y topology is a 3-terminal feedthrough capacitor that
    simultaneously decouples two signal/power lines to a common ground.
    Here it is modelled as a 2-terminal passive (bridging) component;
    one terminal connects to the digital ground (GND) and the other to
    the isolated ground (CAN_GND2 or RS485_GND2).  Value is 4.7 nF.

    Reference: X2Y Attenuators LLC, Application Note AN-0003 (2015).
    """
    return '''\
  (symbol "X2Y_CAP_4N7" (in_bom yes) (on_board yes)
    (property "Reference" "C" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
    (property "Value" "4.7nF X2Y" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Capacitor_SMD:C_0402_1005Metric" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.x2y.com/app/uploads/2015/07/AN-0003.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "X2Y_CAP_4N7_0_1"
      (rectangle (start -2.54 -1.27) (end 2.54 1.27)
        (stroke (width 0.254) (type default)) (fill (type background))))
    (symbol "X2Y_CAP_4N7_1_1"
      (pin passive line (at -5.08 0.00 0) (length 2.54)
        (name "G1" (effects (font (size 1.016 1.016))))
        (number "1" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 5.08 0.00 180) (length 2.54)
        (name "G2" (effects (font (size 1.016 1.016))))
        (number "2" (effects (font (size 1.016 1.016)))))
    )
  )'''


# ===========================================================================
# v2 EMI-hardened lib_symbol replacements (Changes I, J)
# ===========================================================================

def lib_sym_mmc5983ma() -> str:
    """Return the KiCad lib_symbol S-expression for the MMC5983MA magnetometer.

    MMC5983MA: MEMSIC 3-axis magnetometer, LGA-16, I²C/SPI, 18-bit, AEC-Q100.
    Replaces the QMC5883L in CAPE-A-2.  The schematic interface is identical:
    SCL, SDA, GND, VDD, DRDY — same 5 pins, same body geometry.

    Pin layout (lib origin 0,0):
      Left side (angle=0, tips at x = −10.16):
        SCL  at lib (−10.16, −2.54)
        SDA  at lib (−10.16,  0.00)
        GND  at lib (−10.16, +2.54)
      Right side (angle=180, tips at x = +10.16):
        VDD  at lib (+10.16, −2.54)
        DRDY at lib (+10.16, +2.54)
    Body rectangle: (−7.62, −3.81) to (+7.62, +3.81).

    Reference: MEMSIC MMC5983MA datasheet (Rev. C, 2022).
    """
    return '''\
  (symbol "MMC5983MA" (in_bom yes) (on_board yes)
    (property "Reference" "U" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
    (property "Value" "MMC5983MA" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Sensor_Magnetic:MMC5983MA" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.memsic.com/Public/Uploads/uploadfile/files/20220119/MMC5983MA-RevC.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "MMC5983MA_0_1"
      (rectangle (start -7.62 -3.81) (end 7.62 3.81)
        (stroke (width 0.254) (type default)) (fill (type background)))
    )
    (symbol "MMC5983MA_1_1"
      (pin input line (at -10.16 -2.54 0) (length 2.54)
        (name "SCL" (effects (font (size 1.016 1.016))))
        (number "1" (effects (font (size 1.016 1.016)))))
      (pin bidirectional line (at -10.16 0.00 0) (length 2.54)
        (name "SDA" (effects (font (size 1.016 1.016))))
        (number "2" (effects (font (size 1.016 1.016)))))
      (pin power_in line (at -10.16 2.54 0) (length 2.54)
        (name "GND" (effects (font (size 1.016 1.016))))
        (number "3" (effects (font (size 1.016 1.016)))))
      (pin power_in line (at 10.16 -2.54 180) (length 2.54)
        (name "VDD" (effects (font (size 1.016 1.016))))
        (number "4" (effects (font (size 1.016 1.016)))))
      (pin output line (at 10.16 2.54 180) (length 2.54)
        (name "DRDY" (effects (font (size 1.016 1.016))))
        (number "5" (effects (font (size 1.016 1.016)))))
    )
  )'''


def lib_sym_ina226() -> str:
    """Return the KiCad lib_symbol S-expression for the INA226AIDGSR.

    INA226AIDGSR: TI bidirectional current/voltage monitor, VSSOP-8, I²C,
    16-bit, 36 V max bus voltage.  Replaces INA219AIDR in CAPE-A-2.

    VSSOP-8 pin assignment (TI SBOS547):
      Pin 1 = IN+, Pin 2 = IN−, Pin 3 = GND, Pin 4 = VS,
      Pin 5 = SDA, Pin 6 = SCL, Pin 7 = A1,  Pin 8 = A0.

    Symbol pin layout (lib origin 0,0, 2.54 mm pitch, ±3.81 mm from centre):
      Left side (angle=0, tips at x = −10.16):
        IN+ (pin 1) at lib (−10.16, −3.81)
        IN− (pin 2) at lib (−10.16, −1.27)
        GND (pin 3) at lib (−10.16, +1.27)
        VS  (pin 4) at lib (−10.16, +3.81)
      Right side (angle=180, tips at x = +10.16):
        SDA (pin 5) at lib (+10.16, −3.81)
        SCL (pin 6) at lib (+10.16, −1.27)
        A1  (pin 7) at lib (+10.16, +1.27)
        A0  (pin 8) at lib (+10.16, +3.81)
    Body rectangle: (−7.62, −5.08) to (+7.62, +5.08).

    Note: The VS supply pin of INA226 corresponds to V+ of INA219; both
    connect to +3V3 in this design.

    Reference: TI INA226 datasheet SBOS547 (Rev. A, 2011).
    """
    return '''\
  (symbol "INA226AIDGSR" (in_bom yes) (on_board yes)
    (property "Reference" "U" (at 0 -7.62 0) (effects (font (size 1.27 1.27))))
    (property "Value" "INA226AIDGSR" (at 0 7.62 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_SO:SSOP-8_4.4x3mm_P0.65mm" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.ti.com/lit/ds/symlink/ina226.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "INA226AIDGSR_0_1"
      (rectangle (start -7.62 -5.08) (end 7.62 5.08)
        (stroke (width 0.254) (type default)) (fill (type background)))
    )
    (symbol "INA226AIDGSR_1_1"
      (pin input line (at -10.16 -3.81 0) (length 2.54)
        (name "IN+" (effects (font (size 1.016 1.016))))
        (number "1" (effects (font (size 1.016 1.016)))))
      (pin input line (at -10.16 -1.27 0) (length 2.54)
        (name "IN-" (effects (font (size 1.016 1.016))))
        (number "2" (effects (font (size 1.016 1.016)))))
      (pin power_in line (at -10.16 1.27 0) (length 2.54)
        (name "GND" (effects (font (size 1.016 1.016))))
        (number "3" (effects (font (size 1.016 1.016)))))
      (pin power_in line (at -10.16 3.81 0) (length 2.54)
        (name "VS" (effects (font (size 1.016 1.016))))
        (number "4" (effects (font (size 1.016 1.016)))))
      (pin bidirectional line (at 10.16 -3.81 180) (length 2.54)
        (name "SDA" (effects (font (size 1.016 1.016))))
        (number "5" (effects (font (size 1.016 1.016)))))
      (pin input line (at 10.16 -1.27 180) (length 2.54)
        (name "SCL" (effects (font (size 1.016 1.016))))
        (number "6" (effects (font (size 1.016 1.016)))))
      (pin input line (at 10.16 1.27 180) (length 2.54)
        (name "A1" (effects (font (size 1.016 1.016))))
        (number "7" (effects (font (size 1.016 1.016)))))
      (pin input line (at 10.16 3.81 180) (length 2.54)
        (name "A0" (effects (font (size 1.016 1.016))))
        (number "8" (effects (font (size 1.016 1.016)))))
    )
  )'''


# ===========================================================================
# v2 component instance generators (Changes I, J, K)
# ===========================================================================

def inst_mag_v2(cx: float, cy: float) -> str:
    """Return the symbol instance block for the MMC5983MA magnetometer (v2).

    The MMC5983MA replaces the QMC5883L at the same schematic position
    (*cx*, *cy*) = (155, 560).  Pin connections and net names are identical
    to the QMC5883L instance since the lib_symbol exposes the same 5 signals.

    Connected nets (same as QMC5883L):
      SCL  → global I2C1_SCL  (angle=180)
      SDA  → global I2C1_SDA  (angle=180)
      GND  → GND power (270°)
      VDD  → +3V3 power (90°)
      DRDY → global GPIO_MAG_DRDY (angle=0)

    Args:
        cx: Component centre X coordinate in mm  (155).
        cy: Component centre Y coordinate in mm  (560).
    """
    left_x = cx - 10.16     # 144.84
    right_x = cx + 10.16    # 165.16
    y_scl = cy - 2.54       # 557.46
    y_sda = cy              # 560.00
    y_gnd = cy + 2.54       # 562.54
    y_vdd = cy - 2.54       # 557.46
    y_drdy = cy + 2.54      # 562.54

    uid_inst = next_uuid()
    uid_p1 = next_uuid()
    uid_p2 = next_uuid()
    uid_p3 = next_uuid()
    uid_p4 = next_uuid()
    uid_p5 = next_uuid()

    return f'''\
  (symbol (lib_id "MMC5983MA") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uid_inst}")
    (property "Reference" "U_MAG" (at {cx:.2f} {cy - 5.08:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "MMC5983MA" (at {cx:.2f} {cy + 5.08:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Sensor_Magnetic:MMC5983MA" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.memsic.com/Public/Uploads/uploadfile/files/20220119/MMC5983MA-RevC.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{uid_p1}"))
    (pin "2" (uuid "{uid_p2}"))
    (pin "3" (uuid "{uid_p3}"))
    (pin "4" (uuid "{uid_p4}"))
    (pin "5" (uuid "{uid_p5}"))
  )
  (global_label "I2C1_SCL" (shape bidirectional) (at {left_x:.2f} {y_scl:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_x:.2f} {y_scl:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (global_label "I2C1_SDA" (shape bidirectional) (at {left_x:.2f} {y_sda:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_x:.2f} {y_sda:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (symbol (lib_id "GND") (at {left_x:.2f} {y_gnd:.2f} 270)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "#PWR0A921" (at {left_x:.2f} {y_gnd:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at {left_x:.2f} {y_gnd + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid()}"))
  )
  (symbol (lib_id "+3V3") (at {right_x:.2f} {y_vdd:.2f} 90)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "#PWR0A922" (at {right_x:.2f} {y_vdd:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "+3V3" (at {right_x:.2f} {y_vdd - 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid()}"))
  )
  (global_label "GPIO_MAG_DRDY" (shape bidirectional) (at {right_x:.2f} {y_drdy:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {right_x:.2f} {y_drdy:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))'''


def inst_batt_mon_v2(cx: float, cy: float) -> str:
    """Return the symbol instance block for the INA226AIDGSR battery monitor (v2).

    The INA226AIDGSR replaces the INA219AIDR at the same position
    (*cx*, *cy*) = (290, 560).  Net connections are identical — the pin
    names differ (VS instead of V+; pin numbers rearranged) but all signals
    connect to the same nets.

    Connected nets (same as INA219AIDR instance):
      IN+  → global VBAT_MON_P (angle=180)
      IN−  → global VBAT_MON_P (angle=180)  [voltage-only mode]
      GND  → GND power (270°)
      VS   → +3V3 power (90°)
      SDA  → global I2C1_SDA (angle=0)
      SCL  → global I2C1_SCL (angle=0)
      A0   → GND power (270°)
      A1   → GND power (270°)

    Args:
        cx: Component centre X coordinate in mm  (290).
        cy: Component centre Y coordinate in mm  (560).
    """
    left_x = cx - 10.16     # 279.84
    right_x = cx + 10.16    # 300.16

    y_in_plus = cy - 3.81   # 556.19
    y_in_minus = cy - 1.27  # 558.73
    y_gnd_pin = cy + 1.27   # 561.27
    y_vs = cy + 3.81        # 563.81

    y_sda = cy - 3.81       # 556.19  (INA226 pin 5 = SDA)
    y_scl = cy - 1.27       # 558.73  (INA226 pin 6 = SCL)
    y_a1 = cy + 1.27        # 561.27  (INA226 pin 7 = A1)
    y_a0 = cy + 3.81        # 563.81  (INA226 pin 8 = A0)

    uid_inst = next_uuid()
    uid_p1 = next_uuid()
    uid_p2 = next_uuid()
    uid_p3 = next_uuid()
    uid_p4 = next_uuid()
    uid_p5 = next_uuid()
    uid_p6 = next_uuid()
    uid_p7 = next_uuid()
    uid_p8 = next_uuid()

    return f'''\
  (symbol (lib_id "INA226AIDGSR") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uid_inst}")
    (property "Reference" "U_BMON" (at {cx:.2f} {cy - 7.62:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "INA226AIDGSR" (at {cx:.2f} {cy + 7.62:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_SO:SSOP-8_4.4x3mm_P0.65mm" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.ti.com/lit/ds/symlink/ina226.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{uid_p1}"))
    (pin "2" (uuid "{uid_p2}"))
    (pin "3" (uuid "{uid_p3}"))
    (pin "4" (uuid "{uid_p4}"))
    (pin "5" (uuid "{uid_p5}"))
    (pin "6" (uuid "{uid_p6}"))
    (pin "7" (uuid "{uid_p7}"))
    (pin "8" (uuid "{uid_p8}"))
  )
  (global_label "VBAT_MON_P" (shape bidirectional) (at {left_x:.2f} {y_in_plus:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_x:.2f} {y_in_plus:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (global_label "VBAT_MON_P" (shape bidirectional) (at {left_x:.2f} {y_in_minus:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_x:.2f} {y_in_minus:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (symbol (lib_id "GND") (at {left_x:.2f} {y_gnd_pin:.2f} 270)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "#PWR0A923" (at {left_x:.2f} {y_gnd_pin:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at {left_x:.2f} {y_gnd_pin + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid()}"))
  )
  (symbol (lib_id "+3V3") (at {left_x:.2f} {y_vs:.2f} 90)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "#PWR0A924" (at {left_x:.2f} {y_vs:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "+3V3" (at {left_x:.2f} {y_vs - 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid()}"))
  )
  (global_label "I2C1_SDA" (shape bidirectional) (at {right_x:.2f} {y_sda:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {right_x:.2f} {y_sda:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (global_label "I2C1_SCL" (shape bidirectional) (at {right_x:.2f} {y_scl:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {right_x:.2f} {y_scl:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (symbol (lib_id "GND") (at {right_x:.2f} {y_a1:.2f} 270)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "#PWR0A925" (at {right_x:.2f} {y_a1:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at {right_x:.2f} {y_a1 + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid()}"))
  )
  (symbol (lib_id "GND") (at {right_x:.2f} {y_a0:.2f} 270)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "#PWR0A926" (at {right_x:.2f} {y_a0:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at {right_x:.2f} {y_a0 + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid()}"))
  )'''


def inst_sbus_tvs(cx: float, cy: float) -> str:
    """Return the PRTR5V0U2X TVS instance on the SBUS_RAW input line.

    D_SBUS_TVS is placed at (*cx*, *cy*) = (125, 627.54) on the SBUS_RAW
    net, clamping transients on the RC receiver signal before it reaches
    R_SBUS and U_SBUS.

    The PRTR5V0U2X lib_symbol is already present in the CAPE-A-2 schematic
    (inserted by the existing gen_cape_a2.py for CAN/RS-485 protection).

    Pin layout from lib_sym_prtr5v0u2x() (body centre at cx,cy):
      A1 tip at (cx − 7.62, cy − 2.54)  →  global SBUS_RAW (angle=180)
      A2 tip at (cx − 7.62, cy + 2.54)  →  no_connect (unused channel)
      K  tip at (cx + 7.62, cy + 0.00)  →  GND power (0°)

    Args:
        cx: Component centre X coordinate in mm  (125).
        cy: Component centre Y coordinate in mm  (627.54).
    """
    left_x = cx - 7.62      # 117.38
    right_x = cx + 7.62     # 132.62
    y_a1 = cy - 2.54        # 625.00
    y_a2 = cy + 2.54        # 630.08
    y_k = cy                # 627.54

    uid_inst = next_uuid()
    uid_p1 = next_uuid()
    uid_p2 = next_uuid()
    uid_p3 = next_uuid()

    return f'''\
  (symbol (lib_id "PRTR5V0U2X") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uid_inst}")
    (property "Reference" "D_SBUS_TVS" (at {cx:.2f} {cy - 5.08:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "PRTR5V0U2X" (at {cx:.2f} {cy + 5.08:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_TO_SOT_SMD:SOT-363_SC-70-6" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://assets.nexperia.com/documents/data-sheet/PRTR5V0U2X.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{uid_p1}"))
    (pin "2" (uuid "{uid_p2}"))
    (pin "3" (uuid "{uid_p3}"))
  )
  (global_label "SBUS_RAW" (shape bidirectional) (at {left_x:.2f} {y_a1:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_x:.2f} {y_a1:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (no_connect (at {left_x:.2f} {y_a2:.2f}) (uuid "{next_uuid()}"))
  (symbol (lib_id "GND") (at {right_x:.2f} {y_k:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "#PWR0A927" (at {right_x:.2f} {y_k:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at {right_x + 2.54:.2f} {y_k:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid()}"))
  )'''


# ===========================================================================
# New component instance generators
# ===========================================================================
# Each function returns a multi-line string ready to be inserted verbatim
# into the schematic body (outside lib_symbols, before the closing ')').

def inst_isow1044(cx: float, cy: float) -> str:
    """Return the symbol instance block for the ISOW1044BDFMR.

    The component is centred at (*cx*, *cy*) = (310, 170), matching the
    ATA6561 it replaces.  Global labels are placed at pin endpoints.

    VCC1 and GND1 are connected directly to power symbols.
    VCC2 is connected to a 100 nF bypass cap (placed separately) on CAN_GND2.
    ISOGND connects to CAN_GND2 net label.
    CANH/CANL feed into the SRF2012 common-mode choke (CMC_CAN).
    TXD/STB_N/RXD connect to existing MCAN0_TX/CAN_STB/MCAN0_RX global labels.

    Args:
        cx: Component centre X coordinate (mm).
        cy: Component centre Y coordinate (mm).
    """
    # Pin endpoint X coordinates (component x ± pin_length = ±12.70 ± 2.54)
    left_x = cx - 12.70  # = 297.30 for cx=310
    right_x = cx + 12.70  # = 322.70 for cx=310

    # Left-side pin Y absolute coordinates
    y_vcc1 = cy - 5.08    # 164.92
    y_txd = cy - 1.27     # 168.73
    y_stb_n = cy + 1.27   # 171.27
    y_rxd = cy + 3.81     # 173.81
    y_gnd1 = cy + 6.35    # 176.35

    # Right-side pin Y absolute coordinates
    y_vcc2 = cy - 5.08    # 164.92
    y_canh = cy - 2.54    # 167.46
    y_canl = cy           # 170.00
    y_isognd = cy + 2.54  # 172.54

    uid_inst = next_uuid()
    uid_p1 = next_uuid()
    uid_p2 = next_uuid()
    uid_p3 = next_uuid()
    uid_p4 = next_uuid()
    uid_p6 = next_uuid()
    uid_p10 = next_uuid()
    uid_p11 = next_uuid()
    uid_p14 = next_uuid()
    uid_p15 = next_uuid()

    return f'''\
  (symbol (lib_id "ISOW1044BDFMR") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uid_inst}")
    (property "Reference" "CAN-TR" (at {cx:.2f} {cy - 11.43:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "ISOW1044BDFMR" (at {cx:.2f} {cy + 11.43:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.ti.com/lit/ds/sllseo9/sllseo9.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{uid_p1}"))
    (pin "2" (uuid "{uid_p2}"))
    (pin "3" (uuid "{uid_p3}"))
    (pin "4" (uuid "{uid_p4}"))
    (pin "6" (uuid "{uid_p6}"))
    (pin "10" (uuid "{uid_p10}"))
    (pin "11" (uuid "{uid_p11}"))
    (pin "14" (uuid "{uid_p14}"))
    (pin "15" (uuid "{uid_p15}"))
  )
  (global_label "MCAN0_TX" (shape bidirectional) (at {left_x:.2f} {y_txd:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_x:.2f} {y_txd:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (global_label "CAN_STB" (shape bidirectional) (at {left_x:.2f} {y_stb_n:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_x:.2f} {y_stb_n:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (global_label "MCAN0_RX" (shape bidirectional) (at {left_x:.2f} {y_rxd:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_x:.2f} {y_rxd:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (symbol (lib_id "+3V3") (at {left_x:.2f} {y_vcc1:.2f} 90)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "#PWR0A201" (at {left_x:.2f} {y_vcc1:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "+3V3" (at {left_x:.2f} {y_vcc1 - 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid()}"))
  )
  (symbol (lib_id "GND") (at {left_x:.2f} {y_gnd1:.2f} 270)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "#PWR0A202" (at {left_x:.2f} {y_gnd1:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at {left_x:.2f} {y_gnd1 + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid()}"))
  )
  (global_label "CAN_GND2" (shape bidirectional) (at {right_x:.2f} {y_isognd:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {right_x:.2f} {y_isognd:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (symbol (lib_id "+3V3") (at {right_x:.2f} {y_vcc2:.2f} 90)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "#PWR0A203" (at {right_x:.2f} {y_vcc2:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "+3V3" (at {right_x:.2f} {y_vcc2 - 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid()}"))
  )'''


def inst_adm2795(cx: float, cy: float) -> str:
    """Return the symbol instance block for the ADM2795EBRWZ.

    The component is centred at (*cx*, *cy*) = (210, 260), matching the
    MAX3485E it replaces.  RE_N is tied to DE by a short wire segment so
    the transceiver operates half-duplex with automatic direction control.

    VCC1 → +3V3 power symbol.
    GND1 → GND power symbol.
    VCC2 → +3V3 power symbol (bus side, locally bypassed externally).
    GND2 → RS485_GND2 global label.
    DI / DE / RE_N / RO → RS485_TX / RS485_DE / (tie to DE) / RS485_RX.
    A / B → feed into CMC_RS485 (placed separately).

    Args:
        cx: Component centre X coordinate (mm).
        cy: Component centre Y coordinate (mm).
    """
    left_x = cx - 12.70   # 197.30
    right_x = cx + 12.70  # 222.70

    # Left-side pin Y values
    y_vcc1 = cy - 5.08   # 254.92
    y_di = cy - 2.54     # 257.46
    y_de = cy            # 260.00
    y_ren = cy + 2.54    # 262.54
    y_ro = cy + 5.08     # 265.08
    y_gnd1 = cy + 7.62   # 267.62

    # Right-side pin Y values
    y_vcc2 = cy - 5.08   # 254.92
    y_a = cy - 2.54      # 257.46
    y_b = cy             # 260.00
    y_gnd2 = cy + 2.54   # 262.54

    uid_inst = next_uuid()
    uid_p1 = next_uuid()
    uid_p2 = next_uuid()
    uid_p3 = next_uuid()
    uid_p4 = next_uuid()
    uid_p10 = next_uuid()
    uid_p11 = next_uuid()
    uid_p16 = next_uuid()
    uid_p17 = next_uuid()
    uid_p20 = next_uuid()

    return f'''\
  (symbol (lib_id "ADM2795EBRWZ") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uid_inst}")
    (property "Reference" "RS485" (at {cx:.2f} {cy - 12.70:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "ADM2795EBRWZ" (at {cx:.2f} {cy + 12.70:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.analog.com/media/en/technical-documentation/data-sheets/ADM2795E.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{uid_p1}"))
    (pin "2" (uuid "{uid_p2}"))
    (pin "3" (uuid "{uid_p3}"))
    (pin "4" (uuid "{uid_p4}"))
    (pin "10" (uuid "{uid_p10}"))
    (pin "11" (uuid "{uid_p11}"))
    (pin "16" (uuid "{uid_p16}"))
    (pin "17" (uuid "{uid_p17}"))
    (pin "20" (uuid "{uid_p20}"))
  )
  (global_label "RS485_TX" (shape bidirectional) (at {left_x:.2f} {y_di:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_x:.2f} {y_di:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (global_label "RS485_DE" (shape bidirectional) (at {left_x:.2f} {y_de:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_x:.2f} {y_de:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (wire (pts (xy {left_x:.2f} {y_ren:.2f}) (xy {left_x:.2f} {y_de:.2f}))
    (uuid "{next_uuid()}"))
  (global_label "RS485_RX" (shape bidirectional) (at {left_x:.2f} {y_ro:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_x:.2f} {y_ro:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (symbol (lib_id "+3V3") (at {left_x:.2f} {y_vcc1:.2f} 90)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "#PWR0A204" (at {left_x:.2f} {y_vcc1:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "+3V3" (at {left_x:.2f} {y_vcc1 - 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid()}"))
  )
  (symbol (lib_id "GND") (at {left_x:.2f} {y_gnd1:.2f} 270)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "#PWR0A205" (at {left_x:.2f} {y_gnd1:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at {left_x:.2f} {y_gnd1 + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid()}"))
  )
  (symbol (lib_id "+3V3") (at {right_x:.2f} {y_vcc2:.2f} 90)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "#PWR0A206" (at {right_x:.2f} {y_vcc2:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "+3V3" (at {right_x:.2f} {y_vcc2 - 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid()}"))
  )
  (global_label "RS485_GND2" (shape bidirectional) (at {right_x:.2f} {y_gnd2:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {right_x:.2f} {y_gnd2:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (global_label "RS485_A" (shape bidirectional) (at {right_x:.2f} {y_a:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {right_x:.2f} {y_a:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (global_label "RS485_B" (shape bidirectional) (at {right_x:.2f} {y_b:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {right_x:.2f} {y_b:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))'''


def inst_cmc_can(cx: float, cy: float) -> str:
    """Return the SRF2012-100Y CMC instance block for the CAN bus.

    CMC_CAN is placed at (335, 170) between the ISOW1044BDFMR CANH/CANL
    outputs and the external field connector net labels CAN_H_CMC / CAN_L_CMC.
    Pin L1A receives CAN_H from the transceiver; L1B drives CAN_H_CMC.
    Pin L2A receives CAN_L; L2B drives CAN_L_CMC.

    Args:
        cx: Component centre X (335).
        cy: Component centre Y (170).
    """
    # Absolute pin tip positions for this component orientation.
    # Pin length in lib_sym is 2.54; component half-width from centre to pin = 7.62.
    left_x = cx - 7.62   # 327.38 — L1A and L2A tips
    right_x = cx + 7.62  # 342.62 — L1B and L2B tips
    y_l1 = cy - 2.54     # 167.46 — upper winding (CAN_H line)
    y_l2 = cy            # 170.00 — lower winding (CAN_L line)

    return f'''\
  (symbol (lib_id "SRF2012-100Y") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "CMC_CAN" (at {cx:.2f} {cy - 5.08:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "SRF2012-100Y" (at {cx:.2f} {cy + 5.08:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Inductor_SMD:L_Taiyo-Yuden_NR-20xx" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{next_uuid()}"))
    (pin "2" (uuid "{next_uuid()}"))
    (pin "3" (uuid "{next_uuid()}"))
    (pin "4" (uuid "{next_uuid()}"))
  )
  (wire (pts (xy 322.70 167.46) (xy {left_x:.2f} {y_l1:.2f}))
    (uuid "{next_uuid()}"))
  (wire (pts (xy 322.70 170.00) (xy {left_x:.2f} {y_l2:.2f}))
    (uuid "{next_uuid()}"))
  (global_label "CAN_H_CMC" (shape bidirectional) (at {right_x:.2f} {y_l1:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {right_x:.2f} {y_l1:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (global_label "CAN_L_CMC" (shape bidirectional) (at {right_x:.2f} {y_l2:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {right_x:.2f} {y_l2:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))'''


def inst_tvs_can(cx: float, cy: float) -> str:
    """Return the PRTR5V0U2X TVS instance block for the CAN bus.

    D_CAN is placed at (355, 175) on the CAN_H_CMC and CAN_L_CMC nets,
    clamping differential transients after the CMC filter.
    Cathode K connects to CAN_GND2 (isolated ground).

    Args:
        cx: Component centre X (355).
        cy: Component centre Y (175).
    """
    left_x = cx - 7.62   # 347.38
    right_x = cx + 7.62  # 362.62
    y_a1 = cy - 2.54     # 172.46
    y_a2 = cy + 2.54     # 177.54

    return f'''\
  (symbol (lib_id "PRTR5V0U2X") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "D_CAN" (at {cx:.2f} {cy - 5.08:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "PRTR5V0U2X" (at {cx:.2f} {cy + 5.08:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_TO_SOT_SMD:SOT-363_SC-70-6" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{next_uuid()}"))
    (pin "2" (uuid "{next_uuid()}"))
    (pin "3" (uuid "{next_uuid()}"))
  )
  (global_label "CAN_H_CMC" (shape bidirectional) (at {left_x:.2f} {y_a1:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_x:.2f} {y_a1:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (global_label "CAN_L_CMC" (shape bidirectional) (at {left_x:.2f} {y_a2:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_x:.2f} {y_a2:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (global_label "CAN_GND2" (shape bidirectional) (at {right_x:.2f} {cy:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {right_x:.2f} {cy:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))'''


def inst_cmc_rs485(cx: float, cy: float) -> str:
    """Return the SRF2012-100Y CMC instance block for the RS-485 bus.

    CMC_RS485 is placed at (235, 260), identical topology to CMC_CAN
    but on the RS-485 A/B lines.

    Args:
        cx: Component centre X (235).
        cy: Component centre Y (260).
    """
    left_x = cx - 7.62
    right_x = cx + 7.62
    y_l1 = cy - 2.54
    y_l2 = cy

    return f'''\
  (symbol (lib_id "SRF2012-100Y") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "CMC_RS485" (at {cx:.2f} {cy - 5.08:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "SRF2012-100Y" (at {cx:.2f} {cy + 5.08:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Inductor_SMD:L_Taiyo-Yuden_NR-20xx" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{next_uuid()}"))
    (pin "2" (uuid "{next_uuid()}"))
    (pin "3" (uuid "{next_uuid()}"))
    (pin "4" (uuid "{next_uuid()}"))
  )
  (wire (pts (xy 222.70 257.46) (xy {left_x:.2f} {y_l1:.2f}))
    (uuid "{next_uuid()}"))
  (wire (pts (xy 222.70 260.00) (xy {left_x:.2f} {y_l2:.2f}))
    (uuid "{next_uuid()}"))
  (global_label "RS485_A_CMC" (shape bidirectional) (at {right_x:.2f} {y_l1:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {right_x:.2f} {y_l1:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (global_label "RS485_B_CMC" (shape bidirectional) (at {right_x:.2f} {y_l2:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {right_x:.2f} {y_l2:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))'''


def inst_tvs_rs485(cx: float, cy: float) -> str:
    """Return the PRTR5V0U2X TVS instance block for the RS-485 bus.

    D_RS485 is placed at (255, 265), mirroring D_CAN in topology.

    Args:
        cx: Component centre X (255).
        cy: Component centre Y (265).
    """
    left_x = cx - 7.62
    right_x = cx + 7.62
    y_a1 = cy - 2.54
    y_a2 = cy + 2.54

    return f'''\
  (symbol (lib_id "PRTR5V0U2X") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "D_RS485" (at {cx:.2f} {cy - 5.08:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "PRTR5V0U2X" (at {cx:.2f} {cy + 5.08:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_TO_SOT_SMD:SOT-363_SC-70-6" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{next_uuid()}"))
    (pin "2" (uuid "{next_uuid()}"))
    (pin "3" (uuid "{next_uuid()}"))
  )
  (global_label "RS485_A_CMC" (shape bidirectional) (at {left_x:.2f} {y_a1:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_x:.2f} {y_a1:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (global_label "RS485_B_CMC" (shape bidirectional) (at {left_x:.2f} {y_a2:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_x:.2f} {y_a2:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (global_label "RS485_GND2" (shape bidirectional) (at {right_x:.2f} {cy:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {right_x:.2f} {cy:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))'''


def inst_tvs_1553(cx: float, cy: float) -> str:
    """Return two SMAJ33CA TVS diode instances for MIL-STD-1553 bus protection.

    D_1553A protects the 1553_A (BUS_1553_A_P) bus line.
    D_1553B protects the 1553_B (BUS_1553_A_N) bus line.
    Both diode cathodes (K) go to chassis GND.

    Placed at (330, 365) — immediately beside the SM-1553-11 transformer
    secondary lines — so trace lengths to the bus are minimised.

    Args:
        cx: Nominal centre X (330).
        cy: Nominal centre Y (365).
    """
    # Place two TVS diodes side by side vertically, 5.08 mm apart.
    cx_a = cx
    cy_a = cy - 2.54
    cx_b = cx
    cy_b = cy + 2.54

    left_a = cx_a - 6.35
    right_a = cx_a + 6.35
    left_b = cx_b - 6.35
    right_b = cx_b + 6.35

    return f'''\
  (symbol (lib_id "SMAJ33CA") (at {cx_a:.2f} {cy_a:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "D_1553A" (at {cx_a:.2f} {cy_a - 3.81:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "SMAJ33CA" (at {cx_a:.2f} {cy_a + 3.81:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Diode_SMD:D_SMB" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{next_uuid()}"))
    (pin "2" (uuid "{next_uuid()}"))
  )
  (global_label "BUS_1553_A_P" (shape bidirectional) (at {left_a:.2f} {cy_a:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_a:.2f} {cy_a:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (symbol (lib_id "GND") (at {right_a:.2f} {cy_a:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "#PWR0A207" (at {right_a:.2f} {cy_a:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at {right_a + 2.54:.2f} {cy_a:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid()}"))
  )
  (symbol (lib_id "SMAJ33CA") (at {cx_b:.2f} {cy_b:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "D_1553B" (at {cx_b:.2f} {cy_b - 3.81:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "SMAJ33CA" (at {cx_b:.2f} {cy_b + 3.81:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Diode_SMD:D_SMB" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{next_uuid()}"))
    (pin "2" (uuid "{next_uuid()}"))
  )
  (global_label "BUS_1553_A_N" (shape bidirectional) (at {left_b:.2f} {cy_b:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_b:.2f} {cy_b:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (symbol (lib_id "GND") (at {right_b:.2f} {cy_b:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "#PWR0A208" (at {right_b:.2f} {cy_b:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at {right_b + 2.54:.2f} {cy_b:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid()}"))
  )'''


def inst_fb_pwr(cx: float, cy: float) -> str:
    """Return the Würth 742792512 ferrite bead instance at the +5V power entry.

    FB_PWR is placed near the PB2-P1 connector +5V pin (nominally at
    x=72.62, y=123.09 in the original schematic).  It is inserted in series
    with the +5V rail between the connector and the local +5V distribution
    net to suppress conducted EMI from the motor drive harness.

    The bead input (P1) connects to the +5V global power symbol coming
    from the connector; the output (P2) connects to the local +5V net
    (same net name, further into the board).

    Args:
        cx: Centre X — placed at (85, 123).
        cy: Centre Y.
    """
    left_x = cx - 6.35
    right_x = cx + 6.35

    return f'''\
  (symbol (lib_id "742792512") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "FB_PWR" (at {cx:.2f} {cy - 3.81:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "742792512" (at {cx:.2f} {cy + 3.81:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Inductor_SMD:L_0805_2012Metric" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{next_uuid()}"))
    (pin "2" (uuid "{next_uuid()}"))
  )
  (symbol (lib_id "+5V") (at {left_x:.2f} {cy:.2f} 270)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "#PWR0A209" (at {left_x:.2f} {cy:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "+5V" (at {left_x - 2.54:.2f} {cy:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid()}"))
  )
  (symbol (lib_id "+5V") (at {right_x:.2f} {cy:.2f} 90)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "#PWR0A210" (at {right_x:.2f} {cy:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "+5V" (at {right_x + 2.54:.2f} {cy:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid()}"))
  )'''


def inst_x2y_can(cx: float, cy: float) -> str:
    """Return the X2Y capacitor instance bridging GND and CAN_GND2.

    X2Y_CAN is placed at (320, 180), directly below the ISOW1044BDFMR.
    Terminal G1 connects to GND; G2 connects to CAN_GND2.

    Args:
        cx: Centre X (320).
        cy: Centre Y (180).
    """
    left_x = cx - 5.08
    right_x = cx + 5.08

    return f'''\
  (symbol (lib_id "X2Y_CAP_4N7") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "X2Y_CAN" (at {cx:.2f} {cy - 3.81:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "4.7nF X2Y" (at {cx:.2f} {cy + 3.81:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Capacitor_SMD:C_0402_1005Metric" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{next_uuid()}"))
    (pin "2" (uuid "{next_uuid()}"))
  )
  (symbol (lib_id "GND") (at {left_x:.2f} {cy:.2f} 270)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "#PWR0A211" (at {left_x:.2f} {cy:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at {left_x:.2f} {cy + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid()}"))
  )
  (global_label "CAN_GND2" (shape bidirectional) (at {right_x:.2f} {cy:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {right_x:.2f} {cy:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))'''


def inst_x2y_rs485(cx: float, cy: float) -> str:
    """Return the X2Y capacitor instance bridging GND and RS485_GND2.

    X2Y_RS485 is placed at (220, 270), directly below the ADM2795EBRWZ.
    Terminal G1 connects to GND; G2 connects to RS485_GND2.

    Args:
        cx: Centre X (220).
        cy: Centre Y (270).
    """
    left_x = cx - 5.08
    right_x = cx + 5.08

    return f'''\
  (symbol (lib_id "X2Y_CAP_4N7") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "X2Y_RS485" (at {cx:.2f} {cy - 3.81:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "4.7nF X2Y" (at {cx:.2f} {cy + 3.81:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Capacitor_SMD:C_0402_1005Metric" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{next_uuid()}"))
    (pin "2" (uuid "{next_uuid()}"))
  )
  (symbol (lib_id "GND") (at {left_x:.2f} {cy:.2f} 270)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid()}")
    (property "Reference" "#PWR0A212" (at {left_x:.2f} {cy:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at {left_x:.2f} {cy + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid()}"))
  )
  (global_label "RS485_GND2" (shape bidirectional) (at {right_x:.2f} {cy:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {right_x:.2f} {cy:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))'''


# ===========================================================================
# No-connect markers for former PHY connector pins
# ===========================================================================

def phy_no_connects() -> str:
    """Return no_connect markers for the PB2-P2 connector pins that formerly
    drove the two DP83825I Ethernet PHYs (RMII0/RMII1, MDC, MDIO, PHY*).

    The PB2-P2 connector pin endpoints as extracted from the source file.
    Pin tips are at x=67.54 for the global_labels on PB2-P2.
    In the original schematic, global_labels on the left side of PB2-P2
    connect at x=67.54.  The connector body is at x=65.00, pin length 2.54,
    so the pin tip is at 65.00 + 2.54 = 67.54.

    We place no_connect markers at the same (x, y) coordinates where the
    removed global_labels began.
    """
    # Y positions of all removed PB2-P2 labels (from source lines 839–947).
    phy_ys = [
        390.63,  # RMII0_TXD0
        393.17,  # RMII0_TXD1
        395.71,  # RMII0_TX_EN
        398.25,  # RMII0_RXD0
        400.79,  # RMII0_RXD1
        403.33,  # RMII0_CRS_DV
        405.87,  # RMII0_RX_ER
        408.41,  # RMII0_REF_CLK
        410.95,  # RMII1_TXD0
        413.49,  # RMII1_TXD1
        416.03,  # RMII1_TX_EN
        418.57,  # RMII1_RXD0
        421.11,  # RMII1_RXD1
        423.65,  # RMII1_CRS_DV
        426.19,  # RMII1_RX_ER
        428.73,  # RMII1_REF_CLK
        431.27,  # MDC
        433.81,  # MDIO
        436.35,  # PHY1_INTRN
        438.89,  # PHY1_RSTN
        441.43,  # PHY2_INTRN
        443.97,  # PHY2_RSTN
    ]
    blocks = []
    for y in phy_ys:
        uid = next_uuid()
        blocks.append(
            f'  (no_connect (at 67.54 {y:.2f}) (uuid "{uid}"))'
        )
    return "\n".join(blocks)


# ===========================================================================
# Main transformation function
# ===========================================================================

def transform(src: str) -> str:
    """Apply all EMI-hardening transformations to the CAPE-A-1 schematic text.

    The transformation is performed as a sequence of string-level operations
    on the full schematic text.  Each step is clearly labelled; they are
    applied in dependency order so that later steps do not accidentally
    re-match regions already replaced.

    Args:
        src: Full text of CAPE-A-1.kicad_sch.

    Returns:
        Transformed text for CAPE-A-2.kicad_sch.
    """
    text = src

    # ------------------------------------------------------------------
    # A. Title block — update title, rev, date
    # ------------------------------------------------------------------
    # The original title_block is a single-line compound expression.
    # We replace only the three fields that change; all others are kept.
    text = text.replace(
        '(title "CAPE-A-1")',
        '(title "CAPE-A-2 EMI-Hardened Flight Control & Sensor Cape")'
    )
    text = text.replace('(rev "M")', '(rev "2")')
    text = text.replace('(date "2026-05-21")', '(date "2026-06-03")')

    # ------------------------------------------------------------------
    # B. Replace ATA6561 lib_symbol with ISOW1044BDFMR lib_symbol.
    #    The lib_symbols section is inside the outer (lib_symbols ...) block.
    # ------------------------------------------------------------------
    try:
        s, e = find_sexp_block(text, 'symbol "ATA6561"')
        text = text[:s] + lib_sym_isow1044() + "\n" + text[e:]
    except ValueError as exc:
        print(f"WARNING: ATA6561 lib_symbol not found: {exc}", file=sys.stderr)

    # ------------------------------------------------------------------
    # C. Replace MAX3485E lib_symbol with ADM2795EBRWZ lib_symbol.
    # ------------------------------------------------------------------
    try:
        s, e = find_sexp_block(text, 'symbol "MAX3485E"')
        text = text[:s] + lib_sym_adm2795() + "\n" + text[e:]
    except ValueError as exc:
        print(f"WARNING: MAX3485E lib_symbol not found: {exc}", file=sys.stderr)

    # ------------------------------------------------------------------
    # D1. Remove the DP83825I lib_symbol definition entirely.
    # ------------------------------------------------------------------
    try:
        s, e = find_sexp_block(text, 'symbol "DP83825I"')
        text = text[:s] + text[e:]
    except ValueError as exc:
        print(f"WARNING: DP83825I lib_symbol not found: {exc}", file=sys.stderr)

    # ------------------------------------------------------------------
    # D2. Insert new EMI lib_symbol definitions into lib_symbols block.
    #     We locate the closing ')' of the lib_symbols block and insert
    #     before it.  The lib_symbols block ends with the pattern
    #     '  )\n  (' or '  )\n)' (after the last symbol definition).
    #     More robustly: find the exact closing of the lib_symbols sexp.
    # ------------------------------------------------------------------
    # Find '(lib_symbols' and then its closing ')'.
    try:
        ls_start, ls_end = find_sexp_block(text, 'lib_symbols')
        # Insert new lib_symbol definitions just before the closing ')'.
        new_syms = (
            "\n" +
            lib_sym_srf2012() + "\n" +
            lib_sym_prtr5v0u2x() + "\n" +
            lib_sym_smaj33ca() + "\n" +
            lib_sym_ferrite_742792512() + "\n" +
            lib_sym_x2y_cap() + "\n"
        )
        # ls_end points one past the closing ')' of lib_symbols block.
        # The closing ')' itself is at ls_end - 1.
        insert_pos = ls_end - 1  # position of the closing ')' character
        text = text[:insert_pos] + new_syms + "  " + text[insert_pos:]
    except ValueError as exc:
        print(f"WARNING: lib_symbols block not found: {exc}", file=sys.stderr)

    # ------------------------------------------------------------------
    # B2. Replace ATA6561 symbol instance with ISOW1044BDFMR instance.
    #     The instance begins with '(symbol (lib_id "ATA6561")'.
    # ------------------------------------------------------------------
    try:
        s, e = find_sexp_block(text, 'symbol (lib_id "ATA6561")')
        text = text[:s] + inst_isow1044(310.0, 170.0) + "\n" + text[e:]
    except ValueError as exc:
        print(f"WARNING: ATA6561 instance not found: {exc}", file=sys.stderr)

    # Remove the old ATA6561 global_labels (MCAN0_TX / CAN_STB / MCAN0_RX
    # / CAN_H / CAN_L that were directly connected to ATA6561).
    # These are replaced by the labels inside inst_isow1044().
    # We identify them by their (at 297.30 ... 180) and (at 322.70 ... 0)
    # positions within the CAN transceiver area (y = 165–175).
    def remove_global_labels_by_pattern(txt: str, pattern: str) -> str:
        """Remove all global_label blocks whose text matches *pattern*."""
        regex = re.compile(r'  \(global_label[^\n]*' + re.escape(pattern))
        for match in regex.finditer(txt):
            start = match.start()
            try:
                end = find_balanced_sexp(txt, start)
                # Remove leading newline if present.
                if start > 0 and txt[start - 1] == '\n':
                    start -= 1
                return txt[:start] + txt[end:]
            except ValueError:
                pass
        return txt

    # Remove the original ATA6561-connected CAN global_labels (precise
    # Y-range 165–175 to avoid clipping unrelated labels with same names).
    def remove_can_ata6561_labels(txt: str) -> str:
        """Remove CAN labels at the ATA6561 instance position range."""
        # Pattern: global_label at y in [164, 175] connected to old chip.
        # We match on position strings (297.30 or 322.70) within y 164–176.
        for label_name in ("MCAN0_TX", "CAN_STB", "MCAN0_RX", "CAN_H", "CAN_L"):
            # Find all occurrences; remove those that sit in the ATA6561 area.
            pattern = re.compile(
                r'\n  \(global_label "' + re.escape(label_name) +
                r'" \(shape bidirectional\) \(at (?:297\.30|322\.70) 1[67]\d\.\d+ '
                r'(?:180|0)\)'
            )
            for m in list(pattern.finditer(txt)):
                blk_start = m.start() + 1  # skip leading \n
                try:
                    blk_end = find_balanced_sexp(txt, blk_start)
                    txt = txt[:m.start()] + txt[blk_end:]
                    break  # re-search from top after mutation
                except ValueError:
                    pass
        return txt

    text = remove_can_ata6561_labels(text)

    # ------------------------------------------------------------------
    # C2. Replace MAX3485E symbol instance with ADM2795EBRWZ instance.
    # ------------------------------------------------------------------
    try:
        s, e = find_sexp_block(text, 'symbol (lib_id "MAX3485E")')
        text = text[:s] + inst_adm2795(210.0, 260.0) + "\n" + text[e:]
    except ValueError as exc:
        print(f"WARNING: MAX3485E instance not found: {exc}", file=sys.stderr)

    # Remove the old MAX3485E global_labels connected at (197.30, *) or
    # (222.70, *) in the y=250–270 band (RS-485 area).
    def remove_rs485_max3485_labels(txt: str) -> str:
        """Remove RS-485 labels at the MAX3485E instance position range."""
        for label_name in ("RS485_TX", "RS485_DE", "RS485_RX", "RS485_A", "RS485_B"):
            pattern = re.compile(
                r'\n  \(global_label "' + re.escape(label_name) +
                r'" \(shape bidirectional\) \(at (?:197\.30|222\.70) 2[5-7]\d\.\d+ '
                r'(?:180|0)\)'
            )
            for m in list(pattern.finditer(txt)):
                blk_start = m.start() + 1
                try:
                    blk_end = find_balanced_sexp(txt, blk_start)
                    txt = txt[:m.start()] + txt[blk_end:]
                    break
                except ValueError:
                    pass
        return txt

    text = remove_rs485_max3485_labels(text)

    # Also remove the second RS485_DE label at (197.30, 262.54) that
    # was tied to RE_N on MAX3485E (now handled by the wire in inst_adm2795).
    # The above loop handles both occurrences via repeated passes; do one
    # final targeted pass for the RE_N-tied one.
    text = re.sub(
        r'\n  \(global_label "RS485_DE" \(shape bidirectional\)'
        r' \(at 197\.30 262\.54 180\)[^\)]*\)[^\)]*\)',
        '',
        text,
        flags=re.DOTALL
    )

    # ------------------------------------------------------------------
    # D3. Remove both DP83825I symbol instances and all connected labels.
    # ------------------------------------------------------------------
    for _ in range(2):
        try:
            s, e = find_sexp_block(text, 'symbol (lib_id "DP83825I")')
            text = text[:s] + text[e:]
        except ValueError:
            break  # no more instances

    # Remove all global_labels whose names are PHY-specific (RMII*, MDC,
    # MDIO, PHY*_INTRN, PHY*_RSTN, ETH*_TX_*, ETH*_RX_*).
    # These labels appear both on PB2-P2 (left side) and near the PHY ICs.
    phy_label_pattern = re.compile(
        r'\n  \(global_label "('
        r'RMII[01]_TXD[01]|RMII[01]_TX_EN|RMII[01]_RXD[01]|'
        r'RMII[01]_CRS_DV|RMII[01]_RX_ER|RMII[01]_REF_CLK|'
        r'MDC|MDIO|'
        r'PHY[12]_INTRN|PHY[12]_RSTN|'
        r'ETH[12]_TX_[PN]|ETH[12]_RX_[PN]'
        r')" \(shape'
    )

    def remove_all_matching_labels(txt: str, pat: re.Pattern) -> str:
        """Iteratively remove all global_label blocks matched by *pat*."""
        found = True
        while found:
            found = False
            m = pat.search(txt)
            if m:
                blk_start = m.start() + 1  # skip leading \n
                try:
                    blk_end = find_balanced_sexp(txt, blk_start)
                    txt = txt[:m.start()] + txt[blk_end:]
                    found = True
                except ValueError:
                    pass
        return txt

    text = remove_all_matching_labels(text, phy_label_pattern)

    # Remove the two wires that led from PB2-P2 to GND/+5V in the PHY area
    # (the two (wire ...) blocks at y=385.55 and y=388.09) and their
    # associated power symbols at (72.62, 385.55) and (72.62, 388.09).
    # These are at the top of the PB2-P2 section; we detect them by the
    # exact coordinate strings present in the source.
    # The power symbols (GND @ 385.55, +5V @ 388.09) in the PHY supply area.
    phy_power_patterns = [
        r'\n  \(wire \(pts \(xy 67\.54 385\.55\) \(xy 72\.62 385\.55\)\)[^\)]*\)',
        r'\n  \(wire \(pts \(xy 67\.54 388\.09\) \(xy 72\.62 388\.09\)\)[^\)]*\)',
    ]
    for pat in phy_power_patterns:
        text = re.sub(pat, '', text, flags=re.DOTALL)

    # Remove power symbol blocks at PHY supply positions:
    # (symbol (lib_id "GND") (at 72.62 385.55 ...) and
    # (symbol (lib_id "+5V") (at 72.62 388.09 ...)
    phy_pwr_sym_pattern = re.compile(
        r'\n  \(symbol \(lib_id "[^"]+"\) \(at 72\.62 (?:385\.55|388\.09) 0\)'
    )

    def remove_all_matching_syms(txt: str, pat: re.Pattern) -> str:
        """Iteratively remove symbol blocks whose opening matches *pat*."""
        found = True
        while found:
            found = False
            m = pat.search(txt)
            if m:
                blk_start = m.start() + 1
                try:
                    blk_end = find_balanced_sexp(txt, blk_start)
                    txt = txt[:m.start()] + txt[blk_end:]
                    found = True
                except ValueError:
                    pass
        return txt

    text = remove_all_matching_syms(text, phy_pwr_sym_pattern)

    # ------------------------------------------------------------------
    # D4. Add no_connect markers for the former PHY pins on PB2-P2.
    # ------------------------------------------------------------------
    # Insert no_connect markers just before the final closing ')' of
    # the entire schematic.
    no_conn_text = "\n" + phy_no_connects() + "\n"
    # Find the very last ')' in the file (the file-level closing paren).
    last_close = text.rfind('\n)')
    if last_close != -1:
        text = text[:last_close] + no_conn_text + text[last_close:]

    # ------------------------------------------------------------------
    # E/F. Add all new EMI component instances before the final ')'.
    # ------------------------------------------------------------------
    new_instances = (
        "\n" +
        inst_cmc_can(335.0, 170.0) + "\n" +
        inst_tvs_can(355.0, 175.0) + "\n" +
        inst_cmc_rs485(235.0, 260.0) + "\n" +
        inst_tvs_rs485(255.0, 265.0) + "\n" +
        inst_tvs_1553(330.0, 365.0) + "\n" +
        inst_fb_pwr(85.0, 123.09) + "\n" +
        inst_x2y_can(320.0, 180.0) + "\n" +
        inst_x2y_rs485(220.0, 270.0) + "\n"
    )
    last_close2 = text.rfind('\n)')
    if last_close2 != -1:
        text = text[:last_close2] + new_instances + text[last_close2:]

    # ------------------------------------------------------------------
    # I. Replace QMC5883L lib_symbol with MMC5983MA lib_symbol.
    #    The MMC5983MA is a drop-in upgrade: same 5 pins (SCL, SDA, GND,
    #    VDD, DRDY), same body geometry, higher performance and AEC-Q100.
    # ------------------------------------------------------------------
    try:
        s, e = find_sexp_block(text, 'symbol "QMC5883L"')
        text = text[:s] + lib_sym_mmc5983ma() + "\n" + text[e:]
        print("  Replaced QMC5883L lib_symbol with MMC5983MA")
    except ValueError as exc:
        print(f"WARNING: QMC5883L lib_symbol not found: {exc}", file=sys.stderr)

    # Replace the QMC5883L symbol instance with an MMC5983MA instance.
    # The instance sits at the same position (155, 560) and has the same
    # net connections; only the lib_id and Value/Footprint/Datasheet change.
    try:
        s, e = find_sexp_block(text, 'symbol (lib_id "QMC5883L")')
        text = text[:s] + inst_mag_v2(155.0, 560.0) + "\n" + text[e:]
        print("  Replaced QMC5883L instance with MMC5983MA instance")
    except ValueError as exc:
        print(f"WARNING: QMC5883L instance not found: {exc}", file=sys.stderr)

    # ------------------------------------------------------------------
    # J. Replace INA219AIDR lib_symbol with INA226AIDGSR lib_symbol.
    #    The INA226 is pin-compatible at the net level: IN+, IN−, GND,
    #    supply (VS vs V+), SDA, SCL, A0, A1 all connect identically.
    # ------------------------------------------------------------------
    try:
        s, e = find_sexp_block(text, 'symbol "INA219AIDR"')
        text = text[:s] + lib_sym_ina226() + "\n" + text[e:]
        print("  Replaced INA219AIDR lib_symbol with INA226AIDGSR")
    except ValueError as exc:
        print(f"WARNING: INA219AIDR lib_symbol not found: {exc}", file=sys.stderr)

    # Replace the INA219AIDR symbol instance with an INA226AIDGSR instance.
    try:
        s, e = find_sexp_block(text, 'symbol (lib_id "INA219AIDR")')
        text = text[:s] + inst_batt_mon_v2(290.0, 560.0) + "\n" + text[e:]
        print("  Replaced INA219AIDR instance with INA226AIDGSR instance")
    except ValueError as exc:
        print(f"WARNING: INA219AIDR instance not found: {exc}", file=sys.stderr)

    # ------------------------------------------------------------------
    # K. Add PRTR5V0U2X TVS on the SBUS_RAW input net (D_SBUS_TVS).
    #    The PRTR5V0U2X lib_symbol is already present from Step E above.
    #    We simply append a new instance.
    # ------------------------------------------------------------------
    sbus_tvs_block = "\n" + inst_sbus_tvs(125.0, 627.54) + "\n"
    last_close_k = text.rfind('\n)')
    if last_close_k != -1:
        text = text[:last_close_k] + sbus_tvs_block + text[last_close_k:]
        print("  Added D_SBUS_TVS (PRTR5V0U2X) on SBUS_RAW at (125, 627.54)")

    # ------------------------------------------------------------------
    # G. Update sheet UUID in sheet_instances section.
    #    The source has no explicit sheet_instances block; KiCad generates
    #    one automatically.  We add a sheet_instances block if absent to
    #    pin the UUID, or update it if present.
    # ------------------------------------------------------------------
    new_sheet_uuid = "a2000000-0000-0000-0000-000000000001"
    sheet_inst_pattern = re.compile(
        r'\(sheet_instances\s*\(path\s*"/"\s*\(page\s*"[^"]*"\s*\)\s*\)\s*\)'
    )
    if sheet_inst_pattern.search(text):
        # Replace the page-path entry UUID if one exists embedded in a uuid field.
        pass  # KiCad inlines page info without a uuid attribute in this version.
    else:
        # Inject a minimal sheet_instances block.
        sheet_inst_block = (
            f'\n  (sheet_instances\n'
            f'    (path "/" (page "1"))\n'
            f'  )\n'
        )
        last_close3 = text.rfind('\n)')
        if last_close3 != -1:
            text = text[:last_close3] + sheet_inst_block + text[last_close3:]

    # ------------------------------------------------------------------
    # H. Remap all UUIDs from old prefix to new prefix.
    # ------------------------------------------------------------------
    text = text.replace(OLD_UUID_PREFIX, NEW_UUID_PREFIX)

    return text


# ===========================================================================
# Entry point
# ===========================================================================

def main() -> None:
    """Read CAPE-A-1.kicad_sch, transform it, and write CAPE-A-2.kicad_sch."""
    # --- Read source ---
    if not os.path.isfile(SRC_PATH):
        print(f"ERROR: Source file not found: {SRC_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(SRC_PATH, "r", encoding="utf-8") as fh:
        src_text = fh.read()

    print(f"Read {len(src_text):,} characters from {SRC_PATH}")

    # --- Transform ---
    result_text = transform(src_text)

    # --- Write output ---
    with open(DST_PATH, "w", encoding="utf-8") as fh:
        fh.write(result_text)

    line_count = result_text.count('\n') + 1
    print(f"Wrote {line_count:,} lines ({len(result_text):,} characters) to {DST_PATH}")


if __name__ == "__main__":
    main()
