#!/usr/bin/env python3
"""wbs_burndown.py -- open and closed WBS items per federation file, and change since a baseline.

The execution plan (docs/plans/2026-11-07-001-feat-rev-u-completion-execution-plan.md)
measures each sprint by the items it CLOSES.  Closures are counted, not the net open count,
so recording a new finding (AGENTS.md requires it the same day) never counts against a sprint.

The file list and the open-item rule are the federation's own: tools/gen_todo_from_wbs.py
PAIRS and extract_open_items() (an open item = an unchecked box not inside another open
box; the per-folder open-items line count).  A closed item is any checked box, at any depth.  The
root WBS.md is an index that repeats many subsystem lines AND owns project-wide items
(0.x, 5.x, 6.x), so it is reported on its own row and never added to the subsystem total.

Usage:
    python3 tools/wbs_burndown.py                         # open/closed per WBS.md
    python3 tools/wbs_burndown.py --json snap.json        # also write a snapshot
    python3 tools/wbs_burndown.py --baseline snap.json    # add the change since that snapshot
Exit 0 on a report; 2 if the baseline file is not a wbs_burndown snapshot.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic, Claude Opus 5.5) under the author's direction, 2026-11-07.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_todo_from_wbs import PAIRS, extract_open_items  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ROOT_WBS = "WBS.md"
BOX = re.compile(r"^(\s*)- \[( |x|X)\]")
SNAPSHOT_KEYS = ("date", "files", "total_open", "total_closed", "root")
#: Counting rule stamped into every snapshot; a baseline made under another rule is refused.
RULE = "open:top-level(gen_todo); closed:any-depth"


def count_closed(text: str) -> int:
    """Every checked box, at any nesting depth.

    Open items follow the open-items rule (top level only), but a closure is work done wherever it
    sits: many WBS entries (e.g. NAC-64-ASM-01) are sub-items of a still-open parent, and the
    top-level rule would hide their closure from the sprint measure.
    """
    n = 0
    for raw in text.splitlines():
        box = BOX.match(raw)
        if box and box.group(2) != " ":
            n += 1
    return n


def count_file(text: str, root: bool) -> dict[str, int]:
    open_n = sum(len(items) for _, _, items in extract_open_items(text, root=root))
    return {"open": open_n, "closed": count_closed(text)}


def snapshot(repo: Path = ROOT, pairs: tuple[str, ...] = PAIRS) -> dict:
    files: dict[str, dict[str, int]] = {}
    for rel in pairs:
        p = repo / rel
        text = p.read_text(encoding="utf-8") if p.exists() else ""
        files[rel] = count_file(text, root=(rel == ROOT_WBS))
    root = files.pop(ROOT_WBS, {"open": 0, "closed": 0})
    return {"date": date.today().isoformat(), "rule": RULE, "files": files, "root": root,
            "total_open": sum(v["open"] for v in files.values()),
            "total_closed": sum(v["closed"] for v in files.values())}


def report(snap: dict, base: dict | None = None) -> list[str]:
    """Table lines; with a baseline, the change in open and closed per file and in total."""
    names = list(snap["files"])
    if base:
        names += [f for f in base["files"] if f not in snap["files"]]   # removed since
    head = f"{'WBS file':46s} {'open':>5s} {'closed':>6s}"
    if base:
        head += f" {'d_open':>7s} {'closed+':>7s}"
    out = [head]

    def row(label: str, now: dict, was: dict | None) -> str:
        line = f"{label:46s} {now['open']:5d} {now['closed']:6d}"
        if base:
            was = was or {"open": 0, "closed": 0}
            line += f" {now['open'] - was['open']:+7d} {now['closed'] - was['closed']:+7d}"
        return line

    zero = {"open": 0, "closed": 0}
    for f in names:
        out.append(row(f, snap["files"].get(f, zero), base["files"].get(f) if base else None))
    out.append(row("TOTAL (subsystem files)", {"open": snap["total_open"],
                                               "closed": snap["total_closed"]},
                   {"open": base["total_open"], "closed": base["total_closed"]} if base else None))
    out.append(row("root WBS.md (index + project items)", snap["root"],
                   base["root"] if base else None))
    if base:
        out.append(f"baseline {base['date']}: {base['total_open']} open, "
                   f"{base['total_closed']} closed (subsystem files)")
    return out


def load_baseline(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = [k for k in SNAPSHOT_KEYS if k not in data]
    if missing:
        raise ValueError(f"{path} is not a wbs_burndown snapshot (missing {', '.join(missing)})")
    if data.get("rule") != RULE:
        raise ValueError(f"{path} was counted under rule {data.get('rule')!r}, not {RULE!r}; "
                         "regenerate the baseline from its commit")
    return data


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], epilog=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", type=Path, help="write the snapshot to this file")
    ap.add_argument("--baseline", type=Path, help="compare with an earlier snapshot")
    args = ap.parse_args(argv)
    base = None
    if args.baseline:
        try:
            base = load_baseline(args.baseline)
        except (ValueError, json.JSONDecodeError) as exc:
            print(f"wbs_burndown: {exc}", file=sys.stderr)
            return 2
    snap = snapshot()
    print("\n".join(report(snap, base)))
    if args.json:
        args.json.write_text(json.dumps(snap, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
