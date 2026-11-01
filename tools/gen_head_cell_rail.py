#!/usr/bin/env python3
"""gen_head_cell_rail.py -- generate the head-cell rail (head piece), stop,
catch and sled as installed-position R2 STLs (plan 2026-10-26-001 U4/U5).

All stations come from tools/head_layout_fit.py (single source).  The rail is
the cargo cradle's inverted U carried forward (KTD6): ceiling over the band,
two side walls, two inward lips the sled rides on.  The fore-aft crash load
is carried by LONGITUDINAL webs -- the side walls continue down to the head
floor and end in bonded flanges -- because a transverse saddle loaded in its
weak axis cannot carry it (797 N ultimate on a 3 mm plate ~ 780 MPa,
2026-10-27).  The webs stop forward of the head/cargo splice collar so the
rail never loads the collar (plan 001 U4 step 3).

Statics (limit 79.4 g in every direction on cell + sled, FOS 3.0) are in
docs/BATTERY_MOUNT.md §8 and printed by --statics.

Run:
    /usr/bin/python3 tools/gen_head_cell_rail.py            # write STLs
    /usr/bin/python3 tools/gen_head_cell_rail.py --statics  # statics only

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the
author's direction, 2026-10-27, per `AGENTS.md` §3 AI attribution.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""

import argparse
import os
import struct
import sys

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import hull_datums as hd  # noqa: E402
import head_layout_fit as h  # noqa: E402  single source of stations
from cargo_layout_fit import box, to_man  # noqa: E402

OUT_DIR = os.path.join(REPO, "airframe", "stls", "fuselage", "head")
G0 = 9.80665  # m/s^2, standard gravity

# Web / flange geometry (head piece)
WEB_Y1 = 224.0  # webs end 2.7 mm forward of the collar ring (Y 226.7)
FLANGE_W = 10.0  # bonded flange width each side of the web foot
FLANGE_T = 3.0
FLANGE_STEP = 4.0  # Y pitch of the skin-following flange segments
# Catch: vertical CF-PETG leaf on the stop's forward face, tooth through the
# stop into a hole in a tongue on the sled nose (KTD7).
# Rev H3 catch (2026-10-27): a HORIZONTAL leaf lying on top of the sled-nose
# tongue, forward of the stop (the vertical leaf rose above the rail ceiling
# into the Bay A pouches).  A full-width blade under the leaf tip drops into a
# groove across the tongue's top at the stop face; an aft crash load drives the
# groove face into the blade and the blade into the STOP face, so the leaf
# carries no crash load -- it only holds the blade down.  Lift 3 mm to release.
LEAF_L, LEAF_W, LEAF_T = 30.0, 20.0, 1.0  # span (X), width (Y), thickness (Z)
GROOVE_D = 2.5  # blade engagement depth into the tongue
LEAF_DEFLECT = GROOVE_D + 0.5  # lift to release
TONGUE_X = -10.0  # tongue / blade lateral centre (leaf root at +X, port side)
TONGUE_W, TONGUE_T = 14.0, 6.0  # tongue width (X) and thickness (Z)
TONGUE_FWD = 9.4  # projection forward of the stop face (blade 5 + gap + 4 mm ridge)
BLADE_Y = 5.0  # blade length (Y) in shear
STOP_T = 4.0

# Cited allowables (20 % CF-PETG)
FLEX_STRENGTH = 77.0  # MPa, ASTM D790 [REF-MAT-002]
FLEX_MODULUS = 6670.0  # MPa [REF-MAT-002]
TENSILE = 39.23  # MPa, ASTM D638 [REF-MAT-001]
COMPRESSIVE = 47.0  # MPa, low end of the D695 range [REF-MAT-001]
SHEAR_EST = 0.577 * TENSILE  # distortion-energy estimate, order of magnitude only
BOND = 5.0  # MPa, repo bond-limited CF-PETG figure (docs/structural_analysis.md §7.3)
SLED_G = 20.0  # estimate, refine from the rendered sled volume
LOAD_G = 79.4  # docs/LANDING_GEAR_ANALYSIS.md Rev R6, 4 ft level (plan 001 R7)
FOS = 3.0


def statics():
    m = (h.CELL_G + SLED_G) / 1000.0
    lim = m * G0 * LOAD_G
    ult = lim * FOS
    rows = []

    def row(name, stress, allow, src):
        rows.append((name, stress, allow, allow / stress if stress else float("inf"), src))

    # forward: stop plate, 4-edge simply supported, uniform load; coefficient 0.29 for
    # a/b ~ 1.1 is REQUIRES VERIFICATION against a cited plate table (TODO §0.x)
    a, b = h.BAND_W, h.BAND_H
    q = ult / (a * b)
    row("stop plate bending (fwd)", 0.29 * q * b * b / STOP_T ** 2, FLEX_STRENGTH, "REF-MAT-002")
    row("stop bearing (fwd)", ult / (a * b), COMPRESSIVE, "REF-MAT-001")
    # fwd load into the webs as shear, then the flange bond
    web_len = WEB_Y1 - h.RAIL_Y0
    row("web shear (fwd/aft)", ult / (2 * web_len * h.RAIL_T), SHEAR_EST, "REF-MAT-001 est")
    row("flange bond (any dir)", ult / (2 * web_len * FLANGE_W), BOND, "structural_analysis §7.3")
    # up: ceiling plate strip spanning the band
    p = ult / (h.CELL_L * h.BAND_W)
    row("ceiling bending (up)", 6 * (p * h.BAND_W ** 2 / 8) / h.RAIL_T ** 2, FLEX_STRENGTH,
        "REF-MAT-002")
    # down: lips as cantilevers, load at 2 mm arm, both lips over the cell length
    w = ult / (2 * h.CELL_L)
    row("lip bending (down)", 6 * (w * 2.0) / h.RAIL_T ** 2, FLEX_STRENGTH, "REF-MAT-002")
    # aft: groove face bears on the blade, blade bears on the stop face; the
    # ridge forward of the groove shears off along the groove floor
    row("blade shear (aft)", ult / (TONGUE_W * BLADE_Y), SHEAR_EST, "REF-MAT-001 est")
    row("groove-face bearing (aft)", ult / (TONGUE_W * GROOVE_D), COMPRESSIVE, "REF-MAT-001")
    row("ridge shear-out (aft)", ult / (TONGUE_W * (TONGUE_FWD - BLADE_Y - 0.4)), SHEAR_EST,
        "REF-MAT-001 est")
    row("tongue section tension (aft)", ult / (TONGUE_W * (TONGUE_T - GROOVE_D)), TENSILE,
        "REF-MAT-001")
    # catch leaf at release (not a crash case): strain/stress and pull force
    sig = 3 * FLEX_MODULUS * LEAF_T * LEAF_DEFLECT / (2 * LEAF_L ** 2)
    i_leaf = LEAF_W * LEAF_T ** 3 / 12
    f_rel = 3 * FLEX_MODULUS * i_leaf * LEAF_DEFLECT / LEAF_L ** 3
    print(f"cell + sled {m * 1000:.0f} g; limit {lim:.1f} N ({lim / 4.44822:.1f} lbf) at "
          f"{LOAD_G} g; ultimate {ult:.1f} N ({ult / 4.44822:.1f} lbf) at FOS {FOS}")
    print(f"{'element':28s} {'stress MPa':>10s} {'allow MPa':>10s} {'margin':>7s}  source")
    ok = True
    for n, s, al, mg, src in rows:
        ok &= mg >= 1.0
        print(f"{n:28s} {s:10.2f} {al:10.2f} {mg:7.2f}  {src}")
    print(f"catch leaf at release: {sig:.1f} MPa vs {FLEX_STRENGTH} (x{FLEX_STRENGTH / sig:.2f});"
          f" release force {f_rel:.1f} N ({f_rel / 4.44822:.2f} lbf) -- one-hand pull."
          " No cited fatigue allowable: bench-cycle the leaf before flight.")
    print(f"STATICS: {'PASS' if ok else 'FAIL'} (margins on ultimate; >= 1.0 required)")
    return ok


def _tm(m):
    mm = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts))


def skin_z(head_tm, x, y, z_from=166.0):
    """Inner skin Z below (x, y), by a downward ray from inside the head."""
    loc, _, _ = head_tm.ray.intersects_location([[x, y, z_from]], [[0, 0, -1.0]],
                                                multiple_hits=False)
    return float(loc[0][2]) if len(loc) else None


def rail_head(head_tm):
    shell = to_man(head_tm)
    rail = to_man(h.rail_solid(h.RAIL_Y0, h.RAIL_HEAD_Y1))
    rail = rail + to_man(box(-h.BAND_W / 2, h.BAND_W / 2, h.RAIL_Y0, h.STOP_Y,
                             h.BAND_Z0 - h.RAIL_T, h.BAND_Z1))  # stop plate
    hw = h.BAND_W / 2
    z_top = h.BAND_Z0 - h.RAIL_T
    for sx in (-1, 1):
        x0, x1 = sorted((sx * hw, sx * (hw + h.RAIL_T)))
        rail = rail + to_man(box(x0, x1, h.RAIL_Y0, WEB_Y1, 120.0, z_top + 0.5))
        xc = 0.5 * (x0 + x1)
        fx0, fx1 = xc - FLANGE_W / 2, xc + FLANGE_W / 2
        for y in np.arange(h.RAIL_Y0, WEB_Y1, FLANGE_STEP):
            zs = [skin_z(head_tm, xx, y + FLANGE_STEP / 2) for xx in (fx0, xc, fx1)]
            zs = [z for z in zs if z is not None]
            if not zs:
                continue
            rail = rail + to_man(box(fx0, fx1, y, min(y + FLANGE_STEP, WEB_Y1),
                                     min(zs) - 2.0, max(zs) + FLANGE_T))
    rail = rail - shell
    tm = _tm(rail)
    parts = tm.split(only_watertight=False)
    # keep the body that holds the ceiling (the rail), drop skin-outside slivers
    keep = max(parts, key=lambda p: p.volume)
    # slot in the stop for the tongue + tooth
    slot = box(TONGUE_X - TONGUE_W / 2 - 0.3, TONGUE_X + TONGUE_W / 2 + 0.3, h.RAIL_Y0 - 1,
               h.STOP_Y + 1, h.BAND_ZC - TONGUE_T / 2 - 0.3, h.BAND_ZC + TONGUE_T / 2 + 0.3)
    return _tm(to_man(keep) - to_man(slot))


def _tongue_y():
    """(y0, y1) of the tongue: from its forward tip to the cell nose."""
    return h.RAIL_Y0 - TONGUE_FWD, h.CELL_Y0


def sled():
    hw = h.BAND_W / 2 - 0.5
    floor = box(-hw, hw, h.STOP_Y, h.CELL_Y1 + h.SLED_LIP, h.BAND_Z0, h.BAND_Z0 + h.SLED_FLOOR_T)
    nose = box(-hw, hw, h.STOP_Y, h.CELL_Y0, h.BAND_Z0, h.BAND_Z1 - 0.5)
    tail = box(-hw, hw, h.CELL_Y1, h.CELL_Y1 + h.SLED_LIP, h.BAND_Z0, h.BAND_Z0 + 12.0)
    ty0, ty1 = _tongue_y()
    z0, z1 = h.BAND_ZC - TONGUE_T / 2, h.BAND_ZC + TONGUE_T / 2
    tongue = box(TONGUE_X - TONGUE_W / 2, TONGUE_X + TONGUE_W / 2, ty0, ty1, z0, z1)
    groove = box(TONGUE_X - TONGUE_W / 2 - 1, TONGUE_X + TONGUE_W / 2 + 1,
                 h.RAIL_Y0 - BLADE_Y - 0.4, h.RAIL_Y0, z1 - GROOVE_D, z1 + 1)
    m = to_man(floor) + to_man(nose) + to_man(tail) + to_man(tongue) - to_man(groove)
    return _tm(m)


def catch():
    """Horizontal leaf on the tongue top, root block bonded to the stop's
    forward face at +X (port), blade under the tip in the tongue groove."""
    z1 = h.BAND_ZC + TONGUE_T / 2
    x_tip = TONGUE_X - TONGUE_W / 2
    x_root = x_tip + LEAF_L
    leaf = box(x_tip, x_root, h.RAIL_Y0 - LEAF_W, h.RAIL_Y0, z1, z1 + LEAF_T)
    root = box(x_root - 4.0, x_root, h.RAIL_Y0 - LEAF_W, h.RAIL_Y0, z1 - TONGUE_T, z1 + LEAF_T)
    blade = box(x_tip, TONGUE_X + TONGUE_W / 2, h.RAIL_Y0 - BLADE_Y - 0.2, h.RAIL_Y0 - 0.2,
                z1 - GROOVE_D + 0.2, z1)
    return _tm(to_man(leaf) + to_man(root) + to_man(blade))


def write(tm, name):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name)
    tm.export(path)
    with open(path, "r+b") as f:  # stamp the R2 marker into the 80-byte header
        f.write(hd.FRAME_MARKER.ljust(80, b" ")[:80])
        f.seek(80)
        struct.unpack("<I", f.read(4))
    print(f"wrote {os.path.relpath(path, REPO)}  vol {tm.volume:.0f} mm^3  "
          f"watertight {tm.is_watertight}  ~{tm.volume * 1.05e-3:.1f} g as printed")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--statics", action="store_true")
    a = ap.parse_args()
    ok = statics()
    if a.statics:
        return 0 if ok else 1
    head_tm = trimesh.load(h.HEAD)
    write(rail_head(head_tm), "head_cell_rail.stl")
    write(sled(), "head_cell_sled.stl")
    write(catch(), "head_cell_catch.stl")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
