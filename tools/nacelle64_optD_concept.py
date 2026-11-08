#!/usr/bin/env python3
"""nacelle64_optD_concept.py -- OD-17 option D: tilt joint moved outboard, 4 x 10 AWG routed.

Builds the option-D concept in the nacelle-local frame (stbd, pylon +X): the pod collar boss carried
`--shift` mm outboard, trunnion/spar/wing/pinion moved with it, and the four wires routed from the
spar bore (2 x 2) around a 3 x OD bend, forward in the annulus, fanned out to the disconnect-bay
studs.
Reports each wire's bend radius and exit X, wire-to-wire gaps, wire-vs-wing/pinion contact over the
tilt sweep, and the pod material the wire channels remove; with --render-dir it writes top, bottom,
front and back close-ups at 0 and 90 deg tilt (pyvista, off-screen), each wire in its own colour.
Brief: docs/NACELLE_64MM_POWER_CROSSING_BRIEF.md.  Wire OD 5.5 mm is ASSUMED (SPAR-20-WIREOD).

Usage:  python3 tools/nacelle64_optD_concept.py --pod POD.stl --trunnion TRUNNION.stl
            [--shift 23] [--render-dir docs/figures]

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic, Claude Opus 5.5) under the author's direction, 2026-11-08.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import manifold3d as m
import numpy as np
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nacelle64_assembly_check as a  # noqa: E402


PZ, X0, DZ = a.PIVOT_Z, a.TRUNNION_X0, a.DISC_Z
# assumed 10 AWG OD; 3 x OD minimum bend (repo citation)
WIRE_D, R_MIN = 5.5, 3 * 5.5
OFFS = [(-2.75, -2.75), (2.75, -2.75), (-2.75, 2.75), (2.75, 2.75)]   # 2 x 2 in the spar bore
STUD_Y = {(-2.75, -2.75): -3.75, (2.75, -2.75): 3.75, (-2.75, 2.75): -11.25, (2.75, 2.75): 11.25}
NAMES = {(-2.75, -2.75): 'ESC A +', (-2.75, 2.75): 'ESC A -',
         (2.75, -2.75): 'ESC B +', (2.75, 2.75): 'ESC B -'}
COLORS = {'ESC A +': 'red', 'ESC A -': 'royalblue', 'ESC B +': 'orange', 'ESC B -': 'magenta'}
X_LUG = 40.5


def shift(t, s):
    return a.xform(t, a.mat4([[1, 0, 0, s], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]))


def pod_side_path(off, S):
    """Polyline in the pod frame (tilt 0) from inside the spar mouth to the stud."""
    y0, z0 = off
    xm = X0 + S
    zc = PZ - 2.75 - R_MIN
    R = (PZ + z0) - zc
    pts = [(xm + 6, y0, PZ + z0)]
    for ph in np.linspace(0, np.pi / 2, 19):
        pts.append((xm - R * np.sin(ph), y0, zc + R * np.cos(ph)))
    xe = xm - R
    ys = STUD_Y[off]
    zmid = 0.5 * (zc + DZ + 9)
    for f in np.linspace(0, 1, 9)[1:]:           # run forward, fanning out in Y to the studs
        pts.append((xe, y0 + (ys - y0) * f, zc + (zmid - zc) * f))
    for f in np.linspace(0, 1, 9)[1:]:           # then ease in X to the lug plane
        pts.append((xe + (X_LUG - xe) * f, ys, zmid + (DZ + 9 - zmid) * f))
    pts.append((X_LUG, ys, DZ + 4.5))           # lug barrel above the stud
    pts.append((X_LUG, ys, DZ))
    return np.array(pts), R, xe


def spar_side_path(off, S, tilt_deg, far=70.0):
    """Inside the spar: fixed (wing) end at xm+far, pod end at xm+6 rotated with the pod."""
    xm = X0 + S
    y0, z0 = off
    pts = []
    for f in np.linspace(0, 1, 25):
        x = xm + far - (far - 6) * f
        th = np.radians(-tilt_deg * f)            # tilt_matrix(t) = rot_x(-t) about the axis
        c, s_ = np.cos(th), np.sin(th)
        y = c * y0 - s_ * z0
        z = s_ * y0 + c * z0
        pts.append((x, y, PZ + z))
    return np.array(pts)


def tube(pts, d):
    """Tube mesh (trimesh) along a polyline, as a union of capsules."""
    parts = []
    for p, q in zip(pts[:-1], pts[1:]):
        v = q - p
        L = np.linalg.norm(v)
        if L < 1e-6:
            continue
        c = trimesh.creation.cylinder(radius=d / 2, segment=[p, q], sections=16)
        parts.append(c)
        parts.append(trimesh.creation.icosphere(subdivisions=1, radius=d / 2).apply_translation(q))
    return trimesh.util.concatenate(parts)


def build(S, pod_path, trunnion_path):
    parts = a.load_parts(pod_path, trunnion_path)
    for k in ('trunnion', 'spar', 'wing', 'pinion'):
        parts[k] = shift(parts[k], S)
    # pod extension: collar boss carried S further outboard (concept: annulus r 19.05..27)
    boss = m.Manifold.cylinder(S + 4, 27.0, 27.0, 96).rotate([0, 90, 0]).translate([47.8, 0, PZ]) \
        - m.Manifold.cylinder(S + 6, 19.05, 19.05, 96).rotate([0, 90, 0]).translate([46.8, 0, PZ])
    return parts, boss


def report(SH: float, parts: dict, boss: m.Manifold) -> None:
    man = {k: a.to_man(v) for k, v in parts.items()}
    pod = man["pod"] + boss
    print(f"shift {a.inch(SH)}; spar mouth X {a.inch(X0 + SH)}")
    wires = {}
    for off in OFFS:
        pts, R, xe = pod_side_path(off, SH)
        flag = "  INSIDE the duct wall" if xe - WIRE_D / 2 < 34.5 else ""
        print(f"  {NAMES[off]:8s} bend R {a.inch(R)}, leaves the bend at X {a.inch(xe)}{flag}")
        wires[NAMES[off]] = a.to_man(tube(pts, WIRE_D))
    for n, w in wires.items():
        print(f"  {n:8s} pod material on its path (channel): {a.cu_in(float((w ^ pod).volume()))}")
    names = list(wires)
    for i in range(4):
        for j in range(i + 1, 4):
            v = float((wires[names[i]] ^ wires[names[j]]).volume())
            g = float(wires[names[i]].min_gap(wires[names[j]], 5))
            print(f"  {names[i]} / {names[j]}: overlap {a.cu_in(v)}, gap {a.inch(g)}")
    worst = 0.0
    for t in np.arange(a.TILT_MIN, a.TILT_MAX + 0.1, 5.0):
        T = np.asarray(a.tilt_matrix(t)[:3, :4], float)
        for w in wires.values():
            wt = w.transform(T)
            worst = max(worst, float((wt ^ man["pinion"]).volume()
                                     ) + float((wt ^ man["wing"]).volume()))
    print(f"  wires vs wing + pinion over the tilt sweep, worst: {a.cu_in(worst)}")


def render_views(SH: float, parts: dict, boss: m.Manifold, outdir: Path) -> None:
    import pyvista as pv  # noqa: PLC0415

    pv.OFF_SCREEN = True

    man = {k: a.to_man(v) for k, v in parts.items()}
    cut = None
    paths = {}
    for off in OFFS:
        pts, R, xe = pod_side_path(off, SH)
        paths[NAMES[off]] = pts
        c = a.to_man(tube(pts, WIRE_D + 1.0))
        cut = c if cut is None else cut + c
    pod_d = (man['pod'] + boss) - cut
    print('channel material removed', a.cu_in(float((man['pod'] + boss).volume() - pod_d.volume())))
    studs = trimesh.util.concatenate([trimesh.creation.cylinder(
        radius=1.5, segment=[[37.6 - 3.5, y, a.DISC_Z], [a.FACE_X + 1, y, a.DISC_Z]])
                                      for y in (-11.25, -3.75, 3.75, 11.25)])

    def pvmesh(t):
        if isinstance(t, m.Manifold):
            t = a.to_trimesh(t)
        return pv.wrap(trimesh.Trimesh(t.vertices, t.faces, process=False))

    def scene(tilt):
        T = a.tilt_matrix(tilt)
        tilting = {'pod': a.to_trimesh(
            pod_d), 'cartridge': parts['cartridge'], 'trunnion': parts['trunnion'], 'studs': studs}
        items = []
        style = {'pod': ('lightgray', 0.22), 'cartridge': ('steelblue', 0.25),
                 'trunnion': ('dimgray', 0.55), 'studs': ('gold', 1.0),
                 'spar': ('darkslategray', 0.35), 'wing': ('powderblue', 0.45),
                 'pinion': ('saddlebrown', 1.0)}
        for k, t in tilting.items():
            tt = t.copy()
            tt.apply_transform(T)
            items.append((pvmesh(tt), *style[k]))
        for k in ('spar', 'wing', 'pinion'):
            items.append((pvmesh(parts[k]), *style[k]))
        wires = []
        for off in OFFS:
            n = NAMES[off]
            pp = paths[n]
            pp = (T @ np.c_[pp, np.ones(len(pp))].T).T[:, :3]
            sp = spar_side_path(off, SH, tilt)
            wires.append((pv.Spline(np.vstack([sp, pp]), 400).tube(
                radius=WIRE_D / 2, n_sides=16), COLORS[n], n))
        return items, wires

    VIEWS = {'top': ((0, -1, 0), (0, 0, -1)), 'bottom': ((0, 1, 0), (0, 0, -1)),
             'front': ((0, 0, -1), (0, -1, 0)), 'back': ((0, 0, 1), (0, -1, 0))}
    for tilt, label in ((0, 'HORIZONTAL (cruise, 0 deg tilt)'),
                        (90, 'VERTICAL (hover, 90 deg tilt)')):
        items, wires = scene(tilt)
        focus = np.array([52.0, 0.0, 92.0])
        p = pv.Plotter(off_screen=True, shape=(2, 2), window_size=(1800, 1500), border=False)
        for i, (vname, (d, up)) in enumerate(VIEWS.items()):
            p.subplot(i // 2, i % 2)
            for mesh, col, op in items:
                p.add_mesh(mesh, color=col, opacity=op, smooth_shading=True)
            for mesh, col, n in wires:
                p.add_mesh(mesh, color=col, smooth_shading=True)
            cap = {'top': 'TOP: looking down; nose up the page; wing tip on the left',
                   'bottom': 'BOTTOM: looking up; nose up the page; wing tip on the right',
                   'front': 'FRONT: looking aft from ahead; up is up; wing tip on the left',
                   'back': 'BACK: looking forward from behind; up is up; wing tip on the right',
                   }[vname]
            p.add_text(cap, font_size=11, position='upper_left')
            p.add_text(f'nacelle {label}; window ~3.5 in (88 mm) tall',
                       font_size=9, position='lower_left')
            p.camera.focal_point = focus
            p.camera.position = focus + 400 * np.array(d, float)
            p.camera.up = up
            p.enable_parallel_projection()
            p.camera.parallel_scale = 44
            if i == 0:
                p.add_legend([(n, c) for _, c, n in wires]
                             + [('studs (bay)', 'gold'), ('pinion (wing-fixed)', 'saddlebrown')],
                             bcolor='white', size=(0.24, 0.2), loc='lower right')
        name = "horizontal" if tilt == 0 else "vertical"
        p.screenshot(str(outdir / f"nacelle64_od17_optD_{name}.png"))
        p.close()
        print('rendered', tilt)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], epilog=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pod", type=Path, required=True)
    ap.add_argument("--trunnion", type=Path, required=True)
    ap.add_argument("--shift", type=float, default=23.0, help="joint shift outboard, mm")
    ap.add_argument("--render-dir", type=Path)
    args = ap.parse_args(argv)
    parts, boss = build(args.shift, args.pod, args.trunnion)
    report(args.shift, parts, boss)
    if args.render_dir:
        args.render_dir.mkdir(parents=True, exist_ok=True)
        render_views(args.shift, parts, boss, args.render_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
