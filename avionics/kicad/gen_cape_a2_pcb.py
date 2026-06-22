#!/usr/bin/env python3
"""
gen_cape_a2_pcb.py — Transform CAPE-A-1.kicad_pcb into Wash.kicad_pcb.

Wash is the EMI-hardened [REF-NIST-002 §6.2.5] Flight Control & Sensor Cape for the Serenity UAV.
This script performs the following PCB-level transformations:

    A. Updates the title block (title, rev, comment line) to reflect Wash.
    B. Replaces the ATA6561 CAN transceiver footprint (SOIC-8) with the
       ISOW1044BDFMR (SOIC-16W, 5 kV reinforced isolation + integrated DC/DC)
       [REF-IEC-001 §5.5.2] [REF-VDE-001 Cl.4.3].
    C. Replaces the MAX3485E RS-485 transceiver footprint (SOIC-8) with the
       ADM2795EBRWZ (SOIC-20W, 5 kV reinforced isolation + integrated DC/DC)
       [REF-IEC-001 §5.5.2] [REF-VDE-001 Cl.4.3].
    D. Removes both DP83825I Ethernet PHY footprints (LQFP-48).
    E. Removes the ETH1 and ETH2 JST-GH-6P connector footprints.
    F. Adds the ADIN1300BCPZ EMI-hardened PHY (LFCSP-48).
    G. Adds two ISO7642FDWRR digital isolators (SOIC-16W) for RMII isolation
       [REF-IEEE-001 Clause 22] at the same 5 kV level [REF-IEC-001 §5.5.2].
    H. Adds the Würth 749010012A SMD Ethernet transformer (8-pad SMD),
       1500 Vrms isolation per [REF-IEEE-001 Clause 38].
    I. Adds a JST GH 4-pin Ethernet harness connector (J-ETH).
    J. Adds EMI protection components: SRF2012-100Y common-mode chokes,
       PRTR5V0U2X TVS arrays, SMAJ33CA 1553 TVS, Würth 742792512 ferrite bead,
       and X2Y bridging capacitors across isolation boundaries.
    K. Adds net declarations for all new isolation-domain signals.
    L. Remaps all UUIDs to the "a2000000-0000-0000-0000-" prefix.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
         Griffing Technology LLC
License: CC BY 4.0  |  creativecommons.org/licenses/by/4.0
Date:    2026-06-04
Project: Serenity UAV — EDF Tilt-Rotor UAV

References:
    - Texas Instruments ISOW1044BDFMR datasheet (SLLSEO9, 2023)
    - Analog Devices ADM2795EBRWZ datasheet (Rev. C, 2022)
    - Analog Devices ADIN1300BCPZ datasheet (Rev. A, 2022)
    - Texas Instruments ISO7642FDWRR datasheet (SLLSE88F, 2022)
    - Würth Elektronik 749010012A datasheet (Rev. B, 2021)
    - Würth Elektronik 742792512 ferrite bead datasheet
    - Nexperia PRTR5V0U2X datasheet (Rev. 5, 2021)
    - Bourns SRF2012-100Y datasheet (2020)
    - KiCad PCB format version 20241229
    - IPC-7351 land pattern standard
    - JEDEC MS-012 SOIC package standard
    - JEDEC JESD75-5 LFCSP package standard
"""

import re
import os

# ---------------------------------------------------------------------------
# File paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(SCRIPT_DIR, "CAPE-A-1.kicad_pcb")
DST_PATH = os.path.join(SCRIPT_DIR, "Wash.kicad_pcb")

# ---------------------------------------------------------------------------
# UUID management
# ---------------------------------------------------------------------------
# All original CAPE-A-1 UUIDs are remapped to use "a2000000-0000-0000-0000-"
# prefix so Wash is unambiguously distinct in any KiCad project database.
OLD_UUID_RE = re.compile(
    r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
)
NEW_UUID_PREFIX = "a2000000-0000-0000-0000-"

_uuid_counter = 200_000_000_001


def next_uuid() -> str:
    """Return the next sequential UUID with the Wash prefix.

    Sequential UUIDs keep the PCB deterministic and reproducible.
    Counter starts at 200000000001 to sort well after remapped originals.
    """
    global _uuid_counter
    uid = f"{NEW_UUID_PREFIX}{_uuid_counter:012d}"
    _uuid_counter += 1
    return uid


# ---------------------------------------------------------------------------
# S-expression bracket parser
# ---------------------------------------------------------------------------

def find_balanced(text: str, start: int) -> int:
    """Return the index ONE PAST the closing ')' balancing the '(' at *start*.

    Correctly handles quoted strings (which may contain parentheses).

    Args:
        text:  Full PCB text.
        start: Index of the opening '(' to balance.

    Returns:
        Index immediately after the matching closing ')'.

    Raises:
        ValueError: If the text ends before the expression is closed.
    """
    depth = 0
    i = start
    in_string = False
    escape_next = False
    while i < len(text):
        ch = text[i]
        if escape_next:
            escape_next = False
        elif ch == '\\' and in_string:
            escape_next = True
        elif ch == '"':
            in_string = not in_string
        elif not in_string:
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    return i + 1
        i += 1
    raise ValueError(f"Unclosed S-expression starting at index {start}")


def find_footprint(text: str, ref: str):
    """Find the footprint block with the given Reference property value.

    Iterates through all (footprint ...) blocks and returns (start, end)
    index pair for the one whose "Reference" property matches *ref*.

    Args:
        text: Full PCB text.
        ref:  Reference designator string to search for (e.g. "CAN-TR").

    Returns:
        (start, end) tuple or (None, None) if not found.
    """
    i = 0
    pattern = re.compile(r'\(footprint\s')
    while i < len(text):
        m = pattern.search(text, i)
        if not m:
            break
        fp_start = m.start()
        fp_end = find_balanced(text, fp_start)
        block = text[fp_start:fp_end]
        # Match the exact Reference property value
        if re.search(r'\(property\s+"Reference"\s+"' + re.escape(ref) + r'"', block):
            return fp_start, fp_end
        i = fp_end
    return None, None


def remove_footprint(text: str, ref: str) -> str:
    """Remove the footprint block with the given Reference from *text*.

    Args:
        text: Full PCB text.
        ref:  Reference designator to remove.

    Returns:
        Modified text with the footprint block removed.
    """
    start, end = find_footprint(text, ref)
    if start is None:
        print(f"  WARNING: footprint '{ref}' not found — skipping removal")
        return text
    # Remove the block plus any leading newline/whitespace on its line
    prefix = text[:start]
    # Step back over whitespace on the same line to remove clean indentation
    while prefix and prefix[-1] in ('\t', ' '):
        prefix = prefix[:-1]
    if prefix.endswith('\n'):
        prefix = prefix[:-1]
    result = prefix + text[end:]
    print(f"  Removed footprint '{ref}'")
    return result


def replace_footprint(text: str, ref: str, new_block: str) -> str:
    """Replace the footprint block for *ref* with *new_block*.

    Args:
        text:      Full PCB text.
        ref:       Reference designator to replace.
        new_block: Complete new footprint block string.

    Returns:
        Modified text with the footprint block replaced.
    """
    start, end = find_footprint(text, ref)
    if start is None:
        print(f"  WARNING: footprint '{ref}' not found — skipping replacement")
        return text
    result = text[:start] + new_block + text[end:]
    print(f"  Replaced footprint '{ref}'")
    return result


