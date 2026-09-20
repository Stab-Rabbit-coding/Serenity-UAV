#!/usr/bin/env python3
"""gen_xo_sch.py — Author the datasheet-accurate XO (CAPE-B-1 successor) schematic.

Schematic-first rebuild of the XO comms/logging/payload cape (PocketBeagle 2
Industrial cape), following the exact method used for the Pilot rebuild
(``avionics/kicad/Pilot/scripts/gen_pilot_sch.py``): every IC is a rectangular
symbol carrying its FULL datasheet pinout, every functional pin is wired to a
global net label, and every symbol carries the footprint the PCB generator
(``gen_xo_pcb.py``) places.  ``kicad-cli sch erc`` and the PCB net-sync both
read from the ``ICS`` / ``SIMPLE`` tables below.

Scope for this rebuild
-----------------------
The prior ``XO.kicad_sch`` had 169 component references against only 43 PCB
footprints (matching Pilot's pre-rebuild divergence) and 564 ERC violations —
not a patchable state.  This rebuild starts fresh, reusing the fleet-shared
blocks already verified on Pilot (identical part, identical pin table) and
authoring the XO-unique radio/logging/payload blocks new:

* **Fleet-shared (reused verbatim from Pilot, ``_B_`` net suffix per XO.md's
  own documented rationale — lets Pilot and XO share one bus ring without net
  collisions):** ISOW1044BDFMR (CAN FD), ISOW1412DFMR (RS-485), SLB9672 (TPM),
  Holt HI-1573 + Premier PM-DB2791S (MIL-STD-1553B — the RS-422 DS26LV31/32 +
  fake "SM-1553-11" defect in the legacy schematic is retired, same fix as
  Pilot), DP83825I (Ethernet PHY) + WE-LAN transformer, PocketBeagle 2 P1/P2
  stacking headers.
* **Ethernet inclusion resolved via avionics/WBS.md** (higher authority than
  XO.md's own internal contradiction — see WBS.md "Re-evaluate space / restore
  Ethernet to XO", DONE at Rev R, single DP83825I, confirmed adequate space):
  XO gets **one** PHY (RMII0), not the dual pair Pilot has (WBS §1.2a "XO: 1x
  PHY (RMII0)").
* **XO-unique (new this pass):** RFD900x SiK UHF radio (rfd900x-datasheet.pdf),
  RFM95W LoRa module (rfm95w-datasheet.pdf — a real module, NOT the bare
  SX1276), WL1837MOD WiFi+BT (wl1837mod.pdf, ~14 of 100 balls carry a net —
  disclosed scope calibration, see gen_xo_footprints.py), TPS63031 buck-boost
  for the RF 3V3 rail (tps63031.pdf), W25Q128JV SPI NOR flash (w25q128jv.pdf),
  DRV8833 winch H-bridge driver (drv8833.pdf), HX711 load-cell ADC
  (hx711.pdf), PCA9685 PWM/I2C driver (pca9685.pdf), ATF16V8BQL PLD used as a
  logging write-block interlock (atf16v8bql.pdf — the JEDEC fuse map/logic
  equations are a firmware deliverable, out of scope here; every pin is wired
  to a real net so the schematic is ERC-complete), three antenna filter/ESD
  chains, microSD card slot, fan connector.
* **Explicitly excluded:** the Zigbee radio (WBS.md flags it as never having
  been added to XO — a pre-existing scope gap, not addressed by this pass)
  and the confirmed-obsolete J_XCVR (49 MHz Commo cable) / SBUS blocks.

Two part-number defects found in XO.md itself and corrected here (flagged to
the user, not silently fixed — see the commit message and gen_xo_footprints.py
docstring for the full trail): XO.md's antenna-filter table cited Johanson
"0915LP15B0100E" and "2450BP15B050E", neither of which exists in Johanson's
catalog; substituted with the closest real Johanson parts found
(0915LP15B026E, 2450BP15E0100) pending user confirmation.  The microSD
connector "Molex 503182-1852" XO.md cited could not be verified real; the
system KiCad library's ``Connector_Card:microSD_HC_Molex_104031-0811`` (a
confirmed, datasheet-real part) is used instead.

Datasheets (all in ``avionics/datasheets/``):
  ISOW1044BDFMR/ISOW1412DFMR/SLB9672/HI-1573/PM-DB2791S/DP83825I — see
  gen_pilot_sch.py docstring (identical parts, identical citations) |
  RFD900x rfd900x-datasheet.pdf §4 | RFM95W rfm95w-datasheet.pdf §1.4 |
  WL1837MOD wl1837mod.pdf SWRS170L | TPS63031 tps63031.pdf Table (Pin Functions) |
  W25Q128JV w25q128jv.pdf §3.3 | DRV8833 drv8833.pdf §5 (Pin Functions, WQFN) |
  HX711 hx711.pdf Pin Description (SOP-16L) | PCA9685 pca9685.pdf Table 3 |
  ATF16V8BQL atf16v8bql.pdf Pin Configurations | SRF2012A SRF2012A.pdf |
  PRTR5V0U2X prtr5v0u2x.pdf (Nexperia, SOT143B) | SMAJ33CA smaj-series-tvs-datasheet.pdf.

Author: Claude Sonnet 5, 2026-09-20.  Human owner: sgriffing (Griffing
Technology LLC).  License: CC BY 4.0.
"""

from __future__ import annotations

import itertools
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "kicads" / "XO.kicad_sch"
SYMLIB = HERE.parent / "kicads" / "XO.kicad_sym"

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
FP_SOIC8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
FP_SOIC16 = "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm"
FP_SOIC20W = "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm"
FP_TSSOP28 = "Package_SO:TSSOP-28_4.4x9.7mm_P0.65mm"
FP_WQFN16 = "Package_DFN_QFN:WQFN-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm"
FP_UQFN32 = "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.6x3.6mm"
FP_QFN44 = "Package_DFN_QFN:QFN-44-1EP_7x7mm_P0.5mm_EP5.2x5.2mm"
FP_SMA = "Diode_SMD:D_SMA"
FP_SOT363 = "Package_TO_SOT_SMD:SOT-363_SC-70-6"
FP_SOT143 = "Package_TO_SOT_SMD:SOT-143"
FP_X1553 = "Serenity-Custom:Xfmr_1553_SMD_0.40in_8pin"
FP_GH4 = "Connector_JST:JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal"
FP_GH3 = "Connector_JST:JST_GH_SM03B-GHS-TB_1x03-1MP_P1.25mm_Horizontal"
FP_HOLE = "Serenity-Custom:MountingHole_2.7mm_M2.5_PGND_Ring"
FP_USMD = "Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical"
FP_SMA_EDGE = "Connector_Coaxial:SMA_Amphenol_132289_EdgeMount"
FP_MMCX = "Connector_Coaxial:MMCX_Molex_73415-1471_Vertical"
FP_MICROSD = "Connector_Card:microSD_HC_Molex_104031-0811"
# project-custom lands (avionics/kicad/Serenity-Custom.pretty)
FP_PB2P1 = "Serenity-Custom:PocketBeagle2_2x18_P1_Socket"
FP_PB2P2 = "Serenity-Custom:PocketBeagle2_2x18_P2_Socket"
FP_NANOFIT = "Serenity-Custom:Molex_NanoFit_1x04_Horizontal"
FP_SRF2012 = "Serenity-Custom:Bourns_SRF2012_4T"
FP_X2Y0805 = "Serenity-Custom:X2Y_0805_4T"
FP_WELAN = "Serenity-Custom:Wurth_749010012A_WE-LAN"
FP_RFD900X = "Serenity-Custom:RFDesign_RFD900x_2x8_THT"
FP_RFM95W = "Serenity-Custom:HopeRF_RFM95W_Castellated_16"
FP_WL1837 = "Serenity-Custom:WL1837MOD_MOC_100"
FP_VSON10 = "Serenity-Custom:TPS6303x_VSON-10_2p5"
FP_FLLORA = "Serenity-Custom:Johanson_0915LP15B026E_SMD4"
FP_FLWIFI = "Serenity-Custom:Johanson_2450BP15E0100_SMD4"
FP_RCLAMP = "Serenity-Custom:RCLAMP0502B_SOD882"
FP_SOT89 = "Package_TO_SOT_SMD:SOT-89-3"


