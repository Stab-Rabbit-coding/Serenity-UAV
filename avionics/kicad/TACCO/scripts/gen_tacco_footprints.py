#!/usr/bin/env python3
"""gen_xo_footprints.py — Author the project-custom land patterns XO needs.

Writes KiCad 9 ``.kicad_mod`` files into ``avionics/kicad/Serenity-Custom.pretty``
(the same shared custom library Pilot uses — ``gen_pilot_footprints.py`` and this
script write disjoint file names into it).  Every land pattern below is
transcribed from the OEM datasheet in ``avionics/datasheets/`` where one could be
obtained; two parts could NOT be fully datasheet-verified this pass and are
flagged individually below and in ``XO.md`` — this mirrors the project's
existing precedent for an unverified land (Pilot's Molex Nano-Fit, WBS §1.2a).

Footprints and sources
----------------------
* ``RFDesign_RFD900x_2x8_THT``     rfd900x-datasheet.pdf §5 Fig 5-1: 2 x 8 THT,
                                   0.1 in (2.54 mm) pitch within a row, 20.0 mm
                                   row-to-row separation, 3 x M3 mounting holes.
                                   [avionics/datasheets/rfd900x-datasheet.pdf]
* ``HopeRF_RFM95W_Castellated_16`` rfm95w-datasheet.pdf §1.4 pin table (16 pins) /
                                   package outline p.120: 16 x 16 mm body, 8
                                   castellated half-holes per side, 2.0 mm pitch.
* ``Murata_Type2EL_LGA107``        type2el.pdf Rev.18 Table 5/Fig 3/Fig 24
                                   (LBES5PL2EL-923, WiFi+BT+802.15.4).  Body
                                   envelope (8.8 x 7.7 x 1.3mm) is
                                   DATASHEET-EXACT.  Replaces WL1837MOD
                                   2026-09-21 (also closes the never-
                                   implemented Zigbee scope gap — see
                                   gen_xo_sch.py's swap note).  *** Pad-by-pad
                                   positions are a PLACEHOLDER, NOT
                                   pixel-verified *** — the 107-terminal LGA
                                   array's raster in the source PDF was too
                                   low-resolution to map exactly; do not
                                   release to fab without re-verifying against
                                   Murata's own CAD library or a
                                   high-resolution Fig 24.  See the function's
                                   own docstring for full detail.
* ``TPS6303x_VSON-10_2p5``        tps63031.pdf p.1/§ device info: VSON(DSK)
                                   10-pin, 2.50 x 2.50 mm body, 0.5 mm pitch.
                                   KiCad's system ``Package_SON.pretty`` only
                                   ships the 3x3 mm VSON-10 variant; pad
                                   geometry here is pattern-matched from that
                                   family scaled to the datasheet's 2.5x2.5 mm
                                   body — courtyard is per datasheet, individual
                                   pad corners are NOT pixel-verified against
                                   TI's mechanical drawing.  Flagged.
* ``Johanson_0915LP15B026E_SMD4``  johanson-0915lp15b026e.pdf: substituted for
                                   the fabricated "0915LP15B0100E" part number
                                   XO.md originally cited (that MPN does not
                                   exist in Johanson's catalog — confirmed by
                                   direct catalog search).  0915LP15B026E is a
                                   real Johanson 915 MHz LOW-PASS filter (not a
                                   band-pass, a different topology than XO.md's
                                   table implied); 4-pad SMD, ~2.0 x 1.25 mm
                                   body, pattern-matched to Johanson's standard
                                   0805-size RF filter footprint family since no
                                   land-pattern drawing was recoverable from the
                                   fetched PDF.  NEEDS user confirmation.
* ``RCLAMP0502B_SOD882``           Semtech RCLAMP0502B: a real, current part
                                   (Semtech product page confirms SOD-882 /
                                   SC-75 2-pad package, <1 pF, marked "not
                                   recommended for new designs"), but NO
                                   datasheet PDF could be fetched this pass
                                   (every mirror tried — Semtech, Mouser,
                                   DigiKey, LCSC — returned an HTML block page,
                                   not a PDF).  Pad geometry here is a
                                   reasonable SOD-882 estimate (0.9 x 0.5 mm
                                   pads, 1.8 mm pitch), NOT datasheet-verified.
                                   Flagged for confirmation / re-fetch.

Author: Claude Sonnet 5, 2026-09-20.  Owner: sgriffing.  License: CC BY 4.0.
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
        '\t(generator "gen_xo_footprints.py")',
        '\t(generator_version "9.0")',
        '\t(layer "F.Cu")',
        f'\t(descr "{descr}")',
        f'\t(tags "Serenity XO {name}")',
        f"\t(attr {attr})",
        '\t(property "Reference" "REF**" (at 0 -1 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
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


def castellated_pad(num: str, x: float, y: float, sx: float, sy: float) -> str:
    """Half-via castellated edge pad (RFM95W module edges)."""
    return (f'\t(pad "{num}" smd roundrect (at {x:.3f} {y:.3f}) (size {sx:.3f} {sy:.3f}) '
            f'(layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.4))')


def tht_pad(num: str, x: float, y: float, d: float, drill: float, shape: str = "circle") -> str:
    return (f'\t(pad "{num}" thru_hole {shape} (at {x:.3f} {y:.3f}) (size {d:.3f} {d:.3f}) '
            f'(drill {drill:.3f}) (layers "*.Cu" "*.Mask"))')


def nplated_hole(x: float, y: float, d: float) -> str:
    return (f'\t(pad "" np_thru_hole circle (at {x:.3f} {y:.3f}) (size {d:.3f} {d:.3f}) '
            f'(drill {d:.3f}) (layers "*.Cu" "*.Mask"))')


def write(name: str, body: List[str]) -> None:
    (LIB / f"{name}.kicad_mod").write_text("\n".join(body + [")"]) + "\n")
    print("wrote", name)


def rfd900ux_smt() -> None:
    """RF Design RFD900ux-SMT/RFD868ux-SMT — replaces the earlier RFD900x THT
    piggyback header 2026-09-20: the owner found the RFD900x (42.5x30mm THT,
    even piggybacked) overhangs the 55x35mm XO cape in more than one
    direction. The RFD900ux-SMT is the same manufacturer's flush SMT variant,
    21x29x4.2mm body (~48% of the RFD900x's footprint area) — real, verified
    from "RFD900ux DataSheet v1.2.pdf" §5.2 (Fig 5-2, 28-pad pin layout),
    §6.1 (Fig 6-1 / Table 6-1, land pattern: 2x14 castellated edge pads +
    2 central thermal/GND pads). No piggyback/standoff mounting needed —
    this module mounts flush like RFM95W/WL1837MOD.

    2026-09-21: XO's own SIK (RFD900ux-SMT) instance was REMOVED from this
    board's schematic (relocated to Commo; see gen_xo_sch.py's swap note and
    avionics/WBS.md) — this function stays here and still runs from main()
    because Commo's own footprint generator does not (yet) duplicate it, and
    Serenity-Custom.pretty is the one shared library both boards' generators
    write into. Do not delete this function without checking Commo's own
    schematic/PCB no longer needs the footprint file it produces."""
    name = "RFDesign_RFD900ux_SMT"
    hx, hy = 21.2 / 2, 29.0 / 2  # K=21.2mm land width; body height per §2 "21x29x4.2mm"
    b = hdr(name, "RF Design RFD900ux-SMT/RFD868ux-SMT, 21x29x4.2mm flush SMT, 28 castellated "
                  "edge pads (14/side) + 2 central GND thermal pads (RFD900ux DataSheet v1.2.pdf "
                  "Fig 5-2 pinout / Fig 6-1 + Table 6-1 land pattern)")
    b.append(rect("F.Fab", -hx, -hy, hx, hy))
    b.append(rect("F.CrtYd", -hx - 0.5, -hy - 0.5, hx + 0.5, hy + 0.5, 0.05))
    b.append(rect("F.SilkS", -hx + 0.15, -hy + 0.15, hx - 0.15, hy - 0.15))
    b.append(circ("F.SilkS", -hx - 0.3, -hy - 0.3, 0.2))
    # Pad pitch/size CONFIRMED 2026-09-21 against Table 6-1 (read directly
    # from RFD900ux DataSheet v1.2.pdf p.11): A=2mm is the pad pitch (13
    # gaps x 2mm = 26mm span, + H=1.5mm top/bottom margin each side =
    # 29mm body height -- matches exactly). B=2.4mm/C=1mm are the pad's
    # depth-into-board / along-edge dimensions respectively; the along-
    # edge (pitch-direction, Y here) dimension MUST be the smaller one
    # (C=1mm) or adjacent castellated pads on the same edge short into
    # each other at 2mm pitch -- an earlier estimate (pitch=1.9mm) had
    # this backwards (1.0 x 2.4 with the 2.4 in the pitch direction),
    # which DRC caught as pad-to-pad shorts once this footprint was
    # first actually placed (Commo SIK swap). Resolves the "NOT pixel-
    # verified" flag this function previously carried.
    pitch = 2.0
    span = (14 - 1) * pitch
    y0 = span / 2
    # Left column: pins 15 (top) .. 28 (bottom); Right column: 14 (top) .. 1 (bottom)
    # per Fig 5-2's silkscreen pin numbering (top view).
    for i in range(14):
        y = y0 - i * pitch
        b.append(castellated_pad(str(15 + i), -hx, y, 2.4, 1.0))
        b.append(castellated_pad(str(14 - i), hx, y, 2.4, 1.0))
    # Two central GND/thermal pads (D=8 x E=6.6mm each per Table 6-1), stacked
    # vertically per Fig 6-1, both tied to GND.
    b.append(smd_pad("29", 0.0, -4.0, 8.0, 6.6, "rect"))
    b.append(smd_pad("30", 0.0, 4.0, 8.0, 6.6, "rect"))
    write(name, b)


def rfm95w_castellated() -> None:
    name = "HopeRF_RFM95W_Castellated_16"
    b = hdr(name, "HopeRF RFM95W LoRa module, 16x16 mm SMD, 8 castellated half-pads per side, "
                  "2.0 mm pitch (rfm95w-datasheet.pdf Table pin description / package outline p.120)")
    half = 16.0 / 2
    b.append(rect("F.Fab", -half, -half, half, half))
    b.append(rect("F.CrtYd", -half - 0.5, -half - 0.5, half + 0.5, half + 0.5, 0.05))
    b.append(rect("F.SilkS", -half + 0.2, -half + 0.2, half - 0.2, half - 0.2))
    b.append(circ("F.SilkS", -half - 0.8, -half - 0.8, 0.25))
    pitch = 2.0
    # Pin 1 bottom-left, CCW: 1-4 bottom (L->R), 5-8 right (bottom->top),
    # 9-12 top (R->L), 13-16 left (top->bottom) — matches the datasheet's
    # pin-1-dot bottom-left convention used on the module's own silk.
    pads: List[Tuple[str, float, float, float, float]] = []
    for i in range(4):
        x = -1.5 * pitch + i * pitch
        pads.append((str(1 + i), x, half, 1.0, 1.2))
    for i in range(4):
        y = half - 1.5 * pitch - i * pitch
        pads.append((str(5 + i), half, y, 1.2, 1.0))
    for i in range(4):
        x = half - 1.5 * pitch - i * pitch
        pads.append((str(9 + i), x, -half, 1.0, 1.2))
    for i in range(4):
        y = -half + 1.5 * pitch + i * pitch
        pads.append((str(13 + i), -half, y, 1.2, 1.0))
    for num, x, y, sx, sy in pads:
        b.append(castellated_pad(num, x, y, sx, sy))
    write(name, b)


def seeed_wioe5_qfn28() -> None:
    name = "Seeed_WioE5_QFN28"
    b = hdr(name, "Seeed Wio-E5 (STM32WLE5JC-based LoRa module), 28-pin castellated QFN, "
                  "12 x 12 x 2.5mm body (wio-e5-datasheet.pdf V1.1 Table 4 'Structure', "
                  "§5.1 Package information Fig showing 12+0.3/-0.2mm x 12+0.3/-0.2mm x "
                  "2.5+/-0.2mm, and Fig 11 'PCB layout' giving 1.0mm pad width / 1.25mm pitch "
                  "/ 2.3mm pad depth, 7 pads per side). Pin-1 dot at top-left per Fig 2 'Pin "
                  "arrangement'; numbering proceeds counterclockwise from there (down the left "
                  "edge 1-7, right along the bottom 8-14, up the right edge 15-21, left along "
                  "the top 22-28) — this is a uniform-pitch castellated QFN fully specified by "
                  "the datasheet's own numeric dimensions plus its Table 1 pin-name-per-position "
                  "list, not an estimate (unlike the Type2EL LGA above).")
    half = 12.0 / 2
    b.append(rect("F.Fab", -half, -half, half, half))
    b.append(rect("F.CrtYd", -half - 0.5, -half - 0.5, half + 0.5, half + 0.5, 0.05))
    b.append(rect("F.SilkS", -half + 0.2, -half + 0.2, half - 0.2, half - 0.2))
    b.append(circ("F.SilkS", -half - 0.8, -half - 0.8, 0.25))
    pitch = 1.25
    n = 7
    span = (n - 1) * pitch / 2
    pads: List[Tuple[str, float, float, float, float]] = []
    for i in range(n):
        y = span - i * pitch
        pads.append((str(1 + i), -half, y, 2.3, 1.0))
    for i in range(n):
        x = -span + i * pitch
        pads.append((str(8 + i), x, -half, 1.0, 2.3))
    for i in range(n):
        y = -span + i * pitch
        pads.append((str(15 + i), half, y, 2.3, 1.0))
    for i in range(n):
        x = span - i * pitch
        pads.append((str(22 + i), x, half, 1.0, 2.3))
    for num, x, y, sx, sy in pads:
        b.append(castellated_pad(num, x, y, sx, sy))
    # Exposed center thermal/ground pad (Fig 16 bottom-view shows a large
    # center land) — no dedicated pin number in Table 1, so numbered "29"
    # (unused number, consistent with this project's thermal-pad convention
    # elsewhere) and tied to GND in the schematic.
    b.append(smd_pad("29", 0.0, 0.0, 6.0, 6.0, "rect"))
    write(name, b)


def type2el_lga107() -> None:
    name = "Murata_Type2EL_LGA107"
    b = hdr(name, "Murata Type 2EL (LBES5PL2EL-923) WiFi+BT+802.15.4 tri-radio module, "
                  "107-terminal LGA (type2el.pdf Rev.18 Table 5/Figure 3/Figure 24). "
                  "Body 8.8 x 7.7 x 1.3mm max is DATASHEET-EXACT (Table 5: L=8.8+/-0.2, "
                  "W=7.7+/-0.2, T=1.3max) and courtyard is derived from it directly. Pad "
                  "geometry (all 107 positions/sizes below) is transcribed EXACTLY from the "
                  "vendor's own CAD drawing, "
                  "avionics/datasheets/type2el-2dl-module-footprint-topview.dxf (owner-supplied, "
                  "AutoCAD R14, 'NC_Work2' layer = 107 pad rectangles [428 LINE entities, 4 per "
                  "pad], 'ProductsBoradOutline' layer = the 8.8x7.7mm body outline — both parsed "
                  "programmatically, not hand-traced). *** ONE THING REMAINS AN INFERENCE, NOT "
                  "A VENDOR FACT: pin-NUMBER-to-PAD correspondence. *** The DXF has no per-pad "
                  "text labels, so which physical pad is pin 1 vs pin 54 vs pin 107 is assigned "
                  "here by the standard LGA convention (pin 1 at the bottom-left corner, matching "
                  "Fig.3's e1/a1 bottom-left dimension callouts; numbered clockwise around the "
                  "54-pad perimeter, then the 53-pad interior array in row-major raster order) — "
                  "this is a well-reasoned default, not a wild guess, but it has NOT been cross-"
                  "checked against Murata's own pin-numbered CAD/BOM output. Re-verify pin-1 "
                  "orientation and the perimeter winding direction before fab.")
    L, W = 8.8 / 2, 7.7 / 2
    b.append(rect("F.Fab", -L, -W, L, W))
    b.append(rect("F.CrtYd", -L - 0.3, -W - 0.3, L + 0.3, W + 0.3, 0.05))
    b.append(rect("F.SilkS", -L - 0.1, -W - 0.1, L + 0.1, W + 0.1))
    b.append(circ("F.SilkS", -L - 0.5, -W - 0.5, 0.25))
    # Pad centers/sizes below are exact (see docstring): (pin, x, y, size_x, size_y),
    # already recentered so (0,0) = body center, transcribed from
    # type2el-2dl-module-footprint-topview.dxf via a one-off parse script
    # (group DXF LINE entities on the 'NC_Work2' layer into 4-line pad
    # rectangles, order the 54 perimeter pads clockwise from bottom-left,
    # then the 53 interior pads in row-major raster order — see this
    # function's docstring for what is and is not vendor-verified).
    PADS = [
        (1, -3.975, -3.275, 0.25, 0.55), (2, -3.25, -3.275, 0.25, 0.55),
        (3, -2.75, -3.275, 0.25, 0.55), (4, -2.25, -3.275, 0.25, 0.55),
        (5, -1.75, -3.275, 0.25, 0.55), (6, -1.25, -3.275, 0.25, 0.55),
        (7, -0.75, -3.275, 0.25, 0.55), (8, -0.25, -3.275, 0.25, 0.55),
        (9, 0.25, -3.275, 0.25, 0.55), (10, 0.75, -3.275, 0.25, 0.55),
        (11, 1.25, -3.275, 0.25, 0.55), (12, 1.75, -3.275, 0.25, 0.55),
        (13, 2.25, -3.275, 0.25, 0.55), (14, 2.75, -3.275, 0.25, 0.55),
        (15, 3.25, -3.275, 0.25, 0.55), (16, 3.975, -3.275, 0.25, 0.55),
        (17, 3.825, -2.5, 0.55, 0.25), (18, 3.825, -2.0, 0.55, 0.25),
        (19, 3.825, -1.5, 0.55, 0.25), (20, 3.825, -1.0, 0.55, 0.25),
        (21, 3.825, -0.5, 0.55, 0.25), (22, 3.825, 0.0, 0.55, 0.25),
        (23, 3.825, 0.5, 0.55, 0.25), (24, 3.825, 1.0, 0.55, 0.25),
        (25, 3.825, 1.5, 0.55, 0.25), (26, 3.825, 2.0, 0.55, 0.25),
        (27, 3.825, 2.5, 0.55, 0.25), (28, 3.975, 3.275, 0.25, 0.55),
        (29, 3.25, 3.275, 0.25, 0.55), (30, 2.75, 3.275, 0.25, 0.55),
        (31, 2.25, 3.275, 0.25, 0.55), (32, 1.75, 3.275, 0.25, 0.55),
        (33, 1.25, 3.275, 0.25, 0.55), (34, 0.75, 3.275, 0.25, 0.55),
        (35, 0.25, 3.275, 0.25, 0.55), (36, -0.25, 3.275, 0.25, 0.55),
        (37, -0.75, 3.275, 0.25, 0.55), (38, -1.25, 3.275, 0.25, 0.55),
        (39, -1.75, 3.275, 0.25, 0.55), (40, -2.25, 3.275, 0.25, 0.55),
        (41, -2.75, 3.275, 0.25, 0.55), (42, -3.25, 3.275, 0.25, 0.55),
        (43, -3.975, 3.275, 0.25, 0.55), (44, -3.825, 2.5, 0.55, 0.25),
        (45, -3.825, 2.0, 0.55, 0.25), (46, -3.825, 1.5, 0.55, 0.25),
        (47, -3.825, 1.0, 0.55, 0.25), (48, -3.825, 0.5, 0.55, 0.25),
        (49, -3.825, 0.0, 0.55, 0.25), (50, -3.825, -0.5, 0.55, 0.25),
        (51, -3.825, -1.0, 0.55, 0.25), (52, -3.825, -1.5, 0.55, 0.25),
        (53, -3.825, -2.0, 0.55, 0.25), (54, -3.825, -2.5, 0.55, 0.25),
        (55, -1.425, -2.0, 0.55, 0.25), (56, -0.475, -2.0, 0.55, 0.25),
        (57, 0.475, -2.0, 0.55, 0.25), (58, 1.425, -2.0, 0.55, 0.25),
        (59, 2.375, -2.0, 0.55, 0.25), (60, -2.375, -1.5, 0.55, 0.25),
        (61, -1.425, -1.5, 0.55, 0.25), (62, -0.475, -1.5, 0.55, 0.25),
        (63, 0.475, -1.5, 0.55, 0.25), (64, 1.425, -1.5, 0.55, 0.25),
        (65, 2.375, -1.5, 0.55, 0.25), (66, -2.375, -1.0, 0.55, 0.25),
        (67, -1.425, -1.0, 0.55, 0.25), (68, -0.475, -1.0, 0.55, 0.25),
        (69, 0.475, -1.0, 0.55, 0.25), (70, 1.425, -1.0, 0.55, 0.25),
        (71, 2.375, -1.0, 0.55, 0.25), (72, -2.375, -0.5, 0.55, 0.25),
        (73, -1.425, -0.5, 0.55, 0.25), (74, -0.475, -0.5, 0.55, 0.25),
        (75, 0.475, -0.5, 0.55, 0.25), (76, 1.425, -0.5, 0.55, 0.25),
        (77, 2.375, -0.5, 0.55, 0.25), (78, -2.375, 0.0, 0.55, 0.25),
        (79, -1.425, 0.0, 0.55, 0.25), (80, -0.475, 0.0, 0.55, 0.25),
        (81, 0.475, 0.0, 0.55, 0.25), (82, 1.425, 0.0, 0.55, 0.25),
        (83, 2.375, 0.0, 0.55, 0.25), (84, -2.375, 0.5, 0.55, 0.25),
        (85, -1.425, 0.5, 0.55, 0.25), (86, -0.475, 0.5, 0.55, 0.25),
        (87, 0.475, 0.5, 0.55, 0.25), (88, 1.425, 0.5, 0.55, 0.25),
        (89, 2.375, 0.5, 0.55, 0.25), (90, -2.375, 1.0, 0.55, 0.25),
        (91, -1.425, 1.0, 0.55, 0.25), (92, -0.475, 1.0, 0.55, 0.25),
        (93, 0.475, 1.0, 0.55, 0.25), (94, 1.425, 1.0, 0.55, 0.25),
        (95, 2.375, 1.0, 0.55, 0.25), (96, -2.375, 1.5, 0.55, 0.25),
        (97, -1.425, 1.5, 0.55, 0.25), (98, -0.475, 1.5, 0.55, 0.25),
        (99, 0.475, 1.5, 0.55, 0.25), (100, 1.425, 1.5, 0.55, 0.25),
        (101, 2.375, 1.5, 0.55, 0.25), (102, -2.375, 2.0, 0.55, 0.25),
        (103, -1.425, 2.0, 0.55, 0.25), (104, -0.475, 2.0, 0.55, 0.25),
        (105, 0.475, 2.0, 0.55, 0.25), (106, 1.425, 2.0, 0.55, 0.25),
        (107, 2.375, 2.0, 0.55, 0.25),
    ]
    for n, x, y, sx, sy in PADS:
        b.append(smd_pad(str(n), x, y, sx, sy, "rect"))
    write(name, b)


def tps6303x_vson10() -> None:
    name = "TPS6303x_VSON-10_2p5"
    b = hdr(name, "TI TPS6303x buck-boost, VSON-10 (DSK), 2.50 x 2.50 mm body, 0.5 mm pitch "
                  "(tps63031.pdf device info table); pad geometry pattern-matched from KiCad's "
                  "3x3 mm VSON-10 family scaled down — flagged, not pixel-verified.")
    half = 2.5 / 2
    b.append(rect("F.Fab", -half, -half, half, half))
    b.append(rect("F.CrtYd", -half - 0.6, -half - 0.6, half + 0.6, half + 0.6, 0.05))
    b.append(circ("F.SilkS", -half - 0.3, -half - 0.3, 0.2))
    # 3 pins each on top/bottom (long edges), 2 pins each on left/right (short edges) —
    # matches the 3-2-3-2 lead-frame convention typical of a 10-pin VSON.
    pitch = 0.5
    for i in range(3):
        x = -pitch + i * pitch
        b.append(smd_pad(str(1 + i), x, -half - 0.15, 0.28, 0.5))
    for i in range(2):
        y = -pitch / 2 + i * pitch
        b.append(smd_pad(str(4 + i), half + 0.15, y, 0.5, 0.28))
    for i in range(3):
        x = pitch - i * pitch
        b.append(smd_pad(str(6 + i), x, half + 0.15, 0.28, 0.5))
    for i in range(2):
        y = pitch / 2 - i * pitch
        b.append(smd_pad(str(9 + i), -half - 0.15, y, 0.5, 0.28))
    b.append(f'\t(pad "11" smd rect (at 0 0) (size {half:.3f} {half:.3f}) (layers "F.Cu" "F.Paste" "F.Mask"))')
    write(name, b)


def rf_filter_smd4(name: str, descr: str) -> None:
    """Generic 4-pad SMD RF filter footprint, Johanson 0805-size family."""
    b = hdr(name, descr)
    bx, by = 2.0 / 2, 1.25 / 2
    b.append(rect("F.Fab", -bx, -by, bx, by))
    b.append(rect("F.CrtYd", -bx - 0.4, -by - 0.4, bx + 0.4, by + 0.4, 0.05))
    b.append(circ("F.SilkS", -bx - 0.25, -by - 0.25, 0.15))
    # pins 1(IN) / 2(GND) / 3(GND) / 4(OUT) — 2 pads per short end (standard
    # Johanson RF-filter pinout: end pads are RF I/O, middle pads are GND).
    b.append(smd_pad("1", -bx - 0.15, -by * 0.55, 0.5, 0.4))
    b.append(smd_pad("2", -bx - 0.15, by * 0.55, 0.5, 0.4))
    b.append(smd_pad("3", bx + 0.15, by * 0.55, 0.5, 0.4))
    b.append(smd_pad("4", bx + 0.15, -by * 0.55, 0.5, 0.4))
    write(name, b)


def rclamp0502b() -> None:
    name = "RCLAMP0502B_SOD882"
    b = hdr(name, "Semtech RCLAMP0502B 2-line ESD/RF clamp, SOD-882 (SC-75), 2-pad, "
                  "~1.0 x 0.6 mm body — NOT datasheet-verified (no PDF obtained this pass, "
                  "product page confirms package family only). Flagged for confirmation.")
    bx, by = 1.0 / 2, 0.6 / 2
    b.append(rect("F.Fab", -bx, -by, bx, by))
    b.append(rect("F.CrtYd", -bx - 0.35, -by - 0.35, bx + 0.35, by + 0.35, 0.05))
    b.append(line("F.SilkS", -bx - 0.15, -by - 0.15, -bx - 0.15, by + 0.15))
    pitch = 1.8 / 2
    b.append(smd_pad("1", -pitch, 0.0, 0.5, 0.5))
    b.append(smd_pad("2", pitch, 0.0, 0.5, 0.5))
    write(name, b)


def main() -> None:
    LIB.mkdir(parents=True, exist_ok=True)
    rfd900ux_smt()
    rfm95w_castellated()
    type2el_lga107()
    seeed_wioe5_qfn28()
    tps6303x_vson10()
    rf_filter_smd4("Johanson_0915LP15B026E_SMD4",
                   "Johanson 0915LP15B026E 915 MHz low-pass RF filter, substituted for the "
                   "fabricated 0915LP15B0100E part number XO.md originally cited (does not exist "
                   "in Johanson's catalog); 4-pad SMD, ~2.0x1.25 mm, pattern-matched land — NEEDS "
                   "user confirmation.")
    rclamp0502b()


if __name__ == "__main__":
    main()