# ---------------------------------------------------------------------------
# Footprint block generators — SOIC-16W (7.5 mm × 10.3 mm, 1.27 mm pitch)
# ---------------------------------------------------------------------------
# Pad geometry (IPC-7351 land pattern for SOIC-16W):
#   pad size: 1.95 mm × 0.60 mm
#   pad X centres: ±5.10 mm
#   pad Y centres (8 pins, 1.27 mm pitch): ±4.445, ±3.175, ±1.905, ±0.635
#   left pins 1-8 top→bottom, right pins 9-16 bottom→top
SOIC16W_Y = [-4.445, -3.175, -1.905, -0.635, 0.635, 1.905, 3.175, 4.445]


def _pad(num: str, x: float, y: float, net_num: int, net_name: str,
         size_x: float = 1.95, size_y: float = 0.60,
         angle: float = 0.0) -> str:
    """Generate a single SMD roundrect pad entry."""
    at_str = f"{x} {y}" if angle == 0.0 else f"{x} {y} {angle}"
    net_str = f"\n\t\t\t(net {net_num} \"{net_name}\")" if net_num > 0 else ""
    return (
        f"\t\t(pad \"{num}\" smd roundrect\n"
        f"\t\t\t(at {at_str})\n"
        f"\t\t\t(size {size_x} {size_y})\n"
        f"\t\t\t(layers \"F.Cu\" \"F.Mask\" \"F.Paste\")\n"
        f"\t\t\t(roundrect_rratio 0.25){net_str}\n"
        f"\t\t\t(uuid \"{next_uuid()}\")\n"
        f"\t\t)\n"
    )


def _pad_rect(num: str, x: float, y: float, net_num: int, net_name: str,
              size_x: float = 0.80, size_y: float = 1.60) -> str:
    """Generate a single SMD rect pad entry (for JST connectors)."""
    net_str = f"\n\t\t\t(net {net_num} \"{net_name}\")" if net_num > 0 else ""
    return (
        f"\t\t(pad \"{num}\" smd rect\n"
        f"\t\t\t(at {x} {y})\n"
        f"\t\t\t(size {size_x} {size_y})\n"
        f"\t\t\t(layers \"F.Cu\" \"F.Mask\" \"F.Paste\")\n"
        f"\t\t\t(uuid \"{next_uuid()}\")\n"
        f"\t\t\t{net_str}\n"
        f"\t\t)\n"
    ) if net_num == 0 else (
        f"\t\t(pad \"{num}\" smd rect\n"
        f"\t\t\t(at {x} {y})\n"
        f"\t\t\t(size {size_x} {size_y})\n"
        f"\t\t\t(layers \"F.Cu\" \"F.Mask\" \"F.Paste\")\n"
        f"\t\t\t(net {net_num} \"{net_name}\")\n"
        f"\t\t\t(uuid \"{next_uuid()}\")\n"
        f"\t\t)\n"
    )


def _prop(name: str, value: str, at_x: float, at_y: float,
          layer: str = "F.SilkS", size: float = 1.0,
          hide: bool = False) -> str:
    """Generate a (property ...) entry."""
    hide_str = "\n\t\t\t(hide yes)" if hide else ""
    return (
        f"\t\t(property \"{name}\" \"{value}\"\n"
        f"\t\t\t(at {at_x} {at_y} 0)\n"
        f"\t\t\t(layer \"{layer}\"){hide_str}\n"
        f"\t\t\t(uuid \"{next_uuid()}\")\n"
        f"\t\t\t(effects (font (size {size} {size}) (thickness 0.15)))\n"
        f"\t\t)\n"
    )


def _soic_silk_lines(half_w: float, half_h: float,
                     corner_indent: float = 1.0) -> str:
    """Generate F.SilkS corner lines for an SOIC package body outline."""
    lines = []
    # Top-left and top-right (notch for pin-1 marker)
    lines.append(
        f"\t\t(fp_line (start -{half_w} -{half_h - corner_indent}) "
        f"(end -{half_w} -{half_h}) (stroke (width 0.12) (type solid)) "
        f"(layer \"F.SilkS\") (uuid \"{next_uuid()}\"))\n"
    )
    lines.append(
        f"\t\t(fp_line (start -{half_w} -{half_h}) "
        f"(end {half_w} -{half_h}) (stroke (width 0.12) (type solid)) "
        f"(layer \"F.SilkS\") (uuid \"{next_uuid()}\"))\n"
    )
    lines.append(
        f"\t\t(fp_line (start {half_w} -{half_h}) "
        f"(end {half_w} {half_h}) (stroke (width 0.12) (type solid)) "
        f"(layer \"F.SilkS\") (uuid \"{next_uuid()}\"))\n"
    )
    lines.append(
        f"\t\t(fp_line (start {half_w} {half_h}) "
        f"(end -{half_w} {half_h}) (stroke (width 0.12) (type solid)) "
        f"(layer \"F.SilkS\") (uuid \"{next_uuid()}\"))\n"
    )
    lines.append(
        f"\t\t(fp_line (start -{half_w} {half_h}) "
        f"(end -{half_w} {half_h - corner_indent}) "
        f"(stroke (width 0.12) (type solid)) "
        f"(layer \"F.SilkS\") (uuid \"{next_uuid()}\"))\n"
    )
    return "".join(lines)


def _soic_courtyard(cx_outer: float, cy_outer: float) -> str:
    """Generate F.CrtYd rectangle lines for an SOIC package."""
    # Courtyard: rectangular box
    pts = [
        (f"-{cx_outer}", f"-{cy_outer}"),
        (f" {cx_outer}", f"-{cy_outer}"),
        (f" {cx_outer}", f" {cy_outer}"),
        (f"-{cx_outer}", f" {cy_outer}"),
    ]
    lines = []
    for i in range(4):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % 4]
        lines.append(
            f"\t\t(fp_line (start {x0} {y0}) (end {x1} {y1}) "
            f"(stroke (width 0.05) (type solid)) "
            f"(layer \"F.CrtYd\") (uuid \"{next_uuid()}\"))\n"
        )
    return "".join(lines)


def make_soic16w(ref: str, value: str, x: float, y: float,
                 pin_nets: dict) -> str:
    """Generate a complete SOIC-16W footprint block.

    Package: 7.5 × 10.3 mm, 1.27 mm pitch (JEDEC MS-012W).
    Pins 1-8 on left side (top → bottom), 9-16 on right (bottom → top).

    Args:
        ref:      Reference designator string.
        value:    Component value / part number.
        x, y:     PCB placement coordinates in mm.
        pin_nets: Dict {pin_num: (net_num, net_name)} for connected pins.
                  Pins not in dict are treated as NC (net 0).

    Returns:
        Complete KiCad PCB footprint block string.
    """
    pads_str = ""
    # Left side: pins 1-8 top to bottom at X = -5.1
    for i, py in enumerate(SOIC16W_Y):
        pin = i + 1
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _pad(str(pin), -5.1, py, nn, nm)
    # Right side: pins 9-16 bottom to top at X = +5.1
    for i, py in enumerate(reversed(SOIC16W_Y)):
        pin = 9 + i
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _pad(str(pin), 5.1, py, nn, nm)

    silk = _soic_silk_lines(half_w=2.0, half_h=5.2)
    cyd = _soic_courtyard(cx_outer=6.4, cy_outer=5.55)

    return (
        f"\t(footprint \"SOIC-16W_7.5x10.3mm_P1.27mm\"\n"
        f"\t\t(layer \"F.Cu\")\n"
        f"\t\t(uuid \"{next_uuid()}\")\n"
        f"\t\t(at {x} {y})\n"
        f"\t\t(descr \"SOIC-16W, 7.5x10.3mm, 1.27mm pitch — {value}\")\n"
        f"\t\t(tags \"SOIC SO SOIC16W isolated\")\n"
        f"{_prop('Reference', ref, 0, -6.0)}"
        f"{_prop('Value', value, 0, 6.0, layer='F.Fab')}"
        f"{_prop('Datasheet', '', 0, 0, layer='F.Fab', hide=True)}"
        f"\t\t(attr smd)\n"
        f"{silk}"
        f"{cyd}"
        f"{pads_str}"
        f"\t\t(embedded_fonts no)\n"
        f"\t)\n"
    )


