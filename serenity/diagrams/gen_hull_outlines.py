#!/usr/bin/env python3
"""
gen_hull_outlines.py — Generate accurate SVG hull-outline paths from Serenity-UAV STL files.

Orthographic projections derived from 24-inch shell STLs in
thingverse-serenity/files-hollowed-18in/.

Coordinate system (confirmed from STL bounding-box analysis):
  X  =  fore–aft  (+X = nose / forward,  -X = tail / aft)
  Y  =  beam / lateral  (total 424mm span in 24″ scale)
  Z  =  height   (Z=0 = keel / ground,  Z_max≈182mm = top)

Full ship extent at 24″ scale (including pylon arms):
  X: -311 … +299 mm  (609.6 mm ≈ 24.00 in)
  Z:    0 … +182 mm  (7.17 in)
  Y: -415 …   +9 mm  (total beam including cargo bay depth)

Outputs:
  serenity/diagrams/hull_side.svg    — XZ side profile (nose right)
  serenity/diagrams/hull_top.svg     — XY top-down plan (nose right)
  serenity/diagrams/hull_front.svg   — YZ frontal view (from nose looking aft)
  serenity/diagrams/hull_bottom.svg  — XY bottom view (nose right)

These are standalone geometry references; the four overview_*.svg files
are updated separately using the paths extracted here.

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0  (hull geometry derived from Peter Farrell CC BY 4.0 model)
Source STLs: Thingiverse Serenity model scaled to 24 in, modified for
             50 mm EDF bores (Rev O).  See blender_shells_v3.py for scale math.
"""

import struct
import os
import math

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STL_DIR = (
    "/home/user/Serenity-UAV/thingverse-serenity/files-hollowed-18in"
)
OUT_DIR = "/home/user/Serenity-UAV/serenity/diagrams"

# Physical extents from STL analysis (mm, 24″ scale)
HULL_X_MIN = -311.0   # stern wing-tip
HULL_X_MAX =  299.0   # bow pylon-arm tip
HULL_Z_MIN =    0.0   # keel
HULL_Z_MAX =  182.0   # top of aft engine section
HULL_Y_MIN = -415.0   # bottom of cargo bay
HULL_Y_MAX =    9.0   # fuselage centreline (roughly)

# Annotation constants (Rev O specs)
HULL_LENGTH_MM = 609.6
HULL_HEIGHT_MM = 182.0
NACELLE_SPAN_MM = 486.0

# SVG canvas dimensions
SVG_SIDE_W  = 1200
SVG_SIDE_H  =  400
SVG_TOP_W   = 1200
SVG_TOP_H   =  600
SVG_FRONT_W =  800
SVG_FRONT_H =  500

MARGIN = 60   # px margin inside canvas

# Colour palette
C_HULL      = "#1a6ba0"   # main hull fill
C_HULL_STR  = "#0d3d5c"   # hull stroke
C_NACELLE   = "#c06010"   # nacelle / engine
C_WING      = "#2a7a3a"   # wing
C_CARGO     = "#6a3a8a"   # cargo section
C_GRID      = "#cccccc"   # dimension grid lines
C_DIM       = "#333333"   # dimension text
C_LABEL     = "#ffffff"   # label text on dark bg
C_BG        = "#f8f8f8"

FONT = "'OpenDyslexic', 'OpenDyslexicMono', sans-serif"

# ---------------------------------------------------------------------------
# STL reader
# ---------------------------------------------------------------------------

def read_stl_verts(fname):
    """
    Read all vertex coordinates from a binary STL file.
    Returns list of (x, y, z) tuples (each triangle → 3 vertices).
    """
    path = os.path.join(STL_DIR, fname)
    if not os.path.exists(path):
        print(f"  WARNING: {fname} not found – skipped")
        return []
    verts = []
    with open(path, "rb") as fh:
        fh.read(80)                                   # 80-byte header
        n_tri = struct.unpack("<I", fh.read(4))[0]
        for _ in range(n_tri):
            fh.read(12)                               # normal vector
            for _ in range(3):
                x, y, z = struct.unpack("<fff", fh.read(12))
                verts.append((x, y, z))
            fh.read(2)                                # attribute byte count
    return verts

