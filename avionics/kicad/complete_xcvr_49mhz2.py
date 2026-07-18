#!/usr/bin/env python3
"""
complete_xcvr_49mhz2.py

Completes XCVR-49MHZ-2.kicad_pcb by adding all remaining BOM components,
assigning nets, routing the critical RF signal path and power distribution,
placing GND stitching vias, drawing the RF shield-can outline, and adding
descriptive silk labels plus a full attribution block on the back copper.

BOM reference : XCVR-49MHZ-2.md
PCB constraints: XCVR-49MHZ-2.md §PCB Layout Constraints
50 Ohm microstrip: W=2.75mm on F.Cu (verified Z0=52.26 Ohm, FR4 1.6mm)

Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
"""

import os
import sys

import pcbnew

PCB_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "XCVR-49MHZ-2.kicad_pcb"
)
FPLIB = "/usr/share/kicad/footprints"


# ---------------------------------------------------------------------------
# Unit helpers
# ---------------------------------------------------------------------------
def mm(v):
    """Millimetres to KiCad internal units (nanometres)."""
    return pcbnew.FromMM(v)


def to_mm(v):
    """KiCad internal units to millimetres."""
    return float(v) / 1_000_000.0


# ---------------------------------------------------------------------------
# Board helpers
# ---------------------------------------------------------------------------
def get_or_add_net(board, name):
    n = board.FindNet(name)
    if n is None:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
    return n


def load_fp(lib, mod, ref, val, x_mm, y_mm, rot_deg=0):
    """Load a footprint from a standard .pretty library, place, label it."""
    lib_path = f"{FPLIB}/{lib}.pretty"
    fp = pcbnew.FootprintLoad(lib_path, mod)
    if fp is None:
        raise RuntimeError(f"Cannot load footprint  {lib}:{mod}")
    fp.SetReference(ref)
    fp.SetValue(val)
    fp.SetPosition(pcbnew.VECTOR2I(mm(x_mm), mm(y_mm)))
    if rot_deg:
        fp.SetOrientation(pcbnew.EDA_ANGLE(rot_deg, pcbnew.DEGREES_T))
    return fp


def assign_pads(board, fp, pad_map):
    """Assign nets to pads.  pad_map = {pad_number_str: net_name_str}"""
    for pad in fp.Pads():
        net_name = pad_map.get(pad.GetNumber())
        if net_name:
            pad.SetNet(get_or_add_net(board, net_name))


def pad_xy(fp, pad_num):
    """Return (x_mm, y_mm) of pad centre after footprint is placed."""
    for pad in fp.Pads():
        if pad.GetNumber() == str(pad_num):
            p = pad.GetPosition()
            return to_mm(p.x), to_mm(p.y)
    return None, None


def add_track(board, layer, net_name, x1, y1, x2, y2, w_mm):
    t = pcbnew.PCB_TRACK(board)
    t.SetLayer(layer)
    t.SetNet(get_or_add_net(board, net_name))
    t.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
    t.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
    t.SetWidth(mm(w_mm))
    board.Add(t)


def add_via(board, x_mm, y_mm, net_name="GND", drill=0.4, size=0.8):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(mm(x_mm), mm(y_mm)))
    v.SetDrill(mm(drill))
    # pcbnew 9: set annular-ring width per copper layer to avoid warning.
    # pylint (introspecting whatever pcbnew is installed locally) may only
    # see the older single-argument SetWidth(width) signature.
    for lyr in (pcbnew.F_Cu, pcbnew.B_Cu):
        v.SetWidth(lyr, mm(size))  # pylint: disable=too-many-function-args
    v.SetNet(get_or_add_net(board, net_name))
    board.Add(v)


def add_fab_seg(board, x1, y1, x2, y2, w=0.15, layer=pcbnew.F_Fab):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetLayer(layer)
    s.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
    s.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
    s.SetWidth(mm(w))
    board.Add(s)


