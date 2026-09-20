#!/usr/bin/env python3
"""gen_fe_footprints.py — Author the project-custom land patterns FlightEngineer needs.

Writes into ``avionics/kicad/Serenity-Custom.pretty`` (shared with Pilot/XO).
Most FlightEngineer connectors/passives use REAL, EXACT KiCad system footprints
(AMASS XT30PW-F/XT60PW-F, Molex Nano-Fit, JST-GH, JST-XH — all confirmed
present in the installed KiCad 9 system libraries by filename match against
the exact MPNs FlightEngineer.md cites). Only a handful of mechanical items
with no off-the-shelf KiCad footprint are authored here:

* ``MAXI_Blade_Fuseholder_2P``   Littelfuse 0297150.ZXNV (150 A MAXI blade,
                                 F1) — system lib only has ATO/Mini blade
                                 holders; MAXI is a larger 2-pin THT blade
                                 fuse land, dims per Littelfuse's generic
                                 MAXI mechanical envelope (29.2 x 24.4 mm
                                 body). NOT pixel-verified against a specific
                                 holder P/N — flagged.
* ``Wurth_7440640500_CMC_THT``  Würth WE-CMB 7440640500 (10 A, 2x100 uH
                                 common-mode choke, THT) — used 7x on this
                                 board (CM1, CM2, CM_ESC1-4). No exact KiCad
                                 footprint in the system libraries; land is a
                                 reasonable 4-pin THT estimate from Würth's
                                 typical WE-CMB mechanical family, flagged
                                 not pixel-verified.
* ``M3_Chassis_Lug_PGND``       M3 x 6mm PCB-mount threaded brass insert
                                 (McMaster-Carr 94459A120) used for every
                                 J_PGND_BATT / J_SHLD_ESCn / J_CHASSIS pad —
                                 single-pad THT land sized for the insert's
                                 barrel, PGND-labelled per FlightEngineer.md's
                                 own "M3 threaded brass insert" callout.
* ``PGND_ViaPad_1p2mm``         1.2 mm drilled / 2.0 mm annular via-pad for
                                 the J_SHLD_5V/6V/I2C/ALERT/NTC shield drains,
                                 per FlightEngineer.md's own spec.

Author: Claude Sonnet 5, 2026-09-20.  Owner: sgriffing.  License: CC BY 4.0.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

HERE = Path(__file__).resolve().parent
LIB = HERE.parent.parent / "Serenity-Custom.pretty"


def hdr(name: str, descr: str, smd: bool = False) -> List[str]:
    attr = "smd" if smd else "through_hole"
    return [
        f'(footprint "{name}"',
        "\t(version 20241229)",
        '\t(generator "gen_fe_footprints.py")',
        '\t(generator_version "9.0")',
        '\t(layer "F.Cu")',
        f'\t(descr "{descr}")',
        f'\t(tags "Serenity FlightEngineer {name}")',
        f"\t(attr {attr})",
        '\t(property "Reference" "REF**" (at 0 -2 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
        f'\t(property "Value" "{name}" (at 0 2 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))',
        '\t(property "Datasheet" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))',
        '\t(property "Description" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))',
    ]


def rect(layer: str, x1: float, y1: float, x2: float, y2: float, w: float = 0.1) -> str:
    return (f'\t(fp_rect (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) '
            f'(stroke (width {w}) (type default)) (fill no) (layer "{layer}"))')


def tht_pad(num: str, x: float, y: float, d: float, drill: float, shape: str = "circle") -> str:
    return (f'\t(pad "{num}" thru_hole {shape} (at {x:.3f} {y:.3f}) (size {d:.3f} {d:.3f}) '
            f'(drill {drill:.3f}) (layers "*.Cu" "*.Mask"))')


def write(name: str, body: List[str]) -> None:
    (LIB / f"{name}.kicad_mod").write_text("\n".join(body + [")"]) + "\n")
    print("wrote", name)


def maxi_fuseholder() -> None:
    name = "MAXI_Blade_Fuseholder_2P"
    b = hdr(name, "MAXI blade fuse holder, 2-pin THT, ~29.2 x 24.4 mm body envelope "
                  "(Littelfuse MAXI mechanical family; F1 150A per FlightEngineer.md) — "
                  "not pixel-verified against a specific holder P/N, flagged")
    b.append(rect("F.Fab", -14.6, -12.2, 14.6, 12.2))
    b.append(rect("F.CrtYd", -15.0, -12.6, 15.0, 12.6, 0.05))
    b.append(tht_pad("1", -10.0, 0, 3.5, 2.2, "oval"))
    b.append(tht_pad("2", 10.0, 0, 3.5, 2.2, "oval"))
    write(name, b)


def cmc_choke_tht() -> None:
    name = "Wurth_7440640500_CMC_THT"
    b = hdr(name, "Wurth WE-CMB 7440640500, 10A, 2x100uH common-mode choke, 4-pin THT, "
                  "estimated land from Würth's typical WE-CMB mechanical family — not "
                  "pixel-verified, flagged")
    b.append(rect("F.Fab", -8.0, -6.0, 8.0, 6.0))
    b.append(rect("F.CrtYd", -8.4, -6.4, 8.4, 6.4, 0.05))
    for i, (x, y) in enumerate([(-6.0, -4.0), (6.0, -4.0), (-6.0, 4.0), (6.0, 4.0)], start=1):
        b.append(tht_pad(str(i), x, y, 1.8, 1.0))
    write(name, b)


def aon6260_dfn5x6() -> None:
    name = "AOSMD_DFN5x6-8L"
    b = hdr(name, "AOSMD DFN5x6-8L single N-channel MOSFET land (AON6260/AON6554/AON6558 family): "
                  "3 Source (pins 1-3) + Gate (pin 4) + 4 Drain (pins 5-8), large Drain exposed pad — "
                  "standard AOSMD DFN5x6 convention (aon6260.pdf p.1 'PIN1...S' + package marking), "
                  "no KiCad system land matches this exact 5x6mm body, flagged not pixel-verified", smd=True)
    hx, hy = 2.5, 3.0
    b.append(rect("F.Fab", -hx, -hy, hx, hy))
    b.append(rect("F.CrtYd", -hx - 0.5, -hy - 0.5, hx + 0.5, hy + 0.5, 0.05))
    # bottom edge: 3 Source pads
    for i, x in enumerate((-1.5, 0.0, 1.5)):
        b.append(f'\t(pad "{1+i}" smd rect (at {x:.3f} {-hy - 0.3:.3f}) (size 0.6 0.8) (layers "F.Cu" "F.Paste" "F.Mask"))')
    # top-left: Gate pad
    b.append(f'\t(pad "4" smd rect (at {-1.6:.3f} {hy + 0.3:.3f}) (size 0.6 0.8) (layers "F.Cu" "F.Paste" "F.Mask"))')
    # top edge: 4 Drain tab pads (5-8), separate from the gate pad
    for i, num in enumerate((5, 6, 7, 8)):
        x = -0.3 + i * 0.7
        b.append(f'\t(pad "{num}" smd rect (at {x:.3f} {hy + 0.3:.3f}) (size 0.5 0.8) (layers "F.Cu" "F.Paste" "F.Mask"))')
    # large exposed-pad Drain (same net as 5-8) under the die
    b.append(f'\t(pad "9" smd rect (at 0 0) (size {2*hx-0.6} {2*hy-1.6}) (layers "F.Cu" "F.Paste" "F.Mask"))')
    write(name, b)


def tps54620_vqfn14() -> None:
    name = "Texas_RGY0014A_VQFN-14-1EP_3.5x3.5mm"
    b = hdr(name, "TI RGY0014A VQFN-14, 3.5x3.5mm, 0.65mm pitch, EP ~2.1x2.1mm (tps54620.pdf mechanical "
                  "package). No exact KiCad system land (only a 2.5x3mm DHVQFN-14 exists) — pad geometry "
                  "pattern-matched from KiCad's other 0.65mm-pitch small QFN families, flagged not "
                  "pixel-verified", smd=True)
    half = 3.5 / 2
    b.append(rect("F.Fab", -half, -half, half, half))
    b.append(rect("F.CrtYd", -half - 0.5, -half - 0.5, half + 0.5, half + 0.5, 0.05))
    pitch = 0.65
    for i in range(4):
        x = -1.5 * pitch + i * pitch
        b.append(f'\t(pad "{1+i}" smd roundrect (at {x:.3f} {-half - 0.25:.3f}) (size 0.35 0.5) '
                  f'(layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.25))')
    for i in range(4):
        y = -1.5 * pitch + i * pitch
        b.append(f'\t(pad "{5+i}" smd roundrect (at {half + 0.25:.3f} {y:.3f}) (size 0.5 0.35) '
                  f'(layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.25))')
    for i in range(3):
        x = pitch - i * pitch
        b.append(f'\t(pad "{9+i}" smd roundrect (at {x:.3f} {half + 0.25:.3f}) (size 0.35 0.5) '
                  f'(layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.25))')
    for i in range(3):
        y = pitch - i * pitch
        b.append(f'\t(pad "{12+i}" smd roundrect (at {-half - 0.25:.3f} {y:.3f}) (size 0.5 0.35) '
                  f'(layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.25))')
    b.append(f'\t(pad "15" smd rect (at 0 0) (size 2.1 2.1) (layers "F.Cu" "F.Paste" "F.Mask"))')
    write(name, b)


def m3_chassis_lug() -> None:
    name = "M3_Chassis_Lug_PGND"
    b = hdr(name, "M3 x 6mm PCB-mount threaded brass insert (McMaster-Carr 94459A120), "
                  "PGND chassis lug pad per FlightEngineer.md's connector shield spec")
    b.append(rect("F.Fab", -3.0, -3.0, 3.0, 3.0))
    b.append(rect("F.CrtYd", -3.5, -3.5, 3.5, 3.5, 0.05))
    b.append(tht_pad("1", 0, 0, 5.0, 3.2))
    write(name, b)


def pgnd_via_pad() -> None:
    name = "PGND_ViaPad_1p2mm"
    b = hdr(name, "1.2mm drilled / 2.0mm annular via-pad, PGND shield drain per "
                  "FlightEngineer.md's connector shield spec")
    b.append(rect("F.CrtYd", -1.3, -1.3, 1.3, 1.3, 0.05))
    b.append(tht_pad("1", 0, 0, 2.0, 1.2))
    write(name, b)


def main() -> None:
    LIB.mkdir(parents=True, exist_ok=True)
    maxi_fuseholder()
    cmc_choke_tht()
    aon6260_dfn5x6()
    tps54620_vqfn14()
    m3_chassis_lug()
    pgnd_via_pad()


if __name__ == "__main__":
    main()
