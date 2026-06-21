#!/usr/bin/env python3
"""Build assembled / exploded / deformed demonstration STLs for the Rev R5
vertical-post + 4-wire-brace landing gear (2 spring wires at the apex branch,
2 ductile wires at the 1/3-down branch).

This is a SCHEMATIC illustration of the design described in
docs/LANDING_GEAR_ANALYSIS.md Rev R5, not a finalized hull-integrated
assembly: the hull boss is a simple placeholder cylinder (LG-02, the real
boss SCAD integration, is still open), and the canonical foot pad is
positioned under the post's foot point without a finalized socket detail.

Outputs (airframe/stls/fuselage/landing-gear/):
    landing_gear_assembled.stl   -- post + foot + 2 spring wires (apex) +
                                     2 ductile wires (1/3-down) + 4 boss
                                     placeholders, in correct relative
                                     position, all wires nominal.
    landing_gear_exploded.stl    -- same parts, separated along each part's
                                     local insertion axis for visual clarity.
    landing_gear_deformed.stl    -- same as assembled, but the ductile wires
                                     are swapped for the fired/flattened
                                     variant, showing the post-overload state
                                     (spring pair still nominal/intact).

Run: python3 tools/build_landing_gear_views.py
"""

import numpy as np
import trimesh

GEAR_DIR = "airframe/stls/fuselage/landing-gear"

LEAN_ANG = 24.0   # deg from vertical
AZ_SPLIT = 15.0   # deg, +/- within each pair
POST_MID_Z = 79.8 * 2.0 / 3.0   # 1/3-down branch height (ductile pair)
POST_TOP_Z = 79.8                # apex branch height (spring pair)
SPRING_L = 45.0
DUCTILE_L = 30.0

BOSS_OD = 13.0
BOSS_LEN = 12.0
EXPLODE_OFFSET = 25.0


def branch_direction(az_deg):
    """Unit vector for a branch bored at LEAN_ANG from vertical (+Z), at
    azimuth az_deg measured the same way OpenSCAD's rotate([0, LEAN_ANG, az])
    applies it to the +Z axis.
    """
    lean = np.radians(LEAN_ANG)
    az = np.radians(az_deg)
    # Equivalent to rotating +Z by LEAN_ANG about Y then by az about Z.
    v = np.array([np.sin(lean), 0, np.cos(lean)])
    rot_z = np.array([
        [np.cos(az), -np.sin(az), 0],
        [np.sin(az), np.cos(az), 0],
        [0, 0, 1],
    ])
    return rot_z @ v


def align_z_to(direction):
    direction = direction / np.linalg.norm(direction)
    return trimesh.geometry.align_vectors([0, 0, 1], direction)


def boss_placeholder():
    return trimesh.creation.cylinder(radius=BOSS_OD / 2.0, height=BOSS_LEN, sections=48)


def place_wire(wire_mesh, socket_pt, direction, start_offset):
    """Orient wire_mesh (built with its chord along local Z, centred at its
    own origin) along `direction`, with its near (-Z) end starting
    `start_offset` mm out from socket_pt along that direction.
    """
    xform = align_z_to(direction)
    placed = wire_mesh.copy()
    placed.apply_transform(xform)
    half_len = placed.extents[2] / 2.0
    anchor = socket_pt + direction * (start_offset + half_len)
    placed.apply_translation(anchor)
    return placed, half_len


def place_boss(direction, far_point):
    boss_inst = boss_placeholder()
    boss_inst.apply_transform(align_z_to(direction))
    boss_inst.apply_translation(far_point + direction * (BOSS_LEN / 2.0))
    return boss_inst


def place_foot(foot_mesh, foot_pt):
    fb = foot_mesh.bounds
    top_face_center = np.array(
        [(fb[0][0] + fb[1][0]) / 2.0, (fb[0][1] + fb[1][1]) / 2.0, fb[1][2]]
    )
    placed = foot_mesh.copy()
    placed.apply_translation(foot_pt - top_face_center)
    return placed


def build(
    post,
    foot,
    spring_wire,
    ductile_wire,
    foot_pt,
    explode=False,
    deformed_ductile=None,
):
    offset_socket = EXPLODE_OFFSET * 0.5 if explode else 0.0
    offset_far = EXPLODE_OFFSET * 0.5 if explode else 0.0

    parts = [post.copy()]
    foot_offset = np.array([0, 0, EXPLODE_OFFSET if explode else 0.0])
    foot_placed = place_foot(foot, foot_pt - foot_offset)
    parts.append(foot_placed)

    socket_top = foot_pt + np.array([0, 0, POST_TOP_Z])
    socket_mid = foot_pt + np.array([0, 0, POST_MID_Z])

    for az_sign in (-1, 1):
        direction = branch_direction(90 + az_sign * AZ_SPLIT)
        wire, half_len = place_wire(spring_wire, socket_top, direction, offset_socket)
        parts.append(wire)
        far_point = socket_top + direction * (offset_socket + 2 * half_len + offset_far)
        parts.append(place_boss(direction, far_point))

    ductile_mesh = deformed_ductile if deformed_ductile is not None else ductile_wire
    for az_sign in (-1, 1):
        direction = branch_direction(90 + az_sign * AZ_SPLIT)
        wire, half_len = place_wire(ductile_mesh, socket_mid, direction, offset_socket)
        parts.append(wire)
        far_point = socket_mid + direction * (offset_socket + 2 * half_len + offset_far)
        parts.append(place_boss(direction, far_point))

    return trimesh.util.concatenate(parts), len(parts)


def largest_body(mesh):
    """Drop tiny disconnected CSG slivers (e.g. where two angled socket
    bores cross near the post centreline) -- keep only the largest body."""
    bodies = mesh.split()
    if len(bodies) <= 1:
        return mesh
    return max(bodies, key=lambda b: b.volume)


def main():
    post = largest_body(trimesh.load(f"{GEAR_DIR}/post.stl"))
    foot = trimesh.load(f"{GEAR_DIR}/foot_1_scaled24.stl")
    spring_nom = trimesh.load(f"{GEAR_DIR}/spring_wire_nominal.stl")
    ductile_nom = trimesh.load(f"{GEAR_DIR}/ductile_wire_nominal.stl")
    ductile_def = trimesh.load(f"{GEAR_DIR}/ductile_wire_deformed.stl")

    # post-local frame, foot already at its own origin
    foot_pt = np.array([0.0, 0.0, 0.0])

    assembled, n = build(post, foot, spring_nom, ductile_nom, foot_pt, explode=False)
    assembled.export(f"{GEAR_DIR}/landing_gear_assembled.stl")
    print(f"assembled: {n} parts, bounds {assembled.bounds.tolist()}")

    exploded, n = build(post, foot, spring_nom, ductile_nom, foot_pt, explode=True)
    exploded.export(f"{GEAR_DIR}/landing_gear_exploded.stl")
    print(f"exploded: {n} parts, bounds {exploded.bounds.tolist()}")

    deformed, n = build(
        post,
        foot,
        spring_nom,
        ductile_nom,
        foot_pt,
        explode=False,
        deformed_ductile=ductile_def,
    )
    deformed.export(f"{GEAR_DIR}/landing_gear_deformed.stl")
    print(f"deformed: {n} parts, bounds {deformed.bounds.tolist()}")


if __name__ == "__main__":
    main()
