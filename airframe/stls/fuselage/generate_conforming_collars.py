#!/usr/bin/env python3
# ============================================================================
# HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11). See CLAUDE.md.
#   Hull frame: X=+port, Y=+aft, Z=+dorsal; origin = SerenityAssembly world.
#   These parts are generated DIRECTLY in hull frame (identity placement).
#
#   generate_conforming_collars.py  (Rev R2, 2026-07-06)
#   --------------------------------------------------------------------------
#   Internal bonded splice collars for the three fuselage section joints:
#     head/cargo (Y≈-71), cargo/middle (Y≈+130), middle/rear (Y≈+203).
#
#   Supersedes the three single-cross-section generators
#   (generate_head_cargo_splice_collar.py etc.), which extruded ONE inner
#   contour straight across the joint.  That produced a constant-section prism
#   that was WIDER than the shells' tapering/rounded joint ends, so the collar
#   passed through solid plastic (collar∩shell ≈ 1600-2000 mm³ per side —
#   verified 2026-07-06).
#
#   This generator instead builds each collar as a LOFTED, CONFORMING sleeve:
#   it samples the ACTUAL inner-cavity cross-section of whichever section exists
#   at each Y station across the joint span, insets it by the bond gap, and
#   lofts consecutive stations via their pairwise INTERSECTION (so every slab is
#   ≤ both neighbouring contours — guaranteeing the collar fits inside the
#   non-uniform, tapering interior of BOTH sections with a bond gap everywhere).
#   Result: collar∩shell ≈ 0.  The small inter-section gap left by the flat
#   mating-face cut (add_structural_features.MATING_PLANES: ~1.7-2.0 mm) is the
#   slip-fit / bond line the collar bridges, filled with West System 105/206 +
#   406 thickened epoxy — a shear-loaded double-lap doubler (see the retired
#   generators' docstrings for the load rationale, unchanged).
#
#   Requires the sections to have been regenerated with FLAT OPEN mating faces
#   first (merge_cargo_interior.py, add_structural_features.py [head/middle],
#   regen_rear_interior.py), so the collar has open bores to slip into.
#
# Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  (design)
# AI-assist: Claude Opus 4.8 (Anthropic) — conforming-loft generator, 2026-07-06
# License: CC BY 4.0 - creativecommons.org/licenses/by/4.0
# Print spec: CF-PETG, 0.15 mm layer, 4 perimeters, 100% infill; bond West 105/206.
# ============================================================================
"""Generate the three CONFORMING splice collars (hull frame)."""

import os

import numpy as np
import trimesh
from manifold3d import Manifold, Mesh
from shapely.geometry import Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
CAVITY_FLOOR = 5.0  # mm^2 — ignore section loops smaller than this (noise)
BOND_GAP = 0.6  # mm — collar outer inset from the section inner wall
WALL_T = 2.0  # mm — collar radial wall
INSERT = 8.0  # mm — collar insertion depth into EACH section
SAMPLES = 41  # stations sampled across the collar span
SIMPLIFY = 0.4  # mm — contour simplification tolerance
JUNK_FACES = 64

# joint: (name, fwd_stl, aft_stl, fwd_face_Y, aft_face_Y, out_stl)
#   fwd section occupies Y <= fwd_face_Y ; aft section occupies Y >= aft_face_Y.
JOINTS = [
    (
        "head/cargo",
        "head_shell24_2mm_repaired.stl",
        "cargo/cargo_sect_shell24_2mm_repaired.stl",
        -71.2,
        -69.5,
        "head_cargo_splice_collar.stl",
    ),
    (
        "cargo/middle",
        "cargo/cargo_sect_shell24_2mm_repaired.stl",
        "middle_shell24_2mm_repaired.stl",
        129.0,
        131.0,
        "cargo_middle_splice_collar.stl",
    ),
    (
        "middle/rear",
        "middle_shell24_2mm_repaired.stl",
        "rear_shell24_2mm_repaired.stl",
        202.3,
        204.3,
        "middle_rear_splice_collar.stl",
    ),
]


def to_man(tm):
    return Manifold(
        Mesh(
            vert_properties=tm.vertices.astype(np.float32),
            tri_verts=tm.faces.astype(np.uint32),
        )
    )


def from_man(m):
    mm = m.to_mesh()
    out = trimesh.Trimesh(
        vertices=np.asarray(mm.vert_properties)[:, :3].astype(np.float64),
        faces=np.asarray(mm.tri_verts),
        process=False,
    )
    out.merge_vertices()
    return out


def inner_cavity(mesh, y):
    """The section's largest inner-cavity polygon (2nd-largest loop) at Y, or None."""
    s = mesh.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    if s is None:
        return None
    polys = []
    for loop in s.discrete:
        p = Polygon(np.asarray(loop)[:, [0, 2]])
        if p.is_valid and p.area > CAVITY_FLOOR:
            polys.append(p.buffer(0))
    if len(polys) < 2:
        return None
    polys.sort(key=lambda p: p.area, reverse=True)
    return polys[1].simplify(SIMPLIFY)


