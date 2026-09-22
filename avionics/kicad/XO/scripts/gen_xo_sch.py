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
* **XO-unique (new this pass):** Seeed Wio-E5 module running mLRS firmware
  (wio-e5-datasheet.pdf — replaces RFD900x SiK, relocated to Commo; see the
  2026-09-21 SiK-swap note below), Murata Type 2EL WiFi+BT+802.15.4 tri-radio
  module (type2el.pdf — see the 2026-09-21 swap note below), TPS63031
  buck-boost for the RF 3V3 rail (tps63031.pdf), W25Q128JV SPI NOR flash
  (w25q128jv.pdf), DRV8833 winch H-bridge driver (drv8833.pdf), HX711
  load-cell ADC (hx711.pdf), PCA9685 PWM/I2C driver (pca9685.pdf), ATF16V8BQL
  PLD used as a logging write-block interlock (atf16v8bql.pdf — the JEDEC
  fuse map/logic equations are a firmware deliverable, out of scope here;
  every pin is wired to a real net so the schematic is ERC-complete), antenna
  filter/ESD chains, microSD card slot, fan connector.
* **2026-09-21 — SiK (RFD900ux-SMT) relocated to Commo, replaced by mLRS on a
  Seeed Wio-E5 module:** per owner direction (via `ce-ideate` footprint/power/
  firmware analysis, see avionics/WBS.md's "APPROVED DIRECTION" entry), XO's
  own long-range link becomes mLRS running on STM32WLE5JC (LoRa radio
  integrated in the die — no separate MCU+radio-chip subsystem). Every net on
  the WIOE5 IC entry below is transcribed directly from mLRS's own published
  HAL source for this hardware target (`rx-hal-WioE5-Mini-wle5jc.h`), not
  guessed. This does NOT re-collapse the path-diversity argument that killed
  the earlier mLRS-for-SiK proposal (avionics/WBS.md's original mLRS
  rejection): that rejection assumed XO would carry SiK AND a LoRa-family
  radio in parallel; here SiK leaves XO entirely, so the fleet still ends up
  with one SiK-class link (now on Commo) and one LoRa-class link (now on XO)
  — same two-family split as before, different physical boards.
* **2026-09-21 — WL1837MOD (WiFi+BT) + the never-implemented Zigbee scope gap
  both replaced/closed by one part:** Murata Type 2EL (LBES5PL2EL-923,
  type2el.pdf) is an NXP IW612-based module that combines WiFi 802.11a/b/g/n/
  ac/ax + Bluetooth 5.4 + IEEE 802.15.4 in one 8.8x7.7x1.3mm LGA — one module
  now covers what would otherwise need two distinct subsystems (a WiFi/BT
  module plus a separate 802.15.4/Zigbee radio the WBS previously flagged as
  never added). Wired in shared-antenna (SANT) mode per the datasheet's own
  Fig.1/Table 6/7 and the companion Unified Design Guide Rev.2.0 Fig.10 —
  one antenna feed for all three radios. See the WIFI-BT-ZB IC entry below
  for the full pin-by-pin rationale, including the AVDD18 high-current
  finding (needs a new dedicated buck, U-1V8RF — the existing WL1837MOD-era
  150mA LDO could not have supplied it) and the antenna matching-network
  disclosure (populated per vendor reference pattern: series 0R placeholder,
  both shunts DNP pending bench VSWR tuning against the real antenna).
  RF_CNTL0/1 outputs and several independent-reset/wake/PCM/JTAG-reserved
  pins are left NC, same disclosed-scope-calibration style WL1837MOD itself
  used.
* The confirmed-obsolete J_XCVR (49 MHz Commo cable) / SBUS blocks remain
  excluded.

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
  Wio-E5 wio-e5-datasheet.pdf V1.1 Table 1/§5.1 + mLRS rx-hal-WioE5-Mini-wle5jc.h
  (github.com/olliw42/mLRS) for pin function assignment |
  Type 2EL type2el.pdf Rev.18 + Unified Design Guide Rev.2.0 |
  TPS63031 tps63031.pdf Table (Pin Functions) |
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
# Real Würth 742792510 size per its own datasheet's SIZE/TYPE field is 1812
# (4.5x3.2mm), NOT 0402/0805 as earlier assumed — FP_L0805 was undersized for
# every ferrite bead using this MPN; corrected 2026-09-20.
FP_L1812 = "Inductor_SMD:L_1812_4532Metric"
# TPS63031's own datasheet (Table 3, §9.2.2.2) recommends Coilcraft LPS3015 /
# Murata LQH3NP / Taiyo Yuden NR3015 for the 2.2uH switching inductor —
# "744042002" (the MPN previously used here) could not be found as a real
# Würth part number anywhere and appears to have been fabricated during this
# rebuild; corrected to a real Coilcraft LPS3015 part. No exact Coilcraft
# LPS3015 KiCad footprint exists in the system libraries; the body-size-
# matched "L_Wuerth_MAPI-3015" 3015-family land is used as a stand-in,
# flagged as NOT pixel-verified against Coilcraft's own land drawing.
FP_L3015 = "Inductor_SMD:L_Wuerth_MAPI-3015"
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
FP_LED0603 = "LED_SMD:LED_0603_1608Metric"
FP_BOOTBTN = "Button_Switch_SMD:SW_Push_1P1T_NO_CK_PTS125Sx43PSMTR"
# project-custom lands (avionics/kicad/Serenity-Custom.pretty)
FP_PB2P1 = "Serenity-Custom:PocketBeagle2_2x18_P1_Socket"
FP_PB2P2 = "Serenity-Custom:PocketBeagle2_2x18_P2_Socket"
FP_NANOFIT = "Serenity-Custom:Molex_NanoFit_1x04_Horizontal"
FP_SRF2012 = "Serenity-Custom:Bourns_SRF2012_4T"
FP_X2Y0805 = "Serenity-Custom:X2Y_0805_4T"
FP_WELAN = "Serenity-Custom:Wurth_749010012A_WE-LAN"
FP_RFM95W = "Serenity-Custom:HopeRF_RFM95W_Castellated_16"
FP_TYPE2EL = "Serenity-Custom:Murata_Type2EL_LGA107"
FP_WIOE5 = "Serenity-Custom:Seeed_WioE5_QFN28"
FP_VSON10 = "Serenity-Custom:TPS6303x_VSON-10_2p5"
FP_FLLORA = "Serenity-Custom:Johanson_0915LP15B026E_SMD4"
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
        "ds": "tps63031.pdf Pin Functions (VSON-10 DSK) — dedicated buck-boost RF rail so "
              "WIFI-BT-ZB (AVDD33)/RFM95W/RFD900x RF supply stays regulated even if +5V sags "
              "(XO.md §12 power budget +3V3_RF 1.5A cont / 2.0A peak)",
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
        "ref": "U-1V8RF",
        "value": "TPS62933DRLR",
        "fp": "Package_TO_SOT_SMD:SOT-583-8",
        "mpn": "TPS62933DRLR",
        "ds": "tps62933.pdf Table 7-1 Pin Functions (SOT-583) [REF-PWR-001] — second instance of "
              "the same buck already used for U-3V3, refactored for a 1.8V output via the FB "
              "divider below. Added 2026-09-21 because WIFI-BT-ZB's AVDD18 draws up to 1009 mA "
              "peak (type2el.pdf §9.1) — the pre-existing 150 mA LDO (U-1V8, sized only for SDIO "
              "signaling level) could not supply this. Rather than run two separate 1.8V "
              "regulators, U-1V8 was removed entirely: SD_VIO is just 1.8V logic-level signaling "
              "(a few mA) at the same nominal voltage, so it shares THIS regulator's +1V8_RF "
              "output directly (own local bypass cap, same as any other rail pin) — one "
              "regulator for the whole 1.8V domain, less total footprint than two.",
        "pins": [
            ("3", "VIN", "+5V", "L"),
            ("2", "EN", "U1V8RF_EN", "L"),
            ("1", "RT", "GND", "L"),
            ("4", "GND", "GND", "L"),
            ("5", "SW", "SW_1V8RF", "R"),
            ("6", "BST", "BST_1V8RF", "R"),
            ("7", "SS/PG", "SS_1V8RF", "R"),
            ("8", "FB", "FB_1V8RF", "R"),
        ],
    },
    # SIK (RFD900ux-SMT) REMOVED 2026-09-21 per owner: relocated to Commo
    # (which has ~994 mm^2 of headroom against its own 4-layer ~70% ceiling,
    # confirmed via pcbnew against Commo's actual PCB, not estimated) in
    # exchange for Commo's LoRa (RFM95W) — see avionics/WBS.md's "APPROVED
    # DIRECTION" entry for the full footprint/power/firmware tradeoff
    # analysis (via ce-ideate). XO's own long-range link is replaced by
    # mLRS running on a Seeed Wio-E5 module (STM32WLE5JC, LoRa radio
    # integrated in the die) — chosen over a bare-LoRa+custom-firmware
    # approach (mLRS is the closest like-for-like replacement for what SiK
    # did: MAVLink-transparent telemetry + RC + frequency hopping) and over
    # a CH32V006-class tiny MCU (mLRS's firmware is confirmed ARM-only, no
    # RISC-V support at all — a hard architecture stop, not a size tradeoff).
    {
        "ref": "WIOE5",
        "value": "Wio-E5",
        "fp": FP_WIOE5,
        "mpn": "420J00019W",
        "ds": "wio-e5-datasheet.pdf V1.1 Table 1 (pinout), §5.1 (12x12x2.5mm package). Pin "
              "function/net assignment below is NOT guessed — it is transcribed directly from "
              "mLRS's own published receiver-role HAL source for this exact hardware target "
              "(github.com/olliw42/mLRS, mLRS/Common/hal/stm32/rx-hal-WioE5-Mini-wle5jc.h): "
              "UARTB=USART2 PA2(TX)/PA3(RX) is the host serial link (MAVLink-transparent, same "
              "role SiK's UART played); BUTTON/BOOT_BUTTON=PB13 (active-low, MCU's own internal "
              "pull-up, no external resistor needed — doubles as bind button in normal operation "
              "and a hold-at-power-on system-bootloader trigger); LED_GREEN=PA15 (active-high), "
              "LED_RED=PB5 (active-low); PB15 MUST be left floating per the HAL's own "
              "leds_init() comment (\"used as artificial pad for green LED\" on Seeed's reference "
              "layout — this is a from-scratch layout, so PB15 is simply left NC here). SX_RX_EN/"
              "SX_TX_EN (PA4/PA5 on the bare STM32WLE5) control the module's own internal RF "
              "switch and are NOT exposed on Wio-E5's 28-pin castellated interface at all (absent "
              "from the datasheet's own Table 1) — nothing to wire, handled inside the module. "
              "PA13/PA14 (SWDIO/SWCLK) exposed to a debug header: these modules ship from Seeed "
              "with their OWN AT-command firmware and MUST be reflashed with mLRS firmware before "
              "first use. PB6/PB7 (UART1, mLRS's secondary debug/bootloader-fallback port) and "
              "PC0/PC1 (LPUART1 'OUT' port, SBus-style — not needed for MAVLink telemetry) are "
              "left NC: SWD is the chosen programming path, disclosed scope calibration. PA0, "
              "PB3, PB4, PB9, PB10, PB14, PA9, PA10, PB0 are confirmed UNUSED by mLRS's own "
              "Rx-Mini HAL for this target (grepped the actual firmware source, not assumed) — "
              "left NC; PB0 additionally carries the datasheet's own \"must be left floating, "
              "not allowed to be pulled up or grounded\" note.",
        "pins": [
            ("1", "VCC", "+3V3_RF", "L"),
            ("2", "GND", "GND", "L"),
            ("3", "PA13", "WIOE5_SWDIO", "L"),
            ("4", "PA14", "WIOE5_SWCLK", "L"),
            ("5", "PB15", None, "L"),
            ("6", "PA15", "WIOE5_LED_G", "L"),
            ("7", "PB4", None, "L"),
            ("8", "PB3", None, "L"),
            ("9", "PB7", None, "L"),
            ("10", "PB6", None, "L"),
            ("11", "PB5", "WIOE5_LED_R", "L"),
            ("12", "PC1", None, "L"),
            ("13", "PC0", None, "L"),
            ("14", "GND", "GND", "L"),
            ("15", "RFIO", "WIOE5_ANT_RF", "R"),
            ("16", "GND", "GND", "R"),
            ("17", "RST", "WIOE5_RST", "R"),
            ("18", "PA3", "UART_WIOE5_RX_F", "R"),
            ("19", "PA2", "UART_WIOE5_TX_F", "R"),
            ("20", "PB10", None, "R"),
            ("21", "PA9", None, "R"),
            ("22", "GND", "GND", "R"),
            ("23", "PA0", None, "R"),
            ("24", "PB13", "WIOE5_BOOT_BTN", "R"),
            ("25", "PB9", None, "R"),
            ("26", "PB14", None, "R"),
            ("27", "PA10", None, "R"),
            ("28", "PB0", None, "R"),
            ("29", "PAD_GND", "GND", "R"),
        ],
    },
    # LORA (RFM95W) REMOVED 2026-09-20 per owner: Commo already carries a
    # LoRa radio, so XO's own LoRa was fleet-level DUPLICATE capability, not
    # a unique function — removing it is de-duplication, not a capability
    # loss (unlike the earlier area-crisis "cut a subsystem" options, which
    # would have actually removed a function nothing else on the fleet
    # covers). Recovers ~292 mm^2 (module body) plus its SPI series
    # resistors, bypass cap, reset pull-up, antenna filter/ESD/MMCX chain —
    # the single largest lever available once RFD900ux-SMT's flush-mount
    # area correction pushed XO to 99.6% of its two-sided theoretical
    # ceiling. SiK (915 MHz self-contained mesh telemetry) and WiFi/BT stay;
    # neither duplicates a function Commo already provides.
    # WL1837MOD (WiFi+BT) REMOVED 2026-09-21 per owner: replaced by Murata
    # Type 2EL (LBES5PL2EL-923, type2el.pdf Rev.18 + the companion
    # "Type 2EL/2DL/2LL/2KL Unified Design Guide" Rev.2.0 app note, both in
    # avionics/datasheets/) — one NXP IW612-based module that ALSO adds
    # 802.15.4 (Zigbee/Thread PHY), which XO.md's own scope gap note flagged
    # as never having been implemented (no separate radio was ever added).
    # Net effect: one module replaces what would otherwise be TWO distinct
    # subsystems (WiFi/BT module + a hypothetical future 802.15.4 module,
    # each with its own antenna chain) — real board-area and BOM-count win,
    # not just a smaller WiFi/BT part. Single shared antenna (SANT mode,
    # ANT0 only) per the datasheet's Fig.1/Table 6 note that ANT1 must loop
    # back to BT_15.4_IN through an external 10pF cap in this mode (see
    # C-ANT-SANT below) — one antenna feed for all three radios instead of
    # (at minimum) two.
    {
        "ref": "WIFI-BT-ZB",
        "value": "LBES5PL2EL-923",
        "fp": FP_TYPE2EL,
        "mpn": "LBES5PL2EL-923",
        "ds": "type2el.pdf Rev.18 Table 6/7 (Terminal Configurations/Pin Descriptions), Table 8 "
              "(CONFIG_HOST straps), Fig.1 (shared-antenna block diagram); Unified Design Guide "
              "Rev.2.0 Fig.10 (SANT-mode ANT1<->BT_15.4_IN 10pF requirement). Murata NXP IW612 "
              "tri-radio SMD LGA, 8.8x7.7x1.3mm. AVDD18 needs up to 1009 mA peak / ~392-550 mA "
              "typ Tx (type2el.pdf §9.1/§12.18 DC characteristics) — this is FAR beyond the "
              "pre-existing 150 mA LDO's (U-1V8, sized only for WL1837MOD's SDIO signaling level, "
              "a few mA) rating; a new dedicated high-current 1.8V buck (U-1V8RF below) supplies "
              "AVDD18. U-1V8 itself was REMOVED (not kept) — SD_VIO shares U-1V8RF's +1V8_RF "
              "output directly rather than running two separate 1.8V regulators, since SD_VIO is "
              "just low-current logic-level signaling at the same nominal voltage. Scope calibration, "
              "disclosed (same pattern as WL1837MOD's own disclosed ball-population choice): "
              "PCM audio (pins 57-61), Bluetooth/WLAN/802.15.4 independent-reset and wake pins "
              "(37,38,63,64,73-76), JTAG-reserved pins (33-36), WCI-2 coexistence (69,70), and "
              "RF_CNTL1/0 (26,27, outputs, reserved) are left NC — none are needed for basic "
              "SDIO WiFi + UART Bluetooth + SPI 802.15.4 host operation, and the datasheet's own "
              "I/O state table (Table 9) shows each has a defined internal pull, so floating is a "
              "documented-safe default, not an unverified guess.",
        "pins": [
            ("1", "GND", "GND", "L"),
            ("2", "GND", "GND", "L"),
            ("4", "SPI_FRM", "SPI0_B_CS_ZB", "L"),
            ("5", "SPI_INT", "ZB_SPI_INT", "L"),
            ("6", "SPI_RXD", "SPI0_B_MISO", "L"),
            ("7", "SPI_TXD", "SPI0_B_MOSI", "L"),
            ("8", "SPI_CLK", "SPI0_B_CLK", "L"),
            ("9", "GND", "GND", "L"),
            ("10", "PDn", "WIFI_EN", "L"),
            ("11", "GND", "GND", "L"),
            ("12", "AVDD33_1", "+3V3_RF", "L"),
            ("13", "AVDD33_2", "+3V3_RF", "L"),
            ("14", "GND", "GND", "L"),
            ("15", "ANT0", "RADIO_ANT_RF", "L"),
            ("16", "GND", "GND", "L"),
            ("17", "GND", "GND", "L"),
            ("18", "BT_15.4_IN", "RADIO_ANT1_IN", "L"),
            ("19", "GND", "GND", "L"),
            ("20", "GND", "GND", "L"),
            ("21", "GND", "GND", "L"),
            ("22", "GND", "GND", "L"),
            ("23", "ANT1", "RADIO_ANT1_OUT", "L"),
            ("24", "RF_CNTL4", "+3V3", "L"),
            ("25", "RF_CNTL3/CONFIG_XOSC_SEL", "+3V3", "L"),
            ("26", "RF_CNTL1", None, "L"),
            ("27", "RF_CNTL0", None, "L"),
            ("28", "GND", "GND", "L"),
            ("29", "GND", "GND", "L"),
            ("30", "AVDD18_2", "+1V8_RF", "L"),
            ("31", "AVDD18_1", "+1V8_RF", "L"),
            ("32", "GND", "GND", "L"),
            ("33", "Reserved/JTAG_TDO", None, "R"),
            ("34", "Reserved/JTAG_TMS", None, "R"),
            ("35", "Reserved/JTAG_TCK", None, "R"),
            ("36", "Reserved/JTAG_TDI", None, "R"),
            ("37", "RST_IND", None, "R"),
            ("38", "IND_RST_15.4", None, "R"),
            ("39", "GND", "GND", "R"),
            ("40", "SD_VIO", "+1V8_RF", "R"),
            ("41", "GND", "GND", "R"),
            ("42", "SD_CMD", "SDIO_CMD_F", "R"),
            ("43", "GND", "GND", "R"),
            ("44", "SD_CLK", "SDIO_CLK_F", "R"),
            ("45", "SD_DAT1", "SDIO_D1_F", "R"),
            ("46", "SD_DAT3", "SDIO_D3_F", "R"),
            ("47", "SD_DAT2", "SDIO_D2_F", "R"),
            ("48", "SD_DAT0", "SDIO_D0_F", "R"),
            ("49", "UART_TX", "BT_UART_TX", "R"),
            ("50", "UART_CTS", "BT_UART_CTS", "R"),
            ("51", "UART_RX", "BT_UART_RX", "R"),
            ("52", "UART_RTS", "BT_UART_RTS", "R"),
            ("53", "GND", "GND", "R"),
            ("54", "VIO", "+3V3", "R"),
            ("55", "CONFIG_HOST[0]", "+3V3", "R"),
            ("56", "CONFIG_HOST[1]", "+3V3", "R"),
            ("57", "PCM_CLK", None, "R"),
            ("58", "PCM_MCLK", None, "R"),
            ("59", "PCM_DOUT", None, "R"),
            ("60", "PCM_DIN", None, "R"),
            ("61", "PCM_SYNC", None, "R"),
            ("62", "GND", "GND", "R"),
            ("63", "IND_RST_WL", None, "R"),
            ("64", "IND_RST_BT", None, "R"),
            ("65", "Reserved", None, "R"),
            ("66", "Reserved", None, "R"),
            ("67", "GND", "GND", "R"),
            ("68", "GND", "GND", "R"),
            ("69", "WCI-2_SIN", None, "R"),
            ("70", "WCI-2_SOUT", None, "R"),
            ("71", "GND", "GND", "R"),
            ("72", "SD_INT", "WIFI_IRQ", "R"),
            ("73", "WL_WAKE_OUT", None, "R"),
            ("74", "WL_WAKE_IN", None, "R"),
            ("75", "BT15.4_WAKE_IN", None, "R"),
            ("76", "BT15.4_WAKE_OUT", None, "R"),
            ("77", "NC", None, "R"),
            ("78", "NC", None, "R"),
            ("79", "NC", None, "R"),
            ("80", "NC", None, "R"),
        ] + [(str(n), "GND", "GND", "L" if n % 2 else "R") for n in range(81, 108)],
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
    # Indices 2-5 (was WINCH_IN1-4, freed 2026-09-20) now carry the
    # Bluetooth UART for WIFI-BT-ZB (Murata Type 2EL) — a second, dedicated
    # UART bus, distinct from SiK's UART_SIK_RX/TX pair below.
    "GND", "GND", "BT_UART_TX", "BT_UART_RX", "BT_UART_RTS", "BT_UART_CTS",
    "PRU_1553B_RX_N", "PRU_1553B_RX_P", "PRU_1553B_TX_N", "PRU_1553B_TX_P",
    "RS485_B_DE", "RS485_B_RX", "RS485_B_TX", "CAN_B_STB", "MCAN0_B_RX", "MCAN0_B_TX",
    "SD_CD", None, None, "M1553B_TX_INH", "SPI0_B_CS_TPM",
    "SPI0_B_CS_FLASH", "SPI0_B_MISO", "SPI0_B_MOSI", "SPI0_B_CLK",
    "SPI0_B_CS_ZB",  # was SPI0_B_CS_LORA (freed 2026-09-20); reused 2026-09-21
                     # for WIFI-BT-ZB's 802.15.4 SPI_FRM (shares the SPI0_B
                     # MISO/MOSI/CLK bus with TPM/flash via its own CS, same
                     # multi-drop pattern already used for those two).
    "ZB_SPI_INT", None, None, None, "UART_WIOE5_RX",  # was UART_SIK_RX, reused 2026-09-21
    "UART_WIOE5_TX", "+3V3_PB2", "+3V3_PB2", "+5V", "GND",  # was UART_SIK_TX
]
PB2_P2 = [
    # index 27 (was LORA_DIO0) freed 2026-09-20 when RFM95W/LORA was removed
    # (duplicate of Commo's LoRa radio) -- left None rather than reassigned.
    # indices 2-3 (were SIK_CTS/SIK_RTS) freed 2026-09-21: Wio-E5's mLRS UART
    # (UARTB=USART2) carries no RTS/CTS flow control per mLRS's own HAL
    # source for this target -- left None rather than reassigned.
    "SDIO_D2", "SDIO_D3", None, None, "FAN_PWM_B", "PLD_CLK", "PLD_I1", "PLD_I2",
    "WIFI_EN", "WIFI_IRQ", "TPM_B_RSTN", "TPM_B_IRQN",
    "PLD_I3", "PLD_I4", "PHY1_RSTN", "PHY1_INTRN", "MDIO0", "MDC0",
    "SDIO_CLK", "SDIO_CMD", "SDIO_D0", "SDIO_D1",
    "PLD_I5", "PLD_I6", "PLD_I7", "PLD_I8",
    None, "RMII0_RX_ER", "RMII0_CRS_DV", "RMII0_RXD1",
    "RMII0_RXD0", "RMII0_TX_EN", "RMII0_TXD1", "RMII0_TXD0", "+5V", "GND",
]


