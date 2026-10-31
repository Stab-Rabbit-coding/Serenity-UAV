# Serenity UAV — SLS Material Selection from the 3D Systems Datasheets

**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Date:** 2026-10-31
**Tool:** `tools/sls_material_screen.py` (reproduces every figure below)
**Follows:** `docs/SLS_27IN_TWO_SECTION_TRIM_STUDY.md`, which this document corrects in §1.

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

Labels: **[SRC]** a supplied 3D Systems datasheet. **[REPO]** repo document. **[CALC]** my
arithmetic. **[ASSUMED]** needs verification.

---

## 1. Corrections to my earlier study

Two statements in `SLS_27IN_TWO_SECTION_TRIM_STUDY.md` do not survive the new datasheets and the
repo's own mass audit.

**1.1 PA12 is the wrong hull-skin material if you want today's stiffness.** I suggested PA12
hull sections because they weigh less. That compared mass at equal thickness and ignored stiffness.
The repo's CF-PETG flexural modulus is **6,670 MPa (967 ksi)** [REPO `MASS_AUDIT_CARGO_WING_ROOT.md`
§1, REF-MAT-002]. DuraForm PA12 Black is **1,500 MPa (210 ksi)** [SRC 3DS-30112A], 4.4× lower.
For equal plate bending stiffness (stiffness ∝ E·t³) against a 2 mm CF-PETG skin [CALC]:

| Material | Thickness for equal stiffness | Mass vs 2 mm CF-PETG at solid 1.28 g/cc |
|---|---|---|
| **PA CF** | 1.97 mm (0.078 in) | **0.85** |
| ProX HST | 2.50 mm | 1.09 |
| ProX PA | 3.19 mm | 1.18 |
| PA12 Black | 3.29 mm (0.130 in) | **1.28** |
| PA11 Black | 3.29 mm | 1.32 |

So at 2 mm, PA12 gives a skin with about a quarter of the stiffness. Keeping stiffness with PA12
costs about 28% more mass. **PA CF is the hull material that matches CF-PETG stiffness.**

**1.2 The mass saving depends on which density the ledger should have used.** The ledger prices
every printed part at **1.05 g/cc** [REPO `tools/auw_ledger.py` `RHO_PRINT`]. The same audit says
thin perimeter-only sections are nearer the **1.28 g/cc** solid density and that 1.05 is a bulk
figure [REPO `MASS_AUDIT` §1]. A 2 mm hull shell is almost all perimeter. If real shells weigh
1.28 g/cc, the ledger understates the four shells (902 g) by about 198 g [CALC]. If they weigh
1.05, SLS saves much less. My earlier "−150 g" assumed 1.28 for everything. The numbers in §5
give both. **Please weigh one printed hull shell**; that single measurement decides the question.

## 2. The data (supplied datasheets, ASTM, printed XY unless noted)

| Property | PA CF | PA12 Black | PA11 Black | ProX AF+ |
|---|---|---|---|---|
| Datasheet | 3DS-30108A (10-23, preliminary) | 3DS-30112A (02-25) | 3DS-30109A (02-25) | 10-17 |
| Density | 1.11 g/cm³ | 1.00 | 1.03 | 1.31 |
| Tensile modulus | 8,500 MPa (1,230 ksi) | 1,800 (260 ksi) | 1,900 (270 ksi) | 4,340 (630 ksi) |
| Flexural modulus | 7,000 MPa (1,010 ksi) | 1,500 (210 ksi) | 1,500 (220 ksi) | 3,710 (538 ksi) |
| Tensile ultimate | 84 MPa (12.2 ksi) | 45 (6.5 ksi) | 51 (7.4 ksi) | 37 (5.4 ksi) |
| Elongation at break | 3.8% | 13.7% (6.2–13.7%, §2.1) | 52.6% | 3% |
| Notched Izod | 52 J/m (1.0 ft·lb/in) | 35 (0.7) | 42 (0.8) | 54 (1.0) |
| Unnotched Izod | 490 J/m (9) | 410 (8) | did not break | 255 (4.8) |
| HDT 0.455 MPa | 181 °C (357 °F) | 177 °C (350 °F) | 193 °C (380 °F) | 182 °C (360 °F) |
| **HDT 1.82 MPa** | **177 °C (351 °F)** | **84 °C (184 °F)** | **58 °C (136 °F)** | 174 °C (345 °F) |
| 24 h water absorption | 0.47% | 0.32% | 0.36% | 0.25% |
| Electrical | blank | not given | blank | volume resistivity 1.09 × 10¹⁴ Ω·cm |
| UV / weathering | not given | tested, 92–95% retained at 12–18 mo | tested, 86–100% retained at 12 mo | not given |

Selection guide 3DS-30101D (03-23) adds, for other grades [SRC]:

