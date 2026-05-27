"""
generate_overview_svgs.py  —  run with:
    python3 generate_overview_svgs.py

Generates 10 orthographic/isometric overview SVG drawings of the Serenity UAV
assembly from the repaired and scaled STL shell files:

    6 orthographic: top, bottom, port, starboard, bow, stern
    4 isometric:    port_bow, starboard_bow, port_quarter, starboard_quarter

Coordinate system (24"-scaled STL world space, per s_head_shell24.scad):
    X -- longitudinal, positive toward nose
    Y -- vertical,     positive toward dorsal (up)
    Z -- lateral,      positive toward port (left)
    Station mapping: X_stl = 284 - station_mm

Hull centreline references (from s_head_shell24.scad comments):
    Hull Y-centreline:  CY  ≈ -149 mm
    Hull Z-centreline:  CZ  ≈   69 mm

Painter's algorithm with Lambertian shading.  Triangles are subsampled
(SUBSAMPLE_STEP=25) to keep SVG files to a manageable size while preserving
enough detail for engineering overview drawings.

Nacelle shells are shown in approximate hover-mode (nacelle axis vertical).
The nacelle assembly transform rotates the print-bed STL (bore axis = Z_stl)
so the bore axis becomes the world Y axis (vertical/hover).  Lateral offsets
are estimated from the pylon geometry (PYLON_SPAN=88 mm, NACELLE_OD_X/2=34 mm).

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
Date:    2026-05-26

References:
    s_head_shell24.scad      — coordinate system documentation, hull centroid
    s_wing_nacelle_pylon_revo.scad — PYLON_SPAN, PYLON_W, PYLON_H geometry
    nacelle_pod_50mm_tandem.scad   — NACELLE_FACE_X_PYLON, NACELLE_L
    Thingiverse Thing 14474 (Serenity Spaceship) — source hull geometry
"""

import os
import struct
import math
import zlib

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STL_DIR  = os.path.join(BASE_DIR, "files-hollowed-18in")
OUT_DIR  = os.path.join(BASE_DIR, "overview_svgs")

# Only include every Nth triangle (reduces SVG size while preserving shape).
# Increase for higher fidelity; decrease for smaller/faster files.
SUBSAMPLE_STEP = 25

# SVG canvas dimensions in pixels / mm (1 px = 1 mm at 100% zoom)
SVG_W  = 1600
SVG_H  = 1000
MARGIN = 60       # px margin around projected geometry

# Lighting: unit vector toward primary light source (in world coords X,Y,Z).
# Upper-port-bow lamp gives clear shading contrast on most views.
_lx, _ly, _lz = 1.0, 1.5, 1.0
_lm = math.sqrt(_lx*_lx + _ly*_ly + _lz*_lz)
LIGHT_DIR = (_lx/_lm, _ly/_lm, _lz/_lm)
AMBIENT   = 0.28   # minimum shade fraction (0=dark, 1=no shading)

# ---------------------------------------------------------------------------
# Part definitions: (filename, (R, G, B) base colour)
# Colours are in 0..255 integer range.
# ---------------------------------------------------------------------------

# Hull Y-centreline and Z-centreline (world coords) — from s_head_shell24.scad.
HULL_CY = -149.0
HULL_CZ =   69.0

# Nacelle pylon geometry (from s_wing_nacelle_pylon_revo.scad).
PYLON_SPAN    =  88.0   # [mm] nacelle face → wing-root face
NACELLE_FACE_X =  34.0  # [mm] bore-centre to inboard nacelle X-face (= pylon attach)
# Fuselage Z half-width at pylon station (approx, from head Z-bounds / 2).
# Head Z: 0..140, centreline at 69.  Half-width ≈ 69 mm.
FUSE_Z_HALFWIDTH = 70.0
# Port nacelle bore lateral position: centreline + half-width + pylon
NACELLE_PORT_Z   = HULL_CZ + FUSE_Z_HALFWIDTH + NACELLE_FACE_X + PYLON_SPAN
NACELLE_STBD_Z   = HULL_CZ - FUSE_Z_HALFWIDTH - NACELLE_FACE_X - PYLON_SPAN

# Nacelle station (X world) — forward pylon station ≈ station 200 mm from nose.
# Station mapping: X_stl = 284 - station_mm.
NACELLE_STATION_MM = 200.0
NACELLE_X_WORLD    = 284.0 - NACELLE_STATION_MM   # ≈ +84 mm

