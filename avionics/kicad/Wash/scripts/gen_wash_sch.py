#!/usr/bin/env python3
"""gen_wash_sch.py — Author a readable, datasheet-accurate Wash schematic.

Schematic-first rebuild of the Wash (CAPE-A-2) flight-control cape.  Each IC is
emitted as a rectangular symbol with its FULL datasheet pinout (pin number +
function name), and every functional pin is wired to a global net label so the
design reads cleanly and `kicad-cli sch erc` stays quiet on off-sheet nets.

Pinouts are transcribed directly from the OEM datasheets in
``avionics/datasheets/`` (authoritative per avionics/CLAUDE.md):
  * ISOW1044BDFMR  -> isow1044.pdf  Fig 7-1 / Table 7-1 (20-pin DFM)
  * ADM2795EBRWZ   -> adm2795e.pdf  Table 10 (16-lead RW-16)
  * SLB9670 (TPM)  -> SLB_9670VQ20_Infineon.pdf Fig 1 (PG-VQFN-32-13)
  * SAM-M10Q       -> SAM-M10Q_DataSheet_UBX-22013293.pdf §3.1 (LGA module)

This first pass covers the isolated-bus (CAN / RS-485), the TPM, and GPS — the
parts whose net->pin maps were most broken and are now fully verified.  The
Ethernet PHY/isolator section is deferred pending the DP83825I-vs-ADIN1300
architecture decision; the 1553, IMU, baro, compass, GPIO and PB2 headers follow.

Author: Claude (Opus 4.8), 2026-07-14.  CC BY 4.0.
"""
from __future__ import annotations
import itertools
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "kicads" / "Wash_rebuild.kicad_sch"

SIZE = 1.27
PIN_PITCH = 2.54
STUB = 2.54
_uid = itertools.count(1)


def uid() -> str:
    return f"a3000000-0000-0000-0000-{next(_uid):012d}"


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def sanitize(ref: str) -> str:
    import re
    return re.sub(r"[^A-Za-z0-9_+.-]", "_", ref)


# ---------------------------------------------------------------------------
# Datasheet-transcribed pinouts.  Each entry: (pin_number, function, net|None).
# net=None -> emitted as a no-connect (NC / spare / unused-here).
# side "L"/"R" places the pin on the left or right of the box for readability.
# ---------------------------------------------------------------------------
ICS = [
    {
        "ref": "CAN-TR", "value": "ISOW1044BDFMR",
        "ds": "isow1044.pdf Fig 7-1 / Table 7-1 (20-pin DFM)",
        # side 1 (logic) on left, side 2 (isolated CAN bus) on right
        "pins": [
            ("1", "VIO", "+3V3", "L"),
            ("2", "IN", None, "L"),
            ("3", "TXD", "MCAN0_TX", "L"),
            ("4", "STB", "CAN_STB", "L"),
            ("5", "RXD", "MCAN0_RX", "L"),
            ("6", "GNDIO", "GND", "L"),
            ("7", "NC", None, "L"),
            ("8", "EN/FLT", None, "L"),
            ("9", "VDD", "+3V3", "L"),
            ("10", "GND1", "GND", "L"),
            ("20", "VISOIN", "VCC2_CAN", "R"),
            ("19", "CANH", "CAN_H", "R"),
            ("18", "CANL", "CAN_L", "R"),
            ("17", "GISOIN", "GND2_CAN", "R"),
            ("16", "GISOIN", "GND2_CAN", "R"),
            ("15", "GISOIN", "GND2_CAN", "R"),
            ("14", "OUT", None, "R"),
            ("13", "VSIN", "VCC2_CAN", "R"),
            ("12", "VISOOUT", "VCC2_CAN", "R"),
            ("11", "GND2", "GND2_CAN", "R"),
        ],
    },
    {
        "ref": "RS485", "value": "ADM2795EBRWZ",
        "ds": "adm2795e.pdf Table 10 (16-lead RW-16)",
        "pins": [
            ("1", "VDD1", "+3V3", "L"),
            ("2", "GND1", "GND", "L"),
            ("3", "TxD", "RS485_TX", "L"),
            ("4", "DE", "RS485_DE", "L"),
            ("5", "RE", "RS485_DE", "L"),
            ("6", "RxD", "RS485_RX", "L"),
            ("7", "NIC", None, "L"),
            ("8", "GND1", "GND", "L"),
            ("16", "VDD2", "VCC2_RS485", "R"),
            ("15", "GND2", "GND2_RS485", "R"),
            ("14", "B", "RS485_B", "R"),
            ("13", "VDD2", "VCC2_RS485", "R"),
            ("12", "GND2", "GND2_RS485", "R"),
            ("11", "A", "RS485_A", "R"),
            ("10", "GND2", "GND2_RS485", "R"),
            ("9", "GND2", "GND2_RS485", "R"),
        ],
    },
    {
        "ref": "TPM", "value": "SLB9670",
        "ds": "SLB_9670VQ20_Infineon.pdf Fig 1 (PG-VQFN-32-13)",
        "pins": [
            # left column = SPI / control (side toward SoC)
            ("17", "RST#", "TPM_RSTN", "L"),
            ("18", "PIRQ#", "TPM_IRQN", "L"),
            ("19", "SCLK", "SPI0_CLK", "L"),
            ("20", "CS#", "SPI0_CS_TPM", "L"),
            ("21", "MOSI", "SPI0_MOSI", "L"),
            ("24", "MISO", "SPI0_MISO", "L"),
            ("6", "GPIO", None, "L"),
            ("7", "PP", None, "L"),
            # right column = power / ground / NC
            ("22", "VDD", "+3V3", "R"),
            ("8", "VDD", "+3V3", "R"),
            ("2", "GND", "GND", "R"),
            ("9", "GND", "GND", "R"),
            ("23", "GND", "GND", "R"),
            ("32", "GND", "GND", "R"),
            ("33", "EP", "GND", "R"),
            ("1", "NCI/VDD", None, "R"),
        ],
        # NCI pins 3,4,5,10,11,12,13,14,15,16,25,26,27,28,29,30,31 omitted from
        # the readable sheet (all not-connected-internally); documented here.
    },
    {
        "ref": "GPS", "value": "SAM-M10Q-00B",
        "ds": "SAM-M10Q_DataSheet_UBX-22013293.pdf §3.1 (LGA module)",
        "pins": [
            ("2", "V_IO", "+3V3", "L"),
            ("3", "V_BCKP", "+3V3", "L"),
            ("13", "TXD", "UART_GPS_TX", "L"),
            ("14", "RXD", "UART_GPS_RX", "L"),
            ("7", "TIMEPULSE", "GPS_TIMEPULSE", "L"),
            ("8", "SAFEBOOT_N", None, "L"),
            ("9", "SDA", None, "R"),
            ("12", "SCL", None, "R"),
            ("1", "GND", "GND", "R"),
            ("4", "GND", "GND", "R"),
            ("5", "GND", "GND", "R"),
            ("6", "GND", "GND", "R"),
            ("10", "GND", "GND", "R"),
            ("11", "GND", "GND", "R"),
            ("15", "GND", "GND", "R"),
            ("16", "GND", "GND", "R"),
        ],
    },
]


