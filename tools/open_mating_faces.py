#!/usr/bin/env python3
# ============================================================================
# HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
#   Hull frame: X=+port, Y=+aft, Z=+dorsal; origin = SerenityAssembly world.
#
#   open_mating_faces.py  (2026-07-27; allowlist library Rev 2026-09-05)
#   --------------------------------------------------------------------------
#   Open the CAPPED fuselage-section mating faces so the internal splice collars
#   (generate_conforming_collars.py) can actually be installed and bond into an
#   open bore, as the design requires ("the four fuselage sections are open-ended
#   tubes joined by internal splice collars" — merge_cargo_interior.py / CLAUDE.md).
#
#   Why this is needed
#   --------------------------------------------------------------------------
#   The Blender source shells are CLOSED-capped at each fabrication-split face.
#   Every hull-shell pipeline (merge_cargo_interior.py, add_structural_features.py
#   process_head/process_middle, regen_rear_interior.py) ends in its own
#   finalize/repair pass that unconditionally trimesh.repair.fill_holes()s ANY
#   boundary loop a float32 STL round-trip or boolean seam leaves — it cannot
#   distinguish an intentional mating aperture from a genuine defect, so it
#   happily reseals the apertures too. Verified 2026-07-27 (mesh.contains +
#   section scans) and re-verified 2026-09-05 (all six faces, 0.05/0.2/0.5/1.0 mm
#   probes): every one of the six mating faces has been found re-capped by a
#   thin membrane at least once after its owning pipeline's own repair pass ran.
#
#   Permanent fix (2026-09-05): this file is now BOTH a standalone CLI (for an
#   ad-hoc audit/repair pass against the published STLs) and an IMPORTABLE
#   ALLOWLIST LIBRARY. `APERTURES` is the single source of truth for every
#   known-intentional mating aperture (name, owning file, cut method, station).
#   Each owning pipeline imports `ensure_open()` from this module and calls it
#   on its OWN in-memory mesh, for its OWN apertures, as the very last step
#   before writing the final STL — after whatever repair/finalize pass that
#   pipeline runs internally. This makes "the known apertures are open"
#   an enforced invariant at write time, independent of what any upstream
#   repair step did to them: no matter how a fill_holes() call upstream
#   re-caps a face, the mandatory tail call reopens it before the file ever
#   reaches disk. See:
#     - airframe/blender-scripts/merge_cargo_interior.py   (cargo_fwd, cargo_aft)
#     - airframe/blender-scripts/add_structural_features.py (head_aft, middle_fwd,
#       middle_aft)
#     - airframe/blender-scripts/regen_rear_interior.py     (rear_fwd)
#   The station names below match add_structural_features.MATING_PLANES keys
#   exactly, so a caller can look an aperture up by the same name it already
#   uses for its own cutters.
#
#   Two cap shapes ⇒ two methods
#   --------------------------------------------------------------------------
#   * "plug" — a THIN FLAT MEMBRANE at the section's Y-extreme (the bore is
#     full-size right up to the face). A half-space cut has nothing beyond the
#     face to remove, so we subtract a CAVITY PLUG — the inner-wall contour at a
#     clean station, grown a hair, extruded across the membrane — which removes
#     the membrane inside the bore footprint while leaving the 2 mm wall rim and
#     the face location unchanged. This is now the common case (5 of 6 faces).
#   * "flatcut" — a ROUNDED CLOSURE whose bore NECKS toward the tip (head_aft:
#     inner area 7815→6713 mm² over the last ~6 mm) and is sealed by a thin
#     single-loop membrane. A plug sized to the deep bore over-cuts the necked
#     near-face wall, so instead we FLAT-CUT at the first station whose bore is
#     genuinely open (2 loops, inner > MIN_BORE): the whole rounded closure
#     beyond that plane is removed, leaving a clean full-bore open face. The
#     mate plane therefore moves inboard to that station (reported at runtime;
#     the collar generator's JOINTS face for this joint is set to match).
#
#   Boolean of closed manifolds ⇒ still watertight (an open-ended thick tube is
#   watertight like a length of pipe — genus-1, not genus-0: the outer and inner
#   walls connect at the open rim instead of each being capped separately).
#   is_watertight()==True is therefore NOT sufficient on its own to prove a face
#   is genuinely open — is_capped() below (a point probe just inside the face)
#   is the real test; a solid disk cap is also watertight.
#
#   The HULL-FRAME marker is re-stamped so tools/bake_hull_frame.py still skips
#   the file. Idempotent: a face already open (mesh.contains False just inside)
#   is a no-op.
#
# Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  (design)
# AI-assist: Claude Opus 4.8 (Anthropic) — cavity-plug / flat-cut face opener,
#            allowlist library refactor 2026-09-05.
# License: CC BY 4.0 - creativecommons.org/licenses/by/4.0
# ============================================================================
"""Open (and keep open) the six fuselage-section mating-face apertures.

Library usage (preferred — call from the owning pipeline's own finalize step):

    import open_mating_faces as omf
    mesh, changed, note = omf.ensure_open(mesh, "cargo_fwd")
    mesh, changed, note = omf.ensure_open(mesh, "cargo_aft")

CLI usage (ad-hoc audit/repair against the published STLs on disk):

    python3 tools/open_mating_faces.py
"""

