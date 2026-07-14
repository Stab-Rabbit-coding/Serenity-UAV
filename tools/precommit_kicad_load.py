#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
precommit_kicad_load.py — block a commit if any staged KiCad board/schematic is
unloadable or has a broken copper stackup / outline.
==============================================================================
Guards against the recurring GUI-save corruption that has bitten Jayne three
times (a dropped In2.Cu layer -> invalid 3-copper-layer stackup -> "Failed to
load board", and self-intersecting Edge.Cuts). Those faults do not show up in a
normal diff, so they get committed and only surface when someone next opens the
board. This runs before the commit lands.

Checks, per staged `*.kicad_pcb` / `*.kicad_sch`:
  1. LOADS in `kicad-cli` (the definitive "is it corrupt" test).
  2. (PCB) copper layers form a valid stackup: F.Cu + B.Cu present, and the
     inner copper layers are a contiguous In1..InN with no gaps (the exact
     In2.Cu-missing bug).
  3. (PCB) reports no `invalid_outline` DRC violation (malformed Edge.Cuts).

Exit non-zero (blocking the commit) with a clear message if any check fails.
Full DRC debt (clearance, unrouted, silk) is NOT checked here — that is CI's
job (`tools/validate_kicad.py`); this hook only catches "the file is broken".

Usage:
  precommit_kicad_load.py [FILE ...]     # explicit files (pre-commit passes them)
  precommit_kicad_load.py                 # else: auto-discovers staged KiCad files
  precommit_kicad_load.py --all           # check every tracked KiCad file

Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  (Griffing Technology LLC)
AI-assist: Claude Opus 4.8 (Anthropic) — hook authoring, 2026-07-06.
License: CC BY 4.0
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CANON_COPPER = {"F.Cu", "B.Cu"}


def sh(args):
    return subprocess.run(args, capture_output=True, text=True)


def staged_kicad_files():
    r = sh(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"])
    out = []
    for line in r.stdout.splitlines():
        if line.endswith((".kicad_pcb", ".kicad_sch")) and Path(line).exists():
            out.append(Path(line))
    return out


def all_kicad_files():
    r = sh(["git", "ls-files", "*.kicad_pcb", "*.kicad_sch"])
    return [Path(p) for p in r.stdout.splitlines() if Path(p).exists()]


def check_loads(path, is_pcb):
    """Return (ok, report_json_or_None, message)."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        rpt = tf.name
    if is_pcb:
        r = sh(["kicad-cli", "pcb", "drc", "--format", "json", "-o", rpt, str(path)])
    else:
        r = sh(["kicad-cli", "sch", "erc", "--format", "json", "-o", rpt, str(path)])
    combined = r.stdout + r.stderr
    if "Failed to load" in combined or (
        "Saved" not in combined and "violations" not in combined
    ):
        return False, None, "kicad-cli could not load the file (corrupt)."
    try:
        data = json.load(open(rpt))
    except Exception:
        data = None
    return True, data, ""


def check_pcb_stackup(path):
    """Validate the copper layer list directly from the file text: F.Cu + B.Cu
    present and inner copper contiguous In1..InN (catches the In2.Cu-missing bug
    even if a future kicad-cli tolerates it)."""
    txt = path.read_text(encoding="utf-8")
    m = re.search(r"\(layers\b(.*?)\n\t\)", txt, re.S)
    if not m:
        return True, ""  # no layer block found; leave to the load check
    names = re.findall(r'"((?:F|B|In\d+)\.Cu)"', m.group(1))
    names = set(names)
    if not CANON_COPPER <= names:
        return False, f"copper layers missing F.Cu/B.Cu (have {sorted(names)})."
    inners = sorted(
        int(re.match(r"In(\d+)\.Cu", n).group(1)) for n in names if n.startswith("In")
    )
    if inners and inners != list(range(1, len(inners) + 1)):
        return (
            False,
            f"inner copper layers are not contiguous In1..InN "
            f"(have In{inners}); a dropped inner layer makes an "
            f"invalid stackup that will not load.",
        )
    return True, ""


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--all" in sys.argv[1:]:
        files = all_kicad_files()
    elif args:
        files = [Path(a) for a in args if a.endswith((".kicad_pcb", ".kicad_sch"))]
    else:
        files = staged_kicad_files()

    if not files:
        return 0

    if sh(["kicad-cli", "version"]).returncode != 0:
        print(
            "precommit_kicad_load: kicad-cli not found — skipping (install KiCad "
            "to enable this guard).",
            file=sys.stderr,
        )
        return 0

    failures = []
    for f in files:
        is_pcb = f.suffix == ".kicad_pcb"
        ok, data, msg = check_loads(f, is_pcb)
        if not ok:
            failures.append((f, msg))
            continue
        if is_pcb:
            sok, smsg = check_pcb_stackup(f)
            if not sok:
                failures.append((f, smsg))
                continue
            if data:
                n = sum(
                    1
                    for v in data.get("violations", [])
                    if v.get("type") == "invalid_outline"
                )
                if n:
                    failures.append(
                        (
                            f,
                            f"{n} invalid_outline violation(s) — "
                            f"Edge.Cuts is malformed/self-intersecting.",
                        )
                    )

    if failures:
        print("\n❌  Commit blocked — broken KiCad file(s):\n", file=sys.stderr)
        for f, msg in failures:
            print(f"   {f}: {msg}", file=sys.stderr)
        print(
            "\nFix the file (it must open in KiCad / `kicad-cli`) before committing.\n"
            "This is the recurring In2.Cu / Edge.Cuts corruption guard — see\n"
            "avionics/kicad/Jayne/Jayne.md. To bypass in an emergency:\n"
            "  git commit --no-verify\n",
            file=sys.stderr,
        )
        return 1

    print(f"precommit_kicad_load: {len(files)} KiCad file(s) load OK.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
