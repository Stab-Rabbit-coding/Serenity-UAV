#!/usr/bin/env python3
"""
add_structural_features.py  —  add structural features to the four baked fuselage shells.

Implements the structural engineering design from docs/structural_analysis.md (Rev R1,
2026-06-14).  All geometry is in the hull frame (X = +port, Y = +aft, Z = +dorsal).
All four input STLs must already be baked (header carries "SerenityUAV HULL-FRAME R1").

Features added per shell:

    Head:   bore-open aft face; 3× boss-pin bores (Joint 1)
    Cargo:  DELEGATED to merge_cargo_interior.py (Rev R1, 2026-06-30) — that
            script starts from the clean Blender source and merges the joint
            features AND every cargo interior feature (clamshell doors, wing
            spar/mortises, bosses, interior-wall removal) in one robust
            manifold3d pass.  Cargo is SKIPPED here (see main()).
    Middle: bore-open fwd + aft faces; 6× boss-pin bores (Joints 2+3);
            2× CF skid-rod channels (port + stbd)
    Rear:   bore-open fwd face; 3× boss-pin bores (Joint 3);
            keel locating channel; ring-frame pocket at Y = +290 mm;
            2× CF skid-rod channels (port + stbd)

MESH-01 root-cause fix (2026-06-30): _subtract_all now unions all cutters and
does a single manifold3d difference instead of fragile sequential per-cut
booleans — see that function's docstring.  Middle and rear still need a
clean-source regeneration pass with this fixed core (TODO.md MESH-01).

Ring-frame inner-profile CSVs are also exported to airframe/diagrams/ring_frames/.

Structural analysis basis: docs/structural_analysis.md.
References:
    docs/structural_analysis.md (Rev R1, 2026-06-14) — full first-principles analysis,
        load cases, FOS calculations, and design decisions implemented here.
    ASTM F2910-14 [ASTM F38] — Standard Specification for Design and Construction of a
        Small Unmanned Aircraft System (sUAS); primary design reference.
    ASTM F3264-18 [ASTM F44] — Normal Category Aeroplane Airworthiness; 1.5 FOS
        ultimate/limit load methodology adapted as conservative UAS engineering baseline.
        Not a compliance claim (F3264 applies to manned aircraft).
    14 CFR Part 107 — FAA Small Unmanned Aircraft Systems; operational envelope context.
    ISO 21384-1:2022 — UAS General Requirements; design intent reference.
        Compliance review is a pre-certification task.
    CF structural member material allowable σ_u = 1 500 N/mm²: estimated from typical
        commercial pultruded unidirectional CF rod/flat-bar stock data.  ASTM D3039
        tensile and ASTM D695 compressive test certificates from the actual supplier
        are required before fabrication.
    West System 105/206 technical data sheet — epoxy joint bonding properties.

Run (no Blender needed):
    python3 airframe/blender-scripts/add_structural_features.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
"""

import csv
import os
import struct
import sys

import numpy as np
import trimesh
from manifold3d import Manifold as _Manifold
from manifold3d import Mesh as _Mesh
from shapely.geometry import Polygon

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
STL_DIR = os.path.join(REPO_ROOT, "airframe", "stls")
RING_CSV_DIR = os.path.join(REPO_ROOT, "airframe", "diagrams", "ring_frames")

# Canonical baked shell paths (hull frame, identity placement)
SHELLS = {
    "head": os.path.join(STL_DIR, "fuselage", "head_shell24_2mm_repaired.stl"),
    "cargo": os.path.join(
        STL_DIR, "fuselage", "cargo", "cargo_sect_shell24_2mm_repaired.stl"
    ),
    "middle": os.path.join(STL_DIR, "fuselage", "middle_shell24_2mm_repaired.stl"),
    "rear": os.path.join(STL_DIR, "fuselage", "rear_shell24_2mm_repaired.stl"),
}

MARKER = b"SerenityUAV HULL-FRAME R1"

# ---------------------------------------------------------------------------
# Structural feature geometry (all dimensions in mm, hull frame)
# Basis: docs/structural_analysis.md Rev R1 2026-06-14
# ---------------------------------------------------------------------------

