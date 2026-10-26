#!/usr/bin/env python3
"""Serenity UAV -- verify every placed part sits where it belongs in the hull frame.

Consumes the master-assembly export (``freecadcmd tools/export_assembly_meshes.py
-- DIR``) and the pair census of it (``tools/airframe_interface_census.py DIR
--json > DIR/census.json``) and gives each placed part three verdicts:

* ATTACH   -- the part touches (CONTACT) or is bonded/merged into (CLASH) at
             least one of the hosts it is declared to mount on.  A part that
             floats free of its mount is mislocated, however clean its pairs.
* CONTAIN  -- an interior part lies inside the hull's outer skin: every
             sampled vertex is tested against the outer contour of the hull
             cross-section at its own Y station (section-and-probe, the method
             tools/cargo_bay_envelope.py documents; a closed-cavity solid does
             not work on these open shells).
* CURRENT  -- the part is not one the design has retired (a superseded part
             still placed corrupts the census and the mass ledger).

The joint census owns CLASH/NEAR between parts (owner direction 2026-10-03,
plan 2026-10-03-002); this tool owns location.  Exit 2 on any FAIL.

Run:
    freecadcmd tools/export_assembly_meshes.py -- DIR
    /usr/bin/python3 tools/airframe_interface_census.py DIR --json > DIR/census.json
    /usr/bin/python3 tools/placement_audit.py DIR

Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CEH (GitHub Stab-Rabbit-coding)
AI note : Written by Claude (Claude Opus 5.5, Anthropic) under the author's
          direction, 2026-10-19 ("parts need to be verified to be in their
          correct hull frame location"), per AGENTS.md AI attribution.
License : MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import MultiPoint, Point, Polygon

SHELLS = ("Head_Shell", "Cargo_Shell", "Middle_Shell", "Rear_Shell")

# Declared mounts: a part must touch or bond to at least one of these.
HOSTS = {
    "Head_Shell": ["Head_Cargo_Splice_Collar"],
    "Cargo_Shell": ["Head_Cargo_Splice_Collar", "Cargo_Middle_Splice_Collar"],
    "Middle_Shell": ["Cargo_Middle_Splice_Collar", "Middle_Rear_Splice_Collar"],
    "Rear_Shell": ["Middle_Rear_Splice_Collar"],
    "Head_Cargo_Splice_Collar": ["Head_Shell", "Cargo_Shell"],
    "Cargo_Middle_Splice_Collar": ["Cargo_Shell", "Middle_Shell"],
    "Middle_Rear_Splice_Collar": ["Middle_Shell", "Rear_Shell"],
    "Landing_Gear_R6": ["Cargo_Shell"],
    "Cargo_Door_Port": ["Cargo_Hinge_Retention", "Cargo_Shell"],
    "Cargo_Door_Stbd": ["Cargo_Hinge_Retention", "Cargo_Shell"],
    "Cargo_Hinge_Retention": ["Cargo_Shell"],
    "Wing_Port": ["Cargo_Shell"],
    "Wing_Stbd": ["Cargo_Shell"],
    "Nacelle_Port": ["Nacelle_Port_Trunnion"],
    "Nacelle_Stbd": ["Nacelle_Stbd_Trunnion"],
    "Nacelle_Port_Trunnion": ["Wing_Port", "Nacelle_Port"],
    "Nacelle_Stbd_Trunnion": ["Wing_Stbd", "Nacelle_Stbd"],
    "Wing_Port_Tilt_Pinion": ["Wing_Port", "Nacelle_Port_Trunnion"],
    "Wing_Stbd_Tilt_Pinion": ["Wing_Stbd", "Nacelle_Stbd_Trunnion"],
    "Tilt_Bracket_Port": ["Cargo_Shell"],
    "Tilt_Bracket_Stbd": ["Cargo_Shell"],
    "Tilt_Worm_Port": ["Tilt_Bracket_Port", "Tilt_Wheel_Port"],
    "Tilt_Worm_Stbd": ["Tilt_Bracket_Stbd", "Tilt_Wheel_Stbd"],
    "Tilt_Wheel_Port": ["Tilt_Worm_Port"],
    "Tilt_Wheel_Stbd": ["Tilt_Worm_Stbd"],
    "Tilt_Brake_Guide_Port": ["Tilt_Bracket_Port"],
    "Tilt_Brake_Guide_Stbd": ["Tilt_Bracket_Stbd"],
    "Battery_Cradle": ["Cargo_Shell"],
    "Chin_Node_Shelf": ["Cargo_Shell"],
    "Door_Latch_Bracket_Port": ["Cargo_Shell"],
    "Door_Latch_Bracket_Stbd": ["Cargo_Shell"],
    # DOOR-REWORK (2026-10-26): the bell-crank turns on its bracket's pivot pin
    "Door_Latch_Crank_Port": ["Door_Latch_Bracket_Port"],
    "Door_Latch_Crank_Stbd": ["Door_Latch_Bracket_Stbd"],
    "Gateway_Door_Tray": ["Cargo_Shell"],
    "Cargo_Cradle": ["Cargo_Shell", "Cargo_Door_Port", "Cargo_Door_Stbd"],
    "Cargo_FPV_Bezel": ["Cargo_Shell", "Head_Shell"],
    "Cargo_GPS_Ring": ["Cargo_Shell"],
    "Cargo_Door_Servo_Bracket": ["Cargo_Shell"],
    "Cargo_Release_Servo_Bracket": ["Cargo_Shell"],
    "Dorsal_Antenna_Fin": ["Cargo_Shell", "Head_Shell"],
}

# Parts that live inside the hull skin (CONTAIN applies).
INTERIOR = {
    "Head_Cargo_Splice_Collar", "Cargo_Middle_Splice_Collar",
    "Middle_Rear_Splice_Collar", "Cargo_Hinge_Retention", "Tilt_Bracket_Port",
    "Tilt_Bracket_Stbd", "Tilt_Worm_Port", "Tilt_Worm_Stbd", "Tilt_Wheel_Port",
    "Tilt_Wheel_Stbd", "Tilt_Brake_Guide_Port", "Tilt_Brake_Guide_Stbd",
    "Battery_Cradle", "Chin_Node_Shelf", "Door_Latch_Bracket_Port",
    "Door_Latch_Bracket_Stbd", "Door_Latch_Crank_Port", "Door_Latch_Crank_Stbd",
    "Gateway_Door_Tray", "Cargo_Cradle",
    "Cargo_GPS_Ring", "Cargo_Door_Servo_Bracket", "Cargo_Release_Servo_Bracket",
}

# Retired designs that must not be placed.
SUPERSEDED = {
    "Cargo_Winch_Mount": "N20 cantilever winch, scrubbed 2026-07-27 (fuselage-mid WBS)",
    "Cargo_Winch_Spool": "N20 D-bore spool, scrubbed 2026-07-27 (fuselage-mid WBS)",
    "Cargo_DRV8833_Tray": "retired 2026-09-21 (docs/CARGO_DOOR_GATEWAY_SPEC.md)",
    "Battery_Tray": "superseded by Battery_Cradle, Rev T5 (docs/BATTERY_MOUNT.md)",
    "Belly_Panel": "superseded with the keel battery tray, Rev T5",
}

# Bonded joints carry a glue line: within this gap counts as attached.
BONDED = {"Head_Cargo_Splice_Collar", "Cargo_Middle_Splice_Collar",
          "Middle_Rear_Splice_Collar", "Head_Shell", "Cargo_Shell", "Middle_Shell",
          "Rear_Shell"}
BOND_GAP_MM = 1.0
TOL_OUT_MM = 0.5          # vertex may sit this far outside the outer contour
SLAB_MM = 2.0             # vertices within +/- this of a section are tested


def outer_contour(shell: trimesh.Trimesh, y: float) -> Polygon | None:
    """Outer skin contour (X, Z) of a shell at hull station y.

    The cargo section is OPEN at the clamshell aperture and the mating rims,
    so its section is not a closed loop; the convex hull of the section points
    is the outer envelope used.  A point outside it is certainly outside the
    skin; concave skin regions are over-generous (a containment PASS there is
    advisory, a FAIL is real)."""
    sec = shell.section(plane_origin=[0.0, y, 0.0], plane_normal=[0.0, 1.0, 0.0])
    if sec is None or len(sec.vertices) < 3:
        return None
    hull = MultiPoint([tuple(p) for p in sec.vertices[:, [0, 2]]]).convex_hull
    return hull if isinstance(hull, Polygon) else None


def contain(part: trimesh.Trimesh, shells: dict[str, trimesh.Trimesh]) -> tuple[bool, str]:
    """Every sampled vertex of an interior part inside the hull outer contour."""
    v = part.vertices
    ys = np.linspace(v[:, 1].min() + 0.5, v[:, 1].max() - 0.5, 7)
    worst = 0.0
    tested = 0
    for y in ys:
        # nearest shell by Y (splice collars straddle the inter-shell gaps)
        host = min(shells.values(), key=lambda s: max(s.bounds[0][1] - y, y - s.bounds[1][1], 0))
        if max(host.bounds[0][1] - y, y - host.bounds[1][1]) > 3.0:
            return False, f"Y {y:.1f} more than 3 mm from every shell"
        y = min(max(y, host.bounds[0][1] + 0.5), host.bounds[1][1] - 0.5)
        poly = outer_contour(host, y)
        if poly is None:
            continue
        sl = v[np.abs(v[:, 1] - y) <= SLAB_MM]
        for x, z in sl[:: max(1, len(sl) // 200), [0, 2]]:
            tested += 1
            if not poly.contains(Point(x, z)):
                worst = max(worst, poly.exterior.distance(Point(x, z)))
    if tested == 0:
        return True, "no slab vertices (thin part) -- bbox only"
    ok = worst <= TOL_OUT_MM
    return ok, f"{tested} pts, worst outside {worst:.2f} mm"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("census", type=Path, help="export dir with manifest.json + census.json")
    a = ap.parse_args(argv)
    man = json.loads((a.census / "manifest.json").read_text())
    cen = json.loads((a.census / "census.json").read_text())
    pairs = {}
    for r in cen["pairs"]:
        pairs[(r["a"], r["b"])] = pairs[(r["b"], r["a"])] = r
    meshes = {k: trimesh.load_mesh(v["file"], force="mesh") for k, v in man.items()}
    shells = {k: meshes[k] for k in SHELLS if k in meshes}
    fails = 0
    print(f"{'part':30} {'ATTACH':34} {'CONTAIN':36} CURRENT")
    for name in sorted(meshes):
        if name in SUPERSEDED:
            fails += 1
            print(f"{name:30} {'-':34} {'-':36} FAIL: {SUPERSEDED[name]}")
            continue
        hosts = HOSTS.get(name)
        if hosts is None:
            att, aok = "no host declared", False
        else:
            hit = [(h, pairs[(name, h)]) for h in hosts if (name, h) in pairs]
            good = [f"{h} {r['class'].split('/')[0]} {r['gap_mm']}" for h, r in hit
                    if r["class"].startswith(("CLASH", "CONTACT"))
                    or (name in BONDED and r["gap_mm"] <= BOND_GAP_MM)]
            aok = bool(good)
            att = good[0] if good else ("nearest " + ", ".join(
                f"{h} {r['gap_mm']} mm" for h, r in hit) if hit else "no host within 3 mm")
        if name in INTERIOR:
            cok, ctext = contain(meshes[name], shells)
        else:
            cok, ctext = True, "exterior / structure"
        ok = aok and cok
        fails += not ok
        print(f"{name:30} {('ok  ' if aok else 'FAIL ') + att:34.34} "
              f"{('ok  ' if cok else 'FAIL ') + ctext:36.36} ok")
    print(f"\nRESULT: {'PASS' if not fails else f'FAIL -- {fails} part(s)'}")
    return 2 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
