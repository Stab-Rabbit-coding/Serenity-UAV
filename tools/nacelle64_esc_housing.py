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

GEOMETRY -- in the frame nacelle_pod_64mm_tandem.scad renders by default (NACELLE_SIDE = +1:
left shell, HOLLOW_*_PORT grid): duct axis +Z from the intake face, azimuth from local +X, the
CM07 at az ~270.  Bay azimuths are the optimiser's port-frame azimuths unchanged, so the housing
unions straight onto the pod render; the other pod is that render's X-mirror
(tools/prep_nacelle_64_bake.py).  (Until 2026-11-22 this tool worked in the mirrored, right-shell
frame, local az = 180 - port az; the geometry is the same, mirrored.)
  * Each ESC B bay is a hinged board pair (power 0.79 in / 20 mm + logic 0.55 in / 14 mm panels)
    whose inner face sits at the mount radius 1.46 in (37.2 mm), stack 0.24 in (6.0 mm, power bay)
    / 0.26 in (6.65 mm, logic bay) outward (tools/esc70_design_f1.json).  The housing's outer
    faces run parallel to those panels: 0.016 in (0.4 mm) running clearance, then a 0.079 in
    (2.0 mm) plate (AGENTS.md sec. 7 SLS minimum) plus the 0.018 in (0.45 mm) panel-line groove
    depth, so the plate is still 2.0 mm under a groove.  Side walls are clearance + 2.0 mm.
    NOTE: the bay design (esc70_design_f1.json cover_t 1.5) assumed a 1.5 mm cover, which is
    below the 2.0 mm rule; the housing uses 2.0 mm.
  * 45 deg side chamfers, a 30 deg fairing ramp forward, a 60 deg aft face; the logic housing is
    square-cut one wall aft of its board (Z 6.29 in / 159.8 mm), 0.018 in (0.45 mm) short of the
    F1 nozzle housing face (Z 6.31 in / 160.25 mm).
  * Panel-line grooves (0.031 in / 0.8 mm wide, 0.018 in / 0.45 mm deep) every 0.79 in (20 mm),
    kept clear of the louvre band.
  * Four louvres on the power face, 0.098 x 0.374 in (2.5 x 9.5 mm) each (0.147 in2 / 95 mm2 =
    the design's four 5.5 mm bleed holes), from the board face out through clearance and plate:
    they are the ESC cooling outlets.  The build checks each one opens to air.
  The housing is the solid outside the canonical skin; the pod/cover integration (seats, screws)
  is a separate step (WBS NAC-64-ESC-BLISTER).

BAYS: G1 (owner decision 2026-11-22, pivot Z 109.73 mm), from tools/esc80_cooptimize.py on
tools/esc70_design_f1.json with the G1 keep-outs -- the per-bay "bays" output, port frame.

Usage:  /usr/bin/python3 tools/nacelle64_esc_housing.py --out HOUSING.stl [--json REPORT]
        Exit 2, writing no STL, if the canonical OML or the housing is not a valid solid, a board
        is left outside the housed skin, the measured wall over any board is below clearance +
        2.0 mm, a louvre is blocked, or the logic housing reaches the F1 nozzle housing.
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
from typing import Any
from pathlib import Path

import manifold3d as mf
import numpy as np
import trimesh

import nacelle_64_scale as ns

REPO = Path(__file__).resolve().parents[1]
MOUNT_R = 37.2  # esc80_cooptimize.MOUNT_R (board inner face)
COVER_T = 2.0  # housing plate: AGENTS.md sec. 7 SLS default minimum wall (load case not stated)
COVER_CLR = 0.4  # running clearance, as esc80_cooptimize.overrides_64mm (SKIN_WALL = cover_t + 0.4)
SKIN_WALL = COVER_T + COVER_CLR  # 2.4 mm side/aft wall; esc70_design_f1.json assumed cover 1.5
GROOVE_PITCH, GROOVE_W, GROOVE_D = 20.0, 0.8, 0.45
TOP_WALL = SKIN_WALL + GROOVE_D  # outer face: the plate is still COVER_T under a groove
W_POWER, W_SIGNAL = 20.0, 14.0
ENV = {"power": 6.0, "logic": 6.65}  # stack + cooling lane; power bay capped at 2.0 mm parts
Z_F1_HOUSING = 160.25  # F1 nozzle housing forward face
LOUVRE = (2.5, 9.5, 4, 4.5)  # length along Z, width, count, pitch (mm)
X_BURY = 36.0  # housing base buried inside the skin (r), so the union is clean

# G1 bays (port-frame = render-frame hinge azimuth; Z = board span incl. harness reserves)
G1_BAYS: dict[str, list[dict[str, Any]]] = {
    "A": [{"az": 336.0, "z": [109.4, 157.4]}, {"az": 262.0, "z": [67.4, 105.4]}],
    "B": [{"az": 78.0, "z": [73.4, 133.7]}, {"az": 136.0, "z": [135.4, 157.4]}],
}
Z_LOGIC_AFT = G1_BAYS["B"][1]["z"][1] + SKIN_WALL  # 159.8: one full wall aft of the logic board
assert Z_LOGIC_AFT <= Z_F1_HOUSING - 0.4, "logic housing would reach the F1 nozzle housing"


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
    """Scaled canonical LEFT shell in the pod's render frame (as the 64 mm pod imports it)."""
    sh = trimesh.load_mesh(REPO / "airframe/stls/nacelles/eng_left_shell24_50mm_repaired.stl")
    sh.apply_translation([-42.72, 190.79, 0.0])  # nacelle_hollow_profile.SHELLS["PORT"], BORE_CY
    sh.vertices *= [ns.get("P64_K"), ns.get("P64_K"), ns.get("P64_A")]
    m = man(sh)
    if m.status() != mf.Error.NoError or m.volume() <= 0.0:
        raise RuntimeError(f"canonical OML is not a valid solid: {m.status()}")
    return m


def panel_angles(b: dict) -> list:
    """(width, centre azimuth) of the power and signal panels: power on the +az side of the
    hinge, as esc80_cooptimize and the pod SCAD's esc_bay_footprint() place it."""
    ap = math.degrees(math.atan2(W_POWER / 2, MOUNT_R))
    as_ = math.degrees(math.atan2(W_SIGNAL / 2, MOUNT_R))
    return [(W_POWER, b["az"] + ap), (W_SIGNAL, b["az"] - as_)]


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
    xt = MOUNT_R + env + TOP_WALL
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


def louvre_z(b: dict) -> list:
    """Louvre centre stations (power face, aft end of the power bay)."""
    return [b["z"][1] - 3.0 - i * LOUVRE[3] for i in range(LOUVRE[2])]


def groove_z(b: dict, role: str) -> list:
    """Panel-line stations: every GROOVE_PITCH, skipping the louvre group on the power face."""
    zz = np.arange(b["z"][0] + 4.0, b["z"][1] - 2.0, GROOVE_PITCH)
    lz = louvre_z(b) if role == "power" else []
    if not lz:
        return [float(z) for z in zz]
    lo, hi = min(lz) - LOUVRE[0] - GROOVE_W, max(lz) + LOUVRE[0] + GROOVE_W
    return [float(z) for z in zz if not lo <= z <= hi]


def housing(b: dict, role: str) -> mf.Manifold:
    env = ENV[role]
    aft = Z_LOGIC_AFT if role == "logic" else None
    facets = [(w, a) + facet(w, a, b["z"][0], b["z"][1], env, aft) for w, a in panel_angles(b)]
    hs = mf.Manifold.batch_hull([f[2] for f in facets])
    core = board(b, env)
    cuts = None
    for w, a, _, xt in facets:
        for z in groove_z(b, role):
            g = (
                mf.Manifold.cube([1.5, w + 2 * SKIN_WALL + 1.0, GROOVE_W])
                .translate([xt - GROOVE_D, -(w / 2 + SKIN_WALL + 0.5), z - GROOVE_W / 2])
                .rotate([0, 0, a])
            )
            cuts = g if cuts is None else cuts + g
    if role == "power":
        w, a, _, xt = facets[0]
        ln, wd = LOUVRE[0], LOUVRE[1]
        for zc in louvre_z(b):
            c = (
                mf.Manifold.cube([TOP_WALL + 0.6, wd, ln])
                .translate([xt - TOP_WALL, -wd / 2, zc - ln / 2])  # board face out through plate
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
    wall_min, blocked = measure(tmesh(housed))
    rep = {
        "status_ok": proud.status() == mf.Error.NoError,
        "housing_volume_mm3": round(proud.volume(), 1),
        "z_extent_mm": [round(float(v[:, 2].min()), 2), round(float(v[:, 2].max()), 2)],
        "esc_b_board_outside_mm3": round((boards_b - housed).volume(), 3),
        "wall_over_boards_min_mm": round(wall_min, 3),
        "louvres_blocked": blocked,
        "louvre_open_area_mm2": LOUVRE[0] * LOUVRE[1] * LOUVRE[2],
        "design_bleed_area_mm2": round(4 * math.pi * 5.5**2 / 4, 1),
    }
    return proud, rep


def _rot(p, a_deg: float):
    c, s = math.cos(math.radians(a_deg)), math.sin(math.radians(a_deg))
    return [p[0] * c - p[1] * s, p[0] * s + p[1] * c, p[2]]


def measure(housed: trimesh.Trimesh) -> tuple:
    """Independent check by ray cast on the built solid (not on the construction): the solid
    thickness outward of each board's outer face, sampled over the panel away from the louvres,
    and whether each louvre centre ray reaches air."""
    o: list = []
    d: list = []
    tag: list[int | None] = []
    for role, b in zip(("power", "logic"), G1_BAYS["B"]):
        env = ENV[role]
        lz = louvre_z(b) if role == "power" else []
        for k, (w, a) in enumerate(panel_angles(b)):
            n = _rot([1.0, 0.0, 0.0], a)
            zs = np.arange(b["z"][0] + 0.5, b["z"][1], 1.5)
            grooves = groove_z(b, role)  # sample under each panel line too
            for z in np.concatenate([zs, grooves]):
                for y in np.linspace(-w / 2 + 0.5, w / 2 - 0.5, 7):
                    in_louvre = k == 0 and any(
                        abs(z - zc) <= LOUVRE[0] / 2 + 0.3 and abs(y) <= LOUVRE[1] / 2 + 0.3
                        for zc in lz
                    )
                    if not in_louvre:
                        o.append(_rot([MOUNT_R + env - 0.05, y, z], a))
                        d.append(n)
                        tag.append(None)
            if k == 0:
                for i, zc in enumerate(lz):
                    o.append(_rot([MOUNT_R + env + 0.1, 0.0, zc], a))
                    d.append(n)
                    tag.append(i)
    loc, idx, _ = housed.ray.intersects_location(np.array(o), np.array(d), multiple_hits=True)
    first = np.full(len(o), np.inf)
    dist = ((loc - np.array(o)[idx]) * np.array(d)[idx]).sum(1)
    np.fmin.at(first, idx, dist)
    walls = [first[i] - 0.05 for i, t in enumerate(tag) if t is None]
    blocked = [t for i, t in enumerate(tag) if t is not None and np.isfinite(first[i])]
    return float(min(walls)), blocked


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Canonical-styled ESC B housings (H1), 64 mm nacelle.",
        epilog="example: /usr/bin/python3 tools/nacelle64_esc_housing.py "
        "--out /tmp/h1_housing.stl --json /tmp/h1_housing.json",
    )
    ap.add_argument(
        "--out", type=Path, required=True, help="housing STL (starboard, nacelle-local)"
    )
    ap.add_argument("--json", type=Path)
    a = ap.parse_args(argv)
    proud, rep = build()
    txt = json.dumps(rep, indent=1)
    print(txt)
    if a.json:
        a.json.write_text(txt)
    ok = rep["status_ok"] and rep["esc_b_board_outside_mm3"] < 0.05
    ok = ok and rep["z_extent_mm"][1] <= Z_LOGIC_AFT + 0.01
    ok = ok and rep["wall_over_boards_min_mm"] >= SKIN_WALL - 0.05 and not rep["louvres_blocked"]
    if ok:
        tmesh(proud).export(a.out)
    print(
        f"housing {rep['housing_volume_mm3'] / 16387.064:.3f} in3, Z "
        f"{rep['z_extent_mm'][0] / 25.4:.2f}-{rep['z_extent_mm'][1] / 25.4:.2f} in; "
        + ("PASS" if ok else "FAIL (no STL written)")
    )
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
