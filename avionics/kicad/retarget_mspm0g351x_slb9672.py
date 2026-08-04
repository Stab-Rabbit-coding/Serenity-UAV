#!/usr/bin/env python3
"""
Retarget the Serenity trust-module MCU and TPM (2026-08-03).

    CAN-PERIPH-GW-1   MSPM0G3507 RGZ-48  ->  MSPM0G3518-Q1 RHB-32 (M0G3518QRHBRQ1)
    Kaylee            MSPM0G3507 RGZ-48  ->  MSPM0G3518-Q1 RHB-32 (M0G3518QRHBRQ1)
    Jayne             MSPM0G3507 RGZ-48  ->  MSPM0G3519-Q1 RGZ-48 (M0G3519QRGZRQ1)
    all three         SLB9670VQ2.0       ->  SLB 9672AU2.0 (PG-UQFN-32-1,-2)

This is a *non-destructive injection* pass over the existing `.kicad_sch`
files.  The board generator scripts have drifted from the as-placed
schematics, so they are deliberately not re-run; this script edits the
committed schematics in place instead.

What it changes
---------------
1.  The `lib_symbols` entry for the MCU and the TPM is replaced with the new
    clean-room symbol, read from `avionics/kicad/symbols/`.
2.  Each MCU/TPM instance gets a new `lib_id`, `Value` and `Footprint`.
3.  On the two boards moving to the 32-pin RHB package, every attached global
    label is moved from its old RGZ-48 pin coordinate to the corresponding
    RHB-32 pin coordinate, following the port remap tables below.
4.  A `GND` global label is added on TPM pad 33 (the exposed thermal pad),
    which the SLB9670 symbol omitted entirely.

Pin geometry
------------
KiCad places a global label directly on a pin's connection point, so for an
instance at (ix, iy) with rotation 0 and a symbol pin at (px, py):

    label position = (ix + px, iy - py)

That identity is asserted for every connected pad before anything is written;
the script refuses to modify a board whose labels do not line up.

Port remap rationale (32-pin RHB)
---------------------------------
The RHB-32 package bonds out PA0-PA27 only - none of the PBx ports exist
(TI SLASFA6B Figure 6-6).  The five (gateway) / four (Kaylee) signals that
were on PBx are therefore rehomed onto free PA pins, choosing pins that still
offer the required peripheral function per SLASFA6B Table 6-2:

    RS485_TX       PB15 UART2_TX  ->  PA8  UART1_TX  (PF2)
    RS485_RX       PB16 UART2_RX  ->  PA9  UART1_RX  (PF2)
    RS485_DE       PB2  GPIO      ->  PA21 GPIO
    RS485_FLT_N    PB3/PA8 GPIO   ->  PA22 GPIO
    CANFD_FLT_N    PA8  GPIO      ->  PA23 GPIO      (Kaylee only)
    FLEX_PWM_IO    PB3  GPIO      ->  PA25 TIMA0_C3  (PF5, gateway only)
    FLEX_BSHOT_IO  PB6  GPIO      ->  PA26 TIMG8_C0  (PF4, gateway only)

Everything else keeps its port and only changes pad number.  Note that the
CAN and SPI1 signals stay on the same physical ports but change IOMUX PF
value on this device family (CAN0_TX/CAN0_RX move to PF12, and PA15 offers
SPI1_CS2 rather than SPI1_CS0) - a firmware pinmux change, not a wiring one.

References
----------
    [REF-SENSOR-004R] TI SLASFA6B  MSPM0G351x-Q1 datasheet, Fig 6-5/6-6, Table 6-2
    [REF-SEC-002]     Infineon SLB9672 FW16.xx datasheet Rev 1.3, Fig 6, Tables 11-13
"""

import argparse
import re
import shutil
from pathlib import Path

KICAD = Path(__file__).resolve().parent
SYMDIR = KICAD / "symbols"

