#!/usr/bin/env python3
"""od17_junction_cfd/geom_asbuilt.py -- OD17-FAIR-CFD: the as-built wing-tip fairing assembly as a CFD body.

geom.py's end-plate body is an idealisation: a solid teardrop (round 28 mm nose, NACA tail, zero wall
at the collar) that runs unbroken from the nacelle flank to the wing.  The printed part
(tools/nacelle64_wing_fairing.py) is not that.  It is only the tail aft of the tilt axis, with a 56 mm
(r 28 mm) bore cut through its whole length for the rotating collar.  The collar ends at X 74.8 mm and
the trunnion at 79.0 mm, so from about X 79 mm out to the fairing's end at 94.3 mm the bore is an
OPEN, forward-facing pocket holding only the wing and a spar tube.  This body keeps that:

  * the printed fairing as a solid (Builder.part(): outline, 2 mm wall at the axis, 2 mm trailing-edge
    cut, 94 % fillet toe, bore and pinion pocket cut; no foam cavity, which the airstream cannot see);
  * the collar boss as a solid cylinder, r 28 mm (the 1 mm running gap to the bore is closed: this
    mesh cannot resolve it), X from the nacelle flank to the pod's collar end;
  * the actual trunnion, spar and tilt pinion meshes, and the actual wing.

Same frame, clip (X 40-165 mm) and units as geom.py: nacelle-local frame, written in metres to
S/cfd/asbuilt.stl.  Inputs in S/asm/: pod_s2_default.stl and trunnion.stl (OpenSCAD renders at the
Sprint 2 geometry, as for geom.py).

An earlier version of this file (commit 1ca65a3) built the body from the fairing's outer loft without
the bore.  That put a solid, flat-faced tail block where the real part has an open bore, and gave a
drag about 66 % above the end-plate body that was an artefact of the wrong body.  Corrected 2026-11-12.

Usage:  python3 geom_asbuilt.py S        (then: python3 mkcase.py S asbuilt ; run.sh S/cfd/asbuilt)

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic) under the author's direction, 2026-11-12.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
import os
import sys

import manifold3d as m
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import nacelle64_assembly_check as a  # noqa: E402
import nacelle64_optD_concept as d  # noqa: E402
import nacelle64_wing_fairing as wf  # noqa: E402

if len(sys.argv) != 2:
    sys.exit('usage: geom_asbuilt.py S')
S = sys.argv[1]
X_FLANK = 48.0          # geom.py's X0: the nacelle flank, where the CFD domain starts
h2l = a.hull_to_local('stbd')


def load(name):
    t = trimesh.load(a.STL / name, force='mesh')
    return a.to_man(a.xform(t, h2l))


# the pod, trunnion, spar, pinion and wing exactly as the assembly check places them
parts, _ = d.build(0.0, f'{S}/asm/pod_s2_default.stl', f'{S}/asm/trunnion.stl')
collar_end = float(parts['pod'].bounds[1, 0])            # 74.8: the pod's collar end face
wing = a.to_man(parts['wing'])
pin = load('wings/wing_tilt_pinion_stbd.stl')
fairing = wf.Builder(wing, pin).part()                    # printed outer shape, bore and pocket cut
collar = m.Manifold.cylinder(collar_end - X_FLANK, wf.R_BORE, wf.R_BORE, 160).rotate(
    [0, 90, 0]).translate([X_FLANK, 0, wf.PZ])
solid = collar + fairing + wing
for k in ('trunnion', 'spar', 'pinion'):
    solid = solid + a.to_man(parts[k])
clip = m.Manifold.cube([165.0 - 40.0, 400, 400]).translate([40.0, -200, -100])
body = solid ^ clip
t = a.to_trimesh(body)
print('asbuilt status', body.status().name, 'volume', a.cu_in(float(body.volume())),
      'watertight', t.is_watertight, 'X', t.bounds[:, 0].round(1))
print(f'collar r {wf.R_BORE} mm to X {collar_end:.1f}; trunnion X {parts["trunnion"].bounds[:, 0].round(1)}; '
      f'fairing X {a.to_trimesh(fairing).bounds[:, 0].round(1)}; wing tip face X {a.WING_TIP_FACE:.1f}')
os.makedirs(f'{S}/cfd', exist_ok=True)
t.apply_scale(0.001)
t.export(f'{S}/cfd/asbuilt.stl')