# Nacelle altitude: in hover mode, intake (Z_nac=0) is at the top.
# The pylon pivot attaches at Z_nac ≈ 83 mm from intake.
# Set the pylon connection height at fuselage Y-centreline (≈ hull top, ≈ -90 mm).
NACELLE_PIVOT_Z_NAC  =  83.0   # [mm] nacelle local Z of pivot (from intake end)
NACELLE_PIVOT_Y_WORLD = HULL_CY + 60.0  # ≈ hull top rail height

# ---------------------------------------------------------------------------
# Parts list
# ---------------------------------------------------------------------------

def _rgb(r, g, b):
    return (r, g, b)

PARTS = [
    # (filename,                        colour,            transform_fn_or_None)
    ("s_head_shell24_repaired.stl",     _rgb(120, 130, 145), None),
    ("s_middle_shell24.stl",            _rgb(130, 145, 160), None),
    ("s_cargo_sect_shell24_repaired.stl",_rgb(110, 122, 135),None),
    ("s_rear_shell24_repaired.stl",     _rgb(105, 118, 130), None),
    ("s_wings_both_shell24.stl",        _rgb( 90, 100, 115), None),
    # 1× nacelles (not repaired but suitable for overview rendering)
    ("s_eng_left_shell24.stl",          _rgb( 80, 120, 145), "nacelle_port"),
    ("s_eng_right_shell24.stl",         _rgb( 80, 120, 145), "nacelle_stbd"),
]

# ---------------------------------------------------------------------------
# Math utilities
# ---------------------------------------------------------------------------

def _dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]


def _cross(a, b):
    return (
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0],
    )


def _normalize(v):
    m = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    if m < 1e-12:
        return (0.0, 0.0, 1.0)
    return (v[0]/m, v[1]/m, v[2]/m)


def _mat_vec(m, v):
    """Multiply 3×3 row-major matrix m by column vector v."""
    return (
        m[0]*v[0] + m[1]*v[1] + m[2]*v[2],
        m[3]*v[0] + m[4]*v[1] + m[5]*v[2],
        m[6]*v[0] + m[7]*v[1] + m[8]*v[2],
    )


def _add(a, b):
    return (a[0]+b[0], a[1]+b[1], a[2]+b[2])


def _sub(a, b):
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])


# ---------------------------------------------------------------------------
# Nacelle assembly transforms
#
# The nacelle STLs have their bore axis along world Z (lateral).  To show them
# in hover mode (bore axis = world Y, vertical), we apply a cyclic permutation:
#   new = (old.y, old.z, old.x)
# followed by a translation to the assembly position.
#
# Bore centre in 1× STL space: left=(34.18, -152.63), right=(124.0, -152.5),
# both at Z-midpoint ≈ 74.1 mm.
#
# Port (left) nacelle bore centre after rotation (y,z,x):
#   new_x = old.y = -152.63   (fore-aft — arbitrary print-bed offset)
#   new_y = old.z =   74.1    (vertical — bore midpoint altitude)
#   new_z = old.x =   34.18   (lateral — bore centre in cross-section)
#
# We subtract (bore_x_after, bore_y_after, bore_z_after) then add assembly offset.
# ---------------------------------------------------------------------------

# 1× nacelle bore centres (from inspect_shell_center.py / memory ÷ 1.25)
_BORE_CX_L =  34.18   # [mm] left nacelle bore X in STL space
_BORE_CY_L = -152.63  # [mm] left nacelle bore Y in STL space
_BORE_CZ_L =   74.15  # [mm] left nacelle bore Z (axial midpoint)
_BORE_CX_R = 124.00   # [mm] right nacelle bore X in STL space
_BORE_CY_R = -152.50
_BORE_CZ_R =   74.15

# After rotation (old.y, old.z, old.x), bore centre becomes:
_BORE_L_AFTER = (_BORE_CY_L, _BORE_CZ_L, _BORE_CX_L)   # (-152.63, 74.15, 34.18)
_BORE_R_AFTER = (_BORE_CY_R, _BORE_CZ_R, _BORE_CX_R)   # (-152.50, 74.15, 124.00)

# Assembly position for bore centre in world coords (hover mode):
# X: pylon-station fore-aft position
# Y: pivot altitude + (NACELLE_L/2 - NACELLE_PIVOT_Z_NAC) to centre nacelle at pivot
#    In hover: intake (Z_nac=0) is UP.  Nacelle Y at bore mid ≈ pivot Y.
_NACELLE_ASSM_Y = NACELLE_PIVOT_Y_WORLD  # bore is approximately at pivot height

_ASSM_PORT = (NACELLE_X_WORLD, _NACELLE_ASSM_Y, NACELLE_PORT_Z)
_ASSM_STBD = (NACELLE_X_WORLD, _NACELLE_ASSM_Y, NACELLE_STBD_Z)


