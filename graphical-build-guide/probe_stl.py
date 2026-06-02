#!/usr/bin/env python3
"""
probe_stl.py — Report bounding boxes and triangle counts for Serenity hull STL files.
Used to calibrate the gen_hull_outlines.py SVG generator.

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0
"""

import struct
import os

STL_DIR = "/home/user/Serenity-UAV/thingverse-serenity/files-hollowed-18in"

FILES = [
    "s_head_shell24.stl",
    "s_middle_shell24.stl",
    "s_rear_shell24.stl",
    "s_cargo_sect_shell24.stl",
    "s_wings_both_shell24.stl",
    "s_eng_left_shell24_50mm.stl",
    "s_eng_right_shell24_50mm.stl",
    "s_eng_left_stator_shell24_50mm.stl",
    "nacelle_nozzle_ring.stl",
    "rear_nozzle_frame.stl",
]

def read_stl_verts(path):
    """Read all triangle vertices from a binary STL file."""
    verts = []
    with open(path, "rb") as f:
        f.read(80)  # header
        n_tri = struct.unpack("<I", f.read(4))[0]
        for _ in range(n_tri):
            f.read(12)  # normal
            for _ in range(3):
                x, y, z = struct.unpack("<fff", f.read(12))
                verts.append((x, y, z))
            f.read(2)  # attrib
    return verts

for fname in FILES:
    path = os.path.join(STL_DIR, fname)
    if not os.path.exists(path):
        print(f"  MISSING: {fname}")
        continue
    verts = read_stl_verts(path)
    if not verts:
        print(f"  EMPTY: {fname}")
        continue
    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    zs = [v[2] for v in verts]
    print(f"{fname}:")
    print(f"  tris={len(verts)//3:,}  verts={len(verts):,}")
    print(f"  X: {min(xs):8.2f} .. {max(xs):8.2f}  range={max(xs)-min(xs):.2f}")
    print(f"  Y: {min(ys):8.2f} .. {max(ys):8.2f}  range={max(ys)-min(ys):.2f}")
    print(f"  Z: {min(zs):8.2f} .. {max(zs):8.2f}  range={max(zs)-min(zs):.2f}")
    print()
