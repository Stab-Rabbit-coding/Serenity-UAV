#!/usr/bin/env python3
"""
bake_hull_frame.py — bake validated FreeCAD placements into STL files.

Revision: R1 (2026-06-11)

Purpose
-------
As of Rev R1 the project standardises every 3D artifact on the single
empirically validated hull-frame coordinate system (see CLAUDE.md,
"FreeCAD Assembly Coordinate System"):

    X  positive port (left)
    Y  positive aft (back)
    Z  positive dorsal (up)
    Origin: the SerenityAssembly.FCStd world origin.

This tool applies each component's validated FreeCAD placement
(rotation quaternion + translation, extracted from
airframe/freecad/assembly/SerenityAssembly.FCStd, 2026-06-10) directly
to the STL vertex data, so the published STL coordinates ARE hull-frame
coordinates.  After baking, the FreeCAD assembly loads every component
with an identity placement and no per-part recalculation is needed.

Pipeline rule (Rev R1 onward)
-----------------------------
Generator scripts (OpenSCAD / Blender) may model parts in a convenient
part-local frame, but any STL published to airframe/stls/ for one of
the components listed in COMPONENTS below MUST be passed through this
tool after regeneration:

    python3 tools/bake_hull_frame.py            # bake all components
    python3 tools/bake_hull_frame.py Head_Shell # bake one component
    python3 tools/bake_hull_frame.py --check    # report state, no write

Idempotence / safety
--------------------
Output is always binary STL.  The 80-byte binary header is stamped with
the marker "SerenityUAV HULL-FRAME R1"; a file whose header already
carries the marker is skipped, so the transform can never be applied
twice.  ASCII STL input (OpenSCAD export) is converted to binary on
bake.  Bounding boxes are printed before and after baking, and the
written file is re-read and verified against the in-memory result.

Quaternion convention matches FreeCAD App.Rotation: (Qx, Qy, Qz, Qw)
with Qw the scalar; vertices map as v' = R(q) @ v + P.  The
quaternion-to-matrix expansion follows Shoemake, "Animating rotation
with quaternion curves", SIGGRAPH 1985 (standard form).

Binary STL layout per the 3D Systems STL specification (1989):
80-byte header, uint32 triangle count, then 50 bytes per triangle
(normal 3f, vertices 9f, uint16 attribute byte count).

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
"""

import argparse
import os
import struct
import sys

import numpy as np

# ---------------------------------------------------------------------------
# Path setup — resolved relative to this script so it works from any CWD.
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
STL_DIR = os.path.join(REPO_ROOT, "airframe", "stls")

# Marker stamped into the 80-byte binary STL header after baking.
# Its presence means "vertices are already hull-frame" — do not re-bake.
MARKER = b"SerenityUAV HULL-FRAME R1"

# 1/sqrt(2), shared by all 90-degree-family quaternions below.
_SQ2 = 0.7071067811865476