# ---------------------------------------------------------------------------
# 2D silhouette (binned min/max along the primary axis)
# ---------------------------------------------------------------------------

def compute_silhouette(verts, h_axis, v_axis, n_bins=600):
    """
    For a list of (x,y,z) vertices, project to 2D using h_axis ('x','y','z')
    and v_axis, then return:
      h_vals  — n_bins equally-spaced horizontal positions
      v_top   — max vertical value at each bin  (upper silhouette)
      v_bot   — min vertical value at each bin  (lower silhouette)
    Bins with no data are linearly interpolated.
    """
    idx = {"x": 0, "y": 1, "z": 2}
    hi, vi = idx[h_axis], idx[v_axis]

    h_coords = [v[hi] for v in verts]
    v_coords = [v[vi] for v in verts]

    h_min, h_max = min(h_coords), max(h_coords)
    span = h_max - h_min
    if span == 0:
        return [], [], []

    top  = [None] * n_bins
    bot  = [None] * n_bins
    for hv, vv in zip(h_coords, v_coords):
        b = int((hv - h_min) / span * (n_bins - 1))
        b = max(0, min(n_bins - 1, b))
        if top[b] is None or vv > top[b]:
            top[b] = vv
        if bot[b] is None or vv < bot[b]:
            bot[b] = vv

    # Fill empty bins via linear interpolation
    def fill_gaps(arr, fallback):
        """Fill None entries by linear interp between neighbouring known values."""
        # Forward pass: carry last known value
        last = fallback
        for i in range(len(arr)):
            if arr[i] is None:
                arr[i] = last
            else:
                last = arr[i]
        # Backward pass: blend with next known
        last = fallback
        for i in range(len(arr) - 1, -1, -1):
            if arr[i] == last:
                pass
            else:
                last = arr[i]

    fill_gaps(top, 0.0)
    fill_gaps(bot, 0.0)

    h_vals = [h_min + i / (n_bins - 1) * span for i in range(n_bins)]
    return h_vals, top, bot

# ---------------------------------------------------------------------------
# SVG path builder (from silhouette data)
# ---------------------------------------------------------------------------

def silhouette_to_path(h_vals, v_top, v_bot,
                       h_range, v_range,
                       canvas_w, canvas_h,
                       margin,
                       flip_h=False, flip_v=True):
    """
    Convert silhouette data into a closed SVG <path d="..."> string.

    h_range = (h_min, h_max) in physical mm
    v_range = (v_min, v_max) in physical mm
    flip_h  = True  → reverse horizontal direction
    flip_v  = True  → flip vertical (SVG Y increases downward, Z increases upward)
    """
    h_min, h_max = h_range
    v_min, v_max = v_range

    w_px = canvas_w - 2 * margin
    h_px = canvas_h - 2 * margin

    def to_px(h_phys, v_phys):
        if flip_h:
            px = margin + (1.0 - (h_phys - h_min) / (h_max - h_min)) * w_px
        else:
            px = margin + (h_phys - h_min) / (h_max - h_min) * w_px
        if flip_v:
            py = margin + (1.0 - (v_phys - v_min) / (v_max - v_min)) * h_px
        else:
            py = margin + (v_phys - v_min) / (v_max - v_min) * h_px
        return px, py

    # Build upper outline (left to right)
    pts_top = [to_px(h, v) for h, v in zip(h_vals, v_top)]
    # Build lower outline (right to left for closed path)
    pts_bot = [to_px(h, v) for h, v in reversed(list(zip(h_vals, v_bot)))]

    pts = pts_top + pts_bot
    d = f"M {pts[0][0]:.1f},{pts[0][1]:.1f}"
    for px, py in pts[1:]:
        d += f" L {px:.1f},{py:.1f}"
    d += " Z"
    return d

# ---------------------------------------------------------------------------
# Generic SVG wrapper
# ---------------------------------------------------------------------------

def svg_open(w, h):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}">',
        '<defs>',
        f'  <style>',
        f'    @import url(\'https://fonts.cdnfonts.com/css/opendyslexic\');',
        f'    text, tspan {{ font-family: {FONT}; }}',
        f'  </style>',
        '</defs>',
        f'<rect width="{w}" height="{h}" fill="{C_BG}"/>',
    ]
    return lines

