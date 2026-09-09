#!/usr/bin/env python3
"""
nacelle_housing_profile.py — station sampler for the nozzle housing's outer
skin, so the housing's outer wall can be ovalised to track the canonical
Serenity nacelle mould line instead of a uniform two-point cylindrical taper.

WHY THIS EXISTS
---------------
`nacelle_nozzle_iris.scad`'s `nozzle_throat_and_housing()` module built its
outer shell as `cylinder(r=HOUSING_OUTER_R)` blended with `cylinder(r1, r2)`
to `HOUSING_AFT_R` — i.e. two radii, rotationally symmetric.  The canonical
shell is NOT rotationally symmetric at the nozzle station (it is an ovoid
cowl, not a body of revolution), so a uniform circle sized to clear the
widest direction of the cowl is, by construction, proud of the mould line
everywhere the cowl pinches in — measured by this plan at 3.2 mm growing to
3.9 mm proud aft.  This tool ray-casts the same canonical shell meshes
`tools/nacelle_hollow_profile.py` already uses, over the housing's own axial
span, and emits a (Z, azimuth) radius grid so the housing can be LOFTED to
the true cross-section (via `nacelle_shell_grid.scad`'s `grid_solid()`)
instead of assumed circular.

COORDINATE FRAME — reusing, not re-deriving, `nacelle_hollow_profile.py`
-------------------------------------------------------------------------
`nacelle_nozzle_iris.scad` is modelled in the SAME nacelle-local print frame
as `nacelle_pod_50mm_tandem.scad` (duct axis = local +Z), just Z-shifted: the
assembly script places the iris STL at nacelle-local Z = NOZZLE_RING_Z
(confirmed by reading `nacelle_pod_50mm_tandem.scad`'s `nozzle_iris_stl()`
placement in `serenity_assembly.py` — `nacelle_rows(side, _IDENTITY3,
(0, 0, NOZZLE_RING_Z))`, identity rotation, so no additional transform is
needed beyond that one Z offset). `nacelle_pod_50mm_tandem.scad` imports the
canonical shell STL directly into that SAME nacelle-local frame with a plain
translate — no rotation:

    translate([-BORE_CX_L, BORE_CY, 0]) import("eng_left_shell24_...stl")

which is exactly what `nacelle_hollow_profile.py`'s `skin_grid()` already
does.  So this tool reuses that ray-cast + translate approach unmodified
(mirroring its structure) rather than routing through the assembly's
hull-frame R_BAKE/T_BAKE rotation — that rotation matters for placing the
nacelle sub-assembly in the WORLD, but the housing and the canonical shell
already share one local frame before that placement is ever applied, so
composing R_BAKE would rotate both operands identically and cancel out.

TWO NACELLES, ONE HOUSING PART
-------------------------------
`nacelle_nozzle_iris.scad` has no per-side (`NACELLE_SIDE`) parameter today —
Makefile/`serenity_assembly.py` build ONE housing STL and place it,
unmirrored, at both the port and starboard nacelle stations (see
`nozzle_iris_stl()` / `nacelle_rows()` call sites). Adding a side parameter
would touch the Makefile and the assembly script, which this plan unit's file
list does not include. Given one physical part must serve both nacelles, and
`eng_left_shell24_...` / `eng_right_shell24_...` are two independently
measured (not programmatically mirrored) meshes, the SAFE choice is to take
the ELEMENTWISE MINIMUM of the two sides' canonical radii at every station —
the single housing then clears BOTH cowls, not just the one it happened to be
sampled from. Both sides' raw grids are still emitted for the record.

Usage:
    /usr/bin/python3 tools/nacelle_housing_profile.py            # trade table
    /usr/bin/python3 tools/nacelle_housing_profile.py --emit     # write the .scad
    /usr/bin/python3 tools/nacelle_housing_profile.py --check    # proud-point gate

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CEH
Analysis and tool by Claude (Claude Sonnet 5, Anthropic) under the author's
direction, per AGENTS.md S3 "Attribution and Licensing".
License: CC BY 4.0 - creativecommons.org/licenses/by/4.0
"""

