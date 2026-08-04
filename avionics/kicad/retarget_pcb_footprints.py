#!/usr/bin/env python3
"""
PCB-side companion to `retarget_mspm0g351x_slb9672.py` (2026-08-03).

Swaps the physical footprint of the retargeted parts on the two boards that
have them placed, re-anchoring each new footprint on the old one's origin,
rotation and reference designator:

    CAN-PERIPH-GW-1   U1_1, U1_2   QFN-48 EP5.15 (7x7)  ->  Texas RHB0032E VQFN-32 EP3.45 (5x5)
    Observer             U3           QFN-48 EP5.15 (7x7)  ->  VQFN-48 EP4.1 (7x7)
    both boards       TPM          QFN-32 EP3.45        ->  QFN-32 EP3.6 (PG-UQFN-32-1,-2)

Why the Observer footprint changes even though the package does not
----------------------------------------------------------------
Observer stays in the 48-pin RGZ package, but the land it was drawn on is wrong
and always has been.  `QFN-48-1EP_7x7mm_P0.5mm_EP5.15x5.15mm` is, per its own
KiCad `descr` field, an Analog Devices LTC legacy QFN outline.  TI's RGZ0048F
exposed thermal pad is 4.1 mm square (SLASFA6B land pattern 4229427/A), so the
5.15 mm land overhangs the package's thermal pad by 0.525 mm on every side.
The lead pads are identical between the two footprints, so this swap only
shrinks pad 49 - it cannot pull any lead off its trace.

Likewise the TPM: the SLB9672 is a PG-UQFN-32-1,-2 whose recommended land has a
3.6 mm exposed pad (Infineon SLB9672 FW16.xx datasheet Rev 1.3, Figure 3), not
the 3.45 mm of the PG-VQFN-32 land the SLB9670 was drawn on.

What this does NOT do
---------------------
It does not route.  On the gateway the MCU shrinks from 48 pads at 7x7 mm to
32 pads at 5x5 mm, so every existing trace into U1_1/U1_2 is left dangling and
the board will show fresh DRC/ratsnest errors that need a manual routing pass.
That is expected and is tracked in TODO.md 1.2d.
"""

import argparse
import re
import shutil
from pathlib import Path

KICAD = Path(__file__).resolve().parent
FPLIB = Path("/usr/share/kicad/footprints/Package_DFN_QFN.pretty")

JOBS = [
    {
        "board": "CAN-PERIPH-GW-1",
        "pcb": KICAD / "CAN-PERIPH-GW-1/kicads/CAN-PERIPH-GW-1.kicad_pcb",
        "net": KICAD / "CAN-PERIPH-GW-1/kicads/CAN-PERIPH-GW-1.kicad_sch",
        "swaps": [
            {"refs": ["U1_1", "U1_2"],
             "old_fp": "Package_DFN_QFN:QFN-48-1EP_7x7mm_P0.5mm_EP5.15x5.15mm",
             "new_fp": "Package_DFN_QFN:Texas_RHB0032E_VQFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm",
             "mod": "Texas_RHB0032E_VQFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm",
             "value": "TI MSPM0G3518-Q1",
             "mode": "renet"},
            {"refs": ["U2_1", "U2_2", "U2_3", "U2_4"],
             "old_fp": "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm",
             "new_fp": "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.6x3.6mm",
             "mod": "QFN-32-1EP_5x5mm_P0.5mm_EP3.6x3.6mm",
             "value": "Infineon SLB 9672AU2.0"},
        ],
    },
    {
        "board": "Observer",
        "pcb": KICAD / "Observer/kicads/Observer.kicad_pcb",
        "net": KICAD / "Observer/kicads/Observer.kicad_sch",
        "swaps": [
            {"refs": ["U3"],
             "old_fp": "Package_DFN_QFN:QFN-48-1EP_7x7mm_P0.5mm_EP5.15x5.15mm",
             "new_fp": "Package_DFN_QFN:VQFN-48-1EP_7x7mm_P0.5mm_EP4.1x4.1mm",
             "mod": "VQFN-48-1EP_7x7mm_P0.5mm_EP4.1x4.1mm",
             "value": "TI MSPM0G3519-Q1"},
            {"refs": ["U5"],
             "old_fp": "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm",
             "new_fp": "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.6x3.6mm",
             "mod": "QFN-32-1EP_5x5mm_P0.5mm_EP3.6x3.6mm",
             "value": "Infineon SLB 9672AU2.0"},
        ],
    },
]


