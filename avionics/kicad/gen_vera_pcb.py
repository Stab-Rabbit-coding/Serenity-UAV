#!/usr/bin/env python3
"""gen_vera_pcb.py — Generate Vera.kicad_pcb (component placement + net-correct footprints).

Vera is a STANDALONE board (not a PocketBeagle 2 Industrial cape). Double-sided, 4-layer
FR4, rounded corners (3mm radius, matching Wash/Kaylee convention).

EMI HARDENING (added 2026-07-03, matching Wash/Zoe Rev R baseline — see TODO.md §1.2c and
Vera.md "EMI Hardening Status"): both Ethernet ports now carry the full magnetics +
common-mode-choke + TVS chain (Wurth 749010012A transformer, 2x Bourns SRF2012-100Y
common-mode chokes, 2x Nexperia PRTR5V0U2X TVS per port), and the CAN-FD transceiver is the
galvanically-isolated TI ISOW1044BDFMR (replacing the earlier non-isolated TCAN1042HG-Q1)
with its own common-mode-choke+TVS on the bus side.
All of these reuse REAL footprints already verified in this project's own Wash/Zoe generator
(gen_cape_a2.py / gen_cape_a2_pcb.py) — not fabricated placeholders.

COMPACTION: component body sizes were corrected to REAL verified datasheet dimensions
(2026-07-03 research pass) instead of rough first-guess estimates:
    AM62A7      18x18mm   (484-ball FCBGA/FCCSP, TI datasheet)
    KSZ9477     14x14mm   (128-TQFP-EP, Microchip datasheet)
    MSPM0G3507  7.1x4.9mm (VSSOP-28/DGS package — smaller than the VQFN-48 first assumed)
    SLB9670      5x5mm    (PG-VQFN-32, Infineon datasheet)
    TPS65219     5x5mm    (VQFN-32/RSM, TI datasheet)
This, plus using both copper faces, is what let the board shrink significantly from the
110x190mm single-sided first draft.

IMPORTANT — footprint honesty policy for this file:
    U1 (AM62A7, 484-ball BGA), U2 (KSZ9477), U3 (MSPM0G3507), U5 (SLB9670), U_PMIC
    (TPS65219) do NOT get a fabricated "realistic-looking" BGA/QFN pad grid here.
    Inventing a plausible-looking full ball-out with no datasheet to back it up would be
    worse than an honest placeholder. Instead each gets a deliberately simple TWO-ROW pad
    placeholder (matching the schematic symbol's pin list), with pads clearly labelled and
    a fab-layer warning text. These MUST be replaced with the real manufacturer footprint
    before fabrication (tracked in TODO.md §1.2c). Pad PITCH on these placeholders is tuned
    per-component to roughly match real proportions (see comp_2row_placeholder docstring) —
    it is still not a real ball-out/lead-frame, just less absurdly oversized.

    NOTE: as of 2026-07-07 the hand-edited KiCad output in `avionics/kicad/Vera.kicad_pcb`
    was further compacted to the current 1.0 × 2.75 in (25.4 × 69.85 mm) baseline in the GUI.
    This script still generates the 78×80 mm pre-compaction layout. Do not re-run it unless you intend to
    overwrite the manual compaction, or update the generator to match the new baseline.

    U4 (ISOW1044BDFMR, SOIC-16W), T1/T2 (Wurth 749010012A magnetics), CMC1-5 (SRF2012-100Y),
    D1-5 (PRTR5V0U2X), and all connectors use REAL KiCad footprint geometry.

Author: Steve Griffing PE(CSE) CISSP-ISSEP CPP  |  CC BY 4.0
Usage:  python3 gen_vera_pcb.py
"""

import itertools
import math
from pathlib import Path

# ---------------------------------------------------------------------------
# UUID management
# ---------------------------------------------------------------------------
_UID_PREFIX = "7e5aec00-0000-0000-0000-"
_uid_seq = itertools.count(1)


def _uid() -> str:
    return f"{_UID_PREFIX}{next(_uid_seq):012d}"


# ---------------------------------------------------------------------------
# Net registry — must match the nets present in Vera.kicad_sch's netlist export
# ---------------------------------------------------------------------------
_NET_NAMES = [
    "",
    "+3V3",
    "+5V",
    "CAM_PWDN",
    "CAM_RESET_N",
    "CAM_SCL",
    "CAM_SDA",
    "CANFD_H",
    "CANFD_ISOGND",
    "CANFD_ISO_H",
    "CANFD_ISO_L",
    "CANFD_L",
    "CANFD_RX",
    "CANFD_STBY_N",
    "CANFD_TX",
    "CSI_CLK_N",
    "CSI_CLK_P",
    "CSI_D0_N",
    "CSI_D0_P",
    "ETH_IN_KSZ_RXN",
    "ETH_IN_KSZ_RXP",
    "ETH_IN_KSZ_TXN",
    "ETH_IN_KSZ_TXP",
    "ETH_IN_RXN",
    "ETH_IN_RXP",
    "ETH_IN_TXN",
    "ETH_IN_TXP",
    "ETH_IN_XFMR_RXN",
    "ETH_IN_XFMR_RXP",
    "ETH_IN_XFMR_TXN",
    "ETH_IN_XFMR_TXP",
    "ETH_OUT_KSZ_RXN",
    "ETH_OUT_KSZ_RXP",
    "ETH_OUT_KSZ_TXN",
    "ETH_OUT_KSZ_TXP",
    "ETH_OUT_RXN",
    "ETH_OUT_RXP",
    "ETH_OUT_TXN",
    "ETH_OUT_TXP",
    "ETH_OUT_XFMR_RXN",
    "ETH_OUT_XFMR_RXP",
    "ETH_OUT_XFMR_TXN",
    "ETH_OUT_XFMR_TXP",
    "GND",
    "LASER_CATHODE",
    "LASER_EN",
    "LASER_GATE",
    "LASER_IND",
    "LASER_KEY_IN",
    "MCU_NRST",
    "MCU_SWCLK",
    "MCU_SWDIO",
    "MDC",
    "MDIO",
    "PGND",
    "PGND_SHIELD",
    "PMIC_EN",
    "PMIC_SCL",
    "PMIC_SDA",
    "RGMII1_RXC",
    "RGMII1_RXCTL",
    "RGMII1_RXD0",
    "RGMII1_TXC",
    "RGMII1_TXCTL",
    "RGMII1_TXD0",
    "SD_CARD_NC",
    "SOC_BOOT0",
    "SOC_PORZ",
    "SW_1V2",
    "SW_INT_N",
    "SW_RESET_N",
    "SW_SPI_CS",
    "SW_SPI_MISO",
    "SW_SPI_MOSI",
    "SW_SPI_SCK",
    "SW_XTAL_25M",
    "TPM_PIRQ",
    "TPM_RESET_N",
    "TPM_SPI_CS",
    "TPM_SPI_MISO",
    "TPM_SPI_MOSI",
    "TPM_SPI_SCK",
    "UART_A2M",
    "UART_M2A",
    "UART_TOF_RX",
    "UART_TOF_TX",
    "VDD_CORE",
    "VDDR",
    "VDDSHV",
]
_NET_BY_NAME = {name: i for i, name in enumerate(_NET_NAMES)}
NO_NET = (0, "")


