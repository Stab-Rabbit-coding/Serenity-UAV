#!/usr/bin/env python3
"""
nacelle_crossflow_cfd.py — 3-D OpenFOAM screen of the tilt-axis aero moment on
the 64 mm nacelle in crossflow (WBS NAC-64-TILT-01 action (c), TILT-CTL-06).

WHY
---
The tilt drive and its 50T tip ring gear carry the aero moment about the tilt
axis, and the bearings carry its couple.  tools/nacelle_tilt_dynamics.py had
only a first-order momentum-drag estimate, and its BOUNDING case (an ASSUMED
2 x corridor crossflow) left the tip gear at Lewis FOS 2.2.  The owner chose
(2026-10-03) to bound the aero with CFD before resizing the gear.

MODEL
-----
  * Steady, incompressible simpleFoam, k-omega SST, wall functions, full 3-D
    (no symmetry plane, so no snap-to-boundary artefacts on the body).
  * Body: a solid of revolution built from the adopted design's contours —
    the lipE elliptical lip and 64 mm bore inside; the lip ring, then the
    measured canonical skin (nacelle_hollow_profile.scad, mean radius per
    station, x 1.21 radial, x 1.13 axial), then a taper to the exit outside.
    The pod's non-round canonical section is averaged to round; ESC covers,
    trunnion collar and nozzle flaps are not modelled.  Recorded limitation.
  * Fan: a 2 mm disc closing the bore at the rotor station.  Its upstream
    face is an OUTFLOW at the hover volume flow and its downstream face an
    INFLOW at the same flow, axial — the fan's mass flow and jet without a
    blade model or baffle function objects (every function object aborts in
    the packaged v1912 here; see tools/nacelle_intake_cfd.py).
  * Freestream: crossflow normal to the nacelle axis at the corridor value
    7.8 m/s and the bound 15.6 m/s (tools/nacelle_tilt_dynamics.py
    V_CROSS), plus 0 m/s as a hover control.
  * Loads: F = rho * sum over body faces of (p S_f + U (U . S_f)), i.e. wall
    pressure plus momentum flux through the fan faces (control volume
    around the fan).  Viscous wall shear is NOT included (pressure-dominated
    bluff-body/inlet loads; recorded).  Moment about the tilt axis (spanwise,
    through PIVOT_Z on the duct axis).

Coordinates: nacelle axis +z from the intake face (nacelle-local Z), crossflow
+x, tilt axis along y through (0, 0, PIVOT_Z).

Usage:
    /usr/bin/python3 tools/nacelle_crossflow_cfd.py --workdir DIR [--np 4]

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CEH (GitHub Stab-Rabbit-coding) —
owner decision to bound the aero before resizing the gear.  Case generator and
analysis by Claude (Claude Opus 5.5, Anthropic) under the author's direction,
per AGENTS.md AI attribution.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import math
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nacelle_intake_cfd as ic  # FOAM helpers, header(), write(), field parse

REPO = Path(__file__).resolve().parent.parent
RHO = 1.225
K, A = 1.21, 1.13                     # adopted radial / axial scale
R_BORE = 0.032
LIP_A, LIP_F = 0.016, 0.008           # lipE internal ellipse
RING_R, FORE_A, RING_HOLD = 0.0425, 0.0015625, 0.022
L_NAC = 0.1852 * A                    # 0.20928 m
R_EXIT_OUT = 0.036
Z_FAN, FAN_T = 0.0305, 0.002          # rotor station, disc thickness
PIVOT_Z = 0.1097
THRUST_N = 2 * 20.9 * 0.90            # [REF-EDF-003] tandem screen
Q_FAN = math.sqrt(THRUST_N / RHO * math.pi * R_BORE ** 2)   # m^3/s
CROSSFLOWS = {"hover (0 m/s)": 0.0, "corridor (7.8 m/s)": 7.8,
              "bound (15.6 m/s)": 15.6}
N_AZ = 96


def skin_mean() -> list[tuple[float, float]]:
    """(z, r) of the canonical skin, azimuth-averaged, scaled, metres."""
    t = (REPO / "airframe/openscad/nacelles/nacelle_hollow_profile.scad"
         ).read_text(encoding="utf-8")
    zs = [float(v) for v in
          re.search(r"HOLLOW_Z = \[(.*?)\];", t).group(1).split(",")]
    body = re.search(r"HOLLOW_SKIN_STBD = \[(.*?)\];", t, re.DOTALL).group(1)
    rows = [[float(v) for v in r.strip(" [],\n").split(",") if v.strip()]
            for r in body.split("],") if r.strip(" \n[]")]
    return [(z * A / 1000.0, sum(r) / len(r) * K / 1000.0)
            for z, r in zip(zs, rows)]


def profile() -> list[tuple[float, float]]:
    """Closed (r, z) polygon of the body cross-section, metres, CCW."""
    def r_in(z: float) -> float:
        u = 1.0 - z / LIP_A
        return R_BORE + LIP_F * (1.0 - math.sqrt(max(0.0, 1.0 - u * u)))

    def r_out(z: float) -> float:
        u = 1.0 - z / FORE_A
        return R_BORE + LIP_F + (RING_R - R_BORE - LIP_F) * math.sqrt(
            max(0.0, 1.0 - u * u))

    pts: list[tuple[float, float]] = []
    # inner flow surface, exit -> fan downstream face
    pts += [(R_BORE, L_NAC), (R_BORE, Z_FAN + FAN_T)]
    # fan disc
    pts += [(0.0, Z_FAN + FAN_T), (0.0, Z_FAN), (R_BORE, Z_FAN)]
    # inner surface, fan -> lip throat -> highlight
    pts += [(r_in(LIP_A * i / 24), LIP_A * i / 24) for i in range(24, -1, -1)]
    # external lip branch, highlight -> ring
    pts += [(r_out(FORE_A * i / 12), FORE_A * i / 12) for i in range(1, 13)]
    pts += [(RING_R, RING_HOLD)]
    # canonical skin (mean), then taper to the exit
    sk = [p for p in skin_mean() if p[0] > RING_HOLD + 0.002]
    pts += [(r, z) for z, r in sk]
    pts += [(R_EXIT_OUT, L_NAC)]
    return pts


def revolve_stl(path: Path) -> None:
    """Multi-solid ASCII STL: regions wall, fanIn, fanOut."""
    prof = profile()
    tris: dict[str, list] = {"wall": [], "fanIn": [], "fanOut": []}
    angs = [2 * math.pi * k / N_AZ for k in range(N_AZ)]

    def pt(r: float, z: float, a: float) -> tuple[float, float, float]:
        return (r * math.cos(a), r * math.sin(a), z)

    n = len(prof)
    for i in range(n):
        (r0, z0), (r1, z1) = prof[i], prof[(i + 1) % n]
        if r0 == 0.0 and r1 == 0.0:
            continue
        if abs(z0 - z1) < 1e-12 and abs(z0 - Z_FAN) < 1e-9:
            region = "fanIn"
        elif abs(z0 - z1) < 1e-12 and abs(z0 - Z_FAN - FAN_T) < 1e-9:
            region = "fanOut"
        else:
            region = "wall"
        for k in range(N_AZ):
            a0, a1 = angs[k], angs[(k + 1) % N_AZ]
            p00, p01 = pt(r0, z0, a0), pt(r0, z0, a1)
            p10, p11 = pt(r1, z1, a0), pt(r1, z1, a1)
            if r0 > 0:
                tris[region].append((p00, p10, p01))
            if r1 > 0:
                tris[region].append((p01, p10, p11))
    lines = []
    for name, ts in tris.items():
        lines.append(f"solid {name}")
        for a, b, c in ts:
            ux, uy, uz = (b[i] - a[i] for i in range(3))
            vx, vy, vz = (c[i] - a[i] for i in range(3))
            nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
            m = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            lines.append(f"  facet normal {nx / m:.6e} {ny / m:.6e} "
                         f"{nz / m:.6e}\n    outer loop")
            for p in (a, b, c):
                lines.append(f"      vertex {p[0]:.7e} {p[1]:.7e} {p[2]:.7e}")
            lines.append("    endloop\n  endfacet")
        lines.append(f"endsolid {name}")
    ic.write(path, "\n".join(lines) + "\n")


def write_case(case: Path, vc: float, np_: int) -> None:
    """All dictionaries for one crossflow speed."""
    h = ic.header
    revolve_stl(case / "constant/triSurface/nacelle.stl")
    ic.write(case / "system/blockMeshDict", h("dictionary", "blockMeshDict") + """
