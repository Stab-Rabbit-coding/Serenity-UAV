#!/usr/bin/env python3
"""Stamp the Wurth usage notice and the uncrewed-only notice onto boards.

Owner decision 2026-09-26 (avionics/WBS.md U7.1d): keep the Wurth
Elektronik parts, and record Wurth's datasheet usage notice VERBATIM on
every board that carries a Wurth part -- in the board's ``.md`` file, as
a text item on the schematic drawing page, as ``Cmts.User`` text on the
PCB, and as title-block comments 8/9 on both -- together with a statement
that the Serenity avionics are intended for use only on uncrewed aircraft.

Source of the verbatim text: Wurth Elektronik eiSos, 749010012A data
sheet rev 004.000 (2024-04-11), p. 1 (the same notice is printed on every
Wurth product data sheet).  [REF-SENSOR-028 in REFERENCES.md]

Idempotent: every inserted item carries MARKER; re-running replaces the
previous stamp instead of adding a second one.  Text-level S-expression
edit (no pcbnew/kiutils -- see PCBNEW_SWIG_BUG.md); geometry, nets and
UUIDs of existing items are untouched.

Attribution: authored by Claude Opus 5.5 (Anthropic), 2026-09-26.

Usage::

    python3 tools/add_board_notices.py            # all Wurth-bearing boards
"""

import pathlib
import re
import sys
import textwrap
import uuid

ROOT = pathlib.Path(__file__).resolve().parent.parent
KICAD = ROOT / "avionics" / "kicad"
MARKER = "USAGE-NOTICE-2026-09-26"

WURTH_NOTICE = (
    "This electronic component has been designed and developed for usage in "
    "general electronic equipment only. This product is not authorized for "
    "use in equipment where a higher safety standard and reliability "
    "standard is especially required or where a failure of the product is "
    "reasonably expected to cause severe personal injury or death, unless "
    "the parties have executed an agreement specifically governing such "
    "use. Moreover Würth Elektronik eiSos GmbH & Co KG products are neither "
    "designed nor intended for use in areas such as military, aerospace, "
    "aviation, nuclear control, submarine, transportation, transportation "
    "signal, disaster prevention, medical, public information network etc.. "
    "Würth Elektronik eiSos GmbH & Co KG must be informed about the intent "
    "of such usage before the design-in stage. In addition, sufficient "
    "reliability evaluation checks for safety must be performed on every "
    "electronic component which is used in electrical circuits that require "
    "high safety and reliability functions or performance."
)
UNCREWED = ("INTENDED USE: The Serenity-UAV avionics, including this board, "
            "are intended for use only on uncrewed aircraft.")

# Board -> (project path stem, .md file, Wurth parts carried on the board).
BOARDS = {
    "Pilot": ("Pilot/kicads/Pilot", "Pilot/Pilot.md",
              "749010012A, 742792512, WE-MAPI 3015"),
    "TACCO": ("TACCO/kicads/TACCO", "TACCO/TACCO.md",
              "749010012A, 742792510, WE-MAPI 3015"),
    "Commo": ("Commo/kicads/Commo", "Commo/Commo.md",
              "749010012A, 742792510, 742792512"),
    "FlightEngineer": ("FlightEngineer/kicads/FlightEngineer",
                       "FlightEngineer/FlightEngineer.md",
                       "7440640500, 742792612"),
    "Observer": ("Observer/kicads/Observer", "Observer/Observer.md",
                 "749010012A"),
}


def q(text):
    """Quote for an S-expression string (KiCad escapes \\ and ")."""
    return '"' + (text.replace("\\", "\\\\").replace('"', '\\"')
                  .replace("\n", "\\n")) + '"'


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


def strip_marked(text, head):
    """Remove every top-level ``(head ...)`` block containing MARKER."""
    out, i = [], 0
    for m in re.finditer(r"\n\s*\(%s\b" % re.escape(head), text):
        s = text.index("(", m.start())
        if s < i:
            continue
        e = block_end(text, s)
        if MARKER in text[s:e]:
            out.append(text[i:m.start()])
            i = e
    out.append(text[i:])
    return "".join(out)


def set_comments(text, parts):
    """Write title-block comments 8 and 9 (replacing any previous ones)."""
    tb = text.index("(title_block")
    tb_end = block_end(text, tb)
    blk = re.sub(r'\s*\(comment [89] "(?:[^"\\]|\\.)*"\)', "", text[tb:tb_end])
    add = ('\n\t\t(comment 8 %s)\n\t\t(comment 9 %s)'
           % (q("Wurth parts (%s): see Wurth usage notice on this page "
                "[%s]" % (parts, MARKER)),
              q("Intended for use ONLY on uncrewed aircraft")))
    blk = blk[:-1].rstrip() + add + "\n\t)"
    return text[:tb] + blk + text[tb_end:]


