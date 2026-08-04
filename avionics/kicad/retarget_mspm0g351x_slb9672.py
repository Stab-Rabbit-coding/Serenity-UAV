#!/usr/bin/env python3
"""
Retarget the Serenity trust-module MCU and TPM (2026-08-03).

    CAN-PERIPH-GW-1   MSPM0G3507 RGZ-48  ->  MSPM0G3518-Q1 RHB-32 (M0G3518QRHBRQ1)
    FlightEngineer            MSPM0G3507 RGZ-48  ->  MSPM0G3518-Q1 RHB-32 (M0G3518QRHBRQ1)
    Observer             MSPM0G3507 RGZ-48  ->  MSPM0G3519-Q1 RGZ-48 (M0G3519QRGZRQ1)
    all three         SLB9670VQ2.0       ->  SLB 9672AU2.0 (PG-UQFN-32-1,-2)

ALREADY APPLIED. This pass ran on 2026-08-03 and is kept for audit and
reproducibility; the symbols it consumes were renamed afterwards when main
moved the boards to crew-role names, so it cannot be replayed as-is.

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
    CANFD_FLT_N    PA8  GPIO      ->  PA23 GPIO      (FlightEngineer only)
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

MCU_OLD = "Observer_MSPM0G3507_RGZ"
TPM_OLD = "Observer_SLB9670_TPM"
TPM_NEW = "SLB9672_TPM"
TPM_VALUE = "Infineon SLB 9672AU2.0"
TPM_FP = "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.6x3.6mm"

# old RGZ-48 pad -> new RHB-32 pad, for the boards moving to the 32-pin package
GW_REMAP = {
    1: 1, 2: 2, 4: 3, 6: 4, 7: 5, 8: 6, 9: 7, 10: 8, 11: 9, 12: 10, 13: 11,
    25: 12, 26: 13, 27: 16, 28: 17, 29: 18, 30: 19, 31: 20, 32: 21, 33: 22,
    34: 23, 35: 24, 14: 25, 16: 26, 43: 27, 44: 28, 15: 29, 20: 30,
    48: 32, 49: 33,
}
FLIGHT_ENGINEER_REMAP = {
    1: 1, 2: 2, 4: 3, 6: 4, 7: 5, 8: 6, 9: 7, 10: 8, 11: 9, 12: 10, 13: 11,
    25: 12, 26: 13, 27: 16, 28: 17, 34: 23, 35: 24, 14: 25, 15: 26, 16: 27,
    48: 32, 49: 33,
}

# FlightEngineer has a pre-existing schematic-layout defect: U_MCU (at y=90.17, a
# 49-pin symbol 68.6 mm tall) and U_TPM (at y=129.54, 66 mm tall) are drawn on
# top of each other.  Seventeen MCU pads land on the exact coordinate of a TPM
# pad, so a single global label serves both symbols and silently shorts them:
#
#     MCU 17..24 == TPM 20,19,21,24,18,17,6,7   (the whole SPI bus + two NCI)
#     MCU 41..47 == TPM 8,22,1,14,2,9,23        (the TPM's supply pins)
#     MCU 48     == TPM 32   -> MCU VCORE tied to TPM GND
#     MCU 49     == TPM 16
#
# That is what the baseline `pin_to_pin` ERC errors are reporting.  Shrinking
# the MCU to the 32-pin symbol does not clear it (the MCU still reaches
# y=110.49 and the TPM starts at y=104.14), so the TPM is moved down out of the
# way first and its labels re-emitted from its authoritative pin map before the
# MCU is remapped.  See TODO.md 1.2d.
FLIGHT_ENGINEER_TPM_SHIFT = 34.29        # mm, clears the retargeted MCU with margin

# Authoritative TPM pin map: `tpm_nm` in
# FlightEngineer/scripts/inject_flight_engineer_trust_module.py, plus pad 33 (exposed pad).
FLIGHT_ENGINEER_TPM_NETS = {
    1: "+3V3", 2: "PGND", 8: "+3V3", 9: "PGND", 14: "+3V3", 16: "PGND",
    17: "TPM_RESET_N", 18: "TPM_PIRQ", 19: "TPM_SPI_SCK", 20: "TPM_SPI_CS",
    21: "TPM_SPI_MOSI", 22: "+3V3", 23: "PGND", 24: "TPM_SPI_MISO",
    32: "PGND", 33: "PGND",
}

BOARDS = {
    "CAN-PERIPH-GW-1": {
        "sch": KICAD / "CAN-PERIPH-GW-1/kicads/CAN-PERIPH-GW-1.kicad_sch",
        "mcu_new": "MSPM0G3518_Q1_RHB",
        "mcu_value": "TI MSPM0G3518-Q1",
        "mcu_fp": "Package_DFN_QFN:Texas_RHB0032E_VQFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm",
        "remap": GW_REMAP,
    },
    "FlightEngineer": {
        "sch": KICAD / "FlightEngineer/kicads/FlightEngineer.kicad_sch",
        "mcu_new": "MSPM0G3518_Q1_RHB",
        "mcu_value": "TI MSPM0G3518-Q1",
        "mcu_fp": "Package_DFN_QFN:Texas_RHB0032E_VQFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm",
        "remap": FLIGHT_ENGINEER_REMAP,
        "tpm_shift": FLIGHT_ENGINEER_TPM_SHIFT,
        "tpm_nets": FLIGHT_ENGINEER_TPM_NETS,
        # MCU pads 48/49 shared a coordinate with TPM pads 32/16, so clearing
        # the TPM's labels also removed the MCU's.  Restore them from the
        # authoritative `mcu_nm` map before the remap runs.
        "mcu_restore": {48: "MCU_VCORE", 49: "PGND"},
    },
    "Observer": {
        "sch": KICAD / "Observer/kicads/Observer.kicad_sch",
        "mcu_new": "MSPM0G3519_Q1_RGZ",
        "mcu_value": "TI MSPM0G3519-Q1",
        # RGZ0048F exposed thermal pad is 4.1 mm square, not the 5.15 mm of the
        # Analog Devices legacy QFN outline previously referenced.
        "mcu_fp": "Package_DFN_QFN:VQFN-48-1EP_7x7mm_P0.5mm_EP4.1x4.1mm",
        "remap": None,          # identical package, pads and nets stay put
    },
}


def _cut(text: str, start: int) -> str:
    """Delete the balanced s-expression at `start`, plus its line whitespace."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    else:
        raise ValueError("unterminated s-expression")
    while end < len(text) and text[end] in " \t":
        end += 1
    if end < len(text) and text[end] == "\n":
        end += 1
    while start > 0 and text[start - 1] in " \t":
        start -= 1
    return text[:start] + text[end:]


