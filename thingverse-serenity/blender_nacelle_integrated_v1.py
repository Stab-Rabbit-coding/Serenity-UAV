"""
blender_nacelle_integrated_v1.py  —  run with:
    blender --background --python blender_nacelle_integrated_v1.py

Rev N: integrated-stator nacelle shells for the Serenity-UAV 24" design.

Generates two nacelle shells with 8-fin twisted inter-stage stators built
directly into the bore, replacing the separate press-fit stator_50mm.stl.
The fins are solid geometry added at Z=STATOR_BOT..Z=STATOR_TOP inside each
nacelle bore, joined into the same mesh that gets printed as the nacelle.

Design layout (bore runs along Z; Z=0 is the aft / nozzle exit end):
  Nozzle / exit face    Z = 0
  EDF2 (downstream)    Z = 5 .. 50 mm   (45 mm seat depth)
  Stator gap (clearance)Z = 50 .. 53 mm
  Stator fins           Z = 53 .. 73 mm  (STATOR_HEIGHT = 20 mm)
  Stator gap            Z = 73 .. 76 mm
  EDF1 (upstream)       Z = 76 .. 126 mm (50 mm including motor can)
  Intake bell           Z = 126 .. 148 mm

Counter-rotating EDF pairs — swirl direction is opposite per nacelle so
torque reaction cancels across the airframe:
  Port  (left)  nacelle: EDFs rotate CW viewed from intake → SWIRL_DIR = +1
  Starboard (right) nacelle: EDFs rotate CCW from intake   → SWIRL_DIR = −1

Nacelle bore geometry (measured from s_eng_*_shell24.stl at 24" scale):
  Left bore centre:  X = 34.2, Y = −152.5  (Z axis is bore axis)
  Right bore centre: X = 124.0, Y = −152.5
  Bore inscribed ID ≈ 55.5 mm (X), 62 mm (Y) — treats bore as 55 mm nominal
  EDF casing OD = 55 mm → R_FIN_OUT = 27.0 mm (0.5 mm inside EDF casing)

Outputs (files-hollowed-18in/):
  s_eng_left_stator_shell24.stl   — port nacelle, CW stator fins
  s_eng_right_stator_shell24.stl  — starboard nacelle, CCW stator fins
"""

import bpy
import bmesh
import os
import math

# ── tunables ─────────────────────────────────────────────────────────────────
N_FINS         = 8
STATOR_BOT     = 53.0      # mm from Z=0 (nozzle face) — bottom of stator
STATOR_HEIGHT  = 20.0      # mm axial extent of stator
FIN_THICKNESS  = 2.0       # mm tangential thickness of each fin
VANE_ANGLE_DEG = 33.0      # degrees from axial — matches 50mm 6S EDF tip swirl
R_FIN_OUT      = 27.0      # mm — fin outer radius (just inside EDF casing)
R_HUB_OUT      = 11.0      # mm — hub outer radius
R_HUB_BORE     = 8.0       # mm — hub inner bore (wire routing)
N_HUB_SEG      = 32        # polygon count for hub ring

# Nacelle bore centres (world-space X, Y; bore axis = Z)
NACELLES = [
    {
        "in_stl":  "s_eng_left_shell24.stl",
        "out_stl": "s_eng_left_stator_shell24.stl",
        "bore_cx": 34.2,
        "bore_cy": -152.5,
        "swirl":   +1,      # CW viewed from intake (port nacelle)
        "label":   "PORT (left), CW stator",
    },
    {
        "in_stl":  "s_eng_right_shell24.stl",
        "out_stl": "s_eng_right_stator_shell24.stl",
        "bore_cx": 124.0,
        "bore_cy": -152.5,
        "swirl":   -1,      # CCW viewed from intake (starboard nacelle)
        "label":   "STARBOARD (right), CCW stator",
    },
]

BASE = os.path.dirname(os.path.abspath(__file__))
IN_DIR  = os.path.join(BASE, "files-hollowed-18in")
OUT_DIR = IN_DIR
# ─────────────────────────────────────────────────────────────────────────────

