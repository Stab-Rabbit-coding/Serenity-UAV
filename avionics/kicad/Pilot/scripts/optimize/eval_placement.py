#!/usr/bin/env python3
"""eval_placement.py — Measurement harness for the Pilot placement optimisation loop.

Usage:
    python3 eval_placement.py [moves.json] [--board <committed.kicad_pcb>]

Reads ``placement_moves.json`` (the ONLY mutable input of the loop), applies it to a
copy of the committed Pilot board, strips every routed track/via from that copy (this
loop scores placement, not routing — moved parts would otherwise leave dangling copper
that reads as DRC errors), then prints ONE JSON object of metrics on stdout:

* ``drc_errors``      gate — error-severity DRC items on the stripped board (courtyards,
                      copper-edge, ISO_BAND items_not_allowed on pads, ...)
* ``parity_issues``   gate — schematic parity (must stay 0)
* ``capfit_sum_mm``   PRIMARY (minimise) — sum over every bypass cap of the distance
                      from its supply pad to the nearest same-net pin of the IC it
                      serves (TARGETS below; caps with no shared net are skipped)
* ``caps_over_1p5mm`` diagnostic — caps further than 1.5 mm from their pin
* ``iso_hf_max_mm``   diagnostic — worst of the four ISOW 10 nF HF caps (datasheet < 1 mm)
* ``plane_pads_in_band`` diagnostic — GND/+3V3 pads whose position lies inside the
                      In1–In4 ISO_BAND outline (cannot take a plane via)

moves.json schema::

    {"moves": {"<ref>": {"x": mm, "y": mm, "rot": deg, "side": "F"|"B"}},   # any subset
     "band_outline": [[x, y], ...]}          # optional: replaces the F/In1-In4 ISO_BAND polygon

Side flips are only supported for 2-pad passives (symmetric lands), which is all the
caps this loop moves.

Author: Claude Opus 5.5, 2026-10-10.  Owner: sgriffing.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOARD = HERE.parents[1] / "kicads" / "Pilot.kicad_pcb"

# cap-ref prefix -> IC it decouples (from the Datasheet field text in Pilot.net)
TARGETS = [("C-485-", "RS485"), ("C-CAN", "CAN-TR"), ("C-1553", "1553-XCVR"), ("C-TPM", "TPM"),
           ("C-P1-", "ETH1-PHY"), ("C-P2-", "ETH2-PHY"), ("C-IMU", "IMU"), ("C-BARO", "BARO"),
           ("C-GPS", "GPS"), ("C-3V3-", "U-3V3"), ("C-BST", "U-3V3"), ("C-SS", "U-3V3"),
           ("C-25M", "X-25M"), ("C-50M", "X-50M"), ("C-ANT", "L-ANT")]
ISO_HF = ("C-CAN1", "C-CAN4", "C-485-1", "C-485-4")
GROUNDS = {"GND", "GND2_CAN", "GND2_RS485", "PGND"}
# caps scored on the committed board (2026-10-10); fewer means a ref or net vanished
EXPECTED_CAPS = 45


def fp_block(text: str, ref: str) -> "tuple[int, int]":
    """[start, end) of the top-level footprint block whose Reference is ``ref``."""
    i = text.index(f'(property "Reference" "{ref}"')
    s = text.rfind("\n\t(footprint ", 0, i) + 1
    m = re.compile(r"^\t\)\n", re.M).search(text, i)
    return s, m.end()


def rotate_children(blk: str, delta: float) -> str:
    """Add ``delta`` degrees to every pad / text ``(at x y [angle])`` in a footprint."""
    def bump(m: "re.Match") -> str:
        ang = round((float(m.group(3) or 0.0) + delta) % 360, 6)
        ang = 0.0 if ang in (0.0, 360.0) else ang
        return f"\t\t\t(at {m.group(1)} {m.group(2)}" + (f" {ang:g}" if ang else "") + ")"
    return re.sub(r"^\t\t\t\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)", bump, blk, flags=re.M)


def apply_moves(text: str, spec: dict) -> str:
    for ref, mv in spec.get("moves", {}).items():
        s, e = fp_block(text, ref)
        blk = text[s:e]
        side = "B" if '\t\t(layer "B.Cu")' in blk[:200] else "F"
        if mv.get("side") and mv["side"] != side:
            if len(re.findall(r"\(pad ", blk)) > 4:
                raise SystemExit(f"{ref}: side flip only supported for 2-pad passives")
            blk = re.sub(r'"([FB])\.(Cu|Paste|Mask|SilkS|Fab|CrtYd)"',
                         lambda m: f'"{"B" if m.group(1) == "F" else "F"}.{m.group(2)}"', blk)
            if mv["side"] == "F":
                blk = blk.replace("\t\t\t\t(justify mirror)\n", "")
            else:
                blk = re.sub(r"(\t\t\t\(effects\n(?:\t\t\t\t.*\n)*?)(\t\t\t\))",
                             lambda m: m.group(1) + "\t\t\t\t(justify mirror)\n" + m.group(2), blk)
        m = re.search(r"\n\t\t\(at ([-\d.]+) ([-\d.]+)((?: [-\d.]+)?)\)", blk)
        x = mv.get("x", float(m.group(1)))
        y = mv.get("y", float(m.group(2)))
        old_rot = float(m.group(3)) if m.group(3).strip() else 0.0
        rot = mv.get("rot", old_rot) % 360
        at = f"\n\t\t(at {x:g} {y:g}" + (f" {rot:g}" if rot else "") + ")"
        blk = blk[:m.start()] + at + blk[m.end():]
        if rot != old_rot % 360:
            # KiCad stores pad and text angles ABSOLUTE (footprint rotation included),
            # so a footprint rotation must rotate every child angle by the same delta
            # (review finding #1; matches pcbnew FOOTPRINT::SetOrientation).
            blk = rotate_children(blk, rot - old_rot)
        text = text[:s] + blk + text[e:]
    if "band_outline" in spec:
        pts = " ".join(f"(xy {x:g} {y:g})" for x, y in spec["band_outline"])
        replaced = 0
        # the ISO_BAND rule area that covers F.Cu + inner layers (not the two small B.Cu ones)
        for m in re.finditer(r'\t\(zone\n(?:\t\t.*\n)*?\t\t\(name "ISO_BAND"\)', text):
            z_end = text.index("\n\t)\n", m.start())
            blk = text[m.start():z_end]
            if '"In1.Cu"' not in blk:
                continue
            blk2, replaced = re.subn(r"\(pts\n(?:\t+\(xy[^\n]*\n)+\t+\)",
                                     f"(pts\n\t\t\t\t{pts}\n\t\t\t)", blk, count=1)
            text = text[:m.start()] + blk2 + text[z_end:]
            break
        if replaced != 1:  # review finding #4: never let an outline change silently no-op
            raise SystemExit("band_outline given but the In1 ISO_BAND outline was not replaced")
    return text


def strip_routing(text: str) -> str:
    """Remove every top-level segment / arc / via block and prove none remain."""
    out = re.sub(r"^\t\((segment|arc|via)(?: \w+)?\n.*?^\t\)\n", "", text, flags=re.S | re.M)
    if re.search(r"^\t\((segment|arc|via)\b", out, re.M):
        raise SystemExit("strip_routing left routed items behind (file format changed?)")
    return out


def geometry(pcb: Path) -> dict:
    """Read-only pcbnew pass (no polygon calls: the 9.0.2 binding breaks after them)."""
    code = f"""
