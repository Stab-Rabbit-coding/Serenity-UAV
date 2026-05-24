"""
blender_nacelle_revo.py  —  run with:
    blender --background --python blender_nacelle_revo.py

Rev O: integrated-stator nacelle shells for the Serenity-UAV 24" tiltrotor design.
Derived from blender_nacelle_integrated_v2.py (Rev N).

Key changes from Rev N:
  1. Pivot relocated from Z=74mm to Z=83mm (nacelle CG per mass breakdown below).
  2. Gear linkage mount features added: Pinion A bearing boss, bevel housing M2.5
     mount posts, longitudinal shaft conduit rib, crown pinion bearing boss.
  3. Output filenames updated to _revo suffix.

Gear train overview (M=1.0 ISO 54):
  Drive pinion A (N=12T, R=6mm) on transverse X-axis shaft, co-planar with tilt pivot.
  Fixed sector gear (R=22mm) on wing arm → ratio 22/6 = 3.667×.
  Bevel pair (N=14T, R=7mm, 45° pitch cone) redirects torque 90° to longitudinal shaft.
  Crown pinion (N=12T, R=6mm) drives nozzle ring rack (R_eff=28mm) → 6/28 = 0.214× step-down.
  Net: 90° nacelle tilt × (22/6) × (6/28) = 70.7° ring rotation → full iris open.

Rev O CG analysis (1× reference coords, Z=0=intake):
  Component                     Mass(g)  Z_cg(mm)  Moment(g·mm)
  Shell CF-PETG                 130      74.2       9,646
  Thrust tube sleeve             18      75.0       1,350
  EDF1 upstream (Z=22..72)       68      47.0       3,196
  ESC1 (co-located EDF1)         25      47.0       1,175
  EDF2 downstream (Z=98..143)    68     120.5       8,194
  ESC2 (co-located EDF2)         25     120.5       3,013
  Stator hub+fins (Z=75..95)      8      85.0         680
  Nozzle iris + hardware          22     140.0       3,080
  Gear train (M1.0 gears/shafts) 18      90.0       1,620
  LED ring                         8     143.0       1,144
  Inlet bell                      10      11.0         110
  Wiring (motor leads, ESC)       12      80.0         960
  Motor mount struts (×2)          6      82.5         495
  Clevis / pivot boss              8      74.0         592
  Fasteners / misc                 8     100.0         800
  TOTAL                          434               36,055
  CG_Z = 36,055 / 434 = 83.1 mm → PIVOT set to 83.0 mm

Design layout (bore runs along Z; Z=0 is the intake face, Z≈185 is exhaust):
All positions shown at 1× reference scale; runtime axial_scale ≈ 1.25 for 50mm shells.
  Intake bell           Z =   0 ..  22 mm  (→  0 ..  27.5 mm at 1.25×)
  EDF1 (upstream)       Z =  22 ..  72 mm  (→ 27.5 ..  90.0 mm at 1.25×)
  Stator gap            Z =  72 ..  75 mm  (→ 90.0 ..  93.75 mm at 1.25×)
  Stator fins           Z =  75 ..  95 mm  (→ 93.75 .. 118.75 mm at 1.25×)
  Stator gap            Z =  95 ..  98 mm  (→ 118.75 .. 122.5 mm at 1.25×)
  EDF2 (downstream)     Z =  98 .. 143 mm  (→ 122.5 .. 178.75 mm at 1.25×)
  Nozzle exit face      Z ≈ 143 .. 148 mm  (→ 178.75 .. 185.35 mm at 1.25×)

Nozzle iris behavior:
  - Ring is fixed to the nacelle shell at Z = NOZZLE_HINGE_Z (scaled).
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

Nacelle bore geometry (measured from s_eng_*_shell24_50mm.stl at 1.25× scale):
  Left bore centre:  X = 42.75, Y = −190.625  (Z axis is bore axis)
  Right bore centre: X = 155.0, Y = −190.625
  Shell Z range: 0..185.35 mm  (REF_SHELL_LENGTH = 148.3 mm → axial_scale ≈ 1.25)
  EDF casing OD = 55 mm → bore inner radius R_FIN_OUT = 25.0 mm (50mm ID bore)

Outputs (files-hollowed-18in/):
  s_eng_left_stator_shell24_revo.stl   — port nacelle, CW stator fins
  s_eng_right_stator_shell24_revo.stl  — starboard nacelle, CCW stator fins

License: CC BY 4.0
Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
Source:  Derived from blender_nacelle_integrated_v2.py (Rev N) in this repository.
         Attribution chain: Rev N → Rev O (this file).
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
    print("  blender --background --python blender_nacelle_revo.py")
    raise SystemExit(1)

# ── Stator / fin tunables ─────────────────────────────────────────────────────
# All values identical to Rev N (v2) unless noted in this file's change log.
N_FINS         = 11
STATOR_BOT     = 75.0      # mm from Z=0 (intake face) — bottom of stator at 1× scale world Z
STATOR_HEIGHT  = 20.0      # mm axial extent of stator
FIN_THICKNESS  = 2.0       # mm tangential thickness of each fin
VANE_ANGLE_DEG = 33.0      # degrees from axial — matches 50mm 6S EDF tip swirl
R_FIN_OUT      = 25.0      # mm — fin outer radius = 50mm fan radius (flush with bore)
R_HUB_OUT      = 16.0      # mm — hub outer radius (fits Xfly 2627 motor can ~30mm OD)
R_HUB_BORE     = 10.0      # mm — hub inner bore (wire routing)
N_HUB_SEG      = 32        # polygon count for hub ring

# ── Nozzle iris constants ─────────────────────────────────────────────────────
NOZZLE_HINGE_Z          = 15.0   # mm from Z=0 (nozzle face) — fixed-ring attachment face
NOZZLE_RING_OUTER_R     = 31.0   # mm — ring outer radius at hinge
NOZZLE_RING_INNER_R     = 25.0   # mm — ring inner radius = bore ID (50mm / 2)
NOZZLE_RING_H           = 6.0    # mm — ring axial height
NOZZLE_RING_TEETH       = 32     # internal rack teeth for passive crown pinion actuation
NOZZLE_RING_RACK_DEPTH  = 1.0
NOZZLE_RING_RACK_WIDTH  = 0.36
NOZZLE_CUT_Z            = 21.0   # mm — remove internal shell faces under the hinge region
NOZZLE_CUT_R            = 26.0   # mm — cut radius to clear ring pocket; preserves outer hull
NOZZLE_RING_FROM_EXHAUST = 15.0  # mm from exhaust face to nozzle ring hinge face

# ── Motor-mount and wire-guide constants ──────────────────────────────────────
AFT_MOTOR_MOUNT_FROM_INTAKE   = 108.0  # mm from Z=0 intake → EDF2 motor struts (98..143mm range)
FRONT_MOTOR_MOUNT_FROM_INTAKE =  35.0  # mm from Z=0 intake → EDF1 motor struts (22..72mm range)

# ── Thrust tube (50mm ID sleeve) constants ────────────────────────────────────
BORE_CARVE_R      = 27.5    # mm — bore carve radius (EDF casing OD=55mm → R=27.5mm)
OLD_PETAL_FROM_INTAKE = 4.58 * 25.4   # mm — old fixed nozzle petal start (≈116.3mm); remove them
WIRE_GUIDE_WIDTH      = 3.0
WIRE_GUIDE_THICKNESS  = 2.0
WIRE_GUIDE_LENGTH     = 20.0

# ── Pivot / clevis constants ──────────────────────────────────────────────────
# Rev O: pivot relocated to nacelle CG, computed from mass breakdown in module docstring.
PIVOT_Z_FROM_INTAKE  = 83.0   # mm — Rev O: pivot at nacelle CG, computed from mass breakdown above
CLEVIS_ARM_SLOT      = 16.0   # mm — slot width between ears; arm width must be ≤15mm with 0.5mm clearance
CLEVIS_EAR_THICK     = 10.0   # mm — X-direction thickness of each ear (F688ZZ is 5mm wide → 2.5mm each side)
CLEVIS_EAR_OD        = 26.0   # mm — ear outer diameter (F688ZZ OD=16mm + 2×5mm CF-PETG housing wall)
CLEVIS_PIN_D         =  8.0   # mm — F688ZZ bearing ID; hinge-pin = CF spar through-bore
CLEVIS_Y_FROM_BORE   = -41.9  # mm — ear centre Y offset from bore_cy (negative → inboard −Y skin)

# ── Inlet bell constants ──────────────────────────────────────────────────────
INLET_BELL_Z_THROAT = 22.0   # mm — inlet bell joins thrust tube here (= EDF1 entry face)
INLET_BELL_FLARE    =  3.0   # mm — extra radius at intake lip vs bore radius
THRUST_TUBE_WALL    =  2.5   # mm — thrust tube wall thickness (OD = 50+5 = 55mm = EDF casing OD)

# Reference axial length used when the axial-placement constants above were tuned.
# If the imported shell is longer/shorter, we compute:
#   axial_scale = shell_max_z / REF_SHELL_LENGTH
# so that features keep their relative positions while the thrust tube ID stays 50mm.
REF_SHELL_LENGTH = 148.3  # mm — 1× reference Z length of nacelle shell

# ── Gear linkage mount features ───────────────────────────────────────────────
# All gear dimensions use Module M=1.0 (ISO 54).
# Drive pinion A (N=12T, R=6mm) meshes with fixed sector gear (R=22mm).
# Bevel pair (N=14T, R=7mm, 45° pitch cone) redirects to longitudinal shaft.
# Crown pinion (N=12T, R=6mm) drives nozzle ring rack (R_eff=28mm).
# Full ratio: 90° nacelle × (22/6) × 1.0 × (6/28) = 70.7° ring → nozzle open.
PINION_A_SHAFT_D    =  3.0    # mm — MR63ZZ bearing ID; 3mm CF rod shaft
PINION_A_BOSS_OD    =  7.0    # mm — MR63ZZ OD 6mm + 0.5mm press-fit wall
PINION_A_BOSS_ID    =  3.2    # mm — shaft clearance bore (0.2mm on 3mm rod)
PINION_A_BOSS_LEN   = 10.0    # mm — spans 2× MR63ZZ bearings (2×2.5mm + 5mm gap)
PINION_A_Y_OFFSET   = -41.9   # mm — same Y as clevis ears (inboard −Y face)
# Bevel housing mount: two M2.5 boss posts flanking the transverse shaft.
BEVEL_BOSS_SPACING  = 16.0    # mm — centre-to-centre along X (clevis slot width)
BEVEL_BOSS_OD       =  6.0    # mm — M2.5 clearance + 2×1.75mm wall
BEVEL_BOSS_H        =  8.0    # mm — protrudes −Y from nacelle skin
BEVEL_BOSS_BORE     =  2.7    # mm — M2.5 clearance
# Longitudinal shaft conduit: 3mm CF shaft routes from bevel B output to crown pinion.
SHAFT_CONDUIT_OD    =  5.5    # mm — OD of conduit rib on nacelle exterior
SHAFT_CONDUIT_ID    =  3.5    # mm — clears 3mm shaft inside 4mm OD PTFE sleeve
SHAFT_CONDUIT_ANGLE = -0.5    # rad — angular position of conduit on bore (−Y direction toward fuselage)
SHAFT_CONDUIT_R     = 31.0    # mm — radial distance of conduit centreline from bore axis
CROWN_PINION_Z_REF  = 133.0   # mm — crown pinion shaft centre (1× ref); near nozzle ring bottom
# Crown pinion boss (same bearing spec as Pinion A)
CROWN_BOSS_OD       =  7.0    # mm
CROWN_BOSS_ID       =  3.2    # mm
CROWN_BOSS_LEN      = 10.0    # mm

# ── Nacelle bore centres (world-space X, Y; bore axis = Z) ───────────────────
NACELLES = [
    {
        "in_stl":  "s_eng_left_shell24_50mm.stl",
        "out_stl": "s_eng_left_stator_shell24_revo.stl",      # Rev O output
        "bore_cx": 42.75,       # X bore centre at 1.25× scale (fallback if compute_bore_center fails)
        "bore_cy": -190.625,    # Y bore centre at 1.25× scale
        "swirl":   +1,          # CW viewed from intake (port nacelle)
        "label":   "PORT (left), CW stator",
    },
    {
        "in_stl":  "s_eng_right_shell24_50mm.stl",
        "out_stl": "s_eng_right_stator_shell24_revo.stl",     # Rev O output
        "bore_cx": 155.0,       # X bore centre at 1.25× scale
        "bore_cy": -190.625,    # Y bore centre at 1.25× scale
        "swirl":   -1,          # CCW viewed from intake (starboard nacelle)
        "label":   "STARBOARD (right), CCW stator",
    },
]

BASE    = os.path.dirname(os.path.abspath(__file__))
IN_DIR  = os.path.join(BASE, "files-hollowed-18in")
OUT_DIR = IN_DIR
# ─────────────────────────────────────────────────────────────────────────────

# Pre-compute derived stator constants at module level (1× scale; scaled inside loop).
STATOR_TOP = STATOR_BOT + STATOR_HEIGHT
VANE_A     = math.radians(VANE_ANGLE_DEG)
T_HALF     = FIN_THICKNESS / 2.0

# Keep originals so per-nacelle scaling doesn't mutate module globals.
# Each nacelle iteration scales these independently; second nacelle is not double-scaled.
ORIG_STATOR_BOT                  = STATOR_BOT
ORIG_STATOR_HEIGHT               = STATOR_HEIGHT
ORIG_NOZZLE_HINGE_Z              = NOZZLE_HINGE_Z
ORIG_NOZZLE_RING_FROM_EXHAUST    = NOZZLE_RING_FROM_EXHAUST
ORIG_AFT_MOTOR_MOUNT_FROM_INTAKE = AFT_MOTOR_MOUNT_FROM_INTAKE
ORIG_FRONT_MOTOR_MOUNT_FROM_INTAKE = FRONT_MOTOR_MOUNT_FROM_INTAKE
ORIG_PIVOT_Z_FROM_INTAKE         = PIVOT_Z_FROM_INTAKE
ORIG_INLET_BELL_Z_THROAT         = INLET_BELL_Z_THROAT
ORIG_OLD_PETAL_FROM_INTAKE       = OLD_PETAL_FROM_INTAKE


# ── Scene / IO helpers ────────────────────────────────────────────────────────

def clear_scene():
    """Remove all objects from the current Blender scene before each nacelle pass."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def import_stl(path):
    """Import an STL file and return the resulting Blender object."""
    bpy.ops.wm.stl_import(filepath=path)
    return bpy.context.selected_objects[0]


