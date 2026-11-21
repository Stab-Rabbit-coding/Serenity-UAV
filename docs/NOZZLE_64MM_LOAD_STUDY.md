# 64 mm Iris Nozzle — Gas Load, Spring and Servo Study (2026-11-21)

License: CC BY-SA 4.0 — see LICENSES/CC-BY-SA-4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (GitHub `Stab-Rabbit-coding`), owner direction
2026-11-21 ("resolve the load calculations to ensure the nozzles do their jobs and the servos do as
well").
**Analysis:** Claude (Claude Opus 5.5, Anthropic), with the `statics-and-dynamics` and
`mechanical-engineering` skills. **Reproduce:** `/usr/bin/python3 tools/nozzle64_flap_loads.py`.
**Owning items:** `airframe/wings-nacelles/WBS.md` NAC-64-SERVO-01, NAC-64-SERVO-HOLD,
NAC-64-NOZ-EXIT, NAC-64-NOZ-BALANCE; plan `docs/plans/2026-11-16-001-...` (D-SV-2, U2, U6, U8);
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
  angles from open (1.43°) to closed (16.96°) and sliced for the wetted inner radius.
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

**Closed (cruise schedule), full throttle:**

| Fan model | Flight | Exit q_e | Radial gas force, all flaps | Hinge moment, all flaps | Gas load at the ring ear |
|---|---|---|---|---|---|
| constant Δp | static | 7,225 Pa | 5.11 lbf (22.7 N) | 2.53 lbf·in (0.286 N·m) | 1.03 lbf (4.6 N) |
| constant Δp | V_NE | 8,452 Pa | 5.98 lbf (26.6 N) | 2.96 lbf·in (0.334 N·m) | 1.21 lbf (5.4 N) |
| constant power | static | 12,148 Pa | 8.59 lbf (38.2 N) | 4.25 lbf·in (0.480 N·m) | 1.74 lbf (7.7 N) |
| constant power | V_NE | 13,375 Pa | 9.46 lbf (42.1 N) | 4.68 lbf·in (0.529 N·m) | 1.92 lbf (8.5 N) |
| **constant thrust** | **V_NE** | **16,980 Pa** | **12.01 lbf (53.4 N)** | **5.94 lbf·in (0.671 N·m)** | **2.43 lbf (10.8 N)** |

The gas pushes the flaps **open** (the fail-safe direction) at every angle; the load falls to zero
as the nozzle opens.

### Finding 1 — the servo cannot hold the nozzle closed

| | At the ring ear |
|---|---|
| Required continuous hold, design (spring 2.0 + gas 10.8 N) | **2.88 lbf (12.8 N)**; × 1.5 = 4.32 lbf (19.2 N) |
| Required, nominal (spring 2.0 + gas 8.5 N) | 2.36 lbf (10.5 N) |
| CM07 **continuous**, any voltage | **0.50 lbf (2.23 N)** |
| CM07 stall at 6.0 / 7.4 / 8.4 V | 2.00 / 2.33 / 2.67 lbf (8.9 / 10.4 / 11.9 N) |

The CM07 cannot hold the closed nozzle continuously under any fan model, and at 6.0 V it cannot
even close it against the nominal load. The assumed 0.38 lbf (1.7 N) flap allowance was 3–6 × too
low, and the 50 %-of-stall holding assumption was 2.4 × the sheet's continuous rating. **The spring
alone (2.0 N × 1.5 = 3.0 N) exceeds the CM07's continuous capability**: even with zero gas load the
servo cannot hold any position but fully open indefinitely. The X06H had the same problem.

### Finding 2 — the nozzle misses its exit targets

The 75 % / 105 % targets are applied to the flap **hinge line** in the SCAD; the flow sees the inner
face, about 0.10–0.13 in (2.5–3.3 mm) further in. Measured flow exit: **closed 0.853 in (21.67 mm)
= 67.7 % of the bore** (requirement 75 %); **open 1.224 in (31.09 mm) = 97.1 %** (requirement
105 %). Open, the flap roots stand 0.035 in (0.9 mm) inside the 32.0 mm bore, so the flow steps
inward at the hinge. 105 % is **not reachable** with today's hinge circle and flap root: the root
inner face cannot leave r 31.1 mm. The 75 % flow exit is reached at φ ≈ 13.0°, where the design gas
load at the ear is ≈ 1.73 lbf (7.7 N).

### Finding 3 — the centre of pressure is stable, so the flaps can be balanced

The centre of pressure sits 0.48–0.49 in (12.3–12.6 mm) along the 1.38 in (35 mm) wetted face at
every angle and every fan model: the pressure **shape** is set by the geometry, only its size
by the throttle. Moving the hinge aft along the flap by s_h cuts the closed design load at the ear
by ≈ 0.19 lbf (0.86 N) per mm:

| Hinge aft of today | Closed design gas load at the ear | Gas still opens at every angle? |
|---|---|---|
| 0 mm (today) | 2.43 lbf (10.8 N) | yes |
| 8 mm (0.31 in) | 0.88 lbf (3.9 N) | yes |
| 10 mm (0.39 in) | 0.50 lbf (2.2 N) | yes |
| 12 mm (0.47 in) | 0.11 lbf (0.5 N) | yes (marginal, 0.3 mm from the c.p.) |
| 13 mm or more | negative (gas CLOSES) | **no — fail-open at full throttle lost** |

A hinge at **10 mm** keeps a gas opening moment with 2.3 mm (0.09 in) of margin to the centre of
pressure. That margin is a 1-D result: it shall be confirmed by an axisymmetric CFD of the closed
nozzle (the `openfoam-cfd` skill; `tools/od17_junction_cfd/` is the case-writer pattern) before the
hinge is moved.

### Structure (one flap, design load)

Gas resultant 1.50 lbf (6.7 N) per flap; it is reacted by the hinge pin and the cam follower pin
at a 0.31 in (7.8 mm) tab, **2.41 lbf (10.7 N) at each follower pin**. Root bending in a 1.02 ×
0.098 in (26 × 2.5 mm) section: 449 psi (3.1 MPa) against the 12,180 psi (84 MPa) DuraForm PA CF
tensile strength (`allowables.json`, REF-MAT-011); not governing. **Governing and unverified:**
pin bearing in PA CF and the cam-slot wear under the 10.7 N pin load (`allowables.json` bearing
strength "requires_verification").

## 4. Options for D and E

| | S1 keep CM07, reduce loads | S2 bigger servo | S3 CM07 + zero-power latch | S4 status quo |
|---|---|---|---|---|
| Nozzle geometry | **Fix the exit targets** (N1) and **balance the flaps**, hinge 10 mm aft (N2) | N1 + N2 | N1 + N2 | as built |
| Spring | Reduce to 1.5 × measured friction (bench U8) | 2.0 N kept | 2.0 N kept | 2.0 N |
| Closed hold, design × 1.5 | (spring + 2.2) × 1.5: fits only if spring ≤ 0.0 N — **fails at full throttle**; with a 0.5 N spring it fits while the closed gas load is ≤ 0.99 N, i.e. up to ≈ 45 % of full thrust (gas load scales with thrust) | needs ≥ 6.3 N continuous at the ear (1.27 kgf·cm continuous); the LD5801 (3.8 kgf·cm stall) is the only listed candidate and has **no published continuous rating** | the latch holds the closed position with no servo current; power loss releases it → fails open | fails |
| Intermediate positions (transition) | ok if the spring is reduced | ok if rated | servo short-time only (< 10 s per the sheet) **unless the spring is reduced** | fails |
| Added parts | throttle limit on closure in cruise (firmware) | larger pocket (≈ 23 × 7 × 18 mm) | latch pawl + small solenoid per nacelle, power-to-hold | — |
| Rail (D-SV-2) | 6.0 V | per servo | 6.0 V (closing stall 8.9 N ≥ 6.3 N required) | — |

**Recommendation:** **N1 + N2 + S3**, with the spring re-sized from the U8 friction measurement:
fix the exit targets on the flow surface, move the flap hinge 10 mm aft (CFD-confirmed), hold the
cruise-closed position on a power-to-hold latch so the CM07 only moves the nozzle, and keep the
6.0 V rail (D1). The latch preserves fail-open on power loss; the balanced flaps keep the gas
pushing open at every angle; reducing the spring is what lets the CM07 hold intermediate positions
during transition. If the owner prefers no latch, S2 is the alternative, gated on a servo with a
published continuous rating.

**Bench measurements that close the largest unknowns (plan U8):** a static-pressure tap upstream
of the closed nozzle at full throttle (selects the fan model: 5.4–10.8 N spread), the
ring-and-flap friction (sets the spring), and the CM07 holding current and case temperature.

## 5. Not checked here

Fan surge or stall with the nozzle closed at full throttle (no fan curve published); thermal
effects on PA CF at the nozzle (cold exhaust, electric fan); flap flutter; the open-position
seal-flap step (U8). Cruise drag effect of the 67.7 % exit is not computed.

## Changelog

- 2026-11-21 — first issue (Claude Opus 5.5).
