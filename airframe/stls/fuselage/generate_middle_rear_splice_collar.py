#!/usr/bin/env python3
# ============================================================================
# HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
#   Hull frame (canonical for ALL design artifacts): X = +port (left),
#   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
#   world origin.  This part is generated DIRECTLY in hull frame (it spans the
#   middle/rear joint at hull Y ~ +203 mm); identity placement in assembly.
#
#   middle_rear_splice_collar  (Rev R1, 2026-07-03)
#   --------------------------------------------------------------------------
#   Internal bonded splice collar securing the MIDDLE section to the REAR
#   section across the fabrication-split joint at hull Y ~ +203 mm.  Mirrors
#   the first-principles method used for the head/cargo joint
#   (generate_head_cargo_splice_collar.py, docs/structural_analysis.md S7.3;
#   TODO.md S1.1.1.0b "Middle/Rear splice structure analysis + design").
#
#   Why this part exists
#   --------------------------------------------------------------------------
#   Two structural paths already cross this joint: the CF skid rods (Ø4 mm,
#   hull Y +173..+233, FOS 205 in axial tension, structural_analysis.md S6.2)
#   and the closed inner-neck tube (CLAUDE.md "middle section is one printed
#   piece").  Those size the SKID-IMPACT load path.  They do not, by
#   themselves, satisfy the CLAUDE.md fabrication standard for the SHELL
#   joint itself (minimum 2-wall contact annulus + positive-stop shoulder;
#   friction fits are not acceptable) — the three Ø3.2 mm boss pins at this
#   joint (structural_analysis.md S7.2 Joint 3) are alignment dowels only,
#   same shallow-engagement limitation documented at Joints 1 and 2, and a
#   bare 2 mm-shell butt bond still loads the bondline in peel.
#
#   Cross-section survey (trimesh, this repo's baked STLs, 2026-07-03):
#   AT THE JOINT PLANE ITSELF the middle cross-section is still a single
#   closed tube (convex-hull-area ratio 0.96-1.00 for hull Y = 195-203 mm) —
#   the ventral horseshoe opening does not appear until further forward
#   (multiple separate loops appear only for hull Y <~ +191 mm going forward
#   from the joint).  This means a FULL RING collar (not a partial arch or an
#   inner-neck-only sleeve, as speculatively raised in TODO.md S1.1.1.0b) is
#   feasible here too, covering the WHOLE section exactly as at the head/
#   cargo and cargo/middle joints, not just the inner neck.
#
#   Load check (ultimate, joint FOS 4.0 per structural_analysis.md S3/S7.3) —
#   SHELL bending only; the skid-tip impact load is carried by the CF skid
#   rods (S6.2), not this collar:
#   mass aft of this joint = rear shell (314 g) + the same "~300 g avionics/
#   wiring" allocation used in S4.3's rear-cantilever check = 614 g (same
#   figure S4.3 already uses for the rear section).  Arm = half the rear
#   section length (uniform-distributed-load convention, S4.3) =
#   (384.3 - 203.4) / 2 = 90.5 mm.
#     2g maneuver x4.0 = 8.0g:  F = 48.2 N  M = 4 365 N*mm
#     2.5g landing x4.0 = 10.0g: F = 60.2 N  M = 5 451 N*mm
#     9g crash x1.5 = 13.5g:    F = 81.3 N  M = 7 362 N*mm
#   Real section modulus computed from the actual digitized middle cross-
#   section at Y = 195 mm (thin-wall line integral about the lateral bending
#   axis, wall_t = 2 mm): perimeter 442 mm, S_x = 27 713 mm^3.  Peak fibre
#   stress at 9g crash = 7362 / 27713 = 0.27 MPa -- far below the CF-PETG/
#   epoxy allowable (~5 MPa, S7.3).  NOT strength-limited (even less demanding
#   than the cargo/middle joint) — the governing requirements are again peel
#   resistance, alignment, and anti-ovalisation of the thin section.
#
#   Design -- internal bonded splice collar (PRINT-MIDDLE-REAR-COLLAR).
#   Profile = MIDDLE inner-wall contour at hull Y = +195 mm (a clean region
#   8.4 mm forward of the joint, inside the middle section, before the
#   horseshoe opens further forward) inset by a 2 mm bond gap, 2 mm wall.
#   L = 16 mm (8 mm into each section, centred on the joint at hull
#   Y = +203.4 mm -- the midpoint of the measured middle aft face,
#   Y = +203.62 mm, and rear fwd face, Y = +203.20 mm).  Middle is again the
#   narrower section at this joint (inner area ~11 400 mm^2 at Y=195 vs the
#   rear's ~13 600-13 800 mm^2 at the nearest clean rear stations), so the
#   collar (sized to middle) slips into rear with a larger, epoxy-filled gap
#   -- same asymmetric-fit pattern as both other collars.
#
#   MESH-01 caveat: the rear shell (airframe/stls/fuselage/
#   rear_shell24_2mm_repaired.stl) is NOT watertight as of this writing
#   (TODO.md MESH-01; 36 disconnected bodies) and the defect band (hull
#   Y ~ +205..+230 mm) overlaps this collar's rear-side bonding span (hull
#   Y +203.4..+219.4).  The nearest clean rear cross-section is Y = +233 mm
#   (~30 mm aft of the joint, main-tube area ~13 600-14 900 mm^2 alongside
#   the two skid-arm lobes), used here only as a size/fit sanity check, not a
#   fit verification over the true bonding span on the rear side.  Re-verify
#   the rear-side fit once MESH-01 is resolved for rear.
#
#   Bond: West System 105/206 thickened with 406 colloidal silica.  Double-lap
#   shear area ~= 442 mm perim x 8 mm x 2 sides ~= 7072 mm^2; worst-case
#   bending couple tension (~81 N at 9g crash over a ~65 mm lever) gives bond
#   shear << 0.05 MPa -> FOS > 100 on the bond; sized by handling/printability
#   (~16 g), not stress -- same governing criterion as S7.3.
#
# Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
# License: CC BY 4.0 - creativecommons.org/licenses/by/4.0
# Print spec:  CF-PETG, 0.15 mm layer, 4 perimeters, 100% infill (thin ring;
#              perimeters fill the 2 mm wall).  Bond with West System 105/206.
# ============================================================================
"""generate_middle_rear_splice_collar.py — Rev R1 (2026-07-03)

Generate the internal middle/rear splice collar (hull frame) from the baked
middle shell inner contour.

Output: middle_rear_splice_collar.stl
Run:    python3 generate_middle_rear_splice_collar.py
"""

