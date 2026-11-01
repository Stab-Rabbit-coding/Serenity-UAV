#!/usr/bin/env python3
"""wing_polar_compare.py -- 2-D polars for the AS-BUILT wing sections vs the true
S1223, with XFOIL (viscous panel, e^N transition) and NeuralFoil cross-checks.

Sections (thickness-only scaling about the unscaled camber line, exactly what
`s1223_section()` in wings_s1223_revo.scad builds; coordinates are PARSED FROM THE
SCAD by tools/wing_airfoil_variants.py, never re-typed):

    S1223        t scale 1.00   (the characterised section)
    root t17.7   t scale 1.46   chord 129 mm
    tip  t26.7   t scale 2.20   chord  93 mm

Operating Re = V c / nu, nu = 1.461e-5 m^2/s (ISA sea level).  The SCAD header
gives 1.3-1.8e5 for the wing; at 40 kt (20.58 m/s) root 1.82e5, tip 1.31e5.

Transition cases: N_crit 9 (clean), 5 (contaminated / rough-ish), and a FORCED
TRIP at 5 % chord both surfaces (fully rough surface proxy).  N_crit and a trip
are proxies for roughness, not a roughness model.

Needs: XFOIL 6.99 on PATH (xvfb-run -a xfoil works headless), numpy,
aerosandbox + neuralfoil.

Run:  python3 tools/wing_polar_compare.py [--out DIR]

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic) under the author's direction,
2026-10-31, per `AGENTS.md` §3 AI attribution.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""

import argparse
import csv
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from wing_airfoil_variants import variant, write_dat  # noqa: E402
from wing_spar_station_fit import WING_SCAD, scad_points, scad_scalar  # noqa: E402

NU = 1.461e-5
V40KT = 40 * 0.514444


def sections():
    src = open(WING_SCAD).read()
    up, lo = scad_points(src, "S1223_UPPER"), scad_points(src, "S1223_LOWER")
    t_root = scad_scalar(src, "THICKNESS_SCALE")
    t_tip = scad_scalar(src, "THICKNESS_SCALE_TIP")
    c_root, c_tip = scad_scalar(src, "WING_CHORD_ROOT"), scad_scalar(src, "WING_CHORD_TIP")
    out = {}
    for name, sc, chord in (("S1223", 1.0, c_root),
                            (f"root_t{sc_pct(1.0, up, lo, t_root)}", t_root, c_root),
                            (f"tip_t{sc_pct(1.0, up, lo, t_tip)}", t_tip, c_tip)):
        x, yu, yl = variant(up, lo, sc, "thickness")
        out[name] = dict(x=x, yu=yu, yl=yl, scale=sc, chord=chord,
                         tc=float((yu - yl).max()))
    return out


def sc_pct(_unused, up, lo, scale):
    x, yu, yl = variant(up, lo, scale, "thickness")
    return f"{100 * (yu - yl).max():.1f}"


def xfoil_polar(dat, re, ncrit=9.0, trip=None, a0=-4.0, a1=22.0, da=0.25):
    """Run XFOIL; returns array rows alpha, CL, CD, CM, xtr_top, xtr_bot."""
    with tempfile.TemporaryDirectory() as td:
        import shutil
        short = os.path.join(td, "a.dat")  # XFOIL truncates long paths
        shutil.copy(dat, short)
        dat = short
        pol = os.path.join(td, "p.txt")
        cmds = [f"LOAD {dat}", "PANE", "OPER", f"VISC {re:.0f}", "MACH 0",
                "VPAR", f"N {ncrit}"]
        if trip is not None:
            cmds += [f"XTR {trip} {trip}"]
        cmds += ["", "ITER 800", "PACC", pol, "", "ALFA 0", f"ASEQ 0 {a1} {da}",
                 "INIT", "ALFA 0", f"ASEQ 0 {a0} {da}", "INIT", f"ALFA {a1 - 6}", f"ASEQ {a1 - 6} "
                                                                                  f"0 {-da}",
                 "PACC", "", "QUIT"]
        try:
            subprocess.run(["xvfb-run", "-a", "xfoil"], input="\n".join(cmds) + "\n", text=True,
                           # XFOIL drops *.bl dumps in cwd
                           capture_output=True, timeout=240, cwd=td)
        except subprocess.TimeoutExpired:
            pass
        rows = []
        if os.path.exists(pol):
            for ln in open(pol).read().splitlines()[12:]:
                p = ln.split()
                if len(p) >= 7:
                    try:
                        rows.append([float(v) for v in p[:7]])
                    except ValueError:
                        pass
    if not rows:
        return np.zeros((0, 7))
    a = np.array(rows)
    return a[np.argsort(a[:, 0])]


def neuralfoil_polar(sec, re, ncrit=9.0, a0=-4.0, a1=22.0, da=0.5):
    import aerosandbox as asb
    x, yu, yl = sec["x"], sec["yu"], sec["yl"]
    up = np.column_stack([x[::-1], yu[::-1]])
    lw = np.column_stack([x[1:], yl[1:]])
    af = asb.Airfoil(name="s", coordinates=np.vstack([up, lw]))
    al = np.arange(a0, a1 + 1e-9, da)
    r = af.get_aero_from_neuralfoil(alpha=al, Re=re, mach=0.0, n_crit=ncrit, model_size="xlarge")
    return np.column_stack([al, r["CL"], r["CD"], r["CM"], r["analysis_confidence"]])


CL_REQ = 1.54  # 7.6 N cruise lift at 40 kt on 0.019025 m^2 (SCAD header), q = 259 Pa


def summarize(p):
    nanrow = dict(clmax=np.nan, a_clmax=np.nan, ldmax=np.nan, a_req=np.nan, cd_req=np.nan,
                  cl_a0=np.nan, conf=np.nan)
    if len(p) == 0:
        return nanrow
    a, cl, cd = p[:, 0], p[:, 1], p[:, 2]
    i = int(np.argmax(cl))
    pa, pcl, pcd = a[: i + 1], cl[: i + 1], cd[: i + 1]  # pre-stall branch only
    ld = pcl / np.maximum(pcd, 1e-6)
    out = dict(clmax=float(cl[i]), a_clmax=float(a[i]), ldmax=float(ld.max()),
               cl_a0=float(np.interp(0.0, a, cl)), conf=np.nan, a_req=np.nan, cd_req=np.nan)
    if cl[i] >= CL_REQ:
        j = int(np.argmax(pcl >= CL_REQ))
        out["a_req"] = float(np.interp(CL_REQ, pcl[max(j - 1, 0): j + 1],
                             pa[max(j - 1, 0): j + 1])) if j else float(pa[0])
        out["cd_req"] = float(np.interp(CL_REQ, pcl[max(j - 1, 0): j + 1],
                              pcd[max(j - 1, 0): j + 1])) if j else float(pcd[0])
    if (p.shape[1] >= 5 and p[:, 4].max() <= 1.0 and p[:, 4].min() >= 0.0
            and np.allclose(p[:, 4], np.round(p[:, 4], 6))):
        out["conf"] = float(np.mean(p[: i + 1, 4])) if p.shape[1] == 5 else np.nan
    return out


def span_sweep(out):
    """NeuralFoil section data at eta = 0..1 (linear taper of chord and thickness scale),
    plus a strip-theory lift ratio vs a wing built from true S1223 at the same chords.
    Strip theory ignores 3-D flow (low aspect ratio), so use it as a RATIO only."""
    from wing_spar_station_fit import scad_points as sp
    src = open(WING_SCAD).read()
    up, lo = sp(src, "S1223_UPPER"), sp(src, "S1223_LOWER")
    tr, tt = scad_scalar(src, "THICKNESS_SCALE"), scad_scalar(src, "THICKNESS_SCALE_TIP")
    cr, ct = scad_scalar(src, "WING_CHORD_ROOT"), scad_scalar(src, "WING_CHORD_TIP")
    etas = np.linspace(0, 1, 9)
    rows = []
    res = {}
    for nc in (9.0, 5.0):
        for alpha in (4.0, 6.0):
            num = den = 0.0
            for eta in etas:
                c = cr + (ct - cr) * eta
                t = tr + (tt - tr) * eta
                re = V40KT * c / 1000 / NU
                for lab, sc in (("built", t), ("S1223", 1.0)):
                    x, yu, yl = variant(up, lo, sc, "thickness")
                    sec = dict(x=x, yu=yu, yl=yl)
                    pp = neuralfoil_polar(sec, re, nc, a0=alpha, a1=alpha, da=1.0)
                    cl = float(pp[0, 1])
                    w = c * 1.0 if eta not in (0, 1) else c * 0.5
                    if lab == "built":
                        num += w * cl
                    else:
                        den += w * cl
                    if alpha == 4.0:
                        sm = summarize(neuralfoil_polar(sec, re, nc))
                        rows.append([nc, round(eta, 3), round(c, 1),
                                     round(100 * (yu - yl).max(), 1), lab,
                                     round(re), sm["clmax"], sm["cl_a0"], cl, sm["ldmax"]])
            res[(nc, alpha)] = num / den
    with open(os.path.join(out, "span_sweep.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["ncrit", "eta", "chord_mm", "tc_pct", "section",
                   "Re", "CLmax", "CL_a0", "CL_a4", "LDmax"])
        w.writerows(rows)
    print("\nspan sweep (NeuralFoil), built vs true-S1223 sections, same chords")
    print(f"{'ncrit':>5s} {'eta':>5s} {'c mm':>6s} {'t/c%':>5s} {'sect':>6s} {'Re':>7s} "
          f"{'CLmax':>6s} {'CL@0':>6s} {'CL@4':>6s} {'L/Dmax':>7s}")
    for r in rows:
        print(f"{r[0]:5.0f} {r[1]:5.2f} {r[2]:6.1f} {r[3]:5.1f} {r[4]:>6s} {r[5]:7d} {r[6]:6.2f} "
              f"{r[7]:6.2f} {r[8]:6.2f} {r[9]:7.1f}")
    for (nc, al), v in res.items():
        print(
            f"strip-theory 2-D lift of built wing / true-S1223 wing: ncrit {nc:.0f}, alpha "
            f"{al:.0f} deg: {v:.2f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--span", action="store_true", help="only run the NeuralFoil span sweep")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "docs", "sls-study", "wing-polars"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    if args.span:
        span_sweep(args.out)
        return
    secs = sections()
    print(f"V = 40 kt = {V40KT:.2f} m/s, nu = {NU:.3e}")
    cases = [("clean N9", 9.0, None), ("N5", 5.0, None), ("trip 5%c", 9.0, 0.05)]
    hdr = (f"{'section':14s} {'Re':>8s} {'case':10s} {'tool':6s} {'CLmax':>6s} {'a@max':>6s} "
           f"{'(L/D)max':>9s} "
           f"{'a@1.54':>7s} {'CD@1.54':>8s} {'CL@0':>6s} {'conf':>5s}")
    print(hdr)
    rows_out = []
    for name, s in secs.items():
        dat = os.path.join(args.out, f"{name}.dat")
        write_dat(dat, s["x"], s["yu"], s["yl"], name)
        re0 = V40KT * s["chord"] / 1000 / NU
        for re in (round(re0, -3), 1.0e5):
            for cname, nc, trip in cases:
                for tool in ("xfoil", "nf"):
                    if tool == "xfoil":
                        p = xfoil_polar(dat, re, nc, trip)
                    else:
                        if trip is not None:
                            continue
                        p = neuralfoil_polar(s, re, nc)
                    sm = summarize(p)
                    print(f"{name:14s} {re:8.0f} {cname:10s} {tool:6s} {sm['clmax']:6.2f} "
                          f"{sm['a_clmax']:6.1f} "
                          f"{sm['ldmax']:9.1f} {sm['a_req']:7.1f} {sm['cd_req']:8.4f} "
                          f"{sm['cl_a0']:6.2f} {sm['conf']:5.2f}")
                    rows_out.append([name, re, cname, tool, sm["clmax"], sm["a_clmax"], sm["ldmax"],
                                     sm["a_req"], sm["cd_req"], sm["cl_a0"], sm["conf"]])
                    if len(p):
                        csv_name = f"{name}_Re{re:.0f}_{cname.replace(' ', '')}_{tool}.csv"
                        np.savetxt(os.path.join(args.out, csv_name),
                                   p, delimiter=",", fmt="%.5f",
                                   header="alpha,CL,CD,CM,x1,x2,x3 (xfoil) | "
                                          "alpha,CL,CD,CM,confidence (nf)")
    with open(os.path.join(args.out, "summary.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["section", "Re", "case", "tool", "CLmax", "alpha_at_CLmax", "LDmax",
                   "alpha_at_CLreq", "CD_at_CLreq", "CL_at_0", "nf_confidence"])
        w.writerows(rows_out)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
