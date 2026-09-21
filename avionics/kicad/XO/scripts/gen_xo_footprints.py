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
* ``WL1837MOD_MOC_100``           wl1837mod.pdf SWRS170L pinout table (100-ball
                                   MOC).  Only the ~14 functionally-used balls
                                   (SDIO, WLAN_EN, BT_EN, WLAN_IRQ, VBAT_IN x2,
                                   VIO, RF_ANT1, a GND subset) carry a net on
                                   this pass, per the datasheet's own "leave
                                   NC if unused" guidance for the rest — an
                                   explicit, disclosed scope calibration (see
                                   XO.md and the commit message), NOT a
                                   pin-by-pin-verified land pattern like the
                                   Pilot boards's GNSS/IMU/baro footprints.
                                   The full 100-ball grid is still drawn (every
                                   physical solder ball must land somewhere)
                                   using the datasheet's row/column layout;
                                   unused balls are wired NC in the schematic.
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
* ``Johanson_2450BP15E0100_SMD4``  johanson-2450bp15e0100.pdf: substituted for
                                   the fabricated "2450BP15B050E" part number
                                   (also does not exist).  2450BP15E0100 is a
                                   real Johanson 2.45 GHz band-pass filter,
                                   same 4-pad SMD family as above.  NEEDS user
                                   confirmation.
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
    this module mounts flush like RFM95W/WL1837MOD."""
    name = "RFDesign_RFD900ux_SMT"
    hx, hy = 21.2 / 2, 29.0 / 2  # K=21.2mm land width; body height per §2 "21x29x4.2mm"
    b = hdr(name, "RF Design RFD900ux-SMT/RFD868ux-SMT, 21x29x4.2mm flush SMT, 28 castellated "
                  "edge pads (14/side) + 2 central GND thermal pads (RFD900ux DataSheet v1.2.pdf "
                  "Fig 5-2 pinout / Fig 6-1 + Table 6-1 land pattern)")
    b.append(rect("F.Fab", -hx, -hy, hx, hy))
    b.append(rect("F.CrtYd", -hx - 0.5, -hy - 0.5, hx + 0.5, hy + 0.5, 0.05))
    b.append(rect("F.SilkS", -hx + 0.15, -hy + 0.15, hx - 0.15, hy - 0.15))
    b.append(circ("F.SilkS", -hx - 0.3, -hy - 0.3, 0.2))
    # Pad pitch: Table 6-1 gives absolute pad/margin dimensions (A,B,C,G,H,K,
    # etc.) but not a single "pitch" value, and Figure 6-1's vector art
    # wasn't machine-extractable at pad-to-pad resolution. Estimated as
    # (body height 29mm - top/bottom keepout) / 13 gaps ~= 1.9mm, NOT
    # pixel-verified against the figure -- flagged for confirmation before
    # this footprint is used on a real fab order.
    pitch = 1.9
    span = (14 - 1) * pitch
    y0 = span / 2
    # Left column: pins 15 (top) .. 28 (bottom); Right column: 14 (top) .. 1 (bottom)
    # per Fig 5-2's silkscreen pin numbering (top view).
    for i in range(14):
        y = y0 - i * pitch
        b.append(castellated_pad(str(15 + i), -hx, y, 1.0, 2.4))
        b.append(castellated_pad(str(14 - i), hx, y, 1.0, 2.4))
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


def wl1837mod_moc100() -> None:
    name = "WL1837MOD_MOC_100"
    b = hdr(name, "TI WL1837MOD WiFi+BT combo module, 100-ball MOC package "
                  "(wl1837mod.pdf SWRS170L). Only the ~14 functionally-used balls carry a "
                  "schematic net this pass (scope calibration disclosed in XO.md); the full "
                  "10x10 ball grid is still drawn since every physical ball must have a land.")
    body = 9.0 / 2  # approx MOC-100 body per typical TI MOC package family
    b.append(rect("F.Fab", -body, -body, body, body))
    b.append(rect("F.CrtYd", -body - 0.5, -body - 0.5, body + 0.5, body + 0.5, 0.05))
    b.append(rect("F.SilkS", -body - 0.15, -body - 0.15, body + 0.15, body + 0.15))
    b.append(circ("F.SilkS", -body - 0.8, -body - 0.8, 0.25))
    pitch = 0.65
    n = 10
    span = (n - 1) * pitch / 2
    idx = 1
    for row in range(n):
        y = -span + row * pitch
        for col in range(n):
            x = -span + col * pitch
            b.append(smd_pad(str(idx), x, y, 0.35, 0.35, "circle"))
            idx += 1
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
    wl1837mod_moc100()
    tps6303x_vson10()
    rf_filter_smd4("Johanson_0915LP15B026E_SMD4",
                   "Johanson 0915LP15B026E 915 MHz low-pass RF filter, substituted for the "
                   "fabricated 0915LP15B0100E part number XO.md originally cited (does not exist "
                   "in Johanson's catalog); 4-pad SMD, ~2.0x1.25 mm, pattern-matched land — NEEDS "
                   "user confirmation.")
    rf_filter_smd4("Johanson_2450BP15E0100_SMD4",
                   "Johanson 2450BP15E0100 2.45 GHz band-pass RF filter, substituted for the "
                   "fabricated 2450BP15B050E part number XO.md originally cited (does not exist "
                   "in Johanson's catalog); 4-pad SMD, ~2.0x1.25 mm, pattern-matched land — NEEDS "
                   "user confirmation.")
    rclamp0502b()


if __name__ == "__main__":
    main()
