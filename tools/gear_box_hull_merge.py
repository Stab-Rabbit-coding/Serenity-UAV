#!/usr/bin/python3
"""Fuse the canonical landing-gear box into the one-piece forward hull as SKIN.

Plan docs/plans/2026-11-01-001-feat-canonical-gear-box-plan.md, U3.  Owner
2026-11-01: "merge it into the one piece printed hull".

Called by tools/merge_head_cargo_shell.py after the wing-root flanges are
fused; also runnable alone as a gate (--check) on the published hull.

Operands (aircraft datum R2, tools/hull_datums.py):
  Bo, Bi  the box OUTER solid (concept SCAD, INSET 0) and INNER solid
          (INSET = WALL), both trimmed by gear_box_concept_fit.trim() -- the
          inner with every clearance + WALL, so the skin keeps its wall
          against the wing shadow, the root flange and every penetration.
          Port built, starboard = exact mirror about hd.X_CL.
  O, I    the cargo section's OUTER and 2 mm eroded INNER operand solids
          (Blender pipeline, files-hollowed-24in/operands/), placed with
          bake_hull_frame's Cargo_Shell transform -- the hull's own
          envelope and cavity.
  slots   the swept leg paths (concept SCAD PART "slots_port").

Construction:
  new skin  = (Bo - Bi) - O - gear   box walls only OUTSIDE the old hull, so
                                     no box wall stands in the cargo hold;
                                     clear of the moving gear (leg_keepout)
  opening   = ((Bi n O) - I) - protect
                                     the OLD flank skin band inside the box
                                     cavity is removed, so the cavity opens
                                     into the hold: SLS powder drains (a
                                     sealed pocket traps unsintered powder)
  leg path  = (slots n O) - protect  the new fore swing plane crosses old
                                     hull material
  hull'     = hull - opening - leg path + new skin
  protect   = wing-root flanges + every wing-root penetration keep-out,
              each grown PROTECT_CLR: on the hull the wing always wins
              (merge_cargo_interior LG-10.4); + each bolted bay's seat
              (footprint grown BAY_SEAT_CLR) -- the bays carry the hip pins.

WALL = 2.0 mm: the hull's own skin (2 mm solidify), SLS PA12-CF.

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, per AGENTS.md AI attribution.
License: MIT (SPDX-License-Identifier: MIT) -- see tools/LICENSE.
"""

from __future__ import annotations

import os
import sys
import tempfile

import numpy as np
import trimesh
from manifold3d import Manifold

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import bake_hull_frame as bk  # noqa: E402
import gear_box_concept_fit as fit  # noqa: E402
import hull_datums as hd  # noqa: E402

OPS = os.path.join(REPO, "airframe", "blender-scripts", "files-hollowed-24in", "operands")
FSTL = os.path.join(REPO, "airframe", "stls", "fuselage")
WALL = 2.0          # mm, box skin = the hull's 2 mm skin
PROTECT_CLR = 1.0   # mm, flange / penetration protection for the opening and leg path
# The bolted Rev R6/A1B bay parts carry the hip pins and the CF backbone and
# STAY as internal structure inside the box (plan U3).  The old flank skin
# they seat on (rebate, collar, M3 bores) is protected from the opening by
# each bay's footprint grown BAY_SEAT_CLR.
BAY_SEAT_CLR = 6.0  # mm
BAYS = ("fore-port", "fore-stbd", "aft-port", "aft-stbd")


def placed(name: str, comp: str) -> Manifold:
    """Operand placed by bake_hull_frame's transform for `comp`."""
    tm = trimesh.load(os.path.join(OPS, name))
    px, py, pz, qx, qy, qz, qw = bk.COMPONENTS[comp][1]
    T = np.eye(4)
    T[:3, :3] = np.asarray(bk.quat_to_matrix(qx, qy, qz, qw))[:3, :3]
    T[:3, 3] = (px, py, pz)
    tm.apply_transform(T)
    return fit.to_man(tm)


def mirror_cl(m: Manifold) -> Manifold:
    """Starboard twin about the centreline X = hd.X_CL."""
    return m.mirror((1.0, 0.0, 0.0)).translate((2.0 * hd.X_CL, 0.0, 0.0))


def both(m: Manifold) -> Manifold:
    return m + mirror_cl(m)


LEG_CLR = 1.0       # mm, box skin to the moving gear