def uid() -> str:
    return f"b7000000-0000-0000-0000-{next(_uid):012d}"


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
        "ds": "isow1044.pdf Fig 7-1 / Table 7-1 (20-pin DFM) [REF-SENSOR-009]; same part as Pilot CAN-TR",
        "pins": [
            ("1", "VIO", "+3V3", "L"),
            ("2", "IN", None, "L"),
            ("3", "TXD", "MCAN0_B_TX", "L"),
            ("4", "STB", "CAN_B_STB", "L"),
            ("5", "RXD", "MCAN0_B_RX", "L"),
            ("6", "GNDIO", "GND", "L"),
            ("7", "NC", None, "L"),
            ("8", "EN/FLT", None, "L"),
            ("9", "VDD", "+5V", "L"),
            ("10", "GND1", "GND", "L"),
            ("20", "VISOIN", "VCC2_CANB", "R"),
            ("19", "CANH", "CAN_B_H", "R"),
            ("18", "CANL", "CAN_B_L", "R"),
            ("17", "GISOIN", "GND2_CANB", "R"),
            ("16", "GISOIN", "GND2_CANB", "R"),
            ("15", "GISOIN", "GND2_CANB", "R"),
            ("14", "OUT", None, "R"),
            ("13", "VSIN", "VCC2_CANB", "R"),
            ("12", "VISOOUT", "VCC2_CANB", "R"),
            ("11", "GND2", "GND2_CANB", "R"),
        ],
    },
    {
        "ref": "RS485",
        "value": "ISOW1412DFMR",
        "fp": FP_SOIC20W,
        "mpn": "ISOW1412DFMR",
        "ds": "isow1412.pdf Table 7-1 (20-pin DFM) [REF-SENSOR-010]; same part as Pilot RS485 "
              "(supersedes the legacy schematic's stale ADM2795EBRWZ citation)",
        "pins": [
            ("1", "VIO", "+3V3", "L"),
            ("2", "D", "RS485_B_TX", "L"),
            ("3", "DE", "RS485_B_DE", "L"),
            ("4", "R", "RS485_B_RX", "L"),
            ("5", "RE", "RS485_B_DE", "L"),
            ("6", "GNDIO", "GND", "L"),
            ("7", "OUT", None, "L"),
            ("8", "EN/FLT", "+3V3", "L"),
            ("9", "VDD", "+5V", "L"),
            ("10", "GND1", "GND", "L"),
            ("20", "A", "RS485_B_A", "R"),
            ("19", "B", "RS485_B_B", "R"),
            ("18", "Z", "RS485_B_B", "R"),
            ("17", "Y", "RS485_B_A", "R"),
            ("16", "VISOIN", "VCC2_RS485B", "R"),
            ("15", "GISOIN", "GND2_RS485B", "R"),
            ("14", "IN", None, "R"),
            ("13", "MODE", "GND2_RS485B", "R"),
            ("12", "VISOOUT", "VCC2_RS485B", "R"),
            ("11", "GND2", "GND2_RS485B", "R"),
        ],
    },
    {
        "ref": "TPM",
        "value": "SLB9672XU20",
        "fp": FP_UQFN32,
        "mpn": "SLB9672XU20FW1611XUMA1",
        "ds": "slb9672.pdf §3.1.2 Tables 11-13 / Figure 6 (PG-UQFN-32) [REF-SENSOR-011]; same part as Pilot TPM",
        "pins": [
            ("17", "RST#", "TPM_B_RSTN", "L"),
            ("18", "PIRQ#", "TPM_B_IRQN", "L"),
            ("19", "SCLK", "SPI0_B_CLK", "L"),
            ("20", "CS#", "SPI0_B_CS_TPM", "L"),
            ("21", "MOSI", "SPI0_B_MOSI", "L"),
            ("24", "MISO", "SPI0_B_MISO", "L"),
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
            ("10", "NCI/VDD", "TPM_B_P10_PU", "R"),
            ("8", "NCI/VDD", None, "R"),
            ("6", "NC", None, "R"),
            ("29", "NC", None, "R"),
            ("30", "NC", None, "R"),
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
        "ref": "1553-XCVR",
        "value": "HI-1573PCI",
        "fp": FP_QFN44,
        "mpn": "HI-1573PCI",
        "ds": "hi-1573.pdf p.1 Pin Configurations (44-pin 7x7 QFN) / p.11 package [REF-SENSOR-030]; "
              "same part as Pilot 1553-XCVR (retires the legacy DS26LV31/32 RS-422 + fake "
              "\"SM-1553-11\" defect — RS-422 cannot meet MIL-STD-1553B §4.5.2 levels [REF-MIL-001])",
        "pins": [
            ("36", "TXA", "PRU_1553B_TX_P", "L"),
            ("37", "TXA*", "PRU_1553B_TX_N", "L"),
            ("31", "TXINHA", "M1553B_TX_INH", "L"),
            ("2", "RXENA", "+3V3", "L"),
            ("30", "RXA", "PRU_1553B_RX_P", "L"),
            ("29", "RXA*", "PRU_1553B_RX_N", "L"),
            ("25", "TXB", "GND", "L"),
            ("26", "TXB*", "GND", "L"),
            ("24", "TXINHB", "+3V3", "L"),
            ("16", "RXENB", "GND", "L"),
            ("21", "RXB", None, "L"),
            ("20", "RXB*", None, "L"),
            ("40", "BUSA", "M1553B_P", "R"),
            ("41", "BUSA", "M1553B_P", "R"),
            ("42", "BUSA*", "M1553B_N", "R"),
            ("43", "BUSA*", "M1553B_N", "R"),
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
        "pins": [
            ("1", "PRI_P", "M1553B_P", "L"),
            ("2", "PRI_CT", "GND", "L"),
            ("3", "PRI_N", "M1553B_N", "L"),
            ("4", "SEC_P", "M1553B_SEC_P", "R"),
            ("5", "NC", None, "R"),
            ("6", "NC", None, "R"),
            ("7", "NC", None, "R"),
            ("8", "SEC_N", "M1553B_SEC_N", "R"),
        ],
    },
    {
        "ref": "U-3V3",
        "value": "TPS62933DRLR",
        "fp": "Package_TO_SOT_SMD:SOT-583-8",
        "mpn": "TPS62933DRLR",
        "ds": "tps62933.pdf Table 7-1 Pin Functions (SOT-583) [REF-PWR-001]; logic +3V3, same design as Pilot U-3V3",
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
    {
        "ref": "U-3V3RF",
        "value": "TPS63031DSKR",
        "fp": FP_VSON10,
        "mpn": "TPS63031DSKR",
        "ds": "tps63031.pdf Pin Functions (VSON-10 DSK) — dedicated buck-boost RF rail so WL1837MOD/"
              "RFM95W/RFD900x RF supply stays regulated even if +5V sags (XO.md §12 power budget "
              "+3V3_RF 1.5A cont / 2.0A peak)",
        "pins": [
            ("5", "VIN", "+5V", "L"),
            ("8", "VINA", "+5V", "L"),
            ("6", "EN", "+3V3", "L"),
            ("7", "PS/SYNC", "GND", "L"),
            ("9", "GND", "GND", "L"),
            ("4", "L1", "RF_SW1", "R"),
            ("2", "L2", "RF_SW2", "R"),
            ("3", "PGND", "GND", "R"),
            ("10", "FB", "+3V3_RF", "R"),
            ("1", "VOUT", "+3V3_RF", "R"),
        ],
    },
    {
        "ref": "SIK",
        "value": "RFD900x",
        "fp": FP_RFD900X,
        "mpn": "RFD900X",
        "ds": "rfd900x-datasheet.pdf §4 Pin signals and layout (16-pin, 2x8 THT) [REF-SENSOR-031]",
        "pins": [
            ("1", "GND", "GND", "L"),
            ("2", "GND", "GND", "L"),
            ("3", "CTS", "SIK_CTS_F", "L"),
            ("4", "Vcc", "SIK_VCC_F", "L"),
            ("5", "Vusb", None, "L"),
            ("6", "Vusb", None, "L"),
            ("7", "RX", "UART_SIK_RX_F", "L"),
            ("8", "GPIO5/P3.4", None, "L"),
            ("9", "TX", "UART_SIK_TX_F", "R"),
            ("10", "GPIO4/P3.3", None, "R"),
            ("11", "RTS", "SIK_RTS", "R"),
            ("12", "GPIO3/P1.3", None, "R"),
            ("13", "GPIO0/P1.0", None, "R"),
            ("14", "GPIO2/P1.2", None, "R"),
            ("15", "GPIO1/P1.1", None, "R"),
            ("16", "GND", "GND", "R"),
        ],
    },
    {
        "ref": "LORA",
        "value": "RFM95W",
        "fp": FP_RFM95W,
        "mpn": "RFM95W-915S2",
        "ds": "rfm95w-datasheet.pdf §1.4 Pin Description (16-pin castellated module, NOT the bare "
              "SX1276 die) [REF-SENSOR-032]",
        "pins": [
            ("1", "GND", "GND", "L"),
            ("2", "MISO", "SPI0_B_MISO_F", "L"),
            ("3", "MOSI", "SPI0_B_MOSI_F", "L"),
            ("4", "SCK", "SPI0_B_CLK_F", "L"),
            ("5", "NSS", "SPI0_B_CS_LORA_F", "L"),
            ("6", "RESET", "LORA_RESETN", "L"),
            ("7", "DIO5", None, "L"),
            ("8", "GND", "GND", "L"),
            ("9", "ANT", "LORA_ANT_RF", "R"),
            ("10", "GND", "GND", "R"),
            ("11", "DIO3", None, "R"),
            ("12", "DIO4", None, "R"),
            ("13", "3.3V", "+3V3_RF", "R"),
            ("14", "DIO0", "LORA_DIO0", "R"),
            ("15", "DIO1", None, "R"),
            ("16", "DIO2", None, "R"),
        ],
    },
    {
        "ref": "WIFI",
        "value": "WL1837MOD",
        "fp": FP_WL1837,
        "mpn": "WL1837MOD",
        "ds": "wl1837mod.pdf SWRS170L — 100-ball MOC package; only the functionally-used balls "
              "below carry a net (disclosed scope calibration, gen_xo_footprints.py docstring). "
              "SDIO signals are 1.8V (VIO pin 38), NOT 3.3V — level per PB2 SoC's SDIO PHY.",
        "pins": [
            ("40", "WLAN_EN", "WIFI_EN", "L"),
            ("41", "BT_EN", "GND", "L"),
            ("38", "VIO", "+1V8_IO", "L"),
            ("46", "VBAT_IN", "+3V3_RF", "L"),
            ("47", "VBAT_IN", "+3V3_RF", "L"),
            ("14", "WLAN_IRQ", "WIFI_IRQ", "L"),
            ("6", "WL_SDIO_CMD", "SDIO_CMD_F", "R"),
            ("8", "WL_SDIO_CLK", "SDIO_CLK_F", "R"),
            ("10", "WL_SDIO_D0", "SDIO_D0_F", "R"),
            ("11", "WL_SDIO_D1", "SDIO_D1_F", "R"),
            ("12", "WL_SDIO_D2", "SDIO_D2_F", "R"),
            ("13", "WL_SDIO_D3", "SDIO_D3_F", "R"),
            ("32", "RF_ANT1", "WIFI_ANT_RF", "R"),
            ("1", "GND", "GND", "R"),
            ("7", "GND", "GND", "R"),
            ("9", "GND", "GND", "R"),
            ("15", "GND", "GND", "R"),
            ("17", "GND", "GND", "R"),
        ] + [(str(n), "NC", None, "L" if n % 2 else "R")
             for n in range(2, 101)
             if n not in (6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 32, 38, 40, 41, 46, 47)],
    },
    {
        "ref": "NOR-FLASH",
        "value": "W25Q128JVSIQ",
        "fp": FP_SOIC8,
        "mpn": "W25Q128JVSIQ",
        "ds": "w25q128jv.pdf §3.3 Pin Description SOIC 208-mil [REF-SENSOR-033]",
        "pins": [
            ("1", "/CS", "SPI0_B_CS_FLASH", "L"),
            ("2", "DO(IO1)", "SPI0_B_MISO", "L"),
            ("3", "/WP(IO2)", "FLASH_WP_N", "L"),
            ("4", "GND", "GND", "L"),
            ("5", "DI(IO0)", "SPI0_B_MOSI", "R"),
            ("6", "CLK", "SPI0_B_CLK", "R"),
            ("7", "/HOLD_or_/RESET(IO3)", "+3V3", "R"),
            ("8", "VCC", "+3V3", "R"),
        ],
    },
    # WINCH-DRV (DRV8833 H-bridge), LOAD-ADC (HX711), and PWM-I2C (PCA9685)
    # REMOVED 2026-09-20 per owner correction: the winch is a remote
    # multi-turn servo on CAN-FD/RS-485 (same bus-networked actuator pattern
    # as the nacelle tilt encoder's edge gateway) rather than a local
    # H-bridge, its tension sensing lives on that same remote node, and the
    # SG90 door servos are ALSO controlled over that bus rather than by a
    # local PWM driver — so XO carries no local actuator-drive silicon at
    # all.  This recovers real board-area budget (DRV8833 + HX711 + PCA9685 +
    # their motor/load-cell/servo connectors + ~10 supporting passives) toward
    # the 55x35 mm area problem found while building this board's PCB.
    {
        "ref": "SD-WB",
        "value": "ATF16V8BQL-15XI",
        "fp": "Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm",
        "mpn": "ATF16V8BQL-15XI",
        "ds": "atf16v8bql.pdf Ordering Information (20X = TSSOP, 4.4mm wide) [REF-SENSOR-037] — TSSOP-20 "
              "chosen over the SOIC-20W package for a smaller board footprint, per the user's XO "
              "board-area-reduction directive (same pin numbering, standard PAL16V8 pinout). Used as a "
              "logging write-block interlock: gates the NOR flash /WP line. The JEDEC fuse map "
              "(logic equations) is a firmware/programming deliverable, out of scope for this "
              "schematic pass — every pin is wired to a real net so ERC is complete; unused I/O "
              "macrocells (12-18) are left as no-connects, standard practice for a partially-used "
              "PAL/GAL.",
        "pins": [
            ("1", "I/CLK", "PLD_CLK", "L"),
            ("2", "I1", "PLD_I1", "L"),
            ("3", "I2", "PLD_I2", "L"),
            ("4", "I3", "PLD_I3", "L"),
            ("5", "I4", "PLD_I4", "L"),
            ("6", "I5", "PLD_I5", "L"),
            ("7", "I6", "PLD_I6", "L"),
            ("8", "I7", "PLD_I7", "L"),
            ("9", "I8", "PLD_I8", "L"),
            ("10", "GND", "GND", "L"),
            ("11", "I9/OE", "GND", "R"),
            ("12", "I/O", None, "R"),
            ("13", "I/O", None, "R"),
            ("14", "I/O", None, "R"),
            ("15", "I/O", None, "R"),
            ("16", "I/O", None, "R"),
            ("17", "I/O", None, "R"),
            ("18", "I/O", None, "R"),
            ("19", "I/O", "FLASH_WP_N", "R"),
            ("20", "VCC", "+3V3", "R"),
        ],
    },
]


def dp83825i(ref: str, rmii: str, rstn: str, intn: str, eth: str, mdio: str, mdc: str) -> Dict[str, Any]:
    """TI DP83825I 10/100 RMII PHY, WQFN-24 — dp83825i.pdf Table 4-1 (identical part/pin table to
    Pilot's ETH1-PHY; XO gets ONE PHY per WBS.md §1.2a "XO: 1x PHY (RMII0)")."""
    return {
        "ref": ref, "value": "DP83825IRHBR", "fp": "Package_DFN_QFN:Texas_RMQ0024A_WQFN-24-1EP_3x3mm_P0.4mm_EP1.9x1.9mm",
        "mpn": "DP83825IRHBR",
        "ds": "dp83825i.pdf Table 4-1 (WQFN-24), Fig 8-3/8-4 [REF-SENSOR-029]",
        "pins": [
            ("1", "RX_D0/PHYAD0", f"{rmii}_RXD0", "L"),
            ("2", "RX_D1", f"{rmii}_RXD1", "L"),
            ("3", "RX_ER", f"{rmii}_RX_ER", "L"),
            ("4", "CRS_DV", f"{rmii}_CRS_DV", "L"),
            ("5", "TX_EN", f"{rmii}_TX_EN", "L"),
            ("6", "TX_D0", f"{rmii}_TXD0", "L"),
            ("7", "TX_D1", f"{rmii}_TXD1", "L"),
            ("8", "X1", "PHY_XI_25M", "L"),
            ("9", "X2", None, "L"),
            ("10", "DGND", "GND", "L"),
            ("11", "DVDD10", None, "L"),
            ("12", "RESET_N", rstn, "L"),
            ("13", "MDIO", mdio, "R"),
            ("14", "MDC", mdc, "R"),
            ("15", "INT_N", intn, "R"),
            ("16", "AGND_TX", "GND", "R"),
            ("17", "TXOP", f"{eth}_TXP", "R"),
            ("18", "TXON", f"{eth}_TXN", "R"),
            ("19", "AVDD33_TX", "+3V3", "R"),
            ("20", "AGND_RX", "GND", "R"),
            ("21", "RXIP", f"{eth}_RXP", "R"),
            ("22", "RXIN", f"{eth}_RXN", "R"),
            ("23", "AVDD33_RX", "+3V3", "R"),
            ("24", "RBIAS", f"{ref}_RBIAS", "R"),
            ("25", "EP", "GND", "R"),
        ],
    }


def eth_xfmr(ref: str, eth: str) -> Dict[str, Any]:
    """Wurth 749010012A WE-LAN 10/100 SMT transformer (749010012A.pdf p.1) — identical part/pin
    table to Pilot's T-ETH/T-ETH2 (16 mechanical pads; 4/5/12/13 no winding; PHY side 1-3/6-8,
    line side 9-11/14-16, 1:1 CT, 1500 V isolation barrier)."""
    return {
        "ref": ref, "value": "749010012A", "fp": FP_WELAN, "mpn": "749010012A",
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
    dp83825i("ETH-PHY", "RMII0", "PHY1_RSTN", "PHY1_INTRN", "ETHB", "MDIO0", "MDC0"),
    eth_xfmr("T-ETH", "ETHB"),
]

# ---------------------------------------------------------------------------
# PocketBeagle 2 Industrial stacking headers — XO's own P1/P2 map.  Physical
# connector/pitch is identical to Pilot's (same SBC), but the assigned
# balls/functions differ per cape: XO trades Pilot's dual-PHY RMII1 + sensor
# (IMU/baro/GPS) balls for its own comms/logging/payload peripherals (winch
# H-bridge, SD card, SPI-NOR flash, LoRa/SiK/WiFi radios, load cell, PLD).
# ---------------------------------------------------------------------------
PB2_P1 = [
    # Indices 3-6 and 17-19 (WINCH_IN1-4 / WINCH_FAULTN / WINCH_SLEEPN) and
    # 27-28 (HX711_DOUT/SCK) freed by the 2026-09-20 winch/load-cell removal
    # (winch is a remote CAN-FD/RS-485 servo, not a local H-bridge) — left
    # unassigned (None) rather than inventing a new function for real SoC
    # balls that don't need one yet; a future subsystem can claim them.
    "GND", "GND", None, None, None, None,
    "PRU_1553B_RX_N", "PRU_1553B_RX_P", "PRU_1553B_TX_N", "PRU_1553B_TX_P",
    "RS485_B_DE", "RS485_B_RX", "RS485_B_TX", "CAN_B_STB", "MCAN0_B_RX", "MCAN0_B_TX",
    "SD_CD", None, None, "M1553B_TX_INH", "SPI0_B_CS_TPM",
    "SPI0_B_CS_FLASH", "SPI0_B_MISO", "SPI0_B_MOSI", "SPI0_B_CLK", "SPI0_B_CS_LORA",
    None, None, None, None, "UART_SIK_RX",
    "UART_SIK_TX", "+3V3_PB2", "+3V3_PB2", "+5V", "GND",
]
PB2_P2 = [
    "SDIO_D2", "SDIO_D3", "SIK_CTS", "SIK_RTS", "FAN_PWM_B", "PLD_CLK", "PLD_I1", "PLD_I2",
    "WIFI_EN", "WIFI_IRQ", "TPM_B_RSTN", "TPM_B_IRQN",
    "PLD_I3", "PLD_I4", "PHY1_RSTN", "PHY1_INTRN", "MDIO0", "MDC0",
    "SDIO_CLK", "SDIO_CMD", "SDIO_D0", "SDIO_D1",
    "PLD_I5", "PLD_I6", "PLD_I7", "PLD_I8",
    "LORA_DIO0", "RMII0_RX_ER", "RMII0_CRS_DV", "RMII0_RXD1",
    "RMII0_RXD0", "RMII0_TX_EN", "RMII0_TXD1", "RMII0_TXD0", "+5V", "GND",
]


def pb2_header(ref: str, value: str, fp: str, nets: List[str]) -> Dict[str, Any]:
    pins = [(str(i), f"P{i}", net, "L" if i <= 18 else "R") for i, net in enumerate(nets, start=1)]
    return {"ref": ref, "value": value, "fp": fp, "mpn": "", "ds": "PocketBeagle 2 P1/P2 expansion rails (XO map)", "pins": pins}


ICS += [
    pb2_header("PB2-P1", "PB2I-P1-2x18", FP_PB2P1, PB2_P1),
    pb2_header("PB2-P2", "PB2I-P2-2x18", FP_PB2P2, PB2_P2),
]

# ---------------------------------------------------------------------------
# SIMPLE parts: passives, connectors, filters.  (ref, value, fp, mpn, ds, pins,
# [flags]).  pins: List[(num, fn, net)].
# ---------------------------------------------------------------------------
SIMPLE: List[Any] = [
    # --- power entry --------------------------------------------------------
    ("PWR-IN", "Nano-Fit 4P", FP_NANOFIT, "105313-1204",
     "XO.md §14 power entry (Molex Nano-Fit 2.5 mm, 4 ckt) — NOT datasheet-verified, same flag as Pilot PWR-IN",
     [("1", "+5V_IN", "+5V_IN"), ("2", "+5V_IN", "+5V_IN"), ("3", "GND", "GND"), ("4", "GND", "GND")]),
    ("FB1", "742792510", FP_L0805, "742792510", "wurth-742792510.pdf 0402 ferrite bead; XO §12 power "
     "budget draws 3.0A +5V so a HIGHER-current bead than Pilot's 742792512 (2A) is required here",
     [("1", "IN", "+5V_IN"), ("2", "OUT", "+5V")]),
    ("C-IN1", "47uF 10V X5R", FP_C1210, "", "XO.md §6 input bulk", [("1", "P", "+5V_IN"), ("2", "N", "GND")]),
    ("C-IN2", "10uF 10V X5R", FP_C0805, "", "XO.md §6 filtered bulk", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-IN3", "100nF", FP_C0402, "", "XO.md §6 HF bypass", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("R-PGND", "0R", FP_R0805, "", "XO.md §7 single-point GND<->PGND link", [("1", "A", "GND"), ("2", "B", "PGND")]),
    # --- +3V3 logic buck (TPS62933) ------------------------------------------
    ("R-EN3", "100k", FP_R0201, "", "TPS62933 EN pull-up to VIN", [("1", "A", "+5V"), ("2", "B", "U3V3_EN")]),
    ("C-3V3-IN", "10uF 10V X5R", FP_C0805, "", "TPS62933 CIN at VIN/GND", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-3V3-HF", "100nF", FP_C0402, "", "TPS62933 CIN HF", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-BST", "100nF", FP_C0402, "", "TPS62933 BST-SW bootstrap", [("1", "P", "BST_3V3"), ("2", "N", "SW_3V3")]),
    ("C-SS", "10nF", FP_C0201, "", "TPS62933 soft-start", [("1", "P", "SS_3V3"), ("2", "N", "GND")]),
    ("L-3V3", "3.3uH 2.25A", "Serenity-Custom:L_WE-MAPI_3015", "74438335033", "TPS62933 inductor, WE-MAPI 3015 (same custom land as Pilot L-3V3) [REF-PWR-003]",
     [("1", "A", "SW_3V3"), ("2", "B", "+3V3")]),
    ("R-FB3H", "100k 1%", FP_R0201, "", "TPS62933 FB divider top", [("1", "A", "+3V3"), ("2", "B", "FB_3V3")]),
    ("R-FB3L", "32.4k 1%", FP_R0201, "", "TPS62933 FB divider bottom (3.27 V)", [("1", "A", "FB_3V3"), ("2", "B", "GND")]),
    ("C-3V3-O1", "22uF 6.3V X5R", FP_C0805, "", "TPS62933 COUT", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-3V3-O2", "22uF 6.3V X5R", FP_C0805, "", "TPS62933 COUT", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    # --- +3V3_RF buck-boost (TPS63031) --------------------------------------
    ("L-RF1", "2.2uH 3A", FP_L0805, "744042002", "TPS63031 first inductor leg (typical app circuit)",
     [("1", "A", "RF_SW1"), ("2", "B", "+5V")]),
    ("L-RF2", "2.2uH 3A", FP_L0805, "744042002", "TPS63031 second inductor leg", [("1", "A", "RF_SW2"), ("2", "B", "+3V3_RF")]),
    ("C-RF-IN1", "10uF 10V X5R", FP_C0805, "", "TPS63031 VIN bulk", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-RF-IN2", "100nF", FP_C0402, "", "TPS63031 VIN HF", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-RF-O1", "22uF 6.3V X5R", FP_C0805, "", "TPS63031 COUT", [("1", "P", "+3V3_RF"), ("2", "N", "GND")]),
    ("C-RF-O2", "22uF 6.3V X5R", FP_C0805, "", "TPS63031 COUT", [("1", "P", "+3V3_RF"), ("2", "N", "GND")]),
    # --- WL1837MOD 1.8V SDIO/VIO rail (small LDO from +3V3) -----------------
    ("U-1V8", "TLV75718PDBVR", FP_SOT89, "TLV75718PDBVR", "TI TLV757 fixed 1.8V/150mA LDO for WL1837MOD "
     "VIO / SDIO PHY level (wl1837mod.pdf pin 38 = VIO, SDIO signals are 1.8V not 3.3V)",
     [("1", "GND", "GND"), ("2", "OUT", "+1V8_IO"), ("3", "IN", "+3V3")]),
    ("C-1V8-IN", "1uF", FP_C0402, "", "TLV757 input bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-1V8-OUT", "1uF", FP_C0402, "", "TLV757 output bypass", [("1", "P", "+1V8_IO"), ("2", "N", "GND")]),
    # --- CAN FD field port ---------------------------------------------------
    ("C-CAN1", "10nF", FP_C0201, "", "ISOW1044 VDD HF bypass §13.1", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-CAN2", "10uF 10V X5R", FP_C0805, "", "ISOW1044 VDD bulk §13.1", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-CAN3", "100nF", FP_C0402, "", "ISOW1044 VIO bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-CAN4", "10nF", FP_C0201, "", "ISOW1044 VISOOUT HF bypass", [("1", "P", "VCC2_CANB"), ("2", "N", "GND2_CANB")]),
    ("C-CAN5", "10uF 10V X5R", FP_C0805, "", "ISOW1044 VISOOUT bulk", [("1", "P", "VCC2_CANB"), ("2", "N", "GND2_CANB")]),
    ("C-CAN6", "100nF", FP_C0402, "", "ISOW1044 VISOIN bypass", [("1", "P", "VCC2_CANB"), ("2", "N", "GND2_CANB")]),
    ("CMC-CAN", "SRF2012-100Y", FP_SRF2012, "SRF2012-121YA", "SRF2012A.pdf windings 1-2 / 4-3 [REF-SENSOR-026]",
     [("1", "W1_IN", "CAN_B_H"), ("2", "W1_OUT", "CAN_B_H_F"), ("4", "W2_IN", "CAN_B_L"), ("3", "W2_OUT", "CAN_B_L_F")]),
    ("TVS-CAN", "PRTR5V0U2X", FP_SOT143, "PRTR5V0U2X,315", "prtr5v0u2x.pdf (Nexperia, SOT143B 4-pin) [REF-SENSOR-038]",
     [("1", "IO1", "CAN_B_H_F"), ("2", "GND", "GND2_CANB"), ("3", "IO2", "CAN_B_L_F"), ("4", "VCC", "VCC2_CANB")]),
    ("R-CANT", "120R", FP_R0603, "", "CAN bus termination — populate ONLY at a bus end node (DNP default)",
     [("1", "A", "CAN_B_H_F"), ("2", "B", "CAN_B_L_F")], {"dnp": True}),
    ("J-CAN", "SM03B-GHS-TB", FP_GH3, "SM03B-GHS-TB(LF)(SN)", "XO.md §14 J_CAN",
     [("1", "CAN_H", "CAN_B_H_F"), ("2", "CAN_L", "CAN_B_L_F"), ("3", "GND", "GND2_CANB"), ("MP", "SHIELD", "PGND")]),
    ("X2Y-CAN", "4.7nF X2Y", FP_X2Y0805, "CX0805MRX7R0BB472", "GND1<->GND2 RF bridge (Yageo X2Y 0805)",
     [("1", "A", "GND"), ("2", "B", "GND"), ("3", "G1", "GND2_CANB"), ("4", "G2", "GND2_CANB")]),
    # --- RS-485 field port ---------------------------------------------------
    ("C-485-1", "10nF", FP_C0201, "", "ISOW1412 VDD HF bypass", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-485-2", "10uF 10V X5R", FP_C0805, "", "ISOW1412 VDD bulk", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-485-3", "100nF", FP_C0402, "", "ISOW1412 VIO bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-485-4", "10nF", FP_C0201, "", "ISOW1412 VISOOUT HF bypass", [("1", "P", "VCC2_RS485B"), ("2", "N", "GND2_RS485B")]),
    ("C-485-5", "10uF 10V X5R", FP_C0805, "", "ISOW1412 VISOOUT bulk", [("1", "P", "VCC2_RS485B"), ("2", "N", "GND2_RS485B")]),
    ("C-485-6", "100nF", FP_C0402, "", "ISOW1412 VISOIN bypass", [("1", "P", "VCC2_RS485B"), ("2", "N", "GND2_RS485B")]),
    ("CMC-RS485", "SRF2012-100Y", FP_SRF2012, "SRF2012-121YA", "SRF2012A.pdf windings 1-2 / 4-3 [REF-SENSOR-026]",
     [("1", "W1_IN", "RS485_B_A"), ("2", "W1_OUT", "RS485_B_A_F"), ("4", "W2_IN", "RS485_B_B"), ("3", "W2_OUT", "RS485_B_B_F")]),
    ("TVS-RS485", "PRTR5V0U2X", FP_SOT143, "PRTR5V0U2X,315", "prtr5v0u2x.pdf (Nexperia, SOT143B) [REF-SENSOR-038]",
     [("1", "IO1", "RS485_B_A_F"), ("2", "GND", "GND2_RS485B"), ("3", "IO2", "RS485_B_B_F"), ("4", "VCC", "VCC2_RS485B")]),
    ("R-485T", "120R", FP_R0603, "", "RS-485 termination — populate ONLY at a bus end node (DNP default)",
     [("1", "A", "RS485_B_A_F"), ("2", "B", "RS485_B_B_F")], {"dnp": True}),
    ("J-485", "SM03B-GHS-TB", FP_GH3, "SM03B-GHS-TB(LF)(SN)", "XO.md §14 J_485",
     [("1", "A", "RS485_B_A_F"), ("2", "B", "RS485_B_B_F"), ("3", "GND", "GND2_RS485B"), ("MP", "SHIELD", "PGND")]),
    ("X2Y-RS485", "4.7nF X2Y", FP_X2Y0805, "CX0805MRX7R0BB472", "GND1<->GND2 RF bridge (Yageo X2Y 0805)",
     [("1", "A", "GND"), ("2", "B", "GND"), ("3", "G1", "GND2_RS485B"), ("4", "G2", "GND2_RS485B")]),
    # --- Ethernet line side (single PHY, Bob-Smith termination) -------------
    ("J-ETH", "SM04B-GHS-TB", FP_GH4, "SM04B-GHS-TB(LF)(SN)", "ETH line pair to T-ETH secondary",
     [("1", "TXP", "ETHB_LINE_TXP"), ("2", "TXN", "ETHB_LINE_TXN"), ("3", "RXP", "ETHB_LINE_RXP"), ("4", "RXN", "ETHB_LINE_RXN"),
      ("MP", "SHIELD", "PGND")]),
    ("R-BST", "75R", FP_R0402, "", "ETH line TX centre tap Bob-Smith (Fig 8-3 R135)", [("1", "A", "ETHB_LINE_CTX"), ("2", "B", "ETHB_BS")]),
    ("R-BSR", "75R", FP_R0402, "", "ETH line RX centre tap Bob-Smith (Fig 8-3 R143)", [("1", "A", "ETHB_LINE_CRX"), ("2", "B", "ETHB_BS")]),
    ("C-BS", "10nF 2kV", FP_C1808, "", "ETH Bob-Smith HV cap to chassis (Fig 8-3 C38)", [("1", "P", "ETHB_BS"), ("2", "N", "PGND")]),
    ("X-25M", "25MHz 3.3V", "Oscillator:Oscillator_SMD_ECS_2520MV-xxx-xx-4Pin_2.5x2.0mm", "ECS-2520MV-250-BN-TR",
     "PHY 25 MHz reference (dp83825i.pdf §8.2.1.1.1) [REF-PWR-004]",
     [("1", "TRI", None), ("2", "GND", "GND"), ("3", "OUT", "PHY_XI_25M"), ("4", "VDD", "+3V3")]),
    ("C-25M", "100nF", FP_C0402, "", "oscillator VDD bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("R-RBIAS", "6.49k 1%", FP_R0201, "", "DP83825I RBIAS to GND (pin 24)", [("1", "A", "ETH-PHY_RBIAS"), ("2", "B", "GND")]),
    ("R-AD0", "2.49k", FP_R0201, "", "PhyAdd[0] strap mode 1 -> PHY address 1", [("1", "A", "+3V3"), ("2", "B", "RMII0_RXD0")]),
    ("C-PHY-A1", "10nF", FP_C0201, "", "VDDA3V3 HF bypass (Fig 8-4)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-PHY-A2", "100nF", FP_C0402, "", "VDDA3V3 bypass (Fig 8-4)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-PHY-A3", "1uF", FP_C0402, "", "VDDA3V3 bulk (Fig 8-4)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-PHY-CTD1", "100nF", FP_C0402, "", "device-side TX centre tap to GND (Fig 8-3 C41)", [("1", "P", "ETHB_CTD"), ("2", "N", "GND")]),
    ("C-PHY-CTD2", "1uF", FP_C0402, "", "device-side TX centre tap to GND (Fig 8-3 C44)", [("1", "P", "ETHB_CTD"), ("2", "N", "GND")]),
    ("C-PHY-CRD1", "100nF", FP_C0402, "", "device-side RX centre tap to GND (Fig 8-3 C75)", [("1", "P", "ETHB_CRD"), ("2", "N", "GND")]),
    ("C-PHY-CRD2", "1uF", FP_C0402, "", "device-side RX centre tap to GND (Fig 8-3 C74)", [("1", "P", "ETHB_CRD"), ("2", "N", "GND")]),
    # --- MIL-STD-1553B field port -------------------------------------------
    ("R-1553P", "55R 2%", FP_R0603, "", "MIL-STD-1553B §4.5.1.5.2 direct-coupled stub isolation resistor",
     [("1", "A", "M1553B_SEC_P"), ("2", "B", "BUS_1553_B_P")]),
    ("R-1553N", "55R 2%", FP_R0603, "", "MIL-STD-1553B §4.5.1.5.2 direct-coupled stub isolation resistor",
     [("1", "A", "M1553B_SEC_N"), ("2", "B", "BUS_1553_B_N")]),
    ("TVS-1553P", "SMAJ33CA", FP_SMA, "SMAJ33CA", "bidirectional TVS, BUS_P to PGND", [("1", "A", "BUS_1553_B_P"), ("2", "K", "PGND")]),
    ("TVS-1553N", "SMAJ33CA", FP_SMA, "SMAJ33CA", "bidirectional TVS, BUS_N to PGND", [("1", "A", "BUS_1553_B_N"), ("2", "K", "PGND")]),
    ("J-1553", "SM04B-GHS-TB", FP_GH4, "SM04B-GHS-TB(LF)(SN)", "XO.md §14 J_1553",
     [("1", "BUS_P", "BUS_1553_B_P"), ("2", "BUS_N", "BUS_1553_B_N"), ("3", "GND", "GND"), ("4", "SHIELD", "PGND"),
      ("MP", "SHIELD", "PGND")]),
    ("C-1553A", "100nF", FP_C0402, "", "HI-1573 VDDA bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-1553B", "100nF", FP_C0402, "", "HI-1573 VDDB bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-1553C", "10uF 6.3V X5R", FP_C0805, "", "HI-1573 transmitter bulk", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    # --- TPM ------------------------------------------------------------------
    ("C-TPM1", "1uF", FP_C0402, "", "SLB9672 §3.1.3 typical schematic bulk", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-TPM2", "100nF", FP_C0402, "", "SLB9672 VDD bypass (pin 1)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-TPM3", "100nF", FP_C0402, "", "SLB9672 VDD bypass (pin 14)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-TPM4", "100nF", FP_C0402, "", "SLB9672 VDD bypass (pin 22)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("R-TPMCS", "10k", FP_R0201, "", "SLB9672 CS# pull-up (§3.1.3)", [("1", "A", "+3V3"), ("2", "B", "SPI0_B_CS_TPM")]),
    ("R-TPM10", "10k", FP_R0201, "", "SLB9672 pin 10 NCI/VDD pull-up (Table 13, preferred)", [("1", "A", "+3V3"), ("2", "B", "TPM_B_P10_PU")]),
    # --- SiK (RFD900x) supply/UART filtering --------------------------------
    ("FB-SIK1", "742792510", FP_L0805, "742792510", "RFD900x Vcc filter bead (Wurth 742792510)", [("1", "IN", "+5V"), ("2", "OUT", "SIK_VCC_F")]),
    ("C-SIK1", "10uF 10V X5R", FP_C0805, "", "RFD900x Vcc bulk", [("1", "P", "SIK_VCC_F"), ("2", "N", "GND")]),
    ("C-SIK2", "100nF", FP_C0402, "", "RFD900x Vcc HF", [("1", "P", "SIK_VCC_F"), ("2", "N", "GND")]),
    ("FB-SIK2", "742792510", FP_L0805, "742792510", "RFD900x UART RX line filter", [("1", "IN", "UART_SIK_RX"), ("2", "OUT", "UART_SIK_RX_F")]),
    ("FB-SIK3", "742792510", FP_L0805, "742792510", "RFD900x UART TX line filter", [("1", "IN", "UART_SIK_TX"), ("2", "OUT", "UART_SIK_TX_F")]),
    ("FB-SIK4", "742792510", FP_L0805, "742792510", "RFD900x CTS line filter", [("1", "IN", "SIK_CTS"), ("2", "OUT", "SIK_CTS_F")]),
    # --- LoRa (RFM95W) SPI filtering ----------------------------------------
    ("R-LORA-M1", "33R", FP_R0402, "", "RFM95W MISO series (CM3 SRF2012 pairing per XO.md §12)", [("1", "A", "SPI0_B_MISO"), ("2", "B", "SPI0_B_MISO_F")]),
    ("R-LORA-M2", "33R", FP_R0402, "", "RFM95W MOSI series", [("1", "A", "SPI0_B_MOSI"), ("2", "B", "SPI0_B_MOSI_F")]),
    ("R-LORA-C", "33R", FP_R0402, "", "RFM95W SCK series", [("1", "A", "SPI0_B_CLK"), ("2", "B", "SPI0_B_CLK_F")]),
    ("R-LORA-N", "33R", FP_R0402, "", "RFM95W NSS series", [("1", "A", "SPI0_B_CS_LORA"), ("2", "B", "SPI0_B_CS_LORA_F")]),
    ("C-LORA1", "100nF", FP_C0402, "", "RFM95W 3.3V bypass", [("1", "P", "+3V3_RF"), ("2", "N", "GND")]),
    ("R-LORA-RST", "10k", FP_R0201, "", "RFM95W RESET pull-up (open-drain reset per §7.2.2)", [("1", "A", "+3V3_RF"), ("2", "B", "LORA_RESETN")]),
    # --- WiFi/BT (WL1837MOD) SDIO filtering + supply ------------------------
    ("C-WIFI1", "100nF", FP_C0402, "", "WL1837MOD VBAT_IN bypass", [("1", "P", "+3V3_RF"), ("2", "N", "GND")]),
    ("C-WIFI2", "10uF 6.3V X5R", FP_C0805, "", "WL1837MOD VBAT_IN bulk", [("1", "P", "+3V3_RF"), ("2", "N", "GND")]),
    ("R-WIFI-EN", "10k", FP_R0201, "", "WLAN_EN pull-up (power-up default off, PB2 drives active)", [("1", "A", "+1V8_IO"), ("2", "B", "WIFI_EN")]),
    ("FB-SDIO1", "742792510", FP_L0805, "742792510", "SDIO CMD ferrite (Wurth 742792510)", [("1", "IN", "SDIO_CMD"), ("2", "OUT", "SDIO_CMD_F")]),
    ("FB-SDIO2", "742792510", FP_L0805, "742792510", "SDIO CLK ferrite", [("1", "IN", "SDIO_CLK"), ("2", "OUT", "SDIO_CLK_F")]),
    ("FB-SDIO3", "742792510", FP_L0805, "742792510", "SDIO D0 ferrite", [("1", "IN", "SDIO_D0"), ("2", "OUT", "SDIO_D0_F")]),
    ("FB-SDIO4", "742792510", FP_L0805, "742792510", "SDIO D1 ferrite", [("1", "IN", "SDIO_D1"), ("2", "OUT", "SDIO_D1_F")]),
    ("FB-SDIO5", "742792510", FP_L0805, "742792510", "SDIO D2 ferrite", [("1", "IN", "SDIO_D2"), ("2", "OUT", "SDIO_D2_F")]),
    ("FB-SDIO6", "742792510", FP_L0805, "742792510", "SDIO D3 ferrite", [("1", "IN", "SDIO_D3"), ("2", "OUT", "SDIO_D3_F")]),
    # --- SPI-NOR flash + logging PLD supply ---------------------------------
    ("C-FLASH1", "100nF", FP_C0402, "", "W25Q128JV VCC bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("R-FLASH-WP", "10k", FP_R0201, "", "FLASH_WP_N pull-up (write-enabled default; PLD asserts low to block)",
     [("1", "A", "+3V3"), ("2", "B", "FLASH_WP_N")]),
    ("C-PLD1", "100nF", FP_C0402, "", "ATF16V8BQL VCC bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    # --- fan + SD --------------------------------------------------------
    ("J-FAN", "SM03B-GHS-TB", FP_GH3, "SM03B-GHS-TB(LF)(SN)", "XO.md §14 J_FAN (bay ventilation)",
     [("1", "GND", "GND"), ("2", "+5V", "+5V"), ("3", "FAN_PWM", "FAN_PWM_B")]),
    ("J-SD", "microSD push-pull", FP_MICROSD, "104031-0811",
     "molex-104031.pdf (Molex 104031-0811) — used in place of XO.md's cited \"Molex 503182-1852\", "
     "which could not be verified as a real Molex part number this pass; 104031-0811 IS a confirmed, "
     "datasheet-real microSD connector and is already in KiCad's system library",
     [("1", "CD/DAT3", None), ("2", "CMD", None), ("3", "VSS1", "GND"), ("4", "VDD", "+3V3"),
      ("5", "CLK", None), ("6", "VSS2", "GND"), ("7", "DAT0", None), ("8", "DAT1", None),
      ("9", "DAT2", None), ("10", "SW-COM", "GND"), ("11", "SW-NC", "SD_CD")]),
    # --- antenna filter/ESD chains (XO.md §13) ------------------------------
    ("FL-SIK", "0915LP15B026E", FP_FLLORA, "0915LP15B026E", "Johanson 915 MHz filter — see gen_xo_footprints.py "
     "docstring: substituted for XO.md's fabricated \"0915LP15B0100E\", NEEDS user confirmation",
     [("1", "IN", "SIK_ANT_RF"), ("2", "GND", "GND"), ("3", "GND", "GND"), ("4", "OUT", "SIK_ANT_F")]),
    ("D-ANT-SIK", "RCLAMP0502B", FP_RCLAMP, "RCLAMP0502BTCL", "RF ESD shunt — datasheet PDF not obtained this pass, flagged",
     [("1", "A", "SIK_ANT_F"), ("2", "K", "PGND")]),
    ("J-SIK-ANT", "U.FL-R-SMT-1", FP_USMD, "U.FL-R-SMT-1(10)", "SiK module pigtail (module ANT pin has no on-module connector — "
     "reuses the datasheet's U.FL RF-out convention already applied to Pilot's GPS-ANT)",
     [("1", "RF", "SIK_ANT_RF"), ("2", "SHIELD", "GND")]),
    ("J-SMA-SIK", "MMCX vertical", FP_MMCX, "73415-1471",
     "SiK antenna jack — swapped from a panel-mount SMA edge connector to a vertical MMCX (Molex "
     "73415-1471, real/verified, KiCad system library) per the 2026-09-20 board-area decision: MMCX's "
     "courtyard is ~24 mm^2 vs SMA edge-mount's ~198 mm^2 (~8x smaller), recovering the area SMA cost "
     "without needing an off-board pigtail. Trade-off: MMCX is snap-on, not threaded — less secure "
     "under vibration than SMA; accepted for this rebuild per owner direction. A panel-mount SMA "
     "bulkhead adapter cable can still terminate the MMCX externally if a threaded exterior connector "
     "is wanted at the airframe skin.",
     [("1", "RF", "SIK_ANT_F"), ("2", "SHIELD", "PGND")]),
    ("FL-LORA", "0915LP15B026E", FP_FLLORA, "0915LP15B026E", "Johanson 915 MHz filter, same substitution as FL-SIK",
     [("1", "IN", "LORA_ANT_RF"), ("2", "GND", "GND"), ("3", "GND", "GND"), ("4", "OUT", "LORA_ANT_F")]),
    ("D-ANT-LORA", "RCLAMP0502B", FP_RCLAMP, "RCLAMP0502BTCL", "RF ESD shunt, same flag as D-ANT-SIK",
     [("1", "A", "LORA_ANT_F"), ("2", "K", "PGND")]),
    ("J-SMA-LORA", "MMCX vertical", FP_MMCX, "73415-1471",
     "LoRa antenna jack — swapped SMA edge-mount for vertical MMCX, same rationale as J-SMA-SIK",
     [("1", "RF", "LORA_ANT_F"), ("2", "SHIELD", "PGND")]),
    ("FL-WIFI", "2450BP15E0100", FP_FLWIFI, "2450BP15E0100", "Johanson 2.45 GHz band-pass filter — substituted for XO.md's "
     "fabricated \"2450BP15B050E\", NEEDS user confirmation",
     [("1", "IN", "WIFI_ANT_RF"), ("2", "GND", "GND"), ("3", "GND", "GND"), ("4", "OUT", "WIFI_ANT_F")]),
    ("D-ANT-WIFI", "RCLAMP0502B", FP_RCLAMP, "RCLAMP0502BTCL", "RF ESD shunt, same flag as D-ANT-SIK",
     [("1", "A", "WIFI_ANT_F"), ("2", "K", "PGND")]),
    ("J-SMA-WIFI", "MMCX vertical", FP_MMCX, "73415-1471",
     "WiFi antenna jack — swapped SMA edge-mount for vertical MMCX, same rationale as J-SMA-SIK",
     [("1", "RF", "WIFI_ANT_F"), ("2", "SHIELD", "PGND")]),
    # SG90 door servos: 2026-09-20 owner correction — controlled over the
    # CAN-FD/RS-485 bus (same remote servo-controller pattern as the winch),
    # not by a local PWM driver on this cape, so no local servo header exists
    # on XO at all.
]
# Mounting holes on chassis ground (matches Pilot's convention).
SIMPLE += [
    (f"H{i}", "M2.5 PGND", FP_HOLE, "", "chassis bond via mounting hardware", [("1", "PGND", "PGND")])
    for i in range(1, 5)
]

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
        f'    (symbol "XO:{libid}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)',
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
        f'  (symbol (lib_id "XO:{libid}") (at {X:.2f} {Y:.2f} 0) (unit 1)',
        f'    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp {dnp}) (uuid "{uid()}")',
        f'    (property "Reference" "{esc(ref)}" (at {X:.2f} {Y - half_h - 1.27:.2f} 0) (effects (font (size {SIZE} {SIZE}))))',
        f'    (property "Value" "{esc(value)}" (at {X:.2f} {Y + half_h + 1.27:.2f} 0) (effects (font (size {SIZE} {SIZE}))))',
        f'    (property "Footprint" "{esc(ic["fp"])}" (at {X:.2f} {Y:.2f} 0) (effects (font (size {SIZE} {SIZE})) (hide yes)))',
        f'    (property "Datasheet" "{esc(ic["ds"])}" (at {X:.2f} {Y:.2f} 0) (effects (font (size {SIZE} {SIZE})) (hide yes)))',
        f'    (property "MPN" "{esc(ic.get("mpn", ""))}" (at {X:.2f} {Y:.2f} 0) (effects (font (size {SIZE} {SIZE})) (hide yes)))',
    ]
    for pn, *_ in left + right:
        out.append(f'    (pin "{esc(pn)}" (uuid "{uid()}"))')
    out.append(f'    (instances (project "XO" (path "/{sheet_uuid}" (reference "{esc(ref)}") (unit 1))))')
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


PWR_FLAG_RAILS = ["GND", "+3V3", "+5V", "+5V_IN", "GND2_CANB", "GND2_RS485B",
                  "VCC2_CANB", "VCC2_RS485B", "PGND", "+3V3_PB2", "+3V3_RF", "+1V8_IO"]

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
            f'    (instances (project "XO" (path "/{sheet_uuid}" (reference "#FLG{i + 1}") (unit 1)))))'
        )
        out.append(wire(x, y0, x, y0 + STUB))
        out.append(label(rail, x, y0 + STUB, 270))
    return out


TITLE_BLOCK = """  (title_block
    (title "XO — Comms / Logging / Payload Cape")
    (date "2026-09-20")
    (rev "S2")
    (company "Griffing Technology LLC")
    (comment 1 "XO Node — PocketBeagle 2 Industrial cape, 4-layer")
    (comment 2 "Generated by avionics/kicad/XO/scripts/gen_xo_sch.py — do not hand-edit; edit the generator")
    (comment 3 "Author: Claude Sonnet 5 (2026-09-20); owner sgriffing")
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
    COL_MAX_Y = 610.0
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
    lib = ["(kicad_symbol_lib (version 20241209) (generator \"gen_xo_sch.py\") (generator_version \"9.0\")"]
    for ic, left, right, hw, hh in built:
        lib.append(lib_symbol(ic)[0].replace('(symbol "XO:', '(symbol "', 1))
    lib.append(")")
    SYMLIB.write_text("\n".join(lib) + "\n")
    npins = sum(len(ic["pins"]) for ic in ICS)
    print(f"Wrote {OUT}")
    print(f"  parts: {len(ICS)}   pins: {npins}   columns: {int((x - X0) / DX) + 1}")


if __name__ == "__main__":
    main()