def pb2_header(ref: str, value: str, fp: str, nets: List[Optional[str]]) -> Dict[str, Any]:
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
    ("FB1", "742792510", FP_L1812, "742792510", "wurth-742792510.pdf 1812 ferrite bead (SIZE/TYPE field, "
     "corrected 2026-09-20 from an earlier wrong 0402/0805 assumption); XO §12 power "
     "budget draws 3.0A +5V so a HIGHER-current bead than Pilot's 742792512 (2A) is required here",
     [("1", "IN", "+5V_IN"), ("2", "OUT", "+5V")]),
    ("C-IN1", "47uF 10V X5R", FP_C1210, "", "XO.md §6 input bulk", [("1", "P", "+5V_IN"), ("2", "N", "GND")]),
    ("C-IN2", "10uF 10V X5R", FP_C0603, "", "XO.md §6 filtered bulk", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-IN3", "100nF", FP_C0402, "", "XO.md §6 HF bypass", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("R-PGND", "0R", FP_R0805, "", "XO.md §7 single-point GND<->PGND link", [("1", "A", "GND"), ("2", "B", "PGND")]),
    # --- +3V3 logic buck (TPS62933) ------------------------------------------
    ("R-EN3", "100k", FP_R0201, "", "TPS62933 EN pull-up to VIN", [("1", "A", "+5V"), ("2", "B", "U3V3_EN")]),
    ("C-3V3-IN", "10uF 10V X5R", FP_C0603, "", "TPS62933 CIN at VIN/GND", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-3V3-HF", "100nF", FP_C0402, "", "TPS62933 CIN HF", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-BST", "100nF", FP_C0402, "", "TPS62933 BST-SW bootstrap", [("1", "P", "BST_3V3"), ("2", "N", "SW_3V3")]),
    ("C-SS", "10nF", FP_C0201, "", "TPS62933 soft-start", [("1", "P", "SS_3V3"), ("2", "N", "GND")]),
    ("L-3V3", "3.3uH 2.25A", "Serenity-Custom:L_WE-MAPI_3015", "74438335033", "TPS62933 inductor, WE-MAPI 3015 (same custom land as Pilot L-3V3) [REF-PWR-003]",
     [("1", "A", "SW_3V3"), ("2", "B", "+3V3")]),
    ("R-FB3H", "100k 1%", FP_R0201, "", "TPS62933 FB divider top", [("1", "A", "+3V3"), ("2", "B", "FB_3V3")]),
    ("R-FB3L", "32.4k 1%", FP_R0201, "", "TPS62933 FB divider bottom (3.27 V)", [("1", "A", "FB_3V3"), ("2", "B", "GND")]),
    ("C-3V3-O1", "22uF 6.3V X5R", FP_C0603, "", "TPS62933 COUT", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-3V3-O2", "22uF 6.3V X5R", FP_C0603, "", "TPS62933 COUT", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    # --- +1V8_RF high-current buck (TPS62933, 2nd instance) — WIFI-BT-ZB AVDD18
    # + SD_VIO (added 2026-09-21, replacing the removed 150mA U-1V8 LDO; see
    # U-1V8RF's own docstring above for the one-regulator-not-two rationale)
    ("R-EN18", "100k", FP_R0201, "", "U-1V8RF EN pull-up to VIN", [("1", "A", "+5V"), ("2", "B", "U1V8RF_EN")]),
    ("C-1V8RF-IN", "10uF 10V X5R", FP_C0603, "", "U-1V8RF CIN at VIN/GND", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-1V8RF-HF", "100nF", FP_C0402, "", "U-1V8RF CIN HF", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-BST18", "100nF", FP_C0402, "", "U-1V8RF BST-SW bootstrap", [("1", "P", "BST_1V8RF"), ("2", "N", "SW_1V8RF")]),
    ("C-SS18", "10nF", FP_C0201, "", "U-1V8RF soft-start", [("1", "P", "SS_1V8RF"), ("2", "N", "GND")]),
    ("L-1V8RF", "3.3uH 2.25A", "Serenity-Custom:L_WE-MAPI_3015", "74438335033", "U-1V8RF inductor, same WE-MAPI 3015 part/land as L-3V3",
     [("1", "A", "SW_1V8RF"), ("2", "B", "+1V8_RF")]),
    ("R-FB18H", "40.2k 1%", FP_R0201, "", "U-1V8RF FB divider top (Vfb=0.8V -> 1.79V; 0.8*(1+40.2/32.4))", [("1", "A", "+1V8_RF"), ("2", "B", "FB_1V8RF")]),
    ("R-FB18L", "32.4k 1%", FP_R0201, "", "U-1V8RF FB divider bottom", [("1", "A", "FB_1V8RF"), ("2", "B", "GND")]),
    ("C-1V8RF-O1", "22uF 6.3V X5R", FP_C0603, "", "U-1V8RF COUT", [("1", "P", "+1V8_RF"), ("2", "N", "GND")]),
    ("C-1V8RF-O2", "22uF 6.3V X5R", FP_C0603, "", "U-1V8RF COUT", [("1", "P", "+1V8_RF"), ("2", "N", "GND")]),
    # --- +3V3_RF buck-boost (TPS63031) --------------------------------------
    ("L-RF1", "2.2uH 3A", FP_L3015, "LPS3015-222MRC", "TPS63031 first inductor leg; tps63031.pdf Table 3 "
     "recommends Coilcraft LPS3015/Murata LQH3NP/Taiyo Yuden NR3015 — \"744042002\" (used here previously) "
     "could not be found as a real Wurth part and appears fabricated during this rebuild, corrected "
     "2026-09-20 to a real Coilcraft LPS3015 part",
     [("1", "A", "RF_SW1"), ("2", "B", "+5V")]),
    ("L-RF2", "2.2uH 3A", FP_L3015, "LPS3015-222MRC", "TPS63031 second inductor leg, same correction as L-RF1",
     [("1", "A", "RF_SW2"), ("2", "B", "+3V3_RF")]),
    ("C-RF-IN1", "10uF 10V X5R", FP_C0603, "", "TPS63031 VIN bulk", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-RF-IN2", "100nF", FP_C0402, "", "TPS63031 VIN HF", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-RF-O1", "22uF 6.3V X5R", FP_C0603, "", "TPS63031 COUT", [("1", "P", "+3V3_RF"), ("2", "N", "GND")]),
    ("C-RF-O2", "22uF 6.3V X5R", FP_C0603, "", "TPS63031 COUT", [("1", "P", "+3V3_RF"), ("2", "N", "GND")]),
    # U-1V8 (TLV75718 150mA LDO, WL1837MOD-era dedicated SDIO/VIO-level rail)
    # REMOVED 2026-09-21 per owner question: since U-1V8RF (below) already
    # exists as a real high-current 1.8V buck for AVDD18, and SD_VIO is just
    # 1.8V logic-level signaling (a few mA) at the SAME nominal voltage, a
    # second dedicated LDO for SD_VIO alone is unnecessary board area — SD_VIO
    # now shares U-1V8RF's +1V8_RF output directly (own local 100nF bypass,
    # C-ZB-SDVIO, same as any other rail pin). One regulator, not two, for the
    # whole 1.8V domain. (A separate, low-noise LDO for the two 1.8V rails
    # would be the standard move IF SD_VIO's signal integrity were sensitive
    # to the buck's switching ripple — but SD_VIO is logic-level SDIO
    # signaling, not an analog/RF reference, so sharing is the right call
    # here.)
    # --- CAN FD field port ---------------------------------------------------
    ("C-CAN1", "10nF", FP_C0201, "", "ISOW1044 VDD HF bypass §13.1", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-CAN2", "10uF 10V X5R", FP_C0603, "", "ISOW1044 VDD bulk §13.1", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-CAN3", "100nF", FP_C0402, "", "ISOW1044 VIO bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-CAN4", "10nF", FP_C0201, "", "ISOW1044 VISOOUT HF bypass", [("1", "P", "VCC2_CANB"), ("2", "N", "GND2_CANB")]),
    ("C-CAN5", "10uF 10V X5R", FP_C0603, "", "ISOW1044 VISOOUT bulk", [("1", "P", "VCC2_CANB"), ("2", "N", "GND2_CANB")]),
    ("C-CAN6", "100nF", FP_C0402, "", "ISOW1044 VISOIN bypass", [("1", "P", "VCC2_CANB"), ("2", "N", "GND2_CANB")]),
    ("CMC-CAN", "SRF2012-100Y", FP_SRF2012, "SRF2012-121YA", "SRF2012A.pdf windings 1-2 / 4-3 [REF-SENSOR-026]",
     [("1", "W1_IN", "CAN_B_H"), ("2", "W1_OUT", "CAN_B_H_F"), ("4", "W2_IN", "CAN_B_L"), ("3", "W2_OUT", "CAN_B_L_F")]),
    ("TVS-CAN", "PRTR5V0U2X", FP_SOT143, "PRTR5V0U2X,315", "prtr5v0u2x.pdf (Nexperia, SOT143B 4-pin) [REF-SENSOR-038]",
     [("1", "IO1", "CAN_B_H_F"), ("2", "GND", "GND2_CANB"), ("3", "IO2", "CAN_B_L_F"), ("4", "VCC", "VCC2_CANB")]),
    ("R-CANT", "120R", FP_R0402, "", "CAN bus termination — populate ONLY at a bus end node (DNP default); shrunk to 0402, DNP by default so no continuous-power concern",
     [("1", "A", "CAN_B_H_F"), ("2", "B", "CAN_B_L_F")], {"dnp": True}),
    ("J-CAN", "SM03B-GHS-TB", FP_GH3, "SM03B-GHS-TB(LF)(SN)", "XO.md §14 J_CAN",
     [("1", "CAN_H", "CAN_B_H_F"), ("2", "CAN_L", "CAN_B_L_F"), ("3", "GND", "GND2_CANB"), ("MP", "SHIELD", "PGND")]),
    ("X2Y-CAN", "4.7nF X2Y", FP_X2Y0805, "CX0805MRX7R0BB472", "GND1<->GND2 RF bridge (Yageo X2Y 0805)",
     [("1", "A", "GND"), ("2", "B", "GND"), ("3", "G1", "GND2_CANB"), ("4", "G2", "GND2_CANB")]),
    # --- RS-485 field port ---------------------------------------------------
    ("C-485-1", "10nF", FP_C0201, "", "ISOW1412 VDD HF bypass", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-485-2", "10uF 10V X5R", FP_C0603, "", "ISOW1412 VDD bulk", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-485-3", "100nF", FP_C0402, "", "ISOW1412 VIO bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-485-4", "10nF", FP_C0201, "", "ISOW1412 VISOOUT HF bypass", [("1", "P", "VCC2_RS485B"), ("2", "N", "GND2_RS485B")]),
    ("C-485-5", "10uF 10V X5R", FP_C0603, "", "ISOW1412 VISOOUT bulk", [("1", "P", "VCC2_RS485B"), ("2", "N", "GND2_RS485B")]),
    ("C-485-6", "100nF", FP_C0402, "", "ISOW1412 VISOIN bypass", [("1", "P", "VCC2_RS485B"), ("2", "N", "GND2_RS485B")]),
    ("CMC-RS485", "SRF2012-100Y", FP_SRF2012, "SRF2012-121YA", "SRF2012A.pdf windings 1-2 / 4-3 [REF-SENSOR-026]",
     [("1", "W1_IN", "RS485_B_A"), ("2", "W1_OUT", "RS485_B_A_F"), ("4", "W2_IN", "RS485_B_B"), ("3", "W2_OUT", "RS485_B_B_F")]),
    ("TVS-RS485", "PRTR5V0U2X", FP_SOT143, "PRTR5V0U2X,315", "prtr5v0u2x.pdf (Nexperia, SOT143B) [REF-SENSOR-038]",
     [("1", "IO1", "RS485_B_A_F"), ("2", "GND", "GND2_RS485B"), ("3", "IO2", "RS485_B_B_F"), ("4", "VCC", "VCC2_RS485B")]),
    ("R-485T", "120R", FP_R0402, "", "RS-485 termination — populate ONLY at a bus end node (DNP default); shrunk to 0402, DNP by default so no continuous-power concern",
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
    ("C-1553C", "10uF 6.3V X5R", FP_C0603, "", "HI-1573 transmitter bulk", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    # --- TPM ------------------------------------------------------------------
    ("C-TPM1", "1uF", FP_C0402, "", "SLB9672 §3.1.3 typical schematic bulk", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-TPM2", "100nF", FP_C0402, "", "SLB9672 VDD bypass (pin 1)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-TPM3", "100nF", FP_C0402, "", "SLB9672 VDD bypass (pin 14)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-TPM4", "100nF", FP_C0402, "", "SLB9672 VDD bypass (pin 22)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("R-TPMCS", "10k", FP_R0201, "", "SLB9672 CS# pull-up (§3.1.3)", [("1", "A", "+3V3"), ("2", "B", "SPI0_B_CS_TPM")]),
    ("R-TPM10", "10k", FP_R0201, "", "SLB9672 pin 10 NCI/VDD pull-up (Table 13, preferred)", [("1", "A", "+3V3"), ("2", "B", "TPM_B_P10_PU")]),
    # --- Wio-E5 (mLRS) supply/UART filtering + RST + boot/bind + LEDs -------
    ("C-WIOE5-IN", "4.7uF", FP_C0603, "", "Wio-E5 VCC bypass (wio-e5-datasheet.pdf Fig.12 reference design C1)", [("1", "P", "+3V3_RF"), ("2", "N", "GND")]),
    ("R-WIOE5-RST", "22k", FP_R0201, "", "Wio-E5 RST pull-up (Fig.12 reference design R1)", [("1", "A", "+3V3_RF"), ("2", "B", "WIOE5_RST")]),
    ("FB-WIOE5-1", "742792510", FP_L1812, "742792510", "Wio-E5 host UART RX line filter", [("1", "IN", "UART_WIOE5_RX"), ("2", "OUT", "UART_WIOE5_RX_F")]),
    ("FB-WIOE5-2", "742792510", FP_L1812, "742792510", "Wio-E5 host UART TX line filter", [("1", "IN", "UART_WIOE5_TX"), ("2", "OUT", "UART_WIOE5_TX_F")]),
    ("R-WIOE5-SWDIO", "22R", FP_R0201, "", "Wio-E5 SWDIO series (Fig.12 reference design R2)", [("1", "A", "WIOE5_SWDIO"), ("2", "B", "WIOE5_SWDIO_HDR")]),
    ("R-WIOE5-SWCLK", "22R", FP_R0201, "", "Wio-E5 SWCLK series (Fig.12 reference design R3)", [("1", "A", "WIOE5_SWCLK"), ("2", "B", "WIOE5_SWCLK_HDR")]),
    ("J-WIOE5-SWD", "SM04B-GHS-TB", FP_GH4, "SM04B-GHS-TB(LF)(SN)",
     "Wio-E5 SWD programming header — required since the module ships from Seeed with its own "
     "AT-command firmware and must be reflashed with mLRS firmware before first use",
     [("1", "VTREF", "+3V3_RF"), ("2", "SWDIO", "WIOE5_SWDIO_HDR"), ("3", "SWCLK", "WIOE5_SWCLK_HDR"), ("4", "GND", "GND")]),
    ("SW-WIOE5-BOOT", "PTS125Sx43", FP_BOOTBTN, "PTS125S43SMTR2LFS",
     "Wio-E5 bind/boot button (mLRS BUTTON=PB13, active-low, MCU's own internal pull-up per "
     "the HAL source — no external pull-up needed)",
     [("1", "A", "WIOE5_BOOT_BTN"), ("2", "B", "GND")]),
    ("R-WIOE5-LEDG", "1k", FP_R0201, "", "Wio-E5 LED_GREEN (PA15) current limit, active-high per HAL", [("1", "A", "WIOE5_LED_G"), ("2", "B", "WIOE5_LEDG_A")]),
    ("LED-WIOE5-G", "Green", FP_LED0603, "", "Wio-E5 status LED (green)", [("1", "A", "WIOE5_LEDG_A"), ("2", "K", "GND")]),
    ("R-WIOE5-LEDR", "1k", FP_R0201, "", "Wio-E5 LED_RED (PB5) current limit, active-low (sinks) per HAL", [("1", "A", "+3V3_RF"), ("2", "B", "WIOE5_LEDR_A")]),
    ("LED-WIOE5-R", "Red", FP_LED0603, "", "Wio-E5 status LED (red)", [("1", "A", "WIOE5_LEDR_A"), ("2", "K", "WIOE5_LED_R")]),
    # LoRa (RFM95W) SPI filtering block REMOVED 2026-09-20 along with LORA
    # itself (duplicate of Commo's LoRa radio; see the ICS list note above).
    # --- WIFI-BT-ZB (Murata Type 2EL) power bypass + SDIO filtering ---------
    # R-WIFI-EN (WLAN_EN pull-up) REMOVED 2026-09-21: Type2EL's PDn (unlike
    # WL1837MOD's WLAN_EN) already has a documented internal weak pull-DOWN
    # (type2el.pdf Table 9, 51kOhm nominal) — the module defaults to power-down
    # until the host actively drives PDn/WIFI_EN high, so an external pull-up
    # would fight that documented-safe default rather than support it.
    ("C-ZB-33-1", "100nF", FP_C0402, "", "WIFI-BT-ZB AVDD33_1 bypass", [("1", "P", "+3V3_RF"), ("2", "N", "GND")]),
    ("C-ZB-33-2", "100nF", FP_C0402, "", "WIFI-BT-ZB AVDD33_2 bypass", [("1", "P", "+3V3_RF"), ("2", "N", "GND")]),
    ("C-ZB-18-1", "100nF", FP_C0402, "", "WIFI-BT-ZB AVDD18_1 bypass", [("1", "P", "+1V8_RF"), ("2", "N", "GND")]),
    ("C-ZB-18-2", "100nF", FP_C0402, "", "WIFI-BT-ZB AVDD18_2 bypass", [("1", "P", "+1V8_RF"), ("2", "N", "GND")]),
    ("C-ZB-VIO", "100nF", FP_C0402, "", "WIFI-BT-ZB VIO bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-ZB-SDVIO", "100nF", FP_C0402, "", "WIFI-BT-ZB SD_VIO bypass (shares U-1V8RF's +1V8_RF, no separate LDO)", [("1", "P", "+1V8_RF"), ("2", "N", "GND")]),
    ("FB-SDIO1", "742792510", FP_L1812, "742792510", "SDIO CMD ferrite (Wurth 742792510)", [("1", "IN", "SDIO_CMD"), ("2", "OUT", "SDIO_CMD_F")]),
    ("FB-SDIO2", "742792510", FP_L1812, "742792510", "SDIO CLK ferrite", [("1", "IN", "SDIO_CLK"), ("2", "OUT", "SDIO_CLK_F")]),
    ("FB-SDIO3", "742792510", FP_L1812, "742792510", "SDIO D0 ferrite", [("1", "IN", "SDIO_D0"), ("2", "OUT", "SDIO_D0_F")]),
    ("FB-SDIO4", "742792510", FP_L1812, "742792510", "SDIO D1 ferrite", [("1", "IN", "SDIO_D1"), ("2", "OUT", "SDIO_D1_F")]),
    ("FB-SDIO5", "742792510", FP_L1812, "742792510", "SDIO D2 ferrite", [("1", "IN", "SDIO_D2"), ("2", "OUT", "SDIO_D2_F")]),
    ("FB-SDIO6", "742792510", FP_L1812, "742792510", "SDIO D3 ferrite", [("1", "IN", "SDIO_D3"), ("2", "OUT", "SDIO_D3_F")]),
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
    # FL-SIK/D-ANT-SIK/J-SMA-SIK (RFD900ux-SMT's own antenna chain) REMOVED
    # 2026-09-21 along with SIK itself (relocated to Commo). Wio-E5's antenna
    # chain follows the vendor's OWN reference design (wio-e5-datasheet.pdf
    # Fig.12: RFIO -> C2/C3 matching caps -> SMA), not the Johanson
    # bandpass-filter part SIK used — a generic 915MHz bandpass filter isn't
    # necessarily the right match network for the SX126x radio integrated in
    # STM32WLE5, so this follows the same disclosed "populate per bench VSWR
    # tuning" pattern already used for WIFI-BT-ZB's shared antenna (Type2EL):
    # series 0R placeholder for continuity, both shunt positions DNP.
    ("C-WIOE5-SH1", "DNP", FP_C0201, "", "Wio-E5 antenna match shunt 1 (DNP until bench VSWR tuning)",
     [("1", "A", "WIOE5_ANT_RF"), ("2", "B", "GND")]),
    ("L-WIOE5-SER", "0R link", FP_R0402, "", "Wio-E5 antenna match series position — 0R placeholder for continuity before tuning",
     [("1", "A", "WIOE5_ANT_RF"), ("2", "B", "WIOE5_ANT_F")]),
    ("C-WIOE5-SH2", "DNP", FP_C0201, "", "Wio-E5 antenna match shunt 2 (DNP until bench VSWR tuning)",
     [("1", "A", "WIOE5_ANT_F"), ("2", "B", "GND")]),
    ("D-ANT-WIOE5", "RCLAMP0502B", FP_RCLAMP, "RCLAMP0502BTCL", "RF ESD shunt, same flag as D-ANT-SIK originally carried",
     [("1", "A", "WIOE5_ANT_F"), ("2", "K", "PGND")]),
    ("J-ANT-WIOE5", "MMCX vertical", FP_MMCX, "73415-1471",
     "Wio-E5/mLRS antenna jack — same vertical-MMCX board-area rationale as XO's other antenna "
     "jacks (SiK's own former jack, WIFI-BT-ZB's shared jack)",
     [("1", "RF", "WIOE5_ANT_F"), ("2", "SHIELD", "PGND")]),
    # FL-LORA / D-ANT-LORA / J-SMA-LORA (LoRa antenna filter/ESD/jack chain)
    # REMOVED 2026-09-20 along with LORA itself.
    # FL-WIFI (Johanson 2.45 GHz band-pass filter) REMOVED 2026-09-21 along
    # with WL1837MOD: Type2EL's own on-module front end already contains the
    # LPF/diplexer/SPDT per its datasheet Fig.1 block diagram, so a discrete
    # single-band filter ahead of a now-TRI-band shared antenna feed (2.4/5
    # GHz WLAN + 802.15.4) would be actively wrong, not just redundant.
    # Replaced with a standard pi (shunt-series-shunt) antenna matching
    # network per the Unified Design Guide Fig.6/7 reference schematic's own
    # "Antenna & Tuning / Matching Components" section — that section shows
    # several of its own positions as DNP, because a matching network for a
    # shared multi-band antenna is genuinely antenna-specific and always
    # bench-tuned (VNA/VSWR) against the real, as-built antenna, never
    # populated from a vendor reference value blindly. Series position
    # starts populated with a 0R link so the board is continuity-testable
    # before tuning; both shunt positions start DNP (open, unpopulated
    # footprint) per the vendor's own reference pattern.
    ("C-ANT-SH1", "DNP", FP_C0402, "", "Antenna match shunt 1 (DNP until bench VSWR tuning against the real antenna)",
     [("1", "A", "RADIO_ANT_RF"), ("2", "B", "GND")]),
    ("L-ANT-SER", "0R link", FP_R0402, "", "Antenna match series position — 0R placeholder for continuity before tuning",
     [("1", "A", "RADIO_ANT_RF"), ("2", "B", "RADIO_ANT_F")]),
    ("C-ANT-SH2", "DNP", FP_C0402, "", "Antenna match shunt 2 (DNP until bench VSWR tuning)",
     [("1", "A", "RADIO_ANT_F"), ("2", "B", "GND")]),
    ("D-ANT-RADIO", "RCLAMP0502B", FP_RCLAMP, "RCLAMP0502BTCL", "RF ESD shunt, same flag as D-ANT-SIK — now the "
     "single shared WiFi/BT/802.15.4 antenna feed (was WiFi-only)",
     [("1", "A", "RADIO_ANT_F"), ("2", "K", "PGND")]),
    ("J-ANT-RADIO", "MMCX vertical", FP_MMCX, "73415-1471",
     "Shared WiFi/BT/802.15.4 antenna jack (SANT mode) — was WiFi-only J-SMA-WIFI; Type2EL's single "
     "ANT0 feed now serves all three radios, so XO drops from needing (at minimum) two antenna "
     "jacks/chains down to one",
     [("1", "RF", "RADIO_ANT_F"), ("2", "SHIELD", "PGND")]),
    ("C-ANT-SANT", "10pF", FP_C0201, "", "SANT-mode loopback per type2el.pdf Table 6/7 + Unified Design "
     "Guide Fig.10: shared-antenna mode requires ANT1 (pin 23) looped back to BT_15.4_IN (pin 18) "
     "through this cap, NOT a direct short",
     [("1", "A", "RADIO_ANT1_OUT"), ("2", "B", "RADIO_ANT1_IN")]),
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
                  "VCC2_CANB", "VCC2_RS485B", "PGND", "+3V3_PB2", "+3V3_RF", "+1V8_RF"]

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