# ---------- bore-open joint-face cutters (measured-geometry, subtracted) ----------
#
# HOLE-01 fix (2026-06-22): this used to be a hand-picked rectangular box per
# joint, "sized to ~80% of the inner cross-section at each face." That sizing
# assumed the cross-section's Z-height is roughly constant across its X-width,
# which is false for Serenity's tapering/oval/horseshoe profiles — at the
# lateral edges of every one of the six joints the true hull is shorter in Z
# than the box, so the box's full Z-range exited through the side skin and
# punched a clean hole through the fuselage wall instead of staying inside the
# cavity. Confirmed on the pristine pre-cut shells: all 6 joints punched
# through at the lateral edges (cargo_aft and middle_fwd punched through
# across roughly half their X-span). This is what produced the "huge gaps
# between sections" defect. See TODO.md HOLE-01 for the incident writeup.
#
# Fix: instead of guessing a box, _bore_open_cutter() measures the actual
# inner-cavity cross-section of the shell being processed (it slices the
# REAL mesh, not an assumed bounding box) at several stations across the
# joint's Y-span, insets each one by FACE_BORE_MARGIN, and intersects them
# all together. The result is, by construction, never larger than the
# narrowest true cavity opening anywhere in that Y-span, so it can never
# reach the inner wall — let alone the outer skin — regardless of how the
# cross-section tapers. Only the Y-span (how deep into each section the bore
# reaches) is still a hand-picked constant; X/Z shape is always measured.
FACE_BORE_Y_RANGES = {
    # Head aft face (Y = -70.7 mm): bore from 14 mm inside head to 2.7 mm past face
    "head_aft": (-85.0, -68.0),
    # Cargo fwd face (Y = -71.5 mm): from 2 mm before face to 13.5 mm inside cargo
    "cargo_fwd": (-75.0, -58.0),
    # Cargo aft face (Y = +132.0 mm): 10 mm inside cargo to 2 mm past face
    "cargo_aft": (+122.0, +134.0),
    # Middle fwd face (Y = +130.4 mm): 2 mm before face to 14.6 mm inside middle
    "middle_fwd": (+128.0, +145.0),
    # Middle aft face (Y = +203.6 mm): 10 mm inside middle to 3.4 mm past face
    "middle_aft": (+193.0, +207.0),
    # Rear fwd face (Y = +203.2 mm): 2 mm before face to 13.8 mm inside rear
    "rear_fwd": (+201.0, +217.0),
}
FACE_BORE_MARGIN = 1.5  # mm — inset from the measured inner-cavity wall
FACE_BORE_SAMPLES = 7  # Y stations sampled across each joint's span

# ---------- boss-pin bores (Ø 3.2 mm cylinders, Y-axis, 8 mm each section) ----------
# Positions on r = 35 mm circle at 0° / 120° / 240° from cross-section centroid.
# Y range spans both mating sections (≈ 8–10 mm depth each).
# Basis: structural_analysis.md §7.2
BOSS_PIN_BORES = {
    "joint1": {  # Head / Cargo, hull Y ≈ -71 mm
        "y_range": (-79.0, -62.0),
        "pins": [
            (-168.3, +143.9),  # Pin A — top
            (-138.0, +91.4),  # Pin B — lower stbd
            (-198.6, +91.4),  # Pin C — lower port
        ],
    },
    "joint2": {  # Cargo / Middle, hull Y ≈ +131 mm
        "y_range": (+121.0, +141.0),
        "pins": [
            (-170.1, +115.0),  # Pin A — top
            (-139.8, +62.5),  # Pin B — lower stbd
            (-200.4, +62.5),  # Pin C — lower port
        ],
    },
    "joint3": {  # Middle / Rear, hull Y ≈ +203 mm
        "y_range": (+193.0, +213.0),
        "pins": [
            (-170.1, +109.6),  # Pin A — top
            (-139.8, +57.1),  # Pin B — lower stbd
            (-200.4, +57.1),  # Pin C — lower port
        ],
    },
}
BOSS_PIN_RADIUS = 1.6  # mm — Ø 3.2 mm bore (CF rod 3.0 mm OD + 0.1 mm clearance/side)

# ---------- keel locating channel (3.5 mm wide × 1.0 mm deep, inner belly surface) ----------
# Groove centred at hull X = -170 mm; 1 mm removed from inner surface.
# Cargo belly outer Z ≈ 0 mm → inner Z ≈ 2 mm → groove at Z = [1.0, 2.0].
# Rear belly outer Z ≈ 3.7 mm → inner Z ≈ 5.7 mm → groove at Z = [4.7, 5.7].
# Middle section has no belly (horseshoe open at -Z) → no channel.
# Basis: structural_analysis.md §4.5
#
# MESH-01 fix (2026-06-16): the groove's outer face (z_max for cargo, z_max for
# rear) previously landed exactly ON the shell's existing inner-wall surface —
# a zero-overlap coincident face that the manifold3d boolean difference turned
# into non-manifold edges / degenerate slivers (see TODO.md MESH-01). CUT_OVERLAP
# pushes that face CUT_OVERLAP past the existing surface, into the already-hollow
# interior, where there is no material to over-remove.
CUT_OVERLAP = 0.5  # mm — clearance past an existing mesh surface for any cutter
# face meant to coincide with it (avoids manifold3d non-manifold
# edges from exactly-coplanar cut/surface faces; MESH-01 fix)

