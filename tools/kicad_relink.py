#!/usr/bin/env python3
"""Relink a placed part to a SecureControllers library symbol + footprint.

Purpose
-------
Moves one reference designator on a Serenity-UAV board from its local /
board-scoped symbol and footprint onto the shared, datasheet-verified
``SecureControllers`` library (avionics/WBS.md U7.1/U7.3), matching pins
**by name** so that a wrong pin *number* in the old symbol is corrected
rather than propagated.  First used for the TLV62569 -> TLV62569PDRL
(SOT-563) and TLV75725PDBV -> TLV75725PDRV (WSON-6) package swaps
(owner-approved 2026-09-26).

Schematic side
    * The instance's old pin positions are computed from its cached lib
      symbol and **verified** against the labels / wires / no-connects
      actually attached (aborts if the geometry does not line up).
    * Each attachment is re-seated on the new pin carrying the same pin
      name: global/local labels and power symbols move, a stub wire whose
      far end only carries a label is removed and the label moved onto the
      pin, any other wire has its pin-end moved, no-connects move.
    * ``--set PIN=NET`` attaches a global label to a pin (new nets / fixes),
      ``--nc PIN`` places a no-connect flag.
    * The new symbol is embedded in ``lib_symbols`` as
      ``SecureControllers:<name>``; the instance lib_id, Value, Footprint
      and Datasheet are updated; reference, UUID and instances are kept.

PCB side
    * The footprint is rebuilt from the library ``.kicad_mod`` at the same
      position / rotation / side; Reference and Value keep their board
      placement; pads get nets from the schematic mapping.
    * Track segments ending on the old pads are removed (they no longer
      land on copper) -- the connections reappear as ratsnest.

All edits are text-level S-expression edits (see PCBNEW_SWIG_BUG.md and
the kiutils-missing note); run kicad-cli ERC/DRC afterwards.

Transform convention (KiCad schematic): sheet = at + Rot(angle)(x, -y),
mirror applied to the library coordinates first.  The rotation sign is
selected per instance by matching the attached items, so a convention
mismatch cannot silently mis-seat a label.

Attribution: authored by Claude Opus 5.5 (Anthropic), 2026-09-26.
File formats: KiCad Developer Documentation, S-expression schematic,
board and footprint formats [REF-KICAD-FMT].

Usage::

    python3 tools/kicad_relink.py SCH PCB REF SYMBOL [--set 5=+5V] [--nc 6]
"""

import argparse
import math
import os
import pathlib
import re
import sys
import uuid

HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_LIB = HERE.parent.parent / "SecureControllers" / "kicad" / "libraries"
LIB_DIR = pathlib.Path(os.environ.get("SECURE_CONTROLLERS_LIB", DEFAULT_LIB))
STOCK_FP = pathlib.Path("/usr/share/kicad/footprints")
NICK = "SecureControllers"
EPS = 0.02  # mm; coordinate match tolerance


# --------------------------------------------------------------------------
# S-expression helpers
# --------------------------------------------------------------------------
def block_end(text, start):
    """Index one past the ``)`` closing the ``(`` at *start*."""
    depth, i, in_str = 0, start, False
    while True:
        ch = text[i]
        if in_str:
            if ch == "\\":
                i += 2
                continue
            if ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1


def children(text, start, end):
    """Yield (s, e) spans of direct child blocks of the block at start."""
    i = text.index("(", start + 1)
    while i < end - 1:
        if text[i] == "(":
            e = block_end(text, i)
            yield i, e
            i = e
        else:
            i += 1


def top_blocks(text, head):
    """Yield (s, e) of top-level ``(head ...)`` blocks (depth 1)."""
    root = text.index("(")
    for s, e in children(text, root, block_end(text, root)):
        if re.match(r"\(%s[\s)]" % re.escape(head), text[s:s + len(head) + 2]):
            yield s, e


def near(a, b):
    """True if two points coincide within EPS."""
    return abs(a[0] - b[0]) < EPS and abs(a[1] - b[1]) < EPS


