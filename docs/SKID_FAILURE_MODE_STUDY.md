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

**Owner decision (2026-10-31): PA12-CF U-frame plus a ventral strut at Y 620, elastic
design.** This supersedes the §0 and §3 PA11 plastic-hinge recommendation.

Next steps:

1. Size the local wall at Y 630–650 with a factor of safety of 1.5 on the 84 MPa strength.
2. Design the strut pad, the M3 bolt, and the doubler to the CF frame for 2.8 kN per pair.
3. Check the single-skid strike: cross member bending and torsion.
4. Check the ring root at V 630 N and M 22 N·m per skid.
5. Re-run the co-strike (`tail_strike_requirement.py`) with an *elastic* skid (k ≈ 127 N/mm),
   not a plateau. CS-1 and CS-2 change shape: the peak force is about 930 N at full
   stroke.

## 9. Strut and elastic co-strike design (items 2 and 5, 2026-10-31)

Reproduce with `/usr/bin/python3 tools/skid_mount_loads.py`. The figures below come from
`size_elastic_design()`, `strut_design()` and `tail_strike_requirement.py` (elastic mode).
US customary first, metric in parentheses.

### 9.1 Canon guidance [REF-CAD-003, REF-CAD-002]

QMx Sheet Two (the pack's tablet extract is at thumbnail resolution) names the aft
structure **"the big yoke around the back of the engine."** Nick Henning's renders
(`nick-henning-close-back-combine.jpg`, `nick-henning-final-backside-combine.jpg`) show
it clearly:

- a **broad, flat ring** over the top of the engine bell;
- at the bottom, each side turns aft into a **flat rectangular skid rail**, wider than it
  is tall, running close under the bell and ending in a squared tip behind it;
- **no visible strut** between the rails and the bell in profile. The rails hide
  everything beneath the bell.

Henning ranks below QMx and is used here for detail only.

Rules that keep the strut and skids canonical:

1. **The outer shape is unchanged.** All skid strengthening goes *inside* the tube, as
   wall growth.
2. **The strut is a low pad**, about 0.04 in (1 mm), between the cross member and the bell
   underside, at **X ±1.6 in (±40 mm), inboard of the rails**. The near rail hides it in
   side view. There is no diagonal post.
3. **The rib is internal**, inside the hull, running from the pad forward to the rear CF
   ring frame.
4. **The bolt enters from below** (a socket head on the underside, as with existing
   underside detail). There is no new exterior silhouette.

### 9.2 Results

| Item | Value |
| --- | --- |
| Design case | 4 ft co-strike at 14.19 lbm. Skids sacrificial above 0.95 × ultimate (TS-5 practice, as for the gear). |
| Skid stiffness | **1,244 lbf/in (218 N/mm) per skid** |
| Skid stroke | **0.213 in (5.42 mm)** against a 0.217 in (5.5 mm) limit: 6.5 mm clearance less the 1 mm margin |
| Skid peak force | **266 lbf (1,181 N) per skid**, elastic. The energy is returned on rebound. |
| Pad (strut) reaction | **489 lbf (2,177 N) per side**, 978 lbf (4,354 N) per pair, at Y 620 |
| Ring-root moment | 315 lbf·in (35.6 N·m) per skid |
| Aft gear stroke | 0.78 in (19.8 mm) of the 1.21 in (30.7 mm) settle limit |
| Skid wall | grows up to **×2.4** over Y 589–661, inside the tube: **+0.25 oz (7.2 g) per skid** |
| Internal rib (PA12-CF) | 0.24 × 1.01 in (6 × 26 mm), 0.96 in (24.3 mm) long: **0.15 oz (4.2 g) per side** |
| Pads, M3 bolts, heat-set inserts | about 0.14 oz (4 g) per pair [ASSUMED] |
| **1.5 ft ordinary landing** | peak 149 lbf. Maximum skid stress **6,500 psi against 8,120 psi** (ultimate ÷ 1.5): **elastic, no damage** |
| **Mass added, pair** | **+0.94 oz (27 g) at Y ≈ 620 → hover CG +0.048 in (1.2 mm) aft** |

### 9.3 Notes

- **Why not sized elastically at 1.5 × for the crash?** Holding the 4 ft peak to
  ultimate ÷ 1.5 needs about ×4.8 wall growth: +2.45 oz (69 g) and +0.12 in CG. Each
  stiffening step raises the peak force. Elastic energy storage in a brittle composite at
  a high factor of safety is mass-hungry, so the crash case is allowed to be sacrificial,
  as for the gear (TS-5).
- **The stroke margin is thin:** 0.004 in to the limit. The as-built skid stiffness must
  be checked by a bench deflection test. If it comes out softer, add wall.
- **The minimum SLS wall** (1.5 mm for fibre-filled grades) is met: the wall grows from
  2.3 mm.
- **Still open:**
    - the single-skid (rolled) strike;
    - the rib and CF frame joint detail: 489 lbf plus 41 lbf·in per side into the frame;
    - interior clearance for the rib at X ±1.6 in, Y 596–620, against the rear-section
      equipment;
    - tolerance stack for co-planarity of the feet and skid tips.

## 10. The five open items, on the current specification (2026-10-31)

Owner direction: keep the current specs, work the open items, and flag anything that
breaks a spec. Reproduce with `/usr/bin/python3 tools/skid_open_items.py`. Item 4 was done
by mesh inspection in the session and is recorded here.

### 10.1 Item 1: stroke margin against as-built stiffness — **FLAG**

| Skid stiffness (per skid) | 4 ft stroke | Status |
| --- | ---: | --- |
| 1,369 lbf/in (×1.10) | 0.205 in (5.20 mm) | ok |
| **1,245 lbf/in (nominal)** | **0.213 in (5.42 mm)** | ok |
| 1,207 lbf/in (×0.97) | 0.216 in (5.49 mm) | ok, the lowest that passes |
| 1,183 lbf/in (×0.95) | 0.218 in (5.54 mm) | **over 0.217 in** |
| 1,058 lbf/in (×0.85, worst case) | 0.229 in (5.81 mm) | **over** |

The worst-case stiffness combines the SLS wall tolerance (±0.3 mm on a 5.5 mm wall, so I
±5%) with modulus scatter (±10% [ASSUMED]; 3DS-30108A gives none). It is ×0.85.

> **FLAG — breaks R2 / CS-7 at worst-case tolerance.** The design has a 3% stiffness
> margin.
>
> - **Required:** an as-built acceptance test. Bench-load each skid at the tip and require
>   **k ≥ 1,207 lbf/in (211 N/mm)**. Reject or shim any softer skid.
> - **Alternative**, a design change not made per the owner: add about 15% stiffness, which
>   is about 0.1 oz more wall per skid.

### 10.2 Item 2: single-skid (rolled) strike — **FLAG**

The bound is conservative: one skid plus the aft gear pair, in pitch only, with no roll
relief. The ledger carries I_pitch only, not I_roll.

| Quantity | Value |
| --- | --- |
| Skid stroke | **0.285 in (7.24 mm)**, against a 0.217 in limit: **the hull touches** |
| Skid peak | **355 lbf (1,579 N)**, about **1.27 × ultimate**, so the skid fractures |
| Strut, loaded side | 654 lbf (2,909 N) |
| U-frame torsion | about 629 lbf·in [45 mm lever ASSUMED] |
| Gear stroke | 0.84 in, within the 1.21 in limit |

> **FLAG — breaks R2 / CS-7 and the TS-5 intent for a one-skid-first touchdown.**
>
> - Roll relief would lower it; the true effective mass depends on I_roll and the roll
>   arm, which are not in the ledger.
> - **Required:** add I_roll to `tools/auw_ledger.py` and re-run.
> - If it still fails, the owner chooses between limiting the design roll attitude at
>   touchdown, which is an operating limit, and accepting skid fracture on a rolled 4 ft
>   crash, which TS-5 allows if the hull does not crack. A fracture lets the hull touch, so
>   that also has to be confirmed.

**Owner direction (2026-10-31): record the rollover failure mode as a CAUTION.** It is
equipment damage only, so a CAUTION, not a WARNING (CNAF M-3710.7 [REF-MIL-003]).

> **CAUTION:** Rolled (one-skid-first) hard landing. Each aft skid is sized to share a
> nose-high 4 ft drop *with the other skid and the aft gear*. If the aircraft touches down
> rolled, so that one skid takes the strike alone, that skid can be driven past its ultimate
> strength (about 355 lbf, 1.27 × ultimate, conservative pitch-only estimate) and **fracture
> at the ring root**. The tail cross member and hull can then touch the ground. Inspect both
> skids, the ring root and the ventral strut pads after any rolled or hard landing, and
> replace a cracked skid frame before the next flight. Avoid rolled touchdowns until the
> I_roll re-analysis (WBS §0.12) sets a roll-attitude limit.

### 10.3 Item 3: rib to CF ring frame joint — **FLAG, resolved by a rib change**

- **As specified, it breaks.** The rib is cantilevered aft from the frame, so it loads the
  2 mm CF plate frame **out of plane**: 468 lbf·in on a 0.08 × 0.39 in band, about
  1,150,000 psi (7,935 MPa). A plate frame cannot carry that.
- **Resolution: the rib passes over the frame as a lever**, bonded or bolted along the
  2 mm skin zone, from Y ≈ 572 to 620:
    - **Forward tie:** 502 lbf. Two M3 bolts in tension carry 251 lbf each (FOS 3.2). Skin
      pull-through is 392 lbf per bolt (FOS 1.56).
    - **Frame reaction:** 991 lbf (4,409 N) per side, **in plane** (vertical), which is the
      direction a ring frame carries.
    - **Rib:** grows 0.93 in forward, **+0.14 oz (4.1 g) per side, +0.28 oz pair**. The CG
      effect is negligible (about +0.01 in; most of the added mass is near the pivot).

> **FLAG — the specified joint concept breaks; the lever rib above replaces it.**
>
> - The CF plate bearing allowable under the rib saddle is **unsourced**. Gate it on a
>   coupon (WBS §0.12).
> - The forward tie lands in the 2 mm keep zone (plan 001 R4). If that skin is thinned,
>   add a backing plate.

### 10.4 Item 4: interior clearance for the rib — **no conflict**

- The ledger has nothing at Y 560–660 except the rear shell and the CF ring frame.
- Sectioning the rear shell at Y 597–619 shows only the outer and inner skin loops
  crossing the rib volume (X ±1.46–1.69 in, 26 mm deep). There is no inner-neck, pod or
  equipment geometry there.
- The rib sits in the lower interior corner, about 0.3 in (8 mm) from the side wall.
- **Recheck** when the rear section is rebuilt from source, or when equipment is placed
  aft of Y 560.

### 10.5 Item 5: co-planarity tolerance (R1 ±1 mm) — **R1 met (RSS); margin FLAG**

SLS ±0.3% or ±0.3 mm per dimension (`3d-print-design` skill, SLS rules):

| Contributor | ± |
| --- | ---: |
| U-frame, ring mount to skid tip (~200 mm) | 0.024 in (0.60 mm) |
| Middle shell, ring seat to aft gear bay | 0.012 in (0.30 mm) |
| Gear leg frame, 3.0 in | 0.014 in (0.36 mm) |
| Bay plate + foot | 0.017 in (0.42 mm) |
| Wire bow set | 0.008 in (0.20 mm) |
| Ring-to-hull joint | 0.008 in (0.20 mm) |
| **RSS** | **0.036 in (0.92 mm)**: **R1 met** (worst-case sum 0.082 in, not met) |

- **The skid-to-hull part of the stack** (±0.63 mm) eats the stroke margin. 6.5 mm
  clearance − 0.63 − 5.42 mm stroke leaves **0.45 mm** against the required 1 mm. The hull
  still clears, but the margin spec does not hold.

**Owner direction (2026-10-31):** if the margin cannot be brought back to 1 mm, put a note
in the assembly instructions. It **cannot** be brought back by analysis or process choice:
the SLS tolerance (±0.3% or ±0.3 mm) is a process limit, and a tighter vendor class is
unverified. So the NOTE is in `graphical-build-guide/REVN_BUILD_GUIDE_24IN.md` Phase 1
Checks.

> **FLAG — breaks the CS-2 / CS-7 1 mm hull margin at tolerance.** Resolutions, owner to
> choose:
>
> - **A measure-and-shim step:** set the skid tip height to the hull at assembly, using
>   the Option B bolted ring joint.
> - **Combine with the item-1 bench test**, so the as-built stroke is verified.
> - **Accept a 0.45 mm worst-case margin.**

### 10.6 Summary of flags

| # | Spec | Status | Path |
| --- | --- | --- | --- |
| 1 | R2 / CS-7 stroke | Breaks at worst-case stiffness | Bench acceptance k ≥ 1,207 lbf/in, or +15% stiffness |
| 2 | R2 / CS-7, TS-5 | Breaks under the conservative single-skid bound | Add I_roll and re-run; then a roll-attitude limit or accepted fracture |
| 3 | Joint concept | Breaks (out-of-plane frame load) | Lever rib over the frame, +0.28 oz pair; CF bearing coupon |
| 4 | Interior clearance | OK | Recheck after the source rebuild |
| 5 | R1 (RSS) OK; CS-2 margin | Margin breaks at tolerance (0.45 mm) | Measure and shim at assembly |
