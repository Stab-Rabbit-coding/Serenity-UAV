#!/usr/bin/env python3
"""scad_flatten.py -- flatten an OpenSCAD file that layers parameter overrides on a base file.

Why: nacelle_pod_64mm_tandem.scad used to `include` the 50 mm pod and override its
parameters (OpenSCAD keeps the LAST assignment of a variable for the whole file scope, and
the last definition of a module or function).  That tied the 64 mm nacelle to the 50 mm
sources.  This tool applies OpenSCAD's own rules once and writes ONE self-contained file,
so the 50 mm base can be archived.

Rules reproduced (OpenSCAD 2021.01, `FileModule::instantiate` / `evaluate_assignments`):
  * `include <f>` is textual inclusion at file scope, so every included file is spliced in
    at the include statement's position (recursively).  `use <f>` is kept as written.
  * A variable assigned several times keeps ONE assignment: at the position of its FIRST
    assignment, with the expression of its LAST (the override rule documented in
    nacelle_pod_64mm_tandem.scad).
  * A module or function defined several times keeps the LAST definition.
  * Everything else (geometry calls, echo, for/if, comments) is kept in order.

Usage:
    tools/scad_flatten.py ROOT.scad -o OUT.scad [--keep-include NAME ...]
        --keep-include   leave `include <NAME>` as an include (generated or shared files)
Exit 2 if a kept include defines a name the flattened file also defines (an unsafe split).

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic) under the author's direction, 2026-11-07.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ASSIGN = re.compile(r"^\s*([$A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)")
MODULE = re.compile(r"^\s*module\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
FUNCTION = re.compile(r"^\s*function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
BRACED = ("module", "if", "for", "intersection_for", "difference", "union", "intersection")
INCLUDE = re.compile(r"^\s*include\s*<([^>]+)>\s*;?")


def split_statements(src: str) -> list[dict]:
    """Split file-scope source into statements, each with its leading comment text.

    Returns dicts: {lead: comments/blank lines before it, text: the statement, kind, name}.
    """
    out: list[dict] = []
    i, n = 0, len(src)
    lead_start = 0
    while i < n:
        # skip whitespace and comments to find where the next statement begins
        j = i
        while j < n:
            if src[j].isspace():
                j += 1
            elif src.startswith("//", j):
                k = src.find("\n", j)
                j = n if k < 0 else k + 1
            elif src.startswith("/*", j):
                k = src.find("*/", j + 2)
                j = n if k < 0 else k + 2
            else:
                break
        if j >= n:
            if src[lead_start:]:
                out.append({"lead": src[lead_start:], "text": "", "kind": "tail", "name": ""})
            break
        start = j
        depth = 0
        k = start
        end: int | None = None
        first_word = re.match(r"[A-Za-z_]+", src[start:])
        word = first_word.group(0) if first_word else ""
        inc_m = re.match(r"(?:include|use)\s*<[^>\n]*>[ \t]*;?", src[start:])
        if inc_m:
            # include/use take no terminating semicolon: they end at the closing '>'
            end = start + inc_m.end()
            k = n  # skip the scanner below
        while k < n:
            c = src[k]
            if c == '"':
                k += 1
                while k < n and src[k] != '"':
                    k += 2 if src[k] == "\\" else 1
            elif src.startswith("//", k):
                nl = src.find("\n", k)
                k = n if nl < 0 else nl
                continue
            elif src.startswith("/*", k):
                close = src.find("*/", k + 2)
                k = n if close < 0 else close + 1
            elif c in "([{":
                depth += 1
            elif c in ")]}":
                depth -= 1
                if depth == 0 and c == "}" and word in BRACED:
                    # a braced body ends the statement unless an `else` follows
                    if not re.match(r"\s*else\b", src[k + 1:]):
                        end = k + 1
                        break
            elif c == ";" and depth == 0:
                end = k + 1
                break
            k += 1
        if end is None:
            end = n
        text = src[start:end]
        kind, name = "other", ""
        m_inc, m_mod = INCLUDE.match(text), MODULE.match(text)
        m_fun, m_asg = FUNCTION.match(text), ASSIGN.match(text)
        if m_inc:
            kind, name = "include", m_inc.group(1)
        elif re.match(r"\s*use\s*<", text):
            kind = "use"
        elif m_mod:
            kind, name = "module", m_mod.group(1)
        elif m_fun:
            kind, name = "function", m_fun.group(1)
        elif m_asg:
            kind, name = "assign", m_asg.group(1)
        out.append({"lead": src[lead_start:start], "text": text, "kind": kind, "name": name})
        i = lead_start = end
    return out


def expand(path: Path, keep: set[str], seen: tuple[Path, ...] = ()) -> list[dict]:
    """Statements of `path` with non-kept includes spliced in recursively."""
    if path in seen:
        raise SystemExit(f"include cycle at {path}")
    stmts: list[dict] = []
    for s in split_statements(path.read_text(encoding="utf-8")):
        if s["kind"] == "include" and Path(s["name"]).name not in keep:
            inc = (path.parent / s["name"]).resolve()
            if not inc.exists():
                raise SystemExit(f"{path}: include <{s['name']}> not found")
            stmts.append({"lead": s["lead"] + f"// ---- begin include <{s['name']}> "
                          f"(inlined by scad_flatten.py) ----\n",
                          "text": "", "kind": "note", "name": ""})
            stmts.extend(expand(inc, keep, seen + (path,)))
            stmts.append({"lead": f"// ---- end include <{s['name']}> ----\n", "text": "",
                          "kind": "note", "name": ""})
        else:
            stmts.append(s)
    return stmts


def flatten(stmts: list[dict]) -> list[dict]:
    """Apply OpenSCAD's last-wins rules."""
    last_assign: dict[str, dict] = {}
    last_def: dict[tuple[str, str], dict] = {}
    for s in stmts:
        if s["kind"] == "assign":
            last_assign[s["name"]] = s
        elif s["kind"] in ("module", "function"):
            last_def[(s["kind"], s["name"])] = s
    out: list[dict] = []
    first_seen: set[str] = set()
    for s in stmts:
        if s["kind"] == "assign":
            if s["name"] in first_seen:
                # later duplicate: drop the statement, keep any comments that preceded it
                if s["lead"].strip():
                    out.append({"lead": s["lead"], "text": "", "kind": "note", "name": ""})
                continue
            first_seen.add(s["name"])
            winner = last_assign[s["name"]]
            if winner is s:
                out.append(s)
            else:
                out.append({"lead": s["lead"] + f"// [flattened] {s['name']}: value from its "
                            "last assignment (override), kept at the first position\n",
                            "text": winner["text"], "kind": "assign", "name": s["name"]})
        elif s["kind"] in ("module", "function"):
            if last_def[(s["kind"], s["name"])] is s:
                out.append(s)
            elif s["lead"].strip():
                out.append({"lead": s["lead"], "text": "", "kind": "note", "name": ""})
        else:
            out.append(s)
    return out


