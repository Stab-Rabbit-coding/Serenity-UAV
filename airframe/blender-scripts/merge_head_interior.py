#!/usr/bin/env python3
"""
merge_head_interior.py — Rev R1d (2026-07-03)

Merge the bow sensor pod cuts (TODO.md §1.1.1.1a, `bow_sensor_pod.scad`
bow_pod_cuts()) into the published, already hull-frame-baked head shell
(airframe/stls/fuselage/head_shell24_2mm_repaired.stl).

Scope (deliberately narrow)
---------------------------
The head shell's joint-boss / bore-open-aft-face features are ALREADY merged
by add_structural_features.py's process_head() and that shell verifies clean
(no MESH-01 fragmentation on head — see TODO.md §1.1.1.0b). This script does
NOT redo that work; it starts from the current published (already-baked,
already-featured) head STL and adds ONLY the four bow-pod cuts:
  * bow_camera_cut  — 10 mm lens aperture + 20x20x21 mm interior body pocket
  * bow_tof_cut     — 8 mm aperture + 36x20x22 mm interior body pocket (rolled 90 deg)
  * bow_laser_cut   — 6 mm beam-exit aperture + 12.5 mm module bore + M3 set-screw hole
  * bow_face_seat   — shaves the two modeller camera bumps flat + 4x M2 insert pilot holes

All four cuts are unioned into ONE cutter solid and subtracted from the shell
in a SINGLE manifold3d boolean (closed-manifold-in / closed-manifold-out —
same robust pattern used by merge_cargo_interior.py to avoid the MESH-01
fragmentation class of defect).

Vera nose-mount bosses (head_shell24.scad vera_board_bosses()) are
DELIBERATELY EXCLUDED — those are explicitly flagged PROPOSED / not
FreeCAD-verified (see TODO.md §1.2c.3, avionics/kicad/Vera.md); merging them
here would falsely certify an unverified placement.  Likewise
book_dorsal_boss() (Shepherd's Book bay) is excluded — it carries a known,
not-yet-fixed legacy axis bug (see TODO.md §1.1.1.0a).

Coordinate handling
--------------------
bow_sensor_pod.scad's cut modules are authored directly in head_shell24.scad's
own LOCAL frame (identity-rotation bake per tools/bake_hull_frame.py
COMPONENTS["Head_Shell"] — local X/Y/Z axes already match hull X/Y/Z, offset
only).  Each cutter is built exactly as OpenSCAD builds it (primitive in its
own child frame -> inner translate([0,0,-(WALL_T+1)]) -> rotate(BOW_ROT) ->
translate(pos)), then the whole cutter union receives the ONE remaining step,
+ BAKE_T, to land in hull frame — matching tools/bake_hull_frame.py exactly.

Ref: TODO.md §1.1.1.1a ("Merge bow_pod_cuts() into the canonical Blender head
shell" / "Re-run mesh validation after head shell regen" — both BLOCKS on
head printing); airframe/openscad/fuselage/bow_sensor_pod.scad (source of
truth for all cut geometry, read-only, not re-derived here);
tools/verify_bow_pod.py (skin-landing verification, already PASS on these
positions prior to cutting).
"""

import os
import struct

import numpy as np
import trimesh
from manifold3d import Manifold, Mesh

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
HEAD_PATH = os.environ.get("HEAD_MERGE_OUT") or os.path.join(
    REPO_ROOT, "airframe", "stls", "fuselage", "head_shell24_2mm_repaired.stl"
)

MARKER = b"SerenityUAV HULL-FRAME R1"

# Head_Shell bake transform — MUST match tools/bake_hull_frame.py COMPONENTS
# ("Head: identity rotation ... STL axes already matched the hull frame.")
BAKE_T = np.array([-331.9993360, -17.9999640, 60.9998780])

# CF-PETG mass reporting (same convention as merge_cargo_interior.py)
RHO_PRINT = 1.05e-3  # g/mm^3 (as-printed, 4 perimeters + >=40% infill)
RHO_SOLID = 1.28e-3  # g/mm^3 (fully dense)