import os
import struct
import sys

import numpy as np
import trimesh
from manifold3d import Manifold, Mesh
from shapely.geometry import Polygon

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FUS = os.path.join(REPO, "airframe", "stls", "fuselage")
MARKER = b"SerenityUAV HULL-FRAME R1"
CAVITY_FLOOR = 1000.0  # mm^2 — ignore section loops smaller than a real bore
MIN_BORE = 3000.0      # mm^2 — a station's 2nd loop must exceed this to count "open"
PLUG_GROW = 0.5        # mm — grow the plug past the bore so the whole membrane goes
SCAN_STEP = 0.25       # mm — flat-cut open-station scan pitch
DEFAULT_PROBE = 0.1    # mm — is_capped() probe depth (see is_capped docstring)

# ---------------------------------------------------------------------------
# APERTURES — the allowlist. Single source of truth for every fuselage mating
# face that MUST be open (a real bore, not a disk) for the splice collars to
# install. Keys match add_structural_features.MATING_PLANES exactly.
#
#   rel_path:  path under airframe/stls/fuselage/ (for CLI use / reference)
#   method:    "plug" or "flatcut" (see module docstring)
#   face_y:    the nominal mating-plane hull Y station
#   keep_sign: +1 if the owning section occupies Y > face_y, -1 if Y < face_y
#   clean_y:   ("plug" only) a nearby Y with a known-clean 2-loop cross-section
#              to sample the plug's footprint from; None for "flatcut" (its
#              open station is auto-detected by first_open_station()).
# ---------------------------------------------------------------------------
APERTURES = {
    "head_aft": dict(
        rel_path="head_shell24_2mm_repaired.stl",
        method="flatcut", face_y=-71.2, keep_sign=-1, clean_y=None,
    ),
    "middle_fwd": dict(
        rel_path="middle_shell24_2mm_repaired.stl",
        method="plug", face_y=131.0, keep_sign=+1, clean_y=136.0,
    ),
    "cargo_fwd": dict(
        rel_path="cargo/cargo_sect_shell24_2mm_repaired.stl",
        # clean_y was -68.5 (1 mm inside the face) — still deep in a near-face
        # taper zone specific to this joint: at Y=-68.5 the inner-cavity loop
        # (the 2nd-largest section loop) is bbox X[-223.7,-164.7], only 45% of
        # the true full-width cavity (X[-226.3,-108.6] by Y=-63, confirmed
        # stable X[-227..-232, -103..-110] out to Y=-45) — i.e. it silently
        # dropped the PORT half (less-negative X) of the cavity. A plug built
        # from that station only reopened the stbd half, leaving cargo_fwd's
        # port side still capped and the head/cargo splice collar (which
        # samples this same cargo cross-section) tracing that same half-cut
        # line instead of the true joint profile (found 2026-09-05, reported
        # by the owner after the first aperture-allowlist fix). -63.0 is
        # comfortably past the taper (loop bbox already full-width by -67).
        method="plug", face_y=-69.5, keep_sign=+1, clean_y=-63.0,
    ),
    "cargo_aft": dict(
        rel_path="cargo/cargo_sect_shell24_2mm_repaired.stl",
        method="plug", face_y=129.0, keep_sign=-1, clean_y=127.5,
    ),
    "middle_aft": dict(
        rel_path="middle_shell24_2mm_repaired.stl",
        method="plug", face_y=202.3, keep_sign=-1, clean_y=201.0,
    ),
    "rear_fwd": dict(
        rel_path="rear_shell24_2mm_repaired.stl",
        method="plug", face_y=204.3, keep_sign=+1, clean_y=206.0,
    ),
}