# --------------------------------------------------------------------------
# Library access
# --------------------------------------------------------------------------
def lib_symbol(name):
    """Return the S-expression block of *name* from the shared library."""
    t = (LIB_DIR / "SecureControllers.kicad_sym").read_text(encoding="utf-8")
    for s, e in top_blocks(t, "symbol"):
        if t[s:e].startswith('(symbol "%s"' % name):
            return t[s:e]
    raise SystemExit("symbol %s not in %s" % (name, LIB_DIR))


def sym_pins(block):
    """Return {number: (name, x, y, angle, length)} for a symbol block."""
    pins = {}
    for m in re.finditer(r"\(pin \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)"
                         r"\s*\(length ([\d.]+)\).*?\(name \"((?:[^\"\\]|\\.)*)\""
                         r".*?\(number \"([^\"]*)\"", block, re.S):
        x, y, a, ln, name, num = m.groups()
        pins[num] = (name, float(x), float(y), float(a), float(ln))
    return pins


def prop(block, key):
    """Value of ``(property "key" "...")`` inside *block*, or None."""
    m = re.search(r'\(property "%s"\s+"((?:[^"\\]|\\.)*)"' % re.escape(key),
                  block)
    return m.group(1) if m else None


# --------------------------------------------------------------------------
# Geometry
# --------------------------------------------------------------------------
def to_sheet(inst, px, py, sign):
    """Library point -> sheet point for an instance (sign picks rotation)."""
    x, y = px, -py
    if inst["mirror"] == "x":
        y = -y
    elif inst["mirror"] == "y":
        x = -x
    r = math.radians(inst["rot"]) * sign
    c, s = round(math.cos(r), 9), round(math.sin(r), 9)
    return (round(inst["x"] + c * x - s * y, 4),
            round(inst["y"] + s * x + c * y, 4))


def pin_geom(inst, pin, sign):
    """(connection point, outward label angle) of a pin on the sheet."""
    _, x, y, a, ln = pin
    tip = to_sheet(inst, x, y, sign)
    r = math.radians(a)
    body = to_sheet(inst, x + ln * math.cos(r), y + ln * math.sin(r), sign)
    dx, dy = tip[0] - body[0], tip[1] - body[1]
    if abs(dx) >= abs(dy):
        ang = 0 if dx > 0 else 180
    else:
        ang = 270 if dy > 0 else 90
    return tip, ang


# --------------------------------------------------------------------------
# Schematic
# --------------------------------------------------------------------------
def find_instance(t, ref):
    """Return (s, e, dict) for the placed symbol with Reference *ref*."""
    for s, e in top_blocks(t, "symbol"):
        blk = t[s:e]
        if prop(blk, "Reference") == ref:
            m = re.search(r"\(lib_id \"([^\"]+)\"\)\s*\(at ([-\d.]+) ([-\d.]+)"
                          r"(?: ([-\d.]+))?\)", blk)
            mir = re.search(r"\(mirror (\w)\)", blk)
            return s, e, {"lib_id": m.group(1), "x": float(m.group(2)),
                          "y": float(m.group(3)),
                          "rot": float(m.group(4) or 0),
                          "mirror": mir.group(1) if mir else None}
    raise SystemExit("reference %s not found" % ref)


def cached_symbol(t, lib_id):
    """Return (s, e) of the lib_symbols cache entry for *lib_id*."""
    ls = t.index("(lib_symbols")
    for s, e in children(t, ls, block_end(t, ls)):
        if t[s:e].startswith('(symbol "%s"' % lib_id):
            return s, e
    raise SystemExit("cache entry %s missing" % lib_id)


def attachments(t, point):
    """Items touching *point*: list of (kind, s, e, extra)."""
    hits = []
    for kind in ("global_label", "label", "no_connect", "wire", "symbol"):
        for s, e in top_blocks(t, kind):
            blk = t[s:e]
            if kind == "wire":
                pts = [(float(a), float(b)) for a, b in
                       re.findall(r"\(xy ([-\d.]+) ([-\d.]+)\)", blk)]
                for idx, p in enumerate(pts[:2]):
                    if near(p, point):
                        hits.append((kind, s, e, (idx, pts)))
                continue
            m = re.search(r"\(at ([-\d.]+) ([-\d.]+)", blk)
            if not m or not near((float(m.group(1)), float(m.group(2))), point):
                continue
            if kind == "symbol" and '(lib_id "power:' not in blk:
                raise SystemExit("pin-to-pin contact at %s -- unsupported"
                                 % (point,))
            hits.append((kind, s, e, None))
    return hits


