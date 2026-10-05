#!/usr/bin/python3
"""Stator-tube -> aft-rotor hub transition, 64 mm nacelle (axisymmetric CFD).

Owner direction 2026-10-05: the 11-vane stator forms a tube around the forward
QX QF2822 and must give the air "a continuous smooth path from the stator into
the aft rotor"; the motor still installs from the rear.  The QF2822 can is
Ø27.8 (REF-EDF-003) so the tube is ~Ø31, but the QX rotor hub scales to only
Ø~25 from the QX outline drawing (front view, against its dimensioned Ø77 lip;
±5 % reading) — a ~3 mm radial step that must either be tapered (stage 2 moved
aft into the remaining ~8 mm axial margin) or left as a step at the motor tail.
The owner asked for CFD to decide (prefer the step if the flow is not hurt).

Cases (x = nacelle Z, mm; r = radius, mm; outer duct r 32):
  B       step:   hub r 15.5 to x 103.2, then r 12.5 (rotor hub); rotor at 104.2
  A       taper:  r 15.5 -> 12.5 linearly over x 103.2..111.2; rotor at 112.2
  A_thin  taper from r 15.0 (0.6 mm tube wall) over the same 8 mm

Model: 2-D axisymmetric wedge (2.5 deg), steady incompressible simpleFoam,
k-omega SST, wall functions — the same setup as tools/nacelle_intake_cfd.py
(whose helpers are reused).  Inlet at x 62 (vane trailing edge 60.2 + 1.8),
deswirled axial flow at the design mass flow 0.385 kg/s (tandem 37.6 N,
momentum theory, as tools/nacelle_tilt_dynamics.py); outlet 60 mm aft of the
rotor plane, p = 0.  THE ROTOR IS NOT MODELLED (no suction), so separation on a
contracting hub is shown PESSIMISTICALLY; the comparison between cases is the
result, not the absolute numbers.

Metrics at the rotor plane: total-pressure loss inlet -> rotor (fraction of the
inlet dynamic pressure), axial-velocity non-uniformity over the span, the hub
deficit (mean u in the 3 mm next to the hub / span mean), and the fraction of
hub wall faces with reversed flow.

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, per AGENTS.md AI attribution.  License: MIT — see
LICENSES/MIT (SPDX-License-Identifier: MIT)
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nacelle_intake_cfd as ic  # noqa: E402  (helpers: foam, header, write, ...)

R_OUT = 32.0
MDOT = 0.385                 # kg/s (tandem design point)
RHO = 1.225
X0 = 62.0
CASES = {
    "B":      {"hub": [(X0, 15.5), (103.2, 15.5), (103.2, 12.5)], "x_rotor": 104.2},
    "A":      {"hub": [(X0, 15.5), (103.2, 15.5), (111.2, 12.5)], "x_rotor": 112.2},
    "A_thin": {"hub": [(X0, 15.0), (103.2, 15.0), (111.2, 12.5)], "x_rotor": 112.2},
    # Owner 2026-10-05: the QF2822 front fits a stator SLEEVE with OD = can OD
    # (Ø27.8, the stock QX arrangement), so the exposed can IS the hub (r 13.9).
    "S_step":  {"hub": [(X0, 13.9), (103.2, 13.9), (103.2, 12.5)], "x_rotor": 104.2},
    "S_taper": {"hub": [(X0, 13.9), (103.2, 13.9), (111.2, 12.5)], "x_rotor": 112.2},
    "S_taper6": {"hub": [(X0, 13.9), (103.2, 13.9), (109.2, 12.5)], "x_rotor": 110.2},
    "S_taper4": {"hub": [(X0, 13.9), (103.2, 13.9), (107.2, 12.5)], "x_rotor": 108.2},
}
WEDGE = math.radians(ic.WEDGE_DEG)


def block_mesh(case: dict, fine: bool) -> tuple[str, float]:
    """Wedge blockMesh: blocks in x between hub breakpoints, mm -> m."""
    f = 1.4 if fine else 1.0
    hub = case["hub"]
    x_end = case["x_rotor"] + 60.0
    step = hub[1][0] == hub[2][0]
    nodes, blocks, patches = [], [], {"inlet": [], "outlet": [], "hub": [], "duct": []}
    index: dict[tuple[float, float, int], int] = {}
    def v(x, r, side):
        # SHARED vertices: neighbouring blocks must reuse the same ids or
        # blockMesh leaves them unstitched (found 2026-10-05: 0 internal faces).
        key = (round(x, 6), round(r, 6), side)
        if key not in index:
            index[key] = len(nodes)
            nodes.append(f"({x / 1000:.9f} {r * math.cos(WEDGE) / 1000:.12f} "
                         f"{side * r * math.sin(WEDGE) / 1000:.12f})")
        return index[key]
    def hexb(q, nx, nr, grad):
        # q = [(x,r) x 4] counter-clockwise in (x, r): p0 low-x/low-r, p1 high-x/low-r, ...
        ids = [v(x, r, -1) for x, r in q] + [v(x, r, 1) for x, r in q]
        blocks.append(f"hex ({' '.join(map(str, ids))}) ({nx} {nr} 1) simpleGrading {grad}")
        return ids
    def fc(ids, a, b):            # quad on edge (a, b) across both wedge sides
        return f"({ids[a]} {ids[b]} {ids[b + 4]} {ids[a + 4]})"
    rg = "((0.5 0.5 5) (0.5 0.5 0.2))"
    nr = int(40 * f)
    if step:
        xs = hub[1][0]
        b1 = hexb([(X0, hub[0][1]), (xs, hub[1][1]), (xs, R_OUT), (X0, R_OUT)], int(70 * f), nr, f"(1 {rg} 1)")
        b2 = hexb([(xs, hub[1][1]), (x_end, hub[1][1]), (x_end, R_OUT), (xs, R_OUT)], int(80 * f), nr, f"(4 {rg} 1)")
        b3 = hexb([(xs, hub[2][1]), (x_end, hub[2][1]), (x_end, hub[1][1]), (xs, hub[1][1])], int(80 * f), int(14 * f), "(4 ((0.5 0.5 3) (0.5 0.5 0.33)) 1)")
        patches["inlet"] += [fc(b1, 3, 0)]
        patches["outlet"] += [fc(b2, 1, 2), fc(b3, 1, 2)]
        patches["hub"] += [fc(b1, 0, 1), fc(b3, 3, 0), fc(b3, 0, 1)]
        patches["duct"] += [fc(b1, 2, 3), fc(b2, 2, 3)]
        blocks_ids = [b1, b2, b3]
    else:
        (xa, ra), (xb, rb), (xc, rc) = hub
        b1 = hexb([(xa, ra), (xb, rb), (xb, R_OUT), (xa, R_OUT)], int(70 * f), nr, f"(1 {rg} 1)")
        b2 = hexb([(xb, rb), (xc, rc), (xc, R_OUT), (xb, R_OUT)], int(24 * f), nr, f"(1 {rg} 1)")
        b3 = hexb([(xc, rc), (x_end, rc), (x_end, R_OUT), (xc, R_OUT)], int(80 * f), nr, f"(4 {rg} 1)")
        patches["inlet"] += [fc(b1, 3, 0)]
        patches["outlet"] += [fc(b3, 1, 2)]
        patches["hub"] += [fc(b1, 0, 1), fc(b2, 0, 1), fc(b3, 0, 1)]
        patches["duct"] += [fc(b1, 2, 3), fc(b2, 2, 3), fc(b3, 2, 3)]
        blocks_ids = [b1, b2, b3]
    back = " ".join(f"({' '.join(map(str, b[:4]))})" for b in blocks_ids)
    front = " ".join(f"({' '.join(map(str, b[4:]))})" for b in blocks_ids)
    bnd = "\n".join(f"    {n} {{ type {'wall' if n in ('hub', 'duct') else 'patch'}; "
                    f"faces ( {' '.join(fl)} ); }}" for n, fl in patches.items())
    txt = ic.header("dictionary", "blockMeshDict") + f"""scale 1;
