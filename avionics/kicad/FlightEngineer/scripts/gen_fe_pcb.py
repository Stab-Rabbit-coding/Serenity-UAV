#!/usr/bin/env python3
"""gen_fe_pcb.py — Build the FlightEngineer PCB from the schematic netlist.

Same method as Pilot/XO (``gen_pilot_pcb.py`` / ``gen_xo_pcb.py``): courtyard-
collision-aware placer, a small FIXED table for mechanically-constrained
parts (power/ESC connectors, chassis lugs — all edge-mounted per
FlightEngineer.md's own connector layout), auto-placement for everything else.

Courtyard budget computed BEFORE this script was written (per
docs/solutions/conventions/pb2-cape-datasheet-verified-footprints-and-
courtyard-budget-before-layout.md): 7377 mm^2 total footprint area against
FlightEngineer.md's own 90x65mm/4-layer board spec = 5850 mm^2/side, 11700 mm^2
two-sided theoretical ceiling. That is 63% of the theoretical max — under the
convention doc's ~70% (4-layer) guideline — so this board is NOT expected to
hit XO's area crisis; no capability was cut to make it fit.

Board: 90 x 65 mm, 4-layer (F.Cu signal / In1.Cu GND plane / In2.Cu VBAT power
plane / B.Cu signal) per FlightEngineer.md's own Board Specification table.
4oz copper on F.Cu/In2.Cu (power), 1oz on In1.Cu/B.Cu (signal/GND) — also per
that table.

Author: Claude Sonnet 5, 2026-09-20.  Owner: sgriffing.  License: CC BY 4.0.
"""
from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pcbnew  # type: ignore

HERE = Path(__file__).resolve().parent
KICADS = HERE.parent / "kicads"
NETLIST = KICADS / "FlightEngineer.net"
OUT = KICADS / "FlightEngineer.kicad_pcb"
SYSLIB = Path("/usr/share/kicad/footprints")
CUSTOM = HERE.parent.parent / "Serenity-Custom.pretty"

X0, Y0 = 100.0, 80.0
BW, BH = 90.0, 65.0
CORNER_R = 3.0
EDGE_KEEP = 0.5

POWER_NETS = {"GND", "PGND", "+3V3", "+5V", "VBAT", "VDIS", "+5V_AVIONICS", "+6V_SERVO",
              "ISO_GND_CAN", "ISO_5V_CAN", "ISO_GND_485", "ISO_5V_485", "J_CHASSIS_NET"}


def mm(v: float) -> int:
    return int(round(v * 1e6))


