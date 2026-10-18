#!/usr/bin/env python3
"""refloorplan_pilot.py — ISOW §13.1 re-floorplan of the Pilot cape (2026-10-12).

Usage:
    python3 refloorplan_pilot.py <in.kicad_pcb> <out.kicad_pcb> [--png map.png]

Owner decision 2026-10-12 (S. Griffing / Stab-Rabbit-coding): TI ISOW1044 SLLSFF7A §13.1
p. 36 [REF-SENSOR-009] and ISOW1412 SLLSF86C §13.1 p. 41 [REF-SENSOR-010] are binding:

1. 10 nF 0402 within 1 mm of VDD and of VISOOUT;
2. >= 10 uF bulk after it, 2-4 mm away;
4. BLM15EX331SN1 beads VISOOUT->VISOIN and GND2(11)->GISOIN [REF-SENSOR-043];
5. "no metal traces or ground pour within 4 mm of" VISOOUT (12) and GND2 (11).

This board reads item 5 as every copper layer, measured pad edge to metal edge.  The
4 mm "bubbles" only fit between the B.Cu PB2 rail pads (inner rows end y 96.61 / 113.39),
so both isolators turn to 180 deg (isolated column west, pins 11/12 at the top) and sit
side by side; GNSS left the cape for that room (schematic 3f55d588).

Stages, all on a copy (the input board is never modified):

* strip   — every track / via / arc is removed (the layout is re-routed afterwards);
            with ``--keep-copper`` (owner choice 2026-10-17: keep the manual routing that
            the re-floorplan does not invalidate) nothing is stripped here; the copper the
            moves orphan or make illegal is removed afterwards by ``cleanup_pilot_copper.py``
            and ``repair_pilot_routing.py``;
* sync    — footprints and pad nets follow ``kicads/Pilot.net`` (parts removed, re-
            footprinted or added; new parts load BEFORE any Remove because pcbnew 9.0.2
            segfaults on FootprintLoad after Remove, PCBNEW_SWIG_BUG.md);
* fixed   — ``FIXED`` poses: the isolators, every §13.1 cap / bead, the isolated bus parts
            and the VDD / VIO caps, placed by hand from the datasheet rules above;
* auto    — every other part whose courtyard or pads now break a rule is re-placed by a
            spiral search from its net anchor (B.Cu first), refusing courtyard overlap,
            bubble intrusion, the isolated domains and the PB2-I height budget;
* report  — remaining problems, one per line; exit 1 if any remain.

Coordinates are KiCad board millimetres (y down).

Author: Claude Opus 5.5, 2026-10-12.  Owner: sgriffing.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
from __future__ import annotations

import argparse
import math
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import pcbnew  # type: ignore

HERE = Path(__file__).resolve().parent
NETLIST = HERE.parent / "kicads" / "Pilot.net"
SYSLIB = Path("/usr/share/kicad/footprints")
CUSTOM = HERE.parents[1] / "Serenity-Custom.pretty"
S = 1e6

Rect = Tuple[float, float, float, float]          # x1, y1, x2, y2

BUBBLE = 4.0                                       # §13.1 item 5
ISO_OWN = {"CAN-TR": {"GND2_CAN_DCDC", "VCC2_CAN_DCDC"},
           "RS485": {"GND2_RS485_DCDC", "VCC2_RS485_DCDC"}}
CROSS = 0.5                                        # Pilot.kicad_dru iso_cross_domain_clearance

# Isolated domains per side.  "F" rects also hold on In1-In4; B.Cu carries only the upper
# part (the PB2 P2 rail pads below y 113.39 are logic copper).
DOMAINS: Dict[str, Dict[str, List[Rect]]] = {
    # above the isolator bodies (y < 100.4) only the bulk-cap corner is isolated, so the
    # logic VDD caps can sit beside it; J-PWM's courtyard ends at y 97.5
    "CAN": {"F": [(126.3, 98.0, 132.6, 100.4), (126.3, 100.4, 135.1, 113.7),
                  (126.3, 113.7, 142.1, 114.5), (126.3, 114.5, 144.0, 118.45),
                  (126.3, 118.45, 139.9, 122.2)],
            # B.Cu holds only the bulk cap and beads, so it stops short of the 1553 QFN
            "B": [(126.3, 98.0, 132.6, 104.0), (126.3, 104.0, 133.0, 108.6)]},
    "RS485": {"F": [(142.6, 98.0, 148.0, 100.4), (142.6, 100.4, 150.5, 114.5),
                    (144.5, 114.5, 155.9, 118.95), (140.4, 118.95, 155.9, 122.2)],
              "B": [(142.6, 98.0, 148.0, 100.4), (142.6, 100.4, 150.5, 108.6)]},
}
ISO_NET = re.compile(r"^(GND2_|VCC2_|CAN_H|CAN_L|RS485_A|RS485_B)")
# X2Y GND<->GND2 bridges straddle a domain edge on purpose (Pilot.md "Isolation")
STRADDLE = {"X2Y-CAN", "X2Y-RS485"}

# Hand placement: ref -> (x, y, rot, side).  Pin geometry at rot 180, centre (cx, cy):
# isolated pin k (11..20) at (cx - 4.65, cy - 5.715 + (k - 11) * 1.27), logic pin k (1..10)
# at (cx + 4.65, cy + 5.715 - (k - 1) * 1.27); SOIC-20W pads 1.95 x 0.6 mm.
CAN_C = (135.1, 107.1)        # pin 11 x 130.45: PWR-IN THT pads end x 125.35 (+4 mm)
RS_C = (150.5, 107.1)         # pin 11 pad 4 mm clear of CAN-TR logic pads; T-ETH2 at 156.6
FIXED: Dict[str, Tuple[float, float, float, str]] = {
    # PB2-I rails at their established poses; their library pads were mirrored on
    # 2026-10-17 (pin 1 rows per the official drawing), so sync() reloads them
    "PB2-P1": (148.5, 92.3, 0, "B"),
    "PB2-P2": (148.5, 117.7, 0, "B"),
    "CAN-TR": (CAN_C[0], CAN_C[1], 180, "F"),
    "RS485": (RS_C[0], RS_C[1], 180, "F"),
    # --- CAN, isolated side (west) ---
    "C-CAN4": (128.75, 102.02, 90, "F"),      # 10 nF across pins 11/12, 0.47 mm from the toes
    "C-CAN5": (127.3, 102.0, 90, "B"),        # 10 uF bulk, ~2 mm west of the pins
    "FB-CAN-G": (128.85, 107.0, 270, "B"),    # GND2_DCDC pad up, GND2_CAN pad >= 4 mm away
    "FB-CAN-V": (127.4, 107.0, 270, "B"),
    "C-CAN6": (128.75, 110.6, 90, "F"),       # VISOIN (pin 20) bypass
    "CMC-CAN": (128.3, 114.0, 90, "F"),       # CANH/L pins 19/18 -> connector
    "X2Y-CAN": (126.9, 111.35, 90, "B"),      # GND (PWR-IN pins 3/4) <-> GND2_CAN, west edge; clears PB2-P2
    "TVS-CAN": (142.0, 116.8, 90, "F"),
    "CAN-FD": (134.4, 118.8, 0, "F"),
    "R-CANT": (128.0, 121.0, 0, "F"),      # clear of the P2 clip NPTH
    # --- CAN, logic side (east) ---
    "C-CAN1": (139.75, 100.45, 0, "F"),       # VDD 10 nF just north of pin 10, < 1 mm
    "C-CAN2": (137.2, 98.75, 0, "F"),        # VDD 10 uF bulk, 2-4 mm, 4 mm off the bubble
    "C-CAN3": (141.4, 112.15, 90, "F"),       # VIO (pin 1) bypass
    # --- logic parts placed by hand ---
    "PWR-IN": (124.6, 105.7, 270, "F"),       # power entry stays put (harness interface)
    # HI-6138 QFN-48 on B under CAN-TR's logic half: pads x 134.0-140.8 are 4 mm clear of
    # both bubbles, y 106.2-113.0 sits above the P2 rail pads (113.39)
    "1553-XCVR": (137.4, 109.55, 90, "B"),   # courtyard 0.005 mm clear of the PB2-P2 rail
    # its 10 uF VCCP bulk (695 mA transmit bursts, DS6138 sec 24.3) on the east edge next
    # to VCCP pins 41 / 44, pad 1 (+3V3) beside pin 44; below the RS485 B domain
    "C-1553C": (142.1, 111.3, 270, "B"),
    # 3V3 module (TPSM828224SILR since 2026-10-17, inductor inside [REF-PWR-008]) in the
    # B.Cu pocket above it; its CIN / COUT follow on the same layer (SLVSEP0F sec 11.1)
    "U-3V3": (138.0, 100.6, 0, "B"),
    # CIN across VIN (pins 1/2) and GND (9/10) on the module's south side, COUT from VOUT
    # (5-8) to GND on its east side, second COUT north; courtyards just clear the
    # module's, O1 kept 0.3 mm off the RS485 bubble (SLVSEP0F sec 11.1 [REF-PWR-008])
    "C-3V3-IN": (138.0, 103.0, 0, "B"),
    "C-3V3-O1": (140.13, 100.6, 270, "B"),
    "C-3V3-O2": (138.0, 98.2, 0, "B"),
    # --- RS-485, isolated side (west) ---
    "C-485-4": (144.15, 102.02, 90, "F"),
    "C-485-5": (145.85, 98.9, 0, "B"),        # bulk north of pin 11, ~2 mm
    "FB-485-G": (143.6, 107.0, 270, "B"),
    "FB-485-V": (145.0, 107.0, 270, "B"),
    "C-485-6": (144.15, 107.9, 90, "F"),      # VISOIN (pin 16) bypass
    "CMC-RS485": (143.7, 111.3, 90, "F"),     # A/B pins 17-20
    "X2Y-RS485": (148.0, 108.6, 0, "B"),      # straddles the B domain's south edge
    "TVS-RS485": (142.0, 120.6, 90, "F"),
    "RS-485": (149.2, 118.6, 0, "F"),
    # --- RS-485, logic side (east) ---
    "C-485-1": (155.15, 100.45, 0, "F"),
    "C-485-2": (152.0, 98.75, 0, "F"),
    "C-485-3": (155.15, 99.25, 0, "F"),       # VIO bypass (pins 1/8 +3V3, joined under the body)
}

# B.Cu height budget under the PocketBeagle 2 Industrial (gen_pilot_pcb.py PB2_OBSTRUCTIONS)
X0, Y0 = 121.0, 87.5
PB2_GAP, H_MARGIN = 3.0 + 2.54, 0.5
OBSTRUCTIONS = [(4.0, 10.5, 18.0, 24.5, 1.0), (45.0, 12.5, 55.0, 22.5, 2.95)]
HEIGHT = {"T-ETH": 8.9, "T-ETH2": 8.9, "1553-XFM": 4.70, "TVS-1553P": 2.44, "TVS-1553N": 2.44}
F_ONLY = {"T-ETH", "T-ETH2", "J-GPS", "J-SPI"}     # tall, or cable connectors (B faces the PB2-I)
# footprints whose library geometry changed under the same name: always reloaded
FORCE_RELOAD = {"PB2-P1", "PB2-P2"}
EDGE_CONN = {"J-GPS", "J-SPI"}                    # GH cable connectors: board edge, F side
EDGE = (121.3, 87.8, 175.7, 122.2)                 # 0.3 mm copper-edge rule
CORNERS = [(124.0, 90.5), (173.0, 90.5), (124.0, 119.5), (173.0, 119.5)]   # R3 arc centres
FIRST = {"X-50M"}                                  # re-placed before everything else
MOUNT_KO = 2.75                                    # M2.5 standoff radius keep-out (mm)
POWER = {"GND", "PGND", "+3V3", "+5V", "+5V_IN", "+3V3_PB2", ""}
# pure-supply parts -> the part they serve (anchor)
PARENT = [("C-P1-", "ETH1-PHY"), ("R-P1-", "ETH1-PHY"), ("C-U2-", "ETH2-USB"),
          ("ESD-GPS", "J-GPS"), ("F-GPS", "J-GPS"), ("C-GPS5", "J-GPS"), ("R-I2C", "J-GPS"),
          ("ESD-S", "J-SPI"), ("F-SPI", "J-SPI"), ("C-SPI5", "J-SPI"),
          ("C-3V3", "U-3V3"), ("C-IMU", "IMU"), ("C-BARO", "BARO"),
          ("C-1553", "1553-XCVR"), ("C-50M", "X-50M"), ("C-IN", "PWR-IN"), ("FB1", "PWR-IN"),
          ("R-PGND", "PWR-IN")]
# the 3V3 module and its CIN / COUT share one layer, output-cap ground straight to the
# module GND pins without vias (SLVSEP0F sec 11.1 [REF-PWR-008])
SAME_LAYER_AS = {"C-3V3-IN": "U-3V3", "C-3V3-O1": "U-3V3",
                 "C-3V3-O2": "U-3V3", "C-3V3-HF": "U-3V3"}


def rhit(a: Rect, b: Rect, m: float = 0.0) -> bool:
    return not (a[2] + m <= b[0] or b[2] + m <= a[0] or a[3] + m <= b[1] or b[3] + m <= a[1])


def rdist(a: Rect, b: Rect) -> float:
    dx = max(b[0] - a[2], a[0] - b[2], 0.0)
    dy = max(b[1] - a[3], a[1] - b[3], 0.0)
    return math.hypot(dx, dy)


def in_union(r: Rect, rects: List[Rect]) -> bool:
    """True when every corner of r lies inside some rect of the union."""
    for x, y in ((r[0], r[1]), (r[2], r[1]), (r[0], r[3]), (r[2], r[3])):
        if not any(q[0] - 1e-6 <= x <= q[2] + 1e-6 and q[1] - 1e-6 <= y <= q[3] + 1e-6
                   for q in rects):
            return False
    return True


def box(bb) -> Rect:
    return (bb.GetX() / S, bb.GetY() / S, (bb.GetX() + bb.GetWidth()) / S,
            (bb.GetY() + bb.GetHeight()) / S)


# ---------------------------------------------------------------------------
# netlist (kicadsexpr) — same reader as gen_pilot_pcb.py
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


def read_netlist() -> Tuple[Dict[str, Dict[str, str]], Dict[str, List[Tuple[str, str]]]]:
    tree = sexp(NETLIST.read_text())
    comps: Dict[str, Dict[str, str]] = {}
    nets: Dict[str, List[Tuple[str, str]]] = {}
    for node in tree:
        if isinstance(node, list) and node and node[0] == "components":
            for c in node[1:]:
                d = {f[0]: f[1] for f in c[1:] if f[0] in ("ref", "footprint", "value")}
                comps[d["ref"]] = d
        if isinstance(node, list) and node and node[0] == "nets":
            for n in node[1:]:
                name = next(f[1] for f in n[1:] if f[0] == "name")
                nets[name] = [(next(g[1] for g in f[1:] if g[0] == "ref"),
                               next(g[1] for g in f[1:] if g[0] == "pin"))
                              for f in n[1:] if f[0] == "node"]
    return comps, nets


# ---------------------------------------------------------------------------
def strip(text: str) -> str:
    out = re.sub(r"^\t\((segment|arc|via)(?: \w+)?\n.*?^\t\)\n", "", text, flags=re.S | re.M)
    if re.search(r"^\t\((segment|arc|via)\b", out, re.M):
        raise SystemExit("strip left routed items behind (file format changed?)")
    return out


def sync(b: pcbnew.BOARD) -> List[str]:
    comps, nets = read_netlist()
    have = {f.GetReference(): f for f in b.GetFootprints()}
    new = {}
    for ref, c in comps.items():
        f = have.get(ref)
        if f is not None and f.GetFPIDAsString() == c["footprint"] and ref not in FORCE_RELOAD:
            continue
        lib, name = c["footprint"].split(":", 1)
        path = CUSTOM if lib == "Serenity-Custom" else SYSLIB / f"{lib}.pretty"
        fp = pcbnew.FootprintLoad(str(path), name)
        if fp is None:
            raise SystemExit(f"footprint not found: {c['footprint']}")
        fp.SetFPID(pcbnew.LIB_ID(lib, name))
        fp.SetReference(ref)
        fp.SetValue(c["value"])
        new[ref] = fp
    log = []
    poses = {r: (f.GetPosition().x, f.GetPosition().y, f.GetOrientationDegrees(), f.IsFlipped())
             for r, f in have.items() if r in new}
    for ref, f in have.items():
        if ref not in comps or ref in new:
            b.Remove(f)
            log.append(f"removed {ref}" if ref not in comps else f"re-footprinted {ref}")
    for ref, fp in new.items():
        b.Add(fp)
        old = poses.get(ref)
        if old is None:
            fp.SetPosition(pcbnew.VECTOR2I(int(150 * S), int(80 * S)))   # parked until placed
            log.append(f"added {ref}")
        else:
            # a re-footprinted part keeps its pose, so the baseline rule check (and every
            # part that was legal beside it) still sees it where it was
            x, y, rot, flipped = old
            if flipped:
                fp.Flip(fp.GetPosition(), True)
            fp.SetPosition(pcbnew.VECTOR2I(x, y))
            fp.SetOrientationDegrees(rot)
    pin_net = {(r, p): n for n, nodes in nets.items() for r, p in nodes}
    for n in nets:
        if b.FindNet(n) is None:
            b.Add(pcbnew.NETINFO_ITEM(b, n))
    for pad in b.GetPads():
        n = pin_net.get((pad.GetParentFootprint().GetReference(), pad.GetNumber()))
        if n is None:
            pad.SetNetCode(0)
        else:
            pad.SetNet(b.FindNet(n))
    return log


def pose(f: pcbnew.FOOTPRINT, x: float, y: float, rot: float, side: str) -> None:
    if (side == "B") != f.IsFlipped():
        f.Flip(f.GetPosition(), True)
    f.SetPosition(pcbnew.VECTOR2I(int(round(x * S)), int(round(y * S))))
    f.SetOrientationDegrees(rot)


class Geo:
    """Courtyard + pad rectangles of a footprint in its current pose."""

    def __init__(self, f: pcbnew.FOOTPRINT):
        self.ref = f.GetReference()
        self.side = "B" if f.IsFlipped() else "F"
        f.BuildCourtyardCaches()
        c = f.GetCourtyard(pcbnew.B_CrtYd if self.side == "B" else pcbnew.F_CrtYd)
        self.cy = box(c.BBox()) if c.OutlineCount() else box(f.GetBoundingBox(False, False))
        self.pads = []
        for p in f.Pads():
            th = p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)
            npth = p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH
            self.pads.append((p.GetNumber(), p.GetNetname(), "FB" if th else self.side, npth,
                              box(p.GetBoundingBox())))


def shapes(f: pcbnew.FOOTPRINT, side: str) -> Dict[int, Geo]:
    """Geometry at each rotation with the footprint at the origin."""
    out = {}
    for rot in (0, 90, 180, 270):
        pose(f, 0.0, 0.0, rot, side)
        out[rot] = Geo(f)
    return out


def shift(g: Geo, dx: float, dy: float) -> Geo:
    h = Geo.__new__(Geo)
    h.ref, h.side = g.ref, g.side
    h.cy = (g.cy[0] + dx, g.cy[1] + dy, g.cy[2] + dx, g.cy[3] + dy)
    h.pads = [(n, net, s, np_, (r[0] + dx, r[1] + dy, r[2] + dx, r[3] + dy))
              for n, net, s, np_, r in g.pads]
    return h


class Checker:
    def __init__(self, geos: Dict[str, Geo], bubbles: bool = True):
        self.geos = geos
        self.domains = bubbles
        self._bubbles = {iso: [r for n, _, _, _, r in geos[iso].pads if n in ("11", "12")]
                         for iso in ISO_OWN} if bubbles else {}

    def bubble_src(self):
        return self._bubbles

    def ok(self, g: Geo, skip: set) -> bool:
        """Fast yes/no form of problems() for the site search (cheapest tests first)."""
        c = g.cy
        if c[0] < EDGE[0] or c[1] < EDGE[1] or c[2] > EDGE[2] or c[3] > EDGE[3]:
            return False
        for o in self.geos.values():
            if o.side == g.side and o.ref != g.ref and o.ref not in skip and rhit(c, o.cy):
                if not o.ref.startswith("H"):
                    return False
        return not self.problems(g, skip)

    def problems(self, g: Geo, skip: set) -> List[str]:
        """Rule breaks of one part against everything else (refs in skip ignored)."""
        out = []
        c = g.cy
        if not g.ref.startswith(("H", "PB2")):
            if c[0] < EDGE[0] or c[1] < EDGE[1] or c[2] > EDGE[2] or c[3] > EDGE[3]:
                if not g.ref.startswith(("ETH", "CAN-FD", "RS-485", "MIL", "PWR", "J-GPS", "J-SPI")):
                    out.append("edge")
            # cable connectors must reach the board edge (courtyard within 0.6 mm of it)
            if g.ref in EDGE_CONN and min(c[0] - 121.0, c[1] - 87.5, 176.0 - c[2], 122.5 - c[3]) > 0.6:
                out.append("not at edge")
            for cx, cy_ in CORNERS:
                px = min(max(cx, c[0]), c[2])
                py = min(max(cy_, c[1]), c[3])
                if (px < 124.0 or px > 173.0) and (py < 90.5 or py > 119.5):
                    if math.hypot(px - cx, py - cy_) > 3.0 - 0.3 + 1e-6:
                        out.append("corner arc")
            # M2.5 screw head / standoff: no pad within 2.75 mm of a mounting-hole centre
            # on either face (pcb-routing-best-practices skill sec 1.B "Sacred Mechanical
            # Keepouts"; the holes sit on the R3 corner centres)
            for hx, hy in CORNERS:
                if any(rdist(r, (hx, hy, hx, hy)) < MOUNT_KO for *_, r in g.pads):
                    out.append("mounting-hole keep-out")
                    break
        if g.side == "B":
            h = HEIGHT.get(g.ref, 2.0)
            if g.ref in F_ONLY or h > PB2_GAP - H_MARGIN:
                out.append("too tall for B")
            for u0, v0, u1, v1, oh in OBSTRUCTIONS:
                if rhit(c, (X0 + u0, Y0 + v0, X0 + u1, Y0 + v1)) and h > PB2_GAP - oh - H_MARGIN:
                    out.append("PB2-I obstruction")
        for o in self.geos.values():
            if o.ref == g.ref or o.ref in skip or o.side != g.side:
                continue
            if o.ref.startswith("H") and not g.ref.startswith("H"):
                continue
            if rhit(c, o.cy):
                pair = {g.ref, o.ref}
                if pair & set(ISO_OWN) and pair <= set(FIXED):
                    # §13.1 caps sit inside the SOIC courtyard by design (< 1 mm from the
                    # pins): require 0.2 mm pad-to-pad instead
                    if any(rdist(a[4], b_[4]) < 0.2 for a in g.pads for b_ in o.pads
                           if a[2] == b_[2] or "FB" in (a[2], b_[2])):
                        out.append(f"pads touch {o.ref}")
                    continue
                out.append(f"courtyard x {o.ref}")
        # THT / mounting-hole pads of other parts block both faces
        for o in self.geos.values():
            if o.ref == g.ref or o.ref in skip or o.side == g.side:
                continue
            for _, _, s, _, r in o.pads:
                if s == "FB" and rhit(c, r, 0.2):
                    out.append(f"THT pad of {o.ref}")
                    break
        # §13.1 bubbles: no foreign metal within 4 mm of pins 11/12 (all layers)
        for iso, src in self.bubble_src().items():
            if g.ref == iso:
                continue
            for n, net, _, npth, r in g.pads:
                if npth or net in ISO_OWN[iso]:
                    continue
                if min(rdist(r, s) for s in src) < BUBBLE - 1e-6:
                    out.append(f"bubble {iso} ({n} {net or 'NC'})")
                    break
        # domains, judged on pads: an isolated pad lies inside its own domain and >= 0.5 mm
        # from the other one; a logic pad stays >= 0.5 mm from both (PGND / NC are free)
        if self.domains and g.ref not in STRADDLE:
            for _, net, side, _, r in g.pads:
                if not net or net == "PGND":
                    continue
                own = None
                if ISO_NET.match(net):
                    own = "CAN" if "CAN" in net else "RS485"
                for dom, sides in DOMAINS.items():
                    rects = sides["F"] if "F" in side else []
                    rects = rects + (sides["B"] if "B" in side else [])
                    if dom == own:
                        if not in_union(r, rects):
                            out.append(f"iso pad outside {dom}")
                            break
                    elif any(rhit(r, q, CROSS) for q in rects):
                        out.append(f"pad in {dom} domain")
                        break
        return out


def anchor(ref: str, nets_of: Dict[str, set], placed: set,
           geos: Dict[str, Geo]) -> Tuple[float, float]:
    """Mean position of the placed pads that share a signal net with ``ref``."""
    pts = []
    for net in nets_of.get(ref, ()):
        if net in POWER:
            continue
        for r, g in geos.items():
            if r == ref or r not in placed:
                continue
            for _, n, _, _, q in g.pads:
                if n == net:
                    pts.append(((q[0] + q[2]) / 2, (q[1] + q[3]) / 2))
    if not pts:
        par = next((t for pre, t in PARENT if ref.startswith(pre)), None)
        if par and par in placed:
            g = geos[par]
            return ((g.cy[0] + g.cy[2]) / 2, (g.cy[1] + g.cy[3]) / 2)
        g = geos[ref]
        return ((g.cy[0] + g.cy[2]) / 2, (g.cy[1] + g.cy[3]) / 2)
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("inp")
    ap.add_argument("out")
    ap.add_argument("--png")
    ap.add_argument("--rmax", type=float, default=20.0)
    ap.add_argument("--keep-copper", action="store_true",
                    help="keep tracks/vias (cleanup_pilot_copper.py removes the invalid ones)")
    ap.add_argument("--sync-only", action="store_true", help=argparse.SUPPRESS)
    a = ap.parse_args()

    tmp = Path(a.out).with_suffix(".synced.kicad_pcb")
    if a.sync_only:
        # strip + sync run in their own process: after Remove() the pcbnew 9.0.2 binding
        # hands back unwrapped SwigPyObjects, even for the BOARD (PCBNEW_SWIG_BUG.md)
        text = Path(a.inp).read_text()
        Path(a.out).write_text(text if a.keep_copper else strip(text))
        b = pcbnew.LoadBoard(a.out)
        for line in sync(b):
            print("sync:", line)
        pcbnew.SaveBoard(a.out, b)
        return
    subprocess.run([sys.executable, __file__, "--sync-only"]
                   + (["--keep-copper"] if a.keep_copper else []) + [a.inp, str(tmp)], check=True)
    b = pcbnew.LoadBoard(str(tmp))
    tmp.unlink()
    fps = {f.GetReference(): f for f in b.GetFootprints()}
    # parts parked off-board by sync() (y 80 mm) have no baseline
    base_geos = {r: Geo(f) for r, f in fps.items() if f.GetPosition().y > 87 * S}
    chk_base = Checker({r: Geo(f) for r, f in fps.items()}, bubbles=False)
    for ref, (x, y, rot, side) in FIXED.items():
        pose(fps[ref], x, y, rot, side)
    geos = {r: Geo(f) for r, f in fps.items()}
    chk = Checker(geos)
    nets_of: Dict[str, set] = {}
    for p in b.GetPads():
        nets_of.setdefault(p.GetParentFootprint().GetReference(), set()).add(p.GetNetname())

    # parts that break a rule where they stand (or were parked) get re-placed
    # what the committed board already tolerates (e.g. J-PWM's courtyard over the PB2-P1
    # clip hole) is not this script's business: record it, move only for new breaks
    # a problem the old board already had is tolerated only while the part it involves
    # stayed put: R-BS1R overlapped RS485's courtyard before, and RS485's new FIXED pose
    # put its pads onto R-BS1R's (2026-10-17, a short on the first keep-copper run)
    moved_fixed = {r for r in FIXED if r in base_geos and
                   math.dist(((base_geos[r].cy[0] + base_geos[r].cy[2]) / 2,
                              (base_geos[r].cy[1] + base_geos[r].cy[3]) / 2),
                             ((geos[r].cy[0] + geos[r].cy[2]) / 2,
                              (geos[r].cy[1] + geos[r].cy[3]) / 2)) > 0.5}
    base = {r: {q for q in chk_base.problems(g, set())
                if not any(q.endswith(" " + m) or f" {m} " in q for m in moved_fixed)}
            for r, g in base_geos.items()}
    movable = []
    for ref, g in geos.items():
        if ref in FIXED or ref.startswith(("H", "PB2")):
            continue
        if set(chk.problems(g, set())) - base.get(ref, set()):
            movable.append(ref)
    for ref, pre in SAME_LAYER_AS.items():
        if pre in movable and ref not in movable:
            movable.append(ref)
    # a supply part follows its parent: when the parent moves (re-placed, or a FIXED pose
    # away from where it stood) its bypass caps are re-placed next to it, or they would
    # be left decoupling nothing (2026-10-17: the HI-6138 moved ~13 mm, C-1553A/B/D did not)
    def centre(g: Geo) -> Tuple[float, float]:
        return ((g.cy[0] + g.cy[2]) / 2, (g.cy[1] + g.cy[3]) / 2)
    moved = set(movable) | {r for r in FIXED if r in base_geos and r in geos and
                            math.dist(centre(base_geos[r]), centre(geos[r])) > 0.5}
    for ref in geos:
        par = next((t for pre, t in PARENT if ref.startswith(pre)), None)
        if par in moved and ref not in movable and ref not in FIXED:
            movable.append(ref)
    area = {r: (geos[r].cy[2] - geos[r].cy[0]) * (geos[r].cy[3] - geos[r].cy[1]) for r in movable}
    # parents largest first (they anchor the rest); supply parts after all parents and
    # smallest first, so the HF bypass caps get the sites nearest their pins
    movable.sort(key=lambda r: (1, area[r]) if any(r.startswith(p) for p, _ in PARENT)
                 else (0, -area[r]))
    # locality-critical parts first: the 50 MHz MCLK source belongs beside the HI-6138
    # (short clock trace), the IMU / BARO have no such tie and take what is left
    movable.sort(key=lambda r: 0 if r in FIRST else 1)
    print(f"re-placing {len(movable)}: {' '.join(movable)}")
    placed = set(geos) - set(movable)
    unplaced = []
    for ref in movable:
        f = fps[ref]
        ax, ay = anchor(ref, nets_of, placed, geos)
        sides = ["B", "F"]
        if ref in SAME_LAYER_AS and SAME_LAYER_AS[ref] in placed:
            sides = [geos[SAME_LAYER_AS[ref]].side]
        if ref in F_ONLY:
            sides = ["F"]
        shp = {s: shapes(f, s) for s in sides}
        others = {q for q in movable if q not in placed}
        done = False
        r = 0.0
        step = 0.25
        while r <= a.rmax and not done:
            n = 1 if r == 0 else max(8, int(2 * math.pi * r / step))
            for k in range(n):
                cx = ax + r * math.cos(2 * math.pi * k / n)
                cy = ay + r * math.sin(2 * math.pi * k / n)
                for s in sides:
                    for rot, g0 in shp[s].items():
                        g = shift(g0, cx, cy)
                        if chk.ok(g, others):
                            pose(f, cx, cy, rot, s)
                            geos[ref] = Geo(f)
                            placed.add(ref)
                            done = True
                            break
                    if done:
                        break
                if done:
                    break
            r += step
        if not done:
            unplaced.append(ref)
            print(f"  {ref}: NO legal site within {a.rmax} mm of ({ax:.1f}, {ay:.1f})")
        else:
            g = geos[ref]
            print(f"  {ref}: {g.side} ({(g.cy[0] + g.cy[2]) / 2:.2f}, {(g.cy[1] + g.cy[3]) / 2:.2f})"
                  f"  {math.hypot((g.cy[0] + g.cy[2]) / 2 - ax, (g.cy[1] + g.cy[3]) / 2 - ay):.1f} mm"
                  " from anchor")
    pcbnew.SaveBoard(a.out, b)

    left = []
    for ref, g in geos.items():
        if ref.startswith(("H", "PB2")):
            continue
        for p in set(chk.problems(g, set(unplaced))) - base.get(ref, set()):
            left.append(f"{ref}: {p}")
    print("\n".join(sorted(set(left))) or "no problems")
    print(f"{len(set(left))} problem(s), {len(unplaced)} unplaced")
    if a.png:
        plot(geos, chk, a.png)
    sys.exit(1 if left or unplaced else 0)


def plot(geos: Dict[str, Geo], chk: Checker, png: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Rectangle
    fig, axs = plt.subplots(2, 1, figsize=(16, 21))
    for ax, side in zip(axs, "FB"):
        ax.add_patch(Rectangle((121, 87.5), 55, 35, fill=False, lw=2))
        for dom, sides in DOMAINS.items():
            for r in sides["F" if side == "F" else "B"]:
                ax.add_patch(Rectangle((r[0], r[1]), r[2] - r[0], r[3] - r[1], fc="gold",
                                       alpha=0.15, ec="none"))
        for g in geos.values():
            if g.side != side and not g.ref.startswith(("H", "PB2")):
                continue
            c = g.cy
            col = "tab:red" if g.ref in ISO_OWN else "tab:blue"
            ax.add_patch(Rectangle((c[0], c[1]), c[2] - c[0], c[3] - c[1], fill=False, ec=col, lw=0.8))
            ax.text((c[0] + c[2]) / 2, (c[1] + c[3]) / 2, g.ref, fontsize=5, ha="center", va="center")
            for _, _, s, _, r in g.pads:
                if side in s:
                    ax.add_patch(Rectangle((r[0], r[1]), r[2] - r[0], r[3] - r[1], fc="k", alpha=0.35))
        for iso, src in chk.bubble_src().items():
            x0 = min(s[0] for s in src)
            y0 = min(s[1] for s in src)
            x1 = max(s[2] for s in src)
            y1 = max(s[3] for s in src)
            ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle=f"round,pad={BUBBLE}",
                                        fill=False, ec="r", ls="--"))
        ax.set_xlim(120, 177)
        ax.set_ylim(123, 86.5)
        ax.set_aspect("equal")
        ax.set_xticks(range(121, 177, 2))
        ax.set_yticks(range(88, 123, 2))
        ax.grid(lw=0.2)
        ax.set_title(f"{side} side (gold = isolated domains, red dashed = §13.1 4 mm bubbles)")
    plt.tight_layout()
    plt.savefig(png, dpi=80)


if __name__ == "__main__":
    main()
