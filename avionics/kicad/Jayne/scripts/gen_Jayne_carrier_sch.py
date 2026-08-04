#!/usr/bin/env python3


# ---------------------------------------------------------------------------
# SUPERSEDED PART WARNING (2026-08-03)
#
# This generator still emits the MSPM0G3507 and/or SLB9670VQ2.0.  Both were
# retargeted on 2026-08-03:
#     MSPM0G3507  ->  MSPM0G3519-Q1 (M0G3519QRGZRQ1, RGZ-48)   on Jayne
#                 ->  MSPM0G3518-Q1 (M0G3518QRHBRQ1, RHB-32)   on the gateway and Kaylee
#     SLB9670VQ2.0 -> SLB 9672AU2.0 (PG-UQFN-32-1,-2)          on all three
# See REFERENCES.md REF-SENSOR-013 / REF-SEC-002 and TODO.md 1.2d.
#
# Do NOT re-run this script against the committed schematic: it has drifted
# from the as-placed design and regenerating would revert the retarget.  Apply
# changes with avionics/kicad/retarget_mspm0g351x_slb9672.py instead.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
gen_Jayne_carrier_sch.py -- author Jayne.kicad_sch in the SoM end-state.
=============================================================================
Supersedes the placeholder vision/control sections of gen_Jayne.py (which used
"2-row placeholder" generic-IC symbols for U1 AM62A7 / U_PMIC / U2 / U3 / U4 /
U5).  This generator instantiates the REAL clean-room symbols authored from the
primary datasheets/manual:

  U_SOM  Jayne_SoM_PCM071      PHYTEC phyCORE-AM62x PCM-071 (240-pad, 2xBTH-060)
  U2     Jayne_KSZ9477         Microchip KSZ9477 7-port switch (128-TQFP-EP)
  U3     Jayne_MSPM0G3507_RGZ  TI MSPM0G3507 MCU (48-VQFN)
  U4     Jayne_ISOW1044BDFMR   TI ISOW1044BDFMR isolated CAN-FD (20-DFM/SOIC-20)
  U5     Jayne_SLB9670_TPM     Infineon SLB9670 TPM 2.0 (32-VQFN)

Design decisions locked with the user 2026-07-13:
  * The 240-pin PCM-071 connector takes 5V IN only and hands NO 3V3/2V5/1V2 rail
    back to the carrier (PHYTEC HW manual L-1038e.A5 §5.1: the carrier must feed
    >=1000 mA at 5V).  So the carrier generates its own rails from +5V:
      U_REG_3V3  TI TLV62569 buck  -> +3V3 (KSZ VDDIO, MSPM0, TPM, ISOW VIO, cam)
      U_REG_1V2  TI TLV62569 buck  -> +1V2 (KSZ AVDDL/DVDDL/VDDLS)
      U_REG_2V5  TI TLV75725 LDO   -> +2V5 (KSZ AVDDH/VDDHS)
  * TPM + KSZ management stay on the MSPM0G3507 SPI (carrier control-plane
    unchanged); the SoM simply takes over the nets the old AM62A7 placeholder
    drove (RGMII to the switch, MDIO left NC, CSI-2, camera I2C, UART0 to the
    MCU, PORz, power/GND).

Wiring is by SIGNAL NAME against each symbol's real pin table (parsed live from
the .kicad_sym files) -- no hand-entered pin numbers.  Pins with no carrier net
get an explicit no-connect flag so ERC is clean and the PCB pad carries no net
(no spurious unconnected_items).

The unchanged sections (JST/DS connectors, Ethernet+CAN EMI-hardening chain,
laser driver, ToF interface, PGND/GND single-point bond) reuse gen_Jayne.py's
own verified helpers via import.

