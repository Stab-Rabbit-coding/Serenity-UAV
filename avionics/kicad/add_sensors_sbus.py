#!/usr/bin/env python3
"""
add_sensors_sbus.py — Add sensor and SBUS/XCVR hardware to Cape-A-1 and Cape-B-1
===================================================================================

Appends new hardware to CAPE-A-1.kicad_sch and CAPE-B-1.kicad_sch in-place so
that the v1 schematics carry the additional components before gen_cape_a2.py and
gen_cape_b2.py transform them into v2 variants.

CAPE-A-1 additions (Y ≥ 540):
  1.  QMC5883L        — QST I²C magnetometer, LGA-16, fixed addr 0x0D
  2.  INA219AIDR      — TI I²C current/voltage monitor, SOIC-8
  3.  J_VBAT          — JST GH 2-pin battery-voltage sense connector
  4a. J_SBUS          — JST GH 3-pin SBUS RC input connector
  4b. R_SBUS          — 100 Ω series resistor, 0402
  4c. U_SBUS          — Nexperia 74LVC1G14 Schmitt inverter, SOT-23-5

CAPE-B-1 additions (Y ≥ 540):
  5.  J_XCVR          — JST GH 6-pin transceiver/SBUS shared connector
  6.  U_SBUS_B        — Nexperia 74LVC1G14 Schmitt inverter (XCVR_RX_RAW)
  7.  SW1             — 2-position DIP switch (mode selector)
  8.  R_XCVR_RX       — 100 Ω series resistor (XCVR path), 0402
  9.  R_SBUS_RX       — 100 Ω series resistor (SBUS path), 0402

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
         Griffing Technology LLC
License: CC BY 4.0  |  creativecommons.org/licenses/by/4.0
Date:    2026-06-04
Project: Serenity UAV — EDF Tilt-Rotor UAV

References:
  - QST QMC5883L datasheet     : https://datasheet.lcsc.com/szlcsc/QST-QMC5883L_C192585.pdf
  - TI INA219AIDR datasheet    : https://www.ti.com/lit/ds/symlink/ina219.pdf
  - Nexperia 74LVC1G14         : https://www.nexperia.com/products/analog-logic-ics/asynchronous-interface-logic/inverting-buffers-and-drivers/series/74LVC1G14.html
  - JST GH connector series    : https://www.jst.com/wp-content/uploads/2021/01/eGH.pdf
  - KiCad S-expression format  : KiCad EDA schematic format version 20240101
"""

import os
import re
import sys

# ---------------------------------------------------------------------------
# File paths (absolute, per project convention)
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CAPE_A1_PATH = os.path.join(SCRIPT_DIR, "CAPE-A-1.kicad_sch")
CAPE_B1_PATH = os.path.join(SCRIPT_DIR, "CAPE-B-1.kicad_sch")

# ---------------------------------------------------------------------------
# UUID counters
# ---------------------------------------------------------------------------
# Cape-A-1 max existing counter: 370  →  new additions start at 400
# Cape-B-1 max existing counter: 467  →  new additions start at 500
# Prefix matches the existing CAPE-A-1 / CAPE-B-1 convention.
UUID_PREFIX = "00000000-0000-0000-0000-"

_uuid_counter_a = 400  # Cape-A-1 counter
_uuid_counter_b = 500  # Cape-B-1 counter


def next_uuid_a() -> str:
    """Return the next sequential UUID for Cape-A-1 additions.

    Counter starts at 400 to avoid collisions with existing A-1 UUIDs
    (max existing is 370).  Uses the standard '00000000-0000-0000-0000-'
    prefix so gen_cape_a2.py can remap them to the A-2 prefix in bulk.

    Returns:
        A UUID string of the form '00000000-0000-0000-0000-NNNNNNNNNNNN'.
    """
    global _uuid_counter_a
    uid = f"{UUID_PREFIX}{_uuid_counter_a:012d}"
    _uuid_counter_a += 1
    return uid


def next_uuid_b() -> str:
    """Return the next sequential UUID for Cape-B-1 additions.

    Counter starts at 500 to avoid collisions with existing B-1 UUIDs
    (max existing is 467).

    Returns:
        A UUID string of the form '00000000-0000-0000-0000-NNNNNNNNNNNN'.
    """
    global _uuid_counter_b
    uid = f"{UUID_PREFIX}{_uuid_counter_b:012d}"
    _uuid_counter_b += 1
    return uid


# ---------------------------------------------------------------------------
# Helper: S-expression parser utilities (copied from gen_cape_a2.py)
# ---------------------------------------------------------------------------


