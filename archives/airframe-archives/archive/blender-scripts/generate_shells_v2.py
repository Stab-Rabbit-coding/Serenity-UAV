#!/usr/bin/env python3
"""
generate_shells_v2.py

Pipeline:
  1. pymeshfix  → watertight manifold mesh
  2. trimesh    → scale to 18.0" assembled length
  3. manifold3d → boolean difference with centroid-inset copy → hollow shell

Parts thinner than 4× WALL_MM on any axis are scaled only (no hollow).

Design note (NOT implemented here — separate remix step):
  Fuselage 40mm EDF intake: centred underside of s_middle, just aft of
  cargo bay opening, at the necked-down waist.  Cut at 18" scale.
  Variable-area nozzle (BamJr thing:2991269) mounts at the EDF exit.
  Same nozzle required for all three EDF positions.
"""

import os, sys
import numpy as np
import trimesh
import pymeshfix

# ── tunables ──────────────────────────────────────────────────────────────────
WALL_MM   = 2.5      # shell wall thickness (mm at final scale)
TARGET_IN = 18.0
TARGET_MM = TARGET_IN * 25.4
SCALE     = 2.1974   # assembled 208.1 mm → 457.2 mm
# ─────────────────────────────────────────────────────────────────────────────

BASE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(BASE, "files")
OUT  = os.path.join(BASE, "files-hollowed-18in")
os.makedirs(OUT, exist_ok=True)

HOLLOW_PARTS = [
    "s_head.stl",
    "s_middle.stl",
    "s_rear.stl",
    "s_cargo_sect.stl",
    "s_wings_both.stl",
    "s_eng_left.stl",
    "s_eng_right.stl",
]

SCALE_ONLY_PARTS = [
    "s_cargo_door.stl",
    "s_cargo_door_strutts.stl",
    "s_legs.stl",
    "s_feet_x_4.stl",
    "s_eng_piv_outer.stl",
    "s_eng_pistons.stl",
    "s_pivot_arm_a.stl",
    "s_eng_piv_pins.stl",
]


def load_and_repair(path: str) -> trimesh.Trimesh:
    """Load STL and make watertight via pymeshfix."""
    m = trimesh.load(path, process=False)
    if isinstance(m, trimesh.Scene):
        m = trimesh.util.concatenate(list(m.geometry.values()))
    v = np.asarray(m.vertices, dtype=np.float64)
    f = np.asarray(m.faces,    dtype=np.int32)
    verts, faces = pymeshfix.clean_from_arrays(v, f)
    return trimesh.Trimesh(vertices=verts, faces=faces, process=True)


def make_shell(outer: trimesh.Trimesh, wall: float) -> trimesh.Trimesh:
    """
    Boolean difference of outer with a centroid-inset copy.
    Gives approximately uniform wall thickness on organic shapes.
    Parts thinner than 4×wall on any axis fall through to return the solid.
    """
    bb = outer.bounding_box.extents
    min_dim = bb.min()
    if min_dim < 4 * wall:
        print(f"    (min dim {min_dim:.1f} mm < {4*wall:.1f} mm — returning solid)")
        return outer

    cx, cy, cz = outer.centroid
    sx = max(0.001, (bb[0] - 2 * wall) / bb[0])
    sy = max(0.001, (bb[1] - 2 * wall) / bb[1])
    sz = max(0.001, (bb[2] - 2 * wall) / bb[2])

    inner = outer.copy()
    inner.vertices -= np.array([cx, cy, cz])
    inner.vertices *= np.array([sx, sy, sz])
    inner.vertices += np.array([cx, cy, cz])

    shell = trimesh.boolean.difference([outer, inner], engine='manifold')
    return shell


print(f"Scale factor: {SCALE:.4f}×  ({TARGET_IN}\" / 208.1 mm assembled)")
print(f"Wall:         {WALL_MM} mm\n")

print("=== Hollow hull parts ===")
for fname in HOLLOW_PARTS:
    src = os.path.join(SRC, fname)
    if not os.path.exists(src):
        print(f"  SKIP {fname}")
        continue

    stem = fname.replace(".stl", "")
    out  = os.path.join(OUT, stem + "_shell18.stl")
    print(f"  {fname} ...", end="", flush=True)

    m = load_and_repair(src)
    m.apply_scale(SCALE)
    bb = m.bounding_box.extents
    print(f" scaled {bb[0]:.1f}×{bb[1]:.1f}×{bb[2]:.1f} mm ...", end="", flush=True)

    shell = make_shell(m, WALL_MM)
    shell.export(out)
    sz = os.path.getsize(out) / 1024
    print(f" → {stem}_shell18.stl ({sz:.0f} KB)")

print()
print("=== Scale-only articulation parts ===")
for fname in SCALE_ONLY_PARTS:
    src = os.path.join(SRC, fname)
    if not os.path.exists(src):
        print(f"  SKIP {fname}")
        continue

    stem = fname.replace(".stl", "")
    out  = os.path.join(OUT, stem + "_scaled18.stl")
    print(f"  {fname} ...", end="", flush=True)

    m = load_and_repair(src)
    m.apply_scale(SCALE)
    m.export(out)
    sz = os.path.getsize(out) / 1024
    print(f" → {stem}_scaled18.stl ({sz:.0f} KB)")

print(f"\nDone. Output: {OUT}")
