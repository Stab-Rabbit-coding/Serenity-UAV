# Rear Skid Failure Mode by Material — Root Bending vs Wall Collapse

**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Date:** 2026-10-31
**Tool:** `tools/skid_failure_mode_study.py` (reproduces every figure below)
**Load basis:** co-strike skid plateau CS-1, **625–750 N (141–169 lbf) per skid**
(`docs/TAIL_STRIKE_AND_LG_SLS_MATERIALS.md` §5)
**AI note:** Analysis by Claude Opus 5.5 (Anthropic) under the direction of Steve Griffing
(Stab-Rabbit-coding). Closed-form screening, not FEA.

> **ENGINEERING REVIEW REQUIRED.** Every figure here must be reviewed and accepted by a
> qualified engineer before it is applied to any system carrying risk to life or safety.

Labels: **[MESH]** measured. **[SRC]** cited source. **[CALC]** my arithmetic.
**[ASSUMED]** needs verification.

## 0. Answer

**The skid bends where it joins the ring. Its walls do not collapse along the length.**
This holds for every material. The skid is a cantilever. The bending moment grows
linearly toward the root, while the tube section stays nearly constant over the first
80 mm. The weakest point is therefore **Y ≈ 521**, where the tube emerges from the middle
shell at the horseshoe ring.

| Material | First failure | Tip force at onset, per skid | Behaviour |
| --- | --- | ---: | --- |
| CF-PETG FDM 20% | Root bending (fracture) | 243 N (55 lbf) | Brittle (2.1%): snaps; no stroke |
| PA12-CF (DuraForm PA CF) | Root bending (fracture) | 265 N (60 lbf) | Brittle (3.8%): snaps; no stroke |
| PA12 Black | Root plastic hinge | 229 N (52 lbf) | Ductile, marginal (13.7%; 6.2% in XY) |
| PA11 Black | Root plastic hinge | 260 N (58 lbf) | Ductile (52.6%): hinges and strokes |

**Every material reaches only 35–42% of the CS-1 force.** The skid section has to grow in
any of them. The material decides *how* the skid fails:

- **The brittle grades fracture at the ring joint.** The skid separates, the hull takes the
  strike, and the root may tear out ring material.
- **PA11 forms a plastic hinge at the root and keeps carrying load while it rotates.** That
  is the energy-absorbing behaviour the co-strike needs. It also concentrates the damage at
  one replaceable joint, which suits Option B.

## 1. Measured geometry (port skid, as built) [MESH]

Section loops are traced every 2 mm. The tube is a separate section from **Y 519** (it
emerges from the middle shell at the ring, with sporadic loops at Y 492–502 as it merges)
to the **tip at Y ≈ 686**.

- **Free cantilever: 167 mm (6.6 in).** The repo's earlier "about 177 mm" estimate
  (`docs/structural_analysis.md` §6.4) agrees.
- **Y 613–629:** the tube's outer wall merges into the ventral cross member that ties the
  two skids together. That member is its own loop *below* the hull, not attached to it. It
  ties the pair together but is not a vertical support.

| Y | Outer w × h | Wall | I_x | Z (elastic) | Zp (plastic) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 519 (root) | 23.9 × 23.1 mm | 2.30 mm | 6,473 mm⁴ | 544 mm³ | 866 mm³ |
| 567 | 22.2 × 23.0 mm | 2.51 mm | 6,669 mm⁴ | 573 mm³ | 859 mm³ |
| 631 | 17.4 × 19.2 mm | 2.34 mm | 3,782 mm⁴ | 361 mm³ | 588 mm³ |
| 679 | 14.5 × 17.3 mm | 2.49 mm | 2,892 mm⁴ | 302 mm³ | 495 mm³ |

The tube tapers toward the tip, but the moment falls faster. The aft stations therefore
never govern.

## 2. Failure modes compared (as built, tip load)

| Material | Root bending | Wall crush at contact¹ | Brazier ovalisation² | Local buckling³ |
| --- | ---: | ---: | ---: | ---: |
| CF-PETG FDM | **243 N** | 1,166 N | 2,175 N | 2,824 N |
| PA12-CF | **265 N** | 1,272 N | 2,283 N | 2,964 N |
| PA12 Black | **229 N** | 1,301 N | 489 N | 635 N |
| PA11 Black | **260 N** | 1,475 N | 489 N | 635 N |

1. The tip as a ring under a 10 mm-long contact [ASSUMED contact length]. Brittle: first
   crack at πσt²L/(6R). Ductile: four-hinge collapse at σt²L/R [REF-STR-001, requires
   verification].
2. M_B = (2√2/9)·π·E·r·t² / √(1−ν²) [REF-STR-002].
3. SP-8007 bending knockdown [REF-NASA-002].

**Wall collapse along the length is never the first mode.** For the stiff grades it sits
4–9× above root bending. In the nylons, which are 4.7× softer, ovalisation is the
runner-up at about 1.9× root bending. A larger, thinner tube would bring ovalisation
closer to governing (§3).

**Option B** (ring and skids printed separately, root at the ring, Y 485, 201 mm free
[ASSUMED geometry]) gives the same mode at lower force: 194–228 N.

## 3. What the skid needs (PA11, plastic hinge at the root)

- **Required Zp at the root:** 750 N × 167 mm ÷ 51 MPa = **2,456 mm³**. Today it is 866 mm³,
  so **×2.8**.
- **Option B:** 2,956 mm³ (×3.4).
- **A round tube with today's 2.3 mm wall** would need **OD ≈ 33 mm** (Option B: 36 mm).
  Today's is about 24 × 23 mm.

That is larger than the fixed outer shape (plan R6) likely allows. Better levers:

1. **Thicken the root wall locally.** Zp grows roughly with t at a fixed OD. A 4–5 mm wall
   over the first 30–40 mm, filleted into the ring, gets most of the way, and Brazier
   ovalisation falls as t² rises.
2. **Shorten the lever.** A strut or web from the skid to the hull at around Y 580 cuts
   the free length.
3. **Let the CF rod work.** The existing 4 mm rod (Y 478.7–538.7) spans exactly the root
   hinge zone. It is *ignored* here, and the earlier study credited it with only 2–6% of
   the moment. A larger rod, or a CF tube sleeve through the root, is the stiff and strong
   option. But it turns a ductile hinge back into a brittle one, which works against the
   co-strike stroke.

**Design choice this exposes:** the co-strike wants the root to *yield at about
700 N per skid and keep rotating*. That is a sized plastic hinge in PA11, not a stronger
skid.

## 4. Limits

- The tip force is vertical and static; no dynamic amplification.
- The ring and middle-shell joint behind the root is not checked. It must be stronger than
  the hinge, or the joint fails instead.
- No credit for the CF rod or the cross member.
- Allowables are at face value: no build-axis knockdown, no fatigue.
- The contact length for wall crushing is assumed.
- PA12 Black's 6.2% XY elongation may not sustain a full plastic hinge.