def _no_connects(text: str) -> dict:
    """Map (x, y) -> match start for every no-connect marker."""
    return {(round(float(m.group(1)), 2), round(float(m.group(2)), 2)): m.start()
            for m in re.finditer(r'\(no_connect \(at ([-\d.]+) ([-\d.]+)\)[^\n]*\)', text)}


def _add_no_connects(text: str, coords) -> str:
    add = "".join(
        f'  (no_connect (at {x:g} {y:g}) '
        f'(uuid "9351nc00-0000-0000-0000-{i:012x}"))\n'
        for i, (x, y) in enumerate(sorted(set(coords))))
    text = text.rstrip()
    return text[:-1] + add + ")\n"


def all_pin_coords(text: str, exclude: set) -> set:
    """Every pin coordinate of every placed symbol whose lib_id is not excluded.

    FlightEngineer stacks U_MCU, U_TPM and U_ISOCAN on top of one another, so a label
    sitting on a TPM pin may in fact belong to a third symbol.  Relocating the
    TPM must not take those labels with it.
    """
    libs = {}
    for m in re.finditer(r'\(symbol "([A-Za-z0-9_]+)" \(pin_names', text):
        name = m.group(1)
        try:
            libs[name] = pin_coords(symbol_block(text, name))
        except Exception:
            continue
    out = set()
    for lib, pins in libs.items():
        if lib in exclude:
            continue
        for _, _ref, ix, iy, rot in instances(text, lib):
            for px, py in pins.values():
                out.add((round(ix + px, 2), round(iy - py, 2)))
    return out


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
    # Match a full float including any exponent: a coordinate written as
    # "3.55271e-15" must not be read as 3.55271.
    num_pat = r'[-+]?[\d.]+(?:[eE][-+]?\d+)?'
    out = {}
    for blk in sexpr_blocks(sym_text, "pin"):
        num = re.search(r'\(number\s+"(\d+)"', blk)
        at = re.search(r'\(at\s+(%s)\s+(%s)' % (num_pat, num_pat), blk)
        if not num or not at:
            continue
        out[int(num.group(1))] = (round(float(at.group(1)), 2),
                                  round(float(at.group(2)), 2))
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
    idx: dict[tuple[float, float], list] = {}
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
    drop_pads: set[int] = set()

    # --- FlightEngineer only: separate the overlapping TPM before touching the MCU ---
    shift = cfg.get("tpm_shift")
    if shift:
        dy = float(shift)
        # Geometry comes from the *new* symbol: it is pin-for-pin identical to
        # the SLB9670 for pads 1-32 and additionally carries pad 33 (the
        # exposed pad), which the old symbol omitted.
        tpm_pin = pin_coords(symbol_block(
            (SYMDIR / f"{TPM_NEW}.kicad_sym").read_text(), TPM_NEW))
        labs0 = label_index(text)
        for _, tref, tix, tiy, trot in list(instances(text, TPM_OLD)):
            # Drop every label sitting on a TPM pin; they are re-emitted below
            # at the relocated position, and any that were shared with an MCU
            # pad must not be left behind to keep shorting the two symbols.
            others = all_pin_coords(text, {TPM_OLD, MCU_OLD})
            kill, restore = [], []
            for pad, (px, py) in tpm_pin.items():
                key = (round(tix + px, 2), round(tiy - py, 2))
                for span, name in labs0.get(key, []):
                    kill.append(span)
                    if key in others:
                        # Belongs to a third symbol stacked at this point.
                        restore.append((key, name))
            for span in sorted(set(kill), key=lambda s: s[0], reverse=True):
                depth = 0
                for i in range(span[0], len(text)):
                    if text[i] == "(":
                        depth += 1
                    elif text[i] == ")":
                        depth -= 1
                        if depth == 0:
                            end = i + 1
                            break
                while end < len(text) and text[end] in " \t":
                    end += 1
                if end < len(text) and text[end] == "\n":
                    end += 1
                start = span[0]
                while start > 0 and text[start - 1] in " \t":
                    start -= 1
                text = text[:start] + text[end:]

            # Move the instance itself.
            old_at = '(symbol (lib_id "%s") (at %g %g %d)' % (TPM_OLD, tix, tiy, trot)
            new_at = '(symbol (lib_id "%s") (at %g %g %d)' % (TPM_OLD, tix, tiy + shift, trot)
            if old_at not in text:
                raise SystemExit(f"{board}: could not find {tref} placement to shift")
            text = text.replace(old_at, new_at, 1)
            prop_at = (r'(\(property "(?:Reference|Value)" "[^"]*" '
                       r'\(at %g )([\d.]+)( \d+\))' % tix)
            text = re.sub(
                prop_at,
                lambda m: f"{m.group(1)}{float(m.group(2)) + dy:g}{m.group(3)}",
                text)

            # Re-emit the TPM's labels at the relocated pin coordinates.
            add = []
            for pad, net in sorted(cfg["tpm_nets"].items()):
                px, py = tpm_pin[pad]
                x = round(tix + px, 2)
                y = round(tiy + shift - py, 2)
                rot = 0 if px > 0 else 180
                add.append(
                    f'  (global_label "{net}" (shape bidirectional) (at {x:g} {y:g} {rot})\n'
                    f'    (effects (font (size 1.016 1.016)))\n'
                    f'    (uuid "9672tpm0-0000-0000-0000-{pad:012x}")\n'
                    f'    (property "Intersheet References" "${{INTERSHEET_REFS}}" '
                    f'(at {x:g} {y:g} 0)\n'
                    f'      (effects (font (size 1.016 1.016)) (hide yes))))\n')
            # Enumerate rather than hash for the uuid suffix: hash() is salted
            # per interpreter run, so hashing would make the output differ
            # between otherwise identical runs of this script.
            for n, ((x, y), name) in enumerate(sorted(set(restore))):
                add.append(
                    f'  (global_label "{name}" (shape bidirectional) '
                    f'(at {x:g} {y:g} {0 if x > tix else 180})\n'
                    f'    (effects (font (size 1.016 1.016)))\n'
                    f'    (uuid "9672rst0-0000-0000-0000-{n:012x}")\n'
                    f'    (property "Intersheet References" "${{INTERSHEET_REFS}}" '
                    f'(at {x:g} {y:g} 0)\n'
                    f'      (effects (font (size 1.016 1.016)) (hide yes))))\n')

            text = text.rstrip()
            text = text[:-1] + "".join(add) + ")\n"
            if restore:
                print(f"    {tref}: restored {len(set(restore))} label(s) "
                      f"belonging to symbols stacked at the same coordinates")

            # The TPM's own no-connect markers stayed behind at the old
            # position; move them with it.
            nc = _no_connects(text)
            drop = [nc[(round(tix + px, 2), round(tiy - py, 2))]
                    for px, py in tpm_pin.values()
                    if (round(tix + px, 2), round(tiy - py, 2)) in nc]
            for s in sorted(set(drop), reverse=True):
                text = _cut(text, s)
            text = _add_no_connects(text, [
                (round(tix + px, 2), round(tiy + shift - py, 2))
                for pad, (px, py) in tpm_pin.items() if pad not in cfg["tpm_nets"]])
            n_tpm_nets = len(cfg["tpm_nets"])
            print(f"    {tref}: moved +{shift:g} mm clear of the MCU, "
                  f"{len(set(kill))} shared label(s) replaced by "
                  f"{n_tpm_nets} from its authoritative pin map")

    for pad, net in sorted(cfg.get("mcu_restore", {}).items()):
        for _, mref, mix, miy, _ in list(instances(text, MCU_OLD)):
            px, py = old_pins[pad]
            x, y = round(mix + px, 2), round(miy - py, 2)
            rot = 0 if px > 0 else 180
            text = text.rstrip()
            text = text[:-1] + (
                f'  (global_label "{net}" (shape bidirectional) (at {x:g} {y:g} {rot})\n'
                f'    (effects (font (size 1.016 1.016)))\n'
                f'    (uuid "9351mcu0-0000-0000-0000-{pad:012x}")\n'
                f'    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {x:g} {y:g} 0)\n'
                f'      (effects (font (size 1.016 1.016)) (hide yes))))\n') + ")\n"
            print(f"    {mref}: restored pad {pad} label {net!r}")

    labels = label_index(text)
    moves = []          # (old_span, new_x, new_y, netname, ref, old_pad, new_pad)
    drops = []          # (old_span, netname, ref, old_pad)

    for _, ref, ix, iy, rot in instances(text, MCU_OLD):
        if rot != 0:
            raise SystemExit(f"{board}: {ref} is rotated {rot} deg; unsupported")
        for pad, (px, py) in sorted(old_pins.items()):
            key = (round(ix + px, 2), round(iy - py, 2))
            found = labels.get(key)
            if not found:
                continue                      # pad is unconnected on this board
            span, name = found[0]
            if pad in drop_pads:
                drops.append((span, name, ref, pad))
                continue
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

    for _, name, ref, pad in drops:
        print(f"   {ref:<6} pad {pad:>2}     {name}  <- DROPPED (stale draft label)")

    # Delete the stale labels whole, back-to-front so earlier spans stay valid.
    # The extent has to be found by matching parens from the opening
    # `(global_label`: a label body contains several nested `)))` runs of its
    # own, so scanning for a literal paren run truncates it mid-way.
    for span, *_ in sorted(drops, key=lambda d: d[0][0], reverse=True):
        depth = 0
        for i in range(span[0], len(text)):
            if text[i] == "(":
                depth += 1
            elif text[i] == ")":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        else:
            raise SystemExit(f"{board}: unterminated global_label at {span[0]}")
        while end < len(text) and text[end] in " \t":
            end += 1
        if end < len(text) and text[end] == "\n":
            end += 1
        start = span[0]
        while start > 0 and text[start - 1] in " \t":
            start -= 1
        text = text[:start] + text[end:]

    # Recompute move spans after the deletions shifted the text.
    if drops:
        labels = label_index(text)
        rebuilt = []
        for _, ref, ix, iy, rot in instances(text, MCU_OLD):
            for pad, (px, py) in sorted(old_pins.items()):
                if pad in drop_pads:
                    continue
                key = (round(ix + px, 2), round(iy - py, 2))
                found = labels.get(key)
                if not found:
                    continue
                span, name = found[0]
                new_pad = remap[pad] if remap else pad
                nx, ny = new_pins[new_pad]
                rebuilt.append((span, round(ix + nx, 2), round(iy - ny, 2),
                                name, ref, pad, new_pad))
        moves = rebuilt

    # Apply label moves back-to-front so earlier spans stay valid.
    for span, nx, ny, *_ in sorted(moves, key=lambda m: m[0][0], reverse=True):
        seg = text[span[0]:span[1]]
        seg = re.sub(r'\(at [-\d.]+ [-\d.]+ (\d+)\)',
                     lambda m: f'(at {nx:g} {ny:g} {m.group(1)})', seg)
        text = text[:span[0]] + seg + text[span[1]:]

    # --- no-connect markers ------------------------------------------------
    # The old symbol carried `(no_connect ...)` markers on its unused pins.
    # After a 48 -> 32 pin swap those sit at coordinates the new symbol has no
    # pin at, so KiCad reports them as dangling; meanwhile the new symbol's own
    # unused pins have nothing on them.  Rebuild the set: drop every marker
    # that belongs to an MCU pin, then re-emit one for each new-symbol pin that
    # ends up with neither a label nor a connection.
    if remap is not None:
        # Remove every marker belonging to an old MCU pin first, then work out
        # which of the *new* pins still need one.  Computing "fresh" against
        # the pre-deletion marker set would skip any new pin that happened to
        # share a coordinate with a stale marker, leaving it unconnected.
        stale = []
        for _, ref, ix, iy, rot in instances(text, MCU_OLD):
            nc = _no_connects(text)
            for px, py in old_pins.values():
                key = (round(ix + px, 2), round(iy - py, 2))
                if key in nc:
                    stale.append(nc[key])
        n_stale = len(set(stale))
        for s in sorted(set(stale), reverse=True):
            text = _cut(text, s)

        labels_now = label_index(text)
        nc = _no_connects(text)
        fresh = []
        for _, ref, ix, iy, rot in instances(text, MCU_OLD):
            for px, py in new_pins.values():
                key = (round(ix + px, 2), round(iy - py, 2))
                if key not in labels_now and key not in nc:
                    fresh.append(key)
        text = _add_no_connects(text, fresh)
        print(f"    no-connect: removed {n_stale} stale, added {len(set(fresh))}")

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