def N(name: str):
    if name not in _NET_BY_NAME:
        raise KeyError(f"net {name!r} not registered in _NET_NAMES")
    return (_NET_BY_NAME[name], name)


# ---------------------------------------------------------------------------
# Low-level S-expression helpers (same conventions as gen_kaylee_pcb.py)
# ---------------------------------------------------------------------------


def _fp(lib_ref, ref, value, x, y, angle=0.0, side="F"):
    ang_s = f" {angle}" if angle else ""
    cu, silk, fab = (f"{side}.Cu", f"{side}.SilkS", f"{side}.Fab")
    mirror = " (justify mirror)" if side == "B" else ""
    return [
        f'\t(footprint "{lib_ref}" (layer "{cu}")',
        f"\t\t(at {x:.4f} {y:.4f}{ang_s})",
        f'\t\t(property "Reference" "{ref}" (at 0 -3.5 0) (layer "{silk}")',
        f"\t\t\t(effects (font (size 1.0 1.0) (thickness 0.15)){mirror}))",
        f'\t\t(property "Value" "{value}" (at 0 3.5 0) (layer "{fab}")',
        f"\t\t\t(effects (font (size 1.0 1.0) (thickness 0.15)){mirror}))",
        f'\t\t(property "Footprint" "{lib_ref}" (at 0 0 0) (layer "{fab}")',
        f"\t\t\t(effects (font (size 1.0 1.0) (thickness 0.15)) (hide yes)))",
        f"\t\t(attr smd)",
    ]


def _fp_tht(lib_ref, ref, value, x, y, angle=0.0, side="F"):
    ang_s = f" {angle}" if angle else ""
    cu, silk, fab = (f"{side}.Cu", f"{side}.SilkS", f"{side}.Fab")
    return [
        f'\t(footprint "{lib_ref}" (layer "{cu}")',
        f"\t\t(at {x:.4f} {y:.4f}{ang_s})",
        f'\t\t(property "Reference" "{ref}" (at 0 -3.5 0) (layer "{silk}")',
        f"\t\t\t(effects (font (size 1.0 1.0) (thickness 0.15))))",
        f'\t\t(property "Value" "{value}" (at 0 3.5 0) (layer "{fab}")',
        f"\t\t\t(effects (font (size 1.0 1.0) (thickness 0.15))))",
        f'\t\t(property "Footprint" "{lib_ref}" (at 0 0 0) (layer "{fab}")',
        f"\t\t\t(effects (font (size 1.0 1.0) (thickness 0.15)) (hide yes)))",
    ]


def _fp_end():
    return [f'\t\t(uuid "{_uid()}")', "\t)"]


def _pad_smd(num, px, py, w, h, net, layers=None, side="F"):
    ni, nn = net
    net_s = f' (net {ni} "{nn}")' if ni else ""
    if layers is None:
        layers = f'"{side}.Cu" "{side}.Mask" "{side}.Paste"'
    return (
        f'\t\t(pad "{num}" smd roundrect (at {px:.4f} {py:.4f}) (size {w:.4f} {h:.4f})'
        f' (layers {layers}) (roundrect_rratio 0.25){net_s} (uuid "{_uid()}"))'
    )


def _pad_tht(num, px, py, w, h, drill, net, shape="circle"):
    ni, nn = net
    net_s = f' (net {ni} "{nn}")' if ni else ""
    if shape == "roundrect":
        shape_s, rr = "roundrect", " (roundrect_rratio 0.25)"
    elif shape == "oval":
        shape_s, rr = "oval", ""
    else:
        shape_s, rr = "circle", ""
    return (
        f'\t\t(pad "{num}" thru_hole {shape_s} (at {px:.4f} {py:.4f}) (size {w:.4f} {h:.4f})'
        f' (drill {drill:.4f}) (layers "*.Cu" "*.Mask"){rr}{net_s} (uuid "{_uid()}"))'
    )


def _pad_npth(px, py, drill):
    return (
        f'\t\t(pad "" np_thru_hole circle (at {px:.4f} {py:.4f}) (size {drill:.4f} {drill:.4f})'
        f' (drill {drill:.4f}) (layers "*.Cu" "*.Mask") (uuid "{_uid()}"))'
    )


def _crtyd(x1, y1, x2, y2, layer=None, side="F"):
    layer = layer or f"{side}.CrtYd"
    return [
        f"\t\t(fp_rect (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f})"
        f' (layer "{layer}") (stroke (width 0.05) (type default)) (uuid "{_uid()}"))'
    ]


def _fab_rect(x1, y1, x2, y2, layer=None, side="F"):
    layer = layer or f"{side}.Fab"
    return [
        f"\t\t(fp_rect (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f})"
        f' (layer "{layer}") (stroke (width 0.1) (type default)) (uuid "{_uid()}"))'
    ]


def _fab_text(txt, x, y, layer=None, size=1.0, side="F"):
    layer = layer or f"{side}.Fab"
    mirror = " (justify mirror)" if side == "B" else ""
    return [
        f'\t\t(fp_text user "{txt}" (at {x:.4f} {y:.4f}) (layer "{layer}")',
        f"\t\t\t(effects (font (size {size:.2f} {size:.2f}) (thickness 0.1)){mirror})",
        f'\t\t\t(uuid "{_uid()}"))',
    ]


# ---------------------------------------------------------------------------
# Component generators
# ---------------------------------------------------------------------------


def comp_mounting_hole(ref, x, y):
    lines = _fp_tht("MountingHole:MountingHole_3.2mm_M3", ref, "M3", x, y)
    lines += _crtyd(-3.5, -3.5, 3.5, 3.5)
    lines += _fab_rect(-3.5, -3.5, 3.5, 3.5)
    lines.append(_pad_npth(0.0, 0.0, 3.2))
    lines += _fp_end()
    return lines


def comp_0402(ref, value, x, y, p1_net=NO_NET, p2_net=NO_NET, angle=0.0, side="F"):
    lib = "Resistor_SMD:R_0402_1005Metric"
    lines = _fp(lib, ref, value, x, y, angle, side=side)
    lines += _crtyd(-0.98, -0.73, 0.98, 0.73, side=side)
    lines += _fab_rect(-0.5, -0.25, 0.5, 0.25, side=side)
    lines.append(_pad_smd("1", -0.51, 0.0, 0.54, 0.64, p1_net, side=side))
    lines.append(_pad_smd("2", 0.51, 0.0, 0.54, 0.64, p2_net, side=side))
    lines += _fp_end()
    return lines


def comp_sot23(
    ref, value, x, y, g_net=NO_NET, d_net=NO_NET, s_net=NO_NET, angle=0.0, side="F"
):
    """SOT-23 3-pin (AO3400): pin1=G, pin2=S, pin3=D (standard SOT-23 N-FET pinout).
    When side="B", X is mirrored (standard KiCad convention for back footprints)."""
    lib = "Package_TO_SOT_SMD:SOT-23"
    mx = -1 if side == "B" else 1
    lines = _fp(lib, ref, value, x, y, angle, side=side)
    lines += _crtyd(-1.85, -1.5, 1.85, 1.5, side=side)
    lines += _fab_rect(-1.4, -0.75, 1.4, 0.75, side=side)
    lines.append(_pad_smd("1", -0.95 * mx, 1.0, 0.9, 1.1, g_net, side=side))
    lines.append(_pad_smd("2", 0.95 * mx, 1.0, 0.9, 1.1, s_net, side=side))
    lines.append(_pad_smd("3", 0.0, -1.0, 0.9, 1.1, d_net, side=side))
    lines += _fp_end()
    return lines


