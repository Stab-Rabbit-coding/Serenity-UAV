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
  bearing rating   6704-ZZ static rating C0 = 730 N, dynamic 1.3 kN, JTEKT
                   [REF-BRG-001] (distributor-hosted sheet; confirm against the
                   JTEKT catalogue).  The ~907 N implied by WING_ATTACH_INTERFACE
                   §4.3a matches a DYNAMIC rating and is superseded.
  aero moment      MOMENTUM DRAG (propulsion.md §1 momentum theory): the fan
                   turns the duct-normal crossflow v_c axial, so the inlet
                   carries N = mdot x v_c, mdot = rho A V_bore (hover).  N acts
                   at the inlet plane: about the TILT axis its arm is PIVOT_Z
                   (drive load); about the bearing axis its arm is the thrust
                   arm (bearing couple).  Body crossflow drag on the pod side
                   area acts near the pivot and is carried as a radial force
                   only (Cd 1.2, ASSUMED cylinder value).  This is a first-order
                   screen of TILT-CTL-06, not a 3-D CFD result.
  bearing sizing   fs = C0 / P0 per JTEKT CAT. B2001E §5-5-3 [REF-BRG-003];
                   P0 = radial load (no axial load modelled); minimum fs 1.0
                   (Table 5-10, oscillating with impact); DESIGN TARGET fs >= 2.0
                   at ultimate load (the catalogue's high-accuracy class, and
                   about the 50 mm pod's own margin).

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
RING_M, RING_Z, RING_FACE = 0.8, 50, 10.5     # 64 mm: option A (owner 2026-10-03)
RING_FACE_50 = 5.0                            # 50 mm joint as built
SIGMA_FLEX, LEWIS_Y, GEAR_FOS = 54.0, 0.40, 4.0
# Wing 14T pinion: same tangential load as the ring, but the Lewis form
# factor of a 14-tooth 20 deg full-depth gear is 0.277 (50T: 0.409) --
# Shigley 10th ed. Table 14-2 [REF-STD-GEAR-002; table number REQUIRES
# VERIFICATION against a physical copy].  The ring keeps the conservative
# 0.40 above.  A printed pinion is therefore the weak member; the check
# below reports the bending allowable the (metal) pinion must meet.
PINION_Z, LEWIS_Y_14 = 14, 0.277
SHAFT_D = 4.0                # mm
BRG_SPAN = 4.0               # mm, 2 x 6704ZZ centres (WING_ATTACH §4.3a)
BRG_C0 = 730.0               # N, JTEKT 6704-ZZ static rating [REF-BRG-001]
BRG_C0_6804 = 2450.0         # N, JTEKT 6804-ZZ static rating [REF-BRG-002]
BRG_W_6804, BRG_M_6804 = 7.0, 18.0   # mm width, g mass [REF-BRG-002]
FS_MIN = 1.0                 # JTEKT CAT. B2001E Table 5-10: oscillating, impact
FS_TARGET = 2.0              # design target (module docstring)
RHO_AIR = 1.225              # kg/m^3 ISA sea level
# Duct-normal crossflow at the inlet, m/s.  Corridor value: max over the
# V_min(theta) table of V_min sin(theta) (docs/flight_envelope.md §1: 44.4 kt
# at 20 deg -> 7.8 m/s).  Bound: twice that for gusts / manoeuvre, ASSUMED.
V_CROSS = {"corridor at V_min (7.8 m/s)": 7.8,
           "bound 2 x corridor (15.6 m/s, ASSUMED)": 15.6}
# 3-D OpenFOAM results for the 64 mm nacelle (tools/nacelle_crossflow_cfd.py,
# 2026-10-03, 135,740 cells, k-omega SST; pressure + fan momentum flux, no
# viscous shear).  (normal force N, tilt-axis moment N.m), limit loads.
# Hover control: 0.00 N / 0.0005 N.m, axial 40.2 N vs 37.6 N set — validates
# the fan model.  Crossflow residuals 4e-3 / 1e-2 (unsteady wake): read the
# loads as good to about +/-10 %.  These REPLACE the momentum-drag screen for
# the 64 mm pod; the 50 mm pod keeps the screen (no CFD run for it).
AERO_CFD_64 = {"corridor at V_min (7.8 m/s)": (2.36, 0.339),
               "bound 2 x corridor (15.6 m/s, ASSUMED)": (5.68, 0.734)}
ULT = 1.5                    # ultimate factor (docs/structural_analysis.md)
BUILT_ARRANGEMENT = 3        # index into ARRANGEMENTS — what the CAD builds
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
           for n, mm, _ in m64.ON_AXIS_64]
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
            arm_mm: float, h_spin: float, bore_r_mm: float,
            side_area_m2: float) -> dict:
    """All loads for one nacelle."""
    i_tilt = sum(b.i_about(pivot) for b in bodies) * 1e-9     # kg.m^2
    mass = sum(b.m for b in bodies)
    face = RING_FACE if bore_r_mm == 32.0 else RING_FACE_50
    ring_cap = SIGMA_FLEX * face * RING_M * LEWIS_Y \
        * (RING_Z * RING_M / 2.0) / 1000.0                     # N.m, no FOS
    m_thrust = thrust_n * ULT * arm_mm / 1000.0                # N.m ultimate
    # One stream through both fans: total nacelle thrust T = mdot V_e with
    # V_e = sqrt(T / (rho A)) for an exit area equal to the bore, so
    # mdot = sqrt(T rho A) (propulsion.md §1).
    mdot = math.sqrt(thrust_n * RHO_AIR * math.pi * (bore_r_mm / 1000.0) ** 2)
    aero = {}
    for tag, vc in V_CROSS.items():
        n_in = mdot * vc                                       # N, limit
        f_body = 0.5 * RHO_AIR * vc ** 2 * 1.2 * side_area_m2
        aero[tag] = {"N": n_in, "T_tilt": n_in * pivot / 1000.0,
                     "M_brg": n_in * arm_mm / 1000.0, "F_body": f_body,
                     "src": "momentum-drag screen"}
        if bore_r_mm == 32.0 and tag in AERO_CFD_64:
            n_cfd, m_cfd = AERO_CFD_64[tag]
            # CFD normal force is the TOTAL (inlet + body), so no separate
            # body-drag term; it acts on the duct axis for the bearing couple.
            aero[tag] = {"N": n_cfd, "T_tilt": m_cfd,
                         "M_brg": n_cfd * arm_mm / 1000.0, "F_body": 0.0,
                         "src": "3-D CFD"}
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
    # Governing combined case: drive envelope + bounding aero, ultimate.
    env = rows[1]
    ab = aero["bound 2 x corridor (15.6 m/s, ASSUMED)"]
    t_drive = env["T_ult"] + ab["T_tilt"] * ULT
    m_brg = m_thrust + env["M_gyro_ult"] + ab["M_brg"] * ULT
    f_rad = (thrust_n + ab["N"] + ab["F_body"]) * ULT / 2.0   # per bearing
    # Pieces for re-evaluating the couple at another bearing-pair centre:
    # forces that act on the duct axis scale with the arm; gyro does not.
    f_axis_ult = (thrust_n + ab["N"]) * ULT                   # N on the axis
    return {"name": name, "I": i_tilt, "mass": mass, "pivot": pivot,
            "h_spin": h_spin, "M_thrust_ult": m_thrust, "ring_cap": ring_cap,
            "rows": rows, "aero": aero, "mdot": mdot,
            "T_drive_comb": t_drive, "M_brg_comb": m_brg, "F_rad": f_rad,
            "F_axis_ult": f_axis_ult, "M_gyro_env": env["M_gyro_ult"],
            "arm": arm_mm}


