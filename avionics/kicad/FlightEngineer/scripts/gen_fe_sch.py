#!/usr/bin/env python3
"""gen_fe_sch.py — Author the datasheet-accurate FlightEngineer power-distribution
schematic, from scratch, using the same schematic-first method as
Pilot/XO (``gen_pilot_sch.py`` / ``gen_xo_sch.py``).

Why a from-scratch rebuild: the checked-in ``FlightEngineer.kicad_sch`` carries 586
ERC violations, and the board's own doc says ``gen_flight_engineer.py`` (the prior
generator) "has drifted from the checked-in generator and is not safe to
regenerate from" — regenerating from it reproduces ~247 pre-existing errors
even before Section H (trust module). Patching forward a drifted 97 KB
generator was judged riskier than a clean rebuild against
``FlightEngineer.md``'s own detailed BOM/schematic-description tables, which are
unusually complete (real MPNs, real connections) and made this tractable.

Scope
-----
Full "Section A-G" power path (battery input EMI filter, main bus fusing/
sensing/protection, 4x isolated ESC branches, dual-redundant 5V BEC,
single-channel 6V BEC, BQ76930 6S cell monitor) plus "Section H" trust module
(MSPM0G3518-Q1 RHB-32 MCU, SLB9672 TPM, ISOW1044BDFMR isolated CAN-FD,
ISOW1412 isolated RS-485) — the CURRENT as-built trust module target per
FlightEngineer.md's 2026-08-03 retarget note, not the superseded MSPM0G3507/
SLB9670 the old injector script still names.

One part-number defect found in FlightEngineer.md's own BOM and corrected
(flagged, not silently fixed): "AON6556" (Q_BATT_DSG, cited as "N-MOSFET 60V/
30A") does not exist in AOSMD's catalog — AOSMD's 30V AlphaMOS family (AON6554/
6558) tops out at 30V, and no 60V "AON6556" was found. Substituted with
AON6260, a REAL AOSMD 60V/85A DFN5x6 N-channel MOSFET (comfortably exceeds
the 30A/60V requirement) — NEEDS owner confirmation.

Two BOM parts are confirmed real via manufacturer/distributor product-catalog
search but their datasheet PDFs could not be fetched this pass (every mirror
tried returned an HTML block page, not a PDF) — MBRD1045CT (onsemi dual
Schottky, 10A/45V, D2PAK-3, common-cathode) and SMBJ33CA (TVS, SMB/DO-214AA,
33V standoff). Standard, well-established pinouts for these package families
are used (matching Pilot/XO's own SMAJ33CA convention for the TVS); flagged
for a follow-up datasheet fetch, not a fabrication.

The RHB-32 MCU pinmux and the TPM/CAN-FD isolator pin maps are taken directly
from ``avionics/kicad/retarget_mspm0g351x_slb9672.py``'s own
``FLIGHT_ENGINEER_REMAP`` / ``FLIGHT_ENGINEER_TPM_NETS`` tables (that script's
own remap was independently verified against the MSPM0G3518-Q1 datasheet,
SLASFA6B Table 6-2 — reused here rather than re-derived, to avoid
transcription risk on a 1500-line pin-attribute table). ISOW1044BDFMR,
ISOW1412DFMR, and SLB9672 pin tables are reused verbatim from Pilot's
already-verified ``gen_pilot_sch.py`` (identical parts, identical datasheets).

Datasheets (all in ``avionics/datasheets/``):
  TPS54620 tps54620.pdf Pin Functions (VQFN-14) | TPS54540 tps54540.pdf Pin
  Functions (SO PowerPAD-8) | INA226 ina226.pdf Table 4-1 (VSSOP-10) | BQ76930
  bq76930.pdf §6.3/Table 9-3 (TSSOP-30) | AON6260 aon6260.pdf (DFN5x6-8L,
  standard AOSMD S/G/D convention) | MSPM0G3518-Q1 mspm0g3518-q1.pdf Table 6-2
  (RHB-32) via retarget_mspm0g351x_slb9672.py's verified remap | SLB9672/
  ISOW1044BDFMR/ISOW1412DFMR — see gen_pilot_sch.py docstring.

Author: Claude Sonnet 5, 2026-09-20.  Human owner: sgriffing (Griffing
Technology LLC).  License: CC BY 4.0.
"""

from __future__ import annotations

import itertools
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "kicads" / "FlightEngineer.kicad_sch"
SYMLIB = HERE.parent / "kicads" / "FlightEngineer.kicad_sym"

SIZE = 1.27
PIN_PITCH = 2.54
STUB = 2.54
_uid = itertools.count(1)

# --- footprint library nicknames -------------------------------------------
FP_C0402 = "Capacitor_SMD:C_0402_1005Metric"
FP_C0603 = "Capacitor_SMD:C_0603_1608Metric"
FP_C0805 = "Capacitor_SMD:C_0805_2012Metric"
FP_C1210 = "Capacitor_SMD:C_1210_3225Metric"
FP_CRAD_D10 = "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm"
FP_CRAD_D10x20 = "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm"
FP_R0402 = "Resistor_SMD:R_0402_1005Metric"
FP_R0603 = "Resistor_SMD:R_0603_1608Metric"
FP_L_IND = "Inductor_SMD:L_1210_3225Metric"
FP_SMB = "Diode_SMD:D_SMB"
FP_D2PAK = "Package_TO_SOT_SMD:TO-263-3_TabPin2"
FP_DFN5X6 = "Serenity-Custom:AOSMD_DFN5x6-8L"
FP_VQFN14 = "Serenity-Custom:Texas_RGY0014A_VQFN-14-1EP_3.5x3.5mm"
FP_SO_PP8 = "Package_SO:TI_SO-PowerPAD-8"
FP_VSSOP10 = "Package_SO:VSSOP-10_3x3mm_P0.5mm"
FP_TSSOP30 = "Package_SO:TSSOP-30_4.4x7.8mm_P0.5mm"
FP_MCU_RHB32 = "Package_DFN_QFN:Texas_RHB0032E_VQFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm"
FP_TPM_QFN32 = "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.6x3.6mm"
FP_SOIC20W = "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm"
FP_XT30 = "Connector_AMASS:AMASS_XT30PW-F_1x02_P2.50mm_Horizontal"
FP_XT60 = "Connector_AMASS:AMASS_XT60PW-F_1x02_P7.20mm_Horizontal"
FP_NANOFIT4 = "Connector_Molex:Molex_Nano-Fit_105309-xx04_1x04_P2.50mm_Vertical"
FP_GH2 = "Connector_JST:JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal"
FP_GH3 = "Connector_JST:JST_GH_SM03B-GHS-TB_1x03-1MP_P1.25mm_Horizontal"
FP_GH4 = "Connector_JST:JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal"
FP_XH7 = "Connector_JST:JST_XH_B7B-XH-A_1x07_P2.50mm_Vertical"
FP_MINIBLADE = "Fuse:Fuseholder_Blade_Mini_Keystone_3568"
FP_MAXIBLADE = "Serenity-Custom:MAXI_Blade_Fuseholder_2P"
FP_KELVIN2512 = "Resistor_SMD:R_Shunt_Vishay_WSK2512_6332Metric_T1.19mm"
FP_CMC_THT = "Serenity-Custom:Wurth_7440640500_CMC_THT"
FP_M3LUG = "Serenity-Custom:M3_Chassis_Lug_PGND"
FP_PGNDVIA = "Serenity-Custom:PGND_ViaPad_1p2mm"
FP_SOT23 = "Package_TO_SOT_SMD:SOT-23"