def svg_close():
    return ["</svg>"]

def write_svg(path, lines):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    sz = os.path.getsize(path)
    print(f"  → {os.path.basename(path)}  ({sz // 1024} KB)")

# ---------------------------------------------------------------------------
# Dimension line helper
# ---------------------------------------------------------------------------

def dim_line(x1, y1, x2, y2, label, offset=18, color=C_DIM, font_size=11):
    """Return SVG lines for a horizontal or vertical dimension annotation."""
    lines = []
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    lines.append(
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{color}" stroke-width="1" stroke-dasharray="4,3"/>'
    )
    lines.append(
        f'<text x="{mx:.1f}" y="{my - offset:.1f}" text-anchor="middle" '
        f'font-family="{FONT}" font-size="{font_size}" fill="{color}">'
        f'{label}</text>'
    )
    return lines

# ---------------------------------------------------------------------------
# Part definitions
# ---------------------------------------------------------------------------

FUSELAGE_PARTS = [
    "s_head_shell24.stl",
    "s_middle_shell24.stl",
    "s_rear_shell24.stl",
    "s_cargo_sect_shell24.stl",
]
WING_PARTS = ["s_wings_both_shell24.stl"]
NACELLE_PARTS = [
    "s_eng_left_shell24_50mm.stl",
    "s_eng_right_shell24_50mm.stl",
]
PIVOT_PARTS = [
    "s_pivot_arm_a_scaled24_50mm.stl",
    "s_eng_piv_outer_scaled24_50mm.stl",
    "s_eng_pistons_scaled24_50mm.stl",
]

# ---------------------------------------------------------------------------
# Load geometry
# ---------------------------------------------------------------------------

def load_group(file_list):
    verts = []
    for fname in file_list:
        verts.extend(read_stl_verts(fname))
    return verts

# ---------------------------------------------------------------------------
# Side view (XZ): nose right, keel at bottom
# ---------------------------------------------------------------------------

