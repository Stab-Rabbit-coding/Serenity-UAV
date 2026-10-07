#!/usr/bin/env python3
"""check_tacco_envelope_sync.py — keep every airframe TACCO mount in step with the board size.

TACCO (the comms-node cape) flies at four stations, each with its own envelope
written in a different file:

* nose (CN1)        — Faraday tray, ``head_shell24.scad`` / ``build_head_shell.py``
* cargo chin (CN2/3) — pouches on the chin shelf, ``cargo_layout_fit.py`` (NODE_L)
                       -> ``cargo_layout_t5_params.scad`` -> ``chin_node_shelf.scad``
* middle ring (CN4) — Simon saddle slot, ``middle_layout_fit.py``
                       -> ``middle_layout_t6_params.scad`` -> ``simon_node_saddle.scad``

The board size itself lives in ``avionics/kicad/TACCO/scripts/gen_tacco_pcb.py``
(``BW, BH``).  When the board was grown to 60 x 35 mm (2026-10-06, reverted 2026-10-07)
every one of those files had to move together, and the printable STLs built from them had
to be re-exported.  This check makes that coupling mechanical:

1. **Dimension sync (error).**  Every envelope is re-derived from ``BW``/``BH`` with
   the allowances below and compared with the value written in its file.
2. **STL freshness (warning; error with --strict).**  Each printable STL must be
   unchanged since the STL's own last commit (content, not commit time: a source
   restored to the exact text the STL was built from is not stale);
   otherwise its re-export is still pending.

Stdlib only (runs in CI and the pre-commit hook without the mesh toolchain).

Usage:
    python3 tools/check_tacco_envelope_sync.py            # dims must match; stale STLs warn
    python3 tools/check_tacco_envelope_sync.py --strict   # stale or missing STLs also fail

Author: Claude (Anthropic) under S. Griffing's direction, 2026-10-06.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Allowances, mm (CARGO_SECTION_LAYOUT.md §3a; head_shell24.scad Faraday comments).
POUCH_L = 3.0      # foil pouch on the board's length (55 -> 58, 60 -> 63)
POUCH_H = 2.0      # foil pouch on the board's width (35 -> 37)
TRAY_X = 5.0       # nose tray: 2 x 1.5 mm wall + 2 mm clearance (60 -> 65)
PANEL_CLR = 2.0    # nose access panel: tray + 1 mm each side

GEN = "avionics/kicad/TACCO/scripts/gen_tacco_pcb.py"
CARGO_FIT = "tools/cargo_layout_fit.py"
CARGO_PARAMS = "airframe/openscad/fuselage/cargo/cargo_layout_t5_params.scad"
MIDDLE_FIT = "tools/middle_layout_fit.py"
MIDDLE_PARAMS = "airframe/openscad/fuselage/middle_layout_t6_params.scad"
HEAD_SCAD = "airframe/openscad/fuselage/head_shell24.scad"
HEAD_PY = "tools/build_head_shell.py"

# printable STL -> the sources it is built from
STLS = {
    "airframe/stls/fuselage/cargo/chin_node_shelf.stl": [
        "airframe/openscad/fuselage/cargo/chin_node_shelf.scad", CARGO_PARAMS],
    "airframe/stls/fuselage/cargo/void_former_cargo_node_bay.stl": [
        "tools/gen_cargo_void_formers.py", CARGO_FIT],
    "airframe/stls/fuselage/simon_node_saddle.stl": [
        "airframe/openscad/fuselage/simon_node_saddle.scad", MIDDLE_PARAMS],
    "airframe/stls/fuselage/head_shell24.stl": [HEAD_SCAD, HEAD_PY],
}


def num(path: str, pattern: str) -> float:
    text = (REPO / path).read_text(encoding="utf-8")
    m = re.search(pattern, text, re.MULTILINE)
    if not m:
        raise SystemExit(f"check_tacco_envelope_sync: pattern {pattern!r} not found in {path}")
    return float(m.group(1))


def last_commit(path: str) -> str:
    """Hash of the last commit that touched path ('' if never committed)."""
    return subprocess.run(["git", "-C", str(REPO), "log", "-1", "--format=%H", "--", path],
                          capture_output=True, text=True, check=False).stdout.strip()


def changed_since(rev: str, paths: list) -> list:
    """Sources whose working-tree content differs from their content at rev."""
    out = subprocess.run(["git", "-C", str(REPO), "diff", "--name-only", rev, "--", *paths],
                         capture_output=True, text=True, check=False).stdout.split()
    return [p for p in paths if p in out]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--strict", action="store_true", help="stale or missing STLs fail too")
    a = ap.parse_args()

    bw = num(GEN, r"^BW, BH = ([\d.]+), [\d.]+")
    bh = num(GEN, r"^BW, BH = [\d.]+, ([\d.]+)")
    flt = r"\s*=\s*(-?[\d.]+)"
    panel = bw + TRAY_X + PANEL_CLR
    simon_w = num(MIDDLE_PARAMS, r"SIMON_X1" + flt) - num(MIDDLE_PARAMS, r"SIMON_X0" + flt)
    checks = [
        ("cargo NODE_L (fit tool)", num(CARGO_FIT, r"^NODE_L, NODE_H, NODE_T = ([\d.]+)"),
         bw + POUCH_L),
        ("cargo NODE_L (SCAD params)", num(CARGO_PARAMS, r"^NODE_L" + flt), bw + POUCH_L),
        ("cargo chin pouch length Y1-Y0", num(CARGO_PARAMS, r"^N_CHIN_Y1" + flt)
         - num(CARGO_PARAMS, r"^N_CHIN_Y0" + flt), bw + POUCH_L),
        ("cargo NODE_H (pouch width)", num(CARGO_PARAMS, r"^NODE_H" + flt), bh + POUCH_H),
        ("Simon CN4 slot width", simon_w, bw + POUCH_L),
        ("nose CAPE_PCB_X (SCAD)", num(HEAD_SCAD, r"^CAPE_PCB_X" + flt), bw),
        ("nose CAPE_PCB_X (builder)", num(HEAD_PY, r"^CAPE_PCB_X" + flt), bw),
        ("nose FARADAY_ENC_X (SCAD)", num(HEAD_SCAD, r"^FARADAY_ENC_X" + flt), bw + TRAY_X),
        ("nose FARADAY_ENC_X (builder)", num(HEAD_PY, r"^FARADAY_ENC_X" + flt), bw + TRAY_X),
        ("nose BOOK_PANEL_X (SCAD)", num(HEAD_SCAD, r"^BOOK_PANEL_X" + flt), panel),
        ("nose BOOK_PANEL_X (builder)", num(HEAD_PY, r"^BOOK_PANEL_X" + flt), panel),
    ]
    print(f"TACCO board {bw:g} x {bh:g} mm ({GEN})")
    bad = 0
    for name, got, want in checks:
        ok = abs(got - want) < 0.01
        bad += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name:34s} {got:7.2f}  (expected {want:.2f})")

    stale = 0
    print("Printable STLs vs their sources (source content at the STL's last commit):")
    for stl, srcs in STLS.items():
        rev = last_commit(stl) if (REPO / stl).exists() else ""
        if not rev:
            stale += 1
            print(f"  PENDING {stl}: not exported yet")
            continue
        moved = changed_since(rev, srcs)
        if moved:
            stale += 1
            print(f"  PENDING {stl}: {', '.join(moved)} changed since it was exported — re-export")
        else:
            print(f"  ok      {stl}")

    if bad:
        print(f"RESULT: FAIL — {bad} envelope(s) out of step with the TACCO board size")
        return 1
    if stale:
        verdict = "FAIL" if a.strict else "PASS with warnings"
        print(f"RESULT: {verdict} — {stale} STL re-export(s) pending")
        return 1 if a.strict else 0
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
