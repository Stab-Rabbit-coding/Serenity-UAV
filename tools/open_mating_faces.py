#!/usr/bin/env python3
# ============================================================================
# HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
#   Hull frame: X=+port, Y=+aft, Z=+dorsal; origin = SerenityAssembly world.
#
#   open_mating_faces.py  (2026-07-27)
#   --------------------------------------------------------------------------
#   Open the CAPPED fuselage-section mating faces so the internal splice collars
#   (generate_conforming_collars.py) can actually be installed and bond into an
#   open bore, as the design requires ("the four fuselage sections are open-ended
#   tubes joined by internal splice collars" — merge_cargo_interior.py / CLAUDE.md).
#
#   Why this is needed
#   --------------------------------------------------------------------------
#   The Blender source shells are CLOSED-capped at each fabrication-split face.
#   merge_cargo_interior.py opens cargo's faces and regen_rear_interior.py opens
#   rear's; add_structural_features.process_head/process_middle are SUPPOSED to
#   open head-aft / middle-fwd with a half-space _flat_face_cutter, but on the
#   published shells those closures END AT the mating plane, so the half-space cut
#   is a no-op and the cap survives.  Verified 2026-07-27 (mesh.contains + section
#   scans) that HEAD aft (hull Y≈-71.2) and MIDDLE fwd (hull Y≈+131.0) were still
#   capped, while cargo, rear, and middle-aft are open.  A capped face both blocks
#   collar installation and shows up as a full-cross-section disk in collar∩shell.
#
#   Two cap shapes ⇒ two methods
#   --------------------------------------------------------------------------
#   * MIDDLE fwd is a THIN FLAT MEMBRANE at the section's Y-extreme (the bore is
#     full-size right up to the face).  A half-space cut has nothing beyond the
#     face to remove, so we subtract a CAVITY PLUG — the inner-wall contour at a
#     clean station, grown a hair, extruded across the membrane — which removes
#     the membrane inside the bore footprint while leaving the 2 mm wall rim and
#     the face location unchanged.
#   * HEAD aft is a ROUNDED CLOSURE whose bore NECKS toward the tip (inner area
#     7815→6713 mm² over the last ~6 mm) and is sealed by a thin single-loop
#     membrane at Y≈-72.0..-72.5.  A plug sized to the deep bore over-cuts the
#     necked near-face wall, so instead we FLAT-CUT at the first station whose
#     bore is genuinely open (2 loops, inner > MIN_BORE): the whole rounded
#     closure beyond that plane is removed, leaving a clean full-bore open face.
#     The mate plane therefore moves inboard to that station (reported below; the
#     collar generator's JOINTS face for this joint is set to match).
#
#   Boolean of closed manifolds ⇒ still watertight (an open-ended thick tube is
#   watertight like a length of pipe).  The HULL-FRAME marker is re-stamped so
#   tools/bake_hull_frame.py still skips the file.  Idempotent: a face already
#   open (mesh.contains False just inside) is skipped.
#
# Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  (design)
# AI-assist: Claude Opus 4.8 (Anthropic) — cavity-plug / flat-cut face opener.
# License: CC BY 4.0 - creativecommons.org/licenses/by/4.0
# ============================================================================
"""Open the capped head-aft and middle-fwd fuselage mating faces."""

import os
import struct
import sys

import numpy as np
import trimesh
from manifold3d import Manifold, Mesh
from shapely.geometry import Polygon

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FUS = os.path.join(REPO, "airframe", "stls", "fuselage")
MARKER = b"SerenityUAV HULL-FRAME R1"
CAVITY_FLOOR = 1000.0  # mm^2 — ignore section loops smaller than a real bore
MIN_BORE = 3000.0      # mm^2 — a station's 2nd loop must exceed this to count "open"
PLUG_GROW = 0.5        # mm — grow the plug past the bore so the whole membrane goes
SCAN_STEP = 0.25       # mm — flat-cut open-station scan pitch

# (component, file, method, mate_face_Y, keep_sign, station_or_clean)
#   keep_sign +1: section occupies Y > face ;  -1: section occupies Y < face
#   method "plug":     station_or_clean = clean inner-cavity sample Y
#   method "flatcut":  station_or_clean = ignored (open station auto-detected)
FACES = [
    ("Head_Shell",   "head_shell24_2mm_repaired.stl", "flatcut", -71.2, -1, None),
    ("Middle_Shell", "middle_shell24_2mm_repaired.stl", "plug",  131.0, +1, 136.0),
]


def to_man(tm):
    return Manifold(Mesh(vert_properties=tm.vertices.astype(np.float32),
                         tri_verts=tm.faces.astype(np.uint32)))


def from_man(m):
    mm = m.to_mesh()
    out = trimesh.Trimesh(
        vertices=np.asarray(mm.vert_properties)[:, :3].astype(np.float64),
        faces=np.asarray(mm.tri_verts), process=False)
    out.merge_vertices()
    return out


def _loop_areas(mesh, y):
    s = mesh.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    out = []
    for loop in (s.discrete if s is not None else []):
        p = np.asarray(loop)[:, [0, 2]]
        x, z = p[:, 0], p[:, 1]
        out.append(0.5 * abs(np.dot(x, np.roll(z, -1)) - np.dot(z, np.roll(x, -1))))
    return sorted(out, reverse=True)


