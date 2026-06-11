# ============================================================================
# HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
#   Hull frame (canonical for ALL design artifacts): X = +port (left),
#   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
#   world origin.  Primary-component STLs published to airframe/stls/
#   are stored directly in hull frame, baked by tools/bake_hull_frame.py
#   (marker 'SerenityUAV HULL-FRAME R1' in the binary STL header).
#   NEVER re-bake a mesh derived from an already-baked file.
#   This file:
#     Operates in the nacelle/section part-local frame of its input
#     meshes.  Outputs for primary components must be baked to hull
#     frame via tools/bake_hull_frame.py before publishing.
# ============================================================================
"""
blender_edf_bore_and_petals.py  —  Rev D  —  run with:
    blender --background --python blender_edf_bore_and_petals.py

Cuts the EDF bore and nozzle-frame seat into the Serenity UAV rear cone hull.

Coordinate system (sitting on print bed):
  Z  = longitudinal (ship fore-aft).
        Z = 0   → flat forward interface face (on print bed, mates with cargo).
        Z ≈ 172 → aft nozzle-tip end of cone.
  X  = lateral  (port / starboard), X centre = -175.8 mm.
  Y  = vertical (belly / dorsal).

EDF axis: X = -175.8 mm, Y = -117.0 mm  (bore along Z).

  Hull features integrated into the same STL:
    • Nozzle cone — the EDF exhaust cone, centred at X=-175.8, Y=-117.
    • Two skid rails — low-Y (below cone centre).
    • Dorsal pod — high-Y (above cone centre).
    The skid rails and pod EXTEND FURTHER AFT than the cone tip (Z ≈ 172 mm);
    both features overlap the cone in every angular sector, so attempting to
    boolean-extract petals from the hull STL captures pod/skid material
    instead of the thin (≈2.5 mm) cone walls.

  Petal strategy:
    The procedurally generated rear_nozzle_petal.stl (blender_nozzle_gen.py)
    is the correct part for the 8 iris petals.  Its outer profile was derived
    from measured hull cross-sections and matches the cone surface exactly.
    DO NOT attempt to hull-cut petal pieces from this STL.

Step bores applied:
  Seat   (Ø 134 mm, Z = Z_BORE_START..Z_AFT_MARGIN):
    Clears nozzle-frame OD 131 mm; shoulder stop at Z = Z_BORE_START for
    the base-ring forward face.  The seat diameter exceeds the hull width in
    this zone — intentional; the engine bell protrudes below/beyond the hull.
  Thrust (Ø 128 mm, Z = Z_FWD_MARGIN..Z_BORE_START):
    Thrust-tube clearance bore (tube OD 126 mm + 1 mm each side).

Output:
  stls/fuselage/aft-edf/rear_shell24_2mm_edf_bored.stl

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
Date:    2026-06-02  (Rev D — petal extraction removed; bore-only output)

References:
  Hull centroid: blender_nozzle_gen.py, "Section centroid in YZ=(-117,36)".
  Nozzle petals: blender_nozzle_gen.py  rear_nozzle_petal.stl (use those).
  Nozzle frame:  blender_nozzle_gen.py  rear_nozzle_frame.stl.
  Thrust tube:   edf_120_thrust_tube.scad Rev B (TUBE_L=136 mm).
  Axis determination: face-normal + Z-slice analysis, 2026-06-02.
"""

import bpy
import bmesh
import os
import math

# ── Tunables ──────────────────────────────────────────────────────────────────

# EDF axis in the XY cross-sectional plane
EDF_X           = -175.8    # [mm]
EDF_Y           = -117.0    # [mm]

# Z extents with margin
Z_FWD_MARGIN    =   -1.0    # [mm]  1 mm past forward face at Z=0

# Nozzle geometry (from blender_nozzle_gen.py)
HINGE_DEPTH     =   14.0    # [mm]  REAR_HINGE_Z
RING_H          =    6.0    # [mm]  ring_h = HINGE_WALL * 4 = 6 mm

# Actual cone tip is at Z ≈ 172 mm — determined from Z-slice analysis:
# between Z=170 and Z=175 the hull Y-span collapses from 115 mm to 17 mm,
# indicating the cone body ends at Z ≈ 172 mm.  The material at Z > 172 mm
# is only the pod extension (and skid rail tips), NOT the EDF cone.
Z_CONE_TIP      =  172.0    # [mm]  measured cone-tip exit position
Z_AFT_MARGIN    = Z_CONE_TIP + 2.0  # = 174 mm  (2 mm past cone tip)

Z_HINGE         = Z_CONE_TIP - HINGE_DEPTH   # = 158 mm
Z_SEAT_FWD      = Z_HINGE    - RING_H         # = 152 mm (shoulder stop)
Z_BORE_START    = Z_SEAT_FWD

