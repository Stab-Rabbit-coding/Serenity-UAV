#!/usr/bin/python3
"""Landing-gear bellcrank load path: free-body diagrams of three configurations.

Owner request 2026-10-26: "Draw the free-body diagrams for the current design
and both proposed options. Include the mass penalties for each and the normal
and crash dynamics. Highlight the failure modes and locations."

Why this exists.  The Rev R6 thigh is a bellcrank: the foot force F at the
horizontal arm R_H (80 mm) is reacted by energy-absorber wires pushing on a
crank of radius r (6 mm) about the hip pin.  tools/landing_gear_r6_sizing.py
solves the wire force from the MOMENT balance (F R_H = 2 P r) but checks the
hip pin against F alone.  That is only true if the wires form a pure couple.
In the R6 layout both wires of a row sit at the same crank azimuth and push
the same way, so the FORCE balance puts about 2P through the pin and the bay.

Configurations (all at the decided LG-REMASS schedule, 13.0 lbm design mass):
  C0  current R6 + LG-REMASS: r 6, same-side wire pair, M3 pin, printed ears,
      blind printed wire sockets.
  A   balanced couple: one wire of each row on EACH side of the pin with
      antiparallel chords, r 10; A228 seat slugs on 6061 spreaders under the
      socket floors, 6061 ear liners and pin.  The pin carries only the foot force.
  B   metal load path: R6 layout kept (r 6, same-side pair); the 2P reaction is
      carried by 6061 clevis side plates, a 6061 pin and A228 seat slugs on
      6061 spreaders; the printed bay only locates.

Load cases per leg (foot force, vertical, at R_H), from the sizing tool's
schedule at the 13.0 lbm design mass and the R2 ledger (static share 25.1 %):
  static   stance             F = share x W
  normal   LG-06 1.5 ft drop  stopped elastically inside the 13.7 mm hover
                              nozzle clearance; linear spring, peak F = 2E/x
  crash    LG-17 4 ft drop    tail-down 2-pt, ductile plateau, settle 30.7 mm
  hier.    failure hierarchy  owner rule: mount capacity >= 1.25 x demand at
                              the leg's own breaking moment (grown thigh
                              197.3 N*m, tools/lg_thigh_variants.py); wire-path
                              parts (sockets, cups) >= 1.25 x the ductile
                              plateau, as lg_thigh_variants.py checks them.

Allowables (every one cited; see REFERENCES.md):
  CF-PETG bulk compression 47 MPa, the LOW end of ASTM D695 47-60 MPa
    [REF-MAT-001].  This is NOT a bearing allowable -- the repository holds no
    CF-PETG bearing coupon -- so it is used only as an upper bound for flat
    contact (thrust cups) and as an indicator for pin-in-printed-hole.
  A2 stainless pins: class 50 tensile 500 MPa (what the sizing tool assumes
    for the M3 pin) or class 70 700 MPa, M3 stress area 5.03 mm^2
    [REF-MAT-005 p.2].  Shear = 0.6 x tensile is a design-judgment ratio,
    "requires verification" in REFERENCES.md.
  304 plate yield 205 MPa, used as the steel bearing and tension limit;
    density 7.90 g/cm^3 [REF-MAT-006] (also the density proxy for the A228
    seat slugs; no music-wire density was cited).
  6061-T6: yield 276 MPa (used as the pin-bearing limit), ultimate shear
    207 MPa, density 2.70 g/cm^3 [REF-MAT-007].
  ASTM A228 music wire: minimum tensile 230 ksi (1,586 MPa) at 0.250 in
    [REF-MAT-008]; no yield is published there, so the seat-slug contact is
    checked against the minimum tensile and says so.

Material preference (owner 2026-10-26): printable composite, then pre-cut or
laid-up CF/Kevlar/glass, then aluminium, brass, spring steel, stainless; the
absorber wires stay metal.  A material is used only where a cited allowable
for that failure mode exists; the skips are printed.
  Printed density 1.05 g/cm^3: the project's effective print density
    (tools/auw_ledger.py RHO_PRINT).

Method: planar rigid-body statics of the thigh (FE-level, [REF-NCEES-009]);
energy of a free drop E = m g h x share; linear-spring peak force 2E/x;
ductile plateau force E/s.  Drop speed v = sqrt(2 g h).

Run:  /usr/bin/python3 tools/lg_bellcrank_fbd.py [--svg DIR]
Exit 2 if any configuration's governing margin is below 1.0.

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, 2026-10-26, per AGENTS.md section 3 AI attribution.
License: MIT (SPDX-License-Identifier: MIT) -- see tools/LICENSE.
"""

