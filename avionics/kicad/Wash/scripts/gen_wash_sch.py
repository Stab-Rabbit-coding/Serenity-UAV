#!/usr/bin/env python3
"""gen_wash_sch.py — Author a readable, datasheet-accurate Wash schematic.

Schematic-first rebuild of the Wash (CAPE-A-2) flight-control cape.  Each IC is
emitted as a rectangular symbol with its FULL datasheet pinout (pin number +
function name), and every functional pin is wired to a global net label so the
design reads cleanly and `kicad-cli sch erc` stays quiet on off-sheet nets.

Pinouts are transcribed directly from the OEM datasheets in
``avionics/datasheets/`` (authoritative per avionics/CLAUDE.md):
  * ISOW1044BDFMR  -> isow1044.pdf  Fig 7-1 / Table 7-1 (20-pin DFM)
  * ISOW1412DFMR   -> isow1412.pdf  Table 7-1 (20-pin DFM)
  * SLB9670 (TPM)  -> SLB_9670VQ20_Infineon.pdf Fig 1 (PG-VQFN-32-13)
  * SAM-M10Q       -> SAM-M10Q_DataSheet_UBX-22013293.pdf §3.1 (LGA module)
  * DS26LV31       -> ds26lv31qml.pdf Fig 1 Connection Diagram (SOIC-16)
  * DS26LV32AT     -> ds26lv32at.pdf  Fig 1 Connection Diagram (SOIC-16)
  * ADIN1300BCPZ   -> adin1300.pdf   pin table (40-LFCSP)

Coverage: **all 40 footprints on the Wash PCB**, at ERC = 0 errors — the isolated
buses (CAN / RS-485), TPM, GPS, the MIL-STD-1553B driver/receiver/transformer
chain, the Ethernet PHYs + magnetics, IMU, baro, the PCA9555 GPIO expander, both
PocketBeagle 2 stacking headers, every field connector, and the protection and
filter passives.

Pad-level parity with the board is 32/40.  The 8 that differ are all cases where
the board carries the wrong land pattern for the real part (e.g. a 16-pad
SOIC-16W under the 20-pin ISOW1044); those are enumerated in ``WBS.md`` §1.2a and
in ``sync_wash_pcb_nets.py``'s ``BLOCKED_WRONG_FOOTPRINT``, and are blocked on
footprint replacement, which is a user action per ``avionics/AGENTS.md``.

Progress checkpoints
--------------------
2026-07-14 (Opus 4.8): initial pass — CAN-TR, RS485, TPM, GPS + ADIN1300/magnetics.
2026-07-28 (Opus 5):
  * RS485 retargeted ADM2795EBRWZ (16-pin) -> ISOW1412DFMR (20-pin), which is what
    the PCB's 20-pad SOIC-20W land actually fits, per the 2026-07-26 fleet swap.
    The previous PCB net map had bus pins Y/Z/B/A unconnected and signals sitting
    on GNDIO/VDD/GND2 — i.e. the RS-485 port could not have worked.
  * Added 1553-DRV / 1553-RCV with datasheet-verified pinouts.  The prior PCB net
    map put M1553_TX_N on the driver's VCC pin (pad 16) and host PRU signals on
    driver *outputs*; both are corrected here.
  * Added PWR_FLAG emission so off-sheet-supplied rails clear
    `power_pin_not_driven` without inventing connectivity.
  * Authored the remaining 30 components (PB2-P1/P2, IMU, BARO, U-GPIO, 1553-XFM,
    field connectors, TVS/CMC/X2Y/ferrite passives), taking the sheet to full
    board coverage at ERC 0.  The ISO6442 RMII isolators were *dropped* rather
    than authored: galvanic isolation belongs in the line-side magnetics, and a
    general-purpose digital isolator cannot pass 50 MHz RMII REF_CLK.
  * Promoted to `Wash.kicad_sch` (the superseded hand-authored file is archived
    under `archives/avionics-archives/kicad-archives/Wash-superseded-2026-07-28/`).

Author: Claude (Opus 4.8), 2026-07-14; extended by Claude (Opus 5), 2026-07-28.
License: CC BY 4.0.
"""

