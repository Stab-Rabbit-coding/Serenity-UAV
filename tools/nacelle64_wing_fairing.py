#!/usr/bin/env python3
"""nacelle64_wing_fairing.py -- OD-17 option D: the wing-fixed aft fairing and rounded end plate.

Builds the published part decided by the owner on 2026-11-11
(docs/NACELLE_64MM_POWER_CROSSING_BRIEF.md,
"Option D with an aft fairing behind the collar" and "Junction CFD"):

  * a wing-fixed fairing BEHIND the rotating collar (the collar is the section's round nose); its
    section is the NACA 4-digit symmetric tail from the collar line back to the wing trailing-edge
    line, which is measured on the wing mesh and extended outboard;
  * a rounded end plate where the fairing meets the wing tip: 0.24 in (6 mm) convex rounding, a
    0.04 in (1 mm) wall, then a 0.24 in (6 mm) concave fillet that ends tangent to the wing
    (the case that CFD showed 14 % less drag than the 1.50 in glove,
    tools/od17_junction_cfd/geom.py);
  * the wing's own 22.8 deg trailing-edge taper is kept (owner, 2026-11-11).

Built in the nacelle-local frame of nacelle64_assembly_check.py (stbd, pylon +X), then written in
the
hull frame (R2) for both sides (port = X mirror), next to the wing STLs.  The part is bonded to the
wing; it is cut away from the wing mesh so the two never interpenetrate.

Printable-wall deviation from the CFD shape (recorded in the brief and WBS, OD17-FAIR-WALL): the CFD
body had zero wall where the fairing meets the collar bore (outer half-thickness equal to the bore
radius).  AGENTS.md section 7 requires a 2.0 mm minimum wall, so the outer half-thickness at the
tilt axis here is bore radius + 0.079 in (2.0 mm), and the trailing edge is truncated at 0.079 in
(2.0 mm).  The section is otherwise the CFD shape.

Usage:  python3 tools/nacelle64_wing_fairing.py [--write] [--json OUT.json]
        (reads the published wing, pinion STLs; --write writes
        airframe/stls/wings/wing_tip_fairing_*.stl)

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic) under the author's direction, 2026-11-11; the outline, the
NACA
         tail and the end-plate profile follow tools/nacelle64_optD_aft_fairing.py and
         tools/od17_junction_cfd/geom.py (same author and AI).
Sources: NACA 4-digit thickness distribution (Abbott and von Doenhoff, Theory of Wing Sections,
         eq. 6.1 form, as already used by the two tools above); material density from
         tools/sls_materials.py (3D Systems DuraForm PA CF, 3DS-30108A, ASTM D792) [REF-MAT-015].
License: CERN-OHL-W-2.0 -- see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import manifold3d as m
import numpy as np
import trimesh
from shapely.geometry import LineString, Polygon

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nacelle64_assembly_check as a  # noqa: E402
import sls_materials as sm  # noqa: E402

PZ = a.PIVOT_Z
R_COL = 27.0                    # collar boss radius (COLLAR_OD / 2)
CLR = 1.0                       # running clearance, collar to fairing bore
WALL = 2.0                      # AGENTS.md section 7 minimum wall
R_BORE = R_COL + CLR            # 28.0
R_OUT = R_BORE + WALL           # 30.0: outer half-thickness at the tilt axis
X0F = 52.8                      # 1.0 mm outboard of the pod's collar flare (pod X <= 51.8)
XA = a.SEAT + 2.0               # wing-tip pad face + 2 mm: the end plate starts here
R1 = R2 = 6.0                   # convex rounding / concave fillet
WALL_EP = 1.0                   # near-vertical wall between them
DMAX = 16.4                     # offset between fairing and wing outlines at the end plate
# The fillet stops at 94 % of the way (0.04 in (1 mm) of lip left), not on the wing surface:
# a tangent toe is a zero-thickness contact line.
FILLET_TOE = 0.94
SPAN = R1 + WALL_EP + R2
NS = 90                         # points per half-ring
RHO = sm.rho_g_mm3(sm.PA_CF)    # g/mm^3
YZ = np.array([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0]], float)


def naca_half(xc: Any, t: float) -> Any:
    """NACA 4-digit half-thickness / chord at x/c, for thickness ratio t."""
    return 5 * t * (0.2969 * np.sqrt(xc) - 0.1260 * xc - 0.3516 * xc ** 2 + 0.2843 * xc ** 3
                    - 0.1036 * xc ** 4)


class Builder:
    def __init__(self, wing: m.Manifold, pinion: m.Manifold):
        self.wing, self.pinion = wing, pinion
        self.s = 0.5 * (1 - np.cos(np.linspace(0, np.pi, NS)))
        x1, x2 = 90.0, 150.0
        self.te_k = (self._te_at(x2) - self._te_at(x1)) / (x2 - x1)
        self.te_z1 = self._te_at(x1)

    def _te_at(self, x: float) -> float:
        polys = self.wing.transform(YZ).slice(float(x)).to_polygons()
        if not polys:
            raise SystemExit(f"wing has no section at X {x} mm")
        return max(float(np.max(np.asarray(p)[:, 1])) for p in polys)

    def z_te(self, x: float) -> float:
        """Trailing-edge line of the wing, measured on the mesh, extended outboard."""
        return self.te_z1 + self.te_k * (x - 90.0)

    def outline(self, x: float):
        """(z, y_low, y_high) of the fairing section at span station x."""
        zte = self.z_te(x)
        c = (zte - PZ) / 0.70                       # chord: the collar line is x/c = 0.30
        t = 2 * R_OUT / c / (2 * naca_half(0.30, 1.0))
        z = PZ + self.s * (zte - PZ)
        yh = np.maximum(naca_half(0.30 + (z - PZ) / c, t) * c, WALL / 2)   # 2 mm TE truncation
        return z, -yh, yh

    def wing_outline(self, x: float):
        g: Any = None
        for p in self.wing.transform(YZ).slice(float(x)).to_polygons():
            pg = Polygon(p).buffer(0)
            g = pg if g is None else g.symmetric_difference(pg)
        zmin, zmax = g.bounds[1], g.bounds[3]
        z = zmin + 0.2 + self.s * (zmax - zmin - 0.4)
        up, lo = [], []
        for zz in z:
            seg = g.intersection(LineString([(-80, zz), (80, zz)]))
            b = seg.bounds if not seg.is_empty else (0.0, 0.0, 0.0, 0.0)
            up.append(b[0])
            lo.append(b[2])
        return z, np.array(up), np.array(lo)

    @staticmethod
    def ep_frac(sv: float) -> float:
        """Offset fraction (0 fairing outline, 1 wing) at distance sv along the end plate."""
        if sv <= R1:
            dlt = R1 - np.sqrt(max(R1 ** 2 - sv ** 2, 0.0))
        elif sv <= R1 + WALL_EP:
            dlt = R1 + (DMAX - R1 - R2) * (sv - R1) / WALL_EP
        else:
            q = sv - R1 - WALL_EP
            dlt = DMAX - R2 + np.sqrt(max(R2 ** 2 - (R2 - q) ** 2, 0.0))
        return min(dlt / DMAX, FILLET_TOE)

    def loft(self) -> m.Manifold:
        xs_gap = list(np.linspace(X0F, XA, 12))
        sv = np.r_[np.linspace(0, R1, 10), np.linspace(R1 + 0.1, R1 + WALL_EP, 4),
                   np.linspace(R1 + WALL_EP + 0.1, SPAN, 10)]
        xs = xs_gap + list(XA + sv[1:])
        fs = [0.0] * len(xs_gap) + [self.ep_frac(v) for v in sv[1:]]
        za, ua, la = self.outline(XA)
        zb, ub, lb = self.wing_outline(XA + SPAN)
        rings = []
        for x, f in zip(xs, fs):
            if x <= XA:
                z, u, lo = self.outline(x)
            else:
                z = (1 - f) * za + f * zb
                u = (1 - f) * ua + f * ub
                lo = (1 - f) * la + f * lb
            rings.append(np.vstack([np.c_[np.full(NS, x), u, z],
                                    np.c_[np.full(NS, x), lo, z][::-1][1:-1]]))
        n = len(rings[0])
        verts = np.vstack(rings)
        faces = []
        for i in range(len(rings) - 1):
            for j in range(n):
                a0, a1 = i * n + j, i * n + (j + 1) % n
                b0, b1 = a0 + n, a1 + n
                faces += [[a0, b0, b1], [a0, b1, a1]]
        for i, rev in ((0, True), (len(rings) - 1, False)):
            cid = len(verts)
            verts = np.vstack([verts, rings[i].mean(axis=0)])
            for j in range(n):
                p_, q_ = i * n + j, i * n + (j + 1) % n
                faces.append([cid, q_, p_] if rev else [cid, p_, q_])
        mesh = trimesh.Trimesh(verts, faces, process=True)
        mesh.fix_normals()
        return a.to_man(mesh)

    def part(self) -> m.Manifold:
        body = self.loft()
        x_hi = XA + SPAN + 2.0
        bore = m.Manifold.cylinder(x_hi - X0F + 4, R_BORE, R_BORE, 160).rotate(
            [0, 90, 0]).translate([X0F - 2, 0, PZ])
        pc = self.pinion.bounding_box()
        cy, cz = 0.5 * (pc[1] + pc[4]), 0.5 * (pc[2] + pc[5])
        pocket = m.Manifold.cylinder(x_hi - X0F + 4, 7.2, 7.2, 48).rotate(
            [0, 90, 0]).translate([X0F - 2, cy, cz])
        return body - bore - pocket - self.wing


def to_hull(t: trimesh.Trimesh, side: str) -> trimesh.Trimesh:
    """Local (stbd, pylon +X) -> hull R2; the port part is the X mirror of the stbd one."""
    out = t.copy()
    out.apply_transform(np.linalg.inv(a.hull_to_local("stbd")))
    if side == "port":
        out.apply_transform(np.diag([-1.0, 1, 1, 1]))  # trimesh flips a mirror's winding itself
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="write the two hull-frame STLs")
    ap.add_argument("--json", type=Path)
    args = ap.parse_args(argv)

    h2l = a.hull_to_local("stbd")

    def load(name: str) -> m.Manifold:
        mesh_in: Any = trimesh.load(a.STL / name, force="mesh")
        return a.to_man(a.xform(mesh_in, h2l))

    wing = load("wings/wing_stbd_s1223_revo.stl")
    pin = load("wings/wing_tilt_pinion_stbd.stl")
    bld = Builder(wing, pin)
    part = bld.part()
    mesh = a.to_trimesh(part)
    vol = float(part.volume())
    res = {
        "status": part.status().name, "watertight": bool(mesh.is_watertight),
        "volume_mm3": round(vol, 1), "mass_g": round(vol * RHO, 2),
        "te_slope": round(bld.te_k, 4), "te_z_at_x90_mm": round(bld.te_z1, 2),
        "x_range_mm": [round(float(mesh.bounds[0, 0]), 2), round(float(mesh.bounds[1, 0]), 2)],
        "wall_mm": WALL, "bore_radius_mm": R_BORE, "outer_half_thickness_mm": R_OUT,
        "overlap_with_wing_mm3": round(float((part ^ wing).volume()), 2),
        "overlap_with_pinion_mm3": round(float((part ^ pin).volume()), 2),
    }
    print(f"fairing + end plate: {part.status().name}, watertight {mesh.is_watertight}, "
          f"{a.cu_in(vol)} = {vol * RHO / 453.592:.3f} lbm ({vol * RHO:.1f} g) solid PA CF "
          f"[REF-MAT-015]; X {a.inch(res['x_range_mm'][0])} to {a.inch(res['x_range_mm'][1])}")
    print(f"  TE line slope {bld.te_k:.4f} (measured on the wing mesh); "
          f"bore {a.inch(R_BORE)} radius, "
          f"outer half-thickness at the axis {a.inch(R_OUT)}; wing overlap "
          f"{a.cu_in(res['overlap_with_wing_mm3'])}, pinion overlap "
          f"{a.cu_in(res['overlap_with_pinion_mm3'])}")
    if args.write:
        for side in ("stbd", "port"):
            h = to_hull(mesh, side)
            f = a.STL / f"wings/wing_tip_fairing_{side}.stl"
            h.export(f)
            print("wrote", f.relative_to(a.ROOT),
                  f"({len(h.faces)} faces, watertight {h.is_watertight}, "
                  f"volume {h.volume:.1f} mm3)")
    if args.json:
        args.json.write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