from __future__ import annotations

import argparse
import math
import os
import sys

# ---------------------------------------------------------------- inputs ---
G = 9.807                     # m/s^2
LBF = 4.44822                 # N per lbf
M_GEAR_MASS = 13.0 * 0.45359237     # kg, owner design mass 13.0 lbm
SHARE = 0.251                 # worst per-leg static share (sizing tool, R2 ledger)
R_H = 80.0                    # mm, hip -> foot horizontal arm
FOOT_Z = -118.0               # mm, foot sole below the hip (leg-local GROUND_Z)
NOZZLE_X = 13.7               # mm, hover nozzle-tip clearance (normal-case stop)
SETTLE_CRASH = 30.7           # mm, ductile settle budget the schedule is solved at
M_LEG_BREAK = 197.3e3         # N*mm, grown-thigh breaking moment (lg_thigh_variants)
HIER = 1.25                   # owner failure-hierarchy factor

SIG_PETG = 47.0               # MPa  [REF-MAT-001] bulk compression, low end
SU_A2_50, SU_A2_70 = 500.0, 700.0   # MPa  [REF-MAT-005]
SHEAR_RATIO = 0.6             # design judgment, requires verification
SY_304 = 205.0                # MPa  [REF-MAT-006]
RHO_STEEL = 7.90e-3           # g/mm^3  [REF-MAT-006]
RHO_PRINT = 1.05e-3           # g/mm^3  tools/auw_ledger.py

SOCK_CLR = 0.65               # mm, socket diametral clearance (leg SCAD)
EAR_T = 3.0                   # mm, printed clevis ear (leg SCAD)
PIN_BORE = 3.2                # mm, M3 pin bore (leg SCAD)
D_DUCT0, D_SPRING0 = 5.27, 4.06   # mm, LG-REMASS wires at r = 6
P_DUCT0 = 7655.0              # N, ductile plateau per wire at r = 6 (sizing tool)


def drop(h_ft):
    """(energy per leg J, touchdown speed m/s) for a free drop of h_ft."""
    h = h_ft * 0.3048
    return M_GEAR_MASS * G * h * SHARE, math.sqrt(2 * G * h)


def cases():
    """Foot force per leg (N) for each load case, with its dynamics."""
    w = M_GEAR_MASS * G
    e_n, v_n = drop(1.5)
    e_c, v_c = drop(4.0)
    e_c = M_GEAR_MASS * G * 4.0 * 0.3048 * 0.5          # tail-down 2-pt, 50 % per leg
    f_n = 2 * e_n / (NOZZLE_X / 1000)             # linear spring peak
    f_c = e_c / (SETTLE_CRASH / 1000)             # ductile plateau
    return {
        "static": dict(F=SHARE * w, note="stance"),
        "normal": dict(F=f_n, v=v_n, E=e_n, x=NOZZLE_X,
                       g4=4 * f_n / w, note="1.5 ft, stop in 13.7 mm"),
        "crash": dict(F=f_c, v=v_c, E=e_c, x=SETTLE_CRASH,
                      g2=2 * f_c / w, g4=4 * f_c / w, note="4 ft tail-down"),
        "hier": dict(F=M_LEG_BREAK / R_H, note="leg breaking moment"),
    }


def thigh_fbd(f_foot, r, wires):
    """Solve the thigh: foot force up at (R_H, FOOT_Z), wires at crank radius r.

    wires: list of (azimuth_deg, sign) -- the crank point is r(cos az, sin az)
    and a compression wire pushes on it along sign*(sin az, -cos az), the
    direction whose moment opposes the foot.  Returns (P per wire, pin
    reaction vector, wire force vectors)."""
    n = len(wires)
    p = f_foot * R_H / (n * r)                    # moment balance about the pin
    fw = [(sg * p * math.sin(math.radians(az)), -sg * p * math.cos(math.radians(az)))
          for az, sg in wires]
    sx = sum(f[0] for f in fw)
    sz = sum(f[1] for f in fw) + f_foot
    return p, (-sx, -sz), fw


