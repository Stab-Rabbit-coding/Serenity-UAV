#!/usr/bin/env python3
"""nacelle64_optD_glove.py -- OD-17 option D: spanwise glove blending the aft fairing into the wing.

Morphs the fairing outline at X 81.3 mm (collar-nose circle r 28 mm + NACA tail to the wing TE line)
into the wing's own section at X 81.3 + L with a smoothstep blend (zero spanwise slope at both ends,
so no crease where it starts or ends), lofts it, and reports the largest surface offset, the peak
spanwise surface slope (1.5 x mean for a smoothstep), the material added to the wing and clearance
to the pinion, trunnion and collar.  Concept geometry for docs/NACELLE_64MM_POWER_CROSSING_BRIEF.md.

Usage:  python3 tools/nacelle64_optD_glove.py POD.stl TRUNNION.stl L_MM OUT.stl

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic, Claude Opus 5.5) under the author's direction, 2026-11-11.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""

from __future__ import annotations

import os
import sys

import numpy as np
import trimesh
import sls_materials as sm
from shapely.geometry import LineString, Polygon

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nacelle64_assembly_check as a  # noqa: E402
import nacelle64_optD_concept as d  # noqa: E402

POD, TRN, L, OUT = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
NECK = 28.0
PZ = a.PIVOT_Z


def _z_te(x):
    return 176.0 + 0.42 * (x - 84.3)


def _naca_half(xc, t):
    return 5 * t * (0.2969 * np.sqrt(xc) - 0.1260 * xc - 0.3516 *
                    xc ** 2 + 0.2843 * xc ** 3 - 0.1036 * xc ** 4)


ns = {'z_te': _z_te, 'naca_half': _naca_half}
parts, boss = d.build(23.0, POD, TRN)
wing = a.to_man(parts['wing'])
yz = np.array([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0]], float)
NS = 80
s = 0.5 * (1 - np.cos(np.linspace(0, np.pi, NS)))          # cosine spacing LE->TE


def fairing_outline(x, r=28.0):
    zte = ns['z_te'](x)
    c = (zte - PZ) / 0.70
    t = 2 * r / c / (2 * ns['naca_half'](0.30, 1.0))
    zle = PZ - r
    z = zle + s * (zte - zle)
    yh = np.where(z < PZ, np.sqrt(np.clip(r ** 2 - (z - PZ) ** 2, 0, None)),
                  ns['naca_half'](np.clip((z - PZ) / c + 0.30, 0, 1), t) * c)
    yh = np.maximum(yh, 1.0)
    return z, -yh, yh                                     # Z, upper (Y<0 is up), lower


def wing_outline(x):
    g = None
    for p in wing.transform(yz).slice(float(x)).to_polygons():
        pg = Polygon(p).buffer(0)
        g = pg if g is None else g.symmetric_difference(pg)
    zmin, zmax = g.bounds[1], g.bounds[3]
    z = zmin + 0.3 + s * (zmax - zmin - 0.6)
    up, lo = [], []
    for zz in z:
        seg = g.intersection(LineString([(-60, zz), (60, zz)]))
        ys = np.array(seg.bounds)[[0, 2]] if not seg.is_empty else np.array([0, 0])
        up.append(ys[0])
        lo.append(ys[1])
    return z, np.array(up), np.array(lo)


RHO = sm.rho_g_mm3(sm.PA_CF)                              # g/mm^3, datasheet solid density
XA = 81.3                                                 # inboard of the trunnion flange (X 79.0)
XB = XA + L
za, ua, la = fairing_outline(XA, NECK)
zb, ub, lb = wing_outline(XB)
rings: list = []
X = np.linspace(XA, XB, 21)
prev = None
for x in X:
    tt = (x - XA) / L
    f = 3 * tt ** 2 - 2 * tt ** 3
    z = (1 - f) * za + f * zb
    u = (1 - f) * ua + f * ub
    lo = (1 - f) * la + f * lb
    ring = np.vstack([np.c_[np.full(NS, x), u, z], np.c_[np.full(NS, x), lo, z][::-1][1:-1]])
    rings.append(ring)
dy = np.max(np.abs(np.r_[ua - ub, la - lb]))
print(f'glove L {a.inch(L)}: largest surface offset {a.inch(dy)} per side; '
      f'max spanwise surface slope '
      f'{np.degrees(np.arctan(1.5 * dy / L)):.1f} deg (smoothstep peak = 1.5 x mean)')
N = len(rings[0])
V = np.vstack(rings)
F = []
for i in range(len(rings) - 1):
    for j in range(N):
        a0, a1 = i * N + j, i * N + (j + 1) % N
        b0, b1 = a0 + N, a1 + N
        F += [[a0, b0, b1], [a0, b1, a1]]
for i, rev in ((0, True), (len(rings) - 1, False)):
    cid = len(V)
    V = np.vstack([V, rings[i].mean(axis=0)])
    for j in range(N):
        p_, q_ = i * N + j, i * N + (j + 1) % N
        F.append([cid, q_, p_] if rev else [cid, p_, q_])
gm = trimesh.Trimesh(V, F, process=True)
gm.fix_normals()
glove = a.to_man(gm)
print('glove status', glove.status().name)
add = glove - wing
add_v = float(add.volume())
print('glove material added to the wing:', a.cu_in(add_v),
      f'= {add_v * RHO / 453.6:.3f} lbm ({add_v * RHO:.1f} g) solid')
pinion = a.to_man(parts['pinion'])
print('glove vs pinion', round(float((glove ^ pinion).volume()), 1),
      'mm3; glove vs trunnion/collar at rest',
      round(float((glove ^ (a.to_man(parts['trunnion']) + boss)).volume()), 1))
a.to_trimesh(glove).export(OUT)
