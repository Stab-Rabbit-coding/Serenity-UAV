#!/usr/bin/env python3
"""Generate and compare S1223 thickening strategies for the Rev R1b spar move.

Moving `SPAR_BORE_STATION` aft to 35 % root chord (45.15 mm) puts the bore at
48.5 % of the TIP chord, where S1223 has lost most of its depth.  The tip must
therefore be thickened to keep skin over the bore.  HOW it is thickened is the
aerodynamic question this tool exists to answer.

Two strategies give the SAME depth and therefore the same spar fit:

  uniform    y -> y * s          (what `s1223_section()` does today via
                                  `scale([chord, chord*t_scale])`)
  thickness  camber preserved,
             half-thickness * s  (decompose into camber + thickness, scale
                                  only the thickness, re-assemble)

They are NOT aerodynamically equivalent.  S1223 is a high-lift low-Reynolds
section that earns its Cl_max from strong camber; `uniform` multiplies that
camber by the same factor as the thickness, so a scale chosen purely to fit a
spar silently re-cambers the aerofoil.  `thickness` leaves the camber line
exactly where Selig put it -- the canonical shape -- and only fattens the
section around it.  The SCAD's own comment concedes the point: "Scaling y
uniformly scales both camber and thickness by the same factor, which is a
minor approximation acceptable for t_scale in [0.85,1.0]."  The tip is
already outside that range at 1.25 and would be far outside it at ~1.45.

This tool reports both, and writes coordinate files for the OpenFOAM study in
`tools/wing_cfd_openfoam.py`.

Coordinates are PARSED FROM THE SCAD, never re-typed, so the variants describe
the wing that actually gets built.

Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note : Authored by Claude (model: Claude Opus 5, Anthropic) under the
          author's direction, 2026-08-16, per AGENTS.md AI attribution.
License : CC BY-SA 4.0  <https://creativecommons.org/licenses/by-sa/4.0/>

Run: /usr/bin/python3 tools/wing_airfoil_variants.py [--station MM] [--write DIR]
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402

from wing_spar_station_fit import (  # noqa: E402
    WING_SCAD, MIN_WALL_MM, scad_points, scad_scalar, surf_y,
)


def camber_thickness(upper, lower, xq):
    """(camber, thickness) in t/c at chord fraction xq."""
    yu, yl = surf_y(upper, xq), surf_y(lower, xq)
    return (yu + yl) / 2.0, (yu - yl)


def variant(upper, lower, scale, mode, n=161):
    """Return (x, y_upper, y_lower) in t/c for a thickening strategy.

    Sampled on a cosine distribution so the leading edge -- where curvature is
    highest and a linear sample would cut the nose flat -- is resolved.
    """
    beta = np.linspace(0.0, np.pi, n)
    x = (1.0 - np.cos(beta)) / 2.0
    yu = np.empty(n)
    yl = np.empty(n)
    for i, xq in enumerate(x):
        cam, thk = camber_thickness(upper, lower, float(xq))
        if mode == "uniform":
            # camber AND thickness scale together
            yu[i] = (cam + thk / 2.0) * scale
            yl[i] = (cam - thk / 2.0) * scale
        elif mode == "thickness":
            # camber held; only the thickness envelope opens up
            yu[i] = cam + (thk / 2.0) * scale
            yl[i] = cam - (thk / 2.0) * scale
        else:
            raise ValueError(mode)
    return x, yu, yl


def describe(name, x, yu, yl, chord, station, bore, min_wall):
    """One-line geometric summary plus the spar fit at `station`."""
    thk = yu - yl
    cam = (yu + yl) / 2.0
    i_t = int(np.argmax(thk))
    xq = station / chord
    # interpolate the section at the spar station
    tu = float(np.interp(xq, x, yu)) * chord
    tl = float(np.interp(xq, x, yl)) * chord
    mid = (tu + tl) / 2.0
    wall = min(tu - mid, mid - tl) - bore / 2.0
    ok = "OK " if wall >= min_wall else "THIN"
    return (f"  {name:<22} t/c {thk[i_t]:6.2%} @ {x[i_t]:5.1%}c   "
            f"camber max {cam.max():6.2%}   "
            f"spar wall {wall:+5.2f} mm  {ok}")


def write_dat(path, x, yu, yl, name):
    """Selig-format coordinate file: upper TE->LE, then lower LE->TE."""
    with open(path, "w") as fh:
        fh.write(f"{name}\n")
        for i in range(len(x) - 1, -1, -1):
            fh.write(f"  {x[i]:.6f}  {yu[i]:.6f}\n")
        for i in range(1, len(x)):
            fh.write(f"  {x[i]:.6f}  {yl[i]:.6f}\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--station", type=float, default=45.15,
                    help="spar station, mm aft of LE (default 45.15 = 35%% "
                         "root chord)")
    ap.add_argument("--bore", type=float, default=None,
                    help="spar bore diameter (default SPAR_BORE_OD from SCAD)")
    ap.add_argument("--min-wall", type=float, default=MIN_WALL_MM)
    ap.add_argument("--write", metavar="DIR",
                    help="write .dat coordinate files for the CFD study")
    args = ap.parse_args()

    src = open(WING_SCAD).read()
    upper = scad_points(src, "S1223_UPPER")
    lower = scad_points(src, "S1223_LOWER")
    c_tip = scad_scalar(src, "WING_CHORD_TIP")
    c_root = scad_scalar(src, "WING_CHORD_ROOT")
    ts_tip = scad_scalar(src, "THICKNESS_SCALE_TIP")
    bore = args.bore if args.bore is not None else scad_scalar(src,
                                                               "SPAR_BORE_OD")

    xq = args.station / c_tip
    cam0, thk0 = camber_thickness(upper, lower, xq)
    need_depth = bore + 2.0 * args.min_wall
    need_scale = need_depth / (thk0 * c_tip)

    print("S1223 thickening strategies for the tip section")
    print(f"  tip chord {c_tip:.1f} mm, spar station {args.station:.2f} mm "
          f"= {xq:.1%} tip chord ({args.station / c_root:.1%} root chord)")
    print(f"  bore D{bore}, min wall {args.min_wall:.2f} mm "
          f"-> need {need_depth:.2f} mm of depth")
    print(f"  baseline depth there {thk0 * c_tip:.2f} mm "
          f"-> thickness scale {need_scale:.3f} required (as-built "
          f"{ts_tip:.2f})\n")

    cases = [
        ("baseline S1223", 1.0, "uniform"),
        (f"as-built uniform x{ts_tip:.2f}", ts_tip, "uniform"),
        (f"uniform x{need_scale:.3f}", need_scale, "uniform"),
        (f"thickness-only x{need_scale:.3f}", need_scale, "thickness"),
    ]
    out = []
    for name, sc, mode in cases:
        x, yu, yl = variant(upper, lower, sc, mode)
        print(describe(name, x, yu, yl, c_tip, args.station, bore,
                       args.min_wall))
        out.append((name, mode, sc, x, yu, yl))

    print("\n  Both x{0:.3f} rows give the SAME depth and the SAME spar fit."
          .format(need_scale))
    print("  They differ only in what happens to the camber line, which is "
          "where\n  S1223's lift comes from -- that is what the CFD has to "
          "settle.")

    if args.write:
        os.makedirs(args.write, exist_ok=True)
        for name, mode, sc, x, yu, yl in out:
            slug = (name.replace(" ", "_").replace("x", "s")
                    .replace(".", "p").replace("-", "_"))
            path = os.path.join(args.write, f"{slug}.dat")
            write_dat(path, x, yu, yl, name)
            print(f"  wrote {path}")


if __name__ == "__main__":
    main()
