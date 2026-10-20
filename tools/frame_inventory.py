#!/usr/bin/env python3
"""Inventory every airframe file that carries hull-frame coordinates (datum migration U2).

Lists, for plan docs/plans/2026-10-19-001-aircraft-datum-migration-plan.md:

* STLs: R1-marker STLs, R2-marker STLs, STLs the master assembly places with
  identity (i.e. already in the hull frame), and unmarked STLs whose bounding
  box lies inside the aircraft envelope away from their own origin (likely
  hull-frame, needs a human look) -- versus part-local prints.
* Code: Python / SCAD / FreeCAD files that mention the hull frame, X_CL,
  the bake table or the datum module.

Run: /usr/bin/python3 tools/frame_inventory.py [--json OUT]

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, 2026-10-19, per AGENTS.md AI attribution.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import json
import re
import struct
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
R1 = b"SerenityUAV HULL-FRAME R1"
R2 = b"SerenityUAV AIRCRAFT-FRAME R2"
# R1 aircraft envelope (mm): nacelle tips, nose to tail, ground to fin.
ENV_R1 = np.array([[-460.0, -320.0, -95.0], [130.0, 400.0, 220.0]])
CODE_RE = re.compile(r"hull[- ]frame|\bX_CL\b|HULL-FRAME|bake_hull_frame|hull_datums", re.I)
SKIP_DIRS = ("archive", "archives", "node_modules", ".git", "gcs/", "docs/references")


def stl_bounds(p: Path) -> np.ndarray | None:
    raw = p.read_bytes()
    if raw[:5] == b"solid" and b"facet" in raw[:400]:
        pts = re.findall(rb"vertex\s+(\S+)\s+(\S+)\s+(\S+)", raw)
        if not pts:
            return None
        v = np.array(pts, dtype=float)
    else:
        n = struct.unpack("<I", raw[80:84])[0]
        rec = np.frombuffer(raw[84:84 + 50 * n], dtype=np.dtype(
            [("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
        v = rec["v"].reshape(-1, 3).astype(float)
    return np.array([v.min(0), v.max(0)])


def assembly_identity_stls() -> set[str]:
    src = (REPO / "airframe/FreeCAD-scripts/serenity_assembly.py").read_text()
    return {m.group(1) for m in re.finditer(r'_stl\(f?"([^"]+\.stl)"\)', src)}


def main(argv: list[str]) -> int:
    asm = assembly_identity_stls()
    stls = {"r1_marker": [], "r2_marker": [], "assembly_placed": [], "envelope_candidate": [],
            "part_local": []}
    for p in sorted((REPO / "airframe").rglob("*.stl")):
        rel = p.relative_to(REPO).as_posix()
        if any(s in rel for s in SKIP_DIRS):
            continue
        head = p.read_bytes()[:80]
        if R1 in head:
            stls["r1_marker"].append(rel)
            continue
        if R2 in head:
            stls["r2_marker"].append(rel)
            continue
        if rel.replace("airframe/stls/", "") in asm:
            stls["assembly_placed"].append(rel)
            continue
        b = stl_bounds(p)
        if b is None:
            continue
        c = b.mean(0)
        inside = np.all(b[0] >= ENV_R1[0]) and np.all(b[1] <= ENV_R1[1])
        (stls["envelope_candidate"] if inside and np.linalg.norm(c) > 60.0
         else stls["part_local"]).append(rel)
    code = []
    for p in sorted(REPO.rglob("*")):
        if p.suffix not in (".py", ".scad", ".FCMacro") or not p.is_file():
            continue
        rel = p.relative_to(REPO).as_posix()
        if any(s in rel for s in SKIP_DIRS):
            continue
        if CODE_RE.search(p.read_text(errors="ignore")):
            code.append(rel)
    out = {"stls": stls, "code": code}
    for k, v in stls.items():
        print(f"STL {k:20s} {len(v):4d}")
    print(f"code files               {len(code):4d}")
    if "--json" in argv:
        Path(argv[argv.index("--json") + 1]).write_text(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
