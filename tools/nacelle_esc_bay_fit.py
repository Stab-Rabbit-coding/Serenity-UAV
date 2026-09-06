#!/usr/bin/env python3
"""
nacelle_esc_bay_fit.py — site the hinged Open-Secure-ESC boards in the nacelle.

THE BOARD  (owner direction, 2026-09-01)
----------------------------------------
Each of the two ESCs in a nacelle is TWO PCBs joined by a hinge:

    power panel   23.0 mm wide
    signal panel  10.0 mm wide
    total         33.0 mm across the fold

The hinge exists because the board cannot narrow.  32 mm is the floor set by
`Open-Secure-ESC/.../isolation_envelope.py` — 12.90 mm widest non-isolated part
+ 2 x (7.5 creepage + 1.43 inset) + 2 x 0.55, off the ADM2582E/ADM2587E Table 6
clearance — and the pod's annulus is 7 mm deep.  A flat 33 mm board chords the
annulus; a folded one follows it.

WHY THAT MATTERS, IN ONE NUMBER
--------------------------------
A PCB is flat, and the corners of a flat board swing out of a curved annulus.
The sagitta of a chord of width w on a circle of radius R is R - sqrt(R^2 -
(w/2)^2).  At R = 33 mm:

    one flat 33.0 mm board     4.41 mm   <- eats 63 % of a 7 mm annulus
    23.0 mm power panel        2.03 mm
    10.0 mm signal panel       0.38 mm

Folding does not make the board smaller.  It makes its DEVIATION FROM THE ARC
smaller, and that is the dimension the pod is short of.

WHAT THIS TOOL DOES
-------------------
Ray-casts the canonical shell, then searches every hinge azimuth and every
mounting radius for the longest axial run in which BOTH panels clear the duct
wall on the inside and stay under the skin, less one minimum wall, on the
outside.  The binding points are the OUTER CORNERS of each panel, at radius
sqrt(d_out^2 + (w/2)^2) and azimuth phi +/- atan((w/2)/d_out) — never the panel
centre, which is why a model that treats the bay as an annular sector gets the
wrong answer and recommends a wide, short board.

It also reports what the bay costs: holding the skin at the 2.5 mm minimum
across the bay sectors partly undoes the forward-biased wall schedule that
`nacelle_hollow_profile.py` uses to move the CG aft.

Usage:
    /usr/bin/python3 tools/nacelle_esc_bay_fit.py
    /usr/bin/python3 tools/nacelle_esc_bay_fit.py --stack 4.0 --verbose

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
Analysis and tool by Claude (Claude Opus 5, Anthropic) under the author's
direction, per AGENTS.md S3 "Attribution and Licensing".
License: CC BY 4.0 - creativecommons.org/licenses/by/4.0
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

try:
    import trimesh
except ImportError:  # pragma: no cover - environment guard
    print("Missing dependency 'trimesh'. Install requirements-dev.txt first.")
    raise

REPO = Path(__file__).resolve().parent.parent

# ── The board, per owner direction ───────────────────────────────────────────
W_POWER = 23.0        # [mm] power panel width
W_SIGNAL = 10.0       # [mm] signal panel width
BOARD_T = 1.6         # [mm] PCB thickness (both panels)

# ── The pod, mirrored from nacelle_pod_50mm_tandem.scad ──────────────────────
SKIN_WALL = 2.5       # WALL_T — the repo minimum, 4 perimeters at 0.6 mm
DUCT_WALL = 2.5       # CAVITY_DUCT_WALL
BORE_CX = {"PORT": 42.72, "STBD": 155.02}
BORE_CY = 190.79
SHELL = {"PORT": "eng_left_shell24_50mm_repaired.stl",
         "STBD": "eng_right_shell24_50mm_repaired.stl"}

#: Azimuths already spoken for, as (centre, half-width) in degrees.
#: 0 deg is nacelle-local +X.  The nav cableway rides the OUTBOARD skin and the
#: disconnect bay and trunnion collar both sit on the INBOARD face, so for the
#: port pod (PYLON_SIDE -1) those are 0 deg and 180 deg respectively.
EXCLUDE = [(0.0, 10.0), (180.0, 34.0)]

#: The bay may not run into the intake bell or the nozzle ring pocket.
Z_MIN, Z_MAX = 70.0, 160.0
DZ = 2.0
N_AZ_SAMPLE = 360     # 1 deg skin sampling — the corner test needs fine azimuth


def duct_r(z: float) -> float:
    """Bore radius at station z (EDF1 section, then the sleeve zone)."""
    return 27.7 if z >= 90.0 else 25.0


def skin_grid(side: str):
    """Ray-cast the outer skin radius on a (Z, azimuth) grid."""
    mesh = trimesh.load_mesh(REPO / "airframe/stls/nacelles" / SHELL[side],
                             force="mesh")
    mesh.apply_translation([-BORE_CX[side], BORE_CY, 0.0])
    zs = np.arange(Z_MIN, Z_MAX + DZ / 2, DZ)
    az = np.arange(N_AZ_SAMPLE) * 360.0 / N_AZ_SAMPLE
    origins, dirs = [], []
    for z in zs:
        for a in np.radians(az):
            origins.append([200.0 * math.cos(a), 200.0 * math.sin(a), z])
            dirs.append([-math.cos(a), -math.sin(a), 0.0])
    loc, ray, _ = mesh.ray.intersects_location(np.asarray(origins),
                                               np.asarray(dirs),
                                               multiple_hits=True)
    out = np.zeros(len(origins))
    np.maximum.at(out, ray, np.hypot(loc[:, 0], loc[:, 1]))
    if (out == 0).any():
        raise ValueError(f"{side}: {(out == 0).sum()} rays missed the shell")
    return zs, az, out.reshape(len(zs), N_AZ_SAMPLE)


def skin_at(skin, k: int, deg: float) -> float:
    """Skin radius at ring k and an arbitrary azimuth, conservatively."""
    i = int(round(deg)) % N_AZ_SAMPLE
    j = (i + 1) % N_AZ_SAMPLE
    return min(skin[k, i], skin[k, j])


def panel_fits(skin, k: int, z: float, phi: float, w: float, d_in: float,
               stack: float) -> bool:
    """Does one flat panel of width w fit at ring k?

    `d_in` is the perpendicular distance from the duct axis to the panel's INNER
    face; the component stack grows outward from there.
    """
    if d_in < duct_r(z) + DUCT_WALL:
        return False
    d_out = d_in + stack
    half = w / 2.0
    corner_r = math.hypot(d_out, half)
    corner_da = math.degrees(math.atan2(half, d_out))
    for sgn in (-1.0, 1.0):
        if corner_r > skin_at(skin, k, phi + sgn * corner_da) - SKIN_WALL:
            return False
    return True


def hinge_fits(skin, k: int, z: float, phi_h: float, d_in: float,
               stack: float) -> bool:
    """Both panels of the folded assembly, hinged at azimuth `phi_h`.

    Each panel is tangent to the same inner circle, so the fold angle is the sum
    of the two half-angles — the panels sit at 180 - (a1 + a2) degrees to each
    other.  The power panel is placed on the +phi side by convention; the search
    covers both by sweeping phi_h through 360 deg.
    """
    a_pow = math.degrees(math.atan2(W_POWER / 2.0, d_in))
    a_sig = math.degrees(math.atan2(W_SIGNAL / 2.0, d_in))
    return (panel_fits(skin, k, z, phi_h + a_pow, W_POWER, d_in, stack)
            and panel_fits(skin, k, z, phi_h - a_sig, W_SIGNAL, d_in, stack))


def excluded(phi_h: float, d_in: float) -> bool:
    """Does the folded assembly's angular footprint hit a reserved sector?"""
    a_pow = math.degrees(math.atan2(W_POWER / 2.0, d_in))
    a_sig = math.degrees(math.atan2(W_SIGNAL / 2.0, d_in))
    lo, hi = phi_h - 2 * a_sig, phi_h + 2 * a_pow
    for centre, half in EXCLUDE:
        for turn in (-360.0, 0.0, 360.0):
            c = centre + turn
            if lo <= c + half and hi >= c - half:
                return True
    return False


