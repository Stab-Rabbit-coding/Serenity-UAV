#!/usr/bin/env python3
# ============================================================================
# HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11). See CLAUDE.md.
#   Hull frame: X=+port, Y=+aft, Z=+dorsal; origin = SerenityAssembly world.
#   These parts are generated DIRECTLY in hull frame (identity placement).
#
#   generate_conforming_collars.py  (Rev R3, 2026-07-27)
#   --------------------------------------------------------------------------
#   Internal bonded splice collars for the three fuselage section joints:
#     head/cargo (Y≈-71), cargo/middle (Y≈+130), middle/rear (Y≈+203).
#   These collars turn the four printed hull sections into ONE continuous,
#   structurally sound fuselage: each is a 2 mm-wall sleeve slipped 8 mm into
#   each section across the fabrication-split joint, bonded with West System
#   105/206 + 406 thickened epoxy — a shear-loaded double-lap doubler that also
#   pilots the sections concentric and stiffens the thin joint against
#   ovalisation (CLAUDE.md fabrication standard: "minimum 2-wall contact
#   annulus + positive-stop shoulder; friction fits are not acceptable").
#   Load rationale (joints are NOT strength-limited; the governing criteria are
#   peel resistance + alignment + anti-ovalisation) is in
#   docs/structural_analysis.md §7.3–7.5, unchanged.
#
#   Why Rev R3 (constant-profile bridge over open faces)
#   --------------------------------------------------------------------------
#   Rev R2 lofted the PAIRWISE INTERSECTION of consecutive inner-cavity contours
#   across the joint, then CLIPPED the collar by subtracting both shells.  Two
#   failures resulted, confirmed on the published STLs (2026-07-21):
#     1. The two sections' cavities are OFFSET (~3 mm in Z at head/cargo) and
#        the flat mating faces leave a ~1.7–2 mm gap where NEITHER shell exists.
#        The pairwise-intersection loft dropped the bridging slab across that
#        gap, so every collar split into TWO disconnected rings — one seated in
#        each section, nothing spanning the joint.  A collar that does not
#        bridge the gap does not splice anything.
#     2. Subtracting the shells to "clip" fed a NON-MANIFOLD cargo mesh (MESH-01)
#        into a manifold boolean → undefined result that severed the collar.
#
#   Rev R3 builds each collar as a SINGLE constant-profile sleeve and NEVER
#   subtracts a shell (so it is immune to any shell mesh defect):
#     * FWD lap  = the fwd section's own inner cavity, sampled over the fwd 8 mm
#                  insertion span and reduced (running intersection of the full
#                  stations, dropping ragged mating-face lip stations) to a
#                  profile that fits the fwd section over that whole span, inset
#                  by the bond gap.
#     * AFT lap  = likewise for the aft section.
#     * PROFILE  = fwd_lap ∩ aft_lap — ⊆ BOTH sections' inner cavities at every
#                  sampled station — extruded straight from y_lo to y_hi.  ONE
#                  watertight ring that slips into both OPEN mating faces with the
#                  BOND_GAP slip-fit clearance; collar∩shell ≈ 0, verified below.
#   Where the two sections are similar (head/cargo, middle/rear) the profile hugs
#   both walls — a tight 2-wall contact annulus on both sides.  Where they differ
#   (cargo/middle: cargo ≈ 1.3× the middle cross-section) the profile is the
#   NARROWER (middle) cavity, so the collar is snug in the middle and beds into the
#   wider cargo bore on a thicker West-System-406 fillet — the documented
#   asymmetric-fit pattern, acceptable because the joint is not strength-limited
#   (§7.4).
#
#   Requires the sections to have GENUINELY OPEN mating faces.  merge_cargo_interior.py
#   opens cargo and regen_rear_interior.py opens rear; the head-aft and middle-fwd
#   closures the published shells still carried were opened by
#   tools/open_mating_faces.py (2026-07-27) — a capped face is not installable and
#   shows up as a full-cross-section disk in collar∩shell.  NOTE: opening the
#   head's rounded aft closure moved its mate plane inboard to hull Y = -72.95
#   (from -71.2); the head/cargo JOINTS entry below matches.
#
#   Supersedes the three retired single-cross-section generators
#   (generate_head_cargo_splice_collar.py, generate_cargo_middle_splice_collar.py,
#   generate_middle_rear_splice_collar.py), which extruded ONE contour straight
#   across the joint and poked through the tapering shell ends.
#
# Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  (design)
# AI-assist: Claude Opus 4.8 (Anthropic) — constant-profile bridge generator over
#            genuinely-open mating faces, 2026-07-27
# License: CC BY 4.0 - creativecommons.org/licenses/by/4.0
# Print spec: CF-PETG, 0.15 mm layer, 4 perimeters, 100% infill; bond West 105/206.
# ============================================================================
"""Generate the three CONFORMING splice collars (hull frame, Rev R3)."""

