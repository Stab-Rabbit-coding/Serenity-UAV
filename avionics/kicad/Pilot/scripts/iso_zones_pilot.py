#!/usr/bin/python3
"""iso_zones_pilot.py — Redraw Pilot's isolation zones for the ISOW §13.1 re-floorplan.

Usage:
    /usr/bin/python3 iso_zones_pilot.py <in.kicad_pcb> <out.kicad_pcb>

Run after ``refloorplan_pilot.py`` (2026-10-17, S. Griffing decisions; script by Claude
Opus 5.5).  The isolators now sit at rot 180 with the isolated domains of
``refloorplan_pilot.DOMAINS`` (the old band was one rectangle across the bottom edge), so
every zone derived from the band is replaced:

* ``ISO_BAND`` name-marker rule areas (no keep-out flags; Pilot.kicad_dru keys on them):
  the union of the domains' F rectangles on F.Cu + In1-In4, and of the B rectangles on
  B.Cu.
* ``GND2_CAN island`` / ``GND2_RS485 island`` on In1.Cu: each domain's F union, pulled
  in 0.25 mm per side so the two islands keep 0.5 mm between them, minus the bubbles.
* ``GND plane`` (In1.Cu) and ``+3V3 plane`` (In4.Cu): the board less 0.5 mm, minus every
  domain grown by the 0.5 mm cross-domain moat (Pilot.kicad_dru
  iso_cross_domain_clearance), minus the bubbles.  The explicit notch (not zone
  priority) is kept from ``gen_pilot_pcb.py``.
* The "isolation keepout inner" areas (In2-In4 no tracks / vias) are dropped: logic
  copper is already barred from the band by ``iso_band_logic_copper``, the planes are
  notched, and the isolated B.Cu parts (bulk caps, beads) need vias to F.Cu, which the
  blanket ban forbade (the reason ``iso_via_windows.py`` existed).
* New ``BUBBLE_CAN`` / ``BUBBLE_485`` rule areas on every copper layer: pins 11 (GND2)
  and 12 (VISOOUT) pad outlines grown by 4.0 mm, the TI ISOW1044 SLLSFF7A §13.1 p. 36
  [REF-SENSOR-009] / ISOW1412 SLLSF86C §13.1 p. 41 [REF-SENSOR-010] "no metal traces or
  ground pour within 4 mm" zone, read as every layer, pad edge to metal edge.  The areas
  forbid copper pour themselves; ``bubble_*`` rules appended to Pilot.kicad_dru forbid
  any other track, via or pad there except the isolator's own pins and the converter-
  side nets the datasheet's own layout connects there (``*_DCDC``: the §13.1 10 nF cap
  and the bead pads).

Geometry is computed with shapely (2.1) and written through pcbnew zone calls only; the
old zones are cut from the S-expression text first (no pcbnew Remove(): the 9.0.2 SWIG
binding breaks after it, avionics/kicad/PCBNEW_SWIG_BUG.md).

License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pcbnew  # type: ignore
from shapely.geometry import MultiPolygon, box
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refloorplan_pilot import DOMAINS  # noqa: E402

S = 1e6
BOARD = box(121.5, 88.0, 175.5, 122.0)        # gen_pilot_pcb.py MAIN_PLANE extent
MOAT = 0.5                                     # iso_cross_domain_clearance
BUBBLE = 4.0                                   # §13.1 item 5
OLD = {"ISO_BAND", "GND2_CAN island", "GND2_RS485 island", "GND plane", "+3V3 plane",
       "isolation keepout inner", "BUBBLE_CAN", "BUBBLE_485"}
BUBBLE_NAME = {"CAN-TR": "BUBBLE_CAN", "RS485": "BUBBLE_485"}
DRU_RULES = """
# ISOW §13.1 bubbles (iso_zones_pilot.py, 2026-10-17): no foreign metal within 4 mm of
# pins 11 / 12 on any layer.  The isolator's own pins and its converter-side nets (the
# 10 nF cap and the bead pads, per the datasheet's own layout) are the only exceptions.
(rule bubble_can
    (condition "A.intersectsArea('BUBBLE_CAN') && A.Reference != 'CAN-TR' && A.NetName != 'GND2_CAN_DCDC' && A.NetName != 'VCC2_CAN_DCDC'")
    (constraint disallow track via pad))
(rule bubble_485
    (condition "A.intersectsArea('BUBBLE_485') && A.Reference != 'RS485' && A.NetName != 'GND2_RS485_DCDC' && A.NetName != 'VCC2_RS485_DCDC'")
    (constraint disallow track via pad))
# §13.1 item 1 puts the 10 nF caps < 1 mm from pins 11 / 12, i.e. inside the SOIC-20W
# courtyard margin, and the VDD / VIO caps and the bus CMCs sit as close to their pins.
# Only these named pairs are exempt; their pads still keep the normal clearances.
(rule iso_section_13_1_courtyard
    (condition "(A.Reference == 'CAN-TR' && (B.Reference == 'C-CAN1' || B.Reference == 'C-CAN3' || B.Reference == 'C-CAN4' || B.Reference == 'C-CAN6' || B.Reference == 'CMC-CAN')) || (A.Reference == 'RS485' && (B.Reference == 'C-485-1' || B.Reference == 'C-485-4' || B.Reference == 'C-485-6' || B.Reference == 'CMC-RS485'))")
    (constraint courtyard_clearance (min 0mm))
    (severity ignore))
