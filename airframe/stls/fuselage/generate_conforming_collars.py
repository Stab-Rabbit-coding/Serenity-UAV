#!/usr/bin/env python3
# ============================================================================
# HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11). See CLAUDE.md.
#   Hull frame: X=+port, Y=+aft, Z=+dorsal; origin = SerenityAssembly world.
#   These parts are generated DIRECTLY in hull frame (identity placement).
#
#   generate_conforming_collars.py  (Rev R3, 2026-07-21)
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
#   Why Rev R3 (continuous-bridge nested laps)
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
#     * PROFILE  = fwd_lap ∩ aft_lap — ⊆ BOTH sections' cavities at every sampled
#                  station — extruded as the snug LAP profile over the two deep
#                  insertion zones.
#     * WAIST    = PROFILE inset a further WAIST_INSET mm, over the joint region
#                  [fwd_face−WAIST_MARGIN, aft_face+WAIST_MARGIN].  The flat OPEN
#                  mating faces are pipe rims: the bore closes toward the wall over
#                  the last ~1.5 mm before each cut, which the lap sampling (it
#                  drops those ragged one-loop stations) cannot see, so a
#                  constant-profile prism would poke ~1–1.8 mm into that rim.  A
#                  uniform bigger bond gap does NOT fix it (the poke is a
#                  Y-localised cliff, not a radial oversize — verified 2026-07-21:
#                  gap 0.6→1.5 barely changed it) and a shell CLIP severs the thin
#                  2 mm wall.  The waist steps the collar inward across both rims
#                  instead, so collar∩shell ≈ 0.  The three zones are NESTED
#                  (waist ⊆ profile) → the collar is ONE body by construction and
#                  needs no shell subtraction (immune to any shell mesh defect).
#   Where the two sections are similar (head/cargo, middle/rear) the lap hugs both
#   walls — a tight 2-wall contact annulus on both sides.  Where they differ
#   (cargo/middle: cargo ≈ 1.3× the middle cross-section) the lap is the NARROWER
#   (middle) cavity, so the collar is snug in the middle and beds into the wider
#   cargo bore on a thicker West-System-406 fillet — the documented asymmetric-fit
#   pattern, acceptable because the joint is not strength-limited (§7.4).
#
#   Requires the sections to have been regenerated with FLAT OPEN mating faces
#   (merge_cargo_interior.py [cargo], add_structural_features.py [head/middle],
#   regen_rear_interior.py [rear]); the section Y-extents supply the face planes.
#
#   Supersedes the three retired single-cross-section generators
#   (generate_head_cargo_splice_collar.py, generate_cargo_middle_splice_collar.py,
#   generate_middle_rear_splice_collar.py), which extruded ONE contour straight
#   across the joint and poked through the tapering shell ends.
#
# Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  (design)
# AI-assist: Claude Opus 4.8 (Anthropic) — nested-lap continuous-bridge
#            generator, 2026-07-21
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
BOND_GAP = 1.2        # mm — lap slip-fit inset from the section inner wall over
#                       the deep insertion (West-System-406 fills 1–2 mm).
WAIST_INSET = 1.6     # mm — extra inset of the joint-region "waist" past BOND_GAP,
#                       to clear the closing near-face pipe-rim bore (a shell clip
#                       would sever the 2 mm wall; verified 2026-07-21).  MUST stay
#                       < WALL_T so the waist ring and lap ring overlap (else the
#                       collar splits into disconnected zones — verified 2026-07-21
#                       at WAIST_INSET=2.5).  BOND_GAP+WAIST_INSET (=2.8 mm) exceeds
#                       the worst measured near-face cavity closure (~2.4 mm), so
#                       collar∩shell ≈ 0; WALL_T−WAIST_INSET (=0.4 mm) is the ring
#                       overlap that keeps the collar a single body.
WAIST_MARGIN = 2.0    # mm — how far the waist reaches into each section past the
#                       mating face (covers the ~1.5 mm unsampled near-face band).
WALL_T = 2.0          # mm — collar radial wall thickness
INSERT = 8.0          # mm — collar insertion depth into EACH section
FACE_MARGIN = 1.5     # mm — stop sampling this short of the mating face (lip)
STEP = 0.5            # mm — cavity sampling pitch across the insertion span
CAVITY_FLOOR = 1000.0  # mm^2 — reject loops smaller than a real hull cavity
SIMPLIFY = 0.4        # mm — contour simplification tolerance
FIT_TOL = 50.0        # mm^3 — max acceptable collar∩shell interference

