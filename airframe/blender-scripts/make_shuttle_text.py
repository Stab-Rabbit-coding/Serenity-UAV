"""
make_shuttle_text.py  —  generate INARA / RIVER text cutter slabs for the cargo
shuttle (avionics-bay) interior marks.

    blender --background --python make_shuttle_text.py

Each label is created as a solid slab (text extruded both ways along its face
normal) positioned on the interior outboard wall of its shuttle pod, oriented to
read when looking outboard into the bay.  engrave_shuttles.py intersects each
slab with a thin cavity-adjacent wall layer and subtracts the result, producing
a shallow (<=1 mm) recess that conforms to the curved interior wall and cannot
perforate the 2 mm exterior skin.

Part-local cargo frame (mm): X = lateral (+port), Y = longitudinal, Z = vertical.
Pod interior-wall centres (measured): port (X -11, Y -362, Z 103),
                                      stbd (X -197, Y -363, Z 102).

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0  —  creativecommons.org/licenses/by/4.0
"""

import os

import bpy
import mathutils

OUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "files-hollowed-24in", "operands"
)

LETTER_H = 15.0  # mm, font em size (cap height ~10.5 mm)
SLAB = 8.0  # mm, extrusion thickness straddling the wall (+/-4 mm)
REMESH = 0.3  # mm, voxel pitch to weld the per-letter shells into one volume

# (text, world centre, 3x3 local->world basis rows)
#   local +X = reading direction, +Y = up, +Z = face normal (toward viewer).
LABELS = [
    # PORT (+X wall): read along -Y, up +Z, face -X (viewer inboard at -X).
    ("INARA", (-11.0, -362.0, 103.0), ((0, 0, -1), (-1, 0, 0), (0, 1, 0)), "inara"),
    # STBD (-X wall): read along +Y, up +Z, face +X.
    ("RIVER", (-197.0, -363.0, 102.0), ((0, 0, 1), (1, 0, 0), (0, 1, 0)), "river"),
]


def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def make_label(text, centre, basis, stem):
    clear()
    bpy.ops.object.text_add()
    txt = bpy.context.active_object
    txt.data.body = text
    txt.data.align_x = "CENTER"
    txt.data.align_y = "CENTER"
    txt.data.size = LETTER_H
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.active_object

    # Solidify into a slab that straddles the wall.
    mod = obj.modifiers.new("s", "SOLIDIFY")
    mod.thickness = SLAB
    mod.offset = 0.0
    bpy.ops.object.modifier_apply(modifier="s")

    # Voxel-remesh welds the separate per-letter shells into one watertight
    # manifold volume (required as a manifold3d boolean operand downstream).
    rm = obj.modifiers.new("vr", "REMESH")
    rm.mode = "VOXEL"
    rm.voxel_size = REMESH
    bpy.ops.object.modifier_apply(modifier="vr")

    # Orient (local basis -> world) and position.
    R = mathutils.Matrix(basis).to_4x4()
    obj.matrix_world = mathutils.Matrix.Translation(centre) @ R

    out = os.path.join(OUT, f"text_{stem}.stl")
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.stl_export(filepath=out, export_selected_objects=True)
    print(f"  {text} -> {out}")


print("Generating shuttle text cutter slabs:")
for text, centre, basis, stem in LABELS:
    make_label(text, centre, basis, stem)