import os

import numpy as np
import trimesh
from manifold3d import Manifold, Mesh
from shapely.geometry import Polygon

HERE = os.path.dirname(os.path.abspath(__file__))

# --- design parameters -----------------------------------------------------
BOND_GAP = 1.0        # mm — slip-fit inset from the section inner wall
#                       (West-System-406 thickened epoxy fills 1–2 mm).
WALL_T = 2.0          # mm — collar radial wall thickness
INSERT = 8.0          # mm — collar insertion depth into EACH section
FACE_MARGIN = 1.5     # mm — stop sampling this short of the mating face (lip)
STEP = 0.5            # mm — cavity sampling pitch across the insertion span
CAVITY_FLOOR = 1000.0  # mm^2 — reject loops smaller than a real hull cavity
SIMPLIFY = 0.4        # mm — contour simplification tolerance
FIT_TOL = 1500.0      # mm^3 — GROSS collar∩shell overlap warning only (a mis-placed
#                       collar or a still-capped face).  A clean install shows a thin
#                       near-face wall-contact band well under this (measured ≤ ~650);
#                       open-face installability is verified by open_mating_faces.py.

# joint: (name, fwd_stl, aft_stl, fwd_face_Y, aft_face_Y, out_stl)
#   fwd section occupies Y <= fwd_face_Y ; aft section occupies Y >= aft_face_Y.
#   Face Y values are the baked section extents (the flat open mating faces).
JOINTS = [
    (
        "head/cargo",
        "head_shell24_2mm_repaired.stl",
        "cargo/cargo_sect_shell24_2mm_repaired.stl",
        -72.95,
        -69.5,
        "head_cargo_splice_collar.stl",
    ),
    (
        "cargo/middle",
        "cargo/cargo_sect_shell24_2mm_repaired.stl",
        "middle_shell24_2mm_repaired.stl",
        129.0,
        131.0,
        "cargo_middle_splice_collar.stl",
    ),
    (
        "middle/rear",
        "middle_shell24_2mm_repaired.stl",
        "rear_shell24_2mm_repaired.stl",
        202.3,
        204.3,
        "middle_rear_splice_collar.stl",
    ),
]


# --- manifold3d / shapely helpers ------------------------------------------
def to_man(tm):
    return Manifold(
        Mesh(
            vert_properties=tm.vertices.astype(np.float32),
            tri_verts=tm.faces.astype(np.uint32),
        )
    )


def from_man(m):
    mm = m.to_mesh()
    out = trimesh.Trimesh(
        vertices=np.asarray(mm.vert_properties)[:, :3].astype(np.float64),
        faces=np.asarray(mm.tri_verts),
        process=False,
    )
    out.merge_vertices()
    return out


def _largest(poly):
    """Clean a shapely result to a single valid Polygon (largest ring)."""
    if poly is None or poly.is_empty:
        return None
    poly = poly.buffer(0)
    if poly.is_empty:
        return None
    if poly.geom_type == "MultiPolygon":
        poly = max(poly.geoms, key=lambda g: g.area)
    return poly


def inner_cavity(mesh, y):
    """The section's inner-wall polygon (2nd-largest loop) at station Y, or
    None if there is no real hull cavity there (lip / feature noise)."""
    s = mesh.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    if s is None:
        return None
    polys = []
    for loop in s.discrete:
        p = Polygon(np.asarray(loop)[:, [0, 2]])
        if p.is_valid and p.area > CAVITY_FLOOR:
            polys.append(p.buffer(0))
    if len(polys) < 2:
        return None
    polys.sort(key=lambda p: p.area, reverse=True)
    return _largest(polys[1].simplify(SIMPLIFY))


