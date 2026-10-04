#!/usr/bin/env python3
"""
nacelle_intake_cfd.py — axisymmetric OpenFOAM screen of the 64 mm intake bell.

WHAT THIS SCREENS
-----------------
Plan docs/plans/2026-09-28-001-feat-nacelle-nozzle-servo-drive-plan.md U12
step 2, and the owner's 2026-10-03 direction to put rotor 1 INSIDE the intake
bell (as in the QX shroud) after the bell was trimmed 27.5 -> 19.5 mm.  The
questions, in the static / hover condition where an inlet lip works hardest:

  1. Does flow separate off the lip or the bell wall?  (wall shear stress
     x-component < 0 on the lip/bell = reversed flow)
  2. What flow angle and total-pressure deficit does the rotor leading edge
     see, near the tip, at its in-bell station?
  3. How do the trimmed (19.5 mm) and original (27.5 mm) bells compare?

MODEL — and its limits, stated so they are not forgotten
--------------------------------------------------------
  * 2-D axisymmetric wedge (5 deg), x = duct axis, y = radius.  Steady,
    incompressible simpleFoam, k-omega SST with wall functions.
  * The fan is NOT modelled.  Its suction is imposed as a uniform axial outlet
    velocity 80 mm downstream of the intake face, at the hover bore velocity
    from momentum theory for the QX 2400 KV 6S table thrust (REF-EDF-003):
    T = 20.9 N per fan, A = pi (0.032 m)^2, V = sqrt(T / (rho A)) = 72.8 m/s
    (142 kt).  Swirl, blade blockage and tip leakage are absent; the result
    is the INLET flow the rotor would ingest, not installed thrust.
  * The lip is the SHARP edge the pod SCAD actually produces: the cosine bell
    cut (r = 35.84 mm at Z 0) is larger than the fairing's planar lip
    (INTAKE_LIP_R = 34.5 mm), so the leading edge is where the two cross.
    It is modelled as a flanged sharp lip (a wall annulus in the Z 0 plane) —
    a conservative stand-in for the real fairing, which sweeps aft and so
    turns the flow slightly less hard.
  * Static ambient: total pressure 0 (gauge) on the far field.
  CFD here is a screening tool, not an acceptance test (plan Verification
  Contract): the principal result must be checked on a pressure/thrust bench.

Usage:
    /usr/bin/python3 tools/nacelle_intake_cfd.py --workdir DIR [--fine]

Writes one case per bell length under DIR, runs blockMesh, checkMesh and
simpleFoam (OpenFOAM v1912, sourced from FOAM_BASHRC), samples the results and
prints a comparison table.  Exit 0 = all cases converged and meshed cleanly.

References (REFERENCES.md): [REF-EDF-003] QX-Motor 64 mm EDF thrust table.
Method guidance: aeronautical-engineering skill references/propulsion.md §1
(momentum theory) and §3 (duct inlet lip and tip clearance are first-order);
openfoam-cfd skill best practices (checkMesh, residuals, y+, mesh study).

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CEH (GitHub Stab-Rabbit-coding) —
rotor-in-bell direction and design ownership.  Case generator and analysis by
Claude (Claude Opus 5.5, Anthropic) under the author's direction, per AGENTS.md
AI attribution.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import math
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# OpenFOAM environment script (same install wing_cfd_openfoam.py uses).
FOAM_BASHRC = "/usr/share/openfoam/etc/bashrc"

# ── Geometry, metres.  Shared constants with tools/nacelle_axial_fit.py ──────
R_BORE = 0.032                   # 64 mm nominal flow diameter (KTD9)
FLARE = 0.003 * 64.0 / 50.0      # 3.84 mm bell flare, scaled with the shell
X_UP = -0.150                    # far-field plenum upstream extent
R_FAR = 0.150                    # far-field plenum radius
X_OUT = 0.080                    # fan-suction outlet station
WEDGE_DEG = 2.5                  # half-angle of the axisymmetric wedge
TIP_GROWTH = 0.0001              # 0.1 mm allowed extra tip gap (in-bell rule)

# ── Hover operating point (momentum theory, propulsion.md §1) ───────────────
RHO = 1.225                      # kg/m^3 ISA sea level
THRUST_N = 20.9                  # N per fan, QX 2400 KV 6S table [REF-EDF-003]
NU = 1.5e-5                      # m^2/s air
V_BORE = math.sqrt(THRUST_N / (RHO * math.pi * R_BORE ** 2))   # = 72.8 m/s


@dataclass(frozen=True)
class Bell:
    """One intake variant: profile kind, axial length L and radial flare F, m.

    cosine   the pod SCAD's inlet_bellmouth(): r = R + F/2 (1 + cos(pi x/L)).
             Zero slope at x = 0, so it meets the flat front face at a SQUARE
             corner — a sharp lip.
    ellipse  quarter-ellipse lip, r = R + F (1 - sqrt(1 - (1 - x/L)^2)).
             Vertical tangent at x = 0, so it rolls smoothly into the front
             face — a rounded lip, as on a manufacturer's EDF shroud.
    """

    name: str
    kind: str
    length: float
    flare: float
    rotor_z: float | None = None   # fixed rotor LE station (straight duct)
    # External forebody (axial semi-axis, end radius), m.  None = the
    # conservative flanged lip face; set = the real slim nacelle exterior,
    # an elliptical forebody then a cylinder, with open far field around it.
    fore: tuple[float, float] | None = None


# Variants compared.  The first two are the pod as drawn (sharp lip); the
# last two are rounded lips — one inside today's 3.84 mm flare envelope, one
# QX-shroud-like (lip OD 77.00 mm on a ~64 mm duct ~= 6.5 mm radial lip,
# 7-2.jpg [REF-EDF-003], read as an outline dimension — VERIFY).
VARIANTS = (
    Bell("cos27p5", "cosine", 0.0275, FLARE),
    Bell("cos19p5", "cosine", 0.0195, FLARE),
    Bell("ell19p5_f3p84", "ellipse", 0.0195, FLARE),
    Bell("ell19p5_f6p5", "ellipse", 0.0195, 0.0065),
    # Proportion-trade pick (tools/nacelle_64_proportion_trade.py): a 2:1
    # elliptical lip (13 x 6.5 mm, nose radius b^2/a = 3.25 mm) then straight
    # duct, rotor LE at 30.5 mm in the constant bore — no tip-gap growth.
    Bell("ell2to1_13_f6p5_rot30p5", "ellipse", 0.013, 0.0065, 0.0305),
    # The sweep's literal long bell, kept to show why it was not adopted:
    # 39.5 x 6.5 mm has a 1.07 mm nose radius.
    Bell("ell39p5_f6p5", "ellipse", 0.0395, 0.0065),
    # The pick with its REAL exterior (nacelle_pod_64mm_tandem.scad
    # P64_FORE_A 22.0, P64_FORE_R 40.5): a slim lip, which hover inflow wraps
    # around from behind — the harder case the flange cannot represent.
    Bell("ell2to1_13_f6p5_rot30p5_fore", "ellipse", 0.013, 0.0065, 0.0305,
         (0.022, 0.0405)),
    # Rounded-nose lip sweep (2026-10-03).  The 22 x 2 mm forebody above has
    # an external nose radius B^2/A = 0.18 mm — a knife edge on the outside —
    # and separates in hover.  Each variant below gives the external branch
    # the SAME curvature radius as the internal one at the highlight
    # (A_out = 2 B^2 / F for a 2:1 internal ellipse), so the nose is a true
    # round.  Internal flare trades against external room under the skin.
    Bell("lipA_f6p5_b2p0", "ellipse", 0.013, 0.0065, 0.0305, (0.00123, 0.0405)),
    Bell("lipB_f5p0_b3p5", "ellipse", 0.010, 0.0050, 0.0305, (0.0049, 0.0405)),
    Bell("lipC_f4p0_b4p5", "ellipse", 0.008, 0.0040, 0.0305, (0.0101, 0.0405)),
    Bell("lipD_f5p0_b5p5", "ellipse", 0.010, 0.0050, 0.0305, (0.0121, 0.0425)),
    # Higher contraction, lip ring allowed to the skin's LARGEST first-station
    # radius (42.5 mm); ahead of Z 24 the canonical dome is narrower anyway.
    Bell("lipE_f8p0_b2p5", "ellipse", 0.016, 0.0080, 0.0305, (0.00156, 0.0425)),
    Bell("lipF_f6p5_b4p0", "ellipse", 0.013, 0.0065, 0.0305, (0.00492, 0.0425)),
    # 3:1 internal ellipse (longer, gentler hand-off to the straight duct;
    # 2:1 left a bubble at x 13-18 mm).  External A = B^2 / (F^2 / a).
    Bell("lipG_3to1_f6p5_b4p0", "ellipse", 0.0195, 0.0065, 0.0305,
         (0.00738, 0.0425)),
    Bell("lipH_3to1_f8p0_b2p5", "ellipse", 0.024, 0.0080, 0.0305,
         (0.00234, 0.0425)),
)
# Variants run by --only (default: all).


def bell_r(x: float, bell: Bell) -> float:
    """Wall radius of the bell at axial station x (0 <= x <= L), m."""
    if bell.kind == "cosine":
        return R_BORE + bell.flare * 0.5 * (
            1.0 + math.cos(math.pi * x / bell.length))
    u = 1.0 - x / bell.length
    return R_BORE + bell.flare * (1.0 - math.sqrt(max(0.0, 1.0 - u * u)))


def rotor_entry(bell: Bell) -> float:
    """Forward-most rotor LE station with <= TIP_GROWTH extra tip gap, m.

    Bisection on the monotonic bell profile, so it holds for every kind.
    A variant with a fixed rotor station (straight duct) returns that.
    """
    if bell.rotor_z is not None:
        return bell.rotor_z
    lo, hi = 0.0, bell.length
    for _ in range(60):
        midx = 0.5 * (lo + hi)
        if bell_r(midx, bell) - R_BORE > TIP_GROWTH:
            lo = midx
        else:
            hi = midx
    return hi


def foam(cmd: str, cwd: Path) -> subprocess.CompletedProcess:
    """Run one OpenFOAM utility with the environment sourced.

    Commands are fixed strings built by this script (no user input reaches the
    shell), and the case directory is passed as cwd, not interpolated.
    """
    full = f"source {FOAM_BASHRC} >/dev/null 2>&1; {cmd}"
    return subprocess.run(["bash", "-c", full], cwd=cwd, capture_output=True,
                          text=True, check=False)


def header(cls: str, obj: str, loc: str = "") -> str:
    """Standard FoamFile header."""
    loc_line = f'    location    "{loc}";\n' if loc else ""
    return ("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
            f"    class       {cls};\n{loc_line}    object      {obj};\n}}\n\n")


def write(path: Path, text: str) -> None:
    """Write a case file, creating its directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def block_mesh(bell: Bell, fine: bool) -> str:
    """blockMeshDict for the plenum + bell + duct wedge.

    2-D nodes (x, r):  a = axis, b = lip/wall radius, c = far radius.
        a0(XU,0)  a1(0,0)  a2(L,0)  a3(XO,0)
        b0(XU,RL) b1(0,RL) b2(L,R)  b3(XO,R)
        c0(XU,RF) c1(0,RF)
    With an external forebody, two more nodes and a fifth block outside it:
        e1(XO, R_fore_end)  f1(XO, RF)
    Axis nodes are shared by both wedge faces (collapsed hex, standard wedge).
    """
    bell_l, r_lip = bell.length, R_BORE + bell.flare
    f = 1.5 if fine else 1.0
    n_plen, n_bell, n_duct = int(50 * f), int(40 * f), int(50 * f)
    n_r, n_far = int(40 * f), int(40 * f)
    s, c = math.sin(math.radians(WEDGE_DEG)), math.cos(math.radians(WEDGE_DEG))
    nodes2d = {"a0": (X_UP, 0), "a1": (0, 0), "a2": (bell_l, 0),
               "a3": (X_OUT, 0), "b0": (X_UP, r_lip), "b1": (0, r_lip),
               "b2": (bell_l, R_BORE), "b3": (X_OUT, R_BORE),
               "c0": (X_UP, R_FAR), "c1": (0, R_FAR)}
    if bell.fore is not None:
        nodes2d["e1"] = (X_OUT, bell.fore[1])
        nodes2d["f1"] = (X_OUT, R_FAR)
    verts: list[str] = []
    vid: dict[tuple[str, int], int] = {}
    for name, (x, r) in nodes2d.items():
        for side in (-1, 1):
            if r == 0 and side == 1:
                vid[(name, side)] = vid[(name, -1)]
                continue
            vid[(name, side)] = len(verts)
            verts.append(f"({x:.9f} {r * c:.12f} {side * r * s:.12f})")

    def hexv(q: tuple[str, str, str, str]) -> str:
        """Hex vertex list: the quad on the back wedge face, then the front."""
        back = [vid[(n, -1)] for n in q]
        front = [vid[(n, 1)] for n in q]
        return " ".join(map(str, back + front))

    def face(q: tuple[str, ...], side: int) -> str:
        return "(" + " ".join(str(vid[(n, side)]) for n in q) + ")"

    def edge_face(n1: str, n2: str) -> str:
        """Quad face spanning both wedge sides along the 2-D edge n1-n2."""
        return (f"({vid[(n1, -1)]} {vid[(n2, -1)]} "
                f"{vid[(n2, 1)]} {vid[(n1, 1)]})")

    # Radial grading: cluster at the wall (last/first cell = 0.12) in the duct
    # column; cluster at the lip edge in the outer plenum (first/last = 25).
    g_r, g_far, g_plen = 0.12, 25.0, 0.05
    blocks = [
        (("a0", "a1", "b1", "b0"), (n_plen, n_r), f"({g_plen} {g_r} 1)"),
        (("b0", "b1", "c1", "c0"), (n_plen, n_far), f"({g_plen} {g_far} 1)"),
        (("a1", "a2", "b2", "b1"), (n_bell, n_r), f"(1 {g_r} 1)"),
        (("a2", "a3", "b3", "b2"), (n_duct, n_r), f"(3 {g_r} 1)"),
    ]
    if bell.fore is not None:
        blocks.append((("b1", "e1", "f1", "c1"), (int(60 * f), n_far),
                       f"(4 {g_far} 1)"))
    blk = "\n".join(f"    hex ({hexv(q)}) ({nx} {ny} 1) simpleGrading {g}"
                    for q, (nx, ny), g in blocks)

    # Curved bell wall b1 -> b2 on both wedge faces.
    pts = 24
    edges = []
    for side in (-1, 1):
        inner = " ".join(
            f"({x:.9f} {bell_r(x, bell) * c:.12f} "
            f"{side * bell_r(x, bell) * s:.12f})"
            for x in (bell_l * i / pts for i in range(1, pts)))
        edges.append(f"    polyLine {vid[('b1', side)]} {vid[('b2', side)]} "
                     f"({inner})")

    if bell.fore is not None:
        fa, fr = bell.fore
        fb = fr - r_lip

        def r_ext(x: float) -> float:
            if x >= fa:
                return fr
            u = 1.0 - x / fa
            return r_lip + fb * math.sqrt(max(0.0, 1.0 - u * u))
        xs = [fa * (i / pts) ** 2 for i in range(1, pts + 1)] + [
            fa + (X_OUT - fa) * i / 8 for i in range(1, 8)]
        for side in (-1, 1):
            inner = " ".join(f"({x:.9f} {r_ext(x) * c:.12f} "
                             f"{side * r_ext(x) * s:.12f})" for x in xs)
            edges.append(f"    polyLine {vid[('b1', side)]} "
                         f"{vid[('e1', side)]} ({inner})")
        lip_patch = (f"foreWall {{ type wall;  faces ( "
                     f"{edge_face('b1', 'e1')} ); }}")
        far_extra = f" {edge_face('c1', 'f1')} {edge_face('e1', 'f1')}"
    else:
        lip_patch = (f"lipFace  {{ type wall;  faces ( "
                     f"{edge_face('b1', 'c1')} ); }}")
        far_extra = ""
    wedge_back = " ".join(face(q, -1) for q, _, _ in blocks)
    wedge_front = " ".join(face(q, 1) for q, _, _ in blocks)
    return header("dictionary", "blockMeshDict") + f"""scale 1;

vertices
(
    {chr(10).join('    ' + v for v in verts).strip()}
);

blocks
(
{blk}
);

edges
(
{chr(10).join(edges)}
);

boundary
(
    farfield {{ type patch; faces ( {edge_face('a0', 'b0')}
        {edge_face('b0', 'c0')} {edge_face('c0', 'c1')}{far_extra} ); }}
    {lip_patch}
    bellWall {{ type wall;  faces ( {edge_face('b1', 'b2')} ); }}
    ductWall {{ type wall;  faces ( {edge_face('b2', 'b3')} ); }}
    outlet   {{ type patch; faces ( {edge_face('a3', 'b3')} ); }}
    axis     {{ type empty; faces ( {edge_face('a0', 'a1')}
        {edge_face('a1', 'a2')} {edge_face('a2', 'a3')} ); }}
    back     {{ type wedge; faces ( {wedge_back} ); }}
    front    {{ type wedge; faces ( {wedge_front} ); }}
);
"""


