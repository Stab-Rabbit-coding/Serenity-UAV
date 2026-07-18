"""
make_bay_text.py  —  origin-centred watertight text slabs for avionics-bay marks.

    blender --background --python make_bay_text.py

Each label is created centred at the origin in the XY plane (face normal +Z),
extruded into a slab, then voxel-remeshed into a single watertight manifold
volume (so it is a valid manifold3d boolean operand).  engrave_plaques.py orients
and positions each slab onto a section's interior wall.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0  —  creativecommons.org/licenses/by/4.0
"""

import os

import bpy

OUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "files-hollowed-24in", "operands"
)

SIZE = 13.0  # mm font em size (cap height ~9 mm)
SLAB = 10.0  # mm slab thickness (straddles the wall, centred on origin)
REMESH = 0.3  # mm voxel pitch to weld per-letter shells into one volume

LABELS = ["INARA", "RIVER", "KAYLEE", "SHEPHERD", "SIMON"]


def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def make(text):
    clear()
    bpy.ops.object.text_add()
    t = bpy.context.active_object
    t.data.body = text
    t.data.align_x = "CENTER"
    t.data.align_y = "CENTER"
    t.data.size = SIZE
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.active_object
    m = obj.modifiers.new("s", "SOLIDIFY")
    m.thickness = SLAB
    m.offset = 0.0
    bpy.ops.object.modifier_apply(modifier="s")
    rm = obj.modifiers.new("vr", "REMESH")
    rm.mode = "VOXEL"
    rm.voxel_size = REMESH
    bpy.ops.object.modifier_apply(modifier="vr")
    out = os.path.join(OUT, f"text_{text.lower()}.stl")
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.stl_export(filepath=out, export_selected_objects=True)
    print(f"  {text} -> {out}")


print("Bay-mark text slabs:")
for lbl in LABELS:
    make(lbl)
