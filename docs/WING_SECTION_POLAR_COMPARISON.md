# Serenity UAV — As-Built Wing Sections vs True S1223: XFOIL and NeuralFoil Polars

**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Date:** 2026-10-31
**Tool:** `tools/wing_polar_compare.py` (`--span` for the span sweep). Data and figure:
`docs/sls-study/wing-polars/` (`summary.csv`, `span_sweep.csv`, `wing_section_polars.png`).

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

Labels: **[REPO]** repo document. **[CALC]** computed here. **[ASSUMED]** needs verification.

## 1. What was run

- **Sections:** parsed from `wings_s1223_revo.scad` through `tools/wing_airfoil_variants.py`, with
  thickness scaled about the unscaled camber line, exactly as `s1223_section()` builds it. Check
  values: t/c 12.14% (S1223), 17.72% (root, ×1.46), 26.71% (tip, ×2.20) [CALC], matching the SCAD.
- **Tools installed:** XFOIL 6.99 (Debian package; needs `xvfb-run` and X fonts to run headless)
  and NeuralFoil 0.3.3 with AeroSandbox. OpenFOAM was **not installed in this pass**: the repo's own CFD script
  is blocked on mesh generation, and a 2-D laminar-bubble case needs a transition model I have not
  validated. It is the next step if you want the tip result confirmed by a flow solver.
- **Conditions:** 40 kt (20.58 m/s) sea level, ν = 1.461 × 10⁻⁵ m²/s. Chord Reynolds number
  182,000 at the root (129 mm) and 131,000 at the tip (93 mm), the repo's 1.3–1.8 × 10⁵ range.
- **Transition:** N_crit 9 (clean), N_crit 5 (contaminated), and a forced trip at 5% chord.
  N_crit and a trip are proxies for a rough surface, not a roughness model.
- **Required lift:** the SCAD header's 7.6 N cruise lift on 0.019025 m² at q = 259 Pa needs
  **CL ≈ 1.54** [CALC]. This is high, close to the true S1223's capability.

## 2. Reliability of each tool

- **XFOIL converged only to α ≈ 0.8° on the true S1223 at Re 182k** (it returns CL_max 1.27, which
  is a convergence failure, not a stall). It converged fully at Re 100k (CL_max 2.16) and on the
  as-built root. Rows with α_max below 2° in `summary.csv` are not valid CL_max values.
- **NeuralFoil** runs every case. It reports a confidence of 0.97–0.99 for the root and for the
  N_crit 5 tip, and **0.74 for the clean tip**, so the clean-tip numbers are the least certain.
- Where both converge they agree: root CL_max 2.10 (NeuralFoil) vs 2.20 (XFOIL), clean-tip CL at 0°
  0.73 vs 0.61 and L/D_max 10.3 vs 11.2 [CALC]. The tip collapse is therefore seen by both tools.
  Neither is a flow solver for a stalled laminar bubble; a wind-tunnel or RANS check is the proof.

## 3. Results [CALC]

True S1223 reference (NeuralFoil, N_crit 9): CL_max 2.20–2.23, CL at 0° = 1.22, L/D_max 60–70,
CL 1.54 at α ≈ 2.8°, CD 0.023.

| Section | Re | Transition | CL_max | CL at 0° | L/D_max | α at CL 1.54 | CD at CL 1.54 |
|---|---|---|---|---|---|---|---|
| **Root t17.7** | 182k | N 9 | 2.10 (XFOIL 2.20) | 1.22 | 55 | 2.8° | 0.028 |
| Root t17.7 | 182k | N 5 | 2.12 | 1.17 | 64 | 3.4° | 0.024 |
| Root t17.7 | 100k | N 9 | 1.55 | 1.17 | 34 | 4.4° | 0.050 |
| **Tip t26.7** | 131k | N 9 | **1.13** | **0.73** | **10** | **never reached** | — |
| Tip t26.7 | 131k | N 5 | 1.55 (XFOIL 1.37) | 1.06 | 38 | 5.7° | 0.045 |
| Tip t26.7 | 131k | trip 5% (XFOIL) | 1.30, no stall to 22° | 0.68 | 23 | never reached | — |
| Tip t26.7 | 100k | N 9 | 1.12 | 0.03 | 7 | never reached | — |

