"""
blender_stator_gen.py  —  run with:
    blender --background --python blender_stator_gen.py

8-fin inter-stage stator for the two 50 mm EDFs in series per nacelle.

Purpose: straighten the swirl imparted by EDF1 (upstream) before the air enters
EDF2 (downstream), recovering the tangential kinetic energy lost to swirl and
improving overall duct thrust by ~5-8%.

Design geometry (one stator per nacelle, print × 4):
  ┌──────────────────────────────────────────────────────────┐
  │  EDF1 (upstream) — Z=80..125mm inside nacelle            │
  │  ────── stator ── Z=60..80mm ──────────────────────────  │
  │  EDF2 (downstream) — Z=15..60mm inside nacelle           │
  └──────────────────────────────────────────────────────────┘

Nacelle bore analysis (s_eng_left_shell24.stl, 24" scale):
  Outer hull OD ~58-60mm at Z=22-100mm → clear bore ~55mm for EDF casing
  Stator OD = 55.0mm → presses into nacelle bore at EDF seat ring

Fin angle calculation (50mm EDF at 6S, ~35,000 RPM):
  Tip velocity  = 2π × 0.025m × (35000/60) = 91.6 m/s
  Exit velocity = sqrt(T / (ρ·A)) = sqrt(8.94 / 0.00240) ≈ 61 m/s
  Tip swirl angle = atan(61/91.6) ≈ 33°  → VANE_ANGLE = 33°

Fin twist: each fin is properly twisted (more angular offset at small radius)
  so the vane angle is geometrically correct at every radius, not just at the tip.
  At hub (r=11mm): angular offset Δθ = H·tan(33°)/r = 20·0.649/11 = 1.18 rad = 67.8°
  At outer (r=27mm): Δθ = 20·0.649/27 = 0.48 rad = 27.6°

OUTPUT: files-hollowed-18in/stator_50mm.stl  (print × 4, one per nacelle)
"""

import bpy
import bmesh
import os
import math

# ── tunables ─────────────────────────────────────────────────────────────────
N_FINS          = 8         # must match number of EDF fan blades or be a multiple
STATOR_OD       = 55.0      # mm — matches EDF casing OD, presses into nacelle bore
STATOR_ID       = 16.0      # mm — hub inner bore (wiring/ESC leads routing)
HUB_OD          = 22.0      # mm — hub outer diameter
FIN_THICKNESS   = 2.0       # mm — vane tangential thickness (3 perimeters at 0.6 nozzle)
STATOR_HEIGHT   = 20.0      # mm — axial length of stator
RING_WALL       = 2.0       # mm — outer ring wall thickness
VANE_ANGLE_DEG  = 33.0      # degrees from axial — counteracts EDF tip swirl

# CW swirl correction: set SWIRL_DIR = +1 for CW EDF (viewed from upstream/intake),
# -1 for CCW. Most 50mm EDFs rotate CW when viewed from the intake (leading) face.
SWIRL_DIR       = +1

N_RING_SEG      = 64        # polygon count for rings (outer and hub)

BASE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(BASE, "files-hollowed-18in", "stator_50mm.stl")
# ─────────────────────────────────────────────────────────────────────────────

R_OUT = STATOR_OD / 2           # 27.5mm
R_HUB = HUB_OD / 2              # 11.0mm
R_BORE = STATOR_ID / 2          # 8.0mm
VANE_A = math.radians(VANE_ANGLE_DEG)
H = STATOR_HEIGHT
T_HALF = FIN_THICKNESS / 2      # 1.0mm half-thickness in arc length


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def export_stl(obj, path):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True)


def vert_at(bm, r, phi, z):
    """Add a BMesh vertex at cylindrical coords (r, phi, z)."""
    return bm.verts.new((r * math.cos(phi), r * math.sin(phi), z))


def add_face(bm, verts):
    try:
        bm.faces.new(verts)
    except ValueError:
        pass  # skip degenerate / duplicate


def make_ring(bm, r_outer, r_inner, z_bot, z_top, n_seg):
    """
    Annular cylinder ring with flat top and bottom.
    Used for outer housing and hub.
    """
    a = [2 * math.pi * i / n_seg for i in range(n_seg)]

    # four vertex rings
    bo = [bm.verts.new((r_outer * math.cos(t), r_outer * math.sin(t), z_bot)) for t in a]
    to = [bm.verts.new((r_outer * math.cos(t), r_outer * math.sin(t), z_top)) for t in a]
    bi = [bm.verts.new((r_inner * math.cos(t), r_inner * math.sin(t), z_bot)) for t in a]
    ti = [bm.verts.new((r_inner * math.cos(t), r_inner * math.sin(t), z_top)) for t in a]

    for i in range(n_seg):
        j = (i + 1) % n_seg
        add_face(bm, [bo[i], bo[j], to[j], to[i]])   # outer wall
        add_face(bm, [bi[i], ti[i], ti[j], bi[j]])   # inner wall
        add_face(bm, [bo[i], bi[i], bi[j], bo[j]])   # bottom annulus
        add_face(bm, [to[i], to[j], ti[j], ti[i]])   # top annulus


