#!/usr/bin/env python3
"""merge_middle_rear_shell.py -- one-piece MIDDLE + REAR (aft) hull section;
deletes the middle/rear splice collar at Y 509.

Why: the hull is built as two SLS sections joined at the cargo/middle collar
(docs/SLS_27IN_TWO_SECTION_TRIM_STUDY.md section 4; plan 2026-10-31-003
baseline "one-piece middle+rear").  The forward section was merged by
tools/merge_head_cargo_shell.py (commit d92c4f14).  Owner 2026-11-01:
"merge the middle and aft".

Why a LOFT, not the forward tool's straight ring extrusion: the two sections
do not line up at the joint (docs/MASS_AUDIT_MIDDLE_REAR_SECTIONS.md
section 4: outer section 123 x 145 mm middle-side vs 127 x 142 mm rear-side;
the audit requires "a blended transition", not a boolean union).  Sections
measured 2026-11-01:
  * middle Y 501: 3 closed tubes -- main skin (X +/-62.7, Z 95.7..225.4) and
    port/stbd side ducts (X +/-39.6..63.6, Z 84.2..113.2);
  * rear   Y 530.5: the same 3 tubes (main skin to X +/-70, Z ~238).
Between them sit the obsolete collar LANDS (middle Y 503-508; rear Y 510-520)
and, rear Y 520-528, a DORSAL RESIDUE of the land: the centreline skin runs
2.35-3.07 mm instead of 2.04 and holds two loose slivers (X +/-3..7,
Z 232-237).  The QMx blueprints (REF-CAD-003, Sheet 1 port profile, Sheet 5
ventral plan) show the neck flaring smoothly into the engine-bay bulb with
no dorsal feature or lip at this station, and the Henning renders
(REF-CAD-002, below QMx in authority) agree; the residue is a canonical
error and is rebuilt as plain 2 mm skin.  Y 530.5 is the first clean
station aft of it (2.04 mm dorsal, 3 tubes; the published mesh carries
<1 mm2 debris specks at Y 529, 529.75 and 531, ignored as SPECK_MM2).
(Middle land: extra loops, section area up to 3,794 mm2 vs ~1,200 clean.)
With the collar gone the whole zone is rebuilt as plain skin.

Method:
1. Section each published shell at its clean station (MID_RING_Y,
   REAR_RING_Y), split into tubes, and match tubes by centroid.
2. For each tube, resample its outer loop and its hole loop to N points by
   arc length on both stations (same orientation, start point on the ray
   from the loop centroid toward +X), so point i on one station maps to
   point i on the other.
3. Extrude the middle-station tube (outer minus hole) as a manifold3d
   CrossSection over the seam length with N_DIV slices, then WARP each
   vertex linearly from its middle-station position to its matched
   rear-station position (ruled loft; each tube stays one watertight solid).
4. Part = middle_published n {Y < MID_CUT} u lofts u rear_published n
   {Y > REAR_CUT}; the cut planes sit OVERLAP inside the loft so the pieces
   fuse with volume overlap, not coincident faces.
Published, featured skin is kept everywhere outside the seam zone (the ring-
frame pocket at Y 595.7, neck intake, bosses).

Output: airframe/stls/fuselage/middle_rear_shell24_2mm_merged.stl (aircraft
frame R2, header marked like bake_hull_frame).  middle_rear_splice_collar.stl
and the separate middle/rear shells become RETIRED print articles
(tools/sls_retired_parts.py); the separate shells stay on disk as this
tool's inputs.

Hull geometry derives from "Serenity Firefly with landing gear and swivel
engines" by misubisu (thingiverse.com/thing:7330462, CC BY 4.0).  Full
attribution chain: current-specification/LICENSE_AND_ATTRIBUTION.md section 2.
Loft = ruled surface between arc-length-matched sections (standard lofting;
no external code used).

Run:
    /usr/bin/python3 tools/merge_middle_rear_shell.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (Stab-Rabbit-coding)
AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the
author's direction, 2026-11-01, per `AGENTS.md` section 3 AI attribution.
License: CERN-OHL-W-2.0 -- see LICENSES/CERN-OHL-W 2.0
(SPDX-License-Identifier: CERN-OHL-W-2.0)
"""

import os
import sys

import manifold3d as m3d
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from shapely.geometry import LinearRing, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import bake_hull_frame as bk  # noqa: E402