def export_stl(obj, path):
    """Export a single Blender object to an STL file at the given absolute path."""
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True)


def add_face(bm, verts):
    """Add a face to a bmesh, silently discarding duplicates (ValueError)."""
    try:
        bm.faces.new(verts)
    except ValueError:
        pass


# ── Cylindrical-coordinate vertex helper ─────────────────────────────────────

def vert_at_cyl(bm, cx, cy, r, phi, z):
    """Vertex in world space at cylindrical coords relative to bore centre."""
    return bm.verts.new((cx + r * math.cos(phi), cy + r * math.sin(phi), z))


# ── Hub ring (cable routing annulus) ─────────────────────────────────────────

def add_hub_ring(bm, cx, cy, r_out, r_in, z_bot, z_top, n_seg):
    """Annular hub ring (hollow tube) for cable routing through stator centre."""
    a = [2.0 * math.pi * i / n_seg for i in range(n_seg)]
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


# ── Bore carving (interior shell removal) ────────────────────────────────────

def cut_bore_interior(obj, cx, cy, r_bore, z_min, z_max):
    """Remove interior shell geometry to open a clean cylindrical bore.

    Deletes all faces with centres inside the bore cylinder (cx, cy, r_bore)
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
    If cut_above is True,  delete faces with center Z >= z_threshold.
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


# ── Nozzle iris ring ─────────────────────────────────────────────────────────

def make_nozzle_ring(name, cx, cy, outer_r, inner_r, axial_h,
                     n_seg=128, rack_teeth=0, rack_depth=0.0,
                     rack_width=0.4):
    """Build a fixed nozzle ring with optional internal rack teeth."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    bm   = bmesh.new()

    # Increase polygon resolution so rack tooth pitch is resolved adequately.
    if rack_teeth > 0:
        n_seg = max(n_seg, rack_teeth * 8)

    def inner_radius(angle):
        """Return local inner radius: recessed at rack tooth gaps."""
        if rack_teeth <= 0:
            return inner_r
        pitch = 2.0 * math.pi / rack_teeth
        x = (angle % pitch) / pitch
        if x < rack_width or x > 1.0 - rack_width:
            return inner_r - rack_depth
        return inner_r

    angles = [2.0 * math.pi * i / n_seg for i in range(n_seg)]
    bot_o = [bm.verts.new((cx + outer_r * math.cos(a),
                           cy + outer_r * math.sin(a),
                           0.0))
             for a in angles]
    top_o = [bm.verts.new((cx + outer_r * math.cos(a),
                           cy + outer_r * math.sin(a),
                           axial_h))
             for a in angles]
    bot_i = [bm.verts.new((cx + inner_radius(a) * math.cos(a),
                           cy + inner_radius(a) * math.sin(a),
                           0.0))
             for a in angles]
    top_i = [bm.verts.new((cx + inner_radius(a) * math.cos(a),
                           cy + inner_radius(a) * math.sin(a),
                           axial_h))
             for a in angles]

    def face(vlist):
        """Local face helper with duplicate-edge guard."""
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