def inner_cavity(mesh, y):
    """2nd-largest section loop at station Y as a shapely (X,Z) Polygon."""
    s = mesh.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    polys = []
    for loop in (s.discrete if s is not None else []):
        p = Polygon(np.asarray(loop)[:, [0, 2]])
        if p.is_valid and p.area > CAVITY_FLOOR:
            polys.append(p.buffer(0))
    if len(polys) < 2:
        return None
    polys.sort(key=lambda p: p.area, reverse=True)
    return polys[1].simplify(0.4)


def is_capped(mesh, face_y, keep_sign):
    """True if the bore is solid 1 mm inside the mating face (cap present)."""
    cx, cz = mesh.vertices[:, 0].mean(), mesh.vertices[:, 2].mean()
    return bool(mesh.contains([[cx, face_y + keep_sign * 1.0, cz]])[0])


def first_open_station(mesh, face_y, keep_sign):
    """Scan inboard from the face; return the first Y whose bore is genuinely
    open (>=2 loops, 2nd loop > MIN_BORE)."""
    for k in range(1, 80):
        y = face_y + keep_sign * (SCAN_STEP * k)
        a = _loop_areas(mesh, y)
        if len(a) >= 2 and a[1] > MIN_BORE:
            return round(y, 3)
    return None


def _box(x0, x1, z0, z1, y0, y1):
    b = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    b.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
    return b


def open_flatcut(mesh, face_y, keep_sign):
    """Flat-cut the rounded closure off at the first open-bore station."""
    y_open = first_open_station(mesh, face_y, keep_sign)
    if y_open is None:
        return None, None
    b = mesh.bounds
    pad = 30.0
    if keep_sign < 0:  # keep Y < y_open ; remove Y > y_open
        cutter = _box(b[0][0] - pad, b[1][0] + pad, b[0][2] - pad, b[1][2] + pad,
                      y_open, b[1][1] + pad)
    else:              # keep Y > y_open ; remove Y < y_open
        cutter = _box(b[0][0] - pad, b[1][0] + pad, b[0][2] - pad, b[1][2] + pad,
                      b[0][1] - pad, y_open)
    return from_man(to_man(mesh) - to_man(cutter)), y_open


def open_plug(mesh, face_y, keep_sign, clean_y):
    """Subtract a cavity plug to remove a thin flat membrane at the face extreme."""
    cav = inner_cavity(mesh, clean_y)
    if cav is None:
        return None, None
    plug_poly = cav.buffer(PLUG_GROW).simplify(0.4)
    y0, y1 = (face_y - 0.6, face_y + 2.6) if keep_sign > 0 else (face_y - 2.6, face_y + 0.6)
    ex = trimesh.creation.extrude_polygon(plug_poly, height=y1 - y0)
    ex.apply_transform(np.array(
        [[1, 0, 0, 0], [0, 0, 1, y0], [0, 1, 0, 0], [0, 0, 0, 1.0]]))
    return from_man(to_man(mesh) - to_man(ex)), face_y


def stamp_export(mesh, path, comp):
    tris = mesh.vertices[mesh.faces]
    e1, e2 = tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0]
    n = np.cross(e1, e2)
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    n = np.where(ln > 0, n / np.where(ln > 0, ln, 1.0), 0.0)
    rec = np.zeros(len(mesh.faces), dtype=np.dtype([("d", "<f4", (12,)), ("a", "<u2")]))
    rec["d"][:, 0:3] = n.astype("<f4")
    rec["d"][:, 3:12] = tris.reshape(len(mesh.faces), 9).astype("<f4")
    header = (MARKER + f" {comp} mating-face-open 2026-07-27".encode())[:80].ljust(80, b"\0")
    with open(path, "wb") as fh:
        fh.write(header)
        fh.write(struct.pack("<I", len(mesh.faces)))
        fh.write(rec.tobytes())


def main():
    all_ok = True
    for comp, rel, method, face_y, keep_sign, station in FACES:
        path = os.path.join(FUS, rel)
        mesh = trimesh.load(path, process=False)
        mesh.merge_vertices()
        print(f"\n[{comp}] {rel}  face Y={face_y}  method={method}")
        if not is_capped(mesh, face_y, keep_sign):
            print("  already OPEN — skipped")
            continue
        if method == "flatcut":
            opened, new_face = open_flatcut(mesh, face_y, keep_sign)
        else:
            opened, new_face = open_plug(mesh, face_y, keep_sign, station)
        if opened is None:
            print("  ERROR: could not locate a clean open bore")
            all_ok = False
            continue
        opened.merge_vertices()
        ec = np.bincount(opened.edges_unique_inverse,
                         minlength=len(opened.edges_unique))
        bnd, nm = int((ec == 1).sum()), int((ec > 2).sum())
        bodies = len(opened.split(only_watertight=False))
        still_capped = is_capped(opened, new_face, keep_sign)
        bore = _loop_areas(opened, new_face + keep_sign * 0.5)
        wt = opened.is_watertight
        ok = wt and bnd == 0 and nm == 0 and bodies == 1 and not still_capped
        print(f"  vol {mesh.volume:.0f} -> {opened.volume:.0f} mm^3  "
              f"faces={len(opened.faces)}  new_face_Y={new_face}")
        print(f"  open bore just inside: {[round(v) for v in bore[:2]]} mm^2")
        print(f"  watertight={wt} bodies={bodies} boundary={bnd} nonman={nm} "
              f"still_capped={still_capped}  -> {'PASS' if ok else 'FAIL'}")
        if ok:
            stamp_export(opened, path, comp)
            print(f"  written + re-stamped -> {rel}")
        else:
            all_ok = False
            print("  NOT written (verification failed)")
    print(f"\n=== {'ALL FACES OPENED' if all_ok else 'REVIEW NEEDED'} ===")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