def best_bays(skin, zs, stack: float, d_step: float = 0.25):
    """Longest axial run at every hinge azimuth, over all mounting radii."""
    results = []
    for phi_h in np.arange(0.0, 360.0, 1.0):
        best = None
        d = duct_r(Z_MIN) + DUCT_WALL
        while d < 40.0:
            if excluded(float(phi_h), d):
                d += d_step
                continue
            ok = [hinge_fits(skin, k, float(z), float(phi_h), d, stack)
                  for k, z in enumerate(zs)]
            run = cur = 0
            end = cur_start = start = 0
            for k, good in enumerate(ok):
                if good:
                    if cur == 0:
                        cur_start = k
                    cur += 1
                    if cur > run:
                        run, start, end = cur, cur_start, k
                else:
                    cur = 0
            if run and (best is None or run > best[0]):
                best = (run, float(zs[start]), float(zs[end]), d)
            d += d_step
        if best:
            results.append((float(phi_h), *best))
    results.sort(key=lambda r: (-r[1], r[0]))
    return results


#: Which NACELLE_SIDE each published pod is rendered with.  The Rev R1
#: nacelle-swap renamed the outputs to match their PHYSICAL mounting side but
#: left the shell selector alone, so the mapping is INVERTED and every consumer
#: has to know it.  Getting it wrong put 442 mm3 of cover inside the pod.
POD_SIDE = {"port": -1, "stbd": +1}
COVERS = {"port": ["port_a", "port_b"], "stbd": ["stbd_a", "stbd_b"]}

