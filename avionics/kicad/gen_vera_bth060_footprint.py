#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_vera_bth060_footprint.py -- clean-room carrier footprint for the PHYTEC
phyCORE-AM62x PCM-071 SoM: 2x Samtec BTH-060-01-L-D-A land patterns + M2.5
mounting holes + connector alignment NPTH.
=============================================================================
Land pattern from the Samtec drawing "RECOMMENDED PCB LAYOUT FOR BTH-XXX-XX-X-D-XX"
Rev D (bth-xxx-xx-x-d-xx-footprint.pdf, Fig 1, BTH-060 shown; Table 1):
  * pitch          0.5000 mm (TYP)
  * pad width      0.305 mm (0.0120", along the pitch/row direction)
  * pad length     1.35 mm (radial; drawing shows ~.057[1.448] connector pad region)
  * row spacing    1.986 mm (0.0782" REF, row 01 <-> row 02 centrelines)
  * pad span "B"   29.507 mm (first..last pad centre, 60 pos)
  * align "A"      33.482 mm (2x NPTH per connector, along the length)
  * align hole     0.0400" [1.016] NPTH (the "-A" option in BTH-060-01-L-D-A-K-TR)
Module outline 32x43 mm; 2 connectors 22.4 mm apart; 2x M2.5 corner holes -- from the
PHYTEC HW manual Figs 3/6/7.

Pad names A1..A60/B1..B60/C1..C60/D1..D60 match Vera_SoM_PCM071.kicad_sym so the
symbol associates 1:1.  ROW<->COLUMN assignment (A=right-outer, B=right-inner,
C=left-inner, D=left-outer) and pin-1 end are a best reading of the manual's Fig 6 --
PRE-FAB GATE: verify against the Samtec product print + PHYTEC Fig 6 before routing.

Output: Vera.pretty/phyCORE-AM62x_PCM071_2xBTH-060.kicad_mod

Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  (Griffing Technology LLC)
AI-assist: Claude Opus 4.8 (Anthropic) -- footprint authoring, 2026-07-12.
License: CC BY 4.0
"""

import uuid
from pathlib import Path

OUT = Path(__file__).resolve().parent / "Vera.pretty" / "phyCORE-AM62x_PCM071_2xBTH-060.kicad_mod"

PITCH = 0.5
PADW = 0.305          # along the row (Y)
PADL = 1.35           # radial (X)
ROW = 1.986           # row 01<->02 centreline spacing
NPOS = 60
SPAN = (NPOS - 1) * PITCH      # 29.5 (~ "B" 29.507)
ALIGN = 33.482                  # "A"
ALIGN_D = 1.016
CONN_DX = 11.2        # connector centre offset from module centre (22.4 apart)
MH = (13.2, 18.7)     # M2.5 corner-ish mounting holes (manual Fig 3/7)


def u():
    return str(uuid.uuid4())


def pad_smd(name, x, y):
    return (f'  (pad "{name}" smd roundrect (at {x:.4f} {y:.4f}) '
            f'(size {PADL} {PADW}) (layers "F.Cu" "F.Mask" "F.Paste") '
            f'(roundrect_rratio 0.25) (uuid "{u()}"))')


def npth(x, y, d):
    return (f'  (pad "" np_thru_hole circle (at {x:.4f} {y:.4f}) (size {d} {d}) '
            f'(drill {d}) (layers "*.Cu" "*.Mask") (uuid "{u()}"))')


def mhole(name, x, y):
    return (f'  (pad "{name}" np_thru_hole circle (at {x:.4f} {y:.4f}) '
            f'(size 2.7 2.7) (drill 2.7) (layers "*.Cu" "*.Mask") (uuid "{u()}"))')


def main():
    L = ["(footprint \"phyCORE-AM62x_PCM071_2xBTH-060\" (version 20240108) "
         "(generator \"serenity_vera\")",
         '  (layer "F.Cu")',
         '  (descr "PHYTEC phyCORE-AM62x PCM-071 carrier footprint: 2x Samtec '
         'BTH-060-01-L-D-A (0.5mm, 2x60) + 2x M2.5 holes. Land pattern from Samtec '
         'BTH-XXX-XX-X-D-XX Rev D; module dims from PHYTEC L-1038e.A5. Pad names '
         'A1..D60 match Vera_SoM_PCM071. Verify row<->column + pin-1 vs Fig 6.")',
         "  (attr smd)",
         f'  (property "Reference" "U**" (at 0 -23 0) (layer "F.SilkS")'
         f' (uuid "{u()}") (effects (font (size 1 1) (thickness 0.15))))',
         f'  (property "Value" "phyCORE-AM62x_PCM071" (at 0 23 0) (layer "F.Fab")'
         f' (uuid "{u()}") (effects (font (size 1 1) (thickness 0.15))))',
         # module + courtyard + silk outline (32 x 43)
         f'  (fp_rect (start -16 -21.5) (end 16 21.5) (stroke (width 0.12)'
         f' (type solid)) (fill none) (layer "F.Fab") (uuid "{u()}"))',
         f'  (fp_rect (start -16.5 -22) (end 16.5 22) (stroke (width 0.05)'
         f' (type solid)) (fill none) (layer "F.CrtYd") (uuid "{u()}"))']
    # two connectors: right = A(outer)/B(inner), left = C(inner)/D(outer)
    # rows run along Y (0.5mm pitch, 60), radial (X) rows at connector_cx +/- ROW/2
    banks = {
        "A": (+CONN_DX + ROW / 2), "B": (+CONN_DX - ROW / 2),
        "C": (-CONN_DX + ROW / 2), "D": (-CONN_DX - ROW / 2),
    }
    y0 = -SPAN / 2
    for col, xrow in banks.items():
        for n in range(NPOS):
            L.append(pad_smd(f"{col}{n + 1}", xrow, y0 + n * PITCH))
    # 4 connector alignment NPTH (2 per connector, at +/- ALIGN/2 along Y)
    for cx in (+CONN_DX, -CONN_DX):
        L.append(npth(cx, -ALIGN / 2, ALIGN_D))
        L.append(npth(cx, +ALIGN / 2, ALIGN_D))
    # 2 M2.5 corner mounting holes (lower-left / upper-right)
    L.append(mhole("MH1", -MH[0], -MH[1]))
    L.append(mhole("MH2", +MH[0], +MH[1]))
    L.append(")")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {OUT.name}: {4 * NPOS} SMD pads + 4 align NPTH + 2 M2.5")


if __name__ == "__main__":
    main()
