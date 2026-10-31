# Serenity UAV — SLS PA12 / PA12-CF, 30 in Hull, Single-Piece Print Evaluation

**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Status:** Screening study. Not a design release. No vendor quotes obtained, no FEA run.
**Base:** branch `worktree-fuselage-reconcile` @ `3252b5a2`

> ⚠️ **ENGINEERING REVIEW REQUIRED.** A qualified engineer shall review this before it drives
> any purchase or any change to a flight-critical part.

Labels used below: **[SRC]** = from a cited source (third-party; verify against the vendor's
current datasheet). **[REPO]** = from this repository. **[CALC]** = my arithmetic.
**[ASSUMED]** = my assumption; needs verification.

---

## 0. Bottom line

| # | Change | Verdict |
|---|---|---|
| 1 | FDM CF-PETG → SLS PA12 (shock) / PA12-33%CF (rigid) | **Worth pursuing, as a split-material hull.** Lighter per cc and isotropic. Needs coupon testing and a policy change to `AGENTS.md` §7. |
| 2 | Scale 24 in → 30 in | **Costs more than it gives unless thrust is fixed first.** Hull mass +56% at constant wall; the prior 36 in study already showed T/W worsening with scale. |
| 3 | Print the hull as one piece | **No, at 30 in.** The envelope (about 30 × 9.8 × 10.4 in) does not fit any mainstream SLS/MJF machine. Only a 1,000 mm-class machine fits it, and I found no U.S. bureau listing one. It would also remove the open-section access the design relies on. |

Recommended path: keep sections, move to SLS, and use 2–3 sections (not 4) only if a vendor
confirms the build volume.

---

## 1. Hull envelope (measured)

Measured from the four `*_shell24_2mm_repaired.stl` files [REPO]. Extents are per-part, in each
part's own frame, so the overall box is approximate.

| Dimension | 24 in (now) | 30 in [CALC, ×1.25] |
|---|---|---|
| Length | 24.0 in (610 mm) | 30.0 in (762 mm) |
| Width (hull body, no wings) | ~7.9 in (200 mm) [ASSUMED from cargo section 194 mm] | ~9.8 in (250 mm) |
| Height (incl. rear fin) | ~8.3 in (210 mm) [from rear section 181 mm + margin] | ~10.4 in (263 mm) |

Existing printed hull shells: head 177.6 g, cargo 310.0 g, middle 183.1 g, rear 231.5 g =
**902.1 g (1.99 lbm)** [REPO `auw_ledger.json`]. All 45 PRINT rows total
**1,639.5 g (3.61 lbm)** of 6,052.6 g (13.34 lbm) hover AUW.

## 2. Change 1 — material

| Property | CF-PETG (FDM) | PA12 (MJF/SLS) | PA12-33%CF (SLS) |
|---|---|---|---|
| Density | 1.28 g/cc solid, 1.05 as-printed [REPO `MASS_AUDIT_CARGO_WING_ROOT.md`]; 1.23–1.29 [SRC vendor TDS] | 1.01 g/cc [SRC HP MJF via Materialise] | 1.10 g/cc [SRC ALM PA 603 CF] |
| Tensile modulus | Z: ~1.34 GPa (195 ksi) [SRC Bambu PETG-CF TDS] | 1.7–1.8 GPa (245–260 ksi) [SRC HP MJF] | 7.9 GPa (1,150 ksi) XY [SRC ALM PA 603 CF] |
| Tensile strength | Z: 29–38 MPa (4.2–5.5 ksi) (versions disagree) | 48 MPa (6.96 ksi) XY | 85 MPa (12.3 ksi) XY |
| Elongation at break | not in sources found | 15–20% | 4% |
| Anisotropy | Strong (weak Z, layer lines) | Mild | Mild to moderate [ASSUMED; CF aligns with recoater] |

