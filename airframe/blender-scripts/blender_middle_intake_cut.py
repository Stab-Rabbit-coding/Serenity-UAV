"""
blender_middle_intake_cut.py  —  Rev C  —  run with:
    blender --background --python blender_middle_intake_cut.py

Cuts 4 radial rectangular intake-scoop windows into the Serenity UAV
middle / neck shell (middle_canonical_shell24.stl).

Coordinate system (sitting on print bed, same as rear shell):
  Z  = longitudinal (ship fore-aft).
        Z = 0   → flat forward interface face (on print bed).
        Z = 73  → aft interface face (mates with cargo section).
  X  = lateral (port / starboard).
  Y  = vertical (belly / dorsal).

Hull XY centroids at intake station Z = 30 mm (from Z-slice analysis):
  X centre = 180.9 mm  (constant through all Z stations)
  Y centre = -77.8 mm  (at Z = 30)
  X half-width  = 88.5 mm  (X span = 177 mm)
  Y half-height = 78.3 mm  (Y span = 156.5 mm)

Four scoop directions (radial in XY plane):
  +Y = dorsal  (upward)
  -X = port
  -Y = ventral (belly)
  +X = starboard

Scoop window dimensions (SCOOP_W × SCOOP_H × SCOOP_AX):
  SCOOP_W   = 75 mm  circumferential width (perpendicular to radial in XY)
  SCOOP_H   = 38 mm  radial depth
  SCOOP_AX  = 38 mm  axial slot length in Z, centred on Z_INTAKE

Capture area: 4 × 75 × 38 = 11 400 mm²  (≈ 107 % of 120 mm EDF fan annulus).

Output:
  stls/fuselage/middle_canonical_edf_intake.stl

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
Date:    2026-06-02  (Rev C — correct Z-longitudinal axis)

References:
  neck_intake_frame.scad Rev C (HULL_W2=89, HULL_H2=78, SCOOP_W=75,
    SCOOP_H=38).
  Z-slice analysis: Serenity UAV project log 2026-06-02.
"""

import bpy
import bmesh
import os

# ── Tunables ──────────────────────────────────────────────────────────────────

# Hull XY centreline (constant X centre; Y centre at Z_INTAKE)
HULL_CX       = 180.9    # [mm]
HULL_CY       = -77.8    # [mm]

# Intake axial station and slot extent (Z direction)
Z_INTAKE      =  30.0    # [mm]  Z centre of scoop windows
SCOOP_AX      =  38.0    # [mm]  axial slot length (Z), ± 19 mm from Z_INTAKE

# Scoop window dimensions
SCOOP_W       =  75.0    # [mm]  circumferential (perpendicular to radial)
SCOOP_H       =  38.0    # [mm]  radial depth into hull
OVERDEPTH     =  10.0    # [mm]  extra depth past centroid to ensure clean cut

# File paths
BASE    = os.path.dirname(os.path.abspath(__file__))
IN_STL  = os.path.join(BASE, "..", "stls", "fuselage",
                        "middle_canonical_shell24.stl")
OUT_STL = os.path.join(BASE, "..", "stls", "fuselage",
                        "middle_canonical_edf_intake.stl")

# ── Utilities ─────────────────────────────────────────────────────────────────

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
    return os.path.getsize(path) // 1024


def make_scoop_cutter(name, z_ctr, ax_len,
                      cx, cy, dx, dy,
                      win_w, win_h, overdepth):
    """
    Rectangular box cutter for one radial intake scoop (Z-longitudinal).

    z_ctr      — Z centre of the axial slot
    ax_len     — axial (Z) length of the slot
    cx, cy     — hull XY centreline position
    dx, dy     — unit radial direction in XY (one of ±1, 0 pairs)
    win_w      — circumferential window width (perpendicular to radial in XY)
    win_h      — radial depth of window
    overdepth  — extra radial depth past centreline to ensure cut-through
    """
    half_az      = ax_len  / 2.0
    half_w       = win_w   / 2.0
    total_radial = win_h + overdepth

    # Perpendicular direction in XY: rotate (dx, dy) 90°
    pdx = -dy
    pdy =  dx

    # 8 corners: sz ∈ {-1,+1} → Z extents,
    #            sp ∈ {-1,+1} → circumferential extents,
    #            sr ∈ {0, total_radial} → radial extents
    corners = []
    for sz in (-1, +1):
        for sp in (-1, +1):
            for sr in (0, total_radial):
                x = cx + dx * sr + pdx * sp * half_w
                y = cy + dy * sr + pdy * sp * half_w
                z = z_ctr + sz * half_az
                corners.append((x, y, z))

    bm   = bmesh.new()
    mesh = bpy.data.meshes.new(name + "_mesh")
    verts = [bm.verts.new(c) for c in corners]
    c = verts

    def face(vl):
        try: bm.faces.new(vl)
        except ValueError: pass

    face([c[0], c[2], c[3], c[1]])   # z_lo face
    face([c[4], c[5], c[7], c[6]])   # z_hi face
    face([c[0], c[4], c[6], c[2]])   # inboard (sr=0)
    face([c[1], c[3], c[7], c[5]])   # outboard (sr=h)
    face([c[0], c[1], c[5], c[4]])   # circumferential sp=-1
    face([c[2], c[6], c[7], c[3]])   # circumferential sp=+1

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh); bm.free(); mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def apply_diff(target, cutter):
    bpy.context.view_layer.objects.active = target
    mod = target.modifiers.new("bd", "BOOLEAN")
    mod.operation = "DIFFERENCE"; mod.object = cutter; mod.solver = "EXACT"
    bpy.ops.object.modifier_apply(modifier="bd")
    bpy.data.objects.remove(cutter, do_unlink=True)


# ── Main ──────────────────────────────────────────────────────────────────────

print("\n=== Serenity UAV — Neck shell radial intake cut (Rev C, Z-longitudinal) ===")
print(f"  Hull centre: X={HULL_CX}, Y={HULL_CY}  Station: Z={Z_INTAKE} mm")
print(f"  Scoop: W={SCOOP_W} mm × H={SCOOP_H} mm × AX={SCOOP_AX} mm (4 dirs)\n")

clear_scene()
hull = import_stl(IN_STL)
hull.name = "neck_shell"

# Four radial directions in XY plane (dx, dy):
#   +Y = dorsal  (up)
#   -X = port
#   -Y = ventral (belly)
#   +X = starboard
SCOOPS = [
    ("dorsal",     0.0,  1.0),
    ("port",      -1.0,  0.0),
    ("ventral",    0.0, -1.0),
    ("starboard",  1.0,  0.0),
]

for label, dx, dy in SCOOPS:
    print(f"  Cutting {label} scoop (dx={dx:+.0f}, dy={dy:+.0f}) …")
    cutter = make_scoop_cutter(
        name      = f"scoop_{label}",
        z_ctr     = Z_INTAKE,
        ax_len    = SCOOP_AX,
        cx        = HULL_CX,
        cy        = HULL_CY,
        dx        = dx,
        dy        = dy,
        win_w     = SCOOP_W,
        win_h     = SCOOP_H,
        overdepth = OVERDEPTH,
    )
    apply_diff(hull, cutter)

sz = export_stl(hull, OUT_STL)
print(f"\n  → {os.path.basename(OUT_STL)}  ({sz} KB)")
print(f"""
  Capture area: 4 × {SCOOP_W:.0f} × {SCOOP_H:.0f} = {4*SCOOP_W*SCOOP_H:.0f} mm²
  Bond neck_intake_frame.stl (Rev C) over the four openings.
""")
print("Done.")
