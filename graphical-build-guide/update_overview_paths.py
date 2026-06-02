#!/usr/bin/env python3
"""
update_overview_paths.py — Replace hand-drawn hull polygons in the four
overview_*.svg files with accurate silhouettes derived from the STL geometry.

Coordinate system (confirmed from STL bounding-box analysis):
  X  = fore–aft  (+X = nose / forward, –X = tail / aft)
  Z  = height    (Z=0 = keel, Z_max ≈ 182 mm = top of aft section)
  Y  = beam/lateral  (total span ~424 mm in the 24″ model)

Full assembly extents (all 24″ hull shells combined):
  X: –311 … +299 mm   (609.6 mm fuselage + pylon arm tips)
  Z:    0 … +182 mm
  Y: –415 …   +9 mm

The four overview SVGs already carry all annotations; this script ONLY replaces
the hull shape polygon/path elements, leaving every other SVG element intact.

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0
"""

import struct
import os
import re

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

STL_DIR = "/home/user/Serenity-UAV/thingverse-serenity/files-hollowed-18in"
SVG_DIR = "/home/user/Serenity-UAV/serenity/diagrams"

HULL_PARTS = [
    "s_head_shell24.stl",
    "s_middle_shell24.stl",
    "s_rear_shell24.stl",
    "s_cargo_sect_shell24.stl",
    "s_wings_both_shell24.stl",
    "s_pivot_arm_a_scaled24.stl",
    "s_eng_piv_outer_scaled24.stl",
]

NACELLE_PARTS = [
    "s_eng_left_shell24_50mm.stl",
    "s_eng_right_shell24_50mm.stl",
]

# ---------------------------------------------------------------------------
# STL reader
# ---------------------------------------------------------------------------

def read_stl_verts(fname):
    """Return list of (x,y,z) tuples for all triangle vertices in fname."""
    path = os.path.join(STL_DIR, fname)
    if not os.path.exists(path):
        print(f"  WARNING: {fname} not found")
        return []
    verts = []
    with open(path, "rb") as fh:
        fh.read(80)
        n = struct.unpack("<I", fh.read(4))[0]
        for _ in range(n):
            fh.read(12)
            for _ in range(3):
                x, y, z = struct.unpack("<fff", fh.read(12))
                verts.append((x, y, z))
            fh.read(2)
    return verts

def load_group(file_list):
    verts = []
    for f in file_list:
        verts.extend(read_stl_verts(f))
    return verts

# ---------------------------------------------------------------------------
# 2D silhouette computation
# ---------------------------------------------------------------------------

def silhouette(verts, h_axis, v_axis, n_bins=600):
    """
    Project verts onto 2D and compute min/max v at each h bin.

    Returns:
      h_vals  — list of n_bins physical h-axis positions
      v_top   — list of n_bins max-v values (upper outline)
      v_bot   — list of n_bins min-v values (lower outline)
    """
    AXIS = {"x": 0, "y": 1, "z": 2}
    hi, vi = AXIS[h_axis], AXIS[v_axis]

    hv = [p[hi] for p in verts]
    vv = [p[vi] for p in verts]

    h0, h1 = min(hv), max(hv)
    if h1 == h0:
        return [], [], []

    top = [None] * n_bins
    bot = [None] * n_bins
    inv = (n_bins - 1) / (h1 - h0)
    for h, v in zip(hv, vv):
        b = int((h - h0) * inv)
        b = max(0, min(n_bins - 1, b))
        if top[b] is None or v > top[b]:
            top[b] = v
        if bot[b] is None or v < bot[b]:
            bot[b] = v

    # Fill gaps: forward then backward propagation
    last_t = vv[0]; last_b = vv[0]
    for i in range(n_bins):
        if top[i] is None: top[i] = last_t
        else: last_t = top[i]
        if bot[i] is None: bot[i] = last_b
        else: last_b = bot[i]
    last_t = vv[-1]; last_b = vv[-1]
    for i in range(n_bins - 1, -1, -1):
        if top[i] is not None: last_t = top[i]
        else: top[i] = last_t
        if bot[i] is not None: last_b = bot[i]
        else: bot[i] = last_b

    h_vals = [h0 + i / (n_bins - 1) * (h1 - h0) for i in range(n_bins)]
    return h_vals, top, bot

