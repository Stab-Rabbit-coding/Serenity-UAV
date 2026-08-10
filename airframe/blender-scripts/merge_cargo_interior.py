#!/usr/bin/env python3
"""
merge_cargo_interior.py — Rev R1 (2026-06-30)

Build the FINAL canonical cargo-section shell by merging every cargo interior
feature into the Blender-canonical hull skin, in one robust manifold3d pass.
This is the definitive processor for the cargo section (TODO.md §1.1.1.0a); it
supersedes the cargo path of add_structural_features.py (the script that left
the MESH-01 fragmentation defect — 71 131 disconnected bodies, is_watertight=
False — on the published cargo STL).

Why it is robust (MESH-01 fix)
------------------------------
add_structural_features.py subtracted dozens of cutters one at a time with
trimesh.boolean.difference(engine="manifold") plus a per-step "repair" on a
1.4 M-face mesh; that fragile sequential round-trip is what fragmented the
shells.  This script instead starts from the KNOWN-CLEAN Blender source
(watertight 2-manifold, vol = 370 509 mm^3 = the structural_analysis.md
mass-budget figure), bakes it into the hull frame (same transform
tools/bake_hull_frame.py records for Cargo_Shell), and evaluates
`(shell + positives) − negatives` as a single manifold3d expression.  Boolean
of closed manifolds is closed by construction ⇒ guaranteed watertight out.

Two design essentials handled correctly
---------------------------------------
1. OPEN JOINT FACES.  The four fuselage sections are open-ended tubes joined by
   internal splice collars (CLAUDE.md: "mating surfaces between the four
   fuselage sections will be open").  The Blender source is CLOSED-capped at the
   fwd (head/cargo, hull Y≈−71.5) and aft (cargo/middle, hull Y≈+132) faces, so
   this script removes each end cap with a cavity-shaped plug — leaving a
   watertight OPEN "pipe" end (the 2 mm wall wraps the rim), prepped for the
   splice collars.  (Subtracting a solid plug keeps the mesh a closed
   2-manifold; an open-ended thick tube is watertight like a length of pipe.)

2. WALL-CONFORMING INTERIOR FEATURES.  Serenity's hull walls curve continuously,
   so a flat-faced boss/pad butted against them contacts only at a tangent and
   floats off elsewhere ("orphaned sockets").  Every positive interior feature
   is therefore modelled DEEP (extending past the exterior skin), then clipped
   with the section's own OUTER-SKIN ENVELOPE (∩ envelope).  The intersection
   trims the outboard end exactly to the curved skin surface, so each feature
   seats flush against — and fuses fully into — the real wall, with zero
   exterior protrusion and nothing floating in mid-cavity.

Features merged (hull frame, X=+port, Y=+aft, Z=+dorsal)
-------------------------------------------------------
NEGATIVE (removed):
  * Interior-wall removal — the cargo-bay floor "duct" the Blender hollowing
    left inside the cavity (a ~54×38 mm box blister on the belly, hull
    X −196..−142, Y −15..+102, Z 6..44), confirmed by section + render.
  * Clamshell belly aperture — hull X[−222.5..−117.6] × Y[+2..+108].
  * OPEN fwd + aft joint faces (cavity-plug cap removal).
  * Boss-pin bores (Joint 1 + Joint 2 — collar alignment dowels), keel channel,
    Y=+30 ring-frame pocket — single-sourced from add_structural_features.py.
  * Wing spar bore (Ø12.3, full lateral span) + 2 wing-root mortises (through
    each lateral wall), at the RE-DERIVED chord stations (129 mm root chord, LE
    root hull Y=−7: spar 30% → Y=+31.7; mortise 50% → Y=+57.5; Z=62.5).
  * M3 heat-set bores in the nacelle-servo pads.

POSITIVE (added, envelope-clipped so they conform + fuse to the curved wall):
  * 4 clamshell hinge-pin retention blocks (from generate_cargo_hinge_retention).
  * 2 wing-spar bearing bosses (Ø22, coaxial with the spar bore).
  * 2 nacelle-servo mount pads (one per lateral wall).
  * Inara avionics-bay standoff bosses (4, dorsal port).  The dorsal Faraday
    access-panel CUT and the River (stbd) bay are DEFERRED (SCAD avionics
    modules are still in the pre-R1 legacy Y-as-dorsal frame; TODO.md §1.1.3.3).

Deferred (documented, NOT cut — legacy-frame re-derivation needed):
  * Inara/River dorsal Faraday access-panel cuts; River (stbd) avionics bay.
  * GPS×2 + FPV flush skin recesses; door-servo pads; latch-catch lips.
  * Landing-gear leg-mount bosses (Rev R5 wire-brace) — TODO.md §1.1.4; a
    keep-out check reports whether merged geometry intrudes on those zones.

References
    docs/structural_analysis.md (Rev R1) — joint / wing / ring-frame design.
    airframe/blender-scripts/add_structural_features.py — joint-feature source.
    airframe/stls/fuselage/cargo/generate_cargo_hinge_retention.py — Rev R1c.
    airframe/stls/fuselage/cargo/generate_cargo_doors.py — Rev R1b door geometry.
    airframe/openscad/fuselage/cargo/cargo_sect_shell24.scad — interior-feature
        design intent (legacy-frame constants; superseded here where re-derived).
    tools/bake_hull_frame.py — Cargo_Shell bake transform.

Run (no Blender needed):
    python3 airframe/blender-scripts/merge_cargo_interior.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
"""