# ---------------------------------------------------------------------------
# Footprint generator — SOIC-20W (7.5 mm × 12.8 mm, 1.27 mm pitch)
# ---------------------------------------------------------------------------
# Pad X centres: ±5.10 mm
# Pad Y centres (10 pins, 1.27 mm pitch): ±5.715, ±4.445, ±3.175, ±1.905, ±0.635
SOIC20W_Y = [-5.715, -4.445, -3.175, -1.905, -0.635, 0.635, 1.905, 3.175, 4.445, 5.715]


def make_soic20w(ref: str, value: str, x: float, y: float,
                 pin_nets: dict) -> str:
    """Generate a complete SOIC-20W footprint block.

    Package: 7.5 × 12.8 mm, 1.27 mm pitch (JEDEC MS-013).
    Pins 1-10 on left side (top → bottom), 11-20 on right (bottom → top).

    Args:
        ref:      Reference designator string.
        value:    Component value / part number.
        x, y:     PCB placement coordinates in mm.
        pin_nets: Dict {pin_num: (net_num, net_name)} for connected pins.

    Returns:
        Complete KiCad PCB footprint block string.
    """
    pads_str = ""
    for i, py in enumerate(SOIC20W_Y):
        pin = i + 1
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _pad(str(pin), -5.1, py, nn, nm)
    for i, py in enumerate(reversed(SOIC20W_Y)):
        pin = 11 + i
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _pad(str(pin), 5.1, py, nn, nm)

    silk = _soic_silk_lines(half_w=2.0, half_h=6.5)
    cyd = _soic_courtyard(cx_outer=6.4, cy_outer=6.85)

    return (
        f"\t(footprint \"SOIC-20W_7.5x12.8mm_P1.27mm\"\n"
        f"\t\t(layer \"F.Cu\")\n"
        f"\t\t(uuid \"{next_uuid()}\")\n"
        f"\t\t(at {x} {y})\n"
        f"\t\t(descr \"SOIC-20W, 7.5x12.8mm, 1.27mm pitch — {value}\")\n"
        f"\t\t(tags \"SOIC SO SOIC20W isolated\")\n"
        f"{_prop('Reference', ref, 0, -7.2)}"
        f"{_prop('Value', value, 0, 7.2, layer='F.Fab')}"
        f"{_prop('Datasheet', '', 0, 0, layer='F.Fab', hide=True)}"
        f"\t\t(attr smd)\n"
        f"{silk}"
        f"{cyd}"
        f"{pads_str}"
        f"\t\t(embedded_fonts no)\n"
        f"\t)\n"
    )


# ---------------------------------------------------------------------------
# Footprint generator — LFCSP-48 (7×7 mm, 0.5 mm pitch, 12 pins/side)
# ---------------------------------------------------------------------------
# Package: ADI LFCSP-48 (CP-48-3), body 7×7mm, EP 5.65×5.65mm
# Pin 1 at bottom-left, CCW: 1-12 bottom, 13-24 left, 25-36 top, 37-48 right
# Pad size: 0.65 × 0.30 mm
# Pad centres from body centre:
#   Bottom (pins 1-12): Y=+4.0, X from -2.75 to +2.75 (0.5mm steps)
#   Left   (pins 13-24): X=-4.0, Y from +2.75 to -2.75 (decreasing)
#   Top    (pins 25-36): Y=-4.0, X from +2.75 to -2.75 (decreasing)
#   Right  (pins 37-48): X=+4.0, Y from -2.75 to +2.75 (increasing)
#   EP     (pin 49):     centre, 5.65×5.65mm

_LFCSP48_OFFSETS = [i * 0.5 - 2.75 for i in range(12)]  # -2.75 to +2.75


def _lfcsp_pad(num: str, x: float, y: float, net_num: int,
               net_name: str, w: float = 0.30, h: float = 0.65,
               angle: float = 0.0) -> str:
    """Generate a single QFN/LFCSP pad."""
    at_str = f"{x:.4f} {y:.4f}" if angle == 0.0 else f"{x:.4f} {y:.4f} {angle}"
    net_str = f"\n\t\t\t(net {net_num} \"{net_name}\")" if net_num > 0 else ""
    return (
        f"\t\t(pad \"{num}\" smd roundrect\n"
        f"\t\t\t(at {at_str})\n"
        f"\t\t\t(size {w} {h})\n"
        f"\t\t\t(layers \"F.Cu\" \"F.Mask\" \"F.Paste\")\n"
        f"\t\t\t(roundrect_rratio 0.25){net_str}\n"
        f"\t\t\t(uuid \"{next_uuid()}\")\n"
        f"\t\t)\n"
    )


def make_lfcsp48(ref: str, value: str, x: float, y: float,
                 pin_nets: dict) -> str:
    """Generate a LFCSP-48 (7×7 mm, 0.5 mm pitch) footprint block.

    Pin numbering follows ADI LFCSP convention: pin 1 at bottom-left,
    CCW (bottom→left→top→right), EP is pad 49.

    Args:
        ref:      Reference designator.
        value:    Component value / part number.
        x, y:     PCB placement coordinates in mm.
        pin_nets: Dict {pin_num: (net_num, net_name)}.

    Returns:
        Complete KiCad PCB footprint block string.
    """
    pads_str = ""
    # Bottom side: pins 1-12, Y=+4.0, X left→right
    for i, ox in enumerate(_LFCSP48_OFFSETS):
        pin = i + 1
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _lfcsp_pad(str(pin), ox, 4.0, nn, nm,
                               w=0.30, h=0.65)
    # Left side: pins 13-24, X=-4.0, Y top→bottom (decreasing from +2.75)
    for i, oy in enumerate(reversed(_LFCSP48_OFFSETS)):
        pin = 13 + i
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _lfcsp_pad(str(pin), -4.0, oy, nn, nm,
                               w=0.65, h=0.30)
    # Top side: pins 25-36, Y=-4.0, X right→left (decreasing from +2.75)
    for i, ox in enumerate(reversed(_LFCSP48_OFFSETS)):
        pin = 25 + i
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _lfcsp_pad(str(pin), ox, -4.0, nn, nm,
                               w=0.30, h=0.65)
    # Right side: pins 37-48, X=+4.0, Y bottom→top (increasing from -2.75)
    for i, oy in enumerate(_LFCSP48_OFFSETS):
        pin = 37 + i
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _lfcsp_pad(str(pin), 4.0, oy, nn, nm,
                               w=0.65, h=0.30)
    # Exposed pad (EP): pin 49, GND, 5.65×5.65 mm
    nn_gnd, nm_gnd = pin_nets.get(49, (51, "GND"))
    pads_str += (
        f"\t\t(pad \"49\" thru_hole roundrect\n"
        f"\t\t\t(at 0 0)\n"
        f"\t\t\t(size 5.65 5.65)\n"
        f"\t\t\t(drill oval 0.5 0.5)\n"
        f"\t\t\t(layers \"*.Cu\" \"*.Mask\")\n"
        f"\t\t\t(roundrect_rratio 0.0)\n"
        f"\t\t\t(net {nn_gnd} \"{nm_gnd}\")\n"
        f"\t\t\t(uuid \"{next_uuid()}\")\n"
        f"\t\t)\n"
    )
    # Body outline on Fab, 3.5mm half-width
    cyd_lines = _soic_courtyard(cx_outer=4.5, cy_outer=4.5)
    fab_lines = (
        f"\t\t(fp_rect (start -3.5 -3.5) (end 3.5 3.5) "
        f"(stroke (width 0.1) (type solid)) (fill no) "
        f"(layer \"F.Fab\") (uuid \"{next_uuid()}\"))\n"
    )
    return (
        f"\t(footprint \"QFN-48-1EP_7x7mm_P0.5mm_EP5.65x5.65mm\"\n"
        f"\t\t(layer \"F.Cu\")\n"
        f"\t\t(uuid \"{next_uuid()}\")\n"
        f"\t\t(at {x} {y})\n"
        f"\t\t(descr \"LFCSP-48 (CP-48-3), 7x7mm, 0.5mm pitch — {value}\")\n"
        f"\t\t(tags \"QFN LFCSP 48 7x7 EMI PHY\")\n"
        f"{_prop('Reference', ref, 0, -5.0)}"
        f"{_prop('Value', value, 0, 5.0, layer='F.Fab')}"
        f"{_prop('Datasheet', '', 0, 0, layer='F.Fab', hide=True)}"
        f"\t\t(attr smd)\n"
        f"{fab_lines}"
        f"{cyd_lines}"
        f"{pads_str}"
        f"\t\t(embedded_fonts no)\n"
        f"\t)\n"
    )


