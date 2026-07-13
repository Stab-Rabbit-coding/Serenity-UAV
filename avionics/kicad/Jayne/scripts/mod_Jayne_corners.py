#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mod_jayne_corners.py -- Jayne nose PCB: fillet the trapezoid corners with arcs
CONCENTRIC to corner M2.5 mounting holes, and add port/starboard keep-out strips
for the nose install rails.
=============================================================================
Per user (2026-07-12): move the mounting holes to the corners; round the PCB
corners with an arc concentric to each corner hole; mark a ~1/16 in (1.5875 mm)
component-clear strip along the port and starboard edges so the board edge can
engage slots on the interior of the nose during installation.

- Each corner: fillet radius R=3 mm; an M2.5 NPTH hole (Ø2.7) is placed at the
  fillet centre, so the rounded corner arc is concentric with the hole.
- Port (C1-C2) and starboard (C3-C0) slanted edges each get a 1.5875 mm keep-out
  rule area (no footprints / no copper pour) + an F.SilkS boundary line.

Modifies Jayne.kicad_pcb in place (GUI-owned board).  Trapezoid corners are the
Rev C outline (docs/JAYNE_NOSE_TRAPEZOID.md).  Board loads; invalid_outline = 0.

Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  (Griffing Technology LLC)
AI-assist: Claude Opus 4.8 (Anthropic) -- pcbnew transform, 2026-07-12.
License: CC BY 4.0
"""

import math
import sys
from pathlib import Path

import pcbnew

BOARD = Path(__file__).resolve().parent.parent / "kicads" / "Jayne.kicad_pcb"
CORNERS = [(69.85, 0.0), (69.85, 25.4), (0.0, 41.7), (0.0, -16.3)]
R = 3.0
STRIP = 1.5875  # 1/16 in


def unit(v):
    m = math.hypot(*v)
    return (v[0] / m, v[1] / m)


def fillet(C, i):
    v = C[i]
    p = C[(i - 1) % 4]
    n = C[(i + 1) % 4]
    d1 = unit((p[0] - v[0], p[1] - v[1]))
    d2 = unit((n[0] - v[0], n[1] - v[1]))
    half = math.acos(max(-1, min(1, d1[0] * d2[0] + d1[1] * d2[1]))) / 2
    dt = R / math.tan(half)
    dc = R / math.sin(half)
    bis = unit((d1[0] + d2[0], d1[1] + d2[1]))
    t1 = (v[0] + d1[0] * dt, v[1] + d1[1] * dt)
    t2 = (v[0] + d2[0] * dt, v[1] + d2[1] * dt)
    ctr = (v[0] + bis[0] * dc, v[1] + bis[1] * dc)
    vd = unit((v[0] - ctr[0], v[1] - ctr[1]))
    return t1, t2, ctr, (ctr[0] + vd[0] * R, ctr[1] + vd[1] * R)


def main():
    b = pcbnew.LoadBoard(str(BOARD))
    edge = b.GetLayerID("Edge.Cuts")
    silk = b.GetLayerID("F.SilkS")
    F = [fillet(CORNERS, i) for i in range(4)]

    def vec(pt):
        return pcbnew.VECTOR2I(pcbnew.FromMM(pt[0]), pcbnew.FromMM(pt[1]))

    def seg(a, z, layer=None, w=0.1):
        s = pcbnew.PCB_SHAPE(b)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(vec(a))
        s.SetEnd(vec(z))
        s.SetLayer(edge if layer is None else layer)
        s.SetWidth(pcbnew.FromMM(w))
        b.Add(s)

    def arc(a, m, z):
        s = pcbnew.PCB_SHAPE(b)
        s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetArcGeometry(vec(a), vec(m), vec(z))
        s.SetLayer(edge)
        s.SetWidth(pcbnew.FromMM(0.1))
        b.Add(s)

    for d in list(b.GetDrawings()):
        if d.GetLayer() == edge:
            b.Remove(d)
    for i in range(4):
        t1, t2, ctr, mid = F[i]
        arc(t1, mid, t2)
        seg(t2, F[(i + 1) % 4][0])

    def mhole(ref, ctr):
        fp = pcbnew.FOOTPRINT(b)
        fp.SetReference(ref)
        pad = pcbnew.PAD(fp)
        pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
        pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
        pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(2.7), pcbnew.FromMM(2.7)))
        pad.SetDrillSize(pcbnew.VECTOR2I(pcbnew.FromMM(2.7), pcbnew.FromMM(2.7)))
        ls = pcbnew.LSET()
        ls.addLayer(pcbnew.F_Mask)
        ls.addLayer(pcbnew.B_Mask)
        pad.SetLayerSet(ls)
        fp.Add(pad)
        fp.SetPosition(vec(ctr))
        fp.SetReference(ref)
        b.Add(fp)

    for i in range(4):
        mhole(f"MH{i + 1}", F[i][2])

    cen = (sum(p[0] for p in CORNERS) / 4, sum(p[1] for p in CORNERS) / 4)

    def strip(pa, pb):
        d = unit((pb[0] - pa[0], pb[1] - pa[1]))
        nrm = (-d[1], d[0])
        mid = ((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2)
        if (cen[0] - mid[0]) * nrm[0] + (cen[1] - mid[1]) * nrm[1] < 0:
            nrm = (-nrm[0], -nrm[1])
        q = [pa, pb,
             (pb[0] + nrm[0] * STRIP, pb[1] + nrm[1] * STRIP),
             (pa[0] + nrm[0] * STRIP, pa[1] + nrm[1] * STRIP)]
        z = pcbnew.ZONE(b)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowFootprints(True)
        z.SetDoNotAllowCopperPour(True)
        ls = pcbnew.LSET()
        ls.addLayer(pcbnew.F_Cu)
        ls.addLayer(pcbnew.B_Cu)
        z.SetLayerSet(ls)
        poly = pcbnew.SHAPE_POLY_SET()
        poly.NewOutline()
        for pt in q:
            poly.Append(pcbnew.FromMM(pt[0]), pcbnew.FromMM(pt[1]))
        z.SetOutline(poly)
        b.Add(z)
        seg(q[3], q[2], silk, 0.15)

    strip(CORNERS[1], CORNERS[2])   # port
    strip(CORNERS[3], CORNERS[0])   # starboard
    pcbnew.SaveBoard(str(BOARD), b)
    print("done: 4 corner M2.5 holes + concentric fillets + 2 keep-out strips")
    return 0


if __name__ == "__main__":
    sys.exit(main())
