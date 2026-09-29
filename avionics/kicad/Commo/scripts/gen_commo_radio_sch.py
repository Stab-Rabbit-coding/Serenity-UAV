#!/usr/bin/env python3
"""gen_commo_radio_sch.py -- Commo Rev T 49 MHz radio sheet (U2 + U3).

Writes ``kicads/Commo_radio.kicad_sch`` and ``kicads/Commo_radio.kicad_sym``.
The Rev T top-level sheet (U1, gen_commo_revt_sch.py) connects to it by global
labels only:

    +5V  +3V3  GND                      supply and I2C pull-up rail
    I2C0_SCL  I2C0_SDA                  Si5351B (0x60) shares I2C0 with the SE (0x30)
    VCXO_DAC  (MCU PA15 DAC_OUT)        TX FM modulation into the Si5351B VC pin
    TR_CTRL   (MCU PB15)                PE4259: high = TX (RFC-RF1), low = RX (RFC-RF2)
    RF_EN     (MCU PB9)                 TPS7A2033 enable: the whole RF-analog rail off when idle
    RX_I  RX_Q (MCU PA22 A0_7 / PA21 A1_7)  baseband to the two simultaneous-sampling ADCs

Architecture (see avionics/kicad/Commo/COMMO_REVT_RF_DESIGN.md):
    RP-SMA -> ESD101 -> 6-element LPF -> PE4259 T/R -> RX: 2-pole BPF -> 51 Ohm
    termination -> 2 x SA612A (I, Q) -> TLV9062 difference amp / anti-alias -> ADC.
    TX: Si5351B CLK0 (PLLB, VCXO-FM from MCU DAC) -> 10 dB pi pad -> PE4259 RF1.
    RX LOs: Si5351B CLK1 (0 deg) / CLK2 (90 deg) from PLLA -> 254 mVpp pads.

Every pin table cites the OEM datasheet in avionics/datasheets/ (fleet
convention docs/solutions/conventions/pb2-cape-datasheet-verified-footprints-
and-courtyard-budget-before-layout.md, rule 1).  Component values come from
commo_radio_design.py, which must pass before this sheet is regenerated.

Symbol boxes follow the fleet generators (gen_pilot_sch.py): 2-pin parts get
the compact 600 x 200 mil box, everything else the 1300 mil IC box.

ENGINEERING REVIEW REQUIRED -- see the design note.
Author: Claude Opus 5.5 (2026-09-29); owner sgriffing.  License: CC BY 4.0.
"""

import itertools
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "kicads" / "Commo_radio.kicad_sch"
SYMLIB = HERE.parent / "kicads" / "Commo_radio.kicad_sym"
LIB = "CommoRadio"
PROJECT = "Commo"

SIZE = 1.27
PIN_PITCH = 2.54
STUB = 2.54
_uid = itertools.count(1)

# --- footprints (stock KiCad 9 unless noted) --------------------------------
FP_C0402 = "Capacitor_SMD:C_0402_1005Metric"
FP_C0603 = "Capacitor_SMD:C_0603_1608Metric"
FP_C0805 = "Capacitor_SMD:C_0805_2012Metric"
FP_R0402 = "Resistor_SMD:R_0402_1005Metric"
FP_R0603 = "Resistor_SMD:R_0603_1608Metric"
FP_L0805 = "Inductor_SMD:L_0805_2012Metric"
FP_QFN16 = "Package_DFN_QFN:QFN-16-1EP_3x3mm_P0.5mm_EP1.7x1.7mm"   # EP 1.70 = package min (Si5351-B 12.3)
FP_XTAL = "Crystal:Crystal_SMD_2520-4Pin_2.5x2.0mm"
FP_SO8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
FP_SOT363 = "Package_TO_SOT_SMD:SOT-363_SC-70-6"
FP_SOT23_8 = "Package_TO_SOT_SMD:SOT-23-8"
FP_SOT23_5 = "Package_TO_SOT_SMD:SOT-23-5"
FP_ESD = "SecureControllers:Infineon_TSSLP-2-4_0.62x0.32mm"
FP_RPSMA = "Connector_Coaxial:SMA_Amphenol_132289_EdgeMount"   # 132289RP shares this land (Commo.md J2)