MCU_OLD = "Jayne_MSPM0G3507_RGZ"
TPM_OLD = "Jayne_SLB9670_TPM"
TPM_NEW = "Jayne_SLB9672_TPM"
TPM_VALUE = "Infineon SLB 9672AU2.0"
TPM_FP = "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.6x3.6mm"

# old RGZ-48 pad -> new RHB-32 pad, for the boards moving to the 32-pin package
GW_REMAP = {
    1: 1, 2: 2, 4: 3, 6: 4, 7: 5, 8: 6, 9: 7, 10: 8, 11: 9, 12: 10, 13: 11,
    25: 12, 26: 13, 27: 16, 28: 17, 29: 18, 30: 19, 31: 20, 32: 21, 33: 22,
    34: 23, 35: 24, 14: 25, 16: 26, 43: 27, 44: 28, 15: 29, 20: 30,
    48: 32, 49: 33,
}
KAYLEE_REMAP = {
    1: 1, 2: 2, 4: 3, 6: 4, 7: 5, 8: 6, 9: 7, 10: 8, 11: 9, 12: 10, 13: 11,
    25: 12, 26: 13, 27: 16, 28: 17, 34: 23, 35: 24, 14: 25, 15: 26, 16: 27,
    48: 32, 49: 33,
}

# Kaylee carries stale global labels from a superseded draft pinmux that the
# 2026-07-26 trust-module injection replaced but never cleaned up.  The
# authoritative map is `mcu_nm` in Kaylee/scripts/inject_kaylee_trust_module.py,
# whose comment records that the draft "put CANFD_TX/RX on PA6/PA7 and
# RS485_TX/RX on PB3/PA8, none of which offer CAN or UART functions".  Those
# draft labels are still present, so today:
#   pads 17-22 (PA9,PA10,PA11,PB6,PB7,PB8) duplicate the TPM SPI bus that
#       already lands on pads 8-13, shorting six MCU GPIOs pin-to-pin, and
#   pads 41-44 strap PB20/PB24/PA23/PA24 to +3V3 while pads 45-47 strap
#       PA25/PA26/PA27 to PGND, which shorts a rail the moment firmware
#       configures any of them as an output.
# They are dropped here so the retargeted schematic matches its own documented
# intent.  See TODO.md 1.2d.
KAYLEE_STALE_PADS = {17, 18, 19, 20, 21, 22, 41, 42, 43, 44, 45, 46, 47}

BOARDS = {
    "CAN-PERIPH-GW-1": {
        "sch": KICAD / "CAN-PERIPH-GW-1/kicads/CAN-PERIPH-GW-1.kicad_sch",
        "mcu_new": "Jayne_MSPM0G3518_Q1_RHB",
        "mcu_value": "TI MSPM0G3518-Q1",
        "mcu_fp": "Package_DFN_QFN:Texas_RHB0032E_VQFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm",
        "remap": GW_REMAP,
    },
    "Kaylee": {
        "sch": KICAD / "Kaylee/kicads/Kaylee.kicad_sch",
        "mcu_new": "Jayne_MSPM0G3518_Q1_RHB",
        "mcu_value": "TI MSPM0G3518-Q1",
        "mcu_fp": "Package_DFN_QFN:Texas_RHB0032E_VQFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm",
        "remap": KAYLEE_REMAP,
    },
    "Jayne": {
        "sch": KICAD / "Jayne/kicads/Jayne.kicad_sch",
        "mcu_new": "Jayne_MSPM0G3519_Q1_RGZ",
        "mcu_value": "TI MSPM0G3519-Q1",
        # RGZ0048F exposed thermal pad is 4.1 mm square, not the 5.15 mm of the
        # Analog Devices legacy QFN outline previously referenced.
        "mcu_fp": "Package_DFN_QFN:VQFN-48-1EP_7x7mm_P0.5mm_EP4.1x4.1mm",
        "remap": None,          # identical package, pads and nets stay put
    },
}

