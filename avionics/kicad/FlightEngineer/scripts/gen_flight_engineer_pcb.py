#!/usr/bin/env python3
"""gen_flight_engineer_pcb.py — Generate complete FlightEngineer.kicad_pcb with all component placements.

Flight Engineer is the EMI-hardened [REF-NIST-002 §6.2.5] Power Distribution Board for the Serenity UAV.
90 × 65 mm, 4-layer FR4-TG170, 4 oz Cu on F.Cu/In2.Cu, 1 oz on In1.Cu/B.Cu.

Schematic sections (from gen_flight_engineer.py / FlightEngineer.kicad_sch):
    A — Battery input: J_BATT, CM1, CM2, F1, C1/C2, C_DM1, C3, D1, C_Y1/Y2
    B — Battery disconnect FET + main current shunt: Q_BATT_DSG, R_DSG_G,
        R_CHGND, J_CHASSIS, RS_MAIN, U_IS_MAIN
    C — Four ESC output branches (ESC1..ESC4 active; ESC5 DNP):
        F_ESCn, C_DECn, CM_ESCn, RS_n, U_ISn, J_ESCn, J_SHLD_ESCn
    D — Dual redundant 5 V BEC: FB_5V1/2, C_BEC1/2_IN, L1/L2,
        U_BEC_5V_1/2, D_OR1/2, C_BEC1/2_OUT, J_5V
    E — 6 V servo BEC: FB_6V, C_BEC_SV_IN, L3, U_BEC_6V, C_BEC_SV_OUT, J_6V
    F — BQ76930 6S cell monitor: J_BAL, R_BAL1-6, U_CELL, C_CAP, J_NTC, C_NTC
    G — I2C/alert signal interface: D_I2C, R_ALERT, J_I2C, J_ALERT

Footprint strategy:
    Standard KiCad library footprints are referenced by "Lib:Name" with all pad
    geometry embedded inline (the library reference is only used by KiCad's
    "Update from Library" UI feature; the PCB file is fully self-contained).
    Custom inline footprints (no library) are used for non-standard parts:
      - Wurth 7440640500 WE-SL5 CMC (4-pin THT, 5.08 mm square pitch)
      - MAXI blade fuse holder (2-pin THT, 9.9 mm pitch)
      - CSS2H-2512K 4-terminal Kelvin shunt (SMD, custom land pattern)

Layout notes:
    All coordinates are (X, Y) in mm, origin = board top-left corner.
    Some large THT components (XT30 bodies, CMC chokes) will produce
    courtyard-overlap DRC warnings — these are documented in TODO.md and
    require manual refinement in KiCad after this initial placement.

Usage:
    python3 gen_flight_engineer_pcb.py

Output:
    avionics/kicad/FlightEngineer.kicad_pcb

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
         Griffing Technology LLC
License: CC BY 4.0  |  creativecommons.org/licenses/by/4.0
Date:    2026-06-10
Project: Serenity UAV — EDF Tilt-Rotor UAV

References:
    - KiCad PCB format version 20241229
    - IPC-7351 land pattern standard
    - Wurth Elektronik 7440640500 WE-SL5 CMC datasheet
    - Bourns CSS2H-2512K shunt resistor datasheet
    - Littelfuse MAXI fuse holder 0154.007.DR datasheet
    - Texas Instruments INA226AIDGSR datasheet (SBOS547F, 2015)
    - Texas Instruments TPS54620RGYT datasheet (SLVSA60F, 2022)
    - Texas Instruments TPS54540DDAR datasheet (SLVSAL2G, 2020)
    - Texas Instruments BQ76930PWRQ1 datasheet (SLUSBY5C, 2015)
    - Alpha & Omega AON6556 datasheet (2021)
    - Onsemi MBRD1045CT datasheet (2020)
    - Nexperia PRTR5V0U2X datasheet (Rev. 5, 2021)
    - Littelfuse SMBJ33CA TVS datasheet (2020)
"""

import itertools
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# UUID management — all Flight Engineer PCB UUIDs use prefix "b0d5ea00-0000-0000-0000-"
# ---------------------------------------------------------------------------
_UID_PREFIX = "b0d5ea00-0000-0000-0000-"
_uid_seq = itertools.count(1)


def _uid() -> str:
    """Return next sequential UUID with Flight Engineer PCB prefix."""
    return f"{_UID_PREFIX}{next(_uid_seq):012d}"


# ---------------------------------------------------------------------------
# Net registry — ordered to match the stub in gen_flight_engineer.py gen_pcb()
# ---------------------------------------------------------------------------
_NETS: list[tuple[int, str]] = [
    (0, ""),
    (1, "VBAT"),
    (2, "PGND"),
    (3, "VDIS"),
    (4, "+5V"),
    (5, "+6V"),
    (6, "5V_AVIONICS"),
    (7, "6V_SERVO"),
    (8, "PDB_SDA"),
    (9, "PDB_SCL"),
    (10, "PDB_ALERT_N"),
    (11, "DSG_GATE"),
    (12, "BQ_DSG_OUT"),
    (13, "ESC1_RS_OUT"),
    (14, "ESC2_RS_OUT"),
    (15, "ESC3_RS_OUT"),
    (16, "ESC4_RS_OUT"),
    (17, "ESC5_RS_OUT"),
    (18, "CHASSIS"),
    # Additional internal nets for full PCB connectivity
    (19, "BEC1_PRE_OR"),
    (20, "BEC2_PRE_OR"),
    (21, "BEC1_SW"),
    (22, "BEC2_SW"),
    (23, "BEC6V_SW"),
    (24, "PDB_SDA_RAW"),
    (25, "PDB_SCL_RAW"),
    (26, "NTC_P"),
    (27, "BALCELL1"),
    (28, "BALCELL2"),
    (29, "BALCELL3"),
    (30, "BALCELL4"),
    (31, "BALCELL5"),
    (32, "BALCELL6"),
    (33, "BQ_ALERT_N"),
    (34, "ESC1_FUSED"),
    (35, "ESC2_FUSED"),
    (36, "ESC3_FUSED"),
    (37, "ESC4_FUSED"),
    (38, "MAIN_SNS_P"),
    (39, "MAIN_SNS_N"),
    (40, "ESC1_SNS_P"),
    (41, "ESC1_SNS_N"),
    (42, "ESC2_SNS_P"),
    (43, "ESC2_SNS_N"),
    (44, "ESC3_SNS_P"),
    (45, "ESC3_SNS_N"),
    (46, "ESC4_SNS_P"),
    (47, "ESC4_SNS_N"),
    (48, "BEC1_VIN_F"),
    (49, "BEC2_VIN_F"),
    (50, "BEC6V_VIN_F"),
]

_NET_BY_NAME: dict[str, int] = {name: idx for idx, name in _NETS}


def N(net_name: str) -> tuple[int, str]:
    """Return (net_id, net_name) tuple for the given net name."""
    return (_NET_BY_NAME[net_name], net_name)


NO_NET = (0, "")


# ---------------------------------------------------------------------------
# Low-level S-expression helpers
# ---------------------------------------------------------------------------


def _fp(
    lib_ref: str, ref: str, value: str, x: float, y: float, angle: float = 0.0
) -> list[str]:
    """Start a footprint block and return the opening lines."""
    ang_s = f" {angle}" if angle else ""
    return [
        f'\t(footprint "{lib_ref}" (layer "F.Cu")',
        f"\t\t(at {x:.4f} {y:.4f}{ang_s})",
        f'\t\t(property "Reference" "{ref}" (at 0 -3.5 0) (layer "F.SilkS")',
        f"\t\t\t(effects (font (size 1.0 1.0) (thickness 0.15))))",
        f'\t\t(property "Value" "{value}" (at 0 3.5 0) (layer "F.Fab")',
        f"\t\t\t(effects (font (size 1.0 1.0) (thickness 0.15))))",
        f'\t\t(property "Footprint" "{lib_ref}" (at 0 0 0) (layer "F.Fab")',
        f"\t\t\t(effects (font (size 1.0 1.0) (thickness 0.15)) (hide yes)))",
        f"\t\t(attr smd)",
    ]


def _fp_tht(
    lib_ref: str, ref: str, value: str, x: float, y: float, angle: float = 0.0
) -> list[str]:
    """Start a through-hole footprint block."""
    ang_s = f" {angle}" if angle else ""
    return [
        f'\t(footprint "{lib_ref}" (layer "F.Cu")',
        f"\t\t(at {x:.4f} {y:.4f}{ang_s})",
        f'\t\t(property "Reference" "{ref}" (at 0 -3.5 0) (layer "F.SilkS")',
        f"\t\t\t(effects (font (size 1.0 1.0) (thickness 0.15))))",
        f'\t\t(property "Value" "{value}" (at 0 3.5 0) (layer "F.Fab")',
        f"\t\t\t(effects (font (size 1.0 1.0) (thickness 0.15))))",
        f'\t\t(property "Footprint" "{lib_ref}" (at 0 0 0) (layer "F.Fab")',
        f"\t\t\t(effects (font (size 1.0 1.0) (thickness 0.15)) (hide yes)))",
    ]


def _fp_end() -> list[str]:
    """Close a footprint block."""
    return [f'\t\t(uuid "{_uid()}")', "\t)"]


def _pad_smd(
    num: str,
    px: float,
    py: float,
    w: float,
    h: float,
    net: tuple[int, str],
    layers: str = '"F.Cu" "F.Mask" "F.Paste"',
) -> str:
    """Single SMD pad S-expression line."""
    ni, nn = net
    net_s = f' (net {ni} "{nn}")' if ni else ""
    return (
        f'\t\t(pad "{num}" smd roundrect'
        f" (at {px:.4f} {py:.4f})"
        f" (size {w:.4f} {h:.4f})"
        f" (layers {layers})"
        f" (roundrect_rratio 0.25)"
        f"{net_s}"
        f' (uuid "{_uid()}"))'
    )