def adin1300(ref, rmii, rstn, intn, eth):
    """ADIN1300BCPZ 40-LFCSP, RMII mode (adin1300.pdf pin table).
    RMII isolation redesign: RMII connects DIRECT to the SoC; galvanic
    isolation is provided by the 749010012A magnetics on the MDI/line side
    (the ISO6442-on-RMII scheme is removed — it shorted the barrier and cannot
    pass 50 MHz REF_CLK). Config-strap pins (PHY_CFG*, PHYAD via RXD_2/3) set
    the PHY address by pull resistors at reset — labelled as strap nets."""
    dvdd = f"DVDD_0P9_{ref}"
    rext = f"REXT_{ref}"
    return {
        "ref": ref, "value": "ADIN1300BCPZ",
        "ds": "adin1300.pdf Pin Function Descriptions (40-LFCSP, CP-40-26)",
        "pins": [
            # left: MAC/RMII + management
            ("39", "TXD_0", f"{rmii}_TXD0", "L"),
            ("1", "TXD_1", f"{rmii}_TXD1", "L"),
            ("37", "TX_CTL/TX_EN", f"{rmii}_TX_EN", "L"),
            ("33", "RXD_0", f"{rmii}_RXD0", "L"),
            ("32", "RXD_1", f"{rmii}_RXD1", "L"),
            ("35", "RX_CTL/CRS_DV", f"{rmii}_CRS_DV", "L"),
            ("27", "GP_CLK/RX_ER", f"{rmii}_RX_ER", "L"),
            ("9", "REF_CLK", f"{rmii}_REF_CLK", "L"),
            ("23", "MDC", "MDC", "L"),
            ("24", "MDIO", "MDIO", "L"),
            ("7", "RESET_N", rstn, "L"),
            ("22", "INT_N", intn, "L"),
            ("2", "TXD_2", None, "L"),
            ("3", "TXD_3", None, "L"),
            ("29", "RXD_3/PHYAD_3", f"{ref}_PHYAD3", "L"),
            ("30", "RXD_2/PHYAD_2", f"{ref}_PHYAD2", "L"),
            ("21", "LED_0/PHY_CFG0", f"{ref}_CFG0", "L"),
            ("26", "LINK_ST/PHY_CFG1", f"{ref}_CFG1", "L"),
            ("34", "RXC", None, "L"),
            ("38", "TXC", None, "L"),
            # right: MDI (to magnetics) + analog + power
            ("12", "MDI_0_P", f"{eth}_TXP", "R"),
            ("13", "MDI_0_N", f"{eth}_TXN", "R"),
            ("14", "MDI_1_P", f"{eth}_RXP", "R"),
            ("15", "MDI_1_N", f"{eth}_RXN", "R"),
            ("16", "MDI_2_P", None, "R"),
            ("17", "MDI_2_N", None, "R"),
            ("18", "MDI_3_P", None, "R"),
            ("19", "MDI_3_N", None, "R"),
            ("10", "REXT", rext, "R"),
            ("6", "CLK25_REF", None, "R"),
            ("8", "XTAL_O", None, "R"),
            ("11", "AVDD_3P3", "+3V3", "R"),
            ("20", "AVDD_3P3", "+3V3", "R"),
            ("25", "VDDIO", "+3V3", "R"),
            ("31", "VDDIO", "+3V3", "R"),
            ("40", "VDDIO", "+3V3", "R"),
            ("4", "DVDD_0P9", dvdd, "R"),
            ("28", "DVDD_0P9", dvdd, "R"),
            ("36", "DVDD_0P9", dvdd, "R"),
            ("5", "GND", "GND", "R"),
            ("41", "EP", "GND", "R"),
        ],
    }


