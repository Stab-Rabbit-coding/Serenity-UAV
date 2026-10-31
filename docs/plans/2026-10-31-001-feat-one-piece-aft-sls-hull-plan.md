---
title: One-Piece Middle+Rear SLS Hull for Aft-CG Recovery - Plan
date: 2026-10-31
artifact_contract: ce-unified-plan/v1
artifact_readiness: requirements-only
product_contract_source: ce-brainstorm
license: CC-BY-SA-4.0
---

# One-Piece Middle+Rear SLS Hull for Aft-CG Recovery - Plan

**AI note:** Drafted by Claude Opus 5.5 (Anthropic) under the direction of Steve Griffing
(Stab-Rabbit-coding). This is a requirements-only plan: it records what the build must
achieve, not how to build it.

> **ENGINEERING REVIEW REQUIRED.** Every figure here must be reviewed and accepted by a
> qualified engineer before it is applied to any system carrying risk to life or safety.

## Goal Capsule

- **Objective:** Bring the hover CG to the thrust line, within the trim band. Do it by
  printing the middle and rear fuselage sections as **one** lighter SLS part. Keep the
  single tilt pivot and the current proportions.
- **Product authority:** Owner, Steve Griffing. Decisions dated 2026-10-31.
- **Open blockers:** Gates G1–G3 below.
- **Not active scope:** Head and cargo sections (except where they meet this part),
  wing material, nacelle changes, and any change to scale.

## Product Contract

### Problem

The relocated hover CG is **+16.6 mm (0.65 in)** aft of the pivot (Y 326.7). That figure
uses the 2300KV ledger: AUW 6,310 g (13.9 lbm), merge commit `ea00da21`. The rear and
middle shell skins cause about 85% of the net aft moment
(`docs/ideation/2026-10-31-aft-cg-single-pivot-options-ideation.md` §2).

### Requirements

- **R1.** The middle and rear sections shall be one printed part. The collar at Y 509
  shall be deleted.
- **R2.** The part shall be printed in SLS DuraForm PA CF [3DS-30108A]. That material
  matches the CF-PETG flexural modulus: 7,000 vs 6,670 MPa (1,010 vs 967 ksi).
- **R3.** The horseshoe ring shall remain a **printed frame, integral with the shell**.
  The skids shall continue to attach to it and react through it. *(session-settled:
  owner, 2026-10-31)*
- **R4.** The wall shall be graded by station. The 2.0 mm wall shall be kept at the skid
  channels, the ring, the collar land at Y 436, the horseshoe legs and the hatch frame.
  Away from those features the wall shall be thinner and rib-stiffened.
  - Mass target: rear at ≤50% and middle at ≤70% of the current shells, which are
    231.5 g and 183.1 g.
  - A rib frame with a film skin may be used aft of the ring if it passes G2.
- **R5.** There shall be one tilt pivot. It shall be moved 0.5 in (12.7 mm) aft, per the
  existing plan. *(session-settled: owner rejected indexed or multiple pivots,
  2026-10-31)*
- **R6.** Fuselage proportions and the outer mold line shall not change.
  *(session-settled: owner, 2026-10-31)*
- **R7.** Trim shall come from the battery-rail slack (about ±2.2 mm) plus a nose ballast
  pocket (about 0.050 mm of CG per gram).
- **R8.** The hull re-cut shall be rebuilt from the owner's OpenSCAD/Blender sources. It
  shall not be made by patching the published STLs.

### Success Criteria

- **S1.** Hover CG offset within the trim band. Expected: +1.6 mm with the graded skin,
  −0.7 mm with ribs and film.
- **S2.** The ring, skids and joint at Y 436 survive the plan 001 R7 crash case (79.4 g)
  with the factor of safety the repo requires. The joint loads at 24 in are 645 N
  (145 lbf) shear and 46.9 N·m (415 lbf·in) bending
  (`docs/SLS_27IN_TWO_SECTION_TRIM_STUDY.md`).
- **S3.** The 4-section → 2-section change does not move the hull's center of mass by
  more than the ledger accounts for. The ledger is regenerated from the new mesh.

### Gates (open)

- **G1.** Weigh one printed CF-PETG shell. That settles 1.05 vs 1.28 g/cc and the actual
  baseline mass.
- **G2.** Stiffness and drop check of the thinned wall and the ring frame. Allowables come
  from 3D Systems PA CF data. That data is XY-only, so the Z-direction values need a
  coupon or a vendor answer.
- **G3.** Derive the trim band from the pitch control moment. The ±6.4 mm working target
  is not derived.

### Outstanding Questions

- Does the part fit a vendor's SLS build envelope? The part is about 11 in long
  (Y 436 → about 700) and has not been checked against any vendor's machine.
- Film material and durability, if ribs and film are chosen for the rear.

### How This Work Fits Together

Additive with the FE chin and shuttle split (`docs/plans/2026-10-28-001`, about −2.6 mm).
If both proceed, the CG goes forward of the pivot and the nose ballast pocket is reduced.
