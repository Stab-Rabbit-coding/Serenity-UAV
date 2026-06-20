#!/usr/bin/env python3
"""
serenity_render_views.py — Rev R1 (2026-06-15)

Multi-view render suite for the Serenity UAV 24" assembly.

Imports all baked hull-frame STLs and renders 17 PNG images:
  6  principal-aspect overviews  (port, stbd, top, bottom, bow, stern)
  8  diagonal iso overviews      (all 8 corners of the bounding box)
  3  close-up shots              (nose/bow, landing gear, port nacelle)

Output: graphical-build-guide/pngs/  (1920×1080 PNG, CYCLES renderer)

Hull-frame coordinate system (CLAUDE.md Rev R1):
  X  positive port  (left)   — matches Blender world X
  Y  positive aft   (back)   — matches Blender world Y  (nose at Y ≈ −306)
  Z  positive dorsal (up)    — matches Blender world Z

Run with:
  blender --background --python serenity_render_views.py

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
"""

import bpy
import math
import os
from mathutils import Vector, Euler

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO   = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STLS   = os.path.join(REPO, "airframe", "stls")
OUT    = os.path.join(REPO, "graphical-build-guide", "pngs")
os.makedirs(OUT, exist_ok=True)

print(f"[render] repo  = {REPO}")
print(f"[render] stls  = {STLS}")
print(f"[render] out   = {OUT}")

# ---------------------------------------------------------------------------
# Baked hull-frame assembly centre (from CLAUDE.md validated extents)
#   X: −428.1 (stbd nacelle tip) to +86.0 (port nacelle tip)  → Cx ≈ −171
#   Y: −305.7 (nose tip)          to +384.3 (stern tip)         → Cy ≈  +39
#   Z:    0.0 (cargo belly)       to +201.5 (head dorsal crown)  → Cz ≈ +101
# All values in mm (= Blender scene units here).
# ---------------------------------------------------------------------------
CX, CY, CZ = -171.0, 39.0, 80.0   # ship geometric centre (hull frame, mm)

SHIP_HALF_W = 257.0   # half-width  (mm) — nacelle tip to nacelle tip
SHIP_HALF_L = 345.0   # half-length (mm) — nose to stern from Cy
SHIP_HALF_H = 101.0   # half-height (mm) — belly to crown from Cz

TARGET = (CX, CY, CZ)             # look-at point for all cameras

# ---------------------------------------------------------------------------
# STL component catalogue
#   (path_relative_to_STLS, object_name, material_key)
# ---------------------------------------------------------------------------
FUSELAGE_COLOR  = (0.72, 0.60, 0.44, 1.0)   # warm sandy tan
NACELLE_COLOR   = (0.55, 0.46, 0.34, 1.0)   # slightly darker tan
WING_COLOR      = (0.70, 0.58, 0.42, 1.0)   # near fuselage
GEAR_COLOR      = (0.30, 0.28, 0.25, 1.0)   # dark charcoal for landing gear
DETAIL_COLOR    = (0.40, 0.36, 0.28, 1.0)   # medium brown for accessories
PROP_COLOR      = (0.18, 0.16, 0.14, 1.0)   # near-black for propulsion units
SERVO_COLOR     = (0.35, 0.30, 0.20, 1.0)   # dark tan for servos
BATT_COLOR      = (0.20, 0.30, 0.18, 1.0)   # dark green for battery pack

