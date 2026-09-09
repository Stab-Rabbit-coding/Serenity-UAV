---
title: "Nacelle Mould-Line Conformance and Nozzle Shortening - Plan"
date: 2026-08-29
enriched: 2026-09-08
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
execution: code
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

**Clearance target — settled 2026-08-29, BROKEN 2026-08-31, RESOLVED 2026-09-06
BY A GEAR DECISION. Read this block, then OQ1.**

> **Resolved 2026-09-06 —
> `docs/plans/2026-09-06-001-fix-minimum-safe-landing-gear-leg-length-plan.md`.**
> R3's remaining question ("which gear, and at what margin") is answered there
> and is no longer this plan's to carry. The **3.0 in gear is the flight
> article**; the 1.5 in gear is a non-flight variant, below the derived minimum
> safe belly clearance by 27–40 mm in every case. **R1 (40 → 30 mm flaps) is
> unchanged and still owned here** — but its role changes: with the 3.0 in gear
> fitted, R1 is no longer what makes clearance positive (that is already +33.00 mm
> statically). R1 now buys **attitude margin**, taking the 3.0 in surplus from
> +5.45 mm to +14.37 mm at a 5° touchdown-roll case. That is a promotion in value,
> not a demotion: it is what makes the margin defensible rather than nominal.
> The requirement that survives unchanged is the underlying one — *positive
> clearance with the nacelles vertical, on whatever gear is fitted* — now with a
> derived minimum behind it (`docs/LANDING_GEAR_ANALYSIS.md` §4.8, gated by
> `tools/landing_gear_ground_clearance.py`).

*(Original block, kept for the record:)*

The +9.8 mm figure below rested on `PIVOT_Z` = 116.1, which rested on a
rotating-assembly mass table that estimated the pod shell and both sleeves at
130 g combined. **They measure 339.7 g.** Re-derived from the meshes
(`tools/nacelle_mass_cg.py`, new), the CG — and so the pivot — is **105.8 mm**,
10.3 mm forward of what this plan assumed, and the built `SPAR_Z` is a further
1.57 mm lower than the table that row came from used.

**PARTLY RECOVERED 2026-08-31 (Rev T4b).** Hollowing the pods with a
**forward-biased** wall — owner direction, to move the CG aft on purpose — put
`PIVOT_Z` back to **113.8**, and counting the in-nacelle harness (22.9 g, all of
it aft of the pivot, never carried in any previous roll-up) accounts for part of
that. Where it now stands, measured:

| configuration | `PIVOT_Z` | 1.5 in gear (−38.1) | 3.0 in gear (−80.0) |
|---|---:|---:|---:|
| solid pod, 40 mm flaps *(the failure)* | 105.9 | −10.47 mm **strikes** | +31.43 |
| **hollow pod, 40 mm flaps (built today)** | **113.8** | **−2.55 mm strikes** | +39.35 |
| hollow pod + **this plan's 30 mm flaps** | 112.8 | **+6.41 mm clears** | +48.31 |

So **R1 now finishes the job it could not finish alone** — and equally, the
hollowing could not finish it without R1. Neither lever closes 10.5 mm by
itself; together they clear by 6.41 mm.

**What still needs an owner decision:** +6.41 mm is not the +9.8 mm that was
accepted, and it should not be inherited as though it were. Remaining levers are
KD5's deferred stator compression (~7 mm), aft ballast (17.7 g per nacelle per
4 mm of CG shift), or making the 3.0 in gear mandatory — which clears by 39 mm
today with no further change at all.