def comp_soic8(ref, value, x, y, nets=None, angle=0.0, side="F"):
    nets = nets or {}
    lib = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
    mx = -1 if side == "B" else 1
    lines = _fp(lib, ref, value, x, y, angle, side=side)
    lines += _crtyd(-3.38, -3.13, 3.38, 3.13, side=side)
    lines += _fab_rect(-1.95, -2.45, 1.95, 2.45, side=side)
    pads_l = [("1", -1.905), ("2", -0.635), ("3", 0.635), ("4", 1.905)]
    pads_r = [("5", 1.905), ("6", 0.635), ("7", -0.635), ("8", -1.905)]
    for num, py in pads_l:
        lines.append(
            _pad_smd(num, -2.475 * mx, py, 1.95, 0.60, nets.get(num, NO_NET), side=side)
        )
    for num, py in pads_r:
        lines.append(
            _pad_smd(num, 2.475 * mx, py, 1.95, 0.60, nets.get(num, NO_NET), side=side)
        )
    lines += _fp_end()
    return lines


def comp_soic16w(ref, value, x, y, nets=None, angle=0.0, side="F"):
    """SOIC-16W_7.5x10.3mm_P1.27mm — real footprint, used for ISOW1044BDFMR
    (same part + footprint already verified/working on Wash/Zoe)."""
    nets = nets or {}
    lib = "Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm"
    mx = -1 if side == "B" else 1
    lines = _fp(lib, ref, value, x, y, angle, side=side)
    lines += _crtyd(-4.7, -5.55, 4.7, 5.55, side=side)
    lines += _fab_rect(-3.75, -5.15, 3.75, 5.15, side=side)
    pads_l = [(str(i + 1), -5.715 + i * 1.27) for i in range(8)]
    pads_r = [(str(16 - i), 5.715 - i * 1.27) for i in range(8)]
    for num, py in pads_l:
        lines.append(
            _pad_smd(num, -4.25 * mx, py, 2.0, 0.6, nets.get(num, NO_NET), side=side)
        )
    for num, py in pads_r:
        lines.append(
            _pad_smd(num, 4.25 * mx, py, 2.0, 0.6, nets.get(num, NO_NET), side=side)
        )
    lines += _fp_end()
    return lines


def comp_eth_xfmr(ref, value, x, y, nets=None, angle=0.0, side="F"):
    """Transformer_SMD:Wurth_749010012A_10-100BASE-TX — real footprint, 8-pin
    (1-4 = PHY side TXP/TXN/RXP/RXN, 5-8 = LINE side TXP/TXN/RXP/RXN),
    already used on Wash/Zoe's real Ethernet EMI-hardening chain."""
    nets = nets or {}
    lib = "Transformer_SMD:Wurth_749010012A_10-100BASE-TX"
    mx = -1 if side == "B" else 1
    lines = _fp(lib, ref, value, x, y, angle, side=side)
    lines += _crtyd(-6.0, -4.5, 6.0, 4.5, side=side)
    lines += _fab_rect(-5.5, -4.0, 5.5, 4.0, side=side)
    pads_l = [(str(i + 1), -3.81 + i * 2.54) for i in range(4)]
    pads_r = [(str(i + 5), 3.81 - i * 2.54) for i in range(4)]
    for num, py in pads_l:
        lines.append(
            _pad_smd(num, -5.0 * mx, py, 1.8, 1.0, nets.get(num, NO_NET), side=side)
        )
    for num, py in pads_r:
        lines.append(
            _pad_smd(num, 5.0 * mx, py, 1.8, 1.0, nets.get(num, NO_NET), side=side)
        )
    lines += _fp_end()
    return lines


def comp_cmc_2012(
    ref,
    value,
    x,
    y,
    l1a_net=NO_NET,
    l1b_net=NO_NET,
    l2a_net=NO_NET,
    l2b_net=NO_NET,
    angle=0.0,
    side="F",
):
    """Inductor_SMD:L_Taiyo-Yuden_NR-20xx — real footprint, Bourns SRF2012-100Y
    common-mode choke (4-terminal, 2012 metric ~2.0x1.2mm body)."""
    lib = "Inductor_SMD:L_Taiyo-Yuden_NR-20xx"
    mx = -1 if side == "B" else 1
    lines = _fp(lib, ref, value, x, y, angle, side=side)
    lines += _crtyd(-1.3, -0.9, 1.3, 0.9, side=side)
    lines += _fab_rect(-1.0, -0.6, 1.0, 0.6, side=side)
    lines.append(_pad_smd("1", -0.85 * mx, -0.5, 0.7, 0.5, l1a_net, side=side))
    lines.append(_pad_smd("2", 0.85 * mx, -0.5, 0.7, 0.5, l1b_net, side=side))
    lines.append(_pad_smd("3", -0.85 * mx, 0.5, 0.7, 0.5, l2a_net, side=side))
    lines.append(_pad_smd("4", 0.85 * mx, 0.5, 0.7, 0.5, l2b_net, side=side))
    lines += _fp_end()
    return lines


def comp_tvs_sot363(
    ref, value, x, y, a1_net=NO_NET, a2_net=NO_NET, k_net=NO_NET, angle=0.0, side="F"
):
    """Package_TO_SOT_SMD:SOT-363_SC-70-6 — real footprint, Nexperia PRTR5V0U2X
    dual TVS/ESD array. Only 3 of the 6 physical pads carry a net (A1/A2/K,
    matching the simplified schematic symbol); the other 3 are NC."""
    lib = "Package_TO_SOT_SMD:SOT-363_SC-70-6"
    mx = -1 if side == "B" else 1
    lines = _fp(lib, ref, value, x, y, angle, side=side)
    lines += _crtyd(-1.4, -1.05, 1.4, 1.05, side=side)
    lines += _fab_rect(-1.05, -0.625, 1.05, 0.625, side=side)
    # NOTE: pad NUMBERS below are deliberately reassigned vs. the real SOT-363
    # physical pad numbering, so they match the SIMPLIFIED schematic symbol's
    # pin numbers (1=A1, 2=A2, 3=K) exactly — KiCad matches schematic<->PCB by
    # ref+pin NUMBER, not by net name or physical position, and a mismatch
    # here caused a real schematic-parity DRC failure caught in this session.
    lines.append(_pad_smd("1", -0.65 * mx, -0.85, 0.4, 0.5, a1_net, side=side))
    lines.append(_pad_smd("2", 0.0, -0.85, 0.4, 0.5, a2_net, side=side))
    lines.append(_pad_smd("3", 0.65 * mx, 0.85, 0.4, 0.5, k_net, side=side))
    lines.append(_pad_smd("4", 0.65 * mx, -0.85, 0.4, 0.5, NO_NET, side=side))
    lines.append(_pad_smd("5", 0.0, 0.85, 0.4, 0.5, NO_NET, side=side))
    lines.append(_pad_smd("6", -0.65 * mx, 0.85, 0.4, 0.5, NO_NET, side=side))
    lines += _fp_end()
    return lines