def uid() -> str:
    return f"a4900000-0000-0000-0000-{next(_uid):012d}"


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def sanitize(ref: str) -> str:
    return re.sub(r"[^A-Za-z0-9_+.-]", "_", ref)


# ---------------------------------------------------------------------------
# ICs: (pin, function, net|None, side)
# ---------------------------------------------------------------------------
ICS: List[Dict[str, Any]] = [
    {
        "ref": "U-SYN", "value": "Si5351B-B-GM1", "fp": FP_QFN16, "mpn": "Si5351B-B-GM1",
        "ds": "Si5351-B.pdf Rev 1.3 Table 18 (16-QFN) / Table 8 crystal / VCXO specifications",
        # PLLA -> CLK1 (I LO) and CLK2 (Q LO, PHOFF 90 deg); PLLB (VCXO) -> CLK0 TX.
        # OEB tied low: outputs are enabled/disabled per clock over I2C.
        "pins": [
            ("1", "XA", "XTAL_A", "L"), ("2", "XB", "XTAL_B", "L"), ("3", "VC", "VCXO_VC", "L"),
            ("4", "SCL", "I2C0_SCL", "L"), ("5", "SDA", "I2C0_SDA", "L"), ("6", "OEB", "GND", "L"),
            ("16", "VDD", "+3V3_RF", "L"), ("15", "GND", "GND", "L"), ("17", "EP", "GND", "L"),
            ("10", "CLK0", "TX_CLK", "R"), ("7", "CLK1", "LO_I_RAW", "R"), ("13", "CLK2", "LO_Q_RAW", "R"),
            ("12", "CLK3", None, "R"),
            ("9", "VDDOA", "+3V3_RF", "R"), ("8", "VDDOB", "+3V3_RF", "R"),
            ("14", "VDDOC", "+3V3_RF", "R"), ("11", "VDDOD", "+3V3_RF", "R"),
        ],
    },
    {
        "ref": "Y-SYN", "value": "25MHz 8pF", "fp": FP_XTAL, "mpn": "ECS-250-8-36-CGN-TR",
        "ds": "ECX-2236.pdf: 25.000 MHz, CL 8 pF (Si5351B internal load reg 183), ESR 60 Ohm max, 100 uW",
        "pins": [("1", "IN/OUT", "XTAL_A", "L"), ("2", "GND", "GND", "L"),
                 ("3", "OUT/IN", "XTAL_B", "R"), ("4", "GND", "GND", "R")],
    },
    {
        "ref": "U-TR", "value": "PE4259", "fp": FP_SOT363, "mpn": "PE4259-63",
        "ds": "pe4259.pdf DOC-03694-5.01 Table 7 pins / Table 5 truth table (CTRL high = RFC-RF1)",
        # RF pins 1/3/5 must be DC blocked (datasheet note): C-TX, C-BPF-E1, C-RFC.
        "pins": [("1", "RF1", "SW_RF1", "L"), ("2", "GND", "GND", "L"), ("3", "RF2", "SW_RF2", "L"),
                 ("4", "CTRL", "TR_CTRL", "R"), ("5", "RFC", "SW_RFC", "R"), ("6", "VDD", "+3V3_RF", "R")],
    },
    {
        "ref": "U-MIX-I", "value": "SA612AD/01", "fp": FP_SO8, "mpn": "SA612AD/01,118",
        "ds": "SA612A.pdf Rev 3 Table 3 pinning (SO8); external LO 200-300 mVpp into OSC_B via DC block",
        # OSC_E (pin 7) left open with external LO injection -- bench-verify (design note section 7).
        "pins": [("1", "IN_A", "MIXI_INA", "L"), ("2", "IN_B", "MIXI_INB", "L"), ("3", "GND", "GND", "L"),
                 ("6", "OSC_B", "MIXI_LO", "L"), ("7", "OSC_E", None, "L"),
                 ("8", "VCC", "+5V_RF", "R"), ("4", "OUT_A", "MIXI_OA", "R"), ("5", "OUT_B", "MIXI_OB", "R")],
    },
    {
        "ref": "U-MIX-Q", "value": "SA612AD/01", "fp": FP_SO8, "mpn": "SA612AD/01,118",
        "ds": "SA612A.pdf Rev 3 Table 3 pinning (SO8); identical to U-MIX-I, LO from CLK2 (90 deg)",
        "pins": [("1", "IN_A", "MIXQ_INA", "L"), ("2", "IN_B", "MIXQ_INB", "L"), ("3", "GND", "GND", "L"),
                 ("6", "OSC_B", "MIXQ_LO", "L"), ("7", "OSC_E", None, "L"),
                 ("8", "VCC", "+5V_RF", "R"), ("4", "OUT_A", "MIXQ_OA", "R"), ("5", "OUT_B", "MIXQ_OB", "R")],
    },
    {
        "ref": "U-BB", "value": "TLV9062IDDFR", "fp": FP_SOT23_8, "mpn": "TLV9062IDDFR",
        "ds": "tlv9062.pdf Figure 5-6 / Table 5-3 (DDF SOT-23-8); 10 MHz GBW, RRIO",
        "pins": [("3", "IN1+", "BBI_P", "L"), ("2", "IN1-", "BBI_N", "L"), ("1", "OUT1", "BBI_OUT", "L"),
                 ("4", "V-", "GND", "L"),
                 ("5", "IN2+", "BBQ_P", "R"), ("6", "IN2-", "BBQ_N", "R"), ("7", "OUT2", "BBQ_OUT", "R"),
                 ("8", "V+", "+3V3_RF", "R")],
    },
    {
        "ref": "U-LDO-RF", "value": "TPS7A2033PDBVR", "fp": FP_SOT23_5, "mpn": "TPS7A2033PDBVR",
        "ds": "tps7a20.pdf SBVS338H Pin Functions (SOT-23 DBV): 1 IN, 2 GND, 3 EN (500k pull-down), 4 N/C, 5 OUT",
        # Smaller option: TPS7A2033DQNR X2SON 1 x 1 mm (datasheet package table).
        "pins": [("1", "IN", "+5V_RF", "L"), ("3", "EN", "RF_EN", "L"), ("2", "GND", "GND", "L"),
                 ("4", "NC", None, "R"), ("5", "OUT", "+3V3_RF", "R")],
    },
    {
        "ref": "J-ANT", "value": "RP-SMA edge", "fp": FP_RPSMA, "mpn": "132289RP",
        "ds": "Commo.md J2: Amphenol 132289RP reverse-polarity SMA, 47 CFR 15.203 unique coupling [REF-FCC-003]; datasheet not on file",
        # Shell to RF GND (low-inductance return at 49.86 MHz), not the PGND ring.
        # Stock footprint numbers all four shell/ground pads "2".
        "pins": [("1", "RF", "ANT", "L"), ("2", "GND", "GND", "R")],
    },
]

