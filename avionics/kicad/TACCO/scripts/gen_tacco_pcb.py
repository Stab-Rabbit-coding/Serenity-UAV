#!/usr/bin/env python3
"""gen_tacco_pcb.py — Build the TACCO PCB from the schematic netlist.

Consumes ``kicads/TACCO.net`` (``kicad-cli sch export netlist --format
kicadsexpr`` of ``TACCO.kicad_sch``) and writes ``kicads/TACCO.kicad_pcb`` with every
footprint loaded from the KiCad 9 system libraries or
``avionics/kicad/Serenity-Custom.pretty``, every pad netted, the board
outline, mounting holes, copper zones and the isolation-domain plane splits.
Same method as Pilot's ``gen_pilot_pcb.py`` (courtyard-collision-aware
placer, hand-placed fixed table for mechanically-constrained parts, spiral
auto-placement anchored to a shared net or parent IC for the rest).

Board: PocketBeagle 2 Industrial cape, 55 x 35 mm — TACCO.md §1 is explicit that
the comms/logging/payload rebuild must fit "without any overall board size
increase from the TACCO 55 x 35 mm footprint," so this is a hard
constraint, not a starting guess.  6-layer (F.Cu signal / In1.Cu GND + isolated
GND2 islands / In2.Cu signal / In3.Cu signal / In4.Cu +3V3 / B.Cu signal),
1.6 mm — same stackup decision as Pilot (the 2026-09-19 four-bus-area
ideation's #1, which applies board-wide, not just to Pilot).

Fitting three radio modules (RFD900x 42.5x30 mm, RFM95W 16x16 mm, WL1837MOD
~9x9 mm) plus the full fleet-bus stack onto a 55x35 mm cape is only possible
because RFD900x is a piggyback module on standoffs above the cape (like the
cape-on-PocketBeagle2 stack itself) — its courtyard budget in
``gen_tacco_footprints.py`` is the header pin field, not the full module body
(see that script's docstring).  RFM95W and WL1837MOD are flush SMD and budget
their full body courtyard normally.

2026-09-29 rework (Claude Fable 5.1, owner S. Griffing; avionics/WBS.md §1.2a "TACCO
area recovery"): full auto-placement authorised by the owner.  A hand floor-planned
FIXED table now places every connector, module, transformer and IC (connectors on
the edges; isolated CAN-FD / RS-485 bus sides in a bottom band so the ISO_BAND rule
area and the GND2 islands are derived from where the transceivers actually sit; RF
at the right edge next to the two MMCX jacks), the passives are anchored to their
parent part by the courtyard-collision-aware spiral placer, and 0402/0201 parts
may fall back to the top-face cells between the PB2 rail pins at 45 deg (the rails
are no longer stack-through — Commo Rev T is standalone).  The P2 rail land omits
positions 3-10 (`PocketBeagle2_2x18_P2_Socket_Gap3-10`), so that patch is free on
both faces.

Author: Claude Sonnet 5, 2026-09-20; Claude Fable 5.1, 2026-09-29.  Owner: sgriffing.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
from __future__ import annotations

import math
import random
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pcbnew  # type: ignore

HERE = Path(__file__).resolve().parent
KICADS = HERE.parent / "kicads"
NETLIST = KICADS / "TACCO.net"
OUT = KICADS / "TACCO.kicad_pcb"
DRU = KICADS / "TACCO.kicad_dru"

# Layout experiments (ce-optimize runs): TACCO_WHATIF=<file.json> overrides fixed
# positions ("fixed": {ref: [u, v, rot, "F"|"B"]}), footprints ("fp": {ref:
# "<abs path>.pretty:Name"}), the rail cells ("rail_cells": false) and writes the
# board, project and rules into "out_dir" instead of kicads/.  Unset -> no effect.
WHATIF: dict = {}
if os.environ.get("TACCO_WHATIF"):
    import json as _json
    WHATIF = _json.loads(Path(os.environ["TACCO_WHATIF"]).read_text())
    if WHATIF.get("out_dir"):
        _out = Path(WHATIF["out_dir"])
        OUT, DRU = _out / "TACCO.kicad_pcb", _out / "TACCO.kicad_dru"
SYSLIB = Path("/usr/share/kicad/footprints")
CUSTOM = HERE.parent.parent / "Serenity-Custom.pretty"
SECURE_LIB = Path(os.environ.get("SECURE_CONTROLLERS_LIB", HERE.parents[4] / "SecureControllers" / "kicad" / "libraries"))

X0, Y0 = 121.0, 87.5          # board origin (mm), same absolute sheet coords as the legacy TACCO PCB
BW, BH = 60.0, 35.0           # board size (mm) — owner 2026-10-06: 60 x 35 (was 55 x 35, routing-bound)
U_LO = -5.0                   # board spans u = U_LO..U_LO + BW: the extra 5 mm overhangs the PB2-I's
                              # microSD (pin-1/2) end, clear of its USB-C / JST-SH end; u/v keep the
                              # 55 x 35 PB2 frame so the rails and every fixed station are unchanged
CORNER_R = 3.0
EDGE_KEEP = 0.5

POWER_NETS = {"GND", "PGND", "+3V3", "+5V", "+5V_IN", "GND2_CANB", "GND2_RS485B",
              "VCC2_CANB", "VCC2_RS485B", "+3V3_PB2", "+3V3_RF", "+1V8_IO", "+1V8_RF"}


def mm(v: float) -> int:
    return int(round(v * 1e6))


def P(u: float, v: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(mm(X0 + u), mm(Y0 + v))


# ---------------------------------------------------------------------------
def sexp(text: str):
    tokens = re.findall(r'"(?:[^"\\]|\\.)*"|\(|\)|[^\s()]+', text)
    stack: List[list] = [[]]
    for t in tokens:
        if t == "(":
            stack.append([])
        elif t == ")":
            node = stack.pop()
            stack[-1].append(node)
        else:
            stack[-1].append(t[1:-1].replace('\\"', '"') if t.startswith('"') else t)
    return stack[0][0]


def read_netlist():
    tree = sexp(NETLIST.read_text())
    comps: Dict[str, Dict[str, str]] = {}
    nets: Dict[str, List[Tuple[str, str]]] = {}
    for node in tree:
        if isinstance(node, list) and node and node[0] == "components":
            for c in node[1:]:
                d = {"ref": "", "footprint": "", "value": "", "dnp": False}
                for f in c[1:]:
                    if f[0] == "ref":
                        d["ref"] = f[1]
                    elif f[0] == "footprint":
                        d["footprint"] = f[1]
                    elif f[0] == "value":
                        d["value"] = f[1]
                    elif f[0] == "property" and any(x == ["name", "dnp"] for x in f[1:] if isinstance(x, list)):
                        d["dnp"] = True
                comps[d["ref"]] = d
        if isinstance(node, list) and node and node[0] == "nets":
            for n in node[1:]:
                name = ""
                nodes = []
                for f in n[1:]:
                    if f[0] == "name":
                        name = f[1]
                    elif f[0] == "node":
                        ref = pin = ""
                        for g in f[1:]:
                            if g[0] == "ref":
                                ref = g[1]
                            elif g[0] == "pin":
                                pin = g[1]
                        nodes.append((ref, pin))
                nets[name] = nodes
    return comps, nets


def load_fp(fpid: str) -> pcbnew.FOOTPRINT:
    lib, name = fpid.split(":", 1)
    if lib.endswith(".pretty"):  # what-if footprints from an absolute library path
        fp = pcbnew.FootprintLoad(lib, name)
        if fp is None:
            raise SystemExit(f"footprint not found: {fpid}")
        fp.SetFPID(pcbnew.LIB_ID(Path(lib).stem, name))
        return fp
    if lib == "Serenity-Custom":
        path = CUSTOM
    elif lib == "SecureControllers":  # shared verified library (see kicads/fp-lib-table)
        path = SECURE_LIB / "SecureControllers.pretty"
    else:
        path = SYSLIB / f"{lib}.pretty"
    fp = pcbnew.FootprintLoad(str(path), name)
    if fp is None:
        raise SystemExit(f"footprint not found: {fpid}")
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp


# ---------------------------------------------------------------------------
# fixed placement (u, v, rot, side) — mechanically constrained parts.
# ---------------------------------------------------------------------------
F, B = "F", "B"
# Only the truly mechanically-constrained parts are hand-placed: the chassis
# mounting holes and the PB2 stacking headers (identical positions to Pilot's
# proven-good FIXED table — same SBC, same rail geometry).  Every other part,
# including the field connectors and the three radios, is auto-placed by the
# same courtyard-collision-aware spiral placer Pilot uses; XO's part count and
# mix (three radio modules, none of which existed on Pilot) made a hand-tuned
# coordinate table for the whole board impractical to get collision-free in
# one pass, so the auto-placer — which already IS collision-safe by
# construction — takes the load instead.  This trades hand-picked edge-facing
# orientation for guaranteed non-overlap; a follow-up pass can hand-place
# connectors for cosmetic edge alignment once routing is verified.
# PB2 rail centre-lines: PocketBeagle 2 System Reference Manual Fig. 3.45 (REF-SENSOR-041) puts
# the P1/P2 pin-1 rows 3.53 / 6.07 mm from their long edges, 25.4 mm apart -> each rail
# centre-line is 4.80 mm inside the edge.  (Was 2.54 mm, unsourced, until 2026-10-05.)
RAIL_V = 4.80
# Isolation band rows (u,v): see the ISO_* geometry block below for the rationale.
# Redrawn 2026-10-05 (owner, WBS R3 option 2): transceivers on the top face, bus
# connectors at the bottom edge over the SMT P2 rail, band runs to the edge on F.Cu
# and the inner layers.  B.Cu is NOT part of the band: every isolated pad sits on the
# top face, In2-In4 are kept out and In1 carries only the GND2 islands, so the bottom
# face under the band is logic copper separated from the isolated domain by the full
# laminate (functional bus isolation, not a safety barrier — see TACCO.md §isolation).
ISO_TR_V = 20.6        # CAN-TR / RS485 centre row (SOIC-20W, pins 11-20 face +v)
ISO_V0 = ISO_TR_V - 2.6  # band edge between the package centre line and its logic pad row (same 2.6 mm offset as Rev S3)
ISO_V1 = BH - 0.5      # F.Cu + inner layers: to the copper-edge keep-out

FIXED: Dict[str, Tuple[float, float, float, str]] = {
    # chassis holes + PB2 rails (REF-SENSOR-041 geometry; x matches the manual already).
    # Holes stay at (3, 3): copper clearance to the nearest rail pad is 0.30 mm, drill to
    # drill 1.1 mm; only the courtyard boxes touch (opposite faces).
    "H1": (3.0, 3.0, 0, F), "H2": (52.0, 3.0, 0, F), "H3": (3.0, 32.0, 0, F), "H4": (52.0, 32.0, 0, F),
    "PB2-P1": (27.5, RAIL_V, 0, B), "PB2-P2": (27.5, BH - RAIL_V, 0, B),
    # --- edge connectors (2026-10-05, SSM-DV rails): the rails are bottom-face SMT, so the
    # whole top face is free and the field connectors sit at the board edges over the rails.
    # J-ETH's right MP pad must clear PB2-P1's -LC clip hole at u 47.82; the row packs left.
    "J-FAN": (21.45, 4.2, 0, F),
    "PWR-IN": (31.75, 10.3, 0, F),     # through-hole pins must clear the TSM rail pads (inner edge 0.635 mm from CL)
    "J-ETH": (42.7, 4.2, 0, F),
    "J-ANT-RADIO": (52.0, 9.9, 0, F),
    "J-1553": (3.9, 24.0, 0, F),       # opens left
    "J-SD": (47.9, 18.8, 0, B),        # card exits the right edge; 1.42 mm tall, clears the PB2-I JST
    "J-ANT-MLRS": (2.9, 8.2, 0, F),    # through-hole MMCX: west of the P1 rail's end pins, below H1
    # --- 2026-10-05 floor-plan anchors on the SSM-DV rails: the auto-placer alone left
    # T-ETH / U-3V3RF / L-1V8RF without a site (largest-first order fills the open pockets
    # before them); each is pinned to the pocket a what-if sweep found for it.
    "T-ETH": (47.5, 20.5, 0, F),       # 8.9 mm tall: top face only (PB2-I gap ~5.5 mm)
    "MLRS-MCU": (17.5, 13.5, 0, B),    # bottom face between the P1 rail and the band
    "TPM": (39.8, 21.0, 0, B),         # beside its SPI0_B/TPM pins on P2 (u 36-49): B.Cu-only escape stays short
    "1553-XFM": (31.0, 18.0, 90, B),   # 4.70 mm: bottom face, clear of both PB2-I obstructions, under the band
    "J-MLRS-SWD": (19.0, 22.4, 0, B),  # Tag-Connect NL land under the band, pads north to MLRS-MCU
    # --- isolation band: transceivers straddle its top edge, bus connectors at the edge ---
    "CAN-TR": (14.0, ISO_TR_V, 0, F),
    "RS485": (28.4, ISO_TR_V, 0, F),
    "J-CAN": (14.0, 30.6, 0, F),
    "J-485": (28.4, 30.6, 0, F),
    # X2Y GND<->GND2 bridges straddle the band's top edge on the bottom face, under
    # their transceivers; fixed so auto-placed parts cannot land on them first
    "X2Y-CAN": (10.5, ISO_V0, 0, B),    # shifted west of MLRS-MCU; still under CAN-TR, straddling the band edge
    "X2Y-RS485": (23.6, ISO_V0, 0, B),  # shifted west of 1553-XFM; still under RS485, straddling the band edge
}

# pads that must face a direction (d = unit vector in board u,v)
FACE: Dict[str, Tuple[List[str], Tuple[float, float]]] = {
    "PB2-P1": (["1"], (-1, 0)), "PB2-P2": (["1"], (-1, 0)),
    "CAN-TR": ([str(i) for i in range(11, 21)], (0, 1)),
    "RS485": ([str(i) for i in range(11, 21)], (0, 1)),
}
# connectors / card slot: opening faces this direction (pads are at the back)
EXIT: Dict[str, Tuple[float, float]] = {
    "J-SD": (-1, 0), "J-1553": (-1, 0), "J-FAN": (0, -1), "PWR-IN": (0, -1),
    "J-ETH": (0, -1), "J-CAN": (0, 1), "J-485": (0, 1),
}

# Isolation geometry (u,v) — derived from the FIXED transceiver positions: the band
# starts at the SOIC-20W body centre line (the package itself is the barrier) and
# runs to the bottom edge keep-out, plus the P2 rail gap so J-CAN's ISOLATION-net
# pads can be reached by tracks that stay inside the band.
ISO_U0, ISO_UM, ISO_U1 = 7.2, 21.2, 37.6   # band west edge, CAN/RS-485 island split, east edge
ISO_CAN = [(ISO_U0, ISO_V0), (ISO_UM - 0.25, ISO_V0), (ISO_UM - 0.25, ISO_V1), (ISO_U0, ISO_V1)]
ISO_485 = [(ISO_UM + 0.25, ISO_V0), (ISO_U1, ISO_V0), (ISO_U1, ISO_V1), (ISO_UM + 0.25, ISO_V1)]
ISO_BAND_POLY = [(ISO_U0, ISO_V0), (ISO_U1, ISO_V0), (ISO_U1, ISO_V1), (ISO_U0, ISO_V1)]
MAIN_PLANE = [(U_LO + 0.5, 0.5), (U_LO + BW - 0.5, 0.5), (U_LO + BW - 0.5, 34.5), (ISO_U1, 34.5), (ISO_U1, ISO_V0),
              (ISO_U0, ISO_V0), (ISO_U0, 34.5), (U_LO + 0.5, 34.5)]

ANCHOR_PREFIX = [
    ("C-PHY-", "ETH-PHY"), ("R-RBIAS", "ETH-PHY"), ("R-AD0", "ETH-PHY"),
    ("C-25M", "X-25M"), ("X-25M", "ETH-PHY"),
    ("C-CAN", "CAN-TR"), ("C-485", "RS485"), ("C-TPM", "TPM"), ("R-TPM", "TPM"),
    ("C-1553", "1553-XCVR"), ("R-1553P", "J-1553"), ("R-1553N", "J-1553"), ("R-1553IRQ", "1553-XCVR"),
    ("X-50M", "1553-XCVR"), ("C-50M", "1553-XCVR"),
    ("C-3V3-", "U-3V3"), ("C-BST", "U-3V3"), ("C-SS", "U-3V3"), ("R-FB3", "U-3V3"), ("R-EN3", "U-3V3"),
    ("C-RF-", "U-3V3RF"), ("L-RF", "U-3V3RF"),
    ("C-IN", "PWR-IN"), ("FB1", "PWR-IN"), ("R-PGND", "PWR-IN"),
    ("CMC-CAN", "J-CAN"), ("TVS-CAN", "J-CAN"), ("X2Y-CAN", "CAN-TR"), ("R-CANT", "J-CAN"),
    ("CMC-RS485", "J-485"), ("TVS-RS485", "J-485"), ("X2Y-RS485", "RS485"), ("R-485T", "J-485"),
    ("R-BS", "T-ETH"), ("C-BS", "J-ETH"),
    ("C-ZB-", "WIFI-BT-ZB"),
    ("C-FLASH", "NOR-FLASH"), ("R-FLASH-WP", "NOR-FLASH"), ("C-PLD", "SD-WB"),
    ("C-1V8RF", "U-1V8RF"), ("R-EN18", "U-1V8RF"), ("C-BST18", "U-1V8RF"),
    ("C-SS18", "U-1V8RF"), ("R-FB18", "U-1V8RF"), ("L-1V8RF", "U-1V8RF"),
    ("C-ANT-SH", "J-ANT-RADIO"), ("L-ANT-SER", "J-ANT-RADIO"),
    ("D-ANT-RADIO", "J-ANT-RADIO"), ("C-ANT-SANT", "WIFI-BT-ZB"),
    # mLRS bare-chip radio block
    ("C-MLRS-TCXO", "X-MLRS"), ("C-MLRS-HSE", "X-MLRS"),
    ("C-MLRS-SH", "J-ANT-MLRS"), ("L-MLRS-SER", "J-ANT-MLRS"), ("D-ANT-MLRS", "J-ANT-MLRS"),
    ("C-MLRS-TX", "RFSW-MLRS"), ("L-MLRS-TX", "RFSW-MLRS"), ("C-MLRS-RX", "RFSW-MLRS"),
    ("L-MLRS-RX", "RFSW-MLRS"), ("L-MLRS-PA", "MLRS-MCU"), ("C-MLRS-VRPA", "MLRS-MCU"),
    ("C-MLRS-", "MLRS-MCU"), ("L-MLRS-SMPS", "MLRS-MCU"), ("R-MLRS-", "MLRS-MCU"),
    ("FB-MLRS-", "MLRS-MCU"), ("LED-MLRS-", "SW-MLRS"),
]
ISO_SIDE_NETS = {"GND2_CANB", "GND2_RS485B", "VCC2_CANB", "VCC2_RS485B",
                 "CAN_B_H", "CAN_B_L", "CAN_B_H_F", "CAN_B_L_F",
                 "RS485_B_A", "RS485_B_B", "RS485_B_A_F", "RS485_B_B_F"}


# ---------------------------------------------------------------------------
class Rect:
    __slots__ = ("x1", "y1", "x2", "y2")

    def __init__(self, x1: float, y1: float, x2: float, y2: float):
        self.x1, self.y1, self.x2, self.y2 = min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)

    def grow(self, m: float) -> "Rect":
        return Rect(self.x1 - m, self.y1 - m, self.x2 + m, self.y2 + m)

    def hits(self, o: "Rect") -> bool:
        return not (self.x2 <= o.x1 or o.x2 <= self.x1 or self.y2 <= o.y1 or o.y2 <= self.y1)


def bbox_rect(bb: pcbnew.BOX2I) -> Rect:
    return Rect(bb.GetX() / 1e6, bb.GetY() / 1e6, (bb.GetX() + bb.GetWidth()) / 1e6, (bb.GetY() + bb.GetHeight()) / 1e6)


def courtyard(fp: pcbnew.FOOTPRINT) -> Rect:
    fp.BuildCourtyardCaches()
    layer = pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd
    poly = fp.GetCourtyard(layer)
    if poly.OutlineCount() > 0:
        return bbox_rect(poly.BBox())
    return bbox_rect(fp.GetBoundingBox(False, False)).grow(0.25)


def tht_rects(fp: pcbnew.FOOTPRINT) -> List[Rect]:
    out = []
    for pad in fp.Pads():
        if pad.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
            out.append(bbox_rect(pad.GetBoundingBox()).grow(0.2))
    return out


# Isolation band as rectangles (board u,v) — parts carrying ISOLATION-class nets must
# sit inside, every other part outside, or the .kicad_dru rules make them unroutable.
ISO_RECTS: Dict[str, List[Rect]] = {F: [Rect(X0 + ISO_U0, Y0 + ISO_V0, X0 + ISO_U1, Y0 + ISO_V1)],
             B: []}
# Top-face cells between the PB2 rail pins (rails are not stack-through any more):
# a 0402/0201 fits diagonally in every 2.54 mm cell — owner request 2026-09-29.
# P1 row only (2026-10-04): the P2 inter-row gap and its 2x2 pin-cell centres are the
# only escape for the header positions under the isolation band (P2-3..P2-24: MCAN0,
# MDIO0, TPM/1553/PHY control).  The band blocks every layer to the north and the board
# edge to the south, so those nets run along the gap, via down at the cell centres, and
# leave west or east of the band.  Parts parked in P2 cells closed that channel and left
# 15 nets unroutable in the 2026-09-30 freerouting passes.
RAIL_CELLS = [(7.18 + 2.54 * k, RAIL_V) for k in range(1, 17)]  # k=0 sits next to the square pin-1 pad


# Multi-pin parts allowed on B.Cu beneath the isolation band: every net must be able to
# leave on B.Cu alone.  1553-XFM (2026-10-05): eight pins, three nets to J-1553 west of
# the band and three to 1553-XCVR north of it; nothing else on the board has room for it.
# J-MLRS-SWD: the Tag-Connect NL land's six pads run straight north on B.Cu to MLRS-MCU, and
# its three NPTH alignment holes carry no copper into the band.
# TPM / NOR-FLASH / SD-WB (owner 2026-10-05, "more parts under band"): SPI parts whose bus nets
# run to the PB2 rails, which are themselves on B.Cu; their supply and ground pins leave on
# B.Cu to vias outside the band.
UNDER_BAND_OK = {"1553-XFM", "J-MLRS-SWD", "TPM", "NOR-FLASH", "SD-WB", "1553-XCVR"}


# Bottom-face height budget (owner 2026-10-05): the PB2-I's female receptacles stand 3.0 mm
# (owner caliper) and the TSM-DV insulator is 2.54 mm (samtec_tsm_catalog.pdf), so the cape's
# B.Cu face sits ~5.54 mm above the PB2-I top.  Two PB2-I parts stand proud between the rails:
# the 12 x 7 x 1 mm microSD socket at the pin-1/2 end and the 3-pin JST-SH UART at the
# pin-35/36 end (owner photo; positions estimated from it — confirm by measurement).
PLACEMENT_SEED = 1
PB2_GAP = 3.0 + 2.54
H_MARGIN = 0.5
B_MAX_H = PB2_GAP - H_MARGIN
# (u0, v0, u1, v1, obstruction height) in board u,v; generous boxes around the estimates.
PB2_OBSTRUCTIONS = [
    (4.0, 10.5, 18.0, 24.5, 1.0),    # PB2-I microSD socket (owner: 12 x 7 x 1 mm)
    (45.0, 12.5, 55.0, 22.5, 2.95),  # PB2-I JST-SH 3-pin side-entry (height per JST-SH; confirm)
]
# The PB2-I outline is 56 mm long on the 55 mm rail frame (placeholder STL), so its microSD-end
# edge sits near u = -0.5; B.Cu parts wholly west of it hang beside the PB2-I, not over it.
PB2_U_EDGE = -0.5
B_OVERHANG_MAX_H = 8.0   # stays inside the 22 mm pouch stack (CARGO_SECTION_LAYOUT.md §3a)
# Seated heights above the board (mm), from the archived datasheets where noted; parts not
# listed are assumed <= 2.0 mm (chip passives, QFN/TSSOP/SOIC, 3015 inductors at 1.5 mm).
PART_HEIGHT = {
    "T-ETH": 8.9,        # 749010012A.pdf drawing (to confirm: read from the text layer)
    "1553-XFM": 4.70,    # PremierMagnetics_DB2791S.pdf Fig. 2, .185 in
    "TVS-1553P": 2.44, "TVS-1553N": 2.44,  # SMA (DO-214AC) body
    "J-SD": 1.42,        # Molex 104031-0811 product spec (1.42 mm height)
}


def part_height(fp: pcbnew.FOOTPRINT) -> float:
    return PART_HEIGHT.get(fp.GetReference(), 2.0)


def b_height_ok(r: "Rect", h: float) -> bool:
    """True when a bottom-face part of height h at courtyard r clears the PB2-I."""
    if r.x2 < X0 + PB2_U_EDGE - H_MARGIN:
        return h <= B_OVERHANG_MAX_H  # wholly past the PB2-I's end: only the pouch stack limits it
    if h > B_MAX_H:
        return False
    for u0, v0, u1, v1, oh in PB2_OBSTRUCTIONS:
        if r.hits(Rect(X0 + u0, Y0 + v0, X0 + u1, Y0 + v1)) and h > PB2_GAP - oh - H_MARGIN:
            return False
    return True


class Placer:
    def __init__(self, board: pcbnew.BOARD):
        self.board = board
        self.blk: Dict[str, List[Rect]] = {F: [], B: []}
        # copper a through hole from the other face must clear: SMD pads + other holes
        self.pads: Dict[str, List[Rect]] = {F: [], B: []}
        self.edge = Rect(X0 + U_LO + EDGE_KEEP, Y0 + EDGE_KEEP, X0 + U_LO + BW - EDGE_KEEP, Y0 + BH - EDGE_KEEP)
        self.cells = list(RAIL_CELLS)
        self.iso = False
        self.two_pad = False
        self.height = 2.0

    def register(self, fp: pcbnew.FOOTPRINT) -> None:
        side = B if fp.IsFlipped() else F
        self.blk[side].append(courtyard(fp))
        for pad in fp.Pads():
            if pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD:
                self.pads[side].append(bbox_rect(pad.GetBoundingBox()).grow(0.3))
        for r in tht_rects(fp):
            self.blk[F].append(r)
            self.blk[B].append(r)
            self.pads[F].append(r)
            self.pads[B].append(r)
        for z in fp.Zones():
            if z.GetIsRuleArea():
                r = bbox_rect(z.GetBoundingBox()).grow(0.2)
                self.blk[F].append(r)
                self.blk[B].append(r)

    def free(self, r: Rect, side: str) -> bool:
        if r.x1 < self.edge.x1 or r.y1 < self.edge.y1 or r.x2 > self.edge.x2 or r.y2 > self.edge.y2:
            return False
        # band is top-face (+ inner) only.  Beneath it on B.Cu only two-pad logic parts
        # may sit: no logic via may enter the band, so whatever lands there must escape on
        # B.Cu alone, which a passive can and a multi-pin IC cannot.
        if side == B and not b_height_ok(r, self.height):
            return False
        inside = any(r.hits(o) for o in ISO_RECTS[side])
        if side == B and not self.iso and not self.two_pad and any(r.hits(o) for o in ISO_RECTS[F]):
            return False
        if self.iso:
            # must be wholly inside one band rectangle
            if not any(o.x1 <= r.x1 and r.x2 <= o.x2 and o.y1 <= r.y1 and r.y2 <= o.y2 for o in ISO_RECTS[side]):
                return False
        elif inside:
            return False
        return not any(r.hits(o) for o in self.blk[side])

    def rail_cell(self, fp: pcbnew.FOOTPRINT, au: float, av: float) -> bool:
        """Fallback for 0402/0201-class parts: nearest free top-face cell between the
        rail pins, part rotated 45 deg so its courtyard clears the 1.7 mm pads."""
        r = courtyard(fp)
        w, h = r.x2 - r.x1, r.y2 - r.y1
        if max(w, h) > 1.8 or min(w, h) > 1.2 or not self.cells:
            return False
        self.cells.sort(key=lambda c: (c[0] - au) ** 2 + (c[1] - av) ** 2)
        u, v = self.cells.pop(0)
        self.set(fp, u, v, 45, F)
        return True

    def set(self, fp: pcbnew.FOOTPRINT, u: float, v: float, rot: float, side: str) -> None:
        if (side == B) != fp.IsFlipped():
            fp.Flip(fp.GetPosition(), True)
        fp.SetPosition(P(u, v))
        fp.SetOrientationDegrees(rot)

    def shape(self, fp: pcbnew.FOOTPRINT, side: str, rot: float) -> Tuple[float, float, float, float]:
        self.set(fp, 0.0, 0.0, rot, side)
        r = courtyard(fp).grow(0.15)
        return (r.x1 - X0, r.y1 - Y0, r.x2 - X0, r.y2 - Y0)

    def holes(self, fp: pcbnew.FOOTPRINT, side: str, rot: float) -> List[Tuple[float, float, float, float]]:
        """Through-hole / NPTH pad boxes relative to the footprint origin: they pierce the
        opposite face too, so they must clear that face's parts (found 2026-10-05: a
        Tag-Connect NPTH landed on MLRS-MCU's pads on B.Cu)."""
        self.set(fp, 0.0, 0.0, rot, side)
        return [(r.x1 - X0, r.y1 - Y0, r.x2 - X0, r.y2 - Y0) for r in tht_rects(fp)]

    def spiral(self, fp: pcbnew.FOOTPRINT, au: float, av: float, side: str, rmax: float = 30.0, step: float = 0.25) -> bool:
        shapes = [(rot, self.shape(fp, side, rot), self.holes(fp, side, rot)) for rot in (0, 90)]
        other = B if side == F else F

        def fits(u: float, v: float):
            for rot, (dx1, dy1, dx2, dy2), holes in shapes:
                r = Rect(X0 + u + dx1, Y0 + v + dy1, X0 + u + dx2, Y0 + v + dy2)
                if self.free(r, side) and not any(
                        Rect(X0 + u + h1, Y0 + v + k1, X0 + u + h2, Y0 + v + k2).hits(o)
                        for h1, k1, h2, k2 in holes for o in self.pads[other]):
                    return rot
            return None

        cand = [(au, av)]
        r = step
        while r <= rmax:
            n = max(8, int(2 * math.pi * r / step))
            cand += [(au + r * math.cos(2 * math.pi * k / n), av + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
            r += step
        for u, v in cand:
            rot = fits(u, v)
            if rot is not None:
                self.set(fp, u, v, rot, side)
                return True
        return False


def pad_centroid(fp: pcbnew.FOOTPRINT, pads: List[str]) -> Tuple[float, float]:
    xs = [p.GetPosition() for p in fp.Pads() if p.GetNumber() in pads]
    return sum(p.x for p in xs) / len(xs) / 1e6, sum(p.y for p in xs) / len(xs) / 1e6


def face(fp: pcbnew.FOOTPRINT, pads: List[str], d: Tuple[float, float], placer: Placer, u: float, v: float, side: str) -> None:
    best, bestdot = 0.0, -9.0
    for rot in (0, 90, 180, 270):
        placer.set(fp, u, v, rot, side)
        cx, cy = pad_centroid(fp, pads)
        vx, vy = cx - (X0 + u), cy - (Y0 + v)
        n = math.hypot(vx, vy) or 1.0
        dot = (vx * d[0] + vy * d[1]) / n
        if dot > bestdot:
            best, bestdot = rot, dot
    placer.set(fp, u, v, best, side)


def orient_exit(fp: pcbnew.FOOTPRINT, d: Tuple[float, float], placer: Placer, u: float, v: float, side: str) -> None:
    best, bestdot = 0.0, -9.0
    for rot in (0, 90, 180, 270):
        placer.set(fp, u, v, rot, side)
        pads = [p.GetNumber() for p in fp.Pads() if p.GetNumber() != "MP"]
        px, py = pad_centroid(fp, pads)
        bb = fp.GetBoundingBox(False, False)
        cx, cy = (bb.GetX() + bb.GetWidth() / 2) / 1e6, (bb.GetY() + bb.GetHeight() / 2) / 1e6
        vx, vy = cx - px, cy - py
        n = math.hypot(vx, vy) or 1.0
        dot = (vx * d[0] + vy * d[1]) / n
        if dot > bestdot:
            best, bestdot = rot, dot
    placer.set(fp, u, v, best, side)


def outline(board: pcbnew.BOARD) -> None:
    x1, y1, x2, y2, r = X0 + U_LO, Y0, X0 + U_LO + BW, Y0 + BH, CORNER_R

    def seg(a, b):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(mm(a[0]), mm(a[1])))
        s.SetEnd(pcbnew.VECTOR2I(mm(b[0]), mm(b[1])))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.05))
        board.Add(s)

    def arc(c, start, end):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetCenter(pcbnew.VECTOR2I(mm(c[0]), mm(c[1])))
        s.SetStart(pcbnew.VECTOR2I(mm(start[0]), mm(start[1])))
        s.SetEnd(pcbnew.VECTOR2I(mm(end[0]), mm(end[1])))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.05))
        board.Add(s)

    seg((x1 + r, y1), (x2 - r, y1))
    seg((x2, y1 + r), (x2, y2 - r))
    seg((x2 - r, y2), (x1 + r, y2))
    seg((x1, y2 - r), (x1, y1 + r))
    arc((x2 - r, y1 + r), (x2 - r, y1), (x2, y1 + r))
    arc((x2 - r, y2 - r), (x2, y2 - r), (x2 - r, y2))
    arc((x1 + r, y2 - r), (x1 + r, y2), (x1, y2 - r))
    arc((x1 + r, y1 + r), (x1, y1 + r), (x1 + r, y1))