# ---------------------------------------------------------------------------
# Footprint generator — SMD Ethernet Transformer (Würth 749010012A)
# ---------------------------------------------------------------------------
# Package: 8-pin SMD, 4 pins/side (MDI-side and line-side separated)
# Pad size: 1.20 × 0.60 mm, pad X: ±2.5mm, pad Y: ±1.5, ±0.5
# Pins 1-4 left (IC/MDI side), pins 5-8 right (line side)

ETH_XFMR_Y = [-1.5, -0.5, 0.5, 1.5]


def make_eth_xfmr(ref: str, x: float, y: float, pin_nets: dict) -> str:
    """Generate SMD Ethernet transformer footprint (Würth 749010012A).

    8-pad SMD: pins 1-4 on left (PHY MDI side), pins 5-8 on right
    (line side to external connector).

    Args:
        ref:      Reference designator.
        x, y:     PCB placement coordinates in mm.
        pin_nets: Dict {pin_num: (net_num, net_name)}.

    Returns:
        Complete KiCad PCB footprint block string.
    """
    pads_str = ""
    # Left: pins 1-4 (PHY side MDI signals)
    for i, py in enumerate(ETH_XFMR_Y):
        pin = i + 1
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _pad(str(pin), -2.5, py, nn, nm,
                         size_x=1.20, size_y=0.60)
    # Right: pins 5-8 (line side)
    for i, py in enumerate(ETH_XFMR_Y):
        pin = i + 5
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _pad(str(pin), 2.5, py, nn, nm,
                         size_x=1.20, size_y=0.60)

    cyd = _soic_courtyard(cx_outer=3.8, cy_outer=2.3)
    return (
        f"\t(footprint \"ETH_XFMR_8P_5x3.5mm\"\n"
        f"\t\t(layer \"F.Cu\")\n"
        f"\t\t(uuid \"{next_uuid()}\")\n"
        f"\t\t(at {x} {y})\n"
        f"\t\t(descr \"SMD Ethernet transformer 8-pad — Würth 749010012A\")\n"
        f"\t\t(tags \"transformer Ethernet SMD magnetics 100BASE-TX\")\n"
        f"{_prop('Reference', ref, 0, -2.7)}"
        f"{_prop('Value', '749010012A', 0, 2.7, layer='F.Fab')}"
        f"{_prop('Datasheet', '', 0, 0, layer='F.Fab', hide=True)}"
        f"\t\t(attr smd)\n"
        f"{cyd}"
        f"{pads_str}"
        f"\t\t(embedded_fonts no)\n"
        f"\t)\n"
    )


# ---------------------------------------------------------------------------
# Footprint generator — JST GH 4-pin (SM04B-GHS-TB)
# ---------------------------------------------------------------------------
# Pad layout: 4 pads in a row, 1.25mm pitch, centred at origin
# Pad size: 0.80 × 1.60 mm, type: smd rect

def make_jst_gh4p(ref: str, value: str, x: float, y: float,
                  pin_nets: dict) -> str:
    """Generate JST GH 4-pin connector footprint (SM04B-GHS-TB).

    Args:
        ref:      Reference designator.
        value:    Component value.
        x, y:     PCB placement coordinates in mm.
        pin_nets: Dict {pin_num: (net_num, net_name)}.

    Returns:
        Complete KiCad PCB footprint block string.
    """
    pad_xs = [-1.875, -0.625, 0.625, 1.875]
    pads_str = ""
    for i, px in enumerate(pad_xs):
        pin = i + 1
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _pad_rect(str(pin), px, 0.0, nn, nm,
                               size_x=0.80, size_y=1.60)

    cyd = _soic_courtyard(cx_outer=2.8, cy_outer=1.5)
    return (
        f"\t(footprint \"JST_GH_4P\"\n"
        f"\t\t(layer \"F.Cu\")\n"
        f"\t\t(uuid \"{next_uuid()}\")\n"
        f"\t\t(at {x} {y})\n"
        f"\t\t(descr \"JST GH 4-pin SMD connector, 1.25mm pitch — SM04B-GHS-TB\")\n"
        f"\t\t(tags \"JST GH 4P Ethernet harness\")\n"
        f"{_prop('Reference', ref, 0, -1.8, size=0.8)}"
        f"{_prop('Value', value, 0, 1.8, layer='F.Fab', size=0.8)}"
        f"{_prop('Datasheet', '', 0, 0, layer='F.Fab', hide=True)}"
        f"\t\t(attr smd)\n"
        f"{cyd}"
        f"{pads_str}"
        f"\t\t(embedded_fonts no)\n"
        f"\t)\n"
    )


# ---------------------------------------------------------------------------
# Footprint generator — SRF2012-100Y Common-Mode Choke (4-terminal 2012)
# ---------------------------------------------------------------------------
# Package: Bourns SRF2012, 2.0×1.2mm body, 4 terminals (A1/A2 left, B1/B2 right)
# Pad centres: X=±1.65mm, Y=±0.35mm; pad size: 0.90×0.50mm

def make_srf2012(ref: str, x: float, y: float, pin_nets: dict) -> str:
    """Generate SRF2012-100Y 4-terminal common-mode choke footprint.

    Terminals: A1 (pin 1, left-top), A2 (pin 2, left-bottom),
               B1 (pin 3, right-top), B2 (pin 4, right-bottom).

    Args:
        ref:      Reference designator.
        x, y:     PCB placement coordinates in mm.
        pin_nets: Dict {pin_num: (net_num, net_name)}.

    Returns:
        Complete KiCad PCB footprint block string.
    """
    layout = [(-1.65, -0.35, 1), (-1.65, 0.35, 2),
              (1.65, -0.35, 3), (1.65, 0.35, 4)]
    pads_str = ""
    for px, py, pin in layout:
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _pad(str(pin), px, py, nn, nm,
                         size_x=0.90, size_y=0.50)

    cyd = _soic_courtyard(cx_outer=2.4, cy_outer=1.0)
    return (
        f"\t(footprint \"Bourns_SRF2012_4T\"\n"
        f"\t\t(layer \"F.Cu\")\n"
        f"\t\t(uuid \"{next_uuid()}\")\n"
        f"\t\t(at {x} {y})\n"
        f"\t\t(descr \"Bourns SRF2012-100Y common-mode choke, 4-terminal 2012\")\n"
        f"\t\t(tags \"CMC common-mode choke EMI filter 2012\")\n"
        f"{_prop('Reference', ref, 0, -1.2, size=0.6)}"
        f"{_prop('Value', 'SRF2012-100Y', 0, 1.2, layer='F.Fab', size=0.6)}"
        f"\t\t(attr smd)\n"
        f"{cyd}"
        f"{pads_str}"
        f"\t\t(embedded_fonts no)\n"
        f"\t)\n"
    )