# ---------------------------------------------------------------------------
# Passives and 2-pin parts: (ref, value, fp, mpn, description, [(pin, fn, net), ...])
# Values from commo_radio_design.py.
# ---------------------------------------------------------------------------
C0G = "C0G 50V"
SIMPLE: List[Any] = [
    # --- RF-analog supplies -----------------------------------------------
    ("R-RF5", "4.7R 1%", FP_R0603, "", "+5V -> +5V_RF RC filter (35 mA -> 165 mV drop; SA612A VCC >= 4.5 V at bus 4.75 V)",
     [("1", "A", "+5V"), ("2", "B", "+5V_RF")]),
    ("C-RF5-1", "10uF 10V X5R", FP_C0805, "", "+5V_RF RC filter bulk (fc 3.4 kHz)", [("1", "P", "+5V_RF"), ("2", "N", "GND")]),
    ("C-RF5-2", "100nF", FP_C0402, "", "+5V_RF HF bypass", [("1", "P", "+5V_RF"), ("2", "N", "GND")]),
    ("C-LDO-IN", "1uF 10V X5R", FP_C0402, "", "TPS7A20 CIN (1 uF nominal)", [("1", "P", "+5V_RF"), ("2", "N", "GND")]),
    ("C-LDO-OUT", "1uF 10V X5R", FP_C0402, "", "TPS7A20 COUT (1 uF min, ESR < 100 mOhm)", [("1", "P", "+3V3_RF"), ("2", "N", "GND")]),
    # --- Si5351B support ----------------------------------------------------
    ("C-SYN-1", "1uF 10V X5R", FP_C0402, "", "Si5351B VDD bulk", [("1", "P", "+3V3_RF"), ("2", "N", "GND")]),
    ("C-SYN-2", "100nF", FP_C0402, "", "Si5351B VDD bypass", [("1", "P", "+3V3_RF"), ("2", "N", "GND")]),
    ("C-SYN-A", "100nF", FP_C0402, "", "Si5351B VDDOA (CLK0 TX)", [("1", "P", "+3V3_RF"), ("2", "N", "GND")]),
    ("C-SYN-B", "100nF", FP_C0402, "", "Si5351B VDDOB (CLK1 I LO)", [("1", "P", "+3V3_RF"), ("2", "N", "GND")]),
    ("C-SYN-C", "100nF", FP_C0402, "", "Si5351B VDDOC (CLK2 Q LO)", [("1", "P", "+3V3_RF"), ("2", "N", "GND")]),
    ("C-SYN-D", "100nF", FP_C0402, "", "Si5351B VDDOD (CLK3 unused)", [("1", "P", "+3V3_RF"), ("2", "N", "GND")]),
    ("R-SCL", "2.2k", FP_R0402, "", "I2C0 SCL pull-up (Si5351-B: at least 1 kOhm)", [("1", "A", "+3V3"), ("2", "B", "I2C0_SCL")]),
    ("R-SDA", "2.2k", FP_R0402, "", "I2C0 SDA pull-up (Si5351-B: at least 1 kOhm)", [("1", "A", "+3V3"), ("2", "B", "I2C0_SDA")]),
    ("R-VC", "1.5k 1%", FP_R0402, "", "VCXO VC reconstruction R (fc 12.9 kHz)", [("1", "A", "VCXO_DAC"), ("2", "B", "VCXO_VC")]),
    ("C-VC", "8.2nF C0G", FP_C0402, "", "VCXO VC reconstruction C", [("1", "P", "VCXO_VC"), ("2", "N", "GND")]),
    # --- TX: 10 dB pi pad + DC block to PE4259 RF1 -------------------------
    ("R-TXA", "95.3R 1%", FP_R0402, "", "TX pad shunt (10 dB pi, 50 Ohm)", [("1", "A", "TX_CLK"), ("2", "B", "GND")]),
    ("R-TXB", "71.5R 1%", FP_R0402, "", "TX pad series; value set at EMC test", [("1", "A", "TX_CLK"), ("2", "B", "TX_PAD")]),
    ("R-TXC", "95.3R 1%", FP_R0402, "", "TX pad shunt", [("1", "A", "TX_PAD"), ("2", "B", "GND")]),
    ("C-TX", "1nF " + C0G, FP_C0402, "", "PE4259 RF1 DC block (3.2 Ohm at 49.86 MHz)", [("1", "P", "TX_PAD"), ("2", "N", "SW_RF1")]),
    # --- antenna, ESD, LPF, RFC DC block -----------------------------------
    ("D-ANT", "ESD101-B1-02ELS", FP_ESD, "ESD101-B1-02ELS", "antenna ESD, bidirectional +/-5.5 V, 0.1 pF (esd101-b1.pdf)",
     [("1", "A", "ANT"), ("2", "B", "GND")]),
    ("L-LPF3", "180nH 2%", FP_L0805, "0805CS-181XGRC", "LPF L3 (0805cs.pdf)", [("1", "A", "ANT"), ("2", "B", "LPF_N2")]),
    ("C-LPF3", "120pF " + C0G, FP_C0402, "", "LPF shunt C3", [("1", "P", "ANT"), ("2", "N", "GND")]),
    ("C-LPF2", "180pF " + C0G, FP_C0402, "", "LPF shunt C2", [("1", "P", "LPF_N2"), ("2", "N", "GND")]),
    ("L-LPF2", "180nH 2%", FP_L0805, "0805CS-181XGRC", "LPF L2", [("1", "A", "LPF_N2"), ("2", "B", "LPF_N1")]),
    ("C-LPF1", "120pF " + C0G, FP_C0402, "", "LPF shunt C1", [("1", "P", "LPF_N1"), ("2", "N", "GND")]),
    ("L-LPF1", "100nH 2%", FP_L0805, "0805CS-101XGRC", "LPF L1", [("1", "A", "LPF_N1"), ("2", "B", "LPF_SW")]),
    ("C-RFC", "1nF " + C0G, FP_C0402, "", "PE4259 RFC DC block", [("1", "P", "LPF_SW"), ("2", "N", "SW_RFC")]),
    # --- RX 2-pole top-C-coupled BPF (C-BPF-E1 is also the RF2 DC block) ----
    ("C-BPF-E1", "15pF " + C0G, FP_C0402, "", "BPF input coupling / RF2 DC block", [("1", "P", "SW_RF2"), ("2", "N", "BPF_N1")]),
    ("L-BPF1", "220nH 2%", FP_L0805, "0805CS-221XGRC", "BPF resonator 1", [("1", "A", "BPF_N1"), ("2", "B", "GND")]),
    ("C-BPF-R1", "30pF " + C0G, FP_C0402, "", "BPF resonator 1 C", [("1", "P", "BPF_N1"), ("2", "N", "GND")]),
    ("C-BPF-C", "3.9pF " + C0G, FP_C0402, "", "BPF top coupling", [("1", "P", "BPF_N1"), ("2", "N", "BPF_N2")]),
    ("L-BPF2", "220nH 2%", FP_L0805, "0805CS-221XGRC", "BPF resonator 2", [("1", "A", "BPF_N2"), ("2", "B", "GND")]),
    ("C-BPF-R2", "30pF " + C0G, FP_C0402, "", "BPF resonator 2 C", [("1", "P", "BPF_N2"), ("2", "N", "GND")]),
    ("C-BPF-E2", "15pF " + C0G, FP_C0402, "", "BPF output coupling", [("1", "P", "BPF_N2"), ("2", "N", "RX_RF")]),
    ("R-RXT", "51R 1%", FP_R0402, "", "RX termination: 51 || 2 x SA612A (1.5k || 3 pF) ~ 48 Ohm", [("1", "A", "RX_RF"), ("2", "B", "GND")]),
]


