"""
blender_shells_2mm_solidify.py  —  Rev R1  —  run with:
    blender --background --python blender_shells_2mm_solidify.py

Generates 2.0 mm wall WATERTIGHT HOLLOW shells for the four Serenity UAV
fuselage sections (head, cargo, middle, rear) at the 24" hull scale, for
foam-filled (2 lb/cf low-density closed-cell foam) printing.

Hull geometry derives from "Serenity Firefly with landing gear and swivel
engines" by misubisu (thingiverse.com/thing:7330462, CC BY 4.0).
Full attribution chain: current-specification/LICENSE_AND_ATTRIBUTION.md §2.

WHY THIS SCRIPT EXISTS (root-cause fix, 2026-06-11)
---------------------------------------------------
The predecessor archive/blender-scripts/blender_shells_v3_2mm.py built the
inner void by CENTROID-INSET SCALING — an anisotropic scale of a duplicated
outer solid about the bounding-box centre, then boolean DIFFERENCE.  Its own
docstring conceded the method is only "approximate for concave" parts.  On the
concave fuselage sections that approximation FAILS: features that sit far from
the bbox centre (the cargo section's two shuttle blisters above the wings on
port/starboard, the rear pod and tail-cone) get scaled inboard by a larger
absolute distance than the local wall, so the scaled INNER surface crosses
OUTSIDE the outer skin.  The boolean difference then leaves holes and detached
inner-shell fragments — the "hull breaches" reported on the port/starboard
cargo blisters, and the 9-body / 5-body rear and middle shells.

This script replaces centroid-inset scaling with a UNIFORM INWARD OFFSET cut:
the inner cavity is the outer surface eroded inward by a constant 2.0 mm along
each face normal (even-offset shrink), then subtracted with a boolean
difference.  This:
  * preserves the exterior mold line EXACTLY (only the interior is removed), so
    the canonical Serenity skin geometry — blisters, projections, cut-outs — is
    kept true to the reference per CLAUDE.md; and
  * offsets every face along its own normal, so the wall is uniform and the
    inner surface can never punch through the outer skin on a concave region.
    No breaches.

The eroded inner solid is voxel-remeshed before the boolean so that erosion
self-intersections (in narrowing regions such as the rear tail-cone tip) are
resolved cleanly — a plain inward Solidify leaves those surfaces crossing and
fragmented the rear shell into 22 pieces; this method does not.

FRAME / BAKE INVARIANT
----------------------
Each section is produced SCALE-ONLY (x2.9294, no translation), exactly as the
predecessor did, so the output lands in the SAME part-local frame that the
validated transforms in tools/bake_hull_frame.py COMPONENTS already expect
(e.g. cargo local X -202..-7, Y -415..-211, Z 0..163 -> hull X -267..-73,
Y -71..132).  Solidify preserves the bounding box, so those bake transforms
remain valid.  After regeneration the outputs MUST be promoted to the canonical
published paths and re-baked:
    python3 tools/bake_hull_frame.py

PIPELINE (per part)
-------------------
  1. Import original from archives/thingverse-serenity/files/ (the TRUE source,
     not a copy of a copy).  The raw Thingiverse meshes are non-manifold and
     multi-body with internal clutter.
  2. Scale x2.9294 to 24"; apply transform.
  3. Voxel-remesh OUTER at REMESH_MM (0.8 mm — fine, to keep blister/cut-out
     detail crisp): a single watertight manifold outer solid (O), fusing the
     multi-body source and discarding internal junk geometry.
  4. Build the INNER cavity solid (I): duplicate O, erode it inward by 2.0 mm
     with an even-offset shrink (shrink_fatten), then voxel-remesh I.  The
     remesh resolves the self-intersections that erosion creates in concave /
     narrowing regions (notably the rear tail-cone tip, whose cross-section is
     < 2*wall): there the eroded surface collapses and the remesh simply omits
     it, so the tip stays SOLID rather than fragmenting.
  5. Export the two clean manifold operands (O and I) to OUT/operands/.

The boolean DIFFERENCE O - I is then performed by the companion script
hollow_manifold.py using the manifold3d library, which guarantees a 2-manifold
watertight result.  (Blender's own EXACT boolean leaves a few hundred T-junction
seam edges that fail a strict watertight check -- 194 NM edges on the head
section -- so the boolean is done downstream in manifold3d instead.)  The result
is a watertight 2.0 mm hollow shell, solid wherever I vanished, with the exterior
surface O untouched.

Why boolean+eroded-inner instead of a plain inward Solidify: a closed Solidify
leaves the inner and outer surfaces crossing (not resolved) wherever the wall
exceeds the local half-thickness, which fragmented the rear tail cone into 22
pieces.  Remeshing the eroded inner solid resolves those crossings before the
boolean, so every section -- including the rear -- comes out watertight.

Sealed-watertight shells are the target (matching the known-good head shell).
Downstream SCAD aperture cuts (camera, GPS, access panels, cargo door, wing
mortises) open the interior; CLAUDE.md mating-face access is provided there.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
Date:    2026-06-11 (Rev R1)

References:
    archive/blender-scripts/blender_shells_v3_2mm.py — superseded centroid-inset method
    blender_hollow_shells.py — Solidify-inward precedent (18" pipeline)
    tools/bake_hull_frame.py — hull-frame bake (COMPONENTS transforms)
    CLAUDE.md — Hull-Frame Coordinate Standard (Rev R1); fabrication standards
    Blender Solidify modifier: docs.blender.org/manual/en/latest/modeling/
        modifiers/generate/solidify.html
"""