| Grade | Density | Tensile modulus | Elongation | Notched / unnotched Izod | HDT 0.455 / 1.82 MPa |
|---|---|---|---|---|---|
| DuraForm PAx Black | 1.04 | 1,500 MPa | 100% | 58 / >400 J/m | 110 / 45 °C |
| DuraForm ProX PA | 0.95 | 1,770 MPa | 22% | 45 / 644 J/m | 182 / 97 °C |
| DuraForm ProX EX Black (PA11) | 1.02 | 1,570 MPa | 60% | 75 / 3,336 J/m | 193 / 57 °C |
| DuraForm ProX HST | 1.12 | 4,123 MPa | 4.3% | 55 / 307 J/m | 183 / 171 °C |
| DuraForm HST (sPro) | 1.20 | 5,475–5,725 MPa | 4.5% | 37 / 310 J/m | 184 / 179 °C |
| DuraForm ProX GF | 1.33 | 3,720 MPa | 2.8% | 48 / 207 J/m | 180 / 129 °C |

### 2.1 Things in the sheets that need a question back to 3D Systems

1. **PA12 Black orientation.** The headline table says "printed along XY", but its tensile numbers
   (1,800 MPa, 13.7%) equal the table's **ZY** column. The **XY** column reads 1,600 MPa and 6.2%
   elongation. Design to the low column: 6.2% elongation, 39 MPa, 1,600 MPa.
2. **PA11 Black ISO flexural modulus** prints as "100 MPa / 8 ksi" against 1,500 MPa by ASTM, and
   ISO flexural strength (98 MPa) differs from ASTM (56 MPa). These look like typing errors. I used
   neither ISO flexural value.
3. **PA CF** is a preliminary data set, orientation not stated, electrical rows blank.
4. **Machine compatibility is not stated.** The selection guide separates "sPro compatible" grades
   (EX, PA, GF, HST) from the ProX grades. Which grade a bureau can run depends on its machine.
   The sPro 230 (550 × 550 × 750 mm [SRC Aniwaa]) is the machine whose volume fits the front
   section. A ProX 6100 (381 × 330 × 460 mm [SRC third-party listing]) does **not** fit a 512 mm
   front section even tilted [CALC], though it takes the 24 in front section on end.

## 3. What the numbers say

Figures of merit [CALC, `tools/sls_material_screen.py`]; higher is better:

| Material | Panel index E_flex^(1/3)/ρ | Strut index E_tens^(1/2)/ρ | Elongation | Notched Izod |
|---|---|---|---|---|
| CF-PETG (repo) | 14.7 | — | — | — |
| **PA CF** | **17.2** | **83** | 3.8% | 52 J/m |
| ProX HST | 13.5 | 57 | 4.3% | 55 J/m |
| ProX AF+ | 11.8 | 50 | 3% | 54 J/m |
| ProX PA | 12.4 | 44 | 22% | 45 J/m |
| PA12 Black | 11.4 | 42 | 13.7% | 35 J/m |
| PA11 Black | 11.1 | 42 | 52.6% | 42 J/m |
| PAx Black | 9.3 | 37 | 100% | 58 J/m |

1. **Stiff structure: PA CF.** It beats CF-PETG on panel stiffness per mass (+17%) and strut
   stiffness per mass, and keeps its modulus at temperature (HDT 177 °C at 1.82 MPa).
2. **Shock absorption: PA11, not PA12.** PA11 Black stretches 52.6% and its unnotched bars did not
   break. PA12 Black runs 6–14% depending on orientation. For a part meant to yield and absorb
   energy (the gear leg frame is the designed fuse in the gear failure hierarchy [REPO]), PA11
   Black or PAx/ProX EX is the better fit. The datasheet also claims more consistent isotropy
   and better Z strength for PA11.
3. **PA CF is not as brittle as I said.** Its Izod values (52 J/m notched, 490 unnotched) match or
   exceed PA12 Black (35, 410). What it lacks is elongation (3.8% against 13.7%), so it stores and
   absorbs far less energy in a slow bend. Fine for frames, poor for a part that must yield.
4. **Heat decides the nacelle.** At 1.82 MPa, PA11 softens at 58 °C and PA12 at 84 °C [SRC]. PA CF
   and AF+ hold 174–177 °C. Parts near the EDF motors and ESCs belong in PA CF, whatever the
   toughness.
5. **ProX AF+ buys no weight.** At 1.31 g/cc it is as dense as CF-PETG. Its one distinction is
   that it is the only one with electrical data: an insulator (10¹⁴ Ω·cm). Skip it unless you want
   machinable, press-fit features.
6. **Unfilled PA12 Black is the RF-neutral, UV-tested choice** for the antenna fin, GPS retainer and
   bezel. Carbon-filled parts have no electrical data, so carbon near antennas needs a measurement.

