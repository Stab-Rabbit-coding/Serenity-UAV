#!/usr/bin/env python3
"""cg_relocation_study.py -- move equipment forward until the hover CG sits on
the hover thrust line (nacelle tilt pivot, aircraft datum R2 Y 326.7), with
every placement proved against the published shells and the layout envelopes
(no bounding-box placement, `airframe/AGENTS.md`).

Owner direction 2026-10-27: CG target = hover thrust line; relocations before a
pivot move or ballast; then "finer relocation search" (lateral, mirrored,
rotated and split placements; Y step <= 3 mm, Z step <= 4 mm).

Method
------
1. Mass items come from tools/auw_ledger.py (same roll-up as the ledger).
2. Arrangement = the RAIL LEVER: Bay A (CN1 + FC1) on edge on the rail ceiling
   (Y 100-158), rail stop Y 156, head cell Y 158-274, second cell in the cargo
   band Y 286.2-402.2.  Head geometry (nose sensor bay, pitched Observer board,
   pitot hose) is taken from tools/head_layout_fit.py.
3. FREE-SPACE MAP.  The fixed obstacles (all shells and collars, every layout
   envelope except the candidates being moved) are SLICED by manifold3d at
   each Z level; the hull interior at that level is, per Y row, the span
   between the first and last wall crossing along X (the cargo and middle
   walls slice as separate port/starboard rings because the mating faces are
   open); free = interior minus obstacles.  The map is
   rasterised at GRID_XY x GRID_XY x GRID_Z and queried through a 3-D
   summed-area table, so every box placement (dilated by STATIC_GAP) is an
   O(1) test.  Search: all six axis orders (90 deg rotations), X across the
   section, Y step GRID_XY (1.5 mm), Z step GRID_Z (4 mm).
4. Greedy relocation: candidates are placed in order of aft moment; pairs are
   SPLIT into single nodes (so lateral, mirrored and split placements are all
   covered); each placed item is written back into the map.
5. CG for hover, heaviest payload and third cell, the spread against the
   MIL-F-83300 §3.4.4 50 % control-reserve framing, and the residual moment.

Run:
    /usr/bin/python3 tools/cg_relocation_study.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the
author's direction, 2026-10-27, per `AGENTS.md` §3 AI attribution.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import os
import sys
import time

import numpy as np
import shapely
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import auw_ledger as al  # noqa: E402
import cargo_layout_fit as clf  # noqa: E402
import head_layout_fit as hlf  # noqa: E402
import hull_datums as hd  # noqa: E402
import middle_layout_fit as mlf  # noqa: E402
from cargo_layout_fit import box, to_man  # noqa: E402

PIVOT_Y = hd.SPAR_Y  # 326.7, hover thrust line = nacelle tilt axis
CELL_G = hlf.CELL_G  # 321 g, Tattu R-Line 6S 2200 (ORIGIN flag per plan 001 KTD4)
THIRD_CELL_G = 240.0  # Tattu R-Line v6.0 6S 1600 (plan 001 R9)
STATIC_GAP = 2.0  # static to static (cargo_layout_fit convention)
GRID_XY, GRID_Z = 1.5, 4.0
X_RANGE, Y_RANGE, Z_RANGE = (-72.0, 72.0), (0.0, 700.0), (80.0, 292.0)
FSTL = os.path.join(REPO, "airframe", "stls", "fuselage")

# Rev H2 as handed over (head_layout_fit) -- imported, never retyped
H2_BAYA_Y = hlf.BAYA_Y0 + clf.NODE_L / 2
H2_HEAD_CELL_Y = 0.5 * (hlf.CELL_Y0 + hlf.CELL_Y1)
# Rail lever (probed 2026-10-27): Bay A on edge ON the rail ceiling
LEVER_BAYA_Y0 = 100.0
LEVER_BAYA_Z0 = hlf.BAND_Z1 + hlf.RAIL_T + 1.0  # 208.65
LEVER_STOP_Y = 156.0  # band clear from Y 150 + stop plate + catch leaf allowance
BAYA_Y = LEVER_BAYA_Y0 + clf.NODE_L / 2  # 129
HEAD_CELL_Y0 = LEVER_STOP_Y + hlf.SLED_LIP  # 158
HEAD_CELL_Y = HEAD_CELL_Y0 + hlf.CELL_L / 2  # 216
CELL2_Y1 = hlf.BAND_Y1  # 402.2 (aft nodes bound the band)
CELL2_Y0 = CELL2_Y1 - hlf.CELL_L  # 286.2
CELL2_Y = 0.5 * (CELL2_Y0 + CELL2_Y1)  # 344.2
# Nose Observer is NOT in the ledger: ASSUMED 60 g (the ledger's own cargo
# Observer figure) at the pitched board's centroid.
NOSE_OBS_G = 60.0
NOSE_OBS_Y = float(hlf.observer_board().centroid[1])

NODE1 = (clf.NODE_L + clf.NODE_CABLE, clf.NODE_T, clf.NODE_H)  # one pouch + cable zone
# Candidates: name, ledger predicate, envelope (dx, dy, dz), split count,
# names of the layout envelopes that represent it (removed from the map).
CANDIDATES = [
    ("Flight Engineer (board + can + plate)",
     lambda n: n.startswith("Flight Engineer") or n.startswith("FE can"),
     (mlf.FE_CAN_X, mlf.FE_CAN_Y + mlf.FE_PLATE_Y, mlf.FE_CAN_Z), 1,
     ("Kaylee",)),
    ("Simon CN4+FC4", lambda n: "(node simon)" in n, NODE1, 2,
     ("Simon", "CN4", "FC4")),
    ("aft nodes FC2/FC3", lambda n: "(node aft)" in n, NODE1, 2,
     ("node N2", "node N4")),
    ("cargo Observer node", lambda n: n.startswith("Cargo Observer"),
     (clf.OBSERVER_L, clf.OBSERVER_T, clf.OBSERVER_W), 1, ("Observer",)),
]
NOTES = {
    "Flight Engineer (board + can + plate)": "power hub; needs ventral service access",
    "Simon CN4+FC4": "bus-end termination; SMA whips on the middle crown",
    "aft nodes FC2/FC3": "flight-control pair",
    "cargo Observer node": "hoist monitor: must see the clamshell aperture Y 307.7-413.7",
}


def items():
    bom = al.bom_rows()
    base = al.printed_items() + al.nacelle_items() + al.station_items(bom) + al.gap_items()
    payload = al.Item("payload", "PAYLOAD", al.PAYLOAD_G, al.PAYLOAD_ST[0], None, "", "PAYLOAD")
    return base, payload


def cg_y(entries):
    m = sum(e[0] for e in entries)
    return m, sum(e[0] * e[1] for e in entries) / m


# ---------------------------------------------------------------------------
# obstacle assembly
# ---------------------------------------------------------------------------
def shells():
    m = to_man(trimesh.load(hlf.HEAD)) + to_man(trimesh.load(hlf.COLLAR))
    cs = clf.shell_after_merge(trimesh.load(clf.SHELL))
    m = m + (to_man(cs) if isinstance(cs, trimesh.Trimesh) else cs)
    for f in ("cargo_middle_splice_collar.stl", "middle_shell24_2mm_repaired.stl",
              "middle_rear_splice_collar.stl", "rear_shell24_2mm_repaired.stl"):
        m = m + to_man(trimesh.load(os.path.join(FSTL, f)))
    return m


def envelopes(skip):
    """Every placed envelope except the candidates (`skip` substrings)."""
    m = None

    def add(tm):
        nonlocal m
        mm = to_man(tm)
        m = mm if m is None else m + mm

    L = clf.layout_t5()
    for k, e in list(L.items()):
        if e.get("mirror"):
            L[k + " (stbd)"] = dict(e, solid=clf.mirror_x(e["solid"]))
    for k, e in L.items():
        if k in ("battery", "battery cradle") or any(s in k for s in skip):
            continue
        add(e["solid"])
    for k, e in mlf.layout_t6().items():
        if e.get("section", "middle") != "middle" or k.startswith("hatch"):
            continue
        if any(s in k for s in skip):
            continue
        add(e["solid"])
    HL, _parts = hlf.layout()
    for k, e in HL.items():  # nose bay, Observer board, pitot hose, sensors kept
        if k.startswith(("Bay A", "head cell", "sled", "rail", "stop", "catch", "trunk")):
            continue
        add(e["solid"])
        if e.get("mirror"):
            add(clf.mirror_x(e["solid"]))
    # rail lever: Bay A on the rail ceiling + the rail/band from the stop aft
    for sx in (1, -1):
        x0, x1 = sorted((sx * 1.0, sx * (1.0 + clf.NODE_T)))
        add(box(x0, x1, LEVER_BAYA_Y0, LEVER_BAYA_Y0 + clf.NODE_L + clf.NODE_CABLE,
                LEVER_BAYA_Z0, LEVER_BAYA_Z0 + clf.NODE_H))
    add(box(-hlf.BAND_W / 2 - hlf.RAIL_T, hlf.BAND_W / 2 + hlf.RAIL_T, LEVER_STOP_Y - 10.0,
            CELL2_Y1 + 2.0, hlf.BAND_Z0 - hlf.RAIL_T, hlf.BAND_Z1 + hlf.RAIL_T))
    return m


def home_boxes(skip):
    """Bounding boxes of a candidate's own envelopes at its ledger station
    (re-occupied in the map when it finds no forward placement)."""
    out = []
    L = clf.layout_t5()
    for k, e in list(L.items()):
        if e.get("mirror"):
            L[k + " (stbd)"] = dict(e, solid=clf.mirror_x(e["solid"]))
    ML = {k: e for k, e in mlf.layout_t6().items()
          if e.get("section", "middle") == "middle" and not k.startswith("hatch")}
    for k, e in list(L.items()) + list(ML.items()):
        if any(s in k for s in skip):
            b = e["solid"].bounds
            out.append((b[0][0], b[1][0], b[0][1], b[1][1], b[0][2], b[1][2]))
    return out


# ---------------------------------------------------------------------------
# free-space map
# ---------------------------------------------------------------------------
def _mask(contours, X, Y, inside_outer=False):
    """Even-odd occupancy of a cross-section's contours on the grid points;
    with inside_outer, the union of the CCW (outer) contour interiors."""
    occ = np.zeros(X.shape, bool)
    for c in contours:
        if len(c) < 3:
            continue
        a = 0.5 * np.sum(c[:, 0] * np.roll(c[:, 1], -1) - np.roll(c[:, 0], -1) * c[:, 1])
        if inside_outer and a <= 0:
            continue
        inside = shapely.contains_xy(shapely.Polygon(c), X, Y)
        occ = (occ | inside) if inside_outer else (occ ^ inside)
    return occ


def free_map(shell_m, env_m):
    xs = np.arange(X_RANGE[0], X_RANGE[1], GRID_XY) + GRID_XY / 2
    ys = np.arange(Y_RANGE[0], Y_RANGE[1], GRID_XY) + GRID_XY / 2
    zs = np.arange(Z_RANGE[0], Z_RANGE[1], GRID_Z) + GRID_Z / 2
    X, Y = np.meshgrid(xs, ys, indexing="xy")  # (ny, nx)
    obst = shell_m + env_m
    free = np.zeros((len(zs), len(ys), len(xs)), bool)
    for k, z in enumerate(zs):
        sh = [np.asarray(c) for c in shell_m.slice(float(z)).to_polygons()]
        ob = [np.asarray(c) for c in obst.slice(float(z)).to_polygons()]
        if not sh:
            continue
        wall = _mask(sh, X, Y)
        # interior between the first and last wall crossing along X in each
        # Y row: the cargo/middle walls slice as separate port/stbd rings
        # (open mating faces), so "inside a closed contour" loses the bay
        between = (np.maximum.accumulate(wall, axis=1)
                   & np.maximum.accumulate(wall[:, ::-1], axis=1)[:, ::-1])
        free[k] = between & ~_mask(ob, X, Y)
    return xs, ys, zs, free


class Map:
    def __init__(self, xs, ys, zs, free):
        self.xs, self.ys, self.zs, self.free = xs, ys, zs, free.copy()
        self._sat()

    def _sat(self):
        occ = (~self.free).astype(np.int32)
        s = np.zeros(tuple(n + 1 for n in occ.shape), np.int32)
        s[1:, 1:, 1:] = occ.cumsum(0).cumsum(1).cumsum(2)
        self.sat = s

    def _idx(self, lo, hi, axis):
        g = (self.zs, self.ys, self.xs)[axis]
        step = GRID_Z if axis == 0 else GRID_XY
        i0 = int(np.floor((lo - (g[0] - step / 2)) / step))
        i1 = int(np.ceil((hi - (g[0] - step / 2)) / step))
        return i0, i1

    def window_ok(self, dx, dy, dz):
        """Boolean array [z0, y0, x0] of feasible box corners (cells), box
        dilated by STATIC_GAP."""
        nx = int(np.ceil((dx + 2 * STATIC_GAP) / GRID_XY))
        ny = int(np.ceil((dy + 2 * STATIC_GAP) / GRID_XY))
        nz = int(np.ceil((dz + 2 * STATIC_GAP) / GRID_Z))
        s = self.sat
        if nz >= s.shape[0] or ny >= s.shape[1] or nx >= s.shape[2]:
            return None, (nx, ny, nz)
        tot = (s[nz:, ny:, nx:] - s[:-nz, ny:, nx:] - s[nz:, :-ny, nx:] - s[nz:, ny:, :-nx]
               + s[:-nz, :-ny, nx:] + s[:-nz, ny:, :-nx] + s[nz:, :-ny, :-nx]
               - s[:-nz, :-ny, :-nx])
        return tot == 0, (nx, ny, nz)

    def occupy(self, x0, x1, y0, y1, z0, z1):
        a0, a1 = self._idx(z0, z1, 0)
        b0, b1 = self._idx(y0, y1, 1)
        c0, c1 = self._idx(x0, x1, 2)
        self.free[max(a0, 0):a1, max(b0, 0):b1, max(c0, 0):c1] = False
        self._sat()

    def most_forward(self, dims, y_max):
        best = None
        perms = {(dims[i], dims[j], dims[k]) for i, j, k in
                 ((0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0))}
        for dx, dy, dz in perms:
            ok, (nx, ny, nz) = self.window_ok(dx, dy, dz)
            if ok is None or not ok.any():
                continue
            iz, iy, ix = np.nonzero(ok)
            # cell-corner -> box centre (the gap is inside the window)
            yc = self.ys[0] - GRID_XY / 2 + iy * GRID_XY + ny * GRID_XY / 2
            sel = yc < y_max
            if not sel.any():
                continue
            j = np.argmin(np.where(sel, yc, np.inf))
            xc = self.xs[0] - GRID_XY / 2 + ix[j] * GRID_XY + nx * GRID_XY / 2
            zc = self.zs[0] - GRID_Z / 2 + iz[j] * GRID_Z + nz * GRID_Z / 2
            if best is None or yc[j] < best[1]:
                best = (xc, yc[j], zc, (dx, dy, dz))
        return best


# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    base, payload = items()
    nodeA = [i for i in base if "(node A)" in i.name]
    moved = {i.name for i in nodeA}
    groups = {}
    for name, pred, dims, split, skip in CANDIDATES:
        g = [i for i in base if pred(i.name)]
        m = sum(i.m for i in g)
        groups[name] = dict(m=m, y=sum(i.m * i.cg[1] for i in g) / m, dims=dims,
                            split=split, skip=skip)
        moved |= {i.name for i in g}
    rest = [(i.m, i.cg[1]) for i in base if i.name not in moved]
    mA = sum(i.m for i in nodeA)
    fixed = list(rest) + [(mA, BAYA_Y), (CELL_G, HEAD_CELL_Y), (NOSE_OBS_G, NOSE_OBS_Y)]

    def cgs(pieces, cell2_y=CELL2_Y):
        e = fixed + [(CELL_G, cell2_y)] + pieces
        out = []
        for cfg, extra in (("hover", ()), ("heaviest payload", ((payload.m, payload.cg[1]),)),
                           ("third cell", ((THIRD_CELL_G, payload.cg[1]),))):
            m, y = cg_y(e + list(extra))
            out.append((cfg, m, y, y - PIVOT_Y))
        return out

    def show(label, res):
        print(f"\n{label}")
        for cfg, m, y, d in res:
            print(f"  {cfg:17s} AUW {m:6.0f} g ({m / 453.592:5.2f} lbm)  CG Y {y:6.1f}  "
                  f"offset {d:+6.1f} mm ({d / 25.4:+.2f} in)")

    h2 = fixed[:-3] + [(mA, H2_BAYA_Y), (CELL_G, H2_HEAD_CELL_Y), (NOSE_OBS_G, NOSE_OBS_Y),
                       (CELL_G, 541.7)] + [(g["m"], g["y"]) for g in groups.values()]
    print(f"Rev H2 as handed over: hover offset {cg_y(h2)[1] - PIVOT_Y:+.1f} mm")
    start = [(g["m"], g["y"]) for g in groups.values()]
    show("RAIL LEVER, candidates at their ledger stations", cgs(start))

    # items > 20 g aft of the pivot that are NOT candidates (for the record)
    print("\nother items > 20 g aft of the pivot (not relocatable by function or structure):")
    for i in sorted((i for i in base if i.m > 20 and i.cg[1] > PIVOT_Y and i.name not in moved),
                    key=lambda i: -i.m * (i.cg[1] - PIVOT_Y))[:20]:
        print(f"  {i.name[:48]:48s} {i.m:6.1f} g  Y {i.cg[1]:6.1f}")

    skip = tuple(s for g in groups.values() for s in g["skip"])
    print(f"\nbuilding free-space map ({GRID_XY} x {GRID_XY} x {GRID_Z} mm) ...", flush=True)
    xs, ys, zs, free = free_map(shells(), envelopes(skip))
    fmap = Map(xs, ys, zs, free)
    print(f"  free volume {free.sum() * GRID_XY * GRID_XY * GRID_Z / 1e3:,.0f} cm^3 "
          f"({time.time() - t0:.0f} s)")

    pieces, log = [], []
    order = sorted(groups, key=lambda n: -groups[n]["m"] * (groups[n]["y"] - PIVOT_Y))
    for name in order:
        g = groups[name]
        m1 = g["m"] / g["split"]
        for k in range(g["split"]):
            label = name if g["split"] == 1 else f"{name} #{k + 1}"
            best = fmap.most_forward(g["dims"], g["y"])
            if best is None:
                # stays put: put its own envelopes back into the map
                if k == 0:
                    for bb in home_boxes(g["skip"]):
                        fmap.occupy(*bb)
                pieces.append((m1, g["y"]))
                log.append((label, m1, g["y"], g["y"], None, 0.0))
                continue
            xc, yc, zc, (dx, dy, dz) = best
            fmap.occupy(xc - dx / 2, xc + dx / 2, yc - dy / 2, yc + dy / 2,
                        zc - dz / 2, zc + dz / 2)
            pieces.append((m1, yc))
            log.append((label, m1, g["y"], yc, (xc, zc, (dx, dy, dz)), m1 * (g["y"] - yc)))
    print("\nranked moves (moment gained = mass x forward travel):")
    for label, m, y0, y1, where, gain in sorted(log, key=lambda r: -r[5]):
        if where is None:
            print(f"  {label:42s} {m:6.1f} g  stays at Y {y0:.1f} (no clear forward placement)")
        else:
            xc, zc, d3 = where
            print(f"  {label:42s} {m:6.1f} g  Y {y0:.1f} -> {y1:.1f} at X {xc:+.1f} Z {zc:.1f} "
                  f"box {tuple(round(v, 1) for v in d3)}  gain {gain:,.0f} g.mm  [{NOTES.get(
                      label.split(' #')[0], '')}]")
    res = cgs(pieces)
    show("AFTER FINE RELOCATION", res)
    alt_y = HEAD_CELL_Y0 + hlf.CELL_L + hlf.SLED_LIP + 4.0 + hlf.CELL_L / 2
    show(f"... and cell 2 pulled forward to the head cell's tail (4 mm lead gap, centre Y "
         f"{alt_y:.1f})", cgs(pieces, alt_y))
    hover = res[0]
    spread = max(r[3] for r in res) - min(r[3] for r in res)
    resid = hover[3] * hover[1]
    nac = sum(i.m for i in al.nacelle_items())
    f = nac / hover[1]
    print(f"\nresidual hover moment {resid:,.0f} g.mm; nose ballast at Y 15: "
          f"{resid / (PIVOT_Y - 15.0):.0f} g; pivot move (nacelle fraction f {f:.2f}): "
          f"{hover[3] / (1 - f):.1f} mm aft; config spread {spread:.1f} mm "
          f"({time.time() - t0:.0f} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