# ---------------------------------------------------------------------------
# Validated placement constants — single source of truth.
#
# Extracted from airframe/freecad/assembly/SerenityAssembly.FCStd
# (manually positioned and validated 2026-06-10; previously duplicated
# in serenity_assembly.py as PL_* constants, retired at R1).
#
# Tuple format: (Px, Py, Pz, Qx, Qy, Qz, Qw)
#   Position in mm; rotation as unit quaternion with Qw the scalar.
# ---------------------------------------------------------------------------
COMPONENTS = {
    # Head: identity rotation — STL axes already matched the hull frame.
    # Paths standardised to the no-"s_"-prefix published basenames (Rev R1,
    # 2026-06-11): the regenerated watertight 2 mm shells from
    # blender_shells_2mm_solidify.py + hollow_manifold.py are published under
    # these names.  The duplicate "Cargo_Shell_Repair2" entry was consolidated
    # into the single Cargo_Shell below (per the TODO.md mesh-repair log).
    "Head_Shell": (
        "fuselage/head_shell24_2mm_repaired.stl",
        (-331.9993360, -17.9999640, 60.9998780, 0.0, 0.0, 0.0, 1.0),
    ),
    # Cargo: 180 deg about +Z flips the section hull-forward.
    "Cargo_Shell": (
        "fuselage/cargo/cargo_sect_shell24_2mm_repaired.stl",
        (-274.4000100, -282.8000440, 0.0, 0.0, 0.0, 1.0, 0.0),
    ),
    # Middle / Rear: 90 deg about -X brings the SCAD section axis
    # (modelled along local Z) upright into hull +Z (dorsal).
    "Middle_Shell": (
        "fuselage/middle_shell24_2mm_repaired.stl",
        (-350.9992980, 130.4001963, 10.0174324, -_SQ2, 0.0, 0.0, _SQ2),
    ),
    "Rear_Shell": (
        "fuselage/rear_shell24_2mm_repaired.stl",
        (0.0, 203.1999999, -31.9999360, -_SQ2, 0.0, 0.0, _SQ2),
    ),
    # Wings: identity rotation, translation only.
    # Filenames use the no-"s_"-prefix convention (Rev R1, 2026-06-11).
    # Chord updated to 129/93 mm (root/tip) and LE sweep zeroed in Rev R1
    # 2026-06-14; bake translation unchanged (LE root stays at hull Y=-7).
    "Wing_Port": (
        "wings/wing_port_s1223_revo.stl",
        (-80.9998380, -6.9999860, 57.9998840, 0.0, 0.0, 0.0, 1.0),
    ),
    "Wing_Stbd": (
        "wings/wing_stbd_s1223_revo.stl",
        (-261.9994760, -11.9999760, 57.9998840, 0.0, 0.0, 0.0, 1.0),
    ),
    # Nacelles: 270 deg about +X = cruise / forward-flight attitude.
    # This is the canonical stored attitude; hover tilt is applied
    # about the pivot (Z = PIVOT_Z = 111.5 mm from intake, the full-assembly
    # CG station — see nacelle_pod_50mm_tandem.scad) downstream, not here.
    #
    # nacelle_port_revs.stl — port side (hull +X, Px ≈ +47 mm).
    #   SWIRL_DIR=−1 (CCW from intake); harness exit on −X (inboard) face.
    # nacelle_stbd_revs.stl — starboard side (hull −X, Px ≈ −385 mm).
    #   SWIRL_DIR=+1 (CW from intake); harness exit on +X (inboard) face.
    #
    # NOTE: filenames were corrected 2026-06-11 (Rev R1 nacelle-swap).
    # The original SCAD output used "port" for the NACELLE_SIDE=+1 (right
    # outer shell, harness on +X face) part, which physically fits starboard.
    # Files were renamed so each filename matches its physical mounting side.
    "Nacelle_Port": (
        "nacelles/nacelle_port_revs.stl",
        (46.9999060, -63.9998720, 62.9998740, _SQ2, 0.0, 0.0, -_SQ2),
    ),
    "Nacelle_Stbd": (
        "nacelles/nacelle_stbd_revs.stl",
        (-385.0960040, -69.9998600, 64.9719300, _SQ2, 0.0, 0.0, -_SQ2),
    ),
}


def quat_to_matrix(qx, qy, qz, qw):
    """
    Return the 3x3 rotation matrix for unit quaternion (qx, qy, qz, qw).

    Standard expansion (Shoemake 1985); matches FreeCAD App.Rotation.
    The quaternion is normalised first to guard against drift in the
    recorded constants.
    """
    norm = np.sqrt(qx * qx + qy * qy + qz * qz + qw * qw)
    qx, qy, qz, qw = qx / norm, qy / norm, qz / norm, qw / norm
    return np.array(
        [
            [
                1.0 - 2.0 * (qy * qy + qz * qz),
                2.0 * (qx * qy - qz * qw),
                2.0 * (qx * qz + qy * qw),
            ],
            [
                2.0 * (qx * qy + qz * qw),
                1.0 - 2.0 * (qx * qx + qz * qz),
                2.0 * (qy * qz - qx * qw),
            ],
            [
                2.0 * (qx * qz - qy * qw),
                2.0 * (qy * qz + qx * qw),
                1.0 - 2.0 * (qx * qx + qy * qy),
            ],
        ],
        dtype=np.float64,
    )


def is_baked(path):
    """Return True if the file's binary header carries the bake marker."""
    with open(path, "rb") as fh:
        header = fh.read(80)
    return MARKER in header


def read_stl(path):
    """
    Read an STL file (binary or ASCII) and return triangle vertices.

    Returns a float64 array of shape (N, 3, 3) — facet normals are
    discarded here and recomputed from vertex winding on write.
    """
    with open(path, "rb") as fh:
        data = fh.read()

    # Binary detection: an ASCII STL starts with "solid", but so can a
    # mis-labelled binary file.  Trust the declared triangle count: the
    # file is binary iff its size matches 84 + 50 * count exactly.
    if len(data) >= 84:
        count = struct.unpack_from("<I", data, 80)[0]
        if len(data) == 84 + 50 * count:
            rec = np.frombuffer(data, dtype=np.uint8, offset=84).reshape(count, 50)
            # First 48 bytes per record: 12 little-endian float32
            # (facet normal + 3 vertices); last 2: attribute count.
            floats = np.ascontiguousarray(rec[:, :48]).view("<f4")
            floats = floats.reshape(count, 4, 3)
            return floats[:, 1:4, :].astype(np.float64)

    # ASCII fallback: collect every "vertex x y z" line in file order.
    verts = []
    for line in data.decode("ascii", errors="replace").splitlines():
        line = line.strip()
        if line.startswith("vertex"):
            parts = line.split()
            verts.append([float(parts[1]), float(parts[2]), float(parts[3])])
    arr = np.asarray(verts, dtype=np.float64)
    if arr.size == 0 or arr.shape[0] % 3 != 0:
        raise ValueError(f"{path}: unable to parse as ASCII STL")
    return arr.reshape(-1, 3, 3)