KEEL_CHANNEL = {
    "cargo": {
        "x_range": (-171.75, -168.25),
        "z_range": (1.0, 2.0 + CUT_OVERLAP),
        "y_range": (-71.5, +132.0),
    },
    "rear": {
        "x_range": (-171.75, -168.25),
        "z_range": (4.7, 5.7 + CUT_OVERLAP),
        "y_range": (+203.2, +384.3),
    },
}

# ---------- ring-frame pockets (2.5 mm wide in Y, 1.0 mm deep, 4 side cutters) ----------
# Four thin rectangular slabs are subtracted around the inner perimeter to create a
# locating groove for the 2 mm CF plate to slide into.
# Inner surface estimated as outer bounding-box inset 2 mm each side.
# Basis: structural_analysis.md §5.5
#
# MESH-01 fix (2026-06-16): the original hardcoded top/bottom slab Z-ranges were on
# the WRONG side of the inner surface — they sat entirely in the already-hollow
# interior and never actually touched the solid wall, so the pocket groove was never
# cut at the top/bottom of the ring (only port/stbd were ever real cuts). Replaced
# with _ring_pocket_slabs(), which derives all 4 slabs from the outer bounds + wall
# inset so the pocket geometry is provably on the solid-material side, with
# CUT_OVERLAP clearance past every face that meets the existing mesh surface (both
# the inner-wall face and the four corners where adjacent slabs must overlap).
POCKET_DEPTH = 1.0  # mm — groove depth, per structural_analysis.md §5.5
WALL_INSET = 2.0  # mm — 2 mm wall thickness (outer-to-inner offset)


def _ring_pocket_slabs(
    x_outer,
    z_outer,
    y_centre,
    y_half=1.25,
    inset=WALL_INSET,
    depth=POCKET_DEPTH,
    overlap=CUT_OVERLAP,
):
    """
    Return the 4 perimeter slab cutters (top, port, stbd, bottom) for a ring-frame
    pocket, given the OUTER cross-section bounds at the ring station.

    Each slab removes `depth` mm of the solid wall starting at the inner (cavity-
    facing) surface; the face that meets the existing inner surface is pushed
    `overlap` mm further into the already-hollow interior (MESH-01 fix), and the
    in-plane extent of each slab is grown by `overlap` mm so adjacent slabs overlap
    at the four corners instead of leaving an uncut sliver.
    """
    xo_min, xo_max = x_outer
    zo_min, zo_max = z_outer
    xi_min, xi_max = xo_min + inset, xo_max - inset
    zi_min, zi_max = zo_min + inset, zo_max - inset
    y0, y1 = y_centre - y_half, y_centre + y_half

    top = (xi_min - overlap, xi_max + overlap, zi_max - overlap, zi_max + depth, y0, y1)
    bottom = (
        xi_min - overlap,
        xi_max + overlap,
        zi_min - depth,
        zi_min + overlap,
        y0,
        y1,
    )
    port = (
        xi_min - overlap,
        xi_min + depth,
        zi_min - overlap,
        zi_max + overlap,
        y0,
        y1,
    )
    stbd = (
        xi_max - depth,
        xi_max + overlap,
        zi_min - overlap,
        zi_max + overlap,
        y0,
        y1,
    )
    return [top, port, stbd, bottom]


RING_POCKETS = {
    # Cargo wing-spar zone, Y = +30 mm
    # Outer bounds at Y=30: X[-257.6..-81.1]  Z[+0.5..+158.6]
    "cargo_Y30": _ring_pocket_slabs((-257.6, -81.1), (0.5, 158.6), 30.0),
    # Rear anti-ovalisation zone, Y = +290 mm
    # Outer bounds at Y=290: X[-235.5..-116.0]  Z[+11.9..+152.4]
    "rear_Y290": _ring_pocket_slabs((-235.5, -116.0), (11.9, 152.4), 290.0),
}

