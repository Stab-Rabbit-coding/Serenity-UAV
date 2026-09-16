#!/usr/bin/env python3
"""gen_cargo_void_formers.py -- Rev T5e (2026-09-16; Rev T5 2026-09-15 base)

Generate the removable VOID FORMERS for the cargo section's one foamable
zone (the chin compartment, hull Y -58..-22 forward of the payload bay),
cut EXACTLY to the published shell's cavity so they drop in before the pour
and pull out after cure.  See docs/CARGO_SECTION_LAYOUT.md SS6 "Foam zones".

Why formers are generated from the mesh and not drawn in OpenSCAD
-----------------------------------------------------------------
A void former has to fit INSIDE the cavity it protects, against a compound-
curved 2 mm skin.  Every box or prism drawn by hand is either too big to
insert or leaves a foam fillet where the equipment must later go.  Each
former here is `(design box) INTERSECT (cavity solid)`, where the cavity
chunk is what is left of the box after the shell is subtracted (picked by a
seed point inside the cavity), shrunk 0.4 mm for the wax film and PLA
shrinkage.

Rev T5e (2026-09-16): the two remaining avionics nodes (CN2 / CN3) now lie
FLAT on the chin floor under the battery nose (tools/cargo_layout_fit.py
N_CHIN_*, chin_node_shelf.scad), so a fifth former, node_bay, keeps their
bay (X -214..-126, Z 44..90 over the chin's Y span) foam-free; the battery
chimney now starts above it (Z 90) and the harness trunks are the 10 mm
flank ways OUTBOARD of the node bay.  The chin is now mostly equipment; the
optional pour is the few slivers around it.

The formers
-----------
1. collar_rim   -- keeps the head/cargo splice-collar seat clear (the open
                   fwd mating face is at Y -69.5 and the rim wall is not a closed ring until Y ~-67, so the plug starts at -66): the collar
                   reaches to Y -61.5 (head_cargo_splice_collar.stl) and is
                   bonded AFTER the pour, so the rim band Y -71.5..-58 must
                   stay foam-free right round the section.
2. batt_chimney -- the battery cradle's forward 36 mm sits in the chin; the
                   pack is exchanged DOWNWARD (docs/BATTERY_MOUNT.md Rev T5),
                   so the volume under it down to the chin floor must be open.
3. harness_trunk (x2, port/stbd) -- ways along the chin flanks for the
                   head-section PTFE conduits (docs/PHASED_BUILD_GUIDE.md
                   Phase 1 step 8), outboard of the node bay (10-13 mm to
                   the wall at Z 62..82, more below the shelf).
4. node_bay     -- the chin node shelf and the two pouched nodes, plus the
                   cable channel, Z 44..90 (floor to the battery underside).

Foam in the cargo section is OPTIONAL: the chin's own panels are under the
124 mm unbraced limit that set the 2.0 mm foam-fill wall (cargo_sect_shell24
.scad Rev Q note), and the payload bay and roof band are never foamed.  The
formers exist so that a builder who does pour the chin (buoyancy / stiffness
margin) cannot foam-in the collar seat, the battery drop path or the harness.
The report at the end gives the foam mass the chin would take.

Run:
    /usr/bin/python3 tools/gen_cargo_void_formers.py
Outputs:
    airframe/stls/fuselage/cargo/void_former_cargo_{collar_rim,batt_chimney,
        harness_trunk_port,harness_trunk_stbd}.stl   (hull frame; PLA, waxed)

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5, Anthropic) under the
author's direction, 2026-09-15, per `AGENTS.md` §3 AI attribution.
License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
"""

import os
import sys

import numpy as np
import trimesh
from manifold3d import Manifold, Mesh

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import cargo_layout_fit as clf  # noqa: E402

OUT_DIR = os.path.join(REPO, "airframe", "stls", "fuselage", "cargo")
SHRINK_MM = 0.4            # wax film + PLA shrink: former is this much smaller than the cavity
FOAM_RHO = 32.04e-6        # g/mm^3, 2 lb/ft^3 PU (docs/MASS_AUDIT_CARGO_WING_ROOT.md SS4)
COLLAR_Y1 = -58.0          # head/cargo collar reaches Y -61.5; +3.5 mm bonding access
CHIN_Y1 = -22.0            # aft end of the chin floor (ramp face top)
TRUNK = 20.0               # harness trunk section


def to_man(tm):
    return Manifold(Mesh(vert_properties=tm.vertices.astype(np.float32),
                         tri_verts=tm.faces.astype(np.uint32)))


def from_man(m):
    # process=False: manifold3d's output is already a proper 2-manifold with
    # shared vertex indices; trimesh's merge_vertices() would weld the
    # station-seam T-junctions into 4-face edges and break watertightness.
    msh = m.to_mesh()
    return trimesh.Trimesh(np.asarray(msh.vert_properties)[:, :3],
                           np.asarray(msh.tri_verts), process=False)