def _pad_tht(
    num: str,
    px: float,
    py: float,
    w: float,
    h: float,
    drill: float,
    net: tuple[int, str],
    shape: str = "circle",
) -> str:
    """Single THT pad S-expression line."""
    ni, nn = net
    net_s = f' (net {ni} "{nn}")' if ni else ""
    drill_s = f"{drill:.4f}"
    if shape == "roundrect":
        shape_s = "roundrect"
        rr = " (roundrect_rratio 0.25)"
    elif shape == "oval":
        shape_s = "oval"
        rr = ""
    elif shape == "rect":
        shape_s = "rect"
        rr = ""
    else:
        shape_s = "circle"
        rr = ""
    return (
        f'\t\t(pad "{num}" thru_hole {shape_s}'
        f" (at {px:.4f} {py:.4f})"
        f" (size {w:.4f} {h:.4f})"
        f" (drill {drill_s})"
        f' (layers "*.Cu" "*.Mask")'
        f"{rr}"
        f"{net_s}"
        f' (uuid "{_uid()}"))'
    )


def _pad_npth(px: float, py: float, drill: float) -> str:
    """Non-plated through-hole (mounting, no net)."""
    d = drill
    return (
        f'\t\t(pad "" np_thru_hole circle'
        f" (at {px:.4f} {py:.4f})"
        f" (size {d:.4f} {d:.4f})"
        f" (drill {d:.4f})"
        f' (layers "*.Cu" "*.Mask")'
        f' (uuid "{_uid()}"))'
    )


def _crtyd(
    x1: float, y1: float, x2: float, y2: float, layer: str = "F.CrtYd"
) -> list[str]:
    """Courtyard rectangle."""
    return [
        f"\t\t(fp_rect (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f})"
        f' (layer "{layer}") (stroke (width 0.05) (type default))'
        f' (uuid "{_uid()}"))'
    ]


def _fab_rect(
    x1: float, y1: float, x2: float, y2: float, layer: str = "F.Fab"
) -> list[str]:
    return [
        f"\t\t(fp_rect (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f})"
        f' (layer "{layer}") (stroke (width 0.1) (type default))'
        f' (uuid "{_uid()}"))'
    ]


def _silk_circle(cx: float, cy: float, r: float, layer: str = "F.SilkS") -> list[str]:
    """Silkscreen circle (for body outline of radial components)."""
    return [
        f"\t\t(fp_circle (center {cx:.4f} {cy:.4f}) (end {cx+r:.4f} {cy:.4f})"
        f' (layer "{layer}") (stroke (width 0.15) (type default))'
        f' (uuid "{_uid()}"))'
    ]


# ---------------------------------------------------------------------------
# Component generators — each returns a list of PCB text lines
# ---------------------------------------------------------------------------


# --- Mounting hole (NPTH, M3) ---
def comp_mounting_hole(ref: str, x: float, y: float) -> list[str]:
    """M3 mounting hole, non-plated."""
    lines = _fp_tht("MountingHole:MountingHole_3.2mm_M3", ref, "M3", x, y)
    lines += _crtyd(-3.5, -3.5, 3.5, 3.5)
    lines += _fab_rect(-3.5, -3.5, 3.5, 3.5)
    lines.append(_pad_npth(0.0, 0.0, 3.2))
    lines += _fp_end()
    return lines


# --- M3 chassis lug pad (grounding/shield pads) ---
def comp_m3_lug(
    ref: str, x: float, y: float, net: tuple[int, str] = NO_NET
) -> list[str]:
    """M3 chassis lug — plated THT with CHASSIS net."""
    lines = _fp_tht("MountingHole:MountingHole_3.2mm_M3_Pad_Via", ref, "M3_Lug", x, y)
    lines += _crtyd(-3.5, -3.5, 3.5, 3.5)
    ni, nn = net
    lines.append(
        f'\t\t(pad "" thru_hole circle (at 0 0) (size 6.0 6.0)'
        f' (drill 3.2) (layers "*.Cu" "*.Mask")'
        f' (net {ni} "{nn}")'
        f' (uuid "{_uid()}"))'
    )
    lines += _fp_end()
    return lines


# --- Generic 0402 SMD (resistor or capacitor) ---
def comp_0402(
    ref: str,
    value: str,
    x: float,
    y: float,
    p1_net: tuple[int, str] = NO_NET,
    p2_net: tuple[int, str] = NO_NET,
    angle: float = 0.0,
) -> list[str]:
    """0402 (1005 metric) SMD component."""
    lib = "Resistor_SMD:R_0402_1005Metric"
    lines = _fp(lib, ref, value, x, y, angle)
    lines += _crtyd(-0.98, -0.73, 0.98, 0.73)
    lines += _fab_rect(-0.5, -0.25, 0.5, 0.25)
    lines.append(_pad_smd("1", -0.51, 0.0, 0.54, 0.64, p1_net))
    lines.append(_pad_smd("2", 0.51, 0.0, 0.54, 0.64, p2_net))
    lines += _fp_end()
    return lines


# --- Generic 0805 SMD (ferrite bead or capacitor) ---
def comp_0805(
    ref: str,
    value: str,
    x: float,
    y: float,
    p1_net: tuple[int, str] = NO_NET,
    p2_net: tuple[int, str] = NO_NET,
    angle: float = 0.0,
) -> list[str]:
    """0805 (2012 metric) SMD component."""
    lib = "Capacitor_SMD:C_0805_2012Metric"
    lines = _fp(lib, ref, value, x, y, angle)
    lines += _crtyd(-1.88, -1.10, 1.88, 1.10)
    lines += _fab_rect(-1.0, -0.65, 1.0, 0.65)
    lines.append(_pad_smd("1", -0.95, 0.0, 1.0, 1.45, p1_net))
    lines.append(_pad_smd("2", 0.95, 0.0, 1.0, 1.45, p2_net))
    lines += _fp_end()
    return lines


# --- Generic 1210 SMD inductor ---
def comp_1210(
    ref: str,
    value: str,
    x: float,
    y: float,
    p1_net: tuple[int, str] = NO_NET,
    p2_net: tuple[int, str] = NO_NET,
    angle: float = 0.0,
) -> list[str]:
    """1210 (3225 metric) SMD inductor/cap."""
    lib = "Inductor_SMD:L_1210_3225Metric"
    lines = _fp(lib, ref, value, x, y, angle)
    lines += _crtyd(-2.23, -1.88, 2.23, 1.88)
    lines += _fab_rect(-1.6, -1.6, 1.6, 1.6)
    lines.append(_pad_smd("1", -1.4, 0.0, 1.25, 2.65, p1_net))
    lines.append(_pad_smd("2", 1.4, 0.0, 1.25, 2.65, p2_net))
    lines += _fp_end()
    return lines


# --- SMB diode (SMBJ33CA TVS) ---
def comp_smb_diode(
    ref: str,
    value: str,
    x: float,
    y: float,
    anode_net: tuple[int, str] = NO_NET,
    cathode_net: tuple[int, str] = NO_NET,
) -> list[str]:
    """D_SMB SMD diode (e.g. SMBJ33CA)."""
    lib = "Diode_SMD:D_SMB"
    lines = _fp(lib, ref, value, x, y)
    lines += _crtyd(-3.58, -1.95, 3.58, 1.95)
    lines += _fab_rect(-2.8, -1.3, 2.8, 1.3)
    lines.append(_pad_smd("1", -2.15, 0.0, 2.5, 2.3, anode_net))
    lines.append(_pad_smd("2", 2.15, 0.0, 2.5, 2.3, cathode_net))
    lines += _fp_end()
    return lines


# --- SOT-363 / SC-70-6 (PRTR5V0U2X) ---
def comp_sot363(
    ref: str,
    value: str,
    x: float,
    y: float,
    nets: dict[str, tuple[int, str]] | None = None,
) -> list[str]:
    """SOT-363 (SC-70-6) 6-pin SMD package.

    Pins layout (top view, KiCad):
        1 at (-0.95, -0.65)   4 at (+0.95, +0.65)
        2 at (-0.95,  0.00)   5 at (+0.95,  0.00)
        3 at (-0.95, +0.65)   6 at (+0.95, -0.65)
    """
    if nets is None:
        nets = {}
    lib = "Package_TO_SOT_SMD:SOT-363_SC-70-6"
    lines = _fp(lib, ref, value, x, y)
    lines += _crtyd(-1.7, -1.25, 1.7, 1.25)
    lines += _fab_rect(-0.65, -0.9, 0.65, 0.9)
    pads = [
        ("1", -0.95, -0.65),
        ("2", -0.95, 0.00),
        ("3", -0.95, 0.65),
        ("4", 0.95, 0.65),
        ("5", 0.95, 0.00),
        ("6", 0.95, -0.65),
    ]
    for num, px, py in pads:
        lines.append(_pad_smd(num, px, py, 0.65, 0.40, nets.get(num, NO_NET)))
    lines += _fp_end()
    return lines