# ---------------------------------------------------------------------------
# SVG path builder
# ---------------------------------------------------------------------------

def to_svg_path(h_vals, v_top, v_bot,
                stl_h_range, stl_v_range,
                svg_h_range, svg_v_range,
                flip_h=False, flip_v=True,
                simplify_dp=1.5):
    """
    Convert silhouette arrays to a closed SVG <path d="…"> string.

    stl_h_range / stl_v_range  — (min, max) of the physical STL coordinates used
    svg_h_range / svg_v_range  — (min, max) of the SVG pixel coordinates to fill
    flip_h / flip_v            — reverse direction along each axis
    simplify_dp                — Douglas-Peucker epsilon in pixels (0 = no simplify)
    """
    sh0, sh1 = stl_h_range
    sv0, sv1 = stl_v_range
    dh_stl = sh1 - sh0
    dv_stl = sv1 - sv0
    pxh0, pxh1 = svg_h_range
    pxv0, pxv1 = svg_v_range
    dpxh = pxh1 - pxh0
    dpxv = pxv1 - pxv0

    def conv(h_phys, v_phys):
        """Physical STL coords → SVG pixel coords."""
        th = (h_phys - sh0) / dh_stl   # 0..1 along h axis
        tv = (v_phys - sv0) / dv_stl   # 0..1 along v axis
        if flip_h:
            th = 1.0 - th
        if flip_v:
            tv = 1.0 - tv
        px = pxh0 + th * dpxh
        py = pxv0 + tv * dpxv
        return px, py

    # Build point list (upper outline L→R, then lower R→L)
    upper = [conv(h, vt) for h, vt in zip(h_vals, v_top)]
    lower = [conv(h, vb) for h, vb in reversed(list(zip(h_vals, v_bot)))]
    pts = upper + lower

    if simplify_dp > 0:
        pts = _dp_simplify(pts, simplify_dp)

    d = f"M {pts[0][0]:.1f},{pts[0][1]:.1f}"
    for x, y in pts[1:]:
        d += f" L {x:.1f},{y:.1f}"
    d += " Z"
    return d

def _dp_simplify(pts, eps):
    """Douglas-Peucker polyline simplification."""
    if len(pts) <= 2:
        return pts

    def perp_dist(p, a, b):
        ax, ay = a; bx, by = b; px, py = p
        dx, dy = bx - ax, by - ay
        denom = (dx * dx + dy * dy) ** 0.5
        if denom == 0:
            return ((px - ax)**2 + (py - ay)**2) ** 0.5
        return abs(dy * px - dx * py + bx * ay - by * ax) / denom

    def rdp(pts, eps):
        if len(pts) < 3:
            return list(pts)
        dmax = 0
        idx = 0
        for i in range(1, len(pts) - 1):
            d = perp_dist(pts[i], pts[0], pts[-1])
            if d > dmax:
                dmax = d; idx = i
        if dmax >= eps:
            left  = rdp(pts[:idx + 1], eps)
            right = rdp(pts[idx:], eps)
            return left[:-1] + right
        return [pts[0], pts[-1]]

    return rdp(pts, eps)

# ---------------------------------------------------------------------------
# SVG file update helpers
# ---------------------------------------------------------------------------

def read_svg(fname):
    with open(fname, "r", encoding="utf-8") as f:
        return f.read()