# ---------- CF skid-rod bores (Ø 4.2 mm cylinders, Y-axis, 60 mm total) ----------
# Bore spans 30 mm each side of the middle/rear joint (Y = +203 mm).
# Positions from STL vertex survey; see structural_analysis.md §6.3.
SKID_ROD_BORES = [
    # (x_centre, z_centre, y_start, y_end)
    (-202.0, 18.0, +173.0, +233.0),  # port arm
    (-135.0, 20.0, +173.0, +233.0),  # stbd arm
]
SKID_ROD_RADIUS = 2.1  # mm — Ø 4.2 mm bore (CF rod 4.0 mm OD + 0.1 mm clearance/side)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _box(x0, x1, z0, z1, y0, y1):
    """
    Return a trimesh.Trimesh box (watertight) matching the specified hull-frame
    X/Z/Y corner coordinates.

    trimesh.creation.box creates a box centred at origin; translate to correct centre.
    """
    dx, dy, dz = x1 - x0, y1 - y0, z1 - z0
    # Hull frame: X=0, Y=1, Z=2  →  trimesh box extents in [X, Y, Z]
    box = trimesh.creation.box(extents=[dx, dy, dz])
    centre = np.array([(x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0])
    box.apply_translation(centre)
    return box


def _keel_channel_cutter(section_key):
    """Return the keel-locating-channel box cutter for KEEL_CHANNEL[section_key]
    (shared by process_cargo and process_rear — same geometry construction)."""
    kc = KEEL_CHANNEL[section_key]
    return _box(
        kc["x_range"][0],
        kc["x_range"][1],
        kc["z_range"][0],
        kc["z_range"][1],
        kc["y_range"][0],
        kc["y_range"][1],
    )


def _y_cylinder(x_cen, z_cen, y_start, y_end, radius, sections=32):
    """
    Return a trimesh cylinder aligned with the hull Y axis (positive aft).

    trimesh.creation.cylinder produces a Z-axis cylinder; rotate 90° about X to
    align with Y.
    """
    length = y_end - y_start
    cyl = trimesh.creation.cylinder(radius=radius, height=length, sections=sections)
    # Rotate 90° about +X: Z-axis becomes +Y-axis
    rot = trimesh.transformations.rotation_matrix(np.pi / 2.0, [1.0, 0.0, 0.0])
    cyl.apply_transform(rot)
    y_cen = (y_start + y_end) / 2.0
    cyl.apply_translation([x_cen, y_cen, z_cen])
    return cyl


CAVITY_JUNK_FLOOR = 5.0  # mm^2 — loops smaller than this are mesh artifacts
# (degenerate slivers, boss/rib details), never the
# real inner-cavity boundary; see HOLE-01 fix note.


def _inner_cavity_polygon(mesh, y, margin):
    """
    Return the shell's inner-cavity cross-section (X, Z) at hull Y = y, inset by
    `margin` mm, or None if no valid cross-section is found at that station.

    A 2 mm-wall hollow shell sliced at any interior Y produces, ideally, two
    closed loops: the outer skin boundary (largest area) and the inner cavity
    boundary (second-largest). In practice the slicer can also return several
    tiny sliver loops from mesh detail or float32 voxel-remesh noise — taking
    the SMALLEST loop above a trivial area threshold (the original approach)
    picked up these slivers instead of the real cavity, which silently shrank
    or emptied the cutter (see HOLE-01 fix note on FACE_BORE_Y_RANGES above).
    The second-largest loop, with a sanity floor (CAVITY_JUNK_FLOOR) well
    above any plausible artifact, is the robust choice. Insetting it (negative
    buffer) keeps the returned polygon strictly inside the cavity, away from
    the inner wall.
    """
    section = mesh.section(plane_origin=[0.0, y, 0.0], plane_normal=[0.0, 1.0, 0.0])
    if section is None:
        return None
    polys = []
    for loop in section.discrete:
        arr = np.asarray(loop)
        p = Polygon(arr[:, [0, 2]])
        if p.is_valid and p.area > CAVITY_JUNK_FLOOR:
            polys.append(p)
    if len(polys) < 2:
        return None
    polys.sort(key=lambda p: p.area, reverse=True)
    inset = polys[1].buffer(-margin)
    return None if inset.is_empty else inset


def _bore_open_cutter(
    mesh, y_range, margin=FACE_BORE_MARGIN, samples=FACE_BORE_SAMPLES
):
    """
    Build a bore-open cutter for a joint face that is, by construction, always
    inside the shell's measured inner cavity across the given hull-Y span —
    it can never reach the inner wall, let alone punch through the outer skin
    (see HOLE-01 fix note on FACE_BORE_Y_RANGES above).

    Lofted per-segment construction: the cavity cross-section is measured at
    `samples` stations spanning y_range, and a separate prism is extruded
    between each consecutive pair of stations using the INTERSECTION of just
    those two stations' (inset) cavity polygons. This follows a tapering
    cavity (e.g. near a section's narrowing nose/tail) instead of one global
    intersection across the whole span, which a single local pinch point
    would collapse to empty even though most of the span has plenty of
    clearance. A segment whose pair-wise intersection is empty is simply
    skipped (a real local pinch — nothing safe to cut there); the function
    only raises if EVERY segment across the whole span is empty.
    """
    ys = np.linspace(y_range[0], y_range[1], samples)
    polys = [_inner_cavity_polygon(mesh, y, margin) for y in ys]

    segments = []
    for i in range(len(ys) - 1):
        p0, p1 = polys[i], polys[i + 1]
        if p0 is None or p1 is None:
            continue
        seg_poly = p0.intersection(p1)
        if seg_poly.is_empty or seg_poly.area < 1.0:
            continue
        if seg_poly.geom_type == "MultiPolygon":
            seg_poly = max(seg_poly.geoms, key=lambda g: g.area)
        height = ys[i + 1] - ys[i]
        extrusion = trimesh.creation.extrude_polygon(seg_poly, height=height)
        # extrude_polygon builds (x, y, z) = (poly_x, poly_y, [0, height]);
        # remap to hull frame: hull_X = poly_x, hull_Z = poly_y,
        # hull_Y = z + ys[i].
        remap = np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, ys[i]],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )
        extrusion.apply_transform(remap)
        segments.append(extrusion)

    if not segments:
        raise RuntimeError(
            f"_bore_open_cutter: no safe inner-cavity opening anywhere across "
            f"y_range={y_range} (margin={margin} mm) — narrow y_range or "
            f"reduce margin and re-survey this joint"
        )
    # Return each segment as its own watertight solid rather than one
    # concatenated mesh: adjacent segments' polygons can differ slightly
    # (different pairwise intersections), so gluing them into a single mesh
    # risks non-manifold seams at the shared Y plane. _subtract_all() already
    # takes a list and subtracts cutters one at a time, so independent
    # segments are the natural fit.
    return segments


