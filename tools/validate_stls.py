#!/usr/bin/env python3
"""
Simple STL validator for CI.
Checks that STL files in common directories can be loaded and are watertight.

Usage: python tools/validate_stls.py

This script is intentionally small and has minimal dependencies (trimesh).
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
    Path("airframe/stls/fuselage"),
    Path("airframe/stls/nacelles"),
    Path("airframe/stls/wings"),
]

EXTS = [".stl", ".STL"]

failures = []
found = 0

for base in SEARCH_PATHS:
    if not base.exists():
        continue
    for p in base.rglob("*"):
        if p.suffix in EXTS:
            found += 1
            try:
                mesh = trimesh.load_mesh(p, force='mesh')
                if mesh.is_empty:
                    print(f"ERROR: {p} loaded but is empty")
                    failures.append((p, "empty"))
                else:
                    if not mesh.is_watertight:
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

print(f"All {found} STL files passed watertight check (or are loadable).")
sys.exit(0)
