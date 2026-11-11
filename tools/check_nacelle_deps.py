#!/usr/bin/env python3
"""check_nacelle_deps.py -- every dependency of the 64 mm nacelle exists and is live.

The 64 mm nacelle is the Rev U nacelle.  This gate walks the OpenSCAD sources that build it
and fails if anything they need is missing, archived, or reaches back into a 50 mm design:

  1. SCAD closure: every `include <f>` / `use <f>` resolves to an existing file under
     airframe/openscad, and no file in the closure is a 50 mm design file.
  2. Imports: every literal `import("...")` resolves to an existing file outside archives/.
     The canonical Firefly engine shells `eng_{left,right}_shell24_50mm_repaired.stl` are
     allowed: they are the canon reference mesh the 64 mm pod is scaled from (REF-CAD-001),
     not a 50 mm design.
  3. Required published parts: each printed part the 64 mm roll-up (nacelle_mass_cg_64.py)
     counts has an STL on disk (see REQUIRED_PARTS).  Missing ones are listed, not hidden.

Usage:  python3 tools/check_nacelle_deps.py [--strict-parts]
Exit 0 = SCAD closure and imports clean (and, with --strict-parts, every required part is
published); 1 = a dependency is missing, archived, or 50 mm.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic) under the author's direction, 2026-11-07.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAD = ROOT / "airframe" / "openscad"
NAC = SCAD / "nacelles"
STLS = ROOT / "airframe" / "stls"

#: Sources that build the 64 mm nacelle (the roots of the closure).
ROOTS = [
    "nacelle_pod_64mm_tandem", "nacelle_nozzle_iris_64mm", "nacelle_nozzle_servo_64mm",
    "edf_motor_mount_64mm", "nacelle_trunnion_64mm", "nacelle_tip_gear_variants",
    "nacelle_tilt_joint_context", "nacelle_esc_cover", "nacelle_dorsal_shroud_64_gen",
    "nacelle_nozzle_servo_options_context", "nacelle_64_scale",
    "nozzle_servo_linkage_64_params", "nacelle_cowl_fair_table",
]
#: A file whose name matches is a 50 mm design file and must not be reachable.
FIFTY_MM = re.compile(r"(50mm|_revs\b|nozzle_iris\.scad|nacelle_trunnion\.scad|"
                      r"edf_stator_sleeve|edf_aft_spider_sleeve)")
#: Canon reference meshes (not 50 mm designs) that the 64 mm pod legitimately imports.
CANON_OK = {"eng_left_shell24_50mm_repaired.stl", "eng_right_shell24_50mm_repaired.stl"}

#: Printed parts the 64 mm roll-up counts (nacelle_mass_cg_64.py rows_64 / ON_AXIS_64),
#: relative to airframe/stls.  Path -> what it is.
REQUIRED_PARTS = {
    "nacelles/nacelle_port_64mm.stl": "pod shell, port (stage 1 integral)",
    "nacelles/nacelle_stbd_64mm.stl": "pod shell, starboard (stage 1 integral)",
    "nacelles/edf_motor_mount_64mm_stage2_port.stl": "stage-2 cartridge, port",
    "nacelles/edf_motor_mount_64mm_stage2_stbd.stl": "stage-2 cartridge, starboard",
    "nacelles/nacelle_trunnion_64mm_port.stl": "tilt trunnion, port",
    "nacelles/nacelle_trunnion_64mm_stbd.stl": "tilt trunnion, starboard",
    "nacelles/nozzles/nacelle_nozzle_throat_64mm_port.stl": "nozzle throat + housing, port",
    "nacelles/nozzles/nacelle_nozzle_throat_64mm_stbd.stl": "nozzle throat + housing, starboard",
    "nacelles/nozzles/nacelle_nozzle_ring_64mm_port.stl": "unison ring, port",
    "nacelles/nozzles/nacelle_nozzle_ring_64mm_stbd.stl": "unison ring, starboard",
    "nacelles/nozzles/nacelle_nozzle_flap_64mm.stl": "nozzle flap (master)",
    "nacelles/nozzles/nacelle_nozzle_flap_seal_64mm.stl": "nozzle flap (seal)",
    "nacelles/esc/nacelle_esc_cover_64mm_port_a.stl": "ESC bay cover, port A",
    "nacelles/esc/nacelle_esc_cover_64mm_port_b.stl": "ESC bay cover, port B",
    "nacelles/esc/nacelle_esc_cover_64mm_stbd_a.stl": "ESC bay cover, starboard A",
    "nacelles/esc/nacelle_esc_cover_64mm_stbd_b.stl": "ESC bay cover, starboard B",
}

INC = re.compile(r"^\s*(?:include|use)\s*<([^>]+)>", re.M)
IMP = re.compile(r'import\s*\(\s*(?:file\s*=\s*)?"([^"]+)"')


def strip_comments(s: str) -> str:
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"//[^\n]*", "", s)


def closure() -> tuple[dict[Path, str], list[str]]:
    """SCAD files reachable from ROOTS, and problems found while walking."""
    seen: dict[Path, str] = {}
    problems: list[str] = []

    def walk(p: Path, via: str) -> None:
        p = p.resolve()
        if p in seen:
            return
        seen[p] = via
        if not p.exists():
            problems.append(f"MISSING  {p.relative_to(ROOT)} (from {via})")
            return
        if FIFTY_MM.search(p.name):
            problems.append(f"50 MM    {p.relative_to(ROOT)} reachable from {via}")
        text = strip_comments(p.read_text(encoding="utf-8"))
        for m in INC.finditer(text):
            walk(p.parent / m.group(1), p.name)
        for m in IMP.finditer(text):
            q = (p.parent / m.group(1)).resolve()
            if not q.exists():
                problems.append(f"MISSING  import {m.group(1)} in {p.name}")
            elif "archives" in q.parts:
                problems.append(f"ARCHIVED import {m.group(1)} in {p.name}")
            elif FIFTY_MM.search(q.name) and q.name not in CANON_OK:
                problems.append(f"50 MM    import {q.name} in {p.name}")

    for r in ROOTS:
        walk(NAC / f"{r}.scad", "ROOTS")
    return seen, problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--strict-parts", action="store_true",
                    help="also fail when a required printed part has no published STL")
    args = ap.parse_args(argv)
    seen, problems = closure()
    print(f"check_nacelle_deps: {len(seen)} SCAD files in the 64 mm closure")
    for p in problems:
        print("  " + p)
    missing = [(rel, what) for rel, what in REQUIRED_PARTS.items()
               if not (STLS / rel).exists()]
    for rel, what in missing:
        print(f"  NOT PUBLISHED  {rel}  ({what})")
    bad = bool(problems) or (args.strict_parts and bool(missing))
    if bad:
        print("check_nacelle_deps: FAIL")
        return 1
    print("check_nacelle_deps: PASS" + (f" ({len(missing)} required parts not yet published)"
                                        if missing else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
