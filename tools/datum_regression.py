#!/usr/bin/env python3
"""Datum-migration regression harness (plan 2026-10-19-001, rule R3).

snapshot DIR   run every frame-aware tool under tools/ (no arguments, or the
               arguments in ARGS below) and store each stdout+stderr in DIR.
compare A B    compare two snapshots line by line.  A number may change only by
               a datum offset (+-169.850, +-305.704, +-80.000, within 0.01 mm);
               every other changed number is reported.  A tool that ran in A
               but fails in B is reported.

Run:
    /usr/bin/python3 tools/datum_regression.py snapshot OUT_DIR [TOOL ...]
    /usr/bin/python3 tools/datum_regression.py compare BEFORE AFTER

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, 2026-10-19, per AGENTS.md AI attribution.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OFFSETS = (169.850, 305.704, 80.000)
TOL = 0.011
NUM = re.compile(r"[-+]?\d+\.\d+|[-+]?\d+")
# Tools that need arguments to do anything useful.
ARGS = {
    "landing_gear_wing_clearance.py": ["--proud"],
}
SKIP = {"datum_regression.py", "frame_inventory.py", "shift_baked_stl.py", "hull_datums.py",
        "check_datum_drift.py", "bake_hull_frame.py", "export_assembly_meshes.py",
        "airframe_interface_census.py", "placement_audit.py", "bom_edit_weight_pass_13lbm.py"}
TIMEOUT = 900


def frame_tools() -> list[str]:
    inv = re.compile(r"hull[- ]frame|\bX_CL\b|HULL-FRAME|bake_hull_frame|hull_datums", re.I)
    out = []
    for p in sorted((REPO / "tools").glob("*.py")):
        if p.name in SKIP or p.name.startswith("test_"):
            continue
        if inv.search(p.read_text(errors="ignore")):
            out.append(p.name)
    return out


def snapshot(out: Path, tools: list[str]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    status = {}
    for t in tools:
        cmd = ["/usr/bin/python3", f"tools/{t}", *ARGS.get(t, [])]
        try:
            r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=TIMEOUT)
            text, code = r.stdout + "\n--- stderr ---\n" + r.stderr, r.returncode
        except subprocess.TimeoutExpired:
            text, code = "TIMEOUT", -1
        (out / f"{t}.txt").write_text(text)
        status[t] = code
        print(f"{code:4d}  {t}", flush=True)
    (out / "status.json").write_text(json.dumps(status, indent=1))


def is_offset(d: float) -> bool:
    return abs(d) < TOL or any(abs(abs(d) - o) < TOL for o in OFFSETS)


def compare(a: Path, b: Path) -> int:
    sa = json.loads((a / "status.json").read_text())
    sb = json.loads((b / "status.json").read_text())
    bad = 0
    for t, code in sa.items():
        if t not in sb:
            continue
        if code == 0 and sb[t] != 0:
            print(f"REGRESSED  {t}: exit {code} -> {sb[t]}")
            bad += 1
        la = (a / f"{t}.txt").read_text().split("--- stderr ---")[0].splitlines()
        lb = (b / f"{t}.txt").read_text().split("--- stderr ---")[0].splitlines()
        if len(la) != len(lb):
            print(f"LINES      {t}: {len(la)} -> {len(lb)} lines (review by hand)")
            bad += 1
            continue
        for i, (x, y) in enumerate(zip(la, lb)):
            nx, ny = NUM.findall(x), NUM.findall(y)
            if len(nx) != len(ny):
                print(f"SHAPE      {t}:{i + 1}: {x.strip()[:70]} | {y.strip()[:70]}")
                bad += 1
                continue
            for u, v in zip(nx, ny):
                if not is_offset(float(v) - float(u)):
                    print(f"CHANGED    {t}:{i + 1}: {u} -> {v}   [{y.strip()[:80]}]")
                    bad += 1
                    break
    print(f"\nRESULT: {'PASS' if not bad else f'{bad} finding(s)'}")
    return 0 if not bad else 2


def main(argv: list[str]) -> int:
    if argv[:1] == ["snapshot"]:
        snapshot(Path(argv[1]), argv[2:] or frame_tools())
        return 0
    if argv[:1] == ["compare"]:
        return compare(Path(argv[1]), Path(argv[2]))
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
