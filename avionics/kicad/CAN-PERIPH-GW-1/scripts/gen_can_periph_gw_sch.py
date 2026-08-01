#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_can_periph_gw_sch.py -- author CAN-PERIPH-GW-1.kicad_sch.

CAN-PERIPH-GW-1 ("SKIPPER-CAN-PERIPH-GW-PCB") is a standalone, TPM-secured,
dual-isolated-bus (CAN-FD + RS-485) peripheral gateway. It is a clean-room
remix of the *concept* behind the VimDrones "AP_Periph Pico" (a small
dedicated MCU + CAN transceiver running ArduPilot AP_Periph firmware to
bridge serial/I2C/PWM sensors onto DroneCAN -- see
https://dev.vimdrones.com/products/vimdrones_can_periph_pico/, informational
reference only, spec table read 2026-07-25: STM32L431 MCU, single
non-isolated CAN port, 5V supply, 15x11mm). VimDrones' own KiCad source
(https://github.com/VimDrones/AM32_esc_development_board, confirmed
STM32L431KCUx + NXP TJA1051TK-3) is GPL-3.0-licensed -- INCOMPATIBLE with this
project's CC BY 4.0 terms, so no VimDrones file, symbol, or schematic
geometry is copied here. Only the public spec facts (MCU family choice,
CAN-bridge concept, 5V supply, switchable 120R termination) informed this
design; every symbol/footprint below is either this project's own
already-verified clean-room part (MSPM0G3507, SLB9672, ISOW1044 -- reused
verbatim from Observer, ERC-0 proven) or newly authored here directly from the
OEM datasheet in avionics/datasheets/.

Remix additions over the VimDrones concept (the 3 datasheets in this task):
    U2  Infineon SLB9672   TPM 2.0 (avionics/datasheets/SLB_9672XU20_Infineon.pdf)
    U3  TI ISOW1044BDFMR   isolated CAN-FD xcvr (avionics/datasheets/isow1044.pdf)
    U4  ADI ADM2795E       isolated RS-485 xcvr (avionics/datasheets/adm2795e.pdf)
        -- NEW clean-room symbol authored here from the real 16-lead SOIC_W
           (RW-16) pinout (ADM2795E datasheet Table 10). NOTE: the
           "ADM2795EBRWZ" symbol already embedded in Pilot.kicad_sch /
           XO.kicad_sch has WRONG pin numbers (a pin 17 on a 16-pin part; a
           duplicate pin 20 on two different pin names) -- it was evidently
           cloned from the ISOW1044 (20-pin) template and never corrected.
           Flagged in REFERENCES.md; NOT reused here.

MCU: TI MSPM0G3507 (fleet-standard part, REF-SENSOR-004; native CAN 2.0/CAN-FD
peripheral, 4x UART, 2x SPI, up to 60 GPIO) -- chosen over VimDrones' own
STM32L431 so this gateway is built from the SAME MCU family already used on
Pilot/XO/Observer, not a new one-off part, and so no GPL-licensed VimDrones
schematic content needs to be touched at all.

STACKABLE (2026-07-26): set N_STACKS below to put multiple complete trust
modules (own MCU + own TPM + own isolated CAN-FD xcvr + own isolated RS-485
xcvr) on ONE PCB to conserve board area/connector count when several
sensors/actuators live at the same physical location (e.g. both EDFs of one
nacelle). Per stack i, the following nets are LOCAL (suffixed "_i", not
shared with any other stack): TPM_SPI_*, ENC_SPI_*, ENC_ERROR, CANFD_TX/RX,
CANFD_FLT_N, RS485_TX/RX/DE, MCU_NRST/VCORE/SWDIO/SWCLK, ISO_5V_CAN (each
ISOW1044 has its OWN integrated isolated DC-DC -- paralleling two chips'
independent regulated outputs together would be bad practice, so this stays
per-stack), and the per-stack FLEX_*/encoder headers. The following nets are
SHARED across every stack on the board (true multi-drop bus wiring, exactly
like real DroneCAN/RS-485 nodes on the same physical bus segment): +5V, +3V3,
GND (one shared regulator feeds every stack), CAN_H, CAN_L, ISO_GND_CAN
(every stack's isolated CAN reference must float together with the same bus
common-mode point), RS485_A, RS485_B, ISO_GND_485, ISO_3V3_485 (one shared
external isolated DC-DC feeds every ADM2795E's VDD2 -- VDD2 is a power INPUT
pin, so paralleling multiple chips off one real driver is fine, unlike
ISO_5V_CAN above). Only ONE pair of CAN-FD bus connectors + ONE pair of
RS-485 bus connectors + ONE termination resistor/jumper per bus is placed for
the whole board (true bus topology, not per-stack) -- see gen_shared_bus().