def defined_names(stmts: list[dict]) -> set[str]:
    return {s["name"] for s in stmts if s["kind"] in ("assign", "module", "function")}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", type=Path)
    ap.add_argument("-o", "--out", type=Path, required=True)
    ap.add_argument("--keep-include", nargs="*", default=[])
    ap.add_argument("--header", type=Path, help="text file placed above the flattened body")
    args = ap.parse_args(argv)
    keep = set(args.keep_include)
    stmts = expand(args.root.resolve(), keep)
    flat = flatten(stmts)
    # a kept include must not redefine a name the flattened file also defines
    clash = []
    for name in sorted(keep):
        inc = (args.root.resolve().parent / name)
        if inc.exists():
            both = defined_names(split_statements(inc.read_text(encoding="utf-8"))) \
                & defined_names(flat)
            clash += [f"{name}: {b}" for b in sorted(both)]
    if clash:
        print("UNSAFE: kept include(s) define names also defined in the flattened file:",
              file=sys.stderr)
        for c in clash:
            print("  " + c, file=sys.stderr)
        return 2
    body = "".join(s["lead"] + s["text"] for s in flat)
    head = args.header.read_text(encoding="utf-8") if args.header else ""
    args.out.write_text(head + body + ("" if body.endswith("\n") else "\n"), encoding="utf-8")
    n_assign = sum(1 for s in stmts if s["kind"] == "assign")
    n_kept = sum(1 for s in flat if s["kind"] == "assign")
    print(f"scad_flatten: {args.root.name} -> {args.out.name}: "
          f"{n_assign} assignments -> {n_kept}; "
          f"{sum(1 for s in stmts if s['kind'] in ('module', 'function'))} defs -> "
          f"{sum(1 for s in flat if s['kind'] in ('module', 'function'))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