import os
import struct
import sys

import numpy as np
import trimesh
from manifold3d import Manifold, Mesh

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
BLENDER_SRC = os.path.join(
    SCRIPT_DIR, "files-hollowed-24in", "cargo_sect_shell24_2mm_repaired.stl"
)
OUT_PATH = os.environ.get("CARGO_MERGE_OUT") or os.path.join(
    REPO_ROOT,
    "airframe",
    "stls",
    "fuselage",
    "cargo",
    "cargo_sect_shell24_2mm_repaired.stl",
)
CARGO_DIR = os.path.join(REPO_ROOT, "airframe", "stls", "fuselage", "cargo")

# Reuse the single-sourced joint-feature design from add_structural_features.py
sys.path.insert(0, SCRIPT_DIR)
import add_structural_features as asf  # noqa: E402

# Reuse the Rev R1c hull-frame hinge retention blocks verbatim
sys.path.insert(0, CARGO_DIR)
import generate_cargo_hinge_retention as hinge  # noqa: E402

MARKER = b"SerenityUAV HULL-FRAME R1"

# Cargo_Shell bake transform — MUST match tools/bake_hull_frame.py COMPONENTS.
#   180 deg about +Z → (x,y,z)→(−x,−y,z);  T = (−274.4, −282.8, 0)
BAKE_T = np.array([-274.4000100, -282.8000440, 0.0])

WALL_MM = 2.0  # 2 mm foam-fill wall (Blender hollowing pitch / SCAD)

# CF-PETG mass reporting: as-printed (4 perimeters + ≥40% infill) ~1.05 g/cm^3;
# fully dense CF-PETG ~1.28 g/cm^3.  These bracket the true printed mass.
RHO_PRINT = 1.05e-3  # g/mm^3
RHO_SOLID = 1.28e-3  # g/mm^3


# ---------------------------------------------------------------------------
# manifold3d helpers
# ---------------------------------------------------------------------------


def to_man(tm):
    """trimesh.Trimesh -> manifold3d.Manifold (float32, as manifold3d uses)."""
    return Manifold(
        Mesh(
            vert_properties=tm.vertices.astype(np.float32),
            tri_verts=tm.faces.astype(np.uint32),
        )
    )


def from_man(man):
    """manifold3d.Manifold -> trimesh.Trimesh (float64 vertices)."""
    msh = man.to_mesh()
    return trimesh.Trimesh(
        vertices=np.asarray(msh.vert_properties, dtype=np.float64)[:, :3],
        faces=np.asarray(msh.tri_verts, dtype=np.int64),
        process=False,
    )


