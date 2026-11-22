#!/usr/bin/env python3
"""nacelle64_hollow_skin_check.py -- does the 64 mm pod's hollow cavity leave a real outer skin?

WHY THIS EXISTS
---------------
2026-11-22 (WBS NAC-64-HOLLOW-SKIN): tools/nacelle_hollow_profile.py measured the skin by casting
each ray through the duct axis and keeping the LARGEST hit, so its skin grid at an azimuth is the
larger of that side and the opposite side.  The committed cavity grid (HOLLOW_R_* / HOLLOW_SKIN_*
in nacelle_pod_64mm_tandem.scad) was therefore cut to the fatter side's skin.  This tool measures
the consequence on the published pod STL.

METHOD
  1. Near-side truth: re-cast the canonical shell (same file, frame and grid as the hollow tool),
     keeping only hits on the ray's own side of the axis.
  2. Grid wall: wall = K * near - cavity', with
     cavity' = HOLLOW_R + (K - 1) * HOLLOW_SKIN (the SCAD's radial_k_cavity) at Z * A.  A cell
     is live where the cavity is open (not pushed into the duct wall).  wall < 0 means the
     cavity surface lies outside the true skin.
  3. Real part: for every live cell with grid wall < 2.0 mm, cast a ray from the axis through the
     published pod (moved to nacelle-local: --pod-local) and the scaled canonical OML (--oml), and
     classify: skin present >= 2.0 mm / present < 2.0 mm / open but an ESC cover closes it / open
     with nothing modelled closing it.
  The map is written to docs/figures/nacelle64_hollow_skin_check.png.

Usage:  /usr/bin/python3 tools/nacelle64_hollow_skin_check.py --pod-local POD.stl --oml OML.stl
            --covers C0.stl C1.stl [--json OUT]
        All meshes nacelle-local (duct axis = Z, intake face Z 0), starboard.  Exit 2 if any cell
        is open with nothing closing it, or any skin is thinner than 2.0 mm.
Requires: numpy, trimesh, matplotlib.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (GitHub Stab-Rabbit-coding) -- owner direction.
AI note: Tool by Claude (Claude Opus 5.5, Anthropic), 2026-11-22, per AGENTS.md sec. 3.
         Analytical; ENGINEERING REVIEW REQUIRED before any result is applied.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import trimesh

import nacelle_64_scale as ns
import nacelle_hollow_profile as hp

REPO = Path(__file__).resolve().parents[1]
SCAD = REPO / "airframe/openscad/nacelles/nacelle_pod_64mm_tandem.scad"
MIN_WALL = 2.0  # AGENTS.md sec. 7


def scad_array(src: str, name: str) -> np.ndarray:
    i = src.index(name + " = [")
    j = src.index("];", i)
    i0, i1 = i + len(name) + 3, j + 1
    body = re.sub(r"//[^\n]*", "", src[i0:i1]).replace("\n", "")
    return np.array(json.loads(re.sub(r",\s*\]", "]", body)), float)


def near_skin(z_list, naz):
    name, cx = hp.SHELLS["STBD"]
    mesh = trimesh.load_mesh(REPO / "airframe/stls/nacelles" / name, force="mesh")
    mesh.apply_translation([-cx, hp.BORE_CY, 0.0])
    o, d = [], []
    for z in z_list:
        for j in range(naz):
            a = math.radians(j * 360.0 / naz)
            o.append([200 * math.cos(a), 200 * math.sin(a), z])
            d.append([-math.cos(a), -math.sin(a), 0.0])
    o, d = np.array(o), np.array(d)
    loc, idx, _ = mesh.ray.intersects_location(o, d, multiple_hits=True)
    keep = (loc[:, :2] * -d[idx, :2]).sum(1) > 0.0
    out = np.full(len(o), np.nan)
    np.fmax.at(out, idx[keep], np.hypot(loc[keep, 0], loc[keep, 1]))
    return out.reshape(len(z_list), naz)


def radial_hits(mesh, z, a):
    o = np.array([[0.0, 0.0, z]])
    d = np.array([[math.cos(a), math.sin(a), 0.0]])
    loc = np.asarray(mesh.ray.intersects_location(o, d)[0]).reshape(-1, 3)
    return np.sort(np.hypot(loc[:, 0], loc[:, 1]))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Hollow-cavity skin check of the 64 mm pod.")
    ap.add_argument("--pod-local", type=Path, required=True)
    ap.add_argument("--oml", type=Path, required=True)
    ap.add_argument("--covers", type=Path, nargs="*", default=[])
    ap.add_argument("--json", type=Path)
    ap.add_argument(
        "--fig", type=Path, default=REPO / "docs/figures/nacelle64_hollow_skin_check.png"
    )
    a = ap.parse_args(argv)

    src = SCAD.read_text()
    zi = src.index("HOLLOW_Z = [")
    z0, z1 = zi + 11, src.index("];", zi) + 1
    z50 = np.array(json.loads(src[z0:z1]))
    r50, sk50 = scad_array(src, "HOLLOW_R_STBD"), scad_array(src, "HOLLOW_SKIN_STBD")
    k_r, k_a = ns.get("P64_K"), ns.get("P64_A")
    cav = r50 + (k_r - 1) * sk50
    true = near_skin(z50, r50.shape[1])
    inner = np.array([hp.bore_r(float(z)) + hp.DUCT_WALL for z in z50])[:, None] * k_r
    live = cav >= inner - 0.1
    wall = np.where(live, k_r * true - cav, np.nan)

    pod, oml = trimesh.load(a.pod_local), trimesh.load(a.oml)
    covers = [trimesh.load(c) for c in a.covers]
    cls: dict[str, list] = {"skin_ok": [], "thin": [], "covered": [], "uncovered": []}
    naz = r50.shape[1]
    for k, j in np.argwhere(wall < MIN_WALL):
        z, az = float(z50[k] * k_a), j * 360.0 / naz
        rr, ro = radial_hits(pod, z, math.radians(az)), radial_hits(oml, z, math.radians(az))
        r_oml = float(ro[-1]) if len(ro) else 0.0
        row = [round(z, 1), az, round(float(wall[k, j]), 2)]
        if len(rr) and rr[-1] > r_oml - 0.8:
            t = float(rr[-1] - rr[-2]) if len(rr) > 1 else 99.0
            cls["skin_ok" if t >= MIN_WALL else "thin"].append(row + [round(t, 2)])
        elif any(len(radial_hits(c, z, math.radians(az))) for c in covers):
            cls["covered"].append(row)
        else:
            cls["uncovered"].append(row)

    w_live = wall[live]
    res = {
        "tool_skin_over_truth_max_mm": float(np.nanmax(sk50 - true)),
        "cells_tool_over_0p3": int((sk50 - true > 0.3).sum()),
        "cells": int(sk50.size),
        "live": int(live.sum()),
        "cavity_outside_skin": int((w_live < 0).sum()),
        "wall_below_2mm": int((w_live < MIN_WALL).sum()),
        **{f"n_{k}": len(v) for k, v in cls.items()},
        "uncovered_with_cavity_outside": sum(1 for r in cls["uncovered"] if r[2] < 0),
        "classified": cls,
    }
    print(
        f"tool skin over the near-side truth: max {res['tool_skin_over_truth_max_mm']:.2f} mm, "
        f"{res['cells_tool_over_0p3']} of {res['cells']} cells > 0.3 mm"
    )
    print(
        f"live cavity cells {res['live']}: cavity outside the true skin "
        f"{res['cavity_outside_skin']}, "
        f"wall < 2.0 mm {res['wall_below_2mm']}"
    )
    print(
        f"on the published pod: skin >= 2.0 {res['n_skin_ok']}, skin < 2.0 {res['n_thin']}, "
        f"open + ESC cover {res['n_covered']}, OPEN with nothing closing it {res['n_uncovered']} "
        f"({res['uncovered_with_cavity_outside']} where the cavity is outside the skin)"
    )
    if a.json:
        a.json.write_text(json.dumps(res, indent=1, default=float))
    figure(a.fig, wall, z50 * k_a, naz, cls)
    return 2 if (cls["uncovered"] or cls["thin"]) else 0


def figure(path: Path, wall, zs, naz, cls) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 2, figsize=(17, 6.8), gridspec_kw=dict(width_ratios=[1.35, 1]))
    p = ax[0]
    k, j = np.where(~np.isnan(wall))
    p.scatter(
        j * 360.0 / naz, zs[k], s=10, c="0.85", marker="s", label="cavity cell, wall OK by grid"
    )
    for key, col, lab in (
        ("thin", "#e08a00", "pod skin present but < 0.079 in (2.0 mm)"),
        ("uncovered", "#d01c1c", "NO skin, nothing modelled closes it"),
        ("covered", "#2a6fdb", "no skin, but an ESC cover closes it (designed bay)"),
    ):
        pts = np.array([[r[1], r[0]] for r in cls[key]]) if cls[key] else np.zeros((0, 2))
        p.scatter(pts[:, 0], pts[:, 1], s=26, c=col, marker="s", label=f"{lab}: {len(pts)} cells")
    p.set_xlabel("azimuth, deg (nacelle-local, starboard: 0 inboard, 90 ventral, 270 dorsal)")
    p.set_ylabel("Z from intake face, mm")
    p.set_xlim(-4, 364)
    p.set_ylim(20, 200)
    p.invert_yaxis()
    p.legend(loc="lower right", fontsize=8.5)
    p.set_title(
        "As-built starboard 64 mm pod: outer skin vs the canonical skin\n(every hollow-cavity grid "
        "cell whose wall the grid leaves < 2.0 mm, checked on the real STL)",
        loc="left",
        fontsize=10,
    )
    h = ax[1]
    ww = wall[~np.isnan(wall)].ravel()
    h.hist(np.clip(ww, -10, 10), bins=40, color="0.5")
    top = h.get_ylim()[1]
    h.axvline(2.0, color="k", ls="--")
    h.text(2.2, top * 0.9, "2.0 mm rule", fontsize=8)
    h.axvline(2.5, color="g", ls=":")
    h.text(2.7, top * 0.8, "design 2.5 mm", fontsize=8, color="g")
    h.axvline(0.0, color="r")
    h.text(-9.5, top * 0.9, "< 0: cavity outside\nthe true skin", fontsize=8, color="r")
    h.set_xlabel("wall the committed cavity grid leaves under the TRUE skin, mm (clipped +/-10)")
    h.set_ylabel("grid cells")
    h.set_title(
        f"{int((ww < 0).sum())} of {ww.size} live cells put the cavity outside the skin;\n"
        f"{int((ww < MIN_WALL).sum())} leave < 2.0 mm (design intent 2.5-8.0 mm)",
        loc="left",
        fontsize=10,
    )
    fig.suptitle(
        "NAC-64-HOLLOW-SKIN: tools/nacelle_hollow_profile.py kept the far-side hit, so the cavity "
        "was cut to the opposite (fatter) side's skin.  Analytical - REQUIRES VERIFICATION on the "
        "printed part.",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(path, dpi=85)


if __name__ == "__main__":
    sys.exit(main())