def label_at(t, point):
    """(s, e) of a label exactly at *point*, else None."""
    for kind in ("global_label", "label"):
        for s, e in top_blocks(t, kind):
            m = re.search(r"\(at ([-\d.]+) ([-\d.]+)", t[s:e])
            if near((float(m.group(1)), float(m.group(2))), point):
                return s, e
    return None


def move_item(blk, new, ang=None):
    """Rewrite the first (at x y [a]) of a label/no-connect/power block."""
    def sub(m):
        a = m.group(3)
        if ang is not None and a is not None:
            a = "%g" % ang
        return "(at %.4f %.4f%s)" % (new[0], new[1], (" " + a) if a else "")
    blk = re.sub(r"\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)", sub, blk,
                 count=1)
    # Label text justification follows the direction; let KiCad derive it.
    return re.sub(r"\s*\(justify (?:left|right)\)", "", blk, count=1) \
        if ang is not None else blk


def new_label(net, point, ang):
    """A fresh global label block."""
    return ('(global_label "%s" (shape bidirectional) (at %.4f %.4f %d)\n'
            '    (effects (font (size 1.27 1.27)))\n    (uuid "%s"))'
            % (net, point[0], point[1], ang, uuid.uuid4()))


def relink_sch(sch_path, ref, sym_name, sets, ncs, rewire=False):
    """Relink the schematic instance; return {new_pin_number: net_hint}."""
    t = sch_path.read_text(encoding="utf-8")
    s, e, inst = find_instance(t, ref)
    cs, ce = cached_symbol(t, inst["lib_id"])
    old = sym_pins(t[cs:ce])
    new_blk = lib_symbol(sym_name)
    new = sym_pins(new_blk)

    # Pick the rotation sign that makes the most old pins touch something.
    score, sign = max(
        (sum(bool(attachments(t, pin_geom(inst, p, sg)[0]))
             for p in old.values()), sg) for sg in (1, -1))
    if score == 0:
        raise SystemExit("%s: no attachments found at computed pin positions"
                         % ref)

    by_name = {}
    for num, p in new.items():
        by_name.setdefault(p[0], []).append(num)
    edits = []   # (s, e, replacement) on the ORIGINAL text
    adds = []
    for num, p in old.items():
        point, _ = pin_geom(inst, p, sign)
        items = attachments(t, point)
        if not items:
            continue
        targets = by_name.get(p[0])
        if rewire:
            # --rewire: the old pin map is untrusted; every connection is
            # restated with --set, so all old attachments are dropped.
            tnum, drop = None, True
            npoint = nang = None
        else:
            if not targets:
                raise SystemExit("%s pin %s (%s) has no same-named pin in %s"
                                 % (ref, num, p[0], sym_name))
            tnum = targets.pop(0)
            npoint, nang = pin_geom(inst, new[tnum], sign)
            # A pin whose net is REPLACED via --set loses its old
            # attachments instead of carrying them over (never both, which
            # would short the old and new nets together).
            drop = tnum in sets
        for kind, a, b, extra in items:
            blk = t[a:b]
            if kind == "wire":
                idx, pts = extra
                far = pts[1 - idx]
                lab = label_at(t, far)
                if lab and len(attachments(t, far)) == 2:
                    edits.append((a, b, ""))
                    edits.append((lab[0], lab[1], "" if drop else
                                  move_item(t[lab[0]:lab[1]], npoint, nang)))
                elif drop:
                    raise SystemExit("%s pin %s: cannot replace net on a "
                                     "non-stub wire" % (ref, num))
                else:
                    old_xy = "(xy %s %s)" % tuple(
                        re.findall(r"\(xy ([-\d.]+ [-\d.]+)\)", blk)[idx]
                        .split())
                    edits.append((a, b, blk.replace(
                        old_xy, "(xy %.4f %.4f)" % npoint, 1)))
            elif drop:
                edits.append((a, b, ""))
            else:
                edits.append((a, b, move_item(
                    blk, npoint, nang if kind != "no_connect" else None)))
    for pin, net in sets.items():
        pt, ang = pin_geom(inst, new[pin], sign)
        adds.append(new_label(net, pt, ang))
    for pin in ncs:
        pt, _ = pin_geom(inst, new[pin], sign)
        adds.append('(no_connect (at %.4f %.4f) (uuid "%s"))'
                    % (pt[0], pt[1], uuid.uuid4()))

    # Instance header: lib_id + properties.
    iblk = t[s:e]
    iblk = iblk.replace('(lib_id "%s")' % inst["lib_id"],
                        '(lib_id "%s:%s")' % (NICK, sym_name), 1)
    for key in ("Value", "Footprint", "Datasheet"):
        val = prop(new_blk, key) if key != "Value" else (
            prop(new_blk, "MPN") or sym_name)
        if prop(iblk, key) is None:
            # Some generated instances omit the property entirely; add it
            # hidden at the symbol origin so parity sees the footprint.
            i = iblk.index("(property")
            iblk = (iblk[:i] + '(property "%s" "%s" (at %.2f %.2f 0) '
                    '(effects (font (size 1.27 1.27)) (hide yes)))\n    '
                    % (key, val, inst["x"], inst["y"]) + iblk[i:])
            continue
        iblk = re.sub(r'(\(property "%s"\s+)"(?:[^"\\]|\\.)*"' % key,
                      lambda m, v=val: m.group(1) + '"%s"' % v, iblk, count=1)
    edits.append((s, e, iblk))

    # Apply edits back-to-front on the original offsets (dedupe spans).
    seen = set()
    for a, b, rep in sorted(edits, key=lambda x: -x[0]):
        if (a, b) in seen:
            continue
        seen.add((a, b))
        t = t[:a] + rep + t[b:]

    # Cache: add the shared symbol, drop the old entry if now unused.
    cached = new_blk.replace('(symbol "%s"' % sym_name,
                             '(symbol "%s:%s"' % (NICK, sym_name), 1)
    ls = t.index("(lib_symbols")
    le = block_end(t, ls)
    if '(symbol "%s:%s"' % (NICK, sym_name) not in t[ls:le]:
        t = t[:le - 1] + "  " + cached + "\n  " + t[le - 1:]
    if '(lib_id "%s")' % inst["lib_id"] not in t:
        cs, ce = cached_symbol(t, inst["lib_id"])
        t = t[:cs] + t[ce:]
    if adds:
        i = t.rindex("(sheet_instances") if "(sheet_instances" in t \
            else t.rstrip().rindex(")")
        t = t[:i] + "\n  ".join(adds) + "\n  " + t[i:]
    return (t, prop(new_blk, "Footprint"), prop(new_blk, "MPN") or sym_name,
            {n: p[0] for n, p in new.items()})