def eth_xfmr(ref, eth):
    """Wurth 749010012A dual 10/100 LAN transformer (749010012A.pdf schematic).
    PHY-side TD±/RD± (1-3,6-8) <-> line-side TX±/RX± (9-11,14-16); 1:1, 1500 V
    isolation — this is the Ethernet galvanic barrier."""
    return {
        "ref": ref, "value": "749010012A",
        "ds": "749010012A.pdf mechanical/schematic (WE-LAN 10/100 SMT)",
        "pins": [
            ("1", "TD+", f"{eth}_TXP", "L"),
            ("3", "TD-", f"{eth}_TXN", "L"),
            ("6", "RD+", f"{eth}_RXP", "L"),
            ("8", "RD-", f"{eth}_RXN", "L"),
            ("2", "CTD", f"{eth}_CTD", "L"),
            ("7", "CRD", f"{eth}_CRD", "L"),
            ("16", "TX+", f"{eth}_LINE_TXP", "R"),
            ("14", "TX-", f"{eth}_LINE_TXN", "R"),
            ("11", "RX+", f"{eth}_LINE_RXP", "R"),
            ("9", "RX-", f"{eth}_LINE_RXN", "R"),
            ("15", "CTX", f"{eth}_LINE_CT", "R"),
            ("10", "CRX", f"{eth}_LINE_CT", "R"),
        ],
    }


ICS += [
    adin1300("ETH1-PHY", "RMII0", "PHY1_RSTN", "PHY1_INTRN", "ETH"),
    adin1300("ETH2-PHY", "RMII1", "PHY2_RSTN", "PHY2_INTRN", "ETH2"),
    eth_xfmr("T-ETH", "ETH"),
    eth_xfmr("T-ETH2", "ETH2"),
]


def lib_symbol(ic) -> str:
    ref, pins = ic["ref"], ic["pins"]
    left = [p for p in pins if p[3] == "L"]
    right = [p for p in pins if p[3] == "R"]
    rows = max(len(left), len(right), 1)
    half_h = (rows * PIN_PITCH) / 2 + PIN_PITCH
    half_w = 16.51
    libid = f"S_{sanitize(ref)}"
    s = [
        f'    (symbol "{libid}" (pin_names (offset 1.016)) '
        f"(exclude_from_sim no) (in_bom yes) (on_board yes)",
        f'      (property "Reference" "U" (at 0 {half_h + 1.27:.2f} 0) '
        f"(effects (font (size {SIZE} {SIZE}))))",
        f'      (property "Value" "{esc(ic["value"])}" (at 0 {-half_h - 1.27:.2f} 0) '
        f"(effects (font (size {SIZE} {SIZE}))))",
        f'      (symbol "{libid}_0_1"',
        f"        (rectangle (start {-half_w:.2f} {half_h:.2f}) "
        f"(end {half_w:.2f} {-half_h:.2f}) "
        f"(stroke (width 0.2540) (type default)) (fill (type background)))",
        "      )",
        f'      (symbol "{libid}_1_1"',
    ]
    for i, (pn, fn, net, _) in enumerate(left):
        y = half_h - PIN_PITCH * (i + 1)
        s.append(pin_def(-half_w - PIN_PITCH, y, 0, pn, fn))
    for i, (pn, fn, net, _) in enumerate(right):
        y = half_h - PIN_PITCH * (i + 1)
        s.append(pin_def(half_w + PIN_PITCH, y, 180, pn, fn))
    s += ["      )", "    )"]
    return "\n".join(s), left, right, half_w, half_h


