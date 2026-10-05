#!/usr/bin/env python3
"""Add one part to a board's schematic AND PCB, nets bound by pin number.

Used for datasheet-driven circuit fixes that need a new component (first
use: the TLV62569 feedback divider on Flight Engineer U_REG_3V3_H,
avionics/WBS.md U7.1e).  The symbol comes from the stock KiCad library
(``Device:R`` ...) or from ``SecureControllers``; each pin gets a global
label carrying its net; the footprint is placed at the given board
coordinate with pad nets assigned.  Refuses to reuse an existing
reference designator.

Attribution: authored by Claude Opus 5.5 (Anthropic), 2026-09-26.

Usage::

    python3 tools/kicad_add_part.py SCH PCB REF LIB:SYMBOL VALUE FOOTPRINT \\
        --sch-at X,Y[,ROT] --pcb-at X,Y[,ROT] --net 1=NET --net 2=NET
"""

import argparse
import pathlib
import re
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
# pylint: disable=wrong-import-position
from kicad_relink import (LIB_DIR, NICK, block_end, fp_file, new_label,  # noqa
                          pin_geom, prop, sym_pins, top_blocks)

STOCK_SYM = pathlib.Path("/usr/share/kicad/symbols")


def load_symbol(lib_id):
    """Return the library block for ``Lib:Name`` (stock or shared)."""
    lib, name = lib_id.split(":", 1)
    path = LIB_DIR / (NICK + ".kicad_sym") if lib == NICK \
        else STOCK_SYM / (lib + ".kicad_sym")
    t = path.read_text(encoding="utf-8")
    for s, e in top_blocks(t, "symbol"):
        if t[s:e].startswith('(symbol "%s"' % name):
            if "(extends" in t[s:e]:
                raise SystemExit("%s uses extends -- not supported" % lib_id)
            return t[s:e]
    raise SystemExit("%s not found" % lib_id)


def add_sch(sch, ref, lib_id, value, fp, at, nets):
    """Place the symbol and one global label per connected pin."""
    t = sch.read_text(encoding="utf-8")
    for s, e in top_blocks(t, "symbol"):
        if prop(t[s:e], "Reference") == ref:
            raise SystemExit("%s already exists in %s" % (ref, sch.name))
    blk = load_symbol(lib_id)
    name = lib_id.split(":", 1)[1]
    ls = t.index("(lib_symbols")
    le = block_end(t, ls)
    if '(symbol "%s"' % lib_id not in t[ls:le]:
        cached = blk.replace('(symbol "%s"' % name, '(symbol "%s"' % lib_id, 1)
        t = t[:le - 1] + "  " + cached + "\n  " + t[le - 1:]
    proj = re.search(r'\(instances \(project "([^"]+)" \(path "([^"]+)"', t)
    x, y, rot = at
    inst = {"x": x, "y": y, "rot": rot, "mirror": None}
    sym = ('(symbol (lib_id "%s") (at %.2f %.2f %g) (unit 1)\n'
           '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)'
           ' (uuid "%s")\n'
           '    (property "Reference" "%s" (at %.2f %.2f 0) (effects (font'
           ' (size 1.27 1.27))))\n'
           '    (property "Value" "%s" (at %.2f %.2f 0) (effects (font'
           ' (size 1.27 1.27))))\n'
           '    (property "Footprint" "%s" (at %.2f %.2f 0) (effects (font'
           ' (size 1.27 1.27)) (hide yes)))\n'
           '    (property "Datasheet" "" (at %.2f %.2f 0) (effects (font'
           ' (size 1.27 1.27)) (hide yes)))\n'
           % (lib_id, x, y, rot, uuid.uuid4(), ref, x + 2.54, y - 1.27,
              value, x + 2.54, y + 1.27, fp, x, y, x, y))
    pins = sym_pins(blk)
    for num in pins:
        sym += '    (pin "%s" (uuid "%s"))\n' % (num, uuid.uuid4())
    if proj:
        sym += ('    (instances (project "%s" (path "%s" (reference "%s")'
                ' (unit 1)))))' % (proj.group(1), proj.group(2), ref))
    else:
        sym += "  )"
    items = [sym]
    for num, net in nets.items():
        pt, ang = pin_geom(inst, pins[num], 1)
        items.append(new_label(net, pt, ang))
    i = t.rindex("(sheet_instances") if "(sheet_instances" in t \
        else t.rstrip().rindex(")")
    t = t[:i] + "\n  ".join(items) + "\n  " + t[i:]
    sch.write_text(t, encoding="utf-8")