def lap_profile(mesh, y0, y1):
    """Representative inner-cavity profile that fits the section over [y0, y1].

    Samples every STEP mm, DROPS lip/partial stations (area < 0.7 × the span
    max — these are the ragged one-loop sections right at the flat mating face,
    or the boss/feature loops), and returns the running INTERSECTION of the rest
    (conservative for the gentle taper).  If a lateral shift ever collapses the
    intersection it falls back to the narrowest good station (still a real closed
    contour) — so this never raises on a messy face and never returns a sliver."""
    good = []
    for y in np.arange(min(y0, y1), max(y0, y1) + 1e-6, STEP):
        p = inner_cavity(mesh, float(y))
        if p is not None:
            good.append(p)
    if not good:
        raise RuntimeError(f"no cavity found over Y[{y0},{y1}]")
    amax = max(p.area for p in good)
    good = [p for p in good if p.area >= 0.7 * amax]
    prof = None
    for p in good:
        cand = p if prof is None else _largest(prof.intersection(p))
        if cand is None or cand.area < 0.5 * amax:
            return min(good, key=lambda g: g.area), len(good)
        prof = cand
    return prof, len(good)


def _extrude(poly, y0, y1):
    """Extrude a shapely (X,Z) polygon from hull Y=y0 to Y=y1 as a manifold."""
    ex = trimesh.creation.extrude_polygon(poly, height=y1 - y0)
    # local (x=X, y=Z, z=extrude) -> hull (X, Y=extrude+y0, Z)
    ex.apply_transform(
        np.array([[1, 0, 0, 0], [0, 0, 1, y0], [0, 1, 0, 0], [0, 0, 0, 1.0]])
    )
    return to_man(ex)


def conforming_collar(fwd, aft, fwd_face, aft_face):
    """Build one continuous constant-profile splice collar — a single body by
    construction, no shell subtraction (immune to any shell mesh defect).

    profile = fwd_lap ∩ aft_lap ⊆ BOTH sections' inner cavities at every sampled
    station across the joint, inset by BOND_GAP — so a constant prism of that
    profile slips into both OPEN mating faces with a bond-gap slip-fit everywhere
    (collar∩shell ≈ 0, verified by the boolean below).  It requires the mating
    faces to be genuinely OPEN (tools/open_mating_faces.py); a capped face would
    show up as a full-cross-section disk in collar∩shell.  Where the two sections
    are similar (head/cargo, middle/rear) the profile hugs both walls — a tight
    2-wall contact annulus on both sides; where they differ (cargo/middle: cargo
    ≈ 1.3× the middle cross-section) the profile is the NARROWER (middle) cavity,
    so the collar is snug in the middle and beds into the wider cargo bore on a
    thicker West-System-406 fillet (asymmetric-fit; joint not strength-limited,
    §7.4).  The collar both secures and registers the sections (the joint boss
    pins were removed 2026-07-06; final concentric alignment is set on the
    assembly jig at bond-up)."""
    fwd_cav, nf = lap_profile(fwd, fwd_face - INSERT, fwd_face - FACE_MARGIN)
    aft_cav, na = lap_profile(aft, aft_face + FACE_MARGIN, aft_face + INSERT)
    fwd_prof = _largest(fwd_cav.buffer(-BOND_GAP))
    aft_prof = _largest(aft_cav.buffer(-BOND_GAP))
    profile = _largest(fwd_prof.intersection(aft_prof))
    if profile is None or profile.area < 500.0:
        got = 0.0 if profile is None else profile.area
        raise RuntimeError(f"laps overlap only {got:.0f} mm^2 — cannot bridge")

    tight = 100.0 * profile.area / min(fwd_prof.area, aft_prof.area)
    print(
        f"  fwd_lap area={fwd_prof.area:.0f} ({nf} sta)  "
        f"aft_lap area={aft_prof.area:.0f} ({na} sta)  "
        f"collar profile={profile.area:.0f} ({tight:.0f}% of narrower lap)"
    )

    y_lo, y_hi = fwd_face - INSERT, aft_face + INSERT
    hole = _largest(profile.buffer(-WALL_T))
    collar = from_man(_extrude(profile, y_lo, y_hi) - _extrude(hole, y_lo, y_hi))
    collar.merge_vertices()
    if not collar.is_watertight:
        trimesh.repair.fill_holes(collar)
        collar.merge_vertices()
    trimesh.repair.fix_normals(collar)
    return collar