def find_balanced_sexp(text: str, start: int) -> int:
    """Return the index ONE PAST the closing ')' that balances the '(' at *start*.

    Scans *text* forward from *start*.  Raises ValueError when the text is
    exhausted before the expression is closed.  Handles quoted strings so
    that parentheses inside strings do not affect the nesting depth.

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
            if ch == "\\":
                escape_next = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    return i + 1
        i += 1
    raise ValueError(f"Unbalanced S-expression starting at index {start}")


def find_sexp_block(text: str, tag: str) -> tuple:
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
    pattern = r"\(" + re.escape(tag)
    match = re.search(pattern, text)
    if match is None:
        raise ValueError(f"Tag not found: ({tag}")
    start = match.start()
    end = find_balanced_sexp(text, start)
    return start, end


# ===========================================================================
# lib_symbol definitions — Cape-A-1 components
# ===========================================================================


def lib_sym_qmc5883l() -> str:
    """Return the KiCad lib_symbol S-expression for the QMC5883L magnetometer.

    QMC5883L: QST 3-axis magnetometer, LGA-16 package, fixed I²C address
    0x0D.  The symbol presents a 5-pin interface: SCL, SDA, GND, VDD, DRDY.

    Pin layout in library coordinates (component origin at 0,0):
      Left side (angle=0, tips at x = −10.16):
        SCL  at lib (−10.16, −2.54)
        SDA  at lib (−10.16,  0.00)
        GND  at lib (−10.16, +2.54)
      Right side (angle=180, tips at x = +10.16):
        VDD  at lib (+10.16, −2.54)
        DRDY at lib (+10.16, +2.54)
    Body rectangle: (−7.62, −3.81) to (+7.62, +3.81).

    Reference: QST QMC5883L datasheet, LCSC C192585.
    """
    return """\
  (symbol "QMC5883L" (in_bom yes) (on_board yes)
    (property "Reference" "U" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
    (property "Value" "QMC5883L" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Sensor_Magnetic:QMC5883L" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://datasheet.lcsc.com/szlcsc/QST-QMC5883L_C192585.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "QMC5883L_0_1"
      (rectangle (start -7.62 -3.81) (end 7.62 3.81)
        (stroke (width 0.254) (type default)) (fill (type background)))
    )
    (symbol "QMC5883L_1_1"
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
  )"""


def lib_sym_ina219() -> str:
    """Return the KiCad lib_symbol S-expression for the INA219AIDR.

    INA219AIDR: TI bidirectional current/voltage monitor, SOIC-8, I²C.
    SOIC-8 pin assignment (from TI datasheet SBOS137I):
      Pin 1 = GND, Pin 2 = V+, Pin 3 = IN−, Pin 4 = IN+,
      Pin 5 = A1,  Pin 6 = A0, Pin 7 = SDA, Pin 8 = SCL.

    Symbol pin layout (lib origin 0,0, 2.54 mm pitch, ±3.81 mm from centre):
      Left side (angle=0, tips at x = −10.16):
        IN+ (pin 4) at lib (−10.16, −3.81)
        IN− (pin 3) at lib (−10.16, −1.27)
        GND (pin 1) at lib (−10.16, +1.27)
        V+  (pin 2) at lib (−10.16, +3.81)
      Right side (angle=180, tips at x = +10.16):
        A1  (pin 5) at lib (+10.16, −3.81)
        A0  (pin 6) at lib (+10.16, −1.27)
        SDA (pin 7) at lib (+10.16, +1.27)
        SCL (pin 8) at lib (+10.16, +3.81)
    Body rectangle: (−7.62, −5.08) to (+7.62, +5.08).

    Reference: TI INA219 datasheet SBOS137I (Rev. I, 2015).
    """
    return """\
  (symbol "INA219AIDR" (in_bom yes) (on_board yes)
    (property "Reference" "U" (at 0 -7.62 0) (effects (font (size 1.27 1.27))))
    (property "Value" "INA219AIDR" (at 0 7.62 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.ti.com/lit/ds/symlink/ina219.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "INA219AIDR_0_1"
      (rectangle (start -7.62 -5.08) (end 7.62 5.08)
        (stroke (width 0.254) (type default)) (fill (type background)))
    )
    (symbol "INA219AIDR_1_1"
      (pin input line (at -10.16 -3.81 0) (length 2.54)
        (name "IN+" (effects (font (size 1.016 1.016))))
        (number "4" (effects (font (size 1.016 1.016)))))
      (pin input line (at -10.16 -1.27 0) (length 2.54)
        (name "IN-" (effects (font (size 1.016 1.016))))
        (number "3" (effects (font (size 1.016 1.016)))))
      (pin power_in line (at -10.16 1.27 0) (length 2.54)
        (name "GND" (effects (font (size 1.016 1.016))))
        (number "1" (effects (font (size 1.016 1.016)))))
      (pin power_in line (at -10.16 3.81 0) (length 2.54)
        (name "V+" (effects (font (size 1.016 1.016))))
        (number "2" (effects (font (size 1.016 1.016)))))
      (pin input line (at 10.16 -3.81 180) (length 2.54)
        (name "A1" (effects (font (size 1.016 1.016))))
        (number "5" (effects (font (size 1.016 1.016)))))
      (pin input line (at 10.16 -1.27 180) (length 2.54)
        (name "A0" (effects (font (size 1.016 1.016))))
        (number "6" (effects (font (size 1.016 1.016)))))
      (pin bidirectional line (at 10.16 1.27 180) (length 2.54)
        (name "SDA" (effects (font (size 1.016 1.016))))
        (number "7" (effects (font (size 1.016 1.016)))))
      (pin input line (at 10.16 3.81 180) (length 2.54)
        (name "SCL" (effects (font (size 1.016 1.016))))
        (number "8" (effects (font (size 1.016 1.016)))))
    )
  )"""


def lib_sym_conn_jst_gh_02p() -> str:
    """Return the KiCad lib_symbol S-expression for a 2-pin JST GH connector.

    Conn_JST_GH_02P: JST GH series SMD 2-position horizontal connector
    (SM02B-GHS-TB).  The symbol has two pins on the right side (tips at
    x = +2.54 in library coordinates, angle=180 meaning pin faces right).

    Pin layout (lib origin 0,0):
      Pin 1 at lib (+2.54, −1.27, 180)   →  tip at +2.54 y = −1.27
      Pin 2 at lib (+2.54, +1.27, 180)   →  tip at +2.54 y = +1.27
    Body: (−3.81, −2.54) to (0, +2.54).

    Reference: JST SM02B-GHS-TB product page.
    """
    return """\
  (symbol "Conn_JST_GH_02P" (in_bom yes) (on_board yes)
    (property "Reference" "J" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
    (property "Value" "Conn_JST_GH_02P" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Connector_JST:JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.jst.com/wp-content/uploads/2021/01/eGH.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "Conn_JST_GH_02P_0_1"
      (rectangle (start -3.81 -2.54) (end 0 2.54)
        (stroke (width 0.254) (type default)) (fill (type background)))
    )
    (symbol "Conn_JST_GH_02P_1_1"
      (pin passive line (at 2.54 -1.27 180) (length 2.54)
        (name "Pin_1" (effects (font (size 1.016 1.016))))
        (number "1" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 2.54 1.27 180) (length 2.54)
        (name "Pin_2" (effects (font (size 1.016 1.016))))
        (number "2" (effects (font (size 1.016 1.016)))))
    )
  )"""


def lib_sym_conn_jst_gh_03p() -> str:
    """Return the KiCad lib_symbol S-expression for a 3-pin JST GH connector.

    Conn_JST_GH_03P: JST GH series SMD 3-position horizontal connector
    (SM03B-GHS-TB).  Three pins on the right side, 2.54 mm pitch.

    Pin layout (lib origin 0,0):
      Pin 1 at lib (+2.54, −2.54, 180)
      Pin 2 at lib (+2.54,  0.00, 180)
      Pin 3 at lib (+2.54, +2.54, 180)
    Body: (−3.81, −3.81) to (0, +3.81).

    Reference: JST SM03B-GHS-TB product page.
    """
    return """\
  (symbol "Conn_JST_GH_03P" (in_bom yes) (on_board yes)
    (property "Reference" "J" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
    (property "Value" "Conn_JST_GH_03P" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Connector_JST:JST_GH_SM03B-GHS-TB_1x03-1MP_P1.25mm_Horizontal" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.jst.com/wp-content/uploads/2021/01/eGH.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "Conn_JST_GH_03P_0_1"
      (rectangle (start -3.81 -3.81) (end 0 3.81)
        (stroke (width 0.254) (type default)) (fill (type background)))
    )
    (symbol "Conn_JST_GH_03P_1_1"
      (pin passive line (at 2.54 -2.54 180) (length 2.54)
        (name "Pin_1" (effects (font (size 1.016 1.016))))
        (number "1" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 2.54 0.00 180) (length 2.54)
        (name "Pin_2" (effects (font (size 1.016 1.016))))
        (number "2" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 2.54 2.54 180) (length 2.54)
        (name "Pin_3" (effects (font (size 1.016 1.016))))
        (number "3" (effects (font (size 1.016 1.016)))))
    )
  )"""


def lib_sym_resistor() -> str:
    """Return the KiCad lib_symbol S-expression for a generic 0402 resistor.

    R_SMD: 2-pin passive resistor symbol used for R_SBUS (100 Ω, 0402).
    Pin length = 3.81 mm from body edge; body half-width = 1.27 mm.

    Pin layout (lib origin 0,0):
      Pin 1 at lib (−3.81, 0, 0)    →  tip at −3.81
      Pin 2 at lib (+3.81, 0, 180)  →  tip at +3.81
    Body: (−1.27, −0.508) to (+1.27, +0.508).

    Reference: Generic SMD resistor.
    """
    return """\
  (symbol "R_SMD" (in_bom yes) (on_board yes)
    (property "Reference" "R" (at 0 -1.778 0) (effects (font (size 1.27 1.27))))
    (property "Value" "R" (at 0 1.778 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Resistor_SMD:R_0402_1005Metric" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "R_SMD_0_1"
      (rectangle (start -1.27 -0.508) (end 1.27 0.508)
        (stroke (width 0.254) (type default)) (fill (type background)))
    )
    (symbol "R_SMD_1_1"
      (pin passive line (at -3.81 0.00 0) (length 2.54)
        (name "~" (effects (font (size 1.016 1.016))))
        (number "1" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 3.81 0.00 180) (length 2.54)
        (name "~" (effects (font (size 1.016 1.016))))
        (number "2" (effects (font (size 1.016 1.016)))))
    )
  )"""


def lib_sym_74lvc1g14() -> str:
    """Return the KiCad lib_symbol S-expression for the 74LVC1G14 Schmitt inverter.

    74LVC1G14: Nexperia single Schmitt-trigger inverter, SOT-23-5.
    Used to invert the SBUS signal from the RC receiver (idle-high inverted
    UART at 100 kbps) into standard UART idle-high polarity.

    Pin layout (lib origin 0,0):
      A   (pin 1, input)    at lib (−7.62,  0.00, 0)
      GND (pin 2, power_in) at lib ( 0.00, +5.08, 270)
      Y   (pin 4, output)   at lib (+7.62,  0.00, 180)
      VCC (pin 5, power_in) at lib ( 0.00, −5.08, 90)
    Body: (−5.08, −2.54) to (+5.08, +2.54).

    Reference: Nexperia 74LVC1G14 datasheet (Rev. 11, 2021).
    """
    return """\
  (symbol "74LVC1G14" (in_bom yes) (on_board yes)
    (property "Reference" "U" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
    (property "Value" "74LVC1G14GW" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_TO_SOT_SMD:SOT-23-5" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.nexperia.com/products/analog-logic-ics/asynchronous-interface-logic/inverting-buffers-and-drivers/series/74LVC1G14.html" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "74LVC1G14_0_1"
      (rectangle (start -5.08 -2.54) (end 5.08 2.54)
        (stroke (width 0.254) (type default)) (fill (type background)))
    )
    (symbol "74LVC1G14_1_1"
      (pin input line (at -7.62 0.00 0) (length 2.54)
        (name "A" (effects (font (size 1.016 1.016))))
        (number "1" (effects (font (size 1.016 1.016)))))
      (pin power_in line (at 0.00 5.08 270) (length 2.54)
        (name "GND" (effects (font (size 1.016 1.016))))
        (number "2" (effects (font (size 1.016 1.016)))))
      (pin output line (at 7.62 0.00 180) (length 2.54)
        (name "Y" (effects (font (size 1.016 1.016))))
        (number "4" (effects (font (size 1.016 1.016)))))
      (pin power_in line (at 0.00 -5.08 90) (length 2.54)
        (name "VCC" (effects (font (size 1.016 1.016))))
        (number "5" (effects (font (size 1.016 1.016)))))
    )
  )"""


# ===========================================================================
# lib_symbol definitions — Cape-B-1 additional components
# ===========================================================================


def lib_sym_conn_jst_gh_06p() -> str:
    """Return the KiCad lib_symbol S-expression for a 6-pin JST GH connector.

    Conn_JST_GH_06P: JST GH series SMD 6-position horizontal connector
    (SM06B-GHS-TB).  Six pins on the right side, 2.54 mm pitch.

    Pin layout (lib origin 0,0):
      Pin 1 at lib (+2.54, −6.35, 180)
      Pin 2 at lib (+2.54, −3.81, 180)
      Pin 3 at lib (+2.54, −1.27, 180)
      Pin 4 at lib (+2.54, +1.27, 180)
      Pin 5 at lib (+2.54, +3.81, 180)
      Pin 6 at lib (+2.54, +6.35, 180)
    Body: (−3.81, −7.62) to (0, +7.62).

    Reference: JST SM06B-GHS-TB product page.
    """
    return """\
  (symbol "Conn_JST_GH_06P" (in_bom yes) (on_board yes)
    (property "Reference" "J" (at 0 -8.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "Conn_JST_GH_06P" (at 0 8.89 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Connector_JST:JST_GH_SM06B-GHS-TB_1x06-1MP_P1.25mm_Horizontal" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.jst.com/wp-content/uploads/2021/01/eGH.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "Conn_JST_GH_06P_0_1"
      (rectangle (start -3.81 -7.62) (end 0 7.62)
        (stroke (width 0.254) (type default)) (fill (type background)))
    )
    (symbol "Conn_JST_GH_06P_1_1"
      (pin passive line (at 2.54 -6.35 180) (length 2.54)
        (name "Pin_1" (effects (font (size 1.016 1.016))))
        (number "1" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 2.54 -3.81 180) (length 2.54)
        (name "Pin_2" (effects (font (size 1.016 1.016))))
        (number "2" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 2.54 -1.27 180) (length 2.54)
        (name "Pin_3" (effects (font (size 1.016 1.016))))
        (number "3" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 2.54 1.27 180) (length 2.54)
        (name "Pin_4" (effects (font (size 1.016 1.016))))
        (number "4" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 2.54 3.81 180) (length 2.54)
        (name "Pin_5" (effects (font (size 1.016 1.016))))
        (number "5" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 2.54 6.35 180) (length 2.54)
        (name "Pin_6" (effects (font (size 1.016 1.016))))
        (number "6" (effects (font (size 1.016 1.016)))))
    )
  )"""


def lib_sym_sw_dip_x02() -> str:
    """Return the KiCad lib_symbol S-expression for a 2-position DIP switch.

    SW_DIP_x02: Two-position DIP switch with two independent SPST contacts.
    Each switch has a COM (common) and NO (normally-open) terminal.

    Pin layout (lib origin 0,0):
      COM1 (pin 1) at lib (−7.62, −2.54, 0)   →  tip at −7.62
      NO1  (pin 2) at lib (+7.62, −2.54, 180)  →  tip at +7.62
      COM2 (pin 3) at lib (−7.62, +2.54, 0)   →  tip at −7.62
      NO2  (pin 4) at lib (+7.62, +2.54, 180)  →  tip at +7.62
    Body: (−5.08, −5.08) to (+5.08, +5.08).

    Reference: Generic DIP switch symbol.
    """
    return """\
  (symbol "SW_DIP_x02" (in_bom yes) (on_board yes)
    (property "Reference" "SW" (at 0 -6.35 0) (effects (font (size 1.27 1.27))))
    (property "Value" "SW_DIP_x02" (at 0 6.35 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_DIP:DIP-4_W7.62mm" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "SW_DIP_x02_0_1"
      (rectangle (start -5.08 -5.08) (end 5.08 5.08)
        (stroke (width 0.254) (type default)) (fill (type background)))
    )
    (symbol "SW_DIP_x02_1_1"
      (pin passive line (at -7.62 -2.54 0) (length 2.54)
        (name "COM1" (effects (font (size 1.016 1.016))))
        (number "1" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 7.62 -2.54 180) (length 2.54)
        (name "NO1" (effects (font (size 1.016 1.016))))
        (number "2" (effects (font (size 1.016 1.016)))))
      (pin passive line (at -7.62 2.54 0) (length 2.54)
        (name "COM2" (effects (font (size 1.016 1.016))))
        (number "3" (effects (font (size 1.016 1.016)))))
      (pin passive line (at 7.62 2.54 180) (length 2.54)
        (name "NO2" (effects (font (size 1.016 1.016))))
        (number "4" (effects (font (size 1.016 1.016)))))
    )
  )"""


# ===========================================================================
# Component instance generators — Cape-A-1
# ===========================================================================


def inst_qmc5883l(cx: float, cy: float) -> str:
    """Return the symbol instance block for the QMC5883L magnetometer.

    The component is centred at (*cx*, *cy*) = (155, 560) on the schematic.
    Absolute pin tip coordinates are derived from library offsets:
      SCL  tip at (cx − 10.16,  cy − 2.54)  →  global I2C1_SCL  (angle=180)
      SDA  tip at (cx − 10.16,  cy + 0.00)  →  global I2C1_SDA  (angle=180)
      GND  tip at (cx − 10.16,  cy + 2.54)  →  GND power (270°)
      VDD  tip at (cx + 10.16,  cy − 2.54)  →  +3V3 power (90°)
      DRDY tip at (cx + 10.16,  cy + 2.54)  →  global GPIO_MAG_DRDY (angle=0)

    Args:
        cx: Component centre X coordinate in mm.
        cy: Component centre Y coordinate in mm.
    """
    # Pin tip X coordinates
    left_x = cx - 10.16  # 144.84 for cx=155
    right_x = cx + 10.16  # 165.16 for cx=155

    # Pin tip Y coordinates
    y_scl = cy - 2.54  # 557.46
    y_sda = cy  # 560.00
    y_gnd = cy + 2.54  # 562.54
    y_vdd = cy - 2.54  # 557.46
    y_drdy = cy + 2.54  # 562.54

    uid_inst = next_uuid_a()
    uid_p1 = next_uuid_a()
    uid_p2 = next_uuid_a()
    uid_p3 = next_uuid_a()
    uid_p4 = next_uuid_a()
    uid_p5 = next_uuid_a()

    return f"""\
  (symbol (lib_id "QMC5883L") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uid_inst}")
    (property "Reference" "U_MAG" (at {cx:.2f} {cy - 5.08:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "QMC5883L" (at {cx:.2f} {cy + 5.08:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Sensor_Magnetic:QMC5883L" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://datasheet.lcsc.com/szlcsc/QST-QMC5883L_C192585.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{uid_p1}"))
    (pin "2" (uuid "{uid_p2}"))
    (pin "3" (uuid "{uid_p3}"))
    (pin "4" (uuid "{uid_p4}"))
    (pin "5" (uuid "{uid_p5}"))
  )
  (global_label "I2C1_SCL" (shape bidirectional) (at {left_x:.2f} {y_scl:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid_a()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_x:.2f} {y_scl:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (global_label "I2C1_SDA" (shape bidirectional) (at {left_x:.2f} {y_sda:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid_a()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_x:.2f} {y_sda:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (symbol (lib_id "GND") (at {left_x:.2f} {y_gnd:.2f} 270)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid_a()}")
    (property "Reference" "#PWR0A401" (at {left_x:.2f} {y_gnd:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at {left_x:.2f} {y_gnd + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid_a()}"))
  )
  (symbol (lib_id "+3V3") (at {right_x:.2f} {y_vdd:.2f} 90)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid_a()}")
    (property "Reference" "#PWR0A402" (at {right_x:.2f} {y_vdd:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "+3V3" (at {right_x:.2f} {y_vdd - 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid_a()}"))
  )
  (global_label "GPIO_MAG_DRDY" (shape bidirectional) (at {right_x:.2f} {y_drdy:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid_a()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {right_x:.2f} {y_drdy:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))"""


def inst_ina219(cx: float, cy: float) -> str:
    """Return the symbol instance block for the INA219AIDR battery monitor.

    The component is centred at (*cx*, *cy*) = (290, 560).

    Pin tip coordinates derived from lib offsets (2.54 mm pitch, ±3.81 from centre):
      Left side (tip x = cx − 10.16 = 279.84):
        IN+: y = cy − 3.81 = 556.19  →  global VBAT_MON_P (angle=180)
        IN−: y = cy − 1.27 = 558.73  →  global VBAT_MON_P (angle=180)  [voltage-only mode]
        GND: y = cy + 1.27 = 561.27  →  GND power (270°)
        V+:  y = cy + 3.81 = 563.81  →  +3V3 power (90°)
      Right side (tip x = cx + 10.16 = 300.16):
        A1:  y = cy − 3.81 = 556.19  →  GND power (270°)
        A0:  y = cy − 1.27 = 558.73  →  GND power (270°)
        SDA: y = cy + 1.27 = 561.27  →  global I2C1_SDA (angle=0)
        SCL: y = cy + 3.81 = 563.81  →  global I2C1_SCL (angle=0)

    Note: IN+ and IN− are both tied to VBAT_MON_P.  This implements
    voltage-only monitoring mode (no shunt resistor).  For current monitoring,
    insert a 10 mΩ shunt between J_VBAT pin 1 and IN+, with IN− on the shunt
    low side.

    Args:
        cx: Component centre X coordinate in mm.
        cy: Component centre Y coordinate in mm.
    """
    left_x = cx - 10.16  # 279.84
    right_x = cx + 10.16  # 300.16

    y_in_plus = cy - 3.81  # 556.19
    y_in_minus = cy - 1.27  # 558.73
    y_gnd_pin = cy + 1.27  # 561.27
    y_vplus = cy + 3.81  # 563.81

    y_a1 = cy - 3.81  # 556.19
    y_a0 = cy - 1.27  # 558.73
    y_sda = cy + 1.27  # 561.27
    y_scl = cy + 3.81  # 563.81

    uid_inst = next_uuid_a()
    uid_p1 = next_uuid_a()
    uid_p2 = next_uuid_a()
    uid_p3 = next_uuid_a()
    uid_p4 = next_uuid_a()
    uid_p5 = next_uuid_a()
    uid_p6 = next_uuid_a()
    uid_p7 = next_uuid_a()
    uid_p8 = next_uuid_a()

    return f"""\
  (symbol (lib_id "INA219AIDR") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uid_inst}")
    (property "Reference" "U_BMON" (at {cx:.2f} {cy - 7.62:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "INA219AIDR" (at {cx:.2f} {cy + 7.62:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.ti.com/lit/ds/symlink/ina219.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
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
    (uuid "{next_uuid_a()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_x:.2f} {y_in_plus:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (global_label "VBAT_MON_P" (shape bidirectional) (at {left_x:.2f} {y_in_minus:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid_a()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_x:.2f} {y_in_minus:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (symbol (lib_id "GND") (at {left_x:.2f} {y_gnd_pin:.2f} 270)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid_a()}")
    (property "Reference" "#PWR0A403" (at {left_x:.2f} {y_gnd_pin:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at {left_x:.2f} {y_gnd_pin + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid_a()}"))
  )
  (symbol (lib_id "+3V3") (at {left_x:.2f} {y_vplus:.2f} 90)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid_a()}")
    (property "Reference" "#PWR0A404" (at {left_x:.2f} {y_vplus:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "+3V3" (at {left_x:.2f} {y_vplus - 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid_a()}"))
  )
  (symbol (lib_id "GND") (at {right_x:.2f} {y_a1:.2f} 270)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid_a()}")
    (property "Reference" "#PWR0A405" (at {right_x:.2f} {y_a1:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at {right_x:.2f} {y_a1 + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid_a()}"))
  )
  (symbol (lib_id "GND") (at {right_x:.2f} {y_a0:.2f} 270)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid_a()}")
    (property "Reference" "#PWR0A406" (at {right_x:.2f} {y_a0:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at {right_x:.2f} {y_a0 + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid_a()}"))
  )
  (global_label "I2C1_SDA" (shape bidirectional) (at {right_x:.2f} {y_sda:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid_a()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {right_x:.2f} {y_sda:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (global_label "I2C1_SCL" (shape bidirectional) (at {right_x:.2f} {y_scl:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid_a()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {right_x:.2f} {y_scl:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (text "NOTE: IN+ and IN- tied to VBAT_MON_P = voltage monitoring only.\\nFor current monitoring: insert 10 mO shunt between J_VBAT pin 1 and IN+ with IN- on shunt low side."
    (at {cx:.2f} {cy + 10.16:.2f} 0) (effects (font (size 1.016 1.016))))"""


def inst_j_vbat(cx: float, cy: float) -> str:
    """Return the symbol instance block for J_VBAT (JST GH 2-pin).

    J_VBAT is the battery voltage sense connector, placed at (*cx*, *cy*)
    = (370, 557).

    Pin 1 tip at (cx + 2.54, cy − 1.27) = (372.54, 555.73) → VBAT_MON_P
    Pin 2 tip at (cx + 2.54, cy + 1.27) = (372.54, 558.27) → GND power

    Args:
        cx: Component centre X coordinate in mm.
        cy: Component centre Y coordinate in mm.
    """
    tip_x = cx + 2.54  # 372.54 — right side pin tips
    y_pin1 = cy - 1.27  # 555.73
    y_pin2 = cy + 1.27  # 558.27

    uid_inst = next_uuid_a()
    uid_p1 = next_uuid_a()
    uid_p2 = next_uuid_a()

    return f"""\
  (symbol (lib_id "Conn_JST_GH_02P") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uid_inst}")
    (property "Reference" "J_VBAT" (at {cx:.2f} {cy - 3.81:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "Conn_JST_GH_02P" (at {cx:.2f} {cy + 3.81:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Connector_JST:JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.jst.com/wp-content/uploads/2021/01/eGH.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{uid_p1}"))
    (pin "2" (uuid "{uid_p2}"))
  )
  (global_label "VBAT_MON_P" (shape bidirectional) (at {tip_x:.2f} {y_pin1:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid_a()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {tip_x:.2f} {y_pin1:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (symbol (lib_id "GND") (at {tip_x:.2f} {y_pin2:.2f} 270)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid_a()}")
    (property "Reference" "#PWR0A407" (at {tip_x:.2f} {y_pin2:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at {tip_x:.2f} {y_pin2 + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid_a()}"))
  )"""


def inst_j_sbus(cx: float, cy: float) -> str:
    """Return the symbol instance block for J_SBUS (JST GH 3-pin SBUS input).

    J_SBUS is the SBUS RC input connector, placed at (*cx*, *cy*) = (100, 625).

    Pin tip positions (lib angle=180 → pins on right side, tip at cx + 2.54):
      Pin 1 (GND)      tip (102.54, 622.46)  →  GND power (270°)
      Pin 2 (+5V)      tip (102.54, 625.00)  →  +5V power (90°)
      Pin 3 (SBUS_RAW) tip (102.54, 627.54)  →  global SBUS_RAW (angle=0)

    Args:
        cx: Component centre X in mm.
        cy: Component centre Y in mm.
    """
    tip_x = cx + 2.54  # 102.54
    y_p1 = cy - 2.54  # 622.46 — GND
    y_p2 = cy  # 625.00 — +5V
    y_p3 = cy + 2.54  # 627.54 — SBUS_RAW

    uid_inst = next_uuid_a()
    uid_p1 = next_uuid_a()
    uid_p2 = next_uuid_a()
    uid_p3 = next_uuid_a()

    return f"""\
  (symbol (lib_id "Conn_JST_GH_03P") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uid_inst}")
    (property "Reference" "J_SBUS" (at {cx:.2f} {cy - 5.08:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "Conn_JST_GH_03P" (at {cx:.2f} {cy + 5.08:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Connector_JST:JST_GH_SM03B-GHS-TB_1x03-1MP_P1.25mm_Horizontal" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.jst.com/wp-content/uploads/2021/01/eGH.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{uid_p1}"))
    (pin "2" (uuid "{uid_p2}"))
    (pin "3" (uuid "{uid_p3}"))
  )
  (symbol (lib_id "GND") (at {tip_x:.2f} {y_p1:.2f} 270)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid_a()}")
    (property "Reference" "#PWR0A408" (at {tip_x:.2f} {y_p1:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at {tip_x:.2f} {y_p1 + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid_a()}"))
  )
  (symbol (lib_id "+5V") (at {tip_x:.2f} {y_p2:.2f} 90)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid_a()}")
    (property "Reference" "#PWR0A409" (at {tip_x:.2f} {y_p2:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "+5V" (at {tip_x:.2f} {y_p2 - 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid_a()}"))
  )
  (global_label "SBUS_RAW" (shape bidirectional) (at {tip_x:.2f} {y_p3:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid_a()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {tip_x:.2f} {y_p3:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))"""


def inst_r_sbus(cx: float, cy: float) -> str:
    """Return the symbol instance block for R_SBUS (100 Ω 0402 series resistor).

    R_SBUS is placed at (*cx*, *cy*) = (145, 627.54).  Pin tip positions:
      Pin 1 tip at (cx − 3.81, cy) = (141.19, 627.54)  →  global SBUS_RAW (angle=180)
      Pin 2 tip at (cx + 3.81, cy) = (148.81, 627.54)  →  wire to U_SBUS input

    Args:
        cx: Component centre X in mm.
        cy: Component centre Y in mm.
    """
    left_tip_x = cx - 3.81  # 141.19
    right_tip_x = cx + 3.81  # 148.81

    uid_inst = next_uuid_a()
    uid_p1 = next_uuid_a()
    uid_p2 = next_uuid_a()

    return f"""\
  (symbol (lib_id "R_SMD") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uid_inst}")
    (property "Reference" "R_SBUS" (at {cx:.2f} {cy - 1.778:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "100R" (at {cx:.2f} {cy + 1.778:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Resistor_SMD:R_0402_1005Metric" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{uid_p1}"))
    (pin "2" (uuid "{uid_p2}"))
  )
  (global_label "SBUS_RAW" (shape bidirectional) (at {left_tip_x:.2f} {cy:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid_a()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {left_tip_x:.2f} {cy:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))"""


def inst_u_sbus(cx: float, cy: float, r_sbus_right_tip_x: float) -> str:
    """Return the symbol instance block for U_SBUS (74LVC1G14 Schmitt inverter).

    U_SBUS is placed at (*cx*, *cy*) = (180, 627.54).

    Pin tip positions derived from lib offsets:
      A   tip at (cx − 7.62, cy)        = (172.38, 627.54)  [input]
      Y   tip at (cx + 7.62, cy)        = (187.62, 627.54)  [output]
      VCC tip at (cx, cy − 5.08)        = (180.00, 622.46)  [+3V3, angle=90]
      GND tip at (cx, cy + 5.08)        = (180.00, 632.62)  [GND, angle=270]

    A connecting wire runs from R_SBUS pin 2 tip at *r_sbus_right_tip_x* to
    the A pin tip at (cx − 7.62).

    Args:
        cx: Component centre X in mm.
        cy: Component centre Y in mm.
        r_sbus_right_tip_x: X coordinate of R_SBUS pin 2 tip (wire start).
    """
    a_tip_x = cx - 7.62  # 172.38
    y_tip_x = cx + 7.62  # 187.62
    vcc_tip_y = cy - 5.08  # 622.46
    gnd_tip_y = cy + 5.08  # 632.62

    uid_inst = next_uuid_a()
    uid_p1 = next_uuid_a()
    uid_p2 = next_uuid_a()
    uid_p4 = next_uuid_a()
    uid_p5 = next_uuid_a()

    return f"""\
  (symbol (lib_id "74LVC1G14") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uid_inst}")
    (property "Reference" "U_SBUS" (at {cx:.2f} {cy - 5.08:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "74LVC1G14GW" (at {cx:.2f} {cy + 5.08:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_TO_SOT_SMD:SOT-23-5" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.nexperia.com/products/analog-logic-ics/asynchronous-interface-logic/inverting-buffers-and-drivers/series/74LVC1G14.html" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{uid_p1}"))
    (pin "2" (uuid "{uid_p2}"))
    (pin "4" (uuid "{uid_p4}"))
    (pin "5" (uuid "{uid_p5}"))
  )
  (wire (pts (xy {r_sbus_right_tip_x:.2f} {cy:.2f}) (xy {a_tip_x:.2f} {cy:.2f}))
    (stroke (width 0) (type default))
    (uuid "{next_uuid_a()}"))
  (global_label "UART_SBUS_RX" (shape bidirectional) (at {y_tip_x:.2f} {cy:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid_a()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {y_tip_x:.2f} {cy:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (symbol (lib_id "+3V3") (at {cx:.2f} {vcc_tip_y:.2f} 90)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid_a()}")
    (property "Reference" "#PWR0A410" (at {cx:.2f} {vcc_tip_y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "+3V3" (at {cx:.2f} {vcc_tip_y - 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid_a()}"))
  )
  (symbol (lib_id "GND") (at {cx:.2f} {gnd_tip_y:.2f} 270)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid_a()}")
    (property "Reference" "#PWR0A411" (at {cx:.2f} {gnd_tip_y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at {cx:.2f} {gnd_tip_y + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid_a()}"))
  )"""


# ===========================================================================
# Component instance generators — Cape-B-1
# ===========================================================================


def inst_j_xcvr(cx: float, cy: float) -> str:
    """Return the symbol instance block for J_XCVR (JST GH 6-pin).

    J_XCVR is the shared 49 MHz transceiver / SBUS RC receiver connector,
    placed at (*cx*, *cy*) = (100, 560).

    Pin tip positions (tip_x = cx + 2.54 = 102.54):
      Pin 1 (102.54, 553.65)  →  GND power
      Pin 2 (102.54, 556.19)  →  +5V power
      Pin 3 (102.54, 558.73)  →  global UART_49MHZ_XCVR_TX (angle=0)
      Pin 4 (102.54, 561.27)  →  global XCVR_RX_RAW  (angle=0)
      Pin 5 (102.54, 563.81)  →  global XCVR_PTT_N   (angle=0)
      Pin 6 (102.54, 566.35)  →  +3V3 power

    Args:
        cx: Component centre X in mm.
        cy: Component centre Y in mm.
    """
    tip_x = cx + 2.54  # 102.54
    y_p1 = cy - 6.35  # 553.65 — GND
    y_p2 = cy - 3.81  # 556.19 — +5V
    y_p3 = cy - 1.27  # 558.73 — UART_49MHZ_XCVR_TX
    y_p4 = cy + 1.27  # 561.27 — XCVR_RX_RAW
    y_p5 = cy + 3.81  # 563.81 — XCVR_PTT_N
    y_p6 = cy + 6.35  # 566.35 — +3V3

    uid_inst = next_uuid_b()
    uid_p1 = next_uuid_b()
    uid_p2 = next_uuid_b()
    uid_p3 = next_uuid_b()
    uid_p4 = next_uuid_b()
    uid_p5 = next_uuid_b()
    uid_p6 = next_uuid_b()

    return f"""\
  (symbol (lib_id "Conn_JST_GH_06P") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uid_inst}")
    (property "Reference" "J_XCVR" (at {cx:.2f} {cy - 8.89:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "Conn_JST_GH_06P" (at {cx:.2f} {cy + 8.89:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Connector_JST:JST_GH_SM06B-GHS-TB_1x06-1MP_P1.25mm_Horizontal" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.jst.com/wp-content/uploads/2021/01/eGH.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{uid_p1}"))
    (pin "2" (uuid "{uid_p2}"))
    (pin "3" (uuid "{uid_p3}"))
    (pin "4" (uuid "{uid_p4}"))
    (pin "5" (uuid "{uid_p5}"))
    (pin "6" (uuid "{uid_p6}"))
  )
  (symbol (lib_id "GND") (at {tip_x:.2f} {y_p1:.2f} 270)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid_b()}")
    (property "Reference" "#PWR0B501" (at {tip_x:.2f} {y_p1:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at {tip_x:.2f} {y_p1 + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid_b()}"))
  )
  (symbol (lib_id "+5V") (at {tip_x:.2f} {y_p2:.2f} 90)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid_b()}")
    (property "Reference" "#PWR0B502" (at {tip_x:.2f} {y_p2:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "+5V" (at {tip_x:.2f} {y_p2 - 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid_b()}"))
  )
  (global_label "UART_49MHZ_XCVR_TX" (shape bidirectional) (at {tip_x:.2f} {y_p3:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid_b()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {tip_x:.2f} {y_p3:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (global_label "XCVR_RX_RAW" (shape bidirectional) (at {tip_x:.2f} {y_p4:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid_b()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {tip_x:.2f} {y_p4:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (global_label "XCVR_PTT_N" (shape bidirectional) (at {tip_x:.2f} {y_p5:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid_b()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {tip_x:.2f} {y_p5:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (symbol (lib_id "+3V3") (at {tip_x:.2f} {y_p6:.2f} 90)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid_b()}")
    (property "Reference" "#PWR0B503" (at {tip_x:.2f} {y_p6:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "+3V3" (at {tip_x:.2f} {y_p6 - 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid_b()}"))
  )
  (text "J_XCVR pin 4: XCVR serial RX (SW1-1) OR SBUS signal (SW1-2)\\nSet SW1: pos 1 = XCVR-49MHz mode, pos 2 = SBUS RC mode"
    (at {cx:.2f} {cy + 12.70:.2f} 0) (effects (font (size 1.016 1.016))))"""


def inst_u_sbus_b(cx: float, cy: float) -> str:
    """Return the symbol instance block for U_SBUS_B (74LVC1G14 Schmitt inverter).

    U_SBUS_B inverts the XCVR_RX_RAW signal for SBUS use on Cape-B.
    Placed at (*cx*, *cy*) = (165, 568).

    Pin tip positions:
      A   tip at (cx − 7.62, cy)   = (157.38, 568.00)  →  global XCVR_RX_RAW (angle=180)
      Y   tip at (cx + 7.62, cy)   = (172.62, 568.00)  →  global SBUS_INV_RX  (angle=0)
      VCC tip at (cx, cy − 5.08)   = (165.00, 562.92)  →  +3V3 power (90°)
      GND tip at (cx, cy + 5.08)   = (165.00, 573.08)  →  GND power (270°)

    Args:
        cx: Component centre X in mm.
        cy: Component centre Y in mm.
    """
    a_tip_x = cx - 7.62  # 157.38
    y_tip_x = cx + 7.62  # 172.62
    vcc_tip_y = cy - 5.08  # 562.92
    gnd_tip_y = cy + 5.08  # 573.08

    uid_inst = next_uuid_b()
    uid_p1 = next_uuid_b()
    uid_p2 = next_uuid_b()
    uid_p4 = next_uuid_b()
    uid_p5 = next_uuid_b()

    return f"""\
  (symbol (lib_id "74LVC1G14") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uid_inst}")
    (property "Reference" "U_SBUS_B" (at {cx:.2f} {cy - 5.08:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "74LVC1G14GW" (at {cx:.2f} {cy + 5.08:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_TO_SOT_SMD:SOT-23-5" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.nexperia.com/products/analog-logic-ics/asynchronous-interface-logic/inverting-buffers-and-drivers/series/74LVC1G14.html" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{uid_p1}"))
    (pin "2" (uuid "{uid_p2}"))
    (pin "4" (uuid "{uid_p4}"))
    (pin "5" (uuid "{uid_p5}"))
  )
  (global_label "XCVR_RX_RAW" (shape bidirectional) (at {a_tip_x:.2f} {cy:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid_b()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {a_tip_x:.2f} {cy:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (global_label "SBUS_INV_RX" (shape bidirectional) (at {y_tip_x:.2f} {cy:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid_b()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {y_tip_x:.2f} {cy:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (symbol (lib_id "+3V3") (at {cx:.2f} {vcc_tip_y:.2f} 90)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid_b()}")
    (property "Reference" "#PWR0B504" (at {cx:.2f} {vcc_tip_y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "+3V3" (at {cx:.2f} {vcc_tip_y - 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid_b()}"))
  )
  (symbol (lib_id "GND") (at {cx:.2f} {gnd_tip_y:.2f} 270)
    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)
    (uuid "{next_uuid_b()}")
    (property "Reference" "#PWR0B505" (at {cx:.2f} {gnd_tip_y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "GND" (at {cx:.2f} {gnd_tip_y + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{next_uuid_b()}"))
  )"""


def inst_sw1(cx: float, cy: float) -> str:
    """Return the symbol instance block for SW1 (2-position DIP switch).

    SW1 is the XCVR/SBUS mode selector DIP switch, placed at
    (*cx*, *cy*) = (235, 562).

    Pin tip positions derived from lib offsets (±7.62 mm half-width):
      COM1 tip at (cx − 7.62, cy − 2.54) = (227.38, 559.46)  →  global XCVR_RX_RAW (angle=180)
      NO1  tip at (cx + 7.62, cy − 2.54) = (242.62, 559.46)  →  wire to R_XCVR_RX pin 1
      COM2 tip at (cx − 7.62, cy + 2.54) = (227.38, 564.54)  →  global SBUS_INV_RX (angle=180)
      NO2  tip at (cx + 7.62, cy + 2.54) = (242.62, 564.54)  →  wire to R_SBUS_RX pin 1

    Args:
        cx: Component centre X in mm.
        cy: Component centre Y in mm.
    """
    com1_x = cx - 7.62  # 227.38
    no1_x = cx + 7.62  # 242.62
    com2_x = cx - 7.62  # 227.38
    no2_x = cx + 7.62  # 242.62
    y_sw1 = cy - 2.54  # 559.46  (upper switch)
    y_sw2 = cy + 2.54  # 564.54  (lower switch)

    uid_inst = next_uuid_b()
    uid_p1 = next_uuid_b()
    uid_p2 = next_uuid_b()
    uid_p3 = next_uuid_b()
    uid_p4 = next_uuid_b()

    return f"""\
  (symbol (lib_id "SW_DIP_x02") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uid_inst}")
    (property "Reference" "SW1" (at {cx:.2f} {cy - 7.62:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "SW_DIP_x02" (at {cx:.2f} {cy + 7.62:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_DIP:DIP-4_W7.62mm" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{uid_p1}"))
    (pin "2" (uuid "{uid_p2}"))
    (pin "3" (uuid "{uid_p3}"))
    (pin "4" (uuid "{uid_p4}"))
  )
  (global_label "XCVR_RX_RAW" (shape bidirectional) (at {com1_x:.2f} {y_sw1:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid_b()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {com1_x:.2f} {y_sw1:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (global_label "SBUS_INV_RX" (shape bidirectional) (at {com2_x:.2f} {y_sw2:.2f} 180)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid_b()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {com2_x:.2f} {y_sw2:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))
  (text "SW1-1=XCVR, SW1-2=SBUS"
    (at {cx:.2f} {cy - 9.0:.2f} 0) (effects (font (size 1.016 1.016))))"""


def inst_r_xcvr_rx(cx: float, cy: float, sw_no1_x: float) -> str:
    """Return the symbol instance block for R_XCVR_RX (100 Ω 0402).

    R_XCVR_RX is placed at (*cx*, *cy*) = (268, 559.46).

    Pin tip positions:
      Pin 1 tip at (cx − 3.81, cy) = (264.19, 559.46)  →  wire from SW1 NO1
      Pin 2 tip at (cx + 3.81, cy) = (271.81, 559.46)  →  global UART_49MHZ_XCVR_RX (angle=0)

    Args:
        cx: Component centre X in mm.
        cy: Component centre Y in mm.
        sw_no1_x: X coordinate of SW1 NO1 tip (wire start).
    """
    left_tip_x = cx - 3.81  # 264.19
    right_tip_x = cx + 3.81  # 271.81

    uid_inst = next_uuid_b()
    uid_p1 = next_uuid_b()
    uid_p2 = next_uuid_b()

    return f"""\
  (symbol (lib_id "R_SMD") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uid_inst}")
    (property "Reference" "R_XCVR_RX" (at {cx:.2f} {cy - 1.778:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "100R" (at {cx:.2f} {cy + 1.778:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Resistor_SMD:R_0402_1005Metric" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{uid_p1}"))
    (pin "2" (uuid "{uid_p2}"))
  )
  (wire (pts (xy {sw_no1_x:.2f} {cy:.2f}) (xy {left_tip_x:.2f} {cy:.2f}))
    (stroke (width 0) (type default))
    (uuid "{next_uuid_b()}"))
  (global_label "UART_49MHZ_XCVR_RX" (shape bidirectional) (at {right_tip_x:.2f} {cy:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid_b()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {right_tip_x:.2f} {cy:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))"""


def inst_r_sbus_rx(cx: float, cy: float, sw_no2_x: float) -> str:
    """Return the symbol instance block for R_SBUS_RX (100 Ω 0402).

    R_SBUS_RX is placed at (*cx*, *cy*) = (268, 564.54).

    Pin tip positions:
      Pin 1 tip at (cx − 3.81, cy) = (264.19, 564.54)  →  wire from SW1 NO2
      Pin 2 tip at (cx + 3.81, cy) = (271.81, 564.54)  →  global UART_49MHZ_XCVR_RX (angle=0)

    Args:
        cx: Component centre X in mm.
        cy: Component centre Y in mm.
        sw_no2_x: X coordinate of SW1 NO2 tip (wire start).
    """
    left_tip_x = cx - 3.81  # 264.19
    right_tip_x = cx + 3.81  # 271.81

    uid_inst = next_uuid_b()
    uid_p1 = next_uuid_b()
    uid_p2 = next_uuid_b()

    return f"""\
  (symbol (lib_id "R_SMD") (at {cx:.2f} {cy:.2f} 0)
    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uid_inst}")
    (property "Reference" "R_SBUS_RX" (at {cx:.2f} {cy - 1.778:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "100R" (at {cx:.2f} {cy + 1.778:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Resistor_SMD:R_0402_1005Metric" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (pin "1" (uuid "{uid_p1}"))
    (pin "2" (uuid "{uid_p2}"))
  )
  (wire (pts (xy {sw_no2_x:.2f} {cy:.2f}) (xy {left_tip_x:.2f} {cy:.2f}))
    (stroke (width 0) (type default))
    (uuid "{next_uuid_b()}"))
  (global_label "UART_49MHZ_XCVR_RX" (shape bidirectional) (at {right_tip_x:.2f} {cy:.2f} 0)
    (effects (font (size 1.016 1.016)))
    (uuid "{next_uuid_b()}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {right_tip_x:.2f} {cy:.2f} 0)
      (effects (font (size 1.016 1.016)) (hide yes))))"""


# ===========================================================================
# Schematic modification helpers
# ===========================================================================


def insert_lib_symbols(text: str, new_sym_defs: str) -> str:
    """Insert *new_sym_defs* at the end of the (lib_symbols ...) block.

    Locates the lib_symbols block via find_sexp_block and inserts the new
    definitions immediately before the closing ')' of that block.

    Args:
        text:         Full schematic text.
        new_sym_defs: One or more lib_symbol definitions to insert.

    Returns:
        Modified schematic text.
    """
    try:
        ls_start, ls_end = find_sexp_block(text, "lib_symbols")
    except ValueError as exc:
        raise RuntimeError(f"lib_symbols block not found: {exc}") from exc

    # ls_end points one past the closing ')'.  The closing ')' is at ls_end-1.
    insert_pos = ls_end - 1
    text = text[:insert_pos] + "\n" + new_sym_defs + "\n" + "  " + text[insert_pos:]
    return text


def append_instances(text: str, new_instances: str) -> str:
    """Append *new_instances* before the final closing ')' of the schematic.

    The KiCad schematic file ends with a single ')' on its own line.
    We insert the new content immediately before that closing character.

    Args:
        text:          Full schematic text.
        new_instances: One or more symbol/wire/label instances to append.

    Returns:
        Modified schematic text.
    """
    last_close = text.rfind("\n)")
    if last_close == -1:
        raise RuntimeError("Could not find final closing ')' in schematic")
    text = text[:last_close] + "\n" + new_instances + "\n" + text[last_close:]
    return text


# ===========================================================================
# Main modification routines — Cape-A-1
# ===========================================================================


def modify_cape_a1(src_text: str) -> str:
    """Apply all Cape-A-1 additions to the schematic text.

    Adds the following components to CAPE-A-1 (Y ≥ 540 region):
      1.  QMC5883L magnetometer at (155, 560)
      2.  INA219AIDR battery voltage monitor at (290, 560)
      3.  J_VBAT JST GH 2-pin connector at (370, 557)
      4a. J_SBUS JST GH 3-pin connector at (100, 625)
      4b. R_SBUS 100 Ω resistor at (145, 627.54)
      4c. U_SBUS 74LVC1G14 inverter at (180, 627.54)

    Args:
        src_text: Full text of CAPE-A-1.kicad_sch.

    Returns:
        Modified text with all additions.
    """
    text = src_text

    # ------------------------------------------------------------------
    # Step 1: Insert new lib_symbol definitions into the lib_symbols block.
    # Order must not matter for KiCad; we insert them in component order.
    # ------------------------------------------------------------------
    new_lib_syms = (
        lib_sym_qmc5883l()
        + "\n"
        + lib_sym_ina219()
        + "\n"
        + lib_sym_conn_jst_gh_02p()
        + "\n"
        + lib_sym_conn_jst_gh_03p()
        + "\n"
        + lib_sym_resistor()
        + "\n"
        + lib_sym_74lvc1g14()
    )
    text = insert_lib_symbols(text, new_lib_syms)
    print(
        "  [A] Inserted 6 new lib_symbols (QMC5883L, INA219AIDR, "
        "Conn_JST_GH_02P, Conn_JST_GH_03P, R_SMD, 74LVC1G14)"
    )

    # ------------------------------------------------------------------
    # Step 2: Build component instances.
    # ------------------------------------------------------------------

    # 1. QMC5883L at (155, 560)
    mag_block = inst_qmc5883l(155.0, 560.0)
    print("  [A] Built QMC5883L instance at (155, 560)")

    # 2. INA219AIDR at (290, 560)
    bmon_block = inst_ina219(290.0, 560.0)
    print("  [A] Built INA219AIDR instance at (290, 560)")

    # 3. J_VBAT at (370, 557)
    jvbat_block = inst_j_vbat(370.0, 557.0)
    print("  [A] Built J_VBAT instance at (370, 557)")

    # 4a. J_SBUS at (100, 625)
    jsbus_block = inst_j_sbus(100.0, 625.0)
    print("  [A] Built J_SBUS instance at (100, 625)")

    # 4b. R_SBUS at (145, 627.54)
    rsbus_block = inst_r_sbus(145.0, 627.54)
    print("  [A] Built R_SBUS instance at (145, 627.54)")

    # 4c. U_SBUS at (180, 627.54); R_SBUS pin 2 tip = 145 + 3.81 = 148.81
    usbus_block = inst_u_sbus(180.0, 627.54, 148.81)
    print("  [A] Built U_SBUS instance at (180, 627.54) with wire from R_SBUS")

    # ------------------------------------------------------------------
    # Step 3: Append all instance blocks before the final ')'.
    # ------------------------------------------------------------------
    all_instances = (
        mag_block
        + "\n"
        + bmon_block
        + "\n"
        + jvbat_block
        + "\n"
        + jsbus_block
        + "\n"
        + rsbus_block
        + "\n"
        + usbus_block
    )
    text = append_instances(text, all_instances)
    print("  [A] Appended all Cape-A-1 instance blocks to schematic")

    return text


# ===========================================================================
# Main modification routines — Cape-B-1
# ===========================================================================


def modify_cape_b1(src_text: str) -> str:
    """Apply all Cape-B-1 additions to the schematic text.

    Adds the following components to CAPE-B-1 (Y ≥ 540 region):
      5.  J_XCVR  JST GH 6-pin connector at (100, 560)
      6.  U_SBUS_B 74LVC1G14 inverter at (165, 568)
      7.  SW1     2-position DIP switch at (235, 562)
      8.  R_XCVR_RX 100 Ω resistor at (268, 559.46)
      9.  R_SBUS_RX 100 Ω resistor at (268, 564.54)

    Args:
        src_text: Full text of CAPE-B-1.kicad_sch.

    Returns:
        Modified text with all additions.
    """
    text = src_text

    # ------------------------------------------------------------------
    # Step 1: Insert new lib_symbol definitions.
    # 74LVC1G14 and R_SMD are also needed here; SW_DIP_x02 and
    # Conn_JST_GH_06P are new to Cape-B.
    # ------------------------------------------------------------------
    new_lib_syms = (
        lib_sym_conn_jst_gh_06p()
        + "\n"
        + lib_sym_74lvc1g14()
        + "\n"
        + lib_sym_sw_dip_x02()
        + "\n"
        + lib_sym_resistor()
    )
    text = insert_lib_symbols(text, new_lib_syms)
    print(
        "  [B] Inserted 4 new lib_symbols (Conn_JST_GH_06P, 74LVC1G14, "
        "SW_DIP_x02, R_SMD)"
    )

    # ------------------------------------------------------------------
    # Step 2: Build component instances.
    # ------------------------------------------------------------------

    # 5. J_XCVR at (100, 560)
    jxcvr_block = inst_j_xcvr(100.0, 560.0)
    print("  [B] Built J_XCVR instance at (100, 560)")

    # 6. U_SBUS_B at (165, 568)
    usbus_b_block = inst_u_sbus_b(165.0, 568.0)
    print("  [B] Built U_SBUS_B instance at (165, 568)")

    # 7. SW1 at (235, 562)
    #    COM1 tip x = 235 - 7.62 = 227.38;  NO1 tip x = 235 + 7.62 = 242.62
    #    y_sw1 = 562 - 2.54 = 559.46;  y_sw2 = 562 + 2.54 = 564.54
    sw1_block = inst_sw1(235.0, 562.0)
    print("  [B] Built SW1 instance at (235, 562)")

    # 8. R_XCVR_RX at (268, 559.46); wire from SW1 NO1 x=242.62
    rxcvr_block = inst_r_xcvr_rx(268.0, 559.46, 242.62)
    print("  [B] Built R_XCVR_RX instance at (268, 559.46)")

    # 9. R_SBUS_RX at (268, 564.54); wire from SW1 NO2 x=242.62
    rsbus_rx_block = inst_r_sbus_rx(268.0, 564.54, 242.62)
    print("  [B] Built R_SBUS_RX instance at (268, 564.54)")

    # ------------------------------------------------------------------
    # Step 3: Append all instance blocks before the final ')'.
    # ------------------------------------------------------------------
    all_instances = (
        jxcvr_block
        + "\n"
        + usbus_b_block
        + "\n"
        + sw1_block
        + "\n"
        + rxcvr_block
        + "\n"
        + rsbus_rx_block
    )
    text = append_instances(text, all_instances)
    print("  [B] Appended all Cape-B-1 instance blocks to schematic")

    return text


# ===========================================================================
# Entry point
# ===========================================================================


def main() -> None:
    """Read both Cape-A-1 and Cape-B-1 schematics, add hardware, write back.

    Process summary:
      1. Read CAPE-A-1.kicad_sch.
      2. Apply all Cape-A-1 additions (magnetometer, INA219, VBAT connector,
         SBUS RC input circuit).
      3. Write modified CAPE-A-1.kicad_sch.
      4. Read CAPE-B-1.kicad_sch.
      5. Apply all Cape-B-1 additions (J_XCVR, U_SBUS_B, SW1, R_XCVR_RX,
         R_SBUS_RX).
      6. Write modified CAPE-B-1.kicad_sch.
    """
    # -----------------------------------------------------------------------
    # Process CAPE-A-1
    # -----------------------------------------------------------------------
    if not os.path.isfile(CAPE_A1_PATH):
        print(f"ERROR: {CAPE_A1_PATH} not found", file=sys.stderr)
        sys.exit(1)

    print(f"\nProcessing CAPE-A-1: {CAPE_A1_PATH}")
    with open(CAPE_A1_PATH, "r", encoding="utf-8") as fh:
        cape_a1_src = fh.read()
    print(f"  Read {len(cape_a1_src):,} characters from source")

    cape_a1_result = modify_cape_a1(cape_a1_src)

    with open(CAPE_A1_PATH, "w", encoding="utf-8") as fh:
        fh.write(cape_a1_result)
    line_count_a = cape_a1_result.count("\n") + 1
    print(
        f"  Wrote {line_count_a:,} lines ({len(cape_a1_result):,} chars) "
        f"back to {CAPE_A1_PATH}"
    )

    # Quick sanity checks for Cape-A-1
    checks_a = [
        ("QMC5883L", True),
        ("INA219AIDR", True),
        ("Conn_JST_GH_02P", True),
        ("Conn_JST_GH_03P", True),
        ("R_SMD", True),
        ("74LVC1G14", True),
        ("UART_SBUS_RX", True),
        ("VBAT_MON_P", True),
        ("GPIO_MAG_DRDY", True),
        ("J_VBAT", True),
        ("J_SBUS", True),
        ("R_SBUS", True),
        ("U_SBUS", True),
    ]
    print("  Sanity checks (Cape-A-1):")
    all_ok_a = True
    for token, should_exist in checks_a:
        found = token in cape_a1_result
        if found == should_exist:
            status = "OK  "
        else:
            status = "FAIL"
            all_ok_a = False
        print(f"    {status}: '{token}' {'present' if found else 'absent'}")
    if all_ok_a:
        print("  All Cape-A-1 checks PASSED.")
    else:
        print("  WARNING: One or more Cape-A-1 checks FAILED.", file=sys.stderr)

    # -----------------------------------------------------------------------
    # Process CAPE-B-1
    # -----------------------------------------------------------------------
    if not os.path.isfile(CAPE_B1_PATH):
        print(f"ERROR: {CAPE_B1_PATH} not found", file=sys.stderr)
        sys.exit(1)

    print(f"\nProcessing CAPE-B-1: {CAPE_B1_PATH}")
    with open(CAPE_B1_PATH, "r", encoding="utf-8") as fh:
        cape_b1_src = fh.read()
    print(f"  Read {len(cape_b1_src):,} characters from source")

    cape_b1_result = modify_cape_b1(cape_b1_src)

    with open(CAPE_B1_PATH, "w", encoding="utf-8") as fh:
        fh.write(cape_b1_result)
    line_count_b = cape_b1_result.count("\n") + 1
    print(
        f"  Wrote {line_count_b:,} lines ({len(cape_b1_result):,} chars) "
        f"back to {CAPE_B1_PATH}"
    )

    # Quick sanity checks for Cape-B-1
    checks_b = [
        ("Conn_JST_GH_06P", True),
        ("74LVC1G14", True),
        ("SW_DIP_x02", True),
        ("R_SMD", True),
        ("J_XCVR", True),
        ("U_SBUS_B", True),
        ("SW1", True),
        ("R_XCVR_RX", True),
        ("R_SBUS_RX", True),
        ("XCVR_RX_RAW", True),
        ("SBUS_INV_RX", True),
        ("UART_49MHZ_XCVR_TX", True),
        ("UART_49MHZ_XCVR_RX", True),
        ("XCVR_PTT_N", True),
    ]
    print("  Sanity checks (Cape-B-1):")
    all_ok_b = True
    for token, should_exist in checks_b:
        found = token in cape_b1_result
        if found == should_exist:
            status = "OK  "
        else:
            status = "FAIL"
            all_ok_b = False
        print(f"    {status}: '{token}' {'present' if found else 'absent'}")
    if all_ok_b:
        print("  All Cape-B-1 checks PASSED.")
    else:
        print("  WARNING: One or more Cape-B-1 checks FAILED.", file=sys.stderr)

    print("\nadd_sensors_sbus.py complete.")
    if not (all_ok_a and all_ok_b):
        sys.exit(1)


if __name__ == "__main__":
    main()
