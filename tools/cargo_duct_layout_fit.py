#!/usr/bin/env python3
"""cargo_duct_layout_fit.py -- the sealed cargo bay as the tail EDF's air duct, with its
equipment (plan 002 U6, TEDF-06; R4, R6, R11-R15, R19, R20, R25, R26, R34; KD5, KD7, KD11).

What it does
  1. MEASURES the duct: at each station from the ramp to the cargo/middle splice it rasterises
     the published one-piece head+cargo hull with the parts that close it in the built
     aircraft (the fused cargo doors, KD5; the splice collar, the wing-root flanges, the wings,
     the landing-gear bays and legs -- the wall set of tools/cfd_internal_air_domain.py) and
     flood-fills the cavity.  The wing-spar bore at the pivot is plugged outboard of the duct
     (the spar fills it; R25 needs its ends capped -- printed as a finding).
  2. PLACES the equipment.  Kept at their stations (R13, R20, KD7): the cargo-bay items of
     tools/cargo_layout_fit.py less the retired ones (payload, door gateway and its tray, the
     old roof winch and hoist lines, and the cargo battery and cradle, retired at Rev U as in
     winch_packaging_fit.py and cfd_internal_air_domain.py); the Cargo Observer.  Fixed by the
     plan: the winch on the floor at Y 356.5 (R13; the stack of winch_packaging_fit.py), the
     fairlead on the belly under the tilt pivot (R14), the hook recess (R15) and a line guard
     between them (R26).  Moved forward as far as fit and function allow (R19, KD11): the
     Flight Engineer box, the tail EDF speed controller, the RCS gateway and the three RCS
     servos (owner option B, tools/rcs_jets.py) -- a search over orientation and position
     that takes the most forward station clearing the hull, every other envelope and the
     stream free-area floor.
  3. CHECKS one limits list: every envelope clears the hull and its neighbours by the gap; the
     fairlead is under the pivot; the winch line runs inside its guard; the stream keeps the
     stated free area at every bay station (the duct floor of tools/tail_edf_flow.py); every
     serviceable item is reachable through the belly service panel (R12); the R34 aft balance
     allowance gives at least the bow pocket's CG travel.
  4. REPORTS the moved items' CG effect, the lead run from the speed controller to the tail
     motor (length, gauge, drop at hover), the louvre / screen / frame at the ramp, the
     flow-guide placeholders U2 must size, the openings list of R25, and the bench fixtures.

ASSUMED inputs are labelled; any PASS resting on one is PROVISIONAL.  Two inputs come from
units not yet run: the flow guides from U2 (TEDF-02) and the bow pocket's CG travel from U7
(TEDF-07); this tool states placeholders for both and says so on every run.

Run:
    /usr/bin/python3 tools/cargo_duct_layout_fit.py [--json OUT.json]

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic) under the author's direction, 2026-11-19, per AGENTS.md
         section 3.
License: CERN-OHL-W-2.0 -- see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from dataclasses import dataclass, replace
from typing import Any

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import hull_datums as hd  # noqa: E402

FS = os.path.join(REPO, "airframe", "stls", "fuselage")
LEDGER = os.path.join(REPO, "current-specification", "auw_ledger.json")

# --- raster and stations ----------------------------------------------------------------------
PITCH = 1.0  # mm per pixel in each station's (X, Z) raster
X0, X1, Z0, Z1 = -100.0, 100.0, 70.0, 290.0
BAY_Y0, BAY_Y1 = 288.0, 432.0  # the bay stations gated for free area (aft of the ramp fairing)
STATION_STEP = 4.0
MAX_CLOSE = 4  # mm: seams narrower than about twice this are closed when finding the cavity
SEED_XZ = (0.0, 150.0)  # inside the bay at every station

# --- fixed by the owner, the plan or a cited document -----------------------------------------
PIVOT_Y = hd.SPAR_Y  # 339.4, the tilt pivot (R14: fairlead under it)
SPAR_Z = hd.SPAR_Z
WINCH_Y = 356.5  # R13 / KD7: the winch stays at its present station (cargo_layout_fit HOIST_Y)
OBSERVER_Y0, OBSERVER_Y1 = 409.5, 429.5  # R20: the Cargo Observer stays (cargo_layout_fit)
DOOR_X, DOOR_Y0, DOOR_Y1 = 50.5, 307.7, 413.7  # the fused clamshell doors (KD5), measured
FE_BOX = (75.0, 94.0, 36.0)  # Flight Engineer unit: can 75 x 94 x 28 + 8 mm entry plate
#                              (tools/middle_layout_fit.py FE_CAN_*, FE_PLATE_Y)
CM07 = (20.5, 7.5, 19.0)  # KST CM07 case [REF-ACT-006]; the RCS valve servo (owner 2026-11-19)
CM07_LUGS = 28.5  # mm over the mounting lugs (plan 2026-11-16-001 candidate table; verify)
N_RCS_SERVOS = 3  # owner option B (tools/rcs_jets.py): two upper jets and one ventral
# Owner benchmark 2026-11-19 (AGENTS.md, airframe/AGENTS.md "Interior Air Path"): every bay
# station keeps at least 8,000 mm^2 (12.4 in^2) of stream free area; future changes hold this
# line.  tools/tail_edf_flow.py puts its cost at about -0.7 % hover tail thrust (k_cargo ASSUMED).
A_STREAM_MIN = 8000.0
# Owner rule 2026-11-19: every PCB in the air path lies in line with the flow; none stands across
# the stream as an air dam (its thinnest side may not lie along Y).
PCB_PREFIXES = ("Flight Engineer", "tail speed controller", "RCS gateway", "node ",
                "observer tray", "tilt controller board")

# --- ASSUMED, labelled on every run -------------------------------------------------------------
GAP = 2.0  # mm static clearance, equipment to hull and to each other (cargo_layout_fit gap)
ESC_BOX = (44.0, 33.0, 15.0)  # OSESC-NAC folded board 44 x 33 (nacelle_esc_thermal) + parts
GATEWAY_BOX = (49.0, 13.6, 25.5)  # SKIPPER-CAN-PERIPH-GW-PCB, N_STACKS=1 (door-gateway envelope)
SERVO_BOX = (CM07_LUGS, CM07[1] + 4.0, CM07[2] + 6.0)  # CM07 over lugs + horn and cable exit
FAIRLEAD_R, FAIRLEAD_H = 8.0, 10.0  # boss radius, height above the belly
HOOK_R, HOOK_DEPTH = 14.0, 12.0  # hook / magnet recess in the belly (R15)
GUARD_R = 7.0  # line guard tube radius around the line, drum to fairlead (R26)
REACH = 10.0  # mm: a footprint edge this far inside the panel opening is reachable
REACH_MIN = 0.5  # of a serviceable item's footprint inside the opening (ASSUMED rule)
PANEL_EDGE = 8.0  # mm: frame land outside the opening for the gasket and fasteners
FASTENER_PITCH = 45.0  # mm along the panel edge (quarter-turn receptacles; part TBD, R12)
BOW_POCKET_TRAVEL = 2.0  # mm: PLACEHOLDER until U7 sizes the bow pocket (OQ8)
BALLAST_RHO = 10.0  # g/cm^3, tungsten putty class (ASSUMED; no part sourced)
REAR_BALLAST_Y = 640.0  # an aft ballast provision in the rear cone, aft of the tail motor
REAR_BALLAST_CAP = 30.0  # g it is laid out to hold (ASSUMED; U13 cuts it)
PANEL_X = DOOR_X  # the belly service panel stays inside the fused door field's width (ASSUMED)
MASS = {"Flight Engineer box": 158.0,  # ledger "Flight Engineer" (BOM Unit_Mass_g)
        "tail speed controller": 52.7,  # OSESC-NAC roll-up estimate (ESC wire market survey)
        "RCS gateway": 6.0,  # as CAN-PERIPH-GW-DOOR (BOM)
        "RCS servo": 7.0}  # KST CM07 [REF-ACT-006]
FE_FROM_Y = 467.7  # the Flight Engineer box today (ledger, middle-section neck)
TAIL_MOTOR_Y = 582.3  # tail EDF motor centre, Y 553.3..611.3 (tools/rear_cone_layout_fit.py)
TAIL_MOTOR_Z = 165.25
LEAD_SLACK = 40.0  # mm of lead slack and bend allowance
AWG14_OHM_PER_M = 0.00828  # standard annealed-copper AWG table value (requires verification)
HOVER_THROTTLE = 0.8
V_BUS = 22.2  # 6S nominal


@dataclass(frozen=True)
class Box:
    name: str
    x0: float
    x1: float
    y0: float
    y1: float
    z0: float
    z1: float
    kind: str = "equipment"  # equipment | fixed | kept | guard | recess
    serviceable: bool = False

    def at_y(self, y: float) -> bool:
        return self.y0 <= y <= self.y1

    @property
    def footprint(self) -> tuple[float, float, float, float]:
        return (self.x0, self.x1, self.y0, self.y1)

    def grown(self, d: float) -> "Box":
        return replace(self, x0=self.x0 - d, x1=self.x1 + d, y0=self.y0 - d, y1=self.y1 + d,
                       z0=self.z0 - d, z1=self.z1 + d)


def overlap(a: Box, b: Box) -> float:
    dx = min(a.x1, b.x1) - max(a.x0, b.x0)
    dy = min(a.y1, b.y1) - max(a.y0, b.y0)
    dz = min(a.z1, b.z1) - max(a.z0, b.z0)
    return dx * dy * dz if dx > 0 and dy > 0 and dz > 0 else 0.0


# --- the hull walls ---------------------------------------------------------------------------
_WALLS: dict[str, Any] = {}


def wall_meshes():
    """The closing wall set of tools/cfd_internal_air_domain.py, hull from its tarball."""
    if "m" in _WALLS:
        return _WALLS["m"]
    import trimesh
    import winch_packaging_fit as wp
    hull = wp.load_hull()
    if not hull.is_watertight or not hull.volume > 0.0:
        raise SystemExit("head+cargo hull mesh is not a closed solid")
    skins = [hull]
    skins += [trimesh.load(os.path.join(FS, "cargo", f))
              for f in ("cargo_door_port.stl", "cargo_door_stbd.stl")]
    skins.append(trimesh.load(os.path.join(FS, "cargo_middle_splice_collar.stl")))
    for f in ("wing_root_flange_port.stl", "wing_root_flange_stbd.stl"):
        skins.append(trimesh.load(os.path.join(FS, f)))
    for f in ("wing_port_s1223_revo.stl", "wing_stbd_s1223_revo.stl"):
        skins.append(trimesh.load(os.path.join(REPO, "airframe", "stls", "wings", f)))
    lg = os.path.join(FS, "landing-gear")
    for f in ("lg_r6_3_0in_bay_fore-port.stl", "lg_r6_3_0in_bay_fore-stbd.stl",
              "lg_r6_3_0in_bay_aft-port.stl", "lg_r6_3_0in_bay_aft-stbd.stl",
              "lg_r6_3_0in_hull_legs.stl", "lg_a1b_housing_fore-port.stl",
              "lg_a1b_housing_fore-stbd.stl"):
        skins.append(trimesh.load(os.path.join(lg, f)))
    _WALLS["m"] = skins
    return skins


NX, NZ = int(round((X1 - X0) / PITCH)), int(round((Z1 - Z0) / PITCH))


def _ij(x, z):
    return int((x - X0) / PITCH), int((z - Z0) / PITCH)


def _raster_lines(mask, mesh, y):
    sec = mesh.section(plane_origin=[0.0, y, 0.0], plane_normal=[0.0, 1.0, 0.0])
    if sec is None:
        return
    for ent in sec.discrete:
        pts = np.asarray(ent)[:, [0, 2]]
        seg = np.diff(pts, axis=0)
        n = np.maximum(1, (np.linalg.norm(seg, axis=1) / 0.3).astype(int))
        for a, d, k in zip(pts[:-1], seg, n):
            p = a + np.linspace(0.0, 1.0, k + 1)[:, None] * d
            i = ((p[:, 0] - X0) / PITCH).astype(int)
            j = ((p[:, 1] - Z0) / PITCH).astype(int)
            ok = (i >= 0) & (i < NX) & (j >= 0) & (j < NZ)
            mask[i[ok], j[ok]] = True


def spar_plug(mask, y):
    """The wing spar fills its bore at the pivot; plug it outboard of the duct walls."""
    r = 9.5
    dy = y - PIVOT_Y
    if abs(dy) >= r:
        return
    h = math.sqrt(r * r - dy * dy)
    j0, j1 = _ij(0.0, SPAR_Z - h)[1], _ij(0.0, SPAR_Z + h)[1] + 1
    for xa, xb in ((-X1, -55.0), (55.0, X1)):
        i0, i1 = _ij(xa, 0.0)[0], _ij(xb, 0.0)[0] + 1
        mask[max(i0, 0):min(i1, NX), max(j0, 0):min(j1, NZ)] = True


_CAV: dict[float, Any] = {}


def cavity(y: float):
    """(air mask, closing used mm) of the duct at station y, before any equipment."""
    from scipy import ndimage
    if y in _CAV:
        return _CAV[y]
    w = np.zeros((NX, NZ), bool)
    for m in wall_meshes():
        if m.bounds[0][1] <= y <= m.bounds[1][1]:
            _raster_lines(w, m, y)
    spar_plug(w, y)
    w1 = ndimage.binary_dilation(w, iterations=1)
    seed = _ij(*SEED_XZ)
    for it in range(1, MAX_CLOSE + 1):
        wd = ndimage.binary_dilation(w, iterations=it)
        inside = ndimage.binary_fill_holes(wd) & ~wd
        lab, _ = ndimage.label(inside)
        if lab[seed]:
            reg = lab == lab[seed]
            if it > 1:
                reg = ndimage.binary_dilation(reg, iterations=it - 1)
            _CAV[y] = (reg & ~w1, it)
            return _CAV[y]
    _CAV[y] = (None, None)
    return _CAV[y]


def box_mask(b: Box) -> np.ndarray:
    m = np.zeros((NX, NZ), bool)
    i0, j0 = _ij(b.x0, b.z0)
    i1, j1 = _ij(b.x1, b.z1)
    m[max(i0, 0):min(i1 + 1, NX), max(j0, 0):min(j1 + 1, NZ)] = True
    return m


def stations(y0=BAY_Y0, y1=BAY_Y1, step=STATION_STEP):
    return [float(y) for y in np.arange(y0, y1 + 1e-9, step)]


# --- the envelopes ----------------------------------------------------------------------------
RETIRED = ("payload", "door gateway", "hoist line", "winch drum", "winch axle", "battery",
           "cradle")


def kept_boxes() -> list[Box]:
    """The cargo-bay items that stay (cargo_layout_fit layout, less the retired ones), as their
    bounding boxes (conservative for the free-area count)."""
    import cargo_layout_fit as clf
    out = []
    for name, item in clf.layout_t5().items():
        if any(k in name for k in RETIRED) or item.get("skin_seat"):
            continue
        (x0, y0, z0), (x1, y1, z1) = item["solid"].bounds
        if y1 < BAY_Y0 - 60.0 or y0 > BAY_Y1 + 10.0:
            continue
        serv = name.startswith("observer")
        out.append(Box(name, x0, x1, y0, y1, z0, z1, "kept", serviceable=serv))
    return out


def floor_z(x0: float, x1: float, y0: float, y1: float) -> float:
    """Highest air-free floor under the footprint: the lowest Z the box may sit at (+gap)."""
    zs = []
    for y in stations(y0, y1, 2.0):
        air, _ = cavity(y)
        if air is None:
            return math.inf
        i0, i1 = _ij(x0, 0)[0], _ij(x1, 0)[0]
        cols = air[max(i0, 0):min(i1 + 1, NX)]
        lows = [np.argmax(c) for c in cols if c.any()]
        if len(lows) < cols.shape[0]:
            return math.inf
        zs.append(Z0 + max(lows) * PITCH)
    return max(zs) + GAP


def ceiling_z(x0: float, x1: float, y0: float, y1: float) -> float:
    """Lowest roof over the footprint, less the gap: the highest Z a box top may reach."""
    zs = []
    for y in stations(y0, y1, 2.0):
        air, _ = cavity(y)
        if air is None:
            return -math.inf
        i0, i1 = _ij(x0, 0)[0], _ij(x1, 0)[0]
        cols = air[max(i0, 0):min(i1 + 1, NX)]
        if not all(c.any() for c in cols):
            return -math.inf
        highs = [NZ - 1 - np.argmax(c[::-1]) for c in cols]
        zs.append(Z0 + min(highs) * PITCH)
    return min(zs) - GAP


def winch_boxes(z_floor: float, hand: int = 1) -> tuple[list[Box], dict[str, float]]:
    """The winch stack of winch_packaging_fit.py on the floor at Y 356.5, drum on the
    centreline; hand -1 mirrors it (servo to starboard).  The line runs from the drum's
    forward-bottom tangent to the fairlead."""
    import winch_packaging_fit as wp
    rmax = max(e[4] for e in wp.ELEMENTS if e[1] == "cyl")
    zmin_box = min(e[6] for e in wp.ELEMENTS if e[1] == "box")
    oz = z_floor + max(rmax, -zmin_box) + wp.CLEARANCE_MM
    out = []
    for name, kind, x0, x1, a, b, c, d in wp.ELEMENTS:
        if hand < 0:
            x0, x1 = -x1, -x0
        if kind == "cyl":
            out.append(Box(f"winch {name}", x0, x1, WINCH_Y - a, WINCH_Y + a, oz - a, oz + a,
                           "fixed", serviceable=True))
        else:
            out.append(Box(f"winch {name}", x0, x1, WINCH_Y + a, WINCH_Y + b, oz + c, oz + d,
                           "fixed", serviceable=True))
    drum_r = next(e[4] for e in wp.ELEMENTS if e[0] == "drum")
    return out, {"spool_z": oz, "drum_r": drum_r}


def line_geometry(spool_z: float, drum_r: float, belly_z: float) -> dict[str, float]:
    """The line leaves the drum at the tangent point toward the fairlead mouth (Y PIVOT_Y,
    Z belly + boss height) and runs straight to it inside the guard."""
    py, pz = PIVOT_Y, belly_z + FAIRLEAD_H
    dy, dz = py - WINCH_Y, pz - spool_z
    dist = math.hypot(dy, dz)
    ang = math.atan2(dz, dy) + math.asin(min(1.0, drum_r / dist))
    ty = WINCH_Y + drum_r * math.sin(ang)
    tz = spool_z - drum_r * math.cos(ang)
    return {"tan_y": ty, "tan_z": tz, "mouth_y": py, "mouth_z": pz,
            "length": math.hypot(py - ty, pz - tz)}


def line_points(lg: dict[str, float], n=40):
    t = np.linspace(0.0, 1.0, n)
    return np.column_stack([np.zeros(n), lg["tan_y"] + t * (lg["mouth_y"] - lg["tan_y"]),
                            lg["tan_z"] + t * (lg["mouth_z"] - lg["tan_z"])])


def guard_box(lg: dict[str, float]) -> Box:
    ys = (lg["tan_y"], lg["mouth_y"])
    zs = (lg["tan_z"], lg["mouth_z"])
    return Box("line guard (R26)", -GUARD_R, GUARD_R, min(ys) - GUARD_R, max(ys) + GUARD_R,
               min(zs) - GUARD_R, max(zs) + GUARD_R, "guard")


def fixed_boxes(belly_z: float) -> tuple[list[Box], dict[str, Any]]:
    # The hook recess bulges HOOK_DEPTH into the bay right under the drum's forward edge, so
    # the winch stands on a printed plinth that lifts its stack clear of it (and of the boss).
    z = belly_z + max(HOOK_DEPTH, FAIRLEAD_H) + GAP
    kept = kept_boxes()
    hand = 1
    for hand in (1, -1):  # the hand whose servo clears the kept tilt drive
        wb, w = winch_boxes(z, hand)
        if not any(overlap(a.grown(GAP), k) > 0.0 for a in wb for k in kept):
            break
    w["hand"] = hand
    lg = line_geometry(w["spool_z"], w["drum_r"], belly_z)
    out = wb + [
        Box("fairlead boss (R14)", -FAIRLEAD_R, FAIRLEAD_R, PIVOT_Y - FAIRLEAD_R,
            PIVOT_Y + FAIRLEAD_R, belly_z, belly_z + FAIRLEAD_H, "fixed"),
        Box("hook recess (R15)", -HOOK_R, HOOK_R, PIVOT_Y - HOOK_R, PIVOT_Y + HOOK_R,
            belly_z, belly_z + HOOK_DEPTH, "recess"),
        guard_box(lg),
    ]
    return out, {**w, "line": lg}  # type: ignore[dict-item]


LINE_SYSTEM = ("winch drum", "winch stbd flange", "winch port flange", "fairlead boss",
               "hook recess", "line guard")


# --- ramp louvre and screen (R5, R6, KD6) ------------------------------------------------------
SCREEN_LAND = 4.0  # mm of frame land beyond the opening on every side (ASSUMED)
SCREEN_FRAME_T = 3.0  # mm frame depth, on the ramp fairing's aft land (ASSUMED)


def ramp_opening() -> tuple[float, float, float, float]:
    """The sealed ramp fairing's opening, X and Z (tools/cargo_layout_fit.py RAMP_*)."""
    import cargo_layout_fit as clf
    return (clf.RAMP_X0, clf.RAMP_X1, clf.RAMP_Z0, clf.RAMP_Z1)


