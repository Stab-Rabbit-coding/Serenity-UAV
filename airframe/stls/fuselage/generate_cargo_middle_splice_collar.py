#!/usr/bin/env python3
# ============================================================================
# HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
#   Hull frame (canonical for ALL design artifacts): X = +port (left),
#   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
#   world origin.  This part is generated DIRECTLY in hull frame (it spans the
#   cargo/middle joint at hull Y ~ +131 mm); identity placement in assembly.
#
#   cargo_middle_splice_collar  (Rev R1, 2026-07-03)
#   --------------------------------------------------------------------------
#   Internal bonded splice collar securing the CARGO section to the MIDDLE
#   section across the fabrication-split joint at hull Y ~ +131 mm.  Mirrors
#   the first-principles method used for the head/cargo joint
#   (generate_head_cargo_splice_collar.py, docs/structural_analysis.md S7.3;
#   TODO.md S1.1.1.0b "Cargo/Middle splice analysis + design").
#
#   Why this part exists
#   --------------------------------------------------------------------------
#   Cargo/middle is a fabrication split, but it is NOT load-free: everything
#   aft of it (middle shell + rear shell + their avionics/EDF allocation) is
#   cantilevered from this joint under maneuver, landing, and crash loads,
#   same as the head/cargo joint reacted the forward head cantilever.  The
#   three Ø3.2 mm boss pins at this joint (structural_analysis.md S7.2 Joint 2)
#   are alignment dowels only (same shallow-engagement limitation documented
#   for Joint 1) and a bare 2 mm-shell butt bond loads the bondline in peel,
#   not shear.
#
#   Cross-section survey (trimesh, this repo's baked STLs, 2026-07-03):
#   the CARGO aft face and the MIDDLE fwd face are BOTH closed sections at
#   this joint -- the middle section's ventral horseshoe opening does not
#   begin until further aft (loops separate into outer-ring + inner-neck only
#   past hull Y ~ +175 mm; at Y = 131-141 mm the whole middle cross-section is
#   still one closed tube, confirmed by convex-hull-area ratio 0.98 at
#   Y = 137 mm vs 0.88-0.96 further aft).  A FULL RING collar (not a
#   partial/inner-neck-only sleeve) is therefore feasible here, exactly as at
#   the head/cargo joint.
#
#   Load check (ultimate, joint FOS 4.0 per structural_analysis.md S3/S7.3):
#   mass aft of this joint = middle shell (295 g) + rear shell (314 g) + the
#   same "~300 g avionics/wiring per section" allocation already used in S4.3
#   for the analogous head- and rear-cantilever checks = 1209 g.  Arm = half
#   the aft-of-joint fuselage length (uniform-distributed-load convention,
#   S4.3) = (384.3 - 131.1) / 2 = 126.6 mm.
#     2g maneuver x4.0 = 8.0g:  F = 94.9 N   M = 12 010 N*mm
#     2.5g landing x4.0 = 10.0g: F = 118.6 N  M = 15 020 N*mm
#     9g crash x1.5 = 13.5g:    F = 160.1 N  M = 20 260 N*mm
#   Real section modulus computed from the actual digitized middle cross-
#   section at Y = 137 mm (thin-wall line integral about the lateral bending
#   axis, wall_t = 2 mm): perimeter 454 mm, S_x = 31 984 mm^3.  Peak fibre
#   stress at 9g crash = 20260 / 31984 = 0.63 MPa -- far below the CF-PETG/
#   epoxy allowable (~5 MPa, S7.3).  NOT strength-limited, same conclusion as
#   the head/cargo joint; the governing requirements are peel resistance,
#   alignment, and anti-ovalisation of the thin section per the CLAUDE.md
#   fabrication standard (2-wall contact annulus + positive-stop shoulder).
#
#   Design -- internal bonded splice collar (PRINT-CARGO-MIDDLE-COLLAR).
#   Profile = MIDDLE inner-wall contour at hull Y = +137 mm (a clean region
#   5.9 mm aft of the joint, inside the middle section, before the horseshoe
#   opens further aft) inset by a 2 mm bond gap, 2 mm wall.  L = 16 mm
#   (8 mm into each section, centred on the joint at hull Y = +131.1 mm --
#   the midpoint of the measured cargo aft face, Y = +131.74 mm, and middle
#   fwd face, Y = +130.40 mm).  Middle is the narrower of the two sections at
#   this joint (inner area ~14 300 mm^2 vs cargo's ~19 000 mm^2 at the nearest
#   clean cargo station, Y = +122 mm), so the collar (sized to middle) slips
#   into cargo with a larger, epoxy-filled gap -- same asymmetric-fit pattern
#   as the head/cargo collar (built to the narrower HEAD profile).
#
#   MESH-01 caveat: the cargo shell (airframe/stls/fuselage/cargo/
#   cargo_sect_shell24_2mm_repaired.stl) is NOT watertight as of this writing
#   (TODO.md MESH-01; 41 disconnected bodies) and the defect band overlaps
#   this collar's cargo-side bonding span (hull Y +123.7..+139.7).  The
#   nearest clean cargo cross-section is Y = +122 mm (10 mm forward of the
#   joint, area 18955-20205 mm^2), used here only as a size/fit sanity check,
#   not a fit verification over the true bonding span on the cargo side.
#   Re-verify the cargo-side fit once MESH-01 is resolved for cargo.
#
#   Bond: West System 105/206 thickened with 406 colloidal silica.  Double-lap
#   shear area ~= 454 mm perim x 8 mm x 2 sides ~= 7264 mm^2; worst-case
#   bending couple tension (~160 N at 9g crash over a ~70 mm lever) gives bond
#   shear << 0.1 MPa -> FOS > 100 on the bond; sized by handling/printability
#   (~17 g), not stress -- same governing criterion as S7.3.
#
# Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
# License: CC BY 4.0 - creativecommons.org/licenses/by/4.0
# Print spec:  CF-PETG, 0.15 mm layer, 4 perimeters, 100% infill (thin ring;
#              perimeters fill the 2 mm wall).  Bond with West System 105/206.
# ============================================================================
"""generate_cargo_middle_splice_collar.py — Rev R1 (2026-07-03)

Generate the internal cargo/middle splice collar (hull frame) from the baked
middle shell inner contour.

Output: cargo_middle_splice_collar.stl
Run:    python3 generate_cargo_middle_splice_collar.py
"""

