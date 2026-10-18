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
    - MIL-STD-1553C (2026-09-28 fleet swap, avionics/WBS.md §1.2a.3): Holt
      HI-6138 BC/RT/MT protocol engine with on-chip transceiver (QFN-48 6x6,
      host SPI0, DS6138 Rev S) replaces the HI-1573 + AM6254 PRU Manchester
      codec; 50 MHz MCLK from a dedicated ECS-2520MV (not the PHY's RMII clock,
      so an Ethernet PHY reset cannot stop 1553).  Premier PM-DB2791S 1:2.5
      direct-coupled stub + 2 x 55 R + 2 x SMAJ33CA are unchanged (DS6138
      Fig 28; [REF-MIL-001 §4.5.1.5.2]).  Pin table and area budget:
      avionics/kicad/HI6138_FOOTPRINT_VERIFICATION.md.
    - PWM/DSHOT block: Samtec TSM-108-01-L-DV 2x8 SMT 0.1 in header (SIG /
      +5V / GND / PGND-shield per channel) so B.Cu under it stays usable;
      0201 for straps, pull-ups and 10 nF HF bypass.
    - Cape-local +3V3 module (TPSM828224SILR, [REF-PWR-008]; was TPS62933
      [REF-PWR-001] until 2026-10-17) so the cape does not
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
* 2026-10-12 (Claude Opus 5.5) — GNSS moved OFF the cape (owner decision): the
  MAX-M10S, its bias-T (R-ANT / C-ANT / L-ANT), U.FL J-ANT and C-GPS1/2 are
  removed and P1-31/32 (UART) + P2-9/10 (RESET_N / TIMEPULSE) become NC.  The
  two dorsal GPS cups get isolated CAN-FD GPS pucks instead (avionics/WBS.md).
  Reason: two ISOW §13.1 4 mm metal-free bubbles [REF-SENSOR-009/010] do not
  fit the 55 x 35 mm cape with the GPS aboard.  The same pass adds the §13.1
  ferrite beads and splits the DC-DC output nets (see FB-CAN-* / FB-485-*).

Datasheets (all in ``avionics/datasheets/``; OEM documents are authoritative
per ``avionics/AGENTS.md``):
  ISOW1044BDFMR isow1044.pdf Table 7-1 | ISOW1412DFMR isow1412.pdf Table 7-1 |
  SLB9672 slb9672.pdf §3.1.2 | BLM15EX331SN1D Murata_BLM15EX_JENF243A-0023M-01.pdf |
  DP83825I dp83825i.pdf Table 4-1/6-8..6-11, Fig 8-3/8-4 | 749010012A 749010012A.pdf p.1 |
  HI-6138 hi-6138_v-rev-s.pdf p.1/Table 1/§29 | PM-DB2791S PremierMagnetics_DB2791S.pdf | Samtec TSM samtec_tsm-dv-footprint.pdf |
  ICM-42688-P ds-000347 Table 10 | BMP388 bst-bmp388-ds001.pdf Table 50 |
  SRF2012A SRF2012A.pdf | TPSM828224SILR tpsm82822.pdf (SLVSEP0F) Table 6-1 |
  ECS-2520MV ECS-2520MV.pdf p.1 |
  X2Y (Yageo CX0805) X2Y_15-2237598.pdf Table 3.

Author: Claude Opus 4.8 (2026-07-14); Claude Opus 5 (2026-07-28, 2026-09-19);
Claude Opus 5.5 (2026-09-28, HI-6138 1553C swap; 2026-10-12, §13.1 beads + GNSS off-board).
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
FP_L0402 = "Inductor_SMD:L_0402_1005Metric"
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
FP_HI6138 = "Serenity-Custom:Holt_HI-6138_QFN-48_6x6mm_P0.4mm_EP4.6mm"
FP_SMA = "Diode_SMD:D_SMA"
FP_X1553 = "Serenity-Custom:Xfmr_1553_SMD_0.40in_8pin"
FP_TSM2X8 = "Serenity-Custom:Samtec_TSM-108-01-x-DV"
FP_LGA14 = "Package_LGA:Bosch_LGA-14_3x2.5mm_P0.5mm"
FP_SOT583 = "Package_TO_SOT_SMD:SOT-583-8"
FP_SIL0010D = "Serenity-Custom:TI_SIL0010D_uSiP-10_2.0x2.5mm_P0.5mm"
FP_SOT363 = "Package_TO_SOT_SMD:SOT-363_SC-70-6"
FP_OSC2520 = "Oscillator:Oscillator_SMD_ECS_2520MV-xxx-xx-4Pin_2.5x2.0mm"
FP_GH4 = "Connector_JST:JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal"
FP_GH6 = "Connector_JST:JST_GH_SM06B-GHS-TB_1x06-1MP_P1.25mm_Horizontal"
FP_GH7 = "Connector_JST:JST_GH_SM07B-GHS-TB_1x07-1MP_P1.25mm_Horizontal"
FP_QFN24_4X4 = "Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.8x2.8mm"
FP_DQA10 = "Serenity-Custom:TI_DQA0010A_USON-10_2.5x1.0mm_P0.5mm"
FP_SOD523 = "Diode_SMD:D_SOD-523"
FP_F0805 = "Fuse:Fuse_0805_2012Metric"
FP_HOLE = "Serenity-Custom:MountingHole_2.7mm_M2.5_PGND_Ring"
# project-custom lands (avionics/kicad/Serenity-Custom.pretty)
FP_SAM = "Serenity-Custom:uBlox_SAM-M10Q-00B"
FP_WELAN = "Serenity-Custom:Wurth_749010012A_WE-LAN"
FP_BMP388 = "Serenity-Custom:Bosch_BMP388_LGA-10_2x2mm"
FP_X2Y0805 = "Serenity-Custom:X2Y_0805_4T"
FP_SRF2012 = "Serenity-Custom:Bourns_SRF2012_4T"
FP_NANOFIT = "Serenity-Custom:Molex_NanoFit_1x04_Horizontal"
# PB2 rails: Samtec TSM-118-04-L-DV-LC SMT male terminal strips, same as TACCO (owner
# 2026-10-05/06, avionics/WBS.md R2): the PocketBeagle 2 Industrial carries female
# receptacles, so the cape carries the pins.  samtec_tsm-dv-footprint.pdf Rev F Fig. 1
# land; -04 is the shortest post, giving a ~5.5 mm cape-to-PB2 gap; -LC clips anchor it.
FP_PB2P1 = "Serenity-Custom:PocketBeagle2_2x18_P1_TSM-DV-LC"
FP_PB2P2 = "Serenity-Custom:PocketBeagle2_2x18_P2_TSM-DV-LC"
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
            # 2026-10-12 ISOW1044 SLLSFF7A sec 13.1 item 4: the DC-DC side (VISOOUT/VSIN,
            # GND2) is split from the transceiver side (VISOIN, GISOIN) by two
            # BLM15EX331SN1D beads, FB-CAN-V / FB-CAN-G (owner decision, Claude Opus 5.5).
            ("13", "VSIN", "VCC2_CAN_DCDC", "R"),
            ("12", "VISOOUT", "VCC2_CAN_DCDC", "R"),
            ("11", "GND2", "GND2_CAN_DCDC", "R"),
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
            # 2026-10-12 ISOW1412 SLLSF86C sec 13.1 items 4/5: DC-DC side split from the
            # transceiver side by FB-485-V / FB-485-G; MODE stays in the VISOOUT domain
            # (shorted to pin 11 -> 3.3 V transceiver supply, unchanged).
            ("13", "MODE", "GND2_RS485_DCDC", "R"),
            ("12", "VISOOUT", "VCC2_RS485_DCDC", "R"),
            ("11", "GND2", "GND2_RS485_DCDC", "R"),
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
]