# All STL components — tuple of (relative_path, obj_name, color_rgba).
# BAKED components (hull-frame, identity placement):
#   head, cargo, middle, rear, nacelles, wings — exact positions verified in FreeCAD.
# PLACEHOLDER components (part-local / approximate, identity placement per assembly script):
#   landing gear, pylon, tip caps, antenna fin — included for visual completeness.
COMPONENTS = [
    # --- Baked hull-frame (exact) ---
    ("fuselage/head_shell24_2mm_repaired.stl",
     "Head",           FUSELAGE_COLOR),
    ("fuselage/cargo/cargo_sect_shell24_2mm_repaired.stl",
     "Cargo",          FUSELAGE_COLOR),
    ("fuselage/middle_shell24_2mm_repaired.stl",
     "Middle",         FUSELAGE_COLOR),
    ("fuselage/rear_shell24_2mm_repaired.stl",
     "Rear",           FUSELAGE_COLOR),
    ("nacelles/nacelle_port_revq.stl",
     "Nacelle_Port",   NACELLE_COLOR),
    ("nacelles/nacelle_stbd_revq.stl",
     "Nacelle_Stbd",   NACELLE_COLOR),
    ("wings/wing_port_s1223_revo.stl",
     "Wing_Port",      WING_COLOR),
    ("wings/wing_stbd_s1223_revo.stl",
     "Wing_Stbd",      WING_COLOR),

    # --- Landing gear: STALE pre-R1.4 single-leg render, orphaned by the Rev
    # R1.4 corner V-brace frame redesign; see TODO.md 1.1.4.1. Re-render via
    # landing_leg_assy.scad PART="assy" before relying on this view.
    ("fuselage/landing-gear/landing_legs_hull_r1.stl",
     "Landing_Legs",   GEAR_COLOR),
    # Pylon (wing-to-nacelle tilt pivot): placement unverified in FreeCAD.
    ("wings/wing_nacelle_pylon_revo.stl",
     "Pylon",          DETAIL_COLOR),
    # Nacelle tip caps (port and stbd)
    ("nacelles/nacelle_tip_cap_port.stl",
     "TipCap_Port",    NACELLE_COLOR),
    ("nacelles/nacelle_tip_cap_stbd.stl",
     "TipCap_Stbd",    NACELLE_COLOR),
    # Dorsal antenna fin (fuselage top)
    ("fuselage/dorsal_antenna_fin.stl",
     "Dorsal_Fin",     DETAIL_COLOR),
    # Nacelle internal printed sub-components (part-local Z = duct axis; loaded
    # at identity — approximate visual position only, not hull-frame verified)
    ("nacelles/edf_stator_sleeve.stl",
     "Stator_Sleeve",  DETAIL_COLOR),
    ("nacelles/edf_aft_spider_sleeve.stl",
     "Spider_Sleeve",  DETAIL_COLOR),
    ("nacelles/nozzles/nacelle_nozzle_closed_asm.stl",
     "Nozzle_Asm",     DETAIL_COLOR),
    # Cargo bay doors (printed; positioned in cargo-section local frame)
    ("fuselage/cargo/cargo_door_port.stl",
     "Cargo_Door_Port", FUSELAGE_COLOR),
    ("fuselage/cargo/cargo_door_stbd.stl",
     "Cargo_Door_Stbd", FUSELAGE_COLOR),
]

# ---------------------------------------------------------------------------
# Placeholder components — non-printable hardware, with hull-frame offsets
# and optional part-local rotations so they align with the baked assembly.
#
# Nacelle bake transform (tools/bake_hull_frame.py, Rev R1):
#   Quaternion (_SQ2, 0, 0, -_SQ2) = R_x(90°): scad_z → hull_y, scad_y → -hull_z
#   Port  bake translation: (47, -64, 63)  mm
#   Stbd  bake translation: (-385, -70, 65) mm
#
# EDF SCAD axial midpoints (tandem pair, total duct ≈ 172 mm):
#   Fore EDF centre: scad_z ≈ 43 → hull_y = 43 - 64 = -21  (port); -27 (stbd)
#   Aft  EDF centre: scad_z ≈ 129 → hull_y = 129 - 64 = +65 (port); +59 (stbd)
#
# Tuple: (abs_path, obj_name, color_rgba, offset_xyz_mm, rotation_euler_rad | None)
# ---------------------------------------------------------------------------
_PH = os.path.join(REPO, "airframe", "placeholders")
_NAC_ROT = (math.radians(90), 0.0, 0.0)   # rotate part-local Z onto hull Y