def uid() -> str:
    return f"fe000000-0000-0000-0000-{next(_uid):012d}"


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def sanitize(ref: str) -> str:
    return re.sub(r"[^A-Za-z0-9_+.-]", "_", ref)


# ---------------------------------------------------------------------------
ICS: List[Dict[str, Any]] = [
    {
        "ref": "U_IS_MAIN", "value": "INA226AIDGSR", "fp": FP_VSSOP10, "mpn": "INA226AIDGSR",
        "ds": "ina226.pdf Table 4-1 (VSSOP-10) [REF-SENSOR-039]. Addr 0x44 (A1=VCC,A0=GND) main bus, 75A FS.",
        "pins": [
            ("1", "A1", "+5V", "L"), ("2", "A0", "GND", "L"), ("3", "Alert", None, "L"),
            ("4", "SDA", "I2C_SDA", "L"),
            ("5", "SCL", "I2C_SCL", "R"), ("6", "VS", "+5V", "R"), ("7", "GND", "GND", "R"),
            ("8", "VBUS", "VDIS", "R"), ("9", "IN-", "SHUNT_MAIN_N", "R"), ("10", "IN+", "SHUNT_MAIN_P", "R"),
        ],
    },
    {
        "ref": "U_CELL", "value": "BQ76930PWRQ1", "fp": FP_TSSOP30, "mpn": "BQ76930PWRQ1",
        "ds": "bq76930.pdf §6.3 Pin Diagram (30-TSSOP) / Table 9-3 6-cell config [REF-SENSOR-040]",
        "pins": [
            ("1", "DSG", "BATT_DSG_GATE", "L"), ("2", "CHG", "CELL_CHG_GATE", "L"), ("3", "VSS", "PGND", "L"),
            ("4", "SDA", "I2C_SDA", "L"), ("5", "SCL", "I2C_SCL", "L"), ("6", "TS1", "NTC_P", "L"),
            ("7", "CAP1", "CELL_CAP1", "L"), ("8", "REGOUT", "CELL_REGOUT", "L"), ("9", "REGSRC", "VBAT", "L"),
            ("10", "VC5x", "CELL_B5", "L"), ("11", "NC", "CELL_CAP2", "L"), ("12", "NC", "CELL_CAP2", "L"),
            ("13", "TS2", "PGND", "L"), ("14", "CAP2", "CELL_CAP2", "L"), ("15", "BAT", "VBAT", "L"),
            ("30", "ALERT", "CELL_ALERT_N", "R"), ("29", "SRN", "SHUNT_MAIN_N", "R"), ("28", "SRP", "SHUNT_MAIN_P", "R"),
            ("27", "VC0", "CELL_B0", "R"), ("26", "VC1", "CELL_B1", "R"), ("25", "VC2", "CELL_B2", "R"),
            ("24", "VC3", "CELL_B3", "R"), ("23", "VC4", "CELL_B4", "R"), ("22", "VC5", "CELL_B5", "R"),
            ("21", "VC5B", "CELL_B5", "R"), ("20", "VC6", "CELL_B6", "R"), ("19", "VC7", "CELL_B6", "R"),
            ("18", "VC8", "CELL_B6", "R"), ("17", "VC9", "CELL_B6", "R"), ("16", "VC10", "CELL_B6", "R"),
        ],
    },
    {
        "ref": "Q_BATT_DSG", "value": "AON6260", "fp": FP_DFN5X6, "mpn": "AON6260",
        "ds": "aon6260.pdf (DFN5x6-8L, 60V/85A) [REF-PWR-005] — substituted for FlightEngineer.md's fabricated "
              "\"AON6556\" (no such AOSMD part exists; AOSMD's 30V family tops out with AON6554/6558, no 60V "
              "\"6556\" found). AON6260 is real, 60V/85A, exceeds the 30A/60V requirement — NEEDS confirmation.",
        "pins": [
            ("1", "S", "VDIS", "L"), ("2", "S", "VDIS", "L"), ("3", "S", "VDIS", "L"),
            ("4", "G", "BATT_DSG_GATE_R", "L"),
            ("5", "D", "VBAT", "R"), ("6", "D", "VBAT", "R"), ("7", "D", "VBAT", "R"), ("8", "D", "VBAT", "R"),
        ],
    },
    {
        "ref": "Q_BATT_CHG", "value": "AON6260 (DNP)", "fp": FP_DFN5X6, "mpn": "AON6260",
        "ds": "FlightEngineer.md CHG path — DNP/future per doc (\"Q_BATT_CHG gate (future / DNP)\")",
        "dnp": True,
        "pins": [
            ("1", "S", "VBAT", "L"), ("2", "S", "VBAT", "L"), ("3", "S", "VBAT", "L"),
            ("4", "G", "CELL_CHG_GATE", "L"),
            ("5", "D", "VBAT", "R"), ("6", "D", "VBAT", "R"), ("7", "D", "VBAT", "R"), ("8", "D", "VBAT", "R"),
        ],
    },
    {
        "ref": "U_BEC_5V_1", "value": "TPS54620RGYT", "fp": FP_VQFN14, "mpn": "TPS54620RGYT",
        "ds": "tps54620.pdf Pin Functions (VQFN-14 RGY) [REF-PWR-006]. 5.3V setpoint (Schottky-OR drop budget).",
        "pins": [
            ("1", "RT/CLK", "GND", "L"), ("2", "GND", "GND", "L"), ("3", "GND", "GND", "L"),
            ("4", "PVIN", "VDIS", "L"), ("5", "PVIN", "VDIS", "L"), ("6", "VIN", "VDIS", "L"), ("7", "VSENSE", "BEC1_FB", "L"),
            ("8", "COMP", "BEC1_COMP", "R"), ("9", "SS/TR", "BEC1_SS", "R"), ("10", "EN", "+3V3_BIAS_EN", "R"),
            ("11", "PH", "BEC1_SW", "R"), ("12", "PH", "BEC1_SW", "R"), ("13", "BOOT", "BEC1_BOOT", "R"), ("14", "PWRGD", None, "R"),
            ("15", "EP", "GND", "R"),
        ],
    },
    {
        "ref": "U_BEC_5V_2", "value": "TPS54620RGYT", "fp": FP_VQFN14, "mpn": "TPS54620RGYT",
        "ds": "tps54620.pdf Pin Functions (VQFN-14 RGY) — identical to U_BEC_5V_1 (dual-redundant OR'd pair)",
        "pins": [
            ("1", "RT/CLK", "GND", "L"), ("2", "GND", "GND", "L"), ("3", "GND", "GND", "L"),
            ("4", "PVIN", "VDIS", "L"), ("5", "PVIN", "VDIS", "L"), ("6", "VIN", "VDIS", "L"), ("7", "VSENSE", "BEC2_FB", "L"),
            ("8", "COMP", "BEC2_COMP", "R"), ("9", "SS/TR", "BEC2_SS", "R"), ("10", "EN", "+3V3_BIAS_EN", "R"),
            ("11", "PH", "BEC2_SW", "R"), ("12", "PH", "BEC2_SW", "R"), ("13", "BOOT", "BEC2_BOOT", "R"), ("14", "PWRGD", None, "R"),
            ("15", "EP", "GND", "R"),
        ],
    },
    {
        "ref": "U_BEC_6V", "value": "TPS54540DDAR", "fp": FP_SO_PP8, "mpn": "TPS54540DDAR",
        "ds": "tps54540.pdf Pin Functions (SO PowerPAD-8) [REF-PWR-007]. 6.0V +/-1% setpoint.",
        "pins": [
            ("2", "VIN", "VDIS", "L"), ("3", "EN", "+3V3_BIAS_EN", "L"), ("4", "RT/CLK", "GND", "L"), ("5", "FB", "BEC6_FB", "L"),
            ("6", "COMP", "BEC6_COMP", "R"), ("1", "BOOT", "BEC6_BOOT", "R"), ("8", "SW", "BEC6_SW", "R"), ("7", "GND", "GND", "R"),
            ("9", "EP", "GND", "R"),
        ],
    },
]


