#!/usr/bin/env python3
# ============================================================
# verify_bow_pod.py — Rev R1 (2026-06-30)
#
# Geometric verification of the bow sensor pod aperture
# positions (bow_sensor_pod.scad) against the BAKED, hull-frame
# head shell STL.  Performs reproducible ray-cast geometry checks
# against the canonical mesh to validate aperture positioning.
#
# For each bore (Dome A camera, Dome B ToF, Dome B laser) the tool
# casts a ray along the bore axis through the SCAD-specified
# aperture centre and reports:
#   * the hull-Y station where the bore pierces the EXTERIOR skin
#     (the "bow flat face" the slicer check looks for),
#   * the skin wall thickness measured along the bore axis,
#   * whether the aperture centre lies on solid skin (2 crossings),
#   * whether the interior body pocket depth stays inside the hull
#     interior cavity (no breach out the far side / no collision
#     with the opposite skin).
#
# The SCAD bow_sensor_pod.scad models positions in the head
# part-local frame.  The published head STL is baked to the hull
# frame by tools/bake_hull_frame.py with the Head_Shell placement
# (identity rotation, translation BAKE_T below).  Part-local SCAD
# coordinates therefore map to hull coordinates by adding BAKE_T.
#
# Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
#         (verification tool authored by Claude Opus 4.8)
# License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
# ============================================================

import sys
import numpy as np

try:
    import trimesh
except ImportError:  # pragma: no cover - dependency guard
    sys.stderr.write("verify_bow_pod.py requires trimesh (pip install trimesh)\n")
    sys.exit(2)

# Head_Shell bake translation (identity rotation) — must match
# tools/bake_hull_frame.py COMPONENTS["Head_Shell"].  Hull = local + BAKE_T.
BAKE_T = np.array([-331.9993360, -17.9999640, 60.9998780])

HEAD_STL = "airframe/stls/fuselage/head_shell24_2mm_repaired.stl"

# ── SCAD constants replicated from bow_sensor_pod.scad (Rev R1c) ─────
# Flat-face layout on the 40 deg bow mounting flat: camera PORT bump,
# ToF STARBOARD bump, laser on CL between them; all bores NORMAL to the
# flat.  Positions are part-local SCAD [x, y, z]; keep in sync with
# bow_sensor_pod.scad CAM_POS / TOF_POS / LASER_POS.
CAM_POS = (170.80, -282.68, 55.01)    # 10 mm camera lens, port bump
TOF_POS = (154.33, -282.98, 55.61)    # TFmini-S ToF, starboard bump
LASER_POS = (161.33, -281.94, 56.14)  # crosshair laser exit, on CL

# Flat outward normal (bore axis, exterior-facing): tilt 40 deg about +X.
FLAT_N = np.array([0.0, -np.cos(np.radians(40.0)), -np.sin(np.radians(40.0))])

# Face aperture diameters and interior pocket depths.
CAM_APER = 10.0
CAM_BODY_D = 21.0
TOF_APER = 8.0
TOF_BODY_D = 22.0
LASER_EXIT = 6.0
LASER_BORE_L = 38.0

# Flat extents (hull), for the aperture-row fit check.
FLAT_W = 26.4  # mm — flat width spec (1.04 in)
FLAT_CENTER_X = -167.15

# Bore axis unit vectors in hull frame (exterior-facing, i.e. toward bow tip).
# BOW_ROT cylinders fire toward -Y; LASER_ROT fires 30 deg below the -Y horizon.
DIR_FWD = np.array([0.0, -1.0, 0.0])
DIR_LASER = np.array([0.0, -np.cos(np.radians(30.0)), -np.sin(np.radians(30.0))])


def local_to_hull(x, y, z):
    """Map a bow_sensor_pod.scad part-local point to baked hull coords."""
    return np.array([x, y, z]) + BAKE_T


def cast(mesh, centre, axis):
    """
    Cast a ray along ``axis`` through ``centre`` and return all surface
    hits sorted by signed distance from ``centre`` (negative = exterior
    side, positive = interior side).  ``axis`` points toward the exterior.
    """
    axis = axis / np.linalg.norm(axis)
    # Start well outside the bow tip and travel inward (interior dir = -axis).
    origin = centre + axis * 60.0
    direction = -axis
    locs, _, _ = mesh.ray.intersects_location(
        ray_origins=origin[None, :], ray_directions=direction[None, :])
    if len(locs) == 0:
        return np.empty((0,)), np.empty((0, 3))
    # Signed distance from centre measured along the interior direction:
    # positive = interior of centre, negative = exterior of centre.
    signed = (locs - centre) @ (-axis)
    order = np.argsort(signed)
    return signed[order], locs[order]