def mixer(tag: str) -> List[Any]:
    """Per-channel mixer coupling, LO pad, and baseband difference amp (I or Q)."""
    t, T = tag.lower(), tag
    return [
        (f"C-MIX{T}-A", "1nF " + C0G, FP_C0402, "", f"SA612A {T} IN_A coupling", [("1", "P", "RX_RF"), ("2", "N", f"MIX{T}_INA")]),
        (f"C-MIX{T}-B", "1nF " + C0G, FP_C0402, "", f"SA612A {T} IN_B AC ground", [("1", "P", f"MIX{T}_INB"), ("2", "N", "GND")]),
        (f"C-MIX{T}-V", "100nF", FP_C0402, "", f"SA612A {T} VCC bypass", [("1", "P", "+5V_RF"), ("2", "N", "GND")]),
        (f"R-LO{T}-S", "2.4k 1%", FP_R0402, "", f"{T} LO pad series (254 mVpp, 1.27 mA)", [("1", "A", f"LO_{T}_RAW"), ("2", "B", f"LO_{T}_PAD")]),
        (f"R-LO{T}-P", "200R 1%", FP_R0402, "", f"{T} LO pad shunt", [("1", "A", f"LO_{T}_PAD"), ("2", "B", "GND")]),
        (f"C-LO{T}", "1nF " + C0G, FP_C0402, "", f"{T} LO DC block into OSC_B", [("1", "P", f"LO_{T}_PAD"), ("2", "N", f"MIX{T}_LO")]),
        (f"C-BB{T}-A", "1uF 10V X5R", FP_C0402, "", f"{T} OUT_A AC coupling (HPF 13.8 Hz)", [("1", "P", f"MIX{T}_OA"), ("2", "N", f"BB{T}_A")]),
        (f"C-BB{T}-B", "1uF 10V X5R", FP_C0402, "", f"{T} OUT_B AC coupling", [("1", "P", f"MIX{T}_OB"), ("2", "N", f"BB{T}_B")]),
        (f"R-BB{T}-A", "10k 1%", FP_R0402, "", f"{T} diff-amp input R (-)", [("1", "A", f"BB{T}_A"), ("2", "B", f"BB{T}_N")]),
        (f"R-BB{T}-B", "10k 1%", FP_R0402, "", f"{T} diff-amp input R (+)", [("1", "A", f"BB{T}_B"), ("2", "B", f"BB{T}_P")]),
        (f"R-BB{T}-F", "100k 1%", FP_R0402, "", f"{T} feedback R (gain x8.7)", [("1", "A", f"BB{T}_N"), ("2", "B", f"BB{T}_OUT")]),
        (f"C-BB{T}-F", "68pF " + C0G, FP_C0402, "", f"{T} feedback C (LPF 23.4 kHz)", [("1", "P", f"BB{T}_N"), ("2", "N", f"BB{T}_OUT")]),
        (f"R-BB{T}-G", "100k 1%", FP_R0402, "", f"{T} reference R to BB_VREF", [("1", "A", f"BB{T}_P"), ("2", "B", "BB_VREF")]),
        (f"C-BB{T}-G", "68pF " + C0G, FP_C0402, "", f"{T} reference C (matches feedback)", [("1", "P", f"BB{T}_P"), ("2", "N", "BB_VREF")]),
        (f"R-BB{T}-O", "1k 1%", FP_R0402, "", f"{T} ADC drive R (post-filter 72 kHz)", [("1", "A", f"BB{T}_OUT"), ("2", "B", f"RX_{T}")]),
        (f"C-BB{T}-O", "2.2nF C0G", FP_C0402, "", f"{T} ADC charge reservoir", [("1", "P", f"RX_{T}"), ("2", "N", "GND")]),
    ] if t else []