def pin_def(x, y, ang, pn, fn):
    etype = "power_in" if fn in ("GND", "EP") else "passive"
    return (
        f"        (pin {etype} line (at {x:.2f} {y:.2f} {ang}) (length {PIN_PITCH}) "
        f'(name "{esc(fn)}" (effects (font (size {SIZE} {SIZE})))) '
        f'(number "{esc(pn)}" (effects (font (size {SIZE} {SIZE})))))'
    )


def wire(x1, y1, x2, y2):
    return (
        f"  (wire (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f})) "
        f'(stroke (width 0) (type default)) (uuid "{uid()}"))'
    )


def label(net, x, y, ang):
    just = "left" if ang == 0 else "right"
    return (
        f'  (global_label "{esc(net)}" (shape passive) (at {x:.2f} {y:.2f} {ang}) '
        f"(effects (font (size {SIZE} {SIZE})) (justify {just})) "
        f'(uuid "{uid()}"))'
    )


def no_connect(x, y):
    return f'  (no_connect (at {x:.2f} {y:.2f}) (uuid "{uid()}"))'


def emit_instance(ic, X, Y, left, right, half_w, half_h, sheet_uuid):
    ref, value = ic["ref"], ic["value"]
    libid = f"S_{sanitize(ref)}"
    out = [
        f'  (symbol (lib_id "{libid}") (at {X:.2f} {Y:.2f} 0) (unit 1)',
        f'    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid()}")',
        f'    (property "Reference" "{esc(ref)}" (at {X:.2f} {Y - half_h - 1.27:.2f} 0) '
        f"(effects (font (size {SIZE} {SIZE}))))",
        f'    (property "Value" "{esc(value)}" (at {X:.2f} {Y + half_h + 1.27:.2f} 0) '
        f"(effects (font (size {SIZE} {SIZE}))))",
    ]
    for pn, *_ in left + right:
        out.append(f'    (pin "{esc(pn)}" (uuid "{uid()}"))')
    out.append(
        f'    (instances (project "Wash" (path "/{sheet_uuid}" '
        f'(reference "{esc(ref)}") (unit 1))))'
    )
    out.append("  )")
    wl = []
    for i, (pn, fn, net, _) in enumerate(left):
        ly = half_h - PIN_PITCH * (i + 1)
        cx, cy = X - half_w - PIN_PITCH, Y - ly
        if net is None:
            wl.append(no_connect(cx, cy))
            continue
        wl.append(wire(cx, cy, cx - STUB, cy))
        wl.append(label(net, cx - STUB, cy, 180))
    for i, (pn, fn, net, _) in enumerate(right):
        ly = half_h - PIN_PITCH * (i + 1)
        cx, cy = X + half_w + PIN_PITCH, Y - ly
        if net is None:
            wl.append(no_connect(cx, cy))
            continue
        wl.append(wire(cx, cy, cx + STUB, cy))
        wl.append(label(net, cx + STUB, cy, 0))
    return out + wl


def main():
    sheet_uuid = uid()
    parts = [
        "(kicad_sch (version 20240101) (generator eeschema)",
        f'  (uuid "{uid()}")',
        '  (paper "A2")',
        "  (lib_symbols",
    ]
    placed = []
    X0, Y0, DX = 76.2, 76.2, 101.6
    for k, ic in enumerate(ICS):
        libtext, left, right, hw, hh = lib_symbol(ic)
        parts.append(libtext)
        col = k % 3
        rowi = k // 3
        X = X0 + col * DX
        Y = Y0 + rowi * 152.4
        placed.append((ic, X, Y, left, right, hw, hh))
    parts.append("  )")
    for ic, X, Y, left, right, hw, hh in placed:
        parts += emit_instance(ic, X, Y, left, right, hw, hh, sheet_uuid)
    parts.append('  (sheet_instances (path "/" (page "1")))')
    parts.append(")")
    OUT.write_text("\n".join(parts) + "\n")
    npins = sum(len(ic["pins"]) for ic in ICS)
    print(f"Wrote {OUT}")
    print(f"  ICs: {len(ICS)}  ({', '.join(ic['ref'] for ic in ICS)})")
    print(f"  total datasheet pins emitted: {npins}")


if __name__ == "__main__":
    main()