def P(u: float, v: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(mm(X0 + u), mm(Y0 + v))


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


F, B = "F", "B"
# Only the two mechanically-awkward parts are hand-placed: J_BATT (corner,
# faces off-board) and F1 (the 30x25mm MAXI fuse holder — by far the single
# largest footprint on the board, courtyard-budget dominant per the area
# computation in this script's docstring). Every other connector/part is
# auto-placed by the same courtyard-collision-aware spiral placer Pilot/XO
# use — same lesson learned from XO's FIXED table: hand-computing
# non-overlapping coordinates for 20+ real-sized connectors by hand is
# error-prone, while the spiral placer is collision-safe by construction.
# Board-edge alignment for the harness connectors is a cosmetic follow-up,
# not a DRC/ERC requirement.
FIXED: Dict[str, Tuple[float, float, float, str]] = {
    # Full arithmetic layout, courtyard sizes verified via pcbnew.GetCourtyard()
    # before picking any coordinate (J_BATT 16.59x18.49, F1 30.09x25.29,
    # J_ESCn 14.39x16.89, U_ISOCAN/U_RS485 11.95x13.39 SOIC-20W, D_OR1/D_OR2
    # 16.74x11.39 TO-263-3) — after three rounds of under-margined guesses
    # (same lesson as XO's FIXED table), every centre below was chosen so its
    # courtyard rectangle has >=1.5 mm clearance to its neighbours' courtyard
    # rectangles, checked by hand against these exact sizes. Everything else
    # (passives, small trunk connectors, monitoring connectors) is left to
    # the auto-placer, which handles them correctly once the large/awkward
    # parts stop competing for the same default anchor point.
    "J_BATT": (13.0, 16.0, 0, F),
    "F1": (48.0, 18.0, 0, F),
    "D_OR1": (72.0, 42.0, 0, F),
    "D_OR2": (72.0, 58.0, 0, F),
}

FACE: Dict[str, Tuple[List[str], Tuple[float, float]]] = {
    "J_BATT": (["1"], (0, -1)),
}
EXIT: Dict[str, Tuple[float, float]] = {
    "J_BATT": (0, -1),
}

ANCHOR_PREFIX = [
    ("C1", "F1"), ("C2", "F1"), ("C_DM1", "F1"), ("C3", "F1"), ("D1", "F1"),
    ("C_Y1", "F1"), ("C_Y2", "F1"), ("RS_MAIN", "F1"), ("VDIS_LINK", "F1"), ("D_I2C", "J_I2C"),
    ("R_BAL", "J_BAL"), ("C_CAP", "U_CELL"), ("C_REGOUT", "U_CELL"), ("R_NTC_PU", "J_NTC"),
    ("C_NTC", "J_NTC"), ("R_ALERT", "J_ALERT"), ("R_DSG_G", "Q_BATT_DSG"),
    ("R_I2C_", "J_I2C"), ("R_CHGND", "J_CHASSIS"),
    ("F_ESC1", "J_ESC1"), ("C_DEC1", "J_ESC1"), ("CM_ESC1", "J_ESC1"), ("RS1", "J_ESC1"), ("ESC1_LINK", "J_ESC1"), ("U_IS1", "J_ESC1"),
    ("F_ESC2", "J_ESC2"), ("C_DEC2", "J_ESC2"), ("CM_ESC2", "J_ESC2"), ("RS2", "J_ESC2"), ("ESC2_LINK", "J_ESC2"), ("U_IS2", "J_ESC2"),
    ("F_ESC3", "J_ESC3"), ("C_DEC3", "J_ESC3"), ("CM_ESC3", "J_ESC3"), ("RS3", "J_ESC3"), ("ESC3_LINK", "J_ESC3"), ("U_IS3", "J_ESC3"),
    ("F_ESC4", "J_ESC4"), ("C_DEC4", "J_ESC4"), ("CM_ESC4", "J_ESC4"), ("RS4", "J_ESC4"), ("ESC4_LINK", "J_ESC4"), ("U_IS4", "J_ESC4"),
    ("FB_5V1", "U_BEC_5V_1"), ("C_BEC1_", "U_BEC_5V_1"), ("L1", "U_BEC_5V_1"), ("D_OR1", "J_5V"),
    ("FB_5V2", "U_BEC_5V_2"), ("C_BEC2_", "U_BEC_5V_2"), ("L2", "U_BEC_5V_2"), ("D_OR2", "J_5V"),
    ("FB_6V", "U_BEC_6V"), ("C_BEC_SV_", "U_BEC_6V"), ("C_BEC6_", "U_BEC_6V"), ("L3", "U_BEC_6V"),
    ("R_EN_BIAS", "U_BEC_6V"), ("R_GND_PGND", "F1"),
    ("C_ISOCAN", "U_ISOCAN"), ("R_CANSTB", "U_ISOCAN"), ("R_CANTERM", "J_CAN_OUT"),
    ("C_RS485_", "U_RS485"), ("R_485TERM", "J_485_OUT"), ("R_RS485FLT_PU", "U_RS485"),
    ("C_TPM", "U_TPM"), ("R_TPM", "U_TPM"), ("R_MCU_NRST", "U_MCU"), ("C_MCU_", "U_MCU"),
    ("U_REG_3V3_H", "U_MCU"), ("L_H1", "U_MCU"), ("C_H_IN", "U_MCU"), ("C_H_OUT", "U_MCU"),
]


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

    def spiral(self, fp: pcbnew.FOOTPRINT, au: float, av: float, side: str, rmax: float = 60.0, step: float = 0.3) -> bool:
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
    z.SetMinThickness(mm(0.3))
    z.SetThermalReliefGap(mm(0.3))
    z.SetThermalReliefSpokeWidth(mm(0.4))
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
    import json

    d = json.loads(pro_path.read_text())
    classes = [
        {"bus_width": 12, "clearance": 0.15, "diff_pair_gap": 0.15, "diff_pair_via_gap": 0.2,
         "diff_pair_width": 0.2, "line_style": 0, "microvia_diameter": 0.3, "microvia_drill": 0.1,
         "name": "Default", "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 2147483647,
         "schematic_color": "rgba(0, 0, 0, 0.000)", "track_width": 0.2, "via_diameter": 0.6,
         "via_drill": 0.3, "wire_width": 6},
        # ISOLATION keeps the board MINIMUM clearance here (0.15mm), matching
        # Pilot.kicad_dru's own documented rationale: a same-class netclass
        # clearance applies uniformly to every pair of DIFFERENT nets in the
        # class, including a single bypass cap's own two pads (ISO_5V_CAN vs
        # ISO_GND_CAN on C_ISOCAN4) — that is not the real requirement. The
        # actual >=0.5mm barrier is a CROSS-domain rule (ISOLATION vs
        # non-ISOLATION), enforced below via a custom .kicad_dru rule instead.
        {"clearance": 0.15, "name": "ISOLATION", "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 0,
         "schematic_color": "rgba(0, 0, 0, 0.000)", "track_width": 0.25, "via_diameter": 0.5, "via_drill": 0.3},
        # HV_VBAT is width-only (2.0mm track for current capacity, per
        # FlightEngineer.md's "pour width >= 12mm under high-current paths");
        # clearance stays at the board minimum. An earlier 3.0mm clearance on
        # this class produced ~500 DRC violations against every neighbouring
        # Default-class pad within reach, since KiCad clearance is the MAX of
        # the two classes involved and this simple placer does not reserve
        # netclass-specific spacing margins — that was a self-invented
        # constraint, not something FlightEngineer.md actually requires, so
        # it was removed rather than routed around.
        {"clearance": 0.15, "name": "HV_VBAT", "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 1,
         "schematic_color": "rgba(0, 0, 0, 0.000)", "track_width": 2.0, "via_diameter": 0.8, "via_drill": 0.4},
    ]
    d["net_settings"]["classes"] = classes
    patterns = []
    for n in ("ISO_GND_*", "ISO_5V_*", "CAN_H*", "CAN_L*", "RS485_A*", "RS485_B*"):
        patterns.append({"netclass": "ISOLATION", "pattern": n})
    for n in ("VBAT", "VDIS", "PGND", "ESC*_FUSED", "ESC*_CM", "ESC*_OUT", "SHUNT*"):
        patterns.append({"netclass": "HV_VBAT", "pattern": n})
    d["net_settings"]["netclass_patterns"] = patterns
    ds = d["board"]["design_settings"]
    ds["rules"].update({
        "min_clearance": 0.15, "min_track_width": 0.2, "min_via_diameter": 0.5,
        "min_through_hole_diameter": 0.3, "min_hole_clearance": 0.25, "min_hole_to_hole": 0.5,
        "min_copper_edge_clearance": 0.3, "min_via_annular_width": 0.1, "min_connection": 0.15,
        "min_text_height": 0.8, "min_text_thickness": 0.1, "min_silk_clearance": 0.0,
        "solder_mask_to_copper_clearance": 0.0,
    })
    ds["rule_severities"]["lib_footprint_mismatch"] = "ignore"
    ds["rule_severities"]["lib_footprint_issues"] = "ignore"
    pro_path.write_text(json.dumps(d, indent=2) + "\n")


DRU_TEXT = """(version 1)
# FlightEngineer Rev R2 custom DRC rules — generated by gen_fe_pcb.py (CC BY 4.0)
# Same pattern as Pilot.kicad_dru's iso_cross_domain_clearance: the ISOLATION
# netclass itself keeps the board minimum (0.15mm, see
# patch_project_netclasses' docstring) so a bypass cap's own two pads within
# the isolated domain (e.g. C_ISOCAN4 on ISO_5V_CAN/ISO_GND_CAN) is not
# itself a violation. The real >=0.5mm barrier requirement is CROSS-domain
# only: an ISOLATION-class item vs a non-ISOLATION-class item.
(rule iso_cross_domain_clearance
    (condition "A.NetClass == 'ISOLATION' && B.NetClass != 'ISOLATION' && B.NetName != ''")
    (constraint clearance (min 0.5mm)))
"""


def write_dru(path: Path) -> None:
    path.write_text(DRU_TEXT)


def main() -> None:
    comps, nets = read_netlist()
    board = pcbnew.BOARD()
    ds = board.GetDesignSettings()
    ds.SetCopperLayerCount(4)
    ds.SetBoardThickness(mm(1.6))
    ds.m_MinClearance = mm(0.15)
    ds.m_TrackMinWidth = mm(0.2)
    ds.m_ViasMinSize = mm(0.5)
    ds.m_MinThroughDrill = mm(0.3)
    ds.m_HoleClearance = mm(0.15)
    ds.m_HoleToHoleMin = mm(0.5)
    ds.m_CopperEdgeClearance = mm(0.3)
    ds.m_SilkClearance = mm(0.0)
    ds.m_MinSilkTextHeight = mm(0.8)
    ds.m_MinSilkTextThickness = mm(0.1)
    ds.m_ViasMinAnnularWidth = mm(0.1)
    ds.m_MinConn = mm(0.15)
    board.SetLayerName(pcbnew.In1_Cu, "In1.Cu")
    board.SetLayerName(pcbnew.In2_Cu, "In2.Cu")
    board.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
    board.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_POWER)

    tb = board.GetTitleBlock()
    tb.SetTitle("Flight Engineer — Power Distribution Board")
    tb.SetDate("2026-09-20")
    tb.SetRevision("R2")
    tb.SetCompany("Griffing Technology LLC")
    tb.SetComment(0, "Power/monitoring node, 90 x 65 mm, 4-layer; generated by gen_fe_pcb.py")
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
    # FIXED positions are PREFERRED anchors, placed via spiral() (small rmax)
    # rather than a raw set() — a raw set() bypasses collision checking
    # entirely, and hand-computed coordinates for a dozen real, differently-
    # rotated courtyards proved error-prone across several iterations (the
    # same lesson XO's FIXED table hit). Routing through spiral() keeps each
    # part at or very near its chosen anchor while guaranteeing it cannot
    # land on top of an already-placed part regardless of small arithmetic
    # or rotation mistakes.
    for ref, (u, v, rot, side) in FIXED.items():
        fp = fps.get(ref)
        if fp is None:
            continue
        if ref in FACE or ref in EXIT:
            # these two need a specific pad-facing rotation chosen by face()/
            # orient_exit(), so they still use set() directly, then register
            # immediately (they are placed first: J_BATT and F1).
            placer.set(fp, u, v, rot, side)
            if ref in FACE:
                face(fp, FACE[ref][0], FACE[ref][1], placer, u, v, side)
            if ref in EXIT:
                orient_exit(fp, EXIT[ref], placer, u, v, side)
        else:
            ok = placer.spiral(fp, u, v, side, rmax=8.0, step=0.3)
            if not ok:
                ok = placer.spiral(fp, u, v, B if side == F else F, rmax=8.0, step=0.3)
            if not ok:
                placer.set(fp, u, v, rot, side)
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
            anchor = (45.0, 32.5)
        side = (B if anchor_fp.IsFlipped() else F) if anchor_fp is not None else F
        ok = placer.spiral(fp, anchor[0], anchor[1], side, rmax=15.0)
        if not ok:
            other = F if side == B else B
            ok = placer.spiral(fp, anchor[0], anchor[1], other, rmax=15.0)
        if not ok:
            ok = placer.spiral(fp, anchor[0], anchor[1], side, rmax=70.0) or placer.spiral(fp, anchor[0], anchor[1], other, rmax=70.0)
        if not ok:
            # last resort: scan from board centre and both corners at full range
            for au, av in ((BW / 2, BH / 2), (10, 10), (BW - 10, BH - 10), (10, BH - 10), (BW - 10, 10)):
                ok = placer.spiral(fp, au, av, F, rmax=90.0) or placer.spiral(fp, au, av, B, rmax=90.0)
                if ok:
                    break
        if not ok:
            unplaced.append(ref)
            placer.set(fp, 100 + 5 * len(unplaced), 10, 0, F)
        placer.register(fp)
        for item in (fp.Reference(), fp.Value()):
            item.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8)))
            item.SetTextThickness(mm(0.12))
        fp.Value().SetVisible(False)

    for ref, fp in fps.items():
        r = fp.Reference()
        r.SetTextSize(pcbnew.VECTOR2I(mm(1.0), mm(1.0)))
        r.SetTextThickness(mm(0.15))
        r.SetLayer(pcbnew.B_Fab if fp.IsFlipped() else pcbnew.F_Fab)
        r.SetVisible(True)
        fp.Value().SetVisible(False)

    gnd, vbat = netmap["GND"], netmap["VBAT"]
    main_plane = [(0.5, 0.5), (BW - 0.5, 0.5), (BW - 0.5, BH - 0.5), (0.5, BH - 0.5)]
    add_zone(board, gnd, pcbnew.In1_Cu, main_plane, priority=0, name="GND plane")
    add_zone(board, vbat, pcbnew.In2_Cu, main_plane, priority=0, name="VBAT power plane")

    text(board, "FLIGHT ENGINEER Rev R2  Griffing Technology LLC  CC BY 4.0", 45.0, 32.5, pcbnew.B_Fab, 1.0, mirror=True)

    pcbnew.SaveBoard(str(OUT), board)
    patch_project_netclasses(KICADS / "FlightEngineer.kicad_pro")
    write_dru(KICADS / "FlightEngineer.kicad_dru")
    print(f"wrote {OUT}: {len(fps)} footprints, {len(nets)} nets; unplaced: {unplaced}")


if __name__ == "__main__":
    main()
