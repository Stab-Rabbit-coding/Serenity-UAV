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
from bhd02_option_study import bolt_group, dilate  # noqa: E402

OUT = os.path.join(REPO, "airframe", "stls", "fuselage", "landing-gear")
PARAMS = os.path.join(REPO, "airframe", "blender-scripts", "lg_bay_corner_params.py")

SLIVER_MM3 = 1.0          # mm^3; below this a split-off piece is boolean residue
STATIC_GAP = 2.0          # mm, the layout tool's static gap to fixed parts
# 2026-10-11: + the wings (the aft plate top and upper M3 sat under the wing
# root, 267/339 + 60/61 mm^3), the tilt brackets (fore M3 nut/driver access,
# 81 mm^3) and the doors closed and swept 0..145 (aft M3 keep-outs, 2-6 mm^3).
# Every bolt that then fails slides down its flange; the bay is trimmed clear.
KEEPOUTS = ("TACCO CN2 port", "TACCO CN3 stbd", "chin shelf",
            "wing port", "wing stbd", "tilt bracket port", "tilt bracket stbd",
            "door port (closed)", "door stbd (closed)", "door port swept", "door stbd swept")
BOLT_KEEP_D = 3.4 + 2 * 2.5   # O8.4 washer / nut / driver, as the census
BOLT_T = (-30.0, 20.0)    # bore extent along e_x, as the hull merge
BOLT_SLIDE_MAX = 30.0     # mm a blocked bolt may slide down its side flange
BOLT_MIN_FLANGE = 150.0   # mm^3 of flange around a bolt's O8.4 keep-out (a fully
                          # seated nominal bolt measures 275 mm^3; 150 = more
                          # than half of the washer footprint on material)
BOLT_MIN_COLLAR = 150.0   # mm^3 of hull seat collar under it (same reasoning)
T = mci.BAY_PLATE_T
COWL_H = mci.COWL_H
BOLT_CAP_4MM = 2310.0     # N, bearing: wall + 5 mm boss + 4 mm backing plate (owner
                          # 2026-10-10; 2,100 N at 3 mm, landing_gear_r6_sizing.py)
RHO, INFILL = 1.30e-3, 0.40   # CF-PETG g/mm^3 solid, 40 % gyroid (repo convention)


def feat(station: str, name: str, tf: np.ndarray) -> Manifold:
    p = lgbf.render(lgbf.SCAD, station, name, lgbf.FEATURES[name][0])
    return lgbf.posed(p, tf)


