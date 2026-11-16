#!/usr/bin/env python3
"""cfd_internal_air_domain.py -- voxel air domain of the fuselage interior for
the OpenFOAM cooling-air case (owner, 2026-11-01: rear fan pulling bow-inlet
air to the Phase 11 tail exit; "use /openfoam-cfd for your airflow
modeling").

Walls: the merged head+cargo hull, the cargo doors (closed), the cargo/middle
splice collar, the middle and rear shells (treated as ONE section with no
middle/rear collar -- owner 2026-11-01, joined in another workspace; the
2 mm gap between the two STLs is closed by the wall dilation), and every
equipment envelope in the published layout (head fwd layout incl. the Bay A
mounts, twin tray, cargo layout minus the retired cargo battery/cradle,
middle layout).  The sealed forward ramp fairing is part of the published
shell (cargo_layout_fit, "ramp fairing").

Air = cells reached by a flood fill from a seed inside Bay A that are not
wall.  If the fill reaches the domain boundary the hull LEAKS; the tool
reports the first leaking cells and stops.

Method: every mesh is sectioned at each Y layer; skin sections are open
polylines and are rasterised along their length (0.4 mm steps); equipment is
rasterised the same way and filled (closed sections).  Walls are dilated by
one cell so a 2.5 mm voxel cannot pass a seam.

Output: air.npz (mask, origin, pitch) for tools/cfd_cooling_case.py.

Run:
    /usr/bin/python3 tools/cfd_internal_air_domain.py [--pitch 2.5] [--out DIR]

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the
author's direction, 2026-11-01, per `AGENTS.md` §3 AI attribution.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import argparse
import os
import sys

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

X0, X1, Z0, Z1 = -80.0, 80.0, 60.0, 300.0
Y0, Y1 = -5.0, 695.0
SEED = (0.0, 330.0, 200.0)  # open cargo bay over the payload (22.5 mm clearance), R2 mm


def wall_meshes():
    import trimesh
    import node_thermal_forced_air as n
    import head_layout_fit as h
    g = n._geometry()
    fs = os.path.join(h.REPO, "airframe", "stls", "fuselage")
    skins = [m for m, _ in g["hulls"]]
    skins += [trimesh.load(os.path.join(fs, "cargo", f))
              for f in ("cargo_door_port.stl", "cargo_door_stbd.stl")]
    skins.append(trimesh.load(os.path.join(fs, "cargo_middle_splice_collar.stl")))
    # parts that close hull apertures in the built aircraft (owner 2026-11-01:
    # "are the legs attached? are the wings attached?") -- wings + root
    # flanges close the wing-root mortise; the 3.0 in flight-article gear bays
    # and legs close the gear openings
    for f in ("wing_root_flange_port.stl", "wing_root_flange_stbd.stl"):
        skins.append(trimesh.load(os.path.join(fs, f)))
    for f in ("wing_port_s1223_revo.stl", "wing_stbd_s1223_revo.stl"):
        skins.append(trimesh.load(os.path.join(h.REPO, "airframe", "stls", "wings", f)))
    lg = os.path.join(fs, "landing-gear")
    for f in ("lg_r6_3_0in_bay_fore-port.stl", "lg_r6_3_0in_bay_fore-stbd.stl",
              "lg_r6_3_0in_bay_aft-port.stl", "lg_r6_3_0in_bay_aft-stbd.stl",
              "lg_r6_3_0in_hull_legs.stl", "lg_a1b_housing_fore-port.stl",
              "lg_a1b_housing_fore-stbd.stl"):
        skins.append(trimesh.load(os.path.join(lg, f)))
    # physical equipment only: keep-out / swept / harness envelopes are not walls
    keep_out = ("swept", "zone", "line", "corridor", "LOS", "cone", "trunk", "keep")
    return skins, [s for name, s in g["solids"] if not any(k in name for k in keep_out)]


def _raster_lines(mask2d, mesh, y, pitch):
    sec = mesh.section(plane_origin=[0.0, y, 0.0], plane_normal=[0.0, 1.0, 0.0])
    if sec is None:
        return
    for ent in sec.discrete:
        pts = np.asarray(ent)[:, [0, 2]]
        seg = np.diff(pts, axis=0)
        n = np.maximum(1, (np.linalg.norm(seg, axis=1) / 0.4).astype(int))
        for a, d, k in zip(pts[:-1], seg, n):
            t = np.linspace(0.0, 1.0, k + 1)[:, None]
            p = a + t * d
            i = ((p[:, 0] - X0) / pitch).astype(int)
            j = ((p[:, 1] - Z0) / pitch).astype(int)
            ok = (i >= 0) & (i < mask2d.shape[0]) & (j >= 0) & (j < mask2d.shape[1])
            mask2d[i[ok], j[ok]] = True


def build(pitch):
    skins, solids = wall_meshes()
    nx, ny, nz = (int(round((X1 - X0) / pitch)), int(round((Y1 - Y0) / pitch)),
                  int(round((Z1 - Z0) / pitch)))
    wall = np.zeros((nx, ny, nz), bool)
    for jy in range(ny):
        y = Y0 + (jy + 0.5) * pitch
        sl = np.zeros((nx, nz), bool)
        for m in skins:
            if m.bounds[0][1] <= y <= m.bounds[1][1]:
                _raster_lines(sl, m, y, pitch)
        eq = np.zeros((nx, nz), bool)
        for m in solids:
            if m.bounds[0][1] <= y <= m.bounds[1][1]:
                _raster_lines(eq, m, y, pitch)
        sl |= ndimage.binary_fill_holes(eq)
        wall[:, jy, :] = sl
    wall = ndimage.binary_dilation(wall, iterations=1)
    seed = tuple(int((v - o) / pitch) for v, o in zip(SEED, (X0, Y0, Z0)))
    if wall[seed]:
        raise SystemExit(f"seed {SEED} is inside a wall")
    lab, _ = ndimage.label(~wall)
    air = lab == lab[seed]
    leak = air[0].any() or air[-1].any() or air[:, 0].any() or air[:, -1].any() \
        or air[:, :, 0].any() or air[:, :, -1].any()
    return air, wall, leak


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pitch", type=float, default=2.5)
    ap.add_argument("--out", default=".")
    a = ap.parse_args()
    air, wall, leak = build(a.pitch)
    vol_l = air.sum() * a.pitch ** 3 / 1e6
    print(f"air cells {air.sum()} ({vol_l:.2f} L) at pitch {a.pitch} mm; leak={leak}")
    if leak:
        idx = np.argwhere(air)
        for ax, name in ((0, "X"), (1, "Y"), (2, "Z")):
            lo, hi = idx[:, ax].min(), idx[:, ax].max()
            print(f"  air spans {name} cells {lo}..{hi} of {air.shape[ax]}")
        ys = np.unique(idx[(idx[:, 0] == 0) | (idx[:, 0] == air.shape[0] - 1)
                           | (idx[:, 2] == 0) | (idx[:, 2] == air.shape[2] - 1), 1])
        print("  boundary-touching Y stations (mm):",
              sorted({round(Y0 + (j + 0.5) * a.pitch) for j in ys})[:40])
    np.savez_compressed(os.path.join(a.out, "air.npz"), air=air, wall=wall,
                        origin=np.array([X0, Y0, Z0]), pitch=a.pitch)
    return 1 if leak else 0


if __name__ == "__main__":
    sys.exit(main())