def comp_jst_gh_2p(ref, value, x, y, p1_net=NO_NET, p2_net=NO_NET):
    lib = "Connector_JST:JST_GH_BM02B-GHS-TBT_1x02-1MP_P1.25mm_Vertical"
    lines = _fp(lib, ref, value, x, y)
    lines += _crtyd(-3.2, -1.8, 3.2, 3.3)
    lines += _fab_rect(-0.95, 0.5, 0.95, 3.3)
    lines.append(_pad_smd("MP", -2.475, -1.4, 1.0, 2.8, NO_NET))
    lines.append(_pad_smd("MP", 2.475, -1.4, 1.0, 2.8, NO_NET))
    lines.append(_pad_smd("1", -0.625, 1.95, 0.60, 1.70, p1_net))
    lines.append(_pad_smd("2", 0.625, 1.95, 0.60, 1.70, p2_net))
    lines += _fp_end()
    return lines


def comp_jst_sh_2p(ref, value, x, y, p1_net=NO_NET, p2_net=NO_NET):
    """JST-SH BM02B-SRSS-TB 1x02 P1.00mm SMD vertical (ultra-low-profile laser lead)."""
    lib = "Connector_JST:JST_SH_BM02B-SRSS-TB_1x02-1MP_P1.00mm_Vertical"
    lines = _fp(lib, ref, value, x, y)
    lines += _crtyd(-2.4, -1.4, 2.4, 2.6)
    lines += _fab_rect(-0.75, 0.3, 0.75, 2.6)
    lines.append(_pad_smd("MP", -1.75, -1.0, 0.8, 2.0, NO_NET))
    lines.append(_pad_smd("MP", 1.75, -1.0, 0.8, 2.0, NO_NET))
    lines.append(_pad_smd("1", -0.5, 1.5, 0.5, 1.3, p1_net))
    lines.append(_pad_smd("2", 0.5, 1.5, 0.5, 1.3, p2_net))
    lines += _fp_end()
    return lines


def comp_jst_gh_4p(ref, value, x, y, p_nets=None):
    p_nets = p_nets or [NO_NET] * 4
    lib = "Connector_JST:JST_GH_BM04B-GHS-TBT_1x04-1MP_P1.25mm_Vertical"
    lines = _fp(lib, ref, value, x, y)
    lines += _crtyd(-4.0, -1.8, 4.0, 3.3)
    lines += _fab_rect(-1.875, 0.5, 1.875, 3.3)
    for mpx in (-3.1, 3.1):
        lines.append(_pad_smd("MP", mpx, -1.4, 1.0, 2.8, NO_NET))
    pads_x = [-1.875, -0.625, 0.625, 1.875]
    for i, px in enumerate(pads_x):
        lines.append(
            _pad_smd(
                str(i + 1),
                px,
                1.95,
                0.60,
                1.70,
                p_nets[i] if i < len(p_nets) else NO_NET,
            )
        )
    lines += _fp_end()
    return lines


def comp_jst_gh_5p(ref, value, x, y, p_nets=None):
    """Approximation of Connector_JST:JST_GH_SM05B-GHS-TB_1x05-1MP_P1.25mm_Horizontal
    — the REAL footprint used on Wash for its Ethernet ports (5-pin: GND + 4
    signal). Exact pad geometry not independently re-verified this session;
    this is a reasonable horizontal-SMD approximation at the real 1.25mm pitch."""
    p_nets = p_nets or [NO_NET] * 5
    lib = "Connector_JST:JST_GH_SM05B-GHS-TB_1x05-1MP_P1.25mm_Horizontal"
    lines = _fp(lib, ref, value, x, y)
    lines += _crtyd(-5.5, -2.2, 5.5, 2.2)
    lines += _fab_rect(-4.7, -1.6, 4.7, 1.6)
    lines.append(_pad_smd("MP", 0.0, -2.0, 1.2, 0.8, NO_NET))
    lines.append(_pad_smd("MP", 0.0, 2.0, 1.2, 0.8, NO_NET))
    pads_x = [-2.5, -1.25, 0.0, 1.25, 2.5]
    for i, px in enumerate(pads_x):
        lines.append(
            _pad_smd(
                str(i + 1), px, 0.0, 0.6, 1.4, p_nets[i] if i < len(p_nets) else NO_NET
            )
        )
    lines += _fp_end()
    return lines


def comp_crystal_2p(ref, value, x, y, p1_net=NO_NET, p2_net=NO_NET, side="F"):
    """2-pad SMD crystal footprint — matches Y1's SIMPLIFIED 2-pin schematic
    symbol (lib_symbol_2pin_h) exactly. A real 25MHz crystal is usually a 4-pad
    package (2 signal + 2 case-ground); if/when the schematic symbol is upgraded
    to model the case-ground pins, this footprint must gain matching pads too —
    a prior 4-pad version of this footprint failed schematic-parity DRC because
    the symbol only ever had 2 pins."""
    lib = "Crystal:Crystal_SMD_2016-2Pin_2.0x1.6mm"
    lines = _fp(lib, ref, value, x, y, side=side)
    lines += _crtyd(-1.35, -0.95, 1.35, 0.95, side=side)
    lines += _fab_rect(-1.0, -0.8, 1.0, 0.8, side=side)
    lines.append(_pad_smd("1", -0.85, 0, 1.0, 1.3, p1_net, side=side))
    lines.append(_pad_smd("2", 0.85, 0, 1.0, 1.3, p2_net, side=side))
    lines += _fp_end()
    return lines


