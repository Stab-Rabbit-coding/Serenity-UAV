---
title: SLS Material, 30 in Scale and Single-Piece Hull — Brainstorm Informed by Weight-and-Balance and Joint Plans
type: brainstorm
date: 2026-10-31
status: draft
companion: docs/SLS_PA12_30IN_SINGLE_PIECE_EVALUATION.md
---

# SLS Material, 30 in Scale and Single-Piece Hull — Brainstorm

> **SUPERSEDED IN PART (2026-10-31).** See `docs/SLS_27IN_TWO_SECTION_TRIM_STUDY.md`. The 36 in study cited here dates from 2026-09-28 and is stale (AUW, stacking and T/W inputs predate the 10-19 to 10-27 ledger, envelope and CG work). The T/W 'open conflict' below is resolved: 0.98–1.01 is the stale figure; current is 1.35–1.37. The 30 in and single-piece conclusions are replaced by a 27 in, two-section recommendation.


**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)

> ⚠️ **ENGINEERING REVIEW REQUIRED.** Screening ideas only. A qualified engineer shall review
> any number here before it drives a purchase or a flight-article change.

Labels: **[REPO]** from a repo document (cited). **[CALC]** my arithmetic on repo figures.
**[ASSUMED]** my assumption, needs verification.

## 1. What the repo already says (inputs read)

| Source | What matters here |
|---|---|
| `docs/CG_RELOCATION_STUDY.md` | Hover CG is **+16.3 mm (0.64 in) aft** of the thrust line (tilt pivot, Y 326.7 mm) after the rail lever, AUW 13.74 lbm (6,232 g). CG spread across payload and third cell is only 0.7 mm. No equipment relocation remains at a 2 mm gap. Closing it needs nose ballast (326 g, rejected: T/W 1.37 to ~1.30), a **pivot move of ~23 mm (0.91 in) aft**, or mass cut aft of the pivot. |
| `docs/plans/2026-10-26-001-feat-split-battery-head-rail-plan.md` | A rail carries the head cell and cargo cell through the head/cargo collar. Head cell loads through the open cargo doors. Catch design load **79.4 g**. Third cell optional. |
| `docs/plans/2026-10-26-003-feat-mass-diet-two-sortie-plan.md` | Goal: cut **555 g** (6,318 to 5,763 g). KD4: **keep 2 mm shells**. Endurance scales ~mass^-1.5. Retrieval sortie is an unmet requirement (R9) behind a propulsion decision gate (R10). |
| `docs/plans/2026-10-03-002-feat-exhaustive-joint-analysis-plan.md` | Joint audit rules: R1 pair census generates the interface list; R3 fixes flow through **shared parameters only**; R4 port/starboard desync over 0.5 mm fails; R5 non-printed parts and air paths are solids; R6 motion is swept. Gate: no CLASH, DESYNC, unregistered interface, or GAP. |
| `docs/solutions/design-patterns/build-every-joint-in-context-through-its-full-motion.md` | Parameter checks passed while assembled meshes clashed (five defects at the tilt joint). Verify in context. |
| `airframe/fuselage-joints/WBS.md` | Head/cargo joint pins are **alignment dowels only**; positive-stop-by-pin-depth is "not achieved as-baked" (measured engagement 2.0 / 12.5 mm dorsal, 2.0 / 3.5–4.5 mm flank). The bonded West System lap carries the joint. `AGENTS.md` §7 still demands a 2-wall annulus plus a positive-stop shoulder. |
| `current-specification/auw_ledger.json` | Printed parts total 1,639.5 g; four hull shells 902.1 g; three splice collars 41.7 g (11.5 + 15.8 + 14.4). |

## 2. Findings that change the earlier evaluation

**F1. Scaling does not fix the CG offset; it scales it.** If every station grows 1.25×, the
+16.3 mm offset becomes about **+20 mm (0.80 in)** and the pivot move about **29 mm (1.14 in)**
[CALC, assumes geometric similarity]. Extra room lets you place items, but the study found every
heavy aft item is tied to structure or function, so room alone buys little CG.

**F2. 30 in cancels the mass diet unless SLS pays for it.** Endurance factor
((AUW + Δ)/AUW)^-1.5 on 6,232 g [CALC]:

| Case (hull shell only, k² scaling) | Δ hull mass | Endurance change |
|---|---|---|
| 24 in, SLS PA12 (×0.79) | −190 g | **+4.7%** |
| 24 in, SLS PA12-CF (×0.86) | −126 g | +3.1% |
| 30 in, CF-PETG | +507 g | **−11%** |
| 30 in, SLS PA12 | +211 g | −4.9% |

The −190 g is a third of the 555 g diet target, with no change to the 2 mm shell (KD4).
It is the largest single item I can see that the diet plan does not already list. The
all-printed-parts figure (−230 to −344 g) is an **upper bound**: infilled parts print at
~1.05 g/cc as-printed [REPO], barely above PA12's 1.01, so the real saving is in the
perimeter-only shells.