# --------------------------------------------------------------------------
# PCB
# --------------------------------------------------------------------------
def fp_file(fp_id):
    """Path of the library .kicad_mod for ``Lib:Name``."""
    lib, name = fp_id.split(":", 1)
    base = LIB_DIR / (NICK + ".pretty") if lib == NICK \
        else STOCK_FP / (lib + ".pretty")
    return base / (name + ".kicad_mod")


def relink_pcb(pcb_path, ref, fp_id, pin_names, name_to_net, value):
    """Rebuild footprint *ref* as *fp_id*; nets by pin name; set Value."""
    t = pcb_path.read_text(encoding="utf-8")
    for s, e in top_blocks(t, "footprint"):
        if prop(t[s:e], "Reference") == ref:
            break
    else:
        raise SystemExit("footprint %s not on board" % ref)
    old = t[s:e]
    m = re.search(r"\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)", old)
    fx, fy, rot = float(m.group(1)), float(m.group(2)), float(m.group(3) or 0)
    layer = re.search(r'\(layer "([^"]+)"\)', old).group(1)
    back = layer == "B.Cu"

    # Old pad absolute positions (for track clean-up).
    old_abs = []
    r = math.radians(rot)
    for pm in re.finditer(r'\(pad "[^"]*" \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+)',
                          old):
        px, py = float(pm.group(1)), float(pm.group(2))
        old_abs.append((fx + px * math.cos(r) + py * math.sin(r),
                        fy - px * math.sin(r) + py * math.cos(r)))

    lib = fp_file(fp_id).read_text(encoding="utf-8")
    nets = dict((n, int(i)) for i, n in
                re.findall(r'^\t\(net (\d+) "((?:[^"\\]|\\.)*)"\)', t, re.M))
    body = []
    ls, le = 0, block_end(lib, 0)
    for cs_, ce_ in children(lib, ls, le):
        blk = lib[cs_:ce_]
        head = re.match(r"\((\w+)", blk).group(1)
        if head in ("version", "generator", "generator_version", "layer",
                    "uuid", "at"):
            continue
        if head == "property" and re.match(r'\(property "(Reference|Value)"',
                                           blk):
            continue
        if head == "pad":
            num = re.match(r'\(pad "([^"]*)"', blk).group(1)
            net = name_to_net.get(pin_names.get(num))
            blk = re.sub(r"\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)",
                         lambda mm: "(at %s %s %g)" % (
                             mm.group(1), mm.group(2),
                             (float(mm.group(3) or 0) + rot) % 360),
                         blk, count=1)
            if net:
                if net not in nets:
                    nets[net] = max(nets.values()) + 1
                    i = t.index("\n", [mm.end() for mm in re.finditer(
                        r'^\t\(net \d+ "[^"]*"\)', t, re.M)][-1])
                    t = t[:i] + '\n\t(net %d "%s")' % (nets[net], net) + t[i:]
                    s, e = [(a, b) for a, b in top_blocks(t, "footprint")
                            if prop(t[a:b], "Reference") == ref][0]
                blk = blk[:-1].rstrip() + '\n\t\t\t(net %d "%s")\n\t\t)' % (
                    nets[net], net)
        elif head in ("fp_text",) and "(at " in blk:
            blk = re.sub(r"\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)",
                         lambda mm: "(at %s %s %g)" % (
                             mm.group(1), mm.group(2),
                             (float(mm.group(3) or 0) + rot) % 360),
                         blk, count=1)
        if back:
            blk = flip_block(blk, rot)
        body.append(blk)

    keep = [old[a:b] for a, b in children(old, 0, len(old))
            if re.match(r'\((uuid|at|path|sheetname|sheetfile)\b', old[a:b])
            or re.match(r'\(property "(Reference|Value)"', old[a:b])]
    new = ('(footprint "%s"\n\t\t(layer "%s")\n\t\t' % (fp_id, layer)
           + "\n\t\t".join(keep + body) + "\n\t)")
    new = re.sub(r'(\(property "Value"\s+)"(?:[^"\\]|\\.)*"',
                 lambda mm: mm.group(1) + '"%s"' % value, new, count=1)
    t = t[:s] + new + t[e:]

    # Remove segments that ended on the old pads.
    removed = 0
    for a, b in reversed(list(top_blocks(t, "segment"))):
        seg = t[a:b]
        pts = [(float(x), float(y)) for x, y in
               re.findall(r"\((?:start|end) ([-\d.]+) ([-\d.]+)\)", seg)]
        if any(math.hypot(p[0] - q[0], p[1] - q[1]) < 0.3
               for p in pts for q in old_abs):
            t = t[:a] + t[b:]
            removed += 1
    return t, removed


