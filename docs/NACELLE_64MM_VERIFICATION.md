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

The rotating assembly is 2.10 lbm (954 g) per nacelle. The CG and PIVOT_Z are at 3.87 in
(98.3 mm), moved from 107.5 mm, converged on both pods (residual ≤ 0.01 mm, iteration 2). The 10 AWG disconnect bay moves to Z
51 mm to clear the trunnion cavity. Hover clearance is +0.94 in (+23.9 mm) on the 3.0 in flight
gear; the retired 1.5 in gear strikes (−18 mm). Rows marked ASSUMED or SCALED (rotors, ESCs,
sleeves, nozzle) must be weighed or re-measured before release.

## 6. Install and removal (owner requirement)

See WBS NAC-64-SVC-01. Rotor 1 services through the intake. Both stages come out **aft** as
sleeve cartridges after the nozzle is removed. This requires phase-lead bullet connectors in the
ESC bays and an axial lead-escape slot in the bore. ESCs service through their existing covers;
the 10 AWG feeds service at the disconnect bay.

## 7. Open items raised by this record

- Owner decision: adopt the 6.5 mm elliptical lip (§3) and its exterior change (§4).
- Zero-volume slivers where the ESC discharge ports graze the sleeve bore (r 34.7 mm, Z 79/83/87):
  NAC-64-GEOM-02.
- Packaged OpenFOAM v1912 on this host: every function object aborts with "IOstream sha1". The
  CFD tool post-processes raw fields instead.
