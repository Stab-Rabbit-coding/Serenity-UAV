#!/usr/bin/env python3
"""Pilot PCB repair pass: strip stale routing, reconcile with Wash_rebuild.

Context (2026-07-21): the user re-placed Pilot's components to clear
overlaps; the old routed tracks were left behind and now short across the
moved footprints (DRC: 127 shorting_items / 77 clearance).  The
schematic-first rebuild (Wash_rebuild.kicad_sch, AUTHORITATIVE per the
user) currently covers the 8 core ICs (CAN-TR, ETH1-PHY, ETH2-PHY, GPS,
RS485, T-ETH, T-ETH2, TPM).

This script:
1. Deletes every (segment)/(via) — all routing predates the re-placement
   and is copper garbage against the new positions.  Zones are kept (they
   re-fill to the new geometry).
2. Renames T-ETH1 -> T-ETH to follow the rebuild's naming.
3. Gives the four no-reference mounting holes refs MH1..MH4 and the
   board_only attribute so parity checks skip them.
4. Injects pad nets for the rebuild-covered refs from the exported
   Wash_rebuild netlist ((ref, pin) -> net), adding any new net names to
   the board net table.  Pads the rebuild does not cover keep their
   existing nets (full-board injection waits until the rebuild schematic
   covers the whole board).

Authored by Claude Fable 5 (Anthropic), 2026-07-21.  License: CC BY 4.0.
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "kicads" / "Pilot.kicad_pcb"
NET = Path(
    "/tmp/claude-1000/-home-steve-Documents-Vocation-Employers-Griffing-tech-designs"
    "-Serenity-UAV/944eee09-8cfd-4808-b8ad-cae9a0568deb/scratchpad/wash_rebuild.net"
)


def parse_padnet():
    src = NET.read_text()
    padnet = {}
    for m in re.finditer(
        r'\(net \(code "[^"]*"\) \(name "([^"]*)"\)(.*?)(?=\(net \(code|\Z)', src, re.S
    ):
        name = m.group(1)
        for r, p in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"', m.group(2)):
            padnet[(r, p)] = name
    return padnet


def strip_blocks(src, opener):
    """Remove every top-level block starting with `opener` (tab-indented)."""
    out, i, n = [], 0, 0
    while True:
        j = src.find(opener, i)
        if j == -1:
            out.append(src[i:])
            break
        out.append(src[i:j])
        d = 0
        for k in range(j, len(src)):
            if src[k] == "(":
                d += 1
            elif src[k] == ")":
                d -= 1
                if d == 0:
                    end = k + 1
                    break
        if end < len(src) and src[end] == "\n":
            end += 1
        i = end
        n += 1
    return "".join(out), n


def main():
    src = PCB.read_text()
    padnet = parse_padnet()

    src, nseg = strip_blocks(src, "\t(segment")
    src, nvia = strip_blocks(src, "\t(via")
    print(f"stripped {nseg} segments, {nvia} vias")

    src = src.replace('(property "Reference" "T-ETH1"',
                      '(property "Reference" "T-ETH"', 1)

    # net table: existing names + any new ones from the rebuild netlist
    names = dict(re.findall(r'^\t\(net (\d+) "([^"]*)"\)', src, re.M))
    by_name = {v: int(k) for k, v in names.items()}
    nxt = max(int(k) for k in names) + 1
    for n in sorted({v for v in padnet.values() if v}):
        if n not in by_name:
            by_name[n] = nxt
            nxt += 1
    last_decl = list(re.finditer(r'^\t\(net \d+ "[^"]*"\)\n', src, re.M))[-1]
    add_decls = "".join(
        f'\t(net {c} "{n}")\n'
        for n, c in sorted(by_name.items(), key=lambda kv: kv[1])
        if str(c) not in names
    )
    src = src[: last_decl.end()] + add_decls + src[last_decl.end():]

    # walk footprints: MH refs, board_only, pad-net injection
    covered = {r for (r, _p) in padnet}
    out, i, mh, hits, miss = [], 0, 0, 0, 0
    while True:
        j = src.find('\t(footprint "', i)
        if j == -1:
            out.append(src[i:])
            break
        out.append(src[i:j])
        d = 0
        for k in range(j, len(src)):
            if src[k] == "(":
                d += 1
            elif src[k] == ")":
                d -= 1
                if d == 0:
                    end = k + 1
                    break
        block = src[j:end]
        rm = re.search(r'\(property "Reference" "([^"]+)"', block)
        ref = rm.group(1) if rm else None
        if ref is None and "MountingHole" in block[:80]:
            mh += 1
            ref = f"MH{mh}"
            at = re.search(r"\n\t\t\(at [^)]+\)", block)
            prop = (
                f'\n\t\t(property "Reference" "{ref}"\n'
                f"\t\t\t(at 0 -3 0)\n\t\t\t(layer \"F.Fab\")\n"
                f'\t\t\t(uuid "pilot-mh-ref-{mh}")\n'
                f"\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1 1)\n"
                f"\t\t\t\t\t(thickness 0.15)\n\t\t\t\t)\n\t\t\t)\n\t\t)"
            )
            block = block[: at.end()] + prop + block[at.end():]
            if "(attr " in block:
                block = re.sub(r"\(attr ([^)]+)\)", r"(attr \1 board_only)", block, count=1)
            else:
                block = block[: at.end()] + "\n\t\t(attr board_only exclude_from_bom)" + block[at.end():]
        if ref in covered:
            def rewrite_pad(padtxt):
                nonlocal hits, miss
                num = re.match(r'\(pad "([^"]*)"', padtxt).group(1)
                net = padnet.get((ref, num))
                if net is None:
                    miss += 1
                    padtxt = re.sub(r'\s*\(net \d+ "[^"]*"\)', "", padtxt)
                    return padtxt
                hits += 1
                padtxt = re.sub(r'\s*\(net \d+ "[^"]*"\)', "", padtxt)
                netexpr = f'\n\t\t\t(net {by_name[net]} "{net}")'
                lm = re.search(r"\(layers[^)]*\)", padtxt)
                return padtxt[: lm.end()] + netexpr + padtxt[lm.end():]

            nb, p = [], 0
            while True:
                pj = block.find("(pad ", p)
                if pj == -1:
                    nb.append(block[p:])
                    break
                nb.append(block[p:pj])
                dd = 0
                for k in range(pj, len(block)):
                    if block[k] == "(":
                        dd += 1
                    elif block[k] == ")":
                        dd -= 1
                        if dd == 0:
                            pe = k + 1
                            break
                nb.append(rewrite_pad(block[pj:pe]))
                p = pe
            block = "".join(nb)
        out.append(block)
        i = end
    src = "".join(out)

    PCB.write_text(src)
    print(f"MH refs added: {mh}; pad nets injected: {hits}; netless pads on covered refs: {miss}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
