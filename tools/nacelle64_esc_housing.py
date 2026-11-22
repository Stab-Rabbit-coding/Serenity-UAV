#!/usr/bin/env python3
"""nacelle64_esc_housing.py -- canonical-styled ventral ESC B housings for the 64 mm nacelle (H1).

WHY THIS EXISTS
---------------
Owner decision 2026-11-22, brief H option H1 (docs/THEME_N_DECISION_BRIEFS.md): keep the G1 ESC
bays and pivot and cover ESC B's two ventral bays with housings that stand proud of the canonical
skin, styled after the canonical nacelle: QMx Official Serenity Blueprints (REF-CAD-003) Sheet 5
(ventral plan) and Sheet 3 (stern elevation) show raised rectangular machinery housings on the
nacelle mid-body; the Nick Henning engine renders (REF-CAD-002) show overlapping cowl plates with
stepped lips, panel lines and louvre groups.  Both are internal references only.

GEOMETRY (starboard nacelle-local frame: duct axis +Z from the intake face, az 270 dorsal; the
port pod is the X-mirror, as tools/prep_nacelle_64_bake.py makes it)
  * Each ESC B bay is a hinged board pair (power 20 mm + logic 14 mm panels) whose inner face sits
    at the mount radius 37.2 mm, stack 6.0 mm (power bay) / 6.65 mm (logic bay) outward
    (tools/esc70_design_f1.json).  The housing's two outer faces run parallel to those panels at
    the housing wall: a 2.0 mm plate (AGENTS.md sec. 7 SLS minimum) plus 0.4 mm running clearance
    = 2.4 mm.  NOTE: the bay design (esc70_design_f1.json cover_t 1.5) assumed a 1.5 mm cover,
    which is below the 2.0 mm rule; the housing uses 2.0 mm.
  * 45 deg side chamfers, a 30 deg fairing ramp forward, a 60 deg aft face; the logic housing is
    square-cut at Z_LOGIC_AFT so it abuts, and does not enter, the F1 nozzle housing
    (face Z 160.25).
  * Panel-line grooves (0.8 mm wide, 0.45 mm deep) every 20 mm, kept out of the board envelope.
  * Four louvres on the power face, 2.5 x 9.5 mm each (95 mm2 = the design's four 5.5 mm bleed
    holes), through the plate into the cooling lane: they are the ESC cooling outlets.
  The housing is the solid outside the canonical skin; the pod/cover integration (seats, screws)
  is a separate step (WBS NAC-64-ESC-BLISTER).

BAYS: G1 (owner decision 2026-11-22, pivot Z 109.73 mm), from tools/esc80_cooptimize.py on
tools/esc70_design_f1.json with the G1 keep-outs -- the per-bay "bays" output, port frame.

Usage:  /usr/bin/python3 tools/nacelle64_esc_housing.py --out HOUSING.stl [--json REPORT]
        Exit 2 if a board is left outside the housed skin or the logic housing passes Z_LOGIC_AFT.
Requires: numpy, trimesh, manifold3d.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (GitHub Stab-Rabbit-coding) -- owner direction.
AI note: Tool by Claude (Claude Opus 5.5, Anthropic), 2026-11-22, per AGENTS.md sec. 3.
         Analytical; ENGINEERING REVIEW REQUIRED before any result is applied.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import argparse
import json
import math
import sys
from pathlib import Path

import manifold3d as mf
import numpy as np
import trimesh

import nacelle_64_scale as ns

REPO = Path(__file__).resolve().parents[1]
MOUNT_R = 37.2  # esc80_cooptimize.MOUNT_R (board inner face)
COVER_T = 2.0  # housing plate: AGENTS.md sec. 7 SLS default minimum wall (load case not stated)
COVER_CLR = 0.4  # running clearance, as esc80_cooptimize.overrides_64mm (SKIN_WALL = cover_t + 0.4)
SKIN_WALL = (
    COVER_T + COVER_CLR
)  # 2.4 mm; the F1 bay design (esc70_design_f1.json) assumed cover 1.5
W_POWER, W_SIGNAL = 20.0, 14.0
ENV = {"power": 6.0, "logic": 6.65}  # stack + cooling lane; power bay capped at 2.0 mm parts
Z_LOGIC_AFT = 159.3  # square aft face; F1 nozzle housing face is Z 160.25
GROOVE_PITCH, GROOVE_W, GROOVE_D = 20.0, 0.8, 0.45
LOUVRE = (2.5, 9.5, 4, 4.5)  # length along Z, width, count, pitch (mm)
X_BURY = 36.0  # housing base buried inside the skin (r), so the union is clean

# G1 bays (port frame azimuth = hinge azimuth; Z = board span incl. harness reserves)
G1_BAYS = {
    "A": [{"az": 336.0, "z": [109.4, 157.4]}, {"az": 262.0, "z": [67.4, 105.4]}],
    "B": [{"az": 78.0, "z": [73.4, 133.7]}, {"az": 136.0, "z": [135.4, 157.4]}],
}


def man(t: trimesh.Trimesh) -> mf.Manifold:
    return mf.Manifold(
        mf.Mesh(
            vert_properties=np.asarray(t.vertices, np.float32),
            tri_verts=np.asarray(t.faces, np.uint32),
        )
    )


def tmesh(x: mf.Manifold) -> trimesh.Trimesh:
    q = x.to_mesh()
    return trimesh.Trimesh(np.asarray(q.vert_properties)[:, :3], np.asarray(q.tri_verts))


def canonical_oml() -> mf.Manifold:
    """Scaled canonical starboard shell, nacelle-local (as the 64 mm pod imports it)."""
    sh = trimesh.load_mesh(REPO / "airframe/stls/nacelles/eng_right_shell24_50mm_repaired.stl")
    sh.apply_translation([-155.02, 190.79, 0.0])
    sh.vertices *= [ns.get("P64_K"), ns.get("P64_K"), ns.get("P64_A")]
    return man(sh)


def panel_angles(b: dict) -> list:
    """(width, local centre azimuth) of the power and signal panels; port -> local is 180 - a."""
    ap = math.degrees(math.atan2(W_POWER / 2, MOUNT_R))
    as_ = math.degrees(math.atan2(W_SIGNAL / 2, MOUNT_R))
    return [(W_POWER, 180.0 - (b["az"] + ap)), (W_SIGNAL, 180.0 - (b["az"] - as_))]


def board(b: dict, env: float) -> mf.Manifold:
    acc = None
    for w, a in panel_angles(b):
        p = (
            mf.Manifold.cube([env, w, b["z"][1] - b["z"][0]])
            .translate([MOUNT_R, -w / 2, b["z"][0]])
            .rotate([0, 0, a])
        )
        acc = p if acc is None else acc + p
    return acc


def facet(w: float, a: float, z0: float, z1: float, env: float, aft_square: float | None):
    xt = MOUNT_R + env + SKIN_WALL
    h = xt - X_BURY
    t30, t60 = math.tan(math.radians(30)), math.tan(math.radians(60))
    za_top = z1 + SKIN_WALL if aft_square is None else aft_square
    za_bot = z1 + SKIN_WALL + h / t60 if aft_square is None else aft_square
    top = [
        (xt, y, z)
        for y in (-(w / 2 + SKIN_WALL), w / 2 + SKIN_WALL)
        for z in (z0 - SKIN_WALL, za_top)
    ]
    bot = [
        (X_BURY, y, z)
        for y in (-(w / 2 + SKIN_WALL + h), w / 2 + SKIN_WALL + h)
        for z in (z0 - SKIN_WALL - h / t30, za_bot)
    ]
    pts = [mf.Manifold.cube([0.01, 0.01, 0.01]).translate(list(p)) for p in top + bot]
    return mf.Manifold.batch_hull(pts).rotate([0, 0, a]), xt


def housing(b: dict, role: str) -> mf.Manifold:
    env = ENV[role]
    aft = Z_LOGIC_AFT if role == "logic" else None
    facets = [(w, a) + facet(w, a, b["z"][0], b["z"][1], env, aft) for w, a in panel_angles(b)]
    hs = mf.Manifold.batch_hull([f[2] for f in facets])
    core = board(b, env)
    cuts = None
    zz = np.arange(b["z"][0] + 4.0, b["z"][1] - 2.0, GROOVE_PITCH)
    for w, a, _, xt in facets:
        for z in zz:
            g = (
                mf.Manifold.cube([1.5, w + 2 * SKIN_WALL + 1.0, GROOVE_W])
                .translate([xt - GROOVE_D, -(w / 2 + SKIN_WALL + 0.5), z - GROOVE_W / 2])
                .rotate([0, 0, a])
            )
            cuts = g if cuts is None else cuts + g
    if role == "power":
        w, a, _, xt = facets[0]
        ln, wd, n, pitch = LOUVRE
        for i in range(n):
            zc = b["z"][1] - 3.0 - i * pitch
            c = (
                mf.Manifold.cube([SKIN_WALL + 0.6, wd, ln])
                .translate([xt - SKIN_WALL, -wd / 2, zc - ln / 2])  # through plate + clearance
                .rotate([0, 0, a])
            )
            cuts = c if cuts is None else cuts + c
    return hs - (cuts - core)


def build():
    oml = canonical_oml()
    hs = None
    for role, b in zip(("power", "logic"), G1_BAYS["B"]):
        x = housing(b, role)
        hs = x if hs is None else hs + x
    proud = hs - oml
    housed = oml + hs
    boards_b = board(G1_BAYS["B"][0], ENV["power"]) + board(G1_BAYS["B"][1], ENV["logic"])
    m = tmesh(proud)
    v = m.vertices
    rep = {
        "status_ok": proud.status() == mf.Error.NoError,
        "housing_volume_mm3": round(proud.volume(), 1),
        "z_extent_mm": [round(float(v[:, 2].min()), 2), round(float(v[:, 2].max()), 2)],
        "esc_b_board_outside_mm3": round((boards_b - housed).volume(), 3),
        "louvre_open_area_mm2": LOUVRE[0] * LOUVRE[1] * LOUVRE[2],
        "design_bleed_area_mm2": round(4 * math.pi * 5.5**2 / 4, 1),
    }
    return proud, rep


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Canonical-styled ESC B housings (H1), 64 mm nacelle.")
    ap.add_argument(
        "--out", type=Path, required=True, help="housing STL (starboard, nacelle-local)"
    )
    ap.add_argument("--json", type=Path)
    a = ap.parse_args(argv)
    proud, rep = build()
    tmesh(proud).export(a.out)
    txt = json.dumps(rep, indent=1)
    print(txt)
    if a.json:
        a.json.write_text(txt)
    ok = rep["status_ok"] and rep["esc_b_board_outside_mm3"] < 0.05
    ok = ok and rep["z_extent_mm"][1] <= Z_LOGIC_AFT + 0.01
    print(
        f"housing {rep['housing_volume_mm3'] / 16387.064:.3f} in3, Z "
        f"{rep['z_extent_mm'][0] / 25.4:.2f}-{rep['z_extent_mm'][1] / 25.4:.2f} in; "
        + ("PASS" if ok else "FAIL")
    )
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
