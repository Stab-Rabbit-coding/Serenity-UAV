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

Author: Claude Sonnet 5, 2026-09-20.  Owner: sgriffing.  License: CC BY 4.0.
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
NETLIST = KICADS / "TACCO.net"
OUT = KICADS / "TACCO.kicad_pcb"
DRU = KICADS / "TACCO.kicad_dru"
SYSLIB = Path("/usr/share/kicad/footprints")
CUSTOM = HERE.parent.parent / "Serenity-Custom.pretty"

X0, Y0 = 121.0, 87.5          # board origin (mm), same absolute sheet coords as the legacy TACCO PCB
BW, BH = 55.0, 35.0           # board size (mm) — TACCO.md §1 hard constraint
CORNER_R = 3.0
EDGE_KEEP = 0.5

POWER_NETS = {"GND", "PGND", "+3V3", "+5V", "+5V_IN", "GND2_CANB", "GND2_RS485B",
              "VCC2_CANB", "VCC2_RS485B", "+3V3_PB2", "+3V3_RF", "+1V8_IO"}


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
    path = CUSTOM if lib == "Serenity-Custom" else SYSLIB / f"{lib}.pretty"
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
FIXED: Dict[str, Tuple[float, float, float, str]] = {
    "H1": (3.0, 3.0, 0, F), "H2": (52.0, 3.0, 0, F), "H3": (3.0, 32.0, 0, F), "H4": (52.0, 32.0, 0, F),
    "PB2-P1": (27.5, 2.54, 0, B), "PB2-P2": (27.5, 32.46, 0, B),
}

FACE: Dict[str, Tuple[List[str], Tuple[float, float]]] = {
    "PB2-P1": (["1"], (-1, 0)), "PB2-P2": (["1"], (-1, 0)),
}
EXIT: Dict[str, Tuple[float, float]] = {}

ISO_CAN = [(5.5, 23.0), (17.3, 23.0), (17.3, 30.2), (5.5, 30.2)]
ISO_485 = [(17.5, 23.0), (33.6, 23.0), (33.6, 30.2), (17.5, 30.2)]
MAIN_PLANE = [(0.5, 0.5), (54.5, 0.5), (54.5, 34.5), (34.1, 34.5), (34.1, 22.5), (5.0, 22.5), (5.0, 34.5), (0.5, 34.5)]

