#!/usr/bin/env python3
"""
finalize_head_rear.py  —  build the final head and rear 2 mm shells with thin
exterior details filled solid, plus the head starboard parabolic-dish pitot.

    python3 finalize_head_rear.py

Inputs (airframe/blender-scripts/files-hollowed-24in/operands/):
  <part>_shell24_2mm_repaired__outer.stl   clean watertight outer (exterior O)
  <part>_shell24_2mm_repaired__inner.stl   clean 2 mm-eroded inner (original)
  <part>_inner_opened.stl                  voxel morphological-opening of inner
                                           (morph_open_voxel.py) — thin details removed

Per part the subtracted solid is  inner_used = opened INTERSECT original  so the
wall is never thinner than the nominal 2 mm (opening alone can slightly exceed
the original at concave fills).  shell = outer - inner_used  ->  thin exterior
details (antenna spikes, fins, skids, greebles) come out SOLID instead of as
fragile 2 mm voids that snap off and cannot be foam-filled.

HEAD — starboard parabolic dish antenna (hull-frame ~ X-205, Y-260, Z+130):
  * the dish + central spike are forced solid by removing a cylinder of inner
    along the dish axis (DISH_* below);
  * a PITOT bore (1.5 mm) is drilled through the spike tip into the interior;
  * an interior BARB boss (4 mm OD / 2.5 mm ID, with a retention ridge) is added
    in the cavity, coaxial with the bore, for the silicone line to a differential
    airspeed sensor (e.g. MS4525DO / MPXV7002).
Dish geometry was measured on the outer mesh (part-local frame):
  spike tip   T = (117.5, -265.4, 67.8)
  dish base   C = (130.5, -256.8, 72.4)
  axis a (outward, base->tip) = normalize(T - C)

All booleans use the manifold3d engine (guaranteed 2-manifold watertight).

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0  —  creativecommons.org/licenses/by/4.0
"""

import os

import numpy as np
import trimesh

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "files-hollowed-24in")
PARTS = os.path.join(OUT, "operands")

ENG = "manifold"


def diff(a, b):
    return trimesh.boolean.difference([a, b], engine=ENG)


def union(a, b):
    return trimesh.boolean.union([a, b], engine=ENG)


def inter(a, b):
    return trimesh.boolean.intersection([a, b], engine=ENG)


def rod(p0, p1, radius, sections=48):
    """Solid cylinder spanning two 3-D points."""
    return trimesh.creation.cylinder(
        radius=radius, segment=np.array([p0, p1]), sections=sections)


def load(name):
    m = trimesh.load(os.path.join(PARTS, name), process=True)
    return m


def drop_islands(mesh, min_faces=100):
    """Drop tiny sliver components, keeping outer skin + large cavity lobes."""
    comps = mesh.split(only_watertight=False)
    keep = [c for c in comps if len(c.faces) >= min_faces]
    return trimesh.util.concatenate(keep) if keep else mesh


# ── Head dish geometry (part-local mm) ───────────────────────────────────────
T = np.array([117.5, -265.4, 67.8])          # spike tip (exterior)
C = np.array([130.5, -256.8, 72.4])          # dish base centre
A = (T - C) / np.linalg.norm(T - C)          # outward axis (base -> tip)

DISH_R = 13.0          # mm, solid-fill cylinder radius (~dish disc radius)
DISH_BACK = 30.0       # mm, fill depth into the hull from the spike tip
PITOT_D = 1.5          # mm, pitot air bore through the spike tip
BARB_OD = 4.0          # mm, interior barb boss outer diameter
BARB_ID = 2.5          # mm, barb through-bore (silicone line)
BARB_RIDGE_OD = 5.0    # mm, retention ridge OD
BARB_LEN = 14.0        # mm, barb protrusion into the cavity
WIDE_LEN = DISH_BACK + BARB_LEN   # 2.5 mm channel from cavity up toward the tip


def build_head():
    O = load("head_shell24_2mm_repaired__outer.stl")
    inner = load("head_shell24_2mm_repaired__inner.stl")
    opened = load("head_inner_opened.stl")

    inner_used = inter(opened, inner)         # clamp opened to <= original

    # Force the dish + spike solid: remove a cylinder of inner along the axis.
    dish_fill = rod(T + A * 2.0, T - A * DISH_BACK, DISH_R)
    inner_used = diff(inner_used, dish_fill)

    shell = diff(O, inner_used)

    # Interior barb boss (coaxial), anchored in the solid fill, into the cavity.
    p_anchor = T - A * (DISH_BACK - 4.0)      # 4 mm inside the fill's inner end
    p_cav = p_anchor - A * BARB_LEN           # barb tip, in the cavity
    boss = rod(p_anchor, p_cav, BARB_OD / 2.0)
    ridge = rod(p_cav + A * 3.0, p_cav + A * 0.5, BARB_RIDGE_OD / 2.0)
    shell = union(shell, union(boss, ridge))

    # Air path: 2.5 mm channel from the barb tip up toward the spike, then a
    # 1.5 mm pitot orifice through the spike tip to the exterior.
    wide = rod(p_cav - A * 1.0, p_cav + A * (WIDE_LEN), BARB_ID / 2.0)
    pitot = rod(T + A * 3.0, T - A * (DISH_BACK + 6.0), PITOT_D / 2.0)
    shell = diff(shell, wide)
    shell = diff(shell, pitot)

    shell = drop_islands(shell)
    out = os.path.join(OUT, "head_shell24_2mm_repaired.stl")
    shell.export(out)
    print(f"head: facets={len(shell.faces)} watertight={shell.is_watertight} "
          f"vol={shell.volume:.0f} -> {out}")


def build_rear():
    O = load("rear_shell24_2mm_repaired__outer.stl")
    inner = load("rear_shell24_2mm_repaired__inner.stl")
    opened = load("rear_inner_opened.stl")
    inner_used = inter(opened, inner)
    shell = diff(O, inner_used)
    shell = drop_islands(shell)
    out = os.path.join(OUT, "rear_shell24_2mm_repaired.stl")
    shell.export(out)
    print(f"rear: facets={len(shell.faces)} watertight={shell.is_watertight} "
          f"vol={shell.volume:.0f} -> {out}")


if __name__ == "__main__":
    build_head()
    build_rear()