This is precisely the failure mode OQ5 was written to catch — "R3 is an
owner-accepted margin and this plan is the last thing that can silently spend
it" — except that what spent it was a mass error upstream, not this plan.

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
- **R3** — ~~Hover ground clearance is **≥ 9.8 mm on the 1.5 in gear**~~
  **CANNOT BE MET AS WRITTEN (2026-08-31).** The measured pivot is 105.8, not
  116.1. **Re-measured 2026-08-31 after the pods were hollowed:** the 1.5 in gear
  is −2.55 mm before this plan's flap trim and **+6.41 mm after it**. R3 must be
  re-decided by the owner as one of: (a) the 3.0 in gear
  becomes mandatory (+31.4 mm today, no other change needed); (b) the stack
  shortens by more than the 10 mm R1 buys — KD5's deferred stator compression is
  the named next lever, worth ~7 mm; (c) aft ballast, at 17.7 g per nacelle per
  4 mm of CG shift and a T/W cost. The requirement that survives untouched is the
  underlying one: **positive clearance with the nacelles vertical, on whatever
  gear is fitted.**
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

- **OQ1 — RESOLVED 2026-09-06 by
  `docs/plans/2026-09-06-001-fix-minimum-safe-landing-gear-leg-length-plan.md`.**
  Not by re-accepting a margin on the 1.5 in gear, but by retiring it: the
  minimum safe belly clearance is derived at **65.5–78.4 mm** and the 1.5 in
  gear's 38.1 mm cannot reach it by any lever on this plan's table. The 3.0 in
  gear is the flight article and carries **+14.37 mm** of surplus at a 5°
  touchdown-roll case once R1's 30 mm flaps land. Residual owner decisions moved
  to **LG-27** (the attitude case itself) and **LG-28** (nozzle strike during a
  full fuse arrest).
- **OQ1 — RE-OPENED 2026-08-31 (superseded by the above).** The resolution below is void: it was accepted
  against a pivot station that a measured mass roll-up does not support. See the
  Clearance target block and R3.
- **OQ1 (superseded text, kept for the record).** +9.8 mm on the 1.5 in gear,
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
- **OQ5 — RESOLVED, THEN VINDICATED 2026-08-31.** The re-verification this item
  demanded was finally run, and it failed. Keeping the original text below,
  because the item did its job.
- **OQ5 (original).** RESOLVED 2026-08-29 by implementation. The spar station move is
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

## Planning Contract

**Product Contract preservation:** unchanged. This enrichment adds execution
detail only; no R-ID, KD, or success criterion is renumbered or reworded.

**Scope for this execution pass:** **R1, R4, and R5 only.** R2 and R6 are
invariants this pass must preserve, not build — U1/U2 verify R2's exit-area
schedule stays fixed; U3/U4 verify R6's Ø50 mm duct stays untouched. **R3 is
resolved and closed** by `docs/plans/2026-09-06-001-fix-minimum-safe-landing-gear-leg-length-plan.md`
(3.0 in gear is the flight article) — do not reopen it here. R7 (residual
deviation documentation) is folded into U8 rather than given its own unit.

**Additional scope beyond the original Product Contract**, added at
implementation time by owner direction (2026-09-08): bake and export the
production STLs (U5), update the 64 % PLA prototype to match (U6), and add a
production↔prototype sync check (U7) so the prototype can't silently drift
from production again — this is the exact failure mode that let the 1.5 in
vs 3.0 in gear deviation and this plan's own R4/R5 deviations sit unnoticed.

**Session-settled decisions (2026-09-08, user-directed):**
- **RSSR linkage re-verification (OQ2) is closed by building a reusable check
  tool**, not a one-off manual FreeCAD pass and not left open. *(session-settled:
  user-directed — chosen over "manual FreeCAD, documented" and over "flag as
  open, don't block R1": a script becomes a standing gate future flap-length or
  hinge changes can re-run, rather than a fact that ages out of memory.)*
  Governs U2.
- **The sync mechanism (U7) is a staleness check that fails until regenerated,
  not an auto-regenerating hook.** *(session-settled: user-directed — chosen
  over full auto-regenerate in the hook: full PLA regeneration needs
  OpenSCAD + FreeCAD + Cura, and a hook that silently spends minutes per commit,
  or fails outright on a machine missing one of those tools, is worse than one
  that names the drift and points at a `make` target.)* Governs U7. This mirrors
  the repo's own existing `index-check` CI job, which verifies and does not
  write back for exactly this reason (see `.github/workflows/ci.yml`).