def screen_frame() -> dict[str, float]:
    x0, x1, z0, z1 = ramp_opening()
    return {"x0": x0 - SCREEN_LAND, "x1": x1 + SCREEN_LAND, "z0": z0 - SCREEN_LAND,
            "z1": z1 + SCREEN_LAND, "y0": 291.7, "y1": 291.7 + SCREEN_FRAME_T}


def screen_coverage(screen: dict[str, float], opening) -> float:
    """Fraction of the ramp opening the screen covers (R6: all of it)."""
    x0, x1, z0, z1 = opening
    fx = max(0.0, min(x1, screen["x1"]) - max(x0, screen["x0"]))
    fz = max(0.0, min(z1, screen["z1"]) - max(z0, screen["z0"]))
    return fx * fz / ((x1 - x0) * (z1 - z0))


# --- the forward-move search ------------------------------------------------------------------
def orientations(size: tuple[float, float, float], pcb: bool = False
                 ) -> list[tuple[float, float, float]]:
    """The six axis permutations; for a PCB, only those with its thinnest side across the flow."""
    a, b, c = size
    out = sorted({(a, b, c), (b, a, c), (a, c, b), (c, a, b), (b, c, a), (c, b, a)})
    if pcb and min(size) < max(size):
        out = [o for o in out if o[1] > min(size)]
    return out