def add_zone(board: pcbnew.BOARD, net: pcbnew.NETINFO_ITEM, layer: int, pts: List[Tuple[float, float]],
             priority: int = 0, name: str = "") -> pcbnew.ZONE:
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(net)
    z.SetAssignedPriority(priority)
    z.SetZoneName(name)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetLocalClearance(mm(0.25))
    z.SetMinThickness(mm(0.2))
    z.SetThermalReliefGap(mm(0.3))
    z.SetThermalReliefSpokeWidth(mm(0.3))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    ol = z.Outline()
    ol.NewOutline()
    for u, v in pts:
        ol.Append(mm(X0 + u), mm(Y0 + v))
    board.Add(z)
    return z


def text(board: pcbnew.BOARD, s: str, u: float, v: float, layer: int, size: float = 1.0, mirror: bool = False) -> None:
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(P(u, v))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(0.15))
    t.SetMirrored(mirror)
    board.Add(t)


def restore_project_settings(pro_path: Path, prior: dict) -> None:
    """SaveBoard() rewrites TACCO.kicad_pro from a host-less BOARD, dropping every
    setting the owner saved from the KiCad GUI (ERC pin map, BOM presets, schematic
    editor options).  Put back any key the regenerated file lacks; keys the generator
    owns (net_settings, board design rules) are left as just written."""
    import json

    def merge(new: dict, old: dict) -> dict:
        # keep the prior file's key order so the diff shows only real changes
        out = {}
        for k, v in old.items():
            if k not in new:
                out[k] = v
            elif isinstance(v, dict) and isinstance(new[k], dict):
                out[k] = merge(new[k], v)
            else:
                out[k] = new[k]
        for k, v in new.items():
            out.setdefault(k, v)
        return out

    d = merge(json.loads(pro_path.read_text()), prior)
    pro_path.write_text(json.dumps(d, indent=2) + "\n")