# ---------------------------------------------------------------------------
# bow_sensor_pod.scad constants (read-only mirror — see that file for the
# authoritative source and citations; values copied verbatim, not re-derived)
# ---------------------------------------------------------------------------
WALL_T = 3.5  # mm, SCAD cutter-overlap reference (real mesh wall is 2.0 mm;
# all cuts overshoot both faces by >=1 mm so this discrepancy
# does not affect correctness)

BOW_ROT_DEG = 130.0  # rotate([130,0,0]) — camera/ToF/faceplate-seat axis
LASER_ROT_DEG = 130.0  # rotate([130,0,0]) — laser axis (same as BOW_ROT)

CAM_POS = np.array([170.80, -282.68, 55.01])
CAM_APER_D = 10.0
CAM_BODY_W, CAM_BODY_H, CAM_BODY_D = 20.0, 20.0, 21.0

TOF_POS = np.array([154.33, -282.98, 55.61])
TOF_BODY_ROLL_DEG = 90.0
TOF_APER_D = 8.0
TOF_BODY_X, TOF_BODY_Y, TOF_BODY_D = 36.0, 20.0, 22.0

LASER_POS = np.array([161.33, -281.94, 56.14])
LASER_EXIT_D = 6.0
LASER_BORE_D, LASER_BORE_L = 12.5, 38.0
LASER_SETSCR_D, LASER_SETSCR_OFST = 3.2, 20.0

FACEPLATE_CTR = np.array([162.15, -282.53, 55.59])
FACEPLATE_W, FACEPLATE_H = 29.0, 17.0
SEAT_CLEAR = 6.0
FP_INS_D, FP_INS_DEP = 3.0, 6.0
FP_INS_X, FP_INS_Y = 11.0, 6.0


# ---------------------------------------------------------------------------
# manifold3d helpers (same convention as merge_cargo_interior.py)
# ---------------------------------------------------------------------------


def to_man(tm):
    return Manifold(
        Mesh(
            vert_properties=tm.vertices.astype(np.float32),
            tri_verts=tm.faces.astype(np.uint32),
        )
    )


def from_man(man):
    msh = man.to_mesh()
    return trimesh.Trimesh(
        vertices=np.asarray(msh.vert_properties, dtype=np.float64)[:, :3],
        faces=np.asarray(msh.tri_verts, dtype=np.int64),
        process=False,
    )


def union_all(meshes):
    acc = None
    for m in meshes:
        mm = to_man(m)
        acc = mm if acc is None else (acc + mm)
    return acc


def rot_x(deg):
    """3x3 rotation matrix for OpenSCAD's rotate([deg, 0, 0])."""
    a = np.radians(deg)
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def cyl_z(d, z0, z1, sections=48):
    """OpenSCAD-style cylinder(h=z1-z0, d=d) sitting at z in [z0, z1]."""
    c = trimesh.creation.cylinder(radius=d / 2.0, height=(z1 - z0), sections=sections)
    c.apply_translation([0, 0, (z0 + z1) / 2.0])
    return c


def box_corner(x0, y0, z0, dx, dy, dz):
    """OpenSCAD-style cube([dx,dy,dz]) placed with its low corner at (x0,y0,z0)."""
    b = trimesh.creation.box(extents=[dx, dy, dz])
    b.apply_translation([x0 + dx / 2.0, y0 + dy / 2.0, z0 + dz / 2.0])
    return b


def place(local_children, pos, rot_deg_x, roll_deg_z=0.0):
    """
    Apply the SCAD wrapper `translate(pos) rotate([rot_deg_x,0,0]) rotate([0,0,roll_deg_z])`
    to a list of child meshes already built in the module's own local frame
    (i.e. already including the module's inner translate([0,0,-(WALL_T+1)])).
    Returns hull-frame meshes (BAKE_T applied).
    """
    Rx = rot_x(rot_deg_x)
    a = np.radians(roll_deg_z)
    Rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    out = []
    for m in local_children:
        mm = m.copy()
        v = mm.vertices @ Rz.T  # roll about local Z first (innermost)
        v = v @ Rx.T  # then the module's own axis rotation
        v = v + pos  # then place at pos (head-local frame)
        v = v + BAKE_T  # then bake to hull frame
        mm.vertices = v
        out.append(mm)
    return out


