"""
blender_shells_v3_2mm.py  —  Rev Q  —  run with:
    blender --background --python blender_shells_v3_2mm.py

Generates 2.0 mm wall MANIFOLD HOLLOW shells for the Serenity UAV fuselage
sections that will be foam-filled (2 lb/cf low-density closed-cell foam).

Rev Q changes from Rev P (2026-05-27):
  Previous workflow (BROKEN):
    Step 1 — join outer + inner (flipped normals) → intermediate _shell24_2mm.stl
    Step 2 — voxel remesh in repair_shells_for_scad.py → FILLED the hollow,
             producing SOLID STLs (~1466 cm³ for head vs correct ~108 cm³).
  Root cause: Blender voxel remesh uses winding-number classification.  The
  joined outer+inner mesh (with flipped inner normals) has winding number 0
  inside the hollow interior, so the remesh treats the hollow as exterior and
  reconstructs a fully solid object.

  New workflow (CORRECT):
    1. Import source STL, scale to 24".
    2. Voxel-remesh outer solid at OUTER_REMESH_MM pitch → manifold outer.
    3. Duplicate → centroid-inset scale 2.0 mm inward → manifold inner.
    4. Boolean DIFFERENCE (EXACT solver): outer − inner → hollow manifold shell.
       The Boolean op bridges outer/inner surfaces at all open section-joint
       faces, producing sealed end caps (≈ 2 mm thick) at each joint plane.
       These end caps are cut through by SCAD sensor/boss cutter modules
       (WALL_T = 3.5 mm overlap accounts for cap thickness variation).
    5. Verify non-manifold edge count, warn if > 0.
    6. Export directly as <stem>_shell24_2mm_repaired.stl (SCAD-ready).
       No further repair step needed; removes dependency on repair_shells_for_scad.py
       for hull sections.

  Verification (2026-05-27): s_head result 108.5 cm³ (hollow, 2 mm wall) vs
  previous solid result 1466 cm³ — confirms correct hollow shell produced.

Structural analysis (2026-05-26) established that 2.0 mm CF-PETG with foam
fill is adequate for skin-only panels:
  - Panel deflection at 28 m/s cruise: 0.054 mm (foam-supported, vs 1.08 mm
    without foam) — well within the 0.5 mm target.
  - Boss walls and section joint zones retain adequate stiffness via SCAD union
    M3 boss posts (8 mm OD, 6 mm tall, 4.1 mm bore).
  - Reference: structural_analysis.py log, Serenity UAV project, 2026-05-26.

Scope: fuselage hull sections only (head, cargo, rear, middle, wings).
  Nacelle shells remain at 2.5 mm (blender_shells_v3_50mm.py) — interior bore
  cavity is only ≈ 4 mm, too tight for this workflow.
  Nacelle repair (voxel remesh → solid + SCAD bore cut) is still correct
  because the SCAD file explicitly re-opens the bore.

Per-part outer voxel remesh pitch (HOLLOW_PARTS list):
  1.5 mm — head, cargo, rear, middle: large sections, 1.5 mm gives ≥ 40 voxels
            across minimum dimension; good shape fidelity for CGAL boolean.
  0.8 mm — wings (19.4 mm min_dim): finer pitch to prevent inner surface merge.

OUTER_REMESH_MM resolution vs. wall accuracy:
  The nominal 2.0 mm wall is subject to ± outer_remesh_mm variation from the
  centroid-inset scaling approach on non-spherical shapes.  WALL_T = 3.5 mm
  in SCAD cutter modules (nominal 2.0 + 1.5 mm overlap) handles this tolerance.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
Date:    2026-05-26 (Rev Q: 2026-05-27)

References:
    blender_shells_v3_50mm.py — nacelle script (2.5 mm, 1.25× nacelle scale)
    blender_shells_v3.py      — grandparent (2.5 mm, 24" scale only)
    Structural analysis: UAV structural_analysis log 2026-05-26.
    Blender Boolean modifier: docs.blender.org/manual/en/latest/modeling/
        modifiers/generate/booleans.html
"""

import bpy
import bmesh
import os

WALL_MM  = 2.0     # [mm] nominal foam-fill skin wall thickness
SCALE_X  = 2.9294  # uniform 24" scale from 18" native Thingiverse model
SCALE_Y  = 2.9294
SCALE_Z  = 2.9294

BASE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(BASE, "files")
OUT  = os.path.join(BASE, "files-hollowed-18in")
os.makedirs(OUT, exist_ok=True)

