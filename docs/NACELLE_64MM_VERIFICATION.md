# 64 mm Nacelle — Verification Record (2026-10-03)

> ⚠️ **ENGINEERING REVIEW REQUIRED — this output is not a substitute for a
> qualified engineer.** Every result, calculation, and recommendation produced
> with this skill **must be independently reviewed and accepted by a properly
> qualified individual** — a licensed Professional Engineer or an equivalently
> qualified authority for the jurisdiction and discipline — **before it is
> applied to any system carrying risk to life or safety.** This skill informs
> engineering judgment; it does not replace it. It is reference material
> provided AS-IS (see LICENSE §5), is not an engineering service, and does not
> constitute a sealed, certified, or reviewed work product for any specific
> project.

**Owner:** Steve Griffing, PE(CSE), CISSP-ISSEP, CEH (GitHub `Stab-Rabbit-coding`). The owner
supplied the design decisions and the rotor-in-bell idea checked here.
**Analysis:** Claude (Claude Opus 5.5, Anthropic), using the `aeronautical-engineering` and
`openfoam-cfd` skills, per `AGENTS.md` AI attribution.
**Plan:** `docs/plans/2026-09-28-001-feat-nacelle-nozzle-servo-drive-plan.md` (U5, U9, U12).
**Geometry:** `airframe/openscad/nacelles/nacelle_pod_64mm_tandem.scad`.

Regulatory basis: the aircraft is an sUAS under 14 CFR Part 107, which governs operations and
imposes no structural certification basis. These checks are against the project's own adopted
criteria.

## 0. Design summary (current, 2026-10-03)

| Item | Value | Source |
| --- | --- | --- |
| Radial scale | 1.21 (packaging minimum) | `tools/nacelle_64_proportion_trade.py` |
| Length | 8.24 in (209.3 mm), canonical axial stretch 1.13 | same |
| Canon L/D, plan / side | 2.29 / 2.08 against canon 2.24 / 2.31 | §4 |
| Intake | 2:1 elliptical lip 16 × 8 mm, round 4.0 mm nose, ring 42.5 mm | §3 |
| Rotor 1 | Z 30.5 mm, constant 64 mm bore (no tip-gap growth) | wrapper |
| Motor margin to nozzle pocket | +0.43 in (+11.0 mm), VERIFY | §1 |
| Pivot, mass, hover clearance | §5 | `tools/nacelle_mass_cg_64.py` |

## 1. Axial fit (R11) — `tools/nacelle_axial_fit.py`

| Case | Rotor-1 entry | Motor-2 tail | Margin to nozzle pocket |
| --- | --- | --- | --- |
| Current architecture (8 mm spiders), 185.2 mm | 1.08 in (27.5 mm) | 7.89 in (200.5 mm) | −1.35 in (−34.2 mm) FAIL |
| Stator-as-mount, full bell, 185.2 mm | 1.08 in (27.5 mm) | 6.85 in (173.9 mm) | −0.30 in (−7.7 mm) FAIL |
| Stator-as-mount, 8 mm trim, rotor in the bell, 185.2 mm | 0.69 in (17.49 mm) | 6.45 in (163.9 mm) | +0.09 in (+2.4 mm), superseded |
| **Lengthened (gate):** 209.3 mm, lip + straight duct | 1.20 in (30.5 mm) | 6.96 in (176.9 mm) | **+0.43 in (+11.0 mm) PASS, VERIFY** |

The QF2822 body is 2.28 in (58.0 mm) from rear cap to mount face [REF-EDF-003, 8-4.jpg], against
about 1.06 in (27 mm) for the 50 mm stack's 2627 motor. This is the driver. Every dimension here
comes from the drawing; NAC-64-FIT-02 measures a physical motor and rotor.

## 2. Inlet hand checks (`aeronautical-engineering`, propulsion.md §1, §3)

**Inputs:**

- Thrust T = 4.70 lbf (20.9 N) per fan [REF-EDF-003, QF2822-2400 KV, 22.2 V row].
- Air density ρ = 1.225 kg/m³ (ISA sea level), ASSUMED.
- Disc area A = π (0.032 m)² = 32.2 cm².

