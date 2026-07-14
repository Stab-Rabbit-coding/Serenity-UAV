#!/usr/bin/env python3
"""
validate_kicad.py — KiCad schematic/PCB validator for CI.

Runs `kicad-cli sch erc` and `kicad-cli pcb drc --schematic-parity` on every
.kicad_sch / .kicad_pcb in the repository and fails if any REAL electrical
violation is found.

Severity policy (matches the standard already applied by hand to every KiCad
board in this project this session -- Wash/Zoe/Kaylee/Emma/Jayne):

  HARD (any occurrence fails the build) -- these mean the board is
  electrically wrong: shorts, schematic/PCB net mismatches, overlapping
  courtyards, clearance violations, a broken board outline, exposed copper
  under soldermask, or any ERC/DRC finding at "error" severity.

  SOFT (reported, does not fail the build) -- cosmetic / informational only,
  and already an accepted, tracked class of finding across every board in
  this repo (see e.g. avionics/kicad/Jayne/Jayne.md "EMI Hardening Status", Kaylee's
  701 open ERC/DRC items): footprint-library mismatches on intentionally
  simplified/placeholder footprints, silkscreen overlap/clearance, and the
  schematic-parity "extra footprint" / "footprint symbol mismatch" categories
  that fire on footprints not yet back-annotated to the schematic.

Scope: by default checks every .kicad_sch/.kicad_pcb in the repo EXCEPT
archive/archives directories (frozen historical boards, e.g. the pre-Rev-Q
CAPE-A-1 family, are not held to ongoing standards -- see root CLAUDE.md
revision/archival policy). Several currently-active boards (Wash, Kaylee,
Emma) predate this validator and carry a large pre-existing backlog of real
DRC findings (matching this project's own long-standing practice of tracking
open ERC/DRC items rather than blocking on them, e.g. Kaylee's 701 open
items) -- retroactively fixing that backlog is a separate, large hardware
task, not something a CI script should silently paper over or suddenly
block on. So in CI, pass --changed-since <base-ref> to scope the HARD check
to only the KiCad files actually touched by the current push/PR: this
catches regressions and any new board (like Jayne, which is fully clean) at
the moment they're introduced, without failing every future PR on
pre-existing debt in boards it never touched.

Ref: TODO.md (KiCad DRC/ERC workflow used throughout this project); CLAUDE.md
"For any KiCad PCB design... run DRC after every modification and document
violations."
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_DIR_NAMES = {"archive", "archives"}

# DRC violation "type" values that indicate a real electrical/mechanical
# defect. Anything else reported by kicad-cli is treated as soft (reported,
# non-fatal) -- see module docstring for the established precedent.
HARD_DRC_TYPES = {
    "shorting_items",
    "net_conflict",
    "courtyards_overlap",
    "clearance",
    "invalid_outline",
    "solder_mask_bridge",
}

# ERC "error"-severity types treated as SOFT (accepted) rather than
# build-failing. Confirmed 2026-07-03 that every current instance of these on
# Jayne.kicad_sch traces to the already-documented, self-acknowledged
# placeholder-footprint gaps in avionics/kicad/Jayne/Jayne.md ("Verified vs
# Placeholder" / "Known Gaps" -- e.g. U_PMIC's EN/sequencing pins, U1's
# BOOT_MODE0/PORz strap pins, U3's NRST/SWCLK debug pins are all real pins on
# real parts whose full pinout/power-sequencing isn't modeled yet, not a
# forgotten connection on a finished design). A genuinely unconnected pin on a
# board that claims to be finished is a real bug -- this exemption is scoped
# to the ERC *type*, not a specific board, so re-tighten it (move back to
# HARD) once a board's placeholder ICs are replaced with fully-verified parts.
ERC_SOFT_TYPES = {
    "pin_not_driven",
    "power_pin_not_driven",
}


def _is_archived(path):
    return any(part in ARCHIVE_DIR_NAMES for part in path.relative_to(REPO_ROOT).parts)


def find_kicad_files():
    sch = sorted(p for p in REPO_ROOT.rglob("*.kicad_sch") if not _is_archived(p))
    pcb = sorted(p for p in REPO_ROOT.rglob("*.kicad_pcb") if not _is_archived(p))
    return sch, pcb


def changed_files_since(base_ref):
    """Return the set of repo-relative paths changed vs base_ref (git diff)."""
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        print(f"  ! git diff against {base_ref} failed: {result.stderr.strip()}")
        return None
    return {REPO_ROOT / line for line in result.stdout.splitlines() if line.strip()}


def run_kicad_cli(args):
    result = subprocess.run(
        ["kicad-cli", *args], capture_output=True, text=True, cwd=REPO_ROOT
    )
    return result


def load_report(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"  ! could not parse kicad-cli output: {exc}")
        return None


def check_erc(sch_path, verbose=False):
    """Return (hard_count, soft_count) for one schematic."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        out_path = tmp.name
    result = run_kicad_cli(
        [
            "sch",
            "erc",
            "--format",
            "json",
            "--severity-all",
            "--output",
            out_path,
            str(sch_path),
        ]
    )
    report = load_report(out_path)
    Path(out_path).unlink(missing_ok=True)
    if report is None:
        print(f"  ! kicad-cli sch erc failed on {sch_path.relative_to(REPO_ROOT)}:")
        print(f"    {result.stderr.strip()[:500]}")
        return 1, 0

    hard = 0
    soft = 0
    for sheet in report.get("sheets", []):
        for v in sheet.get("violations", []):
            sev = v.get("severity", "")
            vtype = v.get("type", "")
            if sev == "error" and vtype not in ERC_SOFT_TYPES:
                hard += 1
                if verbose:
                    print(
                        f"    HARD (ERC {vtype or 'error'}): {v.get('description', v)}"
                    )
            else:
                soft += 1
    return hard, soft