**F3. Trim is a mass-times-arm problem, and the arm is the nose.** One gram at the nose
(about 312 mm ahead of the pivot) moves the CG ~0.05 mm; 16.3 mm needs ~326 g, matching the
study [CALC]. So post-build adjustment in grams is fine-grained at the ends and coarse near the
pivot. Design the trim pockets at the ends.

**F4. A single piece deletes joints the audit has trouble proving.** It removes three splice
collars (41.7 g), the bonded laps, and the dowel-only pins. But the head cell loads through
the cargo doors and rides a rail through the head/cargo collar, so a one-piece hull needs
the rail to become a printed-in or bonded-in structure instead of a pass-through.

**F5. Scaling is a joint-audit event.** Every Blender-baked mesh, the datum R2 Y 326.7 spar
station, the layout stations and the 64 mm nacelle bake would change. Per the joint plan R3/R4,
scale must come from **one shared parameter**, or port and starboard parts desync.
Procured parts do not scale (EDF 64 mm, cells 116 × 34 × 38.5 mm, PCBs), so free volume
grows ~1.95× (4,892 to ~9,550 cm³ [CALC]) while the equipment stays the same size.

## 3. Idea space

### 3.1 Weight and balance after the build

1. **Printed ballast pockets at the extremes.** Nose and tail pockets with captive lugs, sized
   to take 0–300 g of tungsten putty or steel slugs. Cheap in SLS; closes the sign problem
   of "add mass only at the nose".
2. **Make the rail the trim axis.** The rail lever already gave ~78,000 g·mm. A rail with a
   graduated stop (detent every 5 mm) turns a 321 g cell into ~0.05 mm CG per mm of travel
   [CALC: 321/6232]. Needs the 79.4 g catch to hold at every detent.
3. **Weigh-and-balance datums printed in.** Knife-edge or load-cell bosses at known Y on a
   fixture, so every build is weighed the same way and logged against `auw_ledger.json`.
4. **Pivot-move option.** Print the spar carry-through with two selectable pivot stations
   (baseline and +23 mm aft) so the 23 mm move can be tested without a new hull. Touches the
   tilt actuators and wing-root flanges, so it ties to joint rows.
5. **SLS lattice for stiffness without mass.** Lattice cores in frames; only if a vendor
   confirms powder evacuation. [ASSUMED]
6. **Mass-removal trim.** Print sacrificial tabs on aft parts that can be cut back in
   fractions of a gram.

### 3.2 Joint audit with SLS

1. **Print the positive stop.** SLS prints undercuts and shoulders that FDM could not.
   A stepped or dovetail splice with a real shoulder would close the `AGENTS.md` §7 gap the
   dowel pins leave open. [ASSUMED: needs a tolerance coupon]
2. **Bond quality is unproven.** The current joint is a West System lap on CF-PETG. Whether it
   bonds to PA12 well, and with what surface prep, is unverified. Coupon-test before any
   hull print.
3. **Inserts and threads.** Heat-set inserts and self-tapping holes in SLS nylon behave
   differently from CF-PETG. Add each type as a register row.
4. **Re-run the census on any scaled or reprinted set.** Steps 1–3 of the joint plan (export,
   pair census, coverage) must pass with no CLASH or DESYNC before release.
5. **Shell tolerance budget.** Measure shrink and warp on a long thin print. A 30 in, 2 mm
   hull will warp more than a 6 in coupon. Joint clearances come from that measurement.
6. **One shared scale parameter.** Add a single hull-scale constant read by the assembly,
   the layout stations and the joint register, so no part is scaled by hand.

### 3.3 Options to compare

| Option | Summary | Pros | Cons |
|---|---|---|---|
| A | 24 in, SLS PA12/PA12-CF, sections, rail trim | −126 to −190 g; no joint-audit reset | no extra volume |
| B | A plus printed ballast pockets and a pivot-station option | closes trim without a hull change | pivot move reworks spar carry-through |
| C | ~27 in, SLS, sections | some room; smaller mass and audit hit | still a full re-baseline |
| D | 30 in, SLS, 2–3 sections | most room | +211 g, endurance −4.9%, full re-baseline, CG offset grows |
| E | 30 in, one piece | fewest joints | does not fit common machines; kills the open-section access and the rail pass-through |

**Leaning:** A, then B. Revisit C/D only after the R10 propulsion gate and a thrust-stand
result. Option E is out unless a 1,000 mm-class US bureau appears.

## 4. Questions for the owner

1. Is the 30 in goal driven by **volume** or by **trim authority**? Volume and trim are
   separate problems; the rail and ballast ideas address trim without growing the hull.
2. Is dropping CF-PETG (`AGENTS.md` §7) acceptable, and for which parts?
3. Does KD4 (keep 2 mm shells) still hold if SLS vendors recommend thicker walls for
   powder removal and warp?
4. Do you want the pivot-move option (3.1 item 4) studied, given its spar and actuator
   impact?
5. Hover current and T/W: the 36 in study and the ledger disagree (0.98–1.01 vs 1.36–1.41).
   Which is authoritative? F2 uses the ledger's 6,232 g AUW only.

## 5. Not done

No FEA, no vendor quotes, no CAD change, no census run. Figures marked [CALC] use repo
numbers as given and were not re-derived from the meshes.
