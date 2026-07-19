#!/usr/bin/env python3
"""
engrave_plaques.py  —  engrave flat recessed name plaques into the interior
walls of the avionics / power bays.

    1) blender --background --python make_bay_text.py   (text slabs, once)
    2) python3 engrave_plaques.py [part ...]            (cargo head middle)

For each plaque a ray is cast from an interior anchor point toward the bay wall
to find the actual interior surface point S and its normal n.  A shallow flat
rectangular POCKET (depth POCKET_D) is milled into the wall at S (giving a flat,
legible reference face on the curved hull), and the letters are recessed a further
LETTER_D into that pocket floor.  Total depth (POCKET_D + LETTER_D) stays well
under the 2 mm wall so the canonical exterior skin is never perforated; the result
is verified watertight (no boundary edges) afterward.

Placements (part-local mm; see CLAUDE.md bay naming):
  cargo  : INARA  port shuttle wall,  RIVER  stbd shuttle wall
  head   : SHEPHERD forward dorsal interior
  middle : SIMON dorsal interior,     KAYLEE ventral interior (PDB + battery)

All booleans use manifold3d (guaranteed watertight).

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0  —  creativecommons.org/licenses/by/4.0
"""

import os
import sys

import numpy as np
import trimesh

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "files-hollowed-24in")
PARTS = os.path.join(OUT, "operands")
ENG = "manifold"

POCKET_D = 0.7  # mm flat pocket depth
LETTER_D = 0.6  # mm extra letter recess below the pocket floor
PLAQUE_MARGIN = 7.0  # mm border around the text inside the pocket

# part -> list of (label, anchor(inside cavity), wall_dir(anchor->wall), read_dir)
#   wall_dir  : unit vector from the anchor toward the wall to engrave.
#   read_dir  : in-plane left->right reading direction of the text.
PLAQUES = {
    "cargo_sect_shell24_2mm_repaired": [
        ("inara", (-40.0, -362.0, 103.0), (1, 0, 0), (0, -1, 0)),  # port +X wall
        ("river", (-168.0, -363.0, 102.0), (-1, 0, 0), (0, 1, 0)),  # stbd -X wall
    ],
    "head_shell24_2mm_repaired": [
        (
            "shepherd",
            (165.0, -235.0, 90.0),
            (0, 0, 1),
            (0, -1, 0),
        ),  # fwd dorsal ceiling
    ],
    "middle_shell24_2mm_repaired": [
        ("simon", (180.0, -70.0, 55.0), (0, 0, 1), (1, 0, 0)),  # dorsal ceiling
        ("kaylee", (180.0, -70.0, 18.0), (0, 0, -1), (1, 0, 0)),  # ventral floor
    ],
}


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def surface_hit(mesh, anchor, direction):
    """Return (point, inward_normal) of the first wall surface along direction."""
    locs, _, tri = mesh.ray.intersects_location([anchor], [unit(direction)])
    if len(locs) == 0:
        raise RuntimeError(f"no wall hit from {anchor} dir {direction}")
    d = np.linalg.norm(locs - np.asarray(anchor), axis=1)
    k = int(np.argmin(d))
    n = mesh.face_normals[tri[k]]
    if n @ unit(direction) > 0:  # want the normal pointing back toward the cavity
        n = -n
    return locs[k], unit(n)


def oriented_box(ex, ey, ez, centre, sx, sy, sz):
    """Axis-from-basis box of extents (sx,sy,sz) centred at `centre`."""
    box = trimesh.creation.box(extents=(sx, sy, sz))
    T = np.eye(4)
    T[:3, 0], T[:3, 1], T[:3, 2] = ex, ey, ez
    T[:3, 3] = centre
    box.apply_transform(T)
    return box


def place_text(slab, ex, ey, ez, centre):
    """Orient an origin XY text slab (normal +Z) to (ex,ey,ez) at centre."""
    s = slab.copy()
    T = np.eye(4)
    T[:3, 0], T[:3, 1], T[:3, 2] = ex, ey, ez
    T[:3, 3] = centre
    s.apply_transform(T)
    return s


def engrave(shell, label, anchor, wall_dir, read_dir):
    S, n = surface_hit(shell, anchor, wall_dir)
    ez = -n  # depth axis: into the wall (away from cavity)
    ex = unit(np.asarray(read_dir) - (np.asarray(read_dir) @ (-ez)) * (-ez))
    ey = unit(np.cross(-ez, ex))  # up, with -ez facing the viewer
    cav = -ez  # toward the cavity/viewer

    slab = trimesh.load(os.path.join(PARTS, f"text_{label}.stl"), process=True)
    tw = slab.bounds[1][0] - slab.bounds[0][0]
    th = slab.bounds[1][1] - slab.bounds[0][1]
    W, H = tw + 2 * PLAQUE_MARGIN, th + 2 * PLAQUE_MARGIN

    # Flat pocket: box from 2 mm into the cavity to POCKET_D into the wall.
    depth_p = POCKET_D + 2.0
    pcen = S + cav * (2.0 - POCKET_D) / 2.0
    pocket = oriented_box(ex, ey, ez, pcen, W, H, depth_p)

    # Letters: recess from the pocket floor a further LETTER_D into the wall.
    letters = place_text(slab, ex, ey, cav, S + cav * 2.0)
    lcut = trimesh.creation.box(extents=(W, H, POCKET_D + LETTER_D + 2.0))
    Tl = np.eye(4)
    Tl[:3, 0], Tl[:3, 1], Tl[:3, 2] = ex, ey, ez
    Tl[:3, 3] = S + cav * (2.0 - (POCKET_D + LETTER_D)) / 2.0
    # keep only the letter slab within the allowed depth band
    band = trimesh.creation.box(extents=(W, H, POCKET_D + LETTER_D + 2.0))
    band.apply_transform(Tl)
    letters = trimesh.boolean.intersection([letters, band], engine=ENG)

    shell = trimesh.boolean.difference([shell, pocket], engine=ENG)
    shell = trimesh.boolean.difference([shell, letters], engine=ENG)
    print(f"  {label}: S={S.round(1).tolist()} plaque {W:.0f}x{H:.0f} mm engraved")
    return shell


def drop_islands(mesh, min_faces=100):
    comps = mesh.split(only_watertight=False)
    keep = [c for c in comps if len(c.faces) >= min_faces]
    return trimesh.util.concatenate(keep) if keep else mesh


def main():
    sel = sys.argv[1:] or ["cargo", "head", "middle"]
    name = {
        "cargo": "cargo_sect_shell24_2mm_repaired",
        "head": "head_shell24_2mm_repaired",
        "middle": "middle_shell24_2mm_repaired",
    }
    for s in sel:
        part = name[s]
        path = os.path.join(OUT, part + ".stl")
        shell = trimesh.load(path, process=True)
        print(f"{part}:")
        for label, anchor, wd, rd in PLAQUES[part]:
            shell = engrave(shell, label, anchor, wd, rd)
        shell = drop_islands(shell)
        shell.export(path)
        print(
            f"  -> {path}  watertight={shell.is_watertight} facets={len(shell.faces)}"
        )


if __name__ == "__main__":
    main()
