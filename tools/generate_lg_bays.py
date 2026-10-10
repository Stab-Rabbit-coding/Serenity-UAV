#!/usr/bin/python3
"""Generate the four CONFORMING 3.0 in landing-gear bays (BHD-02, 2026-10-10).

Owner decisions of 2026-10-10 (docs/BHD02_OPTION_STUDY.md SS10):

* the fore station moves forward (hip Y -38), where the flank is more curved
  (17.1 mm of relief across the fore footprint vs a 12 mm flat rebate), so
* the bay's back face FOLLOWS the curve, and
* port and starboard bays are distinct MIRROR images, not one part rotated.

So the printed bay is no longer one flat-backed SCAD part per station.  It is
generated per corner from the SCAD design source
(airframe/openscad/fuselage/canonical_leg_r6_3_0in.scad, PART="none" library
mode) and from the hull's own outer-skin envelope:

    flange = skin layer 0..T          inside bay_flange_outline()
    liner  = skin layer 0..T+COWL_H   inside bay_liner_outline()
    bay    = flange + liner + bay_body()  - bay_cuts() - 4 x M3 - keep-outs

The skin layers come from merge_cargo_interior.lg_skin_layer(), the function
that also cuts the hull's rebate (0..T) and builds its seat collar
(T..T+LG_SEAT_D), so the hull and the part are made from one definition.

Keep-outs: the fore bays move next to the TACCO chin pouches (Faraday-pouched
PocketBeagle 2 + cape, tools/cargo_layout_fit.py) and the chin shelf.  The
owner accepted a trim (2026-10-10): every bay is cut clear of those solids
dilated by STATIC_GAP, and any M3 whose O8.4 keep-out (washer / nut / driver,
run 30 mm inboard) would hit them slides down its side flange until clear.
The resulting bolt pattern is written to
airframe/blender-scripts/lg_bay_corner_params.py, which the hull merge reads,
so the hull bores follow the part.

Checks on every corner (exit 2 on failure): one body; the leg swept 0..26 deg
clears its bay; every bolt still lands in flange material.

Outputs (airframe/stls/fuselage/landing-gear/):
    lg_r6_3_0in_bay_<corner>.stl        hull frame, for the assembly and gates
    lg_r6_3_0in_bay_<corner>_print.stl  leg-local (stbd = mirrored), for slicing

Run:  /usr/bin/python3 tools/generate_lg_bays.py [--check]   (--check: no writes)

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, per AGENTS.md AI attribution.
License: MIT (SPDX-License-Identifier: MIT) -- see tools/LICENSE.
"""

from __future__ import annotations

import argparse
import os
import pprint
import sys

import numpy as np
import trimesh
from manifold3d import Manifold, OpType

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "airframe", "blender-scripts"))
import cargo_bulkhead_context as cbc  # noqa: E402
import landing_gear_bay_function as lgbf  # noqa: E402
import merge_cargo_interior as mci  # noqa: E402
from bhd02_option_study import dilate  # noqa: E402

OUT = os.path.join(REPO, "airframe", "stls", "fuselage", "landing-gear")
PARAMS = os.path.join(REPO, "airframe", "blender-scripts", "lg_bay_corner_params.py")

STATIC_GAP = 2.0          # mm, the layout tool's static gap to fixed parts
KEEPOUTS = ("TACCO CN2 port", "TACCO CN3 stbd", "chin shelf")
BOLT_KEEP_D = 3.4 + 2 * 2.5   # O8.4 washer / nut / driver, as the census
BOLT_T = (-30.0, 20.0)    # bore extent along e_x, as the hull merge
BOLT_SLIDE_MAX = 30.0     # mm a blocked bolt may slide down its side flange
BOLT_MIN_FLANGE = 20.0    # mm^3 of flange that must surround a bolt hole
T = mci.BAY_PLATE_T
COWL_H = mci.COWL_H
RHO, INFILL = 1.30e-3, 0.40   # CF-PETG g/mm^3 solid, 40 % gyroid (repo convention)


def feat(station: str, name: str, tf: np.ndarray) -> Manifold:
    p = lgbf.render(lgbf.SCAD, station, name, lgbf.FEATURES[name][0])
    return lgbf.posed(p, tf)


def bolt_cyl(org, ex, ey, ez, u, v, d) -> Manifold:
    return mci.to_man(mci.axis_cylinder(org + ey * u + ez * v, ex,
                                        BOLT_T[0], BOLT_T[1], d / 2.0))


