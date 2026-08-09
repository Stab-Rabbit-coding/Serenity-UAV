#!/usr/bin/env python3
"""Verify the Rev R6 bay cowl clears the leg through its full flexion sweep.

The canonical retraction-bay cowl (LG-19) is a rim standing proud of the bay
plate so the leg reads as emerging from a recessed flank bay.  The rim sits
directly in the thigh's swing path, so "it looks fine" is not good enough --
the first closed-rectangle rim rendered convincingly and still fouled the thigh
by 188 mm^3 at rest.  This tool settles it by boolean intersection.

Method
------
For each flexion angle, render `intersection(bay_cowl(), rotate(leg_frame()))`
and measure the result:

  * OpenSCAD prints "Current top level object is empty" and writes NO output
    file when the intersection is void -- that is the CLEAR case.
  * Any written STL is real interference; its volume is reported.

Treating a missing file as clear is only safe because the empty-object message
is checked too: a render that failed for any other reason also produces no
file, and would otherwise pass silently.

Exit status is non-zero if any angle interferes, so this can gate a commit.

Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note : Authored by Claude (model: Claude Opus 5, Anthropic) under the
          author's direction, 2026-08-09, per AGENTS.md AI attribution.
License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>

Run: python3 tools/landing_gear_cowl_clearance.py [--variant 1_5in|3_0in]
"""

import argparse
import os
import subprocess
import sys
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
SCAD_DIR = os.path.join(REPO_ROOT, "airframe", "openscad", "fuselage")

# Sample the full hip rotation; FLEX_DEG = 30.9 at full ductile stroke.
FLEX_ANGLES = (0.0, 8.0, 16.0, 24.0, 30.9)
EMPTY_MARKER = "Current top level object is empty"
TIMEOUT_S = 400


def check_angle(scad_path, flex, workdir):
    """Return (interference_mm3, note) for one flexion angle."""
    src = os.path.join(workdir, f"c{flex}.scad")
    out = os.path.join(workdir, f"c{flex}.stl")
    with open(src, "w") as fh:
        fh.write(f"use <{scad_path}>\n")
        fh.write(f"intersection() {{ bay_cowl(); "
                 f"rotate([0, -{flex}, 0]) leg_frame(); }}\n")

    proc = subprocess.run(
        ["openscad", "-o", out, src],
        capture_output=True, text=True, timeout=TIMEOUT_S,
    )
    log = proc.stdout + proc.stderr
    empty = EMPTY_MARKER in log

    if not os.path.exists(out):
        if empty:
            return 0.0, "clear (empty intersection)"
        return None, f"NO OUTPUT and no empty-marker (exit {proc.returncode})"

    try:
        import trimesh
        mesh = trimesh.load(out)
        return abs(mesh.volume), f"{len(mesh.faces)} faces"
    except ImportError:
        return float("nan"), "trimesh unavailable; STL written => interference"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="1_5in", choices=("1_5in", "3_0in"))
    args = ap.parse_args()

    scad = os.path.join(SCAD_DIR, f"canonical_leg_r6_{args.variant}.scad")
    if not os.path.exists(scad):
        sys.exit(f"missing SCAD source: {scad}")

    print(f"cowl clearance -- canonical_leg_r6_{args.variant}.scad")
    print(f"  {'flex (deg)':>11}  {'interference':>14}  note")

    worst, failures = 0.0, []
    with tempfile.TemporaryDirectory(prefix="lg_cowl_") as workdir:
        for flex in FLEX_ANGLES:
            vol, note = check_angle(scad, flex, workdir)
            if vol is None:
                failures.append(f"flex={flex}: {note}")
                print(f"  {flex:11.1f}  {'ERROR':>14}  {note}")
                continue
            worst = max(worst, vol)
            print(f"  {flex:11.1f}  {vol:11.3f} mm^3  {note}")

    print()
    if failures:
        for f in failures:
            print(f"  RENDER FAILURE: {f}")
        sys.exit(2)
    if worst > 1e-6:
        print(f"  FOULS -- worst interference {worst:.3f} mm^3")
        sys.exit(1)
    print("  CLEAR -- no interference at any sampled angle")


if __name__ == "__main__":
    main()