def comp_2row_placeholder(
    ref,
    value,
    x,
    y,
    left,
    right,
    size,
    footprint_name,
    netmap,
    side="F",
    pitch=2.54,
    pad_size=(2.2, 0.5),
):
    """DELIBERATELY OBVIOUS placeholder footprint for U1/U2/U3/U5/U_PMIC — two columns
    of rectangular pads. NOT a real package outline/ball-out. Loud F.Fab warning text
    included on every instance.

    `size` is the REAL verified body half-extent (drives the courtyard/outline only —
    a genuine size cue for board-area planning). `pitch` is the PAD row spacing, which
    is deliberately NOT tied to `size`: at a fixed 2.54mm pitch, a real small package
    (e.g. MSPM0G3507's 28-pin VSSOP, 7.1x4.9mm body) with a dozen-plus modeled signal
    pins would produce a placeholder footprint many times taller than the real part,
    defeating the whole point of using its real body size for board-area planning.
    Callers pass a tighter `pitch` for small real packages (see gen_pcb() call sites).

    netmap: dict of {pin_local_name: net_name}, taken VERBATIM from the exact
    glabel_pin()/pwr_pin() calls in gen_vera.py for this component — deliberately
    NOT a single shared remap table, because several ICs reuse the same local pin
    name (e.g. "RESET_N", "GND") for DIFFERENT actual nets, and a shared table
    caused a real net-swap bug caught by kicad-cli's schematic-parity DRC check.

    side="B" mounts on the back (B.Cu) — used to stack the control-half ICs
    directly underneath U1's footprint area to compact the board (both faces
    populated), with X mirrored per KiCad's back-footprint convention."""
    hx, hy = size
    mx = -1 if side == "B" else 1
    pw, ph = pad_size
    lines = _fp(footprint_name, ref, value, x, y, side=side)
    lines += _crtyd(-hx - 2.0, -hy - 1.2, hx + 2.0, hy + 1.2, side=side)
    lines += _fab_rect(-hx, -hy, hx, hy, side=side)
    lines += _fab_text("PLACEHOLDER - NOT REAL PACKAGE", 0, 0, size=0.6, side=side)

    def net_of(pname):
        net_name = netmap[pname]
        return N("GND") if net_name == "GND" else N(net_name)

    pad_x = hx + pw / 2 + 0.5
    n = len(left)
    start_y = -((n - 1) * pitch) / 2.0
    for i, (pname, pnum, ptype) in enumerate(left):
        py = start_y + i * pitch
        lines.append(_pad_smd(pnum, -pad_x * mx, py, pw, ph, net_of(pname), side=side))
    n = len(right)
    start_y = -((n - 1) * pitch) / 2.0
    for i, (pname, pnum, ptype) in enumerate(right):
        py = start_y + i * pitch
        lines.append(_pad_smd(pnum, pad_x * mx, py, pw, ph, net_of(pname), side=side))
    lines += _fp_end()
    return lines


def rounded_board_outline(w, h, radius=3.0):
    """4 straight Edge.Cuts segments + 4 corner arcs, matching Wash/Kaylee's
    real rounded-corner board outline convention."""
    r = radius
    k = r * (1 - math.sqrt(2) / 2)  # 45-degree arc midpoint offset
    lines = []

    def line(x1, y1, x2, y2):
        return [
            f"\t(gr_line (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f})",
            '\t\t(stroke (width 0.05) (type solid)) (layer "Edge.Cuts")',
            f'\t\t(uuid "{_uid()}"))',
        ]

    def arc(x1, y1, mx, my, x2, y2):
        return [
            f"\t(gr_arc (start {x1:.4f} {y1:.4f}) (mid {mx:.4f} {my:.4f}) (end {x2:.4f} {y2:.4f})",
            '\t\t(stroke (width 0.05) (type solid)) (layer "Edge.Cuts")',
            f'\t\t(uuid "{_uid()}"))',
        ]

    lines += line(r, 0, w - r, 0)
    lines += line(w, r, w, h - r)
    lines += line(w - r, h, r, h)
    lines += line(0, h - r, 0, r)
    lines += arc(0, r, k, k, r, 0)
    lines += arc(w - r, 0, w - k, k, w, r)
    lines += arc(w, h - r, w - k, h - k, w - r, h)
    lines += arc(r, h, k, h - k, 0, h - r)
    return lines


# ---------------------------------------------------------------------------
# Pin lists — copied from gen_vera.py (kept in sync manually; both files are
# generator scripts checked into the same commit whenever either changes)
# ---------------------------------------------------------------------------

AM62A_SIZE = (9.0, 9.0)  # AM62A7: 18x18mm 484-ball FCBGA/FCCSP (real body size)
AM62A_L = [
    ("VDD_CORE", "A1", "power_in"),
    ("VDDSHV_MAIN", "A2", "power_in"),
    ("VDDR_CORE", "A3", "power_in"),
    ("GND", "A4", "power_in"),
    ("PORz", "B1", "input"),
    ("BOOT_MODE0", "B2", "input"),
    ("CAM_I2C_SDA", "C1", "bidirectional"),
    ("CAM_I2C_SCL", "C2", "input"),
    ("CAM_RESET_N", "C3", "output"),
    ("CAM_PWDN", "C4", "output"),
    ("CSI_CLK_P", "D1", "input"),
    ("CSI_CLK_N", "D2", "input"),
    ("CSI_D0_P", "D3", "input"),
    ("CSI_D0_N", "D4", "input"),
]
AM62A_R = [
    ("RGMII1_TXC", "P1", "output"),
    ("RGMII1_TXCTL", "P2", "output"),
    ("RGMII1_TXD0", "P3", "output"),
    ("RGMII1_RXC", "P4", "input"),
    ("RGMII1_RXCTL", "P5", "input"),
    ("RGMII1_RXD0", "P6", "input"),
    ("MDIO", "P7", "bidirectional"),
    ("MDC", "P8", "output"),
    ("MCU_UART_TX", "R1", "output"),
    ("MCU_UART_RX", "R2", "input"),
    ("SD_CARD", "R3", "bidirectional"),
]

MSPM0_SIZE = (3.55, 2.45)  # MSPM0G3507 VSSOP-28 (DGS): real body ~7.1x4.9mm
MSPM0_L = [
    ("+3V3", "1", "power_in"),
    ("GND", "2", "power_in"),
    ("NRST", "3", "input"),
    ("SWCLK", "4", "input"),
    ("SWDIO", "5", "bidirectional"),
    ("MCAN_TX", "6", "output"),
    ("MCAN_RX", "7", "input"),
    ("UART0_TX", "8", "output"),
    ("UART0_RX", "9", "input"),
    ("UART1_TX", "22", "output"),
    ("UART1_RX", "23", "input"),
]
MSPM0_R = [
    ("SPI0_CS_TPM", "10", "output"),
    ("SPI0_SCK", "11", "output"),
    ("SPI0_MOSI", "12", "output"),
    ("SPI0_MISO", "13", "input"),
    ("TPM_PIRQ", "14", "input"),
    ("SPI1_CS_SW", "15", "output"),
    ("SPI1_SCK", "16", "output"),
    ("SPI1_MOSI", "17", "output"),
    ("SPI1_MISO", "18", "input"),
    ("GPIO_LASER_EN", "19", "output"),
    ("GPIO_LASER_KEY", "20", "input"),
    ("GPIO_LASER_IND", "21", "output"),
]

KSZ_SIZE = (7.0, 7.0)  # KSZ9477STXI: 128-TQFP-EP, real body 14x14mm
KSZ_L = [
    ("+3V3", "1", "power_in"),
    ("+1V2", "2", "power_in"),
    ("GND", "3", "power_in"),
    ("RESET_N", "4", "input"),
    ("INT_N", "5", "output"),
    ("XTAL_25M", "6", "input"),
    ("SPI_CS_HOST", "7", "input"),
    ("SPI_SCK_HOST", "8", "input"),
    ("SPI_MOSI_HOST", "9", "input"),
    ("SPI_MISO_HOST", "10", "output"),
]
KSZ_R = [
    ("P1_RGMII_TXC", "20", "input"),
    ("P1_RGMII_TXCTL", "21", "input"),
    ("P1_RGMII_TXD0", "22", "input"),
    ("P1_RGMII_RXC", "23", "output"),
    ("P1_RGMII_RXCTL", "24", "output"),
    ("P1_RGMII_RXD0", "25", "output"),
    ("P2_TXP", "26", "output"),
    ("P2_TXN", "27", "output"),
    ("P2_RXP", "28", "input"),
    ("P2_RXN", "29", "input"),
    ("P3_TXP", "30", "output"),
    ("P3_TXN", "31", "output"),
    ("P3_RXP", "32", "input"),
    ("P3_RXN", "33", "input"),
]