def _nacelle_transform(v, bore_after, assm_pos):
    """
    Rotate nacelle STL vertex from print-bed orientation to hover mode,
    then translate to assembly position.

    Rotation: (x,y,z) -> (y, z, x) — cyclic permutation so that:
        old Z (bore/nacelle axis) -> new Y (vertical in hover)
        old X (inboard/outboard)  -> new Z (lateral)
        old Y (fore-aft)          -> new X (longitudinal)
    """
    rx = v[1]
    ry = v[2]
    rz = v[0]
    # Subtract bore-centre-after-rotation, add assembly offset
    wx = rx - bore_after[0] + assm_pos[0]
    wy = ry - bore_after[1] + assm_pos[1]
    wz = rz - bore_after[2] + assm_pos[2]
    return (wx, wy, wz)


def _nacelle_normal(n, _bore_after, _assm_pos):
    """Apply same rotation to the surface normal (no translation)."""
    return (n[1], n[2], n[0])


# ---------------------------------------------------------------------------
# STL loading
# ---------------------------------------------------------------------------

def load_stl(path, transform_tag=None):
    """
    Load a binary STL and return a list of (normal, v0, v1, v2) tuples.

    transform_tag: 'nacelle_port', 'nacelle_stbd', or None (identity).
    Triangles are subsampled every SUBSAMPLE_STEP entries.
    """
    if not os.path.isfile(path):
        print(f"  SKIP — not found: {path}")
        return []

    triangles = []
    with open(path, 'rb') as f:
        f.read(80)  # 80-byte header
        n_tri = struct.unpack('<I', f.read(4))[0]
        for idx in range(n_tri):
            raw = f.read(50)
            if idx % SUBSAMPLE_STEP != 0:
                continue
            n  = struct.unpack_from('<3f', raw,  0)
            v0 = struct.unpack_from('<3f', raw, 12)
            v1 = struct.unpack_from('<3f', raw, 24)
            v2 = struct.unpack_from('<3f', raw, 36)

            if transform_tag == "nacelle_port":
                v0 = _nacelle_transform(v0, _BORE_L_AFTER, _ASSM_PORT)
                v1 = _nacelle_transform(v1, _BORE_L_AFTER, _ASSM_PORT)
                v2 = _nacelle_transform(v2, _BORE_L_AFTER, _ASSM_PORT)
                n  = _nacelle_normal(n,  _BORE_L_AFTER, _ASSM_PORT)
            elif transform_tag == "nacelle_stbd":
                # Starboard: mirror Z (negative port = starboard)
                v0 = _nacelle_transform(v0, _BORE_R_AFTER, _ASSM_STBD)
                v1 = _nacelle_transform(v1, _BORE_R_AFTER, _ASSM_STBD)
                v2 = _nacelle_transform(v2, _BORE_R_AFTER, _ASSM_STBD)
                n  = _nacelle_normal(n,  _BORE_R_AFTER, _ASSM_STBD)

            # Recompute normal from geometry (more reliable than STL stored normal)
            e1 = _sub(v1, v0)
            e2 = _sub(v2, v0)
            cn = _cross(e1, e2)
            cm = math.sqrt(cn[0]*cn[0]+cn[1]*cn[1]+cn[2]*cn[2])
            if cm > 1e-12:
                cn = (cn[0]/cm, cn[1]/cm, cn[2]/cm)
            else:
                cn = n  # degenerate triangle — keep stored normal

            triangles.append((cn, v0, v1, v2))

    print(f"  Loaded {len(triangles):,} tris from {os.path.basename(path)}")
    return triangles


# ---------------------------------------------------------------------------
# View definitions
#
# Each view is a dict with:
#   'right'  : world-space unit vector that maps to SVG +x (right)
#   'up'     : world-space unit vector that maps to SVG -y (up on screen)
#   'eye'    : world-space unit vector FROM the subject TO the camera
#   'label'  : human-readable name
# ---------------------------------------------------------------------------

def _make_iso(eye_x, eye_y, eye_z, label):
    """Build an isometric view from a camera direction."""
    eye = _normalize((eye_x, eye_y, eye_z))
    view_dir = (-eye[0], -eye[1], -eye[2])
    world_up = (0.0, 1.0, 0.0)
    right = _normalize(_cross(view_dir, world_up))
    up    = _normalize(_cross(right, view_dir))
    return {'right': right, 'up': up, 'eye': eye, 'label': label}


