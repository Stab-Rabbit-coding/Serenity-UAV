#!/usr/bin/python3
"""BHD-02 option study: geometry and loads for the three owner decisions.

BHD-02 (docs/CARGO_BULKHEAD_FIT_CHECK.md) is the landing-gear bays clashing
with the wing root.  tools/landing_gear_bay_function.py says WHICH feature
hits WHAT; this tool sizes the three ways out that need an owner decision,
with the geometry built from the same posed solids and the loads from the
repo's own load cases:

A  Wing-root flange cut for the fore gear well.
   The bonded root flange (80 x 60 mm, Rev T1c) was added after LG-10 sited
   the fore bays, and it covers the whole fore well: aperture, liner, clevis,
   boss cluster and the swinging thigh.  No reshape of the gear clears the
   THIGH (it must swing), so the flange must be cut.  The cut is the
   projection onto the wall (hull Y-Z) of everything the fore gear puts
   through the flange's X slab -- bay, leg swept 0..26 deg, M3 keep-outs --
   offset by CLR and taken through the plate's thickness, because a printed,
   bonded plate wants a clean through-pocket, not a 3-D sculpted relief.
   Loads: wing root moment, ultimate 14.60 N.m (docs/WING_ATTACH_INTERFACE.md
   SS2.1), reacted by the plate's bonded footprint.  Three models are
   reported, intact vs cut:
     doc     -- the generator docstring's own method, F = 3M/(2h) over A/3,
                kept so the 29.2 baseline is reproduced and comparable;
     bonded  -- linear stress about the net footprint's centroidal axis,
                sigma = M c / I (bond in tension = peel, the honest case);
     bearing -- rigid plate rocking on either edge, triangular pressure
                over the material actually present, p_max = M d_max / sum(d^2 dA).
   Governing = max(bonded, bearing).  Allowable 5 MPa (bond-limited
   CF-PETG, docs/structural_analysis.md -- that document itself says the
   figure predates any cited test value: ASSUMED, not verified).

B  The wire-seat clusters hit the wing (aft bays: seats, bosses, carrier,
   pads; fore bays: carrier, pads, bosses).  Two ways out:
     B1 rotate the whole wire cluster down about the hip pin (CRANK_AZ and
        CHORD_AZ together, so the 90 deg crank-to-chord transmission angle and
        therefore every load is unchanged) -- evaluated by re-running
        landing_gear_bay_function.py with -D overrides; this tool reads those
        JSON results if given (--b1 DELTA=path ...).
     B2 relieve the WING around the cluster -- volume, depth and the wing
        section loss at that station, plus clearance to the CF spar.
   Loads for B1 are identical by construction; the check is clearance.  For B2
   the primary bending path is the CF spar (FOS 9.0 cantilever-bound,
   WING_ATTACH_INTERFACE SS2.2), so the relief is checked for not reaching the
   spar or shaft and for section-area loss.

C  Shared vs handed bays.  The starboard corners are ROTATED (az 180-port), not
   mirrored, so the CF spar crosses the fore bay's top flange at leg-local
   +y on port and -y on starboard.  A spar relief (spar O20 + 2 x CLR) costs
   the upper M3 on that side.  Shared part: relieve both sides, relocate both
   upper bolts.  Handed parts: one each.  Bolt loads by the LG-02 method of
   tools/landing_gear_r6_sizing.py (hip moment 48.8 N.m prying about the
   lower bolt line, F_leg 610 N shared in shear): T_i = M d_i / sum(d_j^2).

Run:  /usr/bin/python3 tools/bhd02_option_study.py --export DIR [--json OUT]
      [--b1 30=b1_30.json --b1 45=b1_45.json]

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, per AGENTS.md AI attribution.
License: MIT (SPDX-License-Identifier: MIT) -- see tools/LICENSE.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
from manifold3d import CrossSection, JoinType, Manifold, OpType
from matplotlib.path import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cargo_bulkhead_context as cbc  # noqa: E402
import landing_gear_bay_function as lgbf  # noqa: E402

CLR = 1.5                 # mm, printed-part clearance around a cut (FDM, bonded)
M_ROOT = 14.60            # N.m, ultimate wing root moment (WING_ATTACH_INTERFACE SS2.1)
SIGMA_ALLOW = 5.0         # MPa, bond-limited CF-PETG -- ASSUMED (see docstring)
FOS_TARGET = 4.0          # project joint target (WING_ATTACH_INTERFACE SS2.1, SS23.2265)
RHO = 1.30e-3             # g/mm^3 CF-PETG solid (generate_wing_root_flange.py)
INFILL = 0.40

# LG-02 bolt case (tools/landing_gear_r6_sizing.py, 4 ft adopted schedule)
M_HIP = 48.8              # N.m, hip moment = 2 P r
F_LEG = 610.0             # N, worst leg force
BOLT_CAP_BEARING = 2100.0  # N, wall + boss + 3 mm backing plate (sizing script)
M3_TENSION = 3521.0       # N, A2-70 (sizing script)

# Bay bolt pattern, plate frame -- canonical_leg_r6_3_0in.scad BAY_BOLT_*.
BOLT_ZB = (-37.0, 31.0)
BOLT_YB = (17.5, 22.0)
APER_W = (25.0, 34.0)     # aperture width bottom / top
APER_ZB0, APER_L, FLANGE = -38.0, 58.0, 10.0
KEEP_D = 3.4 + 2 * 2.5    # M3 keep-out (washer / nut / driver), as the census

# hull (x,y,z) -> (y,z,x) and back, so Manifold.project() gives the wall plane
TO_YZX = [[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0]]


def from_yzx(x0: float) -> list[list[float]]:
    return [[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0]]


def feature(cn: str, name: str, corners: dict, defines=()) -> Manifold:
    """A bay feature posed at corner `cn` (render cached by the census tool)."""
    st = lgbf.STATION[cn]
    p = lgbf.render(lgbf.SCAD, st, name, lgbf.FEATURES[name][0], defines)
    tf = lgbf.corner_tf(corners[cn])
    if name.startswith("leg"):
        return lgbf.swept_leg(p, tf)
    return lgbf.posed(p, tf)


def dilate(m: Manifold, r: float) -> Manifold:
    """Cheap outward offset: union of the solid shifted +/-r on each axis and
    the 8 cube diagonals.  Under-estimates a true offset by < 0.3 r on
    oblique faces -- conservative for a CUT because CLR is added on top."""
    d = r / np.sqrt(3.0)
    shifts = [(s * r, 0, 0) for s in (-1, 1)] + [(0, s * r, 0) for s in (-1, 1)] + \
        [(0, 0, s * r) for s in (-1, 1)] + \
        [(a * d, b * d, c * d) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)]
    return Manifold.batch_boolean([m] + [m.translate(s) for s in shifts], OpType.Add)


# --------------------------------------------------------------------------
# footprint rasterisation and the three flange load models
# --------------------------------------------------------------------------
def raster(cs: CrossSection, pitch: float = 0.25):
    """(Y, Z, mask) grid of a CrossSection in the wall plane (even-odd fill)."""
    (y0, z0), (y1, z1) = np.array(cs.bounds()).reshape(2, 2)
    ys = np.arange(y0 + pitch / 2, y1, pitch)
    zs = np.arange(z0 + pitch / 2, z1, pitch)
    Y, Z = np.meshgrid(ys, zs, indexing="ij")
    pts = np.column_stack([Y.ravel(), Z.ravel()])
    inside = np.zeros(len(pts), bool)
    for poly in cs.to_polygons():
        inside ^= Path(np.asarray(poly)).contains_points(pts)
    return Y, Z, inside.reshape(Y.shape), pitch


def flange_models(cs: CrossSection, m_nm: float = M_ROOT) -> dict:
    """Stress in the bonded footprint under the root moment (axis || hull Y)."""
    Y, Z, k, p = raster(cs)
    dA = p * p
    z = Z[k]
    A = k.sum() * dA
    h = z.max() - z.min()
    M = m_nm * 1e3                                  # N.mm
    doc = (3 * M / (2 * h)) / (A / 3)               # generator docstring method
    zc = z.mean()
    i_yy = ((z - zc) ** 2).sum() * dA
    bonded = M * max(z.max() - zc, zc - z.min()) / i_yy
    bearing = 0.0
    for piv in (z.max(), z.min()):                  # rock on either edge
        d = np.abs(z - piv)
        bearing = max(bearing, M * d.max() / ((d ** 2).sum() * dA))
    gov = max(bonded, bearing)
    return dict(area_mm2=round(A, 0), h_mm=round(h, 1), centroid_z=round(zc, 2),
                I_mm4=round(i_yy, 0), sigma_doc_mpa=round(doc, 3),
                fos_doc=round(SIGMA_ALLOW / doc, 1), sigma_bonded_mpa=round(bonded, 3),
                sigma_bearing_mpa=round(bearing, 3), sigma_gov_mpa=round(gov, 3),
                fos_gov=round(SIGMA_ALLOW / gov, 1), passes=SIGMA_ALLOW / gov >= FOS_TARGET)


def wall_section(m: Manifold) -> CrossSection:
    return m.transform(TO_YZX).project()


# Reshaped fore bays from option C, leg-local: {option: {bay, keep}}.  Option A
# cuts the flange around THESE, because the unrelieved bay overlaps the CF spar
# and a flange cut sized on it would bore the spar socket away.
LOCAL: dict[str, dict] = {}


# --------------------------------------------------------------------------
# A -- root flange cut for the fore well
# --------------------------------------------------------------------------
def option_a(P: dict, corners: dict, out: str | None) -> dict:
    res = {}
    for side, cn in (("port", "fore-port"), ("stbd", "fore-stbd")):
        fl = P[f"root flange {side}"]["m"]
        lo, hi = np.array(fl.bounding_box()).reshape(2, 3)
        tf = lgbf.corner_tf(corners[cn])[:3, :].tolist()
        shaped = LOCAL[f"handed {side}"]
        gear = Manifold.batch_boolean([
            shaped["bay"].transform(tf), shaped["keep"].transform(tf),
            feature(cn, "leg (thigh+shin+foot)", corners)], OpType.Add)
        slab = Manifold.cube(list(hi - lo + [0, 40, 40])).translate(list(lo - [0, 20, 20]))
        through = gear ^ slab
        cut_cs = wall_section(through).offset(CLR, JoinType.Round)
        cut = cut_cs.extrude(hi[0] - lo[0] + 2.0).transform(from_yzx(lo[0] - 1.0))
        parts = sorted((fl - cut).decompose(), key=lambda m: -m.volume())
        cut_fl = parts[0]                    # islands cannot be bonded: dropped
        islands = [round(m.volume(), 0) for m in parts[1:] if m.volume() > 0.5]
        intact = flange_models(wall_section(fl))
        notched = flange_models(wall_section(cut_fl))
        removed = fl.volume() - cut_fl.volume()
        bodies = len(parts)
        clash_after = {n: round((gear ^ cut_fl).volume(), 2) for n in ("gear",)}
        res[side] = dict(intact=intact, cut=notched, removed_mm3=round(removed, 0),
                         removed_g=round(removed * RHO * INFILL, 1),
                         cut_area_mm2=round(cut_cs.area(), 0), bodies_after=bodies,
                         islands_dropped_mm3=islands,
                         gear_vs_cut_flange_mm3=clash_after["gear"],
                         cut_x_cf_spar_mm3=round((P[f"CF spar {side}"]["m"] ^ cut).volume(), 1),
                         # flange left between the cut and the spar: the socket ring
                         cut_to_spar_gap_mm=round(cut.min_gap(
                             P[f"CF spar {side}"]["m"], 20.0), 2))
        if out:
            cbc.tri(cut_fl).export(os.path.join(out, f"A_flange_cut_{side}.stl"))
            cbc.tri(fl ^ cut).export(os.path.join(out, f"A_flange_removed_{side}.stl"))
            cbc.tri(through).export(os.path.join(out, f"A_gear_through_flange_{side}.stl"))
    return res


# --------------------------------------------------------------------------
# B2 -- wing relief around the wire clusters
# --------------------------------------------------------------------------
CLUSTER = ("boss carrier", "wire bosses", "wire seats", "retention pads",
           "cowl (flange+liner)", "M3 bolt keep-out")


def option_b2(P: dict, corners: dict, out: str | None) -> dict:
    res = {}
    for cn in lgbf.CORNER_NAMES:
        side = lgbf.SIDE[cn]
        wing = P[f"wing {side}"]["m"]
        if lgbf.STATION[cn] == "fore" and f"handed {side}" in LOCAL:
            # fore bays: size the wing relief on the option-C reshaped bay
            # (spar relief + relocated bolt); the raw bay overlaps the spar
            tf = lgbf.corner_tf(corners[cn])[:3, :].tolist()
            sh = LOCAL[f"handed {side}"]
            cl = sh["bay"].transform(tf) + sh["keep"].transform(tf)
        else:
            cl = Manifold.batch_boolean([feature(cn, n, corners) for n in CLUSTER],
                                        OpType.Add)
        # A printable wing pocket is ONE clean cut: the convex hull of the
        # dilated cluster.  The raw dilated union shatters the wing section
        # into ~50 slivers (measured 2026-10-10) that no slicer would hold.
        # Exception, the fore corners: their hull bridges the option-C spar
        # relief and breaks the wing's spar-bore wall (0.2 mm), so the fore
        # pocket CONFORMS to the reshaped bay instead (4.1 / 3.5 mm wall left).
        if lgbf.STATION[cn] == "fore":
            relief = dilate(cl, CLR) ^ wing
        else:
            relief = dilate(cl, CLR).hull() ^ wing
        v = relief.volume()
        if v <= 0.05:
            res[cn] = dict(relief_mm3=0.0)
            continue
        lo, hi = np.array(relief.bounding_box()).reshape(2, 3)
        xm = float((lo[0] + hi[0]) / 2)
        # wing chordwise section at the relief's span station, intact vs relieved
        sec0 = wing.transform(TO_YZX).slice(xm)
        sec1 = (wing - relief).transform(TO_YZX).slice(xm)
        res[cn] = dict(
            relief_mm3=round(v, 1), relief_g=round(v * RHO * INFILL, 1),
            box=[lo.round(1).tolist(), hi.round(1).tolist()],
            depth_z_mm=round(float(hi[2] - lo[2]), 1),
            section_x=round(xm, 1), section_area_mm2=round(sec0.area(), 0),
            section_area_after_mm2=round(sec1.area(), 0),
            section_loss_pct=round(100 * (1 - sec1.area() / max(sec0.area(), 1e-9)), 1),
            section_contours=[len(sec0.to_polygons()), len(sec1.to_polygons())],
            gap_to_cf_spar_mm=round(relief.min_gap(P[f"CF spar {side}"]["m"], 50.0), 1),
            gap_to_drive_shaft_mm=round(relief.min_gap(P[f"drive shaft {side}"]["m"], 50.0), 1))
        if out:
            cbc.tri(relief).export(os.path.join(out, f"B2_wing_relief_{cn}.stl"))
    return res


def b1_summary(paths: dict[str, str]) -> dict:
    """Summarise census runs with the wire cluster rotated down by DELTA deg."""
    res = {}
    for delta, path in paths.items():
        R = json.load(open(path, encoding="utf-8"))
        wing = [r for r in R["rows"] if r["target"].startswith("wing") and
                r["feature"] != "bay (printed part)" and r["verdict"] == "CLASH"]
        res[delta] = dict(
            defines=R["defines"],
            wing_clash_mm3={f"{r['corner']} {r['feature']}": r["mm3"] for r in wing},
            new_clashes=sorted({f"{r['corner']} {r['feature']} x {r['target']}"
                                for r in R["rows"] if r["verdict"] == "CLASH"
                                and not r["target"].startswith(("wing", "shell"))}),
            function=R["function"])
    return res


# --------------------------------------------------------------------------
# C -- shared vs handed fore bays (spar relief and the upper bolts)
# --------------------------------------------------------------------------
def aper_half(zb: float) -> float:
    t = (zb - APER_ZB0) / APER_L
    return (APER_W[0] + t * (APER_W[1] - APER_W[0])) / 2.0


def bolt_group(levers: list[float], n_bolts: int = 4) -> dict:
    """LG-02 prying: T_i = M d_i / sum d^2 about the lower bolt line; the leg
    force is shared in shear by all n_bolts (lower bolts have d = 0)."""
    s2 = sum(d * d for d in levers)
    T = [M_HIP * 1e3 * d / s2 for d in levers]
    V = F_LEG / n_bolts
    R = [np.hypot(t, V) for t in T]
    return dict(levers_mm=[round(d, 1) for d in levers], tension_n=[round(t) for t in T],
                shear_n=round(V), resultant_max_n=round(max(R)),
                fos_tension=round(M3_TENSION / max(T), 1),
                fos_bearing=round(BOLT_CAP_BEARING / max(R), 2))


def option_c(P: dict, corners: dict, out: str | None) -> dict:
    """Spar relief in each fore bay, in leg-local, and what it costs the bolts."""
    res = {}
    rel_local = {}
    for side, cn in (("port", "fore-port"), ("stbd", "fore-stbd")):
        spar = P[f"CF spar {side}"]["m"]
        lo, hi = np.array(spar.bounding_box()).reshape(2, 3)
        r = cbc.SPAR_D / 2 + CLR
        cyl = cbc.xcyl(cbc.SPAR_Y, cbc.SPAR_Z, lo[0] - 40, hi[0] + 40, 2 * r)
        cyl = cbc.man(cyl)
        inv = np.linalg.inv(lgbf.corner_tf(corners[cn]))
        rel_local[side] = cyl.transform(inv[:3, :].tolist())
    bay_local = lgbf.posed(lgbf.render(lgbf.SCAD, "fore", "bay (printed part)",
                                       lgbf.FEATURES["bay (printed part)"][0]), np.eye(4))
    keep_local = lgbf.posed(lgbf.render(lgbf.SCAD, "fore", "M3 bolt keep-out",
                                        lgbf.FEATURES["M3 bolt keep-out"][0]), np.eye(4))
    # which bolt keep-outs each relief kills (keep-out solids split per bolt)
    bolts = sorted(keep_local.decompose(), key=lambda m: tuple(
        np.round(np.array(m.bounding_box()).reshape(2, 3).mean(0), 1)))
    for name, sides in (("handed port", ("port",)), ("handed stbd", ("stbd",)),
                        ("shared", ("port", "stbd"))):
        rel = Manifold.batch_boolean([rel_local[s] for s in sides], OpType.Add)
        killed = [i for i, b in enumerate(bolts) if (b ^ rel).volume() > 0.05]
        kept_levers = []
        for i, b in enumerate(bolts):
            c = np.array(b.bounding_box()).reshape(2, 3).mean(0)
            upper = c[2] > 30.0                      # leg-local Z: top bolts sit high
            if i in killed:
                continue
            kept_levers.append(BOLT_ZB[1] - BOLT_ZB[0] if upper else 0.0)
        # relocate each killed upper bolt down its side flange until the
        # keep-out clears the relief, and record its new lever
        reloc = []
        for i in killed:
            b = bolts[i]
            for dz in np.arange(1.0, 50.0, 0.5):
                if ((b.translate([0, 0, -dz])) ^ rel).volume() <= 0.05:
                    zb_new = BOLT_ZB[1] - dz
                    reloc.append(dict(bolt=i, drop_mm=float(dz), zb_new=float(zb_new),
                                      flange_centre_y=round(aper_half(zb_new) + FLANGE / 2, 1)))
                    kept_levers.append(zb_new - BOLT_ZB[0])
                    break
        removed = (bay_local ^ rel).volume()
        bay_after = bay_local - rel
        levers = [d for d in kept_levers if d > 0]
        grp = bolt_group(levers) if levers else {}
        keep_after = Manifold.batch_boolean(
            [b for i, b in enumerate(bolts) if i not in killed] +
            [bolts[r["bolt"]].translate([0, 0, -r["drop_mm"]]) for r in reloc], OpType.Add)
        LOCAL[name] = dict(bay=bay_after, keep=keep_after)
        res[name] = dict(bolts_killed=killed, relocated=reloc,
                         bay_removed_mm3=round(removed, 0),
                         bay_bodies_after=len(bay_after.decompose()),
                         bolt_group=grp, part_numbers=1 if name == "shared" else 2)
        if out:
            cbc.tri(bay_after).export(os.path.join(out, f"C_bay_{name.replace(' ', '_')}.stl"))
            cbc.tri(bay_local ^ rel).export(
                os.path.join(out, f"C_removed_{name.replace(' ', '_')}.stl"))
    res["baseline"] = dict(bolt_group=bolt_group([BOLT_ZB[1] - BOLT_ZB[0]] * 2))
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--export", help="write option solids here (for the renders)")
    ap.add_argument("--json", help="write the study as JSON")
    ap.add_argument("--b1", action="append", default=[],
                    help="DELTA=census.json from a rotated-cluster census run")
    ap.add_argument("--only", choices=("A", "B", "C"), action="append")
    a = ap.parse_args()
    if a.export:
        os.makedirs(a.export, exist_ok=True)
    P = cbc.build()
    corners = lgbf.parse_corners(lgbf.SCAD)
    only = set(a.only or ("A", "B", "C"))
    S = {}
    if only & {"A", "B", "C"}:
        S["C"] = option_c(P, corners, a.export)
    if "A" in only:
        S["A"] = option_a(P, corners, a.export)
    if "B" in only:
        S["B2"] = option_b2(P, corners, a.export)
        if a.b1:
            S["B1"] = b1_summary(dict(kv.split("=", 1) for kv in a.b1))
    print(json.dumps(S, indent=2, default=float))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(S, fh, indent=2, default=float)
    return 0


if __name__ == "__main__":
    sys.exit(main())
