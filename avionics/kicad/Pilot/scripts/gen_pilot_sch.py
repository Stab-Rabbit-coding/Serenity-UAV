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
* 2026-10-18 (Claude Opus 5.5; owner decisions S. Griffing 2026-10-17):
    - One JST-GH expansion port only (no second board-edge site): J-SPI becomes
      a 6-pin SM06B-GHS-TB (5V, SCK, MISO, MOSI, SS1, GND on the SPI2 pins; the
      same pins also mux to UART1 / UART6).  J-GPS, its PTC / bypass / I2C
      pull-ups / ESD array and the SS2 line are removed; P1-31/33/36 and
      P2-2/4 become spare.
    - Sourcing rule (AGENTS.md §5): the Nexperia PRTR5V0U2X (Nexperia is owned
      by PRC-domiciled Wingtech) at the CAN and RS-485 field connectors is
      replaced.  It was also the wrong clamp: a 5 V rail-referenced array holds
      the bus inside 0..5 V, far narrower than the ISOW1044 receiver's +/-12 V and
      the RS-485 -7..+12 V common-mode ranges.  Each TVS row now carries a
      ``Manufacturer`` property (new optional ``mfr`` flag).  CAN: TI
      ESD2CAN24-Q1, SC-70 (+/-24 V VRWM, 3 pF; the ISOW1044 bus pins are rated
      +/-58 V) [REF-SENSOR-053].  RS-485: Bourns
      CDSOT23-SM712 (-7 / +12 V VWM, the RS-485 common-mode range; the
      ISOW1412 bus pins are rated -12..+15 V) [REF-SENSOR-054].  The 1553
      SMAJ33CA now names a compliant manufacturer, Bourns [REF-SENSOR-055].
    - USB1 ring-leg NIC: WCH CH397A (PRC, AGENTS.md §5) -> ASIX AX88772E
      [REF-SENSOR-056], built to the ASIX demo board V1.01 [REF-SENSOR-058] and
      app note v1.10 [REF-SENSOR-057]: own 20 MHz ECS crystal (no external clock
      input), on-die 1.1 V buck with a 2.2 uH inductor, two BLM15EX331 beads, per-pin
      decoupling, RSET 24 k 1 %.  VBUS pin: 4.7 k pull-up plus P1-31 GPIO0_59 (owner).
      X-25M now clocks only the DP83825I.
* 2026-10-19 (Claude Opus 5.5; owner choice "smaller LAN magnetics"): each
  749010012A WE-LAN module (146 mm^2 courtyard) becomes two YAGEO/Pulse TC1G00
  PulseChip transformers, one per pair (1CT:1CT, 1500 Vac 60 s) [REF-SENSOR-061]:
  T-RMII2-TX/-RX and T-USB1-TX/-RX.  Same nets, so the centre-tap caps and the
  Bob-Smith networks are unchanged.

Datasheets (all in ``avionics/datasheets/``; OEM documents are authoritative
per ``avionics/AGENTS.md``):
  ISOW1044BDFMR isow1044.pdf Table 7-1 | ISOW1412DFMR isow1412.pdf Table 7-1 |
  SLB9672 slb9672.pdf §3.1.2 | BLM15EX331SN1D Murata_BLM15EX_JENF243A-0023M-01.pdf |
  DP83825I dp83825i.pdf Table 4-1/6-8..6-11, Fig 8-3/8-4 | 749010012A 749010012A.pdf p.1 |
  HI-6138 hi-6138_v-rev-s.pdf p.1/Table 1/§29 | PM-DB2791S PremierMagnetics_DB2791S.pdf | Samtec TSM samtec_tsm-dv-footprint.pdf |
  ICM-42688-P ds-000347 Table 10 | BMP388 bst-bmp388-ds001.pdf Table 50 |
  SRF2012A SRF2012A.pdf | TPSM828224SILR tpsm82822.pdf (SLVSEP0F) Table 6-1 |
  ECS-2520MV ECS-2520MV.pdf p.1 |
  X2Y (Yageo CX0805) X2Y_15-2237598.pdf Table 3 |
  ESD2CAN24-Q1 ESD2CANxx24-Q1_SLVSFW5D.pdf Table 4-1 | CDSOT23-SM712 Bourns_CDSOT23-SM712.pdf p.1 |
  SMAJ33CA Bourns_SMAJ.pdf (REV. 09/20) | TPD4E05U06 TPDxE05U06_SLVSBO7O.pdf Table 4-2 |
  AX88772E AX88772E_Datasheet_v103.pdf, AX88772E_Application_DesignNote_v110.pdf,
  AX88772E_DEMO_BOARD_SCHEMATIC_V101.pdf sheet 2 | ECS ECX-32 ECS_ECX-32.pdf |
  TC1G00 Pulse_TC002_PulseChip.pdf p.1-2.