def patch_project_netclasses(pro_path: Path) -> None:
    """Same rationale as gen_pilot_pcb.py's function of the same name: a
    Python-scripted BOARD() with no host project resets net_settings on save,
    so the netclasses this board actually needs are reapplied every run."""
    import json

    d = json.loads(pro_path.read_text())
    classes = [
        {"bus_width": 12, "clearance": 0.127, "diff_pair_gap": 0.15, "diff_pair_via_gap": 0.2,
         "diff_pair_width": 0.15, "line_style": 0, "microvia_diameter": 0.3, "microvia_drill": 0.1,
         "name": "Default", "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 2147483647,
         "schematic_color": "rgba(0, 0, 0, 0.000)", "track_width": 0.127, "via_diameter": 0.6,
         "via_drill": 0.3, "wire_width": 6},
        {"clearance": 0.127, "diff_pair_gap": 0.15, "diff_pair_via_gap": 0.2, "diff_pair_width": 0.15,
         "name": "DIFF_PAIR", "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 0,
         "schematic_color": "rgba(0, 0, 0, 0.000)", "track_width": 0.2, "via_diameter": 0.6, "via_drill": 0.3},
        {"clearance": 0.127, "name": "ISOLATION", "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 1,
         "schematic_color": "rgba(0, 0, 0, 0.000)", "track_width": 0.25, "via_diameter": 0.6, "via_drill": 0.3},
        {"clearance": 0.127, "name": "POWER", "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 2,
         "schematic_color": "rgba(0, 0, 0, 0.000)", "track_width": 0.4, "via_diameter": 0.6, "via_drill": 0.3},
        # Plane-fed rails (In1 GND, In4 +3V3, local +3V3_RF/+1V8_RF pours): copper on the
        # routing layers is only pad-to-via stubs at 0.5 mm-pitch QFN pins ringed by 0201
        # bypasses, so 0.2 mm (~0.9 A / 10 degC rise, 1 oz) is the width the escape
        # geometry admits; 0.4 mm left ~70 plane pins unroutable (2026-09-30 routing pass).
        {"clearance": 0.127, "name": "PLANE", "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 4,
         "schematic_color": "rgba(0, 0, 0, 0.000)", "track_width": 0.2, "via_diameter": 0.6, "via_drill": 0.3},
        # 50 Ohm microstrip on the 6-layer stack (TACCO.md §13: ~0.35 mm over the In1 GND plane)
        {"clearance": 0.127, "name": "RF", "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 3,
         "schematic_color": "rgba(0, 0, 0, 0.000)", "track_width": 0.35, "via_diameter": 0.6, "via_drill": 0.3},
    ]
    d["net_settings"]["classes"] = classes
    patterns = []
    for n in ("ETHB_TXP", "ETHB_TXN", "ETHB_RXP", "ETHB_RXN",
              "ETHB_LINE_TXP", "ETHB_LINE_TXN", "ETHB_LINE_RXP", "ETHB_LINE_RXN"):
        patterns.append({"netclass": "DIFF_PAIR", "pattern": n})
    for n in ("GND2_*", "VCC2_*", "CAN_B_H*", "CAN_B_L*", "RS485_B_A*", "RS485_B_B*"):
        patterns.append({"netclass": "ISOLATION", "pattern": n})
    for n in ("+5V*", "PGND"):
        patterns.append({"netclass": "POWER", "pattern": n})
    for n in ("+3V3", "+3V3_RF", "+1V8_RF", "GND"):
        patterns.append({"netclass": "PLANE", "pattern": n})
    for n in ("MLRS_RFO_HP", "MLRS_TX*", "MLRS_RX*", "MLRS_RFI_*", "MLRS_ANT*", "RADIO_ANT*"):
        patterns.append({"netclass": "RF", "pattern": n})
    d["net_settings"]["netclass_patterns"] = patterns
    ds = d["board"]["design_settings"]
    ds["rules"].update({
        "min_clearance": 0.127, "min_track_width": 0.127, "min_via_diameter": 0.5,
        "min_through_hole_diameter": 0.3, "min_hole_clearance": 0.25, "min_hole_to_hole": 0.5,
        "min_copper_edge_clearance": 0.3, "min_via_annular_width": 0.1, "min_connection": 0.127,
        "min_text_height": 0.8, "min_text_thickness": 0.1, "min_silk_clearance": 0.0,
        "solder_mask_to_copper_clearance": 0.0,
    })
    ds["rule_severities"]["lib_footprint_mismatch"] = "ignore"
    ds["rule_severities"]["lib_footprint_issues"] = "ignore"
    pro_path.write_text(json.dumps(d, indent=2) + "\n")


