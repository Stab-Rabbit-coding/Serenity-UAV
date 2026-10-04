#!/usr/bin/python3
"""Stage the 64 mm nacelle parts, in NACELLE-LOCAL frame, for the hull bake.

Inputs (OpenSCAD renders):
  --stbd-pod / --port-pod   nacelle_pod_64mm_tandem.scad, PYLON_SIDE +1 / -1
  --trunnion                nacelle_trunnion_64mm.scad (trunnion PART frame)
  --pinion                  airframe/openscad/wings/wing_tilt_pinion.scad

Writes (unbaked; ``tools/bake_hull_frame.py`` then bakes them, marker-guarded):
  airframe/stls/nacelles/nacelle_{stbd,port}_64mm.stl
  airframe/stls/nacelles/nacelle_trunnion_64mm_{stbd,port}.stl
  airframe/stls/wings/wing_tilt_pinion_{stbd,port}.stl

All six share ONE nacelle-local frame per side, so ONE bake transform per
side (bake_hull_frame.py COMPONENTS 'Nacelle64_*', 'Trunnion64_*',
'TiltPinion64_*') places them coherently.  Port parts are the MIRROR of the
starboard parts through the pod mid-plane (local x = 0), exactly as the pod
itself is generated with PYLON_SIDE = -1; trimesh flips the winding of a
negative-determinant transform, so the mirrored meshes stay outward-facing.

Frames (as in nacelle_tilt_joint_context.scad):
  trunnion part -> nacelle local, starboard:  x_l = z_p + TRUNNION_X0,
                  y_l = -y_p,  z_l = x_p + PIVOT_Z.
  pinion: on the wing shaft at azimuth SHAFT_AZ, radius SHAFT_R about the
  tilt axis (part frame), outboard face at part z = GEAR_Z0, rotated to the
  cruise mesh phase spin = PHASE + SHAFT_AZ * (1 + 50/14) (in-context sweep,
  2026-10-03).

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, per AGENTS.md AI attribution.  License: CC BY 4.0.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import trimesh

REPO = Path(__file__).resolve().parents[1]
STL = REPO / "airframe" / "stls"

# Single-sourced values (see the SCAD files named beside each).
TRUNNION_X0 = 35.34          # nacelle_trunnion_64mm.scad TRUNNION_X0
PIVOT_Z = 109.7              # nacelle_pod_64mm_tandem.scad PIVOT_Z
GEAR_Z0 = 2.0                # trunnion GEAR_Z0 (option A band 2.0..12.5)
SHAFT_DY, SHAFT_DZ = 25.6, 2.2391   # trunnion SHAFT_DY / SHAFT_DZ (Rev T6)
SHAFT_R = math.hypot(SHAFT_DY, SHAFT_DZ)
SHAFT_AZ = math.degrees(math.atan2(SHAFT_DZ, SHAFT_DY))
PHASE = 13.0                 # mesh phase found by the 2026-10-03 roll sweep

P2L = np.array([[0, 0, 1, TRUNNION_X0], [0, -1, 0, 0], [1, 0, 0, PIVOT_Z],
                [0, 0, 0, 1]], float)
MIRROR_X = np.diag([-1.0, 1.0, 1.0, 1.0])


def rz(deg: float) -> np.ndarray:
    """4x4 rotation about z."""
    return trimesh.transformations.rotation_matrix(math.radians(deg), [0, 0, 1])


def pinion_local(pinion: trimesh.Trimesh) -> trimesh.Trimesh:
    """Starboard pinion in nacelle-local frame at the cruise mesh phase."""
    p = pinion.copy()
    p.apply_transform(rz(PHASE + SHAFT_AZ * (1 + 50 / 14)))
    a = math.radians(SHAFT_AZ)
    p.apply_translation([SHAFT_R * math.cos(a), SHAFT_R * math.sin(a), GEAR_Z0])
    p.apply_transform(P2L)
    return p


def write(mesh: trimesh.Trimesh, rel: str) -> None:
    """Write an unbaked binary STL and report it."""
    out = STL / rel
    if out.exists():
        hdr = out.read_bytes()[:80]
        if b"HULL-FRAME" in hdr:
            raise SystemExit(f"{rel} is already baked; remove it first (never re-bake)")
    mesh.export(out)
    print(f"  wrote {rel}: {len(mesh.faces)} faces, watertight {mesh.is_watertight}, "
          f"bounds x {mesh.bounds[:, 0].round(2)}")


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    for k in ("stbd-pod", "port-pod", "trunnion", "pinion"):
        ap.add_argument(f"--{k}", type=Path, required=True)
    a = ap.parse_args()
    tr = trimesh.load_mesh(a.trunnion, force="mesh")
    tr.apply_transform(P2L)
    pin = pinion_local(trimesh.load_mesh(a.pinion, force="mesh"))
    print(f"shaft R {SHAFT_R:.3f} mm, azimuth {SHAFT_AZ:.3f} deg")
    write(trimesh.load_mesh(a.stbd_pod, force="mesh"), "nacelles/nacelle_stbd_64mm.stl")
    write(trimesh.load_mesh(a.port_pod, force="mesh"), "nacelles/nacelle_port_64mm.stl")
    write(tr, "nacelles/nacelle_trunnion_64mm_stbd.stl")
    write(pin, "wings/wing_tilt_pinion_stbd.stl")
    for m, rel in ((tr, "nacelles/nacelle_trunnion_64mm_port.stl"),
                   (pin, "wings/wing_tilt_pinion_port.stl")):
        mm = m.copy()
        mm.apply_transform(MIRROR_X)
        write(mm, rel)


if __name__ == "__main__":
    main()
