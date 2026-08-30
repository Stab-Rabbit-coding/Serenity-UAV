---
title: "Nacelle Mould-Line Conformance and Nozzle Shortening - Plan"
date: 2026-08-29
artifact_contract: ce-unified-plan/v1
artifact_readiness: requirements-only
product_contract_source: ce-brainstorm
related:
  - docs/plans/2026-08-29-003-feat-unified-20mm-spar-trunnion-belt-drive-plan.md
  - docs/plans/2026-08-29-004-feat-nacelle-trunnion-pivot-tilt-drive-plan.md
  - docs/plans/2026-08-26-001-nacelle-esc-intake-integration-plan.md
---

# Nacelle Mould-Line Conformance and Nozzle Shortening - Plan

**Target repo:** Serenity-UAV (this repo)

---

## Goal Capsule

**Objective.** Bring both ends of the nacelle into conformance with the
canonical Serenity mould line, and shorten the nozzle stack enough to recover
hover ground clearance. Three pieces of work that share one subject — where the
printed nacelle deviates from the canonical shell — and one of which is also a
flight-safety fix.

**Product authority.** The canonical shell
(`airframe/stls/nacelles/eng_left_shell24_50mm_repaired.stl`, Thingiverse
Thing 14474 scaled 1.25×) is the mould-line authority. Where printed geometry
stands proud of it, the printed geometry is wrong unless a functional
requirement says otherwise and that requirement is recorded.

**Clearance target — settled 2026-08-29.** The flap trim (40 → 30 mm) combines
with plan 003's revised station (28.0) and ESC1 relocation to give **+9.8 mm on
the existing 1.5 in gear**, which the owner has accepted. No landing-gear change
is forced. No blockers remain.

---

## Problem Frame

Three deviations from the canonical shell, discovered separately, all in the
same subsystem:

1. **The nozzle stack overhangs the shell by 36.1 mm** and, with the nacelles
   vertical, the tip strikes the ground. Measured: rotating assembly reaches
   nacelle-local Z 221.3 against a 185.2 mm shell; in hover the tip sits at hull
   Z −41.39 against a −38.1 mm ground plane on the 1.5 in gear that
   `serenity_assembly.py` L505-518 calls the active default variant. **This is a
   strike on every vertical takeoff and landing.**
2. **The nozzle housing stands proud radially.** Housing `HOUSING_OUTER_R` is
   35.6 where the canonical shell's max radius at the pocket start (Z 166.25) is
   32.4 — **3.2 mm proud**, growing to **3.9 mm** at the shell's aft end where
   the canonical profile has narrowed to 29.6. The SCAD records this as owed
   work: *"Fully ovalising the housing to the cowl mould line … deferred
   VERIFY."* The WBS `[x]` for "Housing aft taper (Stage 2)" covers only the
   simple cylindrical taper (35.6 → 33.5), not the ovalising.
3. **The intake blend stands proud at the nose.** The additive fairing curve
   rises to `INTAKE_BLEND_R_PEAK` on a monotone rise/fall while the canonical
   dome does not, so the two curves cross. Measured deviation:

   | Z | shell r_max | blend r | blend − shell |
   |---|---|---|---|
   | 0 | 22.2 | 27.5 | **+5.3 proud** |
   | 5 | 28.0 | 28.4 | **+0.4 proud** |
   | 10 | 31.5 | 29.3 | −2.2 |
   | 25 | 38.1 | 32.0 | −6.2 |
   | 60 | 38.5 | 38.2 | −0.3 |

   The blend is proud only over roughly Z 0–7 and is buried elsewhere. That
   single crossing is what produces the wavy flange already logged in
   `docs/plans/2026-08-26-001-…` U5.

### Why the overhang cannot simply be deleted

The tandem stack fills the canonical shell. Only **6.4 mm** is left aft of EDF2
for a nozzle that measures **58.1 mm**:

| Item | Span | Length |
|---|---|---|
| intake bell | 0 – 27.5 | 27.5 |
| EDF1 | 27.5 – 90.0 | 62.5 |
| stator | 90.0 – 122.5 | 32.5 |
| EDF2 | 122.5 – 178.8 | 56.3 |
| **free for nozzle** | **178.8 – 185.2** | **6.4** |

A variable-area iris behind a tandem EDF stack **cannot** fit inside a
canonical-length nacelle. The overhang is structural to the propulsion
architecture, not drift. This plan therefore *reduces* it rather than removing
it, and records the residual as an accepted, documented deviation.

