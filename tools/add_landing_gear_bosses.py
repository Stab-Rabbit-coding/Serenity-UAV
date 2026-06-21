#!/usr/bin/env python3
"""Add 16 Rev R5 landing-gear hull boss sockets (4 per corner, one per wire)
to the baked Cargo_Shell outer skin.

This implements TODO.md LG-02 / docs/LANDING_GEAR_ANALYSIS.md SS4.7 against the
ALREADY-BAKED `cargo_sect_shell24_2mm_repaired.stl` (hull-frame coordinates,
"SerenityUAV HULL-FRAME R1" marker). Per CLAUDE.md, this mesh must never be
re-baked (no transform is applied here -- only new geometry is unioned/cut in
place, in the same hull-frame coordinates the file already carries).

Corner placement (X, Y reused from the validated Rev R1 single-leg socket
table in TODO.md; rotation 0/90/180/270 deg matching the established
Strong-Leg Union/Union001-003 corner scheme) is a first-pass estimate, NOT
yet confirmed in FreeCAD -- see TODO.md LG-10 (still open). Each computed
attachment point is snapped to the nearest point on the actual hull surface
before the boss is built, so the boss always sits flush on the real mesh
regardless of small placement-estimate error.

Output: airframe/stls/fuselage/cargo/cargo_sect_shell24_2mm_bossed.stl
(a NEW file -- the existing canonical *_repaired.stl is left untouched).
Per CLAUDE.md's Blender-pipeline-is-authoritative policy, this boss geometry
should eventually be folded back into the Blender source once LG-10
placement is finalized; this script provides a working, demonstrable
boss integration in the meantime.

Run: python3 tools/add_landing_gear_bosses.py
"""

import numpy as np
import trimesh

CARGO_DIR = "airframe/stls/fuselage/cargo"
INPUT_STL = f"{CARGO_DIR}/cargo_sect_shell24_2mm_repaired.stl"
OUTPUT_STL = f"{CARGO_DIR}/cargo_sect_shell24_2mm_bossed.stl"

LEAN_ANG = 24.0
AZ_SPLIT = 15.0
POST_MID_Z = 79.8 * 2.0 / 3.0
POST_TOP_Z = 79.8
SPRING_L = 45.0
DUCTILE_L = 30.0
HULL_ATTACH_Z = 44.0  # mm above cargo belly -- validated Rev R1 socket height

BOSS_OD = 10.0
BOSS_LEN = 24.0          # generous length -- robust overlap even where the
                          # local hull surface is sharply curved (e.g. near
                          # a chamfer), at the cost of embedding deeper than
                          # structurally necessary; refine once LG-10 placement
                          # is finalized and the real local curvature is known.
BOSS_EMBED = 14.0        # mm pushed into the shell (along the surface normal)
BORE_D = 5.5             # mm, wire-end clearance bore
BORE_DEPTH = 10.0        # mm

# (label, X, Y, corner Z-rotation deg) -- see module docstring
CORNERS = [
    ("fwd-port", -96.0, 2.0, 0.0),
    ("fwd-stbd", -242.0, 2.0, 90.0),
    ("aft-port", -96.0, 107.0, 180.0),
    ("aft-stbd", -242.0, 107.0, 270.0),
]

POST_ORIGIN_Z = HULL_ATTACH_Z - POST_TOP_Z


def branch_direction(az_deg):
    lean = np.radians(LEAN_ANG)
    az = np.radians(az_deg)
    v = np.array([np.sin(lean), 0, np.cos(lean)])
    rot_z = np.array([
        [np.cos(az), -np.sin(az), 0],
        [np.sin(az), np.cos(az), 0],
        [0, 0, 1],
    ])
    return rot_z @ v


def corner_transform(x, y, zrot_deg):
    zrot = np.radians(zrot_deg)
    rot = np.array([
        [np.cos(zrot), -np.sin(zrot), 0],
        [np.sin(zrot), np.cos(zrot), 0],
        [0, 0, 1],
    ])
    return rot, np.array([x, y, POST_ORIGIN_Z])