def flip_block(blk, rot):
    """Mirror one footprint child block onto the back side.

    KiCad stores back-side footprint children in the footprint frame with
    local y negated (x unchanged), F.* layers swapped to B.*, and pad
    angles mirrored.  Convention confirmed 2026-09-26 against Pilot
    ETH1-PHY / CAN-TR (B.Cu, -90 deg): library pad y -0.9 -> stored +0.9.
    """
    def neg(m):
        return "(%s %s %s%s)" % (m.group(1), m.group(2),
                                 fmt(-float(m.group(3))), m.group(4) or "")
    head = re.match(r"\((\w+)", blk).group(1)
    if head == "pad":
        blk = re.sub(r"\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)",
                     lambda m: "(at %s %s %g)" % (
                         m.group(1), fmt(-float(m.group(2))),
                         (2 * rot - float(m.group(3))) % 360), blk, count=1)
    blk = re.sub(r"\((start|end|center|mid|xy|at) ([-\d.]+) ([-\d.]+)"
                 r"((?: [-\d.]+)?)\)",
                 neg, blk) if head != "pad" else blk
    blk = re.sub(r'"F\.(\w+)"', r'"B.\1"', blk)
    blk = blk.replace('"*.Cu"', '"*.Cu"')
    return blk


def fmt(v):
    """Compact float formatting for coordinates."""
    return ("%.6f" % v).rstrip("0").rstrip(".") if v else "0"


