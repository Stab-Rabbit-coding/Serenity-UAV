#!/usr/bin/env python3
"""sls_dfm_audit.py -- bow-to-stern SLS design-for-manufacture audit of every
active printed airframe STL (fuselage head/cargo/middle/rear, landing gear,
wings, both nacelles, ESC bays, nozzles; port and starboard).

Why this exists: the airframe is moving from FDM CF-PETG to SLS DuraForm PA CF
(PA12-CF) [REF-MAT-015] and DuraForm PA11 Black [REF-MAT-016].  FDM rules
(perimeter-multiple walls, overhang limits, support access) no longer govern;
SLS rules do.  This tool measures each part against the SLS rules below so the
geometry changes go where a rule is actually broken.

Rules checked (all from the 3D Systems SLS Design Guide, June 2019 [REF-MFG-001]):
  R1 Build envelope -- 3D Systems SLS 380, 15 x 13 x 18 in (381.0 x 330.2 x
     457.2 mm), the machine the owner (Stab-Rabbit-coding) confirmed 3D Systems
     will build on, 2026-11-01.  The guide lists the same 15 x 13 x 18 in class
     for ProX 6100 / sPro 60 (p. 17, rounded there to 460 mm); the exact inch
     figure is used.  Checked axis-aligned in the best of the 6 axis
     permutations (conservative: a tilted nest may still fit).
  R2 Minimum wall -- 1.0 mm.  The guide gives >1 mm for sealed tank walls
     (p. 15) and >1 mm for tag sticks (p. 14); used here as the general floor.
     Measured by inward ray-casting from sampled surface points
     (Moller-Trumbore: T. Moller & B. Trumbore, "Fast, Minimum Storage
     Ray/Triangle Intersection", J. Graphics Tools 2(1), 1997; numpy, since
     rtree/embree are not installed on this system).
  R3 Trapped powder -- every enclosed void (a closed inner shell) needs an
     escape path.  The guide's blind-boss fix is a >2 mm hole at the base
     (p. 6); duct/axle cavities need 2 mm+ clearance and air ports (p. 3).
     A void is reported as a closed component whose signed volume is negative.
  R4 Mesh validity -- watertight, consistent winding, positive volume
     (needed by every SLS build-prep tool; not a guide rule, a file rule).

Not checked here (needs part-by-part design intent, see docs/SLS_MIGRATION.md):
  moving-part clearance 0.3 mm / 0.2 mm min (guide pp. 3, 7, 12), blind-boss
  escape holes, thick-section shrink.

Run:  /usr/bin/python3 tools/sls_dfm_audit.py [--rays N] [--json out.json]

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (Stab-Rabbit-coding)
AI note: Written by Claude Opus 5.5 (Anthropic) under the author's direction,
         2026-11-01.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import argparse
import json
import os
import sys
from itertools import permutations

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
STL_ROOT = os.path.join(ROOT, "airframe", "stls")

ENVELOPE_SLS380 = (15 * 25.4, 13 * 25.4, 18 * 25.4)  # owner 2026-11-01; [REF-MFG-001 p. 17]
MIN_WALL_MM = 1.0                       # [REF-MFG-001 pp. 14-15]
# A designed 1.00 mm wall measures 0.99x by ray; edge/corner grazing rays read
# short on every part.  Flag only if >5 % of the surface reads below 0.95 mm.
WALL_TOL_MM = 0.05
THIN_FRAC_LIMIT = 0.05
ESCAPE_HOLE_MIN_MM = 2.0                # [REF-MFG-001 p. 6]

# Files that are never printed: void formers are boolean tools, reference
# meshes are for clearance checks only.
SKIP_TOKENS = ("void_former", "reference", "_ref.", "envelope", "keepout",
               # assembly / kinematic views and metal wire, not printed parts
               "_assembled", "_deformed", "hull_stance", "hull_legs",
               "iris-open", "iris-closed", "_wire_")


def fits(ext, env):
    """True if sorted extents fit the envelope in any axis permutation."""
    return any(all(e <= v for e, v in zip(ext, p)) for p in permutations(env))


def ray_first_hit(origins, dirs, tri):
    """Distance to the first triangle hit for each ray (inf if none).

    Moller-Trumbore, vectorised over triangles, looped over rays in chunks so
    memory stays bounded.  A small epsilon skips the triangle the ray starts on.
    """
    v0, v1, v2 = tri[:, 0], tri[:, 1], tri[:, 2]
    e1, e2 = v1 - v0, v2 - v0
    out = np.full(len(origins), np.inf)
    for i, (o, d) in enumerate(zip(origins, dirs)):
        p = np.cross(d, e2)
        det = np.einsum("ij,ij->i", e1, p)
        ok = np.abs(det) > 1e-12
        inv = np.zeros_like(det)
        inv[ok] = 1.0 / det[ok]
        s = o - v0
        u = np.einsum("ij,ij->i", s, p) * inv
        q = np.cross(s, e1)
        v = (q @ d) * inv
        t = np.einsum("ij,ij->i", e2, q) * inv
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-4)
        if hit.any():
            out[i] = t[hit].min()
    return out


def audit(path, rays, rng):
    m = trimesh.load(path, force="mesh")
    rel = os.path.relpath(path, ROOT)
    ext = sorted(m.extents.tolist())
    r = {"part": rel, "extents_mm": [round(x, 1) for x in m.extents],
         "watertight": bool(m.is_watertight),
         "winding_ok": bool(m.is_winding_consistent),
         "volume_cc": round(abs(m.volume) / 1000.0, 2) if m.is_watertight else None,
         "fits_sls380": fits(ext, ENVELOPE_SLS380)}
    # R3: closed components with negative signed volume are inner void shells.
    voids = []
    for c in m.split(only_watertight=False):
        if c.is_watertight and c.volume < 0:
            voids.append(round(-c.volume / 1000.0, 3))
    r["enclosed_voids_cc"] = voids
    # R2: inward ray thickness at sampled surface points.
    pts, fid = trimesh.sample.sample_surface(m, rays, seed=int(rng.integers(1 << 31)))
    n = m.face_normals[fid]
    d = ray_first_hit(pts - n * 1e-3, -n, m.triangles)
    d = d[np.isfinite(d)]
    if len(d):
        r["wall_p01_mm"] = round(float(np.percentile(d, 1)), 2)
        r["wall_p50_mm"] = round(float(np.median(d)), 2)
        r["frac_below_min"] = round(float((d < MIN_WALL_MM - WALL_TOL_MM).mean()), 3)
    else:
        r["wall_p01_mm"] = r["wall_p50_mm"] = r["frac_below_min"] = None
    fails = []
    if not r["fits_sls380"]:
        fails.append("R1-envelope")
    if r["frac_below_min"] and r["frac_below_min"] > THIN_FRAC_LIMIT:
        fails.append("R2-thin-wall")
    if voids:
        fails.append("R3-trapped-powder")
    if not (r["watertight"] and r["winding_ok"]):
        fails.append("R4-mesh")
    r["fails"] = fails
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--rays", type=int, default=300)
    ap.add_argument("--json", default=os.path.join(ROOT, "docs", "sls-study",
                                                   "sls_dfm_audit.json"))
    a = ap.parse_args()
    rng = np.random.default_rng(20261101)  # fixed seed: reproducible report
    files = sorted(
        os.path.join(dp, f) for dp, _, fs in os.walk(STL_ROOT) for f in fs
        if f.lower().endswith(".stl") and "rchive" not in dp
        and not any(t in f.lower() for t in SKIP_TOKENS))
    rows = []
    for f in files:
        try:
            rows.append(audit(f, a.rays, rng))
        except Exception as exc:  # report, never hide, a part that won't load
            rows.append({"part": os.path.relpath(f, ROOT), "fails": [f"LOAD: {exc}"]})
        r = rows[-1]
        print(f"{'FAIL' if r['fails'] else 'ok  '} {r['part']:70s} "
              f"{r.get('extents_mm')} p01={r.get('wall_p01_mm')} "
              f"<1mm={r.get('frac_below_min')} {' '.join(r['fails'])}", flush=True)
    with open(a.json, "w") as fh:
        json.dump(rows, fh, indent=1)
    nf = sum(1 for r in rows if r["fails"])
    print(f"\n{len(rows)} parts audited, {nf} with findings -> {os.path.relpath(a.json, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