from __future__ import annotations

import argparse
import ast
import operator
import re
import sys
from pathlib import Path

import numpy as np

try:
    import trimesh
except ImportError:  # pragma: no cover - environment guard
    print("Missing dependency 'trimesh'. Install requirements-dev.txt first.")
    raise

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "airframe/openscad/nacelles/nacelle_housing_profile.scad"
IRIS_SCAD = REPO / "airframe/openscad/nacelles/nacelle_nozzle_iris.scad"
POD_SCAD = REPO / "airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad"

# Reuse tools/nacelle_hollow_profile.py's SHELLS/BORE_CY exactly — same repo
# directory, so this import works whether run as a script or as a module.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nacelle_hollow_profile as nhp  # noqa: E402  (path insert must precede)

SHELLS = nhp.SHELLS          # {"PORT": (stl name, bore-centring X), "STBD": (...)}
BORE_CY = nhp.BORE_CY        # [mm] shared bore Y-centring offset

# -----------------------------------------------------------------------------
# Constants mirrored from source SCAD, NOT re-derived — provenance below.
# -----------------------------------------------------------------------------

# nacelle_pod_50mm_tandem.scad:350 — nozzle ring pocket start station, which is
# also where serenity_assembly.py's nozzle_iris_stl() placement puts iris.scad
# local Z = 0 (see nacelle_rows(side, _IDENTITY3, (0, 0, NOZZLE_RING_Z)) at
# serenity_assembly.py ~line 854).
NOZZLE_RING_Z = 166.25

# nacelle_nozzle_iris.scad:489 — full axial height of the cam-ring region;
# the outer shell is a plain cylinder over this span before it starts tapering.
RING_H = 8.0

# nacelle_nozzle_iris.scad:317 — throat tube axial length; also the housing's
# aft face and the hinge-boss station HINGE_Z (iris.scad:335, HINGE_Z=THROAT_LEN).
THROAT_LEN = 15.0
HINGE_Z = THROAT_LEN

# nacelle_nozzle_iris.scad:315-316 — R6 bore invariant, UNTOUCHED by this unit.
# Read here only to compute the hinge geometry below (mirrors THROAT_OUTER_R).
BORE_R = 25.0                       # iris.scad:307
THROAT_WALL = 2.5                   # iris.scad:314
THROAT_OUTER_R = BORE_R + THROAT_WALL  # iris.scad:316 = 27.5

# nacelle_nozzle_iris.scad:321 — tangential hinge circle radius = THROAT_OUTER_R.
R_HINGE = THROAT_OUTER_R

# nacelle_nozzle_iris.scad:428 — flap/hinge-boss count.
N_FLAPS = 8

# nacelle_nozzle_iris.scad:431-432 — hinge pin OD and its clearance bore.
HINGE_PIN_D = 3.0
HINGE_BORE_D = 3.2

# nacelle_nozzle_iris.scad:600-601 — hinge-boss envelope geometry (verbatim
# formula from nozzle_throat_and_housing()): boss OD, boss centre offset, and
# therefore boss outer-edge radius from the duct axis.
HINGE_BOSS_OD = HINGE_BORE_D + 5.0                      # = 8.2
HINGE_BOSS_X_CEN = R_HINGE + HINGE_BOSS_OD / 2 - 1.0    # = 30.6
HINGE_BOSS_MAX_R = HINGE_BOSS_X_CEN + HINGE_BOSS_OD / 2  # = 34.7 (Ø69.4, iris.scad:548)

# Current (pre-ovalisation) housing constants — read live from the SCAD source
# by `read_current_housing()` below rather than hardcoded here, so --check
# reflects whatever nacelle_nozzle_iris.scad actually says at run time.