---

## Product Contract

### Requirements

- **R1** — Nozzle flap length goes 40 → 30 mm, reducing the stack overhang from
  36.1 mm to 26.1 mm and raising hover clearance by 10 mm.
- **R2** — The nozzle drive still reaches both end stops across the full tilt
  range at the larger swing arc the shorter flaps require, with the same exit-
  area range as today (75 %/105 % bore targets).
- **R3** — Hover ground clearance is **≥ 9.8 mm on the 1.5 in gear** with the
  nacelles vertical, verified against final geometry. This is the owner-accepted
  margin (~1 cm); it is not a derived requirement and must not be silently
  traded away by downstream geometry changes.
- **R4** — The nozzle housing conforms to the canonical cowl mould line: no
  point of the housing or its hinge bosses stands proud of the canonical shell
  radius at the same station, or the exception is recorded with its functional
  justification.
- **R5** — The intake fairing is a single fair curve: circular at the lip,
  following the most convex line of the canonical profile at Z 0, and tangent
  into the canonical mould line at or before the dome's monotonic limit
  (Z ≈ 30, measured). It stands proud of the canonical dome nowhere. The
  existing `INTAKE_BLEND_L = 90` / peak-at-Z-60 construction is retired — it
  peaks past the dome's own maximum, which is the cause of the crossing.
- **R6** — The Ø50 mm internal flow path and its effective area are unchanged by
  R4 and R5. Mould-line conformance is an *exterior* change; the duct is not to
  be reshaped to achieve it.
- **R7** — Every residual deviation from the canonical shell that survives this
  work — notably the 26.1 mm aft overhang — is documented with its measured
  magnitude and the reason it is accepted.

### Key Decisions

- **KD1 — Flaps to 30 mm, not 20 mm.** *(session-settled: user-directed —
  chosen over 20 mm, which yields +13.7 mm but doubles the swing arc back to
  3.58–25.94°.)* 30 mm splits the difference: +10 mm of clearance for a
  proportionally smaller arc penalty. Governs R1, R2.
- **KD2 — The overhang is reduced, not eliminated.** Established by the axial
  budget above. Governs R7.
- **KD3 — Mould-line conformance is exterior-only.** The duct's Ø50 mm flow
  path and area schedule are held fixed; conformance is achieved by reshaping
  skin and fairing, not the bore. Governs R6.
- **KD4 — Intake and exhaust conformance ship together.** They are the same
  defect class against the same authority, they touch adjacent parametric
  blocks in one file, and both require the same canonical-shell measurement
  tooling. Splitting them would duplicate that tooling. Governs R4, R5.
- **KD5 — Stator compression is out of scope.** It was offered as a further
  clearance lever (~7 mm from the 32.5 mm inter-stage gap) and not selected. It
  would need an aero justification for the shortened stator, which is a
  different investigation. Recorded in Scope Boundaries as deferred.

### Success Criteria

1. Hover clearance is positive at the chosen gear with a margin the owner has
   explicitly accepted (OQ1).
2. No printed nacelle geometry stands proud of the canonical shell radius at
   any station, except documented exceptions under R7.
3. The intake flange reads as one continuous curve — no crossing, no waviness.
4. Nozzle exit-area range is unchanged from today at the new flap length.
5. The Ø50 mm duct area schedule is unchanged.

### Scope Boundaries

**In scope:** flap length change and the linkage re-solve it forces; nozzle
housing radial ovalising to the cowl mould line (the deferred Stage 2); intake
fairing conformance and the wavy-flange fix; measurement tooling for
canonical-shell conformance; documentation of residual deviations.

**Deferred:**
- Stator/inter-stage compression as a further clearance lever (KD5).
- Landing-gear length change — tracked as `LG-HOVER-01`; this plan reduces the
  deficit but does not decide the gear.
- The radial protrusion of the *nozzle drive* (~10 mm past the OD), already an
  open WBS item — related but a different part.

**Out of scope:** any change to the EDF units, duct diameter, or the propulsion
architecture that creates the overhang.

### Outstanding Questions

- **OQ1 — RESOLVED 2026-08-29 (owner-accepted).** +9.8 mm on the 1.5 in gear,
  reached by combining the 30 mm flaps with plan 003's station 28.0 and the ESC1
  relocation. The compact gear stays viable; `LG-HOVER-01` closes with it.
  Ballast could buy more (+16.6 mm at 12 mm CG shift) but costs T/W 1.59 → 1.55
  and is not taken.