DRU_TEXT = """(version 1)
# TACCO Rev S3 custom DRC rules — generated by gen_tacco_pcb.py (CC BY 4.0)
# Same isolation-domain scheme as Pilot.kicad_dru (see that file's comments
# for the full rationale) — CAN-FD/RS-485 isolated pin rows here use the
# GND2_CANB/GND2_RS485B/VCC2_CANB/VCC2_RS485B nets (XO's _B_ suffix).
(rule iso_band_logic_copper
    (condition "A.insideArea('ISO_BAND') && A.NetClass != 'ISOLATION' && A.NetName != 'PGND' && A.NetName != ''")
    (constraint disallow track via))
(rule iso_nets_stay_in_band
    (condition "A.NetClass == 'ISOLATION' && !A.insideArea('ISO_BAND') && A.Type != 'Pad'")
    (constraint disallow track via))
(rule iso_cross_domain_clearance
    (condition "A.NetClass == 'ISOLATION' && B.NetClass != 'ISOLATION' && B.NetName != '' && A.Reference != 'X2Y-CAN' && A.Reference != 'X2Y-RS485' && B.Reference != 'X2Y-CAN' && B.Reference != 'X2Y-RS485'")
    (constraint clearance (min 0.5mm)))
"""


def write_dru(path: Path) -> None:
    path.write_text(DRU_TEXT)