def is_pcb(name: str) -> bool:
    return name.startswith(PCB_PREFIXES)


def in_line(b: Box) -> bool:
    """A board is in line with the flow unless its Y extent is its thinnest side."""
    dx, dy, dz = b.x1 - b.x0, b.y1 - b.y0, b.z1 - b.z0
    return not (dy < min(dx, dz) - 1e-9)


def clears(b: Box, placed: list[Box]) -> bool:
    if any(overlap(b.grown(GAP), p) > 0.0 for p in placed if p.kind != "recess"):
        return False
    for y in stations(b.y0, b.y1, 2.0):
        air, _ = cavity(y)
        if air is None:
            return False
        from scipy import ndimage
        inner = ndimage.binary_erosion(air, iterations=int(GAP / PITCH))
        m = box_mask(b)
        if (m & ~inner).any():
            return False
    return True


def free_area(y: float, boxes: list[Box]) -> float:
    air, _ = cavity(y)
    if air is None:
        return 0.0
    occ = np.zeros_like(air)
    for b in boxes:
        if b.at_y(y) and b.kind != "recess":
            occ |= box_mask(b)
    return float((air & ~occ).sum()) * PITCH * PITCH


_BASE: dict[float, float] = {}


def stream_ok(b: Box, placed: list[Box]) -> bool:
    """Where a station meets the stream floor before U6, it must after; where it is already
    below the floor (kept equipment), U6 may add no blockage there at all."""
    for y in stations(BAY_Y0, BAY_Y1, STATION_STEP):
        if not b.at_y(y):
            continue
        after = free_area(y, placed + [b])
        base = _BASE.get(y, A_STREAM_MIN)
        if base >= A_STREAM_MIN and after < A_STREAM_MIN:
            return False
        if base < A_STREAM_MIN and after < free_area(y, placed) - 0.5:
            return False
    return True