def pcb_pin_nets(pcb_path, ref, sch_pin_names):
    """{pin name: net} from the board's CURRENT pads, via the old symbol."""
    t = pcb_path.read_text(encoding="utf-8")
    for s, e in top_blocks(t, "footprint"):
        if prop(t[s:e], "Reference") == ref:
            out = {}
            for pm in re.finditer(r'\(pad "([^"]*)"', t[s:e]):
                pb = t[s:e][pm.start():block_end(t[s:e], pm.start())]
                n = re.search(r'\(net \d+ "((?:[^"\\]|\\.)*)"\)', pb)
                name = sch_pin_names.get(pm.group(1))
                if n and name:
                    out.setdefault(name, n.group(1))
            return out
    raise SystemExit("footprint %s not on board" % ref)


def main():
    """CLI entry point."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("sch")
    ap.add_argument("pcb")
    ap.add_argument("ref")
    ap.add_argument("symbol")
    ap.add_argument("--set", action="append", default=[],
                    help="NEWPIN=NET: attach a global label (fix/new net)")
    ap.add_argument("--nc", action="append", default=[],
                    help="NEWPIN: add a no-connect flag")
    ap.add_argument("--rewire", action="store_true",
                    help="drop ALL old pin attachments; nets come only from "
                         "--set (for parts whose old pin map is wrong)")
    args = ap.parse_args()
    sch, pcb = pathlib.Path(args.sch), pathlib.Path(args.pcb)

    # Old pin-number -> name map, captured before the schematic changes.
    t = sch.read_text(encoding="utf-8")
    _, _, inst = find_instance(t, args.ref)
    cs, ce = cached_symbol(t, inst["lib_id"])
    old_names = {n: p[0] for n, p in sym_pins(t[cs:ce]).items()}
    name_to_net = pcb_pin_nets(pcb, args.ref, old_names)

    sets = dict(s.split("=", 1) for s in args.set)
    sch_text, fp_id, value, new_names = relink_sch(
        sch, args.ref, args.symbol, sets, args.nc, args.rewire)
    if args.rewire:
        name_to_net = {}
    for pin, net in sets.items():
        name_to_net[new_names[pin]] = net
    pcb_text, removed = relink_pcb(pcb, args.ref, fp_id, new_names,
                                   name_to_net, value)
    # Both edits succeeded in memory: only now touch the files (atomic).
    sch.write_text(sch_text, encoding="utf-8")
    pcb.write_text(pcb_text, encoding="utf-8")
    print("%s -> %s:%s  footprint %s  (%d stale segments removed)"
          % (args.ref, NICK, args.symbol, fp_id, removed))
    for num in sorted(new_names, key=lambda x: (len(x), x)):
        name = new_names[num]
        net = name_to_net.get(name, "(none)")
        print("   pin %-3s %-10s net %s" % (num, name, net))
    return 0


if __name__ == "__main__":
    sys.exit(main())
