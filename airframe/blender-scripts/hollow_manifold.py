#!/usr/bin/env python3
"""
hollow_manifold.py  —  manifold3d boolean stage of the 2 mm shell pipeline.

Consumes the clean voxel-remeshed operands written by
blender_shells_2mm_solidify.py (OUT/operands/<name>__outer.stl and __inner.stl)
and produces the final watertight 2.0 mm hollow shell <name>.stl by computing
the boolean DIFFERENCE outer - inner with the manifold3d library.

manifold3d is the same Manifold geometry kernel that Blender 4.x wraps for its
EXACT solver, but the library guarantees a 2-manifold (watertight) result, where
Blender's modifier export leaves a few hundred T-junction seam edges that fail a
strict watertight check.  Doing the boolean here makes every section pass
verify_shells.py.

After the boolean, tiny enclosed islands left by the voxel remesh (sub-
ISLAND_FACE_MIN connected components — internal "bubbles") are dropped, so the
result is exactly the outer skin + inner cavity surface = one watertight solid.

Hull geometry derives from "Serenity Firefly with landing gear and swivel
engines" by misubisu (thingiverse.com/thing:7330462, CC BY 4.0).
Full attribution chain: current-specification/LICENSE_AND_ATTRIBUTION.md §2.

Run (no Blender needed; trimesh + manifold3d only):
    python3 airframe/blender-scripts/hollow_manifold.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0  —  creativecommons.org/licenses/by/4.0
"""

import os

import numpy as np
import trimesh

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "files-hollowed-24in")
PARTS = os.path.join(OUT, "operands")

# Connected components smaller than this many faces are voxel-remesh bubbles.
ISLAND_FACE_MIN = 100

SHELLS = [
    "head_shell24_2mm_repaired.stl",
    "cargo_sect_shell24_2mm_repaired.stl",
    "middle_shell24_2mm_repaired.stl",
    "rear_shell24_2mm_repaired.stl",
]


def load_clean_volume(path, min_faces):
    """
    Load an operand STL and return a single watertight volume.

    Uses default processing (merges only exact-coincident vertices — never a
    digit-rounded merge, which can weld distinct nearby vertices into
    non-manifold pinches at sharp features such as the tail-cone tip) and drops
    voxel-remesh bubble islands, leaving the one large closed solid that
    manifold3d requires as a boolean operand.
    """
    m = trimesh.load(path, process=True)
    comps = m.split(only_watertight=False)
    keep = [c for c in comps if len(c.faces) >= min_faces]
    dropped = len(comps) - len(keep)
    solid = max(keep, key=lambda c: len(c.faces)) if keep else m
    return solid, dropped


def process(name):
    """Compute outer - inner for one section and write the final shell STL."""
    outer_p = os.path.join(PARTS, name.replace(".stl", "__outer.stl"))
    inner_p = os.path.join(PARTS, name.replace(".stl", "__inner.stl"))
    out_p = os.path.join(OUT, name)
    if not (os.path.exists(outer_p) and os.path.exists(inner_p)):
        print(f"  SKIP {name}: operands missing")
        return

    outer, d_o = load_clean_volume(outer_p, ISLAND_FACE_MIN)
    inner, d_i = load_clean_volume(inner_p, ISLAND_FACE_MIN)

    # Guaranteed 2-manifold difference via manifold3d (clean volumes in -> volume out).
    shell = trimesh.boolean.difference([outer, inner], engine="manifold")

    # Drop tiny sliver components the difference can leave in thin-wall regions
    # (e.g. rear skids / pod), keeping the outer skin + all large cavity lobes.
    comps = shell.split(only_watertight=False)
    keep = [c for c in comps if len(c.faces) >= ISLAND_FACE_MIN]
    d_r = len(comps) - len(keep)
    if keep:
        shell = trimesh.util.concatenate(keep)

    shell.export(out_p)  # trimesh writes binary STL for .stl
    print(
        f"  {name}: facets={len(shell.faces):>8d}  watertight={shell.is_watertight}"
        f"  winding={shell.is_winding_consistent}  bubbles(o/i/result)={d_o}/{d_i}/{d_r}"
        f"  vol={shell.volume:.0f} mm^3  ({os.path.getsize(out_p)//1024} KB)"
    )


def main():
    print("=== hollow_manifold.py — manifold3d boolean (outer - inner) ===")
    for name in SHELLS:
        process(name)
    print("\nDone.  Run verify_shells.py, then promote to airframe/stls/fuselage/.")


if __name__ == "__main__":
    main()