def panel_field() -> tuple[float, float, float, float]:
    """The largest belly panel opening: the fused door field's width, the bay's length."""
    return (-PANEL_X + PANEL_EDGE, PANEL_X - PANEL_EDGE, BAY_Y0 + PANEL_EDGE,
            BAY_Y1 - PANEL_EDGE)


def reach_fraction(b: Box, opening) -> float:
    x0, x1, y0, y1 = opening
    fx = max(0.0, min(b.x1, x1 - REACH) - max(b.x0, x0 + REACH))
    fy = max(0.0, min(b.y1, y1 - REACH) - max(b.y0, y0 + REACH))
    return fx * fy / ((b.x1 - b.x0) * (b.y1 - b.y0))


def place_forward(name: str, size, placed: list[Box], y_lo=292.0, y_hi=430.0,
                  x_step=2.0, y_step=2.0) -> Box | None:
    """Most forward station (smallest Y) at which the item fits on the floor or on another
    face, clear of the hull, of every placed envelope and of the stream floor."""
    best: Box | None = None
    for dx, dy, dz in orientations(size, is_pcb(name)):
        for y0 in np.arange(y_lo, y_hi - dy + 1e-9, y_step):
            if best is not None and y0 >= best.y0:
                break
            for xc in sorted(np.arange(-85.0 + dx / 2, 85.0 - dx / 2 + 1e-9, x_step),
                             key=abs):
                x0, x1 = xc - dx / 2, xc + dx / 2
                zf = floor_z(x0, x1, float(y0), float(y0 + dy))
                zc = ceiling_z(x0, x1, float(y0), float(y0 + dy))
                found = None
                # on the floor first; else hung from the roof (the retired cargo battery's
                # place at the roof centre is free since Rev U)
                for z0 in (zf, zc - dz):
                    if not math.isfinite(z0) or z0 < zf - 1e-9 or z0 + dz > zc + 1e-9:
                        continue
                    b = Box(name, x0, x1, float(y0), float(y0 + dy), z0, z0 + dz, "equipment",
                            serviceable=True)
                    if (reach_fraction(b, panel_field()) >= REACH_MIN and clears(b, placed)
                            and stream_ok(b, placed)):
                        found = b
                        break
                if found is not None:
                    best = found
                    break
            if best is not None and best.y0 == y0:
                break
    return best