def attachment_points():
    """16 (label, far_point, wire_direction) tuples in hull frame."""
    out = []
    for label, x, y, zrot in CORNERS:
        rot, t = corner_transform(x, y, zrot)
        for branch_name, z_local, length in [("spring", POST_TOP_Z, SPRING_L), ("ductile", POST_MID_Z, DUCTILE_L)]:
            socket_world = rot @ np.array([0, 0, z_local]) + t
            for sign in (-1, 1):
                d_local = branch_direction(90 + sign * AZ_SPLIT)
                d_world = rot @ d_local
                far_point = socket_world + d_world * length
                out.append((f"{label}-{branch_name}-{'a' if sign < 0 else 'b'}", far_point, d_world))
    return out


def align_z_to(direction):
    direction = direction / np.linalg.norm(direction)
    return trimesh.geometry.align_vectors([0, 0, 1], direction)


def boss_geometry(center, normal, wire_dir):
    """A boss bump (cylinder along the local surface normal, embedded
    BOSS_EMBED into the shell) with a bore (cylinder along the wire's own
    approach direction, so the wire actually plugs in at the right angle).
    """
    boss = trimesh.creation.cylinder(radius=BOSS_OD / 2.0, height=BOSS_LEN, sections=32)
    boss.apply_transform(align_z_to(normal))
    boss_center = center + normal * (BOSS_LEN / 2.0 - BOSS_EMBED)
    boss.apply_translation(boss_center)

    bore = trimesh.creation.cylinder(radius=BORE_D / 2.0, height=BORE_DEPTH * 2.5, sections=24)
    bore.apply_transform(align_z_to(wire_dir))
    bore.apply_translation(center + wire_dir * (BORE_DEPTH * 0.3))

    return boss, bore


def main():
    print(f"Loading {INPUT_STL} ...", flush=True)
    mesh = trimesh.load(INPUT_STL)
    bodies = mesh.split()
    print(f"  {len(bodies)} bodies", flush=True)
    outer = max(bodies, key=lambda b: b.volume)
    inner = min(bodies, key=lambda b: b.volume)
    print(f"  outer: {len(outer.vertices)} verts, watertight={outer.is_watertight}", flush=True)

    points = attachment_points()
    targets = np.array([p[1] for p in points])
    closest, dist, tri_id = outer.nearest.on_surface(targets)
    normals = outer.face_normals[tri_id]

    result = outer
    for i, (label, _far_point, wire_dir) in enumerate(points):
        center = closest[i]
        normal = normals[i]
        boss, bore = boss_geometry(center, normal, wire_dir)
        print(f"[{i+1:2d}/16] {label:20s} dist_to_surface={dist[i]:5.1f}mm  unioning boss ...", flush=True)
        result = result.union(boss, engine="manifold")
        result = result.difference(bore, engine="manifold")

    # Defensive: a boss boolean op can occasionally fail to weld at a sharply
    # curved/chamfered patch of hull, leaving a small disconnected island
    # instead of a true union. Drop any such island and flag it loudly --
    # these need a second pass once LG-10 final placement is validated.
    result_bodies = result.split()
    if len(result_bodies) > 1:
        main_body = max(result_bodies, key=lambda b: len(b.vertices))
        for b in result_bodies:
            if b is not main_body:
                print(f"  [WARN] dropped a disconnected island near {b.bounds.tolist()} "
                      f"({len(b.vertices)} verts) -- a boss failed to weld there; "
                      f"needs a second pass after LG-10 placement is finalized.", flush=True)
        result = main_body

    print("Recombining with inner shell ...", flush=True)
    combined = trimesh.util.concatenate([result, inner])
    combined.export(OUTPUT_STL)
    print(f"Saved -> {OUTPUT_STL}", flush=True)
    print(f"Final: bodies={combined.body_count}, "
          f"outer watertight={result.is_watertight}, inner watertight={inner.is_watertight}", flush=True)


if __name__ == "__main__":
    main()