PHCOMPONENTS = [
    # --- Port nacelle propulsion (hull X ≈ 47, Z ≈ 63) ---
    (os.path.join(_PH, "propulsion", "EDF_50mm_6S.stl"),
     "EDF_Port_Fore", PROP_COLOR, (47, -21, 63), _NAC_ROT),
    (os.path.join(_PH, "propulsion", "EDF_50mm_6S.stl"),
     "EDF_Port_Aft",  PROP_COLOR, (47,  65, 63), _NAC_ROT),
    # --- Stbd nacelle propulsion (hull X ≈ -385, Z ≈ 65) ---
    (os.path.join(_PH, "propulsion", "EDF_50mm_6S.stl"),
     "EDF_Stbd_Fore", PROP_COLOR, (-385, -27, 65), _NAC_ROT),
    (os.path.join(_PH, "propulsion", "EDF_50mm_6S.stl"),
     "EDF_Stbd_Aft",  PROP_COLOR, (-385,  59, 65), _NAC_ROT),
    # --- ESC units (one per EDF, approximate — mounted on nacelle wall) ---
    (os.path.join(_PH, "propulsion", "ESC_40A_6S_BLHeli32.stl"),
     "ESC_Port_Fore",  PROP_COLOR, (70, -21, 90), _NAC_ROT),
    (os.path.join(_PH, "propulsion", "ESC_40A_6S_BLHeli32.stl"),
     "ESC_Port_Aft",   PROP_COLOR, (70,  65, 90), _NAC_ROT),
    (os.path.join(_PH, "propulsion", "ESC_40A_6S_BLHeli32.stl"),
     "ESC_Stbd_Fore",  PROP_COLOR, (-368, -27, 90), _NAC_ROT),
    (os.path.join(_PH, "propulsion", "ESC_40A_6S_BLHeli32.stl"),
     "ESC_Stbd_Aft",   PROP_COLOR, (-368,  59, 90), _NAC_ROT),
    # --- Tilt servos — one per nacelle, at pylon pivot (approximate) ---
    (os.path.join(_PH, "servos", "DS3218MG_25kgcm.stl"),
     "Servo_Port_Tilt", SERVO_COLOR, (80, 22, 63), None),
    (os.path.join(_PH, "servos", "DS3218MG_25kgcm.stl"),
     "Servo_Stbd_Tilt", SERVO_COLOR, (-375, 16, 65), None),
    # --- Main battery (cargo bay, approximate longitudinal centre) ---
    (os.path.join(_PH, "power", "LiPo_6S_4000mAh_138x44x36mm.stl"),
     "Battery_Main", BATT_COLOR, (CX, 20, 40), None),
]

# ---------------------------------------------------------------------------
# Renderer setup
# ---------------------------------------------------------------------------
def setup_renderer(res: tuple = (1280, 720)) -> None:
    """
    Configure EEVEE-NEXT for fast headless rendering.

    EEVEE-NEXT (rasteriser) is used instead of Cycles because the fuselage
    STLs total ~5 M triangles, which makes Cycles path-tracing prohibitively
    slow on the project's 4-core i7-7600U build machine.  EEVEE-NEXT handles
    the same mesh data in seconds per frame at equivalent visual quality for
    build-guide illustrations.
    """
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.compression = 15
    print(f"[render] EEVEE-NEXT renderer, {res[0]}×{res[1]}")

# ---------------------------------------------------------------------------
# Scene utility
# ---------------------------------------------------------------------------
def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for block in list(bpy.data.meshes) + list(bpy.data.cameras) + list(bpy.data.lights):
        try:
            bpy.data.batch_remove((block,))
        except Exception:
            pass

# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------
_MAT_CACHE: dict = {}

def get_material(color_rgba: tuple) -> bpy.types.Material:
    key = color_rgba
    if key in _MAT_CACHE:
        return _MAT_CACHE[key]
    r, g, b, a = color_rgba
    name = f"Mat_{r:.2f}_{g:.2f}_{b:.2f}"
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out  = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (r, g, b, a)
    bsdf.inputs["Roughness"].default_value = 0.78
    bsdf.inputs["Metallic"].default_value = 0.05
    # Blender 4.x uses 'Specular IOR Level'; 3.x used 'Specular'.
    try:
        bsdf.inputs["Specular IOR Level"].default_value = 0.25
    except KeyError:
        try:
            bsdf.inputs["Specular"].default_value = 0.25
        except KeyError:
            pass

    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    _MAT_CACHE[key] = mat
    return mat

# ---------------------------------------------------------------------------
# STL import
# ---------------------------------------------------------------------------
def import_stl(filepath: str, obj_name: str, material: bpy.types.Material,
               offset: tuple | None = None,
               rotation: tuple | None = None) -> bpy.types.Object | None:
    if not os.path.isfile(filepath):
        print(f"[render] SKIP (not found): {filepath}")
        return None
    print(f"[render] importing {os.path.basename(filepath)} …")
    # Blender 4.0+ uses wm.stl_import; older builds use import_mesh.stl.
    try:
        bpy.ops.wm.stl_import(filepath=filepath)
    except AttributeError:
        bpy.ops.import_mesh.stl(filepath=filepath)
    objs = bpy.context.selected_objects
    if not objs:
        print(f"[render] WARN: import produced no objects for {filepath}")
        return None
    obj = objs[0]
    obj.name = obj_name

    # Apply smooth shading (Blender 4.x shade_smooth_by_angle preferred)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    try:
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(60))
    except AttributeError:
        bpy.ops.object.shade_smooth()

    # Optional part-local rotation (Euler XYZ, radians) for placeholder alignment
    if rotation is not None:
        obj.rotation_euler = Euler(rotation)
    # Optional part-local → hull-frame translation for non-baked parts
    if offset is not None:
        obj.location.x += offset[0]
        obj.location.y += offset[1]
        obj.location.z += offset[2]

    # Assign material
    obj.data.materials.clear()
    obj.data.materials.append(material)
    return obj