def to_man(tm):
    return Manifold(Mesh(vert_properties=tm.vertices.astype(np.float32),
                         tri_verts=tm.faces.astype(np.uint32)))


def from_man(m):
    mm = m.to_mesh()
    out = trimesh.Trimesh(
        vertices=np.asarray(mm.vert_properties)[:, :3].astype(np.float64),
        faces=np.asarray(mm.tri_verts), process=False)
    out.merge_vertices()
    return out


def _loop_areas(mesh, y):
    s = mesh.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    out = []
    for loop in (s.discrete if s is not None else []):
        p = np.asarray(loop)[:, [0, 2]]
        x, z = p[:, 0], p[:, 1]
        out.append(0.5 * abs(np.dot(x, np.roll(z, -1)) - np.dot(z, np.roll(x, -1))))
    return sorted(out, reverse=True)


def inner_cavity(mesh, y):
    """2nd-largest section loop at station Y as a shapely (X,Z) Polygon."""
    s = mesh.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    polys = []
    for loop in (s.discrete if s is not None else []):
        p = Polygon(np.asarray(loop)[:, [0, 2]])
        if p.is_valid and p.area > CAVITY_FLOOR:
            polys.append(p.buffer(0))
    if len(polys) < 2:
        return None
    polys.sort(key=lambda p: p.area, reverse=True)
    return polys[1].simplify(0.4)


def _sample_points_in_poly(poly, n=5):
    """N (x, z) points spread across poly's X-extent, each snapped to the
    nearest point actually inside poly (a single centroid probe can sit
    entirely within one half of an asymmetric cavity and miss a partial cap
    on the other side — see is_capped()'s 2026-09-05 note)."""
    from shapely.geometry import Point
    from shapely.ops import nearest_points

    minx, _, maxx, _ = poly.bounds
    cz = poly.centroid.y
    pts = []
    for frac in np.linspace(0.1, 0.9, n):
        x = minx + frac * (maxx - minx)
        p = Point(x, cz)
        if not poly.contains(p):
            p = nearest_points(poly, p)[0]
        pts.append((p.x, p.y))
    return pts


def is_capped(mesh, face_y, keep_sign, probe=DEFAULT_PROBE, points=None):
    """True if the bore is solid `probe` mm inside the mating face (cap present)
    at ANY of `points` (each an (x, z) pair) — capped if any point tests solid.

    2026-09-05: was hard-coded to a 1.0 mm probe, which misses a thin
    (~0.5-1.0 mm) membrane sitting right at the face — cargo_fwd/cargo_aft/
    middle_aft/rear_fwd all tested "already open" at 1.0 mm while genuinely
    capped at 0.05-0.5 mm. Default lowered to 0.1 mm; still parameterised so a
    caller can widen it for a known deep rounded closure (flatcut case).

    2026-09-05 (later same day): a SINGLE probe point (previously always the
    whole-mesh vertex centroid) also missed a genuinely asymmetric partial
    cap — cargo_fwd's port half stayed capped after a fix verified only at
    the mesh centroid, which happened to land in the already-open stbd half.
    `points` defaults to that historical single-centroid behaviour when not
    given; callers checking a known cavity footprint (see ensure_open())
    should pass multiple points from _sample_points_in_poly() instead."""
    if points is None:
        points = [(mesh.vertices[:, 0].mean(), mesh.vertices[:, 2].mean())]
    probe_pts = [[x, face_y + keep_sign * probe, z] for x, z in points]
    return bool(np.any(mesh.contains(probe_pts)))