def isow1044(ref: str, tx: str, rx: str, stb_net: str, can_h: str, can_l: str, gnd2: str, vcc2: str) -> Dict[str, Any]:
    """TI ISOW1044BDFMR — identical part/pin table to Pilot's CAN-TR (isow1044.pdf Table 7-1)."""
    return {
        "ref": ref, "value": "ISOW1044BDFMR", "fp": FP_SOIC20W, "mpn": "ISOW1044BDFMR",
        "ds": "isow1044.pdf Fig 7-1 / Table 7-1 (20-pin DFM) [REF-SENSOR-009]; same part as Pilot CAN-TR",
        "pins": [
            ("1", "VIO", "+3V3", "L"), ("2", "IN", None, "L"), ("3", "TXD", tx, "L"), ("4", "STB", stb_net, "L"),
            ("5", "RXD", rx, "L"), ("6", "GNDIO", "GND", "L"), ("7", "NC", None, "L"), ("8", "EN/FLT", None, "L"),
            ("9", "VDD", "+5V", "L"), ("10", "GND1", "GND", "L"),
            ("20", "VISOIN", vcc2, "R"), ("19", "CANH", can_h, "R"), ("18", "CANL", can_l, "R"),
            ("17", "GISOIN", gnd2, "R"), ("16", "GISOIN", gnd2, "R"), ("15", "GISOIN", gnd2, "R"),
            ("14", "OUT", None, "R"), ("13", "VSIN", vcc2, "R"), ("12", "VISOOUT", vcc2, "R"), ("11", "GND2", gnd2, "R"),
        ],
    }


def isow1412(ref: str, tx: str, rx: str, de: str, a: str, b: str, gnd2: str, vcc2: str, flt: str) -> Dict[str, Any]:
    """TI ISOW1412DFMR — identical part/pin table to Pilot's RS485 (isow1412.pdf Table 7-1). Unlike Pilot
    (EN/FLT tied to +3V3, no fault monitoring), FlightEngineer's MCU has a spare RS485_FLT_N GPIO
    (freed by the RHB-32 pinmux), so EN/FLT is wired to it (pulled up externally) for real enable/fault
    control instead of being hard-tied."""
    return {
        "ref": ref, "value": "ISOW1412DFMR", "fp": FP_SOIC20W, "mpn": "ISOW1412DFMR",
        "ds": "isow1412.pdf Table 7-1 (20-pin DFM) [REF-SENSOR-010]; same part as Pilot RS485",
        "pins": [
            ("1", "VIO", "+3V3", "L"), ("2", "D", tx, "L"), ("3", "DE", de, "L"), ("4", "R", rx, "L"),
            ("5", "RE", de, "L"), ("6", "GNDIO", "GND", "L"), ("7", "OUT", None, "L"), ("8", "EN/FLT", flt, "L"),
            ("9", "VDD", "+5V", "L"), ("10", "GND1", "GND", "L"),
            ("20", "A", a, "R"), ("19", "B", b, "R"), ("18", "Z", b, "R"), ("17", "Y", a, "R"),
            ("16", "VISOIN", vcc2, "R"), ("15", "GISOIN", gnd2, "R"), ("14", "IN", None, "R"),
            ("13", "MODE", gnd2, "R"), ("12", "VISOOUT", vcc2, "R"), ("11", "GND2", gnd2, "R"),
        ],
    }


