#!/usr/bin/env python3
"""Flight Engineer PCB Rev S1: remove the 6 V servo BEC, add the 5 V servo BEC.



Steps:
1. Reference renames: FB_6V->FB_SERVO, R_FB6_1/2->R_FBSV_1/2,
   J_6V->J_SERVO_5V (footprints and positions untouched — the user owns
   placement).
2. Net renames (codes preserved, so the pours stay consistent):
   +6V -> 5V_SERVO, BEC6V_VIN_F -> BECSV_VIN_F, BEC6V_SW -> BECSV_SW.
3. U_BEC_6V (TPS54540, SOIC-8) deleted; U_BEC_SERVO_5V added as a clone of
   U_BEC_5V_2's footprint block at U_BEC_6V's old position, pad nets mapped
   BEC2_* -> BECSV_* / 5V_SERVO.
4. Electrical repairs found during conversion (PCB-side bugs):
   a. Feedback dividers had NO midpoint net (R_FBx_1 pad 2 and R_FBx_2
      pad 1 were netless) — new nets BEC1_FB / BEC2_FB / BECSV_FB join
      them.  Their attachment to the regulator FB pin is deferred until
      the TPS54620 package/pinmap is verified (the VQFN-20 footprint's pad
      map is unconfirmed — see FlightEngineer.md).
   b. L_BEC1/2/3 connected the filtered INPUT rail to the SW node, leaving
      the buck output floating; the input-side pad now carries the output
      net (BEC1_PRE_OR / BEC2_PRE_OR / 5V_SERVO) as a buck requires.

Authored by Claude Fable 5 (Anthropic), 2026-07-21.  License: CC BY 4.0.
"""

import re
import sys
import uuid
from pathlib import Path

PCB = Path(__file__).resolve().parents[1] / "kicads" / "FlightEngineer.kicad_pcb"


def u():
    return str(uuid.uuid4())


def find_block(src, header_re):
    """(start, end) of the first footprint block whose text matches header_re."""
    i = 0
    while True:
        j = src.find('\t(footprint "', i)
        if j == -1:
            return None
        d = 0
        for k in range(j, len(src)):
            if src[k] == "(":
                d += 1
            elif src[k] == ")":
                d -= 1
                if d == 0:
                    end = k + 1
                    break
        if re.search(header_re, src[j:end]):
            return j, end
        i = end


def set_pad_net(block, pad, code, name):
    """Set (or insert) the net of one pad inside a footprint block."""
    p = block.find(f'(pad "{pad}"')
    if p == -1:
        print(f"  WARN: pad {pad} not found")
        return block
    d = 0
    for k in range(p, len(block)):
        if block[k] == "(":
            d += 1
        elif block[k] == ")":
            d -= 1
            if d == 0:
                pe = k + 1
                break
    padtxt = block[p:pe]
    if "(net " in padtxt:
        padtxt = re.sub(r'\(net \d+ "[^"]*"\)', f'(net {code} "{name}")', padtxt)
    else:
        lm = re.search(r"\(layers[^)]*\)", padtxt)
        padtxt = (
            padtxt[: lm.end()] + f'\n\t\t\t(net {code} "{name}")' + padtxt[lm.end():]
        )
    return block[:p] + padtxt + block[pe:]


