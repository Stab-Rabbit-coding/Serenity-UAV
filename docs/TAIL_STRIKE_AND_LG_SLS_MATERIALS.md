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

1. **The skid tips are the first aft contact, but only just.** *(Corrected 2026-10-31:
   an earlier version said the tail cone strikes first. That vertex, at X ±37 mm, is a
   skid tip, not the tail cone.)*
   - The tip-back angle is **25.6°** nose-up about the aft feet. The first contact is the
     skid tips at X ±37, Y 689.8, Z 119.2 [MESH].
   - The lowest centerline point is the ventral cross member between the skids
     (Y 627.6, Z 96.6, 27.3°).
   - At skid contact, the cross member is **6.5 mm** off the ground. That is the skid
     stroke available before the hull touches.
2. **Skid-first strike energy is small, because the long lever arm makes the effective
   mass small.** The skid pair has to absorb:

   | Attitude | Energy in first contact | Fraction of aircraft mass acting |
   | --- | --- | --- |
   | Tip-back, 25.6° | 8.5 J (6.3 ft·lbf) | 0.110 |
   | 40.6° (tip-back + 15°) | 12.3 J (9.1 ft·lbf) | 0.160 |
   | Near-vertical, tail-first | approaches 77.0 J | approaches 1.0 |

   At the SLS design mass, 14.19 lbm.

   [CALC, the same method as the gear tool].
3. **A strike at exactly tip-back loads the aft gear, not the skids.**
   - The CG is only 14.4 mm ahead of the aft feet at that attitude, so the aft pair takes
     98% of the energy: **40.1 J per leg** at FDM-solid mass. The gear schedule is 35.3 J
     per leg.
   - The cause is mass. The gear was sized at **13.0 lbm**. The heaviest configuration is
     **13.88 lbm** on the FDM ledger and **15.09 lbm** with every printed part re-priced at
     solid CF-PETG density. That is ×1.16, so **F_leg rises from 1,148 N to 1,333 N
     (300 lbf)**.