# -----------------------------------------------------------------------------
# Sampling grid.
# -----------------------------------------------------------------------------
#: Axial stations, in IRIS-LOCAL Z (0 = ring/lip start = nacelle-local
#: NOZZLE_RING_Z, THROAT_LEN = aft face / hinge station).  1 mm steps: fine
#: enough to catch the taper's own RING_H break and resolve the hinge-boss
#: station exactly (both are integer mm values already).
DZ = 1.0
Z_LOCAL = np.arange(0.0, THROAT_LEN + DZ / 2, DZ)

#: Circumferential samples.  48, matching nacelle_hollow_profile.py's N_AZ —
#: and, not incidentally, divisible by N_FLAPS=8, so the hinge-boss azimuths
#: (0, 45, ..., 315 deg) land EXACTLY on grid samples (indices 0, 6, 12, ...),
#: rather than needing a separate off-grid ray-cast for the boss check.
N_AZ = 48
AZ = np.arange(N_AZ) * 360.0 / N_AZ
BOSS_AZ_IDX = [i * (N_AZ // N_FLAPS) for i in range(N_FLAPS)]

#: Margin the housing is held INBOARD of the measured canonical radius at
#: every station — NOT flush.  0.5 mm matches this same file's own existing
#: convention for the unison-ring bore clearance ("Ø66.2 + 0.5 mm/side clr",
#: nacelle_nozzle_iris.scad:510) — a normal FDM running/skin clearance, not an
#: arbitrarily chosen number.
MARGIN = 0.5

#: Conservative floor: never let the ovalised wall pinch thinner than this
#: past the housing's own internal bore, in the region where that bore exists
#: (Z <= RING_CAVITY_Z_HI = RING_H + 1.0, nacelle_nozzle_iris.scad:624).  This
#: does NOT override the margin above — if the canonical shell itself does not
#: leave room for both the margin AND this floor, --check reports a distinct
#: "thin wall" finding rather than silently pushing the housing proud to make
#: room for it.
HOUSING_INNER_R = 33.6              # iris.scad:510, R6-adjacent, unchanged
MIN_WALL = 1.0
RING_CAVITY_Z_HI = RING_H + 1.0      # iris.scad:624


def skin_grid(side: str):
    """Ray-cast the canonical shell's outer radius over the housing's span.

    Identical method to `nacelle_hollow_profile.py.skin_grid()` (ray cast
    inward from outside the bounding box, 3x3 sub-sample per cell, take the
    MINIMUM over the sub-sample) but parameterised to the housing's own,
    much shorter, axial span rather than the whole pod cavity.  Conservative
    by the same construction: the housing must never sit proud, so the
    tightest sub-sample point in a cell is the one that governs.
    """
    name, cx = SHELLS[side]
    mesh = trimesh.load_mesh(REPO / "airframe/stls/nacelles" / name, force="mesh")
    mesh.apply_translation([-cx, BORE_CY, 0.0])

    zs_nacelle = NOZZLE_RING_Z + Z_LOCAL
    sub_dz = [-DZ / 3, 0.0, DZ / 3]
    sub_da = [-360.0 / N_AZ / 3, 0.0, 360.0 / N_AZ / 3]

    origins, dirs = [], []
    for z in zs_nacelle:
        for a in AZ:
            for ddz in sub_dz:
                for dda in sub_da:
                    t = np.radians(a + dda)
                    origins.append([200.0 * np.cos(t), 200.0 * np.sin(t), z + ddz])
                    dirs.append([-np.cos(t), -np.sin(t), 0.0])
    origins = np.asarray(origins)
    dirs = np.asarray(dirs)
    loc, ray_idx, _ = mesh.ray.intersects_location(origins, dirs, multiple_hits=True)

    outer = np.zeros(len(origins))
    radii = np.hypot(loc[:, 0], loc[:, 1])
    np.maximum.at(outer, ray_idx, radii)
    if (outer == 0).any():
        raise ValueError(f"{side}: {(outer == 0).sum()} rays missed the shell")
    outer = outer.reshape(len(Z_LOCAL), N_AZ, 9).min(axis=2)
    return outer


def canonical_grids():
    """Return {side: (n_z, n_az) canonical outer-skin radius grid}."""
    return {side: skin_grid(side) for side in SHELLS}


def combined_profile(grids):
    """Elementwise MIN across sides minus the margin -- see module docstring
    ('TWO NACELLES, ONE HOUSING PART') for why min(), not port-only."""
    port, stbd = grids["PORT"], grids["STBD"]
    canon_min = np.minimum(port, stbd)
    return canon_min, canon_min - MARGIN


_SAFE_BINOPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
}


def _safe_eval_scad_expr(expr: str, names: dict) -> float:
    """Evaluate a tiny arithmetic SCAD constant expression (numbers, `+ - * /`,
    and references to already-parsed names) WITHOUT calling eval() on
    untrusted/arbitrary source -- walks a restricted AST instead, so a stray
    or malicious expression in the .scad source cannot execute code."""
    node = ast.parse(expr, mode="eval").body

    def _walk(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return float(n.value)
        if isinstance(n, ast.Name):
            if n.id not in names:
                raise NameError(n.id)
            return names[n.id]
        if isinstance(n, ast.BinOp) and type(n.op) in _SAFE_BINOPS:
            return _SAFE_BINOPS[type(n.op)](_walk(n.left), _walk(n.right))
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
            return -_walk(n.operand)
        raise ValueError(f"unsupported expression node in SCAD constant: {expr!r}")

    return _walk(node)


def read_current_housing():
    """Parse HOUSING_OUTER_R / HOUSING_AFT_R / THROAT_*_R / BORE_R / THROAT_WALL
    live from the checked-out nacelle_nozzle_iris.scad, so --check reflects the
    file as it actually stands (pre- or post-edit) rather than a hardcoded
    snapshot.  THROAT_INNER_R / THROAT_OUTER_R are declared as SCAD
    expressions referencing earlier constants (`= BORE_R;`, `= BORE_R +
    THROAT_WALL;`), not numeric literals, so this parses in declaration order
    and evaluates each right-hand side against the names collected so far --
    still a plain read, not a re-derivation of the values."""
    src = IRIS_SCAD.read_text(encoding="utf-8")
    names = ("BORE_R", "THROAT_WALL", "THROAT_INNER_R", "THROAT_OUTER_R",
             "HOUSING_INNER_R", "HOUSING_OUTER_R", "HOUSING_AFT_R")
    out: dict[str, float] = {}
    for name in names:
        m = re.search(rf"^{name}\s*=\s*([^;]+);", src, re.MULTILINE)
        if not m:
            raise ValueError(f"could not find {name} in {IRIS_SCAD}")
        expr = m.group(1).strip()
        try:
            out[name] = _safe_eval_scad_expr(expr, out)
        except NameError as exc:
            raise ValueError(f"{name} = '{expr}' references an unparsed "
                             f"name in {IRIS_SCAD}") from exc
    return out


def old_taper_radius(z_local: float, current: dict) -> float:
    """Reproduce the PRE-ovalisation two-point taper's radius at z_local, for
    the 'before' side of the before/after comparison in --check output."""
    if z_local <= RING_H:
        return current["HOUSING_OUTER_R"]
    t = (z_local - RING_H) / (THROAT_LEN - RING_H)
    return current["HOUSING_OUTER_R"] + t * (current["HOUSING_AFT_R"] - current["HOUSING_OUTER_R"])


def emit(canon_min, profile) -> str:
    """Render the generated OpenSCAD source, mirroring
    nacelle_hollow_profile.scad's shape (Z array + per-side/az radius rows)."""
    lines = [
        "// =============================================================================",
        "// nacelle_housing_profile.scad — GENERATED FILE, DO NOT EDIT BY HAND",
        "// =============================================================================",
        "//",
        "// Regenerate with:  /usr/bin/python3 tools/nacelle_housing_profile.py --emit",
        "//",
        "// Station->radius profile for the nozzle housing's outer wall (Rev T3->T4",
        "// ovalisation), measured by ray-casting BOTH canonical nacelle shells over",
        "// the housing's own axial span (iris-local Z = 0 (ring/lip start) .. "
        f"{THROAT_LEN:.1f} (aft face / hinge station)) and taking the elementwise",
        "// MINIMUM across the two sides so one housing part clears both cowls, then",
        f"// holding a {MARGIN:.1f} mm margin inboard of that -- not flush.  See the",
        "// tool's header for the full derivation (coordinate frame, why min-of-sides).",
        "//",
        "// HOUSING_R is the profile nacelle_nozzle_iris.scad actually builds the outer",
        "// wall from (margin already applied). HOUSING_R_CANON is the raw measured",
        "// canonical minimum, kept for --check and for engineering record.",
        "//",
        "// Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CEH",
        "// Generated by Claude (Claude Sonnet 5, Anthropic) under the author's",
        "// direction, per AGENTS.md S3 'Attribution and Licensing'.",
        "// License: CC BY 4.0 - creativecommons.org/licenses/by/4.0",
        "// =============================================================================",
        "",
        f"HOUSING_N_AZ = {N_AZ};",
        f"HOUSING_MARGIN = {MARGIN:.2f};",
        "HOUSING_Z = [" + ", ".join(f"{z:.2f}" for z in Z_LOCAL) + "];",
        "",
        "HOUSING_R_CANON = [",
    ]
    for row in canon_min:
        lines.append("  [" + ",".join(f"{v:.3f}" for v in row) + "],")
    lines.append("];")
    lines.append("")
    lines.append("HOUSING_R = [")
    for row in profile:
        lines.append("  [" + ",".join(f"{v:.3f}" for v in row) + "],")
    lines.append("];")
    lines.append("")
    return "\n".join(lines)


def run_check(canon_min, profile) -> int:
    """--check: report proud stations (outer wall, then hinge bosses) and the
    R6 bore-invariant diff.  Returns 0 if every check passes, 1 otherwise."""
    violations = 0
    worst_margin = None  # (margin_actual, z, az_idx) — most negative = worst

    # 1. Outer wall grid vs canonical, at every sampled station/azimuth.
    n_stations = len(Z_LOCAL)
    for k in range(n_stations):
        for i in range(N_AZ):
            actual_margin = canon_min[k, i] - profile[k, i]
            if worst_margin is None or actual_margin < worst_margin[0]:
                worst_margin = (actual_margin, Z_LOCAL[k], AZ[i])
            if profile[k, i] > canon_min[k, i] + 1e-9:
                violations += 1
                print(f"  PROUD (outer wall): z={Z_LOCAL[k]:.1f} az={AZ[i]:.1f} "
                      f"profile_r={profile[k, i]:.2f} canon_r={canon_min[k, i]:.2f}")

    # 2. Thin-wall advisory (not a proud violation, but flagged distinctly).
    thin_wall_count = 0
    for k, z in enumerate(Z_LOCAL):
        if z > RING_CAVITY_Z_HI:
            continue
        floor = HOUSING_INNER_R + MIN_WALL
        row_min = profile[k].min()
        if row_min < floor:
            thin_wall_count += 1
            print(f"  THIN WALL (advisory, not proud): z={z:.1f} "
                  f"min_profile_r={row_min:.2f} < floor={floor:.2f}")

    # 3. Hinge-boss envelope vs canonical, at HINGE_Z / boss azimuths only.
    #    HINGE_Z (iris-local, = THROAT_LEN) IS the last sampled station, so no
    #    extra ray-cast is needed -- index it directly out of canon_min.
    hinge_k = len(Z_LOCAL) - 1
    assert abs(Z_LOCAL[hinge_k] - HINGE_Z) < 1e-9, "HINGE_Z must be the last sampled station"
    boss_violations = 0
    boss_worst_margin = None
    for idx in BOSS_AZ_IDX:
        canon_r = canon_min[hinge_k, idx]
        actual_margin = canon_r - HINGE_BOSS_MAX_R
        if boss_worst_margin is None or actual_margin < boss_worst_margin[0]:
            boss_worst_margin = (actual_margin, AZ[idx])
        if HINGE_BOSS_MAX_R > canon_r + 1e-9:
            boss_violations += 1
            violations += 1
            print(f"  PROUD (hinge boss): az={AZ[idx]:.1f} "
                  f"boss_r={HINGE_BOSS_MAX_R:.2f} canon_r={canon_r:.2f}")

    # 4. R6 bore invariant -- read-only report here; the byte-diff itself is
    #    done by the caller (git diff) since this tool only ever reads the file.
    current = read_current_housing()

    print(f"\nStations checked: {n_stations} axial x {N_AZ} azimuthal "
          f"({n_stations * N_AZ} outer-wall samples) + {N_FLAPS} hinge-boss samples")
    print(f"Outer-wall proud violations: {violations - boss_violations}")
    print(f"Hinge-boss proud violations: {boss_violations}")
    print(f"Thin-wall advisories (z <= {RING_CAVITY_Z_HI:.1f}, not proud): {thin_wall_count}")
    if worst_margin is not None:
        print(f"Worst-case outer-wall margin (canonical - profile): "
              f"{worst_margin[0]:.3f} mm at z={worst_margin[1]:.1f}, az={worst_margin[2]:.1f}")
    if boss_worst_margin is not None:
        print(f"Worst-case hinge-boss margin (canonical - boss_r): "
              f"{boss_worst_margin[0]:.3f} mm at az={boss_worst_margin[1]:.1f}")
    print(f"THROAT_INNER_R = {current['THROAT_INNER_R']:.4f}  "
          f"THROAT_OUTER_R = {current['THROAT_OUTER_R']:.4f}  (R6 bore -- unchanged by this tool)")

    if violations == 0:
        print("\nPASS: 0 stations proud of the canonical shell.")
        return 0
    print(f"\nFAIL: {violations} proud stations found.")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--emit", action="store_true",
                    help="write airframe/openscad/nacelles/nacelle_housing_profile.scad")
    ap.add_argument("--check", action="store_true",
                    help="report proud-station violations; exit 0 iff none")
    args = ap.parse_args()

    grids = canonical_grids()
    canon_min, profile = combined_profile(grids)

    if args.check:
        return run_check(canon_min, profile)

    current = read_current_housing()
    print("Nozzle housing ovalisation -- canonical mould-line trade table")
    print(f"  axial span (iris-local Z): 0.0 .. {THROAT_LEN:.1f} mm "
          f"(nacelle-local {NOZZLE_RING_Z:.2f} .. {NOZZLE_RING_Z + THROAT_LEN:.2f} mm)")
    print(f"  grid: {len(Z_LOCAL)} stations x {N_AZ} azimuths, margin {MARGIN:.1f} mm\n")
    print(f"  {'z(local)':>9}{'old_r':>9}{'canon_min':>11}{'new_r':>9}{'delta':>9}")
    for k, z in enumerate(Z_LOCAL):
        old_r = old_taper_radius(float(z), current)
        canon_r = canon_min[k].min()
        new_r = profile[k].min()
        print(f"  {z:9.1f}{old_r:9.2f}{canon_r:11.2f}{new_r:9.2f}{old_r - new_r:9.2f}")

    print(f"\n  hinge-boss envelope radius: {HINGE_BOSS_MAX_R:.2f} mm "
          f"(Ø{2 * HINGE_BOSS_MAX_R:.1f} mm) at z={HINGE_Z:.1f}")
    for idx in BOSS_AZ_IDX:
        print(f"    az={AZ[idx]:6.1f}  canon_r={canon_min[-1, idx]:.2f}  "
              f"margin={canon_min[-1, idx] - HINGE_BOSS_MAX_R:.2f}")

    if args.emit:
        OUT.write_text(emit(canon_min, profile), encoding="utf-8")
        print(f"\n  wrote {OUT.relative_to(REPO)} ({OUT.stat().st_size / 1024:.0f} KB)")
    else:
        print("\n  (dry run -- pass --emit to write the .scad, --check to gate)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
