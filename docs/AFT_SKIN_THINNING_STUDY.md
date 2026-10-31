# Aft Skin Thinning Study — Joined Middle+Rear SLS Part

**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Date:** 2026-10-31
**Tool:** `tools/aft_skin_thinning_study.py` (reproduces every figure below)
**Baseline:** `docs/MASS_AUDIT_MIDDLE_REAR_SECTIONS.md`
**Feeds:** `docs/plans/2026-10-31-001-feat-one-piece-aft-sls-hull-plan.md` R4 and S1
**AI note:** Analysis and text by Claude Opus 5.5 (Anthropic) under the direction of
Steve Griffing (Stab-Rabbit-coding). No geometry has been changed.

> **ENGINEERING REVIEW REQUIRED.** Every figure here must be reviewed and accepted by a
> qualified engineer before it is applied to any system carrying risk to life or safety.

Labels: **[MESH]** measured. **[SRC]** cited source. **[CALC]** my arithmetic.
**[ASSUMED]** needs verification.

## 0. Headline

1. **Strength and shell buckling do not size this skin.** The ultimate crash moment at
   the Y 436 joint is **68.3 N·m (604 lbf·in)**. The margin is at least **+5.1** for every
   candidate, including a bare 0.8 mm skin [CALC, REF-NASA-002].
2. **Handling governs.** A 20 lbf (89 N) fingertip load on a 5 mm radius patch, with the
   assumed 0.5 build-axis strength knockdown, fails every skin under 2 mm:
    - 1.0 mm skin: MS **−0.74**.
    - 2.0 mm baseline: MS **+0.04**.

    The ribs barely help, because the stress is local plate bending, which scales with
    1/t². **Both inputs are assumptions** (§4). They decide the answer.
3. **The ceiling of skin thinning is about 3.2 mm of CG.** The best stiffened candidate
   (1.0 mm skin plus isogrid ribs at 40 mm) brings the joined part from **417.9 g to
   332.9 g** in PA CF. That is 0.80 of the baseline, not the plan's ×0.5 and ×0.7
   targets. Hover offset with the single pivot 0.5 in aft: **+4.4 mm** (as-is: +7.2 mm).
4. **Foam fill is rejected.** Filling the rear cavity adds **67.6 g** at Y 587, which is
   17,577 g·mm aft: more moment than the skin thinning removes. A 5 mm liner is 11.5 g
   (2,991 g·mm aft). Its benefit for handling cannot be computed without a foam modulus,
   and the repo has none.
5. **The ring and skids are one continuous member** (owner, 2026-10-31).
    - There is no ring-to-skid attachment, so the old stanchion and collar-land bands are
     no longer kept at 2 mm.
    - The skid tubes are hollow tubes, about 20 mm across, at X ±35–58, Z 88–112. They run
     continuously from the ring (Y about 480) to Y about 665 and weigh **56.9 g**
     [MESH]. They carry the landing load, so they are held at full section and excluded
     from the thinning.

## 1. What was held at full section

| Zone | Why |
| --- | --- |
| Y 436–450 joint land | the joint at Y 436 to the cargo section stays |
| Horseshoe ring, Y 450–460 and 480–490 | owner decision: printed frame (plan R3) |
| Ring-frame pocket, Y 590–600 | CF ring frame seat |
| Skid tubes, every band (56.9 g) | continuous ring and skid member, landing load path |

Everything else counts as acreage. Each acreage band scales by t_eq / t_band, where t_eq is
the skin thickness plus the smeared rib thickness 3·b·d/h [REF-NASA-003]. The keep zones
are whole 10 mm bands. That is coarse: the true features are narrower, so the masses
below are slightly **conservative** (heavy) [ASSUMED].

## 2. Results (PA CF 1.11 g/cc)

| Candidate | t_eq | Part | MS, bend/buckle | MS, handling | f1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline 2.0 mm | 2.00 | 417.9 g | +23.2 | +0.04 | 562 Hz |
| 1.2 mm bare | 1.20 | 320.3 g | +17.1 | −0.63 | 464 Hz |
| 1.0 mm bare | 1.00 | 295.2 g | +13.6 | −0.74 | 431 Hz |
| 0.8 mm bare | 0.80 | 270.1 g | +8.6 | −0.83 | 392 Hz |
| 0.8 + isogrid 1.0×4 mm @ 30 | 1.20 | 320.3 g | +7.1 | −0.67 | 464 Hz |
| 1.0 + isogrid 1.0×4 mm @ 40 | 1.30 | 332.9 g | +6.4 | −0.57 | 478 Hz |
| 1.0 + isogrid 1.0×4 mm @ 30 | 1.40 | 345.5 g | +12.8 | −0.49 | 492 Hz |
| 1.2 + isogrid 1.0×4 mm @ 45 | 1.47 | 353.8 g | +8.1 | −0.43 | 501 Hz |

MS is the margin of safety at ultimate (×1.5, [REF-FAA-004 §23.2230]) under the plan R7
crash load factor of 79.4. The governing station is always Y 440. f1 is the first
bending mode of the part as a cantilever from Y 436, carrying its items [REF-STR-001].

| Hover CG (relocated baseline, 2300KV ledger) | AUW | Offset | Single pivot 0.5 in aft |
| --- | ---: | ---: | ---: |
| Joined part, 2.0 mm as-is | 6,299 g | +16.2 mm | +7.2 mm |
| 1.0 + isogrid @ 40 | 6,214 g | +13.3 mm | **+4.4 mm** |
| 0.8 + isogrid @ 30 | 6,202 g | +12.9 mm | +4.0 mm |

## 3. Method

1. **Moment.** M(y) = 1.5·n·g·Σ m_i(y_i − y), taken over every ledger item and shell band
   aft of y.
2. **Skin stress.** M / (πR²t_eq), with R = (W + H)/4 from the measured sections.
3. **Shell buckling.** 0.605·γ·E·t/R on the bare skin, with the SP-8007 bending
   knockdown γ [REF-NASA-002].
4. **Skin-pocket buckling.** A flat plate with k = 4, b equal to the rib spacing.
5. **Handling.** A simply supported circular plate with a central patch load, plate
   radius equal to the pocket inradius h/3 [REF-STR-001].
6. **Allowable.** The lower of 0.5 × 84 MPa [REF-MAT-011] and the buckling stress.

## 4. What decides the answer, and what to do about it

1. **Handling load and contact patch** (20 lbf, 5 mm radius) are my assumptions. Owner
   to set them (WBS §0.12).
2. **Build-axis strength.** The 0.5 knockdown is assumed; the PA CF datasheet has no Z
   data. If coupons show the skin's bending direction near the XY value, the 1.0 mm
   handling margin rises from −0.74 to about −0.48. That is still short, so the skin
   still needs zoning.
3. **Zone the skin rather than thinning it everywhere.** Keep about 1.4–2.0 mm where
   hands, ground contact and hatch edges load it. Use 0.8–1.0 mm plus isogrid on
   protected acreage (between the skids, the inner faces). Zoning lands between the
   +4.4 mm and +7.2 mm rows above.
4. **Frequency.** f1 falls from 562 Hz to 392–501 Hz. The EDF rotor 1P frequency at hover
   is not in the repo. A modal check against it is needed before choosing the thinnest
   skin.
5. **The remaining offset** of about +4 mm has to come from outside the skin. The
   FE chin and shuttle split (plan 2026-10-28-001, about −2.6 mm) brings it to about
   +1.8 mm, inside the ±6.4 mm working trim band.
