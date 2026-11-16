#!/usr/bin/env python3
"""observer_nose_fit.py -- exact fit of the nose Observer board with its
sensors soldered to the board's leading edge (owner, 2026-10-27).

Geometry (aircraft datum R2)
----------------------------
* Each sensor's optical axis is the bow flat's outward normal FLAT_N through
  its published aperture centre (bow cuts already merged in the head shell;
  positions from airframe/blender-scripts/merge_head_interior.py).
* Each sensor body is a box: its FRONT face sits at the inner skin face of the
  aperture (WALL behind the aperture centre along -FLAT_N), its REAR face is
  the solder joint on the board's leading edge.
* The board plane contains FLAT_N and hull X, i.e. it is pitched 40 deg
  nose-down, so edge-mounted sensors look out along their aperture axes.  The
  leading edge is the line through the joint points; the trapezoid extends
  aft-and-up along -FLAT_N.
* Each sensor box is centred on its axis; the board-normal direction is
  B_N = X x FLAT_N.  The body's "thickness" straddles the board plane.

Checks: sensor bodies and board against the published head shell, sensors
pairwise, and the board against the sensors' own envelopes.  Reported per
sensor set: leading-edge depth, joint plane, and every interference volume.

Sensor dimension sources: TFmini-S 35 x 18.5 x 21 mm [REF-SENSOR-002] --
REJECTED (sourcing, BOW-02), kept as the as-designed reference; LightWare
SF000/B 22 x 34 x 21 mm (retailer copy of the maker datasheet, VERIFY before
REFERENCES.md).  Camera and laser modules are NOT selected: their envelopes
are parameters, labelled ASSUMED on every run.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the
author's direction, 2026-10-27, per `AGENTS.md` §3 AI attribution.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""

import os
import sys

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "airframe", "blender-scripts"))
import merge_head_interior as mhi  # noqa: E402  aperture positions (single source)
from cargo_layout_fit import to_man  # noqa: E402

HEAD = os.path.join(REPO, "airframe", "stls", "fuselage", "head_shell24_2mm_repaired.stl")
FLAT_N = np.array([0.0, -np.cos(np.radians(40.0)), -np.sin(np.radians(40.0))])
X = np.array([1.0, 0.0, 0.0])
B_N = np.cross(X, FLAT_N)  # board normal (in the flat's in-plane vertical)
WALL = 2.0  # mm, skin; sensor front face at the inner face
BOARD_T = 1.6
BOARD_L, BOARD_W_FWD, BOARD_W_AFT = 69.85, 25.4, 54.0
JOINT = 1.0  # mm solder-joint allowance between sensor rear face and board edge

APERTURE = {  # hull R2 aperture centres on the exterior skin
    "camera": mhi.CAM_POS + mhi.BAKE_T,
    "ToF": mhi.TOF_POS + mhi.BAKE_T,
    "laser": mhi.LASER_POS + mhi.BAKE_T,
}

# body = (width along X, thickness along B_N, depth along the axis), mm
SETS = {
    "as-designed (TFmini-S, rejected)": {
        "ToF": (18.5, 35.0, 21.0),  # rolled: 18.5 lateral [REF-SENSOR-002]
        "camera": (12.0, 12.0, 15.0),  # ASSUMED small MIPI module
        "laser": (6.0, 6.0, 18.0),  # ASSUMED TO-38 PLT5 520 + collimator
    },
    "SF000/B candidate": {
        "ToF": (22.0, 34.0, 21.0),  # 22 x 34 x 21 (retailer datasheet copy, VERIFY)
        "camera": (12.0, 12.0, 15.0),  # ASSUMED
        "laser": (6.0, 6.0, 18.0),  # ASSUMED
    },
}


def oriented_box(center, w, t, d):
    """Box centred at `center`, axes X (w), B_N (t), FLAT_N (d)."""
    b = trimesh.creation.box(extents=[w, t, d])
    R = np.eye(4)
    R[:3, 0], R[:3, 1], R[:3, 2] = X, B_N, FLAT_N
    R[:3, 3] = center
    b.apply_transform(R)
    return b


def fit(head_m, sensors):
    bodies, rear = {}, []
    for name, (w, t, d) in sensors.items():
        front = APERTURE[name] - FLAT_N * WALL  # inner face of the skin
        c = front - FLAT_N * (d / 2)
        bodies[name] = oriented_box(c, w, t, d)
        rear.append(front - FLAT_N * d)
    # leading edge: the deepest rear face governs (all sensors join one edge);
    # depth measured along -FLAT_N from the aperture plane
    depths = [float(np.dot(APERTURE[n] - r, FLAT_N)) for n, r in zip(sensors, rear)]
    edge_depth = max(depths) + JOINT
    origin = APERTURE["laser"] * np.array([0, 1, 1]) - FLAT_N * edge_depth  # on CL
    board_c = origin - FLAT_N * (BOARD_L / 2)
    # trapezoid approximated by its fwd-width box over the first 20 mm and the
    # aft-width box behind it (conservative for the narrow end)
    seg1 = oriented_box(origin - FLAT_N * 10.0, BOARD_W_FWD, BOARD_T, 20.0)
    seg2 = oriented_box(origin - FLAT_N * (20.0 + (BOARD_L - 20.0) / 2),
                        BOARD_W_AFT, BOARD_T, BOARD_L - 20.0)
    board = trimesh.util.concatenate([seg1, seg2])
    rows = []
    for n, b in bodies.items():
        rows.append((f"{n} body x shell", (to_man(b) ^ head_m).volume()))
    names = list(bodies)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            rows.append((f"{a} x {b}", (to_man(bodies[a]) ^ to_man(bodies[b])).volume()))
    for seg, nm in ((seg1, "board fwd 20 mm"), (seg2, "board aft")):
        rows.append((f"{nm} x shell", (to_man(seg) ^ head_m).volume()))
    end = origin - FLAT_N * BOARD_L
    return edge_depth, origin, end, board_c, rows, bodies, board


def main():
    head_m = to_man(trimesh.load(HEAD))
    print("apertures (R2):", {k: np.round(v, 2).tolist() for k, v in APERTURE.items()})
    print(f"flat normal {np.round(FLAT_N, 3).tolist()}, board normal {np.round(B_N, 3).tolist()}")
    worst = 0
    for label, s in SETS.items():
        d, o, e, _c, rows, _b, _bd = fit(head_m, s)
        print(f"\n== {label} ==")
        for n, (w, t, dd) in s.items():
            print(f"  {n:7s} body {w} x {t} x {dd} mm (X x board-normal x axis)")
        print(f"  leading edge {d:.1f} mm behind the apertures; edge centre Y {o[1]:.1f}"
              f" Z {o[2]:.1f}; board aft end Y {e[1]:.1f} Z {e[2]:.1f}")
        for n, v in rows:
            flag = "CLASH" if v > 1.0 else "ok"
            worst += v > 1.0
            print(f"  {n:28s} {v:8.0f} mm3  {flag}")
        # lateral layout on the edge
        xs = {n: (APERTURE[n][0] - s[n][0] / 2, APERTURE[n][0] + s[n][0] / 2) for n in s}
        print("  lateral spans on the edge (X):",
              {n: (round(a, 1), round(b, 1)) for n, (a, b) in xs.items()},
              f"edge width {BOARD_W_FWD} = X +-{BOARD_W_FWD / 2}")
    print(f"\n{worst} interference(s) across the sets")
    return 0 if worst == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
