#!/usr/bin/env python3
"""gen_pilot_footprints.py — Author the project-custom land patterns Pilot needs.

Writes KiCad 9 ``.kicad_mod`` files into ``avionics/kicad/Serenity-Custom.pretty``.
Every land pattern below is transcribed from the OEM datasheet's recommended
land pattern / package outline in ``avionics/datasheets/`` (authoritative per
``avionics/AGENTS.md`` §6-7).  Where a datasheet gives only the package outline,
the pad is drawn per its bottom-view terminal geometry and noted as such.

Footprints and sources
----------------------
* ``Samtec_TSM-108-01-x-DV``      samtec_tsm-dv-footprint.pdf Rev F Fig 1 (pads 1.27 x 3.68,
                                  1.27 gap, 2.54 pitch); body per samtec_tsm_catalog.pdf.  [REF-CONN-001]
* (Samtec SSM-1xx-DV SMT sockets were evaluated for the PB2 rails and REJECTED:
  samtec_ssm_footprint.pdf Fig 4 puts the outer pad edge 3.935 mm from the rail
  centre-line, but the PB2 rails are 2.54 mm from the cape edge -> pads 1.4 mm
  off-board.  Rails stay THT.)
* ``uBlox_SAM-M10Q-00B``          SAM-M10Q_DataSheet_UBX-22013293.pdf §6 Fig 4 /
                                  Table 19 (A 15.5, B 7.6 -> pitch 1.9, J 13.2,
                                  H 1.7 x I 1.5), §3.1 Fig 2 pin order.  [REF-SENSOR-027]
* ``Wurth_749010012A_WE-LAN``     749010012A.pdf p.1 "Recommended Land Pattern":
                                  2 x 8 pads 0.64 x 1.91, pitch 1.27, row span 8.77,
                                  body 12.2 x 7.0.  [REF-SENSOR-028]
* ``Xfmr_1553_SMD_0.40in_8pin``  PremierMagnetics_DB2791S.pdf Fig 2 = SM1553-Series RevD p.1 "Recommended Pad Layout":
                                  pads .060 x .035 in, left column 3 @ .150 in,
                                  right column 5 @ .075 in, span .430 in; body .410 in.
                                  [REF-SENSOR-025]
* ``Bosch_BMP388_LGA-10_2x2mm``   bst-bmp388-ds001.pdf §7.1 Fig 26 (bottom view) —
                                  Bosch §7.2 says to use the outline as the land:
                                  side pads 0.275 x 0.250 @ x=±0.75, y=0/±0.5;
                                  end pads 0.250 x 0.275 @ x=±0.25, y=±0.75.
                                  Pin order §6.1 Fig 23.  [REF-SENSOR-023]
* ``X2Y_0805_4T``                 X2Y_15-2237598.pdf (Yageo) Table 3 / Fig 3, 0805:
                                  A 3.05, B 1.27, C 0.89, D 0.56, E 2.03.
* ``Bourns_SRF2012_4T``           SRF2012A.pdf "Recommended Layout": pads 1.1 x 0.45,
                                  x pitch 2.6, y span 1.25; pin 1 top-left, 2 top-right,
                                  3 bottom-right, 4 bottom-left.  [REF-SENSOR-026]
                                  (The superseded embedded land had pins 1 and 2 on
                                  the SAME end, which is not the part.)
* ``L_WE-MAPI_3015``              74438335033.pdf p.1 land: 2 pads 1.3 x 3.4, gap 0.8.
                                  [REF-PWR-003]
* ``Molex_NanoFit_1x04_Horizontal`` geometry carried over from the prior board
                                  (2.50 mm pitch THT, 1.5 mm pad / 1.0 mm drill);
                                  ** P/N 105313-1204 and land NOT datasheet-verified —
                                  no Nano-Fit drawing on disk (WBS §1.2a open gap). **
* ``PocketBeagle2_2x18_P1_Socket`` / ``_P2_Socket``  2 x 18, 2.54 mm, 1.7 mm pad /
                                  1.0 mm drill, carried over from the prior board
                                  (the PB2 cape rail geometry).

Author: Claude Opus 5, 2026-09-19.  Owner: sgriffing.  License: CC BY 4.0.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

HERE = Path(__file__).resolve().parent
LIB = HERE.parent.parent / "Serenity-Custom.pretty"


def hdr(name: str, descr: str, smd: bool = True) -> List[str]:
    attr = "smd" if smd else "through_hole"
    return [
        f'(footprint "{name}"',
        "\t(version 20241229)",
        '\t(generator "gen_pilot_footprints.py")',
        '\t(generator_version "9.0")',
        '\t(layer "F.Cu")',
        f'\t(descr "{descr}")',
        f'\t(tags "Serenity Pilot {name}")',
        f"\t(attr {attr})",
        f'\t(property "Reference" "REF**" (at 0 -1 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
        f'\t(property "Value" "{name}" (at 0 1 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))',
        '\t(property "Datasheet" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))',
        '\t(property "Description" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))',
    ]


def rect(layer: str, x1: float, y1: float, x2: float, y2: float, w: float = 0.1) -> str:
    return (f'\t(fp_rect (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) '
            f'(stroke (width {w}) (type default)) (fill no) (layer "{layer}"))')


def line(layer: str, x1: float, y1: float, x2: float, y2: float, w: float = 0.12) -> str:
    return (f'\t(fp_line (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) '
            f'(stroke (width {w}) (type default)) (layer "{layer}"))')


def circ(layer: str, x: float, y: float, r: float, w: float = 0.12) -> str:
    return (f'\t(fp_circle (center {x:.3f} {y:.3f}) (end {x + r:.3f} {y:.3f}) '
            f'(stroke (width {w}) (type default)) (fill no) (layer "{layer}"))')


def smd_pad(num: str, x: float, y: float, sx: float, sy: float, shape: str = "roundrect") -> str:
    rr = " (roundrect_rratio 0.25)" if shape == "roundrect" else ""
    return (f'\t(pad "{num}" smd {shape} (at {x:.3f} {y:.3f}) (size {sx:.3f} {sy:.3f}) '
            f'(layers "F.Cu" "F.Paste" "F.Mask"){rr})')


def tht_pad(num: str, x: float, y: float, d: float, drill: float, shape: str = "circle") -> str:
    return (f'\t(pad "{num}" thru_hole {shape} (at {x:.3f} {y:.3f}) (size {d:.3f} {d:.3f}) '
            f'(drill {drill:.3f}) (layers "*.Cu" "*.Mask"))')


def write(name: str, body: List[str]) -> None:
    (LIB / f"{name}.kicad_mod").write_text("\n".join(body + [")"]) + "\n")
    print("wrote", name)


def sam_m10q() -> None:
    name = "uBlox_SAM-M10Q-00B"
    b = hdr(name, "u-blox SAM-M10Q GNSS module, 20-pad LCC, 15.5 x 15.5 x 6.3 mm; land per UBX-22013293 §6 Fig 4 / Table 19, pin order §3.1 Fig 2")
    half = 15.5 / 2
    b.append(rect("F.Fab", -half, -half, half, half))
    b.append(rect("F.CrtYd", -half - 0.5, -half - 0.5, half + 0.5, half + 0.5, 0.05))
    b.append(rect("F.SilkS", -half - 0.15, -half - 0.15, half + 0.15, half + 0.15))
    b.append(circ("F.SilkS", -half - 0.8, -3.8 - 1.9 / 2 - 0.6, 0.25))
    # keep-out for the patch antenna reference: no copper inside E=11.1 square except GND paddle
    pc = 6.75            # pad centre offset from module centre (pad from 5.75 to 7.75)
    pitch = 1.9
    # left column pins 1-5 top->bottom, bottom row 6-10 left->right,
    # right column 11-15 bottom->top, top row 16-20 right->left (top view, CCW)
    pads: List[Tuple[str, float, float, float, float]] = []
    for i in range(5):
        y = -2 * pitch + i * pitch
        pads.append((str(1 + i), -pc, y, 2.0, 1.5))          # left (pad 2.0 wide radial x 1.5 tall)
    for i in range(5):
        x = -2 * pitch + i * pitch
        pads.append((str(6 + i), x, pc, 1.5, 2.0))           # bottom
    for i in range(5):
        y = 2 * pitch - i * pitch
        pads.append((str(11 + i), pc, y, 2.0, 1.5))          # right
    for i in range(5):
        x = 2 * pitch - i * pitch
        pads.append((str(16 + i), x, -pc, 1.5, 2.0))         # top
    for num, x, y, sx, sy in pads:
        b.append(smd_pad(num, x, y, sx, sy))
    b.append('\t(zone (net 0) (net_name "") (layers "F.Cu") (name "SAM_no_copper") (hatch edge 0.5) (priority 10) '
             '(connect_pads (clearance 0)) (min_thickness 0.25) (keepout (tracks not_allowed) (vias not_allowed) '
             '(pads allowed) (copperpour not_allowed) (footprints not_allowed)) (fill (thermal_gap 0.5) (thermal_bridge_width 0.5)) '
             '(polygon (pts (xy -5.55 -5.55) (xy 5.55 -5.55) (xy 5.55 5.55) (xy -5.55 5.55))))')
    write(name, b)


def we_lan() -> None:
    name = "Wurth_749010012A_WE-LAN"
    b = hdr(name, "Wurth 749010012A WE-LAN 10/100Base-TX SMT transformer, 16-pad SOIC-style 1.27 mm, land per datasheet p.1")
    b.append(rect("F.Fab", -6.1, -3.5, 6.1, 3.5))
    b.append(rect("F.CrtYd", -6.4, -5.6, 6.4, 5.6, 0.05))
    b.append(line("F.SilkS", -6.25, -3.2, 6.25, -3.2))
    b.append(line("F.SilkS", -6.25, 3.2, 6.25, 3.2))
    b.append(circ("F.SilkS", -5.5, 5.9, 0.2))
    row = 8.77 / 2
    for i in range(8):
        x = -3.5 * 1.27 + i * 1.27
        b.append(smd_pad(str(1 + i), x, row, 0.64, 1.91))      # bottom row 1..8 left->right
        b.append(smd_pad(str(16 - i), x, -row, 0.64, 1.91))    # top row 16..9 left->right
    write(name, b)


def sm1553() -> None:
    name = "Xfmr_1553_SMD_0.40in_8pin"
    inch = 25.4
    b = hdr(name, "MIL-STD-1553 SMD isolation transformer, 0.40 in body, 8 gull-wing leads (3 @ 0.150 in left, 5 @ 0.075 in right, 0.430 in span): Premier Magnetics PM-DB2791S (Fig 2) and Vanguard SM1553 (RevD p.1) share this land")
    body = 0.410 * inch / 2
    b.append(rect("F.Fab", -body, -body, body, body))
    b.append(rect("F.CrtYd", -6.6, -5.6, 6.6, 5.6, 0.05))
    col = 0.430 * inch / 2
    sx, sy = 0.060 * inch, 0.035 * inch
    # Silk outline: horizontal top/bottom segments clear the pad rows (pads
    # reach y=+/-4.255, body edge is y=+/-5.207); the vertical sides would run
    # straight through the pad columns (pads span x=4.699..6.223, crossing the
    # body-edge line at x=+/-5.207), so those are left off rather than clipped
    # by solder mask.  Corner ticks mark the body width without the overlap.
    b.append(line("F.SilkS", -body, -body, body, -body))
    b.append(line("F.SilkS", -body, body, body, body))
    b.append(line("F.SilkS", -body, -body, -body, -body + 0.5))
    b.append(line("F.SilkS", -body, body, -body, body - 0.5))
    b.append(line("F.SilkS", body, -body, body, -body + 0.5))
    b.append(line("F.SilkS", body, body, body, body - 0.5))
    b.append(circ("F.Fab", -body - 0.4, -0.150 * inch - 1.2, 0.2))
    for i, y_in in enumerate((0.150, 0.0, -0.150)):        # pins 1,2,3 top->bottom (left)
        b.append(smd_pad(str(1 + i), -col, -y_in * inch, sx, sy))
    for i, y_in in enumerate((0.150, 0.075, 0.0, -0.075, -0.150)):  # pins 8..4 top->bottom (right)
        b.append(smd_pad(str(8 - i), col, -y_in * inch, sx, sy))
    write(name, b)


def bmp388() -> None:
    name = "Bosch_BMP388_LGA-10_2x2mm"
    b = hdr(name, "Bosch BMP388 10-pin metal-lid LGA 2.0 x 2.0 x 0.75 mm; land = package bottom view per BST-BMP388-DS001 §7.1/7.2")
    b.append(rect("F.Fab", -1.0, -1.0, 1.0, 1.0))
    b.append(rect("F.CrtYd", -1.35, -1.35, 1.35, 1.35, 0.05))
    b.append(line("F.SilkS", -1.15, -1.15, 1.15, -1.15))
    b.append(line("F.SilkS", -1.15, 1.15, 1.15, 1.15))
    b.append(circ("F.SilkS", 1.45, -1.45, 0.15))
    # top view, KiCad y-down.  pin1 top-right.
    pads = {
        "1": (0.25, -0.75, 0.25, 0.275), "2": (-0.25, -0.75, 0.25, 0.275),
        "3": (-0.75, -0.5, 0.275, 0.25), "4": (-0.75, 0.0, 0.275, 0.25), "5": (-0.75, 0.5, 0.275, 0.25),
        "6": (-0.25, 0.75, 0.25, 0.275), "7": (0.25, 0.75, 0.25, 0.275),
        "8": (0.75, 0.5, 0.275, 0.25), "9": (0.75, 0.0, 0.275, 0.25), "10": (0.75, -0.5, 0.275, 0.25),
    }
    for n, (x, y, sx, sy) in pads.items():
        b.append(smd_pad(n, x, y, sx, sy))
    write(name, b)


def x2y_0805() -> None:
    name = "X2Y_0805_4T"
    b = hdr(name, "X2Y 4-terminal EMI filter capacitor, 0805; land per Yageo X2Y spec V.15 Table 3 (A 3.05 B 1.27 C 0.89 D 0.56 E 2.03). 1/2 = A/B ends, 3/4 = G terminals")
    b.append(rect("F.Fab", -1.0, -0.625, 1.0, 0.625))
    b.append(rect("F.CrtYd", -1.8, -1.3, 1.8, 1.3, 0.05))
    xe = (3.05 - 0.89) / 2
    b.append(smd_pad("1", -xe, 0, 0.89, 1.27))
    b.append(smd_pad("2", xe, 0, 0.89, 1.27))
    gy = 2.03 / 2 - 0.35
    b.append(smd_pad("3", 0, -gy, 0.56, 0.7))
    b.append(smd_pad("4", 0, gy, 0.56, 0.7))
    write(name, b)


def srf2012() -> None:
    name = "Bourns_SRF2012_4T"
    b = hdr(name, "Bourns SRF2012A common-mode chip inductor 2.0 x 1.2 mm, 4-terminal; land per datasheet Recommended Layout (1.1 x 0.45 pads, 2.6 x-pitch, 1.25 y-span). Windings 1-2 and 4-3")
    b.append(rect("F.Fab", -1.0, -0.6, 1.0, 0.6))
    b.append(rect("F.CrtYd", -2.1, -1.0, 2.1, 1.0, 0.05))
    b.append(circ("F.SilkS", -2.3, -0.4, 0.15))
    yy = (1.25 - 0.45) / 2
    b.append(smd_pad("1", -1.3, -yy, 1.1, 0.45))
    b.append(smd_pad("2", 1.3, -yy, 1.1, 0.45))
    b.append(smd_pad("3", 1.3, yy, 1.1, 0.45))
    b.append(smd_pad("4", -1.3, yy, 1.1, 0.45))
    write(name, b)


def we_mapi_3015() -> None:
    name = "L_WE-MAPI_3015"
    b = hdr(name, "Wurth WE-MAPI 3015 SMT power inductor 3.0 x 3.0 x 1.5 mm (74438335033); land per datasheet p.1: 2 pads 1.3 x 3.4, 0.8 gap")
    b.append(rect("F.Fab", -1.5, -1.5, 1.5, 1.5))
    b.append(rect("F.CrtYd", -2.0, -2.0, 2.0, 2.0, 0.05))
    b.append(line("F.SilkS", -1.65, -1.95, 1.65, -1.95))
    b.append(line("F.SilkS", -1.65, 1.95, 1.65, 1.95))
    b.append(smd_pad("1", -1.05, 0, 1.3, 3.4))
    b.append(smd_pad("2", 1.05, 0, 1.3, 3.4))
    write(name, b)


def nanofit() -> None:
    name = "Molex_NanoFit_1x04_Horizontal"
    b = hdr(name, "Molex Nano-Fit 2.50 mm 1x4 header (105313-1204) — geometry carried over from prior board; NOT datasheet-verified (no drawing on disk)", smd=False)
    b.append(rect("F.Fab", -5.6, -3.0, 5.6, 3.0))
    b.append(rect("F.CrtYd", -6.1, -3.5, 6.1, 3.5, 0.05))
    b.append(rect("F.SilkS", -5.75, -3.15, 5.75, 3.15))
    for i in range(4):
        x = -3.75 + i * 2.5
        b.append(tht_pad(str(1 + i), x, 0, 1.5, 1.0, "rect" if i == 0 else "circle"))
    write(name, b)


def pb2_socket(name: str) -> None:
    b = hdr(name, "PocketBeagle 2 Industrial cape rail: 2 x 18 socket, 2.54 mm pitch, pin 1 at -21.59,-1.27 (odd row y=-1.27)", smd=False)
    b.append(rect("F.Fab", -22.86, -2.54, 22.86, 2.54))
    b.append(rect("F.CrtYd", -23.0, -2.8, 23.0, 2.8, 0.05))
    b.append(line("F.SilkS", -23.0, -2.7, 23.0, -2.7))
    b.append(line("F.SilkS", -23.0, 2.7, 23.0, 2.7))
    b.append(circ("F.Fab", -23.6, -1.27, 0.25))
    for i in range(18):
        x = -21.59 + i * 2.54
        b.append(tht_pad(str(2 * i + 1), x, -1.27, 1.7, 1.0, "rect" if i == 0 else "circle"))
        b.append(tht_pad(str(2 * i + 2), x, 1.27, 1.7, 1.0))
    write(name, b)


def pgnd_hole() -> None:
    """M2.5 mounting hole (2.7 mm) with a 3.6 mm PGND ring: the cape's chassis bond
    through the stack hardware (Pilot.md §7).  A 3.6 mm ring (not KiCad's 5.0 mm
    _Pad variant) keeps 0.26 mm to the PB2 rail's corner pins with the hole on
    the R3 corner centre (u,v = 3.0 / 52.0)."""
    name = "MountingHole_2.7mm_M2.5_PGND_Ring"
    b = hdr(name, "M2.5 mounting hole, 2.7 mm drill, 3.6 mm annular PGND ring for the cape chassis bond", smd=False)
    b.append(circ("F.CrtYd", 0, 0, 2.05, 0.05))
    b.append(tht_pad("1", 0, 0, 3.6, 2.7))
    write(name, b)


def tsm_2x8_dv() -> None:
    """Samtec TSM-108-01-x-DV: 2 x 8 SMT 0.1 in terminal strip.  Recommended PCB
    layout per samtec_tsm-dv-footprint.pdf Rev F Fig 1: pads 1.27 x 3.68 mm,
    inner edges 1.27 mm apart (centres at y = +/-2.475), 2.54 mm column pitch,
    both rows in the same columns.  Samtec numbering: column k -> pin 2k-1 (row A,
    y < 0) and pin 2k (row B, y > 0).  Body 20.32 x 5.08 mm (catalog F-226)."""
    name = "Samtec_TSM-108-01-x-DV"
    b = hdr(name, "Samtec TSM-108-01-x-DV 2x8 SMT 0.100 in terminal strip; pads 1.27x3.68 @ y=+/-2.475, 2.54 pitch (TSM-DV footprint Rev F)")
    n = 8
    w = n * 2.54 / 2
    b.append(rect("F.Fab", -w, -2.54, w, 2.54))
    b.append(rect("F.CrtYd", -w - 0.5, -4.6, w + 0.5, 4.6, 0.05))
    b.append(line("F.SilkS", -w - 0.15, -0.6, -w - 0.15, 0.6))
    b.append(line("F.SilkS", w + 0.15, -0.6, w + 0.15, 0.6))
    b.append(circ("F.SilkS", -w + 1.27, -4.9, 0.2))
    for k in range(n):
        x = -w + 1.27 + k * 2.54
        b.append(smd_pad(str(2 * k + 1), x, -2.475, 1.27, 3.68, "rect"))
        b.append(smd_pad(str(2 * k + 2), x, 2.475, 1.27, 3.68, "rect"))
    write(name, b)


def main() -> None:
    LIB.mkdir(exist_ok=True)
    tsm_2x8_dv()
    pgnd_hole()
    # sam_m10q() retired 2026-09-19: Pilot's GPS moved to MAX-M10S (external
    # antenna, RF_GPS:ublox_MAX system footprint) per the four-bus area
    # ideation.  The SAM-M10Q land generator stays defined (other fleet
    # boards' replace_footprints.py still reference the shared footprint) but
    # is no longer regenerated from this board's script.
    we_lan()
    sm1553()
    bmp388()
    x2y_0805()
    srf2012()
    we_mapi_3015()
    nanofit()
    pb2_socket("PocketBeagle2_2x18_P1_Socket")
    pb2_socket("PocketBeagle2_2x18_P2_Socket")


if __name__ == "__main__":
    main()
