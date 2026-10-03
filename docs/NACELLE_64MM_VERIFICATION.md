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

## 1. Axial fit (R11) — `tools/nacelle_axial_fit.py`

| Case | Rotor-1 entry | Motor-2 tail | Margin to nozzle pocket (Z 166.25 mm) |
| --- | --- | --- | --- |
| Current architecture (8 mm spiders) | 1.08 in (27.5 mm) | 7.89 in (200.5 mm) | −1.35 in (−34.2 mm) FAIL |
| Stator-as-mount, full bell | 1.08 in (27.5 mm) | 6.85 in (173.9 mm) | −0.30 in (−7.7 mm) FAIL |
| **Adopted:** stator-as-mount, 8 mm trim, rotor in the bell | 0.69 in (17.49 mm) | 6.45 in (163.9 mm) | **+0.09 in (+2.4 mm) PASS, VERIFY** |

The QF2822 body is 2.28 in (58.0 mm) from rear cap to mount face [REF-EDF-003, 8-4.jpg], against
about 1.06 in (27 mm) for the 50 mm stack's 2627 motor. This is the driver. Every dimension here
comes from the drawing; NAC-64-FIT-02 measures a physical motor and rotor.

## 2. Rotor inside the bell — hand checks (`aeronautical-engineering`, propulsion.md §1, §3)

**Inputs:**

- Thrust T = 4.70 lbf (20.9 N) per fan [REF-EDF-003, QF2822-2400 KV, 22.2 V row].
- Air density ρ = 1.225 kg/m³ (ISA sea level), ASSUMED.
- Disc area A = π (0.032 m)² = 32.2 cm².

**Regime:** bore velocity √(T/ρA) = 142 kt (72.8 m/s), M 0.21, so incompressible treatment is
valid in the duct. The momentum disc velocity is 100 kt (51.5 m/s). Tip speed at an ASSUMED
45,000 rpm is about 151 m/s (M 0.44), and blade Re is about 1.0 × 10⁵ (10 mm chord ASSUMED).

**Tip clearance:** the rotor leading edge goes only as far forward as the bell adds ≤ 0.004 in
(0.1 mm) of radius. With an ASSUMED 0.4 mm running gap, c/D moves from 0.62 % to at most 0.78 %
over the first ~2 mm of blade tip only. propulsion.md §3 calls tip clearance a first-order loss on
small EDFs, and no cited loss coefficient is available, so this must be bench-measured
(thrust/RPM at both rotor stations).

**Bell geometry:** trimming the cosine bell from 27.5 to 19.5 mm steepens its maximum wall slope
from 12.4° to 17.2° and halves its end radius of curvature (39.9 → 20.1 mm).

## 3. OpenFOAM screen — `tools/nacelle_intake_cfd.py`

The model is a 2-D axisymmetric wedge (simpleFoam, k-ω SST, wall functions) of the static/hover
inlet. Fan suction is imposed at the hover bore velocity. The fan itself is not modelled, so this
screens inlet flow, not installed thrust.

**Mesh study:** coarse (7,600 cells) and fine (2.25× cells) both pass checkMesh, with max
non-orthogonality 17° and skewness 0.33. Physical residuals reached ≤ 2 × 10⁻⁶; the out-of-plane
`Uz` residual is excluded.

| Variant | Reversed flow on bell wall (coarse / fine) | Rotor-LE total-pressure deficit at r/R 0.95 / 0.98 (fine) | Flow angle at r/R 0.95 (fine) |
| --- | --- | --- | --- |
| Cosine bell, 27.5 mm, 3.84 mm flare (as drawn, sharp lip) | 88 % / 87 % | 123 % / 135 % of q | +7.0° |
| Cosine bell, 19.5 mm (adopted trim, sharp lip) | 98 % / 93 % | 120 % / 143 % of q | +5.7° |
| Elliptical lip, 19.5 mm, 3.84 mm flare | 68 % / 47 % | 0.8 % / 91 % of q | −2.1° |
| **Elliptical lip, 19.5 mm, 6.5 mm flare (QX-like)** | **0 % / 0 %** | **0.6 % / 3.8 % of q** | **−4.3°** |

**Finding:** the bell **as drawn has a sharp lip**. The cosine profile reaches the front face with
zero slope, and the bell cut radius at Z 0 (35.84 mm) is larger than the fairing lip
(INTAKE_LIP_R 34.5 mm). In static/hover flow that lip separates for both bell lengths, so the
outer ~10 % of radius at the rotor face is recirculation. That is where the fan does most of its
work. **The trim is not the problem; the lip is.** The 50 mm pod has the same feature (28.0 vs
27.5 mm).

**The rotor-in-bell idea is sound with a rounded lip.** A quarter-elliptical lip with 6.5 mm of
radial flare (QX shroud outline ø77.00 mm [REF-EDF-003, 7-2.jpg], VERIFY) gives fully attached,
uniform inflow to r/R 0.98. Its gentler wall also lets the rotor sit at Z 16.09 mm, which adds
+1.4 mm of axial margin (+3.8 mm total). It needs about 38.5 mm of lip radius at the intake face,
which affects the exterior; see §4. **Owner decision pending.** CFD is screening only; confirm on
a thrust/pressure bench (plan U12).

## 4. Exterior shape against the canonical blueprints [REF-CAD-003]

Source: Sheet 2, Starboard Outboard Profile, main engine in flight position (815 px pack image;
±10 % reading uncertainty).

| Measure | Canon | 50 mm pod | 64 mm pod (1.28× radial) |
| --- | --- | --- | --- |
| Side-profile length ÷ height | ≈ 2.5 | 185.2 / 83.3 = 2.22 | 185.2 / 106.6 = **1.74** |
| Deviation from canon | — | −11 % | **−30 %** |

The canonical engine also shows a pronounced rounded forward intake ring, which is consistent with
the §3 rounded-lip recommendation. The radial growth is the owner-approved R10 deviation, recorded
here as required; holding canon L/H would need about 266 mm of length (R11 stop). The canonical
engine is about 23 % of ship length on the same sheet, against about 30 % for the 24 in (610 mm)
build. That is a pre-existing, owner-approved enlargement.

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