#: A boolean of two independently-built meshes never returns exactly zero; this
#: is the floor below which the residue is boundary noise rather than a foul.
FIT_TOL_MM3 = 1.0


def check_cover_fit() -> list[str]:
    """T9 — do the published covers actually fit the published pods?

    This is a MESH-AGAINST-MESH test on the built artefacts, not a re-derivation
    from the same parameters that built them, and that distinction is the only
    reason it is worth running: the parameters agreed perfectly while the covers
    were being built on the wrong shell.  Only geometry catches that.
    """
    import trimesh
    from manifold3d import Manifold, Mesh

    def man(m):
        return Manifold(Mesh(
            vert_properties=np.asarray(m.vertices, dtype=np.float32),
            tri_verts=np.asarray(m.faces, dtype=np.uint32)))

    # The published pods are BAKED to hull frame; the covers are part-local.
    # Comparing them as they sit on disk is meaningless — and worse than
    # meaningless, because the two frames partly overlap in space, so the test
    # returns a plausible non-zero number instead of an obvious nonsense.  That
    # is exactly how this check failed the first time it was run.  Un-bake the
    # pod using bake_hull_frame's own recorded placement rather than restating
    # the transform here.
    sys.path.insert(0, str(REPO / "tools"))
    import bake_hull_frame as bake

    def unbake(mesh, component):
        _, placement = bake.COMPONENTS[component]
        px, py, pz, qx, qy, qz, qw = placement
        rot = bake.quat_to_matrix(qx, qy, qz, qw)
        out = mesh.copy()
        out.vertices = (rot.T @ (mesh.vertices - [px, py, pz]).T).T
        return out

    fails = []
    base = REPO / "airframe/stls/nacelles"
    for side, bays in COVERS.items():
        pod_path = base / f"nacelle_{side}_revs.stl"
        if not pod_path.exists():
            fails.append(f"T9 {side}: pod not published")
            continue
        raw = trimesh.load_mesh(pod_path, force="mesh")
        comp = "Nacelle_Port" if side == "port" else "Nacelle_Stbd"
        pod = man(unbake(raw, comp))
        for bay in bays:
            cov_path = base / "esc" / f"nacelle_esc_cover_{bay}.stl"
            if not cov_path.exists():
                fails.append(f"T9 {bay}: cover not published")
                continue
            cov = trimesh.load_mesh(cov_path, force="mesh")
            inter = (pod ^ man(cov)).to_mesh()
            vol = 0.0
            if len(inter.tri_verts):
                vol = abs(trimesh.Trimesh(
                    vertices=inter.vert_properties[:, :3],
                    faces=inter.tri_verts, process=False).volume)
            state = "ok  " if vol <= FIT_TOL_MM3 else "FAIL"
            print(f"  {state} [T9] {bay} in nacelle_{side}: cover/pod "
                  f"interference {vol:.3f} mm3 (tol {FIT_TOL_MM3})")
            if vol > FIT_TOL_MM3:
                fails.append(f"T9 {bay}")
    return fails


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--stack", type=float, default=4.0,
                    help="component stack height above the PCB inner face, mm")
    ap.add_argument("--side", default="PORT", choices=list(SHELL))
    ap.add_argument("--verbose", "-v", action="store_true")
    ap.add_argument("--check-fit", action="store_true",
                    help="T9 only: test the published covers against the "
                         "published pods, mesh against mesh")
    args = ap.parse_args()

    if args.check_fit:
        print("T9  ESC access cover vs pod — published meshes\n")
        fails = check_cover_fit()
        print()
        if fails:
            print(f"FAILED: {', '.join(fails)}")
            return 2
        print("All covers fit their pods.")
        return 0

    print("Hinged ESC bay fit — Open-Secure-ESC in the Rev T4b hollowed pod\n")
    print(f"  board: {W_POWER:.1f} mm power + {W_SIGNAL:.1f} mm signal "
          f"= {W_POWER + W_SIGNAL:.1f} mm folded, {BOARD_T} mm PCB")
    for label, w in (("one flat board", W_POWER + W_SIGNAL),
                     ("power panel", W_POWER), ("signal panel", W_SIGNAL)):
        r = 33.0
        sag = r - math.sqrt(max(r * r - (w / 2) ** 2, 0.0))
        print(f"    sagitta at R 33, {label:<15} {w:5.1f} mm wide: {sag:5.2f} mm")

    zs, _, skin = skin_grid(args.side)

    print(f"\n  stack height {args.stack:.1f} mm "
          f"(PCB {BOARD_T} + {args.stack - BOARD_T:.1f} of parts and mounting)")
    print(f"\n  {'hinge az':>9}{'Z from':>9}{'Z to':>8}{'length':>9}"
          f"{'d_in':>8}{'centroid':>10}")
    rows = best_bays(skin, zs, args.stack)
    for phi, run, z0, z1, d in rows[:12]:
        print(f"  {phi:9.0f}{z0:9.1f}{z1:8.1f}{z1 - z0 + DZ:9.1f}"
              f"{d:8.2f}{(z0 + z1) / 2:10.1f}")

    if not rows:
        print("\n  NO BAY FITS at this stack height.")
        return 2

    phi, run, z0, z1, d = rows[0]
    a_pow = math.degrees(math.atan2(W_POWER / 2.0, d))
    a_sig = math.degrees(math.atan2(W_SIGNAL / 2.0, d))
    print(f"\n  BEST: hinge at azimuth {phi:.0f} deg, Z {z0:.0f}-{z1:.0f} "
          f"({z1 - z0 + DZ:.0f} mm), inner face at R {d:.2f}")
    print(f"    power panel centre  az {phi + a_pow:7.2f} deg  (half-angle "
          f"{a_pow:.2f})")
    print(f"    signal panel centre az {phi - a_sig:7.2f} deg  (half-angle "
          f"{a_sig:.2f})")
    print(f"    fold angle {a_pow + a_sig:.2f} deg — panels at "
          f"{180 - a_pow - a_sig:.1f} deg to each other")
    print(f"    angular footprint {2 * (a_pow + a_sig):.1f} deg, "
          f"az {phi - 2 * a_sig:.1f} .. {phi + 2 * a_pow:.1f}")
    print(f"    board area {(z1 - z0 + DZ) * (W_POWER + W_SIGNAL):.0f} mm2 "
          f"vs as-built 32.0 x 66.1 = 2115 mm2 "
          f"({100 * (z1 - z0 + DZ) * (W_POWER + W_SIGNAL) / 2115:.0f} %)")

    # The second bay: the best one at least 120 deg away, so the two ESCs do not
    # share a sector and the pod keeps hoop material between them.
    for phi2, run2, z02, z12, d2 in rows:
        sep = abs((phi2 - phi + 180) % 360 - 180)
        if sep >= 120:
            print(f"\n  SECOND BAY: hinge azimuth {phi2:.0f} deg "
                  f"({sep:.0f} deg away), Z {z02:.0f}-{z12:.0f} "
                  f"({z12 - z02 + DZ:.0f} mm), R {d2:.2f}")
            break
    return 0


if __name__ == "__main__":
    sys.exit(main())