ANCHOR_PREFIX = [
    ("C-PHY-", "ETH-PHY"), ("R-RBIAS", "ETH-PHY"), ("R-AD0", "ETH-PHY"),
    ("C-25M", "X-25M"),
    ("C-CAN", "CAN-TR"), ("C-485", "RS485"), ("C-TPM", "TPM"), ("R-TPM", "TPM"),
    ("C-1553", "1553-XCVR"), ("R-1553", "J-1553"),
    ("C-3V3-", "U-3V3"), ("C-BST", "U-3V3"), ("C-SS", "U-3V3"), ("R-FB3", "U-3V3"), ("R-EN3", "U-3V3"),
    ("C-RF-", "U-3V3RF"), ("L-RF", "U-3V3RF"),
    ("C-IN", "PWR-IN"), ("FB1", "PWR-IN"), ("R-PGND", "PWR-IN"),
    ("CMC-CAN", "J-CAN"), ("TVS-CAN", "J-CAN"), ("X2Y-CAN", "CAN-TR"), ("R-CANT", "J-CAN"),
    ("CMC-RS485", "J-485"), ("TVS-RS485", "J-485"), ("X2Y-RS485", "RS485"), ("R-485T", "J-485"),
    ("R-BS", "T-ETH"), ("C-BS", "J-ETH"),
    ("FB-SIK", "SIK"), ("C-SIK", "SIK"),
    ("C-ZB-", "WIFI-BT-ZB"), ("FB-SDIO", "WIFI-BT-ZB"),
    ("C-FLASH", "NOR-FLASH"), ("R-FLASH-WP", "NOR-FLASH"), ("C-PLD", "SD-WB"),
    ("C-1V8RF", "U-1V8RF"), ("R-EN18", "U-1V8RF"), ("C-BST18", "U-1V8RF"),
    ("C-SS18", "U-1V8RF"), ("R-FB18", "U-1V8RF"), ("L-1V8RF", "U-1V8RF"),
    ("FL-SIK", "J-SMA-SIK"), ("D-ANT-SIK", "J-SMA-SIK"),
    ("C-ANT-SH", "J-ANT-RADIO"), ("L-ANT-SER", "J-ANT-RADIO"),
    ("D-ANT-RADIO", "J-ANT-RADIO"), ("C-ANT-SANT", "WIFI-BT-ZB"),
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


class Placer:
    def __init__(self, board: pcbnew.BOARD):
        self.board = board
        self.blk: Dict[str, List[Rect]] = {F: [], B: []}
        self.edge = Rect(X0 + EDGE_KEEP, Y0 + EDGE_KEEP, X0 + BW - EDGE_KEEP, Y0 + BH - EDGE_KEEP)

    def register(self, fp: pcbnew.FOOTPRINT) -> None:
        side = B if fp.IsFlipped() else F
        self.blk[side].append(courtyard(fp))
        for r in tht_rects(fp):
            self.blk[F].append(r)
            self.blk[B].append(r)
        for z in fp.Zones():
            if z.GetIsRuleArea():
                r = bbox_rect(z.GetBoundingBox()).grow(0.2)
                self.blk[F].append(r)
                self.blk[B].append(r)

    def free(self, r: Rect, side: str) -> bool:
        if r.x1 < self.edge.x1 or r.y1 < self.edge.y1 or r.x2 > self.edge.x2 or r.y2 > self.edge.y2:
            return False
        return not any(r.hits(o) for o in self.blk[side])

    def set(self, fp: pcbnew.FOOTPRINT, u: float, v: float, rot: float, side: str) -> None:
        if (side == B) != fp.IsFlipped():
            fp.Flip(fp.GetPosition(), True)
        fp.SetPosition(P(u, v))
        fp.SetOrientationDegrees(rot)

    def shape(self, fp: pcbnew.FOOTPRINT, side: str, rot: float) -> Tuple[float, float, float, float]:
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
    """Same rationale as gen_pilot_pcb.py's function of the same name: a
    Python-scripted BOARD() with no host project resets net_settings on save,
    so the netclasses this board actually needs are reapplied every run."""
    import json

    d = json.loads(pro_path.read_text())
    classes = [
        {"bus_width": 12, "clearance": 0.127, "diff_pair_gap": 0.15, "diff_pair_via_gap": 0.2,
         "diff_pair_width": 0.15, "line_style": 0, "microvia_diameter": 0.3, "microvia_drill": 0.1,
         "name": "Default", "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 2147483647,
         "schematic_color": "rgba(0, 0, 0, 0.000)", "track_width": 0.127, "via_diameter": 0.5,
         "via_drill": 0.3, "wire_width": 6},
        {"clearance": 0.127, "diff_pair_gap": 0.15, "diff_pair_via_gap": 0.2, "diff_pair_width": 0.15,
         "name": "DIFF_PAIR", "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 0,
         "schematic_color": "rgba(0, 0, 0, 0.000)", "track_width": 0.2, "via_diameter": 0.5, "via_drill": 0.3},
        {"clearance": 0.127, "name": "ISOLATION", "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 1,
         "schematic_color": "rgba(0, 0, 0, 0.000)", "track_width": 0.25, "via_diameter": 0.5, "via_drill": 0.3},
        {"clearance": 0.127, "name": "POWER", "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 2,
         "schematic_color": "rgba(0, 0, 0, 0.000)", "track_width": 0.4, "via_diameter": 0.6, "via_drill": 0.3},
    ]
    d["net_settings"]["classes"] = classes
    patterns = []
    for n in ("ETHB_TXP", "ETHB_TXN", "ETHB_RXP", "ETHB_RXN",
              "ETHB_LINE_TXP", "ETHB_LINE_TXN", "ETHB_LINE_RXP", "ETHB_LINE_RXN"):
        patterns.append({"netclass": "DIFF_PAIR", "pattern": n})
    for n in ("GND2_*", "VCC2_*", "CAN_B_H*", "CAN_B_L*", "RS485_B_A*", "RS485_B_B*"):
        patterns.append({"netclass": "ISOLATION", "pattern": n})
    for n in ("+5V*", "+3V3", "+3V3_RF", "GND", "PGND"):
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
    ds["rule_severities"]["lib_footprint_mismatch"] = "ignore"
    ds["rule_severities"]["lib_footprint_issues"] = "ignore"
    pro_path.write_text(json.dumps(d, indent=2) + "\n")


DRU_TEXT = """(version 1)
# TACCO Rev S2 custom DRC rules — generated by gen_tacco_pcb.py (CC BY 4.0)
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
    tb.SetTitle("XO — Comms / Logging / Payload Cape")
    tb.SetDate("2026-09-20")
    tb.SetRevision("S2")
    tb.SetCompany("Griffing Technology LLC")
    tb.SetComment(0, "PocketBeagle 2 Industrial cape, 55 x 35 mm, 6-layer; generated by gen_tacco_pcb.py")
    tb.SetComment(1, "Author: Claude Sonnet 5 (2026-09-20); owner sgriffing; CC BY 4.0")

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
            if f1.IsFlipped() == f2.IsFlipped() and courtyard(f1).hits(courtyard(f2)):
                print(f"  FIXED COLLISION {f1.GetReference()} x {f2.GetReference()}")
    for f1 in fixed_fps:
        c = courtyard(f1)
        if c.x1 < X0 + 0.3 or c.y1 < Y0 + 0.3 or c.x2 > X0 + BW - 0.3 or c.y2 > Y0 + BH - 0.3:
            print(f"  FIXED OFF-BOARD {f1.GetReference()} {c.x1-X0:.2f},{c.y1-Y0:.2f}..{c.x2-X0:.2f},{c.y2-Y0:.2f}")

    def area(fp):
        r = courtyard(fp)
        return (r.x2 - r.x1) * (r.y2 - r.y1)

    todo = [r for r in fps if r not in FIXED]
    todo.sort(key=lambda r: -area(fps[r]))
    unplaced = []
    for ref in todo:
        fp = fps[ref]
        my_nets = {pad.GetNetname() for pad in fp.Pads() if pad.GetNetname()}
        sig = [n for n in my_nets if n not in POWER_NETS]
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
        for item in (fp.Reference(), fp.Value()):
            item.SetTextSize(pcbnew.VECTOR2I(mm(0.6), mm(0.6)))
            item.SetTextThickness(mm(0.1))
        fp.Value().SetVisible(False)

    for ref, fp in fps.items():
        r = fp.Reference()
        r.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8)))
        r.SetTextThickness(mm(0.12))
        r.SetLayer(pcbnew.B_Fab if fp.IsFlipped() else pcbnew.F_Fab)
        r.SetVisible(True)
        fp.Value().SetVisible(False)

    gnd, g2c, g2r, p3v3 = netmap["GND"], netmap["GND2_CANB"], netmap["GND2_RS485B"], netmap["+3V3"]
    for layer, net, name in ((pcbnew.In1_Cu, gnd, "GND plane"), (pcbnew.In4_Cu, p3v3, "+3V3 plane")):
        add_zone(board, net, layer, MAIN_PLANE, priority=0, name=name)
    add_zone(board, g2c, pcbnew.In1_Cu, ISO_CAN, priority=1, name="GND2_CANB island")
    add_zone(board, g2r, pcbnew.In1_Cu, ISO_485, priority=1, name="GND2_RS485B island")
    band = [(5.0, 22.5), (34.1, 22.5), (34.1, 30.2), (5.0, 30.2)]
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
    z = pcbnew.ZONE(board)
    z.SetLayerSet(pcbnew.LSET.AllCuMask(6))
    z.SetIsRuleArea(True)
    z.SetDoNotAllowCopperPour(False)
    z.SetDoNotAllowTracks(False)
    z.SetDoNotAllowVias(False)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    z.SetZoneName("ISO_BAND")
    ol = z.Outline()
    ol.NewOutline()
    for u, v in band:
        ol.Append(mm(X0 + u), mm(Y0 + v))
    board.Add(z)

    text(board, "XO Rev S2  Griffing Technology LLC  CC BY 4.0", 27.5, 16.5, pcbnew.B_Fab, 0.9, mirror=True)
    text(board, "ISOLATED CAN-FD | RS-485", 16.0, 30.9, pcbnew.F_Fab, 0.8)

    pcbnew.SaveBoard(str(OUT), board)
    patch_project_netclasses(KICADS / "XO.kicad_pro")
    write_dru(DRU)
    print(f"wrote {OUT}: {len(fps)} footprints, {len(nets)} nets; unplaced: {unplaced}")


if __name__ == "__main__":
    main()