FSTL = os.path.join(REPO, "airframe", "stls", "fuselage")
MID_PUB = os.path.join(FSTL, "middle_shell24_2mm_repaired.stl")
REAR_PUB = os.path.join(FSTL, "rear_shell24_2mm_repaired.stl")
OUT = os.path.join(FSTL, "middle_rear_shell24_2mm_merged.stl")

MID_RING_Y, REAR_RING_Y = 501.0, 530.5   # clean 3-tube stations (see docstring)
OVERLAP = 0.4    # published parts are cut this far INSIDE the loft span
N_PTS = 720      # resample points per loop
N_DIV = 59       # loft slices (0.5 mm pitch over 29.5 mm)
SPECK_MM2 = 1.0  # section pieces below this are mesh debris, not skin
EXPECT_TUBES = 3
# Loft end rings are OUTSET this far (outer loop out, hole loop in) so the
# loft fully covers each published cut face inside the overlap and its sides
# CROSS the published skin instead of sharing a curve with it.  History,
# 2026-11-01: on-surface rings pinched into 23 non-manifold edges at the
# rear station; a 0.02 mm INSET left 0.02 mm knife ledges on the cut faces
# (84 edges after STL welding).  0.02 mm is ~1/5 of an SLS layer.
OUTSET = 0.02
BIG = 1000.0


def man(tm):
    return m3d.Manifold(m3d.Mesh(vert_properties=np.asarray(tm.vertices, np.float32),
                                 tri_verts=np.asarray(tm.faces, np.uint32)))


def tm_of(m):
    """trimesh of a manifold, WITHOUT trimesh's vertex welding: manifold3d's
    output is already index-shared and 2-manifold, and welding by position
    created 4 non-manifold edges at the loft/rear meeting (Y 524, dorsal
    ridge) in the first run."""
    mm = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts),
                           process=False)


def slab(y0, y1):
    return m3d.Manifold.cube((2 * BIG, y1 - y0, 2 * BIG)).translate((-BIG, y0, -BIG))


def tubes(tm, y):
    """Section at Y = y as shapely polygons in plane coords (u, v) = (x, -z).
    (u, v, h) -> world (x = u, y = y + h, z = -v) is a PROPER rotation (det +1),
    so extrusions along +h keep outward normals."""
    sec = tm.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    M = np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, -1, 0, y], [0, 0, 0, 1]], float)
    u = unary_union(list(sec.to_2D(to_2D=M)[0].polygons_full))
    return [orient(p, 1.0) for p in getattr(u, "geoms", [u]) if p.area >= SPECK_MM2]


def resample(ring, n):
    """n points by arc length, CCW/CW as given, starting on the +u ray."""
    ring = LinearRing(ring.coords)
    pts = np.array([ring.interpolate(t, normalized=True).coords[0]
                    for t in np.linspace(0.0, 1.0, n, endpoint=False)])
    c = pts.mean(axis=0)
    # start index: point whose direction from the centroid is closest to +u
    ang = np.abs(np.arctan2(pts[:, 1] - c[1], pts[:, 0] - c[0]))
    return np.roll(pts, -int(np.argmin(ang)), axis=0)


def loft(pa, pb, y0, y1):
    """Ruled loft of polygon-with-holes pa (at y0) onto pb (at y1)."""
    if len(pa.interiors) != len(pb.interiors):
        raise RuntimeError("tube topology differs between stations")
    la = [resample(pa.exterior, N_PTS)] + [resample(h, N_PTS) for h in pa.interiors]
    lb = [resample(pb.exterior, N_PTS)] + [resample(h, N_PTS) for h in pb.interiors]
    # holes: match by centroid when a tube has more than one
    if len(la) > 2:
        cb = [lp.mean(axis=0) for lp in lb[1:]]

        def nearest(lp):
            return lb[1 + int(np.argmin([np.linalg.norm(c - lp.mean(axis=0)) for c in cb]))]

        lb = [lb[0]] + [nearest(lp) for lp in la[1:]]
    A, B = np.vstack(la), np.vstack(lb)
    cs = m3d.CrossSection([lp.tolist() for lp in la], m3d.FillRule.EvenOdd)
    L = y1 - y0
    ext = m3d.Manifold.extrude(cs, L, n_divisions=N_DIV)
    tree = cKDTree(A)

    def warp(P):
        P = np.asarray(P, float)
        d, i = tree.query(P[:, :2])
        if d.max() > 1e-3:
            raise RuntimeError(f"loft vertex not on a station loop ({d.max():.4f} mm)")
        t = (P[:, 2] / L)[:, None]
        uv = (1.0 - t) * A[i] + t * B[i]
        return np.column_stack([uv[:, 0], y0 + P[:, 2], -uv[:, 1]])

    return ext.warp_batch(warp)


