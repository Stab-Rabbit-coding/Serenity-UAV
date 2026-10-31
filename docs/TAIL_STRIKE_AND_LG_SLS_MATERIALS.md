# Tail Strike on the Aft Skids (4 ft Drop) and Landing-Gear Materials in SLS

**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Date:** 2026-10-31
**Tool:** `tools/tail_strike_requirement.py` (reproduces every figure below)
**Basis:**
- `docs/LANDING_GEAR_ANALYSIS.md` (4 ft drop, LG-17).
- `tools/landing_gear_r6_sizing.py` (13.0 lbm schedule, rigid-body effective mass).
- `docs/LG_BELLCRANK_LOAD_PATH_STUDY.md`.

**AI note:** Analysis by Claude Opus 5.5 (Anthropic) under the direction of
Steve Griffing (Stab-Rabbit-coding).

> **ENGINEERING REVIEW REQUIRED.** Every figure here must be reviewed and accepted by a
> qualified engineer before it is applied to any system carrying risk to life or safety.

Labels: **[MESH]** measured. **[SRC]** datasheet or cited source. **[REPO]** repo tool.
**[CALC]** my arithmetic. **[ASSUMED]** needs verification.

## 0. Headline

1. **The tail cone strikes before the skids.**
   - The tip-back angle is **25.6°** nose-up about the aft feet. The first contact is the
     tail-cone tip at Y 689.8, Z 119.2 [MESH].
   - The skid tips reach the ground about 0.6° later.
   - The skids are not yet protecting the tail.
2. **Skid-first strike energy is small, because the long lever arm makes the effective
   mass small.** The skid pair has to absorb:

   | Attitude | Energy in first contact | Fraction of aircraft mass acting |
   | --- | --- | --- |
   | Tip-back, 25.6° | 8.8 J (6.5 ft·lbf) | 0.110 |
   | 40.6° (tip-back + 15°) | 12.8 J (9.4 ft·lbf) | 0.160 |
   | Near-vertical, tail-first | approaches 79.6 J | approaches 1.0 |

   [CALC, the same method as the gear tool].
3. **A strike at exactly tip-back loads the aft gear, not the skids.**
   - The CG is only 14.4 mm ahead of the aft feet at that attitude, so the aft pair takes
     98% of the energy: **39.0 J per leg**. The gear schedule is 35.3 J per leg.
   - The cause is mass. The gear was sized at **13.0 lbm**. The heaviest configuration is
     **13.88 lbm** on the FDM ledger and **14.68 lbm** with the printed parts re-priced at
     solid CF-PETG density. That is ×1.13, so **F_leg rises from 1,148 N to 1,296 N
     (291 lbf)**.
4. **SLS PA CF lowers the AUW.** With PA CF printed parts the heaviest configuration is
   **14.09 lbm**, against 14.68 lbm FDM-solid: ×1.084 the gear design mass. The 13.38 lbm
   hover figure is FDM CF-PETG at the ledger density (owner, 2026-10-31).
5. **Gear materials:** PA12-CF (DuraForm PA CF) is the only one of the three that carries
   the leg frame and bay loads. PA11 belongs where energy is absorbed: the skids and the
   feet. PA12 Black is dominated by PA11 here, being weaker, less tough and only 1.6 g
   lighter (§3).

## 1. Tail-strike geometry (datum R2, 3.0 in flight gear)

| Item | Value | Source |
| --- | --- | --- |
| Aft feet | Y 440.7, ground Z 0 | `tools/landing_gear_r6_sizing.py` [REPO] |
| CG, heaviest configuration | Y 349.5, Z 157.3; k_pitch 102.1 mm | `auw_ledger.json` [REPO] |
| First aft contact | tail-cone tip at Y 689.8, Z 119.2: **25.6°** | [MESH] |
| Skid tip | about Y 680, Z 117.7: **26.2°** | [MESH] |
| Skid below the adjacent hull | 2.7 mm at Y 575, 7.0 mm at Y 605. At Y 625 the cross member between the skids (Z 96) is lower than the skid tubes (Z 99.9). | [MESH] |

The 1.5 in-era note in `LANDING_GEAR_ANALYSIS.md` §2.3 ("≈12° to skid contact") is
superseded for the 3.0 in flight gear: the angle is 25.6°.

## 2. Requirements derived for the aft skids (4 ft drop, LG-17)