scale 1;
vertices ( (-0.45 -0.35 -0.30) (0.75 -0.35 -0.30) (0.75 0.35 -0.30)
           (-0.45 0.35 -0.30) (-0.45 -0.35 0.60) (0.75 -0.35 0.60)
           (0.75 0.35 0.60) (-0.45 0.35 0.60) );
blocks ( hex (0 1 2 3 4 5 6 7) (48 28 36) simpleGrading (1 1 1) );
boundary
(
    inlet  { type patch; faces ((0 4 7 3)); }
    outlet { type patch; faces ((1 2 6 5)); }
    sides  { type patch; faces ((0 1 5 4) (3 7 6 2) (0 3 2 1) (4 5 6 7)); }
);
""")
    ic.write(case / "system/surfaceFeatureExtractDict",
             h("dictionary", "surfaceFeatureExtractDict") + """
nacelle.stl
{
    extractionMethod extractFromSurface;
    extractFromSurfaceCoeffs { includedAngle 150; }
    writeObj no;
}
""")
    ic.write(case / "system/snappyHexMeshDict", h("dictionary", "snappyHexMeshDict") + """
castellatedMesh true; snap true; addLayers false;
geometry
{
    nacelle.stl { type triSurfaceMesh; name nacelle;
        regions { wall { name wall; } fanIn { name fanIn; } fanOut { name fanOut; } } }
    near { type searchableBox; min (-0.08 -0.08 -0.05); max (0.12 0.08 0.30); }
}
castellatedMeshControls
{
    maxLocalCells 2000000; maxGlobalCells 6000000; minRefinementCells 10;
    maxLoadUnbalance 0.10; nCellsBetweenLevels 3;
    features ( { file "nacelle.eMesh"; level 3; } );
    refinementSurfaces { nacelle { level (3 3);
        regions { fanIn { level (4 4); } fanOut { level (4 4); } } } }
    resolveFeatureAngle 30;
    refinementRegions { near { mode inside; levels ((1E15 2)); } }
    locationInMesh (0.40 0.20 0.45);
    allowFreeStandingZoneFaces true;
}
snapControls { nSmoothPatch 3; tolerance 2.0; nSolveIter 50; nRelaxIter 5;
    nFeatureSnapIter 10; implicitFeatureSnap false; explicitFeatureSnap true;
    multiRegionFeatureSnap false; }
