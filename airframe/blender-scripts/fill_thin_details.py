"""
fill_thin_details.py  —  morphological-opening pass for shell inner operands.

Run with:
    blender --background --python fill_thin_details.py -- <inner_stl> <out_stl> <radius_mm> <pitch_mm>

Purpose
-------
The inner operand (the subtracted void) of a fuselage shell follows the exterior
inward by the wall thickness, so it ALSO reaches into every thin exterior detail
(antenna spikes, fins, greebles, skids, pod blisters).  When subtracted those
thin features become hollow 2 mm shells that cannot be foam-filled and snap off
in handling.

This pass applies a morphological OPENING to the inner solid:
    opened = dilate( erode( inner, r ), r )
implemented with even-offset normal shrink/grow (shrink_fatten) plus a voxel
remesh after each step to resolve self-intersections.  Opening deletes every
protrusion thinner than ~2*r while leaving the large interior cavity intact, so
those thin details come out SOLID in the final shell.  Opening is anti-extensive
(opened subset of original) so the downstream O - opened wall is never thinner
than the original 2 mm anywhere — no new breaches.  (The hollow_manifold.py step
additionally intersects opened with the original inner to guarantee this.)

Operates on shell operands derived from the Serenity hull geometry: "Serenity
Firefly with landing gear and swivel engines" by misubisu
(thingiverse.com/thing:7330462, CC BY 4.0).
Full attribution chain: current-specification/LICENSE_AND_ATTRIBUTION.md §2.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0  —  creativecommons.org/licenses/by/4.0
"""

import sys

import bpy


def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def remesh(obj, pitch):
    mod = obj.modifiers.new("vr", "REMESH")
    mod.mode = "VOXEL"
    mod.voxel_size = pitch
    bpy.ops.object.modifier_apply(modifier="vr")


def offset(obj, dist):
    """Even-offset move of all vertices along their normals by dist (mm)."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.transform.shrink_fatten(value=dist, use_even_offset=False)
    bpy.ops.object.mode_set(mode="OBJECT")


def main():
    a = sys.argv[sys.argv.index("--") + 1 :]
    in_stl, out_stl, radius, pitch = a[0], a[1], float(a[2]), float(a[3])

    clear()
    bpy.ops.wm.stl_import(filepath=in_stl)
    obj = bpy.context.selected_objects[0]

    # Erode inward, remesh to clean folds, dilate back out, remesh again.
    offset(obj, -radius)
    remesh(obj, pitch)
    offset(obj, +radius)
    remesh(obj, pitch)

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.stl_export(filepath=out_stl, export_selected_objects=True)
    print(f"opened r={radius} pitch={pitch} -> {out_stl}")


main()