def sexpr_at(text: str, start: int) -> tuple[int, int]:
    """Return (start, end) of the balanced s-expression opening at `start`."""
    depth = 0
    in_str = False
    i = start
    while i < len(text):
        c = text[i]
        if in_str:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return start, i + 1
        i += 1
    raise ValueError("unbalanced s-expression")


def find_footprint(text: str, ref: str):
    """Locate the `(footprint ...)` block carrying Reference == ref.

    Returns (start, end, block) with `start` on the line's leading tab, so a
    splice replaces the indentation too and cannot double it up.
    """
    for m in re.finditer(r'^(\t*)\(footprint ', text, re.M):
        open_paren = m.start() + len(m.group(1))
        _, e = sexpr_at(text, open_paren)
        blk = text[open_paren:e]
        if re.search(r'\(property "Reference" "%s"' % re.escape(ref), blk):
            return m.start(), e, blk
    return None


def pad_nets(block: str) -> dict[str, tuple[int, str]]:
    """Map pad number -> (net code, net name) from an existing footprint block.

    Each pad is isolated as its own balanced s-expression first.  Scanning
    forward from `(pad "N"` for the next `(net ...)` would silently attribute
    the *following* pad's net to any pad that has none.
    """
    out: dict[str, tuple[int, str]] = {}
    for m in re.finditer(r'\(pad "([^"]+)"', block):
        _, end = sexpr_at(block, m.start())
        pad_blk = block[m.start():end]
        net = re.search(r'\(net (\d+) "([^"]*)"\)', pad_blk)
        if net:
            out.setdefault(m.group(1), (int(net.group(1)), net.group(2)))
    return out


def sch_pad_nets(sch_net_file: Path, ref: str) -> dict[str, str]:
    """Map pad number -> net name for `ref`, from an exported netlist."""
    text = sch_net_file.read_text()
    out = {}
    for blk in re.split(r'\n    \(net ', text.split("(nets", 1)[1]):
        name = re.search(r'\(name "([^"]+)"\)', blk)
        if not name:
            continue
        for r, p in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', blk):
            if r == ref:
                out[p] = name.group(1)
    return out


def net_codes(pcb: str) -> dict[str, int]:
    return {m.group(2): int(m.group(1))
            for m in re.finditer(r'^\t\(net (\d+) "([^"]*)"\)', pcb, re.M)}


def build_block(mod_text: str, new_fp: str, ref: str, value: str,
                at_line: str, uuid: str, layer: str,
                pads: dict[str, str], codes: dict[str, int],
                ref_at: str, val_at: str) -> str:
    """Compose a placed `(footprint ...)` block from a library .kicad_mod."""
    s, e = sexpr_at(mod_text, mod_text.index("(footprint "))
    body = mod_text[s:e]

    # Strip the library header line and re-emit it with placement data.
    body = re.sub(r'^\(footprint "[^"]*"', "", body, count=1).lstrip("\n")
    body = re.sub(r'^\t*\(version [^\n]*\n', "", body, flags=re.M)
    body = re.sub(r'^\t*\(generator[^\n]*\n', "", body, flags=re.M)
    body = re.sub(r'^\t*\(generator_version[^\n]*\n', "", body, flags=re.M)
    body = re.sub(r'^\t*\(layer "[^"]*"\)\n', "", body, count=1, flags=re.M)
    body = body.rstrip()
    assert body.endswith(")")
    body = body[:-1].rstrip()

    # Library footprints carry placeholder REF**/value text; replace with ours.
    # `[^\n]*` swallows the trailing paren of the original `(at ...)`, so the
    # replacement has to put it back.
    body = re.sub(r'\(property "Reference" "[^"]*"\n(\s*)\(at [^\n]*',
                  lambda m: f'(property "Reference" "{ref}"\n{m.group(1)}(at {ref_at})',
                  body, count=1)
    body = re.sub(r'\(property "Value" "[^"]*"\n(\s*)\(at [^\n]*',
                  lambda m: f'(property "Value" "{value}"\n{m.group(1)}(at {val_at})',
                  body, count=1)

    # Attach nets pad by pad, from the schematic netlist.
    def add_net(m):
        pad_no = m.group(1)
        name = pads.get(pad_no)
        if name is None:
            return m.group(0)          # genuinely unconnected pad
        code = codes.get(name)
        if code is None:
            raise SystemExit(f"net '{name}' is not in the PCB net table")
        return m.group(0).rstrip() + f'\n\t\t\t(net {code} "{name}")'

    body = re.sub(r'\(pad "([^"]+)"[^\n]*\n(?:\t*\([^\n]*\n)*?', add_net, body)

    return (f'\t(footprint "{new_fp}"\n'
            f'\t\t(layer "{layer}")\n'
            f'\t\t(uuid "{uuid}")\n'
            f'\t\t(at {at_line})\n'
            f'{body}\n\t)')