def first_open_station(mesh, face_y, keep_sign):
    """Scan inboard from the face; return the first Y whose bore is genuinely
    open (>=2 loops, 2nd loop > MIN_BORE)."""
    for k in range(1, 80):
        y = face_y + keep_sign * (SCAN_STEP * k)
        a = _loop_areas(mesh, y)
        if len(a) >= 2 and a[1] > MIN_BORE:
            return round(y, 3)
    return None


def _box(x0, x1, z0, z1, y0, y1):
    b = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    b.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
    return b


def open_flatcut(mesh, face_y, keep_sign):
    """Flat-cut the rounded closure off at the first open-bore station."""
    y_open = first_open_station(mesh, face_y, keep_sign)
    if y_open is None:
        return None, None
    b = mesh.bounds
    pad = 30.0
    if keep_sign < 0:  # keep Y < y_open ; remove Y > y_open
        cutter = _box(b[0][0] - pad, b[1][0] + pad, b[0][2] - pad, b[1][2] + pad,
                      y_open, b[1][1] + pad)
    else:              # keep Y > y_open ; remove Y < y_open
        cutter = _box(b[0][0] - pad, b[1][0] + pad, b[0][2] - pad, b[1][2] + pad,
                      b[0][1] - pad, y_open)
    return from_man(to_man(mesh) - to_man(cutter)), y_open


def open_plug(mesh, face_y, keep_sign, clean_y):
    """Subtract a cavity plug to remove a thin flat membrane at the face extreme."""
    cav = inner_cavity(mesh, clean_y)
    if cav is None:
        return None, None
    plug_poly = cav.buffer(PLUG_GROW).simplify(0.4)
    y0, y1 = (face_y - 0.6, face_y + 2.6) if keep_sign > 0 else (face_y - 2.6, face_y + 0.6)
    ex = trimesh.creation.extrude_polygon(plug_poly, height=y1 - y0)
    ex.apply_transform(np.array(
        [[1, 0, 0, 0], [0, 0, 1, y0], [0, 1, 0, 0], [0, 0, 0, 1.0]]))
    return from_man(to_man(mesh) - to_man(ex)), face_y


def ensure_open(mesh, name, probe=DEFAULT_PROBE):
    """Ensure the named mating aperture is genuinely open on `mesh` (in memory).

    This is the call every hull-shell pipeline should make on its OWN mesh,
    for its OWN aperture(s), as the very last step before writing the final
    STL — after any internal repair/finalize pass, so it does not matter
    whether that pass re-capped the face; this call re-opens it regardless.

    Returns (mesh, changed, note):
        mesh    — the (possibly modified) mesh; always a valid, merged mesh.
        changed — True if a cap was found and removed.
        note    — human-readable status, for the caller to print/log.

    Raises ValueError if `name` isn't in APERTURES, or RuntimeError if a cap
    was found but could not be verified as removed (caller should treat this
    as a hard failure, not silently continue — an unopened aperture blocks
    collar installation and is worse than a loud pipeline failure).
    """
    if name not in APERTURES:
        raise ValueError(
            f"unknown mating aperture {name!r} — known: {sorted(APERTURES)}"
        )
    ap = APERTURES[name]
    mesh = mesh.copy()
    mesh.merge_vertices()

    # Probe points: for "plug" apertures, sample across the FULL expected
    # cavity footprint (from clean_y), not just the mesh's whole-vertex
    # centroid — a single centroid point can sit entirely inside an already-
    # open half of an asymmetric cavity and miss a genuine partial cap on the
    # other side (found 2026-09-05: cargo_fwd's port half stayed capped after
    # a fix that verified clean at the mesh centroid, which happened to land
    # in the already-open stbd half). "flatcut" apertures keep the single
    # centroid probe — first_open_station() already scans the full loop area,
    # so open_flatcut() doesn't have the same asymmetric-footprint blind spot.
    points = None
    if ap["method"] == "plug":
        cav = inner_cavity(mesh, ap["clean_y"])
        if cav is not None:
            points = _sample_points_in_poly(cav.buffer(PLUG_GROW))

    if not is_capped(mesh, ap["face_y"], ap["keep_sign"], probe, points):
        return mesh, False, f"{name}: already open"

    if ap["method"] == "flatcut":
        opened, new_face = open_flatcut(mesh, ap["face_y"], ap["keep_sign"])
    else:
        opened, new_face = open_plug(
            mesh, ap["face_y"], ap["keep_sign"], ap["clean_y"]
        )
    if opened is None:
        raise RuntimeError(f"{name}: capped, but could not locate a clean open bore")

    opened.merge_vertices()
    ec = np.bincount(opened.edges_unique_inverse, minlength=len(opened.edges_unique))
    bnd, nm = int((ec == 1).sum()), int((ec > 2).sum())
    bodies = len(opened.split(only_watertight=False))
    # Re-derive points against the OPENED mesh's own cavity at new_face's
    # inboard side — the pre-fix cav above was sampled from the (possibly
    # still-capped) input mesh and may not reflect the post-fix geometry.
    verify_points = points
    if ap["method"] == "plug":
        post_cav = inner_cavity(opened, ap["clean_y"])
        if post_cav is not None:
            verify_points = _sample_points_in_poly(post_cav.buffer(PLUG_GROW))
    still_capped = is_capped(opened, new_face, ap["keep_sign"], probe, verify_points)
    ok = opened.is_watertight and bnd == 0 and nm == 0 and bodies == 1 and not still_capped
    if not ok:
        raise RuntimeError(
            f"{name}: reopen attempted but failed verification "
            f"(watertight={opened.is_watertight} bodies={bodies} boundary={bnd} "
            f"nonman={nm} still_capped={still_capped})"
        )
    note = f"{name}: was CAPPED — reopened at Y={new_face} (method={ap['method']})"
    return opened, True, note