def aper_half(v: float) -> float:
    """Aperture half-width at plate-frame height v (the trapezoid, mci values)."""
    t = (v - mci.BAY_APER_ZB0) / mci.BAY_APER_L
    return (mci.BAY_APER_W_BOT + t * (mci.BAY_APER_W_TOP - mci.BAY_APER_W_BOT)) / 2.0


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
    # Bolts (BHD-02 / BHD-02i).  Each starts at its nominal centre; it is
    # accepted only when (1) its O8.4 keep-out clears the keep-outs, (2) the
    # printed flange surrounds the hole, and (3) the hull's seat COLLAR lies
    # under it -- the flank curls under at the lower-forward corner and the
    # nominal bolt there clamped over air (3.4 / 5.4 mm^3 of flange, measured
    # 2026-10-10).  A rejected bolt slides along its own side-flange CENTRELINE
    # (u follows the trapezoid, so the hole never breaks into the aperture):
    # lower bolts up, upper bolts down, in 0.5 mm steps.
    collar = mci.lg_skin_layer(env, org, ex, ey, ez, mci.BAY_PLATE_WB, mci.BAY_PLATE_W,
                               mci.BAY_PLATE_ZB0, zb1, T, T + mci.LG_SEAT_D)
    bolts, moved = [], []
    for u0, v0 in mci.lg_nominal_bolts():
        step = 0.5 if v0 < 0 else -0.5
        dv = 0.0
        while True:
            v = v0 + dv
            u = u0 if dv == 0.0 else np.sign(u0) * (aper_half(v) + mci.BAY_FLANGE / 2.0)
            k = bolt_cyl(org, ex, ey, ez, u, v, BOLT_KEEP_D)
            ok = ((k ^ keep).volume() <= 0.05
                  and (k ^ flange).volume() >= BOLT_MIN_FLANGE
                  and (k ^ collar).volume() >= BOLT_MIN_COLLAR)
            if ok:
                break
            dv += step
            if abs(dv) > BOLT_SLIDE_MAX:
                raise RuntimeError(f"{label}: bolt ({u0:+.1f},{v0:+.1f}) finds no seat "
                                   f"within {BOLT_SLIDE_MAX} mm")
        bolts.append((round(float(u), 2), round(float(v), 2)))
        if dv:
            moved.append(dict(nominal=(u0, v0), to=bolts[-1], slid_mm=abs(dv)))
    holes = Manifold.batch_boolean([bolt_cyl(org, ex, ey, ez, u, v, mci.LG_M3_D)
                                    for u, v in bolts], OpType.Add)
    seat = [(bolt_cyl(org, ex, ey, ez, u, v, BOLT_KEEP_D) ^ flange).volume() for u, v in bolts]
    under = [(bolt_cyl(org, ex, ey, ez, u, v, BOLT_KEEP_D) ^ collar).volume() for u, v in bolts]
    bay = bay - holes - feat(st, "cuts", tf)
    legp = lgbf.render(lgbf.SCAD, st, "leg (thigh+shin+foot)",
                       lgbf.FEATURES["leg (thigh+shin+foot)"][0])
    leg_x = (lgbf.swept_leg(legp, tf) ^ bay).volume()
    parts = sorted(bay.decompose(), key=lambda m: -m.volume())
    # Zero-volume boolean slivers (coplanar-face residue) are not bodies; drop
    # them and say so, as generate_wing_root_flange.keep_plate() does.
    slivers = [p for p in parts[1:] if p.volume() < SLIVER_MM3]
    if slivers:
        print(f"     {label}: dropped {len(slivers)} sliver(s) < {SLIVER_MM3} mm^3")
        parts = [parts[0]] + [p for p in parts[1:] if p.volume() >= SLIVER_MM3]
        bay = Manifold.batch_boolean(parts, OpType.Add) if len(parts) > 1 else parts[0]
    inv = np.linalg.inv(tf)
    loose = [dict(mm3=round(m.volume(), 1), local_bounds=trimesh.transform_points(
        np.array(m.bounding_box()).reshape(2, 3), inv).round(1).tolist()) for m in parts[1:]]
    return dict(label=label, bay=bay, tf=tf, bolts=bolts, moved=moved,
                bolt_flange_mm3=[round(x, 1) for x in seat],
                bolt_collar_mm3=[round(x, 1) for x in under],
                bolt_group=bolt_loads(bolts),
                bodies=len(parts), body_mm3=sorted((round(p.volume(), 1) for p in parts),
                                                   reverse=True),
                loose=loose, leg_sweep_x_bay_mm3=round(leg_x, 2), volume=bay.volume(),
                mass_g=round(bay.volume() * RHO * INFILL, 1),
                flange_mm3=round(flange.volume(), 1), liner_mm3=round(liner.volume(), 1))


def bolt_loads(bolts) -> dict:
    """LG-02 bolt group for this corner's pattern (tools/landing_gear_r6_sizing.py
    method: hip moment 48.8 N.m prying about the lowest bolt line, F_leg 610 N
    shared by all 4 in shear; bearing cap 2,310 N = wall + 5 mm boss + 4 mm
    backing plate, owner 2026-10-10)."""
    vmin = min(v for _u, v in bolts)
    return bolt_group([v - vmin for _u, v in bolts if v - vmin > 1e-6], cap=BOLT_CAP_4MM)


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
              and min(r["bolt_flange_mm3"]) >= BOLT_MIN_FLANGE
              and min(r["bolt_collar_mm3"]) >= BOLT_MIN_COLLAR
              and r["bolt_group"]["fos_bearing"] >= 4.0)
        bad |= not ok
        print(f"{'OK  ' if ok else 'FAIL'} {label:10s} {r['volume']:8.0f} mm3 {r['mass_g']:5.1f} g "
              f"bodies {r['bodies']} {r['body_mm3'][:3]}  leg x bay {r['leg_sweep_x_bay_mm3']} "
              f"flange {r['flange_mm3']} liner {r['liner_mm3']}")
        print(f"     bolts {r['bolts']}  flange {r['bolt_flange_mm3']}  collar "
              f"{r['bolt_collar_mm3']}  moved {r['moved']}")
        print(f"     bolt group {r['bolt_group']}")
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