def main() -> None:
    comps, nets = read_netlist()
    board = pcbnew.BOARD()
    ds = board.GetDesignSettings()
    ds.SetCopperLayerCount(6)
    ds.SetBoardThickness(mm(1.6))
    ds.m_MinClearance = mm(0.127)
    ds.m_TrackMinWidth = mm(0.127)
    ds.m_ViasMinSize = mm(0.5)  # netclass vias are 0.6/0.3 so hole-to-copper stays >= 0.25 at 0.127 clearance
    ds.m_MinThroughDrill = mm(0.3)
    ds.m_HoleClearance = mm(0.25)
    ds.m_HoleToHoleMin = mm(0.5)
    ds.m_CopperEdgeClearance = mm(0.3)
    ds.m_SilkClearance = mm(0.0)
    ds.m_MinSilkTextHeight = mm(0.8)
    ds.m_MinSilkTextThickness = mm(0.1)
    ds.m_ViasMinAnnularWidth = mm(0.1)
    ds.m_MinConn = mm(0.127)
    board.SetLayerName(pcbnew.In1_Cu, "In1.Cu")
    board.SetLayerName(pcbnew.In2_Cu, "In2.Cu")
    board.SetLayerName(pcbnew.In3_Cu, "In3.Cu")
    board.SetLayerName(pcbnew.In4_Cu, "In4.Cu")
    board.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
    board.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_SIGNAL)
    board.SetLayerType(pcbnew.In3_Cu, pcbnew.LT_SIGNAL)
    board.SetLayerType(pcbnew.In4_Cu, pcbnew.LT_POWER)

    tb = board.GetTitleBlock()
    tb.SetTitle("TACCO — Comms / Logging / Payload Cape")
    tb.SetDate("2026-09-29")
    tb.SetRevision("S3")
    tb.SetCompany("Griffing Technology LLC")
    tb.SetComment(0, "PocketBeagle 2 Industrial cape, 60 x 35 mm, 6-layer; generated by gen_tacco_pcb.py")
    tb.SetComment(1, "Authors: Claude Sonnet 5 (2026-09-20), Claude Fable 5.1 (2026-09-29); owner sgriffing; CC BY 4.0")

    outline(board)

    netmap: Dict[str, pcbnew.NETINFO_ITEM] = {}
    for name in nets:
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        netmap[name] = ni
    pad_net: Dict[Tuple[str, str], str] = {}
    for name, nodes in nets.items():
        for ref, pin in nodes:
            pad_net[(ref, pin)] = name

    for ref, val in WHATIF.get("fixed", {}).items():
        FIXED[ref] = (float(val[0]), float(val[1]), float(val[2]), str(val[3]))
    if WHATIF.get("rail_cells") is False:
        RAIL_CELLS.clear()
    fps: Dict[str, pcbnew.FOOTPRINT] = {}
    for ref, c in comps.items():
        fp = load_fp(WHATIF.get("fp", {}).get(ref, c["footprint"]))
        fp.SetReference(ref)
        fp.SetValue(c["value"])
        # library lands such as Tag-Connect carry "exclude from BOM"; the schematic
        # symbols are all in_bom, so keep the attributes in parity (DNP handles the
        # no-part case).
        fp.SetAttributes(fp.GetAttributes() & ~pcbnew.FP_EXCLUDE_FROM_BOM)
        if c["dnp"]:
            fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_DNP | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
        for pad in fp.Pads():
            n = pad_net.get((ref, pad.GetNumber()))
            if n:
                pad.SetNet(netmap[n])
        board.Add(fp)
        fps[ref] = fp

    placer = Placer(board)
    for ref, (u, v, rot, side) in FIXED.items():
        fp = fps.get(ref)
        if fp is None:
            continue
        placer.set(fp, u, v, rot, side)
        if ref in FACE:
            face(fp, FACE[ref][0], FACE[ref][1], placer, u, v, side)
        if ref in EXIT:
            orient_exit(fp, EXIT[ref], placer, u, v, side)
        placer.register(fp)

    fixed_fps = [fps[r] for r in FIXED if r in fps]
    for i, f1 in enumerate(fixed_fps):
        for f2 in fixed_fps[i + 1:]:
            same = f1.IsFlipped() == f2.IsFlipped()
            cross = (not same) and (any(r.hits(courtyard(f2)) for r in tht_rects(f1))
                                    or any(r.hits(courtyard(f1)) for r in tht_rects(f2)))
            if (same and courtyard(f1).hits(courtyard(f2))) or cross:
                print(f"  FIXED COLLISION {f1.GetReference()} x {f2.GetReference()}")
    for f1 in fixed_fps:
        if f1.IsFlipped() and not b_height_ok(courtyard(f1), part_height(f1)):
            print(f"  FIXED TOO TALL FOR B.Cu {f1.GetReference()} ({part_height(f1)} mm)")
    for f1 in fixed_fps:
        c = courtyard(f1)
        if c.x1 < X0 + U_LO + 0.3 or c.y1 < Y0 + 0.3 or c.x2 > X0 + U_LO + BW - 0.3 or c.y2 > Y0 + BH - 0.3:
            print(f"  FIXED OFF-BOARD {f1.GetReference()} {c.x1-X0:.2f},{c.y1-Y0:.2f}..{c.x2-X0:.2f},{c.y2-Y0:.2f}")

    def area(fp):
        r = courtyard(fp)
        return (r.x2 - r.x1) * (r.y2 - r.y1)

    todo = [r for r in fps if r not in FIXED]
    # largest first, but never before the ANCHOR_PREFIX parent it clusters around: a child
    # placed while its parent still sat unplaced at the origin anchored off-board and was
    # dropped (L-RF1 / L-1V8RF before their regulators, found 2026-10-05).
    def parent_of(r: str) -> Optional[str]:
        for pre, par in ANCHOR_PREFIX:
            if r.startswith(pre):
                return par if par in fps and par not in FIXED and par != r else None
        return None

    # "seed": jitter the area order (+/-20 %) so a sweep can search orderings the
    # strict largest-first rule never tries; the committed board uses PLACEMENT_SEED.
    # PLACEMENT_SEED 1 (2026-10-05): of seeds 1-6, five place every part DRC-clean; seed 1 has
    # the shortest total half-perimeter wirelength (3116 mm vs 3313-3561 mm).
    # Not a security function: a reproducible seed for placement order only (DevSkim DS148264).
    rng = random.Random(WHATIF.get("seed", PLACEMENT_SEED))  # DevSkim: ignore DS148264
    jit = {r: 1.0 + rng.uniform(-0.2, 0.2) for r in sorted(fps)}

    def order_key(r: str) -> Tuple[float, int, float, str]:
        par = parent_of(r)
        if par:
            return (-area(fps[par]) * jit[par], 1, -area(fps[r]) * jit[r], r)
        return (-area(fps[r]) * jit[r], 0, 0.0, r)

    todo.sort(key=order_key)
    unplaced = []
    anchors: Dict[str, Tuple[Tuple[float, float], str]] = {}
    for ref in todo:
        fp = fps[ref]
        my_nets = {pad.GetNetname() for pad in fp.Pads() if pad.GetNetname()}
        # sorted: set order follows PYTHONHASHSEED, so an unsorted walk picked a
        # different anchor net (and placement) on every run (found 2026-10-04)
        sig = sorted(n for n in my_nets if n not in POWER_NETS)
        anchor_fp: Optional[pcbnew.FOOTPRINT] = None
        for pre, parent in ANCHOR_PREFIX:
            if ref.startswith(pre):
                anchor_fp = fps.get(parent)
                break
        anchor = None
        if sig:
            best = None
            for n in sig:
                for (r2, pin) in nets.get(n, []):
                    if r2 == ref or r2 not in FIXED and r2 in todo and fps[r2].GetPosition() == pcbnew.VECTOR2I(0, 0):
                        continue
                    f2 = fps[r2]
                    for pad in f2.Pads():
                        if pad.GetNumber() == pin:
                            pos = pad.GetPosition()
                            cand = (pos.x / 1e6 - X0, pos.y / 1e6 - Y0, f2)
                            if anchor_fp is None or f2 is anchor_fp or best is None:
                                best = cand
            if best:
                anchor = (best[0], best[1])
                if anchor_fp is None:
                    anchor_fp = best[2]
        if anchor is None and anchor_fp is not None:
            pos = anchor_fp.GetPosition()
            anchor = (pos.x / 1e6 - X0, pos.y / 1e6 - Y0)
        if anchor is None:
            anchor = (27.5, 17.5)
        side = (B if anchor_fp.IsFlipped() else F) if anchor_fp is not None else F
        if my_nets & ISO_SIDE_NETS and anchor_fp is not None and anchor_fp.GetReference() in ("CAN-TR", "RS485"):
            cx, cy = pad_centroid(anchor_fp, [str(i) for i in range(11, 21)])
            anchor = (cx - X0, cy - Y0 + 1.2)
        placer.iso = bool(my_nets & ISO_SIDE_NETS) and ref not in ("X2Y-CAN", "X2Y-RS485")
        if ref in ("X2Y-CAN", "X2Y-RS485"):
            # X2Y bridges GND<->GND2 across the barrier: straddle the band edge.
            placer.iso = False
            uu = FIXED["CAN-TR" if ref == "X2Y-CAN" else "RS485"][0]
            placer.set(fp, uu, ISO_V0, 0, B)
            placer.register(fp)
            continue
        anchors[ref] = (anchor, side)
        placer.height = part_height(fp)
        placer.two_pad = len([p for p in fp.Pads() if p.GetNumber()]) <= 2 or ref in UNDER_BAND_OK
        other = F if side == B else B
        ok = placer.spiral(fp, anchor[0], anchor[1], side, rmax=8.0)
        if not ok:
            ok = placer.spiral(fp, anchor[0], anchor[1], other, rmax=8.0)
        if not ok:
            ok = placer.spiral(fp, anchor[0], anchor[1], side, rmax=40.0) or placer.spiral(fp, anchor[0], anchor[1], other, rmax=40.0)
        if not ok and not placer.iso:
            ok = placer.rail_cell(fp, anchor[0], anchor[1])
        if not ok:
            unplaced.append(ref)
            placer.set(fp, 60 + 3 * len(unplaced), 10, 0, F)
        placer.register(fp)
        for item in (fp.Reference(), fp.Value()):
            item.SetTextSize(pcbnew.VECTOR2I(mm(0.6), mm(0.6)))
            item.SetTextThickness(mm(0.1))
        fp.Value().SetVisible(False)

    # --- rip-up-and-repair (2026-10-05): at ~95 % fill the greedy pass strands one or two
    # parts.  For each, find the site whose blockers are fewest small movable parts, lift
    # them, place the stranded part there and re-place the lifted parts; keep the result only
    # when every part lands, otherwise restore and try the next site.
    def flags(ref: str) -> Tuple[bool, bool, float]:
        fp = fps[ref]
        nets = {pad.GetNetname() for pad in fp.Pads() if pad.GetNetname()}
        iso = bool(nets & ISO_SIDE_NETS) and ref not in ("X2Y-CAN", "X2Y-RS485")
        two = len([q for q in fp.Pads() if q.GetNumber()]) <= 2 or ref in UNDER_BAND_OK
        return iso, two, part_height(fp)

    def rebuild() -> None:
        placer.blk = {F: [], B: []}
        placer.pads = {F: [], B: []}
        for r2, f2 in fps.items():
            if r2 not in unplaced:
                placer.register(f2)

    def movable(r2: str) -> bool:
        return r2 not in FIXED and area(fps[r2]) < 20.0

    def try_place(ref: str, au: float, av: float, side: str, rmax: float = 40.0) -> bool:
        placer.iso, placer.two_pad, placer.height = flags(ref)
        fp = fps[ref]
        other = B if side == F else F
        return placer.spiral(fp, au, av, side, rmax=rmax) or placer.spiral(fp, au, av, other, rmax=rmax)

    for ref in list(unplaced):
        fp = fps[ref]
        (au, av), side0 = anchors.get(ref, ((27.5, 17.5), F))
        sites = []
        for side in (side0, B if side0 == F else F):
            for rot in (0, 90):
                placer.set(fp, 0.0, 0.0, rot, side)
                c = courtyard(fp).grow(0.15)
                dx1, dy1, dx2, dy2 = c.x1 - X0, c.y1 - Y0, c.x2 - X0, c.y2 - Y0
                for iu in range(int(2 * U_LO) + 2, int(2 * (U_LO + BW)) - 2):
                    for iv in range(2, 68):
                        u, v = iu * 0.5, iv * 0.5
                        r = Rect(X0 + u + dx1, Y0 + v + dy1, X0 + u + dx2, Y0 + v + dy2)
                        if r.x1 < placer.edge.x1 or r.y1 < placer.edge.y1 or r.x2 > placer.edge.x2 or r.y2 > placer.edge.y2:
                            continue
                        iso, two, h = flags(ref)
                        if side == B and not b_height_ok(r, h):
                            continue
                        if any(r.hits(o) for o in ISO_RECTS[side]) and not iso:
                            continue
                        if side == B and not two and any(r.hits(o) for o in ISO_RECTS[F]):
                            continue
                        hit = []
                        ok_site = True
                        for r2, f2 in fps.items():
                            if r2 == ref or r2 in unplaced:
                                continue
                            same = (B if f2.IsFlipped() else F) == side
                            if (same and courtyard(f2).hits(r)) or any(t.hits(r) for t in tht_rects(f2)):
                                if not movable(r2):
                                    ok_site = False
                                    break
                                hit.append(r2)
                        if ok_site and len(hit) <= 12:
                            sites.append((sum(area(fps[q]) for q in hit), (u - au) ** 2 + (v - av) ** 2, u, v, rot, side, hit))
        sites.sort()
        done = False
        seen: set = set()
        for _, _, u, v, rot, side, hit in sites:
            key = (side, tuple(sorted(hit)))
            if key in seen or len(seen) >= 120:
                continue
            seen.add(key)
            saved = {r2: (fps[r2].GetPosition(), fps[r2].GetOrientationDegrees(), fps[r2].IsFlipped()) for r2 in hit}
            for r2 in hit:
                placer.set(fps[r2], 60.0, 40.0, 0, F)
            unplaced.extend(hit)
            unplaced.remove(ref)
            placer.set(fp, u, v, rot, side)
            rebuild()
            placer.iso, placer.two_pad, placer.height = flags(ref)
            good = True
            for r2 in sorted(hit, key=lambda q: -area(fps[q])):
                (a2u, a2v), s2 = anchors.get(r2, ((27.5, 17.5), F))
                if try_place(r2, a2u, a2v, s2):
                    unplaced.remove(r2)
                    placer.register(fps[r2])
                else:
                    good = False
                    break
            if good:
                done = True
                print(f"  repair: {ref} placed at ({u:.1f}, {v:.1f}) {side}, re-placed {hit}")
                break
            for r2 in hit:
                pos, rot2, flp = saved[r2]
                if fps[r2].IsFlipped() != flp:
                    fps[r2].Flip(fps[r2].GetPosition(), True)
                fps[r2].SetPosition(pos)
                fps[r2].SetOrientationDegrees(rot2)
                if r2 in unplaced:
                    unplaced.remove(r2)
            unplaced.append(ref)
            placer.set(fp, 60 + 3 * len(unplaced), 10, 0, F)
            rebuild()
        if not done:
            print(f"  repair: no site for {ref}")

    for ref, fp in fps.items():
        ref_txt = fp.Reference()
        ref_txt.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8)))
        ref_txt.SetTextThickness(mm(0.12))
        ref_txt.SetLayer(pcbnew.B_Fab if fp.IsFlipped() else pcbnew.F_Fab)
        ref_txt.SetVisible(True)
        fp.Value().SetVisible(False)

    gnd, g2c, g2r, p3v3 = netmap["GND"], netmap["GND2_CANB"], netmap["GND2_RS485B"], netmap["+3V3"]
    for layer, net, name in ((pcbnew.In1_Cu, gnd, "GND plane"), (pcbnew.In4_Cu, p3v3, "+3V3 plane")):
        add_zone(board, net, layer, MAIN_PLANE, priority=0, name=name)
    add_zone(board, g2c, pcbnew.In1_Cu, ISO_CAN, priority=1, name="GND2_CANB island")
    add_zone(board, g2r, pcbnew.In1_Cu, ISO_485, priority=1, name="GND2_RS485B island")
    band = ISO_BAND_POLY
    for layer in (pcbnew.In2_Cu, pcbnew.In3_Cu, pcbnew.In4_Cu):
        z = pcbnew.ZONE(board)
        z.SetLayer(layer)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowCopperPour(True)
        z.SetDoNotAllowTracks(True)
        z.SetDoNotAllowVias(True)
        z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
        z.SetZoneName("isolation keepout inner")
        ol = z.Outline()
        ol.NewOutline()
        for u, v in band:
            ol.Append(mm(X0 + u), mm(Y0 + v))
        board.Add(z)
    # ISO_BAND (named rule area read by the .kicad_dru rules): F.Cu and the inner layers
    # only — B.Cu under the band is logic copper (see the ISO_V0 comment).
    top_and_inner = pcbnew.LSET.AllCuMask(6)
    top_and_inner.RemoveLayer(pcbnew.B_Cu)
    # B.Cu patches around each X2Y bridge (bottom face, straddling the band edge): its GND2
    # pad's short stub to the island via is an ISOLATION track and must sit inside ISO_BAND.
    bot = pcbnew.LSET()
    bot.AddLayer(pcbnew.B_Cu)
    shapes = [(top_and_inner, band)]
    for xref in ("X2Y-CAN", "X2Y-RS485"):
        xu = FIXED[xref][0]
        # only the G1-G2 (GND2) strip between its two GND end terminals: u +/-0.35 mm
        shapes.append((bot, [(xu - 0.35, ISO_V0 - 1.1), (xu + 0.35, ISO_V0 - 1.1), (xu + 0.35, ISO_V0 + 1.1), (xu - 0.35, ISO_V0 + 1.1)]))
    for lset, poly in shapes:
        z = pcbnew.ZONE(board)
        z.SetLayerSet(lset)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowCopperPour(False)
        z.SetDoNotAllowTracks(False)
        z.SetDoNotAllowVias(False)
        z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
        z.SetZoneName("ISO_BAND")
        ol = z.Outline()
        ol.NewOutline()
        for u, v in poly:
            ol.Append(mm(X0 + u), mm(Y0 + v))
        board.Add(z)

    text(board, "TACCO Rev S3  Griffing Technology LLC  CC BY 4.0", 27.5, 17.2, pcbnew.B_Fab, 0.9, mirror=True)
    text(board, "ISOLATED CAN-FD | RS-485", 21.0, 24.4, pcbnew.F_Fab, 0.8)

    pro = OUT.parent / "TACCO.kicad_pro"
    import json
    prior = json.loads(pro.read_text()) if pro.exists() else {}
    pcbnew.SaveBoard(str(OUT), board)
    patch_project_netclasses(pro)
    restore_project_settings(pro, prior)
    write_dru(DRU)
    print(f"wrote {OUT}: {len(fps)} footprints, {len(nets)} nets; unplaced: {unplaced}")


if __name__ == "__main__":
    main()