def write_case(case: Path, bell: Bell, fine: bool) -> float:
    """Write every dictionary for one variant; return rotor LE station m."""
    x_le = rotor_entry(bell)
    write(case / "system/blockMeshDict", block_mesh(bell, fine))
    k0, w0 = 1.5 * (0.01 * V_BORE) ** 2, 200.0   # 1 % intensity, ambient omega
    walls = "lipFace|foreWall|bellWall|ductWall"
    fields = {
        "U": ("volVectorField", "[0 1 -1 0 0 0 0]", "uniform (0 0 0)", {
            "farfield": "type pressureInletOutletVelocity; value uniform (0 0 0);",
            f"({walls})": "type noSlip;",
            "outlet": f"type fixedValue; value uniform ({V_BORE:.4f} 0 0);"}),
        "p": ("volScalarField", "[0 2 -2 0 0 0 0]", "uniform 0", {
            "farfield": "type totalPressure; p0 uniform 0; value uniform 0;",
            f"({walls})": "type zeroGradient;",
            "outlet": "type zeroGradient;"}),
        "k": ("volScalarField", "[0 2 -2 0 0 0 0]", f"uniform {k0:.5f}", {
            "farfield": f"type inletOutlet; inletValue uniform {k0:.5f}; "
                        f"value uniform {k0:.5f};",
            f"({walls})": f"type kqRWallFunction; value uniform {k0:.5f};",
            "outlet": "type zeroGradient;"}),
        "omega": ("volScalarField", "[0 0 -1 0 0 0 0]", f"uniform {w0}", {
            "farfield": f"type inletOutlet; inletValue uniform {w0}; "
                        f"value uniform {w0};",
            f"({walls})": f"type omegaWallFunction; value uniform {w0};",
            "outlet": "type zeroGradient;"}),
        "nut": ("volScalarField", "[0 2 -1 0 0 0 0]", "uniform 0", {
            "farfield": "type calculated; value uniform 0;",
            f"({walls})": "type nutkWallFunction; value uniform 0;",
            "outlet": "type calculated; value uniform 0;"}),
    }
    for name, (cls, dims, internal, bcs) in fields.items():
        body = "\n".join(f'    "{p}" {{ {v} }}' for p, v in bcs.items())
        write(case / "0" / name, header(cls, name, "0")
              + f"dimensions {dims};\ninternalField {internal};\n"
              + f"boundaryField\n{{\n{body}\n    \"(back|front)\" "
              + "{ type wedge; }\n    axis { type empty; }\n}\n")

    write(case / "constant/transportProperties",
          header("dictionary", "transportProperties")
          + f"transportModel Newtonian;\nnu [0 2 -1 0 0 0 0] {NU};\n")
    write(case / "constant/turbulenceProperties",
          header("dictionary", "turbulenceProperties")
          + "simulationType RAS;\nRAS { RASModel kOmegaSST; turbulence on; "
            "printCoeffs off; }\n")

    # No function objects: see post_process() for why.
    write(case / "system/controlDict", header("dictionary", "controlDict") + """
application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         3000;
deltaT          1;
writeControl    timeStep;
writeInterval   3000;
purgeWrite      0;
writeFormat     ascii;
writePrecision  8;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;

""")
    write(case / "system/fvSchemes", header("dictionary", "fvSchemes") + """
ddtSchemes { default steadyState; }
gradSchemes { default Gauss linear; grad(U) cellLimited Gauss linear 1; }
divSchemes
{
    default none;
    div(phi,U) bounded Gauss linearUpwind grad(U);
    div(phi,k) bounded Gauss upwind;
    div(phi,omega) bounded Gauss upwind;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes { default corrected; }
wallDist { method meshWave; }
""")
    write(case / "system/fvSolution", header("dictionary", "fvSolution") + """
solvers
{
    p { solver GAMG; tolerance 1e-7; relTol 0.01; smoother GaussSeidel; }
    "(U|k|omega)" { solver smoothSolver; smoother GaussSeidel;
        tolerance 1e-8; relTol 0.1; }
}
SIMPLE
{
    nNonOrthogonalCorrectors 2; consistent yes;
    residualControl { p 1e-5; U 1e-6; "(k|omega)" 1e-6; }
}
relaxationFactors { equations { U 0.7; ".*" 0.7; } fields { p 0.5; } }
""")
    return x_le