STATOR_TOP = STATOR_BOT + STATOR_HEIGHT
VANE_A     = math.radians(VANE_ANGLE_DEG)
T_HALF     = FIN_THICKNESS / 2


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


def add_face(bm, verts):
    try:
        bm.faces.new(verts)
    except ValueError:
        pass


def vert_at_cyl(bm, cx, cy, r, phi, z):
    """Vertex in world space at cylindrical coords relative to bore centre."""
    return bm.verts.new((cx + r * math.cos(phi), cy + r * math.sin(phi), z))


def add_hub_ring(bm, cx, cy, r_out, r_in, z_bot, z_top, n_seg):
    """Annular hub ring (hollow tube) for cable routing through stator centre."""
    a = [2 * math.pi * i / n_seg for i in range(n_seg)]
    bo = [bm.verts.new((cx + r_out * math.cos(t), cy + r_out * math.sin(t), z_bot)) for t in a]
    to = [bm.verts.new((cx + r_out * math.cos(t), cy + r_out * math.sin(t), z_top)) for t in a]
    bi = [bm.verts.new((cx + r_in  * math.cos(t), cy + r_in  * math.sin(t), z_bot)) for t in a]
    ti = [bm.verts.new((cx + r_in  * math.cos(t), cy + r_in  * math.sin(t), z_top)) for t in a]
    for i in range(n_seg):
        j = (i + 1) % n_seg
        add_face(bm, [bo[i], bo[j], to[j], to[i]])   # outer wall
        add_face(bm, [bi[i], ti[i], ti[j], bi[j]])   # inner wall (bore)
        add_face(bm, [bo[i], bi[i], bi[j], bo[j]])   # bottom annulus
        add_face(bm, [to[i], to[j], ti[j], ti[i]])   # top annulus


def add_fin(bm, cx, cy, phi_center, r_hub, r_out, z_bot, h,
            t_half, vane_angle, swirl_dir):
    """
    One twisted stator fin in world space.

    The fin is twisted so Δφ = swirl_dir × h × tan(vane_angle) / r at each
    radius, correcting radially-varying EDF swirl.  The bottom face (z_bot)
    is the downstream (EDF2) side; the top face (z_bot+h) faces EDF1.

    Eight vertices: trailing/leading × hub/outer × bot/top.
    """
    def delta(r):
        return swirl_dir * h * math.tan(vane_angle) / r

    tw_h = t_half / r_hub
    tw_o = t_half / r_out
    dh_h = delta(r_hub)
    dh_o = delta(r_out)

    def v(r, phi, z):
        return bm.verts.new((cx + r * math.cos(phi), cy + r * math.sin(phi), z))

    # bottom face verts
    tl_h_b = v(r_hub, phi_center - tw_h, z_bot)
    ld_h_b = v(r_hub, phi_center + tw_h, z_bot)
    tl_o_b = v(r_out, phi_center - tw_o, z_bot)
    ld_o_b = v(r_out, phi_center + tw_o, z_bot)
    # top face verts (twisted)
    z_top = z_bot + h
    tl_h_t = v(r_hub, phi_center + dh_h - tw_h, z_top)
    ld_h_t = v(r_hub, phi_center + dh_h + tw_h, z_top)
    tl_o_t = v(r_out, phi_center + dh_o - tw_o, z_top)
    ld_o_t = v(r_out, phi_center + dh_o + tw_o, z_top)

    add_face(bm, [tl_o_b, ld_o_b, ld_o_t, tl_o_t])  # outer face
    add_face(bm, [tl_h_b, tl_h_t, ld_h_t, ld_h_b])  # hub face
    add_face(bm, [tl_h_b, tl_o_b, tl_o_t, tl_h_t])  # trailing side
    add_face(bm, [ld_h_b, ld_h_t, ld_o_t, ld_o_b])  # leading side
    add_face(bm, [tl_h_b, ld_h_b, ld_o_b, tl_o_b])  # bottom (EDF2 side)
    add_face(bm, [tl_h_t, tl_o_t, ld_o_t, ld_h_t])  # top (EDF1 side)