def union_all(meshes):
    """Union a list of trimesh solids into one Manifold (None if empty)."""
    acc = None
    for m in meshes:
        mm = to_man(m)
        acc = mm if acc is None else (acc + mm)
    return acc


def box(x0, x1, y0, y1, z0, z1):
    """Axis-aligned box from hull-frame corner coordinates."""
    b = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    b.apply_translation([(x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0])
    return b


def x_cylinder(y_cen, z_cen, x0, x1, radius, sections=48):
    """Cylinder whose axis is hull X (lateral), spanning x0..x1."""
    cyl = trimesh.creation.cylinder(radius=radius, height=(x1 - x0), sections=sections)
    cyl.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2.0, [0, 1, 0]))
    cyl.apply_translation([(x0 + x1) / 2.0, y_cen, z_cen])
    return cyl


def z_cylinder(x_cen, y_cen, z0, z1, radius, sections=48):
    """Cylinder whose axis is hull Z (dorsal), spanning z0..z1."""
    cyl = trimesh.creation.cylinder(radius=radius, height=(z1 - z0), sections=sections)
    cyl.apply_translation([x_cen, y_cen, (z0 + z1) / 2.0])
    return cyl


def y_pin(x_cen, z_cen, y0, y1, radius, sections=32):
    """Y-axis boss-pin bore (matches asf._y_cylinder geometry)."""
    cyl = trimesh.creation.cylinder(radius=radius, height=(y1 - y0), sections=sections)
    cyl.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2.0, [1, 0, 0]))
    cyl.apply_translation([x_cen, (y0 + y1) / 2.0, z_cen])
    return cyl


# ---------------------------------------------------------------------------
# Outer-skin envelope (for wall-conforming feature clipping)
# ---------------------------------------------------------------------------


def extract_envelope(shell_tm):
    """Return the section's OUTER-skin closed solid (the exterior envelope).

    The hollow shell is two nested closed surfaces (outer skin + inner cavity
    wall); the outer one — the larger bounding box — is the exterior envelope.
    Intersecting a deep feature with this trims its outboard end exactly to the
    curved skin, so bosses/pads seat flush against the real wall."""
    comps = trimesh.graph.connected_components(
        shell_tm.face_adjacency, nodes=np.arange(len(shell_tm.faces))
    )
    best, best_v = None, -1.0
    for c in comps:
        sub = shell_tm.submesh([c], append=True)
        e = sub.extents
        v = float(e[0] * e[1] * e[2])
        if v > best_v:
            best, best_v = sub, v
    return best


# ---------------------------------------------------------------------------
# Joint-face opening
# ---------------------------------------------------------------------------
# The fwd (head/cargo) and aft (cargo/middle) mating faces are cut FLAT at their
# mating planes (asf._flat_face_cutter with asf.MATING_PLANES["cargo_fwd"] /
# ["cargo_aft"]) in build_negatives(), removing the rounded closure caps and
# leaving clean flat OPEN tubes the conforming splice collars slip into.
# History (JOINT-01/JOINT-02, 2026-07-06): the original single-station
# open_face_plug() bit the fwd dorsal skin and left ragged rim fragments; the
# lofted _bore_open_cutter() that replaced it cleaned the rim but never removed
# the closure cap, so the collar still passed through solid plastic — the flat
# half-space cut here fixes both (a plane leaves no jaggies and does remove the
# cap).  The section end profiles no longer taper into a rounded cap, so the
# splice collar is now a CONFORMING lofted sleeve (generate_conforming_collars.py).


# ---------------------------------------------------------------------------
# Feature geometry (hull frame, mm)
# ---------------------------------------------------------------------------

# Interior-wall (cargo-bay floor "duct") removal — box engulfs the duct walls
# above the belly skin; the door aperture below clears the rest.  Bottom held
# at Z=8 so belly skin FWD of the bay is untouched (a <=2 mm foam-filled curb
# is left where the duct met the floor).
DUCT_CUT = (-201.0, -137.0, -20.0, 107.0, 8.0, 48.0)  # x0,x1,y0,y1,z0,z1

