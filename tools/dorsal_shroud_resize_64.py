#!/usr/bin/python3
"""Resize the canonical dorsal shroud of the 64 mm nacelle to enclose the
nozzle-servo drive (WBS NAC-64-SERVO-01).

Owner rule (2026-10-04): "any increase in the height must be smoothly shaped to
be just a resizing of the canonical dorsal shroud of the nacelles."  So the
new shroud is the CANONICAL shroud with exactly two scalars applied:

    r'(az, z) = base(az, z) + K_H * h(az, z_src),
    z_src = z                      for z <= Z0   (shroud kept as canon)
    z_src = Z0 + (z - Z0) / K_Z    for z >  Z0   (its TAIL stretched aft)

  * h(az, z) = canonical skin radius minus the body base under the shroud,
    where base(az, z) runs linearly in azimuth between the skin radii at the
    shroud's two edges (AZ_L, AZ_R) — so h = 0 at both edges and the resized
    shroud meets the body seamlessly there (base is evaluated at the TRUE z,
    so the body under it is untouched);
  * K_H scales the shroud's height above the body uniformly; K_Z stretches
    its TAIL aft of Z0 (chosen at the crest) — the canonical shroud is cut off
    by the nozzle at Z ~187 and QMx shows it running on over the actuator ring
    [REF-CAD-003], so the tail is continued rather than the whole shroud
    shifted.  A stretch of the whole shroud about its start was tried first and
    rejected: it dragged the tall crest aft, away from the drive (needed 5.3x).

K_H, K_Z are the smallest pair for which every point of the drive's envelope
(servo body, horn, link, bellcrank plate, rod and ball-link bodies over the full
stroke, from nozzle_servo_linkage_64_params.scad) lies at least CLR + SKIN
below the new surface.  Output: ``nacelle_dorsal_shroud_64_gen.scad`` with a
closed polyhedron ``dorsal_shroud_64()`` (skin r' down to r 34.9), unioned into
the pod by nacelle_nozzle_servo_64mm.scad.  Starboard frame; port = mirror.

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, per AGENTS.md AI attribution.  License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
from __future__ import annotations

import ast
import math
import re
import sys
from pathlib import Path

import numpy as np
import trimesh
from scipy.interpolate import RegularGridInterpolator as RGI

REPO = Path(__file__).resolve().parents[1]
NAC = REPO / "airframe/openscad/nacelles"
PARAMS = NAC / "nozzle_servo_linkage_64_params.scad"
OUT = NAC / "nacelle_dorsal_shroud_64_gen.scad"
SHELL = REPO / "airframe/stls/nacelles/eng_right_shell24_50mm_repaired.stl"

AZ_L, AZ_R = 226.0, 314.0      # shroud edges (canonical spine spans ~+/-44 deg)
Z0 = 175.0                     # tail-stretch anchor (searched, see main)
Z_START = 100.0                # the canonical shroud's forward end (crest h ~0)
R_IN = 34.9                    # solid down to just outside the sleeve bore
CLR, SKIN = 0.6, 1.6           # cavity running clearance, printable wall
AZ = np.arange(AZ_L, AZ_R + 0.01, 1.0)
ZG = np.arange(90.0, 209.0, 0.5)


def params() -> dict:
    txt = PARAMS.read_text()
    out = {}
    for k, v in re.findall(r"(NSL_\w+)\s*=\s*([^;]+);", txt):
        v = v.strip()
        out[k] = np.array(ast.literal_eval(v)) if v.startswith("[") else float(v)
    return out


def skin_grid():
    sh = trimesh.load(SHELL)
    sh.apply_translation([-155.02, 190.79, 0])
    sh.apply_transform(np.diag([1.21, 1.21, 1.13, 1]))
    o, d = [], []
    for z in ZG:
        for a in AZ:
            o.append([0, 0, z]); d.append([math.cos(math.radians(a)), math.sin(math.radians(a)), 0])
    loc, ri, _ = sh.ray.intersects_location(np.array(o), np.array(d))
    r = np.zeros(len(o))
    np.maximum.at(r, ri, np.hypot(loc[:, 0], loc[:, 1]))
    r = r.reshape(len(ZG), len(AZ))
    # A ray can slip through a seam of the canonical mesh (~0.4 % of rays) and
    # record r = 0; fill each miss from its axial neighbours so a seam is never
    # read as a 48 mm "rise" (bug found 2026-10-04, ce-optimize run nds-1).
    for j in range(r.shape[1]):
        col = r[:, j]
        ok = col > 1.0
        if ok.sum() >= 2 and (~ok).any():
            col[~ok] = np.interp(ZG[~ok], ZG[ok], col[ok])
    return r


def mech_points(p: dict) -> np.ndarray:
    """Outer envelope samples of the drive over its stroke (nacelle-local)."""
    def er(a): return np.array([math.cos(math.radians(a)), math.sin(math.radians(a)), 0])
    C, U, V = p["NSL_C"], p["NSL_U"], p["NSL_V"]
    def arm(phi, L): return C + L * (math.cos(math.radians(phi)) * U + math.sin(math.radians(phi)) * V)
    def ball(psi): return np.array([p["NSL_B_R"] * math.cos(math.radians(psi)),
                                    p["NSL_B_R"] * math.sin(math.radians(psi)), p["NSL_B_Z"]])
    sh, saz = p["NSL_SHAFT"], p["NSL_SHAFT_AZ"]
    def horn(th): return sh + p["NSL_HORN"] * (math.cos(math.radians(th)) * er(saz)
                                              + math.sin(math.radians(th)) * np.array([0, 0, 1.0]))
    pts = []
    def sphere(c, d):
        for t in np.linspace(0, math.pi, 7):
            for ph in np.linspace(0, 2 * math.pi, 12, endpoint=False):
                pts.append(c + d / 2 * np.array([math.sin(t) * math.cos(ph), math.sin(t) * math.sin(ph), math.cos(t)]))
    def seg(a, b, d, n=6):
        for t in np.linspace(0, 1, n): sphere(a + (b - a) * t, d)
    # servo body box (KST X06 L x W x H): L along z, W radial, H tangential (NSL_SERVO_SIDE)
    L, W, H = p["NSL_SERVO"]
    rs = math.hypot(sh[0], sh[1]); et = np.array([-math.sin(math.radians(saz)), math.cos(math.radians(saz)), 0])
    side = p.get("NSL_SERVO_SIDE", 1.0)
    for a in np.linspace(rs - W / 2, rs + W / 2, 3):
        for t in side * np.linspace(1.5, 1.5 + H, 5):
            for z in np.linspace(sh[2] - (L - 4.5), sh[2] + 4.5, 6):
                pts.append(a * er(saz) + t * et + np.array([0, 0, z]))
    for f in np.linspace(0, 1, 9):
        ph = p["NSL_PHI_CLOSED"] + f * (p["NSL_PHI_OPEN"] - p["NSL_PHI_CLOSED"])
        th = p["NSL_TH_CLOSED"] + f * (p["NSL_TH_OPEN"] - p["NSL_TH_CLOSED"])
        ps = p["NSL_PSI_CLOSED"] + f * (p["NSL_PSI_OPEN"] - p["NSL_PSI_CLOSED"])
        seg(sh, horn(th), 3.0)                                       # horn
        t_in = arm(ph + p["NSL_ARM_OFFSET"], p["NSL_L_IN"])
        seg(horn(th), t_in, 3.2); sphere(horn(th), 5.5); sphere(t_in, 5.5)   # link + ball links
        # bellcrank: 3 mm plate across the radius (axis along C's radial)
        ax = C / np.linalg.norm([C[0], C[1], 0]); ax[2] = 0
        for q in (C, t_in, arm(ph, p["NSL_L_OUT"])):
            for s in (-1.5, 1.5): pts.append(q + s * ax)
        tip = arm(ph, p["NSL_L_OUT"]); b = ball(ps)
        seg(tip, b, 3.2); sphere(tip, 5.5); sphere(b, 5.5)          # rod + ball links
    return np.array(pts)


def main() -> int:
    import argparse
    global PARAMS, OUT
    ap = argparse.ArgumentParser()
    ap.add_argument('--params', type=Path); ap.add_argument('--out', type=Path)
    ap.add_argument('--eval-only', action='store_true')
    ap.add_argument('--z0', type=float, nargs='*', default=[170.0, 174.0, 177.0, 180.0, 182.0, 184.0])
    a = ap.parse_args()
    if a.params: PARAMS = a.params
    if a.out: OUT = a.out
    p = params()
    R = skin_grid()
    skin = RGI((ZG, AZ), R, bounds_error=False, fill_value=None)
    def base(az, z):
        w = (np.asarray(az) - AZ_L) / (AZ_R - AZ_L)
        return (1 - w) * skin(np.c_[z, np.full_like(z, AZ_L)]) + w * skin(np.c_[z, np.full_like(z, AZ_R)])
    def h(az, z):
        return np.maximum(0.0, skin(np.c_[z, az]) - base(az, z))
    P = mech_points(p)
    pr = np.hypot(P[:, 0], P[:, 1]); paz = np.degrees(np.arctan2(P[:, 1], P[:, 0])) % 360; pz = P[:, 2]
    if paz.min() < AZ_L + 2 or paz.max() > AZ_R - 2:
        print(f"drive leaves the shroud azimuth span: {paz.min():.1f}..{paz.max():.1f}"); return 2
    need = pr + CLR + SKIN
    best = None
    global Z0
    for Z0 in a.z0:
     for kz in np.arange(1.00, 8.001, 0.1):
        zs = np.where(pz <= Z0, pz, Z0 + (pz - Z0) / kz)
        hh = h(paz, zs); bb = base(paz, pz)
        bad = (hh < 0.05) & (need > bb)
        if np.any(bad):
            continue
        kh = np.max(np.where(hh > 0.05, (need - bb) / np.maximum(hh, 1e-6), 0.0))
        kh = max(kh, 1.0)
        Zg, Ag = np.meshgrid(ZG[ZG < 187.86], AZ, indexing="ij")
        new = base(Ag.ravel(), Zg.ravel()) + kh * h(Ag.ravel(), np.where(Zg.ravel() <= Z0, Zg.ravel(), Z0 + (Zg.ravel() - Z0) / kz))
        rise = np.max(new - skin(np.c_[Zg.ravel(), Ag.ravel()]))
        peak = np.max(new)
        # crest-height increase: per azimuth, resized peak minus canonical peak
        # (the station-wise 'rise' counts the nozzle-truncation cliff aft of
        # Z 185 that the owner asked to continue, so it is a diagnostic only)
        nr = new.reshape(Zg.shape); cr = skin(np.c_[Zg.ravel(), Ag.ravel()]).reshape(Zg.shape)
        crest = float(np.max(nr.max(axis=0) - cr.max(axis=0)))
        score = crest
        if best is None or score < best[0]:
            best = (score, kz, kh, rise, peak, Z0, crest)
    if best is None:
        print("no (K_H, K_Z) encloses the drive"); return 2
    _, kz, kh, rise, peak, Z0, crest = best
    print(f"Z0 {Z0}: resized canonical dorsal shroud: K_H {kh:.3f} (height), K_Z {kz:.2f} (length, about Z {Z0}); "
          f"peak r {peak:.2f} mm vs canonical peak {R.max():.2f}; max local rise {rise:.2f} mm; crest increase {crest:.2f} mm")
    if a.eval_only:
        return 0
    # polyhedron: top surface r'(az, z'), inner r = R_IN, z' from Z0 to the stretched end
    z_end = min(209.0, Z0 + kz * (190.0 - Z0) + 2.0)
    zz = np.arange(Z_START, z_end + 0.01, 0.5)
    def zsrc(z): return z if z <= Z0 else Z0 + (z - Z0) / kz
    top = np.array([[base(np.array([a]), np.array([z]))[0] + kh * h(np.array([a]), np.array([zsrc(z)]))[0]
                     for a in AZ] for z in zz])
    top = np.maximum(top, R_IN + 0.2)
    nz, na = top.shape
    pts, faces = [], []
    def idx(layer, i, j): return layer * nz * na + i * na + j
    for layer, rr in ((0, None), (1, R_IN)):
        for i, z in enumerate(zz):
            for j, a in enumerate(AZ):
                r = top[i, j] if layer == 0 else rr
                pts.append([r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), z])
    for i in range(nz - 1):
        for j in range(na - 1):
            faces.append([idx(0, i, j), idx(0, i + 1, j), idx(0, i + 1, j + 1), idx(0, i, j + 1)])
            faces.append([idx(1, i, j), idx(1, i, j + 1), idx(1, i + 1, j + 1), idx(1, i + 1, j)])
    for i in range(nz - 1):
        faces.append([idx(0, i, 0), idx(1, i, 0), idx(1, i + 1, 0), idx(0, i + 1, 0)])
        faces.append([idx(0, i, na - 1), idx(0, i + 1, na - 1), idx(1, i + 1, na - 1), idx(1, i, na - 1)])
    for j in range(na - 1):
        faces.append([idx(0, 0, j), idx(0, 0, j + 1), idx(1, 0, j + 1), idx(1, 0, j)])
        faces.append([idx(0, nz - 1, j), idx(1, nz - 1, j), idx(1, nz - 1, j + 1), idx(0, nz - 1, j + 1)])
    fmt = lambda v: "[" + ",".join(f"{x:.3f}" for x in v) + "]"
    OUT.write_text(
        "// GENERATED by tools/dorsal_shroud_resize_64.py — do not hand-edit.\n"
        f"// Canonical dorsal shroud resized: K_H {kh:.4f}, K_Z {kz:.3f} about Z {Z0}; "
        f"edges az {AZ_L}..{AZ_R}; starboard frame.\n"
        f"DS64_K_H = {kh:.4f}; DS64_K_Z = {kz:.3f}; DS64_PEAK_R = {peak:.3f}; DS64_RISE = {rise:.3f};\n"
        "module dorsal_shroud_64() { polyhedron(points = [" + ",".join(fmt(q) for q in pts)
        + "], faces = [" + ",".join("[" + ",".join(map(str, f)) + "]" for f in faces) + "], convexity = 6); }\n")
    print(f"wrote {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
