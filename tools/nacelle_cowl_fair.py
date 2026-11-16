#!/usr/bin/env python3
"""
nacelle_cowl_fair.py — measure the canonical nacelle skin where the 64 mm
intake cowl joins it, and write the per-azimuth fairing table that
nacelle_pod_64mm_tandem.scad lofts the cowl from.

WHY
---
airframe/AGENTS.md "Geometry Integrity": deviations from the canonical
exterior hull shall be minimised, and every deviation shall keep the style and
character of the Serenity spaceship.  The 64 mm intake needs a highlight
radius of 40 mm (64 mm throat + 8 mm lipE flare), wider than the canonical
dome ahead of Z ~30, so some deviation forward is unavoidable.  The previous
lip ring held a CYLINDER (r 45.05 mm) to Z 23.3 and then dropped inside the
skin: a plain can standing proud of the dome with a groove behind it, which
the canonical engine (Henning model [REF-CAD-002]; QMx blueprint pack
[REF-CAD-003] Sheets 3/4) never shows — there the cowl rolls continuously from
the intake lip into the bulbous forward shell.

The replacement cowl keeps the CFD-selected lipE nose exactly (highlight
r 40.0, external ellipse 1.5625 x 2.5 mm, nose radius 4.0 mm = internal;
tools/nacelle_intake_cfd.py) and then, on each azimuth, runs a monotone
cubic Hermite from the lip shoulder (r 42.5, slope 0) to the MEASURED skin at
the junction station, matching the skin's radius and slope there.  The
cowl therefore inherits the canonical dome's asymmetry and joins it with no
step, crease or groove.

OUTPUT
------
airframe/openscad/nacelles/nacelle_cowl_fair_table.scad (GENERATED — do not
hand-edit): for each shell (port / starboard source mesh) a list of
[azimuth_deg, z_junction_mm, r_skin_mm, dr_dz] at each azimuth's junction, in
the 64 mm pod-local frame
(shell scaled by P64_K radially and P64_A axially, bore on the Z axis — the
same transform as nacelle_pod_50mm_tandem.scad nacelle_shell_imported()).

Run:  /usr/bin/python3 tools/nacelle_cowl_fair.py
Requires trimesh + numpy (system Python; the repo .venv hides them).

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of Steve
Griffing, PE (GitHub Stab-Rabbit-coding), 2026-11-01.
License: CERN-OHL-W-2.0 — writes CAD source (root AGENTS.md licence by output);
see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""

import itertools
import math
import pathlib
import sys

import numpy as np
import trimesh

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import nacelle_64_scale  # noqa: E402  single source
import nacelle_hollow_profile as nhp  # noqa: E402  shell file/placement

P64_K = nacelle_64_scale.get("P64_K")
P64_A = nacelle_64_scale.get("P64_A")

ROOT = pathlib.Path(__file__).resolve().parents[1]
STL_DIR = ROOT / "airframe" / "stls" / "nacelles"
OUT = ROOT / "airframe" / "openscad" / "nacelles" / "nacelle_cowl_fair_table.scad"

# Shell files and placement — single source with the 50 mm hollow-profile tool
# (same values as nacelle_pod_50mm_tandem.scad BORE_CX_* / BORE_CY).
SHELLS = nhp.SHELLS
BORE_CY = nhp.BORE_CY

# Upper bound of the junction search (pod-local Z): the dome's crest region.
# The junctions actually chosen are printed on each run (2026-11-01: Z 28-45).
COWL_ZJ = 50.0      # [mm]
COWL_Z_LO = 28.0    # [mm] earliest junction (lip shoulder hand-off room)
DZ_SLOPE = 2.0      # [mm] central-difference half-step for dr/dz
LIP_SHOULDER_R = 42.5   # [mm] = P64_FORE_R (CFD lipE), pod SCAD
LIP_SHOULDER_Z = 1.5625  # [mm] = P64_FORE_A, pod SCAD
COWL_SINK = 0.3         # [mm] = P64_COWL_SINK, pod SCAD
N_AZ = 72           # 5 deg azimuth resolution


def load_shell(name, cx):
    """Load a source shell into the 64 mm pod-local frame."""
    mesh = trimesh.load_mesh(STL_DIR / name, force="mesh")
    v = mesh.vertices.copy()
    v[:, 0] = (v[:, 0] - cx) * P64_K
    v[:, 1] = (v[:, 1] + BORE_CY) * P64_K
    v[:, 2] = v[:, 2] * P64_A
    mesh.vertices = v
    return mesh


def ray_radius(sec, az_deg):
    """Outermost skin radius on the ray at azimuth az_deg in a Z section."""
    d = np.array([math.cos(math.radians(az_deg)), math.sin(math.radians(az_deg))])
    best = 0.0
    for ent in sec.entities:
        pts = sec.vertices[ent.points][:, :2]
        for p, q in itertools.pairwise(pts):
            # Solve t*d = p + s*(q - p), t >= 0, 0 <= s <= 1.
            e = q - p
            den = d[0] * (-e[1]) - d[1] * (-e[0])
            if abs(den) < 1e-12:
                continue
            t = (p[0] * (-e[1]) - p[1] * (-e[0])) / den
            s = (d[0] * p[1] - d[1] * p[0]) / den
            if t > 0 and -1e-9 <= s <= 1 + 1e-9:
                best = max(best, t)
    if best <= 0:
        raise RuntimeError(f"ray at az {az_deg} missed the skin")
    return best


def table(mesh):
    """Per azimuth: the EARLIEST station on [COWL_Z_LO, COWL_ZJ] where the
    skin can be met with G1 continuity by the monotone cubic Hermite the pod
    SCAD builds from the lip shoulder (slope 0) — i.e. where
    0 <= dr/dz <= 3 (r - sink - R_sh) / (z - Z_sh) (Fritsch-Carlson; the SCAD
    clamp is then inactive) — or the skin's local crest if that comes first
    (dr/dz <= 0 there; reported as 0).  Earliest = shortest departure from
    canon.  Code review 2026-11-01 found the first cut (crest on Z 28-40)
    clamped the end slope on rising-skin azimuths, leaving ~6 deg kinks."""
    zs = np.arange(COWL_Z_LO - DZ_SLOPE, COWL_ZJ + DZ_SLOPE + 1e-9, 1.0)
    secs = {}
    for z in zs:
        sec = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if sec is None:
            raise RuntimeError(f"no skin section at Z {z}")
        secs[round(z, 3)] = sec
    rows = []
    for i in range(N_AZ):
        az = 360.0 * i / N_AZ
        r = {z: ray_radius(sec, az) for z, sec in secs.items()}
        pick = None
        for z in sorted(z for z in r if COWL_Z_LO - 1e-9 <= z <= COWL_ZJ + 1e-9):
            slope = (r[round(z + DZ_SLOPE, 3)] - r[round(z - DZ_SLOPE, 3)]) / (2 * DZ_SLOPE)
            rise = r[z] - COWL_SINK - LIP_SHOULDER_R
            if rise <= 0:
                continue
            if slope <= 0 or slope <= 3 * rise / (z - LIP_SHOULDER_Z):
                pick = (az, z, r[z], max(0.0, slope))
                break
        if pick is None:
            raise SystemExit(f"az {az}: no G1 junction on Z {COWL_Z_LO}-{COWL_ZJ}")
        rows.append(pick)
    return rows


def main():
    out = [
        "// GENERATED by tools/nacelle_cowl_fair.py — DO NOT HAND-EDIT.",
        "// Canonical skin radius and slope at the 64 mm intake-cowl junction,",
        "// per azimuth, 64 mm pod-local frame.  Rows: [az_deg, z_junction_mm, r_mm, dr_dz].",
        "// SPDX-License-Identifier: CERN-OHL-W-2.0",
        "// Generator constants — the pod SCAD asserts its own P64_* values",
        "// equal these, so a change on either side fails at parse time.",
        f"COWL_GEN_SHOULDER_R = {LIP_SHOULDER_R};",
        f"COWL_GEN_SHOULDER_Z = {LIP_SHOULDER_Z};",
        f"COWL_GEN_SINK = {COWL_SINK};",
    ]
    for side, (name, cx) in SHELLS.items():
        rows = table(load_shell(name, cx))
        rmin = min(r for _, _, r, _ in rows)
        print(f"{side}: r_skin at junction: min {rmin:.2f} max "
              f"{max(r for _, _, r, _ in rows):.2f} mm; junction Z "
              f"{min(z for _, z, _, _ in rows):.0f}..{max(z for _, z, _, _ in rows):.0f}")
        if rmin < LIP_SHOULDER_R + 1.0:
            raise SystemExit(f"{side}: skin at the junction is under the lip "
                             f"shoulder + 1 mm ({rmin:.2f}) — raise COWL_ZJ")
        out.append(f"COWL_SKIN_{side} = [")
        out += [f"    [{az:6.1f}, {z:5.1f}, {r:7.3f}, {s:7.4f}]," for az, z, r, s in rows]
        out.append("];")
    OUT.write_text("\n".join(out) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
