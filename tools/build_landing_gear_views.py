#!/usr/bin/env python3
"""Build assembled / exploded / deformed demonstration STLs for the Rev R3
Strong-Leg + per-arm wire-loop fuse landing gear assembly.

This is a SCHEMATIC illustration of the design described in
docs/LANDING_GEAR_ANALYSIS.md Rev R3, not a finalized hull-integrated
assembly: the hull boss is a simple placeholder cylinder (LG-02, the real
boss SCAD integration, is still open), and the Strong-Leg used is the
standalone exported part (pulled away from the hull per CLAUDE.md / TODO
LG-10), not yet baked to a final corner placement.

Outputs (airframe/stls/fuselage/landing-gear/):
    landing_gear_assembled.stl   -- leg + foot + 2 wire fuses + 2 boss
                                     placeholders, in correct relative
                                     position, nominal (undeformed) fuses.
    landing_gear_exploded.stl    -- same parts, separated along each part's
                                     local insertion axis for visual clarity.
    landing_gear_deformed.stl    -- same as assembled, but one arm's wire
                                     fuse is swapped for the crushed/deformed
                                     variant and the boss on that arm is
                                     pulled in to sit against the shortened
                                     fuse, showing the post-overload state.

Run: python3 tools/build_landing_gear_views.py
"""

import numpy as np
import trimesh

GEAR_DIR = "airframe/stls/fuselage/landing-gear"

# Measured Strong-Leg geometry (docs/LANDING_GEAR_ANALYSIS.md SS2.3) -- the
# foot point and the two arm-tip centroids, in the standalone exported
# part's own coordinate frame.
FOOT_PT = np.array([-114.71834564, -142.64599609, -12.99771976])
TIP1 = np.array([-96.30127746, -111.34827438, 66.17362423])
TIP2 = np.array([-84.86322096, -124.32145078, 66.17362423])

BOSS_OD = 13.0
BOSS_LEN = 12.0
EXPLODE_OFFSET = 30.0  # mm, separation distance for the exploded view


def align_z_to(direction):
    """Return a 4x4 transform rotating the local +Z axis onto `direction`."""
    direction = direction / np.linalg.norm(direction)
    return trimesh.geometry.align_vectors([0, 0, 1], direction)


def place_along_arm(mesh, foot, tip, start_offset, local_z_extent_half):
    """Orient `mesh` (built with its load axis along local Z, centred at its
    own origin) so its local +Z axis points from foot toward tip, and
    translate it so its -Z end sits at `start_offset` mm along that
    direction beyond the tip.
    """
    direction = tip - foot
    unit = direction / np.linalg.norm(direction)
    xform = align_z_to(unit)
    placed = mesh.copy()
    placed.apply_transform(xform)
    anchor = tip + unit * (start_offset + local_z_extent_half)
    placed.apply_translation(anchor)
    return placed, unit


def boss_placeholder():
    """Simple schematic hull boss: a short cylinder, bore omitted (LG-02
    integration is still open -- see docs/LANDING_GEAR_ANALYSIS.md SS4.6).
    """
    return trimesh.creation.cylinder(radius=BOSS_OD / 2.0, height=BOSS_LEN, sections=48)


def place_foot(foot_mesh, foot_pt, offset_along_neg_z=0.0):
    """Translate the canonical foot pad so its top face centre sits
    `offset_along_neg_z` mm below the leg's foot point (0 = touching).
    """
    fb = foot_mesh.bounds
    top_face_center = np.array([(fb[0][0] + fb[1][0]) / 2.0, (fb[0][1] + fb[1][1]) / 2.0, fb[1][2]])
    placed = foot_mesh.copy()
    target = foot_pt - np.array([0, 0, offset_along_neg_z])
    placed.apply_translation(target - top_face_center)
    return placed


def main():
    leg = trimesh.load(f"{GEAR_DIR}/strong-leg.stl")
    foot = trimesh.load(f"{GEAR_DIR}/foot_1_scaled24.stl")
    fuse_nom = trimesh.load(f"{GEAR_DIR}/wire_loop_fuse_nominal.stl")
    fuse_def = trimesh.load(f"{GEAR_DIR}/wire_loop_fuse_deformed.stl")

    fuse_nom_half_z = fuse_nom.extents[2] / 2.0
    fuse_def_half_z = fuse_def.extents[2] / 2.0
    boss = boss_placeholder()

    # ---- Assembled view (nominal, touching) ----
    parts = [leg, place_foot(foot, FOOT_PT, offset_along_neg_z=0.0)]
    for tip in (TIP1, TIP2):
        fuse, unit = place_along_arm(fuse_nom, FOOT_PT, tip, start_offset=0.0, local_z_extent_half=fuse_nom_half_z)
        parts.append(fuse)
        boss_inst = boss.copy()
        boss_xform = align_z_to(unit)
        boss_inst.apply_transform(boss_xform)
        boss_anchor = tip + unit * (2 * fuse_nom_half_z + BOSS_LEN / 2.0)
        boss_inst.apply_translation(boss_anchor)
        parts.append(boss_inst)
    assembled = trimesh.util.concatenate(parts)
    assembled.export(f"{GEAR_DIR}/landing_gear_assembled.stl")
    print(f"assembled: {len(parts)} parts, bounds {assembled.bounds.tolist()}")

    # ---- Exploded view ----
    parts_exp = [leg, place_foot(foot, FOOT_PT, offset_along_neg_z=EXPLODE_OFFSET)]
    for tip in (TIP1, TIP2):
        fuse, unit = place_along_arm(
            fuse_nom, FOOT_PT, tip, start_offset=EXPLODE_OFFSET * 0.5, local_z_extent_half=fuse_nom_half_z
        )
        parts_exp.append(fuse)
        boss_inst = boss.copy()
        boss_xform = align_z_to(unit)
        boss_inst.apply_transform(boss_xform)
        boss_anchor = tip + unit * (EXPLODE_OFFSET * 0.5 + 2 * fuse_nom_half_z + EXPLODE_OFFSET * 0.5 + BOSS_LEN / 2.0)
        boss_inst.apply_translation(boss_anchor)
        parts_exp.append(boss_inst)
    exploded = trimesh.util.concatenate(parts_exp)
    exploded.export(f"{GEAR_DIR}/landing_gear_exploded.stl")
    print(f"exploded: {len(parts_exp)} parts, bounds {exploded.bounds.tolist()}")

    # ---- Deformed view: arm 1's fuse has fired (crushed), arm 2 intact ----
    parts_def = [leg, place_foot(foot, FOOT_PT, offset_along_neg_z=0.0)]
    tip_fuse_pairs = [(TIP1, fuse_def, fuse_def_half_z), (TIP2, fuse_nom, fuse_nom_half_z)]
    for tip, fuse_mesh, half_z in tip_fuse_pairs:
        fuse, unit = place_along_arm(fuse_mesh, FOOT_PT, tip, start_offset=0.0, local_z_extent_half=half_z)
        parts_def.append(fuse)
        boss_inst = boss.copy()
        boss_xform = align_z_to(unit)
        boss_inst.apply_transform(boss_xform)
        boss_anchor = tip + unit * (2 * half_z + BOSS_LEN / 2.0)
        boss_inst.apply_translation(boss_anchor)
        parts_def.append(boss_inst)
    deformed = trimesh.util.concatenate(parts_def)
    deformed.export(f"{GEAR_DIR}/landing_gear_deformed.stl")
    print(f"deformed: {len(parts_def)} parts, bounds {deformed.bounds.tolist()}")


if __name__ == "__main__":
    main()