# ── EDF housing sleeve section ────────────────────────────────────────────────

def make_housing_shell(name, cx, cy, z_bot, z_top, inner_r, wall_thickness,
                       n_seg=64):
    """Create a hollow 50mm EDF housing sleeve section inside the nacelle."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    bm   = bmesh.new()
    outer_r = inner_r + wall_thickness
    angles  = [2.0 * math.pi * i / n_seg for i in range(n_seg)]

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


# ── Radial motor mount strut spider ──────────────────────────────────────────

def make_motor_mount(name, cx, cy, z_center, inner_r, outer_r,
                     thickness=3.0, axial_length=8.0, n_arms=4):
    """Create a simple radial motor mount support inside the EDF housing."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    bm   = bmesh.new()

    for i in range(n_arms):
        phi    = 2.0 * math.pi * i / n_arms
        direction = Vector((math.cos(phi), math.sin(phi), 0.0))
        length = outer_r - inner_r
        center = Vector((cx, cy, z_center)) + direction * (inner_r + length * 0.5)
        cube   = bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Identity(4))
        for v in cube["verts"]:
            v.co.x *= length * 0.5
            v.co.y *= thickness * 0.5
            v.co.z *= axial_length * 0.5
            v.co.rotate(Matrix.Rotation(phi, 4, "Z"))
            v.co += center

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


# ── Wire guide rib ────────────────────────────────────────────────────────────

def make_wire_guide(name, cx, cy, z_bot, z_top, angle, inner_r,
                    width=WIRE_GUIDE_WIDTH, thickness=WIRE_GUIDE_THICKNESS):
    """Create a shallow wire guide along the inside of the EDF housing."""
    mesh  = bpy.data.meshes.new(name + "_mesh")
    bm    = bmesh.new()
    z_mid = (z_bot + z_top) * 0.5
    length = z_top - z_bot
    center = (Vector((cx, cy, z_mid))
              + Vector((math.cos(angle), math.sin(angle), 0.0)) * (inner_r + width * 0.5))

    cube = bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Identity(4))
    for v in cube["verts"]:
        v.co.x *= width * 0.5
        v.co.y *= thickness * 0.5
        v.co.z *= length * 0.5
        v.co.rotate(Matrix.Rotation(angle, 4, "Z"))
        v.co += center

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


# ── Continuous thrust tube sleeve ─────────────────────────────────────────────

def make_thrust_tube(name, cx, cy, z_bot, z_top,
                     inner_r=25.0, wall=THRUST_TUBE_WALL, n_seg=64):
    """Continuous 50mm ID thrust tube sleeve spanning the full EDF/stator region."""
    mesh    = bpy.data.meshes.new(name + "_mesh")
    bm      = bmesh.new()
    outer_r = inner_r + wall
    angles  = [2.0 * math.pi * i / n_seg for i in range(n_seg)]

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


# ── Bell-mouth inlet ──────────────────────────────────────────────────────────

def make_inlet_bell(name, cx, cy, z_entry, z_throat,
                    r_throat=R_FIN_OUT, flare=INLET_BELL_FLARE,
                    wall=THRUST_TUBE_WALL, n_seg=64, n_rings=16):
    """Aerodynamic bell-mouth inlet: cosine-tapered inner profile from z_entry to z_throat."""
    mesh   = bpy.data.meshes.new(name + "_mesh")
    bm     = bmesh.new()
    angles = [2.0 * math.pi * i / n_seg for i in range(n_seg)]
    L = z_throat - z_entry

    def r_inner(z):
        """Cosine-interpolated radius from flared lip down to throat radius."""
        t = (z - z_entry) / L   # 0 at entry lip, 1 at throat
        return r_throat + flare * 0.5 * (1.0 + math.cos(math.pi * t))

    zs      = [z_entry + L * k / (n_rings - 1) for k in range(n_rings)]
    rings_i = []
    rings_o = []
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
        add_face(bm, [rings_o[0][i], rings_i[0][i], rings_i[0][j], rings_o[0][j]])      # entry lip annulus
        add_face(bm, [rings_o[-1][i], rings_o[-1][j], rings_i[-1][j], rings_i[-1][i]])  # throat annulus

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