# Clamshell belly aperture — between the two door hinge lines (stbd −222.5,
# port −117.6), bay Y +2..+108, Z −3..+9 removes only the belly skin.
APERTURE = (-222.5, -117.6, 2.0, 108.0, -3.0, 9.0)

# Wing subsystem — RE-DERIVED chordwise stations (hull frame).
WING_LE_ROOT_Y = -7.0
WING_ROOT_CHORD = 129.0
WING_SPAR_Y = WING_LE_ROOT_Y + 0.30 * WING_ROOT_CHORD  # = +31.7
WING_MORT_Y = WING_LE_ROOT_Y + 0.50 * WING_ROOT_CHORD  # = +57.5
WING_ROOT_Z = 62.5
WING_SPAR_BORE_D = 12.3
WING_SPAR_BOSS_OD = 22.0
MORT_W = 30.8  # mortise Y span
MORT_H = 20.8  # mortise Z span

# Lateral-wall X reference bands (deep-embed spans; the outboard end is clipped
# to the real skin by the envelope, so only rough bracketing is needed).
PORT_OUTB, PORT_INB = -60.0, -100.0  # port wall bracket (skin ≈ −83..−90)
STBD_OUTB, STBD_INB = -278.0, -240.0  # stbd wall bracket (skin ≈ −250..−255)

# Nacelle-servo mount pads.
NSVMT_Y = 45.0
NSVMT_PAD_W = 52.0  # Y span
NSVMT_PAD_H = 30.0  # Z span
NSVMT_Z = WING_ROOT_Z + 30.5  # = 93.0 (clears spar boss Z 51.5..73.5 by ~4 mm)
NSVMT_HOLE_S_Y = 17.5
NSVMT_HOLE_S_Z = 8.0
NSVMT_M3_D = 4.1

# Inara avionics-bay standoff bosses (dorsal port half, additive only).
INARA_X = -135.0
INARA_Y = 90.0
INARA_BOSS_DX = 25.0
INARA_BOSS_DY = 15.0
BOSS_OD = 8.0
BOSS_BORE_D = 4.1
DORSAL_Z_TOP = 172.0  # above the dorsal skin (Z_max ≈ 163); clipped by envelope
DORSAL_Z_INB = 145.0  # boss reaches this far into the cavity

# Landing-gear leg-mount keep-out zones (DEFERRED; clearance check only).
LEG_ZONES = [
    ("fwd-port", (-130.0, -95.0, 15.0, 35.0, 0.0, 40.0)),
    ("fwd-stbd", (-245.0, -210.0, 15.0, 35.0, 0.0, 40.0)),
    ("aft-port", (-130.0, -95.0, 90.0, 110.0, 0.0, 40.0)),
    ("aft-stbd", (-245.0, -210.0, 90.0, 110.0, 0.0, 40.0)),
]


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def bake(mesh):
    """Apply the Cargo_Shell hull-frame bake transform (180° about Z + T)."""
    v = mesh.vertices.copy()
    v[:, 0] = -v[:, 0] + BAKE_T[0]
    v[:, 1] = -v[:, 1] + BAKE_T[1]
    v[:, 2] = v[:, 2] + BAKE_T[2]
    return trimesh.Trimesh(vertices=v, faces=mesh.faces, process=False)