ICS += [
    isow1044("U_ISOCAN", "CANFD_TX", "CANFD_RX", "CANFD_STB", "CAN_H", "CAN_L", "ISO_GND_CAN", "ISO_5V_CAN"),
    isow1412("U_RS485", "RS485_TX", "RS485_RX", "RS485_DE", "RS485_A", "RS485_B", "ISO_GND_485", "ISO_5V_485", "RS485_FLT_N"),
    {
        "ref": "U_TPM", "value": "SLB9672XU20", "fp": FP_TPM_QFN32, "mpn": "SLB9672XU20FW1611XUMA1",
        "ds": "slb9672.pdf §3.1.2 Tables 11-13 / Figure 6 (PG-UQFN-32) [REF-SENSOR-011]; same part as Pilot TPM. "
              "Net names match FLIGHT_ENGINEER_TPM_NETS in retarget_mspm0g351x_slb9672.py (authoritative for this board).",
        "pins": [
            ("17", "RST#", "TPM_RESET_N", "L"), ("18", "PIRQ#", "TPM_PIRQ", "L"), ("19", "SCLK", "TPM_SPI_SCK", "L"),
            ("20", "CS#", "TPM_SPI_CS", "L"), ("21", "MOSI", "TPM_SPI_MOSI", "L"), ("24", "MISO", "TPM_SPI_MISO", "L"),
            ("3", "GPIO_00", None, "L"), ("4", "GPIO_01", None, "L"), ("7", "GPIO_02", None, "L"),
            ("1", "VDD", "+3V3", "R"), ("14", "VDD", "+3V3", "R"), ("22", "VDD", "+3V3", "R"),
            ("2", "GND", "PGND", "R"), ("9", "GND", "PGND", "R"), ("23", "GND", "PGND", "R"), ("32", "GND", "PGND", "R"),
            ("16", "NCI/GND", "PGND", "R"), ("33", "EP", "PGND", "R"),
            ("10", "NCI/VDD", "TPM_P10_PU", "R"), ("8", "NCI/VDD", None, "R"),
            ("6", "NC", None, "R"), ("29", "NC", None, "R"), ("30", "NC", None, "R"),
            ("5", "NCI", None, "R"), ("11", "NCI", None, "R"), ("12", "NCI", None, "R"), ("13", "NCI", None, "R"),
            ("15", "NCI", None, "R"), ("25", "NCI", None, "R"), ("26", "NCI", None, "R"), ("27", "NCI", None, "R"),
            ("28", "NCI", None, "R"), ("31", "NCI", None, "R"),
        ],
    },
    {
        "ref": "U_MCU", "value": "MSPM0G3518-Q1", "fp": FP_MCU_RHB32, "mpn": "M0G3518QRHBRQ1",
        "ds": "mspm0g3518-q1.pdf Table 6-2 (RHB-32) [REF-SENSOR-017] — pinmux per "
              "retarget_mspm0g351x_slb9672.py FLIGHT_ENGINEER_REMAP (independently verified against this "
              "datasheet already; reused here rather than re-derived).",
        "pins": [
            ("1", "PA0/I2C0_SDA", "I2C_SDA", "L"), ("2", "PA1/I2C0_SCL", "I2C_SCL", "L"), ("3", "NRST", "MCU_NRST", "L"),
            ("4", "+3V3", "+3V3", "L"), ("5", "GND", "PGND", "L"),
            ("6", "PA2/SPI0_CS", "TPM_SPI_CS", "L"), ("7", "PA3/GPIO", "TPM_PIRQ", "L"),
            ("8", "PA4/SPI0_MISO", "TPM_SPI_MISO", "L"), ("9", "PA5/SPI0_MOSI", "TPM_SPI_MOSI", "L"),
            ("10", "PA6/SPI0_SCK", "TPM_SPI_SCK", "L"), ("11", "PA7/GPIO", "TPM_RESET_N", "L"),
            ("12", "PA8/UART1_TX", "RS485_TX", "R"), ("13", "PA9/UART1_RX", "RS485_RX", "R"),
            ("16", "PA12/CAN0_TX", "CANFD_TX", "R"), ("17", "PA13/CAN0_RX", "CANFD_RX", "R"),
            ("23", "PA20/SWDIO", "MCU_SWDIO", "R"), ("24", "PA21b/SWCLK", "MCU_SWCLK", "R"),
            ("25", "PA21/GPIO", "RS485_DE", "R"), ("26", "PA22/GPIO", "RS485_FLT_N", "R"), ("27", "PA23/GPIO", "CANFD_STB", "R"),
            ("32", "VCORE", "MCU_VCORE", "R"), ("33", "EP", "PGND", "R"),
        ],
    },
]

# ---------------------------------------------------------------------------
# ESC branches (x4, identical) — INA226 x4 + Kelvin shunt + CM choke + bulk cap
# ---------------------------------------------------------------------------
ESC_ADDR = {1: ("GND", "GND"), 2: ("+5V", "GND"), 3: ("I2C_SDA", "GND"), 4: ("I2C_SCL", "GND")}
for _i in range(1, 5):
    ICS.append({
        "ref": f"U_IS{_i}", "value": "INA226AIDGSR", "fp": FP_VSSOP10, "mpn": "INA226AIDGSR",
        "ds": f"ina226.pdf Table 4-1 (VSSOP-10) [REF-SENSOR-039]. ESC{_i} branch, addr 0x{0x3F+_i:02x}, 60A FS.",
        "pins": [
            ("1", "A1", ESC_ADDR[_i][1], "L"), ("2", "A0", ESC_ADDR[_i][0], "L"), ("3", "Alert", None, "L"),
            ("4", "SDA", "I2C_SDA", "L"),
            ("5", "SCL", "I2C_SCL", "R"), ("6", "VS", "+5V", "R"), ("7", "GND", "GND", "R"),
            ("8", "VBUS", "VDIS", "R"), ("9", "IN-", f"SHUNT{_i}_N", "R"), ("10", "IN+", f"SHUNT{_i}_P", "R"),
        ],
    })

# ---------------------------------------------------------------------------
# PocketBeagle 2 was never on this board (it's the power/monitoring node, not
# an SBC cape) — no PB2 header here. Pilot's/XO's PB2_P1/P2 pattern does not
# apply to FlightEngineer.
# ---------------------------------------------------------------------------

