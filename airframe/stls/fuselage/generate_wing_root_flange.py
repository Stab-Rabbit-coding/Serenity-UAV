#!/usr/bin/env python3
"""Generate the two bonded wing-root flanges (WA-R1b, Rev T1c).

HULL-FRAME STANDARD R1 — X = +port, Y = +aft, Z = +dorsal; origin =
SerenityAssembly.FCStd world origin.  Output STLs are already in the hull frame;
do NOT run tools/bake_hull_frame.py on them.

WHAT THIS PART IS
-----------------
Under Rev T1 the wing spar is a fixed bonded CF tube and the wing-root joint
splits by load type (docs/WING_ATTACH_INTERFACE.md SS3.3): a short socket takes
the shear, and this flange takes the MOMENT.  Reacting over wall AREA rather
than socket DEPTH is what makes it work -- the cargo bay caps socket depth at
18.67 mm and a socket's capacity goes as 1/L^2, so at that depth a socket gives
FOS 0.51 on the moment.  The flange gives FOS 29.2:

    triangular bearing pressure over height h, arm 2h/3
    F     = 3M / (2h) = 3 x 14.60 N.m / (2 x 0.080 m) = 274 N
    area  = 80 x 60 = 1,600 mm^2
    sigma = 274 / 1600 = 0.17 MPa
    FOS   = 5.0 MPa / 0.17 = 29.2      (5 MPa bond-limited CF-PETG,
                                        docs/structural_analysis.md SS7.3)

WHY IT IS A SEPARATE PART AND NOT SHELL GEOMETRY
------------------------------------------------
Measured 2026-08-30 by ray-casting the baked cargo envelope on a 13 x 17 grid
over the footprint (221/221 hits): the sidewall skin moves through **34.3 mm
(port) / 37.0 mm (stbd)** of hull X across the 80 x 60 window.  The wall is not
flat there, not even approximately.  Consequently:

  * modelling the flange the way merge_cargo_interior.py models every other
    positive -- deep material intersected with the envelope -- would make it up
    to 34 mm thick, hundreds of grams for a plate whose specified 5 mm already
    clears the FOS 4.0 target by 7x; and
  * bounding it with a plane at the nominal inner face instead leaves that plane
    TANGENT to the skin inside the footprint.  That is a knife edge, and it
    measured as one: a 0.46 mm non-manifold edge with 4 incident faces at
    (-86.33, +8.6, +52.2), plus a zero-area sliver body, on the first rebuild.

Subtracting a translated envelope from the whole 900k-face shell to get a
conforming plate was tried and was worse still (4 boundary edges, 2 non-manifold
edges, 4 bodies): a near-coincident boolean over 4,800 mm^2 at that scale does
not resolve cleanly.  Done LOCALLY, on a cropped envelope, the same operation is
small and well-conditioned -- which is what this script does.

So the flange follows the pattern this repository already uses for every other
bonded plate: the CF thwarts (asf.RING_POCKETS) and the three splice collars are
separate parts too, and the shell's only obligation to them is to reserve their
volume.  `merge_cargo_interior.wing_keepout_positives()` carries that reservation
as a nominal slab so the landing-gear bay cannot grow into it.

Run:
    /usr/bin/python3 airframe/stls/fuselage/generate_wing_root_flange.py

Use `/usr/bin/python3`: the repo .venv hides trimesh and manifold3d.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5, Anthropic) under the author's
         direction, per `AGENTS.md` SS3 "Attribution and Licensing".
License: CC BY-SA 4.0 - creativecommons.org/licenses/by-sa/4.0
"""

import os
import sys

import trimesh

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "airframe", "blender-scripts"))
import merge_cargo_interior as mci          # noqa: E402

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Crop margin around the footprint.  The local envelope must extend past the
# plate on every side, or the subtraction that sets the thickness runs out of
# material at the rim and leaves the plate open there.
CROP_PAD = 15.0     # mm

# CF-PETG (20% chopped CF), REF-MAT-002 / current-specification bom FIL-CF-PETG.
RHO_G_MM3 = 1.30e-3     # g/mm^3, solid
INFILL = 0.40           # 40% gyroid, the repo's structural-print convention