import os

import bmesh
import bpy

WALL_MM = 2.0       # [mm] nominal foam-fill skin wall thickness
SCALE = 2.9294      # uniform 24" scale from native Thingiverse model

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(BASE, "..", ".."))
SRC = os.path.join(REPO, "archives", "thingverse-serenity", "files")
OUT = os.path.join(BASE, "files-hollowed-24in")
# Clean manifold boolean operands (outer + eroded inner) for hollow_manifold.py.
PARTS = os.path.join(OUT, "operands")
os.makedirs(PARTS, exist_ok=True)

# (source_filename, output_filename, voxel_remesh_pitch_mm)
# Output names match the canonical published *_2mm_repaired.stl basenames so the
# promote step in the plan is a straight copy.  Pitch 0.8 mm is "fine" per the
# user decision: keeps shuttle blisters / projections / cut-outs crisp at 24".
HOLLOW_PARTS = [
    ("s_head.stl",       "head_shell24_2mm_repaired.stl",       0.8),
    ("s_cargo_sect.stl", "cargo_sect_shell24_2mm_repaired.stl", 0.8),
    ("s_middle.stl",     "middle_shell24_2mm_repaired.stl",     0.8),
    ("s_rear.stl",       "rear_shell24_2mm_repaired.stl",       0.8),
]


# -- Utility functions --------------------------------------------------------

def clear_scene():
    """Remove all objects from the scene."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def import_stl(path):
    """Import an STL and return the imported object."""
    bpy.ops.wm.stl_import(filepath=path)
    return bpy.context.selected_objects[0]


def export_stl(obj, path):
    """Export a single object as a binary STL."""
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True)


def voxel_remesh(obj, pitch_mm):
    """
    Voxel-remesh the object to a single watertight manifold solid.

    Voxel remesh classifies inside/outside by winding number, so it fuses the
    multi-body Thingiverse source into one solid and discards internal clutter,
    while reproducing the exterior surface to within +/- pitch_mm.
    """
    mod = obj.modifiers.new("vr", "REMESH")
    mod.mode = "VOXEL"
    mod.voxel_size = pitch_mm
    bpy.ops.object.modifier_apply(modifier="vr")


def recompute_outward_normals(obj):
    """Make face normals consistently outward."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")