Deployment (see CAN-PERIPH-GW-1.md for the full rationale):
    * ENC-PORT / ENC-STBD  -- reads the local AK7455 nacelle tilt encoder
      (ENC-NACELLE-1 board) over its existing 7-wire SPI+ERROR pigtail
      (J_ENC, footprint Serenity-Custom:Pigtail_7W_DirectSolder, pad-for-pad
      compatible with ENC-NACELLE-1's own P1), republishing the signed angle
      on both isolated buses. Resolves the open avionics/WBS.md 1.9.1 /
      ENC-NACELLE-1.md "Host assignment" item: River/Simon no longer read the
      AK7455 SPI bus directly over a long wire run -- they receive the signed
      angle over CAN-FD/RS-485 like every other node.
    * ESC-{PORT,STBD}-{FWD,AFT} (one per EDF, 4x) -- the same board type
      bridges a VimDrones ESC S50 running AM32 "Standard" firmware
      (DSHOT/PWM command in, BDSHOT/EDSHOT telemetry out -- see
      https://dev.vimdrones.com/products/vimdrones_esc_s50/, informational
      reference only) through J_FLEX, so ESC command/telemetry is also
      TPM-signed and dual-bus.
    * Servo actuator gateway (nacelle tilt / nozzle-drive) -- FLEX_PWM_IO and
      FLEX_TTL_GPIO are plain bidirectional/timer-capable MCU GPIOs, so the
      same header also drives a standard servo PWM/TTL command out; direction
      is a firmware choice, not a hardware one.
    * DEPLOYED CONFIGURATION (2026-07-26): N_STACKS=4, one board per nacelle
      side (GW-PORT / GW-STBD) -- 2x ESC (fwd+aft EDF), 1x nacelle tilt
      servo, 1x AK7455 tilt encoder share the one PCB/one pair of bus
      connectors per side, instead of 4 separate single-stack boards.

Layout convention matches this project's own gen_Observer_carrier_sch.py: real
clean-room symbols are pulled from avionics/kicad/symbols/*.kicad_sym by
parse_real_symbol() and wired by PIN NUMBER via place_real(); electrical
connection is by coincident (x, y) between a pin and its global_label /
power symbol, not by drawn wires (same convention proven ERC-0 in Observer).

PRE-FAB GATES (tracked avionics/WBS.md, see CAN-PERIPH-GW-1.md):
    * MSPM0 GPIO -> peripheral pinmux (SPI0/SPI1/UART0/UART1/CAN/GPIO) is a
      defensible datasheet-capable assignment, not yet cross-checked against
      the MSPM0G3507 pinmux tables -- same caveat Observer's own carrier
      schematic already carries for this MCU.
    * ADM2795E VDD2 (isolated bus-side supply) needs a small isolated DC-DC
      module (e.g. a 1W SIP4 5V->5V or 5V->3.3V isolated converter) -- MPN
      not yet selected/verified against an OEM datasheet, so U_ISO_DCDC is
      placed as a labeled generic 4-pin block, not a claimed real part.
    * CAN-FD / RS-485 termination footprint uses a solder-jumper (open by
      default, matching VimDrones' own "120R switchable, default OFF").

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (Griffing Technology LLC)
AI-assist: Claude Fable 5 (Anthropic), 2026-07-25/26.
License: CC BY 4.0
"""

import re
import sys
from pathlib import Path

# ===========================================================================
# *** CHANGE THIS to set how many complete trust-module stacks (own MCU +
# own TPM + own isolated CAN-FD + own isolated RS-485) share one PCB. ***
# ===========================================================================
N_STACKS = 4

HERE = Path(__file__).resolve().parent
KICADS = HERE.parent / "kicads"
SYMDIR = HERE.parent.parent / "symbols"  # avionics/kicad/symbols

REAL_SYMS = {
    "MCU": (
        "Observer_MSPM0G3507_RGZ",
        "Package_DFN_QFN:QFN-48-1EP_7x7mm_P0.5mm_EP5.15x5.15mm",
    ),
    "TPM": (
        "Observer_SLB9672_TPM",
        "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm",
    ),
    "ISO": ("Observer_ISOW1044BDFMR", "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm"),
}

LANE_WIDTH = 220.0  # mm of X per stack lane

# ---------------------------------------------------------------------------
# Deterministic UUID helper
# ---------------------------------------------------------------------------
_uid_i = [0]


def _next_uid():
    _uid_i[0] += 1
    val = _uid_i[0]
    h = f"{val:032x}"
    return f"c6641000-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


# ---------------------------------------------------------------------------
# Generic s-expr helpers (reused verbatim, same shape as gen_Jayne.py /
# gen_Observer_carrier_sch.py -- this project's own proven infrastructure)
# ---------------------------------------------------------------------------
def _pin_def(ptype, shape, px, py, ang, length, name, number):
    return (
        f"      (pin {ptype} {shape} (at {px:.2f} {py:.2f} {ang}) (length {length:.2f})\n"
        f'        (name "{name}" (effects (font (size 1.016 1.016))))\n'
        f'        (number "{number}" (effects (font (size 1.016 1.016)))))'
    )


def lib_symbol_2pin_h(name):
    return (
        f"""  (symbol "{name}" (in_bom yes) (on_board yes)
    (property "Reference" "R" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{name}" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "{name}_0_1"
      (rectangle (start -2.54 -1.27) (end 2.54 1.27))
        )
    (symbol "{name}_1_1"
"""
        + _pin_def("passive", "line", -3.81, 0, 0, 1.27, "1", "1")
        + "\n"
        + _pin_def("passive", "line", 3.81, 0, 180, 1.27, "2", "2")
        + """
    )
  )"""
    )


def lib_symbol_conn_np(name, n, pin_names=None):
    pin_names = pin_names or [str(i + 1) for i in range(n)]
    half = (n - 1) * 1.27
    lines = [
        f'  (symbol "{name}" (in_bom yes) (on_board yes)',
        f'    (property "Reference" "J" (at 0 {-(half + 3.81):.2f} 0) (effects (font (size 1.27 1.27))))',
        f'    (property "Value" "{name}" (at 0 {(half + 3.81):.2f} 0) (effects (font (size 1.27 1.27))))',
        f'    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        f'    (symbol "{name}_0_1"',
        f"      (rectangle (start -2.54 {-half - 1.27:.2f}) (end 2.54 {half + 1.27:.2f})))",
        f'    (symbol "{name}_1_1"',
    ]
    for i in range(n):
        py = -half + i * 2.54
        lines.append(
            _pin_def("passive", "line", -5.08, py, 0, 2.54, pin_names[i], str(i + 1))
        )
    lines.append("    )")
    lines.append("  )")
    return "\n".join(lines)


def lib_symbol_generic_ic(name, footprint, datasheet, left, right, size=(15.24, 15.24)):
    hx, hy = size
    lines = [
        f'  (symbol "{name}" (in_bom yes) (on_board yes)',
        f'    (property "Reference" "U" (at 0 {-(hy + 3.81):.2f} 0) (effects (font (size 1.27 1.27))))',
        f'    (property "Value" "{name}" (at 0 {(hy + 3.81):.2f} 0) (effects (font (size 1.27 1.27))))',
        f'    (property "Footprint" "{footprint}" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        f'    (property "Datasheet" "{datasheet}" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        f'    (symbol "{name}_0_1"',
        f"      (rectangle (start {-hx:.2f} {-hy:.2f}) (end {hx:.2f} {hy:.2f})))",
        f'    (symbol "{name}_1_1"',
    ]
    n = len(left)
    start_y = -((n - 1) * 2.54) / 2.0
    for i, (pname, pnum, ptype) in enumerate(left):
        py = start_y + i * 2.54
        lines.append(_pin_def(ptype, "line", -(hx + 2.54), py, 0, 2.54, pname, pnum))
    n = len(right)
    start_y = -((n - 1) * 2.54) / 2.0
    for i, (pname, pnum, ptype) in enumerate(right):
        py = start_y + i * 2.54
        lines.append(_pin_def(ptype, "line", hx + 2.54, py, 180, 2.54, pname, pnum))
    lines.append("    )")
    lines.append("  )")
    return "\n".join(lines)


def _ic_pin_xy_bynum(left, right, pin_num, size):
    hx, hy = size
    for lst, side in ((left, "L"), (right, "R")):
        n = len(lst)
        start_y = -((n - 1) * 2.54) / 2.0
        for i, (pname, pnum, ptype) in enumerate(lst):
            if pnum == pin_num:
                local_py = start_y + i * 2.54
                dx = -(hx + 2.54) if side == "L" else (hx + 2.54)
                return (dx, -local_py, side)
    raise KeyError(f"pin #{pin_num!r} not found")


def glabel_pin_bynum(net_name, cx, cy, left, right, pin_num, size):
    dx, dy, side = _ic_pin_xy_bynum(left, right, pin_num, size)
    rot = 180 if side == "L" else 0
    return glabel(net_name, cx + dx, cy + dy, rot=rot)


def no_connect_pin_bynum(cx, cy, left, right, pin_num, size):
    dx, dy, _ = _ic_pin_xy_bynum(left, right, pin_num, size)
    return no_connect(cx + dx, cy + dy)


def _conn_pin_xy(n, idx0):
    half = (n - 1) * 1.27
    local_py = -half + idx0 * 2.54
    return (-5.08, -local_py)


def glabel_conn(net_name, cx, cy, n, idx0):
    dx, dy = _conn_pin_xy(n, idx0)
    return glabel(net_name, cx + dx, cy + dy, rot=180)


def lib_sym_power(name, bar_top=True):
    ybox = -1.27 if bar_top else 1.27
    yend = 1.27 if bar_top else -1.27
    pin_angle = 270 if bar_top else 90
    pin_y = 1.27 if bar_top else -1.27
    return (
        f"""  (symbol "{name}" (power) (in_bom no) (on_board no)
    (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "{name}" (at 0 {yend:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "{name}_0_1"
      (polyline (pts (xy -1.27 {ybox:.2f}) (xy 0 {yend:.2f}) (xy 1.27 {ybox:.2f}))
        (stroke (width 0) (type default)) (fill (type none))))
    (symbol "{name}_1_1"
"""
        + _pin_def("power_in", "line", 0.0, pin_y, pin_angle, 1.27, "~", "1")
        + """
  )
  )"""
    )


def lib_symbol_pwr_flag():
    return (
        '  (symbol "PWR_FLAG" (power) (in_bom no) (on_board no)\n'
        '    (property "Reference" "#FLG" (at 0 1.905 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
        '    (property "Value" "PWR_FLAG" (at 0 3.556 0) (effects (font (size 1.27 1.27))))\n'
        '    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
        '    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
        '    (symbol "PWR_FLAG_0_1"\n'
        "      (polyline (pts (xy 0 0) (xy 0 1.016) (xy -1.016 1.524) (xy 0 2.032) (xy 1.016 1.524) (xy 0 1.016))\n"
        "        (stroke (width 0) (type default)) (fill (type none))))\n"
        '    (symbol "PWR_FLAG_1_1"\n'
        + _pin_def("power_out", "line", 0.0, 0.0, 90, 0.0, "~", "1")
        + "\n    )\n  )"
    )


def pwr_flag(net, x, y):
    inst = "\n".join(
        [
            f'  (symbol (lib_id "PWR_FLAG") (at {x:.2f} {y:.2f} 0)',
            "    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)",
            f'    (uuid "{_next_uid()}")',
            f'    (property "Reference" "#FLG" (at {x:.2f} {y - 2.0:.2f} 0)',
            "      (effects (font (size 1.27 1.27)) (hide yes)))",
            f'    (property "Value" "PWR_FLAG" (at {x:.2f} {y + 2.0:.2f} 0)',
            "      (effects (font (size 1.27 1.27))))",
            f'    (pin "1" (uuid "{_next_uid()}"))',
            "  )",
        ]
    )
    return [inst, glabel(net, x, y, rot=90)]


def sym_inst(lib_id, ref, value, cx, cy, rot=0, footprint="", datasheet=""):
    return "\n".join(
        [
            f'  (symbol (lib_id "{lib_id}") (at {cx:.2f} {cy:.2f} {rot})',
            f"    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)",
            f'    (uuid "{_next_uid()}")',
            f'    (property "Reference" "{ref}" (at {cx:.2f} {cy - 3.81:.2f} {rot})',
            f"      (effects (font (size 1.27 1.27))))",
            f'    (property "Value" "{value}" (at {cx:.2f} {cy + 3.81:.2f} {rot})',
            f"      (effects (font (size 1.27 1.27))))",
            f'    (property "Footprint" "{footprint}" (at 0 0 0)',
            f"      (effects (font (size 1.27 1.27)) (hide yes)))",
            f'    (property "Datasheet" "{datasheet}" (at 0 0 0)',
            f"      (effects (font (size 1.27 1.27)) (hide yes)))",
            "  )",
        ]
    )


_PWR_BAR_TOP = {"+5V": True, "+3V3": True, "GND": False}


def pwr_sym(lib_id, tx, ty, rot=0):
    bar_top = _PWR_BAR_TOP.get(lib_id, True)
    pin_y = 1.27 if bar_top else -1.27
    if rot == 180:
        cx, cy = tx, ty - pin_y
    else:
        cx, cy = tx, ty + pin_y
        rot = 0
    return "\n".join(
        [
            f'  (symbol (lib_id "{lib_id}") (at {cx:.2f} {cy:.2f} {rot})',
            f"    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)",
            f'    (uuid "{_next_uid()}")',
            f'    (property "Reference" "#PWR" (at {cx:.2f} {cy:.2f} 0)',
            f"      (effects (font (size 1.27 1.27)) (hide yes)))",
            f'    (property "Value" "{lib_id}" (at {cx:.2f} {cy - 2.54:.2f} 0)',
            f"      (effects (font (size 1.27 1.27))))",
            f'    (property "Footprint" "" (at 0 0 0)',
            f"      (effects (font (size 1.27 1.27)) (hide yes)))",
            f'    (property "Datasheet" "" (at 0 0 0)',
            f"      (effects (font (size 1.27 1.27)) (hide yes)))",
            f'    (pin "1" (uuid "{_next_uid()}"))',
            "  )",
        ]
    )


def glabel(name, x, y, rot=0, shape="bidirectional"):
    return (
        f'  (global_label "{name}" (shape {shape}) (at {x:.2f} {y:.2f} {rot})\n'
        f"    (effects (font (size 1.016 1.016)))\n"
        f'    (uuid "{_next_uid()}")\n'
        f'    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {x:.2f} {y:.2f} 0)\n'
        f"      (effects (font (size 1.016 1.016)) (hide yes))))"
    )


def no_connect(x, y):
    return f'  (no_connect (at {x:.2f} {y:.2f}) (uuid "{_next_uid()}"))'


def text_note(txt, x, y, size=1.27):
    esc = txt.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return (
        f'  (text "{esc}" (at {x:.2f} {y:.2f} 0)\n'
        f"    (effects (font (size {size:.2f} {size:.2f})))\n"
        f'    (uuid "{_next_uid()}"))'
    )


def snap(v):
    return round(v / 1.27) * 1.27


# ---------------------------------------------------------------------------
# Real clean-room symbol import (verbatim from avionics/kicad/symbols/) --
# same mechanism as gen_Observer_carrier_sch.py's parse_real_symbol()/place_real()
# ---------------------------------------------------------------------------
def parse_real_symbol(name):
    src = (SYMDIR / f"{name}.kicad_sym").read_text()
    start = src.index(f'(symbol "{name}"')
    depth = 0
    end = None
    for i in range(start, len(src)):
        if src[i] == "(":
            depth += 1
        elif src[i] == ")":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    lib_block = src[start:end]

    pins = []
    unit = None
    lines = src.splitlines()
    i = 0
    while i < len(lines):
        mu = re.search(r'\(symbol "[^"]+_(\d+)_\d+"', lines[i])
        if mu:
            unit = int(mu.group(1))
        mp = re.match(
            r"\s*\(pin\s+(\w+)\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+(\d+)\)",
            lines[i],
        )
        if mp:
            etype = mp.group(1)
            x, y, ang = float(mp.group(2)), float(mp.group(3)), int(mp.group(4))
            pname = re.search(r'\(name "([^"]+)"', lines[i + 1]).group(1)
            pnum = re.search(r'\(number "([^"]+)"', lines[i + 2]).group(1)
            pins.append((pnum, pname, x, y, ang, etype, unit))
            i += 3
            continue
        i += 1
    return lib_block, pins


def sym_inst_unit(lib_id, ref, value, cx, cy, unit, footprint):
    return "\n".join(
        [
            f'  (symbol (lib_id "{lib_id}") (at {cx:.2f} {cy:.2f} 0)',
            f"    (unit {unit}) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)",
            f'    (uuid "{_next_uid()}")',
            f'    (property "Reference" "{ref}" (at {cx:.2f} {cy - 2.0:.2f} 0)',
            f"      (effects (font (size 1.27 1.27))))",
            f'    (property "Value" "{value}" (at {cx:.2f} {cy + 2.0:.2f} 0)',
            f"      (effects (font (size 1.27 1.27))))",
            f'    (property "Footprint" "{footprint}" (at 0 0 0)',
            f"      (effects (font (size 1.27 1.27)) (hide yes)))",
            "  )",
        ]
    )


def place_real(key, ref, value, unit_pos, netmap, pins):
    """netmap: pin NUMBER -> net name; missing -> no-connect."""
    lib_id, footprint = REAL_SYMS[key]
    unit_pos = {u: (snap(cx), snap(cy)) for u, (cx, cy) in unit_pos.items()}
    out = []
    for unit, (cx, cy) in unit_pos.items():
        out.append(sym_inst_unit(lib_id, ref, value, cx, cy, unit, footprint))
    for pnum, pname, x, y, ang, etype, unit in pins:
        if unit not in unit_pos:
            continue
        cx, cy = unit_pos[unit]
        sx, sy = cx + x, cy - y
        net = netmap.get(pnum)
        if net is None:
            out.append(no_connect(sx, sy))
        else:
            rot = 180 if ang == 0 else 0
            out.append(glabel(net, sx, sy, rot=rot))
    return out


# ===========================================================================
# ISOW1412 -- NEW clean-room symbol, 20-pin DFM (SOIC-20W compatible), pin
# table from TI ISOW1412/ISOW1432 datasheet (SLLSF86C) Table 7-1 "Pin
# Functions" (avionics/datasheets/isow1412.pdf), read directly for this
# design. Unlike ADM2795E (signal-only isolator, needs an external isolated
# DC-DC for its bus-side supply -- see the superseded note below), ISOW1412
# has an INTEGRATED isolated DC-DC converter, exactly like ISOW1044 does for
# CAN-FD -- so no external iso-DC-DC placeholder is needed here at all.
# Y/Z (driver out) and A/B (receiver in) are modeled "bidirectional" (not
# strictly the datasheet's O/O/I/I) because they are wired shorted
# (Y-to-A, Z-to-B) to run this full-duplex part in half-duplex mode on this
# project's established 2-wire RS485_A/RS485_B multi-drop bus -- the same
# ERC-modeling choice this project already makes for ISOW1044's CANH/CANL
# (also tri-statable shared-bus pins, also typed "bidirectional" in its own
# verified pinmap CSV).
#
# SUPERSEDED: this board originally used ADI ADM2795E (signal-only isolator)
# with a generic "MPN TBD" external isolated DC-DC placeholder for its VDD2
# rail. Replaced 2026-07-26 (user request: "switch all adm2795e rs485 chips
# on all nodes with ISOW1412 ... to provide both power and signal isolation
# on all nodes") -- this also closes the "isolated DC-DC MPN not selected"
# open item, since ISOW1412 needs no external DC-DC at all.
# ===========================================================================
RS485_SIZE = (15.24, 12.7)
RS485_L = [
    ("VIO", "1", "power_in"),
    ("D", "2", "input"),
    ("DE", "3", "input"),
    ("R", "4", "output"),
    ("RE_N", "5", "input"),
    ("GNDIO", "6", "power_in"),
    ("OUT", "7", "output"),
    ("EN_FLT", "8", "bidirectional"),
    ("VDD", "9", "power_in"),
    ("GND1", "10", "power_in"),
]
RS485_R = [
    ("GND2", "11", "power_in"),
    ("VISOOUT", "12", "power_out"),
    ("MODE", "13", "input"),
    ("IN", "14", "input"),
    ("GISOIN", "15", "power_in"),
    ("VISOIN", "16", "power_in"),
    ("Y", "17", "bidirectional"),
    ("Z", "18", "bidirectional"),
    ("B", "19", "bidirectional"),
    ("A", "20", "bidirectional"),
]
RS485_DATASHEET = "https://www.ti.com/lit/ds/symlink/isow1412.pdf"
RS485_FOOTPRINT = "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm"


# ===========================================================================
# Per-stack trust module: own MCU + own TPM + own isolated CAN-FD + own
# isolated RS-485 + own encoder/flex headers. idx is 1-based.
# ===========================================================================
def gen_stack(idx, mcu_pins, tpm_pins, iso_pins):
    s = f"_{idx}"
    off = (idx - 1) * LANE_WIDTH
    body = []
    body.append(
        text_note(
            f"=== Stack {idx}: U1{s} MCU / U2{s} TPM / U3{s} CAN-FD / U4{s} RS-485 ===",
            10 + off,
            90,
        )
    )

    # -- MCU --
    # Pinmux VERIFIED against the real MSPM0G3507 datasheet (SLASEX6C
    # Table 6-2 "Pin Attributes"), read directly on request (2026-07-26) --
    # replaces an earlier draft that assigned CANFD_TX/RX and several other
    # signals to arbitrary "next free pad" numbers without checking whether
    # that pin's alternate-function list actually offers the needed signal.
    # Real, checked assignments used here (pad# -> PAxx -> AF):
    #   CAN:    PA12 pad27 CAN_TX AF5 / PA13 pad28 CAN_RX AF6 (the device's
    #           ONLY CAN pin pair -- confirmed no other pin offers CAN_TX/RX)
    #   SPI0:   CS=PA2 pad8 AF3, SCK=PA6 pad12 AF3, MOSI=PA5 pad11 AF3,
    #           MISO=PA4 pad10 AF3 (TPM bus)
    #   SPI1:   CS=PA15 pad30 AF3, SCK=PA17 pad32 AF3, MOSI=PA18 pad33 AF3,
    #           MISO=PA16 pad31 AF3 (encoder bus)
    #   UART2:  TX=PB15 pad25 AF2, RX=PB16 pad26 AF2 (RS-485)
    #   UART0:  TX=PA0 pad1 AF2, RX=PA1 pad2 AF2 (flex header)
    #   Remaining signals (PIRQ/RESET/ERROR/FLT/DE/GPIO) are plain digital
    #   I/O -- any pin works regardless of AF list, so free pads were used.
    mcu_netmap = {
        "1": f"FLEX_UART_TX{s}",
        "2": f"FLEX_UART_RX{s}",
        "4": f"MCU_NRST{s}",
        "6": "+3V3",
        "7": "GND",
        "8": f"TPM_SPI_CS{s}",
        "9": f"TPM_PIRQ{s}",
        "10": f"TPM_SPI_MISO{s}",
        "11": f"TPM_SPI_MOSI{s}",
        "12": f"TPM_SPI_SCK{s}",
        "13": f"TPM_RESET_N{s}",
        "14": f"RS485_DE{s}",
        "15": f"FLEX_PWM_IO{s}",
        "16": f"RS485_FLT_N{s}",
        "20": f"FLEX_BSHOT_IO{s}",
        "25": f"RS485_TX{s}",
        "26": f"RS485_RX{s}",
        "27": f"CANFD_TX{s}",
        "28": f"CANFD_RX{s}",
        "29": f"ENC_ERROR{s}",
        "30": f"ENC_SPI_CS{s}",
        "31": f"ENC_SPI_MISO{s}",
        "32": f"ENC_SPI_SCK{s}",
        "33": f"ENC_SPI_MOSI{s}",
        "34": f"MCU_SWDIO{s}",
        "35": f"MCU_SWCLK{s}",
        "43": f"CANFD_FLT_N{s}",
        "44": f"FLEX_TTL_GPIO{s}",
        "48": f"MCU_VCORE{s}",
        "49": "GND",
    }
    body += place_real(
        "MCU", f"U1{s}", "TI MSPM0G3507", {1: (110 + off, 165)}, mcu_netmap, mcu_pins
    )
    body.append(sym_inst("R_Generic", f"R_NRST{s}", "10k", 70 + off, 145, footprint="Resistor_SMD:R_0402_1005Metric"))
    body.append(glabel("+3V3", 66.19 + off, 145, rot=180))
    body.append(glabel(f"MCU_NRST{s}", 73.81 + off, 145, rot=0))
    body.append(sym_inst("C_Generic", f"C_VCORE{s}", "1uF", 70 + off, 155, footprint="Capacitor_SMD:C_0402_1005Metric"))
    body.append(glabel(f"MCU_VCORE{s}", 66.19 + off, 155, rot=180))
    body.append(glabel("GND", 73.81 + off, 155, rot=0))
    body.append(sym_inst("C_Generic", f"C_MCU1{s}", "100nF", 70 + off, 165, footprint="Capacitor_SMD:C_0402_1005Metric"))
    body.append(glabel("+3V3", 66.19 + off, 165, rot=180))
    body.append(glabel("GND", 73.81 + off, 165, rot=0))
    body.append(
        sym_inst(
            "Conn_JST_GH_04P", f"J_SWD{s}", "SWD: DIO/CLK/NRST/GND", 160 + off, 145,
            footprint="Connector_JST:JST_GH_BM04B-GHS-TBT_1x04-1MP_P1.25mm_Vertical",
        )
    )
    body.append(glabel_conn(f"MCU_SWDIO{s}", 160 + off, 145, 4, 0))
    body.append(glabel_conn(f"MCU_SWCLK{s}", 160 + off, 145, 4, 1))
    body.append(glabel_conn(f"MCU_NRST{s}", 160 + off, 145, 4, 2))
    body.append(glabel_conn("GND", 160 + off, 145, 4, 3))

    # -- TPM --
    tpm_netmap = {
        "1": "+3V3", "2": "GND", "8": "+3V3", "9": "GND", "14": "+3V3", "16": "GND",
        "17": f"TPM_RESET_N{s}", "18": f"TPM_PIRQ{s}", "19": f"TPM_SPI_SCK{s}",
        "20": f"TPM_SPI_CS{s}", "21": f"TPM_SPI_MOSI{s}", "22": "+3V3", "23": "GND",
        "24": f"TPM_SPI_MISO{s}", "32": "GND",
    }
    body += place_real(
        "TPM", f"U2{s}", "Infineon SLB9672 TPM2.0", {1: (110 + off, 230)}, tpm_netmap, tpm_pins
    )
    body.append(sym_inst("C_Generic", f"C_TPM1{s}", "100nF", 145 + off, 220, footprint="Capacitor_SMD:C_0402_1005Metric"))
    body.append(glabel("+3V3", 141.19 + off, 220, rot=180))
    body.append(glabel("GND", 148.81 + off, 220, rot=0))
    body.append(sym_inst("C_Generic", f"C_TPM2{s}", "1uF", 145 + off, 226, footprint="Capacitor_SMD:C_0402_1005Metric"))
    body.append(glabel("+3V3", 141.19 + off, 226, rot=180))
    body.append(glabel("GND", 148.81 + off, 226, rot=0))
    body.append(sym_inst("R_Generic", f"R_TPM_RST{s}", "10k", 145 + off, 232, footprint="Resistor_SMD:R_0402_1005Metric"))
    body.append(glabel("+3V3", 141.19 + off, 232, rot=180))
    body.append(glabel(f"TPM_RESET_N{s}", 148.81 + off, 232, rot=0))

    # -- Isolated CAN-FD (own integrated isolated DC-DC -> per-stack ISO_5V_CAN{s}) --
    iso_netmap = {
        "1": "+3V3", "3": f"CANFD_TX{s}", "4": "GND", "5": f"CANFD_RX{s}", "6": "GND",
        "8": f"CANFD_FLT_N{s}", "9": "+3V3", "10": "GND",
        "11": "ISO_GND_CAN", "12": f"ISO_5V_CAN{s}", "13": f"ISO_5V_CAN{s}",
        "15": "ISO_GND_CAN", "16": "ISO_GND_CAN", "17": "ISO_GND_CAN",
        "18": "CAN_L", "19": "CAN_H", "20": f"ISO_5V_CAN{s}",
    }
    body += place_real(
        "ISO", f"U3{s}", "TI ISOW1044BDFMR", {1: (110 + off, 330)}, iso_netmap, iso_pins
    )
    body.append(sym_inst("C_Generic", f"C_ISO1{s}", "100nF", 145 + off, 310, footprint="Capacitor_SMD:C_0402_1005Metric"))
    body.append(glabel("+3V3", 141.19 + off, 310, rot=180))
    body.append(glabel("GND", 148.81 + off, 310, rot=0))
    body.append(sym_inst("C_Generic", f"C_ISO2{s}", "1uF", 145 + off, 316, footprint="Capacitor_SMD:C_0402_1005Metric"))
    body.append(glabel(f"ISO_5V_CAN{s}", 141.19 + off, 316, rot=180))
    body.append(glabel("ISO_GND_CAN", 148.81 + off, 316, rot=0))
    # NOTE: no PWR_FLAG needed on ISO_5V_CAN{s} -- pin 12 VISOOUT is itself a
    # real "power_out" pin (this chip's own internal isolated DC-DC output).
    # GND2/GISOIN (power_in / reference pins, not outputs) go straight onto
    # the shared board-level ISO_GND_CAN bus reference net -- every stack's
    # isolated CAN side must float together with the same bus common-mode
    # point, and tying multiple power_IN pins to one net is not an ERC
    # conflict (only paralleling multiple power_OUT pins would be).

    # -- Isolated RS-485 (ISOW1412 -- own integrated isolated DC-DC, per
    # stack, same reasoning as ISO_5V_CAN above: don't parallel two chips'
    # independent regulated outputs. Y/Z shorted to A/B to run this
    # full-duplex part in half-duplex mode on the shared 2-wire bus.) --
    rs_cx, rs_cy = 110 + off, 420
    rs_netmap = {
        "1": "+3V3", "2": f"RS485_TX{s}", "3": f"RS485_DE{s}", "4": f"RS485_RX{s}",
        "5": f"RS485_DE{s}", "6": "GND", "8": f"RS485_FLT_N{s}", "9": "+3V3",
        "10": "GND", "11": "ISO_GND_485", "12": f"ISO_3V3_485{s}",
        "13": "ISO_GND_485", "15": "ISO_GND_485", "16": f"ISO_3V3_485{s}",
        "17": "RS485_A", "18": "RS485_B", "19": "RS485_B", "20": "RS485_A",
    }
    body.append(
        sym_inst("GW_ISOW1412", f"U4{s}", "TI ISOW1412", rs_cx, rs_cy, footprint=RS485_FOOTPRINT, datasheet=RS485_DATASHEET)
    )
    for pname, pnum, ptype in RS485_L + RS485_R:
        net = rs_netmap.get(pnum)
        if net is None:
            body.append(no_connect_pin_bynum(rs_cx, rs_cy, RS485_L, RS485_R, pnum, RS485_SIZE))
        else:
            body.append(glabel_pin_bynum(net, rs_cx, rs_cy, RS485_L, RS485_R, pnum, RS485_SIZE))
    body.append(sym_inst("C_Generic", f"C_RS1{s}", "100nF", 145 + off, 405, footprint="Capacitor_SMD:C_0402_1005Metric"))
    body.append(glabel("+3V3", 141.19 + off, 405, rot=180))
    body.append(glabel("GND", 148.81 + off, 405, rot=0))
    body.append(sym_inst("C_Generic", f"C_RS2{s}", "100nF", 145 + off, 411, footprint="Capacitor_SMD:C_0402_1005Metric"))
    body.append(glabel(f"ISO_3V3_485{s}", 141.19 + off, 411, rot=180))
    body.append(glabel("ISO_GND_485", 148.81 + off, 411, rot=0))

    # -- J_ENC: AK7455 tilt-encoder input (ENC-NACELLE-1 pigtail-compatible) --
    body.append(
        sym_inst(
            "Pigtail_7W_DirectSolder", f"J_ENC{s}",
            "7W direct-solder, mates ENC-NACELLE-1 P1 pigtail 1:1", 60 + off, 500,
            footprint="Serenity-Custom:Pigtail_7W_DirectSolder",
        )
    )
    enc_pins = ["GND", f"ENC_SPI_CS{s}", f"ENC_SPI_SCK{s}", f"ENC_SPI_MOSI{s}", f"ENC_SPI_MISO{s}", "+3V3", f"ENC_ERROR{s}"]
    for i, net in enumerate(enc_pins):
        body.append(glabel_conn(net, 60 + off, 500, 7, i))

    # -- J_FLEX: flexible UART/TTL/PWM/BSHOT sensor+actuator header --
    body.append(
        sym_inst(
            "PinHeader_1x08", f"J_FLEX{s}", "1x08 2.54mm: TX/RX/TTL/PWM/BSHOT/+5V/+3V3/GND",
            60 + off, 580, footprint="Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical",
        )
    )
    flex_pins = [f"FLEX_UART_TX{s}", f"FLEX_UART_RX{s}", f"FLEX_TTL_GPIO{s}", f"FLEX_PWM_IO{s}", f"FLEX_BSHOT_IO{s}", "+5V", "+3V3", "GND"]
    for i, net in enumerate(flex_pins):
        body.append(glabel_conn(net, 60 + off, 580, 8, i))

    return body


# ===========================================================================
# Shared, board-level sections: power (Section A) and the two physical
# multi-drop buses (CAN-FD, RS-485) with their single termination network --
# generated ONCE regardless of N_STACKS.
# ===========================================================================
def gen_power_section():
    body = []
    body.append(text_note("=== Section A: Power Input + 3V3 Rail (shared by every stack) ===", 10, 20))
    body.append(
        sym_inst(
            "Conn_JST_GH_02P", "J_PWR", "JST-GH 2P +5V/GND (local supply)", 25, 32,
            footprint="Connector_JST:JST_GH_BM02B-GHS-TBT_1x02-1MP_P1.25mm_Vertical",
        )
    )
    body.append(glabel_conn("+5V", 25, 32, 2, 0))
    body.append(glabel_conn("GND", 25, 32, 2, 1))
    body += pwr_flag("+5V", 25, 15)

    body.append(
        sym_inst(
            "TLV62569_DBV", "U_REG_3V3", "TLV62569DBVR -> +3V3", 25, 48,
            footprint="Package_TO_SOT_SMD:SOT-23-6",
            datasheet="https://www.ti.com/lit/ds/symlink/tlv62569.pdf",
        )
    )
    L = [("EN", "1", "input"), ("GND", "2", "power_in"), ("VIN", "4", "power_in")]
    R = [("SW", "3", "output"), ("FB", "5", "input"), ("PG", "6", "output")]
    SZ = (7.62, 5.08)
    body.append(glabel_pin_bynum("+5V", 25, 48, L, R, "1", SZ))
    body.append(glabel_pin_bynum("GND", 25, 48, L, R, "2", SZ))
    body.append(glabel_pin_bynum("+5V", 25, 48, L, R, "4", SZ))
    body.append(glabel_pin_bynum("U_REG_SW", 25, 48, L, R, "3", SZ))
    body.append(glabel_pin_bynum("U_REG_FB", 25, 48, L, R, "5", SZ))
    body.append(no_connect_pin_bynum(25, 48, L, R, "6", SZ))

    body.append(sym_inst("L_Generic", "L1", "2.2uH", 45, 45.46, footprint="Inductor_SMD:L_Taiyo-Yuden_NR-20xx"))
    body.append(glabel("U_REG_SW", 41.19, 45.46, rot=180))
    body.append(glabel("+3V3", 48.81, 45.46, rot=0))
    body.append(sym_inst("R_Generic", "R_FBT", "10k", 45, 54, footprint="Resistor_SMD:R_0402_1005Metric"))
    body.append(glabel("+3V3", 41.19, 54, rot=180))
    body.append(glabel("U_REG_FB", 48.81, 54, rot=0))
    body.append(sym_inst("R_Generic", "R_FBB", "20k", 45, 59, footprint="Resistor_SMD:R_0402_1005Metric"))
    body.append(glabel("U_REG_FB", 41.19, 59, rot=180))
    body.append(glabel("GND", 48.81, 59, rot=0))
    body.append(sym_inst("C_Generic", "C_IN", "10uF", 9, 48, footprint="Capacitor_SMD:C_0402_1005Metric"))
    body.append(glabel("+5V", 5.19, 48, rot=180))
    body.append(glabel("GND", 12.81, 48, rot=0))
    body.append(sym_inst("C_Generic", "C_OUT", "22uF", 55, 45.46, footprint="Capacitor_SMD:C_0402_1005Metric"))
    body.append(glabel("+3V3", 51.19, 45.46, rot=180))
    body.append(glabel("GND", 58.81, 45.46, rot=0))
    body += pwr_flag("+3V3", 65, 45.46)
    body += pwr_flag("GND", 65, 48)
    return body


def gen_shared_bus(n_stacks):
    body = []
    lane_right = 10 + (n_stacks - 1) * LANE_WIDTH + 190  # clear of the last stack lane
    bus_x = lane_right + 40

    body.append(text_note("=== Shared CAN-FD bus: one physical multi-drop segment for every stack ===", bus_x, 280))
    body.append(sym_inst("Conn_JST_GH_03P", "J_CAN_IN", "CAN-FD trunk IN (CANH/CANL/GND)", bus_x, 300, footprint="Connector_JST:JST_GH_BM03B-GHS-TBT_1x03-1MP_P1.25mm_Vertical"))
    body.append(glabel_conn("CAN_H", bus_x, 300, 3, 0))
    body.append(glabel_conn("CAN_L", bus_x, 300, 3, 1))
    body.append(glabel_conn("ISO_GND_CAN", bus_x, 300, 3, 2))
    body.append(sym_inst("Conn_JST_GH_03P", "J_CAN_OUT", "CAN-FD trunk OUT (CANH/CANL/GND)", bus_x + 40, 300, footprint="Connector_JST:JST_GH_BM03B-GHS-TBT_1x03-1MP_P1.25mm_Vertical"))
    body.append(glabel_conn("CAN_H", bus_x + 40, 300, 3, 0))
    body.append(glabel_conn("CAN_L", bus_x + 40, 300, 3, 1))
    body.append(glabel_conn("ISO_GND_CAN", bus_x + 40, 300, 3, 2))
    body.append(sym_inst("R_Generic", "R_CANTERM", "120R", bus_x, 330, footprint="Resistor_SMD:R_0402_1005Metric"))
    body.append(glabel("CAN_H", bus_x - 3.81, 330, rot=180))
    body.append(glabel("CANTERM_MID", bus_x + 3.81, 330, rot=0))
    body.append(sym_inst("SJ_Generic", "SJ1", "open by default (VimDrones-style switchable 120R term)", bus_x + 20, 330, footprint="Jumper:SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm"))
    body.append(glabel("CANTERM_MID", bus_x + 16.19, 330, rot=180))
    body.append(glabel("CAN_L", bus_x + 23.81, 330, rot=0))
    body += pwr_flag("ISO_GND_CAN", bus_x + 60, 300)

    body.append(text_note("=== Shared RS-485 bus: one physical multi-drop segment for every stack ===", bus_x, 380))
    body.append(sym_inst("Conn_JST_GH_03P", "J_RS485_IN", "RS-485 trunk IN (A/B/GND)", bus_x, 400, footprint="Connector_JST:JST_GH_BM03B-GHS-TBT_1x03-1MP_P1.25mm_Vertical"))
    body.append(glabel_conn("RS485_A", bus_x, 400, 3, 0))
    body.append(glabel_conn("RS485_B", bus_x, 400, 3, 1))
    body.append(glabel_conn("ISO_GND_485", bus_x, 400, 3, 2))
    body.append(sym_inst("Conn_JST_GH_03P", "J_RS485_OUT", "RS-485 trunk OUT (A/B/GND)", bus_x + 40, 400, footprint="Connector_JST:JST_GH_BM03B-GHS-TBT_1x03-1MP_P1.25mm_Vertical"))
    body.append(glabel_conn("RS485_A", bus_x + 40, 400, 3, 0))
    body.append(glabel_conn("RS485_B", bus_x + 40, 400, 3, 1))
    body.append(glabel_conn("ISO_GND_485", bus_x + 40, 400, 3, 2))
    body.append(sym_inst("R_Generic", "R_485TERM", "120R", bus_x, 430, footprint="Resistor_SMD:R_0402_1005Metric"))
    body.append(glabel("RS485_A", bus_x - 3.81, 430, rot=180))
    body.append(glabel("TERM485_MID", bus_x + 3.81, 430, rot=0))
    body.append(sym_inst("SJ_Generic", "SJ2", "open by default", bus_x + 20, 430, footprint="Jumper:SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm"))
    body.append(glabel("TERM485_MID", bus_x + 16.19, 430, rot=180))
    body.append(glabel("RS485_B", bus_x + 23.81, 430, rot=0))
    body += pwr_flag("ISO_GND_485", bus_x + 60, 400)
    # No shared external isolated DC-DC needed -- each stack's own ISOW1412
    # (U4_i) has an integrated isolated DC-DC (see gen_stack()), same as
    # ISOW1044 already does for CAN-FD.
    return body


def gen_sch():
    lib = [
        "  (lib_symbols",
        lib_symbol_pwr_flag(),
        lib_sym_power("+5V", bar_top=True),
        lib_sym_power("+3V3", bar_top=True),
        lib_sym_power("GND", bar_top=False),
        lib_symbol_2pin_h("R_Generic"),
        lib_symbol_2pin_h("C_Generic"),
        lib_symbol_2pin_h("L_Generic"),
        lib_symbol_2pin_h("SJ_Generic"),
        lib_symbol_conn_np("Conn_JST_GH_02P", 2, ["1", "2"]),
        lib_symbol_conn_np("Conn_JST_GH_03P", 3, ["1", "2", "3"]),
        lib_symbol_conn_np("Conn_JST_GH_04P", 4, ["1", "2", "3", "4"]),
        lib_symbol_conn_np("Pigtail_7W_DirectSolder", 7),
        lib_symbol_conn_np("PinHeader_1x08", 8, ["1", "2", "3", "4", "5", "6", "7", "8"]),
        lib_symbol_generic_ic("GW_ISOW1412", RS485_FOOTPRINT, RS485_DATASHEET, left=RS485_L, right=RS485_R, size=RS485_SIZE),
        lib_symbol_generic_ic(
            "TLV62569_DBV", "Package_TO_SOT_SMD:SOT-23-6", "https://www.ti.com/lit/ds/symlink/tlv62569.pdf",
            left=[("EN", "1", "input"), ("GND", "2", "power_in"), ("VIN", "4", "power_in")],
            right=[("SW", "3", "output"), ("FB", "5", "input"), ("PG", "6", "output")],
            size=(7.62, 5.08),
        ),
    ]
    # Pull in the real, already-verified clean-room symbols verbatim.
    mcu_block, mcu_pins = parse_real_symbol("Observer_MSPM0G3507_RGZ")
    tpm_block, tpm_pins = parse_real_symbol("Observer_SLB9672_TPM")
    iso_block, iso_pins = parse_real_symbol("Observer_ISOW1044BDFMR")
    lib += [mcu_block, tpm_block, iso_block]
    lib.append("  )")

    body = []
    body += gen_power_section()
    for i in range(1, N_STACKS + 1):
        body += gen_stack(i, mcu_pins, tpm_pins, iso_pins)
    body += gen_shared_bus(N_STACKS)

    header = [
        "(kicad_sch (version 20240101) (generator eeschema)",
        '  (paper "A2")',
        "  (title_block",
        f'    (title "CAN-PERIPH-GW-1 -- TPM-secured Dual-Isolated-Bus (CAN-FD + RS-485) Peripheral Gateway ({N_STACKS}x stack)") (date "2026-07-26") (rev "1") (company "Griffing Technology LLC")',
        '    (comment 1 "Serenity UAV -- SKIPPER-CAN-PERIPH-GW-PCB -- standalone board, not a PocketBeagle 2 Industrial cape")',
        '    (comment 2 "Copyright 2026 Steve Griffing PE(CSE) CISSP-ISSEP CPP | Griffing Technology LLC")',
        '    (comment 3 "License: CC BY 4.0  |  creativecommons.org/licenses/by/4.0")',
        '    (comment 4 "Concept remix of VimDrones AP_Periph Pico (informational ref only, GPLv3 -- no source copied); see CAN-PERIPH-GW-1.md")',
        "  )",
    ]
    footer = [")"]
    return "\n".join(header + lib + body + footer)


if __name__ == "__main__":
    out = KICADS / "CAN-PERIPH-GW-1.kicad_sch"
    content = gen_sch()
    out.write_text(content, encoding="utf-8")
    print(f"  Written: {out}  ({len(content):,} bytes, N_STACKS={N_STACKS})")
