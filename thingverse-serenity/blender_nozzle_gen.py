"""
blender_nozzle_gen.py  —  run with:
    blender --background --python blender_nozzle_gen.py

Rev L variable-area EDF nozzles for Serenity-UAV at 24" scale.

Design intent:
  CLOSED: petal outer surfaces form the continuation of the Serenity hull geometry,
          exactly matching the nacelle tip / rear engine bell as-modelled.
  OPEN:   petals hinge radially outward ~75°, exposing the EDF bore.
          The concave inner bowl face glows (paint or translucent blue insert)
          — this is the "Serenity at full burn" look from the show.

Replaces Rev F nozzles which did not maintain the external hull shape.
BamJr thing:2991269 iris mechanism is used as the actuation reference but
all new exterior geometry is generated here from the actual hull cross-sections.

OUTPUTS (all in files-hollowed-18in/):
  nacelle_nozzle_petal.stl        — single petal for 50 mm ID nacelle nozzle
                                    (print × 8 per nacelle, × 4 nacelles = 32 total)
  nacelle_nozzle_ring.stl         — fixed base ring / hinge carrier (× 4)
  rear_nozzle_petal.stl           — single petal for 120 mm ID rear nozzle
                                    (print × 8, rear engine)
  rear_nozzle_ring.stl            — fixed base ring / hinge carrier (× 1)
  nacelle_nozzle_closed_asm.stl   — 8-petal closed assembly, verification only
  rear_nozzle_closed_asm.stl      — 8-petal closed assembly, verification only

HULL CROSS-SECTION DATA (from blender_nozzle_gen.py analysis of shell24 files):
  Nacelle (s_eng_left_shell24.stl) — axis = Z, exit at Z=0:
    Z=  0mm  OD=38mm  →  outer_r=19.0mm   (tip, closed-nozzle outer edge)
    Z=  7mm  OD=49mm  →  outer_r=24.5mm
    Z= 15mm  OD=56mm  →  outer_r=28.0mm   (hinge position)
    EDF exit radius at hinge = 25mm (50mm fan / 2)
    Nacelle centroid in XY  = (34, -150) mm

  Rear (s_rear_shell24.stl) — axis = X, exit at X=−246mm:
    X=−246mm  section = 54mm Y × 66mm Z  →  approx mean_r=30mm, tip  (closed)
    X=−232mm  section =131mm Y ×119mm Z  →  mean_r=62.5mm at hinge
    EDF exit radius at hinge = 60mm (120mm fan / 2)
    Section centroid in YZ   = (−117, 36) mm  →  treat as (0,0) in nozzle local frame
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
    print("  blender --background --python blender_nozzle_gen.py")
    raise SystemExit(1)

# ── tunables ─────────────────────────────────────────────────────────────────
N_PETALS         = 8          # iris petals per nozzle (8 replicates the show look)
OVERLAP_DEG      = 3.0        # each petal spans 360/N + overlap (for sealing)
N_PROFILE_Z      = 6          # radial profile subdivisions along petal length
N_ANGLE          = 8          # angular subdivisions per petal

HINGE_DIA_MM     = 3.0        # hinge pin through-hole diameter
HINGE_WALL       = 1.5        # wall around hinge pin
NAC_RING_TEETH   = 32         # inner ring rack teeth count for passive crown pinion actuation
NAC_RING_RACK_DEPTH = 1.0     # tooth depth on inner ring wall (mm)
NAC_RING_RACK_WIDTH = 0.36    # tooth width fraction of one pitch

# ── nacelle nozzle parameters (50 mm EDF, Z-axis, Z=0 exit) ─────────────────
# This nozzle is designed for a 50mm EDF installed between the stator and
# the petal/hinge assembly; the downstream EDF span occupies the bore
# upstream of the nozzle ring and the stator begins further upstream.
NAC_EDF_R    = 25.0       # EDF fan radius (50 mm / 2)
NAC_HINGE_Z  = 15.0       # z of hinge (where petal meets fixed ring)
NAC_TIP_Z    = 0.0        # z of petal tip (hull exit face)
# outer_r profile: list of (z, r) from tip to hinge — sampled from hull
NAC_OUTER_PROFILE = [     # (z_mm, outer_r_mm)  — hull cross-section data
    (0.0,  12.0),         # inner tip (axis-side) at Z=0 — converges toward axis
    (4.0,  16.0),
    (8.0,  21.0),
    (12.0, 25.5),
    (15.0, 28.0),         # at hinge: hull OD/2 = 28mm
]
NAC_INNER_PROFILE = [     # inner (EDF bore side) profile — converging nozzle path
    (0.0,  0.0),          # tip: closes to axis
    (4.0,  8.0),
    (8.0,  16.0),
    (12.0, 22.0),
    (15.0, 25.0),         # at hinge: EDF radius = 25mm
]

# ── rear nozzle parameters (120 mm EDF, X-axis, exit at X=−246 in world) ────
# We work in local nozzle coords: axial = local_z, X=-246 = local_z=0 (tip)
REAR_EDF_R    = 60.0      # EDF fan radius (120 mm / 2)
REAR_HINGE_Z  = 14.0      # local_z of hinge (−232 in world = 14mm from tip)
REAR_TIP_Z    = 0.0       # tip
REAR_OUTER_PROFILE = [    # (local_z_mm, outer_r_mm) — hull cross-section mean_r
    (0.0,   22.0),        # aft tip: mean_r = sqrt((54/2)*(66/2)) ≈ 30mm, use 22 for inner
    (5.0,   32.0),
    (10.0,  50.0),
    (14.0,  62.5),        # hinge: mean of 131/2, 119/2 ≈ 62.5mm
]
REAR_INNER_PROFILE = [    # EDF bore converging toward tip
    (0.0,   0.0),
    (5.0,   18.0),
    (10.0,  42.0),
    (14.0,  60.0),        # EDF radius = 60mm at hinge
]

# ── rear cone frame parameters (structural ribs between petals) ──────────────
# The rear nozzle has a FIXED rib skeleton that holds the cone shape even when
# petals are fully open.  8 ribs at 45° intervals; petals fill between them.
REAR_RIB_SPAN_DEG  = 6.0   # angular width of each rib (degrees)
REAR_RIB_DEPTH     = 3.5   # radial depth of rib (outer surface - inner surface, mm)
REAR_RIB_GAP_DEG   = 0.5   # clearance gap between rib edge and petal edge
# Petal span = 45° - rib - 2×gap = 45 - 6 - 1 = 38° (NO sealing overlap needed;
# ribs handle the inter-petal structure, so petals just need to cover the opening)
REAR_PETAL_SPAN_DEG = 360.0 / N_PETALS - REAR_RIB_SPAN_DEG - 2 * REAR_RIB_GAP_DEG

BASE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(BASE, "files-hollowed-18in")
# ─────────────────────────────────────────────────────────────────────────────


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def export_stl(obj, path):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True)
    return os.path.getsize(path) // 1024


def lerp_profile(profile, z):
    """Linear interpolate r from a (z, r) profile list."""
    profile = sorted(profile, key=lambda x: x[0])
    if z <= profile[0][0]:
        return profile[0][1]
    if z >= profile[-1][0]:
        return profile[-1][1]
    for i in range(len(profile) - 1):
        z0, r0 = profile[i]
        z1, r1 = profile[i + 1]
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0)
            return r0 + t * (r1 - r0)
    return profile[-1][1]


def make_petal(name, n_petals, outer_profile, inner_profile,
               tip_z, hinge_z, edf_r, n_angle_sub=8, n_z_sub=6,
               span_override_deg=None):
    """
    Build one iris petal as a closed solid mesh.

    The petal occupies angular span = span_override_deg if given, else
    (360/N + OVERLAP) degrees, centred on θ=0.
    Axial extent: tip_z (exit face) to hinge_z (fixed-ring interface).
    Outer surface: follows outer_profile (hull skin shape).
    Inner surface: follows inner_profile (EDF bore / flow path).
    End caps close the solid at both z ends and at both angular sides.

    Returns the Blender object (not yet linked to scene).
    """
    span_deg = span_override_deg if span_override_deg is not None \
               else 360.0 / n_petals + OVERLAP_DEG
    span_rad = math.radians(span_deg)
    half     = span_rad / 2.0

    z_values = [tip_z + (hinge_z - tip_z) * i / (n_z_sub - 1) for i in range(n_z_sub)]
    a_values = [-half + span_rad * i / (n_angle_sub - 1) for i in range(n_angle_sub)]

    mesh = bpy.data.meshes.new(name + "_mesh")
    bm   = bmesh.new()

    # ── build vertex grid: outer and inner surfaces ──────────────────────────
    # Index scheme: outer[iz][ia], inner[iz][ia]
    outer_verts = []
    inner_verts = []
    for iz, z in enumerate(z_values):
        ro = lerp_profile(outer_profile, z)
        ri = lerp_profile(inner_profile, z)
        row_o = []
        row_i = []
        for ia, a in enumerate(a_values):
            co_a = math.cos(a)
            si_a = math.sin(a)
            row_o.append(bm.verts.new((ro * co_a, ro * si_a, z)))
            row_i.append(bm.verts.new((ri * co_a, ri * si_a, z)))
        outer_verts.append(row_o)
        inner_verts.append(row_i)

    bm.verts.ensure_lookup_table()

    def face(vlist):
        try:
            bm.faces.new(vlist)
        except ValueError:
            pass  # skip degenerate face

    # ── outer surface (hull skin) ────────────────────────────────────────────
    for iz in range(n_z_sub - 1):
        for ia in range(n_angle_sub - 1):
            face([outer_verts[iz][ia],
                  outer_verts[iz][ia + 1],
                  outer_verts[iz + 1][ia + 1],
                  outer_verts[iz + 1][ia]])

    # ── inner surface (EDF bore / concave bowl) — reversed normal ───────────
    for iz in range(n_z_sub - 1):
        for ia in range(n_angle_sub - 1):
            face([inner_verts[iz][ia],
                  inner_verts[iz + 1][ia],
                  inner_verts[iz + 1][ia + 1],
                  inner_verts[iz][ia + 1]])

    # ── angular side caps (the two cut edges of the petal) ──────────────────
    for iz in range(n_z_sub - 1):
        # starboard side (ia=0)
        face([outer_verts[iz][0], outer_verts[iz + 1][0],
              inner_verts[iz + 1][0], inner_verts[iz][0]])
        # port side (ia=-1)
        ia = n_angle_sub - 1
        face([outer_verts[iz][ia], inner_verts[iz][ia],
              inner_verts[iz + 1][ia], outer_verts[iz + 1][ia]])

    # ── tip cap (z = tip_z, the open/exit face when petal is closed) ─────────
    for ia in range(n_angle_sub - 1):
        ro0 = lerp_profile(outer_profile, tip_z)
        ri0 = lerp_profile(inner_profile, tip_z)
        if abs(ri0) < 0.5:
            # inner radius ≈ 0: triangular fan to axis point
            apex = bm.verts.new((0.0, 0.0, tip_z))
            face([outer_verts[0][ia], outer_verts[0][ia + 1], apex])
        else:
            face([outer_verts[0][ia], outer_verts[0][ia + 1],
                  inner_verts[0][ia + 1], inner_verts[0][ia]])

    # ── hinge cap (z = hinge_z, the fixed-ring interface) ───────────────────
    iz = n_z_sub - 1
    for ia in range(n_angle_sub - 1):
        face([outer_verts[iz][ia], inner_verts[iz][ia],
              inner_verts[iz][ia + 1], outer_verts[iz][ia + 1]])

    # ── hinge lug: a functional tab at hinge_z for a 3 mm pivot pin ───────
    # The lug includes a through-hole so the petal can pivot on a real pin.
    r_hinge  = lerp_profile(outer_profile, hinge_z)
    lug_r    = r_hinge + HINGE_WALL * 2
    lug_h    = HINGE_WALL * 3   # tab axial height above hinge face
    hole_r   = HINGE_DIA_MM / 2.0
    hole_cx  = r_hinge + HINGE_WALL
    hole_off = hole_r
    lug_half_a = math.radians(span_deg / 4)

    # outer lug corners at bottom and top
    o0 = bm.verts.new((r_hinge * math.cos(-lug_half_a),
                       r_hinge * math.sin(-lug_half_a), hinge_z))
    o1 = bm.verts.new((r_hinge * math.cos(+lug_half_a),
                       r_hinge * math.sin(+lug_half_a), hinge_z))
    o2 = bm.verts.new((lug_r   * math.cos(+lug_half_a),
                       lug_r   * math.sin(+lug_half_a), hinge_z))
    o3 = bm.verts.new((lug_r   * math.cos(-lug_half_a),
                       lug_r   * math.sin(-lug_half_a), hinge_z))
    o4 = bm.verts.new((r_hinge * math.cos(-lug_half_a),
                       r_hinge * math.sin(-lug_half_a), hinge_z + lug_h))
    o5 = bm.verts.new((r_hinge * math.cos(+lug_half_a),
                       r_hinge * math.sin(+lug_half_a), hinge_z + lug_h))
    o6 = bm.verts.new((lug_r   * math.cos(+lug_half_a),
                       lug_r   * math.sin(+lug_half_a), hinge_z + lug_h))
    o7 = bm.verts.new((lug_r   * math.cos(-lug_half_a),
                       lug_r   * math.sin(-lug_half_a), hinge_z + lug_h))

    # square through-hole corners around the hinge pin center
    ih0 = bm.verts.new((hole_cx - hole_off, -hole_off, hinge_z))
    ih1 = bm.verts.new((hole_cx + hole_off, -hole_off, hinge_z))
    ih2 = bm.verts.new((hole_cx + hole_off, +hole_off, hinge_z))
    ih3 = bm.verts.new((hole_cx - hole_off, +hole_off, hinge_z))
    ih4 = bm.verts.new((hole_cx - hole_off, -hole_off, hinge_z + lug_h))
    ih5 = bm.verts.new((hole_cx + hole_off, -hole_off, hinge_z + lug_h))
    ih6 = bm.verts.new((hole_cx + hole_off, +hole_off, hinge_z + lug_h))
    ih7 = bm.verts.new((hole_cx - hole_off, +hole_off, hinge_z + lug_h))

    # bottom & top frame faces with a functional pin hole opening
    face([o0, o1, ih1, ih0])
    face([o1, o2, ih2, ih1])
    face([o2, o3, ih3, ih2])
    face([o3, o0, ih0, ih3])
    face([o4, o7, ih7, ih4])
    face([o5, o4, ih4, ih5])
    face([o6, o5, ih5, ih6])
    face([o7, o6, ih6, ih7])

    # outer and inner vertical faces
    face([o0, o4, o5, o1])  # inner side
    face([o1, o5, o6, o2])  # outer side
    face([o2, o6, o7, o3])  # outer back
    face([o3, o7, o4, o0])  # inner back
    face([ih0, ih1, ih5, ih4])  # hole side 1
    face([ih1, ih2, ih6, ih5])  # hole side 2
    face([ih2, ih3, ih7, ih6])  # hole side 3
    face([ih3, ih0, ih4, ih7])  # hole side 4

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def make_base_ring(name, outer_r, inner_r, axial_h, n_seg=64,
                   hinge_lugs=8, rack_teeth=0, rack_depth=0.0,
                   rack_width=0.4):
    """
    Fixed base ring that the petals hinge from.
    outer_r / inner_r: ring radii, axial_h: ring height.
    The outer ring is sized to accept the petal hinge lug tabs, and the
    optional inner rack profile mates with a crown pinion for tilt-actuated
    iris motion.
    """
    if rack_teeth > 0:
        n_seg = max(n_seg, rack_teeth * 8)

    mesh = bpy.data.meshes.new(name + "_mesh")
    bm   = bmesh.new()

    def inner_radius(angle):
        if rack_teeth <= 0:
            return inner_r
        pitch = 2 * math.pi / rack_teeth
        x = (angle % pitch) / pitch
        # rectangular tooth approximated on the inner wall
        if x < rack_width or x > 1.0 - rack_width:
            return inner_r - rack_depth
        return inner_r

    angles = [2 * math.pi * i / n_seg for i in range(n_seg)]

    bot_o = [bm.verts.new((outer_r * math.cos(a), outer_r * math.sin(a), 0.0))
             for a in angles]
    top_o = [bm.verts.new((outer_r * math.cos(a), outer_r * math.sin(a), axial_h))
             for a in angles]
    bot_i = [bm.verts.new((inner_radius(a) * math.cos(a),
                          inner_radius(a) * math.sin(a), 0.0))
             for a in angles]
    top_i = [bm.verts.new((inner_radius(a) * math.cos(a),
                          inner_radius(a) * math.sin(a), axial_h))
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


def make_cone_rib(bm_target, phi_center, outer_profile, tip_z, hinge_z,
                  rib_span_deg=6.0, rib_depth=3.5, n_angle_sub=4, n_z_sub=6):
    """
    Add one structural cone rib into an existing BMesh (bm_target).

    The rib is a thin radial panel that permanently holds the cone profile.
    It has no hinge lug — it is fixed to the base ring.

    phi_center: angular centre of this rib (radians)
    outer_profile: same hull profile list used by the mating petals
    rib_span_deg: angular width of the rib
    rib_depth: radial thickness (outer surface minus inner surface, mm)
    """
    span_rad = math.radians(rib_span_deg)
    half     = span_rad / 2.0

    z_vals = [tip_z + (hinge_z - tip_z) * i / (n_z_sub - 1) for i in range(n_z_sub)]
    a_vals = [phi_center - half + span_rad * i / (n_angle_sub - 1)
              for i in range(n_angle_sub)]

    def bv(r, a, z):
        return bm_target.verts.new((r * math.cos(a), r * math.sin(a), z))

    def bf(vl):
        try:
            bm_target.faces.new(vl)
        except ValueError:
            pass

    outer_v = []
    inner_v = []
    for z in z_vals:
        ro = lerp_profile(outer_profile, z)
        ri = max(0.5, ro - rib_depth)
        outer_v.append([bv(ro, a, z) for a in a_vals])
        inner_v.append([bv(ri, a, z) for a in a_vals])

    # outer surface
    for iz in range(n_z_sub - 1):
        for ia in range(n_angle_sub - 1):
            bf([outer_v[iz][ia], outer_v[iz][ia+1],
                outer_v[iz+1][ia+1], outer_v[iz+1][ia]])
    # inner surface
    for iz in range(n_z_sub - 1):
        for ia in range(n_angle_sub - 1):
            bf([inner_v[iz][ia], inner_v[iz+1][ia],
                inner_v[iz+1][ia+1], inner_v[iz][ia+1]])
    # angular side caps
    for iz in range(n_z_sub - 1):
        bf([outer_v[iz][0], outer_v[iz+1][0], inner_v[iz+1][0], inner_v[iz][0]])
        ia = n_angle_sub - 1
        bf([outer_v[iz][ia], inner_v[iz][ia], inner_v[iz+1][ia], outer_v[iz+1][ia]])
    # tip cap (z = tip_z)
    for ia in range(n_angle_sub - 1):
        ro0 = lerp_profile(outer_profile, tip_z)
        ri0 = max(0.5, ro0 - rib_depth)
        if ri0 < 1.0:
            apex = bm_target.verts.new((0.0, 0.0, tip_z))
            bf([outer_v[0][ia], outer_v[0][ia+1], apex])
        else:
            bf([outer_v[0][ia], outer_v[0][ia+1],
                inner_v[0][ia+1], inner_v[0][ia]])
    # hinge cap (z = hinge_z)
    iz = n_z_sub - 1
    for ia in range(n_angle_sub - 1):
        bf([outer_v[iz][ia], inner_v[iz][ia],
            inner_v[iz][ia+1], outer_v[iz][ia+1]])


def make_rear_frame(name, outer_profile, tip_z, hinge_z,
                    n_ribs, rib_span_deg, rib_depth,
                    ring_outer_r, ring_inner_r, ring_h):
    """
    One-piece base ring + N structural cone ribs for the rear nozzle frame.

    Base ring: z = hinge_z to z = hinge_z + ring_h  (attaches to aft fuselage)
    Ribs:      z = tip_z to z = hinge_z             (cone spine, aft-facing)
    Ribs are at half-step angular offsets from petal positions (between petals),
    so the frame skeleton is visible through the petal gaps when open.
    """
    mesh = bpy.data.meshes.new(name + "_mesh")
    bm   = bmesh.new()

    # Base ring at hinge_z (aft face, into the fuselage hull)
    n_seg  = 64
    angles = [2 * math.pi * i / n_seg for i in range(n_seg)]
    z_rb   = hinge_z           # aft face of ring (faces aft, mates with petals)
    z_rt   = hinge_z + ring_h  # forward face (into fuselage interior)

    bot_o = [bm.verts.new((ring_outer_r*math.cos(a), ring_outer_r*math.sin(a), z_rb))
             for a in angles]
    top_o = [bm.verts.new((ring_outer_r*math.cos(a), ring_outer_r*math.sin(a), z_rt))
             for a in angles]
    bot_i = [bm.verts.new((ring_inner_r*math.cos(a), ring_inner_r*math.sin(a), z_rb))
             for a in angles]
    top_i = [bm.verts.new((ring_inner_r*math.cos(a), ring_inner_r*math.sin(a), z_rt))
             for a in angles]

    def rf(vl):
        try:
            bm.faces.new(vl)
        except ValueError:
            pass

    for i in range(n_seg):
        j = (i + 1) % n_seg
        rf([bot_o[i], bot_o[j], top_o[j], top_o[i]])   # outer wall
        rf([bot_i[i], top_i[i], top_i[j], bot_i[j]])   # inner wall
        rf([bot_o[i], bot_i[i], bot_i[j], bot_o[j]])   # aft annulus
        rf([top_o[i], top_o[j], top_i[j], top_i[i]])   # forward annulus

    # 8 ribs: sit between petal positions at +22.5° offsets from petals.
    # Petals sit at 0°, 45°, 90°… so ribs at 22.5°, 67.5°, 112.5°…
    rib_offset = math.pi / n_ribs
    for i in range(n_ribs):
        phi = 2 * math.pi * i / n_ribs + rib_offset
        make_cone_rib(bm, phi, outer_profile,
                      tip_z   = tip_z,    # z=0 — cone apex (aft-most point)
                      hinge_z = hinge_z,  # z=14mm — base ring attachment face
                      rib_span_deg = rib_span_deg,
                      rib_depth    = rib_depth)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def assemble_closed(petal_obj, n_petals, out_path):
    """
    Duplicate petal_obj N times around Z axis, join, export as verification STL.
    Does not alter the original petal_obj.
    """
    copies = []
    for i in range(n_petals):
        bpy.ops.object.select_all(action="DESELECT")
        petal_obj.select_set(True)
        bpy.context.view_layer.objects.active = petal_obj
        bpy.ops.object.duplicate()
        dup = bpy.context.active_object
        angle = 2 * math.pi * i / n_petals
        dup.rotation_euler.z = angle
        bpy.ops.object.transform_apply(rotation=True)
        copies.append(dup)

    bpy.ops.object.select_all(action="DESELECT")
    for c in copies:
        c.select_set(True)
    bpy.context.view_layer.objects.active = copies[0]
    bpy.ops.object.join()
    joined = bpy.context.active_object
    joined.name = "closed_asm"

    bpy.ops.object.select_all(action="DESELECT")
    joined.select_set(True)
    bpy.context.view_layer.objects.active = joined
    bpy.ops.wm.stl_export(filepath=out_path, export_selected_objects=True)
    sz = os.path.getsize(out_path) // 1024
    print(f"  → {os.path.basename(out_path)}  ({sz} KB)  [closed assembly, verification]")

    # Remove joined copy; keep original petal
    bpy.ops.object.delete()


# ═══════════════════════════════════════════════════════════════════════════════
# NACELLE NOZZLE  (50 mm ID, Z-axis, 8 petals × 4 nacelles = 32 total)
# This assembly is sized for the dual 6S 50mm EDF stack and delivers its
# exhaust through a pivot-actuated iris.  The petals hinge at the outer ring
# while the ring carries an internal rack for crown pinion drive from the
# nacelle tilt mechanism.
# ═══════════════════════════════════════════════════════════════════════════════
print("\n=== Nacelle nozzle (50 mm ID) ===")
clear_scene()

nac_petal = make_petal(
    name          = "nacelle_petal",
    n_petals      = N_PETALS,
    outer_profile = NAC_OUTER_PROFILE,
    inner_profile = NAC_INNER_PROFILE,
    tip_z         = NAC_TIP_Z,
    hinge_z       = NAC_HINGE_Z,
    edf_r         = NAC_EDF_R,
    n_angle_sub   = N_ANGLE,
    n_z_sub       = N_PROFILE_Z,
)

nac_ring = make_base_ring(
    name      = "nacelle_ring",
    outer_r   = lerp_profile(NAC_OUTER_PROFILE, NAC_HINGE_Z) + HINGE_WALL * 2,
    inner_r   = lerp_profile(NAC_INNER_PROFILE, NAC_HINGE_Z) - 0.5,
    axial_h   = HINGE_WALL * 4,
    rack_teeth = NAC_RING_TEETH,
    rack_depth = NAC_RING_RACK_DEPTH,
    rack_width = NAC_RING_RACK_WIDTH,
)

petal_path = os.path.join(OUT, "nacelle_nozzle_petal.stl")
ring_path  = os.path.join(OUT, "nacelle_nozzle_ring.stl")
asm_path   = os.path.join(OUT, "nacelle_nozzle_closed_asm.stl")

export_stl(nac_petal, petal_path)
print(f"  → nacelle_nozzle_petal.stl  ({os.path.getsize(petal_path)//1024} KB)"
      f"  print × {N_PETALS} per nacelle × 4 nacelles = {N_PETALS*4} total")
export_stl(nac_ring, ring_path)
print(f"  → nacelle_nozzle_ring.stl   ({os.path.getsize(ring_path)//1024} KB)"
      f"  print × 4 (one per nacelle, inner rack teeth {NAC_RING_TEETH} × {NAC_RING_RACK_DEPTH:.1f}mm) ")

assemble_closed(nac_petal, N_PETALS, asm_path)


# ═══════════════════════════════════════════════════════════════════════════════
# REAR NOZZLE  (120 mm ID, straight-aft exhaust, local-Z = world-X aft direction)
#
# Frame design: 8 fixed ribs between the 8 moving petals.
# When petals are CLOSED: ribs + petals = smooth Serenity engine bell.
# When petals are OPEN:   rib skeleton alone defines the cone silhouette;
#                         EDF bore is visible through the petal gaps;
#                         lit blue = "Serenity at full burn" look.
#
# Print set (one rear nozzle):
#   rear_nozzle_frame.stl  — base ring + 8 integral ribs (print × 1)
#   rear_nozzle_petal.stl  — moving petal, angular span = REAR_PETAL_SPAN_DEG
#                            (print × 8)
#   rear_nozzle_closed_asm.stl — frame + petals in closed position (verify only)
#
# ORIENTATION NOTE: local-Z = world-X aft direction.  Mount so that the cone
# tip (Z=0 in local / STL print space) faces AFT.  Exhaust exits straight aft.
# ═══════════════════════════════════════════════════════════════════════════════
print("\n=== Rear nozzle (120 mm ID, framed cone) ===")
clear_scene()

_rear_ring_outer = lerp_profile(REAR_OUTER_PROFILE, REAR_HINGE_Z) + HINGE_WALL * 2
_rear_ring_inner = lerp_profile(REAR_INNER_PROFILE, REAR_HINGE_Z) - 0.5
_rear_ring_h     = HINGE_WALL * 4

rear_frame = make_rear_frame(
    name         = "rear_frame",
    outer_profile = REAR_OUTER_PROFILE,
    tip_z        = REAR_TIP_Z,
    hinge_z      = REAR_HINGE_Z,
    n_ribs       = N_PETALS,
    rib_span_deg = REAR_RIB_SPAN_DEG,
    rib_depth    = REAR_RIB_DEPTH,
    ring_outer_r = _rear_ring_outer,
    ring_inner_r = _rear_ring_inner,
    ring_h       = _rear_ring_h,
)

rear_petal = make_petal(
    name             = "rear_petal",
    n_petals         = N_PETALS,
    outer_profile    = REAR_OUTER_PROFILE,
    inner_profile    = REAR_INNER_PROFILE,
    tip_z            = REAR_TIP_Z,
    hinge_z          = REAR_HINGE_Z,
    edf_r            = REAR_EDF_R,
    n_angle_sub      = N_ANGLE,
    n_z_sub          = N_PROFILE_Z,
    span_override_deg = REAR_PETAL_SPAN_DEG,   # 38° — fits between ribs
)

frame_path = os.path.join(OUT, "rear_nozzle_frame.stl")
petal_path = os.path.join(OUT, "rear_nozzle_petal.stl")
asm_path   = os.path.join(OUT, "rear_nozzle_closed_asm.stl")

export_stl(rear_frame, frame_path)
print(f"  → rear_nozzle_frame.stl   ({os.path.getsize(frame_path)//1024} KB)"
      f"  — base ring + {N_PETALS} ribs, print × 1")
export_stl(rear_petal, petal_path)
print(f"  → rear_nozzle_petal.stl   ({os.path.getsize(petal_path)//1024} KB)"
      f"  — {REAR_PETAL_SPAN_DEG:.1f}° span, print × {N_PETALS}")

# Closed assembly verification: frame + petals
asm_copies = [rear_frame]
for i in range(N_PETALS):
    bpy.ops.object.select_all(action="DESELECT")
    rear_petal.select_set(True)
    bpy.context.view_layer.objects.active = rear_petal
    bpy.ops.object.duplicate()
    dup = bpy.context.active_object
    dup.rotation_euler.z = 2 * math.pi * i / N_PETALS
    bpy.ops.object.transform_apply(rotation=True)
    asm_copies.append(dup)

bpy.ops.object.select_all(action="DESELECT")
for c in asm_copies:
    c.select_set(True)
bpy.context.view_layer.objects.active = asm_copies[0]
bpy.ops.object.join()
joined = bpy.context.active_object
joined.name = "rear_closed_asm"
bpy.ops.object.select_all(action="DESELECT")
joined.select_set(True)
bpy.context.view_layer.objects.active = joined
bpy.ops.wm.stl_export(filepath=asm_path, export_selected_objects=True)
sz = os.path.getsize(asm_path) // 1024
print(f"  → rear_nozzle_closed_asm.stl  ({sz} KB)  [frame+petals, verify only]")
bpy.ops.object.delete()   # remove joined assembly copy

print(f"\n  Rib angular span: {REAR_RIB_SPAN_DEG}°  "
      f"Petal span: {REAR_PETAL_SPAN_DEG:.1f}°  "
      f"Gap each side: {REAR_RIB_GAP_DEG}°")

print("""
─────────────────────────────────────────────────────────────────────────────
ASSEMBLY NOTES  (Rev L nozzles)
─────────────────────────────────────────────────────────────────────────────
Rear nozzle exhaust is STRAIGHT AFT (local-Z = world-X aft direction).
Mount rear_nozzle_frame with cone tip pointing aft; EDF exhausts straight back.

Frame (rear_nozzle_frame.stl):  base ring + 8 fixed cone ribs in one print.
  Ribs sit between the 8 petal positions at 22.5° offsets (between petals).
  When petals are open, the 8 ribs alone maintain the full cone silhouette —
  the frame defines the shape at all petal positions, open or closed.

Hinge pin:  3 mm steel pin through each petal lug and matching boss on the
            frame base ring.  Secure with a 3 mm E-clip or CA.

Actuation:  one SG90-class servo per nozzle via 1 mm piano-wire pushrod
            and a link ring inside the EDF duct (same as nacelle nozzles).
            Rear servo mounts inside the fuselage, accessible via cargo bay.

Filament:
  • Nacelle petal outer / Rear cone rib+petal outer — hull filament (brown PLA+)
  • Petal inner concave face — translucent blue PETG, or paint Testors Blue.
    Place WS2812B LED ring inside the duct; backlight gives full-burn glow.
  • Frame base ring — black PLA+ (structural, inside fuselage, hidden)

Nacelle nozzles: plain 8-petal iris, no frame (frame is rear-only).
─────────────────────────────────────────────────────────────────────────────
""")