| ID | Requirement | Basis |
| --- | --- | --- |
| **TS-1** | The skids shall make the first aft ground contact at every nose-up attitude above aft-gear tip-back. Today the tail cone leads by 0.6°. Proportions are fixed (plan R6), so the fix is in the skid tip itself. Its underside shall reach at least about 2 mm below the line from the aft feet to the tail tip (margin [ASSUMED]). | §1 |
| **TS-2** | Design attitude envelope: tip-back to tip-back + 15° (25.6–40.6°) **[ASSUMED, owner to set]**. Skid-pair energy **≥ 12.8 J (9.4 ft·lbf)**, absorbed without the hull or tail cone reaching the ground. | §0 item 2 |
| **TS-3** | Stroke. The skids shall provide their absorbing stroke before the skin touches. That stroke is **3–7 mm** today. Pair force at the stated stroke and 12.8 J: 10 mm, 1,276 N (287 lbf); 20 mm, 638 N; 30 mm, 425 N. At 10 mm the CG sees about 19.5 g and the skid point about 122 g. | [CALC] |
| **TS-4** | Simultaneous aft gear and tail at tip-back: the aft gear pair shall take 39.0 J per leg (F_leg about 1,296 N) at the as-built design mass. **Re-size the gear schedule from 13.0 lbm to the as-weighed AUW** (LG-15). | §0 item 3 |
| **TS-5** | Skids may be sacrificial after a 4 ft drop, as for the gear (`LANDING_GEAR_ANALYSIS.md` §1). The hull shall not crack. | LG-17 practice |

**Why stroke drives the material.** At 12.8 J the energy needs a skid that yields and
strokes rather than one that breaks. PA CF fails at 3.8% elongation, so it fractures with
little absorbed energy. PA11 Black stretches to 52.6%, so it yields and keeps absorbing.
This supports Option B (`docs/AFT_SKIN_THINNING_STUDY.md` §5): the ring and skids
printed separately in PA11.

## 3. Landing-gear material re-check

Demands come from the gear tool at the 13.0 lbm, 4 ft schedule. Allowable = ultimate / 2,
the tool's own convention. Bearing scales by the CF-PETG ratio, which is **[ASSUMED]**:
the SLS datasheets have no bearing data. **At the as-built 14.68 lbm, divide every
margin by 1.13; at 14.09 lbm with SLS parts, by 1.08.**

| Material | Leg frame (3.0 in) | Thigh, 6 mm bore | Thigh, solid | Bay boss bearing | Bay bolt FOS (target 4.0) | Stiffness vs CF-PETG | Elongation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| CF-PETG FDM [REF-MAT-002] | 52.0 g | 0.58× | 0.66× | 0.82× | 2.86 | 1.00× | 2.1% |
| **PA12-CF (PA CF) [REF-MAT-011]** | **45.1 g** | 0.88× | **1.01×** | **1.26×** | **4.37** | 1.05× | 3.8% |
| PA12 Black [REF-MAT-013] | 40.6 g | 0.47× | 0.54× | 0.67× | 2.34 | 0.22× | 13.7% |
| PA11 Black [REF-MAT-012] | 41.9 g | 0.53× | 0.62× | 0.76× | 2.65 | 0.22× | 52.6% |

**What makes sense for each section**

| Section | Material | Why |
| --- | --- | --- |
| Leg frame: thigh bellcrank and shin | **PA12-CF, solid thigh (no bore)** | The only material that passes, at 1.01× and 13.0 lbm. At 14.09 lbm it is 0.93×, so the thigh diameter needs +2.7% (Z ×1.08). Or carry the moment in the Option A1b CF backbone (PR #262). Saves 6.9 g per leg against CF-PETG. |
| Bay plate, boss and bolt lands | **PA12-CF** | Boss 1.26× and bolt FOS 4.37 at 13.0 lbm. At 14.09 lbm these become 1.16× and **4.03**, just at the 4.0 target. The nylons fail both. |
| Foot (ground contact) | **PA11** | Small and in direct impact and abrasion, so toughness counts more than stiffness. |
| Skids and ring (Option B) | **PA11** | The energy absorber for TS-2 and TS-3 (§2). Equal-OD stiffness is 0.22×, which is acceptable because the skids are meant to stroke. |
| PA12 Black | **No section** | PA11 is stronger, tougher and more uniform across build orientations, for 1.6 g more per leg-sized part. |

**Mass:** four PA12-CF leg frames save **27.6 g** against CF-PETG. The ductile and spring
wires, the pins and the CF backbone are unchanged.

## 4. Open items

- The owner sets the TS-2 attitude envelope, and the skid fix for TS-1 within the fixed
  outer shape.
- **Re-size the gear wires** (ductile Ø, spring Ø) at the as-weighed AUW (LG-15). This
  depends on the SLS or FDM decision: 14.09 vs 14.68 lbm.
- PA CF and PA11 bearing allowables and build-axis data: coupons or the vendor
  (WBS §0.12).
- PA11 and PA12 Black datasheets are cataloged as REF-MAT-012 and REF-MAT-013; their official URLs still need validating.