def last_time(case: Path) -> Path | None:
    """Latest numeric time directory other than 0."""
    times = [d for d in case.iterdir() if d.is_dir()
             and d.name.replace(".", "", 1).isdigit() and d.name != "0"]
    return max(times, key=lambda d: float(d.name)) if times else None


def _foam_list(path: Path) -> list[str]:
    """Body lines of an ASCII OpenFOAM list file (after the count line)."""
    lines = path.read_text(encoding="utf-8").splitlines()
    i = next(n for n, ln in enumerate(lines) if ln.strip() == "(")
    j = len(lines) - 1 - next(n for n, ln in enumerate(reversed(lines))
                              if ln.strip() == ")")
    return [ln.strip() for ln in lines[i + 1:j] if ln.strip()]


def _vec(text: str) -> tuple[float, ...]:
    return tuple(float(v) for v in text.strip("()").split())


def _internal_field(path: Path) -> list[tuple[float, ...] | float]:
    """internalField values (nonuniform list) of an ASCII field file."""
    text = path.read_text(encoding="utf-8")
    i = text.index("internalField")
    j = text.index("(", text.index("\n", i))
    k = text.index("\n)", j)
    body = [ln.strip() for ln in text[j + 1:k].splitlines() if ln.strip()]
    return [_vec(v) if v.startswith("(") else float(v) for v in body]


