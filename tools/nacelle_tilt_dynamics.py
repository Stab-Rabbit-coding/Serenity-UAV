#!/usr/bin/env python3
"""
nacelle_tilt_dynamics.py — tilt-axis inertia, gyroscopic moment and drive /
trunnion load check, 50 mm vs 64 mm nacelle.

WHY
---
Owner direction 2026-10-03: "recalculate the moments of inertia for the
larger nacelles, since it will take more force to accelerate them around
their cg pivot ... the trunnion, bearings, gears, driveshaft and tilt servos
will have to take the load."

The only prior figure, I = 7.189e-4 kg.m^2 (docs/TILT_SPAR_ANALYSIS.md
§2.1.2), is a POINT-MASS sum on pre-Rev-T4 masses: it omits every part's own
inertia and the off-axis ESCs.  This tool builds a rigid-body inertia about
the tilt axis (spanwise X through the pivot on the duct axis) for BOTH pods
the same way, so the 64 / 50 ratio is apples to apples.

LOADS CHECKED (per nacelle)
---------------------------
  inertia    T = I_tilt x alpha, at three profiles:
               vectoring  — TILT-CTL-05: 120 deg/s peak at 4 Hz (sinusoid),
                            alpha = omega_pk x 2 pi f
               drive envelope — the BUILT drive's no-load maximum 144 deg/s
                            (docs/TILT_ACTUATOR_SELECTION.md Opt 4) with the
                            vectoring alpha, both at once (conservative)
               legacy     — 145 deg / 0.5 s (TILT_SPAR_ANALYSIS §2.1.2); NOT
                            achievable by the built drive, comparison only
  gyroscopic M = n_rotor x I_spin x Omega x omega_tilt about the axis normal
             to both the duct and the tilt axis.  Both rotors in a nacelle
             co-rotate (one SWIRL_DIR per nacelle, stator between stages), so
             their spin momenta ADD.  This moment does NOT load the tilt drive
             (it is normal to the tilt axis); it loads the TRUNNION BEARINGS
             and the spar stub as a couple across the bearing span — the same
             axis as the thrust moment, so the two add.
  bearings   per-bearing couple force = (M_thrust + M_gyro) / span.
  tip gear   50T m0.8 ring, 5 mm face (nacelle_trunnion.scad), printed;
             Lewis bending capacity sigma b m Y, sigma = 54 MPa flexural
             [REF-MAT-002], Y = 0.40 ASSUMED (same as
             tools/tilt_actuator_options.py); required FOS >= 4.
  shaft      torsion in the Ø4 drive shaft, tau = 16 T / (pi d^3), T =
             T_nacelle / (3.571 x 0.95).  The shaft material grade is not
             recorded, so the stress is REPORTED, not passed/failed.
  motor      the built drive's 1.81 N.m stall-limited torque at the nacelle.

INPUTS — ASSUMED values are labelled; every other value is cited or measured
------------------------------------------------------------------------------
  pod meshes       rendered nacelle-local STLs (--pod50, --pod64), RHO_PRINT
  component rows   tools/nacelle_mass_cg.py (50 mm), tools/nacelle_mass_cg_64.py
  rotor spin data  ASSUMED: 64 mm rotor 20 g, hub r 10 mm; 50 mm rotor 10 g,
                   hub r 8 mm; tip r = bore - 0.4 mm; I_spin = m(ri^2+ro^2)/2;
                   loaded rpm = 0.85 x KV x 22.2 V (KV 2400 [REF-EDF-003];
                   3200 [REF-EDF-001]).  WEIGH and tach a rotor (FIT-02).
  thrust           64 mm: 2 x 20.9 N x 0.90 tandem factor [REF-EDF-003, plan
                   screen]; 50 mm: 21.9 N (WING_ATTACH_INTERFACE §4.3a); x1.5
                   ultimate.  Thrust arm = duct axis to bearing-pair centre.
  bearing rating   6704ZZ static rating ~907 N, back-computed from
                   WING_ATTACH_INTERFACE §4.3a ("254 N — 28 % of a 6704's
                   static rating").  NOT catalogued in REFERENCES.md — REQUIRES
                   VERIFICATION against a manufacturer datasheet.
  aero moment      UNQUANTIFIED (TILT-CTL-06), as before — larger frontal area
                   makes it larger; the OpenFOAM tool can now supply it.

Usage:
    /usr/bin/python3 tools/nacelle_tilt_dynamics.py --pod50 STL --pod64 STL

Exit 0 = every pass/fail check passes for the 64 mm nacelle.

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CEH (GitHub Stab-Rabbit-coding) —
requirement and load-path scope.  Tool and analysis by Claude (Claude Opus
5.5, Anthropic) under the author's direction, per AGENTS.md AI attribution.
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nacelle_mass_cg as m50  # sibling tool; path set above
import nacelle_mass_cg_64 as m64

RHO = m50.RHO_PRINT          # g/mm^3 bulk printed density
LBF_IN_PER_NM = 8.8507       # lbf.in per N.m
LBF_PER_N = 0.224809

# ── Drive train (docs/TILT_ACTUATOR_SELECTION.md Rev T5e, nacelle_trunnion) ──
T_DRIVE_LIMIT = 1.81         # N.m at the nacelle, motor stall ~ tooth limit
TIP_RATIO, TIP_ETA = 50.0 / 14.0, 0.95
RING_M, RING_Z, RING_FACE = 0.8, 50, 5.0      # module, teeth, face width mm
SIGMA_FLEX, LEWIS_Y, GEAR_FOS = 54.0, 0.40, 4.0
SHAFT_D = 4.0                # mm
BRG_SPAN = 4.0               # mm, 2 x 6704ZZ centres (WING_ATTACH §4.3a)
BRG_C0 = 254.0 / 0.28        # N, REQUIRES VERIFICATION (module docstring)
ULT = 1.5                    # ultimate factor (docs/structural_analysis.md)
LEGACY_X6 = 6.0              # TILT_SPAR_ANALYSIS's 4 g x 1.5 multiplier


@dataclass
class Body:
    """A component: mass g, axial CG z mm, off-axis y mm, and a shape."""

    name: str
    m: float
    z: float
    y: float = 0.0
    shape: str = "point"     # point | tube | disc | tilt_ring
    ri: float = 0.0          # mm
    ro: float = 0.0
    length: float = 0.0

    def i_own(self) -> float:
        """Inertia about an X axis through its own CG, g.mm^2."""
        if self.shape == "tube":       # axis along the duct (z)
            return self.m * (3 * (self.ri ** 2 + self.ro ** 2)
                             + self.length ** 2) / 12.0
        if self.shape == "disc":       # thin annular disc normal to z
            return self.m * (self.ri ** 2 + self.ro ** 2) / 4.0 \
                + self.m * self.length ** 2 / 12.0
        if self.shape == "tilt_ring":  # ring whose own axis IS the X axis
            return self.m * (self.ri ** 2 + self.ro ** 2) / 2.0
        return 0.0

    def i_about(self, pivot: float) -> float:
        """Parallel-axis inertia about the tilt axis, g.mm^2."""
        return self.i_own() + self.m * ((self.z - pivot) ** 2 + self.y ** 2)


def pod_body(stl: Path, name: str) -> Body:
    """The measured pod: its own Ixx about its CG plus its CG offset."""
    mesh = m50.trimesh.load_mesh(stl, force="mesh")
    cg = mesh.center_mass
    ixx = float(mesh.moment_inertia[0][0]) * RHO      # g.mm^2 about the CG
    mass = float(mesh.volume * RHO)
    b = Body(name, mass, float(cg[2]), float(cg[1]))
    b.i_own = lambda ixx=ixx: ixx  # type: ignore[method-assign]
    return b


def bodies_50(pod: Path) -> tuple[list[Body], float]:
    """50 mm nacelle, from tools/nacelle_mass_cg.py rows (Rev T4 as built)."""
    esc_y = 32.0 * math.sin(math.radians(68.0 + 15.0))
    bs = [pod_body(pod, "pod 50 mm (measured)"),
          Body("stator sleeve", 31.0, 106.3, shape="tube", ri=25, ro=27.5,
               length=32.5),
          Body("aft spider sleeve", 24.7, 144.9, shape="tube", ri=25, ro=27.5,
               length=43.8)]
    # EDF combo 75 g = motor 50 g + rotor 25 g, ASSUMED split (unpublished)
    for z in (59.4, 150.6):
        bs += [Body("2627 motor", 50.0, z, shape="tube", ri=0, ro=13.0,
                    length=27.0),
               Body("50 mm rotor + shroud share", 25.0, z - 20.0,
                    shape="disc", ri=8.0, ro=24.6, length=8.0)]
    bs += [Body("ESC", 25.0, 95.0, esc_y), Body("ESC", 25.0, 95.0, -esc_y),
           Body("ESC covers", 6.99, 95.0, 34.0),
           Body("nozzle throat+housing", 21.4, 174.8, shape="tube", ri=28,
                ro=35.6, length=17.0),
           Body("unison ring", 6.7, 169.9, shape="tube", ri=30, ro=34,
                length=6.0),
           Body("8 x flaps 40 mm", 21.1, 198.2, shape="tube", ri=22, ro=30,
                length=40.0),
           Body("pushrod", 3.6, 140.8, 30.0)]
    bs += [Body(n, mm, z) for n, mm, z, _ in m50.HARNESS]
    pivot = 107.5
    bs += [Body(n, mm, pivot, shape="tilt_ring", ri=10.0, ro=20.6)
           for n, mm, _ in m50.ON_AXIS]
    return bs, pivot


def bodies_64(pod: Path) -> tuple[list[Body], float]:
    """64 mm nacelle, from tools/nacelle_mass_cg_64.py stations and rows."""
    k = m64.K
    esc_y = 39.2 * math.sin(math.radians(68.0 + 15.0))
    r1, mo1, r2, mo2 = m64.ROTOR1, m64.MOTOR1, m64.ROTOR2, m64.MOTOR2
    noz = m64.NOZ_Z
    bs = [pod_body(pod, "pod 64 mm (measured)"),
          Body("stator-1 sleeve", 75.0 * k / 1.28, m64.mid(m64.STATOR_SLV),
               shape="tube", ri=32, ro=34.5,
               length=m64.STATOR_SLV[1] - m64.STATOR_SLV[0]),
          Body("aft sleeve", 54.5 * k / 1.28, m64.mid(m64.AFT_SLV),
               shape="tube", ri=32, ro=34.5,
               length=m64.AFT_SLV[1] - m64.AFT_SLV[0])]
    for mo in (mo1, mo2):
        bs.append(Body("QF2822 motor", 135.0, m64.mid(mo), shape="tube",
                       ri=0, ro=13.9, length=58.0))
    for r in (r1, r2):
        bs.append(Body("64 mm rotor", 20.0, m64.mid(r), shape="disc",
                       ri=10.0, ro=31.6, length=10.7))
    bs += [Body("ESC 70 A", 42.0, m64.ESC_BAY_CG, esc_y),
           Body("ESC 70 A", 42.0, m64.ESC_BAY_CG, -esc_y),
           Body("ESC covers", 4 * 6.99 / 2 * k, m64.ESC_BAY_CG, 42.0),
           Body("nozzle throat+housing", 21.4 * k, noz + 8.55, shape="tube",
                ri=34, ro=43.0, length=17.0),
           Body("unison ring", 6.7 * k, noz + 3.65, shape="tube", ri=36,
                ro=41, length=6.0),
           Body("8 x flaps 40 mm", 21.1 * k, noz + 31.95, shape="tube",
                ri=27, ro=36, length=40.0),
           Body("nozzle servo drive", 8.0, noz - 16.25, 38.0)]
    feed = 4 * (0.060 + (m64.PIVOT_Z_SET - m64.DISC_BAY_Z - 29.5) / 1000) * 40
    bs += [Body("4 x 10 AWG feed", feed,
                0.5 * (m64.PIVOT_Z_SET + m64.DISC_BAY_Z), 30.0),
           Body("6 x 14 AWG phase", m50.HARNESS[1][1] * 2.08 / 1.31,
                0.5 * (m64.ESC_BAY_CG + 0.5 * (m64.mid(mo1) + m64.mid(mo2))),
                30.0),
           Body(*m50.HARNESS[2][:3]), Body(*m50.HARNESS[3][:3])]
    pivot = m64.PIVOT_Z_SET
    bs += [Body(n, mm, pivot, shape="tilt_ring", ri=10.0, ro=20.6)
           for n, mm, _ in m50.ON_AXIS]
    return bs, pivot


def spin(m_g: float, ri: float, ro: float, kv: float) -> float:
    """Spin angular momentum of one rotor, N.m.s (ASSUMED inputs, docstring)."""
    i_spin = m_g / 1000.0 * ((ri / 1000.0) ** 2 + (ro / 1000.0) ** 2) / 2.0
    omega = 0.85 * kv * 22.2 * 2 * math.pi / 60.0
    return i_spin * omega


def profiles() -> dict[str, tuple[float, float]]:
    """(peak tilt rate rad/s, peak angular acceleration rad/s^2)."""
    w_v = math.radians(120.0)
    a_v = w_v * 2 * math.pi * 4.0
    vect = (w_v, a_v)
    # Envelope of the BUILT drive: its no-load maximum rate (144 deg/s,
    # TILT_ACTUATOR_SELECTION Opt 4) with the TILT-CTL-05 acceleration, both
    # peaks applied together (conservative).  A triangular 145 deg / 1.04 s
    # profile would demand 279 deg/s, which this drive cannot produce.
    drive = (math.radians(144.0), a_v)
    th, t = math.radians(145.0), 0.5
    legacy = (2 * th / t, th / (t / 2) ** 2)
    return {"vectoring 120 deg/s @ 4 Hz": vect,
            "drive envelope 144 deg/s + vectoring alpha": drive,
            "legacy 145 deg / 0.5 s (not achievable)": legacy}


def analyse(name: str, bodies: list[Body], pivot: float, thrust_n: float,
            arm_mm: float, h_spin: float) -> dict:
    """All loads for one nacelle."""
    i_tilt = sum(b.i_about(pivot) for b in bodies) * 1e-9     # kg.m^2
    mass = sum(b.m for b in bodies)
    ring_cap = SIGMA_FLEX * RING_FACE * RING_M * LEWIS_Y \
        * (RING_Z * RING_M / 2.0) / 1000.0                     # N.m, no FOS
    m_thrust = thrust_n * ULT * arm_mm / 1000.0                # N.m ultimate
    rows = []
    for prof, (w, a) in profiles().items():
        t_in = i_tilt * a
        m_gyro = h_spin * w * ULT
        f_brg = (m_thrust + m_gyro) / (BRG_SPAN / 1000.0)
        t_shaft = t_in * ULT / (TIP_RATIO * TIP_ETA)
        tau = 16 * t_shaft * 1000.0 / (math.pi * SHAFT_D ** 3)  # MPa
        rows.append({"profile": prof, "omega": w, "alpha": a,
                     "T_inertia": t_in, "T_ult": t_in * ULT,
                     "drive_margin": T_DRIVE_LIMIT / (t_in * ULT),
                     "gear_fos": ring_cap / t_in,
                     "M_gyro_ult": m_gyro, "F_brg": f_brg,
                     "brg_frac": f_brg / BRG_C0, "tau_shaft": tau})
    return {"name": name, "I": i_tilt, "mass": mass, "pivot": pivot,
            "h_spin": h_spin, "M_thrust_ult": m_thrust, "ring_cap": ring_cap,
            "rows": rows}


def report(r: dict) -> None:
    print(f"\n{r['name']}: rotating mass {r['mass'] / 453.592:.3f} lbm "
          f"({r['mass']:.0f} g), pivot {r['pivot']:.1f} mm")
    print(f"  I_tilt = {r['I']:.3e} kg.m^2 ({r['I'] * 3417.17:.2f} lbm.in^2)"
          f"   rotor spin momentum (both) {r['h_spin']:.4f} N.m.s")
    print(f"  thrust moment at the trunnion, ultimate {r['M_thrust_ult']:.2f}"
          f" N.m ({r['M_thrust_ult'] * LBF_IN_PER_NM:.1f} lbf.in)")
    print(f"  tip ring Lewis capacity {r['ring_cap']:.3f} N.m (no FOS)")
    for x in r["rows"]:
        print(f"  [{x['profile']}]  peak {math.degrees(x['omega']):.0f} deg/s,"
              f" {x['alpha']:.1f} rad/s^2")
        print(f"     inertia torque {x['T_inertia']:.4f} N.m limit, "
              f"{x['T_ult']:.4f} ult ({x['T_ult'] * LBF_IN_PER_NM:.3f} lbf.in)"
              f" -> drive margin {x['drive_margin']:.1f}x, tip-gear FOS "
              f"{x['gear_fos']:.1f}")
        print(f"     gyro moment (ult) {x['M_gyro_ult']:.3f} N.m -> per-bearing"
              f" {x['F_brg']:.0f} N ({x['F_brg'] * LBF_PER_N:.0f} lbf) = "
              f"{100 * x['brg_frac']:.0f} % of C0 (VERIFY); shaft tau "
              f"{x['tau_shaft']:.1f} MPa")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--pod50", type=Path, required=True)
    ap.add_argument("--pod64", type=Path, required=True)
    args = ap.parse_args(argv)

    b50, p50 = bodies_50(args.pod50)
    b64, p64 = bodies_64(args.pod64)
    h50 = 2 * spin(10.0, 8.0, 24.6, 3200.0)
    h64 = 2 * spin(20.0, 10.0, 31.6, 2400.0)
    arm50 = 28.2 + BRG_SPAN          # duct axis -> bearing-pair centre
    arm64 = m64.K * 34.0 - 34.0 + 28.2 + BRG_SPAN
    r50 = analyse("50 mm (Rev T4)", b50, p50, 21.9, arm50, h50)
    r64 = analyse("64 mm (adopted)", b64, p64, 2 * 20.9 * 0.90, arm64, h64)
    for r in (r50, r64):
        report(r)
    print(f"\n64 / 50: I_tilt x{r64['I'] / r50['I']:.2f}, spin momentum "
          f"x{r64['h_spin'] / r50['h_spin']:.2f}, thrust moment "
          f"x{r64['M_thrust_ult'] / r50['M_thrust_ult']:.2f}")

    ok = True
    for x in r64["rows"]:
        if x["profile"].startswith("legacy"):
            continue
        ok &= x["drive_margin"] >= 1.0 and x["gear_fos"] >= GEAR_FOS \
            and x["brg_frac"] <= 1.0
    print("\nRESULT (64 mm, achievable profiles):", "PASS" if ok else "FAIL",
          "- bearing C0 and rotor spin data REQUIRE VERIFICATION")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
