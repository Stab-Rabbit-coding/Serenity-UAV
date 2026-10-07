#!/usr/bin/env python3
"""finish_tacco_pcb.py — Route TACCO with freerouting through KiCad's Specctra bridge,
then add the outer GND pours and the QFN thermal vias, refill every zone and save.

Usage:
    python3 finish_tacco_pcb.py prepare <board.kicad_pcb>
    python3 finish_tacco_pcb.py export  <board.kicad_pcb> <out.dsn> [--band-keepout]
    python3 finish_tacco_pcb.py import  <board.kicad_pcb> <routed.ses>
    python3 finish_tacco_pcb.py finish  <board.kicad_pcb>

Phases (avionics/WBS.md §1.2a "TACCO area recovery", U5):

1. ``export --band-keepout`` writes a DSN in which the CAN-FD / RS-485 isolation band
   (the ``ISO_BAND`` rule area) is a hard track/via keepout on every copper layer.
   Freerouting knows nothing about this board's ``.kicad_dru`` isolation rules, so
   phase 1 routes every logic net with the band closed; the ISOLATION-class nets
   inside the band are left unrouted on purpose.
2. ``import`` brings the phase-1 session back.  ``export`` (no keepout) then writes a
   second DSN: the routed wires are carried into it, and freerouting finishes the
   ISOLATION nets, whose pads all sit inside the band.
3. ``finish`` adds a top and bottom GND pour (freerouting treats a filled zone as
   fixed copper, which is why the generator leaves F.Cu/B.Cu pour-free until now),
   drops a 3 x 3 grid of 0.3 mm thermal vias under the STM32WLE5JC exposed pad (the
   library ``_ThermalVias`` land uses 0.2 mm drills, below this board's 0.3 mm
   minimum), refills all zones and saves.  ``kicad-cli pcb drc --severity-all
   --schematic-parity`` is the gate that follows.

Operational notes (2026-09-30): freerouting 1.9 only writes the .ses when it stops, so
run it with a pass cap (``-mp``) sized to the residue, not open-ended; and re-exporting a
partly routed board after a netclass width change raises a GUI "net normalization"
warning that blocks until dismissed (xdotool Return under xvfb).

Same discipline as Pilot's ``finish_pilot_pcb.py``: an autorouted result is accepted
only if the DRC gate passes; shorts or isolation-rule violations are fixed or the
result is rejected.

Author: Claude Fable 5.1, 2026-09-29.  Owner: sgriffing.  License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pcbnew  # type: ignore


def mm(v: float) -> int:
    return int(round(v * 1e6))


def board_edge(board: pcbnew.BOARD):
    edge = board.GetBoardEdgesBoundingBox()
    x1, y1 = edge.GetX() / 1e6, edge.GetY() / 1e6
    return x1, y1, x1 + edge.GetWidth() / 1e6, y1 + edge.GetHeight() / 1e6


def add_edge_keepout(board: pcbnew.BOARD, width: float = 0.55) -> None:
    """Hard keepout ring just inside the outline on every copper layer so freerouting
    honours the 0.3 mm copper-to-edge rule it cannot read from the project.  Four
    plain rectangles (the Specctra exporter drops polygon holes, so a ring with a
    hole would have covered the whole board)."""
    x1, y1, x2, y2 = board_edge(board)
    w = width
    strips = [
        [(x1 - 1, y1 - 1), (x2 + 1, y1 - 1), (x2 + 1, y1 + w), (x1 - 1, y1 + w)],
        [(x1 - 1, y2 - w), (x2 + 1, y2 - w), (x2 + 1, y2 + 1), (x1 - 1, y2 + 1)],
        [(x1 - 1, y1 - 1), (x1 + w, y1 - 1), (x1 + w, y2 + 1), (x1 - 1, y2 + 1)],
        [(x2 - w, y1 - 1), (x2 + 1, y1 - 1), (x2 + 1, y2 + 1), (x2 - w, y2 + 1)],
    ]
    for layer in board.GetEnabledLayers().CuStack():
        for pts in strips:
            z = pcbnew.ZONE(board)
            z.SetLayer(layer)
            z.SetIsRuleArea(True)
            z.SetDoNotAllowTracks(True)
            z.SetDoNotAllowVias(True)
            z.SetDoNotAllowCopperPour(False)
            z.SetDoNotAllowPads(False)
            z.SetDoNotAllowFootprints(False)
            z.SetZoneName("TMP_EDGE_KEEPOUT")
            ol = z.Outline()
            ol.NewOutline()
            for x, y in pts:
                ol.Append(mm(x), mm(y))
            board.Add(z)


def _copper_boxes(board: pcbnew.BOARD):
    boxes = []
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            bb = pad.GetBoundingBox()
            boxes.append((bb.GetX(), bb.GetY(), bb.GetX() + bb.GetWidth(), bb.GetY() + bb.GetHeight(), pad.GetNetCode(),
                          pad.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)))
    for t in board.GetTracks():
        bb = t.GetBoundingBox()
        boxes.append((bb.GetX(), bb.GetY(), bb.GetX() + bb.GetWidth(), bb.GetY() + bb.GetHeight(), t.GetNetCode(),
                      t.Type() == pcbnew.PCB_VIA_T))
    return boxes


def plane_fanout(board: pcbnew.BOARD, nets=("GND", "+3V3"), via_d: float = 0.6, drill: float = 0.3,
                 clearance: float = 0.3) -> int:
    """For every SMD pad on a plane net, drop a via next to the pad (away from the part
    body) and a short track from the pad to it, when the site is free of other copper.
    Freerouting keeps these as fixed wires; the In1 GND / In4 +3V3 planes pick them up
    at zone fill.  Returns the number of vias placed."""
    x1, y1, x2, y2 = board_edge(board)
    band = next((z for z in board.Zones() if z.GetIsRuleArea() and z.GetZoneName() == "ISO_BAND"), None)
    bbox = band.GetBoundingBox() if band else None
    boxes = _copper_boxes(board)
    r = mm(via_d / 2 + clearance)
    placed = 0
    for fp in board.GetFootprints():
        c = fp.GetPosition()
        for pad in fp.Pads():
            if pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or pad.GetNetname() not in nets:
                continue
            net = pad.GetNetCode()
            pc = pad.GetPosition()
            bb = pad.GetBoundingBox()
            half = max(bb.GetWidth(), bb.GetHeight()) / 2
            reach = half + mm(via_d / 2 + 0.2)
            dx, dy = pc.x - c.x, pc.y - c.y
            n = (dx * dx + dy * dy) ** 0.5 or 1.0
            dirs = [(dx / n, dy / n), (-dy / n, dx / n), (dy / n, -dx / n), (-dx / n, -dy / n)]
            for ux, uy in dirs:
                vx, vy = int(pc.x + ux * reach), int(pc.y + uy * reach)
                if not (mm(x1 + 0.9) < vx < mm(x2 - 0.9) and mm(y1 + 0.9) < vy < mm(y2 - 0.9)):
                    continue
                if bbox and bbox.GetX() - mm(0.6) <= vx <= bbox.GetX() + bbox.GetWidth() + mm(0.6) and \
                        bbox.GetY() - mm(0.6) <= vy <= bbox.GetY() + bbox.GetHeight() + mm(0.6):
                    continue
                ok = True
                for bx1, by1, bx2, by2, bnet, tht in boxes:
                    if bnet == net and not tht and bx1 <= pc.x <= bx2 and by1 <= pc.y <= by2:
                        continue  # the pad itself
                    if bx1 - r <= vx <= bx2 + r and by1 - r <= vy <= by2 + r:
                        if bnet != net or tht:
                            ok = False
                            break
                if not ok:
                    continue
                v = pcbnew.PCB_VIA(board)
                v.SetPosition(pcbnew.VECTOR2I(vx, vy))
                v.SetViaType(pcbnew.VIATYPE_THROUGH)
                v.SetDrill(mm(drill))
                v.SetWidth(pcbnew.PADSTACK.ALL_LAYERS, mm(via_d))
                v.SetNet(pad.GetNet())
                board.Add(v)
                tr = pcbnew.PCB_TRACK(board)
                tr.SetStart(pcbnew.VECTOR2I(pc.x, pc.y))
                tr.SetEnd(pcbnew.VECTOR2I(vx, vy))
                tr.SetWidth(mm(0.25))
                tr.SetLayer(pcbnew.B_Cu if fp.IsFlipped() else pcbnew.F_Cu)
                tr.SetNet(pad.GetNet())
                board.Add(tr)
                boxes.append((vx - mm(via_d / 2), vy - mm(via_d / 2), vx + mm(via_d / 2), vy + mm(via_d / 2), net, True))
                placed += 1
                break
    return placed


def add_band_keepouts(board: pcbnew.BOARD) -> int:
    """Copy the ISO_BAND rule area into a hard keepout per copper layer (phase 1)."""
    band = next((z for z in board.Zones() if z.GetIsRuleArea() and z.GetZoneName() == "ISO_BAND"), None)
    if band is None:
        raise SystemExit("ISO_BAND rule area not found")
    n = 0
    for layer in board.GetEnabledLayers().CuStack():
        if not band.IsOnLayer(layer):
            continue  # the band is F.Cu + inner layers only; B.Cu under it is logic copper
        z = pcbnew.ZONE(board)
        z.SetLayer(layer)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowTracks(True)
        z.SetDoNotAllowVias(True)
        z.SetDoNotAllowCopperPour(False)
        z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
        z.SetZoneName("TMP_BAND_KEEPOUT")
        ol = z.Outline()
        ol.NewOutline()
        src = band.Outline().Outline(0)
        for i in range(src.PointCount()):
            p = src.CPoint(i)
            ol.Append(p.x, p.y)
        board.Add(z)
        n += 1
    return n


def add_outer_gnd_pours(board: pcbnew.BOARD) -> None:
    gnd = board.FindNet("GND")
    if gnd is None:
        raise SystemExit("net GND not found on board")
    x1, y1, x2, y2 = board_edge(board)
    pts = [(x1 + 0.5, y1 + 0.5), (x2 - 0.5, y1 + 0.5), (x2 - 0.5, y2 - 0.5), (x1 + 0.5, y2 - 0.5)]
    for layer, name in ((pcbnew.F_Cu, "GND pour (top)"), (pcbnew.B_Cu, "GND pour (bottom)")):
        z = pcbnew.ZONE(board)
        z.SetLayer(layer)
        z.SetNet(gnd)
        z.SetZoneName(name)
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetLocalClearance(mm(0.25))
        z.SetMinThickness(mm(0.15))
        z.SetThermalReliefGap(mm(0.3))
        z.SetThermalReliefSpokeWidth(mm(0.3))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        ol = z.Outline()
        ol.NewOutline()
        for x, y in pts:
            ol.Append(mm(x), mm(y))
        board.Add(z)


def add_qfn_thermal_vias(board: pcbnew.BOARD, ref: str = "MLRS-MCU", pitch: float = 1.4, n: int = 3) -> int:
    fp = board.FindFootprintByReference(ref)
    if fp is None:
        raise SystemExit(f"{ref} not found")
    gnd = board.FindNet("GND")
    c = fp.GetPosition()
    added = 0
    for i in range(n):
        for j in range(n):
            v = pcbnew.PCB_VIA(board)
            v.SetPosition(pcbnew.VECTOR2I(c.x + mm((i - (n - 1) / 2) * pitch), c.y + mm((j - (n - 1) / 2) * pitch)))
            v.SetViaType(pcbnew.VIATYPE_THROUGH)
            v.SetDrill(mm(0.3))
            v.SetWidth(pcbnew.PADSTACK.ALL_LAYERS, mm(0.5))
            v.SetNet(gnd)
            board.Add(v)
            added += 1
    return added


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, pcb_path = sys.argv[1], sys.argv[2]
    board = pcbnew.LoadBoard(pcb_path)
    if cmd == "prepare":
        # one-time, before phase 1: QFN thermal vias + plane fanout become fixed copper;
        # any fanout via that DRC still objects to (it only sees pad bounding boxes) is
        # removed together with its stub, so the router starts from a clean board.
        print("thermal vias:", add_qfn_thermal_vias(board))
        print("plane fanout vias:", plane_fanout(board))
        pcbnew.SaveBoard(pcb_path, board)
        import json
        import subprocess
        import tempfile
        rep = Path(tempfile.mkdtemp()) / "drc.json"
        subprocess.run(["kicad-cli", "pcb", "drc", "--severity-all", "--format", "json", "--output", str(rep), pcb_path],
                       capture_output=True, text=True)
        bad = set()
        for v in json.load(open(rep)).get("violations", []):
            if v.get("severity") != "error":
                continue
            for it in v.get("items", []):
                if it.get("description", "").startswith("Via "):
                    bad.add((round(it["pos"]["x"], 3), round(it["pos"]["y"], 3)))
        removed = 0
        for tr in list(board.GetTracks()):
            if tr.Type() == pcbnew.PCB_VIA_T:
                key = (round(tr.GetPosition().x / 1e6, 3), round(tr.GetPosition().y / 1e6, 3))
                if key in bad:
                    for st in list(board.GetTracks()):
                        if st.Type() == pcbnew.PCB_TRACE_T and (st.GetEnd() == tr.GetPosition() or st.GetStart() == tr.GetPosition()):
                            board.Remove(st)
                    board.Remove(tr)
                    removed += 1
        print("fanout vias removed after DRC:", removed)
        pcbnew.SaveBoard(pcb_path, board)
        return
    if cmd == "export":
        dsn = sys.argv[3]
        if "--band-keepout" in sys.argv:
            print("band keepouts added:", add_band_keepouts(board))
        else:
            # ISO_BAND is a DRC name marker (no keepout flags), but KiCad's Specctra
            # exporter writes every rule area as a keepout, which walled the isolated
            # pads off from freerouting in the "open band" phase (found 2026-10-06:
            # phase 2 routed 0 of 51 isolated connections).  Drop the markers from
            # this in-memory copy only; the saved board keeps them for DRC.
            markers = [z for z in board.Zones() if z.GetIsRuleArea() and z.GetZoneName() == "ISO_BAND"]
            for z in markers:
                board.Remove(z)
            print("ISO_BAND markers left out of the DSN:", len(markers))
        add_edge_keepout(board)
        ok = pcbnew.ExportSpecctraDSN(board, dsn)
        print("exported", dsn, ok)
        return
    if cmd == "import":
        ses = sys.argv[3]
        if not pcbnew.ImportSpecctraSES(board, ses):
            sys.exit("ImportSpecctraSES failed")
        for z in list(board.Zones()):
            if z.GetZoneName() in ("TMP_BAND_KEEPOUT", "TMP_EDGE_KEEPOUT"):
                board.Remove(z)
        pcbnew.SaveBoard(pcb_path, board)
        n_vias = sum(1 for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T)
        print(f"imported {ses}: {len(board.GetTracks()) - n_vias} segments, {n_vias} vias; saved {pcb_path}")
        return
    if cmd == "finish":
        add_outer_gnd_pours(board)
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(board.Zones())
        pcbnew.SaveBoard(pcb_path, board)
        print("pours added, zones filled, saved", pcb_path)
        return
    sys.exit(f"unknown command {cmd}")


if __name__ == "__main__":
    main()