# ---------------------------------------------------------------------------
# Footprint generator — PRTR5V0U2X (SOT-363, 6-lead TVS array)
# ---------------------------------------------------------------------------
# Package: SOT-363 (SC-88), 6 leads, 3 per side, 0.65mm pitch
# Pad size: 0.90×0.55mm; row spacing: 2.60mm; Y offsets: ±0.65, 0

def make_prtr5v0u2x(ref: str, x: float, y: float, pin_nets: dict) -> str:
    """Generate PRTR5V0U2X SOT-363 TVS diode array footprint.

    Pin numbering: 1 (top-left), 2 (middle-left), 3 (bottom-left),
                   4 (bottom-right), 5 (middle-right), 6 (top-right).

    Args:
        ref:      Reference designator.
        x, y:     PCB placement coordinates in mm.
        pin_nets: Dict {pin_num: (net_num, net_name)}.

    Returns:
        Complete KiCad PCB footprint block string.
    """
    # Left side: 1,2,3 top to bottom; right side: 4,5,6 bottom to top
    layout = [
        (-1.30, -0.65, 1), (-1.30, 0.0, 2), (-1.30, 0.65, 3),
        (1.30, 0.65, 4),   (1.30, 0.0, 5),  (1.30, -0.65, 6),
    ]
    pads_str = ""
    for px, py, pin in layout:
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _pad(str(pin), px, py, nn, nm,
                         size_x=0.90, size_y=0.55)

    cyd = _soic_courtyard(cx_outer=2.1, cy_outer=1.3)
    return (
        f"\t(footprint \"SOT-363_SC-88\"\n"
        f"\t\t(layer \"F.Cu\")\n"
        f"\t\t(uuid \"{next_uuid()}\")\n"
        f"\t\t(at {x} {y})\n"
        f"\t\t(descr \"Nexperia PRTR5V0U2X — SOT-363 dual TVS protection array\")\n"
        f"\t\t(tags \"TVS ESD SOT363 SC88 EMI protection\")\n"
        f"{_prop('Reference', ref, 0, -1.5, size=0.6)}"
        f"{_prop('Value', 'PRTR5V0U2X', 0, 1.5, layer='F.Fab', size=0.6)}"
        f"\t\t(attr smd)\n"
        f"{cyd}"
        f"{pads_str}"
        f"\t\t(embedded_fonts no)\n"
        f"\t)\n"
    )


# ---------------------------------------------------------------------------
# Footprint generator — SMAJ33CA (DO-214AC / SMA TVS diode)
# ---------------------------------------------------------------------------
# Package: DO-214AC (SMA), body 4.4×2.7mm, lead pitch ~5.4mm
# Pad size: 2.0×2.7mm, centres at X=±2.7mm

def make_smaj33ca(ref: str, x: float, y: float, pin_nets: dict) -> str:
    """Generate SMAJ33CA DO-214AC (SMA) TVS diode footprint.

    Pins: 1 = anode (A), 2 = cathode (K).

    Args:
        ref:      Reference designator.
        x, y:     PCB placement coordinates in mm.
        pin_nets: Dict {1: (net, name), 2: (net, name)}.

    Returns:
        Complete KiCad PCB footprint block string.
    """
    pads_str = ""
    nn1, nm1 = pin_nets.get(1, (0, ""))
    nn2, nm2 = pin_nets.get(2, (0, ""))
    pads_str += _pad("1", -2.7, 0.0, nn1, nm1, size_x=2.0, size_y=2.7)
    pads_str += _pad("2", 2.7, 0.0, nn2, nm2, size_x=2.0, size_y=2.7)

    cyd = _soic_courtyard(cx_outer=4.0, cy_outer=2.0)
    return (
        f"\t(footprint \"DO-214AC_SMA\"\n"
        f"\t\t(layer \"F.Cu\")\n"
        f"\t\t(uuid \"{next_uuid()}\")\n"
        f"\t\t(at {x} {y})\n"
        f"\t\t(descr \"SMAJ33CA — DO-214AC (SMA) 33V TVS, bidirectional\")\n"
        f"\t\t(tags \"TVS SMA DO-214AC 33V 1553 EMI\")\n"
        f"{_prop('Reference', ref, 0, -2.2, size=0.7)}"
        f"{_prop('Value', 'SMAJ33CA', 0, 2.2, layer='F.Fab', size=0.7)}"
        f"\t\t(attr smd)\n"
        f"{cyd}"
        f"{pads_str}"
        f"\t\t(embedded_fonts no)\n"
        f"\t)\n"
    )


# ---------------------------------------------------------------------------
# Footprint generator — 0805 SMD (ferrite bead, bypass caps)
# ---------------------------------------------------------------------------
# Pad size: 1.55×1.40mm, centres at X=±1.15mm (IPC-7351 0805 land pattern)

def make_0805(ref: str, value: str, x: float, y: float,
              pin_nets: dict) -> str:
    """Generate standard 0805 SMD two-pad footprint.

    Pins: 1 = pad A (left), 2 = pad B (right).

    Args:
        ref:      Reference designator.
        value:    Component value / part number.
        x, y:     PCB placement coordinates in mm.
        pin_nets: Dict {1: (net, name), 2: (net, name)}.

    Returns:
        Complete KiCad PCB footprint block string.
    """
    nn1, nm1 = pin_nets.get(1, (0, ""))
    nn2, nm2 = pin_nets.get(2, (0, ""))
    pads_str = _pad("1", -1.15, 0.0, nn1, nm1, size_x=1.55, size_y=1.40)
    pads_str += _pad("2", 1.15, 0.0, nn2, nm2, size_x=1.55, size_y=1.40)

    cyd = _soic_courtyard(cx_outer=2.2, cy_outer=1.1)
    return (
        f"\t(footprint \"C_0805_2012Metric\"\n"
        f"\t\t(layer \"F.Cu\")\n"
        f"\t\t(uuid \"{next_uuid()}\")\n"
        f"\t\t(at {x} {y})\n"
        f"\t\t(descr \"0805 SMD — {value}\")\n"
        f"\t\t(tags \"0805 SMD passive\")\n"
        f"{_prop('Reference', ref, 0, -1.5, size=0.6)}"
        f"{_prop('Value', value, 0, 1.5, layer='F.Fab', size=0.6)}"
        f"\t\t(attr smd)\n"
        f"{cyd}"
        f"{pads_str}"
        f"\t\t(embedded_fonts no)\n"
        f"\t)\n"
    )


# ---------------------------------------------------------------------------
# Footprint generator — X2Y capacitor (4-terminal 0402 SMD)
# ---------------------------------------------------------------------------
# X2Y caps: 2 signal pads (ends) + 2 GND pads (sides)
# Pad size: signal 0.60×0.55mm, GND 0.55×0.40mm
# Centres: signal X=±0.8mm Y=0; GND X=0 Y=±0.4mm

