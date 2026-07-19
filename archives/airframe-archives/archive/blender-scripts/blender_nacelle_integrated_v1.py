"""
blender_nacelle_integrated_v1.py  —  run with:
    blender --background --python blender_nacelle_integrated_v1.py

Rev N: integrated-stator nacelle shells for the Serenity-UAV 24" design.

Generates two nacelle shells with 11-fin twisted inter-stage stators built
directly into the bore, replacing the separate press-fit stator_50mm.stl.
The fins are solid geometry added at Z=STATOR_BOT..Z=STATOR_TOP inside each
nacelle bore, joined into the same mesh that gets printed as the nacelle.

Design layout (bore runs along Z; Z=0 is the intake face, Z≈148 is the exhaust/nozzle exit):
  Intake bell           Z =   0 ..  22 mm
  EDF1 (upstream)       Z =  22 ..  72 mm  (50 mm EDF, motor at intake end)
  Stator gap            Z =  72 ..  75 mm
  Stator fins           Z =  75 ..  95 mm  (STATOR_HEIGHT = 20 mm)
  Stator gap            Z =  95 ..  98 mm
  EDF2 (downstream)     Z =  98 .. 143 mm  (50 mm EDF, motor at stator end)
  Nozzle exit face      Z ≈ 143 .. 148 mm  (iris ring + petal region)

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
    from mathutils import Matrix, Vector
    running_in_blender = True
except Exception:
    bpy = None
    bmesh = None
    Matrix = None
    Vector = None
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
R_FIN_OUT      = 25.0      # mm — fin outer radius = 50mm fan radius (flush with bore)
R_HUB_OUT      = 16.0      # mm — hub outer radius (fits Xfly 2627 motor can ~30mm OD)
R_HUB_BORE     = 10.0      # mm — hub inner bore (wire routing)
N_HUB_SEG      = 32        # polygon count for hub ring

NOZZLE_HINGE_Z = 15.0      # mm from Z=0 (nozzle face) — fixed-ring attachment face
NOZZLE_RING_OUTER_R = 31.0  # mm — ring outer radius at hinge
NOZZLE_RING_INNER_R = 25.0  # mm — ring inner radius = bore ID (50mm / 2)
NOZZLE_RING_H = 6.0        # mm — ring axial height
NOZZLE_RING_TEETH = 32      # internal rack teeth for passive crown pinion actuation
NOZZLE_RING_RACK_DEPTH = 1.0
NOZZLE_RING_RACK_WIDTH = 0.36
NOZZLE_CUT_Z = 21.0         # mm — remove internal shell faces under the hinge region
NOZZLE_CUT_R = 26.0         # mm — cut radius to clear the ring pocket while preserving outer hull (increased by 1mm diameter)
NOZZLE_RING_FROM_EXHAUST = 15.0             # mm from exhaust face to nozzle ring hinge face
AFT_MOTOR_MOUNT_FROM_INTAKE  = 108.0       # mm from Z=0 intake → EDF2 motor struts (within 98..143mm)
FRONT_MOTOR_MOUNT_FROM_INTAKE = 35.0       # mm from Z=0 intake → EDF1 motor struts (within 22..72mm)
BORE_CARVE_R = 27.5         # mm — bore carve radius (EDF housing OD=55mm → R=27.5mm)
OLD_PETAL_FROM_INTAKE = 4.58 * 25.4  # mm — old fixed nozzle petals start here (116.3mm)
WIRE_GUIDE_WIDTH = 3.0
WIRE_GUIDE_THICKNESS = 2.0
WIRE_GUIDE_LENGTH = 20.0

PIVOT_Z_FROM_INTAKE = 74.0   # mm — pivot boss axial center (nacelle aerodynamic CG)
PIVOT_BOSS_Y_OFFSET = 27.5   # mm — boss center radial distance from bore axis (+Y toward wing)
PIVOT_BOSS_OD = 16.0         # mm — bearing seat OD (fits 686ZZ or MR128 bearing)
PIVOT_BOSS_ID = 6.0          # mm — spar/pin through-bore ID
PIVOT_BOSS_HALF_LEN = 12.0   # mm — boss half-length along X (spanwise)

INLET_BELL_Z_THROAT = 22.0   # mm — inlet bell joins thrust tube here (= EDF1 entry face)
INLET_BELL_FLARE    = 3.0    # mm — extra radius at intake lip vs bore radius
THRUST_TUBE_WALL    = 2.5    # mm — thrust tube wall thickness (OD = 50 + 5 = 55mm = EDF casing OD)

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


def cut_bore_interior(obj, cx, cy, r_bore, z_min, z_max):
    """Remove interior shell geometry to open a clean cylindrical bore.
    
    Deletes all faces with centers inside the bore cylinder (cx, cy, r_bore)
    within Z range [z_min, z_max].
    """
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(obj.data)
    bm.faces.ensure_lookup_table()

    r2 = r_bore * r_bore
    to_delete = []
    for face in bm.faces:
        n = len(face.verts)
        if n == 0:
            continue
        fc_x = sum(v.co.x for v in face.verts) / n
        fc_y = sum(v.co.y for v in face.verts) / n
        fc_z = sum(v.co.z for v in face.verts) / n
        
        if z_min <= fc_z <= z_max:
            dx = fc_x - cx
            dy = fc_y - cy
            if dx * dx + dy * dy < r2:
                to_delete.append(face)

    bmesh.ops.delete(bm, geom=to_delete, context="FACES")
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode="OBJECT")
    return len(to_delete)


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


def make_housing_shell(name, cx, cy, z_bot, z_top, inner_r, wall_thickness,
                       n_seg=64):
    """Create a hollow 50mm EDF housing sleeve section inside the nacelle."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    bm   = bmesh.new()
    outer_r = inner_r + wall_thickness
    angles = [2 * math.pi * i / n_seg for i in range(n_seg)]

    bot_i = [bm.verts.new((cx + inner_r * math.cos(a), cy + inner_r * math.sin(a), z_bot))
             for a in angles]
    top_i = [bm.verts.new((cx + inner_r * math.cos(a), cy + inner_r * math.sin(a), z_top))
             for a in angles]
    bot_o = [bm.verts.new((cx + outer_r * math.cos(a), cy + outer_r * math.sin(a), z_bot))
             for a in angles]
    top_o = [bm.verts.new((cx + outer_r * math.cos(a), cy + outer_r * math.sin(a), z_top))
             for a in angles]

    for i in range(n_seg):
        j = (i + 1) % n_seg
        add_face(bm, [bot_o[i], bot_o[j], top_o[j], top_o[i]])
        add_face(bm, [bot_i[j], bot_i[i], top_i[i], top_i[j]])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def make_motor_mount(name, cx, cy, z_center, inner_r, outer_r,
                     thickness=3.0, axial_length=8.0, n_arms=4):
    """Create a simple radial motor mount support inside the EDF housing."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    bm   = bmesh.new()

    for i in range(n_arms):
        phi = 2 * math.pi * i / n_arms
        direction = Vector((math.cos(phi), math.sin(phi), 0.0))
        length = outer_r - inner_r
        center = Vector((cx, cy, z_center)) + direction * (inner_r + length * 0.5)
        cube = bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Identity(4))
        for v in cube["verts"]:
            v.co.x *= length * 0.5
            v.co.y *= thickness * 0.5
            v.co.z *= axial_length * 0.5
            v.co.rotate(Matrix.Rotation(phi, 4, 'Z'))
            v.co += center

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def make_wire_guide(name, cx, cy, z_bot, z_top, angle, inner_r,
                    width=WIRE_GUIDE_WIDTH, thickness=WIRE_GUIDE_THICKNESS):
    """Create a shallow wire guide along the inside of the EDF housing."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    bm   = bmesh.new()
    z_mid = (z_bot + z_top) * 0.5
    length = z_top - z_bot
    center = Vector((cx, cy, z_mid)) + Vector((math.cos(angle), math.sin(angle), 0.0)) * (inner_r + width * 0.5)

    cube = bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Identity(4))
    for v in cube["verts"]:
        v.co.x *= width * 0.5
        v.co.y *= thickness * 0.5
        v.co.z *= length * 0.5
        v.co.rotate(Matrix.Rotation(angle, 4, 'Z'))
        v.co += center

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def make_thrust_tube(name, cx, cy, z_bot, z_top,
                     inner_r=25.0, wall=THRUST_TUBE_WALL, n_seg=64):
    """Continuous 50mm ID thrust tube sleeve spanning the full EDF/stator region."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    bm   = bmesh.new()
    outer_r = inner_r + wall
    angles  = [2 * math.pi * i / n_seg for i in range(n_seg)]

    bi = [bm.verts.new((cx + inner_r * math.cos(a), cy + inner_r * math.sin(a), z_bot)) for a in angles]
    ti = [bm.verts.new((cx + inner_r * math.cos(a), cy + inner_r * math.sin(a), z_top)) for a in angles]
    bo = [bm.verts.new((cx + outer_r * math.cos(a), cy + outer_r * math.sin(a), z_bot)) for a in angles]
    to = [bm.verts.new((cx + outer_r * math.cos(a), cy + outer_r * math.sin(a), z_top)) for a in angles]

    for i in range(n_seg):
        j = (i + 1) % n_seg
        add_face(bm, [bo[i], bo[j], to[j], to[i]])   # outer wall
        add_face(bm, [bi[i], ti[i], ti[j], bi[j]])   # inner wall (50mm bore)
        add_face(bm, [bo[i], bi[i], bi[j], bo[j]])   # bottom annulus
        add_face(bm, [to[i], to[j], ti[j], ti[i]])   # top annulus

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def make_inlet_bell(name, cx, cy, z_entry, z_throat,
                    r_throat=R_FIN_OUT, flare=INLET_BELL_FLARE,
                    wall=THRUST_TUBE_WALL, n_seg=64, n_rings=16):
    """Aerodynamic bell-mouth inlet: cosine-tapered inner profile from z_entry to z_throat."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    bm   = bmesh.new()
    angles = [2 * math.pi * i / n_seg for i in range(n_seg)]
    L = z_throat - z_entry

    def r_inner(z):
        t = (z - z_entry) / L   # 0 at entry lip, 1 at throat
        return r_throat + flare * 0.5 * (1.0 + math.cos(math.pi * t))

    zs       = [z_entry + L * k / (n_rings - 1) for k in range(n_rings)]
    rings_i  = []
    rings_o  = []
    for z in zs:
        ri = r_inner(z)
        ro = ri + wall
        rings_i.append([bm.verts.new((cx + ri * math.cos(a), cy + ri * math.sin(a), z)) for a in angles])
        rings_o.append([bm.verts.new((cx + ro * math.cos(a), cy + ro * math.sin(a), z)) for a in angles])

    for k in range(n_rings - 1):
        for i in range(n_seg):
            j = (i + 1) % n_seg
            add_face(bm, [rings_i[k][i], rings_i[k][j], rings_i[k+1][j], rings_i[k+1][i]])  # inner wall
            add_face(bm, [rings_o[k][i], rings_o[k+1][i], rings_o[k+1][j], rings_o[k][j]])  # outer wall

    for i in range(n_seg):
        j = (i + 1) % n_seg
        add_face(bm, [rings_o[0][i], rings_i[0][i], rings_i[0][j], rings_o[0][j]])   # entry lip annulus
        add_face(bm, [rings_o[-1][i], rings_o[-1][j], rings_i[-1][j], rings_i[-1][i]])  # throat annulus

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def make_pivot_boss(name, cx, cy, z_center,
                    y_offset=PIVOT_BOSS_Y_OFFSET,
                    boss_od=PIVOT_BOSS_OD, boss_id=PIVOT_BOSS_ID,
                    half_len=PIVOT_BOSS_HALF_LEN, n_seg=32):
    """Spanwise pivot bearing boss for nacelle tilt hinge.

    Boss axis runs along X (spanwise).  Outer cylinder = bearing seat;
    central bore = spar / hinge-pin through-bore.  Boss is centred at
    (cx, cy+y_offset, z_center) so it protrudes from the nacelle exterior
    toward the wing spar.
    """
    mesh = bpy.data.meshes.new(name + "_mesh")
    bm   = bmesh.new()
    r_out = boss_od / 2
    r_in  = boss_id / 2
    bcy   = cy + y_offset
    angles = [2 * math.pi * i / n_seg for i in range(n_seg)]

    def ring(x_offset, r):
        return [bm.verts.new((cx + x_offset,
                              bcy + r * math.cos(a),
                              z_center + r * math.sin(a))) for a in angles]

    lo = ring(-half_len, r_out)
    ro = ring(+half_len, r_out)
    li = ring(-half_len, r_in)
    ri = ring(+half_len, r_in)

    for i in range(n_seg):
        j = (i + 1) % n_seg
        add_face(bm, [lo[i], lo[j], ro[j], ro[i]])   # outer wall
        add_face(bm, [li[i], ri[i], ri[j], li[j]])   # inner bore wall
        add_face(bm, [lo[i], li[i], li[j], lo[j]])   # left cap annulus
        add_face(bm, [ro[i], ro[j], ri[j], ri[i]])   # right cap annulus

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

    in_path  = os.path.join(IN_DIR,  cfg["in_stl"])  # type: ignore[call-overload]
    out_path = os.path.join(OUT_DIR, cfg["out_stl"])  # type: ignore[call-overload]

    # Import nacelle shell
    nacelle = import_stl(in_path)
    nacelle.name = "nacelle_shell"
    bb = nacelle.bound_box
    zs = [v[2] for v in bb]
    shell_min_z = min(zs)
    shell_max_z = max(zs)
    print(f"  Shell Z range: {shell_min_z:.1f}..{shell_max_z:.1f} mm  "
          f"(bore axis = Z, intake = Z=0, exhaust = Z={shell_max_z:.1f})")

    # Carve full-length bore from the intake face (Z=0) to nozzle ring pocket.
    # BORE_CARVE_R=27.5mm = thrust tube OD (25mm bore + 2.5mm wall) — clears room for the sleeve.
    bore_removed = cut_bore_interior(nacelle, cfg["bore_cx"], cfg["bore_cy"],
                                     BORE_CARVE_R, 0.0, shell_max_z)
    print(f"  Carved interior bore: removed {bore_removed} faces  (Z=0..{shell_max_z:.0f}mm)")

    # Widen carve at the exhaust end to strip the old fixed nozzle petal cone.
    # Old petals are built into the shell STL starting at 4.58" from intake
    # (Z=116.3mm) and converge toward the exhaust face; they can extend to
    # ~36mm radius.  Carve from 5mm before the petal start to the shell end.
    old_petal_start_z = OLD_PETAL_FROM_INTAKE  # 116.3mm from Z=0=intake
    petal_removed = cut_bore_interior(nacelle, cfg["bore_cx"], cfg["bore_cy"],
                                      36.0, old_petal_start_z - 5.0, shell_max_z)
    print(f"  Stripped old fixed petals: removed {petal_removed} faces at R≤36mm, "
          f"Z={old_petal_start_z-5:.0f}..{shell_max_z:.0f}mm")

    # Build stator mesh at bore centre and mirror it into the shell's actual intake-to-exhaust Z axis.
    stator_mesh = build_stator_mesh(cfg["bore_cx"], cfg["bore_cy"], cfg["swirl"])
    stator_obj  = bpy.data.objects.new("stator_fins", stator_mesh)
    stator_obj.location.z = shell_max_z - (STATOR_BOT + STATOR_TOP)
    bpy.context.collection.objects.link(stator_obj)

    # Nozzle ring hinge sits NOZZLE_RING_FROM_EXHAUST mm before the exhaust face.
    ring_bottom_z = shell_max_z - NOZZLE_RING_FROM_EXHAUST  # world Z of hinge face
    removed_faces = cut_nozzle_shell_region(nacelle,
                                           cfg["bore_cx"], cfg["bore_cy"],
                                           ring_bottom_z, NOZZLE_CUT_R,
                                           cut_above=True)
    print(f"  Cleared nozzle ring pocket: removed {removed_faces} faces at Z>={ring_bottom_z:.1f}mm "
          f"({NOZZLE_RING_FROM_EXHAUST:.0f}mm from exhaust)")

    # Continuous 50mm ID thrust tube — single sleeve from inlet bell throat to nozzle pocket.
    # inner_r=25mm (50mm ID), wall=2.5mm → OD=55mm, matching Xfly Galaxy X5 casing OD.
    # This is the structural bore that houses both EDFs and the inter-stage stator.
    thrust_tube_z_top = ring_bottom_z  # flush with nozzle ring hinge face
    thrust_tube = make_thrust_tube("thrust_tube",
                                   cfg["bore_cx"], cfg["bore_cy"],
                                   INLET_BELL_Z_THROAT, thrust_tube_z_top,
                                   inner_r=R_FIN_OUT, wall=THRUST_TUBE_WALL)
    print(f"  Thrust tube: Z={INLET_BELL_Z_THROAT:.0f}..{thrust_tube_z_top:.0f}mm  "
          f"ID={2*R_FIN_OUT:.0f}mm  OD={2*(R_FIN_OUT+THRUST_TUBE_WALL):.0f}mm")

    # Bell-mouth inlet bell at Z=0..22mm — cylindrical entry cosine-tapered to 50mm bore.
    inlet_bell = make_inlet_bell("inlet_bell",
                                 cfg["bore_cx"], cfg["bore_cy"],
                                 0.0, INLET_BELL_Z_THROAT)
    print(f"  Inlet bell: Z=0..{INLET_BELL_Z_THROAT:.0f}mm  "
          f"entry ID={2*(R_FIN_OUT+INLET_BELL_FLARE):.0f}mm → throat ID={2*R_FIN_OUT:.0f}mm")

    # Pivot bearing boss for nacelle tilt hinge — protrudes +Y (toward wing spar).
    # Boss axis = X (spanwise); boss OD fits a 686ZZ bearing (6mm ID / 13mm OD seated inside).
    pivot_boss = make_pivot_boss("pivot_boss",
                                 cfg["bore_cx"], cfg["bore_cy"],
                                 PIVOT_Z_FROM_INTAKE)
    print(f"  Pivot boss: spanwise axis at Z={PIVOT_Z_FROM_INTAKE:.0f}mm, "
          f"Y+{PIVOT_BOSS_Y_OFFSET:.0f}mm from bore, OD={PIVOT_BOSS_OD:.0f}mm bore-ID={PIVOT_BOSS_ID:.0f}mm")

    aft_mount_z   = AFT_MOTOR_MOUNT_FROM_INTAKE    # world Z from intake (EDF2 motor, ~108mm)
    front_mount_z = FRONT_MOTOR_MOUNT_FROM_INTAKE  # world Z from intake (EDF1 motor, ~35mm)
    # Motor mount struts: 4 arms from hub surface (R_HUB_OUT=16mm) to bore inner wall (R_FIN_OUT=25mm).
    # Xfly 2627: 26mm stator → ~30mm can → hub OD 32mm (R_HUB_OUT=16mm).
    aft_motor_mount = make_motor_mount("aft_motor_mount",
                                       cfg["bore_cx"], cfg["bore_cy"],
                                       aft_mount_z,
                                       R_HUB_OUT, R_FIN_OUT,
                                       thickness=3.0, axial_length=8.0)
    front_motor_mount = make_motor_mount("front_motor_mount",
                                         cfg["bore_cx"], cfg["bore_cy"],
                                         front_mount_z,
                                         R_HUB_OUT, R_FIN_OUT,
                                         thickness=3.0, axial_length=8.0)

    wire_guide_front_1 = make_wire_guide("wire_guide_front_1",
                                         cfg["bore_cx"], cfg["bore_cy"],
                                         front_mount_z - 10.0,
                                         front_mount_z + 10.0,
                                         math.radians(45.0), R_FIN_OUT - 2.0,
                                         width=WIRE_GUIDE_WIDTH,
                                         thickness=WIRE_GUIDE_THICKNESS)
    wire_guide_front_2 = make_wire_guide("wire_guide_front_2",
                                         cfg["bore_cx"], cfg["bore_cy"],
                                         front_mount_z - 10.0,
                                         front_mount_z + 10.0,
                                         math.radians(135.0), R_FIN_OUT - 2.0,
                                         width=WIRE_GUIDE_WIDTH,
                                         thickness=WIRE_GUIDE_THICKNESS)
    wire_guide_aft_1 = make_wire_guide("wire_guide_aft_1",
                                       cfg["bore_cx"], cfg["bore_cy"],
                                       aft_mount_z - 10.0,
                                       aft_mount_z + 10.0,
                                       math.radians(225.0), R_FIN_OUT - 2.0,
                                       width=WIRE_GUIDE_WIDTH,
                                       thickness=WIRE_GUIDE_THICKNESS)
    wire_guide_aft_2 = make_wire_guide("wire_guide_aft_2",
                                       cfg["bore_cx"], cfg["bore_cy"],
                                       aft_mount_z - 10.0,
                                       aft_mount_z + 10.0,
                                       math.radians(315.0), R_FIN_OUT - 2.0,
                                       width=WIRE_GUIDE_WIDTH,
                                       thickness=WIRE_GUIDE_THICKNESS)

    nozzle_ring = make_nozzle_ring("nozzle_ring",
                                   cfg["bore_cx"], cfg["bore_cy"],
                                   NOZZLE_RING_OUTER_R, NOZZLE_RING_INNER_R,
                                   NOZZLE_RING_H,
                                   n_seg = N_HUB_SEG,
                                   rack_teeth = NOZZLE_RING_TEETH,
                                   rack_depth = NOZZLE_RING_RACK_DEPTH,
                                   rack_width = NOZZLE_RING_RACK_WIDTH)
    nozzle_ring.location.z = ring_bottom_z - NOZZLE_HINGE_Z
    print(f"  Added nozzle ring at exhaust end (hinge Z={ring_bottom_z:.1f}mm, "
          f"offset Z={ring_bottom_z - NOZZLE_HINGE_Z:.1f}mm): "
          f"{NOZZLE_RING_TEETH} teeth, {NOZZLE_RING_RACK_DEPTH:.1f}mm depth")
    print("  Nozzle iris is sized for the dual 50mm EDF path and is intended "
          "to open with vertical nacelle tilt and close with horizontal tilt.")

    # Join all geometry into one printable shell.
    combined = join_objects([nacelle, thrust_tube, inlet_bell, stator_obj,
                             aft_motor_mount, front_motor_mount,
                             wire_guide_front_1, wire_guide_front_2,
                             wire_guide_aft_1, wire_guide_aft_2,
                             pivot_boss, nozzle_ring])
    combined.name = cfg["out_stl"].replace(".stl", "")  # type: ignore[attr-defined]

    export_stl(combined, out_path)
    sz = os.path.getsize(out_path) // 1024
    twist_hub = math.degrees(STATOR_HEIGHT * math.tan(VANE_A) / R_HUB_OUT)
    twist_out = math.degrees(STATOR_HEIGHT * math.tan(VANE_A) / R_FIN_OUT)
    stator_world_bot = STATOR_BOT + (shell_max_z - (STATOR_BOT + STATOR_TOP))
    stator_world_top = stator_world_bot + STATOR_HEIGHT
    print(f"  → {cfg['out_stl']}  ({sz} KB)")
    print(f"  Thrust tube: Z={INLET_BELL_Z_THROAT:.0f}..{thrust_tube_z_top:.0f}mm  "
          f"ID={2*R_FIN_OUT:.0f}mm (50mm bore)  OD={2*(R_FIN_OUT+THRUST_TUBE_WALL):.0f}mm")
    print(f"  Stator world: Z={stator_world_bot:.0f}..{stator_world_top:.0f}mm  "
          f"swirl_dir={cfg['swirl']:+d}  "
          f"fin_twist hub={twist_hub:.1f}° outer={twist_out:.1f}°")
    print(f"  EDF1 seat: Z=22..72mm (intake end)  |  EDF2 seat: Z=98..143mm (exhaust end)")
    print(f"  Nozzle ring hinge: Z={ring_bottom_z:.0f}mm  "
          f"Pivot boss: Z={PIVOT_Z_FROM_INTAKE:.0f}mm  Hub bore ID={2*R_HUB_BORE:.0f}mm")

print("\nDone.  Print each nacelle shell in CF-PETG at 0.15mm / 25% infill.")
print("EDF installation (Z=0 = intake face, Z≈148 = exhaust/nozzle face):")
print("  1. Press EDF1 in from the INTAKE end (Z=0), seat at Z=22, motor forward.")
print("  2. Apply 3 dabs structural epoxy to EDF1 casing at Z=72 shoulder.")
print("  3. Route EDF1 leads back through hub bore toward intake.")
print("  4. Press EDF2 in from the EXHAUST end (Z≈148), seat at Z=143, motor toward stator.")
print("  5. Apply 3 dabs structural epoxy to EDF2 casing at Z=98 shoulder.")
print("  6. Confirm stator fin vanes visible in gap Z=72..98 — stator is between EDFs.")
print("  7. Seat nozzle iris ring on hinge bosses at Z≈133mm; install 3mm hinge pins.")
print("\nSWIRL DIRECTION:")
print("  Port  (left)  nacelle: SWIRL_DIR=+1 — EDF motors wired CW viewed from intake.")
print("  Stbd (right) nacelle: SWIRL_DIR=−1 — EDF motors wired CCW viewed from intake.")
print("  Verify rotation before sealing: spin-test each EDF before installing nacelle.")