CONFIGS = {
    "C0": dict(name="Current R6 + LG-REMASS", r=6.0, wires=[(30, 1), (30, 1)]),
    "A": dict(name="Option A: balanced couple", r=10.0, wires=[(30, 1), (210, 1)]),
    "B": dict(name="Option B: metal load path", r=6.0, wires=[(30, 1), (30, 1)]),
}


def disk_area(d):
    return math.pi / 4 * d * d


# Owner material preference (2026-10-26), first match wins for each part:
#   1 printable composite (CF-PETG)  2 pre-cut / laid-up CF, Kevlar, glass
#   3 aluminium  4 brass  5 spring steel  6 stainless.
# The absorber WIRES stay metal (ductile and elastic behaviour are the point).
# A material is eligible for a part only with a CITED allowable for that
# failure mode; otherwise it is skipped and the reason is printed.
SY_6061, SS_6061 = 276.0, 207.0     # MPa yield, ult. shear  [REF-MAT-007]
RHO_6061 = 2.70e-3                  # g/mm^3                 [REF-MAT-007]
SU_A228 = 1586.0                    # MPa, A228 min tensile 230 ksi, 0.250 in row [REF-MAT-008]
SKIPPED = {
    "CF-PETG (printed)": "no cited shear or pin-bearing allowable; flat contact only (47 MPa)",
    "CF / Kevlar / glass plate": "no cited bearing, shear or through-thickness allowable "
                                 "(LG-11 coupons would make it eligible)",
    "brass": "no verified allowable obtained (requires a cited source)",
}
SLUG_D, SLUG_L = 7.0, 4.0           # mm, A228 seat slug (largest stock dia 0.283 in)
SPREAD_T = 1.5                      # mm, 6061 spreader disc under the slug


def size_pin(dem):
    """6061 pin, double shear: smallest whole-mm dia that carries dem."""
    d = math.ceil(math.sqrt(dem / (2 * SS_6061) * 4 / math.pi))
    return d, 2 * SS_6061 * disk_area(d)


def size_plates(dem, d_pin):
    """6061 ear liners / side plates, pin bearing at yield, 0.5 mm steps."""
    t = math.ceil(dem / (2 * d_pin * SY_6061) * 2) / 2
    return t, 2 * t * d_pin * SY_6061