# --- MSOP-10 (INA226AIDGSR) ---
def comp_msop10(
    ref: str,
    value: str,
    x: float,
    y: float,
    nets: dict[str, tuple[int, str]] | None = None,
) -> list[str]:
    """MSOP-10 3×3 mm SMD package (INA226).

    Pins:
        1-5 on left  (x=-2.1125, y= -1.0…+1.0 in 0.5 steps)
        6-10 on right (x=+2.1125, y= +1.0…-1.0 in 0.5 steps)
    """
    if nets is None:
        nets = {}
    lib = "Package_SO:MSOP-10_3x3mm_P0.5mm"
    lines = _fp(lib, ref, value, x, y)
    lines += _crtyd(-2.95, -1.88, 2.95, 1.88)
    lines += _fab_rect(-1.5, -1.5, 1.5, 1.5)
    px_l, px_r = -2.1125, 2.1125
    pads_l = [("1", -1.0), ("2", -0.5), ("3", 0.0), ("4", 0.5), ("5", 1.0)]
    pads_r = [("6", 1.0), ("7", 0.5), ("8", 0.0), ("9", -0.5), ("10", -1.0)]
    for num, py in pads_l:
        lines.append(_pad_smd(num, px_l, py, 1.625, 0.35, nets.get(num, NO_NET)))
    for num, py in pads_r:
        lines.append(_pad_smd(num, px_r, py, 1.625, 0.35, nets.get(num, NO_NET)))
    lines += _fp_end()
    return lines


# --- SOIC-8 (AON6556, TPS54540) ---
def comp_soic8(
    ref: str,
    value: str,
    x: float,
    y: float,
    nets: dict[str, tuple[int, str]] | None = None,
    angle: float = 0.0,
) -> list[str]:
    """SOIC-8 3.9×4.9 mm SMD package.

    Pins:
        1-4 left  (x=-2.475, y=-1.905…+1.905)
        5-8 right (x=+2.475, y=+1.905…-1.905)
    """
    if nets is None:
        nets = {}
    lib = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
    lines = _fp(lib, ref, value, x, y, angle)
    lines += _crtyd(-3.38, -3.13, 3.38, 3.13)
    lines += _fab_rect(-1.95, -2.45, 1.95, 2.45)
    px_l, px_r = -2.475, 2.475
    pads_l = [("1", -1.905), ("2", -0.635), ("3", 0.635), ("4", 1.905)]
    pads_r = [("5", 1.905), ("6", 0.635), ("7", -0.635), ("8", -1.905)]
    for num, py in pads_l:
        lines.append(_pad_smd(num, px_l, py, 1.95, 0.60, nets.get(num, NO_NET)))
    for num, py in pads_r:
        lines.append(_pad_smd(num, px_r, py, 1.95, 0.60, nets.get(num, NO_NET)))
    lines += _fp_end()
    return lines


# --- TSSOP-30 (BQ76930PWRQ1) ---
def comp_tssop30(
    ref: str,
    value: str,
    x: float,
    y: float,
    nets: dict[str, tuple[int, str]] | None = None,
) -> list[str]:
    """TSSOP-30 6.1×9.7 mm SMD package (BQ76930).

    Pins 1-15 on left (x=-3.7125, y=-4.55…+4.55 step +0.65)
    Pins 16-30 on right (x=+3.7125, y=+4.55…-4.55 step -0.65)
    """
    if nets is None:
        nets = {}
    lib = "Package_SO:TSSOP-30_6.1x9.7mm_P0.65mm"
    lines = _fp(lib, ref, value, x, y)
    lines += _crtyd(-4.70, -6.23, 4.70, 6.23)
    lines += _fab_rect(-3.05, -4.85, 3.05, 4.85)
    px_l, px_r = -3.7125, 3.7125
    ys_l = [-4.55 + i * 0.65 for i in range(15)]
    ys_r = [4.55 - i * 0.65 for i in range(15)]
    for i, py in enumerate(ys_l):
        num = str(i + 1)
        lines.append(_pad_smd(num, px_l, py, 1.475, 0.40, nets.get(num, NO_NET)))
    for i, py in enumerate(ys_r):
        num = str(i + 16)
        lines.append(_pad_smd(num, px_r, py, 1.475, 0.40, nets.get(num, NO_NET)))
    lines += _fp_end()
    return lines


# --- VQFN-20 with EP (TPS54620RGYT) ---
def comp_vqfn20(
    ref: str,
    value: str,
    x: float,
    y: float,
    nets: dict[str, tuple[int, str]] | None = None,
) -> list[str]:
    """Texas Instruments VQFN-20 4×4 mm QFN package (TPS54620).

    Pad layout (5 pads per side + EP21):
        Pins 1-5:  left side  (x=-1.9625, y=-1.0…+1.0 step 0.5)
        Pins 6-10: bottom     (y=+1.9625, x=+1.0…-1.0 step -0.5)
        Pins 11-15: right     (x=+1.9625, y=+1.0…-1.0 step -0.5)
        Pins 16-20: top       (y=-1.9625, x=-1.0…+1.0 step 0.5)
        Pin  21:   EP center  (0,0) 2.7×2.7 mm
    """
    if nets is None:
        nets = {}
    lib = "Package_DFN_QFN:Texas_RGP0020D_VQFN-20-1EP_4x4mm_P0.5mm_EP2.7x2.7mm"
    lines = _fp(lib, ref, value, x, y)
    lines += _crtyd(-2.6, -2.6, 2.6, 2.6)
    lines += _fab_rect(-2.0, -2.0, 2.0, 2.0)
    # Pins 1-5 left side
    for i in range(5):
        num = str(i + 1)
        py = -1.0 + i * 0.5
        lines.append(_pad_smd(num, -1.9625, py, 0.825, 0.25, nets.get(num, NO_NET)))
    # Pins 6-10 bottom
    for i in range(5):
        num = str(i + 6)
        px = 1.0 - i * 0.5
        lines.append(_pad_smd(num, px, 1.9625, 0.25, 0.825, nets.get(num, NO_NET)))
    # Pins 11-15 right side
    for i in range(5):
        num = str(i + 11)
        py = 1.0 - i * 0.5
        lines.append(_pad_smd(num, 1.9625, py, 0.825, 0.25, nets.get(num, NO_NET)))
    # Pins 16-20 top
    for i in range(5):
        num = str(i + 16)
        px = -1.0 + i * 0.5
        lines.append(_pad_smd(num, px, -1.9625, 0.25, 0.825, nets.get(num, NO_NET)))
    # EP pin 21 — thermal pad
    ni, nn = nets.get("21", N("PGND"))
    lines.append(
        f'\t\t(pad "21" smd roundrect (at 0 0) (size 2.7 2.7)'
        f' (layers "F.Cu" "F.Mask")'
        f" (roundrect_rratio 0.111111)"
        f' (net {ni} "{nn}")'
        f' (uuid "{_uid()}"))'
    )
    lines += _fp_end()
    return lines


# --- TO-252-3 TabPin2 DPAK (MBRD1045CT) ---
def comp_dpak(
    ref: str,
    value: str,
    x: float,
    y: float,
    p1_net: tuple[int, str] = NO_NET,
    p2_net: tuple[int, str] = NO_NET,
    p3_net: tuple[int, str] = NO_NET,
) -> list[str]:
    """TO-252-3 DPAK (TabPin2 = cathode for MBRD1045CT dual Schottky).

    Pin 1 (anode 1)  : (-5.04, -2.28) 2.2×1.2 mm
    Pin 2 (cathode/tab): (-5.04, 0.00) 2.2×1.2 mm + (1.26, 0) 6.4×5.8 mm tab
    Pin 3 (anode 2)  : (-5.04, +2.28) 2.2×1.2 mm
    """
    lib = "Package_TO_SOT_SMD:TO-252-3_TabPin2"
    lines = _fp(lib, ref, value, x, y)
    lines += _crtyd(-6.75, -3.83, 5.50, 3.83)
    lines += _fab_rect(-4.0, -3.0, 4.5, 3.0)
    # Gate/signal pins (small)
    lines.append(_pad_smd("1", -5.04, -2.28, 2.2, 1.2, p1_net))
    lines.append(_pad_smd("2", -5.04, 0.00, 2.2, 1.2, p2_net))
    lines.append(_pad_smd("3", -5.04, 2.28, 2.2, 1.2, p3_net))
    # Tab (large exposed pad — same net as pin 2)
    ni, nn = p2_net
    lines.append(
        f'\t\t(pad "2" smd roundrect (at 1.26 0) (size 6.4 5.8)'
        f' (layers "F.Cu" "F.Mask")'
        f" (roundrect_rratio 0.043103)"
        f' (net {ni} "{nn}")'
        f' (uuid "{_uid()}"))'
    )
    lines += _fp_end()
    return lines


# --- XT60PW-F horizontal PCB-mount (J_BATT battery input) ---
def comp_xt60pw_f(
    ref: str,
    value: str,
    x: float,
    y: float,
    p_net: tuple[int, str] = NO_NET,
    n_net: tuple[int, str] = NO_NET,
) -> list[str]:
    """AMASS XT60PW-F 1×02 P7.20mm horizontal PCB-mount connector.

    Pad 1 (+) at (0, 0), Pad 2 (−) at (7.2, 0).
    Body extends in −Y direction; courtyard top at y = −16.5.
    Mount pins at (−10.35, −6) and (3.15, −6).
    """
    lib = "Connector_AMASS:AMASS_XT60PW-F_1x02_P7.20mm_Horizontal"
    lines = _fp_tht(lib, ref, value, x, y)
    lines += _crtyd(-11.6, -17.5, 5.8, 5.0)
    lines += _fab_rect(-11.0, -16.5, 5.2, 4.5)
    # Mounting pin (no net)
    lines.append(_pad_npth(-10.35, -6.0, 1.5))
    lines.append(_pad_npth(3.15, -6.0, 1.5))
    # Signal pads
    lines.append(_pad_tht("1", 0.0, 0.0, 4.0, 4.0, 2.5, p_net, "roundrect"))
    lines.append(_pad_tht("2", 7.2, 0.0, 4.0, 4.0, 2.5, n_net))
    lines += _fp_end()
    return lines