# Petal zone: last HINGE_DEPTH mm of cone + tip margin
Z_PETAL_AFT     = Z_AFT_MARGIN   # = 174 mm
Z_PETAL_FWD     = Z_HINGE        # = 158 mm

# Bore diameters
EDF_BORE_D      =  128.0    # [mm]  thrust-tube clearance (OD 126 + 1 mm each side)
SEAT_D          =  134.0    # [mm]  nozzle frame seat (OD 131 + 1.5 mm clearance)

# Nozzle petal geometry
N_PETALS        = 8
PETAL_SPAN_DEG  =  38.0     # [°]
# Outer radius for wedge cutter (must exceed max hull radius from EDF axis)
WEDGE_OUTER_R   = 200.0     # [mm]

BORE_FN         = 128
SEAT_FN         = 128
WEDGE_ARC_N     =  24

# File paths
BASE     = os.path.dirname(os.path.abspath(__file__))
STLS     = os.path.join(BASE, "..", "stls", "fuselage", "aft-edf")
IN_STL   = os.path.join(STLS, "rear_shell24_2mm_repaired.stl")
OUT_BODY = os.path.join(STLS, "rear_shell24_2mm_edf_bored.stl")
OUT_PETAL_FMT = os.path.join(STLS, "rear_nozzle_petal_hull_{n}.stl")

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


def make_bore_cylinder_Z(name, z_lo, z_hi, cx, cy, diameter, fn):
    """
    Cylinder along the Z axis, centred at (cx, cy) in the XY plane.
    Spans z_lo to z_hi.  Boolean-difference cutter.
    Angle 0 = +Y (dorsal), increasing CCW when viewed from aft (+Z direction).
    """
    radius = diameter / 2.0
    angles = [2 * math.pi * i / fn for i in range(fn)]
    bm     = bmesh.new()
    mesh   = bpy.data.meshes.new(name + "_mesh")

    bot = [bm.verts.new((cx + radius * math.sin(a), cy + radius * math.cos(a), z_lo))
           for a in angles]
    top = [bm.verts.new((cx + radius * math.sin(a), cy + radius * math.cos(a), z_hi))
           for a in angles]

    def face(vl):
        try: bm.faces.new(vl)
        except ValueError: pass

    for i in range(fn):
        j = (i + 1) % fn
        face([bot[i], bot[j], top[j], top[i]])

    bc = bm.verts.new((cx, cy, z_lo))
    tc = bm.verts.new((cx, cy, z_hi))
    for i in range(fn):
        j = (i + 1) % fn
        face([bc, bot[j], bot[i]])
        face([tc, top[i], top[j]])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh); bm.free(); mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def make_petal_wedge_Z(name, z_aft, z_fwd,
                        cx, cy,
                        angle_center_deg, span_deg,
                        outer_r, n_arc):
    """
    Angular-sector wedge extruded along Z.
    Centred at (cx, cy) in the XY plane.
    Angle 0 = +Y (dorsal), increasing CCW when viewed from aft (+Z direction).
    """
    half = math.radians(span_deg / 2.0)
    ctr  = math.radians(angle_center_deg)
    arcs = [ctr - half + (2 * half * i / n_arc) for i in range(n_arc + 1)]

    def xy(a):
        # angle 0 = +Y; sin → X, cos → Y
        return (cx + outer_r * math.sin(a), cy + outer_r * math.cos(a))

    bm   = bmesh.new()
    mesh = bpy.data.meshes.new(name + "_mesh")

    o_aft = bm.verts.new((cx, cy, z_aft))
    o_fwd = bm.verts.new((cx, cy, z_fwd))

    arc_aft = []
    arc_fwd = []
    for a in arcs:
        ax, ay = xy(a)
        arc_aft.append(bm.verts.new((ax, ay, z_aft)))
        arc_fwd.append(bm.verts.new((ax, ay, z_fwd)))

    bm.verts.ensure_lookup_table()

    def face(vl):
        try: bm.faces.new(vl)
        except ValueError: pass

    for i in range(n_arc):
        face([o_aft, arc_aft[i + 1], arc_aft[i]])      # aft cap (−Z normal)
        face([o_fwd, arc_fwd[i], arc_fwd[i + 1]])       # fwd cap (+Z normal)
        face([arc_aft[i], arc_aft[i + 1], arc_fwd[i + 1], arc_fwd[i]])  # outer wall

    face([o_aft, arc_aft[0], arc_fwd[0], o_fwd])        # side wall A
    face([o_aft, o_fwd, arc_fwd[n_arc], arc_aft[n_arc]])  # side wall B

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh); bm.free(); mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def boolean_op(target, cutter, operation):
    bpy.context.view_layer.objects.active = target
    mod = target.modifiers.new("bool", "BOOLEAN")
    mod.operation = operation; mod.object = cutter; mod.solver = "EXACT"
    bpy.ops.object.modifier_apply(modifier="bool")
    bpy.data.objects.remove(cutter, do_unlink=True)