**Reused, not re-derived (from repo research):**
- Part-local→hull transform: `R_BAKE` / `T_BAKE["port"|"stbd"]` in
  `airframe/FreeCAD-scripts/serenity_assembly.py` (`nacelle_rows()`, ~line 315),
  sourced from `tools/bake_hull_frame.py`'s `COMPONENTS` table — this answers
  OQ3 (the transform exists and is already measured-verified; no new transform
  needed for R4).
- Station-sampling pattern: `tools/nacelle_hollow_profile.py` already ray-casts
  the canonical shell STL station-by-station and emits an `include`d SCAD
  profile (`nacelle_hollow_profile.scad`, consumed by
  `nacelle_pod_50mm_tandem.scad` line ~708). U3 and U4 extend this pattern
  rather than inventing a new one.
- Bake tool contract: `tools/bake_hull_frame.py` — "any STL published to
  `airframe/stls/` for one of the components listed in `COMPONENTS` MUST be
  passed through this tool after regeneration" (its own docstring). U5 follows
  this literally.
- Existing hook convention: `.githooks/pre-commit` runs
  `precommit_kicad_load.py` → `precommit_sanitize.py` → `precommit_index.py`,
  each regenerating-then-`git add`-ing its own artifact. U7's check step is
  appended to this same script, but as a **check**, not a regenerate-and-add
  step, per the settled decision above.
- Mesh-repair precedent: `docs/solutions/logic-errors/mating-face-aperture-allowlist.md`
  (watertight ≠ defect-free; probe multiple points, not one centroid) and
  `docs/solutions/runtime-errors/curaengine-hangs-on-overlapping-mesh-faces.md`
  (self-union via `manifold3d` fixes overlapping-face CuraEngine hangs even on
  a mesh `trimesh` already reports watertight) — both apply to U5/U6's
  validation and print-slicing steps.

---

## Implementation Units

### U1. Trim nozzle flap length 40 → 30 mm

**Goal:** Land R1 — change `FLAP_LENGTH` and confirm the exit-area schedule
(R2/R6) does not move.

**Requirements:** R1, R2 (preserve), R6 (preserve)

**Dependencies:** none

**Files:**
- `airframe/openscad/nacelles/nacelle_nozzle_iris.scad` (line 318
  `FLAP_LENGTH`; lines 328-329 derived `PHI_CLOSED`/`PHI_OPEN` recompute
  automatically)

**Approach:**
- Change `FLAP_LENGTH = 40.0;` to `30.0;`. Update the adjacent header comment
  (lines 56-65) that quotes 40 mm and the old PHI values, so the source
  comment doesn't go stale the way `INTAKE_BLEND_L`'s hardcoded `60` did.
- Do **not** touch `NOZZLE_CLOSED_R` (18.75) or `NOZZLE_OPEN_R` (26.25) — R2/R6
  fix the exit-area schedule; only the flap geometry solving for it changes.
- Confirm via `openscad --hardwarnings` that both derived-angle renders
  (`-D 'FLAP_PHI=PHI_CLOSED'` and `-D 'FLAP_PHI=PHI_OPEN'`, the Makefile's
  existing pattern for `nacelle_nozzle_iris-closed.stl` / `-open.stl`) still
  produce a single watertight body.

**Patterns to follow:** the Makefile's existing `-D 'FLAP_PHI=...'` variant
render pattern (`airframe/FreeCAD-scripts/Makefile`).

**Test scenarios:**
- Rendering at `PHI_CLOSED` (new value ≈16.96°) produces a single watertight
  flap body with exit-boundary min radius unchanged from the 40 mm case
  (18.75 mm target, same tolerance as the WBS's prior 16.311 mm/35.600 mm
  verification for the flap-shingle change).
- Rendering at `PHI_OPEN` (new value ≈2.39°) likewise produces exit radius
  26.25 mm.
- `grep` confirms `NOZZLE_CLOSED_R`/`NOZZLE_OPEN_R` are byte-identical to
  before the change.