def blockers(name: str, size, placed: list[Box], step=6.0) -> dict[str, int]:
    """Why an item finds no station: over a coarse grid of positions and orientations, count
    what rejects each candidate (the neighbour it hits, the hull, reach, the stream)."""
    from collections import Counter
    from scipy import ndimage
    cnt: Counter = Counter()
    for dx, dy, dz in orientations(size, is_pcb(name)):
        for y0 in np.arange(296.0, BAY_Y1 - dy + 1e-9, step):
            for xc in np.arange(-80.0 + dx / 2, 80.0 - dx / 2 + 1e-9, step):
                x0, x1 = xc - dx / 2, xc + dx / 2
                zf = floor_z(x0, x1, float(y0), float(y0 + dy))
                zc = ceiling_z(x0, x1, float(y0), float(y0 + dy))
                if not (math.isfinite(zf) and math.isfinite(zc)) or zc - zf < dz:
                    cnt["hull height"] += 1
                    continue
                for z0 in (zf, zc - dz):
                    b = Box(name, x0, x1, float(y0), float(y0 + dy), z0, z0 + dz)
                    hit = [p.name for p in placed
                           if p.kind != "recess" and overlap(b.grown(GAP), p) > 0.0]
                    if hit:
                        cnt.update(hit)
                    elif reach_fraction(b, panel_field()) < REACH_MIN:
                        cnt["panel reach"] += 1
                    elif any((box_mask(b) & ~ndimage.binary_erosion(
                            cavity(y)[0], iterations=int(GAP / PITCH))).any()
                            for y in stations(b.y0, b.y1, 2.0)):
                        cnt["hull wall"] += 1
                    elif not stream_ok(b, placed):
                        cnt["stream floor"] += 1
    return dict(cnt.most_common(6))


def moved_items() -> list[tuple[str, tuple[float, float, float]]]:
    items = [("Flight Engineer box", FE_BOX), ("tail speed controller", ESC_BOX),
             ("RCS gateway", GATEWAY_BOX)]
    items += [(f"RCS servo {k + 1}", SERVO_BOX) for k in range(N_RCS_SERVOS)]
    return items