# ── X-axis tilt clevis ────────────────────────────────────────────────────────

def make_clevis_extension(name, bore_cx, bore_cy, z_center,
                          arm_slot=CLEVIS_ARM_SLOT, ear_thick=CLEVIS_EAR_THICK,
                          ear_od=CLEVIS_EAR_OD, y_from_bore=CLEVIS_Y_FROM_BORE,
                          pin_d=CLEVIS_PIN_D, n_seg=32):
    """Two-eared X-axis tilt clevis at nacelle inboard (−Y) face.

    Pivot axis = X (spanwise).  Each ear is an annular tube (F688ZZ bearing bore)
    with axis along X.  The arm_slot gap between the ears receives the rigid wing
    arm.  y_from_bore is negative so the clevis protrudes toward the wing root,
    not into the thrust stream.  Pin through-bore = F688ZZ ID (8mm).

    Fold mechanism (piv_outer, piv_pins, pistons) ELIMINATED.  Single tilt axis only.

    Rev O: pivot Z moved from 74mm to 83mm to align with nacelle CG.

    Layout in X around bore_cx:
      Left ear:   X ∈ [bore_cx − arm_slot/2 − ear_thick, bore_cx − arm_slot/2]
      Slot:       X ∈ [bore_cx − arm_slot/2, bore_cx + arm_slot/2]  (arm inserts here)
      Right ear:  X ∈ [bore_cx + arm_slot/2, bore_cx + arm_slot/2 + ear_thick]
    """
    mesh      = bpy.data.meshes.new(name + "_mesh")
    bm        = bmesh.new()
    r_out     = ear_od / 2.0
    r_in      = pin_d / 2.0
    ey        = bore_cy + y_from_bore   # ear centre Y
    ez        = z_center                # ear centre Z
    half_slot = arm_slot / 2.0

    # Build two ears — each is a short hollow cylinder (axis = X).
    for x_near, x_far in [
        (bore_cx - half_slot - ear_thick, bore_cx - half_slot),          # left ear
        (bore_cx + half_slot,             bore_cx + half_slot + ear_thick),  # right ear
    ]:
        angles = [2.0 * math.pi * i / n_seg for i in range(n_seg)]
        near_o = [bm.verts.new((x_near, ey + r_out * math.cos(a), ez + r_out * math.sin(a))) for a in angles]
        far_o  = [bm.verts.new((x_far,  ey + r_out * math.cos(a), ez + r_out * math.sin(a))) for a in angles]
        near_i = [bm.verts.new((x_near, ey + r_in  * math.cos(a), ez + r_in  * math.sin(a))) for a in angles]
        far_i  = [bm.verts.new((x_far,  ey + r_in  * math.cos(a), ez + r_in  * math.sin(a))) for a in angles]

        for i in range(n_seg):
            j = (i + 1) % n_seg
            add_face(bm, [near_o[i], near_o[j], far_o[j],  far_o[i]])   # outer wall
            add_face(bm, [near_i[i], far_i[i],  far_i[j],  near_i[j]])  # inner bore wall
            add_face(bm, [near_o[i], near_i[i], near_i[j], near_o[j]])  # near cap annulus
            add_face(bm, [far_o[i],  far_o[j],  far_i[j],  far_i[i]])   # far cap annulus

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


# ── Rev O — NEW: Pinion A bearing boss ───────────────────────────────────────

def make_pinion_a_boss(name, bore_cx, bore_cy, z_center,
                       y_offset=PINION_A_Y_OFFSET,
                       boss_od=PINION_A_BOSS_OD, boss_id=PINION_A_BOSS_ID,
                       half_len=None, n_seg=32):
    """Transverse shaft boss for Drive Pinion A (MR63ZZ bearing seats).

    Boss axis = X (spanwise), same axis as clevis pin.  OD = MR63ZZ press-fit
    bore (6mm OD + 0.5mm interference).  Length spans two bearings + gap.
    Boss protrudes −Y (inboard) at the same face as the clevis ears so the
    transverse pinion shaft is co-planar with the tilt pivot axis.
    """
    if half_len is None:
        half_len = PINION_A_BOSS_LEN / 2.0

    mesh  = bpy.data.meshes.new(name + "_mesh")
    bm    = bmesh.new()
    r_out = boss_od / 2.0
    r_in  = boss_id / 2.0
    # Boss centre Y: bore_cy + y_offset; boss centre Z: z_center; axis runs ±half_len in X.
    ey    = bore_cy + y_offset
    angles = [2.0 * math.pi * i / n_seg for i in range(n_seg)]

    # Four rings of vertices: near/far × outer/inner (boss axis = X direction).
    near_o = [bm.verts.new((bore_cx - half_len, ey + r_out * math.cos(a), z_center + r_out * math.sin(a))) for a in angles]
    far_o  = [bm.verts.new((bore_cx + half_len, ey + r_out * math.cos(a), z_center + r_out * math.sin(a))) for a in angles]
    near_i = [bm.verts.new((bore_cx - half_len, ey + r_in  * math.cos(a), z_center + r_in  * math.sin(a))) for a in angles]
    far_i  = [bm.verts.new((bore_cx + half_len, ey + r_in  * math.cos(a), z_center + r_in  * math.sin(a))) for a in angles]

    for i in range(n_seg):
        j = (i + 1) % n_seg
        add_face(bm, [near_o[i], near_o[j], far_o[j],  far_o[i]])   # outer wall
        add_face(bm, [near_i[i], far_i[i],  far_i[j],  near_i[j]])  # inner bore wall
        add_face(bm, [near_o[i], near_i[i], near_i[j], near_o[j]])  # near cap annulus
        add_face(bm, [far_o[i],  far_o[j],  far_i[j],  far_i[i]])   # far cap annulus

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


# ── Rev O — NEW: Bevel housing M2.5 mount posts ───────────────────────────────

def make_bevel_mount_bosses(name, bore_cx, bore_cy, z_center,
                             y_offset=PINION_A_Y_OFFSET,
                             spacing=BEVEL_BOSS_SPACING,
                             boss_od=BEVEL_BOSS_OD, boss_h=BEVEL_BOSS_H,
                             boss_bore=BEVEL_BOSS_BORE, n_seg=24):
    """Two M2.5 mounting posts for the bevel gear housing, flanking the pinion A shaft.

    Posts protrude −Y from the nacelle skin at the pivot Z station.  The bevel
    housing bolts to these posts, holding Bevel A (transverse) and Bevel B
    (longitudinal) and the MR63ZZ shaft bearings.
    """
    mesh = bpy.data.meshes.new(name + "_mesh")
    bm   = bmesh.new()
    r_o  = boss_od / 2.0
    r_i  = boss_bore / 2.0
    ey   = bore_cy + y_offset

    # Two posts: one at −spacing/2 in X, one at +spacing/2 in X.
    for x_off in [-spacing / 2.0, +spacing / 2.0]:
        x_c    = bore_cx + x_off
        angles = [2.0 * math.pi * i / n_seg for i in range(n_seg)]
        # Posts run in Y direction (−Y protrusion from nacelle skin)
        near_y = ey
        far_y  = ey - boss_h
        no = [bm.verts.new((x_c + r_o * math.cos(a), near_y, z_center + r_o * math.sin(a))) for a in angles]
        fo = [bm.verts.new((x_c + r_o * math.cos(a), far_y,  z_center + r_o * math.sin(a))) for a in angles]
        ni = [bm.verts.new((x_c + r_i * math.cos(a), near_y, z_center + r_i * math.sin(a))) for a in angles]
        fi = [bm.verts.new((x_c + r_i * math.cos(a), far_y,  z_center + r_i * math.sin(a))) for a in angles]
        for i in range(n_seg):
            j = (i + 1) % n_seg
            add_face(bm, [no[i], no[j], fo[j], fo[i]])   # outer wall
            add_face(bm, [ni[i], fi[i], fi[j], ni[j]])   # inner bore wall
            add_face(bm, [no[i], ni[i], ni[j], no[j]])   # near (skin side) annulus
            add_face(bm, [fo[i], fo[j], fi[j], fi[i]])   # far (tip) annulus

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


