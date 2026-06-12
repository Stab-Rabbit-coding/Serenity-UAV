#!/usr/bin/env python3
"""
morph_open_voxel.py  —  voxel-SDF morphological opening of a shell inner operand.

    python3 morph_open_voxel.py <inner_stl> <out_stl> <radius_mm> [pitch_mm]

Removes every protrusion thinner than ~2*radius from the inner (subtracted) solid
so those thin exterior details come out SOLID in the final shell, while leaving
the large interior cavity intact.  Implemented as a true morphological opening on
a filled voxel occupancy grid:

    opened = dilate( erode( solid, ball(r) ), ball(r) )

This is stable (unlike mesh normal-offset, whose even-offset factor blows up at
sharp spikes) and anti-extensive (opened is a subset of the original), so the
downstream wall is never thinner than the nominal 2 mm — no new breaches.
The surface is recovered with marching cubes.  The interior cavity surface need
not be smooth (it is hidden and foam-filled); exterior fidelity is unaffected
because only the inner operand is changed.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0  —  creativecommons.org/licenses/by/4.0
"""

import sys

import numpy as np
import trimesh
from scipy import ndimage
from skimage import measure


def ball(r):
    """Boolean spherical structuring element of integer radius r voxels."""
    span = np.arange(-r, r + 1)
    x, y, z = np.meshgrid(span, span, span, indexing="ij")
    return (x * x + y * y + z * z) <= r * r


def main():
    in_stl, out_stl, radius = sys.argv[1], sys.argv[2], float(sys.argv[3])
    pitch = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
    rvox = max(1, int(round(radius / pitch)))

    mesh = trimesh.load(in_stl, process=True)

    # Filled occupancy grid (solid interior, not just the surface shell).
    vg = mesh.voxelized(pitch=pitch).fill()
    grid = np.asarray(vg.matrix, dtype=bool)
    origin = vg.transform[:3, 3]              # world coord of voxel (0,0,0) centre
    # Pad so dilation cannot clip at the array border.
    pad = rvox + 2
    grid = np.pad(grid, pad, mode="constant", constant_values=False)
    origin = origin - pad * pitch

    se = ball(rvox)
    opened = ndimage.binary_erosion(grid, structure=se, border_value=0)
    opened = ndimage.binary_dilation(opened, structure=se, border_value=0)

    # Marching cubes -> surface; verts are in voxel index space -> world.
    verts, faces, _, _ = measure.marching_cubes(
        opened.astype(np.float32), level=0.5)
    verts = verts * pitch + origin
    out = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    out.fix_normals()                          # outward winding (positive volume)
    out.export(out_stl)
    print(f"opened r={radius} pitch={pitch} rvox={rvox}: "
          f"faces={len(out.faces)} vol={out.volume:.0f} "
          f"(orig vol={mesh.volume:.0f}) -> {out_stl}")


if __name__ == "__main__":
    main()