# --- belly panel, aft allowance, routing, CG --------------------------------------------------
def service_items(boxes: list[Box]) -> list[Box]:
    """Serviceable items, with the winch stack and the Observer counted as one item each."""
    out = [b for b in boxes if b.serviceable and not b.name.startswith(("winch ", "observer"))]
    for prefix, name in (("winch ", "winch (stack)"), ("observer", "Cargo Observer tray")):
        grp = [b for b in boxes if b.serviceable and b.name.startswith(prefix)]
        if grp:
            out.append(Box(name, min(b.x0 for b in grp), max(b.x1 for b in grp),
                           min(b.y0 for b in grp), max(b.y1 for b in grp),
                           min(b.z0 for b in grp), max(b.z1 for b in grp), "fixed", True))
    return out


def belly_panel(boxes: list[Box]) -> dict[str, Any]:
    """Smallest opening, inside the largest belly field, that reaches every serviceable item."""
    serv = service_items(boxes)
    fx0, fx1, fy0, fy1 = panel_field()
    x0 = max(fx0, min(b.x0 for b in serv) - REACH)
    x1 = min(fx1, max(b.x1 for b in serv) + REACH)
    y0 = max(fy0, min(b.y0 for b in serv) - REACH)
    y1 = min(fy1, max(b.y1 for b in serv) + REACH)
    reach = {b.name: reach_fraction(b, (x0, x1, y0, y1)) for b in serv}
    perim = 2.0 * ((x1 - x0) + (y1 - y0))
    return {"x0": x0, "x1": x1, "y0": y0, "y1": y1, "area": (x1 - x0) * (y1 - y0),
            "reach": reach, "fasteners": max(4, int(math.ceil(perim / FASTENER_PITCH)))}


def ledger_hover():
    with open(LEDGER, encoding="utf-8") as fh:
        c = json.load(fh)["configs"]["hover_twin_2200"]
    return c["mass_g"], c["cg"][1]


def cg_moves(boxes: list[Box]) -> dict[str, Any]:
    m0, y0 = ledger_hover()
    by = {b.name: b for b in boxes}
    fe = by.get("Flight Engineer box")
    rows: list[tuple[str, float, float | None, float]] = []
    moment = 0.0
    dm = 0.0
    if fe:
        yc = 0.5 * (fe.y0 + fe.y1)
        rows.append(("Flight Engineer box", MASS["Flight Engineer box"], FE_FROM_Y, yc))
        moment += MASS["Flight Engineer box"] * (yc - FE_FROM_Y)
    for b in boxes:
        if b.name.startswith(("tail speed controller", "RCS gateway", "RCS servo")):
            key = "RCS servo" if b.name.startswith("RCS servo") else b.name
            m = MASS[key]
            yc = 0.5 * (b.y0 + b.y1)
            rows.append((b.name, m, None, yc))
            moment += m * (yc - y0)
            dm += m
    return {"m0": m0, "y0": y0, "dm": dm, "dy": moment / (m0 + dm), "rows": rows}


def aft_allowance(boxes: list[Box], cg: dict[str, Any]) -> dict[str, Any]:
    """R34: an aft allowance with CG travel >= the bow pocket's.  Two candidates: (a) a
    movable-equipment allowance -- a second, aft mount for the speed controller, gateway and
    servos at the cargo bay's aft end; (b) an aft ballast pocket at the bay's aft floor."""
    m = cg["m0"] + cg["dm"]
    movers = [b for b in boxes if b.name.startswith(("tail speed controller", "RCS gateway",
                                                     "RCS servo"))]
    aft_y = BAY_Y1 - 12.0
    mm = sum(MASS["RCS servo" if b.name.startswith("RCS servo") else b.name] for b in movers)
    mom = sum(MASS["RCS servo" if b.name.startswith("RCS servo") else b.name]
              * (aft_y - 0.5 * (b.y0 + b.y1)) for b in movers)
    travel_a = mom / m
    need_g = BOW_POCKET_TRAVEL * m / (aft_y - cg["y0"])
    rear = REAR_BALLAST_CAP * (REAR_BALLAST_Y - cg["y0"]) / (m + REAR_BALLAST_CAP)
    return {"movable_travel": travel_a, "movable_mass": mm, "aft_y": aft_y,
            "ballast_g": need_g, "ballast_cm3": need_g / BALLAST_RHO,
            "rear_travel": rear, "total": travel_a + rear, "target": BOW_POCKET_TRAVEL}


def motor_lead(boxes: list[Box]) -> dict[str, float]:
    esc = next(b for b in boxes if b.name == "tail speed controller")
    yc, zc = 0.5 * (esc.y0 + esc.y1), 0.5 * (esc.z0 + esc.z1)
    length = abs(TAIL_MOTOR_Y - yc) + abs(TAIL_MOTOR_Z - zc) + LEAD_SLACK
    import tail_edf_flow as tf
    p = tf.Inputs().p_elec_w * HOVER_THROTTLE ** 3
    i_bus = p / V_BUS
    drop = i_bus * AWG14_OHM_PER_M * length / 1e3 * 2.0
    return {"length_mm": length, "i_hover": i_bus, "drop_v": drop,
            "drop_pct": 100.0 * drop / V_BUS, "p_hover": p}