**Verification:** both derived-angle STLs render cleanly under
`--hardwarnings`; exit radii match the 75 %/105 % bore targets to the
precision the existing WBS verification used.

---

### U2. Nozzle pushrod linkage reachability check (closes OQ2)

**Goal:** Build a reusable tool that proves the RSSR pushrod linkage
(`nacelle_nozzle_pushrod.scad`) stays monotonic and non-locking across the
0–90° tilt range at the new, wider swing arc, closing OQ2 rather than
carrying it forward again.

**Requirements:** R2 (linkage still reaches both end stops)

**Dependencies:** U1 (needs the new `PHI_CLOSED`/`PHI_OPEN`)

**Files:**
- `tools/nozzle_linkage_check.py` (new)
- `airframe/openscad/nacelles/nacelle_nozzle_pushrod.scad` (read-only source of
  `CRANK_R` = 8.5 mm and the ring-lever rotation range 0..23.75°; add a
  one-line comment pointing at the new checker if the file's header VERIFY
  note needs updating once this closes)

**Approach:**
1. Model the RSSR linkage's crank/rod/ring-lever geometry from the constants
   already in `nacelle_nozzle_pushrod.scad` (mirror them into the tool with an
   explicit "source of truth: <file>:<line>" comment, per this repo's existing
   convention in `tools/landing_gear_ground_clearance.py` for `PIVOT_Z`
   provenance — do not silently duplicate a magic number).
2. Sweep tilt 0→90° at a fine step (e.g. 1°), solve the crank angle → ring
   angle mapping, and assert it is monotonic and that no sample requires a rod
   length outside the physically buildable range (RSSR triangle-inequality
   failure = locking).
3. Run the sweep at both the old `FLAP_LENGTH=40` derived angles (regression
   check — the tool must reproduce the previously-accepted geometry) and the
   new `FLAP_LENGTH=30` derived angles from U1.
4. Exit non-zero with the offending tilt angle on any failure; exit 0 with a
   pass summary otherwise.

**Patterns to follow:** `tools/landing_gear_ground_clearance.py`'s
sweep-and-assert structure and its explicit-provenance-comment convention for
constants copied from SCAD source.

**Test scenarios:**
- 0–90° sweep at `FLAP_LENGTH=40` (regression) passes — confirms the tool
  matches previously-accepted geometry before trusting it on the new case.
- 0–90° sweep at `FLAP_LENGTH=30` (this plan's target) passes with no locking
  angle found.
- A deliberately-shortened synthetic `FLAP_LENGTH` (e.g. 15 mm, chosen to
  produce an out-of-range swing per the plan's own rejected-20mm-option
  reasoning) is asserted to **fail** the check — proves the tool actually
  detects a locking condition and isn't vacuously passing.

**Verification:** `python3 tools/nozzle_linkage_check.py` exits 0 for
`FLAP_LENGTH=30`; the synthetic failure case exits non-zero naming the
offending tilt angle.

---

### U3. Ovalise the nozzle housing to the canonical cowl mould line

**Goal:** Land R4 — replace the uniform cylindrical taper
(`HOUSING_OUTER_R`→`HOUSING_AFT_R`) with a station-sampled radius that tracks
the canonical shell, closing the WBS's "[OPEN — VERIFY] Full housing
ovalization" item and OQ3.

**Requirements:** R4, R6 (preserve — bore untouched)

**Dependencies:** none (parallel to U1/U2)

**Files:**
- `tools/nacelle_housing_profile.py` (new — station sampler)
- `airframe/openscad/nacelles/nacelle_housing_profile.scad` (new — generated
  `include`, same pattern as `nacelle_hollow_profile.scad`)
- `airframe/openscad/nacelles/nacelle_nozzle_iris.scad` (lines 499-560 —
  consume the generated profile instead of the two-point taper)

**Approach:**
1. Extend the `tools/nacelle_hollow_profile.py` ray-cast pattern: for each
   axial station across the housing's extent (from the ring/lip start to the
   aft face), transform the nacelle-local station into hull frame using
   `serenity_assembly.py`'s `R_BAKE`/`T_BAKE["port"]` (do not re-derive this
   transform — it's already measured-verified, per Planning Contract above),
   then ray-cast the canonical shell
   (`airframe/stls/nacelles/eng_left_shell24_50mm_repaired.stl`) at that hull
   station to get the canonical max radius.