SIMPLE: List[Any] = [
    # --- input EMI filter / main bus ----------------------------------------
    ("J_BATT", "XT60PW-F", FP_XT60, "XT60PW-F", "FlightEngineer.md Input: 6S LiPo main +/-",
     [("1", "+", "BATT_RAW_P"), ("2", "-", "BATT_RAW_N")]),
    ("CM1", "7440640500", FP_CMC_THT, "7440640500", "First-stage CM choke, battery lead (10A, 2x100uH)",
     [("1", "P1A", "BATT_RAW_P"), ("2", "P1B", "BATT_CM1_P"), ("3", "P2A", "BATT_RAW_N"), ("4", "P2B", "BATT_CM1_N")]),
    ("CM2", "7440640500", FP_CMC_THT, "7440640500", "Second-stage CM choke, series with CM1 (CS114 two-stage filter)",
     [("1", "P1A", "BATT_CM1_P"), ("2", "P1B", "VBAT"), ("3", "P2A", "BATT_CM1_N"), ("4", "P2B", "PGND")]),
    ("F1", "0297150.ZXNV 150A MAXI", FP_MAXIBLADE, "0297150.ZXNV", "Main bus fuse (150A MAXI blade)",
     [("1", "A", "VBAT"), ("2", "B", "VBAT_F1")]),
    ("C1", "220uF 35V", FP_CRAD_D10, "EEF-CX1V221R", "Bulk stiffening cap 1", [("1", "P", "VBAT_F1"), ("2", "N", "PGND")]),
    ("C2", "220uF 35V", FP_CRAD_D10, "EEF-CX1V221R", "Bulk stiffening cap 2", [("1", "P", "VBAT_F1"), ("2", "N", "PGND")]),
    ("C_DM1", "10uF 50V X7R 1210", FP_C1210, "885012207016", "DM HF filter, ESR<5mR@1MHz", [("1", "P", "VBAT_F1"), ("2", "N", "PGND")]),
    ("C3", "100nF X7R 0805", FP_C0805, "", "VBAT HF bypass", [("1", "P", "VBAT_F1"), ("2", "N", "PGND")]),
    ("D1", "SMBJ33CA", FP_SMB, "SMBJ33CA", "Main bus bidirectional TVS (33V/53.3V clamp) — real part, PDF not "
     "obtained this pass (every mirror blocked), standard SMB 2-pin convention used",
     [("1", "A", "VBAT_F1"), ("2", "K", "PGND")]),
    ("C_Y1", "4.7nF 250V Y2", FP_C0805, "SA305E472MAR", "VBAT+ -> chassis CM bypass", [("1", "P", "VBAT_F1"), ("2", "N", "J_CHASSIS_NET")]),
    ("C_Y2", "4.7nF 250V Y2", FP_C0805, "SA305E472MAR", "VBAT- -> chassis CM bypass", [("1", "P", "PGND"), ("2", "N", "J_CHASSIS_NET")]),
    ("RS_MAIN", "1mOhm 5W Kelvin", FP_KELVIN2512, "CSS2H-2512K-1L00F", "Main bus shunt (Bourns Kelvin 2512, closest "
     "real system land is the Vishay WSK2512 Kelvin family — same 4-pad pattern)",
     [("1", "IP", "VBAT_F1"), ("2", "IP", "VBAT_F1"), ("3", "SP", "SHUNT_MAIN_P"), ("4", "SN", "SHUNT_MAIN_N")]),
    ("VDIS_LINK", "0R link", FP_R0603, "", "Shunt output -> VDIS protected rail node", [("1", "A", "SHUNT_MAIN_N"), ("2", "B", "VDIS")]),
    ("D_I2C", "PRTR5V0U2X", "Package_TO_SOT_SMD:SOT-363_SC-70-6", "PRTR5V0U2X,115",
     "prtr5v0u2x.pdf — I2C line RF transient protection at enclosure wall",
     [("1", "IO1", "I2C_SCL"), ("2", "GND", "PGND"), ("3", "IO2", "I2C_SDA"), ("4", "NC", None),
      ("5", "VCC", "+5V"), ("6", "NC", None)]),
    # --- BQ76930 support -----------------------------------------------------
    ("J_BAL", "XH-7P", FP_XH7, "", "6S balance lead: BAL_GND,B1-B6",
     [("1", "BAL_GND", "CELL_B0"), ("2", "B1", "CELL_BAL1"), ("3", "B2", "CELL_BAL2"), ("4", "B3", "CELL_BAL3"),
      ("5", "B4", "CELL_BAL4"), ("6", "B5", "CELL_BAL5"), ("7", "B6", "CELL_BAL6")]),
    ("R_BAL1", "100R", FP_R0402, "", "Balance current limit B1", [("1", "A", "CELL_BAL1"), ("2", "B", "CELL_B1")]),
    ("R_BAL2", "100R", FP_R0402, "", "Balance current limit B2", [("1", "A", "CELL_BAL2"), ("2", "B", "CELL_B2")]),
    ("R_BAL3", "100R", FP_R0402, "", "Balance current limit B3", [("1", "A", "CELL_BAL3"), ("2", "B", "CELL_B3")]),
    ("R_BAL4", "100R", FP_R0402, "", "Balance current limit B4", [("1", "A", "CELL_BAL4"), ("2", "B", "CELL_B4")]),
    ("R_BAL5", "100R", FP_R0402, "", "Balance current limit B5", [("1", "A", "CELL_BAL5"), ("2", "B", "CELL_B5")]),
    ("R_BAL6", "100R", FP_R0402, "", "Balance current limit B6", [("1", "A", "CELL_BAL6"), ("2", "B", "CELL_B6")]),
    ("C_CAP1", "0.1uF", FP_C0402, "", "BQ76930 CAP1 boot cap (REGSRC-referenced)", [("1", "P", "CELL_CAP1"), ("2", "N", "CELL_B0")]),
    ("C_CAP2", "0.1uF", FP_C0402, "", "BQ76930 CAP2 boot cap (upper group)", [("1", "P", "CELL_CAP2"), ("2", "N", "CELL_B5")]),
    ("C_REGOUT", "1uF", FP_C0402, "", "BQ76930 REGOUT decouple (internal 3.3V LDO)", [("1", "P", "CELL_REGOUT"), ("2", "N", "CELL_B0")]),
    ("J_NTC", "SM02B-GHS-TB", FP_GH2, "SM02B-GHS-TB(LF)(SN)", "External battery NTC 10k", [("1", "NTC+", "NTC_P"), ("2", "NTC-", "PGND")]),
    ("R_NTC_PU", "10k", FP_R0402, "", "TS1 external NTC bias to REGOUT", [("1", "A", "CELL_REGOUT"), ("2", "B", "NTC_P")]),
    ("C_NTC", "100nF X7R", FP_C0402, "", "TS1 filter cap", [("1", "P", "NTC_P"), ("2", "N", "PGND")]),
    ("J_ALERT", "SM02B-GHS-TB", FP_GH2, "SM02B-GHS-TB(LF)(SN)", "BQ76930 ALERT to Pilot GPIO",
     [("1", "GND", "PGND"), ("2", "ALERT_N", "CELL_ALERT_N")]),
    ("R_ALERT", "2.2k", FP_R0402, "", "ALERT open-drain pull-up to 5V", [("1", "A", "+5V"), ("2", "B", "CELL_ALERT_N")]),
    ("R_DSG_G", "10k", FP_R0402, "", "DSG gate resistor to Q_BATT_DSG", [("1", "A", "BATT_DSG_GATE"), ("2", "B", "BATT_DSG_GATE_R")]),
    ("J_SHLD_I2C", "PGND via", FP_PGNDVIA, "", "I2C cable shield drain", [("1", "PGND", "PGND")]),
    ("J_SHLD_ALERT", "PGND via", FP_PGNDVIA, "", "ALERT cable shield drain", [("1", "PGND", "PGND")]),
    ("J_SHLD_NTC", "PGND via", FP_PGNDVIA, "", "NTC cable shield drain", [("1", "PGND", "PGND")]),
    ("J_I2C", "SM04B-GHS-TB", FP_GH4, "SM04B-GHS-TB(LF)(SN)", "PDB I2C bus to Pilot J_EXT_I2C",
     [("1", "GND", "PGND"), ("2", "+5V", "+5V"), ("3", "SCL", "I2C_SCL"), ("4", "SDA", "I2C_SDA")]),
    ("R_I2C_SCL", "4.7k", FP_R0402, "", "I2C SCL pull-up (host end per doc; also populated here as the "
     "bus's own node reference)", [("1", "A", "+5V"), ("2", "B", "I2C_SCL")]),
    ("R_I2C_SDA", "4.7k", FP_R0402, "", "I2C SDA pull-up", [("1", "A", "+5V"), ("2", "B", "I2C_SDA")]),
]

