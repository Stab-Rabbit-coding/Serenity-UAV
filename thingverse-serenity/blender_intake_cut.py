"""
blender_intake_cut.py  —  run with:
    blender --background --python blender_intake_cut.py

Cuts a 120 mm diameter EDF air intake into s_middle_shell24.stl.

Geometry reference (s_middle at 24" scale):
  X: 92..270 mm  (fore-aft; X=92 is the aft/cargo-bay end)
  Y: -156..9 mm  (lateral width, Y=0 ≈ starboard skin)
  Z: 0..73 mm    (height; Z=0 is the bottom/underside of fuselage)

The intake is centred on the underside (Z=0 face) in the aft necked-down
region just forward of where s_middle meets the cargo-bay assembly.
INTAKE_X ≈ 130 mm places the cut at the narrowing transition; adjust
toward X=92 to move it further aft.

Method: bmesh face-deletion (no boolean needed on the non-manifold shell).
Faces within the intake circle and within Z_THRESHOLD mm of the bottom are
removed, leaving a clean circular opening that the slicer prints as an open
hole.  A separate blender_nozzle_gen.py script adds the variable nozzle.
"""

import bpy
import bmesh
import os
import math

# ── tunables ─────────────────────────────────────────────────────────────────
INTAKE_DIA_MM  = 120.0       # EDF duct inner diameter at 24" scale
INTAKE_R       = INTAKE_DIA_MM / 2
Z_THRESHOLD    = 4.0         # faces with centroid Z < this are "bottom face"

# Intake centre in XY (the Z=0 bottom face plane).
# X=130 is in the necked transition just aft of the full-beam cargo-bay region.
# Y centre of s_middle at X=130: table shows Y=-141..6, centre ≈ -67.
INTAKE_X = 130.0
INTAKE_Y = -67.0

BASE    = os.path.dirname(os.path.abspath(__file__))
IN_STL  = os.path.join(BASE, "files-hollowed-18in", "s_middle_shell24.stl")
OUT_STL = os.path.join(BASE, "files-hollowed-18in", "s_middle_intake_shell24.stl")
# ─────────────────────────────────────────────────────────────────────────────


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


def cut_intake_bmesh(obj, cx, cy, radius, z_thresh):
    """
    Delete all faces whose centroid is:
      - within radius of (cx, cy) in the XY plane, AND
      - within z_thresh of Z=0 (the bottom face).
    Returns the number of faces removed.
    """
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")

    bm = bmesh.from_edit_mesh(obj.data)
    bm.faces.ensure_lookup_table()

    r2 = radius * radius
    to_delete = []
    for face in bm.faces:
        n = len(face.verts)
        fc_x = sum(v.co.x for v in face.verts) / n
        fc_y = sum(v.co.y for v in face.verts) / n
        fc_z = sum(v.co.z for v in face.verts) / n

        if fc_z < z_thresh:
            dx = fc_x - cx
            dy = fc_y - cy
            if dx * dx + dy * dy < r2:
                to_delete.append(face)

    bmesh.ops.delete(bm, geom=to_delete, context="FACES")
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode="OBJECT")
    return len(to_delete)


clear_scene()
hull = import_stl(IN_STL)
hull.name = "s_middle"

bb = hull.bound_box
xs = [v[0] for v in bb]; ys = [v[1] for v in bb]; zs = [v[2] for v in bb]
print(f"\ns_middle bounds: X {min(xs):.1f}..{max(xs):.1f}  "
      f"Y {min(ys):.1f}..{max(ys):.1f}  Z {min(zs):.1f}..{max(zs):.1f}")
print(f"Cutting {INTAKE_DIA_MM:.0f} mm intake at X={INTAKE_X}, Y={INTAKE_Y}, Z=0 face\n")

n = cut_intake_bmesh(hull, INTAKE_X, INTAKE_Y, INTAKE_R, Z_THRESHOLD)
print(f"  Removed {n} faces for intake opening")

export_stl(hull, OUT_STL)
sz = os.path.getsize(OUT_STL) / 1024
print(f"  → s_middle_intake_shell24.stl  ({sz:.0f} KB)")
print(f"\nDone. Adjust INTAKE_X / INTAKE_Y in the script if position needs refinement.")