def post_process(case: Path, t: Path, x_le: float) -> tuple[dict, list]:
    """Wall-reversal fractions and the rotor-LE profile, from raw fields.

    The function objects (wallShearStress, sets) are NOT used: every function
    object in the packaged OpenFOAM v1912 on this host aborts with
    "error in IOstream sha1", a build defect, so the same quantities are
    computed here from the ASCII polyMesh and fields.

    Separation test: the owner cell of each wall face; its velocity component
    along the wall tangent (in the meridional plane, oriented downstream)
    negative => near-wall flow runs upstream.  Bell/duct walls flow +x; the
    flanged lip face is swept radially inward, so its tangent is -y.
    """
    mesh = case / "constant/polyMesh"
    pts = [_vec(v) for v in _foam_list(mesh / "points")]
    faces = [[int(i) for i in v[v.index("(") + 1:-1].split()]
             for v in _foam_list(mesh / "faces")]
    owner = [int(v) for v in _foam_list(mesh / "owner")]
    neigh = [int(v) for v in _foam_list(mesh / "neighbour")]
    n_cells = max(owner) + 1
    vel = _internal_field(t / "U")
    prs = _internal_field(t / "p")

    # Cell x-extent and mean radius from their faces' points.
    xlo = [1e9] * n_cells
    xhi = [-1e9] * n_cells
    rsum = [0.0] * n_cells
    rcnt = [0] * n_cells
    for fi, f in enumerate(faces):
        cells = [owner[fi]] + ([neigh[fi]] if fi < len(neigh) else [])
        for c in cells:
            for pi in f:
                x, y, z = pts[pi]
                xlo[c] = min(xlo[c], x)
                xhi[c] = max(xhi[c], x)
                rsum[c] += math.hypot(y, z)
                rcnt[c] += 1

    # Boundary patches: name -> (startFace, nFaces).
    btext = (mesh / "boundary").read_text(encoding="utf-8")
    walls: dict[str, tuple[float, float]] = {}
    for patch, tang in (("lipFace", (0.0, -1.0)), ("foreWall", (-1.0, 0.0)),
                        ("bellWall", None), ("ductWall", None)):
        if f"    {patch}\n" not in btext:
            continue
        blk = btext[btext.index(f"    {patch}\n"):]
        n = int(blk.split("nFaces")[1].split(";")[0])
        start = int(blk.split("startFace")[1].split(";")[0])
        rev = 0
        for fi in range(start, start + n):
            u = vel[owner[fi]]
            if tang is None:
                # Downstream tangent from the face's own x-extent: the bell
                # wall's slope is <= 17 deg, so +x orientation is unambiguous.
                fx = [pts[p][0] for p in faces[fi]]
                fr = [math.hypot(pts[p][1], pts[p][2]) for p in faces[fi]]
                i0, i1 = fx.index(min(fx)), fx.index(max(fx))
                dx, dr = fx[i1] - fx[i0], fr[i1] - fr[i0]
                norm = math.hypot(dx, dr) or 1.0
                ut = (u[0] * dx + u[1] * dr) / norm
            else:
                ut = u[0] * tang[0] + u[1] * tang[1]
            rev += ut < 0
        walls[patch] = (rev / n if n else 0.0, float(n))

    profile = []
    for c in range(n_cells):
        # Duct cells only: with an external forebody the outside block spans
        # the rotor station too, and its far-field air is not rotor inflow.
        if xlo[c] <= x_le <= xhi[c] and rsum[c] / rcnt[c] < R_BORE + FLARE:
            u = vel[c]
            r = rsum[c] / rcnt[c]
            profile.append((r, u[0], u[1],
                            prs[c] + 0.5 * (u[0] ** 2 + u[1] ** 2)))
    return walls, sorted(profile)