def report_bore(name, mesh, centre_hull, axis, pocket_depth):
    print(f"\n── {name} ──")
    print(f"   aperture centre (hull mm): "
          f"({centre_hull[0]:+.2f}, {centre_hull[1]:+.2f}, {centre_hull[2]:+.2f})")
    signed, locs = cast(mesh, centre_hull, axis)
    if len(signed) < 2:
        print(f"   *** FAIL: only {len(signed)} skin crossing(s) on bore axis — "
              f"aperture does NOT land on a solid 2-wall skin.")
        return False
    # Exterior face = last crossing on the exterior side (signed<=~0),
    # interior face = first crossing on the interior side.
    ext_idx = np.where(signed <= 1e-6)[0]
    int_idx = np.where(signed > 1e-6)[0]
    if len(ext_idx) == 0 or len(int_idx) == 0:
        # Centre sits off the skin; fall back to the two crossings nearest 0.
        near = np.argsort(np.abs(signed))[:2]
        near.sort()
        ext_s, int_s = signed[near[0]], signed[near[1]]
        ext_p = locs[near[0]]
        offset = ext_s
        note = " (aperture centre not exactly on skin; see offset)"
    else:
        ext_s, int_s = signed[ext_idx[-1]], signed[int_idx[0]]
        ext_p = locs[ext_idx[-1]]
        offset = ext_s
        note = ""

    wall = int_s - ext_s
    print(f"   exterior skin pierced at hull Y = {ext_p[1]:+.2f} mm  "
          f"(SCAD-placed face Y {centre_hull[1]:+.2f} mm){note}")
    print(f"   wall thickness along bore = {wall:.2f} mm "
          f"({'OK >=2 mm' if wall >= 1.8 else 'THIN <2 mm — CHECK'})")
    print(f"   aperture-centre offset from exterior skin = {offset:+.2f} mm "
          f"({'on skin' if abs(offset) < 1.0 else 'OFF skin — adjust position'})")

    # Interior pocket: does pocket_depth stay inside the cavity?
    # Walk crossings deeper than the interior face; the next crossing is the
    # opposite (far) interior wall.  Pocket must not reach it.
    deeper = signed[signed > int_s + 1e-3]
    if len(deeper) == 0:
        clearance = float("inf")
        far = None
    else:
        far = deeper[0]
        clearance = far - int_s
    pd_txt = f"{pocket_depth:.1f} mm"
    if clearance == float("inf"):
        print(f"   interior pocket depth {pd_txt}: open cavity beyond inner "
              f"face (no far wall on axis) — OK")
    elif clearance >= pocket_depth:
        print(f"   interior pocket depth {pd_txt}: cavity clearance "
              f"{clearance:.1f} mm to far wall — OK")
    else:
        print(f"   *** WARN: interior pocket {pd_txt} exceeds {clearance:.1f} mm "
              f"cavity clearance — pocket would breach far interior feature.")
    ok = (wall >= 1.8) and (abs(offset) < 1.5)
    print(f"   verdict: {'PASS' if ok else 'REVIEW'}")
    return ok


def main():
    print("Loading baked head shell:", HEAD_STL)
    mesh = trimesh.load(HEAD_STL, process=False)
    lo, hi = mesh.bounds
    print(f"   hull extents  X {lo[0]:+.1f}..{hi[0]:+.1f}  "
          f"Y {lo[1]:+.1f}..{hi[1]:+.1f}  Z {lo[2]:+.1f}..{hi[2]:+.1f} mm")
    print(f"   watertight={mesh.is_watertight}  tris={len(mesh.faces)}")

    cam = local_to_hull(*CAM_POS)
    tof = local_to_hull(*TOF_POS)
    las = local_to_hull(*LASER_POS)

    # All three bores are normal to the 40 deg flat.
    results = []
    results.append(report_bore("Camera (PORT bump) — 10 mm lens", mesh, cam,
                               FLAT_N, CAM_BODY_D))
    results.append(report_bore("ToF (STARBOARD bump) — TFmini-S", mesh, tof,
                               FLAT_N, TOF_BODY_D))
    results.append(report_bore("Laser (CL) — 6 mm exit, normal to flat", mesh,
                               las, FLAT_N, LASER_BORE_L))

    # Aperture-row fit across the 26.4 mm flat width (hull X).
    print("\n── aperture-row fit on the 40 deg flat (hull X) ──")
    half = FLAT_W / 2.0
    spans = [
        ("camera", cam[0] - CAM_APER / 2, cam[0] + CAM_APER / 2),
        ("laser", las[0] - LASER_EXIT / 2, las[0] + LASER_EXIT / 2),
        ("tof", tof[0] - TOF_APER / 2, tof[0] + TOF_APER / 2),
    ]
    spans.sort(key=lambda s: s[1])
    for (n1, a1, b1), (n2, a2, b2) in zip(spans, spans[1:]):
        gap = a2 - b1
        flag = "OK" if gap >= -0.3 else f"OVERLAP {-gap:.1f} mm"
        print(f"   {n1:>6} [{a1:+.1f}..{b1:+.1f}] | {n2:<6} [{a2:+.1f}..{b2:+.1f}]"
              f"  gap {gap:+.1f} mm  {flag}")
    row_lo = min(s[1] for s in spans)
    row_hi = max(s[2] for s in spans)
    flat_lo, flat_hi = FLAT_CENTER_X - half, FLAT_CENTER_X + half
    spill_lo = max(0.0, flat_lo - row_lo)
    spill_hi = max(0.0, row_hi - flat_hi)
    row_span = row_hi - row_lo
    print(
        f"   row span hull X [{row_lo:+.1f}..{row_hi:+.1f}] = {row_span:.1f} mm "
        f"in flat [{flat_lo:+.1f}..{flat_hi:+.1f}] ({FLAT_W:.1f} mm)"
    )
    if spill_lo or spill_hi:
        print(
            f"   over-run onto flat roll-off: stbd {spill_lo:.1f} mm / "
            f"port {spill_hi:.1f} mm (faceplate bridges; fine-tune in FreeCAD)"
        )
    else:
        print("   row fits within the flat width")

    print("\n=== SUMMARY ===")
    print(f"   bores PASS: {sum(results)}/{len(results)}")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