**Regime:** bore velocity √(T/ρA) = 142 kt (72.8 m/s), M 0.21, so incompressible treatment is
valid in the duct. Tip speed at an ASSUMED 45,000 rpm is about 151 m/s (M 0.44), and blade Re is
about 1.0 × 10⁵ (10 mm chord ASSUMED).

**Tip clearance:** in the final design the rotor sits in the constant 64 mm bore behind the lip,
so the bell adds no tip gap. The earlier rotor-in-bell option would have added up to 0.1 mm
(c/D 0.62 → 0.78 % with an ASSUMED 0.4 mm gap). propulsion.md §3 rates tip clearance a
first-order loss on small EDFs, and removing it is a thrust gain the lengthening paid for.

**Lip geometry:** contraction ratio (40/32)² = 1.56. Nose radius is 4.0 mm on both branches
(internal F²/a = 8²/16; external B²/A = 2.5²/1.5625).

## 3. OpenFOAM screen — `tools/nacelle_intake_cfd.py`

The model is a 2-D axisymmetric wedge (simpleFoam, k-ω SST, wall functions) of the static/hover
inlet. Fan suction is imposed at the hover bore velocity. The fan itself is not modelled, so this
screens inlet flow, not installed thrust. Physical residuals reach ≤ 5 × 10⁻⁶ (the out-of-plane
`Uz` residual is excluded). The packaged v1912 aborts in every function object, so the tool
post-processes raw fields.

**Stage 1, flanged lip face (conservative thick lip), coarse / fine mesh:**

| Variant | Reversed flow on bell wall | Rotor-face deficit, r/R 0.95 / 0.98 (fine) |
| --- | --- | --- |
| Cosine bell 27.5 mm (as drawn, sharp lip) | 88 % / 87 % | 123 % / 135 % of q |
| Cosine bell 19.5 mm (trim, sharp lip) | 98 % / 93 % | 120 % / 143 % of q |
| Ellipse 19.5 × 3.84 mm | 68 % / 47 % | 0.8 % / 91 % of q |
| Ellipse 19.5 × 6.5 mm | 0 % / 0 % | 0.6 % / 3.8 % of q |

**Stage 2, real external forebody (open far field all round), the case that governs:**

| Variant | Contraction ratio | Nose radius in / out | Reversed (bell, duct) | Deficit at r/R 0.95 / 0.98 |
| --- | --- | --- | --- | --- |
| 13 × 6.5 mm lip, 22 × 2 mm forebody | 1.45 | 3.25 / **0.18** mm | 15 %, 24 % | 91.5 % / 119 % |
| A: 13 × 6.5 mm, round nose | 1.45 | 3.25 / 3.25 | 0 %, 18 % | 18.3 % / 77 % |
| B: 10 × 5 mm | 1.37 | 2.5 / 2.5 | 42 %, 42 % | 103 % / 123 % |
| C: 8 × 4 mm | 1.27 | 2.0 / 2.0 | 82 %, 58 % | 161 % / 163 % |
| D: 10 × 5 mm, fat ring | 1.37 | 2.5 / 2.5 | 40 %, 40 % | 97.5 % / 120 % |
| **E: 16 × 8 mm, ring 42.5 (adopted)** | **1.56** | **4.0 / 4.0** | **0 %, 4 %** | **4.2 % / 38 % (fine: 1.0 % / 32.5 %)** |
| F: 13 × 6.5 mm, ring 42.5 | 1.45 | 3.25 / 3.25 | 0 %, 16 % | 8.6 % / 67 % |
| G: 3:1, 19.5 × 6.5 mm | 1.45 | 2.17 / 2.17 | 0 %, 4 % | 25.3 % / 80 % |
| H: 3:1, 24 × 8 mm | 1.56 | 2.67 / 2.67 | 0 %, 4 % | 5.5 % / 50 % |

**Findings:**

1. The intake **as drawn has a sharp lip** (cosine profile square to the front face) and separates
   in hover for both bell lengths. The 50 mm pod has the same feature.
2. The flanged model hid a second failure: a slim exterior with a knife-edged outside separates,
   because hover inflow wraps around the lip from behind.
