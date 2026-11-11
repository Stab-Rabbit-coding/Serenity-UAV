#!/usr/bin/env python3
"""od17_junction_cfd/geom.py -- OD-17 fairing-to-wing junction CFD screen. Build the two CFD bodies (1.5 in glove; rounded end plate + fillets) as STL in metres.

Workflow (S = a work directory holding asm/pod_s2_default.stl and asm/trunnion.stl renders):
    python3 geom.py S ; python3 mkcase.py S glove ; python3 mkcase.py S endplate
    run.sh S/cfd/glove ; run.sh S/cfd/endplate ; python3 post.py S glove endplate
Results and limits: docs/NACELLE_64MM_POWER_CROSSING_BRIEF.md, "Junction CFD".

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic, Claude Opus 5.5) under the author's direction, 2026-11-11.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""
import os
import sys

import manifold3d as m
import numpy as np
import trimesh
from shapely.geometry import LineString, Polygon

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import nacelle64_assembly_check as a  # noqa: E402
import nacelle64_optD_concept as d  # noqa: E402
S = sys.argv[1]
PZ = a.PIVOT_Z
parts, boss = d.build(23.0, f'{S}/asm/pod_s2_default.stl', f'{S}/asm/trunnion.stl')
wing = a.to_man(parts['wing'])
yz = np.array([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0]], float)
NS = 90
s = 0.5 * (1 - np.cos(np.linspace(0, np.pi, NS)))
def z_te(x): return 176.0 + 0.42 * (x - 84.3)


def naca_half(xc, t): return 5 * t * (0.2969 * np.sqrt(xc) - 0.1260 *
                                      xc - 0.3516 * xc ** 2 + 0.2843 * xc ** 3 - 0.1036 * xc ** 4)


def fair_outline(x, r=28.0):
    zte = z_te(x)
    c = (zte - PZ) / 0.70
    t = 2 * r / c / (2 * naca_half(0.30, 1.0))
    zle = PZ - r
    z = zle + s * (zte - zle)
    yh = np.where(z < PZ, np.sqrt(np.clip(r ** 2 - (z - PZ) ** 2, 0, None)),
                  naca_half(np.clip((z - PZ) / c + 0.30, 0, 1), t) * c)
    yh = np.maximum(yh, 0.6)
    return z, -yh, yh


def wing_outline(x):
    g = None
    for p in wing.transform(yz).slice(float(x)).to_polygons():
        pg = Polygon(p).buffer(0)
        g = pg if g is None else g.symmetric_difference(pg)
    zmin, zmax = g.bounds[1], g.bounds[3]
    z = zmin + 0.2 + s * (zmax - zmin - 0.4)
    up, lo = [], []
    for zz in z:
        b = g.intersection(LineString([(-60, zz), (60, zz)])).bounds
        up.append(b[0])
        lo.append(b[2])
    return z, np.array(up), np.array(lo)


def loft(xs, fs, XA, XB):
    za, ua, la = fair_outline(XA)
    zb, ub, lb = wing_outline(XB)
    rings = []
    for x, f in zip(xs, fs):
        if x <= XA:
            z, u, lo = fair_outline(x)
        else:
            z = (1 - f) * za + f * zb
            u = (1 - f) * ua + f * ub
            lo = (1 - f) * la + f * lb
        rings.append(np.vstack([np.c_[np.full(NS, x), u, z],
                     np.c_[np.full(NS, x), lo, z][::-1][1:-1]]))
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
    t = trimesh.Trimesh(V, F, process=True)
    t.fix_normals()
    return a.to_man(t)


XA, X0 = 81.3, 48.0
xs_gap = list(np.linspace(X0, XA, 12))
# GLOVE: smoothstep over 38 mm
L = 38.0
xg = np.linspace(XA, XA + L, 25)[1:]
fg = [3 * ((x - XA) / L) ** 2 - 2 * ((x - XA) / L) ** 3 for x in xg]
glove = loft(xs_gap + list(xg), [0] * 12 + fg, XA, XA + L)
# ENDPLATE: convex R1 then near-vertical then concave R2, expressed on the peak offset DMAX
R1 = R2 = 6.0
DMAX = 16.4
SPAN = R1 + 1.0 + R2


def ep_frac(sv):
    if sv <= R1:
        dlt = R1 - np.sqrt(max(R1 ** 2 - sv ** 2, 0.0))
    elif sv <= R1 + 1.0:
        dlt = R1 + (DMAX - R1 - R2) * (sv - R1) / 1.0
    else:
        q = sv - R1 - 1.0
        dlt = DMAX - R2 + np.sqrt(max(R2 ** 2 - (R2 - q) ** 2, 0.0)) if q < R2 else DMAX
        dlt = DMAX - (R2 - np.sqrt(max(R2 ** 2 - q ** 2, 0.0))) if False else DMAX - R2 + (R2 -
                                                                                           np.sqrt(max(R2 ** 2 - q ** 2, 0.0))) * 0 + (np.sqrt(max(0.0, R2 ** 2 - (R2 - q) ** 2)))
    return min(dlt / DMAX, 1.0)


sv = np.r_[np.linspace(0, R1, 10), np.linspace(
    R1 + 0.1, R1 + 1.0, 4), np.linspace(R1 + 1.1, SPAN, 10)]
xe = XA + sv
fe = [ep_frac(v) for v in sv]
endp = loft(xs_gap + list(xe[1:]), [0] * 12 + fe[1:], XA, XA + SPAN)
clip = m.Manifold.cube([165.0 - 40.0, 400, 400]).translate([40.0, -200, -100])
for name, body in (('glove', glove), ('endplate', endp)):
    full = (body + wing) ^ clip
    t = a.to_trimesh(full)
    print(name, 'status', full.status().name, 'volume', a.cu_in(float(full.volume())),
          'watertight', t.is_watertight, 'X', t.bounds[:, 0].round(1))
    t.apply_scale(0.001)
    t.export(f'{S}/cfd/{name}.stl')
print('endplate fraction profile', [round(f, 2) for f in fe])
