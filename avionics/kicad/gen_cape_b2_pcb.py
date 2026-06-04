#!/usr/bin/env python3
"""
gen_cape_b2_pcb.py — Transform CAPE-B-1.kicad_pcb into CAPE-B-2.kicad_pcb.

CAPE-B-2 is the EMI-hardened Comms, Logging & Payload Cape for the Serenity UAV.
This script performs the following PCB-level transformations:

    A. Updates the title block (title, rev, comment line) to reflect CAPE-B-2.
    B. Replaces the ATA6561 CAN transceiver footprint (SOIC-8) with the
       ISOW1044BDFMR (SOIC-16W, 5 kV reinforced isolation + integrated DC/DC).
    C. Replaces the MAX3485E RS-485 transceiver footprint (SOIC-8) with the
       ADM2795EBRWZ (SOIC-20W, 5 kV reinforced isolation + integrated DC/DC).
    D. Removes both DP83825I Ethernet PHY footprints (LQFP-48).
    E. Removes the ETH1 and ETH2 JST-GH-6P connector footprints.
    F. Adds the ADIN1300BCPZ EMI-hardened PHY (LFCSP-48).
    G. Adds two ISO7642FDWRR digital isolators (SOIC-16W) for RMII isolation.
    H. Adds the Würth 749010012A SMD Ethernet transformer (8-pad SMD).
    I. Adds a JST GH 4-pin Ethernet harness connector (J-ETH).
    J. Adds EMI protection components: SRF2012-100Y common-mode chokes,
       PRTR5V0U2X TVS arrays, SMAJ33CA 1553 TVS, Würth 742792512 ferrite bead,
       and X2Y bridging capacitors across isolation boundaries.
    K. Adds net declarations for all new isolation-domain signals.
    L. Remaps all UUIDs to the "b2000000-0000-0000-0000-" prefix.
    M. Retains all CAPE-B-specific components: RFM95W LoRa, WL1837MOD WiFi/BT,
       microSD logger, DRV8833 winch driver, HX711 load cell ADC, PCA9685 PWM
       expander, W25Q128JV NOR flash, ATF16V8BQL CPLD.

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
"""

import re
import os

# ---------------------------------------------------------------------------
# File paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(SCRIPT_DIR, "CAPE-B-1.kicad_pcb")
DST_PATH = os.path.join(SCRIPT_DIR, "CAPE-B-2.kicad_pcb")

# ---------------------------------------------------------------------------
# UUID management
# ---------------------------------------------------------------------------
OLD_UUID_RE = re.compile(
    r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
)
NEW_UUID_PREFIX = "b2000000-0000-0000-0000-"
_uuid_counter = 200_000_000_001


def next_uuid() -> str:
    """Return the next sequential UUID with the CAPE-B-2 prefix."""
    global _uuid_counter
    uid = f"{NEW_UUID_PREFIX}{_uuid_counter:012d}"
    _uuid_counter += 1
    return uid


# ---------------------------------------------------------------------------
# S-expression bracket parser
# ---------------------------------------------------------------------------

def find_balanced(text: str, start: int) -> int:
    """Return the index ONE PAST the closing ')' balancing the '(' at *start*.

    Args:
        text:  Full PCB text.
        start: Index of the opening '(' to balance.

    Returns:
        Index immediately after the matching closing ')'.
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
    raise ValueError(f"Unclosed S-expression at index {start}")


def find_footprint(text: str, ref: str):
    """Find the footprint block with the given Reference property value.

    Args:
        text: Full PCB text.
        ref:  Reference designator to search for.

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
        if re.search(r'\(property\s+"Reference"\s+"' + re.escape(ref) + r'"', block):
            return fp_start, fp_end
        i = fp_end
    return None, None


