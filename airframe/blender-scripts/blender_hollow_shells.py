# ============================================================================
# HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
#   Hull frame (canonical for ALL design artifacts): X = +port (left),
#   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
#   world origin.  Primary-component STLs published to airframe/stls/
#   are stored directly in hull frame, baked by tools/bake_hull_frame.py
#   (marker 'SerenityUAV HULL-FRAME R1' in the binary STL header).
#   NEVER re-bake a mesh derived from an already-baked file.
#   This file:
#     Shell hollowing pipeline operating in the source mesh part-local
#     frame.  Outputs destined for airframe/stls/ primary components
#     must be baked to hull frame via tools/bake_hull_frame.py.
# ============================================================================
# Hull geometry derives from "Serenity Firefly with landing gear and swivel
# engines" by misubisu (thingiverse.com/thing:7330462, CC BY 4.0).
# Full attribution chain: current-specification/LICENSE_AND_ATTRIBUTION.md §2.
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

import math
import os
import sys

import bpy

# ── tunables ──────────────────────────────────────────────────────────────────
WALL_MM = 2.5
TARGET_IN = 18.0
TARGET_MM = TARGET_IN * 25.4
SCALE = 2.1974  # pre-computed: 208.1 mm assembled → 457.2 mm
# ─────────────────────────────────────────────────────────────────────────────

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "files")
OUT = os.path.join(BASE, "files-hollowed-18in")
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

# Joint face features: section files, mating faces, and boss/socket assignment.
# Each joint pair alternates so one side gets a boss and the mating side gets a socket.
JOINT_FEATURES = {
    "s_head.stl": [("aft", "max", 1.0, "socket")],
    "s_cargo_sect.stl": [
        ("forward", "min", -1.0, "boss"),
        ("aft", "max", 1.0, "socket"),
    ],
    "s_middle.stl": [
        ("forward", "min", -1.0, "boss"),
        ("aft", "max", 1.0, "socket"),
    ],
    "s_rear.stl": [("forward", "min", -1.0, "boss")],
}

BOSS_OD_MM = 8.0
BOSS_HEIGHT_MM = 6.0
SOCKET_DEPTH_MM = 6.0
BOSS_CLEARANCE_MM = 0.3
M3_SCREW_DIAM_MM = 3.0
M3_CLEARANCE_MM = 0.3
M3_CLEARANCE_DIAM_MM = M3_SCREW_DIAM_MM + M3_CLEARANCE_MM
M3_HOLE_DEPTH_MM = BOSS_HEIGHT_MM + 2.0
BOSS_OFFSET_RATIO = 0.30  # offset from center for boss placement on the mating face


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


