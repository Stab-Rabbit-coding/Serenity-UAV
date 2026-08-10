#!/usr/bin/env python3
"""
finalize_cargo_middle.py  —  build the final cargo and middle 2 mm shells with
thin exterior details filled solid (morphological opening), preserving the two
cargo-section shuttle bays hollow (avionics compartments).

Hull geometry derives from "Serenity Firefly with landing gear and swivel
engines" by misubisu (thingiverse.com/thing:7330462, CC BY 4.0).
Full attribution chain: current-specification/LICENSE_AND_ATTRIBUTION.md §2.

    python3 finalize_cargo_middle.py

Same fill approach as finalize_head_rear.py: inner_used = opened INTERSECT original
(opened = morph_open_voxel.py output) so the wall is never thinner than 2 mm and
thin details (greebles) come out solid.  The r=4 mm opening cannot fill the large
port/starboard shuttle cavities (verified: both pod interiors remain hollow), so
those avionics bays are left open for the Pilot/XO stacks + Faraday trays.

Interior INARA (port +X) / RIVER (stbd -X) shuttle marks are engraved by the
companion step engrave_shuttles.py (kept separate so the recess depth can be
tuned against the measured wall without rerunning the booleans).

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0  —  creativecommons.org/licenses/by/4.0
"""

import os

import trimesh

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "files-hollowed-24in")
PARTS = os.path.join(OUT, "operands")
ENG = "manifold"


def load(name):
    return trimesh.load(os.path.join(PARTS, name), process=True)


def drop_islands(mesh, min_faces=100):
    comps = mesh.split(only_watertight=False)
    keep = [c for c in comps if len(c.faces) >= min_faces]
    return trimesh.util.concatenate(keep) if keep else mesh


def build(part, opened_name, out_name):
    Outr = load(f"{part}__outer.stl")
    inner = load(f"{part}__inner.stl")
    opened = load(opened_name)
    inner_used = trimesh.boolean.intersection([opened, inner], engine=ENG)
    shell = trimesh.boolean.difference([Outr, inner_used], engine=ENG)
    shell = drop_islands(shell)
    out = os.path.join(OUT, out_name)
    shell.export(out)
    print(
        f"{part}: facets={len(shell.faces)} watertight={shell.is_watertight} "
        f"vol={shell.volume:.0f} -> {out}"
    )


if __name__ == "__main__":
    build(
        "cargo_sect_shell24_2mm_repaired",
        "cargo_inner_opened.stl",
        "cargo_sect_shell24_2mm_repaired.stl",
    )
    build(
        "middle_shell24_2mm_repaired",
        "middle_inner_opened.stl",
        "middle_shell24_2mm_repaired.stl",
    )