def remove_footprint(text: str, ref: str) -> str:
    """Remove the footprint block with the given Reference from *text*."""
    start, end = find_footprint(text, ref)
    if start is None:
        print(f"  WARNING: footprint '{ref}' not found — skipping removal")
        return text
    prefix = text[:start]
    while prefix and prefix[-1] in ('\t', ' '):
        prefix = prefix[:-1]
    if prefix.endswith('\n'):
        prefix = prefix[:-1]
    result = prefix + text[end:]
    print(f"  Removed footprint '{ref}'")
    return result


def replace_footprint(text: str, ref: str, new_block: str) -> str:
    """Replace the footprint block for *ref* with *new_block*."""
    start, end = find_footprint(text, ref)
    if start is None:
        print(f"  WARNING: footprint '{ref}' not found — skipping replacement")
        return text
    result = text[:start] + new_block + text[end:]
    print(f"  Replaced footprint '{ref}'")
    return result


# ---------------------------------------------------------------------------
# Pad / property helpers
# ---------------------------------------------------------------------------

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
    """Generate a single SMD rect pad entry."""
    net_str = (
        f"\n\t\t\t(net {net_num} \"{net_name}\")" if net_num > 0 else ""
    )
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


# ---------------------------------------------------------------------------
# Footprint generators (SOIC-16W, SOIC-20W, LFCSP-48, ETH XFMR, JST, EMI)
# ---------------------------------------------------------------------------
SOIC16W_Y = [-4.445, -3.175, -1.905, -0.635, 0.635, 1.905, 3.175, 4.445]
SOIC20W_Y = [-5.715, -4.445, -3.175, -1.905, -0.635,
             0.635, 1.905, 3.175, 4.445, 5.715]
_LFCSP48_OFFSETS = [i * 0.5 - 2.75 for i in range(12)]


