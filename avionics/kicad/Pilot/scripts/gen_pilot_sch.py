#!/usr/bin/env python3
"""gen_pilot_sch.py — Author the datasheet-accurate Pilot (CAPE-A-2) schematic.

Schematic-first rebuild of the Pilot flight-control cape (PocketBeagle 2
Industrial cape, 55 x 35 mm, 4-layer).  Every IC is emitted as a rectangular
symbol carrying its FULL datasheet pinout (pin number + function name), every
functional pin is wired to a global net label, and every symbol carries the
footprint that the PCB generator (``gen_pilot_pcb.py``) places.  Connectivity is
by net name, so ``kicad-cli sch erc`` and the PCB net-sync both read from one
authoritative table: the ``ICS`` / ``SIMPLE`` lists below.

Lineage
-------
* 2026-07-14 (Claude Opus 4.8) — first pass: CAN-TR, RS485, TPM, GPS.
* 2026-07-28 (Claude Opus 5, as ``gen_wash_sch.py`` on branch
  ``don't-let-all-the-air-out``) — all 40 board footprints at ERC 0; five latent
  board defects fixed (SRF2012 winding short, FB1 short, RS-485 bus pins
  floating, 1553 driver VCC carrying a signal, IMU SPI scrambled).  That branch
  was never merged; this file ports it forward under the 2026-08-01 call-sign
  rename (Wash -> Pilot).
* 2026-09-19 (Claude Opus 5) — completion pass to a fabricable board:
    - GNSS receiver changed SAM-M10Q -> **MAX-M10S** (external antenna): the
      nodes fly in Faraday pouches with the antennas in dorsal cups, so an
      integrated patch could never see the sky; also the 16-pin SAM symbol had
      omitted VCC.  Bias-T per the integration manual.  [REF-SENSOR-027]
    - 749010012A re-authored with all **16** mechanical pads (4/5/12/13 NC)
      so schematic pad count == land pad count.  [REF-SENSOR-028]
    - TPM re-pinned to the **SLB 9672** map (VDD 1/14/22, GND 2/9/23/32,
      16 = NCI/GND, 10 = NCI/VDD pull-up, 6/29/30 must float).
      [REF-SENSOR-011] Tables 11-13, Figure 6.
    - Ethernet PHY: 2026-09-19 ideation (docs/ideation/2026-09-19-pilot-cape-
      four-bus-area-ideation.html, owner-selected #1 #2 #5) returned the PHY to
      the DP83825I the architecture specifies (AVIONICS_PB2_REDESIGN.md §3.1
      U8): WQFN-24 3x3, single 3.3 V, RMII Leader mode sourcing 50MHzOut to
      the SoC from one shared 25 MHz oscillator; RBIAS 6.49 k, PhyAdd[0]
      strap, Fig 8-4 decoupling, Fig 8-3 TPI network (device-side centre taps
      0.1 uF + 1 uF to GND, line-side 75 R x2 + 10 nF/2 kV to PGND).  The
      interim ADIN1300 + 0.9 V LDO + 50 MHz-per-port design is superseded.
    - MIL-STD-1553B: compliant Holt HI-1573 (3.3 V, QFN-44) + Premier
      PM-DB2791S 1:2.5 direct-coupled stub + 2 x 55 R + 2 x SMAJ33CA; the
      RS-422 DS26LV31/32 chain (cannot meet §4.5.2 levels) is retired.
    - PWM/DSHOT block: Samtec TSM-108-01-L-DV 2x8 SMT 0.1 in header (SIG /
      +5V / GND / PGND-shield per channel) so B.Cu under it stays usable;
      0201 for straps, pull-ups and 10 nF HF bypass.
    - Cape-local +3V3 buck (TPS62933, [REF-PWR-001]) so the cape does not
      depend on the PocketBeagle 2's 3.3 V rail budget; PB2 3.3 V pins are
      renamed ``+3V3_PB2`` and left unloaded.
    - ISOW1044 / ISOW1412 DC-DC input (VDD) moved to +5V, logic VIO on
      +3V3; bypass per [REF-SENSOR-009] §13.1 / [REF-SENSOR-010].
    - Bob-Smith line-side termination (75 R + 1 nF/2 kV to PGND) on each
      LAN transformer.  MIL-STD-1553B section removed (RS-422 drivers cannot
      meet §4.5.2 levels; no board area) — see the SIMPLE list comment.
    - PGND<->GND single-point 0 R link, mounting holes on PGND (Pilot.md §7).
    - GPIO ports + J_ESC/J_SERVO replaced by ONE 3x6 servo/ESC header on the
      PRU DSHOT0-3 / SERVO0-1 balls (PWM/DSHOT-capable), PCA9555 removed.

Datasheets (all in ``avionics/datasheets/``; OEM documents are authoritative
per ``avionics/AGENTS.md``):
  ISOW1044BDFMR isow1044.pdf Table 7-1 | ISOW1412DFMR isow1412.pdf Table 7-1 |
  SLB9672 slb9672.pdf §3.1.2 | MAX-M10S MAX-M10S_DataSheet_UBX-20035208.pdf §3.1 |
  DP83825I dp83825i.pdf Table 4-1/6-8..6-11, Fig 8-3/8-4 | 749010012A 749010012A.pdf p.1 |
  HI-1573 hi-1573.pdf p.1/p.11 | PM-DB2791S PremierMagnetics_DB2791S.pdf | Samtec TSM samtec_tsm-dv-footprint.pdf |
  ICM-42688-P ds-000347 Table 10 | BMP388 bst-bmp388-ds001.pdf Table 50 |
  SRF2012A SRF2012A.pdf | TPS62933 tps62933.pdf Table 7-1 |
  ECS-2520MV ECS-2520MV.pdf p.1 |
  X2Y (Yageo CX0805) X2Y_15-2237598.pdf Table 3.

Author: Claude Opus 4.8 (2026-07-14); Claude Opus 5 (2026-07-28, 2026-09-19).
Human owner: sgriffing (Griffing Technology LLC).  License: CC BY 4.0.
"""

from __future__ import annotations

import itertools
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "kicads" / "Pilot.kicad_sch"
SYMLIB = HERE.parent / "kicads" / "Pilot.kicad_sym"

SIZE = 1.27
PIN_PITCH = 2.54
STUB = 2.54
_uid = itertools.count(1)

# --- footprint library nicknames -------------------------------------------
FP_C0201 = "Capacitor_SMD:C_0201_0603Metric"
FP_C0402 = "Capacitor_SMD:C_0402_1005Metric"
FP_C0603 = "Capacitor_SMD:C_0603_1608Metric"
FP_C0805 = "Capacitor_SMD:C_0805_2012Metric"
FP_C1210 = "Capacitor_SMD:C_1210_3225Metric"
FP_C1808 = "Capacitor_SMD:C_1808_4520Metric"
FP_R0201 = "Resistor_SMD:R_0201_0603Metric"
FP_R0402 = "Resistor_SMD:R_0402_1005Metric"
FP_R0603 = "Resistor_SMD:R_0603_1608Metric"
FP_R0805 = "Resistor_SMD:R_0805_2012Metric"
FP_L0805 = "Inductor_SMD:L_0805_2012Metric"
FP_SOIC20W = "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm"
FP_UQFN32 = "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.6x3.6mm"
FP_WQFN24 = "Package_DFN_QFN:Texas_RMQ0024A_WQFN-24-1EP_3x3mm_P0.4mm_EP1.9x1.9mm"
FP_QFN44 = "Package_DFN_QFN:QFN-44-1EP_7x7mm_P0.5mm_EP5.2x5.2mm"
FP_SMA = "Diode_SMD:D_SMA"
FP_X1553 = "Serenity-Custom:Xfmr_1553_SMD_0.40in_8pin"
FP_TSM2X8 = "Serenity-Custom:Samtec_TSM-108-01-x-DV"
FP_LGA14 = "Package_LGA:Bosch_LGA-14_3x2.5mm_P0.5mm"
FP_SOT583 = "Package_TO_SOT_SMD:SOT-583-8"
FP_SOT363 = "Package_TO_SOT_SMD:SOT-363_SC-70-6"
FP_OSC2520 = "Oscillator:Oscillator_SMD_ECS_2520MV-xxx-xx-4Pin_2.5x2.0mm"
FP_GH4 = "Connector_JST:JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal"
FP_HOLE = "Serenity-Custom:MountingHole_2.7mm_M2.5_PGND_Ring"
# project-custom lands (avionics/kicad/Serenity-Custom.pretty)
FP_SAM = "Serenity-Custom:uBlox_SAM-M10Q-00B"
FP_WELAN = "Serenity-Custom:Wurth_749010012A_WE-LAN"
FP_BMP388 = "Serenity-Custom:Bosch_BMP388_LGA-10_2x2mm"
FP_X2Y0805 = "Serenity-Custom:X2Y_0805_4T"
FP_SRF2012 = "Serenity-Custom:Bourns_SRF2012_4T"
FP_NANOFIT = "Serenity-Custom:Molex_NanoFit_1x04_Horizontal"
FP_PB2P1 = "Serenity-Custom:PocketBeagle2_2x18_P1_Socket"
FP_PB2P2 = "Serenity-Custom:PocketBeagle2_2x18_P2_Socket"
FP_L3015 = "Serenity-Custom:L_WE-MAPI_3015"