def _clean(p):
    if p is None or p.is_empty:
        return None
    if p.geom_type == "MultiPolygon":
        p = max(p.geoms, key=lambda g: g.area)
    return p


def _extrude(poly, y0, y1):
    ex = trimesh.creation.extrude_polygon(poly, height=y1 - y0)
    # (x, y_poly, z_extrude) -> hull (X, Y=extrude+y0, Z)
    ex.apply_transform(
        np.array([[1, 0, 0, 0], [0, 0, 1, y0], [0, 1, 0, 0], [0, 0, 0, 1.0]])
    )
    return ex


def _loft(polys, ys):
    """Union of pairwise-intersection slabs (each ≤ both neighbours)."""
    man = None
    for i in range(len(ys) - 1):
        a, b = polys[i], polys[i + 1]
        if a is None or b is None:
            continue
        seg = _clean(a.intersection(b))
        if seg is None or seg.area < 1.0:
            continue
        m = to_man(_extrude(seg, ys[i], ys[i + 1]))
        man = m if man is None else man + m
    return man


def conforming_collar(fwd, aft, fwd_face, aft_face):
    y_lo = min(fwd_face, aft_face) - INSERT
    y_hi = max(fwd_face, aft_face) + INSERT
    ys = np.linspace(y_lo, y_hi, SAMPLES)
    # inner cavity at each station: whichever section exists there
    inn = []
    for y in ys:
        p = inner_cavity(fwd, y)
        if p is None:
            p = inner_cavity(aft, y)
        inn.append(p)
    # fill gap / bad stations with the nearest valid contour
    valid = [i for i, p in enumerate(inn) if p is not None]
    if not valid:
        raise RuntimeError("no inner cavity found across the joint span")
    for i in range(len(inn)):
        if inn[i] is None:
            j = min(valid, key=lambda k: abs(k - i))
            inn[i] = inn[j]
    outer = [_clean(p.buffer(-BOND_GAP)) for p in inn]
    bore = [_clean(p.buffer(-(BOND_GAP + WALL_T))) for p in inn]
    om, bm = _loft(outer, ys), _loft(bore, ys)
    collar_man = om - bm
    # CLIP to fit inside both shells: subtract each shell's solid so any residual
    # material poking into a wall (from the "2nd-largest-loop" cavity heuristic
    # mis-reading a complex interior — e.g. the rear cone + skid lobes) is trimmed.
    # Guarantees collar∩shell = 0 by construction; the trimmed collar touches the
    # inner wall at worst (a 0-gap bond line, still fine).
    collar_man = collar_man - to_man(fwd) - to_man(aft)
    collar = from_man(collar_man)
    # drop tiny junk fragments
    comps = trimesh.graph.connected_components(
        collar.face_adjacency, nodes=np.arange(len(collar.faces))
    )
    keep = [c for c in comps if len(c) >= JUNK_FACES]
    if len(keep) < len(comps):
        collar = collar.submesh([np.concatenate(keep)], append=True)
        collar.merge_vertices()
    # close any small boundary holes the shell-clip left (keeps the print watertight)
    trimesh.repair.fill_holes(collar)
    collar.merge_vertices()
    trimesh.repair.fix_normals(collar)
    return collar


def main():
    print("=== generate_conforming_collars.py  Rev R2  2026-07-06 ===")
    for name, fwd_rel, aft_rel, fwd_face, aft_face, out_rel in JOINTS:
        fwd = trimesh.load(os.path.join(HERE, fwd_rel), process=False)
        fwd.merge_vertices()
        aft = trimesh.load(os.path.join(HERE, aft_rel), process=False)
        aft.merge_vertices()
        collar = conforming_collar(fwd, aft, fwd_face, aft_face)
        out = os.path.join(HERE, out_rel)
        collar.export(out)
        ec = np.bincount(
            collar.edges_unique_inverse,
            minlength=len(collar.edges_unique),
        )
        ihf = from_man(to_man(collar) ^ to_man(fwd)).volume
        iaf = from_man(to_man(collar) ^ to_man(aft)).volume
        b = collar.bounds
        print(f"\n[{name}] -> {out_rel}")
        print(
            f"  vol={collar.volume:.0f} mm^3  mass={collar.volume * 1.27e-3:.1f} g  "
            f"faces={len(collar.faces)}  boundary={int((ec == 1).sum())}  "
            f"nonman={int((ec > 2).sum())}"
        )
        print(
            f"  Y[{b[0][1]:.1f},{b[1][1]:.1f}]  "
            f"collar∩fwd={ihf:.0f}  collar∩aft={iaf:.0f} mm^3  "
            f"({'FITS' if max(ihf, iaf) < 50 else 'INTERFERENCE'})"
        )


if __name__ == "__main__":
    main()