# --- XT30PW-F horizontal PCB-mount (J_ESCn ESC outputs) ---
def comp_xt30pw_f(
    ref: str,
    value: str,
    x: float,
    y: float,
    p_net: tuple[int, str] = NO_NET,
    n_net: tuple[int, str] = NO_NET,
) -> list[str]:
    """AMASS XT30PW-F 1×02 P2.50mm horizontal PCB-mount connector.

    Pad 1 (+) at (0, 0), Pad 2 (−) at (5.0, 0).
    Body extends in −Y direction; courtyard top at y = −15.5.
    Mount pins at (−3, −5) and (8, −5).
    """
    lib = "Connector_AMASS:AMASS_XT30PW-F_1x02_P2.50mm_Horizontal"
    lines = _fp_tht(lib, ref, value, x, y)
    lines += _crtyd(-4.5, -16.5, 9.5, 4.5)
    lines += _fab_rect(-4.0, -15.5, 9.0, 4.0)
    lines.append(_pad_npth(-3.0, -5.0, 1.2))
    lines.append(_pad_npth(8.0, -5.0, 1.2))
    lines.append(_pad_tht("1", 0.0, 0.0, 3.5, 3.5, 2.0, p_net, "roundrect"))
    lines.append(_pad_tht("2", 5.0, 0.0, 3.5, 3.5, 2.0, n_net))
    lines += _fp_end()
    return lines


# --- D10 radial electrolytic capacitor ---
def comp_cp_d10(
    ref: str,
    value: str,
    x: float,
    y: float,
    p_net: tuple[int, str] = NO_NET,
    n_net: tuple[int, str] = NO_NET,
) -> list[str]:
    """CP_Radial_D10.0mm_P5.00mm electrolytic capacitor.

    Pad 1 (+) at (0, 0), Pad 2 (−) at (5, 0).
    Body centre at (2.5, 0), radius 5 mm.
    """
    lib = "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm"
    lines = _fp_tht(lib, ref, value, x, y)
    # Courtyard: body extends ±6 mm from pad-midpoint (2.5,0), +1 mm margin
    lines += _crtyd(-4.5, -6.5, 9.5, 6.5)
    lines += _silk_circle(2.5, 0.0, 5.5)  # silkscreen body circle
    lines += _fab_rect(0.0, -5.5, 5.0, 5.5)
    lines.append(_pad_tht("1", 0.0, 0.0, 2.0, 2.0, 1.0, p_net, "roundrect"))
    lines.append(_pad_tht("2", 5.0, 0.0, 2.0, 2.0, 1.0, n_net))
    lines += _fp_end()
    return lines


# --- Y2 safety capacitor (THT) — treated as standard radial with P5mm ---
def comp_y2_cap(
    ref: str,
    value: str,
    x: float,
    y: float,
    p1_net: tuple[int, str] = NO_NET,
    p2_net: tuple[int, str] = NO_NET,
) -> list[str]:
    """Y2-class safety capacitor, THT radial, 5.08 mm pitch.

    Used for C_Y1, C_Y2 (battery-to-chassis filter caps).
    """
    lib = "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm"
    lines = _fp_tht(lib, ref, value, x, y)
    lines += _crtyd(-1.3, -2.7, 6.3, 2.7)
    lines += _fab_rect(0.0, -2.3, 5.0, 2.3)
    lines.append(_pad_tht("1", 0.0, 0.0, 1.8, 1.8, 1.0, p1_net, "roundrect"))
    lines.append(_pad_tht("2", 5.0, 0.0, 1.8, 1.8, 1.0, p2_net))
    lines += _fp_end()
    return lines


# --- Molex Nano-Fit 4P single-row vertical (J_5V, J_6V) ---
def comp_nanofit_4p(
    ref: str,
    value: str,
    x: float,
    y: float,
    p_nets: list[tuple[int, str]] | None = None,
) -> list[str]:
    """Molex Nano-Fit 105309-xx04 1×04 P2.50mm vertical THT connector.

    Pads at x=0, y=0, 2.5, 5.0, 7.5 (pin 1 at top).
    """
    if p_nets is None:
        p_nets = [NO_NET] * 4
    lib = "Connector_Molex:Molex_Nano-Fit_105309-xx04_1x04_P2.50mm_Vertical"
    lines = _fp_tht(lib, ref, value, x, y)
    lines += _crtyd(-2.75, -1.3, 2.75, 9.8)
    lines += _fab_rect(-1.65, 0.0, 1.65, 9.0)
    # Latch at x=-2.1 (was -1.34): hole right edge at -1.45 gives 0.427 mm
    # clearance to nearest signal-pad corner — satisfies 0.25 mm minimum.
    lines.append(_pad_npth(-2.1, 3.75, 1.3))  # mechanical latch
    pads_y = [0.0, 2.5, 5.0, 7.5]
    for i, py in enumerate(pads_y):
        shape = "roundrect" if i == 0 else "oval"
        net = p_nets[i] if i < len(p_nets) else NO_NET
        lines.append(_pad_tht(str(i + 1), 0.0, py, 2.2, 1.7, 1.2, net, shape))
    lines += _fp_end()
    return lines


# --- JST-GH 2P SMD vertical (J_NTC, J_ALERT) ---
def comp_jst_gh_2p(
    ref: str,
    value: str,
    x: float,
    y: float,
    p1_net: tuple[int, str] = NO_NET,
    p2_net: tuple[int, str] = NO_NET,
) -> list[str]:
    """JST GH BM02B-GHS-TBT 1×02 P1.25mm SMD vertical."""
    lib = "Connector_JST:JST_GH_BM02B-GHS-TBT_1x02-1MP_P1.25mm_Vertical"
    lines = _fp(lib, ref, value, x, y)
    lines += _crtyd(-3.2, -1.8, 3.2, 3.3)
    lines += _fab_rect(-0.95, 0.5, 0.95, 3.3)
    # Mechanical mount pads (no net)
    lines.append(_pad_smd("MP", -2.475, -1.4, 1.0, 2.8, NO_NET))
    lines.append(_pad_smd("MP", 2.475, -1.4, 1.0, 2.8, NO_NET))
    lines.append(_pad_smd("1", -0.625, 1.95, 0.60, 1.70, p1_net))
    lines.append(_pad_smd("2", 0.625, 1.95, 0.60, 1.70, p2_net))
    lines += _fp_end()
    return lines


# --- JST-GH 4P SMD vertical (J_I2C) ---
def comp_jst_gh_4p(
    ref: str,
    value: str,
    x: float,
    y: float,
    p_nets: list[tuple[int, str]] | None = None,
) -> list[str]:
    """JST GH BM04B-GHS-TBT 1×04 P1.25mm SMD vertical."""
    if p_nets is None:
        p_nets = [NO_NET] * 4
    lib = "Connector_JST:JST_GH_BM04B-GHS-TBT_1x04-1MP_P1.25mm_Vertical"
    lines = _fp(lib, ref, value, x, y)
    lines += _crtyd(-4.0, -1.8, 4.0, 3.3)
    lines += _fab_rect(-1.875, 0.5, 1.875, 3.3)
    # Mechanical mount pads
    ni, nn = NO_NET
    for mpx in [-3.1, 3.1]:
        lines.append(_pad_smd("MP", mpx, -1.4, 1.0, 2.8, NO_NET))
    pads_x = [-1.875, -0.625, 0.625, 1.875]
    for i, px in enumerate(pads_x):
        net = p_nets[i] if i < len(p_nets) else NO_NET
        lines.append(_pad_smd(str(i + 1), px, 1.95, 0.60, 1.70, net))
    lines += _fp_end()
    return lines


# --- JST-XH 7P THT vertical (J_BAL balance connector) ---
def comp_jst_xh_7p(
    ref: str,
    value: str,
    x: float,
    y: float,
    p_nets: list[tuple[int, str]] | None = None,
) -> list[str]:
    """JST XH B7B-XH-A 1×07 P2.50mm THT vertical connector."""
    if p_nets is None:
        p_nets = [NO_NET] * 7
    lib = "Connector_JST:JST_XH_B7B-XH-A_1x07_P2.50mm_Vertical"
    lines = _fp_tht(lib, ref, value, x, y)
    lines += _crtyd(-1.7, -1.7, 17.0, 6.5)
    lines += _fab_rect(0.0, 0.0, 15.0, 5.5)
    for i in range(7):
        px = i * 2.5
        shape = "roundrect" if i == 0 else "oval"
        net = p_nets[i] if i < len(p_nets) else NO_NET
        lines.append(_pad_tht(str(i + 1), px, 0.0, 1.7, 1.95, 0.95, net, shape))
    lines += _fp_end()
    return lines