import pcbnew, json
b = pcbnew.LoadBoard({str(pcb)!r}); s = 1e6
pads = [dict(ref=p.GetParentFootprint().GetReference(), num=p.GetNumber(), net=p.GetNetname(),
             x=p.GetPosition().x/s, y=p.GetPosition().y/s) for p in b.GetPads() if p.GetNumber()]
band = []
for z in b.Zones():
    if z.GetIsRuleArea() and z.GetZoneName() == 'ISO_BAND' and z.IsOnLayer(pcbnew.In1_Cu):
        ol = z.Outline().Outline(0)
        band = [(ol.CPoint(i).x/s, ol.CPoint(i).y/s) for i in range(ol.PointCount())]
print(json.dumps(dict(pads=pads, band=band)))
"""
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    return json.loads(r.stdout.strip().splitlines()[-1])


def in_poly(x: float, y: float, poly: list) -> bool:
    inside = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def capfit(g: dict, loops: "dict | None" = None) -> dict:
    """Supply-pad-to-pin distance per bypass cap.

    When ``loops`` is a dict it is filled with the full decoupling loop per cap: supply
    pad to nearest same-net IC pin PLUS ground pad to nearest same-ground IC pin
    (review finding #3: the supply-only metric ignores the return path).
    """
    by_ref: dict = {}
    for p in g["pads"]:
        by_ref.setdefault(p["ref"], []).append(p)
    dists = {}
    for ref, pads in by_ref.items():
        ic = next((t for pre, t in TARGETS if ref.startswith(pre)), None)
        if not ic or ic not in by_ref:
            continue
        sig = [p for p in pads if p["net"] not in GROUNDS] or pads
        best = min((math.hypot(q["x"] - p["x"], q["y"] - p["y"])
                    for p in sig for q in by_ref[ic] if q["net"] == p["net"]), default=None)
        if best is not None:
            dists[ref] = best
            if loops is not None:
                gnd = min((math.hypot(q["x"] - p["x"], q["y"] - p["y"])
                           for p in pads if p["net"] in GROUNDS
                           for q in by_ref[ic] if q["net"] == p["net"]), default=0.0)
                loops[ref] = best + gnd
    return dists


def main() -> None:
    args = [a for a in sys.argv[1:]]
    board = BOARD
    if "--board" in args:
        board = Path(args[args.index("--board") + 1])
        del args[args.index("--board"):args.index("--board") + 2]
    moves_path = Path(args[0]) if args else HERE / "placement_moves.json"
    spec = json.loads(moves_path.read_text())
    work = Path(tempfile.mkdtemp(prefix="pilot-opt-"))
    for name in ("Pilot.kicad_pro", "Pilot.kicad_dru", "Pilot.kicad_sch", "Pilot.kicad_sym",
                 "sym-lib-table", "fp-lib-table"):
        src = board.parent / name
        if src.exists():
            (work / name).write_text(src.read_text())
    # fp-lib-table uses ${KIPRJMOD}/../../Serenity-Custom.pretty — keep that resolvable
    custom = str(board.parent.parent.parent / "Serenity-Custom.pretty")
    (work / "fp-lib-table").write_text((board.parent / "fp-lib-table").read_text().replace(
        "${KIPRJMOD}/../../Serenity-Custom.pretty", custom))
    pcb = work / "Pilot.kicad_pcb"
    pcb.write_text(strip_routing(apply_moves(board.read_text(), spec)))
    rep = work / "drc.json"
    subprocess.run(["kicad-cli", "pcb", "drc", "--severity-all", "--schematic-parity",
                    "--format", "json", "--output", str(rep), str(pcb)],
                   capture_output=True, check=True)
    d = json.loads(rep.read_text())
    # review findings #2: every gate input must be present — a missing key fails, not passes
    errors = [v for v in d["violations"] if v["severity"] == "error"]
    parity = d["schematic_parity"]
    g = geometry(pcb)
    if len(g["band"]) < 3:
        raise SystemExit("ISO_BAND In1 outline not found — plane_pads_in_band would read 0")
    loops: dict = {}
    dists = capfit(g, loops)
    missing = [r for r in ISO_HF if r not in dists]
    if missing:
        raise SystemExit(f"ISO HF caps not scored: {missing}")
    if len(dists) < EXPECTED_CAPS:
        raise SystemExit(f"only {len(dists)} caps scored, expected >= {EXPECTED_CAPS}")
    in_band = sum(1 for p in g["pads"] if p["net"] in ("GND", "+3V3")
                  and in_poly(p["x"], p["y"], g["band"])
                  and not p["ref"].startswith(("PB2-", "H")))
    out = dict(drc_errors=len(errors), parity_issues=len(parity),
               capfit_sum_mm=round(sum(dists.values()), 3),
               capfit_loop_sum_mm=round(sum(loops.values()), 3),
               caps_scored=len(dists),
               caps_over_1p5mm=sum(1 for v in dists.values() if v > 1.5),
               iso_hf_max_mm=round(max(dists[r] for r in ISO_HF), 3),
               plane_pads_in_band=in_band,
               error_types=sorted({v["type"] for v in errors}))
    print(json.dumps(out))


if __name__ == "__main__":
    main()