def build_corner(label: str, c: list[float], env: Manifold, keep: Manifold) -> dict:
    st = lgbf.STATION[label]
    tf = lgbf.corner_tf(c)
    org, ex, ey, ez = mci.lg_bay_frame(label)
    zb1 = mci.BAY_PLATE_ZB0 + mci.BAY_PLATE_L
    flange = mci.lg_skin_layer(env, org, ex, ey, ez, mci.BAY_PLATE_WB, mci.BAY_PLATE_W,
                               mci.BAY_PLATE_ZB0, zb1, 0.0, T) ^ feat(st, "flange outline", tf)
    liner = mci.lg_skin_layer(env, org, ex, ey, ez, mci.BAY_APER_W_BOT, mci.BAY_APER_W_TOP,
                              mci.BAY_APER_ZB0, mci.BAY_APER_ZB0 + mci.BAY_APER_L,
                              0.0, T + COWL_H) ^ feat(st, "liner outline", tf)
    body = feat(st, "body", tf)
    bay = Manifold.batch_boolean([flange, liner, body], OpType.Add) - keep
    # bolts: nominal, or slid down the side flange until the keep-out clears
    bolts, moved = [], []
    for u, v in mci.lg_nominal_bolts():
        dz = 0.0
        while (bolt_cyl(org, ex, ey, ez, u, v - dz, BOLT_KEEP_D) ^ keep).volume() > 0.05:
            dz += 0.5
            if dz > BOLT_SLIDE_MAX:
                raise RuntimeError(f"{label}: bolt ({u:+.1f},{v:+.1f}) cannot clear the keep-outs")
        bolts.append((round(u, 2), round(v - dz, 2)))
        if dz:
            moved.append(dict(nominal=(u, v), slid_mm=dz))
    holes = Manifold.batch_boolean([bolt_cyl(org, ex, ey, ez, u, v, mci.LG_M3_D)
                                    for u, v in bolts], OpType.Add)
    seat = [(bolt_cyl(org, ex, ey, ez, u, v, BOLT_KEEP_D) ^ flange).volume() for u, v in bolts]
    bay = bay - holes - feat(st, "cuts", tf)
    legp = lgbf.render(lgbf.SCAD, st, "leg (thigh+shin+foot)",
                       lgbf.FEATURES["leg (thigh+shin+foot)"][0])
    leg_x = (lgbf.swept_leg(legp, tf) ^ bay).volume()
    parts = sorted(bay.decompose(), key=lambda m: -m.volume())
    inv = np.linalg.inv(tf)
    loose = [dict(mm3=round(m.volume(), 1), local_bounds=trimesh.transform_points(
        np.array(m.bounding_box()).reshape(2, 3), inv).round(1).tolist()) for m in parts[1:]]
    return dict(label=label, bay=bay, tf=tf, bolts=bolts, moved=moved,
                bolt_flange_mm3=[round(x, 1) for x in seat],
                bodies=len(parts), body_mm3=sorted((round(p.volume(), 1) for p in parts),
                                                   reverse=True),
                loose=loose, leg_sweep_x_bay_mm3=round(leg_x, 2), volume=bay.volume(),
                mass_g=round(bay.volume() * RHO * INFILL, 1),
                flange_mm3=round(flange.volume(), 1), liner_mm3=round(liner.volume(), 1))


def write_params(rows: list[dict]) -> None:
    body = {r["label"]: r["bolts"] for r in rows}
    with open(PARAMS, "w", encoding="utf-8") as fh:
        fh.write('''"""Per-corner landing-gear bay M3 positions -- GENERATED, do not hand-edit.

Written by tools/generate_lg_bays.py; read by merge_cargo_interior.py
(LG_CORNER_BOLTS) so the hull bores follow the printed bays.  Plate frame:
u along e_y, v along e_z (mm); the starboard frame is mirrored (BHD-02).

AI attribution: generated by a tool written by Claude (Claude Opus 5.5,
Anthropic) under the direction of Stab-Rabbit-coding.
License: MIT (SPDX-License-Identifier: MIT)
"""

BOLTS = ''' + pprint.pformat(body, width=88) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="build and check only; write nothing")
    ap.add_argument("--only", action="append", help="build only this corner (repeatable)")
    a = ap.parse_args()
    src = trimesh.load(mci.BLENDER_SRC, process=False)
    src.merge_vertices()
    env = mci.to_man(mci.extract_envelope(mci.bake(src)))
    P = cbc.build()
    keep = dilate(Manifold.batch_boolean([P[k]["m"] for k in KEEPOUTS], OpType.Add), STATIC_GAP)
    corners = lgbf.parse_corners(lgbf.SCAD)
    rows, bad = [], False
    for label, c in corners.items():
        if a.only and label not in a.only:
            continue
        r = build_corner(label, c, env, keep)
        ok = (r["bodies"] == 1 and r["leg_sweep_x_bay_mm3"] < lgbf.CLASH_MM3
              and min(r["bolt_flange_mm3"]) >= BOLT_MIN_FLANGE)
        bad |= not ok
        print(f"{'OK  ' if ok else 'FAIL'} {label:10s} {r['volume']:8.0f} mm3 {r['mass_g']:5.1f} g "
              f"bodies {r['bodies']} {r['body_mm3'][:3]}  leg x bay {r['leg_sweep_x_bay_mm3']} "
              f"flange {r['flange_mm3']} liner {r['liner_mm3']}")
        print(f"     bolts {r['bolts']}  flange around each {r['bolt_flange_mm3']}  "
              f"moved {r['moved']}")
        for lb in r["loose"]:
            print(f"     LOOSE body {lb['mm3']} mm3 at leg-local {lb['local_bounds']}")
        rows.append(r)
        if not a.check:
            m = cbc.tri(r["bay"])
            m.export(os.path.join(OUT, f"lg_r6_3_0in_bay_{label}.stl"))
            m.copy().apply_transform(np.linalg.inv(r["tf"])).export(
                os.path.join(OUT, f"lg_r6_3_0in_bay_{label}_print.stl"))
    if not a.check:
        write_params(rows)
    print(f"\nRESULT: {'FAIL' if bad else 'PASS'}")
    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