vertices
(
{chr(10).join(nodes)}
);
blocks
(
{chr(10).join(blocks)}
);
edges ();
boundary
(
{bnd}
    back  {{ type wedge; faces ( {back} ); }}
    front {{ type wedge; faces ( {front} ); }}
);
mergePatchPairs ();
"""
    return txt, x_end


def write_case(path: Path, case: dict, fine: bool) -> float:
    mesh, _ = block_mesh(case, fine)
    ic.write(path / "system/blockMeshDict", mesh)
    r_h = case["hub"][0][1] / 1000
    u_in = MDOT / (RHO * math.pi * ((R_OUT / 1000) ** 2 - r_h ** 2))
    k0, w0 = 1.5 * (0.03 * u_in) ** 2, 2000.0       # 3 % intensity behind the stator
    fields = {
        "U": ("volVectorField", "[0 1 -1 0 0 0 0]", f"uniform ({u_in:.4f} 0 0)", {
            "inlet": f"type fixedValue; value uniform ({u_in:.4f} 0 0);",
            "(hub|duct)": "type noSlip;", "outlet": "type zeroGradient;"}),
        "p": ("volScalarField", "[0 2 -2 0 0 0 0]", "uniform 0", {
            "inlet": "type zeroGradient;", "(hub|duct)": "type zeroGradient;",
            "outlet": "type fixedValue; value uniform 0;"}),
        "k": ("volScalarField", "[0 2 -2 0 0 0 0]", f"uniform {k0:.5f}", {
            "inlet": f"type fixedValue; value uniform {k0:.5f};",
            "(hub|duct)": f"type kqRWallFunction; value uniform {k0:.5f};",
            "outlet": "type zeroGradient;"}),
        "omega": ("volScalarField", "[0 0 -1 0 0 0 0]", f"uniform {w0}", {
            "inlet": f"type fixedValue; value uniform {w0};",
            "(hub|duct)": f"type omegaWallFunction; value uniform {w0};",
            "outlet": "type zeroGradient;"}),
        "nut": ("volScalarField", "[0 2 -1 0 0 0 0]", "uniform 0", {
            "inlet": "type calculated; value uniform 0;",
            "(hub|duct)": "type nutkWallFunction; value uniform 0;",
            "outlet": "type calculated; value uniform 0;"}),
    }
    for name, (cls, dims, internal, bcs) in fields.items():
        body = "\n".join(f'    "{p}" {{ {v} }}' for p, v in bcs.items())
        ic.write(path / "0" / name, ic.header(cls, name, "0")
                 + f"dimensions {dims};\ninternalField {internal};\n"
                 + f"boundaryField\n{{\n{body}\n    \"(back|front)\" {{ type wedge; }}\n}}\n")
    # same physics / numerics as tools/nacelle_intake_cfd.py
    ic.write(path / "constant/transportProperties", ic.header("dictionary", "transportProperties")
             + f"transportModel Newtonian;\nnu [0 2 -1 0 0 0 0] {ic.NU};\n")
    ic.write(path / "constant/turbulenceProperties", ic.header("dictionary", "turbulenceProperties")
             + "simulationType RAS;\nRAS { RASModel kOmegaSST; turbulence on; printCoeffs off; }\n")
    ic.write(path / "system/controlDict", ic.header("dictionary", "controlDict") + """
