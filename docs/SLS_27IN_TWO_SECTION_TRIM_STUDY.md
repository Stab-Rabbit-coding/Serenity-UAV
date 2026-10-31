# Serenity UAV — 27 in Hull, Two Fuselage Sections, SLS PA12 / PA12-CF, and Trim Authority

**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Date:** 2026-10-31
**Base:** `worktree-fuselage-reconcile` @ `3252b5a2` (2026-10-27, newest commit)
**Method files:** `tools/sls_scale_trim_study.py` (new; reuses `tools/cg_relocation_study.py` items),
`docs/sls-study/hull_build_volume_fit.scad`
**Supersedes:** the 30 in and single-piece conclusions in `docs/SLS_PA12_30IN_SINGLE_PIECE_EVALUATION.md`
and `docs/brainstorms/2026-10-31-sls-30in-trim-and-joints-requirements.md`.

> **CORRECTION (2026-10-31, after the PA12, PA11 and AF+ datasheets).** `docs/SLS_MATERIAL_SELECTION_3DSYSTEMS.md` §1 replaces the material advice in §5, §6 and §8 below: (1) PA12 is **not** a suitable hull skin at 2 mm. Its flexural modulus (1,500 MPa) is 4.4× below the repo's CF-PETG (6,670 MPa); **PA CF** matches it. (2) The hull mass savings in §6 assume real FDM shells weigh 1.28 g/cc; on the ledger's 1.05 g/cc they do not hold. Weigh one printed shell. (3) For shock-absorbing parts use **PA11 Black**, not PA12. The trim, plug, joint and two-section conclusions (§2–§4) are unaffected.

> [!WARNING]
> **ENGINEERING REVIEW REQUIRED — this output is not a substitute for a
> qualified engineer.** Every result, calculation, and recommendation produced
> with this skill **must be independently reviewed and accepted by a properly
> qualified individual** — a licensed Professional Engineer or an equivalently
> qualified authority for the jurisdiction and discipline — **before it is
> applied to any system carrying risk to life or safety.**

> [!CAUTION]
> **This skill informs engineering judgment; it does not replace it.** Applying
> unreviewed results to real equipment or hardware — even where no life-safety
> risk exists — carries a risk of equipment damage or property loss. It is
> reference material provided AS-IS (see LICENSE §5), is not an engineering
> service, and does not constitute a sealed, certified, or reviewed work
> product for any specific project.

Method basis: `aeronautical-engineering` (weight-and-balance, loads), `statics-and-dynamics`
(free-body, equilibrium) and `mechanical-engineering` (additive-polymer caveats) from
`Griffing-Technology-LLC/engineering-pe-skills`. All three are marked *UNREVIEWED DRAFT* by
their own front matter.

Labels: **[REPO]** repo document or tool output. **[SRC]** cited outside source. **[CALC]**
my arithmetic. **[ASSUMED]** needs verification. Datum is aircraft datum R2: Y aft-positive,
nose near Y 0, hover thrust line = nacelle tilt pivot Y 326.7 mm (12.86 in) [REPO
`hull_datums.SPAR_Y`]. Positive CG offset means aft of the thrust line.

---

## 1. Date check: what is stale

| Item | Date | Commit | Status |
|---|---|---|---|
| `HULL_SCALE_36IN_EDF64MM_EVALUATION.md` content | 2026-09-28 | `c7926186` | **Stale.** Only touched since for a licence header (2026-10-04, `31f47594`). |
| Bottom-up AUW/CG ledger | 2026-10-19 | `57a4c2cd` | Replaced the study's "corrected AUW 4,432.6 g". |
| Ledger moved to R2, installed bay meshes | 2026-10-25 | `4ba47dba` | Current station basis. |
| Flight envelope recomputed for split battery | 2026-10-26 | `ca624d4b` | AUW 6,318 g, T/W **1.35**, no stacking loss applied. |
| CG relocation, routed harness, rail lever | 2026-10-27 | `1175e044`, `2c4ebb9f`, `3252b5a2` | AUW 6,232 g, offset **+16.3 mm**. Newest. |