def main():
    src = PCB.read_text()

    # --- 2. net renames (same codes; pours/pads stay consistent) ------------
    for old, new in (("+6V", "5V_SERVO"), ("BEC6V_VIN_F", "BECSV_VIN_F"),
                     ("BEC6V_SW", "BECSV_SW")):
        src = src.replace(f'"{old}"', f'"{new}"')

    # --- 1. reference renames ----------------------------------------------
    for old, new in (
        ('(property "Reference" "FB_6V"', '(property "Reference" "FB_SERVO"'),
        ('(property "Reference" "R_FB6_1"', '(property "Reference" "R_FBSV_1"'),
        ('(property "Reference" "R_FB6_2"', '(property "Reference" "R_FBSV_2"'),
        ('(property "Reference" "J_6V"', '(property "Reference" "J_SERVO_5V"'),
    ):
        if old not in src:
            print(f"  WARN: ref not found: {old}")
        src = src.replace(old, new, 1)

    # --- new net codes ------------------------------------------------------
    codes = {int(n) for n in re.findall(r'^\t\(net (\d+) "', src, re.M)}
    names = dict(re.findall(r'^\t\(net (\d+) "([^"]*)"\)', src, re.M))
    by_name = {v: int(k) for k, v in names.items()}
    nxt = max(codes) + 1
    new_nets = {}
    for n in ("BEC1_FB", "BEC2_FB", "BECSV_FB"):
        new_nets[n] = nxt
        nxt += 1
    last_decl = list(re.finditer(r'^\t\(net \d+ "[^"]*"\)\n', src, re.M))[-1]
    src = (
        src[: last_decl.end()]
        + "".join(f'\t(net {c} "{n}")\n' for n, c in new_nets.items())
        + src[last_decl.end():]
    )

    # --- 3. clone U_BEC_5V_2 -> U_BEC_SERVO_5V at U_BEC_6V's spot -----------
    span6 = find_block(src, r'\(property "Reference" "U_BEC_6V"')
    span2 = find_block(src, r'\(property "Reference" "U_BEC_5V_2"')
    if not span6 or not span2:
        print("  ERROR: U_BEC_6V / U_BEC_5V_2 not found")
        return 1
    old6 = src[span6[0]:span6[1]]
    at6 = re.search(r"\n\t\t\(at ([^)]+)\)", old6).group(1)
    clone = src[span2[0]:span2[1]]
    clone = re.sub(r"\n\t\t\(at [^)]+\)", f"\n\t\t(at {at6})", clone, count=1)
    clone = re.sub(
        r'\(property "Reference" "U_BEC_5V_2"',
        '(property "Reference" "U_BEC_SERVO_5V"', clone, count=1)
    clone = re.sub(
        r'(\(property "Value" ")[^"]*"',
        r'\g<1>TPS54620 sync buck 5.0V servo rail (pkg verify)"', clone, count=1)
    for old, new in (
        ("BEC2_VIN_F", "BECSV_VIN_F"),
        ("BEC2_SW", "BECSV_SW"),
        ("BEC2_PRE_OR", "5V_SERVO"),
    ):
        clone = clone.replace(
            f'(net {by_name[old]} "{old}")', f'(net {by_name[new]} "{new}")'
        )
    clone = re.sub(r'\(uuid "[^"]*"\)', lambda m: f'(uuid "{u()}")', clone)
    # replace the U_BEC_6V block with the clone
    src = src[: span6[0]] + clone + src[span6[1]:]

    # --- 4a. feedback-divider midpoint nets ---------------------------------
    for r1, r2, net in (
        ("R_FB1_1", "R_FB1_2", "BEC1_FB"),
        ("R_FB2_1", "R_FB2_2", "BEC2_FB"),
        ("R_FBSV_1", "R_FBSV_2", "BECSV_FB"),
    ):
        for ref, pad in ((r1, "2"), (r2, "1")):
            span = find_block(src, rf'\(property "Reference" "{ref}"')
            if not span:
                print(f"  WARN: {ref} not found")
                continue
            block = set_pad_net(src[span[0]:span[1]], pad, new_nets[net], net)
            src = src[: span[0]] + block + src[span[1]:]

    # --- 4b. buck inductor output branch ------------------------------------
    for ref, outnet in (
        ("L_BEC1", "BEC1_PRE_OR"),
        ("L_BEC2", "BEC2_PRE_OR"),
        ("L_BEC3", "5V_SERVO"),
    ):
        span = find_block(src, rf'\(property "Reference" "{ref}"')
        if not span:
            print(f"  WARN: {ref} not found")
            continue
        block = set_pad_net(
            src[span[0]:span[1]], "1", by_name[outnet], outnet
        )
        src = src[: span[0]] + block + src[span[1]:]

    PCB.write_text(src)
    print("Flight Engineer PCB Rev S1 conversion applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
