#!/usr/bin/env python3
"""cargo_observer_sensor_fit.py -- place the cargo Observer's remote sensor
heads (camera, dot projector, ToF) and prove the placement.

Why this tool exists
--------------------
The cargo Observer is a hoist monitor and nadir imager: its camera and dot
projector are REMOTE heads off the Observer board (J_CAM / J_LASER / J_TOF,
avionics/kicad/Observer/Observer.md "Cargo install"), separated by a ~75 mm
stereo baseline so the pair is a structured-light 3-D imager
(docs/OBSERVER_LASER_ANALYSIS.md SS4.5).  Owner direction 2026-11-01: put the
heads where they do NOT interfere with the optional third battery (Tattu 6S
1600 in the cargo corridor, Y ~296..366, Zc 190; docs/BATTERY_TRIM_ENDURANCE_
OPTIONS.md) and still give the full field of view hoist operations and
imagery need.

What was ruled out, and why (2026-11-01, measured, not assumed)
---------------------------------------------------------------
  * OVERHEAD on the hoist line: the third pack and the stowed payload box
    occupy the bay centreline above and below Z 167.
  * ON the aft Observer tray: the tray stands 2.2 mm behind the box, so a
    head there looks down a 2.2 mm slot while stowed, and with the box out
    its 33 deg field is clipped by the aperture's aft edge (Y 410.7); tilting
    it 17.5 deg forward to clear the edge leaves the lowered load at the
    edge of the frame.
  * AFT belly strip (Y 410.7..426.7, behind the doors, ahead of the splice
    collar ring): 12 mm of height under the tray and 11 mm of width beside
    it -- a 28 mm camera body does not fit.
The FORWARD belly strip -- ahead of the door aperture (CARGO_BAY_Y_FWD), under
the chin shelf, outboard of the door-servo gateway tray -- has a flat 2 mm belly
(skin Z 80 / 82 out to X +/-45, section-probed) and room for all three heads.

The check (same conventions as cargo_layout_fit.py)
---------------------------------------------------
  * each head is a box seated on the belly's inner skin and cut through it by
    a bezel (the hull re-cut opens the bezel holes, merge_cargo_interior.py);
  * every head is booleaned against every cargo_layout_fit envelope and the
    third-pack keep-out at the 2.0 mm static gap, and against the published
    shell with its own belly seat removed;
  * each head's FIELD-OF-VIEW cone (apex at its lens, half-angle FOV/2,
    boresight tilted TILT_AFT_DEG toward the hoist line) is checked for the
    two ranges hoist operations need -- the load just clear of the belly
    (0.3 m) and at the 5 ft (1.5 m) laser design range -- by asking whether the
    hoist line's ground track falls inside the cone at each range.

Inputs labelled ASSUMED are envelopes, not datasheet figures; replace them
when the heads are procured (TODO.md).

Run:  /usr/bin/python3 tools/cargo_observer_sensor_fit.py [--write-scad]

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CEH (GitHub Stab-Rabbit-coding)
AI note: Written by Claude (Claude Opus 5.5, Anthropic) under the author's
         direction, 2026-11-01, per AGENTS.md AI attribution.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import math
import os
import sys

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import cargo_layout_fit as clf  # noqa: E402  single source of cargo stations
import hull_datums as hd  # noqa: E402

SCAD_OUT = os.path.join(REPO, "airframe", "openscad", "fuselage", "cargo",
                        "cargo_observer_sensor_params.scad")
STATIC_GAP = 2.0          # static-to-static (cargo_layout_fit convention)
SKIN_T = 2.0              # belly skin, published shell
BELLY_OUTER_Z = hd.BELLY_Z  # 80.0, flat across the forward strip (probed)
BELLY_INNER_Z = BELLY_OUTER_Z + SKIN_T

# Third battery keep-out (docs/BATTERY_TRIM_ENDURANCE_OPTIONS.md: bare Tattu
# 6S 1600, 70 x 42 x 41 mm, "fits only at Y ~302-372, Zc 190"; the fit tool
# places it at Y 294..368 with lips).  Owner 2026-11-01: do not interfere.
THIRD_PACK = (-21.0 - 1.5, 21.0 + 1.5, 294.0, 368.0, 190.0 - 20.5 - 1.5, 190.0 + 20.5 + 1.5)

# Heads.  Camera: the "28 mm standard FPV camera body" the cargo bezel is
# sized for (Observer.md: 29 x 29 bezel, O16 lens aperture).  Depth ASSUMED
# 25 mm incl. lens.  FOV 33 deg (OBSERVER_LASER_ANALYSIS SS4.5 working
# figure).  ToF: Benewake TFmini-S 42 x 15 x 16 mm [REF-SENSOR-002], lenses
# down.  Projector: iC-WKN-driven diode + DOE pseudo-random dot head,
# envelope ASSUMED O14 x 26 mm.
CAM = (28.0, 28.0, 25.0)          # X, Y, Z
TOF = (16.0, 42.0, 15.0)          # X, Y (long axis fore/aft), Z
PROJ_D, PROJ_H = 14.0, 26.0
FOV_DEG = 33.0

# Layout: a belly "sensor bar" across X ahead of the door aperture.  Camera to
# port, projector to starboard, BASELINE apart (SS4.5 recommends ~75 mm;
# 76 is what the strip gives clear of the gateway tray), ToF beside the camera,
# inboard, so the range spot sits between the stereo pair.
BASELINE = 76.0
CAM_X = hd.X_CL + BASELINE / 2        # +38.0 (port)
PROJ_X = hd.X_CL - BASELINE / 2       # -38.0 (stbd)
# Fore/aft: the aft faces sit STATIC_GAP ahead of the door aperture's forward
# edge, so no head rides on a door knuckle and the bezels stay in solid belly.
HEAD_Y1 = hd.CARGO_BAY_Y_FWD - STATIC_GAP     # 302.7
CAM_YC = HEAD_Y1 - CAM[1] / 2                 # 288.7
PROJ_YC = HEAD_Y1 - PROJ_D / 2
TOF_X = CAM_X - CAM[0] / 2 - STATIC_GAP - TOF[0] / 2   # inboard of the camera
TOF_YC = HEAD_Y1 - TOF[1] / 2
# Boresight tilt toward the hoist line (aft).  Chosen so the hanging load is
# inside the field at BOTH 0.3 m and 1.5 m below the belly (see check()).
TILT_AFT_DEG = 8.0
RANGES_MM = (300.0, 1524.0)           # load just clear / 5 ft laser design range


def head_boxes():
    """{name: (trimesh box, lens point (x, y, z))} -- port-side layout."""
    z0 = BELLY_INNER_Z
    out = {
        "camera": (clf.box(CAM_X - CAM[0] / 2, CAM_X + CAM[0] / 2, CAM_YC - CAM[1] / 2,
                           CAM_YC + CAM[1] / 2, z0, z0 + CAM[2]), (CAM_X, CAM_YC, BELLY_OUTER_Z)),
        "ToF": (clf.box(TOF_X - TOF[0] / 2, TOF_X + TOF[0] / 2, TOF_YC - TOF[1] / 2,
                        TOF_YC + TOF[1] / 2, z0, z0 + TOF[2]), (TOF_X, TOF_YC, BELLY_OUTER_Z)),
        "projector": (clf.cyl("z", PROJ_X, PROJ_YC, z0, z0 + PROJ_H, PROJ_D / 2),
                      (PROJ_X, PROJ_YC, BELLY_OUTER_Z)),
    }
    return out


def in_cone(apex, target, tilt_deg, half_deg):
    """Is target inside a cone at apex, boresight = nadir tilted aft by tilt?"""
    t = math.radians(tilt_deg)
    axis = np.array([0.0, math.sin(t), -math.cos(t)])
    v = np.asarray(target, float) - np.asarray(apex, float)
    ang = math.degrees(math.acos(float(np.dot(axis, v) / np.linalg.norm(v))))
    return ang <= half_deg, ang


def check():
    fails = []
    heads = head_boxes()
    L = clf.layout_t5()
    third = clf.to_man(clf.box(*THIRD_PACK))
    print("cargo Observer sensor heads -- forward belly strip (aircraft datum R2, mm)")
    for name, (tm, lens) in heads.items():
        lo, hi = tm.bounds
        print(f"  {name:10s} X {lo[0]:+6.1f}..{hi[0]:+6.1f}  Y {lo[1]:6.1f}..{hi[1]:6.1f}  "
              f"Z {lo[2]:5.1f}..{hi[2]:5.1f}   lens at belly Y {lens[1]:.1f}")
    print("\ninterference at the 2.0 mm static gap (blank = clear):")
    names = list(heads)
    for i, a in enumerate(names):
        ma = clf.to_man(clf.dilate(heads[a][0], STATIC_GAP))
        hits = []
        for k, e in L.items():
            v = (ma ^ clf.to_man(e["solid"])).volume()
            if v > 0.5:
                hits.append(f"{k} {v:.0f}")
        v = (ma ^ third).volume()
        if v > 0.5:
            hits.append(f"THIRD PACK {v:.0f}")
        for b in names[i + 1:]:
            v = (clf.to_man(heads[a][0]) ^ clf.to_man(heads[b][0])).volume()
            if v > 0.5:
                hits.append(f"{b} {v:.0f}")
        print(f"  {a:10s} {'; '.join(hits) or 'clear'}")
        fails += [f"{a} x {h}" for h in hits]
    print("\nshell (published, belly seat + bezel removed):")
    shell = clf.to_man(clf.shell_after_merge(trimesh.load(clf.SHELL)))
    for name, (tm, _) in heads.items():
        lo, hi = tm.bounds
        body = clf.box(lo[0], hi[0], lo[1], hi[1], BELLY_INNER_Z + 0.5, hi[2])
        v = (clf.to_man(clf.dilate(body, 1.0)) ^ shell).volume()
        print(f"  {name:10s} {'clear' if v < 0.5 else f'FOUL {v:.0f} mm3'}")
        if v >= 0.5:
            fails.append(f"{name} x shell")
    print(f"\nfield of view: {FOV_DEG:.0f} deg, boresight {TILT_AFT_DEG:.1f} deg aft of nadir; "
          f"target = hoist line Y {clf.HOIST_Y:.1f} on the centreline")
    for name, (_, lens) in heads.items():
        if name == "ToF":
            continue
        row = []
        for r in RANGES_MM:
            ok, ang = in_cone(lens, (hd.X_CL, clf.HOIST_Y, BELLY_OUTER_Z - r), TILT_AFT_DEG,
                              FOV_DEG / 2)
            row.append(f"{r / 304.8:.1f} ft: {ang:4.1f} deg {'in' if ok else 'OUT'}")
            if not ok:
                fails.append(f"{name} FOV at {r:.0f} mm")
        print(f"  {name:10s} " + " | ".join(row))
    # jumper-lead lengths: lens-side connector to the Observer board's sensor
    # end (OBSERVER tray forward face, centreline, mid-height), routed along
    # the belly then up the tray face (Manhattan) + 15 % service loop.
    board = (hd.X_CL, clf.OBSERVER_Y0, clf.OBSERVER_Z0 + clf.OBSERVER_W / 2)
    print("\njumper leads (Manhattan route along the belly to the Observer tray + 15 %):")
    for name, (tm, lens) in heads.items():
        top = tm.bounds[1]
        d = abs(lens[0] - board[0]) + abs(board[1] - top[1]) + abs(board[2] - BELLY_INNER_Z)
        print(f"  {name:10s} {d * 1.15:5.0f} mm ({d * 1.15 / 25.4:4.1f} in)")
    print(f"\nRESULT: {'PASS' if not fails else 'FAIL (' + '; '.join(fails) + ')'}")
    return 1 if fails else 0


def write_scad():
    names = dict(CAM_X=CAM_X, CAM_YC=CAM_YC, PROJ_X=PROJ_X, PROJ_YC=PROJ_YC, TOF_X=TOF_X,
                 TOF_YC=TOF_YC, BELLY_OUTER_Z=BELLY_OUTER_Z, BELLY_INNER_Z=BELLY_INNER_Z,
                 TILT_AFT_DEG=TILT_AFT_DEG, BASELINE=BASELINE)
    lines = ["// GENERATED by tools/cargo_observer_sensor_fit.py --write-scad -- do not edit.",
             "// Aircraft datum R2, mm.  License: CERN-OHL-W-2.0"]
    lines += [f"{k} = {v:.4f};" for k, v in names.items()]
    lines += [f"CAM = [{CAM[0]}, {CAM[1]}, {CAM[2]}];", f"TOF = [{TOF[0]}, {TOF[1]}, {TOF[2]}];",
              f"PROJ_D = {PROJ_D}; PROJ_H = {PROJ_H};"]
    with open(SCAD_OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"wrote {os.path.relpath(SCAD_OUT, REPO)}")


if __name__ == "__main__":
    if "--write-scad" in sys.argv:
        write_scad()
    sys.exit(check())