What the 36 in study got stale:

| Input | 36 in study (2026-09-28) | Current [REPO] |
|---|---|---|
| Baseline AUW | 4,432.6 g | 6,232 g hover, 6,318 g with payload |
| Structure baseline | 2,591 g (backed out) | printed items 1,583 g in the current roll-up |
| Thrust stacking | 90% | none applied (`flight_envelope.md`); if a loss exists, T/W is optimistic |
| T/W, current aircraft | 0.98–1.01 | 1.35 (envelope), 1.37 (CG study) |
| Propulsion | 64 mm EDFs assumed | 64 mm EDFs in the ledger now (8,540 gf) |

**Correction to my earlier documents.** I called the 0.98–1.01 vs 1.36–1.41 difference an open
conflict. It is not: the lower number is the stale one. Both earlier documents now carry a
banner saying so. The qualitative point (hull growth adds mass faster than thrust) survives, but
its numbers do not.

The newest repo work also changes the trim question itself. The 10-27 CG study found no further
equipment moves at a 2 mm static gap and left a residual of **+16.3 mm, 101,694 g·mm**
(AUW 13.74 lbm) [REPO `docs/CG_RELOCATION_STUDY.md` §3, §4].

## 2. The trim problem, stated as statics

Moment balance about the pivot: offset = Σ m·(y − Y_pivot) / Σ m [CALC from the repo roll-up,
rail-lever arrangement]. Reproduced: AUW 6,232 g, CG Y 343.0, offset **+16.3 mm**.
Nacelle mass fraction f = 1,853 / 6,232 = **0.297**.

| Lever | Result [CALC] |
|---|---|
| Pivot shift aft by d | offset closes by d(1 − f) |
| d = 0.50 in (12.7 mm) — your plan | residual **+7.4 mm (0.29 in)**, and zero trim range left |
| d = 1.00 in (25.4 mm) | −1.5 mm |
| d to zero the offset | 23.2 mm (0.91 in), matches the repo |
| Nose ballast | 0.050 mm per gram (arm 312 mm / AUW); 326 g to close 16.3 mm |
| One 321 g cell sliding 1 in | 1.31 mm; both cells 2.62 mm |

So a 0.5 in pivot move still leaves +7.4 mm, and no spare volume to trim it. This agrees with your
reading. Also note the load spread is tiny: hover, heaviest payload and third cell differ by only
0.7 mm of CG [REPO]. The trim you need is for **build-to-build scatter and component swaps**, not
for loading. For scale: an unmodelled 20 g at the tail (arm ~297 mm) moves the CG ~0.95 mm
[CALC].

The repo does not state a pitch control moment, so the **required trim range cannot be computed**.
The 50% control-reserve framing (MIL-F-83300) has no authority number behind it [REPO
`CG_RELOCATION_STUDY.md` §1]. I propose a working target of **±0.25 in (±6.4 mm)** of CG, adjustable
without tools, and ask you to confirm it (§9).

## 3. 27 in: where the extra 3 in goes decides everything

| Option | Hover CG offset [CALC] | Comment |
|---|---|---|
| 24 in baseline | +16.3 mm | no room, no trim |
| 27 in uniform scale (×1.125) | **+18.4 mm** | every arm grows; pivot move to zero becomes 26.1 mm |
| 27 in, 3 in plug at the head/cargo joint (Y 235) | **+8.0 mm** | the 679 g forward of the plug moves nose-ward 3 in |
| 27 in, 3 in plug at Y 286 | +5.0 mm | 929 g forward; not usable, the cargo band is 116 mm and full |
| **Plug at Y 235 + pivot 0.5 in aft** | **−0.9 mm** | on the thrust line before any trim |

Uniform scaling makes the offset worse. A forward plug works because it lengthens the moment arm of
the forward items without touching the pivot-to-aft geometry. That also lets your 0.5 in pivot move
close the rest. Trim range then comes from the plug volume:

- A 3 in plug lets the head cell slide ±1.5 in: ±2.0 mm of CG with no added mass.
- Both cells on one rail across the plug: ±3.9 mm.
- A 100 g ballast pocket at the nose adds ±5 mm but costs about 2.4% endurance (§6), so keep it as a
  last resort, not a baseline.

Cautions [ASSUMED unless noted]:

1. The plug result assumes every item forward of Y 235 rides the forward section. Check each.
2. The head-cell leads and rail lengthen: +27 g of 6 AWG [CALC, 160 g/m from the repo].
3. Moving the pivot aft moves the wing with it. **Pitch balance has to be re-checked at every tilt
   angle through transition, not only hover**, with mid-transition the usual miss [REPO skill
   `weight-and-balance.md` §4]. No transition number exists in the repo for this aircraft.
4. The pivot move reworks the spar carry-through, tilt brackets and wing-root flanges [REPO].
5. A 27 in hull must be re-baked from a single scale-or-stretch parameter, or the joint analysis
   will see port/starboard desync [REPO joint plan R3/R4].

## 4. Two sections: head+cargo and middle+rear

Today the hull has three joints [REPO `auw_ledger.json`, `airframe/fuselage-joints/WBS.md`]:

| Joint | Collar | Notes |
|---|---|---|
| J1 head/cargo | 11.5 g | rail passes through; 3 dowel pins; positive stop "not achieved as-baked" |
| J2 cargo/middle | 15.8 g | full-perimeter collar feasible per WBS |
| J3 middle/rear | 14.4 g | bonded lap |

Your proposal removes J1 and J3 and keeps J2 (Y ≈ 436). All of the high-load structure (spar,
pivot at Y 326.7, tilt brackets, wing-root flanges, gear bays, rail) then sits in one front
print, and only the aft section hangs off a single joint.

**Benefits**
- Removes two bond lines and 25.9 g of collars [REPO].
- The rail becomes continuous instead of passing through a collar.
- The front section (Y 0 to about 512 after the plug) prints as one stiff body with the wing loads.

**Joint load at J2 [CALC, ASSUMED rigid aft mass, whole load reacted at J2]:** aft mass 828 g
(1.82 lbm), centroid Y 508.7, arm 72.7 mm. At the repo's 79.4 g design load [REPO plan 001 R7]
applied normal to the hull axis: **shear 645 N (145 lbf), bending 46.9 N·m (415 lbf·in)**. At the
repo's FOS 3.0 [REPO middle/rear plan R3] the ultimate case is **1,935 N (435 lbf) and 141 N·m
(1,245 lbf·in)**. No allowable for the PA12 bond is sourced, so I report no margin. A coupon
bending test of the J2 joint at that moment is the way to get one.

**Risks that need your call**
1. **Assembly access.** Today the head interior is installed through its open aft face (Bay A on
   the rail ceiling, pitched Observer board, pitot hose, nose sensor bay). Joining head and cargo
   closes that face. A dorsal hatch in the plug (a "trim bay") could serve trim and service, but
   Bay A sits at Y 100–158, ahead of the plug. If it cannot be reached, a removable nose cone is the
   fallback, which makes three pieces.
2. **One material per print.** Hull sections are one material. Stiffer parts (spar carry-through,
   wing-root flanges, tilt brackets, rail) are separate prints already [REPO ledger] and can be
   PA12-CF inside a PA12 hull.
3. **Joint audit.** Re-run the pair census; retire J1/J3 rows; register the plug hatch and the
   rail pass-through as new interfaces [REPO joint plan R1].
4. **Anisotropy.** SLS is milder than FDM but not isotropic. PA12-CF datasheet orientation is not
   stated [SRC §5]. Apply the skill's additive-polymer caveat.

## 5. Materials, with the 3D Systems datasheet you supplied

DuraForm PA CF, **3D Systems datasheet 3DS-30108A (10-23)**, supplied by you [SRC]:

| Property | Value | Method |
|---|---|---|
| Material | 33% carbon-fibre-filled nylon 12 | datasheet text |
| Solid density | 1.11 g/cm³ (0.040 lb/in³) | ASTM D792 |
| Tensile ultimate / yield | 84 MPa (12.2 ksi) / did not yield | ASTM D638 |
| Tensile modulus | 8,500 MPa (1,230 ksi) | ASTM D638 |
| Elongation at break | 3.8% | ASTM D638 |
| Flex strength / modulus | 140 MPa (19.7 ksi) / 7,000 MPa (1,010 ksi) | ASTM D790 |
| Izod notched / unnotched | 52 J/m (1 ft·lb/in) / 490 J/m (9 ft·lb/in) | ASTM D256 / D4812 |
| HDT at 0.455 / 1.82 MPa | 181 °C (357 °F) / 177 °C (351 °F) | ASTM D648 |
| 24 h water absorption | 0.47% | ASTM D570 |
| Electrical rows | blank | ASTM D149/D150/D257 |

The sheet says the complete data set arrives "Q1 2024", states no build orientation, and gives no
minimum wall or maximum part size. Treat these as preliminary. It is ASTM-based, which fits your
US-standards-first rule. It also matches your "PA12-33%CF" and the earlier ALM PA 603 CF
figures (1.10 g/cm³, 7.9 GPa) within the spread.

Consequences [CALC unless noted]:
- Density ratio to CF-PETG solid (1.28 g/cc [REPO]): PA12-CF **0.867**, PA12 (1.01 g/cc, HP MJF
  [SRC Materialise listing]) **0.789**.
- PA12-CF is **stiff but not tough**: 3.8% elongation, notched Izod 52 J/m. Use it for frames,
  brackets, rail, and flanges, not for energy-absorbing parts. The shock-absorbing parts stay
  PA12 (landing gear, bumpers, doors).
- Electrical properties are blank. Carbon-filled parts near the Commo antennas and ferrites need a
  measurement, even with the 500 W/m² objective dropped (mass-diet KD1).
- I did **not** get a 3D Systems standard DuraForm PA (PA12-class) datasheet. Please upload it too.
- Water uptake is small, but dimensional change after conditioning is unverified.

## 6. Mass and endurance at 27 in, two sections [CALC]

Shell masses are the measured ledger values: head 177.6 g, cargo 310.0 g, middle 183.1 g,
rear 231.5 g, J2 collar 15.8 g; today with all three collars = 943.7 g. The plug adds 88–113 g
of CF-PETG-equivalent shell (1.15–1.48 g/mm × 76.2 mm, [ASSUMED] from the adjacent section
mass per length) and +27 g of harness. Endurance uses mass^-1.5 [REPO mass-diet plan].

| Material | Hull + collar | Change vs today | With +27 g harness | Endurance |
|---|---|---|---|---|
| CF-PETG | 1,006–1,031 g | +62 to +87 g | +89 to +114 g | −2.1% to −2.7% |
| **PA12** | 794–813 g | **−150 to −130 g** | −123 to −103 g | **+3.0% to +2.5%** |
| PA12-CF | 872–894 g | −72 to −50 g | −45 to −23 g | +1.1% to +0.6% |

So 27 in with two sections in SLS PA12 is **lighter than today's 24 in hull**, even with the longer
rail harness. The saving is a modest slice of the 555 g diet target and does not threaten KD4
(2 mm shells kept), but it assumes SLS vendors accept a 2 mm closed shell. They will want
powder-evacuation holes, which affect foam fill and the no-voids rule in `AGENTS.md` §7.

## 7. Printing and shops

**Build-volume fit [CALC, bounding boxes only; the shells are not boxes].** Box sizes: 27 in
one-piece 686 × 200 × 210 mm; front section 512 × 200 × 165 mm; rear section 190 × 200 × 181 mm.

| Machine (listed volume) | One piece | Front | Rear |
|---|---|---|---|
| EOS P 770, 700 × 380 × 580 mm | flat, 14 mm to spare | flat | flat |
| 3D Systems sPro 230, 550 × 550 × 750 mm | tilted ~55° only | flat | flat |
| Quickparts (listing), 500 × 500 × 725 mm | tilted ~65° only | tilted | flat |
| Protolabs, 482 × 482 × 431 mm | no | tilted ~45° | flat |
| HP-class, 380 × 284 × 380 mm | no | no | flat |