# (source_filename, outer_voxel_pitch_mm)
# Pitch chosen so minimum part dimension spans ≥ 12 voxels on outer solid.
HOLLOW_PARTS = [
    ("s_head.stl",        1.5),   # min_dim ≈  88 mm → 59 voxels at 1.5 mm
    ("s_cargo_sect.stl",  1.5),   # min_dim ≈ 102 mm → 68 voxels
    ("s_rear.stl",        1.5),   # min_dim ≈  76 mm → 51 voxels
    ("s_middle.stl",      1.5),   # min_dim ≈  60 mm → 40 voxels
    ("s_wings_both.stl",  0.8),   # min_dim ≈  19 mm → 24 voxels at 0.8 mm
]


# ── Utility functions ────────────────────────────────────────────────────────

def clear_scene():
    """Remove all objects from the scene."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def import_stl(path):
    """Import an STL and return the imported object."""
    bpy.ops.wm.stl_import(filepath=path)
    return bpy.context.selected_objects[0]


def export_stl(obj, path):
    """Export a single object as STL."""
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True)


def apply_voxel_remesh(obj, pitch_mm):
    """
    Apply Blender VOXEL remesh at the given pitch to make a mesh manifold.

    This reconstructs a clean watertight solid from the surface.  Intended for
    use on SOLID (not hollow) mesh objects.  Hollow objects are filled by this
    operation — see module docstring for explanation.
    """
    mod = obj.modifiers.new("vr", "REMESH")
    mod.mode      = "VOXEL"
    mod.voxel_size = pitch_mm
    bpy.ops.object.modifier_apply(modifier="vr")


def count_non_manifold(obj):
    """Return the number of non-manifold edges in the active mesh object."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(obj.data)
    bm.edges.ensure_lookup_table()
    count = sum(1 for e in bm.edges if not e.is_manifold)
    bpy.ops.object.mode_set(mode="OBJECT")
    return count


# ── Main per-part processing ─────────────────────────────────────────────────