def residuals(log: str) -> dict[str, float]:
    """Last initial residual of each solved field in a simpleFoam log."""
    out: dict[str, float] = {}
    for ln in log.splitlines():
        if "Solving for" in ln and "Initial residual" in ln:
            field = ln.split("Solving for")[1].split(",")[0].strip()
            if field == "Uz":
                # Out-of-plane wedge component: ~0 everywhere, so its
                # normalised residual is meaningless and never decays.
                continue
            out[field] = float(ln.split("Initial residual =")[1].split(",")[0])
    return out


def run_case(case: Path, bell: Bell, fine: bool) -> dict:
    """Write, mesh, check, solve and sample one bell variant."""
    if case.exists():
        shutil.rmtree(case)
    x_le = write_case(case, bell, fine)
    mesh = foam("blockMesh", case)
    check = foam("checkMesh", case)
    solve = foam("simpleFoam", case)
    (case / "log.blockMesh").write_text(mesh.stdout + mesh.stderr)
    (case / "log.checkMesh").write_text(check.stdout + check.stderr)
    (case / "log.simpleFoam").write_text(solve.stdout + solve.stderr)
    t = last_time(case)
    walls, profile = post_process(case, t, x_le) if t else ({}, [])
    res = residuals(solve.stdout)
    return {"bell": bell, "x_le_mm": x_le * 1000.0,
            "mesh_ok": "Mesh OK" in check.stdout,
            # openfoam-cfd skill: residuals < 1e-4 for engineering accuracy
            "max_residual": max(res.values()) if res else float("nan"),
            "converged": bool(res) and max(res.values()) < 1e-4,
            "iterations": t.name if t else None,
            "walls": walls, "profile": profile}


