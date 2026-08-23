#!/usr/bin/env python3
"""Snap power-symbol instances onto the pins they were meant to touch.

Second systematic defect in the generated FlightEngineer.kicad_sch (after the
Y-inversion fixed by fix_flight_engineer_yinv.py): the power symbols in this file
(PGND, VDIS, VBAT, ...) have their lib pin at (0, -1.27), NOT at the symbol
origin — but the generator placed every power-symbol instance with its
ORIGIN on the target pin.  The rendered power pin therefore sits exactly
1.27 mm away from the component pin (direction depends on the instance
rotation), producing paired ``pin_not_connected`` ERC errors.

Fix: compute each power instance's true pin position
(``sheet_pin = instance + R(theta) . (px, -py)``, KiCad canvas, CCW-positive
theta), find the unique non-power component pin within 1.5 mm, and translate
the instance so the two pins coincide.  Ambiguous cases (0 or >1 candidate)
are left in place and counted.

Authored by Claude Fable 5 (Anthropic), 2026-07-21.  License: CC BY 4.0.
"""

import math
import re
import sys
from pathlib import Path

SCH = Path(__file__).resolve().parents[1] / "kicads" / "FlightEngineer.kicad_sch"
SNAP = 1.5


def parse_lib_pins(src):
    lib = {}
    for m in re.finditer(r'\n  \(symbol "([^"]+)"( \(power\))?', src):
        name, power = m.group(1), bool(m.group(2))
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


def rot(px, py, theta):
    """KiCad canvas rotation (y down, CCW-positive angles)."""
    t = math.radians(theta)
    c, s = round(math.cos(t)), round(math.sin(t))
    return (px * c + py * s, -px * s + py * c)


def main():
    src = SCH.read_text()
    libsec_end = src.find("\n  (text ")
    lib = parse_lib_pins(src[:libsec_end])

    instances = [
        (m.group(1), float(m.group(2)), float(m.group(3)), int(m.group(4)))
        for m in re.finditer(
            r'\(symbol \(lib_id "([^"]+)"\) \(at ([\d.]+) ([\d.]+) (\d+)\)', src
        )
    ]

    # Real pin positions of all NON-power instances (all at rotation 0).
    comp_pins = set()
    for name, x, y, theta in instances:
        pins, power = lib.get(name, ([], False))
        if power:
            continue
        for px, py in pins:
            dx, dy = rot(px, -py, theta)
            comp_pins.add((round(x + dx, 2), round(y + dy, 2)))

    snapped = [0]
    skipped = [0]

    def move_pwr(m):
        name, x, y, theta = (
            m.group(1),
            float(m.group(2)),
            float(m.group(3)),
            int(m.group(4)),
        )
        pins, power = lib.get(name, ([], False))
        if not power or not pins:
            return m.group(0)
        px, py = pins[0]
        dx, dy = rot(px, -py, theta)
        pin = (round(x + dx, 2), round(y + dy, 2))
        if pin in comp_pins:
            return m.group(0)  # already mates with a component pin
        # Origin rule: the generator put the instance ORIGIN on the intended
        # pin (assuming a pin-at-origin symbol); translate so the rendered
        # pin lands where the origin was.
        if (round(x, 2), round(y, 2)) in comp_pins:
            snapped[0] += 1
            return (
                f'(symbol (lib_id "{name}") '
                f"(at {x - dx:.2f} {y - dy:.2f} {theta})"
            )
        near = [
            p
            for p in comp_pins
            if (p[0] - pin[0]) ** 2 + (p[1] - pin[1]) ** 2 <= SNAP * SNAP
        ]
        if len(near) != 1:
            skipped[0] += 1
            return m.group(0)
        nx = x + (near[0][0] - pin[0])
        ny = y + (near[0][1] - pin[1])
        snapped[0] += 1
        return f'(symbol (lib_id "{name}") (at {nx:.2f} {ny:.2f} {theta})'

    src = re.sub(
        r'\(symbol \(lib_id "([^"]+)"\) \(at ([\d.]+) ([\d.]+) (\d+)\)',
        move_pwr,
        src,
    )

    SCH.write_text(src)
    print(f"power symbols snapped: {snapped[0]}, ambiguous/no-target: {skipped[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
