#!/usr/bin/python3
"""Per-feature, in-context clash census of the 3.0 in landing-gear bays (BHD-02).

The cargo bulkhead gate (tools/cargo_bulkhead_context.py) sees the gear as ONE
merged mesh, so it can say *that* the gear hits the wing, root flange or CF
spar but not *which feature* does -- and the fix is different for each: a
liner wall can be trimmed, a wire seat cannot (it is the energy absorber), a
bolt can move, and the swinging thigh can only be cleared by relieving the
OTHER part.  This tool answers the per-feature question.

Method (docs/solutions/design-patterns/
build-every-joint-in-context-through-its-full-motion.md, rules 1-4):

1. Each bay feature is rendered ALONE, in the leg-local frame, from the real
   SCAD modules in airframe/openscad/fuselage/canonical_leg_r6_3_0in.scad
   (PART="none" library mode; feature modules split out of bay() on
   2026-10-10 with the printed part proven unchanged), once per bay station
   because the fore and aft back-face datums differ (BAY_STANDOFF).
2. It is posed at each of the four CORNERS exactly as hull_legs() poses it --
   translate(hip) * rotZ(azimuth) * mirrorY(hand).  Since 2026-10-10 the
   starboard bays are the port bays MIRRORED (owner decision, BHD-02); before
   that they were the same part ROTATED, which flips a one-sided feature to
   the wrong side.
3. The moving leg is swept 0..SWEEP_DEG about the hip pin (leg-local Y) and
   unioned, so the thigh is checked through its whole stroke plus margin
   (FLEX_DEG 22 + 4 = 26 deg, the margin tools/landing_gear_cowl_clearance.py
   already uses).
4. Every posed feature is intersected with every bulkhead-context solid
   (real wing and flange meshes, CF spar, drive shaft, harness exits, tilt
   drive) and the overlap volume is reported.  Function checks ride along:
   bay body count, and the thigh sweep against its own bay.

Rendering is cached on the SCAD file's SHA-256, so a geometry change
re-renders and an unchanged file does not (each bay feature is a CGAL render,
~30 s).

Run:  /usr/bin/python3 tools/landing_gear_bay_function.py [--json OUT] [--export DIR]
      [--scad PATH]   (render an edited copy of the gear SCAD, e.g. a relief trial)
Exit 2 if any non-expected overlap exceeds CLASH_MM3.

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, per AGENTS.md AI attribution.
License: MIT (SPDX-License-Identifier: MIT) -- see tools/LICENSE.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import subprocess  # nosec B404 -- fixed argv to the local openscad binary
import sys
import tempfile

import numpy as np
import trimesh
from manifold3d import Manifold, OpType

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cargo_bulkhead_context as cbc  # noqa: E402  (context solids, man/tri helpers)

REPO = os.path.abspath(os.path.join(HERE, ".."))
SCAD = os.path.join(REPO, "airframe", "openscad", "fuselage", "canonical_leg_r6_3_0in.scad")
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "serenity", "lg_bay_function")

# Mirrors canonical_leg_r6_3_0in.scad CORNERS -- [hip x, y, z, azimuth deg, hand].
# Read back from the SCAD at run time (parse_corners) so the two cannot drift;
# the literal here is only the fallback documentation.
CORNER_NAMES = ("fore-port", "fore-stbd", "aft-port", "aft-stbd")
STATION = {"fore-port": "fore", "fore-stbd": "fore", "aft-port": "aft", "aft-stbd": "aft"}
SIDE = {"fore-port": "port", "fore-stbd": "stbd", "aft-port": "port", "aft-stbd": "stbd"}

FLEX_DEG = 22.0            # SCAD FLEX_DEG (full ductile stroke)
SWEEP_DEG = 26.0           # + 4 deg margin, as landing_gear_cowl_clearance.py
SWEEP_STEP = 2.0          # deg; 26/2 + 1 = 14 poses, chord error < 0.1 mm at r 80
CLASH_MM3 = 1.0            # same floor as the bulkhead gate

# Bay features, each a SCAD expression evaluated in the leg-local frame.
# "functional" features may never be cut by a relief (BHD-02 owner rule:
# reshape the gear blocks but keep the gear working).
FEATURES = {
    "cowl (flange+liner)": ("bay_cowl();", False),
    "boss carrier": ("boss_carrier();", False),
    "clevis gussets": ("clevis_gussets();", False),
    "clevis ears": ("bay_clevis_ears();", True),
    "wire bosses": ("bay_wire_bosses();", False),
    "wire seats": ("bay_wire_seats();", True),
    "retention pads": ("for (i = [0:3]) retention_pad((i - 1.5) * WIRE_STAGGER, "
                       "abs((i - 1.5) * WIRE_STAGGER) > 3, false);", False),
    # M3 clearance bore grown to a O8.4 keep-out: washer face / nut / driver.
    "M3 bolt keep-out": ("bay_bolts(BAY_M3_D + 2 * 2.5);", True),
    "bay (printed part)": ("bay();", False),
    # pieces the conforming-bay generator (tools/generate_lg_bays.py) builds from
    "liner": ("bay_cowl(flange = false);", False),
    "flange outline": ("bay_flange_outline(-40, 40);", False),
    "liner outline": ("bay_liner_outline(-40, 40);", False),
    "body": ("bay_body();", False),
    "cuts": ("bay_cuts();", False),
    "leg (thigh+shin+foot)": ("leg_moving(0);", True),
    # the 4 energy-absorber wires at rest (H_NOM) and the extension-stop
    # cross-pin: procured parts, modelled as solids (joint-in-context rule 2)
    "wires": ("for (i = [0:3]) posed_wire(i, H_NOM);", True),
    # full-stroke bow on the rest chord: a conservative envelope of the bow
    # sweep (the real chord is 2.3 mm shorter there, which bows LESS sideways)
    "wires deformed": ("for (i = [0:3]) posed_wire(i, w_spring(i) ? H_DEF_SPRING : H_DEF_DUCT);",
                       True),
    "stop pin": ("ycyl(STOP_PIN_R * azv(STOP_PIN_AZ), LUG_W + 2 * (EAR_CLR + EAR_T), "
                 "PIN_D - 0.2);", True),
}

# Generator inputs, not features to census on their own.
BUILD_ONLY = ("liner", "body", "cuts", "flange outline", "liner outline")

# Every function check below must be < CLASH_MM3 for a PASS.  One list, used by
# both the printout and the exit code, so a check can never be computed and
# then silently left out of the gate (security review 2026-10-11: the wire /
# stop-pin checks were printed but did not fail the run).
FUNCTION_LIMITS = ("leg_sweep_vs_own_bay_mm3", "wires_x_stop_pin_mm3", "wires_x_bay_mm3",
                   "wires_x_leg_rest_mm3", "stop_pin_x_leg_sweep_mm3", "wire_x_wire_mm3")


def function_ok(f: dict) -> bool:
    """True when the bay is one body and every interference check is clear."""
    return f["bay_bodies"] == 1 and all(f[k] < CLASH_MM3 for k in FUNCTION_LIMITS)

# Context solids the gear is EXPECTED to touch, with why (unordered substrings).
EXPECTED = (
    ("bay (printed part)", "shell", "bay seats in the merged hull pocket"),
    ("M3 bolt keep-out", "shell", "M3 through-bolts pass through the hull wall and collar"),
)


def sha(path: str) -> str:
    """SHA-256 of a file (the render cache key)."""
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]


def parse_corners(path: str) -> dict[str, list[float]]:
    """Read CORNERS out of the SCAD so placement cannot drift from hull_legs()."""
    txt = open(path, encoding="utf-8").read()
    blk = txt[txt.index("CORNERS = ["):]
    blk = blk[:blk.index("\n];")]          # the closing line, not a "];" in a comment
    rows = []
    for line in blk.splitlines()[1:]:
        line = line.split("//")[0].strip()
        if line.startswith("["):
            rows.append([float(v) for v in line.strip("[],").split(",")])
    if len(rows) != 4 or any(len(r) not in (4, 5) for r in rows):
        raise RuntimeError(f"expected 4 CORNERS rows of 4-5 values, parsed {rows}")
    return dict(zip(CORNER_NAMES, rows, strict=True))


def render(scad: str, station: str, name: str, expr: str,
           defines: tuple[str, ...] = ()) -> str:
    """Render one feature (leg-local frame) to a cached STL; return its path.

    `defines` are extra OpenSCAD -D NAME=VALUE overrides (a design trial,
    e.g. a rotated wire cluster); they are part of the cache key.
    """
    tag = hashlib.sha256("\0".join(defines).encode()).hexdigest()[:8] if defines else "base"
    key = os.path.join(CACHE, sha(scad), tag)
    os.makedirs(key, exist_ok=True)
    safe = "".join(c if c.isalnum() else "_" for c in name)
    out = os.path.join(key, f"{station}_{safe}.stl")
    if os.path.exists(out):
        return out
    with tempfile.NamedTemporaryFile("w", suffix=".scad", delete=False,
                                     dir=key, encoding="utf-8") as fh:
        fh.write(f"include <{scad}>\n{expr}\n")
        wrap = fh.name
    try:
        subprocess.run(["openscad", "-o", out + ".tmp.stl",  # noqa: S603, S607 # nosec
                        "-D", 'PART="none"', "-D", f'BAY_STATION="{station}"',
                        *[a for d in defines for a in ("-D", d)], wrap],
                       check=True, capture_output=True, timeout=900)
        os.replace(out + ".tmp.stl", out)
    finally:
        os.unlink(wrap)
    return out


GENERATED = os.path.join(REPO, "airframe", "stls", "fuselage", "landing-gear",
                         "lg_r6_3_0in_bay_{}.stl")


def corner_keepout(cn: str) -> Manifold:
    """The corner's O8.4 M3 keep-outs at its generated bolt pattern."""
    sys.path.insert(0, os.path.join(REPO, "airframe", "blender-scripts"))
    import generate_lg_bays as glb  # noqa: PLC0415
    import merge_cargo_interior as mci  # noqa: PLC0415
    org, ex, ey, ez = mci.lg_bay_frame(cn)
    pts = mci.LG_CORNER_BOLTS.get(cn, mci.lg_nominal_bolts())
    out = None
    for u, v in pts:
        k = glb.bolt_cyl(org, ex, ey, ez, u, v, glb.BOLT_KEEP_D)
        out = k if out is None else out + k
    return out