# --- 4x ESC branches --------------------------------------------------------
for _i in range(1, 5):
    SIMPLE += [
        (f"F_ESC{_i}", "0297040.WXNV 40A mini", FP_MINIBLADE, "0297040.WXNV", f"ESC{_i} branch fuse",
         [("1", "A", "VDIS"), ("2", "B", f"ESC{_i}_FUSED")]),
        (f"C_DEC{_i}", "470uF 35V low-ESR", FP_CRAD_D10x20, "EEUFC1V471", f"ESC{_i} local bulk (stall isolation)",
         [("1", "P", f"ESC{_i}_FUSED"), ("2", "N", "PGND")]),
        (f"CM_ESC{_i}", "7440640500", FP_CMC_THT, "7440640500", f"ESC{_i} output CM choke (noise isolation)",
         [("1", "P1A", f"ESC{_i}_FUSED"), ("2", "P1B", f"ESC{_i}_CM"), ("3", "P2A", "PGND"), ("4", "P2B", "PGND")]),
        (f"RS{_i}", "1mOhm 3W Kelvin", FP_KELVIN2512, "CSS2H-2512K-1L00F", f"ESC{_i} shunt (Kelvin)",
         [("1", "IP", f"ESC{_i}_CM"), ("2", "IP", f"ESC{_i}_CM"), ("3", "SP", f"SHUNT{_i}_P"), ("4", "SN", f"SHUNT{_i}_N")]),
        (f"ESC{_i}_LINK", "0R link", FP_R0603, "", f"ESC{_i} shunt output -> connector",
         [("1", "A", f"SHUNT{_i}_N"), ("2", "B", f"ESC{_i}_OUT")]),
        (f"J_ESC{_i}", "XT30PW-F", FP_XT30, "XT30PW-F", f"ESC{_i} power output",
         [("1", "+", f"ESC{_i}_OUT"), ("2", "-", "PGND")]),
        (f"J_SHLD_ESC{_i}", "M3 chassis lug", FP_M3LUG, "94459A120", f"ESC{_i} cable shield drain",
         [("1", "PGND", "PGND")]),
    ]