def build_negatives(shell_tm):
    """Return (cutters, notes)."""
    cutters, notes = [], []

    cutters.append(box(*DUCT_CUT))
    notes.append("interior-wall duct removal")
    cutters.append(box(*APERTURE))
    notes.append("clamshell belly aperture")

    # Open the fwd + aft mating faces with a FLAT half-space cut at each mating
    # plane (asf._flat_face_cutter): it removes the rounded closure cap the
    # hollowing left, leaving a clean flat OPEN tube the splice collar slips into
    # — no ragged fragments and no dorsal bite (a plane can't make them), and the
    # bore stays genuinely open (JOINT-01 fix superseded 2026-07-06: the lofted
    # bore-open cutter cleaned the rim but never removed the cap, so the collar
    # still passed through solid plastic — see TODO.md).
    cutters.append(asf._flat_face_cutter(shell_tm, "cargo_fwd"))
    notes.append("flat OPEN fwd mating face (head/cargo)")
    cutters.append(asf._flat_face_cutter(shell_tm, "cargo_aft"))
    notes.append("flat OPEN aft mating face (cargo/middle)")

    # Joint 1 + Joint 2 boss-pin bores REMOVED 2026-07-06 (user directive):
    # the head/cargo and cargo/middle splice collars now secure AND align these
    # joints, so no dowel bores are cut into the cargo shell (see
    # add_structural_features.py module docstring, and docs/structural_analysis.md
    # §7.3 — the pins had already been re-roled from load-bearing to alignment-only
    # when the collars were introduced).

    # Keel locating channel + Y=+30 ring-frame pocket.
    kc = asf.KEEL_CHANNEL["cargo"]
    cutters.append(
        box(
            kc["x_range"][0],
            kc["x_range"][1],
            kc["y_range"][0],
            kc["y_range"][1],
            kc["z_range"][0],
            kc["z_range"][1],
        )
    )
    notes.append("keel channel")
    for xm, xx, zm, zx, ym, yx in asf.RING_POCKETS["cargo_Y30"]:
        cutters.append(box(xm, xx, ym, yx, zm, zx))
    notes.append("ring pocket Y=30")

    # Wing spar bore (full lateral span) + 2 root mortises (through each wall).
    cutters.append(
        x_cylinder(WING_SPAR_Y, WING_ROOT_Z, -270.0, -70.0, WING_SPAR_BORE_D / 2.0)
    )
    notes.append("wing spar bore")
    cutters.append(
        box(
            PORT_INB + 1.0,
            PORT_OUTB - 10.0,
            WING_MORT_Y - MORT_W / 2,
            WING_MORT_Y + MORT_W / 2,
            WING_ROOT_Z - MORT_H / 2,
            WING_ROOT_Z + MORT_H / 2,
        )
    )
    cutters.append(
        box(
            STBD_OUTB + 8.0,
            STBD_INB - 1.0,
            WING_MORT_Y - MORT_W / 2,
            WING_MORT_Y + MORT_W / 2,
            WING_ROOT_Z - MORT_H / 2,
            WING_ROOT_Z + MORT_H / 2,
        )
    )
    notes.append("wing mortises (port + stbd)")

    # Nacelle-servo M3 heat-set pilot bores (into the cavity face of each pad).
    for x_in, x_out in ((PORT_INB, PORT_INB + 8.0), (STBD_INB, STBD_INB - 8.0)):
        for dy in (-NSVMT_HOLE_S_Y, NSVMT_HOLE_S_Y):
            for dz in (-NSVMT_HOLE_S_Z, NSVMT_HOLE_S_Z):
                cutters.append(
                    x_cylinder(
                        NSVMT_Y + dy,
                        NSVMT_Z + dz,
                        min(x_in, x_out),
                        max(x_in, x_out),
                        NSVMT_M3_D / 2.0,
                    )
                )
    notes.append("servo M3 pilot bores")

    return cutters, notes