def seam_loft(mesh_a, ya, mesh_b, yb, expect):
    """Blended seam: ruled loft of every skin tube of `mesh_a` sectioned at
    Y = ya onto the matching tube of `mesh_b` at Y = yb (ya < yb), each end
    ring OUTSET by OUTSET.  Shared by merge_head_cargo_shell.py."""
    ta, tb = tubes(mesh_a, ya), tubes(mesh_b, yb)
    if len(ta) != expect or len(tb) != expect:
        raise RuntimeError(f"expected {expect} tubes at both stations, got "
                           f"{len(ta)} / {len(tb)}")
    lofts = None
    for pa in ta:
        pb = min(tb, key=lambda q: q.centroid.distance(pa.centroid))
        pa_o = orient(pa.buffer(OUTSET, join_style=2), 1.0)
        pb_o = orient(pb.buffer(OUTSET, join_style=2), 1.0)
        if not (isinstance(pa_o, Polygon) and isinstance(pb_o, Polygon)):
            raise RuntimeError("outset merged/split a tube; reduce OUTSET")
        lf = loft(pa_o, pb_o, ya, yb)
        print(f"  tube at u,v {np.round(pa.centroid.coords[0], 1).tolist()} -> "
              f"{np.round(pb.centroid.coords[0], 1).tolist()}: loft {lf.volume() / 1e3:.2f} "
              f"cm3, genus {lf.genus()}")
        lofts = lf if lofts is None else lofts + lf
    return lofts


def main():
    mid, rear = trimesh.load(MID_PUB), trimesh.load(REAR_PUB)
    print(f"published middle Y {mid.bounds[0][1]:.2f}..{mid.bounds[1][1]:.2f}, rear Y "
          f"{rear.bounds[0][1]:.2f}..{rear.bounds[1][1]:.2f}; seam zone Y {MID_RING_Y}.."
          f"{REAR_RING_Y} rebuilt as a blended loft")
    lofts = seam_loft(mid, MID_RING_Y, rear, REAR_RING_Y, EXPECT_TUBES)
    cut_m, cut_r = MID_RING_Y + OVERLAP, REAR_RING_Y - OVERLAP
    mm, rr = man(mid), man(rear)
    removed = (mm ^ slab(cut_m, BIG)).volume() + (rr ^ slab(-BIG, cut_r)).volume()
    print(f"collar lands removed (middle Y>{cut_m}, rear Y<{cut_r}): {removed / 1e3:.2f} cm3; "
          f"loft added {lofts.volume() / 1e3:.2f} cm3")
    part = (mm ^ slab(-BIG, cut_m)) + lofts + (rr ^ slab(cut_r, BIG))
    print(f"manifold3d status {part.status()}, genus {part.genus()}")
    tm = tm_of(part)
    bodies = tm.split(only_watertight=False)
    big = [b for b in bodies if len(b.faces) > 200]
    debris = sum(b.area for b in bodies if len(b.faces) <= 200)
    print(f"dropped {len(bodies) - len(big)} sliver component(s), total area {debris:.4f} mm2")
    tm = big[0] if len(big) == 1 else tm
    print(f"merged part: {len(tm.faces):,} faces, watertight {tm.is_watertight}, "
          f"{len(big)} body(ies) > 200 faces, volume {tm.volume / 1e3:.1f} cm3, "
          f"Y {tm.bounds[0][1]:.2f}..{tm.bounds[1][1]:.2f}, bbox "
          f"{np.ptp(tm.bounds, axis=0).round(1).tolist()} mm")
    # skin continuity: every 0.5 mm slice across the seam is the same 3 closed
    # tubes, each around an open cavity
    bad = 0
    for y in np.arange(MID_RING_Y - 1.0, REAR_RING_Y + 1.01, 0.5):
        g = tubes(tm, y)
        ok = len(g) == EXPECT_TUBES and all(len(p.interiors) >= 1 for p in g)
        bad += not ok
        if not ok:
            print(f"  seam slice Y {y:.1f}: {len(g)} piece(s), holes "
                  f"{[len(p.interiors) for p in g]}")
    print(f"seam skin continuity Y {MID_RING_Y - 1:.1f}..{REAR_RING_Y + 1:.1f}: "
          f"{'3 closed tubes at every 0.5 mm slice' if not bad else f'{bad} slice(s) off'}")
    # minimum skin in the loft (SLS floor 1.0 mm, REF-MFG-001 p. 15): sample
    # each slice's ring width as area / mean perimeter
    thin = min(p.area / (0.5 * (p.exterior.length + sum(h.length for h in p.interiors)))
               for y in np.arange(MID_RING_Y, REAR_RING_Y + 0.01, 1.0) for p in tubes(tm, y))
    print(f"loft zone mean-wall floor {thin:.2f} mm (area / mean perimeter)")
    # STL carries no shared indices: every reader welds by position, which
    # turns manifold3d's zero-area pinch points into non-manifold edges and
    # sliver bodies.  Clean the WELDED mesh, then prove it by re-reading.
    tm = separate_f32_collisions(tm)
    tm = weld_clean(tm)
    hdr = (bk.MARKER + b" middle+rear merged (merge_middle_rear_shell.py)").ljust(80, b" ")[:80]
    bk.write_stl_binary(OUT, np.asarray(tm.triangles), hdr)
    back = weld_clean(trimesh.load(OUT), quiet=True)
    es = np.sort(trimesh.load(OUT).edges, axis=1)
    _, cnt = np.unique(es, axis=0, return_counts=True)
    ok = back.is_watertight and (cnt != 2).sum() == 0
    print(f"wrote {os.path.relpath(OUT, REPO)}; re-read: watertight "
          f"{trimesh.load(OUT).is_watertight}, edges not shared by exactly 2 faces "
          f"{(cnt != 2).sum()}, volume {back.volume / 1e3:.1f} cm3")
    return 0 if ok and len(big) == 1 and not bad else 2


