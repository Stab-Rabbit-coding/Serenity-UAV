#!/usr/bin/env python3
"""LG-10.2/10.3 -- reconcile the four canonical hip stations with the real skin.

LG-10.1 established the mounting face: the sponson's 25 deg angled panel, whose
normal measures (0.901, 0.015, -0.433) port, mirrored starboard
(docs/LANDING_GEAR_ANALYSIS.md SS2.4a).  What was never measured is the
STANDOFF: how far each canonical hip station sits from that real skin ALONG that
normal.  Everything downstream needs it --

  * the bay frame can only bolt down if its back face lands on the skin;
  * the 16 bolt bosses can only be aimed if the local skin normal is known at
    the bolt, not just at the panel centroid;
  * LG-10.6's conforming patches are cut from the same measurement.

Method
------
No ray casting: there is no rtree/embree in this environment, so trimesh.ray
and proximity.closest_point are unavailable (HANDOFF.md SS4 trap #4).  Instead,
for each station this walks the mesh VERTICES that fall inside a cylinder about
the hip aimed along the panel normal, and reports the distribution of their
along-normal coordinate.  The OUTBOARD skin is the far end of that
distribution; the near cluster is the opposite (inboard) wall, so a simple
"max" would be right for a convex hull but is checked here against the
histogram rather than assumed.

The local skin normal is then re-measured from the faces actually inside the
footprint, area-weighted -- which is what the bolt axis must follow, and is
reported against the SS2.4a panel constant so drift is visible.

Guards learned the hard way (HANDOFF.md SS4):
  * an X-vs-centreline constraint is mandatory -- `nx > 0.7` alone also selects
    the STARBOARD inner wall, whose normal points toward +X (trap #3);
  * the footprint is height-constrained as well as plan-constrained, or the
    search finds the hull's widest point at Z ~ 78 instead of the bay station
    at Z 38 (trap #2).

Run: /usr/bin/python3 tools/landing_gear_bay_station_fit.py [--stl PATH]

Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note : Authored by Claude (model: Claude Opus 5, Anthropic) under the
          author's direction, 2026-08-09, per AGENTS.md AI attribution.
License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
"""

import argparse
import os

import numpy as np
import trimesh

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DEFAULT_STL = os.path.join(
    REPO_ROOT, "airframe", "stls", "fuselage", "cargo",
    "cargo_sect_shell24_2mm_repaired.stl",
)

X_CL = -169.9              # hull centreline (airframe/AGENTS.md)

# Canonical corner stations, docs/LANDING_GEAR_ANALYSIS.md SS2.2.
# (label, hip_x, hip_y, hip_z, swing_azimuth_deg)
# RECESSED 15 mm along each corner's own swing axis (LG-10.2, 2026-08-09).
# Pre-recess stations were [-90,-7], [-249.8,-7], [-79,107], [-260.8,107]; run
# with --pre-recess to measure those instead.
LG_CORNERS = [
    ("fore-port", -103.87, -1.28, 38.0, -22.4),
    ("fore-stbd", -235.93, -1.28, 38.0, -157.6),
    ("aft-port", -92.24, 99.96, 38.0, 28.0),
    ("aft-stbd", -247.56, 99.96, 38.0, 152.0),
]
LG_CORNERS_PRE = [
    ("fore-port", -90.0, -7.0, 38.0, -22.4),
    ("fore-stbd", -249.8, -7.0, 38.0, -157.6),
    ("aft-port", -79.0, 107.0, 38.0, 28.0),
    ("aft-stbd", -260.8, 107.0, 38.0, 152.0),
]

# Measured sponson panel normal (SS2.4a, mirror-verified to 1.4 mm).
PANEL_N = {"port": np.array([0.901, 0.015, -0.433]),
           "stbd": np.array([-0.901, -0.015, -0.433])}

FOOTPRINT_R = 34.0         # mm, radius about the hip axis to sample
Z_BAND = (12.0, 66.0)      # mm, height band that isolates the bay station
X_MIN_OFF = 30.0           # mm, minimum |X - centreline| (trap #3 guard)


def side_of(hip_x):
    return "port" if hip_x > X_CL else "stbd"


