#!/usr/bin/env python3
"""nacelle64_assembly_check.py -- assemble the 64 mm nacelle and check fit, tilt sweep and cable.

Everything is built in the NACELLE-LOCAL frame (duct axis +Z, intake at Z=0, tilt axis along X
through (Y=0, Z=PIVOT_Z), pylon face at +X).  That frame is the one nacelle_tilt_joint_context.scad
uses; the starboard hull parts map into it by
    x_l = x_h + (176.55 + SEAT)      y_l = -(z_h - SPAR_Z)      z_l = (y_h - SPAR_Y) + PIVOT_Z
(hull frame R2, X +port, Y +aft, Z up; SPAR_Y/SPAR_Z from tools/hull_datums.py).
The port nacelle is the X-mirror of the starboard one.

Checks:
  static   pairwise overlap volume of every part pair at tilt 0 (mm^3, manifold3d booleans)
  sweep    the tilting group (pod, cartridge, nozzle, trunnion) against the fixed group (spar, wing,
           wing-tip pinion) over TILT_MIN..TILT_MAX; ring-gear-vs-pinion contact is
           tooth phase (a meshing pair overlaps at the pitch circle by design)
  cable    a voxel clearance search: can a bundle of BUNDLE_D (+ CLEARANCE) travel from the
           spar-bore exit to the ESC disconnect bay, and how long is that path

Inputs: meshes under airframe/stls (published), the freshly rendered pod (--pod,
default side) and the trunnion rendered from SCAD (--trunnion).  Both are renders of the live
flattened SCAD; the published pod STL is stale (NAC-64-REBAKE).

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic) under the author's direction, 2026-11-07.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

import manifold3d as m
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parent.parent
STL = ROOT / "airframe" / "stls"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import hull_datums as hd  # noqa: E402
import nacelle_64_scale as ns  # noqa: E402

PIVOT_Z = 109.7                                  # pod PIVOT_Z == PIVOT_Z_64 (tilt joint context)
AXIS_SHIFT = ns.get("P64_AXIS_SHIFT_S")          # 9.61
TRUNNION_X0 = 28.2 + AXIS_SHIFT                  # spar tip == trunnion outboard face
WING_TIP_FACE = 41.7 + AXIS_SHIFT + 7.0          # P64_STUB_EXTRA
PAD_PROUD = 2.0
SEAT = WING_TIP_FACE - PAD_PROUD                 # wing tip pad face, local X
WING_TIP_HULL_X = 176.55                         # |X| of the wing tip pad face in hull R2
CART_Z0 = 103.7                                  # stage-2 cartridge seats on the pod bore step
NOZ_Z0 = ns.get("P64_Z_NOZ")                     # nozzle ring pocket station (199.13)
TILT_MIN, TILT_MAX = -5.0, 135.0                 # deg, 0 = duct axis horizontal (aft)
# 4 x 10 AWG circumscribed (WING_ATTACH_INTERFACE 2.3)
BUNDLE_D = 13.28
CLEARANCE = 1.5                                  # radial, so the bundle can twist
SPAR_OD, SPAR_ID = 20.0, 16.3
DISC_Z = 51.0 * ns.get("P64_A")                  # ESC disconnect bay centre Z
DISC_W, DISC_H, DISC_D = 30.0, 14.0, 6.0
FACE_X = 34.0 * ns.get("P64_K")                  # pylon face |X| (43.6)


def to_man(t: trimesh.Trimesh) -> m.Manifold:
    return m.Manifold(m.Mesh(vert_properties=np.asarray(t.vertices, dtype=np.float32),
                             tri_verts=np.asarray(t.faces, dtype=np.uint32)))


def fix_nonmanifold(x: trimesh.Trimesh) -> trimesh.Trimesh:
    """Split the few non-manifold edges where two shell sheets touch along a line (CGAL output)."""
    x = x.copy()
    x.merge_vertices()
    faces = x.faces.copy()
    verts = np.asarray(x.vertices)
    ed: dict = collections.defaultdict(list)
    for fi, f in enumerate(faces):
        for a, b in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])):
            ed[(min(a, b), max(a, b))].append(fi)
    link: dict = collections.defaultdict(set)
    bad: set = set()
    for (a, b), fs in ed.items():
        if len(fs) <= 2:
            continue
        bad.update((a, b))
        ax = verts[b] - verts[a]
        ax /= np.linalg.norm(ax)
        u = np.cross(ax, [0.3, 0.5, 0.8])
        u /= np.linalg.norm(u)
        w = np.cross(ax, u)
        info = []
        for fi in fs:
            f = list(faces[fi])
            o = next(t for t in f if t not in (a, b))
            r = verts[o] - verts[a]
            i = f.index(a)
            info.append((float(np.arctan2(r @ w, r @ u)), fi, f[(i + 1) % 3] == b))
        info.sort()
        n = len(info)
        for off in (0, 1):
            if all(info[(off + 2 * k) % n][2] != info[(off + 2 * k + 1) % n][2]
                   for k in range(n // 2)):
                for k in range(n // 2):
                    p, q = info[(off + 2 * k) % n][1], info[(off + 2 * k + 1) % n][1]
                    link[p].add(q)
                    link[q].add(p)
                break
    vf: dict = collections.defaultdict(list)
    for fi, f in enumerate(faces):
        for v in f:
            if v in bad:
                vf[v].append(fi)
    new_v = list(verts)
    for v, fis in vf.items():
        par = {fi: fi for fi in fis}

        def find(a: int) -> int:
            while par[a] != a:
                par[a] = par[par[a]]
                a = par[a]
            return a

        for fi in fis:
            for w_ in faces[fi]:
                if w_ == v:
                    continue
                fs = ed[(min(v, w_), max(v, w_))]
                if len(fs) == 2:
                    for o in fs:
                        if o != fi and o in par:
                            par[find(fi)] = find(o)
            for o in link.get(fi, ()):
                if o in par:
                    par[find(fi)] = find(o)
        groups: dict = collections.defaultdict(list)
        for fi in fis:
            groups[find(fi)].append(fi)
        for k, g in enumerate(groups.values()):
            if k == 0:
                continue
            nid = len(new_v)
            new_v.append(verts[v])
            for fi in g:
                faces[fi][faces[fi] == v] = nid
    return trimesh.Trimesh(np.array(new_v), faces, process=False)


def xform(t: trimesh.Trimesh, mat: np.ndarray) -> trimesh.Trimesh:
    t = t.copy()
    t.apply_transform(mat)
    return t


def mat4(rows) -> np.ndarray:
    return np.array(rows, dtype=float)


def hull_to_local(side: str) -> np.ndarray:
    """Starboard hull R2 -> local (pylon +X).  Port is mirrored about X in hull first."""
    assert side == "stbd"
    return mat4([[1, 0, 0, WING_TIP_HULL_X + SEAT],
                 [0, 0, -1, hd.SPAR_Z],
                 [0, 1, 0, PIVOT_Z - hd.SPAR_Y],
                 [0, 0, 0, 1]])


def tube(x0: float, length: float, od: float, idia: float, z: float = PIVOT_Z) -> trimesh.Trimesh:
    outer = trimesh.creation.cylinder(radius=od / 2, height=length, sections=96)
    if idia > 0:
        inner = trimesh.creation.cylinder(radius=idia / 2, height=length + 2, sections=96)
        outer = to_trimesh(to_man(outer) - to_man(inner))
    outer = xform(outer, mat4([[0, 0, 1, x0 + length / 2],
                  [0, 1, 0, 0], [-1, 0, 0, z], [0, 0, 0, 1]]))
    return outer


def to_trimesh(mn: m.Manifold) -> trimesh.Trimesh:
    mm = mn.to_mesh()
    return trimesh.Trimesh(np.asarray(mm.vert_properties)[
                           :, :3], np.asarray(mm.tri_verts), process=False)


def rot_x(deg: float, z: float = PIVOT_Z) -> np.ndarray:
    c, s = np.cos(np.radians(deg)), np.sin(np.radians(deg))
    t1 = np.eye(4)
    t1[2, 3] = -z
    r = mat4([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]])
    t2 = np.eye(4)
    t2[2, 3] = z
    return t2 @ r @ t1


def load_parts(pod_path: Path, trunnion_path: Path,
               side: str = "stbd") -> dict[str, trimesh.Trimesh]:
    """Parts in local frame for the starboard-geometry nacelle (pylon +X)."""
    h2l = hull_to_local("stbd")
    parts: dict[str, trimesh.Trimesh] = {}
    parts["pod"] = fix_nonmanifold(trimesh.load(pod_path, force="mesh"))
    cart = trimesh.load(STL / "nacelles/edf_motor_mount_64mm_stage2_stbd.stl", force="mesh")
    parts["cartridge"] = xform(cart, mat4(
        [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, CART_Z0], [0, 0, 0, 1]]))
    for nm in ("throat", "ring"):
        t = trimesh.load(STL / f"nacelles/nozzles/nacelle_nozzle_{nm}_64mm_stbd.stl", force="mesh")
        parts[f"nozzle_{nm}"] = xform(
            t, mat4([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, NOZ_Z0], [0, 0, 0, 1]]))
    tr = trimesh.load(trunnion_path, force="mesh")
    parts["trunnion"] = xform(tr, mat4([[0, 0, 1, TRUNNION_X0], [0, -1, 0, 0], [1, 0, 0, PIVOT_Z],
                                        [0, 0, 0, 1]]))
    # QF2822 can: r 13.9 (dia 27.8), 58 mm body behind each motor plate (plate front Z 42.2 / 115.9,
    # 3 mm thick; REF-EDF-003 dimensions, all VERIFY on a physical unit)
    for nm, zf in (("motor1", 42.2), ("motor2", 115.9)):
        can = trimesh.creation.cylinder(radius=13.9, height=58.0, sections=64)
        parts[nm] = xform(can, mat4([[1, 0, 0, 0], [0, 1, 0, 0], [
                          0, 0, 1, zf + 3.0 + 29.0], [0, 0, 0, 1]]))
    parts["spar"] = tube(TRUNNION_X0, 130.0, SPAR_OD, SPAR_ID)
    wing = trimesh.load(STL / "wings/wing_stbd_s1223_revo.stl", force="mesh")
    parts["wing"] = xform(wing, h2l)
    pin = trimesh.load(STL / "wings/wing_tilt_pinion_stbd.stl", force="mesh")
    parts["pinion"] = xform(pin, h2l)
    return parts


TILTING = ("pod", "cartridge", "motor1", "motor2", "nozzle_throat", "nozzle_ring", "trunnion")
FIXED = ("spar", "wing", "pinion")


def overlap_matrix(man: dict[str, m.Manifold]) -> list[tuple[str, str, float]]:
    out = []
    names = list(man)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            v = (man[a] ^ man[b]).volume()
            out.append((a, b, float(v)))
    return out


def sweep(man: dict[str, m.Manifold], angles) -> list[dict]:
    rows = []
    for ang in angles:
        r = rot_x(ang)
        tilt = {k: man[k].transform(np.asarray(r[:3, :4], dtype=float)) for k in TILTING}
        row = {"deg": float(ang)}
        for a in TILTING:
            for b in FIXED:
                v = float((tilt[a] ^ man[b]).volume())
                if v > 1.0:
                    row[f"{a}|{b}"] = round(v, 1)
        rows.append(row)
    return rows


def raster(man: m.Manifold, grid: dict, fill_holes: bool = False) -> np.ndarray:
    """Boolean occupancy [nx, ny, nz] of a manifold by Z slicing (even-odd fill of each slice)."""
    from PIL import Image, ImageDraw  # noqa: PLC0415

    pitch, x0, y0, z0 = grid["pitch"], grid["x0"], grid["y0"], grid["z0"]
    nx, ny, nz = grid["shape"]
    out = np.zeros((nx, ny, nz), dtype=bool)
    lo, hi = man.bounding_box()[2], man.bounding_box()[5]
    for k in range(nz):
        z = z0 + (k + 0.5) * pitch
        if z < lo or z > hi:
            continue
        polys = man.slice(z).to_polygons()
        if not polys:
            continue
        img = np.zeros((ny, nx), dtype=bool)          # PIL is (row=y, col=x)
        # envelope: convex hull of the slice (the shell skin is not a closed ring)
        if fill_holes:
            from scipy.spatial import ConvexHull  # noqa: PLC0415

            allp = np.vstack(polys)
            hv = allp[ConvexHull(allp).vertices]
            im = Image.new("1", (nx, ny), 0)
            ImageDraw.Draw(im).polygon([((px - x0) / pitch - 0.5, (py - y0) / pitch - 0.5)
                                        for px, py in hv], fill=1)
            img = np.asarray(im, dtype=bool)
        else:
            for poly in polys:
                im = Image.new("1", (nx, ny), 0)
                pts = [((px - x0) / pitch - 0.5, (py - y0) / pitch - 0.5) for px, py in poly]
                ImageDraw.Draw(im).polygon(pts, fill=1)
                img = img ^ np.asarray(im, dtype=bool)
        out[:, :, k] = img.T
    return out


def cable_route(man: dict[str, m.Manifold], pitch: float = 0.75) -> dict:
    """Clearance search for the bundle from the spar-bore mouth to the ESC disconnect bay."""
    from scipy import ndimage  # noqa: PLC0415
    from skimage.graph import MCP_Geometric  # noqa: PLC0415

    x0, x1, y0, y1, z0, z1 = -50.0, 60.0, -56.0, 56.0, 0.0, 212.0
    shape = (int((x1 - x0) / pitch), int((y1 - y0) / pitch), int((z1 - z0) / pitch))
    grid = {"pitch": pitch, "x0": x0, "y0": y0, "z0": z0, "shape": shape}
    solid = np.zeros(shape, dtype=bool)
    for k in man:
        solid |= raster(man[k], grid)
    xs = x0 + (np.arange(shape[0]) + 0.5) * pitch
    ys = y0 + (np.arange(shape[1]) + 0.5) * pitch
    zs = z0 + (np.arange(shape[2]) + 0.5) * pitch
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    # allowed region: the pod's outer envelope (outer rings of its slices), the gap slab between the
    # pylon face and the wing tip pad, and nothing else; the Ø64 flow bore is
    # air but not a cable route
    env = raster(man["pod"], grid, fill_holes=True)
    gap = (X >= FACE_X - 0.01) & (X <= SEAT) & (np.abs(Y) < 45.0) & (Z > 30.0) & (Z < 140.0)
    bore = np.hypot(X, Y) < 32.0
    out: dict = {"pitch": pitch}
    for label, allowed in (("pod interior only", env & ~bore),
                           ("pod interior + gap slab", (env | gap) & ~bore)):
        free = allowed & ~solid
        clr = ndimage.distance_transform_edt(free) * pitch
        # start: bore mouth, on the spar axis just inside the tube; end: bay centre
        si = (int((TRUNNION_X0 + 0.5 - x0) / pitch),
              int((0.0 - y0) / pitch), int((PIVOT_Z - z0) / pitch))
        ei = (int((FACE_X + 0.5 - x0) / pitch), int((0.0 - y0) / pitch), int((DISC_Z - z0) / pitch))
        ax_free = 0.0                       # free axial depth beyond the bore mouth
        while ax_free < 10.0 and not solid[int((TRUNNION_X0 - ax_free - 0.1 - x0) / pitch),
                                           int((0.0 - y0) / pitch), int((PIVOT_Z - z0) / pitch)]:
            ax_free += pitch
        routes: list = []
        res: dict = {"mouth_axial_free_mm": round(ax_free, 2),
                     "start_clearance": round(float(clr[si]), 2),
                     "end_clearance": round(float(clr[ei]), 2), "routes": routes}
        for r_req in (BUNDLE_D / 2, BUNDLE_D / 2 + CLEARANCE):
            cost = np.where(clr >= r_req, 1.0, np.inf)
            if not np.isfinite(cost[si]) or not np.isfinite(cost[ei]):
                res["routes"].append({"r_req": round(r_req, 2), "found": False,
                                      "why": "start or end clearance below requirement"})
                continue
            mcp = MCP_Geometric(cost, fully_connected=True)
            costs, _ = mcp.find_costs([si], [ei])
            c_end = costs[ei]
            if not np.isfinite(c_end):
                res["routes"].append({"r_req": round(r_req, 2), "found": False,
                                      "why": "no connected free path"})
                continue
            path = np.array(mcp.traceback(ei))
            pts = np.c_[xs[path[:, 0]], ys[path[:, 1]], zs[path[:, 2]]]
            res["routes"].append({"r_req": round(r_req, 2), "found": True,
                                  "length_mm": round(float(c_end) * pitch, 1),
                                  "min_clearance": round(float(clr[tuple(path.T)].min()), 2),
                                  "path": pts[::8].round(1).tolist()})
        # widest bundle the best-clearance connection could carry (bottleneck): bisect on r
        lo_r, hi_r = 0.0, min(float(clr[si]), float(clr[ei]))
        for _ in range(14):
            mid = 0.5 * (lo_r + hi_r)
            lab, _n = ndimage.label(clr >= mid)
            if lab[si] and lab[si] == lab[ei]:
                lo_r = mid
            else:
                hi_r = mid
        res["max_bundle_radius_that_connects"] = round(lo_r, 2)
        out[label] = res
    return out


def pinion_pocket(man: dict[str, m.Manifold], step: float = 1.0) -> tuple[float, m.Manifold]:
    """Volume of pod material inside the volume the fixed wing pinion sweeps relative to the pod.

    In the pod frame the pinion orbits the tilt axis by -theta; the pod needs a pocket for the union
    of those positions over TILT_MIN..TILT_MAX.  (Ring-gear teeth are a mesh, not a clash.)
    """
    swept = None
    for ang in np.arange(TILT_MIN, TILT_MAX + 0.01, step):
        # pod-frame position of the pinion at tilt ang = rotate by -ang about the tilt axis
        r = rot_x(-ang)
        pos = man["pinion"].transform(np.asarray(r[:3, :4], dtype=float))
        swept = pos if swept is None else swept + pos
    return float((swept ^ man["pod"]).volume()), swept


def figures(man: dict[str, m.Manifold], swept: m.Manifold, outdir: Path) -> list[Path]:
    import matplotlib  # noqa: PLC0415

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: PLC0415

    outdir.mkdir(parents=True, exist_ok=True)
    cols = {"pod": "k", "cartridge": "tab:blue", "trunnion": "tab:red", "spar": "tab:green",
            "pinion": "m", "wing": "tab:cyan", "nozzle_throat": "tab:orange",
            "nozzle_ring": "tab:brown",
            "motor1": "0.5", "motor2": "0.5"}
    to_xz = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0]], float)     # slice plane Y = const
    to_yz = np.array([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0]], float)     # slice plane X = const
    paths = []
    fig, ax = plt.subplots(1, 3, figsize=(21, 9))
    for k, c in cols.items():
        for poly in man[k].transform(to_xz).slice(0.0).to_polygons():
            for a_ in ax[:2]:
                a_.plot(poly[:, 0], poly[:, 1], c, lw=0.8)
    ax[0].set(xlim=(-50, 62), ylim=(0, 215),
              title="Y = 0 section (X + = pylon/wing side, Z along duct)")
    ax[1].set(xlim=(22, 62), ylim=(40, 140),
              title="Spar-bore mouth and ESC disconnect bay (Y = 0)")
    for poly in swept.transform(to_yz).slice(45.0).to_polygons():
        ax[2].fill(poly[:, 0], poly[:, 1], color="m", alpha=0.35, lw=0)
    for poly in man["pod"].transform(to_yz).slice(45.0).to_polygons():
        ax[2].plot(poly[:, 0], poly[:, 1], "k", lw=0.8)
    ax[2].plot(0, PIVOT_Z, "r+", ms=14)
    ax[2].set(xlim=(-55, 55), ylim=(40, 180),
              title="X = 45 section: pod wall (black) vs pinion sweep (magenta)")
    for a_ in ax:
        a_.set_aspect("equal")
        a_.grid(alpha=0.3)
    f = outdir / "nacelle64_sections.png"
    fig.savefig(f, dpi=75, bbox_inches="tight")
    plt.close(fig)
    paths.append(f)
    return paths


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pod", type=Path, required=True)
    ap.add_argument("--trunnion", type=Path, required=True)
    ap.add_argument("--step", type=float, default=5.0)
    ap.add_argument("--json", type=Path)
    ap.add_argument("--figs", type=Path, help="write section figures to this directory")
    ap.add_argument("--stage", choices=("static", "sweep", "cable", "all"), default="all")
    args = ap.parse_args(argv)

    parts = load_parts(args.pod, args.trunnion)
    man = {k: to_man(v) for k, v in parts.items()}
    print("part status/volume (mm3):")
    for k, v in man.items():
        print(f"  {k:14s} {v.status().name:10s} {v.volume():12.0f}")
    res: dict = {"static": [], "sweep": []}
    if args.stage in ("static", "all"):
        print("\nstatic overlap at tilt 0 (mm3 > 1):")
        for a, b, v in overlap_matrix(man):
            if v > 1.0:
                print(f"  {a:14s} x {b:14s} {v:10.1f}")
                res["static"].append([a, b, round(v, 1)])
        print("\nnearest approach of non-overlapping pairs within 6 mm (mm):")
        res["gap"] = []
        names = list(man)
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                if (man[a] ^ man[b]).volume() > 1.0:
                    continue
                g = float(man[a].min_gap(man[b], 6.0))
                if g < 6.0:
                    print(f"  {a:14s} to {b:14s} {g:7.2f}")
                    res["gap"].append([a, b, round(g, 2)])
    if args.stage in ("sweep", "all"):
        angles = np.arange(TILT_MIN, TILT_MAX + 0.1, args.step)
        print("\ntilt sweep, moving group vs fixed group (mm3 > 1):")
        res["sweep"] = sweep(man, angles)
        for row in res["sweep"]:
            hits = {k: v for k, v in row.items() if k != "deg"}
            line = ", ".join(f"{k}={v}" for k, v in hits.items()) or "clear"
            print(f"  {row['deg']:6.1f} deg  " + line)
    if args.stage in ("sweep", "all"):
        vol, swept = pinion_pocket(man)
        res["pinion_pocket_mm3"] = round(vol, 1)
        print(f"\npod material inside the volume the wing pinion sweeps over "
              f"{TILT_MIN:+.0f}..{TILT_MAX:+.0f} deg: {vol:.0f} mm3 "
              f"(pinion {man['pinion'].volume():.0f} mm3)")
        if args.figs:
            for f in figures(man, swept, args.figs):
                print("figure:", f)
    if args.stage in ("cable", "all"):
        print("\ncable route (bundle %.2f mm + %.1f mm radial):" % (BUNDLE_D, CLEARANCE))
        res["cable"] = cable_route(man)
        for label, r in res["cable"].items():
            if label == "pitch":
                continue
            print(f"  [{label}] start clr {r['start_clearance']}  end clr {r['end_clearance']}  "
                  f"max connecting bundle radius {r['max_bundle_radius_that_connects']}")
            for q in r["routes"]:
                print("     ", {k: v for k, v in q.items() if k != "path"})
    if args.json:
        args.json.write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
