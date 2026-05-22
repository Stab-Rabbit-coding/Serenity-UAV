"""
blender_nacelle_integrated_v1.py  —  run with:
    blender --background --python blender_nacelle_integrated_v1.py

Rev N: integrated-stator nacelle shells for the Serenity-UAV 24" design.

Generates two nacelle shells with 11-fin twisted inter-stage stators built
directly into the bore, replacing the separate press-fit stator_50mm.stl.
The fins are solid geometry added at Z=STATOR_BOT..Z=STATOR_TOP inside each
nacelle bore, joined into the same mesh that gets printed as the nacelle.

Design layout (bore runs along Z; Z=0 is the aft / nozzle exit end):
  Nozzle / exit face    Z = 0
  EDF2 (downstream)    Z = 5 .. 50 mm   (50mm EDF between stator and nozzle)
  Stator gap (clearance)Z = 50 .. 53 mm
  Stator fins           Z = 53 .. 73 mm  (STATOR_HEIGHT = 20 mm)
  Stator gap            Z = 73 .. 76 mm
  EDF1 (upstream)       Z = 76 .. 126 mm (50 mm including motor can)
  Intake bell           Z = 126 .. 148 mm

Nozzle iris behavior:
  - Ring is fixed to the nacelle shell at Z = NOZZLE_HINGE_Z.
  - Internal rack teeth on the ring mate with a crown pinion on the
    nacelle pivot linkage, so tilt motion drives the iris.
  - When the nacelle is vertical, the ring is driven toward the OPEN
    position; when horizontal, the ring is driven toward CLOSED.
  - This keeps the dual 6S 50mm EDF exhaust path directed through the
    nozzle bore without adding a separate hinged actuator.

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

try:
    import bpy
    import bmesh
    running_in_blender = True
except Exception:
    bpy = None
    bmesh = None
    running_in_blender = False
import os
import math

if not running_in_blender and __name__ == "__main__":
    print("ERROR: 'bpy' is not available. Run this script inside Blender:")
    print("  blender --background --python blender_nacelle_integrated_v1.py")
    raise SystemExit(1)

# ── tunables ─────────────────────────────────────────────────────────────────
N_FINS         = 11
STATOR_BOT     = 53.0      # mm from Z=0 (nozzle face) — bottom of stator
STATOR_HEIGHT  = 20.0      # mm axial extent of stator
FIN_THICKNESS  = 2.0       # mm tangential thickness of each fin
VANE_ANGLE_DEG = 33.0      # degrees from axial — matches 50mm 6S EDF tip swirl
R_FIN_OUT      = 27.0      # mm — fin outer radius (just inside EDF casing)
R_HUB_OUT      = 11.0      # mm — hub outer radius
R_HUB_BORE     = 8.0       # mm — hub inner bore (wire routing)
N_HUB_SEG      = 32        # polygon count for hub ring

NOZZLE_HINGE_Z = 15.0      # mm from Z=0 (nozzle face) — fixed-ring attachment face
NOZZLE_RING_OUTER_R = 31.0  # mm — ring outer radius at hinge
NOZZLE_RING_INNER_R = 24.5  # mm — ring inner radius at hinge
NOZZLE_RING_H = 6.0        # mm — ring axial height
NOZZLE_RING_TEETH = 32      # internal rack teeth for passive crown pinion actuation
NOZZLE_RING_RACK_DEPTH = 1.0
NOZZLE_RING_RACK_WIDTH = 0.36
NOZZLE_CUT_Z = 21.0         # mm — remove internal shell faces under the hinge region
NOZZLE_CUT_R = 26.0         # mm — cut radius to clear the ring pocket while preserving outer hull (increased by 1mm diameter)
NOZZLE_RING_BASE_FROM_NOZZLE = 4.5 * 25.4  # mm from nozzle face to the base of the new petals/ring

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


def cut_nozzle_shell_region(obj, cx, cy, z_threshold, r_max, cut_above=False):
    """Remove internal shell faces inside the nozzle ring pocket region.

    If cut_above is False, delete faces with center Z <= z_threshold.
    If cut_above is True, delete faces with center Z >= z_threshold.
    """
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(obj.data)
    bm.faces.ensure_lookup_table()

    r2 = r_max * r_max
    to_delete = []
    for face in bm.faces:
        n = len(face.verts)
        if n == 0:
            continue
        fc_z = sum(v.co.z for v in face.verts) / n
        if (fc_z >= z_threshold if cut_above else fc_z <= z_threshold):
            inside = False
            for v in face.verts:
                dx = v.co.x - cx
                dy = v.co.y - cy
                if dx * dx + dy * dy < r2:
                    inside = True
                    break
            if inside:
                to_delete.append(face)

    bmesh.ops.delete(bm, geom=to_delete, context="FACES")
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode="OBJECT")
    return len(to_delete)


def make_nozzle_ring(name, cx, cy, outer_r, inner_r, axial_h,
                     n_seg=128, rack_teeth=0, rack_depth=0.0,
                     rack_width=0.4):
    """Build a fixed nozzle ring with optional internal rack teeth."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    bm   = bmesh.new()

    if rack_teeth > 0:
        n_seg = max(n_seg, rack_teeth * 8)

    def inner_radius(angle):
        if rack_teeth <= 0:
            return inner_r
        pitch = 2 * math.pi / rack_teeth
        x = (angle % pitch) / pitch
        if x < rack_width or x > 1.0 - rack_width:
            return inner_r - rack_depth
        return inner_r

    angles = [2 * math.pi * i / n_seg for i in range(n_seg)]
    bot_o = [bm.verts.new((cx + outer_r * math.cos(a),
                          cy + outer_r * math.sin(a),
                          NOZZLE_HINGE_Z))
             for a in angles]
    top_o = [bm.verts.new((cx + outer_r * math.cos(a),
                          cy + outer_r * math.sin(a),
                          NOZZLE_HINGE_Z + axial_h))
             for a in angles]
    bot_i = [bm.verts.new((cx + inner_radius(a) * math.cos(a),
                          cy + inner_radius(a) * math.sin(a),
                          NOZZLE_HINGE_Z))
             for a in angles]
    top_i = [bm.verts.new((cx + inner_radius(a) * math.cos(a),
                          cy + inner_radius(a) * math.sin(a),
                          NOZZLE_HINGE_Z + axial_h))
             for a in angles]

    def face(vlist):
        try:
            bm.faces.new(vlist)
        except ValueError:
            pass

    for i in range(n_seg):
        j = (i + 1) % n_seg
        face([bot_o[i], bot_o[j], top_o[j], top_o[i]])     # outer wall
        face([bot_i[i], top_i[i], top_i[j], bot_i[j]])     # inner wall
        face([bot_o[i], bot_i[i], bot_i[j], bot_o[j]])     # bottom annulus
        face([top_o[i], top_o[j], top_i[j], top_i[i]])     # top annulus

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


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

    # 11 twisted fins
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
    shell_min_z = min(zs)
    shell_max_z = max(zs)
    print(f"  Shell Z range: {shell_min_z:.1f}..{shell_max_z:.1f} mm  "
          f"(bore axis = Z, intake = Z=0, exhaust = Z={shell_max_z:.1f})")

    ring_bottom_z = shell_max_z - 2 * NOZZLE_HINGE_Z
    removed_faces = cut_nozzle_shell_region(nacelle,
                                           cfg["bore_cx"], cfg["bore_cy"],
                                           ring_bottom_z, NOZZLE_CUT_R,
                                           cut_above=True)
    print(f"  Removed {removed_faces} internal faces to clear nozzle ring pocket at Z>={ring_bottom_z:.1f}")

    # Build stator mesh at bore centre and mirror it into the shell's actual intake-to-exhaust Z axis.
    stator_mesh = build_stator_mesh(cfg["bore_cx"], cfg["bore_cy"], cfg["swirl"])
    stator_obj  = bpy.data.objects.new("stator_fins", stator_mesh)
    stator_obj.location.z = shell_max_z - (STATOR_BOT + STATOR_TOP)
    bpy.context.collection.objects.link(stator_obj)

    nozzle_ring = make_nozzle_ring("nozzle_ring",
                                   cfg["bore_cx"], cfg["bore_cy"],
                                   NOZZLE_RING_OUTER_R, NOZZLE_RING_INNER_R,
                                   NOZZLE_RING_H,
                                   n_seg = N_HUB_SEG,
                                   rack_teeth = NOZZLE_RING_TEETH,
                                   rack_depth = NOZZLE_RING_RACK_DEPTH,
                                   rack_width = NOZZLE_RING_RACK_WIDTH)
    nozzle_ring.location.z = shell_max_z - 2 * NOZZLE_HINGE_Z
    print(f"  Added nozzle ring with internal rack: {NOZZLE_RING_TEETH} teeth, "
          f"{NOZZLE_RING_RACK_DEPTH:.1f}mm depth")
    print("  Nozzle iris is sized for the dual 50mm EDF path and is intended "
          "to open with vertical nacelle tilt and close with horizontal tilt.")

    # Join nacelle shell + stator + nozzle ring into one printable object
    combined = join_objects([nacelle, stator_obj, nozzle_ring])
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