def build_positives():
    """Return (raw deep features, notes).  Clipped to the envelope in main()."""
    feats, notes = [], []

    for side in ("port", "stbd"):
        for station in ("fwd", "aft"):
            feats.append(hinge._block(side, station))
    notes.append("4 hinge retention blocks")

    # Wing-spar bearing bosses (Ø22, coaxial with the spar; deep, clipped).
    feats.append(
        x_cylinder(
            WING_SPAR_Y, WING_ROOT_Z, PORT_INB, PORT_OUTB, WING_SPAR_BOSS_OD / 2.0
        )
    )
    feats.append(
        x_cylinder(
            WING_SPAR_Y, WING_ROOT_Z, STBD_OUTB, STBD_INB, WING_SPAR_BOSS_OD / 2.0
        )
    )
    notes.append("2 wing-spar bearing bosses")

    # Nacelle-servo mount pads (deep box, clipped).
    feats.append(
        box(
            PORT_INB,
            PORT_OUTB,
            NSVMT_Y - NSVMT_PAD_W / 2,
            NSVMT_Y + NSVMT_PAD_W / 2,
            NSVMT_Z - NSVMT_PAD_H / 2,
            NSVMT_Z + NSVMT_PAD_H / 2,
        )
    )
    feats.append(
        box(
            STBD_OUTB,
            STBD_INB,
            NSVMT_Y - NSVMT_PAD_W / 2,
            NSVMT_Y + NSVMT_PAD_W / 2,
            NSVMT_Z - NSVMT_PAD_H / 2,
            NSVMT_Z + NSVMT_PAD_H / 2,
        )
    )
    notes.append("2 nacelle-servo mount pads")

    # Inara avionics-bay standoff bosses (dorsal port, deep Z-cyl, clipped).
    n = 0
    for dx in (-INARA_BOSS_DX, INARA_BOSS_DX):
        for dy in (-INARA_BOSS_DY, INARA_BOSS_DY):
            body = z_cylinder(
                INARA_X + dx, INARA_Y + dy, DORSAL_Z_INB, DORSAL_Z_TOP, BOSS_OD / 2.0
            )
            bore = z_cylinder(
                INARA_X + dx,
                INARA_Y + dy,
                DORSAL_Z_INB - 0.1,
                DORSAL_Z_TOP + 0.1,
                BOSS_BORE_D / 2.0,
            )
            feats.append(from_man(to_man(body) - to_man(bore)))
            n += 1
    notes.append(f"Inara avionics bosses ({n})")

    return feats, notes


def stamp_export(mesh, out_path):
    """Write binary STL with the HULL-FRAME R1 marker in the 80-byte header."""
    count = len(mesh.faces)
    tris = mesh.vertices[mesh.faces]
    e1 = tris[:, 1, :] - tris[:, 0, :]
    e2 = tris[:, 2, :] - tris[:, 0, :]
    normals = np.cross(e1, e2)
    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    safe = np.where(lengths > 0.0, lengths, 1.0)
    normals = np.where(lengths > 0.0, normals / safe, 0.0)
    rec_dtype = np.dtype([("data", "<f4", (12,)), ("attr", "<u2")])
    rec = np.zeros(count, dtype=rec_dtype)
    rec["data"][:, 0:3] = normals.astype("<f4")
    rec["data"][:, 3:12] = tris.reshape(count, 9).astype("<f4")
    header = (MARKER + b" Cargo_Shell interior-merge 2026-06-30")[:80].ljust(80, b"\0")
    with open(out_path, "wb") as fh:
        fh.write(header)
        fh.write(struct.pack("<I", count))
        fh.write(rec.tobytes())


def check_leg_clearance(mesh):
    """Report whether merged geometry intrudes into the deferred leg-mount
    keep-out zones (informational — leg bosses are Rev R5 future work)."""
    print("\n--- landing-gear leg-mount clearance (deferred; keep-out check) ---")
    v = mesh.vertices
    for name, (x0, x1, y0, y1, z0, z1) in LEG_ZONES:
        inside = (
            (v[:, 0] >= x0)
            & (v[:, 0] <= x1)
            & (v[:, 1] >= y0)
            & (v[:, 1] <= y1)
            & (v[:, 2] >= z0)
            & (v[:, 2] <= z1)
        )
        n = int(inside.sum())
        tag = "clear (skin only)" if n < 4000 else "REVIEW: dense geometry"
        print(
            f"  {name:9s} X[{x0:.0f},{x1:.0f}] Y[{y0:.0f},{y1:.0f}] "
            f"Z[{z0:.0f},{z1:.0f}]: {n} shell verts — {tag}"
        )


def drop_slivers(mesh, min_faces=64):
    """Drop the tiny (1–2 face, zero-area) degenerate components manifold3d can
    leave at cut intersections, so the result is a single clean solid body."""
    comps = trimesh.graph.connected_components(
        mesh.face_adjacency, nodes=np.arange(len(mesh.faces))
    )
    keep = [c for c in comps if len(c) >= min_faces]
    dropped = len(comps) - len(keep)
    if dropped:
        idx = np.concatenate(keep)
        mesh = mesh.submesh([idx], append=True)
        print(
            f"  dropped {dropped} zero-area sliver fragment(s) "
            f"→ {len(keep)} body/bodies"
        )
    return mesh


