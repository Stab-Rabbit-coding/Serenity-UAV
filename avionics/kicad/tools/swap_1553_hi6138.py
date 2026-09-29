#!/usr/bin/env python3
"""In-place PCB patch for the fleet MIL-STD-1553C swap (HI-1573 -> HI-6138).

Why a patch and not a regeneration
----------------------------------
The Pilot and TACCO schematics are generator-owned and regenerate byte-for-byte,
but the committed PCBs carry hand placement made after the last generator run
(a fresh ``gen_pilot_pcb.py`` run moves 16 Pilot parts, checked 2026-09-28).
Re-running the PCB generator would silently discard that work, so this tool
changes only what the swap needs:

1. the ``1553-XCVR`` footprint is replaced by the HI-6138 land at the SAME
   position and side, turned (0/90/180/270 deg) so its BUSA pins face the
   1553 transformer's primary;
2. parts that are in the regenerated netlist but not on the board (the 50 MHz
   MCLK oscillator and its bypass, the IRQ pull-up, the extra VCCP bypass) are
   placed by a courtyard-collision-free spiral search around the new HI-6138
   on the same side -- nothing already placed is moved;
3. every pad's net is re-assigned from the regenerated netlist (so the PB2 P1
   remap and the renamed nets land); pads absent from the netlist are cleared.

The run refuses to place a part it cannot fit without a courtyard overlap and
exits non-zero, rather than forcing an overlap.

Usage::

    python3 swap_1553_hi6138.py <board.kicad_pcb> <board.net>

Plan: docs/plans/2026-09-28-002-feat-fleet-1553c-hi6138-swap-plan.md (U2/U3).
Author: Claude Opus 5.5 (2026-09-28).  Owner: sgriffing.  License: CC BY 4.0.
"""

import math
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import pcbnew

HERE = Path(__file__).resolve().parent
CUSTOM = HERE.parent / "Serenity-Custom.pretty"
SYSLIB = Path("/usr/share/kicad/footprints")
ANCHOR = "1553-XCVR"
XFMR = "1553-XFM"
BUS_PADS = ("43", "45")          # HI-6138 BUSA*/BUSA (DS6138 p.1)
XFMR_PRI = ("1", "3")            # PM-DB2791S primary
MARGIN = 0.15                    # mm courtyard-to-courtyard gap for new parts


def mm(v: float) -> int:
    return pcbnew.FromMM(v)


def sexp(text: str):
    """Minimal S-expression reader for KiCad netlists (same as gen_pilot_pcb)."""
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


def read_netlist(path: Path):
    tree = sexp(path.read_text())
    comps: Dict[str, Dict[str, str]] = {}
    nets: Dict[str, List[Tuple[str, str]]] = {}
    for node in tree:
        if isinstance(node, list) and node and node[0] == "components":
            for c in node[1:]:
                d = {"ref": "", "footprint": "", "value": ""}
                for f in c[1:]:
                    if f[0] in d:
                        d[f[0]] = f[1]
                comps[d["ref"]] = d
        if isinstance(node, list) and node and node[0] == "nets":
            for n in node[1:]:
                name, nodes = "", []
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


def crt(fp: pcbnew.FOOTPRINT, grow: float = 0.0) -> Tuple[float, float, float, float]:
    layer = pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd
    bb = fp.GetCourtyard(layer).BBox()
    if bb.GetWidth() == 0:
        bb = fp.GetBoundingBox(False)
    g = grow
    return (bb.GetLeft() / 1e6 - g, bb.GetTop() / 1e6 - g, bb.GetRight() / 1e6 + g, bb.GetBottom() / 1e6 + g)


def hits(a, b) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def pad_centroid(fp: pcbnew.FOOTPRINT, nums) -> Tuple[float, float]:
    pts = [p.GetPosition() for p in fp.Pads() if p.GetNumber() in nums]
    return (sum(p.x for p in pts) / len(pts) / 1e6, sum(p.y for p in pts) / len(pts) / 1e6)


def blocked_on(fp: pcbnew.FOOTPRINT, flipped: bool) -> bool:
    """A footprint blocks a side if it is on that side or is through-hole."""
    th = any(p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH for p in fp.Pads())
    return th or fp.IsFlipped() == flipped