def analyse(key, cs):
    """Component demand vs capacity for one configuration, plus sizing and mass."""
    c = CONFIGS[key]
    r = c["r"]
    rows, mass_add = [], 0.0
    pin = {}
    for case in ("normal", "crash", "hier"):
        p, rp, _ = thigh_fbd(cs[case]["F"], r, c["wires"])
        pin[case] = (p, math.hypot(*rp))
    p_c = pin["crash"][0]                         # ductile plateau per wire
    d_duct = D_DUCT0 * (p_c / P_DUCT0) ** (1 / 3)  # wire scales as d^3 ~ P
    dem_pin = HIER * pin["hier"][1]               # vs 1.25 x leg-break reaction
    dem_s = HIER * p_c                            # wire path vs 1.25 x plateau
    if key == "C0":
        rows.append(("hip pin, double shear", "M3 A2, class-50 basis", dem_pin,
                     2 * SHEAR_RATIO * SU_A2_50 * disk_area(3.0)))
        rows.append(("clevis ears, pin bearing (printed)", "2 x 3 mm CF-PETG", dem_pin,
                     2 * EAR_T * PIN_BORE * SIG_PETG))
        rows.append(("wire socket floor, end thrust (printed)",
                     f"blind bore dia {d_duct + SOCK_CLR:.2f}", dem_s,
                     disk_area(d_duct + SOCK_CLR) * SIG_PETG))
    else:
        d_pin, cap = size_pin(dem_pin)
        rows.append(("hip pin, double shear", f"6061-T6 dia {d_pin} mm", dem_pin, cap))
        mass_add += (disk_area(d_pin) * RHO_6061 - disk_area(3.0) * RHO_STEEL) * 22.0
        t, cap = size_plates(dem_pin, d_pin)
        vol = 2 * (disk_area(d_pin + 8.0) - disk_area(d_pin)) * t
        if key == "B":                             # side plates run hip -> thrust plate
            vol += 2 * t * 12.0 * 30.0
        mass_add += vol * RHO_6061
        what = "ear liners" if key == "A" else "side plates"
        rows.append((f"clevis {what}, pin bearing", f"6061-T6, 2 x {t} mm", dem_pin, cap))
        # wire end -> A228 slug (contact) -> 6061 spreader -> CF-PETG (flat)
        a_wire = disk_area(d_duct)
        rows.append(("wire end on A228 seat slug, MPa (vs min tensile)",
                     f"music wire dia {SLUG_D:.0f} x {SLUG_L:.0f}", dem_s / a_wire,
                     SU_A228))
        rows.append(("slug on 6061 spreader, bearing, MPa", f"dia {SLUG_D:.0f} on 6061",
                     dem_s / disk_area(SLUG_D), SY_6061))
        d_c = math.ceil(math.sqrt(dem_s / SIG_PETG * 4 / math.pi))
        rows.append(("spreader on CF-PETG, flat bearing", f"6061 disc dia {d_c} x {SPREAD_T}",
                     dem_s, disk_area(d_c) * SIG_PETG))
        n_seats = 4                                # 2 ductile + 2 spring per leg
        mass_add += n_seats * (disk_area(d_c) * SPREAD_T * RHO_6061
                               + disk_area(SLUG_D) * SLUG_L * RHO_STEEL)
    if key == "A":                                 # printed thigh root ring grows r 6 -> 10
        lug = 16.0
        ring_old = disk_area(2 * (6 + (D_DUCT0 + SOCK_CLR) / 2 + 1.5))
        ring_new = disk_area(2 * (r + (d_duct + SOCK_CLR) / 2 + 1.5))
        mass_add += (ring_new - ring_old) * lug * RHO_PRINT
    wire_mass = 8 * (d_duct / D_DUCT0) ** 2 * 6.84 - 8 * 6.84    # 8 ductile wires/aircraft
    return dict(rows=rows, pin=pin, d_duct=d_duct, r=r,
                mass_leg=mass_add, mass_ac=4 * mass_add + wire_mass)


