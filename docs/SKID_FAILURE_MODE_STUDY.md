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

## 5. Stiffness governs, not strength (2026-10-31, owner follow-up)

Tools: `tools/skid_failure_mode_study.py` (`stiffness_check`) and `tools/skid_mount_loads.py`
(beam model with the measured I(y), root fixed at the ring).

**Stroke available.** At skid contact the lowest hull point is ≥ 8.3 mm off the ground,
counting the ventral cross member as part of the skid frame (it is: see §6). Less a 1 mm
margin, that leaves **7.3 mm**. Each skid must absorb about **3.3 J** inside that stroke.
That needs a plateau force of at least 452 N, or an elastic stiffness of at least
**124 N/mm** with a peak of about 900 N.

| Skid (per skid) | Tip stiffness | Force inside 7.3 mm | Energy inside 7.3 mm |
| --- | ---: | ---: | ---: |
| PA11, as built (ring only) | 4.7 N/mm (27 lbf/in) | 34 N | 0.12 J |
| PA11 + ventral strut at Y 596 | 17.5 N/mm | 127 N | 0.47 J |
| PA11 + ventral strut at Y 620 | 29.3 N/mm | 214 N | 0.78 J |
| PA12-CF, as built | 21.7 N/mm | 159 N | 0.58 J |
| PA12-CF + ventral strut at Y 596 | 75.7 N/mm | 552 N | 2.02 J |
| **PA12-CF + ventral strut at Y 620** | **127 N/mm (727 lbf/in)** | **930 N** | **3.39 J** |

**PA11 cannot do the job in any mounting.** Its modulus is 1,500 MPa. The skid bends
away, and the hull reaches the ground before the skid develops even 30% of the force.
The plastic-hinge argument in §0 assumed the skid could load up to its hinge moment; at
this stiffness it cannot, inside the stroke.

**This reverses the §0 material preference.** The only combination that meets the energy
inside the stroke is the **stiff grade (PA12-CF) with a ventral strut at the cross
member**. It absorbs the energy **elastically**: the whole skid flexes like a leaf spring
and returns undamaged, which is the owner's "absorb without damage" aim. Brittleness then
matters only above the design load. That has to be covered by margin, not by yielding.
*(Owner to decide; see §8.)*

## 6. Mount points and their loads

**As built**, measured from section topology:

| Station | Feature | Attached to hull? |
| --- | --- | --- |
| Y 465–475 | Horseshoe ring: one continuous section with the hull | **Yes**, the only structural mount |
| Y 480–500 | Ring lower legs (X ±40–87, Z 85–157) taper into the skid roots | through the ring |
| Y 506 | Ventral bridge between the two skid roots (X ±42, Z 90–110) | no (below the hull) |
| Y 520 | Small ventral keel bar (X ±16, Z 83–91) | hull feature; not tied to the skids |
| Y 512–612 | Skid tubes, separate loops beside the belly | no |
| Y 595.7 | Rear CF ring frame (CF plate in a pocket) | the hard point nearest the skids |
| Y 613–629 | **Ventral cross member**: one U with both skids, Z 95–117, about 1 mm below the hull bottom (Z ≈ 116) | **no** |

So the skid U-frame is **cantilevered from the ring alone**.

**Loads per skid at the design force** (PA12-CF, ventral strut at Y 620, F = 750 N, 169 lbf):

| Mount | Load |
| --- | --- |
| Ring root (Y 506) | V 630 N (142 lbf), M **22.3 N·m (197 lbf·in)** |
| Ventral strut (cross member to hull) | **1,380 N (310 lbf) per skid in compression, 2,760 N (620 lbf) per pair into the hull** |
| Cross member (central strut) | 62 N·m (549 lbf·in) bending each side |
| Skid just aft of the cross member (Y ≈ 630) | about 116 MPa against 84 MPa: **needs Z ×2.1** (wall 2.3 → about 4.8 mm over about 20 mm, about +3 g per skid) |