def build_inner_solid(outer, wall_mm, pitch_mm):
    """
    Return a watertight INNER cavity solid: the outer eroded inward by wall_mm.

    Duplicate the outer, shrink every vertex inward along its normal by an even
    offset (shrink_fatten), then voxel-remesh to a clean watertight solid.  The
    remesh resolves the self-intersections that uniform erosion creates in
    narrowing regions: where the part is thinner than 2*wall the eroded surface
    folds through itself and the remesh omits it, so that region stays solid
    (no cavity) -- exactly what we want at the rear tail-cone tip.
    """
    bpy.ops.object.select_all(action="DESELECT")
    outer.select_set(True)
    bpy.context.view_layer.objects.active = outer
    bpy.ops.object.duplicate()
    inner = bpy.context.selected_objects[0]
    inner.name = "inner"

    # Even-offset inward erosion along vertex normals.
    bpy.context.view_layer.objects.active = inner
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.transform.shrink_fatten(value=-wall_mm, use_even_offset=True)
    bpy.ops.object.mode_set(mode="OBJECT")

    # Remesh resolves erosion self-intersections into a clean watertight solid.
    voxel_remesh(inner, pitch_mm)
    return inner


def count_non_manifold(obj):
    """Return the number of non-manifold edges in the active mesh object."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(obj.data)
    bm.edges.ensure_lookup_table()
    count = sum(1 for e in bm.edges if not e.is_manifold)
    bpy.ops.object.mode_set(mode="OBJECT")
    return count


# -- Main per-part processing -------------------------------------------------

def process_hollow(src_name, out_name, remesh_mm):
    """Generate one watertight 2.0 mm hollow shell via the Solidify pipeline."""
    src = os.path.join(SRC, src_name)
    out = os.path.join(OUT, out_name)

    if not os.path.isfile(src):
        print(f"  SKIP -- source not found: {src}")
        return

    print(f"\n=== {src_name}  ->  {out_name}  (remesh {remesh_mm} mm) ===")
    clear_scene()

    # 1-2. Import and scale to 24" (scale-only: preserves the part-local frame
    #      that the bake transforms expect).
    obj = import_stl(src)
    obj.name = "shell"
    obj.scale = (SCALE, SCALE, SCALE)
    bpy.ops.object.transform_apply(scale=True)
    dx, dy, dz = obj.dimensions
    print(f"  scaled dims: {dx:.1f} x {dy:.1f} x {dz:.1f} mm")

    # 3. Voxel-remesh -> single watertight manifold OUTER solid (O).
    voxel_remesh(obj, remesh_mm)
    recompute_outward_normals(obj)
    nm_o = count_non_manifold(obj)
    print(f"  outer remesh: faces={len(obj.data.polygons)}  NM={nm_o}")

    # 4. Build eroded watertight INNER cavity solid (I).
    inner = build_inner_solid(obj, WALL_MM, remesh_mm)
    nm_i = count_non_manifold(inner)
    print(f"  inner solid:  faces={len(inner.data.polygons)}  NM={nm_i}")

    # 5. Export the two clean manifold operands.  The boolean DIFFERENCE
    #    O - I is performed deterministically in hollow_manifold.py using the
    #    manifold3d library, which guarantees a 2-manifold watertight result
    #    (Blender's EXACT solver leaves a few T-junction seams that are not
    #    watertight under a strict manifold check).
    outer_path = os.path.join(PARTS, out_name.replace(".stl", "__outer.stl"))
    inner_path = os.path.join(PARTS, out_name.replace(".stl", "__inner.stl"))
    export_stl(obj, outer_path)
    export_stl(inner, inner_path)
    if nm_o or nm_i:
        print(f"  WARNING: operand non-manifold (outer={nm_o} inner={nm_i})")
    print(f"  -> operands: {os.path.basename(outer_path)} + "
          f"{os.path.basename(inner_path)}")


# -- Entry point --------------------------------------------------------------

print(f"\nScale: {SCALE:.4f}x   Wall: {WALL_MM} mm   Target: 24\"")
print("=== Serenity UAV -- watertight 2 mm hollow shells (Solidify method) ===")
print(f"Source: {SRC}")
print(f"Output: {OUT}")

for src_name, out_name, pitch in HOLLOW_PARTS:
    process_hollow(src_name, out_name, pitch)

print(f"\nDone.  Operands written to {PARTS}.")
print("Next: python3 airframe/blender-scripts/hollow_manifold.py  (manifold3d "
      "boolean -> final shells), then verify_shells.py, then promote + re-bake.")