def main() -> None:
    pcb_path, net_path = Path(sys.argv[1]), Path(sys.argv[2])
    comps, nets = read_netlist(net_path)
    board = pcbnew.LoadBoard(str(pcb_path))
    onboard = {fp.GetReference(): fp for fp in board.GetFootprints()}

    old = onboard[ANCHOR]
    pos, flipped = old.GetPosition(), old.IsFlipped()
    new_refs = [r for r in comps if r not in onboard]
    # Load every library footprint BEFORE removing anything: pcbnew 9.0.2's
    # SWIG binding can segfault on FootprintLoad after a board Remove.
    new_anchor = load_fp(comps[ANCHOR]["footprint"])
    loaded = {r: load_fp(comps[r]["footprint"]) for r in new_refs}

    # 1) swap the anchor in place ------------------------------------------------
    board.Remove(old)
    fp = new_anchor
    fp.SetReference(ANCHOR)
    fp.SetValue(comps[ANCHOR]["value"])
    board.Add(fp)
    fp.SetPosition(pos)
    if flipped != fp.IsFlipped():
        fp.Flip(pos, True)
    xf = onboard[XFMR]
    tx = pad_centroid(xf, XFMR_PRI)
    best = None
    for rot in (0, 90, 180, 270):
        fp.SetOrientationDegrees(rot)
        bx = pad_centroid(fp, BUS_PADS)
        d = math.hypot(bx[0] - tx[0], bx[1] - tx[1])
        if best is None or d < best[0]:
            best = (d, rot)
    fp.SetOrientationDegrees(best[1])
    # Fleet convention (gen_pilot_pcb.py): reference designators on Fab, not silk.
    fp.Reference().SetLayer(pcbnew.B_Fab if fp.IsFlipped() else pcbnew.F_Fab)
    fp.Value().SetVisible(False)
    print(f"{ANCHOR}: {comps[ANCHOR]['footprint']} at ({pos.x / 1e6:.3f}, {pos.y / 1e6:.3f}) "
          f"{'B' if flipped else 'F'}.Cu rot {best[1]} (BUSA->XFMR {best[0]:.2f} mm)")

    # 2) place new parts near the anchor -----------------------------------------
    edge = board.GetBoardEdgesBoundingBox()
    ex = (edge.GetLeft() / 1e6 + 0.5, edge.GetTop() / 1e6 + 0.5,
          edge.GetRight() / 1e6 - 0.5, edge.GetBottom() / 1e6 - 0.5)
    ax, ay = pos.x / 1e6, pos.y / 1e6
    for ref in new_refs:
        nf = loaded[ref]
        nf.SetReference(ref)
        nf.SetValue(comps[ref]["value"])
        board.Add(nf)
        if flipped != nf.IsFlipped():
            nf.Flip(nf.GetPosition(), True)
        others = [crt(o, MARGIN) for o in board.GetFootprints()
                  if o is not nf and blocked_on(o, flipped)]
        placed = False
        r = 0.0
        while r <= 20.0 and not placed:
            steps = max(1, int(2 * math.pi * r / 0.25))
            for k in range(steps):
                a = 2 * math.pi * k / steps
                for rot in (0, 90):
                    nf.SetOrientationDegrees(rot)
                    nf.SetPosition(pcbnew.VECTOR2I(mm(ax + r * math.cos(a)), mm(ay + r * math.sin(a))))
                    c = crt(nf)
                    if c[0] < ex[0] or c[1] < ex[1] or c[2] > ex[2] or c[3] > ex[3]:
                        continue
                    if any(hits(c, o) for o in others):
                        continue
                    placed = True
                    break
                if placed:
                    break
            r += 0.25
        if not placed:
            raise SystemExit(f"FAIL: no collision-free site for {ref} within 20 mm of {ANCHOR}")
        p = nf.GetPosition()
        print(f"placed {ref} ({comps[ref]['footprint']}) at ({p.x / 1e6:.3f}, {p.y / 1e6:.3f}) r={r - 0.25:.2f} mm")
        nf.Reference().SetLayer(pcbnew.B_Fab if nf.IsFlipped() else pcbnew.F_Fab)
        nf.Value().SetVisible(False)

    # 3) nets from the regenerated netlist ---------------------------------------
    netinfo = board.GetNetInfo()
    netmap: Dict[str, pcbnew.NETINFO_ITEM] = {}
    for name in nets:
        ni = netinfo.GetNetItem(name)
        if ni is None:
            ni = pcbnew.NETINFO_ITEM(board, name)
            board.Add(ni)
        netmap[name] = ni
    pad_net = {(r, p): n for n, nodes in nets.items() for r, p in nodes}
    changed = 0
    for f in board.GetFootprints():
        ref = f.GetReference()
        for pad in f.Pads():
            if not pad.GetNumber():
                continue
            want = pad_net.get((ref, pad.GetNumber()))
            have = pad.GetNetname()
            if want and have != want:
                pad.SetNet(netmap[want])
                changed += 1
            elif not want and have:
                pad.SetNetCode(0)
                changed += 1
    print(f"pad nets changed: {changed}")
    # Nets no longer in the netlist are left padless; KiCad drops padless,
    # trackless nets on the next save from the editor and DRC ignores them.
    board.Save(str(pcb_path))
    print("saved", pcb_path)


if __name__ == "__main__":
    main()