def sexpr_blocks(text: str, head: str):
    """Yield every balanced `(<head> ...)` s-expression found in `text`.

    Paren-matched rather than line-matched so it works with both the compact
    symbol style the Serenity generators emit and the expanded style KiCad
    writes when it re-saves a library.
    """
    for m in re.finditer(r'\(%s\b' % re.escape(head), text):
        depth = 0
        for i in range(m.start(), len(text)):
            if text[i] == "(":
                depth += 1
            elif text[i] == ")":
                depth -= 1
                if depth == 0:
                    yield text[m.start():i + 1]
                    break


def symbol_block(text: str, name: str) -> str:
    """Return the whole `(symbol "<name>" ...)` block from a lib_symbols section."""
    start = text.index(f'(symbol "{name}"')
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise ValueError(f"unterminated symbol block for {name}")


def pin_coords(sym_text: str) -> dict[int, tuple[float, float]]:
    """Map pad number -> (x, y) of the pin's connection point."""
    out = {}
    for blk in sexpr_blocks(sym_text, "pin"):
        num = re.search(r'\(number\s+"(\d+)"', blk)
        at = re.search(r'\(at\s+(-?[\d.]+)\s+(-?[\d.]+)', blk)
        if not num or not at:
            continue
        out[int(num.group(1))] = (float(at.group(1)), float(at.group(2)))
    return out


def instances(text: str, lib_id: str):
    """Yield (match_start, match_end, ref, x, y, rot) for each placed instance."""
    pat = re.compile(
        r'\(symbol \(lib_id "%s"\) \(at ([\d.]+) ([\d.]+) (\d+)\)'
        r'(?:.|\n)*?\(property "Reference" "([^"]+)"' % re.escape(lib_id))
    for m in pat.finditer(text):
        x, y, rot, ref = m.groups()
        yield m.start(), ref, float(x), float(y), int(rot)


def label_index(text: str):
    """Map (x, y) -> list of (span, name) for every global label."""
    idx = {}
    for m in re.finditer(
            r'\(global_label "([^"]+)"[^\n]*\(at ([-\d.]+) ([-\d.]+) (\d+)\)', text):
        key = (round(float(m.group(2)), 2), round(float(m.group(3)), 2))
        idx.setdefault(key, []).append((m.span(), m.group(1)))
    return idx


