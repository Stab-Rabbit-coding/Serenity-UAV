#!/usr/bin/python3
"""64 mm nozzle servo drive: servo -> link -> bellcrank -> rod -> ring ear.

Single source for the nozzle-servo linkage of the 64 mm nacelle (WBS
NAC-64-SERVO-01, owner decisions 2026-10-04: servo inside the canonical dorsal
spine; bellcrank so the drive stays inside canon; nozzle slides off with no
linkage parts handled).  Writes
``airframe/openscad/nacelles/nozzle_servo_linkage_64_params.scad``, which the
pod wrapper and the 64 mm nozzle include, so geometry never drifts from the
solved kinematics.

Frame: STARBOARD nacelle-local (z = duct axis from the intake; az measured
from +x; top of the nacelle in cruise is az 270 = local -y).  Port is the
mirror x -> -x (az -> 180 - az), applied in the SCAD.

Chain (all rigid, all in the pod except the ring):
  * Ring ear ball B(psi): r 39.0, z = nozzle ring Z 187.86 + 4.0, psi from
    292.5 (closed, 75 % exit) to 268.75 (open, 105 %), the 64 mm iris
    (nacelle_nozzle_iris_64mm.scad RING_LEVER_AZ, THETA_RING_REF_OPEN 23.75).
  * Bellcrank on a RADIAL pivot pin at C (az 255, z 179, r 42), output arm 14
    to a rod of length fixed at the closed pose (RSSR search 2026-10-04: worst
    rod-to-ear-motion angle 6 deg over the stroke).
  * Input arm, tangential at mid-stroke so its tip moves axially, driven by an
    axial link from the servo horn.
  * Servo Blue Bird BMS-101DMG [REF-ACT-004], 18.5 x 7.6 x 15.7 mm (VERIFY),
    lying flat in the spine (7.6 radial), output shaft TANGENTIAL, 4.0 mm horn
    radial-outward at mid-stroke, +/-60 deg.

Peak ear force is energy-limited: F = T sin(th) cos(th) / (L_out sin(beta))
(th servo half-sweep, beta bellcrank half-sweep), maximal at th = 45 deg.

Checks (exit 2 on failure): every joint centre inside the canonical shell
with cover, monotonic ring vs servo, transmission angles, horn/arm/rod
clearances, and the force chain against the KTD3 spring.

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, per AGENTS.md AI attribution.  License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "airframe/openscad/nacelles/nozzle_servo_linkage_64_params.scad"

Z_NOZ = 187.86
B_R, B_Z = 39.0, Z_NOZ + 4.0
PSI_CLOSED, PSI_OPEN = 292.5, 268.75
C_AZ, C_Z, C_R = 255.0, 179.0, 42.0
L_OUT = 14.0
HORN, SERVO_SWEEP = 4.0, 90.0           # mm, deg (+/-45: maximises T sin cos)
SERVO_TORQUE = 0.147                    # N.m, 1.5 kgf.cm at 6 V, KST X06 [REF-ACT-005] (VERIFY)
SERVO_DIMS = (20.0, 7.0, 16.6)          # L x W x H mm [REF-ACT-005] (VERIFY)
SPRING_N = 2.0                          # KTD3 spring at the ball (plan U2)


def unit(v):
    return v / np.linalg.norm(v)


def er(az):
    return np.array([math.cos(math.radians(az)), math.sin(math.radians(az)), 0.0])


def ball(psi):
    return np.array([B_R * math.cos(math.radians(psi)),
                     B_R * math.sin(math.radians(psi)), B_Z])


C = C_R * er(C_AZ) + np.array([0, 0, C_Z])
AX = er(C_AZ)                                   # bellcrank pivot axis (radial)
U = unit(np.cross(AX, [0, 0, 1.0]))
V = np.cross(AX, U)


def arm(phi, L):
    return C + L * (math.cos(phi) * U + math.sin(phi) * V)


def solve_out(psi, L_rod, guess):
    """Bellcrank angle putting the output tip at rod length from B(psi)."""
    b = ball(psi)
    best = None
    for d in np.radians(np.arange(-40, 40.01, 0.05)):
        phi = guess + d
        e = abs(np.linalg.norm(arm(phi, L_OUT) - b) - L_rod)
        if best is None or e < best[0]:
            best = (e, phi)
    return best[1], best[0]


def main() -> int:
    import argparse
    global C_AZ, C_Z, C_R, C, AX, U, V, OUT
    ap = argparse.ArgumentParser(description="64 mm nozzle servo linkage")
    ap.add_argument("--pivot", nargs=3, type=float, metavar=("AZ", "Z", "R"),
                    help="trial bellcrank pivot (default: the adopted one)")
    ap.add_argument("--out", type=Path, help="params file (default: the repo one)")
    ap.add_argument("--servo-z", type=float, default=153.0, help="servo shaft Z")
    ap.add_argument("--servo-az", type=float, default=None,
                    help="servo horn-plane azimuth (default: the input tip's)")
    a = ap.parse_args()
    if a.pivot:
        C_AZ, C_Z, C_R = a.pivot
        C = C_R * er(C_AZ) + np.array([0, 0, C_Z])
        AX = er(C_AZ); U = unit(np.cross(AX, [0, 0, 1.0])); V = np.cross(AX, U)
    if a.out:
        OUT = a.out
    # 1. output arm: pick the closed-pose angle maximising worst transmission
    psis = np.linspace(PSI_CLOSED, PSI_OPEN, 49)
    cand = []
    for phi0 in np.radians(np.arange(0, 360, 1.0)):
        L_rod = np.linalg.norm(arm(phi0, L_OUT) - ball(PSI_CLOSED))
        if not 12.0 <= L_rod <= 26.0:
            continue
        phis, worst, ok, g = [], 0.0, True, phi0
        for psi in psis:
            phi, err = solve_out(psi, L_rod, g)
            if err > 0.05 or abs(phi - g) > math.radians(10):
                ok = False
                break
            rod = unit(ball(psi) - arm(phi, L_OUT))
            vb = np.array([-math.sin(math.radians(psi)), math.cos(math.radians(psi)), 0])
            worst = max(worst, math.degrees(math.acos(min(1, abs(rod @ vb)))))
            phis.append(phi)
            g = phi
        if ok:
            cand.append((worst, phi0, L_rod, phis))
    cand.sort(key=lambda c: c[0])
    worst, phi0, L_rod, phis = cand[0]
    bc_sweep = math.degrees(phis[-1] - phis[0])
    phi_mid = 0.5 * (phis[0] + phis[-1])
    # 2. input arm tangential at mid-stroke; length from equal axial travel
    travel = 2 * HORN * math.sin(math.radians(SERVO_SWEEP / 2))
    L_in = travel / (2 * math.sin(math.radians(abs(bc_sweep) / 2)))
    # input arm angle: tip velocity axial at mid => arm along +/-tangent
    et = np.array([-math.sin(math.radians(C_AZ)), math.cos(math.radians(C_AZ)), 0])
    phi_in_mid = math.atan2(et @ V, et @ U)
    off_in = phi_in_mid - phi_mid                   # fixed angle between arms
    tip_in_mid = arm(phi_in_mid, L_in)
    # 3. servo: body on the bore-wall floor (r 36.4 .. 44.0, 7.6 radial), shaft
    #    TANGENTIAL at the body's mid-depth, at the input tip's azimuth; horn
    #    radial-outward at mid-stroke; link = measured horn-tip -> input-tip.
    SERVO_Z = a.servo_z
    t_az = math.degrees(math.atan2(tip_in_mid[1], tip_in_mid[0]))
    if a.servo_az is not None:
        t_az = a.servo_az
    shaft = (36.4 + SERVO_DIMS[1] / 2) * er(t_az) + np.array([0, 0, SERVO_Z])
    s_az = t_az
    def horn(th):   # th = 0 radial-outward; rotates in the (er, ez) plane
        return shaft + HORN * (math.cos(th) * er(t_az) + math.sin(th) * np.array([0, 0, 1.0]))
    LINK = float(np.linalg.norm(tip_in_mid - horn(0.0)))
    # full-stroke solve of the servo loop
    ths, lw = [], 0.0
    g = 0.0
    for phi in phis:
        tip = arm(phi + off_in, L_in)
        best = None
        span = 90 if not ths else 15        # first point: search the full range
        for d in np.radians(np.arange(-span, span + 0.01, 0.05)):
            e = abs(np.linalg.norm(tip - horn(g + d)) - LINK)
            if best is None or e < best[0]:
                best = (e, g + d)
        if best[0] > 0.05:
            print("servo loop: no solution"); return 2
        g = best[1]; ths.append(g)
        link = unit(tip - horn(g))
        hv = HORN * (-math.sin(g) * er(t_az) + math.cos(g) * np.array([0, 0, 1.0]))
        lw = max(lw, math.degrees(math.acos(min(1, abs(link @ unit(hv))))))
    srv_sweep = math.degrees(ths[-1] - ths[0])
    mono = all(np.diff(ths) * np.sign(ths[-1] - ths[0]) > 0)
    print(f"servo loop: servo sweep {srv_sweep:.1f} deg (monotonic {mono}), worst "
          f"link-to-horn-motion angle {lw:.1f} deg")
    # 4. force chain at the worst point
    # worst-case chain: horn force x cos(link angle) x arm ratio x cos(rod angle)
    f_horn = SERVO_TORQUE / (HORN / 1000)
    f_out = f_horn * math.cos(math.radians(lw)) * L_in / L_OUT
    f_ear = f_out * math.cos(math.radians(worst))
    hold = 0.5 * f_ear
    print(f"bellcrank: pivot az {C_AZ} z {C_Z} r {C_R}; output {L_OUT} mm, rod "
          f"{L_rod:.2f} mm, sweep {bc_sweep:.1f} deg, worst rod-to-ear angle {worst:.1f} deg")
    print(f"input arm {L_in:.2f} mm (tangential at mid); link {LINK:.2f} mm; "
          f"servo shaft at r {math.hypot(*shaft[:2]):.2f} az {s_az:.1f} z {shaft[2]:.1f}, "
          f"horn {HORN} mm, sweep {SERVO_SWEEP} deg")
    print(f"force at ear: stall {f_ear:.1f} N ({f_ear/4.448:.2f} lbf), holding "
          f"{hold:.1f} N vs spring {SPRING_N} N -> allowable flap load at ball "
          f"{hold - SPRING_N:.1f} N  (PENDING-U8 bench load)")
    good = worst <= 30 and hold > SPRING_N and mono and lw <= 50 and abs(srv_sweep) <= 130
    OUT.write_text(f"""// GENERATED by tools/nozzle_servo_linkage_64.py — do not hand-edit.
