#!/usr/bin/env python3
"""Export a STEP model of every KiCad board for the build-guide renders.

Plan docs/plans/2026-11-02-001-feat-build-guide-joint-torque-and-sequence-plan.md, unit U12
(requirement R8, KTD6): the cards and renders show the real PCBs, not placeholder boxes.  The
board models come from KiCad itself (``kicad-cli pcb export step``), so they carry the true
outline, hole pattern and every component's 3D model.

For each ``avionics/kicad/<Board>/kicads/<name>.kicad_pcb`` this writes
``avionics/kicad/<Board>/step/<name>.step`` and records, in
``avionics/kicad/step_export_report.json``, the status, size, time and any footprint whose 3D
model KiCad could not find (those parts appear as bare pads in the render).

Guards:
  * the board file's ``generator_version`` shall not be newer than kicad-cli (a newer file is
    refused with a clear message, as a silent bad export is worse than none);
  * a failed or empty export is reported and makes the exit status non-zero.

Usage::

    /usr/bin/python3 tools/export_pcb_step.py                 # every board
    /usr/bin/python3 tools/export_pcb_step.py Pilot TACCO     # selected board directories
    /usr/bin/python3 tools/export_pcb_step.py --list

The STEP files are generated artifacts; regenerate after a board change.  Placement of each
board in the aircraft (cape stack, standoffs, saddle) is separate and owned by the assembly
export -- see the plan, U12.

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (requirement and direction).
Written by Claude Sonnet 5.5 (Anthropic) under the author's direction, 2026-11-02,
per AGENTS.md section 3 AI attribution.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KICAD_DIR = ROOT / "avionics" / "kicad"
REPORT = KICAD_DIR / "step_export_report.json"
MISSING_MODEL = re.compile(r"(could not add 3d model|cannot add 3d model|can't find.*model|"
                           r"3d model.*not found|file not found)", re.I)


def parse_version(text: str) -> tuple[int, int]:
    """'9.0.2' or '9.0' -> (9, 0); raises ValueError when unparseable."""
    m = re.search(r"(\d+)\.(\d+)", text)
    if not m:
        raise ValueError(f"cannot parse a version from {text!r}")
    return int(m.group(1)), int(m.group(2))


def board_generator_version(pcb: Path) -> tuple[int, int]:
    m = re.search(r'\(generator_version\s+"?([\d.]+)"?\)', pcb.read_text(errors="replace")[:4000])
    return parse_version(m.group(1)) if m else (0, 0)


def cli_version() -> tuple[int, int]:
    out = subprocess.run(["kicad-cli", "version"], capture_output=True, text=True, check=True).stdout
    return parse_version(out)


def boards(only: list[str] | None = None) -> list[Path]:
    found = sorted(KICAD_DIR.glob("*/kicads/*.kicad_pcb"))
    if only:
        found = [p for p in found if p.parent.parent.name in only]
    return found


def check_version(pcb: Path, cli: tuple[int, int]) -> str | None:
    """Error text when the board file is newer than kicad-cli, else None."""
    gen = board_generator_version(pcb)
    if gen > cli:
        return (f"{pcb.name} was saved by KiCad {gen[0]}.{gen[1]} but kicad-cli is {cli[0]}.{cli[1]}; "
                "use a kicad-cli at least as new as the file")
    return None


def export(pcb: Path, cli: tuple[int, int]) -> dict:
    out_dir = pcb.parent.parent / "step"
    out = out_dir / (pcb.stem + ".step")
    rec: dict = {"board": pcb.parent.parent.name, "pcb": str(pcb.relative_to(ROOT)),
                 "step": str(out.relative_to(ROOT)), "status": "ok", "missing_models": []}
    err = check_version(pcb, cli)
    if err:
        rec.update(status="refused", error=err)
        return rec
    out_dir.mkdir(exist_ok=True)
    t0 = time.time()
    proc = subprocess.run(
        ["kicad-cli", "pcb", "export", "step", "--force", "--subst-models", "--no-dnp",
         "--output", str(out), str(pcb)], capture_output=True, text=True, timeout=600)
    rec["seconds"] = round(time.time() - t0, 1)
    log = proc.stdout + proc.stderr
    rec["missing_models"] = sorted({ln.strip() for ln in log.splitlines() if MISSING_MODEL.search(ln)})
    if proc.returncode != 0 or not out.exists() or out.stat().st_size == 0:
        rec.update(status="failed", error=(log.strip().splitlines() or ["no output"])[-1])
    else:
        rec["bytes"] = out.stat().st_size
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("boards", nargs="*", help="board directory names under avionics/kicad (default: all)")
    ap.add_argument("--list", action="store_true", help="list boards and exit")
    args = ap.parse_args()
    found = boards(args.boards or None)
    if args.list:
        for p in found:
            print(p.relative_to(ROOT))
        return 0
    if shutil.which("kicad-cli") is None:
        print("export_pcb_step: kicad-cli not found on PATH", file=sys.stderr)
        return 2
    cli = cli_version()
    results = []
    for p in found:
        r = export(p, cli)
        results.append(r)
        extra = f", {len(r['missing_models'])} missing 3D models" if r["missing_models"] else ""
        print(f"{r['status']:8s} {r['board']:16s} {r.get('bytes', 0) / 1e6:6.1f} MB  {r.get('seconds', 0):5.1f} s{extra}"
              + (f"  [{r.get('error')}]" if r["status"] != "ok" else ""))
    REPORT.write_text(json.dumps({"kicad_cli": f"{cli[0]}.{cli[1]}", "boards": results}, indent=2) + "\n")
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
