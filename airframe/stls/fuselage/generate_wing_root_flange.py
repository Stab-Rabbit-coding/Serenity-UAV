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

REV T1d (2026-10-10, BHD-02): FORE-GEAR NOTCH
--------------------------------------------
The fore landing-gear bays sat inside this plate's footprint (the plate came
after LG-10 sited them).  The owner moved the fore station to hip Y -16 and
accepted a notch for what still passes through: the plate now has a through-
notch around the generated conforming fore bay, its M3 keep-outs and the
thigh swept 0..26 deg (fore_gear_notch()).  The 29.2 above is the nominal
80 x 60 plate on the docstring's method; on the measured, bored, notched
footprint the governing BONDED-PEEL stress (linear about the net centroid,
docs/BHD02_OPTION_STUDY.md SS2) is 0.293 / 0.290 MPa -> FOS 17.1 port /
17.3 stbd against the 4.0 target, re-evaluated on every run (fos_report()).
Order matters: tools/generate_lg_bays.py first (this reads its fore bays).

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
         direction, per `AGENTS.md` SS3 "Attribution and Licensing".  Rev T1d
         notch by Claude (Claude Opus 5.5, Anthropic), 2026-10-10.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
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
    # BHD-01 (2026-10-07): bore every wing-root penetration through the plate.
    # Rev T1c generated a SOLID plate; it sits on the inner wall face right over
    # the spar socket, the tilt-shaft bushing seat and the nav/encoder ports, so
    # the spar could not be inserted (spar x flange 1,566 mm^3 per side,
    # tools/cargo_bulkhead_context.py).  The cuts are the merge's OWN negatives
    # -- the same solids that bore the hull -- so the two parts cannot drift.
    for label, cut in mci.wing_keepout_negatives():
        if label.startswith("mortise"):
            continue                     # tenon/mortise is below the plate's job
        plate = plate - mci.to_man(cut)
    # BHD-02 (owner 2026-10-10, "hybrid"): the fore gear bay moved to hip Y -16,
    # off the CF spar, but its upper part and the swinging thigh still pass
    # through this plate's footprint (511 mm^3 at the study).  The plate gets
    # a clean THROUGH-NOTCH: the wall-plane projection of everything the fore
    # gear puts through the plate's slab -- the generated conforming bay, its
    # M3 keep-outs (the corner's own bolt pattern) and the leg swept 0..26 deg
    # -- offset by NOTCH_CLR.  Through, not sculpted: a bonded printed plate
    # wants a pocket it can be laid up against.
    plate = plate - fore_gear_notch(side, plate)
    return keep_plate(mci.from_man(plate), side)


NOTCH_CLR = 1.5     # mm, printed-part clearance around the notch


def fore_gear_notch(side, plate):
    """Through-notch (Manifold) clearing the fore gear of this side's plate."""
    sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
    import numpy as np                                   # noqa: PLC0415
    from manifold3d import JoinType, Manifold, OpType    # noqa: PLC0415
    import landing_gear_bay_function as lgbf             # noqa: PLC0415
    import generate_lg_bays as glb                       # noqa: PLC0415
    import bhd02_option_study as bos                     # noqa: PLC0415
    label = f"fore-{side}"
    corner = lgbf.parse_corners(lgbf.SCAD)[label]
    tf = lgbf.corner_tf(corner)
    bay = mci.to_man(trimesh.load(os.path.join(
        REPO_ROOT, "airframe", "stls", "fuselage", "landing-gear",
        f"lg_r6_3_0in_bay_{label}.stl"), force="mesh"))
    org, ex, ey, ez = mci.lg_bay_frame(label)
    keep = Manifold.batch_boolean(
        [glb.bolt_cyl(org, ex, ey, ez, u, v, glb.BOLT_KEEP_D)
         for u, v in mci.LG_CORNER_BOLTS.get(label, mci.lg_nominal_bolts())], OpType.Add)
    legp = lgbf.render(lgbf.SCAD, "fore", "leg (thigh+shin+foot)",
                       lgbf.FEATURES["leg (thigh+shin+foot)"][0])
    gear = Manifold.batch_boolean([bay, keep, lgbf.swept_leg(legp, tf)], OpType.Add)
    lo, hi = (np.array(plate.bounding_box()).reshape(2, 3))
    slab = Manifold.cube(list(hi - lo + [0.0, 40.0, 40.0])).translate(list(lo - [0.0, 20.0, 20.0]))
    through = gear ^ slab
    if through.volume() <= 0.05:
        return Manifold()
    cs = bos.wall_section(through).offset(NOTCH_CLR, JoinType.Round)
    return cs.extrude(float(hi[0] - lo[0]) + 2.0).transform(bos.from_yzx(float(lo[0]) - 1.0))


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


def fos_report(mesh):
    """Bonded-footprint stress under the ultimate root moment (BHD-02 method).

    Three models, docs/BHD02_OPTION_STUDY.md SS2: the docstring's own (F =
    3M/2h over A/3), bonded linear stress about the net centroid (peel --
    governs), and rigid-plate edge bearing.  Allowable 5 MPa (ASSUMED,
    structural_analysis.md), target FOS 4.0.
    """
    sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
    import bhd02_option_study as bos                     # noqa: PLC0415
    m = bos.flange_models(bos.wall_section(mci.to_man(mesh)))
    print(f"      bond area {m['area_mm2']:.0f} mm^2, sigma bonded {m['sigma_bonded_mpa']} MPa, "
          f"bearing {m['sigma_bearing_mpa']} MPa -> FOS {m['fos_gov']} (target 4.0) "
          f"{'PASS' if m['passes'] else 'FAIL'}")
    return bool(m["passes"])


def main():
    print("=== generate_wing_root_flange.py  Rev T1d  2026-10-10 (fore-gear notch) ===")
    print(f"  footprint {mci.ROOT_FLANGE_W:.0f} (Y) x {mci.ROOT_FLANGE_H:.0f} (Z) mm, "
          f"thickness {mci.ROOT_FLANGE_T:.1f} mm, centred on the spar axis "
          f"(Y {mci.WING_SPAR_Y:+.2f}, Z {mci.WING_SPAR_Z:+.2f})")
    all_ok = True
    for side in ("port", "stbd"):
        mesh = build(side)
        out = os.path.join(OUT_DIR, f"wing_root_flange_{side}.stl")
        mesh.export(out)
        all_ok &= report(mesh, f"wing_root_flange_{side}")
        all_ok &= fos_report(mesh)
        print(f"      written -> {out}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