SIMPLE += mixer("I") + mixer("Q")
SIMPLE += [
    ("C-BB-V", "100nF", FP_C0402, "", "TLV9062 V+ bypass", [("1", "P", "+3V3_RF"), ("2", "N", "GND")]),
    ("R-VR1", "10k 1%", FP_R0402, "", "baseband mid-rail reference top", [("1", "A", "+3V3_RF"), ("2", "B", "BB_VREF")]),
    ("R-VR2", "10k 1%", FP_R0402, "", "baseband mid-rail reference bottom", [("1", "A", "BB_VREF"), ("2", "B", "GND")]),
    ("C-VR", "1uF 10V X5R", FP_C0402, "", "baseband reference decoupling", [("1", "P", "BB_VREF"), ("2", "N", "GND")]),
]

for _entry in SIMPLE:
    _ref, _val, _fp, _mpn, _ds, _pins = _entry[:6]
    _half = (len(_pins) + 1) // 2
    ICS.append({"ref": _ref, "value": _val, "fp": _fp, "mpn": _mpn, "ds": _ds,
                "pins": [(pn, fn, net, "L" if i < _half else "R") for i, (pn, fn, net) in enumerate(_pins)]})


# ---------------------------------------------------------------------------
# rendering (same conventions as gen_pilot_sch.py, compact passive boxes)
# ---------------------------------------------------------------------------
def pin_def(x: float, y: float, ang: int, pn: str, fn: Optional[str]) -> str:
    etype = "power_in" if isinstance(fn, str) and fn in ("GND", "EP") else "passive"
    return (f"        (pin {etype} line (at {x:.2f} {y:.2f} {ang}) (length {PIN_PITCH}) "
            f'(name "{esc(fn) if fn is not None else ""}" (effects (font (size {SIZE} {SIZE})))) '
            f'(number "{esc(pn)}" (effects (font (size {SIZE} {SIZE})))))')


