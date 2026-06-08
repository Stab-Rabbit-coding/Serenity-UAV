#!/usr/bin/env python3
"""
generate_hollow_shells.py

Scales all Serenity (thing:7330462) STL parts so the assembled model is
18.0 inches along its longest axis, then shells each body part to a
closed hollow mesh with WALL_MM wall thickness for 2 lb/cf foam fill.

Articulating parts (door, legs, pins, pistons, arms) are scaled only —
they are too thin to hollow meaningfully.

Design notes captured here:
  - Fuselage EDF intake: cut in the necked-down section just aft of the
    cargo bay (s_middle.stl region), centred on the bottom face.
    Diameter sized for 40mm EDF at 18" final scale.

Outputs: files-hollowed-18in/
  <part>_shell18.stl  — hollowed hull part at 18" scale
  <part>_scaled18.stl — articulation part scaled only
"""

import os
import sys
import subprocess
import trimesh
import numpy as np

# ── tunables ──────────────────────────────────────────────────────────────────
WALL_MM    = 2.5    # shell wall thickness at final scale (mm)
TARGET_IN  = 18.0   # desired assembled length
TARGET_MM  = TARGET_IN * 25.4
# ─────────────────────────────────────────────────────────────────────────────

SRC = os.path.join(os.path.dirname(__file__), "files")
OUT = os.path.join(os.path.dirname(__file__), "files-hollowed-18in")
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

# ── compute scale factor from assembled envelope ──────────────────────────────
all_files = HOLLOW_PARTS + SCALE_ONLY_PARTS
meshes = []
for f in all_files:
    p = os.path.join(SRC, f)
    if os.path.exists(p):
        meshes.append(trimesh.load(p))

all_verts = np.vstack([m.vertices for m in meshes])
asm_extents = all_verts.max(axis=0) - all_verts.min(axis=0)
SCALE = TARGET_MM / asm_extents.max()

print(f"Assembled envelope: {asm_extents[0]:.1f} x {asm_extents[1]:.1f} x {asm_extents[2]:.1f} mm")
print(f"Scale factor:       {SCALE:.4f}×  ({asm_extents.max():.1f} mm → {TARGET_MM:.1f} mm)")
print(f"Final dims:         {asm_extents[0]*SCALE:.1f} x {asm_extents[1]*SCALE:.1f} x {asm_extents[2]*SCALE:.1f} mm")
print(f"                    = {asm_extents[0]*SCALE/25.4:.2f}\" x {asm_extents[1]*SCALE/25.4:.2f}\" x {asm_extents[2]*SCALE/25.4:.2f}\"")
print()


# ── OpenSCAD helpers ──────────────────────────────────────────────────────────

def shell_scad(src_path: str, centroid_scaled, extents_scaled, wall: float) -> str:
    """
    OpenSCAD code: outer = scaled import; inner void = centroid-anchored
    non-uniform shrink of the same mesh.  Gives ≈wall mm shell everywhere.
    """
    cx, cy, cz = centroid_scaled
    ex, ey, ez = extents_scaled

    def inner_scale(dim):
        if dim > 4 * wall:
            return (dim - 2 * wall) / dim
        return 0.01  # part thinner than 4× wall: collapse void to nothing

    sx = inner_scale(ex)
    sy = inner_scale(ey)
    sz = inner_scale(ez)

    rel = os.path.relpath(src_path, OUT)
    return (
        f"// Shell of {os.path.basename(src_path)}\n"
        f"// wall={wall}mm  scale={SCALE:.4f}  centroid=({cx:.2f},{cy:.2f},{cz:.2f})\n"
        f"difference() {{\n"
        f"    scale([{SCALE},{SCALE},{SCALE}]) import(\"{rel}\");\n"
        f"    translate([{cx:.4f},{cy:.4f},{cz:.4f}])\n"
        f"    scale([{sx:.6f},{sy:.6f},{sz:.6f}])\n"
        f"    translate([{-cx:.4f},{-cy:.4f},{-cz:.4f}])\n"
        f"    scale([{SCALE},{SCALE},{SCALE}]) import(\"{rel}\");\n"
        f"}}\n"
    )


def scale_only_scad(src_path: str) -> str:
    rel = os.path.relpath(src_path, OUT)
    return (
        f"// {os.path.basename(src_path)} scaled to {TARGET_IN}\" assembly\n"
        f"scale([{SCALE},{SCALE},{SCALE}]) import(\"{rel}\");\n"
    )


def run_openscad(scad_path: str, out_path: str) -> bool:
    r = subprocess.run(
        ["openscad", "--export-format", "binstl", "-o", out_path, scad_path],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        print(f"  ERROR: {r.stderr.strip()[:300]}")
        return False
    sz = os.path.getsize(out_path) / 1024
    print(f"  → {os.path.basename(out_path)}  ({sz:.0f} KB)")
    return True


# ── hollow parts ─────────────────────────────────────────────────────────────
print("=== Hollow hull parts ===")
for fname in HOLLOW_PARTS:
    src = os.path.join(SRC, fname)
    if not os.path.exists(src):
        print(f"  SKIP {fname} (not found)")
        continue

    m = trimesh.load(src)
    centroid_s = m.centroid * SCALE
    extents_s  = m.bounding_box.extents * SCALE

    scad_code = shell_scad(src, centroid_s, extents_s, WALL_MM)
    stem      = fname.replace(".stl", "")
    scad_path = os.path.join(OUT, stem + "_shell18.scad")
    out_path  = os.path.join(OUT, stem + "_shell18.stl")

    with open(scad_path, "w") as f:
        f.write(scad_code)

    print(f"Rendering {fname} ...")
    run_openscad(scad_path, out_path)


# ── scale-only parts ──────────────────────────────────────────────────────────
print()
print("=== Scale-only articulation parts ===")
for fname in SCALE_ONLY_PARTS:
    src = os.path.join(SRC, fname)
    if not os.path.exists(src):
        print(f"  SKIP {fname} (not found)")
        continue

    scad_code = scale_only_scad(src)
    stem      = fname.replace(".stl", "")
    scad_path = os.path.join(OUT, stem + "_scaled18.scad")
    out_path  = os.path.join(OUT, stem + "_scaled18.stl")

    with open(scad_path, "w") as f:
        f.write(scad_code)

    print(f"Scaling {fname} ...")
    run_openscad(scad_path, out_path)


print()
print("Done.  Output in:", OUT)