VIEWS = {
    'top': {
        'right': (1.0,  0.0,  0.0),   # nose = right
        'up':    (0.0,  0.0,  1.0),   # port = up
        'eye':   (0.0,  1.0,  0.0),   # camera above
        'label': 'TOP (nose right, port up)',
    },
    'bottom': {
        'right': (1.0,  0.0,  0.0),   # nose = right
        'up':    (0.0,  0.0, -1.0),   # starboard = up (aircraft flipped)
        'eye':   (0.0, -1.0,  0.0),   # camera below
        'label': 'BOTTOM (nose right, starboard up)',
    },
    'port': {
        'right': (1.0,  0.0,  0.0),   # nose = right
        'up':    (0.0,  1.0,  0.0),   # dorsal = up
        'eye':   (0.0,  0.0,  1.0),   # camera from port (+Z)
        'label': 'PORT (nose right, dorsal up)',
    },
    'starboard': {
        'right': (1.0,  0.0,  0.0),   # nose = right (mirrored)
        'up':    (0.0,  1.0,  0.0),   # dorsal = up
        'eye':   (0.0,  0.0, -1.0),   # camera from starboard (−Z)
        'label': 'STARBOARD (nose right, dorsal up)',
    },
    'bow': {
        'right': (0.0,  0.0, -1.0),   # port = left, starboard = right
        'up':    (0.0,  1.0,  0.0),   # dorsal = up
        'eye':   (1.0,  0.0,  0.0),   # camera from forward (+X)
        'label': 'BOW (port left, dorsal up)',
    },
    'stern': {
        'right': (0.0,  0.0,  1.0),   # port = right (looking aft)
        'up':    (0.0,  1.0,  0.0),   # dorsal = up
        'eye':   (-1.0, 0.0,  0.0),   # camera from aft (−X)
        'label': 'STERN (port right, dorsal up)',
    },
    'iso_port_bow':      _make_iso( 1.0, 0.7,  1.0, 'ISOMETRIC: PORT BOW'),
    'iso_starboard_bow': _make_iso( 1.0, 0.7, -1.0, 'ISOMETRIC: STARBOARD BOW'),
    'iso_port_quarter':  _make_iso(-1.0, 0.7,  1.0, 'ISOMETRIC: PORT QUARTER'),
    'iso_stbd_quarter':  _make_iso(-1.0, 0.7, -1.0, 'ISOMETRIC: STARBOARD QUARTER'),
}


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _proj2d(v, right, up):
    """Project world vertex v to 2D (x_right, y_up) in mm."""
    return (_dot(v, right), _dot(v, up))


def _tri_depth(v0, v1, v2, eye):
    """Centroid depth along eye direction (larger = closer to camera)."""
    cx = (v0[0]+v1[0]+v2[0]) / 3.0
    cy = (v0[1]+v1[1]+v2[1]) / 3.0
    cz = (v0[2]+v1[2]+v2[2]) / 3.0
    return cx*eye[0] + cy*eye[1] + cz*eye[2]


def _shade(normal, view_eye):
    """
    Lambertian shade for a front-facing triangle.  Returns 0.0..1.0.
    Adds a small back-face contribution so interior surfaces aren't pure black.
    """
    d = _dot(normal, LIGHT_DIR)
    facing = _dot(normal, view_eye)  # positive = faces the camera
    if facing > 0.0:
        # Front face: full Lambertian
        d = max(0.0, d)
        return AMBIENT + (1.0 - AMBIENT) * d
    else:
        # Back face (should be culled but included for partial transparency feel)
        return AMBIENT * 0.4


def _colour_svg(base_rgb, shade_val):
    """Return '#rrggbb' string given base colour tuple and 0..1 shade value."""
    r = min(255, int(base_rgb[0] * shade_val))
    g = min(255, int(base_rgb[1] * shade_val))
    b = min(255, int(base_rgb[2] * shade_val))
    return f"#{r:02x}{g:02x}{b:02x}"