def write_stl_binary(path, tris, header):
    """
    Write tris (N, 3, 3) as a binary STL with the given header bytes.

    Facet normals are recomputed from the (preserved) counter-clockwise
    vertex winding; degenerate facets get a zero normal, which slicers
    recompute themselves per common STL practice.
    """
    count = tris.shape[0]
    edge1 = tris[:, 1, :] - tris[:, 0, :]
    edge2 = tris[:, 2, :] - tris[:, 0, :]
    normals = np.cross(edge1, edge2)
    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    # Guard divide-by-zero on degenerate (zero-area) facets.
    safe = np.where(lengths > 0.0, lengths, 1.0)
    normals = np.where(lengths > 0.0, normals / safe, 0.0)

    # Structured dtype packs to exactly 50 bytes per record (numpy does
    # not pad structured dtypes unless align=True is requested).
    rec_dtype = np.dtype([("data", "<f4", (12,)), ("attr", "<u2")])
    assert rec_dtype.itemsize == 50, "unexpected STL record padding"
    rec = np.zeros(count, dtype=rec_dtype)
    rec["data"][:, 0:3] = normals.astype("<f4")
    rec["data"][:, 3:12] = tris.reshape(count, 9).astype("<f4")

    with open(path, "wb") as fh:
        fh.write(header[:80].ljust(80, b"\0"))
        fh.write(struct.pack("<I", count))
        fh.write(rec.tobytes())


def bbox_str(tris):
    """Return a compact 'min .. max' bounding-box string for tris."""
    lo = tris.reshape(-1, 3).min(axis=0)
    hi = tris.reshape(-1, 3).max(axis=0)
    return (
        f"X[{lo[0]:+9.3f} ..{hi[0]:+9.3f}] "
        f"Y[{lo[1]:+9.3f} ..{hi[1]:+9.3f}] "
        f"Z[{lo[2]:+9.3f} ..{hi[2]:+9.3f}]"
    )


def bake_component(name, check_only=False):
    """
    Bake one component's placement into its STL file.

    Returns one of: "baked", "already", "missing", "check".
    Raises on read/write/verify failure.
    """
    rel_path, placement = COMPONENTS[name]
    path = os.path.join(STL_DIR, rel_path)

    if not os.path.exists(path):
        print(f"[MISSING] {name}: {rel_path}")
        return "missing"

    if is_baked(path):
        print(f"[ALREADY] {name}: header carries '{MARKER.decode()}'")
        return "already"

    if check_only:
        print(f"[PENDING] {name}: {rel_path} not yet baked")
        return "check"

    px, py, pz, qx, qy, qz, qw = placement
    rot = quat_to_matrix(qx, qy, qz, qw)
    pos = np.array([px, py, pz], dtype=np.float64)

    tris = read_stl(path)
    print(f"[BAKE   ] {name}: {tris.shape[0]} facets")
    print(f"          before: {bbox_str(tris)}")

    # v' = R @ v + P applied to every vertex; einsum keeps the
    # (N, 3, 3) triangle structure intact.
    tris = np.einsum("ij,nkj->nki", rot, tris) + pos
    print(f"          after : {bbox_str(tris)}")

    header = MARKER + b" " + name.encode("ascii") + b" 2026-06-11"
    write_stl_binary(path, tris, header)

    # Verification: re-read the written file and confirm it matches the
    # in-memory result to float32 precision.
    verify = read_stl(path)
    if verify.shape != tris.shape:
        raise RuntimeError(f"{name}: facet count changed on write")
    err = np.abs(verify - tris).max()
    if err > 1.0e-3:
        raise RuntimeError(f"{name}: verify error {err:.6f} mm")
    print(f"          verify: re-read OK, max error {err:.2e} mm")
    return "baked"


def main():
    """CLI entry point — bake all or selected components."""
    parser = argparse.ArgumentParser(
        description="Bake validated hull-frame placements into STLs."
    )
    parser.add_argument(
        "components",
        nargs="*",
        metavar="COMPONENT",
        help="component names to bake (default: all); one of: " + ", ".join(COMPONENTS),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="report baked/pending state only; write nothing",
    )
    args = parser.parse_args()

    names = args.components or list(COMPONENTS)
    for name in names:
        if name not in COMPONENTS:
            parser.error(f"unknown component '{name}'")

    results = {}
    for name in names:
        results[name] = bake_component(name, check_only=args.check)

    missing = [n for n, r in results.items() if r == "missing"]
    if missing:
        print(f"\n{len(missing)} component STL(s) missing: " + ", ".join(missing))
        sys.exit(1)
    print("\nAll requested components processed.")


if __name__ == "__main__":
    main()
