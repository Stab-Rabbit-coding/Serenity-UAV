#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_vera_ds_footprints.py -- CLEAN-ROOM direct-solder land footprints for Vera's
nose sensor interface (camera / ToF / laser), as an alternative to the JST
connectors for the cargo install.
=============================================================================
Design intent (docs/VERA_MANUFACTURING_READINESS.md Section 4): for each of the
three nose apertures (camera / ToF / laser, per bow_sensor_pod.scad CAM_POS /
TOF_POS / laser centreline), Vera carries BOTH a JST connector AND a co-located
direct-solder land on the SAME nets.  Populate exactly one per build:
  * Cargo install -> populate the JST connector (cabled), DNP the land.
  * Nose install  -> populate the direct-solder land (module leads/flex solder
    flush, aligned to the sensor mounting plate), DNP the JST connector.

These lands are our own geometry (a simple SMD pad row for hand/reflow soldering
of the module's flex or wire tails).  Pad 1 is marked.  1.0 mm pitch, 0.7 x 1.6 mm
pads.  Pad<->signal order matches the matching JST group (see the schematic /
mod_vera_ds_pcb.py):
  DS_Camera_9P : 1 CSI_CLK_P 2 CSI_CLK_N 3 CSI_D0_P 4 CSI_D0_N 5 CAM_SDA
                 6 CAM_SCL 7 CAM_RESET_N 8 +3V3 9 GND
  DS_ToF_4P    : 1 +5V 2 GND 3 UART_TOF_TX 4 UART_TOF_RX
  DS_Laser_2P  : 1 +5V 2 LASER_CATHODE

Output: Vera.pretty/DS_Camera_9P.kicad_mod, DS_ToF_4P.kicad_mod, DS_Laser_2P.kicad_mod

Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  (Griffing Technology LLC)
AI-assist: Claude Opus 4.8 (Anthropic) -- footprint authoring, 2026-07-12.
License: CC BY 4.0
"""

import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRETTY = HERE / "Vera.pretty"

PITCH = 1.0
PAD_W = 0.7
PAD_H = 1.6


def _u():
    return str(uuid.uuid4())


def make(name, npads):
    span = (npads - 1) * PITCH
    x0 = -span / 2.0
    hw = span / 2.0 + PAD_W / 2.0 + 0.6  # silk/courtyard half-width
    hh = PAD_H / 2.0 + 0.6
    lines = [
        f'(footprint "{name}" (version 20240108) (generator "serenity_vera_ds")',
        '  (layer "F.Cu")',
        "  (attr smd)",
        f'  (property "Reference" "REF**" (at 0 {-hh - 0.8:.2f} 0) '
        '(layer "F.SilkS")',
        f'    (uuid "{_u()}") (effects (font (size 1 1) (thickness 0.15))))',
        f'  (property "Value" "{name}" (at 0 {hh + 0.8:.2f} 0) (layer "F.Fab")',
        f'    (uuid "{_u()}") (effects (font (size 1 1) (thickness 0.15))))',
    ]
    for i in range(npads):
        px = x0 + i * PITCH
        lines.append(
            f'  (pad "{i + 1}" smd roundrect (at {px:.3f} 0) '
            f"(size {PAD_W} {PAD_H}) "
            '(layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) '
            f'(uuid "{_u()}"))'
        )
    # pad-1 triangle marker on silk (left of pad 1)
    m = x0 - PAD_W / 2.0 - 0.35
    lines += [
        f"  (fp_poly (pts (xy {m:.2f} -0.4) (xy {m:.2f} 0.4) (xy {m + 0.5:.2f} 0))"
        ' (stroke (width 0.12) (type solid)) (fill solid) (layer "F.SilkS")'
        f' (uuid "{_u()}"))',
        # courtyard
        f"  (fp_rect (start {-hw:.2f} {-hh:.2f}) (end {hw:.2f} {hh:.2f})"
        ' (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd")'
        f' (uuid "{_u()}"))',
        # fab outline
        f"  (fp_rect (start {-hw + 0.3:.2f} {-hh + 0.3:.2f}) "
        f"(end {hw - 0.3:.2f} {hh - 0.3:.2f})"
        ' (stroke (width 0.1) (type solid)) (fill none) (layer "F.Fab")'
        f' (uuid "{_u()}"))',
        ")",
    ]
    out = PRETTY / f"{name}.kicad_mod"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out.name} ({npads} pads, {span:.1f} mm row)")


def main():
    PRETTY.mkdir(exist_ok=True)
    make("DS_Camera_9P", 9)
    make("DS_ToF_4P", 4)
    make("DS_Laser_2P", 2)


if __name__ == "__main__":
    main()