# ── Rev O — NEW: Longitudinal shaft conduit rib ───────────────────────────────

def make_shaft_conduit(name, bore_cx, bore_cy, z_from, z_to,
                       shaft_angle=SHAFT_CONDUIT_ANGLE,
                       shaft_r=SHAFT_CONDUIT_R,
                       conduit_od=SHAFT_CONDUIT_OD,
                       conduit_id=SHAFT_CONDUIT_ID,
                       n_seg=24):
    """Longitudinal conduit rib on nacelle exterior routing bevel shaft to crown pinion.

    The 3mm CF shaft from Bevel B output runs inside a 4mm OD PTFE sleeve.
    This conduit feature is a short hollow cylinder (axis = Z) forming a rib
    on the nacelle outer skin between z_from and z_to.
    The conduit is positioned at (bore_cx + shaft_r×cos(shaft_angle),
                                   bore_cy + shaft_r×sin(shaft_angle))
    on the outer surface, clear of the thrust tube OD (27.5mm) and nacelle skin.
    """
    # Conduit centre in XY: offset from bore axis at the specified angle and radius.
    cx_c   = bore_cx + shaft_r * math.cos(shaft_angle)
    cy_c   = bore_cy + shaft_r * math.sin(shaft_angle)
    mesh   = bpy.data.meshes.new(name + "_mesh")
    bm     = bmesh.new()
    r_o    = conduit_od / 2.0
    r_i    = conduit_id / 2.0
    angles = [2.0 * math.pi * k / n_seg for k in range(n_seg)]

    # Bottom and top rings at z_from and z_to; inner and outer diameters.
    bi = [bm.verts.new((cx_c + r_i * math.cos(a), cy_c + r_i * math.sin(a), z_from)) for a in angles]
    ti = [bm.verts.new((cx_c + r_i * math.cos(a), cy_c + r_i * math.sin(a), z_to))   for a in angles]
    bo = [bm.verts.new((cx_c + r_o * math.cos(a), cy_c + r_o * math.sin(a), z_from)) for a in angles]
    to = [bm.verts.new((cx_c + r_o * math.cos(a), cy_c + r_o * math.sin(a), z_to))   for a in angles]

    for i in range(n_seg):
        j = (i + 1) % n_seg
        add_face(bm, [bo[i], bo[j], to[j], to[i]])   # outer wall
        add_face(bm, [bi[i], ti[i], ti[j], bi[j]])   # inner wall (PTFE sleeve bore)
        add_face(bm, [bo[i], bi[i], bi[j], bo[j]])   # bottom annulus
        add_face(bm, [to[i], to[j], ti[j], ti[i]])   # top annulus

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


# ── Stator fin (twisted vane) ─────────────────────────────────────────────────

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
        """Angular twist over axial height h at radius r for this swirl direction."""
        return swirl_dir * h * math.tan(vane_angle) / r

    tw_h = t_half / r_hub
    tw_o = t_half / r_out
    dh_h = delta(r_hub)
    dh_o = delta(r_out)

    def v(r, phi, z):
        """Helper: add one vertex in cylindrical coords."""
        return bm.verts.new((cx + r * math.cos(phi), cy + r * math.sin(phi), z))

    # Bottom face verts (at z_bot — downstream EDF2 side)
    tl_h_b = v(r_hub, phi_center - tw_h, z_bot)
    ld_h_b = v(r_hub, phi_center + tw_h, z_bot)
    tl_o_b = v(r_out, phi_center - tw_o, z_bot)
    ld_o_b = v(r_out, phi_center + tw_o, z_bot)
    # Top face verts (at z_top — twisted; upstream EDF1 side)
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


# ── Stator mesh builder ───────────────────────────────────────────────────────

def build_stator_mesh(cx, cy, swirl_dir, height=None):
    """Return a new Blender mesh containing the stator fins + hub ring.

    The mesh is generated with Z in the range 0..height so it can be
    translated into place via the object's `location.z` property.
    """
    if height is None:
        height = STATOR_HEIGHT

    mesh = bpy.data.meshes.new("stator_integrated")
    bm   = bmesh.new()

    # Hub ring (cable routing passage) — generated from z=0..height
    add_hub_ring(bm, cx, cy,
                 r_out=R_HUB_OUT,
                 r_in=R_HUB_BORE,
                 z_bot=0.0,
                 z_top=height,
                 n_seg=N_HUB_SEG)

    # Twisted fins placed at equal angular spacing between z=0..height.
    for i in range(N_FINS):
        phi = 2.0 * math.pi * i / N_FINS
        add_fin(bm, cx, cy,
                phi_center=phi,
                r_hub=R_HUB_OUT,
                r_out=R_FIN_OUT,
                z_bot=0.0,
                h=height,
                t_half=T_HALF,
                vane_angle=VANE_A,
                swirl_dir=swirl_dir)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return mesh


# ── Object join helper ────────────────────────────────────────────────────────

def join_objects(objs):
    """Join a list of Blender objects into the first one and return it."""
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    return bpy.context.active_object