3. **Contraction ratio is the lever** (1.27 → 1.45 → 1.56 progressively clears the tip), and
   2:1 beats 3:1 at equal flare.
4. **Lip E** is the only variant with no separation that also keeps rotor-face loss at or below
   4.2 % (coarse) and 1.0 % (fine) at r/R 0.95, with near-axial flow (−0.2° to +0.1°). The
   32–38 % loss at r/R 0.98 is the wall boundary layer of the 14.5 mm straight duct.

CFD is screening only. Confirm on a thrust/pressure bench (WBS NAC-64-LIP-02, plan U12) and add a
cruise-condition case for ring spillage drag.

## 4. Exterior shape against the canonical blueprints [REF-CAD-003]

Canon was measured from the unobstructed views: Sheet 4 (dorsal plan, engine 166 × 74 px) and
Sheet 3 (VTOL side, 164 × 71 px), on 815 px pack images with about ±5 % reading uncertainty. An
earlier reading from Sheet 2's flight side view (≈ 2.5) is withdrawn: the hull and wing hide the
engine's top in that view.

| Measure | Canon | 50 mm pod | 64 mm at 1.28 × 185.2 mm | **64 mm adopted (1.21 × 209.3 mm)** |
| --- | --- | --- | --- | --- |
| L/D, plan (spanwise) | 2.24 | 2.46 (skinny, +10 %) | 1.92 (−14 %) | **2.29 (+2 %)** |
| L/D, side (fore-aft) | 2.31 | 2.22 (−4 %) | 1.74 (−25 %) | **2.08 (−10 %)** |

The canonical section is nearly round (74 vs 71 px), while the shell is narrow spanwise
(75.4 × 83.3 mm). The ESC bays bound the fore-aft scale, so the side view stays about 10 % full.
The lip ring (42.5 mm) is larger than the canonical dome tip ahead of Z ≈ 20 mm; the canonical
intake ring is itself bulbous, and this is recorded as a deviation. The lengthening is an
owner-approved change to R11 (2026-10-03).

## 5. Mass, CG and pivot — `tools/nacelle_mass_cg_64.py`

| Quantity | Value |
| --- | --- |
| Pod (measured) | 0.584 lbm (265 g), CG 94.6 mm |
| Rotating assembly | **2.05 lbm (929 g)** per nacelle (1.28 × 185.2 mm design: 954 g) |
| CG = PIVOT_Z | **4.32 in (109.7 mm)**, converged on both pods (residual +0.02 mm, iteration 2) |
| Hover clearance, 3.0 in flight gear | **+0.54 in (+13.7 mm)** (floor 0.5 in, Claude-chosen); the retired 1.5 in gear strikes |
| 10 AWG disconnect bay | Z 57.6 mm, between the Z 45.2 and 70.1 bulkheads, clear of the trunnion cavity |

Rows marked ASSUMED or SCALED (rotors, 70 A ESCs, sleeves, nozzle) must be weighed or
re-measured before release.

## 5b. Tilt-axis inertia and load path — `tools/nacelle_tilt_dynamics.py`

The owner asked for this (2026-10-03): the larger nacelle needs more torque to accelerate about
its pivot, and the trunnion, bearings, gears, shaft and tilt drive carry the load. Inertia is a
rigid-body sum: the measured pod's own inertia, plus every component as a shaped body (motors as
cylinders, rotors as discs, sleeves and nozzle as tubes, ESCs at their off-axis bay positions).
The old 7.19 × 10⁻⁴ kg·m² point-mass figure (TILT_SPAR_ANALYSIS §2.1.2) understated even the
50 mm pod by about 1.9×.

| | 50 mm (Rev T4) | 64 mm (adopted) | Ratio |
| --- | --- | --- | --- |
| I about the tilt axis | 1.36 × 10⁻³ kg·m² (4.63 lbm·in²) | 2.74 × 10⁻³ kg·m² (9.37 lbm·in²) | ×2.02 |
| Rotor spin momentum, 2 co-rotating rotors (ASSUMED rotor data) | 0.042 N·m·s | 0.104 N·m·s | ×2.46 |
| Thrust moment at the trunnion, ultimate | 1.06 N·m | 2.22 N·m (19.6 lbf·in) | ×2.10 |