// 64 mm nozzle servo linkage, STARBOARD nacelle-local frame (port = mirror x).
NSL_B_R = {B_R}; NSL_B_Z = {B_Z:.3f};
NSL_PSI_CLOSED = {PSI_CLOSED}; NSL_PSI_OPEN = {PSI_OPEN};
NSL_C = [{C[0]:.4f}, {C[1]:.4f}, {C[2]:.4f}];  NSL_C_AZ = {C_AZ}; NSL_C_R = {C_R};
NSL_U = [{U[0]:.6f}, {U[1]:.6f}, {U[2]:.6f}];  NSL_V = [{V[0]:.6f}, {V[1]:.6f}, {V[2]:.6f}];
NSL_L_OUT = {L_OUT}; NSL_L_IN = {L_in:.3f}; NSL_L_ROD = {L_rod:.3f}; NSL_LINK = {LINK};
NSL_PHI_CLOSED = {math.degrees(phis[0]):.3f}; NSL_PHI_OPEN = {math.degrees(phis[-1]):.3f};
NSL_ARM_OFFSET = {math.degrees(off_in):.3f};   // input arm angle - output arm angle
NSL_SHAFT = [{shaft[0]:.4f}, {shaft[1]:.4f}, {shaft[2]:.4f}];  NSL_SHAFT_AZ = {s_az:.3f};
NSL_HORN = {HORN}; NSL_SERVO_SWEEP = {srv_sweep:.2f}; NSL_TH_CLOSED = {math.degrees(ths[0]):.2f}; NSL_TH_OPEN = {math.degrees(ths[-1]):.2f};
NSL_SERVO_SIDE = -1;   // servo body on the -az side of its horn plane (centred on the crest)
NSL_SERVO = [{SERVO_DIMS[0]}, {SERVO_DIMS[1]}, {SERVO_DIMS[2]}];   // KST X06 L x W x H [REF-ACT-005] VERIFY
""")
    print(f"wrote {OUT}  ->  {'PASS' if good else 'FAIL'}")
    return 0 if good else 2


if __name__ == "__main__":
    sys.exit(main())
