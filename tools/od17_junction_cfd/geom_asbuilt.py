#!/usr/bin/env python3
"""od17_junction_cfd/geom_asbuilt.py -- OD17-FAIR-CFD: the as-built wing-tip fairing as a CFD body.

geom.py's end-plate body has zero wall where the fairing meets the collar (a 28 mm circle blending
into the NACA tail) and a fillet that runs tangent onto the wing.  The printed part
(tools/nacelle64_wing_fairing.py) differs in three ways the owner asked to have checked (OD-18 item 2,
WBS OD17-FAIR-CFD):

  1. The fairing is only the tail aft of the tilt axis, 30 mm half-thickness at the axis (bore 28 mm
     + 2 mm wall); the front of the section is the rotating collar, radius 27 mm.  The flow therefore
     meets a 3 mm forward-facing step on each side at the axis (1 mm running gap + 2 mm wall).  The
     gap itself is closed here: a 1 mm slot cannot be resolved by this mesh.
  2. The trailing edge is cut at 2 mm (1 mm half-thickness floor).
  3. The end-plate fillet stops at 94 % (FILLET_TOE), leaving a 1 mm lip on the wing.

This builds that body by calling the printed part's own Builder (same outline, end plate and fillet
code), so the CFD body and the part cannot drift apart (OD17-TOOLS-01).  The span window, frame and
units match geom.py: nacelle-local frame, clip X 40-165 mm, written in metres to S/cfd/asbuilt.stl.
Between the nacelle flank (X 48 mm, the domain's slip wall) and the printed part's first station
(X 52.8 mm) the pod's collar flare is represented by carrying the X 52.8 mm section inboard, as
geom.py does for its own body.

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
import nacelle64_wing_fairing as wf  # noqa: E402

if len(sys.argv) != 2:
    sys.exit('usage: geom_asbuilt.py S')
S = sys.argv[1]
X_FLANK = 48.0          # geom.py's X0: the nacelle flank, where the CFD domain starts
h2l = a.hull_to_local('stbd')


def load(name):
    t = trimesh.load(a.STL / name, force='mesh')
    return a.to_man(a.xform(t, h2l))


wing = load('wings/wing_stbd_s1223_revo.stl')
pin = load('wings/wing_tilt_pinion_stbd.stl')
x0f_printed = wf.X0F
wf.X0F = X_FLANK        # carry the first printed section inboard to the flank (see docstring)
envelope = wf.Builder(wing, pin).loft()     # outer surface: no bore, no pocket, no hollow
wf.X0F = x0f_printed
collar = m.Manifold.cylinder(a.SEAT + 0.5 - X_FLANK, wf.R_COL, wf.R_COL, 160).rotate(
    [0, 90, 0]).translate([X_FLANK, 0, wf.PZ])
clip = m.Manifold.cube([165.0 - 40.0, 400, 400]).translate([40.0, -200, -100])
body = (collar + envelope + wing) ^ clip
t = a.to_trimesh(body)
print('asbuilt status', body.status().name, 'volume', a.cu_in(float(body.volume())),
      'watertight', t.is_watertight, 'X', t.bounds[:, 0].round(1))
print(f'collar r {wf.R_COL} mm, fairing half-thickness at the axis {wf.R_OUT} mm '
      f'(step {wf.R_OUT - wf.R_COL:.1f} mm per side), TE floor {wf.WALL / 2} mm half-thickness, '
      f'fillet toe {wf.FILLET_TOE}')
os.makedirs(f'{S}/cfd', exist_ok=True)
t.apply_scale(0.001)
t.export(f'{S}/cfd/asbuilt.stl')