def box(x0, x1, y0, y1, z0, z1):
    b = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    b.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
    return b


def former_in_box(shell_man, design_box, seed):
    """`design_box - shell`, decomposed; return the component that contains
    `seed` (a point known to be inside the cavity) as a trimesh.

    This is the whole trick: the cavity never has to be built.  Subtracting
    the shell from the design box leaves the cavity chunk plus exterior
    chunks (outside the skin, inside the box); the seed picks the cavity."""
    parts = (to_man(design_box) - shell_man).decompose()
    for q in sorted(parts, key=lambda q: -q.volume()):
        tm = from_man(q)
        if tm.contains([seed])[0]:
            return tm
    raise RuntimeError(f"no cavity component contains seed {seed}")


# Rev T5e node bay: the shelf + two pouched nodes + 2 mm, floor to the
# battery underside
NODE_BAY_X1 = clf.N_CHIN_X_IN + clf.NODE_H + 2.0        # -125.85
NODE_BAY_X0 = 2 * clf.X_CL - NODE_BAY_X1                # -213.85
NODE_BAY_Z1 = clf.BATT_Z0                               # 90


def main():
    shell = trimesh.load(clf.SHELL, process=True)
    assert shell.is_watertight
    shell_man = to_man(shell)
    print(f"shell vol {shell.volume:,.0f} mm^3")
    os.makedirs(OUT_DIR, exist_ok=True)
    xc = clf.X_CL
    formers = {
        # name: (design box, seed point inside the cavity)
        "collar_rim": (box(-260, -80, -66.0, COLLAR_Y1, 44.0, 170.0), (xc, -64.0, 100.0)),
        "batt_chimney": (box(clf.BATT_X0 - clf.CRADLE_T - 1.0, clf.BATT_X1 + clf.CRADLE_T + 1.0,
                             COLLAR_Y1, CHIN_Y1, NODE_BAY_Z1, clf.CRADLE_TOP_Z + 1.0), (xc, -40.0, 110.0)),
        "harness_trunk_port": (box(NODE_BAY_X1 + 1.0, NODE_BAY_X1 + 1.0 + TRUNK,
                                   -66.0, CHIN_Y1, 44.0, 62.0 + TRUNK),
                               (NODE_BAY_X1 + 4.0, -45.0, 72.0)),
        "harness_trunk_stbd": (box(NODE_BAY_X0 - 1.0 - TRUNK, NODE_BAY_X0 - 1.0,
                                   -66.0, CHIN_Y1, 44.0, 62.0 + TRUNK),
                               (NODE_BAY_X0 - 4.0, -45.0, 72.0)),
        "node_bay": (box(NODE_BAY_X0, NODE_BAY_X1, COLLAR_Y1, CHIN_Y1, 44.0, NODE_BAY_Z1),
                     (xc, -40.0, 75.0)),
    }
    total_void = 0.0
    for name, (b, seed) in formers.items():
        f = former_in_box(shell_man, b, seed)
        # shrink about the former's own centroid so every face moves in by
        # SHRINK_MM (exact on its planar design faces, ~0.1 mm on the curved
        # skin faces at these sizes) -- the wax film + PLA allowance
        ext = f.bounds[1] - f.bounds[0]
        c = f.bounds.mean(axis=0)
        f.apply_translation(-c)
        f.apply_scale(1.0 - 2.0 * SHRINK_MM / np.maximum(ext, 1e-6))
        f.apply_translation(c)
        assert f.is_watertight and f.volume > 0, name
        path = os.path.join(OUT_DIR, f"void_former_cargo_{name}.stl")
        f.export(path)
        chk = trimesh.load(path, process=True)
        assert chk.is_watertight or all(bb.is_watertight for bb in chk.split()), f"{name} on-disk"
        bb = f.bounds
        print(f"  {name:20s} vol {f.volume:9,.0f} mm^3  PLA ~{f.volume * 1.24e-3 * 0.25:5.1f} g @25% infill  "
              f"X{bb[0][0]:.0f}..{bb[1][0]:.0f} Y{bb[0][1]:.0f}..{bb[1][1]:.0f} Z{bb[0][2]:.0f}..{bb[1][2]:.0f}")
        total_void += f.volume
    chin = former_in_box(shell_man, box(-260, -80, -66.0, CHIN_Y1, 44.0, 170.0), (xc, -40.0, 100.0))
    foam = chin.volume - total_void
    print(f"\nchin zone cavity {chin.volume:,.0f} mm^3; formers {total_void:,.0f}; "
          f"foamable {foam:,.0f} mm^3 = {foam * FOAM_RHO:.1f} g of 2 lb/ft^3 PU (optional)")


if __name__ == "__main__":
    main()