import os

import numpy as np
import trimesh
from shapely.geometry import Polygon

MIDDLE_STL = "middle_shell24_2mm_repaired.stl"  # sibling in airframe/stls/fuselage/
REAR_STL = "rear_shell24_2mm_repaired.stl"  # for fit sanity check only
SAMPLE_Y = 195.0  # mm — clean middle inner-contour station for the profile
JOINT_Y = 203.4  # mm — middle/rear mate plane (middle aft +203.62, rear fwd +203.20)
COLLAR_L = 16.0  # mm — total length (8 mm into each section)
BOND_GAP = 2.0  # mm — bond gap (collar outer inset from middle inner wall).
#                       Sized so the collar clears the skin inner wall everywhere
#                       over the bonding span. Bonded with West System 105/206
#                       thickened with 406 colloidal silica; the boss dowel pins
#                       do the concentric piloting, not the collar. The CF skid
#                       rods (S6.2-6.3) are unaffected — bore centres (X=-202/
#                       -135, Z=18/20) sit outside the collar's WALL_T ring at
#                       Y = 195 (collar outer radius << skid-rod bore radius
#                       from the joint centroid X=-170.1, Z=+74.6).
WALL_T = 2.0  # mm — collar radial wall
SIMPLIFY = 0.4  # mm — contour simplification tolerance