def summarise(res: dict) -> None:
    """Print one variant's screening numbers, imperial-primary."""
    prof = res["profile"]
    b = res["bell"]
    print(f"\n{b.name}: {b.kind} lip, L {b.length * 1e3:.1f} mm, flare "
          f"{b.flare * 1e3:.2f} mm; rotor LE at Z {res['x_le_mm']:.2f} mm\n"
          f"  mesh {'OK' if res['mesh_ok'] else 'FAILED'}, "
          f"{'converged' if res['converged'] else 'NOT converged'} "
          f"(max final residual {res['max_residual']:.1e}, "
          f"{res['iterations']} it)")
    for patch, (frac, n) in res["walls"].items():
        print(f"  {patch:<9} reversed near-wall flow on {100 * frac:5.1f} % "
              f"of {n:.0f} wall faces")
    if not prof:
        print("  no rotor-LE profile sampled")
        return
    r_max = prof[-1][0]
    p0_core = sum(p[3] for p in prof[:5]) / 5
    for frac in (0.5, 0.8, 0.9, 0.95, 0.98):
        r, ux, ur, p0 = min(prof, key=lambda p, f=frac: abs(p[0] - f * r_max))
        ang = math.degrees(math.atan2(ur, ux))
        loss = (p0_core - p0) / (0.5 * V_BORE ** 2)
        print(f"  r/R {r / r_max:4.2f}: Ux {ux:6.1f} m/s ({ux / 0.5144:5.0f} kt)"
              f"  flow angle {ang:+5.1f} deg  total-pressure deficit "
              f"{100 * loss:5.1f} % of q_bore")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--workdir", required=True, type=Path,
                    help="directory for the cases (outside the repo)")
    ap.add_argument("--fine", action="store_true",
                    help="1.5x cells in each direction (mesh-sensitivity run)")
    ap.add_argument("--only", nargs="*", default=None,
                    help="variant names to run (default: all)")
    args = ap.parse_args(argv)
    print(f"Hover bore velocity {V_BORE:.1f} m/s ({V_BORE / 0.5144:.0f} kt) "
          f"for {THRUST_N} N ({THRUST_N / 4.448:.2f} lbf) per fan")
    ok = True
    for bell in (b for b in VARIANTS if not args.only or b.name in args.only):
        tag = bell.name + ("_fine" if args.fine else "")
        res = run_case(args.workdir / tag, bell, args.fine)
        summarise(res)
        ok = ok and res["mesh_ok"] and res["converged"]
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
