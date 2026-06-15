#!/usr/bin/env python3
"""
add_structural_features.py  —  add structural features to the four baked fuselage shells.

Implements the structural engineering design from docs/structural_analysis.md (Rev R1,
2026-06-14).  All geometry is in the hull frame (X = +port, Y = +aft, Z = +dorsal).
All four input STLs must already be baked (header carries "SerenityUAV HULL-FRAME R1").

Features added per shell:

    Head:   bore-open aft face; 3× boss-pin bores (Joint 1)
    Cargo:  bore-open fwd + aft faces; 6× boss-pin bores (Joints 1+2);
            keel locating channel; ring-frame pocket at Y = +30 mm
    Middle: bore-open fwd + aft faces; 6× boss-pin bores (Joints 2+3);
            2× CF skid-rod channels (port + stbd)
    Rear:   bore-open fwd face; 3× boss-pin bores (Joint 3);
            keel locating channel; ring-frame pocket at Y = +290 mm;
            2× CF skid-rod channels (port + stbd)

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

import os
import sys
import csv
import struct

import numpy as np
import trimesh
from manifold3d import Manifold as _Manifold, Mesh as _Mesh

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
STL_DIR = os.path.join(REPO_ROOT, "airframe", "stls")
RING_CSV_DIR = os.path.join(REPO_ROOT, "airframe", "diagrams", "ring_frames")

# Canonical baked shell paths (hull frame, identity placement)
SHELLS = {
    "head":   os.path.join(STL_DIR, "fuselage", "head_shell24_2mm_repaired.stl"),
    "cargo":  os.path.join(STL_DIR, "fuselage", "cargo",
                           "cargo_sect_shell24_2mm_repaired.stl"),
    "middle": os.path.join(STL_DIR, "fuselage", "middle_shell24_2mm_repaired.stl"),
    "rear":   os.path.join(STL_DIR, "fuselage", "rear_shell24_2mm_repaired.stl"),
}

MARKER = b"SerenityUAV HULL-FRAME R1"

# ---------------------------------------------------------------------------
# Structural feature geometry (all dimensions in mm, hull frame)
# Basis: docs/structural_analysis.md Rev R1 2026-06-14
# ---------------------------------------------------------------------------

# ---------- bore-open joint-face cutters (rectangular box, subtracted) ----------
# Each cutter is (x_min, x_max, z_min, z_max, y_min, y_max).
# Sized to ~80% of the inner cross-section at each face — conservative so the
# cutter never exits the outer skin on any of the complex Serenity profiles.
# Cross-section survey data: see docs/structural_analysis.md §7 + shell survey.

FACE_BORE_CUTTERS = {
    # Head aft face (Y = -70.7 mm): cutter from 14 mm inside head to 2.7 mm past face
    "head_aft":   (-228.9, -107.6,  65.3, 152.4,  -85.0,  -68.0),
    # Cargo fwd face (Y = -71.5 mm): from 2 mm before face to 13.5 mm inside cargo
    "cargo_fwd":  (-224.2, -111.4,  64.1, 142.8,  -75.0,  -58.0),
    # Cargo aft face (Y = +132.0 mm): 10 mm inside cargo to 2 mm past face
    "cargo_aft":  (-250.8,  -89.3,   4.0, 150.4, +122.0, +134.0),
    # Middle fwd face (Y = +130.4 mm): 2 mm before face to 14.6 mm inside middle
    "middle_fwd": (-254.4,  -85.7,  16.2, 139.0, +128.0, +145.0),
    # Middle aft face (Y = +203.6 mm): 10 mm inside middle to 3.4 mm past face
    "middle_aft": (-231.4, -108.7,   7.7, 141.5, +193.0, +207.0),
    # Rear fwd face (Y = +203.2 mm): 2 mm before face to 13.8 mm inside rear
    "rear_fwd":   (-241.0, -110.5,   8.3, 153.2, +201.0, +217.0),
}

# ---------- boss-pin bores (Ø 3.2 mm cylinders, Y-axis, 8 mm each section) ----------
# Positions on r = 35 mm circle at 0° / 120° / 240° from cross-section centroid.
# Y range spans both mating sections (≈ 8–10 mm depth each).
# Basis: structural_analysis.md §7.2
BOSS_PIN_BORES = {
    "joint1": {  # Head / Cargo, hull Y ≈ -71 mm
        "y_range": (-79.0, -62.0),
        "pins": [
            (-168.3, +143.9),   # Pin A — top
            (-138.0,  +91.4),   # Pin B — lower stbd
            (-198.6,  +91.4),   # Pin C — lower port
        ],
    },
    "joint2": {  # Cargo / Middle, hull Y ≈ +131 mm
        "y_range": (+121.0, +141.0),
        "pins": [
            (-170.1, +115.0),   # Pin A — top
            (-139.8,  +62.5),   # Pin B — lower stbd
            (-200.4,  +62.5),   # Pin C — lower port
        ],
    },
    "joint3": {  # Middle / Rear, hull Y ≈ +203 mm
        "y_range": (+193.0, +213.0),
        "pins": [
            (-170.1, +109.6),   # Pin A — top
            (-139.8,  +57.1),   # Pin B — lower stbd
            (-200.4,  +57.1),   # Pin C — lower port
        ],
    },
}
BOSS_PIN_RADIUS = 1.6   # mm — Ø 3.2 mm bore (CF rod 3.0 mm OD + 0.1 mm clearance/side)

# ---------- keel locating channel (3.5 mm wide × 1.0 mm deep, inner belly surface) ----------
# Groove centred at hull X = -170 mm; 1 mm removed from inner surface.
# Cargo belly outer Z ≈ 0 mm → inner Z ≈ 2 mm → groove at Z = [1.0, 2.0].
# Rear belly outer Z ≈ 3.7 mm → inner Z ≈ 5.7 mm → groove at Z = [4.7, 5.7].
# Middle section has no belly (horseshoe open at -Z) → no channel.
# Basis: structural_analysis.md §4.5
KEEL_CHANNEL = {
    "cargo": {"x_range": (-171.75, -168.25), "z_range": (1.0, 2.0),
              "y_range": (-71.5, +132.0)},
    "rear":  {"x_range": (-171.75, -168.25), "z_range": (4.7,  5.7),
              "y_range": (+203.2, +384.3)},
}

# ---------- ring-frame pockets (2.5 mm wide in Y, 1.0 mm deep, 4 side cutters) ----------
# Four thin rectangular slabs are subtracted around the inner perimeter to create a
# locating groove for the 2 mm CF plate to slide into.
# Inner surface estimated as outer bounding-box inset 2 mm each side.
# Basis: structural_analysis.md §5.5
# Format: list of (x_min, x_max, z_min, z_max, y_min, y_max) slab cutters.
RING_POCKETS = {
    # Cargo wing-spar zone, Y = +30 mm
    # Outer bounds at Y=30: X[-257.6..-81.1]  Z[+0.5..+158.6]
    # Inner (2 mm inset): X[-255.6..-83.1]  Z[+2.5..+156.6]
    "cargo_Y30": [
        # Top slab
        (-255.6, -83.1,  155.6, 156.6,  28.75, 31.25),
        # Port slab
        (-256.6, -255.6,   2.5, 155.6,  28.75, 31.25),
        # Stbd slab
        (-83.1,  -82.1,    2.5, 155.6,  28.75, 31.25),
        # Bottom slab
        (-255.6, -83.1,    2.5,   3.5,  28.75, 31.25),
    ],
    # Rear anti-ovalisation zone, Y = +290 mm
    # Outer bounds at Y=290: X[-235.5..-116.0]  Z[+11.9..+152.4]
    # Inner (2 mm inset): X[-233.5..-118.0]  Z[+13.9..+150.4]
    "rear_Y290": [
        # Top slab
        (-233.5, -118.0,  149.4, 150.4, 288.75, 291.25),
        # Port slab
        (-234.5, -233.5,   13.9, 149.4, 288.75, 291.25),
        # Stbd slab
        (-118.0, -117.0,   13.9, 149.4, 288.75, 291.25),
        # Bottom slab
        (-233.5, -118.0,   13.9,  14.9, 288.75, 291.25),
    ],
}

# ---------- CF skid-rod bores (Ø 4.2 mm cylinders, Y-axis, 60 mm total) ----------
# Bore spans 30 mm each side of the middle/rear joint (Y = +203 mm).
# Positions from STL vertex survey; see structural_analysis.md §6.3.
SKID_ROD_BORES = [
    # (x_centre, z_centre, y_start, y_end)
    (-202.0, 18.0, +173.0, +233.0),   # port arm
    (-135.0, 20.0, +173.0, +233.0),   # stbd arm
]
SKID_ROD_RADIUS = 2.1   # mm — Ø 4.2 mm bore (CF rod 4.0 mm OD + 0.1 mm clearance/side)

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
    centre = np.array([(x0 + x1) / 2.0,
                       (y0 + y1) / 2.0,
                       (z0 + z1) / 2.0])
    box.apply_translation(centre)
    return box


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


def _subtract_all(shell, cutters):
    """
    Subtract a list of cutter meshes from the shell using manifold3d.

    Applies each subtraction sequentially to avoid the union-of-cutters step,
    which can produce non-manifold geometry when cutter boxes share coplanar faces.
    After every subtraction, sub-100-face junk components are dropped so the next
    difference always receives a clean volume.
    """
    result = shell
    for i, cutter in enumerate(cutters):
        # Ensure cutter normals are consistent (trimesh.creation objects should be,
        # but rotations can flip winding on degenerate faces).
        if not cutter.is_volume:
            cutter.fix_normals()
        try:
            result = trimesh.boolean.difference([result, cutter], engine="manifold")
        except Exception as exc:
            print(f"    [WARN] cutter {i} difference failed ({exc}); skipping")
            continue

        # Drop junk components after each step.  Main body is hundreds of
        # thousands of faces; anything under 1000 is a boolean artifact.
        comps = result.split(only_watertight=False)
        keep = [c for c in comps if len(c.faces) >= 1000]
        if len(keep) > 1:
            result = trimesh.util.concatenate(keep)
        elif len(keep) == 1:
            result = keep[0]

    return result


def _stamp_header_export(mesh, out_path, shell_name):
    """
    Write the mesh as binary STL with the HULL-FRAME R1 marker in the 80-byte header.

    Stamping the marker on the output means bake_hull_frame.py --check will see the
    file as already baked (the geometry is already in hull frame; we are only adding
    features, not re-applying a placement transform).
    """
    count = len(mesh.faces)
    tris = mesh.vertices[mesh.faces]           # (N, 3, 3) float64

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

    header_str = (MARKER + b" " + shell_name.encode("ascii")
                  + b" structural-features 2026-06-14")
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
            writer.writerow(["", "", ""])   # blank row between paths

    all_pts = section.vertices
    print(f"    ring profile @ Y={y_station}: {len(section.entities)} paths, "
          f"{len(all_pts)} vertices → {os.path.basename(csv_path)}")


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
    xm, xx, zm, zx, ym, yx = FACE_BORE_CUTTERS["head_aft"]
    cutters.append(_box(xm, xx, zm, zx, ym, yx))

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
        xm, xx, zm, zx, ym, yx = FACE_BORE_CUTTERS[key]
        cutters.append(_box(xm, xx, zm, zx, ym, yx))

    # Boss-pin bores (Joints 1 and 2)
    for jname in ("joint1", "joint2"):
        j = BOSS_PIN_BORES[jname]
        y0, y1 = j["y_range"]
        for x_pin, z_pin in j["pins"]:
            cutters.append(_y_cylinder(x_pin, z_pin, y0, y1, BOSS_PIN_RADIUS))

    # Keel locating channel
    kc = KEEL_CHANNEL["cargo"]
    cutters.append(_box(kc["x_range"][0], kc["x_range"][1],
                        kc["z_range"][0], kc["z_range"][1],
                        kc["y_range"][0], kc["y_range"][1]))

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
        xm, xx, zm, zx, ym, yx = FACE_BORE_CUTTERS[key]
        cutters.append(_box(xm, xx, zm, zx, ym, yx))

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
    xm, xx, zm, zx, ym, yx = FACE_BORE_CUTTERS["rear_fwd"]
    cutters.append(_box(xm, xx, zm, zx, ym, yx))

    # Boss-pin bores (Joint 3)
    j = BOSS_PIN_BORES["joint3"]
    y0, y1 = j["y_range"]
    for x_pin, z_pin in j["pins"]:
        cutters.append(_y_cylinder(x_pin, z_pin, y0, y1, BOSS_PIN_RADIUS))

    # Keel locating channel
    kc = KEEL_CHANNEL["rear"]
    cutters.append(_box(kc["x_range"][0], kc["x_range"][1],
                        kc["z_range"][0], kc["z_range"][1],
                        kc["y_range"][0], kc["y_range"][1]))

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
    Manufacturing-watertight gate: no boundary edges; no large detached chunks (≥ 64
    faces); winding consistent.  Matches the criteria in verify_shells.py.
    """
    # Boundary edges appear exactly once across all face-edge occurrences.
    # edges_unique_inverse maps each entry of mesh.edges to its unique-edge index,
    # so bincount gives the occurrence count per unique edge.
    edge_counts = np.bincount(
        mesh.edges_unique_inverse,
        minlength=len(mesh.edges_unique),
    )
    b_count = int(np.sum(edge_counts == 1))

    comps = mesh.split(only_watertight=False)
    junk = [c for c in comps if 64 <= len(c.faces) < 500]

    status = "PASS" if (b_count == 0 and not junk
                        and mesh.is_winding_consistent) else "FAIL"
    print(f"    verify {name}: {status}  "
          f"boundary={b_count}  "
          f"winding={mesh.is_winding_consistent}  "
          f"watertight={mesh.is_watertight}  "
          f"vol={mesh.volume:.0f} mm³  "
          f"faces={len(mesh.faces):,}")
    return status == "PASS"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Process all four fuselage shells and export ring-frame profiles."""
    print("=== add_structural_features.py  Rev R1  2026-06-14 ===")

    processors = {
        "head":   process_head,
        "cargo":  process_cargo,
        "middle": process_middle,
        "rear":   process_rear,
    }

    # Ring-frame profile export: slice BEFORE modification (geometry unchanged at
    # those Y stations — ring pockets only affect a 2.5 mm Y slice).
    print("\n--- ring-frame inner-profile CSV export ---")
    cargo_mesh_raw = trimesh.load(SHELLS["cargo"], process=True)
    rear_mesh_raw  = trimesh.load(SHELLS["rear"],  process=True)
    _export_ring_profile(
        cargo_mesh_raw, 30.0,
        os.path.join(RING_CSV_DIR, "ring_cargo_Y30_inner.csv"),
    )
    _export_ring_profile(
        rear_mesh_raw, 290.0,
        os.path.join(RING_CSV_DIR, "ring_rear_Y290_inner.csv"),
    )

    results = {}
    for name, path in SHELLS.items():
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
        print("\nWARN: one or more shells failed verification — inspect before printing.")
        sys.exit(1)
    else:
        print("\nAll shells PASS manufacturing-watertight gate.")
        print("Run: python3 tools/bake_hull_frame.py --check  (to confirm HULL-FRAME R1 marker)")
        print("Slicer verification of feature positions is required before first print.")


if __name__ == "__main__":
    main()