def _to_manifold_volume(mesh):
    """
    Round-trip the mesh through manifold3d's Manifold constructor to repair the small
    number of non-manifold edges (typically 4–6 degenerate float32 triangles) that the
    voxel-remesh + boolean pipeline leaves in the baked STLs.

    manifold3d silently drops degenerate topology and returns a guaranteed 2-manifold.
    The head, cargo, and rear shells need this pass; the middle is already a volume.
    """
    if mesh.is_volume:
        return mesh
    verts = mesh.vertices.astype(np.float32)
    faces = mesh.faces.astype(np.uint32)
    mf = _Manifold(_Mesh(vert_properties=verts, tri_verts=faces))
    out = mf.to_mesh()
    repaired = trimesh.Trimesh(
        vertices=np.array(out.vert_properties, dtype=np.float64),
        faces=np.array(out.tri_verts, dtype=np.int64),
        process=False,
    )
    repaired.fix_normals()
    return repaired


def _manifold_from_trimesh(tm):
    """trimesh.Trimesh -> manifold3d.Manifold (float32, as manifold3d uses)."""
    return _Manifold(
        _Mesh(
            vert_properties=tm.vertices.astype(np.float32),
            tri_verts=tm.faces.astype(np.uint32),
        )
    )


def _trimesh_from_manifold(man):
    """manifold3d.Manifold -> trimesh.Trimesh (float64 vertices)."""
    msh = man.to_mesh()
    return trimesh.Trimesh(
        vertices=np.asarray(msh.vert_properties, dtype=np.float64)[:, :3],
        faces=np.asarray(msh.tri_verts, dtype=np.int64),
        process=False,
    )


def _subtract_all(shell, cutters):
    """
    Subtract ALL cutters from the shell in ONE robust manifold3d expression:
    union every cutter into a single Manifold, then evaluate  shell - union.

    MESH-01 fix (2026-06-30): the previous implementation subtracted cutters
    one at a time with trimesh.boolean.difference(engine="manifold") plus a
    per-step _to_manifold_volume "repair" on a ~1.4 M-face shell, then dropped
    sub-1000-face junk.  That fragile sequential round-trip is the actual root
    cause of MESH-01 — it left the published cargo/middle/rear shells
    non-watertight and fragmented (cargo: 71 131 disconnected bodies,
    is_watertight=False; TODO.md MESH-01).

    Boolean subtraction/union of closed 2-manifolds is closed by construction,
    so unioning the cutters and doing a single difference is both robust
    (guaranteed watertight out, no compounding degenerate slivers, no junk
    components to sweep) and far faster than dozens of full-mesh round-trips.
    This is the same manifold3d-direct approach proven on the cargo section by
    merge_cargo_interior.py (watertight=True, single body, volume = the
    structural_analysis.md mass-budget figure).  CUT_OVERLAP (finite clearance
    past coincident surfaces) is still applied on the cutter geometry so no cut
    face lands exactly on an existing wall.
    """
    if not cutters:
        return shell
    shell_man = _manifold_from_trimesh(shell)
    neg = None
    for cutter in cutters:
        cm = _manifold_from_trimesh(cutter)
        neg = cm if neg is None else (neg + cm)
    result = _trimesh_from_manifold(shell_man - neg)

    # Post-boolean cleanup (2026-07-02, MESH-01 follow-up): the manifold3d ->
    # trimesh round trip can leave a small number (observed: 1-2) of zero-area
    # degenerate triangles at cut boundaries where float64 (manifold3d output)
    # is later re-quantized to float32 on binary STL export. These degenerate
    # faces show up as spurious non-manifold edges / isolated near-zero-volume
    # "junk" bodies only AFTER the STL round trip, even though the in-memory
    # result reports watertight=True. Stripping them here (before export)
    # keeps the exported file watertight through the float32 round trip too.
    # See TODO.md MESH-01 for the incident writeup (found while regenerating
    # the middle shell — 2 non-manifold edges / one 2-face 0-volume fragment).
    result.update_faces(result.nondegenerate_faces())
    result.remove_unreferenced_vertices()
    return result