2. Emit a station→radius table as an `include`d SCAD profile
   (`nacelle_housing_profile.scad`), mirroring
   `nacelle_hollow_profile.scad`'s output shape.
3. In `nacelle_nozzle_iris.scad`, replace the `HOUSING_OUTER_R`/`HOUSING_AFT_R`
   two-point `cylinder(...)`/`hull()` taper (lines ~552-560) with a
   `rotate_extrude` or lofted solid built from the station profile, holding a
   documented margin inboard of the canonical radius at every station (not
   flush — flush invites the next repaired-mesh revision to go proud again).
   Include the hinge bosses (~Ø69.4 mm envelope) in the same per-station check
   — the plan's original measurement flagged them as a second binding
   constraint, not just the outer ring.
4. Update the WBS §1.1.3 line (~925) from "[OPEN — VERIFY]" to closed, citing
   this unit.

**Patterns to follow:** `tools/nacelle_hollow_profile.py` (ray-cast + emitted
profile) and its consumption in `nacelle_pod_50mm_tandem.scad` line ~708.

**Test scenarios:**
- At every sampled station across the housing's axial extent, the generated
  housing radius is ≤ the canonical shell radius at the corresponding hull
  station, minus the documented margin — zero proud points (replacing the
  plan's measured 3.2 mm→3.9 mm proud condition).
- The hinge-boss envelope is checked against the canonical radius at its own
  station and found non-proud.
- `THROAT_INNER_R`/`THROAT_OUTER_R` (the Ø50 mm-derived bore) are confirmed
  byte-identical before/after — R6 invariant.
- Rendering the modified housing under `--hardwarnings` still produces one
  watertight body.

**Verification:** `tools/nacelle_housing_profile.py --check` (or equivalent
flag) reports 0 stations proud of the canonical shell; manifold render passes.

---

### U4. Conform the intake fairing to the canonical dome (retire the Z90 blend)

**Goal:** Land R5 — replace the `INTAKE_BLEND_R_PEAK`/`INTAKE_BLEND_L`
construction (including its hardcoded absolute-station `60` split, found in
the blend math at `nacelle_pod_50mm_tandem.scad` lines ~865-887) with a fair
curve that follows the canonical dome's most convex line at Z0 and is tangent
to the canonical mould line by Z≈30, per OQ4's owner-resolved direction.

**Requirements:** R5, R6 (preserve — duct untouched)

**Dependencies:** none (parallel to U1/U2/U3); may reuse U3's
station-sampling tool rather than duplicating it

**Files:**
- `airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad` (lines ~618-621
  named constants; lines ~865-887 blend math, including the hardcoded `60`)
- `tools/nacelle_housing_profile.py` (extend to also sample the dome/intake
  region, or add a sibling function — implementer's call at execution time
  depending on how much the housing and intake sampling actually share)

**Approach:**
1. Sample the canonical dome's radius at Z 0→30 (already measured once in the
   Product Contract's table: 22.2→28.0→31.5→34.3→36.3→38.1→38.4, rising
   monotonically to Z≈30 then falling) to confirm the exact monotonic limit
   against the current mesh rather than trusting the earlier hand-measured
   table verbatim.
2. Construct a new fair curve (not a point-fit to the noisy repaired mesh —
   OQ4 is explicit about this) that starts at the lip radius at Z0 following
   the dome's most convex line, and is tangent (radius **and** slope match) to
   the canonical mould line at the monotonic limit found in step 1.
3. Replace the `rise_frac`/`fall_frac` construction and its hardcoded `60`
   with the new curve, removing `INTAKE_BLEND_R_PEAK`/`INTAKE_BLEND_L` if they
   are no longer meaningful parameters (name their replacements clearly rather
   than reusing the old names for a different curve shape).