# ---------------------------------------------------------------------------
# Lighting
# ---------------------------------------------------------------------------
def setup_lighting() -> None:
    """
    Three-point sun-lamp rig for EEVEE-NEXT.

    SUN lamps are used instead of area lights because the scene is in mm units:
    area lights at 2000 mm standoff would need ~1e7 W to illuminate the hull,
    while SUN lamps have no distance falloff and are trivial to tune.
    A weak area lamp below the hull provides the belly bounce fill.
    """
    # World: dark near-space blue-grey with mild ambient
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background") or \
         world.node_tree.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.05, 0.06, 0.10, 1.0)
    bg.inputs["Strength"].default_value = 0.30

    def add_sun(name: str, direction: tuple, strength: float,
                color=(1.0, 0.98, 0.92)) -> None:
        """Add a directional SUN lamp pointing in *direction* (world XYZ vector)."""
        light = bpy.data.lights.new(name, "SUN")
        light.energy = strength
        light.color = color
        light.angle = math.radians(5)   # slight angular size for soft shadows
        obj = bpy.data.objects.new(name, light)
        bpy.context.scene.collection.objects.link(obj)
        # Sun direction is set via the object's -Z axis tracking the target.
        dir_v = Vector(direction).normalized()
        obj.rotation_euler = dir_v.to_track_quat("-Z", "Y").to_euler()

    def add_area(name: str, loc: tuple, energy: float, size: float,
                 rot_euler=(0, 0, 0), color=(1.0, 1.0, 1.0)) -> None:
        light = bpy.data.lights.new(name, "AREA")
        light.energy = energy
        light.size = size
        light.color = color
        obj = bpy.data.objects.new(name, light)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = loc
        obj.rotation_euler = Euler([math.radians(a) for a in rot_euler])

    # Key — port-fore-dorsal (main illumination, warm white)
    add_sun("Key",    ( 0.6, -0.7,  0.8),  5.0)
    # Fill — starboard-fore (softer, cool blue)
    add_sun("Fill",   (-0.7, -0.5,  0.3),  1.8, color=(0.80, 0.88, 1.00))
    # Rim — aft-dorsal (warm accent on the stern)
    add_sun("Rim",    ( 0.0,  0.8,  0.6),  2.0, color=(1.00, 0.95, 0.80))
    # Bounce — belly fill (large area lamp below, no falloff concern at hull scale)
    add_area("Bounce", (CX, CY, CZ - 1000), 8e6, 1200,
             rot_euler=(70, 0, 0), color=(0.90, 0.85, 0.75))

# ---------------------------------------------------------------------------
# Camera helpers
# ---------------------------------------------------------------------------
def look_at_euler(cam: tuple, tgt: tuple, up: tuple = (0, 0, 1)) -> Euler:
    """Return Euler rotation for a camera at *cam* looking at *tgt*."""
    direction = Vector(tgt) - Vector(cam)
    rot = direction.to_track_quat("-Z", "Y")
    return rot.to_euler()