# ---------------------------------------------------------------------------
# Build the four bow-pod cutter groups (mirrors bow_sensor_pod.scad exactly)
# ---------------------------------------------------------------------------


def build_camera_cut():
    z0 = -(WALL_T + 1)
    children = [
        cyl_z(CAM_APER_D, z0, z0 + WALL_T + 2),
        box_corner(
            -CAM_BODY_W / 2,
            -CAM_BODY_H / 2,
            z0 - CAM_BODY_D,
            CAM_BODY_W,
            CAM_BODY_H,
            CAM_BODY_D + 1,
        ),
    ]
    return place(children, CAM_POS, BOW_ROT_DEG)


def build_tof_cut():
    z0 = -(WALL_T + 1)
    children = [
        cyl_z(TOF_APER_D, z0, z0 + WALL_T + 2),
        box_corner(
            -TOF_BODY_X / 2,
            -TOF_BODY_Y / 2,
            z0 - TOF_BODY_D,
            TOF_BODY_X,
            TOF_BODY_Y,
            TOF_BODY_D + 1,
        ),
    ]
    return place(children, TOF_POS, BOW_ROT_DEG, roll_deg_z=TOF_BODY_ROLL_DEG)


def build_laser_cut():
    z0 = -(WALL_T + 1)
    exit_cyl = cyl_z(LASER_EXIT_D, z0, z0 + WALL_T + 2)
    bore_cyl = cyl_z(
        LASER_BORE_D, z0 - LASER_BORE_L, z0 - LASER_BORE_L + LASER_BORE_L + 0.1
    )
    # M3 lateral set-screw hole: rotate([0,90,0]) about local Y, centered,
    # at z = z0 - LASER_SETSCR_OFST -- axis becomes local X.
    setscr = trimesh.creation.cylinder(
        radius=LASER_SETSCR_D / 2.0, height=LASER_BORE_D + 4, sections=24
    )
    setscr.apply_transform(
        trimesh.transformations.rotation_matrix(np.pi / 2.0, [0, 1, 0])
    )
    setscr.apply_translation([0, 0, z0 - LASER_SETSCR_OFST])
    return place([exit_cyl, bore_cyl, setscr], LASER_POS, LASER_ROT_DEG)


def build_face_seat():
    z0 = -(WALL_T + 1)
    w, h = FACEPLATE_W, FACEPLATE_H
    children = [
        box_corner(-w / 2, -h / 2, z0 - 0.01, w, h, SEAT_CLEAR),
    ]
    for sx in (-1, 1):
        for sy in (-1, 1):
            ins = cyl_z(FP_INS_D, z0 - FP_INS_DEP, z0 - FP_INS_DEP + FP_INS_DEP + 0.5)
            ins.apply_translation([sx * FP_INS_X, sy * FP_INS_Y, 0])
            children.append(ins)
    return place(children, FACEPLATE_CTR, BOW_ROT_DEG)


# ---------------------------------------------------------------------------
# Cleanup / verification (mirrors merge_cargo_interior.py / the middle-shell
# nondegenerate-face fix used in this session's MESH-01 work)
# ---------------------------------------------------------------------------


def keep_largest_body(tm):
    """Drop disconnected boolean-artifact fragments (e.g. a thin sliver where
    two cutter bores graze each other), keeping only the main shell body.
    The head shell is a single printed part -- any second/third component
    after these through-cuts is debris, not an intended separate piece."""
    comps = trimesh.graph.connected_components(
        tm.face_adjacency, nodes=np.arange(len(tm.faces))
    )
    if len(comps) <= 1:
        return tm, 0
    sizes = [len(c) for c in comps]
    biggest = comps[int(np.argmax(sizes))]
    dropped = len(comps) - 1
    kept = tm.submesh([biggest], append=True)
    return kept, dropped


