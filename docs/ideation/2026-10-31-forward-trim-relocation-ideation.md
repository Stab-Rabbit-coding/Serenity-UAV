# Serenity UAV — Forward Trim Room by Relocation (Ideation)

**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Date:** 2026-10-31
**Status:** Ideation (ranked candidates; not requirements, not a plan)
**Feeds:** `docs/plans/2026-10-31-003-feat-forward-trim-room-relocation-plan.md`
**Builds on:** `docs/ideation/2026-10-31-aft-cg-single-pivot-options-ideation.md` (graded skin)
**AI note:** Claude Opus 5.5 (Anthropic) under the direction of Steve Griffing
(Stab-Rabbit-coding). This was a single in-thread pass. The ce-ideate multi-agent fleet
was not dispatched, so the rankings have no independent corroboration.

> **ENGINEERING REVIEW REQUIRED.** Every figure here must be reviewed and accepted by a
> qualified engineer before it is applied to any system carrying risk to life or safety.

Labels: **[REPO]** ledger output (`tools/auw_ledger.py` station items).
**[CALC]** my moment arithmetic. **[ASSUMED]** needs verification.

## 1. Grounding

- **Baseline:** AUW 6,310 g. The CG is +16.6 mm aft of the thrust line (SPAR_Y 326.7).
  1 mm of CG ≈ 6,300 g·mm [REPO, merge `ea00da21`].
- **Current stack stations** [REPO]:

  | Stack (ledger name) | Y | X |
  | --- | --- | --- |
  | node A | 45.7 | 0 |
  | node chin | 276.7 | 0 |
  | node aft | 416.2 | 0 |
  | node simon | 494.7 | 0 |

- **Finding: today's stacks are distributed fore-aft only.** All four sit on the
  centreline (X = 0), so the port/starboard separation in the owner's intent does not
  exist yet. Relocating stacks can therefore improve plan R4 and the CG at the same time.
- **Fixed items:** the nose Observer (fully forward); the hoist line on the thrust line
  and CG; the winch at Y 361.2.

## 2. Ranked survivors

| # | Idea | CG change | R4 effect | Notes |
| --- | --- | --- | --- | --- |
| 1 | **Pivot moved 0.5 in aft** (owner's existing plan) | ≈ −8.9 mm | none | 12.7 mm × (1 − f), f ≈ 0.297 [CALC] |
| 2 | **Graded aft skin**, SLS PA CF (rear ×0.5, middle ×0.7, rear collar deleted) | ≈ −6.2 mm | none | From the earlier ideation doc. Needs a drop and stiffness check on the thinned wall. |
| 3 | **Flight Engineer forward** to about Y 300, in or beside the battery band | ≈ −6.0 mm | none | 225 g × 168 mm [CALC]. The space at Y 300 is unproven [ASSUMED], and ventral service access must hold. The planned chin/shuttle split (about −2.6 mm) is the fallback. |
| 4 | **Simon becomes the NoNFO-Pilot stack and stays aft** | ≈ −1.4 mm | keeps the aft position | Drops one TACCO, one PB2-I and half the pouches (about 58 g) at the longest arm [CALC]. This is the PACE Emergency stack. |
| 5 | **Port/starboard pair at the thrust line.** Move "aft" to the port sidewall and "chin" to the starboard sidewall, both near Y 330. | ≈ −0.5 mm | **creates the port/starboard positions** | Nearly CG-neutral. Its value is separation: the stacks become fore (A), aft (Simon), port and starboard. Sidewall depth versus stack height is [ASSUMED]. |
| 6 | **Uniform scale only if the fit fails** | worsens the offset | none | Use the smallest factor (≤ 27/24) that fits the items in ideas 3 and 5. |

**Combined, at 24 in with no scale:** 16.6 − 8.9 − 6.2 − 6.0 − 1.4 − 0.5 ≈ **−6.4 mm**.
(**Superseded, see §2a.**) That puts the CG about 6 mm forward of the thrust line. The ±2.2 mm cell rail and the
nose pocket (0.050 mm/g) then trim around it, giving about 6 to 8 mm of forward trim room
without stretch [CALC]. If idea 3 does not fit, the sum falls to about −0.4 mm. In that
case, idea 6 (minimum scale to make room for the Flight Engineer) is the lever.

## 2a. CORRECTION — reconciled with later branch work (2026-10-31)

The §2 combined figure (−6.4 mm) is **superseded**. It used the earlier ideation's skin
targets (rear ×0.5, middle ×0.7), and later work on this branch found those unreachable:

- **Skin thinning.** `docs/AFT_SKIN_THINNING_STUDY.md` shows handling governs, not
  strength. The best case is 333 g, about −2.9 mm. At the 1.5 mm minimum wall for
  fibre-filled SLS (§3a) the gain is about −2.0 mm, and even that skin fails the assumed
  handling load (MS −0.42). Credit: **0 to −2.0 mm**.
- **Skid U-frame.** The PA12-CF skid U-frame with a ventral strut at Y 620 (owner,
  `docs/SKID_FAILURE_MODE_STUDY.md` §8) adds about **+0.8 mm aft**.
- **Baseline.** One-piece middle+rear, as-is: +16.2 mm. SLS AUW at hover is 6,211 g
  (`tools/sls_auw_reconcile.py`).

| Step | Offset |
| --- | ---: |
| One-piece as-is, plus skid U-frame | +17.0 mm |
| Pivot moved 0.5 in aft | +8.0 mm |
| Skin at the printable minimum | +6.0 to +8.0 mm |
| Flight Engineer forward to about Y 300 | 0 to +2.0 mm |
| Simon becomes NoNFO-Pilot | −1.4 to +0.6 mm |
| Port/starboard pair | **−1.9 to +0.1 mm** |

**Revised conclusion.** Relocation at 24 in brings the CG to about the thrust line, but it
does not create forward trim room. The Flight Engineer move is still the deciding item,
and it overlaps the FE chin/shuttle split plan (`docs/plans/2026-10-28-001`). Creating real
margin needs one of two things: a minimum uniform stretch that gives the FE and the side
stacks room further forward, or nose ballast at about 0.050 mm per gram.

## 3. Rejected, with reasons

- **Collocating stacks forward** to gain CG. This breaks R4 (single points of failure).
- **Moving node A or the nose Observer.** Both are already at the nose. Moving them
  would lose sensor view or reduce the forward moment.
- **Lead ballast as the primary fix.** It costs endurance at mass^-1.5. The nose pocket
  is kept only as a fine trim.
- **Moving the winch or hoist off the thrust line.** Violates R6.
- **Uniform 27 in scale as the first step.** It worsens the offset (+11.4 mm after the
  pivot shift) and adds 92 to 318 g. Use it only for volume.

## 4. Open checks for planning

1. Fit the Flight Engineer near Y 300 with `tools/cargo_layout_fit.py` on the real meshes,
   with the battery band and service access in place.
2. Check sidewall depth at Y 330 for one full stack with its saddle, on each side.
   Port and starboard must mirror (0.5 mm gate).
3. Check RF and termination when the bus end moves (Simon stays aft, so the effect
   should be small).
4. Measure bench pitch authority to set the trim range (plan A1).