def add_pcb(pcb, ref, value, fp, at, nets):
    """Place the footprint with pad nets."""
    t = pcb.read_text(encoding="utf-8")
    for s, e in top_blocks(t, "footprint"):
        if prop(t[s:e], "Reference") == ref:
            raise SystemExit("%s already exists in %s" % (ref, pcb.name))
    lib = fp_file(fp).read_text(encoding="utf-8")
    table = dict((n, int(i)) for i, n in
                 re.findall(r'^\t\(net (\d+) "((?:[^"\\]|\\.)*)"\)', t, re.M))
    for net in nets.values():
        if net not in table:
            table[net] = max(table.values()) + 1
            last = list(re.finditer(r'^\t\(net \d+ "[^"]*"\)', t, re.M))[-1]
            t = t[:last.end()] + '\n\t(net %d "%s")' % (table[net], net) \
                + t[last.end():]
    x, y, rot = at
    body = []
    for s, e in top_blocks(lib, "pad"):
        pad = lib[s:e]
        num = re.match(r'\(pad "([^"]*)"', pad).group(1)
        pad = re.sub(r"\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)",
                     lambda m: "(at %s %s %g)" % (m.group(1), m.group(2),
                                                  (float(m.group(3) or 0)
                                                   + rot) % 360), pad, count=1)
        if num in nets:
            pad = pad[:-1].rstrip() + '\n\t\t\t(net %d "%s")\n\t\t)' % (
                table[nets[num]], nets[num])
        body.append(pad)
    for head in ("fp_line", "fp_rect", "fp_poly", "fp_circle", "fp_arc",
                 "model", "attr"):
        body += [lib[s:e] for s, e in top_blocks(lib, head)]
    new = ('\n\t(footprint "%s"\n\t\t(layer "F.Cu")\n\t\t(uuid "%s")\n'
           '\t\t(at %.4f %.4f %g)\n'
           '\t\t(property "Reference" "%s" (at 0 -1.2 %g) (layer "F.Fab")'
           ' (uuid "%s") (effects (font (size 1 1) (thickness 0.15))))\n'
           '\t\t(property "Value" "%s" (at 0 1.2 %g) (layer "F.Fab")'
           ' (uuid "%s") (effects (font (size 1 1) (thickness 0.15))))\n'
           '\t\t%s\n\t)'
           % (fp, uuid.uuid4(), x, y, rot, ref, rot, uuid.uuid4(), value,
              rot, uuid.uuid4(), "\n\t\t".join(body)))
    i = t.rstrip().rindex(")")
    t = t[:i].rstrip() + new + "\n)\n"
    pcb.write_text(t, encoding="utf-8")


def xy(text):
    """Parse ``X,Y[,ROT]``."""
    v = [float(a) for a in text.split(",")]
    return v[0], v[1], v[2] if len(v) > 2 else 0.0


def main():
    """CLI entry point."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    for a in ("sch", "pcb", "ref", "symbol", "value", "footprint"):
        ap.add_argument(a)
    ap.add_argument("--sch-at", required=True, type=xy)
    ap.add_argument("--pcb-at", required=True, type=xy)
    ap.add_argument("--net", action="append", default=[])
    args = ap.parse_args()
    nets = dict(n.split("=", 1) for n in args.net)
    add_sch(pathlib.Path(args.sch), args.ref, args.symbol, args.value,
            args.footprint, args.sch_at, nets)
    add_pcb(pathlib.Path(args.pcb), args.ref, args.value, args.footprint,
            args.pcb_at, nets)
    print("added %s (%s, %s) nets %s" % (args.ref, args.value, args.footprint,
                                         nets))
    return 0


if __name__ == "__main__":
    sys.exit(main())
