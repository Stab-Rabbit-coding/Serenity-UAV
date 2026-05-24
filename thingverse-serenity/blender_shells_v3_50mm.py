"""
blender_shells_v3_50mm.py  —  run with:
    blender --background --python blender_shells_v3_50mm.py

This is a 50mm-EDF-targeted variant of `blender_shells_v3.py`.
Approach and workflow are identical; the uniform scale is increased by
25% to enlarge the nacelle bore to accept 50mm EDF units.

Changes from v3:
 - Uniform scale multiplied by 1.25x to increase bore clearance for 50mm EDF
 - All other logic preserved (inset, flip normals, join, export)

Output files are written to `files-hollowed-18in/` with `_shell24_50mm` suffix.
"""

import bpy
import os

WALL_MM   = 2.5
TARGET_IN = 24.0

# Base scale from v3 multiplied by 1.25 to increase internal clearances
SCALE_X = 2.9294 * 1.25
SCALE_Y = 2.9294 * 1.25
SCALE_Z = 2.9294 * 1.25

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


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def import_stl(path):
    bpy.ops.wm.stl_import(filepath=path)
    return bpy.context.selected_objects[0]


def export_stl(obj, path):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True)


def process_hollow(fname):
    src  = os.path.join(SRC, fname)
    stem = fname.replace(".stl", "")
    out  = os.path.join(OUT, stem + "_shell24_50mm.stl")

    clear_scene()
    outer = import_stl(src)
    outer.name = "outer"

    # Uniform scale to new target (50mm EDF clearance)
    outer.scale = (SCALE_X, SCALE_Y, SCALE_Z)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Dimensions at final scale
    dx, dy, dz = outer.dimensions
    min_dim = min(dx, dy, dz)
    if min_dim < 4 * WALL_MM:
        print(f"    (min dim {min_dim:.1f} mm < {4*WALL_MM:.1f} mm — exporting solid)")
        export_stl(outer, out)
        sz = os.path.getsize(out) / 1024
        print(f"  → {stem}_shell24_50mm.stl  ({sz:.0f} KB, solid)")
        return

    # Centroid-inset scale factors (uniform wall thickness per axis)
    sx  = max(0.001, (dx - 2 * WALL_MM) / dx)
    sy  = max(0.001, (dy - 2 * WALL_MM) / dy)
    sz_ = max(0.001, (dz - 2 * WALL_MM) / dz)

    # Bounding box centroid
    bmin = [outer.bound_box[0][i] for i in range(3)]
    bmax = [outer.bound_box[6][i] for i in range(3)]
    cx = (bmin[0] + bmax[0]) / 2
    cy = (bmin[1] + bmax[1]) / 2
    cz = (bmin[2] + bmax[2]) / 2

    # Duplicate to make inner shell
    bpy.ops.object.select_all(action="DESELECT")
    outer.select_set(True)
    bpy.context.view_layer.objects.active = outer
    bpy.ops.object.duplicate()
    inner = bpy.context.selected_objects[0]
    inner.name = "inner"

    # Translate to centroid → scale inward → translate back
    inner.location = (inner.location.x - cx,
                      inner.location.y - cy,
                      inner.location.z - cz)
    bpy.ops.object.transform_apply(location=True)
    inner.scale = (sx, sy, sz_)
    bpy.ops.object.transform_apply(scale=True)
    inner.location = (cx, cy, cz)
    bpy.ops.object.transform_apply(location=True)

    # Flip normals on inner shell so it faces inward
    bpy.context.view_layer.objects.active = inner
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode="OBJECT")

    # Join outer + inner into one object
    outer.select_set(True)
    inner.select_set(True)
    bpy.context.view_layer.objects.active = outer
    bpy.ops.object.join()
    joined = bpy.context.active_object

    export_stl(joined, out)
    sz = os.path.getsize(out) / 1024
    print(f"  → {stem}_shell24_50mm.stl  ({sz:.0f} KB)")


def process_scale_only(fname):
    src  = os.path.join(SRC, fname)
    stem = fname.replace(".stl", "")
    out  = os.path.join(OUT, stem + "_scaled24_50mm.stl")

    clear_scene()
    obj = import_stl(src)
    obj.scale = (SCALE_X, SCALE_Y, SCALE_Z)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    export_stl(obj, out)
    sz = os.path.getsize(out) / 1024
    print(f"  → {stem}_scaled24_50mm.stl  ({sz:.0f} KB)")


print(f"\nScale: {SCALE_X:.4f}× (uniform)  Target: {TARGET_IN}\"  Wall: {WALL_MM} mm\n")

print("=== Hollow hull parts ===")
for f in HOLLOW_PARTS:
    if os.path.exists(os.path.join(SRC, f)):
        print(f"  {f} ...", end="", flush=True)
        process_hollow(f)
    else:
        print(f"  SKIP {f}")

print("\n=== Scale-only articulation parts ===")
for f in SCALE_ONLY_PARTS:
    if os.path.exists(os.path.join(SRC, f)):
        print(f"  {f} ...", end="", flush=True)
        process_scale_only(f)
    else:
        print(f"  SKIP {f}")

print(f"\nDone. Output: {OUT}")