Two sections fit every large SLS machine here; one 27 in piece fits only a P 770-class machine
flat, or a tall tilted build elsewhere, which I would avoid for a 2 mm shell.

**3D Systems.** Facts I could check:
- 3D Systems lists DuraForm PA CF at 33% carbon-filled nylon 12 [SRC product page via search; and your datasheet].
- sPro 230 build volume 550 × 550 × 750 mm (sources disagree which axis is 750)
  [SRC Aniwaa, Treatstock].
- A 2017 On Demand brochure lists DuraForm HST at 20 × 20 × 28 in (508 × 508 × 711 mm); I found no
  figure for PA CF.
- **Location:** headquarters is Rock Hill, South Carolina [SRC multiple]; the company was
  founded in Valencia, California [SRC Wikipedia]. I could not confirm a current California
  production site. Ask them which site would print your order; it affects freight, not the study.
- **Network:** 3dsystems.com is outside this session's allowed domains, so I could not read their
  site. Allow it in the environment's network settings if you want me to pull current material
  pages.

**Overseas versus domestic.** A US shop avoids duty. For an overseas shop I could not establish
the duty rate: sources disagree on the de minimis dates and on how Section 301 and IEEPA duties
now apply, and I found no HTS rate for printed parts. A customs broker's classification is
needed. Freight is volume-driven: a 30 × 12 × 12 in carton is about 31 lb dimensional weight at a
139 in³/lb divisor [ASSUMED carrier divisor], against a part weighing roughly 2 lbm. Dimensional
weight, not part weight, will set shipping.

## 8. What I recommend

1. **27 in with a 3 in plug at the head/cargo joint, built as two sections** (head+cargo, middle+
   rear), single collar at J2. Pair it with the 0.5 in pivot move: CG −0.9 mm before trim.
2. **Put the trim in the plug:** a rail section the head cell (and optionally cell 2) slides along
   with detents, a dorsal hatch, and a printed-in pocket for up to 100 g of ballast as a last
   resort. Target ±6.4 mm of CG range [ASSUMED, §2].
3. **Materials:** PA12 hull sections and impact parts, PA12-CF for rail, spar carry-through,
   flanges and brackets.
4. **Shop:** get PA12 and PA12-CF quotes from 3D Systems and one more US shop for the two sections
   (front 512 mm is the driver). Defer overseas quotes unless the US quotes disappoint.
5. **Before releasing anything:** re-run the joint census at 27 in; resolve the Bay A access
   question; bench-test a J2 bending coupon to 141 N·m; confirm electrical behaviour of PA12-CF
   near antennas; get the pitch-balance numbers through transition.

## 9. Questions for you

1. Is **±0.25 in (±6.4 mm)** the right trim range, or do you have a pitch-authority number?
2. Is the extra 3 in a **plug at the head/cargo joint** as I assumed, rather than distributed?
3. Can Bay A and the nose electronics be installed through the cargo doors and a dorsal hatch, or
   do you want a removable nose cone (three pieces)?
4. Please upload the **DuraForm PA** (PA12-class) datasheet, and the full PA CF data set if you
   have it.
5. Should I allow-list 3dsystems.com for the session so I can read current pages?
6. Is a US-only shop list acceptable for now?

## 10. Not done

No FEA, no CAD change, no vendor quote, no census run, no transition-flight pitch analysis. The
build-volume fits use bounding boxes from per-part STL extents. The skills I used are unreviewed
drafts. The compound-engineering skills (`/ce-setup`, `/ce-work-trees`, `/ce-brainstorm`,
`/ce-ideate`) and `/3d-print-design` are **not in your connected plugin catalog or in this
session**: I searched by name and found only unrelated "brainstorming" and "worktree" plugins from
other authors, and I did not install any. Tell me where they live (a repo, or a plugin name) and
I will load them.