Compare an un-strutted skid sized to reach 750 N by root strength: 135 N·m at the ring.
**The strut cuts the ring-root moment by about 6×**, so the ring legs need no extra
material.

**The new load is the strut reaction into the hull.** About 2.8 kN arrives at Y 620. That
is the tail cone, aft of the CF ring frame at Y 595.7, and its skin may be thinned
(`AFT_SKIN_THINNING_STUDY.md`). It needs a hard point:

- a short longitudinal web or doubler from the strut pad forward to the CF ring frame
  (25 mm); or
- a second CF plate frame at Y ≈ 620.

**The strut itself** spans only about 1 mm between the cross member top (Z 117) and the
hull bottom (Z 116–118). It is a **bonded or bolted pad**, not a column, so buckling does
not arise. Bearing: 1,380 N over a 10 × 20 mm pad is 6.9 MPa. For Option B (ring and skids
separate), use one M3 bolt per side through the pad into a boss on the frame or doubler.
It carries compression in bearing and the small rebound tension in the bolt.

**Single-skid strike** (one skid down, rolled): the cross member carries the full 62 N·m
on one side, plus torsion that the U-frame shares with the ring. The case is not yet
analysed.

## 7. Spring wire at the junction, and a honeycomb interior

**Spring wire at the ring/skid junction: not recommended.**

- **As an elastic hinge or absorber at the junction**, it sits *in series* with the soft
  skid beam. It adds compliance and cannot raise the force the skid develops.
- **As a stiffener carrying the root moment**, music wire at 900 MPa working stress
  [REF-MAT-008] for 125 N·m needs about **Ø 11 mm, about 46 g per skid** over 40 mm. That is
  heavy, at about Y 510–550.
- **Installation, if one is used anyway:** SLS cannot embed metal mid-build, because the
  part sits in a powder bed. Print a straight bore (wire Ø + 0.2 mm), insert the wire from
  the ring face before the ring is fitted, and retain it with epoxy or a set screw. The skid
  centreline curves (X −54 → −30 mm over the span), so a straight insert spans only about
  60 mm. That matches the existing CF rod bore (Y 478.7–538.7).

**Honeycomb or lattice interior with elastically collapsing walls: not recommended as the
absorber.**

- Local elastic crushing of the tube at the contact (ring under a 20 mm line load, PA11)
  gives about **0.2 J with about 1 mm of travel per skid**, roughly 5% of the 3.3 J needed.
  A lattice core raises the crush force but not the elastic energy, which is limited by the
  small volume of material strained.
- It adds about 7–9 g per skid at a 20% gyroid fill.
- It contributes almost nothing to beam stiffness (lattice modulus is about E·ρ²).
- For SLS it must be **open-cell with powder escape holes**. A closed honeycomb traps
  powder.
- Optional: a thin lattice *wear pad* at the tip for scuffing, a few grams.

## 8. Mass and CG of the recommended arrangement

| Item | Δ mass (pair) |
| --- | ---: |
| Skid tubes PA11 → PA12-CF (54.2 cm³ at 1.11 vs 1.03) | +4.3 g |
| Local wall Y 630–650 (Z ×2.1) | about +6 g |
| Strut pads and doubler to the CF frame (PA12-CF) | about +5 g [ASSUMED] |
| 2 × M3 bolts and inserts | about +2 g |
| **Total** | **about +17 g at Y ≈ 620 → hover CG about +0.8 mm aft** |

Against the alternatives:

- PA11 with a root sized for 750 N: Zp ×2.8, about +30 g at Y ≈ 520, about +1 mm CG. It
  *still* fails the stroke, on stiffness.
- A steel spring-wire root: about +92 g.

**Decision needed (owner):** accept PA12-CF for the skid and cross member U-frame, with an
elastic design and a ventral strut at Y 620. Or keep PA11 and accept that the skids cannot
protect the tail in the 4 ft co-strike.