def build_stator_mesh(cx, cy, swirl_dir):
    """Return a new Blender mesh containing the stator fins + hub ring."""
    mesh = bpy.data.meshes.new("stator_integrated")
    bm   = bmesh.new()

    # Hub ring (cable routing passage)
    add_hub_ring(bm, cx, cy,
                 r_out = R_HUB_OUT,
                 r_in  = R_HUB_BORE,
                 z_bot = STATOR_BOT,
                 z_top = STATOR_TOP,
                 n_seg = N_HUB_SEG)

    # 8 twisted fins
    for i in range(N_FINS):
        phi = 2 * math.pi * i / N_FINS
        add_fin(bm, cx, cy,
                phi_center = phi,
                r_hub      = R_HUB_OUT,
                r_out      = R_FIN_OUT,
                z_bot      = STATOR_BOT,
                h          = STATOR_HEIGHT,
                t_half     = T_HALF,
                vane_angle = VANE_A,
                swirl_dir  = swirl_dir)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return mesh


def join_objects(objs):
    """Join a list of Blender objects into the first one and return it."""
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    return bpy.context.active_object


# ─────────────────────────────────────────────────────────────────────────────
for cfg in NACELLES:
    print(f"\n=== Processing {cfg['label']} ===")
    clear_scene()

    in_path  = os.path.join(IN_DIR,  cfg["in_stl"])
    out_path = os.path.join(OUT_DIR, cfg["out_stl"])

    # Import nacelle shell
    nacelle = import_stl(in_path)
    nacelle.name = "nacelle_shell"
    bb = nacelle.bound_box
    zs = [v[2] for v in bb]
    print(f"  Shell Z range: {min(zs):.1f}..{max(zs):.1f} mm  "
          f"(bore axis = Z, nozzle face = Z=0)")

    # Build stator mesh at bore centre
    stator_mesh = build_stator_mesh(cfg["bore_cx"], cfg["bore_cy"], cfg["swirl"])
    stator_obj  = bpy.data.objects.new("stator_fins", stator_mesh)
    bpy.context.collection.objects.link(stator_obj)

    # Join nacelle shell + stator into one printable object
    combined = join_objects([nacelle, stator_obj])
    combined.name = cfg["out_stl"].replace(".stl", "")

    export_stl(combined, out_path)
    sz = os.path.getsize(out_path) // 1024
    twist_hub = math.degrees(STATOR_HEIGHT * math.tan(VANE_A) / R_HUB_OUT)
    twist_out = math.degrees(STATOR_HEIGHT * math.tan(VANE_A) / R_FIN_OUT)
    print(f"  → {cfg['out_stl']}  ({sz} KB)")
    print(f"  Stator: Z={STATOR_BOT:.0f}..{STATOR_TOP:.0f}mm  "
          f"swirl_dir={cfg['swirl']:+d}  "
          f"fin_twist hub={twist_hub:.1f}° outer={twist_out:.1f}°")
    print(f"  EDF2 seat: Z=5..50 mm  |  EDF1 seat: Z=76..126 mm")
    print(f"  Hub bore ID={2*R_HUB_BORE:.0f}mm for EDF lead routing")

print("\nDone.  Print each nacelle shell in CF-PETG at 0.15mm / 25% infill.")
print("EDF installation:")
print("  1. Press EDF2 in from nozzle end (Z=0), seat at Z=5, leads up through hub bore.")
print("  2. Apply 3 dabs structural epoxy to EDF2 casing at Z=50 shoulder.")
print("  3. Route EDF2 leads through hub bore and out the fore (intake) end.")
print("  4. Press EDF1 in from fore end, seat at Z=76, leads forward.")
print("  5. Apply 3 dabs structural epoxy to EDF1 casing at Z=76 shoulder.")
print("  6. Confirm fin vanes visible in gap Z=50..76 — stator is between EDFs.")
print("\nSWIRL DIRECTION:")
print("  Port  (left)  nacelle: SWIRL_DIR=+1 — EDF motor wired CW from intake.")
print("  Stbd (right) nacelle: SWIRL_DIR=−1 — EDF motor wired CCW from intake.")
print("  Verify rotation before sealing: spin-test each EDF before installing nacelle.")