SIMPLE += [
    ("J_PGND_BATT", "M3 chassis lug", FP_M3LUG, "94459A120", "Battery cable shield drain", [("1", "PGND", "PGND")]),
    ("J_CHASSIS", "M3 standoff x4", FP_M3LUG, "94459A120", "PCB chassis ground bond to enclosure",
     [("1", "PGND", "J_CHASSIS_NET")]),
    ("R_CHGND", "0R socketed", FP_R0402, "", "Chassis<->PGND single-point bond (default 0R populated)",
     [("1", "A", "J_CHASSIS_NET"), ("2", "B", "PGND")]),
    # --- 5V dual-redundant BEC ------------------------------------------------
    ("FB_5V1", "742792612", FP_L_IND, "742792612", "5V BEC1 input ferrite (600R@100MHz, 2A)", [("1", "IN", "VDIS"), ("2", "OUT", "VDIS_5V1")]),
    ("C_BEC1_IN", "100uF 50V", FP_C1210, "", "BEC1 input bulk", [("1", "P", "VDIS_5V1"), ("2", "N", "GND")]),
    ("R_FB1_1", "56.2k 1%", FP_R0402, "", "TPS54620#1 FB divider top (Vout=5.3V, Vref=0.8V)", [("1", "A", "+5V_PRE_OR1"), ("2", "B", "BEC1_FB")]),
    ("R_FB1_2", "10.0k 1%", FP_R0402, "", "TPS54620#1 FB divider bottom", [("1", "A", "BEC1_FB"), ("2", "B", "GND")]),
    ("C_BEC1_COMP", "2.2nF", FP_C0402, "", "BEC1 compensation cap", [("1", "P", "BEC1_COMP"), ("2", "N", "BEC1_FB")]),
    ("C_BEC1_SS", "10nF", FP_C0402, "", "BEC1 soft-start", [("1", "P", "BEC1_SS"), ("2", "N", "GND")]),
    ("C_BEC1_BOOT", "100nF", FP_C0402, "", "BEC1 bootstrap", [("1", "P", "BEC1_BOOT"), ("2", "N", "BEC1_SW")]),
    ("L1", "10uH 6A", FP_L_IND, "744314100", "BEC1 switching inductor", [("1", "A", "BEC1_SW"), ("2", "B", "+5V_PRE_OR1")]),
    ("C_BEC1_OUT1", "220uF", FP_C1210, "", "BEC1 output bulk", [("1", "P", "+5V_PRE_OR1"), ("2", "N", "GND")]),
    ("C_BEC1_OUT2", "100nF", FP_C0402, "", "BEC1 output HF", [("1", "P", "+5V_PRE_OR1"), ("2", "N", "GND")]),
    ("D_OR1", "MBRD1045CT", FP_D2PAK, "MBRD1045CT", "BEC1 OR diode (real part confirmed, PDF not obtained "
     "this pass; standard D2PAK-3 common-cathode dual Schottky convention used, only one leg needed here)",
     [("1", "A", "+5V_PRE_OR1"), ("2", "K", "+5V_AVIONICS"), ("3", "K2", "+5V_AVIONICS")]),
    ("FB_5V2", "742792612", FP_L_IND, "742792612", "5V BEC2 input ferrite", [("1", "IN", "VDIS"), ("2", "OUT", "VDIS_5V2")]),
    ("C_BEC2_IN", "100uF 50V", FP_C1210, "", "BEC2 input bulk", [("1", "P", "VDIS_5V2"), ("2", "N", "GND")]),
    ("R_FB2_1", "56.2k 1%", FP_R0402, "", "TPS54620#2 FB divider top", [("1", "A", "+5V_PRE_OR2"), ("2", "B", "BEC2_FB")]),
    ("R_FB2_2", "10.0k 1%", FP_R0402, "", "TPS54620#2 FB divider bottom", [("1", "A", "BEC2_FB"), ("2", "B", "GND")]),
    ("C_BEC2_COMP", "2.2nF", FP_C0402, "", "BEC2 compensation cap", [("1", "P", "BEC2_COMP"), ("2", "N", "BEC2_FB")]),
    ("C_BEC2_SS", "10nF", FP_C0402, "", "BEC2 soft-start", [("1", "P", "BEC2_SS"), ("2", "N", "GND")]),
    ("C_BEC2_BOOT", "100nF", FP_C0402, "", "BEC2 bootstrap", [("1", "P", "BEC2_BOOT"), ("2", "N", "BEC2_SW")]),
    ("L2", "10uH 6A", FP_L_IND, "744314100", "BEC2 switching inductor", [("1", "A", "BEC2_SW"), ("2", "B", "+5V_PRE_OR2")]),
    ("C_BEC2_OUT1", "220uF", FP_C1210, "", "BEC2 output bulk", [("1", "P", "+5V_PRE_OR2"), ("2", "N", "GND")]),
    ("C_BEC2_OUT2", "100nF", FP_C0402, "", "BEC2 output HF", [("1", "P", "+5V_PRE_OR2"), ("2", "N", "GND")]),
    ("D_OR2", "MBRD1045CT", FP_D2PAK, "MBRD1045CT", "BEC2 OR diode, same flag as D_OR1",
     [("1", "A", "+5V_PRE_OR2"), ("2", "K", "+5V_AVIONICS"), ("3", "K2", "+5V_AVIONICS")]),
    ("R_EN_BIAS", "100k", FP_R0402, "", "BEC EN pull-up (float-to-enable per datasheet)", [("1", "A", "VDIS"), ("2", "B", "+3V3_BIAS_EN")]),
    ("J_5V", "Nano-Fit 4P", FP_NANOFIT4, "WM1720-ND", "5V avionics bus output",
     [("1", "+", "+5V_AVIONICS"), ("2", "+", "+5V_AVIONICS"), ("3", "-", "GND"), ("4", "-", "GND")]),
    ("J_SHLD_5V", "PGND via", FP_PGNDVIA, "", "5V cable shield drain", [("1", "PGND", "PGND")]),
    # --- 6V single BEC ---------------------------------------------------------
    ("FB_6V", "742792612", FP_L_IND, "742792612", "6V BEC input ferrite", [("1", "IN", "VDIS"), ("2", "OUT", "VDIS_6V")]),
    ("C_BEC_SV_IN", "100uF 50V", FP_C1210, "", "6V BEC input bulk", [("1", "P", "VDIS_6V"), ("2", "N", "GND")]),
    ("R_FB6_1", "64.9k 1%", FP_R0402, "", "TPS54540 FB divider top (Vout=6.0V, Vref=0.8V)", [("1", "A", "+6V_SERVO"), ("2", "B", "BEC6_FB")]),
    ("R_FB6_2", "10.0k 1%", FP_R0402, "", "TPS54540 FB divider bottom", [("1", "A", "BEC6_FB"), ("2", "B", "GND")]),
    ("C_BEC6_COMP", "1nF", FP_C0402, "", "6V BEC compensation cap", [("1", "P", "BEC6_COMP"), ("2", "N", "BEC6_FB")]),
    ("C_BEC6_BOOT", "100nF", FP_C0402, "", "6V BEC bootstrap", [("1", "P", "BEC6_BOOT"), ("2", "N", "BEC6_SW")]),
    ("L3", "10uH 6A", FP_L_IND, "744314100", "6V BEC switching inductor", [("1", "A", "BEC6_SW"), ("2", "B", "+6V_SERVO")]),
    ("C_BEC_SV_OUT1", "100uF", FP_C1210, "", "6V BEC output bulk", [("1", "P", "+6V_SERVO"), ("2", "N", "GND")]),
    ("C_BEC_SV_OUT2", "100nF", FP_C0402, "", "6V BEC output HF", [("1", "P", "+6V_SERVO"), ("2", "N", "GND")]),
    ("J_6V", "Nano-Fit 4P", FP_NANOFIT4, "WM1720-ND", "6V servo bus output",
     [("1", "+", "+6V_SERVO"), ("2", "+", "+6V_SERVO"), ("3", "-", "GND"), ("4", "-", "GND")]),
    ("J_SHLD_6V", "PGND via", FP_PGNDVIA, "", "6V cable shield drain", [("1", "PGND", "PGND")]),
    ("R_GND_PGND", "0R", FP_R0603, "", "Signal GND<->PGND single-point link (Pilot/XO convention)", [("1", "A", "GND"), ("2", "B", "PGND")]),
    # --- Trust module (Section H) support --------------------------------------
    ("C_ISOCAN1", "10nF", FP_C0402, "", "ISOW1044 VDD HF bypass", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C_ISOCAN2", "10uF", FP_C0805, "", "ISOW1044 VDD bulk", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C_ISOCAN3", "100nF", FP_C0402, "", "ISOW1044 VIO bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C_ISOCAN4", "10nF", FP_C0402, "", "ISOW1044 VISOOUT HF bypass", [("1", "P", "ISO_5V_CAN"), ("2", "N", "ISO_GND_CAN")]),
    ("C_ISOCAN5", "10uF", FP_C0805, "", "ISOW1044 VISOOUT bulk", [("1", "P", "ISO_5V_CAN"), ("2", "N", "ISO_GND_CAN")]),
    ("R_CANSTB", "0R", FP_R0402, "", "CANFD_STB tied active (normal-op mode)", [("1", "A", "CANFD_STB"), ("2", "B", "GND")]),
    ("R_RS485FLT_PU", "10k", FP_R0402, "", "ISOW1412 EN/FLT pull-up (enabled default; MCU can read fault or drive low to disable)",
     [("1", "A", "+3V3"), ("2", "B", "RS485_FLT_N")]),
    ("J_CAN_IN", "SM03B-GHS-TB", FP_GH3, "SM03B-GHS-TB(LF)(SN)", "Isolated CAN-FD trunk IN",
     [("1", "H", "CAN_H"), ("2", "L", "CAN_L"), ("3", "GND", "ISO_GND_CAN")]),
    ("J_CAN_OUT", "SM03B-GHS-TB", FP_GH3, "SM03B-GHS-TB(LF)(SN)", "Isolated CAN-FD trunk OUT",
     [("1", "H", "CAN_H"), ("2", "L", "CAN_L"), ("3", "GND", "ISO_GND_CAN")]),
    ("R_CANTERM", "120R", FP_R0603, "", "CAN termination — populate ONLY at a bus end node (DNP default)",
     [("1", "A", "CAN_H"), ("2", "B", "CAN_L")], {"dnp": True}),
    ("C_RS485_1", "10nF", FP_C0402, "", "ISOW1412 VDD HF bypass", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C_RS485_2", "10uF", FP_C0805, "", "ISOW1412 VDD bulk", [("1", "P", "+5V"), ("2", "N", "GND")]),
    ("C_RS485_3", "100nF", FP_C0402, "", "ISOW1412 VIO bypass", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C_RS485_4", "10nF", FP_C0402, "", "ISOW1412 VISOOUT HF bypass", [("1", "P", "ISO_5V_485"), ("2", "N", "ISO_GND_485")]),
    ("C_RS485_5", "10uF", FP_C0805, "", "ISOW1412 VISOOUT bulk", [("1", "P", "ISO_5V_485"), ("2", "N", "ISO_GND_485")]),
    ("J_485_IN", "SM03B-GHS-TB", FP_GH3, "SM03B-GHS-TB(LF)(SN)", "Isolated RS-485 trunk IN",
     [("1", "A", "RS485_A"), ("2", "B", "RS485_B"), ("3", "GND", "ISO_GND_485")]),
    ("J_485_OUT", "SM03B-GHS-TB", FP_GH3, "SM03B-GHS-TB(LF)(SN)", "Isolated RS-485 trunk OUT",
     [("1", "A", "RS485_A"), ("2", "B", "RS485_B"), ("3", "GND", "ISO_GND_485")]),
    ("R_485TERM", "120R", FP_R0603, "", "RS-485 termination — populate ONLY at a bus end node (DNP default)",
     [("1", "A", "RS485_A"), ("2", "B", "RS485_B")], {"dnp": True}),
    ("C_TPM1", "1uF", FP_C0402, "", "SLB9672 typical schematic bulk", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C_TPM2", "100nF", FP_C0402, "", "SLB9672 VDD bypass (pin 1)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C_TPM3", "100nF", FP_C0402, "", "SLB9672 VDD bypass (pin 14)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("C_TPM4", "100nF", FP_C0402, "", "SLB9672 VDD bypass (pin 22)", [("1", "P", "+3V3"), ("2", "N", "GND")]),
    ("R_TPMCS", "10k", FP_R0402, "", "SLB9672 CS# pull-up", [("1", "A", "+3V3"), ("2", "B", "TPM_SPI_CS")]),
    ("R_TPM10", "10k", FP_R0402, "", "SLB9672 pin 10 NCI/VDD pull-up (Table 13, preferred)", [("1", "A", "+3V3"), ("2", "B", "TPM_P10_PU")]),
    ("R_MCU_NRST", "10k", FP_R0402, "", "MCU NRST pull-up", [("1", "A", "+3V3"), ("2", "B", "MCU_NRST")]),
    ("C_MCU_VCORE", "1uF", FP_C0402, "", "MCU VCORE bypass (dedicated cap per fleet convention)", [("1", "P", "MCU_VCORE"), ("2", "N", "PGND")]),
    ("C_MCU_3V3", "100nF", FP_C0402, "", "MCU +3V3 bypass", [("1", "P", "+3V3"), ("2", "N", "PGND")]),
    ("U_REG_3V3_H", "TLV62569DBVR", FP_SOT23, "TLV62569DBVR", "5V->3V3 buck for the trust-module logic domain",
     [("1", "EN", "+3V3"), ("2", "GND", "PGND"), ("3", "SW", "REG3V3_SW"), ("4", "VIN", "+5V"), ("5", "FB", "+3V3")]),
    ("L_H1", "2.2uH", FP_L_IND, "", "U_REG_3V3_H inductor", [("1", "A", "REG3V3_SW"), ("2", "B", "+3V3")]),
    ("C_H_IN", "10uF", FP_C0805, "", "U_REG_3V3_H input bulk", [("1", "P", "+5V"), ("2", "N", "PGND")]),
    ("C_H_OUT", "22uF", FP_C0805, "", "U_REG_3V3_H output bulk", [("1", "P", "+3V3"), ("2", "N", "PGND")]),
    ("J_SWD_H", "SM04B-GHS-TB", FP_GH4, "SM04B-GHS-TB(LF)(SN)", "MCU SWD debug (DIO/CLK/NRST/GND)",
     [("1", "DIO", "MCU_SWDIO"), ("2", "CLK", "MCU_SWCLK"), ("3", "NRST", "MCU_NRST"), ("4", "GND", "PGND")]),
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
        f'    (symbol "FlightEngineer:{libid}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)',
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
    etype = "power_in" if isinstance(fn, str) and fn in ("GND", "PGND", "EP") else "passive"
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
        f'  (symbol (lib_id "FlightEngineer:{libid}") (at {X:.2f} {Y:.2f} 0) (unit 1)',
        f'    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp {dnp}) (uuid "{uid()}")',
        f'    (property "Reference" "{esc(ref)}" (at {X:.2f} {Y - half_h - 1.27:.2f} 0) (effects (font (size {SIZE} {SIZE}))))',
        f'    (property "Value" "{esc(value)}" (at {X:.2f} {Y + half_h + 1.27:.2f} 0) (effects (font (size {SIZE} {SIZE}))))',
        f'    (property "Footprint" "{esc(ic["fp"])}" (at {X:.2f} {Y:.2f} 0) (effects (font (size {SIZE} {SIZE})) (hide yes)))',
        f'    (property "Datasheet" "{esc(ic["ds"])}" (at {X:.2f} {Y:.2f} 0) (effects (font (size {SIZE} {SIZE})) (hide yes)))',
        f'    (property "MPN" "{esc(ic.get("mpn", ""))}" (at {X:.2f} {Y:.2f} 0) (effects (font (size {SIZE} {SIZE})) (hide yes)))',
    ]
    for pn, *_ in left + right:
        out.append(f'    (pin "{esc(pn)}" (uuid "{uid()}"))')
    out.append(f'    (instances (project "FlightEngineer" (path "/{sheet_uuid}" (reference "{esc(ref)}") (unit 1))))')
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


PWR_FLAG_RAILS = ["GND", "PGND", "+3V3", "+5V", "VBAT", "VDIS", "+5V_AVIONICS", "+6V_SERVO",
                  "ISO_GND_CAN", "ISO_5V_CAN", "ISO_GND_485", "ISO_5V_485", "J_CHASSIS_NET"]

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
            f'    (instances (project "FlightEngineer" (path "/{sheet_uuid}" (reference "#FLG{i + 1}") (unit 1)))))'
        )
        out.append(wire(x, y0, x, y0 + STUB))
        out.append(label(rail, x, y0 + STUB, 270))
    return out


TITLE_BLOCK = """  (title_block
    (title "Flight Engineer — Power Distribution Board")
    (date "2026-09-20")
    (rev "R2")
    (company "Griffing Technology LLC")
    (comment 1 "Power/monitoring node, 90 x 65 mm, 4-layer")
    (comment 2 "Generated by avionics/kicad/FlightEngineer/scripts/gen_fe_sch.py — do not hand-edit; edit the generator")
    (comment 3 "Author: Claude Sonnet 5 (2026-09-20); owner sgriffing")
    (comment 4 "CC BY 4.0 — pinouts transcribed from OEM datasheets in avionics/datasheets/")
  )"""


def main() -> None:
    sheet_uuid = uid()
    parts = [
        "(kicad_sch (version 20240101) (generator eeschema)",
        f'  (uuid "{uid()}")',
        '  (paper "A2")',
        TITLE_BLOCK,
        "  (lib_symbols",
        PWR_FLAG_LIB,
    ]
    placed = []
    X0, Y0, DX = 76.2, 76.2, 127.0
    COL_MAX_Y = 660.0
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
    lib = ["(kicad_symbol_lib (version 20241209) (generator \"gen_fe_sch.py\") (generator_version \"9.0\")"]
    for ic, left, right, hw, hh in built:
        lib.append(lib_symbol(ic)[0].replace('(symbol "FlightEngineer:', '(symbol "', 1))
    lib.append(")")
    SYMLIB.write_text("\n".join(lib) + "\n")
    npins = sum(len(ic["pins"]) for ic in ICS)
    print(f"Wrote {OUT}")
    print(f"  parts: {len(ICS)}   pins: {npins}   columns: {int((x - X0) / DX) + 1}")


if __name__ == "__main__":
    main()