def _stamp_header_export(mesh, out_path, shell_name):
    """
    Write the mesh as binary STL with the HULL-FRAME R1 marker in the 80-byte header.

    Stamping the marker on the output means bake_hull_frame.py --check will see the
    file as already baked (the geometry is already in hull frame; we are only adding
    features, not re-applying a placement transform).
    """
    count = len(mesh.faces)
    tris = mesh.vertices[mesh.faces]  # (N, 3, 3) float64

    # Recompute normals from CCW winding
    e1 = tris[:, 1, :] - tris[:, 0, :]
    e2 = tris[:, 2, :] - tris[:, 0, :]
    normals = np.cross(e1, e2)
    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    safe = np.where(lengths > 0.0, lengths, 1.0)
    normals = np.where(lengths > 0.0, normals / safe, 0.0)

    rec_dtype = np.dtype([("data", "<f4", (12,)), ("attr", "<u2")])
    assert rec_dtype.itemsize == 50
    rec = np.zeros(count, dtype=rec_dtype)
    rec["data"][:, 0:3] = normals.astype("<f4")
    rec["data"][:, 3:12] = tris.reshape(count, 9).astype("<f4")

    header_str = (
        MARKER + b" " + shell_name.encode("ascii") + b" structural-features 2026-06-14"
    )
    header = header_str[:80].ljust(80, b"\0")

    with open(out_path, "wb") as fh:
        fh.write(header)
        fh.write(struct.pack("<I", count))
        fh.write(rec.tobytes())


def _export_ring_profile(shell_mesh, y_station, csv_path):
    """
    Slice the shell at hull Y = y_station and write the inner cross-section boundary
    as a two-column (X, Z) CSV.

    If multiple paths are found at the section, all paths are concatenated (separated
    by a blank row sentinel) so the DXF operator can identify inner vs outer wall.
    """
    section = shell_mesh.section(
        plane_origin=[0.0, y_station, 0.0],
        plane_normal=[0.0, 1.0, 0.0],
    )
    if section is None:
        print(f"    [WARN] no cross-section found at Y={y_station} for CSV export")
        return

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["X_mm", "Z_mm", "path_index"])
        for idx, entity in enumerate(section.entities):
            pts = section.vertices[entity.points]
            for pt in pts:
                writer.writerow([f"{pt[0]:.3f}", f"{pt[2]:.3f}", idx])
            writer.writerow(["", "", ""])  # blank row between paths

    all_pts = section.vertices
    print(
        f"    ring profile @ Y={y_station}: {len(section.entities)} paths, "
        f"{len(all_pts)} vertices → {os.path.basename(csv_path)}"
    )


# ---------------------------------------------------------------------------
# Per-shell processing
# ---------------------------------------------------------------------------


def process_head(mesh):
    """
    Head section structural features:
      - bore-open aft face (Joint 1, hull Y ≈ -71 mm)
      - 3× boss-pin bores (Joint 1)
    """
    mesh = _to_manifold_volume(mesh)
    print("  [head] building cutters …")
    cutters = []

    # Bore-open aft face
    cutters.extend(_bore_open_cutter(mesh, FACE_BORE_Y_RANGES["head_aft"]))

    # Boss-pin bores (Joint 1)
    j = BOSS_PIN_BORES["joint1"]
    y0, y1 = j["y_range"]
    for x_pin, z_pin in j["pins"]:
        cutters.append(_y_cylinder(x_pin, z_pin, y0, y1, BOSS_PIN_RADIUS))

    print(f"  [head] subtracting {len(cutters)} cutters …")
    return _subtract_all(mesh, cutters)