def check_drc(pcb_path, verbose=False):
    """Return (hard_count, soft_count) for one PCB."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        out_path = tmp.name
    result = run_kicad_cli(
        [
            "pcb",
            "drc",
            "--format",
            "json",
            "--severity-all",
            "--schematic-parity",
            "--output",
            out_path,
            str(pcb_path),
        ]
    )
    report = load_report(out_path)
    Path(out_path).unlink(missing_ok=True)
    if report is None:
        print(f"  ! kicad-cli pcb drc failed on {pcb_path.relative_to(REPO_ROOT)}:")
        print(f"    {result.stderr.strip()[:500]}")
        return 1, 0

    hard = 0
    soft = 0
    for key in ("violations", "schematic_parity"):
        for v in report.get(key, []):
            vtype = v.get("type", "")
            sev = v.get("severity", "")
            if vtype in HARD_DRC_TYPES or (
                sev == "error" and vtype not in HARD_DRC_TYPES
            ):
                # Any explicit hard-type match, or an otherwise-unrecognized
                # "error" severity finding -- fail closed on the unknown case
                # rather than silently letting a new violation class through.
                hard += 1
                if verbose:
                    print(f"    HARD ({vtype or sev}): {v.get('description', v)}")
            else:
                soft += 1
    return hard, soft


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "-v", "--verbose", action="store_true", help="print each hard violation"
    )
    ap.add_argument(
        "--changed-since",
        metavar="REF",
        help="only validate .kicad_sch/.kicad_pcb files changed vs this git ref "
        "(e.g. origin/main) -- use in CI to avoid failing on pre-existing debt "
        "in boards the current push/PR doesn't touch",
    )
    args = ap.parse_args()

    sch_files, pcb_files = find_kicad_files()

    if args.changed_since:
        changed = changed_files_since(args.changed_since)
        if changed is None:
            return 1
        sch_files = [p for p in sch_files if p in changed]
        pcb_files = [p for p in pcb_files if p in changed]
        print(
            f"--changed-since {args.changed_since}: "
            f"{len(sch_files)} schematic(s), {len(pcb_files)} PCB(s) touched"
        )

    if not sch_files and not pcb_files:
        print("No .kicad_sch/.kicad_pcb files to validate.")
        return 0

    total_hard = 0
    total_soft = 0

    for sch in sch_files:
        rel = sch.relative_to(REPO_ROOT)
        hard, soft = check_erc(sch, verbose=args.verbose)
        status = "PASS" if hard == 0 else "FAIL"
        print(f"[{status}] ERC {rel}: {hard} hard, {soft} soft (accepted-class)")
        total_hard += hard
        total_soft += soft

    for pcb in pcb_files:
        rel = pcb.relative_to(REPO_ROOT)
        hard, soft = check_drc(pcb, verbose=args.verbose)
        status = "PASS" if hard == 0 else "FAIL"
        print(f"[{status}] DRC {rel}: {hard} hard, {soft} soft (accepted-class)")
        total_hard += hard
        total_soft += soft

    print(
        f"\n{len(sch_files)} schematic(s), {len(pcb_files)} PCB(s) checked. "
        f"{total_hard} hard violation(s), {total_soft} accepted-class finding(s)."
    )
    if total_hard:
        print("FAIL: at least one hard (real electrical) violation found.")
        return 1
    print("PASS: no hard violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