def corner_tf(c: list[float]) -> np.ndarray:
    """Leg-local -> hull: translate(hip) * rotZ(az) * mirrorY(hand), as hull_legs().

    hand (5th column, owner 2026-10-10) is +1 for a port part and -1 for a
    starboard part, which is the port part MIRRORED in leg-local y.  A 4-column
    row (older SCAD) is treated as hand +1, i.e. the old rotated placement.
    The matrix then has determinant -1; trimesh re-winds faces itself.
    """
    t = trimesh.transformations.translation_matrix(c[:3])
    r = trimesh.transformations.rotation_matrix(np.radians(c[3]), [0, 0, 1])
    hand = c[4] if len(c) > 4 else 1.0
    return t @ r @ np.diag([1.0, 1.0 if hand > 0 else -1.0, 1.0, 1.0])


def posed(path: str, tf: np.ndarray) -> Manifold:
    """Load a leg-local STL and place it in the hull frame."""
    m = trimesh.load(path, force="mesh")
    return cbc.man(m.apply_transform(tf))


def swept_leg(path: str, tf: np.ndarray, a1: float = SWEEP_DEG) -> Manifold:
    """Union of the leg rotated 0..a1 deg about the hip pin (SCAD rotate([0,-flex,0]))."""
    base = trimesh.load(path, force="mesh")
    poses = []
    for a in np.arange(0.0, a1 + 1e-9, SWEEP_STEP):
        r = trimesh.transformations.rotation_matrix(np.radians(-a), [0, 1, 0])
        poses.append(cbc.man(base.copy().apply_transform(tf @ r)))
    return Manifold.batch_boolean(poses, OpType.Add)