Author: Claude Opus 4.8 (2026-07-14); Claude Opus 5 (2026-07-28, 2026-09-19);
Claude Opus 5.5 (2026-09-28, HI-6138 1553C swap; 2026-10-12, §13.1 beads + GNSS off-board;
2026-10-18, single GH port + compliant TVS).
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
FP_SOT323 = "Package_TO_SOT_SMD:SOT-323_SC-70"   # TI DCK (SC-70, 3)
FP_SOT23 = "Package_TO_SOT_SMD:SOT-23"           # JEDEC SOT23 (Bourns CDSOT23)
FP_OSC2520 = "Oscillator:Oscillator_SMD_ECS_2520MV-xxx-xx-4Pin_2.5x2.0mm"
FP_GH4 = "Connector_JST:JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal"
FP_GH6 = "Connector_JST:JST_GH_SM06B-GHS-TB_1x06-1MP_P1.25mm_Horizontal"
# AX88772E: matches the data sheet sec 6 recommended land (pads 0.22 x 0.71 mm, 2.90 mm
# E-pad, 3.30 mm inner span) to 0.02 mm [REF-SENSOR-056]
FP_QFN32_4X4 = "Package_DFN_QFN:QFN-32-1EP_4x4mm_P0.4mm_EP2.9x2.9mm"
FP_XTAL3225 = "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm"   # ECS ECX-32: pads 1/3 crystal, 2/4 GND
# 2.0 x 1.6 mm (0806) power-inductor land, placeholder until the L-USB1 MPN is chosen
FP_L2016 = "Inductor_SMD:L_Murata_DFE201610P"
FP_DQA10 = "Serenity-Custom:TI_DQA0010A_USON-10_2.5x1.0mm_P0.5mm"
FP_F0805 = "Fuse:Fuse_0805_2012Metric"
FP_HOLE = "Serenity-Custom:MountingHole_2.7mm_M2.5_PGND_Ring"
# project-custom lands (avionics/kicad/Serenity-Custom.pretty)
FP_SAM = "Serenity-Custom:uBlox_SAM-M10Q-00B"
FP_WELAN = "Serenity-Custom:Wurth_749010012A_WE-LAN"   # retired 2026-10-19 (TC1G00 chips)
FP_TC1G00 = "Serenity-Custom:Pulse_TC1G00_PulseChip_4.7x3.2mm"
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