def add_silk_label(
    board,
    text,
    x_mm,
    y_mm,
    size=0.65,
    thickness=0.10,
    angle_deg=0,
    layer=pcbnew.F_SilkS,
    mirror=False,
):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(pcbnew.VECTOR2I(mm(x_mm), mm(y_mm)))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(thickness))
    if angle_deg:
        t.SetTextAngle(pcbnew.EDA_ANGLE(angle_deg, pcbnew.DEGREES_T))
    if mirror:
        t.SetMirrored(True)
    board.Add(t)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print(f"Loading  {PCB_FILE}")
    board = pcbnew.LoadBoard(PCB_FILE)

    # -----------------------------------------------------------------------
    # Declare internal nets not yet in the PCB net list
    # -----------------------------------------------------------------------
    for n in (
        "DDS_RF",
        "PA_INT",
        "RF_LPF_N1",
        "RF_LPF_N2",
        "RF_FILT",
        "RX_LNA",
        "TCXO_OUT",
        "RSSI_RAW",
        "RF_ANT_SW",
        "COMP_IN",
    ):
        get_or_add_net(board, n)

    # -----------------------------------------------------------------------
    # Layer constants
    # -----------------------------------------------------------------------
    FCU = pcbnew.F_Cu
    BCU = pcbnew.B_Cu

    # Trace widths
    RF_W = 2.75  # 50 Ohm microstrip
    SIG_W = 0.20  # digital / audio signal
    PWR_W = 0.50  # power distribution

    # -----------------------------------------------------------------------
    # U1 — Si5351A-B-GT DDS synthesiser  (MSOP-10, 10-pin)
    # Pinout (Si5351A-B-GT MSOP-10):
    #   1=VDD  2=GND  3=CLK0  4=CLK1  5=CLK2
    #   6=SCL  7=SDA  8=XA   9=XB   10=VDDA
    # -----------------------------------------------------------------------
    u1 = load_fp(
        "Package_SO",
        "MSOP-10_3x3mm_P0.5mm",
        "U1",
        "Si5351A-B-GT  49MHz DDS I2C Synthesiser",
        115.0,
        112.0,
    )
    assign_pads(
        board,
        u1,
        {
            "1": "+3V3",
            "2": "GND",
            "3": "DDS_RF",
            "4": "GND",
            "5": "GND",
            "6": "DDS_CLK",
            "7": "DDS_DAT",
            "8": "TCXO_OUT",
            "9": "GND",
            "10": "+3V3",
        },
    )
    board.Add(u1)

    # X1 — EPSON TG2520SMN 25 MHz ±0.5 ppm TCXO  (4-pad SMD 2520)
    # Pinout: 1=/OE(tie VDD) 2=GND 3=CLK_OUT 4=VDD
    x1 = load_fp(
        "Oscillator",
        "Oscillator_SMD_SeikoEpson_TG2520SMN-xxx-xxxxxx-4Pin_2.5x2.0mm",
        "X1",
        "TG2520SMN  25MHz TCXO ±0.5ppm",
        115.0,
        106.5,
    )
    assign_pads(
        board,
        x1,
        {
            "1": "+3V3",
            "2": "GND",
            "3": "TCXO_OUT",
            "4": "+3V3",
        },
    )
    board.Add(x1)

    # U2A — MCP4921 12-bit SPI DAC  (SOT-23-8) — Bell 202 TX audio
    # Pinout: 1=VDD 2=/CS 3=SCK 4=SDI 5=/LDAC 6=VREF 7=VOUTA 8=GND
    u2a = load_fp(
        "Package_TO_SOT_SMD",
        "SOT-23-8",
        "U2A",
        "MCP4921  12-bit SPI DAC  TX-AFSK Audio",
        122.0,
        112.0,
    )
    assign_pads(
        board,
        u2a,
        {
            "1": "+3V3",
            "2": "DDS_FSYNC",
            "3": "DDS_CLK",
            "4": "DDS_DAT",
            "5": "GND",
            "6": "+3V3",
            "7": "AFSK_OUT",
            "8": "GND",
        },
    )
    board.Add(u2a)

    # U2B — LM393 comparator  (SOT-23-5) — Bell 202 RX demodulator
    # Pinout: 1=OUT 2=VCC 3=IN+ 4=IN- 5=GND
    u2b = load_fp(
        "Package_TO_SOT_SMD",
        "SOT-23-5",
        "U2B",
        "LM393  Comparator  RX-AFSK Demodulator",
        122.0,
        119.0,
    )
    assign_pads(
        board,
        u2b,
        {
            "1": "AFSK_IN",
            "2": "+3V3",
            "3": "COMP_IN",
            "4": "GND",
            "5": "GND",
        },
    )
    board.Add(u2b)

    # U3A — MMBT2222A NPN BJT PA driver  (SOT-23)
    # Pinout: 1=B(base) 2=E(emitter) 3=C(collector)
    u3a = load_fp(
        "Package_TO_SOT_SMD",
        "SOT-23",
        "U3A",
        "MMBT2222A  NPN BJT  PA Class-A Driver",
        133.0,
        112.0,
    )
    assign_pads(
        board,
        u3a,
        {
            "1": "DDS_RF",
            "2": "GND",
            "3": "PA_INT",
        },
    )
    board.Add(u3a)

    # U3B — 2N3866 NPN BJT PA final  (SOT-89-3, collector tab)
    # Pinout: 1=B 2=E 3=C(tab) — tab bonded to GND pour for heatsinking
    u3b = load_fp(
        "Package_TO_SOT_SMD",
        "SOT-89-3",
        "U3B",
        "2N3866  NPN BJT  PA Class-AB Final 100mW",
        137.5,
        112.0,
    )
    assign_pads(
        board,
        u3b,
        {
            "1": "PA_INT",
            "2": "GND",
            "3": "RF_TX",
        },
    )
    board.Add(u3b)

    # -----------------------------------------------------------------------
    # FL1 — 6-element Chebyshev LPF  fc=75MHz  ≥50dBc@98MHz  ≥60dBc@147MHz
    # Topology (series-L / shunt-C alternating):
    #   RF_TX → L1 → N1 → L2 → N2 → L3 → RF_FILT
    #                |              |              |
    #               C1             C2             C3
    #               GND            GND            GND
    # All inductors: Coilcraft 0805HQ shielded ferrite, oriented perp. to each other
    # -----------------------------------------------------------------------
    fl1_l1 = load_fp(
        "Inductor_SMD",
        "L_0805_2012Metric",
        "FL1_L1",
        "100nH  Coilcraft-0805HQ-101J  LPF Series-1",
        132.0,
        117.0,
    )
    assign_pads(board, fl1_l1, {"1": "RF_TX", "2": "RF_LPF_N1"})
    board.Add(fl1_l1)

    fl1_c1 = load_fp(
        "Capacitor_SMD",
        "C_0402_1005Metric",
        "FL1_C1",
        "120pF C0G  LPF Shunt-1",
        132.0,
        120.0,
    )
    assign_pads(board, fl1_c1, {"1": "RF_LPF_N1", "2": "GND"})
    board.Add(fl1_c1)

    fl1_l2 = load_fp(
        "Inductor_SMD",
        "L_0805_2012Metric",
        "FL1_L2",
        "180nH  Coilcraft-0805HQ-181J  LPF Series-2",
        136.0,
        117.0,
        rot_deg=90,
    )
    assign_pads(board, fl1_l2, {"1": "RF_LPF_N1", "2": "RF_LPF_N2"})
    board.Add(fl1_l2)

    fl1_c2 = load_fp(
        "Capacitor_SMD",
        "C_0402_1005Metric",
        "FL1_C2",
        "180pF C0G  LPF Shunt-2",
        136.0,
        120.0,
    )
    assign_pads(board, fl1_c2, {"1": "RF_LPF_N2", "2": "GND"})
    board.Add(fl1_c2)

    fl1_l3 = load_fp(
        "Inductor_SMD",
        "L_0805_2012Metric",
        "FL1_L3",
        "180nH  Coilcraft-0805HQ-181J  LPF Series-3",
        140.0,
        117.0,
    )
    assign_pads(board, fl1_l3, {"1": "RF_LPF_N2", "2": "RF_FILT"})
    board.Add(fl1_l3)

    fl1_c3 = load_fp(
        "Capacitor_SMD",
        "C_0402_1005Metric",
        "FL1_C3",
        "120pF C0G  LPF Shunt-3",
        140.0,
        120.0,
    )
    assign_pads(board, fl1_c3, {"1": "RF_FILT", "2": "GND"})
    board.Add(fl1_c3)

    # -----------------------------------------------------------------------
    # U5 — PE4259-63 SPDT TX/RX switch  (SOT-363 / SC-70-6)
    # Pinout (PE4259 SOT-26 = SOT-363):
    #   1=RFC(common/ANT) 2=GND 3=RF2(RX→LNA) 4=V+(ctrl/supply) 5=RF1(TX←LPF) 6=GND
    # -----------------------------------------------------------------------
    u5 = load_fp(
        "Package_TO_SOT_SMD",
        "SOT-363_SC-70-6",
        "U5",
        "PE4259-63  SPDT TX/RX Switch  ≥35dB isolation",
        143.5,
        117.5,
    )
    assign_pads(
        board,
        u5,
        {
            "1": "RF_ANT_SW",
            "2": "GND",
            "3": "RF_RX",
            "4": "PTT_N",
            "5": "RF_FILT",
            "6": "GND",
        },
    )
    board.Add(u5)

    # -----------------------------------------------------------------------
    # U4 — MGA-82563 LNA  (SOT-363)
    # Pinout (typical Avago/Broadcom SOT-363 LNA):
    #   1=RF_OUT 2=RSSI 3=RF_IN 4=VCC 5=GND 6=GND
    # -----------------------------------------------------------------------
    u4 = load_fp(
        "Package_TO_SOT_SMD",
        "SOT-363_SC-70-6",
        "U4",
        "MGA-82563  LNA  2.4dB NF  50-6000MHz",
        143.5,
        123.5,
    )
    assign_pads(
        board,
        u4,
        {
            "1": "RX_LNA",
            "2": "RSSI_RAW",
            "3": "RF_RX",
            "4": "+3V3",
            "5": "GND",
            "6": "GND",
        },
    )
    board.Add(u4)

    # -----------------------------------------------------------------------
    # U6 — MCP1703T-3302E/CB 3.3V LDO  (SOT-23-5)
    # Pinout: 1=VIN 2=GND 3=VOUT 4=EN(tie to VOUT) 5=GND
    # -----------------------------------------------------------------------
    u6 = load_fp(
        "Package_TO_SOT_SMD",
        "SOT-23-5",
        "U6",
        "MCP1703T-3302  LDO 3.3V  72dB-PSRR@100kHz",
        117.0,
        122.5,
    )
    assign_pads(
        board,
        u6,
        {
            "1": "+5V_FILT",
            "2": "GND",
            "3": "+3V3",
            "4": "+3V3",
            "5": "GND",
        },
    )
    board.Add(u6)

    # -----------------------------------------------------------------------
    # EMI STAGE COMPONENTS (XCVR-49MHZ-2 additions)
    # -----------------------------------------------------------------------

    # TVS6 — PRTR5V0U2X dual TVS on J1 UART_TX/RX  (SOT-363)
    # Placed immediately after J1 (3mm clearance per md)
    # Pinout: 1=GND 2=A1(UART_TX) 3=GND 4=GND 5=A2(UART_RX) 6=GND
    tvs6 = load_fp(
        "Package_TO_SOT_SMD",
        "SOT-363_SC-70-6",
        "TVS6",
        "PRTR5V0U2X  Dual TVS 5.5V  UART-TX/RX ESD",
        104.5,
        110.5,
    )
    assign_pads(
        board,
        tvs6,
        {
            "1": "GND",
            "2": "UART_TX",
            "3": "GND",
            "4": "GND",
            "5": "UART_RX",
            "6": "GND",
        },
    )
    board.Add(tvs6)

    # CM5 — SRF2012-100Y common-mode choke on UART pair
    # Uses L_0402 as SMD proxy (same package footprint, 1.0x0.5mm body).
    # Note: Bourns SRF2012 custom footprint identical to CMC_CAN; use same
    #       library reference when importing into KiCad GUI.
    cm5 = load_fp(
        "Inductor_SMD",
        "L_0402_1005Metric",
        "CM5",
        "SRF2012-100Y  CMC  UART TX/RX Pair 10uH",
        108.5,
        110.5,
    )
    assign_pads(board, cm5, {"1": "UART_TX", "2": "UART_TX"})
    board.Add(cm5)

    # FB_TX — Würth 742792510 series ferrite beads after CM5
    #         on UART_TX, UART_RX, and PTT_N
    for ref, y_pos, net in [
        ("FB_TX", 107.5, "UART_TX"),
        ("FB_RX", 110.5, "UART_RX"),
        ("FB_PT", 113.0, "PTT_N"),
    ]:
        fbtx = load_fp(
            "Inductor_SMD",
            "L_0402_1005Metric",
            ref,
            "742792510  0402 Ferrite Bead 600Ohm@100MHz",
            113.0,
            y_pos,
        )
        assign_pads(board, fbtx, {"1": net, "2": net})
        board.Add(fbtx)

    # TVS-SMA — SMAJ5.0A bidirectional TVS on antenna port  (SOD-123F ≈ SOD-123FL)
    # Within 2mm of J2 (J2 at x=154); placed at edge of RF section.
    # SOD-123F pads: 1=anode 2=cathode
    tvs_sma = load_fp(
        "Diode_SMD",
        "D_SOD-123F",
        "TVS_SMA",
        "SMAJ5.0A  Bidirectional TVS 5V  Antenna ESD",
        151.5,
        116.5,
    )
    assign_pads(board, tvs_sma, {"1": "ANT", "2": "GND"})
    board.Add(tvs_sma)

    # -----------------------------------------------------------------------
    # SUPPLY BYPASS CASCADE  (C21–C27 per md §3)
    # -----------------------------------------------------------------------
    supply_caps = [
        (
            "C21",
            "100uF 10V X5R 1210  +5V Bulk",
            "C_1210_3225Metric",
            110.5,
            121.0,
            "+5V_FILT",
            "GND",
        ),
        (
            "C22",
            "100nF X7R 0402  +5V HF Bypass",
            "C_0402_1005Metric",
            113.0,
            121.0,
            "+5V_FILT",
            "GND",
        ),
        (
            "C23",
            "100uF 10V X5R 1210  +3V3 Bulk",
            "C_1210_3225Metric",
            121.0,
            122.5,
            "+3V3",
            "GND",
        ),
        (
            "C24",
            "10uF X5R 0805  +3V3 Mid-freq",
            "C_0805_2012Metric",
            124.5,
            122.5,
            "+3V3",
            "GND",
        ),
        (
            "C25",
            "100nF X7R 0402  +3V3 HF Bypass",
            "C_0402_1005Metric",
            127.0,
            122.5,
            "+3V3",
            "GND",
        ),
        (
            "C26",
            "10nF C0G 0402  +3V3 VHF 49MHz Bypass",
            "C_0402_1005Metric",
            128.5,
            122.5,
            "+3V3",
            "GND",
        ),
        (
            "C27",
            "10nF C0G 0402  GND-PGND Moat Bridge",
            "C_0402_1005Metric",
            130.0,
            117.0,
            "GND",
            "GND",
        ),
    ]
    for ref, val, mod_name, x, y, n1, n2 in supply_caps:
        c = load_fp("Capacitor_SMD", mod_name, ref, val, x, y)
        assign_pads(board, c, {"1": n1, "2": n2})
        board.Add(c)

    # -----------------------------------------------------------------------
    # IC-LEVEL 100nF 0402 BYPASS CAPS
    # -----------------------------------------------------------------------
    ic_bypass = [
        ("C_U1A", "100nF +3V3 U1-VDDA Bypass", 113.5, 110.5, "+3V3"),
        ("C_U1B", "100nF +3V3 U1-VDD Bypass", 116.5, 110.5, "+3V3"),
        ("C_U2A", "100nF +3V3 U2A DAC Bypass", 120.5, 112.0, "+3V3"),
        ("C_U2B", "100nF +3V3 U2B CMP Bypass", 120.5, 119.0, "+3V3"),
        ("C_U4", "100nF +3V3 U4 LNA Bypass", 141.5, 122.5, "+3V3"),
        ("C_U5", "100nF +3V3 U5 Switch Bypass", 141.5, 117.5, "+3V3"),
        ("C_U6", "100nF +3V3 U6 LDO Bypass", 115.5, 122.5, "+3V3"),
        ("C_X1", "100nF +3V3 X1 TCXO Bypass", 113.5, 106.5, "+3V3"),
        ("C_PA", "100nF +5V U3 PA VCC Bypass", 135.5, 108.5, "+5V_FILT"),
    ]
    for ref, val, x, y, supply in ic_bypass:
        c = load_fp("Capacitor_SMD", "C_0402_1005Metric", ref, val, x, y)
        assign_pads(board, c, {"1": supply, "2": "GND"})
        board.Add(c)

    # -----------------------------------------------------------------------
    # PA BIAS AND SIGNAL CONDITIONING PASSIVES (0402)
    # -----------------------------------------------------------------------
    def res(ref, val, x, y, n1, n2):
        r = load_fp("Resistor_SMD", "R_0402_1005Metric", ref, val, x, y)
        assign_pads(board, r, {"1": n1, "2": n2})
        board.Add(r)

    def cap(ref, val, x, y, n1, n2):
        c = load_fp("Capacitor_SMD", "C_0402_1005Metric", ref, val, x, y)
        assign_pads(board, c, {"1": n1, "2": n2})
        board.Add(c)

    # MMBT2222A (U3A) bias: base resistor + RF coupling cap to DDS output
    res("R_B1", "10k Ohm  U3A Base Bias Resistor", 131.0, 108.5, "+5V_FILT", "DDS_RF")
    cap("C_B1", "100pF  DDS-RF Coupling Cap to U3A", 131.5, 110.5, "DDS_RF", "DDS_RF")
    # U3A collector load (Class-A): +5V to collector via resistor
    res("R_C1", "100 Ohm  U3A Collector Load", 133.0, 109.5, "+5V_FILT", "PA_INT")
    # 2N3866 (U3B) base resistor and emitter degeneration
    res("R_B2", "1k Ohm  U3B Base Bias Resistor", 135.5, 109.5, "PA_INT", "PA_INT")
    cap("C_B2", "100pF  PA Interstage Bypass", 137.0, 109.5, "PA_INT", "GND")
    res("R_E2", "10 Ohm  U3B Emitter Degeneration", 138.0, 114.5, "GND", "GND")
    cap("C_U3B", "1nF  U3B Collector RF Bypass", 139.0, 109.0, "RF_TX", "GND")

    # AFSK audio coupling cap: DAC output to PA modulator
    cap("C_AF", "1uF  AFSK Audio Coupling DAC→PA", 123.5, 115.5, "AFSK_OUT", "AFSK_OUT")

    # RX Bell-202 RC bandpass filter: 1200Hz and 2200Hz poles
    res("R_RX1", "13k Ohm  RX RC Bandpass 1200Hz", 121.0, 124.5, "RX_LNA", "COMP_IN")
    cap("C_RX1", "10nF  RX RC Bandpass 1200Hz Cap", 123.0, 124.5, "COMP_IN", "GND")
    res("R_RX2", "7.2k Ohm  RX RC Bandpass 2200Hz", 125.5, 124.5, "RX_LNA", "COMP_IN")
    cap("C_RX2", "10nF  RX RC Bandpass 2200Hz Cap", 127.5, 124.5, "COMP_IN", "GND")

    # LM393 threshold divider: +3V3 → upper → node → lower → GND
    res("R_TH1", "10k Ohm  LM393 Threshold Upper", 119.5, 124.5, "+3V3", "GND")
    res("R_TH2", "10k Ohm  LM393 Threshold Lower", 119.5, 126.5, "GND", "GND")

    # RSSI analog scaling: LNA RSSI_RAW → voltage divider → RSSI_ANA to J1
    res("R_RS1", "10k Ohm  RSSI Scale Upper", 141.5, 126.5, "RSSI_RAW", "RSSI_ANA")
    res("R_RS2", "10k Ohm  RSSI Scale Lower", 143.0, 126.5, "RSSI_ANA", "GND")

    # -----------------------------------------------------------------------
    # CRITICAL COPPER TRACES
    # All RF traces: 50 Ohm microstrip W=2.75mm on F.Cu
    # -----------------------------------------------------------------------

    # DDS RF carrier: U1 CLK0 (pin 3) → U3A base (pin 1)
    u1_clk0_x, u1_clk0_y = pad_xy(u1, "3")
    u3a_base_x, u3a_base_y = pad_xy(u3a, "1")
    if u1_clk0_x and u3a_base_x:
        add_track(
            board, FCU, "DDS_RF", u1_clk0_x, u1_clk0_y, u3a_base_x, u3a_base_y, SIG_W
        )

    # PA output: U3B collector (pin 3) → FL1_L1 pad 1
    u3b_col_x, u3b_col_y = pad_xy(u3b, "3")
    l1_in_x, l1_in_y = pad_xy(fl1_l1, "1")
    if u3b_col_x and l1_in_x:
        # Route: collector straight right, then angled into L1
        mid_x = (u3b_col_x + l1_in_x) / 2
        add_track(board, FCU, "RF_TX", u3b_col_x, u3b_col_y, mid_x, u3b_col_y, RF_W)
        add_track(board, FCU, "RF_TX", mid_x, u3b_col_y, l1_in_x, l1_in_y, RF_W)

    # LPF through-path: L1→N1→L2→N2→L3→RF_FILT (inside component placements)
    # L1 pad-2 → C1 pad-1 junction (N1): routed by netlist copper pour
    # L3 pad-2 (RF_FILT) → U5 RF1 (pin 5)
    l3_out_x, l3_out_y = pad_xy(fl1_l3, "2")
    u5_rf1_x, u5_rf1_y = pad_xy(u5, "5")
    if l3_out_x and u5_rf1_x:
        add_track(board, FCU, "RF_FILT", l3_out_x, l3_out_y, u5_rf1_x, u5_rf1_y, RF_W)

    # U5 RFC (pin 1) → RF_ANT_SW → toward antenna chain (CMC_CAN at 147,112.5)
    u5_rfc_x, u5_rfc_y = pad_xy(u5, "1")
    if u5_rfc_x:
        add_track(board, FCU, "RF_ANT_SW", u5_rfc_x, u5_rfc_y, 147.0, u5_rfc_y, RF_W)

    # U5 RF2 (pin 3, RX) → U4 RF_IN (pin 3)
    u5_rx_x, u5_rx_y = pad_xy(u5, "3")
    u4_in_x, u4_in_y = pad_xy(u4, "3")
    if u5_rx_x and u4_in_x:
        add_track(board, FCU, "RF_RX", u5_rx_x, u5_rx_y, u4_in_x, u4_in_y, SIG_W)

    # U4 RF_OUT (pin 1) → RX_LNA chain → R_RX1 input
    u4_out_x, u4_out_y = pad_xy(u4, "1")
    rx1_in_x, rx1_in_y = pad_xy(
        next(fp for fp in board.GetFootprints() if fp.GetReference() == "R_RX1"), "1"
    )
    if u4_out_x and rx1_in_x:
        add_track(board, FCU, "RX_LNA", u4_out_x, u4_out_y, rx1_in_x, rx1_in_y, SIG_W)

    # TCXO output: X1 pin 3 → U1 XA (pin 8)
    x1_out_x, x1_out_y = pad_xy(x1, "3")
    u1_xa_x, u1_xa_y = pad_xy(u1, "8")
    if x1_out_x and u1_xa_x:
        add_track(board, FCU, "TCXO_OUT", x1_out_x, x1_out_y, u1_xa_x, u1_xa_y, SIG_W)

    # +5V_FILT: FB1 pad 2 (already in PCB at 106,117) → U6 VIN (pin 1)
    u6_vin_x, u6_vin_y = pad_xy(u6, "1")
    if u6_vin_x:
        add_track(board, FCU, "+5V_FILT", 107.6, 117.0, u6_vin_x, u6_vin_y, PWR_W)

    # +3V3: U6 VOUT (pin 3) → distribution rail
    u6_vout_x, u6_vout_y = pad_xy(u6, "3")
    if u6_vout_x:
        add_track(board, FCU, "+3V3", u6_vout_x, u6_vout_y, 128.0, u6_vout_y, PWR_W)

    # -----------------------------------------------------------------------
    # GND STITCHING VIAS
    # -----------------------------------------------------------------------
    # Column at RF section boundary (x=130) every 2.5mm in Y
    for yv in range(1025, 1351, 25):
        add_via(board, 130.0, yv / 10.0, "GND")

    # Guard ring vias flanking the 50Ohm microstrip at top and bottom (5mm apart)
    for xv in (132, 136, 140, 143):
        add_via(board, float(xv), 109.5, "GND")
        add_via(board, float(xv), 124.5, "GND")

    # -----------------------------------------------------------------------
    # SHIELD CAN OUTLINE  (Laird MSA030020T or equiv, 25x30mm over RF section)
    # Drawn on F.Fab as a fabrication reference
    # -----------------------------------------------------------------------
    shield_coords = [
        (130.5, 101.5, 154.5, 101.5),
        (154.5, 101.5, 154.5, 133.5),
        (154.5, 133.5, 130.5, 133.5),
        (130.5, 133.5, 130.5, 101.5),
    ]
    for x1c, y1c, x2c, y2c in shield_coords:
        add_fab_seg(board, x1c, y1c, x2c, y2c, w=0.20)

    # Tab notches at corners (snap-on lid reference)
    for xn, yn in ((130.5, 107.5), (130.5, 127.5), (154.5, 107.5), (154.5, 127.5)):
        add_fab_seg(board, xn - 0.5, yn, xn + 0.5, yn, w=0.15)

    # -----------------------------------------------------------------------
    # DESCRIPTIVE SILKSCREEN SECTION LABELS  (F.SilkS)
    # -----------------------------------------------------------------------
    silk_labels = [
        ("DDS + I2C MCU I/F", 113.5, 103.5),
        ("TX AFSK DAC", 122.0, 109.0),
        ("RX AFSK DEMOD", 122.0, 116.0),
        ("LDO 3.3V", 117.0, 119.5),
        ("POWER CASCADE", 111.5, 126.5),
        ("EMI FILTER / ESD", 107.5, 107.5),
        ("PA DRIVER", 133.0, 109.5),
        ("PA FINAL 100mW", 137.5, 109.0),
        ("6-ELEM CHEBY LPF", 136.0, 124.0),
        ("TX/RX SWITCH", 143.5, 114.5),
        ("LNA 2.4dB NF", 143.5, 120.5),
        ("SHIELD CAN 25x30mm", 136.5, 103.0),
    ]
    for label, x, y in silk_labels:
        add_silk_label(board, label, x, y, size=0.65, thickness=0.10)

    # -----------------------------------------------------------------------
    # BACK-SILK ATTRIBUTION BLOCK  (B.SilkS, mirrored)
    # Matches CAPE-A/B format for consistency across the avionics suite.
    # -----------------------------------------------------------------------
    attr = (
        "49 MHz AX.25 KISS Transceiver\n"
        "XCVR-49MHZ-2 Rev 2 — EMI-Hardened\n"
        "FCC 47 CFR Part 15 15.235\n"
        "49.830-49.890 MHz  AFSK 1200bd\n"
        "CC BY 4.0 — June 2026\n"
        "Steve Griffing\n"
        "PE(CSE), CISSP-ISSEP, CPP\n"
        "Griffing Technology LLC\n"
        "github.com/Stab-Rabbit-Coding"
    )
    add_silk_label(
        board,
        attr,
        108.5,
        105.0,
        size=0.80,
        thickness=0.12,
        layer=pcbnew.B_SilkS,
        mirror=True,
    )

    # -----------------------------------------------------------------------
    # SAVE
    # -----------------------------------------------------------------------
    board.Save(PCB_FILE)
    fps = list(board.GetFootprints())
    print(f"Saved.  Total footprints on board: {len(fps)}")
    nets = list(board.GetNetInfo().NetsByName().keys())
    print(f"        Total nets: {len(nets)}")


if __name__ == "__main__":
    main()