Along the span (NeuralFoil, same chords, true S1223 for reference):

| η (0 root, 1 tip) | t/c | CL_max, N 9 | CL at 4°, N 9 | CL at 4°, N 5 |
|---|---|---|---|---|
| 0.00 | 17.7% | 2.10 | 1.67 | 1.60 |
| 0.25 | 20.0% | 1.90 | 1.64 | 1.59 |
| 0.50 | 22.2% | 1.65 | 1.55 | 1.58 |
| 0.75 | 24.5% | 1.32 | 1.29 | 1.54 |
| 0.88 | 25.6% | 1.15 | 0.58 | 1.51 |
| 1.00 | 26.7% | 1.13 | 0.34 | 1.46 |
| *true S1223, all η* | 12.1% | 2.2 | 1.66 | 1.60 |

A strip-theory sum of 2-D lift over the span, built wing against a true-S1223 wing of the same
chords, gives **0.83 at 4° and 0.75 at 6° for clean flow**, and 0.97 for N_crit 5 [CALC]. Strip
theory ignores the strong 3-D flow of a wing this small, so read it as a ratio only.

## 4. What it means

1. **The root section is fine.** t17.7 keeps 94% of S1223's CL_max and makes CL 1.54 at about 3°.
   Drag is 15–25% higher.
2. **The outer quarter of the wing is not.** Past η ≈ 0.75 (t/c ≈ 24.5%) a clean flow loses most of
   its lift: at the tip CL at 4° falls from 1.66 to 0.34 and L/D_max from 60 to 10. The mechanism is
   a large laminar separation on a thick section at Re ≈ 1.3 × 10⁵.
3. **The result is highly sensitive to transition.** With early transition (N_crit 5) the tip
   recovers to CL_max 1.5 and L/D 38. With a forced trip at 5% chord, XFOIL shows lift stuck near
   1.3 and L/D 23, never reaching the 1.54 needed. A rough surface can help or hurt, which means
   **surface finish is a design variable here, not a cosmetic one.**
4. **The 7.6 N cruise-lift figure is not supported** for clean flow: the tip cannot make CL 1.54,
   and the wing as a whole loses about 17–25% of the strip lift. The repo already flags this figure
   as unverified [REPO `flight_envelope.md`]; this is the first quantitative check.
5. **Thickness at the tip is set by the spar, not by aerodynamics.** The ×2.20 tip scale exists to
   swallow the Ø20.4 mm spar bore with a 1.16 mm wall floor [REPO `wings_s1223_revo.scad`]. The
   floor is an FDM figure; a vendor minimum wall below that would reduce the scale a little, but
   the spar diameter is the larger lever.

## 5. Consequences for the SLS decision

- **The owner's correction stands:** the spar and wing root carry the aircraft load and the nacelle
  thrust through the tilt range, including unbalanced thrust in manoeuvres, and nothing about them
  is repositioned after printing. That removes my "indexed pivot" idea from consideration and
  fixes the spar bore and the root flange as the primary structure. The repo's own spar analysis
  says the spar alone takes the bending, not the skin [REPO `WING_ATTACH_INTERFACE.md` line 78],
  so the wing shell is not the primary load path. I treat the **shell as an aerodynamic fairing and
  the root flange as structure**, and the flange stays in PA CF.
- **Do not freeze the tip dimensions on this evidence.** The surface texture of a powder-bed part
  and the wall limit of the process both change the answer, and the tip result swings by a factor
  of three in L/D between clean and tripped flow. The shop's finish needs to be known before the
  dimensions are final.
- **Candidate changes to evaluate before the shop** (not run): a thinner tip scale with a smaller
  or tapered spar; a spar that is not Ø20.4 mm to the tip; a turbulator at 10–15% chord to hold
  the flow attached; vapor smoothing to a known Ra. Each is a quick NeuralFoil run now.

## 6. Not done

No wind-tunnel, RANS or OpenFOAM result; no 3-D wing analysis; no roughness-height model. XFOIL
failed to converge on several cases (see `summary.csv`), so NeuralFoil carries most of the numbers.
The 7.6 N requirement is the SCAD header's own figure.
