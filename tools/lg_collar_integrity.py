#!/usr/bin/python3
"""Gate: the hull merge's landing-gear cuts keep every collar joint intact.

When the hull gives way to a printed gear bay (BHD-02g, 2026-10-11 -- the
two-row wire layout puts boss clusters through the bay's own seat collar),
two kinds of collar must survive:

1. The bay SEAT COLLAR -- the hull material the bay flange bolts down onto
   (merge_cargo_interior lg_bay_features: skin layer T..T+LG_SEAT_D).  For
   every corner and every M3 at its generated pattern
   (lg_bay_corner_params.py), the merged hull must still put bearing
   material under the bolt: hull inside the O8.4 washer / nut keep-out,
   below the flange, at least BEARING_MIN_MM3.  The 4 mm backing-plate
   bearing FOS of 4.0 (tools/landing_gear_r6_sizing.py LG-02) assumes that
   material.  Also reported: the collar's surviving volume vs the uncut
   layer and its body count.
2. The fuselage SPLICE-COLLAR joints (head/cargo and cargo/middle, Rev R3):
   the merged hull must be unchanged in each collar's Y band, and the gear
   cuts must not reach the collars (checked against the collar meshes).

Run:  /usr/bin/python3 tools/lg_collar_integrity.py MERGED.stl [--against PUBLISHED.stl]
Exit 2 on any failure.

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, per AGENTS.md AI attribution.
License: MIT (SPDX-License-Identifier: MIT) -- see tools/LICENSE.
"""

from __future__ import annotations

import argparse
import os
import sys

import trimesh
from manifold3d import Manifold

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "airframe", "blender-scripts"))
import cargo_bulkhead_context as cbc  # noqa: E402
import merge_cargo_interior as mci  # noqa: E402

BEARING_MIN_MM3 = 150.0     # hull under each bolt (same bar as generate_lg_bays.py)
KEEP_D = 3.4 + 2 * 2.5      # O8.4 washer / nut keep-out
SPLICE = {"head/cargo": (-61.5, -53.5), "cargo/middle": (121.0, 129.0)}  # collar Y bands
SPLICE_TOL_MM3 = 1.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("merged")
    ap.add_argument("--against", default=os.path.join(
        REPO, "airframe", "stls", "fuselage", "cargo", "cargo_sect_shell24_2mm_repaired.stl"))
    a = ap.parse_args()
    new = cbc.man(cbc.as_trimesh(trimesh.load(a.merged, force="mesh"), a.merged))
    old = cbc.man(cbc.as_trimesh(trimesh.load(a.against, force="mesh"), a.against))
    src = cbc.as_trimesh(trimesh.load(mci.BLENDER_SRC, process=False), mci.BLENDER_SRC)
    src.merge_vertices()
    env = cbc.man(mci.extract_envelope(mci.bake(src)))
    bad = False
    print("1. bay seat collars (bearing under each M3, merged hull)")
    for label, *_ in mci.LG_CORNERS:
        org, ex, ey, ez = mci.lg_bay_frame(label)
        zb1 = mci.BAY_PLATE_ZB0 + mci.BAY_PLATE_L
        layer = mci.lg_skin_layer(env, org, ex, ey, ez, mci.BAY_PLATE_WB, mci.BAY_PLATE_W,
                                  mci.BAY_PLATE_ZB0, zb1, mci.BAY_PLATE_T,
                                  mci.BAY_PLATE_T + mci.LG_SEAT_D)
        kept = layer ^ new
        frac = kept.volume() / max(layer.volume(), 1e-9)
        # a seat collar must stay ONE piece (a split ring loses its load path);
        # sub-1 mm^3 boolean slivers are not pieces
        pieces = [p for p in kept.decompose() if p.volume() >= 1.0]
        ok = len(pieces) == 1
        bad |= not ok
        print(f"  {'OK  ' if ok else 'FAIL'} {label:10s} collar kept {kept.volume():7.0f} of "
              f"{layer.volume():7.0f} mm3 ({frac:.0%}), pieces {len(pieces)}")
        for u, v in mci.LG_CORNER_BOLTS.get(label, mci.lg_nominal_bolts()):
            k = mci.to_man(mci.axis_cylinder(org + ey * u + ez * v, ex, -30.0, 20.0, KEEP_D / 2))
            # bearing = hull below the flange, inside the washer / nut footprint
            under = (k ^ new) - mci.lg_skin_layer(
                env, org, ex, ey, ez, 80, 80, -80, 80, -1.0, mci.BAY_PLATE_T)
            ok = under.volume() >= BEARING_MIN_MM3
            bad |= not ok
            print(f"     {'OK  ' if ok else 'FAIL'} M3 ({u:+6.2f},{v:+6.2f}) bearing "
                  f"{under.volume():6.1f} mm3 (min {BEARING_MIN_MM3:g})")
    print("2. fuselage splice-collar joints")
    collars = {"head/cargo": "head_cargo_splice_collar.stl",
               "cargo/middle": "cargo_middle_splice_collar.stl"}
    for name, (y0, y1) in SPLICE.items():
        band = Manifold.cube([400.0, y1 - y0, 400.0]).translate([-370.0, y0, -100.0])
        diff = ((new ^ band) - (old ^ band)) + ((old ^ band) - (new ^ band))
        # the band also holds the gear-bay pockets on the flank, which are not
        # splice-collar material: fail only where the change reaches the collar
        # itself or its bond face (collar mesh grown 2 mm)
        col_path = os.path.join(REPO, "airframe", "stls", "fuselage", collars[name])
        col = cbc.man(cbc.as_trimesh(trimesh.load(col_path, force="mesh"), col_path))
        grown = col.minkowski_sum(Manifold.sphere(2.0, 8))
        hit = (diff ^ grown).volume()
        ok = hit <= SPLICE_TOL_MM3
        bad |= not ok
        print(f"  {'OK  ' if ok else 'FAIL'} {name:12s} Y {y0:+.1f}..{y1:+.1f}: band change "
              f"{diff.volume():.2f} mm3, of which at the collar / bond face {hit:.2f} mm3")
    print(f"\nRESULT: {'FAIL' if bad else 'PASS'}")
    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