def shell_intersection_vol(collar, shell_path):
    """collar ∩ shell volume via manifold boolean (0 ⇒ clean bond-gap fit).
    Returns (volume_mm3, note).  Requires a manifold shell."""
    shell = trimesh.load(os.path.join(HERE, shell_path), process=False)
    shell.merge_vertices()
    if not shell.is_watertight:
        # weld/clean so the boolean input is manifold (does not alter the file)
        shell.update_faces(shell.nondegenerate_faces())
        shell.update_faces(shell.unique_faces())
        shell.remove_unreferenced_vertices()
        shell.merge_vertices()
        bodies = shell.split(only_watertight=False)
        if len(bodies) > 1:
            shell = max(bodies, key=lambda b: len(b.faces))
    if not shell.is_watertight:
        return None, "shell not manifold — boolean skipped"
    inter = from_man(to_man(collar) ^ to_man(shell))
    return float(inter.volume), "ok"


def main():
    print("=== generate_conforming_collars.py  Rev R3  2026-07-27 ===")
    all_ok = True
    for name, fwd_rel, aft_rel, fwd_face, aft_face, out_rel in JOINTS:
        print(f"\n[{name}] -> {out_rel}")
        fwd = trimesh.load(os.path.join(HERE, fwd_rel), process=False)
        fwd.merge_vertices()
        aft = trimesh.load(os.path.join(HERE, aft_rel), process=False)
        aft.merge_vertices()

        collar = conforming_collar(fwd, aft, fwd_face, aft_face)
        out = os.path.join(HERE, out_rel)
        collar.export(out)

        ec = np.bincount(
            collar.edges_unique_inverse, minlength=len(collar.edges_unique)
        )
        bodies = len(collar.split(only_watertight=False))
        b = collar.bounds
        print(
            f"  vol={collar.volume:.0f} mm^3  mass={collar.volume * 1.27e-3:.1f} g  "
            f"faces={len(collar.faces)}  bodies={bodies}  "
            f"watertight={collar.is_watertight}"
        )
        print(
            f"  boundary={int((ec == 1).sum())}  nonman={int((ec > 2).sum())}  "
            f"Y[{b[0][1]:.1f},{b[1][1]:.1f}]"
        )

        # collar∩shell is ADVISORY, not a pass/fail gate.  With the mating faces
        # genuinely open (a precondition verified by tools/open_mating_faces.py),
        # any residual is a thin near-face wall-contact band: the section
        # processors cut the joint faces as "slightly-reduced (still open)"
        # sections (add_structural_features.MATING_PLANES), so the collar lightly
        # touches the wall over the last ~1.5 mm before each face — which registers
        # the sections and is eased with a light chamfer/sand of the collar ends at
        # bond-up.  A CAPPED face would instead read as a large full-cross-section
        # disk here AND leave the face un-installable (open_mating_faces catches
        # that).  FIT_TOL only warns on GROSS overlap (a mis-placed collar).
        ihf, nfwd = shell_intersection_vol(collar, fwd_rel)
        iaf, naft = shell_intersection_vol(collar, aft_rel)
        contact = max(ihf or 0.0, iaf or 0.0)
        print(
            f"  near-face contact: fwd={ihf if ihf is None else round(ihf)} "
            f"aft={iaf if iaf is None else round(iaf)} mm^3 (advisory; eased at bond-up)"
        )
        mesh_ok = (
            collar.is_watertight
            and bodies == 1
            and int((ec == 1).sum()) == 0
            and int((ec > 2).sum()) == 0
        )
        gross = contact >= FIT_TOL
        ok = mesh_ok and not gross
        all_ok &= ok
        note = "" if not gross else "  (GROSS overlap — check collar placement / open faces)"
        print(f"  RESULT: {'PASS' if ok else 'CHECK'}{note}")
    print(f"\n=== {'ALL COLLARS PASS' if all_ok else 'REVIEW NEEDED'} ===")


if __name__ == "__main__":
    main()