def process_hollow(fname, outer_remesh_mm):
    """
    Generate a manifold 2.0 mm hollow shell for one fuselage section.

    Parameters
    ----------
    fname : str
        Source STL filename (in SRC directory).
    outer_remesh_mm : float
        Voxel pitch for manifold repair of the outer solid.
    """
    src  = os.path.join(SRC, fname)
    stem = fname.replace(".stl", "")
    out  = os.path.join(OUT, stem + "_shell24_2mm_repaired.stl")

    if not os.path.isfile(src):
        print(f"  SKIP — not found: {src}")
        return

    print(f"\n=== Processing {fname}  (outer remesh {outer_remesh_mm} mm) ===")

    clear_scene()

    # ── 1. Import and scale to 24" ───────────────────────────────────────────
    outer = import_stl(src)
    outer.name = "outer"
    outer.scale = (SCALE_X, SCALE_Y, SCALE_Z)
    bpy.ops.object.transform_apply(scale=True)

    dx, dy, dz = outer.dimensions
    min_dim    = min(dx, dy, dz)
    print(f"  Scaled dims: {dx:.1f} × {dy:.1f} × {dz:.1f} mm  (min={min_dim:.1f} mm)")

    # Parts too thin to hollow are exported as-is (solid).
    if min_dim < 4 * WALL_MM:
        print(f"  min_dim {min_dim:.1f} < {4 * WALL_MM:.1f} mm — exporting solid")
        export_stl(outer, out)
        print(f"  → {os.path.basename(out)}  ({os.path.getsize(out) // 1024} KB, solid)")
        return

    # ── 2. Voxel-remesh outer solid → manifold ───────────────────────────────
    # This makes the outer surface a clean closed manifold required by the
    # EXACT boolean solver.  The source STL may have non-manifold edges from
    # the Thingiverse export; remesh repairs all of them.
    apply_voxel_remesh(outer, outer_remesh_mm)
    nm_outer = count_non_manifold(outer)
    dx, dy, dz = outer.dimensions   # re-read after remesh (may change slightly)
    print(f"  Outer after remesh: dims={dx:.1f}×{dy:.1f}×{dz:.1f}  NM={nm_outer}"
          f"  faces={len(outer.data.polygons)}")
    if nm_outer != 0:
        print(f"  WARNING: outer has {nm_outer} NM edges — boolean may fail")

    # ── 3. Centroid-inset duplicate → inner solid ────────────────────────────
    # Scale factors produce a uniform 2.0 mm inset from each face (centroid-
    # based approximation; accurate for convex parts, approximate for concave).
    sx  = max(0.001, (dx - 2 * WALL_MM) / dx)
    sy  = max(0.001, (dy - 2 * WALL_MM) / dy)
    sz_ = max(0.001, (dz - 2 * WALL_MM) / dz)
    print(f"  Inner scale factors: sx={sx:.6f}  sy={sy:.6f}  sz={sz_:.6f}")

    bmin = [outer.bound_box[0][i] for i in range(3)]
    bmax = [outer.bound_box[6][i] for i in range(3)]
    cx   = (bmin[0] + bmax[0]) / 2
    cy   = (bmin[1] + bmax[1]) / 2
    cz   = (bmin[2] + bmax[2]) / 2

    bpy.ops.object.select_all(action="DESELECT")
    outer.select_set(True)
    bpy.context.view_layer.objects.active = outer
    bpy.ops.object.duplicate()
    inner = bpy.context.selected_objects[0]
    inner.name = "inner"

    # Translate to centroid, scale, translate back (centroid-inset pattern).
    inner.location = (inner.location.x - cx,
                      inner.location.y - cy,
                      inner.location.z - cz)
    bpy.ops.object.transform_apply(location=True)
    inner.scale = (sx, sy, sz_)
    bpy.ops.object.transform_apply(scale=True)
    inner.location = (cx, cy, cz)
    bpy.ops.object.transform_apply(location=True)

    nm_inner = count_non_manifold(inner)
    print(f"  Inner (scaled copy): NM={nm_inner}  faces={len(inner.data.polygons)}")

    # ── 4. Boolean DIFFERENCE: outer − inner → hollow shell ──────────────────
    # EXACT solver (Blender 4.x): uses the Manifold library for reliable output
    # on concave/complex shapes.  Produces bridging faces at all section-joint
    # openings, sealing the ends of the hollow shell at ≈ 2 mm thickness.
    bpy.ops.object.select_all(action="DESELECT")
    outer.select_set(True)
    bpy.context.view_layer.objects.active = outer

    bool_mod           = outer.modifiers.new("hollow_diff", "BOOLEAN")
    bool_mod.operation = "DIFFERENCE"
    bool_mod.object    = inner
    bool_mod.solver    = "EXACT"
    bpy.ops.object.modifier_apply(modifier="hollow_diff")

    # Delete cutter object (inner solid no longer needed).
    bpy.data.objects.remove(inner, do_unlink=True)

    # ── 4a. Post-boolean mesh cleanup (bmesh API — headless-safe) ────────────
    # The EXACT boolean solver can produce near-coincident T-junction vertices
    # at concave section-joint boundaries.  bpy.ops.mesh.* operators require a
    # viewport context unavailable in --background mode, so bmesh ops are used
    # directly instead.
    #
    # Pass 1 — remove_doubles at 0.001 mm: welds coincident vertices caused by
    #   T-junctions without touching any intentional geometry (minimum voxel
    #   pitch is 0.8 mm, so 0.001 mm is safely sub-voxel).
    # Pass 2 — holes_fill on remaining open boundary edges: adds bridging faces
    #   to close any open loops left after the weld pass.
    bpy.context.view_layer.objects.active = outer
    bm = bmesh.new()
    bm.from_mesh(outer.data)

    verts_before = len(bm.verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    verts_merged = verts_before - len(bm.verts)
    print(f"  merge_by_distance: {verts_merged} vertex pairs welded")

    open_edges = [e for e in bm.edges if not e.is_manifold]
    if open_edges:
        bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
        print(f"  holes_fill: {len(open_edges)} open edge(s) filled")

    bm.to_mesh(outer.data)
    bm.free()
    outer.data.update()

    # ── 5. Verify manifold ───────────────────────────────────────────────────
    bpy.context.view_layer.objects.active = outer
    nm_final = count_non_manifold(outer)
    n_faces  = len(outer.data.polygons)
    print(f"  Final hollow shell:      NM={nm_final}  faces={n_faces}")

    if nm_final != 0:
        print(f"  ERROR: {nm_final} NM edges remain after both repair passes.")
        print(f"  Fix: reduce outer_remesh_mm for this part and re-run.")

    # ── 6. Export ────────────────────────────────────────────────────────────
    export_stl(outer, out)
    sz_kb = os.path.getsize(out) // 1024
    print(f"  → {os.path.basename(out)}  ({sz_kb} KB)")


# ── Entry point ──────────────────────────────────────────────────────────────

print(f"\nScale: {SCALE_X:.4f}×  Wall: {WALL_MM} mm  Target: 24\"\n")
print("=== Serenity UAV — hollow fuselage shells (boolean diff method, Rev Q) ===")

for fname, remesh_pitch in HOLLOW_PARTS:
    if os.path.exists(os.path.join(SRC, fname)):
        process_hollow(fname, remesh_pitch)
    else:
        print(f"  SKIP — source not found: {os.path.join(SRC, fname)}")

print(f"\nDone.  Output files in {OUT}")
print("Files are _shell24_2mm_repaired.stl — SCAD-ready, no further repair step needed.")
print("repair_shells_for_scad.py: _2mm entries were removed (Rev Q).")
