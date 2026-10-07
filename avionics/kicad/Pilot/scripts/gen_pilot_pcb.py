#!/usr/bin/env python3
"""gen_pilot_pcb.py — Build the Pilot (CAPE-A-2) PCB from the schematic netlist.

Consumes ``kicads/Pilot.net`` (``kicad-cli sch export netlist --format
kicadsexpr`` of the generated ``Pilot.kicad_sch``) and writes
``kicads/Pilot.kicad_pcb`` with every footprint loaded from the KiCad 9 system
libraries or ``avionics/kicad/Serenity-Custom.pretty``, every pad netted, the
board outline, mounting holes, copper zones and the isolation-domain plane
splits.  Routing is done afterwards by ``route_pilot.py`` (Specctra DSN ->
freerouting -> SES), so re-running this script REPLACES the layout: it is the
single source of placement, not a patch tool.

Board: PocketBeagle 2 Industrial cape, 55 x 35 mm (2.165 x 1.378 in), 6-layer
(F.Cu signal / In1.Cu GND + isolated GND2 islands / In2.Cu signal / In3.Cu
signal / In4.Cu +3V3 / B.Cu signal), 1.6 mm (0.063 in) — 6 layers per the
2026-09-19 ideation (#1): the 4-layer board had only F/B for signals and was
unroutable at ~95 % placement density.  Local coordinates (u, v) in mm from the board's
top-left corner; KiCad X = 121 + u, Y = 87.5 + v (the sheet origin the prior
board used, kept so the PB2 rails land on the same absolute pads).

Placement strategy
------------------
* PB2 stacking rails, mounting holes and the field connectors are fixed by the
  cape mechanical envelope (Samtec TSM-118-04-L-DV-LC male SMT strips on B.Cu at
  v = 4.80 / 30.20, PB2 SRM Fig. 3.45 — avionics/WBS.md R2, 2026-10-06; horizontal GH
  connectors on the bottom (CAN, RS-485, 1553) and right (ETH1/ETH2) edges;
  Nano-Fit power entry on the left edge; the 2x8 SMT servo/ESC header along
  the top-left; the MAX-M10S GPS and its U.FL on F.Cu).
* ICs are placed by hand in this table so each isolator's isolated pin row
  faces its field connector, the PHYs sit between the SoC rail and their
  magnetics, and the 1553 transceiver + transformer are grouped on B.Cu with
  the 55 R / TVS / connector directly above them on F.Cu.
* Every passive is auto-placed by ``autoplace()``: the anchor is the placed
  pad it shares a non-power net with (or a named parent IC for pure supply
  bypass parts), and a spiral search finds the nearest courtyard-free spot on
  the anchor's layer, then the other layer.  Bypass capacitors therefore land
  next to the pin they serve, which is what the datasheets ask for.

Isolation: the ISOW1044 / ISOW1412 isolated domains (``GND2_CAN`` /
``GND2_RS485`` and their ``VCC2_*``) get their own In1.Cu plane islands; the
main GND plane is cut away under them.  Copper-to-copper spacing between
domains is enforced by the ``ISOLATION`` netclass (0.5 mm) in ``Pilot.kicad_pro``
— see Pilot.md §"PCB Layout Constraints" for why 8 mm creepage is not
achievable on a 55 x 35 mm cape and what that means for the isolation rating.

Author: Claude Opus 5, 2026-09-19.  Owner: sgriffing.  License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pcbnew  # type: ignore

HERE = Path(__file__).resolve().parent
KICADS = HERE.parent / "kicads"
NETLIST = KICADS / "Pilot.net"
OUT = KICADS / "Pilot.kicad_pcb"
DRU = KICADS / "Pilot.kicad_dru"
SYSLIB = Path("/usr/share/kicad/footprints")
CUSTOM = HERE.parent.parent / "Serenity-Custom.pretty"

X0, Y0 = 121.0, 87.5          # board origin (mm) in sheet coordinates
BW, BH = 55.0, 35.0           # board size (mm)
CORNER_R = 3.0
EDGE_KEEP = 0.5               # courtyard-to-edge margin for auto-placement

POWER_NETS = {"GND", "PGND", "+3V3", "+5V", "+5V_IN", "+0V9", "GND2_CAN", "GND2_RS485",
              "VCC2_CAN", "VCC2_RS485", "+3V3_PB2"}


def mm(v: float) -> int:
    return int(round(v * 1e6))


def P(u: float, v: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(mm(X0 + u), mm(Y0 + v))


# ---------------------------------------------------------------------------
# netlist parsing (kicadsexpr)
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
                    elif f[0] == "property" and len(f) > 1 and f[1] == ["name", "dnp"]:
                        d["dnp"] = True
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


# ---------------------------------------------------------------------------
# footprint loading
# ---------------------------------------------------------------------------
def load_fp(fpid: str) -> pcbnew.FOOTPRINT:
    lib, name = fpid.split(":", 1)
    path = CUSTOM if lib == "Serenity-Custom" else SYSLIB / f"{lib}.pretty"
    fp = pcbnew.FootprintLoad(str(path), name)
    if fp is None:
        raise SystemExit(f"footprint not found: {fpid}")
    fp.SetFPID(pcbnew.LIB_ID(lib, name))          # keep "Lib:Name" so --schematic-parity matches
    return fp


# ---------------------------------------------------------------------------
# fixed placement (u, v, rot, side) — see module docstring
# ---------------------------------------------------------------------------
F, B = "F", "B"
# PB2 rails (REF-SENSOR-041 Fig. 3.45): the P1/P2 pin-1 rows 3.53 / 6.07 mm from their
# long edges, 25.4 mm apart -> each rail centre-line is 4.80 mm inside the edge.  Was
# 2.54 mm (unsourced) until 2026-10-06 (avionics/WBS.md R2; TACCO was corrected 2026-10-05).
RAIL_V = 4.80
# Isolation band (same scheme as TACCO, 2026-10-05): the P2 rail is a bottom-face SMT strip
# under the old band, so the isolators move to the top face with their isolated pin rows
# facing the bottom edge, the bus connectors sit at the edge over the P2 rail, and the band
# covers F.Cu + the inner layers only.  B.Cu under the band is logic copper (rail pads,
# two-pad parts) separated from the isolated domain by the laminate.
ISO_TR_V = 20.6          # CAN-TR / RS485 centre row (SOIC-20W, pins 11-20 face +v)
ISO_V0 = ISO_TR_V - 2.6  # band top edge, between the package centre line and its logic pad row
ISO_V1 = 34.5            # to the copper-edge keep-out
ISO_U0, ISO_UM, ISO_U1 = 7.3, 21.1, 34.9   # band west edge, CAN/RS-485 island split, east edge
FIXED: Dict[str, Tuple[float, float, float, str]] = {
    # mechanical (3.6 mm PGND ring on the R3 corner centres) + PB2 rails (bottom-face SMT)
    "H1": (3.0, 3.0, 0, F), "H2": (52.0, 3.0, 0, F), "H3": (3.0, 32.0, 0, F), "H4": (52.0, 32.0, 0, F),
    "PB2-P1": (27.5, RAIL_V, 0, B), "PB2-P2": (27.5, BH - RAIL_V, 0, B),
    # --- top face (2026-10-06 re-floor-plan for the 4.80 mm SMT rails, WBS R2): the rails
    # free the whole top face, the bottom face is height-limited (~5 mm under the PB2-I)
    "J-PWM": (17.8, 5.15, 0, F),       # pad 1 column clears PB2-P1's -LC clip NPTH at u 7.18 by 0.5 mm
    "TPM": (31.7, 4.5, 0, F),
    "PWR-IN": (3.6, 18.2, 90, F),
    "J-ANT": (3.0, 8.6, 0, F),
    "IMU": (22.0, 12.2, 0, F),
    "U-3V3": (28.6, 11.8, 0, F), "L-3V3": (33.0, 11.6, 0, F),
    "T-ETH": (42.0, 8.65, 0, F), "T-ETH2": (42.0, 20.15, 0, F),   # 8.9 mm tall: top face only
    "ETH1": (51.7, 10.6, 90, F), "ETH2": (51.7, 20.4, 90, F),
    # isolation band: transceivers straddle its top edge, bus connectors at the bottom edge
    "CAN-TR": (14.2, ISO_TR_V, 0, F), "RS485": (28.0, ISO_TR_V, 0, F),
    "CAN-FD": (14.2, 30.6, 0, F), "RS-485": (28.0, 30.6, 0, F), "MIL-1553": (40.8, 30.6, 0, F),
    # --- bottom face ---
    "GPS": (11.2, 15.4, 0, B),                    # 2.5 mm: clears the PB2-I microSD; under the band
    "1553-XFM": (39.25, 17.5, 270, B),           # 4.70 mm: between the band and the PB2-I JST-SH, clear of both obstructions
    "1553-XCVR": (29.0, 13.5, 0, B),
    "TVS-1553P": (29.0, 23.6, 0, B), "TVS-1553N": (29.0, 19.8, 0, B),
    "ETH1-PHY": (48.5, 12.5, 0, B), "ETH2-PHY": (48.5, 19.5, 0, B),
    "X2Y-CAN": (18.4, ISO_V0, 0, B), "X2Y-RS485": (22.6, ISO_V0, 0, B),
}

# pads that must face a direction after placement: (ref) -> (pad numbers, direction unit vector in (u,v))
FACE: Dict[str, Tuple[List[str], Tuple[float, float]]] = {
    "CAN-TR": ([str(i) for i in range(11, 21)], (0, 1)),      # isolated row toward the bottom edge
    "RS485": ([str(i) for i in range(11, 21)], (0, 1)),
    "T-ETH": ([str(i) for i in range(9, 17)], (0, 1)),         # line sides meet mid-board beside ETH1/ETH2
    "T-ETH2": ([str(i) for i in range(9, 17)], (0, -1)),
    "ETH1-PHY": (["7", "8", "10", "11"], (1, 0)),               # MDI pins toward the magnetics
    "ETH2-PHY": (["7", "8", "10", "11"], (1, 0)),
    # 1553-XFM: fixed at 270 deg (11.3 mm wide, primary pins 1/3 on the north side toward the
    # 1553 transceiver) — the only orientation that fits between the band and the JST-SH
    "1553-XCVR": (["40", "41", "42", "43"], (1, 0)),            # BUSA toward the transformer (east)
    "PB2-P1": (["1"], (-1, 0)), "PB2-P2": (["1"], (-1, 0)),
    "PWR-IN": (["1"], (0, -1)),
    "J-PWM": (["1"], (-1, -1)),
    "GPS": (["11"], (0, 1)),                                    # RF_IN toward J-ANT (below)
}
# horizontal connectors: housing (cable exit) must point off-board
EXIT: Dict[str, Tuple[float, float]] = {
    "ETH1": (1, 0), "ETH2": (1, 0),
    "CAN-FD": (0, 1), "RS-485": (0, 1), "MIL-1553": (0, 1),
}

# isolated band (u,v) from the ISO_* rows above, split between the two domains at ISO_UM;
# the main planes are notched around it.
ISO_CAN = [(ISO_U0, ISO_V0), (ISO_UM - 0.25, ISO_V0), (ISO_UM - 0.25, ISO_V1), (ISO_U0, ISO_V1)]
ISO_485 = [(ISO_UM + 0.25, ISO_V0), (ISO_U1, ISO_V0), (ISO_U1, ISO_V1), (ISO_UM + 0.25, ISO_V1)]
ISO_BAND_POLY = [(ISO_U0, ISO_V0), (ISO_U1, ISO_V0), (ISO_U1, ISO_V1), (ISO_U0, ISO_V1)]
MAIN_PLANE = [(0.5, 0.5), (54.5, 0.5), (54.5, 34.5), (ISO_U1, 34.5), (ISO_U1, ISO_V0), (ISO_U0, ISO_V0),
              (ISO_U0, 34.5), (0.5, 34.5)]

# anchor parents for pure-supply passives (ref prefix -> parent ref)
ANCHOR_PREFIX = [
    ("C-P1-", "ETH1-PHY"), ("R-P1-", "ETH1-PHY"),
    ("C-P2-", "ETH2-PHY"), ("R-P2-", "ETH2-PHY"),
    ("C-25M", "X-25M"),
    ("C-CAN", "CAN-TR"), ("C-485", "RS485"), ("C-TPM", "TPM"), ("R-TPM", "TPM"),
    ("C-IMU", "IMU"), ("BARO", "IMU"), ("C-BARO", "BARO"), ("C-GPS", "GPS"), ("R-ANT", "GPS"), ("C-ANT", "GPS"), ("L-ANT", "J-ANT"),
    ("C-1553", "1553-XCVR"), ("R-1553", "MIL-1553"),
    ("C-3V3", "U-3V3"), ("C-BST", "U-3V3"), ("C-SS", "U-3V3"), ("R-FB3", "U-3V3"), ("R-EN3", "U-3V3"),
    ("C-IN", "PWR-IN"), ("FB1", "PWR-IN"), ("R-PGND", "PWR-IN"),
    ("CMC-CAN", "CAN-FD"), ("TVS-CAN", "CAN-FD"), ("X2Y-CAN", "CAN-TR"), ("R-CANT", "CAN-FD"),
    ("CMC-RS485", "RS-485"), ("TVS-RS485", "RS-485"), ("X2Y-RS485", "RS485"), ("R-485T", "RS-485"),
    ("R-BS1", "T-ETH"), ("C-BS1", "ETH1"), ("R-BS2", "T-ETH2"), ("C-BS2", "ETH2"),
]
# passives the isolated domain owns: force onto the isolated side of their IC
ISO_SIDE_NETS = {"GND2_CAN", "GND2_RS485", "VCC2_CAN", "VCC2_RS485", "CAN_H", "CAN_L", "CAN_H_F", "CAN_L_F",
                 "RS485_A", "RS485_B", "RS485_A_F", "RS485_B_F"}


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


# Bottom-face height budget (same stack as TACCO, owner 2026-10-05): the PB2-I's female
# receptacles stand 3.0 mm and the TSM-DV insulator 2.54 mm, so the cape's B.Cu face sits
# ~5.54 mm above the PB2-I top; its microSD socket (pin-1/2 end) and JST-SH UART
# (pin-35/36 end) stand proud between the rails (positions estimated from the owner's photo).
PB2_GAP = 3.0 + 2.54
H_MARGIN = 0.5
B_MAX_H = PB2_GAP - H_MARGIN
PB2_OBSTRUCTIONS = [
    (4.0, 10.5, 18.0, 24.5, 1.0),    # PB2-I microSD socket (owner: 12 x 7 x 1 mm)
    (45.0, 12.5, 55.0, 22.5, 2.95),  # PB2-I JST-SH 3-pin side-entry (height per JST-SH; confirm)
]
# seated heights (mm); unlisted parts are taken as <= 2.0 mm (chip passives, QFN/SOIC)
PART_HEIGHT = {
    "T-ETH": 8.9, "T-ETH2": 8.9,             # Wurth 749010012A drawing
    "1553-XFM": 4.70,                        # PremierMagnetics_DB2791S.pdf Fig. 2, .185 in
    "TVS-1553P": 2.44, "TVS-1553N": 2.44,    # SMA (DO-214AC) body
    "GPS": 2.5,                              # u-blox MAX-M10S 9.7 x 10.1 x 2.5 mm
}
# multi-pad parts allowed on B.Cu under the band (their nets escape on B.Cu alone)
UNDER_BAND_OK = {"X2Y-CAN", "X2Y-RS485", "GPS", "1553-XFM"}


def part_height(fp: pcbnew.FOOTPRINT) -> float:
    return PART_HEIGHT.get(fp.GetReference(), 2.0)


def b_height_ok(r: "Rect", h: float) -> bool:
    """True when a bottom-face part of height h at courtyard r clears the PB2-I."""
    if h > B_MAX_H:
        return False
    for u0, v0, u1, v1, oh in PB2_OBSTRUCTIONS:
        if r.hits(Rect(X0 + u0, Y0 + v0, X0 + u1, Y0 + v1)) and h > PB2_GAP - oh - H_MARGIN:
            return False
    return True


def band_rect() -> "Rect":
    return Rect(X0 + ISO_U0, Y0 + ISO_V0, X0 + ISO_U1, Y0 + ISO_V1)


class Placer:
    """Courtyard-collision aware placement on a two-sided board."""

    def __init__(self, board: pcbnew.BOARD):
        self.board = board
        self.blk: Dict[str, List[Rect]] = {F: [], B: []}
        self.edge = Rect(X0 + EDGE_KEEP, Y0 + EDGE_KEEP, X0 + BW - EDGE_KEEP, Y0 + BH - EDGE_KEEP)
        self.height = 2.0      # seated height of the part being placed
        self.iso = False       # part belongs to the isolated domain (must sit inside the band)
        self.two_pad = True    # may sit on B.Cu under the band

    def register(self, fp: pcbnew.FOOTPRINT) -> None:
        side = B if fp.IsFlipped() else F
        self.blk[side].append(courtyard(fp))
        for r in tht_rects(fp):
            self.blk[F].append(r)
            self.blk[B].append(r)
        # footprint-embedded rule areas (e.g. the U.FL all-layer keepout) block both sides
        for z in fp.Zones():
            if z.GetIsRuleArea():
                r = bbox_rect(z.GetBoundingBox()).grow(0.2)
                self.blk[F].append(r)
                self.blk[B].append(r)

    def free(self, r: Rect, side: str) -> bool:
        if r.x1 < self.edge.x1 or r.y1 < self.edge.y1 or r.x2 > self.edge.x2 or r.y2 > self.edge.y2:
            return False
        band = band_rect()
        if side == B:
            if not b_height_ok(r, self.height):
                return False
            # no logic via may enter the band, so only parts that escape on B.Cu alone
            if not self.iso and not self.two_pad and r.hits(band):
                return False
        elif self.iso:
            if not (band.x1 <= r.x1 and r.x2 <= band.x2 and band.y1 <= r.y1 and r.y2 <= band.y2):
                return False
        elif r.hits(band):
            return False
        return not any(r.hits(o) for o in self.blk[side])

    def set(self, fp: pcbnew.FOOTPRINT, u: float, v: float, rot: float, side: str) -> None:
        if (side == B) != fp.IsFlipped():
            fp.Flip(fp.GetPosition(), True)
        fp.SetPosition(P(u, v))
        fp.SetOrientationDegrees(rot)

    def shape(self, fp: pcbnew.FOOTPRINT, side: str, rot: float) -> Tuple[float, float, float, float]:
        """Courtyard rect offsets (relative to the footprint position) for one orientation."""
        self.set(fp, 0.0, 0.0, rot, side)
        r = courtyard(fp).grow(0.15)
        return (r.x1 - X0, r.y1 - Y0, r.x2 - X0, r.y2 - Y0)

    def spiral(self, fp: pcbnew.FOOTPRINT, au: float, av: float, side: str, rmax: float = 30.0, step: float = 0.25) -> bool:
        shapes = [(rot, self.shape(fp, side, rot)) for rot in (0, 90)]

        def fits(u: float, v: float):
            for rot, (dx1, dy1, dx2, dy2) in shapes:
                r = Rect(X0 + u + dx1, Y0 + v + dy1, X0 + u + dx2, Y0 + v + dy2)
                if self.free(r, side):
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
    """Rotate so the centroid of `pads` lies in direction d from the footprint centre."""
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
    """Rotate a horizontal connector so its housing (bbox centre minus pad centroid) points along d."""
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


# ---------------------------------------------------------------------------
def outline(board: pcbnew.BOARD) -> None:
    x1, y1, x2, y2, r = X0, Y0, X0 + BW, Y0 + BH, CORNER_R

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
    # arcs: KiCad arcs are CCW from start to end about centre (Y down => visually CW)
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


def patch_project_netclasses(pro_path: Path) -> None:
    """pcbnew.SaveBoard() on a Python-scripted BOARD() with no host project
    re-initialises the sibling .kicad_pro's net_settings to a single default
    'Default' netclass at KiCad's stock 0.2 mm clearance, silently discarding
    any netclass tuning — every re-run of this generator undoes it unless this
    runs immediately after.  Reapply the four netclasses this board actually
    uses (Default at the 0.127 mm JLCPCB-capable clearance, DIFF_PAIR,
    ISOLATION at 0.5 mm per Pilot.md's isolation moat, POWER) and their
    pattern assignments every time the board is regenerated."""
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
        # ISOLATION and POWER keep the BOARD MINIMUM clearance here (0.127 mm) —
        # a wider netclass-level clearance would apply uniformly to every pair of
        # different nets in the class, including the two pads of one 0402/0201
        # bypass cap sitting on VCC2_CAN/GND2_CAN or +3V3/GND, which are ~0.18 mm
        # apart on any real footprint.  The real requirement — >=0.5 mm between
        # the isolated domain and everything else — is a CROSS-domain rule, not a
        # same-class rule, so it lives in Pilot.kicad_dru as a custom DRC rule
        # keyed on NetClass difference, not in this flat per-class clearance.
        {"clearance": 0.127, "name": "ISOLATION", "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 1,
         "schematic_color": "rgba(0, 0, 0, 0.000)", "track_width": 0.25, "via_diameter": 0.6, "via_drill": 0.3},
        {"clearance": 0.127, "name": "POWER", "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 2,
         "schematic_color": "rgba(0, 0, 0, 0.000)", "track_width": 0.4, "via_diameter": 0.6, "via_drill": 0.3},
    ]
    d["net_settings"]["classes"] = classes
    patterns = []
    for n in ("ETH_TXP", "ETH_TXN", "ETH_RXP", "ETH_RXN", "ETH2_TXP", "ETH2_TXN", "ETH2_RXP", "ETH2_RXN",
              "ETH_LINE_TXP", "ETH_LINE_TXN", "ETH_LINE_RXP", "ETH_LINE_RXN",
              "ETH2_LINE_TXP", "ETH2_LINE_TXN", "ETH2_LINE_RXP", "ETH2_LINE_RXN"):
        patterns.append({"netclass": "DIFF_PAIR", "pattern": n})
    for n in ("GND2_*", "VCC2_*", "CAN_H*", "CAN_L*", "RS485_A*", "RS485_B*"):
        patterns.append({"netclass": "ISOLATION", "pattern": n})
    for n in ("+5V*", "+3V3", "GND", "PGND"):
        patterns.append({"netclass": "POWER", "pattern": n})
    d["net_settings"]["netclass_patterns"] = patterns
    ds = d["board"]["design_settings"]
    ds["rules"].update({
        "min_clearance": 0.127, "min_track_width": 0.127, "min_via_diameter": 0.5,
        "min_through_hole_diameter": 0.3, "min_hole_clearance": 0.25, "min_hole_to_hole": 0.5,
        "min_copper_edge_clearance": 0.3, "min_via_annular_width": 0.1, "min_connection": 0.127,
        "min_text_height": 0.8, "min_text_thickness": 0.1, "min_silk_clearance": 0.0,
        "solder_mask_to_copper_clearance": 0.0,
    })
    # Every footprint on this board is placed by loading a library copy
    # fresh each run (load_fp()); "lib_footprint_mismatch" here only ever
    # flags trivial serialization differences between that loaded-then-placed
    # instance and a re-read of the same library file (property ordering,
    # generator_version stamps) — never a real drift, since there is no
    # hand-edited PCB copy to diverge from the library.  Silenced rather than
    # warned to keep the DRC report meaningful; a hand-edited board would not
    # get this exemption.
    ds["rule_severities"]["lib_footprint_mismatch"] = "ignore"
    ds["rule_severities"]["lib_footprint_issues"] = "ignore"
    pro_path.write_text(json.dumps(d, indent=2) + "\n")


DRU_TEXT = """(version 1)
# Pilot Rev T custom DRC rules — generated by gen_pilot_pcb.py (CC BY 4.0)
#
# Isolation-domain integrity: the rule area named ISO_BAND (all copper layers)
# covers the isolated pin rows of the ISOW1044 / ISOW1412 and their field
# connectors.  Only nets of the ISOLATION netclass (GND2_*, VCC2_*, CAN_*,
# RS485_*) and chassis PGND may have copper inside it; any logic-side track,
# via or pad landing there is an error.
(rule iso_band_logic_copper
    (condition "A.insideArea('ISO_BAND') && A.NetClass != 'ISOLATION' && A.NetName != 'PGND' && A.NetName != ''")
    (constraint disallow track via))
# Isolated-domain copper may not leave the band on the outer layers either
# (keeps the 0.5 mm moat one straight line the reviewer can see).
(rule iso_nets_stay_in_band
    (condition "A.NetClass == 'ISOLATION' && !A.insideArea('ISO_BAND') && A.Type != 'Pad'")
    (constraint disallow track via))
# Cross-domain creepage: the ISOLATION netclass itself keeps a normal 0.127 mm
# clearance (see gen_pilot_pcb.py patch_project_netclasses docstring) so a
# 0402/0201 bypass cap straddling VCC2_CAN/GND2_CAN is not itself a DRC error.
# The real >= 0.5 mm barrier requirement is CROSS-domain only: an ISOLATION-
# class item vs a non-ISOLATION item (logic-side GND/+3V3/+5V/PGND/etc.).
# X2Y-CAN / X2Y-RS485 are the deliberate GND1<->GND2 RF bridging capacitors
# (Pilot.md Sec.2/3, TI app note SLLA337A): their whole function is a small,
# intentional high-frequency-only bridge straight across the isolation
# barrier, so their own two pin pairs cannot meet the 0.5 mm cross-domain
# clearance by design.  KiCad combines multiple matching numeric 'clearance'
# rules by taking the LARGEST applicable minimum (a later, looser rule does
# NOT relax an earlier, tighter one), so the exemption must be an EXCLUSION
# baked into this rule's own condition, not a second overriding rule.  The
# isolation the barrier still provides here comes from the capacitor's DC
# blocking, not from copper spacing.
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
    ds.SetCopperLayerCount(6)          # F / In1 GND / In2 sig / In3 sig / In4 +3V3 / B (ideation #1)
    ds.SetBoardThickness(mm(1.6))
    # JLCPCB 4-layer capability with margin (jlcpcb skill: 0.09/0.09 min; we use 5 mil)
    ds.m_MinClearance = mm(0.127)
    ds.m_TrackMinWidth = mm(0.127)
    ds.m_ViasMinSize = mm(0.5)
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
    tb.SetTitle("Pilot — EMI-Hardened Flight Control & Sensor Cape")
    tb.SetDate("2026-09-19")
    tb.SetRevision("T")
    tb.SetCompany("Griffing Technology LLC")
    tb.SetComment(0, "PocketBeagle 2 Industrial cape, 55 x 35 mm, 6-layer; generated by gen_pilot_pcb.py + route_pilot.py")
    tb.SetComment(1, "Author: Claude Opus 5 (2026-09-19); owner sgriffing; CC BY 4.0")

    outline(board)

    # nets
    netmap: Dict[str, pcbnew.NETINFO_ITEM] = {}
    for name in nets:
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        netmap[name] = ni
    pad_net: Dict[Tuple[str, str], str] = {}
    for name, nodes in nets.items():
        for ref, pin in nodes:
            pad_net[(ref, pin)] = name

    # footprints
    fps: Dict[str, pcbnew.FOOTPRINT] = {}
    for ref, c in comps.items():
        fp = load_fp(c["footprint"])
        fp.SetReference(ref)
        fp.SetValue(c["value"])
        if c["dnp"]:
            fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_DNP | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
        for pad in fp.Pads():
            n = pad_net.get((ref, pad.GetNumber()))
            if n:
                pad.SetNet(netmap[n])
        board.Add(fp)
        fps[ref] = fp

    placer = Placer(board)
    # 1) fixed parts
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

    # sanity: report fixed-part collisions so the table can be corrected
    fixed_fps = [fps[r] for r in FIXED if r in fps]
    for i, f1 in enumerate(fixed_fps):
        for f2 in fixed_fps[i + 1:]:
            if f1.IsFlipped() == f2.IsFlipped() and courtyard(f1).hits(courtyard(f2)):
                print(f"  FIXED COLLISION {f1.GetReference()} x {f2.GetReference()}")
            for r in tht_rects(f1):
                if r.hits(courtyard(f2)) and f1.GetReference()[:3] != "PB2" and not (f1.GetReference()[0] == "H" and f2.GetReference()[:3] == "PB2"):
                    print(f"  FIXED THT COLLISION {f1.GetReference()} -> {f2.GetReference()}")
            for r in tht_rects(f2):
                if r.hits(courtyard(f1)) and f2.GetReference()[:3] != "PB2" and not (f2.GetReference()[0] == "H" and f1.GetReference()[:3] == "PB2"):
                    print(f"  FIXED THT COLLISION {f2.GetReference()} -> {f1.GetReference()}")
    for f1 in fixed_fps:
        c = courtyard(f1)
        if f1.IsFlipped() and not b_height_ok(c, part_height(f1)):
            print(f"  FIXED TOO TALL FOR B.Cu {f1.GetReference()} ({part_height(f1)} mm)")
        if c.x1 < X0 + 0.3 or c.y1 < Y0 + 0.3 or c.x2 > X0 + BW - 0.3 or c.y2 > Y0 + BH - 0.3:
            print(f"  FIXED OFF-BOARD {f1.GetReference()} {c.x1-X0:.2f},{c.y1-Y0:.2f}..{c.x2-X0:.2f},{c.y2-Y0:.2f}")

    # 2) auto-place the rest, larger parts first, isolated-domain parts before the rest
    def area(fp):
        cy = courtyard(fp)
        return (cy.x2 - cy.x1) * (cy.y2 - cy.y1)

    todo = [r for r in fps if r not in FIXED]
    todo.sort(key=lambda r: -area(fps[r]))
    unplaced = []
    for ref in todo:
        fp = fps[ref]
        my_nets = {pad.GetNetname() for pad in fp.Pads() if pad.GetNetname()}
        sig = [n for n in my_nets if n not in POWER_NETS]
        anchor_fp: Optional[pcbnew.FOOTPRINT] = None
        # explicit parent
        for pre, parent in ANCHOR_PREFIX:
            if ref.startswith(pre):
                anchor_fp = fps.get(parent)
                break
        anchor = None
        if sig:
            # nearest placed pad sharing a signal net
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
        # isolated-domain passives: bias toward the isolated pin row (bottom edge)
        if my_nets & ISO_SIDE_NETS and anchor_fp is not None and anchor_fp.GetReference() in ("CAN-TR", "RS485"):
            cx, cy = pad_centroid(anchor_fp, [str(i) for i in range(11, 21)])
            anchor = (cx - X0, cy - Y0 + 1.2)
        placer.height = part_height(fp)
        placer.iso = bool(my_nets & ISO_SIDE_NETS)
        placer.two_pad = len([q for q in fp.Pads() if q.GetNumber()]) <= 2 or ref in UNDER_BAND_OK
        ok = placer.spiral(fp, anchor[0], anchor[1], side, rmax=8.0)
        if not ok:
            other = F if side == B else B
            ok = placer.spiral(fp, anchor[0], anchor[1], other, rmax=8.0)
        if not ok:
            ok = placer.spiral(fp, anchor[0], anchor[1], side, rmax=40.0) or placer.spiral(fp, anchor[0], anchor[1], other, rmax=40.0)
        if not ok:
            unplaced.append(ref)
            placer.set(fp, 60 + 3 * len(unplaced), 10, 0, F)
        placer.register(fp)
        # keep reference text small and off the pads
        for item in (fp.Reference(), fp.Value()):
            item.SetTextSize(pcbnew.VECTOR2I(mm(0.6), mm(0.6)))
            item.SetTextThickness(mm(0.1))
        fp.Value().SetVisible(False)

    # Reference designators go on the Fab (assembly) layers: at this density
    # silk refs cannot be kept off pads, and JLCPCB assembles from the CPL, not
    # the silkscreen.  Connectors keep a silk label placed by hand below.
    for ref, fp in fps.items():
        ref_text = fp.Reference()
        ref_text.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8)))
        ref_text.SetTextThickness(mm(0.12))
        ref_text.SetLayer(pcbnew.B_Fab if fp.IsFlipped() else pcbnew.F_Fab)
        ref_text.SetVisible(True)
        fp.Value().SetVisible(False)

    # zones -------------------------------------------------------------
    # Inner planes only at this stage: the outer-layer GND pours are added by
    # route_pilot.py AFTER autorouting (freerouting treats exported zones as
    # fixed copper).  The main GND / +3V3 planes carry an explicit notch over
    # the isolated band instead of relying on zone priority, so the Specctra
    # export sees non-overlapping planes.
    gnd, g2c, g2r, p3v3 = netmap["GND"], netmap["GND2_CAN"], netmap["GND2_RS485"], netmap["+3V3"]
    for layer, net, name in ((pcbnew.In1_Cu, gnd, "GND plane"), (pcbnew.In4_Cu, p3v3, "+3V3 plane")):
        add_zone(board, net, layer, MAIN_PLANE, priority=0, name=name)
    add_zone(board, g2c, pcbnew.In1_Cu, ISO_CAN, priority=1, name="GND2_CAN island")
    add_zone(board, g2r, pcbnew.In1_Cu, ISO_485, priority=1, name="GND2_RS485 island")
    # Rule areas: the isolated band is copper-free on the inner signal layers
    # (isolated nets route on F/B only) and on the +3V3 plane; a named area
    # "ISO_BAND" on every copper layer feeds the custom DRC rule in
    # Pilot.kicad_dru that forbids non-ISOLATION-class copper inside it.
    band = ISO_BAND_POLY
    for layer in (pcbnew.In2_Cu, pcbnew.In3_Cu, pcbnew.In4_Cu):
        z = pcbnew.ZONE(board)
        z.SetLayer(layer)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowCopperPour(True)
        z.SetDoNotAllowTracks(True)
        z.SetDoNotAllowVias(True)
        z.SetZoneName("isolation keepout inner")
        ol = z.Outline()
        ol.NewOutline()
        for u, v in band:
            ol.Append(mm(X0 + u), mm(Y0 + v))
        board.Add(z)
    # ISO_BAND is a pure NAME marker for the .kicad_dru rule below — it must
    # not itself restrict anything (no keepout flags), or DRC flags every
    # legitimately-isolated pad/track inside it as "not allowed".  The actual
    # restriction (only ISOLATION-class copper may exist here) is enforced by
    # the custom rule in Pilot.kicad_dru via A.insideArea('ISO_BAND').
    # F.Cu + inner layers only: B.Cu under the band is logic copper (P2 rail pads, two-pad
    # parts).  A B.Cu patch around each X2Y bridge's GND2 strip keeps its short stub to the
    # island via inside ISO_BAND.
    top_and_inner = pcbnew.LSET.AllCuMask(6)
    top_and_inner.RemoveLayer(pcbnew.B_Cu)
    bot = pcbnew.LSET()
    bot.AddLayer(pcbnew.B_Cu)
    shapes = [(top_and_inner, band)]
    for xref in ("X2Y-CAN", "X2Y-RS485"):
        xu = FIXED[xref][0]
        shapes.append((bot, [(xu - 0.35, ISO_V0 - 1.1), (xu + 0.35, ISO_V0 - 1.1),
                             (xu + 0.35, ISO_V0 + 1.1), (xu - 0.35, ISO_V0 + 1.1)]))
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

    # silkscreen ---------------------------------------------------------
    # board legend on the Fab layers (no free silk area at this density)
    text(board, "PILOT Rev T  Griffing Technology LLC  CC BY 4.0", 27.5, 16.5, pcbnew.B_Fab, 0.9, mirror=True)
    text(board, "ISOLATED CAN-FD | RS-485", 19.4, 24.4, pcbnew.F_Fab, 0.8)

    pcbnew.SaveBoard(str(OUT), board)
    patch_project_netclasses(KICADS / "Pilot.kicad_pro")
    write_dru(DRU)
    print(f"wrote {OUT}: {len(fps)} footprints, {len(nets)} nets; unplaced: {unplaced}")


if __name__ == "__main__":
    main()