def station_report(mesh, label, hip, normal, radius=FOOTPRINT_R):
    """Measure skin standoff and local normal in a cylinder about hip//normal."""
    sgn = 1.0 if normal[0] > 0 else -1.0
    v = mesh.vertices - hip
    along = v @ normal
    radial = np.linalg.norm(v - np.outer(along, normal), axis=1)

    sel = (
        (radial < radius)
        & (mesh.vertices[:, 2] > Z_BAND[0])
        & (mesh.vertices[:, 2] < Z_BAND[1])
        & (sgn * (mesh.vertices[:, 0] - X_CL) > X_MIN_OFF)
    )
    n_hit = int(sel.sum())
    if n_hit < 10:
        print(f"  {label:10s}  NO SKIN in footprint (r={radius:.0f} mm, "
              f"{n_hit} verts) -- station is off structure")
        return None

    a = along[sel]
    pct = np.percentile(a, [5, 25, 50, 75, 95])

    # Local skin normal: faces whose centroid is in the same footprint, on the
    # OUTBOARD half of the distribution, area-weighted.
    cen = mesh.triangles.mean(axis=1)
    cv = cen - hip
    calong = cv @ normal
    cradial = np.linalg.norm(cv - np.outer(calong, normal), axis=1)
    fsel = (
        (cradial < radius)
        & (calong > pct[2])                       # outboard of the median
        & (cen[:, 2] > Z_BAND[0]) & (cen[:, 2] < Z_BAND[1])
        & (sgn * (cen[:, 0] - X_CL) > X_MIN_OFF)
        & (sgn * mesh.face_normals[:, 0] > 0.30)  # outward-facing only
    )
    if fsel.sum() >= 5:
        w = mesh.area_faces[fsel][:, None]
        loc = (mesh.face_normals[fsel] * w).sum(axis=0)
        loc /= np.linalg.norm(loc)
        dev = np.degrees(np.arccos(np.clip(loc @ normal, -1, 1)))
        area = float(mesh.area_faces[fsel].sum())
    else:
        loc, dev, area = normal, float("nan"), 0.0

    print(f"  {label:10s}  {n_hit:5d} verts   skin along-normal "
          f"p5 {pct[0]:+7.2f}  p50 {pct[2]:+7.2f}  p95 {pct[4]:+7.2f} mm")
    print(f"              outboard skin standoff from hip = {pct[4]:+7.2f} mm "
          f"(p75 {pct[3]:+.2f})")
    print(f"              local skin normal ({loc[0]:+.3f},{loc[1]:+.3f},"
          f"{loc[2]:+.3f})  {dev:5.1f} deg off the SS2.4a panel constant  "
          f"[{area:6.0f} mm^2]")
    return dict(label=label, standoff=float(pct[4]), p75=float(pct[3]),
                local_n=loc, dev_deg=float(dev), area=area)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stl", default=DEFAULT_STL)
    ap.add_argument("--radius", type=float, default=FOOTPRINT_R)
    ap.add_argument("--pre-recess", action="store_true",
                    help="measure the pre-LG-10.2 hip stations")
    args = ap.parse_args()

    mesh = trimesh.load(args.stl)
    print(f"{os.path.basename(args.stl)}: {len(mesh.faces):,} faces, "
          f"watertight={mesh.is_watertight}")
    print(f"\nStandoff of each canonical hip from the real skin, measured "
          f"ALONG the SS2.4a panel normal (r={args.radius:.0f} mm footprint):")

    out = []
    corners = LG_CORNERS_PRE if args.pre_recess else LG_CORNERS
    for label, hx, hy, hz, _az in corners:
        hip = np.array([hx, hy, hz])
        n = PANEL_N[side_of(hx)]
        r = station_report(mesh, label, hip, n, args.radius)
        if r:
            out.append(r)

    if len(out) == 4:
        s = np.array([r["standoff"] for r in out])
        print(f"\n  standoff spread {s.min():+.2f} .. {s.max():+.2f} mm "
              f"(range {np.ptp(s):.2f} mm)")
        print("  port/stbd mirror check: "
              f"fore {abs(s[0] - s[1]):.2f} mm, aft {abs(s[2] - s[3]):.2f} mm")
        print("\n  => BAY_BACK_X must place the frame's outer face at each "
              "station's standoff;\n     a single shared value is only valid "
              "if the spread is small.")


if __name__ == "__main__":
    main()