4. Leave `EDF_BORE_R`/`INTAKE_LIP_R`'s duct-facing dimensions untouched — R6.

**Patterns to follow:** U3's station-sampling approach; the Product Contract's
own measured table as the acceptance baseline.

**Test scenarios:**
- At every sampled Z from 0 to the monotonic limit, the new blend radius is ≤
  the canonical dome radius at that station (replacing the plan's measured
  +5.3 mm proud condition at Z0 and the crossing near Z7).
- Tangency at the blend's terminus: radius and local slope both match the
  canonical mould line within a documented tolerance.
- `EDF_BORE_R` and the duct-facing lip dimensions are confirmed unchanged
  before/after — R6 invariant.
- Manifold render passes under `--hardwarnings`.

**Verification:** station-sampling check (shared with or sibling to U3's)
reports 0 proud points from Z0 to the monotonic limit; tangency check passes;
manifold render passes.

---

### U5. Bake and export production nacelle STLs

**Goal:** Turn U1/U3/U4's SCAD changes into the production STL set, correctly
baked and validated.

**Requirements:** R1, R4, R5 (materialize as shippable geometry)

**Dependencies:** U1, U2 (gate — do not export a flap geometry whose linkage
hasn't passed), U3, U4

**Files:** `airframe/stls/nacelles/*.stl` (regenerated output only; no source
changes in this unit)

**Approach:**
1. `make stls` (from `airframe/FreeCAD-scripts/`) to re-render the
   OpenSCAD-sourced parts touched by U1/U3/U4 (nozzle iris, housing, pod
   intake).
2. Re-bake the nacelle pod placement: `python3 tools/bake_hull_frame.py
   Nacelle_Port` (and `Nacelle_Stbd` if it's a mirrored bake rather than a
   derived mirror) — mandatory per that tool's own docstring for any STL
   touching the baked component set.
3. `make assembly` (runs `freecadcmd serenity_assembly.py`) to confirm the
   updated sub-component placements still compose correctly against the newly
   baked pod.
4. Export/refresh `nacelle_port_revs.stl` and its starboard/mirror
   counterpart.
5. `python tools/validate_stls.py` — must pass (watertight or all split
   sub-bodies watertight). If it reports a defect `is_watertight` alone
   wouldn't catch (per the mating-face-aperture-allowlist learning), spot the
   intake/housing seams specifically, since those are exactly the surfaces
   this plan just modified.

**Patterns to follow:** `tools/bake_hull_frame.py`'s own "MUST be passed
through this tool after regeneration" contract; the existing `stl-validate`
CI job as the acceptance bar.

**Test scenarios:**
- `tools/validate_stls.py` passes for every regenerated nacelle STL.
- `tools/bake_hull_frame.py --check` passes (bake marker present, matches
  measured pivot).
- `make assembly` completes without error and the resulting FreeCAD assembly
  shows no new interference at the housing/hinge-boss or intake/dome seams
  (visual spot-check, since this is exactly where U3/U4 moved geometry).

**Verification:** `tools/validate_stls.py` exit 0; `bake_hull_frame.py --check`
exit 0; facet-count/volume deltas recorded in the commit message for
traceability (mirroring the WBS's existing practice of recording exact facet
counts for flap-shingle-style changes).

---

### U6. Update the 64 % PLA prototype

**Goal:** Bring the FDM prototype's nacelle geometry into line with U1/U3/U4's
production changes, respecting the print guide's existing non-uniform scale
policy.

**Requirements:** consistency between production and prototype (new scope,
owner-directed 2026-09-08)

**Dependencies:** U5

**Files:**
- `docs/PROTO_PRINT_DAVINCI_JR.md` (§3 scale policy, §4 per-part notes —
  update measured dimensions for the changed nacelle parts)
- Prototype STL/gcode outputs under `airframe/gcode/davinci-jr-proto/`
  (regenerated on demand per the doc's existing convention — confirm at
  execution time whether these are committed or purely local build products;
  do not change that convention as a side effect of this unit)

**Approach:**
1. Re-run `airframe/gcode/davinci-jr-proto/cura/slice_all_batches_cura.py`
   for the affected batches (nozzle/housing/intake-bearing parts), using its
   existing `mesh_repair.py` self-union step for any part that hits the
   documented overlapping-face CuraEngine hang.
2. **Do not force a uniform scale.** The print guide's 64 % hull scale and the
   nacelle pods' separate 89 % bed-fit scale are both intentional per §3/§4 —
   preserve that split; only the *geometry* changes, not the scale policy.
3. Update §4's per-part notes and any measured dimensions in the guide that
   reference the old flap length, housing OD, or intake profile.

**Patterns to follow:** the guide's own "regenerated on demand, not committed"
convention (confirm still current) and its documented non-uniform scale
policy — do not silently unify it.

**Test scenarios:**
- Re-slicing the affected batches completes without the previously-documented
  overlapping-face CuraEngine hang (Test expectation: exercises the
  `mesh_repair.py` path if the new housing/intake geometry reintroduces
  coincident faces).
- The print guide's updated dimensions match the new SCAD parameters
  (`FLAP_LENGTH=30`, new housing/intake profiles) at both scale factors it
  actually uses (64 % hull, 89 % pod).

**Verification:** slice run for affected batches exits cleanly; guide diff
reviewed for consistency with U1/U3/U4's parameter changes.

---

### U7. Production↔prototype sync check (hook + CI)

**Goal:** Prevent the prototype from silently drifting from production again,
via a staleness check — not an auto-regenerating hook (session-settled,
Planning Contract above).

**Requirements:** new scope, owner-directed 2026-09-08

**Dependencies:** U6 (the manifest's initial "synced" state should reflect
U6's completed update, not a pre-U6 state)

**Files:**
- `tools/precommit_prototype_sync.py` (new)
- `.githooks/pre-commit` (append a new step, following the existing
  `precommit_kicad_load.py` → `precommit_sanitize.py` → `precommit_index.py`
  chain — but this new step **checks and fails**, it does not regenerate and
  `git add`, per the settled decision)
- `.github/workflows/ci.yml` (new job, e.g. `prototype-sync-check`, mirrored
  on the existing `index-check` job's verify-only pattern — `needs: lint`)
- A tracked manifest recording which production sources (SCAD files feeding
  the nacelle STLs, plus the baked STL hashes) the prototype was last
  regenerated against (new file, e.g.
  `airframe/gcode/davinci-jr-proto/.prototype-sync-manifest.json`)

**Approach:**
1. Define the tracked production source set: the nacelle SCAD files
   (`nacelle_nozzle_iris.scad`, `nacelle_nozzle_pushrod.scad`,
   `nacelle_pod_50mm_tandem.scad`, plus any new files U3/U4 add) and the baked
   STLs they produce.
2. `precommit_prototype_sync.py` computes a content hash of the tracked set
   and compares it against the manifest. On mismatch: **fail the commit** with
   a message naming the changed files and the `make`/script target that
   regenerates the prototype and updates the manifest (mirroring
   `index-check`'s "DELIBERATELY NOT AUTO-COMMITTING" rationale — a hook that
   silently rewrites a hash file the developer didn't ask to touch is its own
   footgun).
3. The same check runs in CI as `--check`, exactly like
   `tools/precommit_index.py --check` does for the index files — verify only,
   never write back, for the reason already documented in that job's
   comments.
4. Manifest is updated (hash recorded) as part of completing U6, so this
   unit's initial state is "in sync," not "immediately red."

**Patterns to follow:** `.githooks/pre-commit`'s existing chain structure;
`tools/precommit_index.py` / the `index-check` CI job as the direct template
for the hook-checks-locally / CI-checks-again split.

**Test scenarios:**
- Touching a tracked production SCAD file without updating the manifest →
  local pre-commit hook fails with an actionable message.
- Manifest updated to match → hook passes.
- A PR that changes tracked nacelle sources without updating the manifest →
  the `prototype-sync-check` CI job fails; updating the manifest in the same
  PR makes it pass.
- A change to an untracked file (e.g. an unrelated fuselage SCAD) does not
  trip the check — proves the tracked-set scoping isn't over-broad.

**Verification:** all four scenarios above reproduced locally and via a test
CI run (or a documented dry-run trace if a live CI run isn't practical during
implementation).

---

### U8. Close out residual documentation (R7)

**Goal:** Record what changed and what, if anything, remains an accepted
deviation, closing the loop R7 requires.

**Requirements:** R7

**Dependencies:** U1–U7 (this unit summarizes their outcome)

**Files:**
- `airframe/wings-nacelles/WBS.md` (close the "[OPEN — VERIFY] Full housing
  ovalization" line and the intake-fairing item; update `NAC-MOULD-01`)
- This plan file (no rewrite of the Product Contract — append a short closing
  note under Sources, or a new "Outcome" subsection, stating final measured
  values)

**Test expectation:** none — documentation-only unit.

**Verification:** WBS entries for the three deviations this plan targeted
(overhang/flap length, housing proud amount, intake proud amount) each show a
closed status with the measured post-fix values, or an explicit residual
deviation with its accepted magnitude and reason (R7's actual requirement —
some residual overhang is expected and was never meant to reach zero, per the
Problem Frame's axial-budget argument).

---

## Verification Contract

- U1: both derived-angle nozzle renders watertight; exit radii match 75 %/105 %
  bore targets; `NOZZLE_CLOSED_R`/`NOZZLE_OPEN_R` unchanged.
- U2: `tools/nozzle_linkage_check.py` passes at `FLAP_LENGTH=30`, reproduces
  the accepted result at `FLAP_LENGTH=40`, and correctly fails a synthetic
  locking case.
- U3: 0 stations proud of the canonical shell across the housing and hinge
  bosses; bore dimensions unchanged; manifold render passes.
- U4: 0 stations proud of the canonical dome from Z0 to the monotonic limit;
  tangent at the terminus; duct dimensions unchanged; manifold render passes.
- U5: `tools/validate_stls.py` and `tools/bake_hull_frame.py --check` both
  pass on the regenerated nacelle STLs; `make assembly` completes clean.
- U6: affected print batches re-slice without the documented CuraEngine hang;
  print guide dimensions match the new geometry at both scale factors in use.
- U7: sync check fails on a genuine staleness case and passes once the
  manifest is updated, both locally (hook) and in CI.
- U8: WBS shows closed status or an explicit, reasoned residual deviation for
  each of the three original findings.

## Definition of Done

1. `FLAP_LENGTH = 30.0` in `nacelle_nozzle_iris.scad`, with the exit-area
   schedule (R2/R6) provably unchanged (U1).
2. The RSSR pushrod linkage's non-locking behavior at the new swing arc is
   proven by a checked-in, re-runnable tool, not a one-time manual check (U2).
3. No point of the nozzle housing, its hinge bosses, or the intake fairing
   stands proud of the canonical shell at any sampled station, except a
   documented residual overhang consistent with the Problem Frame's axial
   budget (U3, U4, U8).
4. Production STLs under `airframe/stls/nacelles/` reflect all of the above,
   baked and validated (U5).
5. The 64 % PLA prototype's nacelle geometry matches production, without
   flattening the print guide's intentional non-uniform scale policy (U6).
6. A production↔prototype staleness check exists, fails on genuine drift, and
   passes once resynced — in both the local hook and CI (U7).
7. WBS/plan documentation reflects the closed and residual state accurately
   (U8).

---

*Requirements captured by Claude (Claude Sonnet 5, Anthropic) under the author's
direction, 2026-08-29, per `AGENTS.md` AI attribution. Enriched to
implementation-ready by Claude (Claude Sonnet 5, Anthropic), 2026-09-08, per
`AGENTS.md` AI attribution.*