TPM_SIZE = (2.5, 2.5)  # Infineon SLB9670: PG-VQFN-32, real body ~5x5mm
TPM_L = [
    ("+3V3", "1", "power_in"),
    ("GND", "2", "power_in"),
    ("SPI_CS", "3", "input"),
    ("SPI_CLK", "4", "input"),
]
TPM_R = [
    ("SPI_MOSI", "5", "input"),
    ("SPI_MISO", "6", "output"),
    ("PIRQ", "7", "output"),
    ("RESET_N", "8", "input"),
]

PMIC_SIZE = (2.5, 2.5)  # TI TPS65219: VQFN-32 (RSM), real body 5x5mm
PMIC_L = [
    ("VIN", "1", "power_in"),
    ("GND", "2", "power_in"),
    ("EN", "3", "input"),
    ("I2C_SDA", "4", "bidirectional"),
    ("I2C_SCL", "5", "input"),
]
PMIC_R = [
    ("BUCK1_VDD_CORE", "10", "output"),
    ("BUCK2_VDDSHV", "11", "output"),
    ("BUCK3_VDDR", "12", "output"),
    ("LDO1_3V3_CTRL", "13", "output"),
]

# ---------------------------------------------------------------------------
# Per-component pin-name -> net-name maps, transcribed VERBATIM from the
# glabel_pin()/pwr_pin() calls in gen_vera.py's gen_sch(). Deliberately
# per-component (not one shared table) — see comp_2row_placeholder docstring.
# ---------------------------------------------------------------------------

PMIC_NETMAP = {
    "VIN": "+5V",
    "GND": "GND",
    "EN": "PMIC_EN",
    "I2C_SDA": "PMIC_SDA",
    "I2C_SCL": "PMIC_SCL",
    "BUCK1_VDD_CORE": "VDD_CORE",
    "BUCK2_VDDSHV": "VDDSHV",
    "BUCK3_VDDR": "VDDR",
    "LDO1_3V3_CTRL": "+3V3",
}

AM62A_NETMAP = {
    "VDD_CORE": "VDD_CORE",
    "VDDSHV_MAIN": "VDDSHV",
    "VDDR_CORE": "VDDR",
    "GND": "GND",
    "PORz": "SOC_PORZ",
    "BOOT_MODE0": "SOC_BOOT0",
    "CAM_I2C_SDA": "CAM_SDA",
    "CAM_I2C_SCL": "CAM_SCL",
    "CAM_RESET_N": "CAM_RESET_N",
    "CAM_PWDN": "CAM_PWDN",
    "CSI_CLK_P": "CSI_CLK_P",
    "CSI_CLK_N": "CSI_CLK_N",
    "CSI_D0_P": "CSI_D0_P",
    "CSI_D0_N": "CSI_D0_N",
    "RGMII1_TXC": "RGMII1_TXC",
    "RGMII1_TXCTL": "RGMII1_TXCTL",
    "RGMII1_TXD0": "RGMII1_TXD0",
    "RGMII1_RXC": "RGMII1_RXC",
    "RGMII1_RXCTL": "RGMII1_RXCTL",
    "RGMII1_RXD0": "RGMII1_RXD0",
    "MDIO": "MDIO",
    "MDC": "MDC",
    "MCU_UART_TX": "UART_A2M",
    "MCU_UART_RX": "UART_M2A",
    "SD_CARD": "SD_CARD_NC",
}

MSPM0_NETMAP = {
    "+3V3": "+3V3",
    "GND": "GND",
    "NRST": "MCU_NRST",
    "SWCLK": "MCU_SWCLK",
    "SWDIO": "MCU_SWDIO",
    "MCAN_TX": "CANFD_TX",
    "MCAN_RX": "CANFD_RX",
    "UART0_TX": "UART_M2A",
    "UART0_RX": "UART_A2M",
    "UART1_TX": "UART_TOF_TX",
    "UART1_RX": "UART_TOF_RX",
    "SPI0_CS_TPM": "TPM_SPI_CS",
    "SPI0_SCK": "TPM_SPI_SCK",
    "SPI0_MOSI": "TPM_SPI_MOSI",
    "SPI0_MISO": "TPM_SPI_MISO",
    "TPM_PIRQ": "TPM_PIRQ",
    "SPI1_CS_SW": "SW_SPI_CS",
    "SPI1_SCK": "SW_SPI_SCK",
    "SPI1_MOSI": "SW_SPI_MOSI",
    "SPI1_MISO": "SW_SPI_MISO",
    "GPIO_LASER_EN": "LASER_EN",
    "GPIO_LASER_KEY": "LASER_KEY_IN",
    "GPIO_LASER_IND": "LASER_IND",
}

TPM_NETMAP = {
    "+3V3": "+3V3",
    "GND": "GND",
    "SPI_CS": "TPM_SPI_CS",
    "SPI_CLK": "TPM_SPI_SCK",
    "SPI_MOSI": "TPM_SPI_MOSI",
    "SPI_MISO": "TPM_SPI_MISO",
    "PIRQ": "TPM_PIRQ",
    "RESET_N": "TPM_RESET_N",
}

KSZ_NETMAP = {
    "+3V3": "+3V3",
    "+1V2": "SW_1V2",
    "GND": "GND",
    "RESET_N": "SW_RESET_N",
    "INT_N": "SW_INT_N",
    "XTAL_25M": "SW_XTAL_25M",
    "SPI_CS_HOST": "SW_SPI_CS",
    "SPI_SCK_HOST": "SW_SPI_SCK",
    "SPI_MOSI_HOST": "SW_SPI_MOSI",
    "SPI_MISO_HOST": "SW_SPI_MISO",
    "P1_RGMII_TXC": "RGMII1_TXC",
    "P1_RGMII_TXCTL": "RGMII1_TXCTL",
    "P1_RGMII_TXD0": "RGMII1_TXD0",
    "P1_RGMII_RXC": "RGMII1_RXC",
    "P1_RGMII_RXCTL": "RGMII1_RXCTL",
    "P1_RGMII_RXD0": "RGMII1_RXD0",
    "P2_TXP": "ETH_IN_KSZ_TXP",
    "P2_TXN": "ETH_IN_KSZ_TXN",
    "P2_RXP": "ETH_IN_KSZ_RXP",
    "P2_RXN": "ETH_IN_KSZ_RXN",
    "P3_TXP": "ETH_OUT_KSZ_TXP",
    "P3_TXN": "ETH_OUT_KSZ_TXN",
    "P3_RXP": "ETH_OUT_KSZ_RXP",
    "P3_RXN": "ETH_OUT_KSZ_RXN",
}

ISOW_NETS = {
    "1": N("GND"),
    "2": N("CANFD_TX"),
    "3": N("CANFD_STBY_N"),
    "4": N("CANFD_RX"),
    "6": N("+3V3"),
    "10": N("CANFD_ISOGND"),
    "11": N("+5V"),
    "14": N("CANFD_ISO_L"),
    "15": N("CANFD_ISO_H"),
}


