#!/usr/bin/env python3
"""Fail on aircraft-datum drift (plan 2026-10-19-001, rules R1-R4).

Owner directive 2026-10-19: one aircraft datum (centreline, nose tip, static
ground plane); datums are imported, never re-typed; "standardize the
generator scripts to prevent future drift".  Checks every active .py / .scad
file and every airframe STL:

  D1  a datum name (X_CL, CENTRE_X, CARGO_X_CL, X_CL_HULL, Y_NOSE, GROUND_Z,
      SPAR_Y, SPAR_Z) assigned a numeric literal anywhere but
      tools/hull_datums.py or a GENERATED SCAD include;
  D2  an R1-frame datum literal in code: -169.85 / -169.9 / -169.241 (old
      centreline), -305.70x (old nose), as a number, not inside a comment;
  D3  a restated bake translation: `BAKE_T = np.array([<literals>])`;
  D4  an STL still stamped "SerenityUAV HULL-FRAME R1";
  D5  airframe/openscad/hull_datums.scad out of date with hull_datums.py.

Run: /usr/bin/python3 tools/check_datum_drift.py [--summary]
Exit 2 on any finding.

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, 2026-10-19, per AGENTS.md AI attribution.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import hull_datums as hd  # noqa: E402

SKIP = ("/archive", "archives/", "node_modules", "/.git/", "gcs/", "docs/references",
        "graphical-build-guide/", ".worktrees/", ".claude/")
OWNER = {"tools/hull_datums.py", "tools/check_datum_drift.py", "tools/datum_regression.py",
         "tools/frame_inventory.py"}
NAMES = r"(X_CL|CENTRE_X|CENTER_X|CARGO_X_CL|X_CL_HULL|Y_NOSE|GROUND_Z|SPAR_Y|SPAR_Z)"
# [ \t]* not \s*: \s would span blank lines and mis-report the line number.
D1 = re.compile(rf"^[ \t]*{NAMES}[ \t]*=[ \t]*[-+]?\d", re.M)
# A leg- or part-local coordinate that merely shares a datum name (for example
# GROUND_Z in the canonical leg SCADs, the foot-sole plane in the LEG frame) is
# exempt when its own source line says so with the token "leg-local" or
# "part-local".  Owner-flagged false positive, handoff 2026-10-20 step 4.
LOCAL_OK = ("leg-local", "part-local")
D2 = re.compile(r"(?<![\w.])-(169\.(?:85|9|241)\d*|305\.70\d*)(?![\w.])")
D3 = re.compile(r"BAKE_T\s*=\s*np\.array\(\s*\[\s*[-+]?\d")
R1_MARKER = b"SerenityUAV HULL-FRAME R1"


def strip_comments(text: str, scad: bool) -> str:
    out = []
    for line in text.splitlines():
        mark = "//" if scad else "#"
        i = line.find(mark)
        out.append(line if i < 0 else line[:i])
    return "\n".join(out)


def generated(text: str) -> bool:
    return "GENERATED" in text[:400]


def main(argv: list[str]) -> int:
    finds = []
    for p in sorted(REPO.rglob("*")):
        if not p.is_file() or p.suffix not in (".py", ".scad"):
            continue
        rel = p.relative_to(REPO).as_posix()
        if any(s in "/" + rel for s in SKIP) or rel in OWNER:
            continue
        text = p.read_text(errors="ignore")
        if generated(text):
            continue
        code = strip_comments(text, p.suffix == ".scad")
        raw = text.splitlines()
        for m in D1.finditer(code):
            ln = code[:m.start()].count("\n") + 1
            if any(tok in raw[ln - 1] for tok in LOCAL_OK):
                continue
            finds.append(("D1", rel, ln, m.group(0).strip()))
        for m in D2.finditer(code):
            finds.append(("D2", rel, code[:m.start()].count("\n") + 1, m.group(0)))
        for m in D3.finditer(code):
            finds.append(("D3", rel, code[:m.start()].count("\n") + 1, "restated BAKE_T"))
    for p in sorted((REPO / "airframe").rglob("*.stl")):
        rel = p.relative_to(REPO).as_posix()
        if any(s in "/" + rel for s in SKIP):
            continue
        with open(p, "rb") as fh:
            if R1_MARKER in fh.read(80):
                finds.append(("D4", rel, 0, "R1 frame marker"))
    scad = REPO / "airframe/openscad/hull_datums.scad"
    if not scad.exists() or scad.read_text() != hd.scad_text():
        finds.append(("D5", scad.relative_to(REPO).as_posix(), 0,
                      "stale -- run hull_datums.py --write-scad"))
    if "--summary" in argv:
        c = Counter((k, f) for k, f, _, _ in finds)
        for (k, f), n in sorted(c.items()):
            print(f"{k}  {n:4d}  {f}")
    else:
        for k, f, line, what in finds:
            print(f"{k}  {f}:{line}  {what}")
    kinds = Counter(k for k, *_ in finds)
    print(f"\nRESULT: {'PASS' if not finds else 'FAIL ' + str(dict(kinds))}")
    return 2 if finds else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
