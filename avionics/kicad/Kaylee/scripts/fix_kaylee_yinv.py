#!/usr/bin/env python3
"""Repair the Y-inversion label-placement bug in Kaylee.kicad_sch.

The original generator placed every pin-attached item (global labels,
no-connects, power-symbol instances) at ``instance_y + lib_pin_y``.  KiCad's
real transform is ``instance_y - lib_pin_y`` (lib Y is inverted on the sheet
— see the project's KiCad hand-authoring notes), so on every asymmetric
multi-pin symbol the labels attach to the vertically-mirrored WRONG pin
(e.g. FB5V1_OUT landing on the TPS54620's GND pin).  This is the root cause
of Kaylee's ~247 pre-existing ERC errors.

Fix: for every non-power symbol instance (all are rotation 0, verified), for
every lib pin with a non-zero Y offset, any movable item found at the buggy
attach point (X+px, Y+py) is moved to the correct point (X+px, Y-py).
Two-pin horizontal passives (py == 0) are naturally invariant.

Authored by Claude Fable 5 (Anthropic), 2026-07-21.  License: CC BY 4.0.
"""

import re
import sys
from pathlib import Path

SCH = Path(__file__).resolve().parents[1] / "kicads" / "Kaylee.kicad_sch"
TOL = 0.02


def parse_lib_pins(src):
    """lib symbol name -> ([(px, py)], is_power) from the lib_symbols block."""
    lib = {}
    # top-level lib symbols start at two-space indent inside (lib_symbols ...)
    for m in re.finditer(r'\n  \(symbol "([^"]+)"( \(power\))?', src):
        name, power = m.group(1), bool(m.group(2))
        # block ends at the next top-level '  (symbol "' or the section end
        nxt = re.search(r'\n  \(symbol "', src[m.end():])
        block = src[m.end(): m.end() + nxt.start()] if nxt else src[m.end():]
        pins = [
            (float(a), float(b))
            for a, b in re.findall(
                r'\(pin [a-z_]+\s+line \(at\s+(-?[\d.]+)\s+(-?[\d.]+)', block
            )
        ]
        lib[name] = (pins, power)
    return lib


def main():
    src = SCH.read_text()
    libsec_end = src.find("\n  (text ")  # instances begin after the lib section
    lib = parse_lib_pins(src[:libsec_end])

    # Every placed symbol instance: (lib_id, x, y, rot)
    instances = [
        (m.group(1), float(m.group(2)), float(m.group(3)), int(m.group(4)))
        for m in re.finditer(
            r'\(symbol \(lib_id "([^"]+)"\) \(at ([\d.]+) ([\d.]+) (\d+)\)', src
        )
    ]

    # Buggy attach point -> corrected attach point, from non-power instances.
    moves = {}
    for name, x, y, rot in instances:
        pins, power = lib.get(name, ([], False))
        if power or rot != 0:
            continue
        for px, py in pins:
            if abs(py) < 1e-9:
                continue
            moves[(round(x + px, 2), round(y + py, 2))] = (
                round(x + px, 2),
                round(y - py, 2),
            )

    moved = [0]

    # 1. global labels: (global_label "NET" (shape ...) (at X Y R)
    def move_glabel(m):
        x, y = float(m.group(2)), float(m.group(3))
        key = (round(x, 2), round(y, 2))
        if key in moves:
            nx, ny = moves[key]
            moved[0] += 1
            return f"{m.group(1)}(at {nx:.2f} {ny:.2f} {m.group(4)})"
        return m.group(0)

    src = re.sub(
        r'(\(global_label "[^"]+" \(shape [a-z_]+\) )\(at ([\d.]+) ([\d.]+) (\d+)\)',
        move_glabel,
        src,
    )
    # 2. no_connects: (no_connect (at X Y)
    def move_nc(m):
        x, y = float(m.group(1)), float(m.group(2))
        key = (round(x, 2), round(y, 2))
        if key in moves:
            nx, ny = moves[key]
            moved[0] += 1
            return f"(no_connect (at {nx:.2f} {ny:.2f})"
        return m.group(0)

    src = re.sub(r"\(no_connect \(at ([\d.]+) ([\d.]+)\)", move_nc, src)

    # 3. power-symbol instances: move the whole instance (at ...) — their pin
    #    sits at the instance origin, so only the instance position matters.
    powers = {n for n, (_p, pw) in lib.items() if pw}

    def move_pwr(m):
        name, x, y, rot = m.group(1), float(m.group(2)), float(m.group(3)), m.group(4)
        if name not in powers:
            return m.group(0)
        key = (round(x, 2), round(y, 2))
        if key in moves:
            nx, ny = moves[key]
            moved[0] += 1
            return f'(symbol (lib_id "{name}") (at {nx:.2f} {ny:.2f} {rot})'
        return m.group(0)

    src = re.sub(
        r'\(symbol \(lib_id "([^"]+)"\) \(at ([\d.]+) ([\d.]+) (\d+)\)',
        move_pwr,
        src,
    )

    SCH.write_text(src)
    print(f"pin-attach points remapped: {len(moves)}; items moved: {moved[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
