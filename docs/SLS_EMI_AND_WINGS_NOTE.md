# Serenity UAV — SLS Note: Does PA-AF Help EMI, and Should the Wings Stay FDM?

**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Date:** 2026-10-31
**Follows:** `docs/SLS_MATERIAL_SELECTION_3DSYSTEMS.md`

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

Labels: **[SRC]** supplied datasheet or cited source. **[REPO]** repo document. **[CALC]** my
arithmetic. **[ASSUMED]** needs verification.

## 1. PA-AF (DuraForm ProX AF+) and EMI: no

The AF+ datasheet [SRC 10-17] lists volume resistivity **1.09 × 10¹⁴ Ω·cm**, surface resistivity
**1.33 × 10¹³ Ω**, dielectric constant 2.6 and dissipation factor 0.0121. Those are insulator
values. The aluminium particles sit isolated in the nylon, so there is no continuous conductive
path, and a shield needs one. The datasheet gives no shielding-effectiveness figure.

The trade against PA CF is also poor [CALC from the datasheets]:

| | PA CF | ProX AF+ |
|---|---|---|
| Density | 1.11 g/cc | 1.31 g/cc (+18%) |
| Flexural modulus | 7,000 MPa | 3,710 MPa (−47%) |
| Panel index | 17.2 | 11.8 |

So AF+ is heavier, less stiff and not a shield. Its only advantage is documented electrical data.

**What PA CF might do is unknown.** Its electrical rows are blank [SRC 3DS-30108A]. Carbon-filled
nylon can shield: an academic study reports about 42 dB at 30 MHz and 50 dB at 1 GHz for
carbon-fibre-filled nylon 6,6 [SRC as summarised by a search; verify the paper, [Springer 2001](https://link.springer.com/article/10.1007/s11664-001-0113-0)],
but that is a different nylon and process, with longer fibre. I found **no SLS or PA12 shielding
figure** for 33% carbon-fibre powder. Treat any shielding from PA CF as unproven until a coupon is
measured (for example a planar-material test such as ASTM D4935; verify the designation with a
lab).

## 2. EMI in this repo, and what the hull skin can do

- The 500 W/m² objective is **still in `AGENTS.md`** at this base (line 22; last edit 2026-10-20).
  The mass-diet plan proposes dropping it (KD1), but that plan is requirements-only. In my earlier
  documents I wrote as if it were dropped. It is not.
- 500 W/m² is about **434 V/m** in free space [CALC, E = √(S·377 Ω)].
- The repo's shielding relies on per-board enclosures, for example an aluminium Flight Engineer
  enclosure with conductive gasket specified at ≥ 60 dB from 1 MHz [REPO
  `POWER_DISTRIBUTION.md` §347]. The EMI test plan does not credit the hull skin. One analysis note
  calls the carbon fibre a "natural Faraday cage" informally [REPO wire-clearance analysis].
- The hull is not a closed cage in any case: clamshell aperture, intakes, nacelle ports.

**If you do want skin help,** the options are a conductive coating or plating on selected zones.
Vendors plate nylon SLS parts with electroless nickel plus copper or nickel, and a vendor page
calls about 50 µm total sufficient [SRC, [BigRep, promotional](https://bigrep.com/posts/electroplating-3d-printed-parts/)].
Measured shielding for plated 3D-printed polymers is available only for other substrates (about
60 dB over a narrow band on ABS; below 25 dB at 10 MHz for plated metals on a conference paper)
[SRC searches]. Mass is the catch [CALC, ASSUMED geometry]: one hull surface is about 4,740 cm²,
so copper at 10 µm adds about 43 g and 50 µm about 212 g. Plating the whole hull fights the mass
diet; treat only the zones that need it.

Two cautions: a conductive hull can detune antennas, so keep antennas on the separate non-metal
fin (a PA12 Black part), and test before relying on any of this.

**Verdict:** AF+ is not worth it for EMI. Choose the hull material for stiffness and mass (PA CF),
and get EMI from enclosures, with a measured PA CF coupon as a possible bonus.

## 3. Why I said keep the wings on FDM, and why that now changes

My reasons, in the order of weight:

1. **The section was unverified.** The repo says CL_max is unknown for the built S1223/t17.7 root
   and t26.7 tip, and the CFD study is blocked [REPO `wings_s1223_revo.scad`, `flight_envelope.md`].
   Printing a final-dimension wing in a shop before that is checked risks paying twice.
2. **Change one thing at a time.** Wings are where flight testing usually forces revisions.
3. **Surface finish and bore fit** were not in any datasheet I had.

You say you will freeze the dimensions before sending them out. That removes reasons 1 and 2, **if
the aerodynamic check has actually been done first**. It has not: the repo still lists it open. I
would do it before the shop, not after. So the honest answer is: **there is no strong reason to keep
the wings FDM once the dimensions are final.** Here is the SLS case.

**For SLS wings**
- Layer-free, near-isotropic skin on a thin trailing edge. FDM trailing edges and the 1.2 mm wall
  over the spar bore are layer-adhesion limited.
- No support scars on the bore or the surfaces.
- Repeatable mass. Two wings today weigh 191 g at the ledger's 1.05 g/cc.
- The 1.16 mm wall floor over the Ø20.4 mm spar bore is an FDM floor from the repo [REPO]. An SLS
  vendor may allow less, which would let the section come down a little. Ask for their minimum
  wall.

**Against SLS wings, or questions to close first**
- **Surface roughness is unquantified.** I found no as-printed SLS nylon Ra from a sheet. Powder-bed
  parts commonly run tens of microns; vapor smoothing cuts Ra 72–81% in one vendor's own study
  [SRC Formlabs white paper, vendor claim]. At Re 1.3–1.8 × 10⁵ the laminar bubble is sensitive to
  roughness, but you will likely fill and paint the wings anyway. Plan the finish.
- **Spar bore fit.** The Ø20.4 mm bore carries only 0.2 mm per side of clearance on the Ø20 spar
  [REPO]. SLS shrink and warp can bind that; ream the bore after printing.
- **Crash tolerance.** A 93–129 mm chord wing stub takes ground and crash contact.

**Material for the wings is not the hull material.** The wing is a fairing over the spar. The
carbon tube carries the nacelle loads, and the cruise lift is only about 7.6 N [REPO]. Stiffness
matters little; toughness and surface finish matter more. The selection guide rates DuraForm PA /
ProX PA and the PA11 EX grades 5 out of 5 for accuracy and surface finish, against 3 for GF and
HST [SRC 3DS-30101D]. So prefer **a PA or PA11 grade** (ProX PA is also the lightest at 0.95 g/cc),
not PA CF. That puts the pair at about 182 g (ledger basis) or 149 g (solid basis) in PA12 Black
[CALC], against 191 g today: a small saving on the ledger basis.

**Order of operations before the shop**
1. Run the airfoil check for S1223/t17.7 and t26.7 at Re 1.3–1.8 × 10⁵ with a
   transition-sensitive tool (the repo names XFOIL or a RANS run).
2. Decide whether the thickness can come down, using the vendor's minimum wall, and freeze.
3. Ask the shop about surface finish, bore tolerance and reaming.
4. Print one wing first, as a test article, before ordering the pair in quantity.

## 4. Not done

I did not run an airfoil analysis, a shielding measurement or a wing structural check. The
shielding figures are from other materials and processes. The wing mass figures use only density
ratios.