addLayersControls { relativeSizes true; layers { } expansionRatio 1.2;
    finalLayerThickness 0.3; minThickness 0.1; nGrow 0; featureAngle 60;
    nRelaxIter 3; nSmoothSurfaceNormals 1; nSmoothNormals 3;
    nSmoothThickness 10; maxFaceThicknessRatio 0.5;
    maxThicknessToMedialRatio 0.3; minMedianAxisAngle 90;
    nBufferCellsNoExtrude 0; nLayerIter 50; }
meshQualityControls { maxNonOrtho 65; maxBoundarySkewness 20;
    maxInternalSkewness 4; maxConcave 80; minVol 1e-13; minTetQuality 1e-15;
    minArea -1; minTwist 0.02; minDeterminant 0.001; minFaceWeight 0.05;
    minVolRatio 0.01; minTriangleTwist -1; nSmoothScale 4;
    errorReduction 0.75; }
mergeTolerance 1e-6;
""")
    k0, w0 = 0.5, 200.0
    walls = "wall"
    v_in = f"({vc:.4f} 0 0)"
    fields = {
        "U": ("volVectorField", "[0 1 -1 0 0 0 0]", f"uniform {v_in}", {
            "inlet": f"type fixedValue; value uniform {v_in};",
            "outlet": "type inletOutlet; inletValue uniform (0 0 0); "
                      "value uniform (0 0 0);",
            "sides": "type pressureInletOutletVelocity; value uniform (0 0 0);",
            walls: "type noSlip;",
            "fanIn": f"type flowRateOutletVelocity; "
                             f"volumetricFlowRate {Q_FAN:.6f}; "
                             "value uniform (0 0 0);",
            "fanOut": f"type flowRateInletVelocity; "
                              f"volumetricFlowRate {Q_FAN:.6f}; "
                              "value uniform (0 0 0);"}),
        "p": ("volScalarField", "[0 2 -2 0 0 0 0]", "uniform 0", {
            "inlet": "type zeroGradient;",
            "outlet": "type fixedValue; value uniform 0;",
            "sides": "type totalPressure; p0 uniform 0; value uniform 0;",
            walls: "type zeroGradient;",
            "(fanIn|fanOut)": "type zeroGradient;"}),
        "k": ("volScalarField", "[0 2 -2 0 0 0 0]", f"uniform {k0}", {
            "(inlet|fanOut)": f"type fixedValue; value uniform {k0};",
            "(outlet|sides|fanIn)":
                f"type inletOutlet; inletValue uniform {k0}; value uniform {k0};",
            walls: f"type kqRWallFunction; value uniform {k0};"}),
        "omega": ("volScalarField", "[0 0 -1 0 0 0 0]", f"uniform {w0}", {
            "(inlet|fanOut)": f"type fixedValue; value uniform {w0};",
            "(outlet|sides|fanIn)":
                f"type inletOutlet; inletValue uniform {w0}; value uniform {w0};",
            walls: f"type omegaWallFunction; value uniform {w0};"}),
        "nut": ("volScalarField", "[0 2 -1 0 0 0 0]", "uniform 0", {
            "(inlet|outlet|sides|fanIn|fanOut)":
                "type calculated; value uniform 0;",
            walls: "type nutkWallFunction; value uniform 0;"}),
    }
    for name, (cls, dims, internal, bcs) in fields.items():
        body = "\n".join(f'    "{p}" {{ {v} }}' for p, v in bcs.items())
        ic.write(case / "0" / name, h(cls, name, "0")
                 + f"dimensions {dims};\ninternalField {internal};\n"
                 + f"boundaryField\n{{\n{body}\n}}\n")
    ic.write(case / "constant/transportProperties",
             h("dictionary", "transportProperties")
             + f"transportModel Newtonian;\nnu [0 2 -1 0 0 0 0] {ic.NU};\n")
    ic.write(case / "constant/turbulenceProperties",
             h("dictionary", "turbulenceProperties")
             + "simulationType RAS;\nRAS { RASModel kOmegaSST; turbulence on; "
               "printCoeffs off; }\n")
    ic.write(case / "system/controlDict", h("dictionary", "controlDict") + """
