#!/usr/bin/env python3
"""merge_head_cargo_shell.py -- one-piece HEAD + CARGO hull section (deletes
the head/cargo splice collar), built from the SOURCE shell operands.

Why: the twin flat battery tray (tools/twin_head_pack_fit.py, plan 003 R10)
crosses the old head/cargo joint at Y 232-237 and clips the splice collar
ring.  The two-section SLS scheme (docs/SLS_27IN_TWO_SECTION_TRIM_STUDY.md:
head+cargo | middle+rear, one collar) already deletes that collar.  Owner
2026-10-31: "implement the merge of head and cargo sections in your battery
bay build".

Method (rebuild from the source build, not a patch on published STLs --
owner feedback "rebuild hull from source builds"):
1. The Blender pipeline (airframe/blender-scripts/blender_shells_2mm_solidify.py)
   leaves, per section, the OUTER solid O and the 2 mm eroded INNER solid I
   (files-hollowed-24in/operands/).  hollow_manifold.py makes each section as
   O - I.
2. Here both operand pairs are placed with the SAME transforms
   tools/bake_hull_frame.py uses for Head_Shell and Cargo_Shell (datum R2),
   and the joint band is built as (O_head u O_cargo) - (I_head u I_cargo):
   one continuous 2 mm skin across the seam, canonical outer mold line, no
   mating faces.
3. The published, featured sections are kept everywhere else (head bosses,
   apertures and repairs; cargo interior merge, flange bands): the merged
   part is
       head_published  n {Y <  SPLICE_Y0}
     u joint band      n {SPLICE_Y0 <= Y <= SPLICE_Y1}
     u cargo_published n {Y >  SPLICE_Y1}
   The splice planes lie where the published parts equal their raw operand
   skin (checked below: slab volume of published vs raw within VOL_TOL), so
   no feature is cut.

Output: airframe/stls/fuselage/head_cargo_shell24_2mm_merged.stl (aircraft
frame R2, header marked like bake_hull_frame).  The old
head_cargo_splice_collar.stl is RETIRED by this part (not deleted here; the
archive move rides with the layout-tool switch-over, see plan 003).

Hull geometry derives from "Serenity Firefly with landing gear and swivel
engines" by misubisu (thingiverse.com/thing:7330462, CC BY 4.0).  Full
attribution chain: current-specification/LICENSE_AND_ATTRIBUTION.md §2.

Run:
    /usr/bin/python3 tools/merge_head_cargo_shell.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the
author's direction, 2026-10-31, per `AGENTS.md` §3 AI attribution.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0
(SPDX-License-Identifier: CERN-OHL-W-2.0)
"""

import os
import sys

import manifold3d as m3d
import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import bake_hull_frame as bk  # noqa: E402
import cargo_layout_fit as clf  # noqa: E402

OPS = os.path.join(REPO, "airframe", "blender-scripts", "files-hollowed-24in", "operands")
FSTL = os.path.join(REPO, "airframe", "stls", "fuselage")
HEAD_PUB = os.path.join(FSTL, "head_shell24_2mm_repaired.stl")
CARGO_PUB = os.path.join(FSTL, "cargo", "cargo_sect_shell24_2mm_repaired.stl")
OUT = os.path.join(FSTL, "head_cargo_shell24_2mm_merged.stl")
ROOF_SLIT_BOX = (-1.5, 1.5, 98.0, 106.0, 230.0, 300.0)  # X0, X1, Y0, Y1, Z0, Z1
# Seam zone: the old collar LANDS (head Y 229-232.75 thickened inward to
# 1,925 mm2 of section vs 811 clean; cargo Y 236.2-239 fragmented, 239-241
# thickened) are obsolete with the collar gone and intrude on the twin tray.
# The zone is rebuilt as plain skin from CLEAN rings measured just outside it.
HEAD_CUT_Y, HEAD_RING_Y = 227.0, 226.0
CARGO_CUT_Y, CARGO_RING_Y = 241.5, 242.0
OVERLAP = 0.4  # each rim extrusion runs past the meet plane (fused overlap)
BIG = 1000.0


def man(tm):
    return m3d.Manifold(m3d.Mesh(vert_properties=np.asarray(tm.vertices, np.float32),
                                 tri_verts=np.asarray(tm.faces, np.uint32)))


def tm_of(m):
    mm = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts))


def placed(name, comp):
    """Operand placed by bake_hull_frame's transform for `comp`."""
    tm = trimesh.load(os.path.join(OPS, name))
    px, py, pz, qx, qy, qz, qw = bk.COMPONENTS[comp][1]
    T = np.eye(4)
    T[:3, :3] = np.asarray(bk.quat_to_matrix(qx, qy, qz, qw))[:3, :3]
    T[:3, 3] = (px, py, pz)
    tm.apply_transform(T)
    return man(tm)


def slab(y0, y1):
    return m3d.Manifold.cube((2 * BIG, y1 - y0, 2 * BIG)).translate((-BIG, y0, -BIG))


def ring(tm, y, y0, y1):
    """Skin ring of a published section cut at Y = y, extruded over Y y0..y1.
    Plane frame (u, v, w) = (z, x, y - y): an even axis permutation, so the
    transform is a proper rotation and +w is world +Y."""
    sec = tm.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    M = np.array([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, -y], [0, 0, 0, 1]], float)
    p2, T = sec.to_2D(to_2D=M)
    polys = p2.polygons_full
    out = None
    for poly in polys:
        e = trimesh.creation.extrude_polygon(poly, y1 - y0)
        e.apply_translation([0, 0, y0 - y])
        e.apply_transform(T)
        m = man(e)
        out = m if out is None else out + m
    return out, len(polys)


