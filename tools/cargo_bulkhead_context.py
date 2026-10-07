#!/usr/bin/python3
"""In-context fit of the port and starboard cargo-bay bulkheads (side walls).

Builds every part that lives on, passes through or moves past the two cargo
side walls IN POSITION, with its non-printed parts, harnesses and motion, and
reports the intersection volume of every pair.  Method:
docs/solutions/design-patterns/build-every-joint-in-context-through-its-full-motion.md
(rules 1-4) and docs/plans/2026-10-03-002-feat-exhaustive-joint-analysis-plan.md
(R1 exhaustive pairs, R4 symmetry gated, R5 non-printed parts and harnesses as
solids, R6 motion swept).

What is assembled (hull frame, mm; X = +port, Y = +aft, Z = +dorsal):

* Real meshes, identity placement (all are baked in hull frame; bounds are
  printed so a stale bake shows): cargo shell (with the merged LG bays, root
  bosses and harness bores), wings, bonded root flanges, tilt brackets,
  brake guides, battery cradle, chin shelf, door gateway tray, doors, hinge
  retention, latch brackets, both splice collars, 3.0 in gear legs.  The
  starboard brake guide is TRANSLATED, as in serenity_assembly.py (the worm
  has a hand).
* Rotating parts as their SWEPT envelopes: worm-wheel tip cylinder, worm tip
  cylinder, the O4 tilt drive shaft, and each door swept 0..180 deg about its
  own hinge pin (CARGO_DOOR_LATCH_SPEC.md: 180 deg swing).
* Non-printed parts from tools/cargo_layout_fit.layout_t5() (single source):
  gearmotors, tilt controller boards, brake collars and solenoids, battery,
  payload, the TACCO chin pair, the Pilot aft pair, cargo Observer, door
  gateway board, hoist lines and drums.
* The bonded CF spar (O20) from its socket floor to the wing tip stub.
* Harness exits as tubes: the 4 x 10 AWG bundle (O16.3, the spar ID) out of
  the spar wire bore, the AK7455 encoder conduit (O6.5) and the nav conduit
  (O3.2), each carried EXIT_STUB mm inboard of its bore exit -- the minimum
  straight run before any turn.

The 10 AWG route from the spar exit to Flight Engineer (middle-section neck,
POWER_DISTRIBUTION.md) is defined nowhere in the repo, so `--corridor` asks
the geometry whether one exists: the bulkhead zone is voxelised at 1 mm, every
solid above is marked occupied, and a Euclidean distance transform gives the
largest bundle that can reach each voxel from the spar exit.  The answer is
the bottleneck diameter of the best route to the cargo/middle splice.

Run:  /usr/bin/python3 tools/cargo_bulkhead_context.py [--corridor] [--export DIR]
Exit 2 on any unexpected CLASH or a port/starboard DESYNC.

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, per AGENTS.md AI attribution.
License: MIT (SPDX-License-Identifier: MIT) -- see tools/LICENSE.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import sys

import numpy as np
import trimesh
from manifold3d import Manifold, Mesh
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cargo_layout_fit as clf  # noqa: E402  (single source for the cargo stations)

REPO = os.path.abspath(os.path.join(HERE, ".."))
STL = os.path.join(REPO, "airframe", "stls")
sys.path.insert(0, os.path.join(STL, "fuselage", "cargo"))
import cargo_door_hinge_params as hinge  # noqa: E402  (CARGO-HINGE-SYNC source)

X_CL = clf.X_CL                       # cargo centre plane, -169.85
STBD_DX = 2.0 * (X_CL - clf.WORM_X)   # -89.2: worm/wheel/guide translate, not mirror

# Wing datums -- merge_cargo_interior.py (WING_SPAR_*, WING_*_Y/Z), restated
# here only as the check's inputs; the meshes are measured against them.
SPAR_Y, SPAR_Z, SPAR_D = 21.00, 66.851, 20.0
SHAFT_Y, SHAFT_Z, SHAFT_D = clf.SHAFT_Y, clf.SHAFT_Z, 4.0
BUNDLE_D = 16.3            # spar ID = 4 x 10 AWG bundle (SPAR_WIRE_BORE_D)
ENC_Y, ENC_Z, ENC_D = 37.50, 68.689, 6.5
NAV_Y, NAV_Z, NAV_D = 1.00, 61.974, 3.2
SPAR_INB = {"port": -100.0, "stbd": -240.0}      # socket floor (bay clear span)
HARN_INB = {"port": -125.0, "stbd": -213.0}      # harness bore inboard exits
WALL_OUT = {"port": -79.6, "stbd": -260.0}       # root-flange outer bbox = wall skin
EXIT_STUB = 10.0           # straight run inboard of a bore exit before a turn

DOOR_SWING = 180.0         # CARGO_DOOR_LATCH_SPEC.md / airframe WBS 1.1.0
DOOR_STEPS = 19            # 10 deg steps
SPAR_TIP_STUB = 13.5       # wings_s1223_revo.scad SPAR_TIP_PROTRUSION


def man(tm: trimesh.Trimesh) -> Manifold:
    """trimesh -> Manifold (raises if the mesh is not a valid 2-manifold)."""
    m = Manifold(Mesh(vert_properties=np.asarray(tm.vertices, np.float32),
                      tri_verts=np.asarray(tm.faces, np.uint32)))
    return m


def tri(m: Manifold) -> trimesh.Trimesh:
    """Manifold -> trimesh."""
    g = m.to_mesh()
    return trimesh.Trimesh(np.asarray(g.vert_properties)[:, :3],
                           np.asarray(g.tri_verts), process=False)


def load(rel: str) -> trimesh.Trimesh:
    """Load a hull-frame STL under airframe/stls."""
    m = trimesh.load(os.path.join(STL, rel), force="mesh")
    if not isinstance(m, trimesh.Trimesh):
        raise TypeError(f"{rel}: not a single mesh")
    return m


def xcyl(y, z, x0, x1, d):
    """Cylinder along hull X."""
    return clf.cyl("x", y, z, min(x0, x1), max(x0, x1), d / 2.0)


def door_sweep(tm: trimesh.Trimesh, hx: float, hz: float, sign: float) -> Manifold:
    """Union of the door rotated 0..DOOR_SWING about its hinge pin (axis || Y)."""
    out = None
    for a in np.linspace(0.0, DOOR_SWING, DOOR_STEPS):
        r = trimesh.transformations.rotation_matrix(np.radians(sign * a), [0, 1, 0],
                                                    [hx, 0.0, hz])
        m = man(tm.copy().apply_transform(r))
        out = m if out is None else out + m
    return out


def door_sign(tm, hx, hz):
    """Rotation sense that swings the door DOWN (out of the hull) first."""
    for s in (1.0, -1.0):
        r = trimesh.transformations.rotation_matrix(np.radians(s * 45), [0, 1, 0],
                                                    [hx, 0.0, hz])
        if tm.copy().apply_transform(r).bounds[0][2] < tm.bounds[0][2] - 5:
            return s
    raise RuntimeError("door does not swing down for either sense")


def build() -> dict[str, dict]:
    """Every solid in the bulkhead context: name -> {m, side, kind}."""
    P: dict[str, dict] = {}

    def add(name, solid, side="cl", kind="printed"):
        m = solid if isinstance(solid, Manifold) else man(solid)
        if m.status().name != "NoError" or m.volume() <= 0:
            raise RuntimeError(f"{name}: not a valid solid ({m.status()})")
        P[name] = dict(m=m, side=side, kind=kind)

    # --- real meshes ---------------------------------------------------
    add("shell", load("fuselage/cargo/cargo_sect_shell24_2mm_repaired.stl"))
    add("collar head-cargo", load("fuselage/head_cargo_splice_collar.stl"))
    add("collar cargo-middle", load("fuselage/cargo_middle_splice_collar.stl"))
    add("gear legs 3.0in", load("fuselage/landing-gear/lg_r6_3_0in_hull_legs.stl"))
    add("battery cradle", load("fuselage/cargo/battery_cradle.stl"))
    add("chin shelf", load("fuselage/cargo/chin_node_shelf.stl"))
    add("door gateway tray", load("fuselage/cargo/gateway_door_tray.stl"))
    add("hinge retention", load("fuselage/cargo/cargo_hinge_retention.stl"))
    guide = load("fuselage/cargo/tilt_brake_guide.stl")
    for side in ("port", "stbd"):
        add(f"wing {side}", load(f"wings/wing_{side}_s1223_revo.stl"), side)
        add(f"root flange {side}", load(f"fuselage/wing_root_flange_{side}.stl"), side)
        add(f"tilt bracket {side}", load(f"fuselage/cargo/tilt_actuator_bracket_{side}.stl"),
            side)
        g = guide.copy()
        if side == "stbd":
            g.apply_translation([STBD_DX, 0, 0])
        add(f"brake guide {side}", g, side)
        lb = load(f"fuselage/cargo/door_latch_bracket_{side}.stl")
        if not lb.is_watertight:
            trimesh.repair.fill_holes(lb)
        add(f"latch bracket {side}", lb, side)
        door = load(f"fuselage/cargo/cargo_door_{side}.stl")
        hx = hinge.HINGE_X_PORT if side == "port" else hinge.HINGE_X_STBD
        hz = hinge.HINGE_Z_PORT if side == "port" else hinge.HINGE_Z_STBD
        add(f"door {side} (closed)", door, side)
        add(f"door {side} swept 0-180", door_sweep(door, hx, hz, door_sign(door, hx, hz)),
            side, "swept")

    # --- swept rotating parts and procured solids ---------------------
    wing_tip = {"port": P["wing port"]["m"].bounding_box()[3] + SPAR_TIP_STUB,
                "stbd": P["wing stbd"]["m"].bounding_box()[0] - SPAR_TIP_STUB}
    for side in ("port", "stbd"):
        mir = side == "stbd"
        dx = STBD_DX if mir else 0.0
        wheel = clf.cyl("x", SHAFT_Y, SHAFT_Z, clf.GEAR_X_OUT - clf.WHEEL_FACE + dx,
                        clf.GEAR_X_OUT + dx, clf.WHEEL_PD / 2 + clf.GEAR_MODULE)
        add(f"wheel swept {side}", wheel, side, "swept")
        worm = clf.cyl("y", clf.WORM_X + dx, clf.WORM_Z, clf.WORM_YC - clf.WORM_LEN / 2,
                       clf.WORM_YC + clf.WORM_LEN / 2 + clf.WORM_HUB_L,
                       clf.WORM_PD / 2 + clf.GEAR_MODULE)
        add(f"worm swept {side}", worm, side, "swept")
        wheel_in = clf.GEAR_X_OUT - clf.WHEEL_FACE + dx if not mir else clf.GEAR_X_OUT + dx
        add(f"drive shaft {side}", xcyl(SHAFT_Y, SHAFT_Z, wheel_in, wing_tip[side], SHAFT_D),
            side, "swept")
        add(f"CF spar {side}", xcyl(SPAR_Y, SPAR_Z, SPAR_INB[side], wing_tip[side], SPAR_D),
            side, "procured")
        sgn = -1.0 if side == "port" else 1.0          # inboard direction
        xi = HARN_INB[side]
        add(f"10AWG bundle exit {side}",
            xcyl(SPAR_Y, SPAR_Z, SPAR_INB[side], xi + sgn * EXIT_STUB, BUNDLE_D), side, "harness")
        add(f"encoder harness exit {side}",
            xcyl(ENC_Y, ENC_Z, WALL_OUT[side], xi + sgn * EXIT_STUB, ENC_D), side, "harness")
        add(f"nav harness exit {side}",
            xcyl(NAV_Y, NAV_Z, WALL_OUT[side], xi + sgn * EXIT_STUB, NAV_D), side, "harness")

    keep = {"motor": "gearmotor", "tilt controller board": "tilt controller board",
            "brake collar": "brake collar", "brake solenoid": "brake solenoid"}
    L = clf.layout_t5()
    for k, label in keep.items():
        add(f"{label} port", L[k]["solid"], "port", "procured")
        s = L[k]["solid"].copy()
        # Board and motor are mirrored in cargo_layout_fit; the worm-side parts
        # follow the TRANSLATED actuator, so translate them the same way.
        s = clf.mirror_x(s) if k == "tilt controller board" else s.apply_translation(
            [STBD_DX, 0, 0])
        add(f"{label} stbd", s, "stbd", "procured")
    for k, label, side in (
            ("battery", "battery", "cl"), ("payload", "payload keep-out", "cl"),
            ("node N1 CN2 (port chin)", "TACCO CN2 port", "port"),
            ("node N3 CN3 (stbd chin)", "TACCO CN3 stbd", "stbd"),
            ("node N2 FC2 (aft port)", "Pilot FC2 port", "port"),
            ("node N4 FC3 (aft stbd)", "Pilot FC3 stbd", "stbd"),
            ("node N2 FC2 (aft port) cable zone", "Pilot FC2 cable zone", "port"),
            ("node N4 FC3 (aft stbd) cable zone", "Pilot FC3 cable zone", "stbd"),
            ("observer tray", "cargo Observer", "cl"),
            ("door gateway board+parts", "door gateway PCB", "cl"),
            ("hoist line 0", "hoist line stbd", "stbd"),
            ("hoist line 1", "hoist line port", "port"),
            ("winch drum 0 (Phase 7)", "winch drum stbd", "stbd"),
            ("winch drum 1 (Phase 7)", "winch drum port", "port")):
        add(label, L[k]["solid"], side, "procured")
    return P


# Designed contacts: (a, b) -> max overlap mm3 accepted, and why.  Anything
# else that overlaps by > CLASH_MM3 is a finding.  Pairs are unordered.
EXPECTED = {
    ("shell", "root flange"): (1e9, "bonded flange on the wall"),
    ("wing", "root flange"): (1e9, "wing root tenon/face bonded into the flange"),
    ("shell", "wing"): (1e9, "wing root tenon in the shell mortise (measured gap 0.12)"),
    ("CF spar", "wing"): (60.0, "spar in its O20.4 bore (facet chord only)"),
    ("CF spar", "root flange"): (60.0, "spar in its O20.4 socket (facet chord only)"),
    ("CF spar", "shell"): (60.0, "spar in its O20.4 socket (facet chord only)"),
    ("drive shaft", "wheel swept"): (1e9, "shaft carries the wheel"),
    ("worm swept", "wheel swept"): (1e9, "gear mesh"),
    ("gearmotor", "worm swept"): (1e9, "worm on the motor shaft (tip envelope)"),
    ("tilt bracket", "shell"): (1e9, "bracket feet on their bosses"),
    ("tilt bracket", "gearmotor"): (1e9, "motor face plate"),
    ("tilt bracket", "tilt controller board"): (1e9, "card-edge rails"),
    ("tilt bracket", "brake guide"): (1e9, "guide bolted to the web"),
    ("tilt bracket", "wheel swept"): (1e9, "shaft bearing boss around the wheel hub"),
    ("tilt bracket", "drive shaft"): (1e9, "shaft bearing in the bracket"),
    ("tilt bracket", "worm swept"): (1e9, "worm slot in the web (tip envelope)"),
    ("tilt bracket", "brake collar"): (1e9, "collar slot in the web"),
    ("brake guide", "brake solenoid"): (1e9, "solenoid seated in the guide"),
    ("brake guide", "brake collar"): (1e9, "pin engages the collar"),
    ("brake collar", "worm swept"): (1e9, "collar on the worm shaft"),
    ("battery", "battery cradle"): (1e9, "pack in its cradle"),
    ("battery cradle", "shell"): (1e9, "hanger bosses"),
    ("chin shelf", "shell"): (1e9, "floor bosses"),
    ("chin shelf", "TACCO"): (1e9, "nodes lie on the shelf"),
    ("door gateway tray", "shell"): (1e9, "slab bosses"),
    ("door gateway tray", "door gateway PCB"): (1e9, "card-edge rails"),
    ("hinge retention", "shell"): (1e9, "hinge blocks on the belly"),
    ("hinge retention", "door"): (1e9, "hinge knuckles interleave"),
    ("latch bracket", "shell"): (1e9, "bracket bonded to the flank"),
    ("door", "shell"): (1e9, "door seats in the aperture lip"),
    ("collar", "shell"): (1e9, "bonded splice collar"),
    ("gear legs", "shell"): (1e9, "legs seated in the merged bays"),
    ("drive shaft", "wing"): (25.0, "O4 shaft in the O4.4 bore (facet chord only)"),
    ("drive shaft", "root flange"): (25.0, "O4 shaft in its bushing seat"),
    ("drive shaft", "shell"): (25.0, "O4 shaft in its bushing seat"),
    ("10AWG bundle exit", "CF spar"): (1e9, "bundle comes out of the spar"),
    ("10AWG bundle exit", "shell"): (60.0, "bundle in its O16.3 wire bore"),
    ("10AWG bundle exit", "root flange"): (60.0, "bundle in its O16.3 wire bore"),
    ("encoder harness exit", "shell"): (10.0, "in its O7.5 port"),
    ("nav harness exit", "shell"): (10.0, "in its O4.2 port"),
    ("encoder harness exit", "wing"): (10.0, "in its O6.5 wing conduit"),
    ("nav harness exit", "wing"): (10.0, "in its O3.2 wing conduit"),
    ("hoist line", "payload"): (1e9, "line attaches to the payload"),
    ("hoist line", "winch drum"): (1e9, "line on its drum"),
    ("door port swept", "door stbd swept"): (
        25.0, "seam: unsynchronised states only; each swept door vs the other CLOSED is 0"),
    ("Pilot", "cable zone"): (1e9, "node and its own cable zone"),
}
CLASH_MM3 = 0.5


def expected(a: str, b: str):
    """Return (cap, reason) if the pair is a designed contact."""
    for (p, q), v in EXPECTED.items():
        if (a.startswith(p) and b.startswith(q)) or (a.startswith(q) and b.startswith(p)):
            return v
    return None


def census(P: dict) -> list[dict]:
    """Every pair whose bounding boxes touch: overlap volume and verdict."""
    rows = []
    bbox = {n: np.array(P[n]["m"].bounding_box()).reshape(2, 3) for n in P}
    for a, b in itertools.combinations(sorted(P), 2):
        if np.any(np.maximum(bbox[a][0], bbox[b][0]) > np.minimum(bbox[a][1], bbox[b][1])):
            continue
        if a.split(" ")[0] == "door" and b.split(" ")[0] == "door" and \
                a.split(" ")[1] == b.split(" ")[1]:
            continue                         # a door and its own swept volume
        v = (P[a]["m"] ^ P[b]["m"]).volume()
        if v <= CLASH_MM3:
            continue
        e = expected(a, b)
        if e and v <= e[0]:
            verdict, why = "DESIGNED", e[1]
        elif e:
            verdict, why = "CLASH", f"exceeds designed {e[0]:.0f} mm3 ({e[1]})"
        else:
            verdict, why = "CLASH", ""
        bb = tri(P[a]["m"] ^ P[b]["m"]).bounds
        rows.append(dict(a=a, b=b, mm3=round(v, 1), verdict=verdict, why=why,
                         box=[bb[0].round(1).tolist(), bb[1].round(1).tolist()]))
    rows.sort(key=lambda r: (r["verdict"] != "CLASH", -r["mm3"]))
    return rows


def symmetry(P: dict, centre: float, tol: float = 0.5) -> list[dict]:
    """Mirror every port solid's bbox about `centre` and compare with stbd."""
    out = []
    for n in sorted(P):
        if " port" not in n:
            continue
        t = n.replace(" port", " stbd")
        if t not in P:
            continue
        bp = np.array(P[n]["m"].bounding_box()).reshape(2, 3)
        bs = np.array(P[t]["m"].bounding_box()).reshape(2, 3)
        mp = bp.copy()
        mp[:, 0] = 2 * centre - bp[::-1, 0]
        d = float(np.abs(mp - bs).max())
        out.append(dict(part=n.replace(" port", ""), bbox_off_mm=round(d, 2),
                        status="SYNC" if d <= tol else "DESYNC"))
    return out