def make_fin(bm, phi_center, r_hub, r_out, h, t_half, vane_angle, swirl_dir):
    """
    One twisted stator fin, properly angled at every radius.

    phi_center: angular centre of the fin (radians)
    The fin is twisted so that Δφ = h·tan(vane_angle)/r at each radius,
    correcting for the radially varying swirl velocity.

    Vertices are named: [trailing/leading] × [hub/outer] × [bot/top]
    """
    def delta(r):
        """Angular offset from bot face to top face at radius r (with swirl direction)."""
        return swirl_dir * h * math.tan(vane_angle) / r

    # Angular half-width at each radius (tangential thickness)
    tw_hub = t_half / r_hub   # radians
    tw_out = t_half / r_out

    # Δφ at hub and outer radius (twist from bottom to top face)
    dh_hub = delta(r_hub)
    dh_out = delta(r_out)

    # 8 vertices: 4 on bottom face (z=0), 4 on top face (z=h)
    # Naming: trailing (φ - tw), leading (φ + tw); hub, outer; bot, top
    v = {}
    v['tl_h_b'] = vert_at(bm, r_hub, phi_center - tw_hub, 0.0)           # trailing-hub-bot
    v['ld_h_b'] = vert_at(bm, r_hub, phi_center + tw_hub, 0.0)           # leading-hub-bot
    v['tl_o_b'] = vert_at(bm, r_out, phi_center - tw_out, 0.0)           # trailing-outer-bot
    v['ld_o_b'] = vert_at(bm, r_out, phi_center + tw_out, 0.0)           # leading-outer-bot

    v['tl_h_t'] = vert_at(bm, r_hub, phi_center + dh_hub - tw_hub, h)   # trailing-hub-top
    v['ld_h_t'] = vert_at(bm, r_hub, phi_center + dh_hub + tw_hub, h)   # leading-hub-top
    v['tl_o_t'] = vert_at(bm, r_out, phi_center + dh_out - tw_out, h)   # trailing-outer-top
    v['ld_o_t'] = vert_at(bm, r_out, phi_center + dh_out + tw_out, h)   # leading-outer-top

    # 6 faces of the solid fin
    add_face(bm, [v['tl_o_b'], v['ld_o_b'], v['ld_o_t'], v['tl_o_t']])  # outer face
    add_face(bm, [v['tl_h_b'], v['tl_h_t'], v['ld_h_t'], v['ld_h_b']])  # inner/hub face
    add_face(bm, [v['tl_h_b'], v['tl_o_b'], v['tl_o_t'], v['tl_h_t']])  # trailing side
    add_face(bm, [v['ld_h_b'], v['ld_h_t'], v['ld_o_t'], v['ld_o_b']])  # leading side
    add_face(bm, [v['tl_h_b'], v['ld_h_b'], v['ld_o_b'], v['tl_o_b']])  # bottom (EDF2 side)
    add_face(bm, [v['tl_h_t'], v['tl_o_t'], v['ld_o_t'], v['ld_h_t']])  # top (EDF1 side)


# ─────────────────────────────────────────────────────────────────────────────
clear_scene()

mesh = bpy.data.meshes.new("stator_50mm_mesh")
bm   = bmesh.new()

# Outer housing ring
make_ring(bm,
          r_outer = R_OUT,
          r_inner = R_OUT - RING_WALL,
          z_bot   = 0.0,
          z_top   = H,
          n_seg   = N_RING_SEG)

# Central hub ring
make_ring(bm,
          r_outer = R_HUB,
          r_inner = R_BORE,
          z_bot   = 0.0,
          z_top   = H,
          n_seg   = N_RING_SEG // 2)

# 8 twisted fins
for i in range(N_FINS):
    phi = 2 * math.pi * i / N_FINS
    make_fin(bm,
             phi_center = phi,
             r_hub      = R_HUB,
             r_out      = R_OUT - RING_WALL,  # fins connect to inner face of outer ring
             h          = H,
             t_half     = T_HALF,
             vane_angle = VANE_A,
             swirl_dir  = SWIRL_DIR)

bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(mesh)
bm.free()
mesh.update()

obj = bpy.data.objects.new("stator_50mm", mesh)
bpy.context.collection.objects.link(obj)

export_stl(obj, OUT)
sz = os.path.getsize(OUT) // 1024
print(f"\n=== Stator (50 mm EDF, 8 fins, {VANE_ANGLE_DEG}° vane angle) ===")
print(f"  → stator_50mm.stl  ({sz} KB)")
print(f"  OD={STATOR_OD}mm  hub_OD={HUB_OD}mm  bore_ID={STATOR_ID}mm  height={H}mm")
print(f"  Fin twist: hub Δφ={math.degrees(H*math.tan(VANE_A)/R_HUB):.1f}°  "
      f"outer Δφ={math.degrees(H*math.tan(VANE_A)/(R_OUT-RING_WALL)):.1f}°")
print(f"  Print × 4 (one per nacelle)")
print(f"\n  INSTALL: press-fit between EDF1 and EDF2 in the nacelle bore.")
print(f"  Flat face (z=0) faces downstream (EDF2). Top face faces EDF1.")
print(f"  Secure with 3 dabs of epoxy to outer ring after dry-fit.")
print(f"  SWIRL_DIR={SWIRL_DIR}: vane deflects {'CW' if SWIRL_DIR>0 else 'CCW'} "
      f"inlet swirl to axial. Flip to -1 if EDF runs opposite hand.")
print()