def wire_pairs(path: str, tf: np.ndarray) -> float:
    """Sum of pairwise overlaps between the 4 posed wires (BHD-02k: the Rev R6
    3.5 mm pitch put them inside each other)."""
    parts = sorted(cbc.man(trimesh.load(path, force="mesh").apply_transform(tf)).decompose(),
                   key=lambda m: -m.volume())
    tot = 0.0
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            tot += (parts[i] ^ parts[j]).volume()
    if len(parts) < 4:      # merged on render = they already overlap
        tot += 1e3
    return tot


def targets(P: dict) -> dict[str, Manifold]:
    """Bulkhead-context solids a gear feature could hit (not the gear itself)."""
    skip = ("gear legs", "door ", "hoist", "winch", "payload", "battery", "TACCO",
            "Observer", "door gateway", "chin shelf")
    return {n: e["m"] for n, e in P.items() if not n.startswith(skip)}


def bbox_hit(a: Manifold, b: Manifold) -> bool:
    """Cheap reject before the boolean: do the two bounding boxes overlap?"""
    x = np.array(a.bounding_box()).reshape(2, 3)
    y = np.array(b.bounding_box()).reshape(2, 3)
    return bool(np.all(x[0] <= y[1]) and np.all(y[0] <= x[1]))


def expected(feat: str, tgt: str) -> str | None:
    for f, t, why in EXPECTED:
        if f in feat and t in tgt:
            return why
    return None