# ── Main processing loop — one pass per nacelle ───────────────────────────────
for cfg in NACELLES:
    print(f"\n=== Processing {cfg['label']} ===")
    clear_scene()

    in_path  = os.path.join(IN_DIR,  cfg["in_stl"])
    out_path = os.path.join(OUT_DIR, cfg["out_stl"])

    # Import nacelle shell STL.
    nacelle      = import_stl(in_path)
    nacelle.name = "nacelle_shell"
    bb           = nacelle.bound_box
    zs           = [v[2] for v in bb]
    shell_min_z  = min(zs)
    shell_max_z  = max(zs)
    print(f"  Shell Z range: {shell_min_z:.1f}..{shell_max_z:.1f} mm  "
          f"(bore axis = Z, intake = Z=0, exhaust = Z={shell_max_z:.1f})")

    # Compute axial scale factor from the imported shell's actual Z length.
    # Keeps all feature positions proportionally correct regardless of shell version.
    axial_scale = shell_max_z / REF_SHELL_LENGTH if REF_SHELL_LENGTH > 0 else 1.0
    if abs(axial_scale - 1.0) > 0.001:
        print(f"  Axial scale factor: {axial_scale:.3f} (ref {REF_SHELL_LENGTH} mm)")

    # Scaled local placement values — computed from ORIG_* constants to avoid
    # double-scaling when the second nacelle runs through the same loop body.
    sbot                   = ORIG_STATOR_BOT * axial_scale
    sheight                = ORIG_STATOR_HEIGHT * axial_scale
    s_top                  = sbot + sheight
    nozzle_hinge_z         = ORIG_NOZZLE_HINGE_Z * axial_scale
    nozzle_ring_from_exhaust = ORIG_NOZZLE_RING_FROM_EXHAUST * axial_scale
    aft_mount_z            = ORIG_AFT_MOTOR_MOUNT_FROM_INTAKE * axial_scale
    front_mount_z          = ORIG_FRONT_MOTOR_MOUNT_FROM_INTAKE * axial_scale
    pivot_z                = ORIG_PIVOT_Z_FROM_INTAKE * axial_scale   # Rev O: 83.0mm ref → ~103.75mm scaled
    inlet_bell_z_throat    = ORIG_INLET_BELL_Z_THROAT * axial_scale
    old_petal_start_z      = ORIG_OLD_PETAL_FROM_INTAKE * axial_scale

    # Scaled crown pinion Z reference (1× = 133mm → scaled).
    # Used for shaft conduit top and crown pinion boss placement.
    crown_z = CROWN_PINION_Z_REF * axial_scale

    # ── Bore centre determination ─────────────────────────────────────────────
    # Fit a circle to ring vertices sampled in the mid-EDF Z band.
    # More accurate than nominal constants when the shell origin is shifted.
    def compute_bore_center(obj, z_lo, z_hi, expected_cx, expected_cy):
        """Algebraic circle fit (Kása method) on bore-ring vertices in Z band [z_lo, z_hi].

        Falls back to (expected_cx, expected_cy) if fewer than 40 ring points found.
        Reference: Kása (1976) 'A curve fitting procedure and its error analysis',
        IEEE Trans. Instrum. Meas., 25(1), pp. 8–14.
        """
        verts = [v.co for v in obj.data.vertices if z_lo <= v.co.z <= z_hi]
        if not verts:
            return expected_cx, expected_cy

        # First-pass centroid to seed radial filter.
        cx0 = sum(v.x for v in verts) / len(verts)
        cy0 = sum(v.y for v in verts) / len(verts)

        # Keep only vertices near the expected bore inner surface (R_FIN_OUT ± 6mm).
        r_low   = max(0.0, R_FIN_OUT - 6.0)
        r_high  = R_FIN_OUT + 6.0
        ring_pts = []
        for v in verts:
            r = math.hypot(v.x - cx0, v.y - cy0)
            if r_low <= r <= r_high:
                ring_pts.append((v.x, v.y))
        if len(ring_pts) < 40:
            return expected_cx, expected_cy

        xs = [p[0] for p in ring_pts]
        ys = [p[1] for p in ring_pts]
        # Build 3×3 normal-equation matrix for: x² + y² + Dx + Ey + F = 0
        A00 = sum(x * x for x in xs)
        A01 = sum(x * y for x, y in zip(xs, ys))
        A02 = sum(xs)
        A11 = sum(y * y for y in ys)
        A12 = sum(ys)
        A22 = len(ring_pts)
        b0  = -sum((x * x + y * y) * x for x, y in zip(xs, ys))
        b1  = -sum((x * x + y * y) * y for x, y in zip(xs, ys))
        b2  = -sum((x * x + y * y)     for x, y in zip(xs, ys))
        A   = [[float(A00), float(A01), float(A02)],
               [float(A01), float(A11), float(A12)],
               [float(A02), float(A12), float(A22)]]
        b   = [float(b0), float(b1), float(b2)]

        # Gaussian elimination with partial pivoting.
        for i in range(3):
            pivot = i
            for j in range(i + 1, 3):
                if abs(A[j][i]) > abs(A[pivot][i]):
                    pivot = j
            if pivot != i:
                A[i], A[pivot] = A[pivot], A[i]
                b[i], b[pivot] = b[pivot], b[i]
            if abs(A[i][i]) < 1e-12:
                return expected_cx, expected_cy
            fac = A[i][i]
            for j in range(i, 3):
                A[i][j] /= fac
            b[i] /= fac
            for j in range(i + 1, 3):
                f = A[j][i]
                for k in range(i, 3):
                    A[j][k] -= f * A[i][k]
                b[j] -= f * b[i]

        # Back-substitution.
        x = [0.0, 0.0, 0.0]
        for i in range(2, -1, -1):
            s = b[i]
            for j in range(i + 1, 3):
                s -= A[i][j] * x[j]
            x[i] = s / A[i][i] if abs(A[i][i]) > 1e-12 else 0.0
        D, E, _F = x
        cx = -D / 2.0
        cy = -E / 2.0
        return cx, cy

    sample_z_lo = inlet_bell_z_throat + 20.0
    sample_z_hi = min(shell_max_z - 20.0, inlet_bell_z_throat + 100.0)
    bore_cx, bore_cy = compute_bore_center(nacelle,
                                           sample_z_lo, sample_z_hi,
                                           cfg["bore_cx"], cfg["bore_cy"])
    print(f"  Computed bore centre: X={bore_cx:.2f} Y={bore_cy:.2f} "
          f"(sample Z {sample_z_lo:.1f}..{sample_z_hi:.1f})")

    # ── Bore carving ──────────────────────────────────────────────────────────
    # BORE_CARVE_R=27.5mm = thrust tube OD (25mm bore + 2.5mm wall) — room for the sleeve.
    bore_removed = cut_bore_interior(nacelle, bore_cx, bore_cy,
                                     BORE_CARVE_R, 0.0, shell_max_z)
    print(f"  Carved interior bore: removed {bore_removed} faces  (Z=0..{shell_max_z:.0f}mm)")

    # Widen carve at the exhaust end to strip the old fixed nozzle petal cone.
    petal_removed = cut_bore_interior(nacelle, bore_cx, bore_cy,
                                      36.0, old_petal_start_z - 5.0, shell_max_z)
    print(f"  Stripped old fixed petals: removed {petal_removed} faces at R≤36mm, "
          f"Z={old_petal_start_z - 5:.0f}..{shell_max_z:.0f}mm")

    # ── Stator fins + hub ring ────────────────────────────────────────────────
    stator_mesh = build_stator_mesh(bore_cx, bore_cy, cfg["swirl"], height=sheight)
    stator_obj  = bpy.data.objects.new("stator_fins", stator_mesh)
    stator_obj.location.z = sbot   # translate from local z=0 to world sbot
    bpy.context.collection.objects.link(stator_obj)

    # ── Nozzle ring pocket ────────────────────────────────────────────────────
    ring_bottom_z = shell_max_z - nozzle_ring_from_exhaust
    removed_faces = cut_nozzle_shell_region(nacelle,
                                            bore_cx, bore_cy,
                                            ring_bottom_z, NOZZLE_CUT_R,
                                            cut_above=True)
    print(f"  Cleared nozzle ring pocket: removed {removed_faces} faces at Z>={ring_bottom_z:.1f}mm "
          f"({nozzle_ring_from_exhaust:.0f}mm from exhaust)")

    # ── Thrust tube sleeve ────────────────────────────────────────────────────
    # Single 50mm ID sleeve from inlet bell throat to nozzle ring hinge face.
    # inner_r=25mm, wall=2.5mm → OD=55mm = Xfly Galaxy X5 casing OD.
    thrust_tube_z_top = ring_bottom_z   # flush with nozzle ring hinge face
    thrust_tube = make_thrust_tube("thrust_tube",
                                   bore_cx, bore_cy,
                                   inlet_bell_z_throat, thrust_tube_z_top,
                                   inner_r=R_FIN_OUT, wall=THRUST_TUBE_WALL)
    print(f"  Thrust tube: Z={inlet_bell_z_throat:.0f}..{thrust_tube_z_top:.0f}mm  "
          f"ID={2 * R_FIN_OUT:.0f}mm  OD={2 * (R_FIN_OUT + THRUST_TUBE_WALL):.0f}mm")

    # ── Bell-mouth inlet ──────────────────────────────────────────────────────
    inlet_bell = make_inlet_bell("inlet_bell",
                                 bore_cx, bore_cy,
                                 0.0, inlet_bell_z_throat)
    print(f"  Inlet bell: Z=0..{inlet_bell_z_throat:.0f}mm  "
          f"entry ID={2 * (R_FIN_OUT + INLET_BELL_FLARE):.0f}mm "
          f"→ throat ID={2 * R_FIN_OUT:.0f}mm")

    # ── X-axis tilt clevis ────────────────────────────────────────────────────
    # Rev O: clevis at Z=83mm (nacelle CG) instead of 74mm (Rev N).
    # F688ZZ bearing (8mm ID × 16mm OD × 5mm wide); hinge-pin = CF spar through-bore.
    clevis_ext = make_clevis_extension("clevis_ext", bore_cx, bore_cy, pivot_z)
    print(f"  Clevis: X-axis tilt hinge at Z={pivot_z:.1f}mm (Rev O CG-aligned), "
          f"Y_offset={CLEVIS_Y_FROM_BORE:.1f}mm (inboard), "
          f"ear_OD={CLEVIS_EAR_OD:.0f}mm pin_ID={CLEVIS_PIN_D:.0f}mm "
          f"slot={CLEVIS_ARM_SLOT:.0f}mm  [F688ZZ × 2]")

    # ── Rev O: Pinion A bearing boss ─────────────────────────────────────────
    # Transverse shaft boss at CG pivot, inboard face.
    # Boss axis = X (spanwise); boss OD = MR63ZZ press-fit seat (7mm).
    pinion_a_boss = make_pinion_a_boss("pinion_a_boss", bore_cx, bore_cy, pivot_z)
    print(f"  Pinion A boss: X-axis at Z={pivot_z:.1f}mm, Y_offset={PINION_A_Y_OFFSET:.1f}mm "
          f"OD={PINION_A_BOSS_OD:.0f}mm bore={PINION_A_BOSS_ID:.1f}mm [MR63ZZ seats]")

    # ── Rev O: Bevel housing M2.5 mount posts ────────────────────────────────
    # Two M2.5 boss posts flanking the pinion A shaft on the inboard face.
    bevel_mount = make_bevel_mount_bosses("bevel_mount", bore_cx, bore_cy, pivot_z)
    print(f"  Bevel mount posts: Z={pivot_z:.1f}mm, spacing={BEVEL_BOSS_SPACING:.0f}mm X, "
          f"OD={BEVEL_BOSS_OD:.0f}mm, height={BEVEL_BOSS_H:.0f}mm")

    # ── Rev O: Longitudinal shaft conduit ─────────────────────────────────────
    # Routes bevel B output (pivot_z) to crown pinion (crown_z) on nacelle exterior.
    # Conduit at angle SHAFT_CONDUIT_ANGLE (≈−0.5rad ≈ −28.6°, toward fuselage −Y face),
    # R=31mm from bore axis — clear of thrust tube OD (27.5mm) and nacelle skin.
    shaft_conduit = make_shaft_conduit("shaft_conduit", bore_cx, bore_cy,
                                       pivot_z, crown_z)
    print(f"  Shaft conduit: Z={pivot_z:.1f}..{crown_z:.1f}mm, "
          f"R={SHAFT_CONDUIT_R:.0f}mm, OD={SHAFT_CONDUIT_OD:.1f}mm ID={SHAFT_CONDUIT_ID:.1f}mm")

    # ── Rev O: Crown pinion bearing boss at nozzle end ────────────────────────
    # Same spec as Pinion A boss (MR63ZZ press-fit seats); mounted near nozzle ring.
    crown_boss = make_pinion_a_boss("crown_boss", bore_cx, bore_cy, crown_z,
                                    boss_od=CROWN_BOSS_OD, boss_id=CROWN_BOSS_ID,
                                    half_len=CROWN_BOSS_LEN / 2.0)
    print(f"  Crown pinion boss: Z={crown_z:.1f}mm [MR63ZZ seats, same spec as Pinion A]")

    # ── Motor mount struts ────────────────────────────────────────────────────
    # Xfly 2627: 26mm stator → ~30mm can → hub OD 32mm (R_HUB_OUT=16mm).
    aft_motor_mount = make_motor_mount("aft_motor_mount",
                                       bore_cx, bore_cy,
                                       aft_mount_z,
                                       R_HUB_OUT, R_FIN_OUT,
                                       thickness=3.0, axial_length=8.0)
    front_motor_mount = make_motor_mount("front_motor_mount",
                                         bore_cx, bore_cy,
                                         front_mount_z,
                                         R_HUB_OUT, R_FIN_OUT,
                                         thickness=3.0, axial_length=8.0)

    # ── Wire guides ───────────────────────────────────────────────────────────
    wire_guide_front_1 = make_wire_guide("wire_guide_front_1",
                                         bore_cx, bore_cy,
                                         front_mount_z - 10.0,
                                         front_mount_z + 10.0,
                                         math.radians(45.0), R_FIN_OUT - 2.0,
                                         width=WIRE_GUIDE_WIDTH,
                                         thickness=WIRE_GUIDE_THICKNESS)
    wire_guide_front_2 = make_wire_guide("wire_guide_front_2",
                                         bore_cx, bore_cy,
                                         front_mount_z - 10.0,
                                         front_mount_z + 10.0,
                                         math.radians(135.0), R_FIN_OUT - 2.0,
                                         width=WIRE_GUIDE_WIDTH,
                                         thickness=WIRE_GUIDE_THICKNESS)
    wire_guide_aft_1 = make_wire_guide("wire_guide_aft_1",
                                       bore_cx, bore_cy,
                                       aft_mount_z - 10.0,
                                       aft_mount_z + 10.0,
                                       math.radians(225.0), R_FIN_OUT - 2.0,
                                       width=WIRE_GUIDE_WIDTH,
                                       thickness=WIRE_GUIDE_THICKNESS)
    wire_guide_aft_2 = make_wire_guide("wire_guide_aft_2",
                                       bore_cx, bore_cy,
                                       aft_mount_z - 10.0,
                                       aft_mount_z + 10.0,
                                       math.radians(315.0), R_FIN_OUT - 2.0,
                                       width=WIRE_GUIDE_WIDTH,
                                       thickness=WIRE_GUIDE_THICKNESS)

    # ── Nozzle iris ring ──────────────────────────────────────────────────────
    nozzle_ring = make_nozzle_ring("nozzle_ring",
                                   bore_cx, bore_cy,
                                   NOZZLE_RING_OUTER_R, NOZZLE_RING_INNER_R,
                                   NOZZLE_RING_H,
                                   n_seg=N_HUB_SEG,
                                   rack_teeth=NOZZLE_RING_TEETH,
                                   rack_depth=NOZZLE_RING_RACK_DEPTH,
                                   rack_width=NOZZLE_RING_RACK_WIDTH)
    # make_nozzle_ring builds at local z=0..axial_h; location.z places bottom at ring_bottom_z.
    nozzle_ring.location.z = ring_bottom_z
    print(f"  Added nozzle ring at exhaust end (hinge Z={ring_bottom_z:.1f}mm): "
          f"{NOZZLE_RING_TEETH} teeth, {NOZZLE_RING_RACK_DEPTH:.1f}mm depth")
    print("  Nozzle iris is sized for the dual 50mm EDF path and is intended "
          "to open with vertical nacelle tilt and close with horizontal tilt.")

    # ── Join all geometry into one printable shell ────────────────────────────
    # Rev O adds: pinion_a_boss, bevel_mount, shaft_conduit, crown_boss.
    combined = join_objects([
        nacelle,
        thrust_tube,
        inlet_bell,
        stator_obj,
        aft_motor_mount,
        front_motor_mount,
        wire_guide_front_1,
        wire_guide_front_2,
        wire_guide_aft_1,
        wire_guide_aft_2,
        clevis_ext,
        nozzle_ring,
        pinion_a_boss,      # Rev O: M1.0 gear Pinion A MR63ZZ bearing boss
        bevel_mount,        # Rev O: bevel housing M2.5 mount posts
        shaft_conduit,      # Rev O: longitudinal bevel-to-crown shaft conduit rib
        crown_boss,         # Rev O: crown pinion MR63ZZ bearing boss at nozzle end
    ])
    combined.name = cfg["out_stl"].replace(".stl", "")

    export_stl(combined, out_path)
    sz          = os.path.getsize(out_path) // 1024
    twist_hub   = math.degrees(sheight * math.tan(VANE_A) / R_HUB_OUT)
    twist_out   = math.degrees(sheight * math.tan(VANE_A) / R_FIN_OUT)
    stator_world_bot = sbot
    stator_world_top = sbot + sheight
    print(f"  → {cfg['out_stl']}  ({sz} KB)")
    print(f"  Thrust tube: Z={inlet_bell_z_throat:.0f}..{thrust_tube_z_top:.0f}mm  "
          f"ID={2 * R_FIN_OUT:.0f}mm (50mm bore)  OD={2 * (R_FIN_OUT + THRUST_TUBE_WALL):.0f}mm")
    print(f"  Stator world: Z={stator_world_bot:.0f}..{stator_world_top:.0f}mm  "
          f"swirl_dir={cfg['swirl']:+d}  "
          f"fin_twist hub={twist_hub:.1f}° outer={twist_out:.1f}°")
    edf1_top = 72.0 * axial_scale
    edf2_bot = 98.0 * axial_scale
    print(f"  EDF1 seat: Z={inlet_bell_z_throat:.0f}..{edf1_top:.0f}mm (intake end)  |  "
          f"EDF2 seat: Z={edf2_bot:.0f}..{thrust_tube_z_top:.0f}mm (exhaust end)")
    print(f"  Nozzle ring hinge: Z={ring_bottom_z:.0f}mm  "
          f"Clevis (CG pivot): Z={pivot_z:.1f}mm  Hub bore ID={2 * R_HUB_BORE:.0f}mm")