def uid() -> str:
    return f"a3000000-0000-0000-0000-{next(_uid):012d}"


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def sanitize(ref: str) -> str:
    return re.sub(r"[^A-Za-z0-9_+.-]", "_", ref)


# ---------------------------------------------------------------------------
# Datasheet-transcribed pinouts.  Each entry: (pin_number, function, net|None,
# side).  net=None -> emitted as a no-connect.  side "L"/"R" = left/right.
# ---------------------------------------------------------------------------
ICS: List[Dict[str, Any]] = [
    {
        "ref": "CAN-TR",
        "value": "ISOW1044BDFMR",
        "fp": FP_SOIC20W,
        "mpn": "ISOW1044BDFMR",
        "ds": "isow1044.pdf Fig 7-1 / Table 7-1 (20-pin DFM) [REF-SENSOR-009]",
        # DC-DC input VDD on +5V (3-5.5 V allowed), logic VIO on +3V3.
        "pins": [
            ("1", "VIO", "+3V3", "L"),
            ("2", "IN", None, "L"),
            ("3", "TXD", "MCAN0_TX", "L"),
            ("4", "STB", "CAN_STB", "L"),
            ("5", "RXD", "MCAN0_RX", "L"),
            ("6", "GNDIO", "GND", "L"),
            ("7", "NC", None, "L"),
            ("8", "EN/FLT", None, "L"),
            ("9", "VDD", "+5V", "L"),
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
        "fp": FP_SOIC20W,
        "mpn": "ISOW1412DFMR",
        "ds": "isow1412.pdf Table 7-1 (20-pin DFM) [REF-SENSOR-010]",
        # Half duplex on the 2-wire bus: Y->A, Z->B; RE(active low) tied to DE.
        # MODE = GND2 -> 3.3 V isolated-side transceiver supply.
        "pins": [
            ("1", "VIO", "+3V3", "L"),
            ("2", "D", "RS485_TX", "L"),
            ("3", "DE", "RS485_DE", "L"),
            ("4", "R", "RS485_RX", "L"),
            ("5", "RE", "RS485_DE", "L"),
            ("6", "GNDIO", "GND", "L"),
            ("7", "OUT", None, "L"),
            ("8", "EN/FLT", "+3V3", "L"),
            ("9", "VDD", "+5V", "L"),
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
        "value": "SLB9672XU20",
        "fp": FP_UQFN32,
        "mpn": "SLB9672XU20FW1611XUMA1",
        "ds": "slb9672.pdf §3.1.2 Tables 11-13 / Figure 6 (PG-UQFN-32) [REF-SENSOR-011]",
        "pins": [
            ("17", "RST#", "TPM_RSTN", "L"),
            ("18", "PIRQ#", "TPM_IRQN", "L"),
            ("19", "SCLK", "SPI0_CLK", "L"),
            ("20", "CS#", "SPI0_CS_TPM", "L"),
            ("21", "MOSI", "SPI0_MOSI", "L"),
            ("24", "MISO", "SPI0_MISO", "L"),
            ("3", "GPIO_00", None, "L"),
            ("4", "GPIO_01", None, "L"),
            ("7", "GPIO_02", None, "L"),
            ("1", "VDD", "+3V3", "R"),
            ("14", "VDD", "+3V3", "R"),
            ("22", "VDD", "+3V3", "R"),
            ("2", "GND", "GND", "R"),
            ("9", "GND", "GND", "R"),
            ("23", "GND", "GND", "R"),
            ("32", "GND", "GND", "R"),
            ("16", "NCI/GND", "GND", "R"),
            ("33", "EP", "GND", "R"),
            ("10", "NCI/VDD", "TPM_P10_PU", "R"),
            ("8", "NCI/VDD", None, "R"),
            # 6, 29, 30 = NC, must float (Table 13)
            ("6", "NC", None, "R"),
            ("29", "NC", None, "R"),
            ("30", "NC", None, "R"),
            # NCI (not connected internally) — real pads, no signal
            ("5", "NCI", None, "R"),
            ("11", "NCI", None, "R"),
            ("12", "NCI", None, "R"),
            ("13", "NCI", None, "R"),
            ("15", "NCI", None, "R"),
            ("25", "NCI", None, "R"),
            ("26", "NCI", None, "R"),
            ("27", "NCI", None, "R"),
            ("28", "NCI", None, "R"),
            ("31", "NCI", None, "R"),
        ],
    },
    {
        "ref": "GPS",
        "value": "MAX-M10S-00B",
        "fp": "RF_GPS:ublox_MAX",
        "mpn": "MAX-M10S-00B",
        "ds": "MAX-M10S_DataSheet_UBX-20035208.pdf §3.1 Fig 2 / Table 10 (18-pin LCC) [REF-SENSOR-027]",
        # External-antenna receiver: the nodes fly inside Faraday pouches in the
        # cargo bay with the GNSS patch antennas in the dorsal cups
        # (CARGO_SECTION_LAYOUT.md, AVIONICS_PB2_REDESIGN.md "GPS-ANT U.FL ->
        # SMA bulkhead"), so the earlier integrated-patch SAM-M10Q could never
        # see the sky.  Typical 3.3 V design (integration manual B.1 Fig 35):
        # VCC = V_IO = +3V3, VIO_SEL open, V_BCKP on +3V3 (no backup cell),
        # active antenna fed from VCC_RF through the 10 R / 27 nH bias-T
        # (integration manual Fig 37, Tables 52-54).
        "pins": [
            ("8", "VCC", "+3V3", "L"),
            ("7", "V_IO", "+3V3", "L"),
            ("6", "V_BCKP", "+3V3", "L"),
            ("2", "TXD", "UART_GPS_TX", "L"),
            ("3", "RXD", "UART_GPS_RX", "L"),
            ("4", "TIMEPULSE", "GPS_TIMEPULSE", "L"),
            ("9", "RESET_N", "GPS_RESETN", "L"),
            ("5", "EXTINT", None, "L"),
            ("18", "SAFEBOOT_N", None, "L"),
            ("11", "RF_IN", "GPS_RF", "R"),
            ("14", "VCC_RF", "GPS_VCC_RF", "R"),
            ("13", "LNA_EN", None, "R"),
            ("15", "VIO_SEL", None, "R"),
            ("16", "SDA", None, "R"),
            ("17", "SCL", None, "R"),
            ("1", "GND", "GND", "R"),
            ("10", "GND", "GND", "R"),
            ("12", "GND", "GND", "R"),
        ],
    },
]


def dp83825i(ref: str, rmii: str, rstn: str, intn: str, eth: str, mdio: str, mdc: str) -> Dict[str, Any]:
    """TI DP83825I 10/100 RMII PHY, WQFN-24 (RMQ0024A) — dp83825i.pdf Table 4-1.

    The PHY the architecture specified (AVIONICS_PB2_REDESIGN.md §3.1 "U8 |
    DP83825I x 2 | CPSW3G RMII"); replaces the ADIN1300 drift of Rev T (2026-09-19
    ideation #2).  RMII **Leader** mode (RX_D1 strap default 0): the PHY takes
    a 25 MHz reference on XI and sources the 50 MHz RMII clock to the SoC on
    pin 2 (50MHzOut), so no 50 MHz oscillator and no 0.9 V core rail exist.
    Single 3.3 V supply (VDDA3V3 + VDDIO at 3.3 V).  PHY address 1 via the
    RX_D0 PhyAdd[0] strap (Table 6-8/6-9: Rhi 2.49 k).  MDIO has a 10 k
    internal pull-up; RST_N and INTR/PWRDN have internal pull-ups.
    """
    return {
        "ref": ref,
        "value": "DP83825IRMQR",
        "fp": FP_WQFN24,
        "mpn": "DP83825IRMQR",
        "ds": "dp83825i.pdf Table 4-1 Pin Functions / Table 6-8..6-11 straps (WQFN-24 RMQ) [REF-SENSOR-029]",
        "pins": [
            ("1", "TX_EN", f"{rmii}_TX_EN", "L"),
            ("23", "TX_D0", f"{rmii}_TXD0", "L"),
            ("24", "TX_D1", f"{rmii}_TXD1", "L"),
            ("18", "RX_D0/PhyAdd0", f"{rmii}_RXD0", "L"),
            ("17", "RX_D1/Leader", f"{rmii}_RXD1", "L"),
            ("20", "CRS_DV/PhyAdd1", f"{rmii}_CRS_DV", "L"),
            ("22", "RX_ER/A-MDIX", f"{rmii}_RX_ER", "L"),
            ("2", "50MHzOut", f"{rmii}_REF_CLK", "L"),
            ("16", "MDC", mdc, "L"),
            ("15", "MDIO", mdio, "L"),
            ("5", "RST_N", rstn, "L"),
            ("3", "INTR/PWRDN", intn, "L"),
            ("4", "LED0/ANEG", None, "L"),
            ("13", "XI", "PHY_XI_25M", "R"),
            ("12", "XO", None, "R"),
            ("14", "RBIAS", f"{ref}_RBIAS", "R"),
            ("11", "TD_P", f"{eth}_TXP", "R"),
            ("10", "TD_M", f"{eth}_TXN", "R"),
            ("8", "RD_P", f"{eth}_RXP", "R"),
            ("7", "RD_M", f"{eth}_RXN", "R"),
            ("6", "VDDA3V3", "+3V3", "R"),
            ("19", "VDDIO", "+3V3", "R"),
            ("9", "GND", "GND", "R"),
            ("21", "GND", "GND", "R"),
            ("25", "EP", "GND", "R"),
        ],
    }


def eth_xfmr(ref: str, eth: str) -> Dict[str, Any]:
    """Wurth 749010012A WE-LAN 10/100 SMT transformer (749010012A.pdf p.1).
    16 mechanical pads; 4/5/12/13 have no winding.  PHY side 1-3 / 6-8,
    line side 9-11 / 14-16, 1:1 CT, 1500 V — this IS the Ethernet barrier."""
    return {
        "ref": ref,
        "value": "749010012A",
        "fp": FP_WELAN,
        "mpn": "749010012A",
        "ds": "749010012A.pdf p.1 Schematic + Recommended Land Pattern [REF-SENSOR-028]",
        "pins": [
            ("1", "TD+", f"{eth}_TXP", "L"),
            ("2", "CTD", f"{eth}_CTD", "L"),
            ("3", "TD-", f"{eth}_TXN", "L"),
            ("4", "NC", None, "L"),
            ("5", "NC", None, "L"),
            ("6", "RD+", f"{eth}_RXP", "L"),
            ("7", "CRD", f"{eth}_CRD", "L"),
            ("8", "RD-", f"{eth}_RXN", "L"),
            ("16", "TX+", f"{eth}_LINE_TXP", "R"),
            ("15", "CTX", f"{eth}_LINE_CTX", "R"),
            ("14", "TX-", f"{eth}_LINE_TXN", "R"),
            ("13", "NC", None, "R"),
            ("12", "NC", None, "R"),
            ("11", "RX+", f"{eth}_LINE_RXP", "R"),
            ("10", "CRX", f"{eth}_LINE_CRX", "R"),
            ("9", "RX-", f"{eth}_LINE_RXN", "R"),
        ],
    }


ICS += [
    dp83825i("ETH1-PHY", "RMII0", "PHY1_RSTN", "PHY1_INTRN", "ETH", "MDIO0", "MDC0"),
    dp83825i("ETH2-PHY", "RMII1", "PHY2_RSTN", "PHY2_INTRN", "ETH2", "MDIO1", "MDC1"),
    eth_xfmr("T-ETH", "ETH"),
    eth_xfmr("T-ETH2", "ETH2"),
]

ICS += [
    {
        "ref": "IMU",
        "value": "ICM-42688-P",
        "fp": FP_LGA14,
        "mpn": "ICM-42688-P",
        "ds": "ds-000347-icm-42688-p-v1.6.pdf Table 10 (LGA-14), 4-wire SPI [REF-SENSOR-022]",
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
        "fp": FP_BMP388,
        "mpn": "BMP388",
        "ds": "bst-bmp388-ds001.pdf Table 50 (10-pin LGA 2x2), SPI 4-wire [REF-SENSOR-023]",
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
        "ref": "1553-XCVR",
        "value": "HI-1573PCI",
        "fp": FP_QFN44,
        "mpn": "HI-1573PCI",
        "ds": "hi-1573.pdf p.1 Pin Configurations (44-pin 7x7 QFN) / p.11 package [REF-SENSOR-030]",
        # MIL-STD-1553B 3.3 V dual transceiver; only bus A is populated on Pilot
        # (bus B parked: RXENB low, TXINHB high, TXB/TXB* low).  Direct-coupled
        # stub per hi-1573.pdf Fig 2: 1:2.5 isolation transformer + 2 x 55 R,
        # primary centre tap to GND.  Manchester II encode/decode is in the
        # AM6254 PRU (AVIONICS_PB2_REDESIGN.md §94); TXINHA is the PRU's transmit
        # inhibit (active high) on P1-20.  Owner decision open: single (as
        # built) vs dual-redundant bus (second transformer + connector).
        "pins": [
            ("36", "TXA", "PRU_1553_TX_P", "L"),
            ("37", "TXA*", "PRU_1553_TX_N", "L"),
            ("31", "TXINHA", "M1553_TX_INH", "L"),
            ("2", "RXENA", "+3V3", "L"),
            ("30", "RXA", "PRU_1553_RX_P", "L"),
            ("29", "RXA*", "PRU_1553_RX_N", "L"),
            ("25", "TXB", "GND", "L"),
            ("26", "TXB*", "GND", "L"),
            ("24", "TXINHB", "+3V3", "L"),
            ("16", "RXENB", "GND", "L"),
            ("21", "RXB", None, "L"),
            ("20", "RXB*", None, "L"),
            ("40", "BUSA", "M1553_P", "R"),
            ("41", "BUSA", "M1553_P", "R"),
            ("42", "BUSA*", "M1553_N", "R"),
            ("43", "BUSA*", "M1553_N", "R"),
            ("8", "BUSB", None, "R"),
            ("9", "BUSB", None, "R"),
            ("10", "BUSB*", None, "R"),
            ("11", "BUSB*", None, "R"),
            ("38", "VDDA", "+3V3", "R"),
            ("39", "VDDA", "+3V3", "R"),
            ("6", "VDDB", "+3V3", "R"),
            ("7", "VDDB", "+3V3", "R"),
            ("3", "GNDA", "GND", "R"),
            ("4", "GNDA", "GND", "R"),
            ("5", "GNDA", "GND", "R"),
            ("17", "GNDB", "GND", "R"),
            ("18", "GNDB", "GND", "R"),
            ("19", "GNDB", "GND", "R"),
            ("45", "EP", "GND", "R"),
        ] + [(str(n), "NC", None, "R") for n in (1, 12, 13, 14, 15, 22, 23, 27, 28, 32, 33, 34, 35, 44)],
    },
    {
        "ref": "1553-XFM",
        "value": "PM-DB2791S",
        "fp": FP_X1553,
        "mpn": "PM-DB2791S",
        "ds": "PremierMagnetics_DB2791S.pdf Fig 1 schematic (1-3 : 4-8 = 1:2.5) / Fig 2 dims [REF-SENSOR-025]",
        # Holt-recommended isolation transformer (hi-1573.pdf transformer table).
        # Primary 1-3 (CT 2 -> GND) on the transceiver, secondary 4-8 to the bus
        # through the 55 R stub isolation resistors; pads 5/6/7 have no winding.
        "pins": [
            ("1", "PRI_P", "M1553_P", "L"),
            ("2", "PRI_CT", "GND", "L"),
            ("3", "PRI_N", "M1553_N", "L"),
            ("4", "SEC_P", "M1553_SEC_P", "R"),
            ("5", "NC", None, "R"),
            ("6", "NC", None, "R"),
            ("7", "NC", None, "R"),
            ("8", "SEC_N", "M1553_SEC_N", "R"),
        ],
    },
    {
        "ref": "U-3V3",
        "value": "TPS62933DRLR",
        "fp": FP_SOT583,
        "mpn": "TPS62933DRLR",
        "ds": "tps62933.pdf Table 7-1 Pin Functions (SOT-583) [REF-PWR-001]",
        # 5 V -> 3.3 V, 1.2 MHz (RT tied to GND), Vout = 0.8 V x (1 + R1/R2).
        "pins": [
            ("3", "VIN", "+5V", "L"),
            ("2", "EN", "U3V3_EN", "L"),
            ("1", "RT", "GND", "L"),
            ("4", "GND", "GND", "L"),
            ("5", "SW", "SW_3V3", "R"),
            ("6", "BST", "BST_3V3", "R"),
            ("7", "SS/PG", "SS_3V3", "R"),
            ("8", "FB", "FB_3V3", "R"),
        ],
    },
]

# ---------------------------------------------------------------------------
# PocketBeagle 2 Industrial stacking headers — the board's established P1/P2
# map.  Changes 2026-09-19: P1-20 (ex SPI0_CS_1553, unused) -> M1553_TX_EN;
# P1-33/34 (PB2 3.3 V) -> +3V3_PB2 (cape now regulates its own +3V3).
# ---------------------------------------------------------------------------
PB2_P1 = [
    "GND", "GND", "DSHOT3", "DSHOT2", "DSHOT1", "DSHOT0",
    "PRU_1553_RX_N", "PRU_1553_RX_P", "PRU_1553_TX_N", "PRU_1553_TX_P",
    "RS485_DE", "RS485_RX", "RS485_TX", "CAN_STB", "MCAN0_RX", "MCAN0_TX",
    "BARO_INT", "IMU_INT2", "IMU_INT1", "M1553_TX_INH", "SPI0_CS_TPM",
    "SPI0_CS_BARO", "SPI0_MISO", "SPI0_MOSI", "SPI0_CLK", "SPI0_CS_IMU",
    None, None, None, None, "UART_GPS_RX",
    "UART_GPS_TX", "+3V3_PB2", "+3V3_PB2", "+5V", "GND",
]
PB2_P2 = [
    "MDIO1", "MDC1", None, None, None, None, None,
    None, "GPS_RESETN", "GPS_TIMEPULSE", "TPM_RSTN", "TPM_IRQN",
    "PHY2_RSTN", "PHY2_INTRN", "PHY1_RSTN", "PHY1_INTRN", "MDIO0", "MDC0",
    "RMII1_REF_CLK", "RMII1_RX_ER", "RMII1_CRS_DV", "RMII1_RXD1",
    "RMII1_RXD0", "RMII1_TX_EN", "RMII1_TXD1", "RMII1_TXD0",
    "RMII0_REF_CLK", "RMII0_RX_ER", "RMII0_CRS_DV", "RMII0_RXD1",
    "RMII0_RXD0", "RMII0_TX_EN", "RMII0_TXD1", "RMII0_TXD0", "+5V", "GND",
]


def pb2_header(ref: str, value: str, fp: str, nets: List[str]) -> Dict[str, Any]:
    pins = [(str(i), f"P{i}", net, "L" if i <= 18 else "R") for i, net in enumerate(nets, start=1)]
    return {"ref": ref, "value": value, "fp": fp, "mpn": "", "ds": "PocketBeagle 2 P1/P2 expansion rails", "pins": pins}


ICS += [
    pb2_header("PB2-P1", "PB2I-P1-2x18", FP_PB2P1, PB2_P1),
    pb2_header("PB2-P2", "PB2I-P2-2x18", FP_PB2P2, PB2_P2),
]

# ---------------------------------------------------------------------------
# Field connectors, protection, passives.  Tuple: (ref, value, fp, mpn, ds,
# [(pin, fn, net), ...]).  Optional trailing dict for flags (dnp).
# ---------------------------------------------------------------------------
Simple = Tuple[str, str, str, str, str, List[Tuple[str, str, Optional[str]]]]
SIMPLE: List[Any] = [
    # --- power entry -------------------------------------------------------
    ("PWR-IN", "Nano-Fit 4P", FP_NANOFIT, "105313-1204",
     "Pilot.md §14 power entry (Molex Nano-Fit 2.5 mm, 4 ckt)",
     [("1", "+5V_IN", "+5V_IN"), ("2", "+5V_IN", "+5V_IN"), ("3", "GND", "GND"), ("4", "GND", "GND")]),
    ("FB1", "742792512", FP_L0805, "742792512", "Pilot.md §6 pi filter bead 600R@100MHz 2A",
     [("1", "IN", "+5V_IN"), ("2", "OUT", "+5V")]),
    ("C-IN1", "47uF 10V X5R", FP_C1210, "", "Pilot.md §6 C11 input bulk", [("1", "P", "+5V_IN"), ("2", "N", "GND")]),
    ("C-IN2", "10uF 10V X5R", FP_C0805, "", "Pilot.md §6 C12 filtered bulk", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-IN3", "100nF", FP_C0402, "", "Pilot.md §6 C12 HF bypass", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("R-PGND", "0R", FP_R0805, "", "Pilot.md §7 single-point GND<->PGND link",
     [("1", "A", "GND"), ("2", "B", "PGND")]),
    # --- +3V3 buck (TPS62933) ----------------------------------------------
    ("R-EN3", "100k", FP_R0201, "", "TPS62933 EN pull-up to VIN", [("1", "A", "+5V"), ("2", "B", "U3V3_EN")]),
    ("C-3V3-IN", "10uF 10V X5R", FP_C0805, "", "TPS62933 CIN at VIN/GND", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-3V3-HF", "100nF", FP_C0402, "", "TPS62933 CIN HF", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-BST", "100nF", FP_C0402, "", "TPS62933 BST-SW bootstrap", [("1", "P", "BST_3V3"), ("2", "N", "SW_3V3")]),
    ("C-SS", "10nF", FP_C0201, "", "TPS62933 soft-start (>=6.8 nF)", [("1", "P", "SS_3V3"), ("2", "N", "GND")]),
    ("L-3V3", "3.3uH 2.25A", FP_L3015, "74438335033", "TPS62933 inductor, WE-MAPI 3015 (74438335033.pdf) [REF-PWR-003]",
     [("1", "A", "SW_3V3"), ("2", "B", "+3V3")]),
    ("R-FB3H", "100k 1%", FP_R0201, "", "TPS62933 FB divider top", [("1", "A", "+3V3"), ("2", "B", "FB_3V3")]),
    ("R-FB3L", "32.4k 1%", FP_R0201, "", "TPS62933 FB divider bottom (3.27 V)", [("1", "A", "FB_3V3"), ("2", "B", "GND")]),
    ("C-3V3-O1", "22uF 6.3V X5R", FP_C0805, "", "TPS62933 COUT", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-3V3-O2", "22uF 6.3V X5R", FP_C0805, "", "TPS62933 COUT", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    # --- CAN FD field port -------------------------------------------------
    ("C-CAN1", "10nF", FP_C0201, "", "ISOW1044 VDD HF bypass (<1 mm) §13.1", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-CAN2", "10uF 10V X5R", FP_C0805, "", "ISOW1044 VDD bulk §13.1", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-CAN3", "100nF", FP_C0402, "", "ISOW1044 VIO bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-CAN4", "10nF", FP_C0201, "", "ISOW1044 VISOOUT HF bypass (<1 mm)", [("1", "P", "VCC2_CAN"), ("2", "N", "GND2_CAN")]),
    ("C-CAN5", "10uF 10V X5R", FP_C0805, "", "ISOW1044 VISOOUT bulk", [("1", "P", "VCC2_CAN"), ("2", "N", "GND2_CAN")]),
    ("C-CAN6", "100nF", FP_C0402, "", "ISOW1044 VISOIN bypass", [("1", "P", "VCC2_CAN"), ("2", "N", "GND2_CAN")]),
    ("CMC-CAN", "SRF2012-100Y", FP_SRF2012, "SRF2012-121YA", "SRF2012A.pdf windings 1-2 / 4-3 [REF-SENSOR-026]",
     [("1", "W1_IN", "CAN_H"), ("2", "W1_OUT", "CAN_H_F"), ("4", "W2_IN", "CAN_L"), ("3", "W2_OUT", "CAN_L_F")]),
    ("TVS-CAN", "PRTR5V0U2X", FP_SOT363, "PRTR5V0U2X,115", "Pilot.md §5 dual TVS at CAN field connector",
     [("1", "IO1", "CAN_H_F"), ("2", "GND", "GND2_CAN"), ("3", "IO2", "CAN_L_F"), ("4", "NC", None),
      ("5", "VCC", "VCC2_CAN"), ("6", "NC", None)]),
    ("R-CANT", "120R", FP_R0603, "", "CAN bus termination — populate ONLY at a bus end node (DNP default)",
     [("1", "A", "CAN_H_F"), ("2", "B", "CAN_L_F")], {"dnp": True}),
    ("CAN-FD", "SM04B-GHS-TB", FP_GH4, "SM04B-GHS-TB(LF)(SN)", "Pilot.md §14 J_CAN",
     [("1", "GND", "GND2_CAN"), ("2", "CAN_H", "CAN_H_F"), ("3", "CAN_L", "CAN_L_F"), ("4", "VCC", "VCC2_CAN"),
      ("MP", "SHIELD", "PGND")]),
    ("X2Y-CAN", "4.7nF X2Y", FP_X2Y0805, "CX0805MRX7R0BB472", "Pilot.md §2 GND1<->GND2 RF bridge (Yageo X2Y 0805)",
     [("1", "A", "GND"), ("2", "B", "GND"), ("3", "G1", "GND2_CAN"), ("4", "G2", "GND2_CAN")]),
    # --- RS-485 field port -------------------------------------------------
    ("C-485-1", "10nF", FP_C0201, "", "ISOW1412 VDD HF bypass", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-485-2", "10uF 10V X5R", FP_C0805, "", "ISOW1412 VDD bulk", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-485-3", "100nF", FP_C0402, "", "ISOW1412 VIO bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-485-4", "10nF", FP_C0201, "", "ISOW1412 VISOOUT HF bypass", [("1", "P", "VCC2_RS485"), ("2", "N", "GND2_RS485")]),
    ("C-485-5", "10uF 10V X5R", FP_C0805, "", "ISOW1412 VISOOUT bulk", [("1", "P", "VCC2_RS485"), ("2", "N", "GND2_RS485")]),
    ("C-485-6", "100nF", FP_C0402, "", "ISOW1412 VISOIN bypass", [("1", "P", "VCC2_RS485"), ("2", "N", "GND2_RS485")]),
    ("CMC-RS485", "SRF2012-100Y", FP_SRF2012, "SRF2012-121YA", "SRF2012A.pdf windings 1-2 / 4-3 [REF-SENSOR-026]",
     [("1", "W1_IN", "RS485_A"), ("2", "W1_OUT", "RS485_A_F"), ("4", "W2_IN", "RS485_B"), ("3", "W2_OUT", "RS485_B_F")]),
    ("TVS-RS485", "PRTR5V0U2X", FP_SOT363, "PRTR5V0U2X,115", "Pilot.md §5 dual TVS at RS-485 field connector",
     [("1", "IO1", "RS485_A_F"), ("2", "GND", "GND2_RS485"), ("3", "IO2", "RS485_B_F"), ("4", "NC", None),
      ("5", "VCC", "VCC2_RS485"), ("6", "NC", None)]),
    ("R-485T", "120R", FP_R0603, "", "RS-485 termination — populate ONLY at a bus end node (DNP default)",
     [("1", "A", "RS485_A_F"), ("2", "B", "RS485_B_F")], {"dnp": True}),
    ("RS-485", "SM04B-GHS-TB", FP_GH4, "SM04B-GHS-TB(LF)(SN)", "Pilot.md §14 J_485",
     [("1", "GND", "GND2_RS485"), ("2", "A", "RS485_A_F"), ("3", "B", "RS485_B_F"), ("4", "VCC", "VCC2_RS485"),
      ("MP", "SHIELD", "PGND")]),
    ("X2Y-RS485", "4.7nF X2Y", FP_X2Y0805, "CX0805MRX7R0BB472", "Pilot.md §3 GND1<->GND2 RF bridge (Yageo X2Y 0805)",
     [("1", "A", "GND"), ("2", "B", "GND"), ("3", "G1", "GND2_RS485"), ("4", "G2", "GND2_RS485")]),
    # --- Ethernet line-side connectors + Bob-Smith terminations ------------
    ("ETH1", "SM04B-GHS-TB", FP_GH4, "SM04B-GHS-TB(LF)(SN)", "ETH1 line pair to T-ETH secondary",
     [("1", "TXP", "ETH_LINE_TXP"), ("2", "TXN", "ETH_LINE_TXN"), ("3", "RXP", "ETH_LINE_RXP"), ("4", "RXN", "ETH_LINE_RXN"),
      ("MP", "SHIELD", "PGND")]),
    ("ETH2", "SM04B-GHS-TB", FP_GH4, "SM04B-GHS-TB(LF)(SN)", "ETH2 line pair to T-ETH2 secondary",
     [("1", "TXP", "ETH2_LINE_TXP"), ("2", "TXN", "ETH2_LINE_TXN"), ("3", "RXP", "ETH2_LINE_RXP"), ("4", "RXN", "ETH2_LINE_RXN"),
      ("MP", "SHIELD", "PGND")]),
    # TPI network per dp83825i.pdf Fig 8-3: 75 R from each line-side centre tap to a
    # common node, 10 nF (2 kV) to chassis.
    ("R-BS1T", "75R", FP_R0402, "", "ETH1 line TX centre tap Bob-Smith (Fig 8-3 R135)", [("1", "A", "ETH_LINE_CTX"), ("2", "B", "ETH_BS")]),
    ("R-BS1R", "75R", FP_R0402, "", "ETH1 line RX centre tap Bob-Smith (Fig 8-3 R143)", [("1", "A", "ETH_LINE_CRX"), ("2", "B", "ETH_BS")]),
    ("C-BS1", "10nF 2kV", FP_C1808, "", "ETH1 Bob-Smith HV cap to chassis (Fig 8-3 C38)", [("1", "P", "ETH_BS"), ("2", "N", "PGND")]),
    ("R-BS2T", "75R", FP_R0402, "", "ETH2 line TX centre tap Bob-Smith", [("1", "A", "ETH2_LINE_CTX"), ("2", "B", "ETH2_BS")]),
    ("R-BS2R", "75R", FP_R0402, "", "ETH2 line RX centre tap Bob-Smith", [("1", "A", "ETH2_LINE_CRX"), ("2", "B", "ETH2_BS")]),
    ("C-BS2", "10nF 2kV", FP_C1808, "", "ETH2 Bob-Smith HV cap to chassis", [("1", "P", "ETH2_BS"), ("2", "N", "PGND")]),
    # one shared 25 MHz reference for both PHYs (RMII Leader mode, XI input, XO open)
    ("X-25M", "25MHz 3.3V", FP_OSC2520, "ECS-2520MV-250-BN-TR", "PHY 25 MHz reference, +/-50 ppm (dp83825i.pdf §8.2.1.1.1; ECS-2520MV.pdf) [REF-PWR-004]",
     [("1", "TRI", None), ("2", "GND", "GND"), ("3", "OUT", "PHY_XI_25M"), ("4", "VDD", "+3V3")]),
    ("C-25M", "100nF", FP_C0402, "", "oscillator VDD bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    # --- MIL-STD-1553B field port ------------------------------------------
    ("R-1553P", "55R 2%", FP_R0603, "", "MIL-STD-1553B §4.5.1.5.2 direct-coupled stub isolation resistor (hi-1573.pdf Fig 2)",
     [("1", "A", "M1553_SEC_P"), ("2", "B", "BUS_1553_P")]),
    ("R-1553N", "55R 2%", FP_R0603, "", "MIL-STD-1553B §4.5.1.5.2 direct-coupled stub isolation resistor",
     [("1", "A", "M1553_SEC_N"), ("2", "B", "BUS_1553_N")]),
    ("TVS-1553P", "SMAJ33CA", FP_SMA, "SMAJ33CA", "Pilot.md §5 bidirectional TVS, BUS_P to PGND",
     [("1", "A", "BUS_1553_P"), ("2", "K", "PGND")]),
    ("TVS-1553N", "SMAJ33CA", FP_SMA, "SMAJ33CA", "Pilot.md §5 bidirectional TVS, BUS_N to PGND",
     [("1", "A", "BUS_1553_N"), ("2", "K", "PGND")]),
    ("MIL-1553", "SM04B-GHS-TB", FP_GH4, "SM04B-GHS-TB(LF)(SN)", "Pilot.md §14 J_1553",
     [("1", "BUS_P", "BUS_1553_P"), ("2", "BUS_N", "BUS_1553_N"), ("3", "GND", "GND"), ("4", "SHIELD", "PGND"),
      ("MP", "SHIELD", "PGND")]),
    ("C-1553A", "100nF", FP_C0402, "", "HI-1573 VDDA bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-1553B", "100nF", FP_C0402, "", "HI-1573 VDDB bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-1553C", "10uF 6.3V X5R", FP_C0805, "", "HI-1573 transmitter bulk", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    # --- PWM / DSHOT servo-ESC block -------------------------------------------
    # WBS U1 (plan 2026-09-15-001 B1), 2026-09-19: on Serenity the ESCs and tilt
    # actuators live on the isolated CAN-FD / RS-485 trunk, so the dedicated
    # J_ESC (5-pin DSHOT), J_SERVO (1x8), ESC-TLM and the six GH3 GPIO ports are
    # RETIRED.  Per the owner (2026-09-19) the board must stay usable on other
    # platforms with PWM / DSHOT / BDSHOT ESCs, so one standard 3x6 0.1 in
    # servo/ESC header block wired DIRECTLY to PRU-capable SoC balls (DSHOT0-3,
    # SERVO0-1) replaces them; the PCA9555 expander (cannot drive DSHOT) is gone.
    #
    # MIL-STD-1553B section REMOVED in Rev T (2026-09-19): the DS26LV31/32 are
    # RS-422 line drivers (~2 V differential) and cannot meet the MIL-STD-1553B
    # §4.5.2 bus voltage levels [REF-MIL-001], and the chain (2 x SOIC-16 +
    # SM1553 + TVS + connector, ~440 mm^2) does not fit the 55 x 35 mm cape.
    # The PRU_1553_* / M1553_TX_EN balls (P1-7..10, P1-20) stay reserved as
    # no-connects; a compliant transceiver is a WBS item.
    # --- sensors -------------------------------------------------------------
    ("C-IMU1", "100nF", FP_C0402, "", "ICM-42688-P VDD bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-IMU2", "10nF", FP_C0201, "", "ICM-42688-P VDDIO bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-BARO1", "100nF", FP_C0402, "", "BMP388 VDD bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-BARO2", "100nF", FP_C0402, "", "BMP388 VDDIO bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-GPS1", "10uF 6.3V X5R", FP_C0805, "", "MAX-M10S VCC bulk", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-GPS2", "100nF", FP_C0402, "", "MAX-M10S VCC/V_IO bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("R-ANT", "10R", FP_R0201, "", "MAX-M10S antenna supply current limiter R8 (integration manual Table 53)",
     [("1", "A", "GPS_VCC_RF"), ("2", "B", "GPS_ANT_BIAS")]),
    ("C-ANT", "10nF X7R", FP_C0402, "", "MAX-M10S RF bias-T filter C14 (Table 52)", [("1", "P", "GPS_ANT_BIAS"), ("2", "N", "GND")]),
    ("L-ANT", "27nH", "Inductor_SMD:L_0402_1005Metric", "LQG15HN27NJ02D", "MAX-M10S RF bias-T inductor L3 (Table 54, Murata LQG15H)",
     [("1", "A", "GPS_ANT_BIAS"), ("2", "B", "GPS_RF")]),
    ("J-ANT", "U.FL-R-SMT-1", "Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical", "U.FL-R-SMT-1(10)",
     "GNSS active-antenna feed to the dorsal-cup SMA bulkhead (AVIONICS_PB2_REDESIGN.md GPS-ANT)",
     [("1", "RF", "GPS_RF"), ("2", "SHIELD", "GND")]),
    # --- TPM -----------------------------------------------------------------
    ("C-TPM1", "1uF", FP_C0402, "", "SLB9672 §3.1.3 typical schematic bulk", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-TPM2", "100nF", FP_C0402, "", "SLB9672 VDD bypass (pin 1)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-TPM3", "100nF", FP_C0402, "", "SLB9672 VDD bypass (pin 14)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-TPM4", "100nF", FP_C0402, "", "SLB9672 VDD bypass (pin 22)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("R-TPMCS", "10k", FP_R0201, "", "SLB9672 CS# pull-up (§3.1.3)", [("1", "A", "+3V3"), ("2", "B", "SPI0_CS_TPM")]),
    ("R-TPM10", "10k", FP_R0201, "", "SLB9672 pin 10 NCI/VDD pull-up (Table 13, preferred)", [("1", "A", "+3V3"), ("2", "B", "TPM_P10_PU")]),
]
PWM_CH = ["DSHOT0", "DSHOT1", "DSHOT2", "DSHOT3"]
# Samtec TSM-108-01-L-DV 2 x 8 SMT 0.1 in header (samtec_tsm-dv-footprint.pdf).
# Column-major Samtec numbering: column k has pin 2k-1 (row A) and 2k (row B).
# Channel c occupies four consecutive columns of ONE row: SIG, +5V, GND, PGND
# (chassis shield drain) — a 3-pin servo/ESC lead spans the first three, its
# shield lands on the fourth.  ch0/ch1 on row A (cols 1-4 / 5-8), ch2/ch3 on row B.
_pwm_pins: List[Tuple[str, str, Optional[str]]] = []
for _i, _net in enumerate(PWM_CH):
    _row = 0 if _i < 2 else 1                      # 0 = row A (odd pins), 1 = row B (even pins)
    _col0 = 1 + 4 * (_i % 2)
    for _j, (_fn, _n) in enumerate(((f"SIG{_i}", _net), (f"+5V_{_i}", "+5V"), (f"GND{_i}", "GND"), (f"SHLD{_i}", "PGND"))):
        _k = _col0 + _j
        _pwm_pins.append((str(2 * _k - 1 + _row), _fn, _n))
SIMPLE += [
    ("J-PWM", "TSM-108-01-L-DV", FP_TSM2X8, "TSM-108-01-L-DV",
     "Servo / ESC signal block, 2x8 SMT 0.1 in (Samtec TSM -DV); 4 ch x (SIG, +5V, GND, PGND shield) along a row; "
     "SIG = SoC PRU balls DSHOT0-3 (3.3 V logic; PWM / DSHOT / BDSHOT capable) [REF-CONN-001]",
     _pwm_pins),
]
# Mounting holes on chassis ground (Pilot.md §7).
SIMPLE += [
    (f"H{i}", "M2.5 PGND", FP_HOLE, "", "Pilot.md §7 chassis bond via mounting hardware", [("1", "PGND", "PGND")])
    for i in range(1, 5)
]


def phy_support(tag: str, ref: str, rmii: str, eth: str) -> List[Any]:
    """DP83825I per-PHY passives (dp83825i.pdf Table 4-1, Table 6-8/6-9, Fig 8-3, Fig 8-4)."""
    p = f"P{tag}"
    return [
        (f"R-{p}-RBIAS", "6.49k 1%", FP_R0201, "", "DP83825I RBIAS to GND (pin 14)", [("1", "A", f"{ref}_RBIAS"), ("2", "B", "GND")]),
        (f"R-{p}-AD0", "2.49k", FP_R0201, "", "PhyAdd[0] strap mode 1 -> PHY address 1 (Table 6-8/6-9)", [("1", "A", "+3V3"), ("2", "B", f"{rmii}_RXD0")]),
        (f"C-{p}-A1", "10nF", FP_C0201, "", "VDDA3V3 HF bypass (Fig 8-4)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
        (f"C-{p}-A2", "100nF", FP_C0402, "", "VDDA3V3 bypass (Fig 8-4)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
        (f"C-{p}-A3", "1uF", FP_C0402, "", "VDDA3V3 bulk (Fig 8-4)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
        (f"C-{p}-IO1", "10nF", FP_C0201, "", "VDDIO HF bypass (Fig 8-4)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
        (f"C-{p}-IO2", "100nF", FP_C0402, "", "VDDIO bypass (Fig 8-4)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
        (f"C-{p}-IO3", "1uF", FP_C0402, "", "VDDIO bulk (Fig 8-4)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
        (f"C-{p}-CTD1", "100nF", FP_C0402, "", "device-side TX centre tap to GND (Fig 8-3 C41)", [("1", "P", f"{eth}_CTD"), ("2", "N", "GND")]),
        (f"C-{p}-CTD2", "1uF", FP_C0402, "", "device-side TX centre tap to GND (Fig 8-3 C44)", [("1", "P", f"{eth}_CTD"), ("2", "N", "GND")]),
        (f"C-{p}-CRD1", "100nF", FP_C0402, "", "device-side RX centre tap to GND (Fig 8-3 C75)", [("1", "P", f"{eth}_CRD"), ("2", "N", "GND")]),
        (f"C-{p}-CRD2", "1uF", FP_C0402, "", "device-side RX centre tap to GND (Fig 8-3 C74)", [("1", "P", f"{eth}_CRD"), ("2", "N", "GND")]),
    ]


SIMPLE += phy_support("1", "ETH1-PHY", "RMII0", "ETH")
SIMPLE += phy_support("2", "ETH2-PHY", "RMII1", "ETH2")

for _entry in SIMPLE:
    _ref, _val, _fp, _mpn, _ds, _pins = _entry[:6]
    _flags = _entry[6] if len(_entry) > 6 else {}
    _n = len(_pins)
    _half = (_n + 1) // 2
    ICS.append({
        "ref": _ref, "value": _val, "fp": _fp, "mpn": _mpn, "ds": _ds,
        "dnp": bool(_flags.get("dnp")),
        "pins": [(pn, fn, net, "L" if i < _half else "R") for i, (pn, fn, net) in enumerate(_pins)],
    })


def lib_symbol(ic: Dict[str, Any]) -> Tuple[str, List[Any], List[Any], float, float]:
    ref, pins = ic["ref"], ic["pins"]
    left = [p for p in pins if p[3] == "L"]
    right = [p for p in pins if p[3] == "R"]
    rows = max(len(left), len(right), 1)
    half_h = (rows * PIN_PITCH) / 2 + PIN_PITCH
    half_w = 16.51
    libid = f"S_{sanitize(ref)}"
    s = [
        f'    (symbol "Pilot:{libid}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)',
        f'      (property "Reference" "U" (at 0 {half_h + 1.27:.2f} 0) (effects (font (size {SIZE} {SIZE}))))',
        f'      (property "Value" "{esc(ic["value"])}" (at 0 {-half_h - 1.27:.2f} 0) (effects (font (size {SIZE} {SIZE}))))',
        f'      (property "Footprint" "{esc(ic["fp"])}" (at 0 0 0) (effects (font (size {SIZE} {SIZE})) (hide yes)))',
        f'      (property "Datasheet" "{esc(ic["ds"])}" (at 0 0 0) (effects (font (size {SIZE} {SIZE})) (hide yes)))',
        f'      (symbol "{libid}_0_1"',
        f"        (rectangle (start {-half_w:.2f} {half_h:.2f}) (end {half_w:.2f} {-half_h:.2f}) "
        f"(stroke (width 0.2540) (type default)) (fill (type background)))",
        "      )",
        f'      (symbol "{libid}_1_1"',
    ]
    for i, (pn, fn, net, _) in enumerate(left):
        s.append(pin_def(-half_w - PIN_PITCH, half_h - PIN_PITCH * (i + 1), 0, pn, fn))
    for i, (pn, fn, net, _) in enumerate(right):
        s.append(pin_def(half_w + PIN_PITCH, half_h - PIN_PITCH * (i + 1), 180, pn, fn))
    s += ["      )", "    )"]
    return "\n".join(s), left, right, half_w, half_h


def pin_def(x: float, y: float, ang: int, pn: str, fn: Optional[str]) -> str:
    etype = "power_in" if isinstance(fn, str) and fn in ("GND", "EP") else "passive"
    return (
        f"        (pin {etype} line (at {x:.2f} {y:.2f} {ang}) (length {PIN_PITCH}) "
        f'(name "{esc(fn) if fn is not None else ""}" (effects (font (size {SIZE} {SIZE})))) '
        f'(number "{esc(pn)}" (effects (font (size {SIZE} {SIZE})))))'
    )


def wire(x1: float, y1: float, x2: float, y2: float) -> str:
    return (f"  (wire (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f})) "
            f'(stroke (width 0) (type default)) (uuid "{uid()}"))')


def label(net: str, x: float, y: float, ang: int) -> str:
    just = "left" if ang == 0 else "right"
    return (f'  (global_label "{esc(net)}" (shape passive) (at {x:.2f} {y:.2f} {ang}) '
            f"(effects (font (size {SIZE} {SIZE})) (justify {just})) "
            f'(uuid "{uid()}"))')


def no_connect(x: float, y: float) -> str:
    return f'  (no_connect (at {x:.2f} {y:.2f}) (uuid "{uid()}"))'


def emit_instance(ic, X, Y, left, right, half_w, half_h, sheet_uuid) -> List[str]:
    ref, value = ic["ref"], ic["value"]
    libid = f"S_{sanitize(ref)}"
    dnp = "yes" if ic.get("dnp") else "no"
    out = [
        f'  (symbol (lib_id "Pilot:{libid}") (at {X:.2f} {Y:.2f} 0) (unit 1)',
        f'    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp {dnp}) (uuid "{uid()}")',
        f'    (property "Reference" "{esc(ref)}" (at {X:.2f} {Y - half_h - 1.27:.2f} 0) (effects (font (size {SIZE} {SIZE}))))',
        f'    (property "Value" "{esc(value)}" (at {X:.2f} {Y + half_h + 1.27:.2f} 0) (effects (font (size {SIZE} {SIZE}))))',
        f'    (property "Footprint" "{esc(ic["fp"])}" (at {X:.2f} {Y:.2f} 0) (effects (font (size {SIZE} {SIZE})) (hide yes)))',
        f'    (property "Datasheet" "{esc(ic["ds"])}" (at {X:.2f} {Y:.2f} 0) (effects (font (size {SIZE} {SIZE})) (hide yes)))',
        f'    (property "MPN" "{esc(ic.get("mpn", ""))}" (at {X:.2f} {Y:.2f} 0) (effects (font (size {SIZE} {SIZE})) (hide yes)))',
    ]
    for pn, *_ in left + right:
        out.append(f'    (pin "{esc(pn)}" (uuid "{uid()}"))')
    out.append(f'    (instances (project "Pilot" (path "/{sheet_uuid}" (reference "{esc(ref)}") (unit 1))))')
    out.append("  )")
    wl = []
    for i, (pn, fn, net, _) in enumerate(left):
        cx, cy = X - half_w - PIN_PITCH, Y - (half_h - PIN_PITCH * (i + 1))
        if net is None:
            wl.append(no_connect(cx, cy))
            continue
        wl.append(wire(cx, cy, cx - STUB, cy))
        wl.append(label(net, cx - STUB, cy, 180))
    for i, (pn, fn, net, _) in enumerate(right):
        cx, cy = X + half_w + PIN_PITCH, Y - (half_h - PIN_PITCH * (i + 1))
        if net is None:
            wl.append(no_connect(cx, cy))
            continue
        wl.append(wire(cx, cy, cx + STUB, cy))
        wl.append(label(net, cx + STUB, cy, 0))
    return out + wl


# Rails with no power_out pin on this sheet.  +5V_IN enters on PWR-IN; GND2_*
# and VCC2_* are generated inside the isolators; +3V3 comes from U-3V3 whose
# pins are passive in these box symbols; PGND is chassis.
PWR_FLAG_RAILS = ["GND", "+3V3", "+5V", "+5V_IN", "GND2_CAN", "GND2_RS485",
                  "VCC2_CAN", "VCC2_RS485", "PGND", "+3V3_PB2"]

PWR_FLAG_LIB = """    (symbol "power:PWR_FLAG" (power) (pin_numbers (hide yes)) (pin_names (offset 0) (hide yes)) \
(exclude_from_sim no) (in_bom yes) (on_board yes)
      (property "Reference" "#FLG" (at 0 1.905 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (property "Value" "PWR_FLAG" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (property "Description" "Special symbol for telling ERC where power comes from" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (property "ki_keywords" "flag power" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (symbol "PWR_FLAG_0_0"
        (pin power_out line (at 0 0 90) (length 0) (name "~" \
(effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
      )
      (symbol "PWR_FLAG_0_1"
        (polyline (pts (xy 0 0) (xy 0 1.27) (xy -1.016 1.905) (xy 0 2.54) \
(xy 1.016 1.905) (xy 0 1.27)) (stroke (width 0) (type default)) (fill (type none)))
      )
      (embedded_fonts no)
    )"""


def emit_pwr_flags(x0: float, y0: float, sheet_uuid: str) -> List[str]:
    out = []
    for i, rail in enumerate(PWR_FLAG_RAILS):
        x = x0 + i * 20.32
        out.append(
            f'  (symbol (lib_id "power:PWR_FLAG") (at {x:.2f} {y0:.2f} 0) (unit 1)\n'
            f"    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)\n"
            f'    (uuid "{uid()}")\n'
            f'    (property "Reference" "#FLG{i + 1}" (at {x:.2f} {y0 - 2.54:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
            f'    (property "Value" "PWR_FLAG" (at {x:.2f} {y0 - 5.08:.2f} 0) (effects (font (size 1.27 1.27))))\n'
            f'    (instances (project "Pilot" (path "/{sheet_uuid}" (reference "#FLG{i + 1}") (unit 1)))))'
        )
        out.append(wire(x, y0, x, y0 + STUB))
        out.append(label(rail, x, y0 + STUB, 270))
    return out


TITLE_BLOCK = """  (title_block
    (title "Pilot — EMI-Hardened Flight Control & Sensor Cape")
    (date "2026-09-19")
    (rev "T")
    (company "Griffing Technology LLC")
    (comment 1 "FC Node — PocketBeagle 2 Industrial cape, 55 x 35 mm, 4-layer")
    (comment 2 "Generated by avionics/kicad/Pilot/scripts/gen_pilot_sch.py — do not hand-edit; edit the generator")
    (comment 3 "Author: Claude Opus 5 (2026-07-28, 2026-09-19) from Claude Opus 4.8 (2026-07-14); owner sgriffing")
    (comment 4 "CC BY 4.0 — pinouts transcribed from OEM datasheets in avionics/datasheets/")
  )"""


def main() -> None:
    sheet_uuid = uid()
    parts = [
        "(kicad_sch (version 20240101) (generator eeschema)",
        f'  (uuid "{uid()}")',
        '  (paper "A1")',
        TITLE_BLOCK,
        "  (lib_symbols",
        PWR_FLAG_LIB,
    ]
    placed = []
    X0, Y0, DX = 76.2, 76.2, 127.0
    COL_MAX_Y = 560.0
    x, y = X0, Y0
    built = []
    seen = set()
    for ic in ICS:
        if ic["ref"] in seen:
            raise SystemExit(f"duplicate reference {ic['ref']}")
        seen.add(ic["ref"])
        libtext, left, right, hw, hh = lib_symbol(ic)
        parts.append(libtext)
        built.append((ic, left, right, hw, hh))
    for ic, left, right, hw, hh in built:
        if y + 2 * hh > COL_MAX_Y and y > Y0:
            x += DX
            y = Y0
        placed.append((ic, x, y + hh, left, right, hw, hh))
        y += 2 * hh + 15.24
    parts.append("  )")
    for ic, X, Y, left, right, hw, hh in placed:
        parts += emit_instance(ic, X, Y, left, right, hw, hh, sheet_uuid)
    parts += emit_pwr_flags(X0, Y0 - 45.72, sheet_uuid)
    parts.append('  (sheet_instances (path "/" (page "1")))')
    parts.append(")")
    OUT.write_text("\n".join(parts) + "\n")
    # Project symbol library so the sheet's lib_ids resolve (clears ERC
    # lib_symbol_issues).  Same symbol text minus the library prefix.
    lib = ["(kicad_symbol_lib (version 20241209) (generator \"gen_pilot_sch.py\") (generator_version \"9.0\")"]
    for ic, left, right, hw, hh in built:
        lib.append(lib_symbol(ic)[0].replace('(symbol "Pilot:', '(symbol "', 1))
    lib.append(")")
    SYMLIB.write_text("\n".join(lib) + "\n")
    npins = sum(len(ic["pins"]) for ic in ICS)
    print(f"Wrote {OUT}")
    print(f"  parts: {len(ICS)}   pins: {npins}   columns: {int((x - X0) / DX) + 1}")


if __name__ == "__main__":
    main()