def build_side_view():
    print("Building side view (XZ)…")

    # Full hull + wings + pivots for complete silhouette
    fuse_verts   = load_group(FUSELAGE_PARTS)
    wing_verts   = load_group(WING_PARTS)
    nacelle_verts = load_group(NACELLE_PARTS)
    piv_verts    = load_group(PIVOT_PARTS)

    all_fuse = fuse_verts + wing_verts + piv_verts   # everything except nacelle pods

    # Physical extents for this view
    h_range = (HULL_X_MIN, HULL_X_MAX)   # X horizontal
    v_range = (HULL_Z_MIN, HULL_Z_MAX)   # Z vertical

    W, H, M = SVG_SIDE_W, SVG_SIDE_H, MARGIN

    def px(x_mm, z_mm):
        """Convert physical (X,Z) to SVG (px,py)."""
        px_ = M + (x_mm - HULL_X_MIN) / (HULL_X_MAX - HULL_X_MIN) * (W - 2 * M)
        py_ = M + (1.0 - (z_mm - HULL_Z_MIN) / (HULL_Z_MAX - HULL_Z_MIN)) * (H - 2 * M)
        return px_, py_

    # Compute silhouette paths
    hv_f, zt_f, zb_f = compute_silhouette(all_fuse, "x", "z", n_bins=800)
    path_fuse = silhouette_to_path(
        hv_f, zt_f, zb_f, h_range, v_range, W, H, M
    )

    hv_n, zt_n, zb_n = compute_silhouette(nacelle_verts, "x", "z", n_bins=400)
    path_nac = silhouette_to_path(
        hv_n, zt_n, zb_n, h_range, v_range, W, H, M
    )

    # SVG canvas
    lines = svg_open(W, H)

    # Title bar
    lines += [
        f'<rect x="0" y="0" width="{W}" height="36" fill="{C_HULL_STR}"/>',
        f'<text x="{W//2}" y="24" text-anchor="middle" font-family="{FONT}" '
        f'font-size="14" font-weight="bold" fill="{C_LABEL}">'
        f'SERENITY-CLASS TILTROTOR UAV — SIDE VIEW (STARBOARD)  |  '
        f'24.00" (609.6 mm)  Rev O</text>',
    ]

    # Ground reference line
    _, keel_py = px(HULL_X_MIN, HULL_Z_MIN)
    lines.append(
        f'<line x1="{M}" y1="{keel_py:.1f}" x2="{W-M}" y2="{keel_py:.1f}" '
        f'stroke="{C_GRID}" stroke-width="1" stroke-dasharray="6,4"/>'
    )

    # Fuselage silhouette
    lines.append(
        f'<path d="{path_fuse}" fill="{C_HULL}" fill-opacity="0.85" '
        f'stroke="{C_HULL_STR}" stroke-width="1.5"/>'
    )

    # Nacelle silhouette (vertical hover position from STL — shown as separate shape)
    lines.append(
        f'<path d="{path_nac}" fill="{C_NACELLE}" fill-opacity="0.70" '
        f'stroke="{C_NACELLE}" stroke-width="1.2"/>'
    )

    # -----------------------------------------------------------------------
    # Dimension annotations (Rev O spec values)
    # -----------------------------------------------------------------------

    # Overall hull length
    x1_px, z_base_py = px(HULL_X_MIN, HULL_Z_MIN - 12)
    x2_px, _         = px(HULL_X_MAX, HULL_Z_MIN - 12)
    lines += [
        f'<line x1="{x1_px:.1f}" y1="{z_base_py:.1f}" '
        f'x2="{x2_px:.1f}" y2="{z_base_py:.1f}" '
        f'stroke="{C_DIM}" stroke-width="1.5"/>',
        f'<line x1="{x1_px:.1f}" y1="{z_base_py-6:.1f}" '
        f'x2="{x1_px:.1f}" y2="{z_base_py+6:.1f}" stroke="{C_DIM}" stroke-width="1.5"/>',
        f'<line x1="{x2_px:.1f}" y1="{z_base_py-6:.1f}" '
        f'x2="{x2_px:.1f}" y2="{z_base_py+6:.1f}" stroke="{C_DIM}" stroke-width="1.5"/>',
        f'<text x="{(x1_px+x2_px)/2:.1f}" y="{z_base_py+18:.1f}" text-anchor="middle" '
        f'font-family="{FONT}" font-size="11" fill="{C_DIM}">'
        f'609.6 mm (24.00 in)</text>',
    ]

    # Height dimension
    x_ht_px, _ = px(HULL_X_MIN - 10, 0)
    _, z_top_py = px(0, HULL_Z_MAX)
    _, z_bot_py = px(0, HULL_Z_MIN)
    lines += [
        f'<line x1="{x_ht_px:.1f}" y1="{z_top_py:.1f}" '
        f'x2="{x_ht_px:.1f}" y2="{z_bot_py:.1f}" stroke="{C_DIM}" stroke-width="1.5"/>',
        f'<text x="{x_ht_px-4:.1f}" y="{(z_top_py+z_bot_py)/2:.1f}" '
        f'text-anchor="middle" dominant-baseline="middle" '
        f'font-family="{FONT}" font-size="10" fill="{C_DIM}" '
        f'transform="rotate(-90,{x_ht_px-4:.1f},{(z_top_py+z_bot_py)/2:.1f})">'
        f'182 mm (7.17 in)</text>',
    ]

    # Station labels — access panels A–F
    STATIONS = [
        (  0.0, -311, "STERN"),   # X = keel ref
        ( 91.0, -311+91, "STA B"),
        (165.0, -311+165, "STA C"),
        (251.0, -311+251, "STA D"),
        (320.0, -311+320, "STA E"),
        (388.0, -311+388, "STA F"),
    ]
    # Stations are measured from the stern; convert to STL X
    # Stern is at X = HULL_X_MIN = -311mm
    # Station 0 = stern, station 609.6 = nose
    for sta_mm, _, lbl in STATIONS:
        stl_x = HULL_X_MIN + sta_mm
        spx, _ = px(stl_x, HULL_Z_MIN)
        _, spy = px(stl_x, HULL_Z_MIN)
        _, spy2 = px(stl_x, HULL_Z_MAX * 0.1)
        lines.append(
            f'<line x1="{spx:.1f}" y1="{spy:.1f}" x2="{spx:.1f}" y2="{spy2:.1f}" '
            f'stroke="{C_GRID}" stroke-width="0.8" stroke-dasharray="3,3"/>'
        )

    # Key feature labels
    def label(x_mm, z_mm, text, anchor="middle", dy=0, font_size=9):
        lx, ly = px(x_mm, z_mm)
        return (
            f'<text x="{lx:.1f}" y="{ly+dy:.1f}" text-anchor="{anchor}" '
            f'font-family="{FONT}" font-size="{font_size}" fill="{C_DIM}">'
            f'{text}</text>'
        )

    # CG marker at 203mm from nose → X = HULL_X_MAX - 203 = +96mm
    cg_x = HULL_X_MAX - 203.0
    cg_px, cg_py = px(cg_x, HULL_Z_MIN + 15)
    lines += [
        f'<line x1="{cg_px:.1f}" y1="{cg_py-20:.1f}" x2="{cg_px:.1f}" '
        f'y2="{cg_py+20:.1f}" stroke="#e00000" stroke-width="1.5"/>',
        f'<text x="{cg_px:.1f}" y="{cg_py+34:.1f}" text-anchor="middle" '
        f'font-family="{FONT}" font-size="9" fill="#e00000">CG 203 mm</text>',
    ]

    # GPS label at sta 140mm from nose (dorsal)
    gps_x = HULL_X_MAX - 140.0
    gps_px, gps_py = px(gps_x, HULL_Z_MAX * 0.85)
    lines.append(
        f'<text x="{gps_px:.1f}" y="{gps_py:.1f}" text-anchor="middle" '
        f'font-family="{FONT}" font-size="9" fill="{C_DIM}">GPS sta 140</text>'
    )

    # 120 mm rear EDF label
    rear_x = HULL_X_MIN + 60.0
    rear_px, rear_py = px(rear_x, HULL_Z_MAX * 0.5)
    lines.append(
        f'<text x="{rear_px:.1f}" y="{rear_py:.1f}" text-anchor="middle" '
        f'font-family="{FONT}" font-size="9" fill="{C_LABEL}">120 mm EDF</text>'
    )

    # 50 mm nacelle label
    nac_x  = HULL_X_MAX - 230.0   # approx nacelle fore-aft centroid in STL X coords
    nac_px, nac_py = px(nac_x, HULL_Z_MAX * 0.6)
    lines.append(
        f'<text x="{nac_px:.1f}" y="{nac_py:.1f}" text-anchor="middle" '
        f'font-family="{FONT}" font-size="9" fill="{C_NACELLE}">50 mm×2 EDF</text>'
    )

    # Legend
    legend_x, legend_y = W - M - 180, M + 10
    legend_items = [
        (C_HULL,    "Fuselage hull (CF-PETG)"),
        (C_NACELLE, "Nacelles (50 mm×2 tandem EDF)"),
    ]
    for i, (col, txt) in enumerate(legend_items):
        lx = legend_x
        ly = legend_y + i * 18
        lines += [
            f'<rect x="{lx}" y="{ly}" width="12" height="10" fill="{col}" '
            f'fill-opacity="0.8" stroke="{col}" stroke-width="1"/>',
            f'<text x="{lx+16}" y="{ly+9}" font-family="{FONT}" '
            f'font-size="9" fill="{C_DIM}">{txt}</text>',
        ]

    lines += svg_close()
    write_svg(os.path.join(OUT_DIR, "hull_side.svg"), lines)