def notice_lines(parts):
    """The full notice, wrapped to ~100 columns for on-drawing text."""
    body = ("WÜRTH ELEKTRONIK USAGE NOTICE (verbatim, 749010012A data sheet "
            "rev 004.000 p.1; applies to Würth parts on this board: %s):"
            % parts)
    lines = textwrap.wrap(body, 100) + [""] + textwrap.wrap(WURTH_NOTICE, 100)
    return lines + [""] + textwrap.wrap(UNCREWED, 100) + ["[%s]" % MARKER]


def stamp_sch(path, parts):
    """Add the notice text item + title-block comments to a schematic."""
    t = strip_marked(path.read_text(encoding="utf-8"), "text")
    ys = [float(y) for y in re.findall(r"\(at [-\d.]+ ([-\d.]+)", t)]
    xs = [float(x) for x in re.findall(r"\(at ([-\d.]+) [-\d.]+", t)]
    lines = notice_lines(parts)
    # Sit the block just above everything already drawn, grid-aligned.
    x = round(min(xs) / 2.54) * 2.54
    y = round((min(ys) - 2.54 * (len(lines) + 3)) / 2.54) * 2.54
    item = ('\n\t(text %s\n\t\t(exclude_from_sim no)\n\t\t(at %.2f %.2f 0)\n'
            '\t\t(effects (font (size 1.27 1.27)) (justify left top))\n'
            '\t\t(uuid "%s")\n\t)'
            % (q("\n".join(lines)), x, y, uuid.uuid4()))
    i = t.rindex("(sheet_instances") if "(sheet_instances" in t \
        else t.rstrip().rindex(")")
    t = t[:i].rstrip() + item + "\n\t" + t[i:]
    path.write_text(set_comments(t, parts), encoding="utf-8")


def stamp_pcb(path, parts):
    """Add the notice as Cmts.User text right of the board outline."""
    t = strip_marked(path.read_text(encoding="utf-8"), "gr_text")
    edges = " ".join(re.findall(r'\(gr_(?:line|rect|arc|poly).*?'
                                r'\(layer "Edge\.Cuts"\)', t, re.S))
    pts = [(float(a), float(b)) for a, b in
           re.findall(r"\((?:start|end|xy|mid) ([-\d.]+) ([-\d.]+)\)", edges)]
    x = max(p[0] for p in pts) + 5.0
    y = min(p[1] for p in pts)
    item = ('\n\t(gr_text %s\n\t\t(at %.2f %.2f 0)\n\t\t(layer "Cmts.User")\n'
            '\t\t(uuid "%s")\n\t\t(effects (font (size 0.8 0.8) '
            '(thickness 0.1)) (justify left top))\n\t)'
            % (q("\n".join(notice_lines(parts))), x, y, uuid.uuid4()))
    i = t.rstrip().rindex(")")
    t = t[:i].rstrip() + item + "\n)\n"
    path.write_text(set_comments(t, parts), encoding="utf-8")


def stamp_md(path, parts):
    """Add / replace the notice section in the board's markdown file."""
    t = path.read_text(encoding="utf-8")
    t = re.sub(r"\n## Usage notices\n.*?<!-- /%s -->\n" % MARKER, "\n", t,
               flags=re.S)
    sec = ("\n## Usage notices\n\n"
           "**Intended use:** the Serenity-UAV avionics, including this "
           "board, are intended for use only on uncrewed aircraft.\n\n"
           "**Würth Elektronik usage notice** — applies to the Würth parts on "
           "this board (%s). Quoted verbatim from Würth Elektronik eiSos, "
           "*749010012A data sheet* rev 004.000 (2024-04-11), p. 1 "
           "[REF-SENSOR-028]; the same notice appears on every Würth product "
           "data sheet. Owner decision 2026-09-26: the Würth parts are "
           "retained (avionics/WBS.md U7.1d).\n\n> %s\n\n<!-- /%s -->\n"
           % (parts, WURTH_NOTICE, MARKER))
    # Wrap to 80 columns (markdownlint MD013); a wrapped blockquote still
    # renders as the single verbatim paragraph.
    out = []
    for para in sec.split("\n"):
        pre = "> " if para.startswith("> ") else ""
        body = para[len(pre):]
        out += ([pre + ln for ln in textwrap.wrap(body, 80 - len(pre))]
                if len(para) > 80 else [para])
    path.write_text(t.rstrip() + "\n" + "\n".join(out), encoding="utf-8")


def main():
    """Stamp every Wurth-bearing board."""
    for name, (stem, md, parts) in BOARDS.items():
        stamp_sch(KICAD / (stem + ".kicad_sch"), parts)
        stamp_pcb(KICAD / (stem + ".kicad_pcb"), parts)
        stamp_md(KICAD / md, parts)
        print("stamped %s" % name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
