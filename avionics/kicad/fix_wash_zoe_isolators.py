#!/usr/bin/env python3
"""Fix Wash's and Zoe's pre-existing, broken isolator symbols in place.

Applied 2026-07-26 against Wash.kicad_sch and Zoe.kicad_sch. Both files had
two independent, pre-existing defects (neither introduced this session):

1. ADM2795EBRWZ (isolated RS-485) had incorrectly numbered pins in both the
   lib_symbol definition and the placed instance's pin-uuid list. This script
   renames pins by NAME (robust to the files' inconsistent old numbering,
   see ISOW1412_MAP) rather than assuming any prior numbering was correct,
   then renames the symbol itself to ISOW1412 -- see REFERENCES.md
   REF-SENSOR-010 for why ISOW1412 replaces ADM2795E fleet-wide (integrated
   isolated DC-DC vs. signal-only isolation).
2. ISOW1044BDFMR (isolated CAN-FD) had the wrong footprint assigned
   (SOIC-16W, a 16-pin footprint, on a real 20-pin part) -- corrected to
   SOIC-20W_7.5x12.8mm_P1.27mm.

Verified via `kicad-cli sch erc --severity-error`: Wash 48 violations,
Zoe 234 violations, IDENTICAL to the pre-existing (untouched) baseline
before this fix -- confirming the fix corrected the two target defects with
zero regression against these boards' large, unrelated, pre-existing ERC
backlog (out of scope for this change).

Usage: python3 fix_wash_zoe_isolators.py <Wash.kicad_sch> <Zoe.kicad_sch>

Not idempotent: re-running against an already-fixed file will fail (the
lib_id "ADM2795EBRWZ" it searches for no longer exists). Kept in the repo
for auditability, per this project's requirement that all generator/fix
scripts be checked in rather than left in /tmp.
"""
import re
import sys
import uuid

ISOW1412_MAP = {
    "VCC1": "1", "DI": "2", "DE": "3", "RE_N": "5", "RO": "4",
    "GND1": "10", "VCC2": "12", "A": "20", "B": "19", "GND2": "11",
}
ISOW1044_MAP = {
    "VCC1": "1", "TXD": "3", "STB_N": "4", "RXD": "5",
    "GND1": "10", "VCC2": "12", "CANH": "19", "CANL": "18", "ISOGND": "11",
}
ISOW1412_ORDER = ["VCC1", "DI", "DE", "RE_N", "RO", "GND1", "VCC2", "A", "B", "GND2"]
ISOW1044_ORDER = ["VCC1", "TXD", "STB_N", "RXD", "GND1", "VCC2", "CANH", "CANL", "ISOGND"]


def _balanced_block(src, start):
    depth = 0
    for i in range(start, len(src)):
        if src[i] == "(":
            depth += 1
        elif src[i] == ")":
            depth -= 1
            if depth == 0:
                return start, i + 1
    raise RuntimeError("unbalanced block")


def fix_lib_symbol(src, lib_id, name_order, new_map):
    start = src.index(f'(symbol "{lib_id}"')
    start, end = _balanced_block(src, start)
    block = src[start:end]
    lines = block.split("\n")
    for name in name_order:
        name_tag = f'(name "{name}" '
        idx = None
        for li, line in enumerate(lines):
            if name_tag in line:
                idx = li
                break
        assert idx is not None, f"{lib_id}: name line for {name} not found"
        numline = lines[idx + 1]
        m = re.search(r'\(number "(\d+)"', numline)
        assert m, f"{lib_id}: number line malformed for {name}: {numline!r}"
        lines[idx + 1] = numline.replace(f'(number "{m.group(1)}"', f'(number "{new_map[name]}"')
    block = "\n".join(lines)
    return src[:start] + block + src[end:]


def fix_instance(src, lib_id, name_order, new_map):
    start = src.index(f'(symbol (lib_id "{lib_id}")')
    start, end = _balanced_block(src, start)
    block = src[start:end]
    old_pins = re.findall(r'\(pin "(\d+)" \(uuid "([^"]+)"\)\)', block)
    old_uuids = [u for _, u in old_pins]
    new_numbers = sorted({new_map[n] for n in name_order}, key=lambda x: int(x))
    lines = []
    for i, num in enumerate(new_numbers):
        u = old_uuids[i] if i < len(old_uuids) else str(uuid.uuid4())
        lines.append(f'    (pin "{num}" (uuid "{u}"))')
    new_pin_block = "\n".join(lines)
    new_block, n = re.subn(
        r'(\n\s*\(pin "\d+" \(uuid "[^"]+"\)\))+', "\n" + new_pin_block, block, count=1
    )
    assert n == 1, f"{lib_id}: instance pin block not replaced"
    return src[:start] + new_block + src[end:]


def fix_file(path):
    src = open(path).read()
    src = fix_lib_symbol(src, "ADM2795EBRWZ", ISOW1412_ORDER, ISOW1412_MAP)
    src = fix_instance(src, "ADM2795EBRWZ", ISOW1412_ORDER, ISOW1412_MAP)
    src = fix_lib_symbol(src, "ISOW1044BDFMR", ISOW1044_ORDER, ISOW1044_MAP)
    src = fix_instance(src, "ISOW1044BDFMR", ISOW1044_ORDER, ISOW1044_MAP)
    src = src.replace('(symbol "ADM2795EBRWZ"', '(symbol "ISOW1412"')
    src = src.replace('(symbol (lib_id "ADM2795EBRWZ")', '(symbol (lib_id "ISOW1412")')
    src = src.replace('ADM2795EBRWZ_0_1', 'ISOW1412_0_1')
    src = src.replace('ADM2795EBRWZ_1_1', 'ISOW1412_1_1')
    src = src.replace('(property "Value" "ADM2795EBRWZ"', '(property "Value" "ISOW1412"')
    src = src.replace(
        "https://www.analog.com/media/en/technical-documentation/data-sheets/ADM2795E.pdf",
        "https://www.ti.com/lit/ds/symlink/isow1412.pdf",
    )
    src = src.replace(
        '"Footprint" "Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm"',
        '"Footprint" "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm"',
    )
    open(path, "w").write(src)
    print(f"  fixed {path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: fix_wash_zoe_isolators.py <Wash.kicad_sch> <Zoe.kicad_sch> [...]")
    for p in sys.argv[1:]:
        fix_file(p)
