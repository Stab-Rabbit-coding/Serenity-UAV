#!/usr/bin/env python3
"""
merge_head_sensor_bay.py -- Rev H2 (2026-10-27), aircraft datum R2

Cut the twin-pod nose sensor bay (airframe/openscad/fuselage/bow_sensor_pod.scad,
owner-approved 2026-10-27) into the PUBLISHED head shell and write the bonded
bay insert as its own installed-position STL.

Single source: the bay cutter and insert solids come from
tools/head_layout_fit.py (bay_cutter(), bay_insert()), the same functions the
head context gate checks, and the SCAD reads the same generated parameters.

Idempotent: an already-cut head (cutter overlap < 1 mm^3) is detected and
left unchanged -- re-subtracting coplanar faces would only make slivers.
The published head is not reproducible from its upstream pipeline (R2
handoff 2026-10-20), so head features are applied as subtractive merges on
the published mesh, as merge_head_interior.py did.

Run:
    /usr/bin/python3 airframe/blender-scripts/merge_head_sensor_bay.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the
author's direction, 2026-10-27, per `AGENTS.md` §3 AI attribution.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""

import os
import sys

import numpy as np
import trimesh

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
sys.path.insert(0, SCRIPT_DIR)
import hull_datums as hd  # noqa: E402
import head_layout_fit as h  # noqa: E402
from merge_head_interior import keep_largest_body, nondegenerate_faces, stamp_export  # noqa: E402
from cargo_layout_fit import to_man  # noqa: E402

HEAD_PATH = os.environ.get("HEAD_MERGE_OUT") or h.HEAD
INSERT_PATH = os.path.join(REPO_ROOT, "airframe", "stls", "fuselage", "head",
                           "bow_sensor_bay_insert.stl")
RHO_PRINT = 1.05e-3  # g/mm^3, same convention as merge_head_interior.py


def from_man(m):
    mm = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts))


def main():
    # default processing welds the float32 STL's coincident vertices; loading
    # with process=False leaves seams that read as open after the boolean
    shell = trimesh.load(h.HEAD)
    v0 = shell.volume
    overlap = (to_man(shell) ^ to_man(h.bay_cutter())).volume()
    if overlap < 1.0:
        # already cut: re-subtracting coplanar faces only manufactures slivers
        print(f"head: bay already cut (cutter overlap {overlap:.2f} mm^3) -- unchanged")
    else:
        _cut_and_write(shell, v0)
    _write_insert()


def _cut_and_write(shell, v0):
    out = from_man(to_man(shell) - to_man(h.bay_cutter()))
    out = nondegenerate_faces(out)
    out.remove_unreferenced_vertices()
    out, dropped = keep_largest_body(out)
    removed = v0 - out.volume
    print(f"head: {v0:.0f} -> {out.volume:.0f} mm^3 (removed {removed:.0f} mm^3, "
          f"~{removed * RHO_PRINT:.1f} g); watertight {out.is_watertight}; "
          f"dropped {dropped} fragment(s)")
    if not out.is_watertight:
        sys.exit("head not watertight after the bay cut -- not written")
    stamp_export(out, HEAD_PATH)


def _write_insert():
    ins = h.bay_insert()
    os.makedirs(os.path.dirname(INSERT_PATH), exist_ok=True)
    stamp_export(ins, INSERT_PATH)
    with open(INSERT_PATH, "r+b") as f:  # label the insert, not "Head_Shell"
        f.write((hd.FRAME_MARKER + b" Bow_Sensor_Bay_Insert").ljust(80, b" ")[:80])
    print(f"insert: {ins.volume:.0f} mm^3, ~{ins.volume * RHO_PRINT:.1f} g, watertight "
          f"{ins.is_watertight}; marker {hd.FRAME_MARKER.decode()}")


if __name__ == "__main__":
    main()