def add_camera(name: str, location: tuple, target: tuple,
               lens: float = 85.0) -> bpy.types.Object:
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    cam_data.clip_start = 1.0
    cam_data.clip_end = 10000.0
    obj = bpy.data.objects.new(name, cam_data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = Vector(location)
    obj.rotation_euler = look_at_euler(location, target)
    return obj

def render_camera(cam_obj: bpy.types.Object, filename: str) -> None:
    bpy.context.scene.camera = cam_obj
    outpath = os.path.join(OUT, filename)
    bpy.context.scene.render.filepath = outpath
    print(f"[render] rendering → {filename}")
    bpy.ops.render.render(write_still=True)
    print(f"[render] saved     → {outpath}.png")

# ---------------------------------------------------------------------------
# Camera position catalogue
#
# Hull frame orientation in Blender world space:
#   +X = port (left wing outboard)
#   +Y = aft  (stern / engine)
#   -Y = forward (nose)
#   +Z = dorsal (up)
# ---------------------------------------------------------------------------

# Overview stand-off distance
OVR = 1600   # mm from scene centre for principal views
ISO = 1500   # mm from scene centre for iso views (scaled per axis)

OVERVIEW_CAMERAS = [
    # (filename,        camera_pos,                     target,  lens, label)
    ("01_port",    (CX + OVR,  CY,            CZ + 20),  TARGET, 85,  "Port side"),
    ("02_stbd",    (CX - OVR,  CY,            CZ + 20),  TARGET, 85,  "Starboard side"),
    ("03_top",     (CX,        CY,            CZ + OVR), TARGET, 85,  "Dorsal (top)"),
    ("04_bottom",  (CX,        CY,            CZ - OVR), TARGET, 85,  "Ventral (bottom)"),
    ("05_bow",     (CX,        CY - OVR,      CZ + 30),  TARGET, 85,  "Bow (forward)"),
    ("06_stern",   (CX,        CY + OVR,      CZ + 30),  TARGET, 85,  "Stern (aft)"),
]

# Eight diagonal iso views — one per octant
_s = ISO * 0.707   # unit-sphere projection for 45° diagonals
_z_up = ISO * 0.55
_z_dn = ISO * 0.45
ISO_CAMERAS = [
    ("07_iso_port_bow_dorsal",   (CX + _s, CY - _s, CZ + _z_up), TARGET, 70),
    ("08_iso_stbd_bow_dorsal",   (CX - _s, CY - _s, CZ + _z_up), TARGET, 70),
    ("09_iso_port_stern_dorsal", (CX + _s, CY + _s, CZ + _z_up), TARGET, 70),
    ("10_iso_stbd_stern_dorsal", (CX - _s, CY + _s, CZ + _z_up), TARGET, 70),
    ("11_iso_port_bow_ventral",  (CX + _s, CY - _s, CZ - _z_dn), TARGET, 70),
    ("12_iso_stbd_bow_ventral",  (CX - _s, CY - _s, CZ - _z_dn), TARGET, 70),
    ("13_iso_port_stern_ventral",(CX + _s, CY + _s, CZ - _z_dn), TARGET, 70),
    ("14_iso_stbd_stern_ventral",(CX - _s, CY + _s, CZ - _z_dn), TARGET, 70),
]

# Close-up targets (hull frame, mm)
# Nose tip area: head section Y ≈ -305, X ≈ CX, Z ≈ 130 (mid-height of head)
NOSE_TGT = (CX, -280, 130)
# Port nacelle centre (baked extents): X ≈ 45, Y ≈ 22, Z ≈ 63
NACELLE_TGT = (45, 22, 63)
# Landing gear: under rear section, stern belly
GEAR_TGT = (CX, 290, 20)

CLOSEUP_CAMERAS = [
    # (filename,       camera_pos,                           target,       lens)
    ("15_closeup_nose",     (CX - 150, -700, 170),          NOSE_TGT,     50),
    ("16_closeup_gear",     (CX + 350, 280, -200),          GEAR_TGT,     60),
    ("17_closeup_nacelle",  (CX + 350, -180, 230),          NACELLE_TGT,  60),
]

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("[render] === Serenity UAV render suite starting ===")

    clear_scene()
    setup_renderer(res=(1280, 720))   # 720p preview; increase for finals

    # Import all airframe STL components (baked hull-frame and part-local)
    for rel_path, name, color in COMPONENTS:
        full_path = os.path.join(STLS, rel_path)
        mat = get_material(color)
        import_stl(full_path, name, mat)

    # Import placeholder hardware with hull-frame offsets and orientations
    for full_path, name, color, offset, rotation in PHCOMPONENTS:
        mat = get_material(color)
        import_stl(full_path, name, mat, offset=offset, rotation=rotation)

    print("[render] All STLs imported — setting up lighting")
    setup_lighting()

    # -- Overview cameras --
    print("[render] === Overview renders ===")
    for fname, cam_loc, tgt, lens, label in OVERVIEW_CAMERAS:
        cam = add_camera(f"Cam_{fname}", cam_loc, tgt, lens)
        render_camera(cam, fname)

    # -- Iso cameras --
    print("[render] === Iso renders ===")
    for entry in ISO_CAMERAS:
        fname, cam_loc, tgt, lens = entry
        cam = add_camera(f"Cam_{fname}", cam_loc, tgt, lens)
        render_camera(cam, fname)

    # -- Close-up cameras --
    print("[render] === Close-up renders ===")
    for fname, cam_loc, tgt, lens in CLOSEUP_CAMERAS:
        cam = add_camera(f"Cam_{fname}", cam_loc, tgt, lens)
        render_camera(cam, fname)

    print(f"[render] === Complete. {len(OVERVIEW_CAMERAS) + len(ISO_CAMERAS) + len(CLOSEUP_CAMERAS)} images → {OUT} ===")


if __name__ == "__main__":
    main()