def retarget(board: str, cfg: dict, apply_changes: bool) -> None:
    sch = cfg["sch"]
    text = sch.read_text()
    original = text

    old_sym = symbol_block(text, MCU_OLD)
    old_pins = pin_coords(old_sym)
    new_sym_src = (SYMDIR / f'{cfg["mcu_new"]}.kicad_sym').read_text()
    new_sym = symbol_block(new_sym_src, cfg["mcu_new"])
    new_pins = pin_coords(new_sym)

    remap = cfg["remap"]
    labels = label_index(text)
    moves = []          # (old_span, new_x, new_y, netname, ref, old_pad, new_pad)

    for _, ref, ix, iy, rot in instances(text, MCU_OLD):
        if rot != 0:
            raise SystemExit(f"{board}: {ref} is rotated {rot} deg; unsupported")
        for pad, (px, py) in sorted(old_pins.items()):
            key = (round(ix + px, 2), round(iy - py, 2))
            found = labels.get(key)
            if not found:
                continue                      # pad is unconnected on this board
            span, name = found[0]
            new_pad = pad if remap is None else remap.get(pad)
            if new_pad is None:
                raise SystemExit(
                    f"{board}: {ref} pad {pad} carries net {name} but has no "
                    f"entry in the remap table")
            nx, ny = new_pins[new_pad]
            moves.append((span, round(ix + nx, 2), round(iy - ny, 2),
                          name, ref, pad, new_pad))

    print(f"\n=== {board}: {len(moves)} MCU label(s) across "
          f"{len({m[4] for m in moves})} instance(s)")
    for _, nx, ny, name, ref, pad, new_pad in moves:
        if pad != new_pad or remap is None:
            tag = "" if remap is None else "  <- REPINNED"
            print(f"   {ref:<6} pad {pad:>2} -> {new_pad:>2}  {name}{tag}")

    # Apply label moves back-to-front so earlier spans stay valid.
    for span, nx, ny, *_ in sorted(moves, key=lambda m: m[0][0], reverse=True):
        seg = text[span[0]:span[1]]
        seg = re.sub(r'\(at [-\d.]+ [-\d.]+ (\d+)\)',
                     lambda m: f'(at {nx:g} {ny:g} {m.group(1)})', seg)
        text = text[:span[0]] + seg + text[span[1]:]

    # Swap the MCU library symbol and every instance's identity properties.
    text = text.replace(old_sym, new_sym)
    text = text.replace(f'(lib_id "{MCU_OLD}")', f'(lib_id "{cfg["mcu_new"]}")')
    text = re.sub(r'\(property "Value" "TI MSPM0G3507"',
                  f'(property "Value" "{cfg["mcu_value"]}"', text)
    text = text.replace(
        '(property "Footprint" "Package_DFN_QFN:QFN-48-1EP_7x7mm_P0.5mm_EP5.15x5.15mm"',
        f'(property "Footprint" "{cfg["mcu_fp"]}"')

    # --- TPM -------------------------------------------------------------
    tpm_old_sym = symbol_block(text, TPM_OLD)
    tpm_new_sym = symbol_block((SYMDIR / f"{TPM_NEW}.kicad_sym").read_text(), TPM_NEW)
    tpm_pins = pin_coords(tpm_new_sym)

    # Add the missing exposed-pad ground label on every TPM instance.
    ep_x, ep_y = tpm_pins[33]
    added = []
    for _, ref, ix, iy, rot in list(instances(text, TPM_OLD)):
        added.append((ref, round(ix + ep_x, 2), round(iy - ep_y, 2)))

    text = text.replace(tpm_old_sym, tpm_new_sym)
    text = text.replace(f'(lib_id "{TPM_OLD}")', f'(lib_id "{TPM_NEW}")')
    text = re.sub(r'\(property "Value" "Infineon SLB9670"',
                  f'(property "Value" "{TPM_VALUE}"', text)
    text = text.replace(
        '(property "Footprint" "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm"',
        f'(property "Footprint" "{TPM_FP}"')

    ep_labels = "".join(
        f'  (global_label "GND" (shape bidirectional) (at {x:g} {y:g} 180)\n'
        f'    (effects (font (size 1.016 1.016)))\n'
        f'    (uuid "9672ep00-0000-0000-0000-{i:012x}")\n'
        f'    (property "Intersheet References" "${{INTERSHEET_REFS}}" '
        f'(at {x:g} {y:g} 0)\n'
        f'      (effects (font (size 1.016 1.016)) (hide yes))))\n'
        for i, (_, x, y) in enumerate(added))
    text = text.rstrip()
    assert text.endswith(")"), "schematic does not end with a closing paren"
    text = text[:-1] + ep_labels + ")\n"

    print(f"    TPM: {len(added)} instance(s) -> {TPM_VALUE}, "
          f"exposed pad 33 tied to GND")

    if not apply_changes:
        print("    (dry run, nothing written)")
        return
    if text == original:
        print("    no change")
        return
    backup = sch.with_suffix(sch.suffix + ".pre-g351x")
    if not backup.exists():
        shutil.copy2(sch, backup)
    sch.write_text(text)
    print(f"    written; backup at {backup.name}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true",
                    help="write the changes (default is a dry run)")
    ap.add_argument("--board", choices=sorted(BOARDS), action="append",
                    help="limit to one board (repeatable)")
    args = ap.parse_args()

    for name in (args.board or sorted(BOARDS)):
        retarget(name, BOARDS[name], args.apply)


if __name__ == "__main__":
    main()