def separate_f32_collisions(tm, step=2e-3):
    """manifold3d keeps topologically distinct vertices that can sit closer
    than float32 resolution (~6e-5 mm at Y 530).  Binary STL stores float32,
    so on write they collapse into one point and the seam pinches into
    non-manifold edges (44-84 edges seen at the seam planes, 2026-11-01).
    Nudge every colliding vertex but one per group by `step` mm along its own
    vertex normal, so the written file keeps them apart.  2e-3 mm is far below
    SLS resolution."""
    v = np.asarray(tm.vertices, float).copy()
    key = v.astype(np.float32)
    _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
    inv = inv.ravel()
    groups = np.flatnonzero(cnt > 1)
    if len(groups) == 0:
        print("float32 collisions: none")
        return tm
    vn = np.asarray(tm.vertex_normals, float).copy()
    # vertices that only touch zero-area faces have no usable normal; move
    # those along the hull axis (+Y) instead, which is never parallel to the
    # seam planes they sit on
    weak = np.linalg.norm(vn, axis=1) < 0.5
    vn[weak] = (0.0, 1.0, 0.0)
    moved = 0
    for g in groups:
        idx = np.flatnonzero(inv == g)
        for k, i in enumerate(idx[1:], start=1):
            v[i] += step * k * vn[i]
            moved += 1
    print(f"float32 collisions: {len(groups)} group(s), {moved} vertex(es) nudged "
          f"{step} mm along their normals")
    return trimesh.Trimesh(v, tm.faces, process=False)


def weld_clean(tm, quiet=False):
    """Weld by position (as an STL reader does), drop exact duplicate faces,
    keep the one real body.  Zero-area faces are KEPT: they carry topology
    (dropping them opened 29 edges, 2026-11-01)."""
    tm = trimesh.Trimesh(tm.vertices, tm.faces, process=True)
    tm.update_faces(tm.unique_faces())
    tm.remove_unreferenced_vertices()
    bodies = tm.split(only_watertight=False)
    keep = max(bodies, key=lambda b: len(b.faces))
    if not quiet:
        print(f"weld/clean: {len(bodies) - 1} sliver body(ies) dropped "
              f"({sum(b.area for b in bodies if b is not keep):.4f} mm2), "
              f"watertight {keep.is_watertight}")
    return keep


if __name__ == "__main__":
    sys.exit(main())
