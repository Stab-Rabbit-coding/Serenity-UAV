#!/usr/bin/env python3
"""nacelle64_optD_aft_fairing.py -- OD-17 option D: wing-fixed fairing behind the rotating collar.

Owner direction 2026-11-11: fairing behind the collar, trailing edge on the line of the wing's
trailing edge, thickened to the best shape for airflow.  Section = NACA 4-digit symmetric tail from
its maximum thickness (x/c 0.30, on the tilt axis, half-thickness = collar radius + 1 mm) back to
the wing TE line (measured on the wing mesh, extended outboard); the rotating collar is the nose.
TE truncated at 2 mm (AGENTS.md section 7).  Lofted from X 49 mm (1 mm off the pod's inboard face,
a gap that tilting about the spanwise axis cannot change) into the wing's full-chord section.
Reports volume/mass, t/c and fineness, and clearance to every tilting part over -5..135 deg.
SUPERSEDED for the published part by tools/nacelle64_wing_fairing.py (printable wall, end plate);
kept to reproduce the brief's figures.  Run it only on pod/trunnion renders made AFTER the joint
shift (P64_JOINT_SHIFT) landed: SH is 0 because the shift is already in them.
Concept geometry for the decision brief (docs/NACELLE_64MM_POWER_CROSSING_BRIEF.md).

Usage:  python3 tools/nacelle64_optD_aft_fairing.py POD.stl TRUNNION.stl OUT_FAIRING.stl

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic, Claude Opus 5.5) under the author's direction, 2026-11-11.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
import nacelle64_optD_concept as d
import nacelle64_assembly_check as a
import sys
import numpy as np
import trimesh
import sls_materials as sm
import manifold3d as m
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
POD, TRN, OUT = sys.argv[1:4]
SH = 0.0                                      # the 23 mm joint shift is in the pod SCAD and checker
PZ = a.PIVOT_Z
R_COL, CLR = 27.0, 1.0
RHO = sm.rho_g_mm3(sm.PA_CF)                  # g/mm^3, datasheet solid density (single source)
X0F = 49.0                                    # 0.04 in (1 mm) off the pod's inboard face
parts, boss = d.build(SH, POD, TRN)
X_TIP = float(parts['wing'].bounds[0, 0])     # 79.3
X1F = X_TIP + 7.0                             # into the wing's full-chord section for the bond


def z_te(x):                                  # trailing-edge line of the wing, extended outboard
    return 176.0 + 0.42 * (x - 84.3)          # measured: 176.0 @ 84.3, 180.2 @ 94.3, 186.5 @ 109.3


def naca_half(xc, t):
    return 5 * t * (0.2969 * np.sqrt(xc) - 0.1260 * xc - 0.3516 *
                    xc ** 2 + 0.2843 * xc ** 3 - 0.1036 * xc ** 4)


def section(x, n=60):
    """Aft fairing section in (Y, Z): NACA 00xx from its max thickness (x/c 0.30, at the tilt axis,
    half-thickness = collar radius + clearance) back to the wing TE line; TE truncated at
    0.08 in (2 mm)."""
    zte = z_te(x)
    c = (zte - PZ) / 0.70
    # scale so half-thickness at 0.3c = 28
    t = 2 * (R_COL + CLR) / c / (2 * naca_half(0.30, 1.0) / 1.0)
    xs = np.linspace(0.30, 1.0, n)
    yh = naca_half(xs, t) * c
    keep = yh >= 1.0
    xs, yh = xs[keep], yh[keep]
    z = PZ + (xs - 0.30) * c
    top = np.c_[-yh, z]                       # Y negative = up (local Y = down in flight)
    bot = np.c_[yh, z][::-1]
    return np.vstack([top, bot]), c, t, z[-1]


# loft the sections into a closed mesh
xs = np.linspace(X0F, X1F, 9)
rings = []
for x in xs:
    sec, c, t, zend = section(x)
    rings.append(np.c_[np.full(len(sec), x), sec])
# each ring is [top half, bottom half]; resample the halves separately so ring index j means the
# same chord fraction at every station
NH = min(len(r) // 2 for r in rings)


def _half(h):
    return h[np.linspace(0, len(h) - 1, NH).round().astype(int)]


rings = [np.vstack([_half(r[:len(r) // 2]), _half(r[len(r) // 2:])]) for r in rings]
N = len(rings[0])
V = np.vstack(rings)
F = []
for i in range(len(rings) - 1):
    for j in range(N):
        a0, a1 = i * N + j, i * N + (j + 1) % N
        b0, b1 = (i + 1) * N + j, (i + 1) * N + (j + 1) % N
        F += [[a0, b0, b1], [a0, b1, a1]]
# caps: index them against V before the mesh is built (process=True renumbers vertices)
for i, rev in ((0, True), (len(rings) - 1, False)):
    cid = len(V)
    V = np.vstack([V, rings[i].mean(axis=0)])
    for j in range(N):
        p, q = i * N + j, i * N + (j + 1) % N
        F.append([cid, q, p] if rev else [cid, p, q])
mesh = trimesh.Trimesh(V, F, process=True)
mesh.fix_normals()
fair = a.to_man(mesh)
print('loft status', fair.status().name, 'volume', a.cu_in(float(fair.volume())))
bore = m.Manifold.cylinder(X1F - X0F + 4, R_COL + CLR, R_COL + CLR,
                           160).rotate([0, 90, 0]).translate([X0F - 2, 0, PZ])
pin = parts['pinion']
pc = pin.bounds.mean(axis=0)
pocket = m.Manifold.cylinder(X1F - X0F + 4, 7.2, 7.2,
                             48).rotate([0, 90, 0]).translate([X0F - 2, pc[1], pc[2]])
step = m.Manifold.cylinder(52.8 + 1.0 - (X0F - 2), 31.0, 31.0,
                           160).rotate([0, 90, 0]).translate([X0F - 2, 0, PZ])
fair = fair - bore - pocket - step   # clears the pod's own collar (X <= 51.8 mm within r 30 mm)
print('fairing (solid) after the collar bore and pinion pocket:', a.cu_in(float(fair.volume())),
      f'= {fair.volume() * RHO / 453.6:.3f} lbm ({fair.volume() * RHO:.1f} g) PA CF solid')
for x in (X0F, X_TIP):
    sec, c, t, zend = section(x)
    print(f'  at X {a.inch(x)}: full section chord {a.inch(c)}, t/c {t:.2f}, '
          f'max thickness {a.inch(2 * (R_COL + CLR))}, fineness {c / (2 * (R_COL + CLR)):.2f}, '
          f'LE (collar front) Z {a.inch(PZ - 0.3 * c)}, TE Z {a.inch(z_te(x))}')
# interference: fairing (fixed) vs everything that tilts, over the sweep;
# vs wing-fixed parts at rest
man = {k: a.to_man(v) for k, v in parts.items()}
pod = man['pod'] + boss
worst: dict[str, float] = {}
for tdeg in np.arange(a.TILT_MIN, a.TILT_MAX + 0.1, 5.0):
    T = np.asarray(a.tilt_matrix(tdeg)[:3, :4], float)
    for k, mn in (('pod+collar', pod), ('trunnion',
                  man['trunnion']), ('cartridge', man['cartridge'])):
        v = float((mn.transform(T) ^ fair).volume())
        worst[k] = max(worst.get(k, 0.0), v)
print('fairing vs tilting parts over -5..135 deg, worst:',
      {k: round(v, 1) for k, v in worst.items()})
print(
    'fairing vs pinion (wing-fixed):',
    round(
        float(
            (fair ^ man['pinion']).volume()),
        1),
    'mm3; bond overlap with the wing:',
    a.cu_in(
        float(
            (fair ^ man['wing']).volume())))
g = float(fair.min_gap(pod, 3.0))
print('nearest gap fairing to pod+collar at 0 deg:', a.inch(g))
a.to_trimesh(fair).export(OUT)