def write_svg(fname, content):
    with open(fname, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  → {os.path.basename(fname)}  ({os.path.getsize(fname)//1024} KB)")

def replace_element(svg_text, pattern, new_element):
    """
    Replace the first SVG element that matches a regex pattern with new_element.
    Returns (new_text, was_replaced).
    """
    m = re.search(pattern, svg_text, re.DOTALL)
    if m:
        return svg_text[:m.start()] + new_element + svg_text[m.end():], True
    return svg_text, False

# ---------------------------------------------------------------------------
# Process overview_side.svg
# ---------------------------------------------------------------------------

def update_side_view():
    """
    Replace the main hull polygon in overview_side.svg with an STL-derived
    silhouette, maintaining the same coordinate system and styling.

    overview_side.svg coordinate system:
      Nose at LEFT (x = 72),  tail at RIGHT (x = 666)
      Keel at BOTTOM (y = 302), bridge-top at TOP (y = 110)
      Physical scale: 594 px / 609.6 mm = 0.975 px/mm
    """
    print("\nUpdating overview_side.svg…")
    fname = os.path.join(SVG_DIR, "overview_side.svg")
    svg = read_svg(fname)

    # STL physical extents for the side view
    STL_X_MIN, STL_X_MAX = -311.0, 299.0   # fore–aft
    STL_Z_MIN, STL_Z_MAX =    0.0, 182.0   # height

    # SVG pixel extents (from polygon analysis of existing file)
    SVG_X_NOSE  =  72.0    # nose at LEFT
    SVG_X_TAIL  = 666.0    # tail at RIGHT
    SVG_Y_KEEL  = 302.0    # keel at BOTTOM
    SVG_Y_TOP   = 110.0    # bridge top at TOP

    hull_verts = load_group(HULL_PARTS)
    print(f"  Hull verts: {len(hull_verts):,}")

    # Compute XZ silhouette (fuselage side profile)
    h_vals, z_top, z_bot = silhouette(hull_verts, "x", "z", n_bins=600)

    hull_path = to_svg_path(
        h_vals, z_top, z_bot,
        stl_h_range=(STL_X_MIN, STL_X_MAX),
        stl_v_range=(STL_Z_MIN, STL_Z_MAX),
        svg_h_range=(SVG_X_NOSE, SVG_X_TAIL),
        svg_v_range=(SVG_Y_TOP,  SVG_Y_KEEL),
        flip_h=True,    # STL +X = nose; flip so nose stays at SVG LEFT (x=72)
        flip_v=True,    # STL Z=0=keel must map to SVG y=302 (bottom); flip needed
        simplify_dp=0.5,
    )

    # Build replacement path element (preserving existing fill/stroke)
    new_hull = (
        f'<path id="hull-side-stl" d="{hull_path}" '
        f'fill="#0e2030" stroke="#00e5ff" stroke-width="2.5"/>'
    )

    # The existing polygon starts with: M 72.0,205.5 L ...
    # Match the path/polygon that forms the main hull outline
    old_pattern = (
        r'<path d="M 72\.0,205\.5.*?Z"[^/]*/>'
    )
    svg, replaced = replace_element(svg, old_pattern, new_hull)
    if not replaced:
        # Try polygon fallback
        old_poly = (
            r'<path[^>]+d="M [0-9].*?fill="#0e2030" stroke="#00e5ff"[^/]*/>'
        )
        svg, replaced = replace_element(svg, old_poly, new_hull)

    if replaced:
        print("  Hull polygon replaced ✓")
    else:
        # Append the new hull BEFORE the first annotation element
        # (insert after the grid rect)
        svg = svg.replace(
            '<rect width="820" height="420" fill="url(#grid)"/>',
            '<rect width="820" height="420" fill="url(#grid)"/>\n' + new_hull,
        )
        print("  Hull polygon INSERTED (original not matched — both now present)")

    write_svg(fname, svg)

# ---------------------------------------------------------------------------
# Process overview_top.svg
# ---------------------------------------------------------------------------

def update_top_view():
    """
    Replace the main hull polygon in overview_top.svg with an STL-derived
    top-view (XY) silhouette.

    overview_top.svg coordinate system:
      Nose at LEFT (x = 110),  tail at RIGHT (x = 681.5)
      Fuselage Y-centre at y ≈ 230.0
      The Y-axis maps STL-Y with fuselage centroid (≈ –73.6 mm) → y=230

    The existing polygon spans y=178..281 (≈ 103 px for ~110 mm hull width).
    Scale: 103 px / 110 mm ≈ 0.936 px/mm (beam axis)
           571.5 px / 609.6 mm ≈ 0.937 px/mm (length axis)  — nearly isometric
    """
    print("\nUpdating overview_top.svg…")
    fname = os.path.join(SVG_DIR, "overview_top.svg")
    svg = read_svg(fname)

    # STL extents used for the top-view mapping
    STL_X_MIN, STL_X_MAX = -311.0, 299.0

    # The fuselage top-view Y extent:
    # Middle section spans Y: –156 … +9 (centroid ≈ –73.6)
    # Use a slightly wider range to capture head and rear sections:
    STL_Y_MIN  = -160.0   # port-most fuselage edge visible from above
    STL_Y_MAX  =   15.0   # starboard-most

    # SVG extents
    SVG_X_NOSE  = 110.0
    SVG_X_TAIL  = 681.5
    SVG_Y_PORT  = 178.6   # top of polygon (port side at top of diagram)
    SVG_Y_STBD  = 281.4   # bottom of polygon (starboard side at bottom)

    hull_verts = load_group(HULL_PARTS)

    # Filter to only verts within the fuselage Y band (exclude deep cargo bay)
    fuse_verts = [(x, y, z) for x, y, z in hull_verts if STL_Y_MIN <= y <= STL_Y_MAX]
    print(f"  Fuselage (Y-filtered) verts: {len(fuse_verts):,}")

    h_vals, y_top, y_bot = silhouette(fuse_verts, "x", "y", n_bins=600)

    # In the top view, "y_top" = max Y (most positive = starboard = SVG bottom)
    # and "y_bot" = min Y (most negative = port = SVG top)
    # SVG_Y_PORT is the visual top → maps to STL_Y_MIN (most negative Y)
    # SVG_Y_STBD is the visual bottom → maps to STL_Y_MAX (most positive Y)
    hull_path = to_svg_path(
        h_vals, y_top, y_bot,
        stl_h_range=(STL_X_MIN, STL_X_MAX),
        stl_v_range=(STL_Y_MIN, STL_Y_MAX),
        svg_h_range=(SVG_X_NOSE, SVG_X_TAIL),
        svg_v_range=(SVG_Y_PORT,  SVG_Y_STBD),
        flip_h=True,    # +X = nose = SVG LEFT
        flip_v=False,   # STL Y: more positive → SVG bottom → no flip needed when using top/bot
        simplify_dp=0.5,
    )

    new_hull = (
        f'<path id="hull-top-stl" d="{hull_path}" '
        f'fill="#0e2030" stroke="#00e5ff" stroke-width="2.5"/>'
    )

    # Match the main hull polygon in overview_top.svg
    old_pattern = (
        r'<path d="M 110\.0,230\.0.*?Z" fill="#0e2030" stroke="#00e5ff"[^/]*/>'
    )
    svg, replaced = replace_element(svg, old_pattern, new_hull)

    if replaced:
        print("  Hull polygon replaced ✓")
    else:
        svg = svg.replace(
            '<rect width="820" height="460" fill="url(#grid)"/>',
            '<rect width="820" height="460" fill="url(#grid)"/>\n' + new_hull,
        )
        print("  Hull polygon INSERTED (original not matched — both now present)")

    write_svg(fname, svg)

# ---------------------------------------------------------------------------
# Process overview_front.svg
# ---------------------------------------------------------------------------

def update_front_view():
    """
    Replace/add hull outline in overview_front.svg.
    Front view: YZ plane (Y = beam horizontal, Z = height vertical).
    """
    print("\nUpdating overview_front.svg…")
    fname = os.path.join(SVG_DIR, "overview_front.svg")
    svg = read_svg(fname)

    # Verify the file exists
    if not os.path.exists(fname):
        print("  overview_front.svg not found — skipping")
        return

    # Load existing SVG to find canvas dimensions
    m = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
    if m:
        canvas_w, canvas_h = int(m.group(1)), int(m.group(2))
    else:
        canvas_w, canvas_h = 820, 420

    # STL extents for front view (looking from nose, along -X direction)
    # Show only the forward half for a cleaner profile
    STL_Y_MIN, STL_Y_MAX = -415.0,  9.0   # full Y span
    STL_Z_MIN, STL_Z_MAX =    0.0, 182.0

    # SVG layout: centred
    MARGIN = 60
    SVG_Y_LEFT  = MARGIN
    SVG_Y_RIGHT = canvas_w - MARGIN
    SVG_Z_TOP   = MARGIN + 20
    SVG_Z_BOT   = canvas_h - MARGIN - 30

    hull_verts = load_group(HULL_PARTS)
    # Take only verts in the forward half (nose region)
    fwd_verts = [(x, y, z) for x, y, z in hull_verts if x > -100]

    h_vals, z_top, z_bot = silhouette(fwd_verts, "y", "z", n_bins=400)

    hull_path = to_svg_path(
        h_vals, z_top, z_bot,
        stl_h_range=(STL_Y_MIN, STL_Y_MAX),
        stl_v_range=(STL_Z_MIN, STL_Z_MAX),
        svg_h_range=(SVG_Y_RIGHT, SVG_Y_LEFT),   # flip H: port left in view
        svg_v_range=(SVG_Z_BOT, SVG_Z_TOP),
        flip_h=False,
        flip_v=False,
        simplify_dp=0.5,
    )

    new_hull = (
        f'<path id="hull-front-stl" d="{hull_path}" '
        f'fill="#0e2030" fill-opacity="0.85" stroke="#00e5ff" stroke-width="2"/>'
    )

    # Try to replace existing hull path
    old_pattern = r'<path[^>]+id="hull-front[^>]*/>'
    svg, replaced = replace_element(svg, old_pattern, new_hull)
    if not replaced:
        # Insert after background rects
        insert_after = re.search(
            r'<rect[^>]+fill="url\(#grid\)"[^/]*/>', svg
        )
        if insert_after:
            svg = (svg[:insert_after.end()] + "\n" + new_hull +
                   svg[insert_after.end():])
            print("  Hull path inserted ✓")
        else:
            print("  WARNING: Could not find insertion point")
            return

    if replaced:
        print("  Hull path replaced ✓")

    write_svg(fname, svg)

# ---------------------------------------------------------------------------
# Process overview_bottom.svg
# ---------------------------------------------------------------------------

def update_bottom_view():
    """
    Replace/add hull outline in overview_bottom.svg.
    Bottom view: XY plane (X = fore–aft, Y = beam) looking upward.
    """
    print("\nUpdating overview_bottom.svg…")
    fname = os.path.join(SVG_DIR, "overview_bottom.svg")
    svg = read_svg(fname)

    if not os.path.exists(fname):
        print("  overview_bottom.svg not found — skipping")
        return

    m = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
    if m:
        canvas_w, canvas_h = int(m.group(1)), int(m.group(2))
    else:
        canvas_w, canvas_h = 820, 460

    STL_X_MIN, STL_X_MAX = -311.0, 299.0
    STL_Y_MIN, STL_Y_MAX = -160.0,  15.0   # fuselage Y band

    MARGIN = 60
    SVG_X_LEFT  = MARGIN
    SVG_X_RIGHT = canvas_w - MARGIN - 20
    SVG_Y_TOP   = MARGIN + 20
    SVG_Y_BOT   = canvas_h - MARGIN - 30

    hull_verts = load_group(HULL_PARTS)
    fuse_verts = [(x, y, z) for x, y, z in hull_verts
                  if STL_Y_MIN <= y <= STL_Y_MAX]

    h_vals, y_top, y_bot = silhouette(fuse_verts, "x", "y", n_bins=600)

    hull_path = to_svg_path(
        h_vals, y_top, y_bot,
        stl_h_range=(STL_X_MIN, STL_X_MAX),
        stl_v_range=(STL_Y_MIN, STL_Y_MAX),
        svg_h_range=(SVG_X_RIGHT, SVG_X_LEFT),   # flip H: nose at right
        svg_v_range=(SVG_Y_TOP, SVG_Y_BOT),
        flip_h=False,
        flip_v=False,
        simplify_dp=0.5,
    )

    new_hull = (
        f'<path id="hull-bottom-stl" d="{hull_path}" '
        f'fill="#0e2030" fill-opacity="0.85" stroke="#00e5ff" stroke-width="2"/>'
    )

    old_pattern = r'<path[^>]+id="hull-bottom[^>]*/>'
    svg, replaced = replace_element(svg, old_pattern, new_hull)
    if not replaced:
        insert_after = re.search(
            r'<rect[^>]+fill="url\(#grid\)"[^/]*/>', svg
        )
        if insert_after:
            svg = (svg[:insert_after.end()] + "\n" + new_hull +
                   svg[insert_after.end():])
            print("  Hull path inserted ✓")
        else:
            print("  WARNING: Could not find insertion point")
            return

    if replaced:
        print("  Hull path replaced ✓")

    write_svg(fname, svg)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Serenity-UAV — overview SVG hull path updater")
    print(f"STL source: {STL_DIR}")
    print(f"SVG target: {SVG_DIR}")

    update_side_view()
    update_top_view()
    update_front_view()
    update_bottom_view()

    print("\nAll overview SVG hull paths updated.")
    print("Run a visual diff to verify the new hull contours before committing.")