def main():
    head, cargo = trimesh.load(HEAD_PUB), trimesh.load(CARGO_PUB)
    hy1, cy0 = head.bounds[1][1], cargo.bounds[0][1]
    mid = 0.5 * (hy1 + cy0)
    print(f"published head ends Y {hy1:.2f}, cargo starts Y {cy0:.2f}: seam gap "
          f"{cy0 - hy1:.2f} mm, meet plane Y {mid:.2f}")
    rh, nh = ring(head, HEAD_RING_Y, HEAD_CUT_Y - 0.5, mid + OVERLAP)
    rc, nc = ring(cargo, CARGO_RING_Y, mid - OVERLAP, CARGO_CUT_Y + 0.5)
    print(f"head ring (Y {HEAD_RING_Y}): {nh} polygon(s); cargo ring (Y {CARGO_RING_Y}): "
          f"{nc} polygon(s); seam zone Y {HEAD_CUT_Y}..{CARGO_CUT_Y} rebuilt as plain skin")
    # 2026-11-01: the cargo shell no longer builds the retired cradle hangers
    # (merge_cargo_interior.CARGO_CRADLE = False).  The boxes this script used
    # to subtract for them ran to Z 250, ABOVE the roof skin, and punched four
    # roof holes (Y 255.7 / 385.7, X +-18; found by
    # tools/assembly_integrity_check.py) -- removed.
    cm = man(cargo)
    part = ((man(head) ^ slab(-BIG, HEAD_CUT_Y)) + rh + rc
            + (cm ^ slab(CARGO_CUT_Y, BIG)))
    # Head roof centreline crack (published head, X 0..0.5, Y 99..104.5; found
    # by tools/assembly_integrity_check.py): bridge it with the skin copied
    # 1 mm either side of the centreline, clipped to the slit's box.
    hm = man(head)
    bridge = ((hm.translate((1.0, 0.0, 0.0)) + hm.translate((-1.0, 0.0, 0.0)))
              ^ man(clf.box(*ROOF_SLIT_BOX)))
    part = part + bridge
    print(f"head roof crack bridged: {bridge.volume():.2f} mm3")
    # Wing-root flanges FUSED into the one-piece print (owner 2026-11-01): the
    # flange was a separate bonded part only for mesh-processing reasons (its
    # docstring: a wall that moves 34 mm across the footprint, knife edges, a
    # whole-shell boolean that did not resolve).  The generator now builds a
    # conforming, locally cropped plate; on the one-piece SLS hull fusing it
    # removes the bond line that limited it.  Flanges sit on SPAR_Y.
    for side in ("port", "stbd"):
        fl = man(trimesh.load(os.path.join(FSTL, f"wing_root_flange_{side}.stl")))
        part = part + fl
        print(f"wing-root flange {side} fused: {fl.volume() / 1e3:.2f} cm3")
    tm = tm_of(part)
    tm.merge_vertices()
    bodies = tm.split(only_watertight=False)
    big = [b for b in bodies if len(b.faces) > 200]
    # drop the zero-area 2-face slivers manifold3d leaves at coplanar seams
    # (same rule as hollow_manifold.py ISLAND_FACE_MIN)
    debris = sum(b.area for b in bodies if len(b.faces) <= 200)
    print(f"dropped {len(bodies) - len(big)} sliver component(s), total area {debris:.4f} mm2")
    tm = big[0] if len(big) == 1 else tm
    print(f"merged part: {len(tm.faces):,} faces, watertight {tm.is_watertight}, "
          f"{len(big)} body(ies) > 200 faces ({len(bodies)} total), volume "
          f"{tm.volume / 1e3:.1f} cm3, Y {tm.bounds[0][1]:.2f}..{tm.bounds[1][1]:.2f}")
    # open cavity across the seam: a probe on the centreline passes through
    probe = m3d.Manifold.cube((20.0, 20.0, 20.0)).translate((-10.0, mid - 10.0, 180.0))
    print(f"seam cavity probe (20 mm cube at Y {mid:.1f}, Z 180-200) overlap with skin: "
          f"{(part ^ probe).volume():.2f} mm3")
    # skin continuity: every slice across the seam is ONE ring around ONE cavity
    from shapely.ops import unary_union
    bad = 0
    for y in np.arange(HEAD_CUT_Y - 1.0, CARGO_CUT_Y + 1.01, 0.5):
        sec = tm.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
        M = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, y], [0, 0, 0, 1]], float)
        u = unary_union(list(sec.to_2D(to_2D=M)[0].polygons_full))
        g = getattr(u, "geoms", [u])
        ok = len(g) == 1 and len(g[0].interiors) >= 1
        bad += not ok
        if not ok:
            print(f"  seam slice Y {y:.1f}: {len(g)} piece(s) -- skin gap")
    print(f"seam skin continuity Y {HEAD_CUT_Y - 1:.1f}..{CARGO_CUT_Y + 1:.1f}: "
          f"{'one closed ring at every 0.5 mm slice' if not bad else f'{bad} slice(s) open'}")
    hdr = (bk.MARKER + b" head+cargo merged (merge_head_cargo_shell.py)").ljust(80, b" ")[:80]
    bk.write_stl_binary(OUT, np.asarray(tm.triangles), hdr)
    print(f"wrote {os.path.relpath(OUT, REPO)}")
    return 0 if tm.is_watertight and len(big) == 1 and not bad else 2


if __name__ == "__main__":
    sys.exit(main())
