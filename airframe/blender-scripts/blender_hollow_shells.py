"""
blender_hollow_shells.py  —  run with:
    blender --background --python blender_hollow_shells.py

Scales all Serenity (thing:7330462) hull STLs to 18.0" assembled length,
then shells each body part to WALL_MM thickness using the Solidify modifier
(inward offset, so exterior surface is preserved exactly).

Articulation parts (door, pins, pistons, arms, legs, feet) are scaled only.

Design note: fuselage EDF intake is NOT cut here — it belongs in the
necked-down section of s_middle just aft of the cargo bay, centred on the
underside, for a 40mm EDF at 18" final scale (~88mm ID at final scale).
"""

import bpy
import os
import sys
import math

# ── tunables ──────────────────────────────────────────────────────────────────
WALL_MM    = 2.5
TARGET_IN  = 18.0
TARGET_MM  = TARGET_IN * 25.4
SCALE      = 2.1974   # pre-computed: 208.1 mm assembled → 457.2 mm
# ─────────────────────────────────────────────────────────────────────────────

BASE  = os.path.dirname(os.path.abspath(__file__))
SRC   = os.path.join(BASE, "files")
OUT   = os.path.join(BASE, "files-hollowed-18in")
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


def make_watertight_and_shell(obj, wall_mm, voxel_mm=1.0):
    """
    1. Voxel remesh → watertight manifold (preserves exterior to ±voxel_mm)
    2. Solidify inward → closed shell of wall_mm thickness
    """
    bpy.context.view_layer.objects.active = obj

    # Step 1: voxel remesh to guarantee a watertight manifold.
    # Use the object-level voxel remesh (faster than the modifier path in 4.x).
    obj.data.remesh_voxel_size = voxel_mm
    obj.data.remesh_voxel_adaptivity = 0.0
    bpy.ops.object.voxel_remesh()

    # Step 2: solidify inward — exterior surface stays exactly where it is.
    mod = obj.modifiers.new(name="Shell", type="SOLIDIFY")
    mod.thickness           = -wall_mm   # negative = inward offset
    mod.offset              = -1.0       # anchor at outer surface
    mod.use_even_offset     = True
    mod.use_quality_normals = True
    bpy.ops.object.modifier_apply(modifier="Shell")


def process_hollow(fname):
    src = os.path.join(SRC, fname)
    stem = fname.replace(".stl", "")
    out = os.path.join(OUT, stem + "_shell18.stl")

    clear_scene()
    obj = import_stl(src)

    # Scale to 18"
    obj.scale = (SCALE, SCALE, SCALE)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Voxel remesh (1 mm voxels at final scale) → Solidify inward 2.5 mm
    make_watertight_and_shell(obj, wall_mm=WALL_MM, voxel_mm=1.0)

    export_stl(obj, out)
    sz = os.path.getsize(out) / 1024
    print(f"  {fname}  →  {stem}_shell18.stl  ({sz:.0f} KB)")


def process_scale_only(fname):
    src = os.path.join(SRC, fname)
    stem = fname.replace(".stl", "")
    out = os.path.join(OUT, stem + "_scaled18.stl")

    clear_scene()
    obj = import_stl(src)

    obj.scale = (SCALE, SCALE, SCALE)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    export_stl(obj, out)
    sz = os.path.getsize(out) / 1024
    print(f"  {fname}  →  {stem}_scaled18.stl  ({sz:.0f} KB)")


print(f"\nScale factor: {SCALE:.4f}×  (18.0\" / 208.1 mm assembled)")
print(f"Wall thickness: {WALL_MM} mm\n")

print("=== Hollow hull parts ===")
for f in HOLLOW_PARTS:
    if os.path.exists(os.path.join(SRC, f)):
        process_hollow(f)
    else:
        print(f"  SKIP {f} (not found)")

print("\n=== Scale-only articulation parts ===")
for f in SCALE_ONLY_PARTS:
    if os.path.exists(os.path.join(SRC, f)):
        process_scale_only(f)
    else:
        print(f"  SKIP {f} (not found)")

print(f"\nDone. Output: {OUT}")