# ── Rev O: summary and assembly notes ────────────────────────────────────────
print("\nDone.  Print each nacelle shell in CF-PETG at 0.15mm / 4 perimeters / 40% infill load-bearing.")
print("Shells are 1.25× scale (50mm EDF); Z=0 = intake face, Z≈185.35mm = exhaust face.")

print("\nRev O CHANGES vs Rev N:")
print("  • Pivot Z moved from 74mm (ref) to 83mm (ref) — aligned to computed nacelle CG.")
print("    Benefit: zero first-moment of inertia about tilt axis; tilt servo only works against")
print("    aerodynamic moment, not gravity moment.  Reduces servo stall current in hover.")
print("  • Pinion A bearing boss added at pivot Z: MR63ZZ press-fit (7mm OD, 3mm bore), X-axis.")
print("  • Bevel housing M2.5 mount posts (×2) added flanking Pinion A on inboard face.")
print("  • Longitudinal shaft conduit rib added on nacelle exterior:")
print(f"    Route: pivot_Z → crown_Z={CROWN_PINION_Z_REF:.0f}mm (ref), "
      f"R={SHAFT_CONDUIT_R:.0f}mm from bore axis, angle≈{math.degrees(SHAFT_CONDUIT_ANGLE):.1f}°.")
print("    3mm CF shaft inside 4mm OD PTFE sleeve; conduit OD=5.5mm ID=3.5mm.")
print("  • Crown pinion bearing boss added at Z≈133mm (ref) — MR63ZZ same as Pinion A.")