application simpleFoam; startFrom startTime; startTime 0; stopAt endTime; endTime 2500;
deltaT 1; writeControl timeStep; writeInterval 2500; purgeWrite 0; writeFormat ascii;
writePrecision 8; timeFormat general; timePrecision 6; runTimeModifiable false;
""")
    ic.write(path / "system/fvSchemes", ic.header("dictionary", "fvSchemes") + """
ddtSchemes { default steadyState; }
gradSchemes { default Gauss linear; grad(U) cellLimited Gauss linear 1; }
divSchemes { default none; div(phi,U) bounded Gauss linearUpwind grad(U);
    div(phi,k) bounded Gauss upwind; div(phi,omega) bounded Gauss upwind;
    div((nuEff*dev2(T(grad(U))))) Gauss linear; }
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes { default corrected; }
wallDist { method meshWave; }
""")
    ic.write(path / "system/fvSolution", ic.header("dictionary", "fvSolution") + """
solvers { p { solver GAMG; tolerance 1e-7; relTol 0.01; smoother GaussSeidel; }
    "(U|k|omega)" { solver smoothSolver; smoother GaussSeidel; tolerance 1e-8; relTol 0.1; } }
SIMPLE { nNonOrthogonalCorrectors 1; consistent yes;
    residualControl { p 1e-5; U 1e-6; "(k|omega)" 1e-6; } }
