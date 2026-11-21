#!/usr/bin/env python3
"""nacelle64_esc_bay_check.py -- the 64 mm ESC bay covers fit their pods, and what the windows cost.

Rev U plan S4 (NAC-64-GEOM-03 covers, window structural allowance) and NAC-64-GEOM-05 (the bay gates
read the 64 mm pod).  The 50 mm tool `nacelle_esc_bay_fit.py` sited the bays on the archived 50 mm
pods; the 64 mm bay siting was settled by `esc80_cooptimize.py` and OD-3.  What carries over is its
gate T9 (do the published covers fit the published pods?) and the section-modulus report the cover
file promises ("tools/nacelle_esc_bay_fit.py reports the section modulus with and without the
windows").  Both run here on the PUBLISHED, hull-baked meshes, mapped back to nacelle-local with the
inverse of each part's own bake placement (tools/bake_hull_frame.py COMPONENTS), so this gates what
is actually shipped.

Checks, per side:
  C1  overlap  cover AND pod volume, every cover (manifold3d boolean).  Gate: <= 1 mm3 (0.00006 in3).
  C2  seating  distance from sampled cover points to the pod surface.  A seated cover lands its rim
               and underside within the rebate clearance (ESC_COVER_FIT 0.25 mm per side, plus
               facet error); a displaced one has nothing that close.  Gate: the closest 1 % of
               points within 0.6 mm.  The median is reported.
  C3  section  the pod's cross-section at the bay mid-station (nacelle-local Z = ESC bay centre):
               area, second moments about the duct-axis-parallel centroidal axes, and the elastic
               section modulus Z = I / c, with the windows OPEN (pod alone) and CLOSED (pod + covers).
               Reported, not gated: the cover is a bolted doubler and carries load only through its
               six fasteners, so "closed" is the upper bound and "open" the lower bound.

Usage:  /usr/bin/python3 tools/nacelle64_esc_bay_check.py [--json PATH]
Exit 0 = C1 and C2 pass on all four covers; 1 = a cover does not fit.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (GitHub Stab-Rabbit-coding)
AI note: Written by Claude (Claude Opus 5.5, Anthropic) under the author's direction, 2026-11-21.
         Derivative of nacelle_esc_bay_fit.py (gate T9).
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import manifold3d as mf
import numpy as np
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bake_hull_frame as bhf  # noqa: E402  the placements the published parts were baked with
import nacelle_64_scale as ns  # noqa: E402  single-source scale (ESC bay stations ride on it)

ROOT = Path(__file__).resolve().parent.parent
STL = ROOT / "airframe" / "stls"
IN3 = 16387.064            # mm3 per in3
OVERLAP_GATE_MM3 = 1.0
SEAT_GATE_MM = 0.6
#: ESC bay centre, nacelle-local Z: nacelle_pod_64mm_tandem.scad ESC_BAY_Z0/Z1 = 95 x P64_A -/+ 21.
BAY_MID_Z = 95.0 * ns.get("P64_A")


def placement(name: str) -> np.ndarray:
    """4x4 hull <- nacelle-local transform a component was baked with."""
    _rel, (px, py, pz, qx, qy, qz, qw) = bhf.COMPONENTS[name]
    m = np.eye(4)
    m[:3, :3] = bhf.quat_to_matrix(qx, qy, qz, qw)
    m[:3, 3] = (px, py, pz)
    return m


def local_mesh(name: str) -> trimesh.Trimesh:
    """Published part, mapped back into nacelle-local."""
    rel, _pl = bhf.COMPONENTS[name]
    mesh = trimesh.load_mesh(STL / rel, force="mesh")
    mesh.apply_transform(np.linalg.inv(placement(name)))
    return mesh


def to_manifold(mesh: trimesh.Trimesh) -> mf.Manifold:
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(mesh.vertices, np.float32),
                               tri_verts=np.asarray(mesh.faces, np.uint32)))


def section_props(mesh: trimesh.Trimesh, z: float) -> dict:
    """Area, centroidal second moments and section moduli of the slice at nacelle-local z."""
    sec = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    # to_2D with an identity frame keeps the nacelle-local x, y of the slice.
    planar, _ = sec.to_2D(to_2D=np.array([[1, 0, 0, 0], [0, 1, 0, 0],
                                          [0, 0, 1, -z], [0, 0, 0, 1]], float))
    polys = planar.polygons_full
    area = sum(p.area for p in polys)
    cx = sum(p.area * p.centroid.x for p in polys) / area
    cy = sum(p.area * p.centroid.y for p in polys) / area
    ixx = iyy = 0.0
    xs, ys = [], []
    for p in polys:
        for ring in [p.exterior, *p.interiors]:
            c = np.asarray(ring.coords)
            x, y = c[:, 0] - cx, c[:, 1] - cy
            cross = x[:-1] * y[1:] - x[1:] * y[:-1]
            # Green's theorem; interiors are wound opposite to exteriors by shapely.
            ixx += np.sum((y[:-1] ** 2 + y[:-1] * y[1:] + y[1:] ** 2) * cross) / 12.0
            iyy += np.sum((x[:-1] ** 2 + x[:-1] * x[1:] + x[1:] ** 2) * cross) / 12.0
            xs.extend(x)
            ys.extend(y)
    ixx, iyy = abs(ixx), abs(iyy)
    return {"area_mm2": area, "ixx_mm4": ixx, "iyy_mm4": iyy,
            "zxx_mm3": ixx / max(abs(min(ys)), abs(max(ys))),
            "zyy_mm3": iyy / max(abs(min(xs)), abs(max(xs)))}


def check_side(side: str) -> tuple[dict, list[str]]:
    cap = side.capitalize()
    pod = local_mesh(f"Nacelle64_{cap}")
    pod_m = to_manifold(pod)
    out: dict = {"covers": {}}
    fails: list[str] = []
    covers = []
    for bay in ("A", "B"):
        cname = f"EscCover64_{cap}_{bay}"
        cov = local_mesh(cname)
        covers.append(cov)
        ov = (to_manifold(cov) ^ pod_m).volume()
        # Seating: unsigned distance from sampled cover points to the pod, clipped to the cover's
        # neighbourhood to keep the query small.  A seated cover has its rim and underside within
        # the rebate clearance of the pod; a displaced one has nothing that close.
        lo, hi = cov.bounds[0] - 5.0, cov.bounds[1] + 5.0
        near = pod.slice_plane(lo, [1, 0, 0]).slice_plane(hi, [-1, 0, 0])
        near = near.slice_plane(lo, [0, 1, 0]).slice_plane(hi, [0, -1, 0])
        near = near.slice_plane(lo, [0, 0, 1]).slice_plane(hi, [0, 0, -1])
        rng = np.random.default_rng(0)
        pts = cov.vertices[rng.choice(len(cov.vertices), min(5000, len(cov.vertices)),
                                      replace=False)]
        db = trimesh.proximity.ProximityQuery(near).on_surface(pts)[1]
        p95, med = float(np.percentile(db, 1)), float(np.median(db))
        ok = ov <= OVERLAP_GATE_MM3 and p95 <= SEAT_GATE_MM
        out["covers"][bay] = {"overlap_mm3": ov, "seat_p01_mm": p95, "seat_median_mm": med,
                              "mass_g": cov.volume * 1.11e-3, "pass": ok}
        print(f"  {'ok  ' if ok else 'FAIL'} [C1/C2] {side} cover {bay}: overlap "
              f"{ov / IN3:.5f} in3 ({ov:.2f} mm3); closest-1 % to pod {p95 / 25.4:.4f} in "
              f"({p95:.3f} mm), median {med:.3f} mm")
        if not ok:
            fails.append(f"{side} cover {bay}")
    open_ = section_props(pod, BAY_MID_Z)
    closed = section_props(trimesh.util.concatenate([pod, *covers]), BAY_MID_Z)
    out["section_open"], out["section_closed"] = open_, closed
    for k, lab in (("zxx_mm3", "Z about local x (pitch in cruise)"),
                   ("zyy_mm3", "Z about local y (yaw in cruise)")):
        print(f"  [C3] {side} {lab}: windows open {open_[k] / IN3 * 1e3:.1f} x10^-3 in3 "
              f"({open_[k]:,.0f} mm3), covers in {closed[k] / IN3 * 1e3:.1f} x10^-3 in3 "
              f"({closed[k]:,.0f} mm3); open/closed {open_[k] / closed[k]:.3f}")
    print(f"  [C3] {side} section area at Z {BAY_MID_Z:.2f} mm: open {open_['area_mm2']:.0f}, "
          f"closed {closed['area_mm2']:.0f} mm2")
    return out, fails


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path, help="write the results here")
    args = ap.parse_args(argv)
    print(f"64 mm ESC bay check (published meshes; bay mid-station nacelle-local Z {BAY_MID_Z:.2f} mm)")
    results, fails = {}, []
    for side in ("port", "stbd"):
        results[side], f = check_side(side)
        fails += f
    if args.json:
        args.json.write_text(json.dumps(results, indent=2))
    print("RESULT:", "PASS" if not fails else "FAIL -- " + ", ".join(fails))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