def render_view(all_parts_tris, view, out_path):
    """
    Painter's algorithm SVG render for one view.

    all_parts_tris: list of (triangles, base_colour) per part.
    """
    right = view['right']
    up    = view['up']
    eye   = view['eye']
    label = view['label']

    # Collect all (depth, shade, svg_colour, p0, p1, p2)
    items = []
    for tris, base_rgb in all_parts_tris:
        for (n, v0, v1, v2) in tris:
            # Back-face cull: skip triangles facing away from camera
            facing = _dot(n, eye)
            if facing < -0.05:   # allow a small threshold for seams
                continue
            depth = _tri_depth(v0, v1, v2, eye)
            shade_val = _shade(n, eye)
            col = _colour_svg(base_rgb, shade_val)
            p0 = _proj2d(v0, right, up)
            p1 = _proj2d(v1, right, up)
            p2 = _proj2d(v2, right, up)
            items.append((depth, col, p0, p1, p2))

    if not items:
        print(f"  WARNING: no visible triangles for {label}")
        return

    # Sort back-to-front (smaller depth = further away = paint first)
    items.sort(key=lambda t: t[0])

    # Find projected bounding box
    all_x = [p[0] for _, _, p0, p1, p2 in items for p in (p0, p1, p2)]
    all_y = [p[1] for _, _, p0, p1, p2 in items for p in (p0, p1, p2)]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)

    span_x = max_x - min_x
    span_y = max_y - min_y

    draw_w = SVG_W - 2 * MARGIN
    draw_h = SVG_H - 2 * MARGIN

    if span_x < 1e-6 or span_y < 1e-6:
        scale = 1.0
    else:
        scale = min(draw_w / span_x, draw_h / span_y)

    # Centre within canvas
    mid_x = (min_x + max_x) / 2.0
    mid_y = (min_y + max_y) / 2.0
    off_x = SVG_W / 2.0 - mid_x * scale
    # SVG Y axis is inverted (positive = down), so negate the up-axis projection
    off_y = SVG_H / 2.0 + mid_y * scale

    def to_svg(p):
        sx = p[0] * scale + off_x
        sy = -p[1] * scale + off_y   # negate: world-up = SVG-up
        return f"{sx:.2f},{sy:.2f}"

    # Build SVG
    lines = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<!-- Serenity UAV overview — {label} -->',
        f'<!-- Generated by generate_overview_svgs.py  CC BY 4.0  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP -->',
        f'<svg xmlns="http://www.w3.org/2000/svg"',
        f'     width="{SVG_W}" height="{SVG_H}"',
        f'     viewBox="0 0 {SVG_W} {SVG_H}">',
        f'  <rect width="{SVG_W}" height="{SVG_H}" fill="#f4f4f0"/>',
        f'  <!-- border -->',
        f'  <rect x="10" y="10" width="{SVG_W-20}" height="{SVG_H-20}"',
        f'        fill="none" stroke="#888" stroke-width="1"/>',
        f'  <!-- geometry: {len(items):,} triangles, scale={scale:.3f} mm/px -->',
        f'  <g id="hull" stroke="none">',
    ]

    for (_depth, col, p0, p1, p2) in items:
        pts = f"{to_svg(p0)} {to_svg(p1)} {to_svg(p2)}"
        lines.append(f'    <polygon points="{pts}" fill="{col}"/>')

    # Title text
    lines += [
        f'  </g>',
        f'  <text x="20" y="30" font-family="monospace" font-size="14"',
        f'        fill="#333">Serenity UAV  —  {label}</text>',
        f'  <text x="20" y="{SVG_H-15}" font-family="monospace" font-size="9"',
        f'        fill="#888">CC BY 4.0  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  |  ',
        f'subsample={SUBSAMPLE_STEP}  tris={len(items):,}</text>',
        f'</svg>',
    ]

    content = "\n".join(lines)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)

    kb = os.path.getsize(out_path) // 1024
    print(f"  -> {os.path.basename(out_path)}  ({kb} KB,  {len(items):,} tris)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    print("Loading STL parts...")
    all_parts = []
    for fname, colour, transform_tag in PARTS:
        path = os.path.join(STL_DIR, fname)
        tris = load_stl(path, transform_tag)
        if tris:
            all_parts.append((tris, colour))

    total_tris = sum(len(t) for t, _ in all_parts)
    print(f"\nTotal triangles in scene: {total_tris:,}")

    print(f"\nRendering {len(VIEWS)} views to {OUT_DIR}/\n")
    for view_name, view in VIEWS.items():
        out_path = os.path.join(OUT_DIR, f"serenity_{view_name}.svg")
        print(f"  Rendering {view['label']} ...")
        render_view(all_parts, view, out_path)

    print("\nDone.")
    print(f"Output directory: {OUT_DIR}")
    print("Open any .svg file in a browser or Inkscape to view.")
    print()
    print("Assembly notes:")
    print(f"  Nacelle port Z-position (estimated):  {NACELLE_PORT_Z:.1f} mm")
    print(f"  Nacelle stbd Z-position (estimated):  {NACELLE_STBD_Z:.1f} mm")
    print(f"  Nacelle fore-aft station:              {NACELLE_STATION_MM:.0f} mm from nose")
    print("  Adjust NACELLE_STATION_MM / NACELLE_PORT_Z / NACELLE_STBD_Z as needed.")


if __name__ == "__main__":
    main()
