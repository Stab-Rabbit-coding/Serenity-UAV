# 64 mm Iris Nozzle — Gas Load, Spring and Servo Study (2026-11-21)

License: CC BY-SA 4.0 — see LICENSES/CC-BY-SA-4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (GitHub `Stab-Rabbit-coding`), owner direction
2026-11-21 ("resolve the load calculations to ensure the nozzles do their jobs and the servos do as
well").
**Analysis:** Claude (Claude Opus 5.5, Anthropic), with the `statics-and-dynamics` and
`mechanical-engineering` skills. **Reproduce:** `/usr/bin/python3 tools/nozzle64_flap_loads.py`.
**Owning items:** `airframe/wings-nacelles/WBS.md` NAC-64-SERVO-01, NAC-64-SERVO-HOLD,
NAC-64-NOZ-EXIT, NAC-64-NOZ-BALANCE (rejected); plan `docs/plans/2026-11-16-001-...` (D-SV-2, U2, U6, U8);
`docs/THEME_N_DECISION_BRIEFS.md` briefs D and E.

> **WARNING** — These results are analytical, unreviewed, and are not a substitute for a qualified
> engineer. A licensed Professional Engineer or an equivalently qualified authority shall review
> and accept them before they are applied to flight hardware. The nozzle is part of the hover
> thrust path; a nozzle that cannot reach or hold its scheduled position changes thrust in flight.

![Nozzle load study](figures/nozzle64_flap_loads.png)

## 1. Prior studies

None computed the gas load. The drive was fit-closed (2026-10-04) against a fail-open spring of
0.45 lbf (2.0 N) at the ring ear and an **assumed** flap allowance of 0.38 lbf (1.7 N), marked
"PENDING-U8" for a bench measurement (`tools/nozzle_servo_linkage_64.py`; plan 2026-09-28-001 U8
carries a 20 N placeholder). Its "holding" force was taken as 50 % of stall. Station pressures in
`nacelle_esc_bay.scad` (50 mm, inter-stage −2,781 Pa) are upstream of the fans' second stage and do
not describe the nozzle.

## 2. Method

- **Geometry, measured.** The eight flaps are rendered from `nacelle_nozzle_iris_64mm.scad` at seven
  angles from open (−2.54°) to closed (12.94°) and sliced for the wetted inner radius. The exit is
  read at the trailing edge of the inner face (0.7 mm short of the tip bevel), not at the minimum
  radius: open, the flaps diverge and the smallest radius is the hinge clevis lobes (§3, Finding 2).
- **Flow.** One-dimensional and incompressible (duct M 0.21): the exit is a subsonic free jet at
  ambient static pressure, and the static pressure at area A is
  Δp = q_e [1 − (A_e/A)²]. The exit dynamic pressure q_e is bounded three ways per nacelle (two
  QF2822-2300KV fans in series, 5.23 lbf (23.24 N) each at full throttle [REF-EDF-003]; stock exit
  ASSUMED equal to the bore): **constant pressure rise** (lower bound), **constant jet power**
  (nominal), **constant thrust** (upper bound, used as the design case because a fan's pressure
  rises toward shutoff as the nozzle closes). Ram at V_NE 87 kt (`flight_limits.json`) adds
  1,227 Pa in forward flight.
- **Statics.** Isolated body: the ring of eight flaps, each on its own tangential hinge pin, loaded
  by the net inner pressure (outer faces at ambient) and reacted at the hinge and the cam follower
  pin. Determinate per flap (hinge force components + pin force). Hinge moment
  M = Σ Δp · 2πr · s · ds, s along the face from the hinge station.
- **Transfer to the servo.** Virtual work through the spiral cam (pin radius linear in ring angle,
  the SCAD's `TAB_X`/`TAB_Z` 3.674/6.905 mm): T_ring = M · |dφ/dθ| (0.63–0.69), then
  F_ear = T_ring / 39.0 mm. Frictionless; friction is a bench quantity.
- **Servo capability.** KST CM07 sheet (2026-05): stall 1.80 / 2.10 / 2.40 kgf·cm at 6.0 / 7.4 /
  8.4 V; continuous zone ends ≈ 0.45 kgf·cm (read off the 7.4 V chart). At the ear through the
  re-solved linkage's worst point: 50.4 N per N·m.
- **Factor of safety.** 1.5 on the holding requirement, declared as engineering judgment (it
  equals the project's `fastener_default`, `current-specification/safety_factors.json`); no code
  sets one for this mechanism.

## 3. Results

Revision 2 (same day): the exit targets are now set on the flow surface (owner direction
2026-11-21, Finding 2) and the hinge stays at the root of the canonical petals (owner direction
2026-11-21, which rejects the balanced hinge of revision 1). The numbers below are for that
geometry; revision 1's numbers (closed at 16.96°, 67.7 % exit) are in the changelog.

**Closed (cruise schedule, flow exit 75.0 % of the bore), full throttle:**

| Fan model | Flight | Exit q_e | Radial gas force, all flaps | Hinge moment, all flaps | Gas load at the ring ear |
|---|---|---|---|---|---|
| constant Δp | static | 7,225 Pa | 4.37 lbf (19.4 N) | 2.16 lbf·in (0.244 N·m) | 0.88 lbf (3.9 N) |
| constant Δp | V_NE | 8,452 Pa | 5.11 lbf (22.7 N) | 2.53 lbf·in (0.285 N·m) | 1.03 lbf (4.6 N) |
| constant power | static | 10,599 Pa | 6.41 lbf (28.5 N) | 3.17 lbf·in (0.358 N·m) | 1.29 lbf (5.8 N) |
| constant power | V_NE | 11,826 Pa | 7.15 lbf (31.8 N) | 3.53 lbf·in (0.399 N·m) | 1.44 lbf (6.4 N) |
| **constant thrust** | **V_NE** | **14,065 Pa** | **8.50 lbf (37.8 N)** | **4.20 lbf·in (0.475 N·m)** | **1.72 lbf (7.6 N)** |

The gas pushes the flaps **open** (the fail-safe direction) at every angle; the load falls to zero
as the nozzle opens.

### Finding 1 — the servo cannot hold the nozzle closed

| | At the ring ear |
|---|---|
| Required continuous hold, design (spring 2.0 + gas 7.6 N) | **2.17 lbf (9.6 N)**; × 1.5 = 3.25 lbf (14.5 N) |
| Required, nominal (spring 2.0 + gas 6.4 N) | 1.89 lbf (8.4 N) |
| CM07 **continuous**, any voltage | **0.50 lbf (2.23 N)** |
| CM07 stall at 6.0 / 7.4 / 8.4 V | 2.00 / 2.33 / 2.67 lbf (8.9 / 10.4 / 11.9 N) |

Through today's linkage the CM07 cannot hold the closed nozzle continuously under any fan model.
At 6.0 V its stall torque closes the nozzle against the nominal load (8.9 ≥ 8.4 N, 6 % margin)
but not the design load (8.9 < 9.6 N); at 7.4 V it closes against the design load with 8 %
margin, which is not a design margin. The assumed 0.38 lbf (1.7 N) flap allowance was 3–4 × too
low, and the 50 %-of-stall holding assumption was 2.4 × the sheet's continuous rating. **The
spring alone (2.0 N × 1.5 = 3.0 N) exceeds the CM07's continuous capability**: even with zero gas
load the servo cannot hold any position but fully open indefinitely. The X06H had the same
problem. Setting the exit on the flow surface cut the closed design load from 10.8 to 7.6 N (the
nozzle now closes less far, 12.94° against 16.96°), but did not close this finding.

### Finding 2 — exit targets, now met on the flow surface

Revision 1 found the 75 % / 105 % targets applied to the flap **hinge line**, so the flow (which
sees the inner face, 2.5–3.3 mm further in) got 67.7 % closed and 97.1 % open. The SCAD now
solves the angle for the inner-face trailing edge,
r_exit = R_HINGE − L sin φ − t cos φ (L 36 mm, t 2.5 mm), and asserts it. Measured from the
rendered flaps: **closed 0.945 in (24.01 mm) = 75.0 %**; **open 1.316 in (33.43 mm) = 104.5 %**
(target 105 %; the 0.17 mm shortfall is the slice station 0.7 mm ahead of the tip and facet
error). The open nozzle now diverges (φ −2.54°), so a 0.5 mm (0.020 in) lift was added under the
lever-tab tip (`TAB_TIP_LIFT`) to keep it off the ring face.

Two root-region findings, recorded and **not** changed (the hinges stay at the canonical petal
root):

- **Clevis lobes inside the bore, open.** The flap hinge lobes stand to r 31.18 mm (0.8 mm,
  0.03 in, inside the 32.0 mm bore) over 48° of circumference at z 15.5 mm, 16° at z 17 mm, none
  by z 20 mm. A local step at the hinge, upstream of the exit; it does not set the exit area. Its
  loss is a CFD question (§5).
- **Lever tab through the housing hinge boss.** The rendered flap overlaps the housing's central
  hinge boss by about 1,600–1,800 mm³ (0.10–0.11 in³) at every angle, unchanged by this revision
  (it predates it). This is a modelling interference to resolve before print (WBS NAC-64-NOZ-EXIT).

### Finding 3 — centre of pressure; balancing rejected

The centre of pressure sits 0.49 in (12.6 mm) along the 1.39 in (35.4 mm) wetted face at every
angle and fan model. Moving the hinge about 12 mm aft would balance the flaps (revision 1), but
the owner has directed that the hinges stay at the root of the canonical petals, so **the gas
hinge moment is taken as given** and any relief has to come from the drive: the linkage
mechanical advantage (WBS NAC-64-SERVO-01, exploration in progress), the spring, or a latch.

### Structure (one flap, design load)

Gas resultant 1.06 lbf (4.7 N) per flap; it is reacted by the hinge pin and the cam follower pin
at a 0.31 in (7.8 mm) tab, **1.70 lbf (7.6 N) at each follower pin**. Root bending in a 1.02 ×
0.098 in (26 × 2.5 mm) section: 318 psi (2.2 MPa) against the 12,180 psi (84 MPa) DuraForm PA CF
tensile strength (`allowables.json`, REF-MAT-011); not governing. **Governing and unverified:**
pin bearing in PA CF and the cam-slot wear under the 7.6 N pin load (`allowables.json` bearing
strength "requires_verification").

## 4. Options for D and E

| | S1 keep CM07, reduce loads | S2 bigger servo | S3 CM07 + zero-power latch | S4 status quo |
|---|---|---|---|---|
| Nozzle geometry | flow-surface exit (done); hinge fixed | same | same | same |
| Spring | Reduce to 1.5 × measured friction (bench U8) | 2.0 N kept | 2.0 N kept, or reduced | 2.0 N |
| Closed hold, design × 1.5 | (spring + 7.6) × 1.5 ≥ 11.4 N against 2.2 N continuous: **fails at full throttle**; with a 0.5 N spring it holds while the closed gas load is ≤ 1.0 N, i.e. up to ≈ 13 % of full thrust | needs ≥ 14.5 N continuous at the ear (2.9 kgf·cm continuous through today's linkage); no listed candidate publishes such a rating | the latch holds closed with no servo current; power loss releases it → fails open | fails |
| Closing at full throttle (stall) | 6.0 V: 8.9 N against 8.1 N (0.5 N spring), 10 % margin | per servo | as S1; 2.0 N spring needs 7.4 V | 6.0 V fails |
| Intermediate positions (transition) | ok only at low gas load | ok if rated | servo short-time only (< 10 s per the sheet) **unless the spring is reduced** | fails |
| Added parts | throttle limit on closure in cruise (firmware) | larger pocket (≈ 23 × 7 × 18 mm) | latch pawl + small solenoid per nacelle, power-to-hold | — |
| Rail (D-SV-2) | 6.0 V | per servo | 6.0 V with a reduced spring, else 7.4 V | — |

Every column is limited by the linkage's 50.4 N at the ear per N·m of servo torque. A linkage
with more mechanical advantage scales every servo number in this table; that exploration is the
next step (WBS NAC-64-SERVO-01) and **the recommendation is held until it reports**. The
constraint it shall respect: an unpowered CM07 must still be back-driven open by the spring and
gas, so a toggle (dead-centre) linkage at the closed position is not acceptable without a
release.

**Bench measurements that close the largest unknowns (plan U8):** a static-pressure tap upstream
of the closed nozzle at full throttle (selects the fan model: 3.9–7.6 N spread), the
ring-and-flap friction (sets the spring), and the CM07 holding current and case temperature.

## 5. Not checked here

Fan surge or stall with the nozzle closed at full throttle (no fan curve published); thermal
effects on PA CF at the nozzle (cold exhaust, electric fan); flap flutter; the open-position
seal-flap step (U8). The pressure loss of the clevis-lobe step at the open hinge is not computed; an axisymmetric CFD (`openfoam-cfd` skill, `tools/od17_junction_cfd/` pattern) would size it.

## Changelog

- 2026-11-21 — first issue (Claude Opus 5.5). Closed at 16.96°: flow exit 67.7 %, open 97.1 %;
  closed design gas load 10.8 N at the ear; recommended a 10 mm aft (balanced) hinge.
- 2026-11-21 — revision 2 (Claude Opus 5.5): exit targets set on the flow surface (closed 12.94°,
  open −2.54°; measured 75.0 % / 104.5 %); design gas load 7.6 N; balanced hinge withdrawn per
  owner direction (hinges at the canonical petal root); open-exit read at the trailing edge;
  clevis-lobe and tab/boss findings recorded; recommendation held for the linkage study.