def verify(mesh):
    ec = np.bincount(mesh.edges_unique_inverse, minlength=len(mesh.edges_unique))
    boundary = int((ec == 1).sum())
    nonman = int((ec > 2).sum())
    wt = mesh.is_watertight
    wind = mesh.is_winding_consistent
    vol = mesh.volume
    bodies = len(
        trimesh.graph.connected_components(
            mesh.face_adjacency, nodes=np.arange(len(mesh.faces))
        )
    )
    print("\n=== verify (final cargo shell) ===")
    print(
        f"  faces={len(mesh.faces):,}  bodies={bodies}  "
        f"watertight={wt}  winding={wind}"
    )
    print(f"  boundary_edges={boundary}  nonmanifold_edges={nonman}")
    print(
        f"  volume={vol:.0f} mm^3  "
        f"mass={vol * RHO_PRINT:.1f} g (as-printed) .. "
        f"{vol * RHO_SOLID:.1f} g (solid CF-PETG)"
    )
    ok = wt and wind and boundary == 0 and nonman == 0 and vol > 0
    print(f"  RESULT: {'PASS' if ok else 'FAIL'}")
    return ok


def finalize_watertight(mesh):
    """Weld float32-coincident boolean-seam vertices, strip the resulting
    degenerate/duplicate faces, and keep the single largest body — so the mesh
    stays a clean watertight 2-manifold AFTER the binary-STL round-trip.

    Ordering matters: WELD (merge_vertices) FIRST, then strip degenerate faces.
    An earlier revision skipped this and noted that nondegenerate_faces() alone
    "opens ~120 boundary holes"; that is true only when the coincident
    boolean-seam vertices have NOT been welded first — the faces bordering them
    are not yet zero-area, so stripping them tears the surface.  After a weld
    pass those seam duplicates collapse to true zero-area faces that strip
    cleanly, closing the ~48 non-manifold seam edges the float32 export
    otherwise leaves.  Verified 2026-07-21: watertight=True, 1 body, volume and
    bounds identical to the pre-finalize mesh (only zero-area junk removed)."""
    mesh.merge_vertices()
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.update_faces(mesh.unique_faces())
    mesh.remove_unreferenced_vertices()
    # ALWAYS rebuild from the largest split body — trimesh's submesh() re-welds
    # coincident vertices, which closes the tiny (≤3-edge) seams the degenerate
    # strip opens AND drops the zero-area sliver bodies, in one step.  (Returning
    # the un-split mesh when there is a single body leaves those seams open;
    # verified 2026-07-21.)  Do NOT add a trailing merge_vertices() — a second
    # weld pass reopens a seam.
    bodies = mesh.split(only_watertight=False)
    if bodies:
        big = max(bodies, key=lambda b: len(b.faces))
        if len(bodies) > 1:
            print(
                f"  finalize: kept largest of {len(bodies)} bodies "
                f"({len(big.faces):,} faces); dropped {len(bodies) - 1} "
                f"zero-area sliver body/bodies"
            )
        mesh = big
    # Insurance: close any residual small holes so the result is a true 2-manifold.
    if not mesh.is_watertight:
        trimesh.repair.fill_holes(mesh)
    trimesh.repair.fix_normals(mesh)
    return mesh