# --- Custom: Wurth 7440640500 WE-SL5 CMC (4-pin THT, 5.08mm pitch sq) ---
def comp_wurth_cmc(
    ref: str,
    x: float,
    y: float,
    p1_net: tuple[int, str] = NO_NET,  # winding1 in
    p2_net: tuple[int, str] = NO_NET,  # winding1 out
    p3_net: tuple[int, str] = NO_NET,  # winding2 in
    p4_net: tuple[int, str] = NO_NET,
) -> list[str]:  # winding2 out
    """Wurth 7440640500 WE-SL5 CMC — custom inline footprint.

    4-pin THT in 2×2 square grid, 5.08 mm pitch.
    Body: 11.3 mm diameter circle centred at (2.54, 2.54).

    Pin assignments (top view):
        1 (2.54,−2.54)  winding1 in
        2 (2.54,+2.54)  winding1 out
        3 (−2.54,−2.54) winding2 in
        4 (−2.54,+2.54) winding2 out
    Reference:
        Wurth Elektronik 7440640500 datasheet, Fig. 4 land pattern, 2023.
        Pitch 5.08 mm (0.2 in) per IPC-2221B through-hole land pattern.
    """
    lines = _fp_tht("Flight Engineer:CMC_WE-SL5_7440640500", ref, "WE-SL5_7440640500", x, y)
    lines += _crtyd(-5.54, -5.54, 5.54, 5.54)
    # Fab-layer body circle (11.3 mm dia, centred at origin)
    lines += _silk_circle(0.0, 0.0, 5.65)
    lines += _fab_rect(-2.54, -2.54, 2.54, 2.54)
    # Pins: layout centres on (0,0), pins at ±2.54 from centre
    lines.append(_pad_tht("1", 2.54, -2.54, 1.9, 1.9, 1.2, p1_net, "roundrect"))
    lines.append(_pad_tht("2", 2.54, 2.54, 1.9, 1.9, 1.2, p2_net))
    lines.append(_pad_tht("3", -2.54, -2.54, 1.9, 1.9, 1.2, p3_net))
    lines.append(_pad_tht("4", -2.54, 2.54, 1.9, 1.9, 1.2, p4_net))
    lines += _fp_end()
    return lines


# --- Custom: MAXI blade fuse holder (Littelfuse 0154.007.DR) ---
def comp_maxi_fuse(
    ref: str,
    x: float,
    y: float,
    p1_net: tuple[int, str] = NO_NET,
    p2_net: tuple[int, str] = NO_NET,
) -> list[str]:
    """MAXI blade fuse holder — custom inline footprint.

    2-pin THT, 9.9 mm pitch.  Body ~22 × 14 mm.
    Reference:
        Littelfuse 0154.007.DR PCB-mount MAXI holder datasheet, 2022.
    """
    lines = _fp_tht("Flight Engineer:FuseHolder_MAXI_PCB", ref, "FuseHolder_MAXI_150A", x, y)
    lines += _crtyd(-2.2, -7.5, 12.1, 7.5)
    lines += _fab_rect(-1.5, -7.0, 11.4, 7.0)
    lines.append(_pad_tht("1", 0.0, 0.0, 3.0, 3.0, 1.8, p1_net, "roundrect"))
    lines.append(_pad_tht("2", 9.9, 0.0, 3.0, 3.0, 1.8, p2_net))
    lines += _fp_end()
    return lines


# --- Mini blade fuse holder (Keystone 3568 / Littelfuse 0154.004.DR) ---
def comp_mini_fuse(
    ref: str,
    x: float,
    y: float,
    p1_net: tuple[int, str] = NO_NET,
    p2_net: tuple[int, str] = NO_NET,
) -> list[str]:
    """Mini blade fuse holder Keystone 3568 THT.

    Two parallel rows of 2 pads each (4 THT pads total), pitch 9.92 mm H.
    Pads at (0,0), (0,3.4), (9.92,0), (9.92,3.4).
    """
    lib = "Fuse:Fuseholder_Blade_Mini_Keystone_3568"
    lines = _fp_tht(lib, ref, "FuseHolder_Mini_40A", x, y)
    lines += _crtyd(-1.7, -1.7, 11.6, 5.1)
    lines += _fab_rect(0.0, 0.0, 9.92, 3.4)
    lines.append(_pad_tht("1", 0.00, 0.0, 2.78, 2.78, 1.78, p1_net, "roundrect"))
    lines.append(_pad_tht("1", 0.00, 3.4, 2.78, 2.78, 1.78, p1_net))
    lines.append(_pad_tht("2", 9.92, 0.0, 2.78, 2.78, 1.78, p2_net))
    lines.append(_pad_tht("2", 9.92, 3.4, 2.78, 2.78, 1.78, p2_net))
    lines += _fp_end()
    return lines


# --- Custom: CSS2H-2512K 4-terminal Kelvin shunt resistor ---
def comp_kelvin_shunt(
    ref: str,
    x: float,
    y: float,
    c_in_net: tuple[int, str] = NO_NET,  # current in
    s_p_net: tuple[int, str] = NO_NET,  # sense +
    s_n_net: tuple[int, str] = NO_NET,  # sense −
    c_out_net: tuple[int, str] = NO_NET,
) -> list[str]:  # current out
    """Bourns CSS2H-2512K 4-terminal Kelvin shunt (SMD, 2512 body).

    Land pattern (IPC-2221B modified for Kelvin configuration):
        Pad 1 (I_IN  current, wide):  centre (−2.54,  0) 2.0 × 2.5 mm
        Pad 2 (V_PLS sense):          centre (−0.64,  0) 0.8 × 2.0 mm
        Pad 3 (V_MNS sense):          centre (+0.64,  0) 0.8 × 2.0 mm
        Pad 4 (I_OUT current, wide):  centre (+2.54,  0) 2.0 × 2.5 mm

    Pad-to-pad gaps: current↔sense = 0.50 mm (meets IPC-2221B ≤31 V external);
    sense↔sense = 0.48 mm.

    Reference:
        Bourns CSS2H-2512K datasheet, Figure 9 PCB land pattern, 2021.
    """
    lines = _fp("Flight Engineer:R_Shunt_CSS2H_2512K", ref, "1mOhm_Kelvin_2512", x, y)
    lines += _crtyd(-4.28, -2.50, 4.28, 2.50)
    lines += _fab_rect(-3.175, -1.60, 3.175, 1.60)
    # Pad centres chosen so current-pad-edge to sense-pad-edge gap = 0.50 mm,
    # meeting IPC-2221B minimum for conductors at ≤ 31 V on external layers.
    # I_IN  right edge  = -2.54 + 1.00 = -1.54 mm
    # V_PLS left  edge  = -0.64 - 0.40 = -1.04 mm  → gap 0.50 mm ✓
    lines.append(_pad_smd("1", -2.54, 0.0, 2.0, 2.5, c_in_net))
    lines.append(_pad_smd("2", -0.64, 0.0, 0.8, 2.0, s_p_net))
    lines.append(_pad_smd("3", 0.64, 0.0, 0.8, 2.0, s_n_net))
    lines.append(_pad_smd("4", 2.54, 0.0, 2.0, 2.5, c_out_net))
    lines += _fp_end()
    return lines


# ---------------------------------------------------------------------------
# Copper zone generators (GND plane In1.Cu, VBAT plane In2.Cu)
# ---------------------------------------------------------------------------


def _zone(
    net: tuple[int, str],
    layer: str,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    clearance: float = 0.5,
) -> list[str]:
    """Rectangular copper pour zone."""
    ni, nn = net
    return [
        f'\t(zone (net {ni}) (net_name "{nn}") (layer "{layer}")',
        f'\t\t(tstamp "{_uid()}")',
        f"\t\t(hatch edge 0.508)",
        f"\t\t(connect_pads (clearance {clearance:.3f}))",
        f"\t\t(min_thickness 0.254)",
        f"\t\t(fill yes (thermal_gap 0.5) (thermal_bridge_width 0.5))",
        f"\t\t(polygon",
        f"\t\t\t(pts",
        f"\t\t\t\t(xy {x1:.4f} {y1:.4f})",
        f"\t\t\t\t(xy {x2:.4f} {y1:.4f})",
        f"\t\t\t\t(xy {x2:.4f} {y2:.4f})",
        f"\t\t\t\t(xy {x1:.4f} {y2:.4f})",
        f"\t\t\t)",
        f"\t\t)",
        f"\t)",
    ]


# ---------------------------------------------------------------------------
# PCB generation — board header, stackup, all components, copper zones
# ---------------------------------------------------------------------------