def make_x2y_cap(ref: str, x: float, y: float, pin_nets: dict) -> str:
    """Generate X2Y bridging capacitor footprint (4-terminal 0402-style).

    Pins: 1/2 = signal pins (left/right ends),
          3/4 = GND1/GND2 (top/bottom sides, bridging isolation planes).

    Args:
        ref:      Reference designator.
        x, y:     PCB placement coordinates in mm.
        pin_nets: Dict {pin_num: (net_num, net_name)}.

    Returns:
        Complete KiCad PCB footprint block string.
    """
    nn1, nm1 = pin_nets.get(1, (0, ""))
    nn2, nm2 = pin_nets.get(2, (0, ""))
    nn3, nm3 = pin_nets.get(3, (51, "GND"))
    nn4, nm4 = pin_nets.get(4, (0, ""))

    pads_str = _pad("1", -0.8, 0.0, nn1, nm1, size_x=0.60, size_y=0.55)
    pads_str += _pad("2", 0.8, 0.0, nn2, nm2, size_x=0.60, size_y=0.55)
    pads_str += _pad("3", 0.0, -0.4, nn3, nm3, size_x=0.55, size_y=0.40)
    pads_str += _pad("4", 0.0, 0.4, nn4, nm4, size_x=0.55, size_y=0.40)

    cyd = _soic_courtyard(cx_outer=1.4, cy_outer=0.8)
    return (
        f"\t(footprint \"X2Y_Cap_4T_0402\"\n"
        f"\t\t(layer \"F.Cu\")\n"
        f"\t\t(uuid \"{next_uuid()}\")\n"
        f"\t\t(at {x} {y})\n"
        f"\t\t(descr \"X2Y bridging capacitor 4.7nF — signal-to-GND isolation bridge\")\n"
        f"\t\t(tags \"X2Y cap 4-terminal isolation bridge EMI\")\n"
        f"{_prop('Reference', ref, 0, -1.1, size=0.5)}"
        f"{_prop('Value', '4.7nF X2Y', 0, 1.1, layer='F.Fab', size=0.5)}"
        f"\t\t(attr smd)\n"
        f"{cyd}"
        f"{pads_str}"
        f"\t\t(embedded_fonts no)\n"
        f"\t)\n"
    )


# ---------------------------------------------------------------------------
# Net list helpers
# ---------------------------------------------------------------------------

def insert_new_nets(text: str, new_nets: dict) -> str:
    """Insert new net declarations after the last existing (net N ...) line.

    Args:
        text:     Full PCB text.
        new_nets: Ordered dict {net_num: net_name} of nets to add.

    Returns:
        Modified text with new net declarations inserted.
    """
    # Find the position of the last net declaration before the first footprint
    last_net_m = None
    for m in re.finditer(r'^\t\(net \d+ ".*?"\)\n', text, re.MULTILINE):
        last_net_m = m
    if last_net_m is None:
        print("  WARNING: no existing net declarations found")
        return text
    insert_pos = last_net_m.end()
    new_lines = ""
    for num, name in sorted(new_nets.items()):
        new_lines += f'\t(net {num} "{name}")\n'
    return text[:insert_pos] + new_lines + text[insert_pos:]


# ---------------------------------------------------------------------------
# UUID remapping
# ---------------------------------------------------------------------------

def remap_uuids(text: str) -> str:
    """Remap all original UUIDs to the Wash UUID namespace.

    Replaces every UUID in *text* that does NOT already start with the
    Wash prefix with a fresh sequential UUID.

    Args:
        text: Full PCB text.

    Returns:
        Text with all UUIDs remapped.
    """
    seen: dict[str, str] = {}

    def _replace(m: re.Match) -> str:
        orig = m.group(0)
        # Keep already-prefixed UUIDs
        if orig.startswith(NEW_UUID_PREFIX.replace("-0000-0000-0000-", "")):
            return orig
        if orig not in seen:
            seen[orig] = next_uuid()
        return seen[orig]

    return OLD_UUID_RE.sub(_replace, text)


# ---------------------------------------------------------------------------
# Net assignments for replaced / new components
# ---------------------------------------------------------------------------
# CAPE-A-1 existing net numbers:
#   9=+3V3  15=CAN_STB  41=RS485_RX  44=MCAN0_RX  51=GND  52=MCAN0_TX
#   54=+5V  63=RS485_TX  65=RS485_DE  74=CAN_L  78=RS485_B
#   3=MDC  14=MDIO  19=RMII0_REF_CLK  2=RMII0_TXD0  23=RMII0_TXD1
#   36=RMII0_TX_EN  56=RMII0_RXD0  20=RMII0_RXD1  10=RMII0_CRS_DV
#   55=RMII0_RX_ER  22=PHY1_RSTN  53=PHY1_INTRN
#
# New Wash nets starting at 83:
NEW_NETS_A2 = {
    83: "GND2_CAN",
    84: "VCC2_CAN",
    85: "GND2_RS485",
    86: "VCC2_RS485",
    87: "GND2_ETH",
    88: "VCC2_ETH",
    89: "CAN_H",
    90: "RS485_A",
    91: "ETH_TXP",
    92: "ETH_TXN",
    93: "ETH_RXP",
    94: "ETH_RXN",
    95: "ETH_LINE_TXP",
    96: "ETH_LINE_TXN",
    97: "ETH_LINE_RXP",
    98: "ETH_LINE_RXN",
}

# ---------------------------------------------------------------------------
# ISOW1044BDFMR pin→net mapping (SOIC-16W)
# ---------------------------------------------------------------------------
# Pinout (TI SLLSEO9):
#   1=VCC1  2=TXD  3=STB_N  4=RXD  5=NC  6=NC  7=NC  8=GND1
#   9=CANH  10=CANL  11=NC  12=GND2  13=GND2  14=VCC2_OUT  15=NC  16=NC
ISOW_NETS = {
    1:  (9,  "+3V3"),
    2:  (52, "MCAN0_TX"),
    3:  (15, "CAN_STB"),
    4:  (44, "MCAN0_RX"),
    8:  (51, "GND"),
    9:  (89, "CAN_H"),
    10: (74, "CAN_L"),
    12: (83, "GND2_CAN"),
    13: (83, "GND2_CAN"),
    14: (84, "VCC2_CAN"),
}

# ---------------------------------------------------------------------------
# ADM2795EBRWZ pin→net mapping (SOIC-20W)
# ---------------------------------------------------------------------------
# Pinout (ADI Rev. C, SOIC-20W):
#   1=VDD1  2=GND1  3=TXD  4=DE  5=RE_N  6=RXD  7=GND1  8=GND1
#   9=NC  10=NC  11=VDD2  12=GND2  13=GND2  14=A  15=B
#   16=NC  17=NC  18=GND2  19=GND2  20=VDD2
ADM_NETS = {
    1:  (9,  "+3V3"),
    2:  (51, "GND"),
    3:  (63, "RS485_TX"),
    4:  (65, "RS485_DE"),
    5:  (65, "RS485_DE"),    # RE_N tied to DE for half-duplex
    6:  (41, "RS485_RX"),
    7:  (51, "GND"),
    8:  (51, "GND"),
    11: (86, "VCC2_RS485"),
    12: (85, "GND2_RS485"),
    13: (85, "GND2_RS485"),
    14: (90, "RS485_A"),
    15: (78, "RS485_B"),
    18: (85, "GND2_RS485"),
    19: (85, "GND2_RS485"),
    20: (86, "VCC2_RS485"),
}