def process_cargo(mesh):
    """
    Cargo section structural features:
      (pre-repair: manifold3d round-trip to remove degenerate float32 edges)
      - bore-open fwd face (Joint 1)
      - bore-open aft face (Joint 2)
      - 3× boss-pin bores (Joint 1) — shared bore with head
      - 3× boss-pin bores (Joint 2) — shared bore with middle
      - keel locating channel
      - ring-frame pocket at Y = +30 mm
    """
    mesh = _to_manifold_volume(mesh)
    print("  [cargo] building cutters …")
    cutters = []

    # Bore-open faces
    for key in ("cargo_fwd", "cargo_aft"):
        cutters.extend(_bore_open_cutter(mesh, FACE_BORE_Y_RANGES[key]))

    # Boss-pin bores (Joints 1 and 2)
    for jname in ("joint1", "joint2"):
        j = BOSS_PIN_BORES[jname]
        y0, y1 = j["y_range"]
        for x_pin, z_pin in j["pins"]:
            cutters.append(_y_cylinder(x_pin, z_pin, y0, y1, BOSS_PIN_RADIUS))

    # Keel locating channel
    cutters.append(_keel_channel_cutter("cargo"))

    # Ring-frame pocket at Y = +30 mm (4 side cutters)
    for xm, xx, zm, zx, ym, yx in RING_POCKETS["cargo_Y30"]:
        cutters.append(_box(xm, xx, zm, zx, ym, yx))

    print(f"  [cargo] subtracting {len(cutters)} cutters …")
    return _subtract_all(mesh, cutters)


def process_middle(mesh):
    """
    Middle section structural features:
      - bore-open fwd face (Joint 2)
      - bore-open aft face (Joint 3)
      - 3× boss-pin bores (Joint 2)
      - 3× boss-pin bores (Joint 3)
      - 2× CF skid-rod bores (port + stbd)
    """
    mesh = _to_manifold_volume(mesh)
    print("  [middle] building cutters …")
    cutters = []

    # Bore-open faces
    for key in ("middle_fwd", "middle_aft"):
        cutters.extend(_bore_open_cutter(mesh, FACE_BORE_Y_RANGES[key]))

    # Boss-pin bores (Joints 2 and 3)
    for jname in ("joint2", "joint3"):
        j = BOSS_PIN_BORES[jname]
        y0, y1 = j["y_range"]
        for x_pin, z_pin in j["pins"]:
            cutters.append(_y_cylinder(x_pin, z_pin, y0, y1, BOSS_PIN_RADIUS))

    # CF skid-rod bores
    for x_cen, z_cen, y0, y1 in SKID_ROD_BORES:
        cutters.append(_y_cylinder(x_cen, z_cen, y0, y1, SKID_ROD_RADIUS))

    print(f"  [middle] subtracting {len(cutters)} cutters …")
    return _subtract_all(mesh, cutters)


def process_rear(mesh):
    """
    Rear section structural features:
      - bore-open fwd face (Joint 3)
      - 3× boss-pin bores (Joint 3)
      - keel locating channel
      - ring-frame pocket at Y = +290 mm
      - 2× CF skid-rod bores (port + stbd)
    """
    mesh = _to_manifold_volume(mesh)
    print("  [rear] building cutters …")
    cutters = []

    # Bore-open fwd face
    cutters.extend(_bore_open_cutter(mesh, FACE_BORE_Y_RANGES["rear_fwd"]))

    # Boss-pin bores (Joint 3)
    j = BOSS_PIN_BORES["joint3"]
    y0, y1 = j["y_range"]
    for x_pin, z_pin in j["pins"]:
        cutters.append(_y_cylinder(x_pin, z_pin, y0, y1, BOSS_PIN_RADIUS))

    # Keel locating channel
    cutters.append(_keel_channel_cutter("rear"))

    # Ring-frame pocket at Y = +290 mm
    for xm, xx, zm, zx, ym, yx in RING_POCKETS["rear_Y290"]:
        cutters.append(_box(xm, xx, zm, zx, ym, yx))

    # CF skid-rod bores
    for x_cen, z_cen, y0, y1 in SKID_ROD_BORES:
        cutters.append(_y_cylinder(x_cen, z_cen, y0, y1, SKID_ROD_RADIUS))

    print(f"  [rear] subtracting {len(cutters)} cutters …")
    return _subtract_all(mesh, cutters)


# ---------------------------------------------------------------------------
# Verification gate
# ---------------------------------------------------------------------------