def nondegenerate_faces(tm):
    tris = tm.vertices[tm.faces]
    e1 = tris[:, 1, :] - tris[:, 0, :]
    e2 = tris[:, 2, :] - tris[:, 0, :]
    area2 = np.linalg.norm(np.cross(e1, e2), axis=1)
    keep = area2 > 1e-9
    if keep.all():
        return tm
    return trimesh.Trimesh(vertices=tm.vertices, faces=tm.faces[keep], process=False)


def stamp_export(mesh, out_path):
    count = len(mesh.faces)
    tris = mesh.vertices[mesh.faces]
    e1 = tris[:, 1, :] - tris[:, 0, :]
    e2 = tris[:, 2, :] - tris[:, 0, :]
    normals = np.cross(e1, e2)
    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    safe = np.where(lengths > 0.0, lengths, 1.0)
    normals = np.where(lengths > 0.0, normals / safe, 0.0)
    rec_dtype = np.dtype([("data", "<f4", (12,)), ("attr", "<u2")])
    rec = np.zeros(count, dtype=rec_dtype)
    rec["data"][:, 0:3] = normals.astype("<f4")
    rec["data"][:, 3:12] = tris.reshape(count, 9).astype("<f4")
    header = (MARKER + b" Head_Shell bow-pod-merge 2026-07-03")[:80].ljust(80, b"\0")
    with open(out_path, "wb") as fh:
        fh.write(header)
        fh.write(struct.pack("<I", count))
        fh.write(rec.tobytes())


def verify(mesh, label):
    ec = np.bincount(mesh.edges_unique_inverse, minlength=len(mesh.edges_unique))
    boundary = int((ec == 1).sum())
    nonman = int((ec > 2).sum())
    wt = mesh.is_watertight
    wind = mesh.is_winding_consistent
    vol = mesh.volume
    bodies = len(
        trimesh.graph.connected_components(
            mesh.face_adjacency, nodes=np.arange(len(mesh.faces))
        )
    )
    print(f"\n=== verify ({label}) ===")
    print(
        f"  faces={len(mesh.faces):,}  bodies={bodies}  "
        f"watertight={wt}  winding={wind}"
    )
    print(f"  boundary_edges={boundary}  nonmanifold_edges={nonman}")
    print(
        f"  volume={vol:.0f} mm^3  "
        f"mass={vol * RHO_PRINT:.1f} g (as-printed) .. "
        f"{vol * RHO_SOLID:.1f} g (solid CF-PETG)"
    )
    ok = wt and wind and boundary == 0 and nonman == 0 and vol > 0
    print(f"  RESULT: {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    print("=== merge_head_interior.py  Rev R1d  2026-07-03 ===")
    print(f"target (already baked, already boss/aft-face featured): {HEAD_PATH}")

    shell = trimesh.load(HEAD_PATH, process=False)
    shell.merge_vertices()
    print(
        f"pre-cut: faces={len(shell.faces):,} volume={shell.volume:.0f} mm^3 "
        f"watertight={shell.is_watertight}"
    )

    cutters = []
    cutters += build_camera_cut()
    cutters += build_tof_cut()
    cutters += build_laser_cut()
    cutters += build_face_seat()
    print(f"built {len(cutters)} cutter primitives (camera+ToF+laser+face-seat)")

    cutter_union = union_all(cutters)
    shell_man = to_man(shell)
    result_man = shell_man - cutter_union
    result = from_man(result_man)
    result = nondegenerate_faces(result)
    result.remove_unreferenced_vertices()
    result, dropped = keep_largest_body(result)
    if dropped:
        print(
            f"  dropped {dropped} disconnected boolean-artifact fragment(s) "
            f"(kept the main shell body only)"
        )
    result.remove_unreferenced_vertices()

    ok = verify(result, "head shell + bow-pod cuts")
    if not ok:
        print("\nREFUSING to overwrite the published STL — result failed verification.")
        print("(no-fabrication policy: an honest failure beats a silently-broken mesh)")
        raise SystemExit(1)

    stamp_export(result, HEAD_PATH)
    print(f"\nwrote {HEAD_PATH}")
    print(
        "Marker preserved: SerenityUAV HULL-FRAME R1 (identity-rotation bake, "
        "no re-bake needed -- only booleans were applied)."
    )


if __name__ == "__main__":
    main()
