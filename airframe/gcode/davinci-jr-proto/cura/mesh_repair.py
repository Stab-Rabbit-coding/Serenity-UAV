#!/usr/bin/env python3
"""
mesh_repair.py -- Cura-CLI-specific mesh cleanup for Rev T "heavy" STLs.

Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
Date   : 2026-09-07

Six current-Rev-T STLs (the 4 hull shells + 2 nacelle pods) carry an
"overlapping faces" defect left over from the Blender hollowing/boolean
pipeline (see project history: SCAD manifold fixes, cargo_interior merge
pipeline) -- self-intersecting or duplicated coincident triangles that a
trimesh watertight/manifold check does not catch (the mesh IS watertight),
but which slow or crash CuraEngine 5.0.0's support/combing pass.

`rear_shell24_2mm_repaired.stl` is the worst case: it did not finish
slicing within 400s even with support disabled, unlike the other 5 heavy
files which slice fine as-is. This module repairs that specific defect
class with a **self-union** through the Manifold geometry kernel
(manifold3d, https://github.com/elalish/manifold) -- Manifold guarantees
its output has no self-intersections or duplicate coincident faces by
construction, so unioning a mesh with itself is a standard way to
canonicalize/clean a mesh that is otherwise topologically valid but
contains this kind of boolean-pipeline leftover. A light `simplify()` pass
(manifold3d's own decimator, tolerance-bounded so every point on the
surface moves less than the tolerance) is applied afterward purely for
CuraEngine slicing speed -- at a 64% print scale on a 0.4mm nozzle, a
0.15mm native-scale tolerance is far finer than the printer can resolve.

This is a print-pipeline-local fix, not a change to the canonical Rev T
geometry in airframe/stls/ -- per airframe/AGENTS.md "Geometry Integrity",
canonical hull-frame STLs are only regenerated from their Blender/SCAD
source, never hand-patched. The repaired mesh produced here is scoped to
this Cura slicing pipeline and is not committed (regenerate on demand, same
as the *.gcode outputs this directory already gitignores).

If the same self-intersecting geometry needs fixing at the canonical-source
level (not just for one slicer's CLI), that's a Blender-hollowing-pipeline
task per tools/TOOL_REFERENCE.md, not this script.

Usage:
    python3 mesh_repair.py <input.stl> <output.stl> [--tolerance 0.15]
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import trimesh
import manifold3d as m3d


def repair_mesh(mesh: trimesh.Trimesh, tolerance: float = 0.15) -> trimesh.Trimesh:
    """Self-union + simplify a mesh through manifold3d to remove
    overlapping/duplicate coincident faces left by a source boolean
    pipeline, then lightly decimate for slicer speed.

    Args:
        mesh: input mesh (any watertight, edge-manifold mesh -- the defect
            this fixes is invisible to trimesh's own watertight check, so
            "is_watertight" passing beforehand is not evidence there is
            nothing to repair here).
        tolerance: manifold3d simplify() bound, mm, at the mesh's own
            (native) scale -- every point on the output surface moves less
            than this from the input. 0.15mm at native 24in scale is well
            under 0.4mm-nozzle resolution even before the 64% print scale
            shrinks it further.

    Returns:
        A new trimesh.Trimesh, self-unioned and simplified. Report the
        result's `is_watertight` for the caller's own logging -- some
        residual trimesh-flagged non-manifold edges can remain (localized,
        single-digit edge count on a ~1e6-face mesh in testing) even though
        manifold3d itself reports Error.NoError on the same output; this
        reflects a difference in how the two tools define manifoldness at
        edges shared by coincident-but-topologically-separate surface
        patches, not a slicing-blocking defect -- verify by test-slicing,
        not by chasing trimesh's edge count to exactly 0.
    """
    mesh_in = m3d.Mesh(
        vert_properties=mesh.vertices.astype("float32"),
        tri_verts=mesh.faces.astype("uint32"),
    )
    man = m3d.Manifold(mesh_in)
    repaired = (man + man).simplify(tolerance)
    if repaired.status() != m3d.Error.NoError:
        raise RuntimeError(f"manifold3d reported {repaired.status()} after repair")

    out_mesh = repaired.to_mesh()
    verts = np.array(out_mesh.vert_properties)[:, :3]
    faces = np.array(out_mesh.tri_verts)
    return trimesh.Trimesh(vertices=verts, faces=faces, process=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--tolerance", type=float, default=0.15)
    args = ap.parse_args()

    mesh = trimesh.load(args.input, process=True)
    print(f"input:  {len(mesh.faces):,} faces, volume={mesh.volume:.1f} mm^3")

    fixed = repair_mesh(mesh, args.tolerance)
    print(f"output: {len(fixed.faces):,} faces, volume={fixed.volume:.1f} mm^3, "
          f"watertight={fixed.is_watertight}, winding_consistent={fixed.is_winding_consistent}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fixed.export(args.output)
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