def verify(mesh, name):
    """
    Manufacturing-watertight gate: no open boundary edges, no non-manifold edges,
    no small junk fragments (< JUNK_FACE_LIMIT faces), winding consistent, and
    `mesh.is_watertight` true.  Body count is NOT capped — a properly hollowed
    2 mm shell legitimately splits into 2+ large components (outer surface +
    disconnected inner surface, which never share an edge; rear additionally has
    skid/pod cavity lobes).  See verify_shells.py module docstring for the
    empirical confirmation (signed sub-volumes summing to the exact
    structural_analysis.md mass-budget figures).

    MESH-01 fix (2026-06-16): the previous gate only checked open-boundary edges
    (count == 1) and a 64-500-face junk-component window.  It missed non-manifold
    edges (count > 2, the actual defect signature left by near-coincident cutter
    faces) and never hard-required `is_watertight` — so it reported "PASS" on
    shells that were not watertight and, in the rear shell's case, fragmented into
    multiple disconnected solid islands.  An initial fix over-corrected to require
    exactly 1 body, which incorrectly failed the legitimate outer+inner double-wall
    topology; reverted in favour of a junk-fragment-size check.  See TODO.md
    MESH-01 for the full incident writeup.
    """
    JUNK_FACE_LIMIT = 64

    edge_counts = np.bincount(
        mesh.edges_unique_inverse,
        minlength=len(mesh.edges_unique),
    )
    b_count = int(np.sum(edge_counts == 1))  # open boundary edges
    nm_count = int(np.sum(edge_counts > 2))  # non-manifold edges

    comps = mesh.split(only_watertight=False)
    bodies = len(comps)
    junk = [c for c in comps if len(c.faces) < JUNK_FACE_LIMIT]

    status = (
        "PASS"
        if (
            b_count == 0
            and nm_count == 0
            and not junk
            and mesh.is_winding_consistent
            and mesh.is_watertight
        )
        else "FAIL"
    )
    print(
        f"    verify {name}: {status}  "
        f"boundary={b_count}  nonmanifold={nm_count}  bodies={bodies}  "
        f"junk_fragments={len(junk)}  "
        f"winding={mesh.is_winding_consistent}  "
        f"watertight={mesh.is_watertight}  "
        f"vol={mesh.volume:.0f} mm³  "
        f"faces={len(mesh.faces):,}"
    )
    return status == "PASS"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    """Process all four fuselage shells and export ring-frame profiles."""
    print("=== add_structural_features.py  Rev R1  2026-06-14 ===")

    processors = {
        "head": process_head,
        "cargo": process_cargo,
        "middle": process_middle,
        "rear": process_rear,
    }

    # Ring-frame profile export: slice BEFORE modification (geometry unchanged at
    # those Y stations — ring pockets only affect a 2.5 mm Y slice).
    print("\n--- ring-frame inner-profile CSV export ---")
    cargo_mesh_raw = trimesh.load(SHELLS["cargo"], process=True)
    rear_mesh_raw = trimesh.load(SHELLS["rear"], process=True)
    _export_ring_profile(
        cargo_mesh_raw,
        30.0,
        os.path.join(RING_CSV_DIR, "ring_cargo_Y30_inner.csv"),
    )
    _export_ring_profile(
        rear_mesh_raw,
        290.0,
        os.path.join(RING_CSV_DIR, "ring_rear_Y290_inner.csv"),
    )

    # Cargo is now processed by airframe/blender-scripts/merge_cargo_interior.py,
    # which starts from the CLEAN Blender source and merges the joint features
    # AND all cargo interior features (doors, wing, bosses, interior-wall
    # removal) in one robust manifold3d pass (TODO.md §1.1.1.0a).  Running the
    # joint cuts here as well would double-process the cargo joints, so cargo is
    # skipped.  Middle and rear still need a clean-source regeneration pass with
    # the MESH-01-fixed _subtract_all above (TODO.md MESH-01 / §1.1.1.0a).
    SKIP = {"cargo"}

    results = {}
    for name, path in SHELLS.items():
        if name in SKIP:
            print(f"\n--- {name}: SKIPPED (see merge_cargo_interior.py) ---")
            continue
        print(f"\n--- {name} ({path}) ---")
        mesh = trimesh.load(path, process=True)
        print(f"  loaded: {len(mesh.faces):,} faces  vol={mesh.volume:.0f} mm³")

        modified = processors[name](mesh)

        print(f"  after:  {len(modified.faces):,} faces  vol={modified.volume:.0f} mm³")
        passed = verify(modified, name)

        # Write output with HULL-FRAME R1 header (geometry already in hull frame;
        # no placement transform applied — only boolean subtractions).
        _stamp_header_export(modified, path, name.capitalize() + "_Shell")
        print(f"  written → {path}")
        results[name] = "PASS" if passed else "FAIL"

    # Summary
    print("\n=== Summary ===")
    for name, status in results.items():
        print(f"  {name:10s}: {status}")
    any_fail = any(s == "FAIL" for s in results.values())
    if any_fail:
        print(
            "\nWARN: one or more shells failed verification — inspect before printing."
        )
        sys.exit(1)
    else:
        print("\nAll shells PASS manufacturing-watertight gate.")
        print(
            "Run: python3 tools/bake_hull_frame.py --check  (to confirm HULL-FRAME R1 marker)"
        )
        print(
            "Slicer verification of feature positions is required before first print."
        )


if __name__ == "__main__":
    main()