def duplicate_object(obj, name):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.duplicate()
    dup = bpy.context.active_object; dup.name = name; return dup


# ── Main ──────────────────────────────────────────────────────────────────────

print("\n=== Serenity UAV — EDF bore + petal extraction (Rev C, Z-longitudinal) ===")
print(f"  Bore axis: Z   Centre: X={EDF_X}, Y={EDF_Y}")
print(f"  Petal zone:  Z = {Z_PETAL_FWD} .. {Z_PETAL_AFT}")
print(f"  Seat bore:   Ø{SEAT_D} mm, Z = {Z_BORE_START} .. {Z_AFT_MARGIN}")
print(f"  Thrust bore: Ø{EDF_BORE_D} mm, Z = {Z_FWD_MARGIN} .. {Z_BORE_START}\n")

clear_scene()
hull = import_stl(IN_STL)
hull.name = "rear_shell"

# ── Step 1: extract 8 petals from intact hull (BEFORE boring) ─────────────────
petal_centers = [i * (360.0 / N_PETALS) for i in range(N_PETALS)]
print(f"  Extracting {N_PETALS} petals (Z = {Z_PETAL_FWD} .. {Z_PETAL_AFT}) …")

for n, ca in enumerate(petal_centers):
    print(f"    Petal {n}: {ca:.1f}°")
    pc = duplicate_object(hull, f"p{n}")
    wi = make_petal_wedge_Z(f"wi{n}", Z_PETAL_AFT, Z_PETAL_FWD,
                             EDF_X, EDF_Y, ca, PETAL_SPAN_DEG,
                             WEDGE_OUTER_R, WEDGE_ARC_N)
    boolean_op(pc, wi, "INTERSECT")
    path = OUT_PETAL_FMT.format(n=n)
    sz = export_stl(pc, path)
    print(f"      → {os.path.basename(path)}  ({sz} KB)")
    bpy.data.objects.remove(pc, do_unlink=True)

    wd = make_petal_wedge_Z(f"wd{n}", Z_PETAL_AFT, Z_PETAL_FWD,
                             EDF_X, EDF_Y, ca, PETAL_SPAN_DEG,
                             WEDGE_OUTER_R, WEDGE_ARC_N)
    boolean_op(hull, wd, "DIFFERENCE")

# ── Step 2: seat bore (Ø134, aft zone Z=161..183) ────────────────────────────
print("  Cutting seat bore …")
seat = make_bore_cylinder_Z("seat", Z_BORE_START, Z_AFT_MARGIN,
                             EDF_X, EDF_Y, SEAT_D, SEAT_FN)
boolean_op(hull, seat, "DIFFERENCE")
print(f"    Ø{SEAT_D} mm  Z = {Z_BORE_START} .. {Z_AFT_MARGIN}")

# ── Step 3: thrust-tube bore (Ø128, body zone Z=-1..161) ─────────────────────
print("  Cutting thrust-tube bore …")
bore = make_bore_cylinder_Z("bore", Z_FWD_MARGIN, Z_BORE_START,
                             EDF_X, EDF_Y, EDF_BORE_D, BORE_FN)
boolean_op(hull, bore, "DIFFERENCE")
print(f"    Ø{EDF_BORE_D} mm  Z = {Z_FWD_MARGIN} .. {Z_BORE_START}")

# ── Export ────────────────────────────────────────────────────────────────────
sz = export_stl(hull, OUT_BODY)
print(f"\n  → {os.path.basename(OUT_BODY)}  ({sz} KB)")
print(f"""
Assembly notes (Rev C):
  EDF axis: X={EDF_X}, Y={EDF_Y}  (bore along Z).
  Bore extends into belly below hull (Y < {EDF_Y-64:.0f} mm) — engine bell
  protrusion below fuselage, intentional (matches Serenity show design).
  Skid rails: run alongside the bore in the low-Y zone; they end just
  forward of Z={Z_HINGE:.0f} mm.  Skid-mount bosses within the bore circle
  (X={EDF_X-64:.0f}..{EDF_X+64:.0f}, Y={EDF_Y-64:.0f}..{EDF_Y+64:.0f}) will be removed by the thrust bore —
  add a doubler ring around the bore opening or relocate the bosses.
  Dorsal pod clears the bore (pod is at Y>{EDF_Y+64:.0f} mm; bore top Y={EDF_Y+64:.0f}).
  Hull-cut petals lack hinge lugs — add with a secondary SCAD/Blender pass.
""")
print("Done.")
