#!/usr/bin/env python3
"""
engrave_shuttles.py  —  engrave the INARA / RIVER avionics-bay marks into the
interior walls of the cargo shuttle cavities.

    1) blender --background --python make_shuttle_text.py   (text cutter slabs)
    2) python3 engrave_shuttles.py                          (this script)

The recess is bounded so it cannot perforate the canonical 2 mm exterior skin:
the text cutter is intersected with a thin (LAYER_MM) wall layer immediately
adjacent to the cavity (the void dilated outward by LAYER_MM, intersected with
the shell), so the engraving depth is at most LAYER_MM and conforms to the
curved interior wall.  All booleans use manifold3d (guaranteed watertight).

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0  —  creativecommons.org/licenses/by/4.0
"""

import os

import numpy as np
import trimesh
from scipy import ndimage
from skimage import measure

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "files-hollowed-24in")
PARTS = os.path.join(OUT, "operands")
ENG = "manifold"
LAYER_MM = 1.0        # max engrave depth (must stay < 2 mm wall)
PITCH = 1.0


def load(p):
    return trimesh.load(p, process=True)


def dilate_void(void, layer_mm, pitch):
    """Return the void grown outward by layer_mm (morphological dilation)."""
    vg = void.voxelized(pitch=pitch).fill()
    grid = np.asarray(vg.matrix, bool)
    origin = vg.transform[:3, 3]
    pad = int(round(layer_mm / pitch)) + 2
    grid = np.pad(grid, pad, mode="constant", constant_values=False)
    origin = origin - pad * pitch
    r = max(1, int(round(layer_mm / pitch)))
    grid = ndimage.binary_dilation(grid, iterations=r)
    verts, faces, _, _ = measure.marching_cubes(grid.astype(np.float32), 0.5)
    verts = verts * pitch + origin
    m = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    m.fix_normals()
    return m


def main():
    shell = load(os.path.join(OUT, "cargo_sect_shell24_2mm_repaired.stl"))
    opened = load(os.path.join(PARTS, "cargo_inner_opened.stl"))
    orig = load(os.path.join(PARTS, "cargo_sect_shell24_2mm_repaired__inner.stl"))

    void = trimesh.boolean.intersection([opened, orig], engine=ENG)
    void_dil = dilate_void(void, LAYER_MM, PITCH)
    layer = trimesh.boolean.intersection([shell, void_dil], engine=ENG)
    print(f"cavity-adjacent layer: facets={len(layer.faces)} vol={layer.volume:.0f}")

    for stem in ("inara", "river"):
        text = load(os.path.join(PARTS, f"text_{stem}.stl"))
        cut = trimesh.boolean.intersection([text, layer], engine=ENG)
        print(f"  {stem}: recess facets={len(cut.faces)} vol={cut.volume:.0f}")
        shell = trimesh.boolean.difference([shell, cut], engine=ENG)

    # Drop tiny sliver islands the recess booleans can shed.
    comps = shell.split(only_watertight=False)
    keep = [c for c in comps if len(c.faces) >= 100]
    if keep:
        shell = trimesh.util.concatenate(keep)

    out = os.path.join(OUT, "cargo_sect_shell24_2mm_repaired.stl")
    shell.export(out)
    print(f"engraved cargo: facets={len(shell.faces)} "
          f"watertight={shell.is_watertight} vol={shell.volume:.0f} -> {out}")


if __name__ == "__main__":
    main()
