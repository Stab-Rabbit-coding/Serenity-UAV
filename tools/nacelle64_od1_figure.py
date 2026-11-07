#!/usr/bin/env python3
"""nacelle64_od1_figure.py -- picture of the OD-1 decision: nozzle spigot vs stage-2 cartridge.

Three Y = 0 half-sections (inches, mm scale on the top/right edges) of the nozzle joint:
the cartridge as it was (read from git, default commit a7bdbc95) with the overlap in red,
option A (the cartridge ends 0.12 in (3 mm) short, the shipped fix) and option B (spigot
removed), plus a 3-D view of the overlap ring.  Reads the published stage-2 cartridge and
nozzle throat/ring STLs; the pod is not needed.

Usage:  python3 tools/nacelle64_od1_figure.py --out docs/figures/nacelle64_od1_spigot_cartridge.png
        [--before-rev a7bdbc95]

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic) under the author's direction, 2026-11-07.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import io
import subprocess
import sys
from pathlib import Path

import manifold3d as m
import numpy as np
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nacelle64_assembly_check as a  # noqa: E402

CART = "airframe/stls/nacelles/edf_motor_mount_64mm_stage2_stbd.stl"
K = 1.0 / a.MM_IN


def load_at(rev: str | None) -> trimesh.Trimesh:
    if rev is None:
        t = trimesh.load(a.ROOT / CART, force="mesh")
    else:
        raw = subprocess.run(["git", "show", f"{rev}:{CART}"], cwd=a.ROOT, capture_output=True,
                             check=True).stdout
        t = trimesh.load(io.BytesIO(raw), file_type="stl", force="mesh")
    return a.xform(t, a.mat4([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, a.CART_Z0], [0, 0, 0, 1]]))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], epilog=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--before-rev", default="a7bdbc95")
    args = ap.parse_args(argv)
    import matplotlib  # noqa: PLC0415

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: PLC0415
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: PLC0415

    z0 = a.NOZ_Z0
    noz = a.STL / "nacelles/nozzles"
    thr_t = trimesh.load(noz / "nacelle_nozzle_throat_64mm_stbd.stl", force="mesh")
    ring_t = trimesh.load(noz / "nacelle_nozzle_ring_64mm_stbd.stl", force="mesh")
    tf = a.mat4([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, z0], [0, 0, 0, 1]])
    thr, ring = a.to_man(a.xform(thr_t, tf)), a.to_man(a.xform(ring_t, tf))
    before, after = a.to_man(load_at(args.before_rev)), a.to_man(load_at(None))
    big = m.Manifold.cube([300, 300, 300], center=True)
    thr_b = thr - big.translate([0, 0, z0 - 150])      # option B: spigot (z < station) removed
    clash = before ^ thr
    to_xz = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0]], float)

    def sec(ax, mn, **kw):
        for p in mn.transform(to_xz).slice(0.0).to_polygons():
            ax.fill(p[:, 0] * K, p[:, 1] * K, **kw)

    fig = plt.figure(figsize=(21, 8))
    cases = [(f"Before: {a.cu_in(clash.volume())} overlap", before, thr, clash),
             ("Option A (shipped): cartridge 0.12 in (3 mm) shorter", after, thr, None),
             ("Option B: spigot removed", before, thr_b, None)]
    for i, (title, cart, t, cl) in enumerate(cases):
        ax = fig.add_subplot(1, 4, i + 1)
        sec(ax, cart, color="tab:blue", alpha=0.75, lw=0)
        sec(ax, t, color="tab:orange", alpha=0.75, lw=0)
        sec(ax, ring, color="tab:brown", alpha=0.6, lw=0)
        if cl is not None:
            sec(ax, cl, color="red", lw=0)
        ax.axhline(z0 * K, color="k", ls="--", lw=0.8)
        ax.text(1.05, z0 * K + 0.02, f"nozzle station Z {z0 * K:.2f} in ({z0:.1f} mm)", fontsize=8)
        ax.set(xlim=(1.0, 1.75), ylim=(7.3, 8.35), aspect="equal", title=title,
               xlabel="in from duct axis (mm on top edge); + = pylon side",
               ylabel="in along duct, aft up (mm on right edge)")
        ax.grid(alpha=0.3)
        ax.secondary_xaxis("top", functions=(lambda v: v * a.MM_IN, lambda v: v / a.MM_IN))
        ax.secondary_yaxis("right", functions=(lambda v: v * a.MM_IN, lambda v: v / a.MM_IN))
    fig.axes[0].text(1.03, 8.15, "orange: nozzle throat\nblue: stage-2 cartridge\n"
                     "brown: unison ring", fontsize=8)
    ax3 = fig.add_subplot(1, 4, 4, projection="3d")
    for mn, col, al in ((before - big.translate([0, 0, z0 - 12 - 150]), "tab:blue", 0.25),
                        (clash, "red", 1.0)):
        t3 = a.to_trimesh(mn)
        ax3.add_collection3d(Poly3DCollection(t3.vertices[t3.faces] * K, facecolor=col,
                                              edgecolor="none", alpha=al))
    ax3.set(xlim=(-1.6, 1.6), ylim=(-1.6, 1.6), zlim=(7.3, 8.1),
            title="3-D: red ring = the overlap\n(aft 0.12 in (3 mm) of the old cartridge)")
    ax3.view_init(elev=25, azim=-60)
    ax3.set_box_aspect((1, 1, 0.3))
    fig.suptitle("OD-1: nozzle throat spigot vs stage-2 cartridge, Y = 0 half-section, stbd "
                 "(port identical); inches, mm in brackets", fontsize=13)
    fig.tight_layout()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=100)
    print(f"overlap before: {a.cu_in(clash.volume())}; option A: "
          f"{a.cu_in(float((after ^ thr).volume()))}; option B: "
          f"{a.cu_in(float((before ^ thr_b).volume()))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