def dp83825i(ref: str, rmii: str, rstn: str, intn: str, eth: str, mdio: str, mdc: str) -> Dict[str, Any]:
    """TI DP83825I 10/100 RMII PHY, WQFN-24 (RMQ0024A) — dp83825i.pdf Table 4-1.

    2026-10-17 (Claude Opus 5.5): re-checked against TI SNLS638C (rev. April 2026) Table
    4-1 and the strap table: pin 17 RX_D1 is the Leader/Follower strap, default 0 =
    RMII Leader (internal pull-down), so the 50 MHz RMII reference on pin 2 is set by
    hardware.  Used once, on the PB2-I's only header MAC (RMII2 + MDIO0, official
    BeagleBoard schematic sheet 16) for ring port 1.

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
            ("13", "XI", "XI_25M", "R"),
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


def ch397a(ref: str, eth: str) -> Dict[str, Any]:
    """WCH CH397A USB 2.0 to 10/100 Ethernet controller with integrated MAC + PHY,
    QFN24 4x4 mm, built-in SPI flash (MAC address / configuration).  Owner decision
    2026-10-17 (S. Griffing, "Option 1"): the Ethernet ring's second port runs on the
    PB2-I's USB1 (D+/D- on P1-11/P1-9, official schematic sheets 14/16), bridged in
    Linux with ring port 1 (DP83825I on RMII2).  Implemented by Claude Opus 5.5.

    Pinout: CH397 datasheet V1.2 Fig. 1-1 / Table 1-3, CH397A column [REF-SENSOR-048];
    no RSTB pin on the CH397A (internal POR, sec 3.1.2).  Supply per sec 3.7 / sec 6.1:
    for industrial use V5 and AVDD33 both on the 3.3 V supply (TA -40..85 C, sec 4.1);
    XI takes "a 25 MHz crystal or an external clock input" (Table 1-3) -> the shared
    X-25M oscillator, XO open.  50 ohm MDI termination is internal (sec 3.3, sec 6.1),
    transformer centre taps to GND through capacitors only (sec 6.1 note on T1).
    Firmware default CDC-ECM (sec 3.2) -> Linux cdc_ether.
    """
    return {
        "ref": ref,
        "value": "CH397A",
        "fp": FP_QFN24_4X4,
        "mpn": "CH397A",
        "ds": "CH397 datasheet V1.2 Table 1-3 / Fig. 1-1 (CH397A QFN24) [REF-SENSOR-048]",
        "pins": [
            ("8", "UDP", "USB1_DP", "L"),
            ("7", "UDM", "USB1_DM", "L"),
            ("21", "XI", "XI_25M", "L"),
            ("22", "XO", None, "L"),
            ("15", "LED0", None, "L"),
            ("17", "LED1", None, "L"),
            ("14", "GPIO6", None, "L"),
            ("12", "NC", None, "L"),
            ("16", "NC", None, "L"),
            ("19", "NC", None, "L"),
            ("20", "NC", None, "L"),
            ("2", "MDITP", f"{eth}_TXP", "R"),
            ("3", "MDITN", f"{eth}_TXN", "R"),
            ("4", "MDIRP", f"{eth}_RXP", "R"),
            ("5", "MDIRN", f"{eth}_RXN", "R"),
            ("11", "V5", "+3V3", "R"),
            ("10", "AVDD33", "+3V3", "R"),
            ("1", "AVDD33", "+3V3", "R"),
            ("13", "VDDIO", "+3V3", "R"),
            ("18", "VDDIO", "+3V3", "R"),
            ("23", "AVDDK", f"{ref}_AVDDK", "R"),
            ("9", "DVDDK", f"{ref}_DVDDK", "R"),
            ("6", "GND", "GND", "R"),
            ("24", "GND", "GND", "R"),
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
    dp83825i("PHY-RMII2", "RMII2", "RMII2_PHY_RSTN", "RMII2_PHY_INTRN", "ETH_RMII2", "MDIO0", "MDC0"),
    ch397a("NIC-USB1", "ETH_USB1"),
    eth_xfmr("T-RMII2", "ETH_RMII2"),
    eth_xfmr("T-USB1", "ETH_USB1"),
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
        "value": "HI-6138PCIF",
        "fp": FP_HI6138,
        "mpn": "HI-6138PCIF",
        "ds": "hi-6138_v-rev-s.pdf p.1 Pin Configuration (48-pin 6x6 QFN) / Table 1 pp.16-18 / §29 p.263",
        # MIL-STD-1553 BC/MT/RT protocol engine with shared on-chip dual
        # transceiver (DS6138 Rev S).  Host SPI0 (CE on P1-20 GPIO), IRQ
        # open-drain -> P1-7 with 10 k pull-up, MR -> P1-8, TXINHA -> P1-9
        # (internal pull-up = transmit inhibited until the host drives it low).
        # Bus A only, as before; TXINHB left on its internal pull-up (bus B
        # inhibited).  LOCK low (internal pull-down) so the host writes the RT
        # address; RTA4:0/RTAP left on internal pull-ups.  EEPROM auto-init
        # port unused.  Every no-connect is justified pin by pin in
        # avionics/kicad/HI6138_FOOTPRINT_VERIFICATION.md §2.
        "pins": [
            ("2", "IRQ*", "M1553_IRQN", "L"),
            ("11", "TXINHA", "M1553_TX_INH", "L"),
            ("15", "CE*", "SPI0_CS_1553", "L"),
            ("17", "SCK", "SPI0_CLK", "L"),
            ("18", "SO", "SPI0_MISO", "L"),
            ("19", "SI", "SPI0_MOSI", "L"),
            ("21", "MCLK", "M1553_MCLK", "L"),
            ("23", "MR*", "M1553_MRN", "L"),
            ("45", "BUSA", "M1553_P", "R"),
            ("43", "BUSA*", "M1553_N", "R"),
            ("40", "BUSB", None, "R"),
            ("42", "BUSB*", None, "R"),
            ("6", "VCC", "+3V3", "R"),
            ("16", "VCC", "+3V3", "R"),
            ("31", "VCC", "+3V3", "R"),
            ("41", "VCCP", "+3V3", "R"),
            ("44", "VCCP", "+3V3", "R"),
            ("7", "GND", "GND", "R"),
            ("20", "GND", "GND", "R"),
            ("30", "GND", "GND", "R"),
            ("49", "EP", "GND", "R"),
        ] + [(str(n), nm, None, "L") for n, nm in (
            (1, "MODE"), (3, "ACKIRQ"), (4, "MODE1760"), (5, "READY"), (8, "ACTIVE"),
            (9, "RTSSF"), (10, "AUTOEN"), (12, "TXINHB"), (13, "RTAP"), (14, "RTA0"),
            (22, "RTA1"), (24, "RTA2"), (25, "RTA3"), (26, "RTA4"), (27, "LOCK"),
            (28, "MTTCLK"), (29, "EMISO"), (32, "EMOSI"), (33, "ECS*"), (34, "EECOPY"),
            (35, "ESCLK"), (36, "TTCLK"), (37, "RTMC8*"), (38, "EE2K"), (39, "MTSTOFF"),
            (46, "TEST"), (47, "BENDI"), (48, "BCTRIG"))],
    },
    {
        "ref": "1553-XFM",
        "value": "PM-DB2791S",
        "fp": FP_X1553,
        "mpn": "PM-DB2791S",
        "ds": "PremierMagnetics_DB2791S.pdf Fig 1 schematic (1-3 : 4-8 = 1:2.5) / Fig 2 dims [REF-SENSOR-025]",
        # 1:2.5 isolation transformer per DS6138 Fig 28 (same ratio Holt specifies for HI-1573).
        # Primary 1-3 (CT 2 -> GND) on the HI-6138 BUSA pins, secondary 4-8 to the bus
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
        "value": "TPSM828224SILR",
        "fp": FP_SIL0010D,
        "mpn": "TPSM828224SILR",
        "ds": "tpsm82822.pdf SLVSEP0F Table 6-1 Pin Functions (uSiL SIL0010D) [REF-PWR-008]",
        # 2026-10-17 (S. Griffing decision; Claude Opus 5.5): TPS62933 + WE-MAPI
        # 3015 replaced by the TI TPSM828224SILR fixed-3.3 V, 2 A MicroSiP module
        # (inductor inside, 2.0 x 2.5 x 1.1 mm) to fit the 3V3 supply between the
        # ISOW sec 13.1 bubbles.  Fixed-output device: FB (8) ties to VOUT and
        # R1/R2/C3 are not needed (SLVSEP0F sec 9.2.1.2.1).  EN (3) "do not leave
        # floating" -> tied to VIN.  PG (4) unused -> floating per Table 6-1.
        # VIN 2.4-5.5 V (abs max 6 V); +5V is held 4.5-5.5 V by the ISOW VDD limit.
        "pins": [
            ("1", "VIN", "+5V", "L"),
            ("2", "VIN", "+5V", "L"),
            ("3", "EN", "+5V", "L"),
            ("4", "PG", None, "L"),
            ("5", "VOUT", "+3V3", "R"),
            ("6", "VOUT", "+3V3", "R"),
            ("7", "VOUT", "+3V3", "R"),
            ("8", "FB", "+3V3", "R"),
            ("9", "GND", "GND", "R"),
            ("10", "GND", "GND", "R"),
        ],
    },
]

# ---------------------------------------------------------------------------
# PocketBeagle 2 Industrial (PB2-I) P1 / P2 cape headers — rebuilt 2026-10-17 from the
# OFFICIAL BeagleBoard references (owner directive: not project files), by Claude Opus 5.5:
#   * openbeagle.org/pocketbeagle/pocketbeagle-2 @ be5f0a4 (CC BY-SA 4.0):
#     pocketbeagle2_sch.pdf V10 (2024-12-20) sheet 16 "P1 / P2", sheet 15 (AIN0-7 run
#     straight to the MSPM0L1105, no RC), sheet 12 (EMMC_RSTn = F23, not a header ball);
#     design/pocketbeagle2 revA_dimension.pdf + images/pocketbeagle2-back.jpg (pin 1 rows);
#   * PocketBeagle 2 SRM (docs.beagleboard.org/pocketbeagle-2.pdf) sec 4.2 pin/ball/mux
#     tables [REF-SENSOR-041];
#   * beagleboard.org/boards/pocketbeagle-2-industrial: PB2-I = PB2 + 1 GB DDR4 + 64 GB
#     eMMC + -40..85 C; its "Design" link is the same repository, so the header map is the
#     PB2's.
# The previous table (GND on P1-1 = PB2 VIN, +3V3/+5V on PRU balls, PHY resets on
# P2-13..16 = VSYS / VBAT / GND / BAT_TS, RMII0/1 that the headers do not carry) is gone.
# Rules: power / ground / USB / battery / reset pins are hardware and are wired per the
# schematic or left open; peripheral functions sit on the pins that carry that function's
# ball (mux mode in the SRM table); remappable GPIO roles are placed on the header pins
# nearest their consumer to shorten routes.  Where a header pin has two balls, the second
# ball must be left as an input by the device tree (noted).  Not driven by the cape: P1-14
# / P2-23 (PB2 3V3 out), P1-24 / P2-13 (VSYS), P2-14 (VBAT), P2-16 (BAT_TS), P2-12
# (PWR_BTN), P2-26 (RESET#), P1-7 (VIN.USB), P1-17/18 (AIN refs), P1-30/32 (UART0 = the
# PB2 console).  USB1 (P1-5 VBUS, P1-9 D-, P1-11 D+) carries ring port 2 (CH397A); its
# DRVVBUS (P1-3) and ID (P1-13) balls are plain GPIO here, USB1 runs host-only.  P1-19/21/23/25/27 and P2-35/36 are also MSPM0 AIN inputs: the MSPM0
# must keep them high-impedance (firmware requirement).
# ---------------------------------------------------------------------------
PB2_P1 = [
    "+5V",            # 1  VIN 5 V in (cape powers the PB2-I)
    "RMII2_TX_EN",    # 2  AA19 RMII2_TX_EN (E18 GPIO1_10 left input)
    "SPI0_CS_IMU",    # 3  F18 GPIO1_51 (GPIO chip select, next to the IMU)
    "RMII2_TXD0",     # 4  Y18 RMII2_TXD0 (D20 left input)
    "+5V",            # 5  USB1_VBUS: cape-supplied VBUS (PB2-I divides it 1k/20k to AB10) — USB1 host to the CH397A
    "EXT_SPI_SS1",    # 6  E19 SPI2_CS0 (AD18 left input)
    None,             # 7  VIN.USB
    "EXT_SPI_SCK",    # 8  A20 SPI2_CLK
    "USB1_DM",        # 9  AD10 USB1_DM -> CH397A UDM
    "EXT_SPI_MISO",   # 10 B19 SPI2_D0 (A18 left input)
    "USB1_DP",        # 11 AE9 USB1_DP -> CH397A UDP
    "EXT_SPI_MOSI",   # 12 A19 SPI2_D1 (AE18 left input)
    "DSHOT1",         # 13 N20 PR0_PRU0_GPO13
    None,             # 14 VDD_3V3 out of the PB2 (cape has its own +3V3)
    "GND",            # 15
    "GND",            # 16
    None,             # 17 AIN.VREF-
    None,             # 18 AIN.VREF+
    "RMII2_RX_ER",    # 19 AD22 RMII2_RX_ER (+AIN0)
    "TPM_IRQN",       # 20 Y24 GPIO0_50
    "DSHOT3",         # 21 AE22 PR0_PRU0_GPO16 (+AIN1)
    "GND",            # 22
    "DSHOT0",         # 23 AC21 PR0_PRU0_GPO4 (+AIN2)
    None,             # 24 VOUT (VSYS)
    "RMII2_RXD1",     # 25 AB20 RMII2_RXD1 (+AIN3)
    "SPI0_CS_TPM",    # 26 K24 GPIO0_44 (D6 left input) — beside the TPM
    "RMII2_RXD0",     # 27 AE23 RMII2_RXD0 (+AIN4)
    "TPM_RSTN",       # 28 K22 GPIO0_43 (B3 left input)
    "DSHOT2",         # 29 Y20 PR0_PRU0_GPO7
    None,             # 30 E14 UART0_TXD — PB2 console, left free
    "EXT_SPI_SS2",    # 31 Y22 GPIO0_59
    None,             # 32 D14 UART0_RXD — PB2 console, left free
    "EXT_I2C_SDA",    # 33 A17 I2C1_SDA (AA23 left input)
    "RMII2_REF_CLK",  # 34 AD23 RMII2_REF_CLK
    "RMII2_CRS_DV",   # 35 AE21 RMII2_CRS_DV
    "EXT_I2C_SCL",    # 36 B17 I2C1_SCL (V20 left input)
]
PB2_P2 = [
    "MDC0",           # 1  AD24 MDIO0_MDC (B20 left input)
    "EXT_UART_RX",    # 2  U22 UART2_RXD
    "MDIO0",          # 3  AB22 MDIO0_MDIO (B18 left input)
    "EXT_UART_TX",    # 4  V24 UART2_TXD
    "MCAN0_TX",       # 5  C15 MCAN0_TX (B5 left input)
    "M1553_MRN",      # 6  W25 GPIO0_47
    "MCAN0_RX",       # 7  E15 MCAN0_RX (A5 left input)
    "M1553_TX_INH",   # 8  W24 GPIO0_48
    "SPI0_CS_1553",   # 9  A15 SPI0_CS2 (D4 left input)
    "CAN_STB",        # 10 AD21 GPIO0_91
    "SPI0_CS_BARO",   # 11 B15 SPI0_CS3 (E5 left input)
    None,             # 12 PWR_BTN
    None,             # 13 VOUT (VSYS)
    None,             # 14 BAT.VIN
    "GND",            # 15
    None,             # 16 BAT.TEMP
    "M1553_IRQN",     # 17 AC24 GPIO0_64
    "BARO_INT",       # 18 V21 GPIO0_53
    "IMU_INT1",       # 19 AC20 GPIO1_0
    "RMII2_PHY_RSTN",      # 20 Y25 GPIO0_49 (DP83825I reset)
    "GND",            # 21
    "IMU_INT2",       # 22 AC25 GPIO0_63
    None,             # 23 VDD_3V3 out of the PB2
    "RS485_RX",       # 24 Y23 UART5_RXD
    "SPI0_MOSI",      # 25 B14 SPI0_D1
    None,             # 26 RESET#
    "SPI0_MISO",      # 27 B13 SPI0_D0
    "RMII2_PHY_INTRN",     # 28 AB24 GPIO0_61 (DP83825I interrupt)
    "SPI0_CLK",       # 29 A14 SPI0_CLK (M22 left input)
    None,             # 30 AA24 GPIO0_58 — spare
    "RMII2_TXD1",     # 31 AA18 RMII2_TXD1 (A13 SPI0_CS0 left input)
    "RS485_DE",       # 32 AB25 UART5_RTSn (hardware RS-485 direction)
    "RS485_TX",       # 33 AA25 UART5_TXD
    None,             # 34 AA21 GPIO0_60 — spare
    None,             # 35 W21 GPIO0_54 (+AIN5) — spare
    None,             # 36 C13 SPI0_CS1 (+AIN7) — spare
]


def pb2_header(ref: str, value: str, fp: str, nets: List[Optional[str]]) -> Dict[str, Any]:
    rail = ref.split("-")[-1]  # "P1" / "P2"
    # pin names = BeagleBoard SRM designators P1.01..P2.36 [REF-SENSOR-041 sec 4.2]
    pins = [(str(i), f"{rail}.{i:02d}", net, "L" if i <= 18 else "R") for i, net in enumerate(nets, start=1)]
    return {"ref": ref, "value": value, "fp": fp, "mpn": "TSM-118-04-L-DV-LC",
            "ds": "PocketBeagle 2 P1/P2 expansion rails; Samtec TSM-DV SMT male strip, -04 post, "
                  "-LC locking clip (manual placement) [REF-SENSOR-042]", "pins": pins}


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
    # --- +3V3 module (TPSM828224SILR, REF-PWR-008) -------------------------
    # SLVSEP0F sec 9.2.2: effective CIN >= 3 uF and COUT >= 5 uF after DC bias.
    # Parts are TI's own Table 9-1 BOM entries (C1 / C2).  C-3V3-O2 is kept as
    # load-step margin for the HI-6138 transmit bursts.
    # CIN DC bias (2026-10-17, owner decision S. Griffing; Claude Opus 5.5): the first pick,
    # Murata GRM188Z71A106MA73D, keeps only 2.65 uF worst case at 5.5 V [REF-PWR-012] and
    # fails the >= 3 uF floor.  Taiyo Yuden 22 uF: -71 % at 5.5 V [REF-PWR-011] ->
    # 22 x 0.80 x 0.29 x 0.83 = 4.2 uF worst case.  Same 0603 land; one cap part on the rail.
    ("C-3V3-IN", "22uF 6.3V X6S", FP_C0603, "MSASJ168BC6226MTNA01", "TPSM828224 CIN at VIN/GND [REF-PWR-008] [REF-PWR-011]", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-3V3-HF", "100nF", FP_C0402, "", "TPSM828224 CIN HF", [("1", "P", "+5V"), ("2", "N", "GND")]),
    # COUT DC bias (2026-10-17, Claude Opus 5.5): Taiyo Yuden curve [REF-PWR-011] digitized
    # -51 % at 3.333 V; worst case 22 uF x 0.80 (tol) x 0.49 (bias) x 0.83 (X6S, 105 C)
    # = 7.2 uF per cap, so even one cap meets the >= 5 uF effective floor.
    ("C-3V3-O1", "22uF 6.3V X6S", FP_C0603, "MSASJ168BC6226MTNA01", "TPSM828224 COUT (TI Table 9-1 JMK107BC6226MA-T, renumbered) [REF-PWR-008] [REF-PWR-011]", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-3V3-O2", "22uF 6.3V X6S", FP_C0603, "MSASJ168BC6226MTNA01", "TPSM828224 COUT, load-step margin [REF-PWR-008] [REF-PWR-011]", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    # --- CAN FD field port -------------------------------------------------
    ("C-CAN1", "10nF", FP_C0402, "", "ISOW1044 VDD HF bypass, 0402 <1 mm (SLLSFF7A 13.1 #1)", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-CAN2", "10uF 10V X5R", FP_C0805, "", "ISOW1044 VDD bulk §13.1", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-CAN3", "100nF", FP_C0402, "", "ISOW1044 VIO bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-CAN4", "10nF", FP_C0402, "", "ISOW1044 VISOOUT HF bypass, 0402 <1 mm (SLLSFF7A 13.1 #1)",
     [("1", "P", "VCC2_CAN_DCDC"), ("2", "N", "GND2_CAN_DCDC")]),
    ("C-CAN5", "10uF 10V X5R", FP_C0805, "", "ISOW1044 VISOOUT bulk, 2-4 mm (SLLSFF7A 13.1 item 2)",
     [("1", "P", "VCC2_CAN_DCDC"), ("2", "N", "GND2_CAN_DCDC")]),
    ("FB-CAN-V", "330R@100MHz", FP_L0402, "BLM15EX331SN1D",
     "ISOW1044 VISOOUT->VISOIN bead (SLLSFF7A 13.1 item 4) [REF-SENSOR-043]",
     [("1", "A", "VCC2_CAN_DCDC"), ("2", "B", "VCC2_CAN")]),
    ("FB-CAN-G", "330R@100MHz", FP_L0402, "BLM15EX331SN1D",
     "ISOW1044 GND2(11)->GISOIN(15) bead (SLLSFF7A 13.1 item 4) [REF-SENSOR-043]",
     [("1", "A", "GND2_CAN_DCDC"), ("2", "B", "GND2_CAN")]),
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
    ("C-485-1", "10nF", FP_C0402, "", "ISOW1412 VDD HF bypass, 0402 <1 mm (SLLSF86C 13.1 #1)", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-485-2", "10uF 10V X5R", FP_C0805, "", "ISOW1412 VDD bulk", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C-485-3", "100nF", FP_C0402, "", "ISOW1412 VIO bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-485-4", "10nF", FP_C0402, "", "ISOW1412 VISOOUT HF bypass, 0402 <1 mm (SLLSF86C 13.1 #1)",
     [("1", "P", "VCC2_RS485_DCDC"), ("2", "N", "GND2_RS485_DCDC")]),
    ("C-485-5", "10uF 10V X5R", FP_C0805, "", "ISOW1412 VISOOUT bulk (SLLSF86C 13.1 item 2)",
     [("1", "P", "VCC2_RS485_DCDC"), ("2", "N", "GND2_RS485_DCDC")]),
    ("FB-485-V", "330R@100MHz", FP_L0402, "BLM15EX331SN1D",
     "ISOW1412 VISOOUT->VISOIN bead (SLLSF86C 13.1 item 4) [REF-SENSOR-043]",
     [("1", "A", "VCC2_RS485_DCDC"), ("2", "B", "VCC2_RS485")]),
    ("FB-485-G", "330R@100MHz", FP_L0402, "BLM15EX331SN1D",
     "ISOW1412 GND2(11)->GISOIN(15) bead (SLLSF86C 13.1 item 4) [REF-SENSOR-043]",
     [("1", "A", "GND2_RS485_DCDC"), ("2", "B", "GND2_RS485")]),
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
    ("J-ETH-RMII2", "SM04B-GHS-TB", FP_GH4, "SM04B-GHS-TB(LF)(SN)", "J-ETH-RMII2 line pair to T-RMII2 secondary",
     [("1", "TXP", "ETH_RMII2_LINE_TXP"), ("2", "TXN", "ETH_RMII2_LINE_TXN"), ("3", "RXP", "ETH_RMII2_LINE_RXP"), ("4", "RXN", "ETH_RMII2_LINE_RXN"),
      ("MP", "SHIELD", "PGND")]),
    ("J-ETH-USB1", "SM04B-GHS-TB", FP_GH4, "SM04B-GHS-TB(LF)(SN)", "J-ETH-USB1 line pair to T-USB1 secondary",
     [("1", "TXP", "ETH_USB1_LINE_TXP"), ("2", "TXN", "ETH_USB1_LINE_TXN"), ("3", "RXP", "ETH_USB1_LINE_RXP"), ("4", "RXN", "ETH_USB1_LINE_RXN"),
      ("MP", "SHIELD", "PGND")]),
    # TPI network per dp83825i.pdf Fig 8-3: 75 R from each line-side centre tap to a
    # common node, 10 nF (2 kV) to chassis.
    ("R-RMII2-BST", "75R", FP_R0402, "", "J-ETH-RMII2 line TX centre tap Bob-Smith (Fig 8-3 R135)", [("1", "A", "ETH_RMII2_LINE_CTX"), ("2", "B", "ETH_RMII2_BS")]),
    ("R-RMII2-BSR", "75R", FP_R0402, "", "J-ETH-RMII2 line RX centre tap Bob-Smith (Fig 8-3 R143)", [("1", "A", "ETH_RMII2_LINE_CRX"), ("2", "B", "ETH_RMII2_BS")]),
    ("C-RMII2-BS", "10nF 2kV", FP_C1808, "", "J-ETH-RMII2 Bob-Smith HV cap to chassis (Fig 8-3 C38)", [("1", "P", "ETH_RMII2_BS"), ("2", "N", "PGND")]),
    ("R-USB1-BST", "75R", FP_R0402, "", "J-ETH-USB1 line TX centre tap Bob-Smith", [("1", "A", "ETH_USB1_LINE_CTX"), ("2", "B", "ETH_USB1_BS")]),
    ("R-USB1-BSR", "75R", FP_R0402, "", "J-ETH-USB1 line RX centre tap Bob-Smith", [("1", "A", "ETH_USB1_LINE_CRX"), ("2", "B", "ETH_USB1_BS")]),
    ("C-USB1-BS", "10nF 2kV", FP_C1808, "", "J-ETH-USB1 Bob-Smith HV cap to chassis", [("1", "P", "ETH_USB1_BS"), ("2", "N", "PGND")]),
    # one 25 MHz oscillator drives both Ethernet controllers' XI pins (XO pins open)
    ("X-25M", "25MHz 3.3V", FP_OSC2520, "ECS-2520MV-250-BN-TR", "25 MHz reference for the DP83825I XI (RMII Leader, +/-50 ppm, SNLS638C) and the CH397A XI (external clock input, CH397 Table 1-3); ECS-2520MV.pdf [REF-PWR-004]",
     [("1", "TRI", None), ("2", "GND", "GND"), ("3", "OUT", "XI_25M"), ("4", "VDD", "+3V3")]),
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
    ("C-1553A", "100nF", FP_C0402, "", "HI-6138 VCC (pins 6/16/31) bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-1553B", "100nF", FP_C0402, "", "HI-6138 VCCP (pins 41/44) bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-1553C", "10uF 6.3V X5R", FP_C0805, "", "HI-6138 transceiver (VCCP) bulk", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-1553D", "100nF", FP_C0402, "", "HI-6138 VCCP second pin bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("R-1553IRQ", "10k", FP_R0402, "", "HI-6138 IRQ open-drain pull-up (DS6138 Table 1)",
     [("1", "A", "+3V3"), ("2", "B", "M1553_IRQN")]),
    ("X-50M", "50MHz 3.3V", FP_OSC2520, "ECS-2520MV-500-BN-TR",
     "HI-6138 MCLK 50.0 MHz +/-100 ppm required (DS6138 Table 1); +/-50 ppm part (ECS-2520MV.pdf)",
     [("1", "TRI", None), ("2", "GND", "GND"), ("3", "OUT", "M1553_MCLK"), ("4", "VDD", "+3V3")]),
    ("C-50M", "100nF", FP_C0402, "", "50 MHz oscillator VDD bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
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
    # A compliant HI-1573 chain was restored 2026-09-19 and replaced by the
    # HI-6138 protocol engine on 2026-09-28 (see the ICS table and the field
    # port block below).
    # --- sensors -------------------------------------------------------------
    ("C-IMU1", "100nF", FP_C0402, "", "ICM-42688-P VDD bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-IMU2", "10nF", FP_C0201, "", "ICM-42688-P VDDIO bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-BARO1", "100nF", FP_C0402, "", "BMP388 VDD bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-BARO2", "100nF", FP_C0402, "", "BMP388 VDDIO bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
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
    for _j, (_fn, _pin_net) in enumerate(((f"SIG{_i}", _net), (f"+5V_{_i}", "+5V"), (f"GND{_i}", "GND"), (f"SHLD{_i}", "PGND"))):
        _k = _col0 + _j
        _pwm_pins.append((str(2 * _k - 1 + _row), _fn, _pin_net))
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
    p = tag  # TI interface name of the leg, e.g. "RMII2" (2026-10-17 naming alignment)
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


SIMPLE += phy_support("RMII2", "PHY-RMII2", "RMII2", "ETH_RMII2")

# --- CH397A support (CH397 datasheet V1.2 sec 3.7 table, sec 6.1 circuit) [REF-SENSOR-048] --
SIMPLE += [
    ("C-USB1-V5A", "10uF 6.3V X6S", FP_C0603, "MSASJ168BC6226MTNA01", "V5 / AVDD33 (pins 11/10) bulk, 3.3 V supply (sec 6.1 C8)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-USB1-V5B", "100nF", FP_C0201, "", "V5 / AVDD33 (pins 11/10) HF (sec 6.1 C2)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-USB1-A1", "1uF", FP_C0402, "", "AVDD33 pin 1 decoupling (Table 1-3)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-USB1-IO", "100nF", FP_C0201, "", "VDDIO pins 13/18 decoupling (Table 1-3)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C-USB1-AK", "1uF", FP_C0402, "", "AVDDK core-analog decoupling, pin 23 (Table 1-3)", [("1", "P", "NIC-USB1_AVDDK"), ("2", "N", "GND")]),
    ("C-USB1-DK", "100nF", FP_C0201, "", "DVDDK core-digital decoupling, pin 9 (Table 1-3)", [("1", "P", "NIC-USB1_DVDDK"), ("2", "N", "GND")]),
    ("C-USB1-CTD", "1uF", FP_C0402, "", "T-USB1 device-side TX centre tap to GND (sec 6.1 C11; no supply on the CT)", [("1", "P", "ETH_USB1_CTD"), ("2", "N", "GND")]),
    ("C-USB1-CRD", "1uF", FP_C0402, "", "T-USB1 device-side RX centre tap to GND (sec 6.1 C12)", [("1", "P", "ETH_USB1_CRD"), ("2", "N", "GND")]),
]

# --- JST-GH expansion headers replacing the GNSS (owner 2026-10-17) -------------------
# Pin order per Pixhawk DS-009 rev 0.1.0 [REF-CONN-002] "Basic GPS port" and "SPI port"
# (pin-compatible only; this is not a Pixhawk-branded product).  Deviation: VCC is the
# cape +5V through a 0.35 A PTC per port, not DS-009's 2.5 A, because +5V feeds the PB2-I
# (VIN, 1 A) and the 3V3 module through FB1 (2 A).  ESD on every signal at the connector
# (TI TPD4E05U06 / TPD1E05U06, SLVSBO7O [REF-SENSOR-044]); I2C 1.5 k pull-ups on the
# cape side as DS-009 sec "I2C port" specifies.  Signals: UART2 + I2C1 (GPS port), SPI2
# with SS1 = SPI2_CS0 and SS2 = GPIO (SPI port) — see PB2_P1 / PB2_P2.
SIMPLE += [
    ("J-GPS", "SM06B-GHS-TB", FP_GH6, "SM06B-GHS-TB(LF)(SN)", "DS-009 Basic GPS port: 5V, TX, RX, SCL, SDA, GND (eGH.pdf)",
     [("1", "VCC", "EXT_GPS_5V"), ("2", "TX", "EXT_UART_TX"), ("3", "RX", "EXT_UART_RX"), ("4", "SCL", "EXT_I2C_SCL"),
      ("5", "SDA", "EXT_I2C_SDA"), ("6", "GND", "GND"), ("MP", "SHIELD", "PGND")]),
    ("J-SPI", "SM07B-GHS-TB", FP_GH7, "SM07B-GHS-TB(LF)(SN)", "DS-009 SPI port: 5V, SCK, MISO, MOSI, !SS1, !SS2, GND (eGH.pdf)",
     [("1", "VCC", "EXT_SPI_5V"), ("2", "SCK", "EXT_SPI_SCK"), ("3", "MISO", "EXT_SPI_MISO"), ("4", "MOSI", "EXT_SPI_MOSI"),
      ("5", "SS1", "EXT_SPI_SS1"), ("6", "SS2", "EXT_SPI_SS2"), ("7", "GND", "GND"), ("MP", "SHIELD", "PGND")]),
    ("F-GPS", "MF-PSMF035X", FP_F0805, "MF-PSMF035X-2", "GPS port VCC PTC, 0.35 A hold / 0.75 A trip (Bourns MF-PSMF) [REF-PWR-013]",
     [("1", "A", "+5V"), ("2", "B", "EXT_GPS_5V")]),
    ("F-SPI", "MF-PSMF035X", FP_F0805, "MF-PSMF035X-2", "SPI port VCC PTC, 0.35 A hold / 0.75 A trip (Bourns MF-PSMF) [REF-PWR-013]",
     [("1", "A", "+5V"), ("2", "B", "EXT_SPI_5V")]),
    ("C-GPS5", "1uF 10V", FP_C0402, "", "GPS port VCC bypass at the connector", [("1", "P", "EXT_GPS_5V"), ("2", "N", "GND")]),
    ("C-SPI5", "1uF 10V", FP_C0402, "", "SPI port VCC bypass at the connector", [("1", "P", "EXT_SPI_5V"), ("2", "N", "GND")]),
    ("R-I2C-SCL", "1.5k", FP_R0201, "", "DS-009 I2C port: 1.5 k pull-up on the autopilot side", [("1", "A", "+3V3"), ("2", "B", "EXT_I2C_SCL")]),
    ("R-I2C-SDA", "1.5k", FP_R0201, "", "DS-009 I2C port: 1.5 k pull-up on the autopilot side", [("1", "A", "+3V3"), ("2", "B", "EXT_I2C_SDA")]),
    ("ESD-GPS", "TPD4E05U06DQAR", FP_DQA10, "TPD4E05U06DQAR", "GPS port ESD, 4 ch (SLVSBO7O Table 4-2) [REF-SENSOR-044]",
     [("1", "D1+", "EXT_UART_TX"), ("2", "D1-", "EXT_UART_RX"), ("3", "GND", "GND"), ("4", "D2+", "EXT_I2C_SCL"),
      ("5", "D2-", "EXT_I2C_SDA"), ("6", "NC", None), ("7", "NC", None), ("8", "GND", "GND"), ("9", "NC", None), ("10", "NC", None)]),
    ("ESD-SPI", "TPD4E05U06DQAR", FP_DQA10, "TPD4E05U06DQAR", "SPI port ESD, 4 ch (SLVSBO7O Table 4-2) [REF-SENSOR-044]",
     [("1", "D1+", "EXT_SPI_SCK"), ("2", "D1-", "EXT_SPI_MISO"), ("3", "GND", "GND"), ("4", "D2+", "EXT_SPI_MOSI"),
      ("5", "D2-", "EXT_SPI_SS1"), ("6", "NC", None), ("7", "NC", None), ("8", "GND", "GND"), ("9", "NC", None), ("10", "NC", None)]),
    ("ESD-SS2", "TPD1E05U06DYAR", FP_SOD523, "TPD1E05U06DYAR", "SPI port SS2 ESD, 1 ch (SLVSBO7O Table 4-1) [REF-SENSOR-044]",
     [("1", "IO", "EXT_SPI_SS2"), ("2", "GND", "GND")]),
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
    n_pins = len(left) + len(right)
    # Passives (2-pin R/C/L/TVS/etc.) get a compact 600 x 200 mil box instead
    # of the 1300 x 300 mil IC box -- same box machinery, smaller footprint so
    # more parts fit per sheet (owner request 2026-09-29). Height is 200mil
    # (half_h = PIN_PITCH), not the requested 150mil: 150mil (half_h=75mil)
    # is off the 50mil grid this generator's pins/wires all sit on and broke
    # ERC (endpoint_off_grid); 200mil is the nearest on-grid value and also
    # centers the single pin row exactly on the box (y=0).
    if n_pins <= 2:
        half_w = 7.62
        half_h = 2.54
    else:
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
                  "VCC2_CAN", "VCC2_RS485", "PGND",
                  "VCC2_CAN_DCDC", "GND2_CAN_DCDC", "VCC2_RS485_DCDC", "GND2_RS485_DCDC"]

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
    X0, Y0, DX = 76.2, 76.2, 63.5  # halved column pitch to match the smaller passive boxes
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