def draw(key, cs, res, path):
    """Schematic FBD of the thigh at the crash case; failure locations in red."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    c = CONFIGS[key]
    f = cs["crash"]["F"]
    p, rp, fw = thigh_fbd(f, c["r"], c["wires"])
    fig, ax = plt.subplots(figsize=(6.2, 6.2))
    ax.set_aspect("equal")
    ax.plot([0, R_H], [0, FOOT_Z], color="0.55", lw=10, solid_capstyle="round", zorder=1)
    ax.add_patch(plt.Circle((0, 0), c["r"] + 4, color="0.75", zorder=2))
    ax.add_patch(plt.Circle((0, 0), 1.8, color="k", zorder=5))
    sc = 25.0 / max(abs(f), p)                     # arrow scale, mm per N (normalised)
    ax.annotate("", xy=(R_H, FOOT_Z), xytext=(R_H, FOOT_Z - f * sc * 1.6),
                arrowprops=dict(arrowstyle="-|>", color="tab:blue", lw=2.2))
    ax.text(R_H + 3, FOOT_Z - 14, f"F foot {f:.0f} N\n({f / LBF:.0f} lbf)",
            color="tab:blue", fontsize=8)
    fails = [rw for rw in res["rows"] if rw[3] < rw[2]]
    for (az, sg), v in zip(c["wires"], fw):
        cx, cz = c["r"] * math.cos(math.radians(az)), c["r"] * math.sin(math.radians(az))
        bx, bz = cx - v[0] / p * 34, cz - v[1] / p * 34        # boss along the chord
        ax.plot([cx, bx], [cz, bz], color="tab:green", lw=2, zorder=3)
        ax.add_patch(plt.Rectangle((bx - 4, bz - 4), 8, 8, color="tab:olive", zorder=3))
        ax.annotate("", xy=(cx, cz), xytext=(cx - v[0] * sc, cz - v[1] * sc),
                    arrowprops=dict(arrowstyle="-|>", color="tab:green", lw=1.8))
    ax.text(-58, 46, f"wire P {p:.0f} N each\n(r = {c['r']:.0f} mm)", color="tab:green", fontsize=8)
    ax.annotate("", xy=(0, 0), xytext=(-rp[0] * sc, -rp[1] * sc),
                arrowprops=dict(arrowstyle="-|>", color="tab:red", lw=2.4))
    ax.text(-58, -40, f"pin reaction {math.hypot(*rp):.0f} N\n({math.hypot(*rp) / LBF:.0f} lbf)",
            color="tab:red", fontsize=8)
    for i, rw in enumerate(fails):
        ax.text(-58, -70 - 11 * i, f"X FAILS: {rw[0]}  ({rw[3] / rw[2]:.2f}x)",
                color="red", fontsize=7)
    if fails:
        ax.plot(0, 0, "rx", ms=18, mew=3, zorder=6)
    ax.set_xlim(-62, 120)
    ax.set_ylim(-140, 70)
    ax.set_title(f"{c['name']}\n4 ft crash, per leg (thigh FBD, swing plane)", fontsize=9)
    ax.set_xlabel("mm (hip pin at origin)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    # Images are documents: CC BY-SA 4.0 embedded in every original image.
    fig.savefig(path, metadata={
        "Title": f"Serenity UAV gear bellcrank FBD, {c['name']}",
        "Creator": "tools/lg_bellcrank_fbd.py (Claude Opus 5.5 for Stab-Rabbit-coding)",
        "Rights": "CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/4.0/",
    })
    plt.close(fig)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--svg", help="write one FBD SVG per configuration to this directory")
    args = ap.parse_args(argv)
    cs = cases()
    print("LOAD CASES per leg (13.0 lbm design mass, share %.1f %%)" % (100 * SHARE))
    for k, v in cs.items():
        extra = ""
        if "v" in v:
            extra = (f"  touchdown {v['v']:.2f} m/s ({v['v'] / 0.5144:.1f} kt), "
                     f"E {v['E']:.1f} J, stroke {v['x']} mm")
        if "g4" in v:
            extra += f", peak decel level 4-pt {v['g4']:.0f} g"
        if "g2" in v:
            extra += f" / 2-pt {v['g2']:.0f} g"
        print(f"  {k:7s} F {v['F']:7.0f} N ({v['F'] / LBF:6.1f} lbf)  {v['note']}{extra}")
    print("\nMaterial preference skips (owner order 2026-10-26):")
    for m, why in SKIPPED.items():
        print(f"  {m:28s} {why}")
    worst = {}
    for key in CONFIGS:
        res = analyse(key, cs)
        print(f"\n== {key}: {CONFIGS[key]['name']}  (crank r {res['r']:.0f} mm, "
              f"ductile wire dia {res['d_duct']:.2f})")
        for case in ("normal", "crash", "hier"):
            p, rp = res["pin"][case]
            print(f"   {case:7s} wire P {p:7.0f} N   pin reaction {rp:7.0f} N "
                  f"({rp / LBF:6.0f} lbf)")
        for name, what, dem, cap in res["rows"]:
            m = cap / dem
            u = "MPa" if "MPa" in name else "N  "
            print(f"   {name:50s} {what:28s} demand {dem:7.0f} {u} cap {cap:7.0f} {u} "
                  f"margin {m:5.2f} {'OK' if m >= 1.0 else 'FAILS'}")
        worst[key] = min(cap / dem for _, _, dem, cap in res["rows"])
        print(f"   mass penalty vs C0: {res['mass_leg']:+.1f} g/leg, "
              f"{res['mass_ac']:+.1f} g/aircraft incl. wire change "
              f"({res['mass_ac'] / 453.59:+.3f} lbm)")
        if args.svg:
            os.makedirs(args.svg, exist_ok=True)
            draw(key, cs, res, os.path.join(args.svg, f"lg_bellcrank_fbd_{key}.svg"))
    print("\nworst margin: " + ", ".join(f"{k} {v:.2f}" for k, v in worst.items()))
    return 0 if all(v >= 1.0 for k, v in worst.items() if k != "C0") else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