def _yslices(m: Manifold, ys, xs, zs):
    """Point-in-solid count grid [x, y, z] from XZ cross-sections at each Y.

    The solid is rotated +90 deg about X so hull Y becomes the slice height
    (x, y, z) -> (x, -z, y); each slice returns polygons in (x, -z).  The
    returned count is the number of polygon loops containing the point; a point
    is inside the solid when the count is ODD (even-odd rule -- a point in a
    ring's hole is inside two loops)."""
    from matplotlib.path import Path as MPath
    r = m.rotate([90.0, 0.0, 0.0])
    gx, gz = np.meshgrid(xs, zs, indexing="ij")
    pts = np.column_stack([gx.ravel(), -gz.ravel()])
    out = np.zeros((len(xs), len(ys), len(zs)), np.int8)
    for k, y in enumerate(ys):
        cnt = np.zeros(len(pts), np.int8)
        for poly in r.slice(float(y)).to_polygons():
            if len(poly) >= 3:
                cnt += MPath(np.asarray(poly)).contains_points(pts)
        out[:, k, :] = cnt.reshape(len(xs), len(zs))
    return out


def corridor(P: dict, side: str, pitch: float = 1.0) -> dict:
    """Largest bundle that can travel from the spar exit to the aft splice.

    Free space = hull CAVITY in the bulkhead zone (shell section count == 2)
    minus every other solid, the payload keep-out and swept volumes included.
    The zone runs from the wall to 25 mm off the centre plane, so a route
    cannot cross the bay.  Returns the bottleneck diameter (mm) of the best
    route from the spar exit through the cargo/middle splice collar to Y 150
    (into the middle section, towards Flight Engineer), and the
    centreline of the shortest route that carries the 16.3 mm bundle with
    1 mm clearance (for the render)."""
    x_wall = -95.0 if side == "port" else -245.0
    lo = np.array([min(X_CL, x_wall), -20.0, 10.0])
    hi = np.array([max(X_CL, x_wall), 150.0, 165.0])
    xs = np.arange(lo[0] + pitch / 2, hi[0], pitch)
    ys = np.arange(lo[1] + pitch / 2, hi[1], pitch)
    zs = np.arange(lo[2] + pitch / 2, hi[2], pitch)
    occ = None
    for n, e in P.items():
        if e["kind"] == "harness" or n == "shell" or (n.startswith("door") and "swept" in n):
            continue
        bb = np.array(e["m"].bounding_box()).reshape(2, 3)
        if np.any(bb[0] > hi) or np.any(bb[1] < lo):
            continue
        occ = e["m"] if occ is None else occ + e["m"]
    wall = _yslices(P["shell"]["m"], ys, xs, zs) % 2 == 1
    # inside = no wall between the centre plane and the voxel (scan outward),
    # and the centre column itself below its first roof hit (scan upward).
    order = slice(None) if side == "port" else slice(None, None, -1)
    w = wall[order]
    out_x = np.cumsum(w, axis=0) > 0                        # wall seen, scanning outward
    out_x = out_x[order]
    ic = int(np.argmin(np.abs(xs - X_CL)))
    roof = np.cumsum(wall[ic], axis=1) > 0                  # [y, z] wall seen going up
    inside = ~out_x & ~roof[None, :, :]
    solid = _yslices(occ, ys, xs, zs) % 2 == 1
    free = inside & ~wall & ~solid
    free[np.abs(xs - X_CL) < 25.0] = False                  # do not cross the bay
    dist = ndimage.distance_transform_edt(free) * pitch    # mm to nearest solid/wall

    def idx(p):
        return tuple(np.clip(((np.asarray(p) - lo) / pitch).astype(int), 0,
                             np.array(free.shape) - 1))

    c = np.array(idx((HARN_INB[side], SPAR_Y, SPAR_Z)))
    sub = tuple(slice(max(v - 6, 0), v + 7) for v in c)
    loc = np.unravel_index(np.argmax(dist[sub]), dist[sub].shape)
    start = tuple(int(sl.start + v) for sl, v in zip(sub, loc))
    best = 0.0
    for r in (float(v) for v in np.arange(0.5, 30.0, 0.25)):
        lab, _ = ndimage.label(dist >= r)
        if lab[start] == 0 or not np.any(lab[:, -1, :] == lab[start]):
            break
        best = 2 * r
    path = []
    need = BUNDLE_D / 2 + 1.0
    ok = dist >= need
    if ok[start]:
        from collections import deque
        prev: dict[tuple, tuple | None] = {start: None}
        q = deque([start])
        end: tuple | None = None
        while q:
            u = q.popleft()
            if u[1] == free.shape[1] - 1:
                end = u
                break
            for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
                v = (u[0] + d[0], u[1] + d[1], u[2] + d[2])
                if all(0 <= v[i] < free.shape[i] for i in range(3)) and ok[v] and v not in prev:
                    prev[v] = u
                    q.append(v)
        while end is not None:
            path.append((lo + (np.array(end) + 0.5) * pitch).round(1).tolist())
            end = prev[end]
        path.reverse()
    seed = (lo + (np.array(start) + 0.5) * pitch).round(1).tolist()
    return dict(side=side, bottleneck_d_mm=float(best), need_d_mm=BUNDLE_D, seed=seed,
                start_clear_d_mm=round(2 * float(dist[start]), 1),
                path_len_mm=len(path) * pitch, path=path[::5] + path[-1:],
                verdict="ROUTE EXISTS" if best >= BUNDLE_D + 2.0 else "NO ROUTE")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--corridor", action="store_true", help="10 AWG route search")
    ap.add_argument("--export", help="write each solid and each clash as STL here")
    ap.add_argument("--json", help="write the report as JSON here")
    a = ap.parse_args()
    P = build()
    print(f"{len(P)} solids in the bulkhead context")
    for n in sorted(P):
        bb = np.array(P[n]["m"].bounding_box()).reshape(2, 3).round(1)
        print(f"  {n:34s} {P[n]['kind']:9s} {bb[0].tolist()} {bb[1].tolist()}")
    rows = census(P)
    print(f"\n{'verdict':9s} {'a':34s} {'b':34s} {'mm3':>9s}  overlap box / note")
    for r in rows:
        print(f"{r['verdict']:9s} {r['a']:34s} {r['b']:34s} {r['mm3']:9.1f}  "
              f"{r['box'][0]}..{r['box'][1]} {r['why']}")
    centre = X_CL
    sym = symmetry(P, centre)
    print(f"\nSymmetry (port mirrored about X {centre}):")
    for s in sym:
        print(f"  {s['status']:7s} {s['part']:30s} {s['bbox_off_mm']:6.2f} mm")
    cor = []
    if a.corridor:
        print("\n10 AWG bundle corridor (spar exit -> cargo/middle splice):")
        for side in ("port", "stbd"):
            c = corridor(P, side)
            cor.append(c)
            print(f"  {side}: " + str({k: v for k, v in c.items() if k != "path"}))
    if a.export:
        os.makedirs(a.export, exist_ok=True)

        def safe(n):
            return "".join(c if c.isalnum() or c in "_-" else "_" for c in n)
        for n, e in P.items():
            tri(e["m"]).export(os.path.join(a.export, safe(n) + ".stl"))
        for c in cor:                        # the found route as a O16.3 tube
            pts = c["path"]
            tube = None
            for p0, p1 in zip(pts, pts[1:]):
                seg = Manifold.hull(Manifold.sphere(BUNDLE_D / 2, 16).translate(p0) +
                                    Manifold.sphere(BUNDLE_D / 2, 16).translate(p1))
                tube = seg if tube is None else tube + seg
            if tube is not None:
                tri(tube).export(os.path.join(a.export, f"ROUTE_10AWG_{c['side']}.stl"))
        # Side-tagged clash meshes and per-side clipped context, so the render
        # (cargo_bulkhead_context.scad) imports only -- no preview CSG.
        n_side = {"port": 0, "stbd": 0, "cl": 0}
        for r in rows:
            if r["verdict"] != "CLASH":
                continue
            cm = P[r["a"]]["m"] ^ P[r["b"]]["m"]
            cx = float(np.mean(np.array(cm.bounding_box()).reshape(2, 3)[:, 0]))
            sd = "port" if cx > X_CL + 12 else "stbd" if cx < X_CL - 12 else "cl"
            r["side"] = sd
            tri(cm).export(os.path.join(a.export, f"CLASH_{sd}_{n_side[sd]:02d}.stl"))
            n_side[sd] += 1
        slab = {"port": ([-135.0, -90.0, -100.0], [80.0, 260.0, 300.0]),
                "stbd": ([-285.0, -90.0, -100.0], [80.0, 260.0, 300.0])}
        half = {"port": ([X_CL, -200.0, -200.0], [400.0, 600.0, 600.0]),
                "stbd": ([X_CL - 400.0, -200.0, -200.0], [400.0, 600.0, 600.0])}
        for sd in ("port", "stbd"):
            o, d = slab[sd]
            tri(P["shell"]["m"] ^ Manifold.cube(d).translate(o)).export(
                os.path.join(a.export, f"shell_wall_{sd}.stl"))
            o, d = half[sd]
            tri(P["gear legs 3.0in"]["m"] ^ Manifold.cube(d).translate(o)).export(
                os.path.join(a.export, f"gear_legs_{sd}.stl"))
        with open(os.path.join(a.export, "clash_counts.scad"), "w", encoding="utf-8") as fh:
            fh.write("".join(f"N_CLASH_{k.upper()} = {v};\n" for k, v in n_side.items()))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(dict(pairs=rows, symmetry=sym, corridor=cor), fh, indent=2)
    bad = any(r["verdict"] == "CLASH" for r in rows) or any(
        s["status"] != "SYNC" for s in sym) or any(c["verdict"] != "ROUTE EXISTS" for c in cor)
    print(f"\nRESULT: {'FAIL' if bad else 'PASS'}")
    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