print("\nGEAR TRAIN (M=1.0 ISO 54) ASSEMBLY:")
print("  1. Press MR63ZZ bearings into Pinion A boss (ID=7mm press bore).")
print("  2. Slide 3mm CF shaft through bearings and mount pinion A (N=12T).")
print("  3. Bolt bevel housing to M2.5 posts with M2.5×8 SHCS; torque to 0.3 N·m.")
print("  4. Thread 3mm CF shaft from bevel B output through conduit PTFE sleeve.")
print("  5. Press MR63ZZ into crown pinion boss; seat crown pinion (N=12T).")
print("  6. Verify nozzle ring rack engages crown pinion with ≤0.1mm backlash.")
print(f"  Full linkage ratio: (22/6) × (6/28) = {(22.0/6.0) * (6.0/28.0):.3f}  "
      f"→ 90° nacelle = {90.0 * (22.0/6.0) * (6.0/28.0):.1f}° ring travel.")

print("\nEDF installation sequence:")
print("  1. Press EDF1 in from INTAKE end (Z=0), seat at Z≈27.5mm, motor faces forward.")
print("  2. Apply 3 dabs structural epoxy to EDF1 casing at Z≈90mm shoulder.")
print("  3. Route EDF1 leads through hub bore toward intake.")
print("  4. Press EDF2 in from EXHAUST end (Z≈185mm), seat at Z≈178.75mm, motor toward stator.")
print("  5. Apply 3 dabs structural epoxy to EDF2 casing at Z≈122.5mm shoulder.")
print("  6. Confirm stator fin vanes visible in gap Z≈90..123mm — stator is between EDFs.")
print("  7. Seat nozzle iris ring at ring_bottom_z; no separate hinge pins (rack-coupled).")

print("\nTILT HINGE (Rev O — CG-pivot):")
print("  Clevis ears at inboard (−Y) face, Z≈103.75mm (scaled).  Pin = CF spar through F688ZZ.")
print("  Pivot co-planar with Pinion A shaft — one CF spar serves as both hinge pin and gear shaft.")
print("  Arm slot = 16mm wide; fabricate arm ≤15mm wide for 0.5mm clearance each side.")

print("\nSWIRL DIRECTION:")
print("  Port  (left)  nacelle: SWIRL_DIR=+1 — EDF motors wired CW viewed from intake.")
print("  Stbd (right) nacelle: SWIRL_DIR=−1 — EDF motors wired CCW viewed from intake.")
print("  Spin-test each EDF before sealing nacelle; confirm rotation matches SWIRL_DIR.")