def stamp_export(mesh, path, comp):
    tris = mesh.vertices[mesh.faces]
    e1, e2 = tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0]
    n = np.cross(e1, e2)
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    n = np.where(ln > 0, n / np.where(ln > 0, ln, 1.0), 0.0)
    rec = np.zeros(len(mesh.faces), dtype=np.dtype([("d", "<f4", (12,)), ("a", "<u2")]))
    rec["d"][:, 0:3] = n.astype("<f4")
    rec["d"][:, 3:12] = tris.reshape(len(mesh.faces), 9).astype("<f4")
    header = (MARKER + f" {comp} mating-face-open 2026-09-05".encode())[:80].ljust(80, b"\0")
    with open(path, "wb") as fh:
        fh.write(header)
        fh.write(struct.pack("<I", len(mesh.faces)))
        fh.write(rec.tobytes())


def main():
    """CLI: ad-hoc audit/repair pass against the published STLs on disk.

    This is a standalone convenience for auditing the current state of all
    six faces at once (e.g. after an out-of-band edit, or to verify the
    allowlist calls wired into each pipeline are doing their job). It is NOT
    the primary enforcement mechanism any more — that's ensure_open() called
    from each owning pipeline's own finalize step (see module docstring).
    A file this CLI touches is one whose pipeline-level enforcement should be
    investigated, since the invariant is supposed to hold without this pass.
    """
    # group by file so a file needing two apertures (cargo, middle) opens both
    # before writing once.
    by_file = {}
    for name, ap in APERTURES.items():
        by_file.setdefault(ap["rel_path"], []).append(name)

    all_ok = True
    for rel, names in by_file.items():
        path = os.path.join(FUS, rel)
        mesh = trimesh.load(path, process=False)
        mesh.merge_vertices()
        any_changed = False
        for name in names:
            ap = APERTURES[name]
            print(f"\n[{name}] {rel}  face Y={ap['face_y']}  method={ap['method']}")
            try:
                mesh, changed, note = ensure_open(mesh, name)
            except RuntimeError as exc:
                print(f"  ERROR: {exc}")
                all_ok = False
                continue
            print(f"  {note}")
            any_changed = any_changed or changed
        if any_changed:
            comp = os.path.basename(rel).replace(".stl", "")
            stamp_export(mesh, path, comp)
            print(f"  written + re-stamped -> {rel}")
    print(f"\n=== {'ALL FACES OPEN' if all_ok else 'REVIEW NEEDED'} ===")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