PRE-FAB GATES (tracked TODO.md 1.2c):
  * RGMII SoM(MAC) <-> KSZ port6 crossover is wired MAC-to-MAC (SoM TX -> KSZ
    port6 RX and vice-versa); KSZ port6 RGMII MAC/PHY mode strap + delay config
    needs firmware/HW sign-off before fab.
  * MSPM0 GPIO->peripheral pinmux (CAN/UART/SPI/laser) is a defensible datasheet
    assignment; confirm against the final MSPM0 pinmux/firmware.
  * Regulator feedback-divider values, inductors, and the 2V5 LDO current margin
    are first-pass; verify against each TI datasheet's design procedure.

Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  (Griffing Technology LLC)
AI-assist: Claude Fable 5 (Anthropic) -- clean-room carrier schematic, 2026-07-13.
License: CC BY 4.0
"""

import re
import sys
from pathlib import Path

import gen_Jayne as gj  # helper library (glabel, pwr_sym, lib symbols, etc.)

HERE = Path(__file__).resolve().parent
KICADS = HERE.parent / "kicads"
SYMDIR = HERE.parent.parent / "symbols"  # avionics/kicad/symbols

REAL_SYMS = {
    "SOM": ("Jayne_SoM_PCM071", "Jayne:phyCORE-AM62x_PCM071_2xBTH-060"),
    "KSZ": ("Jayne_KSZ9477", "Jayne:TQFP-128-1EP_KSZ9477_14x14mm_P0.4mm_EP10x10"),
    "MSP": (
        "Jayne_MSPM0G3507_RGZ",
        "Package_DFN_QFN:QFN-48-1EP_7x7mm_P0.5mm_EP5.15x5.15mm",
    ),
    "ISO": ("Jayne_ISOW1044BDFMR", "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm"),
    "TPM": (
        "Jayne_SLB9670_TPM",
        "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm",
    ),
}

# ---------------------------------------------------------------------------
# ADM2795E -- NEW clean-room symbol (added 2026-07-26, Section H: isolated
# RS-485). Pin table from the real Analog Devices ADM2795E datasheet (Rev D)
# Table 10 "Pin Function Descriptions" (avionics/datasheets/adm2795e.pdf),
# read directly for this design. The "ADM2795EBRWZ" symbol already embedded
# in Wash.kicad_sch / Zoe.kicad_sch has WRONG pin numbers (a pin 17 on a
# 16-pin part; a duplicate pin 20 on two different names) -- evidently cloned
# from the ISOW1044 (20-pin) template and never corrected. NOT reused here;
# flagged in REFERENCES.md / TODO.md for correction there.
#
# SUPERSEDED 2026-07-26: originally ADI ADM2795E (signal-only isolator,
# needs an external isolated DC-DC for VDD2). Replaced with TI ISOW1412
# (user request: "switch all adm2795e rs485 chips on all nodes with
# ISOW1412 ... to provide both power and signal isolation") -- pin table
# from TI ISOW1412/ISOW1432 datasheet (SLLSF86C) Table 7-1, read directly.
# ISOW1412 has an INTEGRATED isolated DC-DC (like ISOW1044 already has for
# CAN-FD), so no external iso-DC-DC placeholder is needed at all -- this
# also removes Jayne's own "ISO_DCDC_1W_GENERIC ... MPN TBD" open item.
# Y/Z (driver out) and A/B (receiver in) are modeled "bidirectional" and
# wired shorted (Y-A, Z-B) to run this full-duplex part in half-duplex mode
# on the project's 2-wire RS485_A/RS485_B bus -- same modeling choice this
# project already uses for ISOW1044's CANH/CANL.
# ---------------------------------------------------------------------------
ADM_SIZE = (15.24, 12.7)
ADM_L = [
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
ADM_R = [
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
ADM_DATASHEET = "https://www.ti.com/lit/ds/symlink/isow1412.pdf"
ADM_FOOTPRINT = "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm"


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
    return gj.glabel(net_name, cx + dx, cy + dy, rot=rot)


def no_connect_pin_bynum(cx, cy, left, right, pin_num, size):
    dx, dy, _ = _ic_pin_xy_bynum(left, right, pin_num, size)
    return no_connect(cx + dx, cy + dy)


# ---------------------------------------------------------------------------
# Real-symbol parsing (pin table + library block extraction)
# ---------------------------------------------------------------------------
def parse_real_symbol(name):
    """Return (lib_block_text, pins) for a clean-room symbol file.

    pins = [(number, name, x, y, angle, etype, unit), ...] in symbol-local
    (Y-up) coordinates.  lib_block_text is the top-level `(symbol "NAME" ...)`
    s-expression, ready to drop into a schematic (lib_symbols ...) block."""
    src = (SYMDIR / f"{name}.kicad_sym").read_text()
    # Extract the outermost (symbol "NAME" ...) block by brace balancing.
    start = src.index(f'(symbol "{name}"')
    depth = 0
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


def no_connect(x, y):
    return f'  (no_connect (at {x:.2f} {y:.2f}) (uuid "{gj._next_uid()}"))'


def snap(v):
    """Snap a coordinate to the 1.27 mm (50 mil) connection grid."""
    return round(v / 1.27) * 1.27


def lib_symbol_pwr_flag():
    """PWR_FLAG — marks a net as power-driven (one power_output pin) so ERC's
    power_pin_not_driven check is satisfied on rails fed from connectors /
    regulator outputs typed as ordinary outputs."""
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
        + gj._pin_def("power_out", "line", 0.0, 0.0, 90, 0.0, "~", "1")
        + "\n    )\n  )"
    )


def pwr_flag(net, x, y):
    """Place a PWR_FLAG and a coincident global label so `net` is power-driven."""
    x, y = snap(x), snap(y)
    inst = "\n".join(
        [
            f'  (symbol (lib_id "PWR_FLAG") (at {x:.2f} {y:.2f} 0)',
            "    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)",
            f'    (uuid "{gj._next_uid()}")',
            f'    (property "Reference" "#FLG" (at {x:.2f} {y - 2.0:.2f} 0)',
            "      (effects (font (size 1.27 1.27)) (hide yes)))",
            f'    (property "Value" "PWR_FLAG" (at {x:.2f} {y + 2.0:.2f} 0)',
            "      (effects (font (size 1.27 1.27))))",
            f'    (pin "1" (uuid "{gj._next_uid()}"))',
            "  )",
        ]
    )
    return [inst, gj.glabel(net, x, y, rot=90)]


def sym_inst_unit(lib_id, ref, value, cx, cy, unit, footprint):
    """Instance one UNIT of a (possibly multi-unit) symbol."""
    return "\n".join(
        [
            f'  (symbol (lib_id "{lib_id}") (at {cx:.2f} {cy:.2f} 0)',
            f"    (unit {unit}) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)",
            f'    (uuid "{gj._next_uid()}")',
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
    """Emit all units of a real symbol plus a global label (or no-connect) on
    every pin.  netmap maps pin NUMBER -> net name; missing/None -> no-connect.
    unit_pos maps unit -> (cx, cy)."""
    lib_id, footprint = REAL_SYMS[key]
    unit_pos = {u: (snap(cx), snap(cy)) for u, (cx, cy) in unit_pos.items()}
    out = []
    for unit, (cx, cy) in unit_pos.items():
        out.append(sym_inst_unit(lib_id, ref, value, cx, cy, unit, footprint))
    for pnum, pname, x, y, ang, etype, unit in pins:
        if unit not in unit_pos:
            continue
        cx, cy = unit_pos[unit]
        sx, sy = cx + x, cy - y  # symbol Y-up -> sheet Y-down
        net = netmap.get(pnum)
        if net is None:
            out.append(no_connect(sx, sy))
        else:
            rot = 180 if ang == 0 else 0
            out.append(gj.glabel(net, sx, sy, rot=rot))
    return out


# ---------------------------------------------------------------------------
# Net-assignment builders (by signal NAME -> {pin_number: net})
# ---------------------------------------------------------------------------
def build_som_netmap(pins):
    """SoM takes over the old AM62A7 nets.  Signal-name -> carrier net."""
    nm = {}
    for pnum, pname, *_ in pins:
        n = pname
        net = None
        if n == "VIN":
            net = "+5V"
        elif n == "VBAT":
            net = "+3V3"  # RTC/backup domain (verify)
        elif n == "SoC_VDDSHV5_SDIO":
            net = "+3V3"  # SDIO I/O domain supply
        elif n.upper().startswith("GND"):
            net = "GND"
        # --- Camera MIPI CSI-2 (lane 0 modeled; clk + D0) ---
        elif n == "X_CSI0_RXCLKP":
            net = "CSI_CLK_P"
        elif n == "X_CSI0_RXCLKN":
            net = "CSI_CLK_N"
        elif n == "X_CSI0_RXP0":
            net = "CSI_D0_P"
        elif n == "X_CSI0_RXN0":
            net = "CSI_D0_N"
        elif n == "X_I2C1_SCL":
            net = "CAM_SCL"
        elif n == "X_I2C1_SDA":
            net = "CAM_SDA"
        elif n == "X_WKUP_UART0_CTSN":
            net = "CAM_RESET_N"  # WKUP GPIO (pinmux, verify)
        # --- RGMII2 (SoM MAC) -> KSZ port6 (MAC-to-MAC crossover) ---
        elif n == "X_CPSW_RGMII2_TD0":
            net = "RGMII_S2K_D0"
        elif n == "X_CPSW_RGMII2_TD1":
            net = "RGMII_S2K_D1"
        elif n == "X_CPSW_RGMII2_TD2":
            net = "RGMII_S2K_D2"
        elif n == "X_CPSW_RGMII2_TD3":
            net = "RGMII_S2K_D3"
        elif n == "X_CPSW_RGMII2_TXC":
            net = "RGMII_S2K_C"
        elif n == "X_CPSW_RGMII2_TX_CTL":
            net = "RGMII_S2K_CTL"
        elif n == "X_CPSW_RGMII2_RD0":
            net = "RGMII_K2S_D0"
        elif n == "X_CPSW_RGMII2_RD1":
            net = "RGMII_K2S_D1"
        elif n == "X_CPSW_RGMII2_RD2":
            net = "RGMII_K2S_D2"
        elif n == "X_CPSW_RGMII2_RD3":
            net = "RGMII_K2S_D3"
        elif n == "X_CPSW_RGMII2_RXC":
            net = "RGMII_K2S_C"
        elif n == "X_CPSW_RGMII2_RX_CTL":
            net = "RGMII_K2S_CTL"
        # --- App UART0 <-> MSPM0 ---
        elif n == "X_UART0_TXD":
            net = "UART_A2M"  # SoC TX -> MCU RX
        elif n == "X_UART0_RXD":
            net = "UART_M2A"  # MCU TX -> SoC RX
        # --- Reset ---
        elif n == "X_nRESET_IN":
            net = "SOC_PORZ"
        nm[pnum] = net
    return nm


def build_ksz_netmap(pins):
    """Microchip KSZ9477.  Power rails + SPI-slave mgmt to MSPM0 + RGMII port6
    crossover to the SoM + two integrated-PHY copper ports (1,2) to the ring."""
    nm = {}
    for pnum, pname, *_ in pins:
        n = pname
        net = None
        # Power
        if n == "VDDIO":
            net = "+3V3"
        elif n in ("AVDDH", "VDDHS"):
            net = "+2V5"
        elif n in ("AVDDL", "DVDDL", "VDDLS"):
            net = "+1V2"
        elif n == "GND":
            net = "GND"
        elif n == "ISET":
            net = "KSZ_ISET"  # 6.04k to GND
        elif n == "S_REXT":
            net = "KSZ_SREXT"  # 191R to GND (SGMII ref)
        elif n == "XI":
            net = "KSZ_XI"
        elif n == "XO":
            net = "KSZ_XO"
        # SPI-slave management (from MSPM0 SPI1)
        elif n == "SCS_N":
            net = "SW_SPI_CS"
        elif n.startswith("SCL/MDC"):
            net = "SW_SPI_SCK"
        elif n.startswith("SDI/"):
            net = "SW_SPI_MOSI"
        elif n == "SDO":
            net = "SW_SPI_MISO"
        elif n == "RESET_N":
            net = "SW_RESET_N"
        elif n.startswith("INTRP_N"):
            net = "SW_INT_N"
        # RGMII port 6 (MAC-to-MAC crossover vs SoM RGMII2)
        elif n.startswith("RXD6_0"):
            net = "RGMII_S2K_D0"
        elif n.startswith("RXD6_1"):
            net = "RGMII_S2K_D1"
        elif n.startswith("RXD6_2"):
            net = "RGMII_S2K_D2"
        elif n.startswith("RXD6_3"):
            net = "RGMII_S2K_D3"
        elif n.startswith("RX_CLK6"):
            net = "RGMII_S2K_C"
        elif n.startswith("RX_DV6"):
            net = "RGMII_S2K_CTL"
        elif n == "TXD6_0":
            net = "RGMII_K2S_D0"
        elif n == "TXD6_1":
            net = "RGMII_K2S_D1"
        elif n == "TXD6_2":
            net = "RGMII_K2S_D2"
        elif n == "TXD6_3":
            net = "RGMII_K2S_D3"
        elif n.startswith("TX_CLK6"):
            net = "RGMII_K2S_C"
        elif n.startswith("TX_EN6"):
            net = "RGMII_K2S_CTL"
        # Integrated-PHY copper port 1 -> ring IN ; port 2 -> ring OUT
        # (100BASE-TX: A pair = TX, B pair = RX; C/D unused)
        elif n == "TXRX1P_A":
            net = "ETH_IN_KSZ_TXP"
        elif n == "TXRX1M_A":
            net = "ETH_IN_KSZ_TXN"
        elif n == "TXRX1P_B":
            net = "ETH_IN_KSZ_RXP"
        elif n == "TXRX1M_B":
            net = "ETH_IN_KSZ_RXN"
        elif n == "TXRX2P_A":
            net = "ETH_OUT_KSZ_TXP"
        elif n == "TXRX2M_A":
            net = "ETH_OUT_KSZ_TXN"
        elif n == "TXRX2P_B":
            net = "ETH_OUT_KSZ_RXP"
        elif n == "TXRX2M_B":
            net = "ETH_OUT_KSZ_RXN"
        nm[pnum] = net
    return nm


def build_msp_netmap(pins):
    """TI MSPM0G3507 (48-VQFN).  GPIO->peripheral pinmux is a datasheet-backed
    assignment (SLASEX6C Table 6-2); confirm against final firmware pinmux."""
    GPIO_NET = {
        "VDD": "+3V3",
        "VSS": "GND",
        "VCORE": "MCU_VCORE",  # 1.1V internal LDO out -> decoupling cap only
        "NRST": "MCU_NRST",
        "PA19/SWDIO": "MCU_SWDIO",
        "PA20/SWCLK": "MCU_SWCLK",
        # CAN-FD (PA12=CAN_TX, PA13=CAN_RX) -> ISOW1044
        "PA12": "CANFD_TX",
        "PA13": "CANFD_RX",
        # UART0 <-> SoM  (PA10=UART0_TX, PA11=UART0_RX)
        "PA10": "UART_M2A",
        "PA11": "UART_A2M",
        # UART1 <-> TFmini-S ToF (PA8=UART1_TX, PA9=UART1_RX)
        "PA8": "UART_TOF_TX",
        "PA9": "UART_TOF_RX",
        # SPI0 -> TPM  (SCK=PA6, PICO=PA5, POCI=PA4, CS0=PA2)
        "PA6": "TPM_SPI_SCK",
        "PA5": "TPM_SPI_MOSI",
        "PA4": "TPM_SPI_MISO",
        "PA2": "TPM_SPI_CS",
        # SPI1 -> KSZ mgmt (SCK=PA17, PICO=PA18, POCI=PA16, CS2=PA15)
        "PA17": "SW_SPI_SCK",
        "PA18": "SW_SPI_MOSI",
        "PA16": "SW_SPI_MISO",
        "PA15": "SW_SPI_CS",
        # KSZ control
        "PA21": "SW_RESET_N",
        "PA25": "SW_INT_N",
        # TPM control
        "PA27": "TPM_RESET_N",
        "PA26": "TPM_PIRQ",
        # Laser driver enable (interlock LASER_KEY_IN/IND left NC this pass —
        # Class 2 optic makes them optional defense-in-depth, JAYNE_LASER_ANALYSIS)
        "PA22": "LASER_EN",
        # UART2 -> ADM2795E isolated RS-485 (added 2026-07-26, see Section H:
        # "so that all nodes have at least [CAN-FD + RS-485], and everyone
        # gets a TPM" -- Jayne already had MCU+TPM+CAN-FD, this closes the gap).
        # PB15/PB16 verified against the real MSPM0G3507 datasheet (SLASEX6C
        # Table 6-2): PB15 = UART2_TX (AF2), PB16 = UART2_RX (AF2). The
        # original draft used PA3/PA7, which datasheet Table 6-2 shows have
        # NO UART function at all on either pin (PA3: SPI0_CS1/UART2_CTS/
        # TIMA.../COMP1_OUT/I2C1_SDA; PA7: COMP0_OUT/CLK_OUT/TIMG8/TIMA0 --
        # neither offers a TX/RX signal) -- caught when the user supplied the
        # MSPM0G3507 datasheet and asked for pinmux verification.
        "PB15": "RS485_TX",
        "PB16": "RS485_RX",
        "PB2": "RS485_DE",
    }
    nm = {}
    for pnum, pname, *_ in pins:
        nm[pnum] = GPIO_NET.get(pname)
    return nm


def build_tpm_netmap(pins):
    nm = {}
    for pnum, pname, *_ in pins:
        n = pname.upper()
        net = None
        if "VDD" in n and "NCI" not in n:
            net = "+3V3"
        elif n == "GND" or ("GND" in n and "NCI" not in n):
            net = "GND"
        elif n == "SCLK":
            net = "TPM_SPI_SCK"
        elif n == "MOSI":
            net = "TPM_SPI_MOSI"
        elif n == "MISO":
            net = "TPM_SPI_MISO"
        elif n == "CS#":
            net = "TPM_SPI_CS"
        elif n == "RST#":
            net = "TPM_RESET_N"
        elif n == "PIRQ#":
            net = "TPM_PIRQ"
        elif n == "PP":
            net = "+3V3"  # platform-present tie high
        nm[pnum] = net
    return nm


def build_iso_netmap(pins):
    """TI ISOW1044BDFMR isolated CAN-FD.  VIO=3V3 logic, VDD=5V converter in,
    isolated side supplies its own bus power; single-point PGND is on the CAN
    EMI chain (CANFD_ISO_H/L -> CMC -> TVS -> J_CANFD)."""
    nm = {}
    for pnum, pname, *_ in pins:
        n = pname.upper()
        net = None
        if n == "VIO":
            net = "+3V3"
        elif n == "VDD":
            net = "+5V"
        elif n == "TXD":
            net = "CANFD_TX"
        elif n == "RXD":
            net = "CANFD_RX"
        elif n == "STB":
            net = "GND"  # normal mode
        elif n == "GNDIO" or n == "GND1":
            net = "GND"
        elif n in ("GND2",) or n.startswith("GISOIN"):
            net = "CANFD_ISOGND"
        elif n in ("VISOOUT", "VSIN", "VISOIN"):
            net = "CANFD_VISO"  # shorted on-PCB isolated 5V
        elif n == "CANL":
            net = "CANFD_ISO_L"
        elif n == "CANH":
            net = "CANFD_ISO_H"
        # IN (GPIO in), OUT (GPIO out), EN/FLT, NC -> no-connect (internal pulls)
        nm[pnum] = net
    return nm


# ---------------------------------------------------------------------------
# Small discrete parts (regulators, crystal, R, C) — lib symbols
# ---------------------------------------------------------------------------
def lib_symbol_buck_sot23_6():
    """TLV62569DBV — SOT-23-6 synchronous buck.  Pins per TI SLVSDF9: 1=EN,
    2=GND, 3=SW, 4=VIN, 5=FB, 6=PG."""
    body = [
        '  (symbol "TLV62569_DBV" (in_bom yes) (on_board yes)',
        '    (property "Reference" "U" (at 0 -7 0) (effects (font (size 1.27 1.27))))',
        '    (property "Value" "TLV62569DBVR" (at 0 7 0) (effects (font (size 1.27 1.27))))',
        '    (property "Footprint" "Package_TO_SOT_SMD:SOT-23-6" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '    (property "Datasheet" "https://www.ti.com/lit/ds/symlink/tlv62569.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '    (symbol "TLV62569_DBV_0_1"',
        "      (rectangle (start -5.08 -5.08) (end 5.08 5.08)",
        "        (stroke (width 0.254) (type default)) (fill (type background))))",
        '    (symbol "TLV62569_DBV_1_1"',
    ]
    body.append(gj._pin_def("input", "line", -7.62, 2.54, 0, 2.54, "EN", "1"))
    body.append(gj._pin_def("power_in", "line", -7.62, 0.0, 0, 2.54, "GND", "2"))
    body.append(gj._pin_def("power_in", "line", -7.62, -2.54, 0, 2.54, "VIN", "4"))
    body.append(gj._pin_def("output", "line", 7.62, 2.54, 180, 2.54, "SW", "3"))
    body.append(gj._pin_def("input", "line", 7.62, 0.0, 180, 2.54, "FB", "5"))
    body.append(gj._pin_def("output", "line", 7.62, -2.54, 180, 2.54, "PG", "6"))
    body.append("    )")
    body.append("  )")
    return "\n".join(body)


def lib_symbol_ldo_sot23_5():
    """TLV75725P — SOT-23-5 LDO.  Pins per TI: 1=IN, 2=GND, 3=EN, 4=NC, 5=OUT."""
    body = [
        '  (symbol "TLV75725_DBV" (in_bom yes) (on_board yes)',
        '    (property "Reference" "U" (at 0 -7 0) (effects (font (size 1.27 1.27))))',
        '    (property "Value" "TLV75725PDBVR" (at 0 7 0) (effects (font (size 1.27 1.27))))',
        '    (property "Footprint" "Package_TO_SOT_SMD:SOT-23-5" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '    (property "Datasheet" "https://www.ti.com/lit/ds/symlink/tlv757p.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '    (symbol "TLV75725_DBV_0_1"',
        "      (rectangle (start -5.08 -5.08) (end 5.08 5.08)",
        "        (stroke (width 0.254) (type default)) (fill (type background))))",
        '    (symbol "TLV75725_DBV_1_1"',
    ]
    body.append(gj._pin_def("power_in", "line", -7.62, 2.54, 0, 2.54, "IN", "1"))
    body.append(gj._pin_def("power_in", "line", -7.62, 0.0, 0, 2.54, "GND", "2"))
    body.append(gj._pin_def("input", "line", -7.62, -2.54, 0, 2.54, "EN", "3"))
    body.append(gj._pin_def("power_out", "line", 7.62, 0.0, 180, 2.54, "OUT", "5"))
    body.append("    )")
    body.append("  )")
    return "\n".join(body)


def lib_symbol_crystal():
    body = [
        '  (symbol "Crystal_2P" (in_bom yes) (on_board yes)',
        '    (property "Reference" "Y" (at 0 -3 0) (effects (font (size 1.27 1.27))))',
        '    (property "Value" "25MHz" (at 0 3 0) (effects (font (size 1.27 1.27))))',
        '    (property "Footprint" "Crystal:Crystal_SMD_2016-2Pin_2.0x1.6mm" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '    (symbol "Crystal_2P_0_1"',
        "      (rectangle (start -1.27 -2.54) (end 1.27 2.54)",
        "        (stroke (width 0.254) (type default)) (fill (type background))))",
        '    (symbol "Crystal_2P_1_1"',
    ]
    body.append(gj._pin_def("passive", "line", -3.81, 0, 0, 2.54, "1", "1"))
    body.append(gj._pin_def("passive", "line", 3.81, 0, 180, 2.54, "2", "2"))
    body.append("    )")
    body.append("  )")
    return "\n".join(body)


# ---------------------------------------------------------------------------
# Small-part helpers (net-labelled R / C on a 2-pin horizontal symbol)
# ---------------------------------------------------------------------------
def two_pin(lib_id, ref, value, cx, cy, net1, net2, vertical=False):
    """Place a 2-pin part and label each end.  lib_symbol_2pin_h pins sit at
    local (-3.81,0)/(3.81,0)."""
    out = [gj.sym_inst(lib_id, ref, value, cx, cy)]
    if vertical:
        # rot handled by callers that need it; default horizontal here
        pass
    out.append(gj.glabel(net1, cx - 3.81, cy, rot=180))
    out.append(gj.glabel(net2, cx + 3.81, cy, rot=0))
    return out


# ---------------------------------------------------------------------------
# Compose the schematic
# ---------------------------------------------------------------------------
def gen_sch():
    # Parse real symbols once
    real = {k: parse_real_symbol(v[0]) for k, v in REAL_SYMS.items()}

    parts = []

    # -- lib_symbols ----------------------------------------------------
    lib = ["  (lib_symbols"]
    # generic small parts reused from gen_Jayne
    lib.append(gj.lib_symbol_2pin_h("C_Generic"))
    lib.append(gj.lib_symbol_2pin_h("R_Generic"))
    lib.append(gj.lib_symbol_nmos("AO3400"))
    lib.append(gj.lib_symbol_conn_np("Conn_JST_GH_02P", 2, ["1", "2"]))
    lib.append(gj.lib_symbol_conn_np("Conn_JST_GH_04P", 4, ["1", "2", "3", "4"]))
    lib.append(gj.lib_symbol_conn_np("Conn_JST_GH_05P", 5, ["1", "2", "3", "4", "5"]))
    lib.append(gj.lib_symbol_conn_np("Conn_JST_SH_02P", 2, ["1", "2"]))
    lib.append(gj.lib_symbol_conn_np("SolderLand_09P", 9))
    lib.append(gj.lib_symbol_conn_np("SolderLand_04P", 4))
    lib.append(gj.lib_symbol_conn_np("SolderLand_02P", 2))
    # Section H additions (isolated RS-485, added 2026-07-26)
    lib.append(gj.lib_symbol_conn_np("Conn_JST_GH_03P", 3, ["1", "2", "3"]))
    lib.append(gj.lib_symbol_2pin_h("SJ_Generic"))
    lib.append(
        gj.lib_symbol_generic_ic(
            "GW_ISOW1412",
            ADM_FOOTPRINT,
            ADM_DATASHEET,
            left=ADM_L,
            right=ADM_R,
            size=ADM_SIZE,
        )
    )
    # EMI-chain parts (real, from gen_Jayne generic-ic table)
    lib.append(
        gj.lib_symbol_generic_ic(
            "WURTH_ETH_XFMR",
            "Transformer_SMD:Wurth_749010012A_10-100BASE-TX",
            "https://www.we-online.com/catalog/datasheet/749010012A.pdf",
            left=gj.XFMR_L,
            right=gj.XFMR_R,
            size=gj.XFMR_SIZE,
        )
    )
    lib.append(
        gj.lib_symbol_generic_ic(
            "BOURNS_SRF2012_100Y",
            "Inductor_SMD:L_CommonModeChoke_Coilcraft_0805USB",
            "https://www.coilcraft.com/getmedia/3a436de1-46ad-49b9-b3a8-9a3faa3ecf61/srf2012.pdf",
            left=gj.CMC_L,
            right=gj.CMC_R,
            size=gj.CMC_SIZE,
        )
    )
    lib.append(
        gj.lib_symbol_generic_ic(
            "NEXPERIA_PRTR5V0U2X",
            "Package_TO_SOT_SMD:SOT-363_SC-70-6",
            "https://assets.nexperia.com/documents/data-sheet/PRTR5V0U2X.pdf",
            left=gj.TVS_L,
            right=gj.TVS_R,
            size=gj.TVS_SIZE,
        )
    )
    # discrete regulators + crystal
    lib.append(lib_symbol_buck_sot23_6())
    lib.append(lib_symbol_ldo_sot23_5())
    lib.append(lib_symbol_crystal())
    lib.append(lib_symbol_pwr_flag())
    # real clean-room symbols
    for k in ("SOM", "KSZ", "MSP", "ISO", "TPM"):
        lib.append(real[k][0])
    # power flags
    for pf in ("+5V", "+3V3", "+2V5", "+1V2"):
        lib.append(gj.lib_sym_power(pf))
    lib.append(gj.lib_sym_power("GND", bar_top=False))
    lib.append(gj.lib_sym_power("PGND", bar_top=False))
    lib.append("  )")
    parts.extend(lib)

    parts.append(
        gj.text_note(
            "JAYNE — Nose/Cargo Vision/ToF/Laser  |  STANDALONE board (NOT a PB2-I cape)  |  "
            "SoM end-state: PHYTEC PCM-071 + carrier (KSZ9477 / MSPM0G3507 / SLB9670 / ISOW1044)",
            10,
            8,
            2.0,
        )
    )

    # ==================================================================
    # Section A — Power: 5V in + carrier rails (3V3 buck, 1V2 buck, 2V5 LDO)
    # ==================================================================
    parts.append(gj.text_note("=== Section A: Power Input + Carrier Rails ===", 10, 20))
    cx, cy = 25, 32
    parts.append(gj.sym_inst("Conn_JST_GH_02P", "J_PWR", "JST-GH 2P +5V/GND", cx, cy))
    parts.append(gj.glabel("+5V", cx - 5.08, cy - 1.27, rot=180))
    parts.append(gj.glabel("GND", cx - 5.08, cy + 1.27, rot=180))

    # +3V3 buck
    def buck(ref, value, cx, cy, vout_net, fb_top, fb_bot):
        o = [gj.sym_inst("TLV62569_DBV", ref, value, cx, cy)]
        o.append(gj.glabel("+5V", cx - 7.62, cy - 2.54, rot=180))  # VIN
        o.append(gj.glabel("GND", cx - 7.62, cy, rot=180))  # GND
        o.append(gj.glabel("+5V", cx - 7.62, cy + 2.54, rot=180))  # EN tie-high
        o.append(gj.glabel(ref + "_SW", cx + 7.62, cy - 2.54, rot=0))  # SW
        o.append(gj.glabel(ref + "_FB", cx + 7.62, cy, rot=0))  # FB
        o.append(gj.glabel(vout_net + "_PG", cx + 7.62, cy + 2.54, rot=0))  # PG
        # inductor SW -> VOUT
        o.append(gj.sym_inst("R_Generic", ref + "_L", "2.2uH", cx + 20, cy - 2.54))
        o.append(gj.glabel(ref + "_SW", cx + 20 - 3.81, cy - 2.54, rot=180))
        o.append(gj.glabel(vout_net, cx + 20 + 3.81, cy - 2.54, rot=0))
        # feedback divider VOUT -> FB -> GND
        o.append(gj.sym_inst("R_Generic", fb_top, "R_fbtop", cx + 20, cy + 6))
        o.append(gj.glabel(vout_net, cx + 20 - 3.81, cy + 6, rot=180))
        o.append(gj.glabel(ref + "_FB", cx + 20 + 3.81, cy + 6, rot=0))
        o.append(gj.sym_inst("R_Generic", fb_bot, "R_fbbot", cx + 20, cy + 11))
        o.append(gj.glabel(ref + "_FB", cx + 20 - 3.81, cy + 11, rot=180))
        o.append(gj.glabel("GND", cx + 20 + 3.81, cy + 11, rot=0))
        # output cap
        o.append(gj.sym_inst("C_Generic", ref + "_CO", "22uF", cx + 30, cy - 2.54))
        o.append(gj.glabel(vout_net, cx + 30 - 3.81, cy - 2.54, rot=180))
        o.append(gj.glabel("GND", cx + 30 + 3.81, cy - 2.54, rot=0))
        # input cap
        o.append(gj.sym_inst("C_Generic", ref + "_CI", "10uF", cx - 16, cy))
        o.append(gj.glabel("+5V", cx - 16 - 3.81, cy, rot=180))
        o.append(gj.glabel("GND", cx - 16 + 3.81, cy, rot=0))
        return o

    parts.extend(
        buck("U_REG_3V3", "TLV62569 -> +3V3", 25, 48, "+3V3", "R_FB3T", "R_FB3B")
    )
    parts.extend(
        buck("U_REG_1V2", "TLV62569 -> +1V2", 25, 70, "+1V2", "R_FB1T", "R_FB1B")
    )

    # +2V5 LDO (from +3V3)
    lx, ly = 90, 48
    parts.append(gj.sym_inst("TLV75725_DBV", "U_REG_2V5", "TLV75725 -> +2V5", lx, ly))
    parts.append(gj.glabel("+3V3", lx - 7.62, ly - 2.54, rot=180))  # IN
    parts.append(gj.glabel("GND", lx - 7.62, ly, rot=180))  # GND
    parts.append(gj.glabel("+3V3", lx - 7.62, ly + 2.54, rot=180))  # EN
    parts.append(gj.glabel("+2V5", lx + 7.62, ly, rot=0))  # OUT
    parts.append(gj.sym_inst("C_Generic", "C_2V5I", "1uF", lx - 16, ly + 6))
    parts.append(gj.glabel("+3V3", lx - 16 - 3.81, ly + 6, rot=180))
    parts.append(gj.glabel("GND", lx - 16 + 3.81, ly + 6, rot=0))
    parts.append(gj.sym_inst("C_Generic", "C_2V5O", "1uF", lx + 16, ly + 6))
    parts.append(gj.glabel("+2V5", lx + 16 - 3.81, ly + 6, rot=180))
    parts.append(gj.glabel("GND", lx + 16 + 3.81, ly + 6, rot=0))

    # PWR_FLAG on every supply net (ERC: mark connector/regulator-fed rails as
    # power-driven).  Placed in a tidy column clear of other geometry.
    # (+2V5 driven by the LDO OUT power_out pin; CANFD_VISO by U4 VISOOUT —
    #  no flag on those two or ERC flags a power_out/power_out conflict.)
    for i, rail in enumerate(["+5V", "+3V3", "+1V2", "GND", "PGND", "CANFD_ISOGND"]):
        parts.extend(pwr_flag(rail, 130, 30 + i * 5))
    # Power-good pull-ups (open-drain PG -> its own rail) so PG nets aren't dangling
    parts.extend(two_pin("R_Generic", "R_PG3", "100k", 45, 40, "+3V3", "+3V3_PG"))
    parts.extend(two_pin("R_Generic", "R_PG1", "100k", 45, 62, "+1V2", "+1V2_PG"))

    parts.append(
        gj.text_note(
            "Carrier rails (design decision 2026-07-13): PCM-071 provides NO rail to "
            "the carrier; all generated here from +5V. Feedback dividers / inductor / "
            "LDO margin are first-pass — verify per TI datasheet design procedures.",
            60,
            78,
            0.9,
        )
    )

    # ==================================================================
    # Section B — SoM (U_SOM), 4 units
    # ==================================================================
    parts.append(
        gj.text_note("=== Section B: PHYTEC phyCORE PCM-071 SoM (U_SOM) ===", 160, 20)
    )
    som_pins = real["SOM"][1]
    som_nm = build_som_netmap(som_pins)
    som_pos = {1: (185, 90), 2: (255, 90), 3: (325, 90), 4: (395, 90)}
    parts.extend(
        place_real("SOM", "U_SOM", "phyCORE-AM62x PCM-071", som_pos, som_nm, som_pins)
    )

    # ==================================================================
    # Section C — KSZ9477 (U2), 6 units
    # ==================================================================
    parts.append(gj.text_note("=== Section C: Microchip KSZ9477 (U2) ===", 160, 175))
    ksz_pins = real["KSZ"][1]
    ksz_nm = build_ksz_netmap(ksz_pins)
    ksz_pos = {
        1: (180, 250),
        2: (240, 250),
        3: (300, 250),
        4: (360, 250),
        5: (430, 250),
        6: (485, 250),
    }
    parts.extend(
        place_real("KSZ", "U2", "Microchip KSZ9477", ksz_pos, ksz_nm, ksz_pins)
    )
    # 25 MHz crystal for KSZ XI/XO
    parts.append(gj.sym_inst("Crystal_2P", "Y1", "25MHz", 150, 245))
    parts.append(gj.glabel("KSZ_XI", 150 - 3.81, 245, rot=180))
    parts.append(gj.glabel("KSZ_XO", 150 + 3.81, 245, rot=0))
    # ISET 6.04k, S_REXT 191R
    parts.extend(two_pin("R_Generic", "R_ISET", "6.04k", 150, 255, "KSZ_ISET", "GND"))
    parts.extend(two_pin("R_Generic", "R_REXT", "191R", 150, 262, "KSZ_SREXT", "GND"))

    # ==================================================================
    # Section D — MSPM0G3507 (U3) + TPM (U5)
    # ==================================================================
    parts.append(
        gj.text_note("=== Section D: MSPM0G3507 (U3) + SLB9670 TPM (U5) ===", 10, 110)
    )
    msp_pins = real["MSP"][1]
    msp_nm = build_msp_netmap(msp_pins)
    parts.extend(
        place_real("MSP", "U3", "TI MSPM0G3507", {1: (55, 165)}, msp_nm, msp_pins)
    )
    # VCORE decoupling cap
    parts.extend(two_pin("C_Generic", "C_VCORE", "1uF", 20, 200, "MCU_VCORE", "GND"))
    # NRST pull-up + SoM PORz pull-up
    parts.extend(two_pin("R_Generic", "R_NRST", "10k", 20, 150, "+3V3", "MCU_NRST"))
    parts.extend(two_pin("R_Generic", "R_PORZ", "10k", 20, 145, "+3V3", "SOC_PORZ"))
    # SWD debug header (SWDIO/SWCLK/NRST/GND) — resolves debug-pin dangling and
    # provides real programming access to U3.
    sx, sy = 130, 165
    parts.append(
        gj.sym_inst("Conn_JST_GH_04P", "J_SWD", "SWD: DIO/CLK/NRST/GND", sx, sy)
    )
    parts.append(gj.glabel_conn("MCU_SWDIO", sx, sy, 4, 0))
    parts.append(gj.glabel_conn("MCU_SWCLK", sx, sy, 4, 1))
    parts.append(gj.glabel_conn("MCU_NRST", sx, sy, 4, 2))
    parts.append(gj.glabel_conn("GND", sx, sy, 4, 3))

    tpm_pins = real["TPM"][1]
    tpm_nm = build_tpm_netmap(tpm_pins)
    parts.extend(
        place_real("TPM", "U5", "Infineon SLB9670", {1: (110, 165)}, tpm_nm, tpm_pins)
    )

    # ==================================================================
    # Section E — ISOW1044 isolated CAN-FD (U4) + CAN EMI chain
    # ==================================================================
    parts.append(
        gj.text_note("=== Section E: ISOW1044 Isolated CAN-FD (U4) ===", 10, 305)
    )
    iso_pins = real["ISO"][1]
    iso_nm = build_iso_netmap(iso_pins)
    parts.extend(
        place_real("ISO", "U4", "TI ISOW1044BDFMR", {1: (55, 360)}, iso_nm, iso_pins)
    )
    # CAN CMC (isolated H/L -> bus) + TVS + connector
    cx, cy = 110, 355
    parts.append(
        gj.sym_inst("BOURNS_SRF2012_100Y", "CMC5", "SRF2012-100Y (CAN)", cx, cy)
    )
    parts.append(
        gj.glabel_pin("CANFD_ISO_H", cx, cy, gj.CMC_L, gj.CMC_R, "L1A", gj.CMC_SIZE)
    )
    parts.append(
        gj.glabel_pin("CANFD_H", cx, cy, gj.CMC_L, gj.CMC_R, "L1B", gj.CMC_SIZE)
    )
    parts.append(
        gj.glabel_pin("CANFD_ISO_L", cx, cy, gj.CMC_L, gj.CMC_R, "L2A", gj.CMC_SIZE)
    )
    parts.append(
        gj.glabel_pin("CANFD_L", cx, cy, gj.CMC_L, gj.CMC_R, "L2B", gj.CMC_SIZE)
    )
    cx2, cy2 = 145, 355
    parts.append(gj.sym_inst("NEXPERIA_PRTR5V0U2X", "D5", "PRTR5V0U2X (CAN)", cx2, cy2))
    parts.append(
        gj.glabel_pin("CANFD_H", cx2, cy2, gj.TVS_L, gj.TVS_R, "A1", gj.TVS_SIZE)
    )
    parts.append(
        gj.glabel_pin("CANFD_L", cx2, cy2, gj.TVS_L, gj.TVS_R, "A2", gj.TVS_SIZE)
    )
    parts.append(gj.pwr_pin("PGND", cx2, cy2, gj.TVS_L, gj.TVS_R, "K", gj.TVS_SIZE))
    cx3, cy3 = 180, 355
    parts.append(
        gj.sym_inst("Conn_JST_GH_04P", "J_CANFD", "5V/CANH/CANL/GND", cx3, cy3)
    )
    parts.append(gj.glabel_conn("+5V", cx3, cy3, 4, 0))
    parts.append(gj.glabel_conn("CANFD_H", cx3, cy3, 4, 1))
    parts.append(gj.glabel_conn("CANFD_L", cx3, cy3, 4, 2))
    parts.append(gj.glabel_conn("GND", cx3, cy3, 4, 3))
    # ISOW isolated-side power short: VISO decoupling cap to CANFD_ISOGND
    parts.extend(
        two_pin("C_Generic", "C_VISO", "1uF", 20, 400, "CANFD_VISO", "CANFD_ISOGND")
    )

    # ==================================================================
    # Section F — Ethernet ring EMI chain (per port: XFMR -> CMC -> TVS -> J)
    # ==================================================================
    parts.append(
        gj.text_note("=== Section F: Ethernet Ring EMI Chain (in / out) ===", 250, 305)
    )

    def eth_port(label, cx, cy, jref, tref):
        o = []
        txp, txn = f"{label}_KSZ_TXP", f"{label}_KSZ_TXN"
        rxp, rxn = f"{label}_KSZ_RXP", f"{label}_KSZ_RXN"
        ltxp, ltxn = f"{label}_L_TXP", f"{label}_L_TXN"
        lrxp, lrxn = f"{label}_L_RXP", f"{label}_L_RXN"
        # transformer
        o.append(gj.sym_inst("WURTH_ETH_XFMR", tref, "Wurth 749010012A", cx, cy))
        o.append(
            gj.glabel_pin(txp, cx, cy, gj.XFMR_L, gj.XFMR_R, "PHY_TXP", gj.XFMR_SIZE)
        )
        o.append(
            gj.glabel_pin(txn, cx, cy, gj.XFMR_L, gj.XFMR_R, "PHY_TXN", gj.XFMR_SIZE)
        )
        o.append(
            gj.glabel_pin(rxp, cx, cy, gj.XFMR_L, gj.XFMR_R, "PHY_RXP", gj.XFMR_SIZE)
        )
        o.append(
            gj.glabel_pin(rxn, cx, cy, gj.XFMR_L, gj.XFMR_R, "PHY_RXN", gj.XFMR_SIZE)
        )
        o.append(
            gj.glabel_pin(
                f"{label}_LTXP", cx, cy, gj.XFMR_L, gj.XFMR_R, "LINE_TXP", gj.XFMR_SIZE
            )
        )
        o.append(
            gj.glabel_pin(
                f"{label}_LTXN", cx, cy, gj.XFMR_L, gj.XFMR_R, "LINE_TXN", gj.XFMR_SIZE
            )
        )
        o.append(
            gj.glabel_pin(
                f"{label}_LRXP", cx, cy, gj.XFMR_L, gj.XFMR_R, "LINE_RXP", gj.XFMR_SIZE
            )
        )
        o.append(
            gj.glabel_pin(
                f"{label}_LRXN", cx, cy, gj.XFMR_L, gj.XFMR_R, "LINE_RXN", gj.XFMR_SIZE
            )
        )
        # CMC on line TX pair
        cx1 = cx + 35
        o.append(
            gj.sym_inst("BOURNS_SRF2012_100Y", tref + "_CMC1", "SRF2012-100Y", cx1, cy)
        )
        o.append(
            gj.glabel_pin(
                f"{label}_LTXP", cx1, cy, gj.CMC_L, gj.CMC_R, "L1A", gj.CMC_SIZE
            )
        )
        o.append(
            gj.glabel_pin(
                f"{label}_TXP", cx1, cy, gj.CMC_L, gj.CMC_R, "L1B", gj.CMC_SIZE
            )
        )
        o.append(
            gj.glabel_pin(
                f"{label}_LTXN", cx1, cy, gj.CMC_L, gj.CMC_R, "L2A", gj.CMC_SIZE
            )
        )
        o.append(
            gj.glabel_pin(
                f"{label}_TXN", cx1, cy, gj.CMC_L, gj.CMC_R, "L2B", gj.CMC_SIZE
            )
        )
        # CMC on line RX pair
        cx2 = cx + 35
        cy2 = cy + 12
        o.append(
            gj.sym_inst("BOURNS_SRF2012_100Y", tref + "_CMC2", "SRF2012-100Y", cx2, cy2)
        )
        o.append(
            gj.glabel_pin(
                f"{label}_LRXP", cx2, cy2, gj.CMC_L, gj.CMC_R, "L1A", gj.CMC_SIZE
            )
        )
        o.append(
            gj.glabel_pin(
                f"{label}_RXP", cx2, cy2, gj.CMC_L, gj.CMC_R, "L1B", gj.CMC_SIZE
            )
        )
        o.append(
            gj.glabel_pin(
                f"{label}_LRXN", cx2, cy2, gj.CMC_L, gj.CMC_R, "L2A", gj.CMC_SIZE
            )
        )
        o.append(
            gj.glabel_pin(
                f"{label}_RXN", cx2, cy2, gj.CMC_L, gj.CMC_R, "L2B", gj.CMC_SIZE
            )
        )
        # TVS on TX pair
        cx3 = cx + 70
        o.append(
            gj.sym_inst("NEXPERIA_PRTR5V0U2X", tref + "_D1", "PRTR5V0U2X", cx3, cy)
        )
        o.append(
            gj.glabel_pin(
                f"{label}_TXP", cx3, cy, gj.TVS_L, gj.TVS_R, "A1", gj.TVS_SIZE
            )
        )
        o.append(
            gj.glabel_pin(
                f"{label}_TXN", cx3, cy, gj.TVS_L, gj.TVS_R, "A2", gj.TVS_SIZE
            )
        )
        o.append(gj.pwr_pin("GND", cx3, cy, gj.TVS_L, gj.TVS_R, "K", gj.TVS_SIZE))
        # TVS on RX pair
        cx4 = cx + 70
        cy4 = cy + 12
        o.append(
            gj.sym_inst("NEXPERIA_PRTR5V0U2X", tref + "_D2", "PRTR5V0U2X", cx4, cy4)
        )
        o.append(
            gj.glabel_pin(
                f"{label}_RXP", cx4, cy4, gj.TVS_L, gj.TVS_R, "A1", gj.TVS_SIZE
            )
        )
        o.append(
            gj.glabel_pin(
                f"{label}_RXN", cx4, cy4, gj.TVS_L, gj.TVS_R, "A2", gj.TVS_SIZE
            )
        )
        o.append(gj.pwr_pin("GND", cx4, cy4, gj.TVS_L, gj.TVS_R, "K", gj.TVS_SIZE))
        # connector (5P: GND + TX+/TX-/RX+/RX-)
        cx5 = cx + 95
        o.append(
            gj.sym_inst("Conn_JST_GH_05P", jref, "JST-GH 5P shielded Eth ring", cx5, cy)
        )
        o.append(gj.glabel_conn("PGND_SHIELD", cx5, cy, 5, 0))
        o.append(gj.glabel_conn(f"{label}_TXP", cx5, cy, 5, 1))
        o.append(gj.glabel_conn(f"{label}_TXN", cx5, cy, 5, 2))
        o.append(gj.glabel_conn(f"{label}_RXP", cx5, cy, 5, 3))
        o.append(gj.glabel_conn(f"{label}_RXN", cx5, cy, 5, 4))
        return o

    parts.extend(eth_port("ETH_IN", 250, 330, "J_ETH_IN", "T1"))
    parts.extend(eth_port("ETH_OUT", 250, 370, "J_ETH_OUT", "T2"))

    # ==================================================================
    # Section G — PGND/GND single-point bond
    # ==================================================================
    parts.append(gj.text_note("=== Section G: PGND/GND single-point bond ===", 10, 430))
    parts.extend(two_pin("R_Generic", "J_CHASSIS_R", "0R", 30, 445, "GND", "PGND"))
    parts.extend(two_pin("C_Generic", "C_ISO", "100nF/500V", 30, 452, "GND", "PGND"))
    # tie PGND_SHIELD (connector shrouds) to PGND via 0R (chassis)
    parts.extend(two_pin("R_Generic", "R_SHIELD", "0R", 60, 445, "PGND", "PGND_SHIELD"))

    # ==================================================================
    # Section H — Camera + ToF + Laser (nets to SoM/MCU; connectors + DS lands)
    # ==================================================================
    parts.append(gj.text_note("=== Section H: Camera / ToF / Laser ===", 250, 430))
    # Camera JST (CSI clk/D0) + I2C/reset/3V3
    cx, cy = 250, 445
    parts.append(gj.sym_inst("Conn_JST_GH_04P", "J_CAM1", "CSI CLK/D0", cx, cy))
    parts.append(gj.glabel_conn("CSI_CLK_P", cx, cy, 4, 0))
    parts.append(gj.glabel_conn("CSI_CLK_N", cx, cy, 4, 1))
    parts.append(gj.glabel_conn("CSI_D0_P", cx, cy, 4, 2))
    parts.append(gj.glabel_conn("CSI_D0_N", cx, cy, 4, 3))
    cx, cy = 285, 445
    parts.append(
        gj.sym_inst("Conn_JST_GH_04P", "J_CAM2", "CAM SDA/SCL/RST/3V3", cx, cy)
    )
    parts.append(gj.glabel_conn("CAM_SDA", cx, cy, 4, 0))
    parts.append(gj.glabel_conn("CAM_SCL", cx, cy, 4, 1))
    parts.append(gj.glabel_conn("CAM_RESET_N", cx, cy, 4, 2))
    parts.append(gj.glabel_conn("+3V3", cx, cy, 4, 3))
    # Camera direct-solder land (9P)
    dsx, dsy = 320, 445
    parts.append(
        gj.sym_inst(
            "SolderLand_09P",
            "J_CAM_DS",
            "Direct-solder camera land (nose; DNP if J_CAM* used)",
            dsx,
            dsy,
            footprint="Jayne:DS_Camera_9P",
        )
    )
    for i, net in enumerate(
        [
            "CSI_CLK_P",
            "CSI_CLK_N",
            "CSI_D0_P",
            "CSI_D0_N",
            "CAM_SDA",
            "CAM_SCL",
            "CAM_RESET_N",
            "+3V3",
            "GND",
        ]
    ):
        parts.append(gj.glabel_conn(net, dsx, dsy, 9, i))
    # ToF JST + DS land
    cx, cy = 250, 480
    parts.append(
        gj.sym_inst("Conn_JST_GH_04P", "J_TOF", "TFmini-S 5V/GND/TX/RX", cx, cy)
    )
    parts.append(gj.glabel_conn("+5V", cx, cy, 4, 0))
    parts.append(gj.glabel_conn("GND", cx, cy, 4, 1))
    parts.append(gj.glabel_conn("UART_TOF_TX", cx, cy, 4, 2))
    parts.append(gj.glabel_conn("UART_TOF_RX", cx, cy, 4, 3))
    tdx, tdy = 285, 480
    parts.append(
        gj.sym_inst(
            "SolderLand_04P",
            "J_TOF_DS",
            "Direct-solder ToF land (nose; DNP if J_TOF used)",
            tdx,
            tdy,
            footprint="Jayne:DS_ToF_4P",
        )
    )
    for i, net in enumerate(["+5V", "GND", "UART_TOF_TX", "UART_TOF_RX"]):
        parts.append(gj.glabel_conn(net, tdx, tdy, 4, i))
    # Laser driver Q1 + R1 + R2 + JST + DS land
    cx, cy = 340, 480
    parts.append(gj.sym_inst("AO3400", "Q1", "AO3400 logic-level N-MOSFET", cx, cy))
    parts.append(gj.glabel("LASER_GATE", cx - 7.62, cy, rot=180))
    parts.append(gj.glabel("LASER_CATHODE", cx + 2.54, cy - 7.62, rot=90))
    parts.append(gj.pwr_sym("GND", cx + 2.54, cy + 7.62, rot=0))
    parts.append(gj.sym_inst("R_Generic", "R1", "100R gate", cx - 25, cy))
    parts.append(gj.glabel("LASER_EN", cx - 25 - 3.81, cy, rot=180))
    parts.append(gj.glabel("LASER_GATE", cx - 25 + 3.81, cy, rot=0))
    parts.append(gj.sym_inst("R_Generic", "R2", "10k pulldown", cx - 25, cy + 10))
    parts.append(gj.glabel("LASER_GATE", cx - 25 - 3.81, cy + 10, rot=180))
    parts.append(gj.pwr_sym("GND", cx - 25 + 3.81, cy + 10, rot=0))
    cx2, cy2 = 375, 480
    parts.append(
        gj.sym_inst("Conn_JST_SH_02P", "J_LASER", "laser +5V/cathode", cx2, cy2)
    )
    parts.append(gj.glabel_conn("+5V", cx2, cy2, 2, 0))
    parts.append(gj.glabel_conn("LASER_CATHODE", cx2, cy2, 2, 1))
    ldx, ldy = 410, 480
    parts.append(
        gj.sym_inst(
            "SolderLand_02P",
            "J_LASER_DS",
            "Direct-solder laser land (nose; DNP if J_LASER used)",
            ldx,
            ldy,
            footprint="Jayne:DS_Laser_2P",
        )
    )
    parts.append(gj.glabel_conn("+5V", ldx, ldy, 2, 0))
    parts.append(gj.glabel_conn("LASER_CATHODE", ldx, ldy, 2, 1))

    # ==================================================================
    # Section H — ISOW1412 isolated RS-485 (U6, NEW 2026-07-26)
    # "add rs485 to jayne as well, so that all nodes have at least those
    # two busses" -- Jayne already had MCU (U3) + TPM (U5) + isolated CAN-FD
    # (U4); this section closes the RS-485 gap using the same recipe as
    # CAN-PERIPH-GW-1's Section E (avionics/kicad/CAN-PERIPH-GW-1/). Uses
    # TI ISOW1412 (integrated isolated DC-DC, like ISOW1044 for CAN-FD) --
    # superseded ADM2795E, see the ADM_L/ADM_R table comment above.
    # ==================================================================
    parts.append(
        gj.text_note("=== Section H: ISOW1412 Isolated RS-485 (U6) ===", 250, 440)
    )
    adm_cx, adm_cy = 300, 480
    adm_netmap = {
        "1": "+3V3",
        "2": "RS485_TX",
        "3": "RS485_DE",
        "4": "RS485_RX",
        "5": "RS485_DE",
        "6": "GND",
        "8": "RS485_FLT_N",
        "9": "+3V3",
        "10": "GND",
        "11": "ISO_GND_485",
        "12": "ISO_3V3_485",
        "13": "ISO_GND_485",
        "15": "ISO_GND_485",
        "16": "ISO_3V3_485",
        "17": "RS485_A",
        "18": "RS485_B",
        "19": "RS485_B",
        "20": "RS485_A",
    }
    parts.append(
        gj.sym_inst(
            "GW_ISOW1412", "U6", "TI ISOW1412", adm_cx, adm_cy,
            footprint=ADM_FOOTPRINT, datasheet=ADM_DATASHEET,
        )
    )
    for pname, pnum, ptype in ADM_L + ADM_R:
        net = adm_netmap.get(pnum)
        if net is None:
            parts.append(no_connect_pin_bynum(adm_cx, adm_cy, ADM_L, ADM_R, pnum, ADM_SIZE))
        else:
            parts.append(glabel_pin_bynum(net, adm_cx, adm_cy, ADM_L, ADM_R, pnum, ADM_SIZE))

    parts.extend(two_pin("C_Generic", "C_ADM1", "100nF", 250, 465, "+3V3", "GND"))
    parts.extend(
        two_pin("C_Generic", "C_ADM2", "100nF", 250, 471, "ISO_3V3_485", "ISO_GND_485")
    )
    parts.extend(pwr_flag("ISO_GND_485", 340, 471))
    # No external isolated DC-DC needed -- ISOW1412 has its own integrated
    # isolated DC-DC (VISOOUT/VISOIN, pins 12/16), same as ISOW1044 (U4).

    parts.append(
        gj.sym_inst(
            "Conn_JST_GH_03P", "J_RS485_IN", "RS-485 trunk IN (A/B/GND)", 350, 470,
        )
    )
    parts.append(gj.glabel_conn("RS485_A", 350, 470, 3, 0))
    parts.append(gj.glabel_conn("RS485_B", 350, 470, 3, 1))
    parts.append(gj.glabel_conn("ISO_GND_485", 350, 470, 3, 2))
    parts.append(
        gj.sym_inst(
            "Conn_JST_GH_03P", "J_RS485_OUT", "RS-485 trunk OUT (A/B/GND)", 380, 470,
        )
    )
    parts.append(gj.glabel_conn("RS485_A", 380, 470, 3, 0))
    parts.append(gj.glabel_conn("RS485_B", 380, 470, 3, 1))
    parts.append(gj.glabel_conn("ISO_GND_485", 380, 470, 3, 2))

    parts.extend(two_pin("R_Generic", "R_485TERM", "120R", 350, 495, "RS485_A", "TERM485_MID"))
    parts.append(
        gj.sym_inst(
            "SJ_Generic", "SJ_485", "open by default", 370, 495,
            footprint="Jumper:SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm",
        )
    )
    parts.append(gj.glabel("TERM485_MID", 366.19, 495, rot=180))
    parts.append(gj.glabel("RS485_B", 373.81, 495, rot=0))

    # -- compose --------------------------------------------------------
    sch = [
        "(kicad_sch (version 20240101) (generator eeschema)",
        '  (paper "A1")',
        "  (title_block",
        '    (title "Jayne — Nose/Cargo-Bay Vision, ToF & Laser Board (SoM end-state)")'
        ' (date "2026-07-13") (rev "S1") (company "Griffing Technology LLC")',
        '    (comment 1 "Serenity UAV — STANDALONE board, NOT a PocketBeagle 2 Industrial cape")',
        '    (comment 2 "Copyright 2026 Steve Griffing PE(CSE) CISSP-ISSEP CPP | Griffing Technology LLC")',
        '    (comment 3 "License: CC BY 4.0  |  creativecommons.org/licenses/by/4.0")',
        '    (comment 4 "SoM carrier: real clean-room symbols; see gen_Jayne_carrier_sch.py")',
        "  )",
    ]
    sch.extend(parts)
    sch.append(")")
    return "\n".join(sch)


# Footprint each ref carries on the PCB (mirrors gen_Jayne_carrier_pcb.py) so
# schematic-parity DRC sees matching footprints instead of empty fields.
def footprint_for(ref):
    R = "Resistor_SMD:R_0402_1005Metric"
    C = "Capacitor_SMD:C_0402_1005Metric"
    if ref in ("CMC5",) or ref.endswith(("_CMC1", "_CMC2")):
        return "Inductor_SMD:L_CommonModeChoke_Coilcraft_0805USB"
    if ref in ("T1", "T2"):
        return "Jayne:Wurth_749010012A_10-100BASE-TX"
    if ref in ("D5",) or ref.endswith(("_D1", "_D2")):
        return "Package_TO_SOT_SMD:SOT-363_SC-70-6"
    if ref in ("U_REG_3V3", "U_REG_1V2"):
        return "Package_TO_SOT_SMD:SOT-23-6"
    if ref == "U_REG_2V5":
        return "Package_TO_SOT_SMD:SOT-23-5"
    if ref.endswith("_L"):
        return "Inductor_SMD:L_Taiyo-Yuden_NR-20xx"
    if ref == "Q1":
        return "Package_TO_SOT_SMD:SOT-23"
    if ref == "Y1":
        return "Crystal:Crystal_SMD_2012-2Pin_2.0x1.2mm"
    if ref == "J_PWR":
        return "Connector_JST:JST_GH_BM02B-GHS-TBT_1x02-1MP_P1.25mm_Vertical"
    if ref in ("J_CANFD", "J_CAM1", "J_CAM2", "J_TOF", "J_SWD"):
        return "Connector_JST:JST_GH_BM04B-GHS-TBT_1x04-1MP_P1.25mm_Vertical"
    if ref in ("J_ETH_IN", "J_ETH_OUT"):
        return "Connector_JST:JST_GH_SM05B-GHS-TB_1x05-1MP_P1.25mm_Horizontal"
    if ref == "J_LASER":
        return "Connector_JST:JST_SH_BM02B-SRSS-TB_1x02-1MP_P1.00mm_Vertical"
    if ref == "J_CAM_DS":
        return "Jayne:DS_Camera_9P"
    if ref == "J_TOF_DS":
        return "Jayne:DS_ToF_4P"
    if ref == "J_LASER_DS":
        return "Jayne:DS_Laser_2P"
    if ref in ("R1", "R2") or ref.startswith("R_") or ref == "J_CHASSIS_R":
        return R
    if ref.startswith("C_") or ref.endswith(("_CI", "_CO", "_CV")):
        return C
    return None


def fill_footprints(content):
    """Fill empty Footprint properties on placed symbols with the PCB footprint."""

    def repl(m):
        block = m.group(0)
        rm = re.search(r'\(property "Reference" "([^"]+)"', block)
        if not rm:
            return block
        ref = rm.group(1)
        fpn = footprint_for(ref)
        if not fpn:
            return block
        return re.sub(
            r'\(property "Footprint" ""',
            f'(property "Footprint" "{fpn}"',
            block,
            count=1,
        )

    # each placed symbol instance is a top-level (symbol (lib_id ...) ...) block
    return re.sub(r'\(symbol \(lib_id "[^"]+"\).*?\n  \)', repl, content, flags=re.S)


if __name__ == "__main__":
    out = KICADS / "Jayne.kicad_sch"
    content = fill_footprints(gen_sch())
    out.write_text(content, encoding="utf-8")
    print(f"  Written: {out}  ({len(content):,} bytes)")