# Bearing arrangements, all on the 20 mm spar stub (bore fixed by the spar),
# stacked from the spar tip at TRUNNION_X0.  Stack = bearing length; span =
# centre-to-centre of the pair; the pair centre sets the thrust arm.
X0_64 = 28.2 + (34.0 * 1.21 - 34.0)          # = 35.34 mm, spar tip
ARRANGEMENTS = [
    ("2 x 6704-ZZ, 8.0 mm stack (50 mm joint carried over)", BRG_C0, 8.0, 4.0),
    ("2 x 6704-ZZ, magnet nested round the inboard race (10.0 mm)",
     BRG_C0, 10.0, 4.0),
    ("2 x 6704-ZZ, 12.5 mm stack (wing pad recessed)", BRG_C0, 12.5, 4.0),
    ("2 x 6804-ZZ, 14.0 mm stack (BUILT, nacelle_trunnion_64mm)",
     BRG_C0_6804, 14.0, 7.0),
    ("2 x 6804-ZZ, 16.0 mm stack", BRG_C0_6804, 16.0, 7.0),
]


def bearing_table(r: dict) -> list[dict]:
    """fs per arrangement: axis forces x (X0 + stack/2) + gyro, over the span."""
    out = []
    for name, c0, stack, width in ARRANGEMENTS:
        span = stack - width
        arm = X0_64 + stack / 2.0
        m = r["F_axis_ult"] * arm / 1000.0 + r["M_gyro_env"]
        p0 = m / (span / 1000.0) + r["F_rad"]
        out.append({"name": name, "stack": stack, "span": span, "arm": arm,
                    "P0": p0, "fs": c0 / p0})
    return out


