#!/usr/bin/env python3
# ============================================================================
# HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
#   Hull frame (canonical for ALL design artifacts): X = +port (left),
#   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
#   world origin.
#
#   This file (Rev R1c, 2026-06-29):
#     Generates the SHELL-SIDE hinge-pin RETENTION BLOCKS for the cargo-bay
#     clamshell doors, directly in hull-frame coordinates.
#
#   Why this file exists / supersedes the legacy SCAD module
#   --------------------------------------------------------
#     The original retention blocks lived in cargo_sect_shell24.scad as the
#     module hinge_pin_block() driven by HINGE_Y/HINGE_Z.  Those parameters
#     were authored in the PRE-BAKE legacy part-local frame (Y = vertical,
#     Z = lateral) and a SINGLE shared centreline hinge running along the
#     lateral axis — backwards from the Rev R1b door design, where each door
#     is its own INDEPENDENT piano hinge pinned at the OUTBOARD belly edge,
#     axis along hull Y (see generate_cargo_doors.py and TODO.md §1.1.1.2).
#     Reframing that single module inside the large legacy SCAD (whose
#     door_bay_cut / servo-pad / latch-lip modules are still in the legacy
#     frame and interdependent) would leave the SCAD internally inconsistent.
#     Because the published cargo shell is now the Blender-canonical mesh
#     (airframe/blender-scripts/files-hollowed-24in/, §1.1.1.0a) and the SCAD
#     is a SECONDARY interior-feature source, the correct realization is this
#     self-contained hull-frame generator — matching the repo pattern set by
#     generate_cargo_doors.py and generate_cargo_mounts.py — whose output is
#     boolean-unioned into the Blender cargo shell during the interior-feature
#     merge (TODO.md §1.1.1.0a "Cargo section interior boss features").
#     The legacy SCAD hinge_pin_block() is marked SUPERSEDED accordingly.
#
#   Mating geometry (taken from generate_cargo_doors.py / verified against the
#   baked door STLs cargo_door_{port,stbd}.stl, 2026-06-29):
#       Door bay (rod span):   hull Y = +2.0 .. +108.0 mm
#       Port door rod axis:    hull X = -117.6 mm, Z = +5.11 mm
#       Stbd door rod axis:    hull X = -222.5 mm, Z = +5.22 mm
#       CF rod:                3.0 mm OD; bore Ø3.3 mm (rod + 0.15 mm/side)
#       Door knuckles (each):  6 mm OD, 12 mm long, at Y = 8.0/39.3/70.7/102.0
#
#   Design
#   ------
#     Two end-support retention blocks per door (FOUR total), one just FWD of
#     the bay (Y < +2) and one just AFT (Y > +108), each bonded to the intact
#     belly skin OUTSIDE the door aperture (belly skin presence at all four
#     stations confirmed against the baked shell, 2026-06-29).  Each block:
#       * Y-axis through-bore Ø3.3 mm on the door's rod axis (seats the CF rod
#         end; the door's four knuckles rotate on the rod span between the two
#         blocks).
#       * M3 grub-screw tap (Ø2.5 mm) from the +Z/dorsal face down onto the
#         bore — DIN 913 M3x4 grub screw clamps the rod against rotation/axial
#         creep, matching the legacy retention scheme and the door knuckle
#         bore Ø3.15 mm.
#     Field disassembly: back out the four grub screws, withdraw the two rods,
#     both doors drop free (CLAUDE.md common-hand-tool field-disassembly rule).
#
# Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
# License: CC BY 4.0 - creativecommons.org/licenses/by/4.0
#
# Print spec:  CF-PETG, 0.15 mm layer, 4 perimeters, >=40% infill (load-bearing
#              flight-critical cargo-retention hardware).  Bonded to the shell
#              interior with West System 105/206 in addition to the printed/
#              merged union.
# ============================================================================
"""generate_cargo_hinge_retention.py — Rev R1c (2026-06-29)

Generate the four shell-side hinge-pin retention blocks (two per cargo door)
in hull-frame coordinates, ready to be boolean-unioned into the Blender
canonical cargo shell.

Output: cargo_hinge_retention.stl  (all four blocks; one file)
Run:    python3 generate_cargo_hinge_retention.py
"""

import os

import numpy as np
import trimesh

# ---------------------------------------------------------------------------
# Mating constants — keep in sync with generate_cargo_doors.py
# ---------------------------------------------------------------------------
BAY_Y_FWD = 2.0       # mm — fwd edge of door bay (rod start)
BAY_Y_AFT = 108.0     # mm — aft edge of door bay (rod end)

# Per-door rod axis (hull X, Z).  Verified against the baked door STLs.
ROD_AXES = {
    "port": (-117.6, 5.11),
    "stbd": (-222.5, 5.22),
}
# Inboard direction (toward ship centreline X_CL ≈ -169.85) for each door:
#   port hinge X = -117.6 is OUTBOARD of CL (less negative) → block extends -X
#   stbd hinge X = -222.5 is OUTBOARD of CL (more negative) → block extends +X
INBOARD_SIGN = {"port": -1.0, "stbd": +1.0}

