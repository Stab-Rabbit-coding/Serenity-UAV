#!/usr/bin/env python3
"""Translate hull-frame (R1) STLs into the aircraft datum (R2), in place.

Datum migration plan 2026-10-19-001, unit U4.  R2 = R1 + hull_datums.R1_TO_R2
(a pure translation).  Reads binary or ASCII STL, adds the offset to every
vertex in float64, writes binary STL with the header marker
"SerenityUAV AIRCRAFT-FRAME R2 <name>", and verifies the result: same
triangle count, same volume (to 1e-3 relative), same watertightness and the
same body count -- otherwise the original is kept.

A file already stamped R2 is refused (never translate twice).

Run: /usr/bin/python3 tools/migrate_stl_r2.py PATH [PATH ...]

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, 2026-10-19, per AGENTS.md AI attribution.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import os
import sys
import tempfile

import numpy as np
import trimesh

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hull_datums as hd  # noqa: E402

R2_MARKER = b"SerenityUAV AIRCRAFT-FRAME R2"


def migrate(path: str) -> bool:
    with open(path, "rb") as fh:
        head = fh.read(80)
    if R2_MARKER in head:
        print(f"[r2] SKIP {path}: already R2")
        return True
    # Weld FIRST (process=True merges coincident vertices in float64), then
    # translate the unique vertex array.  Translating the raw per-face corners
    # moved near-coincident float32 pairs onto a different rounding grid, so
    # some no longer welded on reload (watertight -> open; the MESH-01 class).
    # Distinct vertices closer than float32 resolution at the larger R2
    # coordinates (~3e-5 mm at Y 500) collapse on export; the shells carry 33+
    # such pairs (closest 3.8e-6 mm, MESH-01 boolean slivers).  Weld them at
    # 1e-4 mm (0.1 um -- far below print resolution) BEFORE translating.
    before = trimesh.load(path, force="mesh", process=True)
    before.merge_vertices(digits_vertex=4)
    before.update_faces(before.nondegenerate_faces())
    before.remove_unreferenced_vertices()
    m = before.copy()
    m.vertices = m.vertices + np.asarray(hd.R1_TO_R2, dtype=float)
    name = os.path.splitext(os.path.basename(path))[0][:40]
    header = (R2_MARKER + b" " + name.encode()).ljust(80, b" ")[:80]
    data = trimesh.exchange.stl.export_stl(m)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".stl")
    with os.fdopen(fd, "wb") as fh:
        fh.write(header + data[80:])
    after = trimesh.load(tmp, force="mesh")
    pb = trimesh.load(path, force="mesh")
    ok = (len(after.faces) == len(before.faces)
          and abs(after.volume - pb.volume) <= 1e-3 * max(abs(pb.volume), 1.0)
          and after.is_watertight == pb.is_watertight
          and len(after.split(only_watertight=False)) == len(pb.split(only_watertight=False)))
    if not ok:
        os.unlink(tmp)
        print(f"[r2] FAIL {path}: verification failed -- original kept")
        return False
    os.replace(tmp, path)
    b = after.bounds
    print(f"[r2] ok   {path}: X {b[0][0]:.1f}..{b[1][0]:.1f} Y {b[0][1]:.1f}..{b[1][1]:.1f} "
          f"Z {b[0][2]:.1f}..{b[1][2]:.1f}  vol {after.volume:.0f}")
    return True


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    return 0 if all([migrate(p) for p in argv]) else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
