#!/usr/bin/env python3
"""Re-export every Rev R6 landing-gear STL from the two canonical leg SCADs.

The export recipe used to live only as a comment block in each SCAD ("... same
pattern for every PART above"), which meant a geometry change was published by
hand, one `openscad -o` at a time, and any PART someone forgot silently kept
shipping its old geometry.  LG-10.5/10.6/10.8 each touched shared constants, so
that is now a scripted, all-or-nothing pass.

Two rules the layout encodes:

  * **Per-variant parts** (`leg_frame`, `leg_assembled`, `leg_deformed`,
    `hull_legs`, `hull_stance`) differ between the 1.5in and 3.0in legs and are
    written as `lg_r6_<variant>_<part>.stl`.
  * **Common parts** (`bay`, `foot`, and the four wires) are shared hardware --
    identical geometry in both variants -- and are written once as
    `lg_r6_common_<part>.stl`.  They are exported from EACH variant and the
    results compared; a mismatch means the "shared BOM" claim of
    `docs/LANDING_GEAR_ANALYSIS.md` SS11.4 has quietly broken, and that is a
    hard error rather than a note, because it would mean the two legs need
    different bays.

    The comparison is GEOMETRIC (face count, volume, bounds), not byte-exact:
    two OpenSCAD runs of the same solid may order facets differently, and
    SS11.4's claim is itself a volume/bounds equality.  It earned its keep
    immediately -- it caught `bowed_wire` in the 1.5in file building its side
    wall as a list of face PAIRS wrapped in a no-op `concat()`, so every wire
    on the DEFAULT leg had been exporting as 20 cap faces of zero volume while
    the shared wire STLs were quietly coming from the 3.0in file.

`hull_legs` / `hull_stance` are emitted directly at their hull-frame stations
by the SCAD, so they are NOT passed through `tools/bake_hull_frame.py` and
carry no HULL-FRAME marker -- they are not in that tool's COMPONENTS table.

Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note : Authored by Claude (model: Claude Opus 5, Anthropic) under the
          author's direction, 2026-08-17, per AGENTS.md AI attribution.
License : CC BY-SA 4.0  <https://creativecommons.org/licenses/by-sa/4.0/>

Run: /usr/bin/python3 tools/export_landing_gear_stls.py [--jobs N] [--only PART]
"""

import argparse
import concurrent.futures as cf
import os
import subprocess
import sys
import tempfile

try:
    import numpy as np
    import trimesh
except ImportError:
    sys.exit("trimesh/numpy unavailable -- run with /usr/bin/python3, "
             "not the .venv")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
SCAD_DIR = os.path.join(REPO_ROOT, "airframe", "openscad", "fuselage")
OUT_DIR = os.path.join(REPO_ROOT, "airframe", "stls", "fuselage", "landing-gear")

VARIANTS = ("1_5in", "3_0in")
PER_VARIANT = ("leg_frame", "leg_assembled", "leg_deformed",
               "hull_legs", "hull_stance")
COMMON = ("bay", "foot",
          "spring_wire_nominal", "spring_wire_deformed",
          "ductile_wire_nominal", "ductile_wire_deformed")
# A single corner compound can take several minutes to CGAL-evaluate.
TIMEOUT_S = 1800
# Shared-part equality tolerances.  Both variants evaluate the same solid, so
# the only legitimate difference is float32 export round-off.
VOL_TOL_MM3 = 1e-3
BOUND_TOL_MM = 1e-3


def mesh_signature(path):
    """(face count, volume, bounds) -- what SS11.4's equality claim means."""
    m = trimesh.load(path, process=False)
    return len(m.faces), abs(m.volume), m.bounds


def signatures_match(a, b):
    """True when two shared-part exports are the same solid."""
    return (a[0] == b[0]
            and abs(a[1] - b[1]) <= VOL_TOL_MM3
            and np.allclose(a[2], b[2], atol=BOUND_TOL_MM))


def render(scad, part, out_path):
    """Run one OpenSCAD export.  Returns (ok, note)."""
    cmd = ["openscad", "-o", out_path, "-D", f'PART="{part}"', scad]
    try:
        got = subprocess.run(cmd, capture_output=True, text=True,
                             timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return False, f"TIMEOUT after {TIMEOUT_S}s"
    if got.returncode != 0:
        tail = (got.stderr or got.stdout).strip().splitlines()
        return False, "; ".join(tail[-2:]) if tail else "non-zero exit"
    if not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
        return False, "no output written"
    # An OpenSCAD assert() failure is reported on stderr; treat it as fatal even
    # if a file was somehow produced.
    if "ASSERT" in (got.stderr or "").upper():
        return False, "assertion failed"
    return True, f"{os.path.getsize(out_path) / 1e6:.1f} MB"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=4,
                    help="parallel OpenSCAD renders (default 4)")
    ap.add_argument("--only", help="export just this PART")
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="lg_export_")
    jobs = []          # (label, scad, part, out_path)

    for variant in VARIANTS:
        scad = os.path.join(SCAD_DIR, f"canonical_leg_r6_{variant}.scad")
        for part in PER_VARIANT:
            if args.only and part != args.only:
                continue
            jobs.append((f"{variant}/{part}", scad, part,
                         os.path.join(OUT_DIR, f"lg_r6_{variant}_{part}.stl")))
        for part in COMMON:
            if args.only and part != args.only:
                continue
            # each variant renders the shared part to scratch; compared below
            jobs.append((f"{variant}/{part} (common)", scad, part,
                         os.path.join(tmp, f"{variant}_{part}.stl")))

    print(f"exporting {len(jobs)} STL(s) with {args.jobs} parallel job(s)")
    failed = []
    with cf.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(render, s, p, o): (lab, o)
                   for lab, s, p, o in jobs}
        for fut in cf.as_completed(futures):
            label, _out = futures[fut]
            ok, note = fut.result()
            print(f"  {'ok  ' if ok else 'FAIL'} {label:34s} {note}")
            if not ok:
                failed.append(label)

    # --- shared parts must be byte-identical between the two variants -------
    print("\nshared-part equality (SS11.4 shared BOM)")
    for part in COMMON:
        if args.only and part != args.only:
            continue
        paths = [os.path.join(tmp, f"{v}_{part}.stl") for v in VARIANTS]
        if not all(os.path.exists(p) for p in paths):
            print(f"  skip {part}: not rendered")
            continue
        got = [mesh_signature(p) for p in paths]
        same = signatures_match(*got)
        print(f"  {'ok  ' if same else 'DIFF'} {part:24s} "
              f"{got[0][0]:,} faces {got[0][1]:.2f} mm^3  |  "
              f"{got[1][0]:,} faces {got[1][1]:.2f} mm^3")
        if not same:
            failed.append(f"{part} differs between variants")
            continue
        dest = os.path.join(OUT_DIR, f"lg_r6_common_{part}.stl")
        with open(dest, "wb") as fh:
            fh.write(open(paths[0], "rb").read())
        print(f"       -> {os.path.relpath(dest, REPO_ROOT)}")

    print()
    if failed:
        print(f"  FAILED: {len(failed)} -- {', '.join(failed)}")
        sys.exit(1)
    print("  all landing-gear STLs re-exported")


if __name__ == "__main__":
    main()