# ---------------------------------------------------------------------------
# ADIN1300BCPZ pin→net mapping (LFCSP-48)
# ---------------------------------------------------------------------------
# Simplified RMII net mapping (subset of full 48-pin ADIN1300 pinout):
# Pin 1 bottom-left, CCW. Full pinout from ADI ADIN1300BCPZ datasheet Rev A.
# Bottom (1-12): MDI_TX_P, MDI_TX_N, GND, MDI_RX_P, MDI_RX_N, GND,
#                VDD3P3, VDD3P3, VDD2P5, GND, GND, GND
# Left (13-24):  NC, NC, PHY_ADDR4, PHY_ADDR3, PHY_ADDR2, PHY_ADDR1,
#                PHY_ADDR0, MDIO, MDC, nINT, GND, GND
# Top (25-36):   GND, TX_EN, TXD1, TXD0, REF_CLK, RXD0, RXD1, CRS_DV,
#                RX_ER, GND, nRESET, GND
# Right (37-48): GND, GND, GND, VDD3P3, VDD3P3, GND, GND, GND, GND,
#                GND, GND, GND
ADIN_NETS = {
    # Bottom: MDI signals
    1:  (91, "ETH_TXP"),
    2:  (92, "ETH_TXN"),
    3:  (51, "GND"),
    4:  (93, "ETH_RXP"),
    5:  (94, "ETH_RXN"),
    6:  (51, "GND"),
    7:  (88, "VCC2_ETH"),
    8:  (88, "VCC2_ETH"),
    9:  (88, "VCC2_ETH"),
    10: (51, "GND"),
    11: (51, "GND"),
    12: (51, "GND"),
    # Left: control signals
    18: (14, "MDIO"),
    19: (3,  "MDC"),
    20: (53, "PHY1_INTRN"),
    21: (87, "GND2_ETH"),
    22: (87, "GND2_ETH"),
    # Top: RMII interface
    25: (87, "GND2_ETH"),
    26: (36, "RMII0_TX_EN"),
    27: (23, "RMII0_TXD1"),
    28: (2,  "RMII0_TXD0"),
    29: (19, "RMII0_REF_CLK"),
    30: (56, "RMII0_RXD0"),
    31: (20, "RMII0_RXD1"),
    32: (10, "RMII0_CRS_DV"),
    33: (55, "RMII0_RX_ER"),
    34: (87, "GND2_ETH"),
    35: (22, "PHY1_RSTN"),
    36: (87, "GND2_ETH"),
    # Right: power
    40: (88, "VCC2_ETH"),
    41: (88, "VCC2_ETH"),
    # EP: GND
    49: (51, "GND"),
}

# ---------------------------------------------------------------------------
# ISO7642FDWRR TX isolator pin→net mapping (SOIC-16W)
# ---------------------------------------------------------------------------
# ISO7642FDWRR: 6-channel digital isolator (SOIC-16W, TI SLLSE88F)
# Pinout: VCC1(1), A1(2), A2(3), A3(4), A4(5), A5(6), A6(7), GND1(8)
#         GND2(9), B6(10), B5(11), B4(12), B3(13), B2(14), B1(15), VCC2(16)
# TX isolator: MCU→PHY direction (input side 1, output side 2)
#   Ch1=REF_CLK, Ch2=TXD0, Ch3=TXD1, Ch4=TX_EN, Ch5=MDC, Ch6=PHY1_RSTN
ISO_TX_NETS = {
    1:  (9,  "+3V3"),         # VCC1 (MCU domain 3.3V)
    2:  (19, "RMII0_REF_CLK"),# A1 → REF_CLK in
    3:  (2,  "RMII0_TXD0"),   # A2 → TXD0 in
    4:  (23, "RMII0_TXD1"),   # A3 → TXD1 in
    5:  (36, "RMII0_TX_EN"),  # A4 → TX_EN in
    6:  (3,  "MDC"),           # A5 → MDC in
    7:  (22, "PHY1_RSTN"),    # A6 → RSTN in
    8:  (51, "GND"),           # GND1
    9:  (87, "GND2_ETH"),     # GND2 (isolated ETH domain)
    10: (22, "PHY1_RSTN"),    # B6 → RSTN out (to ADIN1300)
    11: (3,  "MDC"),           # B5 → MDC out
    12: (36, "RMII0_TX_EN"),  # B4 → TX_EN out
    13: (23, "RMII0_TXD1"),   # B3 → TXD1 out
    14: (2,  "RMII0_TXD0"),   # B2 → TXD0 out
    15: (19, "RMII0_REF_CLK"),# B1 → REF_CLK out
    16: (88, "VCC2_ETH"),     # VCC2 (isolated ETH 3.3V)
}

# ISO7642FDWRR RX isolator (PHY→MCU direction)
#   Ch1=RXD0, Ch2=RXD1, Ch3=CRS_DV, Ch4=RX_ER, Ch5=PHY1_INTRN, Ch6=MDIO
ISO_RX_NETS = {
    1:  (88, "VCC2_ETH"),     # VCC1 (isolated ETH domain)
    2:  (56, "RMII0_RXD0"),   # A1 → RXD0 in
    3:  (20, "RMII0_RXD1"),   # A2 → RXD1 in
    4:  (10, "RMII0_CRS_DV"), # A3 → CRS_DV in
    5:  (55, "RMII0_RX_ER"),  # A4 → RX_ER in
    6:  (53, "PHY1_INTRN"),   # A5 → nINT in
    7:  (14, "MDIO"),          # A6 → MDIO in
    8:  (87, "GND2_ETH"),     # GND1 (isolated ETH domain)
    9:  (51, "GND"),           # GND2 (MCU domain)
    10: (14, "MDIO"),          # B6 → MDIO out
    11: (53, "PHY1_INTRN"),   # B5 → nINT out
    12: (55, "RMII0_RX_ER"),  # B4 → RX_ER out
    13: (10, "RMII0_CRS_DV"), # B3 → CRS_DV out
    14: (20, "RMII0_RXD1"),   # B2 → RXD1 out
    15: (56, "RMII0_RXD0"),   # B1 → RXD0 out
    16: (9,  "+3V3"),           # VCC2 (MCU domain 3.3V)
}

# Würth 749010012A transformer pin→net mapping
# Pins 1-4: PHY MDI side (TX+, TX-, RX+, RX-)
# Pins 5-8: Line side (TX+, TX-, RX+, RX-)
ETH_XFMR_NETS = {
    1: (91, "ETH_TXP"),
    2: (92, "ETH_TXN"),
    3: (93, "ETH_RXP"),
    4: (94, "ETH_RXN"),
    5: (95, "ETH_LINE_TXP"),
    6: (96, "ETH_LINE_TXN"),
    7: (97, "ETH_LINE_RXP"),
    8: (98, "ETH_LINE_RXN"),
}

# JST GH 4P Ethernet harness connector pin→net mapping
# Pins: 1=TX+, 2=TX-, 3=RX+, 4=RX-
J_ETH_NETS = {
    1: (95, "ETH_LINE_TXP"),
    2: (96, "ETH_LINE_TXN"),
    3: (97, "ETH_LINE_RXP"),
    4: (98, "ETH_LINE_RXN"),
}

# SRF2012 CMC for CAN bus field lines
# A1/A2 = field-side terminal pair, B1/B2 = IC-side terminal pair
CMC_CAN_NETS = {
    1: (89, "CAN_H"),   # A1 → CAN H field
    2: (74, "CAN_L"),   # A2 → CAN L field
    3: (89, "CAN_H"),   # B1 → CAN H to connector
    4: (74, "CAN_L"),   # B2 → CAN L to connector
}

# SRF2012 CMC for RS-485 bus field lines
CMC_RS485_NETS = {
    1: (90, "RS485_A"),  # A1 → RS-485 A field
    2: (78, "RS485_B"),  # A2 → RS-485 B field
    3: (90, "RS485_A"),  # B1 → RS-485 A to connector
    4: (78, "RS485_B"),  # B2 → RS-485 B to connector
}