ROD_BORE_D = 3.3      # mm — Ø3.3 bore (3.0 CF rod + 0.15 mm/side clearance)
GRUB_TAP_D = 2.5      # mm — M3 grub-screw tap-drill (coarse, pitch 0.5)
GRUB_DEPTH = 4.0      # mm — tap depth below the block +Z face

# Block envelope
BLK_LEN_Y = 12.0      # mm — Y length of each block (rod bearing length)
BLK_W_X = 9.0         # mm — X width (bore wall + bonding flange, extends inboard)
BLK_BASE_Z = 0.5      # mm — block base Z (overlaps belly skin for boolean fusion)
BLK_WALL_TOP = 2.5    # mm — material above the bore for the grub-screw boss
GAP_TO_BAY = 1.0      # mm — clearance between block inner Y face and bay edge

SECTIONS = 48         # cylinder facet count


def _block(side, station):
    """Build one retention block (manifold) for `side` at `station` in
    {'fwd','aft'}.  Returns a hull-frame trimesh solid."""
    hx, hz = ROD_AXES[side]
    sgn = INBOARD_SIGN[side]

    # Y extent: block sits OUTSIDE the bay, abutting its edge with GAP_TO_BAY.
    if station == "fwd":
        y_hi = BAY_Y_FWD - GAP_TO_BAY          # inner face just fwd of bay
        y_lo = y_hi - BLK_LEN_Y
    else:
        y_lo = BAY_Y_AFT + GAP_TO_BAY          # inner face just aft of bay
        y_hi = y_lo + BLK_LEN_Y
    y_cen = 0.5 * (y_lo + y_hi)

    # X extent: from the hinge axis outboard edge, extending INBOARD by BLK_W_X
    # (keeps the block over solid belly and clear of the door swing envelope).
    x_outboard = hx - sgn * 1.0                 # 1 mm outboard of axis
    x_inboard = hx + sgn * BLK_W_X
    x_lo, x_hi = sorted([x_outboard, x_inboard])

    # Z extent: belly base up to the grub-screw boss above the bore.
    z_lo = BLK_BASE_Z
    z_hi = hz + ROD_BORE_D / 2.0 + BLK_WALL_TOP
    x_cen = 0.5 * (x_lo + x_hi)
    z_cen = 0.5 * (z_lo + z_hi)

    body = trimesh.creation.box(
        extents=[x_hi - x_lo, y_hi - y_lo, z_hi - z_lo],
        transform=trimesh.transformations.translation_matrix([x_cen, y_cen, z_cen]),
    )

    # Y-axis rod through-bore at (hx, hz); overshoot 1 mm each end for clean cut.
    bore = trimesh.creation.cylinder(
        radius=ROD_BORE_D / 2.0, height=(y_hi - y_lo) + 2.0, sections=SECTIONS,
    )
    bore.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2.0, [1, 0, 0]))
    bore.apply_transform(trimesh.transformations.translation_matrix([hx, y_cen, hz]))

    # M3 grub-screw tap from +Z face down onto the bore.
    grub = trimesh.creation.cylinder(
        radius=GRUB_TAP_D / 2.0, height=GRUB_DEPTH + 0.5, sections=SECTIONS,
    )
    gz = z_hi - GRUB_DEPTH / 2.0 + 0.25
    grub.apply_transform(trimesh.transformations.translation_matrix([hx, y_cen, gz]))

    solid = trimesh.boolean.difference([body, bore, grub], engine="manifold")
    return solid


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "cargo_hinge_retention.stl")

    blocks = []
    print("Cargo hinge-pin retention blocks (Rev R1c, hull frame):")
    for side in ("port", "stbd"):
        hx, hz = ROD_AXES[side]
        for station in ("fwd", "aft"):
            b = _block(side, station)
            bb = b.bounds
            print(f"  {side:4s} {station:3s}: X {bb[0][0]:7.2f}..{bb[1][0]:7.2f}  "
                  f"Y {bb[0][1]:7.2f}..{bb[1][1]:7.2f}  Z {bb[0][2]:6.2f}..{bb[1][2]:6.2f}  "
                  f"watertight={b.is_watertight}")
            blocks.append(b)

    combined = trimesh.util.concatenate(blocks)
    combined.export(out)
    print("\n  rod axes: port (X=-117.6, Z=5.11), stbd (X=-222.5, Z=5.22)")
    print(f"  wrote {out}")
    print(f"  total blocks={len(blocks)}  facets={len(combined.faces)}  "
          f"bodies={len(combined.split(only_watertight=False))}")


if __name__ == "__main__":
    main()