- **OQ2** — Does the shorter flap still reach the 75 %/105 % bore exit-area
  targets, and does the RSSR linkage stay monotonic and non-locking at the
  larger arc? The linkage synthesis is already an open VERIFY item.
- **OQ3** — Does full ovalising need the part-local→hull transform the SCAD says
  it does, and is that transform available yet in `serenity_assembly.py`?
- **OQ4 — RESOLVED 2026-08-29 (owner-directed).** Do not conform point-by-point
  to the canonical dome at the nose. Instead build **a clean new curve that
  follows the most convex line of the canonical curve at Z 0 and blends into the
  canonical mould line before the dome departs from monotonic.** This sidesteps
  the voxel-repair-fidelity question entirely: the new curve is fair by
  construction rather than inherited from mesh noise.

  Measured, this pins the blend's endpoint. The canonical dome's max radius
  rises monotonically to **Z ≈ 30** (22.2 → 28.0 → 31.5 → 34.3 → 36.3 → 38.1 →
  38.4) and falls thereafter (37.6 at Z 35). The existing fairing instead peaks
  at **Z 60** with `INTAKE_BLEND_L = 90` — well past the monotonic region, which
  is *why* the curves cross. **The blend must terminate by Z ≈ 30, tangent to
  the dome**, not run to Z 90. See R5.
- **OQ5 — RESOLVED 2026-08-29 by implementation.** The spar station move is
  **done** (wing Rev T1, station 28.0, `SPAR_Z` 66.85), so it is no longer a
  sequencing question — this plan's clearance budget must be computed against
  the built spar height, not against a pending one. The +9.8 mm figure in R3
  already assumes station 28.0 and the ESC1 relocation, so it stands; but
  **re-verify it against the built geometry** rather than carrying it forward,
  because R3 is an owner-accepted margin and this plan is the last thing that
  can silently spend it.
- **OQ6 (new)** — The nacelle inherits three joint requirements from the wing
  side that touch this plan's geometry: the 4 × 10 AWG disconnect relocates into
  the nacelle annulus (WA-R10), the ring magnet grows to ID 26 / OD 41.2 and must
  be axially separated from the ring gear (WA-R9), and the spar stub protrusion
  (32 mm) needs confirming against the final trunnion bearing stations (WA-R12).
  See `docs/WING_ATTACH_INTERFACE.md` §4.

---

## How This Work Fits Together

This is one of four active nacelle plans and it is the only one that is
independently shippable — it touches the nozzle and intake, not the spar,
pivot, or drive:

- **002** (spar, station, airfoil) sets `SPAR_Z`, which this plan's clearance
  budget depends on. Its station move *costs* 3.05 mm of the clearance this
  plan recovers.
- **003** (trunnion pivot, tilt drive) is downstream of 002 and shares the
  nozzle-drive datum with this plan's R2.
- **2026-08-26-001** U5 already scopes the intake refinement; this plan supplies
  the measured conformance defect that U5 was written to investigate, and should
  be reconciled with it rather than duplicating it.

Relationships are stated as currently understood; sequencing is a planning
decision, not settled here.

---

## Sources

- Canonical shell profile, intake blend deviation, and axial budget measured
  2026-08-29 from `airframe/stls/nacelles/eng_left_shell24_50mm_repaired.stl`
  (bore-centred) and the current SCAD parameter block.
- `airframe/openscad/nacelles/nacelle_nozzle_iris.scad` — `HOUSING_OUTER_R`,
  `HOUSING_AFT_R`, and the "deferred VERIFY" note on full ovalising.
- `airframe/wings-nacelles/WBS.md` §1.1.3.1 — Rev T2 flap doubling (20 → 40 mm,
  user direction, swing arc halved) and the Stage 2 taper entry.
- `airframe/FreeCAD-scripts/serenity_assembly.py` L505-518 — the active 1.5 in
  gear variant that sets the ground plane.
- `docs/plans/2026-08-26-001-nacelle-esc-intake-integration-plan.md` U5 — the
  existing intake refinement scope.

---

*Requirements captured by Claude (Claude Sonnet 5, Anthropic) under the author's
direction, 2026-08-29, per `AGENTS.md` AI attribution.*
