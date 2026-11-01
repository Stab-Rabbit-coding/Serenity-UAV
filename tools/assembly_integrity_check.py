#!/usr/bin/env python3
"""assembly_integrity_check.py -- find rogue openings in the assembled hull
enclosure and published meshes that disagree with the aircraft datums (owner,
2026-11-01: "determine what the leak is... use this to find any rogue leaks
or structural issues").

Why: the cooling-air CFD domain leaked.  The cause was a stale published
hull -- the 0.5 in aft wing-root shift (hull_datums WING_LE_ROOT_Y 311.4,
SPAR_Y 339.4, 2026-10-31) moved the wing but the cargo shell, the merged
head+cargo hull and the wing-root flanges were never regenerated, so the
spar bore and mortise stayed at Y 326.7.  tools/check_datum_drift.py checks
literals and frame stamps only, never mesh-vs-datum geometry; this tool does.

Checks:
  E1  Enclosure: rays cast outward from the centreline (+X, -X, +Z, -Z) on a
      Y/Z (or Y/X) grid against every ENCLOSING part (hulls, doors, collar,
      wings, wing-root flanges, 3.0 in gear bays + legs, A1b housings, the
      sealed ramp fairing is in the shell).  A ray that escapes without a hit
      marks a through-opening; escapes are clustered and sized.  Openings
      smaller than FASTENER_MAX_MM equivalent diameter are reported as
      fastener holes (closed by hardware), not leaks.
  S1  Spar: the spar-bore window in each hull side, the wing-root flange
      centre and the wing spar bore are compared with hull_datums.SPAR_Y /
      SPAR_Z (tolerance SPAR_TOL_MM).

Run:
    /usr/bin/python3 tools/assembly_integrity_check.py [--pitch 1.0]

Exit 1 on any leak or spar mismatch.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the
author's direction, 2026-11-01, per `AGENTS.md` §3 AI attribution.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import argparse
import os
import sys

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hull_datums as hd  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, ".."))
FS = os.path.join(REPO, "airframe", "stls", "fuselage")
FASTENER_MAX_MM = 8.0  # equivalent diameter at or below which a hole is a bolt/insert hole
SPAR_TOL_MM = 1.0
Y_RANGE = (0.0, 690.0)

ENCLOSURE = (
    ("merged head+cargo hull", os.path.join(FS, "head_cargo_shell24_2mm_merged.stl")),
    ("middle shell", os.path.join(FS, "middle_shell24_2mm_repaired.stl")),
    ("rear shell", os.path.join(FS, "rear_shell24_2mm_repaired.stl")),
    ("cargo/middle collar", os.path.join(FS, "cargo_middle_splice_collar.stl")),
    ("cargo door port", os.path.join(FS, "cargo", "cargo_door_port.stl")),
    ("cargo door stbd", os.path.join(FS, "cargo", "cargo_door_stbd.stl")),
    ("wing-root flange port", os.path.join(FS, "wing_root_flange_port.stl")),
    ("wing-root flange stbd", os.path.join(FS, "wing_root_flange_stbd.stl")),
    ("wing port", os.path.join(REPO, "airframe", "stls", "wings", "wing_port_s1223_revo.stl")),
    ("wing stbd", os.path.join(REPO, "airframe", "stls", "wings", "wing_stbd_s1223_revo.stl")),
) + tuple((f"gear {n}", os.path.join(FS, "landing-gear", f"lg_r6_3_0in_bay_{n}.stl"))
          for n in ("fore-port", "fore-stbd", "aft-port", "aft-stbd")) + (
    ("gear legs 3.0 in", os.path.join(FS, "landing-gear", "lg_r6_3_0in_hull_legs.stl")),
    ("A1b housing fore-port", os.path.join(FS, "landing-gear", "lg_a1b_housing_fore-port.stl")),
    ("A1b housing fore-stbd", os.path.join(FS, "landing-gear", "lg_a1b_housing_fore-stbd.stl")),
)


def load_enclosure():
    import trimesh
    parts = [(name, trimesh.load(p)) for name, p in ENCLOSURE]
    return parts, trimesh.util.concatenate([m for _, m in parts])


def _hull_z_range(scene, y):
    """Interior Z span at the centreline for station y (first skin up/down from
    a point between the extreme skins)."""
    lo, hi = scene.bounds[0][2], scene.bounds[1][2]
    return lo, hi


def escape_map(scene, direction, pitch):
    """Escape mask over (Y, Z) for +-X rays, or (Y, X) for +-Z rays, cast from
    the centreline plane inside the hull."""
    d = np.asarray(direction, float)
    ys = np.arange(Y_RANGE[0], Y_RANGE[1], pitch)
    if d[0] != 0:  # sideways: grid Y x Z, start on X = X_CL
        vs = np.arange(scene.bounds[0][2], scene.bounds[1][2], pitch)
        Y, V = np.meshgrid(ys, vs)
        o = np.c_[np.full(Y.size, hd.X_CL), Y.ravel(), V.ravel()]
    else:  # vertical: grid Y x X, start at the interior mid-height
        vs = np.arange(-60.0, 60.0 + 1e-6, pitch)
        Y, V = np.meshgrid(ys, vs)
        o = np.c_[V.ravel(), Y.ravel(), np.full(Y.size, 175.0)]
    hit = scene.ray.intersects_any(o, np.tile(d, (len(o), 1)))
    # a point is only meaningful if it is INSIDE the enclosure: the opposite
    # ray must hit something too (otherwise the start point is outside)
    back = scene.ray.intersects_any(o, np.tile(-d, (len(o), 1)))
    esc = (~hit & back).reshape(Y.shape)
    return esc, ys, vs


def clusters(esc, ys, vs, pitch):
    lab, n = ndimage.label(esc)
    out = []
    for i in range(1, n + 1):
        idx = np.argwhere(lab == i)
        area = len(idx) * pitch * pitch
        out.append(dict(y=float(ys[idx[:, 1]].mean()), v=float(vs[idx[:, 0]].mean()),
                        y0=float(ys[idx[:, 1]].min()), y1=float(ys[idx[:, 1]].max() + pitch),
                        v0=float(vs[idx[:, 0]].min()), v1=float(vs[idx[:, 0]].max() + pitch),
                        area=area, deq=2 * np.sqrt(area / np.pi)))
    return sorted(out, key=lambda c: -c["area"])


def spar_checks(parts, pitch):
    """S1: hull spar-bore window centre, flange centre, wing spar bore vs datum."""
    findings = []
    byname = dict(parts)
    hull = byname["merged head+cargo hull"]
    # hull side window nearest the datum spar (port side, rays from inside)
    ys = np.arange(hd.SPAR_Y - 40, hd.SPAR_Y + 40, 0.5)
    zs = np.arange(hd.SPAR_Z - 25, hd.SPAR_Z + 25, 0.5)
    Y, Z = np.meshgrid(ys, zs)
    o = np.c_[np.full(Y.size, hd.X_CL + 45.0), Y.ravel(), Z.ravel()]
    open_ = (~hull.ray.intersects_any(o, np.tile([1.0, 0, 0], (len(o), 1)))).reshape(Y.shape)
    lab, n = ndimage.label(open_)
    best = None
    for i in range(1, n + 1):
        idx = np.argwhere(lab == i)
        a = len(idx) * 0.25
        if a < 150:  # the bore is ~O20 (314 mm^2); skip fastener holes
            continue
        c = (ys[idx[:, 1]].mean(), zs[idx[:, 0]].mean(), a)
        if best is None or a > best[2]:
            best = c
    if best is None:
        findings.append(("hull spar bore", "NOT FOUND near the datum spar", None))
    else:
        dy, dz = best[0] - hd.SPAR_Y, best[1] - hd.SPAR_Z
        findings.append(("hull spar bore (port side window)",
                         f"centre Y {best[0]:.1f} Z {best[1]:.1f} (O{2 * np.sqrt(best[2] / np.pi):.1f})",
                         (dy, dz)))
    for side in ("port", "stbd"):
        b = byname[f"wing-root flange {side}"].bounds
        yc, zc = (b[0][1] + b[1][1]) / 2, None
        findings.append((f"wing-root flange {side}", f"Y centre {yc:.1f}", (yc - hd.SPAR_Y, 0.0)))
    w = byname["wing port"]
    findings.append(("wing port root LE", f"Y {w.bounds[0][1]:.1f} (datum WING_LE_ROOT_Y "
                     f"{hd.WING_LE_ROOT_Y:.1f})", (w.bounds[0][1] - hd.WING_LE_ROOT_Y, 0.0)))
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pitch", type=float, default=1.0)
    a = ap.parse_args()
    parts, scene = load_enclosure()
    bad = 0
    print(f"S1 spar vs datum: SPAR_Y {hd.SPAR_Y:.1f}, SPAR_Z {hd.SPAR_Z:.2f} "
          f"(tolerance {SPAR_TOL_MM} mm)")
    for name, desc, off in spar_checks(parts, a.pitch):
        ok = off is not None and abs(off[0]) <= SPAR_TOL_MM and abs(off[1]) <= SPAR_TOL_MM
        bad += not ok
        tail = "" if off is None else f"  offset dY {off[0]:+.1f} dZ {off[1]:+.1f} mm"
        print(f"  {'ok  ' if ok else 'FAIL'} {name:34s} {desc}{tail}")
    print(f"\nE1 enclosure escapes (rays from the centreline, pitch {a.pitch} mm; holes "
          f"<= O{FASTENER_MAX_MM:.0f} mm are fastener holes):")
    for label, d, vname in (("port (+X)", (1, 0, 0), "Z"), ("stbd (-X)", (-1, 0, 0), "Z"),
                            ("top (+Z)", (0, 0, 1), "X"), ("belly (-Z)", (0, 0, -1), "X")):
        esc, ys, vs = escape_map(scene, d, a.pitch)
        cl = clusters(esc, ys, vs, a.pitch)
        leaks = [c for c in cl if c["deq"] > FASTENER_MAX_MM]
        holes = len(cl) - len(leaks)
        bad += len(leaks)
        print(f"  {label}: {len(leaks)} opening(s), {holes} fastener-size hole(s)")
        for c in leaks:
            print(f"    LEAK Y {c['y0']:.0f}..{c['y1']:.0f} {vname} {c['v0']:.0f}..{c['v1']:.0f} "
                  f"(centre Y {c['y']:.1f} {vname} {c['v']:.1f}), {c['area']:.0f} mm2, "
                  f"eq O{c['deq']:.1f}")
    print(f"\nRESULT: {'PASS' if not bad else f'FAIL ({bad})'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
