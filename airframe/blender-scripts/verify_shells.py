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
  * 0 non-manifold edges (edges used by more than 2 faces),
  * winding consistent,
  * watertight (mesh.is_watertight, hard requirement),
  * 0 small junk fragments (< JUNK_FACE_LIMIT faces) — voxel-remesh /
    boolean-pipeline noise, not real geometry.

  Body count is NOT capped: a properly hollowed 2 mm shell legitimately splits
  into 2 large components (an outer surface with positive signed volume and a
  separate, fully disconnected inner surface with negative signed volume — they
  never share an edge), and the rear section legitimately has additional large
  lobes (skid-arm / dorsal-pod cavity surfaces).  Confirmed empirically
  2026-06-16: middle's two large bodies have signed volumes +1,287,847 mm^3 and
  -1,055,410 mm^3, summing to 232,437 mm^3 — the exact mass-budget figure in
  docs/structural_analysis.md.  A real defect shows up as non-manifold/open
  edges or small (< 64-face) sliver fragments, not as "more than one body".

  MESH-01 fix (2026-06-16): the previous gate allowed up to 3 large (>= 64 face)
  detached components and never required mesh.is_watertight or checked for
  non-manifold edges, so it reported "PASS" on add_structural_features.py output
  that was not watertight (cargo, middle, rear) and, for rear, had genuinely
  fragmented into 3 disconnected solid islands plus hundreds of slivers.  An
  initial over-correction (requiring exactly 1 body) was tried and reverted
  after it incorrectly failed the legitimate outer+inner double-wall topology
  on every section.  See TODO.md MESH-01.

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


def nonmanifold_edge_count(mesh):
    """Edges referenced by more than two faces (non-manifold)."""
    edge_counts = np.bincount(
        mesh.edges_unique_inverse,
        minlength=len(mesh.edges_unique),
    )
    return int(np.sum(edge_counts > 2))


def check(path):
    """
    Return (passed, summary_string) for one shell STL.

    Pass criterion is real manufacturing watertightness: 0 open boundary edges,
    0 non-manifold edges, 0 small junk fragments (< JUNK_FACE_LIMIT faces),
    winding consistent, and mesh.is_watertight true.  Body count is informational
    only — see the module docstring for why a clean shell legitimately splits
    into 2+ large bodies (outer/inner double-wall, plus extra lobes on rear).
    """
    mesh = trimesh.load(path, process=True)

    open_edges = boundary_edge_count(mesh)
    nonmanifold_edges = nonmanifold_edge_count(mesh)
    comps = mesh.split(only_watertight=False)
    fragments = [c for c in comps if len(c.faces) < JUNK_FACE_LIMIT]
    big_extra = [c for c in comps if len(c.faces) >= JUNK_FACE_LIMIT]
    # zero-area degenerate faces (float32 slivers) — cosmetic
    degen = int((mesh.area_faces < 1e-9).sum())

    real_breach = (open_edges > 0 or nonmanifold_edges > 0 or len(fragments) > 0
                   or not mesh.is_winding_consistent or not mesh.is_watertight)
    passed = not real_breach

    status = "PASS" if passed else "FAIL"
    summary = (
        f"[{status}] {os.path.basename(path)}\n"
        f"        facets={len(mesh.faces):>7d}  winding_ok={mesh.is_winding_consistent}"
        f"  watertight={mesh.is_watertight}\n"
        f"        open_boundary_edges={open_edges}  nonmanifold_edges={nonmanifold_edges}"
        f"  large_bodies={len(big_extra)} (informational; see docstring)"
        f"  junk_fragments={len(fragments)} (real defect if > 0)"
        f"  degenerate_faces={degen} (cosmetic)"
        f"  vol={mesh.volume:.0f} mm^3"
    )
    if len(big_extra) > 1:
        sizes = sorted((len(c.faces) for c in big_extra), reverse=True)[:12]
        summary += f"\n        large body face counts: {sizes}"
    if fragments:
        sizes = sorted((len(c.faces) for c in fragments), reverse=True)[:12]
        summary += f"\n        JUNK FRAGMENTS (real defect) face counts: {sizes}"
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