Sources: [HP MJF PA12 (Materialise)](https://reseller.materialise.com/ja/node/3844),
[ALM PA 603 CF (SpecialChem)](https://www.specialchem.com/plastics/product/alm-alm-pa-601-cf),
[Bambu PETG-CF TDS](https://polyalkemi.no/wp-content/uploads/2023/08/Bambu_PETG-CF_Technical_Data_Sheet_V2.pdf).
Test methods quoted are ASTM D638 / D792, so US-standard values apply.
The sources are secondary pages, so confirm against the manufacturer datasheets before use.
The "33% CF" PA12 I could identify is the EOS-family ALM PA 603 CF; I did **not** confirm a
U.S. bureau that stocks it. Shapeways "PA 640-GSL" is carbon plus glass microspheres, not 33% CF.

**Mass effect at equal wall thickness [CALC]:** PA12 is 0.79× and PA12-CF 0.86× the CF-PETG
solid density (using 1.28 g/cc).

**Suggested allocation [ASSUMED, needs FEA/coupon test]:**
- **PA12 (energy absorbing):** landing-leg fairings and feet, nose/bow bumper and sensor pod,
  cargo doors, nacelle tip gear, access covers.
- **PA12-CF (stiff):** wing-root flanges, tilt actuator brackets and trunnions, spar carriers,
  bulkheads and splice collars, EDF motor mounts, battery cradle.
- **Hull skin (2 mm):** PA12 for crash tolerance, with PA12-CF frames carrying load. Hull-skin
  stiffness at 1.7 GPa is a question for analysis, not something this study settles.

**Cautions to verify:** PA12 moisture uptake and dimensional change; CF-PA12 conductivity next
to the Faraday enclosure and RF antennas (REPO requires operation in a 500 W/m² field); heat
resistance near ESCs; vendor minimum wall (do not assume below 2 mm without a quote).

**Policy impact:** `AGENTS.md` §7 mandates CF-PETG and a 2.0 mm hollow shell with 2 lb/ft³
foam fill. Moving to SLS needs an explicit decision to change that text. I did not edit it.
The "watertight, no voids" rule also conflicts with SLS: a closed hollow part traps powder,
so each closed cavity needs evacuation holes (vendor guidance commonly 0.2–0.4 in, [ASSUMED]).

## 3. Change 2 — 30 in scale

Hull shell mass, scaled from 902 g [CALC]:

| Scaling law | CF-PETG | PA12 (×0.79) | PA12-CF (×0.86) |
|---|---|---|---|
| Today (24 in) | 902 g (1.99 lbm) | — | — |
| 30 in, k² = 1.5625 (thin shell, wall fixed) | 1,409 g (3.11 lbm) | 1,113 g (2.45 lbm) | 1,212 g (2.67 lbm) |
| 30 in, k³ = 1.953 (frames grow too) | 1,762 g (3.88 lbm) | 1,392 g (3.07 lbm) | 1,515 g (3.34 lbm) |

Material switch alone recovers 14–21% of hull mass, but scaling adds 56–95%. Net: a 30 in
SLS hull weighs **more** than today's 24 in CF-PETG hull (by 211–490 g, 0.47–1.08 lbm).
All 45 printed parts at k² would add about 923 g (2.03 lbm) before material savings.

**Open conflict in the repo:** `docs/HULL_SCALE_36IN_EDF64MM_EVALUATION.md` puts corrected T/W
at 0.98–1.01 against a 1.2 floor, while `auw_ledger.json` reports 1.36–1.41 for the same
airframe. I did not reconcile these. Resolve before trusting any 30 in T/W number.

**Benefit of 30 in:** volume grows 1.95×, giving room for components and for post-build
weight-and-balance trim. **Alternative that costs less:** keep 24 in and add a movable
ballast/battery rail (the head cell already uses a CG rail per the base commit) for trim.

## 4. Change 3 — single-piece hull

**Fit check [CALC, `docs/sls-study/hull_build_volume_fit.scad`]:** rotated the hull bounding box
in 15° steps inside each build volume.

| Machine (listed build volume) | 24 in hull | 30 in hull |
|---|---|---|
| Farsoon HT1001P, 1000 × 500 × 450 mm | fits | **fits, flat, no tilt** |
| EOS P 770, 700 × 380 × 580 mm | fits (tilted) | **does not fit** |
| Protolabs SLS, 482 × 482 × 431 mm | no | no |
| Xometry SLS, 330 × 330 × 559 mm | no | no |
| HP Jet Fusion 5200-class, 380 × 284 × 380 mm | no | no |

Volumes from [EOS P 770](https://na.eos.info/Equipment/Polymer-Platforms/EOS-P-770),
[Farsoon HT1001P](https://3dprinting.com/products/industrial-3d-printer/farsoon-ht1001p/), and a
[bureau comparison](https://all3dp.com/2/best-sls-3d-printing-services/); bureau limits change,
so confirm at quote time. HP 5200 is from memory and not sourced here.

I found **no U.S. service bureau advertising a 1,000 mm-class machine**; known operators are in
China and Germany. A one-piece 30 in hull therefore means an overseas or custom order.

| Factor | Single piece | Sections |
|---|---|---|
| Joints / alignment error | none | splice collars (already designed: 11.5–15.8 g each) |
| Component install | only through nose, tail, and cut access panels | open mating faces (current design intent) |
| Powder removal | worst case: one long closed cavity | easy |
| Foam fill and cable routing | through holes only | per-section |
| Warp risk (762 mm × 2 mm wall) | highest | lower |
| Failure cost | a whole-hull reprint | one section |
| Part count, assembly time | lowest | higher |
| Repair/rework | scrap or cut | swap a section |

A one-piece hull also removes the access that `AGENTS.md` §7 requires ("mating faces stay open
for build access and cable routing") and complicates tilt-actuator, winch, and battery bay work.

## 5. Cost (rough; no quotes)

I could not find published 2025 per-cc prices for the named bureaus. The only anchors:
PA12 powder at $70–$150/kg and a German study citing under €1/cc for large parts
(see the Sinterit and bureau pages linked above). **Get instant quotes for the same STL set
from Xometry, Protolabs, and Fathom** before relying on any figure. Hull volumes are ~1,040 cc
today [CALC from STL] and ~2,030 cc at k³ — use these for quotes.

Qualitative: SLS adds per-part cost against a printer you already own, but cuts print time,
failed prints, post-processing (no supports, isotropic strength), and lets you nest parts.
A one-piece order concentrates all risk and cost in one build.

## 6. Recommendation and next steps

1. **Do change 1 first, at 24 in.** Quote the existing STLs in PA12 and PA12-CF; print a
   coupon set (tensile, flex, a 2 mm wall panel, a splice joint) and test before any flight part.
2. **Defer change 2** until T/W is reconciled (§3) and thrust is fixed. If room is the
   goal, test a 27 in or rail-trim option first.
3. **Reject change 3** at 30 in. If the scale-up proceeds, keep sections; ask vendors to
   confirm build volume for a 2–3 section split.
4. Open decisions for you: edit `AGENTS.md` §7? Which sections carry CF? Accept overseas
   sourcing for any 1,000 mm-class print?

**Not done:** the requested `/ce-*` and `/3d-print-design` skills are not installed in this
session, so none were run. Only `/openscad` was available. No FEA, no mesh validation of new
geometry (nothing new was modeled beyond a bounding-box fit check), no `REFERENCES.md` entries
added: the sources above are catalogued here only and should get REF-IDs after verification.