# --- evaluation ---------------------------------------------------------------------------------
def evaluate() -> dict[str, Any]:
    st = stations()
    cav = {y: cavity(y) for y in st}
    belly_z = floor_z(-FAIRLEAD_R, FAIRLEAD_R, PIVOT_Y - 2.0, PIVOT_Y + 2.0) - GAP
    fixed, w = fixed_boxes(belly_z)
    placed = kept_boxes() + fixed
    baseline = {y: free_area(y, placed) for y in st}
    _BASE.clear()
    _BASE.update(baseline)
    moved = []
    why = {}
    for name, size in moved_items():
        b = place_forward(name, size, placed)
        if b is not None:
            placed.append(b)
            moved.append(b)
        else:
            moved.append(Box(name, 0, 0, 0, 0, 0, 0, "unplaced"))
            why[name] = blockers(name, size, placed)
    final = {y: free_area(y, placed) for y in st}
    pts = line_points(w["line"])
    g = next(b for b in placed if b.kind == "guard")
    inside = all(g.x0 + 1.0 <= p[0] <= g.x1 - 1.0 and g.y0 <= p[1] <= g.y1
                 and g.z0 <= p[2] <= g.z1 for p in pts)
    pairs = []
    real = [b for b in placed if b.kind not in ("recess",)]
    for i, a in enumerate(real):
        for b in real[i + 1:]:
            if a.kind == "kept" and b.kind == "kept":
                continue
            if a.name.startswith("winch ") and b.name.startswith("winch "):
                continue
            if a.name.startswith(LINE_SYSTEM) and b.name.startswith(LINE_SYSTEM):
                continue  # the guard joins the drum to the fairlead; the recess is coaxial
            v = overlap(a, b)
            if v > 0.0:
                pairs.append((a.name, b.name, v))
    panel = belly_panel(placed)
    cg = cg_moves(placed)
    scr = screen_frame()
    r = {"stations": st, "closing": {y: cav[y][1] for y in st}, "baseline": baseline,
         "final": final, "belly_z": belly_z, "winch": w, "line_inside": inside,
         "placed": placed, "moved": moved, "why": why, "pairs": pairs, "screen": scr,
         "screen_cover": screen_coverage(scr, ramp_opening()), "panel": panel, "cg": cg,
         "aft": aft_allowance(placed, cg),
         "lead": motor_lead(placed) if any(b.name == "tail speed controller" and
                                           b.kind != "unplaced" for b in moved) else None}
    r["limits"] = limits(r)
    return r


def limits(r) -> list[tuple[str, float, str, float, str]]:
    """THE limits list: (name, value, comparison, limit, unit)."""
    bay = [y for y in r["stations"] if BAY_Y0 <= y <= BAY_Y1]
    out: list[tuple[str, float, str, float, str]] = [
        ("every bay station is a closed duct (seams closed at <= 4 mm)",
         float(sum(1 for y in bay if r["closing"][y] is None)), "<=", 0.0, "stations"),
        ("stream free area kept at the floor wherever it met it before U6 (least such station "
         "after)", min((r["final"][y] for y in bay if r["baseline"][y] >= A_STREAM_MIN),
                       default=math.inf), ">=", A_STREAM_MIN, "mm2"),
        ("fairlead under the tilt pivot (R14)", 0.0, "<=", 0.5, "mm"),
        ("winch line inside its guard, drum to fairlead (R26)", 1.0 if r["line_inside"] else 0.0,
         ">=", 1.0, ""),
        ("envelope overlaps (moved and fixed items)", float(len(r["pairs"])), "<=", 0.0, ""),
        ("the screen covers the whole ramp opening (R6)", r["screen_cover"], ">=", 1.0, ""),
    ]
    for b in r["moved"]:
        out.append((f"placed clear of the hull, its neighbours and the stream: {b.name}",
                    0.0 if b.kind == "unplaced" else 1.0, ">=", 1.0, ""))
    for name, f in r["panel"]["reach"].items():
        out.append((f"reachable through the belly service panel (R12): {name}", f, ">=",
                    REACH_MIN, "of footprint"))
    a = r["aft"]
    out.append(("R34 aft allowance (movable equipment + rear-cone ballast provision) >= the bow "
                "pocket's travel (PLACEHOLDER until U7)", a["total"], ">=", a["target"], "mm"))
    for b in r["placed"]:
        if is_pcb(b.name) and not b.name.endswith("cable zone") and b.kind != "unplaced":
            out.append((f"PCB in line with the airflow, not an air dam: {b.name}",
                        1.0 if in_line(b) else 0.0, ">=", 1.0, ""))
    pinch = [y for y in r["stations"] if BAY_Y0 <= y <= BAY_Y1
             and r["baseline"][y] < A_STREAM_MIN]
    out.append(("U6 adds no blockage where the kept equipment already pinches the stream",
                max((r["baseline"][y] - r["final"][y] for y in pinch), default=0.0), "<=", 0.5,
                "mm2"))
    return out


def passed(lim) -> bool:
    _, v, op, l, _ = lim
    return v >= l if op == ">=" else v <= l


def inch(mm: float) -> str:
    return f"{mm / 25.4:.2f} in ({mm:.1f} mm)"