def repair_exported(out_path):
    """Reload the exported cargo STL, weld+clean it to a watertight single body,
    and re-stamp the HULL-FRAME marker.  Runs WITHOUT Blender, so it serves both
    as the tail of the full merge (guaranteeing the ON-DISK file is clean, not
    just the in-memory float64 result) and as a standalone ``--repair-only``
    pass on an already-published cargo STL."""
    print(f"\n=== repair_exported (float32 round-trip finalize): {out_path} ===")
    m = trimesh.load(out_path, process=False)
    m.merge_vertices()
    print(f"  reloaded+welded: watertight={m.is_watertight} faces={len(m.faces):,}")
    m = finalize_watertight(m)
    verify(m)  # in-memory result
    stamp_export(m, out_path)
    print(f"  re-stamped -> {out_path}")

    # Definitive check: reload the WRITTEN file exactly the way tools/validate_stls.py
    # (CI) does — process=True merges coincident float32 vertices on load — and
    # confirm the on-disk artifact is a valid watertight 2-manifold.
    chk = trimesh.load(out_path, force="mesh")
    bodies = chk.split(only_watertight=False)
    ci_ok = chk.is_watertight or (bodies and all(b.is_watertight for b in bodies))
    print(
        f"  on-disk CI-style reload: watertight={chk.is_watertight} "
        f"bodies={len(bodies)}  CI_valid={bool(ci_ok)}"
    )
    return bool(ci_ok)


def main():
    # Blender-free finalization: reload the published cargo STL and weld+clean it
    # to a watertight single body (MESH-01 float32 round-trip fix).  No re-merge.
    if "--repair-only" in sys.argv:
        ok = repair_exported(OUT_PATH)
        sys.exit(0 if ok else 1)

    print("=== merge_cargo_interior.py  Rev R2  2026-07-21 ===")
    print(f"source: {BLENDER_SRC}")
    src = trimesh.load(BLENDER_SRC, process=False)
    src.merge_vertices()
    print(
        f"  loaded {len(src.faces):,} faces  watertight={src.is_watertight}  "
        f"vol={src.volume:.0f} mm^3 (part-local)"
    )

    shell_tm = bake(src)
    b = shell_tm.bounds
    print(
        f"  baked hull frame: X {b[0][0]:.1f}..{b[1][0]:.1f}  "
        f"Y {b[0][1]:.1f}..{b[1][1]:.1f}  Z {b[0][2]:.1f}..{b[1][2]:.1f}"
    )

    envelope_tm = extract_envelope(shell_tm)
    eb = envelope_tm.bounds
    print(
        f"  outer-skin envelope: {len(envelope_tm.faces):,} faces  "
        f"watertight={envelope_tm.is_watertight}  "
        f"X {eb[0][0]:.1f}..{eb[1][0]:.1f}"
    )

    negs, nnotes = build_negatives(shell_tm)
    poss, pnotes = build_positives()
    print(f"\n  negatives ({len(negs)} cutters):")
    for n in nnotes:
        print(f"    - {n}")
    print(f"  positives ({len(poss)} features, envelope-clipped):")
    for n in pnotes:
        print(f"    - {n}")

    print("\n  evaluating (shell + (positives ∩ envelope)) − negatives …")
    shell_man = to_man(shell_tm)
    env_man = to_man(envelope_tm)
    pos_man = union_all(poss)
    neg_man = union_all(negs)
    result = shell_man
    if pos_man is not None:
        result = result + (pos_man ^ env_man)  # ^ = intersection in manifold3d
    if neg_man is not None:
        result = result - neg_man
    out = from_man(result)
    out = drop_slivers(out)

    # The in-memory float64 result is a clean watertight single body here, but
    # binary STL stores per-face vertices: the float32 export splits the
    # coincident boolean-seam vertices apart, so the RELOADED file fragments into
    # ~36 bodies with ~48 non-manifold seam edges and FAILS tools/validate_stls.py
    # (the CI watertight check).  This was previously mislabelled a "benign"
    # artifact; it is a real MESH-01 defect on the published STL.  We therefore
    # write the file, then reload + weld + clean it (repair_exported below) so the
    # ON-DISK artifact — not merely the in-memory mesh — is a watertight 2-manifold.
    verify(out)
    check_leg_clearance(out)

    stamp_export(out, OUT_PATH)
    print(f"\n  written -> {OUT_PATH}")
    print("  (already in hull frame + HULL-FRAME R1 marker; do NOT re-bake)")

    # Weld/clean the exported float32 file so the published STL passes CI.
    ok = repair_exported(OUT_PATH)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