def lib_symbol(ic: Dict[str, Any]) -> Tuple[str, List[Any], List[Any], float, float]:
    pins = ic["pins"]
    left = [p for p in pins if p[3] == "L"]
    right = [p for p in pins if p[3] == "R"]
    rows = max(len(left), len(right), 1)
    if len(left) + len(right) <= 2:
        half_w, half_h = 7.62, 2.54
    else:
        half_w, half_h = 16.51, (rows * PIN_PITCH) / 2 + PIN_PITCH
    libid = f"S_{sanitize(ic['ref'])}"
    s = [
        f'    (symbol "{LIB}:{libid}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)',
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
    for i, (pn, fn, _net, _) in enumerate(left):
        s.append(pin_def(-half_w - PIN_PITCH, half_h - PIN_PITCH * (i + 1), 0, pn, fn))
    for i, (pn, fn, _net, _) in enumerate(right):
        s.append(pin_def(half_w + PIN_PITCH, half_h - PIN_PITCH * (i + 1), 180, pn, fn))
    s += ["      )", "    )"]
    return "\n".join(s), left, right, half_w, half_h


def wire(x1: float, y1: float, x2: float, y2: float) -> str:
    return (f"  (wire (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f})) "
            f'(stroke (width 0) (type default)) (uuid "{uid()}"))')


def label(net: str, x: float, y: float, ang: int) -> str:
    just = "left" if ang == 0 else "right"
    return (f'  (global_label "{esc(net)}" (shape passive) (at {x:.2f} {y:.2f} {ang}) '
            f'(effects (font (size {SIZE} {SIZE})) (justify {just})) (uuid "{uid()}"))')


def emit_instance(ic, X, Y, left, right, half_w, half_h, sheet_uuid) -> List[str]:
    ref = ic["ref"]
    libid = f"S_{sanitize(ref)}"
    out = [
        f'  (symbol (lib_id "{LIB}:{libid}") (at {X:.2f} {Y:.2f} 0) (unit 1)',
        f'    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid()}")',
        f'    (property "Reference" "{esc(ref)}" (at {X:.2f} {Y - half_h - 1.27:.2f} 0) (effects (font (size {SIZE} {SIZE}))))',
        f'    (property "Value" "{esc(ic["value"])}" (at {X:.2f} {Y + half_h + 1.27:.2f} 0) (effects (font (size {SIZE} {SIZE}))))',
        f'    (property "Footprint" "{esc(ic["fp"])}" (at {X:.2f} {Y:.2f} 0) (effects (font (size {SIZE} {SIZE})) (hide yes)))',
        f'    (property "Datasheet" "{esc(ic["ds"])}" (at {X:.2f} {Y:.2f} 0) (effects (font (size {SIZE} {SIZE})) (hide yes)))',
        f'    (property "MPN" "{esc(ic.get("mpn", ""))}" (at {X:.2f} {Y:.2f} 0) (effects (font (size {SIZE} {SIZE})) (hide yes)))',
    ]
    for pn, *_ in left + right:
        out.append(f'    (pin "{esc(pn)}" (uuid "{uid()}"))')
    out.append(f'    (instances (project "{PROJECT}" (path "/{sheet_uuid}" (reference "{esc(ref)}") (unit 1))))')
    out.append("  )")
    for i, (_pn, _fn, net, _) in enumerate(left):
        cx, cy = X - half_w - PIN_PITCH, Y - (half_h - PIN_PITCH * (i + 1))
        out.append(f'  (no_connect (at {cx:.2f} {cy:.2f}) (uuid "{uid()}"))' if net is None
                   else wire(cx, cy, cx - STUB, cy) + "\n" + label(net, cx - STUB, cy, 180))
    for i, (_pn, _fn, net, _) in enumerate(right):
        cx, cy = X + half_w + PIN_PITCH, Y - (half_h - PIN_PITCH * (i + 1))
        out.append(f'  (no_connect (at {cx:.2f} {cy:.2f}) (uuid "{uid()}"))' if net is None
                   else wire(cx, cy, cx + STUB, cy) + "\n" + label(net, cx + STUB, cy, 0))
    return out


# Rails that no symbol pin drives as power_out on this sheet (standalone ERC).
PWR_FLAG_RAILS = ["GND", "+5V", "+3V3", "+5V_RF", "+3V3_RF"]
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
            f'    (instances (project "{PROJECT}" (path "/{sheet_uuid}" (reference "#FLG{i + 1}") (unit 1)))))')
        out.append(wire(x, y0, x, y0 + STUB))
        out.append(label(rail, x, y0 + STUB, 270))
    return out


