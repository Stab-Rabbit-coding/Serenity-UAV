#!/usr/bin/env python3
"""gen_bay_a_fwd_mounts.py -- Bay A forward node mounts and the canonical
bridge-roof access hatch, as installed-position R2 STLs (plan 2026-11-01-001
U3, R2; KTD2, KTD7).

Every station comes from tools/head_layout_fit.py (single source).  Parts:

  bay_a_cn1_drawer.stl   BONDED.  Floor under CN1 (Z 203..206, Y 62..120),
                         clipped to the hull's inner skin so its edges bond to
                         the skin; side walls X +-(19.5..21.9) from the floor to
                         the FC1 shelf (Z 228.5), running aft to Y 146 so the
                         shelf has a seat over the CN1 run; forward stop wall
                         at Y 59.5..61.5.  Two M2.5 PGND lug bosses.
  bay_a_cn1_gate.stl     REMOVABLE.  Low snap bar across CN1's aft end
                         (Z 206..209) so the cables leave over it.
  bay_a_fc1_shelf.stl    REMOVABLE.  Floor under FC1 (Z 228.5..230.5,
                         Y 88..146) screwed to the drawer wall tops (4 x M2.5),
                         with two slot pairs each side (X +-(22..28)) for two
                         16 mm cam straps (BATT-STRAP-CAM) over FC1; each
                         strap wraps the 2 mm plate bridge between its slots.
  bay_a_hatch_cover.stl  REMOVABLE.  The canonical bridge-roof panel cut from
                         the merged hull (spikes and all), 8 x M2.5 clearance
                         holes.
  bay_a_hatch_flange.stl BONDED.  6 mm landing flange under the cut's sides
                         (aft of Y 90, clear of the Observer) and aft edge,
                         3 mm under the skin, with 8 insert bosses.  The
                         cover's forward edge is a 6 mm tongue that tucks
                         under the fixed skin at the Y 60 window frame.
  head_cargo_shell24_2mm_merged_hatch.stl  the merged hull with the hatch
                         opening cut (the published merged hull is NOT
                         modified in place; owner rule: rebuild from source).

SERVICE PATH (R2):
  1. Remove the 8 hatch screws, lift the cover's aft edge and draw it aft
     to free the forward tongue (opening Y 60..137, X +-27).
  2. FC1: release both cam straps, unplug, lift the FC1 pouch nose-up and out
     (its aft 9 mm sits under the Y 137 frame; tilt about the aft edge).
  3. FC1 shelf: remove 4 screws, lift out.
  4. CN1: unsnap the aft gate, unplug, slide CN1 aft 26 mm (clear of the
     Observer, which ends at Y 86) and tilt it out through the opening.
  Reverse to install.  The Observer stays in place throughout.

Retention load: limit 79.4 g in every direction (the head-cell rail's case,
docs/BATTERY_MOUNT.md §8), FOS 3.0 -> 3 x 0.058 kg x 79.4 x g0 = 135.5 N per
node.  The strap/snap/insert allowables are not yet cited: statics are an
OPEN item (WBS), reported by --statics as PROVISIONAL.

Material: printable composite first (owner material order); SLS PA12-CF per
docs/SLS_MATERIAL_SELECTION_3DSYSTEMS.md.

Run:
    /usr/bin/python3 tools/gen_bay_a_fwd_mounts.py            # write STLs
    /usr/bin/python3 tools/gen_bay_a_fwd_mounts.py --statics  # loads only

Use /usr/bin/python3: the repository .venv hides trimesh and manifold3d.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the
author's direction, 2026-11-01, per `AGENTS.md` §3 AI attribution.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""

import argparse
import os
import sys

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import head_layout_fit as h  # noqa: E402  single source of stations
import cargo_layout_fit as clf  # noqa: E402  pouch size
from cargo_layout_fit import box, cyl, to_man  # noqa: E402

REPO = h.REPO
OUT_DIR = os.path.join(REPO, "airframe", "stls", "fuselage", "head")
HULL_OUT = os.path.join(REPO, "airframe", "stls", "fuselage",
                        "head_cargo_shell24_2mm_merged_hatch.stl")
SERVICE_PATH = """SERVICE PATH (R2):
  1. Remove the 8 hatch screws, lift the cover's aft edge and draw it aft
     to free the forward tongue (opening Y 60..137, X +-27).
  2. FC1: release both cam straps, unplug, lift the FC1 pouch nose-up and out
     (its aft 9 mm sits under the Y 137 frame; tilt about the aft edge).
  3. FC1 shelf: remove 4 screws, lift out.
  4. CN1: unsnap the aft gate, unplug, slide CN1 aft 26 mm (clear of the
     Observer, which ends at Y 86) and tilt it out through the opening.
  Reverse to install.  The Observer stays in place throughout."""
# (also quoted in the module docstring; this constant is the source)

G0 = 9.80665
LIMIT_G, FOS = 79.4, 3.0
NODE_KG = 0.058  # PB2-I 13 g + cape (TACCO 40 / Pilot 31) + pouch 5 g, heavier case

# Drawer / shelf geometry (mm)
FLOOR_T, SHELF_T = 3.0, 2.0
FLANGE_SHIFT = 3.0  # hatch flange depth under the skin (not 2.0: see hatch_parts)
WALL_X0, WALL_X1 = 19.5, 21.9  # 1 mm off the pouch side (X 18.5), 2.4 mm wall
CN1_TOP = h.CN1F_Z0 + clf.NODE_T  # 228
SHELF_Z0 = CN1_TOP + 0.5  # 228.5
DRAWER_Y1 = h.FC1F_Y0 + clf.NODE_L  # walls run aft to the FC1 shelf's aft end
STOP_T = 2.0
GATE_H, GATE_T = 3.0, 2.0
STRAP_W, SLOT_W = 16.0, 2.0  # 16 mm cam strap; 2 mm slots, 2 mm bridge between
STRAP_X0, STRAP_X1 = 22.0, 28.0
STRAP_Y = (h.FC1F_Y0 + 8.0, h.FC1F_Y0 + 34.0)  # strap slot starts (16 mm slots)
M25_CLEAR, M25_INSERT, BOSS_D = 2.9, 3.6, 7.0  # insert bore: verify against the insert datasheet


def _mesh(m, min_body_mm3=1.0):
    """Manifold -> trimesh, welded, with boolean slivers (< min_body_mm3) dropped."""
    mm = m.to_mesh()
    tm = trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts))
    tm.merge_vertices()
    bodies = [b for b in tm.split(only_watertight=False) if abs(b.volume) >= min_body_mm3]
    return trimesh.util.concatenate(bodies) if len(bodies) > 1 else bodies[0]


def inner_half_width(hull, y, z):
    """First skin hit from the centreline going +X (the hull is port/stbd
    symmetric to 0.5 mm, gated separately)."""
    loc, _, _ = hull.ray.intersects_location([[0.0, y, z]], [[1.0, 0.0, 0.0]])
    return float(loc[:, 0].min()) if len(loc) else np.nan


def skin_clipped_plate(hull, y0, y1, z0, z1, step=2.0, bite=0.0):
    """Plate between y0..y1 whose outline follows the inner skin: the half-width
    at each station is the NARROWER of the skin at the plate's top and bottom
    faces, plus `bite` (0 = touching for a bonded edge, negative = clearance)."""
    ys = np.arange(y0, y1 + 1e-6, step)
    if ys[-1] < y1:
        ys = np.append(ys, y1)
    w = np.array([min(inner_half_width(hull, y, z0 + 0.05), inner_half_width(hull, y, z1 - 0.05))
                  for y in ys]) + bite
    if np.isnan(w).any():
        raise ValueError(f"no skin found for plate Y {y0}..{y1} Z {z0}..{z1}")
    pts = [(-wi, yi) for yi, wi in zip(ys, w)] + [(wi, yi) for yi, wi in zip(ys[::-1], w[::-1])]
    poly = trimesh.path.polygons.Polygon(pts)
    m = trimesh.creation.extrude_polygon(poly, z1 - z0)
    m.apply_translation([0.0, 0.0, z0])
    return m


def cn1_drawer(hull):
    ny0, ny1 = h.CN1F_Y0, h.CN1F_Y0 + clf.NODE_L
    floor = to_man(skin_clipped_plate(hull, ny0 - STOP_T, ny1, h.CN1F_Z0 - FLOOR_T, h.CN1F_Z0))
    m = floor
    for s in (1, -1):
        x0, x1 = sorted((s * WALL_X0, s * WALL_X1))
        m = m + to_man(box(x0, x1, ny0 - STOP_T, DRAWER_Y1, h.CN1F_Z0 - FLOOR_T, SHELF_Z0))
    m = m + to_man(box(-WALL_X1, WALL_X1, ny0 - STOP_T - 0.5, ny0 - 0.5, h.CN1F_Z0, CN1_TOP))
    # PGND lug bosses (M2.5 insert) on the floor, port and stbd, at the aft
    # end where the floor is widest (at Y 68 they sank 520 mm^3 into the skin)
    for s in (1, -1):
        b = cyl("z", s * (WALL_X1 + 4.0), ny1 - 10.0, h.CN1F_Z0 - FLOOR_T, h.CN1F_Z0 + 4.0,
                BOSS_D / 2)
        m = m + to_man(b) - to_man(cyl("z", s * (WALL_X1 + 4.0), ny1 - 10.0, h.CN1F_Z0 - 0.5,
                                       h.CN1F_Z0 + 4.1, M25_INSERT / 2))
    # screw bosses on the wall tops for the FC1 shelf (4 x M2.5 insert)
    for s in (1, -1):
        for y in (h.FC1F_Y0 + 4.0, DRAWER_Y1 - 4.0):
            x = s * 0.5 * (WALL_X0 + WALL_X1)
            m = m - to_man(cyl("z", x, y, SHELF_Z0 - 6.0, SHELF_Z0 + 0.1, M25_INSERT / 2))
    return _mesh(m - to_man(hull))  # conform: forward of Y ~76 the floor seats ON the chin skin


def cn1_gate():
    ny1 = h.CN1F_Y0 + clf.NODE_L
    return box(-WALL_X1, WALL_X1, ny1 + 0.5, ny1 + 0.5 + GATE_T, h.CN1F_Z0, h.CN1F_Z0 + GATE_H)


def fc1_shelf(hull):
    y0, y1 = h.FC1F_Y0, DRAWER_Y1
    m = to_man(skin_clipped_plate(hull, y0, y1, SHELF_Z0, SHELF_Z0 + SHELF_T, bite=-2.5))
    for s in (1, -1):
        for ys in STRAP_Y:
            # two slots per strap: down slot A, under the plate bridge, up slot B
            for xa, xb in ((STRAP_X0, STRAP_X0 + SLOT_W), (STRAP_X1 - SLOT_W, STRAP_X1)):
                x0, x1 = sorted((s * xa, s * xb))
                m = m - to_man(box(x0, x1, ys, ys + STRAP_W + 0.5, SHELF_Z0 - 0.1,
                                   SHELF_Z0 + SHELF_T + 0.1))
        for y in (h.FC1F_Y0 + 4.0, DRAWER_Y1 - 4.0):
            x = s * 0.5 * (WALL_X0 + WALL_X1)
            m = m - to_man(cyl("z", x, y, SHELF_Z0 - 0.1, SHELF_Z0 + SHELF_T + 0.1, M25_CLEAR / 2))
    return _mesh(m)


def hatch_box():
    return box(-h.HATCH_X, h.HATCH_X, h.HATCH_Y0, h.HATCH_Y1, h.HATCH_CUT_Z0, 400.0)


FLANGE_Y0 = 90.0  # flange sides start aft of the Observer (its aft end rises to the roof)
TONGUE_D = 6.0  # cover tongue tucked under the fixed skin at the Y 60 window frame


def hatch_fastener_xy():
    """8 points on the flange centreline: 3 per side (Y >= FLANGE_Y0) + 2 aft."""
    o = h.HATCH_FLANGE_W / 2
    xs, y1 = h.HATCH_X - o, h.HATCH_Y1 - o
    ys = (FLANGE_Y0 + 6.0, 0.5 * (FLANGE_Y0 + y1), y1 - 6.0)
    return [(sx * xs, y) for sx in (1, -1) for y in ys] + [(sx * 12.0, y1) for sx in (1, -1)]


def hatch_parts(hull):
    hm = to_man(hull)
    cut = to_man(hatch_box())
    cover = hm ^ cut
    hull_cut = hm - cut
    # flange: ring footprint under the skin -- the hull shifted down 3 mm,
    # inside the ring, minus the hull itself -> a 3 mm layer bonded to the
    # inner skin.  (A 2 mm shift equals the wall thickness and leaves
    # coplanar faces: non-manifold, 2026-11-01.)
    w = h.HATCH_FLANGE_W
    ring = (to_man(box(-h.HATCH_X - w, h.HATCH_X + w, FLANGE_Y0, h.HATCH_Y1 + w,
                       h.HATCH_CUT_Z0 - 20.0, 400.0))
            - to_man(box(-h.HATCH_X + w, h.HATCH_X - w, h.HATCH_Y0 + w, h.HATCH_Y1 - w,
                         h.HATCH_CUT_Z0 - 21.0, 401.0)))
    down = hull.copy()
    down.apply_translation([0.0, 0.0, -FLANGE_SHIFT])
    flange = (ring ^ to_man(down)) - hm
    # forward edge: a tongue on the COVER tucks under the fixed skin forward
    # of the cut (the Observer leaves no room for a bonded flange there)
    tongue = (to_man(box(-h.HATCH_X + 1.0, h.HATCH_X - 1.0, h.HATCH_Y0 - TONGUE_D,
                         h.HATCH_Y0 + 0.01, h.HATCH_CUT_Z0 - 20.0, 400.0))
              ^ to_man(down)) - hm
    cover = cover + tongue
    for x, y in hatch_fastener_xy():
        loc, _, _ = hull.ray.intersects_location([[x, y, 400.0]], [[0.0, 0.0, -1.0]])
        z_out = float(loc[:, 2].max())
        boss = to_man(cyl("z", x, y, z_out - 2.0 - 7.0, z_out - 2.0, BOSS_D / 2)) - hm
        flange = flange + boss - to_man(cyl("z", x, y, z_out - 8.0, z_out - 1.9, M25_INSERT / 2))
        cover = cover - to_man(cyl("z", x, y, z_out - 3.0, z_out + 1.0, M25_CLEAR / 2))
    return _mesh(cover), _mesh(flange), _mesh(hull_cut)


def statics():
    f = FOS * NODE_KG * LIMIT_G * G0
    print(f"retention design load per node: {FOS} x {NODE_KG} kg x {LIMIT_G} g = {f:.1f} N "
          f"({f / 4.44822:.1f} lbf) in every direction")
    print("allowables (cam strap, snap gate, M2.5 insert pull-out, bond shear): NOT CITED -> "
          "statics PROVISIONAL (open WBS item)")
    return f


def write(tm, path):
    tm.export(path)
    print(f"wrote {os.path.relpath(path, REPO)}  watertight={tm.is_watertight}  "
          f"vol={tm.volume / 1000:.2f} cm3")
    return tm.is_watertight


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--statics", action="store_true")
    a = ap.parse_args()
    statics()
    if a.statics:
        return 0
    hull = trimesh.load(h.MERGED)
    cover, flange, hull_cut = hatch_parts(hull)
    parts = [
        (cn1_drawer(hull), os.path.join(OUT_DIR, "bay_a_cn1_drawer.stl")),
        (cn1_gate(), os.path.join(OUT_DIR, "bay_a_cn1_gate.stl")),
        (fc1_shelf(hull), os.path.join(OUT_DIR, "bay_a_fc1_shelf.stl")),
        (cover, os.path.join(OUT_DIR, "bay_a_hatch_cover.stl")),
        (flange, os.path.join(OUT_DIR, "bay_a_hatch_flange.stl")),
        (hull_cut, HULL_OUT),
    ]
    # check every part BEFORE writing any: a failed run never leaves a mixed set
    bad = [os.path.basename(p) for tm, p in parts if not tm.is_watertight]
    if bad:
        print(f"NOT WRITING: non-watertight part(s): {bad}")
        return 1
    ok = all(write(tm, p) for tm, p in parts)
    print("SERVICE PATH:\n" + SERVICE_PATH)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
