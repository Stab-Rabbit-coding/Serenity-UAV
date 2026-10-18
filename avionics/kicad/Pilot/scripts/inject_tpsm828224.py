#!/usr/bin/python3
"""inject_tpsm828224.py — swap the Pilot 3V3 buck to the TI TPSM828224SILR in place.

Usage:
    /usr/bin/python3 inject_tpsm828224.py <in.kicad_pcb> <out.kicad_pcb>

Why an injection and not a regeneration
---------------------------------------
The board carries the owner's hand placement and manual routing (2026-10-09
onward), so ``gen_pilot_pcb.py`` must not be re-run over it (generator drift;
see ``avionics/kicad/Pilot/Pilot.md``).  This script applies only the part swap
that ``gen_pilot_sch.py`` made on 2026-10-17 (S. Griffing decision; script by
Claude Opus 5.5):

* ``U-3V3``  TPS62933DRLR (SOT-583-8) -> TPSM828224SILR
  (``Serenity-Custom:TI_SIL0010D_uSiP-10_2.0x2.5mm_P0.5mm``), same pose.
  Pin nets per TI SLVSEP0F Table 6-1 [REF-PWR-008]: VIN 1/2 and EN 3 = +5V,
  PG 4 = no net, VOUT 5/6/7 and FB 8 = +3V3, GND 9/10.
* ``C-3V3-IN`` and ``C-3V3-O1/O2`` 0805 -> 0603 22 uF 6.3 V X6S (Taiyo Yuden
  MSASJ168BC6226MTNA01, DC-bias checked [REF-PWR-011]), same poses and sides.
* Removed: ``R-EN3``, ``C-BST``, ``C-SS``, ``L-3V3``, ``R-FB3H``, ``R-FB3L``, and
  every track / via on their now-deleted nets (SW_3V3, BST_3V3, SS_3V3,
  FB_3V3, U3V3_EN).

Tracks and vias that fall inside the new ``U-3V3`` courtyard are deleted: they
were the old SOT-583 escapes and would short the module's 0.5 mm-pitch pads.
Other copper on +5V / +3V3 / GND that ran to the old pads is left in place for
the owner to re-route; DRC reports it as dangling.

pcbnew 9.0.2 segfaults on FootprintLoad after a board Remove
(``PCBNEW_SWIG_BUG.md``), so every new footprint is loaded BEFORE anything is
removed.  The input board is never modified.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pcbnew

# Library roots.  Serenity-Custom resolves the same way the project
# fp-lib-table does (${KIPRJMOD}/../../Serenity-Custom.pretty).
HERE = Path(__file__).resolve().parent
CUSTOM = str(HERE.parent.parent / "Serenity-Custom.pretty")
CAPS = "/usr/share/kicad/footprints/Capacitor_SMD.pretty"

# ref -> (library path, footprint name, new value, {pad number: net name or None})
# The library nickname for each path (FootprintLoad drops it; parity needs it).
NICK = {CUSTOM: "Serenity-Custom", CAPS: "Capacitor_SMD"}
SWAPS: dict = {
    "U-3V3": (CUSTOM, "TI_SIL0010D_uSiP-10_2.0x2.5mm_P0.5mm", "TPSM828224SILR",
              {"1": "+5V", "2": "+5V", "3": "+5V", "4": None,
               "5": "+3V3", "6": "+3V3", "7": "+3V3", "8": "+3V3",
               "9": "GND", "10": "GND"}),
    "C-3V3-IN": (CAPS, "C_0603_1608Metric", "22uF 6.3V X6S", {"1": "+5V", "2": "GND"}),
    "C-3V3-O1": (CAPS, "C_0603_1608Metric", "22uF 6.3V X6S", {"1": "+3V3", "2": "GND"}),
    "C-3V3-O2": (CAPS, "C_0603_1608Metric", "22uF 6.3V X6S", {"1": "+3V3", "2": "GND"}),
}
REMOVE = ["R-EN3", "C-BST", "C-SS", "L-3V3", "R-FB3H", "R-FB3L"]
DEAD_NETS = {"SW_3V3", "BST_3V3", "SS_3V3", "FB_3V3", "U3V3_EN"}


def main() -> int:
    """Load, swap, remove, save to the output path; returns a shell exit code."""
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    src, dst = sys.argv[1], sys.argv[2]
    if Path(src).resolve() == Path(dst).resolve():
        print("refusing to overwrite the input board")
        return 2
    board = pcbnew.LoadBoard(src)

    # 1. Load every replacement footprint first (pcbnew 9.0.2 SWIG bug).
    loaded = {ref: pcbnew.FootprintLoad(lib, name) for ref, (lib, name, _v, _n) in SWAPS.items()}
    for ref, fp in loaded.items():
        if fp is None:
            print(f"footprint for {ref} failed to load")
            return 1

    # 2. Place each replacement on the old part's pose and side, carrying the
    #    schematic link (path / sheet) so parity still matches.
    old_fps = []
    for ref, (lib, name, value, pads) in SWAPS.items():
        old = board.FindFootprintByReference(ref)
        if old is None:
            print(f"{ref} not on the board")
            return 1
        new = loaded[ref]
        board.Add(new)
        if old.IsFlipped():
            new.Flip(new.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
        new.SetPosition(old.GetPosition())
        new.SetOrientation(old.GetOrientation())
        new.SetFPID(pcbnew.LIB_ID(NICK[lib], name))
        new.SetReference(ref)
        new.SetValue(value)
        new.SetPath(old.GetPath())
        new.SetSheetname(old.GetSheetname())
        new.SetSheetfile(old.GetSheetfile())
        for pad in new.Pads():
            net = pads.get(pad.GetNumber())
            if net:
                pad.SetNet(board.FindNet(net))
        old_fps.append(old)

    # 3. Remove superseded parts and the copper on their dead nets.
    dead = [t for t in board.GetTracks() if t.GetNetname() in DEAD_NETS]
    # Old SOT-583 escape copper under the new module (courtyard = keep-clear).
    crt = loaded["U-3V3"].GetCourtyard(pcbnew.F_CrtYd)
    under = [t for t in board.GetTracks()
             if t not in dead and (t.Type() == pcbnew.PCB_VIA_T or t.GetLayer() == pcbnew.F_Cu)
             and crt.Collide(t.GetEffectiveShape(), 0)]
    dead += under
    for t in dead:
        board.Remove(t)
    for ref in REMOVE:
        fp = board.FindFootprintByReference(ref)
        if fp is not None:
            old_fps.append(fp)
    for fp in old_fps:
        board.Remove(fp)

    board.Save(dst)
    print(f"swapped {len(SWAPS)}, removed {len(REMOVE)} parts and {len(dead)} dead-net copper items -> {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