def ax88772e(ref: str, eth: str) -> Dict[str, Any]:
    """ASIX AX88772E USB 2.0 to 10/100 Ethernet controller with integrated MAC + PHY,
    32-pin QFN 4 x 4 mm, 0.4 mm pitch, 2.7 mm E-pad.  Ring leg on the PB2-I's USB1
    (D+/D- on P1-11 / P1-9), bridged in Linux with the RMII2 leg (owner 2026-10-17).
    Replaces the CH397A (WCH is PRC-domiciled, AGENTS.md §5) on 2026-10-18; Claude
    Opus 5.5, owner decisions S. Griffing.

    Pinout: AX88772E data sheet v1.03 Fig. 1-2 / Tables 1-1..1-5 [REF-SENSOR-056].
    Supply tree per the ASIX demo board V1.01 sheet 2 [REF-SENSOR-058]: DVDD33 /
    AVDD33_BUCK on +3V3; LX (pin 12) drives the on-die 1.1 V buck through an external
    2.2 uH inductor to the DVDD11 pins; AVDD11_GBE behind a bead from DVDD11; the 3.3 V
    analog pins (AVDD33_USB / _XTAL / _GBE) behind a bead from +3V3.
    Clock: own 20 MHz crystal.  The part "does not support external oscillator clock
    source" (app note §5 note 2 [REF-SENSOR-057]), so it cannot share X-25M.
    MDI0 = transmit pair and MDI1 = receive pair, as wired to the RJ-45 TX/RX pins on the
    demo board (auto-MDIX is supported either way).  Device-side centre taps go to GND
    through 0.1 uF only (demo C4 / C7).
    VBUS (pin 6) is a 3.3 V attach/detach sense input (app note §4).  Owner 2026-10-18:
    4.7 k pull-up to +3V3 (demo R4) so the NIC attaches with no firmware, plus PB2-I
    GPIO P1-31 (GPIO0_59) on the same net so Linux can pull it low to force a USB
    detach / re-attach.  RST_N (internal pull-up + on-chip POR) and GPIO2/3/4 (no SPI
    flash or I2C EEPROM fitted) are left open, as on the demo board's default fit.
    LED_0 / LED_1 are left open (no LEDs on the cape).  The demo's LED pull-ups only
    serve its RJ-45 LEDs.
    """
    return {
        "ref": ref,
        "value": "AX88772EQF",
        "fp": FP_QFN32_4X4,
        "mpn": "AX88772EQF",
        "ds": "AX88772E data sheet v1.03 Tables 1-1..1-5 (QFN-32 4x4) [REF-SENSOR-056]",
        "pins": [
            ("2", "USB_DP", "USB1_DP", "L"),
            ("3", "USB_DM", "USB1_DM", "L"),
            ("6", "VBUS", f"{ref}_VBUS", "L"),
            ("7", "PU", f"{ref}_PU", "L"),
            ("8", "GPIO_8/PME", f"{ref}_PME", "L"),
            ("21", "RST_N", None, "L"),
            ("23", "XTAL_IN", f"{ref}_XI", "L"),
            ("24", "XTAL_OUT", f"{ref}_XO", "L"),
            ("26", "RSET", f"{ref}_RSET", "L"),
            ("15", "LED_0", None, "L"),
            ("16", "LED_1", None, "L"),
            ("17", "GPIO_2", None, "L"),
            ("19", "GPIO_3", None, "L"),
            ("20", "GPIO_4", None, "L"),
            ("9", "NC", None, "L"),
            ("27", "MDIP0", f"{eth}_TXP", "R"),
            ("28", "MDIN0", f"{eth}_TXN", "R"),
            ("30", "MDIP1", f"{eth}_RXP", "R"),
            ("31", "MDIN1", f"{eth}_RXN", "R"),
            ("12", "LX", f"{ref}_LX", "R"),
            ("13", "AVDD33_BUCK", "+3V3", "R"),
            ("14", "AVSS33_BUCK", "GND", "R"),
            ("5", "DVDD33", "+3V3", "R"),
            ("18", "DVDD33", "+3V3", "R"),
            ("1", "AVDD33_USB", f"{ref}_AVDD33", "R"),
            ("25", "AVDD33_XTAL", f"{ref}_AVDD33", "R"),
            ("29", "AVDD33_GBE", f"{ref}_AVDD33", "R"),
            ("4", "DVDD11", f"{ref}_DVDD11", "R"),
            ("10", "DVDD11", f"{ref}_DVDD11", "R"),
            ("11", "DVDD11", f"{ref}_DVDD11", "R"),
            ("22", "DVDD11", f"{ref}_DVDD11", "R"),
            ("32", "AVDD11_GBE", f"{ref}_AVDD11", "R"),
            ("33", "EP", "GND", "R"),
        ],
    }


def pulse_xfmr(ref: str, eth: str, pair: str) -> Dict[str, Any]:
    """YAGEO/Pulse TC1G00 PulseChip LAN transformer, one per pair (TC002.C (10/25)
    [REF-SENSOR-061]): 1CT:1CT, 240 uH min, 1500 Vac / 60 s isolation, -40..+85 C,
    4.70 x 3.20 x 3.15 mm.  Replaces the 749010012A WE-LAN modules on 2026-10-19
    (owner choice "smaller LAN magnetics"; Claude Opus 5.5): the two modules' 146 mm^2
    courtyards each could not leave room for the AX88772E cluster.  Like the WE-LAN it
    is transformer-only (no common-mode choke).

    Windings per the TC002.C schematic: 2 - (8/7) - 1 and 5 - (3/4) - 6, dots at 8 and 3,
    so 2 and 5 are like-phased; 8/7 and 3/4 are centre taps shorted on the PCB (one land
    pad each, named "7" and "3").  The 2/1 winding faces the PHY / NIC, 5/6 the line.
    ``pair`` is "TX" or "RX"; the net names match the old eth_xfmr() so the device-side
    centre-tap caps and the line-side Bob-Smith network are unchanged.
    """
    ct_dev, ct_line = ("CTD", "LINE_CTX") if pair == "TX" else ("CRD", "LINE_CRX")
    return {
        "ref": ref,
        "value": "TC1G00",
        "fp": FP_TC1G00,
        "mpn": "TC1G00",
        "mfr": "YAGEO (Pulse Electronics)",
        "ds": "TC002.C PulseChip LAN Transformer Overview p.1-2, Fig. A / Circuit A [REF-SENSOR-061]",
        "pins": [
            ("2", f"{pair}D+", f"{eth}_{pair}P", "L"),
            ("7", "CT_DEV", f"{eth}_{ct_dev}", "L"),
            ("1", f"{pair}D-", f"{eth}_{pair}N", "L"),
            ("5", f"{pair}L+", f"{eth}_LINE_{pair}P", "R"),
            ("3", "CT_LINE", f"{eth}_{ct_line}", "R"),
            ("6", f"{pair}L-", f"{eth}_LINE_{pair}N", "R"),
        ],
    }