# ---------------------------------------------------------------------------
# Top view (XY): nose right, port at top
# ---------------------------------------------------------------------------

def build_top_view():
    print("Building top view (XY)…")

    fuse_verts    = load_group(FUSELAGE_PARTS)
    wing_verts    = load_group(WING_PARTS)
    nacelle_verts = load_group(NACELLE_PARTS)

    all_hull = fuse_verts + wing_verts

    # For top view: Y is the beam axis; nose to right (X), port to top
    h_range = (HULL_X_MIN, HULL_X_MAX)
    v_range = (HULL_Y_MIN, HULL_Y_MAX)

    W, H, M = SVG_TOP_W, SVG_TOP_H, MARGIN

    def px(x_mm, y_mm):
        px_ = M + (x_mm - HULL_X_MIN) / (HULL_X_MAX - HULL_X_MIN) * (W - 2 * M)
        # Y axis: higher Y (less negative) = starboard = bottom of canvas
        py_ = M + (y_mm - HULL_Y_MIN) / (HULL_Y_MAX - HULL_Y_MIN) * (H - 2 * M)
        return px_, py_

    # Full-hull top silhouette
    hv_h, yt_h, yb_h = compute_silhouette(all_hull, "x", "y", n_bins=800)
    path_hull = silhouette_to_path(
        hv_h, yt_h, yb_h, h_range, v_range, W, H, M, flip_v=False
    )

    # Nacelle top silhouette (shows as oval for vertical nacelles)
    hv_n, yt_n, yb_n = compute_silhouette(nacelle_verts, "x", "y", n_bins=400)
    path_nac = silhouette_to_path(
        hv_n, yt_n, yb_n, h_range, v_range, W, H, M, flip_v=False
    )

    lines = svg_open(W, H)
    lines += [
        f'<rect x="0" y="0" width="{W}" height="36" fill="{C_HULL_STR}"/>',
        f'<text x="{W//2}" y="24" text-anchor="middle" font-family="{FONT}" '
        f'font-size="14" font-weight="bold" fill="{C_LABEL}">'
        f'SERENITY-CLASS TILTROTOR UAV — TOP / PLAN VIEW  |  '
        f'24.00" (609.6 mm)  Rev O</text>',
    ]

    # Centreline
    _, cl_py = px(0, (HULL_Y_MIN + HULL_Y_MAX) / 2)
    # Use actual fuselage Y centroid ≈ -73.6mm for centreline
    cl_x_px, cl_py2 = px(0, -73.6)
    lines.append(
        f'<line x1="{M}" y1="{cl_py2:.1f}" x2="{W-M}" y2="{cl_py2:.1f}" '
        f'stroke="{C_GRID}" stroke-width="0.8" stroke-dasharray="8,4"/>'
    )

    # Hull fill
    lines.append(
        f'<path d="{path_hull}" fill="{C_HULL}" fill-opacity="0.80" '
        f'stroke="{C_HULL_STR}" stroke-width="1.5"/>'
    )

    # Nacelle ovals
    lines.append(
        f'<path d="{path_nac}" fill="{C_NACELLE}" fill-opacity="0.65" '
        f'stroke="{C_NACELLE}" stroke-width="1.2"/>'
    )

    # Span dimension — from Y_MIN to Y_MAX, annotated
    # Nacelle tip-to-tip approximate
    xmid_px, _ = px(0, 0)
    nt_py1 = M + 4
    nt_py2 = H - M - 4
    lines += [
        f'<line x1="{M+20}" y1="{nt_py1}" x2="{M+20}" y2="{nt_py2}" '
        f'stroke="{C_DIM}" stroke-width="1"/>',
        f'<text x="{M+30}" y="{(nt_py1+nt_py2)//2}" dominant-baseline="middle" '
        f'font-family="{FONT}" font-size="10" fill="{C_DIM}" '
        f'transform="rotate(-90,{M+30},{(nt_py1+nt_py2)//2})">'
        f'~486 mm tip-to-tip</text>',
    ]

    # Hull length bar
    x1_px, _ = px(HULL_X_MIN, HULL_Y_MIN)
    x2_px, _ = px(HULL_X_MAX, HULL_Y_MIN)
    bar_y = H - M + 20
    lines += [
        f'<line x1="{x1_px:.1f}" y1="{bar_y}" x2="{x2_px:.1f}" y2="{bar_y}" '
        f'stroke="{C_DIM}" stroke-width="1.5"/>',
        f'<text x="{(x1_px+x2_px)/2:.1f}" y="{bar_y+14}" text-anchor="middle" '
        f'font-family="{FONT}" font-size="11" fill="{C_DIM}">609.6 mm (24.00 in)</text>',
    ]

    # CG line
    cg_x = HULL_X_MAX - 203.0
    cg_px2, _ = px(cg_x, 0)
    lines.append(
        f'<line x1="{cg_px2:.1f}" y1="{M}" x2="{cg_px2:.1f}" y2="{H-M}" '
        f'stroke="#e00000" stroke-width="1" stroke-dasharray="5,3"/>'
    )
    lines.append(
        f'<text x="{cg_px2+4:.1f}" y="{M+20}" font-family="{FONT}" '
        f'font-size="9" fill="#e00000">CG</text>'
    )

    # North arrow / forward direction label
    lines.append(
        f'<text x="{W-M-5}" y="{M+18}" text-anchor="end" font-family="{FONT}" '
        f'font-size="11" font-weight="bold" fill="{C_DIM}">▶ NOSE</text>'
    )

    lines += svg_close()
    write_svg(os.path.join(OUT_DIR, "hull_top.svg"), lines)