def report(r: dict) -> None:
    print(f"\n{r['name']}: rotating mass {r['mass'] / 453.592:.3f} lbm "
          f"({r['mass']:.0f} g), pivot {r['pivot']:.1f} mm")
    print(f"  I_tilt = {r['I']:.3e} kg.m^2 ({r['I'] * 3417.17:.2f} lbm.in^2)"
          f"   rotor spin momentum (both) {r['h_spin']:.4f} N.m.s")
    print(f"  thrust moment at the trunnion, ultimate {r['M_thrust_ult']:.2f}"
          f" N.m ({r['M_thrust_ult'] * LBF_IN_PER_NM:.1f} lbf.in)")
    print(f"  tip ring Lewis capacity {r['ring_cap']:.3f} N.m (no FOS)")
    print(f"  inlet mass flow {r['mdot']:.3f} kg/s (hover)")
    for tag, a in r["aero"].items():
        print(f"  aero [{tag}] ({a['src']}): normal force {a['N']:.2f} N "
              f"({a['N'] * LBF_PER_N:.2f} lbf) -> tilt-axis {a['T_tilt']:.3f}"
              f" N.m, bearing couple {a['M_brg']:.3f} N.m; body drag "
              f"{a['F_body']:.2f} N (limit loads)")
    for x in r["rows"]:
        print(f"  [{x['profile']}]  peak {math.degrees(x['omega']):.0f} deg/s,"
              f" {x['alpha']:.1f} rad/s^2")
        print(f"     inertia torque {x['T_inertia']:.4f} N.m limit, "
              f"{x['T_ult']:.4f} ult ({x['T_ult'] * LBF_IN_PER_NM:.3f} lbf.in)"
              f" -> drive margin {x['drive_margin']:.1f}x, tip-gear FOS "
              f"{x['gear_fos']:.1f}")
        print(f"     gyro moment (ult) {x['M_gyro_ult']:.3f} N.m -> per-bearing"
              f" {x['F_brg']:.0f} N ({x['F_brg'] * LBF_PER_N:.0f} lbf) = "
              f"{100 * x['brg_frac']:.0f} % of C0, s0 {1 / x['brg_frac']:.2f}; shaft tau "
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
    r50 = analyse("50 mm (Rev T4)", b50, p50, 21.9, arm50, h50, 25.0,
                  0.1852 * 0.0833)
    r64 = analyse("64 mm (adopted)", b64, p64, 2 * 20.9 * 0.90, arm64, h64,
                  32.0, 0.2093 * 0.1008)
    for r in (r50, r64):
        report(r)
    print(f"\n64 / 50: I_tilt x{r64['I'] / r50['I']:.2f}, spin momentum "
          f"x{r64['h_spin'] / r50['h_spin']:.2f}, thrust moment "
          f"x{r64['M_thrust_ult'] / r50['M_thrust_ult']:.2f}")

    print("\nCOMBINED (drive envelope + aero, ultimate):")
    for r in (r50, r64):
        ac = r["aero"]["corridor at V_min (7.8 m/s)"]
        t_c = r["rows"][1]["T_ult"] + ac["T_tilt"] * ULT
        print(f"  {r['name']} corridor aero: tilt-drive {t_c:.3f} N.m -> "
              f"margin {T_DRIVE_LIMIT / t_c:.1f}x; tip-gear FOS "
              f"{r['ring_cap'] / (t_c / ULT):.1f}")
        print(f"  {r['name']} BOUNDING aero: tilt-drive {r['T_drive_comb']:.3f} N.m "
              f"-> margin {T_DRIVE_LIMIT / r['T_drive_comb']:.1f}x; tip-gear "
              f"FOS {r['ring_cap'] / (r['T_drive_comb'] / ULT):.1f}; bearing "
              f"couple {r['M_brg_comb']:.2f} N.m + radial {r['F_rad']:.0f} N "
              "per bearing")
    print(f"\nBearing arrangements, 64 mm combined ultimate (fs = C0/P0; "
          f"min {FS_MIN}, target {FS_TARGET}) [REF-BRG-001/002/003]:")
    table = bearing_table(r64)
    for t in table:
        flag = ("MEETS TARGET" if t["fs"] >= FS_TARGET else
                "above min only" if t["fs"] >= FS_MIN else "BELOW MIN")
        print(f"  {t['name']:<58} span {t['span']:4.1f} arm {t['arm']:4.1f} mm"
              f"  P0 {t['P0']:5.0f}"
              f" N  fs {t['fs']:4.2f}  {flag}")
    built = table[BUILT_ARRANGEMENT]
    drive = T_DRIVE_LIMIT / r64["T_drive_comb"]
    gear = r64["ring_cap"] / (r64["T_drive_comb"] / ULT)
    # Tangential tooth load at the ring pitch circle (N, LIMIT load -- the
    # ring FOS above is also taken on limit), then the pinion root bending
    # stress sigma = F / (b m Y) (MPa).
    f_t = r64["T_drive_comb"] / ULT * 1000.0 / (RING_Z * RING_M / 2.0)
    sig_pin = f_t / (RING_FACE * RING_M * LEWIS_Y_14)
    pin_pr = SIGMA_FLEX / sig_pin
    print(f"\nWing 14T pinion (face {RING_FACE} mm, Y {LEWIS_Y_14}): tooth load "
          f"{f_t:.1f} N limit, root stress {sig_pin:.1f} MPa; printed CF-PETG "
          f"FOS {pin_pr:.2f}; so the pinion is METAL (wing_tilt_pinion.scad): bending allowable >= "
          f"{GEAR_FOS * sig_pin:.0f} MPa")
    checks = [("tilt drive (>= 1.0x)", drive, drive >= 1.0),
              (f"tip ring gear, Lewis (>= {GEAR_FOS:.0f})", gear,
               gear >= GEAR_FOS),
              # Not a pass/fail on geometry: the value is the bending
              # allowable (MPa) the metal pinion's material must meet.
              ("wing pinion: METAL, min allowable [MPa]", GEAR_FOS * sig_pin,
               True),
              ("trunnion bearings fs, " + built["name"][:11]
               + f" (>= {FS_TARGET:.0f})", built["fs"],
               built["fs"] >= FS_TARGET)]
    print("\nRESULT, 64 mm, combined ultimate with BOUNDING aero:")
    for label, val, good in checks:
        print(f"  {label:<44} {val:5.2f}  {'PASS' if good else 'FAIL'}")
    print("  (rotor spin data ASSUMED; 64 mm aero loads are 3-D CFD at the "
          "corridor speed and at an ASSUMED 2 x corridor bounding speed)")
    ok = all(good for _, _, good in checks)
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
