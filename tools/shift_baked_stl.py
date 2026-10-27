#!/usr/bin/env python3
"""Translate an already hull-frame-baked binary STL along hull X, in place.

Used when a bake placement in tools/bake_hull_frame.py COMPONENTS is corrected
for a part whose published STL cannot be re-baked from source (the bake
refuses to double-transform) -- the 2026-10-19 symmetry correction about
hull_datums.X_CL.  The 80-byte header (with its "SerenityUAV HULL-FRAME R1"
marker) and the triangle order are kept; every vertex gets the SAME float
offset, so vertices that were coincident stay coincident (the float32
re-weld trap of MESH-01 does not arise).

Run: /usr/bin/python3 tools/shift_baked_stl.py DX PATH [PATH ...]

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

import sys as _sys  # noqa: E402
import os as _os  # noqa: E402
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import hull_datums as hd  # noqa: E402
MARKER = hd.FRAME_MARKER  # single source (aircraft datum R2, 2026-10-19)
REC = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])


def _mesh(path: str) -> trimesh.Trimesh:
    """Load a file that must be one Trimesh; raise on a Scene or Path."""
    geom = trimesh.load(path, force="mesh")
    if not isinstance(geom, trimesh.Trimesh):
        raise TypeError(f"{path}: not a single mesh")
    return geom


def shift(path: str, dx: float) -> None:
    raw = open(path, "rb").read()
    header = raw[:80]
    if MARKER not in header:
        sys.exit(f"[shift] {path}: not a hull-frame baked STL (no marker) -- refusing")
    n = int(np.frombuffer(raw[80:84], "<u4")[0])
    recs = np.frombuffer(raw[84:84 + n * 50], REC).copy()
    if len(recs) != n:
        sys.exit(f"[shift] {path}: truncated ({len(recs)} of {n} triangles)")
    recs["v"][:, :, 0] += np.float32(dx)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".stl")
    with os.fdopen(fd, "wb") as fh:
        fh.write(header)
        fh.write(np.uint32(n).tobytes())
        fh.write(recs.tobytes())
    was = _mesh(path).is_watertight
    m = _mesh(tmp)
    if was and not m.is_watertight:            # refuse only if the shift made it worse
        os.unlink(tmp)
        sys.exit(f"[shift] {path}: result not watertight -- original kept")
    if not was:
        print(f"[shift] NOTE {os.path.relpath(path)} was already not watertight (unchanged)")
    os.replace(tmp, path)
    print(f"[shift] {os.path.relpath(path)}: dX {dx:+.4f} mm, X now "
          f"{m.bounds[0][0]:.3f}..{m.bounds[1][0]:.3f}, watertight")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    dx = float(argv[0])
    for p in argv[1:]:
        shift(p, dx)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
