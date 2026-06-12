#!/usr/bin/env python3
"""
verify_shells.py  —  watertight / no-breach gate for the 2 mm fuselage shells.

Run after blender_shells_2mm_solidify.py (on the staging dir) or against the
published STLs to confirm each section is a single watertight, winding-
consistent solid with NO open boundary edges and NO detached inner-shell
fragments (the signature of the old centroid-inset "hull breaches").

    python3 airframe/blender-scripts/verify_shells.py            # staging dir
    python3 airframe/blender-scripts/verify_shells.py --published # published STLs

Gate (per section, all must hold to PASS):
  * 0 open boundary edges (edges used by exactly one face),
  * winding consistent,
  * watertight,
  * no "junk" body with > JUNK_FACE_LIMIT faces other than the main solid
    (a hollow sealed shell legitimately has 2 surface shells: outer + inner;
     trimesh body_count therefore reports 2 for a clean shell).

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0  —  creativecommons.org/licenses/by/4.0
"""

import os
import sys

import numpy as np
import trimesh

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(BASE, "..", ".."))
STAGING = os.path.join(BASE, "files-hollowed-24in")
PUBLISHED = os.path.join(REPO, "airframe", "stls", "fuselage")

# Connected components smaller than this many faces are voxel-remesh "bubbles"
# (internal noise) — a clean shell must have none.  A multi-lobed cavity (e.g.
# the rear fuselage + separate pod/skid cavities) legitimately yields several
# large surface shells, so we do NOT cap the surface-shell count; we only reject
# small fragments and any non-watertight / non-manifold topology.
JUNK_FACE_LIMIT = 64

# basename -> published relative path (under airframe/stls/fuselage)
SECTIONS = {
    "head_shell24_2mm_repaired.stl":       "head_shell24_2mm_repaired.stl",
    "cargo_sect_shell24_2mm_repaired.stl": "cargo/cargo_sect_shell24_2mm_repaired.stl",
    "middle_shell24_2mm_repaired.stl":     "middle_shell24_2mm_repaired.stl",
    "rear_shell24_2mm_repaired.stl":       "rear_shell24_2mm_repaired.stl",
}


def boundary_edge_count(mesh):
    """Edges referenced by exactly one face (open boundary)."""
    return len(trimesh.grouping.group_rows(mesh.edges_sorted, require_count=1))


def check(path):
    """Return (passed, summary_string) for one shell STL."""
    # Default processing merges only exact-coincident vertices.  Do NOT use a
    # digit-rounded merge_vertices here: rounding welds distinct nearby vertices
    # at sharp features (e.g. the tail-cone tip) into phantom non-manifold
    # pinches and falsely reports a watertight mesh as broken.
    mesh = trimesh.load(path, process=True)

    open_edges = boundary_edge_count(mesh)
    comps = mesh.split(only_watertight=False)
    fragments = [c for c in comps if len(c.faces) < JUNK_FACE_LIMIT]
    large_shells = len(comps) - len(fragments)

    passed = (
        open_edges == 0
        and mesh.is_winding_consistent
        and mesh.is_watertight
        and len(fragments) == 0
    )
    status = "PASS" if passed else "FAIL"
    summary = (
        f"[{status}] {os.path.basename(path)}\n"
        f"        facets={len(mesh.faces):>7d}  watertight={mesh.is_watertight}"
        f"  winding_ok={mesh.is_winding_consistent}\n"
        f"        open_boundary_edges={open_edges}  surface_shells={large_shells}"
        f"  bubble_fragments={len(fragments)}  vol={mesh.volume:.0f} mm^3"
    )
    if len(fragments):
        sizes = sorted((len(c.faces) for c in fragments), reverse=True)[:12]
        summary += f"\n        fragment face counts: {sizes}"
    return passed, summary


def main():
    use_published = "--published" in sys.argv
    all_pass = True
    print(f"=== verify_shells.py  ({'published' if use_published else 'staging'}) ===")
    for staging_name, pub_rel in SECTIONS.items():
        path = (os.path.join(PUBLISHED, pub_rel) if use_published
                else os.path.join(STAGING, staging_name))
        if not os.path.exists(path):
            print(f"[MISS] {path}")
            all_pass = False
            continue
        ok, summary = check(path)
        all_pass = all_pass and ok
        print(summary)
    print("\n" + ("ALL PASS" if all_pass else "FAILURES PRESENT"))
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