def _ring_polygon(here):
    """Build the collar ring (shapely Polygon with a hole) from the middle
    inner contour at SAMPLE_Y."""
    mesh = trimesh.load(os.path.join(here, MIDDLE_STL))
    sec = mesh.section(plane_origin=[0, SAMPLE_Y, 0], plane_normal=[0, 1, 0])
    loops = [loop[:, [0, 2]] for loop in sec.discrete]  # (X, Z) loops

    def area(p):
        x, z = p[:, 0], p[:, 1]
        return 0.5 * abs(np.dot(x, np.roll(z, -1)) - np.dot(z, np.roll(x, -1)))

    loops.sort(key=area, reverse=True)
    inner_contour = loops[1]  # [0] outer wall, [1] inner wall
    poly = Polygon(inner_contour).buffer(0).simplify(SIMPLIFY)

    outer = poly.buffer(-BOND_GAP)  # collar outer surface (slip fit)
    hole = outer.buffer(-WALL_T)  # collar inner surface
    return outer, hole, mesh


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    outer, hole, middle = _ring_polygon(here)

    ring = outer.difference(hole)
    # extrude the (X,Z) ring along its local +Z, then remap local Z -> hull Y
    solid = trimesh.creation.extrude_polygon(ring, height=COLLAR_L)
    v = solid.vertices.copy()
    # local (x=X, y=Z, z=extrude) -> hull (X, Y=extrude centred on joint, Z)
    hull = np.column_stack([v[:, 0], v[:, 2] + (JOINT_Y - COLLAR_L / 2.0), v[:, 1]])
    solid = trimesh.Trimesh(vertices=hull, faces=solid.faces, process=True)
    # the X/Z axis swap above is a reflection → flips face winding; restore
    # outward normals so the solid has positive volume.
    solid.fix_normals()

    out = os.path.join(here, "middle_rear_splice_collar.stl")
    solid.export(out)

    b = solid.bounds

    def _loop_areas(mesh, y):
        s = mesh.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
        if s is None:
            return []
        out = []
        for loop in s.discrete:
            p = loop[:, [0, 2]]
            x, z = p[:, 0], p[:, 1]
            out.append(0.5 * abs(np.dot(x, np.roll(z, -1)) - np.dot(z, np.roll(x, -1))))
        return sorted(out, reverse=True)

    print("middle/rear splice collar (Rev R1, hull frame):")
    print(
        f"  profile: middle inner @Y={SAMPLE_Y}  gap={BOND_GAP}  wall={WALL_T}"
        f"  L={COLLAR_L}"
    )
    print(
        f"  bounds: X {b[0][0]:.1f}..{b[1][0]:.1f}  "
        f"Y {b[0][1]:.1f}..{b[1][1]:.1f}  "
        f"Z {b[0][2]:.1f}..{b[1][2]:.1f} mm"
    )
    print(
        f"  watertight={solid.is_watertight}  "
        f"facets={len(solid.faces)}  "
        f"volume={solid.volume:.0f} mm^3  "
        f"mass(CF-PETG)={solid.volume * 1.27e-3:.1f} g"
    )
    all_fit = True
    for y in (196.0, 198.0, 200.0):
        ma = _loop_areas(middle, y)
        ca = _loop_areas(solid, y)
        if len(ma) < 2 or not ca:
            continue
        middle_inner, collar_outer = ma[1], ca[0]
        fit = collar_outer < middle_inner
        all_fit &= fit
        print(
            f"  fit @Y={y}: collar_outer {collar_outer:.0f} "
            f"< middle_inner {middle_inner:.0f} mm^2 "
            f"→ {'OK' if fit else 'INTERFERENCE'}"
        )
    msg = "OK — collar clears the middle inner wall" if all_fit else "CHECK"
    print(f"  FIT OVER SPAN (middle side): {msg}")

    # Rear-side sanity check — best-available clean station only (MESH-01
    # caveat: the true rear-side bonding span Y+203.4..+219.4 overlaps the
    # documented rear mesh defect band; Y=233 is the nearest clean station).
    rear = trimesh.load(os.path.join(here, REAR_STL))
    ra_rear = _loop_areas(rear, 233.0)
    cs_collar = _loop_areas(solid, 207.0)
    if len(ra_rear) >= 2 and cs_collar:
        rear_inner, collar_outer = ra_rear[1], cs_collar[0]
        fit = collar_outer < rear_inner
        print(
            f"  rear-side sanity @Y=233 (nearest clean station, NOT the true "
            f"bonding span — see MESH-01 caveat): collar_outer {collar_outer:.0f} "
            f"< rear_inner {rear_inner:.0f} mm^2 → {'OK' if fit else 'CHECK'}"
        )
    print(f"  wrote {out}")


if __name__ == "__main__":
    main()
