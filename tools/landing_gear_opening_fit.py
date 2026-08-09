#!/usr/bin/env python3
"""LG-10.1 -- locate and measure the landing-gear opening flats in the sponson.

The Rev R6 bay was designed to surface-mount on the cargo flank.  That is
wrong: the mounting face is the ANGLED TRAPEZOIDAL FLAT of the landing-gear
opening in the sponson (docs/LANDING_GEAR_ANALYSIS.md SS2.4a).  The vertical
walls squared to port/starboard are the hull sides FORWARD of the sponson and
are not a mounting face.

Method
------
Constant-Y sectioning was tried first and is the wrong tool: it segments the
outline by half-width slope, which is noisy wherever the surface turns, and it
reported a "trapezoidal flat" at Y -7 that is actually a small chamfer on the
vertical wall.  This instead segments the mesh into genuine PLANAR PATCHES
(trimesh facets = coplanar connected face groups), then keeps the patches whose
normal points outboard AND downward -- which is exactly the signature of the
angled opening face and excludes both the vertical walls (nz ~ 0) and the belly
(nx ~ 0).

Reports each patch's plane, tilt, hull-frame extents, in-plane size and whether
its outline is trapezoidal (width of the lower quartile band vs the upper).

Run: /usr/bin/python3 tools/landing_gear_opening_fit.py
     (system python -- the repo .venv hides nothing needed here, but the rest
     of the landing-gear tooling runs there; see the env memory.)

Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note : Authored by Claude (model: Claude Opus 5, Anthropic) under the
          author's direction, 2026-08-09, per AGENTS.md AI attribution.
License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
"""

import os

import numpy as np
import trimesh

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
SHELL_STL = os.path.join(
    REPO_ROOT, "airframe", "stls", "fuselage", "cargo",
    "cargo_sect_shell24_2mm_repaired.stl",
)

X_CL = -169.9          # hull centreline (airframe/AGENTS.md)
Z_LO, Z_HI = 2.0, 75.0  # lower-hull band to search
X_OFF = 30.0           # ignore anything within this of the centreline
MIN_AREA = 120.0       # mm^2, drop slivers
MIN_NX = 0.70          # patch normal must point mostly outboard
MIN_NZ = 0.25          # ...and appreciably downward -- this is the key filter


def analyse_side(mesh, sgn, label):
    """Report angled outboard/down planar patches on one side."""
    cen = mesh.triangles.mean(axis=1)
    nrm = mesh.face_normals
    keep = (
        (cen[:, 2] > Z_LO)
        & (cen[:, 2] < Z_HI)
        & (sgn * (cen[:, 0] - X_CL) > X_OFF)
        & (sgn * nrm[:, 0] > 0.15)
    )
    sub = mesh.submesh([np.where(keep)[0]], append=True)
    facets, areas, normals = sub.facets, sub.facets_area, sub.facets_normal

    hits = [
        i for i in range(len(facets))
        if areas[i] > MIN_AREA
        and abs(normals[i][2]) > MIN_NZ
        and sgn * normals[i][0] > MIN_NX
    ]
    hits.sort(key=lambda i: -areas[i])

    print(f"\n===== {label}: angled outboard/down flats =====")
    out = []
    for i in hits:
        n = normals[i]
        verts = sub.vertices[np.unique(sub.faces[facets[i]].reshape(-1))]
        ctr = verts.mean(axis=0)
        tilt = np.degrees(np.arcsin(np.clip(-n[2], -1, 1)))

        e1 = np.cross(n, [0.0, 0.0, 1.0])
        e1 /= np.linalg.norm(e1)
        e2 = np.cross(n, e1)
        u = (verts - ctr) @ e1
        v = (verts - ctr) @ e2
        lo, hi = v < np.percentile(v, 25), v > np.percentile(v, 75)
        w_lo, w_hi = np.ptp(u[lo]), np.ptp(u[hi])
        shape = "TRAPEZOID" if abs(w_hi - w_lo) > 3.0 else "parallel-sided"

        print(f"  area {areas[i]:6.0f} mm^2   n=({n[0]:6.3f},{n[1]:6.3f},"
              f"{n[2]:6.3f})   tilt {tilt:5.1f} deg (down from horizontal-out)")
        print(f"    centroid ({ctr[0]:7.1f},{ctr[1]:7.1f},{ctr[2]:6.1f})"
              f"   Y {verts[:, 1].min():6.1f}..{verts[:, 1].max():6.1f}"
              f"   Z {verts[:, 2].min():5.1f}..{verts[:, 2].max():5.1f}")
        print(f"    in-plane {np.ptp(u):5.1f} x {np.ptp(v):5.1f} mm"
              f"   lower/upper band width {w_lo:5.1f}/{w_hi:5.1f} -> {shape}")
        out.append(dict(area=float(areas[i]), normal=n, centroid=ctr, tilt=tilt))
    return out


def main():
    mesh = trimesh.load(SHELL_STL)
    print(f"{os.path.basename(SHELL_STL)}: {len(mesh.faces):,} faces")
    port = analyse_side(mesh, +1, "PORT")
    stbd = analyse_side(mesh, -1, "STBD")

    if port and stbd:
        print("\n--- mirror check (port centroid reflected about X_CL) ---")
        for p, s in zip(port, stbd):
            mx = 2 * X_CL - p["centroid"][0]
            d = abs(mx - s["centroid"][0])
            print(f"  port X {p['centroid'][0]:7.1f} -> {mx:7.1f} vs stbd "
                  f"{s['centroid'][0]:7.1f}   delta {d:4.1f} mm"
                  f"   tilt {p['tilt']:.1f} / {s['tilt']:.1f} deg")


if __name__ == "__main__":
    main()