"""


def cut_zones(text: str) -> str:
    """Remove the top-level zone blocks whose (name ...) is in OLD."""
    out, i, n = [], 0, 0
    for m in re.finditer(r"^\t\(zone\n.*?^\t\)\n", text, flags=re.S | re.M):
        name = re.search(r'^\t\t\(name "([^"]*)"\)', m.group(0), re.M)
        if name and name.group(1) in OLD:
            out.append(text[i:m.start()])
            i = m.end()
            n += 1
    out.append(text[i:])
    print(f"removed {n} old zones")
    return "".join(out)


def polys(g) -> list:
    if g.is_empty:
        return []
    return list(g.geoms) if isinstance(g, MultiPolygon) else [g]


def add(board, geom, layers, name, net=None, priority=0, rule=False, no_pour=False):
    """One zone per polygon of geom (holes kept)."""
    for p in polys(geom):
        z = pcbnew.ZONE(board)
        lset = pcbnew.LSET()
        for layer in layers:
            lset.AddLayer(layer)
        z.SetLayerSet(lset)
        z.SetZoneName(name)
        if rule:
            z.SetIsRuleArea(True)
            z.SetDoNotAllowCopperPour(no_pour)
            z.SetDoNotAllowTracks(False)
            z.SetDoNotAllowVias(False)
            z.SetDoNotAllowPads(False)
            z.SetDoNotAllowFootprints(False)
        else:
            z.SetNet(net)
            z.SetAssignedPriority(priority)
            z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
            z.SetLocalClearance(int(0.25 * S))
            z.SetMinThickness(int(0.2 * S))
            z.SetThermalReliefGap(int(0.3 * S))
            z.SetThermalReliefSpokeWidth(int(0.3 * S))
            z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        ol = z.Outline()
        ol.NewOutline()
        for x, y in list(p.exterior.coords)[:-1]:
            ol.Append(int(round(x * S)), int(round(y * S)))
        for k, hole in enumerate(p.interiors):
            ol.NewHole()
            for x, y in list(hole.coords)[:-1]:
                ol.Append(int(round(x * S)), int(round(y * S)), 0, k)
        board.Add(z)


def main() -> None:
    src, dst = sys.argv[1], sys.argv[2]
    if Path(src).resolve() == Path(dst).resolve():
        raise SystemExit("refusing to overwrite the input board")
    Path(dst).write_text(cut_zones(Path(src).read_text()))
    b = pcbnew.LoadBoard(dst)

    dom_f = {d: unary_union([box(*r) for r in s["F"]]) for d, s in DOMAINS.items()}
    dom_b = unary_union([box(*r) for s in DOMAINS.values() for r in s["B"]])
    all_f = unary_union(list(dom_f.values()))
    bubbles = {}
    for iso, name in BUBBLE_NAME.items():
        f = b.FindFootprintByReference(iso)
        pads = []
        for p in f.Pads():
            if p.GetNumber() in ("11", "12"):
                bb = p.GetBoundingBox()
                pads.append(box(bb.GetLeft() / S, bb.GetTop() / S, bb.GetRight() / S, bb.GetBottom() / S))
        assert len(pads) == 2, iso
        bubbles[iso] = unary_union(pads).buffer(BUBBLE, quad_segs=8)
    all_bub = unary_union(list(bubbles.values()))

    cu = [b.GetLayerID(n) for n in ("F.Cu", "In1.Cu", "In2.Cu", "In3.Cu", "In4.Cu", "B.Cu")]
    top_inner = cu[:5]
    add(b, all_f, top_inner, "ISO_BAND", rule=True)
    add(b, dom_b, [pcbnew.B_Cu], "ISO_BAND", rule=True)
    for iso, g in bubbles.items():
        add(b, g, cu, BUBBLE_NAME[iso], rule=True, no_pour=True)
    island = {"CAN": "GND2_CAN", "RS485": "GND2_RS485"}
    for d, g in dom_f.items():
        shp = g.buffer(-MOAT / 2, join_style="mitre").difference(all_bub)
        add(b, shp, [pcbnew.In1_Cu], f"{island[d]} island", b.FindNet(island[d]), priority=1)
    plane = BOARD.difference(all_f.buffer(MOAT, join_style="mitre")).difference(all_bub)
    add(b, plane, [pcbnew.In1_Cu], "GND plane", b.FindNet("GND"))
    add(b, plane, [pcbnew.In4_Cu], "+3V3 plane", b.FindNet("+3V3"))
    pcbnew.SaveBoard(dst, b)

    dru = Path(dst).with_suffix(".kicad_dru")
    base = Path(src).with_suffix(".kicad_dru")
    text = base.read_text() if base.exists() else "(version 1)\n"
    if "rule bubble_can" not in text:
        text = text.rstrip("\n") + "\n" + DRU_RULES
    dru.write_text(text)
    print(f"wrote {dst} and {dru.name}; bubbles: "
          + ", ".join(f"{k} {v.bounds[0]:.2f}-{v.bounds[2]:.2f} x {v.bounds[1]:.2f}-{v.bounds[3]:.2f}"
                      for k, v in bubbles.items()))


if __name__ == "__main__":
    main()
