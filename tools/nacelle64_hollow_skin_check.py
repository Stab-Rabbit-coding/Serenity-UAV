#!/usr/bin/env python3
"""nacelle64_hollow_skin_check.py -- does the 64 mm pod's hollow cavity leave a real outer skin?

WHY THIS EXISTS
---------------
2026-11-22 (WBS NAC-64-HOLLOW-SKIN): tools/nacelle_hollow_profile.py measured the skin by casting
each ray through the duct axis and keeping the LARGEST hit, so its skin grid at an azimuth is the
larger of that side and the opposite side.  The committed cavity grid (HOLLOW_R_* / HOLLOW_SKIN_*
in nacelle_pod_64mm_tandem.scad) was therefore cut to the fatter side's skin.  This tool measures
the consequence on a pod mesh (published or freshly rendered).

METHOD
  1. Near-side truth: re-cast the canonical shell (same file, frame and grid as the hollow tool),
     keeping only hits on the ray's own side of the axis.
  2. Grid wall: wall = K * near - cavity', with
     cavity' = HOLLOW_R + (K - 1) * HOLLOW_SKIN (the SCAD's radial_k_cavity) at Z * A.  A cell
     is live where the cavity is open (not pushed into the duct wall).  wall < 0 means the
     cavity surface lies outside the true skin.
  3. Real part: for EVERY live cell (not only those the grid flags -- the grid is the model under
     test), cast a ray from the axis through the pod (nacelle-local: --pod-local).  The skin is
     present where the pod's outermost surface lies outside the cavity's INNER surface (bore +
     duct wall): a ray that leaves through the cavity ends at that inner surface.  Its thickness
     is the outermost solid layer.  With --pod-nocavity (the same pod rendered with
     hollow_cavity() commented out), a thin layer the cavity did not change is a feature of
     another cut (pocket floor, register bore) and is listed as "feature_thin"; a cell open in
     both renders is a designed opening ("feature_open").  Neither is gated here.
     Classify: skin present >= 0.079 in (2.0 mm) / present < 2.0 mm /
     open but an ESC cover closes it / open with nothing modelled closing it.
  The map is written to docs/figures/nacelle64_hollow_skin_check.png.

Usage:  /usr/bin/python3 tools/nacelle64_hollow_skin_check.py --pod-local POD.stl
            [--pod-nocavity POD_NOCAV.stl] --covers C0.stl C1.stl [--json OUT]
        All meshes in the frame the pod was rendered in (duct axis = Z, intake face Z 0).
        FRAME (fixed 2026-11-22): the SCAD's default render (NACELLE_SIDE = +1) imports the
        left shell and cuts the HOLLOW_*_PORT grid; --side must match the render (default PORT).
        Before this fix the check read the STBD grid against that render: cell selection was
        mirrored (the two grids differ by up to 12.7 mm unmirrored).  Exit 2 if any cell
        is open with nothing closing it, any skin is thinner than 2.0 mm, or the grid puts the
        cavity outside the true skin at a cell no ESC cover closes.
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


def near_skin(z_list, naz, side: str = "PORT"):
    name, cx = hp.SHELLS[side]
    mesh = trimesh.load_mesh(REPO / "airframe/stls/nacelles" / name, force="mesh")
    mesh.apply_translation([-cx, hp.BORE_CY, 0.0])
    ol, dl = [], []
    for z in z_list:
        for j in range(naz):
            a = math.radians(j * 360.0 / naz)
            ol.append([200 * math.cos(a), 200 * math.sin(a), z])
            dl.append([-math.cos(a), -math.sin(a), 0.0])
    o, d = np.array(ol), np.array(dl)
    loc, idx, _ = mesh.ray.intersects_location(o, d, multiple_hits=True)
    keep = (loc[:, :2] * -d[idx, :2]).sum(1) > 0.0
    out = np.full(len(o), np.nan)
    np.fmax.at(out, idx[keep], np.hypot(loc[keep, 0], loc[keep, 1]))
    return out.reshape(len(z_list), naz)


def radial_hits(mesh, z, a):
    return radial_hits_many(mesh, [(z, a)])[0]


def radial_hits_many(mesh, za) -> list:
    """Sorted hit radii of rays from the axis at (z, azimuth rad), one array per ray."""
    o = np.array([[0.0, 0.0, z] for z, _ in za])
    d = np.array([[math.cos(a), math.sin(a), 0.0] for _, a in za])
    loc, idx, _ = mesh.ray.intersects_location(o, d, multiple_hits=True)
    r = np.hypot(loc[:, 0], loc[:, 1])
    return [np.sort(r[idx == i]) for i in range(len(za))]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Hollow-cavity skin check of the 64 mm pod.")
    ap.add_argument("--pod-local", type=Path, required=True)
    ap.add_argument(
        "--side",
        choices=("PORT", "STBD"),
        default="PORT",
        help="shell and cavity grid the pod was rendered with: the SCAD default "
        "(NACELLE_SIDE = +1) imports the LEFT shell and cuts HOLLOW_*_PORT -> PORT",
    )
    ap.add_argument("--pod-nocavity", type=Path, help="same pod without hollow_cavity()")
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
    r50, sk50 = scad_array(src, f"HOLLOW_R_{a.side}"), scad_array(src, f"HOLLOW_SKIN_{a.side}")
    k_r, k_a = ns.get("P64_K"), ns.get("P64_A")
    cav = r50 + (k_r - 1) * sk50
    true = near_skin(z50, r50.shape[1], a.side)
    inner = np.array([hp.bore_r(float(z)) + hp.DUCT_WALL for z in z50])[:, None] * k_r
    live = cav >= inner - 0.1
    wall = np.where(live, k_r * true - cav, np.nan)

    pod = trimesh.load(a.pod_local)
    covers = [trimesh.load(c) for c in a.covers]
    cls: dict[str, list] = {
        "skin_ok": [],
        "thin": [],
        "feature_thin": [],
        "feature_open": [],
        "covered": [],
        "uncovered": [],
    }
    naz = r50.shape[1]
    cells = np.argwhere(live)
    za = [(float(z50[k] * k_a), math.radians(j * 360.0 / naz)) for k, j in cells]
    hp_ = radial_hits_many(pod, za)
    hn_ = radial_hits_many(trimesh.load(a.pod_nocavity), za) if a.pod_nocavity else None
    hc_ = [radial_hits_many(c, za) for c in covers]
    flagged = 0
    for n, (k, j) in enumerate(cells):
        rr = hp_[n]
        row = [round(za[n][0], 1), j * 360.0 / naz, round(float(wall[k, j]), 2)]
        flagged += bool(wall[k, j] < MIN_WALL)
        # Skin present unless the ray left through the cavity (it then ends on the cavity's
        # inner surface); its thickness is the outermost solid layer.
        if len(rr) > 1 and rr[-1] > inner[k, 0] + 0.5:
            t = float(rr[-1] - rr[-2])
            if t >= MIN_WALL and wall[k, j] >= MIN_WALL:
                continue  # grid and part agree: not plotted
            key = "skin_ok" if t >= MIN_WALL else "thin"
            if key == "thin" and hn_ is not None and len(hn_[n]) > 1:
                rn = hn_[n]
                if abs(rn[-1] - rr[-1]) < 0.3 and abs((rn[-1] - rn[-2]) - t) < 0.3:
                    key = "feature_thin"  # the cavity did not make this layer
            cls[key].append(row + [round(t, 2)])
        elif any(len(h[n]) for h in hc_):
            cls["covered"].append(row)
        elif hn_ is not None and not (len(hn_[n]) > 1 and hn_[n][-1] > inner[k, 0] + 0.5):
            cls["feature_open"].append(row)  # open without the cavity too: a designed opening
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
        "cells_probed": len(cells),
        "grid_flagged": flagged,
        "classified": cls,
    }
    print(
        f"tool skin over the near-side truth: max {res['tool_skin_over_truth_max_mm']:.2f} mm, "
        f"{res['cells_tool_over_0p3']} of {res['cells']} cells > 0.3 mm"
    )
    print(
        f"not gated (other cuts): designed openings {res['n_feature_open']}, "
        f"< 2.0 mm walls made by another cut {res['n_feature_thin']}"
        + ("" if a.pod_nocavity else " (pass --pod-nocavity to separate them)")
    )
    print(
        f"live cavity cells {res['live']}: cavity outside the true skin "
        f"{res['cavity_outside_skin']}, "
        f"wall < 2.0 mm {res['wall_below_2mm']}"
    )
    print(
        f"on the pod mesh: skin >= 2.0 {res['n_skin_ok']}, skin < 2.0 {res['n_thin']}, "
        f"open + ESC cover {res['n_covered']}, OPEN with nothing closing it {res['n_uncovered']} "
        f"({res['uncovered_with_cavity_outside']} where the cavity is outside the skin)"
    )
    if a.json:
        a.json.write_text(json.dumps(res, indent=1, default=float))
    figure(a.fig, wall, z50 * k_a, naz, cls)
    return 2 if (cls["uncovered"] or cls["thin"] or res["uncovered_with_cavity_outside"]) else 0


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
        ("feature_open", "#7a7a7a", "designed opening (open without the cavity too)"),
        ("feature_thin", "#b58cd0", "< 2.0 mm wall made by another cut, not the cavity"),
        ("thin", "#e08a00", "cavity leaves pod skin < 0.079 in (2.0 mm)"),
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
        "As-built starboard 64 mm pod: every live hollow-cavity cell ray-cast on the real STL\n"
        "(cells where grid and part both leave >= 2.0 mm are grey)",
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
