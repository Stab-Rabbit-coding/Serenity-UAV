#!/usr/bin/env python3
"""node_thermal_forced_air.py -- forced-air thermal budget for every CN/FC
node: one rear fan pulling a single stream from bow inlets to the tail, with
16 ga brass heat spreaders where the pouch alone is not enough (owner,
2026-11-01).

AIR PATH (owner, 2026-11-01).  One fan, Delta ASB02505SHA-AY6B (25 x 25 x
10 mm, 5 VDC) [REF-FAN-001], sits in the REAR cone and PULLS outside air:
  bow inlets beside the sensor bay -> inlet duct into CN1's side channels
  (Bay A) -> FC1 -> under/around the twin pack tray -> chin nodes CN2/CN3 ->
  aft nodes FC2/FC3 -> cargo/middle collar -> past the Flight Engineer can ->
  Simon stack CN4/FC4 (middle neck) -> rear cone -> fan -> the Phase 11 fixed
  elliptical tail nozzle exit, 2.06 x 1.76 in (52.3 x 44.7 mm)
  (deferred/WBS.md Phase 11; outline per QMx [REF-CAD-003] / Henning
  [REF-CAD-002]).
Every node sees the inlet air plus the heat of every node upstream of it.
The fan motor heat leaves downstream of every node.

METHOD (mechanical-engineering skill: plane-wall conduction, convection,
series/parallel resistances; Darcy-Weisbach minor losses; the fin rule).
  1. Fan operating point: the datasheet P-Q curve [REF-FAN-001 p.4,
     digitized] meets the system curve, the sum over the stream stations of
     K * rho/2 * (Q/A)^2.  A is the free area MEASURED at each station (hull
     cavity minus every equipment section); K = 1.0 (sudden expansion) after
     each restriction, 1.5 at the inlets (entry + expansion), 1.0 at the
     exit.  Straight-run friction is neglected (short, wide path) -- stated.
  2. Air temperature at each node: T_in + sum(P upstream)/(m_dot c_p).
  3. Film coefficient: laminar flat plate, average, Nu_L = 0.664 Re^1/2
     Pr^1/3 (Re_L < 5e5) [REF-HT-001, section number requires verification],
     L = pouch length in the flow (58 mm), V = Q / A at the node's station.
  4. Node: board -> pouch film (washed pouch area) in parallel with
     board -> contact -> 16 ga brass spreader -> air.  The spreader is set
     flush into the node's mount floor under the pouch and runs out beside it
     as straight plate fins, insulated tips, top face washed:
     eta = tanh(mL)/(mL), m = sqrt(h/(k t)) [REF-HT-001].
  5. Sizing: the smallest overhang per side that holds the limit, against the
     room MEASURED beside the pouch in the spreader plane; and the highest
     sustained dissipation the largest fitting plate can carry (the
     transmit-throttle target).

ASSUMED inputs are labelled; any PASS resting on one is PROVISIONAL.
Brass: C26000 cartridge brass, k 70 Btu/(hr ft F) (121.2 W/m-K), density
0.308 lbm/in^3 (8.53 g/cm^3) at 68 F [REF-MAT-008].  16 ga = 0.0508 in
(1.29 mm), B&S gauge (verify against the purchased sheet).

Run:
    /usr/bin/python3 tools/node_thermal_forced_air.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the
author's direction, 2026-11-01, per `AGENTS.md` §3 AI attribution.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import math
import os
import sys
from dataclasses import dataclass

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# --- fan [REF-FAN-001] -------------------------------------------------------
FAN_MPN = "Delta Electronics ASB02505SHA-AY6B"
FAN_W = 0.60  # rated power, W
FAN_G = 5.6  # mass, g (datasheet §3-5, "REF.")
FAN_FRAME_MM, FAN_DEPTH_MM = 25.0, 10.0
# P-Q curve, digitized from the datasheet p.4 at 5 V: (m^3/min, mmH2O)
FAN_PQ = ((0.000, 8.13), (0.025, 6.1), (0.050, 3.6), (0.065, 2.75), (0.075, 2.5),
          (0.100, 1.7), (0.122, 0.0))
MMH2O_PA = 9.80665

# --- air [REF-HT-001 air table; requires verification] ------------------------
CP_AIR = 1007.0  # J/kg-K
K_AIR, NU_AIR, PR_AIR = 0.02808, 1.896e-5, 0.7202  # at a 60 C film temperature
R_AIR = 287.05  # J/kg-K, ideal gas

# --- brass [REF-MAT-008] -------------------------------------------------------
K_BRASS = 121.2  # W/m-K
RHO_BRASS = 8530.0  # kg/m^3
T_16GA = 0.0508 * 0.0254  # m

# --- node pouch (cargo_layout_fit.NODE_*) --------------------------------------
NODE_L, NODE_W, NODE_T = 0.058, 0.037, 0.022

# --- stations -------------------------------------------------------------------
# key -> (station Y, pouch X0, X1, Z0, Z1), aircraft datum R2, mm (from
# head_layout_fit / cargo_layout_fit / middle_layout_fit, 2026-11-01)
POUCH = {
    "CN1": (91.0, -18.5, 18.5, 206.0, 228.0),
    "FC1": (117.0, -18.5, 18.5, 230.5, 252.5),
    "CN2": (273.1, 5.0, 42.0, 146.0, 168.0),
    "CN3": (273.1, -42.0, -5.0, 146.0, 168.0),
    "FC2": (416.2, 1.0, 59.0, 167.0, 204.0),
    "FC3": (416.2, -60.0, -2.0, 167.0, 204.0),
    "CN4": (494.7, -29.0, 29.0, 122.0, 144.0),
    "FC4": (494.7, -29.0, 29.0, 147.0, 169.0),
}
# Longest plate along the flow each mount floor can carry (mm): CN1 drawer
# floor + wall run Y 60..146; FC1 shelf Y 88..146; the chin shelf and the aft
# and Simon saddles carry the pouch footprint only until they are redrawn.
W_MAX = {"CN1": 84.0, "FC1": 58.0, "CN2": 58.0, "CN3": 58.0, "FC2": 58.0, "FC3": 58.0,
         "CN4": 58.0, "FC4": 58.0}
OWNER_GUESS_IN = (12.0, 2.0)  # owner's rough spreader size (length x width), in
# Mount parts the spreader passes under (excluded from the room check).
OWN_MOUNT = {"CN1": ("drawer", "CN1 gate", "CN1 node", "CN1 (fwd"),
             "FC1": ("FC1 shelf", "FC1 (raised"), "CN2": ("N1 CN2", "chin shelf"),
             "CN3": ("N3 CN3", "chin shelf"), "FC2": ("N2 FC2",), "FC3": ("N4 FC3",),
             "CN4": ("CN4", "Simon saddle"), "FC4": ("FC4", "CN4")}
# Stream stations in flow order: (key, station Y mm, minor-loss K after it).
STREAM = (("INLET", None, 1.5), ("CN1", 91.0, 1.0), ("FC1", 117.0, 1.0),
          ("CHIN", 273.1, 1.0), ("AFT", 416.2, 1.0), ("COLLAR", 441.0, 1.0),
          ("FE", 467.7, 1.0), ("SIMON", 494.7, 1.0), ("EXIT", None, 1.0))
NODE_STATION = {"CN1": "CN1", "FC1": "FC1", "CN2": "CHIN", "CN3": "CHIN", "FC2": "AFT",
                "FC3": "AFT", "CN4": "SIMON", "FC4": "SIMON"}
NOZZLE_A, NOZZLE_B = 52.3, 44.7  # mm, Phase 11 fixed elliptical exit (deferred/WBS.md)
NOZZLE_AREA_M2 = math.pi / 4 * NOZZLE_A * NOZZLE_B * 1e-6
# CN1 is ducted: the inlet duct delivers the bow air into the two side
# channels beside the CN1 drawer, where its spreader runs.  (|X| >=, Z0, Z1)
DUCT_WINDOW = {"CN1": (19.5, 203.0, 228.0)}


@dataclass
class Node:
    name: str
    y_mm: float
    p_avg: float
    p_peak: float
    exposed: float  # fraction of the pouch area washed by the stream -- ASSUMED per mount
    room_mm: float  # measured spreader room per side


@dataclass
class Inputs:
    t_ambient_c: float = 40.0  # ASSUMED design ambient, owner to confirm (BAYA-FWD-T2)
    t_limit_c: float = 85.0  # PB2-I module rating (module spec, not an owner requirement)
    a_inlet_m2: float = 2 * 25e-6 * 16  # two 25 x 16 mm bow inlet slots
    r_contact: float = 1.5  # K/W pouch -> brass (fabric + adhesive) -- ASSUMED
    cn_avg_w: float = 3.0  # docs/AVIONICS_PB2_REDESIGN.md §Power
    cn_peak_w: float = 8.3
    fc_w: float = 1.25


# --- geometry, measured at run time ---------------------------------------------
_GEOM: dict = {}


def _geometry():
    """Hulls (merged head+cargo, middle, rear) and every equipment envelope in
    the published layout, named.  Cached for the run."""
    if _GEOM:
        return _GEOM
    import trimesh
    import cargo_layout_fit as c
    import head_layout_fit as h
    import middle_layout_fit as mlf
    import twin_head_pack_fit as t
    fs = os.path.join(h.REPO, "airframe", "stls", "fuselage")
    hulls = [(trimesh.load(h.MERGED), 436.7), (trimesh.load(mlf.MIDDLE_SHELL), 508.0),
             (trimesh.load(os.path.join(fs, "rear_shell24_2mm_repaired.stl")), 1e9)]
    solids = [(k, e["solid"]) for k, e in h.layout()[0].items()]
    hw = t.TRAY_W / 2
    solids.append(("twin tray", c.box(-hw - 2.4, hw + 2.4, t.TRAY_Y0 - 4, t.TRAY_Y1,
                                      t.TRAY_ZC - t.TRAY_H / 2 - 2.4,
                                      t.TRAY_ZC + t.TRAY_H / 2 + 2.4)))
    for k, e in c.layout_t5().items():
        if k in ("battery", "battery cradle") or "cradle" in k:
            continue
        solids.append(("cargo: " + k, e["solid"]))
        if e.get("mirror"):
            solids.append(("cargo: " + k + " (stbd)", c.mirror_x(e["solid"])))
    for k, e in mlf.layout_t6().items():
        solids.append(("middle: " + k, e["solid"]))
    _GEOM.update(hulls=hulls, solids=solids)
    return _GEOM


def _hull_at(y):
    for mesh, y_end in _geometry()["hulls"]:
        if y <= y_end:
            return mesh
    raise ValueError(y)


def _xz(mesh, y, rings="exterior"):
    """Section rings at y as (X, Z) polygons: exteriors, or interiors."""
    from shapely.geometry import Polygon
    sec = mesh.section(plane_origin=[0.0, y, 0.0], plane_normal=[0.0, 1.0, 0.0])
    if sec is None:
        return []
    p, T = sec.to_2D()
    out = []
    for q in p.polygons_full:
        loops = [q.exterior] if rings == "exterior" else list(q.interiors)
        for ring in loops:
            pts = np.array(ring.coords)
            w = (T @ np.c_[pts, np.zeros(len(pts)), np.ones(len(pts))].T).T[:, :3]
            poly = Polygon(np.c_[w[:, 0], w[:, 2]]).buffer(0)
            if poly.area > 0:
                out.append(poly)
    return out


def cavity_at(y):
    """Hull cavity at y: the largest interior ring of the section (the
    middle_layout_fit.neck_void method)."""
    rings = _xz(_hull_at(y), y, "interiors")
    if not rings:
        raise ValueError(f"no hull cavity at Y {y}")
    return max(rings, key=lambda q: q.area)


def measure_free_area(y, key=None):
    """Free flow area (m^2): cavity minus every equipment section at y; inside
    DUCT_WINDOW[key] for a ducted station."""
    from shapely.geometry import box as sbox
    from shapely.ops import unary_union
    eq = unary_union([p for _, s in _geometry()["solids"] for p in _xz(s, y)])
    free = cavity_at(y).difference(eq)
    if key in DUCT_WINDOW:
        xin, z0, z1 = DUCT_WINDOW[key]
        free = free.intersection(unary_union([sbox(xin, z0, 200.0, z1),
                                              sbox(-200.0, z0, -xin, z1)]))
    return float(free.area) * 1e-6


def station_areas(inp):
    """[(key, y, K, free area m^2)] for every stream station, in flow order."""
    out = []
    for key, y, k in STREAM:
        if key == "INLET":
            a = inp.a_inlet_m2
        elif key == "EXIT":
            a = NOZZLE_AREA_M2
        else:
            a = measure_free_area(y, key)
        if a <= 0:
            raise ValueError(f"stream blocked at {key} (free area {a})")
        out.append((key, y, k, a))
    return out


def measure_room(key):
    """Spreader room per side (mm): in the plane 0.65 mm under the pouch (mid
    thickness of a 16 ga plate flush in the mount floor), the smaller port /
    stbd gap from the pouch side to the skin or the nearest OTHER equipment,
    less 1 mm, by ray cast in X."""
    import trimesh
    y, x0, x1, z0, _ = POUCH[key]
    own = OWN_MOUNT[key]
    meshes = [_hull_at(y)] + [s for name, s in _geometry()["solids"]
                              if not any(o in name for o in own)]
    scene = trimesh.util.concatenate(meshes)
    gaps = []
    for xs, d in ((x1 + 0.01, 1.0), (x0 - 0.01, -1.0)):
        loc, _, _ = scene.ray.intersects_location([[xs, y, z0 - 0.65]], [[d, 0.0, 0.0]])
        gaps.append(float(np.min(np.abs(loc[:, 0] - xs))) if len(loc) else 0.0)
    return max(0.0, min(gaps) - 1.0)


def nodes(inp):
    """Every CN/FC node in flow order."""
    cn, fc = (inp.cn_avg_w, inp.cn_peak_w), (inp.fc_w, inp.fc_w)
    spec = (("CN1", "Bay A (TACCO)", cn, 0.35), ("FC1", "Bay A (Pilot)", fc, 0.55),
            ("CN2", "chin port (TACCO)", cn, 0.35), ("CN3", "chin stbd (TACCO)", cn, 0.35),
            ("FC2", "aft port (Pilot)", fc, 0.70), ("FC3", "aft stbd (Pilot)", fc, 0.70),
            ("CN4", "Simon (TACCO)", cn, 0.50), ("FC4", "Simon (Pilot)", fc, 0.50))
    return [Node(f"{k} {d}", POUCH[k][0], p[0], p[1], exposed=e, room_mm=measure_room(k))
            for k, d, p, e in spec]


# --- fan and system ---------------------------------------------------------------
def fan_dp(q_m3s):
    """Fan static pressure (Pa) at flow q, linear between digitized points."""
    qs = [p[0] / 60.0 for p in FAN_PQ]
    ps = [p[1] * MMH2O_PA for p in FAN_PQ]
    return float(np.interp(q_m3s, qs, ps, right=0.0))


def system_dp(q_m3s, rho, areas):
    """Sum of K * rho/2 * V^2 over the stream stations."""
    return sum(k * 0.5 * rho * (q_m3s / a) ** 2 for _, _, k, a in areas)


def operating_point(inp, areas):
    """Bisect fan_dp(q) = system_dp(q).  Returns (q m^3/s, dp Pa, rho)."""
    rho = 101325.0 / (R_AIR * (inp.t_ambient_c + 273.15))
    lo, hi = 0.0, FAN_PQ[-1][0] / 60.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if fan_dp(mid) > system_dp(mid, rho, areas):
            lo = mid
        else:
            hi = mid
    return lo, fan_dp(lo), rho


# --- node heat path -----------------------------------------------------------------
def h_flat_plate(v):
    """Average laminar flat-plate film coefficient over the pouch length."""
    re = v * NODE_L / NU_AIR
    if re >= 5e5:
        raise ValueError(f"Re {re:.0f} outside the laminar correlation")
    return 0.664 * math.sqrt(re) * PR_AIR ** (1 / 3) * K_AIR / NODE_L, re


def _fin(h, length_m, width_m, sides=1):
    """Straight rectangular fin, insulated tip [REF-HT-001]: h * A * eta."""
    if length_m <= 0 or width_m <= 0:
        return 0.0
    m = math.sqrt(sides * h / (K_BRASS * T_16GA))
    ml = m * length_m
    return sides * h * length_m * width_m * math.tanh(ml) / ml


def spreader_conductance(h, overhang_m, width_m=NODE_L, sides=1):
    """16 ga plate under the pouch, top face washed: two lateral fins
    (overhang each side, `width_m` along the flow) plus fore/aft fins when the
    plate is longer than the pouch.  Corners ignored (conservative).  W/K."""
    g = 2 * _fin(h, overhang_m, width_m, sides)
    extra = max(0.0, width_m - NODE_L) / 2
    return g + 2 * _fin(h, extra, NODE_W, sides)


def _g_node(inp, h, exposed, overhang_m, width_m):
    area = exposed * 2 * (NODE_L * NODE_W + NODE_L * NODE_T + NODE_W * NODE_T)
    g_fin = spreader_conductance(h, overhang_m, width_m)
    return h * area + (1.0 / (inp.r_contact + 1.0 / g_fin) if g_fin > 0 else 0.0)


def board_temp(inp, h, t_air, p, exposed, overhang_m, width_m=NODE_L):
    return t_air + p / _g_node(inp, h, exposed, overhang_m, width_m)


def required_overhang(inp, h, t_air, p, exposed, width_m=NODE_L, max_mm=400.0):
    """Smallest overhang per side (mm) that holds the limit, or None."""
    if board_temp(inp, h, t_air, p, exposed, 0.0, width_m) <= inp.t_limit_c:
        return 0.0
    if board_temp(inp, h, t_air, p, exposed, max_mm / 1000, width_m) > inp.t_limit_c:
        return None
    lo, hi = 0.0, max_mm / 1000
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if board_temp(inp, h, t_air, p, exposed, mid, width_m) > inp.t_limit_c:
            lo = mid
        else:
            hi = mid
    return hi * 1000


def max_sustained_w(inp, h, t_air, exposed, room_mm, width_m):
    """Highest steady dissipation (W) holding the limit with the largest plate
    that fits.  Linear in P."""
    return max(0.0, (inp.t_limit_c - t_air) * _g_node(inp, h, exposed, room_mm / 1000, width_m))


def budget(inp=None, case="peak", areas=None, node_list=None):
    """Rows per node in flow order.  The stream heats with each node's `case`
    power; the fan is at the exit, so its motor heat reaches no node."""
    inp = inp or Inputs()
    areas = areas if areas is not None else station_areas(inp)
    area_of = {k: a for k, _, _, a in areas}
    q, dp, rho = operating_point(inp, areas)
    m_dot = rho * q
    t_air = inp.t_ambient_c
    rows = []
    for n in node_list if node_list is not None else nodes(inp):
        p = n.p_peak if case == "peak" else n.p_avg
        key = n.name.split()[0]
        v = q / area_of[NODE_STATION[key]]
        h, re = h_flat_plate(v)
        w = W_MAX[key] / 1000
        need = required_overhang(inp, h, t_air, p, n.exposed, w)
        if need is None:
            status = "FAIL (no spreader size)"
        elif need == 0.0:
            status = "OK bare"
        elif need <= n.room_mm:
            status = "OK with spreader"
        else:
            status = "FAIL (no room)"
        plate = None if not need else ((2 * need / 1000 + NODE_W), w)  # m (across, along)
        rows.append(dict(
            name=n.name, t_air=t_air, v=v, re=re, h=h,
            t_bare=board_temp(inp, h, t_air, p, n.exposed, 0.0), need_mm=need,
            room_mm=n.room_mm, status=status, plate=plate,
            brass_g=0.0 if not plate else plate[0] * plate[1] * T_16GA * RHO_BRASS * 1e3,
            p_max=max_sustained_w(inp, h, t_air, n.exposed, n.room_mm, w)))
        t_air += p / (m_dot * CP_AIR)
    return rows, (q, dp, rho)


def main():
    inp = Inputs()
    areas = station_areas(inp)
    q, dp, rho = operating_point(inp, areas)
    node_list = nodes(inp)
    print("stream free areas: " + ", ".join(f"{k} {a * 1e6:.0f} mm2" for k, _, _, a in areas))
    print(f"fan {FAN_MPN}: {q * 60:.3f} m^3/min ({q * 2118.88:.2f} CFM) at {dp:.1f} Pa "
          f"({dp / 249.089:.3f} in H2O); inlet {inp.t_ambient_c:.0f} C (ASSUMED)")
    fails = 0
    for case in ("average", "peak"):
        rows, _ = budget(inp, case, areas, node_list)
        print(f"\n{case}: node | air C | V m/s | Re | h W/m2K | bare board C | spreader "
              f"need/room mm per side | status")
        for r in rows:
            need = "-" if r["need_mm"] is None else f"{r['need_mm']:.0f}"
            pl = "" if not r["plate"] else (
                f"  plate {r['plate'][0] / 0.0254:.2f} x {r['plate'][1] / 0.0254:.2f} in "
                f"({r['plate'][0] * 1e3:.0f} x {r['plate'][1] * 1e3:.0f} mm), "
                f"{r['brass_g'] / 28.3495:.2f} oz ({r['brass_g']:.0f} g)")
            print(f"  {r['name']:24s} {r['t_air']:5.1f} {r['v']:5.2f} {r['re']:6.0f} "
                  f"{r['h']:5.1f} {r['t_bare']:6.1f}  {need:>4s}/{r['room_mm']:.0f}  "
                  f"{r['status']}{pl}  [max sustained {r['p_max']:.1f} W]")
            fails += r["status"].startswith("FAIL")
    print(f"\nRESULT: {'FAIL' if fails else 'PASS'} -- PROVISIONAL (ambient, film, contact, "
          f"minor-loss K and pouch exposure are ASSUMED)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