# ---------------------------------------------------------------------------
# Board
# ---------------------------------------------------------------------------


def gen_pcb() -> str:
    W, H = 78.0, 80.0
    MH_M = 4.0

    lines: list[str] = []
    lines += [
        "(kicad_pcb",
        "\t(version 20241229)",
        '\t(generator "pcbnew")',
        '\t(generator_version "9.0")',
        "\t(general",
        "\t\t(thickness 1.6)",
        "\t\t(legacy_teardrops no)",
        "\t)",
        '\t(paper "A3")',
        "\t(title_block",
        '\t\t(title "Vera — Nose/Cargo-Bay Vision, ToF & Laser Board")',
        '\t\t(date "2026-07-03")',
        '\t\t(rev "-")',
        '\t\t(comment 1 "Serenity UAV — STANDALONE board, NOT a PocketBeagle 2 Industrial cape")',
        '\t\t(comment 2 "CC BY 4.0 creativecommons.org/licenses/by/4.0")',
        '\t\t(comment 3 "78×80 mm pre-compaction layout, 4-layer FR4, DOUBLE-SIDED, EMI-hardened — actual hand-compacted board is 1.0 × 2.75 in (25.4 × 69.85 mm) in avionics/kicad/Vera.kicad_pcb")',
        '\t\t(comment 4 "U1/U2/U3/U5/U_PMIC use PLACEHOLDER footprints — not real packages, see docstring")',
        "\t)",
    ]
    lines += [
        "\t(layers",
        '\t\t(0 "F.Cu" signal)',
        '\t\t(31 "B.Cu" signal)',
        '\t\t(1 "In1.Cu" power)',
        '\t\t(2 "In2.Cu" power)',
        '\t\t(32 "B.Adhes" user)',
        '\t\t(33 "F.Adhes" user)',
        '\t\t(34 "B.Paste" user)',
        '\t\t(35 "F.Paste" user)',
        '\t\t(36 "B.SilkS" user "B.Silkscreen")',
        '\t\t(37 "F.SilkS" user "F.Silkscreen")',
        '\t\t(38 "B.Mask" user)',
        '\t\t(39 "F.Mask" user)',
        '\t\t(44 "Edge.Cuts" user)',
        '\t\t(46 "B.CrtYd" user "B.Courtyard")',
        '\t\t(47 "F.CrtYd" user "F.Courtyard")',
        '\t\t(48 "B.Fab" user)',
        '\t\t(49 "F.Fab" user)',
        "\t)",
    ]
    lines += [
        "\t(setup",
        "\t\t(pad_to_mask_clearance 0)",
        "\t\t(allow_soldermask_bridges_in_footprints no)",
        "\t\t(tenting front back)",
        "\t)",
    ]
    for idx, name in enumerate(_NET_NAMES):
        lines.append(f'\t(net {idx} "{name}")')

    lines += rounded_board_outline(W, H, radius=3.0)
    lines += [
        f'\t(gr_text "Vera Rev - (design exploration)" (at {W/2:.2f} {H + 3.0:.2f} 0) (layer "F.Fab")',
        f"\t\t(effects (font (size 1.5 1.5) (thickness 0.15)))",
        f'\t\t(uuid "{_uid()}"))',
        f'\t(gr_text "Griffing Technology LLC | CC BY 4.0" (at {W/2:.2f} {H + 5.5:.2f} 0) (layer "F.Fab")',
        f"\t\t(effects (font (size 1.0 1.0) (thickness 0.1)))",
        f'\t\t(uuid "{_uid()}"))',
    ]

    for i, (mx, my) in enumerate(
        [(MH_M, MH_M), (W - MH_M, MH_M), (MH_M, H - MH_M), (W - MH_M, H - MH_M)]
    ):
        lines += comp_mounting_hole(f"H{i+1}", mx, my)

    # ------------------------------------------------------------------
    # DOUBLE-SIDED COMPACTION: U1 (AM62A7) populates the FRONT of the board's
    # upper area; U_PMIC/U3/U5/U2 populate the BACK of that SAME area (legal —
    # opposite copper faces don't collide). Real (smaller) body sizes plus
    # both-side population are what let this shrink well below the original
    # 110x190mm single-sided draft.
    # ------------------------------------------------------------------

    # --- FRONT: U1 (AM62A7) + camera connectors ---
    lines += comp_2row_placeholder(
        "U1",
        "TI AM62A7",
        24.0,
        22.0,
        AM62A_L,
        AM62A_R,
        AM62A_SIZE,
        "Vera:BGA484_18x18mm_PLACEHOLDER",
        AM62A_NETMAP,
        pitch=1.27,
    )

    lines += comp_jst_gh_4p(
        "J_CAM1",
        "CSI_CLK/D0",
        62.0,
        10.0,
        p_nets=[N("CSI_CLK_P"), N("CSI_CLK_N"), N("CSI_D0_P"), N("CSI_D0_N")],
    )
    lines += comp_jst_gh_4p(
        "J_CAM2",
        "CAM SDA/SCL/RST/3V3",
        62.0,
        22.0,
        p_nets=[N("CAM_SDA"), N("CAM_SCL"), N("CAM_RESET_N"), N("+3V3")],
    )

    # --- BACK: U_PMIC, U5 (TPM), U3 (MSPM0G3507), U2 (KSZ9477) — stacked
    # under U1's footprint region, plus Y1 crystal next to U2. ---
    lines += comp_2row_placeholder(
        "U_PMIC",
        "TPS65219",
        12.0,
        8.0,
        PMIC_L,
        PMIC_R,
        PMIC_SIZE,
        "Vera:PMIC_TPS65219_PLACEHOLDER_VQFN32",
        PMIC_NETMAP,
        side="B",
        pitch=1.0,
    )

    lines += comp_2row_placeholder(
        "U5",
        "Infineon SLB9670",
        34.0,
        8.0,
        TPM_L,
        TPM_R,
        TPM_SIZE,
        "Vera:TPM_SLB9670_PLACEHOLDER_VQFN32",
        TPM_NETMAP,
        side="B",
        pitch=1.0,
    )

    lines += comp_2row_placeholder(
        "U3",
        "TI MSPM0G3507",
        12.0,
        34.0,
        MSPM0_L,
        MSPM0_R,
        MSPM0_SIZE,
        "Vera:MSPM0G3507_PLACEHOLDER_VSSOP28",
        MSPM0_NETMAP,
        side="B",
        pitch=0.65,
        pad_size=(1.1, 0.3),
    )
    lines += comp_0402(
        "C_MCU1", "100nF", 12.0, 44.0, p1_net=N("+3V3"), p2_net=N("GND"), side="B"
    )

    lines += comp_2row_placeholder(
        "U2",
        "Microchip KSZ9477",
        36.0,
        36.0,
        KSZ_L,
        KSZ_R,
        KSZ_SIZE,
        "Vera:QFN128_KSZ9477_PLACEHOLDER_14x14mm",
        KSZ_NETMAP,
        side="B",
        pitch=0.9,
    )
    lines += comp_crystal_2p(
        "Y1", "25MHz", 36.0, 50.0, p1_net=N("SW_XTAL_25M"), p2_net=N("GND"), side="B"
    )

    # =====================================================================
    # EMI hardening — Ethernet ports: KSZ9477 -> Wurth 749010012A magnetics
    # -> 2x SRF2012-100Y CMC -> 2x PRTR5V0U2X TVS -> JST-GH 5P connector.
    # All FRONT side. Matches Wash/Zoe Rev R baseline.
    # =====================================================================

    def eth_port_chain(
        port, x0, y0, xfmr_ref, cmc_tx, cmc_rx, tvs_tx, tvs_rx, conn_ref
    ):
        lines2 = []
        lines2 += comp_eth_xfmr(
            xfmr_ref,
            "Wurth 749010012A",
            x0,
            y0,
            nets={
                "1": N(f"{port}_KSZ_TXP"),
                "2": N(f"{port}_KSZ_TXN"),
                "3": N(f"{port}_KSZ_RXP"),
                "4": N(f"{port}_KSZ_RXN"),
                "5": N(f"{port}_XFMR_TXP"),
                "6": N(f"{port}_XFMR_TXN"),
                "7": N(f"{port}_XFMR_RXP"),
                "8": N(f"{port}_XFMR_RXN"),
            },
        )
        lines2 += comp_cmc_2012(
            cmc_tx,
            "SRF2012-100Y (TX)",
            x0 + 8,
            y0 - 2,
            l1a_net=N(f"{port}_XFMR_TXP"),
            l1b_net=N(f"{port}_TXP"),
            l2a_net=N(f"{port}_XFMR_TXN"),
            l2b_net=N(f"{port}_TXN"),
        )
        lines2 += comp_cmc_2012(
            cmc_rx,
            "SRF2012-100Y (RX)",
            x0 + 8,
            y0 + 2,
            l1a_net=N(f"{port}_XFMR_RXP"),
            l1b_net=N(f"{port}_RXP"),
            l2a_net=N(f"{port}_XFMR_RXN"),
            l2b_net=N(f"{port}_RXN"),
        )
        lines2 += comp_tvs_sot363(
            tvs_tx,
            "PRTR5V0U2X (TX)",
            x0 + 14,
            y0 - 2,
            a1_net=N(f"{port}_TXP"),
            a2_net=N(f"{port}_TXN"),
            k_net=N("GND"),
        )
        lines2 += comp_tvs_sot363(
            tvs_rx,
            "PRTR5V0U2X (RX)",
            x0 + 14,
            y0 + 2,
            a1_net=N(f"{port}_RXP"),
            a2_net=N(f"{port}_RXN"),
            k_net=N("GND"),
        )
        lines2 += comp_jst_gh_5p(
            conn_ref,
            f"JST-GH 5P (shielded) Ethernet ring",
            x0 + 24,
            y0,
            p_nets=[
                N("PGND_SHIELD"),
                N(f"{port}_TXP"),
                N(f"{port}_TXN"),
                N(f"{port}_RXP"),
                N(f"{port}_RXN"),
            ],
        )
        return lines2

    lines += eth_port_chain(
        "ETH_IN", 46.0, 48.0, "T1", "CMC1", "CMC2", "D1", "D2", "J_ETH_IN"
    )
    lines += eth_port_chain(
        "ETH_OUT", 46.0, 60.0, "T2", "CMC3", "CMC4", "D3", "D4", "J_ETH_OUT"
    )

    # =====================================================================
    # EMI hardening — CAN-FD: TI ISOW1044BDFMR (isolated) -> SRF2012-100Y CMC
    # -> PRTR5V0U2X TVS -> JST-GH 4P connector.
    # =====================================================================
    lines += comp_soic16w("U4", "TI ISOW1044BDFMR", 12.0, 48.0, nets=ISOW_NETS)
    lines += comp_cmc_2012(
        "CMC5",
        "SRF2012-100Y (CAN)",
        20.0,
        48.0,
        l1a_net=N("CANFD_ISO_H"),
        l1b_net=N("CANFD_H"),
        l2a_net=N("CANFD_ISO_L"),
        l2b_net=N("CANFD_L"),
    )
    lines += comp_tvs_sot363(
        "D5",
        "PRTR5V0U2X (CAN)",
        26.0,
        48.0,
        a1_net=N("CANFD_H"),
        a2_net=N("CANFD_L"),
        k_net=N("PGND"),
    )
    lines += comp_jst_gh_4p(
        "J_CANFD",
        "5V/CANH/CANL/GND",
        12.0,
        60.0,
        p_nets=[N("+5V"), N("CANFD_H"), N("CANFD_L"), N("GND")],
    )

    # --- FRONT: power input + ToF + laser driver ---
    lines += comp_jst_gh_2p(
        "J_PWR", "JST-GH 2P +5V/GND", 11.0, 70.0, p1_net=N("+5V"), p2_net=N("GND")
    )
    lines += comp_0402(
        "J_CHASSIS_R", "0R chassis bond", 16.0, 70.0, p1_net=N("GND"), p2_net=N("PGND")
    )
    lines += comp_0402(
        "C_ISO", "100nF/500V", 22.0, 70.0, p1_net=N("GND"), p2_net=N("PGND")
    )

    lines += comp_jst_gh_4p(
        "J_TOF",
        "TFmini-S 5V/GND/TX/RX",
        32.0,
        70.0,
        p_nets=[N("+5V"), N("GND"), N("UART_TOF_TX"), N("UART_TOF_RX")],
    )

    lines += comp_sot23(
        "Q1",
        "AO3400",
        52.0,
        70.0,
        g_net=N("LASER_GATE"),
        d_net=N("LASER_CATHODE"),
        s_net=N("GND"),
    )
    lines += comp_0402(
        "R1", "100R", 45.0, 70.0, p1_net=N("LASER_EN"), p2_net=N("LASER_GATE")
    )
    lines += comp_0402("R2", "10k", 45.0, 74.0, p1_net=N("LASER_GATE"), p2_net=N("GND"))
    lines += comp_jst_sh_2p(
        "J_LASER",
        "laser +5V/cathode",
        62.0,
        70.0,
        p1_net=N("+5V"),
        p2_net=N("LASER_CATHODE"),
    )

    # ------------------------------------------------------------------
    # Copper zones — In1.Cu GND plane
    # ------------------------------------------------------------------
    lines += [
        f'\t(zone (net {N("GND")[0]}) (net_name "GND") (layer "In1.Cu") (uuid "{_uid()}")',
        "\t\t(hatch edge 0.5)",
        "\t\t(connect_pads (clearance 0.5))",
        "\t\t(min_thickness 0.2)",
        "\t\t(fill yes)",
        "\t\t(polygon",
        f"\t\t\t(pts (xy 2 2) (xy {W-2:.2f} 2) (xy {W-2:.2f} {H-2:.2f}) (xy 2 {H-2:.2f}))",
        "\t\t)",
        "\t)",
    ]

    lines.append(")")
    return "\n".join(lines)


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    content = gen_pcb()
    path = here / "Vera.kicad_pcb"
    path.write_text(content, encoding="utf-8")
    print(f"  Written: {path}  ({len(content):,} bytes)")
    print("Done.")