# joint: (name, fwd_stl, aft_stl, fwd_face_Y, aft_face_Y, out_stl)
#   fwd section occupies Y <= fwd_face_Y ; aft section occupies Y >= aft_face_Y.
#   Face Y values are the baked section extents (the flat open mating faces).
JOINTS = [
    (
        "head/cargo",
        "head_shell24_2mm_repaired.stl",
        "cargo/cargo_sect_shell24_2mm_repaired.stl",
        -71.2,
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
    """Build one continuous WAISTED splice collar (snug lap zones + a stepped-in
    waist across the joint) — a single body by construction, no shell subtraction.

    profile = fwd_lap ∩ aft_lap ⊆ BOTH sections' cavities at every sampled station.
    It is extruded as the snug LAP over the two deep insertion zones and inset a
    further WAIST_INSET as the WAIST over the joint region (which brackets both
    flat OPEN mating faces).  The waist clears the closing near-face pipe-rim bore
    that the lap sampling cannot see; the three zones nest (waist ⊆ profile) so the
    collar is ONE body.  collar∩shell ≈ 0 is verified by the boolean below.  Where
    the sections differ (cargo/middle) the lap is the NARROWER (middle) cavity, so
    the collar beds into the wider cargo bore on a thicker West-System-406 fillet
    (asymmetric-fit; joint not strength-limited, §7.4).  Collar + butted faces
    secure and register the sections (the joint boss pins were removed 2026-07-06;
    final concentric alignment is set on the assembly jig at bond-up)."""
    fwd_cav, nf = lap_profile(fwd, fwd_face - INSERT, fwd_face - FACE_MARGIN)
    aft_cav, na = lap_profile(aft, aft_face + FACE_MARGIN, aft_face + INSERT)
    fwd_prof = _largest(fwd_cav.buffer(-BOND_GAP))
    aft_prof = _largest(aft_cav.buffer(-BOND_GAP))
    profile = _largest(fwd_prof.intersection(aft_prof))
    if profile is None or profile.area < 500.0:
        got = 0.0 if profile is None else profile.area
        raise RuntimeError(f"laps overlap only {got:.0f} mm^2 — cannot bridge")
    waist = _largest(profile.buffer(-WAIST_INSET))
    if waist is None or waist.area < 500.0:
        raise RuntimeError("waist profile collapsed — WAIST_INSET too large")

    tight = 100.0 * profile.area / min(fwd_prof.area, aft_prof.area)
    print(
        f"  fwd_lap area={fwd_prof.area:.0f} ({nf} sta)  "
        f"aft_lap area={aft_prof.area:.0f} ({na} sta)  "
        f"lap profile={profile.area:.0f} ({tight:.0f}% of narrower lap)  "
        f"waist={waist.area:.0f}"
    )

    # three nested Y zones: fwd lap | waist (across the joint) | aft lap
    y_lo, y_hi = fwd_face - INSERT, aft_face + INSERT
    w0, w1 = fwd_face - WAIST_MARGIN, aft_face + WAIST_MARGIN
    zones = [
        (profile, y_lo, w0),   # fwd lap (snug, deep)
        (waist, w0, w1),       # waist across both mating-face rims + the gap
        (profile, w1, y_hi),   # aft lap (snug, deep)
    ]
    outer = None
    inner = None
    for poly, y0, y1 in zones:
        if y1 - y0 <= 0:
            continue
        o = _extrude(poly, y0, y1)
        h = _extrude(_largest(poly.buffer(-WALL_T)), y0, y1)
        outer = o if outer is None else outer + o
        inner = h if inner is None else inner + h
    collar = from_man(outer - inner)
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
    print("=== generate_conforming_collars.py  Rev R3  2026-07-21 ===")
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

        ihf, nfwd = shell_intersection_vol(collar, fwd_rel)
        iaf, naft = shell_intersection_vol(collar, aft_rel)
        fwd_ok = ihf is not None and ihf < FIT_TOL
        aft_ok = iaf is not None and iaf < FIT_TOL
        print(
            f"  collar∩fwd={ihf if ihf is None else round(ihf)} ({nfwd})  "
            f"collar∩aft={iaf if iaf is None else round(iaf)} ({naft}) mm^3"
        )
        ok = (
            collar.is_watertight
            and bodies == 1
            and int((ec == 1).sum()) == 0
            and int((ec > 2).sum()) == 0
            and fwd_ok
            and aft_ok
        )
        all_ok &= ok
        print(f"  RESULT: {'PASS' if ok else 'CHECK'}")
    print(f"\n=== {'ALL COLLARS PASS' if all_ok else 'REVIEW NEEDED'} ===")


if __name__ == "__main__":
    main()