4. **SLS lowers the AUW against solid FDM.** With SLS printed parts (PA CF, PA11 feet) on
   the hull and both nacelles, the heaviest configuration is **14.19 lbm**, against
   15.09 lbm FDM-solid: ×1.092 the gear design mass. The 13.38 lbm figure is the *empty* (no-payload)
   configuration, FDM at the ledger's 1.05 g/cc. The SLS equivalent, still empty, is
   **13.69 lbm** (§6). *(Corrected 2026-10-31: earlier figures of 14.09 and 14.68 lbm re-priced only the hull's printed parts and left out the 852 g of nacelle printed parts. See `tools/sls_auw_reconcile.py` and §6.)*
5. **Gear materials:** PA12-CF (DuraForm PA CF) is the only one of the three that carries
   the leg frame and bay loads. PA11 belongs where energy is absorbed: the skids and the
   feet. PA12 Black is dominated by PA11 here, being weaker, less tough and only 1.6 g
   lighter (§3).

## 1. Tail-strike geometry (datum R2, 3.0 in flight gear)

| Item | Value | Source |
| --- | --- | --- |
| Aft feet | Y 440.7, ground Z 0 | `tools/landing_gear_r6_sizing.py` [REPO] |
| CG, heaviest configuration | Y 349.5, Z 157.3; k_pitch 102.1 mm | `auw_ledger.json` [REPO] |
| First aft contact | skid tips at X ±37, Y 689.8, Z 119.2: **25.6°** | [MESH] |
| Lowest centerline hull point | ventral cross member at Y 627.6, Z 96.6: **27.3°**; 6.5 mm clear at skid contact | [MESH] |
| Skid below the adjacent hull | 2.7 mm at Y 575, 7.0 mm at Y 605. At Y 625 the cross member between the skids (Z 96) is lower than the skid tubes (Z 99.9). | [MESH] |

The 1.5 in-era note in `LANDING_GEAR_ANALYSIS.md` §2.3 ("≈12° to skid contact") is
superseded for the 3.0 in flight gear: the angle is 25.6°.

## 2. Requirements derived for the aft skids (4 ft drop, LG-17)

| ID | Requirement | Basis |
| --- | --- | --- |
| **TS-1** | The skids shall make the first aft ground contact at every nose-up attitude above aft-gear tip-back. **Met today** (25.6° vs 27.3° for the hull). The hull clearance at skid contact (6.5 mm) shall be at least the skid stroke; see §5. | §1, §5 |
| **TS-2** | Design attitude envelope: tip-back to tip-back + 15° (25.6–40.6°) **[ASSUMED, owner to set]**. Skid-pair energy **≥ 12.3 J (9.1 ft·lbf)** at 14.19 lbm, absorbed without the hull or tail cone reaching the ground. | §0 item 2 |
| **TS-3** | Stroke. The skids shall provide their absorbing stroke before the skin touches. The hull clearance at skid contact is **6.5 mm** today (the ventral cross member; §1). Pair force at the stated stroke and 12.3 J: 10 mm, 1,234 N (277 lbf); 20 mm, 617 N; 30 mm, 411 N. At 10 mm the CG sees about 19.5 g and the skid point about 122 g. | [CALC] |
| **TS-4** | Simultaneous aft gear and tail at tip-back: the aft gear pair shall take 40.1 J per leg (F_leg about 1,333 N) at FDM-solid mass, or 37.7 J and 1,254 N at the SLS 14.19 lbm. **Re-size the gear schedule from 13.0 lbm to the as-weighed AUW** (LG-15). | §0 item 3 |
| **TS-5** | Skids may be sacrificial after a 4 ft drop, as for the gear (`LANDING_GEAR_ANALYSIS.md` §1). The hull shall not crack. | LG-17 practice |

**Why stroke drives the material.** At 12.3 J the energy needs a skid that yields and
strokes rather than one that breaks. PA CF fails at 3.8% elongation, so it fractures with
little absorbed energy. PA11 Black stretches to 52.6%, so it yields and keeps absorbing.
This supports Option B (`docs/AFT_SKIN_THINNING_STUDY.md` §5): the ring and skids
printed separately in PA11.

## 3. Landing-gear material re-check

Demands come from the gear tool at the 13.0 lbm, 4 ft schedule. Allowable = ultimate / 2,
the tool's own convention. Bearing scales by the CF-PETG ratio, which is **[ASSUMED]**:
the SLS datasheets have no bearing data. **At FDM-solid 15.09 lbm, divide every
margin by 1.16; at the SLS 14.19 lbm, by 1.09.**

| Material | Leg frame (3.0 in) | Thigh, 6 mm bore | Thigh, solid | Bay boss bearing | Bay bolt FOS (target 4.0) | Stiffness vs CF-PETG | Elongation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| CF-PETG FDM [REF-MAT-002] | 52.0 g | 0.58× | 0.66× | 0.82× | 2.86 | 1.00× | 2.1% |
| **PA12-CF (PA CF) [REF-MAT-015]** | **45.1 g** | 0.88× | **1.01×** | **1.26×** | **4.37** | 1.05× | 3.8% |
| PA12 Black [REF-MAT-017] | 40.6 g | 0.47× | 0.54× | 0.67× | 2.34 | 0.22× | 13.7% |
| PA11 Black [REF-MAT-016] | 41.9 g | 0.53× | 0.62× | 0.76× | 2.65 | 0.22× | 52.6% |

**What makes sense for each section**

| Section | Material | Why |
| --- | --- | --- |
| Leg frame: thigh bellcrank and shin | **PA12-CF, solid thigh (no bore)** | The only material that passes, at 1.01× and 13.0 lbm. At 14.19 lbm it is 0.93×, so the thigh cylinders need +2.5%, Ø14 → Ø14.35 mm (Z ×1.08). Or carry the moment in the Option A1b CF backbone (PR #262). Saves 6.9 g per leg against CF-PETG. |
| Bay plate, boss and bolt lands | **PA12-CF** | Boss 1.26× and bolt FOS 4.37 at 13.0 lbm. At 14.19 lbm these become 1.15× and **4.00**, exactly at the 4.0 target, with no margin. The nylons fail both. |
| Foot (ground contact) | **PA11** | Small and in direct impact and abrasion, so toughness counts more than stiffness. |
| Skids and ring (Option B) | **~~PA11~~ → PA12-CF** (owner, 2026-10-31; stiffness governs, `SKID_FAILURE_MODE_STUDY.md` §5) | The energy absorber for TS-2 and TS-3 (§2). Equal-OD stiffness is 0.22×, which is acceptable because the skids are meant to stroke. |
| PA12 Black | **No section** | PA11 is stronger, tougher and more uniform across build orientations, for 1.6 g more per leg-sized part. |

**Mass:** four PA12-CF leg frames save **27.6 g** against CF-PETG. The ductile and spring
wires, the pins and the CF backbone are unchanged.

## 4. Open items

- The owner sets the TS-2 attitude envelope, and the skid-stroke margin (§5) within the fixed
  outer shape.
- **Re-size the gear wires** (ductile Ø, spring Ø) at the as-weighed AUW (LG-15). This
  SLS is now the process (owner, 2026-10-31): interim 14.19 lbm.
- PA CF and PA11 bearing allowables and build-axis data: coupons or the vendor
  (WBS §0.12).
- PA11 and PA12 Black datasheets are cataloged as REF-MAT-016 and REF-MAT-017; their official URLs still need validating.

## 5. Co-strike design case (owner, 2026-10-31; plan 2026-10-31-002)

The design case is **the aft gear and the tail skids striking together** at tip-back. The
model is `co_strike()` in `tools/tail_strike_requirement.py`: a planar rigid body with two
constant-force (plateau) absorbers and gravity, extending the gear tool's effective-mass
method [REF-NCEES-009]. Design mass is **14.19 lbm** (SLS on the hull and both nacelles,
interim; the final value comes from the LG-15 weigh-in). The gear is re-sized at that mass:
F_leg 1,254 N per leg.

| Skid pair force | Gear pair | Gear stroke | Skid pair | Skid stroke | Slap-down, per fore leg |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 N | 77.4 J | 30.9 mm | 0 J | 22.3 mm (the hull strikes) | 1.5 J |
| 750 N | 64.3 J | 25.6 mm | 5.6 J | 7.5 mm | 5.2 J |
| **1,000 N** | 62.8 J | 25.0 mm | 6.1 J | **6.1 mm** | 5.6 J |
| 1,250 N | 61.7 J | 24.6 mm | 6.5 J | 5.2 mm | 6.0 J |
| 1,500 N | 60.9 J | 24.3 mm | 6.8 J | 4.5 mm | 6.2 J |

**Skid specification (U4), for the owner's source rebuild of the separate ring and skid
member** *(Superseded 2026-10-31, owner decision: the skid and cross member U-frame is **PA12-CF** (DuraForm PA CF), designed elastic, with a ventral strut at Y 620. PA11 was too flexible to absorb the co-strike inside the stroke. See `docs/SKID_FAILURE_MODE_STUDY.md` §5–8.)*:

| ID | Requirement |
| --- | --- |
| **CS-1** | Skid-pair plateau force **1,250–1,500 N (281–337 lbf)**, so **625–750 N (141–169 lbf) per skid**, held over the stroke. *(Corrected by review 2026-10-31: 1,000 N fails CS-2.)* |
| **CS-2** | Skid stroke **≤ 5.5 mm**: the 6.5 mm hull clearance at skid contact, less a **1 mm** margin [margin ASSUMED, owner to confirm]. 1,250 N gives 5.2 mm; 1,000 N gives 6.1 mm and fails. |
| **CS-3** | The skid tips stay the first aft contact (TS-1), with the tip at Y about 690 and X about ±37. |
| **CS-4** | Each skid absorbs **3.3–3.4 J (2.4–2.5 ft·lbf)**. In PA11 this has to come from yielding [REF-MAT-016]. The plateau model is an assumption until a coupon or skid drop test confirms it. |
| **CS-5** | Acceptance: `co_strike_mesh_check()` passes on the rebuilt STL at the chosen stroke plus the 1 mm margin. It identifies the skid tubes from their own cross-section loops and checks the middle and rear shells. Today it passes at 5.2 mm and fails at 6.1 mm. |
| **CS-7 (elastic, supersedes the CS-1/CS-2 plateau figures for the PA12-CF design)** | PA12-CF U-frame, pad strut at Y 620, stiffness **1,244 lbf/in (218 N/mm) per skid**. 4 ft co-strike: stroke ≤ 0.217 in (5.5 mm), today 0.213 in; peak 266 lbf (1,181 N) per skid at ≤ 0.95 × ultimate (sacrificial allowed). 1.5 ft landing: elastic at ultimate ÷ 1.5. Sizing: `docs/SKID_FAILURE_MODE_STUDY.md` §9. **Open-item flags (§10):** stroke at worst-case stiffness, single-skid strike (**CAUTION** recorded for a rolled landing), the frame joint concept, and the tolerance margin (**NOTE** in the build guide: measure and shim the skid tip height). |
| **CS-6** | **The skid section shall carry CS-1.** Estimate: a Ø20 × 2 mm tube cantilevered about 205 mm from the ring collapses at about **165 N** in PA11 (51 MPa plastic moment) and breaks at about **190 N** in PA12-CF. That is roughly a quarter of the 625–750 N needed [CALC; the cantilever length is ASSUMED from the mesh stations]. The rebuild needs a larger or thicker tube, a strut to the hull, or a shorter cantilever, within the fixed outer shape. |

**Gear in the co-strike:** about 25 mm of stroke against the 30.7 mm settle limit. That is
5.7 mm more margin than in a gear-only strike. The nose slap-down puts **≤ 6.2 J per fore
leg**. The comparison value is 38.5 J: the tail-down per-leg *demand* the shared wire is sized for, not an independent fore-leg capacity. R3 and R4 are **met under the plateau assumption**. That depends on the CS-4 coupon or drop test and on CS-6. Not yet analysed: roll or one-skid attitudes, a ±1 mm skid-height offset, local skin or ring joint capacity at the skid roots, and a rising (non-plateau) PA11 force curve.

## 6. How the AUW goes from 13.38 lbm (FDM) to SLS

Reproduce with `/usr/bin/python3 tools/sls_auw_reconcile.py`. Every printed part keeps its
STL volume. Only the density changes. Non-printed mass (BOM, nacelle hardware, GAP) is
unchanged.

| Step | Empty, no payload (`hover_4000`) | Heaviest = max hover AUW (`heaviest_4000_payload`, +8 oz payload; the design case) |
| --- | ---: | ---: |
| Ledger: FDM CF-PETG at 1.05 g/cc | **6,071 g, 13.38 lbm** | 6,298 g, 13.88 lbm |
| + hull printed parts to SLS (1,638 → 1,729 g) | +91 g | +91 g |
| + nacelle printed parts to SLS (852 → 901 g, both nacelles) | +49 g | +49 g |
| **SLS** | **6,211 g, 13.69 lbm** | **6,438 g, 14.19 lbm** |
| For comparison: FDM at solid 1.28 g/cc | 6,617 g, 14.59 lbm | 6,844 g, 15.09 lbm |

**Reading it.** VTOL: every sortie takes off and lands in hover, so the heaviest
configuration *is* the maximum hover AUW. The ledger name `hover_4000` means
"4000 mAh, no payload", not a separate flight regime. Hover T/W at the SLS design mass
is 9,480 gf / 6,438 g = **1.47**.

- **There are two steps, not one.** 13.38 → 14.09 lbm (my earlier figure) mixed two
  separate changes:
    - A configuration change: empty to loaded (+8 oz payload), +227 g.
    - A process change: FDM to SLS, which I applied to the hull only.
- **The process change, done properly over the whole aircraft, is +140 g (0.31 lbm).**
- **SLS is heavier than the ledger and lighter than real FDM.**
    - Against the ledger's 1.05 g/cc FDM, SLS PA CF (1.11 g/cc, printed fully dense) is
      heavier.
    - Against FDM thin walls printed solid (1.28 g/cc), SLS is **406 g (0.90 lbm)
      lighter**.
    - Which comparison is real still depends on weighing one printed FDM shell
      (plan 001 gate G1).
- **Not yet included:**
    - The aft-skin thinning (`docs/AFT_SKIN_THINNING_STUDY.md`, about −85 g).
    - The Option B skids in PA11 (−4.3 g).
    - The PA12-CF thigh growth (Ø14 → Ø14.35 mm, a few grams).

**CG effect.** Re-pricing the printed parts barely moves the CG (empty configuration). It shifts
**+0.16 mm** aft with SLS and +0.57 mm with FDM-solid, against Y 349.1 on the ledger.
The nacelle printed mass rides the pivot station. None of the CG studies
(`docs/AFT_SKIN_THINNING_STUDY.md`, plan 001) change materially [CALC].
