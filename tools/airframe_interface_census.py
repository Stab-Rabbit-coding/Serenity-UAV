#!/usr/bin/python3
"""Exhaustive interface census of the airframe master assembly.

Input: the hull-frame STLs written by ``tools/export_assembly_meshes.py``
(every part exactly where ``serenity_assembly.py`` places it).

Output (stdout table, ``--json`` for machine use):

1. **Pair census** — EVERY pair of placed parts is tested (n(n-1)/2, no
   hand-picked list), so no joint can be skipped by omission.  Each pair is
   classified:

   * ``CLASH``   intersection volume > ``--clash-mm3`` (manifold3d boolean;
                 needs both meshes watertight)
   * ``CONTACT`` closest vertex-to-surface gap <= ``--contact-mm``
   * ``NEAR``    gap <= ``--near-mm`` (a joint or clearance to justify)
   * pairs farther apart are not interfaces and are omitted.

   A pair whose mesh is not watertight is reported ``UNVERIFIED-VOLUME``
   rather than silently passing.

2. **Symmetry / synchronisation** — every ``*_Port`` part is mirrored
   through the hull centre plane and compared with its ``*_Stbd`` twin
   (centroid offset and bounding-box mismatch).  A local joint fix that
   moved one side only shows up here.  This is the owner rule of
   2026-10-03: local assemblies INFORM the airframe; they never desync it.

Every interface found here must map to a row in the joint register
(``docs/AIRFRAME_JOINT_REGISTER.md``), which carries the joint's type,
motion, non-printed parts, air paths and the in-context check that owns it.

Usage::

    /usr/bin/python3 tools/airframe_interface_census.py CENSUS_DIR [--json]

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, per AGENTS.md AI attribution.  License: CC BY 4.0.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree

try:
    import manifold3d as m3
except ImportError:  # pragma: no cover - reported, never silently skipped
    m3 = None

SPAN_AXIS = 0          # hull X is span (port +X / stbd -X, serenity_assembly.py)
# Hull centre plane, MEASURED on the baked cargo shell (tools/bake_hull_frame.py
# Wing_Stbd note): the hull frame origin is NOT on the aircraft centreline.
CENTRE_X = -169.241


def load(census: Path) -> dict[str, trimesh.Trimesh]:
    """Load every placed mesh named in the manifest."""
    man = json.loads((census / "manifest.json").read_text())
    out = {}
    for label, rec in man.items():
        m = trimesh.load_mesh(rec["file"], force="mesh")
        if len(m.faces):
            out[label] = m
    return out


def to_manifold(m: trimesh.Trimesh):
    """manifold3d solid, or None when the mesh cannot be one."""
    if m3 is None or not m.is_watertight:
        return None
    mesh = m3.Mesh(vert_properties=np.asarray(m.vertices, np.float32),
                   tri_verts=np.asarray(m.faces, np.uint32))
    solid = m3.Manifold(mesh)
    return None if solid.status() != m3.Error.NoError else solid


def prepare(m: trimesh.Trimesh, spacing: float) -> np.ndarray:
    """Vertices plus an even surface sample at ~spacing (mm) for the gap trees.

    Vertex-only distance overstates gaps across large flat faces; sampling
    the surface bounds the gap error by about the sample spacing.  (Edge
    subdivision did the same but timed out on the fuselage shells.)"""
    n = int(min(max(m.area / (spacing * spacing), 2000), 400000))
    pts, _ = trimesh.sample.sample_surface_even(m, n, seed=1)
    return np.vstack([m.vertices, pts])


def census(parts: dict, near: float, contact: float, clash: float,
           max_edge: float) -> list[dict]:
    """Classify every pair of parts."""
    names = sorted(parts)
    verts = {n: prepare(parts[n], max_edge) for n in names}
    trees = {n: cKDTree(verts[n]) for n in names}
    solids = {n: to_manifold(parts[n]) for n in names}
    rows = []
    for a, b in itertools.combinations(names, 2):
        lo = np.maximum(parts[a].bounds[0], parts[b].bounds[0]) - near
        hi = np.minimum(parts[a].bounds[1], parts[b].bounds[1]) + near
        if np.any(lo > hi):
            continue                                   # boxes too far apart
        d1, _ = trees[b].query(verts[a], k=1)
        d2, _ = trees[a].query(verts[b], k=1)
        g = float(min(d1.min(), d2.min()))
        if g > near:
            continue
        vol = None
        if solids[a] is not None and solids[b] is not None:
            vol = (solids[a] ^ solids[b]).volume()
        if vol is not None and vol > clash:
            cls = "CLASH"
        elif g <= contact:
            cls = "CONTACT" if vol is not None else "CONTACT/UNVERIFIED-VOLUME"
        else:
            cls = "NEAR" if vol is not None else "NEAR/UNVERIFIED-VOLUME"
        rows.append({"a": a, "b": b, "class": cls, "gap_mm": round(g, 2),
                     "overlap_mm3": None if vol is None else round(vol, 2)})
    order = {"CLASH": 0}
    rows.sort(key=lambda r: (order.get(r["class"], 1), r["gap_mm"]))
    return rows


def symmetry(parts: dict, tol: float) -> list[dict]:
    """Mirror each *_Port part and compare with its *_Stbd twin."""
    out = []
    for name, m in sorted(parts.items()):
        if not name.endswith("_Port"):
            continue
        twin = name[:-5] + "_Stbd"
        if twin not in parts:
            out.append({"part": name, "status": "NO STBD TWIN"})
            continue
        p = m.bounds.copy()
        p[:, SPAN_AXIS] = 2 * CENTRE_X - p[::-1, SPAN_AXIS]   # mirror the box
        s = parts[twin].bounds
        cp = m.centroid.copy()
        cp[SPAN_AXIS] = 2 * CENTRE_X - cp[SPAN_AXIS]
        dc = float(np.linalg.norm(cp - parts[twin].centroid))
        db = float(np.abs(p - s).max())
        out.append({"part": name[:-5], "centroid_off_mm": round(dc, 2),
                    "bbox_off_mm": round(db, 2),
                    "status": "SYNC" if max(dc, db) <= tol else "DESYNC"})
    return out


def main() -> int:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("census", type=Path)
    ap.add_argument("--near-mm", type=float, default=3.0)
    ap.add_argument("--contact-mm", type=float, default=0.3)
    ap.add_argument("--clash-mm3", type=float, default=0.5)
    ap.add_argument("--sym-tol-mm", type=float, default=0.5)
    ap.add_argument("--max-edge", type=float, default=0.7,
                    help="surface-sample spacing for gaps (mm)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    parts = load(a.census)
    rows = census(parts, a.near_mm, a.contact_mm, a.clash_mm3, a.max_edge)
    sym = symmetry(parts, a.sym_tol_mm)
    if a.json:
        print(json.dumps({"parts": sorted(parts), "pairs": rows, "symmetry": sym},
                         indent=2))
    else:
        nt = [n for n, m in parts.items() if not m.is_watertight]
        print(f"{len(parts)} placed parts, {len(parts) * (len(parts) - 1) // 2} pairs "
              f"tested; {len(rows)} interfaces; non-watertight: {len(nt)}")
        for r in rows:
            print(f"  {r['class']:<26} {r['a']:<34} {r['b']:<34} gap {r['gap_mm']:6.2f}"
                  f"  overlap {r['overlap_mm3']}")
        print("\nSymmetry (port mirrored vs stbd):")
        for s in sym:
            print("  ", s)
    bad = any(r["class"] == "CLASH" for r in rows) or any(
        s.get("status") != "SYNC" for s in sym)
    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