ICS += [
    dp83825i("PHY-RMII2", "RMII2", "RMII2_PHY_RSTN", "RMII2_PHY_INTRN", "ETH_RMII2", "MDIO0", "MDC0"),
    ax88772e("NIC-USB1", "ETH_USB1"),
    pulse_xfmr("T-RMII2-TX", "ETH_RMII2", "TX"),
    pulse_xfmr("T-RMII2-RX", "ETH_RMII2", "RX"),
    pulse_xfmr("T-USB1-TX", "ETH_USB1", "TX"),
    pulse_xfmr("T-USB1-RX", "ETH_USB1", "RX"),
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
# PB2 console).  USB1 (P1-5 VBUS, P1-9 D-, P1-11 D+) carries ring port 2 (AX88772E); its
# DRVVBUS (P1-3) and ID (P1-13) balls are plain GPIO here, USB1 runs host-only.  P1-19/21/23/25/27 and P2-35/36 are also MSPM0 AIN inputs: the MSPM0
# must keep them high-impedance (firmware requirement).
# ---------------------------------------------------------------------------
PB2_P1 = [
    "+5V",            # 1  VIN 5 V in (cape powers the PB2-I)
    "RMII2_TX_EN",    # 2  AA19 RMII2_TX_EN (E18 GPIO1_10 left input)
    "SPI0_CS_IMU",    # 3  F18 GPIO1_51 (GPIO chip select, next to the IMU)
    "RMII2_TXD0",     # 4  Y18 RMII2_TXD0 (D20 left input)
    "+5V",            # 5  USB1_VBUS: cape-supplied VBUS (PB2-I divides 1k/20k to AB10)
    "EXT_SPI_SS1",    # 6  E19 SPI2_CS0 (AD18 left input)
    None,             # 7  VIN.USB
    "EXT_SPI_SCK",    # 8  A20 SPI2_CLK
    "USB1_DM",        # 9  AD10 USB1_DM -> AX88772E USB_DM
    "EXT_SPI_MISO",   # 10 B19 SPI2_D0 (A18 left input)
    "USB1_DP",        # 11 AE9 USB1_DP -> AX88772E USB_DP
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
    "NIC-USB1_VBUS",  # 31 Y22 GPIO0_59 — AX88772E VBUS detach over 4.7 k pull-up (owner)
    None,             # 32 D14 UART0_RXD — PB2 console, left free
    None,             # 33 A17 I2C1_SDA (AA23 left input) — spare (was J-GPS, removed 2026-10-18)
    "RMII2_REF_CLK",  # 34 AD23 RMII2_REF_CLK
    "RMII2_CRS_DV",   # 35 AE21 RMII2_CRS_DV
    None,             # 36 B17 I2C1_SCL (V20 left input) — spare (was J-GPS, removed 2026-10-18)
]
PB2_P2 = [
    "MDC0",           # 1  AD24 MDIO0_MDC (B20 left input)
    None,             # 2  U22 UART2_RXD — spare (was J-GPS, removed 2026-10-18)
    "MDIO0",          # 3  AB22 MDIO0_MDIO (B18 left input)
    None,             # 4  V24 UART2_TXD — spare (was J-GPS, removed 2026-10-18)
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
    # 2026-10-18: TI ESD2CAN24-Q1, SC-70 DCK (SLVSFW5D Table 4-1: IO 1, 2; GND 3).
    # +/-24 V VRWM clears the CAN common-mode range; 37 V clamp (5.7 A 8/20 us) sits
    # below the ISOW1044 +/-58 V bus rating (SLLSFF7A sec 8.1) [REF-SENSOR-053].
    ("TVS-CAN", "ESD2CAN24-Q1", FP_SOT323, "ESD2CAN24DCKRQ1",
     "Dual-line CAN TVS at the field connector, +/-24 V, 3 pF (TI SLVSFW5D) [REF-SENSOR-053]",
     [("1", "IO1", "CAN_H_F"), ("2", "IO2", "CAN_L_F"), ("3", "GND", "GND2_CAN")],
     {"mfr": "Texas Instruments"}),
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
    # 2026-10-18: Bourns CDSOT23-SM712 (lines on pins 1, 2; common pin 3 to GND2).
    # VWM -7 V / +12 V = the RS-485 common-mode range; VC 19 V at 1 A.  The ISOW1412
    # bus pins are rated -12..+15 V (SLLSF86C sec 8.1), so the part's own IEC
    # 61000-4-2 +/-8 kV bus protection and the CMC take the residual above the
    # clamp [REF-SENSOR-054] [REF-SENSOR-010].
    ("TVS-RS485", "CDSOT23-SM712", FP_SOT23, "CDSOT23-SM712",
     "Asymmetric -7/+12 V RS-485 TVS at the field connector (Bourns) [REF-SENSOR-054]",
     [("1", "IO1", "RS485_A_F"), ("2", "IO2", "RS485_B_F"), ("3", "COM", "GND2_RS485")],
     {"mfr": "Bourns"}),
    ("R-485T", "120R", FP_R0603, "", "RS-485 termination — populate ONLY at a bus end node (DNP default)",
     [("1", "A", "RS485_A_F"), ("2", "B", "RS485_B_F")], {"dnp": True}),
    ("RS-485", "SM04B-GHS-TB", FP_GH4, "SM04B-GHS-TB(LF)(SN)", "Pilot.md §14 J_485",
     [("1", "GND", "GND2_RS485"), ("2", "A", "RS485_A_F"), ("3", "B", "RS485_B_F"), ("4", "VCC", "VCC2_RS485"),
      ("MP", "SHIELD", "PGND")]),
    ("X2Y-RS485", "4.7nF X2Y", FP_X2Y0805, "CX0805MRX7R0BB472", "Pilot.md §3 GND1<->GND2 RF bridge (Yageo X2Y 0805)",
     [("1", "A", "GND"), ("2", "B", "GND"), ("3", "G1", "GND2_RS485"), ("4", "G2", "GND2_RS485")]),
    # --- Ethernet line-side connectors + Bob-Smith terminations ------------
    ("J-ETH-RMII2", "SM04B-GHS-TB", FP_GH4, "SM04B-GHS-TB(LF)(SN)", "J-ETH-RMII2 line pairs to the T-RMII2-TX / -RX line windings",
     [("1", "TXP", "ETH_RMII2_LINE_TXP"), ("2", "TXN", "ETH_RMII2_LINE_TXN"), ("3", "RXP", "ETH_RMII2_LINE_RXP"), ("4", "RXN", "ETH_RMII2_LINE_RXN"),
      ("MP", "SHIELD", "PGND")]),
    ("J-ETH-USB1", "SM04B-GHS-TB", FP_GH4, "SM04B-GHS-TB(LF)(SN)", "J-ETH-USB1 line pairs to the T-USB1-TX / -RX line windings",
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
    # 25 MHz oscillator for the DP83825I XI only (XO open); the AX88772E has its own crystal
    ("X-25M", "25MHz 3.3V", FP_OSC2520, "ECS-2520MV-250-BN-TR",
     "25 MHz reference for the DP83825I XI (RMII Leader, +/-50 ppm, SNLS638C); "
     "ECS-2520MV.pdf [REF-PWR-004]",
     [("1", "TRI", None), ("2", "GND", "GND"), ("3", "OUT", "XI_25M"), ("4", "VDD", "+3V3")]),
    ("C-25M", "100nF", FP_C0402, "", "oscillator VDD bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    # --- MIL-STD-1553B field port ------------------------------------------
    ("R-1553P", "55R 2%", FP_R0603, "", "MIL-STD-1553B §4.5.1.5.2 direct-coupled stub isolation resistor (hi-1573.pdf Fig 2)",
     [("1", "A", "M1553_SEC_P"), ("2", "B", "BUS_1553_P")]),
    ("R-1553N", "55R 2%", FP_R0603, "", "MIL-STD-1553B §4.5.1.5.2 direct-coupled stub isolation resistor",
     [("1", "A", "M1553_SEC_N"), ("2", "B", "BUS_1553_N")]),
    # Generic SMAJ33CA: manufacturer named per AGENTS.md §5 (2026-10-18) — Bourns, US.
    ("TVS-1553P", "SMAJ33CA", FP_SMA, "SMAJ33CA",
     "Pilot.md §5 bidirectional TVS, BUS_P to PGND [REF-SENSOR-055]",
     [("1", "A", "BUS_1553_P"), ("2", "K", "PGND")], {"mfr": "Bourns"}),
    ("TVS-1553N", "SMAJ33CA", FP_SMA, "SMAJ33CA",
     "Pilot.md §5 bidirectional TVS, BUS_N to PGND [REF-SENSOR-055]",
     [("1", "A", "BUS_1553_N"), ("2", "K", "PGND")], {"mfr": "Bourns"}),
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

# --- AX88772E support (ASIX demo board V1.01 sheet 2 [REF-SENSOR-058]; app note v1.10
# [REF-SENSOR-057]; owner 2026-10-18).  Demo designators in parentheses.  The app note
# §8 item 5 wants a decoupling capacitor on every power pin, so the demo's per-pin
# 0.1 uF set is kept; 0.1 uF goes in 0201 to save area.  Beads: the demo's Chilisin
# PBY160808T-110Y-N (110 R) has no datasheet on file, so the cape reuses the vetted
# Murata BLM15EX331SN1D (330 R at 100 MHz, 0.205 R max DCR, 1.1 A) [REF-SENSOR-043];
# the drop at the ~25 mA rail load is about 5 mV.  Crystal: the demo's "NSK 20M
# CRYSTAL" has no part number and no identifiable maker (AGENTS.md §5), so ECS
# ECS-200-20-33-AGM-TR (Lenexa KS; 20 MHz, CL 20 pF, +/-25 ppm tol, +/-30 ppm
# stability, -20..+70 C, ESR 60 R max; ECX-32 data sheet [REF-SENSOR-059]) meets the
# app note §5 spec (CL 20 pF, +/-30 ppm, ESR <= 100 R).  Smaller ECS packages list a
# CL of 8 pF typical, which the demo's 15 pF load caps cannot load to 20 pF.
SIMPLE += [
    # 1.1 V buck: LX -> L1 2.2 uH -> DVDD11 (demo L1, C2, C3; note 2-5: at pin 12)
    (
        "L-USB1",
        "2.2uH",
        FP_L2016,
        "",
        "AX88772E 1.1 V buck inductor, LX pin 12 (demo L1 2.2 uH 2016, Darfon IP20162R2MP59); "
        "MPN to be confirmed against a downloaded data sheet (avionics/WBS.md)",
        [("1", "A", "NIC-USB1_LX"), ("2", "B", "NIC-USB1_DVDD11")],
    ),
    (
        "C-USB1-LXB",
        "10uF 6.3V X5R",
        FP_C0603,
        "",
        "DVDD11 buck output bulk at pin 12 (demo C2)",
        [("1", "P", "NIC-USB1_DVDD11"), ("2", "N", "GND")],
    ),
    (
        "C-USB1-LXH",
        "100nF",
        FP_C0201,
        "",
        "DVDD11 buck output HF at pin 12 (demo C3)",
        [("1", "P", "NIC-USB1_DVDD11"), ("2", "N", "GND")],
    ),
    (
        "C-USB1-D04",
        "100nF",
        FP_C0201,
        "",
        "DVDD11 pin 4 (demo C20)",
        [("1", "P", "NIC-USB1_DVDD11"), ("2", "N", "GND")],
    ),
    (
        "C-USB1-D10",
        "100nF",
        FP_C0201,
        "",
        "DVDD11 pin 10 (demo C18)",
        [("1", "P", "NIC-USB1_DVDD11"), ("2", "N", "GND")],
    ),
    (
        "C-USB1-D11",
        "100nF",
        FP_C0201,
        "",
        "DVDD11 pin 11 (demo C24)",
        [("1", "P", "NIC-USB1_DVDD11"), ("2", "N", "GND")],
    ),
    (
        "C-USB1-D22",
        "100nF",
        FP_C0201,
        "",
        "DVDD11 pin 22 (demo C19)",
        [("1", "P", "NIC-USB1_DVDD11"), ("2", "N", "GND")],
    ),
    # AVDD11_GBE behind a bead (demo L4, C15, C14, C17)
    (
        "FB-USB1-A11",
        "330R@100MHz",
        FP_L0402,
        "BLM15EX331SN1D",
        "DVDD11 -> AVDD11_GBE bead (demo L4) [REF-SENSOR-043]",
        [("1", "A", "NIC-USB1_DVDD11"), ("2", "B", "NIC-USB1_AVDD11")],
    ),
    (
        "C-USB1-A11B",
        "10uF 6.3V X5R",
        FP_C0603,
        "",
        "AVDD11_GBE pin 32 bulk (demo C15)",
        [("1", "P", "NIC-USB1_AVDD11"), ("2", "N", "GND")],
    ),
    (
        "C-USB1-A11H1",
        "100nF",
        FP_C0201,
        "",
        "AVDD11_GBE pin 32 (demo C14)",
        [("1", "P", "NIC-USB1_AVDD11"), ("2", "N", "GND")],
    ),
    (
        "C-USB1-A11H2",
        "100nF",
        FP_C0201,
        "",
        "AVDD11_GBE pin 32 (demo C17)",
        [("1", "P", "NIC-USB1_AVDD11"), ("2", "N", "GND")],
    ),
    # 3.3 V: buck input at pin 13 (note 2-4), DVDD33 pins 5 / 18
    (
        "C-USB1-BKB",
        "4.7uF 10V X5R",
        FP_C0603,
        "",
        "AVDD33_BUCK pin 13 bulk (demo C5, note 2-4)",
        [("1", "P", "+3V3"), ("2", "N", "GND")],
    ),
    (
        "C-USB1-BKH",
        "100nF",
        FP_C0201,
        "",
        "AVDD33_BUCK pin 13 HF (demo C6, note 2-4)",
        [("1", "P", "+3V3"), ("2", "N", "GND")],
    ),
    (
        "C-USB1-IO5",
        "100nF",
        FP_C0201,
        "",
        "DVDD33 pin 5 (demo C23)",
        [("1", "P", "+3V3"), ("2", "N", "GND")],
    ),
    (
        "C-USB1-IO18",
        "100nF",
        FP_C0201,
        "",
        "DVDD33 pin 18 (demo C16)",
        [("1", "P", "+3V3"), ("2", "N", "GND")],
    ),
    # 3.3 V analog behind a bead (demo L5, C27, C21, C22, C25, C26)
    (
        "FB-USB1-A33",
        "330R@100MHz",
        FP_L0402,
        "BLM15EX331SN1D",
        "+3V3 -> AVDD33 analog bead (demo L5) [REF-SENSOR-043]",
        [("1", "A", "+3V3"), ("2", "B", "NIC-USB1_AVDD33")],
    ),
    (
        "C-USB1-A33B",
        "4.7uF 10V X5R",
        FP_C0603,
        "",
        "AVDD33 analog bulk (demo C27)",
        [("1", "P", "NIC-USB1_AVDD33"), ("2", "N", "GND")],
    ),
    (
        "C-USB1-A33H1",
        "100nF",
        FP_C0201,
        "",
        "AVDD33_USB pin 1 (demo C21)",
        [("1", "P", "NIC-USB1_AVDD33"), ("2", "N", "GND")],
    ),
    (
        "C-USB1-A33H2",
        "100nF",
        FP_C0201,
        "",
        "AVDD33_XTAL pin 25 (demo C22)",
        [("1", "P", "NIC-USB1_AVDD33"), ("2", "N", "GND")],
    ),
    (
        "C-USB1-A33H3",
        "100nF",
        FP_C0201,
        "",
        "AVDD33_GBE pin 29 (demo C25)",
        [("1", "P", "NIC-USB1_AVDD33"), ("2", "N", "GND")],
    ),
    (
        "C-USB1-A33H4",
        "100nF",
        FP_C0201,
        "",
        "AVDD33 bead output (demo C26)",
        [("1", "P", "NIC-USB1_AVDD33"), ("2", "N", "GND")],
    ),
    # 20 MHz crystal: XTAL_IN on pad 1; XTAL_OUT through 200 R to pad 3 (demo Y1, C11, C12, R7)
    (
        "Y-USB1",
        "20MHz CL20pF",
        FP_XTAL3225,
        "ECS-200-20-33-AGM-TR",
        "AX88772E 20 MHz crystal, ECX-32: CL 20 pF, +/-25 ppm, +/-30 ppm, ESR 60 R max "
        "(app note §5) [REF-SENSOR-059]",
        [
            ("1", "X1", "NIC-USB1_XI"),
            ("2", "GND", "GND"),
            ("3", "X2", "NIC-USB1_XO_R"),
            ("4", "GND", "GND"),
        ],
        {"mfr": "ECS Inc."},
    ),
    (
        "C-USB1-XI",
        "15pF C0G",
        FP_C0402,
        "",
        "XTAL_IN load cap (demo C11; trim per app note §5 note 1)",
        [("1", "P", "NIC-USB1_XI"), ("2", "N", "GND")],
    ),
    (
        "C-USB1-XO",
        "15pF C0G",
        FP_C0402,
        "",
        "XTAL_OUT load cap, crystal side of R-USB1-XO (demo C12)",
        [("1", "P", "NIC-USB1_XO_R"), ("2", "N", "GND")],
    ),
    (
        "R-USB1-XO",
        "200R",
        FP_R0402,
        "",
        "XTAL_OUT drive-level resistor (demo R7)",
        [("1", "A", "NIC-USB1_XO"), ("2", "B", "NIC-USB1_XO_R")],
    ),
    # bias and straps
    (
        "R-USB1-RSET",
        "24k 1%",
        FP_R0402,
        "",
        "RSET pin 26 to analog GND, 24 kOhm 1 % (data sheet Table 1-4; demo note 2-8)",
        [("1", "A", "NIC-USB1_RSET"), ("2", "B", "GND")],
    ),
    (
        "R-USB1-VBUS",
        "4.7k",
        FP_R0201,
        "",
        "VBUS pin 6 pull-up to 3.3 V (demo R4); PB2-I P1-31 GPIO0_59 can pull it low "
        "(owner 2026-10-18)",
        [("1", "A", "+3V3"), ("2", "B", "NIC-USB1_VBUS")],
    ),
    (
        "R-USB1-PU",
        "4.7k",
        FP_R0201,
        "",
        "PU pin 7 pull-up to 3.3 V (data sheet Table 1-4; demo R3)",
        [("1", "A", "+3V3"), ("2", "B", "NIC-USB1_PU")],
    ),
    (
        "R-USB1-PME",
        "4.7k",
        FP_R0201,
        "",
        "GPIO_8/PME pin 8 must be pulled high (demo note 2-7, R2)",
        [("1", "A", "+3V3"), ("2", "B", "NIC-USB1_PME")],
    ),
    # device-side transformer centre taps: 0.1 uF to GND, no supply (demo C4, C7)
    (
        "C-USB1-CTD",
        "100nF",
        FP_C0402,
        "",
        "T-USB1-TX device-side centre tap to GND (demo C7)",
        [("1", "P", "ETH_USB1_CTD"), ("2", "N", "GND")],
    ),
    (
        "C-USB1-CRD",
        "100nF",
        FP_C0402,
        "",
        "T-USB1-RX device-side centre tap to GND (demo C4)",
        [("1", "P", "ETH_USB1_CRD"), ("2", "N", "GND")],
    ),
]

# --- JST-GH expansion port replacing the GNSS (owner 2026-10-17) ----------------------
# ONE port: the placer found a single free board-edge site, so J-GPS was dropped and
# J-SPI reduced to 6 pins (owner allowed 2026-10-17; avionics/WBS.md §1.2a Pilot).
# Pin order follows Pixhawk DS-009 rev 0.1.0 [REF-CONN-002] "SPI port" minus !SS2
# (pin-compatible only; this is not a Pixhawk-branded product).  All four signals sit on
# SPI2 balls that also mux to UART1 / UART6 (SCK = UART1_TX, MISO = UART6_RX, MOSI =
# UART6_TX, SS1 = UART1_RX; PB2I_AM625_HEADER_CAPABILITIES.md §4), so the port serves an
# SPI or a UART peripheral (e.g. an external GNSS) by device-tree mux alone.  Deviation:
# VCC is the cape +5V through a 0.35 A PTC, not DS-009's 2.5 A, because +5V feeds the
# PB2-I (VIN, 1 A) and the 3V3 module through FB1 (2 A).  ESD on every signal at the
# connector (TI TPD4E05U06, SLVSBO7O [REF-SENSOR-044]).
SIMPLE += [
    ("J-SPI", "SM06B-GHS-TB", FP_GH6, "SM06B-GHS-TB(LF)(SN)",
     "Expansion port, DS-009 SPI order less SS2: 5V, SCK, MISO, MOSI, !SS1, GND (eGH.pdf)",
     [("1", "VCC", "EXT_SPI_5V"), ("2", "SCK", "EXT_SPI_SCK"), ("3", "MISO", "EXT_SPI_MISO"), ("4", "MOSI", "EXT_SPI_MOSI"),
      ("5", "SS1", "EXT_SPI_SS1"), ("6", "GND", "GND"), ("MP", "SHIELD", "PGND")]),
    ("F-SPI", "MF-PSMF035X", FP_F0805, "MF-PSMF035X-2", "SPI port VCC PTC, 0.35 A hold / 0.75 A trip (Bourns MF-PSMF) [REF-PWR-013]",
     [("1", "A", "+5V"), ("2", "B", "EXT_SPI_5V")]),
    ("C-SPI5", "1uF 10V", FP_C0402, "", "SPI port VCC bypass at the connector", [("1", "P", "EXT_SPI_5V"), ("2", "N", "GND")]),
    ("ESD-SPI", "TPD4E05U06DQAR", FP_DQA10, "TPD4E05U06DQAR", "SPI port ESD, 4 ch (SLVSBO7O Table 4-2) [REF-SENSOR-044]",
     [("1", "D1+", "EXT_SPI_SCK"), ("2", "D1-", "EXT_SPI_MISO"), ("3", "GND", "GND"), ("4", "D2+", "EXT_SPI_MOSI"),
      ("5", "D2-", "EXT_SPI_SS1"), ("6", "NC", None), ("7", "NC", None), ("8", "GND", "GND"), ("9", "NC", None), ("10", "NC", None)]),
]

for _entry in SIMPLE:
    _ref, _val, _fp, _mpn, _ds, _pins = _entry[:6]
    _flags = _entry[6] if len(_entry) > 6 else {}
    _n = len(_pins)
    _half = (_n + 1) // 2
    ICS.append({
        "ref": _ref, "value": _val, "fp": _fp, "mpn": _mpn, "ds": _ds,
        "dnp": bool(_flags.get("dnp")),
        "mfr": _flags.get("mfr", ""),
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
    # Manufacturer of record, emitted only where set: a generic part number (e.g.
    # SMAJ33CA) meets the AGENTS.md §5 sourcing rule only once its maker is named.
    if ic.get("mfr"):
        out.append(
            f'    (property "Manufacturer" "{esc(ic["mfr"])}" (at {X:.2f} {Y:.2f} 0) '
            f'(effects (font (size {SIZE} {SIZE})) (hide yes)))'
        )
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
