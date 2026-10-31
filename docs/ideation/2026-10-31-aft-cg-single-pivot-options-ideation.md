# Serenity UAV — Aft-CG Options Under a Single Fixed Pivot and Fixed Proportions

**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Date:** 2026-10-31
**Status:** Ideation (ranked candidates; not requirements, not a plan)
**AI note:** Written by Claude Opus 5.5 (Anthropic) under the direction of Steve Griffing
(Stab-Rabbit-coding). Single in-thread pass; no independent reviewer agents were dispatched,
so the rankings below carry no independent corroboration.

> **ENGINEERING REVIEW REQUIRED.** Every figure here must be reviewed and accepted by a
> qualified engineer before it is applied to any system carrying risk to life or safety.

Labels: **[REPO]** repo tool output. **[CALC]** my arithmetic. **[ASSUMED]** needs verification.

## 1. Constraints (owner, 2026-10-31)

1. One tilt pivot only. Indexed or multiple pivot stations are rejected.
2. Fuselage proportions are fixed. No plug, no non-uniform stretch.
3. Uniform scale stays allowed. It was already shown to worsen the offset
   (+20.5 mm at 27 in, `docs/SLS_27IN_UNIFORM_SCALE_ADDENDUM.md` §2).

## 2. Grounding: where the aft moment comes from

Baseline: the rail-lever arrangement from `tools/sls_scale_trim_study.py`. AUW is 6,232 g
(13.74 lbm), the CG is **+16.3 mm (0.64 in)** aft of the pivot (Y 326.7), and the aft
moment is 101,694 g·mm [REPO].

| Item | Mass | Station Y | Moment about pivot |
|---|---|---|---|
| Rear hull shell | 231.5 g (0.51 lbm) | 586.7 | **60,176 g·mm (59%)** |
| Flight Engineer (board, can and plate) | 224.8 g | 467.7 | 31,698 g·mm |
| Middle hull shell | 183.1 g | 473.2 | **26,824 g·mm (26%)** |
| Simon CN4 and FC4 | 118.0 g | 494.7 | 19,824 g·mm |
| Aft nodes FC2 and FC3 | 118.0 g | 416.2 | 10,561 g·mm |
| All three splice collars | 42 g | 235–509 | about 4,350 g·mm net |

Moments are net of forward items, so the percentages are shares of the net aft moment
[CALC, `tools/sls_scale_trim_study.py` entries].

**Finding.** The rear and middle shell *skins* account for about 85% of the net aft moment.
The earlier SLS documents compared materials on hull-average mass. None of them ranked the
contributors to the moment. Where the skin mass sits matters more than which material it is.

## 3. Ranked survivors

Every offset below is from a moment balance on the baseline item list, with the nacelles
riding the pivot [CALC].

| # | Idea | Offset | Notes |
|---|---|---|---|
| 1 | **Graded aft skin.** Make the rear shell 50% of its current mass (SLS PA CF, thinner wall, integral ribs). Make the middle shell 70%. | **+10.5 mm** | No proportion change. SLS makes thin ribbed walls practical where FDM would not. Needs a stiffness and drop check on the thinned wall. |
| 2 | Idea 1 **plus the single pivot moved 0.5 in (12.7 mm) aft**. This is the owner's existing plan, still one pivot. | **+1.7 mm** | Closes most of the gap. A 2-section hull removes the cargo/middle splice at Y 436 that the wing root trailing edge was crossing. |
| 3 | **Rear section as an SLS rib frame with a film skin** (25% of mass), middle shell 70%, pivot 0.5 in aft. | **−0.7 mm** | Lightest option. The rear section carries almost no load: it sits aft of every mass item. Durability of a film skin in ground handling is [ASSUMED]. |
| 4 | **Forward cells as useful ballast.** Use more capacity in the head cell instead of lead. | — | Each 100 g at the nose arm (about 312 mm) is about 5 mm of CG and adds endurance. Cell selection is open. |
| 5 | **FE chin and shuttle split** (`docs/plans/2026-10-28-001`) | about −2.6 mm | Already planned. Additive with ideas 1–3. |
| 6 | **Trim range without a second pivot.** Cell-rail slack (±2.2 mm) plus a nose ballast pocket (0.050 mm per g). | ±6.4 mm needs about ±125 g of pocket ballast | The trim target is still not derived: there is no pitch-control-moment figure in the repo. |

## 4. Rejected, with reasons

- **Merging sections to save collar mass alone.** The collars are about 42 g in total, worth
  about 0.7 mm. That is a real but secondary effect. Choose the section count for joint
  loads and for the splice/wing conflict, not for CG.
- **Nacelle tilt bias as a trim.** The CG sits only about 11.7 mm above the pivot (Z 158.6
  vs 146.9), so tilting the thrust line barely moves its intercept with the CG, and every
  degree of bias produces a horizontal thrust component [CALC].
- **Moving FC2/FC3 or Simon CN4/FC4 forward.** These are already covered by the open
  CN2/CN3 placement decision. They are not new here.
- **Uniform 27 in or 30 in scale.** Prior study: it worsens the offset. Its only gain is
  volume.

## 5. Review of the earlier conclusions (refresh)

| Document | Verdict |
|---|---|
| `SLS_MATERIAL_SELECTION_3DSYSTEMS.md` | **Holds.** PA CF matches CF-PETG stiffness. **Extend it:** grade the wall by station rather than using one 2 mm wall everywhere. |
| `SLS_27IN_UNIFORM_SCALE_ADDENDUM.md` | **Partly superseded.** The scaling conclusion holds. The "indexed pivot" recommendation is rejected by the owner (2026-10-31). |
| `SLS_27IN_TWO_SECTION_TRIM_STUDY.md` | **Holds** for the joint loads. Its trim levers need to be re-ranked against §3 above. |
| `SLS_EMI_AND_WINGS_NOTE.md` | Not affected. |

**Stale base.** This branch does not contain commit `1f76e5cf`, which carries the
QF2822-2300KV ledger fixes. Here `tools/auw_ledger.py` still reports 2,135 gf per fan and
fails on the unclassified LC-ADC row. Every figure above uses the pre-fix ledger. Re-run
after a rebase.