TITLE_BLOCK = """  (title_block
    (title "Commo Rev T -- 49 MHz I/Q receiver + VCXO-FM transmitter")
    (date "2026-09-29")
    (rev "T")
    (company "Griffing Technology LLC")
    (comment 1 "Plan: docs/plans/2026-09-29-002-feat-commo-revt-49mhz-iq-radio-plan.md (U2/U3)")
    (comment 2 "Generated by avionics/kicad/Commo/scripts/gen_commo_radio_sch.py -- do not hand-edit")
    (comment 3 "Author: Claude Opus 5.5 (2026-09-29); owner sgriffing; ENGINEERING REVIEW REQUIRED")
    (comment 4 "CC BY 4.0 -- values from commo_radio_design.py; pinouts from OEM datasheets")
  )"""


def main() -> None:
    sheet_uuid = uid()
    parts = ["(kicad_sch (version 20240101) (generator eeschema)", f'  (uuid "{uid()}")',
             '  (paper "A2")', TITLE_BLOCK, "  (lib_symbols", PWR_FLAG_LIB]
    X0, Y0, DX, COL_MAX_Y = 50.8, 76.2, 63.5, 400.0
    x, y = X0, Y0
    built, seen, placed = [], set(), []
    for ic in ICS:
        if ic["ref"] in seen:
            raise SystemExit(f"duplicate reference {ic['ref']}")
        seen.add(ic["ref"])
        libtext, left, right, hw, hh = lib_symbol(ic)
        parts.append(libtext)
        built.append((ic, left, right, hw, hh))
    for ic, left, right, hw, hh in built:
        if y + 2 * hh > COL_MAX_Y and y > Y0:
            x, y = x + DX, Y0
        placed.append((ic, x, y + hh, left, right, hw, hh))
        y += 2 * hh + 10.16
    parts.append("  )")
    for ic, X, Y, left, right, hw, hh in placed:
        parts += emit_instance(ic, X, Y, left, right, hw, hh, sheet_uuid)
    parts += emit_pwr_flags(X0, Y0 - 45.72, sheet_uuid)
    parts += ['  (sheet_instances (path "/" (page "1")))', ")"]
    OUT.write_text("\n".join(parts) + "\n")
    lib = ['(kicad_symbol_lib (version 20241209) (generator "gen_commo_radio_sch.py") (generator_version "9.0")']
    for ic, *_ in built:
        lib.append(lib_symbol(ic)[0].replace(f'(symbol "{LIB}:', '(symbol "', 1))
    lib.append(")")
    SYMLIB.write_text("\n".join(lib) + "\n")
    print(f"Wrote {OUT}\n  parts: {len(ICS)}   pins: {sum(len(i['pins']) for i in ICS)}")


if __name__ == "__main__":
    main()