## 4. Part-by-part assignment (proposal; ledger PRINT rows)

| Group | Ledger mass today | Proposed material | Why |
|---|---|---|---|
| Hull shells (4) and splice collars (3) | 944 g | **PA CF** | stiffness parity with CF-PETG, lighter at solid basis |
| Gear leg frames and feet | 192 g | **PA11 Black** | yield-and-absorb fuse; must fail before its mounts |
| Gear bay plates, battery cradle/rail, wing-root flanges, tilt brackets, chin shelf, small brackets | 253 g | **PA CF** | stiff mounts that out-last the fuse; heat near nacelle |
| Cargo doors (2) | 26.7 g | **PA11 Black** | impact and hinge duty (PAx/EX are rated best for living hinges [SRC guide]) |
| Antenna fin, GPS ring, FPV bezel | 7.2 g | **PA12 Black** | RF-neutral, UV data |
| Wings (2) | 191 g | **keep FDM CF-PETG** | the section is unverified [REPO flight envelope]; do not change two things at once |
| Tilt wheel/worm/pinions | 27 g | **keep FDM** until a wear bench test | self-locking worm; no wear data in any sheet |

Total printed mass, 45 items, 1,639 g today [REPO ledger]:

| Basis | Result with this assignment [CALC] |
|---|---|
| Ledger bulk 1.05 g/cc | 1,703 g (**+64 g**) |
| Solid 1.28 g/cc | 1,436 g (**−203 g**) |

So the assignment is a **weight loss only if real FDM parts are near solid density**. If the
ledger's 1.05 is right, SLS PA CF is slightly heavier and the case for SLS rests on stiffness
consistency, heat, isotropy and print time, not on mass. Weigh a printed hull shell and a printed
leg frame to settle it. SLS parts are 100% dense, so chunky parts that FDM prints at 40% infill
will come out heavier unless the vendor can lattice them.

## 5. Multiple technologies

| Need | Technology | Basis |
|---|---|---|
| Hull, collars, brackets, rail, gear, doors | SLS nylon (grades above) | datasheets in hand |
| Wings, tilt gear train, anything under active iteration | stay FDM CF-PETG in-house | cheap iteration; wing section and gear wear unverified |
| Fit-check mock-ups of the 27 in plug and trim bay | FDM in a cheap material at full scale | cheapest way to prove the trim design before paying for SLS |
| Spar, thwarts, ring frame, bars | pre-cut composite | already in the ledger (RHO_CF 1.6); the repo's material order puts composite ahead of metal |
| Metal | only where a cited allowable requires it | `AGENTS.md` material order |

I have no datasheets for MJF, SLA or other 3D Systems processes, so I do not rank them. If a
second bureau offers HP MJF PA12 or PA11, the earlier secondary data (1.01 g/cc, 1.7 GPa)
puts it in the same class as PA12 Black.

## 6. What to ask 3D Systems before quoting

1. Which machine and site would print the **512 mm front section** (and the 190 mm rear section),
   and does that machine run **PA CF** and **PA11 Black**?
2. Is **DuraForm HST** (sPro-compatible, E 5.5 GPa, HDT 179 °C at 1.82 MPa) available as a stiff
   fallback if PA CF is not on the large machine? It is heavier per stiffness (panel index 13.5
   for ProX HST against 17.2 for PA CF).
3. The full PA CF data set, with orientation, electrical properties and a UV/weathering report.
4. Minimum wall for a closed 2 mm shell, powder-evacuation hole size and count, and whether
   they can lattice or hollow chunky parts.
5. Warp and tolerance on a 512 mm part; lead time; whether hull sections can be
   shipped in a 30 × 12 × 12 in carton.

## 7. Revised recommendation

1. **Two sections, 27 in (3 in plug), in DuraForm PA CF** at 2 mm, subject to the shell-weighing
   result and a coupon test. Keep PA12 for the RF-neutral small parts only.
2. **PA11 Black for the gear leg frames, feet and doors**, in place of PA12.
3. **PA CF for every stiff mount and for the hot zone near the nacelles.**
4. **Keep wings and the tilt gear train on FDM** for now.
5. **Weigh a printed 2 mm hull shell** before relying on any SLS mass saving.
6. Test coupons before flight parts: J2 bending to 141 N·m (1,245 lbf·in) [REPO FOS 3.0, see the
   27 in study], a gear-leg drop-test article in PA11, and a PA CF antenna-pattern check.

## 8. Not done

No vendor quote, no FEA, no drop or bend test. Material choices come from datasheet screening only.
Every number marked [SRC] is from the sheets you supplied; I could not open 3dsystems.com. The
quoted machine volumes come from search results and need confirmation with the bureau.