# PRTR5V0U2X TVS for CAN bus
# Pin 1=I/O1(CAN_H), 2=GND(GND2_CAN), 3=I/O2(CAN_L), 4=I/O3(NC), 5=VCC, 6=NC
TVS_CAN_NETS = {
    1: (89, "CAN_H"),
    2: (83, "GND2_CAN"),
    3: (74, "CAN_L"),
    5: (84, "VCC2_CAN"),
}

# PRTR5V0U2X TVS for RS-485 bus
TVS_RS485_NETS = {
    1: (90, "RS485_A"),
    2: (85, "GND2_RS485"),
    3: (78, "RS485_B"),
    5: (86, "VCC2_RS485"),
}

# SMAJ33CA TVS for MIL-STD-1553 bus protection
# Bidirectional, pins: 1=A, 2=K (anode toward bus, cathode to reference)
TVS_1553_NETS = {
    1: (51, "GND"),
    2: (0,  ""),
}

# Würth 742792512 ferrite bead on power entry
# 0805 2-terminal: pin 1 = power-in (+5V), pin 2 = power-out to board
FB1_NETS = {
    1: (54, "+5V"),
    2: (54, "+5V"),   # Same net, bead provides HF filtering
}

# X2Y bridging cap CAN isolation boundary
# Signal pins connect to same net (trivially), GND pins bridge GND↔GND2_CAN
X2Y_CAN_NETS = {
    1: (51, "GND"),
    2: (51, "GND"),
    3: (51, "GND"),
    4: (83, "GND2_CAN"),
}

# X2Y bridging cap RS-485 isolation boundary
X2Y_RS485_NETS = {
    1: (51, "GND"),
    2: (51, "GND"),
    3: (51, "GND"),
    4: (85, "GND2_RS485"),
}


# ---------------------------------------------------------------------------
# Main transform
# ---------------------------------------------------------------------------

def transform() -> None:
    """Execute all CAPE-A-1 → Wash PCB transformations."""
    print(f"Reading {SRC_PATH}")
    with open(SRC_PATH, "r", encoding="utf-8") as fh:
        text = fh.read()

    # -----------------------------------------------------------------------
    # A. Title block update
    # -----------------------------------------------------------------------
    print("Updating title block …")
    text = text.replace(
        '(title "CAPE-A-1")',
        '(title "Wash")'
    )
    text = text.replace(
        '(rev "M")',
        '(rev "A-STUB")'
    )
    text = text.replace(
        "(comment 4 \"ICM-42688-P IMU | BMP388 Baro | SAM-M10Q GPS | "
        "ATA6561 CAN FD | MAX3485E RS-485 | DS26LV31/32 1553 | "
        "DP83825I x2 ETH | SLB9670 TPM2 | 6x GPIO expansion headers\")",
        "(comment 4 \"ICM-42688-P IMU | BMP388 Baro | SAM-M10Q GPS | "
        "ISOW1044BDFMR CAN FD (iso) | ADM2795EBRWZ RS-485 (iso) | "
        "DS26LV31/32 1553 | ADIN1300+ISO7642 ETH (iso) | SLB9670 TPM2 | "
        "EMI: SRF2012 CMC | PRTR5V0U2X TVS | SMAJ33CA 1553 | 742792512 FB\")"
    )
    text = text.replace(
        '(date "2026")',
        '(date "2026-06-04")'
    )

    # -----------------------------------------------------------------------
    # B. Add new net declarations
    # -----------------------------------------------------------------------
    print("Inserting new net declarations …")
    text = insert_new_nets(text, NEW_NETS_A2)

    # -----------------------------------------------------------------------
    # C. Replace ATA6561 → ISOW1044BDFMR
    # -----------------------------------------------------------------------
    print("Replacing ATA6561 → ISOW1044BDFMR …")
    new_isow = make_soic16w("CAN-TR", "ISOW1044BDFMR", 135.0, 115.0, ISOW_NETS)
    text = replace_footprint(text, "CAN-TR", new_isow)

    # -----------------------------------------------------------------------
    # D. Replace MAX3485E → ADM2795EBRWZ
    # -----------------------------------------------------------------------
    print("Replacing MAX3485E → ADM2795EBRWZ …")
    new_adm = make_soic20w("RS485", "ADM2795EBRWZ", 135.0, 110.5, ADM_NETS)
    text = replace_footprint(text, "RS485", new_adm)

    # -----------------------------------------------------------------------
    # E. Remove DP83825I PHY footprints
    # -----------------------------------------------------------------------
    print("Removing DP83825I PHY footprints …")
    text = remove_footprint(text, "ETH1-PHY")
    text = remove_footprint(text, "ETH2-PHY")

    # -----------------------------------------------------------------------
    # F. Remove old ETH JST-GH-6P connector footprints
    # -----------------------------------------------------------------------
    print("Removing old ETH connector footprints …")
    text = remove_footprint(text, "ETH1")
    text = remove_footprint(text, "ETH2")

    # -----------------------------------------------------------------------
    # G. Add new EMI-hardened Ethernet stack
    # -----------------------------------------------------------------------
    print("Adding new Ethernet PHY stack …")
    new_fps = (
        make_soic16w("U-ISO-TX", "ISO7642FDWRR", 133.0, 103.0, ISO_TX_NETS) +
        make_lfcsp48("ETH-PHY", "ADIN1300BCPZ", 143.0, 103.0, ADIN_NETS) +
        make_soic16w("U-ISO-RX", "ISO7642FDWRR", 154.0, 103.0, ISO_RX_NETS) +
        make_eth_xfmr("T-ETH", 160.0, 103.0, ETH_XFMR_NETS) +
        make_jst_gh4p("J-ETH", "JST-GH-4P-ETH", 165.0, 103.0, J_ETH_NETS)
    )

    # -----------------------------------------------------------------------
    # H. Add EMI protection components
    # -----------------------------------------------------------------------
    print("Adding EMI protection components …")
    new_fps += (
        make_srf2012("CMC-CAN",   127.5, 96.5,  CMC_CAN_NETS) +
        make_prtr5v0u2x("TVS-CAN",  131.0, 96.5,  TVS_CAN_NETS) +
        make_srf2012("CMC-RS485",  127.5, 99.5,  CMC_RS485_NETS) +
        make_prtr5v0u2x("TVS-RS485", 131.0, 99.5,  TVS_RS485_NETS) +
        make_smaj33ca("TVS-1553",  149.0, 119.0, TVS_1553_NETS) +
        make_0805("FB1", "742792512", 128.0, 122.0, FB1_NETS) +
        make_x2y_cap("X2Y-CAN",   132.0, 113.5, X2Y_CAN_NETS) +
        make_x2y_cap("X2Y-RS485", 132.0, 109.5, X2Y_RS485_NETS)
    )

    # Insert all new footprints before the final closing paren
    last_paren = text.rfind("\n)")
    if last_paren < 0:
        last_paren = text.rfind(")")
    text = text[:last_paren] + "\n" + new_fps + text[last_paren:]

    # -----------------------------------------------------------------------
    # I. Remap all UUIDs to Wash namespace
    # -----------------------------------------------------------------------
    print("Remapping UUIDs to a2000000 namespace …")
    text = remap_uuids(text)

    # -----------------------------------------------------------------------
    # Write output
    # -----------------------------------------------------------------------
    print(f"Writing {DST_PATH}")
    with open(DST_PATH, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("Done — Wash.kicad_pcb generated successfully.")


if __name__ == "__main__":
    transform()