Governing achievable case: the built drive's 144 °/s with the TILT-CTL-05 acceleration of
52.6 rad/s², × 1.5 ultimate.

| Load-path item | 64 mm result | Verdict |
| --- | --- | --- |
| Tilt drive (1.81 N·m at the nacelle) | 0.216 N·m (1.92 lbf·in) | **8.4× margin**, pass |
| 50T m0.8 tip ring, Lewis, printed | FOS 12.0 against inertia torque | pass (≥ 4) |
| Ø4 mm drive shaft torsion | 5.1 MPa | negligible; grade not recorded |
| Gyroscopic moment | 0.393 N·m ult; normal to the tilt axis, so it loads the bearings, not the drive | — |
| **2 × 6704-ZZ trunnion bearings, 4.0 mm span** | **653 N (147 lbf) per bearing = 89 % of C0 730 N [REF-BRG-001]; s0 1.12** | **thin; owner decision** |

The 50 mm pod's bearings are at 42 % (s0 2.40). The bearing is the critical item because thrust
doubles, the arm grows by the 7.14 mm axis shift, and the gyroscopic moment adds on the same
axis. The repo previously implied a ~907 N "static rating"; that is a dynamic rating, and the
correction is recorded in WING_ATTACH_INTERFACE §4.3a. The tilt-axis aero moment is still
unquantified (TILT-CTL-06), and the larger frontal area makes it bigger.

## 5c. Tilt joint in context — `nacelle_tilt_joint_context.scad` (option A + relief 1)

The real wing mesh, pod, trunnion and pinion were assembled in position and swept through
tilt −5 to 140° with manifold3d (tilt maps to +θ in the trunnion part frame).

| Pair | Before | After |
| --- | --- | --- |
| Pinion vs pod | 474–1127 mm³ | 0 |
| Shaft vs pod collar | 18 mm³ | 0 |
| Shaft vs trunnion flange | 28 mm³ | 0 |
| Pinion (real teeth, rolling) vs ring | — | 0.03–0.06 mm³: zero-backlash tangency |

Ring Lewis capacity is 3.63 N·m, FOS 4.13 on the bound aero case. CG converged to 109.67 mm
against PIVOT_Z 109.7. The pod shell measures 247.6 cm³. Images:
`docs/images/nacelle_64mm_tilt_joint_optionA.png` and `_cutaway.png`. The wing pinion is the
released part `wing_tilt_pinion.scad`: brass, because at Lewis Y 0.277 (14T) a
CF-PETG pinion only reaches FOS 2.86; required allowable ≥ 76 MPa. Learning:
`docs/solutions/design-patterns/build-every-joint-in-context-through-its-full-motion.md`.

## 6. Install and removal (owner requirement)

See WBS NAC-64-SVC-01. Rotor 1 now sits in the straight duct behind the lip and services through
the intake. Both stages come out **aft** as sleeve cartridges after the nozzle is removed. This
requires phase-lead bullet connectors in the ESC bays and an axial lead-escape slot in the bore.
ESCs service through their covers, and the 10 AWG feeds at the disconnect bay.

## 7. Open items raised by this record


- **Trunnion bearings at s0 1.12** (§5b, WBS NAC-64-TILT-01): confirm C0 on the JTEKT
  catalogue, measure rotor spin data and the aero moment, then decide span or bearing.
- **Stator-as-mount sleeves** are not yet drawn (NAC-64-GEOM-01); 70 A ESC bay fit
  (NAC-64-ESC-70A).
- **Zero-volume slivers in the render:** where the ESC cooling ports graze
  the sleeve bore (r 34.7 mm, Z 91.5/95.5/99.5), and one per pod at the
  cover-doubler band (r ≈ 40 mm, Z 77–82). NAC-64-GEOM-02.
- **Bench checks:**
  - lip on a thrust/pressure bench and a cruise-case CFD (NAC-64-LIP-02);
  - physical QF2822 and rotor measurements (NAC-64-FIT-02).
- **Hull-frame bake** for the 7.14 mm axis shift and the new length (NAC-64-GEOM-04).