def build(side):
    """Return (trimesh, label) for one side's conforming flange plate."""
    src = trimesh.load(mci.BLENDER_SRC, process=False)
    src.merge_vertices()
    env = mci.extract_envelope(mci.bake(src))

    y0 = mci.WING_SPAR_Y - mci.ROOT_FLANGE_W / 2.0
    y1 = mci.WING_SPAR_Y + mci.ROOT_FLANGE_W / 2.0
    z0 = mci.WING_SPAR_Z - mci.ROOT_FLANGE_H / 2.0
    z1 = mci.WING_SPAR_Z + mci.ROOT_FLANGE_H / 2.0

    if side == "port":
        x_lo, x_hi = mci.PORT_INB - 20.0, mci.PORT_OUTB
        dx = -mci.ROOT_FLANGE_T          # inboard is -X on the port side
    else:
        x_lo, x_hi = mci.STBD_OUTB, mci.STBD_INB + 20.0
        dx = +mci.ROOT_FLANGE_T          # inboard is +X on the starboard side

    # Local envelope: the footprint plus CROP_PAD on every side.  Everything
    # below is a boolean on THIS, not on the full shell -- that locality is the
    # whole reason the operation is well-conditioned here and was not in
    # merge_cargo_interior.py.
    crop = mci.to_man(mci.box(x_lo, x_hi,
                              y0 - CROP_PAD, y1 + CROP_PAD,
                              z0 - CROP_PAD, z1 + CROP_PAD))
    env_local = crop ^ mci.to_man(env)

    footprint = mci.to_man(mci.box(x_lo, x_hi, y0, y1, z0, z1))
    plate = (footprint ^ env_local) - env_local.translate([dx, 0.0, 0.0])
    return keep_plate(mci.from_man(plate), side)


def keep_plate(mesh, side):
    """Keep the plate proper; report and drop anything else the window caught.

    The footprint window is a box, and inside a box the ray from outboard can
    strike more than one surface: at the aft-upper corner it also clips an
    INTERIOR wall standing behind the skin.  The subtraction then lays a second,
    disconnected 5 mm layer on that wall.  It is real geometry, not mesh noise --
    but it is not part of this plate, and a bonded part cannot be delivered as
    two disconnected solids, so it is dropped and its size is printed.

    Measured 2026-08-30: port drops 293.1 mm^3 (1.2 % of the plate) at
    X -118.4..-111.7, Y +45.4..+51.0, Z +57.8..+71.9; starboard drops an 18-face
    zero-volume sliver.  If a future hull change pushes a dropped body past a few
    percent, the footprint is straddling a discontinuity and the FOOTPRINT is
    what needs revisiting -- not this filter.
    """
    bodies = sorted(mesh.split(only_watertight=False),
                    key=lambda b: abs(b.volume), reverse=True)
    if len(bodies) <= 1:
        return mesh
    kept = bodies[0]
    for b in bodies[1:]:
        frac = abs(b.volume) / max(abs(kept.volume), 1e-9)
        flag = "  <-- REVIEW: over 5 % of the plate" if frac > 0.05 else ""
        print(f"      dropped disconnected body: {abs(b.volume):8.1f} mm^3 "
              f"({frac:.2%} of the plate), {len(b.faces)} faces{flag}")
    return kept


def report(mesh, name):
    bodies = mesh.split(only_watertight=False)
    vol = abs(mesh.volume)
    ok = mesh.is_watertight and len(bodies) == 1
    b = mesh.bounds
    print(f"  {name}: faces={len(mesh.faces):,} bodies={len(bodies)} "
          f"watertight={mesh.is_watertight}")
    print(f"      bounds X {b[0][0]:8.2f}..{b[1][0]:8.2f}  "
          f"Y {b[0][1]:7.2f}..{b[1][1]:7.2f}  Z {b[0][2]:7.2f}..{b[1][2]:7.2f}")
    print(f"      volume {vol:9.1f} mm^3   mass {vol * RHO_G_MM3 * INFILL:5.1f} g "
          f"at {INFILL:.0%} infill ({vol * RHO_G_MM3:5.1f} g solid)")
    print(f"      RESULT: {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    print("=== generate_wing_root_flange.py  Rev T1c  2026-08-30 ===")
    print(f"  footprint {mci.ROOT_FLANGE_W:.0f} (Y) x {mci.ROOT_FLANGE_H:.0f} (Z) mm, "
          f"thickness {mci.ROOT_FLANGE_T:.1f} mm, centred on the spar axis "
          f"(Y {mci.WING_SPAR_Y:+.2f}, Z {mci.WING_SPAR_Z:+.2f})")
    all_ok = True
    for side in ("port", "stbd"):
        mesh = build(side)
        out = os.path.join(OUT_DIR, f"wing_root_flange_{side}.stl")
        mesh.export(out)
        all_ok &= report(mesh, f"wing_root_flange_{side}")
        print(f"      written -> {out}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