import os

import numpy as np
import trimesh
from shapely.geometry import Polygon

MIDDLE_STL = "middle_shell24_2mm_repaired.stl"  # sibling in airframe/stls/fuselage/
CARGO_STL = "cargo/cargo_sect_shell24_2mm_repaired.stl"  # for fit sanity check only
SAMPLE_Y = 137.0  # mm — clean middle inner-contour station for the profile
JOINT_Y = 131.1  # mm — cargo/middle mate plane (cargo aft +131.74, middle fwd +130.40)
COLLAR_L = 16.0  # mm — total length (8 mm into each section)
BOND_GAP = 2.0  # mm — bond gap (collar outer inset from middle inner wall).
#                       Sized so the collar clears the skin inner wall everywhere
#                       over the bonding span. Bonded with West System 105/206
#                       thickened with 406 colloidal silica; the boss dowel pins
#                       do the concentric piloting, not the collar.
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

    out = os.path.join(here, "cargo_middle_splice_collar.stl")
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

    print("cargo/middle splice collar (Rev R1, hull frame):")
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
    for y in (133.0, 135.0, 139.0):
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

    # Cargo-side sanity check — best-available clean station only (MESH-01
    # caveat: the true cargo-side bonding span Y+123.7..+139.7 overlaps the
    # documented cargo mesh defect band; Y=122 is the nearest clean station).
    cargo = trimesh.load(os.path.join(here, CARGO_STL))
    ca_cargo = _loop_areas(cargo, 122.0)
    cs_collar = _loop_areas(solid, 133.0)
    if len(ca_cargo) >= 2 and cs_collar:
        cargo_inner, collar_outer = ca_cargo[1], cs_collar[0]
        fit = collar_outer < cargo_inner
        print(
            f"  cargo-side sanity @Y=122 (nearest clean station, NOT the true "
            f"bonding span — see MESH-01 caveat): collar_outer {collar_outer:.0f} "
            f"< cargo_inner {cargo_inner:.0f} mm^2 → {'OK' if fit else 'CHECK'}"
        )
    print(f"  wrote {out}")


if __name__ == "__main__":
    main()