# ---------------------------------------------------------------------------
# Front view (YZ): looking from nose back → port left, starboard right
# ---------------------------------------------------------------------------

def build_front_view():
    print("Building front view (YZ)…")

    fuse_verts    = load_group(FUSELAGE_PARTS)
    nacelle_verts = load_group(NACELLE_PARTS)

    # For the frontal view, only include the FORWARD half of the hull
    # (X > 0 = forward of midship) to avoid the tail masking the front profile
    forward_fuse = [(x, y, z) for x, y, z in fuse_verts if x > -50]
    forward_nac  = [(x, y, z) for x, y, z in nacelle_verts if x > -50]

    h_range = (HULL_Y_MIN, HULL_Y_MAX)
    v_range = (HULL_Z_MIN, HULL_Z_MAX)

    W, H, M = SVG_FRONT_W, SVG_FRONT_H, MARGIN

    def px(y_mm, z_mm):
        # Port is positive Y → left of view; so flip horizontal
        px_ = M + (1.0 - (y_mm - HULL_Y_MIN) / (HULL_Y_MAX - HULL_Y_MIN)) * (W - 2 * M)
        py_ = M + (1.0 - (z_mm - HULL_Z_MIN) / (HULL_Z_MAX - HULL_Z_MIN)) * (H - 2 * M)
        return px_, py_

    # Full YZ silhouette
    hv_f, zt_f, zb_f = compute_silhouette(forward_fuse + forward_nac, "y", "z", n_bins=600)
    path_full = silhouette_to_path(
        hv_f, zt_f, zb_f, h_range, v_range, W, H, M, flip_h=True
    )

    # Nacelle-only
    hv_n, zt_n, zb_n = compute_silhouette(forward_nac, "y", "z", n_bins=600)
    path_nac  = silhouette_to_path(
        hv_n, zt_n, zb_n, h_range, v_range, W, H, M, flip_h=True
    )

    lines = svg_open(W, H)
    lines += [
        f'<rect x="0" y="0" width="{W}" height="36" fill="{C_HULL_STR}"/>',
        f'<text x="{W//2}" y="24" text-anchor="middle" font-family="{FONT}" '
        f'font-size="14" font-weight="bold" fill="{C_LABEL}">'
        f'SERENITY-CLASS TILTROTOR UAV — FRONT VIEW (FROM NOSE)  |  Rev O</text>',
    ]

    lines.append(
        f'<path d="{path_full}" fill="{C_HULL}" fill-opacity="0.80" '
        f'stroke="{C_HULL_STR}" stroke-width="1.5"/>'
    )
    lines.append(
        f'<path d="{path_nac}" fill="{C_NACELLE}" fill-opacity="0.65" '
        f'stroke="{C_NACELLE}" stroke-width="1.2"/>'
    )

    # Port / Starboard labels
    lines += [
        f'<text x="{M+10}" y="{H//2}" text-anchor="start" dominant-baseline="middle" '
        f'font-family="{FONT}" font-size="11" fill="{C_DIM}">PORT</text>',
        f'<text x="{W-M-10}" y="{H//2}" text-anchor="end" dominant-baseline="middle" '
        f'font-family="{FONT}" font-size="11" fill="{C_DIM}">STBD</text>',
    ]

    # Keel line
    _, keel_py = px(0, HULL_Z_MIN)
    lines.append(
        f'<line x1="{M}" y1="{keel_py:.1f}" x2="{W-M}" y2="{keel_py:.1f}" '
        f'stroke="{C_GRID}" stroke-width="0.8" stroke-dasharray="6,4"/>'
    )

    lines += svg_close()
    write_svg(os.path.join(OUT_DIR, "hull_front.svg"), lines)