relaxationFactors { equations { U 0.7; ".*" 0.7; } fields { p 0.5; } }
""")
    return u_in


def cell_centres(case: Path) -> np.ndarray:
    """Cell centres from the ASCII polyMesh (mean of face centres per cell)."""
    pm = case / "constant/polyMesh"
    pts = np.array([ic._vec(l) for l in ic._foam_list(pm / "points")])
    faces = [list(map(int, l[l.index("(") + 1:l.rindex(")")].split())) for l in ic._foam_list(pm / "faces")]
    owner = np.array([int(l) for l in ic._foam_list(pm / "owner")])
    neigh = np.array([int(l) for l in ic._foam_list(pm / "neighbour")])
    fc = np.array([pts[f].mean(axis=0) for f in faces])
    n = owner.max() + 1
    acc = np.zeros((n, 3)); cnt = np.zeros(n)
    np.add.at(acc, owner, fc); np.add.at(cnt, owner, 1)
    np.add.at(acc, neigh, fc[:len(neigh)]); np.add.at(cnt, neigh, 1)
    return acc / cnt[:, None], fc, owner, faces


def analyse(path: Path, case: dict, u_in: float) -> dict:
    t = ic.last_time(path)
    if t is None:
        return {"error": "no solution"}
    C, fc, owner, faces = cell_centres(path)
    U = np.array(ic._internal_field(t / "U")); p = np.array(ic._internal_field(t / "p"))
    x = C[:, 0] * 1000; r = np.hypot(C[:, 1], C[:, 2]) * 1000
    p0 = p + 0.5 * (U ** 2).sum(axis=1)
    def plane(xp, w=0.6):
        m = np.abs(x - xp) < w
        return m
    def mavg(m, q):
        wgt = np.clip(U[m, 0], 0, None) * r[m]
        return float((q[m] * wgt).sum() / max(wgt.sum(), 1e-12))
    m_in, m_rot = plane(X0 + 1.5), plane(case["x_rotor"])
    loss = (mavg(m_in, p0) - mavg(m_rot, p0)) / (0.5 * u_in ** 2)
    ux = U[m_rot, 0]; rr = r[m_rot]
    w = rr / rr.sum()
    mean = float((ux * w).sum()); nonuni = float(np.sqrt(((ux - mean) ** 2 * w).sum()) / mean)
    r_hub_at_rotor = case["hub"][-1][1]
    hub_band = rr < r_hub_at_rotor + 3.0
    deficit = float(ux[hub_band].mean() / mean) if hub_band.any() else float("nan")
    # reversed flow: cells within 1.5 mm of the hub contour, aft of x 100
    hub = case["hub"]
    def r_hub(xq):
        return np.interp(xq, [h[0] for h in hub] + [999], [h[1] for h in hub] + [hub[-1][1]])
    near = (r - r_hub(x) < 1.5) & (r > r_hub(x) - 0.01) & (x > 100) & (x < case["x_rotor"] + 2)
    rev = float((U[near, 0] < 0).mean()) if near.any() else 0.0
    return {"loss_q": round(loss, 4), "nonuniformity": round(nonuni, 4),
            "hub_deficit": round(deficit, 3), "reversed_near_hub": round(rev, 3),
            "u_mean_rotor": round(mean, 2)}


def main() -> int:
    import argparse
    import json
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dir", type=Path)
    ap.add_argument("--cases", nargs="*", default=list(CASES))
    ap.add_argument("--fine", action="store_true")
    a = ap.parse_args()
    out = {}
    for name in a.cases:
        path = a.dir / name
        u_in = write_case(path, CASES[name], a.fine)
        bm = ic.foam("blockMesh", path); (path / "log.blockMesh").write_text(bm.stdout + bm.stderr)
        cm = ic.foam("checkMesh", path); (path / "log.checkMesh").write_text(cm.stdout + cm.stderr)
        sv = ic.foam("simpleFoam", path); (path / "log.simpleFoam").write_text(sv.stdout + sv.stderr)
        res = ic.residuals(sv.stdout)
        out[name] = {"u_in": round(u_in, 2), "mesh_ok": "Mesh OK" in cm.stdout,
                     "residuals": res, **analyse(path, CASES[name], u_in)}
        print(name, json.dumps(out[name]), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