from __future__ import annotations

import itertools
from pathlib import Path
from typing import Any, List, Tuple

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "kicads" / "Wash.kicad_sch"

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
        "ref": "CAN-TR",
        "value": "ISOW1044BDFMR",
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
        "ref": "RS485",
        "value": "ISOW1412DFMR",
        "ds": "isow1412.pdf Table 7-1 (20-pin DFM / SOIC-20W land)",
        # Fleet-wide ADM2795E -> ISOW1412 swap (2026-07-26): ISOW1412 integrates
        # its own isolated DC-DC, so no external isolated supply is needed.  The
        # 20-pad SOIC-20W land already on the PCB is correct for this part (the
        # WBS "wrong land, part is RW-16" item applied to the superseded
        # ADM2795E and is closed by this swap).
        #
        # Half-duplex on the 2-wire RS485_A/RS485_B bus per Wash.md §3: the
        # full-duplex driver outputs are shorted to the receiver inputs
        # (Y->A, Z->B), and RE (active low) is tied to DE so one direction
        # control line drives both.
        "pins": [
            ("1", "VIO", "+3V3", "L"),
            ("2", "D", "RS485_TX", "L"),
            ("3", "DE", "RS485_DE", "L"),
            ("4", "R", "RS485_RX", "L"),
            ("5", "RE", "RS485_DE", "L"),
            ("6", "GNDIO", "GND", "L"),
            ("7", "OUT", None, "L"),
            ("8", "EN/FLT", "+3V3", "L"),
            ("9", "VDD", "+3V3", "L"),
            ("10", "GND1", "GND", "L"),
            ("20", "A", "RS485_A", "R"),
            ("19", "B", "RS485_B", "R"),
            ("18", "Z", "RS485_B", "R"),
            ("17", "Y", "RS485_A", "R"),
            ("16", "VISOIN", "VCC2_RS485", "R"),
            ("15", "GISOIN", "GND2_RS485", "R"),
            ("14", "IN", None, "R"),
            ("13", "MODE", "GND2_RS485", "R"),
            ("12", "VISOOUT", "VCC2_RS485", "R"),
            ("11", "GND2", "GND2_RS485", "R"),
        ],
    },
    {
        "ref": "TPM",
        "value": "SLB9670",
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
            # NCI = not-connected-internally.  These carry no signal, but they
            # are real pads on the PG-VQFN-32 land, so the symbol must declare
            # them or sch<->pcb pad parity fails.  All emitted as no-connects.
            ("3", "NCI", None, "R"),
            ("4", "NCI", None, "R"),
            ("5", "NCI", None, "R"),
            ("10", "NCI", None, "R"),
            ("11", "NCI", None, "R"),
            ("12", "NCI", None, "R"),
            ("13", "NCI", None, "R"),
            ("14", "NCI", None, "R"),
            ("15", "NCI", None, "R"),
            ("16", "NCI", None, "R"),
            ("25", "NCI", None, "R"),
            ("26", "NCI", None, "R"),
            ("27", "NCI", None, "R"),
            ("28", "NCI", None, "R"),
            ("29", "NCI", None, "R"),
            ("30", "NCI", None, "R"),
            ("31", "NCI", None, "R"),
        ],
    },
    {
        "ref": "1553-DRV",
        "value": "DS26LV31",
        "ds": "ds26lv31qml.pdf Fig 1 Connection Diagram (SOIC-16)",
        # MIL-STD-1553B transmit path.  The PRU emits a complementary
        # Manchester pair (PRU_1553_TX_P / _N); each polarity drives its own
        # line-driver channel, and the two channel outputs form the
        # transformer-primary differential drive (M1553_P / _N).
        #
        # The transformer primary is SHARED with the receiver (half duplex),
        # so the drivers must tri-state while receiving: EN is driven by
        # M1553_TX_EN rather than strapped high.  EN* is held low so the
        # active-high EN alone controls the outputs.
        # ** M1553_TX_EN still needs a host pin allocated on the PB2 rails —
        #    open item, see WBS.md §1.2a. **
        # Channels 3/4 unused: inputs strapped to GND, outputs left open.
        "pins": [
            ("1", "DI1", "PRU_1553_TX_P", "L"),
            ("7", "DI2", "PRU_1553_TX_N", "L"),
            ("9", "DI3", "GND", "L"),
            ("15", "DI4", "GND", "L"),
            ("4", "EN", "M1553_TX_EN", "L"),
            ("12", "EN*", "GND", "L"),
            ("8", "GND", "GND", "L"),
            ("16", "VCC", "+3V3", "L"),
            ("2", "DO1+", "M1553_P", "R"),
            ("3", "DO1-", None, "R"),
            ("6", "DO2+", "M1553_N", "R"),
            ("5", "DO2-", None, "R"),
            ("10", "DO3+", None, "R"),
            ("11", "DO3-", None, "R"),
            ("14", "DO4+", None, "R"),
            ("13", "DO4-", None, "R"),
        ],
    },
    {
        "ref": "1553-RCV",
        "value": "DS26LV32AT",
        "ds": "ds26lv32at.pdf Fig 1 Connection Diagram (SOIC-16)",
        # MIL-STD-1553B receive path.  The transformer primary receive pair
        # (M1553_RX_P / _N) feeds two receiver channels wired in opposite
        # polarity, regenerating the complementary logic pair the PRU
        # Manchester decoder expects (PRU_1553_RX_P / _N).
        # Both enables asserted.  Channels 3/4 unused: inputs open (the part
        # has an OPEN-input failsafe), outputs left open.
        "pins": [
            ("2", "RI1+", "M1553_P", "L"),
            ("1", "RI1-", "M1553_N", "L"),
            ("6", "RI2+", "M1553_N", "L"),
            ("7", "RI2-", "M1553_P", "L"),
            ("10", "RI3+", None, "L"),
            ("9", "RI3-", None, "L"),
            ("14", "RI4+", None, "L"),
            ("15", "RI4-", None, "L"),
            ("4", "EN", "+3V3", "R"),
            ("12", "EN*", "GND", "R"),
            ("8", "GND", "GND", "R"),
            ("16", "VCC", "+3V3", "R"),
            ("3", "RO1", "PRU_1553_RX_P", "R"),
            ("5", "RO2", "PRU_1553_RX_N", "R"),
            ("11", "RO3", None, "R"),
            ("13", "RO4", None, "R"),
        ],
    },
    {
        "ref": "GPS",
        "value": "SAM-M10Q-00B",
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
        "ref": ref,
        "value": "ADIN1300BCPZ",
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
        "ref": ref,
        "value": "749010012A",
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


# ---------------------------------------------------------------------------
# Sensors / expander.
# ---------------------------------------------------------------------------
ICS += [
    {
        "ref": "IMU",
        "value": "ICM-42688-P",
        "ds": "ds-000347-icm-42688-p-v1.6.pdf Table 10 (LGA-14), 4-wire SPI",
        # The prior PCB map was scrambled (SPI0_MOSI on the SDO *output*,
        # SPI0_MISO on VDDIO).  Corrected to the datasheet 4-wire SPI mode.
        # Pin 7 RESV is "Connect to GND" (mandatory); the other RESV pins are
        # "No Connect or Connect to GND" and are grounded here for EMI.
        "pins": [
            ("1", "AP_SDO", "SPI0_MISO", "L"),
            ("14", "AP_SDI", "SPI0_MOSI", "L"),
            ("13", "AP_SCLK", "SPI0_CLK", "L"),
            ("12", "AP_CS", "SPI0_CS_IMU", "L"),
            ("4", "INT1", "IMU_INT1", "L"),
            ("9", "INT2/FSYNC", "IMU_INT2", "L"),
            ("5", "VDDIO", "+3V3", "R"),
            ("8", "VDD", "+3V3", "R"),
            ("6", "GND", "GND", "R"),
            ("7", "RESV(GND)", "GND", "R"),
            ("2", "RESV", "GND", "R"),
            ("3", "RESV", "GND", "R"),
            ("10", "RESV", "GND", "R"),
            ("11", "RESV", "GND", "R"),
        ],
    },
    {
        "ref": "BARO",
        "value": "BMP388",
        "ds": "bst-bmp388-ds001.pdf Table 50 Pin description (10-pin LGA), SPI 4W",
        # NOTE: the PCB currently carries an 8-pad land; BMP388 is a 10-pin
        # part (WBS.md §1.2a footprint item).  Footprint replacement is a
        # PCB-side action for the user; the symbol here is datasheet-correct.
        "pins": [
            ("2", "SCK", "SPI0_CLK", "L"),
            ("4", "SDI", "SPI0_MOSI", "L"),
            ("5", "SDO", "SPI0_MISO", "L"),
            ("6", "CSB", "SPI0_CS_BARO", "L"),
            ("7", "INT", "BARO_INT", "L"),
            ("1", "VDDIO", "+3V3", "R"),
            ("10", "VDD", "+3V3", "R"),
            ("3", "VSS", "GND", "R"),
            ("8", "VSS", "GND", "R"),
            ("9", "VSS", "GND", "R"),
        ],
    },
    {
        "ref": "U-GPIO",
        "value": "PCA9555DB",
        "ds": "PCA9555.pdf Table 3 Pin description (SSOP24)",
        # A0/A1/A2 strapped low => I2C address 0x20 (matches WBS §1.2a.1).
        # Port 0 bits 0-5 drive the six GPIO-A..F field connectors; the rest
        # of port 0 and all of port 1 are spare and left open.
        "pins": [
            ("22", "SCL", "I2C1_SCL", "L"),
            ("23", "SDA", "I2C1_SDA", "L"),
            ("1", "INT", None, "L"),
            ("21", "A0", "GND", "L"),
            ("2", "A1", "GND", "L"),
            ("3", "A2", "GND", "L"),
            ("24", "VDD", "+3V3", "L"),
            ("12", "VSS", "GND", "L"),
            ("4", "IO0_0", "GPIO_EXP_A", "R"),
            ("5", "IO0_1", "GPIO_EXP_B", "R"),
            ("6", "IO0_2", "GPIO_EXP_C", "R"),
            ("7", "IO0_3", "GPIO_EXP_D", "R"),
            ("8", "IO0_4", "GPIO_EXP_E", "R"),
            ("9", "IO0_5", "GPIO_EXP_F", "R"),
            ("10", "IO0_6", None, "R"),
            ("11", "IO0_7", None, "R"),
            ("13", "IO1_0", None, "R"),
            ("14", "IO1_1", None, "R"),
            ("15", "IO1_2", None, "R"),
            ("16", "IO1_3", None, "R"),
            ("17", "IO1_4", None, "R"),
            ("18", "IO1_5", None, "R"),
            ("19", "IO1_6", None, "R"),
            ("20", "IO1_7", None, "R"),
        ],
    },
    {
        "ref": "1553-XFM",
        "value": "SM1553-028",
        "ds": "SM1553-Series...RevD.pdf SCHEMATIC (8-pin, pri 1-3 CT 2, sec 4-8)",
        # MIL-STD-1553B isolation transformer.  Primary 1-3 is shared by the
        # DS26LV31 driver outputs and the DS26LV32 receiver inputs (half
        # duplex: the driver tri-states while receiving).  Secondary 4-8 is the
        # field bus.  Centre tap (2) and the intermediate secondary taps
        # (5/6/7) are unused on this 1.4:1 configuration.
        # NOTE: the PCB carries a 2-pad placeholder land — a real SM1553
        # footprint must be authored and placed (WBS.md §1.2a).
        "pins": [
            ("1", "PRI_P", "M1553_P", "L"),
            ("2", "PRI_CT", None, "L"),
            ("3", "PRI_N", "M1553_N", "L"),
            ("4", "SEC_1", "BUS_1553_P", "R"),
            ("5", "SEC_2", None, "R"),
            ("6", "SEC_3", None, "R"),
            ("7", "SEC_4", None, "R"),
            ("8", "SEC_5", "BUS_1553_N", "R"),
        ],
    },
]


# ---------------------------------------------------------------------------
# PocketBeagle 2 Industrial stacking headers.  Net assignment is the board's
# established P1/P2 map (all 72 pins were already fully netted on the PCB and
# are self-consistent with the signal names used across this sheet).
# ---------------------------------------------------------------------------
PB2_P1 = [
    "GND", "GND", "DSHOT3", "DSHOT2", "DSHOT1", "DSHOT0",
    "PRU_1553_RX_N", "PRU_1553_RX_P", "PRU_1553_TX_N", "PRU_1553_TX_P",
    "RS485_DE", "RS485_RX", "RS485_TX", "CAN_STB", "MCAN0_RX", "MCAN0_TX",
    "BARO_INT", "IMU_INT2", "IMU_INT1", "SPI0_CS_1553", "SPI0_CS_TPM",
    "SPI0_CS_BARO", "SPI0_MISO", "SPI0_MOSI", "SPI0_CLK", "SPI0_CS_IMU",
    "I2C1_SDA", "I2C1_SCL", "UART_ESC_RX", "UART_ESC_TX", "UART_GPS_RX",
    "UART_GPS_TX", "+3V3", "+3V3", "+5V", "GND",
]
PB2_P2 = [
    "MDIO1", "MDC1", "SERVO5", "SERVO4", "SERVO3", "SERVO2", "SERVO1",
    "SERVO0", "GPS_RESETN", "GPS_TIMEPULSE", "TPM_RSTN", "TPM_IRQN",
    "PHY2_RSTN", "PHY2_INTRN", "PHY1_RSTN", "PHY1_INTRN", "MDIO0", "MDC0",
    "RMII1_REF_CLK", "RMII1_RX_ER", "RMII1_CRS_DV", "RMII1_RXD1",
    "RMII1_RXD0", "RMII1_TX_EN", "RMII1_TXD1", "RMII1_TXD0",
    "RMII0_REF_CLK", "RMII0_RX_ER", "RMII0_CRS_DV", "RMII0_RXD1",
    "RMII0_RXD0", "RMII0_TX_EN", "RMII0_TXD1", "RMII0_TXD0", "+5V", "GND",
]


def pb2_header(ref, value, nets):
    """2x18 PocketBeagle 2 socket rail; pins 1-18 left, 19-36 right."""
    pins = []
    for i, net in enumerate(nets, start=1):
        pins.append((str(i), f"P{i}", net, "L" if i <= 18 else "R"))
    return {"ref": ref, "value": value, "ds": "PocketBeagle 2 P1/P2 expansion rails", "pins": pins}


ICS += [
    pb2_header("PB2-P1", "PB2I-P1-2x18", PB2_P1),
    pb2_header("PB2-P2", "PB2I-P2-2x18", PB2_P2),
]


# ---------------------------------------------------------------------------
# Field connectors, protection and passives.
#
# Two bus-filter defects present on the PCB are corrected here:
#   * SRF2012 common-mode chokes: the Bourns datasheet schematic gives windings
#     1-2 and 4-3.  The PCB had CAN_H on pads 1 AND 3 with CAN_L on 2 AND 4,
#     which puts a winding directly across the differential pair — i.e. it
#     SHORTED CAN_H to CAN_L (same on RS-485).  Correct wiring takes the
#     transceiver-side net in on 1/4 and brings the filtered net out on 2/3.
#   * FB1 ferrite bead had +5V on both pads (bead shorted out).  The power
#     entry is now PWR-IN -> +5V_IN -> FB1 -> +5V, per Wash.md §6.
# TVS arrays sit on the filtered/connector side per Wash.md §5.
# ---------------------------------------------------------------------------
SIMPLE = [
    # --- power entry -------------------------------------------------------
    ("PWR-IN", "Molex Nano-Fit 4P", "Wash.md §14 power entry",
     [("1", "+5V_IN", "+5V_IN"), ("2", "+5V_IN", "+5V_IN"),
      ("3", "GND", "GND"), ("4", "GND", "GND")]),
    ("FB1", "742792512 600R@100MHz", "Wash.md §6 power-entry pi filter",
     [("1", "IN", "+5V_IN"), ("2", "OUT", "+5V")]),
    # --- CAN FD field port -------------------------------------------------
    ("CMC-CAN", "SRF2012-100Y", "SRF2012A.pdf schematic (windings 1-2, 4-3)",
     [("1", "W1_IN", "CAN_H"), ("2", "W1_OUT", "CAN_H_F"),
      ("4", "W2_IN", "CAN_L"), ("3", "W2_OUT", "CAN_L_F")]),
    ("TVS-CAN", "PRTR5V0U2X", "Wash.md §5 dual TVS at CAN field connector",
     [("1", "IO1", "CAN_H_F"), ("2", "GND", "GND2_CAN"),
      ("3", "IO2", "CAN_L_F"), ("4", "NC", None),
      ("5", "VCC", "VCC2_CAN"), ("6", "NC", None)]),
    ("CAN-FD", "JST SM04B-GHS-TB", "Wash.md §14 J_CAN",
     [("1", "GND", "GND2_CAN"), ("2", "CAN_H", "CAN_H_F"),
      ("3", "CAN_L", "CAN_L_F"), ("4", "VCC", "VCC2_CAN")]),
    ("X2Y-CAN", "X2Y 4.7nF", "Wash.md §2 GND1<->GND2 RF bridge",
     [("1", "G1", "GND"), ("2", "G1", "GND"),
      ("3", "G1", "GND"), ("4", "G2", "GND2_CAN")]),
    # --- RS-485 field port -------------------------------------------------
    ("CMC-RS485", "SRF2012-100Y", "SRF2012A.pdf schematic (windings 1-2, 4-3)",
     [("1", "W1_IN", "RS485_A"), ("2", "W1_OUT", "RS485_A_F"),
      ("4", "W2_IN", "RS485_B"), ("3", "W2_OUT", "RS485_B_F")]),
    ("TVS-RS485", "PRTR5V0U2X", "Wash.md §5 dual TVS at RS-485 field connector",
     [("1", "IO1", "RS485_A_F"), ("2", "GND", "GND2_RS485"),
      ("3", "IO2", "RS485_B_F"), ("4", "NC", None),
      ("5", "VCC", "VCC2_RS485"), ("6", "NC", None)]),
    ("RS-485", "JST SM04B-GHS-TB", "Wash.md §14 J_485",
     [("1", "GND", "GND2_RS485"), ("2", "A", "RS485_A_F"),
      ("3", "B", "RS485_B_F"), ("4", "VCC", "VCC2_RS485")]),
    ("X2Y-RS485", "X2Y 4.7nF", "Wash.md §3 GND1<->GND2 RF bridge",
     [("1", "G1", "GND"), ("2", "G1", "GND"),
      ("3", "G1", "GND"), ("4", "G2", "GND2_RS485")]),
    # --- Ethernet line-side connectors -------------------------------------
    ("ETH1", "JST SM04B-GHS-TB", "ETH1 line pair to T-ETH secondary",
     [("1", "TXP", "ETH_LINE_TXP"), ("2", "TXN", "ETH_LINE_TXN"),
      ("3", "RXP", "ETH_LINE_RXP"), ("4", "RXN", "ETH_LINE_RXN")]),
    ("ETH2", "JST SM04B-GHS-TB", "ETH2 line pair to T-ETH2 secondary",
     [("1", "TXP", "ETH2_LINE_TXP"), ("2", "TXN", "ETH2_LINE_TXN"),
      ("3", "RXP", "ETH2_LINE_RXP"), ("4", "RXN", "ETH2_LINE_RXN")]),
    # --- MIL-STD-1553B field port ------------------------------------------
    ("TVS-1553", "SMAJ33CA", "Wash.md §5 bidirectional TVS, bus line to PGND",
     [("1", "A", "BUS_1553_P"), ("2", "K", "PGND")]),
    ("MIL-1553", "JST SM04B-GHS-TB", "Wash.md §14 J_1553",
     [("1", "BUS_P", "BUS_1553_P"), ("2", "BUS_N", "BUS_1553_N"),
      ("3", "GND", "GND"), ("4", "SHIELD", "PGND")]),
    # --- ESC / servo / GPIO field ports ------------------------------------
    ("ESC-PWM", "JST SM05B-GHS-TB-1MP", "Wash.md §14 J_ESC (DSHOT0-3)",
     [("1", "DSHOT0", "DSHOT0"), ("2", "DSHOT1", "DSHOT1"),
      ("3", "DSHOT2", "DSHOT2"), ("4", "DSHOT3", "DSHOT3"),
      ("5", "GND", "GND"), ("MP", "SHIELD", "PGND")]),
    ("ESC-TLM", "JST SM03B-GHS-TB", "ESC telemetry UART",
     [("1", "GND", "GND"), ("2", "TX", "UART_ESC_TX"),
      ("3", "RX", "UART_ESC_RX")]),
    ("SERVO-PWM", "PinHeader 2.54mm 1x08", "Wash.md §14 J_SERVO (6 ch + pwr)",
     [("1", "SERVO0", "SERVO0"), ("2", "SERVO1", "SERVO1"),
      ("3", "SERVO2", "SERVO2"), ("4", "SERVO3", "SERVO3"),
      ("5", "SERVO4", "SERVO4"), ("6", "SERVO5", "SERVO5"),
      ("7", "+5V", "+5V"), ("8", "GND", "GND")]),
    ("C-GPIO", "100nF 0805", "PCA9555 VDD decoupling",
     [("1", "P", "+3V3"), ("2", "N", "GND")]),
]
SIMPLE += [
    (f"GPIO-{c}", "JST SM03B-GHS-TB", f"GPIO expander field port {c}",
     [("1", "GND", "GND"), ("2", "+3V3", "+3V3"), ("3", "SIG", f"GPIO_EXP_{c}")])
    for c in "ABCDEF"
]

for _ref, _val, _ds, _pins in SIMPLE:
    _n = len(_pins)
    _half = (_n + 1) // 2
    ICS.append({
        "ref": _ref,
        "value": _val,
        "ds": _ds,
        "pins": [
            (pn, fn, net, "L" if i < _half else "R")
            for i, (pn, fn, net) in enumerate(_pins)
        ],
    })


def lib_symbol(
    ic,
) -> Tuple[
    str, List[Tuple[str, str, Any, str]], List[Tuple[str, str, Any, str]], float, float
]:
    """
    Build the KiCad symbol definition for a single IC.

    Returns
    -------
    tuple
        * **symbol_str** – the KiCad S‑expression for the symbol (a single
        multi‑line string);
        * **left** – list of left‑side pins (each a 4‑tuple);
        * **right** – list of right‑side pins (each a 4‑tuple);
        * **half_w** – half‑width of the symbol box (float);
        * **half_h** – half‑height of the symbol box (float).
    """
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
    s += [
        "      )",
        "    )",
    ]  # The function returns a tuple; the first element is the multi‑line KiCad    # symbol definition, the remaining elements are used later for placement.
    return "\n".join(s), left, right, half_w, half_h


def pin_def(x, y, ang, pn, fn):
    """
    Create a KiCad pin definition.

    Parameters
    ----------
    x, y : float
        Pin coordinates.
    ang : int
        Rotation angle (0, 90, 180, 270).
    pn : str
        Pin number (as it appears on the component).
    fn : str | None
        Pin function name. May be ``None`` for pins that carry no signal.

    Returns
    -------
    str
        The KiCad‑compatible pin description.
    """
    # Pins that are power‑in (GND or EP) are drawn with a different style.
    # If *fn* is ``None`` (or any other string) we fall back to a normal
    # passive pin.
    etype = "power_in" if isinstance(fn, str) and fn in ("GND", "EP") else "passive"

    return (
        f"        (pin {etype} line (at {x:.2f} {y:.2f} {ang}) "
        f"(length {PIN_PITCH}) "
        f'(name "{esc(fn) if fn is not None else ""}" '
        f"(effects (font (size {SIZE} {SIZE})))) "
        f'(number "{esc(pn)}" '
        f"(effects (font (size {SIZE} {SIZE})))))"
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


# Rails that are supplied from off-sheet (the PB2 stack / PWR-IN connector) and
# therefore have no power_out pin on this sheet.  A PWR_FLAG tells ERC each one
# is genuinely driven, clearing `power_pin_not_driven` on the GND/EP power pins
# without falsifying any connectivity.  Remove a rail from this list once a real
# supply symbol for it is authored onto the sheet.
PWR_FLAG_RAILS = ["GND", "+3V3", "GND2_CAN", "GND2_RS485", "PGND"]

PWR_FLAG_LIB = """    (symbol "PWR_FLAG" (power) (pin_numbers hide) (pin_names (offset 0) hide) \
(exclude_from_sim yes) (in_bom no) (on_board no)
      (property "Reference" "#FLG" (at 0 1.905 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (property "Value" "PWR_FLAG" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
      (symbol "PWR_FLAG_0_0"
        (pin power_out line (at 0 0 90) (length 0) (name "~" \
(effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
      )
      (symbol "PWR_FLAG_0_1"
        (polyline (pts (xy 0 0) (xy 0 1.27) (xy -1.016 1.905) (xy 0 2.54) \
(xy 1.016 1.905) (xy 0 1.27)) (stroke (width 0) (type default)) (fill (type none)))
      )
    )"""


def emit_pwr_flags(x0, y0, sheet_uuid):
    """Place one PWR_FLAG per off-sheet-supplied rail, wired to its net label."""
    out = []
    for i, rail in enumerate(PWR_FLAG_RAILS):
        x = x0 + i * 20.32
        out.append(
            f'  (symbol (lib_id "PWR_FLAG") (at {x:.2f} {y0:.2f} 0) (unit 1)\n'
            f"    (exclude_from_sim yes) (in_bom no) (on_board no) (dnp no)\n"
            f'    (uuid "{uid()}")\n'
            f'    (property "Reference" "#FLG{i + 1}" (at {x:.2f} {y0 - 2.54:.2f} 0) '
            f"(effects (font (size 1.27 1.27)) (hide yes)))\n"
            f'    (property "Value" "PWR_FLAG" (at {x:.2f} {y0 - 5.08:.2f} 0) '
            f"(effects (font (size 1.27 1.27))))\n"
            f'    (instances (project "Wash_rebuild" (path "/{sheet_uuid}" '
            f'(reference "#FLG{i + 1}") (unit 1)))))'
        )
        out.append(wire(x, y0, x, y0 + STUB))
        out.append(label(rail, x, y0 + STUB, 270))
    return out


def main():
    sheet_uuid = uid()
    parts = [
        "(kicad_sch (version 20240101) (generator eeschema)",
        f'  (uuid "{uid()}")',
        '  (paper "A2")',
        "  (lib_symbols",
        PWR_FLAG_LIB,
    ]
    # Column-packed layout: symbols vary from 2 to 36 pins, so a fixed row
    # pitch either overlaps the tall parts or wastes metres of sheet.  Walk
    # each column top-down using the actual symbol height plus room for the
    # net-label stubs, and start a new column once the current one is full.
    placed = []
    X0, Y0, DX = 76.2, 76.2, 127.0
    COL_MAX_Y = 1600.0
    x, y = X0, Y0
    built = []
    for ic in ICS:
        libtext, left, right, hw, hh = lib_symbol(ic)
        parts.append(libtext)
        built.append((ic, left, right, hw, hh))
    for ic, left, right, hw, hh in built:
        if y + hh > COL_MAX_Y and y > Y0:
            x += DX
            y = Y0
        placed.append((ic, x, y + hh, left, right, hw, hh))
        y += 2 * hh + 25.4
    parts.append("  )")
    for ic, X, Y, left, right, hw, hh in placed:
        parts += emit_instance(ic, X, Y, left, right, hw, hh, sheet_uuid)
    parts += emit_pwr_flags(X0, Y0 - 45.72, sheet_uuid)
    parts.append('  (sheet_instances (path "/" (page "1")))')
    parts.append(")")
    OUT.write_text("\n".join(parts) + "\n")
    npins = sum(len(ic["pins"]) for ic in ICS)
    print(f"Wrote {OUT}")
    print(f"  ICs: {len(ICS)}  ({', '.join(ic['ref'] for ic in ICS)})")
    print(f"  total datasheet pins emitted: {npins}")


if __name__ == "__main__":
    main()
