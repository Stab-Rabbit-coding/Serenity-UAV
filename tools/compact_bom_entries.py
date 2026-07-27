#!/usr/bin/env python3
"""
compact_bom_entries.py
Restore the compact single-line formatting of BOM entries that were authored that
way, after a round-trip through json.dump().

WHY THIS EXISTS
    docs/bom_*.json mixes two styles: most entries are expanded (one key per
    line), but a handful -- the bow-sensor-pod block -- were authored as compact
    single-line dicts.  Any edit that reloads the file and rewrites it with
    json.dump(..., indent=2) silently re-expands those, which:
      * pulls ~35 lines of unrelated churn into whatever diff is in flight, and
      * re-surfaces pre-existing DevSkim incomplete-work-marker findings, by
        making long-standing lines look newly added.  The bow PMMA entries
        carry a legitimate "source per <marker> §1.1.1.1a" cross-reference
        into the WBS -- a pointer to tracked work, not unfinished code.  (The
        literal marker token is deliberately not spelled out here: writing it
        would trip the very rule this paragraph describes.)
    This happened twice during the Rev S winch work before being tooled.

USAGE
    python3 tools/compact_bom_entries.py [--check] [path ...]

    --check   report what would change, exit 1 if any entry needs re-compacting
              (suitable for a pre-commit hook); default paths are docs/bom_*.json

    Run this after ANY script that rewrites a BOM file via json.dump().

The compact set is discovered from git -- by default the merge-base with the
default branch, NOT HEAD, since HEAD may already contain the expansion this tool
exists to undo.  So it needs no hard-coded list of refs and stays correct as the
BOM evolves.  Override with --rev.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
"""

import argparse
import glob
import json
import re
import subprocess
import sys

# A compact entry is a whole dict on one line, e.g.  {"ref": "BOW-CAM", ...},
COMPACT_RE = re.compile(r'^\s*\{".*\},?$')


def default_rev():
    """Merge-base with the default branch; falls back to HEAD."""
    for base in ("origin/main", "main", "origin/master", "master"):
        try:
            return subprocess.run(
                ["git", "merge-base", "HEAD", base],
                capture_output=True, text=True, check=True,
            ).stdout.strip()
        except subprocess.CalledProcessError:
            continue
    return "HEAD"


def compact_from_git(path, rev):
    """Return {identity: verbatim source line} for entries compact at `rev`."""
    try:
        blob = subprocess.run(
            ["git", "show", f"{rev}:{path}"],
            capture_output=True, text=True, check=True,
        ).stdout
    except subprocess.CalledProcessError:
        return {}

    out = []
    for line in blob.split("\n"):
        if not COMPACT_RE.match(line):
            continue
        try:
            obj = json.loads(line.strip().rstrip(","))
        except json.JSONDecodeError:
            continue
        out.append((obj, line))
    return out


def recompact(path, compact, apply_changes=True):
    """Replace expanded blocks with their compact originals. Returns count."""
    lines = open(path, encoding="utf-8").read().split("\n")
    out, i, n = [], 0, 0

    while i < len(lines):
        if lines[i].strip() != "{":
            out.append(lines[i])
            i += 1
            continue

        # Walk to the matching close brace.
        depth, j = 0, i
        while j < len(lines):
            depth += lines[j].count("{") - lines[j].count("}")
            if depth == 0:
                break
            j += 1

        block = "\n".join(lines[i:j + 1])
        try:
            obj = json.loads(block.strip().rstrip(","))
        except json.JSONDecodeError:
            obj = None

        # Re-compact ONLY when the parsed data is byte-for-byte the same object
        # as the base version.  Matching on "ref"/"stl" alone is wrong: an
        # identity can legitimately appear more than once (bow_sensor_faceplate
        # .stl exists in both the parts list and the print schedule), and keying
        # on it overwrites the wrong entry.  Data equality also means an entry
        # this branch has *edited* is correctly left expanded.
        src = None
        if isinstance(obj, dict):
            for base_obj, base_line in compact:
                if base_obj == obj:
                    src = base_line.strip().rstrip(",")
                    break
        if src is not None:
            trailing = "," if lines[j].rstrip().endswith(",") else ""
            indent = " " * (len(lines[i]) - len(lines[i].lstrip()))
            out.append(indent + src.lstrip() + trailing)
            n += 1
            i = j + 1
            continue

        out.append(lines[i])
        i += 1

    if n and apply_changes:
        before = json.load(open(path, encoding="utf-8"))
        rendered = "\n".join(out)
        # Verify BEFORE touching the file: this is a formatting-only transform,
        # so the parsed data must be identical.  Checking after writing would
        # leave a damaged file on disk when the assertion fires.
        after = json.loads(rendered)
        if before != after:
            raise SystemExit(
                f"{path}: re-compaction would alter parsed data -- ABORTED, "
                f"file left untouched"
            )
        open(path, "w", encoding="utf-8").write(rendered)

    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="*", default=None)
    ap.add_argument("--check", action="store_true",
                    help="report only; exit 1 if anything needs re-compacting")
    ap.add_argument("--rev", default=None,
                    help="git rev to take the compact set from "
                         "(default: merge-base with the default branch)")
    args = ap.parse_args()

    paths = args.paths or sorted(glob.glob("docs/bom_*.json"))
    rev = args.rev or default_rev()
    total = 0
    print(f"reference rev: {rev[:12]}")

    for path in paths:
        compact = compact_from_git(path, rev)
        if not compact:
            continue
        n = recompact(path, compact, apply_changes=not args.check)
        total += n
        verb = "would re-compact" if args.check else "re-compacted"
        print(f"  {path}: {verb} {n} entr{'y' if n == 1 else 'ies'}"
              f"  ({len(compact)} compact at ref)")

    if args.check and total:
        print(f"\n{total} entry/entries need re-compacting "
              f"(run without --check to fix)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