application     simpleFoam;
startFrom       latestTime;
startTime       0;
stopAt          endTime;
endTime         1500;
deltaT          1;
writeControl    timeStep;
writeInterval   1500;
purgeWrite      0;
writeFormat     ascii;
writePrecision  8;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;
""")
    src = case.parent / "_tmpl"
    for d in ("fvSchemes", "fvSolution"):
        shutil.copy(src / "system" / d, case / "system" / d)
    ic.write(case / "system/decomposeParDict",
             h("dictionary", "decomposeParDict")
             + f"numberOfSubdomains {np_};\nmethod hierarchical;\n"
             # the packaged v1912 links a dummy Scotch: hierarchical needs none
             + f"hierarchicalCoeffs {{ n ({np_} 1 1); order xyz; }}\n")


def run(case: Path, np_: int) -> dict:
    """Mesh, solve in parallel, reconstruct; return log tails."""
    steps = ["blockMesh", "surfaceFeatureExtract",
             "snappyHexMesh -overwrite", "checkMesh", "decomposePar -force",
             f"mpirun -np {np_} --oversubscribe simpleFoam -parallel",
             "reconstructPar -latestTime"]
    out = {}
    for cmd in steps:
        r = ic.foam(cmd, case)
        name = cmd.split()[0] if not cmd.startswith("mpirun") else "simpleFoam"
        (case / f"log.{name}").write_text(r.stdout + r.stderr)
        out[name] = r.stdout
    return out


def body_loads(case: Path) -> dict:
    """Force and tilt-axis moment on the body from raw fields (see MODEL)."""
    t = ic.last_time(case)
    mesh = case / "constant/polyMesh"
    pts = [ic._vec(v) for v in ic._foam_list(mesh / "points")]
    owner = [int(v) for v in ic._foam_list(mesh / "owner")]
    btext = (mesh / "boundary").read_text(encoding="utf-8")
    vel = ic._internal_field(t / "U")
    prs = ic._internal_field(t / "p")
    faces_txt = ic._foam_list(mesh / "faces")
    fx = fz = my = 0.0
    per: dict[str, list[float]] = {}
    for patch in ("wall", "fanIn", "fanOut"):
        blk = btext[btext.index(f"    {patch}\n"):]
        n = int(blk.split("nFaces")[1].split(";")[0])
        start = int(blk.split("startFace")[1].split(";")[0])
        pf = [0.0, 0.0, 0.0]
        for fi in range(start, start + n):
            v = faces_txt[fi]
            idx = [int(i) for i in v[v.index("(") + 1:-1].split()]
            ps = [pts[i] for i in idx]
            cx = sum(p[0] for p in ps) / len(ps)
            cy = sum(p[1] for p in ps) / len(ps)
            cz = sum(p[2] for p in ps) / len(ps)
            sx = sy = sz = 0.0              # area vector (out of the fluid)
            for k in range(len(ps)):
                a, b = ps[k], ps[(k + 1) % len(ps)]
                ax, ay, az = a[0] - cx, a[1] - cy, a[2] - cz
                bx, by, bz = b[0] - cx, b[1] - cy, b[2] - cz
                sx += 0.5 * (ay * bz - az * by)
                sy += 0.5 * (az * bx - ax * bz)
                sz += 0.5 * (ax * by - ay * bx)
            c = owner[fi]
            u = vel[c]
            flux = u[0] * sx + u[1] * sy + u[2] * sz
            dfx = RHO * (prs[c] * sx + u[0] * flux)
            dfz = RHO * (prs[c] * sz + u[2] * flux)
            dfy = RHO * (prs[c] * sy + u[1] * flux)
            pf = [pf[0] + dfx, pf[1] + dfy, pf[2] + dfz]
            # moment about the tilt axis (y) through (0, 0, PIVOT_Z)
            my += (cz - PIVOT_Z) * dfx - cx * dfz
        per[patch] = pf
        fx += pf[0]
        fz += pf[2]
    return {"Fx": fx, "Fz": fz, "My": my, "per": per}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--workdir", required=True, type=Path)
    ap.add_argument("--np", type=int, default=4)
    ap.add_argument("--only", nargs="*", default=None)
    args = ap.parse_args(argv)
    # numerics template from the validated axisymmetric tool
    tmpl = args.workdir / "_tmpl"
    if tmpl.exists():
        shutil.rmtree(tmpl)
    ic.write_case(tmpl, ic.VARIANTS[0], False)
    print(f"fan volume flow {Q_FAN:.4f} m^3/s ({Q_FAN * RHO:.3f} kg/s), bore "
          f"velocity {Q_FAN / (math.pi * R_BORE ** 2):.1f} m/s")
    ok = True
    for tag, vc in CROSSFLOWS.items():
        if args.only and tag.split()[0] not in args.only:
            continue
        case = args.workdir / tag.split()[0]
        if case.exists():
            shutil.rmtree(case)
        write_case(case, vc, args.np)
        logs = run(case, args.np)
        cells = re.search(r"cells:\s+(\d+)", logs.get("checkMesh", ""))
        res = ic.residuals(logs.get("simpleFoam", ""))
        good = "Mesh OK" in logs.get("checkMesh", "")
        if not good or not res:
            print(f"{tag}: mesh {'OK' if good else 'FAILED'}, solver "
                  f"{'ran' if res else 'FAILED'} — see {case}/log.*")
            ok = False
            continue
        loads = body_loads(case)
        print(f"\n{tag}: {cells.group(1) if cells else '?'} cells, max final "
              f"residual {max(res.values()):.1e}")
        print(f"  normal force Fx {loads['Fx']:+.2f} N "
              f"({loads['Fx'] * 0.224809:+.3f} lbf), axial Fz "
              f"{loads['Fz']:+.2f} N, tilt-axis moment My {loads['My']:+.4f} "
              f"N.m ({loads['My'] * 8.8507:+.3f} lbf.in)")
        for patch, f in loads["per"].items():
            print(f"    {patch:<16} F = ({f[0]:+.2f}, {f[1]:+.2f}, {f[2]:+.2f}) N")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