def make_soic16w(ref: str, value: str, x: float, y: float,
                 pin_nets: dict, angle: float = 0.0) -> str:
    """Generate a SOIC-16W (7.5×10.3mm, 1.27mm pitch) footprint block.

    Args:
        ref:      Reference designator string.
        value:    Component value / part number.
        x, y:     PCB placement coordinates in mm.
        pin_nets: Dict {pin_num: (net_num, net_name)} for connected pins.
        angle:    Rotation angle in degrees.

    Returns:
        Complete KiCad PCB footprint block string.
    """
    pads_str = ""
    for i, py in enumerate(SOIC16W_Y):
        pin = i + 1
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _pad(str(pin), -5.1, py, nn, nm)
    for i, py in enumerate(reversed(SOIC16W_Y)):
        pin = 9 + i
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _pad(str(pin), 5.1, py, nn, nm)

    silk = _soic_silk_lines(half_w=2.0, half_h=5.2)
    cyd = _soic_courtyard(cx_outer=6.4, cy_outer=5.55)
    angle_str = f" {angle}" if angle != 0.0 else ""

    return (
        f"\t(footprint \"SOIC-16W_7.5x10.3mm_P1.27mm\"\n"
        f"\t\t(layer \"F.Cu\")\n"
        f"\t\t(uuid \"{next_uuid()}\")\n"
        f"\t\t(at {x} {y}{angle_str})\n"
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


def make_soic20w(ref: str, value: str, x: float, y: float,
                 pin_nets: dict, angle: float = 0.0) -> str:
    """Generate a SOIC-20W (7.5×12.8mm, 1.27mm pitch) footprint block.

    Args:
        ref:      Reference designator string.
        value:    Component value / part number.
        x, y:     PCB placement coordinates in mm.
        pin_nets: Dict {pin_num: (net_num, net_name)}.
        angle:    Rotation angle in degrees.

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
    angle_str = f" {angle}" if angle != 0.0 else ""

    return (
        f"\t(footprint \"SOIC-20W_7.5x12.8mm_P1.27mm\"\n"
        f"\t\t(layer \"F.Cu\")\n"
        f"\t\t(uuid \"{next_uuid()}\")\n"
        f"\t\t(at {x} {y}{angle_str})\n"
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


def _lfcsp_pad(num: str, x: float, y: float, net_num: int,
               net_name: str, w: float = 0.30, h: float = 0.65) -> str:
    """Generate a single QFN/LFCSP pad."""
    net_str = f"\n\t\t\t(net {net_num} \"{net_name}\")" if net_num > 0 else ""
    return (
        f"\t\t(pad \"{num}\" smd roundrect\n"
        f"\t\t\t(at {x:.4f} {y:.4f})\n"
        f"\t\t\t(size {w} {h})\n"
        f"\t\t\t(layers \"F.Cu\" \"F.Mask\" \"F.Paste\")\n"
        f"\t\t\t(roundrect_rratio 0.25){net_str}\n"
        f"\t\t\t(uuid \"{next_uuid()}\")\n"
        f"\t\t)\n"
    )


def make_lfcsp48(ref: str, value: str, x: float, y: float,
                 pin_nets: dict) -> str:
    """Generate a LFCSP-48 (7×7mm, 0.5mm pitch) footprint block.

    ADI LFCSP pin 1 at bottom-left, CCW: 1-12 bottom, 13-24 left,
    25-36 top, 37-48 right, EP=49 at centre.

    Args:
        ref:      Reference designator.
        value:    Component value / part number.
        x, y:     PCB placement coordinates in mm.
        pin_nets: Dict {pin_num: (net_num, net_name)}.

    Returns:
        Complete KiCad PCB footprint block string.
    """
    pads_str = ""
    for i, ox in enumerate(_LFCSP48_OFFSETS):
        pin = i + 1
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _lfcsp_pad(str(pin), ox, 4.0, nn, nm, w=0.30, h=0.65)
    for i, oy in enumerate(reversed(_LFCSP48_OFFSETS)):
        pin = 13 + i
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _lfcsp_pad(str(pin), -4.0, oy, nn, nm, w=0.65, h=0.30)
    for i, ox in enumerate(reversed(_LFCSP48_OFFSETS)):
        pin = 25 + i
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _lfcsp_pad(str(pin), ox, -4.0, nn, nm, w=0.30, h=0.65)
    for i, oy in enumerate(_LFCSP48_OFFSETS):
        pin = 37 + i
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _lfcsp_pad(str(pin), 4.0, oy, nn, nm, w=0.65, h=0.30)
    nn_gnd, nm_gnd = pin_nets.get(49, (53, "GND"))
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


def make_eth_xfmr(ref: str, x: float, y: float, pin_nets: dict) -> str:
    """Generate SMD Ethernet transformer footprint (Würth 749010012A).

    8-pad: pins 1-4 left (PHY MDI), pins 5-8 right (line to JST).
    """
    ETH_XFMR_Y_OFFSETS = [-1.5, -0.5, 0.5, 1.5]
    pads_str = ""
    for i, py in enumerate(ETH_XFMR_Y_OFFSETS):
        pin = i + 1
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _pad(str(pin), -2.5, py, nn, nm, size_x=1.20, size_y=0.60)
    for i, py in enumerate(ETH_XFMR_Y_OFFSETS):
        pin = i + 5
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _pad(str(pin), 2.5, py, nn, nm, size_x=1.20, size_y=0.60)
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


def make_jst_gh4p(ref: str, value: str, x: float, y: float,
                  pin_nets: dict) -> str:
    """Generate JST GH 4-pin connector footprint (SM04B-GHS-TB)."""
    pad_xs = [-1.875, -0.625, 0.625, 1.875]
    pads_str = ""
    for i, px in enumerate(pad_xs):
        pin = i + 1
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _pad_rect(str(pin), px, 0.0, nn, nm, 0.80, 1.60)
    cyd = _soic_courtyard(cx_outer=2.8, cy_outer=1.5)
    return (
        f"\t(footprint \"JST_GH_4P\"\n"
        f"\t\t(layer \"F.Cu\")\n"
        f"\t\t(uuid \"{next_uuid()}\")\n"
        f"\t\t(at {x} {y})\n"
        f"\t\t(descr \"JST GH 4-pin SMD, 1.25mm pitch — SM04B-GHS-TB\")\n"
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


def make_srf2012(ref: str, x: float, y: float, pin_nets: dict) -> str:
    """Generate SRF2012-100Y 4-terminal CMC footprint."""
    layout = [(-1.65, -0.35, 1), (-1.65, 0.35, 2),
              (1.65, -0.35, 3), (1.65, 0.35, 4)]
    pads_str = ""
    for px, py, pin in layout:
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _pad(str(pin), px, py, nn, nm, size_x=0.90, size_y=0.50)
    cyd = _soic_courtyard(cx_outer=2.4, cy_outer=1.0)
    return (
        f"\t(footprint \"Bourns_SRF2012_4T\"\n"
        f"\t\t(layer \"F.Cu\")\n"
        f"\t\t(uuid \"{next_uuid()}\")\n"
        f"\t\t(at {x} {y})\n"
        f"\t\t(descr \"Bourns SRF2012-100Y CMC, 4-terminal 2012\")\n"
        f"\t\t(tags \"CMC common-mode choke EMI filter 2012\")\n"
        f"{_prop('Reference', ref, 0, -1.2, size=0.6)}"
        f"{_prop('Value', 'SRF2012-100Y', 0, 1.2, layer='F.Fab', size=0.6)}"
        f"\t\t(attr smd)\n"
        f"{cyd}"
        f"{pads_str}"
        f"\t\t(embedded_fonts no)\n"
        f"\t)\n"
    )


def make_prtr5v0u2x(ref: str, x: float, y: float, pin_nets: dict) -> str:
    """Generate PRTR5V0U2X SOT-363 TVS array footprint."""
    layout = [
        (-1.30, -0.65, 1), (-1.30, 0.0, 2), (-1.30, 0.65, 3),
        (1.30, 0.65, 4),   (1.30, 0.0, 5),  (1.30, -0.65, 6),
    ]
    pads_str = ""
    for px, py, pin in layout:
        nn, nm = pin_nets.get(pin, (0, ""))
        pads_str += _pad(str(pin), px, py, nn, nm, size_x=0.90, size_y=0.55)
    cyd = _soic_courtyard(cx_outer=2.1, cy_outer=1.3)
    return (
        f"\t(footprint \"SOT-363_SC-88\"\n"
        f"\t\t(layer \"F.Cu\")\n"
        f"\t\t(uuid \"{next_uuid()}\")\n"
        f"\t\t(at {x} {y})\n"
        f"\t\t(descr \"Nexperia PRTR5V0U2X SOT-363 dual TVS array\")\n"
        f"\t\t(tags \"TVS ESD SOT363 SC88 EMI protection\")\n"
        f"{_prop('Reference', ref, 0, -1.5, size=0.6)}"
        f"{_prop('Value', 'PRTR5V0U2X', 0, 1.5, layer='F.Fab', size=0.6)}"
        f"\t\t(attr smd)\n"
        f"{cyd}"
        f"{pads_str}"
        f"\t\t(embedded_fonts no)\n"
        f"\t)\n"
    )


def make_smaj33ca(ref: str, x: float, y: float, pin_nets: dict) -> str:
    """Generate SMAJ33CA DO-214AC (SMA) TVS footprint."""
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
        f"\t\t(descr \"SMAJ33CA DO-214AC (SMA) 33V TVS, bidirectional\")\n"
        f"\t\t(tags \"TVS SMA DO-214AC 33V 1553 EMI\")\n"
        f"{_prop('Reference', ref, 0, -2.2, size=0.7)}"
        f"{_prop('Value', 'SMAJ33CA', 0, 2.2, layer='F.Fab', size=0.7)}"
        f"\t\t(attr smd)\n"
        f"{cyd}"
        f"{pads_str}"
        f"\t\t(embedded_fonts no)\n"
        f"\t)\n"
    )


def make_0805(ref: str, value: str, x: float, y: float,
              pin_nets: dict) -> str:
    """Generate standard 0805 SMD two-pad footprint."""
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


def make_x2y_cap(ref: str, x: float, y: float, pin_nets: dict) -> str:
    """Generate X2Y bridging capacitor (4-terminal 0402-style) footprint."""
    nn1, nm1 = pin_nets.get(1, (0, ""))
    nn2, nm2 = pin_nets.get(2, (0, ""))
    nn3, nm3 = pin_nets.get(3, (53, "GND"))
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
        f"\t\t(descr \"X2Y bridging cap 4.7nF — isolation boundary bridge\")\n"
        f"\t\t(tags \"X2Y cap 4-terminal isolation EMI\")\n"
        f"{_prop('Reference', ref, 0, -1.1, size=0.5)}"
        f"{_prop('Value', '4.7nF X2Y', 0, 1.1, layer='F.Fab', size=0.5)}"
        f"\t\t(attr smd)\n"
        f"{cyd}"
        f"{pads_str}"
        f"\t\t(embedded_fonts no)\n"
        f"\t)\n"
    )


# ---------------------------------------------------------------------------
# Net list helper
# ---------------------------------------------------------------------------

def insert_new_nets(text: str, new_nets: dict) -> str:
    """Insert new net declarations after the last existing (net N ...) line."""
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
    """Remap all original UUIDs to the CAPE-B-2 UUID namespace."""
    seen: dict[str, str] = {}

    def _replace(m: re.Match) -> str:
        orig = m.group(0)
        if orig not in seen:
            seen[orig] = next_uuid()
        return seen[orig]

    return OLD_UUID_RE.sub(_replace, text)


# ---------------------------------------------------------------------------
# Net assignments for CAPE-B-2
# ---------------------------------------------------------------------------
# CAPE-B-1 existing net numbers (key signals):
#   47=CAN_STB  40=MCAN1_TX  43=MCAN1_RX  68=CAN_L
#   23=RS485_TX  20=RS485_RX  34=RS485_DE  80=RS485_B
#   53=GND  61=+3V3  62=+5V
#   36=RMII0_REF_CLK  46=RMII0_TXD0  22=RMII0_TXD1  6=RMII0_TX_EN
#   5=RMII0_RXD0  18=RMII0_RXD1  17=RMII0_CRS_DV  44=RMII0_RX_ER
#   7=MDC  52=MDIO  35=PHY1_RSTN  2=PHY1_INTRN
#
# New CAPE-B-2 nets starting at 86 (after TMESH_N at 85):
NEW_NETS_B2 = {
    86:  "GND2_CAN",
    87:  "VCC2_CAN",
    88:  "GND2_RS485",
    89:  "VCC2_RS485",
    90:  "GND2_ETH",
    91:  "VCC2_ETH",
    92:  "CAN_H",
    93:  "RS485_A",
    94:  "ETH_TXP",
    95:  "ETH_TXN",
    96:  "ETH_RXP",
    97:  "ETH_RXN",
    98:  "ETH_LINE_TXP",
    99:  "ETH_LINE_TXN",
    100: "ETH_LINE_RXP",
    101: "ETH_LINE_RXN",
}

# ---------------------------------------------------------------------------
# Component pin→net mappings for CAPE-B-2
# ---------------------------------------------------------------------------
# ISOW1044BDFMR (CAN-TR, SOIC-16W) — CAPE-B-1 uses MCAN1 (not MCAN0)
ISOW_NETS = {
    1:  (61, "+3V3"),
    2:  (40, "MCAN1_TX"),
    3:  (47, "CAN_STB"),
    4:  (43, "MCAN1_RX"),
    8:  (53, "GND"),
    9:  (92, "CAN_H"),
    10: (68, "CAN_L"),
    12: (86, "GND2_CAN"),
    13: (86, "GND2_CAN"),
    14: (87, "VCC2_CAN"),
}

# ADM2795EBRWZ (RS485, SOIC-20W)
ADM_NETS = {
    1:  (61, "+3V3"),
    2:  (53, "GND"),
    3:  (23, "RS485_TX"),
    4:  (34, "RS485_DE"),
    5:  (34, "RS485_DE"),   # RE_N tied to DE
    6:  (20, "RS485_RX"),
    7:  (53, "GND"),
    8:  (53, "GND"),
    11: (89, "VCC2_RS485"),
    12: (88, "GND2_RS485"),
    13: (88, "GND2_RS485"),
    14: (93, "RS485_A"),
    15: (80, "RS485_B"),
    18: (88, "GND2_RS485"),
    19: (88, "GND2_RS485"),
    20: (89, "VCC2_RS485"),
}

# ADIN1300BCPZ (ETH-PHY, LFCSP-48) — using RMII0 from CAPE-B-1
ADIN_NETS = {
    1:  (94, "ETH_TXP"),
    2:  (95, "ETH_TXN"),
    3:  (53, "GND"),
    4:  (96, "ETH_RXP"),
    5:  (97, "ETH_RXN"),
    6:  (53, "GND"),
    7:  (91, "VCC2_ETH"),
    8:  (91, "VCC2_ETH"),
    9:  (91, "VCC2_ETH"),
    10: (53, "GND"),
    11: (53, "GND"),
    12: (53, "GND"),
    18: (52, "MDIO"),
    19: (7,  "MDC"),
    20: (2,  "PHY1_INTRN"),
    21: (90, "GND2_ETH"),
    22: (90, "GND2_ETH"),
    25: (90, "GND2_ETH"),
    26: (6,  "RMII0_TX_EN"),
    27: (22, "RMII0_TXD1"),
    28: (46, "RMII0_TXD0"),
    29: (36, "RMII0_REF_CLK"),
    30: (5,  "RMII0_RXD0"),
    31: (18, "RMII0_RXD1"),
    32: (17, "RMII0_CRS_DV"),
    33: (44, "RMII0_RX_ER"),
    34: (90, "GND2_ETH"),
    35: (35, "PHY1_RSTN"),
    36: (90, "GND2_ETH"),
    40: (91, "VCC2_ETH"),
    41: (91, "VCC2_ETH"),
    49: (53, "GND"),
}

# ISO7642FDWRR TX isolator (MCU→PHY)
ISO_TX_NETS = {
    1:  (61, "+3V3"),
    2:  (36, "RMII0_REF_CLK"),
    3:  (46, "RMII0_TXD0"),
    4:  (22, "RMII0_TXD1"),
    5:  (6,  "RMII0_TX_EN"),
    6:  (7,  "MDC"),
    7:  (35, "PHY1_RSTN"),
    8:  (53, "GND"),
    9:  (90, "GND2_ETH"),
    10: (35, "PHY1_RSTN"),
    11: (7,  "MDC"),
    12: (6,  "RMII0_TX_EN"),
    13: (22, "RMII0_TXD1"),
    14: (46, "RMII0_TXD0"),
    15: (36, "RMII0_REF_CLK"),
    16: (91, "VCC2_ETH"),
}

# ISO7642FDWRR RX isolator (PHY→MCU)
ISO_RX_NETS = {
    1:  (91, "VCC2_ETH"),
    2:  (5,  "RMII0_RXD0"),
    3:  (18, "RMII0_RXD1"),
    4:  (17, "RMII0_CRS_DV"),
    5:  (44, "RMII0_RX_ER"),
    6:  (2,  "PHY1_INTRN"),
    7:  (52, "MDIO"),
    8:  (90, "GND2_ETH"),
    9:  (53, "GND"),
    10: (52, "MDIO"),
    11: (2,  "PHY1_INTRN"),
    12: (44, "RMII0_RX_ER"),
    13: (17, "RMII0_CRS_DV"),
    14: (18, "RMII0_RXD1"),
    15: (5,  "RMII0_RXD0"),
    16: (61, "+3V3"),
}

# Würth 749010012A transformer
ETH_XFMR_NETS = {
    1: (94, "ETH_TXP"),
    2: (95, "ETH_TXN"),
    3: (96, "ETH_RXP"),
    4: (97, "ETH_RXN"),
    5: (98, "ETH_LINE_TXP"),
    6: (99, "ETH_LINE_TXN"),
    7: (100, "ETH_LINE_RXP"),
    8: (101, "ETH_LINE_RXN"),
}

# JST GH 4P Ethernet harness connector
J_ETH_NETS = {
    1: (98,  "ETH_LINE_TXP"),
    2: (99,  "ETH_LINE_TXN"),
    3: (100, "ETH_LINE_RXP"),
    4: (101, "ETH_LINE_RXN"),
}

# SRF2012 CMCs
CMC_CAN_NETS = {
    1: (92, "CAN_H"),  2: (68, "CAN_L"),
    3: (92, "CAN_H"),  4: (68, "CAN_L"),
}
CMC_RS485_NETS = {
    1: (93, "RS485_A"),  2: (80, "RS485_B"),
    3: (93, "RS485_A"),  4: (80, "RS485_B"),
}

# PRTR5V0U2X TVS arrays
TVS_CAN_NETS = {
    1: (92, "CAN_H"),
    2: (86, "GND2_CAN"),
    3: (68, "CAN_L"),
    5: (87, "VCC2_CAN"),
}
TVS_RS485_NETS = {
    1: (93, "RS485_A"),
    2: (88, "GND2_RS485"),
    3: (80, "RS485_B"),
    5: (89, "VCC2_RS485"),
}

# SMAJ33CA 1553 TVS
TVS_1553_NETS = {1: (53, "GND"), 2: (0, "")}

# Würth 742792512 ferrite bead
FB1_NETS = {1: (62, "+5V"), 2: (62, "+5V")}

# X2Y bridging caps
X2Y_CAN_NETS = {
    1: (53, "GND"), 2: (53, "GND"),
    3: (53, "GND"), 4: (86, "GND2_CAN"),
}
X2Y_RS485_NETS = {
    1: (53, "GND"), 2: (53, "GND"),
    3: (53, "GND"), 4: (88, "GND2_RS485"),
}


# ---------------------------------------------------------------------------
# Main transform
# ---------------------------------------------------------------------------

def transform() -> None:
    """Execute all CAPE-B-1 → CAPE-B-2 PCB transformations."""
    print(f"Reading {SRC_PATH}")
    with open(SRC_PATH, "r", encoding="utf-8") as fh:
        text = fh.read()

    # A. Title block update
    print("Updating title block …")
    text = text.replace('(title "CAPE-B-1")', '(title "CAPE-B-2")')
    text = text.replace('(rev "M")', '(rev "A-STUB")')
    text = text.replace(
        "(comment 4 \"F: ATA6561 CAN FD | MAX3485E RS-485 | DS26LV31/32 1553 | "
        "DP83825I x2 ETH | SLB9670 TPM2 | DRV8833 Winch | HX711 Load Cell | "
        "PCA9685 PWM | B: RFM95W LoRa | WL1837MOD WiFi/BT | ATF16V8BQL CPLD | "
        "W25Q128JV NOR | microSD log slot\")",
        "(comment 4 \"F: ISOW1044BDFMR CAN FD (iso) | ADM2795EBRWZ RS-485 (iso) | "
        "DS26LV31/32 1553 | ADIN1300+ISO7642 ETH (iso) | SLB9670 TPM2 | "
        "DRV8833 Winch | HX711 Load Cell | PCA9685 PWM | "
        "B: RFM95W LoRa | WL1837MOD WiFi/BT | ATF16V8BQL CPLD | "
        "W25Q128JV NOR | microSD log slot | EMI: SRF2012 CMC | "
        "PRTR5V0U2X TVS | SMAJ33CA 1553 | 742792512 FB\")"
    )
    text = text.replace('(date "2026")', '(date "2026-06-04")')

    # B. Add new net declarations
    print("Inserting new net declarations …")
    text = insert_new_nets(text, NEW_NETS_B2)

    # C. Replace ATA6561 → ISOW1044BDFMR (placed at 90° in CAPE-B-1)
    print("Replacing ATA6561 → ISOW1044BDFMR …")
    new_isow = make_soic16w("CAN-TR", "ISOW1044BDFMR",
                            140.5, 114.0, ISOW_NETS, angle=90.0)
    text = replace_footprint(text, "CAN-TR", new_isow)

    # D. Replace MAX3485E → ADM2795EBRWZ (placed at 90° in CAPE-B-1)
    print("Replacing MAX3485E → ADM2795EBRWZ …")
    new_adm = make_soic20w("RS485", "ADM2795EBRWZ",
                           134.0, 114.0, ADM_NETS, angle=90.0)
    text = replace_footprint(text, "RS485", new_adm)

    # E. Remove DP83825I PHY footprints
    print("Removing DP83825I PHY footprints …")
    text = remove_footprint(text, "ETH1-PHY")
    text = remove_footprint(text, "ETH2-PHY")

    # F. Remove old ETH connector footprints
    print("Removing old ETH connector footprints …")
    text = remove_footprint(text, "ETH1")
    text = remove_footprint(text, "ETH2")

    # G. Add new Ethernet PHY stack (centred between old PHY positions)
    print("Adding new Ethernet PHY stack …")
    new_fps = (
        make_soic16w("U-ISO-TX", "ISO7642FDWRR", 137.0, 103.75, ISO_TX_NETS) +
        make_lfcsp48("ETH-PHY", "ADIN1300BCPZ", 150.0, 103.75, ADIN_NETS) +
        make_soic16w("U-ISO-RX", "ISO7642FDWRR", 163.0, 103.75, ISO_RX_NETS) +
        make_eth_xfmr("T-ETH", 169.0, 103.75, ETH_XFMR_NETS) +
        make_jst_gh4p("J-ETH", "JST-GH-4P-ETH", 174.0, 103.75, J_ETH_NETS)
    )

    # H. Add EMI protection components
    print("Adding EMI protection components …")
    new_fps += (
        make_srf2012("CMC-CAN",   126.5, 96.5,  CMC_CAN_NETS) +
        make_prtr5v0u2x("TVS-CAN",  130.0, 96.5,  TVS_CAN_NETS) +
        make_srf2012("CMC-RS485",  126.5, 99.5,  CMC_RS485_NETS) +
        make_prtr5v0u2x("TVS-RS485", 130.0, 99.5,  TVS_RS485_NETS) +
        make_smaj33ca("TVS-1553",  148.0, 119.0, TVS_1553_NETS) +
        make_0805("FB1", "742792512", 127.0, 122.0, FB1_NETS) +
        make_x2y_cap("X2Y-CAN",   132.0, 113.5, X2Y_CAN_NETS) +
        make_x2y_cap("X2Y-RS485", 132.0, 109.5, X2Y_RS485_NETS)
    )

    # Insert new footprints before the final closing paren
    last_paren = text.rfind("\n)")
    if last_paren < 0:
        last_paren = text.rfind(")")
    text = text[:last_paren] + "\n" + new_fps + text[last_paren:]

    # I. Remap all UUIDs to CAPE-B-2 namespace
    print("Remapping UUIDs to b2000000 namespace …")
    text = remap_uuids(text)

    # Write output
    print(f"Writing {DST_PATH}")
    with open(DST_PATH, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("Done — CAPE-B-2.kicad_pcb generated successfully.")


if __name__ == "__main__":
    transform()
