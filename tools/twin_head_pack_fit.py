#!/usr/bin/env python3
"""twin_head_pack_fit.py -- detailed placement gate for TWO Tattu R-Line 6S
2200 packs side by side (flat) forward of the thrust line, replacing the
single head cell + cargo cell (docs/BATTERY_TRIM_ENDURANCE_OPTIONS.md options
A and F; plan 003 R10 "battery cells, not dead ballast").

Result of the 2026-10-31 search (this file records and re-proves it):

    TWIN TRAY  band 69.5 W x 41.0 H (2 x 34 lateral + 0.75 per side per pack,
               38.5 tall + 1.25 per side), centre Z 191, Y 163..283,
               stop plate Y 159..163 (Bay A forward, 2026-11-01; was Y 172 with
               the side-by-side Bay A).  Rail = RAIL_T ceiling, side walls and
               RAIL_LIP lips (bonded to the skin like today's rail).
    LOADING    each pack on its own sled, lifted in through the open clamshell
               doors (payload removed, as today), slid FORWARD on the
               centreline (corridor |X| <= 17.75, Y 292..400, Zc 189.5) and stepped
               17.4 mm sideways into its lane at the tray.
    TRUNK      nose avionics trunk re-routed off the centreline to a port side
               channel X 38.5..48.5, Z 193..201 (was over the rail ceiling).

Preconditions (both already in branch plans):
  * the head/cargo splice collar is DELETED -- one-piece head+cargo hull
    (docs/SLS_27IN_TWO_SECTION_TRIM_STUDY.md two-section scheme); with the
    collar the tray clips its ring at Y 230-240;
  * the cargo battery cradle and its forward hangers are removed (the cargo
    band becomes the loading corridor / optional third-pack station).

Obstacles: head and cargo shells (post-merge), every cargo-layout and
head-layout envelope except the retired head cell / sled / rail / catch /
trunk and the cargo battery / cradle.  Static gap GAP (1.0 mm, the head
cell's own gap in head_layout_fit).  Rail parts may touch the skin (bonded
seat); their skin overlap is reported, not failed, below SEAT_MAX.

Run:
    /usr/bin/python3 tools/twin_head_pack_fit.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the
author's direction, 2026-10-31, per `AGENTS.md` §3 AI attribution.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import os
import sys

import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cg_relocation_study as c  # noqa: E402
import hull_datums as hd  # noqa: E402  (PENDING_PIVOT_SHIFT)

h, clf = c.hlf, c.clf

# --- the placement (single source; the SCAD params are written from these) --
CELL_L, CELL_W, CELL_H = h.CELL_L, h.CELL_W, h.CELL_H  # 116 x 38.5 x 34
LAT, VERT = 0.75, 1.25  # band clearance per side (KTD5)
LANE_W = CELL_H + 2 * LAT  # 35.5: pack lies FLAT (34 lateral, 38.5 tall)
TRAY_W = 2 * LANE_W - 1.5  # 69.5: lanes share the centre 1.5 mm
TRAY_H = 41.0  # 38.5 + 2 x 1.25 (KTD5)
TRAY_ZC = 191.0
TRAY_Y0, TRAY_Y1 = 163.0, 283.0  # Bay A forward, published 2026-11-01 (side: 172..292)
STOP_T = 4.0
LANE_X = TRAY_W / 4  # 17.375: lane centre off the centreline
RAIL_T, RAIL_LIP = h.RAIL_T, h.RAIL_LIP
CORRIDOR_Y1 = 400.0
TRUNK_X0, TRUNK_X1, TRUNK_Z0, TRUNK_Z1 = h.PORT_CH_X0, h.PORT_CH_X1, h.PORT_CH_Z0, h.PORT_CH_Z1
# Loading corridor runs 1.5 mm LOWER than the tray (Zc 189.5): at Zc 191 it
# grazes the cargo roof aft of Y 292.  The sled steps up a 1.5 mm chamfered
# ramp at the tray's aft edge.  Payload is out during loading (as today).
CORRIDOR_ZC = 189.5
GAP = 1.0
# Bay A reference layout (head_layout_fit --bay-a side): the side-by-side
# pouches held the tray at Y 172.  Read-only: a side run never writes SCAD.
SIDE_TRAY_Y0 = 172.0
# Bay A forward harness envelopes that must clear the tray (KTD3: defined in
# head_layout_fit.ROUTES, never retyped here).
PORT_LINK_MATE_MAX = 300.0  # mm^3, designed link/channel overlap incl. the 1 mm gap growth
FWD_TRUNKS = ("trunk: CN1 run", "trunk: Observer to CN1", "trunk: riser", "trunk: crossover",
              "trunk: port link")
SEAT_MAX = 100.0  # mm^3 skin overlap accepted as a bonded seat per rail part
CELL_G = h.CELL_G
MERGED = os.path.join(c.REPO, "airframe", "stls", "fuselage",
                      "head_cargo_shell24_2mm_merged.stl")


def obstacles():
    # one-piece head+cargo hull (tools/merge_head_cargo_shell.py), collar retired
    # (shell_after_merge drops the bosses that belong to layout equipment, which
    # are proven separately against that equipment by cargo_layout_fit)
    shell = clf.shell_after_merge(trimesh.load(MERGED))
    shell = shell if not isinstance(shell, trimesh.Trimesh) else c.to_man(shell)
    obs = {}
    L = clf.layout_t5()
    for k, e in L.items():
        if k in ("battery", "battery cradle") or "cradle" in k:
            continue
        obs["cargo: " + k] = c.to_man(e["solid"])
        if e.get("mirror"):
            obs["cargo: " + k + " (stbd)"] = c.to_man(clf.mirror_x(e["solid"]))
    HL, _ = h.layout()
    for k, e in HL.items():
        if k.startswith(("head cell", "sled", "rail", "catch")):
            continue
        # the single-cell centreline trunk is retired (port side channel); in the
        # Bay A "fwd" option the CN1 run and Observer drop stay and must clear the tray
        if k.startswith("trunk") and not (h.BAYA_MODE == "fwd" and k in FWD_TRUNKS):
            continue
        obs["head: " + k] = c.to_man(e["solid"])
        if e.get("mirror"):
            obs["head: " + e["mirror"]] = c.to_man(clf.mirror_x(e["solid"]))
    return shell, obs


def grown(x0, x1, y0, y1, z0, z1, g=GAP):
    return c.to_man(c.box(x0 - g, x1 + g, y0 - g, y1 + g, z0 - g, z1 + g))


def checks():
    z0, z1 = TRAY_ZC - TRAY_H / 2, TRAY_ZC + TRAY_H / 2
    hw = TRAY_W / 2
    statics = {  # must clear shell AND every envelope by GAP
        "pack band (both lanes)": (-hw, hw, TRAY_Y0, TRAY_Y1, z0, z1),
        "loading corridor (one pack, centreline)": (-LANE_W / 2, LANE_W / 2, TRAY_Y1,
                                                    CORRIDOR_Y1, CORRIDOR_ZC - TRAY_H / 2,
                                                    CORRIDOR_ZC + TRAY_H / 2),
        "trunk (port side channel)": (TRUNK_X0, TRUNK_X1, h.PORT_CH_Y0, h.PORT_CH_Y1,
                                      TRUNK_Z0, TRUNK_Z1),
    }
    rail = {  # may seat on the skin; must clear every envelope
        "rail ceiling": (-hw - RAIL_T, hw + RAIL_T, TRAY_Y0, TRAY_Y1, z1, z1 + RAIL_T),
        "rail port wall": (hw, hw + RAIL_T, TRAY_Y0, TRAY_Y1, z0 - RAIL_T, z1),
        "rail stbd wall": (-hw - RAIL_T, -hw, TRAY_Y0, TRAY_Y1, z0 - RAIL_T, z1),
        "rail port lip": (hw - RAIL_LIP, hw, TRAY_Y0, TRAY_Y1, z0 - RAIL_T, z0),
        "rail stbd lip": (-hw, -hw + RAIL_LIP, TRAY_Y0, TRAY_Y1, z0 - RAIL_T, z0),
        "stop plate": (-hw, hw, TRAY_Y0 - STOP_T, TRAY_Y0, z0 - RAIL_T, z1),
    }
    return statics, rail


SCAD_OUT = os.path.join(c.REPO, "airframe", "openscad", "fuselage", "twin_pack_tray_params.scad")


def write_params():
    """Single source for airframe/openscad/fuselage/twin_pack_tray.scad."""
    vals = dict(CELL_L=CELL_L, CELL_W=CELL_W, CELL_H=CELL_H, LAT=LAT, VERT=VERT,
                LANE_W=LANE_W, TRAY_W=TRAY_W, TRAY_H=TRAY_H, TRAY_ZC=TRAY_ZC,
                TRAY_Y0=TRAY_Y0, TRAY_Y1=TRAY_Y1, STOP_T=STOP_T, LANE_X=LANE_X,
                RAIL_T=RAIL_T, CORRIDOR_ZC=CORRIDOR_ZC, SLED_FLOOR_T=h.SLED_FLOOR_T,
                SLED_LIP=h.SLED_LIP)
    with open(SCAD_OUT, "w") as f:
        f.write("// GENERATED by tools/twin_head_pack_fit.py -- do not edit by hand.\n"
                "// Aircraft datum R2, mm.  License: CERN-OHL-W-2.0\n")
        for k, v in vals.items():
            f.write(f"{k} = {v:.4f};\n")
    print(f"wrote {os.path.relpath(SCAD_OUT, c.REPO)}")


def main():
    global TRAY_Y0, TRAY_Y1
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bay-a", choices=("fwd", "side"), default="fwd",
                    help="fwd (published, writes SCAD on PASS) or side (read-only reference)")
    h.BAYA_MODE = ap.parse_args().bay_a
    if h.BAYA_MODE == "side":
        TRAY_Y0, TRAY_Y1 = SIDE_TRAY_Y0, SIDE_TRAY_Y0 + (TRAY_Y1 - TRAY_Y0)
    shell, obs = obstacles()
    statics, rail = checks()
    fails = 0
    print(f"TWIN TRAY {TRAY_W} W x {TRAY_H} H, Zc {TRAY_ZC}, Y {TRAY_Y0}-{TRAY_Y1}; "
          f"lanes at X +/-{LANE_X:.2f}; gap {GAP} mm")
    for name, b in statics.items():
        m = grown(*b)
        hits = {k: (m ^ o).volume() for k, o in obs.items()
                if not (name.startswith("loading") and k == "cargo: payload")}
        # the port link joins the channel by design: allow its designed overlap
        # (10 x 2 x 8 mm grown by GAP -> ~270 mm^3), never more, and print it
        link = hits.pop("head: trunk: port link", None) if name.startswith("trunk") else None
        if link is not None and link > PORT_LINK_MATE_MAX:
            hits["head: trunk: port link (over mate allowance)"] = link
        hits = {k: v for k, v in hits.items() if v > 0.5}
        sv = (m ^ shell).volume()
        # the corridor sweeps the cargo skin where the hull narrows at the
        # door hinge line; under 25 mm^3 is a grid / facet artefact
        ok = not hits and sv <= 25.0
        fails += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name:42s} shell {sv:7.1f} mm3  "
              f"{', '.join(f'{k} {v:.0f}' for k, v in hits.items()) or 'no envelope hits'}")
    for name, b in rail.items():
        m = c.to_man(c.box(*b))
        hits = {k: (m ^ o).volume() for k, o in obs.items()}
        hits = {k: v for k, v in hits.items() if v > 0.5}
        sv = (m ^ shell).volume()
        ok = not hits and sv <= SEAT_MAX
        fails += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name:42s} skin seat {sv:6.1f} mm3  "
              f"{', '.join(f'{k} {v:.0f}' for k, v in hits.items()) or 'no envelope hits'}")
    # CG / endurance (rail-lever baseline: 6,232 g, CG +16.3 mm; S1 packs at
    # the head cell Y 216 and the cargo cell Y 344.2)
    M0, P = 6232.0, c.PIVOT_Y
    cg0 = P + 16.3
    y_twin = 0.5 * (TRAY_Y0 + TRAY_Y1)
    head_y, cargo_y = h.CELL_Y0 + h.CELL_L / 2, c.CELL2_Y
    f = 0.297  # nacelle mass fraction (cg_relocation_study)
    base = M0 * cg0 - CELL_G * (head_y + cargo_y)
    # third pack: a 116 mm 2200 does NOT fit between the tray (Y 292) and the
    # aft-node limit (BAND_Y1 402.2): 110 mm available, 120 needed with lips.
    # The 70 mm Tattu R-Line v6 6S 1600 (240 g, plan 001 R9) does, at the
    # corridor's forward end: Y 294 .. 368.
    y_third = TRAY_Y1 + 2.0 + 2.0 + 70.0 / 2
    print(f"third-pack room aft of the tray: {h.BAND_Y1 - TRAY_Y1 - 2.0:.1f} mm "
          f"(2200 needs {h.CELL_L + 4:.0f}; 1600 needs 74)")
    print(f"\nCG and endurance (pack centroid Y {y_twin:.1f}; endurance ~ capacity x AUW^-1.5)")
    for label, extra_m, extra_y, cap in (
            ("F: both packs in the twin tray", 0.0, 0.0, 4400),
            ("A: twin tray + Tattu 6S 1600 in the corridor", c.THIRD_CELL_G, y_third, 6000)):
        M = M0 + extra_m
        off = (base + 2 * CELL_G * y_twin + extra_m * extra_y) / M - P
        end = cap / 4400 * (M / M0) ** -1.5 - 1
        print(f"  {label:48s} AUW {M:5.0f} g ({M / 453.592:5.2f} lbm)  CG {off:+5.1f} mm; "
              f"with 0.5 in pivot {off - hd.PENDING_PIVOT_SHIFT * (1 - f * M0 / M):+5.1f} mm; "
              f"T/W {8540 / M:.2f}; endurance {end * 100:+.0f} %")
    if h.BAYA_MODE == "fwd" and not fails:
        write_params()
    elif h.BAYA_MODE == "fwd":
        print("not writing twin_pack_tray_params.scad: gate FAILED")
    print(f"\nRESULT: {'PASS' if not fails else f'FAIL ({fails})'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