def open_joint_faces(obj, fname, tolerance_mm=0.5):
    """Remove the flat mating face polygons and leave the shell joint open."""
    planes = JOINT_FEATURES.get(fname, [])
    if not planes:
        return

    import bmesh

    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()

    verts = [v.co.z for v in bm.verts]
    z_min = min(verts)
    z_max = max(verts)

    for _, bound, normal_z, _ in planes:
        plane_z = z_min if bound == "min" else z_max
        marked = []
        for face in bm.faces:
            if abs(face.normal.z - normal_z) > 0.05:
                continue

            centroid_z = sum((v.co.z for v in face.verts)) / len(face.verts)
            if abs(centroid_z - plane_z) > tolerance_mm:
                continue

            marked.append(face)

        if marked:
            bmesh.ops.delete(bm, geom=marked, context="FACES")
            print(f"  Opened joint face at {fname}: {bound} Z={plane_z:.2f}")

    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def add_joint_bosses(obj, fname):
    """Add interior boss or socket features at the open joint face(s)."""
    planes = JOINT_FEATURES.get(fname, [])
    if not planes:
        return

    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bounds = [v.co for v in obj.data.vertices]
    xs = [v.x for v in bounds]
    ys = [v.y for v in bounds]
    x_center = (min(xs) + max(xs)) / 2.0
    y_center = (min(ys) + max(ys)) / 2.0
    x_span = (max(xs) - min(xs)) * 0.5 * BOSS_OFFSET_RATIO
    y_span = (max(ys) - min(ys)) * 0.5 * BOSS_OFFSET_RATIO

    features = []
    boss_hole_centers = []
    for _, bound, normal_z, feature_type in planes:
        z = (
            min(v.co.z for v in bounds)
            if bound == "min"
            else max(v.co.z for v in bounds)
        )
        direction = -normal_z
        if feature_type == "boss":
            depth = BOSS_HEIGHT_MM
            radius = BOSS_OD_MM / 2.0
            name_prefix = "boss"
            offset = BOSS_HEIGHT_MM / 2.0 + 0.5
        else:
            depth = SOCKET_DEPTH_MM
            radius = BOSS_OD_MM / 2.0 + BOSS_CLEARANCE_MM
            name_prefix = "socket"
            offset = SOCKET_DEPTH_MM / 2.0 + 0.5

        feature_z = z + direction * offset
        for ix in (-1, 1):
            for iy in (-1, 1):
                fx = x_center + ix * x_span
                fy = y_center + iy * y_span
                feat_name = f"{name_prefix}_{fname}_{bound}_{ix}_{iy}"
                bpy.ops.mesh.primitive_cylinder_add(
                    radius=radius,
                    depth=depth,
                    enter_editmode=False,
                    location=(fx, fy, feature_z),
                )
                feature_obj = bpy.context.active_object
                feature_obj.name = feat_name
                features.append((feature_obj, feature_type))
                if feature_type == "boss":
                    boss_hole_centers.append((fx, fy, feature_z))

    if not features:
        return

    # Separate boss solids and socket cutters.
    boss_objs = [obj for obj, t in features if t == "boss"]
    socket_objs = [obj for obj, t in features if t == "socket"]

    if boss_objs:
        bpy.ops.object.select_all(action="DESELECT")
        for boss in boss_objs:
            boss.select_set(True)
        bpy.context.view_layer.objects.active = boss_objs[0]
        bpy.ops.object.join()
        boss_group = bpy.context.active_object
        boss_group.name = "joint_bosses"

        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        boss_group.select_set(True)
        bpy.context.view_layer.objects.active = obj
        mod = obj.modifiers.new(name="boss_union", type="BOOLEAN")
        mod.operation = "UNION"
        mod.object = boss_group
        mod.solver = "EXACT"
        bpy.ops.object.modifier_apply(modifier="boss_union")
        bpy.data.objects.remove(boss_group, do_unlink=True)

        cut_m3_clearance_holes(obj, boss_hole_centers)

    if socket_objs:
        bpy.ops.object.select_all(action="DESELECT")
        for socket in socket_objs:
            socket.select_set(True)
        bpy.context.view_layer.objects.active = socket_objs[0]
        bpy.ops.object.join()
        socket_group = bpy.context.active_object
        socket_group.name = "joint_sockets"

        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        socket_group.select_set(True)
        bpy.context.view_layer.objects.active = obj
        mod = obj.modifiers.new(name="socket_cut", type="BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.object = socket_group
        mod.solver = "EXACT"
        bpy.ops.object.modifier_apply(modifier="socket_cut")
        bpy.data.objects.remove(socket_group, do_unlink=True)

    print(
        f"  Added {len(boss_objs)} boss(es) and {len(socket_objs)} socket(s) for {fname}"
    )


def cut_m3_clearance_holes(obj, hole_centers):
    """Cut M3 clearance holes through boss features on the mating face."""
    if not hole_centers:
        return

    bpy.ops.object.select_all(action="DESELECT")
    hole_objs = []
    for idx, (hx, hy, hz) in enumerate(hole_centers, start=1):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=M3_CLEARANCE_DIAM_MM / 2.0,
            depth=M3_HOLE_DEPTH_MM,
            enter_editmode=False,
            location=(hx, hy, hz),
        )
        hole = bpy.context.active_object
        hole.name = f"m3_clearance_hole_{idx}"
        hole.select_set(True)
        hole_objs.append(hole)

    bpy.context.view_layer.objects.active = hole_objs[0]
    bpy.ops.object.join()
    hole_group = bpy.context.active_object
    hole_group.name = "m3_clearance_holes"

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    hole_group.select_set(True)
    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new(name="m3_clearance_cut", type="BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = hole_group
    mod.solver = "EXACT"
    bpy.ops.object.modifier_apply(modifier="m3_clearance_cut")
    bpy.data.objects.remove(hole_group, do_unlink=True)


def make_watertight_and_shell(obj, wall_mm, voxel_mm=1.0, fname=None):
    """
    1. Voxel remesh → watertight manifold (preserves exterior to ±voxel_mm)
    2. Solidify inward → closed shell of wall_mm thickness
    """
    bpy.context.view_layer.objects.active = obj

    # Step 1: voxel remesh to guarantee a watertight manifold.
    # Call the operator with explicit parameters to ensure correct voxel size.
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.voxel_remesh(voxel_size=voxel_mm, adaptivity=0.0)

    # Clean up: merge very-close vertices and make normals consistent (outside).
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    # Merge by distance to remove tiny duplicate verts created by remesh
    bpy.ops.mesh.merge_by_distance()
    # Ensure normals point outward so Solidify applies inward correctly
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")

    # Step 1b: open any section joint faces before shelling.
    if fname is not None:
        open_joint_faces(obj, fname)

    # Step 2: solidify inward — exterior surface stays exactly where it is.
    # Use a positive thickness with offset=-1 to push the new surface inward
    # relative to the outward-facing normals.  Do not cap boundaries here; the
    # mating faces should remain open.
    mod = obj.modifiers.new(name="Shell", type="SOLIDIFY")
    mod.thickness = wall_mm
    mod.offset = -1.0
    mod.use_even_offset = True
    mod.use_quality_normals = True
    mod.use_rim = False
    bpy.ops.object.modifier_apply(modifier="Shell")

    if fname is not None:
        add_joint_bosses(obj, fname)


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
    make_watertight_and_shell(obj, wall_mm=WALL_MM, voxel_mm=1.0, fname=fname)

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


print(f'\nScale factor: {SCALE:.4f}×  (18.0" / 208.1 mm assembled)')
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