def census(scad: str, P: dict, export: str | None = None,
           defines: tuple[str, ...] = ()) -> dict:
    """Feature x corner x target overlap volumes plus the function checks."""
    corners = parse_corners(scad)
    jobs = {(st, n): FEATURES[n][0] for st in ("fore", "aft") for n in FEATURES}
    with cf.ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as ex:
        fut = {k: ex.submit(render, scad, k[0], k[1], e, defines) for k, e in jobs.items()}
        paths = {k: f.result() for k, f in fut.items()}
    T = targets(P)
    rows, func = [], []
    for cn, c in corners.items():
        st, tf = STATION[cn], corner_tf(c)
        # The PRINTED bay is the conforming per-corner part from
        # tools/generate_lg_bays.py when it has been generated (owner
        # 2026-10-10, BHD-02); the flat SCAD bay is then only its design
        # source, and its flat cowl and nominal bolts are not what is built.
        gen = GENERATED.format(cn)
        conforming = os.path.exists(gen) and scad == SCAD and not defines
        if conforming:
            bay = cbc.man(trimesh.load(gen, force="mesh"))
            keep = corner_keepout(cn)
        else:
            bay = posed(paths[(st, "bay (printed part)")], tf)
            keep = None
        leg = swept_leg(paths[(st, "leg (thigh+shin+foot)")], tf)
        bodies = len(bay.decompose()) if conforming else len(
            trimesh.load(paths[(st, "bay (printed part)")], force="mesh")
            .split(only_watertight=False))
        # Thigh corridor: the swept leg against its OWN bay, minus the hip pin
        # contact (the lug sits between the ears on the pin -- designed).
        own = (leg ^ bay).volume()
        wires = posed(paths[(st, "wires")], tf) + posed(paths[(st, "wires deformed")], tf)
        pin = posed(paths[(st, "stop pin")], tf)
        leg0 = posed(paths[(st, "leg (thigh+shin+foot)")], tf)
        func.append(dict(corner=cn, bay_bodies=bodies, leg_sweep_vs_own_bay_mm3=round(own, 1),
                         wires_x_stop_pin_mm3=round((wires ^ pin).volume(), 1),
                         wires_x_bay_mm3=round((wires ^ bay).volume(), 1),
                         wires_x_leg_rest_mm3=round((wires ^ leg0).volume(), 1),
                         stop_pin_x_leg_sweep_mm3=round((pin ^ leg).volume(), 1),
                         wire_x_wire_mm3=round(wire_pairs(paths[(st, "wires deformed")], tf), 1)))
        for fn in FEATURES:
            if fn in BUILD_ONLY or (conforming and fn == "cowl (flange+liner)"):
                continue
            if fn.startswith("leg"):
                m = leg
            elif conforming and fn == "bay (printed part)":
                m = bay
            elif conforming and fn == "M3 bolt keep-out":
                m = keep
            else:
                m = posed(paths[(st, fn)], tf)
            for tn, tm in T.items():
                if SIDE[cn] not in tn and not tn.startswith(("shell", "collar")):
                    continue
                if not bbox_hit(m, tm):
                    continue
                v = (m ^ tm).volume()
                if v <= 0.05:
                    continue
                why = expected(fn, tn)
                verdict = "expected" if why else ("CLASH" if v > CLASH_MM3 else "touch")
                rows.append(dict(corner=cn, feature=fn, target=tn, mm3=round(v, 1),
                                 functional=FEATURES[fn][1], verdict=verdict, why=why or ""))
                if export and verdict == "CLASH":
                    os.makedirs(export, exist_ok=True)
                    safe = "".join(ch if ch.isalnum() else "_" for ch in f"{cn}_{fn}_{tn}")
                    cbc.tri(m ^ tm).export(os.path.join(export, f"CLASH_{safe}.stl"))
        if export:
            os.makedirs(export, exist_ok=True)
            cbc.tri(bay).export(os.path.join(export, f"bay_{cn}.stl"))
            cbc.tri(leg).export(os.path.join(export, f"leg_swept_{cn}.stl"))
    return dict(scad=os.path.relpath(scad, REPO), scad_sha=sha(scad), defines=list(defines),
                sweep_deg=SWEEP_DEG, rows=rows, function=func)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--scad", default=SCAD, help="gear SCAD to evaluate (default canonical)")
    ap.add_argument("-D", "--define", action="append", default=[],
                    help="extra OpenSCAD override NAME=VALUE (repeatable)")
    ap.add_argument("--json", help="write the report here")
    ap.add_argument("--export", help="write posed bays, swept legs and clashes as STL here")
    a = ap.parse_args()
    P = cbc.build()
    R = census(os.path.abspath(a.scad), P, a.export, tuple(a.define))
    print(f"gear SCAD {R['scad']} sha {R['scad_sha']}; leg swept 0..{SWEEP_DEG:g} deg")
    print(f"\n{'corner':10s} {'feature':24s} {'target':30s} {'mm3':>8s}  verdict")
    for r in sorted(R["rows"], key=lambda r: (r["corner"], r["feature"], -r["mm3"])):
        tag = " [FUNCTIONAL: relieve the other part]" if r["functional"] and \
            r["verdict"] == "CLASH" else ""
        print(f"{r['corner']:10s} {r['feature']:24s} {r['target']:30s} {r['mm3']:8.1f}  "
              f"{r['verdict']}{tag} {r['why']}")
    print("\nFunction checks:")
    for f in R["function"]:
        ok = function_ok(f)
        print(f"  {'OK  ' if ok else 'FAIL'} {f['corner']:10s} bay bodies {f['bay_bodies']}, "
              f"leg sweep x own bay {f['leg_sweep_vs_own_bay_mm3']} mm3, wires x stop pin "
              f"{f['wires_x_stop_pin_mm3']} / x bay {f['wires_x_bay_mm3']} / x leg "
              f"{f['wires_x_leg_rest_mm3']}, stop pin x leg sweep "
              f"{f['stop_pin_x_leg_sweep_mm3']} mm3")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(R, fh, indent=2)
    bad = any(r["verdict"] == "CLASH" for r in R["rows"]) or not all(
        function_ok(f) for f in R["function"])
    print(f"\nRESULT: {'FAIL' if bad else 'PASS'}")
    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
