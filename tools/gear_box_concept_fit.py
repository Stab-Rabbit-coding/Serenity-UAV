#!/usr/bin/python3
"""Contour the canonical gear-box concept to the wing root (plan 2026-11-01-001).

Owner 2026-11-01: "contour the top edge of the box to match the bottom of the
wing" and "bring the front edge up so that it has a clean hull skin joint
instead of a shelf in front of the wing root".

The SCAD (airframe/openscad/fuselage/gear_box_canonical_concept.scad) gives
the box a top face that slopes up-inboard into the hull skin.  This tool then
removes everything at or above the wing's underside, less WING_CLR:

    box  -=  U_k  translate(wing, z = -WING_CLR + k * STEP),  k = 0..N

The union of the wing translated straight UP is the wing's vertical "shadow".
Its lower boundary is exactly the lowest copy's underside, so the cut follows
the real S1223-derived lower surface, including its concave aft portion.  A
convex hull would bridge that concavity and leave a gap.  STEP only has to be
smaller than the thinnest wing section (the trailing edge) for the copies
to overlap: 8 mm left 67 mm^3 of TE uncut.  The
bonded wing-root flange is cleared the same way, by FLANGE_CLR in all
directions.

Reports the pre-trim box/wing overlap and writes (port, hull frame R2) the
trimmed STL.  Starboard is the mirror about hd.X_CL (owner: symmetric).

Run:  /usr/bin/python3 tools/gear_box_concept_fit.py OUT_DIR

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, per AGENTS.md AI attribution.
License: MIT (SPDX-License-Identifier: MIT) -- see tools/LICENSE.
"""

from __future__ import annotations

import os
import subprocess
import sys

import numpy as np
import trimesh
from manifold3d import Manifold, Mesh

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import hull_datums as hd  # noqa: E402

sys.path.insert(0, os.path.join(REPO, "airframe", "blender-scripts"))
import merge_cargo_interior as mci  # noqa: E402

SCAD = os.path.join(REPO, "airframe/openscad/fuselage/gear_box_canonical_concept.scad")
WING = os.path.join(REPO, "airframe/stls/wings/wing_port_s1223_revo.stl")
FLANGE = os.path.join(REPO, "airframe/stls/fuselage/wing_root_flange_port.stl")
WING_CLR = 1.5     # mm, box top below the wing underside (assembly + paint)
FLANGE_CLR = 1.0   # mm, all round the bonded root flange
# Owner 2026-11-01: "make sure that your box clears those spar and cable
# holes".  The SAME set the hull merge cuts and the Rev R6 bays honour
# (merge_cargo_interior.wing_keepout_negatives(): spar socket O20.4 + 10 AWG
# bundle exit O16.3, nav O4.2 / encoder O7.5 / tilt-shaft O4.4 entries, shaft
# bushing seat, wing mortise) -- one definition, never re-typed here.
KEEP_CLR = 1.0     # mm, all round each wing-root penetration
STEP = 1.0         # mm between swept wing copies (< thinnest wing section: the TE)
RISE = 80.0        # mm the wing shadow extends upward


def to_man(tm: trimesh.Trimesh) -> Manifold:
    return Manifold(Mesh(vert_properties=np.asarray(tm.vertices, np.float32),
                         tri_verts=np.asarray(tm.faces, np.uint32)))


def from_man(m: Manifold) -> trimesh.Trimesh:
    g = m.to_mesh()
    return trimesh.Trimesh(g.vert_properties[:, :3], g.tri_verts, process=False)


def shifted(m: Manifold, offsets) -> Manifold:
    return Manifold.batch_boolean([m.translate(o) for o in offsets], 0)  # 0 = union


def grow_offsets(c: float):
    """27 translations (+/-c, 0 per axis): a cheap dilation by ~c of a solid."""
    return [(dx, dy, dz) for dx in (-c, 0, c) for dy in (-c, 0, c) for dz in (-c, 0, c)]


def render_box(out_dir: str, inset: float = 0.0, part: str = "port") -> Manifold:
    """Render the concept SCAD (port, hull frame R2) as a Manifold."""
    raw = os.path.join(out_dir, f"gear_box_{part}_inset{inset:g}_raw.stl")
    subprocess.run(["openscad", "-D", f'PART="{part}"', "-D", f"INSET={inset}",
                    "-o", raw, SCAD], check=True, capture_output=True)
    return to_man(trimesh.load(raw))


def port_keepouts():
    """The hull merge's own wing-root penetrations, port side (stbd = mirror)."""
    return [(lab, to_man(tm)) for lab, tm in mci.wing_keepout_negatives() if "stbd" not in lab]


def trim(box: Manifold, extra: float = 0.0, verbose: bool = False) -> Manifold:
    """Remove the wing shadow, root flange and penetrations from `box`.

    `extra` is added to every clearance: 0 for the OUTER solid; the wall
    thickness for the INNER solid, so the trimmed skin keeps its wall
    against every cut face (tools/gear_box_hull_merge.py).
    """
    wing = to_man(trimesh.load(WING))
    flange = to_man(trimesh.load(FLANGE))
    keeps = port_keepouts()
    if verbose:
        print(f"box (raw)            {box.volume():10.0f} mm3")
        print(f"box x wing overlap   {(box ^ wing).volume():10.0f} mm3  (pre-trim)")
        print(f"box x flange overlap {(box ^ flange).volume():10.0f} mm3  (pre-trim)")
        for lab, km in keeps:
            v = (box ^ km).volume()
            if v > 0.01:
                print(f"box x {lab:24s} {v:8.1f} mm3  (pre-trim)")
    n = int(RISE / STEP) + 1
    shadow = shifted(wing, [(0.0, 0.0, -(WING_CLR + extra) + k * STEP) for k in range(n)])
    flange_k = shifted(flange, grow_offsets(FLANGE_CLR + extra))
    keep_k = Manifold.batch_boolean([shifted(km, grow_offsets(KEEP_CLR + extra))
                                     for _l, km in keeps], 0)
    cut = box - shadow - flange_k - keep_k
    # drop boolean residue, as generate_lg_bays.py SLIVER_MM3
    return Manifold.batch_boolean([b for b in cut.decompose() if b.volume() >= 1.0], 0)


def main(out_dir: str) -> int:
    os.makedirs(out_dir, exist_ok=True)
    cut = trim(render_box(out_dir), verbose=True)
    wing = to_man(trimesh.load(WING))
    keeps = port_keepouts()
    bodies = sorted((b.volume() for b in cut.decompose()), reverse=True)
    print(f"box (trimmed)        {cut.volume():10.0f} mm3, bodies {[round(v, 1) for v in bodies]}")
    print(f"trimmed x wing       {(cut ^ wing).volume():10.4f} mm3  (shall be 0)")
    worst = max((cut ^ km).volume() for _l, km in keeps)
    print(f"trimmed x penetrations (worst) {worst:.4f} mm3  (shall be 0)")
    out = from_man(cut)
    path = os.path.join(out_dir, "gear_box_port_fit.stl")
    out.export(path)
    stbd = out.copy()
    stbd.apply_transform(trimesh.transformations.reflection_matrix([hd.X_CL, 0, 0], [1, 0, 0]))
    stbd.export(os.path.join(out_dir, "gear_box_stbd_fit.stl"))
    print("wrote", path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