def leg_keepout() -> Manifold:
    """Every corner's moving gear, from the leg SCAD (single source):
    the leg swept 0..SWEEP_DEG about the hip pin (landing_gear_bay_function
    swept_leg) + the A1B members at rest and at full flex + the CF backbone,
    grown LEG_CLR.  The idealised trapezoid slot is narrower at the hip than
    the real hip assembly (lug, crank horns, cheeks at +/-12.7 mm), which
    left 3,354 mm^3 of new skin in the gear (first fused build, 2026-11-01)."""
    import landing_gear_bay_function as lgbf  # noqa: PLC0415
    parts = []
    for label, c in lgbf.parse_corners(lgbf.SCAD).items():
        st = label.split("-")[0]
        tf = lgbf.corner_tf(c)
        d = (f'BAY_STATION="{st}"',)
        leg = lgbf.render(lgbf.SCAD, st, "leg (thigh+shin+foot)",
                          lgbf.FEATURES["leg (thigh+shin+foot)"][0], d)
        parts.append(lgbf.swept_leg(leg, tf))
        for nm, expr in (("a1b members rest", "a1b_members(0);"),
                         ("a1b members flex", "a1b_members(FLEX_DEG);"),
                         ("a1b backbone", "a1b_backbone();")):
            parts.append(lgbf.posed(lgbf.render(lgbf.SCAD, st, nm, expr, d), tf))
    # + the whole exported gear at rest (hull_legs): the "leg" feature is the
    # thigh/shin/foot only -- the hip hub, lug and crank horns are not in it,
    # and those were exactly the parts the skin hit (86 cm^3 of the rest gear
    # lay outside the feature set, 2026-11-02).
    parts.append(fit.to_man(trimesh.load(os.path.join(
        FSTL, "landing-gear", "lg_r6_3_0in_hull_legs.stl"))))
    gear = Manifold.batch_boolean(parts, 0)
    # 7-point dilation (centre + +/-X/Y/Z), not fit.grow_offsets' 27: the
    # 27-copy union of the swept gear put ~450k faces into the hull and took
    # the published STL past GitHub's 100 MB file limit (115 MB, 2026-11-02).
    c = LEG_CLR
    seven = [(0.0, 0.0, 0.0), (c, 0, 0), (-c, 0, 0), (0, c, 0), (0, -c, 0), (0, 0, c), (0, 0, -c)]
    return fit.shifted(gear, seven)


def operands(work: str) -> dict[str, Manifold]:
    """Box outer / inner / slots (both sides) and the protect set."""
    bo = both(fit.trim(fit.render_box(work, 0.0)))
    bi = both(fit.trim(fit.render_box(work, WALL), extra=WALL))
    slots = both(fit.render_box(work, 0.0, part="slots_port"))
    prot = []
    for side in ("port", "stbd"):
        fl = fit.to_man(trimesh.load(os.path.join(FSTL, f"wing_root_flange_{side}.stl")))
        prot.append(fit.shifted(fl, fit.grow_offsets(PROTECT_CLR)))
    for c in BAYS:
        bay = fit.to_man(trimesh.load(os.path.join(
            FSTL, "landing-gear", f"lg_r6_3_0in_bay_{c}.stl")))
        prot.append(fit.shifted(bay, fit.grow_offsets(BAY_SEAT_CLR)))
    keeps = [km for _l, km in fit.port_keepouts()]
    prot += [both(fit.shifted(km, fit.grow_offsets(PROTECT_CLR))) for km in keeps]
    return {"bo": bo, "bi": bi, "slots": slots,
            "protect": Manifold.batch_boolean(prot, 0)}


def fuse(part: Manifold, work: str | None = None) -> tuple[Manifold, dict]:
    """hull' = hull - opening - leg path + new skin.  Returns (hull', report)."""
    work = work or tempfile.mkdtemp(prefix="gear_box_")
    op = operands(work)
    outer_m = placed("cargo_sect_shell24_2mm_repaired__outer.stl", "Cargo_Shell")
    inner_m = placed("cargo_sect_shell24_2mm_repaired__inner.stl", "Cargo_Shell")
    skin = (op["bo"] - op["bi"]) - outer_m - leg_keepout()
    opening = ((op["bi"] ^ outer_m) - inner_m) - op["protect"]
    legpath = (op["slots"] ^ outer_m) - op["protect"]
    before = part.volume()
    removed = (part ^ (opening + legpath)).volume()
    out = (part - opening - legpath) + skin
    rep = {"new skin cm3": skin.volume() / 1e3,
           "old skin opened cm3": (part ^ opening).volume() / 1e3,
           "leg path cleared cm3": (part ^ legpath).volume() / 1e3,
           "removed cm3": removed / 1e3,
           "net cm3": (out.volume() - before) / 1e3,
           "skin bodies": len(skin.decompose())}
    return out, rep


def main(argv: list[str]) -> int:
    """--check: fuse into the PUBLISHED merged hull in memory and report."""
    pub = trimesh.load(os.path.join(FSTL, "head_cargo_shell24_2mm_merged.stl"))
    out, rep = fuse(fit.to_man(pub))
    for k, v in rep.items():
        print(f"  {k:22s} {v:10.2f}" if isinstance(v, float) else f"  {k:22s} {v}")
    print(f"  result bodies          {len(out.decompose())}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