# ---------------------------------------------------------------------------
# Bottom view (XY): nose right, keel up
# ---------------------------------------------------------------------------

def build_bottom_view():
    print("Building bottom view (XY)…")

    fuse_verts    = load_group(FUSELAGE_PARTS)
    wing_verts    = load_group(WING_PARTS)
    nacelle_verts = load_group(NACELLE_PARTS)

    all_hull = fuse_verts + wing_verts + nacelle_verts

    h_range = (HULL_X_MIN, HULL_X_MAX)
    v_range = (HULL_Y_MIN, HULL_Y_MAX)

    W, H, M = SVG_TOP_W, SVG_TOP_H, MARGIN

    def px(x_mm, y_mm):
        px_ = M + (x_mm - HULL_X_MIN) / (HULL_X_MAX - HULL_X_MIN) * (W - 2 * M)
        # For bottom view, more negative Y = further below = lower on canvas
        py_ = M + (1.0 - (y_mm - HULL_Y_MIN) / (HULL_Y_MAX - HULL_Y_MIN)) * (H - 2 * M)
        return px_, py_

    hv_h, yt_h, yb_h = compute_silhouette(all_hull, "x", "y", n_bins=800)
    path_hull = silhouette_to_path(
        hv_h, yt_h, yb_h, h_range, v_range, W, H, M, flip_v=True
    )

    lines = svg_open(W, H)
    lines += [
        f'<rect x="0" y="0" width="{W}" height="36" fill="{C_HULL_STR}"/>',
        f'<text x="{W//2}" y="24" text-anchor="middle" font-family="{FONT}" '
        f'font-size="14" font-weight="bold" fill="{C_LABEL}">'
        f'SERENITY-CLASS TILTROTOR UAV — BOTTOM VIEW  |  Rev O</text>',
    ]

    lines.append(
        f'<path d="{path_hull}" fill="{C_HULL}" fill-opacity="0.80" '
        f'stroke="{C_HULL_STR}" stroke-width="1.5"/>'
    )

    # Antenna / payload bay annotation
    # SiK belly port at sta 260 from nose → X = HULL_X_MAX - 260 = +39mm
    sik_x = HULL_X_MAX - 260.0
    sik_px, sik_py = px(sik_x, -90)   # approximate belly Y
    lines.append(
        f'<text x="{sik_px:.1f}" y="{sik_py:.1f}" text-anchor="middle" '
        f'font-family="{FONT}" font-size="9" fill="{C_LABEL}">SiK 915 sta 260</text>'
    )

    # Hull length bar
    x1_px, _ = px(HULL_X_MIN, HULL_Y_MIN)
    x2_px, _ = px(HULL_X_MAX, HULL_Y_MIN)
    bar_y = H - 20
    lines += [
        f'<line x1="{x1_px:.1f}" y1="{bar_y}" x2="{x2_px:.1f}" y2="{bar_y}" '
        f'stroke="{C_DIM}" stroke-width="1.5"/>',
        f'<text x="{(x1_px+x2_px)/2:.1f}" y="{bar_y+14}" text-anchor="middle" '
        f'font-family="{FONT}" font-size="11" fill="{C_DIM}">609.6 mm (24.00 in)</text>',
    ]

    lines += svg_close()
    write_svg(os.path.join(OUT_DIR, "hull_bottom.svg"), lines)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Serenity-UAV hull outline generator — Rev O")
    print(f"STL source:  {STL_DIR}")
    print(f"SVG output:  {OUT_DIR}")
    print()

    build_side_view()
    build_top_view()
    build_front_view()
    build_bottom_view()

    print()
    print("Done.  Review hull_side.svg / hull_top.svg / hull_front.svg / hull_bottom.svg")
    print("before embedding paths in overview_*.svg files.")