def run(job: dict, apply_changes: bool) -> None:
    pcb_path = job["pcb"]
    pcb = pcb_path.read_text()
    original = pcb
    codes = net_codes(pcb)

    # Export a fresh netlist from the retargeted schematic for pad-net truth.
    import subprocess
    tmp = Path("/tmp/claude-1000") / f'{job["board"]}_fp.net'
    subprocess.run(["kicad-cli", "sch", "export", "netlist",
                    "--output", str(tmp), str(job["net"])],
                   capture_output=True, check=False)

    print(f"\n=== {job['board']}")
    for swap in job["swaps"]:
        mod_path = FPLIB / f'{swap["mod"]}.kicad_mod'
        mod_text = mod_path.read_text()
        for ref in swap["refs"]:
            found = find_footprint(pcb, ref)
            if not found:
                print(f"   {ref:<6} not placed on this PCB - skipped")
                continue
            s, e, blk = found
            if f'(footprint "{swap["old_fp"]}"' not in blk:
                print(f"   {ref:<6} unexpected footprint, skipped")
                continue

            def field(pattern: str, what: str) -> str:
                """Pull a required field out of the placed footprint block."""
                m = re.search(pattern, blk)
                if m is None:
                    raise SystemExit(
                        f"{job['board']}: {ref} has no {what}; refusing to "
                        f"rebuild the footprint from an incomplete block")
                return m.group(1)

            at_line = field(r'\n\t\t\(at ([^\n]*)\)', "placement")
            uuid = field(r'\n\t\t\(uuid "([^"]+)"\)', "uuid")
            layer = field(r'\n\t\t\(layer "([^"]+)"\)', "layer")
            ref_at = field(r'\(property "Reference" "[^"]*"\n\s*\(at ([^\n]*)\)',
                           "Reference text position")
            val_at = field(r'\(property "Value" "[^"]*"\n\s*\(at ([^\n]*)\)',
                           "Value text position")

            old_nets = pad_nets(blk)
            sch_nets = sch_pad_nets(tmp, ref)

            if swap.get("mode") == "renet":
                # Pad count changes, so the nets have to come from the
                # retargeted schematic.
                new_nets = dict(sch_nets)
            else:
                # Same pad count: this is a land-pattern correction only, so
                # every pad keeps exactly the net it already had.  Pads the PCB
                # left unconnected stay unconnected - these boards have known
                # sch<->pcb parity gaps, and closing them is a separate job.
                # The single deliberate addition is the exposed pad, which the
                # SLB9670 footprint omitted and Infineon requires to be tied to
                # GND (SLB9672 datasheet Rev 1.3, section 2.1.2).
                new_nets = {p: n for p, (_, n) in old_nets.items() if n}
                if "33" not in new_nets and "33" in sch_nets:
                    new_nets["33"] = sch_nets["33"]

            missing = sorted({n for n in new_nets.values() if n not in codes})
            if missing:
                # A net the schematic knows about but the PCB does not is a
                # pre-existing sch<->pcb parity gap.  Leave the pad unconnected
                # rather than inventing a net entry, and say so.
                print(f"   {ref:<6} NOTE: {len(missing)} net(s) absent from the "
                      f"PCB net table, pad left unconnected: {', '.join(missing)}")
                new_nets = {p: n for p, n in new_nets.items() if n in codes}

            new_blk = build_block(mod_text, swap["new_fp"], ref, swap["value"],
                                  at_line, uuid, layer, new_nets, codes,
                                  ref_at, val_at)
            pcb = pcb[:s] + new_blk + pcb[e:]
            print(f"   {ref:<6} {swap['old_fp'].split(':')[1]}")
            print(f"          -> {swap['new_fp'].split(':')[1]}")
            print(f"          anchored at ({at_line}), "
                  f"{len(old_nets)} old pad nets -> {len(new_nets)} new pad nets")

    if not apply_changes:
        print("   (dry run, nothing written)")
        return
    if pcb == original:
        print("   no change")
        return
    backup = pcb_path.with_suffix(pcb_path.suffix + ".pre-g351x")
    if not backup.exists():
        shutil.copy2(pcb_path, backup)
    pcb_path.write_text(pcb)
    print(f"   written; backup at {backup.name}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    for job in JOBS:
        run(job, args.apply)


if __name__ == "__main__":
    main()