def gen_pcb() -> str:
    """Generate the complete FlightEngineer.kicad_pcb content."""
    W, H = 90.0, 65.0
    MH_M = 4.0

    lines: list[str] = []

    # --- File header ---
    lines += [
        "(kicad_pcb",
        "\t(version 20241229)",
        '\t(generator "pcbnew")',
        '\t(generator_version "9.0")',
        "\t(general",
        "\t\t(thickness 1.6)",
        "\t\t(legacy_teardrops no)",
        "\t)",
        '\t(paper "A4")',
        "\t(title_block",
        '\t\t(title "Flight Engineer")',
        '\t\t(date "2026-06-10")',
        '\t\t(rev "A")',
        '\t\t(comment 1 "Serenity-Class Tiltrotor UAV — Power Distribution Board")',
        '\t\t(comment 2 "CC BY 4.0 creativecommons.org/licenses/by/4.0")',
        '\t\t(comment 3 "90x65mm 4-layer FR4-TG170  4oz Cu F.Cu/In2.Cu  1oz In1.Cu/B.Cu")',
        '\t\t(comment 4 "JLCPCB / PCBWay: 4-oz inner planes; ENIG; no V-score")',
        "\t)",
    ]

    # --- Layer definitions ---
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

    # --- Board setup ---
    lines += [
        "\t(setup",
        "\t\t(pad_to_mask_clearance 0)",
        "\t\t(allow_soldermask_bridges_in_footprints no)",
        "\t\t(tenting front back)",
        "\t)",
    ]

    # --- Net declarations ---
    for idx, name in _NETS:
        lines.append(f'\t(net {idx} "{name}")')

    # --- Board outline ---
    lines += [
        f"\t(gr_rect (start 0 0) (end {W} {H})",
        f'\t\t(stroke (width 0.05) (type default)) (layer "Edge.Cuts")',
        f'\t\t(uuid "{_uid()}"))',
        # Board ID text on F.Fab
        f'\t(gr_text "Flight Engineer Rev R" (at {W/2:.2f} {H + 3.0:.2f} 0) (layer "F.Fab")',
        f"\t\t(effects (font (size 1.5 1.5) (thickness 0.15)))",
        f'\t\t(uuid "{_uid()}"))',
        f'\t(gr_text "Griffing Technology LLC | CC BY 4.0"'
        f' (at {W/2:.2f} {H + 5.5:.2f} 0) (layer "F.Fab")',
        f"\t\t(effects (font (size 1.0 1.0) (thickness 0.1)))",
        f'\t\t(uuid "{_uid()}"))',
    ]

    # ==========================================================
    # MOUNTING HOLES H1-H4
    # ==========================================================
    for i, (mx, my) in enumerate(
        [
            (MH_M, MH_M),
            (W - MH_M, MH_M),
            (MH_M, H - MH_M),
            (W - MH_M, H - MH_M),
        ]
    ):
        lines += comp_mounting_hole(f"H{i+1}", mx, my)

    # ==========================================================
    # SECTION A: Battery input filter
    #   J_BATT  → CM1 → CM2 → F1 → VDIS bus
    #   Bypass: C1, C2 (220µF bulk), C_DM1 (10µF DM), C3 (100nF HF)
    #   TVS:    D1 (SMBJ33CA)
    #   Safety: C_Y1, C_Y2 (Y2 class)
    # ==========================================================

    # J_BATT — XT60PW-F, placed so connector body is at top of board
    # Ref at (13, 19): body occupies y=2.5..23, pads at y=19
    lines += comp_xt60pw_f(
        "J_BATT", "XT60PW-F", 13.0, 19.0, p_net=N("VDIS"), n_net=N("PGND")
    )

    # CM1, CM2 — Wurth 7440640500 WE-SL5 CMC
    # Pin assignments: 1=VDIS_in, 2=VDIS_out, 3=PGND, 4=PGND
    lines += comp_wurth_cmc(
        "CM1",
        31.0,
        12.0,
        p1_net=N("VDIS"),
        p2_net=N("VDIS"),
        p3_net=N("PGND"),
        p4_net=N("PGND"),
    )
    lines += comp_wurth_cmc(
        "CM2",
        44.0,
        12.0,
        p1_net=N("VDIS"),
        p2_net=N("VDIS"),
        p3_net=N("PGND"),
        p4_net=N("PGND"),
    )

    # F1 — MAXI fuse holder (150 A)
    lines += comp_maxi_fuse("F1", 56.0, 9.0, p1_net=N("VDIS"), p2_net=N("VDIS"))

    # C1, C2 — 220µF/35V bulk decoupling caps on VDIS bus
    lines += comp_cp_d10(
        "C1", "220uF/35V", 68.0, 12.0, p_net=N("VDIS"), n_net=N("PGND")
    )
    # C2 y=16 (was 12): pad2 at (84,12) was 0.057 mm from U_BEC_5V_1 pin6 at
    # (85,12.96); moved to y=16 puts pad2 at (84,16) — 1.625 mm clearance.
    lines += comp_cp_d10(
        "C2", "220uF/35V", 79.0, 16.0, p_net=N("VDIS"), n_net=N("PGND")
    )

    # D1 — SMBJ33CA bidir TVS (anode=PGND, cathode=VDIS)
    lines += comp_smb_diode(
        "D1", "SMBJ33CA", 14.0, 24.0, anode_net=N("PGND"), cathode_net=N("VDIS")
    )

    # C_Y1, C_Y2 — 4.7nF Y2 safety caps (VDIS-to-CHASSIS and PGND-to-CHASSIS)
    lines += comp_y2_cap(
        "C_Y1", "4.7nF/250V_Y2", 22.0, 24.0, p1_net=N("VDIS"), p2_net=N("CHASSIS")
    )
    lines += comp_y2_cap(
        "C_Y2", "4.7nF/250V_Y2", 29.0, 24.0, p1_net=N("PGND"), p2_net=N("CHASSIS")
    )

    # C_DM1 — 10µF/50V X7R 1210 (differential mode)
    # x=40 (was 37): pad1 at (38.6,24) was 0.075 mm from C_Y2 pad2 (34,24);
    # moved right gives 3.075 mm clearance; C3 pad1 at (42.95,24) still 0.925 mm away.
    lines += comp_1210(
        "C_DM1", "10uF/50V", 40.0, 24.0, p1_net=N("VDIS"), p2_net=N("PGND")
    )

    # C3 — 100nF/50V X7R 0805 (HF bypass)
    lines += comp_0805(
        "C3", "100nF/50V", 44.0, 24.0, p1_net=N("VDIS"), p2_net=N("PGND")
    )

    # J_PGND_BATT — chassis lug pad for battery negative shield
    lines += comp_m3_lug("J_PGND_BATT", 5.0, 20.0, net=N("CHASSIS"))

    # ==========================================================
    # SECTION B: Battery disconnect FET + main current monitor
    # ==========================================================

    # J_CHASSIS — chassis ground bond pad
    lines += comp_m3_lug("J_CHASSIS", 5.0, 32.0, net=N("CHASSIS"))

    # Q_BATT_DSG — AON6556 NMOS, SOIC-8
    # Pin map: 1=S, 2=S, 3=S, 4=S/GND, 5=D, 6=D, 7=D, 8=G
    lines += comp_soic8(
        "Q_BATT_DSG",
        "AON6556",
        16.0,
        33.0,
        nets={
            "1": N("VBAT"),
            "2": N("VBAT"),
            "3": N("VBAT"),
            "4": N("VBAT"),
            "5": N("VDIS"),
            "6": N("VDIS"),
            "7": N("VDIS"),
            "8": N("DSG_GATE"),
        },
    )

    # R_DSG_G — 10k 0402 gate pull-down
    lines += comp_0402(
        "R_DSG_G", "10k", 25.0, 33.0, p1_net=N("DSG_GATE"), p2_net=N("PGND")
    )

    # R_CHGND — 0Ω chassis bond (connects digital PGND to chassis)
    lines += comp_0402(
        "R_CHGND", "0R", 30.5, 33.0, p1_net=N("PGND"), p2_net=N("CHASSIS")
    )

    # RS_MAIN — 1mΩ Kelvin shunt (CSS2H-2512K)
    # C_in=VBAT, V+=MAIN_SNS_P, V-=MAIN_SNS_N, C_out=VBAT (return side not defined)
    lines += comp_kelvin_shunt(
        "RS_MAIN",
        39.0,
        33.0,
        c_in_net=N("VBAT"),
        s_p_net=N("MAIN_SNS_P"),
        s_n_net=N("MAIN_SNS_N"),
        c_out_net=N("VBAT"),
    )

    # U_IS_MAIN — INA226 MSOP-10, I2C addr 0x44
    # Pin map: 1=IN+(MAIN_SNS_P) 2=IN-(MAIN_SNS_N) 3=GND 4=VS(+5V) 5=SDA
    #          6=SCL 7=ALERT 8=A1 9=A0 10=VBUS
    lines += comp_msop10(
        "U_IS_MAIN",
        "INA226_0x44",
        49.0,
        33.0,
        nets={
            "1": N("MAIN_SNS_P"),
            "2": N("MAIN_SNS_N"),
            "3": N("PGND"),
            "4": N("+5V"),
            "5": N("PDB_SDA"),
            "6": N("PDB_SCL"),
            "7": N("PDB_ALERT_N"),
            "8": NO_NET,
            "9": NO_NET,
            "10": N("VBAT"),
        },
    )

    # ==========================================================
    # SECTION C: Four ESC output branches
    # Each branch: F_ESCn (40A Mini fuse) → RS_n (shunt) → CM_ESCn (CMC)
    #              → C_DECn (470µF) → J_ESCn (XT30)
    # ==========================================================

    # ESC branch centres (x); 14 mm pitch gives ≥ 1.3 mm gap between
    # adjacent fuse-holder pad edges (Keystone 3568 span = 12.7 mm).
    # INA226 is stacked below the Kelvin shunt in the same column (same x,
    # different y) to avoid horizontal overlap with the adjacent shunt body.
    esc_cx = [8.0, 22.0, 36.0, 50.0]
    esc_rs_out = [
        N("ESC1_RS_OUT"),
        N("ESC2_RS_OUT"),
        N("ESC3_RS_OUT"),
        N("ESC4_RS_OUT"),
    ]
    esc_fused = [N("ESC1_FUSED"), N("ESC2_FUSED"), N("ESC3_FUSED"), N("ESC4_FUSED")]
    esc_sns_p = [N("ESC1_SNS_P"), N("ESC2_SNS_P"), N("ESC3_SNS_P"), N("ESC4_SNS_P")]
    esc_sns_n = [N("ESC1_SNS_N"), N("ESC2_SNS_N"), N("ESC3_SNS_N"), N("ESC4_SNS_N")]
    # INA226 addresses 0x40-0x43
    ina_addrs = ["0x40", "0x41", "0x42", "0x43"]

    # J_SHLD_ESC1-4 chassis lugs are omitted from generated placement.
    # Every feasible y in x=3-55 conflicts with Section A pads (y=24 CM/filter
    # components) or Section B pads (y=33).  These must be placed manually in
    # KiCad after final component compaction.  See TODO.md §3 PCB Layout.

    for n, cx in enumerate(esc_cx, start=1):
        i = n - 1  # 0-based index
        rso = esc_rs_out[i]
        fsd = esc_fused[i]
        snp = esc_sns_p[i]
        snn = esc_sns_n[i]

        # F_ESCn — Mini blade fuse holder (40 A)
        # Keystone 3568 pad1 at origin, pad2 at x+9.92; origin at cx-5
        lines += comp_mini_fuse(
            f"F_ESC{n}", cx - 5.0, 40.5, p1_net=N("VBAT"), p2_net=fsd
        )

        # RS_n — Kelvin shunt, centred at (cx, 47)
        lines += comp_kelvin_shunt(
            f"RS_{n}", cx, 47.0, c_in_net=fsd, s_p_net=snp, s_n_net=snn, c_out_net=rso
        )

        # U_ISn — INA226, placed at (cx, 53) — below shunt in same column.
        # Shunt pad bottom edge = 47 + 1.25 = 48.25 mm;
        # INA226 topmost pad top edge = 53 − 1.0 − 0.175 = 51.825 mm.
        # Pad gap = 51.825 − 48.25 = 3.575 mm ✓ (no overlap with adjacent col
        # shunt because INA stays within ±2.95 mm of cx).
        lines += comp_msop10(
            f"U_IS{n}",
            f"INA226_{ina_addrs[i]}",
            cx,
            53.0,
            nets={
                "1": snp,
                "2": snn,
                "3": N("PGND"),
                "4": N("+5V"),
                "5": N("PDB_SDA"),
                "6": N("PDB_SCL"),
                "7": N("PDB_ALERT_N"),
                "8": NO_NET,
                "9": NO_NET,
                "10": fsd,
            },
        )

        # CM_ESCn — omitted from generated placement.
        # The Wurth 7440640500 body (11.3 mm dia) occupies the same y band
        # as INA226 pads and the XT30 body on a 65 mm tall board; placing it
        # here causes pad-overlap DRC shorts.  Add manually in KiCad after
        # INA226 and XT30 are finalised.  See TODO.md §3 PCB Layout.

        # C_DECn — omitted from generated placement.
        # D10 radial cap shares y=55-60 with CMC and J_BAL Section F; causes
        # shorts with R_BAL resistors.  Add manually.  See TODO.md §3.

        # J_ESCn — XT30PW-F at (cx, 61); courtyard extends to y=44.5-65.5
        # (0.5 mm past board edge — documented in TODO.md §3).
        lines += comp_xt30pw_f(
            f"J_ESC{n}", f"XT30PW-F_ESC{n}", cx, 61.0, p_net=rso, n_net=N("PGND")
        )

    # ==========================================================
    # SECTION D: Dual redundant 5 V BEC (TPS54620 × 2 + OR diodes)
    # BEC1: FB/cap/inductor y≈8, IC y=11, R_FB y=7.5, C_OUT y=19, D_OR1 y=22
    # BEC2: FB/cap/inductor y≈28, IC y=31, R_FB y=27, C_OUT y=39, D_OR2 y=42
    # J_5V at (83.5, 35) — placed between BEC2 IC and R_FB6 to avoid pin-past-edge
    # ==========================================================

    # BEC1 ----------------------------------------------------------
    # FB_5V1 — ferrite 0805 (VDIS → BEC1_VIN_F)
    # y=13 (was 8): F1 pad2 (VDIS) at (65.9,9) was 0.029 mm from FB_5V1 pad2
    # (BEC1_VIN_F) at (63.95,8); at y=13 the clearance is ≥2 mm.
    lines += comp_0805(
        "FB_5V1", "WE-742792612", 63.0, 13.0, p1_net=N("VDIS"), p2_net=N("BEC1_VIN_F")
    )

    # C_BEC1_IN — 100µF/50V radial input cap for BEC1
    lines += comp_cp_d10(
        "C_BEC1_IN", "100uF/50V", 69.0, 8.0, p_net=N("BEC1_VIN_F"), n_net=N("PGND")
    )

    # L_BEC1 — 10µH/6A SMD inductor 1210
    # x=79 (was 77): clears C_BEC1_IN pad2 right edge at x=75 by 1.975 mm.
    lines += comp_1210(
        "L_BEC1",
        "WE-744314100_10uH",
        79.0,
        8.0,
        p1_net=N("BEC1_VIN_F"),
        p2_net=N("BEC1_SW"),
    )

    # U_BEC_5V_1 — TPS54620RGYT VQFN-20
    # Simplified net map: VIN=BEC1_VIN_F, SW=BEC1_SW, GND/EP=PGND, OUT→+5V
    # y=11 (was 9): top row pads at y=9.04; clears R_FB1_2 bottom at 7.82 by 1.22 mm.
    lines += comp_vqfn20(
        "U_BEC_5V_1",
        "TPS54620RGYT",
        84.0,
        11.0,
        nets={
            "1": N("BEC1_VIN_F"),
            "2": NO_NET,
            "3": NO_NET,
            "4": NO_NET,
            "5": N("BEC1_SW"),
            "6": N("BEC1_SW"),
            "7": N("PGND"),
            "8": N("PGND"),
            "9": N("PGND"),
            "10": N("PGND"),
            "11": N("BEC1_PRE_OR"),
            "12": NO_NET,
            "13": NO_NET,
            "14": NO_NET,
            "15": N("BEC1_VIN_F"),
            "16": N("BEC1_VIN_F"),
            "17": N("BEC1_VIN_F"),
            "18": N("BEC1_VIN_F"),
            "19": N("BEC1_VIN_F"),
            "20": N("BEC1_VIN_F"),
            "21": N("PGND"),
        },
    )

    # R_FB1_1, R_FB1_2 — feedback divider resistors (0402)
    # y=14 (was 7.5, originally 4.5): y=4.5 violated H2 hole clearance;
    # y=7.5 had 0.0 mm Default gap to L_BEC1 pad2; y=10 had 0.0 mm PGND gap
    # to U_BEC_5V_1 EP thermal pad (bottom 12.35 mm).  y=14 clears all:
    # U_BEC_5V_1 EP bottom (12.35) by 1.33 mm; L_BEC1 pad2 bottom (9.33) by 4.35 mm.
    lines += comp_0402(
        "R_FB1_1", "100k", 80.0, 14.0, p1_net=N("BEC1_PRE_OR"), p2_net=NO_NET
    )
    lines += comp_0402("R_FB1_2", "22.1k", 84.5, 14.0, p1_net=NO_NET, p2_net=N("PGND"))

    # C_BEC1_OUT — 100µF/50V radial output cap
    # x=60 (was 70): pad2 right edge at x=66 clears D_OR1 anode1 left at 66.86 by 0.86 mm
    # and D_OR1 tab left at 71.06 by 5.06 mm.
    lines += comp_cp_d10(
        "C_BEC1_OUT", "100uF/50V", 60.0, 19.0, p_net=N("BEC1_PRE_OR"), n_net=N("PGND")
    )

    # D_OR1 — MBRD1045CT DPAK (anode1=BEC1_PRE_OR, cathode=+5V, anode2=BEC2_PRE_OR)
    # x=73 (was 77.5): tab left edge moves to 71.06 — clears C_BEC1_OUT pad2 right (66)
    # by 5.06 mm; R_FB2_1 at (80,27) clears tab right edge (77.46) by 2.54 mm.
    lines += comp_dpak(
        "D_OR1",
        "MBRD1045CT",
        73.0,
        22.0,
        p1_net=N("BEC1_PRE_OR"),
        p2_net=N("+5V"),
        p3_net=N("BEC2_PRE_OR"),
    )

    # BEC2 ----------------------------------------------------------
    # FB_5V2
    lines += comp_0805(
        "FB_5V2", "WE-742792612", 63.0, 28.0, p1_net=N("VDIS"), p2_net=N("BEC2_VIN_F")
    )
    # C_BEC2_IN
    lines += comp_cp_d10(
        "C_BEC2_IN", "100uF/50V", 69.0, 28.0, p_net=N("BEC2_VIN_F"), n_net=N("PGND")
    )
    # L_BEC2 — x=79 (was 77): same clearance fix as L_BEC1.
    lines += comp_1210(
        "L_BEC2",
        "WE-744314100_10uH",
        79.0,
        28.0,
        p1_net=N("BEC2_VIN_F"),
        p2_net=N("BEC2_SW"),
    )
    # U_BEC_5V_2 — y=31 (was 29): top pads at y=29.04; clears R_FB2_2 bottom at 27.32.
    lines += comp_vqfn20(
        "U_BEC_5V_2",
        "TPS54620RGYT",
        84.0,
        31.0,
        nets={
            "1": N("BEC2_VIN_F"),
            "2": NO_NET,
            "3": NO_NET,
            "4": NO_NET,
            "5": N("BEC2_SW"),
            "6": N("BEC2_SW"),
            "7": N("PGND"),
            "8": N("PGND"),
            "9": N("PGND"),
            "10": N("PGND"),
            "11": N("BEC2_PRE_OR"),
            "12": NO_NET,
            "13": NO_NET,
            "14": NO_NET,
            "15": N("BEC2_VIN_F"),
            "16": N("BEC2_VIN_F"),
            "17": N("BEC2_VIN_F"),
            "18": N("BEC2_VIN_F"),
            "19": N("BEC2_VIN_F"),
            "20": N("BEC2_VIN_F"),
            "21": N("PGND"),
        },
    )
    # R_FB2_1 at (80,34), R_FB2_2 at (86,34):
    # y=34 clears U_BEC_5V_2 EP bottom (32.35 mm) by 1.33 mm.
    # R_FB2_2 moved to x=86 (was 84.5) because x=84.5 placed pad1 at x=83.99,
    # overlapping J_5V pin1 (PGND) circle at (83.5,35) r=1 mm.
    # At x=86: pad1 left=85.22, clears J_5V right (84.5) by 0.72 mm and
    # VQFN right-row pin11 bottom (32.73 mm) by 0.95 mm in Y.
    lines += comp_0402(
        "R_FB2_1", "100k", 80.0, 34.0, p1_net=N("BEC2_PRE_OR"), p2_net=NO_NET
    )
    lines += comp_0402("R_FB2_2", "22.1k", 86.0, 34.0, p1_net=NO_NET, p2_net=N("PGND"))
    # C_BEC2_OUT — x=60 (was 70): same fix as C_BEC1_OUT.
    lines += comp_cp_d10(
        "C_BEC2_OUT", "100uF/50V", 60.0, 39.0, p_net=N("BEC2_PRE_OR"), n_net=N("PGND")
    )
    # D_OR2 — x=73 (was 77.5): same fix as D_OR1.
    lines += comp_dpak(
        "D_OR2",
        "MBRD1045CT",
        73.0,
        42.0,
        p1_net=N("BEC2_PRE_OR"),
        p2_net=N("+5V"),
        p3_net=N("BEC2_PRE_OR"),
    )

    # J_5V — Molex Nano-Fit 4P (GND, GND, +5V, +5V)
    # y=35 (was 47.5): placed immediately below U_BEC_5V_2 courtyard bottom (33.6);
    # courtyard top=33.7, pin4 bottom=43.35; clears R_FB6_1 at (80,46) by 2.33 mm.
    lines += comp_nanofit_4p(
        "J_5V",
        "NanoFit-4P_5V",
        83.5,
        35.0,
        p_nets=[
            N("PGND"),
            N("PGND"),
            N("+5V"),
            N("+5V"),
        ],
    )
    # J_SHLD_5V — chassis shield lug OMITTED from generated placement.
    # Every position in x=78-88 conflicts with J_5V THT pads, J_6V THT pads, or
    # U_BEC_5V_2/U_BEC_6V courtyard.  Place manually after connectors are finalised.
    # See TODO.md §3 PCB Layout.

    # ==========================================================
    # SECTION E: 6 V servo BEC (TPS54540)
    # ==========================================================

    # FB_6V — ferrite 0805
    lines += comp_0805(
        "FB_6V", "WE-742792612", 63.0, 48.0, p1_net=N("VDIS"), p2_net=N("BEC6V_VIN_F")
    )

    # C_BEC_SV_IN
    lines += comp_cp_d10(
        "C_BEC_SV_IN", "100uF/50V", 69.0, 48.0, p_net=N("BEC6V_VIN_F"), n_net=N("PGND")
    )

    # L_BEC3 — 10µH 1210 — x=78 (was 77): clears C_BEC_SV_IN pad2 right (75) by
    # 0.975 mm AND clears U_BEC_6V pin1 left edge (80.55) by 0.525 mm.
    lines += comp_1210(
        "L_BEC3",
        "WE-744314100_10uH",
        78.0,
        48.0,
        p1_net=N("BEC6V_VIN_F"),
        p2_net=N("BEC6V_SW"),
    )

    # U_BEC_6V — TPS54540DDAR SOIC-8
    # Pin map: 1=BOOT 2=VIN 3=VIN 4=EN 5=SS 6=VSNS 7=COMP 8=PH (SW node)
    lines += comp_soic8(
        "U_BEC_6V",
        "TPS54540DDAR",
        84.0,
        49.5,
        nets={
            "1": NO_NET,
            "2": N("BEC6V_VIN_F"),
            "3": N("BEC6V_VIN_F"),
            "4": N("BEC6V_VIN_F"),
            "5": NO_NET,
            "6": N("+6V"),
            "7": NO_NET,
            "8": N("BEC6V_SW"),
        },
    )

    # R_FB6_1, R_FB6_2 — feedback divider (0402)
    # y=46 (was 44.5): clears J_5V courtyard bottom (44.8) and gives 2.33 mm pad gap.
    lines += comp_0402("R_FB6_1", "100k", 80.0, 46.0, p1_net=N("+6V"), p2_net=NO_NET)
    lines += comp_0402("R_FB6_2", "30.1k", 84.5, 46.0, p1_net=NO_NET, p2_net=N("PGND"))

    # C_BEC_SV_OUT — y=56 (was 59): at y=59 the THT pad outer rings fell within
    # 0.2 mm of J_ALERT MP pads at y=58.6.  At y=56 all pad-to-MP distances
    # exceed 0.58 mm (both pad1 and pad2 verified analytically).
    lines += comp_cp_d10(
        "C_BEC_SV_OUT", "100uF/50V", 70.0, 56.0, p_net=N("+6V"), n_net=N("PGND")
    )

    # J_6V — Molex Nano-Fit 4P
    # (81, 54): x=81 clears H4 NPTH at (86,61) by 2.3 mm; y=54 places courtyard top
    # at 52.7 — just above U_BEC_6V courtyard bottom (52.63); pin4 bottom=62.35 ✓.
    lines += comp_nanofit_4p(
        "J_6V",
        "NanoFit-4P_6V",
        81.0,
        54.0,
        p_nets=[
            N("PGND"),
            N("PGND"),
            N("+6V"),
            N("+6V"),
        ],
    )
    # J_SHLD_6V — chassis shield lug OMITTED from generated placement.
    # Every position near J_6V and C_BEC_SV_OUT in the y=54-65 band causes pad
    # overlap shorts.  Place manually after output caps and connectors are finalised.
    # See TODO.md §3 PCB Layout.

    # ==========================================================
    # SECTION F: BQ76930 6S cell monitor — OMITTED FROM GENERATED PLACEMENT
    # ==========================================================
    # The BQ76930 (TSSOP-30), J_BAL (JST-XH 7P), R_BAL1-6, C_CAP, J_NTC,
    # C_NTC, and J_SHLD_NTC share the y=50-65 band with ESC branch
    # components (INA226 at y=53, XT30 bodies extending from y=44.5 upward).
    # Every auto-generated position creates pad-overlap DRC shorts.
    # These components must be placed manually in KiCad once the ESC column
    # layout is finalised.
    #
    # Suggested placement target: x=62-88, y=50-65 (below D_OR1/2 DPAKs
    # after BEC vertical height is confirmed).  See TODO.md §3 PCB Layout.

    # ==========================================================
    # SECTION G: I2C interface, TVS, alert connector
    # ==========================================================

    # D_I2C — PRTR5V0U2X SOT-363 dual TVS on I2C bus
    # Pins (per NXP PRTR5V0U2X SOT-363):
    # 1=GND  2=A1  3=A2  4=Y2  5=Y1  6=VCC
    lines += comp_sot363(
        "D_I2C",
        "PRTR5V0U2X",
        59.0,
        54.0,
        nets={
            "1": N("PGND"),
            "2": N("PDB_SDA_RAW"),
            "3": N("PDB_SCL_RAW"),
            "4": N("PDB_SCL"),
            "5": N("PDB_SDA"),
            "6": N("+5V"),
        },
    )

    # R_ALERT — 2.2kΩ 0402 pull-up to +5V for ALERT_N bus
    # x=66 (was 59→62): at x=59 pad1 (+5V) overlapped J_I2C MP; at x=62
    # pad2 (PDB_ALERT_N) at (62.8,62) x-overlapped J_I2C pad3 (PDB_SCL) at
    # (62.625,61.95) — both on different nets so PGND 0.2 mm required.
    # x=66 gives 0.755 mm pad1-to-J_I2C pad4 gap and 2.9 mm to J_ALERT.
    lines += comp_0402(
        "R_ALERT", "2.2k", 66.0, 62.0, p1_net=N("+5V"), p2_net=N("PDB_ALERT_N")
    )

    # J_I2C — JST-GH 4P (GND, +5V, SCL, SDA)
    lines += comp_jst_gh_4p(
        "J_I2C",
        "JST-GH_4P_I2C",
        62.0,
        60.0,
        p_nets=[N("PGND"), N("+5V"), N("PDB_SCL"), N("PDB_SDA")],
    )
    # J_SHLD_I2C — chassis shield lug OMITTED from generated placement.
    # At (59.5, 62.5) the 6 mm copper pad overlaps J_ESC4 XT30 right pad
    # (x=56.75) and J_I2C pads — every feasible y in this column creates a short.
    # Place manually after ESC column and I2C connector are finalised.  See TODO.md §3.

    # J_ALERT — JST-GH 2P (GND, ALERT_N)
    # x=71: C_BEC_SV_OUT was moved from y=59 to y=56 to clear J_ALERT MP pads
    # at y=58.6 (constraint: |cap_y − 58.6| ≥ 0.846 mm).  J_I2C MP2 at
    # (65.1,58.6) is 1.425 mm from J_ALERT MP1 left — clearance satisfied.
    lines += comp_jst_gh_2p(
        "J_ALERT",
        "JST-GH_2P_ALERT",
        71.0,
        60.0,
        p1_net=N("PGND"),
        p2_net=N("PDB_ALERT_N"),
    )
    # J_SHLD_ALERT — chassis shield lug OMITTED from generated placement.
    # At (65.5, 62.5) the pad overlaps J_ALERT pads.  Place manually.  See TODO.md §3.

    # ==========================================================
    # COPPER ZONES
    # In1.Cu (layer 1) = GND plane  (1 oz Cu)
    # In2.Cu (layer 2) = VBAT plane (4 oz Cu)
    # Both zones flood the full board area with 0.5 mm clearance.
    # ==========================================================

    lines += _zone(N("PGND"), "In1.Cu", 0.5, 0.5, 89.5, 64.5, clearance=0.5)
    lines += _zone(N("VBAT"), "In2.Cu", 0.5, 0.5, 89.5, 64.5, clearance=0.5)

    # --- File footer ---
    lines.append(")")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    out_path = here / "FlightEngineer.kicad_pcb"
    content = gen_pcb()
    out_path.write_text(content, encoding="utf-8")
    byte_count = len(content.encode("utf-8"))
    print(f"Written: {out_path}  ({byte_count:,} bytes)")
    print(f"  Nets defined : {len(_NETS)}")
    print(f"  UUIDs used   : {next(_uid_seq) - 1}")
    print("Done.")
