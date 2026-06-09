#!/usr/bin/env python3
"""
STL validator for CI.
Checks that STL files in common directories can be loaded and are watertight.

A mesh passes if:
  - mesh.is_watertight is True, OR
  - every individual body (mesh.split()) is watertight.

The second condition correctly handles multi-body assembly meshes (e.g. four
landing feet as one STL, or a nacelle assembly) where each sub-solid is closed
but trimesh's global winding check fails on the combined file.

Duplicate sub-paths have been removed: airframe/stls rglob already covers all
fuselage/, nacelles/, and wings/ subdirectories.

Usage: python tools/validate_stls.py
"""

from pathlib import Path
import sys

try:
    import trimesh
except Exception as e:
    print("Missing dependency 'trimesh'. Install requirements-dev.txt before running.")
    raise

SEARCH_PATHS = [
    Path("airframe/stls"),
    Path("stls"),
]

EXTS = [".stl", ".STL"]


def is_mesh_valid(mesh):
    """
    Return True if mesh is watertight globally, or all split bodies are watertight.
    A mesh with 0 bodies (non-manifold, unsplittable) fails.
    Raises RuntimeError if graph engines are unavailable (networkx not installed).
    """
    if mesh.is_watertight:
        return True
    try:
        bodies = mesh.split()
    except Exception as e:
        if "graph engines" in str(e).lower():
            raise RuntimeError(
                "mesh.split() requires networkx — add it to requirements-dev.txt"
            ) from e
        raise
    if not bodies:
        return False
    return all(b.is_watertight for b in bodies)


seen = set()
failures = []
found = 0

for base in SEARCH_PATHS:
    if not base.exists():
        continue
    for p in base.rglob("*"):
        if p.suffix not in EXTS:
            continue
        resolved = p.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        found += 1
        try:
            mesh = trimesh.load_mesh(p, force='mesh')
            if mesh.is_empty:
                print(f"ERROR: {p} loaded but is empty")
                failures.append((p, "empty"))
            elif not is_mesh_valid(mesh):
                print(f"WARNING: {p} is not watertight")
                failures.append((p, "not_watertight"))
        except Exception as e:
            print(f"ERROR: failed to load {p}: {e}")
            failures.append((p, str(e)))

if found == 0:
    print("No STL files found in common locations — skipping STL checks.")
    sys.exit(0)

if failures:
    print(f"\nSTL validation found {len(failures)} problem(s)")
    for p, reason in failures:
        print(f" - {p}: {reason}")
    sys.exit(2)

print(f"All {found} STL files passed watertight check.")
sys.exit(0)