def report(r) -> bool:
    print("CARGO DUCT LAYOUT (plan 002 U6, TEDF-06), frame R2, mm.  PROVISIONAL.")
    print(f"ASSUMED: gap {GAP} mm; speed controller {ESC_BOX}; gateway {GATEWAY_BOX}; servo "
          f"envelope {SERVO_BOX} (KST CM07 {CM07} over lugs + horn and cable exit); fairlead boss r {FAIRLEAD_R} x "
          f"{FAIRLEAD_H}; hook recess r {HOOK_R} x {HOOK_DEPTH}; guard r {GUARD_R}; panel reach "
          f"{REACH}, land {PANEL_EDGE}, fastener pitch {FASTENER_PITCH}; masses {MASS}.")
    print(f"PLACEHOLDERS: bow pocket CG travel {BOW_POCKET_TRAVEL} mm (U7 sizes it); flow "
          "guides (U2 names the nodes and sizes them).")
    print(f"  stream floor {A_STREAM_MIN:.0f} mm2 ({A_STREAM_MIN / 645.16:.1f} in2): owner "
          "benchmark 2026-11-19, held by every future change (airframe/AGENTS.md)")
    print("  duct free area by station, before -> after the U6 moves (mm2): " + ", ".join(
        f"Y{y:.0f} {r['baseline'][y]:.0f}->{r['final'][y]:.0f}" for y in r["stations"]))
    hand = ("as drawn" if r["winch"]["hand"] > 0
            else "mirrored (servo to starboard, clear of the port tilt drive)")
    print(f"  winch stack {hand}, on a plinth over the hook recess")
    print(f"  belly floor under the pivot Z {r['belly_z']:.1f}; spool centre Z "
          f"{r['winch']['spool_z']:.1f}; line from the drum tangent (Y "
          f"{r['winch']['line']['tan_y']:.1f} Z {r['winch']['line']['tan_z']:.1f}) to the "
          f"fairlead mouth (Y {PIVOT_Y:.1f} Z {r['winch']['line']['mouth_z']:.1f}), "
          f"{inch(r['winch']['line']['length'])}")
    print("  moved forward (R19, KD11):")
    for b in r["moved"]:
        if b.kind == "unplaced":
            print(f"    {b.name}: NO station found in the bay.  What rejects the candidates "
                  f"(counts over a 6 mm grid, six orientations): {r['why'].get(b.name)}.  "
                  "Plan 002 risk table: the fallback is the winch and Cargo Observer moves of "
                  "KD7 (owner decision at G1).")
            continue
        print(f"    {b.name}: X {b.x0:.1f}..{b.x1:.1f}, Y {b.y0:.1f}..{b.y1:.1f}, Z {b.z0:.1f}.."
              f"{b.z1:.1f}")
    p = r["panel"]
    print(f"  belly service panel (R12): opening X {p['x0']:.1f}..{p['x1']:.1f}, Y {p['y0']:.1f}.."
          f"{p['y1']:.1f} ({p['area'] / 645.16:.1f} in2), {p['fasteners']} captive quarter-turn "
          "fasteners in metal receptacles (part to be sourced and verified, R12), gasketed, "
          "tethered")
    cg = r["cg"]
    print(f"  CG effect on hover_twin_2200 ({cg['m0']:.0f} g, CG Y {cg['y0']:.1f}): "
          f"{cg['dy']:+.2f} mm ({cg['dy'] / 25.4:+.3f} in) with {cg['dm']:.0f} g added")
    for name, m, frm, to in cg["rows"]:
        print(f"    {name}: {m:.1f} g " + (f"from Y {frm:.1f} " if frm else "") + f"at Y {to:.1f}")
    a = r["aft"]
    print(f"  R34 aft allowance: movable equipment ({a['movable_mass']:.0f} g, second mount at Y "
          f"{a['aft_y']:.0f}) gives {a['movable_travel']:.2f} mm aft; a rear-cone ballast "
          f"provision at Y {REAR_BALLAST_Y:.0f} holding {REAR_BALLAST_CAP:.0f} g (ASSUMED) adds "
          f"{a['rear_travel']:.2f} mm; together {a['total']:.2f} mm against the "
          f"{a['target']} mm placeholder.  (A cargo-floor pocket alone at Y {a['aft_y']:.0f} "
          f"would need {a['ballast_g']:.0f} g.)")
    pinch = [y for y in r["stations"] if BAY_Y0 <= y <= BAY_Y1
             and r["baseline"][y] < A_STREAM_MIN]
    if pinch:
        print(f"  FINDING: before U6 the kept equipment already pinches the stream below "
              f"{A_STREAM_MIN:.0f} mm2 at Y "
              + ", ".join(f"{y:.0f} ({r['baseline'][y]:.0f})" for y in pinch)
              + ": the aft avionics nodes N2/N4 with the Observer tray, and the ramp fairing "
              "with the chin shelf.  tools/tail_edf_flow.py a_cargo should take the least "
              "figure (U3 recalibration, TEDF-03).")
    if r["lead"]:
        ld = r["lead"]
        print(f"  speed controller to tail motor: {inch(ld['length_mm'])} per phase lead, 14 AWG "
              f"(ASSUMED); hover {HOVER_THROTTLE:.0%}: {ld['p_hover']:.0f} W, {ld['i_hover']:.1f} A"
              f" bus; drop over two leads {ld['drop_v']:.2f} V ({ld['drop_pct']:.1f} %)")
    print("  R25 openings to outside air (the only ones allowed): ramp louvres, bow inlets, "
          "nozzle, RCS exhausts, belly panel seal, Bay A hatch seal, winch fairlead, Cargo "
          "Observer orifices.  FINDING: the wing-spar bore at the pivot opens the duct to the "
          "wing roots unless the spar's ends are capped; the cargo-door apertures close only "
          "when the doors are fused into the skin (KD5, U13).")
    sc = r["screen"]
    ox0, ox1, oz0, oz1 = ramp_opening()
    print(f"  ramp (R5, R6, KD6): louvre panel on the canon outline over the {ox1 - ox0:.1f} x "
          f"{oz1 - oz0:.1f} mm opening ({(ox1 - ox0) * (oz1 - oz0):.0f} mm2); screen behind it "
          f"in a printed frame X {sc['x0']:.1f}..{sc['x1']:.1f}, Z {sc['z0']:.1f}..{sc['z1']:.1f}"
          f", Y {sc['y0']:.1f}..{sc['y1']:.1f} ({SCREEN_LAND:.0f} mm land; louvre open-area "
          "ratio 0.55 ASSUMED, tools/tail_edf_flow.py).  Flow guides: chin passage to about "
          "3,000 mm2 (plan U6 step 5) -- PLACEHOLDER until U2 names the nodes.")
    print("\n  check | value | limit | result")
    ok = True
    for lim in r["limits"]:
        name, v, op, l, unit = lim
        good = passed(lim)
        ok = ok and good
        print(f"  {'PASS' if good else 'FAIL'}  {name}: {v:.3g} {op} {l:.3g} {unit}")
    print("\nRESULT:", "PASS -- PROVISIONAL" if ok else "FAIL -- see the rows above")
    return ok


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", help="write the evaluation to this JSON file")
    a = ap.parse_args(argv)
    r = evaluate()
    ok = report(r)
    if a.json:
        dump = {"limits": [list(x) + [passed(x)] for x in r["limits"]],
                "moved": [b.__dict__ for b in r["moved"]], "panel": r["panel"],
                "cg": {k: v for k, v in r["cg"].items() if k != "rows"}, "aft": r["aft"],
                "free_area": {f"{y:g}": r["final"][y] for y in r["stations"]}}
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(dump, fh, indent=1, default=str)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
